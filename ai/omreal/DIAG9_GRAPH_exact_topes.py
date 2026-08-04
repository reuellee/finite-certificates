#!/usr/bin/env python3
"""Exact recursive tope enumeration for rational central arrangements.

The algorithm adds rows one at a time.  A chamber of the old arrangement is
split by the new hyperplane exactly when its sign pattern occurs in the
arrangement restricted to that hyperplane.  Restriction lowers the ambient
dimension, giving an induction on (dimension, number of rows).

Every reported sign pattern carries an integer witness.  For a restricted
witness x on a new hyperplane with normal a, choose an integer K so that
K*x +/- a preserves every old strict sign.  These are exact witnesses for the
two new chambers.  Thus the recursion proves both soundness and coverage; it
does not use LP, floating point, or a sampled direction set.
"""

from itertools import combinations
from math import gcd


TRIPLES = tuple(
    sorted(combinations(range(8), 3), key=lambda subset: tuple(reversed(subset)))
)
BASES = tuple(
    sorted(combinations(range(8), 4), key=lambda subset: tuple(reversed(subset)))
)


def primitive(vector):
    vector = tuple(int(value) for value in vector)
    divisor = 0
    for value in vector:
        divisor = gcd(divisor, abs(value))
    divisor = max(divisor, 1)
    return tuple(value // divisor for value in vector)


def dot(left, right):
    return sum(x * y for x, y in zip(left, right))


def determinant(matrix):
    matrix = tuple(tuple(int(value) for value in row) for row in matrix)
    if len(matrix) == 1:
        return matrix[0][0]
    return sum(
        (-1 if column & 1 else 1)
        * value
        * determinant(
            tuple(row[:column] + row[column + 1 :] for row in matrix[1:])
        )
        for column, value in enumerate(matrix[0])
    )


def parent_signs(parent):
    signs = []
    for basis in BASES:
        value = determinant(
            tuple(
                tuple(parent[row][column] for column in basis) for row in range(4)
            )
        )
        if value == 0:
            raise AssertionError(f"nonuniform parent at basis {basis}")
        signs.append(1 if value > 0 else -1)
    return tuple(signs)


def derived_rows(parent, normalize=True):
    rows = []
    for triple in TRIPLES:
        columns = tuple(
            tuple(int(parent[row][column]) for column in triple) for row in range(4)
        )
        normal = []
        for coordinate in range(4):
            minor = tuple(
                row for row_index, row in enumerate(columns) if row_index != coordinate
            )
            normal.append((-1) ** (coordinate + 3) * determinant(minor))
        rows.append(primitive(normal) if normalize else tuple(normal))
    if any(not any(row) for row in rows):
        raise AssertionError("uniform parent produced a zero derived normal")
    return tuple(rows)


def restrict_rows(rows, normal):
    """Restrict row hyperplanes to normal-perp using an integer basis."""
    dimension = len(normal)
    pivot = next(index for index, value in enumerate(normal) if value)
    free = tuple(index for index in range(dimension) if index != pivot)
    pivot_value = normal[pivot]
    restricted = tuple(
        primitive(
            tuple(
                pivot_value * row[index] - row[pivot] * normal[index]
                for index in free
            )
        )
        for row in rows
    )
    return restricted, pivot, free


def lift_restricted(witness, normal, pivot, free):
    vector = [0] * len(normal)
    pivot_value = normal[pivot]
    for index, value in zip(free, witness):
        vector[index] = pivot_value * value
    vector[pivot] = -sum(
        normal[index] * value for index, value in zip(free, witness)
    )
    answer = primitive(vector)
    if dot(normal, answer) != 0:
        raise AssertionError("restriction lift missed the new hyperplane")
    return answer


def enumerate_topes(rows, dimension=None):
    """Return ``{sign_bitset: integer_witness}`` for a central arrangement."""
    rows = tuple(primitive(row) for row in rows)
    if dimension is None:
        if not rows:
            raise ValueError("dimension is required for an empty arrangement")
        dimension = len(rows[0])
    if any(len(row) != dimension for row in rows):
        raise AssertionError("row dimensions disagree")
    # A zero restricted row means that the current subspace is contained in
    # an earlier hyperplane, so its complement inside that subspace is empty.
    if any(not any(row) for row in rows):
        return {}
    if not rows:
        return {0: (1,) + (0,) * (dimension - 1)}
    if dimension == 1:
        positive = sum((row[0] > 0) << index for index, row in enumerate(rows))
        negative = ((1 << len(rows)) - 1) ^ positive
        return {positive: (1,), negative: (-1,)}

    topes = {0: (1,) + (0,) * (dimension - 1)}
    for index, normal in enumerate(rows):
        restricted, pivot, free = restrict_rows(rows[:index], normal)
        boundary = {
            signs: lift_restricted(witness, normal, pivot, free)
            for signs, witness in enumerate_topes(
                restricted, dimension=dimension - 1
            ).items()
        }

        next_topes = {}
        for signs, witness in topes.items():
            if signs in boundary:
                continue
            value = dot(normal, witness)
            if value == 0:
                raise AssertionError("nonsplit chamber witness lies on new wall")
            next_topes[signs | ((value > 0) << index)] = witness

        for signs, wall_witness in boundary.items():
            scale = 1
            for old_row in rows[:index]:
                margin = dot(old_row, wall_witness)
                slope = dot(old_row, normal)
                if margin == 0:
                    raise AssertionError("restricted tope is not strict")
                if slope:
                    scale = max(scale, abs(slope) // abs(margin) + 1)
            positive = primitive(
                scale * value + slope
                for value, slope in zip(wall_witness, normal)
            )
            negative = primitive(
                scale * value - slope
                for value, slope in zip(wall_witness, normal)
            )
            if dot(normal, positive) <= 0 or dot(normal, negative) >= 0:
                raise AssertionError("integer wall perturbation has wrong side")
            next_topes[signs | (1 << index)] = positive
            next_topes[signs] = negative
        topes = next_topes

    return topes


def verify_topes(rows, topes):
    for signs, witness in topes.items():
        if len(witness) != len(rows[0]) or not any(witness):
            raise AssertionError("bad tope witness dimension")
        for index, row in enumerate(rows):
            prescribed = 1 if signs & (1 << index) else -1
            if prescribed * dot(row, witness) <= 0:
                raise AssertionError(f"tope witness fails row {index}")
    if len(topes) != len(set(topes)):
        raise AssertionError("duplicate tope sign pattern")


def parent_topes(parent, verify=True):
    rows = derived_rows(parent)
    topes = enumerate_topes(rows, dimension=4)
    if verify:
        verify_topes(rows, topes)
    return topes
