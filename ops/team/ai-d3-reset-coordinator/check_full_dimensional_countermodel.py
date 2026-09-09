#!/usr/bin/env python3
"""Exact algebra/cellular audit of the full-dimensional generic D3 model.

The topology is proved by explicit homeomorphisms in the companion note.
This script does not purport to be a formal topology prover.
"""

from fractions import Fraction as Q
from itertools import combinations, permutations, product


class P(dict):
    """Small sparse rational polynomial; monomials are sorted variable tuples."""

    def __init__(self, value=0):
        if isinstance(value, dict):
            super().__init__({k: Q(v) for k, v in value.items() if v})
        elif isinstance(value, str):
            super().__init__({(value,): Q(1)})
        else:
            super().__init__({(): Q(value)} if value else {})

    def __add__(self, other):
        out = dict(self)
        for k, v in P(other).items():
            out[k] = out.get(k, Q(0)) + v
        return P(out)

    __radd__ = __add__

    def __neg__(self):
        return P({k: -v for k, v in self.items()})

    def __sub__(self, other):
        return self + -P(other)

    def __rsub__(self, other):
        return P(other) + -self

    def __mul__(self, other):
        out = {}
        for a, x in self.items():
            for b, y in P(other).items():
                k = tuple(sorted(a + b))
                out[k] = out.get(k, Q(0)) + x * y
        return P(out)

    __rmul__ = __mul__

    def __pow__(self, n):
        assert isinstance(n, int) and n >= 0
        out = P(1)
        for _ in range(n):
            out *= self
        return out

    def substitute(self, values):
        out = P()
        for monomial, coefficient in self.items():
            term = P(coefficient)
            for variable in monomial:
                term *= values.get(variable, P(variable))
            out += term
        return out

    def evaluate(self, values):
        out = self.substitute(values)
        assert all(not monomial for monomial in out)
        return out.get((), Q(0))


def require(condition, reason):
    if not condition:
        raise AssertionError(reason)


def determinant(matrix):
    n = len(matrix)
    answer = P()
    for order in permutations(range(n)):
        inversions = sum(order[i] > order[j] for i in range(n) for j in range(i + 1, n))
        term = P((-1) ** inversions)
        for i, j in enumerate(order):
            term *= matrix[i][j]
        answer += term
    return answer


def rank(matrix):
    a = [[Q(v) for v in row] for row in matrix]
    if not a:
        return 0
    pivot_row = 0
    for col in range(len(a[0])):
        pivot = next((j for j in range(pivot_row, len(a)) if a[j][col]), None)
        if pivot is None:
            continue
        a[pivot_row], a[pivot] = a[pivot], a[pivot_row]
        c = a[pivot_row][col]
        a[pivot_row] = [v / c for v in a[pivot_row]]
        for j in range(len(a)):
            if j != pivot_row:
                c = a[j][col]
                a[j] = [v - c * w for v, w in zip(a[j], a[pivot_row])]
        pivot_row += 1
        if pivot_row == len(a):
            break
    return pivot_row


def halfline_product(k, corrupt=False):
    cells = {d: [b for b in product((0, 1), repeat=k) if sum(b) == d] for d in range(k + 1)}
    delta = {}
    for d in range(k):
        matrix = [[0] * len(cells[d]) for _ in cells[d + 1]]
        for col, word in enumerate(cells[d]):
            for j, bit in enumerate(word):
                if bit == 0:
                    target = list(word)
                    target[j] = 1
                    row = cells[d + 1].index(tuple(target))
                    matrix[row][col] += (-1) ** sum(word[:j])
        delta[d] = matrix
    if corrupt:
        delta[0][0][0] = 0
    for d in range(k - 1):
        require(all(sum(delta[d + 1][i][j] * delta[d][j][l] for j in range(len(cells[d + 1]))) == 0
                    for i in range(len(cells[d + 2])) for l in range(len(cells[d]))), "cellular delta squared")
    cohomology = [len(cells[d]) - rank(delta.get(d - 1, [])) - rank(delta.get(d, [])) for d in range(k + 1)]
    require(cohomology == [0] * (k + 1), "halfline-product acyclicity")
    return cohomology


x, y, z, h = (P(v) for v in ("x", "y", "z", "h"))
u = [P(f"u{j}") for j in range(7)]
norm2 = sum(v * v for v in u)
f = [-x, -y, x + y + norm2 - 1]


def make_matrix():
    rows = []
    for j in range(3):
        for s in (1, -1):
            row = [P()] * 4
            row[j] = P(s)
            row[3] = f[j]
            rows.append(row)
    return rows + [[P(), P(), P(), P(1)] for _ in range(50)]


def signatures():
    return [[-1 if r < 6 and r % 2 and r // 2 != i else 1 for r in range(56)] for i in range(3)]


def audit_matrix(rows, signs, dual_factor=-2):
    require(len(rows) == 56 and all(len(r) == 4 for r in rows), "matrix dimensions")
    require(determinant([rows[j] for j in (0, 2, 4, 6)]) == P(1), "constant full-span determinant")
    for i in range(3):
        p = [P() if j == i else f[j] ** 2 + 1 for j in range(3)] + [P(1)]
        values = [signs[i][r] * sum(a * b for a, b in zip(row, p)) for r, row in enumerate(rows)]
        for r, actual in enumerate(values):
            if r >= 6:
                expected = P(1)
            elif r // 2 == i:
                expected = f[i]
            else:
                j = r // 2
                expected = f[j] ** 2 + 1 + (1 if r % 2 == 0 else -1) * f[j]
                completed = (f[j] + Q(1 if r % 2 == 0 else -1, 2)) ** 2 + Q(3, 4)
                require(expected == completed, "strict inactive primal inequality")
            require(actual == expected, "symbolic primal witness")
        weights = [P()] * 56
        weights[2 * i] = weights[2 * i + 1] = P(1)
        weights[6] = dual_factor * f[i]
        for col in range(4):
            require(sum(weights[r] * signs[i][r] * rows[r][col] for r in range(56)) == P(), "symbolic dual annihilation")
        require(sum(weights) == 2 - 2 * f[i], "dual normalization denominator")


def audit_geometry(boundary_constant=1):
    inverse = boundary_constant - x - norm2 - z
    require(f[2].substitute({"y": inverse}) == -z, "B02 pair chart")
    require(f[2].substitute({"x": boundary_constant - y - norm2 - z}) == -z, "B12 pair chart")
    require((x + y + norm2).substitute({"x": h * x, "y": h * y, **{f"u{j}": h * u[j] for j in range(7)}})
            == h * (x + y + norm2) - h * (1 - h) * norm2, "triple convex contraction identity")
    anchors = [(1, -1, 2), (-1, 1, 2), (-1, -1, 0)]
    for i, (a, b, c) in enumerate(anchors):
        values = {"x": a, "y": b, **{f"u{j}": c if j == 0 else 0 for j in range(7)}}
        bad = [v.evaluate(values) <= 0 for v in f]
        require(bad == [j == i for j in range(3)], "exclusive-bad anchor")
    common = {"x": -1, "y": -1, **{f"u{j}": 2 if j == 0 else 0 for j in range(7)}}
    require(all(v.evaluate(common) > 0 for v in f), "common feasible anchor")
    interior = {"x": Q(1, 4), "y": Q(1, 4), **{f"u{j}": 0 for j in range(7)}}
    require(all(v.evaluate(interior) < 0 for v in f), "triple has nonempty interior")


def audit_compactification():
    t, X, Y = P("t"), P("X"), P("Y")
    U = [P(f"U{j}") for j in range(7)]
    rename = {"x": X, "y": Y, **{f"u{j}": U[j] for j in range(7)}}
    expected = [-X * t, -Y * t, (X + Y) * t + sum(v * v for v in U) - t * t]
    for original, homogeneous in zip(f, expected):
        result = P()
        for monomial, coefficient in original.items():
            term = P(coefficient) * t ** (2 - len(monomial))
            for variable in monomial:
                term *= rename[variable]
            result += term
        require(result == homogeneous, "polynomial compactification extension")


def main():
    rows, signs = make_matrix(), signatures()
    audit_matrix(rows, signs)
    audit_geometry()
    audit_compactification()
    require(halfline_product(1) == [0, 0], "singleton cellular spine")
    require(halfline_product(2) == [0, 0, 0], "pair cellular spine")
    triples = list(combinations(range(1, 9), 3))
    require([triples[j] for j in (0, 2, 4, 6)] == [(1, 2, 3), (1, 2, 5), (1, 2, 7), (1, 3, 4)], "shared-label minor")
    require(set.intersection(*(set(triples[j]) for j in (0, 2, 4, 6))) == {1}, "parent annihilator obstruction")
    hostile = []
    hostile.append(lambda: audit_matrix(rows, signs, dual_factor=2))
    hostile.append(lambda: audit_geometry(boundary_constant=0))
    hostile.append(lambda: halfline_product(1, corrupt=True))
    hostile.append(lambda: halfline_product(2, corrupt=True))
    for i in range(3):
        damaged = [s[:] for s in signs]
        damaged[i][2 * i + 1] = -1
        hostile.append(lambda damaged=damaged: audit_matrix(rows, damaged))
    damaged_rows = [r[:] for r in rows]
    damaged_rows[6][3] = P()
    hostile.append(lambda: audit_matrix(damaged_rows, signs))
    rejected = 0
    for check in hostile:
        try:
            check()
        except AssertionError:
            rejected += 1
    require(rejected == len(hostile), "corrupt certificate escaped")
    print("PASS exact polynomial primal/dual witnesses for three signatures of one 56x4 matrix")
    print("PASS domain charts, exclusive-bad anchors, compactification, and shared-label determinant one")
    print("PASS integral half-line product relative complexes: singleton and pair cohomology zero")
    print(f"PASS hostile mutations rejected {rejected}/{len(hostile)}")
    print("SCOPE generic model only; global topology requires the explicit proof and independent review")


if __name__ == "__main__":
    main()
