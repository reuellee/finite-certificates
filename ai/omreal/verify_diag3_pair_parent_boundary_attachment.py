#!/usr/bin/env python3
"""Hostile exact replay of the chart-89 to [1237]=0 attachment."""

from __future__ import annotations

from collections import Counter
import copy
import hashlib
import json
from pathlib import Path
import sys


HERE = Path(__file__).resolve().parent
CERTIFICATE = HERE / "data" / "DIAG3_PAIR_PARENT_BOUNDARY_ATTACHMENT_89_1237.json"
sys.path.insert(0, str(HERE))
import diag3_pair_parent_boundary_attachment_core as core  # noqa: E402


EXPECTED_CERTIFICATE_SHA256 = "9d895a3786a16add585b8310613d98c08cada0be60a2a4cc830ea30a80a2bcbb"
EXPECTED_EVENTS_SHA256 = "211f60ef3a445c16e35cae40cba270ec5f552152dccc99a1abfbd4c0a84d1bf1"


class CertificateError(AssertionError):
    pass


def require(condition, message):
    if not condition:
        raise CertificateError(message)


def validate(record, expected):
    require(record == expected, "certificate differs from exact source replay")
    require((record["format"], record["status"]) == (core.FORMAT, core.STATUS), "format/status")
    scope = record["scope"]
    require((scope["parent_index"], scope["source_chart"]) == (2599, 89), "source scope")
    require(scope["target_parent_divisor"] == "[1237]=0", "target divisor")
    require(scope["global_parent_cell_coverage"] == "NOT_CLAIMED", "honest global scope")
    require(scope["signature_label_continuation"].startswith("OPEN_"), "honest label scope")

    selection = record["selection"]
    require(selection["stored_chart_count"] == 178, "stored chart census")
    require(selection["finite_coordinate_rays_per_chart"] == 9, "ray census")
    require(selection["parent_safe_single_divisor_rays"] == 29, "safe-ray census")
    require(selection["labelled_source_candidate_count"] == 1, "objective source choice")
    candidates = selection["parent_safe_ray_candidates"]
    require(len(candidates) == 29, "candidate list")
    require(Counter(row["boundary_parent_bracket"] for row in candidates) == {"1237": 29}, "candidate boundary labels")

    parent = record["parent_residence"]
    require(parent["parent_bracket_count"] == 70, "parent bracket census")
    require(parent["strict_on_open_ray"], "open-ray residence")
    require(parent["strict_at_endpoint_except_target"] == 69, "endpoint parent residence")
    require(parent["endpoint_parent_sign_census"] == {"positive": 69, "zero": 1}, "endpoint sign census")
    require(parent["target_boundary_is_genuine_parent_divisor"], "genuine divisor tag")
    divisor = parent["compactification_divisor_record"]
    require((divisor["moving_column"], divisor["coordinate_row"], divisor["parent_bracket"]) == (7, 4, "1237"), "divisor map")

    roadmap = record["residual_roadmap"]
    require(roadmap["candidate_factor_count"] == 17_824, "candidate factor census")
    require(roadmap["factor_root_count_census"] == {"0": 16_307, "1": 1_517}, "root census")
    require(roadmap["ordered_root_events"] == 1_517, "event census")
    require(roadmap["endpoint_zero_residual_factors"] == 0, "residual endpoint zeros")
    require(roadmap["events_semantic_sha256"] == EXPECTED_EVENTS_SHA256, "event digest")
    require(roadmap["all_root_boxes_pairwise_ordered"], "root ordering")
    require(roadmap["all_roots_simple_sign_crossings"], "simple crossing claim")
    events = roadmap["events"]
    require(len(events) == 1_517 and all(row["sign_flip"] for row in events), "event records")

    cw = record["regular_cw_path"]
    require(cw == {
        "zero_cells": 1_519,
        "one_cells": 1_518,
        "total_cells": 3_037,
        "strict_closure_pairs": 3_036,
        "scope_endpoint_cells": ["endpoint_chart_89", "endpoint_parent_divisor_1237"],
        "parent_infinity_subcomplex": ["endpoint_parent_divisor_1237"],
    }, "regular-CW path")
    require(record["overlap_with_labelled_0_89_path"]["compatibility"] == "EXACT_COMMON_SOURCE_VERTEX_AND_RAW_LABEL_SET", "source overlap")
    require("2/9" in record["theorem_effect"], "dishonest theorem score")
    return roadmap


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
    roadmap = validate(record, expected)

    hostile = []
    corrupt = copy.deepcopy(record); corrupt["scope"]["global_parent_cell_coverage"] = "COMPLETE"; hostile.append((corrupt, "local ray as global coverage"))
    corrupt = copy.deepcopy(record); corrupt["scope"]["signature_label_continuation"] = "COMPLETE"; hostile.append((corrupt, "unbuilt label continuation"))
    corrupt = copy.deepcopy(record); corrupt["selection"]["labelled_source_candidate_count"] = 2; hostile.append((corrupt, "nonobjective source choice"))
    corrupt = copy.deepcopy(record); corrupt["parent_residence"]["target_boundary_is_genuine_parent_divisor"] = False; hostile.append((corrupt, "artificial infinity"))
    corrupt = copy.deepcopy(record); corrupt["parent_residence"]["strict_at_endpoint_except_target"] = 68; hostile.append((corrupt, "extra parent wall"))
    corrupt = copy.deepcopy(record); corrupt["parent_residence"]["compactification_divisor_record"]["parent_bracket"] = "1238"; hostile.append((corrupt, "wrong divisor map"))
    corrupt = copy.deepcopy(record); corrupt["residual_roadmap"]["endpoint_zero_residual_factors"] = 1; hostile.append((corrupt, "hidden endpoint residual"))
    corrupt = copy.deepcopy(record); corrupt["residual_roadmap"]["events"].pop(); hostile.append((corrupt, "missing residual event"))
    corrupt = copy.deepcopy(record); corrupt["residual_roadmap"]["events_semantic_sha256"] = "0" * 64; hostile.append((corrupt, "wrong event digest"))
    corrupt = copy.deepcopy(record); corrupt["regular_cw_path"]["parent_infinity_subcomplex"] = []; hostile.append((corrupt, "lost relative endpoint"))
    corrupt = copy.deepcopy(record); corrupt["overlap_with_labelled_0_89_path"]["compatibility"] = "UNVERIFIED"; hostile.append((corrupt, "broken source gluing"))
    corrupt = copy.deepcopy(record); corrupt["inputs"]["compactification_atlas_sha256"] = "0" * 64; hostile.append((corrupt, "wrong atlas digest"))
    for corrupt, label in hostile:
        assert_rejected(corrupt, expected, label)

    print("PASS exact chart-89 to [1237]=0 parent-boundary attachment")
    print("PASS unique parent-safe boundary ray from the three labelled source charts")
    print("PASS 69 parent brackets remain positive and [1237] alone vanishes")
    print("PASS all 17,824 residual factors are nonzero at the parent endpoint")
    print("PASS 1,517 pairwise ordered simple residual crossings")
    print("EVENTS_SEMANTIC_SHA256", roadmap["events_semantic_sha256"])
    print("PASS 12/12 hostile corruptions rejected")
    print("SCOPE exact relative endpoint attachment only; global parent-cell coverage remains open")


if __name__ == "__main__":
    main()
