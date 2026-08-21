#!/usr/bin/env python3
"""Hostile exact replay of row-2599 chart-0-to-chart-89 label continuation."""

from __future__ import annotations

from collections import Counter
import copy
import json
from pathlib import Path
import sys


HERE = Path(__file__).resolve().parent
CERTIFICATE = HERE / "data" / "DIAG3_PAIR_PARENT_SOURCE_LABELS_0_89.json"
sys.path.insert(0, str(HERE))
import diag3_pair_parent_source_labels_core as core  # noqa: E402


EXPECTED_TRANSITION_SHA256 = "87f2d7ce337651cea498cc50d36c1b53c8b2294aef54ceac89f0fcc552c7b2d2"
EXPECTED_CHAMBER_SHA256 = "40c9198f55b4fedf27918aeb908bf79f86ad264302599479b881b8f7828d6ce9"
EXPECTED_EVENT_SHA256 = "05dc4bca07c35faf568cc65898ba798a72b3150a47fcd92e766b4f8c1f4e6c05"
EXPECTED_PROFILE_SHA256 = "b201f42b71aa32ac92f790f1419a3e542e1f9e890869664bbac6b4014ce9a4d3"


class CertificateError(AssertionError):
    pass


def require(condition, message):
    if not condition:
        raise CertificateError(message)


def validate(record, expected):
    require(record == expected, "certificate differs from exact source replay")
    require(record["format"] == core.FORMAT and record["status"] == core.STATUS, "format/status")
    scope = record["scope"]
    require((scope["parent_index"], scope["source_chart"], scope["target_chart"]) == (2599, 0, 89), "path scope")
    require(scope["generic_chambers"] == 1238, "chamber census")
    require(scope["signature_label_continuation"] == "COMPLETE_ON_ALL_OPEN_PATH_CHAMBERS", "label coverage")
    require(scope["global_parent_cell_coverage"] == "NOT_CLAIMED", "honest global scope")
    require(record["inputs"]["transition_certificate_sha256"] == EXPECTED_TRANSITION_SHA256, "transition certificate digest")
    require(core.file_sha256(core.TRANSITION) == EXPECTED_TRANSITION_SHA256, "live transition digest")

    normalization = record["normalization"]
    require(normalization["raw_extension_reorientation_mask"] == core.EXPECTED_REORIENTATION_MASK, "reorientation mask")
    require(normalization["mask_row_indices"] == [0, 2, 5, 8, 11, 14, 17, 19, 21, 24, 27, 29, 31, 33, 34, 36, 39, 42, 44, 46, 48, 49, 51, 53, 54, 55], "reorientation rows")
    require(normalization["source_raw_normalized_label_sets_equal_after_reorientation"], "source normalization")

    continuation = record["continuation"]
    require(continuation["extension_signature_universe"] == 97224, "extension universe")
    require(continuation["labels_per_generic_chamber"] == 26112, "generic label census")
    require(continuation["ordered_events"] == 1237, "ordered events")
    require(continuation["simple_mutation_events"] == 1179, "simple events")
    require(continuation["compound_reenumeration_events"] == 58, "compound events")
    require(continuation["simple_preliminary_candidate_census"] == {"2": 771, "4": 224, "6": 122, "8": 34, "10": 16, "12": 11, "14": 1}, "simple candidate census")
    require(continuation["compound_delta_census"] == {
        "multiplicity_2:lost_4:gained_4": 13,
        "multiplicity_15:lost_10:gained_10": 6,
        "multiplicity_65:lost_72:gained_72": 39,
    }, "compound delta census")
    require(continuation["chart_89_raw_label_state_reconstructed"], "target reconstruction")
    require(continuation["chamber_label_digests_sha256"] == EXPECTED_CHAMBER_SHA256, "chamber digest")
    require(continuation["event_label_semantic_sha256"] == EXPECTED_EVENT_SHA256, "event digest")
    events = continuation["event_records"]
    require(len(events) == 1237 and [row["event_index"] for row in events] == list(range(1237)), "event records")
    require(Counter(row["method"] for row in events) == {"simplicial_basis_mutation": 1179, "exact_post_compound_tope_reenumeration": 58}, "continuation methods")
    require(all((row["lost_labels"], row["gained_labels"]) == (2, 2) for row in events if row["method"] == "simplicial_basis_mutation"), "ordinary mutation delta")
    expected_delta = {2: 4, 15: 10, 65: 72}
    require(all(row["lost_labels"] == row["gained_labels"] == expected_delta[row["occurrence_multiplicity"]] for row in events if row["method"] != "simplicial_basis_mutation"), "compound mutation delta")
    require(events[38]["factor_id"] == 8652 and events[38]["lost_labels"] == events[38]["gained_labels"] == 72, "first compound mutation")

    profiles = record["signature_profiles"]
    require(profiles["packed_profile_bytes_each"] == 155, "packed profile width")
    require(profiles["distinct_profiles"] == 2458, "profile census")
    require(profiles["semantic_sha256"] == EXPECTED_PROFILE_SHA256, "profile digest")
    require(sum(profiles["feasible_chamber_count_census"].values()) == 97224, "profile accounting")
    require(profiles["feasible_chamber_count_census"]["0"] == 66000, "never-feasible signatures")
    require(profiles["feasible_chamber_count_census"]["1238"] == 21208, "persistent signatures")
    require(profiles["profile_transition_count_census"] == {"0": 87208, "1": 9490, "2": 512, "3": 14}, "profile transition census")
    require(profiles["all_bad_loci_closed_by_incidence_rule"], "bad-locus closure")
    require("2/9" in record["theorem_effect"], "dishonest theorem score")
    return continuation, profiles


def assert_rejected(record, expected, label):
    try:
        validate(record, expected)
    except (CertificateError, KeyError, ValueError, TypeError):
        return
    raise AssertionError(f"hostile canary was accepted: {label}")


def main():
    record = json.loads(CERTIFICATE.read_text(encoding="utf-8"))
    expected = core.build_record(progress=True)
    continuation, profiles = validate(record, expected)

    hostile = []
    corrupt = copy.deepcopy(record)
    corrupt["scope"]["global_parent_cell_coverage"] = "COMPLETE"
    hostile.append((corrupt, "one path as global coverage"))
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
    corrupt["continuation"]["event_records"][38]["gained_labels"] = 71
    hostile.append((corrupt, "unbalanced compound mutation"))
    corrupt = copy.deepcopy(record)
    corrupt["continuation"]["simple_mutation_events"] -= 1
    hostile.append((corrupt, "corrupt simple-event census"))
    corrupt = copy.deepcopy(record)
    corrupt["continuation"]["chart_89_raw_label_state_reconstructed"] = False
    hostile.append((corrupt, "failed endpoint presented as complete"))
    corrupt = copy.deepcopy(record)
    corrupt["signature_profiles"]["distinct_profiles"] -= 1
    hostile.append((corrupt, "corrupt profile census"))
    corrupt = copy.deepcopy(record)
    corrupt["signature_profiles"]["profile_transition_count_census"]["3"] -= 1
    hostile.append((corrupt, "corrupt profile transitions"))
    corrupt = copy.deepcopy(record)
    corrupt["signature_profiles"]["semantic_sha256"] = "0" * 64
    hostile.append((corrupt, "corrupt profile digest"))
    for corrupt, label in hostile:
        assert_rejected(corrupt, expected, label)

    print("PASS exact row-2599 chart-0-to-chart-89 label continuation")
    print("PASS 1,179 antipodal simplicial mutations + 58 exact compound updates")
    print("PASS every one of 1,238 chambers has 26,112 labels in the 97,224-signature universe")
    print("PASS compound deltas: 13x4 + 6x10 + 39x72 labels each way")
    print("PASS continued endpoint equals the independently stored raw chart-89 tope state")
    print("PASS 2,458 exact profiles; transition census 87,208/9,490/512/14")
    print("PROFILE_SEMANTIC_SHA256", profiles["semantic_sha256"])
    print("EVENT_LABEL_SEMANTIC_SHA256", continuation["event_label_semantic_sha256"])
    print("PASS 10/10 hostile corruptions rejected")
    print("SCOPE complete on one exact source path; global parent-cell coverage remains open")


if __name__ == "__main__":
    main()
