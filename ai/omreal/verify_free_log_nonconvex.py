#!/usr/bin/env python3
"""Exact obstructions to convexity in the nine free log coordinates.

The standard projective-frame chart is

    [e1,e2,e3,e4,(1,1,1,1),(1,a,b,c),(1,d,e,f),(1,g,h,i)].

For two points with the same signs of the nine free coordinates, the midpoint
in ``(log|a|,...,log|i|)`` has coordinates ``sqrt(x_j y_j)`` (with the fixed
sign restored).  All coordinates used below are positive.

This checker uses exact rational endpoint arithmetic and rational interval
enclosures for the square roots.  It certifies two separate failures inside
catalog parent 2599:

* charts 0 and 3 have a free-log midpoint on the wrong side of parent bracket
  [5678], so the parent realization cell is not log-convex; and
* charts 77 and 85 have a free-log midpoint still inside the parent cell, but
  residual side q_44>0 changes to q_44<0, so even that residual side restricted
  to the parent cell is not log-convex.

The result is not a counterexample to 9DVL.  It blocks a convex-log shortcut
whose global premise is convexity of the parent cell or of every residual
side.  It does not block the separate signed-gradient KKT necessary condition.
Coordinate-line convexity is a different, weaker property.
"""

from dataclasses import dataclass
from fractions import Fraction
from itertools import combinations, permutations
from math import isqrt
from pathlib import Path

import numpy as np


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
CERTIFICATE = HERE / "data" / "seeat_parent2599_upper178.npz"
CATALOG = ROOT / "ai" / "omgamma" / "data" / "cat_4_8.txt"
PARENT_INDEX = 2599
PARENT_PAIR = (0, 3)
RESIDUAL_PAIR = (77, 85)
BRACKETS = tuple(combinations(range(8), 4))


def permutation_sign(permutation):
    inversions = sum(
        permutation[left] > permutation[right]
        for left in range(len(permutation))
        for right in range(left + 1, len(permutation))
    )
    return -1 if inversions & 1 else 1


def determinant(matrix):
    size = len(matrix)
    total = Fraction(0)
    for permutation in permutations(range(size)):
        term = Fraction(1)
        for row in range(size):
            term *= matrix[row][permutation[row]]
        total += permutation_sign(permutation) * term
    return total


def fraction_inverse(matrix):
    size = len(matrix)
    work = [
        [Fraction(int(matrix[row][column])) for column in range(size)]
        + [Fraction(row == column) for column in range(size)]
        for row in range(size)
    ]
    for column in range(size):
        pivot = next(
            (row for row in range(column, size) if work[row][column]), None
        )
        if pivot is None:
            raise AssertionError("singular projective frame")
        work[column], work[pivot] = work[pivot], work[column]
        scale = work[column][column]
        work[column] = [value / scale for value in work[column]]
        for row in range(size):
            if row == column:
                continue
            scale = work[row][column]
            if scale:
                work[row] = [
                    left - scale * right
                    for left, right in zip(work[row], work[column], strict=True)
                ]
    return [row[size:] for row in work]


def matmul(left, right):
    return [
        [
            sum(
                (left[row][inner] * right[inner][column] for inner in range(4)),
                Fraction(0),
            )
            for column in range(8)
        ]
        for row in range(4)
    ]


def free_coordinates(matrix):
    """Return exact ``(a,b,c,d,e,f,g,h,i)`` in normalization (25)."""
    raw = [[Fraction(int(matrix[row, column])) for column in range(8)] for row in range(4)]
    inverse = fraction_inverse(np.asarray(matrix[:, :4], dtype=object))
    transformed = matmul(inverse, raw)
    if any(transformed[row][4] == 0 for row in range(4)):
        raise AssertionError("fifth column cannot normalize the affine frame")

    coordinates = []
    for column in range(5, 8):
        top = transformed[0][column] / transformed[0][4]
        if top == 0:
            raise AssertionError("free column has zero first normalized coordinate")
        for row in range(1, 4):
            coordinates.append(
                (transformed[row][column] / transformed[row][4]) / top
            )
    if any(value <= 0 for value in coordinates):
        raise AssertionError("certificate is not in the positive free-coordinate orthant")
    return tuple(coordinates)


def gauge_matrix(coordinates):
    a, b, c, d, e, f, g, h, i = coordinates
    zero, one = Fraction(0), Fraction(1)
    return (
        (one, zero, zero, zero, one, one, one, one),
        (zero, one, zero, zero, one, a, d, g),
        (zero, zero, one, zero, one, b, e, h),
        (zero, zero, zero, one, one, c, f, i),
    )


def bracket_values(matrix):
    return tuple(
        determinant([[matrix[row][column] for column in basis] for row in range(4)])
        for basis in BRACKETS
    )


def original_bracket_values(matrix):
    exact = [[Fraction(int(matrix[row, column])) for column in range(8)] for row in range(4)]
    return bracket_values(exact)


@dataclass(frozen=True)
class Interval:
    lower: Fraction
    upper: Fraction

    def __post_init__(self):
        if self.lower > self.upper:
            raise AssertionError("reversed interval")

    @classmethod
    def point(cls, value):
        value = Fraction(value)
        return cls(value, value)

    def __add__(self, other):
        other = other if isinstance(other, Interval) else Interval.point(other)
        return Interval(self.lower + other.lower, self.upper + other.upper)

    __radd__ = __add__

    def __neg__(self):
        return Interval(-self.upper, -self.lower)

    def __sub__(self, other):
        return self + (-other if isinstance(other, Interval) else -Interval.point(other))

    def __rsub__(self, other):
        return Interval.point(other) - self

    def __mul__(self, other):
        other = other if isinstance(other, Interval) else Interval.point(other)
        products = (
            self.lower * other.lower,
            self.lower * other.upper,
            self.upper * other.lower,
            self.upper * other.upper,
        )
        return Interval(min(products), max(products))

    __rmul__ = __mul__


def sqrt_interval(value, decimal_places=80):
    """Exact decimal enclosure of ``sqrt(value)`` using integer square root."""
    value = Fraction(value)
    if value <= 0:
        raise AssertionError("square-root coordinate must be positive")
    scale = 10**decimal_places
    lower_numerator = isqrt((value.numerator * scale * scale) // value.denominator)
    lower = Fraction(lower_numerator, scale)
    if lower * lower == value:
        return Interval.point(lower)
    upper = Fraction(lower_numerator + 1, scale)
    assert lower * lower < value < upper * upper
    return Interval(lower, upper)


def interval_determinant(matrix):
    total = Interval.point(0)
    size = len(matrix)
    for permutation in permutations(range(size)):
        term = Interval.point(1)
        for row in range(size):
            term *= matrix[row][permutation[row]]
        total += permutation_sign(permutation) * term
    return total


def interval_gauge_matrix(coordinates):
    z, o = Interval.point(0), Interval.point(1)
    a, b, c, d, e, f, g, h, i = coordinates
    return (
        (o, z, z, z, o, o, o, o),
        (z, o, z, z, o, a, d, g),
        (z, z, o, z, o, b, e, h),
        (z, z, z, o, o, c, f, i),
    )


def interval_brackets(matrix):
    return tuple(
        interval_determinant(
            [[matrix[row][column] for column in basis] for row in range(4)]
        )
        for basis in BRACKETS
    )


def q44(values):
    a, b, c, d, e, f, g, h, i = values
    return (
        a * e * i - a * e - a * f * h + a * f + a * h - a * i
        + c * d * h - c * d * i - c * e * g + c * e
        + c * f * g - c * f - c * h + c * i
        - d * h + d * i + e * g - e * i - f * g + f * h
    )


def signed_interval(interval, sign):
    return interval if sign > 0 else -interval


def colex_subsets(n, rank):
    return sorted(combinations(range(n), rank), key=lambda item: tuple(reversed(item)))


def main():
    artifact = np.load(CERTIFICATE, allow_pickle=False)
    charts = artifact["chart_matrix"]
    assert charts.shape == (178, 4, 8)
    assert np.issubdtype(charts.dtype, np.integer)

    catalog = [line.strip() for line in CATALOG.open(encoding="utf-8") if line.strip()]
    expected_catalog = catalog[PARENT_INDEX]
    used_indices = sorted(set(PARENT_PAIR + RESIDUAL_PAIR))
    for index in used_indices:
        values = original_bracket_values(charts[index])
        signs = "".join(
            "+" if values[BRACKETS.index(basis)] > 0 else "-"
            for basis in colex_subsets(8, 4)
        )
        assert signs == expected_catalog

    coordinates = {index: free_coordinates(charts[index]) for index in used_indices}
    exact_brackets = {
        index: bracket_values(gauge_matrix(coordinates[index])) for index in used_indices
    }
    reference_signs = tuple(1 if value > 0 else -1 for value in exact_brackets[0])
    assert all(
        tuple(1 if value > 0 else -1 for value in exact_brackets[index]) == reference_signs
        for index in used_indices
    )

    # Parent cell obstruction: the exact free-log midpoint crosses [5678].
    first, second = (coordinates[index] for index in PARENT_PAIR)
    midpoint = tuple(sqrt_interval(left * right) for left, right in zip(first, second, strict=True))
    midpoint_brackets = interval_brackets(interval_gauge_matrix(midpoint))
    target = BRACKETS.index((4, 5, 6, 7))
    assert exact_brackets[PARENT_PAIR[0]][target] > 0
    assert exact_brackets[PARENT_PAIR[1]][target] > 0
    assert midpoint_brackets[target].upper < 0

    # Residual-side obstruction: this midpoint stays strictly in the parent
    # cell but exits q_44>0.
    first, second = (coordinates[index] for index in RESIDUAL_PAIR)
    midpoint = tuple(sqrt_interval(left * right) for left, right in zip(first, second, strict=True))
    midpoint_brackets = interval_brackets(interval_gauge_matrix(midpoint))
    for sign, enclosure in zip(reference_signs, midpoint_brackets, strict=True):
        assert signed_interval(enclosure, sign).lower > 0
    assert q44(first) > 0 and q44(second) > 0
    midpoint_q44 = q44(midpoint)
    assert midpoint_q44.upper < 0

    print("PASS: four exact charts realize UOM(4,8) parent row 2599")
    print("PASS: charts 0/3 cross parent bracket [5678] at their free-log midpoint")
    print("PASS: charts 77/85 retain all 70 parent signs at their free-log midpoint")
    print("PASS: q_44 is positive at charts 77/85 and negative at that midpoint")
    print("THEOREM: neither the parent cell nor every residual side is free-log convex")
    print("SCOPE: this blocks the convex-log shortcut, not the KKT filter or 9DVL")


if __name__ == "__main__":
    main()
