#!/usr/bin/env python3
"""Build and verify an exact two-cell residual roadmap inside parent 2599.

Starting with exact chart 0 of the stored 178-chart bank, vary matrix entry
(row 2, column 7), zero based:

    Y(t) = Y_0 + t E_(2,7).

On the closed rational segment [3/25, 247/2000], exact Sturm calculations for
all 84,840 labeled residual derived determinants prove that there is one and
only one residual crossing parameter.  Its value is the rational number
342087779263/2802352748594.  Exact recursive central-arrangement enumeration
labels the left cell, wall, and right cell by all supported signatures.

The result is a complete roadmap for this one-dimensional slice, not for the
full nine-dimensional parent realization cell.
"""

from __future__ import annotations

import argparse
from fractions import Fraction
from itertools import combinations, permutations
from math import gcd
from pathlib import Path

import numpy as np

import DIAG9_GRAPH_exact_topes as topes


HERE = Path(__file__).resolve().parent
SOURCE = HERE / "data" / "seeat_parent2599_upper178.npz"
CATALOG = HERE.parent / "omgamma" / "data" / "cat_4_8.txt"
ROADMAP = HERE / "data" / "DIAG9_GRAPH_row2599_slice_roadmap.npz"
GRAPH = HERE / "data" / "DIAG9_GRAPH_row2599_slice_graph.npz"

FORMAT = "diag9-row2599-r2c7-slice-v1"
GRAPH_FORMAT = "diag9-labeled-master-tree-v1"
PARENT_INDEX = 2599
SOURCE_CHART = 0
VARYING_ROW = 2
VARYING_COLUMN = 7
SEGMENT = (Fraction(3, 25), Fraction(247, 2000))
SAMPLES = (Fraction(121, 1000), Fraction(123, 1000))
WALL = Fraction(342087779263, 2802352748594)
RESIDUAL_TYPES = (36, 37, 38, 39, 41, 42, 44, 46, 47, 48, 49, 50, 51)
REPRESENTATIVES = (
    "123/124/345/367",
    "123/124/345/567",
    "123/124/345/678",
    "123/124/356/378",
    "123/124/356/457",
    "123/124/356/478",
    "123/124/356/578",
    "123/145/167/246",
    "123/145/167/248",
    "123/145/246/356",
    "123/145/246/357",
    "123/145/246/378",
    "123/145/267/468",
)


S4 = tuple(permutations(range(4)))
MASK_PERMUTATIONS = tuple(
    tuple(
        sum(((mask >> old) & 1) << permutation[old] for old in range(4))
        for mask in range(16)
    )
    for permutation in S4
)


def parse_representative(text):
    return tuple(
        tuple(int(symbol) - 1 for symbol in triple) for triple in text.split("/")
    )


def orbit_key(edges):
    masks = tuple(
        sum((vertex in edges[edge]) << edge for edge in range(4))
        for vertex in range(8)
    )
    candidates = []
    for permutation in MASK_PERMUTATIONS:
        counts = [0] * 16
        for mask in masks:
            counts[permutation[mask]] += 1
        candidates.append(tuple(counts))
    return min(candidates)


RESIDUAL_KEYS = frozenset(
    orbit_key(parse_representative(text)) for text in REPRESENTATIVES
)


def residual_foursets():
    answer = tuple(
        fourset
        for fourset in combinations(range(56), 4)
        if orbit_key(tuple(topes.TRIPLES[index] for index in fourset))
        in RESIDUAL_KEYS
    )
    if len(RESIDUAL_KEYS) != 13 or len(answer) != 84_840:
        raise AssertionError("residual orbit exhaustion failed")
    return answer


def det3(left, middle, right):
    return (
        left[0] * (middle[1] * right[2] - middle[2] * right[1])
        - left[1] * (middle[0] * right[2] - middle[2] * right[0])
        + left[2] * (middle[0] * right[1] - middle[1] * right[0])
    )


def det4(vectors):
    first, second, third, fourth = vectors
    return (
        first[0] * det3(second[1:], third[1:], fourth[1:])
        - first[1]
        * det3(
            (second[0], second[2], second[3]),
            (third[0], third[2], third[3]),
            (fourth[0], fourth[2], fourth[3]),
        )
        + first[2]
        * det3(
            (second[0], second[1], second[3]),
            (third[0], third[1], third[3]),
            (fourth[0], fourth[1], fourth[3]),
        )
        - first[3] * det3(second[:3], third[:3], fourth[:3])
    )


def primitive_polynomial(coefficients):
    coefficients = list(map(int, coefficients))
    while coefficients and coefficients[-1] == 0:
        coefficients.pop()
    if not coefficients:
        return ()
    divisor = 0
    for coefficient in coefficients:
        divisor = gcd(divisor, abs(coefficient))
    coefficients = [coefficient // max(divisor, 1) for coefficient in coefficients]
    if coefficients[-1] < 0:
        coefficients = [-coefficient for coefficient in coefficients]
    return tuple(coefficients)


def derived_polynomial(fourset, intercept, slope):
    changing = tuple(
        position for position, index in enumerate(fourset) if any(slope[index])
    )
    coefficients = [0] * (len(changing) + 1)
    for mask in range(1 << len(changing)):
        selected = {
            changing[index]
            for index in range(len(changing))
            if mask & (1 << index)
        }
        vectors = tuple(
            slope[row_index] if position in selected else intercept[row_index]
            for position, row_index in enumerate(fourset)
        )
        coefficients[len(selected)] += det4(vectors)
    return primitive_polynomial(coefficients)


def trim(polynomial):
    polynomial = list(map(Fraction, polynomial))
    while polynomial and polynomial[-1] == 0:
        polynomial.pop()
    return polynomial


def polynomial_value(polynomial, value):
    answer = Fraction(0)
    for coefficient in reversed(polynomial):
        answer = answer * value + coefficient
    return answer


def polynomial_divrem(dividend, divisor):
    dividend = trim(dividend)
    divisor = trim(divisor)
    if not divisor:
        raise ZeroDivisionError
    while len(dividend) >= len(divisor):
        quotient = dividend[-1] / divisor[-1]
        shift = len(dividend) - len(divisor)
        for index, coefficient in enumerate(divisor):
            dividend[index + shift] -= quotient * coefficient
        dividend = trim(dividend)
    return dividend


def sturm_sequence(polynomial):
    polynomial = trim(polynomial)
    if len(polynomial) <= 1:
        return tuple(polynomial and (polynomial,))
    derivative = trim(
        index * polynomial[index] for index in range(1, len(polynomial))
    )
    sequence = [polynomial, derivative]
    while derivative:
        remainder = [-value for value in polynomial_divrem(polynomial, derivative)]
        if not remainder:
            break
        sequence.append(remainder)
        polynomial, derivative = derivative, remainder
    return tuple(sequence)


def sign_variations(sequence, value):
    signs = []
    for polynomial in sequence:
        evaluation = polynomial_value(polynomial, value)
        if evaluation:
            signs.append(1 if evaluation > 0 else -1)
    return sum(left != right for left, right in zip(signs, signs[1:]))


def root_count(polynomial, left, right):
    if len(polynomial) <= 1:
        return 0
    if polynomial_value(polynomial, left) == 0 or polynomial_value(polynomial, right) == 0:
        raise AssertionError("Sturm endpoint lies on a derived wall")
    sequence = sturm_sequence(polynomial)
    return sign_variations(sequence, left) - sign_variations(sequence, right)


def scaled_parent(base, parameter):
    matrix = np.asarray(base, dtype=object) * parameter.denominator
    matrix[VARYING_ROW, VARYING_COLUMN] += parameter.numerator
    return matrix


def source_parent():
    source = np.load(SOURCE, allow_pickle=False)
    if int(source["parent_index"].item()) != PARENT_INDEX:
        raise AssertionError("wrong source parent")
    return np.asarray(source["chart_matrix"][SOURCE_CHART], dtype=object)


def expected_parent_signs():
    catalog = [line.strip() for line in CATALOG.open(encoding="utf-8") if line.strip()]
    return tuple(1 if symbol == "+" else -1 for symbol in catalog[PARENT_INDEX])


def slice_polynomials(base):
    intercept = topes.derived_rows(base, normalize=False)
    unit = np.asarray(base, dtype=object).copy()
    unit[VARYING_ROW, VARYING_COLUMN] += 1
    next_rows = topes.derived_rows(unit, normalize=False)
    slope = tuple(
        tuple(right - left for left, right in zip(first, second))
        for first, second in zip(intercept, next_rows)
    )
    # Normal determinants are affine in the one varying matrix entry.
    double = np.asarray(base, dtype=object).copy()
    double[VARYING_ROW, VARYING_COLUMN] += 2
    double_rows = topes.derived_rows(double, normalize=False)
    if any(
        tuple(first + 2 * delta for first, delta in zip(row, change)) != check
        for row, change, check in zip(intercept, slope, double_rows)
    ):
        raise AssertionError("derived normal is not affine on the coordinate line")
    return intercept, slope


def enumerate_wall_occurrences(base):
    intercept, slope = slice_polynomials(base)
    occurrences = []
    for fourset in residual_foursets():
        polynomial = derived_polynomial(fourset, intercept, slope)
        if not polynomial:
            raise AssertionError("generic source slice lies in a residual wall")
        count = root_count(polynomial, *SEGMENT)
        if count not in (0, 1):
            raise AssertionError("residual occurrence has multiple roots in slice segment")
        if count:
            if polynomial_value(polynomial, WALL) != 0:
                raise AssertionError("slice contains a second residual crossing root")
            derivative = tuple(
                index * polynomial[index] for index in range(1, len(polynomial))
            )
            if polynomial_value(derivative, WALL) == 0:
                raise AssertionError("slice is tangent to the residual wall")
            occurrences.append(fourset)
    if not occurrences:
        raise AssertionError("slice unexpectedly contains no residual wall")
    return tuple(occurrences)


def all_topes(base):
    result = []
    for parameter in (*SAMPLES[:1], WALL, *SAMPLES[1:]):
        matrix = scaled_parent(base, parameter)
        if topes.parent_signs(matrix) != expected_parent_signs():
            raise AssertionError("slice sample leaves parent 2599")
        rows = topes.derived_rows(matrix)
        chamber_topes = topes.enumerate_topes(rows, dimension=4)
        topes.verify_topes(rows, chamber_topes)
        result.append(tuple(sorted(chamber_topes)))
    return tuple(result)


def build():
    base = source_parent()
    # Parent brackets are affine in t.  Equal nonzero endpoint signs certify
    # the entire closed segment remains in the parent cell.
    expected = expected_parent_signs()
    for endpoint in SEGMENT:
        if topes.parent_signs(scaled_parent(base, endpoint)) != expected:
            raise AssertionError("segment endpoint leaves parent 2599")

    occurrences = enumerate_wall_occurrences(base)
    left, wall, right = all_topes(base)
    left_set, wall_set, right_set = map(set, (left, wall, right))
    if wall_set != left_set & right_set:
        raise AssertionError("wall labels are not the exact two-sided intersection")
    if len(left) != len(right) != 26_112:
        raise AssertionError("wrong generic derived-arrangement chamber count")
    if len(left) != 26_112 or len(right) != 26_112:
        raise AssertionError("wrong generic derived-arrangement chamber count")
    if len(wall) != 26_040:
        raise AssertionError("wrong wall tope count")
    if len(left_set - right_set) != 72 or len(right_set - left_set) != 72:
        raise AssertionError("wrong wall mutation label difference")

    np.savez_compressed(
        ROADMAP,
        format=np.asarray(FORMAT),
        parent_index=np.asarray(PARENT_INDEX, dtype=np.int64),
        source_chart=np.asarray(SOURCE_CHART, dtype=np.int64),
        varying_position=np.asarray((VARYING_ROW, VARYING_COLUMN), dtype=np.int8),
        segment_num=np.asarray(tuple(value.numerator for value in SEGMENT), dtype=np.int64),
        segment_den=np.asarray(tuple(value.denominator for value in SEGMENT), dtype=np.int64),
        sample_num=np.asarray(tuple(value.numerator for value in SAMPLES), dtype=np.int64),
        sample_den=np.asarray(tuple(value.denominator for value in SAMPLES), dtype=np.int64),
        wall_num=np.asarray(WALL.numerator, dtype=np.int64),
        wall_den=np.asarray(WALL.denominator, dtype=np.int64),
        wall_fourset=np.asarray(occurrences, dtype=np.uint8),
        left_tope=np.asarray(left, dtype=np.uint64),
        wall_tope=np.asarray(wall, dtype=np.uint64),
        right_tope=np.asarray(right, dtype=np.uint64),
    )
    # Quotient the complete slice labels by equal support rows.  The common
    # row is improper on the slice; the two proper rows are left-only/right-only.
    np.savez_compressed(
        GRAPH,
        format=np.asarray(GRAPH_FORMAT),
        edge=np.asarray(((0, 1),), dtype=np.int64),
        support=np.asarray(((1, 0), (0, 1)), dtype=np.uint8),
        tree_edge=np.asarray(((0, 1),), dtype=np.int64),
    )
    print("WROTE", ROADMAP)
    print("WROTE", GRAPH)


def load_fraction_pairs(numerators, denominators):
    return tuple(
        Fraction(int(numerator), int(denominator))
        for numerator, denominator in zip(numerators, denominators)
    )


def verify():
    certificate = np.load(ROADMAP, allow_pickle=False)
    required = {
        "format",
        "parent_index",
        "source_chart",
        "varying_position",
        "segment_num",
        "segment_den",
        "sample_num",
        "sample_den",
        "wall_num",
        "wall_den",
        "wall_fourset",
        "left_tope",
        "wall_tope",
        "right_tope",
    }
    if set(certificate.files) != required:
        raise AssertionError(f"wrong roadmap fields: {sorted(certificate.files)}")
    if str(certificate["format"].item()) != FORMAT:
        raise AssertionError("wrong roadmap format")
    if int(certificate["parent_index"].item()) != PARENT_INDEX:
        raise AssertionError("wrong parent index")
    if int(certificate["source_chart"].item()) != SOURCE_CHART:
        raise AssertionError("wrong source chart")
    if tuple(map(int, certificate["varying_position"])) != (
        VARYING_ROW,
        VARYING_COLUMN,
    ):
        raise AssertionError("wrong varying matrix entry")
    if load_fraction_pairs(certificate["segment_num"], certificate["segment_den"]) != SEGMENT:
        raise AssertionError("wrong slice segment")
    if load_fraction_pairs(certificate["sample_num"], certificate["sample_den"]) != SAMPLES:
        raise AssertionError("wrong slice samples")
    if Fraction(
        int(certificate["wall_num"].item()), int(certificate["wall_den"].item())
    ) != WALL:
        raise AssertionError("wrong wall parameter")
    if not SEGMENT[0] < SAMPLES[0] < WALL < SAMPLES[1] < SEGMENT[1]:
        raise AssertionError("slice parameters have wrong order")

    base = source_parent()
    expected = expected_parent_signs()
    if topes.parent_signs(base) != expected:
        raise AssertionError("source chart does not realize parent 2599")
    for endpoint in SEGMENT:
        if topes.parent_signs(scaled_parent(base, endpoint)) != expected:
            raise AssertionError("parent sign failure at segment endpoint")

    occurrences = enumerate_wall_occurrences(base)
    stored_occurrences = tuple(
        tuple(map(int, row)) for row in certificate["wall_fourset"]
    )
    if stored_occurrences != occurrences:
        raise AssertionError("stored wall-occurrence list is wrong")

    recomputed = all_topes(base)
    stored = tuple(
        tuple(map(int, certificate[field]))
        for field in ("left_tope", "wall_tope", "right_tope")
    )
    if stored != recomputed:
        raise AssertionError("stored complete tope labels disagree")
    left, wall, right = map(set, stored)
    if wall != left & right:
        raise AssertionError("two-sided wall label equality fails")
    if (len(left), len(wall), len(right)) != (26_112, 26_040, 26_112):
        raise AssertionError("wrong exact slice tope counts")
    if (len(left - right), len(right - left)) != (72, 72):
        raise AssertionError("wrong exact changed-label counts")

    graph = np.load(GRAPH, allow_pickle=False)
    if set(graph.files) != {"format", "edge", "support", "tree_edge"}:
        raise AssertionError("wrong slice graph fields")
    if str(graph["format"].item()) != GRAPH_FORMAT:
        raise AssertionError("wrong slice graph format")
    expected_support = np.asarray(((1, 0), (0, 1)), dtype=np.uint8)
    if not np.array_equal(graph["support"], expected_support):
        raise AssertionError("wrong proper-region quotient on slice")
    observed_patterns = {
        (int(signature in left), int(signature in right))
        for signature in left | right
    }
    if observed_patterns != {(1, 0), (0, 1), (1, 1)}:
        raise AssertionError("unexpected signature support pattern on slice")

    print(f"PASS: all 84,840 residual occurrences have exact Sturm coverage")
    print(f"PASS: one crossing parameter has {len(occurrences)} labeled occurrences")
    print("PASS: exact complete labels 26112 -- 26040 -- 26112")
    print("PASS: exactly 72 signatures are lost and 72 gained across the wall")
    print("THEOREM: certified two-cell labeled residual roadmap inside parent 2599")
    print("SCOPE: complete on the displayed 1D slice, not the 9D parent cell")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--build", action="store_true")
    args = parser.parse_args()
    if args.build:
        build()
    verify()


if __name__ == "__main__":
    main()
