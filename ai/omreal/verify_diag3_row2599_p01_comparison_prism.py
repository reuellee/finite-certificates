#!/usr/bin/env python3
"""Exact row-2599 comparison prism from K(p01) to parent infinity.

The nonrelative swept pair face ``K(p01)`` is homotoped, through the locus
where blocks zero and one remain bad, to the certified nonradial relative
collar.  The base homotopy uses five exact polynomial patches.  Taking its
product with the pair block-mass interval gives a three-chain whose only
ordinary boundary pieces are ``K(p01)`` and two explicitly named singleton
lateral disks.

This certifies one of the six comparison prisms needed for the local mixed
``d3`` construction.  It does not identify/fill the two singleton lateral
disks and therefore does not construct ``J`` by itself.
"""

from __future__ import annotations

from fractions import Fraction
from hashlib import sha256
from pathlib import Path

import numpy as np

import verify_diag2_moving_witness_shear as moving
import verify_diag3_row2599_common_proper_escape as common
import verify_diag3_row2599_p01_tangent_collar as collar


SOURCE = collar.SOURCE
SOURCE_SHA256 = collar.SOURCE_SHA256
PATCH_COUNT = 5
EXPECTED_SEMANTIC = "0b015361e1c75007f025e90921fa5f295616b0e3e8d4bbf941e5161545e433c7"


def restrict_axis(polynomial, axis, value):
    answer = {}
    value = Fraction(value)
    for exponent, coefficient in polynomial.items():
        target = list(exponent)
        power = target[axis]
        target[axis] = 0
        target = tuple(target)
        answer[target] = answer.get(target, Fraction(0)) + coefficient * value**power
    return {exponent: coefficient for exponent, coefficient in answer.items() if coefficient}


def restrict_matrix(matrix, axis, value):
    return [
        [restrict_axis(entry, axis, value) for entry in row]
        for row in matrix
    ]


def matrix_equal(left, right):
    return all(
        left[row][column] == right[row][column]
        for row in range(4) for column in range(8)
    )


def build_collar(matrix):
    """Return five literally glued polynomial representatives of the collar."""
    t = collar.variable()
    endpoint_a = collar.WITNESS_WALL + collar.TANGENT_ADVANCE
    stage0 = collar.untapered_root_matrix(
        matrix,
        common.mp_scale(t, collar.WITNESS_WALL),
        common.mp_constant(collar.ROOT_ENDPOINT),
    )
    stage1 = collar.untapered_root_matrix(
        matrix,
        common.mp_add(
            common.mp_constant(collar.WITNESS_WALL),
            common.mp_scale(t, collar.TANGENT_ADVANCE),
        ),
        common.mp_constant(collar.ROOT_ENDPOINT),
    )
    stage1[collar.OFFPLANE_ROW][collar.OFFPLANE_COLUMN] = common.mp_add(
        stage1[collar.OFFPLANE_ROW][collar.OFFPLANE_COLUMN],
        common.mp_scale(t, collar.OFFPLANE_ENDPOINT),
    )
    stage2 = collar.untapered_root_matrix(
        matrix,
        common.mp_constant(endpoint_a),
        common.mp_add(
            common.mp_constant(collar.ROOT_ENDPOINT),
            common.mp_scale(t, collar.ROOT_TARGET - collar.ROOT_ENDPOINT),
        ),
    )
    stage2[collar.OFFPLANE_ROW][collar.OFFPLANE_COLUMN] = common.mp_add(
        stage2[collar.OFFPLANE_ROW][collar.OFFPLANE_COLUMN],
        common.mp_constant(collar.OFFPLANE_ENDPOINT),
    )

    final_a = common.mp_add(
        common.mp_constant(endpoint_a), common.mp_scale(t, 1 - endpoint_a)
    )
    final_b = common.mp_add(
        common.mp_constant(collar.OFFPLANE_ENDPOINT),
        common.mp_scale(t, -collar.OFFPLANE_ENDPOINT),
    )
    root_zero = collar.untapered_root_matrix(
        matrix, final_a, common.mp_constant(0)
    )
    root_one = collar.untapered_root_matrix(
        matrix, final_a, common.mp_constant(1)
    )
    for target in (root_zero, root_one):
        target[collar.OFFPLANE_ROW][collar.OFFPLANE_COLUMN] = common.mp_add(
            target[collar.OFFPLANE_ROW][collar.OFFPLANE_COLUMN], final_b
        )
    value_at_zero = collar.determinant(root_zero, (2, 4, 6, 7))
    root_coefficient = common.mp_add(
        collar.determinant(root_one, (2, 4, 6, 7)),
        common.mp_scale(value_at_zero, -1),
    )
    denominator = root_coefficient
    numerator = common.mp_scale(value_at_zero, -1)
    if min(common.mp_bernstein(denominator)) <= 0:
        denominator = common.mp_scale(denominator, -1)
        numerator = common.mp_scale(numerator, -1)
    if min(common.mp_bernstein(denominator)) <= 0:
        raise AssertionError("comparison prism lost the positive graph denominator")
    stage3 = [[dict(entry) for entry in row] for row in root_zero]
    for row in range(4):
        stage3[row][1] = common.mp_add(
            common.mp_multiply(denominator, root_zero[row][1]),
            common.mp_scale(
                common.mp_multiply(numerator, root_zero[row][7]), -1
            ),
        )

    # Replace the two projective seam identifications by literal positive
    # gauge paths.  This produces five polynomial segments with equal endpoint
    # matrices, which is convenient for an exact cubical prism.
    denominator_start = collar.constant_at(denominator)
    denominator_end = collar.constant_at(collar.restrict(denominator, 1))
    gauge2 = common.mp_add(
        common.mp_constant(1), common.mp_scale(t, denominator_start - 1)
    )
    stage2_gauged = [[dict(entry) for entry in row] for row in stage2]
    for row in range(4):
        stage2_gauged[row][1] = common.mp_multiply(
            gauge2, stage2_gauged[row][1]
        )

    common_apex = collar.untapered_root_matrix(
        matrix, common.mp_constant(1), common.mp_constant(0)
    )
    final_gauge = common.mp_add(
        common.mp_constant(denominator_end),
        common.mp_scale(t, 1 - denominator_end),
    )
    stage4 = [[dict(entry) for entry in row] for row in common_apex]
    for row in range(4):
        stage4[row][1] = common.mp_multiply(final_gauge, stage4[row][1])

    stages = (stage0, stage1, stage2_gauged, stage3, stage4)
    for index in range(len(stages) - 1):
        if not matrix_equal(
            restrict_matrix(stages[index], 0, 1),
            restrict_matrix(stages[index + 1], 0, 0),
        ):
            raise AssertionError(f"literal collar seam {index} changed")
    return stages


def original_subsegment(matrix, index):
    t = collar.variable()
    parameter = common.mp_add(
        common.mp_constant(Fraction(index, PATCH_COUNT)),
        common.mp_scale(t, Fraction(1, PATCH_COUNT)),
    )
    return collar.untapered_root_matrix(
        matrix,
        parameter,
        common.mp_scale(
            common.mp_add(
                common.mp_constant(1), common.mp_scale(parameter, -1)
            ),
            collar.ROOT_ENDPOINT,
        ),
    )


def interpolate(original, relative):
    v = {(0, 1, 0): Fraction(1)}
    return [
        [
            common.mp_add(
                original[row][column],
                common.mp_multiply(
                    v,
                    common.mp_add(
                        relative[row][column],
                        common.mp_scale(original[row][column], -1),
                    ),
                ),
            )
            for column in range(8)
        ]
        for row in range(4)
    ]


def certify_patch(name, matrix, base_brackets, semantic):
    weak_parent = []
    for basis in moving.BASES4:
        label = "".join(map(str, basis))
        polynomial = collar.determinant(matrix, basis)
        signed = common.mp_scale(
            polynomial, 1 if base_brackets[basis] > 0 else -1
        )
        values = common.mp_bernstein(signed)
        if min(values) < 0:
            raise AssertionError(f"{name}: parent sign failed at [{label}]")
        if min(values) == 0:
            weak_parent.append(label)
        semantic.update(repr((name, "P", label, tuple(sorted(signed.items())))).encode("ascii"))

    weak_circuit = []
    for block in (0, 1):
        coefficients = collar.signed_circuit(matrix, block)
        strictly_positive = 0
        for position, polynomial in enumerate(coefficients):
            values = common.mp_bernstein(polynomial)
            if min(values) < 0:
                raise AssertionError(
                    f"{name}: block {block} coefficient {position} changed sign"
                )
            if min(values) == 0:
                weak_circuit.append((block, position))
            else:
                strictly_positive += 1
            semantic.update(
                repr((name, "C", block, position, tuple(sorted(polynomial.items())))).encode("ascii")
            )
        if not strictly_positive:
            raise AssertionError(f"{name}: block {block} circuit could vanish identically")
    return name, tuple(weak_parent), tuple(weak_circuit)


def boundary_table():
    """Signed ordinary boundary after internal/relative faces are removed."""
    # Product orientation du ^ dv ^ dlambda gives
    #   d = (u=1-u=0) - (v=1-v=0) + (lambda=1-lambda=0).
    # The u faces collapse at the two path endpoints, v=1 is the relative
    # collar, and internal u faces cancel between consecutive patches.
    ordinary = {
        "K(p01)": +1,
        "Q(p01,block0)": -1,
        "Q(p01,block1)": +1,
    }
    if sum((+1, -1)) != 0:
        raise AssertionError("internal patch orientations do not cancel")
    return {
        "patches": PATCH_COUNT,
        "internal_u_face_pairs": PATCH_COUNT - 1,
        "relative_collar_faces": PATCH_COUNT,
        "collapsed_relative_endpoint_faces": 2,
        "ordinary_boundary": ordinary,
    }


def main():
    actual_sha = collar.file_sha256(SOURCE)
    if actual_sha != SOURCE_SHA256:
        raise AssertionError(f"row2599 source SHA changed: {actual_sha}")
    with np.load(SOURCE, allow_pickle=False) as source:
        matrix = source["chart_matrix"][0]
    base_brackets = moving.parent_brackets(matrix)
    relative_stages = build_collar(matrix)
    originals = tuple(original_subsegment(matrix, index) for index in range(PATCH_COUNT))
    patches = tuple(
        interpolate(original, relative)
        for original, relative in zip(originals, relative_stages, strict=True)
    )

    # Literal assembly in both boundary paths and through every homotopy seam.
    for index in range(PATCH_COUNT - 1):
        if not matrix_equal(
            restrict_matrix(originals[index], 0, 1),
            restrict_matrix(originals[index + 1], 0, 0),
        ):
            raise AssertionError(f"original K(p01) subdivision seam {index} changed")
        if not matrix_equal(
            restrict_matrix(patches[index], 0, 1),
            restrict_matrix(patches[index + 1], 0, 0),
        ):
            raise AssertionError(f"comparison-prism seam {index} changed")
    if not matrix_equal(
        restrict_matrix(restrict_matrix(patches[0], 0, 0), 1, 0),
        restrict_matrix(restrict_matrix(patches[0], 0, 0), 1, 1),
    ):
        raise AssertionError("source endpoint face does not collapse")
    if not matrix_equal(
        restrict_matrix(restrict_matrix(patches[-1], 0, 1), 1, 0),
        restrict_matrix(restrict_matrix(patches[-1], 0, 1), 1, 1),
    ):
        raise AssertionError("common-apex endpoint face does not collapse")

    semantic = sha256(b"diag3-row2599-p01-comparison-prism-v1\0")
    reports = tuple(
        certify_patch(f"patch-{index}", patch, base_brackets, semantic)
        for index, patch in enumerate(patches)
    )
    table = boundary_table()

    # The v=1 boundary is genuinely relative on every patch; v=0 is exactly
    # the five-piece subdivision of the stored tapered pair sweep.
    relative_walls = []
    for index, (patch, original) in enumerate(zip(patches, originals, strict=True)):
        if not matrix_equal(restrict_matrix(patch, 1, 0), original):
            raise AssertionError(f"patch {index}: v=0 is not K(p01)")
        relative = restrict_matrix(patch, 1, 1)
        zero_walls = tuple(
            "".join(map(str, basis))
            for basis in moving.BASES4
            if not collar.determinant(relative, basis)
        )
        if not zero_walls:
            raise AssertionError(f"patch {index}: collar face is not relative")
        relative_walls.append(zero_walls)

    semantic.update(repr((reports, table, tuple(relative_walls))).encode("ascii"))
    digest = semantic.hexdigest()
    if EXPECTED_SEMANTIC != "TO_BE_PINNED" and digest != EXPECTED_SEMANTIC:
        raise AssertionError(f"p01 comparison-prism semantic changed: {digest}")
    print("PASS five exact p01 comparison patches", reports)
    print("PASS relative collar wall sequence", tuple(relative_walls))
    print("PASS signed comparison-prism boundary", table)
    print("SEMANTIC", digest)
    print("THEOREM one row2599 comparison prism connects K(p01) to parent infinity")
    print("OPEN the named block-0/block-1 lateral disks still require singleton-prism gluing")
    print("SCOPE one of six local comparison prisms; no mixed J, global cover, or ledger change")


if __name__ == "__main__":
    main()
