#!/usr/bin/env python3
"""Exact residual-factor sign states on all 178 stored row-2599 charts.

One labeled determinant representative is chosen for each of the 26,740
localized factor classes.  Parent-bracket units have fixed nonzero signs in
one parent cell, so these raw signs differ from primitive factor signs only by
a fixed coordinate reorientation.  Integer derived-normal determinants give
the complete 178 by 26,740 sign matrix without numerical evaluation.

This is a proof-safe sample lower bound, not geometric roadmap coverage.
"""

from __future__ import annotations

import argparse
import hashlib
from collections import Counter
from pathlib import Path

import numpy as np

import DIAG9_GRAPH_exact_topes as topes
import DIAG9_GRAPH_verify_row2599_slice as slice_verify


HERE = Path(__file__).resolve().parent
GLOBAL = HERE / "data" / "DIAG9_GRAPH_global_factor_census.npz"
CHARTS = HERE / "data" / "seeat_parent2599_upper178.npz"
CERTIFICATE = HERE / "data" / "DIAG9_GRAPH_row2599_factor_states.npz"
FORMAT = "diag9-row2599-factor-state-sample-v1"
EXPECTED_DIGEST = "ab4aeed6eab31d6f4bfa68894b52e8086910076a25d7c7416c806f0529df8f0b"


def representative_occurrences(occurrence_factor, factor_count):
    answer = [-1] * factor_count
    for occurrence, factor in enumerate(map(int, occurrence_factor)):
        if answer[factor] < 0:
            answer[factor] = occurrence
    if any(value < 0 for value in answer):
        raise AssertionError("a global factor has no labeled representative")
    return tuple(answer)


def exact_sign_matrix(progress=True):
    with np.load(GLOBAL, allow_pickle=False) as source:
        if str(source["format"].item()) != "diag9-global-residual-factor-census-v1":
            raise AssertionError("wrong global factor certificate format")
        foursets = tuple(
            tuple(map(int, row)) for row in source["occurrence_fourset"]
        )
        occurrence_factor = np.asarray(source["occurrence_factor"], dtype=np.uint32)
        factor_count = len(source["factor_multiplicity"])
    representatives = representative_occurrences(occurrence_factor, factor_count)
    representative_foursets = tuple(foursets[index] for index in representatives)

    with np.load(CHARTS, allow_pickle=False) as source:
        if int(source["parent_index"].item()) != 2599:
            raise AssertionError("wrong chart-bank parent")
        charts = np.asarray(source["chart_matrix"], dtype=np.int64)
    if charts.shape != (178, 4, 8) or factor_count != 26_740:
        raise AssertionError("wrong chart/factor dimensions")

    expected_parent = topes.parent_signs(charts[0])
    signs = np.empty((len(charts), factor_count), dtype=np.bool_)
    for chart_index, chart in enumerate(charts):
        if topes.parent_signs(chart) != expected_parent:
            raise AssertionError("stored chart leaves parent 2599")
        normals = topes.derived_rows(chart)
        for factor, fourset in enumerate(representative_foursets):
            value = slice_verify.det4(tuple(normals[index] for index in fourset))
            if not value:
                raise AssertionError("stored generic chart lies on a residual wall")
            signs[chart_index, factor] = value > 0
        if progress and (chart_index + 1) % 20 == 0:
            print(f"evaluated {chart_index + 1}/178 exact charts", flush=True)

    chart_packed = np.packbits(signs, axis=1, bitorder="little")
    if len({bytes(row) for row in chart_packed}) != 178:
        raise AssertionError("two stored charts have the same residual factor state")

    trace_packed = np.packbits(signs, axis=0, bitorder="little").T.copy()
    trace_keys = tuple(bytes(row) for row in trace_packed)
    unique_trace_keys = tuple(sorted(set(trace_keys)))
    trace_index = {key: index for index, key in enumerate(unique_trace_keys)}
    factor_trace = np.asarray(
        [trace_index[key] for key in trace_keys], dtype=np.uint16
    )
    trace_multiplicity_counter = Counter(map(int, factor_trace))
    trace_multiplicity = np.asarray(
        [trace_multiplicity_counter[index] for index in range(len(unique_trace_keys))],
        dtype=np.uint16,
    )
    unique_trace_packed = np.asarray(
        [np.frombuffer(key, dtype=np.uint8) for key in unique_trace_keys],
        dtype=np.uint8,
    )

    varied = np.asarray(
        [
            factor
            for factor in range(factor_count)
            if np.any(signs[:, factor] != signs[0, factor])
        ],
        dtype=np.uint16,
    )
    if len(varied) != 10_844:
        raise AssertionError("wrong number of two-sided sampled factors")
    varied_trace_count = len({trace_keys[int(factor)] for factor in varied})
    if varied_trace_count != 10_787:
        raise AssertionError("wrong number of distinct varying-factor traces")
    if len(unique_trace_keys) != 10_789:
        raise AssertionError("wrong number of all sampled factor traces")

    hamming = np.zeros((len(charts), len(charts)), dtype=np.uint16)
    for left in range(len(charts)):
        hamming[left, left + 1 :] = np.count_nonzero(
            signs[left + 1 :] != signs[left], axis=1
        )
    hamming += hamming.T

    return {
        "format": np.asarray(FORMAT),
        "parent_index": np.asarray(2599, dtype=np.uint16),
        "chart_index": np.arange(178, dtype=np.uint16),
        "representative_occurrence_index": np.asarray(
            representatives, dtype=np.uint32
        ),
        "representative_fourset": np.asarray(
            representative_foursets, dtype=np.uint8
        ),
        "chart_factor_sign_packed": chart_packed,
        "factor_trace": factor_trace,
        "unique_trace_packed": unique_trace_packed,
        "trace_multiplicity": trace_multiplicity,
        "varied_factor": varied,
        "chart_hamming": hamming,
    }


def semantic_digest(payload):
    digest = hashlib.sha256()
    for name in sorted(payload):
        array = np.asarray(payload[name])
        digest.update(name.encode("ascii"))
        digest.update(str(array.dtype).encode("ascii"))
        digest.update(repr(array.shape).encode("ascii"))
        digest.update(array.tobytes())
    return digest.hexdigest()


def compare_payload(left, right):
    if set(left) != set(right):
        raise AssertionError("sample certificate field set changed")
    for name in sorted(left):
        if not np.array_equal(np.asarray(left[name]), np.asarray(right[name])):
            raise AssertionError(f"sample certificate mismatch: {name}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--build", action="store_true")
    args = parser.parse_args()

    replay = exact_sign_matrix(progress=True)
    digest = semantic_digest(replay)
    if EXPECTED_DIGEST is not None and digest != EXPECTED_DIGEST:
        raise AssertionError("row-2599 sample semantic digest changed")
    if args.build:
        CERTIFICATE.parent.mkdir(parents=True, exist_ok=True)
        np.savez_compressed(CERTIFICATE, **replay)
        print("WROTE", CERTIFICATE)
    else:
        with np.load(CERTIFICATE, allow_pickle=False) as source:
            stored = {name: source[name] for name in source.files}
        compare_payload(stored, replay)

    hamming = replay["chart_hamming"]
    upper = hamming[np.triu_indices(len(hamming), 1)]
    print("PASS: 178 exact charts have 178 distinct residual factor states")
    print("PASS: 10844 varying factors have 10787 distinct nonconstant traces")
    print("PASS: including both constant traces gives 10789 trace classes")
    print(
        "PASS: exact pairwise factor-sign Hamming range",
        int(upper.min()), int(upper.max()),
    )
    print("SEMANTIC SHA256:", digest)
    print("THEOREM: parent 2599 contains at least 178 residual sign chambers")
    print("SCOPE: exact point-sample lower bound, not roadmap coverage or adjacency")


if __name__ == "__main__":
    main()
