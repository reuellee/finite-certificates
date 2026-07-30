"""Prove the all-degree boundary of the coefficientwise equal-pair mechanism.

If an eligible class e=(i,j) has q_e*s_t=-1 at all three complementary
vertices, the constant multiplier y_e=1 gives the known single-class
certificate.

For every other labeled pattern in the reference sigma set, this script
finds exact positive formal determinant values d_abc such that

    q_e * sum_{t notin e} s_t*d_{tij} > 0

for every eligible class.  Setting all primal weights to one therefore
makes the equal-pair system strictly feasible at that positive formal-D
point.

Why this excludes *every* coefficientwise-positive ordinary-polynomial
certificate, not only the searched degrees: such a certificate is an
ordinary polynomial identity with nonnegative multiplier coefficients and
nonnegative weight slacks.  Evaluation at any positive D preserves
nonnegativity and yields a numeric Gordan certificate, contradicting the
stored strict primal witness.  The formal D point need not lie on the
Pluecker variety; that is precisely legitimate for the mechanism whose
identities require no GP reduction.
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
    PAIRS,
    TRIPLES,
    TRIPLE_INDEX,
    class_pattern,
    fraction_text,
    split_signs,
)


COVERAGE_PATH = HERE / "equal_pair_coverage.json.gz"
OUTPUT = HERE / "coefficientwise_boundary.json.gz"
CANARIES = ((10070, 1), (25998, 2))


def load_gz(path):
    with gzip.open(path, "rt", encoding="utf-8") as handle:
        return json.load(handle)


def write_json_gz(path, payload):
    with path.open("wb") as raw:
        with gzip.GzipFile(
            filename="", mode="wb", fileobj=raw, compresslevel=9, mtime=0
        ) as zipped:
            with io.TextIOWrapper(zipped, encoding="utf-8") as text:
                json.dump(payload, text, separators=(",", ":"), sort_keys=True)
                text.write("\n")


def favorable_classes(pattern, k):
    split = split_signs(k)
    out = []
    for class_index, ((i, j), marker) in enumerate(zip(PAIRS, pattern)):
        if marker == "x":
            continue
        q = 1 if marker == "+" else -1
        if all(q * split[t] == -1 for t in range(5) if t not in (i, j)):
            out.append(class_index)
    return out


def formal_d_rows(pattern, k):
    """Rows whose strict positivity is the all-degree no-go witness."""
    split = split_signs(k)
    eligible = []
    rows = []
    for class_index, ((i, j), marker) in enumerate(zip(PAIRS, pattern)):
        if marker == "x":
            continue
        q = 1 if marker == "+" else -1
        row = [0] * 10
        for t in range(5):
            if t in (i, j):
                continue
            triple = tuple(sorted((t, i, j)))
            row[TRIPLE_INDEX[triple]] = q * split[t]
        eligible.append(class_index)
        rows.append(row)
    rows.extend([
        [1 if variable == triple else 0 for variable in range(10)]
        for triple in range(10)
    ])
    return eligible, rows


def exact_formal_d_witness(pattern, k):
    eligible, rows = formal_d_rows(pattern, k)
    result = linprog(
        np.zeros(10),
        A_ub=-np.asarray(rows, dtype=float),
        b_ub=-np.ones(len(rows)),
        bounds=[(None, None)] * 10,
        method="highs",
    )
    if result.status != 0:
        return None
    for bound in (100, 10_000, 1_000_000, 100_000_000):
        witness = [
            Fraction(float(value)).limit_denominator(bound)
            for value in result.x
        ]
        margins = [
            sum(Fraction(a) * b for a, b in zip(row, witness))
            for row in rows
        ]
        if min(margins) > 0:
            return eligible, witness, margins
    return None


def main():
    start = time.time()
    coverage = load_gz(COVERAGE_PATH)
    patterns = sorted(coverage["pattern_multiplicities"])
    results = {}

    # Mandatory impossible targets are proved first.
    for bits, k in CANARIES:
        pattern = class_pattern(bits)
        key = f"{k}:{pattern}"
        if favorable_classes(pattern, k):
            raise RuntimeError(f"CANARY FAILURE: {bits}, k={k} satisfies criterion")
        solved = exact_formal_d_witness(pattern, k)
        if solved is None:
            raise RuntimeError(f"could not prove canary boundary: {bits}, k={k}")
        eligible, witness, margins = solved
        results[key] = {
            "status": "ALL_DEGREES_IMPOSSIBLE",
            "eligible_classes": eligible,
            "formal_D_strict_primal_witness": [
                fraction_text(value) for value in witness
            ],
            "minimum_margin": fraction_text(min(margins)),
        }
        print(
            f"canary PASS: bits={bits}, k={k}, margin={min(margins)}",
            flush=True,
        )

    processed = 0
    total = 2 * len(patterns)
    for pattern in patterns:
        multiplicity = coverage["pattern_multiplicities"][pattern]
        for k in (1, 2):
            key = f"{k}:{pattern}"
            favorable = favorable_classes(pattern, k)
            if favorable:
                results[key] = {
                    "status": "SINGLE_CLASS_IF_AND_ONLY_IF",
                    "favorable_classes": favorable,
                    "certificate_template": {
                        "side_multiplier_on_each_side": "1",
                        "weight_multiplier_t": "-2*q_ij*s_t*D_tij",
                    },
                }
            elif key not in results:
                solved = exact_formal_d_witness(pattern, k)
                if solved is None:
                    raise RuntimeError(
                        f"all-degree boundary witness failed for {key}"
                    )
                eligible, witness, margins = solved
                results[key] = {
                    "status": "ALL_DEGREES_IMPOSSIBLE",
                    "eligible_classes": eligible,
                    "formal_D_strict_primal_witness": [
                        fraction_text(value) for value in witness
                    ],
                    "minimum_margin": fraction_text(min(margins)),
                }
            processed += 1
            if processed % 1000 == 0 or processed == total:
                successes = sum(
                    result["status"] == "SINGLE_CLASS_IF_AND_ONLY_IF"
                    for result in results.values()
                )
                print(
                    f"boundary {processed}/{total}; success patterns={successes}; "
                    f"elapsed={time.time() - start:.1f}s",
                    flush=True,
                )

    labeled = {
        "SINGLE_CLASS_IF_AND_ONLY_IF": {"1": 0, "2": 0, "total": 0},
        "ALL_DEGREES_IMPOSSIBLE": {"1": 0, "2": 0, "total": 0},
    }
    for bits, k, key, _ in coverage["systems"]:
        status = results[key]["status"]
        labeled[status][str(k)] += 1
        labeled[status]["total"] += 1

    payload = {
        "schema": 1,
        "status": "complete_exact_all_degree_boundary",
        "theorem": (
            "Among all 66,280 labeled systems, a T-independent equal-pair "
            "certificate whose multiplier and weight-slack polynomials are "
            "coefficientwise nonnegative and whose identities hold as ordinary "
            "polynomial identities exists if and only if at least one equal-sign "
            "class (i,j) has q_ij*s_t=-1 for all t outside {i,j}. Consequently "
            "multi-class coefficientwise-positive polynomials of arbitrary "
            "degree extend the single-class family by zero systems."
        ),
        "formal_D_order": ["D" + "".join(map(str, triple)) for triple in TRIPLES],
        "n_distinct_patterns": len(patterns),
        "pattern_results": results,
        "labeled_counts": labeled,
        "canaries": [
            {
                "sigma_bits": bits,
                "k": k,
                "pattern_key": f"{k}:{class_pattern(bits)}",
                "outcome": results[f"{k}:{class_pattern(bits)}"]["status"],
            }
            for bits, k in CANARIES
        ],
        "proof_method": (
            "Sufficiency is the explicit single-class monomial certificate. "
            "For every pattern failing the criterion, the stored positive formal "
            "D point makes every eligible equal-pair primal row strictly "
            "positive at w=(1,1,1,1,1). Evaluation there excludes an ordinary "
            "coefficientwise-positive polynomial Gordan certificate at any "
            "degree."
        ),
        "elapsed_seconds": time.time() - start,
    }
    write_json_gz(OUTPUT, payload)
    print(json.dumps(labeled, indent=2), flush=True)
    print(f"wrote {OUTPUT} ({OUTPUT.stat().st_size} bytes)", flush=True)


if __name__ == "__main__":
    main()
