#!/usr/bin/env python3
"""Exact diagonal-two falsifier for arbitrary-witness shear compatibility.

Two realizable, proper, incomparable parent-16 extension regions are both
bad at the displayed base chart.  One legitimate pair of strict minimal
five-circuit witnesses has no compatible elementary moving-witness shear.
Replacing one circuit element restores a unique shear and an exact escape to
the parent boundary.

This refutes compatibility for arbitrary preselected witnesses.  It does not
refute the existence of a compatible choice after circuit exchange and does
not settle diagonal two.
"""

from fractions import Fraction
from pathlib import Path
import sys


HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import four_chart_gate as gate
import verify_diag2_moving_witness_shear as moving
import verify_second_diagonal_defect_two as defect


LEFT_SIGNATURE = 50_603_577_668_866_936
RIGHT_SIGNATURE = 36_319_034_736_575_472

LEFT_CIRCUIT = (12, 14, 25, 36, 42)       # 236/246/347/138/258
RIGHT_CIRCUIT = (16, 20, 34, 44, 53)      # 156/127/567/458/478
EXCHANGED_RIGHT_CIRCUIT = (16, 20, 30, 44, 53)  # replace 567 by 167

LEFT_WEIGHTS = (
    6_154_715_944,
    12_264_961_032,
    15_996_634_000,
    26_943_855_000,
    52_114_950_616,
)
RIGHT_WEIGHTS = (
    6_364_432_608,
    4_753_062_630,
    3_883_263_297,
    1_512_222_528,
    2_420_252_970,
)
EXCHANGED_RIGHT_WEIGHTS = (
    5_353_124_400,
    11_321_819_622,
    3_883_263_297,
    1_271_930_400,
    6_687_738_720,
)

# Exact child incidences prove realizability, properness, and reciprocal
# incomparability.  The first eight columns are the parent; column nine is
# the extension point.
LEFT_CHILD = (
    (51, 92, 256, 60, -256, 65, -140, -256, -146),
    (17, 256, 35, -245, 245, -256, -81, -30, -63),
    (1, 152, 119, 256, 182, 107, 212, 125, -256),
    (128, -17, -171, -200, -121, 9, 256, -10, -140),
)
RIGHT_CHILD = (
    (32, 32, 23, 5, 32, -5, 13, 1, -12),
    (9, -7, -6, 14, -23, 32, 16, 2, -24),
    (-18, 8, 32, 32, -18, 6, -11, -29, -1),
    (32, 4, 1, -20, -31, 6, 8, -32, 32),
)
RIGHT_BAD_AT_LEFT = (12, 17, 20, 40, 53)  # 236/256/127/348/478
LEFT_BAD_AT_RIGHT = (12, 14, 25, 36, 51)  # 236/246/347/138/278


def parent_of(child):
    return tuple(tuple(row[:8]) for row in child)


def extension_of(child):
    return tuple(row[8] for row in child)


def endpoint_zero_brackets(source, target, direction, endpoint):
    brackets = moving.parent_brackets(moving.PARENT16)
    parameter = direction * Fraction(*endpoint)
    zeros = []
    for basis, constant in brackets.items():
        if source not in basis or target in basis:
            value = Fraction(constant)
        else:
            sequence = list(basis)
            sequence[sequence.index(source)] = target
            replacement = tuple(sorted(sequence))
            value = (
                constant
                + parameter
                * moving.orientation_sign(sequence)
                * brackets[replacement]
            )
        if value == 0:
            zeros.append(basis)
    return tuple(zeros)


def main():
    catalog = [line.strip() for line in gate.CATALOG_48.open() if line.strip()]
    expected_parent = catalog[16]
    if defect.parent_sign_string(moving.PARENT16) != expected_parent:
        raise AssertionError("base chart is not catalog parent 16")

    if moving.extension_gp_violations(moving.PARENT16, LEFT_SIGNATURE):
        raise AssertionError("left signature violates a GP relation")
    if moving.extension_gp_violations(moving.PARENT16, RIGHT_SIGNATURE):
        raise AssertionError("right signature violates a GP relation")
    if moving.positive_circuit_cofactors(
        moving.PARENT16, LEFT_SIGNATURE, LEFT_CIRCUIT
    ) != LEFT_WEIGHTS:
        raise AssertionError("wrong exact left circuit weights")
    if moving.positive_circuit_cofactors(
        moving.PARENT16, RIGHT_SIGNATURE, RIGHT_CIRCUIT
    ) != RIGHT_WEIGHTS:
        raise AssertionError("wrong exact right circuit weights")
    if not moving.pencil_rigid(LEFT_CIRCUIT, RIGHT_CIRCUIT):
        raise AssertionError("falsifier circuit pair is not pencil-rigid")
    if moving.compatible_shears(
        (LEFT_SIGNATURE, RIGHT_SIGNATURE),
        (LEFT_CIRCUIT, RIGHT_CIRCUIT),
    ):
        raise AssertionError("arbitrary-witness falsifier found a compatible shear")

    left_parent = parent_of(LEFT_CHILD)
    right_parent = parent_of(RIGHT_CHILD)
    if (
        defect.parent_sign_string(left_parent) != expected_parent
        or defect.parent_sign_string(right_parent) != expected_parent
    ):
        raise AssertionError("a child leaves catalog parent 16")
    if defect.extension_signature(
        left_parent, extension_of(LEFT_CHILD)
    ) != LEFT_SIGNATURE:
        raise AssertionError("left exact child realizes the wrong signature")
    if defect.extension_signature(
        right_parent, extension_of(RIGHT_CHILD)
    ) != RIGHT_SIGNATURE:
        raise AssertionError("right exact child realizes the wrong signature")
    moving.positive_circuit_cofactors(
        left_parent, RIGHT_SIGNATURE, RIGHT_BAD_AT_LEFT
    )
    moving.positive_circuit_cofactors(
        right_parent, LEFT_SIGNATURE, LEFT_BAD_AT_RIGHT
    )

    if moving.positive_circuit_cofactors(
        moving.PARENT16, RIGHT_SIGNATURE, EXCHANGED_RIGHT_CIRCUIT
    ) != EXCHANGED_RIGHT_WEIGHTS:
        raise AssertionError("wrong exchanged circuit weights")
    compatible = moving.compatible_shears(
        (LEFT_SIGNATURE, RIGHT_SIGNATURE),
        (LEFT_CIRCUIT, EXCHANGED_RIGHT_CIRCUIT),
    )
    if compatible != ((5, 8, -1, 1),):
        raise AssertionError("circuit exchange has the wrong compatible shear")
    endpoint = moving.first_boundary(
        moving.parent_brackets(moving.PARENT16), 5, 8, -1
    )
    if endpoint != (2132, 4912) or Fraction(*endpoint) != Fraction(533, 1228):
        raise AssertionError("wrong exact shear endpoint")
    if endpoint_zero_brackets(5, 8, -1, endpoint) != ((4, 5, 6, 7),):
        raise AssertionError("shear reaches the wrong first parent wall")

    print("PASS exact realizable proper incomparable GP-valid pair")
    print("PASS strict minimal Q,R have zero compatible elementary shears")
    print("PASS one exchange gives 5->8 direction - and [4567] at 533/1228")
    print("CAVEAT arbitrary-witness compatibility is false; diagonal two remains open")


if __name__ == "__main__":
    main()
