#!/usr/bin/env python3
"""Export the seven-variable hard-canary hypersurface for ``msolve -S``.

The exact parent-cell graph identity eliminates ``a`` after the earlier
height-coordinate elimination.  The base output has seven hypersurface
critical equations and a final localizer polynomial.  Optional switches add
the exact ``P=0`` or ``L=0`` rank-drop branches, invert either factor, or use
branch inverse equations while natively saturating the base units.  Thus the
file is an exact modular-discovery input for bounded msolve experiments.
"""

from __future__ import annotations

import argparse
import hashlib
from pathlib import Path
import sys


HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import explore_diag3_triple_hypersurface_groebner as chart  # noqa: E402
import export_diag3_triple_two_pivot_msolve as common  # noqa: E402
import DIAG2_PIVOT_REPRESENTATIVE_TRIPLES_VERIFY as triples  # noqa: E402
import verify_diag3_triple_boundary_stratification as boundary  # noqa: E402
from verify_diag3_triple_two_pivot_rank_drop import EXPECTED_P  # noqa: E402


DEFAULT_ORDER = "cehdfgi"


def rank_drop_factors(generators):
    hypersurface_e = generators[2]
    _constant, slope = boundary.split_linear(hypersurface_e, 4)
    if any(coefficient % 2 for coefficient in slope.values()):
        raise AssertionError("the E_e slope lost its content two")
    half_slope = {
        monomial: coefficient // 2
        for monomial, coefficient in slope.items()
    }
    t = boundary.subtract(boundary.coordinate(8), boundary.coordinate(5))
    primitive_l = triples.exact_divide(half_slope, t)
    if primitive_l is None or len(primitive_l) != 60:
        raise AssertionError("the primitive L factor changed")
    return {"p": EXPECTED_P, "l": primitive_l}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--prime", type=int, required=True)
    parser.add_argument("--order", default=DEFAULT_ORDER)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument(
        "--exclude-walls",
        default="1468,5678",
        help="comma-separated target walls included in the localizer",
    )
    parser.add_argument(
        "--mode",
        choices=("saturation", "hybrid", "separate-inverses"),
        default="saturation",
        help="native saturation, branch inverses plus saturation, or all inverses",
    )
    parser.add_argument(
        "--zero-branch",
        choices=("none", "p", "l", "p-and-l"),
        default="none",
        help="add an exact rank-drop branch equation before localization",
    )
    parser.add_argument(
        "--invert-branch",
        choices=("none", "p", "l", "p-and-l"),
        default="none",
        help="include exact rank-drop factors in the localizer",
    )
    arguments = parser.parse_args()

    variables = tuple(arguments.order)
    if sorted(variables) != sorted(chart.ACTIVE_NAMES):
        raise SystemExit(
            f"--order must be a permutation of {''.join(chart.ACTIVE_NAMES)}"
        )
    if (
        arguments.prime < 3
        or arguments.prime >= 2**31
        or not common.is_prime_32(arguments.prime)
        or (arguments.mode in ("saturation", "hybrid") and arguments.prime < 2**16)
    ):
        lower = "2^16" if arguments.mode in ("saturation", "hybrid") else "3"
        raise SystemExit(
            f"--prime must be a prime in [{lower}, 2^31) for msolve"
        )
    excluded_walls = tuple(
        label for label in arguments.exclude_walls.split(",") if label
    )

    generators, base_unit_factors = chart.build_exact_system(excluded_walls)
    factors = rank_drop_factors(generators)
    zero_labels = () if arguments.zero_branch == "none" else tuple(
        arguments.zero_branch.split("-and-")
    )
    invert_labels = () if arguments.invert_branch == "none" else tuple(
        arguments.invert_branch.split("-and-")
    )
    if set(zero_labels) & set(invert_labels):
        raise SystemExit("a rank-drop factor cannot be both zero and inverted")
    generators += tuple(factors[label] for label in zero_labels)
    branch_unit_factors = tuple(factors[label] for label in invert_labels)
    unit_factors = (
        base_unit_factors
        if arguments.mode == "hybrid"
        else base_unit_factors + branch_unit_factors
    )
    localizer = common.multiply_all(unit_factors)
    compact_generators = tuple(
        common.reorder(polynomial, variables) for polynomial in generators
    )
    if arguments.mode == "saturation":
        output_variables = variables
        compact = compact_generators + (common.reorder(localizer, variables),)
    else:
        inverse_factors = (
            branch_unit_factors
            if arguments.mode == "hybrid"
            else unit_factors
        )
        inverse_variables = tuple(f"z{index}" for index in range(len(inverse_factors)))
        output_variables = variables + inverse_variables
        extension = (0,) * len(inverse_variables)
        compact = tuple(
            {monomial + extension: coefficient for monomial, coefficient in polynomial.items()}
            for polynomial in compact_generators
        )
        inverse_equations = []
        for index, factor in enumerate(inverse_factors):
            equation = {}
            for monomial, coefficient in common.reorder(factor, variables).items():
                powers = [0] * len(inverse_variables)
                powers[index] = 1
                equation[monomial + tuple(powers)] = coefficient
            equation[(0,) * len(output_variables)] = -1
            inverse_equations.append(equation)
        compact += tuple(inverse_equations)
        if arguments.mode == "hybrid":
            compact += (
                {
                    monomial + extension: coefficient
                    for monomial, coefficient in common.reorder(
                        localizer, variables
                    ).items()
                },
            )
    lines = [",".join(output_variables), str(arguments.prime)]
    lines.extend(
        common.format_polynomial(polynomial, output_variables, arguments.prime)
        + ("," if index + 1 < len(compact) else "")
        for index, polynomial in enumerate(compact)
    )
    payload = "\n".join(lines) + "\n"
    arguments.output.write_text(payload, encoding="ascii")

    print("OUTPUT", arguments.output)
    print("SHA256", hashlib.sha256(payload.encode("ascii")).hexdigest())
    print("PRIME", arguments.prime)
    print("ORDER", arguments.order)
    print("MODE", arguments.mode)
    print("ZERO_BRANCH", zero_labels)
    print("INVERT_BRANCH", invert_labels)
    print("EXCLUDED_WALLS", excluded_walls)
    print(
        "GENERATORS",
        tuple((max(map(sum, polynomial)), len(polynomial)) for polynomial in generators),
    )
    print(
        "UNIT_FACTORS",
        tuple((max(map(sum, polynomial)), len(polynomial)) for polynomial in unit_factors),
    )
    print(
        "BRANCH_INVERSES",
        tuple(
            (max(map(sum, polynomial)), len(polynomial))
            for polynomial in branch_unit_factors
        ),
    )
    print("LOCALIZER", (max(map(sum, localizer)), len(localizer)))
    command = (
        "msolve -S -g 2"
        if arguments.mode in ("saturation", "hybrid")
        else "msolve -g 2"
    )
    print(f"SCOPE discovery-only input for: {command} -f INPUT")


if __name__ == "__main__":
    main()
