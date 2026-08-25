#!/usr/bin/env python3
"""Hostile exact replay of chart-0-to-chart-152 block-bridge labels."""

from __future__ import annotations

from collections import Counter
import copy
import hashlib
import json
from pathlib import Path
import sys


HERE = Path(__file__).resolve().parent
CERTIFICATE = HERE / "data" / "DIAG3_PAIR_PARENT_SOURCE_BLOCK_LABELS_0_152.json"
sys.path.insert(0, str(HERE))
import diag3_pair_parent_source_block_labels_core as core  # noqa: E402


EXPECTED_CERTIFICATE_SHA256 = "63b2df38eb82fb126d659cc7150080b55108eb00a29dff639cd556c38750c4da"
EXPECTED_PROFILE_SHA256 = "b6aa84e62805531e4f32ed63ba5a389011ff607288bfbec4ce64b0394731a796"
EXPECTED_EVENT_LABEL_SHA256 = "e65b6cc7cccf07fb66b590ef6a86fec947f51c2bdcf8c8974cd04be30b6f58b6"


class CertificateError(AssertionError):
    pass


def require(condition, message):
    if not condition:
        raise CertificateError(message)


def validate(record, expected):
    require(record == expected, "certificate differs from exact source replay")
    require(record["format"] == core.FORMAT and record["status"] == core.STATUS, "format/status")
    scope = record["scope"]
    require((scope["parent_index"], scope["source_chart"], scope["target_chart"]) == (2599, 0, 152), "path scope")
    require(scope["path_segments"] == 3 and scope["generic_chambers"] == 5615, "path chamber census")
    require(scope["signature_label_continuation"] == "COMPLETE_ON_ALL_OPEN_PATH_CHAMBERS", "label coverage")
    require(scope["waypoint_incidence"] == "PRESERVED_AS_DISTINCT_EQUAL-LABEL_CHAMBERS", "waypoint incidence")
    require(scope["global_parent_cell_coverage"] == "NOT_CLAIMED", "honest global scope")

    continuation = record["continuation"]
    require(continuation["extension_signature_universe"] == 97224, "extension universe")
    require(continuation["labels_per_generic_chamber"] == 26112, "generic label census")
    require(continuation["ordered_events"] == 5612, "ordered events")
    require(continuation["segment_event_census"] == [2774, 1017, 1821], "segment event census")
    require(continuation["simple_mutation_events"] + continuation["compound_reenumeration_events"] == 5612, "method accounting")
    require(continuation["compound_reenumeration_events"] == 293, "compound event census")
    require(continuation["chart_152_raw_label_state_reconstructed"], "target reconstruction")
    require(continuation["event_label_semantic_sha256"] == EXPECTED_EVENT_LABEL_SHA256, "event-label digest")
    waypoints = continuation["internal_waypoints"]
    require(len(waypoints) == 2, "internal waypoint census")
    require(all(row["left_and_right_label_sets_equal"] for row in waypoints), "waypoint label gluing")
    require(all(row["right_chamber"] == row["left_chamber"] + 1 for row in waypoints), "waypoint chamber separation")
    events = continuation["event_records"]
    require(len(events) == 5612 and [row["event_index"] for row in events] == list(range(5612)), "event records")
    require(Counter(row["method"] for row in events) == {
        "simplicial_basis_mutation": 5319,
        "exact_post_compound_tope_reenumeration": 293,
    }, "continuation methods")
    require(all((row["lost_labels"], row["gained_labels"]) == (2, 2) for row in events if row["method"] == "simplicial_basis_mutation"), "ordinary mutation delta")
    require(all(row["lost_labels"] == row["gained_labels"] for row in events), "balanced label deltas")

    profiles = record["signature_profiles"]
    require(profiles["packed_profile_bytes_each"] == 702, "packed profile width")
    require(profiles["semantic_sha256"] == EXPECTED_PROFILE_SHA256, "profile digest")
    require(sum(profiles["feasible_chamber_count_census"].values()) == 97224, "profile accounting")
    require(sum(profiles["profile_transition_count_census"].values()) == 97224, "transition accounting")
    require(profiles["all_bad_loci_closed_by_incidence_rule"], "bad-locus closure")
    require(record["gluing"]["exact_common_source_vertex_and_label_set"], "source gluing")
    require("2/9" in record["theorem_effect"], "dishonest theorem score")
    return continuation, profiles


def assert_rejected(record, expected, label):
    try:
        validate(record, expected)
    except (CertificateError, KeyError, ValueError, TypeError):
        return
    raise AssertionError(f"hostile canary was accepted: {label}")


def main():
    require(hashlib.sha256(CERTIFICATE.read_bytes()).hexdigest() == EXPECTED_CERTIFICATE_SHA256, "certificate digest")
    record = json.loads(CERTIFICATE.read_text(encoding="utf-8"))
    expected = core.build_record(progress=True)
    continuation, profiles = validate(record, expected)

    hostile = []
    corrupt = copy.deepcopy(record)
    corrupt["scope"]["global_parent_cell_coverage"] = "COMPLETE"
    hostile.append((corrupt, "finite source tree as global coverage"))
    corrupt = copy.deepcopy(record)
    corrupt["normalization"]["raw_extension_reorientation_mask"] ^= 1
    hostile.append((corrupt, "wrong raw-label reorientation"))
    corrupt = copy.deepcopy(record)
    corrupt["continuation"]["event_records"].pop()
    hostile.append((corrupt, "missing event label state"))
    corrupt = copy.deepcopy(record)
    corrupt["continuation"]["event_records"][0]["lost_labels"] = 1
    hostile.append((corrupt, "non-antipodal simple mutation"))
    corrupt = copy.deepcopy(record)
    corrupt["continuation"]["event_records"][100]["gained_labels"] += 1
    hostile.append((corrupt, "unbalanced event delta"))
    corrupt = copy.deepcopy(record)
    corrupt["continuation"]["simple_mutation_events"] -= 1
    hostile.append((corrupt, "corrupt simple-event census"))
    corrupt = copy.deepcopy(record)
    corrupt["continuation"]["internal_waypoints"].pop()
    hostile.append((corrupt, "collapsed internal waypoint"))
    corrupt = copy.deepcopy(record)
    corrupt["continuation"]["chart_152_raw_label_state_reconstructed"] = False
    hostile.append((corrupt, "failed endpoint presented as complete"))
    corrupt = copy.deepcopy(record)
    corrupt["signature_profiles"]["distinct_profiles"] -= 1
    hostile.append((corrupt, "corrupt profile census"))
    corrupt = copy.deepcopy(record)
    corrupt["signature_profiles"]["semantic_sha256"] = "0" * 64
    hostile.append((corrupt, "corrupt profile digest"))
    corrupt = copy.deepcopy(record)
    corrupt["gluing"]["exact_common_source_vertex_and_label_set"] = False
    hostile.append((corrupt, "broken chart-zero gluing"))
    corrupt = copy.deepcopy(record)
    corrupt["inputs"]["bridge_certificate_sha256"] = "0" * 64
    hostile.append((corrupt, "corrupt bridge input digest"))
    for corrupt, label in hostile:
        assert_rejected(corrupt, expected, label)

    print("PASS exact row-2599 chart-0-to-chart-152 label continuation")
    print("PASS 5,319 antipodal simplicial mutations + 293 exact compound updates")
    print("PASS every one of 5,615 chambers has 26,112 labels in the 97,224-signature universe")
    print("PASS two internal waypoints preserve distinct equal-label incident chambers")
    print("PASS continued endpoint equals the independently stored raw chart-152 tope state")
    print("PASS exact gluing to the chart-0-to-chart-89 label path")
    print("PROFILE_SEMANTIC_SHA256", profiles["semantic_sha256"])
    print("EVENT_LABEL_SEMANTIC_SHA256", continuation["event_label_semantic_sha256"])
    print("PASS 12/12 hostile corruptions rejected")
    print("SCOPE complete on the exact three-segment source path; global parent-cell coverage remains open")


if __name__ == "__main__":
    main()
