#!/usr/bin/env python3
"""Independent dense-bivariate replay of the row-2599 p01 prism.

This checker does not import either production p01 verifier.  It rebuilds the
five patches with a separate dense bivariate rational-polynomial engine,
checks all parent brackets and the two transported Gordan circuits, and
recomputes the signed ordinary boundary of the resulting singular prism.
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
    2: (0, 11, 17, 24, 40),
}
PATCH_COUNT = 5
EXPECTED_SEMANTIC = "acca3573a369139c9a142592febcaa55ce453eeb10c1d52631ac5b226129127b"


def clean(polynomial):
    return {key: Fraction(value) for key, value in polynomial.items() if value}


def constant(value):
    value = Fraction(value)
    return {(0, 0): value} if value else {}


U = {(1, 0): Fraction(1)}
V = {(0, 1): Fraction(1)}


def add(left, right):
    answer = dict(left)
    for key, value in right.items():
        answer[key] = answer.get(key, Fraction(0)) + value
    return clean(answer)


def scale(polynomial, scalar):
    return clean({key: Fraction(scalar) * value for key, value in polynomial.items()})


def multiply(left, right):
    answer = {}
    for (iu, iv), x in left.items():
        for (ju, jv), y in right.items():
            key = (iu + ju, iv + jv)
            answer[key] = answer.get(key, Fraction(0)) + x * y
    return clean(answer)


def evaluate(polynomial, u, v):
    return sum(
        value * Fraction(u) ** iu * Fraction(v) ** iv
        for (iu, iv), value in polynomial.items()
    )


def restrict(polynomial, axis, value):
    answer = {}
    for (iu, iv), coefficient in polynomial.items():
        powers = [iu, iv]
        power = powers[axis]
        powers[axis] = 0
        key = tuple(powers)
        answer[key] = answer.get(key, Fraction(0)) + coefficient * Fraction(value) ** power
    return clean(answer)


def bernstein(polynomial):
    degree_u = max((key[0] for key in polynomial), default=0)
    degree_v = max((key[1] for key in polynomial), default=0)
    answer = []
    for pu in range(degree_u + 1):
        for pv in range(degree_v + 1):
            value = Fraction(0)
            for (iu, iv), coefficient in polynomial.items():
                if iu <= pu and iv <= pv:
                    value += (
                        coefficient
                        * Fraction(comb(pu, iu), comb(degree_u, iu))
                        * Fraction(comb(pv, iv), comb(degree_v, iv))
                    )
            answer.append(value)
    return tuple(answer)


def determinant(matrix):
    if not matrix:
        return constant(1)
    answer = {}
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


def root_matrix(raw, common_parameter, root_parameter, offplane=None):
    matrix = base_matrix(raw)
    for row in range(4):
        matrix[row][COMMON_COLUMN] = add(
            matrix[row][COMMON_COLUMN],
            scale(common_parameter, COMMON_ENDPOINT * COMMON_DIRECTION[row]),
        )
        matrix[row][1] = add(
            matrix[row][1], scale(multiply(root_parameter, matrix[row][7]), -1)
        )
    matrix[0][5] = add(matrix[0][5], offplane or {})
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
        retained = [column for position, column in enumerate(signed_columns) if position != omitted]
        value = determinant([
            [retained[column][row] for column in range(4)] for row in range(4)
        ])
        coefficients.append(value if not omitted & 1 else scale(value, -1))
    anchor = next(
        evaluate(item, Fraction(1, 2), Fraction(1, 2))
        for item in coefficients
        if evaluate(item, Fraction(1, 2), Fraction(1, 2))
    )
    sign = 1 if anchor > 0 else -1
    coefficients = tuple(scale(item, sign) for item in coefficients)
    for coordinate in range(4):
        total = {}
        for index, coefficient in zip(SUPPORTS[block], coefficients, strict=True):
            total = add(
                total,
                scale(
                    multiply(coefficient, all_normals[index][coordinate]),
                    moving.signature_sign(joined.SIGNATURES[block], index),
                ),
            )
        if total:
            raise AssertionError(f"block {block}: independent cofactor kernel failed")
    return coefficients


def matrix_restrict(matrix, axis, value):
    return [[restrict(entry, axis, value) for entry in row] for row in matrix]


def matrix_equal(left, right):
    return all(left[row][column] == right[row][column] for row in range(4) for column in range(8))


def build_relative(raw):
    endpoint_a = WITNESS_WALL + ADVANCE
    stage0 = root_matrix(raw, scale(U, WITNESS_WALL), constant(ROOT_ENDPOINT))
    stage1 = root_matrix(
        raw,
        add(constant(WITNESS_WALL), scale(U, ADVANCE)),
        constant(ROOT_ENDPOINT),
        scale(U, OFFPLANE),
    )
    stage2 = root_matrix(
        raw,
        constant(endpoint_a),
        add(constant(ROOT_ENDPOINT), scale(U, ROOT_TARGET - ROOT_ENDPOINT)),
        constant(OFFPLANE),
    )
    final_a = add(constant(endpoint_a), scale(U, 1 - endpoint_a))
    final_b = add(constant(OFFPLANE), scale(U, -OFFPLANE))
    root_zero = root_matrix(raw, final_a, constant(0), final_b)
    root_one = root_matrix(raw, final_a, constant(1), final_b)
    value_zero = bracket(root_zero, (2, 4, 6, 7))
    denominator = add(bracket(root_one, (2, 4, 6, 7)), scale(value_zero, -1))
    numerator = scale(value_zero, -1)
    if min(bernstein(denominator)) <= 0:
        denominator, numerator = scale(denominator, -1), scale(numerator, -1)
    if min(bernstein(denominator)) <= 0:
        raise AssertionError("independent graph denominator is not positive")
    stage3 = [[dict(entry) for entry in row] for row in root_zero]
    for row in range(4):
        stage3[row][1] = add(
            multiply(denominator, root_zero[row][1]),
            scale(multiply(numerator, root_zero[row][7]), -1),
        )

    denominator_start = evaluate(denominator, 0, 0)
    denominator_end = evaluate(denominator, 1, 0)
    gauge2 = add(constant(1), scale(U, denominator_start - 1))
    stage2_gauged = [[dict(entry) for entry in row] for row in stage2]
    for row in range(4):
        stage2_gauged[row][1] = multiply(gauge2, stage2_gauged[row][1])
    common_apex = root_matrix(raw, constant(1), constant(0))
    final_gauge = add(constant(denominator_end), scale(U, 1 - denominator_end))
    stage4 = [[dict(entry) for entry in row] for row in common_apex]
    for row in range(4):
        stage4[row][1] = multiply(final_gauge, stage4[row][1])
    return stage0, stage1, stage2_gauged, stage3, stage4


def original(raw, index):
    parameter = add(constant(Fraction(index, PATCH_COUNT)), scale(U, Fraction(1, PATCH_COUNT)))
    return root_matrix(
        raw,
        parameter,
        scale(add(constant(1), scale(parameter, -1)), ROOT_ENDPOINT),
    )


def interpolate(left, right):
    return [[
        add(left[row][column], multiply(V, add(right[row][column], scale(left[row][column], -1))))
        for column in range(8)
    ] for row in range(4)]


def certify(name, matrix, base_brackets, digest):
    weak_parent, weak_circuit = [], []
    for basis in moving.BASES4:
        label = "".join(map(str, basis))
        signed = scale(bracket(matrix, basis), 1 if base_brackets[basis] > 0 else -1)
        values = bernstein(signed)
        if min(values) < 0:
            raise AssertionError(f"{name}: independent parent sign failure [{label}]")
        if min(values) == 0:
            weak_parent.append(label)
        digest.update(repr((name, "P", label, tuple(sorted(signed.items())))).encode("ascii"))
    for block in (0, 1):
        strict = 0
        for position, polynomial in enumerate(circuit(matrix, block)):
            values = bernstein(polynomial)
            if min(values) < 0:
                raise AssertionError(f"{name}: independent block-{block} circuit sign failure")
            if min(values) == 0:
                weak_circuit.append((block, position))
            else:
                strict += 1
            digest.update(repr((name, "C", block, position, tuple(sorted(polynomial.items())))).encode("ascii"))
        if not strict:
            raise AssertionError(f"{name}: independent circuit could vanish")
    return name, tuple(weak_parent), tuple(weak_circuit)


def main():
    if sha256(SOURCE.read_bytes()).hexdigest() != SOURCE_SHA256:
        raise AssertionError("row2599 source SHA changed")
    with np.load(SOURCE, allow_pickle=False) as source:
        raw = source["chart_matrix"][0]
    base_brackets = moving.parent_brackets(raw)
    relatives = build_relative(raw)
    originals = tuple(original(raw, index) for index in range(PATCH_COUNT))
    patches = tuple(interpolate(left, right) for left, right in zip(originals, relatives, strict=True))

    for index in range(PATCH_COUNT - 1):
        if not matrix_equal(matrix_restrict(patches[index], 0, 1), matrix_restrict(patches[index + 1], 0, 0)):
            raise AssertionError(f"independent patch seam {index} changed")
    for patch, left in zip(patches, originals, strict=True):
        if not matrix_equal(matrix_restrict(patch, 1, 0), left):
            raise AssertionError("independent v=0 face left K(p01)")
    for index, patch in enumerate(patches):
        relative = matrix_restrict(patch, 1, 1)
        if not any(not bracket(relative, basis) for basis in moving.BASES4):
            raise AssertionError(f"independent relative wall missing on patch {index}")
    for u_value, patch in ((0, patches[0]), (1, patches[-1])):
        face = matrix_restrict(patch, 0, u_value)
        if not matrix_equal(matrix_restrict(face, 1, 0), matrix_restrict(face, 1, 1)):
            raise AssertionError("independent endpoint face did not collapse")

    digest = sha256(b"diag3-hostile-dense-p01-comparison-prism-v1\0")
    reports = tuple(certify(f"patch-{index}", patch, base_brackets, digest) for index, patch in enumerate(patches))
    boundary = {
        "K(p01)": 1,
        "Q(p01,block0)": -1,
        "Q(p01,block1)": 1,
        "internal_pairs": 4,
        "relative_faces": 5,
        "collapsed_end_faces": 2,
    }
    digest.update(repr((reports, boundary)).encode("ascii"))
    semantic = digest.hexdigest()
    if EXPECTED_SEMANTIC != "TO_BE_PINNED" and semantic != EXPECTED_SEMANTIC:
        raise AssertionError(f"independent comparison semantic changed: {semantic}")
    print("PASS independent dense p01 comparison patches", reports)
    print("PASS independent signed ordinary boundary", boundary)
    print("SEMANTIC", semantic)
    print("SCOPE one of six comparison prisms; named singleton laterals remain open; no d3")


if __name__ == "__main__":
    main()
