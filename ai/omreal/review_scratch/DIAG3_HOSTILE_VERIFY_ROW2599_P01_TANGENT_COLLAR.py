#!/usr/bin/env python3
"""Independent dense-polynomial replay of the row-2599 p01 tangent collar.

This checker deliberately does not import the production collar verifier or
its sparse polynomial arithmetic.  It reconstructs the four pieces using
dense univariate rational polynomials, replays all parent determinants and
both Gordan cofactor kernels, and checks the two projective-gauge seams.
"""

from __future__ import annotations

from fractions import Fraction
from hashlib import sha256
from math import comb
from pathlib import Path
import sys

import numpy as np


HERE = Path(__file__).resolve().parent
OMREAL = HERE.parent
sys.path.insert(0, str(OMREAL))

import verify_diag2_moving_witness_shear as moving  # noqa: E402
import verify_diag3_joined_flow_triangle as joined  # noqa: E402


SOURCE = OMREAL / "data/seeat_parent2599_upper178.npz"
SOURCE_SHA256 = "3b90799d26b7783e92c2ac697eaaf8b76d26a787f53205873b997657e114180a"
COMMON_ENDPOINT = Fraction(23_597_311, 105_015_122)
COMMON_DIRECTION = (81, -262, 91, 86)
COMMON_COLUMN = 6
ROOT_ENDPOINT = Fraction(1_221_971_981, 1_769_366_234)
WITNESS_WALL = Fraction(
    83_503_134_767_238_851_186_305_349_765_512_866,
    43_552_580_189_648_394_406_194_000_441_042_241,
)
ADVANCE = Fraction(9, 160)
OFFPLANE = Fraction(
    3_358_010_538_087_089_065_822_291_885_427_450_701_681_795,
    3_308_387_436_982_263_269_937_203_185_897_076_819_775_106,
)
ROOT_TARGET = Fraction(
    234_256_547_531_343_777_781_047_691_330_195_444_590_421_787_902_374_123_738_445_539_062_790_489_112_404_622_131_159,
    13_372_644_039_892_933_623_810_456_407_340_392_486_129_320_262_099_558_845_715_262_274_062_239_731_375_045_118_995_681,
)
SUPPORTS = {
    0: (2, 19, 21, 37, 38),
    1: (2, 9, 27, 30, 35),
}
EXPECTED_SEMANTIC = "82dda129bef8f52ce4c41fbc8b31e9a316419953bb89a9eaaf8983f9ab1379f8"


def trim(polynomial):
    answer = list(map(Fraction, polynomial))
    while len(answer) > 1 and answer[-1] == 0:
        answer.pop()
    return tuple(answer)


def constant(value):
    return (Fraction(value),)


def add(left, right):
    size = max(len(left), len(right))
    return trim(tuple(
        (left[index] if index < len(left) else 0)
        + (right[index] if index < len(right) else 0)
        for index in range(size)
    ))


def scale(polynomial, scalar):
    return trim(tuple(Fraction(scalar) * value for value in polynomial))


def multiply(left, right):
    answer = [Fraction(0)] * (len(left) + len(right) - 1)
    for first, x in enumerate(left):
        for second, y in enumerate(right):
            answer[first + second] += x * y
    return trim(answer)


def evaluate(polynomial, value):
    answer = Fraction(0)
    for coefficient in reversed(polynomial):
        answer = answer * Fraction(value) + coefficient
    return answer


def bernstein(polynomial):
    degree = len(polynomial) - 1
    return tuple(
        sum(
            polynomial[index] * Fraction(comb(position, index), comb(degree, index))
            for index in range(position + 1)
        )
        for position in range(degree + 1)
    )


def determinant(matrix):
    if not matrix:
        return constant(1)
    answer = constant(0)
    for column, entry in enumerate(matrix[0]):
        minor = [row[:column] + row[column + 1 :] for row in matrix[1:]]
        term = multiply(entry, determinant(minor))
        answer = add(answer, term if not column & 1 else scale(term, -1))
    return answer


def bracket(matrix, basis):
    return determinant(
        [[matrix[row][label - 1] for label in basis] for row in range(4)]
    )


def base_matrix(raw):
    return [[constant(int(raw[row, column])) for column in range(8)] for row in range(4)]


def root_matrix(raw, common_parameter, root_parameter, offplane=constant(0)):
    matrix = base_matrix(raw)
    for row in range(4):
        matrix[row][COMMON_COLUMN] = add(
            matrix[row][COMMON_COLUMN],
            scale(common_parameter, COMMON_ENDPOINT * COMMON_DIRECTION[row]),
        )
        # Root d01=(2 -> 8,-), using one-based labels.
        matrix[row][1] = add(
            matrix[row][1], scale(multiply(root_parameter, matrix[row][7]), -1)
        )
    matrix[0][5] = add(matrix[0][5], offplane)
    return matrix


def normals(matrix):
    answer = []
    for triple in moving.TRIPLES:
        columns = [[matrix[row][label - 1] for label in triple] for row in range(4)]
        answer.append(tuple(
            scale(
                determinant([row for index, row in enumerate(columns) if index != omitted]),
                (-1) ** (omitted + 5),
            )
            for omitted in range(4)
        ))
    return tuple(answer)


def circuit(matrix, block):
    all_normals = normals(matrix)
    signed_columns = tuple(
        tuple(
            scale(value, moving.signature_sign(joined.SIGNATURES[block], index))
            for value in all_normals[index]
        )
        for index in SUPPORTS[block]
    )
    coefficients = []
    for omitted in range(5):
        retained = [
            column for position, column in enumerate(signed_columns)
            if position != omitted
        ]
        value = determinant([
            [retained[column][row] for column in range(4)] for row in range(4)
        ])
        coefficients.append(value if not omitted & 1 else scale(value, -1))
    anchor = next(item[0] for item in coefficients if item[0])
    sign = 1 if anchor > 0 else -1
    coefficients = tuple(scale(item, sign) for item in coefficients)
    for coordinate in range(4):
        total = constant(0)
        for index, coefficient in zip(SUPPORTS[block], coefficients, strict=True):
            total = add(
                total,
                scale(
                    multiply(coefficient, all_normals[index][coordinate]),
                    moving.signature_sign(joined.SIGNATURES[block], index),
                ),
            )
        if trim(total) != constant(0):
            raise AssertionError(f"block {block}: dense cofactor kernel failed")
    return coefficients


def point(matrix, value):
    return [[constant(evaluate(entry, value)) for entry in row] for row in matrix]


def exact_matrix_equal(left, right):
    return all(
        left[row][column] == right[row][column]
        for row in range(4) for column in range(8)
    )


def certify_segment(name, matrix, base_brackets, expected_weak, expected_zero, expected_circuit_weak, digest):
    weak, identically_zero = [], []
    for basis in moving.BASES4:
        label = "".join(map(str, basis))
        polynomial = bracket(matrix, basis)
        signed = scale(polynomial, 1 if base_brackets[basis] > 0 else -1)
        if min(bernstein(signed)) < 0:
            raise AssertionError(f"{name}: dense parent sign failure [{label}]")
        if min(bernstein(signed)) == 0:
            weak.append(label)
        if signed == constant(0):
            identically_zero.append(label)
        digest.update(repr((name, "P", label, signed)).encode("ascii"))
    if tuple(weak) != expected_weak or tuple(identically_zero) != expected_zero:
        raise AssertionError(f"{name}: dense wall census changed")
    circuit_weak = []
    for block in (0, 1):
        for position, polynomial in enumerate(circuit(matrix, block)):
            if min(bernstein(polynomial)) < 0:
                raise AssertionError(f"{name}: dense circuit sign failure")
            if min(bernstein(polynomial)) == 0:
                circuit_weak.append((block, position))
            digest.update(repr((name, "C", block, position, polynomial)).encode("ascii"))
    if tuple(circuit_weak) != expected_circuit_weak:
        raise AssertionError(f"{name}: dense circuit wall census changed")
    return name, tuple(weak), tuple(identically_zero), tuple(circuit_weak)


def gauge_equal(left, right, scale_value):
    if scale_value <= 0:
        raise AssertionError("dense gauge is not positive")
    for row in range(4):
        for column in range(8):
            expected = scale(left[row][column], scale_value) if column == 1 else left[row][column]
            if right[row][column] != expected:
                raise AssertionError("dense projective-gauge seam changed")


def main():
    actual_sha = sha256(SOURCE.read_bytes()).hexdigest()
    if actual_sha != SOURCE_SHA256:
        raise AssertionError(f"row2599 source SHA changed: {actual_sha}")
    with np.load(SOURCE, allow_pickle=False) as source:
        raw = source["chart_matrix"][0]
    base_brackets = moving.parent_brackets(raw)
    t = (Fraction(0), Fraction(1))

    stage0 = root_matrix(raw, scale(t, WITNESS_WALL), constant(ROOT_ENDPOINT))
    endpoint_a = WITNESS_WALL + ADVANCE
    stage1 = root_matrix(
        raw,
        add(constant(WITNESS_WALL), scale(t, ADVANCE)),
        constant(ROOT_ENDPOINT),
        scale(t, OFFPLANE),
    )
    if evaluate(bracket(stage1, (1, 3, 6, 7)), 1):
        raise AssertionError("independent off-plane endpoint left [1367]")

    stage2 = root_matrix(
        raw,
        constant(endpoint_a),
        add(constant(ROOT_ENDPOINT), scale(t, ROOT_TARGET - ROOT_ENDPOINT)),
        constant(OFFPLANE),
    )
    if evaluate(bracket(stage2, (2, 4, 6, 7)), 1):
        raise AssertionError("independent root endpoint left [2467]")

    final_a = add(constant(endpoint_a), scale(t, 1 - endpoint_a))
    final_b = add(constant(OFFPLANE), scale(t, -OFFPLANE))
    root_zero = root_matrix(raw, final_a, constant(0), final_b)
    root_one = root_matrix(raw, final_a, constant(1), final_b)
    numerator_at_zero = bracket(root_zero, (2, 4, 6, 7))
    root_coefficient = add(
        bracket(root_one, (2, 4, 6, 7)), scale(numerator_at_zero, -1)
    )
    denominator = root_coefficient
    numerator = scale(numerator_at_zero, -1)
    if min(bernstein(denominator)) <= 0:
        denominator, numerator = scale(denominator, -1), scale(numerator, -1)
    if min(bernstein(denominator)) <= 0:
        raise AssertionError("independent graph denominator is not positive")
    if numerator[0] / denominator[0] != ROOT_TARGET or evaluate(numerator, 1):
        raise AssertionError("independent [2467] rational graph endpoint changed")
    stage3 = [[entry for entry in row] for row in root_zero]
    for row in range(4):
        stage3[row][1] = add(
            multiply(denominator, root_zero[row][1]),
            scale(multiply(numerator, root_zero[row][7]), -1),
        )

    digest = sha256(b"diag3-hostile-dense-p01-tangent-collar-v1\0")
    reports = (
        certify_segment("source-to-witness", stage0, base_brackets, ("1234",), ("1234",), ((0, 0),), digest),
        certify_segment("off-plane-to-1367", stage1, base_brackets, ("1234", "1367"), ("1234",), ((0, 0),), digest),
        certify_segment("1367-to-2467", stage2, base_brackets, ("1234", "1367", "2467"), ("1367",), (), digest),
        certify_segment("2467-graph-to-common-apex", stage3, base_brackets, ("1367", "2467"), ("2467",), (), digest),
    )
    if not exact_matrix_equal(point(stage0, 1), point(stage1, 0)):
        raise AssertionError("dense first seam changed")
    if not exact_matrix_equal(point(stage1, 1), point(stage2, 0)):
        raise AssertionError("dense second seam changed")
    gauge_equal(point(stage2, 1), point(stage3, 0), denominator[0])
    apex = root_matrix(raw, constant(1), constant(0))
    gauge_equal(apex, point(stage3, 1), evaluate(denominator, 1))

    first = circuit(stage1, 0)[0]
    if len(first) < 2 or first[1] <= 0:
        raise AssertionError("independent tangent derivative is not positive")
    digest.update(repr((reports, denominator, first[1])).encode("ascii"))
    semantic = digest.hexdigest()
    if EXPECTED_SEMANTIC != "TO_BE_PINNED" and semantic != EXPECTED_SEMANTIC:
        raise AssertionError(f"hostile dense semantic changed: {semantic}")
    print("PASS independent dense p01 tangent collar", reports)
    print("PASS independent positive denominator/gauge seams", bernstein(denominator))
    print("SEMANTIC", semantic)
    print("SCOPE independent collar replay only; separate p01 prism still does not close d3")


if __name__ == "__main__":
    main()
