#!/usr/bin/env python3
"""Exact overlap-at-most-eight atlas on all 2,604 catalog representatives.

The committed all-parent screen stores one minimum-overlap witness per exact
parent chart.  This verifier reconstructs the same complete escape-mask table,
checks its pinned record digest, proves the antipodal identity mask(rho) =
mask(-rho), and retains *every* antipodal pair orbit whose overlap is at most
eight directions.

The full run is intentionally explicit::

    python verify_diag2_near_counterexample_atlas.py --full --workers 8 \
        --analysis-output data/DIAG2_NEAR_COUNTEREXAMPLE_atlas8.json.gz

With no flags, the committed atlas is validated and parents 16, 860, and 2599
are replayed exactly.  This is an extremal point-sample atlas, not realization-
chamber coverage and not a proof of diagonal two.
"""

from __future__ import annotations

import argparse
from concurrent.futures import ProcessPoolExecutor, as_completed
import ctypes
import gzip
import hashlib
import json
import os
from pathlib import Path
import subprocess
import tempfile

import numpy as np

import DIAG9_GRAPH_exact_topes as exact_topes
import verify_diag2_common_shear_parent2604 as parent2604


HERE = Path(__file__).resolve().parent
SOURCE = HERE / "diag2_near_counterexample_fast.cpp"
BASE_SUMMARY = HERE / "data" / "DIAG2_COMMON_SHEAR_parent2604_summary.json"
SUMMARY = HERE / "data" / "DIAG2_NEAR_COUNTEREXAMPLE_atlas8.json.gz"

FORMAT = "diag2-near-counterexample-atlas8-v1"
THRESHOLD = 8
SENTINELS = (16, 860, 2599)
INITIAL_CAPACITY = 100_000
FULL_SIGNATURE_MASK = (1 << 56) - 1
HEX_DIGITS = frozenset("0123456789abcdef")
EXPECTED_AGGREGATE_DIGEST = (
    "377ca807cd8a3034677638ed55431ef83cce4cffa237834f3c530ec838f742ee"
)
EXPECTED_ACTIVE_PARENTS = 875
EXPECTED_PAIR_ORBITS = 1_154
EXPECTED_RAW_PAIRS = 4_616
EXPECTED_OVERLAP_HISTOGRAM = {"6": 212, "7": 50, "8": 892}

RESULT_FIELDS = frozenset(
    {
        "catalog_index",
        "matrix_digest",
        "topes",
        "valid_extensions",
        "bad_extensions",
        "canonical_bad_extensions",
        "minimum_escape",
        "minimum_overlap",
        "pair_orbits",
        "raw_pairs",
        "overlap_histogram",
        "record_digest",
        "pair_digest",
        "pairs",
    }
)
SUMMARY_FIELDS = frozenset(
    {
        "format",
        "threshold",
        "catalog_classes",
        "realizable_parents",
        "selected_indices",
        "tested_parents",
        "complete",
        "active_parents",
        "pair_orbits",
        "raw_pairs",
        "overlap_histogram",
        "aggregate_digest",
        "results",
    }
)


class NearResult(ctypes.Structure):
    _fields_ = [
        ("valid_count", ctypes.c_uint64),
        ("bad_count", ctypes.c_uint64),
        ("tope_count", ctypes.c_uint64),
        ("canonical_bad_count", ctypes.c_uint64),
        ("minimum_escape", ctypes.c_uint64),
        ("minimum_overlap", ctypes.c_uint64),
        ("pair_orbit_count", ctypes.c_uint64),
        ("raw_pair_count", ctypes.c_uint64),
        ("required_capacity", ctypes.c_uint64),
        ("overlap_histogram", ctypes.c_uint64 * 113),
        ("record_digest", ctypes.c_ubyte * 32),
        ("pair_digest", ctypes.c_ubyte * 32),
    ]


_LIBRARY = None
_ENTRY_INDEX = None
_REPLACEMENT_INDEX = None
_SORTING_SIGN = None


def compile_helper(output: Path):
    command = [
        "g++",
        "-std=c++17",
        "-O3",
        "-fPIC",
        "-shared",
        str(SOURCE),
        "-lcrypto",
        "-o",
        str(output),
    ]
    completed = subprocess.run(command, capture_output=True, text=True, check=False)
    if completed.returncode:
        raise RuntimeError(
            "failed to compile near-counterexample kernel:\n" + completed.stderr
        )


def initialize_worker(library_path: str):
    global _LIBRARY, _ENTRY_INDEX, _REPLACEMENT_INDEX, _SORTING_SIGN
    _LIBRARY = ctypes.CDLL(library_path)
    function = _LIBRARY.diag2_near_counterexample_audit
    function.argtypes = [
        ctypes.POINTER(ctypes.c_uint8),
        ctypes.POINTER(ctypes.c_uint64),
        ctypes.c_uint64,
        ctypes.POINTER(ctypes.c_uint8),
        ctypes.POINTER(ctypes.c_uint8),
        ctypes.POINTER(ctypes.c_int8),
        ctypes.c_uint64,
        ctypes.c_uint64,
        ctypes.POINTER(ctypes.c_uint64),
        ctypes.POINTER(ctypes.c_uint64),
        ctypes.POINTER(ctypes.c_uint8),
        ctypes.POINTER(NearResult),
        ctypes.c_char_p,
        ctypes.c_uint64,
    ]
    function.restype = ctypes.c_int
    _ENTRY_INDEX, _REPLACEMENT_INDEX, _SORTING_SIGN = parent2604.transport_arrays()


def call_helper(parent_bits, topes, capacity=INITIAL_CAPACITY):
    if _LIBRARY is None:
        raise AssertionError("near-counterexample kernel was not initialized")
    parent_bits = np.ascontiguousarray(parent_bits, dtype=np.uint8)
    topes = np.ascontiguousarray(topes, dtype=np.uint64)

    while True:
        pair_left = np.empty(capacity, dtype=np.uint64)
        pair_right = np.empty(capacity, dtype=np.uint64)
        pair_overlap = np.empty(capacity, dtype=np.uint8)
        result = NearResult()
        error = ctypes.create_string_buffer(1_024)
        code = _LIBRARY.diag2_near_counterexample_audit(
            parent_bits.ctypes.data_as(ctypes.POINTER(ctypes.c_uint8)),
            topes.ctypes.data_as(ctypes.POINTER(ctypes.c_uint64)),
            len(topes),
            _ENTRY_INDEX.ctypes.data_as(ctypes.POINTER(ctypes.c_uint8)),
            _REPLACEMENT_INDEX.ctypes.data_as(ctypes.POINTER(ctypes.c_uint8)),
            _SORTING_SIGN.ctypes.data_as(ctypes.POINTER(ctypes.c_int8)),
            THRESHOLD,
            capacity,
            pair_left.ctypes.data_as(ctypes.POINTER(ctypes.c_uint64)),
            pair_right.ctypes.data_as(ctypes.POINTER(ctypes.c_uint64)),
            pair_overlap.ctypes.data_as(ctypes.POINTER(ctypes.c_uint8)),
            ctypes.byref(result),
            error,
            len(error),
        )
        if code == 2:
            required = int(result.required_capacity)
            if required <= capacity:
                raise AssertionError("kernel reported an inconsistent output capacity")
            capacity = required
            continue
        if code:
            raise AssertionError(error.value.decode("utf-8", errors="replace"))
        count = int(result.pair_orbit_count)
        pairs = [
            [int(pair_left[index]), int(pair_right[index]), int(pair_overlap[index])]
            for index in range(count)
        ]
        return result, pairs


def load_base():
    tasks = parent2604.load_catalog_records()
    by_index = {task["catalog_index"]: task for task in tasks}
    payload = parent2604.verify_summary(by_index, path=BASE_SUMMARY)
    base = {record["catalog_index"]: record for record in payload["results"]}
    if set(base) != set(by_index):
        raise AssertionError("base all-parent summary has incomplete scope")
    return by_index, base


def is_hex_digest(value):
    return (
        type(value) is str
        and len(value) == 64
        and not (set(value) - HEX_DIGITS)
    )


def canonical_signature(signature):
    return min(signature, FULL_SIGNATURE_MASK ^ signature)


def pair_semantic_digest(pairs):
    digest = hashlib.sha256()
    digest.update(b"diag2-near-counterexample-pairs-v1\0")
    digest.update(THRESHOLD.to_bytes(8, "little"))
    for left, right, overlap in pairs:
        digest.update(left.to_bytes(8, "little"))
        digest.update(right.to_bytes(8, "little"))
        digest.update(overlap.to_bytes(8, "little"))
    return digest.hexdigest()


def audit_parent(task, base):
    matrix = parent2604.normalize_matrix(task["matrix"], f"parent {task['catalog_index']}")
    expected_signs = tuple(1 if symbol == "+" else -1 for symbol in task["chi"])
    actual_signs = exact_topes.parent_signs(matrix)
    if actual_signs != expected_signs:
        raise AssertionError(
            f"parent {task['catalog_index']}: exact matrix has the wrong chirotope"
        )
    rows = exact_topes.derived_rows(matrix)
    enumerated = exact_topes.enumerate_topes(rows, dimension=4)
    exact_topes.verify_topes(rows, enumerated)
    topes = np.fromiter(enumerated, dtype=np.uint64, count=len(enumerated))

    result, pairs = call_helper(
        np.fromiter((sign > 0 for sign in actual_signs), dtype=np.uint8),
        topes,
    )
    histogram = {
        str(overlap): int(result.overlap_histogram[overlap])
        for overlap in range(THRESHOLD + 1)
        if result.overlap_histogram[overlap]
    }
    report = {
        "catalog_index": task["catalog_index"],
        "matrix_digest": task["matrix_digest"],
        "topes": int(result.tope_count),
        "valid_extensions": int(result.valid_count),
        "bad_extensions": int(result.bad_count),
        "canonical_bad_extensions": int(result.canonical_bad_count),
        "minimum_escape": int(result.minimum_escape),
        "minimum_overlap": int(result.minimum_overlap),
        "pair_orbits": int(result.pair_orbit_count),
        "raw_pairs": int(result.raw_pair_count),
        "overlap_histogram": histogram,
        "record_digest": bytes(result.record_digest).hex(),
        "pair_digest": bytes(result.pair_digest).hex(),
        "pairs": pairs,
    }
    validate_result(report, task, base)
    return report


def validate_result(record, task, base):
    context = f"parent {task['catalog_index']} near-pair record"
    if type(record) is not dict or set(record) != RESULT_FIELDS:
        raise AssertionError(f"{context}: wrong schema")
    if (
        record["catalog_index"] != task["catalog_index"]
        or record["matrix_digest"] != task["matrix_digest"]
        or record["topes"] != base["topes"]
        or record["valid_extensions"] != base["valid_extensions"]
        or record["bad_extensions"] != base["bad_extensions"]
        or record["minimum_escape"] != base["minimum_escape"]
        or record["minimum_overlap"] != base["minimum_overlap"]
        or record["record_digest"] != base["record_digest"]
    ):
        raise AssertionError(f"{context}: provenance disagrees with all-parent screen")
    if record["canonical_bad_extensions"] * 2 != record["bad_extensions"]:
        raise AssertionError(f"{context}: antipodal quotient count is inconsistent")
    if record["raw_pairs"] != 4 * record["pair_orbits"]:
        raise AssertionError(f"{context}: raw/orbit pair counts are inconsistent")
    if not is_hex_digest(record["pair_digest"]):
        raise AssertionError(f"{context}: malformed pair digest")
    if type(record["pairs"]) is not list or len(record["pairs"]) != record["pair_orbits"]:
        raise AssertionError(f"{context}: pair payload count is inconsistent")
    previous = None
    histogram = {str(index): 0 for index in range(THRESHOLD + 1)}
    for pair in record["pairs"]:
        if (
            type(pair) is not list
            or len(pair) != 3
            or any(type(value) is not int for value in pair)
        ):
            raise AssertionError(f"{context}: malformed pair")
        left, right, overlap = pair
        if (
            not 0 <= left < right <= FULL_SIGNATURE_MASK
            or left != canonical_signature(left)
            or right != canonical_signature(right)
            or not 0 <= overlap <= THRESHOLD
        ):
            raise AssertionError(f"{context}: noncanonical or out-of-range pair")
        key = (left, right)
        if previous is not None and key <= previous:
            raise AssertionError(f"{context}: pairs are duplicated or out of order")
        previous = key
        histogram[str(overlap)] += 1
    histogram = {key: value for key, value in histogram.items() if value}
    if record["overlap_histogram"] != histogram:
        raise AssertionError(f"{context}: overlap histogram disagrees with pairs")
    if record["pair_orbits"] != sum(histogram.values()):
        raise AssertionError(f"{context}: pair-orbit count disagrees with histogram")
    if record["pair_digest"] != pair_semantic_digest(record["pairs"]):
        raise AssertionError(f"{context}: pair semantic digest is inconsistent")

    base_minimum = base["minimum_overlap"]
    if base_minimum <= THRESHOLD:
        if not record["pairs"] or record["minimum_overlap"] != base_minimum:
            raise AssertionError(f"{context}: minimum overlap was not recovered")
        witness = tuple(
            sorted(
                (
                    canonical_signature(base["overlap_left"]),
                    canonical_signature(base["overlap_right"]),
                )
            )
        )
        if not any(tuple(pair[:2]) == witness for pair in record["pairs"]):
            raise AssertionError(f"{context}: stored minimum witness is absent")
    elif record["pairs"] or record["minimum_overlap"] <= THRESHOLD:
        raise AssertionError(f"{context}: unexpected threshold pair")


def aggregate_digest(results):
    digest = hashlib.sha256()
    digest.update(FORMAT.encode("ascii") + b"\0")
    digest.update(THRESHOLD.to_bytes(8, "little"))
    numeric_fields = (
        "catalog_index",
        "topes",
        "valid_extensions",
        "bad_extensions",
        "canonical_bad_extensions",
        "minimum_escape",
        "minimum_overlap",
        "pair_orbits",
        "raw_pairs",
    )
    for record in sorted(results, key=lambda item: item["catalog_index"]):
        digest.update(bytes.fromhex(record["matrix_digest"]))
        for field in numeric_fields:
            digest.update(int(record[field]).to_bytes(16, "little"))
        digest.update(bytes.fromhex(record["record_digest"]))
        digest.update(bytes.fromhex(record["pair_digest"]))
    return digest.hexdigest()


def summary_payload(results, selected_indices, complete):
    selected_indices = tuple(selected_indices)
    if selected_indices != tuple(sorted(set(selected_indices))):
        raise AssertionError("selected indices are not sorted and unique")
    results = sorted(results, key=lambda item: item["catalog_index"])
    result_indices = [record["catalog_index"] for record in results]
    if result_indices != sorted(set(result_indices)) or not set(result_indices) <= set(selected_indices):
        raise AssertionError("results do not match the selected parent scope")
    actual_complete = len(results) == len(selected_indices)
    if bool(complete) != actual_complete:
        raise AssertionError("summary completeness flag disagrees with result count")
    histogram = {
        str(overlap): sum(
            record["overlap_histogram"].get(str(overlap), 0) for record in results
        )
        for overlap in range(THRESHOLD + 1)
    }
    histogram = {key: value for key, value in histogram.items() if value}
    return {
        "format": FORMAT,
        "threshold": THRESHOLD,
        "catalog_classes": parent2604.EXPECTED_CATALOG,
        "realizable_parents": parent2604.EXPECTED_REALIZABLE,
        "selected_indices": list(selected_indices),
        "tested_parents": len(results),
        "complete": actual_complete,
        "active_parents": sum(bool(record["pair_orbits"]) for record in results),
        "pair_orbits": sum(record["pair_orbits"] for record in results),
        "raw_pairs": sum(record["raw_pairs"] for record in results),
        "overlap_histogram": histogram,
        "aggregate_digest": aggregate_digest(results),
        "results": results,
    }


def write_payload(path, results, selected_indices, complete):
    payload = summary_payload(results, selected_indices, complete)
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


def validate_payload(payload, selected_indices, by_index, base_by_index, *, require_complete=False):
    if type(payload) is not dict or set(payload) != SUMMARY_FIELDS:
        raise AssertionError("near-counterexample summary has the wrong schema")
    if payload["format"] != FORMAT or payload["threshold"] != THRESHOLD:
        raise AssertionError("near-counterexample summary has the wrong format")
    if payload["selected_indices"] != list(selected_indices):
        raise AssertionError("near-counterexample summary scope changed")
    results = payload["results"]
    if type(results) is not list or payload["tested_parents"] != len(results):
        raise AssertionError("near-counterexample result count is inconsistent")
    for record in results:
        index = record.get("catalog_index") if type(record) is dict else None
        if type(index) is not int or index not in by_index or index not in selected_indices:
            raise AssertionError("near-counterexample summary contains a foreign parent")
        validate_result(record, by_index[index], base_by_index[index])
    candidate = summary_payload(results, selected_indices, complete=len(results) == len(selected_indices))
    for field in SUMMARY_FIELDS - {"results"}:
        if payload[field] != candidate[field]:
            raise AssertionError(f"near-counterexample aggregate field changed: {field}")
    if require_complete and not payload["complete"]:
        raise AssertionError("near-counterexample summary is incomplete")
    return results


def verify_full_pins(payload):
    if (
        payload["aggregate_digest"] != EXPECTED_AGGREGATE_DIGEST
        or payload["active_parents"] != EXPECTED_ACTIVE_PARENTS
        or payload["pair_orbits"] != EXPECTED_PAIR_ORBITS
        or payload["raw_pairs"] != EXPECTED_RAW_PAIRS
        or payload["overlap_histogram"] != EXPECTED_OVERLAP_HISTOGRAM
    ):
        raise AssertionError("complete near-counterexample atlas pins changed")


def parse_indices(text):
    return tuple(sorted({int(value) for value in text.split(",") if value.strip()}))


def parse_args():
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--full", action="store_true", help="replay all 2,604 parents")
    group.add_argument("--indices", type=parse_indices, help="comma-separated parent indices")
    parser.add_argument(
        "--workers",
        type=int,
        default=min(8, os.cpu_count() or 1),
        help="parallel exact-tope workers (default: min(8, CPU count))",
    )
    parser.add_argument("--analysis-output", type=Path, help="atomic JSON output/checkpoint")
    parser.add_argument("--resume", action="store_true", help="resume an existing checkpoint")
    return parser.parse_args()


def main():
    args = parse_args()
    by_index, base_by_index = load_base()
    if args.full:
        selected_indices = tuple(sorted(by_index))
    elif args.indices is not None:
        selected_indices = args.indices
    else:
        stored = read_payload(SUMMARY)
        full_scope = tuple(sorted(by_index))
        validate_payload(
            stored,
            full_scope,
            by_index,
            base_by_index,
            require_complete=True,
        )
        verify_full_pins(stored)
        selected_indices = SENTINELS
        print("PASS stored complete near-counterexample atlas", stored["aggregate_digest"])
    missing = sorted(set(selected_indices) - set(by_index))
    if missing:
        raise ValueError(f"selected indices are not realizable parents: {missing}")
    if not selected_indices:
        raise ValueError("no parents selected")
    if args.workers < 1:
        raise ValueError("--workers must be positive")

    results = []
    if args.resume:
        if args.analysis_output is None or not args.analysis_output.exists():
            raise ValueError("--resume requires an existing --analysis-output")
        checkpoint = read_payload(args.analysis_output)
        results = validate_payload(
            checkpoint, selected_indices, by_index, base_by_index
        )
        print("RESUME", len(results), "completed;", len(selected_indices) - len(results), "remaining")
    completed = {record["catalog_index"] for record in results}
    selected = [
        (by_index[index], base_by_index[index])
        for index in selected_indices
        if index not in completed
    ]

    if selected:
        with tempfile.TemporaryDirectory(prefix="diag2-near-counterexample-") as build:
            library = Path(build) / "libdiag2_near_counterexample_fast.so"
            compile_helper(library)
            with ProcessPoolExecutor(
                max_workers=args.workers,
                initializer=initialize_worker,
                initargs=(str(library),),
            ) as executor:
                futures = {
                    executor.submit(audit_parent, task, base): task["catalog_index"]
                    for task, base in selected
                }
                for future in as_completed(futures):
                    result = future.result()
                    results.append(result)
                    print(
                        "PASS parent",
                        result["catalog_index"],
                        "near-orbits",
                        result["pair_orbits"],
                        "hist",
                        result["overlap_histogram"],
                        flush=True,
                    )
                    if args.analysis_output is not None and (
                        len(results) % 25 == 0 or len(results) == len(selected_indices)
                    ):
                        write_payload(
                            args.analysis_output,
                            results,
                            selected_indices,
                            complete=len(results) == len(selected_indices),
                        )

    payload = summary_payload(results, selected_indices, complete=True)
    if args.analysis_output is not None:
        write_payload(args.analysis_output, results, selected_indices, complete=True)
        print("WROTE", args.analysis_output)
    print("AGGREGATE_DIGEST", payload["aggregate_digest"])
    print("ACTIVE_PARENTS", payload["active_parents"])
    print("PAIR_ORBITS", payload["pair_orbits"])
    print("RAW_PAIRS", payload["raw_pairs"])
    print("OVERLAP_HISTOGRAM", payload["overlap_histogram"])

    if not args.full and args.indices is None:
        stored_by_index = {record["catalog_index"]: record for record in stored["results"]}
        for result in results:
            if result != stored_by_index[result["catalog_index"]]:
                raise AssertionError(
                    f"sentinel parent {result['catalog_index']} disagrees with atlas"
                )
        print("PASS exact sentinel parents reproduce their stored near-pair records")
    elif args.full:
        if len(results) != parent2604.EXPECTED_REALIZABLE:
            raise AssertionError("full replay did not test 2,604 parents")
        verify_full_pins(payload)
        print("THEOREM AUDIT every overlap-at-most-eight pair orbit was retained")
        print("SCOPE one exact chart per parent; no residual-chamber coverage")


if __name__ == "__main__":
    main()
