#!/usr/bin/env python3
"""Independent exact replay of the row-2599 H2 comparison prism."""

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
ROOTS = ((2, 8, -1), (1, 2, -1), (1, 3, 1))
ENDPOINTS = (
    Fraction(1_221_971_981, 1_769_366_234),
    Fraction(42_214_994, 2_183_619_501),
    Fraction(425_791_163, 1_286_992_887),
)
SUPPORT = (0, 11, 17, 24, 40)
EXPECTED_SEMANTIC = "55539702e53abdcf15a1173a549699d87427f85881d66db881ff33c98586934b"


def clean(polynomial):
    return {key: Fraction(value) for key, value in polynomial.items() if value}


def constant(value):
    value = Fraction(value)
    return {(0, 0, 0): value} if value else {}


def variable(axis):
    key = [0, 0, 0]
    key[axis] = 1
    return {tuple(key): Fraction(1)}


U, R, V = variable(0), variable(1), variable(2)


def add(left, right):
    answer = dict(left)
    for key, value in right.items():
        answer[key] = answer.get(key, Fraction(0)) + value
    return clean(answer)


def scale(polynomial, scalar):
    return clean({key: Fraction(scalar) * value for key, value in polynomial.items()})


def multiply(left, right):
    answer = {}
    for first, x in left.items():
        for second, y in right.items():
            key = tuple(a + b for a, b in zip(first, second, strict=True))
            answer[key] = answer.get(key, Fraction(0)) + x * y
    return clean(answer)


def restrict(polynomial, axis, value):
    answer = {}
    for exponent, coefficient in polynomial.items():
        target = list(exponent)
        power = target[axis]
        target[axis] = 0
        target = tuple(target)
        answer[target] = answer.get(target, Fraction(0)) + coefficient * Fraction(value) ** power
    return clean(answer)


def bernstein(polynomial):
    degrees = tuple(max((key[axis] for key in polynomial), default=0) for axis in range(3))
    answer = []
    for i in range(degrees[0] + 1):
        for j in range(degrees[1] + 1):
            for k in range(degrees[2] + 1):
                target = (i, j, k)
                value = Fraction(0)
                for exponent, coefficient in polynomial.items():
                    if all(exponent[axis] <= target[axis] for axis in range(3)):
                        value += coefficient * Fraction(comb(i, exponent[0]), comb(degrees[0], exponent[0])) * Fraction(comb(j, exponent[1]), comb(degrees[1], exponent[1])) * Fraction(comb(k, exponent[2]), comb(degrees[2], exponent[2]))
                answer.append(value)
    return tuple(answer)


def evaluate(polynomial, point):
    return sum(
        coefficient * point[0] ** exponent[0] * point[1] ** exponent[1] * point[2] ** exponent[2]
        for exponent, coefficient in polynomial.items()
    )


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
    return determinant([[matrix[row][label - 1] for label in basis] for row in range(4)])


def base_matrix(raw):
    return [[constant(int(raw[row, column])) for column in range(8)] for row in range(4)]


def common_move(matrix, parameter):
    for row in range(4):
        matrix[row][COMMON_COLUMN] = add(
            matrix[row][COMMON_COLUMN],
            scale(parameter, COMMON_ENDPOINT * COMMON_DIRECTION[row]),
        )


def apply_root(matrix, root_index, parameter):
    source, destination, sign = ROOTS[root_index]
    for row in range(4):
        matrix[row][source - 1] = add(
            matrix[row][source - 1],
            scale(multiply(parameter, matrix[row][destination - 1]), sign),
        )


def two_root_matrix(raw, common_parameter, first, second):
    matrix = base_matrix(raw)
    common_move(matrix, common_parameter)
    apply_root(matrix, 1, first)
    apply_root(matrix, 2, second)
    return matrix


def single_root_matrix(raw, root_index, common_parameter, root_parameter):
    matrix = base_matrix(raw)
    common_move(matrix, common_parameter)
    apply_root(matrix, root_index, root_parameter)
    return matrix


def root_values(edge):
    if edge == 0:
        return constant(ENDPOINTS[1]), scale(R, ENDPOINTS[2])
    return scale(add(constant(1), scale(R, -1)), ENDPOINTS[1]), constant(ENDPOINTS[2])


def relative(raw, edge, stage):
    first, second = root_values(edge)
    if stage == 0:
        return two_root_matrix(raw, U, first, second)
    taper = add(constant(1), scale(U, -1))
    return two_root_matrix(raw, constant(1), multiply(taper, first), multiply(taper, second))


def original(raw, edge, stage):
    parameter = add(constant(Fraction(stage, 2)), scale(U, Fraction(1, 2)))
    taper = add(constant(1), scale(parameter, -1))
    first, second = root_values(edge)
    return two_root_matrix(raw, parameter, multiply(taper, first), multiply(taper, second))


def interpolate(left, right):
    return [[
        add(left[row][column], multiply(V, add(right[row][column], scale(left[row][column], -1))))
        for column in range(8)
    ] for row in range(4)]


def pair_patch(raw, root_index, stage):
    endpoint = ENDPOINTS[root_index]
    source_parameter = add(constant(Fraction(stage, 2)), scale(U, Fraction(1, 2)))
    source = single_root_matrix(
        raw,
        root_index,
        source_parameter,
        scale(add(constant(1), scale(source_parameter, -1)), endpoint),
    )
    if stage == 0:
        target = single_root_matrix(raw, root_index, U, constant(endpoint))
    else:
        target = single_root_matrix(
            raw,
            root_index,
            constant(1),
            scale(add(constant(1), scale(U, -1)), endpoint),
        )
    return interpolate(source, target)


def matrix_restrict(matrix, axis, value):
    return [[restrict(entry, axis, value) for entry in row] for row in matrix]


def matrix_equal(left, right):
    return all(left[row][column] == right[row][column] for row in range(4) for column in range(8))


def reaxis_r_face(matrix):
    return [[
        {(iu, iv, 0): coefficient for (iu, zero, iv), coefficient in entry.items() if not zero}
        for entry in row
    ] for row in matrix]


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


def circuit(matrix):
    all_normals = normals(matrix)
    columns = tuple(
        tuple(
            scale(value, moving.signature_sign(joined.SIGNATURES[2], index))
            for value in all_normals[index]
        )
        for index in SUPPORT
    )
    coefficients = []
    for omitted in range(5):
        retained = [column for position, column in enumerate(columns) if position != omitted]
        value = determinant([[retained[column][row] for column in range(4)] for row in range(4)])
        coefficients.append(value if not omitted & 1 else scale(value, -1))
    anchor = next(evaluate(item, (Fraction(1, 2),) * 3) for item in coefficients if evaluate(item, (Fraction(1, 2),) * 3))
    sign = 1 if anchor > 0 else -1
    coefficients = tuple(scale(item, sign) for item in coefficients)
    for coordinate in range(4):
        total = {}
        for index, coefficient in zip(SUPPORT, coefficients, strict=True):
            total = add(
                total,
                scale(
                    multiply(coefficient, all_normals[index][coordinate]),
                    moving.signature_sign(joined.SIGNATURES[2], index),
                ),
            )
        if total:
            raise AssertionError("independent H2 cofactor kernel failed")
    return coefficients


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
    strict = 0
    for position, polynomial in enumerate(circuit(matrix)):
        values = bernstein(polynomial)
        if min(values) < 0:
            raise AssertionError(f"{name}: independent block-2 circuit sign failure")
        if min(values) == 0:
            weak_circuit.append(position)
        else:
            strict += 1
        digest.update(repr((name, "C", position, tuple(sorted(polynomial.items())))).encode("ascii"))
    if not strict:
        raise AssertionError(f"{name}: independent circuit could vanish")
    return name, tuple(weak_parent), tuple(weak_circuit)


def main():
    if sha256(SOURCE.read_bytes()).hexdigest() != SOURCE_SHA256:
        raise AssertionError("row2599 source SHA changed")
    with np.load(SOURCE, allow_pickle=False) as source:
        raw = source["chart_matrix"][0]
    base_brackets = moving.parent_brackets(raw)
    patches = tuple(
        tuple(interpolate(original(raw, edge, stage), relative(raw, edge, stage)) for stage in range(2))
        for edge in range(2)
    )
    for edge in range(2):
        if not matrix_equal(matrix_restrict(patches[edge][0], 0, 1), matrix_restrict(patches[edge][1], 0, 0)):
            raise AssertionError("independent H2 u seam changed")
    for stage in range(2):
        if not matrix_equal(matrix_restrict(patches[0][stage], 1, 1), matrix_restrict(patches[1][stage], 1, 0)):
            raise AssertionError("independent H2 frontier seam changed")
        if not matrix_equal(matrix_restrict(patches[0][stage], 1, 0), pair_patch(raw, 1, stage)):
            raise AssertionError("independent H2/p12 lateral mismatch")
        if not matrix_equal(matrix_restrict(patches[1][stage], 1, 1), pair_patch(raw, 2, stage)):
            raise AssertionError("independent H2/p20 lateral mismatch")
    relative_walls = []
    for edge in range(2):
        for stage in range(2):
            face = matrix_restrict(patches[edge][stage], 2, 1)
            walls = tuple("".join(map(str, basis)) for basis in moving.BASES4 if not bracket(face, basis))
            if not walls:
                raise AssertionError("independent H2 relative face lost its wall")
            relative_walls.append((edge, stage, walls))
        source_face = matrix_restrict(patches[edge][0], 0, 0)
        if not matrix_equal(matrix_restrict(source_face, 2, 0), matrix_restrict(source_face, 2, 1)):
            raise AssertionError("independent H2 source face did not collapse")
        if not any(not bracket(source_face, basis) for basis in moving.BASES4):
            raise AssertionError("independent H2 source face is not relative")
        apex_face = matrix_restrict(patches[edge][1], 0, 1)
        if not matrix_equal(matrix_restrict(apex_face, 2, 0), matrix_restrict(apex_face, 2, 1)):
            raise AssertionError("independent H2 apex face did not collapse")
    digest = sha256(b"diag3-hostile-independent-h2-comparison-prism-v1\0")
    reports = tuple(
        certify(f"h2-edge-{edge}-patch-{stage}", patches[edge][stage], base_brackets, digest)
        for edge in range(2) for stage in range(2)
    )
    boundary = {"K(h2)": 1, "Q(p12,block2)": -1, "Q(p20,block2)": 1}
    digest.update(repr((reports, tuple(relative_walls), boundary)).encode("ascii"))
    semantic = digest.hexdigest()
    if EXPECTED_SEMANTIC != "TO_BE_PINNED" and semantic != EXPECTED_SEMANTIC:
        raise AssertionError(f"independent H2 semantic changed: {semantic}")
    print("PASS independent H2 comparison prism", reports)
    print("PASS independent literal pair laterals and boundary", boundary)
    print("SEMANTIC", semantic)
    print("SCOPE comparison count 4/6; H0/H1 and mixed J remain open")


if __name__ == "__main__":
    main()
