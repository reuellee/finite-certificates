#!/usr/bin/env python3
"""Exact minimal-separator profiles for the diagonal-two near-pair atlas.

For every antipodal pair orbit retained by
``verify_diag2_near_counterexample_atlas.py``, this verifier reconstructs the
inclusion-minimal source-local tope separators of both signatures.  It stores
their row supports, label carriers, nonescape covers, and the eight common-
escape deficits of the pair.

The output is evidence for theorem synthesis.  It is a complete description
of the near pairs at one exact representative per realizable parent class,
not a universal realization-chamber theorem.
"""

from __future__ import annotations

import argparse
from collections import Counter
from concurrent.futures import ProcessPoolExecutor, as_completed
import gzip
import hashlib
from itertools import combinations
import json
import os
from pathlib import Path

import DIAG9_GRAPH_exact_topes as exact_topes
import verify_diag2_escape_minimal_separators as minimal
import verify_diag2_near_counterexample_atlas as near


HERE = Path(__file__).resolve().parent
ATLAS = HERE / "data" / "DIAG2_NEAR_COUNTEREXAMPLE_atlas8.json.gz"
SUMMARY = HERE / "data" / "DIAG2_NEAR_COUNTEREXAMPLE_separators8.json.gz"

FORMAT = "diag2-near-counterexample-separators8-v1"
LOCAL_DIRECTIONS = 14
LOCAL_MASK = (1 << LOCAL_DIRECTIONS) - 1
FULL_DIRECTION_MASK = (1 << 112) - 1
SENTINELS = near.SENTINELS
EXPECTED_AGGREGATE_DIGEST = (
    "543fed1a543f9a596e243548c2d05b0b3f4f20da5d82116f3136b1936413a16e"
)
EXPECTED_PAIR_ORBITS = 1_154
EXPECTED_UNIQUE_SIGNATURES = 2_307
EXPECTED_SEPARATOR_SIZE_HISTOGRAM = {"1": 27_684}
EXPECTED_SOURCE_FAMILY_HISTOGRAM = {"0": 106, "1": 9_016, "2": 9_334}
EXPECTED_SOURCE_OVERLAP_TYPES = 523
EXPECTED_MUTATION_DEGREE_HISTOGRAM = {
    "0,1,1,2,2,2,2,2": 106,
    "1,1,1,1,2,2,2,2": 2_201,
}

SEPARATOR_FIELDS = frozenset({"rows", "row_count", "carrier", "cover"})
SOURCE_FIELDS = frozenset(
    {
        "source",
        "raw_candidates",
        "minimal_separators",
        "nonescape_mask",
        "escape_mask",
    }
)
PROFILE_FIELDS = frozenset({"signature", "escape_mask", "escape_size", "sources"})
PAIR_FIELDS = frozenset(
    {"left", "right", "overlap", "source_common_masks", "source_common_counts"}
)
RESULT_FIELDS = frozenset(
    {
        "catalog_index",
        "matrix_digest",
        "pair_digest",
        "topes",
        "pair_orbits",
        "unique_signatures",
        "separator_size_histogram",
        "source_family_histogram",
        "profiles",
        "pairs",
        "record_digest",
    }
)
SUMMARY_FIELDS = frozenset(
    {
        "format",
        "atlas_digest",
        "selected_indices",
        "tested_parents",
        "complete",
        "pair_orbits",
        "unique_signatures",
        "separator_size_histogram",
        "source_family_histogram",
        "source_overlap_histogram",
        "all_pairs_have_a_common_escape",
        "aggregate_digest",
        "results",
    }
)


def load_atlas(path=ATLAS):
    by_index, base_by_index = near.load_base()
    payload = near.read_payload(path)
    full_scope = tuple(sorted(by_index))
    near.validate_payload(
        payload,
        full_scope,
        by_index,
        base_by_index,
        require_complete=True,
    )
    active = {
        record["catalog_index"]: record
        for record in payload["results"]
        if record["pair_orbits"]
    }
    if len(active) != payload["active_parents"]:
        raise AssertionError("near-pair active-parent count is inconsistent")
    return payload, by_index, active


def localize(mask, source):
    return (mask >> ((source - 1) * LOCAL_DIRECTIONS)) & LOCAL_MASK


def carrier_labels(source, separator):
    carrier = set()
    for index in minimal.support_indices(separator):
        triple = minimal.moving.TRIPLES[index]
        if source not in triple:
            raise AssertionError("minimal separator left its source star")
        carrier.update(label for label in triple if label != source)
    if len(carrier) < 2:
        raise AssertionError("nonempty separator has fewer than two carrier labels")
    return sorted(carrier)


def signature_profile(signature, indexes):
    full_escape = 0
    sources = []
    for source in range(1, 9):
        raw_count, separators = minimal.minimal_separators(signature, indexes[source])
        entries = []
        local_nonescape = 0
        for separator in separators:
            global_cover = minimal.separator_nonescape_cover(
                signature, source, separator
            )
            cover = localize(global_cover, source)
            if not cover or cover.bit_count() > 5:
                raise AssertionError("separator has an invalid local cover")
            local_nonescape |= cover
            entries.append(
                {
                    "rows": separator,
                    "row_count": separator.bit_count(),
                    "carrier": carrier_labels(source, separator),
                    "cover": cover,
                }
            )
        local_escape = LOCAL_MASK ^ local_nonescape
        full_escape |= local_escape << ((source - 1) * LOCAL_DIRECTIONS)
        sources.append(
            {
                "source": source,
                "raw_candidates": raw_count,
                "minimal_separators": entries,
                "nonescape_mask": local_nonescape,
                "escape_mask": local_escape,
            }
        )
    return {
        "signature": signature,
        "escape_mask": f"{full_escape:028x}",
        "escape_size": full_escape.bit_count(),
        "sources": sources,
    }


def result_digest(record):
    intrinsic = {key: value for key, value in record.items() if key != "record_digest"}
    digest = hashlib.sha256()
    digest.update(b"diag2-near-counterexample-separators8-record-v1\0")
    digest.update(
        json.dumps(intrinsic, sort_keys=True, separators=(",", ":")).encode("ascii")
    )
    return digest.hexdigest()


def audit_parent(task, atlas_record):
    matrix = near.parent2604.normalize_matrix(
        task["matrix"], f"parent {task['catalog_index']}"
    )
    expected_signs = tuple(1 if symbol == "+" else -1 for symbol in task["chi"])
    if exact_topes.parent_signs(matrix) != expected_signs:
        raise AssertionError(
            f"parent {task['catalog_index']}: exact matrix has the wrong chirotope"
        )
    rows = exact_topes.derived_rows(matrix)
    enumerated = exact_topes.enumerate_topes(rows, dimension=4)
    exact_topes.verify_topes(rows, enumerated)
    topes = tuple(enumerated)
    if len(topes) != atlas_record["topes"]:
        raise AssertionError("separator replay has the wrong tope count")
    indexes = minimal.build_source_indexes(topes)

    signatures = sorted(
        {signature for pair in atlas_record["pairs"] for signature in pair[:2]}
    )
    profiles = [signature_profile(signature, indexes) for signature in signatures]
    by_signature = {
        profile["signature"]: int(profile["escape_mask"], 16)
        for profile in profiles
    }
    pairs = []
    for left, right, expected_overlap in atlas_record["pairs"]:
        common = by_signature[left] & by_signature[right]
        source_masks = [localize(common, source) for source in range(1, 9)]
        counts = [mask.bit_count() for mask in source_masks]
        if sum(counts) != expected_overlap or common.bit_count() != expected_overlap:
            raise AssertionError("minimal separators reconstructed the wrong overlap")
        pairs.append(
            {
                "left": left,
                "right": right,
                "overlap": expected_overlap,
                "source_common_masks": source_masks,
                "source_common_counts": counts,
            }
        )

    separator_sizes = Counter()
    source_families = Counter()
    for profile in profiles:
        for source in profile["sources"]:
            family = source["minimal_separators"]
            source_families[len(family)] += 1
            separator_sizes.update(entry["row_count"] for entry in family)
    report = {
        "catalog_index": task["catalog_index"],
        "matrix_digest": task["matrix_digest"],
        "pair_digest": atlas_record["pair_digest"],
        "topes": len(topes),
        "pair_orbits": len(pairs),
        "unique_signatures": len(profiles),
        "separator_size_histogram": {
            str(key): value for key, value in sorted(separator_sizes.items())
        },
        "source_family_histogram": {
            str(key): value for key, value in sorted(source_families.items())
        },
        "profiles": profiles,
        "pairs": pairs,
    }
    report["record_digest"] = result_digest(report)
    validate_result(report, task, atlas_record)
    return report


def validate_result(record, task, atlas_record):
    context = f"parent {task['catalog_index']} separator record"
    if type(record) is not dict or set(record) != RESULT_FIELDS:
        raise AssertionError(f"{context}: wrong schema")
    if (
        record["catalog_index"] != task["catalog_index"]
        or record["matrix_digest"] != task["matrix_digest"]
        or record["pair_digest"] != atlas_record["pair_digest"]
        or record["topes"] != atlas_record["topes"]
        or record["pair_orbits"] != atlas_record["pair_orbits"]
        or record["record_digest"] != result_digest(record)
    ):
        raise AssertionError(f"{context}: provenance or digest mismatch")
    profiles = record["profiles"]
    if type(profiles) is not list or record["unique_signatures"] != len(profiles):
        raise AssertionError(f"{context}: profile count is inconsistent")
    if [profile.get("signature") for profile in profiles] != sorted(
        profile.get("signature") for profile in profiles
    ):
        raise AssertionError(f"{context}: profiles are not sorted")
    by_signature = {}
    separator_sizes = Counter()
    source_families = Counter()
    for profile in profiles:
        if type(profile) is not dict or set(profile) != PROFILE_FIELDS:
            raise AssertionError(f"{context}: malformed signature profile")
        signature = profile["signature"]
        if (
            type(signature) is not int
            or signature != near.canonical_signature(signature)
            or type(profile["escape_mask"]) is not str
            or len(profile["escape_mask"]) != 28
        ):
            raise AssertionError(f"{context}: invalid signature or escape mask")
        escape = int(profile["escape_mask"], 16)
        if escape > FULL_DIRECTION_MASK or escape.bit_count() != profile["escape_size"]:
            raise AssertionError(f"{context}: escape cardinality is inconsistent")
        sources = profile["sources"]
        if type(sources) is not list or len(sources) != 8:
            raise AssertionError(f"{context}: wrong source count")
        rebuilt_escape = 0
        for source_index, source in enumerate(sources, start=1):
            if type(source) is not dict or set(source) != SOURCE_FIELDS:
                raise AssertionError(f"{context}: malformed source profile")
            if source["source"] != source_index:
                raise AssertionError(f"{context}: source profiles are out of order")
            family = source["minimal_separators"]
            if (
                type(source["raw_candidates"]) is not int
                or source["raw_candidates"] < 0
                or type(family) is not list
                or source["raw_candidates"] < len(family)
            ):
                raise AssertionError(f"{context}: separator family is not a list")
            union = 0
            previous = None
            row_supports = []
            for entry in family:
                if type(entry) is not dict or set(entry) != SEPARATOR_FIELDS:
                    raise AssertionError(f"{context}: malformed separator entry")
                rows = entry["rows"]
                cover = entry["cover"]
                if (
                    type(rows) is not int
                    or not 0 < rows <= near.FULL_SIGNATURE_MASK
                    or rows.bit_count() != entry["row_count"]
                    or type(entry["carrier"]) is not list
                    or entry["carrier"] != carrier_labels(source_index, rows)
                    or type(cover) is not int
                    or not 0 < cover <= LOCAL_MASK
                    or cover.bit_count() > 5
                    or cover
                    != localize(
                        minimal.separator_nonescape_cover(
                            signature, source_index, rows
                        ),
                        source_index,
                    )
                ):
                    raise AssertionError(f"{context}: invalid separator entry")
                key = (rows.bit_count(), rows)
                if previous is not None and key < previous:
                    raise AssertionError(f"{context}: separator family is out of order")
                previous = key
                union |= cover
                row_supports.append(rows)
                separator_sizes[rows.bit_count()] += 1
            if any(
                left != right and left & right == left
                for left in row_supports
                for right in row_supports
            ):
                raise AssertionError(f"{context}: separator family is not an antichain")
            source_families[len(family)] += 1
            if (
                source["nonescape_mask"] != union
                or source["escape_mask"] != (LOCAL_MASK ^ union)
            ):
                raise AssertionError(f"{context}: source cover is inconsistent")
            rebuilt_escape |= source["escape_mask"] << (
                (source_index - 1) * LOCAL_DIRECTIONS
            )
        if rebuilt_escape != escape or signature in by_signature:
            raise AssertionError(f"{context}: profile escape reconstruction failed")
        by_signature[signature] = escape
    if record["separator_size_histogram"] != {
        str(key): value for key, value in sorted(separator_sizes.items())
    }:
        raise AssertionError(f"{context}: separator-size histogram changed")
    if record["source_family_histogram"] != {
        str(key): value for key, value in sorted(source_families.items())
    }:
        raise AssertionError(f"{context}: source-family histogram changed")

    if type(record["pairs"]) is not list or len(record["pairs"]) != record["pair_orbits"]:
        raise AssertionError(f"{context}: pair count is inconsistent")
    expected_pairs = [tuple(pair) for pair in atlas_record["pairs"]]
    actual_pairs = []
    for pair in record["pairs"]:
        if type(pair) is not dict or set(pair) != PAIR_FIELDS:
            raise AssertionError(f"{context}: malformed pair profile")
        left, right, overlap = pair["left"], pair["right"], pair["overlap"]
        common = by_signature[left] & by_signature[right]
        masks = [localize(common, source) for source in range(1, 9)]
        counts = [mask.bit_count() for mask in masks]
        if (
            pair["source_common_masks"] != masks
            or pair["source_common_counts"] != counts
            or sum(counts) != overlap
        ):
            raise AssertionError(f"{context}: source overlap profile is inconsistent")
        actual_pairs.append((left, right, overlap))
    if actual_pairs != expected_pairs:
        raise AssertionError(f"{context}: pair identities changed")


def add_histogram(target, source):
    for key, value in source.items():
        target[key] += value


def aggregate_digest(results):
    digest = hashlib.sha256()
    digest.update(FORMAT.encode("ascii") + b"\0")
    for record in sorted(results, key=lambda item: item["catalog_index"]):
        digest.update(bytes.fromhex(record["record_digest"]))
    return digest.hexdigest()


def summary_payload(results, selected_indices, atlas_digest, complete):
    selected_indices = tuple(selected_indices)
    results = sorted(results, key=lambda item: item["catalog_index"])
    indices = [record["catalog_index"] for record in results]
    if indices != sorted(set(indices)) or not set(indices) <= set(selected_indices):
        raise AssertionError("separator results do not match the selected scope")
    actual_complete = len(results) == len(selected_indices)
    if bool(complete) != actual_complete:
        raise AssertionError("separator completeness flag is inconsistent")
    separator_sizes = Counter()
    source_families = Counter()
    overlap_profiles = Counter()
    for record in results:
        add_histogram(separator_sizes, record["separator_size_histogram"])
        add_histogram(source_families, record["source_family_histogram"])
        for pair in record["pairs"]:
            key = ",".join(str(value) for value in pair["source_common_counts"])
            overlap_profiles[key] += 1
    return {
        "format": FORMAT,
        "atlas_digest": atlas_digest,
        "selected_indices": list(selected_indices),
        "tested_parents": len(results),
        "complete": actual_complete,
        "pair_orbits": sum(record["pair_orbits"] for record in results),
        "unique_signatures": sum(record["unique_signatures"] for record in results),
        "separator_size_histogram": dict(sorted(separator_sizes.items())),
        "source_family_histogram": dict(sorted(source_families.items())),
        "source_overlap_histogram": dict(sorted(overlap_profiles.items())),
        "all_pairs_have_a_common_escape": all(
            pair["overlap"] > 0 for record in results for pair in record["pairs"]
        ),
        "aggregate_digest": aggregate_digest(results),
        "results": results,
    }


def write_payload(path, results, selected_indices, atlas_digest, complete):
    payload = summary_payload(results, selected_indices, atlas_digest, complete)
    temporary = path.with_name(path.name + ".tmp")
    raw = (json.dumps(payload, indent=2, sort_keys=True) + "\n").encode("utf-8")
    if path.suffix == ".gz":
        temporary.write_bytes(gzip.compress(raw, compresslevel=9, mtime=0))
    else:
        temporary.write_bytes(raw)
    temporary.replace(path)


def read_payload(path):
    raw = Path(path).read_bytes()
    if Path(path).suffix == ".gz":
        raw = gzip.decompress(raw)
    return json.loads(raw.decode("utf-8"))


def validate_payload(payload, selected_indices, atlas_digest, by_index, active, *, require_complete=False):
    if type(payload) is not dict or set(payload) != SUMMARY_FIELDS:
        raise AssertionError("separator summary has the wrong schema")
    if payload["format"] != FORMAT or payload["atlas_digest"] != atlas_digest:
        raise AssertionError("separator summary has the wrong format or atlas")
    if payload["selected_indices"] != list(selected_indices):
        raise AssertionError("separator summary scope changed")
    results = payload["results"]
    if type(results) is not list or payload["tested_parents"] != len(results):
        raise AssertionError("separator summary result count is inconsistent")
    for record in results:
        index = record.get("catalog_index") if type(record) is dict else None
        if type(index) is not int or index not in by_index or index not in active:
            raise AssertionError("separator summary contains a foreign parent")
        validate_result(record, by_index[index], active[index])
    candidate = summary_payload(
        results, selected_indices, atlas_digest, complete=len(results) == len(selected_indices)
    )
    for field in SUMMARY_FIELDS - {"results"}:
        if payload[field] != candidate[field]:
            raise AssertionError(f"separator aggregate field changed: {field}")
    if require_complete and not payload["complete"]:
        raise AssertionError("separator summary is incomplete")
    return results


def verify_full_pins(payload):
    if (
        payload["aggregate_digest"] != EXPECTED_AGGREGATE_DIGEST
        or payload["pair_orbits"] != EXPECTED_PAIR_ORBITS
        or payload["unique_signatures"] != EXPECTED_UNIQUE_SIGNATURES
        or payload["separator_size_histogram"]
        != EXPECTED_SEPARATOR_SIZE_HISTOGRAM
        or payload["source_family_histogram"]
        != EXPECTED_SOURCE_FAMILY_HISTOGRAM
        or len(payload["source_overlap_histogram"])
        != EXPECTED_SOURCE_OVERLAP_TYPES
    ):
        raise AssertionError("complete near-pair separator atlas pins changed")
    degree_histogram = Counter()
    for record in payload["results"]:
        for profile in record["profiles"]:
            occurrences = {}
            for source in profile["sources"]:
                for entry in source["minimal_separators"]:
                    if entry["row_count"] != 1:
                        raise AssertionError("near-pair endpoint has a nonsingleton separator")
                    row = entry["rows"].bit_length() - 1
                    occurrences.setdefault(row, []).append(source["source"])
            if len(occurrences) != 4:
                raise AssertionError("near-pair endpoint does not have four mutations")
            degrees = Counter()
            used_pairs = Counter()
            for row, sources in occurrences.items():
                triple = minimal.moving.TRIPLES[row]
                if tuple(sources) != triple:
                    raise AssertionError("singleton mutation lacks its three source copies")
                degrees.update(triple)
                used_pairs.update(combinations(triple, 2))
            if max(used_pairs.values()) > 1:
                raise AssertionError("near-pair mutation hypergraph is not linear")
            degree_key = ",".join(
                str(value)
                for value in sorted(degrees[label] for label in range(1, 9))
            )
            degree_histogram[degree_key] += 1
    if dict(sorted(degree_histogram.items())) != EXPECTED_MUTATION_DEGREE_HISTOGRAM:
        raise AssertionError("near-pair mutation degree-sequence census changed")


def parse_indices(text):
    return tuple(sorted({int(value) for value in text.split(",") if value.strip()}))


def parse_args():
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--full", action="store_true", help="replay every active parent")
    group.add_argument("--indices", type=parse_indices, help="comma-separated active parents")
    parser.add_argument("--atlas", type=Path, default=ATLAS, help="near-pair atlas path")
    parser.add_argument(
        "--workers", type=int, default=min(8, os.cpu_count() or 1), help="worker count"
    )
    parser.add_argument("--analysis-output", type=Path, help="atomic JSON output/checkpoint")
    parser.add_argument("--resume", action="store_true", help="resume an existing checkpoint")
    return parser.parse_args()


def main():
    args = parse_args()
    atlas, by_index, active = load_atlas(args.atlas)
    atlas_digest = atlas["aggregate_digest"]
    active_indices = tuple(sorted(active))
    if args.full:
        selected_indices = active_indices
    elif args.indices is not None:
        selected_indices = args.indices
    else:
        stored = read_payload(SUMMARY)
        validate_payload(
            stored,
            active_indices,
            atlas_digest,
            by_index,
            active,
            require_complete=True,
        )
        verify_full_pins(stored)
        selected_indices = SENTINELS
        print("PASS stored complete separator atlas", stored["aggregate_digest"])
    missing = sorted(set(selected_indices) - set(active))
    if missing:
        raise ValueError(f"selected parents have no overlap-at-most-eight pairs: {missing}")
    if not selected_indices or args.workers < 1:
        raise ValueError("selected parent scope and worker count must be positive")

    results = []
    if args.resume:
        if args.analysis_output is None or not args.analysis_output.exists():
            raise ValueError("--resume requires an existing --analysis-output")
        checkpoint = read_payload(args.analysis_output)
        results = validate_payload(
            checkpoint, selected_indices, atlas_digest, by_index, active
        )
        print("RESUME", len(results), "completed;", len(selected_indices) - len(results), "remaining")
    completed = {record["catalog_index"] for record in results}
    selected = [index for index in selected_indices if index not in completed]

    if selected:
        with ProcessPoolExecutor(max_workers=args.workers) as executor:
            futures = {
                executor.submit(audit_parent, by_index[index], active[index]): index
                for index in selected
            }
            for future in as_completed(futures):
                result = future.result()
                results.append(result)
                print(
                    "PASS parent",
                    result["catalog_index"],
                    "pairs",
                    result["pair_orbits"],
                    "signatures",
                    result["unique_signatures"],
                    flush=True,
                )
                if args.analysis_output is not None and (
                    len(results) % 25 == 0 or len(results) == len(selected_indices)
                ):
                    write_payload(
                        args.analysis_output,
                        results,
                        selected_indices,
                        atlas_digest,
                        complete=len(results) == len(selected_indices),
                    )

    payload = summary_payload(results, selected_indices, atlas_digest, complete=True)
    if args.analysis_output is not None:
        write_payload(
            args.analysis_output, results, selected_indices, atlas_digest, complete=True
        )
        print("WROTE", args.analysis_output)
    print("AGGREGATE_DIGEST", payload["aggregate_digest"])
    print("PAIR_ORBITS", payload["pair_orbits"])
    print("UNIQUE_SIGNATURES", payload["unique_signatures"])
    print("SEPARATOR_SIZE_HISTOGRAM", payload["separator_size_histogram"])
    print("SOURCE_FAMILY_HISTOGRAM", payload["source_family_histogram"])
    print("SOURCE_OVERLAP_TYPES", len(payload["source_overlap_histogram"]))

    if not args.full and args.indices is None:
        stored_by_index = {record["catalog_index"]: record for record in stored["results"]}
        for result in results:
            if result != stored_by_index[result["catalog_index"]]:
                raise AssertionError(
                    f"sentinel parent {result['catalog_index']} disagrees with separator atlas"
                )
        print("PASS exact sentinel parents reproduce their separator profiles")
    elif args.full:
        verify_full_pins(payload)
        print("THEOREM AUDIT every retained pair has an exact eight-source profile")
        print("SCOPE one exact chart per parent; universal cover contradiction remains open")


if __name__ == "__main__":
    main()
