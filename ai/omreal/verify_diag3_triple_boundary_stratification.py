#!/usr/bin/env python3
"""Exact boundary stratification of the diagonal-three hard canary.

This checker refines the raw height-b critical gate for the named triple
``(5563,16134,19284)``.  It distinguishes the height-critical ideal from
the intrinsic singular ideal of the three residual equations, enumerates
all maximal coordinate subspaces in both ideals, certifies smooth linear
components by exact Jacobian ranks, and identifies the first parent wall
that contains every boundary piece found by the calculation.

Nothing here is a global primary decomposition or a noncompactness proof.
In particular, theorem accounting remains unchanged.
"""

from __future__ import annotations

from fractions import Fraction
import hashlib
from itertools import combinations, permutations
import json
from pathlib import Path
import sys


HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import DIAG2_PIVOT_LABELED_PAIR_ORBITS_VERIFY as labeled  # noqa: E402
import DIAG2_PIVOT_REPRESENTATIVE_TRIPLES_VERIFY as triples  # noqa: E402


SYSTEM = HERE / "data/DIAG3_triple_fullspace_critical_h1.json"
SYSTEM_SHA256 = "c9244a47ded5736e7afe724a9914e75631a22b78653442e88c14f5c397919eb8"
VARIABLES = tuple("abcdefghi")
ZERO = (0,) * 9
HEIGHT = 1
PRESENTATION = (5_563, 16_134, 19_284)
PARENT_LOCALIZER = "1378"

RAW_COORDINATE_ANTICHAIN = (
    (0, 1, 2, 3, 5),
    (1, 2, 3, 4, 5),
    (0, 1, 2, 3, 6, 7),
    (0, 1, 2, 4, 5, 8),
    (0, 1, 2, 5, 7, 8),
    (0, 1, 2, 6, 7, 8),
    (0, 1, 3, 4, 6, 7),
    (0, 1, 3, 6, 7, 8),
    (0, 2, 3, 5, 6, 8),
    (1, 2, 3, 4, 6, 7),
    (1, 2, 3, 5, 6, 8),
    (1, 2, 4, 5, 7, 8),
    (3, 4, 5, 6, 7, 8),
)

SINGULAR_COORDINATE_ANTICHAIN = (
    (0, 1, 2, 3, 5),
    (1, 2, 3, 4, 5),
    (0, 1, 2, 4, 5, 8),
    (0, 1, 2, 6, 7, 8),
    (0, 1, 3, 4, 6, 7),
    (0, 2, 3, 5, 6, 8),
    (1, 2, 3, 5, 6, 8),
    (1, 2, 4, 5, 7, 8),
    (3, 4, 5, 6, 7, 8),
    (0, 1, 3, 5, 6, 7, 8),
)

RAW_COMMON_PARENT_WALLS = ("1268", "1378", "1678")
SINGULAR_COMMON_PARENT_WALLS = ("1268", "1367", "1378", "1678")
NONCOORDINATE_AMBIENT_ZERO = (1, 3, 5, 6, 8)
NONCOORDINATE_FACTOR = {
    (0, 0, 1, 0, 0, 0, 0, 1, 0): 1,
    (0, 0, 1, 0, 1, 0, 0, 1, 0): -1,
    (1, 0, 0, 0, 1, 0, 0, 0, 0): -1,
    (1, 0, 0, 0, 1, 0, 0, 1, 0): 1,
}
COORDINATE_C = {(0, 0, 1, 0, 0, 0, 0, 0, 0): 1}


def sha256(path):
    digest = hashlib.sha256()
    with path.open("rb") as source:
        while block := source.read(1 << 20):
            digest.update(block)
    return digest.hexdigest()


def add(left, right):
    answer = dict(left)
    for monomial, coefficient in right.items():
        answer[monomial] = answer.get(monomial, 0) + coefficient
        if not answer[monomial]:
            del answer[monomial]
    return answer


def multiply(left, right):
    answer = {}
    for left_monomial, left_coefficient in left.items():
        for right_monomial, right_coefficient in right.items():
            monomial = tuple(
                x + y for x, y in zip(left_monomial, right_monomial)
            )
            answer[monomial] = answer.get(monomial, 0) + (
                left_coefficient * right_coefficient
            )
    return {monomial: coefficient for monomial, coefficient in answer.items() if coefficient}


def subtract(left, right):
    return add(left, {monomial: -coefficient for monomial, coefficient in right.items()})


def coordinate(variable):
    monomial = [0] * 9
    monomial[variable] = 1
    return {tuple(monomial): 1}


def derivative(polynomial, variable):
    answer = {}
    for monomial, coefficient in polynomial.items():
        exponent = monomial[variable]
        if exponent:
            derived = list(monomial)
            derived[variable] -= 1
            answer[tuple(derived)] = coefficient * exponent
    return answer


def determinant3(matrix):
    answer = {}
    for permutation in permutations(range(3)):
        inversions = sum(
            permutation[left] > permutation[right]
            for left in range(3)
            for right in range(left + 1, 3)
        )
        term = {ZERO: -1 if inversions & 1 else 1}
        for row in range(3):
            term = multiply(term, matrix[row][permutation[row]])
        answer = add(answer, term)
    return answer


def jacobian_minor(residual, columns):
    return determinant3(
        [
            [derivative(residual[row], column) for column in columns]
            for row in range(3)
        ]
    )


def decode_terms(raw):
    answer = {}
    for coefficient, exponent in raw:
        monomial = tuple(int(value) for value in exponent)
        if len(monomial) != 9 or monomial in answer or not coefficient:
            raise AssertionError("noncanonical polynomial encoding")
        answer[monomial] = int(coefficient)
    return answer


def vanishes_on_coordinate_subspace(polynomial, zero_variables):
    zero_variables = set(zero_variables)
    return all(
        any(monomial[variable] for variable in zero_variables)
        for monomial in polynomial
    )


def coordinate_antichain(generators, variables=tuple(range(9))):
    """Inclusion-minimal zero sets, hence maximal coordinate subspaces."""

    hits = []
    for size in range(len(variables) + 1):
        for chosen in combinations(variables, size):
            chosen_set = set(chosen)
            if any(set(previous) <= chosen_set for previous in hits):
                continue
            if all(
                vanishes_on_coordinate_subspace(polynomial, chosen)
                for polynomial in generators
            ):
                hits.append(chosen)
    return tuple(hits)


def evaluate(polynomial, point):
    value = 0
    for monomial, coefficient in polynomial.items():
        term = coefficient
        for coordinate, exponent in zip(point, monomial):
            term *= coordinate**exponent
        value += term
    return value


def restrict(polynomial, zero_variables):
    zero_variables = set(zero_variables)
    return {
        monomial: coefficient
        for monomial, coefficient in polynomial.items()
        if not any(monomial[variable] for variable in zero_variables)
    }


def exact_rank(rows):
    matrix = [list(map(Fraction, row)) for row in rows if any(row)]
    if not matrix:
        return 0
    columns = len(matrix[0])
    rank = 0
    for column in range(columns):
        pivot = next(
            (row for row in range(rank, len(matrix)) if matrix[row][column]),
            None,
        )
        if pivot is None:
            continue
        matrix[rank], matrix[pivot] = matrix[pivot], matrix[rank]
        pivot_value = matrix[rank][column]
        matrix[rank] = [value / pivot_value for value in matrix[rank]]
        for row in range(len(matrix)):
            if row == rank or not matrix[row][column]:
                continue
            scalar = matrix[row][column]
            matrix[row] = [
                value - scalar * pivot_entry
                for value, pivot_entry in zip(matrix[row], matrix[rank])
            ]
        rank += 1
        if rank == columns:
            break
    return rank


def jacobian_rank(generators, point):
    rows = [
        [evaluate(derivative(polynomial, variable), point) for variable in range(9)]
        for polynomial in generators
    ]
    return exact_rank(rows)


def parent_wall_map():
    return {
        str(label): polynomial
        for label, polynomial, *_rest in labeled.parent_bracket_factors()
    }


def common_parent_walls(antichain, walls):
    return tuple(
        label
        for label, polynomial in walls.items()
        if all(
            vanishes_on_coordinate_subspace(polynomial, zero_variables)
            for zero_variables in antichain
        )
    )


def point_on(zero_variables):
    values = (2, 3, 5, 7, 11, 13, 17, 19, 23)
    return tuple(0 if variable in zero_variables else values[variable] for variable in range(9))


def scalar_multiple(polynomial, target):
    if not polynomial:
        return 0
    common = set(polynomial) & set(target)
    if not common:
        return None
    monomial = min(common)
    ratio = Fraction(polynomial[monomial], target[monomial])
    if set(polynomial) != set(target):
        return None
    if all(Fraction(polynomial[key], target[key]) == ratio for key in target):
        return ratio
    return None


def split_linear(polynomial, variable):
    constant_part = {}
    linear_coefficient = {}
    for monomial, coefficient in polynomial.items():
        exponent = monomial[variable]
        if exponent > 1:
            raise AssertionError("expected an affine polynomial")
        if not exponent:
            constant_part[monomial] = coefficient
            continue
        reduced = list(monomial)
        reduced[variable] = 0
        linear_coefficient[tuple(reduced)] = coefficient
    return constant_part, linear_coefficient


def split_by_degree(polynomial, variable):
    """Return coefficients in one variable, retaining ambient exponents."""

    degree = max((monomial[variable] for monomial in polynomial), default=0)
    coefficients = [dict() for _ in range(degree + 1)]
    for monomial, coefficient in polynomial.items():
        exponent = monomial[variable]
        reduced = list(monomial)
        reduced[variable] = 0
        coefficients[exponent][tuple(reduced)] = coefficient
    return tuple(coefficients)


def verify_reduced_height_chart(residual, parent_localizer):
    """Eliminate b exactly after localizing the first parent wall.

    Put t=i-f and u=di-fg.  The first residual is q1=u-bt, so on u!=0
    both b and t are units and b=u/t.  For qj=Aj+bBj define
    Rj=tAj+uBj.  On Rj=0 the gradient identity checked below gives

        dRj = t*(dqj at b=u/t) + Bj*(dq1 at b=u/t).

    Together with H=t*du-u*dt=t*(dq1 at b=u/t), this is a triangular
    row operation of determinant t^3.  Hence the height-critical minors
    are equivalent to the minors of (H,dR2,dR3) in the u*t-local chart.
    """

    t = subtract(coordinate(8), coordinate(5))
    b = coordinate(HEIGHT)
    if residual[0] != subtract(parent_localizer, multiply(b, t)):
        raise AssertionError("q5563 is no longer [1378]-b(i-f)")
    active = tuple(variable for variable in range(9) if variable != HEIGHT)
    reduced_residuals = []
    coefficients = []
    constant_parts = []
    for polynomial in residual[1:]:
        constant_part, coefficient = split_linear(polynomial, HEIGHT)
        reduced_residuals.append(
            add(
                multiply(t, constant_part),
                multiply(parent_localizer, coefficient),
            )
        )
        coefficients.append(coefficient)
        constant_parts.append(constant_part)
    reduced_residuals = tuple(reduced_residuals)
    if tuple(
        (len(polynomial), min(map(sum, polynomial)), max(map(sum, polynomial)))
        for polynomial in reduced_residuals
    ) != ((75, 4, 6), (31, 4, 5)):
        raise AssertionError("eight-variable residual census changed")

    height_numerator = tuple(
        subtract(
            multiply(t, derivative(parent_localizer, variable)),
            multiply(parent_localizer, derivative(t, variable)),
        )
        for variable in active
    )
    for reduced, constant_part, coefficient in zip(
        reduced_residuals, constant_parts, coefficients
    ):
        for column, variable in enumerate(active):
            fixed_b_numerator = add(
                multiply(t, derivative(constant_part, variable)),
                multiply(parent_localizer, derivative(coefficient, variable)),
            )
            left = multiply(t, derivative(reduced, variable))
            right = add(
                add(
                    multiply(t, fixed_b_numerator),
                    multiply(coefficient, height_numerator[column]),
                ),
                multiply(reduced, derivative(t, variable)),
            )
            if left != right:
                raise AssertionError("localized gradient row operation failed")

    reduced_minors = []
    for chosen in combinations(range(8), 3):
        matrix = [[height_numerator[column] for column in chosen]]
        matrix.extend(
            [
                derivative(polynomial, active[column])
                for column in chosen
            ]
            for polynomial in reduced_residuals
        )
        reduced_minors.append(determinant3(matrix))
    census = {
        "formal_minors": len(reduced_minors),
        "nonzero_minors": sum(bool(polynomial) for polynomial in reduced_minors),
        "nonzero_minor_terms": sum(len(polynomial) for polynomial in reduced_minors),
        "minor_degrees": tuple(
            sorted(
                {
                    max(map(sum, polynomial))
                    for polynomial in reduced_minors
                    if polynomial
                }
            )
        ),
    }
    expected = {
        "formal_minors": 56,
        "nonzero_minors": 52,
        "nonzero_minor_terms": 50_034,
        "minor_degrees": (11,),
    }
    if census != expected:
        raise AssertionError(f"eight-variable critical census changed: {census}")
    if any(
        monomial[HEIGHT]
        for polynomial in reduced_residuals + tuple(reduced_minors)
        for monomial in polynomial
    ):
        raise AssertionError("eliminated height b reappeared")
    reduced_generators = reduced_residuals + tuple(
        polynomial for polynomial in reduced_minors if polynomial
    )
    reduced_antichain = coordinate_antichain(reduced_generators, active)
    expected_antichain = (
        (5, 8),
        (0, 2, 3, 5),
        (2, 3, 4, 5),
        (0, 2, 3, 6, 7),
        (0, 2, 6, 7, 8),
        (0, 3, 4, 6, 7),
        (0, 3, 6, 7, 8),
        (2, 3, 4, 6, 7),
    )
    if reduced_antichain != expected_antichain:
        raise AssertionError(
            f"eight-variable coordinate antichain changed: {reduced_antichain}"
        )
    if not all(
        vanishes_on_coordinate_subspace(parent_localizer, zero_variables)
        for zero_variables in reduced_antichain
    ):
        raise AssertionError("a reduced coordinate stratum survives u-localization")

    # In the genuine parent cell, i=[1238] and t=-(2378) are units.  The d
    # entry of H is i*t, so the 21 maximal minors containing the d column
    # generate all 56 maximal minors after localization.  The 35 identities
    # below are the exact four-column Laplace/Pluecker relations.
    walls = parent_wall_map()
    if walls["1238"] != coordinate(8):
        raise AssertionError("parent unit [1238]=i changed")
    if walls["2378"] != subtract(coordinate(5), coordinate(8)):
        raise AssertionError("parent unit [2378]=f-i changed")
    pivot = active.index(3)
    if height_numerator[pivot] != multiply(coordinate(8), t):
        raise AssertionError("localized height pivot H_d=i(i-f) changed")
    remaining = tuple(column for column in range(8) if column != pivot)

    def ordered_minor(chosen):
        matrix = [[height_numerator[column] for column in chosen]]
        matrix.extend(
            [
                derivative(polynomial, active[column])
                for column in chosen
            ]
            for polynomial in reduced_residuals
        )
        return determinant3(matrix)

    pivot_minors = tuple(
        ordered_minor((pivot, left, right))
        for left, right in combinations(remaining, 2)
    )
    pivot_census = {
        "formal_minors": len(pivot_minors),
        "nonzero_minors": sum(bool(polynomial) for polynomial in pivot_minors),
        "nonzero_minor_terms": sum(len(polynomial) for polynomial in pivot_minors),
        "minor_degrees": tuple(
            sorted(
                {
                    max(map(sum, polynomial))
                    for polynomial in pivot_minors
                    if polynomial
                }
            )
        ),
    }
    if pivot_census != {
        "formal_minors": 21,
        "nonzero_minors": 21,
        "nonzero_minor_terms": 21_187,
        "minor_degrees": (11,),
    }:
        raise AssertionError(f"parent-cell pivot census changed: {pivot_census}")
    for left, middle, right in combinations(remaining, 3):
        laplace = add(
            subtract(
                multiply(
                    height_numerator[pivot],
                    ordered_minor((left, middle, right)),
                ),
                multiply(
                    height_numerator[left],
                    ordered_minor((pivot, middle, right)),
                ),
            ),
            subtract(
                multiply(
                    height_numerator[middle],
                    ordered_minor((pivot, left, right)),
                ),
                multiply(
                    height_numerator[right],
                    ordered_minor((pivot, left, middle)),
                ),
            ),
        )
        if laplace:
            raise AssertionError("parent-cell pivot minor identity changed")
    return census, reduced_antichain, pivot_census


def verify_two_pivot_critical_chart(residual, walls):
    """Reduce all parent-cell critical minors to six exact generators.

    After eliminating ``b``, the height row has the parent-unit entry
    ``H_d=i(i-f)``.  The first reduced residual also has the parent-unit
    entry ``dR2/da=B=[2357][2458][1267]``.  Hence the ``d`` and ``a``
    columns are independent everywhere on the parent cell.  Rank at most
    two is therefore equivalent to the six minors using those two columns.
    The identities below verify that equivalence without appealing to a
    pointwise rank argument or silently discarding the complementary branch.
    """

    t = subtract(coordinate(8), coordinate(5))
    u = walls[PARENT_LOCALIZER]

    def eliminate_b(polynomial):
        constant_part, coefficient = split_linear(polynomial, HEIGHT)
        return add(multiply(t, constant_part), multiply(u, coefficient))

    reduced_two, reduced_three = tuple(
        eliminate_b(polynomial) for polynomial in residual[1:]
    )
    _constant_two, coefficient_two = split_linear(reduced_two, 0)
    expected_coefficient = multiply(
        multiply(walls["2357"], walls["2458"]),
        eliminate_b(walls["1267"]),
    )
    if coefficient_two != expected_coefficient:
        raise AssertionError("two-pivot a coefficient changed")
    if derivative(reduced_two, 0) != coefficient_two:
        raise AssertionError("two-pivot dR2/da identity changed")

    active = tuple(variable for variable in range(9) if variable != HEIGHT)
    height = {
        variable: subtract(
            multiply(t, derivative(u, variable)),
            multiply(u, derivative(t, variable)),
        )
        for variable in active
    }
    height_d = multiply(coordinate(8), t)
    if height[3] != height_d or height[0]:
        raise AssertionError("two-pivot height entries changed")

    def critical_minor(columns):
        return determinant3(
            [
                [height[variable] for variable in columns],
                [derivative(reduced_two, variable) for variable in columns],
                [derivative(reduced_three, variable) for variable in columns],
            ]
        )

    remaining = tuple(variable for variable in active if variable not in (3, 0))
    two_pivot = {
        variable: critical_minor((3, 0, variable))
        for variable in remaining
    }

    # Every omitted d-pivot minor is generated by the six two-pivot minors
    # after inverting H_d*B.  This is the exact column-elimination identity
    # behind the rank argument.
    for left, right in combinations(remaining, 2):
        left_coefficient = subtract(
            multiply(height_d, derivative(reduced_two, left)),
            multiply(height[left], derivative(reduced_two, 3)),
        )
        right_coefficient = subtract(
            multiply(height_d, derivative(reduced_two, right)),
            multiply(height[right], derivative(reduced_two, 3)),
        )
        omitted = critical_minor((3, left, right))
        identity = subtract(
            multiply(left_coefficient, two_pivot[right]),
            multiply(right_coefficient, two_pivot[left]),
        )
        if multiply(multiply(height_d, coefficient_two), omitted) != identity:
            raise AssertionError(
                "two-pivot generation identity changed for "
                f"{VARIABLES[left]}{VARIABLES[right]}"
            )

    # Strip only factors that are already named parent units.  The resulting
    # primitive generators are the smaller modular/rational saturation input.
    unit_factors = {"t": t, "i": coordinate(8)}
    expected_factorizations = {
        2: ("t", "t", "i"),
        4: ("t", "i"),
        5: ("i",),
        6: ("t",),
        7: ("t", "t", "i"),
        8: (),
    }
    expected_terms = (290, 341, 949, 510, 194, 888)
    primitive = []
    for variable, expected_names, expected_count in zip(
        remaining, expected_factorizations.values(), expected_terms
    ):
        polynomial = two_pivot[variable]
        for name in expected_names:
            quotient = triples.exact_divide(polynomial, unit_factors[name])
            if quotient is None:
                raise AssertionError(
                    f"two-pivot unit factor {name} disappeared from "
                    f"M_da{VARIABLES[variable]}"
                )
            polynomial = quotient
        if len(polynomial) != expected_count:
            raise AssertionError(
                f"two-pivot primitive term count changed for "
                f"M_da{VARIABLES[variable]}: {len(polynomial)}"
            )
        primitive.append(polynomial)

    # The ae member is exactly H_d times the sparsest residual rank-drop
    # equation.  This is the first chartwise support-containment target.
    rank_drop_ae = subtract(
        multiply(derivative(reduced_two, 0), derivative(reduced_three, 4)),
        multiply(derivative(reduced_two, 4), derivative(reduced_three, 0)),
    )
    if two_pivot[4] != multiply(height_d, rank_drop_ae):
        raise AssertionError("two-pivot ae rank-drop identity changed")
    if len(rank_drop_ae) != 341:
        raise AssertionError("two-pivot ae rank-drop census changed")

    return {
        "unit_pivots": ("i(i-f)", "[2357][2458][1267]"),
        "critical_minors_before": 21,
        "critical_minors_after": len(two_pivot),
        "primitive_terms": tuple(map(len, primitive)),
        "primitive_total_terms": sum(map(len, primitive)),
        "first_chart": "ae",
        "first_rank_drop_terms": len(rank_drop_ae),
        "base_parent_units": (
            "1378", "2378", "1238", "2357", "2458", "1267"
        ),
        "target_walls": ("1468", "5678"),
    }


def verify_parent_cell_hypersurface_chart(residual, walls):
    """Eliminate a by a coefficient that is a product of parent units."""

    t = subtract(coordinate(8), coordinate(5))
    u = walls[PARENT_LOCALIZER]

    def eliminate_b(polynomial):
        constant_part, coefficient = split_linear(polynomial, HEIGHT)
        return add(
            multiply(t, constant_part), multiply(u, coefficient)
        )

    reduced_two, reduced_three = tuple(
        eliminate_b(polynomial) for polynomial in residual[1:]
    )

    # The two discovery walls are not merely divisors: after b elimination
    # they supply simultaneous rational coordinates on the parent cell.
    # First, [1468] is affine in a with the unit slope h*(i-f).  Second,
    # [5678] is affine in each of a,c,e,h with the displayed parent-unit
    # slopes.  The six nonzero two-by-two Jacobians below prove that the wall
    # map ([1468],[5678]) is etale in six explicit parent-cell charts.
    wall_1468_after_b = eliminate_b(walls["1468"])
    wall_5678_after_b = eliminate_b(walls["5678"])
    expected_1468 = subtract(
        multiply(multiply(t, coordinate(0)), coordinate(7)),
        multiply(u, coordinate(6)),
    )
    if wall_1468_after_b != expected_1468:
        raise AssertionError("[1468] wall-coordinate identity changed")
    wall_slopes = {
        0: "2578",
        2: "4578",
        4: "3568",
        7: "3567",
    }
    wall_slope_signs = {0: 1, 2: 1, 4: 1, 7: -1}
    for variable, label in wall_slopes.items():
        expected = multiply(t, walls[label])
        if wall_slope_signs[variable] == -1:
            expected = {monomial: -coefficient for monomial, coefficient in expected.items()}
        if derivative(wall_5678_after_b, variable) != expected:
            raise AssertionError(
                f"[5678] unit slope in {VARIABLES[variable]} changed"
            )

    wall_coordinate_certificates = {
        (0, 2): (1, ("1248", "2378", "2378", "4578")),
        (0, 4): (1, ("1248", "2378", "2378", "3568")),
        (2, 3): (-1, ("1238", "1348", "2378", "4578")),
        (2, 7): (-1, ("1346", "2378", "2378", "4578")),
        (3, 4): (1, ("1238", "1348", "2378", "3568")),
        (4, 7): (-1, ("1346", "2378", "2378", "3568")),
    }
    for (left, right), (sign, labels) in wall_coordinate_certificates.items():
        determinant = subtract(
            multiply(
                derivative(wall_1468_after_b, left),
                derivative(wall_5678_after_b, right),
            ),
            multiply(
                derivative(wall_1468_after_b, right),
                derivative(wall_5678_after_b, left),
            ),
        )
        expected = {ZERO: sign}
        for label in labels:
            expected = multiply(expected, walls[label])
        if determinant != expected:
            raise AssertionError(
                "two-wall coordinate Jacobian changed for "
                f"{VARIABLES[left]}{VARIABLES[right]}"
            )

    # In the four wall charts using height-independent variables, the
    # corresponding critical minor is the unit H_d=i*(i-f) times the
    # residual two-by-two Jacobian.  Hence the non-rank-drop branch cannot
    # contain a critical point on the parent cell.
    height_d = multiply(coordinate(8), t)
    regular_wall_charts = ((0, 2), (0, 4), (2, 7), (4, 7))
    rank_drop_census = []
    for left, right in regular_wall_charts:
        residual_minor = subtract(
            multiply(
                derivative(reduced_two, left),
                derivative(reduced_three, right),
            ),
            multiply(
                derivative(reduced_two, right),
                derivative(reduced_three, left),
            ),
        )
        critical_minor = determinant3(
            [
                [height_d, {}, {}],
                [
                    derivative(reduced_two, 3),
                    derivative(reduced_two, left),
                    derivative(reduced_two, right),
                ],
                [
                    derivative(reduced_three, 3),
                    derivative(reduced_three, left),
                    derivative(reduced_three, right),
                ],
            ]
        )
        if critical_minor != multiply(height_d, residual_minor):
            raise AssertionError(
                "wall-coordinate rank-drop identity changed for "
                f"{VARIABLES[left]}{VARIABLES[right]}"
            )
        rank_drop_census.append(len(residual_minor))
    if tuple(rank_drop_census) != (452, 341, 432, 440):
        raise AssertionError(
            f"wall-coordinate rank-drop census changed: {rank_drop_census}"
        )
    constant_two, coefficient_two = split_linear(reduced_two, 0)
    constant_three, coefficient_three = split_linear(reduced_three, 0)

    wall_1267 = eliminate_b(walls["1267"])
    expected_coefficient = multiply(
        multiply(walls["2357"], walls["2458"]), wall_1267
    )
    if coefficient_two != expected_coefficient:
        raise AssertionError(
            "a-coefficient is no longer [2357][2458][1267]"
        )

    hypersurface = subtract(
        multiply(coefficient_two, constant_three),
        multiply(coefficient_three, constant_two),
    )
    # B*R3 = E + D*R2 is the exact localized elimination identity.
    if multiply(coefficient_two, reduced_three) != add(
        hypersurface, multiply(coefficient_three, reduced_two)
    ):
        raise AssertionError("parent-cell a-elimination identity changed")
    if (
        len(hypersurface),
        min(map(sum, hypersurface)),
        max(map(sum, hypersurface)),
    ) != (594, 7, 10):
        raise AssertionError("seven-variable hypersurface census changed")
    if any(monomial[0] or monomial[HEIGHT] for monomial in hypersurface):
        raise AssertionError("eliminated variables a or b reappeared")

    derivative_d = derivative(hypersurface, 3)
    critical_generators = [hypersurface]
    for variable in (2, 4, 7):
        critical_generators.append(derivative(hypersurface, variable))
    critical_generators.append(
        subtract(
            multiply(t, derivative(hypersurface, 5)),
            multiply(
                subtract(coordinate(3), coordinate(6)), derivative_d
            ),
        )
    )
    critical_generators.append(
        add(
            multiply(coordinate(8), derivative(hypersurface, 6)),
            multiply(coordinate(5), derivative_d),
        )
    )
    critical_generators.append(
        subtract(
            multiply(
                multiply(coordinate(8), t),
                derivative(hypersurface, 8),
            ),
            multiply(
                multiply(
                    coordinate(5),
                    subtract(coordinate(6), coordinate(3)),
                ),
                derivative_d,
            ),
        )
    )
    critical_generators = tuple(critical_generators)
    critical_census = tuple(
        (
            len(polynomial),
            min(map(sum, polynomial)),
            max(map(sum, polynomial)),
        )
        for polynomial in critical_generators
    )
    if critical_census != (
        (594, 7, 10),
        (421, 6, 9),
        (359, 6, 9),
        (424, 6, 9),
        (886, 7, 10),
        (505, 7, 10),
        (815, 8, 11),
    ):
        raise AssertionError(
            f"seven-variable critical census changed: {critical_census}"
        )

    active = (2, 3, 4, 5, 6, 7, 8)
    critical_antichain = coordinate_antichain(
        critical_generators, active
    )
    expected_antichain = (
        (5, 8),
        (2, 3, 5),
        (2, 3, 6, 7),
        (2, 6, 7, 8),
        (3, 4, 6, 7),
        (3, 6, 7, 8),
    )
    if critical_antichain != expected_antichain:
        raise AssertionError(
            f"hypersurface coordinate antichain changed: {critical_antichain}"
        )
    if not all(
        vanishes_on_coordinate_subspace(u, zero_variables)
        for zero_variables in critical_antichain
    ):
        raise AssertionError("a hypersurface coordinate stratum survives [1378]")

    # Test the most direct next graph reduction exhaustively.  In the
    # a-chart, E_c, E_e, and E_h are affine in their own variables.  Reduce
    # every parent wall through both graph substitutions, strip the known
    # denominator units t and B, and check that none of the three leading
    # coefficients has even one transformed parent-wall divisor.
    transformed_walls = {}
    for label, wall in walls.items():
        reduced_wall = eliminate_b(wall)
        wall_constant, wall_coefficient = split_linear(reduced_wall, 0)
        numerator = subtract(
            multiply(coefficient_two, wall_constant),
            multiply(constant_two, wall_coefficient),
        )
        while numerator:
            quotient = triples.exact_divide(numerator, t)
            if quotient is not None:
                numerator = quotient
                continue
            quotient = triples.exact_divide(numerator, coefficient_two)
            if quotient is not None:
                numerator = quotient
                continue
            break
        if numerator:
            transformed_walls[label] = numerator
    transformed_factors = triples.normalized_bracket_factors(
        transformed_walls
    )
    if len(transformed_factors) != 60:
        raise AssertionError("transformed parent-wall census changed")
    affine_leading_terms = []
    for variable in (2, 4, 7):
        _constant_part, leading_coefficient = split_linear(
            derivative(hypersurface, variable), variable
        )
        affine_leading_terms.append(len(leading_coefficient))
        divisors = tuple(
            label
            for label, factor, _sign in transformed_factors
            if triples.exact_divide(leading_coefficient, factor) is not None
        )
        if divisors:
            raise AssertionError(
                f"unexpected parent-unit derivative pivot: {divisors}"
            )
    if tuple(affine_leading_terms) != (144, 103, 154):
        raise AssertionError(
            f"affine derivative coefficient census changed: {affine_leading_terms}"
        )

    # There is a second exact graph chart.  The c-coefficient in R3 is a
    # product of four parent units, while R2 is quadratic in c.  This chart
    # is denser than the a-chart above, but it keeps the candidate next wall
    # [1468] as a four-term cubic after b elimination.
    c = coordinate(2)
    c_constant_three, c_coefficient_three = split_linear(reduced_three, 2)
    expected_c_coefficient = multiply(
        multiply(walls["1348"], walls["1457"]),
        multiply(walls["2378"], walls["2458"]),
    )
    if c_coefficient_three != expected_c_coefficient:
        raise AssertionError(
            "c-coefficient is no longer [1348][1457][2378][2458]"
        )
    c_coefficients_two = split_by_degree(reduced_two, 2)
    if len(c_coefficients_two) != 3:
        raise AssertionError("R2 is no longer quadratic in c")
    c_zero_two, c_one_two, c_two_two = c_coefficients_two
    alternative_hypersurface = add(
        subtract(
            multiply(
                multiply(c_coefficient_three, c_coefficient_three),
                c_zero_two,
            ),
            multiply(
                multiply(c_constant_three, c_coefficient_three),
                c_one_two,
            ),
        ),
        multiply(
            multiply(c_constant_three, c_constant_three), c_two_two
        ),
    )
    alternative_cofactor = add(
        multiply(c_coefficient_three, c_one_two),
        multiply(
            subtract(
                multiply(c, c_coefficient_three), c_constant_three
            ),
            c_two_two,
        ),
    )
    # P1^2 R2 = Ec + R3*(P1 Q1 + (c P1-P0) Q2).
    if multiply(
        multiply(c_coefficient_three, c_coefficient_three), reduced_two
    ) != add(
        alternative_hypersurface,
        multiply(reduced_three, alternative_cofactor),
    ):
        raise AssertionError("parent-cell c-elimination identity changed")
    alternative_census = (
        len(alternative_hypersurface),
        min(map(sum, alternative_hypersurface)),
        max(map(sum, alternative_hypersurface)),
    )
    if alternative_census != (2871, 10, 14):
        raise AssertionError(
            f"alternative c-chart census changed: {alternative_census}"
        )
    if any(monomial[HEIGHT] or monomial[2] for monomial in alternative_hypersurface):
        raise AssertionError("eliminated variables b or c reappeared")
    alternative_derivative_d = derivative(alternative_hypersurface, 3)
    alternative_critical = [alternative_hypersurface]
    alternative_critical.extend(
        derivative(alternative_hypersurface, variable)
        for variable in (0, 4, 7)
    )
    alternative_critical.append(
        subtract(
            multiply(t, derivative(alternative_hypersurface, 5)),
            multiply(
                subtract(coordinate(3), coordinate(6)),
                alternative_derivative_d,
            ),
        )
    )
    alternative_critical.append(
        add(
            multiply(
                coordinate(8), derivative(alternative_hypersurface, 6)
            ),
            multiply(coordinate(5), alternative_derivative_d),
        )
    )
    alternative_critical.append(
        subtract(
            multiply(
                multiply(coordinate(8), t),
                derivative(alternative_hypersurface, 8),
            ),
            multiply(
                multiply(
                    coordinate(5),
                    subtract(coordinate(6), coordinate(3)),
                ),
                alternative_derivative_d,
            ),
        )
    )
    alternative_critical_census = tuple(
        (
            len(polynomial),
            min(map(sum, polynomial)),
            max(map(sum, polynomial)),
        )
        for polynomial in alternative_critical
    )
    if alternative_critical_census != (
        (2871, 10, 14),
        (1788, 9, 13),
        (2196, 9, 13),
        (2199, 9, 13),
        (3807, 10, 14),
        (3225, 10, 14),
        (3975, 11, 15),
    ):
        raise AssertionError(
            "alternative c-chart critical census changed: "
            f"{alternative_critical_census}"
        )

    def eliminate_c_from_affine(polynomial):
        constant_part, coefficient = split_linear(polynomial, 2)
        return subtract(
            multiply(c_coefficient_three, constant_part),
            multiply(c_constant_three, coefficient),
        )

    wall_1468 = eliminate_b(walls["1468"])
    if any(monomial[2] for monomial in wall_1468):
        raise AssertionError("[1468] unexpectedly depends on c")
    wall_5678 = eliminate_c_from_affine(eliminate_b(walls["5678"]))
    wall_census = (
        (
            len(wall_1468),
            min(map(sum, wall_1468)),
            max(map(sum, wall_1468)),
        ),
        (
            len(wall_5678),
            min(map(sum, wall_5678)),
            max(map(sum, wall_5678)),
        ),
    )
    if wall_census != ((4, 3, 3), (226, 6, 8)):
        raise AssertionError(f"alternative wall census changed: {wall_census}")
    return {
        "a_coefficient_parent_units": ("2357", "2458", "1267"),
        "next_wall_unit_slopes": tuple(
            (VARIABLES[variable], label, wall_slope_signs[variable])
            for variable, label in wall_slopes.items()
        ),
        "next_wall_coordinate_charts": tuple(
            VARIABLES[left] + VARIABLES[right]
            for left, right in wall_coordinate_certificates
        ),
        "next_wall_rank_drop_terms": tuple(rank_drop_census),
        "hypersurface_terms": len(hypersurface),
        "critical_generators": len(critical_generators),
        "critical_terms": sum(map(len, critical_generators)),
        "coordinate_antichain": critical_antichain,
        "nonunit_affine_derivative_coefficients": tuple(affine_leading_terms),
        "c_coefficient_parent_units": ("1348", "1457", "2378", "2458"),
        "alternative_hypersurface": alternative_census,
        "alternative_critical_terms": sum(map(len, alternative_critical)),
        "alternative_walls": wall_census,
    }


def main():
    if sha256(SYSTEM) != SYSTEM_SHA256:
        raise AssertionError("full-space critical-system digest changed")
    payload = json.loads(SYSTEM.read_text(encoding="ascii"))
    if tuple(payload["named_presentation"]) != PRESENTATION:
        raise AssertionError("named hard-canary presentation changed")
    if payload["height_index"] != HEIGHT:
        raise AssertionError("height variable changed")
    stored = tuple(decode_terms(record["terms"]) for record in payload["equations"])
    residual = stored[:3]
    height_columns = tuple(
        combinations(
            tuple(variable for variable in range(9) if variable != HEIGHT), 3
        )
    )
    recomputed_height_minors = tuple(
        jacobian_minor(residual, columns) for columns in height_columns
    )
    if stored[3:] != recomputed_height_minors:
        raise AssertionError("stored height-critical minors changed")
    raw_generators = tuple(polynomial for polynomial in stored if polynomial)

    raw_antichain = coordinate_antichain(raw_generators)
    if raw_antichain != RAW_COORDINATE_ANTICHAIN:
        raise AssertionError(f"raw coordinate antichain changed: {raw_antichain}")

    singular_minors = tuple(
        jacobian_minor(residual, columns)
        for columns in combinations(range(9), 3)
    )
    singular_generators = residual + tuple(
        polynomial for polynomial in singular_minors if polynomial
    )
    if len(singular_minors) != 84 or sum(bool(poly) for poly in singular_minors) != 80:
        raise AssertionError("intrinsic singular-minor census changed")
    singular_antichain = coordinate_antichain(singular_generators)
    if singular_antichain != SINGULAR_COORDINATE_ANTICHAIN:
        raise AssertionError(f"singular coordinate antichain changed: {singular_antichain}")

    walls = parent_wall_map()
    if common_parent_walls(raw_antichain, walls) != RAW_COMMON_PARENT_WALLS:
        raise AssertionError("raw common parent-wall intersection changed")
    if common_parent_walls(singular_antichain, walls) != SINGULAR_COMMON_PARENT_WALLS:
        raise AssertionError("singular common parent-wall intersection changed")
    if walls[PARENT_LOCALIZER] != {
        (0, 0, 0, 1, 0, 0, 0, 0, 1): 1,
        (0, 0, 0, 0, 0, 1, 1, 0, 0): -1,
    }:
        raise AssertionError("parent localizer [1378] is no longer di-fg")

    noncoordinate_witness = (1, 0, 1, 0, 2, 0, 0, 2, 0)
    if evaluate(NONCOORDINATE_FACTOR, noncoordinate_witness):
        raise AssertionError("pinned noncoordinate-branch witness left F=0")
    if evaluate(walls["1268"], noncoordinate_witness) != -2:
        raise AssertionError("[1268] unexpectedly contains the noncoordinate branch")
    if not vanishes_on_coordinate_subspace(
        walls["1678"], NONCOORDINATE_AMBIENT_ZERO
    ):
        raise AssertionError("[1678] no longer contains the noncoordinate branch")
    localizer_candidates = tuple(
        label
        for label in RAW_COMMON_PARENT_WALLS
        if vanishes_on_coordinate_subspace(
            walls[label], NONCOORDINATE_AMBIENT_ZERO
        )
    )
    if localizer_candidates != ("1378", "1678"):
        raise AssertionError("first-wall candidate set changed")
    candidate_degrees = {
        label: max(map(sum, walls[label])) for label in localizer_candidates
    }
    if candidate_degrees != {"1378": 2, "1678": 3}:
        raise AssertionError("first-wall candidate degrees changed")

    singular_ranks = []
    for zero_variables in singular_antichain:
        point = point_on(zero_variables)
        if any(evaluate(polynomial, point) for polynomial in singular_generators):
            raise AssertionError("coordinate-stratum test point left the singular ideal")
        singular_ranks.append(jacobian_rank(singular_generators, point))
    expected_ranks = tuple(len(chosen) for chosen in singular_antichain[:9]) + (6,)
    if tuple(singular_ranks) != expected_ranks:
        raise AssertionError(f"singular Jacobian ranks changed: {singular_ranks}")

    restricted = tuple(
        restrict(polynomial, NONCOORDINATE_AMBIENT_ZERO)
        for polynomial in singular_generators
    )
    nonzero_restricted = tuple(polynomial for polynomial in restricted if polynomial)
    restricted_generator = multiply(COORDINATE_C, NONCOORDINATE_FACTOR)
    multiples = tuple(scalar_multiple(polynomial, restricted_generator) for polynomial in nonzero_restricted)
    if not nonzero_restricted or any(ratio is None for ratio in multiples):
        raise AssertionError("noncoordinate ambient restriction changed")
    if set(multiples) != {Fraction(1)}:
        raise AssertionError(f"unexpected restricted singular generators: {multiples}")
    # The restricted ideal is c*F.  Its noncoordinate branch F=0 lies in
    # b=d=f=g=i=0, hence on [1378]=di-fg identically.
    if not vanishes_on_coordinate_subspace(walls[PARENT_LOCALIZER], NONCOORDINATE_AMBIENT_ZERO):
        raise AssertionError("noncoordinate branch escaped parent wall [1378]")

    reduced_census, reduced_antichain, pivot_census = verify_reduced_height_chart(
        residual, walls[PARENT_LOCALIZER]
    )
    two_pivot_report = verify_two_pivot_critical_chart(residual, walls)
    hypersurface_report = verify_parent_cell_hypersurface_chart(
        residual, walls
    )

    print("PASS exact height-b coordinate antichain", raw_antichain)
    print("PASS intrinsic singular coordinate antichain", singular_antichain)
    print("PASS singular smooth-component ranks", tuple(singular_ranks[:9]))
    print("PASS exceptional coordinate stratum has tangent dimension", 9 - singular_ranks[-1])
    print("PASS restricted singular ideal is generated by c*F")
    print("     F = ch - ceh - ae + aeh")
    print("PASS [1268] misses the noncoordinate branch at", noncoordinate_witness)
    print("PASS first minimum-degree boundary localizer [1378] = di-fg")
    print("PASS exact b=(di-fg)/(i-f) reduced critical chart", reduced_census)
    print("PASS all reduced coordinate strata lie on [1378]", reduced_antichain)
    print("PASS parent-cell i(i-f) pivot reduces 56 minors to 21", pivot_census)
    print("PASS parent-cell (d,a) unit pivots reduce 21 minors to 6", two_pivot_report)
    print("PASS parent-cell unit eliminates a to one hypersurface", hypersurface_report)
    print("SCOPE no primary decomposition; no global closure claim")
    print("LEDGER 1,162,302 triple orbits unresolved; theorem score remains 2/9")


if __name__ == "__main__":
    main()
