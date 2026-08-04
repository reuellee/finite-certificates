#!/usr/bin/env python3
"""Exact reduced-UOM(4,8) obstruction to double-contraction convexity.

The two private columns are e_3 and e_4, while every old column has fixed
rank-2 quotient (1,i).  Two endpoint height pairs have the same uniform
parent chirotope and the same two private-extension signatures, but their
height midpoint reverses one parent bracket.  Two further parent charts,
with exact feasible points and positive Gordan dependencies, prove that the
two extension-feasibility regions are proper and pairwise incomparable.

This disproves only joint/iterated convexity of the fixed-quotient lift
fiber.  It does not prove nontrivial homology and does not disprove the
two-color entry of 9DVL.
"""

from fractions import Fraction
from itertools import combinations, permutations


N = 8
TRIPLES = tuple(combinations(range(N), 3))
QUADS = tuple(combinations(range(N), 4))

PRIVATE_0 = (0, 0, 1, 0)
PRIVATE_1 = (0, 0, 0, 1)

LEFT_A = (178, 275, 288, -127, 25, 3, 113, 247)
LEFT_B = (224, -69, 198, 267, -216, -84, -262, 233)
RIGHT_A = (207, 226, 182, -210, -162, -187, -139, -89)
RIGHT_B = (-95, -288, -92, 102, -271, -117, -230, 213)

CHART_A_A = (0, 0, -369, -1046, -1035, -1369, -1390, -1399)
CHART_A_B = (0, 0, 749, 1172, 887, 1554, 1767, 2760)
CHART_A_POINT = (1732, 22987, -1331957, 9511743)

CHART_B_A = (0, 0, 1162, 353, 97, 844, 1203, 2052)
CHART_B_B = (0, 0, 1914, 3933, 4537, 6227, 7292, 8817)
CHART_B_POINT = (-8101, -20633, 29313369, 0)

# (old-element triple, positive integer weight), with zero-based labels.
CHART_A_EXCLUDES_1 = (
    ((0, 2, 7), 3861153462),
    ((1, 2, 7), 3816165327),
    ((3, 4, 7), 5388477543),
    ((5, 6, 7), 11733430217),
)
CHART_B_EXCLUDES_0 = (
    ((0, 2, 5), 39391670823700195),
    ((0, 2, 6), 11841217350579755),
    ((0, 3, 7), 82660040084898816),
    ((1, 2, 3), 24687765975022080),
    ((4, 5, 6), 101812359324856320),
)


def determinant(columns):
    """Leibniz determinant, exact over integers or Fractions."""
    size = len(columns)
    assert all(len(column) == size for column in columns)
    total = 0
    for permutation in permutations(range(size)):
        inversions = sum(
            permutation[left] > permutation[right]
            for left in range(size)
            for right in range(left + 1, size)
        )
        term = -1 if inversions % 2 else 1
        for column, row in enumerate(permutation):
            term *= columns[column][row]
        total += term
    return total


def parent(a_heights, b_heights):
    return tuple(
        (1, index, a_heights[index], b_heights[index])
        for index in range(N)
    )


def signs(values):
    assert all(value != 0 for value in values)
    return tuple(1 if value > 0 else -1 for value in values)


def parent_values(matrix):
    return tuple(
        determinant([matrix[index] for index in basis]) for basis in QUADS
    )


def extension_values(matrix, point):
    return tuple(
        determinant([matrix[index] for index in triple] + [point])
        for triple in TRIPLES
    )


def derived_normal(matrix, triple):
    """n with det(y_i,y_j,y_k,p)=n dot p."""
    normal = []
    for coordinate in range(4):
        unit = tuple(1 if index == coordinate else 0 for index in range(4))
        normal.append(
            determinant([matrix[index] for index in triple] + [unit])
        )
    return tuple(normal)


def check_feasible(matrix, signature, point):
    margins = tuple(
        signature[index] * value
        for index, value in enumerate(extension_values(matrix, point))
    )
    assert min(margins) > 0
    return min(margins)


def check_gordan(matrix, signature, certificate):
    triple_index = {triple: index for index, triple in enumerate(TRIPLES)}
    weighted_sum = [0, 0, 0, 0]
    for triple, weight in certificate:
        assert weight > 0
        index = triple_index[triple]
        normal = derived_normal(matrix, triple)
        for coordinate in range(4):
            weighted_sum[coordinate] += (
                weight * signature[index] * normal[coordinate]
            )
    assert weighted_sum == [0, 0, 0, 0]


left = parent(LEFT_A, LEFT_B)
right = parent(RIGHT_A, RIGHT_B)
mid_a = tuple(
    Fraction(left_height + right_height, 2)
    for left_height, right_height in zip(LEFT_A, RIGHT_A)
)
mid_b = tuple(
    Fraction(left_height + right_height, 2)
    for left_height, right_height in zip(LEFT_B, RIGHT_B)
)
midpoint = parent(mid_a, mid_b)

parent_signature = signs(parent_values(left))
assert signs(parent_values(right)) == parent_signature

signature_0 = signs(extension_values(left, PRIVATE_0))
signature_1 = signs(extension_values(left, PRIVATE_1))
assert signature_0 != signature_1
assert signature_0 != tuple(-value for value in signature_1)
for matrix in (right, midpoint):
    assert signs(extension_values(matrix, PRIVATE_0)) == signature_0
    assert signs(extension_values(matrix, PRIVATE_1)) == signature_1

left_parent_values = parent_values(left)
right_parent_values = parent_values(right)
midpoint_parent_values = parent_values(midpoint)
changed = tuple(
    QUADS[index]
    for index in range(len(QUADS))
    if (midpoint_parent_values[index] > 0)
    != (left_parent_values[index] > 0)
)
assert changed == ((0, 2, 4, 6),)
changed_index = QUADS.index(changed[0])
assert left_parent_values[changed_index] == -2152
assert right_parent_values[changed_index] == -6772
assert midpoint_parent_values[changed_index] == 1182

chart_a = parent(CHART_A_A, CHART_A_B)
chart_b = parent(CHART_B_A, CHART_B_B)
assert signs(parent_values(chart_a)) == parent_signature
assert signs(parent_values(chart_b)) == parent_signature

margin_a = check_feasible(chart_a, signature_0, CHART_A_POINT)
margin_b = check_feasible(chart_b, signature_1, CHART_B_POINT)
assert margin_a == 999981140
assert margin_b == 996240309
check_gordan(chart_a, signature_1, CHART_A_EXCLUDES_1)
check_gordan(chart_b, signature_0, CHART_B_EXCLUDES_0)

print("PASS endpoints define the same uniform UOM(4,8) parent chirotope")
print("PASS both non-antipodal private signatures persist at the midpoint")
print("PASS midpoint reverses exactly parent bracket (0,2,4,6)")
print("PASS chart A supports sigma_0 and exactly excludes sigma_1")
print("PASS chart B supports sigma_1 and exactly excludes sigma_0")
print("PASS both regions are proper and pairwise incomparable")
print("CONCLUSION: the fixed-quotient double-lift fiber is not convex")
print("NON-CONCLUSION: this does not disprove H_7=0 or the s=2 case of 9DVL")
