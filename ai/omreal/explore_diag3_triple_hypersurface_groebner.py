#!/usr/bin/env python3
"""Modular Gröbner discovery for the seven-variable hard-canary chart.

The exact verifier proves that parent-cell criticality reduces to seven
equations on one hypersurface after eliminating b and a.  This script adds
one inverse for the units used by those eliminations and runs a bounded
finite-field Buchberger search.  It is discovery-only and cannot advance the
characteristic-zero theorem ledger.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys


HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import explore_diag3_triple_lagrange_groebner as groebner  # noqa: E402
import verify_diag3_triple_boundary_stratification as boundary  # noqa: E402


ACTIVE = (2, 3, 4, 5, 6, 7, 8)
ACTIVE_NAMES = tuple(boundary.VARIABLES[index] for index in ACTIVE)
VARIABLES = ()
ZERO = ()


def configure_order(with_inverse):
    global VARIABLES, ZERO
    VARIABLES = ACTIVE_NAMES + (("z",) if with_inverse else ())
    ZERO = (0,) * len(VARIABLES)


def compact(polynomial, prime):
    return {
        tuple(monomial[index] for index in ACTIVE)
        + (0,) * (len(VARIABLES) - len(ACTIVE)): coefficient % prime
        for monomial, coefficient in polynomial.items()
        if coefficient % prime
    }


def compact_add(left, right, prime):
    answer = dict(left)
    for monomial, coefficient in right.items():
        value = (answer.get(monomial, 0) + coefficient) % prime
        if value:
            answer[monomial] = value
        else:
            answer.pop(monomial, None)
    return answer


def compact_multiply(left, right, prime):
    answer = {}
    for left_monomial, left_coefficient in left.items():
        for right_monomial, right_coefficient in right.items():
            monomial = tuple(
                x + y for x, y in zip(left_monomial, right_monomial)
            )
            answer[monomial] = (
                answer.get(monomial, 0)
                + left_coefficient * right_coefficient
            ) % prime
    return {monomial: coefficient for monomial, coefficient in answer.items() if coefficient}


def build_exact_system(excluded_walls=()):
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

    # These are precisely the units used by b elimination, a elimination,
    # and the H_d pivot.  Repeated factors are unnecessary.
    localizer_factors = [u, t, boundary.coordinate(8), coefficient_two]
    walls = boundary.parent_wall_map()
    for label in excluded_walls:
        reduced_wall = eliminate_b(walls[label])
        wall_constant, wall_coefficient = boundary.split_linear(
            reduced_wall, 0
        )
        # On R2=constant_two+a*coefficient_two=0 and coefficient_two!=0,
        # this is coefficient_two times the wall after eliminating a.
        wall_numerator = boundary.subtract(
            boundary.multiply(coefficient_two, wall_constant),
            boundary.multiply(constant_two, wall_coefficient),
        )
        localizer_factors.append(wall_numerator)
    return tuple(equations), tuple(localizer_factors)


def build_system(prime, excluded_walls=(), localized_units=False):
    equations, localizer_factors = build_exact_system(excluded_walls)
    compact_equations = [compact(polynomial, prime) for polynomial in equations]
    compact_units = tuple(compact(factor, prime) for factor in localizer_factors)
    if not localized_units:
        localizer = {ZERO: 1}
        for factor in compact_units:
            localizer = compact_multiply(localizer, factor, prime)
        z_monomial = [0] * len(VARIABLES)
        z_monomial[-1] = 1
        z = {tuple(z_monomial): 1}
        inverse = compact_add(
            compact_multiply(z, localizer, prime),
            {ZERO: -1},
            prime,
        )
        compact_equations.append(inverse)
    return tuple(compact_equations), compact_units


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--prime", type=int, default=47)
    parser.add_argument("--maximum-basis", type=int, default=120)
    parser.add_argument("--maximum-pairs", type=int, default=1000)
    parser.add_argument(
        "--exclude-walls",
        default="",
        help="comma-separated parent walls multiplied into the localizer",
    )
    parser.add_argument(
        "--localized-units",
        action="store_true",
        help="strip exact unit factors during reduction instead of adding z",
    )
    parser.add_argument("--progress", action="store_true")
    arguments = parser.parse_args()
    excluded_walls = tuple(
        label for label in arguments.exclude_walls.split(",") if label
    )

    configure_order(with_inverse=not arguments.localized_units)

    groebner.VARIABLES = VARIABLES
    groebner.ZERO = ZERO
    generators, unit_factors = build_system(
        arguments.prime,
        excluded_walls,
        arguments.localized_units,
    )
    groebner.UNIT_FACTORS = (
        tuple(groebner.monic(factor, arguments.prime) for factor in unit_factors)
        if arguments.localized_units
        else ()
    )
    print("VARIABLES", VARIABLES)
    print(
        "GENERATORS",
        len(generators),
        tuple((max(map(sum, poly)), len(poly)) for poly in generators),
    )
    print("EXCLUDED_WALLS", excluded_walls)
    print("LOCALIZED_UNITS", len(groebner.UNIT_FACTORS))
    print("DISCOVERY_ONLY modular hypersurface system")
    basis, processed, complete = groebner.buchberger(
        generators,
        arguments.prime,
        arguments.maximum_basis,
        arguments.maximum_pairs,
        arguments.progress,
    )
    report = {
        "prime": arguments.prime,
        "basis": len(basis),
        "pairs_processed": processed,
        "complete": complete,
        "unit_ideal": any(set(polynomial) == {ZERO} for polynomial in basis),
        "leading_dimension_upper_bound": groebner.dimension_upper_bound(basis),
        "maximum_degree": max(max(map(sum, polynomial)) for polynomial in basis),
        "maximum_terms": max(map(len, basis)),
    }
    print("RESULT", report)


if __name__ == "__main__":
    main()
