#!/usr/bin/env python3
"""Exact audit of the projective-carrier chart for a five-circuit.

For the hard row-2599 support Q0, this checker:

* normalizes its five signed support planes to the standard labeled
  projective frame using the exact positive dependence;
* verifies the carrier dimensions (1,0,1,1,2,1,2,1), whose sum is nine;
* verifies that the labeled plane-frame stabilizer is only the scalar;
* places exact pattern charts 0 and 6 in one oriented affine carrier patch;
* proves both endpoints have the same uniform parent chirotope and retain
  the same strict positive Q0 circuit; and
* proves their carrier-coordinate midpoint still has a strict positive Q0
  circuit but flips exactly four parent brackets.

The last item is an exact nonconvexity certificate for the parent-sign cell
inside the strict carrier chamber.  It does not prove that the cell is not a
topological ball.
"""

from fractions import Fraction
from itertools import combinations
from pathlib import Path
import sys

import numpy as np


HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import BLOCK_GORDAN_HARD_TRIPLE_PIVOT as pivot  # noqa: E402
import prototype_koszul_circuits as koszul  # noqa: E402


CERTIFICATE = HERE / "data" / "seeat_parent2599_shatter8.npz"
SIGNATURE_BIT = 0
ENDPOINT_PATTERNS = (0, 6)
EXPECTED_SUPPORT = ("123", "134", "267", "258", "468")
EXPECTED_DEGREES = (2, 3, 2, 2, 1, 2, 1, 2)
EXPECTED_CARRIER_DIMENSIONS = (1, 0, 1, 1, 2, 1, 2, 1)
# Zero-based homogeneous coordinate used to orient and dehomogenize each
# carrier at the pattern-zero point.
AFFINE_PIVOTS = (3, 1, 3, 2, 1, 1, 3, 1)
EXPECTED_PIVOT_SIGNS = (-1, -1, 1, -1, -1, -1, 1, -1)
EXPECTED_MIDPOINT_FLIPS = {
    (1, 2, 7, 8),
    (1, 3, 6, 7),
    (1, 6, 7, 8),
    (3, 5, 7, 8),
}
STANDARD_NORMALS = (
    (1, 0, 0, 0),
    (0, 1, 0, 0),
    (0, 0, 1, 0),
    (0, 0, 0, 1),
    (-1, -1, -1, -1),
)


def sign(value):
    if value == 0:
        return 0
    return 1 if value > 0 else -1


def bracket(matrix, labels):
    return koszul.determinant([
        [matrix[row][label - 1] for label in labels]
        for row in range(4)
    ])


def chirotope(matrix):
    return tuple(
        sign(bracket(matrix, labels))
        for labels in combinations(range(1, 9), 4)
    )


def raw_cofactors(normals, signature, support):
    columns = pivot.signed_columns(normals, signature, support)
    values = []
    for omitted in range(5):
        selected = [
            columns[index]
            for index in range(5)
            if index != omitted
        ]
        determinant = koszul.determinant([
            [column[row] for column in selected]
            for row in range(4)
        ])
        values.append((-1 if omitted & 1 else 1) * determinant)
    return tuple(values)


def strict_positive_up_to_common_sign(values):
    return all(value > 0 for value in values) or all(value < 0 for value in values)


def normalize_support_frame(matrix, signature, support):
    """Return exact homogeneous columns in the standard five-plane frame."""
    normals = koszul.parent_normals(matrix)
    coefficients = pivot.circuit_coefficients(normals, signature, support)
    if coefficients is None:
        raise AssertionError("support is not a strict positive rank-four circuit")
    signed = pivot.signed_columns(normals, signature, support)
    relation = tuple(
        sum(
            coefficients[index] * signed[index][row]
            for index in range(5)
        )
        for row in range(4)
    )
    if relation != (0, 0, 0, 0):
        raise AssertionError("positive cofactor vector is not a dependence")

    # The first four scaled signed normals are a dual basis.  In the new
    # coordinates they become x_1,...,x_4, while the relation forces the
    # fifth to be -(x_1+x_2+x_3+x_4).
    change = np.asarray([
        [coefficients[index] * value for value in signed[index]]
        for index in range(4)
    ], dtype=object)
    if koszul.determinant(change.tolist()) == 0:
        raise AssertionError("first four support normals do not form a frame")
    transformed = change @ matrix.astype(object)

    for plane, support_index in enumerate(support):
        normal = STANDARD_NORMALS[plane]
        triple = koszul.TRIPLES[support_index]
        for label in triple:
            if sum(
                normal[row] * transformed[row, label - 1]
                for row in range(4)
            ) != 0:
                raise AssertionError("normalized point left its carrier plane")
        columns = [
            tuple(transformed[row, label - 1] for row in range(4))
            for label in triple
        ]
        if koszul.matrix_rank(columns) != 3:
            raise AssertionError("support triple does not span its normalized plane")
    return transformed


def oriented_affine_patch(matrix):
    """Dehomogenize by positive scaling, retaining the oriented ray signs."""
    columns = []
    pivot_signs = []
    for label, pivot_row in enumerate(AFFINE_PIVOTS):
        denominator = matrix[pivot_row, label]
        if denominator == 0:
            raise AssertionError("carrier point left the selected affine patch")
        pivot_signs.append(sign(denominator))
        scale = abs(int(denominator))
        columns.append(tuple(
            Fraction(int(matrix[row, label]), scale)
            for row in range(4)
        ))
    result = tuple(
        tuple(columns[column][row] for column in range(8))
        for row in range(4)
    )
    return result, tuple(pivot_signs)


def carrier_dimensions(support):
    degrees = tuple(
        sum(label in koszul.TRIPLES[index] for index in support)
        for label in range(1, 9)
    )
    dimensions = []
    for label, degree in enumerate(degrees, start=1):
        incident = [
            STANDARD_NORMALS[position]
            for position, index in enumerate(support)
            if label in koszul.TRIPLES[index]
        ]
        rank = koszul.matrix_rank(incident) if incident else 0
        if rank != degree or degree > 3:
            raise AssertionError("incident frame planes are not independent")
        dimensions.append(3 - rank)
    return degrees, tuple(dimensions)


def verify_frame_stabilizer():
    """Infinitesimal labeled stabilizer of five standard hyperplanes."""
    # Variables are the 16 entries X_(k,j), followed by five eigenvalues mu_i.
    equations = []
    for plane, normal in enumerate(STANDARD_NORMALS):
        for column in range(4):
            equation = [0] * 21
            for row in range(4):
                equation[4 * row + column] = normal[row]
            equation[16 + plane] = -normal[column]
            equations.append(equation)
    rank = koszul.matrix_rank(equations)
    if rank != 20 or 21 - rank != 1:
        raise AssertionError("labeled projective-frame stabilizer is nontrivial")


def validate_carriers(matrix, support):
    for plane, support_index in enumerate(support):
        normal = STANDARD_NORMALS[plane]
        for label in koszul.TRIPLES[support_index]:
            if sum(normal[row] * matrix[row][label - 1] for row in range(4)):
                raise AssertionError("affine point violates a carrier equation")


def main():
    certificate = np.load(CERTIFICATE, allow_pickle=False)
    if int(certificate["parent_index"].item()) != 2599:
        raise AssertionError("wrong parent certificate")
    support = pivot.stored_support(certificate, SIGNATURE_BIT)
    if tuple(pivot.name(index) for index in support) != EXPECTED_SUPPORT:
        raise AssertionError("hard support changed")
    signature = int(certificate["signature"][SIGNATURE_BIT])

    degrees, dimensions = carrier_dimensions(support)
    if degrees != EXPECTED_DEGREES:
        raise AssertionError(f"wrong support degrees {degrees}")
    if dimensions != EXPECTED_CARRIER_DIMENSIONS or sum(dimensions) != 9:
        raise AssertionError(f"wrong carrier dimensions {dimensions}")
    verify_frame_stabilizer()

    source_matrices = [
        certificate["pattern_chart"][pattern]
        for pattern in ENDPOINT_PATTERNS
    ]
    source_signs = [
        chirotope(tuple(tuple(int(value) for value in row) for row in matrix))
        for matrix in source_matrices
    ]
    if source_signs[0] != source_signs[1] or 0 in source_signs[0]:
        raise AssertionError("endpoint parents do not realize the same uniform chirotope")

    affine_endpoints = []
    for matrix in source_matrices:
        normalized = normalize_support_frame(matrix, signature, support)
        affine, pivot_signs = oriented_affine_patch(normalized)
        if pivot_signs != EXPECTED_PIVOT_SIGNS:
            raise AssertionError("endpoints do not share the oriented affine patch")
        validate_carriers(affine, support)
        normals = koszul.parent_normals(np.asarray(affine, dtype=object))
        if not strict_positive_up_to_common_sign(
            raw_cofactors(normals, signature, support)
        ):
            raise AssertionError("normalized endpoint lost its positive circuit")
        affine_endpoints.append(affine)

    endpoint_signs = [chirotope(matrix) for matrix in affine_endpoints]
    if endpoint_signs[0] != endpoint_signs[1] or 0 in endpoint_signs[0]:
        raise AssertionError("normalized endpoints left their common sign cell")

    midpoint = tuple(
        tuple(
            (affine_endpoints[0][row][column]
             + affine_endpoints[1][row][column]) / 2
            for column in range(8)
        )
        for row in range(4)
    )
    validate_carriers(midpoint, support)
    midpoint_signs = chirotope(midpoint)
    if 0 in midpoint_signs:
        raise AssertionError("midpoint no-go uses a nonuniform parent")
    flips = {
        labels
        for labels, endpoint, middle in zip(
            combinations(range(1, 9), 4),
            endpoint_signs[0],
            midpoint_signs,
            strict=True,
        )
        if endpoint != middle
    }
    if flips != EXPECTED_MIDPOINT_FLIPS:
        raise AssertionError(f"wrong carrier-midpoint sign flips {flips}")

    midpoint_normals = koszul.parent_normals(np.asarray(midpoint, dtype=object))
    midpoint_cofactors = raw_cofactors(midpoint_normals, signature, support)
    if not all(value > 0 for value in midpoint_cofactors):
        raise AssertionError("midpoint left the strict positive-circuit chamber")

    print("PASS: the five support planes normalize to a labeled projective frame")
    print("PASS: its projective stabilizer is trivial")
    print(f"PASS: carrier dimensions are {dimensions}, summing to 9")
    print("PASS: exact patterns 0 and 6 lie in one oriented carrier patch")
    print("PASS: both endpoints have the same uniform parent signs and strict Q0 circuit")
    print("PASS: their exact midpoint retains the strict Q0 circuit and is uniform")
    print("PASS: the midpoint flips exactly [1278], [1367], [1678], [3578]")
    print("NOTE: the carrier parent-sign cell is not convex; ball topology remains open")


if __name__ == "__main__":
    main()
