#!/usr/bin/env python3
"""Independent exact replay of the row-2599 bounded null certificate."""

from fractions import Fraction
from itertools import combinations, permutations, product
import hashlib
import json
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
DATA = HERE / "CANDIDATE_DOMAIN.json"
SOURCE = REPO / "ai" / "omreal" / "data" / "seeat_parent2599_shatter8.npz"
ZERO = (0, 0, 0, 0)
SELECTED = (0, 4, 5, 6)
TRIPLES = tuple(sorted(combinations(range(1, 9), 3), key=lambda x: tuple(reversed(x))))
BASES = tuple(combinations(range(8), 4))


def parity(permutation):
    inversions = sum(permutation[i] > permutation[j] for i in range(len(permutation)) for j in range(i + 1, len(permutation)))
    return -1 if inversions & 1 else 1


def add(left, right):
    out = dict(left)
    for key, value in right.items():
        out[key] = out.get(key, 0) + value
    return {key: value for key, value in out.items() if value}


def multiply(left, right):
    out = {}
    for a, av in left.items():
        for b, bv in right.items():
            key = tuple(x + y for x, y in zip(a, b, strict=True))
            out[key] = out.get(key, 0) + av * bv
    return {key: value for key, value in out.items() if value}


def polynomial_det(matrix):
    size = len(matrix)
    out = {}
    for permutation in permutations(range(size)):
        term = {ZERO: parity(permutation)}
        for row, column in enumerate(permutation):
            term = multiply(term, matrix[row][column])
        out = add(out, term)
    return out


def integer_det(matrix):
    total = 0
    for permutation in permutations(range(len(matrix))):
        term = parity(permutation)
        for row, column in enumerate(permutation):
            term *= int(matrix[row][column])
        total += term
    return total


def rank(matrix):
    rows = [[Fraction(value) for value in row] for row in matrix]
    pivot_row = 0
    for column in range(len(rows[0]) if rows else 0):
        pivot = next((i for i in range(pivot_row, len(rows)) if rows[i][column]), None)
        if pivot is None:
            continue
        rows[pivot_row], rows[pivot] = rows[pivot], rows[pivot_row]
        scale = rows[pivot_row][column]
        rows[pivot_row] = [value / scale for value in rows[pivot_row]]
        for i in range(len(rows)):
            if i != pivot_row and rows[i][column]:
                scale = rows[i][column]
                rows[i] = [a - scale * b for a, b in zip(rows[i], rows[pivot_row], strict=True)]
        pivot_row += 1
    return pivot_row


def evaluate(polynomial, point):
    total = Fraction(0)
    for monomial, coefficient in polynomial.items():
        term = Fraction(coefficient)
        for index, degree in enumerate(monomial):
            term *= point[index] ** degree
        total += term
    return total


def canonical_digest(payload):
    semantic = {key: value for key, value in payload.items() if key != "semantic_sha256"}
    return hashlib.sha256(json.dumps(semantic, sort_keys=True, separators=(",", ":")).encode("ascii")).hexdigest()


def reconstruct_polynomials(matrix):
    columns = [[{ZERO: int(matrix[row, column])} for column in range(8)] for row in range(4)]
    for target, source, monomial in ((4, 1, (1, 0, 0, 0)), (4, 7, (0, 1, 0, 0)), (0, 2, (0, 0, 1, 0)), (6, 1, (0, 0, 0, 1))):
        for row in range(4):
            columns[row][target] = add(columns[row][target], {monomial: int(matrix[row, source])})
    out = {}
    for basis in BASES:
        polynomial = polynomial_det([[columns[row][column] for column in basis] for row in range(4)])
        if polynomial[ZERO] < 0:
            polynomial = {key: -value for key, value in polynomial.items()}
        out["".join(str(index + 1) for index in basis)] = polynomial
    return columns, out


def signed_rows(matrix, signature):
    rows = []
    for index, triple in enumerate(TRIPLES):
        block = matrix[:, np.asarray(triple) - 1]
        normal = []
        for omitted in range(4):
            minor = np.delete(block, omitted, axis=0)
            value = (-1) ** (omitted + 5) * integer_det(minor.tolist())
            normal.append(value if (signature >> index) & 1 else -value)
        rows.append(tuple(normal))
    return rows


def actual_canary(certificate):
    signatures = [int(value) for value in certificate["signature"]]
    charts = certificate["pattern_chart"]
    weights = certificate["gordan_weight"]
    points = certificate["feasible_point"]
    base_signs = tuple(1 if integer_det(charts[0][:, basis].tolist()) > 0 else -1 for basis in BASES)
    for local_pattern in range(16):
        global_pattern = sum(((local_pattern >> bit) & 1) << index for bit, index in enumerate(SELECTED))
        matrix = charts[global_pattern]
        signs = tuple(1 if integer_det(matrix[:, basis].tolist()) > 0 else -1 for basis in BASES)
        assert signs == base_signs
        for bit, index in enumerate(SELECTED):
            rows = signed_rows(matrix, signatures[index])
            if (local_pattern >> bit) & 1:
                point = [int(value) for value in points[global_pattern, index]]
                assert all(sum(a * b for a, b in zip(row, point, strict=True)) > 0 for row in rows)
            else:
                weight = [int(value) for value in weights[global_pattern, index]]
                assert any(weight) and all(value >= 0 for value in weight)
                assert all(sum(value * row[coordinate] for value, row in zip(weight, rows, strict=True)) == 0 for coordinate in range(4))


def main():
    payload = json.loads(DATA.read_text())
    assert payload["schema"] == "diag4-s53-row2599-candidate-null-v1"
    assert canonical_digest(payload) == payload["semantic_sha256"]
    assert hashlib.sha256(SOURCE.read_bytes()).hexdigest() == payload["source"]["sha256"]
    certificate = np.load(SOURCE, allow_pickle=False)
    matrix = certificate["pattern_chart"][0]
    polynomial_columns, polynomials = reconstruct_polynomials(matrix)
    recorded = {
        item["basis"]: {tuple(term[0]): int(term[1]) for term in item["terms"]}
        for item in payload["domain"]["signed_polynomials"]
    }
    assert recorded == polynomials
    assert len(polynomials) == 70
    assert sum(len(value) > 1 for value in polynomials.values()) == 48
    assert sum(any(sum(key) >= 2 for key in value) for value in polynomials.values()) == 16
    assert all(all(degree <= 1 for degree in key) for value in polynomials.values() for key in value)

    # Support normals are literally constant under the motion.
    for support_index in (0, 2, 31, 42, 48):
        triple = tuple(label - 1 for label in TRIPLES[support_index])
        for omitted in range(4):
            kept = [row for row in range(4) if row != omitted]
            got = polynomial_det([[polynomial_columns[row][column] for column in triple] for row in kept])
            expected = integer_det([[matrix[row, column] for column in triple] for row in kept])
            assert got == {ZERO: expected}

    # Exact boundedness witnesses.
    expected_terms = {
        "3458": {ZERO: 245451, (1, 0, 0, 0): 336697},
        "1358": {ZERO: 172497, (1, 0, 0, 0): -203756},
        "1235": {ZERO: 485532, (0, 1, 0, 0): 203756},
        "3456": {ZERO: 355617, (0, 1, 0, 0): -83738, (1, 0, 0, 0): 651761},
        "1268": {ZERO: 342093, (0, 0, 1, 0): 37757},
        "1278": {ZERO: 145151, (0, 0, 1, 0): -241453},
        "1367": {ZERO: 284598, (0, 0, 0, 1): 369836},
        "3467": {ZERO: 333089, (0, 0, 0, 1): -651761},
    }
    assert all(polynomials[basis] == value for basis, value in expected_terms.items())

    # Multi-affine vertex interpolation certifies the whole closed cube.
    minimum = None
    for basis, polynomial in polynomials.items():
        for signs in product((-1, 1), repeat=4):
            value = evaluate(polynomial, tuple(Fraction(sign, 84) for sign in signs))
            record = (value, basis, signs)
            minimum = record if minimum is None or record < minimum else minimum
    assert minimum == (Fraction(878, 21), "5678", (1, -1, -1, 1))
    failed = evaluate(polynomials["5678"], (Fraction(1, 83), Fraction(-1, 83), Fraction(-1, 83), Fraction(1, 83)))
    assert failed == Fraction(-9050, 83)

    # Relative cube cochains: modulo its boundary, only the top four-cell remains.
    relative_counts = []
    for degree in range(5):
        cells = [state for state in product((0, 1, 2), repeat=4) if state.count(1) == degree]
        relative_counts.append(sum(all(value == 1 for value in state) for state in cells))
    assert relative_counts == [0, 0, 0, 0, 1]
    assert payload["certified_local_cube"]["hc_ranks_degrees_0_to_4"] == [0, 0, 0, 0, 1]

    # Hostile canaries: abstract kernel, sign mutation, and inclusion failure.
    assert 2 - rank([[-1, -1], [1, 1]]) == 1  # abstract false positive
    assert 2 - rank([[1, -1], [1, 1]]) == 0  # sign mutation kills it
    assert 1 - rank([[0]]) == 1              # annulus/circle H1
    assert 1 - rank([[1]]) == 0              # filled disk kills that generator
    actual_canary(certificate)

    assert payload["global_gates"] == {
        "counterexample": "NOT_CLAIMED",
        "full_closed_piece_inclusion_map": "UNREACHED",
        "whole_domain_cell_decomposition": "UNREACHED",
        "whole_domain_hc3": "UNREACHED",
    }
    print("PASS exact row-2599 tuple and 70-polynomial multi-affine domain")
    print("PASS bounded outer enclosure and actual-realizable positive canary")
    print("PASS U=(-1/84,1/84)^4: exact vertex certificate and H_c^3(U)=0")
    print("PASS abstract-false-positive / sign-mutation / boundary / inclusion-failure canaries")
    print("OUTCOME INCONCLUSIVE: whole-domain topology and full-piece inclusion UNREACHED")


if __name__ == "__main__":
    main()
