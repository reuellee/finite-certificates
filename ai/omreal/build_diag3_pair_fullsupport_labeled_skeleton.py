#!/usr/bin/env python3
"""Compile the first exact labelled subcomplex of the 40-edge source cover.

The accepted minimum cover has forty strict-parent segments.  At present only
edge 27, chart 0 to chart 89, has a complete exact residual roadmap and
extension-label continuation.  This producer turns that path into a genuine
face-compatible one-dimensional regular complex, materializes its complete
97,224-signature profile map, and fails closed on the other thirty-nine
unrefined cover edges.
"""

from __future__ import annotations

from base64 import b64encode
from collections import Counter
from copy import deepcopy
from hashlib import sha256
import gzip
import json
from pathlib import Path
import sys

import numpy as np


HERE = Path(__file__).resolve().parent
DATA = HERE / "data"
OUTPUT = DATA / "DIAG3_PAIR_FULLSUPPORT_LABELED_SKELETON.json"
PROFILE_OUTPUT = DATA / "DIAG3_PAIR_FULLSUPPORT_LABELED_SKELETON_PROFILES.json.gz"
COVER = DATA / "DIAG3_PAIR_FULLSUPPORT_SEGMENT_COVER.json"
TRANSITION = DATA / "DIAG3_PAIR_PARENT_SOURCE_TRANSITION_0_89.json"
LABELS = DATA / "DIAG3_PAIR_PARENT_SOURCE_LABELS_0_89.json"
FORMAT = "diag3-pair-fullsupport-labeled-skeleton-v1"
PROFILE_FORMAT = "diag3-pair-fullsupport-labeled-skeleton-profiles-v1"
COMPILED_EDGE_INDEX = 27
EXPECTED_COVER_SHA256 = "19248dd148d1fd002931ed5f48197869dd42c68a513376e1a4d6941389bda307"
EXPECTED_TRANSITION_SHA256 = "87f2d7ce337651cea498cc50d36c1b53c8b2294aef54ceac89f0fcc552c7b2d2"
EXPECTED_LABELS_SHA256 = "c6071484960d8bde8c0140aac40ec2a065cc7597d23fcadb3503b25d87f5466a"

sys.path.insert(0, str(HERE))
import diag3_pair_parent_source_labels_core as labels_core  # noqa: E402
import verify_diag3_pair_fullsupport_safe_segment_walls as safe  # noqa: E402


def canonical_bytes(value) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode("ascii")


def file_sha256(path: Path) -> str:
    digest = sha256()
    with path.open("rb") as source:
        for block in iter(lambda: source.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def semantic_seal(record) -> str:
    payload = deepcopy(record)
    payload.pop("semantic_sha256", None)
    return sha256(canonical_bytes(payload)).hexdigest()


def require_accepted_dependencies(cover, transition, labels) -> None:
    actual = {
        "cover": file_sha256(COVER),
        "transition": file_sha256(TRANSITION),
        "labels": file_sha256(LABELS),
    }
    expected = {
        "cover": EXPECTED_COVER_SHA256,
        "transition": EXPECTED_TRANSITION_SHA256,
        "labels": EXPECTED_LABELS_SHA256,
    }
    if actual != expected:
        raise AssertionError("accepted cover/transition/labels source digest changed")
    if labels["inputs"]["transition_certificate_sha256"] != actual["transition"]:
        raise AssertionError("label continuation is not cross-pinned to the accepted transition")
    if labels["inputs"]["transition_certificate"] != str(
        TRANSITION.relative_to(HERE.parents[1])
    ):
        raise AssertionError("label continuation transition path changed")

    transition_events = transition["residual_roadmap"]["events"]
    label_events = labels["continuation"]["event_records"]
    if len(transition_events) != len(label_events):
        raise AssertionError("transition/label event census differs")
    for event_index, (transition_event, label_event) in enumerate(
        zip(transition_events, label_events, strict=True)
    ):
        expected_event = (
            event_index,
            int(transition_event["factor_id"]),
            int(transition_event["occurrence_multiplicity"]),
        )
        actual_event = (
            int(label_event["event_index"]),
            int(label_event["factor_id"]),
            int(label_event["occurrence_multiplicity"]),
        )
        if actual_event != expected_event:
            raise AssertionError(
                f"transition/label event identity differs at event {event_index}"
            )


def bit_payload(bits) -> bytes:
    return np.packbits(np.asarray(bits, dtype=np.uint8), bitorder="little").tobytes()


def write_deterministic_gzip(path: Path, value) -> None:
    with path.open("wb") as raw:
        with gzip.GzipFile(filename="", mode="wb", fileobj=raw, mtime=0) as target:
            target.write(canonical_bytes(value) + b"\n")


def stable_cells(events):
    zero_ids = ["row2599:chart:0"]
    cells = [{
        "id": zero_ids[0],
        "dimension": 0,
        "kind": "stored_strict_parent_chart",
        "chart_index": 0,
    }]
    for event_index, event in enumerate(events):
        identifier = (
            f"row2599:edge:{COMPILED_EDGE_INDEX:03d}:event:{event_index:04d}:"
            f"factor:{int(event['factor_id'])}:root:{int(event['root_index_within_factor'])}"
        )
        zero_ids.append(identifier)
        cells.append({
            "id": identifier,
            "dimension": 0,
            "kind": "isolated_residual_event",
            "event_index": event_index,
            "factor_id": int(event["factor_id"]),
            "root_index_within_factor": int(event["root_index_within_factor"]),
            "isolating_interval": list(event["isolating_interval"]),
            "occurrence_multiplicity": int(event["occurrence_multiplicity"]),
        })
    zero_ids.append("row2599:chart:89")
    cells.append({
        "id": zero_ids[-1],
        "dimension": 0,
        "kind": "stored_strict_parent_chart",
        "chart_index": 89,
    })

    one_ids = []
    closure = []
    incidence = []
    for chamber in range(len(events) + 1):
        identifier = f"row2599:edge:{COMPILED_EDGE_INDEX:03d}:open:{chamber:04d}"
        one_ids.append(identifier)
        left, right = zero_ids[chamber], zero_ids[chamber + 1]
        cells.append({
            "id": identifier,
            "dimension": 1,
            "kind": "open_residual_chamber",
            "chamber_index": chamber,
            "oriented_boundary": [[left, -1], [right, 1]],
        })
        closure.extend(([identifier, left], [identifier, right]))
        incidence.extend(([left, identifier, -1], [right, identifier, 1]))
    return cells, zero_ids, one_ids, closure, incidence


def profile_catalog(universe, packed_profiles, zero_count, one_count, source_digest):
    if packed_profiles.shape != (97_224, (one_count + 7) // 8):
        raise AssertionError("packed profile shape changed")
    valid_last = (1 << (one_count & 7)) - 1 if one_count & 7 else 255
    payloads = []
    for row in packed_profiles:
        payload = bytearray(row.tobytes())
        payload[-1] &= valid_last
        payloads.append(bytes(payload))
    if tuple(map(int, universe)) != tuple(sorted(map(int, universe))):
        raise AssertionError("extension signatures are not in canonical increasing order")
    unique = sorted(set(payloads))
    if len(unique) != 2_458 or any(
        left >= right for left, right in zip(unique, unique[1:])
    ):
        raise AssertionError("profile payloads are not distinct lexicographic IDs")
    profile_id = {payload: index for index, payload in enumerate(unique)}
    assignments = [profile_id[payload] for payload in payloads]
    counts = Counter(assignments)

    rows = []
    bad_digest = sha256(b"diag3-fullsupport-labeled-skeleton-bad-membership-v1\0")
    for identifier, feasible in enumerate(unique):
        feasible_bits = np.unpackbits(
            np.frombuffer(feasible, dtype=np.uint8), bitorder="little"
        )[:one_count]
        bad_one = 1 - feasible_bits
        bad_zero = np.zeros(zero_count, dtype=np.uint8)
        bad_zero[:-1] |= bad_one
        bad_zero[1:] |= bad_one
        bad_one_payload = bit_payload(bad_one)
        bad_zero_payload = bit_payload(bad_zero)
        row = {
            "profile_id": identifier,
            "signature_count": counts[identifier],
            "feasible_one_cells_base64": b64encode(feasible).decode("ascii"),
            "bad_one_cells_base64": b64encode(bad_one_payload).decode("ascii"),
            "bad_zero_cells_base64": b64encode(bad_zero_payload).decode("ascii"),
        }
        rows.append(row)
        bad_digest.update(identifier.to_bytes(2, "little"))
        bad_digest.update(counts[identifier].to_bytes(4, "little"))
        bad_digest.update(feasible)
        bad_digest.update(bad_one_payload)
        bad_digest.update(bad_zero_payload)

    assignment_payload = b"".join(value.to_bytes(2, "little") for value in assignments)
    universe_digest = sha256(b"diag3-row2599-extension-universe-v1\0")
    semantic = sha256(b"diag3-row2599-path-label-profiles-v1\0")
    for signature, feasible in zip(universe, payloads, strict=True):
        universe_digest.update(int(signature).to_bytes(7, "little"))
        semantic.update(int(signature).to_bytes(7, "little"))
        semantic.update(feasible)
    if semantic.hexdigest() != source_digest:
        raise AssertionError("materialized profiles disagree with accepted semantic digest")

    return {
        "format": PROFILE_FORMAT,
        "source_edge_index": COMPILED_EDGE_INDEX,
        "signature_order": "ascending unsigned 56-bit row-2599 extension signature",
        "signature_universe_count": len(universe),
        "signature_universe_sha256": universe_digest.hexdigest(),
        "signature_profile_id_width_bytes": 2,
        "signature_profile_ids_base64": b64encode(assignment_payload).decode("ascii"),
        "profile_count": len(rows),
        "profile_rows": rows,
        "bad_membership_rule": (
            "an open one-cell is bad iff its chamber is infeasible; a zero-cell "
            "is bad iff at least one incident open one-cell is bad"
        ),
        "bad_membership_semantic_sha256": bad_digest.hexdigest(),
        "source_signature_profile_semantic_sha256": source_digest,
    }


def build_record(progress=False):
    cover = json.loads(COVER.read_text(encoding="utf-8"))
    transition = json.loads(TRANSITION.read_text(encoding="utf-8"))
    stored_labels = json.loads(LABELS.read_text(encoding="utf-8"))
    require_accepted_dependencies(cover, transition, stored_labels)
    selected = tuple(map(int, cover["source_bank"]["selected_edge_indices"]))
    if len(selected) != 40 or COMPILED_EDGE_INDEX not in selected:
        raise AssertionError("minimum-cover edge selection changed")
    if tuple(safe.EDGES[COMPILED_EDGE_INDEX]) != (0, 89):
        raise AssertionError("compiled edge no longer names chart 0 to chart 89")

    rebuilt_labels, universe, packed_profiles = labels_core.build_record(
        progress=progress, include_profile_data=True
    )
    if rebuilt_labels != stored_labels:
        raise AssertionError("accepted path-label certificate differs from exact replay")
    events = transition["residual_roadmap"]["events"]
    if len(events) != 1_237:
        raise AssertionError("compiled event count changed")

    cells, zero_ids, one_ids, closure, incidence = stable_cells(events)
    catalog = profile_catalog(
        universe,
        packed_profiles,
        len(zero_ids),
        len(one_ids),
        stored_labels["signature_profiles"]["semantic_sha256"],
    )
    write_deterministic_gzip(PROFILE_OUTPUT, catalog)

    selected_pairs = [tuple(map(int, safe.EDGES[index])) for index in selected]
    charts = sorted({chart for pair in selected_pairs for chart in pair})
    pending = [index for index in selected if index != COMPILED_EDGE_INDEX]
    cell_digest = sha256(canonical_bytes(cells)).hexdigest()
    closure_digest = sha256(canonical_bytes(closure)).hexdigest()
    incidence_digest = sha256(canonical_bytes(incidence)).hexdigest()
    record = {
        "format": FORMAT,
        "status": "EXACT_PARTIAL_LABELED_SKELETON_BOUNDED_NO_GO",
        "scope": {
            "parent_index": 2599,
            "support": [15, 15, 15],
            "minimum_source_cover_edges": 40,
            "fully_compiled_cover_edges": 1,
            "pending_cover_edges": 39,
            "skeleton_coverage": "COMPLETE_ONLY_ON_SELECTED_EDGE_27_CHART_0_TO_89",
            "parent_cell_component_coverage": "NOT_CLAIMED",
            "global_parent_cell_coverage": "NOT_CLAIMED",
            "pair_branch_closed": False,
            "triple_branch_closed": False,
            "honest_9dvl_score": "2/9",
        },
        "inputs": {
            "minimum_cover_path": str(COVER.relative_to(HERE.parents[1])),
            "minimum_cover_sha256": file_sha256(COVER),
            "transition_path": str(TRANSITION.relative_to(HERE.parents[1])),
            "transition_sha256": file_sha256(TRANSITION),
            "labels_path": str(LABELS.relative_to(HERE.parents[1])),
            "labels_sha256": file_sha256(LABELS),
            "profile_catalog_path": str(PROFILE_OUTPUT.relative_to(HERE.parents[1])),
            "profile_catalog_sha256": file_sha256(PROFILE_OUTPUT),
        },
        "unrefined_minimum_source_graph": {
            "chart_vertex_count": len(charts),
            "chart_indices": charts,
            "coarse_edge_count": 40,
            "coarse_edges": [
                {
                    "edge_index": index,
                    "id": f"row2599:source-edge:{index:03d}",
                    "endpoint_chart_indices": list(safe.EDGES[index]),
                    "label_compatible_regular_refinement": (
                        "COMPLETE" if index == COMPILED_EDGE_INDEX else "MISSING"
                    ),
                }
                for index in selected
            ],
            "warning": (
                "These coarse source edges are exact parent-resident segments, "
                "but an unsubdivided edge is not a label-compatible master cell."
            ),
        },
        "compiled_regular_subcomplex": {
            "compiled_source_edge_index": COMPILED_EDGE_INDEX,
            "compiled_chart_pair": [0, 89],
            "cells": cells,
            "cell_count_by_dimension": {"0": len(zero_ids), "1": len(one_ids)},
            "cells_sha256": cell_digest,
            "strict_closure_pairs": closure,
            "strict_closure_pairs_sha256": closure_digest,
            "strict_three_cell_chains": [],
            "scope_endpoint_cells": [zero_ids[0], zero_ids[-1]],
            "parent_infinity_subcomplex": [],
            "integral_boundary": {
                "c0_basis": zero_ids,
                "c1_basis": one_ids,
                "d1_entries": incidence,
                "d1_entries_sha256": incidence_digest,
                "d_squared_zero": True,
                "rank_d1": len(one_ids),
                "h0_rank": 1,
                "h1_rank": 0,
            },
            "signature_profile_source": {
                "extension_signature_universe": 97_224,
                "generic_one_cells": len(one_ids),
                "distinct_profiles": catalog["profile_count"],
                "source_semantic_sha256": catalog["source_signature_profile_semantic_sha256"],
                "bad_membership_semantic_sha256": catalog["bad_membership_semantic_sha256"],
                "all_bad_loci_closed_by_incidence_rule": True,
            },
        },
        "fail_closed_contract_audit": {
            "result": "BOUNDED_NO_GO_FOR_PROMOTING_THE_40_EDGE_COVER_AS_IS",
            "compiled_edge_indices": [COMPILED_EDGE_INDEX],
            "pending_edge_indices": pending,
            "minimal_missing_datum": (
                "For each pending source edge: the complete ordered exact residual-root "
                "roadmap, including coincident-event groups, plus exact continuation of "
                "the 97,224 extension-signature labels across every compound event."
            ),
            "fields_already_complete_on_edge_27": [
                "globally stable regular cell IDs",
                "strict closure pairs",
                "strict three-cell chains (empty by dimension)",
                "signed integral incidence",
                "complete extension-signature bad-membership profiles",
                "true parent-infinity membership",
            ],
            "parent_infinity_classification": (
                "EMPTY: the exact signed-parent Bernstein certificate keeps the whole "
                "closed segment strictly inside row 2599; its two path endpoints are "
                "ordinary stored interior chart vertices, not parent infinity."
            ),
        },
        "theorem_effect": (
            "Produces a complete labelled regular-CW contract on one of the forty "
            "optimal full-support cover edges and identifies the exact missing datum on "
            "the other thirty-nine. This is source-skeleton coverage, not parent-cell or "
            "component coverage; both diagonal-three obligations remain open and the "
            "honest 9DVL score remains 2/9."
        ),
        "verifier": {
            "command": "python ai/omreal/verify_diag3_pair_fullsupport_labeled_skeleton.py",
            "hostile_corruptions": 16,
            "trust_boundary": (
                "independent structural and profile-digest replay; the exact cover, path "
                "roadmap, and path labels are hard-pinned accepted dependencies with "
                "event-by-event transition/label cross-checking"
            ),
        },
    }
    record["semantic_sha256"] = semantic_seal(record)
    return record


def main():
    record = build_record(progress=True)
    OUTPUT.write_text(json.dumps(record, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print("WROTE", OUTPUT)
    print("WROTE", PROFILE_OUTPUT)


if __name__ == "__main__":
    main()
