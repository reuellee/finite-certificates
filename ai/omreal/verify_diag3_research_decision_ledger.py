#!/usr/bin/env python3
"""Fail-closed audit of the canonical diagonal-three research decision ledger."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
DATA = HERE / "data"
LEDGER_PATH = DATA / "DIAG3_RESEARCH_DECISION_LEDGER.json"
COMPLETION_PATH = DATA / "DIAG3_COMPLETION_OPEN_OBJECT.json"
CLOSURE_PATH = DATA / "DIAG3_PAIR_GLOBAL_CLOSURE_OPEN_OBJECT.json"
POINTER = "ai/omreal/data/DIAG3_RESEARCH_DECISION_LEDGER.json"


def load(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def git_blob_sha1(path: Path) -> str:
    data = path.read_bytes()
    header = f"blob {len(data)}\0".encode("ascii")
    return hashlib.sha1(header + data).hexdigest()


def score(row: dict) -> int:
    return (
        4 * row["proof_criticality"]
        + 3 * row["branch_elimination"]
        + 2 * row["readiness"]
        + 2 * row["decisiveness"]
        - 2 * row["cost"]
        - 2 * row["failure_risk"]
    )


def assert_evidence_exists(record: object) -> None:
    if isinstance(record, dict):
        for key, value in record.items():
            if key in {"evidence", "regression"}:
                paths = value if isinstance(value, list) else [value]
                for path in paths:
                    target = HERE.parent.parent / path
                    if not target.is_file():
                        raise AssertionError(f"missing evidence path: {path}")
            else:
                assert_evidence_exists(value)
    elif isinstance(record, list):
        for value in record:
            assert_evidence_exists(value)


def main() -> None:
    ledger = load(LEDGER_PATH)
    completion = load(COMPLETION_PATH)
    closure = load(CLOSURE_PATH)

    assert ledger["format"] == "diag3-research-decision-ledger-v1"
    assert ledger["status"] == "ACTIVE"
    assert ledger["as_of"] == "2026-08-21"
    assert ledger["repository"] == {
        "full_name": "reuellee/finite-certificates",
        "default_branch": "main",
        "audited_commit": "e4ca567f829bd0e887e98efb05a3ed9437ba69d5",
        "merged_pull_request": 19,
    }
    assert ledger["theorem"]["score"] == completion["ledger_score"] == "2/9"
    assert ledger["theorem"]["proved_diagonals"] == [1, 2]
    assert ledger["theorem"]["active_diagonal"] == 3

    obligations = ledger["invariant_obligations"]
    assert [row["id"] for row in obligations] == [
        "diag3_triple_hc0",
        "diag3_pair_hc1",
    ]
    assert all(row["status"] == "OPEN" for row in obligations)
    triple = obligations[0]
    source = completion["triple_obligation"]
    assert (
        triple["universe_count"],
        triple["proved_noncompact_count"],
        triple["unresolved_count"],
    ) == (
        source["universe_count"],
        source["proved_noncompact_count"],
        source["unresolved_count"],
    ) == (79_102_449, 77_940_147, 1_162_302)
    assert triple["universe_count"] - triple["proved_noncompact_count"] == triple[
        "unresolved_count"
    ]

    pair = obligations[1]
    observations = closure["observations"]
    assert (
        pair["current_global_adjacencies"],
        pair["current_global_strict_closure_pairs"],
        pair["current_global_strict_closure_triples"],
        pair["current_parent_infinity_cells"],
    ) == (
        observations["certified_adjacency_edges_between_distinct_atlas_charts"],
        observations["certified_global_strict_closure_pairs"],
        observations["certified_global_strict_closure_triples"],
        observations["certified_parent_infinity_cells"],
    ) == (0, 0, 0, 0)

    full = ledger["row2599_fullsupport_ledger"]
    assert full["support_count"] == 3_375
    assert full["proper_relative_support_count"] == 3_374
    assert full["possible_nonrelative_supports"] == [[15, 15, 15]]
    assert (
        full["relative_boundary_mixed_restriction_count"]
        + full["fullsupport_factor_count"]
        == full["parent_face_mixed_restriction_count"]
        == closure["global_generator_preflight"][
            "remaining_mixed_residual_restriction_count"
        ]
        == 70_218
    )
    assert (
        full["exact_interior_nonempty_count"]
        + full["exact_empty_count"]
        + full["unresolved_feasibility_count"]
        == full["fullsupport_factor_count"]
        == 17_824
    )
    assert (
        full["exact_interior_nonempty_count"] + full["unresolved_feasibility_count"]
        == full["master_generator_active_wall_upper_bound"]
        == 16_647
    )
    assert full["digests"]["empty_factor_ids"] == (
        "f9022c922d56c69ea541d6098cea89004bdfcff73b01a411a159a78b5c369484"
    )
    assert full["digests"]["unresolved_factor_ids"] == (
        "0c85f0e7370963df311a5a7d04e175e4a801b79c54fe0600a69bb777bf30a76a"
    )
    assert full["digests"]["relative_boundary_collapse"] == (
        "65b425e0a9507dd536b59e770f3c43f5eb025381b2ca2e75eb009e93d022b02a"
    )

    retired = {row["id"]: row for row in ledger["retired_or_subordinated_targets"]}
    assert retired["proper_support_dimension4_subdivision"]["status"] == "RETIRED"
    assert retired["common_normalized_coordinate_scaling"] == {
        "id": "common_normalized_coordinate_scaling",
        "status": "RETIRED",
        "reason": "Every one of the 1162302 final-residue exponent-difference systems has rank nine already over F2, so no nonzero common diagonal weight exists.",
        "regression": "ai/omreal/verify_diag3_triple_common_scaling_no_go.py",
    }
    assert retired["universal_quadratic_ideal_preserving_flow"] == {
        "id": "universal_quadratic_ideal_preserving_flow",
        "status": "RETIRED",
        "reason": "Five pinned hard triples give full-rank 585-column systems for arbitrary quadratic vector fields with affine-linear ideal multipliers.",
        "regression": "ai/omreal/verify_diag3_triple_quadratic_ideal_flow_no_go.py",
    }
    assert retired["moving_column_s3_quotient"]["withdrawn_counts"] == {
        "transported_witnesses": 5_986,
        "residue_factors": 994,
        "quotient_classes": 264,
        "failed_nonidentity_segment_transports": 525,
    }
    assert retired["standalone_degree_one_positive_multiplier_screen"][
        "status"
    ] == "SUBORDINATED"
    assert closure["global_generator_preflight"]["status"] == (
        "PARENT_FACE_GATE_READY_DIMENSION4_SUBDIVISION_MISSING"
    )

    candidates = ledger["candidate_targets"]
    assert len({row["id"] for row in candidates}) == len(candidates)
    for row in candidates:
        assert all(0 <= row[key] <= 5 for key in (
            "proof_criticality",
            "branch_elimination",
            "readiness",
            "decisiveness",
            "cost",
            "failure_risk",
        ))
        assert row["priority_score"] == score(row)
    selected = [row for row in candidates if row["selected"]]
    assert len(selected) == 1
    assert selected[0]["id"] == ledger["selected_target"]
    assert selected[0]["priority_score"] == max(
        row["priority_score"] for row in candidates
    )
    assert ledger["selected_target"] == "fullsupport_master_closure_compiler"
    progress = ledger["selected_target_progress"]
    assert progress["schema_interface"] == "COMPLETE"
    canary = progress["first_proof_producing_canary"]
    assert canary == {
        "status": "PROVED",
        "scope": "one exact two-dimensional full-support disk in row 2599",
        "regular_cw_cells": 17,
        "vertices": 5,
        "edges": 8,
        "chambers": 4,
        "labelled_residual_occurrences_replayed": 84_840,
        "parent_brackets_replayed": 70,
        "extension_signatures_accounted": 97_224,
        "ordered_profile_triples_replayed": 216,
        "nonexact_profile_triples_with_scope_boundary_ordinary": 0,
        "parent_infinity_cells": 0,
        "hostile_corruptions_rejected": 7,
        "evidence": [
            "ai/omreal/DIAG3_PAIR_MASTER_CLOSURE_NODE_CANARY.md",
            "ai/omreal/data/DIAG3_PAIR_MASTER_CLOSURE_NODE_CANARY.json",
            "ai/omreal/verify_diag3_pair_master_closure_node_canary.py",
        ],
    }
    multibox = progress["second_multibox_canary"]
    assert multibox == {
        "status": "PROVED",
        "scope": "one exact 3x3 two-dimensional full-support atlas inside the row-2599 transverse-node disk",
        "boxes": 9,
        "no_wall_boxes": 4,
        "one_wall_boxes": 4,
        "transverse_two_wall_boxes": 1,
        "unclassified_boxes": 0,
        "atomic_boundary_word_segments": 32,
        "shared_boundary_segments_glued": 16,
        "regular_cw_cells": 81,
        "vertices": 25,
        "edges": 40,
        "chambers": 16,
        "barycentric_vertices": 81,
        "barycentric_edges": 208,
        "barycentric_triangles": 128,
        "labelled_residual_occurrences_replayed": 84_840,
        "parent_brackets_replayed": 70,
        "extension_signatures_accounted": 97_224,
        "ordered_profile_triples_replayed": 216,
        "nonexact_profile_triples_with_scope_boundary_ordinary": 0,
        "parent_infinity_cells": 0,
        "hostile_corruptions_rejected": 10,
        "evidence": [
            "ai/omreal/DIAG3_PAIR_MASTER_CLOSURE_MULTIBOX_CANARY.md",
            "ai/omreal/data/DIAG3_PAIR_MASTER_CLOSURE_MULTIBOX_CANARY.json",
            "ai/omreal/verify_diag3_pair_master_closure_multibox_canary.py",
        ],
    }
    first_event = progress["third_first_new_event_atlas"]
    assert first_event == {
        "status": "PROVED",
        "scope": "one exact 64-box two-dimensional full-support atlas crossing the first new residual event in the row-2599 parent plane",
        "boxes": 64,
        "no_wall_boxes": 42,
        "one_wall_boxes": 20,
        "transverse_two_wall_boxes": 2,
        "unclassified_boxes": 0,
        "first_new_event_derived_rows": [2, 8, 22, 49],
        "atomic_boundary_word_segments": 171,
        "shared_boundary_segments_glued": 133,
        "regular_cw_cells": 399,
        "vertices": 110,
        "edges": 199,
        "chambers": 90,
        "barycentric_vertices": 399,
        "barycentric_edges": 1118,
        "barycentric_triangles": 720,
        "labelled_residual_occurrences_replayed": 84_840,
        "parent_brackets_replayed": 70,
        "extension_signatures_accounted": 97_224,
        "signature_profile_count": 8,
        "ordered_profile_triples_replayed": 512,
        "nonexact_profile_triples_with_scope_boundary_ordinary": 0,
        "parent_infinity_cells": 0,
        "hostile_corruptions_rejected": 13,
        "rank_semantic_sha256": "48140daf03371353de766d719e3812219b4612fce87bdeb8b2efc67ed50e7d06",
        "evidence": [
            "ai/omreal/DIAG3_PAIR_MASTER_CLOSURE_FIRST_EVENT.md",
            "ai/omreal/data/DIAG3_PAIR_MASTER_CLOSURE_FIRST_EVENT.json",
            "ai/omreal/verify_diag3_pair_master_closure_first_event.py",
        ],
    }
    source_transition = progress["fourth_parent_source_transition"]
    assert source_transition == {
        "status": "PROVED",
        "scope": "one exact parent-resident straight segment from row-2599 chart 0 to distinct chart 89",
        "selection_rule": "minimum exact factor-state Hamming distance among the 57 certified parent-safe chart-zero segments",
        "endpoint_factor_hamming_distance": 1197,
        "parent_brackets_replayed": 70,
        "candidate_factors_replayed": 17_824,
        "root_free_factors": 16_607,
        "one_root_factors": 1_197,
        "two_root_factors": 20,
        "rooted_factors": 1_217,
        "ordered_root_events": 1_237,
        "simple_single_occurrence_events": 1_179,
        "compound_events": 58,
        "occurrence_multiplicity_census": {"1": 1_179, "2": 13, "15": 6, "65": 39},
        "regular_cw_cells": 2_477,
        "strict_closure_pairs": 2_476,
        "parent_infinity_cells": 0,
        "first_compound_event_index": 38,
        "first_compound_factor_id": 8_652,
        "events_semantic_sha256": "19683a1b46c3dab4f51b770cd7af9237b3c323b7c8f6d0a3d4101a13d890472b",
        "factor_state_sequence_sha256": "68fe63818b53e20a51ca7b4580acfad399a40aa4052bea51f43595a49999e9b4",
        "hostile_corruptions_rejected": 9,
        "evidence": [
            "ai/omreal/DIAG3_PAIR_PARENT_SOURCE_TRANSITION.md",
            "ai/omreal/data/DIAG3_PAIR_PARENT_SOURCE_TRANSITION_0_89.json",
            "ai/omreal/verify_diag3_pair_parent_source_transition.py",
        ],
    }
    source_labels = progress["fifth_parent_source_label_continuation"]
    assert source_labels == {
        "status": "PROVED",
        "scope": "complete exact signature-label continuation over all open chambers of the row-2599 chart-0-to-chart-89 path",
        "generic_chambers": 1_238,
        "extension_signature_universe": 97_224,
        "labels_per_generic_chamber": 26_112,
        "simple_simplicial_mutations": 1_179,
        "compound_exact_reenumerations": 58,
        "compound_delta_census": {
            "multiplicity_2_lost_gained_4": 13,
            "multiplicity_15_lost_gained_10": 6,
            "multiplicity_65_lost_gained_72": 39,
        },
        "distinct_signature_profiles": 2_458,
        "profile_transition_count_census": {"0": 87_208, "1": 9_490, "2": 512, "3": 14},
        "never_feasible_signatures": 66_000,
        "all_chamber_persistent_signatures": 21_208,
        "raw_chart_89_label_state_reconstructed": True,
        "chamber_label_digests_sha256": "40c9198f55b4fedf27918aeb908bf79f86ad264302599479b881b8f7828d6ce9",
        "event_label_semantic_sha256": "05dc4bca07c35faf568cc65898ba798a72b3150a47fcd92e766b4f8c1f4e6c05",
        "profile_semantic_sha256": "b201f42b71aa32ac92f790f1419a3e542e1f9e890869664bbac6b4014ce9a4d3",
        "hostile_corruptions_rejected": 10,
        "evidence": [
            "ai/omreal/DIAG3_PAIR_PARENT_SOURCE_LABELS.md",
            "ai/omreal/data/DIAG3_PAIR_PARENT_SOURCE_LABELS_0_89.json",
            "ai/omreal/verify_diag3_pair_parent_source_labels.py",
        ],
    }
    block_bridge = progress["sixth_parent_source_block_bridge"]
    assert block_bridge == {
        "status": "PROVED",
        "scope": "one exact three-segment one-column-at-a-time bridge from row-2599 chart 0 to formerly straight-isolated chart 152",
        "straight_edges_audited": 105,
        "straight_component_census": {"1": 71, "2": 1, "105": 1},
        "direct_block_bridge_candidates": 6,
        "selection_rule": "minimum certified one-column segment count, then minimum endpoint factor-state Hamming distance, then target chart index",
        "selected_target_chart": 152,
        "selected_block_order": [0, 1, 2],
        "endpoint_factor_hamming_distance": 3_384,
        "parent_brackets_replayed": 70,
        "generic_waypoints": 4,
        "candidate_factor_segment_restrictions": 53_472,
        "ordered_root_events": 5_612,
        "occurrence_multiplicity_census": {"1": 5_319, "2": 66, "15": 46, "65": 181},
        "regular_cw_cells": 11_231,
        "strict_closure_pairs": 11_230,
        "parent_infinity_cells": 0,
        "shared_chart_zero_labels": 26_112,
        "events_semantic_sha256": "7a80560cfc7544f1d114b33c2c9205d35a09400d6385029f2a93e05fe6f50102",
        "factor_state_sequence_sha256": "f64480d5b7138a7f92e440b5daa93f2c7e14598aca1be9a607e550bcda6c74aa",
        "hostile_corruptions_rejected": 12,
        "evidence": [
            "ai/omreal/DIAG3_PAIR_PARENT_SOURCE_BLOCK_BRIDGE.md",
            "ai/omreal/data/DIAG3_PAIR_PARENT_SOURCE_BLOCK_BRIDGE_0_152.json",
            "ai/omreal/verify_diag3_pair_parent_source_block_bridge.py",
        ],
    }
    block_labels = progress["seventh_parent_source_block_label_continuation"]
    assert block_labels == {
        "status": "PROVED",
        "scope": "complete exact signature-label continuation over all open chambers of the three-segment row-2599 chart-0-to-chart-152 block bridge",
        "generic_chambers": 5_615,
        "extension_signature_universe": 97_224,
        "labels_per_generic_chamber": 26_112,
        "simple_simplicial_mutations": 5_319,
        "compound_exact_reenumerations": 293,
        "compound_delta_census": {
            "multiplicity_2_lost_gained_4": 66,
            "multiplicity_15_lost_gained_10": 46,
            "multiplicity_65_lost_gained_72": 181,
        },
        "internal_equal_label_waypoints": 2,
        "distinct_signature_profiles": 9_326,
        "profile_transition_count_census": {
            "0": 62_080,
            "1": 23_496,
            "2": 9_914,
            "3": 1_486,
            "4": 234,
            "5": 14,
        },
        "never_feasible_signatures": 51_114,
        "all_chamber_persistent_signatures": 10_966,
        "raw_chart_152_label_state_reconstructed": True,
        "chamber_label_digests_sha256": "e0657cdf67205ffbc0f8a15ecbf98b6fabe4861e397bb85588651fa0cc585875",
        "event_label_semantic_sha256": "e65b6cc7cccf07fb66b590ef6a86fec947f51c2bdcf8c8974cd04be30b6f58b6",
        "profile_semantic_sha256": "b6aa84e62805531e4f32ed63ba5a389011ff607288bfbec4ce64b0394731a796",
        "hostile_corruptions_rejected": 12,
        "evidence": [
            "ai/omreal/DIAG3_PAIR_PARENT_SOURCE_BLOCK_LABELS.md",
            "ai/omreal/data/DIAG3_PAIR_PARENT_SOURCE_BLOCK_LABELS_0_152.json",
            "ai/omreal/verify_diag3_pair_parent_source_block_labels.py",
        ],
    }
    boundary = progress["eighth_parent_boundary_attachment"]
    assert boundary == {
        "status": "PROVED",
        "scope": "exact fully labelled row-2599 chart-89 coordinate ray to the genuine relative parent divisor [1237]=0",
        "stored_coordinate_rays_audited": 1_602,
        "parent_safe_single_divisor_rays": 29,
        "labelled_source_candidate_rays": 1,
        "source_chart": 89,
        "moving_column": 7,
        "coordinate_row": 4,
        "target_parent_bracket": "1237",
        "parent_brackets_replayed": 70,
        "strict_parent_brackets_at_endpoint": 69,
        "candidate_factors_replayed": 17_824,
        "root_free_factors": 16_307,
        "one_root_factors": 1_517,
        "endpoint_zero_residual_factors": 0,
        "ordered_root_events": 1_517,
        "occurrence_multiplicity_census": {"1": 1_454, "2": 16, "15": 6, "65": 41},
        "regular_cw_cells": 3_037,
        "strict_closure_pairs": 3_036,
        "parent_infinity_cells": 1,
        "generic_chambers": 1_518,
        "labels_per_generic_chamber": 26_112,
        "simple_simplicial_mutations": 1_454,
        "compound_exact_reenumerations": 63,
        "distinct_signature_profiles": 3_029,
        "profile_transition_count_census": {"0": 85_452, "1": 11_576, "2": 196},
        "never_feasible_signatures": 65_128,
        "all_chamber_persistent_signatures": 20_324,
        "last_open_chamber_reconstructed": True,
        "events_semantic_sha256": "211f60ef3a445c16e35cae40cba270ec5f552152dccc99a1abfbd4c0a84d1bf1",
        "event_label_semantic_sha256": "5ce4cd3124c42e8d64e032acaa2e5047c9a6319c0535c1d2607ff58ec08b4812",
        "profile_semantic_sha256": "102a36f099781ba36f8df85c4a042e5bceb72d0abc08be84bcbf8a32fcbf3778",
        "hostile_corruptions_rejected": 24,
        "evidence": [
            "ai/omreal/DIAG3_PAIR_PARENT_BOUNDARY_ATTACHMENT.md",
            "ai/omreal/data/DIAG3_PAIR_PARENT_BOUNDARY_ATTACHMENT_89_1237.json",
            "ai/omreal/verify_diag3_pair_parent_boundary_attachment.py",
            "ai/omreal/data/DIAG3_PAIR_PARENT_BOUNDARY_LABELS_89_1237.json",
            "ai/omreal/verify_diag3_pair_parent_boundary_labels.py",
        ],
    }
    scaling = progress["ninth_triple_escape_language_audit"]
    assert scaling == {
        "status": "PROVED_NO_GO",
        "scope": "exhaustive common diagonal-scaling audit on the final triple residue plus a bounded low-degree ideal-flow regression on five hard triples",
        "final_residue_rows": 1_162_302,
        "final_residue_sha256": "34eee303b7981594805958f5dda79058880af66b54f685035ff9c16ee0073cd9",
        "factor_exponent_rank_census": {
            "1": 330,
            "3": 936,
            "4": 3_600,
            "5": 2_448,
            "6": 6_240,
            "7": 4_944,
            "8": 4_912,
            "9": 3_330,
        },
        "full_common_weight_rank_over_f2": 1_162_302,
        "nontrivial_common_scalings": 0,
        "common_scaling_semantic_sha256": "d83b42d9a5bd05536829e75e3dd507efa8c2855962a18eed85080c7048e63b9e",
        "hard_ideal_flow_triples": 5,
        "quadratic_vector_field_unknowns": 495,
        "affine_multiplier_unknowns": 90,
        "hard_system_rank_census": {"585": 5},
        "quadratic_ideal_flow_semantic_sha256": "c5eb24d2f574e65d848f5238d895fc38fc7baaa2a84ec6c3bed402d49bda51a0",
        "theorem_effect": "Retires two escape languages without reducing the 1162302-row residue; honest 9DVL score remains 2/9.",
        "evidence": [
            "ai/omreal/DIAG3_TRIPLE_COMMON_SCALING_NO_GO.md",
            "ai/omreal/verify_diag3_triple_common_scaling_no_go.py",
            "ai/omreal/verify_diag3_triple_quadratic_ideal_flow_no_go.py",
        ],
    }
    assert progress["theorem_effect"] == (
        "No invariant diagonal-three obligation is closed; honest 9DVL score remains 2/9."
    )
    assert progress["next_stage"].startswith(
        "prove missed-component coverage for the exact labelled source-boundary skeleton"
    )

    digest = git_blob_sha1(LEDGER_PATH)
    for historical in (completion, closure):
        assert historical["current_decision_ledger"] == POINTER
        assert historical["current_decision_ledger_git_blob"] == digest

    assert ledger["process_gates"] == {
        "canonical_state_first": True,
        "independent_verifier_required": True,
        "negative_canary_required": True,
        "exact_scope_labels_required": True,
        "default_branch_and_drive_checkpoint_required_at_cycle_end": True,
        "theorem_score_promotion_requires_all_invariant_obligations_closed": True,
    }
    assert_evidence_exists(ledger)
    print("PASS canonical diagonal-three research decision ledger")
    print("PASS invariant obligations remain open; honest ledger 2/9")
    print(
        "PASS row2599 full support:",
        "10844 interior + 1177 empty + 5803 unresolved = 17824",
    )
    print(
        "SELECTED fullsupport_master_closure_compiler score",
        selected[0]["priority_score"],
    )
    print("PASS first proof-producing master-closure canary: 17 cells / 216 ranks")
    print("PASS second multi-box master-closure canary: 9 boxes / 81 cells / 216 ranks")
    print("PASS third first-event master-closure atlas: 64 boxes / 399 cells / 512 ranks")
    print("PASS fourth parent-source transition: 1237 events / 2477 cells / 58 compound")
    print("PASS fifth source-label continuation: 1238 chambers / 2458 profiles / exact endpoint")
    print("PASS sixth source block bridge: 3 segments / 5612 events / 11231 cells")
    print("PASS ninth triple escape-language audit: 1162302 scaling no-gos / 5 ideal-flow no-gos")
    print("LEDGER_GIT_BLOB", digest)


if __name__ == "__main__":
    main()
