#!/usr/bin/env python3
"""Exact regression for the sharp degree-three rank-five escape.

The proof in ``DIAG2_PIVOT_DUAL_SINGLE_BAD_ESCAPE.md`` is elementary and
does not depend on this example.  This checker exercises the case where the
incidence count is sharp: six four-subset normals on eight labels, with every
label occurring exactly three times.  It uses an integer moment-curve
configuration in rank five, constructs the unique signed positive dependence,
moves one label in the intersection of its three incident support
hyperplanes, and verifies exactly that

* the allowed motion has vector dimension two;
* a parent wall is reached at a positive rational parameter;
* no parent bracket changes sign before that wall;
* every incident derived normal changes by a positive scalar; and
* the rescaled Gordan coefficients still sum to zero.

Only rational arithmetic is used.
"""

from fractions import Fraction
from itertools import combinations


LABELS = tuple(range(8))
SUPPORT = (
    (0, 1, 2, 3),
    (0, 1, 4, 5),
    (0, 1, 6, 7),
    (2, 3, 4, 5),
    (2, 3, 6, 7),
    (4, 5, 6, 7),
)
MOVING = 0


def determinant(matrix):
    """Fraction-preserving determinant of a square row matrix."""
    work = [[Fraction(value) for value in row] for row in matrix]
    size = len(work)
    sign = 1
    answer = Fraction(1)
    for column in range(size):
        pivot = next(
            (row for row in range(column, size) if work[row][column]),
            None,
        )
        if pivot is None:
            return Fraction(0)
        if pivot != column:
            work[column], work[pivot] = work[pivot], work[column]
            sign *= -1
        pivot_value = work[column][column]
        answer *= pivot_value
        for row in range(column + 1, size):
            if not work[row][column]:
                continue
            scale = work[row][column] / pivot_value
            for index in range(column, size):
                work[row][index] -= scale * work[column][index]
    return sign * answer


def rank(matrix):
    """Exact row rank."""
    work = [[Fraction(value) for value in row] for row in matrix]
    if not work:
        return 0
    rows = len(work)
    columns = len(work[0])
    pivot_row = 0
    for column in range(columns):
        pivot = next(
            (row for row in range(pivot_row, rows) if work[row][column]),
            None,
        )
        if pivot is None:
            continue
        work[pivot_row], work[pivot] = work[pivot], work[pivot_row]
        pivot_value = work[pivot_row][column]
        work[pivot_row] = [value / pivot_value for value in work[pivot_row]]
        for row in range(rows):
            if row == pivot_row or not work[row][column]:
                continue
            scale = work[row][column]
            work[row] = [
                value - scale * pivot_value
                for value, pivot_value in zip(work[row], work[pivot_row], strict=True)
            ]
        pivot_row += 1
        if pivot_row == rows:
            break
    return pivot_row


def nullspace(matrix):
    """Exact basis of the right nullspace of a row matrix."""
    work = [[Fraction(value) for value in row] for row in matrix]
    rows = len(work)
    columns = len(work[0])
    pivot_columns = []
    pivot_row = 0
    for column in range(columns):
        pivot = next(
            (row for row in range(pivot_row, rows) if work[row][column]),
            None,
        )
        if pivot is None:
            continue
        work[pivot_row], work[pivot] = work[pivot], work[pivot_row]
        pivot_value = work[pivot_row][column]
        work[pivot_row] = [value / pivot_value for value in work[pivot_row]]
        for row in range(rows):
            if row == pivot_row or not work[row][column]:
                continue
            scale = work[row][column]
            work[row] = [
                value - scale * pivot_value
                for value, pivot_value in zip(work[row], work[pivot_row], strict=True)
            ]
        pivot_columns.append(column)
        pivot_row += 1
        if pivot_row == rows:
            break
    free_columns = [column for column in range(columns) if column not in pivot_columns]
    basis = []
    for free in free_columns:
        vector = [Fraction(0)] * columns
        vector[free] = Fraction(1)
        for row, pivot in reversed(list(enumerate(pivot_columns))):
            vector[pivot] = -sum(
                work[row][column] * vector[column]
                for column in free_columns
            )
        basis.append(vector)
    return basis


def columns_to_rows(columns):
    return [list(row) for row in zip(*columns, strict=True)]


def normal(columns, support):
    """Alternating cofactor normal to four rank-five columns."""
    row_matrix = columns_to_rows([columns[index] for index in support])
    answer = []
    for omitted in range(5):
        minor = row_matrix[:omitted] + row_matrix[omitted + 1 :]
        answer.append(((-1) ** omitted) * determinant(minor))
    if any(
        sum(answer[coordinate] * columns[index][coordinate] for coordinate in range(5))
        for index in support
    ):
        raise AssertionError("cofactor vector is not normal to its support")
    return answer


def basis_value(columns, basis):
    return determinant(columns_to_rows([columns[index] for index in basis]))


def scalar_multiple(vector, reference):
    pivot = next(index for index, value in enumerate(reference) if value)
    scale = vector[pivot] / reference[pivot]
    if vector != [scale * value for value in reference]:
        raise AssertionError("vectors are not scalar multiples")
    return scale


def main():
    columns = [
        [Fraction(t) ** power for power in range(5)]
        for t in range(1, 9)
    ]
    if any(
        basis_value(columns, basis) == 0
        for basis in combinations(LABELS, 5)
    ):
        raise AssertionError("moment-curve parent is not uniform")

    degrees = [sum(label in edge for edge in SUPPORT) for label in LABELS]
    if degrees != [3] * 8 or sum(degrees) != 24:
        raise AssertionError("support is not the sharp 3-regular example")

    unsigned_normals = [normal(columns, edge) for edge in SUPPORT]
    dependence_basis = nullspace(columns_to_rows(unsigned_normals))
    if len(dependence_basis) != 1 or any(value == 0 for value in dependence_basis[0]):
        raise AssertionError("the six normals do not form a circuit")
    dependence = dependence_basis[0]
    signed_normals = [
        [
            (1 if coefficient > 0 else -1) * value
            for value in current_normal
        ]
        for coefficient, current_normal in zip(
            dependence, unsigned_normals, strict=True
        )
    ]
    positive_weights = [abs(value) for value in dependence]
    if any(
        sum(
            weight * current_normal[coordinate]
            for weight, current_normal in zip(
                positive_weights, signed_normals, strict=True
            )
        )
        for coordinate in range(5)
    ):
        raise AssertionError("failed to orient the circuit positively")

    incident_indices = [
        index for index, edge in enumerate(SUPPORT) if MOVING in edge
    ]
    incident_hyperplanes = [unsigned_normals[index] for index in incident_indices]
    motion_space = nullspace(incident_hyperplanes)
    if rank(incident_hyperplanes) != 3 or len(motion_space) != 2:
        raise AssertionError("sharp motion space is not two-dimensional")
    moving_column = columns[MOVING]
    if any(sum(a * b for a, b in zip(row, moving_column, strict=True)) for row in incident_hyperplanes):
        raise AssertionError("moving point is outside an incident hyperplane")
    direction = next(
        vector
        for vector in motion_space
        if rank([moving_column, vector]) == 2
    )

    def wall_roots(test_direction):
        roots = []
        moved_direction = list(columns)
        moved_direction[MOVING] = test_direction
        for other_four in combinations([label for label in LABELS if label != MOVING], 4):
            basis = (MOVING,) + other_four
            constant = basis_value(columns, basis)
            slope = basis_value(moved_direction, basis)
            if slope:
                root = -constant / slope
                if root > 0:
                    roots.append((root, basis))
        return roots

    roots = wall_roots(direction)
    if not roots:
        direction = [-value for value in direction]
        roots = wall_roots(direction)
    if not roots:
        raise AssertionError("the projective motion found no parent wall")
    first_parameter, first_basis = min(roots)

    normal_scales = []
    direction_columns = list(columns)
    direction_columns[MOVING] = direction
    for index, edge in enumerate(SUPPORT):
        if MOVING not in edge:
            normal_scales.append((Fraction(1), Fraction(0)))
            continue
        direction_normal = normal(direction_columns, edge)
        alpha = scalar_multiple(direction_normal, unsigned_normals[index])
        if 1 + first_parameter * alpha < 0:
            raise AssertionError("an incident normal reversed before the first wall")
        normal_scales.append((Fraction(1), alpha))

    midpoint = first_parameter / 2
    moved = list(columns)
    moved[MOVING] = [
        value + midpoint * delta
        for value, delta in zip(moving_column, direction, strict=True)
    ]
    for basis in combinations(LABELS, 5):
        initial = basis_value(columns, basis)
        current = basis_value(moved, basis)
        if current == 0 or (current > 0) != (initial > 0):
            raise AssertionError("parent chirotope changed before the first wall")
    wall_columns = list(columns)
    wall_columns[MOVING] = [
        value + first_parameter * delta
        for value, delta in zip(moving_column, direction, strict=True)
    ]
    if basis_value(wall_columns, first_basis) != 0:
        raise AssertionError("claimed endpoint is not a parent wall")

    moved_signed_normals = []
    moved_weights = []
    for index, edge in enumerate(SUPPORT):
        moved_unsigned = normal(moved, edge)
        scale = scalar_multiple(moved_unsigned, unsigned_normals[index])
        if scale <= 0:
            raise AssertionError("a support normal left its positive ray")
        sign = 1 if dependence[index] > 0 else -1
        moved_signed_normals.append([sign * value for value in moved_unsigned])
        moved_weights.append(positive_weights[index] / scale)
    if any(
        sum(
            weight * current_normal[coordinate]
            for weight, current_normal in zip(
                moved_weights, moved_signed_normals, strict=True
            )
        )
        for coordinate in range(5)
    ):
        raise AssertionError("rescaled positive circuit was not preserved")

    # Rank/dimension bookkeeping used by the dual application.
    assert 9 - 4 == 5                  # rank of N* on nine elements
    assert 5 == 5                      # rank of A* = N*\\p on eight elements
    assert (5 - 1) * (8 - 5 - 1) == 8
    assert (5 - 2) * (8 - 5 - 1) == 6

    print("PASS sharp six-normal support has degree vector", tuple(degrees))
    print("PASS three incident hyperplanes leave motion dimension", len(motion_space))
    print("PASS first exact parent wall", first_basis, "at", first_parameter)
    print("PASS all incident normal rays and the positive circuit persist exactly")


if __name__ == "__main__":
    main()
