#!/usr/bin/env python3
"""Exhaustive small-field discovery for the seven-variable critical chart.

The exact parent-cell reduction is reconstructed independently from the
tracked 59-equation artifact.  Over F3, F5, and F7 this script enumerates the
chart localized at the units used by the b/a eliminations and the H_d pivot,
then checks the two-wall cover suggested by the data.  An optional F9 replay
uses the exact affinity of E_c in c to reduce 9^7 points to 9^6 base cases.

These finite-field counts are discovery evidence only.  In particular, the
cover by [1468] or [5678] must be lifted to an integer/rational saturation
certificate before it can support a characteristic-zero theorem.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

import numpy as np


HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import DIAG2_PIVOT_LABELED_PAIR_ORBITS_VERIFY as labeled  # noqa: E402
import verify_diag3_triple_boundary_stratification as boundary  # noqa: E402


ACTIVE = (2, 3, 4, 5, 6, 7, 8)
EXPECTED = {
    3: {"critical": 4, "1468": 4, "5678": 3, "union": 4},
    5: {"critical": 76, "1468": 65, "5678": 49, "union": 76},
    7: {"critical": 394, "1468": 322, "5678": 245, "union": 394},
}
EXPECTED_GF9 = {"critical": 1306, "1468": 1080, "5678": 841, "union": 1306}


def build_system():
    payload = json.loads(boundary.SYSTEM.read_text(encoding="ascii"))
    residual = tuple(
        boundary.decode_terms(record["terms"])
        for record in payload["equations"][:3]
    )
    t = boundary.subtract(boundary.coordinate(8), boundary.coordinate(5))
    u = boundary.subtract(
        boundary.multiply(boundary.coordinate(3), boundary.coordinate(8)),
        boundary.multiply(boundary.coordinate(5), boundary.coordinate(6)),
    )

    def eliminate_b(polynomial):
        constant_part, coefficient = boundary.split_linear(
            polynomial, boundary.HEIGHT
        )
        return boundary.add(
            boundary.multiply(t, constant_part),
            boundary.multiply(u, coefficient),
        )

    reduced_two, reduced_three = tuple(
        eliminate_b(polynomial) for polynomial in residual[1:]
    )
    constant_two, coefficient_two = boundary.split_linear(reduced_two, 0)
    constant_three, coefficient_three = boundary.split_linear(reduced_three, 0)
    hypersurface = boundary.subtract(
        boundary.multiply(coefficient_two, constant_three),
        boundary.multiply(coefficient_three, constant_two),
    )
    derivative_d = boundary.derivative(hypersurface, 3)
    equations = [hypersurface]
    equations.extend(
        boundary.derivative(hypersurface, variable)
        for variable in (2, 4, 7)
    )
    equations.append(
        boundary.subtract(
            boundary.multiply(t, boundary.derivative(hypersurface, 5)),
            boundary.multiply(
                boundary.subtract(boundary.coordinate(3), boundary.coordinate(6)),
                derivative_d,
            ),
        )
    )
    equations.append(
        boundary.add(
            boundary.multiply(
                boundary.coordinate(8), boundary.derivative(hypersurface, 6)
            ),
            boundary.multiply(boundary.coordinate(5), derivative_d),
        )
    )
    equations.append(
        boundary.subtract(
            boundary.multiply(
                boundary.multiply(boundary.coordinate(8), t),
                boundary.derivative(hypersurface, 8),
            ),
            boundary.multiply(
                boundary.multiply(
                    boundary.coordinate(5),
                    boundary.subtract(boundary.coordinate(6), boundary.coordinate(3)),
                ),
                derivative_d,
            ),
        )
    )
    localizer = boundary.multiply(
        boundary.multiply(u, t),
        boundary.multiply(boundary.coordinate(8), coefficient_two),
    )

    wall_numerators = {}
    for label, polynomial, *_rest in labeled.parent_bracket_factors():
        if str(label) not in {"1468", "5678"}:
            continue
        reduced_wall = eliminate_b(polynomial)
        wall_constant, wall_coefficient = boundary.split_linear(
            reduced_wall, 0
        )
        wall_numerators[str(label)] = boundary.subtract(
            boundary.multiply(coefficient_two, wall_constant),
            boundary.multiply(constant_two, wall_coefficient),
        )
    return tuple(equations), localizer, wall_numerators


def evaluate(polynomial, points, prime):
    answer = np.zeros(len(points), dtype=np.int64)
    powers = []
    for column, variable in enumerate(ACTIVE):
        maximum = max((monomial[variable] for monomial in polynomial), default=0)
        variable_powers = [np.ones(len(points), dtype=np.int64)]
        for _exponent in range(maximum):
            variable_powers.append(
                variable_powers[-1] * points[:, column] % prime
            )
        powers.append(variable_powers)
    for monomial, coefficient in polynomial.items():
        term = np.full(len(points), coefficient % prime, dtype=np.int64)
        for column, variable in enumerate(ACTIVE):
            exponent = monomial[variable]
            if exponent:
                term = term * powers[column][exponent] % prime
        answer = (answer + term) % prime
    return answer


def points(prime):
    count = prime ** len(ACTIVE)
    indices = np.arange(count, dtype=np.int64)
    answer = np.empty((count, len(ACTIVE)), dtype=np.int16)
    for column in range(len(ACTIVE)):
        answer[:, column] = indices % prime
        indices //= prime
    return answer


def enumerate_prime(equations, localizer, walls, prime, progress=False):
    candidates = points(prime)
    mask = evaluate(localizer, candidates, prime) != 0
    for index in sorted(range(len(equations)), key=lambda item: len(equations[item])):
        candidates = candidates[mask]
        mask = evaluate(equations[index], candidates, prime) == 0
        if progress:
            print(
                "p",
                prime,
                "equation",
                index,
                "terms",
                len(equations[index]),
                "survivors",
                int(mask.sum()),
                flush=True,
            )
    candidates = candidates[mask]
    zero_1468 = evaluate(walls["1468"], candidates, prime) == 0
    zero_5678 = evaluate(walls["5678"], candidates, prime) == 0
    return {
        "critical": len(candidates),
        "1468": int(zero_1468.sum()),
        "5678": int(zero_5678.sum()),
        "union": int((zero_1468 | zero_5678).sum()),
    }


def gf9_tables():
    """Arithmetic for F3[w]/(w^2+1), encoded as a+3*b."""

    order = 9
    add = np.empty((order, order), dtype=np.uint8)
    multiply = np.empty((order, order), dtype=np.uint8)
    negative = np.empty(order, dtype=np.uint8)
    for left in range(order):
        a, b = left % 3, left // 3
        negative[left] = (-a) % 3 + 3 * ((-b) % 3)
        for right in range(order):
            c, d = right % 3, right // 3
            add[left, right] = (a + c) % 3 + 3 * ((b + d) % 3)
            multiply[left, right] = (
                (a * c - b * d) % 3 + 3 * ((a * d + b * c) % 3)
            )
    inverse = np.zeros(order, dtype=np.uint8)
    for value in range(1, order):
        inverse[value] = next(
            candidate
            for candidate in range(1, order)
            if multiply[value, candidate] == 1
        )
    return add, multiply, negative, inverse


def evaluate_gf9(polynomial, candidates, add, multiply):
    answer = np.zeros(len(candidates), dtype=np.uint8)
    powers = []
    for column, variable in enumerate(ACTIVE):
        maximum = max((monomial[variable] for monomial in polynomial), default=0)
        variable_powers = [np.ones(len(candidates), dtype=np.uint8)]
        for _exponent in range(maximum):
            variable_powers.append(
                multiply[variable_powers[-1], candidates[:, column]]
            )
        powers.append(variable_powers)
    for monomial, coefficient in polynomial.items():
        term = np.full(len(candidates), coefficient % 3, dtype=np.uint8)
        for column, variable in enumerate(ACTIVE):
            exponent = monomial[variable]
            if exponent:
                term = multiply[term, powers[column][exponent]]
        answer = add[answer, term]
    return answer


def enumerate_gf9(equations, localizer, walls, progress=False):
    """Enumerate F9 by solving the affine equation E_c=0 for c."""

    order = 9
    add, multiply, negative, inverse = gf9_tables()
    count = order**6
    indices = np.arange(count, dtype=np.int64)
    base = np.empty((count, len(ACTIVE)), dtype=np.uint8)
    base[:, 0] = 0
    for column in range(1, len(ACTIVE)):
        base[:, column] = indices % order
        indices //= order

    constant, coefficient = boundary.split_linear(equations[1], ACTIVE[0])
    constant_values = evaluate_gf9(constant, base, add, multiply)
    coefficient_values = evaluate_gf9(coefficient, base, add, multiply)
    generic = coefficient_values != 0
    singular = (coefficient_values == 0) & (constant_values == 0)
    candidates = base[generic].copy()
    candidates[:, 0] = multiply[
        negative[constant_values[generic]], inverse[coefficient_values[generic]]
    ]
    if singular.any():
        exceptional = np.repeat(base[singular], order, axis=0)
        exceptional[:, 0] = np.tile(
            np.arange(order, dtype=np.uint8), int(singular.sum())
        )
        candidates = np.concatenate((candidates, exceptional))
    if progress:
        print(
            "F9 affine E_c solve",
            {
                "base": count,
                "generic": int(generic.sum()),
                "singular_bases": int(singular.sum()),
                "candidates": len(candidates),
            },
            flush=True,
        )

    candidates = candidates[
        evaluate_gf9(localizer, candidates, add, multiply) != 0
    ]
    remaining = tuple(index for index in range(len(equations)) if index != 1)
    for index in sorted(remaining, key=lambda item: len(equations[item])):
        candidates = candidates[
            evaluate_gf9(equations[index], candidates, add, multiply) == 0
        ]
        if progress:
            print(
                "F9 equation",
                index,
                "terms",
                len(equations[index]),
                "survivors",
                len(candidates),
                flush=True,
            )
    zero_1468 = evaluate_gf9(walls["1468"], candidates, add, multiply) == 0
    zero_5678 = evaluate_gf9(walls["5678"], candidates, add, multiply) == 0
    return {
        "critical": len(candidates),
        "1468": int(zero_1468.sum()),
        "5678": int(zero_5678.sum()),
        "union": int((zero_1468 | zero_5678).sum()),
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--primes", default="3,5,7")
    parser.add_argument("--gf9", action="store_true")
    parser.add_argument("--progress", action="store_true")
    arguments = parser.parse_args()
    primes = tuple(int(value) for value in arguments.primes.split(",") if value)
    equations, localizer, walls = build_system()
    print(
        "SYSTEM",
        {"equations": len(equations), "terms": sum(map(len, equations))},
    )
    print("DISCOVERY_ONLY finite-field wall cover")
    for prime in primes:
        report = enumerate_prime(
            equations, localizer, walls, prime, arguments.progress
        )
        if prime in EXPECTED and report != EXPECTED[prime]:
            raise AssertionError(
                f"F_{prime} exploratory census changed: {report}"
            )
        print("FIELD", prime, report)
    if arguments.gf9:
        report = enumerate_gf9(
            equations, localizer, walls, arguments.progress
        )
        if report != EXPECTED_GF9:
            raise AssertionError(f"F9 exploratory census changed: {report}")
        print("FIELD 9", report)
    print("CANDIDATE exact next-wall cover: [1468] or [5678]")
    print("SCOPE modular discovery only; rational saturation remains open")


if __name__ == "__main__":
    main()
