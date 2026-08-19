#!/usr/bin/env python3
"""Independent exact replay of the direct-final-affinity triple layer."""

from __future__ import annotations

import argparse
import hashlib
from pathlib import Path
import struct
import sys


HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import DIAG2_PIVOT_LABELED_PAIR_ORBITS_VERIFY as labeled  # noqa: E402
import DIAG2_PIVOT_REPRESENTATIVE_TRIPLES_VERIFY as triples  # noqa: E402
import verify_diag2_pivot_all_pair_fibers as fibers  # noqa: E402
import verify_residual_log_binomials as poly  # noqa: E402


CERTIFICATE = HERE / "data/DIAG3_triple_direct_final_affinity_certificates.bin"
CERTIFICATE_BYTES = 4_212_318
CERTIFICATE_SHA256 = (
    "6ed192d1dd2f814ae914349ec2dbcc654ffb663669b85f1b289fa37feb147f26"
)
STREAM_SEMANTIC = (
    "7cd37ee421c651563bb6dbeae45b6711b71839893ba53abfb7240b1e165f2b1a"
)
MAGIC = b"D3DFAF2\0"
HEADER_FORMAT = "<8sB3xII"
BLOCK_FORMAT = "<BBHI"
RECORD_FORMAT = "<HHHBBBBBBHHBbB"
TOTAL_RECORDS = 128_198
UNION_COUNT = 58_673
SOURCE_COUNT = 1_221_055
SOURCE_BYTES = 7_326_334
SOURCE_SHA256 = (
    "bdd29e7647a99429f38c7bc20e9e5b9b514dccf7cbf57f9cd9b1b36fec7e7d92"
)
RESIDUE_COUNT = 1_162_382
RESIDUE_SEMANTIC = (
    "44ff9f5f0ea6c332c0382717533f5fa4b8e4b8af3d72024f9d4b0c74e6448dda"
)

# Priority order is part of the certificate contract.  The fourth entry is
# the standalone witness count, the fifth its exact ordered semantic, and the
# last two entries pin the number of distinct second-slope/final algebra keys.
EXPECTED_BLOCKS = (
    (48, 0, 8, 8,
     "96502ea6ad420dc0f5be22da7ee2fa1ca098b21df61f601ad0630404d37ec188",
     5, 8),
    (48, 1, 8, 0,
     "7eab29363a826b80ad81b175cedd26296417ffb0062c95c52ddaab8b81abda00",
     5, 8),
    (48, 2, 8, 0,
     "0fa360b83b7e6acb2d2e88dbc998e66ca2e0d7618783ff01f83bc87b073eef13",
     5, 8),
    (49, 1, 8_488, 8_488,
     "500518b56a6507307d373d9460ff87c5dda5de731790037fc08ac5e016c9b41e",
     1_754, 8_488),
    (49, 3, 8_497, 15,
     "0bf7bb84c3ad3ba0e88b864b6764b66fcffacbc4b6288a279aa723c8100ea761",
     1_772, 8_497),
    (49, 5, 8_503, 6,
     "927a804f85397d6a4f056fb82a29b7e5fcc3237dea80eee62eef8cb93667f3e5",
     1_779, 8_503),
    (50, 1, 29_963, 29_846,
     "0308f1c3148b7e12af04ffede41673ff91b6db451a9fef4f0908b96b57ffa0bc",
     4_520, 29_963),
    (50, 3, 30_483, 527,
     "62fef3ec741b71b1a0409f5f23203b93652a4347ba5d7e973e29dc584ecc7c4e",
     4_645, 30_483),
    (51, 5, 21_161, 19_573,
     "57048240800b06c1687ca627e071b357e507c2f59fd12a20e9d33a0f9dad8e3b",
     2_269, 21_161),
    (51, 6, 21_079, 210,
     "f8c0579fffb1fbafedcc0f2f4d0e4ddeed5ae66ccd39b9237db2356c1c77a3b5",
     2_294, 21_079),
)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def transform_factor(factor, mapping, factor_occurrence, occurrence_factor):
    occurrence = factor_occurrence[factor]
    return occurrence_factor[
        tuple(sorted(mapping[index] for index in occurrence))
    ]


def parse_certificate():
    if CERTIFICATE.stat().st_size != CERTIFICATE_BYTES:
        raise AssertionError("direct-final certificate byte count changed")
    actual = sha256(CERTIFICATE)
    if actual != CERTIFICATE_SHA256:
        raise AssertionError(f"direct-final certificate SHA-256 changed: {actual}")
    raw = CERTIFICATE.read_bytes()
    magic, block_count, total, union_count = struct.unpack_from(
        HEADER_FORMAT, raw
    )
    if (
        magic != MAGIC
        or block_count != len(EXPECTED_BLOCKS)
        or total != TOTAL_RECORDS
        or union_count != UNION_COUNT
    ):
        raise AssertionError("direct-final certificate header changed")
    position = struct.calcsize(HEADER_FORMAT)
    fixed_size = struct.calcsize(RECORD_FORMAT)
    stream_semantic = hashlib.sha256(
        b"diag3-triple-direct-final-affinity-stream-v2\0"
    )
    blocks = []
    priority_rows = set()
    increments = []
    for expected in EXPECTED_BLOCKS:
        kind_expected, pivot_expected, count_expected = expected[:3]
        block_start = position
        kind, pivot, reserved, count = struct.unpack_from(
            BLOCK_FORMAT, raw, position
        )
        position += struct.calcsize(BLOCK_FORMAT)
        if (
            (kind, pivot) != (kind_expected, pivot_expected)
            or reserved != 0
            or count != count_expected
        ):
            raise AssertionError("direct-final block header changed")
        records = []
        seen = set()
        semantic = hashlib.sha256(
            b"diag3-direct-final-affinity-exact-v1\0"
        )
        increment = 0
        for number in range(count):
            fields = struct.unpack_from(RECORD_FORMAT, raw, position)
            position += fixed_size
            label_count = fields[-1]
            labels = tuple(
                raw[position + 4 * index:position + 4 * (index + 1)].decode(
                    "ascii"
                )
                for index in range(label_count)
            )
            position += 4 * label_count
            row = fields[:3]
            if row in seen or len(set(row)) != 3:
                raise AssertionError(
                    f"bad row in block {(kind, pivot)} record {number}"
                )
            seen.add(row)
            (
                anchor_index, recorded_kind, first_pivot, symmetry_index,
                order, second_pivot, second_factor, third_factor,
                final_coordinate, scalar, _label_count,
            ) = fields[3:]
            witness = (
                anchor_index, recorded_kind, first_pivot, symmetry_index,
                order, second_factor, third_factor, second_pivot,
                final_coordinate, (scalar, labels),
            )
            record = row, witness
            records.append(record)
            semantic.update(repr(record).encode("ascii"))
            if row not in priority_rows:
                priority_rows.add(row)
                increment += 1
        stream_semantic.update(raw[block_start:position])
        if semantic.hexdigest() != expected[4]:
            raise AssertionError(f"block semantic changed for {(kind, pivot)}")
        if increment != expected[3]:
            raise AssertionError(f"priority increment changed for {(kind, pivot)}")
        increments.append(increment)
        blocks.append(((kind, pivot), tuple(records)))
    if position != len(raw) or sum(increments) != UNION_COUNT:
        raise AssertionError("direct-final EOF or union count changed")
    if stream_semantic.hexdigest() != STREAM_SEMANTIC:
        raise AssertionError("direct-final stream semantic changed")
    return tuple(blocks), priority_rows, tuple(increments)


def replay_exact(blocks, union_only: bool):
    occurrences, occurrence_factor, factor_polynomials = labeled.factor_polynomials()
    factor_occurrence = labeled.factor_action_is_well_defined(
        occurrences, occurrence_factor
    )
    canonical, alignments, stabilizers = labeled.canonical_anchor_alignments(
        occurrences, occurrence_factor, factor_occurrence
    )
    parents = labeled.parent_bracket_factors()
    chart_cache = {}
    replayed_rows = set()
    all_slope_counts = []
    all_final_counts = []

    for block_index, ((kind, first_pivot), records) in enumerate(blocks):
        expected = EXPECTED_BLOCKS[block_index]
        chart = kind, first_pivot
        if chart not in chart_cache:
            anchor = factor_polynomials[canonical[kind]]
            first_slope, first_constant = fibers.pivot_split(
                anchor, first_pivot
            )
            if poly.add(
                poly.multiply(first_slope, poly.variable(first_pivot)),
                first_constant,
            ) != anchor:
                raise AssertionError(f"first graph reconstruction changed {chart}")
            first_certificate = triples.bracket_factorization(
                first_slope, parents, depth=20
            )
            if first_certificate is None or first_certificate[0] == 0:
                raise AssertionError(f"first slope is not a parent unit {chart}")
            first_numerator = poly.negative(first_constant)
            restricted_parents = {}
            for label, parent, _sign in parents:
                restricted = fibers.graph_restrict(
                    parent, first_pivot, first_slope, first_numerator
                )
                if not restricted:
                    raise AssertionError(f"parent {label} vanishes in {chart}")
                if len(restricted) == 1 and poly.ZERO_EXPONENT in restricted:
                    continue
                restricted_parents[label] = restricted
            chart_cache[chart] = (
                first_slope, first_numerator, restricted_parents, {}
            )
        first_slope, first_numerator, restricted_parents, restricted = (
            chart_cache[chart]
        )
        slope_cache = {}
        final_cache = {}
        for number, (row, witness) in enumerate(records):
            if union_only and row in replayed_rows:
                continue
            replayed_rows.add(row)
            (
                anchor_index, recorded_kind, recorded_pivot, symmetry_index,
                order, second_factor, third_factor, second_pivot,
                final_coordinate, certificate,
            ) = witness
            scalar, labels = certificate
            if (
                (recorded_kind, recorded_pivot) != chart
                or not 0 <= anchor_index < 3
                or not 0 <= symmetry_index < len(stabilizers[kind])
                or order not in (0, 1)
                or not 0 <= second_factor < len(factor_polynomials)
                or not 0 <= third_factor < len(factor_polynomials)
                or second_factor == third_factor
                or not 0 <= second_pivot < 9
                or not 0 <= final_coordinate < 9
                or len({first_pivot, second_pivot, final_coordinate}) != 3
                or scalar == 0
            ):
                raise AssertionError(f"bad metadata in {chart} record {number}")
            mapping = alignments[kind].get(row[anchor_index])
            if mapping is None or transform_factor(
                row[anchor_index], mapping, factor_occurrence, occurrence_factor
            ) != canonical[kind]:
                raise AssertionError(f"bad anchor in {chart} record {number}")
            moved = tuple(
                transform_factor(
                    row[index], mapping, factor_occurrence, occurrence_factor
                )
                for index in range(3)
                if index != anchor_index
            )
            symmetry = stabilizers[kind][symmetry_index]
            targets = tuple(
                transform_factor(
                    factor, symmetry, factor_occurrence, occurrence_factor
                )
                for factor in moved
            )
            if (second_factor, third_factor) != (
                targets[order], targets[1 - order]
            ):
                raise AssertionError(f"bad transport in {chart} record {number}")
            for factor in (second_factor, third_factor):
                if factor not in restricted:
                    restricted[factor] = fibers.graph_restrict(
                        factor_polynomials[factor],
                        first_pivot,
                        first_slope,
                        first_numerator,
                    )
            second = restricted[second_factor]
            slope_key = second_factor, second_pivot, scalar, labels
            if slope_key not in slope_cache:
                second_slope, second_constant = fibers.pivot_split(
                    second, second_pivot
                )
                if poly.add(
                    poly.multiply(
                        second_slope, poly.variable(second_pivot)
                    ),
                    second_constant,
                ) != second:
                    raise AssertionError(
                        f"second graph reconstruction in {chart} record {number}"
                    )
                product = poly.constant(scalar)
                for label in labels:
                    if label not in restricted_parents:
                        raise AssertionError(
                            f"bad parent label {label} in {chart} record {number}"
                        )
                    product = poly.multiply(product, restricted_parents[label])
                if product != second_slope:
                    raise AssertionError(
                        f"false second unit in {chart} record {number}"
                    )
                slope_cache[slope_key] = second_slope, second_constant
            second_slope, second_constant = slope_cache[slope_key]
            final_key = (
                second_factor, second_pivot, third_factor, final_coordinate
            )
            if final_key not in final_cache:
                final = fibers.graph_restrict(
                    restricted[third_factor],
                    second_pivot,
                    second_slope,
                    poly.negative(second_constant),
                )
                if any(
                    monomial[first_pivot] or monomial[second_pivot]
                    for monomial in final
                ):
                    raise AssertionError(
                        f"graph coordinate survives in {chart} record {number}"
                    )
                if any(monomial[final_coordinate] > 1 for monomial in final):
                    raise AssertionError(
                        f"false direct-final affinity in {chart} record {number}"
                    )
                final_cache[final_key] = True
        all_slope_counts.append(len(slope_cache))
        all_final_counts.append(len(final_cache))
        if not union_only and (
            len(slope_cache) != expected[5]
            or len(final_cache) != expected[6]
        ):
            raise AssertionError(f"algebra key census changed for {chart}")
        print(
            "PASS exact direct-final block", chart,
            "records", len(records) if not union_only else "priority-only",
            "slope keys", len(slope_cache),
            "final keys", len(final_cache),
            flush=True,
        )
    if union_only and len(replayed_rows) != UNION_COUNT:
        raise AssertionError("exact priority-union replay count changed")
    if not union_only and len(replayed_rows) != UNION_COUNT:
        # replayed_rows remains a set even though every block occurrence ran.
        raise AssertionError("exact full-block union count changed")
    return replayed_rows, tuple(all_slope_counts), tuple(all_final_counts)


def replay_source(path: Path, union_rows):
    if path.stat().st_size != SOURCE_BYTES or sha256(path) != SOURCE_SHA256:
        raise AssertionError("direct-final source pin changed")
    raw = path.read_bytes()
    count, = struct.unpack_from("<I", raw)
    if count != SOURCE_COUNT or len(raw) != 4 + 6 * count:
        raise AssertionError("bad direct-final source layout")
    source_rows = []
    source_set = set()
    for row in struct.iter_unpack("<HHH", raw[4:]):
        if row in source_set or len(set(row)) != 3:
            raise AssertionError(f"bad direct-final source row {row}")
        source_rows.append(row)
        source_set.add(row)
    if not union_rows <= source_set:
        raise AssertionError(
            f"direct-final certificate has {len(union_rows-source_set)} external rows"
        )
    digest = hashlib.sha256()
    remaining = 0
    for row in source_rows:
        if row not in union_rows:
            digest.update(struct.pack("<HHH", *row))
            remaining += 1
    if remaining != RESIDUE_COUNT or digest.hexdigest() != RESIDUE_SEMANTIC:
        raise AssertionError("direct-final residue pin changed")
    print(
        "PASS source/priority union/residue",
        SOURCE_COUNT, UNION_COUNT, RESIDUE_COUNT, digest.hexdigest(),
    )


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--source-residue",
        type=Path,
        help="optional pinned 1,221,055-row input for source/residue replay",
    )
    parser.add_argument(
        "--all-block-records",
        action="store_true",
        help="also replay algebra for cross-chart duplicate witnesses",
    )
    arguments = parser.parse_args()

    blocks, parsed_union, increments = parse_certificate()
    replayed_union, _slope_counts, _final_counts = replay_exact(
        blocks, union_only=not arguments.all_block_records
    )
    if replayed_union != parsed_union:
        raise AssertionError("parsed and exact priority unions differ")
    if arguments.source_residue is not None:
        replay_source(arguments.source_residue, replayed_union)
    print("PASS direct-final standalone counts", tuple(x[2] for x in EXPECTED_BLOCKS))
    print("PASS direct-final priority increments", increments)
    print("PASS direct-final priority union", len(replayed_union))
    print("CERTIFICATE_SHA256", CERTIFICATE_SHA256)
    print("STREAM_SEMANTIC", STREAM_SEMANTIC)
    print(
        "THEOREM two exact parent-unit graphs followed by a directly affine "
        "fully cleared final equation exclude compact components"
    )
    if arguments.source_residue is None:
        print("CAVEAT pass --source-residue to replay source membership/residue")
    if not arguments.all_block_records:
        print("CAVEAT pass --all-block-records to replay duplicate chart witnesses")


if __name__ == "__main__":
    main()
