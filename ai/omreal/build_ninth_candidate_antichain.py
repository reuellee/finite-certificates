#!/usr/bin/env python3
"""Build exact properness/incomparability witnesses for the ninth stress family.

Floating-point LP is used only to locate witnesses.  Feasible rays and
infeasible Gordan circuits are rationalized and checked with integer
arithmetic before they are written.  The companion verifier has no SciPy
dependency and independently recomputes every derived normal.
"""

from fractions import Fraction
from itertools import combinations
from math import gcd, lcm
from pathlib import Path
import sys

import numpy as np
from scipy.optimize import linprog


HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from verify_seeat_upper_bound import chart_rows_and_parent


SOURCE = HERE / "data" / "seeat_parent2599_upper178.npz"
OUTPUT = HERE / "data" / "ninth_candidate_12_37_antichain.npz"
FORMAT = "ninth-candidate-12-37-antichain-v1"
CHARTS = (1, 22, 67, 69, 27, 36, 60)
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
PATTERNS = (
    "001010011",
    "010111100",
    "100101001",
    "011100100",
    "011001011",
    "100010101",
    "100111110",
)


def primitive(values):
    values = [int(value) for value in values]
    divisor = 0
    for value in values:
        divisor = gcd(divisor, abs(value))
    return [value // max(divisor, 1) for value in values]


def rational_point(target, signed_rows):
    target = np.asarray(target, dtype=float)
    target /= np.max(np.abs(target))
    for denominator in (10**6, 10**8, 10**10, 10**12, 10**14):
        candidate = primitive(np.rint(target * denominator).astype(object))
        if max(map(abs, candidate)) >= 2**63:
            continue
        if all(sum(int(a) * x for a, x in zip(row, candidate)) > 0 for row in signed_rows):
            return candidate
    raise RuntimeError("failed to rationalize a feasible extension ray")


def nullspace(matrix):
    """Exact rational nullspace of a small row matrix."""
    a = [[Fraction(int(value)) for value in row] for row in matrix]
    row_count = len(a)
    column_count = len(a[0])
    pivots = []
    row = 0
    for column in range(column_count):
        pivot = next((i for i in range(row, row_count) if a[i][column]), None)
        if pivot is None:
            continue
        a[row], a[pivot] = a[pivot], a[row]
        scale = a[row][column]
        a[row] = [value / scale for value in a[row]]
        for other in range(row_count):
            if other != row and a[other][column]:
                scale = a[other][column]
                a[other] = [x - scale * y for x, y in zip(a[other], a[row])]
        pivots.append(column)
        row += 1
        if row == row_count:
            break
    free = [column for column in range(column_count) if column not in pivots]
    answer = []
    for free_column in free:
        vector = [Fraction(0) for _ in range(column_count)]
        vector[free_column] = 1
        for equation, pivot in reversed(list(enumerate(pivots))):
            vector[pivot] = -sum(
                a[equation][column] * vector[column] for column in free
            )
        answer.append(vector)
    return answer


def integer_vector(vector):
    denominator = 1
    for value in vector:
        denominator = lcm(denominator, value.denominator)
    return primitive(value.numerator * (denominator // value.denominator) for value in vector)


def positive_circuit(signed_rows):
    raw = np.asarray(signed_rows, dtype=float)
    normalized = raw / np.linalg.norm(raw, axis=1)[:, None]
    result = linprog(
        np.zeros(len(raw)),
        A_eq=np.vstack((normalized.T, np.ones(len(raw)))),
        b_eq=np.r_[np.zeros(4), 1.0],
        bounds=(0, None),
        method="highs",
    )
    if not result.success:
        raise RuntimeError("LP did not locate the expected Gordan circuit")
    active = tuple(int(index) for index in np.where(result.x > 1e-8)[0])
    if len(active) > 5:
        raise RuntimeError(f"nonbasic Gordan support of size {len(active)}")
    for size in range(2, len(active) + 1):
        for support in combinations(active, size):
            matrix = [
                [int(signed_rows[index][coordinate]) for index in support]
                for coordinate in range(4)
            ]
            for vector in nullspace(matrix):
                if all(value > 0 for value in vector) or all(value < 0 for value in vector):
                    if vector[0] < 0:
                        vector = [-value for value in vector]
                    weights = integer_vector(vector)
                    if all(value > 0 for value in weights) and all(
                        sum(
                            weights[position] * int(signed_rows[index][coordinate])
                            for position, index in enumerate(support)
                        )
                        == 0
                        for coordinate in range(4)
                    ):
                        return support, weights
    raise RuntimeError("failed to recover an exact positive circuit")


def main():
    source = np.load(SOURCE, allow_pickle=False)
    points = np.zeros((len(CHARTS), len(SIGNATURES), 4), dtype=np.int64)
    supports = np.full((len(CHARTS), len(SIGNATURES), 5), -1, dtype=np.int8)
    weights = np.full((len(CHARTS), len(SIGNATURES), 5), "0", dtype="<U1")

    stored_weights = [[None] * len(SIGNATURES) for _ in CHARTS]
    for chart_position, (chart_index, pattern) in enumerate(zip(CHARTS, PATTERNS)):
        _, rows = chart_rows_and_parent(source["chart_matrix"][chart_index])
        rows = np.asarray(rows, dtype=object)
        for signature_position, (signature, expected) in enumerate(zip(SIGNATURES, pattern)):
            signs = np.asarray(
                [1 if (signature >> bit) & 1 else -1 for bit in range(56)],
                dtype=object,
            )
            signed = rows * signs[:, None]
            normalized = np.asarray(signed, dtype=float)
            normalized /= np.linalg.norm(normalized, axis=1)[:, None]
            result = linprog(
                np.r_[np.zeros(4), -1.0],
                A_ub=np.column_stack((-normalized, np.ones(56))),
                b_ub=np.zeros(56),
                bounds=[(-1, 1)] * 4 + [(None, None)],
                method="highs",
            )
            feasible = result.success and result.x[4] > 1e-8
            if feasible != (expected == "1"):
                raise RuntimeError(f"unexpected pattern at chart {chart_index}, signature {signature_position}")
            if feasible:
                points[chart_position, signature_position] = rational_point(result.x[:4], signed)
            else:
                support, weight = positive_circuit(signed)
                supports[chart_position, signature_position, : len(support)] = support
                stored_weights[chart_position][signature_position] = weight

    maximum_width = max(
        len(str(value))
        for row in stored_weights
        for vector in row
        if vector is not None
        for value in vector
    )
    weights = np.full(
        (len(CHARTS), len(SIGNATURES), 5), "0", dtype=f"<U{maximum_width}"
    )
    for chart_position, row in enumerate(stored_weights):
        for signature_position, vector in enumerate(row):
            if vector is not None:
                weights[chart_position, signature_position, : len(vector)] = list(map(str, vector))

    np.savez_compressed(
        OUTPUT,
        format=np.asarray(FORMAT),
        parent_index=np.asarray(2599, dtype=np.int64),
        signature=np.asarray(SIGNATURES, dtype=np.uint64),
        chart_index=np.asarray(CHARTS, dtype=np.uint16),
        pattern=np.asarray(PATTERNS),
        feasible_point=points,
        gordan_support=supports,
        gordan_weight=weights,
    )
    print("WROTE", OUTPUT)
    print("EXACT: seven chart patterns distinguish all 72 ordered signature pairs")


if __name__ == "__main__":
    main()
