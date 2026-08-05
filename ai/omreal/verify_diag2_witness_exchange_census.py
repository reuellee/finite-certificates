#!/usr/bin/env python3
"""Exhaustive minimal-circuit census for the witness-exchange falsifier.

At the exact parent-16 base chart, enumerate every support-minimal positive
Gordan circuit for the two realizable signatures in
``verify_diag2_witness_exchange_falsifier.py``.  Test all 646,880 circuit
pairs against all 56 ordered elementary shears, prove the displayed pair is
the unique incompatible pair, and compute each signature's 112-oriented-
direction escape set.
"""

from itertools import combinations
from pathlib import Path
import sys

import numpy as np


HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import verify_diag2_moving_witness_shear as moving
import verify_diag2_witness_exchange_falsifier as falsifier


SIGNATURES = (falsifier.LEFT_SIGNATURE, falsifier.RIGHT_SIGNATURE)


def determinant_rows(columns, rows):
    size = len(columns)
    if size == 1:
        return columns[0][rows[0]]
    if size == 2:
        return (
            columns[0][rows[0]] * columns[1][rows[1]]
            - columns[1][rows[0]] * columns[0][rows[1]]
        )
    if size == 3:
        selected = (tuple(vector[row] for row in rows) for vector in columns)
        return moving.det3(*selected)
    return moving.det4(*columns)


def enumerate_positive_circuits():
    normals = moving.parent_normals(moving.PARENT16)
    four_determinant_sign = {}
    for support in combinations(range(56), 4):
        value = moving.det4(*(normals[index] for index in support))
        four_determinant_sign[support] = (value > 0) - (value < 0)
    if sum(bool(value) for value in four_determinant_sign.values()) != 308_630:
        raise AssertionError("wrong full-rank four-subset census")

    circuits = [[], []]
    for support in combinations(range(56), 5):
        base_signs = []
        for omitted in range(5):
            value = four_determinant_sign[
                support[:omitted] + support[omitted + 1 :]
            ]
            if not value:
                break
            base_signs.append(value if omitted % 2 == 0 else -value)
        if len(base_signs) < 5:
            continue
        for signature_index, signature in enumerate(SIGNATURES):
            oriented = [
                base_signs[position]
                * moving.signature_sign(signature, support[position])
                for position in range(5)
            ]
            if all(value == oriented[0] for value in oriented[1:]):
                circuits[signature_index].append(support)
    if tuple(map(len, circuits)) != (622, 1022):
        raise AssertionError("wrong positive five-circuit census")

    lower_counts = [[0, 0] for _ in range(2, 5)]
    for size in range(2, 5):
        for support in combinations(range(56), size):
            columns = [normals[index] for index in support]
            relation = None
            for rows in combinations(range(4), size - 1):
                cofactors = []
                for omitted in range(size):
                    subfamily = columns[:omitted] + columns[omitted + 1 :]
                    value = determinant_rows(subfamily, rows)
                    cofactors.append(value if omitted % 2 == 0 else -value)
                if any(cofactors):
                    relation = cofactors
                    break
            if relation is None or not all(relation):
                continue
            if any(
                sum(relation[j] * columns[j][row] for j in range(size))
                for row in range(4)
            ):
                continue
            for signature_index, signature in enumerate(SIGNATURES):
                oriented = [
                    relation[position]
                    * moving.signature_sign(signature, support[position])
                    for position in range(size)
                ]
                if all(value > 0 for value in oriented) or all(
                    value < 0 for value in oriented
                ):
                    circuits[signature_index].append(support)
                    lower_counts[size - 2][signature_index] += 1
    if lower_counts != [[0, 0], [0, 0], [0, 18]]:
        raise AssertionError("wrong positive lower-circuit census")
    if tuple(map(len, circuits)) != (622, 1040):
        raise AssertionError("wrong complete minimal-circuit census")
    return tuple(tuple(family) for family in circuits)


def shear_masks(signature, support):
    positive = 0
    negative = 0
    position = 0
    for source in range(1, 9):
        for target in range(1, 9):
            if source == target:
                continue
            values = [
                moving.transport_alpha(signature, index, source, target)
                for index in support
                if moving.replacement(index, source, target) is not None
            ]
            if 1 in values:
                positive |= 1 << position
            if -1 in values:
                negative |= 1 << position
            position += 1
    if position != 56:
        raise AssertionError("wrong ordered-shear universe")
    return positive, negative


def pair_census(circuits):
    states = [
        [shear_masks(SIGNATURES[index], support) for support in circuits[index]]
        for index in range(2)
    ]
    right_positive = np.asarray(
        [state[0] for state in states[1]], dtype=np.uint64
    )
    right_negative = np.asarray(
        [state[1] for state in states[1]], dtype=np.uint64
    )
    full = np.uint64((1 << 56) - 1)
    histogram = {}
    zero_pairs = []
    one_pairs = []
    for left_index, (left_positive, left_negative) in enumerate(states[0]):
        mixed = (
            (np.uint64(left_positive) | right_positive)
            & (np.uint64(left_negative) | right_negative)
        )
        compatible_counts = np.fromiter(
            (int(value).bit_count() for value in full ^ mixed),
            dtype=np.uint8,
            count=len(mixed),
        )
        values, counts = np.unique(compatible_counts, return_counts=True)
        for value, count in zip(values, counts, strict=True):
            histogram[int(value)] = histogram.get(int(value), 0) + int(count)
        for right_index in np.flatnonzero(compatible_counts == 0):
            zero_pairs.append(
                (circuits[0][left_index], circuits[1][int(right_index)])
            )
        for right_index in np.flatnonzero(compatible_counts == 1):
            one_pairs.append(
                (circuits[0][left_index], circuits[1][int(right_index)])
            )

    expected_zero = [
        (falsifier.LEFT_CIRCUIT, falsifier.RIGHT_CIRCUIT),
    ]
    expected_one_right = {
        (16, 20, 30, 44, 53),
        (16, 20, 34, 38, 44),
        (16, 20, 34, 39, 53),
        (16, 20, 34, 40, 53),
        (16, 20, 34, 48, 53),
    }
    if zero_pairs != expected_zero:
        raise AssertionError("the incompatible circuit pair is not unique")
    if len(one_pairs) != 5 or {
        right for left, right in one_pairs if left == falsifier.LEFT_CIRCUIT
    } != expected_one_right:
        raise AssertionError("wrong one-exchange repair census")
    if sum(histogram.values()) != 622 * 1040 == 646_880:
        raise AssertionError("incomplete circuit-pair census")
    if histogram.get(0) != 1 or histogram.get(1) != 5:
        raise AssertionError("wrong low-compatibility histogram")
    return states, histogram


def escape_set(signature, circuits):
    result = set()
    for support in circuits:
        for source in range(1, 9):
            for target in range(1, 9):
                if source == target:
                    continue
                values = {
                    moving.transport_alpha(signature, index, source, target)
                    for index in support
                    if moving.replacement(index, source, target) is not None
                }
                if not values:
                    result.add((source, target, -1))
                    result.add((source, target, 1))
                elif len(values) == 1:
                    result.add((source, target, next(iter(values))))
    return result


def main():
    circuits = enumerate_positive_circuits()
    if falsifier.LEFT_CIRCUIT not in circuits[0]:
        raise AssertionError("displayed left circuit is missing")
    if falsifier.RIGHT_CIRCUIT not in circuits[1]:
        raise AssertionError("displayed right circuit is missing")
    _, histogram = pair_census(circuits)

    escape_sets = tuple(
        escape_set(signature, family)
        for signature, family in zip(SIGNATURES, circuits, strict=True)
    )
    universe = {
        (source, target, direction)
        for source in range(1, 9)
        for target in range(1, 9)
        if source != target
        for direction in (-1, 1)
    }
    if tuple(map(len, escape_sets)) != (89, 99):
        raise AssertionError("wrong escape-direction set sizes")
    if len(escape_sets[0] & escape_sets[1]) != 76:
        raise AssertionError("wrong escape-direction intersection")
    if escape_sets[0] | escape_sets[1] != universe or len(universe) != 112:
        raise AssertionError("escape-direction union is not the full universe")

    print("PASS positive minimal circuits = 622 and 1040 (including 18 four-circuits)")
    print("PASS all 646,880 circuit pairs: exactly one incompatible, five have one shear")
    print("PASS 112-direction escape sets have sizes 89,99 and intersection 76")
    print("THEOREM selected-witness compatibility fails uniquely and one exchange repairs it")
    print("SCOPE exact parent-16 census; universal escape-set intersection remains open")


if __name__ == "__main__":
    main()
