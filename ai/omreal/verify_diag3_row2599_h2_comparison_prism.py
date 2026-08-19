#!/usr/bin/env python3
"""Exact row-2599 H2 comparison prism joining the p12/p20 laterals."""

from __future__ import annotations

from fractions import Fraction
from hashlib import sha256

import numpy as np

import verify_diag2_moving_witness_shear as moving
import verify_diag3_joined_flow_triangle as joined
import verify_diag3_row2599_common_proper_escape as common
import verify_diag3_row2599_p12_p20_comparison_prisms as pairs


SOURCE = pairs.SOURCE
SOURCE_SHA256 = pairs.SOURCE_SHA256
ROOT1 = common.ROOT_ENDPOINTS[1]
ROOT2 = common.ROOT_ENDPOINTS[2]
SUPPORT = (0, 11, 17, 24, 40)
EXPECTED_SEMANTIC = "4027e41a519953200e205f4e7ab2453a83122822d6ca2ed60bb649cd60afc7a7"


def variable(axis):
    exponent = [0, 0, 0]
    exponent[axis] = 1
    return {tuple(exponent): Fraction(1)}


U, R, V = variable(0), variable(1), variable(2)


def root_values(edge):
    if edge == 0:
        return common.mp_constant(ROOT1), common.mp_scale(R, ROOT2)
    if edge == 1:
        return common.mp_scale(
            common.mp_add(common.mp_constant(1), common.mp_scale(R, -1)), ROOT1
        ), common.mp_constant(ROOT2)
    raise AssertionError(edge)


def two_root_matrix(raw, common_parameter, first_parameter, second_parameter):
    matrix = [
        [common.mp_constant(int(raw[row, column])) for column in range(8)]
        for row in range(4)
    ]
    for row in range(4):
        matrix[row][common.MOVING_COLUMN] = common.mp_add(
            matrix[row][common.MOVING_COLUMN],
            common.mp_scale(
                common_parameter, common.ENDPOINT * common.EXPECTED_DIRECTION[row]
            ),
        )
    for root_index, parameter in ((1, first_parameter), (2, second_parameter)):
        source, destination, sign = common.PAIR_ROOTS[root_index]
        for row in range(4):
            matrix[row][source - 1] = common.mp_add(
                matrix[row][source - 1],
                common.mp_scale(
                    common.mp_multiply(parameter, matrix[row][destination - 1]),
                    sign,
                ),
            )
    return matrix


def relative_stage(raw, edge, stage):
    first, second = root_values(edge)
    if stage == 0:
        return two_root_matrix(raw, U, first, second)
    taper = common.mp_add(common.mp_constant(1), common.mp_scale(U, -1))
    return two_root_matrix(
        raw,
        common.mp_constant(1),
        common.mp_multiply(taper, first),
        common.mp_multiply(taper, second),
    )


def original_stage(raw, edge, stage):
    common_parameter = common.mp_add(
        common.mp_constant(Fraction(stage, 2)), common.mp_scale(U, Fraction(1, 2))
    )
    taper = common.mp_add(
        common.mp_constant(1), common.mp_scale(common_parameter, -1)
    )
    first, second = root_values(edge)
    return two_root_matrix(
        raw,
        common_parameter,
        common.mp_multiply(taper, first),
        common.mp_multiply(taper, second),
    )


def interpolate(original, relative):
    return [[
        common.mp_add(
            original[row][column],
            common.mp_multiply(
                V,
                common.mp_add(relative[row][column], common.mp_scale(original[row][column], -1)),
            ),
        )
        for column in range(8)
    ] for row in range(4)]


def restrict(polynomial, axis, value):
    answer = {}
    for exponent, coefficient in polynomial.items():
        target = list(exponent)
        power = target[axis]
        target[axis] = 0
        target = tuple(target)
        answer[target] = answer.get(target, Fraction(0)) + coefficient * Fraction(value) ** power
    return {key: coefficient for key, coefficient in answer.items() if coefficient}


def restrict_matrix(matrix, axis, value):
    return [[restrict(entry, axis, value) for entry in row] for row in matrix]


def reaxis_r_face(matrix):
    """Map an (u,0,v) H2 face to the pair verifier's (u,v,0) axes."""
    return [[
        {(iu, iv, 0): coefficient for (iu, zero, iv), coefficient in entry.items() if not zero}
        for entry in row
    ] for row in matrix]


def matrix_equal(left, right):
    return all(left[row][column] == right[row][column] for row in range(4) for column in range(8))


def determinant(matrix, basis):
    return common.mp_determinant(
        [[matrix[row][label - 1] for label in basis] for row in range(4)]
    )


def certify_patch(name, matrix, base_brackets, semantic):
    weak_parent = []
    for basis in moving.BASES4:
        label = "".join(map(str, basis))
        signed = common.mp_scale(determinant(matrix, basis), 1 if base_brackets[basis] > 0 else -1)
        values = common.mp_bernstein(signed)
        if min(values) < 0:
            raise AssertionError(f"{name}: parent sign failed at [{label}]")
        if min(values) == 0:
            weak_parent.append(label)
        semantic.update(repr((name, "P", label, tuple(sorted(signed.items())))).encode("ascii"))
    normals = common.mp_normals(matrix)
    coefficients = common.mp_circuit(normals, joined.SIGNATURES[2], SUPPORT)
    sign = 1 if common.mp_at_origin(coefficients[0]) > 0 else -1
    weak_circuit, strict = [], 0
    for position, polynomial in enumerate(coefficients):
        signed = common.mp_scale(polynomial, sign)
        values = common.mp_bernstein(signed)
        if min(values) < 0:
            raise AssertionError(f"{name}: block-2 circuit changed sign")
        if min(values) == 0:
            weak_circuit.append(position)
        else:
            strict += 1
        semantic.update(repr((name, "C", position, tuple(sorted(signed.items())))).encode("ascii"))
    if not strict:
        raise AssertionError(f"{name}: block-2 circuit could vanish")
    for coordinate in range(4):
        total = {}
        for factor_index, coefficient in zip(SUPPORT, coefficients, strict=True):
            total = common.mp_add(
                total,
                common.mp_scale(
                    common.mp_multiply(coefficient, normals[factor_index][coordinate]),
                    moving.signature_sign(joined.SIGNATURES[2], factor_index),
                ),
            )
        if total:
            raise AssertionError(f"{name}: block-2 cofactor kernel failed")
    return name, tuple(weak_parent), tuple(weak_circuit)


def pair_patches(raw, root_index):
    relatives = pairs.relative_stages(raw, root_index)
    originals = tuple(pairs.original_segment(raw, root_index, index) for index in range(2))
    return tuple(pairs.interpolate(left, right) for left, right in zip(originals, relatives, strict=True))


def main():
    if pairs.file_sha256(SOURCE) != SOURCE_SHA256:
        raise AssertionError("row2599 source SHA changed")
    with np.load(SOURCE, allow_pickle=False) as source:
        raw = source["chart_matrix"][0]
    base_brackets = moving.parent_brackets(raw)
    patches = tuple(
        tuple(
            interpolate(original_stage(raw, edge, stage), relative_stage(raw, edge, stage))
            for stage in range(2)
        )
        for edge in range(2)
    )

    # Common-parameter subdivision and the two frontier-edge pieces glue.
    for edge in range(2):
        if not matrix_equal(restrict_matrix(patches[edge][0], 0, 1), restrict_matrix(patches[edge][1], 0, 0)):
            raise AssertionError(f"H2 edge {edge}: u seam changed")
    for stage in range(2):
        if not matrix_equal(restrict_matrix(patches[0][stage], 1, 1), restrict_matrix(patches[1][stage], 1, 0)):
            raise AssertionError(f"H2 stage {stage}: frontier corner seam changed")

    # The two external r faces are literally the block-2 lateral disks of
    # the p12 and p20 pair prisms.
    p12, p20 = pair_patches(raw, 1), pair_patches(raw, 2)
    for stage in range(2):
        left = reaxis_r_face(restrict_matrix(patches[0][stage], 1, 0))
        right = reaxis_r_face(restrict_matrix(patches[1][stage], 1, 1))
        if not matrix_equal(left, p12[stage]):
            raise AssertionError(f"H2 stage {stage}: p12 lateral is not literal")
        if not matrix_equal(right, p20[stage]):
            raise AssertionError(f"H2 stage {stage}: p20 lateral is not literal")

    # v=0 is K(h2); v=1 is parent-relative.  The u=0 face is the source
    # parent frontier, while u=1 collapses to the common [2467] apex.
    relative_walls = []
    for edge in range(2):
        for stage in range(2):
            patch = patches[edge][stage]
            relative = restrict_matrix(patch, 2, 1)
            walls = tuple(
                "".join(map(str, basis)) for basis in moving.BASES4
                if not determinant(relative, basis)
            )
            if not walls:
                raise AssertionError("H2 relative face lost its wall")
            relative_walls.append((edge, stage, walls))
    for edge in range(2):
        source_face = restrict_matrix(patches[edge][0], 0, 0)
        if not matrix_equal(restrict_matrix(source_face, 2, 0), restrict_matrix(source_face, 2, 1)):
            raise AssertionError("H2 source face did not collapse in homotopy parameter")
        apex_face = restrict_matrix(patches[edge][1], 0, 1)
        if not matrix_equal(restrict_matrix(apex_face, 2, 0), restrict_matrix(apex_face, 2, 1)):
            raise AssertionError("H2 apex face did not collapse in homotopy parameter")

    semantic = sha256(b"diag3-row2599-h2-comparison-prism-v1\0")
    reports = tuple(
        certify_patch(f"h2-edge-{edge}-patch-{stage}", patches[edge][stage], base_brackets, semantic)
        for edge in range(2) for stage in range(2)
    )
    boundary = {
        "K(h2)": 1,
        "Q(p12,block2)": -1,
        "Q(p20,block2)": 1,
        "relative_patch_faces": 4,
        "internal_u_face_pairs": 2,
        "internal_r_face_pairs": 2,
    }
    semantic.update(repr((reports, tuple(relative_walls), boundary)).encode("ascii"))
    digest = semantic.hexdigest()
    if EXPECTED_SEMANTIC != "TO_BE_PINNED" and digest != EXPECTED_SEMANTIC:
        raise AssertionError(f"H2 comparison semantic changed: {digest}")
    print("PASS exact H2 comparison prism", reports)
    print("PASS literal p12/p20 block-2 lateral disks and signed boundary", boundary)
    print("PASS relative wall patches", tuple(relative_walls))
    print("SEMANTIC", digest)
    print("THEOREM row2599 comparison-incidence count advances to 4/6")
    print("OPEN H0/H1 prisms, mixed J, global cover")
    print("SCOPE one local singular comparison chain; no d3 or ledger change")


if __name__ == "__main__":
    main()
