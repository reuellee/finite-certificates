#!/usr/bin/env python3
"""Hostile exact replay of the row-2599 chart-0-to-chart-89 roadmap."""

from __future__ import annotations

from collections import Counter
from fractions import Fraction
import copy
import json
from pathlib import Path
import sys


HERE = Path(__file__).resolve().parent
CERTIFICATE = HERE / "data" / "DIAG3_PAIR_PARENT_SOURCE_TRANSITION_0_89.json"
sys.path.insert(0, str(HERE))
import build_diag3_pair_parent_source_transition as builder  # noqa: E402
import diag3_pair_parent_source_transition_core as core  # noqa: E402


EXPECTED_POINT_BANK_SHA256 = "3b90799d26b7783e92c2ac697eaaf8b76d26a787f53205873b997657e114180a"
EXPECTED_FACTOR_STATES_SHA256 = "f44b1fccfb4e61273aeceb8796a18098d82c48473e257556ce3d2a22f99b0bcf"
EXPECTED_FACTOR_CENSUS_SHA256 = "3984ce87e11fd59d804e59568177248e218cd1c7bb07aae0a9f9f746858728bc"
EXPECTED_CANDIDATE_SHA256 = "adb2e7257457f158e809450683c46fe7ecafdbdd4a7efdf9ac630e8a4f0fb03f"
EXPECTED_EVENT_SHA256 = "19683a1b46c3dab4f51b770cd7af9237b3c323b7c8f6d0a3d4101a13d890472b"
EXPECTED_STATE_SHA256 = "68fe63818b53e20a51ca7b4580acfad399a40aa4052bea51f43595a49999e9b4"


class CertificateError(AssertionError):
    pass


def require(condition, message):
    if not condition:
        raise CertificateError(message)


def validate(record, expected):
    require(record == expected, "certificate differs from exact source replay")
    inputs = record["inputs"]
    require(core.file_sha256(core.POINT_BANK) == EXPECTED_POINT_BANK_SHA256, "point-bank source digest")
    require(core.file_sha256(core.FACTOR_STATES) == EXPECTED_FACTOR_STATES_SHA256, "factor-state source digest")
    require(core.file_sha256(core.FACTOR_CENSUS) == EXPECTED_FACTOR_CENSUS_SHA256, "factor-census source digest")
    require(core.file_sha256(core.CANDIDATES) == EXPECTED_CANDIDATE_SHA256, "candidate source digest")
    require(inputs["point_bank_sha256"] == EXPECTED_POINT_BANK_SHA256, "stored point-bank digest")
    require(inputs["factor_states_sha256"] == EXPECTED_FACTOR_STATES_SHA256, "stored factor-state digest")
    require(inputs["factor_census_sha256"] == EXPECTED_FACTOR_CENSUS_SHA256, "stored factor-census digest")
    require(inputs["candidate_factor_sha256"] == EXPECTED_CANDIDATE_SHA256, "stored candidate digest")

    require(record["format"] == core.FORMAT and record["status"] == core.STATUS, "format/status")
    scope = record["scope"]
    require((scope["parent_index"], scope["source_chart"], scope["target_chart"]) == (2599, 0, 89), "source transition")
    require(scope["parent_parameter_coverage"] == "COMPLETE_ON_CLOSED_SEGMENT", "parent coverage")
    require(scope["residual_parameter_coverage"] == "COMPLETE_ON_OPEN_SEGMENT", "residual coverage")
    require(scope["global_parent_cell_coverage"] == "NOT_CLAIMED", "honest global scope")
    residence = record["parent_residence"]
    require(residence["parent_bracket_count"] == 70 and residence["strict_on_closed_segment"], "parent residence")
    require(residence["parent_infinity_cells"] == [], "false parent infinity")

    selection = record["selection"]
    require(selection["parent_safe_chart_zero_edge_count"] == 57, "chart-zero safe-edge census")
    require(selection["selected_endpoint_factor_hamming_distance"] == 1197, "selection distance")

    roadmap = record["residual_roadmap"]
    require(roadmap["candidate_factor_count"] == 17824, "candidate factor census")
    require(roadmap["factor_root_count_census"] == {"0": 16607, "1": 1197, "2": 20}, "root-count census")
    require(roadmap["rooted_factor_count"] == 1217, "rooted factor census")
    events = roadmap["events"]
    require(len(events) == roadmap["distinct_ordered_event_count"] == 1237, "event census")
    require(roadmap["event_occurrence_multiplicity_census"] == {"1": 1179, "2": 13, "15": 6, "65": 39}, "event multiplicities")
    require(roadmap["events_semantic_sha256"] == EXPECTED_EVENT_SHA256, "event semantic digest")
    require(roadmap["factor_state_sequence_sha256"] == EXPECTED_STATE_SHA256, "factor-state sequence digest")
    require(roadmap["all_root_boxes_pairwise_ordered"] and roadmap["all_roots_simple_sign_crossings"], "ordered simple roots")
    intervals = [tuple(map(Fraction, event["isolating_interval"])) for event in events]
    require(all(left < right and right - left <= core.ISOLATION_WIDTH for left, right in intervals), "root isolation width")
    require(all(left[1] <= right[0] for left, right in zip(intervals, intervals[1:])), "overlapping event boxes")
    require(all(event["sign_flip"] for event in events), "non-crossing event")
    require(Counter(event["occurrence_multiplicity"] for event in events) == {1: 1179, 2: 13, 15: 6, 65: 39}, "recounted multiplicities")

    cells = record["regular_cw_path"]
    require(cells["zero_cells"] == 1239 and cells["one_cells"] == 1238, "path cell dimensions")
    require(cells["total_cells"] == 2477 and cells["strict_closure_pairs"] == 2476, "path cell/closure census")
    require(cells["parent_infinity_subcomplex"] == [], "false CW infinity")
    frontier = record["label_continuation_frontier"]
    require(frontier["simple_single-occurrence_events"] == 1179, "simple event census")
    require(frontier["compound_events"] == 58, "compound event census")
    require(frontier["compound_event_census"] == {"2": 13, "15": 6, "65": 39}, "compound multiplicities")
    require(frontier["first_compound_event_index"] == 38, "first compound index")
    require(frontier["first_compound_event"] == events[38], "first compound event")
    require("2/9" in record["theorem_effect"], "dishonest theorem score")
    return roadmap, frontier


def assert_rejected(record, expected, label):
    try:
        validate(record, expected)
    except (CertificateError, KeyError, ValueError, TypeError):
        return
    raise AssertionError(f"hostile canary was accepted: {label}")


def main():
    record = json.loads(CERTIFICATE.read_text(encoding="utf-8"))
    expected = builder.build_record()
    roadmap, frontier = validate(record, expected)

    hostile = []
    corrupt = copy.deepcopy(record)
    corrupt["scope"]["global_parent_cell_coverage"] = "COMPLETE"
    hostile.append((corrupt, "sample transition as global coverage"))
    corrupt = copy.deepcopy(record)
    corrupt["scope"]["target_chart"] = 88
    hostile.append((corrupt, "wrong target chart"))
    corrupt = copy.deepcopy(record)
    corrupt["residual_roadmap"]["events"].pop()
    hostile.append((corrupt, "missing event"))
    corrupt = copy.deepcopy(record)
    corrupt["residual_roadmap"]["events"][1]["isolating_interval"][0] = corrupt["residual_roadmap"]["events"][0]["isolating_interval"][0]
    hostile.append((corrupt, "overlapping root boxes"))
    corrupt = copy.deepcopy(record)
    corrupt["residual_roadmap"]["events"][0]["sign_flip"] = False
    hostile.append((corrupt, "tangent event"))
    corrupt = copy.deepcopy(record)
    corrupt["residual_roadmap"]["events"][0]["factor_id"] += 1
    hostile.append((corrupt, "corrupt factor identifier"))
    corrupt = copy.deepcopy(record)
    corrupt["parent_residence"]["parent_infinity_cells"] = ["endpoint_chart_0"]
    hostile.append((corrupt, "endpoint as parent infinity"))
    corrupt = copy.deepcopy(record)
    corrupt["label_continuation_frontier"]["compound_events"] -= 1
    hostile.append((corrupt, "corrupt compound census"))
    corrupt = copy.deepcopy(record)
    corrupt["residual_roadmap"]["factor_state_sequence_sha256"] = "0" * 64
    hostile.append((corrupt, "corrupt state digest"))
    for corrupt, label in hostile:
        assert_rejected(corrupt, expected, label)

    print("PASS exact row-2599 chart-0-to-chart-89 residual roadmap")
    print("PASS all 70 parent brackets remain strict on the closed transition")
    print("PASS 17,824 factors: 16,607 root-free + 1,197 one-root + 20 two-root")
    print("PASS 1,237 pairwise ordered simple crossings reconstruct the chart-89 factor state")
    print("PASS 2,477-cell regular CW path with empty parent-infinity subcomplex")
    print("PASS 1,179 simple events + 58 compound events; first compound index 38")
    print("EVENTS_SEMANTIC_SHA256", roadmap["events_semantic_sha256"])
    print("FIRST_COMPOUND_FACTOR", frontier["first_compound_event"]["factor_id"])
    print("PASS 9/9 hostile corruptions rejected")
    print("SCOPE exact one-segment source transition; label continuation and global coverage remain open")


if __name__ == "__main__":
    main()
