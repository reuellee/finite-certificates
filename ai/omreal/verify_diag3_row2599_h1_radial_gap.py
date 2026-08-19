#!/usr/bin/env python3
"""Exact fail-closed screen for the tempting row-2599 H1 radial prism.

Replacing the exceptional ``p01`` collar by the generic two-stage radial
collar makes the four H1 comparison patches retain the parent signs and the
block-one Gordan circuit.  This is not a relative comparison prism: the
second radial ``p01`` stage is not contained in any parent wall.  The already
certified nonradial ``p01`` collar is relative, but has five literal stages
and is not the external face of this four-patch construction.

The checker records the useful positive screen and the exact gluing
obstruction.  It deliberately does not advance the 4/6 comparison-incidence
count.
"""

from __future__ import annotations

from fractions import Fraction
from hashlib import sha256

import numpy as np

import verify_diag2_moving_witness_shear as moving
import verify_diag3_row2599_common_proper_escape as common
import verify_diag3_row2599_h2_comparison_prism as h2
import verify_diag3_row2599_p01_comparison_prism as p01
import verify_diag3_row2599_p12_p20_comparison_prisms as pairs


ROOT0 = common.ROOT_ENDPOINTS[0]
ROOT1 = common.ROOT_ENDPOINTS[1]
SUPPORT = pairs.SAFE_SUPPORTS[1]
EXPECTED_SEMANTIC = "046e51a271bf169c499e3473d5bf399724f6e22a23612a7b2d31ef660c01cbcc"


def root_values(edge):
    if edge == 0:
        return common.mp_constant(ROOT0), common.mp_scale(h2.R, ROOT1)
    if edge == 1:
        return (
            common.mp_scale(
                common.mp_add(
                    common.mp_constant(1), common.mp_scale(h2.R, -1)
                ),
                ROOT0,
            ),
            common.mp_constant(ROOT1),
        )
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
                common_parameter,
                common.ENDPOINT * common.EXPECTED_DIRECTION[row],
            ),
        )
    for root_index, parameter in ((0, first_parameter), (1, second_parameter)):
        source, destination, sign = common.PAIR_ROOTS[root_index]
        for row in range(4):
            matrix[row][source - 1] = common.mp_add(
                matrix[row][source - 1],
                common.mp_scale(
                    common.mp_multiply(
                        parameter, matrix[row][destination - 1]
                    ),
                    sign,
                ),
            )
    return matrix


def relative_stage(raw, edge, stage):
    first, second = root_values(edge)
    if stage == 0:
        return two_root_matrix(raw, h2.U, first, second)
    if stage == 1:
        taper = common.mp_add(
            common.mp_constant(1), common.mp_scale(h2.U, -1)
        )
        return two_root_matrix(
            raw,
            common.mp_constant(1),
            common.mp_multiply(taper, first),
            common.mp_multiply(taper, second),
        )
    raise AssertionError(stage)


def original_stage(raw, edge, stage):
    parameter = common.mp_add(
        common.mp_constant(Fraction(stage, 2)),
        common.mp_scale(h2.U, Fraction(1, 2)),
    )
    taper = common.mp_add(
        common.mp_constant(1), common.mp_scale(parameter, -1)
    )
    first, second = root_values(edge)
    return two_root_matrix(
        raw,
        parameter,
        common.mp_multiply(taper, first),
        common.mp_multiply(taper, second),
    )


def zero_wall_labels(matrix):
    return tuple(
        "".join(map(str, basis))
        for basis in moving.BASES4
        if not pairs.determinant(matrix, basis)
    )


def main():
    if pairs.file_sha256(pairs.SOURCE) != pairs.SOURCE_SHA256:
        raise AssertionError("row2599 source SHA changed")
    with np.load(pairs.SOURCE, allow_pickle=False) as source:
        raw = source["chart_matrix"][0]
    base_brackets = moving.parent_brackets(raw)

    patches = tuple(
        tuple(
            h2.interpolate(
                original_stage(raw, edge, stage),
                relative_stage(raw, edge, stage),
            )
            for stage in range(2)
        )
        for edge in range(2)
    )

    for edge in range(2):
        if not h2.matrix_equal(
            h2.restrict_matrix(patches[edge][0], 0, 1),
            h2.restrict_matrix(patches[edge][1], 0, 0),
        ):
            raise AssertionError(f"H1 edge {edge}: u seam changed")
    for stage in range(2):
        if not h2.matrix_equal(
            h2.restrict_matrix(patches[0][stage], 1, 1),
            h2.restrict_matrix(patches[1][stage], 1, 0),
        ):
            raise AssertionError(f"H1 stage {stage}: frontier seam changed")

    generic_p01 = tuple(
        pairs.interpolate(
            pairs.original_segment(raw, 0, stage),
            pairs.relative_stages(raw, 0)[stage],
        )
        for stage in range(2)
    )
    p12 = tuple(
        pairs.interpolate(
            pairs.original_segment(raw, 1, stage),
            pairs.relative_stages(raw, 1)[stage],
        )
        for stage in range(2)
    )
    for stage in range(2):
        left = h2.reaxis_r_face(
            h2.restrict_matrix(patches[0][stage], 1, 0)
        )
        right = h2.reaxis_r_face(
            h2.restrict_matrix(patches[1][stage], 1, 1)
        )
        if not h2.matrix_equal(left, generic_p01[stage]):
            raise AssertionError(f"H1 stage {stage}: generic p01 face changed")
        if not h2.matrix_equal(right, p12[stage]):
            raise AssertionError(f"H1 stage {stage}: p12 face changed")

    semantic = sha256(b"diag3-row2599-h1-radial-gap-v1\0")
    reports = tuple(
        pairs.certify_patch(
            f"h1-edge-{edge}-stage-{stage}",
            patches[edge][stage],
            (1,),
            base_brackets,
            semantic,
        )
        for edge in range(2)
        for stage in range(2)
    )

    radial_collar = pairs.relative_stages(raw, 0)
    radial_walls = tuple(zero_wall_labels(stage) for stage in radial_collar)
    if radial_walls != (("1234",), ()):
        raise AssertionError(f"radial p01 wall census changed: {radial_walls}")

    special_collar = p01.build_collar(raw)
    special_walls = tuple(zero_wall_labels(stage) for stage in special_collar)
    expected_special = (
        ("1234",),
        ("1234",),
        ("1367",),
        ("2467",),
        ("2467",),
    )
    if special_walls != expected_special:
        raise AssertionError(f"nonradial p01 wall census changed: {special_walls}")

    gap = {
        "candidate_patches": 4,
        "candidate_block": 1,
        "radial_p01_stages": 2,
        "radial_nonrelative_stages": (1,),
        "certified_p01_stages": 5,
        "literal_external_face": False,
        "comparison_incidence_before": "4/6",
        "comparison_incidence_after": "4/6",
    }
    semantic.update(
        repr((reports, radial_walls, special_walls, gap)).encode("ascii")
    )
    digest = semantic.hexdigest()
    if EXPECTED_SEMANTIC != "TO_BE_PINNED" and digest != EXPECTED_SEMANTIC:
        raise AssertionError(f"H1 radial-gap semantic changed: {digest}")

    print("PASS four H1 radial-screen patches preserve parent signs and block 1")
    print("PASS literal generic-p01/p12 faces", reports)
    print("PASS radial p01 relative-wall census", radial_walls)
    print("PASS certified nonradial p01 relative-wall census", special_walls)
    print("SEMANTIC", digest)
    print("NO-GO second radial p01 stage is not contained in parent infinity")
    print("OPEN a literal compatibility homotopy from the five-stage p01 disk")
    print("LEDGER comparison incidences remain 4/6; theorem score remains 2/9")


if __name__ == "__main__":
    main()
