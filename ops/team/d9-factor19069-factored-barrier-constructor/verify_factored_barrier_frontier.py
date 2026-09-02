#!/usr/bin/env python3
"""Constructor-scope replay and hostile checks for the factored frontier.

This is intentionally a producer self-check, not the cycle's independent
certificate.  The independent verifier must reconstruct the source circuit
without importing this directory.
"""

from __future__ import annotations

from copy import deepcopy
import json
from pathlib import Path

import build_factored_barrier_frontier as producer


HERE = Path(__file__).resolve().parent
FRONTIER = HERE / "FACTORED_BARRIER_FRONTIER.json"
MANIFEST = HERE / "SOURCE_MANIFEST.json"
RESULT = HERE / "RESULT.json"


class Reject(AssertionError):
    pass


def require(condition: bool, message: str) -> None:
    if not condition:
        raise Reject(message)


def canonical_digest(value) -> str:
    return producer.canonical_digest(value)


def validate_manifest(candidate: dict) -> None:
    semantic = dict(candidate)
    stored_digest = semantic.pop("semantic_sha256")
    require(canonical_digest(semantic) == stored_digest, "manifest semantic digest")
    require(candidate["format"] == "d9-factor19069-factored-barrier-source-manifest-v1", "manifest format")
    require(candidate["opening_revision"] == producer.OPENING_REVISION, "manifest opening revision")
    require(candidate["opening_tree"] == producer.OPENING_TREE, "manifest opening tree")
    require(candidate["base_revision"] == producer.BASE_REVISION, "manifest base revision")
    require(candidate["base_tree"] == producer.BASE_TREE, "manifest base tree")
    require(candidate["source_sha256"] == producer.SOURCE_PINS, "manifest source pins")
    require(candidate["source_count"] == len(producer.SOURCE_PINS), "manifest source count")
    require(candidate["drive_connector_used"] is False, "Drive connector scope")
    require(candidate["github_write"] is False, "GitHub scope")


def validate(candidate: dict) -> None:
    semantic = dict(candidate)
    stored_digest = semantic.pop("semantic_sha256")
    require(canonical_digest(semantic) == stored_digest, "frontier semantic digest")
    require(candidate["format"] == "d9-factor19069-factored-barrier-frontier-v1", "format")
    require(candidate["opening_revision"] == producer.OPENING_REVISION, "opening revision")
    require(candidate["opening_tree"] == producer.OPENING_TREE, "opening tree")
    require(candidate["base_revision"] == producer.BASE_REVISION, "base revision")
    require(candidate["base_tree"] == producer.BASE_TREE, "base tree")
    target = candidate["target"]
    require(target["parent_index"] == 2599, "parent index")
    require(target["factor_id"] == 19069, "factor id")
    require(target["parent_sign_factors"] == 70, "parent factor count")
    require(target["fixed_skeleton_edges"] == 40, "skeleton count")

    circuit = candidate["factor_circuit"]
    require(canonical_digest(circuit) == candidate["factor_circuit_semantic_sha256"], "circuit digest")
    require(circuit["format"] == "factor-circuit-dB-wedge-df-v1", "circuit format")
    barrier = circuit["barrier"]
    require(barrier["operation"] == "PRODUCT", "barrier operation")
    require(barrier["factor_count"] == 70, "barrier factor count")
    require(barrier["total_degree"] == 90, "barrier degree")
    require(barrier["expanded_polynomial_present"] is False, "expanded barrier")
    factors = circuit["parent_factor_nodes"]
    require(len(factors) == len({node["node_id"] for node in factors}) == 70, "factor nodes")
    require(barrier["ordered_factor_node_ids"] == [node["node_id"] for node in factors], "factor provenance")
    derivatives = circuit["barrier_derivative_nodes"]
    require(len(derivatives) == 9, "dB coordinate count")
    for coordinate, node in enumerate(derivatives):
        require(node["coordinate_index"] == coordinate, "dB coordinate ordering")
        require(node["operation"] == "SUM_OVER_ALL_70_FACTORS_OF_DH_I_TIMES_PRODUCT_J_NE_I_H_J", "dB operation")
        require(len(node["summands"]) == 70, "dB summand count")
        for factor_index, summand in enumerate(node["summands"]):
            require(summand["differentiated_factor_index"] == factor_index, "dB differentiated factor")
            require(summand["multiply_all_factor_indices_except"] == factor_index, "dB complementary product")
    require(len(circuit["wall_derivative_nodes"]) == 9, "df coordinate count")
    wedges = circuit["wedge_equation_nodes"]
    expected_pairs = [[left, right] for left in range(9) for right in range(left + 1, 9)]
    require([node["coordinate_pair"] for node in wedges] == expected_pairs, "wedge pair coverage")
    require(all(node["operation"] == "dB_left*df_right-dB_right*df_left" for node in wedges), "wedge operation")
    census = candidate["circuit_census"]
    require(census["dB_summands"] == 630, "dB census")
    require(census["wedge_equation_nodes"] == 36, "wedge census")
    require(census["expanded_barrier_monomials"] is None, "expanded monomial census")
    require(census["expanded_product_used"] is False, "expanded product use")

    interior = candidate["strict_interior_critical_frontier"]
    require(interior["systems_constructed"] == len(interior["systems"]) == 1, "interior system count")
    require(interior["connected_components_sampled"] == 0, "component sample count")
    require(interior["zero_dimensional_components_sampled"] == 0, "zero-dimensional samples")
    require(interior["positive_dimensional_components_sampled"] == 0, "positive-dimensional samples")
    require(interior["singular_pieces_discarded"] == 0, "singular scope")
    system = interior["systems"][0]
    system_semantic = dict(system)
    system_digest = system_semantic.pop("semantic_sha256")
    require(canonical_digest(system_semantic) == system_digest, "critical system digest")
    require(system["singular_wall_pieces_included"] is True, "singular pieces")
    require(system["positive_dimensional_pieces_required"] is True, "positive-dimensional pieces")
    require(system["connected_parent_selector"].endswith("REQUIRED"), "connected parent selector")
    require(system["component_decomposition_status"] == "UNSAMPLED_FAIL_CLOSED", "component decomposition")
    first = interior["first_unsampled_component_or_stratum"]
    require(first["stratum_id"] == system["stratum_id"], "first unsampled stratum id")
    require(first["stratum_semantic_sha256"] == system_digest, "first unsampled stratum digest")

    boundary = candidate["true_boundary_frontier"]
    require(boundary["ambient_product_support_strata"] == 3375, "support strata")
    require(boundary["parent_bernstein_excluded_support_strata"] == 3364, "excluded strata")
    require(boundary["proper_nonexcluded_candidate_strata"] == len(boundary["records"]) == 10, "boundary records")
    expected_supports = [[1, 1, 1], [1, 1, 5], [3, 1, 1], [3, 1, 5], [3, 1, 15], [3, 3, 7], [3, 3, 15], [7, 7, 7], [15, 1, 15], [15, 7, 15]]
    require([record["support"] for record in boundary["records"]] == expected_supports, "boundary support coverage")
    require(boundary["certified_witness_paths_to_pinned_parent_closure"] == 1, "boundary path count")
    require(boundary["wall_component_residence_classified_strata"] == 0, "boundary wall residence")
    require(boundary["first_unclassified_boundary_stratum"]["support"] == [1, 1, 1], "first boundary obstruction")
    require(set(boundary["true_parent_boundary_kept_distinct_from"]) == {"SOLVER_BOUNDARY", "BOX_BOUNDARY", "COLLAR_BOUNDARY", "SKELETON_EDGE_ENDPOINT"}, "boundary scope")

    skeleton = candidate["fixed_skeleton_accounting"]
    require(skeleton["all_40_edges_retain_all_70_parent_tags"] is True, "skeleton parent paths")
    require(skeleton["parent_path_tag_checks"] == 2800, "skeleton path census")
    roots = skeleton["factor19069_open_root_counts_by_edge"]
    require(len(roots) == 40, "skeleton root record count")
    require([edge for edge, count in roots.items() if count] == ["39"], "rooted edge")
    require(roots["39"] == 1, "edge39 root")
    anchor = skeleton["exact_attached_wall_anchor"]
    require(anchor["edge_index"] == 39, "anchor edge")
    require(anchor["attachment"] == "LIES_ON_FIXED_SKELETON_EDGE_39", "anchor attachment")
    require(anchor["barrier_critical_sample"] is False, "anchor critical scope")
    require(skeleton["global_wall_component_count"] is None, "global wall count")
    require(skeleton["attachment_classification_complete"] is False, "attachment completeness")

    resources = candidate["resource_accounting"]
    require(resources["max_exact_solver_component_nodes"] == 500000, "node ceiling")
    require(resources["exact_solver_component_nodes_used"] == 0, "nodes used")
    require(resources["paid_or_external_compute"] is False, "compute authority")
    require(candidate["endpoint"] == "HASH_PINNED_FACTORED_BARRIER_CRITICAL_COMPONENT_FRONTIER_WITH_FIRST_UNSAMPLED_COMPONENT", "endpoint")
    require(candidate["classification"] == "EXACT_FAIL_CLOSED_FACTORED_BARRIER_COMPONENT_NULL", "classification")
    require(candidate["producer_independent_certificate_present"] is False, "certificate scope")
    require(candidate["ledger_change_recommended"] == "none", "ledger recommendation")
    require(candidate["theorem_ledger"] == "2/9", "theorem ledger")
    require(len(candidate["fail_closed_controls"]) == 18, "fail-closed controls")


def validate_result(candidate: dict, frontier: dict, manifest: dict) -> None:
    require(candidate["format"] == "d9-factor19069-factored-barrier-constructor-result-v1", "result format")
    require(candidate["opening_revision"] == producer.OPENING_REVISION, "result opening revision")
    require(candidate["opening_tree"] == producer.OPENING_TREE, "result opening tree")
    require(candidate["outcome"] == "pass", "result outcome")
    require(candidate["classification"] == frontier["classification"], "result classification")
    require(candidate["endpoint"] == frontier["endpoint"], "result endpoint")
    require(candidate["frontier_sha256"] == producer.digest_path(FRONTIER), "result frontier hash")
    require(candidate["frontier_semantic_sha256"] == frontier["semantic_sha256"], "result frontier semantic hash")
    require(candidate["source_manifest_sha256"] == producer.digest_path(MANIFEST), "result manifest hash")
    require(candidate["factor_circuit_semantic_sha256"] == frontier["factor_circuit_semantic_sha256"], "result circuit hash")
    require(candidate["exact_circuit"]["dB_wedge_df_equations"] == 36, "result wedge count")
    require(candidate["critical_frontier"]["connected_components_sampled"] == 0, "result component count")
    require(candidate["critical_frontier"]["first_unsampled_stratum_sha256"] == frontier["strict_interior_critical_frontier"]["systems"][0]["semantic_sha256"], "result first stratum hash")
    require(candidate["true_boundary"]["proper_nonexcluded_candidates"] == 10, "result boundary count")
    require(candidate["true_boundary"]["first_unclassified_support"] == [1, 1, 1], "result boundary obstruction")
    require(candidate["fixed_skeleton"]["global_component_inference_from_anchor"] is False, "result skeleton scope")
    require(candidate["constructor_hostile_mutations"] == {"rejected": 19, "total": 19}, "result hostile count")
    require(candidate["producer_independent_certificate_present"] is False, "result certificate scope")
    require(candidate["ledger_change_recommended"] == "none", "result ledger recommendation")
    require(candidate["theorem_ledger"] == "2/9", "result ledger")
    require(manifest["semantic_sha256"] == frontier["source_manifest_semantic_sha256"], "manifest/frontier binding")


def reseal(candidate: dict) -> dict:
    candidate["semantic_sha256"] = canonical_digest(
        {key: value for key, value in candidate.items() if key != "semantic_sha256"}
    )
    return candidate


def hostile_mutations(stored: dict) -> None:
    mutations = []
    altered = deepcopy(stored); altered["opening_revision"] = "0" * 40; mutations.append((reseal(altered), "opening revision"))
    altered = deepcopy(stored); altered["base_tree"] = "0" * 40; mutations.append((reseal(altered), "base tree"))
    altered = deepcopy(stored); altered["target"]["factor_id"] = 19068; mutations.append((reseal(altered), "factor id"))
    altered = deepcopy(stored); altered["factor_circuit"]["barrier"]["factor_count"] = 69; mutations.append((reseal(altered), "circuit digest"))
    altered = deepcopy(stored); altered["factor_circuit"]["parent_factor_nodes"].pop(); mutations.append((reseal(altered), "circuit digest"))
    altered = deepcopy(stored); altered["factor_circuit"]["barrier"]["expanded_polynomial_present"] = True; mutations.append((reseal(altered), "circuit digest"))
    altered = deepcopy(stored); altered["factor_circuit"]["barrier_derivative_nodes"][0]["summands"].pop(); mutations.append((reseal(altered), "circuit digest"))
    altered = deepcopy(stored); altered["factor_circuit"]["barrier_derivative_nodes"][0]["summands"][0]["multiply_all_factor_indices_except"] = 1; mutations.append((reseal(altered), "circuit digest"))
    altered = deepcopy(stored); altered["factor_circuit"]["wedge_equation_nodes"].pop(); mutations.append((reseal(altered), "circuit digest"))
    altered = deepcopy(stored); altered["strict_interior_critical_frontier"]["systems"][0]["positive_dimensional_pieces_required"] = False; mutations.append((reseal(altered), "critical system digest"))
    altered = deepcopy(stored); altered["strict_interior_critical_frontier"]["systems"][0]["singular_wall_pieces_included"] = False; mutations.append((reseal(altered), "critical system digest"))
    altered = deepcopy(stored); altered["strict_interior_critical_frontier"]["systems"][0]["connected_parent_selector"] = "SIGNS_ONLY"; mutations.append((reseal(altered), "critical system digest"))
    altered = deepcopy(stored); altered["true_boundary_frontier"]["records"].pop(); mutations.append((reseal(altered), "boundary records"))
    altered = deepcopy(stored); altered["true_boundary_frontier"]["true_parent_boundary_kept_distinct_from"].pop(); mutations.append((reseal(altered), "boundary scope"))
    altered = deepcopy(stored); altered["fixed_skeleton_accounting"]["all_40_edges_retain_all_70_parent_tags"] = False; mutations.append((reseal(altered), "skeleton parent paths"))
    altered = deepcopy(stored); altered["fixed_skeleton_accounting"]["factor19069_open_root_counts_by_edge"]["39"] = 0; mutations.append((reseal(altered), "rooted edge"))
    altered = deepcopy(stored); altered["fixed_skeleton_accounting"]["global_wall_component_count"] = 1; mutations.append((reseal(altered), "global wall count"))
    altered = deepcopy(stored); altered["fixed_skeleton_accounting"]["attachment_classification_complete"] = True; mutations.append((reseal(altered), "attachment completeness"))
    altered = deepcopy(stored); altered["theorem_ledger"] = "3/9"; mutations.append((reseal(altered), "theorem ledger"))
    rejected = 0
    for candidate, expected in mutations:
        try:
            validate(candidate)
        except Reject as error:
            require(expected in str(error), f"unexpected hostile rejection: expected {expected!r}, got {error!r}")
            rejected += 1
        else:
            raise AssertionError(f"hostile mutation accepted: {expected}")
    require(rejected == len(mutations) == 19, "hostile mutation census")


def main() -> None:
    stored_manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    stored = json.loads(FRONTIER.read_text(encoding="utf-8"))
    result = json.loads(RESULT.read_text(encoding="utf-8"))
    validate_manifest(stored_manifest)
    validate(stored)
    validate_result(result, stored, stored_manifest)
    rebuilt_manifest, rebuilt = producer.build()
    require(stored_manifest == rebuilt_manifest, "manifest does not rebuild")
    require(stored == rebuilt, "frontier does not rebuild")
    hostile_mutations(stored)
    print("PASS exact source manifest and factored-circuit rebuild")
    print("PASS dB wedge df=36; component frontier fails closed at strict interior")
    print("PASS boundary=10 candidates, certified witness paths=1, first unresolved=(1,1,1)")
    print("PASS hostile_mutations=19/19; ledger=2/9")


if __name__ == "__main__":
    main()
