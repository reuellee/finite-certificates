#!/usr/bin/env python3
"""Exhaustive circuit-exchange census at the realized type-50 birth.

The selected positive 4+5 circuit pair is incompatible for every ordered
shear.  This verifier enumerates every positive support-minimal circuit for
both signatures at that exact wall point, then proves that the selected pair
is the unique incompatible choice among all 208,262 circuit pairs.  A
one-triple exchange in the eta witness supplies twelve compatible shears.
"""

from collections import Counter
from itertools import combinations
import hashlib

import numpy as np

import DIAG2_PIVOT_LABELED_PAIR_ORBITS_VERIFY as labeled
import DIAG9_GRAPH_exact_topes as exact_topes
import verify_diag2_moving_witness_shear as moving

import verify_diag2_canonical_robust_edges as wall_tools
import verify_diag2_generic_birth_exchange_repair as repair


POINT = repair.POINT
RHO = repair.RHO
ETA = repair.ETA
SIGNATURES = (RHO, ETA)
SELECTED = (
    labeled.occurrence_representatives()[repair.WALL_TYPE],
    repair.parse_support(repair.PARTNER_TEXT),
)
FULL_SHEAR_MASK = (1 << 56) - 1
EXPECTED_FOUR_SUBSETS = 367290
EXPECTED_DEPENDENT_FOURS = 58661
EXPECTED_MINIMAL_FIVES = 2021940
EXPECTED_CIRCUITS = (101, 2062)
EXPECTED_LOWER = ({4: 1}, {4: 48})
EXPECTED_PAIRS = 208262
EXPECTED_REPAIR = "123/356/247/167/148"
EXPECTED_DIGEST = "4d3ae50be6d6f86794e9b25afb83100a4262bc2f5dbb0990d06c9020c8cb8521"


def determinant_rows(columns, rows):
    size = len(columns)
    if size == 1:
        return columns[0][rows[0]]
    if size == 2:
        return columns[0][rows[0]] * columns[1][rows[1]] - columns[1][rows[0]] * columns[0][rows[1]]
    if size == 3:
        selected = (tuple(vector[row] for row in rows) for vector in columns)
        return moving.det3(*selected)
    return moving.det4(*columns)


def enumerate_positive_circuits(normals):
    four_sign = {}
    zero_four = 0
    for support in combinations(range(56), 4):
        value = moving.det4(*(normals[index] for index in support))
        sign = (value > 0) - (value < 0)
        four_sign[support] = sign
        zero_four += sign == 0
    if len(four_sign) != EXPECTED_FOUR_SUBSETS or zero_four != EXPECTED_DEPENDENT_FOURS:
        raise AssertionError("the four-subset dependence census changed")
    print(f"FOUR_SUBSETS total={len(four_sign)} dependent={zero_four}", flush=True)

    circuits = [[], []]
    five_tested = 0
    for support in combinations(range(56), 5):
        base_signs = []
        for omitted in range(5):
            value = four_sign[support[:omitted] + support[omitted + 1 :]]
            if not value:
                break
            base_signs.append(value if omitted % 2 == 0 else -value)
        if len(base_signs) < 5:
            continue
        five_tested += 1
        for signature_index, signature in enumerate(SIGNATURES):
            oriented = tuple(
                base_signs[position] * moving.signature_sign(signature, support[position])
                for position in range(5)
            )
            if all(value == oriented[0] for value in oriented[1:]):
                circuits[signature_index].append(support)
    if five_tested != EXPECTED_MINIMAL_FIVES:
        raise AssertionError("the minimal five-support census changed")
    print(
        f"FIVE_BASES minimal_candidates={five_tested} "
        f"positive={len(circuits[0])}/{len(circuits[1])}",
        flush=True,
    )

    lower = [Counter(), Counter()]
    for size in range(2, 5):
        for support in combinations(range(56), size):
            columns = [normals[index] for index in support]
            relation = None
            for coordinates in combinations(range(4), size - 1):
                cofactors = []
                for omitted in range(size):
                    subfamily = columns[:omitted] + columns[omitted + 1 :]
                    value = determinant_rows(subfamily, coordinates)
                    cofactors.append(value if omitted % 2 == 0 else -value)
                if any(cofactors):
                    relation = cofactors
                    break
            if relation is None or not all(relation):
                continue
            if any(
                sum(relation[position] * columns[position][row] for position in range(size))
                for row in range(4)
            ):
                continue
            for signature_index, signature in enumerate(SIGNATURES):
                oriented = tuple(
                    relation[position] * moving.signature_sign(signature, support[position])
                    for position in range(size)
                )
                if all(value > 0 for value in oriented) or all(value < 0 for value in oriented):
                    circuits[signature_index].append(support)
                    lower[signature_index][size] += 1
    circuits = tuple(tuple(sorted(family, key=lambda x: (len(x), x))) for family in circuits)
    if tuple(map(len, circuits)) != EXPECTED_CIRCUITS:
        raise AssertionError("the positive minimal-circuit census changed")
    if tuple(map(dict, lower)) != EXPECTED_LOWER:
        raise AssertionError("the lower-support circuit census changed")
    return circuits, tuple(lower)


def shear_masks(signature, support):
    positive = negative = 0
    position = 0
    for source in range(1, 9):
        for target in range(1, 9):
            if source == target:
                continue
            values = tuple(
                moving.transport_alpha(signature, index, source, target)
                for index in support
                if moving.replacement(index, source, target) is not None
            )
            if 1 in values:
                positive |= 1 << position
            if -1 in values:
                negative |= 1 << position
            position += 1
    return positive, negative


def compatible_mask(left, right):
    mixed = (left[0] | right[0]) & (left[1] | right[1])
    return FULL_SHEAR_MASK ^ mixed


def support_text(support):
    return "/".join("".join(map(str, moving.TRIPLES[index])) for index in support)


def pair_census(circuits):
    states = tuple(
        tuple(shear_masks(signature, support) for support in family)
        for signature, family in zip(SIGNATURES, circuits, strict=True)
    )
    right_positive = np.asarray([state[0] for state in states[1]], dtype=np.uint64)
    right_negative = np.asarray([state[1] for state in states[1]], dtype=np.uint64)
    full = np.uint64(FULL_SHEAR_MASK)
    histogram = Counter()
    zero_pairs = []
    best = None
    for left_index, left in enumerate(states[0]):
        mixed = (
            (np.uint64(left[0]) | right_positive)
            & (np.uint64(left[1]) | right_negative)
        )
        compatible_counts = np.fromiter(
            (int(value).bit_count() for value in full ^ mixed),
            dtype=np.uint8,
            count=len(mixed),
        )
        values, counts = np.unique(compatible_counts, return_counts=True)
        histogram.update({int(value): int(count) for value, count in zip(values, counts, strict=True)})
        for right_index in np.flatnonzero(compatible_counts == 0):
            zero_pairs.append((left_index, int(right_index)))
        for right_index in np.flatnonzero(compatible_counts > 0):
            right_index = int(right_index)
            distance = (
                len(set(circuits[0][left_index]) ^ set(SELECTED[0]))
                + len(set(circuits[1][right_index]) ^ set(SELECTED[1]))
            )
            key = (distance, left_index, right_index)
            if best is None or key < best:
                best = key

    selected_indices = tuple(family.index(support) for family, support in zip(circuits, SELECTED, strict=True))
    selected_mask = compatible_mask(states[0][selected_indices[0]], states[1][selected_indices[1]])
    if selected_mask:
        raise AssertionError("selected circuit pair is no longer shear-rigid")

    one_side_repairs = []
    left_index, right_index = selected_indices
    for candidate, state in enumerate(states[1]):
        mask = compatible_mask(states[0][left_index], state)
        if mask:
            distance = len(set(circuits[1][candidate]) ^ set(SELECTED[1]))
            one_side_repairs.append((distance, 1, candidate, mask))
    for candidate, state in enumerate(states[0]):
        mask = compatible_mask(state, states[1][right_index])
        if mask:
            distance = len(set(circuits[0][candidate]) ^ set(SELECTED[0]))
            one_side_repairs.append((distance, 0, candidate, mask))
    one_side_repairs.sort()
    return states, histogram, tuple(zero_pairs), best, selected_indices, tuple(one_side_repairs)


def directions(mask):
    answer = []
    position = 0
    for source in range(1, 9):
        for target in range(1, 9):
            if source != target:
                if (mask >> position) & 1:
                    answer.append((source, target))
                position += 1
    return tuple(answer)


def main():
    matrix = wall_tools.integer_matrix(POINT)
    normals = exact_topes.derived_rows(matrix)
    circuits, lower = enumerate_positive_circuits(normals)
    if any(support not in family for support, family in zip(SELECTED, circuits, strict=True)):
        raise AssertionError("selected positive circuit missing from census")
    states, histogram, zero_pairs, best, selected_indices, repairs = pair_census(circuits)
    if sum(histogram.values()) != EXPECTED_PAIRS:
        raise AssertionError("the circuit-pair census changed")
    if zero_pairs != (selected_indices,):
        raise AssertionError("the selected pair is no longer the unique rigid pair")

    repair = repairs[0] if repairs else None
    if repair is not None:
        distance, side, candidate, mask = repair
        repair_support = circuits[side][candidate]
        repair_record = (distance, side, repair_support, mask)
    else:
        repair_record = None
    if repair_record is None:
        raise AssertionError("the one-sided exchange repair disappeared")
    repair_distance, repair_side, repair_support, repair_mask = repair_record
    if (
        repair_distance != 2
        or repair_side != 1
        or support_text(repair_support) != EXPECTED_REPAIR
        or repair_mask.bit_count() != 12
    ):
        raise AssertionError("the canonical one-triple eta repair changed")
    best_record = None
    if best is not None:
        distance, left, right = best
        mask = compatible_mask(states[0][left], states[1][right])
        best_record = (distance, circuits[0][left], circuits[1][right], mask)

    fields = (circuits, tuple(sorted(histogram.items())), zero_pairs, best_record, repair_record)
    digest = hashlib.sha256()
    digest.update(b"diag2-type50-step271-circuit-census-v1\0")
    digest.update(repr(fields).encode("ascii"))
    if digest.hexdigest() != EXPECTED_DIGEST:
        raise AssertionError("the circuit-exchange semantic digest changed")
    print(
        f"CIRCUITS rho={len(circuits[0])} eta={len(circuits[1])} "
        f"rho_lower={dict(lower[0])} eta_lower={dict(lower[1])}",
        flush=True,
    )
    print(
        f"PAIRS total={len(circuits[0]) * len(circuits[1])} "
        f"zero={len(zero_pairs)} histogram={dict(sorted(histogram.items()))}",
        flush=True,
    )
    if repair_record is not None:
        distance, side, support, mask = repair_record
        print(
            f"ONE_SIDE_REPAIR distance={distance} side={'rho' if side == 0 else 'eta'} "
            f"support={support_text(support)} shears={directions(mask)}",
            flush=True,
        )
    if best_record is not None:
        distance, left, right, mask = best_record
        print(
            f"BEST_PAIR_REPAIR distance={distance} rho={support_text(left)} "
            f"eta={support_text(right)} shears={directions(mask)}",
            flush=True,
        )
    print(f"SEMANTIC {digest.hexdigest()}", flush=True)
    print("SCOPE exhaustive witness exchange at one exact wall point; not diagonal two")


if __name__ == "__main__":
    main()
