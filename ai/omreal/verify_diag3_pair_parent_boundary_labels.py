#!/usr/bin/env python3
"""Hostile exact replay of labels on the chart-89 boundary attachment."""

from __future__ import annotations

from collections import Counter
import copy
import hashlib
import json
from pathlib import Path
import sys


HERE = Path(__file__).resolve().parent
CERTIFICATE = HERE / "data" / "DIAG3_PAIR_PARENT_BOUNDARY_LABELS_89_1237.json"
sys.path.insert(0, str(HERE))
import diag3_pair_parent_boundary_labels_core as core  # noqa: E402


EXPECTED_CERTIFICATE_SHA256 = "dfff5b35f2ad6080449b0979250884207587e51fca710dbae08a972b6eb169be"
EXPECTED_PROFILE_SHA256 = "102a36f099781ba36f8df85c4a042e5bceb72d0abc08be84bcbf8a32fcbf3778"
EXPECTED_EVENT_LABEL_SHA256 = "5ce4cd3124c42e8d64e032acaa2e5047c9a6319c0535c1d2607ff58ec08b4812"


class CertificateError(AssertionError):
    pass


def require(condition, message):
    if not condition:
        raise CertificateError(message)


def validate(record, expected):
    require(record == expected, "certificate differs from exact source replay")
    require((record["format"], record["status"]) == (core.FORMAT, core.STATUS), "format/status")
    scope = record["scope"]
    require((scope["parent_index"], scope["source_chart"], scope["target_parent_divisor"]) == (2599, 89, "[1237]=0"), "path scope")
    require(scope["generic_chambers"] == 1_518, "chamber census")
    require(scope["signature_label_continuation"] == "COMPLETE_ON_ALL_OPEN_RAY_CHAMBERS", "label coverage")
    require(scope["relative_endpoint_rule"] == "PARENT_DIVISOR_CELL_EXCLUDED_FROM_RELATIVE_CHAINS", "relative endpoint")
    require(scope["global_parent_cell_coverage"] == "NOT_CLAIMED", "honest global scope")

    continuation = record["continuation"]
    require(continuation["extension_signature_universe"] == 97_224, "extension universe")
    require(continuation["labels_per_generic_chamber"] == 26_112, "label census")
    require(continuation["ordered_events"] == 1_517, "event census")
    require(continuation["simple_mutation_events"] == 1_454, "simple mutations")
    require(continuation["compound_reenumeration_events"] == 63, "compound updates")
    require(continuation["last_open_chamber_reconstructed_by_independent_endpoint_near_reenumeration"], "last-chamber reconstruction")
    require(continuation["event_label_semantic_sha256"] == EXPECTED_EVENT_LABEL_SHA256, "event-label digest")
    events = continuation["event_records"]
    require(len(events) == 1_517 and [row["event_index"] for row in events] == list(range(1_517)), "event records")
    require(Counter(row["method"] for row in events) == {
        "simplicial_basis_mutation": 1_454,
        "exact_post_compound_tope_reenumeration": 63,
    }, "continuation methods")
    require(all((row["lost_labels"], row["gained_labels"]) == (2, 2) for row in events if row["method"] == "simplicial_basis_mutation"), "ordinary mutation delta")
    require(all(row["lost_labels"] == row["gained_labels"] for row in events), "balanced label deltas")

    profiles = record["signature_profiles"]
    require(profiles["packed_profile_bytes_each"] == 190, "profile width")
    require(profiles["semantic_sha256"] == EXPECTED_PROFILE_SHA256, "profile digest")
    require(sum(profiles["feasible_chamber_count_census"].values()) == 97_224, "profile accounting")
    require(sum(profiles["profile_transition_count_census"].values()) == 97_224, "transition accounting")
    require(profiles["all_bad_loci_closed_by_incidence_rule"], "incidence closure")
    require(record["gluing"]["exact_common_source_vertex_and_label_set"], "chart-89 gluing")
    relative = record["relative_boundary"]
    require(relative["parent_infinity_subcomplex"] == ["endpoint_parent_divisor_1237"], "parent infinity")
    require(relative["endpoint_residual_factor_zeros"] == 0, "endpoint residual zeros")
    require(relative["endpoint_chain_generators_retained"] == 0, "relative quotient")
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
    corrupt = copy.deepcopy(record); corrupt["scope"]["global_parent_cell_coverage"] = "COMPLETE"; hostile.append((corrupt, "local boundary path as global coverage"))
    corrupt = copy.deepcopy(record); corrupt["scope"]["relative_endpoint_rule"] = "ORDINARY_CELL"; hostile.append((corrupt, "relative endpoint retained"))
    corrupt = copy.deepcopy(record); corrupt["normalization"]["raw_extension_reorientation_mask"] ^= 1; hostile.append((corrupt, "wrong reorientation"))
    corrupt = copy.deepcopy(record); corrupt["continuation"]["event_records"].pop(); hostile.append((corrupt, "missing label event"))
    corrupt = copy.deepcopy(record); corrupt["continuation"]["event_records"][0]["lost_labels"] = 1; hostile.append((corrupt, "non-antipodal mutation"))
    corrupt = copy.deepcopy(record); corrupt["continuation"]["compound_reenumeration_events"] -= 1; hostile.append((corrupt, "compound census"))
    corrupt = copy.deepcopy(record); corrupt["continuation"]["last_open_chamber_reconstructed_by_independent_endpoint_near_reenumeration"] = False; hostile.append((corrupt, "unverified last chamber"))
    corrupt = copy.deepcopy(record); corrupt["signature_profiles"]["distinct_profiles"] -= 1; hostile.append((corrupt, "profile census"))
    corrupt = copy.deepcopy(record); corrupt["signature_profiles"]["semantic_sha256"] = "0" * 64; hostile.append((corrupt, "profile digest"))
    corrupt = copy.deepcopy(record); corrupt["gluing"]["exact_common_source_vertex_and_label_set"] = False; hostile.append((corrupt, "broken source gluing"))
    corrupt = copy.deepcopy(record); corrupt["relative_boundary"]["parent_infinity_subcomplex"] = []; hostile.append((corrupt, "lost parent infinity"))
    corrupt = copy.deepcopy(record); corrupt["relative_boundary"]["endpoint_residual_factor_zeros"] = 1; hostile.append((corrupt, "hidden residual endpoint wall"))
    for corrupt, label in hostile:
        assert_rejected(corrupt, expected, label)

    print("PASS exact labels on chart-89 to [1237]=0 boundary attachment")
    print("PASS 1,454 antipodal simplicial mutations + 63 exact compound updates")
    print("PASS every one of 1,518 open-ray chambers has 26,112 labels")
    print("PASS final open chamber equals an independent endpoint-near reenumeration")
    print("PASS [1237]=0 endpoint is correctly quotiented as genuine parent infinity")
    print("PROFILE_SEMANTIC_SHA256", profiles["semantic_sha256"])
    print("EVENT_LABEL_SEMANTIC_SHA256", continuation["event_label_semantic_sha256"])
    print("PASS 12/12 hostile corruptions rejected")
    print("SCOPE complete on the exact relative boundary path; global parent-cell coverage remains open")


if __name__ == "__main__":
    main()
