#!/usr/bin/env python3
"""Exact Hodge-complement regression for the single-region H_7 theorem.

At row-2599 pattern 1, signature bit 0 has an exact feasible extension
column p.  This checker forms N=[Y|p], contracts p, and independently takes
exact right kernels.  It verifies:

* deletion of the Gale dual N* is a Gale dual of N/p;
* all complementary Pluecker coordinates agree with one common Hodge scale;
* in contraction coordinates, the dual extension column is exactly -B h;
* height gauge directions are precisely the row space of N/p; and
* taking the Hodge complement twice returns the original row space.

This is a regression for the normalized Gale lift/extension identification,
not a finite-data proof of the topological escape theorem.
"""

from fractions import Fraction
from itertools import combinations
from pathlib import Path
import sys

import numpy as np


HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import prototype_koszul_circuits as koszul  # noqa: E402


CERTIFICATE = HERE / "data" / "seeat_parent2599_shatter8.npz"
PATTERN = 1
SIGNATURE_BIT = 0


def determinant_columns(matrix, columns):
    return koszul.determinant([
        [matrix[row][column] for column in columns]
        for row in range(len(matrix))
    ])


def permutation_sign(sequence):
    inversions = sum(
        sequence[left] > sequence[right]
        for left in range(len(sequence))
        for right in range(left + 1, len(sequence))
    )
    return -1 if inversions & 1 else 1


def exact_matrix(array):
    return [
        [Fraction(value) for value in row]
        for row in np.asarray(array, dtype=object).tolist()
    ]


def matmul(left, right):
    return [
        [
            sum(
                left[row][inner] * right[inner][column]
                for inner in range(len(right))
            )
            for column in range(len(right[0]))
        ]
        for row in range(len(left))
    ]


def transpose(matrix):
    return [list(row) for row in zip(*matrix, strict=True)]


def hodge_ratios(primal, dual):
    """Complementary Pluecker ratios for orthogonal row spaces."""
    ncolumns = len(primal[0])
    dual_rank = len(dual)
    ratios = set()
    for dual_basis in combinations(range(ncolumns), dual_rank):
        primal_basis = tuple(
            index for index in range(ncolumns) if index not in dual_basis
        )
        epsilon = permutation_sign(dual_basis + primal_basis)
        primal_minor = determinant_columns(primal, primal_basis)
        dual_minor = determinant_columns(dual, dual_basis)
        if not primal_minor or not dual_minor:
            raise AssertionError("uniform Hodge regression has a zero minor")
        ratios.add(Fraction(dual_minor, epsilon * primal_minor))
    if len(ratios) != 1:
        raise AssertionError("complementary Pluecker coordinates lack one Hodge scale")
    return next(iter(ratios))


def same_row_space(first, second):
    rank = koszul.matrix_rank(first)
    return (
        rank == koszul.matrix_rank(second)
        and koszul.matrix_rank(first + second) == rank
    )


def rank_five_normal(matrix, support):
    columns = np.asarray(matrix, dtype=object)[:, np.asarray(support) - 1]
    return tuple(
        (-1) ** (row + 6)
        * koszul.determinant(np.delete(columns, row, axis=0).tolist())
        for row in range(5)
    )


def rank_five_bracket(matrix, labels):
    return koszul.determinant([
        [matrix[row][label - 1] for label in labels]
        for row in range(5)
    ])


def rank_five_pencil_regression():
    """Hard equality case: six 4-supports, every label of degree three."""
    parent = [
        [Fraction(label**row) for label in range(1, 9)]
        for row in range(5)
    ]
    supports = (
        (1, 2, 3, 4),
        (1, 2, 5, 6),
        (1, 2, 7, 8),
        (3, 4, 5, 6),
        (3, 4, 7, 8),
        (5, 6, 7, 8),
    )
    relation = (
        Fraction(1),
        Fraction(-1),
        Fraction(1, 35),
        Fraction(35),
        Fraction(-1),
        Fraction(1),
    )
    normals = [rank_five_normal(parent, support) for support in supports]
    if koszul.matrix_rank([
        [normals[column][row] for column in range(6)]
        for row in range(5)
    ]) != 5:
        raise AssertionError("synthetic six-normal support lacks rank five")
    if tuple(
        sum(relation[index] * normals[index][row] for index in range(6))
        for row in range(5)
    ) != (0, 0, 0, 0, 0):
        raise AssertionError("synthetic signed circuit relation failed")
    degrees = tuple(
        sum(label in support for support in supports)
        for label in range(1, 9)
    )
    if degrees != (3, 3, 3, 3, 3, 3, 3, 3):
        raise AssertionError("synthetic support does not attain the degree-three bound")

    moving_label = 1
    incident_normals = [
        normals[index]
        for index, support in enumerate(supports)
        if moving_label in support
    ]
    line_space = koszul.nullspace(incident_normals)
    if len(line_space) != 2:
        raise AssertionError("three incident hyperplanes do not meet in a line")
    initial = tuple(parent[row][moving_label - 1] for row in range(5))
    direction = next(
        vector for vector in line_space
        if koszul.matrix_rank([initial, vector]) == 2
    )
    if any(
        sum(normal[row] * direction[row] for row in range(5))
        for normal in incident_normals
    ):
        raise AssertionError("pencil direction left an incident support plane")

    roots = []
    derivative_parent = [row[:] for row in parent]
    for row in range(5):
        derivative_parent[row][moving_label - 1] = direction[row]
    for other_labels in combinations(range(2, 9), 4):
        labels = (moving_label,) + other_labels
        constant = rank_five_bracket(parent, labels)
        derivative = rank_five_bracket(derivative_parent, labels)
        if not constant or not derivative:
            raise AssertionError("cyclic pencil unexpectedly has a zero bracket term")
        roots.append(Fraction(-constant, derivative))
    if max(root for root in roots if root < 0) != Fraction(-1, 2):
        raise AssertionError("wrong first rank-five parent wall")
    if any(root > 0 for root in roots):
        raise AssertionError("chosen oriented pencil unexpectedly has a positive wall")
    exit_time = Fraction(-1, 2)
    midpoint_time = Fraction(-1, 4)

    # The first wall is the genuine collision y_1=(-t*)v + y_1 = y_2/16.
    endpoint = tuple(
        initial[row] + exit_time * direction[row]
        for row in range(5)
    )
    second = tuple(parent[row][1] for row in range(5))
    if endpoint != tuple(value / 16 for value in second):
        raise AssertionError("first pencil wall is not the certified column collision")

    midpoint_parent = [row[:] for row in parent]
    for row in range(5):
        midpoint_parent[row][0] = initial[row] + midpoint_time * direction[row]
    for labels in combinations(range(1, 9), 5):
        if (
            (rank_five_bracket(parent, labels) > 0)
            != (rank_five_bracket(midpoint_parent, labels) > 0)
        ):
            raise AssertionError("parent chirotope changed before the first wall")

    midpoint_normals = [
        rank_five_normal(midpoint_parent, support)
        for support in supports
    ]
    transported = []
    for coefficient, support in zip(relation, supports, strict=True):
        scale = Fraction(1, 2) if moving_label in support else Fraction(1)
        transported.append(abs(coefficient) / scale)
    signed_midpoint_normals = [
        tuple(
            (1 if relation[index] > 0 else -1) * value
            for value in midpoint_normals[index]
        )
        for index in range(6)
    ]
    if tuple(
        sum(
            transported[index] * signed_midpoint_normals[index][row]
            for index in range(6)
        )
        for row in range(5)
    ) != (0, 0, 0, 0, 0):
        raise AssertionError("positive Gordan circuit did not transport along the pencil")
    if not all(value > 0 for value in transported):
        raise AssertionError("transported Gordan coefficient lost positivity")
    return degrees, exit_time


def main():
    certificate = np.load(CERTIFICATE, allow_pickle=False)
    if int(certificate["parent_index"].item()) != 2599:
        raise AssertionError("wrong parent certificate")
    parent = exact_matrix(certificate["pattern_chart"][PATTERN])
    point = [
        Fraction(int(value))
        for value in certificate["feasible_point"][PATTERN, SIGNATURE_BIT]
    ]
    if not any(point):
        raise AssertionError("stored extension point is zero")

    # Check directly that the stored point realizes the selected extension.
    normals = koszul.parent_normals(np.asarray(parent, dtype=object))
    signature = int(certificate["signature"][SIGNATURE_BIT])
    strict_values = []
    for index, normal in enumerate(normals):
        value = sum(normal[row] * point[row] for row in range(4))
        strict_values.append(value if (signature >> index) & 1 else -value)
    if not all(value > 0 for value in strict_values):
        raise AssertionError("stored column does not realize its extension signature")

    lifted = [parent[row] + [point[row]] for row in range(4)]
    if koszul.matrix_rank(lifted) != 4:
        raise AssertionError("lift matrix has wrong rank")
    dual_lifted = koszul.nullspace(lifted)
    if len(dual_lifted) != 5 or koszul.matrix_rank(dual_lifted) != 5:
        raise AssertionError("Gale dual of the lift has wrong rank")

    # A quotient map V -> V/<p> is any rank-three covector matrix killing p.
    quotient = koszul.nullspace([point])
    if len(quotient) != 3 or koszul.matrix_rank(quotient) != 3:
        raise AssertionError("contraction quotient has wrong rank")
    contraction = matmul(quotient, parent)
    if koszul.matrix_rank(contraction) != 3:
        raise AssertionError("contracted realization has wrong rank")

    dual_deletion = [row[:8] for row in dual_lifted]
    if koszul.matrix_rank(dual_deletion) != 5:
        raise AssertionError("dual deletion has wrong rank")
    annihilation = matmul(contraction, transpose(dual_deletion))
    if any(value for row in annihilation for value in row):
        raise AssertionError("dual deletion is not the kernel of the contraction")
    if len(koszul.nullspace(contraction)) != 5:
        raise AssertionError("contraction kernel has wrong dimension")
    if not same_row_space(dual_deletion, koszul.nullspace(contraction)):
        raise AssertionError("(N/p)* is not the deletion of the computed N*")

    lift_hodge_scale = hodge_ratios(lifted, dual_lifted)
    contraction_hodge_scale = hodge_ratios(contraction, dual_deletion)

    # Complete the quotient covectors by a height covector taking p to one.
    pivot = next(index for index, value in enumerate(point) if value)
    height_covector = [Fraction(0) for _ in range(4)]
    height_covector[pivot] = 1 / point[pivot]
    coordinate_change = quotient + [height_covector]
    if koszul.matrix_rank(coordinate_change) != 4:
        raise AssertionError("contraction-height coordinates are singular")
    normalized_lift = matmul(coordinate_change, lifted)
    if [normalized_lift[row][8] for row in range(4)] != [0, 0, 0, 1]:
        raise AssertionError("contracted element did not normalize to e_4")
    if normalized_lift[:3] != [row + [Fraction(0)] for row in contraction]:
        raise AssertionError("top contraction rows changed unexpectedly")

    heights = normalized_lift[3][:8]
    dual_extension = [row[8] for row in dual_lifted]
    expected_extension = [
        -sum(dual_deletion[row][column] * heights[column] for column in range(8))
        for row in range(5)
    ]
    if dual_extension != expected_extension:
        raise AssertionError("dual extension column is not -B h")

    # B has rank five, so h -> -Bh is onto.  Its kernel has dimension three
    # and is exactly row(A), proving the height-gauge quotient is R^5.
    if len(koszul.nullspace(dual_deletion)) != 3:
        raise AssertionError("height-to-extension map is not onto")
    if not same_row_space(contraction, koszul.nullspace(dual_deletion)):
        raise AssertionError("height gauge is larger than the contraction row space")

    double_complement = koszul.nullspace(dual_lifted)
    if len(double_complement) != 4 or not same_row_space(lifted, double_complement):
        raise AssertionError("double Hodge complement did not recover the lift")

    degrees, exit_time = rank_five_pencil_regression()

    print("PASS: stored row-2599 column realizes the selected strict extension")
    print("PASS: deletion of the exact Gale dual equals the dual contraction")
    print(f"lift Hodge scale={lift_hodge_scale}")
    print(f"contraction Hodge scale={contraction_hodge_scale}")
    print("PASS: every complementary Pluecker coordinate has the same Hodge scale")
    print("PASS: the dual extension column is exactly -B h")
    print("PASS: height gauge ker(B) is exactly row(N/p)")
    print("PASS: taking the exact Hodge complement twice recovers row(N)")
    print(f"PASS: rank-five six-normal equality case has degrees {degrees}")
    print(f"PASS: its positive circuit escapes to a genuine wall at t={exit_time}")


if __name__ == "__main__":
    main()
