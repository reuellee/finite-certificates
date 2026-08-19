#!/usr/bin/env python3
"""Build the exact height-b critical system for the diagonal-three canary.

The output is deterministic canonical JSON.  It contains the three residual
factor equations and all 56 formal 3-by-3 minors of the Jacobian columns
other than b.  Zero minors are retained so the column-subset census is
explicit rather than inferred from the nonzero generators.
"""

from __future__ import annotations

from itertools import combinations
import json
from pathlib import Path
import sys


HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import DIAG2_PIVOT_LABELED_PAIR_ORBITS_VERIFY as labeled  # noqa: E402
import DIAG2_PIVOT_REPRESENTATIVE_TRIPLES_VERIFY as triples  # noqa: E402


OUTPUT = HERE / "data/DIAG3_triple_fullspace_critical_h1.json"
SCHEMA = "diag3-triple-fullspace-critical-system-v1"
VARIABLES = tuple("abcdefghi")
HEIGHT = 1
PRESENTATION = (5_563, 16_134, 19_284)
CANONICAL = (5_563, 4_373, 23_221)
PERMUTATION = (6, 2, 5, 8, 3, 4, 1, 7)


def terms(polynomial):
    return [
        [int(coefficient), list(monomial)]
        for monomial, coefficient in sorted(polynomial.items())
    ]


def build_payload():
    _occurrences, _occurrence_factor, factor_polynomials = (
        labeled.factor_polynomials()
    )
    residual = {
        row: factor_polynomials[factor]
        for row, factor in enumerate(PRESENTATION)
    }
    equations = [
        {
            "kind": "factor",
            "factor": factor,
            "terms": terms(factor_polynomials[factor]),
        }
        for factor in PRESENTATION
    ]
    columns = tuple(variable for variable in range(9) if variable != HEIGHT)
    for chosen in combinations(columns, 3):
        equations.append(
            {
                "kind": "height_minor",
                "columns": list(chosen),
                "terms": terms(
                    triples.jacobian_minor(residual, (0, 1, 2), chosen)
                ),
            }
        )
    if len(equations) != 59:
        raise AssertionError("critical-system equation census changed")
    return {
        "schema": SCHEMA,
        "variables": list(VARIABLES),
        "height_index": HEIGHT,
        "height_variable": VARIABLES[HEIGHT],
        "named_presentation": list(PRESENTATION),
        "canonical_row": list(CANONICAL),
        "named_to_canonical_permutation": list(PERMUTATION),
        "equations": equations,
    }


def main():
    payload = build_payload()
    encoded = (
        json.dumps(payload, sort_keys=True, separators=(",", ":")) + "\n"
    ).encode("ascii")
    OUTPUT.write_bytes(encoded)
    print("WROTE", OUTPUT, len(encoded), "bytes")


if __name__ == "__main__":
    main()
