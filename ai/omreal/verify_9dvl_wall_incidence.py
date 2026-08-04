#!/usr/bin/env python3
"""Exact two-wall obstruction to a 52-label 9DVL face complex.

The 52 labels classify one four-normal dependence up to S_8.  This checker
shows that they do not determine even pairwise face incidence: two distinct
pairs carrying the same label multiset {46, 46} are respectively coincident
and disjoint on the uniform locus.

Only exact symbolic arithmetic is used.
"""

from itertools import combinations

import sympy as sp


a, b, c, d, e, f, g, h, i = sp.symbols("a b c d e f g h i")
variables = (a, b, c, d, e, f, g, h, i)
Y = sp.Matrix(
    [
        [1, 0, 0, 0, 1, 1, 1, 1],
        [0, 1, 0, 0, 1, a, d, g],
        [0, 0, 1, 0, 1, b, e, h],
        [0, 0, 0, 1, 1, c, f, i],
    ]
)


def bracket(indices):
    return sp.expand(Y[:, indices].det())


def normal(triple):
    columns = Y[:, triple]
    return sp.Matrix(
        [
            (-1) ** (row + 3)
            * columns.extract(
                [other for other in range(4) if other != row], range(3)
            ).det()
            for row in range(4)
        ]
    )


def derived(edges):
    return sp.expand(sp.Matrix.hstack(*(normal(edge) for edge in edges)).det())


def permute(edges, permutation):
    return tuple(
        sorted(tuple(sorted(permutation[vertex] for vertex in edge)) for edge in edges)
    )


def equal_up_to_sign(left, right):
    return sp.expand(left - right) == 0 or sp.expand(left + right) == 0


# Orbit-46 representative 123/145/167/246.
A = ((0, 1, 2), (0, 3, 4), (0, 5, 6), (1, 3, 5))

# Swapping labels 6 and 7 gives another orbit-46 instance.  It has the same
# first three normals, so its wall is literally the same localization wall.
swap_67 = (0, 1, 2, 3, 4, 6, 5, 7)
C = permute(A, swap_67)
assert C == ((0, 1, 2), (0, 3, 4), (0, 5, 6), (1, 3, 6))

# Swapping labels 1 and 4 gives a third orbit-46 instance.
swap_14 = (3, 1, 2, 0, 4, 5, 6, 7)
B = permute(A, swap_14)
assert B == ((0, 1, 5), (0, 3, 4), (1, 2, 3), (3, 5, 6))

q1 = a * f - b * f - c * d + c * e
q2 = a - b - d + e

# Parent-bracket factors are units on every uniform realization cell.
assert equal_up_to_sign(derived(A), bracket((0, 1, 3, 5)) * q1)  # [1246] q1
assert equal_up_to_sign(derived(C), bracket((0, 1, 3, 6)) * q1)  # [1247] q1
assert equal_up_to_sign(derived(B), bracket((0, 1, 3, 5)) * q2)  # [1246] q2

# The coincident pair is nonempty and codimension one on the uniform locus.
wall_point = {
    a: 2,
    b: 3,
    c: 5,
    d: 7,
    e: sp.Rational(46, 5),
    f: 11,
    g: 13,
    h: 17,
    i: 19,
}
all_brackets = [bracket(basis) for basis in combinations(range(8), 4)]
assert q1.subs(wall_point) == 0
assert all(parent.subs(wall_point) != 0 for parent in all_brackets)
assert sp.diff(q1, a).subs(wall_point) != 0

# In contrast, A and B cannot meet anywhere on the uniform locus.  The exact
# identity puts a product of two inverted parent brackets in (q1,q2).
b1456 = bracket((0, 3, 4, 5))
b2367 = bracket((1, 2, 5, 6))
assert sp.expand(q1 - c * q2 + b1456 * b2367) == 0
assert b1456 == -a + b
assert b2367 == -c + f

print("PASS all three determinants have derived-wall orbit type 46")
print("PASS one {46,46} pair is the same nonempty smooth wall")
print("PASS another {46,46} pair is disjoint on the uniform locus")
print("CONCLUSION: 52 one-wall labels do not determine pairwise face incidence")
