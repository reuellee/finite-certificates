#!/usr/bin/env python3
"""Exact infinitesimal sparse-three-vector test on all 45 s=3 survivors.

For every generic five-support orbit retained by
``verify_third_diagonal_support_filter.cpp``, take the exact row-2599
pattern-zero chart ``Y`` and its alternating cofactor vector ``c_Q``.  Thus
``Lambda^3(Y)(c_Q)=0``.  This checker computes

    {A in gl(8), mu in Q : A.c_Q = mu c_Q}

and the rank of its induced infinitesimal motion ``Y A`` after quotienting by
left ``GL(4)`` and independent column scales.  The computation is exact over
``QQ``.  It tests whether the sparse-form stabilizer strategy has any orbit
with only vertical/scalar directions.

It does not integrate these tangent directions, prove that a stabilizer orbit
reaches the parent-cell boundary, or imply compact-support cohomology
vanishing.  In particular tangent rank alone cannot kill H_c^2.
"""

from collections import Counter
from functools import reduce
from itertools import combinations
from math import gcd
from pathlib import Path

import numpy as np
import sympy as sp


HERE = Path(__file__).resolve().parent
CERTIFICATE = HERE / "data" / "seeat_parent2599_shatter8.npz"

# Canonical representatives emitted by the independently audited C++ census.
REPRESENTATIVES = """
345/236/146/127/128
145/245/236/137/128
245/236/146/137/128
123/345/246/137/128
125/345/246/137/128
135/345/246/137/128
235/345/246/137/128
345/246/156/137/128
345/246/256/137/128
123/234/456/137/128
124/234/456/137/128
234/125/456/137/128
234/235/456/137/128
234/145/456/137/128
234/245/456/137/128
145/236/456/137/128
245/236/456/137/128
345/246/456/137/128
234/456/127/137/128
123/456/137/237/128
124/456/137/237/128
134/456/137/237/128
145/456/137/237/128
345/456/137/237/128
234/356/137/147/128
245/356/137/147/128
234/356/237/147/128
245/356/237/147/128
345/356/237/147/128
356/456/237/147/128
123/156/356/347/128
124/156/356/347/128
125/156/356/347/128
135/156/356/347/128
235/156/356/347/128
245/156/356/347/128
356/456/127/347/128
156/456/137/347/128
256/456/137/347/128
356/456/137/347/128
146/356/347/157/128
246/356/347/157/128
346/356/347/157/128
356/456/347/157/128
346/456/347/357/128
""".split()

TRIPLES = tuple(combinations(range(8), 3))
TRIPLE_INDEX = {triple: index for index, triple in enumerate(TRIPLES)}


def vectorize(matrix):
    """Row-major vectorization, used consistently in all tangent maps."""
    return sp.Matrix([
        matrix[row, column]
        for row in range(matrix.rows)
        for column in range(matrix.cols)
    ])


def support_indices(text):
    return tuple(
        TRIPLE_INDEX[tuple(int(value) - 1 for value in edge)]
        for edge in text.split("/")
    )


def parent_normals(matrix):
    normals = []
    for triple in TRIPLES:
        columns = matrix[:, triple]
        normals.append(sp.Matrix([
            (-1) ** (row + 3)
            * columns.extract(
                [other for other in range(4) if other != row], range(3)
            ).det()
            for row in range(4)
        ]))
    return tuple(normals)


def primitive_cofactors(normals, support):
    coefficients = [
        (-1) ** omitted
        * sp.Matrix.hstack(*[
            normals[support[index]]
            for index in range(5)
            if index != omitted
        ]).det()
        for omitted in range(5)
    ]
    if not all(coefficients):
        raise AssertionError("the exact chart lies on a retained cofactor wall")
    divisor = reduce(gcd, (abs(int(value)) for value in coefficients))
    return tuple(int(value) // divisor for value in coefficients)


def action_matrix(support, coefficients):
    """Matrix of (A,mu) -> A.c-mu*c in Lambda^3(Q^8)."""
    result = sp.zeros(56, 65)
    for triple_index, coefficient in zip(support, coefficients, strict=True):
        triple = TRIPLES[triple_index]
        for position, source in enumerate(triple):
            for target in range(8):
                image = list(triple)
                image[position] = target
                if len(set(image)) < 3:
                    continue
                inversions = sum(
                    image[left] > image[right]
                    for left in range(3)
                    for right in range(left + 1, 3)
                )
                sign = -1 if inversions & 1 else 1
                row = TRIPLE_INDEX[tuple(sorted(image))]
                result[row, 8 * target + source] += coefficient * sign
        result[triple_index, 64] -= coefficient
    return result


def tangent_quotient(matrix):
    """Return qF, where ker(q) is left-GL4 plus column-scale gauge."""
    trivial = []
    for row in range(4):
        for column in range(4):
            left = sp.zeros(4)
            left[row, column] = 1
            trivial.append(vectorize(left * matrix))
    for column in range(8):
        diagonal = sp.zeros(8)
        diagonal[column, column] = 1
        trivial.append(vectorize(matrix * diagonal))
    trivial = sp.Matrix.hstack(*trivial)
    if trivial.rank() != 23:
        raise AssertionError("wrong GL4/column-gauge tangent rank")
    quotient = sp.Matrix.vstack(*[
        vector.T for vector in trivial.T.nullspace()
    ])
    if quotient.shape != (9, 32) or quotient * trivial != sp.zeros(9, 24):
        raise AssertionError("wrong nine-dimensional tangent quotient")

    motion = sp.zeros(32, 65)
    # (Y A)_(row,column) = sum_target Y_(row,target) A_(target,column).
    for row in range(4):
        for column in range(8):
            for target in range(8):
                motion[8 * row + column, 8 * target + column] = matrix[row, target]
    return quotient * motion


def beta(support):
    base = set(TRIPLES[support[0]])
    centered = sp.Matrix([
        [
            int(vertex in TRIPLES[index]) - int(vertex in base)
            for vertex in range(8)
        ]
        for index in support[1:]
    ])
    return 4 - centered.rank()


def main():
    if len(REPRESENTATIVES) != 45 or len(set(REPRESENTATIVES)) != 45:
        raise AssertionError("need 45 distinct support representatives")
    fingerprint = 14_695_981_039_346_656_037
    for line in sorted(REPRESENTATIVES):
        for byte in (line + "\n").encode("ascii"):
            fingerprint = ((fingerprint ^ byte) * 1_099_511_628_211) & ((1 << 64) - 1)
    if fingerprint != 0x2B0DACE2B3066B2E:
        raise AssertionError("representative list does not match the audited C++ census")
    certificate = np.load(CERTIFICATE, allow_pickle=False)
    if int(certificate["parent_index"].item()) != 2599:
        raise AssertionError("wrong parent certificate")
    matrix = sp.Matrix(certificate["pattern_chart"][0].tolist())
    normals = parent_normals(matrix)
    quotient_motion = tangent_quotient(matrix)

    distribution = Counter()
    exceptional_motion = []
    beta_one_data = None
    for text in REPRESENTATIVES:
        support = support_indices(text)
        coefficients = primitive_cofactors(normals, support)
        if any(
            sum(
                coefficient * normals[index][coordinate]
                for coefficient, index in zip(coefficients, support, strict=True)
            )
            for coordinate in range(4)
        ):
            raise AssertionError("cofactor tensor is not killed by Lambda^3(Y)")

        action = action_matrix(support, coefficients)
        action_rank = action.rank()
        stabilizer_dimension = 65 - action_rank
        diagonal_columns = [8 * index + index for index in range(8)] + [64]
        vertical_dimension = 9 - action[:, diagonal_columns].rank()
        nonvertical_dimension = stabilizer_dimension - vertical_dimension
        # For S=ker(action), rank(qF|S)=rank([action;qF])-rank(action).
        geometric_rank = action.col_join(quotient_motion).rank() - action_rank
        current_beta = beta(support)
        record = (
            current_beta,
            stabilizer_dimension,
            vertical_dimension,
            nonvertical_dimension,
            geometric_rank,
        )
        distribution[record] += 1
        if geometric_rank < 9:
            exceptional_motion.append((text, current_beta, geometric_rank))
        if current_beta == 1:
            beta_one_data = (support, coefficients, action, action_rank)

    expected = Counter({
        (0, 18, 4, 14, 9): 17,
        (0, 17, 4, 13, 9): 9,
        (0, 24, 4, 20, 9): 7,
        (0, 21, 4, 17, 9): 5,
        (0, 25, 4, 21, 9): 1,
        (0, 22, 4, 18, 9): 1,
        (0, 19, 4, 15, 9): 1,
        (0, 15, 4, 11, 9): 1,
        (0, 13, 4, 9, 9): 1,
        (0, 12, 4, 8, 8): 1,
        (1, 17, 5, 12, 8): 1,
    })
    if distribution != expected:
        raise AssertionError(f"wrong exact-c stabilizer distribution {distribution}")
    if exceptional_motion != [
        ("156/456/137/347/128", 1, 8),
        ("246/356/347/157/128", 0, 8),
    ]:
        raise AssertionError(f"wrong rank-eight exceptions {exceptional_motion}")

    # The looser beta-one strategy which merely preserves the five-coordinate
    # support is maximally nonselective: it has dimension 21 and already maps
    # onto all nine tangent directions.  This independently explains why the
    # exact-c equation, not support preservation alone, must be retained.
    support, _coefficients, exact_action, _ = beta_one_data
    outside = [index for index in range(56) if index not in support]
    support_action = exact_action.extract(outside, range(64))
    support_rank = support_action.rank()
    support_stabilizer_dimension = 64 - support_rank
    support_geometric_rank = (
        support_action.col_join(quotient_motion[:, :64]).rank() - support_rank
    )
    if (support_stabilizer_dimension, support_geometric_rank) != (21, 9):
        raise AssertionError("wrong raw beta-one support-stabilizer ranks")

    print("PASS: exact projective-c stabilizers checked on all 45 survivor orbits")
    print("43 beta-zero representatives induce tangent rank 9")
    print("rank-8 exceptions: beta1 156/456/137/347/128 and beta0 246/356/347/157/128")
    print("minimum exact-c nonvertical dimension=8; no orbit is only vertical/scalar")
    print("beta-one raw support stabilizer: dimension=21, quotient tangent rank=9")
    print("NOTE: infinitesimal rank does not supply a global escape or kill H_c^2")


if __name__ == "__main__":
    main()
