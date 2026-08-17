#!/usr/bin/env python3
"""Pre-a modular census for the diagonal-three next-wall target.

The exact b-eliminated chart has residuals R2,R3 and 21 critical minors.
This discovery-only program enumerates that eight-variable system over small
fields after inverting [1378], i-f, and i.  It checks precisely why the
additional parent unit

    B = [2357] [2458] [1267]

must be inverted before the candidate cover by [1468] or [5678] is true.
No finite-field count from this file advances characteristic-zero theorem
accounting.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

import numpy as np


HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import explore_diag3_triple_parentcell_macaulay as macaulay  # noqa: E402
import verify_diag3_triple_boundary_stratification as boundary  # noqa: E402


EXPECTED = {
    3: {
        "critical": 229,
        "B_nonzero": 4,
        "two_wall_union": 219,
        "uncovered": 10,
        "uncovered_B_zero": 10,
        "uncovered_2357": 5,
        "uncovered_2458": 6,
        "uncovered_1267": 5,
        "uncovered_attachment_union": 10,
    },
    5: {
        "critical": 3487,
        "B_nonzero": 76,
        "two_wall_union": 3195,
        "uncovered": 292,
        "uncovered_B_zero": 292,
        "uncovered_2357": 122,
        "uncovered_2458": 178,
        "uncovered_1267": 152,
        "uncovered_attachment_union": 292,
    },
}


def build_system():
    payload = json.loads(boundary.SYSTEM.read_text(encoding="ascii"))
    residual = tuple(
        boundary.decode_terms(record["terms"])
        for record in payload["equations"][:3]
    )
    walls = boundary.parent_wall_map()
    t = boundary.subtract(boundary.coordinate(8), boundary.coordinate(5))
    u = walls[boundary.PARENT_LOCALIZER]

    def eliminate_b(polynomial):
        constant_part, coefficient = boundary.split_linear(
            polynomial, boundary.HEIGHT
        )
        return boundary.add(
            boundary.multiply(t, constant_part),
            boundary.multiply(u, coefficient),
        )

    reduced_two = eliminate_b(residual[1])
    _constant_two, coefficient_two = boundary.split_linear(reduced_two, 0)
    expected_coefficient = boundary.multiply(
        boundary.multiply(walls["2357"], walls["2458"]),
        eliminate_b(walls["1267"]),
    )
    if coefficient_two != expected_coefficient:
        raise AssertionError("parent-unit coefficient B changed")

    # The reusable builder returns R2,R3, one inverse equation, and the 21
    # pivot minors.  Drop its inverse and impose units by point filtering.
    stored = macaulay.build_system()
    equations = stored[:2] + stored[3:]
    polynomials = {
        "localizer": macaulay.compact(
            boundary.multiply(
                boundary.multiply(u, t), boundary.coordinate(8)
            )
        ),
        "B": macaulay.compact(coefficient_two),
        "1468": macaulay.compact(eliminate_b(walls["1468"])),
        "5678": macaulay.compact(eliminate_b(walls["5678"])),
        "2357": macaulay.compact(walls["2357"]),
        "2458": macaulay.compact(walls["2458"]),
        "1267": macaulay.compact(eliminate_b(walls["1267"])),
    }
    return equations, polynomials


def points(prime):
    count = prime**8
    indices = np.arange(count, dtype=np.int64)
    answer = np.empty((count, 8), dtype=np.int16)
    for column in range(8):
        answer[:, column] = indices % prime
        indices //= prime
    return answer


def evaluate(polynomial, candidates, prime):
    answer = np.zeros(len(candidates), dtype=np.int64)
    powers = []
    for variable in range(8):
        maximum = max(
            (monomial[variable] for monomial in polynomial), default=0
        )
        variable_powers = [np.ones(len(candidates), dtype=np.int64)]
        for _exponent in range(maximum):
            variable_powers.append(
                variable_powers[-1] * candidates[:, variable] % prime
            )
        powers.append(variable_powers)
    for monomial, coefficient in polynomial.items():
        term = np.full(len(candidates), coefficient % prime, dtype=np.int64)
        for variable in range(8):
            exponent = monomial[variable]
            if exponent:
                term = term * powers[variable][exponent] % prime
        answer = (answer + term) % prime
    return answer


def enumerate_prime(equations, polynomials, prime, progress=False):
    candidates = points(prime)
    candidates = candidates[
        evaluate(polynomials["localizer"], candidates, prime) != 0
    ]
    for index in sorted(range(len(equations)), key=lambda item: len(equations[item])):
        candidates = candidates[evaluate(equations[index], candidates, prime) == 0]
        if progress:
            print(
                "p",
                prime,
                "equation",
                index,
                "terms",
                len(equations[index]),
                "survivors",
                len(candidates),
                flush=True,
            )

    zero = {
        label: evaluate(polynomial, candidates, prime) == 0
        for label, polynomial in polynomials.items()
        if label != "localizer"
    }
    two_wall_union = zero["1468"] | zero["5678"]
    uncovered = ~two_wall_union
    attachment_union = zero["2357"] | zero["2458"] | zero["1267"]
    return {
        "critical": len(candidates),
        "B_nonzero": int((~zero["B"]).sum()),
        "two_wall_union": int(two_wall_union.sum()),
        "uncovered": int(uncovered.sum()),
        "uncovered_B_zero": int((uncovered & zero["B"]).sum()),
        "uncovered_2357": int((uncovered & zero["2357"]).sum()),
        "uncovered_2458": int((uncovered & zero["2458"]).sum()),
        "uncovered_1267": int((uncovered & zero["1267"]).sum()),
        "uncovered_attachment_union": int((uncovered & attachment_union).sum()),
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--primes", default="3,5")
    parser.add_argument("--progress", action="store_true")
    arguments = parser.parse_args()
    primes = tuple(int(value) for value in arguments.primes.split(",") if value)
    equations, polynomials = build_system()
    print(
        "SYSTEM",
        {"equations": len(equations), "terms": sum(map(len, equations))},
    )
    print("DISCOVERY_ONLY pre-a parent-boundary census")
    for prime in primes:
        report = enumerate_prime(
            equations, polynomials, prime, arguments.progress
        )
        if prime in EXPECTED and report != EXPECTED[prime]:
            raise AssertionError(
                f"F_{prime} exploratory census changed: {report}"
            )
        print("FIELD", prime, report)
    print("CONCLUSION B=0 is the indispensable discarded parent boundary")
    print("SCOPE finite-field discovery only; rational saturation remains open")


if __name__ == "__main__":
    main()
