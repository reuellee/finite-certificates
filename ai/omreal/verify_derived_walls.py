#!/usr/bin/env python3
"""Exact checker for the UOM(4,8) derived-wall classification.

No floating point arithmetic is used.  Orbit enumeration is exhaustive over
C(56,4) = 367,290 four-sets of triples.  Polynomial identities are checked by
expansion over ZZ; irreducibility is checked over QQ.
"""

from itertools import combinations, permutations

import sympy as sp


def edge_permute_mask(mask, permutation):
    out = 0
    for old in range(4):
        if mask & (1 << old):
            out |= 1 << permutation[old]
    return out


S4 = tuple(permutations(range(4)))


def orbit_key(edges):
    """Complete S_8 x S_4 invariant for a four-edge 3-uniform hypergraph."""
    masks = []
    for vertex in range(8):
        mask = sum((vertex in edges[j]) << j for j in range(4))
        masks.append(mask)
    candidates = []
    for permutation in S4:
        counts = [0] * 16
        for mask in masks:
            counts[edge_permute_mask(mask, permutation)] += 1
        candidates.append(tuple(counts))
    return min(candidates)


def structural(edges):
    common = set(edges[0]).intersection(*edges[1:])
    if common:
        return True
    for pair in combinations(range(8), 2):
        if sum(set(pair) <= set(edge) for edge in edges) >= 3:
            return True
    return False


triples = tuple(combinations(range(8), 3))
representatives = {}
for four_set in combinations(triples, 4):
    representatives.setdefault(orbit_key(four_set), four_set)
assert len(representatives) == 52
representatives = list(representatives.values())

# The insertion order above is stable under lexicographic combinations.  This
# independent list makes an orbit-key regression visible instead of silently
# changing the factor certificates below.
expected_representatives = (
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
).split()


def representative_string(edges):
    return "/".join("".join(str(vertex + 1) for vertex in edge) for edge in edges)


assert [representative_string(rep) for rep in representatives] == expected_representatives

a, b, c, d, e, f, g, h, i = sp.symbols("a b c d e f g h i")
variables = (a, b, c, d, e, f, g, h, i)
Y = sp.Matrix([
    [1, 0, 0, 0, 1, 1, 1, 1],
    [0, 1, 0, 0, 1, a, d, g],
    [0, 0, 1, 0, 1, b, e, h],
    [0, 0, 0, 1, 1, c, f, i],
])


def bracket(indices):
    return sp.expand(Y[:, indices].det())


brackets = {
    "".join(str(vertex + 1) for vertex in basis): bracket(basis)
    for basis in combinations(range(8), 4)
}


def normal(triple):
    columns = Y[:, triple]
    # Coefficient of v_r in det(y_i,y_j,y_k,v).
    return sp.Matrix([
        (-1) ** (row + 3)
        * columns.extract(
            [other for other in range(4) if other != row], range(3)
        ).det()
        for row in range(4)
    ])


normals = {triple: normal(triple) for triple in triples}


def derived(edges):
    return sp.expand(sp.Matrix.hstack(*(normals[edge] for edge in edges)).det())


ZERO = {0, 1, 2, 3, 4, 5, 6, 7, 8, 13, 14, 15, 24, 25}
FIXED = {
    9: (), 10: (), 11: ("1256",), 12: ("1567",),
    16: ("1236",), 17: (), 18: ("1246",), 19: ("1256",),
    20: ("1267",), 21: ("1456",), 22: ("1467",), 23: ("1678",),
    26: ("1256", "1256"), 27: ("1256", "1257"),
    28: ("1256", "1278"), 29: ("1256",),
    30: ("1347", "1256"), 31: ("1356", "1256"),
    32: ("1256", "1357"), 33: ("1256", "1378"),
    34: ("1256", "1567"), 35: ("1256", "1578"),
    40: ("3456", "1256"), 43: ("1256", "3567"),
    45: ("1256", "5678"),
}

RESIDUAL = {
    36: a*f - c*d + c - f,
    37: a*e - a*f - b*d + b + c*d - c - e + f,
    38: a*e*i - a*f*h - b*d*i + b*f*g - b*f + b*i
        + c*d*h - c*e*g + c*e - c*h - e*i + f*h,
    39: a*f - a*i - c*d*i + c*f*g - c*f + c*i + d*i - f*g,
    41: a*e - a - c*d + c + d - e,
    42: a*e - a*h - c*d*h + c*e*g - c*e + c*h + d*h - e*g,
    44: a*e*i - a*e - a*f*h + a*f + a*h - a*i + c*d*h - c*d*i
        - c*e*g + c*e + c*f*g - c*f - c*h + c*i - d*h + d*i
        + e*g - e*i - f*g + f*h,
    46: a*f - b*f - c*d + c*e,
    47: a*f - b*f - c*d + c*e,
    48: a + b*c - b - c,
    49: b*f - b + d - f,
    50: b*f - b*i + d*i - f*g,
    51: a*b*f - a*c*e + a*c*h - a*f*h - b**2*f + b*c*e
        - b*c*g + b*f*h + c*e*g - c*e*h,
}
RESIDUAL_BRACKETS = {46: ("1246",), 47: ("1248",)}

# For every genuine residual q, one coordinate derivative is a unit in the
# localization at the parent brackets.  This certifies wall nonsingularity on
# the uniform locus.  Values are (coordinate, parent-bracket product), with
# equality understood up to sign.
PIVOT = {
    36: (a, ("1237",)),
    37: (a, ("1257",)),
    38: (a, ("1278",)),
    39: (a, ("2378",)),
    41: (a, ("2457",)),
    42: (a, ("2478",)),
    44: (d, ("2356", "1258")),
    46: (a, ("1237",)),
    47: (a, ("1237",)),
    48: (a, ()),
    49: (d, ()),
    50: (d, ("1238",)),
    51: (f, ("2468", "1456")),
}


def product(labels):
    result = sp.Integer(1)
    for label in labels:
        result *= brackets[label]
    return sp.expand(result)


def equal_up_to_sign(left, right):
    return sp.expand(left - right) == 0 or sp.expand(left + right) == 0


assert (
    len(ZERO) == 14
    and len(FIXED) == 25
    and len(RESIDUAL) == len(PIVOT) == 13
)
for index, edges in enumerate(representatives):
    determinant = derived(edges)
    if index in ZERO:
        assert structural(edges)
        assert determinant == 0
    elif index in FIXED:
        assert not structural(edges)
        assert equal_up_to_sign(determinant, product(FIXED[index]))
    else:
        assert index in RESIDUAL and not structural(edges)
        right = product(RESIDUAL_BRACKETS.get(index, ())) * RESIDUAL[index]
        assert equal_up_to_sign(determinant, right)

        # The residual is a genuine non-bracket factor.  In the UFD obtained
        # by localizing at all parent brackets, an irreducible factor is a unit
        # exactly when it divides one of those brackets.
        _, factors = sp.factor_list(RESIDUAL[index], *variables)
        assert factors in ([(RESIDUAL[index], 1)], [(-RESIDUAL[index], 1)])
        assert all(
            sp.Poly(sp.gcd(RESIDUAL[index], parent), *variables).total_degree() == 0
            for parent in brackets.values()
            if parent != 0
        )
        pivot, derivative_brackets = PIVOT[index]
        derivative = sp.expand(sp.diff(RESIDUAL[index], pivot))
        assert sp.degree(RESIDUAL[index], pivot) == 1
        assert pivot not in derivative.free_symbols
        assert equal_up_to_sign(derivative, product(derivative_brackets))

# Orbits 46 and 47 are two views of one localization wall.  Their first
# three normals all annihilate y_1.  The only nonzero maximal cofactor of
# that 4-by-3 matrix is the common residual R, while a fixed 2-by-2 minor is
# a unit.  Thus their rank drops from three to exactly two on R = 0.
shared = representatives[46][:3]
assert shared == representatives[47][:3] == (
    (0, 1, 2), (0, 3, 4), (0, 5, 6)
)
shared_matrix = sp.Matrix.hstack(*(normals[edge] for edge in shared))
shared_maximal_minors = [
    sp.expand(shared_matrix.extract(rows, range(3)).det())
    for rows in combinations(range(4), 3)
]
assert shared_maximal_minors == [0, 0, 0, RESIDUAL[46]]
assert shared_matrix.extract((1, 3), (0, 1)).det() == 1

# Every fourth triple not containing vertex 1 lifts the same localization
# determinant, multiplied by its nonzero parent bracket.  Fourth triples
# containing vertex 1 give precisely the structural zero case.
for edge in triples:
    lifted = derived(shared + (edge,))
    if 0 in edge:
        assert lifted == 0
    else:
        parent_bracket = bracket((0,) + edge)
        assert parent_bracket != 0
        assert equal_up_to_sign(lifted, parent_bracket * RESIDUAL[46])

# An exact uniform point on the common wall.
wall_point = {
    a: 2, b: 3, c: 5,
    d: 7, e: sp.Rational(46, 5), f: 11,
    g: 13, h: 17, i: 19,
}
wall_matrix = sp.Matrix([
    [1, 0, 0, 0, 1, 1, 1, 1],
    [0, 1, 0, 0, 1, 2, 7, 13],
    [0, 0, 1, 0, 1, 3, sp.Rational(46, 5), 17],
    [0, 0, 0, 1, 1, 5, 11, 19],
])
assert Y.subs(wall_point) == wall_matrix
assert RESIDUAL[46].subs(wall_point) == 0
assert shared_matrix.subs(wall_point).rank() == 2
wall_brackets = [
    wall_matrix[:, basis].det() for basis in combinations(range(8), 4)
]
assert len(wall_brackets) == 70 and all(value != 0 for value in wall_brackets)

# Exhaustion plus the exact identities certifies the converse structural
# statement: precisely the predicate-positive incidence types vanish.
assert {
    index for index, edges in enumerate(representatives) if structural(edges)
} == ZERO

# Canaries: a changed residual and a changed incidence pattern must be rejected.
assert not equal_up_to_sign(derived(representatives[36]), RESIDUAL[36] + 1)
assert structural(representatives[0]) and not structural(representatives[36])

print(
    "PASS: 367290 four-sets -> 52 orbits = "
    "14 zero + 25 bracket-unit + 13 smooth residual"
)
print("PASS: all 13 residuals are affine in a bracket-unit pivot")
print("PASS: orbit-46/47 localization wall and exact uniform witness")
