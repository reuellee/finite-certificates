#!/usr/bin/env python3
"""Exact local joined flow-triangle certificate for diagonal three.

This checker pins a row-2599 triple of GP-valid bad signatures with no
common elementary escape root.  Three pairwise roots and three singleton
ordered two-root carriers nevertheless give the integral relative flow-disk
two-skeleton described in ``DIAG3_JOINED_FLOW_TRIANGLE.md``.  Its primitive
``H2`` relation is the still-missing boundary of a relative three-cell.

The statement is local to one exact parent chart.  It is not a coverage or
specialization theorem and does not prove the third diagonal.
"""

from itertools import combinations
from pathlib import Path
import sys

import numpy as np


HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import DIAG9_GRAPH_exact_topes as exact_topes  # noqa: E402
import verify_diag2_escape_set_topes as escape  # noqa: E402
import verify_diag2_moving_witness_shear as moving  # noqa: E402
import verify_diag3_ordered_root_atlas178 as ordered  # noqa: E402


ATLAS = HERE / "data" / "seeat_parent2599_upper178.npz"
SIGNATURES = (
    14_988_895_318_912,
    3_405_195_891_438_080,
    40_418_075_143_643_136,
)
PAIR_ROOTS = (
    (2, 8, -1),
    (1, 2, -1),
    (1, 3, +1),
)
EXPECTED_ROOT_INDICES = (26, 0, 3)
EXPECTED_ESCAPE_SIZES = (56, 56, 60)


def determinant(matrix):
    """Exact Bareiss determinant of a square integer matrix."""
    work = [list(map(int, row)) for row in matrix]
    size = len(work)
    if any(len(row) != size for row in work):
        raise ValueError("determinant expects a square matrix")
    if size == 0:
        return 1
    sign = 1
    previous = 1
    for column in range(size - 1):
        pivot = next(
            (row for row in range(column, size) if work[row][column]),
            None,
        )
        if pivot is None:
            return 0
        if pivot != column:
            work[column], work[pivot] = work[pivot], work[column]
            sign = -sign
        value = work[column][column]
        for row in range(column + 1, size):
            for target in range(column + 1, size):
                numerator = (
                    work[row][target] * value
                    - work[row][column] * work[column][target]
                )
                if numerator % previous:
                    raise AssertionError("Bareiss division was not exact")
                work[row][target] = numerator // previous
        previous = value
    return sign * work[-1][-1]


def rank(matrix):
    """Rational rank certified by nonzero integer minors."""
    rows = len(matrix)
    columns = len(matrix[0]) if rows else 0
    for size in range(min(rows, columns), 0, -1):
        for selected_rows in combinations(range(rows), size):
            for selected_columns in combinations(range(columns), size):
                minor = [
                    [matrix[row][column] for column in selected_columns]
                    for row in selected_rows
                ]
                if determinant(minor):
                    return size
    return 0


def transpose(columns):
    return [list(row) for row in zip(*columns, strict=True)]


def multiply(left, right):
    return [
        [
            sum(left[row][middle] * right[middle][column]
                for middle in range(len(right)))
            for column in range(len(right[0]))
        ]
        for row in range(len(left))
    ]


def verify_relative_complex():
    boundary_1 = [
        [-1, 0, +1, -1, 0, 0, 0, 0, -1],
        [+1, -1, 0, 0, -1, -1, 0, 0, 0],
        [0, +1, -1, 0, 0, 0, -1, -1, 0],
    ]
    # Column order: T,S01,S12,S20,H0,H1,H2.  Row order is the C1 order
    # used in DIAG3_JOINED_FLOW_TRIANGLE.md.
    boundary_2_columns = [
        [+1, +1, +1, 0, 0, 0, 0, 0, 0],
        [+1, 0, 0, -1, +1, 0, 0, 0, 0],
        [0, +1, 0, 0, 0, -1, +1, 0, 0],
        [0, 0, +1, 0, 0, 0, 0, -1, +1],
        [0, 0, 0, +1, 0, 0, 0, 0, -1],
        [0, 0, 0, 0, -1, +1, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, -1, +1, 0],
    ]
    boundary_2 = transpose(boundary_2_columns)
    if multiply(boundary_1, boundary_2) != [[0] * 7 for _ in range(3)]:
        raise AssertionError("relative boundary does not square to zero")
    if rank(boundary_1) != 3 or rank(boundary_2) != 6:
        raise AssertionError("wrong relative boundary ranks")

    # One unit maximal minor proves that all six nonzero Smith invariants
    # are units; the rank equality then gives integral H1=0.
    unit_minor = False
    for selected_rows in combinations(range(9), 6):
        for selected_columns in combinations(range(7), 6):
            minor = [
                [boundary_2[row][column] for column in selected_columns]
                for row in selected_rows
            ]
            if abs(determinant(minor)) == 1:
                unit_minor = True
                break
        if unit_minor:
            break
    if not unit_minor:
        raise AssertionError("relative boundary has no unit maximal minor")

    top_relation = (-1, +1, +1, +1, +1, +1, +1)
    if any(
        sum(boundary_2[row][column] * top_relation[column]
            for column in range(7))
        for row in range(9)
    ):
        raise AssertionError("wrong fundamental flow-disk relation")
    # This is the exact hypothetical C3 -> C2 column required geometrically.
    # Its unit T coefficient makes the primitive H2 generator a boundary.
    if abs(top_relation[0]) != 1:
        raise AssertionError("the required d3 attachment is not primitive")
    print("PASS integral flow-disk two-skeleton: H0=H1=0 and H2=Z")
    print("MISSING geometric d3 column", top_relation)


def main():
    with np.load(ATLAS, allow_pickle=False) as source:
        matrix = source["chart_matrix"][0]

    # Check the three sign strings directly against the exact parent, rather
    # than trusting their provenance in a catalog enumeration.
    for signature in SIGNATURES:
        if moving.extension_gp_violations(matrix, signature):
            raise AssertionError("a pinned signature violates a GP relation")

    rows = exact_topes.derived_rows(matrix)
    enumerated = exact_topes.enumerate_topes(rows, dimension=4)
    exact_topes.verify_topes(rows, enumerated)
    topes = tuple(enumerated)
    if len(topes) != 26_112:
        raise AssertionError("wrong complete derived-tope count")
    if any(signature in enumerated for signature in SIGNATURES):
        raise AssertionError("a pinned signature is not bad at chart zero")

    prepared = escape.prepare_directions(topes)
    masks = tuple(
        escape.escape_mask(signature, prepared)
        for signature in SIGNATURES
    )
    if tuple(mask.bit_count() for mask in masks) != EXPECTED_ESCAPE_SIZES:
        raise AssertionError("escape-set sizes changed")
    if masks[0] & masks[1] & masks[2]:
        raise AssertionError("the no-common-root canary acquired a common root")

    root_indices = tuple(escape.DIRECTION_INDEX[root] for root in PAIR_ROOTS)
    if root_indices != EXPECTED_ROOT_INDICES:
        raise AssertionError("ordered root indexing changed")
    for pair_index, (left, right) in enumerate(((0, 1), (1, 2), (2, 0))):
        root_index = root_indices[pair_index]
        if not all((masks[block] >> root_index) & 1 for block in (left, right)):
            raise AssertionError("a displayed pair root is not common")

    # The Section-5 Cech cocycle uses phi=0 on E0 cap E1 and phi=1 on
    # E1 cap E2.  Its value on d01 -> d12 is one, while the other two
    # root-loop edges lie in K2 and K0 where the cochain is zero.
    d01, d12, _d20 = root_indices
    phi_d01 = int(bool((masks[2] >> d01) & 1))
    phi_d12 = int(bool((masks[2] >> d12) & 1))
    if (phi_d01, phi_d12, phi_d12 - phi_d01) != (0, 1, 1):
        raise AssertionError("the singleton-root nerve cocycle changed")

    # At block 0 use roots d01,d20; at block 1 use d01,d12; at block 2
    # use d12,d20.  One common order is enough.  Block 1 is the asymmetric
    # order-sensitive regression.
    incident_pairs = ((0, 2), (0, 1), (1, 2))
    order_truth = []
    for block, (first, second) in enumerate(incident_pairs):
        forward = ordered.order_works(
            (SIGNATURES[block],),
            root_indices[first],
            root_indices[second],
            topes,
        )
        reverse = ordered.order_works(
            (SIGNATURES[block],),
            root_indices[second],
            root_indices[first],
            topes,
        )
        if not (forward or reverse):
            raise AssertionError("a singleton sector has no ordered carrier")
        order_truth.append((forward, reverse))
    if tuple(order_truth) != ((True, True), (True, False), (True, True)):
        raise AssertionError("ordered sector truth table changed")

    print("PASS three GP-valid bad signatures have escape sizes 56/56/60")
    print("PASS their elementary escape sets have empty triple intersection")
    print("PASS three pair roots and singleton ordered sectors fill the triangle")
    print("PASS integral nerve cocycle evaluates one on the root-choice loop")
    print("ORDER_TRUTH", tuple(order_truth))
    verify_relative_complex()
    print("SCOPE exact local carrier only; no coverage or specialization theorem")


if __name__ == "__main__":
    main()
