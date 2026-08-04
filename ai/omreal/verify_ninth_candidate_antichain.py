#!/usr/bin/env python3
"""Exact verifier that the row-2599 ninth stress family is a proper antichain.

For each entry of seven stored chart/signature patterns, an integer extension
ray proves feasibility or a positive integer Gordan relation proves
infeasibility.  The seven patterns distinguish every ordered pair of the nine
regions.  Hence all nine regions are nonempty and proper and no one contains
another.  No floating-point arithmetic or LP is used here.
"""

from itertools import combinations
from pathlib import Path

import numpy as np


HERE = Path(__file__).resolve().parent
CERTIFICATE = HERE / "data" / "ninth_candidate_12_37_antichain.npz"
SOURCE = HERE / "data" / "seeat_parent2599_upper178.npz"
CATALOG = HERE.parent / "omgamma" / "data" / "cat_4_8.txt"
FORMAT = "ninth-candidate-12-37-antichain-v1"
PARENT_INDEX = 2599
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
CHARTS = (1, 22, 67, 69, 27, 36, 60)
PATTERNS = (
    "001010011",
    "010111100",
    "100101001",
    "011100100",
    "011001011",
    "100010101",
    "100111110",
)
TRIPLES = tuple(sorted(combinations(range(8), 3), key=lambda item: tuple(reversed(item))))
BASES = tuple(sorted(combinations(range(8), 4), key=lambda item: tuple(reversed(item))))


def determinant(matrix):
    """Small exact recursive determinant, independent of the path verifier."""
    matrix = [[int(value) for value in row] for row in matrix]
    if len(matrix) == 1:
        return matrix[0][0]
    total = 0
    for column, value in enumerate(matrix[0]):
        minor = [row[:column] + row[column + 1 :] for row in matrix[1:]]
        total += (-1 if column & 1 else 1) * value * determinant(minor)
    return total


def derived_rows(parent):
    rows = []
    for triple in TRIPLES:
        columns = [[int(parent[row, column]) for column in triple] for row in range(4)]
        normal = []
        for coordinate in range(4):
            minor = [row for row_index, row in enumerate(columns) if row_index != coordinate]
            normal.append((-1) ** (coordinate + 3) * determinant(minor))
        rows.append(tuple(normal))
    return tuple(rows)


def parent_signs(parent):
    answer = []
    for basis in BASES:
        matrix = [[int(parent[row, column]) for column in basis] for row in range(4)]
        value = determinant(matrix)
        if value == 0:
            raise AssertionError("stored chart is a nonuniform parent")
        answer.append(1 if value > 0 else -1)
    return tuple(answer)


def main():
    certificate = np.load(CERTIFICATE, allow_pickle=False)
    required = {
        "format", "parent_index", "signature", "chart_index", "pattern",
        "feasible_point", "gordan_support", "gordan_weight",
    }
    if set(certificate.files) != required:
        raise AssertionError(f"wrong certificate fields: {sorted(certificate.files)}")
    if str(certificate["format"].item()) != FORMAT:
        raise AssertionError("wrong certificate format")
    if int(certificate["parent_index"].item()) != PARENT_INDEX:
        raise AssertionError("wrong parent index")
    if tuple(map(int, certificate["signature"])) != SIGNATURES:
        raise AssertionError("wrong signature family")
    if tuple(map(int, certificate["chart_index"])) != CHARTS:
        raise AssertionError("wrong chart indices")
    if tuple(map(str, certificate["pattern"])) != PATTERNS:
        raise AssertionError("wrong feasibility patterns")

    points = certificate["feasible_point"]
    supports = certificate["gordan_support"]
    weights = certificate["gordan_weight"]
    if points.shape != (7, 9, 4) or supports.shape != (7, 9, 5) or weights.shape != (7, 9, 5):
        raise AssertionError("wrong witness-array shape")

    source = np.load(SOURCE, allow_pickle=False)
    catalog = [line.strip() for line in CATALOG.open(encoding="utf-8") if line.strip()]
    expected_parent = tuple(1 if symbol == "+" else -1 for symbol in catalog[PARENT_INDEX])

    for chart_position, (chart_index, pattern) in enumerate(zip(CHARTS, PATTERNS)):
        parent = source["chart_matrix"][chart_index]
        if parent_signs(parent) != expected_parent:
            raise AssertionError(f"chart {chart_index} does not realize parent 2599")
        rows = derived_rows(parent)
        for signature_position, (signature, expected) in enumerate(zip(SIGNATURES, pattern)):
            signed = [
                tuple(
                    (1 if (signature >> bit) & 1 else -1) * coordinate
                    for coordinate in row
                )
                for bit, row in enumerate(rows)
            ]
            support = [int(index) for index in supports[chart_position, signature_position] if int(index) >= 0]
            weight = [
                int(value)
                for index, value in zip(supports[chart_position, signature_position], weights[chart_position, signature_position])
                if int(index) >= 0
            ]
            if expected == "1":
                if support or any(int(value) for value in weights[chart_position, signature_position]):
                    raise AssertionError("feasible entry unexpectedly stores a circuit")
                point = [int(value) for value in points[chart_position, signature_position]]
                if not any(point):
                    raise AssertionError("zero feasible ray")
                if any(sum(a * x for a, x in zip(row, point)) <= 0 for row in signed):
                    raise AssertionError(f"bad feasible ray at chart {chart_index}")
            else:
                if any(int(value) for value in points[chart_position, signature_position]):
                    raise AssertionError("infeasible entry unexpectedly stores a point")
                if not 2 <= len(support) <= 5 or len(set(support)) != len(support):
                    raise AssertionError("bad Gordan support")
                if len(weight) != len(support) or any(value <= 0 for value in weight):
                    raise AssertionError("Gordan weights are not strictly positive")
                relation = [
                    sum(weight[position] * signed[index][coordinate] for position, index in enumerate(support))
                    for coordinate in range(4)
                ]
                if relation != [0, 0, 0, 0]:
                    raise AssertionError(f"bad Gordan relation at chart {chart_index}")

    # Each signature occurs and fails in the seven exact charts, proving its
    # feasibility region is nonempty and proper.  Every ordered pair (i,j)
    # has a chart containing i and excluding j, disproving F_i subset F_j.
    for signature_position in range(9):
        column = [pattern[signature_position] for pattern in PATTERNS]
        if set(column) != {"0", "1"}:
            raise AssertionError("a region was not certified nonempty and proper")
    missing_ordered_pairs = [
        (left, right)
        for left in range(9)
        for right in range(9)
        if left != right
        and not any(pattern[left] == "1" and pattern[right] == "0" for pattern in PATTERNS)
    ]
    if missing_ordered_pairs:
        raise AssertionError(f"unseparated ordered pairs: {missing_ordered_pairs}")

    print("PASS: 63 exact chart/signature feasibility or Gordan witnesses")
    print("PASS: all nine regions are nonempty and proper")
    print("PASS: seven charts distinguish all 72 ordered signature pairs")
    print("THEOREM: the nine stress regions form a proper pairwise-incomparable family")
    print("SCOPE: this validates the 9DVL input family; it does not prove F_S connected")


if __name__ == "__main__":
    main()
