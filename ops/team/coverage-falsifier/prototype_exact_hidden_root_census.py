#!/usr/bin/env python3
"""Exact red-team census for even-parity roots hidden from endpoint signs.

The 40-edge source cover is optimized from the 105-by-17,824 endpoint-sign
incidence matrix.  Endpoint equality does not in general imply that a
restricted polynomial is root free.  This program uses Sturm's theorem to
count *all distinct roots in (0,1)* for every endpoint-uncrossed candidate on
all 105 certified strict-parent segments.

This is a bounded falsification census.  A hit proves that the endpoint-sign
classification missed a strict-parent wall.  A null result says only that the
105 existing segments have no such hidden root; it cannot establish global
parent-cell or wall-component coverage.
"""

from __future__ import annotations

import argparse
from collections import Counter
from fractions import Fraction
from hashlib import sha256
import json
from multiprocessing import get_context
from pathlib import Path
import sys

import numpy as np


ROOT = Path(__file__).resolve().parents[3]
OMREAL = ROOT / "ai" / "omreal"
OUTPUT = Path(__file__).with_name("EXACT_HIDDEN_ROOT_CENSUS.json")
BASE_REVISION = "ec362dba8a912bc4749c004641aee2da0a88dc05"

sys.path.insert(0, str(OMREAL))
import DIAG2_PIVOT_LABELED_PAIR_ORBITS_VERIFY as labeled  # noqa: E402
import DIAG9_GRAPH_verify_row2599_slice as sturm  # noqa: E402
import diag3_pair_parent_source_transition_EDGE39_0_113_core as edge39  # noqa: E402
import verify_diag3_pair_fullsupport_safe_segment_walls as safe  # noqa: E402
import verify_diag3_pair_fullsupport_segment_cover as cover  # noqa: E402
import verify_diag3_pair_global_parent_face_gate as gate  # noqa: E402


PINNED = {
    OMREAL / "data" / "DIAG3_PAIR_FULLSUPPORT_SEGMENT_COVER.json":
        "19248dd148d1fd002931ed5f48197869dd42c68a513376e1a4d6941389bda307",
    OMREAL / "data" / "DIAG3_PAIR_FULLSUPPORT_LABELED_SKELETON_EDGE27_EDGE39.json":
        "dcb707220df3e61b1a94eeedcf8e46b6602f30d405f4a92fc542c0f52f672806",
    OMREAL / "data" / "DIAG3_PAIR_FULLSUPPORT_COMPONENT_COLLAR.json":
        "5930cc19019470fdfdf55d67523f6c4211ccf5b540f5c2bb5df36c64db75d7bd",
    OMREAL / "data" / "DIAG3_PAIR_PARENT_SOURCE_TRANSITION_EDGE39_0_113.json":
        "cb6eebc0df9bfeae8055c81471f09d594f8116e002caf11f62f9e865b0936dd7",
    OMREAL / "data" / "seeat_parent2599_upper178.npz":
        "3b90799d26b7783e92c2ac697eaaf8b76d26a787f53205873b997657e114180a",
    OMREAL / "data" / "DIAG9_GRAPH_row2599_factor_states.npz":
        "f44b1fccfb4e61273aeceb8796a18098d82c48473e257556ce3d2a22f99b0bcf",
    OMREAL / "data" / "DIAG3_PAIR_GLOBAL_row2599_candidate_factors.bin":
        "adb2e7257457f158e809450683c46fe7ecafdbdd4a7efdf9ac630e8a4f0fb03f",
    OMREAL / "verify_diag3_pair_fullsupport_safe_segment_walls.py":
        "ea45d9541543207447fa3a8f3066dbc7716da68e46a90447283f0007322a3d1f",
    OMREAL / "DIAG2_PIVOT_LABELED_PAIR_ORBITS_VERIFY.py":
        "8f51cf73ea75b4de7baf38af19b6e4cc941293edb82216a4aa00feef83c38e26",
}


POINTS = None
POLYNOMIALS = None
OPEN_IDS = None


def file_digest(path: Path) -> str:
    digest = sha256()
    with path.open("rb") as source:
        for block in iter(lambda: source.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def ids_digest(domain: bytes, identifiers) -> str:
    payload = ",".join(map(str, sorted(identifiers))).encode("ascii")
    return sha256(domain + b"\0" + payload).hexdigest()


def canonical_digest(value) -> str:
    return sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":")).encode("ascii")
    ).hexdigest()


def exact_root_count(polynomial) -> int:
    if not sturm.polynomial_value(polynomial, Fraction(0)):
        raise AssertionError("restricted factor vanishes at source endpoint 0")
    if not sturm.polynomial_value(polynomial, Fraction(1)):
        raise AssertionError("restricted factor vanishes at source endpoint 1")
    return sturm.root_count(polynomial, Fraction(0), Fraction(1))


def run_canaries():
    # Same positive endpoint signs, but two distinct interior roots.
    hidden = edge39.primitive_univariate((Fraction(3, 16), -1, 1))
    if exact_root_count(hidden) != 2:
        raise AssertionError("hidden-even-root positive canary failed")
    if (sturm.polynomial_value(hidden, Fraction(0)) > 0) != (
        sturm.polynomial_value(hidden, Fraction(1)) > 0
    ):
        raise AssertionError("hidden-even-root canary changed endpoint parity")
    if exact_root_count((1, 1)) != 0:
        raise AssertionError("null-root canary failed")
    rejected = []
    for polynomial in ((0, 1), (-1, 1)):
        try:
            exact_root_count(polynomial)
        except AssertionError:
            rejected.append(True)
    if len(rejected) != 2:
        raise AssertionError("endpoint-root hostile canary was accepted")
    try:
        edge39.primitive_univariate((0, 0))
    except AssertionError:
        zero_rejected = True
    else:
        zero_rejected = False
    if not zero_rejected:
        raise AssertionError("identically-zero hostile canary was accepted")
    return {
        "positive_hidden_even_root": "DETECTED_2_DISTINCT_ROOTS_WITH_EQUAL_ENDPOINT_SIGNS",
        "null_nonzero_affine": "DETECTED_0_ROOTS",
        "hostile_endpoint_roots": "REJECTED_BOTH_ENDPOINTS",
        "hostile_identically_zero_restriction": "REJECTED",
    }


def initialise():
    global POINTS, POLYNOMIALS, OPEN_IDS
    for path, expected in PINNED.items():
        actual = file_digest(path)
        if actual != expected:
            raise AssertionError(f"pinned input moved: {path}: {actual}")
    _matrices, POINTS, _states, _hamming, _occurrences = edge39.exact_inputs()
    candidates = tuple(gate.parse_candidates())
    _points_again, replay_candidates, incidence = cover.exact_inputs()
    if tuple(replay_candidates) != candidates:
        raise AssertionError("candidate order disagreement")
    known = incidence.any(axis=0)
    if (len(candidates), int(known.sum()), int((~known).sum())) != (17_824, 10_844, 6_980):
        raise AssertionError("endpoint incidence census changed")
    OPEN_IDS = tuple(candidates[index] for index in np.where(~known)[0])
    _types, _terms, POLYNOMIALS = labeled.factor_polynomials()


def edge_census(edge_index: int):
    left, right = safe.EDGES[edge_index]
    hits = []
    root_count_census = Counter()
    degree_census = Counter()
    for factor_id in OPEN_IDS:
        polynomial = edge39.primitive_univariate(
            safe.segment_power(POLYNOMIALS[factor_id], POINTS[left], POINTS[right])
        )
        degree_census[len(polynomial) - 1] += 1
        count = exact_root_count(polynomial)
        root_count_census[count] += 1
        if count:
            hits.append(
                {
                    "factor_id": int(factor_id),
                    "distinct_open_segment_roots": count,
                    "primitive_restriction": list(polynomial),
                }
            )
    return {
        "edge_index": edge_index,
        "charts": [int(left), int(right)],
        "endpoint_uncrossed_factors": len(OPEN_IDS),
        "root_count_census": {str(key): value for key, value in sorted(root_count_census.items())},
        "degree_census": {str(key): value for key, value in sorted(degree_census.items())},
        "hits": hits,
    }


def replay_edge39_endpoint_parity_obstruction(open_ids):
    record = json.loads(
        (OMREAL / "data" / "DIAG3_PAIR_PARENT_SOURCE_TRANSITION_EDGE39_0_113.json").read_text()
    )
    roots = Counter(
        member["factor_id"]
        for event in record["residual_roadmap"]["events"]
        for member in event["members"]
    )
    census = Counter(roots.values())
    hidden = sorted(factor_id for factor_id, count in roots.items() if count == 2)
    if census != Counter({1: 5_091, 2: 118}):
        raise AssertionError(f"edge-39 rooted-factor census changed: {census}")
    if len(record["residual_roadmap"]["events"]) != 5_327:
        raise AssertionError("edge-39 event census changed")
    if record["edge_interface"]["endpoint_factor_hamming_distance"] != 5_091:
        raise AssertionError("edge-39 endpoint Hamming distance changed")
    if set(hidden) & set(open_ids):
        raise AssertionError("edge-39 obstruction unexpectedly reached base-open residue")
    witness_factor = hidden[0]
    witness_polynomial = edge39.primitive_univariate(
        safe.segment_power(POLYNOMIALS[witness_factor], POINTS[0], POINTS[113])
    )
    witness_root_count = exact_root_count(witness_polynomial)
    witness_endpoints = [
        sturm.polynomial_value(witness_polynomial, Fraction(0)),
        sturm.polynomial_value(witness_polynomial, Fraction(1)),
    ]
    if witness_root_count != 2 or witness_endpoints[0] * witness_endpoints[1] <= 0:
        raise AssertionError("least edge-39 parity witness failed direct exact replay")
    return {
        "edge_index": 39,
        "charts": [0, 113],
        "rooted_factor_count": len(roots),
        "interior_distinct_root_count": sum(roots.values()),
        "endpoint_hamming_distance": 5_091,
        "equal_endpoint_sign_two_root_factor_count": len(hidden),
        "equal_endpoint_sign_two_root_factor_ids": hidden,
        "equal_endpoint_sign_two_root_ids_sha256": ids_digest(
            b"diag3-edge39-even-root-factor-ids-v1", hidden
        ),
        "intersection_with_6980_endpoint_uncrossed_residue": 0,
        "least_exact_witness": {
            "factor_id": witness_factor,
            "primitive_restriction_low_to_high": list(witness_polynomial),
            "endpoint_values": list(map(edge39.fraction_text, witness_endpoints)),
            "distinct_roots_in_open_segment_by_sturm": witness_root_count,
            "endpoint_signs_equal": True,
        },
        "consequence": "endpoint sign incidence does not determine roots even on one retained segment",
        "nonconsequence": "does not prove that any of the 118 factors has more than one global wall component",
    }


def build(workers: int, edge_indices, output: Path):
    initialise()
    canaries = run_canaries()
    context = get_context("fork")
    with context.Pool(processes=workers) as pool:
        rows = list(pool.imap_unordered(edge_census, edge_indices, chunksize=1))
    rows.sort(key=lambda row: row["edge_index"])
    hits = [
        {"edge_index": row["edge_index"], "charts": row["charts"], **hit}
        for row in rows
        for hit in row["hits"]
    ]
    total_pairs = sum(row["endpoint_uncrossed_factors"] for row in rows)
    if total_pairs != len(edge_indices) * 6_980:
        raise AssertionError("factor-segment pair accounting changed")
    selected = json.loads(
        (OMREAL / "data" / "DIAG3_PAIR_FULLSUPPORT_SEGMENT_COVER.json").read_text()
    )["source_bank"]["selected_edge_indices"]
    selected_hits = [hit for hit in hits if hit["edge_index"] in selected]
    omitted_hits = [hit for hit in hits if hit["edge_index"] not in selected]
    record = {
        "format": "diag3-coverage-falsifier-hidden-root-census-v1",
        "base_revision": BASE_REVISION,
        "outcome": "COUNTEREXAMPLE" if hits else "NULL_EXACT_BOUNDED_CENSUS",
        "inputs": {str(path.relative_to(ROOT)): digest for path, digest in PINNED.items()},
        "scope": {
            "parent_index": 2599,
            "candidate_fullsupport_factors": 17_824,
            "endpoint_crossed_factor_classes": 10_844,
            "endpoint_uncrossed_factor_classes": 6_980,
            "certified_strict_parent_segment_bank": len(safe.EDGES),
            "certified_strict_parent_segments_tested": list(edge_indices),
            "factor_segment_pairs_exactly_tested": total_pairs,
            "selected_cover_edges": len(selected),
            "omitted_bank_edges": len(safe.EDGES) - len(selected),
        },
        "result": {
            "hidden_root_incidences": len(hits),
            "hidden_root_factor_ids": sorted({hit["factor_id"] for hit in hits}),
            "hidden_root_factor_ids_sha256": ids_digest(
                b"diag3-hidden-root-factor-ids-v1", {hit["factor_id"] for hit in hits}
            ),
            "selected_edge_hits": selected_hits,
            "omitted_edge_hits": omitted_hits,
            "per_edge": rows,
            "edge39_endpoint_parity_obstruction": replay_edge39_endpoint_parity_obstruction(OPEN_IDS),
        },
        "canaries": canaries,
        "coverage": {
            "included": f"all 6,980 endpoint-uncrossed candidates on stored strict-parent segment indices {list(edge_indices)}",
            "excluded": "untested segments; points off the 105 segments; components of a wall away from a tested segment; parent-cell coverage; the pair and triple obligations",
            "nonconsequence": "a null census does not imply that the 40 selected segments meet every wall or every wall component in the nine-dimensional parent cell",
        },
    }
    record["semantic_sha256"] = canonical_digest(record)
    output.write_text(json.dumps(record, indent=2, sort_keys=True) + "\n")
    return record


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--workers", type=int, default=6)
    parser.add_argument(
        "--edge-indices",
        default=",".join(map(str, range(105))),
        help="comma-separated exact subset of the 105 edge indices",
    )
    parser.add_argument("--output", type=Path, default=OUTPUT)
    args = parser.parse_args()
    if not 1 <= args.workers <= 6:
        raise SystemExit("workers must be between 1 and 6")
    edge_indices = tuple(sorted({int(item) for item in args.edge_indices.split(",") if item}))
    if not edge_indices or edge_indices[0] < 0 or edge_indices[-1] >= len(safe.EDGES):
        raise SystemExit("edge indices must be a nonempty subset of 0..104")
    record = build(args.workers, edge_indices, args.output)
    print("OUTCOME", record["outcome"])
    print("EXACT_FACTOR_SEGMENT_PAIRS", record["scope"]["factor_segment_pairs_exactly_tested"])
    print("HIDDEN_ROOT_INCIDENCES", record["result"]["hidden_root_incidences"])
    print("SEMANTIC_SHA256", record["semantic_sha256"])
    resolved_output = args.output.resolve()
    try:
        display_output = resolved_output.relative_to(ROOT)
    except ValueError:
        display_output = resolved_output
    print("ARTIFACT", display_output)


if __name__ == "__main__":
    main()
