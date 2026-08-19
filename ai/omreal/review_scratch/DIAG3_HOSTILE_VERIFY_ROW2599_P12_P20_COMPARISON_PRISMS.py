#!/usr/bin/env python3
"""Independent dense replay of the row-2599 p12/p20 prisms."""

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

import DIAG3_HOSTILE_VERIFY_ROW2599_P01_COMPARISON_PRISM as dense  # noqa: E402
import verify_diag2_moving_witness_shear as moving  # noqa: E402


SOURCE = dense.SOURCE
SOURCE_SHA256 = dense.SOURCE_SHA256
ROOTS = ((2, 8, -1), (1, 2, -1), (1, 3, 1))
ENDPOINTS = (
    Fraction(1_221_971_981, 1_769_366_234),
    Fraction(42_214_994, 2_183_619_501),
    Fraction(425_791_163, 1_286_992_887),
)
BLOCKS = {1: (1, 2), 2: (2, 0)}
NAMES = {1: "p12", 2: "p20"}
EXPECTED_SEMANTIC = "930d28e2fbc1990cb68e403b034b3ec7aa440a455b5017a13aa1426e1336dba4"


def root_matrix(raw, root_index, common_parameter, root_parameter):
    matrix = dense.base_matrix(raw)
    for row in range(4):
        matrix[row][dense.COMMON_COLUMN] = dense.add(
            matrix[row][dense.COMMON_COLUMN],
            dense.scale(
                common_parameter,
                dense.COMMON_ENDPOINT * dense.COMMON_DIRECTION[row],
            ),
        )
    source, destination, sign = ROOTS[root_index]
    for row in range(4):
        matrix[row][source - 1] = dense.add(
            matrix[row][source - 1],
            dense.scale(
                dense.multiply(root_parameter, matrix[row][destination - 1]),
                sign,
            ),
        )
    return matrix


def relative(raw, root_index):
    endpoint = ENDPOINTS[root_index]
    stage0 = root_matrix(raw, root_index, dense.U, dense.constant(endpoint))
    stage1 = root_matrix(
        raw,
        root_index,
        dense.constant(1),
        dense.scale(dense.add(dense.constant(1), dense.scale(dense.U, -1)), endpoint),
    )
    return stage0, stage1


def original(raw, root_index, index):
    parameter = dense.add(dense.constant(Fraction(index, 2)), dense.scale(dense.U, Fraction(1, 2)))
    root_parameter = dense.scale(
        dense.add(dense.constant(1), dense.scale(parameter, -1)),
        ENDPOINTS[root_index],
    )
    return root_matrix(raw, root_index, parameter, root_parameter)


def certify(name, matrix, blocks, base_brackets, digest):
    weak_parent, weak_circuit = [], []
    for basis in moving.BASES4:
        label = "".join(map(str, basis))
        signed = dense.scale(dense.bracket(matrix, basis), 1 if base_brackets[basis] > 0 else -1)
        values = dense.bernstein(signed)
        if min(values) < 0:
            raise AssertionError(f"{name}: dense parent sign failure [{label}]")
        if min(values) == 0:
            weak_parent.append(label)
        digest.update(repr((name, "P", label, tuple(sorted(signed.items())))).encode("ascii"))
    for block in blocks:
        strict = 0
        for position, polynomial in enumerate(dense.circuit(matrix, block)):
            values = dense.bernstein(polynomial)
            if min(values) < 0:
                raise AssertionError(f"{name}: dense block-{block} circuit sign failure")
            if min(values) == 0:
                weak_circuit.append((block, position))
            else:
                strict += 1
            digest.update(repr((name, "C", block, position, tuple(sorted(polynomial.items())))).encode("ascii"))
        if not strict:
            raise AssertionError(f"{name}: dense block-{block} circuit could vanish")
    return name, tuple(weak_parent), tuple(weak_circuit)


def replay(raw, root_index, base_brackets, digest):
    name = NAMES[root_index]
    relatives = relative(raw, root_index)
    originals = tuple(original(raw, root_index, index) for index in range(2))
    patches = tuple(dense.interpolate(left, right) for left, right in zip(originals, relatives, strict=True))
    if not dense.matrix_equal(dense.matrix_restrict(patches[0], 0, 1), dense.matrix_restrict(patches[1], 0, 0)):
        raise AssertionError(f"{name}: dense internal seam changed")
    for patch, source in zip(patches, originals, strict=True):
        if not dense.matrix_equal(dense.matrix_restrict(patch, 1, 0), source):
            raise AssertionError(f"{name}: dense v=0 face changed")
        relative_face = dense.matrix_restrict(patch, 1, 1)
        if not any(not dense.bracket(relative_face, basis) for basis in moving.BASES4):
            raise AssertionError(f"{name}: dense relative face lost its wall")
    for u_value, patch in ((0, patches[0]), (1, patches[1])):
        face = dense.matrix_restrict(patch, 0, u_value)
        if not dense.matrix_equal(dense.matrix_restrict(face, 1, 0), dense.matrix_restrict(face, 1, 1)):
            raise AssertionError(f"{name}: dense endpoint face did not collapse")
    reports = tuple(
        certify(f"{name}-patch-{index}", patch, BLOCKS[root_index], base_brackets, digest)
        for index, patch in enumerate(patches)
    )
    boundary = {
        f"K({name})": 1,
        f"Q({name},block{BLOCKS[root_index][0]})": -1,
        f"Q({name},block{BLOCKS[root_index][1]})": 1,
    }
    return name, reports, boundary


def main():
    if sha256(SOURCE.read_bytes()).hexdigest() != SOURCE_SHA256:
        raise AssertionError("row2599 source SHA changed")
    with np.load(SOURCE, allow_pickle=False) as source:
        raw = source["chart_matrix"][0]
    base_brackets = moving.parent_brackets(raw)
    digest = sha256(b"diag3-hostile-dense-p12-p20-comparison-prisms-v1\0")
    reports = tuple(replay(raw, root_index, base_brackets, digest) for root_index in (1, 2))
    digest.update(repr(reports).encode("ascii"))
    semantic = digest.hexdigest()
    if EXPECTED_SEMANTIC != "TO_BE_PINNED" and semantic != EXPECTED_SEMANTIC:
        raise AssertionError(f"dense p12/p20 semantic changed: {semantic}")
    print("PASS independent dense p12/p20 comparison prisms", reports)
    print("SEMANTIC", semantic)
    print("SCOPE pair-edge comparison count 3/6; singleton prisms and mixed J remain open")


if __name__ == "__main__":
    main()
