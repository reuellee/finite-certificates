#!/usr/bin/env python3
"""Exact scope audit for discriminantal/higher-Bruhat shortcuts.

For every uniform rank-four 4-by-8 parent Y, the 56 extension hyperplanes
spanned by triples of Y are linearly isomorphic to the essential
discriminantal arrangement B(8,4,K) of a Gale dual K.  This script verifies
the Hodge-complement identification on the hard row-2599 chart.

It also checks two boundaries of that identification:

* row 2599 is not a reorientation/relabeling of the alternating (cyclic)
  rank-four oriented matroid, after exhaustive testing of all 8! orders; and
* the four triples in a higher-Bruhat 3-packet form fixed wall orbit 9, not
  one of the 13 residual parent walls.

Finally it reruns the small exact Djokovic--Winkler nontransitivity
certificate for the broader varying-chirotope mutation graph.  The latter is
only a scope warning, not a fixed-row-2599 counterexample.
"""

from fractions import Fraction
from itertools import combinations, permutations
from pathlib import Path
import sys

import numpy as np


HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import BLOCK_GORDAN_TRIPLE_WALL_AUDIT as wall  # noqa: E402
import prototype_koszul_circuits as koszul  # noqa: E402
import verify_mutation_graph_not_partial_cube as mutation  # noqa: E402


CERTIFICATE = HERE / "data" / "seeat_parent2599_shatter8.npz"
RESIDUAL_ORBITS = {36, 37, 38, 39, 41, 42, 44, 46, 47, 48, 49, 50, 51}


def transpose(matrix):
    return [list(row) for row in zip(*matrix, strict=True)]


def matvec(matrix, vector):
    return tuple(
        sum((Fraction(x) * y for x, y in zip(row, vector, strict=True)), Fraction(0))
        for row in matrix
    )


def solve_square(matrix, target):
    size = len(matrix)
    work = [
        [Fraction(value) for value in row] + [Fraction(target[index])]
        for index, row in enumerate(matrix)
    ]
    for column in range(size):
        pivot = next(
            (row for row in range(column, size) if work[row][column]), None
        )
        if pivot is None:
            raise AssertionError("singular square solve")
        work[column], work[pivot] = work[pivot], work[column]
        scale = work[column][column]
        work[column] = [value / scale for value in work[column]]
        for row in range(size):
            if row == column or not work[row][column]:
                continue
            scale = work[row][column]
            work[row] = [
                left - scale * right
                for left, right in zip(work[row], work[column], strict=True)
            ]
    return tuple(work[row][-1] for row in range(size))


def proportional(left, right):
    pivot = next(
        (index for index, value in enumerate(right) if value), None
    )
    if pivot is None or not left[pivot]:
        return False
    return all(
        left[index] * right[pivot] == right[index] * left[pivot]
        for index in range(len(left))
    )


def discriminantal_identification(matrix):
    """Verify all 56 complement-circuit/derived-normal identifications."""
    y_rows = [[Fraction(int(value)) for value in row] for row in matrix]
    gale_rows = tuple(tuple(row) for row in koszul.nullspace(y_rows))
    if len(gale_rows) != 4 or koszul.matrix_rank(gale_rows) != 4:
        raise AssertionError("wrong Gale rank")
    for y_row in y_rows:
        for gale_row in gale_rows:
            if sum(x * y for x, y in zip(y_row, gale_row, strict=True)):
                raise AssertionError("Gale rows do not span ker(Y)")

    derived = koszul.parent_normals(matrix)
    labels = set(range(8))
    basis = next(
        basis
        for basis in combinations(range(8), 4)
        if koszul.determinant([
            [int(matrix[row, column]) for column in basis]
            for row in range(4)
        ])
    )
    basis_matrix = [
        [Fraction(int(matrix[column, label])) for column in range(4)]
        for label in basis
    ]

    for triple_index, triple_one_based in enumerate(koszul.TRIPLES):
        triple = {label - 1 for label in triple_one_based}
        complement = tuple(sorted(labels - triple))

        # The unique circuit of the four-dimensional Gale configuration K on
        # the complementary five-set L.
        circuit = [Fraction(0)] * 8
        for omitted, label in enumerate(complement):
            retained = [item for index, item in enumerate(complement) if index != omitted]
            determinant = koszul.determinant([
                [gale_rows[row][column] for column in retained]
                for row in range(4)
            ])
            circuit[label] = determinant if not omitted & 1 else -determinant
        if not all(circuit[label] for label in complement):
            raise AssertionError("Gale complement is not a uniform five-circuit")
        if matvec(gale_rows, circuit) != (0, 0, 0, 0):
            raise AssertionError("wrong discriminantal circuit")

        # Since ker(K)=row(Y), c=Y^T q.  Solve on one parent basis, then check
        # all eight coordinates.  Under the essential quotient map [t] -> Yt,
        # the discriminantal equation c.t=0 becomes q.(Yt)=0.
        q = solve_square(basis_matrix, tuple(circuit[label] for label in basis))
        if tuple(
            sum(y_rows[row][label] * q[row] for row in range(4))
            for label in range(8)
        ) != tuple(circuit):
            raise AssertionError("discriminantal equation does not descend through Y")
        if not proportional(q, derived[triple_index]):
            raise AssertionError("complement circuit is not the derived triple normal")

    return gale_rows


def permutation_parity(sequence):
    inversions = sum(
        sequence[left] > sequence[right]
        for left in range(len(sequence))
        for right in range(left + 1, len(sequence))
    )
    return inversions & 1


def factorable_reorientation(mismatches, bases):
    """Solve mismatch_B = global + sum_{e in B} epsilon_e over GF(2)."""
    rows = []
    for basis, mismatch in zip(bases, mismatches, strict=True):
        coefficients = 1  # bit zero is the global sign
        for label in basis:
            coefficients |= 1 << (label + 1)
        rows.append(coefficients | (int(mismatch) << 9))

    rank = 0
    for column in range(9):
        pivot = next(
            (row for row in range(rank, len(rows)) if (rows[row] >> column) & 1),
            None,
        )
        if pivot is None:
            continue
        rows[rank], rows[pivot] = rows[pivot], rows[rank]
        for row in range(len(rows)):
            if row != rank and (rows[row] >> column) & 1:
                rows[row] ^= rows[rank]
        rank += 1
    coefficient_mask = (1 << 9) - 1
    return not any(
        not (row & coefficient_mask) and ((row >> 9) & 1)
        for row in rows
    )


def verify_noncyclic(matrix):
    """Exhaust every label order and every factorizable reorientation."""
    bases = tuple(combinations(range(8), 4))
    chirotope = tuple(
        wall.sign(wall.bracket(matrix, tuple(label + 1 for label in basis)))
        for basis in bases
    )
    if 0 in chirotope:
        raise AssertionError("parent must be uniform")

    for order in permutations(range(8)):
        position = [0] * 8
        for index, label in enumerate(order):
            position[label] = index
        cyclic_signs = tuple(
            -1 if permutation_parity(tuple(position[label] for label in basis)) else 1
            for basis in bases
        )
        mismatches = tuple(
            actual != cyclic
            for actual, cyclic in zip(chirotope, cyclic_signs, strict=True)
        )
        if factorable_reorientation(mismatches, bases):
            raise AssertionError("row 2599 is a relabeled/reoriented cyclic matroid")


def verify_packet_mismatch():
    lookup = {
        "".join(map(str, triple)): index
        for index, triple in enumerate(koszul.TRIPLES)
    }
    packet = tuple(sorted(lookup[name] for name in ("123", "124", "134", "234")))
    orbit = koszul.wall_orbit(packet)
    if orbit != 9 or koszul.orbit_kind(orbit) != "unit":
        raise AssertionError("the basic 3-packet is not the expected fixed wall")
    if orbit in RESIDUAL_ORBITS or len(RESIDUAL_ORBITS) != 13:
        raise AssertionError("higher-Bruhat packet was confused with a residual wall")


def verify_general_mutation_warning():
    vertices = tuple(
        mask
        for mask in range(1 << len(mutation.BASES))
        if mutation.gp_failure(mask) is None
    )
    vertex_set = set(vertices)
    adjacency = {
        mask: tuple(
            neighbor
            for index in range(len(mutation.BASES))
            if (neighbor := mask ^ (1 << index)) in vertex_set
        )
        for mask in vertices
    }
    if len(vertices) != 384 or sum(map(len, adjacency.values())) // 2 != 960:
        raise AssertionError("mutation regression graph changed")
    endpoints = {0, 1, 6, 7, 74, 75}
    distance = {source: mutation.distances(adjacency, source) for source in endpoints}
    first, middle, last = (6, 7), (0, 1), (74, 75)
    if not mutation.theta(distance, first, middle):
        raise AssertionError("first Djokovic--Winkler pair lost its relation")
    if not mutation.theta(distance, middle, last):
        raise AssertionError("second Djokovic--Winkler pair lost its relation")
    if mutation.theta(distance, first, last):
        raise AssertionError("nontransitivity certificate disappeared")


def main():
    certificate = np.load(CERTIFICATE, allow_pickle=False)
    if int(certificate["parent_index"].item()) != 2599:
        raise AssertionError("wrong parent certificate")
    matrix = certificate["pattern_chart"][0]

    gale = discriminantal_identification(matrix)
    verify_noncyclic(matrix)
    verify_packet_mismatch()
    verify_general_mutation_warning()

    print("PASS: the 56 derived hyperplanes are the essential B(8,4,Gale(Y)) arrangement")
    print("PASS: all 56 complementary five-circuits match their triple normals")
    print("PASS: the exact Gale dual has rank=" + str(koszul.matrix_rank(gale)))
    print("PASS: all 8! orders reject cyclicity of row 2599 up to reorientation")
    print("PASS: a higher-Bruhat 3-packet is unit orbit 9, not a residual wall")
    print("PASS: the general mutation graph retains its non-partial-cube certificate")
    print("NOTE: fixed-fiber discriminantal zonotopes do not organize parent-wall variation")


if __name__ == "__main__":
    main()
