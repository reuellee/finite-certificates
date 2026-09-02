#!/usr/bin/env python3
"""Exact one-chart common-shear screen for all 2,604 realizable UOM(4,8)s.

The repository contains one exact integer 4x8 realization for every
realizable catalog parent.  For each selected parent this verifier:

1. recomputes all 70 parent-bracket signs from the matrix;
2. reconstructs and verifies every complete tope of the 56-row derived
   arrangement with the existing exact integer recursion;
3. enumerates every abstract uniform single-element extension by the exact
   Grassmann--Pluecker backtracker; and
4. computes the 112-direction moving-witness escape set of every bad
   extension and tests all pairs for a common direction.

The last two Boolean-heavy steps use ``diag2_common_shear_fast.cpp``.  A
parent-16 replay is independently matched bit-for-bit against the original
pure-Python implementation in ``verify_diag2_escape_set_topes.py``.

The full command is intentionally explicit because the 2,604 matrices are a
point transversal, not a chamber atlas::

    python verify_diag2_common_shear_parent2604.py --full \
        --analysis-output data/DIAG2_COMMON_SHEAR_parent2604_summary.json

With no flag, the committed summary is checked and, when a supported native
toolchain can build and load the pinned kernel, three exact sentinel parents
are replayed.  Otherwise the verifier reports its validated stored-summary
fallback explicitly.  Neither mode claims residual-chamber coverage or
promotes diagonal two.

The one-time ``--upgrade-summary`` mode accepts only a complete canonical v1
full-sweep artifact, validates every legacy record against the catalog and
extension census, and atomically enriches it to the strict v2 schema.
"""

from __future__ import annotations

import argparse
from concurrent.futures import ProcessPoolExecutor, as_completed
import ctypes
import hashlib
import json
import os
from pathlib import Path
import shlex
import shutil
import subprocess
import sys
import tempfile

import numpy as np

import DIAG9_GRAPH_exact_topes as exact_topes
import four_chart_gate as gate
import verify_diag2_escape_set_topes as escape


HERE = Path(__file__).resolve().parent
CATALOG = gate.CATALOG_48
CERTIFICATES = HERE / "certs_4_8.jsonl"
EXTCOUNTS = gate.EXTCOUNTS
SOURCE = HERE / "diag2_common_shear_fast.cpp"
SUMMARY = HERE / "data" / "DIAG2_COMMON_SHEAR_parent2604_summary.json"

LEGACY_FORMAT = "diag2-common-shear-parent2604-v1"
FORMAT = "diag2-common-shear-parent2604-v2"
EXPECTED_CATALOG = 2_628
EXPECTED_REALIZABLE = 2_604
SENTINELS = (16, 860, 2599)
EXPECTED_PARENT16_RECORD_DIGEST = (
    "942d7cac1ce3afff4ff0299c5b9acb382e60c4350616f9b42eb49385fd831737"
)

# Pinned by the first independent complete replay and its strict v1-to-v2
# provenance upgrade (catalog chirotopes, exact matrices, and extension census).
EXPECTED_AGGREGATE_DIGEST = (
    "58b5a8cb8f6e36466efabb6dc6a4ba1b9bf9f812f5899f5138d6abc96c2c8a18"
)
EXPECTED_KERNEL_SHA256 = (
    "1a8b7a5292c2e424eff4bd6a164629f27db15b7903094e33ed407b136073754e"
)
EXPECTED_GLOBAL_MINIMUM_ESCAPE = 52
EXPECTED_GLOBAL_MINIMUM_OVERLAP = 6

SIGNATURE_LIMIT = 1 << 56
HEX_DIGITS = frozenset("0123456789abcdef")
RESULT_FIELDS = frozenset(
    {
        "catalog_index",
        "chi",
        "matrix_digest",
        "expected_extensions",
        "topes",
        "valid_extensions",
        "bad_extensions",
        "minimum_escape",
        "minimum_escape_count",
        "minimum_overlap",
        "overlap_left",
        "overlap_right",
        "overlap_left_size",
        "overlap_right_size",
        "pairwise_intersection",
        "disjoint_left",
        "disjoint_right",
        "record_digest",
    }
)
LEGACY_RESULT_FIELDS = RESULT_FIELDS - {"matrix_digest", "expected_extensions"}
SUMMARY_FIELDS = frozenset(
    {
        "format",
        "catalog_classes",
        "realizable_parents",
        "selected_parents",
        "selected_indices",
        "tested_parents",
        "complete",
        "all_pairwise_intersecting",
        "aggregate_digest",
        "global_minimum_escape",
        "global_minimum_overlap",
        "results",
    }
)
LEGACY_SUMMARY_FIELDS = SUMMARY_FIELDS - {"selected_indices"}


class AuditResult(ctypes.Structure):
    _fields_ = [
        ("valid_count", ctypes.c_uint64),
        ("bad_count", ctypes.c_uint64),
        ("tope_count", ctypes.c_uint64),
        ("minimum_escape", ctypes.c_uint64),
        ("minimum_escape_count", ctypes.c_uint64),
        ("minimum_overlap", ctypes.c_uint64),
        ("overlap_left", ctypes.c_uint64),
        ("overlap_right", ctypes.c_uint64),
        ("overlap_left_size", ctypes.c_uint64),
        ("overlap_right_size", ctypes.c_uint64),
        ("disjoint_found", ctypes.c_uint64),
        ("disjoint_left", ctypes.c_uint64),
        ("disjoint_right", ctypes.c_uint64),
        ("record_digest", ctypes.c_ubyte * 32),
    ]


_LIBRARY = None
_ENTRY_INDEX = None
_REPLACEMENT_INDEX = None
_SORTING_SIGN = None


class NativeToolchainUnavailable(RuntimeError):
    """The optional native kernel cannot be built or loaded on this host."""


def transport_arrays():
    entries = []
    for source in range(1, 9):
        for target in range(1, 9):
            if source != target:
                transport, _source_mask = escape.source_transport_data(source, target)
                entries.extend(transport)
    if len(entries) != 56 * 15:
        raise AssertionError("wrong elementary-shear transport table")
    return (
        np.asarray([entry[0] for entry in entries], dtype=np.uint8),
        np.asarray([entry[1] for entry in entries], dtype=np.uint8),
        np.asarray([entry[2] for entry in entries], dtype=np.int8),
    )


def verify_kernel_source():
    digest = hashlib.sha256(SOURCE.read_bytes()).hexdigest()
    if digest != EXPECTED_KERNEL_SHA256:
        raise AssertionError(
            "diagonal-two finite-kernel source digest changed: " + digest
        )


def parse_compiler_command(configured):
    """Parse the platform command line supplied through ``CXX``."""
    if not configured.strip():
        raise RuntimeError("CXX is set but empty")
    configured = configured.strip()
    if os.name == "nt":
        argc = ctypes.c_int()
        command_line_to_argv = ctypes.windll.shell32.CommandLineToArgvW
        command_line_to_argv.argtypes = (
            ctypes.c_wchar_p,
            ctypes.POINTER(ctypes.c_int),
        )
        command_line_to_argv.restype = ctypes.POINTER(ctypes.c_wchar_p)
        argv = command_line_to_argv(configured, ctypes.byref(argc))
        if not argv:
            raise RuntimeError(f"invalid CXX command: {ctypes.WinError()}")
        try:
            return tuple(argv[index] for index in range(argc.value))
        finally:
            local_free = ctypes.windll.kernel32.LocalFree
            local_free.argtypes = (ctypes.c_void_p,)
            local_free.restype = ctypes.c_void_p
            local_free(ctypes.cast(argv, ctypes.c_void_p))
    try:
        command = shlex.split(configured, posix=True)
    except ValueError as error:
        raise RuntimeError(f"invalid CXX command: {error}") from error
    if not command:
        raise RuntimeError("CXX is set but empty")
    return tuple(command)


def compiler_candidates():
    if "CXX" in os.environ:
        command = parse_compiler_command(os.environ["CXX"])
        if shutil.which(command[0]) is None and not Path(command[0]).is_file():
            raise RuntimeError(f"CXX compiler is not executable: {command[0]}")
        return (command,), True
    candidates = []
    seen = set()
    for candidate in ("g++", "clang++"):
        resolved = shutil.which(candidate)
        if resolved is not None and resolved not in seen:
            candidates.append((resolved,))
            seen.add(resolved)
    return tuple(candidates), False


def compile_helper(output: Path, compiler):
    command = [
        *compiler,
        "-std=c++17",
        "-O3",
    ]
    if os.name != "nt":
        command.append("-fPIC")
    command.extend(
        [
            "-dynamiclib" if sys.platform == "darwin" else "-shared",
            str(SOURCE),
            "-lcrypto",
            "-o",
            str(output),
        ]
    )
    try:
        completed = subprocess.run(
            command, capture_output=True, text=True, check=False
        )
    except OSError as error:
        raise NativeToolchainUnavailable(
            f"failed to invoke {compiler[0]}: {error}"
        ) from error
    if completed.returncode:
        raise NativeToolchainUnavailable(
            "failed to compile diagonal-two finite kernel:\n" + completed.stderr
        )


def preflight_library(library: Path):
    probe = (
        "import ctypes,sys; "
        "library=ctypes.CDLL(sys.argv[1]); "
        "getattr(library,'diag2_common_shear_audit')"
    )
    try:
        completed = subprocess.run(
            [sys.executable, "-c", probe, str(library)],
            capture_output=True,
            text=True,
            check=False,
        )
    except OSError as error:
        raise NativeToolchainUnavailable(
            f"compiled diagonal-two kernel preflight cannot be launched: {error}"
        ) from error
    if completed.returncode:
        detail = completed.stderr.strip() or completed.stdout.strip()
        raise NativeToolchainUnavailable(
            "compiled diagonal-two kernel cannot be loaded or does not export "
            f"diag2_common_shear_audit:\n{detail}"
        )


def native_failure_report(failures):
    return "\n".join(
        f"{compiler[0]}:\n{error}" for compiler, error in failures
    )


def print_stored_fallback(reason):
    print(
        "PASS portable stored-summary gate; compiled sentinel replay "
        f"unavailable ({reason})"
    )
    print(
        "SCOPE full v2 artifact, catalog, matrices, extension census, and "
        "aggregate digest validated; use --require-compiled-replay for a "
        "strict live-kernel gate"
    )


def initialize_worker(library_path: str):
    global _LIBRARY, _ENTRY_INDEX, _REPLACEMENT_INDEX, _SORTING_SIGN
    _LIBRARY = ctypes.CDLL(library_path)
    function = _LIBRARY.diag2_common_shear_audit
    function.argtypes = [
        ctypes.POINTER(ctypes.c_uint8),
        ctypes.POINTER(ctypes.c_uint64),
        ctypes.c_uint64,
        ctypes.POINTER(ctypes.c_uint8),
        ctypes.POINTER(ctypes.c_uint8),
        ctypes.POINTER(ctypes.c_int8),
        ctypes.POINTER(AuditResult),
        ctypes.c_char_p,
        ctypes.c_uint64,
    ]
    function.restype = ctypes.c_int
    _ENTRY_INDEX, _REPLACEMENT_INDEX, _SORTING_SIGN = transport_arrays()


def call_helper(parent_bits, topes):
    if _LIBRARY is None:
        raise AssertionError("finite kernel was not initialized")
    parent_bits = np.ascontiguousarray(parent_bits, dtype=np.uint8)
    topes = np.ascontiguousarray(topes, dtype=np.uint64)
    result = AuditResult()
    error = ctypes.create_string_buffer(1_024)
    code = _LIBRARY.diag2_common_shear_audit(
        parent_bits.ctypes.data_as(ctypes.POINTER(ctypes.c_uint8)),
        topes.ctypes.data_as(ctypes.POINTER(ctypes.c_uint64)),
        len(topes),
        _ENTRY_INDEX.ctypes.data_as(ctypes.POINTER(ctypes.c_uint8)),
        _REPLACEMENT_INDEX.ctypes.data_as(ctypes.POINTER(ctypes.c_uint8)),
        _SORTING_SIGN.ctypes.data_as(ctypes.POINTER(ctypes.c_int8)),
        ctypes.byref(result),
        error,
        len(error),
    )
    if code:
        raise AssertionError(error.value.decode("utf-8", errors="replace"))
    return result


def normalize_matrix(matrix, label):
    if not isinstance(matrix, (list, tuple)) or len(matrix) != 4:
        raise AssertionError(f"{label}: parent matrix does not have four rows")
    normalized = []
    for row in matrix:
        if not isinstance(row, (list, tuple)) or len(row) != 8:
            raise AssertionError(f"{label}: parent matrix does not have shape 4x8")
        if any(type(value) is not int for value in row):
            raise AssertionError(f"{label}: parent matrix contains a non-integer")
        normalized.append(tuple(row))
    return tuple(normalized)


def matrix_semantic_digest(matrix):
    matrix = normalize_matrix(matrix, "matrix digest")
    digest = hashlib.sha256()
    digest.update(b"diag2-parent-matrix-v1\0")
    digest.update(
        json.dumps(matrix, ensure_ascii=True, separators=(",", ":")).encode("ascii")
    )
    return digest.hexdigest()


def load_extension_counts():
    rows = [
        json.loads(line)
        for line in EXTCOUNTS.open(encoding="utf-8")
        if line.strip()
    ]
    if len(rows) != EXPECTED_CATALOG:
        raise AssertionError("wrong UOM(4,8) extension-count row count")
    by_index = {}
    for row in rows:
        if set(row) != {"i", "E", "stab"}:
            raise AssertionError("UOM(4,8) extension-count row has the wrong schema")
        if any(type(row[field]) is not int for field in ("i", "E", "stab")):
            raise AssertionError("UOM(4,8) extension-count row is not integral")
        if (
            not 0 <= row["i"] < EXPECTED_CATALOG
            or row["E"] <= 0
            or row["stab"] <= 0
            or row["i"] in by_index
        ):
            raise AssertionError("invalid UOM(4,8) extension-count row")
        by_index[row["i"]] = row["E"]
    if set(by_index) != set(range(EXPECTED_CATALOG)):
        raise AssertionError("UOM(4,8) extension-count indices are incomplete")
    return by_index


def load_catalog_records():
    catalog = [line.strip() for line in CATALOG.open(encoding="utf-8") if line.strip()]
    certificates = [
        json.loads(line)
        for line in CERTIFICATES.open(encoding="utf-8")
        if line.strip()
    ]
    if len(catalog) != EXPECTED_CATALOG or len(certificates) != EXPECTED_CATALOG:
        raise AssertionError("wrong UOM(4,8) catalog or certificate count")
    if any(len(chi) != 70 or set(chi) - {"+", "-"} for chi in catalog):
        raise AssertionError("malformed UOM(4,8) catalog chirotope")
    by_chi = {record["chi"]: record for record in certificates}
    if len(by_chi) != EXPECTED_CATALOG or set(by_chi) != set(catalog):
        raise AssertionError("certificate ledger and UOM(4,8) catalog disagree")
    extension_counts = load_extension_counts()
    answer = []
    for catalog_index, chi in enumerate(catalog):
        record = by_chi[chi]
        if record["verdict"] == "REALIZABLE":
            matrix = normalize_matrix(record["matrix"], f"parent {catalog_index}")
            answer.append(
                {
                    "catalog_index": catalog_index,
                    "chi": chi,
                    "matrix": matrix,
                    "matrix_digest": matrix_semantic_digest(matrix),
                    "expected_extensions": extension_counts[catalog_index],
                }
            )
        elif record["verdict"] != "NON_REALIZABLE":
            raise AssertionError("certificate ledger has an unresolved parent")
    if len(answer) != EXPECTED_REALIZABLE:
        raise AssertionError("wrong realizable UOM(4,8) count")
    return answer


def is_hex_digest(value):
    return (
        type(value) is str
        and len(value) == 64
        and not (set(value) - HEX_DIGITS)
    )


def validate_result_record(record, expected_task, context="result record"):
    if type(record) is not dict or set(record) != RESULT_FIELDS:
        raise AssertionError(f"{context}: wrong result-record schema")
    integer_fields = RESULT_FIELDS - {
        "chi",
        "matrix_digest",
        "pairwise_intersection",
        "record_digest",
    }
    if any(type(record[field]) is not int for field in integer_fields):
        raise AssertionError(f"{context}: a numeric result field is not an integer")
    if type(record["pairwise_intersection"]) is not bool:
        raise AssertionError(f"{context}: pairwise verdict is not Boolean")
    for field in ("matrix_digest", "record_digest"):
        if not is_hex_digest(record[field]):
            raise AssertionError(f"{context}: {field} is not a lowercase SHA-256")
    if (
        record["catalog_index"] != expected_task["catalog_index"]
        or record["chi"] != expected_task["chi"]
        or record["matrix_digest"] != expected_task["matrix_digest"]
        or record["expected_extensions"] != expected_task["expected_extensions"]
    ):
        raise AssertionError(f"{context}: result does not match its catalog task")
    if record["valid_extensions"] != record["expected_extensions"]:
        raise AssertionError(f"{context}: GP extension count disagrees with census")
    if (
        record["topes"] <= 0
        or record["bad_extensions"] < 2
        or record["bad_extensions"] + record["topes"]
        != record["valid_extensions"]
    ):
        raise AssertionError(f"{context}: tope/bad/valid counts are inconsistent")
    if (
        not 0 <= record["minimum_escape"] <= 112
        or not 1 <= record["minimum_escape_count"] <= record["bad_extensions"]
        or not 0 <= record["minimum_overlap"] <= 112
    ):
        raise AssertionError(f"{context}: escape or overlap minimum is out of range")
    for field in ("overlap_left", "overlap_right"):
        if not 0 <= record[field] < SIGNATURE_LIMIT:
            raise AssertionError(
                f"{context}: overlap witness is not a 56-bit signature"
            )
    if record["overlap_left"] == record["overlap_right"]:
        raise AssertionError(f"{context}: overlap witnesses are not distinct")
    for field in ("overlap_left_size", "overlap_right_size"):
        if not 0 <= record[field] <= 112:
            raise AssertionError(f"{context}: overlap-witness size is out of range")
    if (
        record["minimum_escape"]
        > min(record["overlap_left_size"], record["overlap_right_size"])
        or record["minimum_overlap"]
        > min(record["overlap_left_size"], record["overlap_right_size"])
        or record["overlap_left_size"]
        + record["overlap_right_size"]
        - record["minimum_overlap"]
        > 112
    ):
        raise AssertionError(f"{context}: overlap-witness cardinalities are impossible")
    if record["pairwise_intersection"] != (record["minimum_overlap"] > 0):
        raise AssertionError(
            f"{context}: pairwise verdict disagrees with minimum overlap"
        )
    for field in ("disjoint_left", "disjoint_right"):
        if not 0 <= record[field] < SIGNATURE_LIMIT:
            raise AssertionError(
                f"{context}: disjoint witness is not a 56-bit signature"
            )
    if record["pairwise_intersection"]:
        if record["disjoint_left"] or record["disjoint_right"]:
            raise AssertionError(
                f"{context}: intersecting record stores a disjoint witness"
            )
    elif (
        record["disjoint_left"] != record["overlap_left"]
        or record["disjoint_right"] != record["overlap_right"]
    ):
        raise AssertionError(
            f"{context}: disjoint witness disagrees with overlap witness"
        )


def audit_parent(task):
    matrix = normalize_matrix(task["matrix"], f"parent {task['catalog_index']}")
    if matrix_semantic_digest(matrix) != task["matrix_digest"]:
        raise AssertionError(f"parent {task['catalog_index']}: matrix digest changed")
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
    result = call_helper(
        np.fromiter((sign > 0 for sign in actual_signs), dtype=np.uint8),
        topes,
    )
    if int(result.valid_count) != task["expected_extensions"]:
        raise AssertionError(
            f"parent {task['catalog_index']}: compiled GP count disagrees "
            "with extcount_4_9.jsonl"
        )
    report = {
        "catalog_index": task["catalog_index"],
        "chi": task["chi"],
        "matrix_digest": task["matrix_digest"],
        "expected_extensions": task["expected_extensions"],
        "topes": int(result.tope_count),
        "valid_extensions": int(result.valid_count),
        "bad_extensions": int(result.bad_count),
        "minimum_escape": int(result.minimum_escape),
        "minimum_escape_count": int(result.minimum_escape_count),
        "minimum_overlap": int(result.minimum_overlap),
        "overlap_left": int(result.overlap_left),
        "overlap_right": int(result.overlap_right),
        "overlap_left_size": int(result.overlap_left_size),
        "overlap_right_size": int(result.overlap_right_size),
        "pairwise_intersection": not bool(result.disjoint_found),
        "disjoint_left": int(result.disjoint_left),
        "disjoint_right": int(result.disjoint_right),
        "record_digest": bytes(result.record_digest).hex(),
    }
    if task["catalog_index"] == 16:
        expected = (66_636, 40_524, 52, 2, 8, EXPECTED_PARENT16_RECORD_DIGEST)
        actual = (
            report["valid_extensions"],
            report["bad_extensions"],
            report["minimum_escape"],
            report["minimum_escape_count"],
            report["minimum_overlap"],
            report["record_digest"],
        )
        if actual != expected:
            raise AssertionError(
                "compiled finite kernel disagrees with the independent "
                "pure-Python parent-16 audit"
            )
    validate_result_record(
        report, task, context=f"parent {task['catalog_index']} result"
    )
    return report


def update_unsigned(digest, value):
    digest.update(int(value).to_bytes(16, "little", signed=False))


def legacy_aggregate_digest(results):
    digest = hashlib.sha256()
    digest.update(LEGACY_FORMAT.encode("ascii") + b"\0")
    numeric_fields = (
        "catalog_index",
        "topes",
        "valid_extensions",
        "bad_extensions",
        "minimum_escape",
        "minimum_escape_count",
        "minimum_overlap",
        "overlap_left",
        "overlap_right",
        "overlap_left_size",
        "overlap_right_size",
        "pairwise_intersection",
        "disjoint_left",
        "disjoint_right",
    )
    for record in sorted(results, key=lambda item: item["catalog_index"]):
        digest.update(record["chi"].encode("ascii") + b"\0")
        for field in numeric_fields:
            update_unsigned(digest, record[field])
        digest.update(bytes.fromhex(record["record_digest"]))
    return digest.hexdigest()


def aggregate_digest(results):
    digest = hashlib.sha256()
    digest.update(FORMAT.encode("ascii") + b"\0")
    numeric_fields = (
        "catalog_index",
        "expected_extensions",
        "topes",
        "valid_extensions",
        "bad_extensions",
        "minimum_escape",
        "minimum_escape_count",
        "minimum_overlap",
        "overlap_left",
        "overlap_right",
        "overlap_left_size",
        "overlap_right_size",
        "pairwise_intersection",
        "disjoint_left",
        "disjoint_right",
    )
    for record in sorted(results, key=lambda item: item["catalog_index"]):
        digest.update(record["chi"].encode("ascii") + b"\0")
        digest.update(bytes.fromhex(record["matrix_digest"]))
        for field in numeric_fields:
            update_unsigned(digest, record[field])
        digest.update(bytes.fromhex(record["record_digest"]))
    return digest.hexdigest()


def summary_payload(results, selected_indices, complete):
    selected_indices = tuple(selected_indices)
    if selected_indices != tuple(sorted(set(selected_indices))):
        raise AssertionError("selected parent indices are not sorted and unique")
    results = sorted(results, key=lambda item: item["catalog_index"])
    result_indices = [record["catalog_index"] for record in results]
    if len(set(result_indices)) != len(result_indices) or not set(
        result_indices
    ) <= set(selected_indices):
        raise AssertionError("result records do not match the selected parent scope")
    actual_complete = len(results) == len(selected_indices)
    if bool(complete) != actual_complete:
        raise AssertionError("summary completeness flag disagrees with result count")
    return {
        "format": FORMAT,
        "catalog_classes": EXPECTED_CATALOG,
        "realizable_parents": EXPECTED_REALIZABLE,
        "selected_parents": len(selected_indices),
        "selected_indices": list(selected_indices),
        "tested_parents": len(results),
        "complete": actual_complete,
        "all_pairwise_intersecting": bool(results)
        and all(record["pairwise_intersection"] for record in results),
        "aggregate_digest": aggregate_digest(results),
        "global_minimum_escape": min(
            (record["minimum_escape"] for record in results), default=None
        ),
        "global_minimum_overlap": min(
            (record["minimum_overlap"] for record in results), default=None
        ),
        "results": results,
    }


def write_payload(path, results, selected_indices, complete):
    payload = summary_payload(results, selected_indices, complete)
    temporary = path.with_name(path.name + ".tmp")
    temporary.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    temporary.replace(path)


def validate_payload(
    payload,
    selected_indices,
    by_index,
    *,
    require_complete=False,
    context="summary",
):
    selected_indices = tuple(selected_indices)
    if selected_indices != tuple(sorted(set(selected_indices))):
        raise AssertionError(f"{context}: selected scope is not sorted and unique")
    if type(payload) is not dict or set(payload) != SUMMARY_FIELDS:
        raise AssertionError(f"{context}: wrong summary schema")
    if payload["format"] != FORMAT:
        raise AssertionError(f"{context}: wrong summary format")
    for field in (
        "catalog_classes",
        "realizable_parents",
        "selected_parents",
        "tested_parents",
    ):
        if type(payload[field]) is not int:
            raise AssertionError(f"{context}: {field} is not an integer")
    for field in ("complete", "all_pairwise_intersecting"):
        if type(payload[field]) is not bool:
            raise AssertionError(f"{context}: {field} is not Boolean")
    if type(payload["selected_indices"]) is not list or payload[
        "selected_indices"
    ] != list(selected_indices):
        raise AssertionError(f"{context}: selected parent scope changed")
    if (
        payload["catalog_classes"] != EXPECTED_CATALOG
        or payload["realizable_parents"] != EXPECTED_REALIZABLE
        or payload["selected_parents"] != len(selected_indices)
    ):
        raise AssertionError(f"{context}: wrong catalog or selected-parent count")
    results = payload["results"]
    if type(results) is not list or payload["tested_parents"] != len(results):
        raise AssertionError(f"{context}: tested-parent count is inconsistent")
    catalog_indices = []
    for record in results:
        if type(record) is not dict or type(record.get("catalog_index")) is not int:
            raise AssertionError(f"{context}: result has no integral catalog index")
        catalog_index = record["catalog_index"]
        if catalog_index not in by_index or catalog_index not in selected_indices:
            raise AssertionError(f"{context}: result contains a foreign parent")
        validate_result_record(
            record,
            by_index[catalog_index],
            context=f"{context} parent {catalog_index}",
        )
        catalog_indices.append(catalog_index)
    if catalog_indices != sorted(set(catalog_indices)):
        raise AssertionError(f"{context}: results are duplicated or out of order")
    complete = len(results) == len(selected_indices)
    if payload["complete"] != complete or (require_complete and not complete):
        raise AssertionError(f"{context}: completeness flag or result count is wrong")
    if not is_hex_digest(payload["aggregate_digest"]):
        raise AssertionError(f"{context}: aggregate digest is not a lowercase SHA-256")
    digest = aggregate_digest(results)
    if payload["aggregate_digest"] != digest:
        raise AssertionError(f"{context}: aggregate digest is inconsistent")
    all_pairwise = bool(results) and all(
        record["pairwise_intersection"] for record in results
    )
    if payload["all_pairwise_intersecting"] != all_pairwise:
        raise AssertionError(
            f"{context}: pairwise-intersection verdict is inconsistent"
        )
    minimum_escape = min(
        (record["minimum_escape"] for record in results), default=None
    )
    minimum_overlap = min(
        (record["minimum_overlap"] for record in results), default=None
    )
    if payload["global_minimum_escape"] != minimum_escape:
        raise AssertionError(f"{context}: global minimum escape is inconsistent")
    if payload["global_minimum_overlap"] != minimum_overlap:
        raise AssertionError(f"{context}: global minimum overlap is inconsistent")
    return results


def verify_summary(by_index, path=SUMMARY):
    payload = json.loads(path.read_text(encoding="utf-8"))
    selected_indices = tuple(sorted(by_index))
    validate_payload(
        payload,
        selected_indices,
        by_index,
        require_complete=True,
        context="stored 2,604-parent summary",
    )
    digest = payload["aggregate_digest"]
    minimum_escape = payload["global_minimum_escape"]
    minimum_overlap = payload["global_minimum_overlap"]
    if EXPECTED_AGGREGATE_DIGEST is not None and digest != EXPECTED_AGGREGATE_DIGEST:
        raise AssertionError("stored 2,604-parent aggregate digest changed")
    if (
        EXPECTED_GLOBAL_MINIMUM_ESCAPE is not None
        and minimum_escape != EXPECTED_GLOBAL_MINIMUM_ESCAPE
    ):
        raise AssertionError("stored global minimum escape changed")
    if (
        EXPECTED_GLOBAL_MINIMUM_OVERLAP is not None
        and minimum_overlap != EXPECTED_GLOBAL_MINIMUM_OVERLAP
    ):
        raise AssertionError("stored global minimum overlap changed")
    return payload


def validate_legacy_full_payload(payload, by_index):
    context = "legacy 2,604-parent summary"
    if type(payload) is not dict or set(payload) != LEGACY_SUMMARY_FIELDS:
        raise AssertionError(f"{context}: wrong summary schema")
    if payload["format"] != LEGACY_FORMAT:
        raise AssertionError(f"{context}: wrong summary format")
    for field in (
        "catalog_classes",
        "realizable_parents",
        "selected_parents",
        "tested_parents",
    ):
        if type(payload[field]) is not int:
            raise AssertionError(f"{context}: {field} is not an integer")
    if type(payload["complete"]) is not bool or type(
        payload["all_pairwise_intersecting"]
    ) is not bool:
        raise AssertionError(f"{context}: verdict fields are not Boolean")
    selected_indices = tuple(sorted(by_index))
    results = payload["results"]
    if (
        payload["catalog_classes"] != EXPECTED_CATALOG
        or payload["realizable_parents"] != EXPECTED_REALIZABLE
        or payload["selected_parents"] != EXPECTED_REALIZABLE
        or payload["tested_parents"] != EXPECTED_REALIZABLE
        or type(results) is not list
        or len(results) != EXPECTED_REALIZABLE
        or payload["complete"] is not True
    ):
        raise AssertionError(f"{context}: summary is not a complete full sweep")
    enriched = []
    catalog_indices = []
    for record in results:
        if type(record) is not dict or set(record) != LEGACY_RESULT_FIELDS:
            raise AssertionError(f"{context}: wrong legacy result-record schema")
        if type(record.get("catalog_index")) is not int:
            raise AssertionError(f"{context}: result has no integral catalog index")
        catalog_index = record["catalog_index"]
        if catalog_index not in by_index:
            raise AssertionError(f"{context}: result contains a foreign parent")
        upgraded = dict(record)
        upgraded["matrix_digest"] = by_index[catalog_index]["matrix_digest"]
        upgraded["expected_extensions"] = by_index[catalog_index][
            "expected_extensions"
        ]
        validate_result_record(
            upgraded,
            by_index[catalog_index],
            context=f"{context} parent {catalog_index}",
        )
        enriched.append(upgraded)
        catalog_indices.append(catalog_index)
    if catalog_indices != list(selected_indices):
        raise AssertionError(f"{context}: catalog index/chi coverage is not exact")
    if not is_hex_digest(payload["aggregate_digest"]) or payload[
        "aggregate_digest"
    ] != legacy_aggregate_digest(results):
        raise AssertionError(f"{context}: aggregate digest is inconsistent")
    all_pairwise = all(record["pairwise_intersection"] for record in results)
    minimum_escape = min(record["minimum_escape"] for record in results)
    minimum_overlap = min(record["minimum_overlap"] for record in results)
    if (
        payload["all_pairwise_intersecting"] != all_pairwise
        or payload["global_minimum_escape"] != minimum_escape
        or payload["global_minimum_overlap"] != minimum_overlap
    ):
        raise AssertionError(f"{context}: stored aggregate fields are inconsistent")
    return enriched


def upgrade_legacy_summary(by_index):
    payload = json.loads(SUMMARY.read_text(encoding="utf-8"))
    if payload.get("format") == FORMAT:
        raise ValueError("canonical summary is already in the v2 format")
    old_digest = payload.get("aggregate_digest")
    results = validate_legacy_full_payload(payload, by_index)
    selected_indices = tuple(sorted(by_index))
    candidate = summary_payload(results, selected_indices, complete=True)
    validate_payload(
        candidate,
        selected_indices,
        by_index,
        require_complete=True,
        context="candidate upgraded summary",
    )
    write_payload(SUMMARY, results, selected_indices, complete=True)
    upgraded = verify_summary(by_index)
    print("UPGRADED", SUMMARY)
    print("LEGACY_AGGREGATE_DIGEST", old_digest)
    print("AGGREGATE_DIGEST", upgraded["aggregate_digest"])


def parse_indices(text):
    return tuple(sorted({int(value) for value in text.split(",") if value.strip()}))


def parse_args():
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--full", action="store_true", help="replay all 2,604 parents")
    group.add_argument(
        "--indices",
        type=parse_indices,
        help="comma-separated catalog-parent indices for an exact scoped replay",
    )
    group.add_argument(
        "--upgrade-summary",
        action="store_true",
        help="atomically upgrade the complete canonical v1 summary to strict v2",
    )
    parser.add_argument(
        "--workers",
        type=int,
        default=min(8, os.cpu_count() or 1),
        help="parallel exact-tope workers (default: min(8, CPU count))",
    )
    parser.add_argument(
        "--analysis-output",
        type=Path,
        help="write an atomic JSON result/checkpoint every 25 completed parents",
    )
    parser.add_argument(
        "--resume",
        action="store_true",
        help="resume selected parents from an existing --analysis-output checkpoint",
    )
    parser.add_argument(
        "--require-compiled-replay",
        action="store_true",
        help="fail instead of using the validated stored-summary fallback",
    )
    return parser.parse_args()


def main():
    args = parse_args()
    records = load_catalog_records()
    by_index = {record["catalog_index"]: record for record in records}

    if args.upgrade_summary:
        if (
            args.resume
            or args.analysis_output is not None
            or args.require_compiled_replay
        ):
            raise ValueError(
                "--upgrade-summary cannot be combined with --resume, "
                "--analysis-output, or --require-compiled-replay"
            )
        upgrade_legacy_summary(by_index)
        return
    verify_kernel_source()
    if (
        not args.full
        and args.analysis_output is not None
        and args.analysis_output.resolve() == SUMMARY.resolve()
    ):
        raise ValueError(
            "only --full may write the canonical 2,604-parent summary; "
            "choose another --analysis-output for a scoped replay"
        )

    if not args.full and args.indices is None:
        stored = verify_summary(by_index)
        selected_indices = SENTINELS
        print(
            "PASS stored complete 2,604-parent summary",
            stored["aggregate_digest"],
            flush=True,
        )
    elif args.full:
        selected_indices = tuple(sorted(by_index))
    else:
        selected_indices = args.indices
    missing = sorted(set(selected_indices) - set(by_index))
    if missing:
        raise ValueError(f"selected catalog indices are not realizable parents: {missing}")
    selected = [by_index[index] for index in selected_indices]
    if not selected:
        raise ValueError("no parents selected")
    if args.workers < 1:
        raise ValueError("--workers must be positive")
    if args.resume and (args.analysis_output is None or not args.analysis_output.exists()):
        raise ValueError("--resume requires an existing --analysis-output")

    try:
        compilers, explicit_compiler = compiler_candidates()
    except RuntimeError as error:
        raise SystemExit(f"ERROR: {error}") from error
    default_stored_mode = (
        not args.full
        and args.indices is None
        and args.analysis_output is None
        and not args.resume
    )
    native_required = args.require_compiled_replay or not default_stored_mode
    if not compilers:
        if native_required:
            raise SystemExit(
                "ERROR: compiled replay requires CXX, g++, or clang++ with "
                "C++17 and OpenSSL libcrypto support"
            )
        print_stored_fallback("no supported C++17 compiler")
        return

    results = []
    if args.resume:
        checkpoint = json.loads(args.analysis_output.read_text(encoding="utf-8"))
        results = validate_payload(
            checkpoint,
            selected_indices,
            by_index,
            context="resume checkpoint",
        )
        completed = {record["catalog_index"] for record in results}
        selected = [
            record for record in selected if record["catalog_index"] not in completed
        ]
        print("RESUME", len(results), "completed;", len(selected), "remaining")

    if selected:
        with tempfile.TemporaryDirectory(prefix="diag2-common-shear-") as build:
            library = None
            native_failures = []
            for candidate_index, compiler in enumerate(compilers):
                if os.name == "nt":
                    library_name = f"diag2_common_shear_fast-{candidate_index}.dll"
                elif sys.platform == "darwin":
                    library_name = (
                        f"libdiag2_common_shear_fast-{candidate_index}.dylib"
                    )
                else:
                    library_name = f"libdiag2_common_shear_fast-{candidate_index}.so"
                candidate_library = Path(build) / library_name
                try:
                    compile_helper(candidate_library, compiler)
                    preflight_library(candidate_library)
                except NativeToolchainUnavailable as error:
                    native_failures.append((compiler, error))
                    if explicit_compiler:
                        raise SystemExit(
                            "ERROR: explicit CXX cannot build/load the compiled "
                            f"replay:\n{error}"
                        ) from error
                    continue
                library = candidate_library
                break
            if library is None:
                failures = native_failure_report(native_failures)
                if native_required:
                    raise SystemExit(
                        "ERROR: no auto-discovered compiler can build/load the "
                        f"compiled replay:\n{failures}"
                    )
                print_stored_fallback(
                    "auto-discovered C++ toolchains could not build/load the "
                    "pinned kernel"
                )
                return
            with ProcessPoolExecutor(
                max_workers=args.workers,
                initializer=initialize_worker,
                initargs=(str(library),),
            ) as executor:
                futures = {
                    executor.submit(audit_parent, record): record["catalog_index"]
                    for record in selected
                }
                for future in as_completed(futures):
                    result = future.result()
                    results.append(result)
                    print(
                        "PASS parent",
                        result["catalog_index"],
                        "topes",
                        result["topes"],
                        "extensions",
                        result["valid_extensions"],
                        "bad",
                        result["bad_extensions"],
                        "min-escape",
                        result["minimum_escape"],
                        "min-overlap",
                        result["minimum_overlap"],
                        "pairwise" if result["pairwise_intersection"] else "DISJOINT",
                        flush=True,
                    )
                    if (
                        args.analysis_output is not None
                        and (
                            len(results) % 25 == 0
                            or len(results) == len(selected_indices)
                        )
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
    print("GLOBAL_MINIMUM_ESCAPE", payload["global_minimum_escape"])
    print("GLOBAL_MINIMUM_OVERLAP", payload["global_minimum_overlap"])
    if not payload["all_pairwise_intersecting"]:
        raise AssertionError("an exact parent representative has disjoint escape sets")

    if not args.full and args.indices is None:
        stored_by_index = {
            record["catalog_index"]: record for record in stored["results"]
        }
        for result in results:
            if result != stored_by_index[result["catalog_index"]]:
                raise AssertionError(
                    f"sentinel parent {result['catalog_index']} disagrees with summary"
                )
        print("PASS exact sentinel parents reproduce their committed full-sweep records")
    elif args.full:
        if len(results) != EXPECTED_REALIZABLE:
            raise AssertionError("full replay did not test 2,604 parents")
        print(
            "THEOREM AUDIT all 2,604 exact catalog representatives have "
            "pairwise-intersecting moving-witness escape sets"
        )
        print(
            "SCOPE one exact chart per parent; no residual-chamber coverage or "
            "diagonal-two promotion"
        )


if __name__ == "__main__":
    main()
