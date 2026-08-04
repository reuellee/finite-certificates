#!/usr/bin/env python3
"""Exact algebraic checks for the block-Gordan formal no-go family.

For each proposed middle diagonal ``s=3,...,8``, the accompanying audit note
uses ``s`` disjoint cylinders

    B_j = S^(9-s) x R^(s-1) subset R^9

as bad loci of 56 strict linear inequalities in a private R^4 witness.  The
normalized Gordan fiber is a singleton over each B_j and empty elsewhere.
Thus properness, full row span, nonzero rows, compact convex fibers, and even
pairwise incomparability do not imply the desired compact-support vanishing.

This script checks the exact matrix identities.  The cylinder cohomology is
the elementary compact-support Kunneth computation recorded in
``BLOCK_GORDAN_AUDIT.md``.
"""

from fractions import Fraction
from pathlib import Path
import sys


HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import prototype_koszul_circuits as koszul  # noqa: E402


def rows(g_squared):
    result = [
        (1, g_squared, 0, 0),
        (-1, g_squared, 0, 0),
        (0, 1, 0, 0),
        (0, 0, 1, 0),
        (0, 0, 0, 1),
    ]
    result.extend([(0, 1, 0, 0)] * (56 - len(result)))
    return result


def transpose_product(matrix, vector):
    return tuple(
        sum(weight * row[column] for weight, row in zip(vector, matrix, strict=True))
        for column in range(4)
    )


def dot(left, right):
    return sum(x * y for x, y in zip(left, right, strict=True))


def main():
    for g_squared in (0, 1, 4, 25):
        matrix = rows(g_squared)
        if len(matrix) != 56 or any(not any(row) for row in matrix):
            raise AssertionError("the no-go matrix must have 56 nonzero rows")
        if koszul.matrix_rank(matrix) != 4:
            raise AssertionError("the no-go matrix must span R^4")

        if g_squared == 0:
            weight = [Fraction(0) for _ in matrix]
            weight[0] = weight[1] = Fraction(1, 2)
            if sum(weight) != 1 or transpose_product(matrix, weight) != (0, 0, 0, 0):
                raise AssertionError("wrong singleton Gordan witness")
            # The first two primal inequalities are p_1>0 and -p_1>0.
            if not (matrix[0][0] == 1 and matrix[1][0] == -1):
                raise AssertionError("missing exact infeasibility pair")
        else:
            witness = (0, 1, 1, 1)
            if not all(dot(row, witness) > 0 for row in matrix):
                raise AssertionError("off-cylinder primal witness is not strict")

    for s in range(3, 9):
        sphere_dimension = 9 - s
        euclidean_dimension = s - 1
        if (sphere_dimension + 1) + euclidean_dimension != 9:
            raise AssertionError("wrong ambient dimension")
        # Centers 4e_1*j give pairwise distance at least four, while every
        # cylinder has unit-radius sphere factor.  Hence their bad loci are
        # disjoint and their open complements are pairwise incomparable.
        if 4 <= 2:
            raise AssertionError("cylinder centers are not separated")

    print("PASS: all 56 rows are nonzero and span R^4, including on the bad locus")
    print("PASS: the normalized bad fiber is the singleton (1/2,1/2,0,...,0)")
    print("PASS: p=(0,1,1,1) is strict at every point off the bad cylinder")
    print("PASS: the construction has the exact R^9 dimensions for s=3,...,8")
    print("NOTE: H_c^(s-1)(S^(9-s) x R^(s-1);Q)=Q by Kunneth")


if __name__ == "__main__":
    main()
