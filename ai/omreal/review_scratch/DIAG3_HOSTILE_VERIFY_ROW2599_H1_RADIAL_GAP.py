#!/usr/bin/env python3
"""Independent exact replay of the row-2599 H1 radial obstruction."""

from __future__ import annotations

from fractions import Fraction
from hashlib import sha256
from pathlib import Path
import sys

import numpy as np


HERE = Path(__file__).resolve().parent
OMREAL = HERE.parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(OMREAL))

import DIAG3_HOSTILE_VERIFY_ROW2599_H2_COMPARISON_PRISM as dense  # noqa: E402
import verify_diag2_moving_witness_shear as moving  # noqa: E402
import verify_diag3_joined_flow_triangle as joined  # noqa: E402


SUPPORT = (2, 9, 27, 30, 35)
EXPECTED_SEMANTIC = "7f8b7ac35c9f6a7e5580ec40ccde6140b95814ac6a25b2051fb83f01a603eee7"


def two_root_matrix(raw, common_parameter, first, second):
    matrix = dense.base_matrix(raw)
    dense.common_move(matrix, common_parameter)
    dense.apply_root(matrix, 0, first)
    dense.apply_root(matrix, 1, second)
    return matrix


def root_values(edge):
    if edge == 0:
        return dense.constant(dense.ENDPOINTS[0]), dense.scale(
            dense.R, dense.ENDPOINTS[1]
        )
    if edge == 1:
        return (
            dense.scale(
                dense.add(dense.constant(1), dense.scale(dense.R, -1)),
                dense.ENDPOINTS[0],
            ),
            dense.constant(dense.ENDPOINTS[1]),
        )
    raise AssertionError(edge)


def relative(raw, edge, stage):
    first, second = root_values(edge)
    if stage == 0:
        return two_root_matrix(raw, dense.U, first, second)
    if stage == 1:
        taper = dense.add(dense.constant(1), dense.scale(dense.U, -1))
        return two_root_matrix(
            raw,
            dense.constant(1),
            dense.multiply(taper, first),
            dense.multiply(taper, second),
        )
    raise AssertionError(stage)


def original(raw, edge, stage):
    parameter = dense.add(
        dense.constant(Fraction(stage, 2)), dense.scale(dense.U, Fraction(1, 2))
    )
    taper = dense.add(dense.constant(1), dense.scale(parameter, -1))
    first, second = root_values(edge)
    return two_root_matrix(
        raw,
        parameter,
        dense.multiply(taper, first),
        dense.multiply(taper, second),
    )


def pair_patch(raw, root_index, stage):
    endpoint = dense.ENDPOINTS[root_index]
    parameter = dense.add(
        dense.constant(Fraction(stage, 2)), dense.scale(dense.U, Fraction(1, 2))
    )
    source = dense.single_root_matrix(
        raw,
        root_index,
        parameter,
        dense.scale(dense.add(dense.constant(1), dense.scale(parameter, -1)), endpoint),
    )
    if stage == 0:
        target = dense.single_root_matrix(
            raw, root_index, dense.U, dense.constant(endpoint)
        )
    else:
        target = dense.single_root_matrix(
            raw,
            root_index,
            dense.constant(1),
            dense.scale(
                dense.add(dense.constant(1), dense.scale(dense.U, -1)), endpoint
            ),
        )
    return dense.interpolate(source, target)


def circuit(matrix):
    all_normals = dense.normals(matrix)
    columns = tuple(
        tuple(
            dense.scale(
                value, moving.signature_sign(joined.SIGNATURES[1], index)
            )
            for value in all_normals[index]
        )
        for index in SUPPORT
    )
    coefficients = []
    for omitted in range(5):
        retained = [
            column for position, column in enumerate(columns) if position != omitted
        ]
        value = dense.determinant(
            [[retained[column][row] for column in range(4)] for row in range(4)]
        )
        coefficients.append(value if not omitted & 1 else dense.scale(value, -1))
    anchor = next(
        dense.evaluate(item, (Fraction(1, 2),) * 3)
        for item in coefficients
        if dense.evaluate(item, (Fraction(1, 2),) * 3)
    )
    sign = 1 if anchor > 0 else -1
    coefficients = tuple(dense.scale(item, sign) for item in coefficients)
    for coordinate in range(4):
        total = {}
        for index, coefficient in zip(SUPPORT, coefficients, strict=True):
            total = dense.add(
                total,
                dense.scale(
                    dense.multiply(coefficient, all_normals[index][coordinate]),
                    moving.signature_sign(joined.SIGNATURES[1], index),
                ),
            )
        if total:
            raise AssertionError("independent H1 cofactor kernel failed")
    return coefficients


def certify(name, matrix, base_brackets, digest):
    weak_parent = []
    for basis in moving.BASES4:
        label = "".join(map(str, basis))
        signed = dense.scale(
            dense.bracket(matrix, basis),
            1 if base_brackets[basis] > 0 else -1,
        )
        values = dense.bernstein(signed)
        if min(values) < 0:
            raise AssertionError(f"{name}: independent parent sign failure [{label}]")
        if min(values) == 0:
            weak_parent.append(label)
        digest.update(
            repr((name, "P", label, tuple(sorted(signed.items())))).encode("ascii")
        )
    weak_circuit = []
    strict = 0
    for position, polynomial in enumerate(circuit(matrix)):
        values = dense.bernstein(polynomial)
        if min(values) < 0:
            raise AssertionError(f"{name}: independent block-1 circuit failure")
        if min(values) == 0:
            weak_circuit.append(position)
        else:
            strict += 1
        digest.update(
            repr((name, "C", position, tuple(sorted(polynomial.items())))).encode(
                "ascii"
            )
        )
    if not strict:
        raise AssertionError(f"{name}: independent circuit could vanish")
    return name, tuple(weak_parent), tuple(weak_circuit)


def zero_walls(matrix):
    return tuple(
        "".join(map(str, basis))
        for basis in moving.BASES4
        if not dense.bracket(matrix, basis)
    )


def main():
    if sha256(dense.SOURCE.read_bytes()).hexdigest() != dense.SOURCE_SHA256:
        raise AssertionError("row2599 source SHA changed")
    with np.load(dense.SOURCE, allow_pickle=False) as source:
        raw = source["chart_matrix"][0]
    base_brackets = moving.parent_brackets(raw)
    patches = tuple(
        tuple(
            dense.interpolate(original(raw, edge, stage), relative(raw, edge, stage))
            for stage in range(2)
        )
        for edge in range(2)
    )
    for edge in range(2):
        if not dense.matrix_equal(
            dense.matrix_restrict(patches[edge][0], 0, 1),
            dense.matrix_restrict(patches[edge][1], 0, 0),
        ):
            raise AssertionError("independent H1 u seam changed")
    for stage in range(2):
        if not dense.matrix_equal(
            dense.matrix_restrict(patches[0][stage], 1, 1),
            dense.matrix_restrict(patches[1][stage], 1, 0),
        ):
            raise AssertionError("independent H1 frontier seam changed")
        if not dense.matrix_equal(
            dense.matrix_restrict(patches[0][stage], 1, 0),
            pair_patch(raw, 0, stage),
        ):
            raise AssertionError("independent H1/generic-p01 lateral mismatch")
        if not dense.matrix_equal(
            dense.matrix_restrict(patches[1][stage], 1, 1),
            pair_patch(raw, 1, stage),
        ):
            raise AssertionError("independent H1/p12 lateral mismatch")

    radial_walls = tuple(zero_walls(relative(raw, 0, stage)) for stage in range(2))
    if radial_walls != (("1234",), ()):
        raise AssertionError(f"independent radial wall census changed: {radial_walls}")
    digest = sha256(b"diag3-hostile-independent-h1-radial-gap-v1\0")
    reports = tuple(
        certify(
            f"h1-edge-{edge}-stage-{stage}",
            patches[edge][stage],
            base_brackets,
            digest,
        )
        for edge in range(2)
        for stage in range(2)
    )
    digest.update(repr((reports, radial_walls)).encode("ascii"))
    semantic = digest.hexdigest()
    if EXPECTED_SEMANTIC != "TO_BE_PINNED" and semantic != EXPECTED_SEMANTIC:
        raise AssertionError(f"independent H1-gap semantic changed: {semantic}")
    print("PASS independent H1 radial-screen patches", reports)
    print("PASS independent radial p01 wall census", radial_walls)
    print("SEMANTIC", semantic)
    print("NO-GO second radial p01 stage is not relative")
    print("LEDGER comparison count remains 4/6; theorem score remains 2/9")


if __name__ == "__main__":
    main()
