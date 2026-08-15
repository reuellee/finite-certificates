#!/usr/bin/env python3
"""Exact nonradial relative collar for the exceptional row-2599 p01 edge.

The direct two-parameter ``p01`` wall slide is false: block zero becomes good
before the first additional parent wall.  This verifier constructs a different
piecewise-rational path.  It leaves that plane at the exact witness wall,
reaches ``[1367]``, follows ``[1367]`` to ``[2467]``, and then follows the
``[2467]`` graph to the already certified common endpoint.

Every segment lies in the genuine parent frontier.  Exact Bernstein
coefficients certify all 70 parent signs and positive Gordan circuits for both
incident blocks.  This is a relative pair-wall collar, not yet a comparison
prism or the missing mixed ``d3`` cell.
"""

from __future__ import annotations

from fractions import Fraction
from hashlib import sha256
from math import comb
from pathlib import Path
import sys

import numpy as np


HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import verify_diag2_moving_witness_shear as moving  # noqa: E402
import verify_diag3_joined_flow_triangle as joined  # noqa: E402
import verify_diag3_row2599_common_proper_escape as common  # noqa: E402


SOURCE = HERE / "data/seeat_parent2599_upper178.npz"
SOURCE_SHA256 = "3b90799d26b7783e92c2ac697eaaf8b76d26a787f53205873b997657e114180a"

ROOT_ENDPOINT = Fraction(1_221_971_981, 1_769_366_234)
WITNESS_WALL = Fraction(
    83_503_134_767_238_851_186_305_349_765_512_866,
    43_552_580_189_648_394_406_194_000_441_042_241,
)
TANGENT_ADVANCE = Fraction(9, 160)
OFFPLANE_ENDPOINT = Fraction(
    3_358_010_538_087_089_065_822_291_885_427_450_701_681_795,
    3_308_387_436_982_263_269_937_203_185_897_076_819_775_106,
)
ROOT_TARGET = Fraction(
    234_256_547_531_343_777_781_047_691_330_195_444_590_421_787_902_374_123_738_445_539_062_790_489_112_404_622_131_159,
    13_372_644_039_892_933_623_810_456_407_340_392_486_129_320_262_099_558_845_715_262_274_062_239_731_375_045_118_995_681,
)

# The tangent changes the first coordinate of labelled column six.  Columns
# one through four therefore remain dependent along the first two stages.
OFFPLANE_ROW = 0
OFFPLANE_COLUMN = 5

SUPPORTS = {
    0: (2, 19, 21, 37, 38),
    1: (2, 9, 27, 30, 35),
}
SUPPORT_LABELS = {
    0: ("134", "456", "137", "238", "148"),
    1: ("134", "345", "257", "167", "128"),
}

EXPECTED_SEMANTIC = "e3df18c1a98ccca9e022832e3656c7e2ae3a9c7c822a153c7fc40e9519e08016"


def file_sha256(path: Path) -> str:
    digest = sha256()
    with path.open("rb") as source:
        while block := source.read(1 << 20):
            digest.update(block)
    return digest.hexdigest()


def variable():
    return {(1, 0, 0): Fraction(1)}


def determinant(matrix, basis):
    return common.mp_determinant(
        [[matrix[row][label - 1] for label in basis] for row in range(4)]
    )


def untapered_root_matrix(matrix, common_parameter, root_parameter):
    target = [
        [common.mp_constant(int(matrix[row, column])) for column in range(8)]
        for row in range(4)
    ]
    for row in range(4):
        target[row][common.MOVING_COLUMN] = common.mp_add(
            target[row][common.MOVING_COLUMN],
            common.mp_scale(
                common_parameter,
                common.ENDPOINT * common.EXPECTED_DIRECTION[row],
            ),
        )
    source, destination, sign = common.PAIR_ROOTS[0]
    for row in range(4):
        target[row][source - 1] = common.mp_add(
            target[row][source - 1],
            common.mp_scale(
                common.mp_multiply(root_parameter, target[row][destination - 1]),
                sign,
            ),
        )
    return target


def restrict(polynomial, value):
    answer = {}
    value = Fraction(value)
    for exponent, coefficient in polynomial.items():
        power = exponent[0]
        target = (0, exponent[1], exponent[2])
        answer[target] = answer.get(target, Fraction(0)) + coefficient * value**power
    return {exponent: coefficient for exponent, coefficient in answer.items() if coefficient}


def restrict_matrix(matrix, value):
    return [[restrict(entry, value) for entry in row] for row in matrix]


def constant_at(polynomial):
    return polynomial.get((0, 0, 0), Fraction(0))


def evaluate_two(polynomial, first, second):
    first, second = Fraction(first), Fraction(second)
    return sum(
        coefficient * first**exponent[0] * second**exponent[1]
        for exponent, coefficient in polynomial.items()
    )


def signed_circuit(matrix, block):
    normals = common.mp_normals(matrix)
    coefficients = common.mp_circuit(
        normals, joined.SIGNATURES[block], SUPPORTS[block]
    )
    anchor = next(
        constant_at(coefficient)
        for coefficient in coefficients
        if constant_at(coefficient)
    )
    sign = 1 if anchor > 0 else -1
    signed = tuple(common.mp_scale(coefficient, sign) for coefficient in coefficients)

    # Replay the cofactor kernel instead of trusting positivity alone.
    for coordinate in range(4):
        total = {}
        for index, coefficient in zip(SUPPORTS[block], signed, strict=True):
            total = common.mp_add(
                total,
                common.mp_scale(
                    common.mp_multiply(coefficient, normals[index][coordinate]),
                    moving.signature_sign(joined.SIGNATURES[block], index),
                ),
            )
        if total:
            raise AssertionError(f"block {block}: cofactor kernel identity failed")
    return signed


def certificate_segment(
    name,
    matrix,
    base_brackets,
    expected_parent_weak,
    expected_parent_identically_zero,
    expected_circuit_weak,
    semantic,
):
    parent_weak = []
    parent_identically_zero = []
    for basis in moving.BASES4:
        label = "".join(map(str, basis))
        polynomial = determinant(matrix, basis)
        sign = 1 if base_brackets[basis] > 0 else -1
        signed = common.mp_scale(polynomial, sign)
        values = tuple(sign * value for value in common.mp_bernstein(polynomial))
        if min(values) < 0:
            raise AssertionError(f"{name}: parent sign failed at [{label}]")
        if min(values) == 0:
            parent_weak.append(label)
        if not polynomial:
            parent_identically_zero.append(label)
        semantic.update(name.encode("ascii") + b"\0P\0" + label.encode("ascii") + b"\0")
        semantic.update(repr(tuple(sorted(signed.items()))).encode("ascii"))

    if tuple(parent_weak) != tuple(expected_parent_weak):
        raise AssertionError(f"{name}: weak parent walls changed: {parent_weak}")
    if tuple(parent_identically_zero) != tuple(expected_parent_identically_zero):
        raise AssertionError(
            f"{name}: identically-zero parent walls changed: {parent_identically_zero}"
        )

    circuit_weak = []
    for block in (0, 1):
        for position, (label, polynomial) in enumerate(
            zip(SUPPORT_LABELS[block], signed_circuit(matrix, block), strict=True)
        ):
            values = common.mp_bernstein(polynomial)
            if min(values) < 0:
                raise AssertionError(
                    f"{name}: block {block} circuit coefficient {label} changed sign"
                )
            if min(values) == 0:
                circuit_weak.append((block, position, label))
            semantic.update(
                name.encode("ascii")
                + b"\0C"
                + str(block).encode("ascii")
                + b"\0"
                + label.encode("ascii")
                + b"\0"
            )
            semantic.update(repr(tuple(sorted(polynomial.items()))).encode("ascii"))
    if tuple(circuit_weak) != tuple(expected_circuit_weak):
        raise AssertionError(f"{name}: weak circuit census changed: {circuit_weak}")
    if not parent_identically_zero:
        raise AssertionError(f"{name}: segment is not contained in parent infinity")
    return {
        "name": name,
        "weak_parent_walls": tuple(parent_weak),
        "identically_zero_parent_walls": tuple(parent_identically_zero),
        "weak_circuit_coefficients": tuple(circuit_weak),
    }


def matrices_equal(left, right):
    return all(
        left[row][column] == right[row][column]
        for row in range(4)
        for column in range(8)
    )


def verify_positive_column_gauge(left, right, scale, column, blocks):
    """Check a seam differing only by one positive projective column scale."""
    scale = Fraction(scale)
    if scale <= 0:
        raise AssertionError("column gauge is not positive")
    for row in range(4):
        for current in range(8):
            left_value = constant_at(left[row][current])
            right_value = constant_at(right[row][current])
            expected = scale * left_value if current == column else left_value
            if right_value != expected:
                raise AssertionError("projective column-gauge seam changed")

    # A derived normal is scaled exactly when its triple contains the scaled
    # label.  Dividing that row's Gordan weight by the same positive factor
    # transports the witness section across the gauge seam.
    left_normals = common.mp_normals(left)
    right_normals = common.mp_normals(right)
    scaled_label = column + 1
    for index, triple in enumerate(moving.TRIPLES):
        row_scale = scale if scaled_label in triple else Fraction(1)
        for coordinate in range(4):
            if constant_at(right_normals[index][coordinate]) != (
                row_scale * constant_at(left_normals[index][coordinate])
            ):
                raise AssertionError("derived-normal gauge transport changed")
    for block in blocks:
        coefficients = signed_circuit(left, block)
        transported = tuple(
            constant_at(coefficient)
            / (scale if scaled_label in moving.TRIPLES[index] else 1)
            for index, coefficient in zip(SUPPORTS[block], coefficients, strict=True)
        )
        if min(transported) <= 0:
            raise AssertionError("transported Gordan section lost positivity")
        for coordinate in range(4):
            total = sum(
                coefficient
                * moving.signature_sign(joined.SIGNATURES[block], index)
                * constant_at(right_normals[index][coordinate])
                for index, coefficient in zip(
                    SUPPORTS[block], transported, strict=True
                )
            )
            if total:
                raise AssertionError("transported Gordan section left the kernel")


def main():
    actual_sha = file_sha256(SOURCE)
    if actual_sha != SOURCE_SHA256:
        raise AssertionError(f"row2599 source SHA changed: {actual_sha}")
    with np.load(SOURCE, allow_pickle=False) as source:
        matrix = source["chart_matrix"][0]
    base_brackets = moving.parent_brackets(matrix)
    t = variable()
    semantic = sha256(b"diag3-row2599-p01-tangent-collar-v1\0")
    semantic.update(actual_sha.encode("ascii") + b"\0")

    # Segment zero: the original [1234] wall slide is valid only through the
    # exact block-zero witness wall.  Its last coefficient may vanish at the
    # endpoint, but the remaining four coefficients stay positive.
    stage0 = untapered_root_matrix(
        matrix,
        common.mp_scale(t, WITNESS_WALL),
        common.mp_constant(ROOT_ENDPOINT),
    )

    # Derive, rather than assume, the off-plane endpoint on [1367].
    a = {(1, 0, 0): Fraction(1)}
    generic = untapered_root_matrix(
        matrix, a, common.mp_constant(ROOT_ENDPOINT)
    )
    generic[OFFPLANE_ROW][OFFPLANE_COLUMN] = common.mp_add(
        generic[OFFPLANE_ROW][OFFPLANE_COLUMN],
        {(0, 1, 0): Fraction(1)},
    )
    endpoint_a = WITNESS_WALL + TANGENT_ADVANCE
    wall = determinant(generic, (1, 3, 6, 7))
    wall_at_zero = evaluate_two(wall, endpoint_a, 0)
    wall_slope = evaluate_two(wall, endpoint_a, 1) - wall_at_zero
    endpoint_b = -wall_at_zero / wall_slope
    if endpoint_b != OFFPLANE_ENDPOINT or endpoint_b <= 0:
        raise AssertionError(f"off-plane [1367] endpoint changed: {endpoint_b}")

    stage1 = untapered_root_matrix(
        matrix,
        common.mp_add(
            common.mp_constant(WITNESS_WALL),
            common.mp_scale(t, TANGENT_ADVANCE),
        ),
        common.mp_constant(ROOT_ENDPOINT),
    )
    stage1[OFFPLANE_ROW][OFFPLANE_COLUMN] = common.mp_add(
        stage1[OFFPLANE_ROW][OFFPLANE_COLUMN],
        common.mp_scale(t, endpoint_b),
    )

    # At [1367], varying the root does not move that wall.  Solve the affine
    # [2467] equation exactly for the next relative corner.
    root_variable_matrix = untapered_root_matrix(
        matrix, common.mp_constant(endpoint_a), t
    )
    root_variable_matrix[OFFPLANE_ROW][OFFPLANE_COLUMN] = common.mp_add(
        root_variable_matrix[OFFPLANE_ROW][OFFPLANE_COLUMN],
        common.mp_constant(endpoint_b),
    )
    target_wall = determinant(root_variable_matrix, (2, 4, 6, 7))
    target_constant = constant_at(target_wall)
    target_slope = target_wall.get((1, 0, 0), Fraction(0))
    if set(target_wall) - {(0, 0, 0), (1, 0, 0)} or not target_slope:
        raise AssertionError("[2467] root equation is no longer affine")
    root_target = -target_constant / target_slope
    if root_target != ROOT_TARGET:
        raise AssertionError(f"[1367]/[2467] root target changed: {root_target}")
    stage2 = untapered_root_matrix(
        matrix,
        common.mp_constant(endpoint_a),
        common.mp_add(
            common.mp_constant(ROOT_ENDPOINT),
            common.mp_scale(t, root_target - ROOT_ENDPOINT),
        ),
    )
    stage2[OFFPLANE_ROW][OFFPLANE_COLUMN] = common.mp_add(
        stage2[OFFPLANE_ROW][OFFPLANE_COLUMN],
        common.mp_constant(endpoint_b),
    )

    # Final graph leg.  Interpolate a and b, solve [2467]=0 for the root, and
    # clear its rational denominator by a positive scaling of labelled column
    # two.  This ends at the pre-existing common [2467] apex.
    final_a = common.mp_add(
        common.mp_constant(endpoint_a), common.mp_scale(t, 1 - endpoint_a)
    )
    final_b = common.mp_add(
        common.mp_constant(endpoint_b), common.mp_scale(t, -endpoint_b)
    )
    root_zero = untapered_root_matrix(
        matrix, final_a, common.mp_constant(0)
    )
    root_zero[OFFPLANE_ROW][OFFPLANE_COLUMN] = common.mp_add(
        root_zero[OFFPLANE_ROW][OFFPLANE_COLUMN], final_b
    )
    root_one = untapered_root_matrix(
        matrix, final_a, common.mp_constant(1)
    )
    root_one[OFFPLANE_ROW][OFFPLANE_COLUMN] = common.mp_add(
        root_one[OFFPLANE_ROW][OFFPLANE_COLUMN], final_b
    )
    numerator_at_zero = determinant(root_zero, (2, 4, 6, 7))
    root_coefficient = common.mp_add(
        determinant(root_one, (2, 4, 6, 7)),
        common.mp_scale(numerator_at_zero, -1),
    )
    denominator = root_coefficient
    numerator = common.mp_scale(numerator_at_zero, -1)
    if min(common.mp_bernstein(denominator)) <= 0:
        denominator = common.mp_scale(denominator, -1)
        numerator = common.mp_scale(numerator, -1)
    if min(common.mp_bernstein(denominator)) <= 0:
        raise AssertionError("[2467] graph denominator is not strictly positive")
    if constant_at(numerator) / constant_at(denominator) != root_target:
        raise AssertionError("final [2467] graph does not start at the root target")
    if constant_at(restrict(numerator, 1)):
        raise AssertionError("final [2467] graph does not end at zero root")

    stage3 = [[dict(entry) for entry in row] for row in root_zero]
    for row in range(4):
        stage3[row][1] = common.mp_add(
            common.mp_multiply(denominator, root_zero[row][1]),
            common.mp_scale(
                common.mp_multiply(numerator, root_zero[row][7]), -1
            ),
        )

    reports = (
        certificate_segment(
            "source-to-witness",
            stage0,
            base_brackets,
            ("1234",),
            ("1234",),
            ((0, 0, "134"),),
            semantic,
        ),
        certificate_segment(
            "off-plane-to-1367",
            stage1,
            base_brackets,
            ("1234", "1367"),
            ("1234",),
            ((0, 0, "134"),),
            semantic,
        ),
        certificate_segment(
            "1367-to-2467",
            stage2,
            base_brackets,
            ("1234", "1367", "2467"),
            ("1367",),
            (),
            semantic,
        ),
        certificate_segment(
            "2467-graph-to-common-apex",
            stage3,
            base_brackets,
            ("1367", "2467"),
            ("2467",),
            (),
            semantic,
        ),
    )

    # Literal seams for the first three stages.
    if not matrices_equal(restrict_matrix(stage0, 1), restrict_matrix(stage1, 0)):
        raise AssertionError("source/witness-to-tangent seam changed")
    if not matrices_equal(restrict_matrix(stage1, 1), restrict_matrix(stage2, 0)):
        raise AssertionError("tangent/[1367] seam changed")

    # The denominator clearing on stage three is a positive projective gauge.
    denominator_start = constant_at(denominator)
    denominator_end = constant_at(restrict(denominator, 1))
    verify_positive_column_gauge(
        restrict_matrix(stage2, 1),
        restrict_matrix(stage3, 0),
        denominator_start,
        1,
        (0, 1),
    )
    common_apex = untapered_root_matrix(
        matrix, common.mp_constant(1), common.mp_constant(0)
    )
    verify_positive_column_gauge(
        common_apex,
        restrict_matrix(stage3, 1),
        denominator_end,
        1,
        (0, 1),
    )

    # The first off-plane derivative is positive for the coefficient which
    # vanished on the false direct collar.  This pins the actual tangent-cone
    # repair rather than only its distant endpoint.
    first_coefficient = signed_circuit(stage1, 0)[0]
    tangent_derivative = first_coefficient.get((1, 0, 0), Fraction(0))
    if tangent_derivative <= 0:
        raise AssertionError("off-plane tangent does not enter the block-0 bad side")

    semantic.update(repr((
        WITNESS_WALL,
        TANGENT_ADVANCE,
        endpoint_b,
        root_target,
        tuple(common.mp_bernstein(denominator)),
        tangent_derivative,
        reports,
    )).encode("ascii"))
    digest = semantic.hexdigest()
    if EXPECTED_SEMANTIC != "TO_BE_PINNED" and digest != EXPECTED_SEMANTIC:
        raise AssertionError(f"p01 tangent-collar semantic changed: {digest}")

    print("PASS pinned row2599 source", actual_sha)
    print("PASS exact p01 relative tangent collar", reports)
    print("PASS off-plane endpoint [1234,1367]", endpoint_a, endpoint_b)
    print("PASS root corner [1367,2467]", root_target)
    print("PASS positive [2467] graph denominator", common.mp_bernstein(denominator))
    print("PASS exact positive projective-gauge seams", denominator_start, denominator_end)
    print("SEMANTIC", digest)
    print("THEOREM the row2599 p01 pair edge has a four-segment relative bad-locus collar")
    print("SCOPE collar replay only; the separate p01 prism does not close mixed d3 or global cover")


if __name__ == "__main__":
    main()
