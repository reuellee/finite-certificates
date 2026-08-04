#!/usr/bin/env python3
"""Exact classifier and mixed-resultant canaries for post-contraction 9DVL.

This classifies the rank-3 direction discriminants and constructs the first
one- and two-color lift resultants.  It demonstrates that the 52 rank-4
parent-derived wall labels are not the wall alphabet of the multi-contraction
normal form.
"""

from collections import Counter
from itertools import combinations

import sympy as sp


a, b, c, d, e, f, g, h = sp.symbols("a b c d e f g h")
base_variables = (a, b, c, d, e, f, g, h)
X = sp.Matrix(
    [
        [1, 0, 0, 1, 1, 1, 1, 1],
        [0, 1, 0, 1, a, c, e, g],
        [0, 0, 1, 1, b, d, f, h],
    ]
)
columns = tuple(X[:, index] for index in range(8))


def det3(vectors):
    return sp.expand(sp.Matrix.hstack(*vectors).det())


def bracket(indices):
    return det3([columns[index] for index in indices])


def pair_normal(edge):
    left, right = (columns[index] for index in edge)
    return sp.Matrix(
        [
            left[1] * right[2] - left[2] * right[1],
            left[2] * right[0] - left[0] * right[2],
            left[0] * right[1] - left[1] * right[0],
        ]
    )


def direction_discriminant(edges):
    return sp.expand(
        sp.Matrix.hstack(*(pair_normal(edge) for edge in edges)).det()
    )


def graph_type(edges):
    degrees = Counter(vertex for edge in edges for vertex in edge)
    profile = tuple(sorted(degrees.values(), reverse=True))
    return {
        (2, 2, 2): "triangle",
        (3, 1, 1, 1): "star",
        (2, 2, 1, 1): "path4",
        (2, 1, 1, 1, 1): "path3+edge",
        (1, 1, 1, 1, 1, 1): "matching",
    }[profile]


pairs = tuple(combinations(range(8), 2))
counts = Counter(graph_type(edges) for edges in combinations(pairs, 3))
assert counts == {
    "triangle": 56,
    "star": 280,
    "path4": 840,
    "path3+edge": 1680,
    "matching": 420,
}

triangle = ((0, 1), (0, 2), (1, 2))
star = ((0, 1), (0, 2), (0, 3))
path4 = ((0, 1), (1, 2), (2, 3))
path3_edge = ((0, 1), (1, 2), (3, 4))
matching = ((0, 1), (2, 3), (4, 5))

# These invariant bracket identities classify all five S_8 orbits.
assert direction_discriminant(triangle) == bracket((0, 1, 2)) ** 2
assert direction_discriminant(star) == 0
assert direction_discriminant(path4) == (
    bracket((0, 1, 2)) * bracket((1, 2, 3))
)
assert direction_discriminant(path3_edge) == (
    bracket((0, 1, 2)) * bracket((1, 3, 4))
)
matching_residual = sp.expand(
    bracket((0, 1, 4)) * bracket((2, 3, 5))
    - bracket((0, 1, 5)) * bracket((2, 3, 4))
)
assert direction_discriminant(matching) == matching_residual

# The matching orbit is the only genuine rank-3 direction discriminant.  It
# is smooth after localizing at the nonzero parent brackets.
_, matching_factors = sp.factor_list(matching_residual, *base_variables)
assert matching_factors in (
    [(matching_residual, 1)],
    [(-matching_residual, 1)],
)
parent_brackets = [bracket(basis) for basis in combinations(range(8), 3)]
assert all(
    sp.Poly(sp.gcd(matching_residual, parent), *base_variables).total_degree()
    == 0
    for parent in parent_brackets
    if parent != 0
)
assert sp.diff(matching_residual, a) == -bracket((0, 1, 5))


def parent_lift_row(basis, colors):
    """Coefficient row on (h_4,...,h_8,t_1,...,t_colors)."""
    row = [sp.Integer(0)] * (5 + colors)
    for position, element in enumerate(basis):
        if element >= 3:
            row[element - 3] = (-1) ** (5 + position) * bracket(
                tuple(other for other in basis if other != element)
            )
    return row


def extension_lift_row(color, triple, directions):
    """Coefficient row for det(y_i,y_j,y_k,(q_color,t_color))."""
    colors = len(directions)
    row = [sp.Integer(0)] * (5 + colors)
    augmented = [columns[element] for element in triple] + [directions[color]]
    for position, element in enumerate(triple):
        if element >= 3:
            row[element - 3] = (-1) ** (5 + position) * det3(
                [augmented[index] for index in range(4) if index != position]
            )
    row[5 + color] = bracket(triple)
    return row


def standard_lift_basis(directions):
    colors = len(directions)
    return [
        parent_lift_row((0, 1, 2, element), colors) for element in range(3, 8)
    ] + [
        extension_lift_row(color, (0, 1, 2), directions)
        for color in range(colors)
    ]


# For s extensions there are k=s-1 directions and L=5+k=s+4 homogeneous
# lift variables after killing the three affine-height gauge directions.
u, v, w = sp.symbols("u v w")
q = sp.Matrix((u, v, w))
one_color_basis = standard_lift_basis((q,))
assert len(one_color_basis) == 6
assert sp.Matrix(one_color_basis).det() == 1

# A maximal lift minor already recovers a direction wall; it is not one of
# the 52 parent-derived four-normal determinants.
one_color_rows = [
    extension_lift_row(0, (0, 1, 3), (q,)),
    *[
        parent_lift_row((0, 1, 2, element), 1)
        for element in range(4, 8)
    ],
    extension_lift_row(0, (0, 1, 2), (q,)),
]
delta_12 = det3([columns[0], columns[1], q])
assert sp.Matrix(one_color_rows).det() == -delta_12

# With two remaining extensions, maximal minors also contain irreducible
# cross-color resultants.  This is the first genuinely colored boundary.
u1, v1, w1, u2, v2, w2 = sp.symbols("u1 v1 w1 u2 v2 w2")
q1 = sp.Matrix((u1, v1, w1))
q2 = sp.Matrix((u2, v2, w2))
directions = (q1, q2)
two_color_basis = standard_lift_basis(directions)
assert len(two_color_basis) == 7
assert sp.Matrix(two_color_basis).det() == 1
two_color_rows = [
    extension_lift_row(0, (0, 3, 4), directions),
    extension_lift_row(1, (1, 3, 4), directions),
    *[
        parent_lift_row((0, 1, 2, element), 2)
        for element in range(5, 8)
    ],
    extension_lift_row(0, (0, 1, 2), directions),
    extension_lift_row(1, (0, 1, 2), directions),
]
mixed_resultant = sp.expand(sp.Matrix(two_color_rows).det())


def direction_form(left, right, direction):
    return det3([columns[left], columns[right], direction])


expected_mixed = -sp.expand(
    direction_form(0, 4, q1) * direction_form(1, 3, q2)
    - direction_form(0, 3, q1) * direction_form(1, 4, q2)
)
assert mixed_resultant == expected_mixed
_, mixed_factors = sp.factor_list(
    mixed_resultant,
    a,
    b,
    c,
    d,
    e,
    f,
    g,
    h,
    u1,
    v1,
    w1,
    u2,
    v2,
    w2,
)
assert mixed_factors in ([(mixed_resultant, 1)], [(-mixed_resultant, 1)])

print("PASS 3276 direction triples -> 5 S8 orbits")
print("PASS direction discriminants = 1 zero + 3 bracket-unit + 1 smooth matching")
print("PASS one-color lift minor contains a direction wall")
print("PASS two-color lift minor contains an irreducible mixed resultant")
print("CONCLUSION: post-contraction face maps require a new, color-dependent alphabet")
