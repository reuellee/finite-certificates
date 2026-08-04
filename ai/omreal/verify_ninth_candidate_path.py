#!/usr/bin/env python3
"""Exact verifier for the row-2599 charts-12/37 ninth-diagonal stress path.

The certificate connects the two exact parent charts inside the common
feasibility region of nine displayed signatures.  Every ordinary path edge
changes one homogeneous column.  Hence every constrained determinant is
constant or affine on that edge, and strict positivity at both endpoints
proves strict positivity on the whole segment.  The only jumps are exact
positive projective gauge changes, verified independently here.

This disproves the *sampled separator claim for this candidate only*.  It is
not a proof of the ninth diagonal and makes no global properness or
incomparability claim about the nine regions.
"""

from fractions import Fraction
from itertools import combinations
from math import gcd, lcm
from pathlib import Path

import numpy as np


HERE = Path(__file__).resolve().parent
CERTIFICATE = HERE / "data" / "ninth_candidate_12_37_path.npz"
SOURCE = HERE / "data" / "seeat_parent2599_upper178.npz"
CATALOG = HERE.parent / "omgamma" / "data" / "cat_4_8.txt"

FORMAT = "ninth-candidate-12-37-coordinate-path-v1"
PARENT_INDEX = 2599
ENDPOINTS = (12, 37)
SIGNATURES = (
    32577326938880,
    31532828708796544,
    3510916511430656,
    72042742044167295,
    3476291556529680,
    2137481474473987,
    58098186400358399,
    32444182421504,
    68557050812244096,
)
TRIPLES = tuple(sorted(combinations(range(8), 3), key=lambda q: tuple(reversed(q))))
BASES = tuple(sorted(combinations(range(8), 4), key=lambda q: tuple(reversed(q))))


def determinant(v, q):
    """Fraction-free exact determinant of the selected four columns."""
    matrix = [[int(v[row, col]) for col in q] for row in range(4)]
    sign = 1
    previous = 1
    for i in range(3):
        if matrix[i][i] == 0:
            pivot = next((j for j in range(i + 1, 4) if matrix[j][i]), None)
            if pivot is None:
                return 0
            matrix[i], matrix[pivot] = matrix[pivot], matrix[i]
            sign = -sign
        for j in range(i + 1, 4):
            for k in range(i + 1, 4):
                matrix[j][k] = (
                    matrix[j][k] * matrix[i][i] - matrix[j][i] * matrix[i][k]
                ) // previous
        previous = matrix[i][i]
    return sign * matrix[3][3]


def parent_signs(y):
    signs = []
    for q in BASES:
        value = determinant(y, q)
        if not value:
            raise AssertionError(f"nonuniform parent at {q}")
        signs.append(1 if value > 0 else -1)
    return tuple(signs)


def constraints(signs):
    out = [(q, sign) for q, sign in zip(BASES, signs)]
    for j, signature in enumerate(SIGNATURES):
        for bit, triple in enumerate(TRIPLES):
            sign = 1 if (signature >> bit) & 1 else -1
            out.append((triple + (8 + j,), sign))
    return tuple(out)


def exact_ok(v, q, sign):
    return sign * determinant(v, q) > 0


def assert_incidence(v, cons, label):
    if np.shape(v) != (4, 17):
        raise AssertionError(f"{label}: wrong incidence shape")
    if any(not exact_ok(v, q, sign) for q, sign in cons):
        raise AssertionError(f"{label}: determinant sign failure")


def relevant_constraints(cons):
    out = [[] for _ in range(17)]
    for q, sign in cons:
        for k in q:
            out[k].append((q, sign))
    return out


def replay(v, columns, vectors, relevant, label):
    v = np.asarray(v, dtype=object).copy()
    if len(columns) != len(vectors):
        raise AssertionError(f"{label}: update arrays disagree")
    for index, (column, vector) in enumerate(zip(columns, vectors), 1):
        k = int(column)
        if not 0 <= k < 17:
            raise AssertionError(f"{label}: bad column {k}")
        vector = [int(x) for x in vector]
        if not any(vector):
            raise AssertionError(f"{label}: zero homogeneous column")
        v[:, k] = vector
        if any(not exact_ok(v, q, sign) for q, sign in relevant[k]):
            raise AssertionError(f"{label}: update {index} leaves incidence space")
    return v


def fraction_inverse(matrix):
    n = len(matrix)
    a = [
        [Fraction(int(matrix[i][j])) for j in range(n)]
        + [Fraction(int(i == j)) for j in range(n)]
        for i in range(n)
    ]
    for column in range(n):
        pivot = next((row for row in range(column, n) if a[row][column]), None)
        if pivot is None:
            raise AssertionError("singular projective frame")
        a[column], a[pivot] = a[pivot], a[column]
        scale = a[column][column]
        a[column] = [x / scale for x in a[column]]
        for row in range(n):
            if row == column:
                continue
            scale = a[row][column]
            if scale:
                a[row] = [x - scale * y for x, y in zip(a[row], a[column])]
    return [row[n:] for row in a]


def matmul(left, right):
    return [
        [sum(left[i][k] * right[k][j] for k in range(len(right))) for j in range(len(right[0]))]
        for i in range(len(left))
    ]


def fraction_column_to_int(column):
    denominator = 1
    for value in column:
        denominator = lcm(denominator, value.denominator)
    integers = [value.numerator * (denominator // value.denominator) for value in column]
    divisor = 0
    for value in integers:
        divisor = gcd(divisor, abs(value))
    return [value // max(divisor, 1) for value in integers]


def canonicalize(v):
    """Independently reproduce the positive projective-frame gauge."""
    if determinant(v, (0, 1, 2, 3)) <= 0:
        raise AssertionError("frame GL change would reverse global orientation")
    raw = [[Fraction(int(v[i, j])) for j in range(17)] for i in range(4)]
    inverse = fraction_inverse([[raw[i][j] for j in range(4)] for i in range(4)])
    z = matmul(inverse, raw)
    frame = [1 if z[i][4] > 0 else -1 for i in range(4)]
    diagonal = [Fraction(frame[i], 1) / z[i][4] for i in range(4)]
    if any(value <= 0 for value in diagonal):
        raise AssertionError("frame normalization used a negative row scale")
    z = [[diagonal[i] * value for value in z[i]] for i in range(4)]
    for j in range(4):
        scale = Fraction(1, 1) / z[j][j]
        if scale <= 0:
            raise AssertionError("basis column rescaling is not positive")
        for i in range(4):
            z[i][j] *= scale
    for j in range(5, 8):
        target = 1 if z[0][j] > 0 else -1
        scale = Fraction(target, 1) / z[0][j]
        if scale <= 0:
            raise AssertionError("parent affine rescaling is not positive")
        for i in range(4):
            z[i][j] *= scale
    for j in range(8, 17):
        first = next((z[i][j] for i in range(4) if z[i][j]), None)
        if first is None:
            raise AssertionError("zero extension column")
        scale = Fraction(1, 1) / abs(first)
        for i in range(4):
            z[i][j] *= scale
    out = [[0] * 17 for _ in range(4)]
    for j in range(17):
        column = fraction_column_to_int([z[i][j] for i in range(4)])
        for i in range(4):
            out[i][j] = column[i]
    return np.asarray(out, dtype=object)


def projectively_equal(left, right):
    left = np.asarray(left, dtype=object)
    right = np.asarray(right, dtype=object)
    if left.shape != right.shape:
        return False
    for j in range(left.shape[1]):
        a = [int(left[i, j]) for i in range(4)]
        b = [int(right[i, j]) for i in range(4)]
        paired = next(((x, y) for x, y in zip(a, b) if x and y), None)
        if paired is None or paired[0] * paired[1] <= 0:
            return False
        if any(a[i] * b[k] != a[k] * b[i] for i in range(4) for k in range(4)):
            return False
    return True


def parse_strings(array):
    return np.asarray([[int(x) for x in row] for row in array], dtype=object)


def main():
    certificate = np.load(CERTIFICATE, allow_pickle=False)
    required = {
        "format", "parent_index", "endpoint", "signature",
        "initial_p_a", "initial_p_b", "update_col_a", "update_vec_a",
        "update_col_b", "update_vec_b", "canonical_a", "canonical_b",
        "bridge_start", "bridge_col", "bridge_vec",
    }
    if set(certificate.files) != required:
        raise AssertionError(f"wrong certificate fields: {sorted(certificate.files)}")
    if str(certificate["format"].item()) != FORMAT:
        raise AssertionError("wrong format")
    if int(certificate["parent_index"].item()) != PARENT_INDEX:
        raise AssertionError("wrong parent")
    if tuple(map(int, certificate["endpoint"])) != ENDPOINTS:
        raise AssertionError("wrong endpoints")
    if tuple(map(int, certificate["signature"])) != SIGNATURES:
        raise AssertionError("wrong signature family")

    source = np.load(SOURCE, allow_pickle=False)
    parents = [np.asarray(source["chart_matrix"][index], dtype=object) for index in ENDPOINTS]
    signs = parent_signs(parents[0])
    if parent_signs(parents[1]) != signs:
        raise AssertionError("source endpoints have different parents")
    catalog = [line.strip() for line in CATALOG.open() if line.strip()]
    expected = tuple(1 if symbol == "+" else -1 for symbol in catalog[PARENT_INDEX])
    if signs != expected:
        raise AssertionError("source endpoints do not realize catalog row 2599")
    cons = constraints(signs)
    relevant = relevant_constraints(cons)

    initial = []
    for tag, parent in zip(("a", "b"), parents):
        p = np.asarray(certificate[f"initial_p_{tag}"], dtype=object).T
        v = np.column_stack((parent, p))
        assert_incidence(v, cons, f"initial {tag.upper()}")
        initial.append(v)
    print("PASS: both exact endpoint incidences support all nine signatures")

    final_a = replay(
        initial[0], certificate["update_col_a"], certificate["update_vec_a"],
        relevant, "A chain",
    )
    final_b = replay(
        initial[1], certificate["update_col_b"], certificate["update_vec_b"],
        relevant, "B chain",
    )
    print(
        "PASS: exact one-column chains",
        len(certificate["update_col_a"]),
        "and",
        len(certificate["update_col_b"]),
        "segments",
    )

    canonical_a = parse_strings(certificate["canonical_a"])
    canonical_b = parse_strings(certificate["canonical_b"])
    if not np.array_equal(canonicalize(final_a), canonical_a):
        raise AssertionError("A canonical gauge mismatch")
    if not np.array_equal(canonicalize(final_b), canonical_b):
        raise AssertionError("B canonical gauge mismatch")
    assert_incidence(canonical_a, cons, "canonical A")
    assert_incidence(canonical_b, cons, "canonical B")

    bridge_start = parse_strings(certificate["bridge_start"])
    if not projectively_equal(canonical_a, bridge_start):
        raise AssertionError("bridge start is not a positive column rescaling of A")
    assert_incidence(bridge_start, cons, "bridge start")
    bridge_vectors = parse_strings(certificate["bridge_vec"])
    bridge_end = replay(
        bridge_start, certificate["bridge_col"], bridge_vectors, relevant, "bridge"
    )
    if not projectively_equal(bridge_end, canonical_b):
        raise AssertionError("bridge end is not projectively canonical B")
    print("PASS: exact", len(certificate["bridge_col"]), "segment rational bridge")

    total = (
        len(certificate["update_col_a"])
        + len(certificate["bridge_col"])
        + len(certificate["update_col_b"])
    )
    print("PASS: every segment changes one column and has positive exact endpoints")
    print(
        f"THEOREM: charts {ENDPOINTS[0]} and {ENDPOINTS[1]} lie in one "
        f"component of F_S ({total} segments)"
    )
    print("SCOPE: this refutes only the sampled separator candidate, not ninth-diagonal 9DVL")


if __name__ == "__main__":
    main()
