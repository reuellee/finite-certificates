#!/usr/bin/env python3
"""Structural and provenance verifier for MP-001.

This checker does not invoke the producer or trust its summary booleans.  It
pins every input and result, recomputes the finite identities from the stored
records, independently enumerates the parent-safe block-order class, and runs
hostile claim mutations.  Full rederivation of the two newly generated label
histories remains the producer replay described in the research note.
"""

from __future__ import annotations

import argparse
from collections import Counter
from copy import deepcopy
from fractions import Fraction
from hashlib import sha256
from itertools import combinations, permutations
import json
from pathlib import Path
import sys


HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
OMREAL = REPO / "ai" / "omreal"
MANIFEST = HERE / "data" / "EXTENSION_PATH_ALTERNATION_MANIFEST.json"
FULL_MASK = (1 << 56) - 1
EXPECTED_STATUS = "OBSERVATION"
EXPECTED_SCORE = "2/9"
EXPECTED_PATH_FAMILY = (
    "all parent-safe three-block column orders between the pinned chart-0 "
    "and chart-152 representatives"
)


def file_sha256(path: Path) -> str:
    digest = sha256()
    with path.open("rb") as source:
        for block in iter(lambda: source.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def semantic_sha256(record: dict) -> str:
    payload = deepcopy(record)
    payload.pop("semantic_sha256", None)
    return sha256(
        json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("ascii")
    ).hexdigest()


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def verify_claim_boundary(manifest: dict) -> None:
    require(manifest["status"] == EXPECTED_STATUS, "retrospective result was falsely promoted")
    require(manifest["honest_9dvl_score"] == EXPECTED_SCORE, "9DVL score contamination")
    scope = manifest["scope"]
    require(scope["path_family"] == EXPECTED_PATH_FAMILY, "path-family scope was enlarged")
    forbidden = set(scope["excluded_claims"])
    required = {
        "optimality over arbitrary paths in the parent cell",
        "a global row-2599 invariant",
        "a theorem about all oriented matroids",
        "continuous connected-component counts without wall and waypoint semantics",
        "novelty of binary total variation, run counts, or consecutive-ones language",
        "any change to the honest 9DVL score",
    }
    require(required <= forbidden, "a required overclaim exclusion disappeared")
    require("no registered holdout" in manifest["status_reason"], "false holdout language")


def verify_pinned_file(row: dict) -> None:
    path = REPO / row["path"]
    require(path.is_file(), f"missing pinned file: {row['path']}")
    require(file_sha256(path) == row["sha256"], f"hash mismatch: {row['path']}")


def normalized_spectrum(record: dict) -> dict[int, int]:
    return {int(level): int(amount) for level, amount in record["transition_spectrum"].items()}


def tail_counts(spectrum: dict[int, int]) -> dict[int, int]:
    return {
        threshold: sum(amount for level, amount in spectrum.items() if level >= threshold)
        for threshold in range(1, max(spectrum) + 1)
    }


def verify_result(record: dict, expected: dict) -> None:
    require(record["path_id"] == expected["path_id"], "path identity mismatch")
    if "block_order" in expected:
        actual_order = record.get("block_order")
        if actual_order is None and record["path_id"] == "row2599-chart-0-to-152-three-block":
            actual_order = [0, 1, 2]
        require(actual_order == expected["block_order"], "record block-order mismatch")
    spectrum = normalized_spectrum(record)
    expected_spectrum = {int(level): amount for level, amount in expected["transition_spectrum"].items()}
    require(spectrum == expected_spectrum, "transition spectrum mismatch")
    require(sum(spectrum.values()) == record["signature_universe"] == 97_224, "universe census mismatch")
    require(
        sum(level * amount for level, amount in spectrum.items()) == record["transition_mass"],
        "transition-mass identity failed",
    )
    require(
        sum(amount for level, amount in spectrum.items() if level & 1)
        == record["endpoint_symmetric_difference"],
        "endpoint-parity census failed",
    )
    maximum = max(spectrum)
    maximizers = record["maximizers"]
    signatures = [int(row["signature"]) for row in maximizers]
    require(record["maximum_alternation"] == maximum == expected["maximum_alternation"], "maximum mismatch")
    require(len(maximizers) == spectrum[maximum] == record["maximizer_count"] == expected["maximizer_count"], "maximizer census mismatch")
    require(len(signatures) == len(set(signatures)), "duplicate maximizer")
    require(
        all(len(row["event_indices"]) == maximum for row in maximizers),
        "maximizer history length mismatch",
    )
    require(
        all(
            row["event_indices"] == sorted(set(row["event_indices"]))
            and all(0 <= index < record["events"] for index in row["event_indices"])
            for row in maximizers
        ),
        "invalid maximizer event history",
    )
    require(
        all(row["antipode"] == (row["signature"] ^ FULL_MASK) for row in maximizers),
        "bad antipode field",
    )
    require(all((signature ^ FULL_MASK) in set(signatures) for signature in signatures), "maximizers are not antipode-closed")
    require(record["maximizers_antipode_closed"] is True, "false antipode-closure verdict")
    require(tail_counts(spectrum) == {int(k): v for k, v in expected["tail_counts"].items()}, "tail census mismatch")
    for key in ("events", "transition_mass", "endpoint_symmetric_difference"):
        require(record[key] == expected[key], f"{key} mismatch")
    require(record["semantic_sha256"] == expected["semantic_sha256"], "semantic pin mismatch")
    require(semantic_sha256(record) == record["semantic_sha256"], "semantic digest mismatch")


def verify_committed_spectra(records: dict[str, dict]) -> None:
    source = json.loads(
        (OMREAL / "data" / "DIAG3_PAIR_PARENT_SOURCE_LABELS_0_89.json").read_text()
    )
    block = json.loads(
        (OMREAL / "data" / "DIAG3_PAIR_PARENT_SOURCE_BLOCK_LABELS_0_152.json").read_text()
    )
    require(
        records["row2599-chart-0-to-89"]["transition_spectrum"]
        == source["signature_profiles"]["profile_transition_count_census"],
        "source result no longer recovers the committed spectrum",
    )
    require(
        records["row2599-chart-0-to-152-three-block"]["transition_spectrum"]
        == block["signature_profiles"]["profile_transition_count_census"],
        "block-012 result no longer recovers the committed spectrum",
    )


def exact_valid_orders() -> list[list[int]]:
    sys.path.insert(0, str(OMREAL))
    import diag3_pair_parent_source_block_bridge_core as bridge  # noqa: PLC0415
    import diag3_pair_parent_source_transition_core as transition  # noqa: PLC0415
    import verify_diag3_pair_fullsupport_safe_segment_walls as safe  # noqa: PLC0415
    import verify_diag3_pair_global_parent_face_gate as gate  # noqa: PLC0415

    _matrices, points, _packed, _states, _hamming, _multiplicity = transition.exact_inputs()
    records = [json.loads(line) for line in safe.CATALOG.read_text().splitlines() if line]
    parents, _parent_digest = gate.parent_polynomials(records[2599])
    answer = []
    for order in permutations(range(3)):
        vertices = bridge.bridge_vertices(points[0], points[152], order)
        if all(
            all(
                target * bridge.evaluator.evaluate(polynomial, vertex) > Fraction(0)
                for _label, target, polynomial, _terms in parents
            )
            for vertex in vertices
        ):
            answer.append(list(order))
    return answer


def verify_conclusions(manifest: dict, records: dict[str, dict]) -> None:
    expected_orders = [[0, 1, 2], [0, 2, 1], [1, 0, 2]]
    require(manifest["scope"]["valid_block_orders"] == expected_orders, "manifest order class changed")
    require(exact_valid_orders() == expected_orders, "exact parent-safe block-order class changed")
    by_order = {
        tuple(row["block_order"]): records[row["path_id"]]
        for row in manifest["results"]
        if "block_order" in row
    }
    require(set(by_order) == {tuple(order) for order in expected_orders}, "missing valid block order")
    maxima = {order: record["maximum_alternation"] for order, record in by_order.items()}
    require(min(maxima.values()) == manifest["finite_conclusions"]["restricted_block_order_minimax"] == 5, "false restricted minimax")
    winner = tuple(manifest["finite_conclusions"]["strict_tail_dominator"])
    require(winner == (1, 0, 2), "tail winner changed")
    winner_tail = tail_counts(normalized_spectrum(by_order[winner]))
    thresholds = manifest["finite_conclusions"]["strict_tail_dominance_thresholds"]
    require(thresholds == [1, 2, 3, 4, 5], "tail thresholds changed")
    for order, record in by_order.items():
        if order == winner:
            continue
        rival_tail = tail_counts(normalized_spectrum(record))
        require(all(winner_tail[k] < rival_tail[k] for k in thresholds), f"no strict tail dominance over {order}")
        require(by_order[winner]["events"] < record["events"], f"event-count dominance failed over {order}")
        require(by_order[winner]["transition_mass"] < record["transition_mass"], f"mass dominance failed over {order}")
    maximizer_sets = {
        path_id: {row["signature"] for row in record["maximizers"]}
        for path_id, record in records.items()
    }
    require(
        all(not maximizer_sets[left] & maximizer_sets[right] for left, right in combinations(maximizer_sets, 2)),
        "maximizer sets are not pairwise disjoint",
    )
    require(
        manifest["finite_conclusions"]["retrospective_shared_exceptional_core_candidate"] == "REFUTED",
        "refutation status changed",
    )
    require(
        manifest["finite_conclusions"]["strictly_fewer_events_than_other_valid_orders"] is True,
        "event dominance conclusion disappeared",
    )
    require(
        manifest["finite_conclusions"]["strictly_smaller_transition_mass_than_other_valid_orders"] is True,
        "mass dominance conclusion disappeared",
    )
    require(
        manifest["finite_conclusions"]["pairwise_disjoint_maximizer_sets_across_all_four_paths"] is True,
        "disjointness conclusion disappeared",
    )


def rejection(action, fragment: str) -> None:
    try:
        action()
    except AssertionError as error:
        require(fragment in str(error), f"canary failed for the wrong reason: {error}")
    else:
        raise AssertionError(f"hostile mutation survived: {fragment}")


def hostile_canaries(manifest: dict, records: dict[str, dict]) -> int:
    source_id = "row2599-chart-0-to-89"
    block_id = "row2599-chart-0-to-152-three-block"
    source_expected = next(row for row in manifest["results"] if row["path_id"] == source_id)

    bad = deepcopy(records[source_id])
    bad["transition_spectrum"]["3"] -= 1
    rejection(lambda: verify_result(bad, source_expected), "transition spectrum mismatch")

    bad = deepcopy(records[source_id])
    bad["maximizers"].pop()
    rejection(lambda: verify_result(bad, source_expected), "maximizer census mismatch")

    bad_manifest = deepcopy(manifest)
    bad_manifest["status"] = "EXACT_FINITE_FACT"
    rejection(lambda: verify_claim_boundary(bad_manifest), "falsely promoted")

    bad_manifest = deepcopy(manifest)
    bad_manifest["status_reason"] = "A registered holdout passed."
    rejection(lambda: verify_claim_boundary(bad_manifest), "false holdout language")

    bad_manifest = deepcopy(manifest)
    bad_manifest["honest_9dvl_score"] = "3/9"
    rejection(lambda: verify_claim_boundary(bad_manifest), "score contamination")

    bad_manifest = deepcopy(manifest)
    bad_manifest["scope"]["path_family"] = "all paths in the row-2599 parent cell"
    rejection(lambda: verify_claim_boundary(bad_manifest), "scope was enlarged")

    bad_manifest = deepcopy(manifest)
    bad_manifest["finite_conclusions"]["restricted_block_order_minimax"] = 4
    rejection(lambda: verify_conclusions(bad_manifest, records), "false restricted minimax")

    bad_manifest = deepcopy(manifest)
    bad_manifest["provenance"]["inputs"][0]["sha256"] = "0" * 64
    rejection(lambda: verify_pinned_file(bad_manifest["provenance"]["inputs"][0]), "hash mismatch")

    bad_records = deepcopy(records)
    bad_records[block_id]["maximizers"] = bad_records[source_id]["maximizers"]
    rejection(lambda: verify_conclusions(manifest, bad_records), "not pairwise disjoint")
    return 9


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--skip-canaries", action="store_true")
    args = parser.parse_args()
    manifest = json.loads(MANIFEST.read_text())
    verify_claim_boundary(manifest)
    verify_pinned_file(manifest["provenance"]["producer"])
    for row in manifest["provenance"]["inputs"]:
        verify_pinned_file(row)

    records = {}
    for expected in manifest["results"]:
        verify_pinned_file(expected)
        record = json.loads((REPO / expected["path"]).read_text())
        verify_result(record, expected)
        records[record["path_id"]] = record
    verify_committed_spectra(records)
    verify_conclusions(manifest, records)
    canaries = 0 if args.skip_canaries else hostile_canaries(manifest, records)
    print(
        "PASS MP-001 structural/provenance verification: "
        f"paths={len(records)} valid_block_orders=3 hostile_canaries={canaries} "
        "status=OBSERVATION honest_9dvl_score=2/9"
    )


if __name__ == "__main__":
    main()
