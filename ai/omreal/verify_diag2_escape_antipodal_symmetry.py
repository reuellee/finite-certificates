#!/usr/bin/env python3
"""Independent exact regression for E_T(-rho) = E_T(rho).

This checker deliberately reconstructs the restriction-hash calculation
without importing ``verify_diag2_escape_set_topes``.  It enumerates the exact
parent-16 derived topes, verifies antipodal closure, and pins five bad escape
masks together with their globally sign-reversed partners.

The general lemma is algebraic; these finite cases are regression witnesses,
not a replacement for its proof and not a proof of diagonal two.
"""

from collections import defaultdict
from itertools import combinations
from pathlib import Path
import sys


HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import DIAG9_GRAPH_exact_topes as exact_topes
import four_chart_gate as gate


FULL_SIGNATURE_MASK = (1 << 56) - 1
TRIPLES = tuple(
    sorted(combinations(range(1, 9), 3), key=lambda subset: tuple(reversed(subset)))
)
TRIPLE_INDEX = {triple: index for index, triple in enumerate(TRIPLES)}
DIRECTIONS = tuple(
    (source, target, direction)
    for source in range(1, 9)
    for target in range(1, 9)
    if source != target
    for direction in (-1, 1)
)
DIRECTION_INDEX = {direction: index for index, direction in enumerate(DIRECTIONS)}

PARENT16 = (
    (8, 4, -3, -6, 1, 0, 8, 1),
    (1, 8, 8, 1, 2, -5, -1, -3),
    (3, -1, 5, -2, -8, 5, -1, -8),
    (-1, -1, 0, 8, 2, 8, 4, 5),
)

# Representative signature -> independently pinned 112-bit escape mask.
EXPECTED = {
    21_526_203_349_335_055: 0x2967576FA894289435B5E9AD482,
    50_603_577_668_866_936: 0x59EDDFEFFFFFFFBEFD51AFFFF59E,
    36_319_034_736_575_472: 0xE75FFFFFFFF7BFF95FFFFB6FFFFF,
    26_988_370_886_400_909: 0xFFFFFFFFDFFFFFFFFFEEFFFFFFFF,
    45_348_283_816_043_521: 0xEEFF77EFFFFFFFFFEBFFFFFFFEEF,
}


def orientation_sign(sequence):
    inversions = sum(
        sequence[left] > sequence[right]
        for left in range(len(sequence))
        for right in range(left + 1, len(sequence))
    )
    return -1 if inversions & 1 else 1


def replacement(index, source, target):
    triple = TRIPLES[index]
    if source not in triple or target in triple:
        return None
    sequence = list(triple)
    sequence[sequence.index(source)] = target
    return TRIPLE_INDEX[tuple(sorted(sequence))], orientation_sign(sequence)


def source_transport_data(source, target):
    entries = []
    source_mask = 0
    for index in range(56):
        result = replacement(index, source, target)
        if result is None:
            continue
        replacement_index, sorting_sign = result
        entries.append((index, replacement_index, sorting_sign))
        source_mask |= 1 << index
    if len(entries) != 15 or source_mask.bit_count() != 15:
        raise AssertionError("wrong transported-row count")
    return tuple(entries), source_mask


def prepare_directions(topes):
    prepared = []
    for source in range(1, 9):
        for target in range(1, 9):
            if source == target:
                continue
            entries, source_mask = source_transport_data(source, target)
            common_mask = FULL_SIGNATURE_MASK ^ source_mask
            by_common = defaultdict(list)
            for tope in topes:
                by_common[tope & common_mask].append(tope & source_mask)
            prepared.append(
                (source, target, entries, source_mask, common_mask, dict(by_common))
            )
    return tuple(prepared)


def direction_deletions(signature, entries):
    delete_positive = 0
    delete_negative = 0
    for index, replacement_index, sorting_sign in entries:
        first = 1 if signature & (1 << index) else -1
        second = 1 if signature & (1 << replacement_index) else -1
        alpha = -sorting_sign * first * second
        if alpha > 0:
            delete_negative |= 1 << index
        else:
            delete_positive |= 1 << index
    return delete_positive, delete_negative


def no_agreeing_tope(signature, source_mask, common_mask, by_common, delete_mask):
    kept_source = source_mask ^ delete_mask
    return not any(
        ((candidate ^ signature) & kept_source) == 0
        for candidate in by_common.get(signature & common_mask, ())
    )


def escape_mask(signature, prepared):
    answer = 0
    for source, target, entries, source_mask, common_mask, by_common in prepared:
        delete_positive, delete_negative = direction_deletions(signature, entries)
        if no_agreeing_tope(
            signature, source_mask, common_mask, by_common, delete_negative
        ):
            answer |= 1 << DIRECTION_INDEX[(source, target, -1)]
        if no_agreeing_tope(
            signature, source_mask, common_mask, by_common, delete_positive
        ):
            answer |= 1 << DIRECTION_INDEX[(source, target, 1)]
    return answer


def main():
    parents = [
        line.strip()
        for line in gate.CATALOG_48.open(encoding="utf-8")
        if line.strip()
    ]
    parent = parents[16]
    expected_parent_signs = tuple(1 if sign == "+" else -1 for sign in parent)
    if exact_topes.parent_signs(PARENT16) != expected_parent_signs:
        raise AssertionError("hardcoded matrix does not realize catalog parent 16")

    _parent_bits, extensions = gate.enumerate_extensions(parent)
    valid_extensions = set(map(int, extensions))
    if len(valid_extensions) != 66_636:
        raise AssertionError("catalog parent-16 extension count changed")

    rows = exact_topes.derived_rows(PARENT16)
    topes = exact_topes.enumerate_topes(rows, dimension=4)
    exact_topes.verify_topes(rows, topes)
    if len(topes) != 26_112:
        raise AssertionError("parent-16 complete-tope count changed")
    if {signature ^ FULL_SIGNATURE_MASK for signature in topes} != set(topes):
        raise AssertionError("the central arrangement tope table is not antipodal")

    prepared = prepare_directions(topes)
    for signature, expected in EXPECTED.items():
        opposite = signature ^ FULL_SIGNATURE_MASK
        if signature not in valid_extensions or opposite not in valid_extensions:
            raise AssertionError(
                "pinned antipodal pair is not a GP-valid parent-16 extension"
            )
        if signature in topes or opposite in topes:
            raise AssertionError("pinned GP-valid extension is not bad with its antipode")
        for _source, _target, entries, *_rest in prepared:
            if direction_deletions(signature, entries) != direction_deletions(
                opposite, entries
            ):
                raise AssertionError("transport deletion partition changed on reversal")
        first = escape_mask(signature, prepared)
        second = escape_mask(opposite, prepared)
        if first != expected or second != expected:
            raise AssertionError(
                f"antipodal escape mask changed at signature {signature}: "
                f"{first:#x}, {second:#x}"
            )

    print("PASS hardcoded matrix realizes catalog parent 16")
    print("PASS parent-16 complete topes are antipodally closed")
    print("PASS five GP-valid pinned bad pairs satisfy E_T(-rho) = E_T(rho)")
    print("REGRESSION global sign reversal preserves every pinned escape direction")
    print(
        "SCOPE finite regression for the universal algebraic symmetry lemma; "
        "no pairwise-intersection claim"
    )


if __name__ == "__main__":
    main()
