#!/usr/bin/env python3
"""Hostile exact replay of the row-2599 chart-0-to-chart-152 block bridge."""

from __future__ import annotations

from collections import Counter
from fractions import Fraction
import copy
import json

import diag3_pair_parent_source_block_bridge_core as core


class CertificateError(AssertionError):
    pass


def require(condition, message):
    if not condition:
        raise CertificateError(message)


def validate(record, expected):
    require(record == expected, "certificate differs from exact block-bridge replay")
    require(record["format"] == core.FORMAT and record["status"] == core.STATUS, "format/status")
    scope = record["scope"]
    require((scope["source_chart"], scope["target_chart"]) == (0, 152), "bridge endpoints")
    require(scope["parent_parameter_coverage"] == "COMPLETE_ON_CLOSED_PIECEWISE_LINEAR_PATH", "parent coverage")
    require(scope["global_parent_cell_coverage"] == "NOT_CLAIMED", "dishonest global coverage")

    audit = record["straight_transition_audit"]
    require(audit["certified_straight_edges"] == 105, "straight edge census")
    require(audit["component_size_census"] == {"1": 71, "2": 1, "105": 1}, "straight component census")
    require(audit["straight_isolated_germs"] == 71 and audit["target_was_straight_isolated"], "isolated target")

    selection = record["selection"]
    require(selection["minimum_segment_count"] == 3, "bridge length")
    require(selection["selected_endpoint_factor_hamming_distance"] == 3384, "selection Hamming distance")
    require(selection["selected_block_order"] == [0, 1, 2], "block order")
    require(len(selection["direct_chart_zero_block_bridge_candidates"]) == 6, "candidate bridge census")
    require(selection["direct_chart_zero_block_bridge_candidates"][0]["target_chart"] == 152, "objective target")

    residence = record["parent_residence"]
    require(residence["parent_bracket_count"] == 70, "parent bracket census")
    require(residence["strict_generic_waypoints"] == 4, "generic waypoint census")
    require(len(residence["segments"]) == 3, "parent segment census")
    require(all(row["parent_brackets_strict"] == 70 for row in residence["segments"]), "parent strictness")
    require(residence["parent_infinity_cells"] == [], "false parent infinity")

    overlap = record["overlap_with_labelled_0_89_path"]
    require(overlap["shared_chart"] == 0, "wrong overlap vertex")
    require(overlap["raw_extension_labels"] == 26_112, "overlap label census")
    require(overlap["compatibility"] == "EXACT_COMMON_SOURCE_VERTEX_AND_RAW_LABEL_SET", "overlap compatibility")

    roadmap = record["residual_roadmap"]
    require(roadmap["candidate_factor_count"] == 17_824, "candidate factor census")
    require(roadmap["segment_factor_root_count_census"] == [
        {"0": 15_059, "1": 2_756, "2": 9},
        {"0": 16_808, "1": 1_015, "2": 1},
        {"0": 16_008, "1": 1_811, "2": 5},
    ], "segment root census")
    events = roadmap["events"]
    require(len(events) == roadmap["ordered_root_events"] == 5_612, "event census")
    require(roadmap["generic_waypoint_zero_factor_census"] == [0, 0, 0, 0], "nongeneric waypoint")
    require(roadmap["all_root_boxes_pairwise_ordered_within_segments"], "unordered roots")
    require(roadmap["all_roots_simple_sign_crossings"], "nonsimple root")
    require(roadmap["target_factor_state_reconstructed"], "target state not reconstructed")
    require(Counter(event["segment_index"] for event in events) == {0: 2774, 1: 1017, 2: 1821}, "segment event census")
    require(all(event["sign_flip"] for event in events), "noncrossing event")
    for segment in range(3):
        intervals = [
            tuple(map(Fraction, event["isolating_interval"]))
            for event in events
            if event["segment_index"] == segment
        ]
        require(all(left < right and right - left <= core.ISOLATION_WIDTH for left, right in intervals), "root isolation width")
        require(all(first[1] <= second[0] for first, second in zip(intervals, intervals[1:])), "overlapping roots")

    cells = record["regular_cw_path"]
    require(cells["zero_cells"] == 5_616 and cells["one_cells"] == 5_615, "path dimensions")
    require(cells["total_cells"] == 11_231 and cells["strict_closure_pairs"] == 11_230, "path closure census")
    require(cells["parent_infinity_subcomplex"] == [], "false CW infinity")
    require("2/9" in record["theorem_effect"], "dishonest theorem score")
    return roadmap


def assert_rejected(record, expected, label):
    try:
        validate(record, expected)
    except (CertificateError, KeyError, ValueError, TypeError):
        return
    raise AssertionError(f"hostile canary was accepted: {label}")


def main():
    record = json.loads(core.OUTPUT.read_text(encoding="utf-8"))
    expected = core.build_record(progress=True)
    roadmap = validate(record, expected)

    hostile = []
    corrupt = copy.deepcopy(record)
    corrupt["scope"]["global_parent_cell_coverage"] = "COMPLETE"
    hostile.append((corrupt, "finite bridge as global coverage"))
    corrupt = copy.deepcopy(record)
    corrupt["straight_transition_audit"]["straight_isolated_germs"] -= 1
    hostile.append((corrupt, "corrupt straight component audit"))
    corrupt = copy.deepcopy(record)
    corrupt["selection"]["selected_endpoint_factor_hamming_distance"] -= 1
    hostile.append((corrupt, "dishonest objective selection"))
    corrupt = copy.deepcopy(record)
    corrupt["selection"]["selected_block_order"] = [1, 0, 2]
    hostile.append((corrupt, "wrong block order"))
    corrupt = copy.deepcopy(record)
    corrupt["parent_residence"]["segments"][0]["parent_brackets_strict"] -= 1
    hostile.append((corrupt, "lost parent bracket"))
    corrupt = copy.deepcopy(record)
    corrupt["overlap_with_labelled_0_89_path"]["raw_extension_labels"] -= 1
    hostile.append((corrupt, "corrupt labelled overlap"))
    corrupt = copy.deepcopy(record)
    corrupt["residual_roadmap"]["events"].pop()
    hostile.append((corrupt, "missing residual event"))
    corrupt = copy.deepcopy(record)
    corrupt["residual_roadmap"]["events"][0]["sign_flip"] = False
    hostile.append((corrupt, "tangent event"))
    corrupt = copy.deepcopy(record)
    corrupt["residual_roadmap"]["events"][0]["factor_id"] += 1
    hostile.append((corrupt, "corrupt factor ID"))
    corrupt = copy.deepcopy(record)
    corrupt["residual_roadmap"]["factor_state_sequence_sha256"] = "0" * 64
    hostile.append((corrupt, "corrupt state digest"))
    corrupt = copy.deepcopy(record)
    corrupt["parent_residence"]["parent_infinity_cells"] = ["scope_endpoint"]
    hostile.append((corrupt, "scope endpoint as infinity"))
    corrupt = copy.deepcopy(record)
    corrupt["regular_cw_path"]["strict_closure_pairs"] -= 1
    hostile.append((corrupt, "incomplete closure"))
    for corrupt, label in hostile:
        assert_rejected(corrupt, expected, label)

    print("PASS exact row-2599 chart-0-to-chart-152 three-block bridge")
    print("PASS straight graph audit: 105 edges / 73 components / 71 isolated germs")
    print("PASS objective direct bridge selection: chart 152 / 3 segments / Hamming 3384")
    print("PASS all 70 parent brackets strict on all three one-column segments")
    print("PASS 17,824 factors x 3 segments; 5,612 ordered simple crossings")
    print("PASS 11,231-cell regular CW path; target factor state reconstructed")
    print("EVENTS_SEMANTIC_SHA256", roadmap["events_semantic_sha256"])
    print("PASS 12/12 hostile corruptions rejected")
    print("SCOPE exact bridge to one formerly isolated germ; global coverage remains open")


if __name__ == "__main__":
    main()
