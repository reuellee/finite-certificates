#!/usr/bin/env python3
"""Exact prototype for the Koszul/Gordan reduction on parent row 2599.

The eight-shatter certificate contains a parent chart at which eight selected
extension signatures are simultaneously infeasible.  This checker does more
than recheck Gordan's alternative:

* it constructs the degree-three Koszul subspace
  ``ker(Y) wedge Lambda^2(Q^8)``;
* it verifies that this 52-dimensional space is exactly the kernel of the
  third-compound map ``Lambda^3(Y)``;
* it proves that every stored Gordan vector is a *minimal* positive circuit of
  support four or five and agrees with the exact alternating-cofactor vector;
* it identifies the 52-wall orbit of every four-normal cofactor involved.

Only integer and rational arithmetic is used.  The script performs no LP,
sampling, floating-point arithmetic, or symbolic factorization.  The latter
is already certified independently by ``verify_derived_walls.py``.
"""

from fractions import Fraction
from itertools import combinations, permutations
from math import gcd
from pathlib import Path
import sys

import numpy as np

import four_chart_gate as gate


HERE = Path(__file__).resolve().parent
CERTIFICATE = HERE / "data" / "seeat_parent2599_shatter8.npz"
PATTERN = 0
TRIPLES = gate.colex_subsets(8, 3)
TRIPLE_INDEX = {triple: index for index, triple in enumerate(TRIPLES)}
ANCHORS = tuple(
    TRIPLE_INDEX[tuple(value for value in (1, 2, 3, 4) if value != omitted)]
    for omitted in (1, 2, 3, 4)
)


def determinant(matrix):
    """Exact recursive determinant for matrices of order at most four."""
    matrix = [list(row) for row in matrix]
    if not matrix:
        return 1
    if len(matrix) == 1:
        return matrix[0][0]
    return sum(
        (-1 if column & 1 else 1)
        * value
        * determinant([row[:column] + row[column + 1 :] for row in matrix[1:]])
        for column, value in enumerate(matrix[0])
    )


def matrix_rank(matrix):
    """Rank over Q by exact reduced row elimination."""
    rows = [[Fraction(value) for value in row] for row in matrix]
    if not rows:
        return 0
    row = 0
    for column in range(len(rows[0])):
        pivot = next((r for r in range(row, len(rows)) if rows[r][column]), None)
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
        row += 1
        if row == len(rows):
            break
    return row


def nullspace(matrix):
    """A rational basis for the right kernel of a matrix."""
    rows = [[Fraction(value) for value in row] for row in matrix]
    ncolumns = len(rows[0])
    pivot_columns = []
    row = 0
    for column in range(ncolumns):
        pivot = next((r for r in range(row, len(rows)) if rows[r][column]), None)
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

    free_columns = [column for column in range(ncolumns) if column not in pivot_columns]
    basis = []
    for free in free_columns:
        vector = [Fraction(0) for _ in range(ncolumns)]
        vector[free] = 1
        for pivot_row, pivot_column in enumerate(pivot_columns):
            vector[pivot_column] = -rows[pivot_row][free]
        basis.append(vector)
    return basis


def parent_normals(matrix):
    rows = []
    for triple in TRIPLES:
        columns = matrix[:, np.asarray(triple) - 1]
        row = []
        for coordinate in range(4):
            minor = np.delete(columns, coordinate, axis=0)
            row.append((-1) ** (coordinate + 5) * determinant(minor.tolist()))
        if not any(row):
            raise AssertionError("zero derived normal")
        rows.append(tuple(row))
    return rows


def exterior_sign(sequence):
    inversions = sum(
        sequence[i] > sequence[j]
        for i in range(len(sequence))
        for j in range(i + 1, len(sequence))
    )
    return -1 if inversions & 1 else 1


def koszul_matrix(kernel_basis):
    """Columns k wedge e_i wedge e_j in the certificate's triple order."""
    columns = []
    for kernel_vector in kernel_basis:
        for first, second in combinations(range(8), 2):
            column = [Fraction(0) for _ in TRIPLES]
            for coordinate, value in enumerate(kernel_vector):
                if not value or coordinate in (first, second):
                    continue
                sequence = (coordinate, first, second)
                triple = tuple(sorted(value + 1 for value in sequence))
                column[TRIPLE_INDEX[triple]] += exterior_sign(sequence) * value
            columns.append(column)
    return [list(row) for row in zip(*columns, strict=True)]


def primitive(vector):
    divisor = 0
    for value in vector:
        divisor = gcd(divisor, abs(int(value)))
    vector = [int(value) // divisor for value in vector]
    if next(value for value in vector if value) < 0:
        vector = [-value for value in vector]
    return vector


def circuit_cofactors(signed_columns):
    """Alternating maximal minors of a rank-(k-1), 4-by-k matrix."""
    size = len(signed_columns)
    matrix = [
        [signed_columns[column][row] for column in range(size)]
        for row in range(4)
    ]
    rank = matrix_rank(matrix)
    if rank != size - 1:
        raise AssertionError(f"support of size {size} has rank {rank}")
    if size == 5:
        selected_rows = tuple(range(4))
    elif size == 4:
        selected_rows = next(
            rows
            for rows in combinations(range(4), 3)
            if matrix_rank([[matrix[row][column] for column in range(4)] for row in rows]) == 3
        )
    else:
        raise AssertionError("prototype expects support four or five")

    square_rows = [[matrix[row][column] for column in range(size)] for row in selected_rows]
    cofactors = []
    for omitted in range(size):
        minor = [row[:omitted] + row[omitted + 1 :] for row in square_rows]
        cofactors.append((-1 if omitted & 1 else 1) * determinant(minor))
    if all(value < 0 for value in cofactors):
        cofactors = [-value for value in cofactors]
    if not all(value > 0 for value in cofactors):
        raise AssertionError(f"circuit is not positive: {cofactors}")
    return rank, primitive(cofactors)


def anchored_circuit_cofactors(signed_columns, normals):
    """Rank-three circuit cofactors as classified four-normal determinants."""
    support_matrix = [
        [signed_columns[column][row] for column in range(4)]
        for row in range(4)
    ]
    anchor_index = next(
        index
        for index in ANCHORS
        if matrix_rank(
            [
                support_matrix[row] + [normals[index][row]]
                for row in range(4)
            ]
        )
        == 4
    )
    columns = signed_columns + [normals[anchor_index]]
    matrix = [[columns[column][row] for column in range(5)] for row in range(4)]
    cofactors = []
    for omitted in range(5):
        minor = [row[:omitted] + row[omitted + 1 :] for row in matrix]
        cofactors.append((-1 if omitted & 1 else 1) * determinant(minor))
    if all(value < 0 for value in cofactors[:4]):
        cofactors = [-value for value in cofactors]
    if not all(value > 0 for value in cofactors[:4]) or cofactors[4] != 0:
        raise AssertionError("anchor did not recover the positive rank-three circuit")
    return anchor_index, primitive(cofactors[:4])


def edge_permute_mask(mask, permutation):
    out = 0
    for old in range(4):
        if mask & (1 << old):
            out |= 1 << permutation[old]
    return out


S4 = tuple(permutations(range(4)))


def orbit_key(edges):
    masks = []
    for vertex in range(8):
        masks.append(sum((vertex in edges[j]) << j for j in range(4)))
    candidates = []
    for permutation in S4:
        counts = [0] * 16
        for mask in masks:
            counts[edge_permute_mask(mask, permutation)] += 1
        candidates.append(tuple(counts))
    return min(candidates)


REPRESENTATIVE_TEXT = (
    "123/124/125/126 123/124/125/134 123/124/125/136 123/124/125/167 "
    "123/124/125/345 123/124/125/346 123/124/125/367 123/124/125/678 "
    "123/124/134/156 123/124/134/234 123/124/134/235 123/124/134/256 "
    "123/124/134/567 123/124/135/145 123/124/135/146 123/124/135/167 "
    "123/124/135/236 123/124/135/245 123/124/135/246 123/124/135/256 "
    "123/124/135/267 123/124/135/456 123/124/135/467 123/124/135/678 "
    "123/124/156/157 123/124/156/178 123/124/156/256 123/124/156/257 "
    "123/124/156/278 123/124/156/345 123/124/156/347 123/124/156/356 "
    "123/124/156/357 123/124/156/378 123/124/156/567 123/124/156/578 "
    "123/124/345/367 123/124/345/567 123/124/345/678 123/124/356/378 "
    "123/124/356/456 123/124/356/457 123/124/356/478 123/124/356/567 "
    "123/124/356/578 123/124/567/568 123/145/167/246 123/145/167/248 "
    "123/145/246/356 123/145/246/357 123/145/246/378 123/145/267/468"
)


def parse_edges(text):
    return tuple(tuple(int(value) - 1 for value in edge) for edge in text.split("/"))


ORBIT_INDEX = {
    orbit_key(parse_edges(text)): index
    for index, text in enumerate(REPRESENTATIVE_TEXT.split())
}
assert len(ORBIT_INDEX) == 52
ZERO = {0, 1, 2, 3, 4, 5, 6, 7, 8, 13, 14, 15, 24, 25}
RESIDUAL = {36, 37, 38, 39, 41, 42, 44, 46, 47, 48, 49, 50, 51}


def wall_orbit(triple_indices):
    edges = tuple(tuple(value - 1 for value in TRIPLES[index]) for index in triple_indices)
    return ORBIT_INDEX[orbit_key(edges)]


def orbit_kind(index):
    if index in ZERO:
        return "zero"
    if index in RESIDUAL:
        return "residual"
    return "unit"


def shear_rigid_union(first_support, second_support):
    """Whether the union has none of the residence shears from (5m)."""
    triples = [set(TRIPLES[index]) for index in first_support | second_support]
    for label in range(1, 9):
        incident = [triple for triple in triples if label in triple]
        if len(incident) < 2:
            return False
        common_partners = set.intersection(
            *(triple - {label} for triple in incident)
        )
        if common_partners:
            return False
    return True


def main():
    certificate = np.load(CERTIFICATE, allow_pickle=False)
    if int(certificate["parent_index"].item()) != gate.PARENT_INDEX:
        raise AssertionError("certificate is not for parent row 2599")
    matrix = certificate["pattern_chart"][PATTERN]
    signatures = [int(value) for value in certificate["signature"]]
    weights = certificate["gordan_weight"][PATTERN]

    catalog = [
        line.strip()
        for line in gate.CATALOG_48.open(encoding="utf-8")
        if line.strip()
    ]
    parent_signs = []
    for basis in gate.colex_subsets(8, 4):
        columns = matrix[:, np.asarray(basis) - 1]
        value = determinant(columns.tolist())
        if not value:
            raise AssertionError("prototype parent chart is nonuniform")
        parent_signs.append("+" if value > 0 else "-")
    if "".join(parent_signs) != catalog[gate.PARENT_INDEX]:
        raise AssertionError("prototype chart does not realize parent row 2599")

    normals = parent_normals(matrix)

    # Lambda^3(Y) is the 4-by-56 matrix of derived normals.  Its kernel has
    # dimension 52.  The degree-three Koszul ideal generated by ker(Y) has
    # that same dimension and is visibly killed by Lambda^3(Y).
    compound = [[normal[row] for normal in normals] for row in range(4)]
    if matrix_rank(compound) != 4:
        raise AssertionError("third compound does not have rank four")
    kernel_basis = nullspace(matrix.tolist())
    if len(kernel_basis) != 4:
        raise AssertionError("parent kernel does not have dimension four")
    koszul = koszul_matrix(kernel_basis)
    if matrix_rank(koszul) != 52:
        raise AssertionError("degree-three Koszul image does not have dimension 52")
    for compound_row in compound:
        for koszul_column in zip(*koszul, strict=True):
            if sum(
                Fraction(left) * right
                for left, right in zip(compound_row, koszul_column, strict=True)
            ):
                raise AssertionError("Koszul generator survives Lambda^3(Y)")
    print("PASS ker(Lambda^3 Y) = ker(Y) wedge Lambda^2(Q^8), dimension 52")

    circuit_supports = []
    for bit, signature in enumerate(signatures):
        witness = [int(value) for value in weights[bit]]
        if not any(witness) or any(value < 0 for value in witness):
            raise AssertionError(
                f"signature {bit}: stored Gordan weights are not positive"
            )
        support = [index for index, value in enumerate(witness) if value]
        circuit_supports.append(set(support))
        signed_columns = [
            tuple(
                value if (signature >> index) & 1 else -value
                for value in normals[index]
            )
            for index in support
        ]
        rank, cofactor_vector = circuit_cofactors(signed_columns)
        witness_vector = primitive([witness[index] for index in support])
        if cofactor_vector != witness_vector:
            raise AssertionError(
                f"signature {bit}: witness {witness_vector} != cofactors {cofactor_vector}"
            )

        # The signed coefficient 3-form is killed by Lambda^3(Y), hence lies
        # in the already-certified Koszul kernel.
        coefficient = [0] * len(TRIPLES)
        for index in support:
            coefficient[index] = witness[index] if (signature >> index) & 1 else -witness[index]
        if any(
            sum(row[index] * coefficient[index] for index in range(len(TRIPLES)))
            for row in compound
        ):
            raise AssertionError("Gordan form is not in the third-compound kernel")

        if len(support) == 5:
            orbits = [
                wall_orbit(tuple(index for j, index in enumerate(support) if j != omitted))
                for omitted in range(5)
            ]
        else:
            anchor, anchored_vector = anchored_circuit_cofactors(signed_columns, normals)
            if anchored_vector != witness_vector:
                raise AssertionError("anchored derived determinants give the wrong circuit")
            orbits = [wall_orbit(tuple(support))] + [
                wall_orbit(
                    tuple(index for j, index in enumerate(support) if j != omitted)
                    + (anchor,)
                )
                for omitted in range(4)
            ]
        orbit_summary = ",".join(f"{index}:{orbit_kind(index)}" for index in orbits)
        support_summary = "/".join("".join(map(str, TRIPLES[index])) for index in support)
        print(
            f"PASS signature {bit}: positive circuit {support_summary}; "
            f"rank {rank}; wall orbits {orbit_summary}"
        )

    rigid_pairs = {
        (first, second)
        for first, second in combinations(range(len(circuit_supports)), 2)
        if shear_rigid_union(
            circuit_supports[first], circuit_supports[second]
        )
    }
    expected_rigid_pairs = {
        (0, 3), (0, 4), (0, 5), (0, 6), (3, 5), (4, 7)
    }
    if rigid_pairs != expected_rigid_pairs:
        raise AssertionError(f"unexpected shear-rigid pairs: {rigid_pairs}")
    print("PASS six stored positive-circuit pairs have shear-rigid support unions")

    print("THEOREM (prototype): all eight exact infeasibility witnesses are")
    print("minimal positive Koszul circuits controlled by the 52-wall classification")


if __name__ == "__main__":
    # Make invocation from either the repository root or ai/omreal reliable.
    sys.path.insert(0, str(HERE))
    main()
