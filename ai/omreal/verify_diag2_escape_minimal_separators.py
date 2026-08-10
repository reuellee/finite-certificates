#!/usr/bin/env python3
"""Exact parent-16 audit of the minimal-tope-separator reduction.

For a bad signature rho and source e, retain only inclusion-minimal
disagreement sets between rho and complete chart topes which agree away from
e.  The accompanying note proves that these antichains determine every
moving-witness escape direction.  This checker reconstructs all parent-16
escape masks from those antichains without importing the direct escape-mask
implementation.

Scope: one exact chart.  This is not residual-chamber coverage and not a
proof of diagonal two.
"""

from __future__ import annotations

from collections import Counter, defaultdict
import hashlib

import DIAG9_GRAPH_exact_topes as exact_topes
import four_chart_gate as gate
import verify_diag2_moving_witness_shear as moving


FULL_SIGNATURE_MASK = (1 << 56) - 1
DIRECTIONS = tuple(
    (source, target, direction)
    for source in range(1, 9)
    for target in range(1, 9)
    if source != target
    for direction in (-1, 1)
)
DIRECTION_INDEX = {direction: index for index, direction in enumerate(DIRECTIONS)}
FULL_DIRECTION_MASK = (1 << len(DIRECTIONS)) - 1

EXPECTED_TOPES = 26_112
EXPECTED_VALID = 66_636
EXPECTED_BAD = 40_524
EXPECTED_RAW_SEPARATORS = 2_063_096
EXPECTED_MINIMAL_SEPARATORS = 287_560
EXPECTED_MAX_RAW_SOURCE_FAMILY = 282
EXPECTED_MAX_MINIMAL_SOURCE_FAMILY = 6
EXPECTED_MINIMUM_ESCAPE = 52
EXPECTED_MINIMUM_COUNT = 2
EXPECTED_MINIMIZERS = {
    50_531_390_688_592_880,
    21_526_203_349_335_055,
}
EXPECTED_DIGEST = "c63e476f934e14908cf6d5848c3c9d97e35537d86b9955eee94bb4ae09e36130"


def catalog_parent(index: int) -> str:
    parents = [line.strip() for line in gate.CATALOG_48.open() if line.strip()]
    return parents[index]


def source_mask(source: int) -> int:
    return sum(
        1 << index
        for index, triple in enumerate(moving.TRIPLES)
        if source in triple
    )


def build_source_indexes(topes):
    """Index complete topes by their 35 signs away from each source."""
    answer = {}
    for source in range(1, 9):
        on_source = source_mask(source)
        away = FULL_SIGNATURE_MASK ^ on_source
        by_away = defaultdict(list)
        for tope in topes:
            by_away[tope & away].append(tope & on_source)
        answer[source] = (on_source, away, dict(by_away))
    return answer


def minimal_separators(signature: int, source_index):
    """Return (raw count, inclusion-minimal source-local separators)."""
    on_source, away, by_away = source_index
    candidates = sorted(
        {
            (tope_on_source ^ signature) & on_source
            for tope_on_source in by_away.get(signature & away, ())
        },
        key=lambda separator: (separator.bit_count(), separator),
    )
    if 0 in candidates:
        raise AssertionError("a bad signature appeared as a complete chart tope")

    minimal = []
    for separator in candidates:
        if not any(
            (earlier & separator) == earlier for earlier in minimal
        ):
            minimal.append(separator)
    return len(candidates), tuple(minimal)


def support_indices(bits: int):
    while bits:
        bit = bits & -bits
        yield bit.bit_length() - 1
        bits ^= bit


def separator_nonescape_cover(signature: int, source: int, separator: int) -> int:
    """Directions whose deleted half-star contains this separator."""
    indices = tuple(support_indices(separator))
    if not indices:
        raise AssertionError("bad-signature minimal separator is empty")

    carrier = set()
    for index in indices:
        triple = moving.TRIPLES[index]
        if source not in triple:
            raise AssertionError("separator left its source star")
        carrier.update(label for label in triple if label != source)

    answer = 0
    for target in range(1, 9):
        if target == source or target in carrier:
            continue
        alphas = []
        for index in indices:
            replacement = moving.replacement(index, source, target)
            if replacement is None:
                raise AssertionError("eligible target did not define a replacement")
            replacement_index, sorting_sign = replacement
            alphas.append(
                -sorting_sign
                * moving.signature_sign(signature, index)
                * moving.signature_sign(signature, replacement_index)
            )
        if all(alpha == alphas[0] for alpha in alphas):
            # Delta_rho(e,f,a) deletes precisely the rows with alpha=-a.
            direction = (source, target, -alphas[0])
            answer |= 1 << DIRECTION_INDEX[direction]

    carrier_bound = 7 - len(carrier)
    if answer.bit_count() > carrier_bound or carrier_bound > 5:
        raise AssertionError("minimal separator violated its carrier bound")
    return answer


def escape_mask_from_minimal_separators(signature: int, indexes):
    nonescape = 0
    raw_count = 0
    minimal_count = 0
    max_raw = 0
    max_minimal = 0
    cover_histogram = Counter()

    for source in range(1, 9):
        raw, separators = minimal_separators(signature, indexes[source])
        raw_count += raw
        minimal_count += len(separators)
        max_raw = max(max_raw, raw)
        max_minimal = max(max_minimal, len(separators))
        for separator in separators:
            cover = separator_nonescape_cover(signature, source, separator)
            cover_histogram[cover.bit_count()] += 1
            nonescape |= cover

    return (
        FULL_DIRECTION_MASK ^ nonescape,
        raw_count,
        minimal_count,
        max_raw,
        max_minimal,
        cover_histogram,
    )


def semantic_digest(records):
    digest = hashlib.sha256()
    digest.update(b"diag2-tope-escape-sets-v1\0")
    digest.update(b"parent16\0")
    for signature, mask in sorted(records):
        digest.update(int(signature).to_bytes(8, "little"))
        digest.update(int(mask).to_bytes(16, "little"))
    return digest.hexdigest()


def find_eight_source_cover(records):
    """Find E(rho) cap E(eta)=empty, equivalently all eight blocks covered."""
    containing = [0] * len(DIRECTIONS)
    for record_index, (_signature, escape) in enumerate(records):
        bits = escape
        while bits:
            bit = bits & -bits
            containing[bit.bit_length() - 1] |= 1 << record_index
            bits ^= bit

    all_records = (1 << len(records)) - 1
    for left_index, (left_signature, left_escape) in enumerate(records):
        intersects_left = 0
        bits = left_escape
        while bits:
            bit = bits & -bits
            intersects_left |= containing[bit.bit_length() - 1]
            bits ^= bit
        disjoint = all_records & ~intersects_left
        disjoint &= ~((1 << (left_index + 1)) - 1)
        if disjoint:
            bit = disjoint & -disjoint
            right_index = bit.bit_length() - 1
            right_signature, right_escape = records[right_index]
            # Spell out the equivalent source-cover condition as a guard.
            for source in range(1, 9):
                local = sum(
                    1 << DIRECTION_INDEX[(source, target, direction)]
                    for target in range(1, 9)
                    if target != source
                    for direction in (-1, 1)
                )
                left_nonescape = local & ~left_escape
                right_nonescape = local & ~right_escape
                if (left_nonescape | right_nonescape) != local:
                    raise AssertionError(
                        "disjoint masks failed the source-cover identity"
                    )
            return left_signature, right_signature
    return None


def main():
    parent = catalog_parent(16)
    expected_parent_signs = tuple(1 if sign == "+" else -1 for sign in parent)
    if exact_topes.parent_signs(moving.PARENT16) != expected_parent_signs:
        raise AssertionError("stored parent-16 matrix has the wrong chirotope")

    _parent_bits, signatures = gate.enumerate_extensions(parent)
    if len(signatures) != EXPECTED_VALID:
        raise AssertionError("parent-16 extension count changed")

    rows = exact_topes.derived_rows(moving.PARENT16)
    enumerated = exact_topes.enumerate_topes(rows, dimension=4)
    exact_topes.verify_topes(rows, enumerated)
    topes = tuple(enumerated)
    if len(topes) != EXPECTED_TOPES:
        raise AssertionError("parent-16 complete-tope count changed")

    tope_set = set(topes)
    indexes = build_source_indexes(topes)
    records = []
    raw_total = 0
    minimal_total = 0
    maximum_raw = 0
    maximum_minimal = 0
    cover_histogram = Counter()

    for signature in signatures:
        if signature in tope_set:
            continue
        (
            escape,
            raw_count,
            minimal_count,
            max_raw,
            max_minimal,
            cover_hist,
        ) = escape_mask_from_minimal_separators(signature, indexes)
        records.append((signature, escape))
        raw_total += raw_count
        minimal_total += minimal_count
        maximum_raw = max(maximum_raw, max_raw)
        maximum_minimal = max(maximum_minimal, max_minimal)
        cover_histogram.update(cover_hist)

    if len(records) != EXPECTED_BAD:
        raise AssertionError("parent-16 bad-signature count changed")
    if (raw_total, minimal_total) != (
        EXPECTED_RAW_SEPARATORS,
        EXPECTED_MINIMAL_SEPARATORS,
    ):
        raise AssertionError("raw/minimal separator totals changed")
    if (maximum_raw, maximum_minimal) != (
        EXPECTED_MAX_RAW_SOURCE_FAMILY,
        EXPECTED_MAX_MINIMAL_SOURCE_FAMILY,
    ):
        raise AssertionError("source-family compression maxima changed")
    if max(cover_histogram, default=0) > 5:
        raise AssertionError("a separator covered more than five directions")

    sizes = Counter(mask.bit_count() for _signature, mask in records)
    if (
        min(sizes) != EXPECTED_MINIMUM_ESCAPE
        or sizes[min(sizes)] != EXPECTED_MINIMUM_COUNT
    ):
        raise AssertionError("minimum escape-set summary changed")
    minimizers = {
        signature
        for signature, mask in records
        if mask.bit_count() == EXPECTED_MINIMUM_ESCAPE
    }
    if minimizers != EXPECTED_MINIMIZERS:
        raise AssertionError("minimum escape signatures changed")
    minimum_masks = {
        mask for signature, mask in records if signature in EXPECTED_MINIMIZERS
    }
    if len(minimum_masks) != 1:
        raise AssertionError("antipodal minimizers have different escape masks")

    digest = semantic_digest(records)
    if digest != EXPECTED_DIGEST:
        raise AssertionError(f"minimal-separator semantic digest changed: {digest}")
    counterexample = find_eight_source_cover(records)
    if counterexample is not None:
        raise AssertionError(f"eight-source cover found at {counterexample}")

    print(
        "PASS parent 16: 26,112 topes, 66,636 extensions, "
        "40,524 bad signatures"
    )
    print(
        "PASS minimal separators:",
        f"{raw_total:,} raw -> {minimal_total:,} minimal;",
        f"maximum source family {maximum_raw} -> {maximum_minimal}",
    )
    print("PASS every minimal separator covers at most five nonescape directions")
    print("PASS reconstructed minimum escape size 52 and pinned semantic digest")
    print("SEMANTIC", digest)
    print("PASS no pair satisfies all eight 14-direction source covers")
    print("SCOPE exact parent-16 chart; universal cover contradiction remains open")


if __name__ == "__main__":
    main()
