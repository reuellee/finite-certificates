#!/usr/bin/env python3
"""Exact tope-restriction audit for diagonal-two escape sets.

For a bad extension signature rho at a parent chart T and an oriented
elementary shear d, the moving-witness lemma asks whether the signed derived
rows retained by d have a nonzero nonnegative dependence.  Strict Gordan
duality and a generic perturbation give the equivalent finite test used here:

    d is an escape direction
    iff no complete derived-arrangement tope agrees with rho on every
        retained row.

The checker proves this characterization computationally without enumerating
Gordan circuits.  Its no-argument regression exhausts all 40,524 bad abstract
extensions of catalog parent 16 and four hard charts in the exact parent-2599
atlas.  ``--stress`` adds fifteen factor-sign-distant atlas charts.
"""

from __future__ import annotations

import argparse
from collections import Counter, defaultdict
from concurrent.futures import ProcessPoolExecutor, as_completed
import hashlib
from pathlib import Path

import numpy as np


HERE = Path(__file__).resolve().parent

import DIAG9_GRAPH_exact_topes as exact_topes
import four_chart_gate as gate
import verify_diag2_moving_witness_shear as moving
import verify_diag2_witness_exchange_falsifier as falsifier


FULL_SIGNATURE_MASK = (1 << 56) - 1
DIRECTIONS = tuple(
    (source, target, direction)
    for source in range(1, 9)
    for target in range(1, 9)
    if source != target
    for direction in (-1, 1)
)
DIRECTION_INDEX = {direction: index for index, direction in enumerate(DIRECTIONS)}

CANONICAL_CHARTS = (0, 12, 37, 176)
STRESS_CHARTS = (
    41,
    92,
    45,
    6,
    161,
    102,
    30,
    132,
    3,
    157,
    52,
    111,
    174,
    25,
    16,
)
EXPECTED_PARENT16_DIGEST = (
    "c63e476f934e14908cf6d5848c3c9d97e35537d86b9955eee94bb4ae09e36130"
)
EXPECTED_CHART_DIGESTS = {
    0: "f55d5868df8b5e70310e2bad71b3151dc7f8f40d9b1c10d275a2372fa5390177",
    3: "3e87d9721f362cefc59b2da87296c62e24e55e5b6bb9e01b682478f9ecb99527",
    6: "483f988d0d825e9caf7337ea26e7a311192b7b07c84f8249ca11e2a98748834f",
    12: "254b3409044804cee48c2b132f542ebe894eca93b6b4dbe534c1f8c107832b9c",
    16: "30c9fd14357ce0bd96cbff5215bf347190cd8b87b4989849a748501a72f6db8a",
    25: "5e67b3f8b0851aa18f3d76a6c1836e012c6985ce8ad43b4ee3f165562dc6ad31",
    30: "8c35192c7415699a69ada7a3ea6f2df52235336f5cb01e47aaa2c71e6ef05651",
    37: "d16911b0ab2b4faa4771cb0d41d3aa3055823086e2799b96164f3caf6c025401",
    41: "a056d739f34bd966a95dfabd8c5aac8339be363039ea0c2b6b4ec7c1a4877048",
    45: "3313b2c353d135173f4e8327c85b413ccfd287120a6dbd52b7be13363dbbfbcd",
    52: "19712fc6a8ec2a3ca2b56230eb602a62c814c6fee5ae727c7475e3ed83b64f8c",
    92: "1690685ff63912bb536ba10af8ca19a6a7765f8a064127bbef0d242f7a64f03f",
    102: "260ef15d843d9fbf7de863dd044abc16a47be27d08ab96ea40e1a45b3accd95c",
    111: "e2b718fa25861fa9c291d09838e5c88c7a19a90c8d5431857bb23ba6cbacc744",
    132: "b67d0ad1877e27e30e2200a2db18d739b073085545f195959e057b4b3c019845",
    157: "d6ce1b5adf8d755fd9f6178636789a7bdf90f66635c714afe7b4dc40c7e59378",
    161: "9d34f867eb0272a45c82b8c405eb1609f89d891e5cf02336eeb6cf1129577d97",
    174: "6cf04cb78ea94dfc2c3ec765d7f84b97ce3abde5fd8f4d0584ab9707f1d20a1b",
    176: "3429f7472c67cdb9cec40c91757cd618e60c9a184ea8187757545f90100e45c3",
}
EXPECTED_CHART_MINIMUM_COUNTS = {
    0: 6,
    3: 8,
    6: 8,
    12: 6,
    16: 2,
    25: 10,
    30: 8,
    37: 12,
    41: 12,
    45: 8,
    52: 16,
    92: 14,
    102: 24,
    111: 14,
    132: 2,
    157: 8,
    161: 10,
    174: 16,
    176: 20,
}


def source_transport_data(source, target):
    entries = []
    source_mask = 0
    for index in range(56):
        replacement = moving.replacement(index, source, target)
        if replacement is None:
            continue
        replacement_index, sorting_sign = replacement
        entries.append((index, replacement_index, sorting_sign))
        source_mask |= 1 << index
    if len(entries) != 15 or source_mask.bit_count() != 15:
        raise AssertionError("an ordered shear must transport exactly 15 triples")
    return tuple(entries), source_mask


def index_topes_by_unchanged_rows(tope_bits, source_mask):
    common_mask = FULL_SIGNATURE_MASK ^ source_mask
    by_common = defaultdict(list)
    for tope in tope_bits:
        by_common[tope & common_mask].append(tope & source_mask)
    return common_mask, dict(by_common)


def prepare_directions(tope_bits):
    prepared = []
    for source in range(1, 9):
        for target in range(1, 9):
            if source == target:
                continue
            entries, source_mask = source_transport_data(source, target)
            common_mask, by_common = index_topes_by_unchanged_rows(
                tope_bits, source_mask
            )
            prepared.append(
                (source, target, entries, source_mask, common_mask, by_common)
            )
    if len(prepared) != 56:
        raise AssertionError("wrong ordered-shear universe")
    return tuple(prepared)


def direction_deletions(signature, entries):
    delete_for_positive = 0
    delete_for_negative = 0
    for index, replacement_index, sorting_sign in entries:
        alpha = (
            -sorting_sign
            * moving.signature_sign(signature, index)
            * moving.signature_sign(signature, replacement_index)
        )
        if alpha == 1:
            delete_for_negative |= 1 << index
        elif alpha == -1:
            delete_for_positive |= 1 << index
        else:
            raise AssertionError("transport coefficient has no sign")
    if delete_for_positive & delete_for_negative:
        raise AssertionError("a transported row received two coefficient signs")
    if (delete_for_positive | delete_for_negative).bit_count() != 15:
        raise AssertionError("transport sign partition is incomplete")
    return delete_for_positive, delete_for_negative


def restricted_system_has_no_positive_covector(
    signature, source_mask, common_mask, by_common, delete_mask
):
    kept_source = source_mask ^ delete_mask
    candidates = by_common.get(signature & common_mask, ())
    return not any(
        ((candidate ^ signature) & kept_source) == 0 for candidate in candidates
    )


def escape_mask(signature, prepared):
    answer = 0
    for (
        source,
        target,
        entries,
        source_mask,
        common_mask,
        by_common,
    ) in prepared:
        delete_positive, delete_negative = direction_deletions(signature, entries)
        if restricted_system_has_no_positive_covector(
            signature, source_mask, common_mask, by_common, delete_negative
        ):
            answer |= 1 << DIRECTION_INDEX[(source, target, -1)]
        if restricted_system_has_no_positive_covector(
            signature, source_mask, common_mask, by_common, delete_positive
        ):
            answer |= 1 << DIRECTION_INDEX[(source, target, 1)]
    return answer


def semantic_digest(label, bad_records):
    digest = hashlib.sha256()
    digest.update(b"diag2-tope-escape-sets-v1\0")
    digest.update(label.encode("ascii") + b"\0")
    for signature, mask in sorted(bad_records):
        digest.update(int(signature).to_bytes(8, "little"))
        digest.update(int(mask).to_bytes(16, "little"))
    return digest.hexdigest()


def prove_pairwise_intersection(bad_records):
    containing = [0] * len(DIRECTIONS)
    for record_index, (_, mask) in enumerate(bad_records):
        bits = mask
        while bits:
            bit = bits & -bits
            containing[bit.bit_length() - 1] |= 1 << record_index
            bits ^= bit

    all_records = (1 << len(bad_records)) - 1
    for left_index, (left_signature, mask) in enumerate(bad_records):
        intersecting = 0
        bits = mask
        while bits:
            bit = bits & -bits
            intersecting |= containing[bit.bit_length() - 1]
            bits ^= bit
        disjoint = all_records & ~intersecting
        disjoint &= ~((1 << (left_index + 1)) - 1)
        if disjoint:
            bit = disjoint & -disjoint
            right_index = bit.bit_length() - 1
            return left_signature, bad_records[right_index][0]
    return None


def analyze_matrix(matrix, signatures, label):
    rows = exact_topes.derived_rows(matrix)
    enumerated = exact_topes.enumerate_topes(rows, dimension=4)
    exact_topes.verify_topes(rows, enumerated)
    tope_bits = tuple(enumerated)
    if len(tope_bits) != 26_112:
        raise AssertionError(f"{label}: wrong derived-arrangement tope count")
    prepared = prepare_directions(tope_bits)
    tope_set = set(tope_bits)
    bad_records = [
        (signature, escape_mask(signature, prepared))
        for signature in signatures
        if signature not in tope_set
    ]
    histogram = Counter(mask.bit_count() for _, mask in bad_records)
    disjoint = prove_pairwise_intersection(bad_records)
    if disjoint is not None:
        raise AssertionError(f"{label}: disjoint escape sets at {disjoint}")
    return {
        "label": label,
        "topes": len(tope_bits),
        "valid": len(signatures),
        "bad": len(bad_records),
        "minimum": min(histogram),
        "minimum_count": histogram[min(histogram)],
        "digest": semantic_digest(label, bad_records),
        "records": bad_records,
    }


def catalog_parent(index):
    catalog = [line.strip() for line in gate.CATALOG_48.open() if line.strip()]
    return catalog[index]


def parent16_audit():
    parent = catalog_parent(16)
    expected_parent_signs = tuple(1 if sign == "+" else -1 for sign in parent)
    if exact_topes.parent_signs(moving.PARENT16) != expected_parent_signs:
        raise AssertionError("stored parent-16 chart has the wrong chirotope")
    _, signatures = gate.enumerate_extensions(parent)
    result = analyze_matrix(moving.PARENT16, signatures, "parent16")
    if (result["valid"], result["bad"], result["minimum"], result["minimum_count"]) != (
        66_636,
        40_524,
        52,
        2,
    ):
        raise AssertionError("parent-16 exhaustive summary changed")
    minimizers = {
        signature
        for signature, mask in result["records"]
        if mask.bit_count() == 52
    }
    if minimizers != {50_531_390_688_592_880, 21_526_203_349_335_055}:
        raise AssertionError("parent-16 minimum escape signatures changed")
    minimum_masks = {
        mask for signature, mask in result["records"] if signature in minimizers
    }
    if len(minimum_masks) != 1:
        raise AssertionError("the two parent-16 minimum escape sets diverged")
    left = dict(result["records"])[falsifier.LEFT_SIGNATURE]
    right = dict(result["records"])[falsifier.RIGHT_SIGNATURE]
    if (
        left.bit_count(),
        right.bit_count(),
        (left & right).bit_count(),
        (left | right).bit_count(),
    ) != (89, 99, 76, 112):
        raise AssertionError("tope reduction disagrees with the circuit falsifier")
    expected = EXPECTED_PARENT16_DIGEST
    if result["digest"] != expected:
        raise AssertionError(f"parent-16 semantic digest changed: {result['digest']}")
    del result["records"]
    return result


def row2599_chart_audit(chart_index):
    parent = catalog_parent(gate.PARENT_INDEX)
    _, signatures = gate.enumerate_extensions(parent)
    with np.load(HERE / "data" / "seeat_parent2599_upper178.npz") as atlas:
        matrix = atlas["chart_matrix"][chart_index]
    result = analyze_matrix(matrix, signatures, f"row2599-chart-{chart_index}")
    if (result["valid"], result["bad"], result["minimum"]) != (
        97_224,
        71_112,
        53,
    ):
        raise AssertionError(f"chart {chart_index}: exhaustive summary changed")
    expected = EXPECTED_CHART_DIGESTS.get(chart_index)
    if expected is not None and result["digest"] != expected:
        raise AssertionError(
            f"chart {chart_index}: semantic digest changed: {result['digest']}"
        )
    if chart_index in EXPECTED_CHART_MINIMUM_COUNTS:
        expected_count = EXPECTED_CHART_MINIMUM_COUNTS[chart_index]
        if result["minimum_count"] != expected_count:
            raise AssertionError(f"chart {chart_index}: minimum-count pin changed")
    del result["records"]
    return result


def parse_args():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--stress",
        action="store_true",
        help="also replay fifteen factor-sign-distant row-2599 charts",
    )
    parser.add_argument(
        "--workers",
        type=int,
        default=4,
        help="parallel row-2599 chart workers (default: 4)",
    )
    return parser.parse_args()


def main():
    args = parse_args()
    selected_charts = set(CANONICAL_CHARTS + STRESS_CHARTS)
    if set(EXPECTED_CHART_DIGESTS) != selected_charts:
        raise AssertionError("selected-chart semantic digest pins are incomplete")
    if set(EXPECTED_CHART_MINIMUM_COUNTS) != selected_charts:
        raise AssertionError("selected-chart minimum-count pins are incomplete")
    parent16 = parent16_audit()
    print(
        "PASS parent 16: 66,636 extensions, 40,524 bad, "
        "minimum escape size 52 (two signatures)"
    )
    print("PASS circuit falsifier escape sizes 89,99; intersection 76; union 112")
    print("SEMANTIC parent16", parent16["digest"])

    charts = CANONICAL_CHARTS + (STRESS_CHARTS if args.stress else ())
    results = []
    with ProcessPoolExecutor(max_workers=args.workers) as executor:
        futures = {
            executor.submit(row2599_chart_audit, chart): chart for chart in charts
        }
        for future in as_completed(futures):
            results.append(future.result())
    for result in sorted(results, key=lambda item: int(item["label"].rsplit("-", 1)[1])):
        print(
            f"PASS {result['label']}: 97,224 extensions, 71,112 bad, "
            f"minimum 53 ({result['minimum_count']} signatures), pairwise intersection"
        )
        print("SEMANTIC", result["label"], result["digest"])
    print("THEOREM AUDIT escape membership equals a complete-tope restriction test")
    print("SCOPE exact chart-level evidence; universal chart theorem and global assembly remain open")


if __name__ == "__main__":
    main()
