#!/usr/bin/env python3
"""Bounded modular pilot for the diagonal-three two-wall saturation.

The exact boundary verifier proves that two parent-unit columns, ``d`` and
``a``, reduce the 21 parent-cell critical minors to the six minors
``M_da*``.  This script constructs that smaller system, localizes at the
base parent units and at the complement of the two candidate attachment
walls, and runs the repository's bounded sparse Buchberger implementation.

All output is discovery-only.  In particular, a modular unit ideal would
still require rational reconstruction and an independent exact replay.
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


ACTIVE = tuple(variable for variable in range(9) if variable != boundary.HEIGHT)
VARIABLES = tuple(boundary.VARIABLES[variable] for variable in ACTIVE)
ZERO = (0,) * len(VARIABLES)
TARGET_WALLS = ("1468", "5678")


def compact(polynomial, prime):
    return {
        tuple(monomial[variable] for variable in ACTIVE): coefficient % prime
        for monomial, coefficient in polynomial.items()
        if coefficient % prime
    }


def build_exact_system():
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

    reduced = tuple(eliminate_b(polynomial) for polynomial in residual[1:])
    _constant_two, coefficient_two = boundary.split_linear(reduced[0], 0)
    expected_coefficient = boundary.multiply(
        boundary.multiply(walls["2357"], walls["2458"]),
        eliminate_b(walls["1267"]),
    )
    if coefficient_two != expected_coefficient:
        raise AssertionError("parent-unit a pivot changed")

    height = {
        variable: boundary.subtract(
            boundary.multiply(t, boundary.derivative(u, variable)),
            boundary.multiply(u, boundary.derivative(t, variable)),
        )
        for variable in ACTIVE
    }
    remaining = tuple(variable for variable in ACTIVE if variable not in (3, 0))
    critical = []
    for variable in remaining:
        critical.append(
            boundary.determinant3(
                [
                    [height[index] for index in (3, 0, variable)],
                    [
                        boundary.derivative(reduced[0], index)
                        for index in (3, 0, variable)
                    ],
                    [
                        boundary.derivative(reduced[1], index)
                        for index in (3, 0, variable)
                    ],
                ]
            )
        )

    wall_numerators = tuple(eliminate_b(walls[label]) for label in TARGET_WALLS)
    unit_polynomials = (
        u,
        t,
        boundary.coordinate(8),
        coefficient_two,
    ) + wall_numerators
    generators = reduced + tuple(critical)

    rank_drop_ae = boundary.subtract(
        boundary.multiply(
            boundary.derivative(reduced[0], 0),
            boundary.derivative(reduced[1], 4),
        ),
        boundary.multiply(
            boundary.derivative(reduced[0], 4),
            boundary.derivative(reduced[1], 0),
        ),
    )
    if len(rank_drop_ae) != 341:
        raise AssertionError("ae rank-drop census changed")
    return generators, unit_polynomials, {
        "variables": VARIABLES,
        "residual_terms": tuple(map(len, reduced)),
        "critical_terms": tuple(map(len, critical)),
        "ae_rank_drop_terms": len(rank_drop_ae),
        "base_units": ("1378", "2378", "1238", "2357*2458*1267"),
        "target_walls": TARGET_WALLS,
    }


def build_system(prime):
    generators, units, census = build_exact_system()
    return (
        tuple(compact(polynomial, prime) for polynomial in generators),
        tuple(compact(polynomial, prime) for polynomial in units),
        census,
    )


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--prime", type=int, default=3)
    parser.add_argument("--maximum-basis", type=int, default=12)
    parser.add_argument("--maximum-pairs", type=int, default=50)
    parser.add_argument("--progress", action="store_true")
    arguments = parser.parse_args()

    groebner.VARIABLES = VARIABLES
    groebner.ZERO = ZERO
    generators, units, census = build_system(arguments.prime)
    groebner.UNIT_FACTORS = tuple(
        groebner.monic(unit, arguments.prime) for unit in units
    )
    print("SYSTEM", census)
    print(
        "GENERATORS",
        tuple(
            (max(map(sum, polynomial)), len(polynomial))
            for polynomial in generators
        ),
    )
    print(
        "UNITS",
        tuple(
            (max(map(sum, polynomial)), len(polynomial))
            for polynomial in units
        ),
    )
    print("DISCOVERY_ONLY modular two-wall complement")
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
    print("SCOPE bounded modular pilot; rational saturation remains open")


if __name__ == "__main__":
    main()
