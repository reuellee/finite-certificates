#!/usr/bin/env python3
"""Exact obstruction to a convex log-bracket proof of Extension--Helly.

Many residual derived-wall equations are binomials in parent brackets.  After
taking logarithms of absolute bracket values, each such binomial wall becomes
an ordinary affine hyperplane.  The usual realizable-COM argument would then
apply if the log-bracket image of a fixed parent realization cell were convex.

This checker proves that the needed convexity already fails for parent row
2599.  It uses two exact integer charts from the tracked 178-chart artifact.
Their coordinatewise logarithmic midpoint would have bracket magnitudes

    g_B = sqrt(abs(p_B * q_B))

and the same fixed bracket signs.  One three-term Pluecker relation fails at
``g``.  The failure is invariant under positive column rescaling and the
common determinant factor from a change of row basis, so it also obstructs
convexity in the projectively normalized log-bracket quotient.

This does not prove that any residual sign region is disconnected, and it is
not a counterexample to 9DVL.  It rules out only the direct strategy that
restricts a hyperplane arrangement to a convex log-bracket image.
"""

from itertools import combinations
from pathlib import Path

import numpy as np


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
CERTIFICATE = HERE / "data" / "seeat_parent2599_upper178.npz"
CATALOG = ROOT / "ai" / "omgamma" / "data" / "cat_4_8.txt"
PARENT_INDEX = 2599


def determinant(matrix):
    matrix = [[int(value) for value in row] for row in matrix]
    if len(matrix) == 1:
        return matrix[0][0]
    return sum(
        (-1 if column & 1 else 1)
        * value
        * determinant(
            [row[:column] + row[column + 1 :] for row in matrix[1:]]
        )
        for column, value in enumerate(matrix[0])
    )


def colex_subsets(n, r):
    return sorted(combinations(range(n), r), key=lambda item: tuple(reversed(item)))


def increasing_brackets(matrix):
    return {
        basis: determinant(matrix[:, basis].tolist())
        for basis in combinations(range(8), 4)
    }


def ordered_bracket(brackets, ordered_basis):
    inversions = sum(
        ordered_basis[left] > ordered_basis[right]
        for left in range(len(ordered_basis))
        for right in range(left + 1, len(ordered_basis))
    )
    value = brackets[tuple(sorted(ordered_basis))]
    return -value if inversions & 1 else value


def gp_terms(brackets, common, first, second, third, fourth):
    return (
        ordered_bracket(brackets, common + (first, second))
        * ordered_bracket(brackets, common + (third, fourth)),
        -ordered_bracket(brackets, common + (first, third))
        * ordered_bracket(brackets, common + (second, fourth)),
        ordered_bracket(brackets, common + (first, fourth))
        * ordered_bracket(brackets, common + (second, third)),
    )


def main():
    artifact = np.load(CERTIFICATE, allow_pickle=False)
    charts = artifact["chart_matrix"]
    assert charts.shape == (178, 4, 8)
    assert np.issubdtype(charts.dtype, np.integer)
    first_chart, second_chart = charts[1], charts[4]
    first = increasing_brackets(first_chart)
    second = increasing_brackets(second_chart)
    assert all(first[basis] and second[basis] for basis in first)

    catalog = [line.strip() for line in CATALOG.open(encoding="utf-8") if line.strip()]
    expected = catalog[PARENT_INDEX]
    for brackets in (first, second):
        signs = "".join(
            "+" if brackets[basis] > 0 else "-"
            for basis in colex_subsets(8, 4)
        )
        assert signs == expected

    # Labels are zero-based here.  The relation has common pair {5,8} and
    # remaining labels {1,2,6,7} in the human-readable one-based convention.
    relation = ((4, 7), 0, 1, 5, 6)
    first_terms = gp_terms(first, *relation)
    second_terms = gp_terms(second, *relation)
    assert first_terms == (1_984_680, -4_428_300, 2_443_620)
    assert second_terms == (1_101_443_200, -56_241_502_200, 55_140_059_000)
    assert sum(first_terms) == sum(second_terms) == 0

    # At the coordinatewise log midpoint the three signed terms would be
    # +sqrt(R0), -sqrt(R1), +sqrt(R2).  Equality would force
    # sqrt(R1)=sqrt(R0)+sqrt(R2), and hence the squared integer identity
    # below.  Its exact failure is a radical-free certificate.
    radicands = tuple(
        abs(left * right)
        for left, right in zip(first_terms, second_terms, strict=True)
    )
    assert radicands == (
        2_186_012_290_176_000,
        249_054_244_192_260_000,
        134_741_350_973_580_000,
    )
    left_side = (radicands[1] - radicands[0] - radicands[2]) ** 2
    right_side = 4 * radicands[0] * radicands[2]
    assert left_side == 12_572_437_426_754_914_037_159_678_016_000_000
    assert right_side == 1_178_184_996_892_655_292_278_200_320_000_000
    assert left_side != right_side

    print("PASS: both exact charts realize UOM(4,8) parent row 2599")
    print("PASS: endpoint Pluecker relations and midpoint radicals checked")
    print("THEOREM: the projective log-bracket image of row 2599 is nonconvex")
    print("SCOPE: this blocks direct convex-log COM, not 9DVL")


if __name__ == "__main__":
    main()
