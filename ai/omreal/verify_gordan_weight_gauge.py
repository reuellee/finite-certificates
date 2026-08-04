#!/usr/bin/env python3
"""Exact weight-gauge check for the row-2599 pencil-rigid residue.

For circuit supports Q_j, positive rescaling of the eight parent columns acts
linearly on logarithmic Gordan-weight ratios.  The action matrix has one row

    1_I - 1_{I_0}

for every non-base triple I in every support.  Hence the number of
torus-invariant positive weight moduli is

    beta = sum_j (|Q_j|-1) - rank_Q(D).

This checker verifies that statement's integer linear algebra on every
pencil-rigid pair of stored positive circuits in the exact row-2599
eight-shatter certificate.  It also constructs primitive integer exponent
vectors for the invariant monomials.  Across all 256 stored charts, the exact
sample has 65 pencil-rigid pair occurrences: three 4+5 occurrences have
beta=0, while 58 and four 5+5 occurrences have beta=1 and beta=2,
respectively.  There are 55 distinct unordered support pairs.

This is a finite exact sample, not a universal census of support pairs.  The
weight gauge applies to relative interiors of weight-simplex faces; zero
weights are handled by passing to the corresponding smaller support.
"""

from fractions import Fraction
from itertools import combinations
from math import gcd
from pathlib import Path
import sys

import numpy as np


HERE = Path(__file__).resolve().parent
CERTIFICATE = HERE / "data" / "seeat_parent2599_shatter8.npz"
sys.path.insert(0, str(HERE))

import prototype_koszul_circuits as koszul  # noqa: E402


TRIPLES = koszul.TRIPLES


def support(weights):
    return tuple(index for index, value in enumerate(weights) if int(value))


def pencil_rigid(first, second):
    union = set(first) | set(second)
    degrees = {
        vertex: sum(vertex in TRIPLES[index] for index in union)
        for vertex in range(1, 9)
    }
    if min(degrees.values()) < 3:
        return False
    for vertex in range(1, 9):
        incident = [index for index in union if vertex in TRIPLES[index]]
        for partner in range(1, 9):
            if partner == vertex:
                continue
            if all(partner in TRIPLES[index] for index in incident):
                return False
    return True


def incidence_vector(index):
    triple = TRIPLES[index]
    return tuple(int(vertex in triple) for vertex in range(1, 9))


def gauge_matrix(supports):
    rows = []
    labels = []
    for block, current in enumerate(supports):
        base = incidence_vector(current[0])
        for index in current[1:]:
            rows.append(
                tuple(value - origin for value, origin in zip(
                    incidence_vector(index), base, strict=True
                ))
            )
            labels.append((block, index))
    return rows, labels


def rref(matrix):
    rows = [[Fraction(value) for value in row] for row in matrix]
    if not rows:
        return rows, ()
    pivot_columns = []
    pivot_row = 0
    for column in range(len(rows[0])):
        pivot = next(
            (row for row in range(pivot_row, len(rows)) if rows[row][column]),
            None,
        )
        if pivot is None:
            continue
        rows[pivot_row], rows[pivot] = rows[pivot], rows[pivot_row]
        scale = rows[pivot_row][column]
        rows[pivot_row] = [value / scale for value in rows[pivot_row]]
        for row in range(len(rows)):
            if row == pivot_row or not rows[row][column]:
                continue
            scale = rows[row][column]
            rows[row] = [
                left - scale * right
                for left, right in zip(rows[row], rows[pivot_row], strict=True)
            ]
        pivot_columns.append(column)
        pivot_row += 1
        if pivot_row == len(rows):
            break
    return rows, tuple(pivot_columns)


def rank(matrix):
    return len(rref(matrix)[1])


def transpose(matrix):
    return [list(column) for column in zip(*matrix, strict=True)]


def lcm(left, right):
    return abs(left * right) // gcd(left, right) if left and right else 0


def primitive_integer(vector):
    denominator = 1
    for value in vector:
        denominator = lcm(denominator, value.denominator)
    result = [int(value * denominator) for value in vector]
    divisor = 0
    for value in result:
        divisor = gcd(divisor, abs(value))
    result = [value // divisor for value in result]
    first = next(value for value in result if value)
    if first < 0:
        result = [-value for value in result]
    return tuple(result)


def nullspace(matrix):
    reduced, pivots = rref(matrix)
    columns = len(matrix[0]) if matrix else 0
    free_columns = [column for column in range(columns) if column not in pivots]
    basis = []
    for free in free_columns:
        vector = [Fraction(0) for _ in range(columns)]
        vector[free] = 1
        for row, pivot in enumerate(pivots):
            vector[pivot] = -reduced[row][free]
        basis.append(primitive_integer(vector))
    return tuple(basis)


def full_block_exponents(supports, ratio_exponents):
    result = []
    offset = 0
    for current in supports:
        tail = ratio_exponents[offset : offset + len(current) - 1]
        offset += len(current) - 1
        result.append((-sum(tail),) + tuple(tail))
    assert offset == len(ratio_exponents)
    return tuple(result)


def verify_balanced(supports, block_exponents):
    for exponents in block_exponents:
        assert sum(exponents) == 0
    vertex_balance = [0] * 8
    for current, exponents in zip(supports, block_exponents, strict=True):
        for index, exponent in zip(current, exponents, strict=True):
            for vertex in TRIPLES[index]:
                vertex_balance[vertex - 1] += exponent
    assert vertex_balance == [0] * 8


def verify_positive_circuit(certificate, pattern, bit, current, normals):
    signature = int(certificate["signature"][bit])
    columns = [
        tuple(
            coefficient if (signature >> index) & 1 else -coefficient
            for coefficient in normals[index]
        )
        for index in current
    ]
    coefficients = [
        int(certificate["gordan_weight"][pattern, bit, index])
        for index in current
    ]
    if not all(value > 0 for value in coefficients):
        raise AssertionError("stored support coefficient is not positive")
    if any(
        sum(value * column[coordinate] for value, column in zip(
            coefficients, columns, strict=True
        ))
        for coordinate in range(4)
    ):
        raise AssertionError("stored positive dependence is not exact")
    expected_rank = len(current) - 1
    if koszul.matrix_rank(columns) != expected_rank:
        raise AssertionError("stored dependence has the wrong total rank")
    if any(
        koszul.matrix_rank([columns[index] for index in subset]) != expected_rank
        for subset in combinations(range(len(current)), expected_rank)
    ):
        raise AssertionError("stored positive dependence is not support-minimal")


def main():
    certificate = np.load(CERTIFICATE, allow_pickle=False)
    if int(certificate["parent_index"].item()) != 2599:
        raise AssertionError("wrong parent certificate")

    records = []
    checked_circuits = set()
    normal_cache = {}
    for pattern in range(256):
        bad = [bit for bit in range(8) if not ((pattern >> bit) & 1)]
        supports = {
            bit: support(certificate["gordan_weight"][pattern, bit])
            for bit in bad
        }
        for left_index, left in enumerate(bad):
            for right in bad[left_index + 1 :]:
                pair = (supports[left], supports[right])
                sizes = tuple(sorted(map(len, pair)))
                if sizes not in ((4, 5), (5, 5)) or not pencil_rigid(*pair):
                    continue
                if pattern not in normal_cache:
                    normal_cache[pattern] = koszul.parent_normals(
                        certificate["pattern_chart"][pattern]
                    )
                for bit, current in ((left, pair[0]), (right, pair[1])):
                    if (pattern, bit) not in checked_circuits:
                        verify_positive_circuit(
                            certificate,
                            pattern,
                            bit,
                            current,
                            normal_cache[pattern],
                        )
                        checked_circuits.add((pattern, bit))
                matrix, _ = gauge_matrix(pair)
                matrix_rank = rank(matrix)
                beta = len(matrix) - matrix_rank
                invariants = nullspace(transpose(matrix))
                if len(invariants) != beta:
                    raise AssertionError("wrong invariant-space dimension")
                expanded = tuple(
                    full_block_exponents(pair, invariant)
                    for invariant in invariants
                )
                for block_exponents in expanded:
                    verify_balanced(pair, block_exponents)
                records.append(
                    (pattern, left, right, sizes, matrix_rank, beta, expanded)
                )

    if len(records) != 65:
        raise AssertionError(f"expected 65 pencil-rigid pairs, got {len(records)}")
    distribution = {}
    for _, _, _, sizes, _, beta, _ in records:
        distribution[sizes, beta] = distribution.get((sizes, beta), 0) + 1
    expected = {((4, 5), 0): 3, ((5, 5), 1): 58, ((5, 5), 2): 4}
    if distribution != expected:
        raise AssertionError(f"wrong gauge distribution {distribution}")

    distinct = {}
    for record in records:
        pair = tuple(
            sorted(
                sum(1 << index for index in current)
                for current in (
                    support(certificate["gordan_weight"][record[0], record[1]]),
                    support(certificate["gordan_weight"][record[0], record[2]]),
                )
            )
        )
        value = (record[3], record[5])
        if pair in distinct and distinct[pair] != value:
            raise AssertionError("one support pair has inconsistent gauge rank")
        distinct[pair] = value
    if len(distinct) != 55:
        raise AssertionError(f"expected 55 distinct support pairs, got {len(distinct)}")

    representative = next(record for record in records if record[5] == 2)
    pattern, left, right, _, matrix_rank, beta, invariants = representative
    print("PASS: exact minimal positive pencil-rigid pair occurrences = 65 (55 distinct)")
    print("PASS: 4+5 has rank 7 and beta 0 (three occurrences)")
    print("PASS: 5+5 beta distribution = 1:58, 2:4 occurrences")
    print(
        "PASS: primitive balanced monomial exponent for sample "
        f"pattern/bits {pattern}/{left},{right}: {invariants[0]}"
    )
    print("THEOREM (sample): column scaling removes all but at most two weight ratios")
    print("CAVEAT: this is the exact row-2599 shatter sample, not a universal census")


if __name__ == "__main__":
    main()
