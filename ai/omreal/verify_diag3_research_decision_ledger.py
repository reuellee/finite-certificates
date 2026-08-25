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
    assert ledger["as_of"] == "2026-08-25"
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
    assert retired["full_sign_invariant_source_square_arrangement"] == {
        "id": "full_sign_invariant_source_square_arrangement",
        "status": "SUBORDINATED",
        "reason": "Two disjoint exact boundary-order families already force 618120 intersecting curve pairs on the chart-0-to-chart-152 source square; full sign-arrangement materialization is not needed for missed-component coverage.",
        "replacement": "component-coverage quotient certified by exact Bernstein feasibility and projection-discriminant replay",
        "regression": "ai/omreal/verify_diag3_pair_source_square_coverage.py",
    }
    assert retired["naive_full_source_block_cube"] == {
        "id": "naive_full_source_block_cube",
        "status": "RETIRED",
        "reason": "Two of eight chart-0/chart-152 hybrid block vertices leave the signed row-2599 parent cell: (0,0,1) fails [1268], while (0,1,1) fails [1268] and [5678].",
        "replacement": "the exact parent-safe [1/2,1] x [0,1] x [0,1] block half-cube",
        "regression": "ai/omreal/verify_diag3_pair_source_block_cube_feasibility.py",
    }
    assert retired["universal_chart0_chart152_source_family_incidence"] == {
        "id": "universal_chart0_chart152_source_family_incidence",
        "status": "RETIRED",
        "reason": "Exactly 5390 factors with certified row-2599 parent-interior sign crossings are zero-free on the entire chart-0/chart-152 three-parameter source cube, so no refinement confined to that cube can meet every global wall.",
        "replacement": "genuinely distinct source families with a global incidence theorem, or a direct coverage-certified parent-cell roadmap/master complex",
        "regression": "ai/omreal/verify_diag3_pair_source_family_incidence_no_go.py",
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
        "FOUR_SUPPORT_1665_SECTIONS_LIFTED_28_ALGEBRAIC_SECTIONS_MISSING"
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
    infrastructure = ledger["research_infrastructure"]["exact_semialgebraic_toolkit"]
    assert infrastructure == {
        "status": "EXTRACTED_AND_CANARY_VERIFIED",
        "arithmetic": "EXACT_RATIONAL",
        "decision_policy": "FAIL_CLOSED",
        "parameter_dimension": "ARBITRARY_POSITIVE_DIMENSION",
        "analytic_canaries": 8,
        "hostile_semantic_mutations_rejected": 10,
        "compact_component_negative_canary": "INTERIOR_SPHERES_REFUSE_BOX_CRITICAL_EXCLUSION_AND_SIMPLEX_EMPTY_CLASSIFICATION",
        "producer_reuse": "SOURCE_CUBE_STAIRCASE_AND_FOUR_SUPPORT_SIMPLEX_GATE",
        "independent_certificate_replay": "STILL_REQUIRED",
        "global_topology_from_local_boxes": "NOT_CLAIMED",
        "evidence": [
            "ai/omreal/EXACT_SEMIALGEBRAIC_CERTIFICATE_METHOD.md",
            "ai/omreal/exact_semialgebraic/README.md",
            "ai/omreal/data/EXACT_SEMIALGEBRAIC_TOOLKIT_CANARIES.json",
            "ai/omreal/verify_exact_semialgebraic_toolkit.py",
        ],
    }
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
    square = progress["tenth_pair_source_square_component_coverage"]
    assert square == {
        "status": "PROVED",
        "scope": "exact wall-component coverage on one parent-resident two-parameter square joining row-2599 charts 0 and 152 in two moving-column blocks",
        "parent_brackets_replayed": 70,
        "strict_square_corners": 4,
        "candidate_factors_replayed": 17_824,
        "zero_free_walls": 14_061,
        "occurring_walls": 3_763,
        "unresolved_walls": 0,
        "graph_type_walls": 2_531,
        "biquadratic_walls": 1_232,
        "squarefree_projection_discriminants": 1_232,
        "compact_oval_candidates": 0,
        "wall_component_coverage": "EVERY_OCCURRING_WALL_COMPONENT_MEETS_SQUARE_BOUNDARY",
        "forced_intersecting_curve_pairs": 618_120,
        "full_sign_invariant_arrangement": "SUBORDINATED",
        "classification_semantic_sha256": "4b400742a6516d41209f548ceb9a97d3ff6fddc916f913b8a8b6c412f98045cc",
        "critical_semantic_sha256": "4791e9d4270e9d1e3f4ebf8a6687228572f5bce9a24de91130d2e82a380a246b",
        "boundary_semantic_sha256": "bb64fa529b5926d72a2c183e633147957145c4058fa8bd9557586637359d6d70",
        "hostile_corruptions_rejected": 12,
        "evidence": [
            "ai/omreal/DIAG3_PAIR_SOURCE_SQUARE_COVERAGE.md",
            "ai/omreal/data/DIAG3_PAIR_SOURCE_SQUARE_COVERAGE_0_152.json",
            "ai/omreal/verify_diag3_pair_source_square_coverage.py",
        ],
    }
    half_cube = progress["eleventh_pair_source_block_half_cube_component_coverage"]
    assert half_cube == {
        "status": "PROVED",
        "scope": "exact parent residence and wall feasibility on the chart-0/chart-152 block box [1/2,1] x [0,1] x [0,1]",
        "naive_full_cube_safe_vertices": 6,
        "naive_full_cube_failed_vertices": 2,
        "parent_brackets_replayed": 70,
        "strict_half_cube_vertices": 8,
        "candidate_factors_replayed": 17_824,
        "zero_free_walls": 13_374,
        "occurring_walls": 4_450,
        "unresolved_walls": 0,
        "maximum_subboxes_visited_for_one_wall": 25,
        "graph_type_occurring_walls": 3_889,
        "graph_type_component_coverage": "EVERY_COMPONENT_MEETS_HALF_CUBE_BOUNDARY",
        "fully_triquadratic_occurring_walls": 561,
        "fully_triquadratic_critical_systems_proved_empty": 561,
        "fully_triquadratic_critical_systems_unresolved": 0,
        "critical_depth_census": {"0": 552, "1": 4, "2": 3, "3": 1, "4": 1},
        "maximum_critical_subboxes_visited": 81,
        "fully_triquadratic_component_coverage": "EVERY_COMPONENT_MEETS_HALF_CUBE_BOUNDARY",
        "all_occurring_wall_component_coverage": "EVERY_COMPONENT_MEETS_HALF_CUBE_BOUNDARY",
        "graph_type_factor_ids_sha256": "87f98bd5d74697556cddc0809131ad54047e597a5b674b2a6cdc8b93c97984c3",
        "fully_triquadratic_factor_ids_sha256": "483908d8ece34b330e5942c3cedf32c013c9f3e23d1b8487249e17208e332802",
        "classification_semantic_sha256": "d3761de31661811d27c1340ab175c1c47431dfbf59c7993b7747bbbbcb622381",
        "critical_semantic_sha256": "214c653a6ffdec28a89a0f824c44e0b01658b60627825fd92032509aea7f855c",
        "hostile_corruptions_rejected": 11,
        "evidence": [
            "ai/omreal/DIAG3_PAIR_SOURCE_BLOCK_HALF_CUBE_FEASIBILITY.md",
            "ai/omreal/data/DIAG3_PAIR_SOURCE_BLOCK_HALF_CUBE_FEASIBILITY_0_152.json",
            "ai/omreal/verify_diag3_pair_source_block_cube_feasibility.py",
        ],
    }
    staircase = progress["twelfth_pair_source_staircase_component_coverage"]
    assert staircase == {
        "status": "PROVED",
        "scope": "exact parent residence, wall feasibility, and boxwise wall-component coverage on a five-box chart-0/chart-152 source staircase",
        "source_boxes": 5,
        "exact_parameter_volume": "373/512",
        "parent_bracket_box_restrictions_replayed": 350,
        "strict_parent_vertices_replayed": 40,
        "box_factor_restrictions_replayed": 89_120,
        "box_occurring_wall_census": [1_546, 2_069, 2_770, 3_300, 4_450],
        "distinct_staircase_occurring_walls": 5_106,
        "zero_free_on_all_staircase_boxes": 12_718,
        "unresolved_box_factor_restrictions": 0,
        "graph_type_box_occurrences": 12_276,
        "fully_triquadratic_box_occurrences": 1_859,
        "adaptive_critical_systems_proved_empty": 1_859,
        "adaptive_critical_systems_unresolved": 0,
        "alternate_derivative_pair_selections": 1,
        "preserved_inconclusive_derivative_pair_attempts": 1,
        "maximum_total_critical_subboxes_visited_for_one_factor": 48,
        "boxwise_component_coverage": "EVERY_OCCURRING_WALL_COMPONENT_MEETS_ITS_SOURCE_BOX_BOUNDARY",
        "source_skeleton": "UNION_OF_ALL_FIVE_BOX_BOUNDARIES",
        "staircase_global_boundary_coverage": "NOT_CLAIMED",
        "global_parent_cell_coverage": "NOT_CLAIMED",
        "staircase_occurring_factor_ids_sha256": "e51aea503481b62b028dbf94628cbb629ab493ad41b08aa0143c9d82708ee357",
        "staircase_zero_free_factor_ids_sha256": "2e6693ec80ada175f1b534f2b4155735a8281a79c692e3f7bc294e60bd6a5089",
        "box_classification_semantic_sha256": [
            "61a61fb2eb81fd1f69739bc6dcd000a8acffcf0025b7459f784f8939badbdc6b",
            "5030b7cc03a3ec3da99f27a2c5421a4e733e625c3889c9b43c3f3e0ad861b095",
            "a7bf40a18f916a8e0d81404b901de4fdd8657cbf05686d9bec72eea3962b938e",
            "c0a9dc2f09640a0ad688202fb6ec93c1d9b94ebfc0a1d6069d9ded22b0afe6e7",
            "152c16f19053901214c455aa4281cb20c8c5b4c91adde999e4d30bd5c3c21637",
        ],
        "box_critical_semantic_sha256": [
            "4ccf29178a0000d9d7e5b520c034b3c8e5638272ed9210536b9df7dbd856cdd5",
            "03dd4e5ae288a36127fa7d89c3a800f7f9ded8d55d829c1a6597da2aefb4a5b5",
            "e3c26fbfe2254a590b81a23fca668dea56f13073a9cea997c51a6ce1e3993fac",
            "02f44a46d7a0f090bea63d3c1ca8d82ec1294c136695b4d5bff484c1eadc8ae6",
            "23d4c04c8809405b2b8a204cc683e6faf3fb182d155709019d622f2bcae4835a",
        ],
        "hostile_corruptions_rejected": 14,
        "evidence": [
            "ai/omreal/DIAG3_PAIR_SOURCE_STAIRCASE_COVERAGE.md",
            "ai/omreal/data/DIAG3_PAIR_SOURCE_STAIRCASE_COVERAGE_0_152.json",
            "ai/omreal/verify_diag3_pair_source_staircase_coverage.py",
        ],
    }
    ambient_cube = progress["thirteenth_pair_full_hybrid_cube_ambient_topology"]
    assert ambient_cube == {
        "status": "PROVED",
        "scope": "exact ambient zero-set topology for all residual restrictions on the full chart-0/chart-152 three-parameter hybrid cube; parent residence is not claimed",
        "candidate_factors_replayed": 17_824,
        "zero_free_walls": 12_247,
        "occurring_walls": 5_577,
        "unresolved_walls": 0,
        "graph_type_occurring_walls": 4_898,
        "fully_triquadratic_occurring_walls": 679,
        "adaptive_critical_systems_proved_empty": 679,
        "adaptive_critical_systems_unresolved": 0,
        "alternate_derivative_pair_selections": 3,
        "preserved_inconclusive_derivative_pair_attempts": 4,
        "maximum_subboxes_visited_for_one_wall": 89,
        "maximum_total_critical_subboxes_visited_for_one_factor": 352,
        "parent_safe_cube_vertices": 6,
        "parent_failed_cube_vertices": 2,
        "full_cube_component_coverage": "EVERY_OCCURRING_RESTRICTED_WALL_COMPONENT_MEETS_FULL_HYBRID_CUBE_BOUNDARY",
        "source_subregion_transfer": "EVERY_RESTRICTED_WALL_COMPONENT_IN_A_PARENT_SAFE_SOURCE_STAIRCASE_MEETS_ITS_TRUE_OUTER_BOUNDARY",
        "internal_seams_required": False,
        "global_parent_cell_coverage": "NOT_CLAIMED",
        "occurring_factor_ids_sha256": "ca6e3d7911be1cc341fb4a40369542eadb8c526bd3c81a3f449037e97cfa425b",
        "zero_free_factor_ids_sha256": "3eab27338a090d6001e6d7d374d50d6983aeafe1967fac37b5b857f8ca168419",
        "classification_semantic_sha256": "5e290f7aab3da48706f326b1bb89a867b737efb3af354a182e679c62cbe1454d",
        "critical_semantic_sha256": "a7f8f690c855982e8eee416e97f8f7aa444646b0a3c1c964db15920ed6b6548e",
        "hostile_corruptions_rejected": 13,
        "evidence": [
            "ai/omreal/DIAG3_PAIR_FULL_HYBRID_CUBE_TOPOLOGY.md",
            "ai/omreal/data/DIAG3_PAIR_FULL_HYBRID_CUBE_TOPOLOGY_0_152.json",
            "ai/omreal/verify_diag3_pair_full_hybrid_cube_topology.py",
        ],
    }
    staircase8 = progress["fourteenth_pair_source_staircase8_yield_gate"]
    assert staircase8 == {
        "status": "PROVED_AND_STOPPED",
        "scope": "exact parent residence, complete wall feasibility, and true outer-boundary component coverage on an eight-box chart-0/chart-152 source staircase",
        "source_boxes": 8,
        "exact_parameter_volume": "12817/16384",
        "previous_exact_parameter_volume": "373/512",
        "exact_volume_gain": "881/16384",
        "parent_bracket_box_restrictions_replayed": 560,
        "strict_parent_vertices_replayed": 64,
        "box_factor_restrictions_replayed": 142_592,
        "box_occurring_wall_census": [1_320, 1_677, 1_982, 2_314, 2_637, 2_956, 3_232, 4_610],
        "distinct_staircase_occurring_walls": 5_139,
        "zero_free_on_all_staircase_boxes": 12_685,
        "unresolved_box_factor_restrictions": 0,
        "additional_distinct_occurring_walls_over_five_box_staircase": 33,
        "outer_boundary_component_coverage": "EVERY_RESTRICTED_WALL_COMPONENT_MEETS_STAIRCASE_OUTER_BOUNDARY",
        "internal_seams_required": False,
        "global_parent_cell_coverage": "NOT_CLAIMED",
        "further_dyadic_refinement": "STOPPED_LOW_YIELD",
        "staircase_occurring_factor_ids_sha256": "9e439b58569770fcacfef7a3b6b74b182e68453b020a1e7fceb8bc31f9954bc8",
        "staircase_zero_free_factor_ids_sha256": "0edd74b10c6263a5e92c00cb977902b7df38d52341d9fa1df7fac75d111b4ad4",
        "box_classification_semantic_sha256": [
            "5875b9ab05e129b1c7ce247a0b18a4ad31022dc10d5225e61a8fbe6661a5b4cd",
            "4184f86ff37bcd4b70afeeb98a26e544cb66c85e995dc325af27c1f32b04d3eb",
            "d16e1786faf172544199823991425fa794fee8fb97e3d58de3e3a9cea6ba3d0c",
            "0f8703e58ebe007a6b80d4df497373309de30c811a34fff0f03ca4761b85d996",
            "88421ea4b083691796e3199ed5f79b7fcf27a7a4b3e2162cbddb67dd1f79a65d",
            "88c9781db00f79b57c88c28d8b0075fdded6e2767473cfea1dd9c08755436a2a",
            "59434a320e45bc51fda7d988e7b0e7e95c8cb3cfd9ba4c8aae00c0864984edc4",
            "a82d60f2674d0d8595036365b2534d7c62da1edc7e175ca9c9323a3ea6ce9277",
        ],
        "hostile_corruptions_rejected": 12,
        "evidence": [
            "ai/omreal/DIAG3_DECISION_2026-08-22.md",
            "ai/omreal/DIAG3_PAIR_SOURCE_STAIRCASE8_COVERAGE.md",
            "ai/omreal/data/DIAG3_PAIR_SOURCE_STAIRCASE8_COVERAGE_0_152.json",
            "ai/omreal/verify_diag3_pair_source_staircase8_coverage.py",
        ],
    }
    incidence_no_go = progress["fifteenth_pair_source_family_incidence_no_go"]
    assert incidence_no_go == {
        "status": "PROVED_NO_GO",
        "scope": "exact comparison of known row-2599 parent-interior wall crossings with the complete chart-0/chart-152 full-source-cube occurrence set",
        "candidate_factors": 17_824,
        "parent_safe_segments": 105,
        "known_parent_interior_walls": 10_844,
        "source_cube_occurring_walls": 5_577,
        "known_parent_walls_meeting_source_cube": 5_454,
        "known_parent_walls_zero_free_on_source_cube": 5_390,
        "source_cube_walls_not_crossed_by_safe_segments": 123,
        "least_counterexample_factor_id": 5,
        "least_counterexample_parent_safe_segment_charts": [0, 2],
        "known_parent_walls_zero_free_on_source_cube_sha256": "26cce16d217d55e01081dad817d13778d2c797724659bcebd51555eb66855382",
        "known_parent_walls_meeting_source_cube_sha256": "ef52b6bf65c9eda5b5a198c1e9e15ed275d90c7dffa083b9e928e294e60a2d66",
        "retired_target": "PROVE_EVERY_GLOBAL_WALL_COMPONENT_MEETS_CHART0_CHART152_SOURCE_FAMILY",
        "replacement_target": "ADD_GENUINELY_DISTINCT_SOURCE_FAMILIES_OR_BUILD_A_DIRECT_GLOBAL_ROADMAP_MASTER_COMPLEX",
        "global_pair_obligation": "OPEN",
        "hostile_corruptions_rejected": 11,
        "evidence": [
            "ai/omreal/DIAG3_PAIR_SOURCE_FAMILY_INCIDENCE_NO_GO.md",
            "ai/omreal/data/DIAG3_PAIR_SOURCE_FAMILY_INCIDENCE_NO_GO_0_152.json",
            "ai/omreal/verify_diag3_pair_source_family_incidence_no_go.py",
        ],
    }
    four_support = progress["sixteenth_pair_first_four_support_gate"]
    assert four_support == {
        "status": "PROVED",
        "scope": "complete exact parent-domain coverage and residual-wall feasibility on the first two nominally four-dimensional row-2599 supports (3,1,15) and (3,3,7)",
        "supports": [[3, 1, 15], [3, 3, 7]],
        "forced_parent_equalities": ["g=i", "d=g"],
        "actual_parent_dimension": 3,
        "common_parent_domain": "0<=g<=a<=1 and 0<=g<=h<=1",
        "coverage_tetrahedra_per_support": 2,
        "independent_rational_coverage_points": 2_125,
        "parent_brackets_replayed_per_support": 70,
        "ambient_mixed_residual_restrictions": 8_017,
        "distinct_parent_reduced_zero_sets": 94,
        "distinct_active_remainders_before_positive_quotient": 26,
        "distinct_active_walls_after_positive_quotient": 22,
        "active_interior_factor_union_count": 436,
        "unresolved_interior_zero_sets": 0,
        "active_wall_catalog_sha256": "b3ee1a1e6c0ae0cbf9baaf5733f5569f89cf6282bd7da731a06fdc207db9f1e9",
        "hostile_corruptions_rejected": 12,
        "global_parent_cell_coverage": "NOT_CLAIMED",
        "evidence": [
            "ai/omreal/DIAG3_PAIR_GLOBAL_FOUR_SUPPORT_GATE.md",
            "ai/omreal/data/DIAG3_PAIR_GLOBAL_FOUR_SUPPORT_GATE.json",
            "ai/omreal/verify_diag3_pair_global_four_support_gate.py",
        ],
    }
    projection = progress["seventeenth_pair_first_four_support_projection"]
    assert projection == {
        "status": "PROVED",
        "scope": "complete first fiber-projection family for the 22 active wall equations on the two covered square-pyramid parent domains",
        "cube_parameterization": "a=t+(1-t)u, g=t, h=t+(1-t)v",
        "independent_rational_bijection_points": 5_372,
        "active_walls": 22,
        "base_only_walls": 1,
        "linear_fiber_walls": 20,
        "quadratic_fiber_walls": 1,
        "higher_degree_fiber_walls": 0,
        "raw_projection_obligations": 255,
        "distinct_boundary_reduced_projection_polynomials": 136,
        "maximum_base_bidegree": [4, 5],
        "projection_polynomial_ceiling": 100_000,
        "ceiling_not_triggered": True,
        "semantic_sha256": "fccd155814c3311d14a4988417c64335c551af14552a2265e428fbd3f00d500a",
        "hostile_corruptions_rejected": 12,
        "base_sign_invariant_cad": "NOT_YET_CONSTRUCTED",
        "global_parent_cell_coverage": "NOT_CLAIMED",
        "evidence": [
            "ai/omreal/DIAG3_PAIR_GLOBAL_FOUR_SUPPORT_PROJECTION.md",
            "ai/omreal/data/DIAG3_PAIR_GLOBAL_FOUR_SUPPORT_PROJECTION.json",
            "ai/omreal/verify_diag3_pair_global_four_support_projection.py",
        ],
    }
    base_projection = progress["eighteenth_pair_first_four_support_base_projection"]
    assert base_projection == {
        "status": "PROVED",
        "scope": "complete coefficient-discriminant-resultant projection of the 136 first-projection base polynomials to the t axis, with exact factorization replay and Sturm root-incidence census",
        "source_projection_polynomials": 136,
        "nonconstant_source_polynomials": 135,
        "distinct_base_curve_factors": 114,
        "base_factor_occurrences": 170,
        "nonconstant_projection_obligations": 6_061,
        "projection_kind_census": {
            "coefficient": 128,
            "discriminant": 69,
            "pair_resultant": 5_864,
        },
        "identically_zero_pair_resultants": 0,
        "distinct_squarefree_boundary_reduced_projection_polynomials": 2_554,
        "distinct_univariate_factor_polynomials": 2_333,
        "maximum_univariate_degree": 10,
        "interior_factor_root_incidences": 1_693,
        "distinct_interior_t_sections_upper_bound": 1_693,
        "projection_polynomial_ceiling": 100_000,
        "ceiling_not_triggered": True,
        "semantic_sha256": "985acacf6df251330a7dcc857a4d9d4e32d13862fa2b0bbb34b3bbc90f0eab08",
        "hostile_corruptions_rejected": 12,
        "base_sign_invariant_cad": "NOT_YET_CONSTRUCTED",
        "global_parent_cell_coverage": "NOT_CLAIMED",
        "evidence": [
            "ai/omreal/DIAG3_PAIR_GLOBAL_FOUR_SUPPORT_BASE_PROJECTION.md",
            "ai/omreal/data/DIAG3_PAIR_GLOBAL_FOUR_SUPPORT_BASE_PROJECTION.json.gz",
            "ai/omreal/verify_diag3_pair_global_four_support_base_projection.py",
        ],
    }
    root_isolation = progress["nineteenth_pair_first_four_support_root_isolation"]
    assert root_isolation == {
        "status": "PROVED",
        "scope": "complete exact isolation, deduplication, and global ordering of every interior root in the four-support second-projection factor catalog",
        "source_univariate_factor_polynomials": 2_333,
        "source_factor_root_incidences": 1_693,
        "factors_with_interior_sections": 1_442,
        "distinct_interior_t_sections": 1_693,
        "rational_sections": 19,
        "irrational_sections": 1_674,
        "requested_interval_width_ceiling": "1/281474976710656",
        "minimum_certified_gap": "500506336/3173419554501589",
        "maximum_endpoint_numerator_bits": 32,
        "maximum_endpoint_denominator_bits": 33,
        "sections_sha256": "e4060d9c578ed2148c7c22d8b26c669d578ca8d9cb63c9d558fd9d3a0f23c90d",
        "semantic_sha256": "2f285bf8c2c2a5f01a86981cbe11cc601dfd73538ab7181da5d80647445ebc67",
        "hostile_corruptions_rejected": 11,
        "base_sign_invariant_cad": "NOT_YET_CONSTRUCTED",
        "global_parent_cell_coverage": "NOT_CLAIMED",
        "evidence": [
            "ai/omreal/DIAG3_PAIR_GLOBAL_FOUR_SUPPORT_ROOT_ISOLATION.md",
            "ai/omreal/data/DIAG3_PAIR_GLOBAL_FOUR_SUPPORT_ROOT_ISOLATION.json.gz",
            "ai/omreal/verify_diag3_pair_global_four_support_root_isolation.py",
        ],
    }
    open_sector_lift = progress["twentieth_pair_first_four_support_open_sector_lift"]
    assert open_sector_lift == {
        "status": "PROVED",
        "scope": "complete exact ordered u-root stacks and sign-invariant base cells over every open t sector of the first two covered four-support domains",
        "base_curve_factors": 114,
        "ordered_t_sections": 1_693,
        "open_t_sectors": 1_694,
        "specialized_base_factor_instances": 193_116,
        "specialization_interior_root_count_census": {"0": 66_720, "1": 120_658, "2": 5_738},
        "open_sector_u_root_sections": 132_134,
        "open_sector_u_strips": 133_828,
        "open_sector_base_cells": 265_962,
        "minimum_roots_in_one_t_sector": 54,
        "maximum_roots_in_one_t_sector": 109,
        "nonconstant_u1_boundary_evaluations": 28,
        "distinct_projection_factors_covering_u1_boundary": 7,
        "missing_u1_boundary_factors": 0,
        "dyadic_endpoint_exponent": 48,
        "maximum_interval_span_numerator": 257,
        "minimum_within_sector_certified_gap": "11005/281474976710656",
        "sectors_sha256": "31fdab22ac2846a0180113bd627ccb367c08c5cc4e7f205ec5bad331123e0dcb",
        "semantic_sha256": "15c549ea4245cd85fa8546bfd859a77ccdf0bdfda805182aaa30727519f701c7",
        "artifact_shards": 32,
        "hostile_corruptions_rejected": 12,
        "algebraic_t_section_base_lift": "NOT_YET_CONSTRUCTED",
        "v_fiber_lift": "NOT_YET_CONSTRUCTED",
        "global_parent_cell_coverage": "NOT_CLAIMED",
        "evidence": [
            "ai/omreal/DIAG3_PAIR_GLOBAL_FOUR_SUPPORT_OPEN_SECTOR_LIFT.md",
            "ai/omreal/data/DIAG3_PAIR_GLOBAL_FOUR_SUPPORT_OPEN_SECTOR_LIFT.json",
            "ai/omreal/verify_diag3_pair_global_four_support_open_sector_lift.py",
        ],
    }
    simple_section_lift = progress["twenty_first_pair_first_four_support_simple_section_lift"]
    assert simple_section_lift == {
        "status": "PROVED",
        "scope": "complete exact algebraic-section fibers and local crossing attachments for every simple adjacent-transposition event between certified open-sector root stacks",
        "ordered_t_sections": 1_693,
        "simple_transversal_crossing_sections": 1_022,
        "resultant_multiplicity_one_sections": 1_022,
        "sections_with_coefficient_discriminant_or_u1_event": 0,
        "section_u_root_points": 84_794,
        "section_u_strips": 85_816,
        "section_base_cells": 170_610,
        "minimum_adjacent_sector_root_count": 54,
        "maximum_adjacent_sector_root_count": 109,
        "remaining_algebraic_t_sections": 671,
        "remaining_section_census": {
            "complex_same_count_transition": 251,
            "no_visible_stack_change": 406,
            "root_count_change": 14,
        },
        "crossings_sha256": "310760fd22ddec3a67961923bdff00f8cb42bacb89c0a0b216eed3549d8f59ec",
        "semantic_sha256": "37606875618910dd79dd110e7369c6487a3a81ffa21aefe2f0743ea095f800fd",
        "hostile_corruptions_rejected": 12,
        "remaining_algebraic_t_section_lifts": "NOT_YET_CONSTRUCTED",
        "v_fiber_lift": "NOT_YET_CONSTRUCTED",
        "global_parent_cell_coverage": "NOT_CLAIMED",
        "evidence": [
            "ai/omreal/DIAG3_PAIR_GLOBAL_FOUR_SUPPORT_SIMPLE_SECTION_LIFT.md",
            "ai/omreal/data/DIAG3_PAIR_GLOBAL_FOUR_SUPPORT_SIMPLE_SECTION_LIFT.json",
            "ai/omreal/verify_diag3_pair_global_four_support_simple_section_lift.py",
        ],
    }
    invisible_section_lift = progress["twenty_second_pair_first_four_support_invisible_section_lift"]
    assert invisible_section_lift == {
        "status": "PROVED",
        "scope": "complete exact constant-stack algebraic fibers for every unchanged adjacent stack carrying one raw-simple nonboundary projection event",
        "completed_constant_stack_sections": 363,
        "raw_event_kind_census": {"coefficient": 1, "discriminant": 6, "resultant": 356},
        "raw_event_multiplicity_one_sections": 363,
        "u_boundary_event_sections": 0,
        "section_u_root_points": 21_076,
        "section_u_strips": 21_439,
        "section_base_cells": 42_515,
        "remaining_algebraic_t_sections": 308,
        "remaining_section_census": {
            "complex_unchanged_stack": 43,
            "complex_same_count_transition": 251,
            "root_count_change": 14,
        },
        "completed_sha256": "b9e80ba2911b61213319095a7cef74a9fc92c68f0030b249bfd15c6c7876c1fe",
        "semantic_sha256": "d3451e30200e05f0b7900d56dc471aa8fb740f0519315541634fb455ed99bb5f",
        "hostile_corruptions_rejected": 11,
        "remaining_algebraic_t_section_lifts": "NOT_YET_CONSTRUCTED",
        "v_fiber_lift": "NOT_YET_CONSTRUCTED",
        "global_parent_cell_coverage": "NOT_CLAIMED",
        "evidence": [
            "ai/omreal/DIAG3_PAIR_GLOBAL_FOUR_SUPPORT_INVISIBLE_SECTION_LIFT.md",
            "ai/omreal/data/DIAG3_PAIR_GLOBAL_FOUR_SUPPORT_INVISIBLE_SECTION_LIFT.json",
            "ai/omreal/verify_diag3_pair_global_four_support_invisible_section_lift.py",
        ],
    }
    multi_section_lift = progress["twenty_third_pair_first_four_support_multi_section_lift"]
    assert multi_section_lift == {
        "status": "PROVED",
        "scope": "complete exact algebraic-section fibers for every remaining same-count transition carrying only raw multiplicity-one pair-resultant events and no coefficient, discriminant, or u-boundary event",
        "completed_same_count_sections": 240,
        "raw_resultant_events": 1_549,
        "visible_inversion_edges": 1_390,
        "interior_collision_groups": 549,
        "all_raw_event_multiplicities_one": True,
        "sections_with_coefficient_discriminant_or_boundary_event": 0,
        "section_u_root_points": 19_922,
        "section_u_strips": 20_162,
        "section_base_cells": 40_084,
        "remaining_algebraic_t_sections": 68,
        "remaining_section_census": {
            "complex_unchanged_stack": 43,
            "complex_same_count_transition": 11,
            "root_count_change": 14,
        },
        "completed_sha256": "a7004fa157e7a34a496c595fb5a7e7a43f50ab4830d61afe00f201f63481586a",
        "semantic_sha256": "1908a66a87b2cb75bc09b676e138c5d2a399ff6aacf662df36c72fc32027976a",
        "hostile_corruptions_rejected": 12,
        "remaining_algebraic_t_section_lifts": "NOT_YET_CONSTRUCTED",
        "v_fiber_lift": "NOT_YET_CONSTRUCTED",
        "global_parent_cell_coverage": "NOT_CLAIMED",
        "evidence": [
            "ai/omreal/DIAG3_PAIR_GLOBAL_FOUR_SUPPORT_MULTI_SECTION_LIFT.md",
            "ai/omreal/data/DIAG3_PAIR_GLOBAL_FOUR_SUPPORT_MULTI_SECTION_LIFT.json",
            "ai/omreal/verify_diag3_pair_global_four_support_multi_section_lift.py",
        ],
    }
    regular_residual = progress["twenty_fourth_pair_first_four_support_regular_residual_section_lift"]
    assert regular_residual == {
        "status": "PROVED",
        "scope": "complete exact algebraic-section fibers for unchanged stacks carrying only multiplicity-one resultants and same-count transitions carrying multiplicity-one resultants plus harmless non-leading coefficient events",
        "completed_sections": 40,
        "completed_unchanged_sections": 36,
        "completed_same_count_sections": 4,
        "raw_events": 197,
        "simple_resultant_events": 193,
        "harmless_nonleading_coefficient_events": 4,
        "visible_inversion_edges": 30,
        "invisible_simple_resultant_events": 163,
        "interior_collision_groups": 12,
        "section_u_root_points": 2_285,
        "section_u_strips": 2_325,
        "section_base_cells": 4_610,
        "remaining_algebraic_t_sections": 28,
        "remaining_section_census": {
            "complex_unchanged_stack": 7,
            "complex_same_count_transition": 7,
            "root_count_change": 14,
        },
        "completed_sha256": "5a4b84280cc75b8ca8c57b0c2417b56f6dea10c0a3b2cff06200e1199d488e66",
        "semantic_sha256": "54f278c42390c7de75a2ce1ddfe57f0b6e4e8f489de54e29f4845466add4e7ed",
        "hostile_corruptions_rejected": 13,
        "remaining_algebraic_t_section_lifts": "NOT_YET_CONSTRUCTED",
        "v_fiber_lift": "NOT_YET_CONSTRUCTED",
        "global_parent_cell_coverage": "NOT_CLAIMED",
        "evidence": [
            "ai/omreal/DIAG3_PAIR_GLOBAL_FOUR_SUPPORT_REGULAR_RESIDUAL_SECTION_LIFT.md",
            "ai/omreal/data/DIAG3_PAIR_GLOBAL_FOUR_SUPPORT_REGULAR_RESIDUAL_SECTION_LIFT.json",
            "ai/omreal/verify_diag3_pair_global_four_support_regular_residual_section_lift.py",
        ],
    }
    final_sections = progress["twenty_fifth_pair_first_four_support_final_section_lift"]
    assert final_sections == {
        "status": "PROVED",
        "scope": "complete exact base lifts for all final higher-multiplicity and count-changing algebraic t sections using ordered degree-at-most-four number-field Sturm certificates",
        "completed_sections": 28,
        "section_kind_census": {
            "count_change": 14,
            "same_count": 7,
            "unchanged": 7,
        },
        "minimal_degree_census": {"1": 6, "2": 11, "3": 9, "4": 2},
        "vertical_zero_factor_incidences": 1,
        "boundary_zero_factor_incidences": 33,
        "section_u_root_points": 1_862,
        "section_u_strips": 1_890,
        "section_base_cells": 3_752,
        "all_1693_algebraic_t_section_base_lifts": "COMPLETE",
        "remaining_algebraic_t_sections": 0,
        "sections_sha256": "244b48f6824fdfc524505b2d669b6dcd9ff028d0f8d9247fe1cafacb093458e2",
        "semantic_sha256": "312a564de346a75c9393446fbaf32a4a2e97ffe50f5665983fade0d9210da859",
        "hostile_corruptions_rejected": 12,
        "v_fiber_lift": "NOT_YET_CONSTRUCTED",
        "global_parent_cell_coverage": "NOT_CLAIMED",
        "evidence": [
            "ai/omreal/DIAG3_PAIR_GLOBAL_FOUR_SUPPORT_FINAL_SECTION_LIFT.md",
            "ai/omreal/data/DIAG3_PAIR_GLOBAL_FOUR_SUPPORT_FINAL_SECTION_LIFT.json",
            "ai/omreal/verify_diag3_pair_global_four_support_final_section_lift.py",
        ],
    }
    open_cell_v_lift = progress["twenty_sixth_pair_first_four_support_open_cell_v_lift"]
    assert open_cell_v_lift == {
        "status": "PROVED",
        "scope": "complete exact ordered v-root stacks for every full-dimensional base cell over an open t sector and open u strip",
        "v_endpoint_evaluations": 44,
        "missing_nonboundary_endpoint_factors": 0,
        "open_t_sectors": 1_694,
        "open_base_cells": 133_828,
        "distinct_fiber_order_signatures": 2_082,
        "minimum_interior_v_roots": 11,
        "maximum_interior_v_roots": 20,
        "interior_v_root_sections": 2_181_404,
        "open_v_strips": 2_315_232,
        "lifted_cells": 4_496_636,
        "signature_catalog_sha256": "2ba0f70e9aab9dc5bdb9a2e1c741a982845f0f8d9059dd4503dd87104803892d",
        "sector_signature_ids_sha256": "17ba454dffd6dbe26942a9da906befbb274f19f9de3635032f9c3e4667fbf6fb",
        "semantic_sha256": "6de66f64ba4ab1cdd1d07880322e665de0eab09e5462eebd9d3040c565d2ffc3",
        "artifact_shards": 32,
        "hostile_corruptions_rejected": 40,
        "open_t_algebraic_u_section_v_lift": "NOT_YET_CONSTRUCTED",
        "algebraic_t_section_v_lift": "NOT_YET_CONSTRUCTED",
        "global_gluing_and_closure_data": "NOT_CLAIMED",
        "evidence": [
            "ai/omreal/DIAG3_PAIR_GLOBAL_FOUR_SUPPORT_OPEN_CELL_V_LIFT.md",
            "ai/omreal/data/DIAG3_PAIR_GLOBAL_FOUR_SUPPORT_OPEN_CELL_V_LIFT.json",
            "ai/omreal/verify_diag3_pair_global_four_support_open_cell_v_lift.py",
        ],
    }
    regular_u_v_lift = progress[
        "twenty_seventh_pair_first_four_support_regular_u_section_v_lift"
    ]
    assert regular_u_v_lift == {
        "status": "PROVED",
        "scope": "exact v-fiber lifts for every multiplicity-one raw-resultant algebraic u section with equal adjacent root counts and no coefficient, discriminant, or v-endpoint event over all open t sectors",
        "open_t_sectors": 1_694,
        "algebraic_u_sections_examined": 132_134,
        "completed_sections": 120_174,
        "unresolved_sections": 11_960,
        "completed_fraction": "60087/66067",
        "completed_raw_resultant_events": 183_374,
        "visible_inversion_edges": 169_750,
        "interior_collision_groups": 148_896,
        "section_v_root_points": 1_809_609,
        "section_open_v_strips": 1_929_783,
        "lifted_cells": 3_739_392,
        "residual_reason_census": {
            "endpoint_and_count_change": 3_990,
            "coefficient_only": 3_388,
            "coefficient_endpoint_and_count_change": 2_888,
            "coefficient_and_endpoint_equal_count": 1_694,
        },
        "partition_sha256": "1b3ed3501793744b1ebc01a3d930d458efff4e30690c520aaa3ec48d3d7c9dfc",
        "semantic_sha256": "4caa3b63cfa4dd6e88b88076e0b4d6cd299822c7ff8680a73c6113f6ff3ff0ac",
        "artifact_shards": 32,
        "hostile_corruptions_rejected": 20,
        "remaining_open_t_algebraic_u_section_v_lift": "NOT_YET_CONSTRUCTED",
        "algebraic_t_section_v_lift": "NOT_YET_CONSTRUCTED",
        "global_gluing_and_closure_data": "NOT_CLAIMED",
        "evidence": [
            "ai/omreal/DIAG3_PAIR_GLOBAL_FOUR_SUPPORT_REGULAR_U_SECTION_V_LIFT.md",
            "ai/omreal/data/DIAG3_PAIR_GLOBAL_FOUR_SUPPORT_REGULAR_U_SECTION_V_LIFT.json",
            "ai/omreal/verify_diag3_pair_global_four_support_regular_u_section_v_lift.py",
            "ai/omreal/REVIEW_DIAG3_REGULAR_U_SECTION_V_LIFT_2026-08-24.md",
        ],
    }
    endpoint_u_v_lift = progress[
        "twenty_eighth_pair_first_four_support_endpoint_u_section_v_lift"
    ]
    assert endpoint_u_v_lift == {
        "status": "PROVED",
        "scope": "exact endpoint attachments for every open-t algebraic-u section whose only non-regular feature is one multiplicity-one linear v-endpoint crossing",
        "prior_residual_sections": 11_960,
        "completed_sections": 3_990,
        "remaining_sections": 7_970,
        "completed_factor_census": {"12": 1_194, "57": 1_694, "86": 1_102},
        "completed_raw_resultant_events": 10_184,
        "visible_inversion_edges": 9_951,
        "interior_collision_groups": 7_747,
        "section_v_root_points": 58_239,
        "section_open_v_strips": 62_229,
        "lifted_cells": 120_468,
        "remaining_reason_census": {
            "coefficient_only": 3_388,
            "coefficient_endpoint_and_count_change": 2_888,
            "coefficient_and_endpoint_equal_count": 1_694,
        },
        "partition_sha256": "5460ed86cfecd79d89feb2766743d923575b6ed676b2b49cca59afd7ce8164a6",
        "semantic_sha256": "20848c291db5f7a1cb81dfe74f64ac5e1e94b002ce1433fd897ae09c155fe04a",
        "artifact_shards": 32,
        "hostile_corruptions_rejected": 19,
        "remaining_open_t_coefficient_event_u_section_v_lift": "NOT_YET_CONSTRUCTED",
        "algebraic_t_section_v_lift": "NOT_YET_CONSTRUCTED",
        "global_gluing_and_closure_data": "NOT_CLAIMED",
        "evidence": [
            "ai/omreal/DIAG3_PAIR_GLOBAL_FOUR_SUPPORT_ENDPOINT_U_SECTION_V_LIFT.md",
            "ai/omreal/data/DIAG3_PAIR_GLOBAL_FOUR_SUPPORT_ENDPOINT_U_SECTION_V_LIFT.json",
            "ai/omreal/verify_diag3_pair_global_four_support_endpoint_u_section_v_lift.py",
        ],
    }
    coefficient_only_u_v_lift = progress[
        "twenty_ninth_pair_first_four_support_coefficient_only_u_section_v_lift"
    ]
    assert coefficient_only_u_v_lift == {
        "status": "PROVED",
        "scope": "exact unbounded degree-drop analysis for every coefficient-only open-t algebraic-u section",
        "prior_residual_sections": 7_970,
        "completed_sections": 3_388,
        "remaining_sections": 4_582,
        "completed_factor_census": {"27": 1_694, "38": 1_694},
        "simple_leading_coefficient_events": 3_388,
        "completed_raw_resultant_events": 11_858,
        "visible_inversion_edges": 10_704,
        "interior_collision_groups": 10_704,
        "section_v_root_points": 38_214,
        "section_open_v_strips": 41_602,
        "lifted_cells": 79_816,
        "remaining_reason_census": {
            "coefficient_endpoint_and_count_change": 2_888,
            "coefficient_and_endpoint_equal_count": 1_694,
        },
        "partition_sha256": "238b8c106db4f9aff97df8cd71c52b0347d6fc2e0a1f13f9c3295315ce47593e",
        "semantic_sha256": "0e46044a9d730459f3b848191c6cef62727e55eab456afe17e7f150656decbea",
        "artifact_shards": 32,
        "hostile_corruptions_rejected": 19,
        "remaining_open_t_coefficient_endpoint_u_section_v_lift": "NOT_YET_CONSTRUCTED",
        "algebraic_t_section_v_lift": "NOT_YET_CONSTRUCTED",
        "global_gluing_and_closure_data": "NOT_CLAIMED",
        "evidence": [
            "ai/omreal/DIAG3_PAIR_GLOBAL_FOUR_SUPPORT_COEFFICIENT_ONLY_U_SECTION_V_LIFT.md",
            "ai/omreal/data/DIAG3_PAIR_GLOBAL_FOUR_SUPPORT_COEFFICIENT_ONLY_U_SECTION_V_LIFT.json",
            "ai/omreal/verify_diag3_pair_global_four_support_coefficient_only_u_section_v_lift.py",
        ],
    }
    coefficient_endpoint_u_v_lift = progress[
        "thirtieth_pair_first_four_support_coefficient_endpoint_u_section_v_lift"
    ]
    assert coefficient_endpoint_u_v_lift == {
        "status": "PROVED",
        "scope": "exact bounded degree-drop, endpoint-attachment, and fiber-wide-zero analysis for the final open-t algebraic-u sections",
        "prior_residual_sections": 4_582,
        "completed_sections": 4_582,
        "remaining_open_t_algebraic_u_sections": 0,
        "completed_factor_census": {"35": 1_694, "56": 1_694, "72": 1_194},
        "simple_coefficient_events": 6_970,
        "simple_endpoint_attachments": 10_358,
        "fiber_wide_zero_wall_sections": 1_194,
        "completed_raw_resultant_events": 21_910,
        "visible_inversion_edges": 14_896,
        "interior_collision_groups": 10_586,
        "section_v_root_points": 51_794,
        "section_open_v_strips": 56_376,
        "lifted_cells": 108_170,
        "cumulative_open_t_algebraic_u_sections": 132_134,
        "cumulative_section_v_root_points": 1_957_856,
        "cumulative_section_open_v_strips": 2_089_990,
        "cumulative_lifted_cells": 4_047_846,
        "partition_sha256": "e9cb1628ea6a27112ccffe95dc8b53c87e7a99e6c49f6f147b74134cd411e192",
        "semantic_sha256": "2fdb7b5da77d155d90d651d5a4f9d2a84c4237a208b5e6c05a686c029007d9dc",
        "artifact_shards": 32,
        "hostile_corruptions_rejected": 23,
        "all_open_t_algebraic_u_section_v_lifts": "COMPLETE",
        "algebraic_t_section_v_lift": "NOT_YET_CONSTRUCTED",
        "global_gluing_and_closure_data": "NOT_CLAIMED",
        "evidence": [
            "ai/omreal/DIAG3_PAIR_GLOBAL_FOUR_SUPPORT_COEFFICIENT_ENDPOINT_U_SECTION_V_LIFT.md",
            "ai/omreal/data/DIAG3_PAIR_GLOBAL_FOUR_SUPPORT_COEFFICIENT_ENDPOINT_U_SECTION_V_LIFT.json",
            "ai/omreal/verify_diag3_pair_global_four_support_coefficient_endpoint_u_section_v_lift.py",
        ],
    }
    algebraic_t_open_u_v_lift = progress[
        "thirty_first_pair_first_four_support_algebraic_t_open_u_strip_v_lift"
    ]
    assert algebraic_t_open_u_v_lift == {
        "status": "PROVED",
        "scope": "exact v lift for every open-u strip over all algebraic-t sections",
        "algebraic_t_sections": 1_693,
        "prior_algebraic_t_base_cells": 261_571,
        "completed_open_u_strip_cells": 131_632,
        "remaining_algebraic_t_u_point_cells": 129_939,
        "unique_final_alignment_sections": 28,
        "adjacent_signature_agreements": 131_549,
        "exact_residual_strips": 83,
        "event_census": {
            "interior_collision": 48,
            "transport": 131_549,
            "upper_endpoint_exit": 35,
        },
        "section_v_root_points": 2_143_770,
        "section_open_v_strips": 2_275_402,
        "lifted_cells": 4_419_172,
        "section_signature_catalog_entries": 2_125,
        "partition_sha256": "f160d05c9b04d587679bd48234ca64b356dac93dace6075fb257a22f654db9ee",
        "section_signature_catalog_sha256": "908aad6ec3adbea5ffd897302f219ead458912c826681fc7e0e92f130e1f6273",
        "semantic_sha256": "794a839ba49b2418a541c7938131acd63fe16482ea8d187f0872fc3b1f2a80cf",
        "artifact_shards": 32,
        "hostile_corruptions_rejected": 24,
        "algebraic_t_open_u_strip_v_lifts": "COMPLETE",
        "algebraic_t_u_point_v_lifts": "NOT_YET_CONSTRUCTED",
        "global_gluing_and_closure_data": "NOT_CLAIMED",
        "evidence": [
            "ai/omreal/DIAG3_PAIR_GLOBAL_FOUR_SUPPORT_ALGEBRAIC_T_OPEN_U_STRIP_V_LIFT.md",
            "ai/omreal/data/DIAG3_PAIR_GLOBAL_FOUR_SUPPORT_ALGEBRAIC_T_OPEN_U_STRIP_V_LIFT.json",
            "ai/omreal/verify_diag3_pair_global_four_support_algebraic_t_open_u_strip_v_lift.py",
        ],
    }
    algebraic_t_regular_u_point_v_lift = progress[
        "thirty_second_pair_first_four_support_algebraic_t_regular_u_point_v_lift"
    ]
    assert algebraic_t_regular_u_point_v_lift == {
        "status": "PROVED",
        "scope": "exact compound-resultant v lift for regular algebraic-t algebraic-u point fibers",
        "prior_algebraic_t_u_point_cells": 129_939,
        "completed_points": 118_001,
        "remaining_points": 11_938,
        "completed_raw_resultant_events": 182_648,
        "visible_inversion_edges": 169_056,
        "algebraic_collision_edges": 169_113,
        "tangential_clique_completion_points": 9,
        "tangential_clique_completion_edges": 14,
        "connected_clique_completion_edges": 8,
        "isolated_tangential_k2_edges": 6,
        "interior_collision_groups": 148_041,
        "section_v_root_points": 1_773_150,
        "section_open_v_strips": 1_891_151,
        "lifted_cells": 3_664_301,
        "point_signature_catalog_entries": 4_721,
        "remaining_reason_census": {
            "coefficient_endpoint_count_change": 2_888,
            "coefficient_endpoint_equal_count": 1_692,
            "coefficient_only": 3_380,
            "endpoint_count_change": 3_976,
            "endpoint_equal_count": 2,
        },
        "partition_sha256": "48c7eaffa9f4badff5d22d5d4b1cee3423fee6d231910803afd8d372730ceb44",
        "point_signature_catalog_sha256": "26401e885102d200c7a818c52b32d361807f126442a4dd0824a685ca0c184dbb",
        "semantic_sha256": "3c6e1efad2193c4ab1a7d63a660bff97d100f45e518300f8b024564a23bd0fb1",
        "artifact_shards": 32,
        "hostile_corruptions_rejected": 28,
        "regular_algebraic_t_u_point_v_lifts": "COMPLETE",
        "remaining_algebraic_t_u_point_v_lifts": "NOT_YET_CONSTRUCTED",
        "global_gluing_and_closure_data": "NOT_CLAIMED",
        "evidence": [
            "ai/omreal/DIAG3_PAIR_GLOBAL_FOUR_SUPPORT_ALGEBRAIC_T_REGULAR_U_POINT_V_LIFT.md",
            "ai/omreal/data/DIAG3_PAIR_GLOBAL_FOUR_SUPPORT_ALGEBRAIC_T_REGULAR_U_POINT_V_LIFT.json",
            "ai/omreal/verify_diag3_pair_global_four_support_algebraic_t_regular_u_point_v_lift.py",
        ],
    }
    assert progress["theorem_effect"] == (
        "No invariant diagonal-three obligation is closed; honest 9DVL score remains 2/9."
    )
    assert progress["next_stage"].startswith(
        "lift the remaining 11938 coefficient/endpoint algebraic-t u-point fibers"
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
    print("PASS tenth source-square coverage: 3763 occurring walls / 0 missed components")
    print("PASS twelfth source staircase: 5 boxes / 89120 restrictions / volume 373/512")
    print("PASS eleventh source half-cube: all 4450 wall components boundary-attached")
    print("PASS thirteenth ambient cube: 5577 occurring walls / true boundary coverage")
    print("PASS fourteenth staircase yield gate: 8 boxes / volume 12817/16384 / +33 factors")
    print("PASS fifteenth source-family no-go: 5390 known parent walls miss the source cube")
    print("PASS sixteenth four-support gate: 8017 restrictions -> 94 zero sets -> 22 walls")
    print("PASS seventeenth four-support projection: 255 obligations -> 136 base polynomials")
    print("PASS eighteenth base projection: 6061 obligations -> 2554 polynomials -> 1693 root incidences")
    print("PASS nineteenth root isolation: 1693 distinct globally ordered t sections")
    print("PASS twentieth open-sector lift: 193116 specializations -> 265962 base cells")
    print("PASS twenty-first simple-section lift: 1022 fibers -> 170610 base cells")
    print("PASS twenty-second constant-stack lift: 363 fibers -> 42515 base cells")
    print("PASS twenty-third multi-crossing lift: 240 fibers -> 40084 base cells -> 68-section frontier")
    print("PASS twenty-fourth regular-residual lift: 40 fibers -> 4610 base cells -> 28-section frontier")
    print("PASS twenty-fifth final-section lift: 28 fibers -> 3752 base cells -> 0-section frontier")
    print("PASS twenty-sixth open-cell v lift: 133828 base cells -> 4496636 lifted cells")
    print(
        "PASS twenty-seventh regular algebraic-u v lift: "
        "120174/132134 sections -> 3739392 lifted cells -> 11960-section residue"
    )
    print(
        "PASS twenty-eighth endpoint algebraic-u v lift: "
        "3990 sections -> 120468 lifted cells -> 7970-section residue"
    )
    print(
        "PASS twenty-ninth coefficient-only algebraic-u v lift: "
        "3388 sections -> 79816 lifted cells -> 4582-section residue"
    )
    print(
        "PASS thirtieth coefficient-endpoint algebraic-u v lift: "
        "4582 sections -> 108170 lifted cells -> 0-section residue"
    )
    print(
        "PASS thirty-first algebraic-t open-u-strip v lift: "
        "131632 base strips -> 4419172 lifted cells -> 129939 u-point-cell residue"
    )
    print(
        "PASS thirty-second algebraic-t pure-resultant-u-point v lift: "
        "118001 points -> 3664301 lifted cells -> 11938-point residue"
    )
    print("LEDGER_GIT_BLOB", digest)


if __name__ == "__main__":
    main()
