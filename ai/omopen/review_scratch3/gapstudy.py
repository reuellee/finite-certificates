#!/usr/bin/env python3
"""Measure float64 false negatives for weaponA one-point completion LPs.

The exact oracle is the verdict.  Determinant-one integer row operations are
used for stress tests, so every transformed instance retains the original
bracket signs and the transformed deleted column remains an exact witness.
"""

import io
import itertools
import json
import math
import os
import random
import statistics
import sys


# Set these before importing NumPy/SciPy through weaponA.  One thread is below
# the task's two-core ceiling, and bytecode is disabled both internally and in
# the documented invocation printed below.
os.environ["PYTHONDONTWRITEBYTECODE"] = "1"
for _name in (
    "OMP_NUM_THREADS",
    "MKL_NUM_THREADS",
    "OPENBLAS_NUM_THREADS",
    "NUMEXPR_NUM_THREADS",
):
    os.environ[_name] = "1"
sys.dont_write_bytecode = True

HERE = os.path.dirname(os.path.abspath(__file__))
OMOPEN = os.path.dirname(HERE)
sys.path.insert(0, OMOPEN)

import numpy as np  # noqa: E402

import catalog  # noqa: E402
import exactlp  # noqa: E402
import weaponA  # noqa: E402


SEED = 20260802
SAMPLE_SIZE = 8
# The six requested decade-like bands, plus the largest entry reported in
# OPEN_ATTACK.md (2^18) and weaponA._shrink's hard cap (2^22).
STRESS_BANDS = (
    (10, "<=2^10"),
    (18, "observed-run-max <=2^18"),
    (20, "<=2^20"),
    (22, "repo-cap <=2^22"),
    (30, "<=2^30"),
    (40, "<=2^40"),
    (50, "<=2^50"),
    (60, "<=2^60"),
)


def max_abs(values):
    """Maximum absolute Python integer in an array or nested sequence."""
    return max(abs(int(value)) for value in np.asarray(values, dtype=object).flat)


def chi_array(record):
    return np.array(
        [1 if sign == "+" else -1 for sign in record["chi"]],
        dtype=np.int64,
    )


def integer_rows(rows):
    return [[int(value) for value in row] for row in rows]


def dot(row, column):
    return sum((int(a) * int(b) for a, b in zip(row, column)), 0)


def determinant4(matrix):
    """Exact 4x4 determinant, used only to audit stress transforms."""
    total = 0
    for permutation in itertools.permutations(range(4)):
        inversions = sum(
            permutation[i] > permutation[j]
            for i in range(4)
            for j in range(i + 1, 4)
        )
        term = 1
        for i, j in enumerate(permutation):
            term *= int(matrix[i, j])
        total += -term if inversions & 1 else term
    return total


def float_verdict(rows):
    """Return weaponA's stated float verdict, margin, and any exception."""
    try:
        x, t = weaponA._lp_interior(rows)
    except Exception as exc:  # A solver/conversion failure counts as "none".
        return False, None, "%s: %s" % (type(exc).__name__, exc)
    feasible = x is not None and t is not None and math.isfinite(t) and t > 0.0
    return feasible, t, None


def evaluate(rows, max_x_entry, known_witness=None):
    rows = integer_rows(rows)
    if known_witness is not None:
        products = [dot(row, known_witness) for row in rows]
        if min(products) <= 0:
            raise AssertionError("the known completion is not strictly feasible")

    float_feasible, t, float_error = float_verdict(rows)
    exact_status, exact_certificate = exactlp.exact_feasible(rows)
    exact_feasible = exact_status == "FEASIBLE"
    if known_witness is not None and not exact_feasible:
        raise AssertionError("exactlp rejected a strict, integer known witness")

    return {
        "float_feasible": float_feasible,
        "exact_feasible": exact_feasible,
        "float_t": t,
        "float_error": float_error,
        "max_x_entry": int(max_x_entry),
        "max_lp_coefficient": max_abs(rows),
        "exact_certificate": exact_certificate,
    }


def select_easy_to_hard(certs, geom):
    """Choose quantiles of natural float margin among small-entry certs."""
    candidates = []
    for index, record in enumerate(certs):
        matrix = np.array(record["matrix"], dtype=object)
        # This lets every selected certificate participate in the <=2^10 band.
        if max_abs(matrix) > (1 << 10):
            continue
        chi = chi_array(record)
        margins = []
        for p in range(9):
            rows, _ = weaponA.completion_rows(matrix, chi, geom, p)
            _, t, _ = float_verdict(rows)
            margins.append(float("-inf") if t is None else float(t))
        candidates.append((min(margins), index, max_abs(matrix)))

    candidates.sort()
    if len(candidates) < SAMPLE_SIZE:
        raise RuntimeError("not enough <=2^10 certificates to form the sample")
    positions = [
        round(i * (len(candidates) - 1) / (SAMPLE_SIZE - 1))
        for i in range(SAMPLE_SIZE)
    ]
    return [candidates[position] for position in positions]


def grow_unimodular_to_band(transform, matrix, exponent, rng):
    """Grow an SL(4,Z) transform until max |U X| lies in (2^(e-1), 2^e]."""
    lower = 1 << (exponent - 1)
    upper = 1 << exponent
    current = max_abs(transform @ matrix)
    steps = 0

    while current < lower:
        candidates = []
        for i in range(4):
            for j in range(4):
                if i == j:
                    continue
                for multiplier in (-2, -1, 1, 2):
                    proposal = transform.copy()
                    proposal[i, :] = [
                        int(proposal[i, k])
                        + multiplier * int(proposal[j, k])
                        for k in range(4)
                    ]
                    magnitude = max_abs(proposal @ matrix)
                    if current < magnitude <= upper:
                        # Prefer moderate growth, with seeded random choice among
                        # the four closest operations to avoid a fixed shear.
                        score = abs(math.log2(magnitude / current) - 0.75)
                        candidates.append((score, magnitude, proposal))
        if not candidates:
            raise RuntimeError("could not grow a unimodular transform into band")
        candidates.sort(key=lambda item: (item[0], item[1]))
        shortlist = candidates[: min(4, len(candidates))]
        _, current, transform = shortlist[rng.randrange(len(shortlist))]
        steps += 1
        if steps > 2000:
            raise RuntimeError("unimodular growth exceeded its step limit")

    if current > upper or determinant4(transform) != 1:
        raise AssertionError("invalid determinant-one stress transform")
    return transform, transform @ matrix, steps


def aggregate(population, band, observations):
    exact_yes = sum(item["exact_feasible"] for item in observations)
    float_yes = sum(item["float_feasible"] for item in observations)
    false_negatives = sum(
        item["exact_feasible"] and not item["float_feasible"]
        for item in observations
    )
    disagreements = sum(
        item["exact_feasible"] != item["float_feasible"]
        for item in observations
    )
    return {
        "population": population,
        "band": band,
        "n": len(observations),
        "float_says_feasible": int(float_yes),
        "exact_says_feasible": int(exact_yes),
        "disagreements": int(disagreements),
        "false_negatives": int(false_negatives),
        "false_negative_rate": (
            false_negatives / exact_yes if exact_yes else None
        ),
        "float_exceptions": sum(item["float_error"] is not None for item in observations),
        "max_x_entry_min": min(item["max_x_entry"] for item in observations),
        "max_x_entry_max": max(item["max_x_entry"] for item in observations),
        "max_lp_coefficient_min": min(
            item["max_lp_coefficient"] for item in observations
        ),
        "max_lp_coefficient_max": max(
            item["max_lp_coefficient"] for item in observations
        ),
    }


def integer_summary(values):
    ordered = sorted(int(value) for value in values)
    return {
        "min": ordered[0],
        "median": ordered[len(ordered) // 2],
        "max": ordered[-1],
    }


def scientific_range(lo, hi):
    return "%.2e..%.2e" % (lo, hi)


def percent(rate):
    return "n/a" if rate is None else "%.2f%%" % (100.0 * rate)


def main():
    cert_path = os.path.join(OMOPEN, "data", "certs_realizable.jsonl")
    with io.open(cert_path, encoding="utf-8") as handle:
        certs = [json.loads(line) for line in handle]

    geom = catalog.realize_mod().Geom(9, 4)
    selected = select_easy_to_hard(certs, geom)
    selected_indices = [index for _, index, _ in selected]
    rows_out = []

    print("gapstudy: exact rational verdict versus weaponA float64 LP")
    print("certificates sampled: %d of %d" % (len(selected), len(certs)))
    print("sample indices:", selected_indices)
    print(
        "sample natural minimum margins:",
        ["%.3e" % margin for margin, _, _ in selected],
    )

    ground_observations = []
    for _, index, _ in selected:
        record = certs[index]
        matrix = np.array(record["matrix"], dtype=object)
        chi = chi_array(record)
        for p in range(9):
            rows, _ = weaponA.completion_rows(matrix, chi, geom, p)
            ground_observations.append(
                evaluate(rows, max_abs(matrix), known_witness=matrix[:, p])
            )
    rows_out.append(
        aggregate("GROUND-TRUTH-FEASIBLE", "shipped", ground_observations)
    )

    stress_by_band = {label: [] for _, label in STRESS_BANDS}
    stress_steps = {label: [] for _, label in STRESS_BANDS}
    for _, index, _ in selected:
        record = certs[index]
        matrix = np.array(record["matrix"], dtype=object)
        chi = chi_array(record)
        transform = np.eye(4, dtype=object)
        rng = random.Random(SEED + 1009 * index)
        for exponent, label in STRESS_BANDS:
            transform, transformed, steps = grow_unimodular_to_band(
                transform, matrix, exponent, rng
            )
            stress_steps[label].append(steps)
            transformed_max = max_abs(transformed)
            for p in range(9):
                rows, _ = weaponA.completion_rows(transformed, chi, geom, p)
                stress_by_band[label].append(
                    evaluate(
                        rows,
                        transformed_max,
                        known_witness=transformed[:, p],
                    )
                )

    for _, label in STRESS_BANDS:
        rows_out.append(aggregate("STRESS-FEASIBLE", label, stress_by_band[label]))

    # For every sampled deletion, perturb one of the eight retained columns
    # until the exact oracle supplies a nontrivial Gordan certificate.  Zero
    # rows are rejected so this population is not made of trivial degeneracy.
    infeasible_observations = []
    gordan_records = []
    perturbation_trials = 0
    perturb_rng = random.Random(SEED + 1)
    for _, index, _ in selected:
        record = certs[index]
        matrix = np.array(record["matrix"], dtype=object)
        chi = chi_array(record)
        scale = max_abs(matrix)
        for p in range(9):
            retained = [q for q in range(9) if q != p]
            found = False
            for attempt in range(1, 81):
                perturbation_trials += 1
                perturbed = matrix.copy()
                q = perturb_rng.choice(retained)
                if attempt & 1:
                    replacement = [
                        perturb_rng.randint(-2 * scale, 2 * scale)
                        for _ in range(4)
                    ]
                    if not any(replacement):
                        replacement[0] = scale
                    perturbed[:, q] = replacement
                    perturbation = {"kind": "replace", "column": q}
                else:
                    source = perturb_rng.choice([r for r in retained if r != q])
                    multiplier = perturb_rng.choice((-64, -16, -4, 4, 16, 64))
                    perturbed[:, q] = [
                        int(matrix[i, q]) + multiplier * int(matrix[i, source])
                        for i in range(4)
                    ]
                    perturbation = {
                        "kind": "column_shear",
                        "column": q,
                        "source": source,
                        "multiplier": multiplier,
                    }

                rows, _ = weaponA.completion_rows(perturbed, chi, geom, p)
                rows = integer_rows(rows)
                if any(not any(row) for row in rows):
                    continue
                status, lam = exactlp.exact_feasible(rows)
                if status != "INFEASIBLE":
                    continue

                # evaluate repeats exactlp intentionally: it ensures every
                # table observation goes through precisely the same path.
                observation = evaluate(rows, max_abs(perturbed))
                if observation["exact_feasible"]:
                    raise AssertionError("infeasible candidate changed verdict")
                infeasible_observations.append(observation)
                support = sum(value != 0 for value in lam)
                maximum = max(abs(int(value)) for value in lam)
                l1_norm = sum(abs(int(value)) for value in lam)
                gordan_records.append(
                    {
                        "certificate_index": index,
                        "deleted_column": p,
                        "attempt": attempt,
                        "perturbation": perturbation,
                        "vector_length": len(lam),
                        "support": support,
                        "max_coefficient": maximum,
                        "max_coefficient_bits": maximum.bit_length(),
                        "l1_norm": l1_norm,
                        "l1_norm_bits": l1_norm.bit_length(),
                    }
                )
                found = True
                break
            if not found:
                raise RuntimeError(
                    "failed to find exact-infeasible perturbation for cert %d, p=%d"
                    % (index, p)
                )

    rows_out.append(
        aggregate("GENUINELY-INFEASIBLE", "one-column perturbation", infeasible_observations)
    )

    gordan_summary = {
        "n": len(gordan_records),
        "vector_length": integer_summary(
            [item["vector_length"] for item in gordan_records]
        ),
        "support": integer_summary([item["support"] for item in gordan_records]),
        "max_coefficient": integer_summary(
            [item["max_coefficient"] for item in gordan_records]
        ),
        "max_coefficient_bits": integer_summary(
            [item["max_coefficient_bits"] for item in gordan_records]
        ),
        "l1_norm": integer_summary([item["l1_norm"] for item in gordan_records]),
        "l1_norm_bits": integer_summary(
            [item["l1_norm_bits"] for item in gordan_records]
        ),
    }

    print()
    print(
        "population                  band                         n  "
        "float_yes exact_yes disagree  FN-rate  max|X| range          max|A| range"
    )
    print("-" * 139)
    for row in rows_out:
        print(
            "%-27s %-28s %3d %10d %9d %8d %8s  %-21s %-21s"
            % (
                row["population"],
                row["band"],
                row["n"],
                row["float_says_feasible"],
                row["exact_says_feasible"],
                row["disagreements"],
                percent(row["false_negative_rate"]),
                scientific_range(row["max_x_entry_min"], row["max_x_entry_max"]),
                scientific_range(
                    row["max_lp_coefficient_min"],
                    row["max_lp_coefficient_max"],
                ),
            )
        )

    print()
    print("Gordan certificate sizes (min / median / max):")
    print(
        "  support: {min} / {median} / {max}; max-coefficient bits: "
        "{bmin} / {bmedian} / {bmax}; l1-norm bits: "
        "{lmin} / {lmedian} / {lmax}".format(
            min=gordan_summary["support"]["min"],
            median=gordan_summary["support"]["median"],
            max=gordan_summary["support"]["max"],
            bmin=gordan_summary["max_coefficient_bits"]["min"],
            bmedian=gordan_summary["max_coefficient_bits"]["median"],
            bmax=gordan_summary["max_coefficient_bits"]["max"],
            lmin=gordan_summary["l1_norm_bits"]["min"],
            lmedian=gordan_summary["l1_norm_bits"]["median"],
            lmax=gordan_summary["l1_norm_bits"]["max"],
        )
    )

    stress_rows = [row for row in rows_out if row["population"] == "STRESS-FEASIBLE"]
    first_failure = next(
        (row for row in stress_rows if row["false_negatives"]), None
    )
    natural_row = rows_out[0]
    observed_row = next(
        row for row in stress_rows if row["band"].startswith("observed-run-max")
    )
    cap_row = next(row for row in stress_rows if row["band"].startswith("repo-cap"))
    infeasible_row = rows_out[-1]

    if first_failure is None:
        first_line = "Float64 produced no false negatives in any tested stress band."
    else:
        first_line = (
            "Float64 first failed in band %s (max matrix entries %s and max LP "
            "coefficients %s)."
            % (
                first_failure["band"],
                scientific_range(
                    first_failure["max_x_entry_min"],
                    first_failure["max_x_entry_max"],
                ),
                scientific_range(
                    first_failure["max_lp_coefficient_min"],
                    first_failure["max_lp_coefficient_max"],
                ),
            )
        )
    conclusions = [
        first_line,
        "The untransformed shipped sample had a %.2f%% false-negative rate; the stress band at the run's reported 2^18 maximum had %.2f%%."
        % (
            100.0 * natural_row["false_negative_rate"],
            100.0 * observed_row["false_negative_rate"],
        ),
        "At weaponA._shrink's 2^22 entry cap, the measured stress false-negative rate was %.2f%% (%d of %d feasible instances missed)."
        % (
            100.0 * cap_row["false_negative_rate"],
            cap_row["false_negatives"],
            cap_row["exact_says_feasible"],
        ),
        "Float64 claimed feasible on %d of %d exact-infeasible controls; their Gordan supports ranged from %d to %d rows."
        % (
            infeasible_row["float_says_feasible"],
            infeasible_row["n"],
            gordan_summary["support"]["min"],
            gordan_summary["support"]["max"],
        ),
        (
            "The 47,723 reported 'infeasible' LP calls are supported as numerically reliable at the tested repository magnitudes (0 of 72 misses at the cap), but they are not formal exact certificates and the exact noisy fraction cannot be recovered without their original row matrices."
            if cap_row["false_negatives"] == 0
            else
            "The 47,723 reported 'infeasible' LP calls should not be treated as reliable infeasibility verdicts because false negatives occurred within the repository's allowed magnitude range."
        ),
    ]

    output = {
        "experiment": "weaponA float64 completion LP versus exactlp rational oracle",
        "seed": SEED,
        "certificate_file": os.path.relpath(cert_path, OMOPEN).replace(os.sep, "/"),
        "certificate_count": len(certs),
        "selected_certificate_indices": selected_indices,
        "selected_natural_min_float_margins": [margin for margin, _, _ in selected],
        "stress_band_upper_exponents": [exponent for exponent, _ in STRESS_BANDS],
        "stress_unimodular_steps_per_certificate": stress_steps,
        "table": rows_out,
        "infeasible_perturbation_trials": perturbation_trials,
        "gordan_certificate_summary": gordan_summary,
        "gordan_certificates": gordan_records,
        "conclusion": conclusions,
    }
    output_path = os.path.join(HERE, "gapstudy.json")
    with io.open(output_path, "w", encoding="utf-8", newline="\n") as handle:
        json.dump(output, handle, indent=2, sort_keys=True)
        handle.write("\n")

    print()
    print("CONCLUSION (five plain-prose lines)")
    for line in conclusions:
        print(line)
    print()
    print("JSON written to", output_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
