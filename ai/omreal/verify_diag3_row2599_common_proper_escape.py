#!/usr/bin/env python3
"""Exact local common proper escape for the row-2599 flow-triangle triple.

This verifies one parent-resident ray on which the three signatures from
``verify_diag3_joined_flow_triangle.py`` remain simultaneously bad.  It is a
local compact-component certificate.  It does not construct the missing
mixed-block ``d3`` cell or any of its comparison faces.
"""

from __future__ import annotations

from fractions import Fraction
from hashlib import sha256
from itertools import combinations, product
from math import comb, prod
from pathlib import Path
import sys

import numpy as np


HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import BLOCK_GORDAN_ENDPOINT_WALL_REROUTE as exact  # noqa: E402
import prototype_koszul_circuits as koszul  # noqa: E402
import verify_diag2_moving_witness_shear as moving  # noqa: E402
import verify_diag3_joined_flow_triangle as joined  # noqa: E402


SOURCE = HERE / "data/seeat_parent2599_upper178.npz"
SOURCE_SHA256 = "3b90799d26b7783e92c2ac697eaaf8b76d26a787f53205873b997657e114180a"
START_CHART = 0
TARGET_CHART = 1
MOVING_COLUMN = 6  # zero based: labelled column 7
ENDPOINT = Fraction(23_597_311, 105_015_122)
ENDPOINT_BRACKET = (2, 4, 6, 7)
EXPECTED_DIRECTION = (81, -262, 91, 86)
PERSISTENT_SUPPORTS = (
    (0, 19, 21, 37, 38),
    (0, 9, 27, 30, 35),
    (0, 11, 17, 24, 40),
)
EXPECTED_SUPPORT_LABELS = (
    ("123", "456", "137", "238", "148"),
    ("123", "345", "257", "167", "128"),
    ("123", "136", "256", "247", "348"),
)

# Bounded comparison-cube regressions.  The three elementary roots are the
# pair choices d01,d12,d20 in the joined flow triangle.  U is each root's
# exact first-parent-wall parameter at chart zero.  The cube uses the common
# ray parameter s and ordered root amplitudes (1-s)xU_i,(1-s)yU_j.
PAIR_ROOTS = ((2, 8, -1), (1, 2, -1), (1, 3, +1))
ROOT_ENDPOINTS = (
    Fraction(1_221_971_981, 1_769_366_234),
    Fraction(42_214_994, 2_183_619_501),
    Fraction(425_791_163, 1_286_992_887),
)
BLOCK_ROOT_PAIRS = ((0, 2), (0, 1), (1, 2))
EXPECTED_TAPERED_PARENT_ZERO_COUNTS = (3, 3, 3, 3, 3, 3)

# Exact negative regression for a tempting but false common-root shortcut.
# On block 1's fixed support, (1 -> 3,+) transports rows 167 and 128 with
# opposite orthant signs, so fixed-witness naturality fails.
FALSE_COMMON_ROOT = (1, 3, +1)
FALSE_COMMON_ROOT_CONFLICT = ((30, -1), (35, +1))


# Sparse Q[s,x,y] arithmetic, only for the bounded exact cube replay.
ZERO3 = (0, 0, 0)


def mp_constant(value):
    value = Fraction(value)
    return {} if not value else {ZERO3: value}


def mp_add(left, right):
    answer = dict(left)
    for exponent, coefficient in right.items():
        answer[exponent] = answer.get(exponent, Fraction(0)) + coefficient
        if not answer[exponent]:
            del answer[exponent]
    return answer


def mp_scale(value, scalar):
    scalar = Fraction(scalar)
    return {} if not scalar else {
        exponent: scalar * coefficient for exponent, coefficient in value.items()
    }


def mp_multiply(left, right):
    answer = {}
    for first, x in left.items():
        for second, y in right.items():
            exponent = tuple(first[index] + second[index] for index in range(3))
            answer[exponent] = answer.get(exponent, Fraction(0)) + x * y
    return {exponent: value for exponent, value in answer.items() if value}


def mp_determinant(matrix):
    if not matrix:
        return mp_constant(1)
    answer = {}
    for column, entry in enumerate(matrix[0]):
        minor = [row[:column] + row[column + 1 :] for row in matrix[1:]]
        term = mp_multiply(entry, mp_determinant(minor))
        answer = mp_add(answer, term if not column & 1 else mp_scale(term, -1))
    return answer


def mp_degrees(value):
    return tuple(
        max((exponent[index] for exponent in value), default=0)
        for index in range(3)
    )


def mp_bernstein(value):
    degrees = mp_degrees(value)
    answer = []
    for index in product(*(range(degree + 1) for degree in degrees)):
        answer.append(sum(
            coefficient
            * prod(
                Fraction(comb(index[axis], exponent[axis]),
                         comb(degrees[axis], exponent[axis]))
                for axis in range(3)
            )
            for exponent, coefficient in value.items()
            if all(exponent[axis] <= index[axis] for axis in range(3))
        ))
    return tuple(answer)


def tapered_matrix(start, direction, order):
    matrix = [
        [mp_constant(int(start[row, column])) for column in range(8)]
        for row in range(4)
    ]
    s = {(1, 0, 0): Fraction(1)}
    root_variables = (
        {(0, 1, 0): Fraction(1)},
        {(0, 0, 1): Fraction(1)},
    )
    one_minus_s = {ZERO3: Fraction(1), (1, 0, 0): Fraction(-1)}
    for row in range(4):
        matrix[row][MOVING_COLUMN] = mp_add(
            matrix[row][MOVING_COLUMN],
            mp_scale(s, ENDPOINT * int(direction[row])),
        )
    for root_index, variable in zip(order, root_variables, strict=True):
        source, target, parameter_sign = PAIR_ROOTS[root_index]
        amplitude = mp_scale(
            mp_multiply(one_minus_s, variable),
            parameter_sign * ROOT_ENDPOINTS[root_index],
        )
        for row in range(4):
            matrix[row][source - 1] = mp_add(
                matrix[row][source - 1],
                mp_multiply(amplitude, matrix[row][target - 1]),
            )
    return matrix


def mp_normals(matrix):
    normals = []
    for triple in koszul.TRIPLES:
        columns = [[matrix[row][label - 1] for label in triple] for row in range(4)]
        normal = []
        for omitted in range(4):
            minor = [row for index, row in enumerate(columns) if index != omitted]
            normal.append(mp_scale(mp_determinant(minor), (-1) ** (omitted + 5)))
        normals.append(tuple(normal))
    return tuple(normals)


def mp_circuit(normals, signature, support):
    columns = [
        tuple(mp_scale(value, moving.signature_sign(signature, index)) for value in normals[index])
        for index in support
    ]
    coefficients = []
    for omitted in range(5):
        retained = [column for index, column in enumerate(columns) if index != omitted]
        value = mp_determinant([
            [retained[column][row] for column in range(4)] for row in range(4)
        ])
        coefficients.append(value if not omitted & 1 else mp_scale(value, -1))
    return tuple(coefficients)


def mp_at_origin(value):
    return value.get(ZERO3, Fraction(0))


def verify_bounded_tapered_cubes(start, direction, base_brackets):
    orders = tuple(
        order
        for pair in BLOCK_ROOT_PAIRS
        for order in (pair, pair[::-1])
    )
    zero_counts = []
    for block, order in zip((0, 0, 1, 1, 2, 2), orders, strict=True):
        matrix = tapered_matrix(start, direction, order)
        parent_zero_count = 0
        for basis in moving.BASES4:
            value = mp_determinant([
                [matrix[row][label - 1] for label in basis] for row in range(4)
            ])
            desired = 1 if base_brackets[basis] > 0 else -1
            signed = tuple(desired * coefficient for coefficient in mp_bernstein(value))
            if min(signed) < 0:
                raise AssertionError(f"tapered parent sign failed: {order}/{basis}")
            parent_zero_count += int(min(signed) == 0)
        zero_counts.append(parent_zero_count)
        coefficients = mp_circuit(
            mp_normals(matrix), joined.SIGNATURES[block], PERSISTENT_SUPPORTS[block]
        )
        common_sign = 1 if mp_at_origin(coefficients[0]) > 0 else -1
        if not all(
            min(common_sign * value for value in mp_bernstein(coefficient)) > 0
            for coefficient in coefficients
        ):
            raise AssertionError(f"tapered block circuit failed: {order}")
    if tuple(zero_counts) != EXPECTED_TAPERED_PARENT_ZERO_COUNTS:
        raise AssertionError(f"tapered parent zero census changed: {zero_counts}")
    return orders, tuple(zero_counts)


def verify_false_common_root():
    source, target, _direction = FALSE_COMMON_ROOT
    support = PERSISTENT_SUPPORTS[1]
    actual = tuple(
        (index, moving.transport_alpha(joined.SIGNATURES[1], index, source, target))
        for index in support
        if moving.replacement(index, source, target) is not None
    )
    if actual != FALSE_COMMON_ROOT_CONFLICT:
        raise AssertionError(f"false-common-root canary changed: {actual}")
    return actual


def file_sha256(path: Path) -> str:
    digest = sha256()
    with path.open("rb") as source:
        while block := source.read(1 << 20):
            digest.update(block)
    return digest.hexdigest()


def path_matrix(start, direction):
    """Matrix over Q[t], with t in [0,1] reaching the parent wall."""
    return [
        [
            (
                Fraction(int(start[row, column])),
                ENDPOINT * int(direction[row])
                if column == MOVING_COLUMN
                else Fraction(0),
            )
            for column in range(8)
        ]
        for row in range(4)
    ]


def bracket_polynomial(matrix, basis):
    return exact.poly_determinant(
        [[matrix[row][label - 1] for label in basis] for row in range(4)]
    )


def main():
    actual_sha = file_sha256(SOURCE)
    if actual_sha != SOURCE_SHA256:
        raise AssertionError(f"row2599 source SHA-256 changed: {actual_sha}")
    with np.load(SOURCE, allow_pickle=False) as source:
        if str(source["format"].item()) != "seeat-parent2599-upper-cover-v1":
            raise AssertionError("wrong row2599 source format")
        if int(source["parent_index"].item()) != 2599:
            raise AssertionError("wrong source parent index")
        charts = source["chart_matrix"]
        if charts.shape != (178, 4, 8):
            raise AssertionError("wrong row2599 chart bank shape")
        start = charts[START_CHART]
        target = charts[TARGET_CHART]

    direction = tuple(
        int(target[row, MOVING_COLUMN] - start[row, MOVING_COLUMN])
        for row in range(4)
    )
    if direction != EXPECTED_DIRECTION:
        raise AssertionError(f"common-ray direction changed: {direction}")

    matrix = path_matrix(start, direction)
    base_brackets = moving.parent_brackets(start)
    endpoint_walls = []
    for basis in moving.BASES4:
        polynomial = bracket_polynomial(matrix, basis)
        desired = 1 if base_brackets[basis] > 0 else -1
        coefficients = exact.bernstein_coefficients(polynomial)
        if all(desired * value > 0 for value in coefficients):
            continue
        if (
            all(desired * value >= 0 for value in coefficients)
            and exact.poly_eval(polynomial, 1) == 0
            and exact.poly_eval(polynomial, 0) != 0
        ):
            endpoint_walls.append(basis)
            continue
        raise AssertionError(f"parent residence failed at bracket {basis}")
    if endpoint_walls != [ENDPOINT_BRACKET]:
        raise AssertionError(f"wrong parent endpoint walls: {endpoint_walls}")

    normals = exact.derived_normal_polynomials(matrix)
    if tuple(joined.SIGNATURES) != (
        14_988_895_318_912,
        3_405_195_891_438_080,
        40_418_075_143_643_136,
    ):
        raise AssertionError("flow-triangle signatures changed")
    labels = tuple(
        tuple("".join(map(str, koszul.TRIPLES[index])) for index in support)
        for support in PERSISTENT_SUPPORTS
    )
    if labels != EXPECTED_SUPPORT_LABELS:
        raise AssertionError(f"persistent support labels changed: {labels}")

    coefficient_degrees = []
    for block, (signature, support) in enumerate(
        zip(joined.SIGNATURES, PERSISTENT_SUPPORTS, strict=True)
    ):
        coefficients = exact.five_circuit_cofactors(
            normals, signature, support
        )
        sign = 1 if exact.poly_eval(coefficients[0], 0) > 0 else -1
        if not all(
            all(sign * value > 0 for value in exact.bernstein_coefficients(poly))
            for poly in coefficients
        ):
            raise AssertionError(f"block {block} loses its strict circuit")
        exact.verify_polynomial_kernel(
            normals, signature, support, coefficients
        )
        coefficient_degrees.append(tuple(len(poly) - 1 for poly in coefficients))

    orders, tapered_zero_counts = verify_bounded_tapered_cubes(
        start, direction, base_brackets
    )
    false_common_root_conflict = verify_false_common_root()

    print("PASS pinned row2599 chart-zero common-ray source", actual_sha)
    print("PASS parent residence for 0<=t<1; unique endpoint [2467]")
    print("PASS strict persistent circuits", labels)
    print("PASS exact coefficient degrees", tuple(coefficient_degrees))
    print(
        "PASS six bounded tapered root-pair cubes: parent signs and fixed strict circuits",
        orders,
    )
    print("PASS tapered parent-boundary zero census", tapered_zero_counts)
    print(
        "PASS false common-root regression: block-1 transport alpha conflict",
        false_common_root_conflict,
    )
    print("ENDPOINT", ENDPOINT.numerator, ENDPOINT.denominator)
    print(
        "THEOREM the flow-triangle triple has a common proper bad-locus ray "
        "to parent boundary [2467]"
    )
    print(
        "SCOPE local H_c^0/component certificate only; no mixed d3 cell or "
        "comparison incidence; bounded tapered cubes do not certify the "
        "outer ordered-sector remainder or transported-witness face naturality"
    )


if __name__ == "__main__":
    main()
