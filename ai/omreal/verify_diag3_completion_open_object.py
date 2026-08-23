#!/usr/bin/env python3
"""Replay the arithmetic and artifact pins in the open diagonal-three ledger.

This checker intentionally proves no new topology.  It prevents a future
handoff from losing the exact source/residue partition, double-counting the
two post-sequential layers, or treating the conditional pair compiler as a
completed global complex.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
MANIFEST = HERE / "data" / "DIAG3_COMPLETION_OPEN_OBJECT.json"


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def main() -> None:
    record = json.loads(MANIFEST.read_text())
    assert record["format"] == "diag3-completion-open-object-v1"
    assert record["status"] == "OPEN"
    assert record["ledger_score"] == "2/9"
    assert record["authoritative_remote_base"]["commit"] == (
        "f4fcce6a5d1a49d6607ba858a1f0b0090af72f44"
    )

    triple = record["triple_obligation"]
    assert triple["status"] == "OPEN"
    universe = triple["universe_count"]
    closed = triple["proved_noncompact_count"]
    unresolved = triple["unresolved_count"]
    assert universe == 79_102_449
    assert closed == 77_940_147
    assert unresolved == 1_162_302
    assert universe - closed == unresolved

    layers = triple["new_layers_after_pr17"]
    sequential = layers["sequential_affine"]
    double = layers["double_graph_type49_pivot3"]
    extension = layers["double_graph_type49_pivot1_5_extension"]
    double_union = layers["double_graph_type49_pivot1_3_5"]
    generic = layers["double_graph_generic_all_chart_increment"]
    all_double = layers["double_graph_all_certificates"]
    minor = layers["unit_minor_after_graph"]
    union = layers["double_graph_union_unit_minor"]
    direct = layers["direct_final_affinity"]
    primitive = layers["primitive_final_direction"]
    direct_primitive = layers["direct_primitive_final_union"]
    support3 = layers["primitive_final_support3"]
    final_union = layers["all_final_affinity_union"]
    assert sequential["residue_count"] == 1_638_903
    assert 77_282_660 + sequential["closed_count"] == 77_463_546
    assert minor["standalone_closed_count"] - minor["overlap_with_double_graph"] == (
        minor["increment_after_double_graph"]
    )
    assert extension["disjoint_from_pivot3"]
    assert extension["disjoint_from_unit_minor"]
    assert extension["closed_count"] + double["closed_count"] == (
        double_union["closed_count"]
    )
    assert double_union["pivot3_count"] == double["closed_count"]
    assert double_union["pivot1_5_increment"] == extension["closed_count"]
    assert generic["disjoint_from_prior_accepted_union"]
    assert double_union["closed_count"] + generic["closed_count"] == (
        all_double["closed_count"]
    )
    assert all_double["type49_count"] == double_union["closed_count"]
    assert all_double["generic_increment"] == generic["closed_count"]
    assert minor["overlap_with_pivot3"] == minor["overlap_with_double_graph"]
    assert minor["overlap_with_pivot1_5_extension"] == 0
    assert all_double["closed_count"] + minor["increment_after_double_graph"] == (
        union["closed_count"]
    )
    assert sequential["residue_count"] - union["closed_count"] == (
        union["residue_count"]
    )
    assert union["residue_count"] == direct["source_count"] == 1_221_055
    assert union["residue_semantic_digest"] == (
        "432854b7f00b57c5cf0009033e3ddfd3f4cb702bafed8fad2e5e69b369f30597"
    )
    assert direct["closed_count"] == 58_673
    assert direct["witness_occurrence_count"] == 128_198
    assert direct["source_count"] - direct["closed_count"] == (
        direct["residue_count"]
    )
    assert direct["residue_count"] == 1_162_382
    assert direct["stream_semantic_digest"] == (
        "7cd37ee421c651563bb6dbeae45b6711b71839893ba53abfb7240b1e165f2b1a"
    )
    assert direct["residue_semantic_digest"] == (
        "44ff9f5f0ea6c332c0382717533f5fa4b8e4b8af3d72024f9d4b0c74e6448dda"
    )
    assert primitive["closed_count"] == 23
    assert primitive["disjoint_from_direct_final_affinity"]
    assert primitive["stream_semantic_digest"] == (
        "8917815ae6b4c65c83b74e09d5ee8f3f18f237d9bd493fce04094ca3d8f0f055"
    )
    assert primitive["row_semantic_digest"] == (
        "a1af2ac4e6ff2b9e9037ebc8f9bf969485acda4ce5f50adaeb0ab24f96a4e971"
    )
    assert direct["closed_count"] + primitive["closed_count"] == (
        direct_primitive["closed_count"]
    )
    assert direct_primitive["direct_final_count"] == direct["closed_count"]
    assert direct_primitive["primitive_final_increment"] == (
        primitive["closed_count"]
    )
    assert direct_primitive["residue_count"] == 1_162_359
    assert direct_primitive["residue_semantic_digest"] == (
        "6c477d76ec0173ab340db4c9f5b783d3638393d0714e58440bae35b143b02b6a"
    )
    assert support3["closed_count"] == 57
    assert support3["disjoint_from_direct_and_support2"]
    assert support3["stream_semantic_digest"] == (
        "71df56d10ebd93be6f4c59f626d38d9a992264b2cbaf74fe0070618fed4a0de0"
    )
    assert support3["row_semantic_digest"] == (
        "4aa31365ba2f8dd9f429b5dd5ffbbc735f161c68dc5605372a597892da65965b"
    )
    assert direct_primitive["closed_count"] + support3["closed_count"] == (
        final_union["closed_count"]
    )
    assert final_union["direct_support2_count"] == (
        direct_primitive["closed_count"]
    )
    assert final_union["support3_increment"] == support3["closed_count"]
    assert union["residue_count"] - final_union["closed_count"] == unresolved
    assert final_union["residue_count"] == unresolved
    assert final_union["residue_semantic_digest"] == (
        "a76a7c2cd6631c2d9724b450540bec7f3be6c106a41ae41f1736bbd2755a5ca4"
    )
    assert 77_463_546 + union["closed_count"] + final_union["closed_count"] == (
        closed
    )

    critical_gate = triple["fullspace_critical_h1_gate"]
    assert critical_gate["status"] == "FAIL_CLOSED"
    assert critical_gate["formal_equation_count"] == 59
    assert critical_gate["nonzero_height_minor_count"] == 52
    assert critical_gate["nonzero_height_minor_terms"] == 14_681
    assert critical_gate["raw_coordinate_boundary_component_dimensions"] == [4, 4]
    critical_system = HERE.parent.parent / critical_gate["system"]
    assert sha256(critical_system) == critical_gate["system_sha256"]
    critical_manifest = json.loads(
        (HERE.parent.parent / critical_gate["manifest"]).read_text()
    )
    assert critical_manifest["semantic_sha256"] == critical_gate["semantic_digest"]
    assert critical_manifest["decision"]["status"] == "FAIL_CLOSED"
    assert critical_manifest["theorem_accounting"]["score_after"] == "2/9"
    assert critical_manifest["theorem_accounting"][
        "final_unresolved_triple_orbits"
    ] == unresolved
    koszul = triple["factored_koszul_gate"]
    assert koszul["status"] == "BOUNDED_ROUTE_EXHAUSTED"
    assert koszul["exact_directional_minor_count"] == 10
    assert koszul["primitive_minor_term_range"] == [18_459, 37_222]
    assert koszul["degree_14_macaulay"] == {
        "target_count": 88,
        "F2_rank": 5_202,
        "F2_hits": 0,
        "F3_rank": 5_202,
        "F3_hits": 0,
    }

    for layer in (
        sequential, double, extension, generic, minor, direct, primitive,
        support3,
    ):
        artifact = HERE.parent.parent / layer["certificate"]
        assert artifact.is_file(), artifact
        assert artifact.stat().st_size == layer["certificate_bytes"], artifact
        assert sha256(artifact) == layer["certificate_sha256"], artifact

    pair = record["pair_obligation"]
    assert pair["status"] == "OPEN"
    assert pair["integral_lift_status"] == "CONDITIONAL_ON_GLOBAL_REGULAR_CLOSURE_POSET"
    assert pair["middle_exactness_status"] == "NOT_COMPUTABLE_GLOBALLY_FROM_CURRENT_DATA"
    closure_path = HERE.parent.parent / pair["global_closure_manifest"]
    closure = json.loads(closure_path.read_text())
    assert closure["status"] == "OPEN"
    assert closure["observation_digest"] == pair["global_closure_observation_digest"]
    assert closure["smallest_open_object"]["id"] == pair["smallest_open_object"]
    assert closure["smallest_open_object"]["first_missing_block"] == pair["first_missing_block"]
    assert pair["current_data"]["row2599_local_relative_pair_wall_collars"] == 3
    assert pair["current_data"]["row2599_local_complete_comparison_incidences"] == 4
    assert pair["current_data"]["row2599_candidate_factor_input_count"] == 17_824
    assert pair["current_data"]["row2599_compactification_model"] == "(Delta^3)^3"
    assert pair["current_data"]["row2599_compactification_chart_count"] == 64
    assert pair["current_data"]["row2599_compactification_support_face_count"] == 3_375
    assert pair["current_data"]["row2599_bernstein_factor_face_pair_count"] == 60_156_000
    assert pair["current_data"]["row2599_bernstein_eliminated_pair_count"] == 42_547_692
    assert pair["current_data"]["row2599_bernstein_mixed_pair_count"] == 17_608_308
    assert pair["current_data"]["row2599_bernstein_face_state_stream_sha256"] == (
        "292b16a874914134657a6d09a26d5bdde239d2e6989fe7c23234b90ac698f82b"
    )
    assert pair["current_data"]["row2599_parent_face_excluded_support_count"] == 3_364
    assert pair["current_data"]["row2599_parent_face_nonexcluded_support_count"] == 11
    assert pair["current_data"]["row2599_parent_face_remaining_mixed_count"] == 70_218
    assert pair["current_data"]["row2599_parent_face_state_stream_sha256"] == (
        "e4f15408f786c26c34b4d721d7973aedc6e206a7382e5a92ce839f8c732be9f5"
    )
    assert pair["current_data"]["row2599_support_one_skeleton"] == {
        "vertices": 3, "edges": 2, "active_residual_walls": 0
    }
    assert pair["current_data"]["row2599_support_two_face_cellulation"] == {
        "vertices": 4, "edges": 5, "faces": 2, "dividing_wall": "a=h"
    }
    preflight = closure["global_generator_preflight"]
    assert preflight["status"] == (
        "FOUR_SUPPORT_1385_SECTIONS_LIFTED_308_ALGEBRAIC_SECTIONS_MISSING"
    )
    candidate_path = HERE.parent.parent / preflight["candidate_factor_artifact"]
    assert candidate_path.stat().st_size == preflight["candidate_factor_artifact_bytes"]
    assert sha256(candidate_path) == preflight["candidate_factor_artifact_sha256"]
    atlas_path = HERE.parent.parent / preflight["compactification_atlas"]
    assert sha256(atlas_path) == preflight["compactification_atlas_sha256"]
    bernstein_path = HERE.parent.parent / preflight["face_bernstein_atlas"]
    assert sha256(bernstein_path) == preflight["face_bernstein_atlas_sha256"]
    parent_face_path = HERE.parent.parent / preflight["parent_face_gate"]
    assert sha256(parent_face_path) == preflight["parent_face_gate_sha256"]
    assert closure["row2599_flow_triangle_mixed_d3"][
        "certified_relative_pair_wall_collar_count"
    ] == 3
    assert closure["row2599_flow_triangle_mixed_d3"][
        "certified_comparison_incidence_count"
    ] == 4

    assert record["hostile_audit"]["completion_verdict"] == (
        "DIAGONAL_THREE_REMAINS_OPEN_AT_2_OF_9"
    )
    print(
        "PASS diagonal-three open checkpoint: "
        f"{closed}/{universe} triple rows closed, {unresolved} unresolved; "
        "pair global closure missing; ledger 2/9"
    )


if __name__ == "__main__":
    main()
