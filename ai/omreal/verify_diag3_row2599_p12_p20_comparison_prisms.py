#!/usr/bin/env python3
"""Exact row-2599 comparison prisms for the p12 and p20 pair edges.

Each stored tapered pair sweep is homotoped to its two-stage certified parent-
wall collar.  The two exact bivariate patches retain both incident bad-block
circuits.  Taking the block-mass product gives a singular comparison
three-chain with two named singleton lateral disks.
"""

from __future__ import annotations

from fractions import Fraction
from hashlib import sha256
from pathlib import Path

import numpy as np

import verify_diag2_moving_witness_shear as moving
import verify_diag3_joined_flow_triangle as joined
import verify_diag3_row2599_common_proper_escape as common


SOURCE = Path(__file__).resolve().parent / "data/seeat_parent2599_upper178.npz"
SOURCE_SHA256 = "3b90799d26b7783e92c2ac697eaaf8b76d26a787f53205873b997657e114180a"
PATCH_COUNT = 2
PAIR_BLOCKS = {1: (1, 2), 2: (2, 0)}
SAFE_SUPPORTS = {
    0: (2, 19, 21, 37, 38),
    1: (2, 9, 27, 30, 35),
    2: (0, 11, 17, 24, 40),
}
PAIR_NAMES = {1: "p12", 2: "p20"}
EXPECTED_SEMANTIC = "48871bfbc021051f4f672eaf6372ecd5d1d0f0324005648b8d471e130b60e8f8"


def file_sha256(path):
    digest = sha256()
    with path.open("rb") as source:
        while block := source.read(1 << 20):
            digest.update(block)
    return digest.hexdigest()


def variable(axis=0):
    exponent = [0, 0, 0]
    exponent[axis] = 1
    return {tuple(exponent): Fraction(1)}


def restrict(polynomial, axis, value):
    answer = {}
    value = Fraction(value)
    for exponent, coefficient in polynomial.items():
        target = list(exponent)
        power = target[axis]
        target[axis] = 0
        target = tuple(target)
        answer[target] = answer.get(target, Fraction(0)) + coefficient * value**power
    return {key: coefficient for key, coefficient in answer.items() if coefficient}


def restrict_matrix(matrix, axis, value):
    return [[restrict(entry, axis, value) for entry in row] for row in matrix]


def matrix_equal(left, right):
    return all(left[row][column] == right[row][column] for row in range(4) for column in range(8))


def root_matrix(raw, root_index, common_parameter, root_parameter):
    matrix = [
        [common.mp_constant(int(raw[row, column])) for column in range(8)]
        for row in range(4)
    ]
    for row in range(4):
        matrix[row][common.MOVING_COLUMN] = common.mp_add(
            matrix[row][common.MOVING_COLUMN],
            common.mp_scale(
                common_parameter,
                common.ENDPOINT * common.EXPECTED_DIRECTION[row],
            ),
        )
    source, destination, sign = common.PAIR_ROOTS[root_index]
    for row in range(4):
        matrix[row][source - 1] = common.mp_add(
            matrix[row][source - 1],
            common.mp_scale(
                common.mp_multiply(root_parameter, matrix[row][destination - 1]),
                sign,
            ),
        )
    return matrix


def relative_stages(raw, root_index):
    u = variable()
    endpoint = common.ROOT_ENDPOINTS[root_index]
    stage0 = root_matrix(raw, root_index, u, common.mp_constant(endpoint))
    stage1 = root_matrix(
        raw,
        root_index,
        common.mp_constant(1),
        common.mp_scale(
            common.mp_add(common.mp_constant(1), common.mp_scale(u, -1)),
            endpoint,
        ),
    )
    if not matrix_equal(restrict_matrix(stage0, 0, 1), restrict_matrix(stage1, 0, 0)):
        raise AssertionError(f"{PAIR_NAMES[root_index]} relative collar seam changed")
    return stage0, stage1


def original_segment(raw, root_index, index):
    u = variable()
    parameter = common.mp_add(
        common.mp_constant(Fraction(index, PATCH_COUNT)),
        common.mp_scale(u, Fraction(1, PATCH_COUNT)),
    )
    endpoint = common.ROOT_ENDPOINTS[root_index]
    root_parameter = common.mp_scale(
        common.mp_add(common.mp_constant(1), common.mp_scale(parameter, -1)),
        endpoint,
    )
    return root_matrix(raw, root_index, parameter, root_parameter)


def interpolate(original, relative):
    v = variable(1)
    return [[
        common.mp_add(
            original[row][column],
            common.mp_multiply(
                v,
                common.mp_add(relative[row][column], common.mp_scale(original[row][column], -1)),
            ),
        )
        for column in range(8)
    ] for row in range(4)]


def determinant(matrix, basis):
    return common.mp_determinant(
        [[matrix[row][label - 1] for label in basis] for row in range(4)]
    )


def circuit(matrix, block):
    return common.mp_circuit(
        common.mp_normals(matrix), joined.SIGNATURES[block], SAFE_SUPPORTS[block]
    )


def certify_patch(name, matrix, blocks, base_brackets, semantic):
    weak_parent = []
    for basis in moving.BASES4:
        label = "".join(map(str, basis))
        polynomial = determinant(matrix, basis)
        signed = common.mp_scale(polynomial, 1 if base_brackets[basis] > 0 else -1)
        values = common.mp_bernstein(signed)
        if min(values) < 0:
            raise AssertionError(f"{name}: parent sign failed at [{label}]")
        if min(values) == 0:
            weak_parent.append(label)
        semantic.update(repr((name, "P", label, tuple(sorted(signed.items())))).encode("ascii"))
    weak_circuit = []
    for block in blocks:
        coefficients = circuit(matrix, block)
        sign = 1 if common.mp_at_origin(coefficients[0]) > 0 else -1
        strict = 0
        normals = common.mp_normals(matrix)
        for position, polynomial in enumerate(coefficients):
            signed = common.mp_scale(polynomial, sign)
            values = common.mp_bernstein(signed)
            if min(values) < 0:
                raise AssertionError(f"{name}: block {block} circuit changed sign")
            if min(values) == 0:
                weak_circuit.append((block, position))
            else:
                strict += 1
            semantic.update(repr((name, "C", block, position, tuple(sorted(signed.items())))).encode("ascii"))
        if not strict:
            raise AssertionError(f"{name}: block {block} circuit could vanish")
        for coordinate in range(4):
            total = {}
            for factor_index, coefficient in zip(SAFE_SUPPORTS[block], coefficients, strict=True):
                total = common.mp_add(
                    total,
                    common.mp_scale(
                        common.mp_multiply(coefficient, normals[factor_index][coordinate]),
                        moving.signature_sign(joined.SIGNATURES[block], factor_index),
                    ),
                )
            if total:
                raise AssertionError(f"{name}: block {block} cofactor kernel failed")
    return name, tuple(weak_parent), tuple(weak_circuit)


def certify_prism(raw, root_index, base_brackets, semantic):
    name = PAIR_NAMES[root_index]
    blocks = PAIR_BLOCKS[root_index]
    relatives = relative_stages(raw, root_index)
    originals = tuple(original_segment(raw, root_index, index) for index in range(PATCH_COUNT))
    patches = tuple(interpolate(left, right) for left, right in zip(originals, relatives, strict=True))
    if not matrix_equal(restrict_matrix(patches[0], 0, 1), restrict_matrix(patches[1], 0, 0)):
        raise AssertionError(f"{name}: comparison seam changed")
    for patch, original in zip(patches, originals, strict=True):
        if not matrix_equal(restrict_matrix(patch, 1, 0), original):
            raise AssertionError(f"{name}: v=0 left stored pair sweep")
    for u_value, patch in ((0, patches[0]), (1, patches[-1])):
        face = restrict_matrix(patch, 0, u_value)
        if not matrix_equal(restrict_matrix(face, 1, 0), restrict_matrix(face, 1, 1)):
            raise AssertionError(f"{name}: endpoint face did not collapse")
    relative_walls = []
    for patch in patches:
        face = restrict_matrix(patch, 1, 1)
        walls = tuple(
            "".join(map(str, basis)) for basis in moving.BASES4
            if not determinant(face, basis)
        )
        if not walls:
            raise AssertionError(f"{name}: relative face lost its parent wall")
        relative_walls.append(walls)
    reports = tuple(
        certify_patch(f"{name}-patch-{index}", patch, blocks, base_brackets, semantic)
        for index, patch in enumerate(patches)
    )
    ordinary = {
        f"K({name})": 1,
        f"Q({name},block{blocks[0]})": -1,
        f"Q({name},block{blocks[1]})": 1,
    }
    return {
        "pair": name,
        "blocks": blocks,
        "reports": reports,
        "relative_walls": tuple(relative_walls),
        "ordinary_boundary": ordinary,
    }


def main():
    if file_sha256(SOURCE) != SOURCE_SHA256:
        raise AssertionError("row2599 source SHA changed")
    with np.load(SOURCE, allow_pickle=False) as source:
        raw = source["chart_matrix"][0]
    base_brackets = moving.parent_brackets(raw)
    semantic = sha256(b"diag3-row2599-p12-p20-comparison-prisms-v1\0")
    reports = tuple(
        certify_prism(raw, root_index, base_brackets, semantic)
        for root_index in (1, 2)
    )
    semantic.update(repr(reports).encode("ascii"))
    digest = semantic.hexdigest()
    if EXPECTED_SEMANTIC != "TO_BE_PINNED" and digest != EXPECTED_SEMANTIC:
        raise AssertionError(f"p12/p20 comparison semantic changed: {digest}")
    print("PASS exact p12/p20 comparison prisms", reports)
    print("SEMANTIC", digest)
    print("THEOREM three pair-edge comparison prisms are now certified at row2599")
    print("OPEN singleton lateral gluing, H0/H1/H2 prisms, mixed J, global cover")
    print("SCOPE two local singular comparison chains; no d3 or ledger change")


if __name__ == "__main__":
    main()
