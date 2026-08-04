#!/usr/bin/env python3
"""Exact Jacobian audit of the 65-fold row-2599 line crossing.

At the rational crossing stored by DIAG9_GRAPH_verify_row2599_slice.py,
compute every labeled residual determinant as a polynomial in all 32 parent
matrix entries. Exact cofactor differentiation proves that the 65 nonzero
ambient gradients span a one-dimensional space and that none annihilates the
certified line direction E_(2,7).

Rank-one tangent data does not prove that the 65 global polynomials have one
common irreducible residual factor: distinct smooth hypersurfaces can be
tangent. This verifier records the strongest conclusion supplied by first
derivatives and leaves factor identity to a higher-dimensional roadmap.
"""

from __future__ import annotations

import DIAG9_GRAPH_exact_topes as topes
import DIAG9_GRAPH_verify_row2599_slice as slice_verify


AMBIENT_DIMENSION = 32


def det2(matrix):
    return matrix[0][0] * matrix[1][1] - matrix[0][1] * matrix[1][0]


def normal_with_derivatives(parent, triple):
    """Return one derived normal and its 4-by-32 exact Jacobian."""
    columns = tuple(triple)
    normal = []
    derivatives = []
    for omitted_row in range(4):
        rows = tuple(row for row in range(4) if row != omitted_row)
        minor = tuple(
            tuple(int(parent[row][column]) for column in columns)
            for row in rows
        )
        orientation = (-1) ** (omitted_row + 3)
        normal.append(orientation * topes.determinant(minor))

        coordinate_derivative = [0] * AMBIENT_DIMENSION
        for minor_row, parent_row in enumerate(rows):
            for minor_column, parent_column in enumerate(columns):
                cofactor_minor = tuple(
                    tuple(
                        minor[row][column]
                        for column in range(3)
                        if column != minor_column
                    )
                    for row in range(3)
                    if row != minor_row
                )
                coordinate_derivative[8 * parent_row + parent_column] = (
                    orientation
                    * (-1) ** (minor_row + minor_column)
                    * det2(cofactor_minor)
                )
        derivatives.append(tuple(coordinate_derivative))
    return tuple(normal), tuple(derivatives)


def determinant_gradient(fourset, normal_data):
    """Differentiate the determinant of four derived-normal rows."""
    matrix = tuple(normal_data[index][0] for index in fourset)
    gradient = [0] * AMBIENT_DIMENSION
    for normal_position in range(4):
        for coordinate in range(4):
            cofactor_minor = tuple(
                tuple(
                    matrix[row][column]
                    for column in range(4)
                    if column != coordinate
                )
                for row in range(4)
                if row != normal_position
            )
            cofactor = (
                (-1) ** (normal_position + coordinate)
                * topes.determinant(cofactor_minor)
            )
            derivative = normal_data[fourset[normal_position]][1][coordinate]
            for index, value in enumerate(derivative):
                gradient[index] += cofactor * value
    return tuple(gradient)


def main():
    base = slice_verify.source_parent()
    wall_parent = slice_verify.scaled_parent(base, slice_verify.WALL)
    occurrences = slice_verify.enumerate_wall_occurrences(base)
    if len(occurrences) != 65:
        raise AssertionError("wrong labeled crossing multiplicity")

    normal_data = tuple(
        normal_with_derivatives(wall_parent, triple) for triple in topes.TRIPLES
    )
    gradients = tuple(
        determinant_gradient(fourset, normal_data) for fourset in occurrences
    )
    if any(not any(gradient) for gradient in gradients):
        raise AssertionError("a residual determinant has zero ambient gradient")

    reference = gradients[0]
    pivot = next(index for index, value in enumerate(reference) if value)
    for gradient in gradients[1:]:
        if any(
            gradient[index] * reference[pivot]
            != reference[index] * gradient[pivot]
            for index in range(AMBIENT_DIMENSION)
        ):
            raise AssertionError("the 65 crossing gradients have rank above one")

    line_coordinate = 8 * slice_verify.VARYING_ROW + slice_verify.VARYING_COLUMN
    if any(gradient[line_coordinate] == 0 for gradient in gradients):
        raise AssertionError("the certified line is tangent to a labeled wall")

    print("PASS: 65 labeled residual determinants vanish at the exact rational crossing")
    print("PASS: their 65 nonzero ambient gradients have exact rank one")
    print("PASS: every gradient is transverse to the E_(2,7) line direction")
    print("SCOPE: rank-one tangent data does not prove common global factor identity")


if __name__ == "__main__":
    main()
