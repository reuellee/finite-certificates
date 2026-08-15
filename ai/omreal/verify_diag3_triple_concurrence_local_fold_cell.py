#!/usr/bin/env python3
"""Critical census and boundary cell for a hard diagonal-3 pinned slice.

The dependency-free part verifies the degree-20 RUR consequences, its six
real roots, their parent chambers and fold invariants, and a rational
parametric-Krawczyk chain from the unique in-chamber fold to two source-parent
faces.  Completeness of the saturated critical ideal is a deliberately named
msolve-0.10.1 trust boundary.  Under that exact-CAS boundary the saturated
chart slice has no compact component.  Exact incidence identities prove that
the three removed interpolation divisors force parent nonuniformity, while
``[1234]=0`` is itself a parent boundary.  Thus the same result holds on the
unsaturated pinned affine slice, but not on the full nine-variable factor
triple, its orbit, or triple H_c^0.
"""

from __future__ import annotations

import argparse
from collections import defaultdict
from fractions import Fraction as Q
import hashlib
from itertools import combinations, permutations
import json
from math import prod
from pathlib import Path
import re
import struct
import subprocess
import sys
import tempfile


HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE / "data"))

import DIAG3_concurrence_ramification_rur as certificate  # noqa: E402
import verify_diag3_concurrence_normal_form as base  # noqa: E402
import verify_diag3_projective_column_fiber_scan as source_scan  # noqa: E402


HARD_PRESENTATIONS = (
    (2_277, 390, 22_507),
    (5_563, 16_134, 19_284),
    (12_985, 16_183, 7_196),
    (20_355, 5_442, 5_949),
    (9_667, 16_486, 26_315),
    (9_758, 24_338, 15_810),
)
CANONICAL_ROWS = (
    (2_277, 390, 22_507),
    (5_563, 4_373, 23_221),
    (5_563, 4_373, 23_221),
    (5_563, 5_031, 11_209),
    (2_267, 4_271, 20_520),
    (13_950, 4_097, 17_312),
)
# One-based label permutations.  Images retain the source factor order; the
# canonical row is an unordered triple, so EXPECTED_IMAGES pins the ordering.
LABEL_PERMUTATIONS = (
    (1, 2, 3, 4, 5, 6, 7, 8),
    (6, 2, 5, 8, 3, 4, 1, 7),
    (6, 3, 5, 2, 8, 1, 7, 4),
    (3, 4, 6, 7, 5, 1, 8, 2),
    (3, 5, 6, 8, 4, 7, 2, 1),
    (7, 1, 8, 5, 3, 4, 6, 2),
)
EXPECTED_IMAGES = (
    (2_277, 390, 22_507),
    (4_373, 5_563, 23_221),
    (4_373, 23_221, 5_563),
    (5_563, 11_209, 5_031),
    (20_520, 2_267, 4_271),
    (13_950, 4_097, 17_312),
)
DISTINCT_CANONICAL_ROWS = tuple(dict.fromkeys(CANONICAL_ROWS))
EXPECTED_CANONICAL_OCCURRENCE_PRODUCTS = (65, 1, 1, 1, 2)
EXPECTED_NAMED_OCCURRENCE_DIGEST = (
    "f32424ceb96ce446b97f398e50212eced4b47473ec61629c950775e7df3ea51d"
)
EXPECTED_CANONICAL_OCCURRENCE_DIGEST = (
    "54bf6637941cfaff91a394d3eaad456a54e1adf74fb22c988454f9eec47f41e2"
)
EXPECTED_UNION4_DIGEST = (
    "54b03c31910de606b80f9dcc448ce3dde93063a8dbc3f2dbcaa7a02901df0303"
)
EXPECTED_UNION4_COUNT = 1_897_733
EXPECTED_FINAL_UNRESOLVED = 1_819_789
CONSTANT_SHEAR = HERE / "data/DIAG3_frame1119_constant_shear.json"
CONSTANT_SHEAR_DIGEST = (
    "1cece61ff1a551faaeefc0062267e24266d264d9e19748d40fa5a74db9ce0be3"
)
BOUNDARY_CHAIN = HERE / "data/DIAG3_triple_fold_boundary_chain.json"
BOUNDARY_CHAIN_DIGEST = (
    "3e665f0923fed4bef65def70ea15c875cd868fede3bfc618c0407380a2cb3301"
)
BOUNDARY_CHAIN_SCHEMA = "diag3-triple-fold-boundary-chain-v1"
COMPLETE_CRITICAL_INPUT = (
    HERE / "data/DIAG3_concurrence_ramification_complete.msolve"
)
COMPLETE_CRITICAL_INPUT_DIGEST = (
    "a13bd2e95337ff571ff577ec83ed1515c57764e579e28ef61a10bfce3b94f09d"
)
COMPLETE_CRITICAL_OUTPUT_DIGEST = (
    "a802303ebdb11bc0985d8445245b7d64726bea398b08b1c127dd6cc3a912464f"
)


def sparse_derivative(terms, variable):
    answer = []
    for monomial, coefficient in terms:
        if monomial[variable]:
            derived = list(monomial)
            scalar = derived[variable]
            derived[variable] -= 1
            answer.append((tuple(derived), scalar * coefficient))
    return answer


def sparse_interval_evaluate(terms, values):
    answer = base.Interval(0)
    for monomial, coefficient in terms:
        term = base.Interval(coefficient)
        for value, exponent in zip(values, monomial):
            for _ in range(exponent):
                term *= value
        answer += term
    return answer


def solve3(matrix, right):
    denominator = base.determinant(matrix)
    if denominator.contains_zero():
        raise AssertionError("singular interval 3 by 3 solve")
    answer = []
    for column in range(3):
        replaced = [list(row) for row in matrix]
        for row in range(3):
            replaced[row][column] = right[row]
        answer.append(base.determinant(replaced) / denominator)
    return answer


def plane_normal(points, triple):
    answer = []
    for omitted in range(4):
        minor = [
            [points[column][row] for column in triple]
            for row in range(4)
            if row != omitted
        ]
        value = base.determinant(minor)
        answer.append(-value if omitted & 1 else value)
    return tuple(answer)


# The continuation certificate uses five local variables in the order
# (v_r,v_s,w_r,w_s,t).  Polynomial dictionaries below have the same five
# exponents; the last exponent becomes the centered continuation parameter.
ZERO5 = (0, 0, 0, 0, 0)


def poly_add(left, right):
    answer = dict(left)
    for monomial, coefficient in right.items():
        answer[monomial] = answer.get(monomial, 0) + coefficient
    return {monomial: value for monomial, value in answer.items() if value}


def poly_multiply(left, right):
    answer = {}
    for first, first_value in left.items():
        for second, second_value in right.items():
            monomial = tuple(a + b for a, b in zip(first, second))
            answer[monomial] = answer.get(monomial, 0) + first_value * second_value
    return {monomial: value for monomial, value in answer.items() if value}


def poly_power(polynomial, exponent):
    answer = {ZERO5: Q(1)}
    for _ in range(exponent):
        answer = poly_multiply(answer, polynomial)
    return answer


def poly_constant(value):
    return {} if not value else {ZERO5: Q(value)}


def poly_variable(index):
    exponent = [0] * 5
    exponent[index] = 1
    return {tuple(exponent): Q(1)}


def poly_scale(polynomial, scalar):
    return {monomial: Q(scalar) * value for monomial, value in polynomial.items()}


def poly_subtract(left, right):
    return poly_add(left, poly_scale(right, -1))


def polynomial_determinant4(matrix):
    answer = {}
    for permutation in permutations(range(4)):
        inversions = sum(
            permutation[left] > permutation[right]
            for left in range(4)
            for right in range(left + 1, 4)
        )
        term = poly_constant(-1 if inversions & 1 else 1)
        for row in range(4):
            term = poly_multiply(term, matrix[row][permutation[row]])
        answer = poly_add(answer, term)
    return answer


def scalar_collinearity(y, z, triple):
    """The exact affine collinearity equation C_{abc}(y,z)."""

    first, second, third = triple
    return (
        (y[second] - y[first]) * (z[third] - z[first])
        - (y[third] - y[first]) * (z[second] - z[first])
    )


def polynomial_collinearity(y, z, triple):
    first, second, third = triple
    return poly_subtract(
        poly_multiply(
            poly_subtract(y[second], y[first]),
            poly_subtract(z[third], z[first]),
        ),
        poly_multiply(
            poly_subtract(y[third], y[first]),
            poly_subtract(z[second], z[first]),
        ),
    )


def exact_affine_solution(matrix, right):
    """Return one point and a basis for every solution of Ax=b over Q."""

    augmented = [
        [Q(value) for value in row] + [Q(value)]
        for row, value in zip(matrix, right)
    ]
    row_count = len(augmented)
    column_count = len(augmented[0]) - 1
    rank = 0
    pivots = []
    for column in range(column_count):
        pivot = next(
            (
                row
                for row in range(rank, row_count)
                if augmented[row][column]
            ),
            None,
        )
        if pivot is None:
            continue
        augmented[rank], augmented[pivot] = augmented[pivot], augmented[rank]
        scalar = augmented[rank][column]
        augmented[rank] = [value / scalar for value in augmented[rank]]
        for row in range(row_count):
            if row == rank or not augmented[row][column]:
                continue
            scalar = augmented[row][column]
            augmented[row] = [
                left - scalar * pivot_value
                for left, pivot_value in zip(augmented[row], augmented[rank])
            ]
        pivots.append(column)
        rank += 1

    if any(
        all(not value for value in row[:column_count]) and row[-1]
        for row in augmented
    ):
        raise AssertionError("inconsistent concurrence interpolation system")
    free = [column for column in range(column_count) if column not in pivots]
    particular = [Q(0)] * column_count
    for row, column in enumerate(pivots):
        particular[column] = augmented[row][-1]
    directions = []
    for free_column in free:
        direction = [Q(0)] * column_count
        direction[free_column] = Q(1)
        for row, column in enumerate(pivots):
            direction[column] = -augmented[row][free_column]
        directions.append(tuple(direction))
    return tuple(particular), tuple(directions), rank


def incidence_affine_space(u, supports):
    """Solve C_support(u,z)=0 with z_1=0,z_2=1 exhaustively."""

    fixed = [Q(0)] * 8
    fixed[1] = Q(1)
    matrix = []
    right = []
    for support in supports:
        constant = scalar_collinearity(u, fixed, support)
        coefficients = []
        for label in range(2, 8):
            basis = list(fixed)
            basis[label] += 1
            coefficients.append(
                scalar_collinearity(u, basis, support) - constant
            )
        matrix.append(coefficients)
        right.append(-constant)
    particular, directions, rank = exact_affine_solution(matrix, right)
    return (
        tuple(fixed[:2] + list(particular)),
        tuple((Q(0), Q(0)) + direction for direction in directions),
        rank,
    )


def affine_coordinate_polynomials(particular, directions, offset):
    if len(directions) != 2:
        raise AssertionError("frontier interpolation does not have two parameters")
    answer = []
    for label, value in enumerate(particular):
        polynomial = poly_constant(value)
        for index, direction in enumerate(directions):
            polynomial = poly_add(
                polynomial,
                poly_scale(poly_variable(offset + index), direction[label]),
            )
        answer.append(polynomial)
    return tuple(answer)


def parent_bracket_polynomial(points, labels):
    columns = [points[label - 1] for label in labels]
    return polynomial_determinant4(
        [[columns[column][row] for column in range(4)] for row in range(4)]
    )


def parse_msolve_polynomial(line, variable_order):
    """Parse the restricted expanded-polynomial syntax used by the pinned input."""

    answer = {}
    for raw_term in re.findall(r"[+-]?[^+-]+", line.strip().rstrip(",").replace(" ", "")):
        sign = -1 if raw_term.startswith("-") else 1
        term = raw_term.lstrip("+-")
        coefficient = sign
        exponents = [0] * len(variable_order)
        for factor in term.split("*"):
            if factor.isdigit():
                coefficient *= int(factor)
                continue
            match = re.fullmatch(r"([A-Za-z_][A-Za-z0-9_]*)(?:\^(\d+))?", factor)
            if match is None or match.group(1) not in variable_order:
                raise AssertionError(f"unexpected msolve factor {factor!r}")
            exponents[variable_order.index(match.group(1))] += int(match.group(2) or 1)
        monomial = tuple(exponents)
        answer[monomial] = answer.get(monomial, 0) + coefficient
    return {monomial: value for monomial, value in answer.items() if value}


def verify_saturation_frontiers():
    """Prove that every divisor removed by the critical-ideal saturation is safe."""

    variable_order = ("vr", "vs", "wr", "ws", "sat", "denominator_saturation", "t")
    lines = COMPLETE_CRITICAL_INPUT.read_text().splitlines()
    if len(lines) != 9 or tuple(lines[0].split(",")) != variable_order:
        raise AssertionError("complete-critical msolve variable order changed")

    # Reconstruct [1234] from the unsaturated affine coordinates.  Columns P3
    # and P4 are cleared respectively by 85(4t+3) and 136(20t-3).
    vr, vs, wr, ws, t = (poly_variable(index) for index in range(5))
    zero = poly_constant(0)
    one = poly_constant(1)
    four_t_plus_three = poly_add(poly_scale(t, 4), poly_constant(3))
    twenty_t_minus_three = poly_add(poly_scale(t, 20), poly_constant(-3))
    p1 = (zero, zero, zero, one)
    p2 = (one, one, one, one)
    p3 = (
        poly_scale(four_t_plus_three, 68),
        poly_add(
            poly_add(poly_scale(poly_multiply(t, vr), 315), poly_scale(t, -360)),
            poly_add(
                poly_scale(vr, -252),
                poly_add(poly_scale(vs, 527), poly_constant(288)),
            ),
        ),
        poly_scale(
            poly_multiply(
                four_t_plus_three,
                poly_add(poly_scale(wr, 33), poly_constant(-7)),
            ),
            17,
        ),
        poly_scale(four_t_plus_three, 85),
    )
    p4 = (
        poly_scale(twenty_t_minus_three, -102),
        poly_scale(
            poly_multiply(
                poly_add(poly_scale(vr, 7), poly_constant(-8)),
                twenty_t_minus_three,
            ),
            18,
        ),
        poly_scale(
            poly_add(
                poly_add(poly_scale(poly_multiply(t, wr), 204), poly_scale(t, -44)),
                poly_add(
                    poly_scale(wr, 153),
                    poly_add(poly_scale(ws, -144), poly_constant(-33)),
                ),
            ),
            17,
        ),
        poly_scale(twenty_t_minus_three, 136),
    )
    cleared_1234 = polynomial_determinant4(
        [
            [column[row] for column in (p1, p2, p3, p4)]
            for row in range(4)
        ]
    )
    if any(coefficient.denominator != 1 or coefficient % 17 for coefficient in cleared_1234.values()):
        raise AssertionError("cleared [1234] does not have the pinned content")
    saturation_factor = poly_scale(cleared_1234, Q(1, 17))
    interpolation_product = poly_multiply(
        t, poly_multiply(four_t_plus_three, twenty_t_minus_three)
    )
    bracket_denominator = poly_scale(
        poly_multiply(four_t_plus_three, twenty_t_minus_three), 680
    )

    def lift(polynomial, sat=0, denominator_saturation=0):
        return {
            (monomial[0], monomial[1], monomial[2], monomial[3],
             sat, denominator_saturation, monomial[4]): coefficient
            for monomial, coefficient in polynomial.items()
        }

    expected_bracket_inverse = poly_add(
        lift(saturation_factor, sat=1),
        poly_scale(lift(bracket_denominator), -1),
    )
    expected_interpolation_inverse = poly_add(
        lift(interpolation_product, denominator_saturation=1),
        {(0, 0, 0, 0, 0, 0, 0): -1},
    )
    if parse_msolve_polynomial(lines[7], variable_order) != expected_bracket_inverse:
        raise AssertionError("msolve [1234] saturation equation changed semantically")
    if parse_msolve_polynomial(lines[8], variable_order) != expected_interpolation_inverse:
        raise AssertionError("msolve interpolation saturation equation changed semantically")

    selected_supports = tuple(
        tuple(base.labeled.TRIPLES[index]) for occurrence in base.SELECTED
        for index in occurrence
    )
    expected_supports = (
        (0, 1, 2), (0, 3, 4), (1, 3, 5), (2, 6, 7),
        (0, 1, 5), (1, 4, 6), (2, 5, 6), (3, 4, 7),
        (1, 3, 4), (0, 4, 6), (2, 3, 7), (0, 5, 7),
    )
    if selected_supports != expected_supports:
        raise AssertionError("selected concurrence supports changed")
    color_two = selected_supports[4:8]
    color_three = selected_supports[8:12]
    cases = (
        (Q(0), ((1, 3, 4, 8), (1, 5, 7, 8))),
        (
            Q(-3, 4),
            tuple(
                tuple(sorted((4, 8) + labels))
                for labels in combinations((1, 2, 3, 5, 6, 7), 2)
            ),
        ),
        (Q(3, 20), ((2, 5, 7, 8),)),
    )
    reports = []
    for t_value, forced_brackets in cases:
        u_scalar = (
            Q(0), Q(1), Q(4, 5), Q(-3, 4), Q(3, 20),
            Q(1, 4), Q(1, 3), t_value,
        )
        v_particular, v_directions, v_rank = incidence_affine_space(
            u_scalar, color_three
        )
        w_particular, w_directions, w_rank = incidence_affine_space(
            u_scalar, color_two
        )
        if (v_rank, w_rank, len(v_directions), len(w_directions)) != (4, 4, 2, 2):
            raise AssertionError("frontier incidence rank changed")
        u = tuple(poly_constant(value) for value in u_scalar)
        v = affine_coordinate_polynomials(v_particular, v_directions, 0)
        w = affine_coordinate_polynomials(w_particular, w_directions, 2)
        if any(polynomial_collinearity(u, v, support) for support in color_three):
            raise AssertionError("color-three frontier parameterization is not exact")
        if any(polynomial_collinearity(u, w, support) for support in color_two):
            raise AssertionError("color-two frontier parameterization is not exact")
        points = tuple((u[index], v[index], w[index], one) for index in range(8))
        if t_value == Q(-3, 4) and points[3] != points[7]:
            raise AssertionError("t=-3/4 does not force P4=P8")
        if any(parent_bracket_polynomial(points, labels) for labels in forced_brackets):
            raise AssertionError(f"frontier parent-wall identity failed at t={t_value}")
        if not parent_bracket_polynomial(points, (1, 2, 3, 4)):
            raise AssertionError("frontier control bracket vanished identically")
        reports.append((str(t_value), tuple("".join(map(str, labels)) for labels in forced_brackets)))

    print(
        "PASS exact saturation semantics",
        "[1234] inverse and t(4t+3)(20t-3) inverse",
    )
    print(
        "PASS unsaturated interpolation-frontier exclusion",
        reports,
        "all force parent nonuniformity",
    )


def target_bracket_numerator(target):
    """Cleared numerator of parent bracket [2678] or [2467]."""
    vr, vs, wr, ws, t = (poly_variable(index) for index in range(5))
    one = poly_constant(1)
    p2 = (one, one, one, one)
    # P6 has been multiplied by 4t, a unit throughout the certified chain.
    p6 = (t, vs, t, poly_scale(t, 4))
    p7 = (poly_constant(Q(1, 3)), vr, wr, one)
    if target == 54:  # zero-based combination index for [2678]
        p8 = (t, vs, ws, one)
        columns = (p2, p6, p7, p8)
    elif target == 48:  # zero-based combination index for [2467]
        twenty_t_minus_three = poly_add(poly_scale(t, 20), poly_constant(-3))
        # P4 has been multiplied by 136(20t-3), also a unit on the chain.
        p4 = (
            poly_scale(twenty_t_minus_three, -102),
            poly_scale(
                poly_multiply(
                    poly_add(poly_scale(vr, 7), poly_constant(-8)),
                    twenty_t_minus_three,
                ),
                18,
            ),
            poly_scale(
                poly_add(
                    poly_add(poly_scale(poly_multiply(t, wr), 204), poly_scale(t, -44)),
                    poly_add(
                        poly_scale(wr, 153),
                        poly_add(poly_scale(ws, -144), poly_constant(-33)),
                    ),
                ),
                17,
            ),
            poly_scale(twenty_t_minus_three, 136),
        )
        columns = (p2, p4, p6, p7)
    else:
        raise AssertionError(f"unexpected target bracket {target}")
    return polynomial_determinant4(
        [[columns[column][row] for column in range(4)] for row in range(4)]
    )


def affine_transform(terms, midpoint, tangent, parameter, unknown):
    """Exactly substitute z=midpoint+tangent*s+y into sparse terms."""
    forms = []
    for old in range(5):
        form = {
            ZERO5: Q(midpoint[old]),
            (0, 0, 0, 0, 1): Q(1 if old == parameter else tangent[old]),
        }
        if old != parameter:
            exponent = [0] * 5
            exponent[unknown.index(old)] = 1
            form[tuple(exponent)] = Q(1)
        forms.append(form)
    answer = {}
    for monomial, coefficient in terms:
        term = {ZERO5: Q(coefficient)}
        for form, exponent in zip(forms, monomial):
            term = poly_multiply(term, poly_power(form, exponent))
        answer = poly_add(answer, term)
    return answer


def local_interval_evaluate(polynomial, variables, parameter, derivative=None):
    """Evaluate, or differentiate in y_0,...,y_3,s and evaluate."""
    coefficients = {}
    for monomial, scalar in polynomial.items():
        if derivative is not None and not monomial[derivative]:
            continue
        exponents = list(monomial)
        multiplier = exponents[derivative] if derivative is not None else 1
        if derivative is not None:
            exponents[derivative] -= 1
        value = base.Interval(Q(scalar) * multiplier)
        for index in range(4):
            for _ in range(exponents[index]):
                value *= variables[index]
        coefficients[exponents[4]] = coefficients.get(
            exponents[4], base.Interval(0)
        ) + value
    if not coefficients:
        return base.Interval(0)
    answer = base.Interval(0)
    for exponent in reversed(range(max(coefficients) + 1)):
        answer = answer * parameter + coefficients.get(exponent, base.Interval(0))
    return answer


def interval_matrix_vector(matrix, vector):
    return [
        sum(
            (matrix[row][column] * vector[column] for column in range(len(vector))),
            base.Interval(0),
        )
        for row in range(len(matrix))
    ]


def interval_matrix_multiply(left, right):
    return [
        [
            sum(
                (
                    left[row][middle] * right[middle][column]
                    for middle in range(len(right))
                ),
                base.Interval(0),
            )
            for column in range(len(right[0]))
        ]
        for row in range(len(left))
    ]


def inverse_rational(matrix):
    size = len(matrix)
    augmented = [
        [Q(value) for value in row]
        + [Q(1 if row_index == column else 0) for column in range(size)]
        for row_index, row in enumerate(matrix)
    ]
    for column in range(size):
        pivot = next(row for row in range(column, size) if augmented[row][column])
        augmented[column], augmented[pivot] = augmented[pivot], augmented[column]
        scalar = augmented[column][column]
        augmented[column] = [value / scalar for value in augmented[column]]
        for row in range(size):
            if row == column or not augmented[row][column]:
                continue
            scalar = augmented[row][column]
            augmented[row] = [
                left - scalar * right
                for left, right in zip(augmented[row], augmented[column])
            ]
    return [row[size:] for row in augmented]


def certify_chain_segment(left, right, radius):
    """Parametric Krawczyk inclusion with v_r as continuation parameter."""
    parameter = 0
    unknown = (1, 2, 3, 4)
    midpoint = tuple((a + b) / 2 for a, b in zip(left, right))
    delta = tuple(b - a for a, b in zip(left, right))
    if not delta[parameter]:
        raise AssertionError("zero v_r continuation step")
    tangent = [Q(0)] * 5
    tangent[parameter] = Q(1)
    for index in unknown:
        tangent[index] = delta[index] / delta[parameter]
    tangent = tuple(tangent)
    parameter_interval = base.Interval(
        -abs(delta[parameter]) / 2, abs(delta[parameter]) / 2
    )
    transformed = tuple(
        affine_transform(polynomial, midpoint, tangent, parameter, unknown)
        for polynomial in certificate.SYSTEM[:4]
    )
    box = [base.Interval(-radius, radius) for _ in range(4)]
    jacobian = [
        [
            local_interval_evaluate(polynomial, box, parameter_interval, column)
            for column in range(4)
        ]
        for polynomial in transformed
    ]
    midpoint_jacobian = [
        [
            local_interval_evaluate(
                polynomial, [base.Interval(0)] * 4, base.Interval(0), column
            ).lower
            for column in range(4)
        ]
        for polynomial in transformed
    ]
    preconditioner = [
        [base.Interval(value) for value in row]
        for row in inverse_rational(midpoint_jacobian)
    ]
    center_values = [
        local_interval_evaluate(
            polynomial, [base.Interval(0)] * 4, parameter_interval
        )
        for polynomial in transformed
    ]
    center = [
        -value for value in interval_matrix_vector(preconditioner, center_values)
    ]
    product = interval_matrix_multiply(preconditioner, jacobian)
    remainder = [
        [
            base.Interval(1 if row == column else 0) - product[row][column]
            for column in range(4)
        ]
        for row in range(4)
    ]
    correction = interval_matrix_vector(remainder, box)
    image = tuple(center[index] + correction[index] for index in range(4))
    if not all(
        box[index].lower < image[index].lower
        and image[index].upper < box[index].upper
        for index in range(4)
    ):
        return None
    original = []
    for old in range(5):
        value = base.Interval(midpoint[old]) + tangent[old] * parameter_interval
        if old != parameter:
            value += image[unknown.index(old)]
        original.append(value)
    return {
        "left": left,
        "right": right,
        "radius": radius,
        "midpoint": midpoint,
        "tangent": tangent,
        "unknown": unknown,
        "parameter_interval": parameter_interval,
        "transformed": transformed,
        "image": image,
        "original": tuple(original),
    }


def chain_parent_brackets(point):
    vr, vs, wr, ws, t = point
    interval = base.Interval
    u = (
        interval(0), interval(1), interval(Q(4, 5)), interval(Q(-3, 4)),
        interval(Q(3, 20)), interval(Q(1, 4)), interval(Q(1, 3)), t,
    )
    v = (
        interval(0), interval(1),
        (315 * t * vr - 360 * t - 252 * vr + 527 * vs + 288)
        / (85 * (4 * t + 3)),
        9 * (7 * vr - 8) / 68,
        9 * vr / 20,
        vs / (4 * t),
        vr,
        vs,
    )
    w = (
        interval(0), interval(1),
        (33 * wr - 7) / 5,
        (204 * t * wr - 44 * t + 153 * wr - 144 * ws - 33)
        / (8 * (20 * t - 3)),
        (51 * wr - 11) / 40,
        interval(Q(1, 4)),
        wr,
        ws,
    )
    points = tuple(zip(u, v, w, (interval(1),) * 8))
    return tuple(
        base.determinant(
            [[points[column][row] for column in indices] for row in range(4)]
        )
        for indices in combinations(range(8), 4)
    )


def transformed_target(cell, target):
    return affine_transform(
        tuple(target_bracket_numerator(target).items()),
        cell["midpoint"],
        cell["tangent"],
        0,
        cell["unknown"],
    )


def target_interval(cell, target, endpoint=None):
    parameter = cell["parameter_interval"]
    if endpoint is not None:
        parameter = base.Interval(
            parameter.lower if endpoint < 0 else parameter.upper
        )
    return local_interval_evaluate(
        transformed_target(cell, target), cell["image"], parameter
    )


def transverse_target_derivative(cell, target):
    """Schur-complement derivative dg/dv_r along the certified root graph."""
    equations = cell["transformed"]
    target_polynomial = transformed_target(cell, target)
    variables = cell["image"]
    parameter = cell["parameter_interval"]
    four = [
        [
            local_interval_evaluate(polynomial, variables, parameter, column)
            for column in range(4)
        ]
        for polynomial in equations
    ]
    five = [
        [
            local_interval_evaluate(polynomial, variables, parameter, column)
            for column in range(5)
        ]
        for polynomial in equations + (target_polynomial,)
    ]
    denominator = base.determinant(four)
    numerator = base.determinant(five)
    if denominator.contains_zero() or numerator.contains_zero():
        raise AssertionError("target transversality determinant is not separated")
    return numerator / denominator


def interval_margin(value):
    if value.contains_zero():
        return Q(0)
    return min(abs(value.lower), abs(value.upper))


def verify_boundary_chain(fold_values):
    raw = BOUNDARY_CHAIN.read_bytes()
    if hashlib.sha256(raw).hexdigest() != BOUNDARY_CHAIN_DIGEST:
        raise AssertionError("boundary-chain data digest changed")
    payload = json.loads(raw)
    if (
        payload.get("schema") != BOUNDARY_CHAIN_SCHEMA
        or payload.get("presentation") != [5_563, 16_134, 19_284]
        or payload.get("coordinate_order") != ["vr", "vs", "wr", "ws", "t"]
        or payload.get("parameter_index") != 0
        or len(payload.get("branches", ())) != 2
    ):
        raise AssertionError("bad boundary-chain metadata")
    denominator = payload.get("denominator")
    if denominator != 10**13:
        raise AssertionError("boundary-chain denominator changed")

    certified_branches = []
    total_segments = 0
    total_glues = 0
    global_margin = None
    exit_report = []
    expected = (
        (-1, 54, ((Q(1, 10**6), 157), (Q(1, 500_000), 3))),
        (1, 48, ((Q(1, 5_000_000), 160),)),
    )
    for record, (direction, target, expected_histogram) in zip(
        payload["branches"], expected
    ):
        if (
            record.get("direction") != direction
            or record.get("target_parent_bracket_index_zero_based") != target
        ):
            raise AssertionError("boundary-chain branch metadata changed")
        vertices = tuple(
            tuple(Q(numerator, denominator) for numerator in row)
            for row in record.get("vertices", ())
        )
        if len(vertices) != 161 or any(len(row) != 5 for row in vertices):
            raise AssertionError("boundary-chain vertex count changed")
        cells = []
        histogram = defaultdict(int)
        candidates = (
            (Q(1, 10**6), Q(1, 500_000))
            if direction < 0
            else (Q(1, 5_000_000),)
        )
        for left, right in zip(vertices, vertices[1:]):
            cell = None
            for radius in candidates:
                cell = certify_chain_segment(left, right, radius)
                if cell is not None:
                    histogram[radius] += 1
                    break
            if cell is None:
                raise AssertionError("parametric Krawczyk segment failed")
            cells.append(cell)
        if tuple(sorted(histogram.items())) != tuple(sorted(expected_histogram)):
            raise AssertionError(f"Krawczyk radius histogram changed: {histogram}")

        # Consecutive cells have the literal same rational predictor endpoint.
        # Their centered scalar-radius boxes are nested, hence uniqueness in the
        # larger box identifies the two endpoint roots.
        for left, right in zip(cells, cells[1:]):
            if left["right"] != right["left"]:
                raise AssertionError("nonmatching rational chain endpoint")
            total_glues += 1

        target_hits = []
        branch_margin = None
        for index, cell in enumerate(cells):
            brackets = chain_parent_brackets(cell["original"])
            if len(brackets) != 70:
                raise AssertionError("parent-bracket count changed")
            bad_other = [
                number
                for number, value in enumerate(brackets)
                if number != target and value.contains_zero()
            ]
            if bad_other:
                raise AssertionError(
                    f"unexpected parent wall on branch {direction}: {bad_other}"
                )
            for number, value in enumerate(brackets):
                if number == target:
                    continue
                margin = interval_margin(value)
                branch_margin = margin if branch_margin is None else min(branch_margin, margin)
            target_value = target_interval(cell, target)
            if target_value.contains_zero():
                target_hits.append(index)
            elif index:
                branch_margin = min(branch_margin, interval_margin(target_value))
        if target_hits != [0]:
            raise AssertionError(f"target wall is not isolated: {target_hits}")
        first = cells[0]
        endpoint_values = (
            target_interval(first, target, -1),
            target_interval(first, target, 1),
        )
        if (
            endpoint_values[0].contains_zero()
            or endpoint_values[1].contains_zero()
            or endpoint_values[0].lower * endpoint_values[1].lower >= 0
        ):
            raise AssertionError("target endpoint signs are not opposite")
        derivative = transverse_target_derivative(first, target)
        global_margin = (
            branch_margin if global_margin is None else min(global_margin, branch_margin)
        )
        exit_report.append(
            (
                target,
                (float(endpoint_values[0].lower), float(endpoint_values[0].upper)),
                (float(endpoint_values[1].lower), float(endpoint_values[1].upper)),
                (float(derivative.lower), float(derivative.upper)),
            )
        )
        certified_branches.append(cells)
        total_segments += len(cells)

    bridge_radius = Q(*payload.get("bridge_radius", ()))
    bridge = certify_chain_segment(
        certified_branches[0][-1]["right"],
        certified_branches[1][-1]["right"],
        bridge_radius,
    )
    if bridge is None:
        raise AssertionError("fold bridge Krawczyk inclusion failed")
    for attachment in (
        (certified_branches[0][-1], bridge, "right", "left"),
        (certified_branches[1][-1], bridge, "right", "right"),
    ):
        branch_cell, bridge_cell, branch_side, bridge_side = attachment
        if branch_cell[branch_side] != bridge_cell[bridge_side]:
            raise AssertionError("fold bridge endpoint mismatch")
        total_glues += 1
    fold_parameter = fold_values[0] - bridge["midpoint"][0]
    if not (
        bridge["parameter_interval"].lower <= fold_parameter.lower
        and fold_parameter.upper <= bridge["parameter_interval"].upper
    ):
        raise AssertionError("RUR fold is outside bridge parameter interval")
    for old_index in bridge["unknown"]:
        fold_local = (
            fold_values[old_index]
            - bridge["midpoint"][old_index]
            - bridge["tangent"][old_index] * fold_parameter
        )
        if not (
            -bridge_radius <= fold_local.lower
            and fold_local.upper <= bridge_radius
        ):
            raise AssertionError("RUR fold is outside bridge Krawczyk box")
    bridge_brackets = chain_parent_brackets(bridge["original"])
    bridge_bad = [
        number for number, value in enumerate(bridge_brackets) if value.contains_zero()
    ]
    if bridge_bad:
        raise AssertionError(f"parent wall meets fold bridge: {bridge_bad}")
    global_margin = min(
        global_margin, *(interval_margin(value) for value in bridge_brackets)
    )

    print(
        "PASS exact rational boundary chain",
        f"vertices={sum(len(branch) + 1 for branch in certified_branches)}",
        f"segments={total_segments}+1_bridge",
        f"shared_endpoint_glues={total_glues}",
        "RUR_fold_in_bridge=yes",
        "radius_histograms=((1e-6:157,2e-6:3),(2e-7:160))",
    )
    print(
        "PASS transverse source-parent exits",
        exit_report,
        f"all_other_parent_margin>{float(global_margin):.8g}",
    )
    print(
        "GRAPH [2678] boundary -- 160-cell sheet -- fold bridge -- "
        "160-cell sheet -- [2467] boundary"
    )


CRITICAL_ROOT_BOUNDS = (
    (Q(-1, 2), Q(-1, 4)),
    (Q(-1, 50), Q(-1, 100)),
    (Q(0), Q(3, 1000)),
    (Q(1, 10), Q(2, 5)),
    (Q(7, 10), Q(1)),
    (Q(2), Q(3)),
)
CRITICAL_SIGN_DIGESTS = (
    "e6e37c708cb7e7e893ffb8917a441d98700bb92370f1cd98887dd036e0a4caab",
    "f73af4b61ea38520f7f2b56b6ab45b0b0b63b9c3069775b15b89feef0d427547",
    "8d5653502dc82bb91f71f61658c9faeba9c98485819c8479ecb83e26eab98378",
    "4d27866ee9ee4a26c5b4e20e65e39e43de683323ee2feff9193ebc83c60cf959",
    "4a4bc02f3ece6cec7d03ebe4f8945ec4e80b8732b790ad21988df4379f8d97c6",
    "7b490ffdad4d6655d714298afc9abb779f539433dd6c911bfda0025a34d81850",
)
CRITICAL_POSITIVE_COUNTS = (35, 32, 36, 36, 42, 49)
CRITICAL_FOLD_HAMMING = (37, 36, 32, 36, 0, 11)


def isolate_critical_root(left, right, bits=220):
    elimination = list(certificate.ELIMINATION)
    left_value = base.evaluate(elimination, left)
    right_value = base.evaluate(elimination, right)
    if not left_value or not right_value or left_value * right_value >= 0:
        raise AssertionError("critical root bracket does not change sign")
    while right - left > Q(1, 1 << bits):
        midpoint = (left + right) / 2
        midpoint_value = base.evaluate(elimination, midpoint)
        if not midpoint_value:
            left = midpoint - Q(1, 1 << (bits + 2))
            right = midpoint + Q(1, 1 << (bits + 2))
            break
        if left_value * midpoint_value < 0:
            right = midpoint
            right_value = midpoint_value
        else:
            left = midpoint
            left_value = midpoint_value
    derivative = [
        exponent * elimination[exponent]
        for exponent in range(1, len(elimination))
    ]
    root = base.Interval(left, right)
    derivative_interval = base.interval_evaluate(derivative, root)
    if derivative_interval.contains_zero():
        raise AssertionError("critical elimination root is not simple")
    return root, derivative_interval


def critical_coordinates(root, derivative_interval):
    return tuple(
        -base.interval_evaluate(polynomial, root)
        / (denominator * derivative_interval)
        for polynomial, denominator in certificate.PARAMETERS
    )


def critical_fold_invariants(values):
    jacobian5 = [
        [
            sparse_interval_evaluate(
                sparse_derivative(terms, variable), values
            )
            for variable in range(5)
        ]
        for terms in certificate.SYSTEM
    ]
    full_determinant = base.determinant(jacobian5)
    if full_determinant.contains_zero():
        raise AssertionError("critical full five-equation Jacobian is singular")
    fiber = [row[:4] for row in jacobian5[:4]]
    witness = None
    for rows in combinations(range(4), 3):
        for columns in combinations(range(4), 3):
            minor = base.determinant(
                [[fiber[row][column] for column in columns] for row in rows]
            )
            if not minor.contains_zero():
                witness = (rows, columns, minor)
                break
        if witness is not None:
            break
    if witness is None:
        raise AssertionError("critical fiber rank-three minor is not separated")
    rows, columns, _minor = witness
    omitted_column = next(column for column in range(4) if column not in columns)
    omitted_row = next(row for row in range(4) if row not in rows)
    right_solved = solve3(
        [[fiber[row][column] for column in columns] for row in rows],
        [-fiber[row][omitted_column] for row in rows],
    )
    right_kernel = [base.Interval(0)] * 4
    right_kernel[omitted_column] = base.Interval(1)
    for column, value in zip(columns, right_solved):
        right_kernel[column] = value
    left_solved = solve3(
        [[fiber[row][column] for row in rows] for column in columns],
        [-fiber[omitted_row][column] for column in columns],
    )
    left_kernel = [base.Interval(0)] * 4
    left_kernel[omitted_row] = base.Interval(1)
    for row, value in zip(rows, left_solved):
        left_kernel[row] = value
    alpha = sum(
        (left_kernel[row] * jacobian5[row][4] for row in range(4)),
        base.Interval(0),
    )
    contractions = []
    for equation in certificate.SYSTEM[:4]:
        contraction = base.Interval(0)
        for left in range(4):
            for right in range(4):
                contraction += (
                    right_kernel[left]
                    * right_kernel[right]
                    * sparse_interval_evaluate(
                        sparse_derivative(
                            sparse_derivative(equation, left), right
                        ),
                        values,
                    )
                )
        contractions.append(contraction)
    beta = sum(
        (left_kernel[row] * contractions[row] for row in range(4)),
        base.Interval(0),
    )
    second_t = -beta / alpha
    if second_t.contains_zero():
        raise AssertionError("critical point is not a simple fold")
    return full_determinant, second_t, witness


def verify_complete_real_critical_census():
    records = []
    for root_number, ((left, right), expected_digest) in enumerate(
        zip(CRITICAL_ROOT_BOUNDS, CRITICAL_SIGN_DIGESTS), start=1
    ):
        root, derivative_interval = isolate_critical_root(left, right)
        coordinates = critical_coordinates(root, derivative_interval)
        values = tuple(coordinates) + (root,)
        brackets = chain_parent_brackets(values)
        if any(value.contains_zero() for value in brackets):
            raise AssertionError(f"critical root {root_number} meets a parent wall")
        signs = "".join("+" if value.lower > 0 else "-" for value in brackets)
        digest = hashlib.sha256(signs.encode("ascii")).hexdigest()
        if digest != expected_digest:
            raise AssertionError(f"critical chamber digest {root_number} changed")
        full_determinant, second_t, witness = critical_fold_invariants(values)
        records.append(
            {
                "root": root,
                "coordinates": coordinates,
                "values": values,
                "signs": signs,
                "margin": min(interval_margin(value) for value in brackets),
                "det5": full_determinant,
                "second_t": second_t,
                "rank_minor": witness,
            }
        )
    fold_signs = records[4]["signs"]
    positive_counts = tuple(record["signs"].count("+") for record in records)
    hamming = tuple(
        sum(left != right for left, right in zip(record["signs"], fold_signs))
        for record in records
    )
    if (
        positive_counts != CRITICAL_POSITIVE_COUNTS
        or hamming != CRITICAL_FOLD_HAMMING
        or [index for index, distance in enumerate(hamming) if distance == 0] != [4]
    ):
        raise AssertionError("critical parent-chamber classification changed")
    print(
        "PASS dependency-free six-real-critical census",
        "all six simple folds",
        "positive_brackets=" + repr(positive_counts),
        "fold_chamber_hamming=" + repr(hamming),
    )
    print(
        "PASS unique in-chamber critical point",
        "root=5",
        "t=[%.16g,%.16g]" % (
            float(records[4]["root"].lower),
            float(records[4]["root"].upper),
        ),
        "margin>%.12g" % float(records[4]["margin"]),
    )
    return records


def verify_complete_critical_provenance(msolve_binary):
    raw = COMPLETE_CRITICAL_INPUT.read_bytes()
    if (
        len(raw) != 2_992
        or hashlib.sha256(raw).hexdigest() != COMPLETE_CRITICAL_INPUT_DIGEST
        or len(raw.splitlines()) != 9
    ):
        raise AssertionError("complete-critical msolve input changed")
    # A one-coefficient corruption must be caught by the pinned semantic hash.
    corrupted = raw.replace(b"-315*t*vr", b"-316*t*vr", 1)
    if (
        corrupted == raw
        or hashlib.sha256(corrupted).hexdigest() == COMPLETE_CRITICAL_INPUT_DIGEST
    ):
        raise AssertionError("complete-critical corruption canary failed")
    if msolve_binary is not None:
        with tempfile.TemporaryDirectory(prefix="diag3-critical-") as directory:
            output = Path(directory) / "critical.out"
            command = (
                str(msolve_binary), "-P", "1", "-p", "256", "-v", "1",
                "-f", str(COMPLETE_CRITICAL_INPUT), "-o", str(output),
            )
            completed = subprocess.run(
                command, check=False, stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT, text=True,
            )
            if completed.returncode:
                raise AssertionError(
                    "msolve completeness replay failed:\n" + completed.stdout[-4000:]
                )
            digest = hashlib.sha256(output.read_bytes()).hexdigest()
            if digest != COMPLETE_CRITICAL_OUTPUT_DIGEST:
                raise AssertionError(f"msolve output digest changed: {digest}")
        replay = "fresh_output_digest=PASS"
    else:
        replay = "fresh replay available with --msolve /path/to/msolve"
    print(
        "TRUST exact msolve-0.10.1 saturation boundary",
        "ideal_degree=20 squarefree_t_eliminant_degree=20 real_roots=6",
        "input=" + COMPLETE_CRITICAL_INPUT_DIGEST,
        "output=" + COMPLETE_CRITICAL_OUTPUT_DIGEST,
        replay,
    )


def verify_local_fold(occurrences, occurrence_factor):
    payload = (
        certificate.ELIMINATION,
        certificate.PARAMETERS,
        certificate.SYSTEM,
    )
    digest = hashlib.sha256(repr(payload).encode("ascii")).hexdigest()
    if digest != base.EXPECTED_DIGEST or digest != certificate.SEMANTIC_SHA256:
        raise AssertionError("ramification RUR semantic changed")
    if tuple(occurrence_factor[support] for support in base.SELECTED) != (
        base.EXPECTED_FACTORS
    ):
        raise AssertionError("selected occurrence/factor map changed")

    base.verify_support_ranks()
    base.verify_sparse_system()
    root, coordinates, bracket_margin, _rank_minor, points = base.verify_rur()
    suspects, factor_margin, factor_digest = base.verify_no_extra_factor(
        points, occurrences, occurrence_factor
    )
    if factor_digest != base.EXPECTED_FACTOR_INTERVAL_DIGEST:
        raise AssertionError("all-factor interval semantic changed")

    values = list(coordinates) + [root]
    jacobian5 = [
        [
            sparse_interval_evaluate(
                sparse_derivative(terms, variable), values
            )
            for variable in range(5)
        ]
        for terms in certificate.SYSTEM
    ]
    fold_determinant = base.determinant(jacobian5)
    if fold_determinant.contains_zero():
        raise AssertionError("five-equation Jacobian is not separated")

    # Rank(D_fiber F)=3.  Normalize right and left nullvectors by fixing their
    # fourth entries to one.  Differentiating F(x(s),t(s)) twice at t'=0 gives
    #   (left . F_t) t'' + left . F_xx[right,right] = 0.
    # Its separated sign pins the side on which the two sheet germs occur.
    fiber_jacobian = [row[:4] for row in jacobian5[:4]]
    right_kernel = solve3(
        [row[:3] for row in fiber_jacobian[:3]],
        [-row[3] for row in fiber_jacobian[:3]],
    ) + [base.Interval(1)]
    left_kernel = solve3(
        [
            [fiber_jacobian[column][row] for column in range(3)]
            for row in range(3)
        ],
        [-fiber_jacobian[3][row] for row in range(3)],
    ) + [base.Interval(1)]
    alpha = sum(
        (
            left_kernel[row] * jacobian5[row][4]
            for row in range(4)
        ),
        base.Interval(0),
    )
    contractions = []
    for equation in certificate.SYSTEM[:4]:
        contraction = base.Interval(0)
        for left in range(4):
            for right in range(4):
                second = sparse_derivative(
                    sparse_derivative(equation, left), right
                )
                contraction += (
                    right_kernel[left]
                    * right_kernel[right]
                    * sparse_interval_evaluate(second, values)
                )
        contractions.append(contraction)
    beta = sum(
        (left_kernel[row] * contractions[row] for row in range(4)),
        base.Interval(0),
    )
    second_t = -beta / alpha
    if second_t.contains_zero() or second_t.upper >= 0:
        raise AssertionError("fold direction is not strictly toward t<t0")

    # The affine/gauge and parent-column denominators are units here.  In the
    # normalized concurrence chart h_j=1 exactly for all eight columns.
    interpolation = (root, 4 * root + 3, 20 * root - 3)
    if any(value.contains_zero() for value in interpolation):
        raise AssertionError("interpolation denominator contains zero")

    normals = tuple(
        plane_normal(points, triple) for triple in base.labeled.TRIPLES
    )
    normal_witnesses = []
    for support in base.SELECTED:
        witness = None
        for rows in combinations(support, 3):
            for columns in combinations(range(4), 3):
                value = base.determinant(
                    [
                        [normals[row][column] for column in columns]
                        for row in rows
                    ]
                )
                if not value.contains_zero():
                    witness = (rows, columns, value)
                    break
            if witness is not None:
                break
        if witness is None:
            raise AssertionError("occurrence normal rank is not separated")
        normal_witnesses.append(witness)

    print(
        "PASS exact simple-fold attachment",
        "det5=[%.12g,%.12g]" % (
            float(fold_determinant.lower),
            float(fold_determinant.upper),
        ),
        "d2t=[%.12g,%.12g]" % (
            float(second_t.lower),
            float(second_t.upper),
        ),
    )
    print(
        "PASS local frontier separation",
        f"parent_brackets=70 margin>{float(bracket_margin):.8g}",
        "h_j=1 gauge=1",
        "fiber_projective_homogenizers=1",
        "interpolation=" + repr(
            tuple(
                (float(value.lower), float(value.upper))
                for value in interpolation
            )
        ),
    )
    print(
        "PASS occurrence-normal ranks",
        tuple(
            (
                rows,
                columns,
                float(value.lower),
                float(value.upper),
            )
            for rows, columns, value in normal_witnesses
        ),
    )
    print(
        "PASS internal-divisor separation",
        "only", tuple(factor for factor, _ in suspects), "vanish among 26740",
        f"nonzero_margin_bits={factor_margin.bit_length()}",
    )
    print(
        "GRAPH two t<t0 regular sheet germs -- one internal simple-fold vertex; "
        "no local parent/chart/projective-infinity/other-factor boundary"
    )
    return tuple(values)


def parse_morse_originals():
    if source_scan.sha256(source_scan.MORSE_CERTIFICATE) != (
        source_scan.MORSE_CERTIFICATE_DIGEST
    ):
        raise AssertionError("Morse certificate digest changed")
    raw = source_scan.MORSE_CERTIFICATE.read_bytes()
    header = "<8sIHHHIII"
    magic, count, *_ = struct.unpack_from(header, raw)
    if magic != source_scan.MORSE_MAGIC or count != source_scan.MORSE_CLOSED_COUNT:
        raise AssertionError("bad Morse certificate header")
    position = struct.calcsize(header)
    fixed = "<HHHHHbB"
    originals = set()
    for _ in range(count):
        first, second, third, _frame, _variables, _scalar, factor_count = (
            struct.unpack_from(fixed, raw, position)
        )
        position += struct.calcsize(fixed) + factor_count
        originals.add((first, second, third))
    if position != len(raw) or len(originals) != count:
        raise AssertionError("bad Morse certificate body")
    return originals


def verify_source_accounting(union4: Path | None):
    occurrences, occurrence_factor, _polynomials = base.labeled.factor_polynomials()
    factor_occurrence = base.labeled.factor_action_is_well_defined(
        occurrences, occurrence_factor
    )
    by_factor = defaultdict(list)
    for occurrence in occurrences:
        by_factor[occurrence_factor[occurrence]].append(occurrence)

    for source, canonical, permutation, expected in zip(
        HARD_PRESENTATIONS,
        CANONICAL_ROWS,
        LABEL_PERMUTATIONS,
        EXPECTED_IMAGES,
    ):
        mapping = base.labeled.triple_map(
            tuple(label - 1 for label in permutation)
        )
        image = tuple(
            base.labeled.transform_factor(
                factor, mapping, factor_occurrence, occurrence_factor
            )
            for factor in source
        )
        if image != expected or set(image) != set(canonical):
            raise AssertionError(f"hard-presentation map changed: {source}")

    def occurrence_payload(rows):
        return tuple(
            (
                row,
                tuple(
                    (factor, tuple(sorted(by_factor[factor])))
                    for factor in row
                ),
            )
            for row in rows
        )

    named_digest = hashlib.sha256(
        repr(occurrence_payload(HARD_PRESENTATIONS)).encode("ascii")
    ).hexdigest()
    canonical_digest = hashlib.sha256(
        repr(occurrence_payload(DISTINCT_CANONICAL_ROWS)).encode("ascii")
    ).hexdigest()
    products = tuple(
        prod(len(by_factor[factor]) for factor in row)
        for row in DISTINCT_CANONICAL_ROWS
    )
    if (
        named_digest != EXPECTED_NAMED_OCCURRENCE_DIGEST
        or canonical_digest != EXPECTED_CANONICAL_OCCURRENCE_DIGEST
        or products != EXPECTED_CANONICAL_OCCURRENCE_PRODUCTS
    ):
        raise AssertionError("hard-canary occurrence accounting changed")

    feature_raw = source_scan.TRIANGULAR_FEATURES.read_bytes()
    if source_scan.sha256(source_scan.TRIANGULAR_FEATURES) != (
        source_scan.TRIANGULAR_FEATURE_DIGEST
    ):
        raise AssertionError("triangular feature digest changed")
    factor_count, = struct.unpack_from("<I", feature_raw)
    features = tuple(
        struct.unpack_from("<HH", feature_raw, 4 + 4 * factor)
        for factor in range(factor_count)
    )
    morse = parse_morse_originals()
    if hashlib.sha256(CONSTANT_SHEAR.read_bytes()).hexdigest() != (
        CONSTANT_SHEAR_DIGEST
    ):
        raise AssertionError("constant-shear digest changed")
    constant_shear = {
        tuple(record["original"])
        for record in json.loads(CONSTANT_SHEAR.read_text())["records"]
    }
    for row in DISTINCT_CANONICAL_ROWS:
        if source_scan.triangular_works(row, features):
            raise AssertionError(f"hard row became triangular: {row}")
        if row in morse or row in constant_shear:
            raise AssertionError(f"hard row entered a later closure: {row}")

    if union4 is not None:
        if source_scan.sha256(union4) != EXPECTED_UNION4_DIGEST:
            raise AssertionError("union-four bucket digest changed")
        raw = union4.read_bytes()
        count, = struct.unpack_from("<I", raw)
        if count != EXPECTED_UNION4_COUNT or len(raw) != 4 + 6 * count:
            raise AssertionError("bad union-four bucket")
        wanted = set(DISTINCT_CANONICAL_ROWS)
        found = set()
        for index in range(count):
            row = struct.unpack_from("<HHH", raw, 4 + 6 * index)
            if row in wanted:
                found.add(row)
        if found != wanted:
            raise AssertionError(f"hard canonical rows missing: {wanted - found}")
        if count - source_scan.TRIANGULAR_CLOSED_COUNT - len(morse) - len(
            constant_shear
        ) != EXPECTED_FINAL_UNRESOLVED:
            raise AssertionError("final residue arithmetic changed")
        provenance = f"union4={count} final={EXPECTED_FINAL_UNRESOLVED}"
    else:
        provenance = "union4 membership requires --union4"

    print(
        "PASS hard source map",
        "six presentations -> five canonical rows",
        DISTINCT_CANONICAL_ROWS,
    )
    print(
        "PASS hard occurrence accounting",
        products,
        "total", sum(products),
        "semantic", canonical_digest,
    )
    print(
        "PASS hard later-layer exclusion",
        "nontriangular/not-Morse/not-constant-shear",
        provenance,
    )
    return occurrences, occurrence_factor


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--union4",
        type=Path,
        help="pinned diag3_union_degree4.bin for exact source membership",
    )
    parser.add_argument(
        "--msolve",
        type=Path,
        help="optional msolve-0.10.1 binary for fresh critical-ideal replay",
    )
    arguments = parser.parse_args()
    verify_saturation_frontiers()
    verify_complete_critical_provenance(arguments.msolve)
    critical_records = verify_complete_real_critical_census()
    occurrences, occurrence_factor = verify_source_accounting(arguments.union4)
    fold_values = verify_local_fold(occurrences, occurrence_factor)
    for broad, narrow in zip(fold_values, critical_records[4]["values"]):
        if broad.upper < narrow.lower or narrow.upper < broad.lower:
            raise AssertionError("local fold and complete critical census disagree")
    verify_boundary_chain(fold_values)
    print(
        "THEOREM under the pinned exact msolve saturation trust boundary: "
        "the selected unsaturated affine concurrence slice has no compact component; "
        "its unique in-chamber t-critical point lies on the certified "
        "boundary-to-boundary component"
    )
    print(
        "SCOPE pinned affine slice only; all-factor separation is fold-local; "
        "no full nine-variable factor-triple/orbit theorem or triple H_c^0 closure"
    )


if __name__ == "__main__":
    main()
