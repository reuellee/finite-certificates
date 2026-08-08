#!/usr/bin/env python3
"""Exhaust the elementary-shear escape-set test on all 178 stored charts.

This is a quantitative strengthening of ``verify_diag2_escape_set_topes.py``.
For every exact chart in the row-2599 source bank it enumerates all complete
topes of the 56-row derived arrangement, all abstract extensions of the
parent, and the 112-direction moving-witness escape mask of every extension
which is bad at that chart.  It then proves that every two distinct bad
signatures have a common escape direction and records the minimum overlap.

The 178 matrices are exact point samples, not a certified chamber atlas.
Consequently this checker is a finite theorem about the stored bank and not
a proof of diagonal two or of coverage of the parent realization space.
"""

from __future__ import annotations

import argparse
from collections import Counter
from concurrent.futures import ProcessPoolExecutor, as_completed
import hashlib
import json
from pathlib import Path

import numpy as np

import DIAG9_GRAPH_exact_topes as exact_topes
import four_chart_gate as gate
import verify_diag2_escape_set_topes as escape


EXPECTED_CHARTS = 178
EXPECTED_VALID = 97_224
EXPECTED_BAD = 71_112
EXPECTED_TOPES = 26_112

# Filled after the first complete exact replay.  Keeping the pins here makes
# later CI/stress runs detect changes in any of the 12,657,936 escape masks.
EXPECTED_ATLAS_DIGEST = (
    "d255845e6b246865ed3c50a61c001ec8701d3b22fffd218087d955ac0854d111"
)
EXPECTED_GLOBAL_MINIMUM_ESCAPE = 53
EXPECTED_GLOBAL_MINIMUM_OVERLAP = 6
SUMMARY = escape.HERE / "data" / "DIAG2_ESCAPE_SET_atlas178_summary.json"

SIGNATURES: tuple[int, ...] = ()
PARENT_SIGNS: tuple[int, ...] = ()
MATRICES: np.ndarray | None = None


def minimum_pair_overlap(records):
    """Return the exact minimum |E(rho) intersect E(eta)| for rho != eta.

    Sorting by set size gives a rigorous branch-and-bound: two subsets of a
    112-element universe intersect in at least ``left_size+right_size-112``.
    Once this lower bound reaches the incumbent, all later (larger) partners
    can be skipped.
    """
    ordered = sorted(
        ((mask.bit_count(), int(signature), int(mask)) for signature, mask in records)
    )
    best = 113
    witness = None
    for left_index, (left_size, left_signature, left_mask) in enumerate(ordered):
        if 2 * left_size - 112 >= best:
            break
        for right_size, right_signature, right_mask in ordered[left_index + 1 :]:
            if left_size + right_size - 112 >= best:
                break
            overlap = (left_mask & right_mask).bit_count()
            if overlap < best:
                best = overlap
                witness = (
                    left_signature,
                    right_signature,
                    left_size,
                    right_size,
                )
                if best == 0:
                    return best, witness
    if witness is None:
        raise AssertionError("fewer than two bad signatures")
    return best, witness


def audit_chart(chart_index):
    if MATRICES is None:
        raise AssertionError("chart bank was not initialized")
    matrix = MATRICES[chart_index]
    if exact_topes.parent_signs(matrix) != PARENT_SIGNS:
        raise AssertionError(f"chart {chart_index}: wrong parent chirotope")

    rows = exact_topes.derived_rows(matrix)
    enumerated = exact_topes.enumerate_topes(rows, dimension=4)
    exact_topes.verify_topes(rows, enumerated)
    topes = tuple(enumerated)
    if len(topes) != EXPECTED_TOPES:
        raise AssertionError(f"chart {chart_index}: wrong tope count")

    prepared = escape.prepare_directions(topes)
    tope_set = set(topes)
    records = [
        (signature, escape.escape_mask(signature, prepared))
        for signature in SIGNATURES
        if signature not in tope_set
    ]
    if len(records) != EXPECTED_BAD:
        raise AssertionError(f"chart {chart_index}: wrong bad-signature count")

    disjoint = escape.prove_pairwise_intersection(records)
    if disjoint is not None:
        raise AssertionError(
            f"chart {chart_index}: disjoint escape masks for {disjoint}"
        )
    minimum_escape = min(mask.bit_count() for _, mask in records)
    minimum_escape_count = sum(
        mask.bit_count() == minimum_escape for _, mask in records
    )
    minimum_overlap, witness = minimum_pair_overlap(records)
    if minimum_overlap <= 0:
        raise AssertionError(f"chart {chart_index}: zero common escape directions")

    label = f"row2599-chart-{chart_index}"
    return {
        "chart": chart_index,
        "topes": len(topes),
        "valid": len(SIGNATURES),
        "bad": len(records),
        "minimum_escape": minimum_escape,
        "minimum_escape_count": minimum_escape_count,
        "minimum_overlap": minimum_overlap,
        "overlap_left": witness[0],
        "overlap_right": witness[1],
        "overlap_left_size": witness[2],
        "overlap_right_size": witness[3],
        "escape_digest": escape.semantic_digest(label, records),
    }


def atlas_digest(results):
    digest = hashlib.sha256()
    digest.update(b"diag2-escape-set-atlas178-v1\0")
    for result in sorted(results, key=lambda record: record["chart"]):
        for key in (
            "chart",
            "topes",
            "valid",
            "bad",
            "minimum_escape",
            "minimum_escape_count",
            "minimum_overlap",
            "overlap_left",
            "overlap_right",
            "overlap_left_size",
            "overlap_right_size",
        ):
            digest.update(int(result[key]).to_bytes(16, "little", signed=False))
        digest.update(bytes.fromhex(result["escape_digest"]))
    return digest.hexdigest()


def verify_stored_summary():
    """Check the optional compact result table without replaying the masks."""
    if not SUMMARY.exists():
        return
    payload = json.loads(SUMMARY.read_text(encoding="utf-8"))
    if set(payload) != {
        "format",
        "charts",
        "atlas_digest",
        "global_minimum_escape",
        "global_minimum_overlap",
        "results",
    }:
        raise AssertionError("stored 178-chart summary fields changed")
    results = payload["results"]
    if payload["format"] != "diag2-escape-set-atlas178-v1":
        raise AssertionError("stored 178-chart summary format changed")
    if payload["charts"] != EXPECTED_CHARTS or len(results) != EXPECTED_CHARTS:
        raise AssertionError("stored 178-chart summary count changed")
    digest = atlas_digest(results)
    if payload["atlas_digest"] != digest or digest != EXPECTED_ATLAS_DIGEST:
        raise AssertionError("stored 178-chart summary digest changed")
    if payload["global_minimum_escape"] != EXPECTED_GLOBAL_MINIMUM_ESCAPE:
        raise AssertionError("stored summary minimum escape changed")
    if payload["global_minimum_overlap"] != EXPECTED_GLOBAL_MINIMUM_OVERLAP:
        raise AssertionError("stored summary minimum overlap changed")
    if min(record["minimum_escape"] for record in results) != EXPECTED_GLOBAL_MINIMUM_ESCAPE:
        raise AssertionError("stored per-chart escape minima disagree")
    if min(record["minimum_overlap"] for record in results) != EXPECTED_GLOBAL_MINIMUM_OVERLAP:
        raise AssertionError("stored per-chart overlap minima disagree")


def parse_args():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--workers", type=int, default=8)
    parser.add_argument(
        "--limit",
        type=int,
        default=EXPECTED_CHARTS,
        help="debug prefix only; digest pins apply only to the full 178-chart run",
    )
    parser.add_argument(
        "--analysis-output",
        type=Path,
        help="optional deterministic JSON summary for the audited chart prefix",
    )
    return parser.parse_args()


def main():
    global SIGNATURES, PARENT_SIGNS, MATRICES
    args = parse_args()
    if not 1 <= args.limit <= EXPECTED_CHARTS:
        raise ValueError("--limit must lie in 1..178")
    verify_stored_summary()

    parents = [line.strip() for line in gate.CATALOG_48.open() if line.strip()]
    parent = parents[gate.PARENT_INDEX]
    parent_bits, signatures = gate.enumerate_extensions(parent)
    SIGNATURES = tuple(int(signature) for signature in signatures)
    PARENT_SIGNS = tuple(1 if bit else -1 for bit in parent_bits)
    if len(SIGNATURES) != EXPECTED_VALID:
        raise AssertionError("row-2599 extension count changed")

    with np.load(escape.HERE / "data" / "seeat_parent2599_upper178.npz") as atlas:
        MATRICES = np.asarray(atlas["chart_matrix"], dtype=np.int64)
    if MATRICES.shape != (EXPECTED_CHARTS, 4, 8):
        raise AssertionError("wrong 178-chart bank shape")

    results = []
    with ProcessPoolExecutor(max_workers=args.workers) as executor:
        futures = {
            executor.submit(audit_chart, chart): chart for chart in range(args.limit)
        }
        for future in as_completed(futures):
            result = future.result()
            results.append(result)
            print(
                "PASS chart",
                result["chart"],
                "min-escape",
                result["minimum_escape"],
                "min-overlap",
                result["minimum_overlap"],
                flush=True,
            )

    results.sort(key=lambda record: record["chart"])
    digest = atlas_digest(results)
    global_minimum_escape = min(record["minimum_escape"] for record in results)
    global_minimum_overlap = min(record["minimum_overlap"] for record in results)
    print("ATLAS_DIGEST", digest)
    print("GLOBAL_MINIMUM_ESCAPE", global_minimum_escape)
    print("GLOBAL_MINIMUM_OVERLAP", global_minimum_overlap)
    print(
        "MINIMUM_ESCAPE_HISTOGRAM",
        dict(sorted(Counter(record["minimum_escape"] for record in results).items())),
    )
    print(
        "MINIMUM_OVERLAP_HISTOGRAM",
        dict(sorted(Counter(record["minimum_overlap"] for record in results).items())),
    )

    if args.analysis_output is not None:
        payload = {
            "format": "diag2-escape-set-atlas178-v1",
            "charts": len(results),
            "atlas_digest": digest,
            "global_minimum_escape": global_minimum_escape,
            "global_minimum_overlap": global_minimum_overlap,
            "results": results,
        }
        args.analysis_output.write_text(
            json.dumps(payload, sort_keys=True, indent=2) + "\n",
            encoding="utf-8",
        )
        print("WROTE", args.analysis_output)

    if args.limit == EXPECTED_CHARTS:
        if EXPECTED_ATLAS_DIGEST is not None and digest != EXPECTED_ATLAS_DIGEST:
            raise AssertionError(f"atlas digest changed: {digest}")
        if (
            EXPECTED_GLOBAL_MINIMUM_ESCAPE is not None
            and global_minimum_escape != EXPECTED_GLOBAL_MINIMUM_ESCAPE
        ):
            raise AssertionError("global minimum escape size changed")
        if (
            EXPECTED_GLOBAL_MINIMUM_OVERLAP is not None
            and global_minimum_overlap != EXPECTED_GLOBAL_MINIMUM_OVERLAP
        ):
            raise AssertionError("global minimum overlap changed")
        print(
            "THEOREM AUDIT all 178 exact charts have pairwise-intersecting "
            "moving-witness escape sets"
        )
        print(
            "SCOPE stored exact point bank only; no chamber coverage or "
            "diagonal-two promotion"
        )


if __name__ == "__main__":
    main()
