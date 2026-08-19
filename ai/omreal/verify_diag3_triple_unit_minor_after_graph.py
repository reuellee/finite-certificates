#!/usr/bin/env python3
"""Exact replay, independent of discovery, of unit-minor graph certificates.

The compact artifact records exact positive target-pair identities in the
canonical type-49, pivot-3 graph chart.  This verifier reconstructs every
polynomial over Z from the global factor certificate, performs both cleared
graph restrictions, differentiates, and compares the recorded two-by-two
Jacobian minor to the complete product of graph-restricted parent brackets.
It then independently scans the pinned sequential-affine residue and checks
the exact anchor/coset map for every newly closed row.
"""

from __future__ import annotations

from collections import Counter
import hashlib
from pathlib import Path
import struct
import sys


HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import DIAG2_PIVOT_LABELED_PAIR_ORBITS_VERIFY as labeled  # noqa: E402
import DIAG2_PIVOT_REPRESENTATIVE_GRADIENT_VERIFY as gradient  # noqa: E402
import DIAG9_GRAPH_global_factor_census as global_factors  # noqa: E402
import verify_diag2_pivot_all_pair_fibers as fibers  # noqa: E402
import verify_residual_log_binomials as poly  # noqa: E402


CERTIFICATE = HERE / "data/DIAG3_triple_unit_minor_after_graph_certificates.bin"
CERTIFICATE_SHA256 = "9889d40c9fdc4c23817a28e94b311cec1673b4e4dfd3e072dace17ff49ffd97a"
MAGIC = b"D3UMPAIR"
PAIR_COUNT = 234
KIND = 49
PIVOT = 3
LABEL_COUNT = 55
EXPECTED_PAIR_SEMANTIC = "15b761934f6fb98d036f1820e99b3c6012ea4134ae5746579dac874280537e15"
EXPECTED_ROW_COUNT = 117
EXPECTED_ANCHOR_INDEX_COUNTS = {0: 2, 1: 12, 2: 103}
EXPECTED_ROW_SEMANTIC = "8dabe7ae8baf1bf6ce7d8dbac7621a4e6810860717fd3c4a39700db018b22e79"
SEQUENTIAL_RESIDUE_COUNT = 1_638_903
SEQUENTIAL_RESIDUE_SHA256 = "5ba2314c94ba115d5bf5e975e68412e3f4b44e2c65df51b757f6150a3352d4e1"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        while block := source.read(1 << 20):
            digest.update(block)
    return digest.hexdigest()


def parse_certificate(path: Path):
    if sha256(path) != CERTIFICATE_SHA256:
        raise AssertionError("unit-minor certificate SHA-256 changed")
    raw = path.read_bytes()
    count, kind, pivot, label_count = struct.unpack_from("<IHHH", raw, 8)
    if (raw[:8], count, kind, pivot, label_count) != (
        MAGIC, PAIR_COUNT, KIND, PIVOT, LABEL_COUNT
    ):
        raise AssertionError("unit-minor certificate header changed")
    position = struct.calcsize("<8sIHHH")
    labels = tuple(
        raw[position + 4 * index:position + 4 * (index + 1)].decode("ascii")
        for index in range(label_count)
    )
    position += 4 * label_count
    records = []
    for _ in range(count):
        first, second, left, right, scalar, factor_count = struct.unpack_from(
            "<HHBBbB", raw, position
        )
        position += struct.calcsize("<HHBBbB")
        indices = raw[position:position + factor_count]
        position += factor_count
        if any(index >= label_count for index in indices):
            raise AssertionError("bad parent-label index")
        records.append(
            (first, second, left, right, scalar, tuple(labels[index] for index in indices))
        )
    if position != len(raw):
        raise AssertionError("trailing unit-minor certificate bytes")
    return tuple(records)


def graph_data(factor_polynomials, canonical_factor, parent_by_label):
    anchor = factor_polynomials[canonical_factor]
    slope, constant = fibers.pivot_split(anchor, PIVOT)
    if slope != poly.constant(1):
        raise AssertionError("type-49/pivot-3 anchor slope changed")
    numerator = poly.negative(constant)
    restricted_parents = {
        label: fibers.graph_restrict(parent, PIVOT, slope, numerator)
        for label, parent in parent_by_label.items()
    }
    if any(not parent for parent in restricted_parents.values()):
        raise AssertionError("anchor graph acquired an identically zero parent bracket")
    return slope, numerator, restricted_parents


def replay_pairs(records, factor_polynomials, canonical_factor, parent_by_label):
    slope, numerator, restricted_parents = graph_data(
        factor_polynomials, canonical_factor, parent_by_label
    )
    restricted_cache = {}
    semantic = hashlib.sha256(b"diag3-unit-minor-after-graph-exact-v1\0")
    pair_witnesses = {}
    length_counts = Counter()
    for number, record in enumerate(records):
        first, second, left, right, scalar, labels = record
        if not first < second or PIVOT in (left, right) or not left < right:
            raise AssertionError(f"bad pair metadata at record {number}")
        for factor in (first, second):
            if factor not in restricted_cache:
                restricted_cache[factor] = fibers.graph_restrict(
                    factor_polynomials[factor], PIVOT, slope, numerator
                )
        minor = poly.subtract(
            poly.multiply(
                gradient.derivative(restricted_cache[first], left),
                gradient.derivative(restricted_cache[second], right),
            ),
            poly.multiply(
                gradient.derivative(restricted_cache[first], right),
                gradient.derivative(restricted_cache[second], left),
            ),
        )
        product = poly.constant(scalar)
        for label in labels:
            if label not in restricted_parents:
                raise AssertionError(f"unknown parent bracket {label}")
            product = poly.multiply(product, restricted_parents[label])
        if minor != product:
            raise AssertionError(f"false exact unit-minor identity at record {number}")
        key = first, second
        if key in pair_witnesses:
            raise AssertionError("duplicate target-pair certificate")
        pair_witnesses[key] = left, right, scalar, labels
        length_counts[len(labels)] += 1
        semantic.update(repr(record).encode("ascii"))
    digest = semantic.hexdigest()
    if digest != EXPECTED_PAIR_SEMANTIC:
        raise AssertionError(f"pair semantic changed: {digest}")
    return pair_witnesses, length_counts, digest


def replay_rows(path, pair_witnesses, canonical, anchor_alignments, stabilizers,
                factor_occurrence, occurrence_factor):
    if sha256(path) != SEQUENTIAL_RESIDUE_SHA256:
        raise AssertionError("sequential-affine residue SHA-256 changed")
    raw = path.read_bytes()
    count, = struct.unpack_from("<I", raw)
    if count != SEQUENTIAL_RESIDUE_COUNT or len(raw) != 4 + 6 * count:
        raise AssertionError("bad sequential-affine residue")
    semantic = hashlib.sha256(b"diag3-unit-minor-after-graph-row-v1\0")
    anchor_counts = Counter()
    closed = 0
    seen = set()
    for row in struct.iter_unpack("<HHH", raw[4:]):
        if row in seen or len(set(row)) != 3:
            raise AssertionError("duplicate or repeated-factor sequential-residue row")
        seen.add(row)
        witness = None
        for anchor_index, anchor in enumerate(row):
            mapping = anchor_alignments[KIND].get(anchor)
            if mapping is None:
                continue
            if labeled.transform_factor(
                anchor, mapping, factor_occurrence, occurrence_factor
            ) != canonical[KIND]:
                raise AssertionError("anchor alignment does not reach canonical factor")
            others = tuple(row[index] for index in range(3) if index != anchor_index)
            moved = tuple(
                labeled.transform_factor(
                    factor, mapping, factor_occurrence, occurrence_factor
                )
                for factor in others
            )
            for symmetry_index, symmetry in enumerate(stabilizers[KIND]):
                targets = tuple(
                    labeled.transform_factor(
                        factor, symmetry, factor_occurrence, occurrence_factor
                    )
                    for factor in moved
                )
                key = tuple(sorted(targets))
                if key in pair_witnesses:
                    left, right, scalar, labels = pair_witnesses[key]
                    witness = (
                        anchor_index, symmetry_index, key,
                        left, right, scalar, labels,
                    )
                    break
            if witness is not None:
                break
        if witness is not None:
            closed += 1
            anchor_counts[witness[0]] += 1
            semantic.update(repr((row, witness)).encode("ascii"))
    digest = semantic.hexdigest()
    if (
        closed != EXPECTED_ROW_COUNT
        or dict(anchor_counts) != EXPECTED_ANCHOR_INDEX_COUNTS
        or digest != EXPECTED_ROW_SEMANTIC
    ):
        raise AssertionError(
            f"row replay changed: {closed} {dict(anchor_counts)} {digest}"
        )
    remaining = count - closed
    if remaining != 1_638_786:
        raise AssertionError(f"unit-minor residue count changed: {remaining}")
    return closed, remaining, dict(anchor_counts), digest


def main():
    import argparse

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--sequential-residue", type=Path,
        help="optional regenerable 1,638,903-row residue for exhaustive row mapping",
    )
    arguments = parser.parse_args()

    records = parse_certificate(CERTIFICATE)
    occurrences, occurrence_factor, factor_polynomials = labeled.factor_polynomials()
    factor_occurrence = labeled.factor_action_is_well_defined(
        occurrences, occurrence_factor
    )
    canonical, anchor_alignments, stabilizers = labeled.canonical_anchor_alignments(
        occurrences, occurrence_factor, factor_occurrence
    )
    parent_by_label = {
        "".join(str(index + 1) for index in basis): polynomial
        for basis, polynomial in global_factors.bracket_records(
            global_factors.normalized_matrix()
        )
    }
    if len(parent_by_label) != 62:
        raise AssertionError("parent-bracket reconstruction changed")
    pair_witnesses, length_counts, pair_digest = replay_pairs(
        records, factor_polynomials, canonical[KIND], parent_by_label
    )
    print("PASS exact graph-restricted unit-minor pairs", len(pair_witnesses))
    print("PASS parent-product lengths", dict(sorted(length_counts.items())))
    print("PAIR_SEMANTIC", pair_digest)
    if arguments.sequential_residue is not None:
        closed, remaining, anchor_counts, row_digest = replay_rows(
            arguments.sequential_residue, pair_witnesses, canonical,
            anchor_alignments, stabilizers, factor_occurrence, occurrence_factor,
        )
        print("PASS exact sequential-residue rows", closed, anchor_counts)
        print("UNRESOLVED_AFTER_UNIT_MINOR", remaining)
        print("ROW_SEMANTIC", row_digest)
    else:
        print(
            "PROVENANCE exhaustive row mapping requires --sequential-residue",
            SEQUENTIAL_RESIDUE_SHA256,
        )
    print(
        "THEOREM each mapped row has a fixed nowhere-zero two-by-two Jacobian "
        "minor on its open eight-dimensional anchor graph domain"
    )
    print("CAVEAT this certificate is a positive subset, not an exhaustive unit-minor scan")


if __name__ == "__main__":
    main()
