#!/usr/bin/env python3
"""Exact replay of the sign-shattered private-triple contraction theorem.

The theorem is positive but scoped: a simple four-trace condition on three
extension signatures makes every triple of realizing private columns
independent.  Hence contraction by the private triple has no rank-loss
stratum, and retaining all rank-one loop covectors gives a contractible
fiberwise completion.

This verifier checks the condition on the pinned row-2599 triple, performs
two deterministic finite censuses, and reconstructs the complete 928-cell
ambient loop-covector complex of the exact parent.  It does not claim a
triple-bad escape or diagonal-three closure.
"""

from fractions import Fraction
from itertools import combinations
from math import comb, gcd, lcm
from pathlib import Path
import hashlib
import struct
import sys

import numpy as np


HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import DIAG9_GRAPH_exact_topes as exact_topes  # noqa: E402


WIDTH = HERE / "data" / "seeat_parent2599_width7.npz"
SHATTER = HERE / "data" / "seeat_parent2599_shatter8.npz"
WIDTH_SIGNATURE_DIGEST = "6e3b0ff4453e033c5aabf7fe56220922e552e7f1c766c822c9481e71b68eb75d"
SHATTER_SIGNATURE_DIGEST = "e4d7fc781f1e55cbc5dd20fd1a971bef19aec9a79395d6e58c58f6ed410862e9"
PINNED = (0, 3, 6)
EXPECTED_PINNED_ROWS = (28, 25, 0, 40)
EXPECTED_SHATTER_PASS = 52
EXPECTED_WIDTH_PASS = 1_625_014
EXPECTED_WIDTH_FAIL = 125_526
EXPECTED_LOOP_F_VECTOR = (128, 352, 336, 112)


def signature_digest(signatures):
    digest = hashlib.sha256()
    for signature in signatures:
        digest.update(struct.pack("<Q", int(signature)))
    return digest.hexdigest()


def canonical_trace(trace):
    return trace if trace[0] == 1 else tuple(-value for value in trace)


TRACE_CLASSES = (
    (1, 1, 1),
    (1, 1, -1),
    (1, -1, 1),
    (1, -1, -1),
)


def traces(signatures):
    result = {}
    for row in range(56):
        trace = canonical_trace(
            tuple(1 if (signature >> row) & 1 else -1 for signature in signatures)
        )
        result.setdefault(trace, row)
    return result


def raw_trace(signatures, row):
    return tuple(1 if (signature >> row) & 1 else -1 for signature in signatures)


def shatters_antipodal_traces(signatures):
    return all(trace in traces(signatures) for trace in TRACE_CLASSES)


def fast_trace_count(signatures):
    """Count triples whose pairwise XOR masks realize all four traces."""
    mask = (1 << 56) - 1
    passed = 0
    failed = 0
    for first, second, third in combinations(signatures, 3):
        u = int(first) ^ int(second)
        v = int(first) ^ int(third)
        classes = (
            (~u & ~v) & mask,
            (~u & v) & mask,
            (u & ~v) & mask,
            u & v,
        )
        if all(classes):
            passed += 1
        else:
            failed += 1
    return passed, failed


def matrix_rank_and_nullspace(matrix):
    rows = [[Fraction(value) for value in row] for row in matrix]
    if not rows:
        return 0, [
            tuple(Fraction(row == column) for row in range(4))
            for column in range(4)
        ]
    ncolumns = len(rows[0])
    pivot_columns = []
    row = 0
    for column in range(ncolumns):
        pivot = next(
            (other for other in range(row, len(rows)) if rows[other][column]),
            None,
        )
        if pivot is None:
            continue
        rows[row], rows[pivot] = rows[pivot], rows[row]
        scale = rows[row][column]
        rows[row] = [value / scale for value in rows[row]]
        for other in range(len(rows)):
            if other == row or not rows[other][column]:
                continue
            scale = rows[other][column]
            rows[other] = [
                left - scale * right
                for left, right in zip(rows[other], rows[row], strict=True)
            ]
        pivot_columns.append(column)
        row += 1
        if row == len(rows):
            break

    free_columns = [
        column for column in range(ncolumns) if column not in pivot_columns
    ]
    basis = []
    for free in free_columns:
        vector = [Fraction(0) for _ in range(ncolumns)]
        vector[free] = 1
        for pivot_row, pivot_column in enumerate(pivot_columns):
            vector[pivot_column] = -rows[pivot_row][free]
        basis.append(tuple(vector))
    return row, basis


def primitive_fraction_row(row):
    denominator = 1
    for value in row:
        denominator = lcm(denominator, value.denominator)
    integers = [int(value * denominator) for value in row]
    divisor = 0
    for value in integers:
        divisor = gcd(divisor, abs(value))
    if not divisor:
        return tuple(0 for _ in integers)
    return tuple(value // divisor for value in integers)


def parent_columns(parent):
    return tuple(
        tuple(int(parent[row, column]) for row in range(4)) for column in range(8)
    )


def restricted_rows(columns, zero_set):
    rank, basis = matrix_rank_and_nullspace([columns[index] for index in zero_set])
    if rank != len(zero_set) or len(basis) != 4 - len(zero_set):
        raise AssertionError("parent zero set is not independent")
    remaining = [index for index in range(8) if index not in zero_set]
    rows = tuple(
        primitive_fraction_row(
            tuple(
                sum(
                    Fraction(columns[index][coordinate]) * vector[coordinate]
                    for coordinate in range(4)
                )
                for vector in basis
            )
        )
        for index in remaining
    )
    if any(not any(row) for row in rows):
        raise AssertionError("a fourth parent lies on a loop face")
    return remaining, rows


def covector_complex(parent):
    columns = parent_columns(parent)
    # Uniformity also proves that a nonzero contraction covector has at most
    # three loops.
    exact_topes.parent_signs(tuple(tuple(int(value) for value in row) for row in parent))

    by_zero_count = []
    all_covectors = set()
    for zero_count in range(4):
        expected_per_flat = 2 * sum(
            comb(7 - zero_count, degree) for degree in range(4 - zero_count)
        )
        count = 0
        for zero_set in combinations(range(8), zero_count):
            remaining, rows = restricted_rows(columns, zero_set)
            topes = exact_topes.enumerate_topes(rows, dimension=4 - zero_count)
            exact_topes.verify_topes(rows, topes)
            if len(topes) != expected_per_flat:
                raise AssertionError(
                    f"wrong restricted tope count at {zero_set}: {len(topes)}"
                )
            for bits in topes:
                signs = [0] * 8
                for local, parent_index in enumerate(remaining):
                    signs[parent_index] = 1 if bits & (1 << local) else -1
                covector = tuple(signs)
                if covector in all_covectors:
                    raise AssertionError("duplicate loop covector")
                all_covectors.add(covector)
            count += len(topes)
        by_zero_count.append(count)

    if tuple(by_zero_count) != EXPECTED_LOOP_F_VECTOR:
        raise AssertionError(f"loop covector f-vector changed: {by_zero_count}")
    if len(all_covectors) != sum(EXPECTED_LOOP_F_VECTOR):
        raise AssertionError("wrong total loop covector count")

    topes = {covector for covector in all_covectors if 0 not in covector}
    facets = {covector for covector in all_covectors if covector.count(0) == 1}
    adjacency = {tope: set() for tope in topes}
    for facet in facets:
        zero = facet.index(0)
        sides = []
        for sign in (-1, 1):
            side = list(facet)
            side[zero] = sign
            side = tuple(side)
            if side not in topes:
                raise AssertionError("loop facet does not have two tope sides")
            sides.append(side)
        adjacency[sides[0]].add(sides[1])
        adjacency[sides[1]].add(sides[0])

    seen = set()
    stack = [next(iter(topes))]
    while stack:
        current = stack.pop()
        if current in seen:
            continue
        seen.add(current)
        stack.extend(adjacency[current] - seen)
    if seen != topes:
        raise AssertionError("loop-complete tope adjacency graph is disconnected")
    if sum(len(neighbors) for neighbors in adjacency.values()) // 2 != len(facets):
        raise AssertionError("wrong loop-facet adjacency count")
    return tuple(by_zero_count), len(facets)


def verify_realizing_points(parent, signatures, stored_points):
    rows = exact_topes.derived_rows(
        tuple(tuple(int(value) for value in row) for row in parent),
        normalize=False,
    )
    minima = []
    for signature, stored in zip(signatures, stored_points, strict=True):
        point = tuple(Fraction(str(value)) for value in stored)
        signed = []
        for index, row in enumerate(rows):
            value = sum(
                Fraction(coefficient) * coordinate
                for coefficient, coordinate in zip(row, point, strict=True)
            )
            if not (signature >> index) & 1:
                value = -value
            signed.append(value)
        if min(signed) <= 0:
            raise AssertionError("stored pinned private point is not strict")
        minima.append(min(signed))
    return tuple(minima)


def main():
    with np.load(SHATTER) as data:
        if str(data["format"].item()) != "seeat-parent2599-shatter8-v1":
            raise AssertionError("wrong shatter certificate format")
        shatter_signatures = tuple(int(value) for value in data["signature"])
        parent = data["pattern_chart"][255]
        stored_points = tuple(data["feasible_point"][255, index] for index in PINNED)
    if signature_digest(shatter_signatures) != SHATTER_SIGNATURE_DIGEST:
        raise AssertionError("shatter signature digest changed")

    pinned_signatures = tuple(shatter_signatures[index] for index in PINNED)
    point_minima = verify_realizing_points(parent, pinned_signatures, stored_points)
    if not shatters_antipodal_traces(pinned_signatures):
        raise AssertionError("pinned triple lost an antipodal trace class")
    # Pin positive-first representatives when they occur; the theorem would
    # equally allow their simultaneous negatives.
    rows = tuple(
        next(
            row
            for row in range(56)
            if raw_trace(pinned_signatures, row) == trace
        )
        for trace in TRACE_CLASSES
    )
    if rows != EXPECTED_PINNED_ROWS:
        raise AssertionError(f"pinned trace witnesses changed: {rows}")
    triple_rows = tuple(
        tuple(label + 1 for label in exact_topes.TRIPLES[row]) for row in rows
    )

    shatter_pass, shatter_fail = fast_trace_count(shatter_signatures)
    if (shatter_pass, shatter_fail) != (
        EXPECTED_SHATTER_PASS,
        comb(len(shatter_signatures), 3) - EXPECTED_SHATTER_PASS,
    ):
        raise AssertionError("shatter-eight trace census changed")

    with np.load(WIDTH) as data:
        if str(data["format"].item()) != "seeat-parent2599-width7-v1":
            raise AssertionError("wrong width certificate format")
        width_signatures = tuple(int(value) for value in data["vertex_signature"])
    if signature_digest(width_signatures) != WIDTH_SIGNATURE_DIGEST:
        raise AssertionError("width signature digest changed")
    width_pass, width_fail = fast_trace_count(width_signatures)
    if (width_pass, width_fail) != (EXPECTED_WIDTH_PASS, EXPECTED_WIDTH_FAIL):
        raise AssertionError("220-signature trace census changed")

    f_vector, facet_count = covector_complex(parent)

    print("PASS: pinned signatures", PINNED, "hit all four antipodal trace classes")
    print("PASS: colex witness rows", rows, "are parent triples", triple_rows)
    print("PASS: pinned exact private points have signed minima", point_minima)
    print("THEOREM: every realizing private triple for these signatures is independent")
    print("PASS: shatter-eight trace-safe triples", shatter_pass, "/", shatter_pass + shatter_fail)
    print("PASS: 220-signature trace-safe triples", width_pass, "/", width_pass + width_fail)
    print("PASS: complete uniform rank-one loop-covector f-vector", f_vector)
    print("PASS: all", facet_count, "one-loop faces connect the 128-tope adjacency graph")
    print("SCOPE: contractible private-good loop completion; no triple-bad or parent-infinity escape")


if __name__ == "__main__":
    main()
