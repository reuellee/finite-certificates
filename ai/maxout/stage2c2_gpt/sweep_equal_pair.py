"""Complete labeled-system equal-pair sweep for Stage 2c-2.

SciPy/HiGHS is used only to suggest a small dual support or a primal
point.  Every terminal classification is then checked in Fraction/integer
arithmetic.  The output stores one exact result per distinct
(class-pattern, k) and maps all 66,280 labeled systems to those results.
"""
from __future__ import annotations

import gzip
import io
import json
import math
import time
from fractions import Fraction

import numpy as np
from scipy.optimize import linprog

from common import (
    HERE,
    MASK20,
    PAIRS,
    REFERENCE_PATH,
    REPRESENTATIVES,
    U_INTS,
    VALID_BITS,
    check_sparse_kernel,
    class_pattern,
    fraction_text,
    full_system_rows,
    lift_reduced_certificate,
    reduced_equal_pair_rows,
)


SEED = 2026073101
OUTPUT = HERE / "equal_pair_coverage.json.gz"

# Canonical (side-0-fixed) Stage 2b residue members, one at each split.
# They are deliberately present before any search begins.  A dual success
# on either target is a fatal canary failure.
CANARIES = ((10070, 1), (25998, 2))


def write_json_gz(path, payload):
    with path.open("wb") as raw:
        with gzip.GzipFile(
            filename="", mode="wb", fileobj=raw, compresslevel=9, mtime=0
        ) as zipped:
            with io.TextIOWrapper(zipped, encoding="utf-8") as text:
                json.dump(payload, text, separators=(",", ":"), sort_keys=True)
                text.write("\n")


def solve_exact_on_support(rows, support):
    """Solve rows[support]^T*y=0, sum(y)=1 by exact RREF."""
    support = list(support)
    m = len(support)
    matrix = [
        [Fraction(rows[row][column]) for row in support] + [Fraction(0)]
        for column in range(5)
    ]
    matrix.append([Fraction(1)] * m + [Fraction(1)])
    pivot_row = 0
    pivots = {}
    for column in range(m):
        chosen = next(
            (
                row
                for row in range(pivot_row, len(matrix))
                if matrix[row][column] != 0
            ),
            None,
        )
        if chosen is None:
            continue
        matrix[pivot_row], matrix[chosen] = matrix[chosen], matrix[pivot_row]
        pivot = matrix[pivot_row][column]
        matrix[pivot_row] = [value / pivot for value in matrix[pivot_row]]
        for row in range(len(matrix)):
            if row == pivot_row or matrix[row][column] == 0:
                continue
            factor = matrix[row][column]
            matrix[row] = [
                a - factor * b
                for a, b in zip(matrix[row], matrix[pivot_row])
            ]
        pivots[column] = pivot_row
        pivot_row += 1
    for row in matrix:
        if all(row[column] == 0 for column in range(m)) and row[m] != 0:
            return None
    if len(pivots) != m:
        return None
    solution = [matrix[pivots[column]][m] for column in range(m)]
    if any(value <= 0 for value in solution):
        return None
    return solution


def primitive_certificate(rows, support, values):
    common = 1
    for value in values:
        common = math.lcm(common, value.denominator)
    integers = [
        value.numerator * (common // value.denominator)
        for value in values
    ]
    divisor = 0
    for value in integers:
        divisor = math.gcd(divisor, abs(value))
    sparse = [
        [int(row), int(value // divisor)]
        for row, value in zip(support, integers)
        if value
    ]
    candidate = tuple((row, value) for row, value in sparse)
    if not check_sparse_kernel(rows, candidate):
        return None
    return sparse


def exact_dual(rows, rng, max_attempts=12):
    """Find and exactly repair a nonnegative kernel vector."""
    matrix = np.asarray(rows, dtype=float)
    equalities = np.vstack([matrix.T, np.ones(len(rows))])
    rhs = np.r_[np.zeros(5), 1.0]
    scales = np.maximum(np.max(np.abs(equalities), axis=1), 1.0)
    equalities = equalities / scales[:, None]
    rhs = rhs / scales
    objectives = [np.zeros(len(rows))]
    objectives.extend(
        rng.normal(size=len(rows)) for _ in range(max_attempts - 1)
    )
    last_status = None
    for objective in objectives:
        result = linprog(
            objective,
            A_eq=equalities,
            b_eq=rhs,
            bounds=[(0, None)] * len(rows),
            method="highs",
        )
        last_status = result.status
        if result.status != 0:
            continue
        maximum = max(float(np.max(result.x)), 1.0)
        for tolerance in (1e-7, 1e-9, 1e-11, 1e-13):
            support = [
                index
                for index, value in enumerate(result.x)
                if value > tolerance * maximum
            ]
            values = solve_exact_on_support(rows, support)
            if values is None:
                continue
            certificate = primitive_certificate(rows, support, values)
            if certificate is not None:
                return certificate
    return None, last_status


def exact_primal(rows):
    """Find w with every reduced row dot w > 0, then verify exactly."""
    result = linprog(
        np.zeros(5),
        A_ub=-np.asarray(rows, dtype=float),
        b_ub=-np.ones(len(rows)),
        bounds=[(None, None)] * 5,
        method="highs",
    )
    if result.status != 0:
        return None
    for bound in (10**4, 10**6, 10**8, 10**10, 10**12):
        witness = [
            Fraction(float(value)).limit_denominator(bound)
            for value in result.x
        ]
        margins = [
            sum(Fraction(a) * b for a, b in zip(row, witness))
            for row in rows
        ]
        if min(margins) > 0:
            return witness, margins
    return None


def classify(pattern, k, rng):
    eligible, rows = reduced_equal_pair_rows(pattern, k)
    dual = exact_dual(rows, rng)
    if not isinstance(dual, tuple):
        lifted_example = None
        return {
            "status": "T_INDEPENDENTLY_COVERED",
            "eligible_classes": list(eligible),
            "reduced_certificate": dual,
            "support_size": len(dual),
            "lifted_example": lifted_example,
        }
    primal = exact_primal(rows)
    if primal is None:
        raise RuntimeError(
            f"neither exact dual nor exact primal for pattern={pattern}, k={k}; "
            f"dual LP status={dual[1]}"
        )
    witness, margins = primal
    return {
        "status": "HARD",
        "eligible_classes": list(eligible),
        "strict_primal_witness": [fraction_text(value) for value in witness],
        "minimum_margin": fraction_text(min(margins)),
    }


def main():
    start = time.time()
    rng = np.random.default_rng(SEED)
    valid_set = set(VALID_BITS)
    for bits, _ in CANARIES:
        if bits not in valid_set or bits & 1:
            raise AssertionError(f"canary {bits} is not a canonical valid sigma")

    patterns = sorted({class_pattern(bits) for bits in VALID_BITS})
    pattern_results = {}
    total = 2 * len(patterns)
    processed = 0

    # Canary-first: a false success stops the entire sweep immediately.
    canary_keys = []
    for bits, k in CANARIES:
        pattern = class_pattern(bits)
        key = f"{k}:{pattern}"
        result = classify(pattern, k, rng)
        if result["status"] != "HARD":
            raise RuntimeError(
                f"CANARY FAILURE: bits={bits}, k={k} accepted as covered"
            )
        pattern_results[key] = result
        canary_keys.append(key)
        print(
            f"canary PASS: bits={bits}, k={k}, pattern={pattern}, "
            f"margin={result['minimum_margin']}",
            flush=True,
        )

    for pattern in patterns:
        for k in (1, 2):
            key = f"{k}:{pattern}"
            if key not in pattern_results:
                pattern_results[key] = classify(pattern, k, rng)
            processed += 1
            if processed % 500 == 0 or processed == total:
                covered = sum(
                    result["status"] == "T_INDEPENDENTLY_COVERED"
                    for result in pattern_results.values()
                )
                print(
                    f"patterns {processed}/{total}; covered patterns={covered}; "
                    f"elapsed={time.time() - start:.1f}s",
                    flush=True,
                )

    systems = []
    counts = {
        "T_INDEPENDENTLY_COVERED": {"1": 0, "2": 0, "total": 0},
        "HARD": {"1": 0, "2": 0, "total": 0},
    }
    pattern_multiplicities = {}
    for bits in VALID_BITS:
        pattern = class_pattern(bits)
        pattern_multiplicities[pattern] = (
            pattern_multiplicities.get(pattern, 0) + 1
        )
        for k in (1, 2):
            key = f"{k}:{pattern}"
            status = pattern_results[key]["status"]
            systems.append([bits, k, key, status])
            counts[status][str(k)] += 1
            counts[status]["total"] += 1

            # Labeled-system exact verification, including both flip members.
            if status == "T_INDEPENDENTLY_COVERED":
                reduced = pattern_results[key]["reduced_certificate"]
                lifted = lift_reduced_certificate(
                    bits, pattern, tuple(tuple(item) for item in reduced)
                )
                if not check_sparse_kernel(full_system_rows(bits, k), lifted):
                    raise AssertionError(
                        f"bad lifted certificate at bits={bits}, k={k}"
                    )
            else:
                witness = [
                    Fraction(value)
                    for value in pattern_results[key]["strict_primal_witness"]
                ]
                _, rows = reduced_equal_pair_rows(pattern, k)
                if not all(
                    sum(Fraction(a) * b for a, b in zip(row, witness)) > 0
                    for row in rows
                ):
                    raise AssertionError(
                        f"bad strict witness at bits={bits}, k={k}"
                    )

    payload = {
        "schema": 1,
        "status": "complete_exact_labeled_sweep",
        "reference_path": str(REFERENCE_PATH.relative_to(HERE.parent.parent.parent)),
        "U_ints": [list(row) for row in U_INTS],
        "system_order": "sigma_bits ascending, then k=1,2",
        "n_valid_labeled_sigmas": len(VALID_BITS),
        "n_systems": len(systems),
        "n_distinct_class_patterns": len(patterns),
        "counts": counts,
        "canaries": [
            {
                "sigma_bits": bits,
                "k": k,
                "pattern_key": key,
                "expected": "HARD",
                "outcome": pattern_results[key]["status"],
            }
            for (bits, k), key in zip(CANARIES, canary_keys)
        ],
        "method": (
            "For every labeled (sigma,k), allow every class with equal side "
            "signs, require equal multipliers on its two sides, and allow all "
            "five positive-weight rows. HiGHS supplies supports/points only; "
            "all dual kernels and strict primal witnesses are verified exactly."
        ),
        "pattern_multiplicities": pattern_multiplicities,
        "pattern_results": pattern_results,
        "systems": systems,
        "seed_for_float_hints": SEED,
        "elapsed_seconds": time.time() - start,
    }
    write_json_gz(OUTPUT, payload)
    print(json.dumps(counts, indent=2), flush=True)
    print(f"wrote {OUTPUT} ({OUTPUT.stat().st_size} bytes)", flush=True)


if __name__ == "__main__":
    main()

