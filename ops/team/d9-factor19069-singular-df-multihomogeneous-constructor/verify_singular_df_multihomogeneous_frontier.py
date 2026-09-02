#!/usr/bin/env python3
"""Independently verify the exact affine source-structure null frontier."""

from __future__ import annotations

from collections import Counter
from copy import deepcopy
from hashlib import sha256
import json
from pathlib import Path
import subprocess


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
PREDECESSOR = ROOT / "ops" / "team" / "d9-factor19069-critical-equidim-constructor" / "CRITICAL_EQUIDIM_FRONTIER.json"
FRONTIER = HERE / "SINGULAR_DF_MULTIHOMOGENEOUS_FRONTIER.json"
MANIFEST = HERE / "SOURCE_MANIFEST.json"
RESULT = HERE / "RESULT.json"
VARIABLES = tuple("abcdefghi")
BLOCKS = ((0, 1, 2), (3, 4, 5), (6, 7, 8))
EXPECTED_PREDECESSOR_SHA256 = "4d7f4f21d0a5ab59ae42fa265d5a3cf851fa74dd1ff7069cd19209ec897d3a33"
OPENING_REVISION = "a2860f3f6436f573a913fc8ca6312b944212aadd"
HISTORICAL_CONTROL_PATHS = {
    "ops/research-team/PROTOCOL.md",
    "ops/research-team/verify_cycle_protocol.py",
}


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def digest_path(path: Path) -> str:
    state = sha256()
    with path.open("rb") as source:
        for block in iter(lambda: source.read(1 << 20), b""):
            state.update(block)
    return state.hexdigest()


def source_digest(relative: str) -> str:
    if relative in HISTORICAL_CONTROL_PATHS:
        frozen = subprocess.check_output(
            ["git", "show", f"{OPENING_REVISION}:{relative}"], cwd=ROOT
        )
        return sha256(frozen).hexdigest()
    return digest_path(ROOT / relative)


def canonical_digest(value) -> str:
    return sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode("ascii")).hexdigest()


def without_semantic(value: dict) -> dict:
    copy = deepcopy(value)
    del copy["semantic_sha256"]
    return copy


def derivative(terms: list[dict], coordinate: int) -> list[dict]:
    accumulator: dict[tuple[int, ...], int] = {}
    for term in terms:
        power = term["exponents"][coordinate]
        if not power:
            continue
        exponent = list(term["exponents"])
        exponent[coordinate] -= 1
        key = tuple(exponent)
        accumulator[key] = accumulator.get(key, 0) + term["coefficient"] * power
    return [
        {"coefficient": coefficient, "exponents": list(exponent)}
        for exponent, coefficient in sorted(accumulator.items())
        if coefficient
    ]


def block_degree(exponent: list[int]) -> tuple[int, int, int]:
    return tuple(sum(exponent[index] for index in block) for block in BLOCKS)


def validate(candidate: dict, predecessor: dict) -> None:
    require(candidate["semantic_sha256"] == canonical_digest(without_semantic(candidate)), "frontier semantic digest")
    require(candidate["format"] == "d9-factor19069-singular-df-multihomogeneous-constructor-frontier-v1", "format")
    require(candidate["classification"] == "EXACT_SOURCE_STRUCTURE_FALSIFICATION_FAIL_CLOSED_NULL", "classification")
    require(candidate["endpoint"] == "HASH_PIN_FIRST_UNRESOLVED_MULTIHOMOGENEOUS_SINGULAR_BRANCH", "endpoint")
    require(candidate["theorem_ledger"] == "2/9" and candidate["ledger_change_recommended"] == "none", "ledger")

    terms = predecessor["factor_circuit"]["wall_polynomial"]["sparse_polynomial"]
    source = candidate["original_singular_jacobian_ideal"]["generators"][0]
    require(source["node_id"] == "f_19069" and source["sparse_polynomial"] == terms, "source polynomial")
    require(source["semantic_sha256"] == canonical_digest(without_semantic(source)), "source semantic")
    require(candidate["original_singular_jacobian_ideal"]["generator_count"] == 10, "generator count")
    require(candidate["original_singular_jacobian_ideal"]["inverse_variables"] == 0, "inverse variable route")
    for coordinate, variable in enumerate(VARIABLES):
        node = candidate["original_singular_jacobian_ideal"]["generators"][coordinate + 1]
        require(node["coordinate"] == variable and node["coordinate_index"] == coordinate, "derivative identity")
        require(node["sparse_polynomial"] == derivative(terms, coordinate), "derivative replay")
        require(node["term_count"] == len(node["sparse_polynomial"]), "derivative term count")
        require(node["semantic_sha256"] == canonical_digest(without_semantic(node)), "derivative semantic")
    jacobian = candidate["original_singular_jacobian_ideal"]
    require(jacobian["semantic_sha256"] == canonical_digest(without_semantic(jacobian)), "Jacobian semantic")

    structure = candidate["exact_affine_source_structure"]
    require(structure["semantic_sha256"] == canonical_digest(without_semantic(structure)), "structure semantic")
    total = Counter(sum(term["exponents"]) for term in terms)
    blocks = Counter(block_degree(term["exponents"]) for term in terms)
    require(total == Counter({4: 58, 5: 39, 6: 11}), "total-degree distribution")
    require(blocks == Counter({(1, 2, 1): 20, (2, 1, 1): 15, (2, 2, 1): 15, (1, 1, 2): 12, (1, 2, 2): 12, (2, 1, 2): 12, (2, 2, 0): 11, (2, 2, 2): 11}), "block distribution")
    require(structure["block_degree_sets"] == [[1, 2], [1, 2], [0, 1, 2]], "block degree sets")
    maxima = [max(term["exponents"][index] for term in terms) for index in range(9)]
    require(maxima == [2, 1, 2, 2, 2, 2, 1, 2, 1], "variable maxima replay")
    require(structure["per_variable_max_exponents"] == dict(zip(VARIABLES, maxima)), "variable maxima artifact")
    require(structure["terms_not_of_block_degree_2_2_2"] == 97, "nonhomogeneous term count")
    require(structure["terms_with_at_least_one_squared_variable"] == 44, "nonmultiaffine term count")
    require(structure["affine_block_homogeneous_of_degree_2_2_2"] is False, "false homogeneity classification")
    require(structure["affine_multiaffine"] is False, "false multiaffinity classification")
    first_block = structure["first_exact_block_homogeneity_counterexample"]
    require(first_block["block_degree"] != [2, 2, 2], "block counterexample")
    first_square = structure["first_exact_multiaffinity_counterexample"]
    require(max(first_square["exponents"]) == 2, "multiaffinity counterexample")
    homogenized = structure["canonical_trihomogenization"]
    require(homogenized["term_count"] == 108 and homogenized["block_degree"] == [2, 2, 2], "trihomogenization census")
    require(len(homogenized["terms"]) == 108, "trihomogenization terms")
    for original, lifted in zip(terms, homogenized["terms"]):
        degree = block_degree(original["exponents"])
        require(lifted["coefficient"] == original["coefficient"], "homogenized coefficient")
        require(lifted["exponents_a_b_c_d_e_f_g_h_i"] == original["exponents"], "homogenized exponent")
        require(lifted["homogenizer_exponents_u_v_w"] == [2 - value for value in degree], "homogenizer exponent")

    branch_frontier = candidate["decomposition_frontier"]
    require(branch_frontier["semantic_sha256"] == canonical_digest(without_semantic(branch_frontier)), "branch frontier semantic")
    require(branch_frontier["branch_order"] == ["MH-B00-AFFINE-SOURCE-STRUCTURE-CONTRACT"], "branch order")
    branch = branch_frontier["branches"][0]
    require(branch["semantic_sha256"] == canonical_digest(without_semantic(branch)), "branch semantic")
    require(branch["status"] == "UNRESOLVED_FAIL_CLOSED_SOURCE_STRUCTURE_MISMATCH", "branch status")
    require(branch["stop_rule_invoked"] == "STOP_ON_SOURCE_DRIFT", "stop rule")
    require(branch["characteristic_zero_decomposition_started"] is False, "decomposition start overclaim")
    require(branch["componentwise_parent_factor_tests_completed"] == 0, "incidence overclaim")
    require(branch_frontier["embedded_components_discarded"] == 0, "embedded loss")
    require(branch_frontier["singular_or_boundary_strata_discarded"] == 0, "stratum loss")

    incidence = candidate["parent_factor_incidence_frontier"]
    require(incidence["semantic_sha256"] == canonical_digest(without_semantic(incidence)), "incidence semantic")
    require(incidence["ordered_factor_count"] == len(incidence["records"]) == 70, "incidence factor count")
    require(incidence["completed_component_factor_pairs"] == 0, "component-factor pair overclaim")
    require(incidence["inverse_variable_discovery_used"] is False, "prohibited inverse discovery")
    inherited_factors = predecessor["factor_circuit"]["parent_factor_nodes"]
    for index, (record, inherited) in enumerate(zip(incidence["records"], inherited_factors)):
        require(record["factor_index"] == index, "factor index")
        require(record["factor_node_id"] == inherited["node_id"], "factor node id")
        require(record["sparse_polynomial"] == inherited["sparse_polynomial"], "factor source")
        require(record["componentwise_incidence_status"] == "PENDING_NO_COMPONENT_DECOMPOSITION", "factor status")
        require(record["semantic_sha256"] == canonical_digest(without_semantic(record)), "factor record semantic")

    require(candidate["preserved_boundary_frontier"] == predecessor["true_boundary_frontier"], "boundary preservation")
    require(candidate["preserved_fixed_skeleton_accounting"] == predecessor["fixed_skeleton_accounting"], "skeleton preservation")
    require(candidate["preserved_null_frontier"] == predecessor["verified_null_frontier"], "null frontier preservation")
    require(candidate["endpoint_accounting"] == {
        "negative": "NOT_REACHED_NO_EXACT_POSITIVE_DIMENSIONAL_REAL_STRICT_COMPONENT",
        "null": "REACHED_EXACT_SOURCE_STRUCTURE_MISMATCH_HASH_PINNED",
        "positive": "NOT_REACHED_NO_STRICT_SINGULAR_EMPTINESS_PROOF",
        "timeout": "NOT_REACHED",
    }, "endpoint accounting")
    resources = candidate["resource_accounting"]
    require(resources["component_decomposition_nodes_used"] == 0, "decomposition resource drift")
    require(resources["seventy_inverse_variable_discovery_used"] is False, "inverse resource drift")
    require(resources["numerical_or_modular_probe_used"] is False, "probe promotion")
    require(resources["ceiling_crossed"] is False, "ceiling")


def rehash(candidate: dict) -> None:
    candidate["semantic_sha256"] = canonical_digest(without_semantic(candidate))


def hostile_mutations(artifact: dict, predecessor: dict) -> tuple[int, int]:
    def mutate(path, value):
        def apply(candidate):
            target = candidate
            for key in path[:-1]:
                target = target[key]
            target[path[-1]] = value
            rehash(candidate)
        return apply

    mutations = [
        mutate(["classification"], "EXACT_STRICT_SINGULAR_EMPTINESS"),
        mutate(["endpoint"], "POSITIVE"),
        mutate(["theorem_ledger"], "3/9"),
        mutate(["ledger_change_recommended"], "promote"),
        mutate(["exact_affine_source_structure", "affine_block_homogeneous_of_degree_2_2_2"], True),
        mutate(["exact_affine_source_structure", "affine_multiaffine"], True),
        mutate(["exact_affine_source_structure", "block_degree_sets"], [[2], [2], [2]]),
        mutate(["exact_affine_source_structure", "terms_not_of_block_degree_2_2_2"], 0),
        mutate(["exact_affine_source_structure", "terms_with_at_least_one_squared_variable"], 0),
        mutate(["exact_affine_source_structure", "per_variable_max_exponents", "a"], 1),
        mutate(["exact_affine_source_structure", "canonical_trihomogenization", "term_count"], 107),
        mutate(["original_singular_jacobian_ideal", "generator_count"], 9),
        mutate(["original_singular_jacobian_ideal", "inverse_variables"], 70),
        mutate(["original_singular_jacobian_ideal", "generators", 1, "term_count"], 0),
        mutate(["decomposition_frontier", "branch_order"], []),
        mutate(["decomposition_frontier", "branches", 0, "status"], "RESOLVED"),
        mutate(["decomposition_frontier", "branches", 0, "stop_rule_invoked"], "CONTINUE"),
        mutate(["decomposition_frontier", "branches", 0, "characteristic_zero_decomposition_started"], True),
        mutate(["decomposition_frontier", "branches", 0, "componentwise_parent_factor_tests_completed"], 70),
        mutate(["decomposition_frontier", "embedded_components_discarded"], 1),
        mutate(["decomposition_frontier", "singular_or_boundary_strata_discarded"], 1),
        mutate(["parent_factor_incidence_frontier", "ordered_factor_count"], 69),
        mutate(["parent_factor_incidence_frontier", "completed_component_factor_pairs"], 1),
        mutate(["parent_factor_incidence_frontier", "inverse_variable_discovery_used"], True),
        mutate(["parent_factor_incidence_frontier", "records", 0, "factor_index"], 1),
        mutate(["parent_factor_incidence_frontier", "records", 1, "factor_node_id"], "H_MUTATED"),
        mutate(["parent_factor_incidence_frontier", "records", 2, "componentwise_incidence_status"], "KILLED"),
        mutate(["preserved_boundary_frontier", "proper_nonexcluded_candidate_strata"], 9),
        mutate(["preserved_fixed_skeleton_accounting", "parent_path_tag_checks"], 2799),
        mutate(["preserved_null_frontier", "connected_components_sampled"], 1),
        mutate(["resource_accounting", "component_decomposition_nodes_used"], 1),
        mutate(["resource_accounting", "seventy_inverse_variable_discovery_used"], True),
        mutate(["resource_accounting", "numerical_or_modular_probe_used"], True),
        mutate(["resource_accounting", "ceiling_crossed"], True),
    ]
    rejected = 0
    for mutation in mutations:
        candidate = deepcopy(artifact)
        mutation(candidate)
        try:
            validate(candidate, predecessor)
        except (AssertionError, KeyError, IndexError, TypeError):
            rejected += 1
    return rejected, len(mutations)


def validate_manifest(manifest: dict) -> None:
    require(manifest["semantic_sha256"] == canonical_digest(without_semantic(manifest)), "manifest semantic")
    require(manifest["canonical_base_revision"] == "9c9a78c4225a39803a0a5ac7e4e204d9b9f3773d", "manifest base")
    policy = manifest["source_policy"]
    require(policy["producer_code_imported"] is False, "producer import")
    require(policy["network_or_connector_used"] is False, "connector use")
    require(policy["numerical_or_modular_probe_used"] is False, "probe use")
    require(policy["seventy_inverse_variable_discovery_used"] is False, "inverse route")
    for relative, expected in manifest["pins"].items():
        require(source_digest(relative) == expected, f"manifest pin: {relative}")


def validate_result(result: dict, artifact: dict, manifest: dict) -> None:
    require(result["frontier_sha256"] == digest_path(FRONTIER), "result frontier hash")
    require(result["source_manifest_sha256"] == digest_path(MANIFEST), "result manifest hash")
    require(result["frontier_semantic_sha256"] == artifact["semantic_sha256"], "result frontier semantic")
    require(result["source_manifest_semantic_sha256"] == manifest["semantic_sha256"], "result manifest semantic")
    require(result["block_degree_sets"] == [[1, 2], [1, 2], [0, 1, 2]], "result block sets")
    require(result["per_variable_max_exponents"] == dict(zip(VARIABLES, [2, 1, 2, 2, 2, 2, 1, 2, 1])), "result maxima")
    require(result["terms_not_of_block_degree_2_2_2"] == 97, "result block counterexample count")
    require(result["terms_with_at_least_one_squared_variable"] == 44, "result multiaffinity counterexample count")
    require(result["characteristic_zero_decomposition_completed"] is False, "result decomposition overclaim")
    require(result["componentwise_parent_factor_tests_completed"] == 0, "result incidence overclaim")
    require(result["singular_or_boundary_strata_discarded"] == 0, "result strata")
    require(result["inverse_variable_discovery_used"] is False, "result inverse route")
    require(result["theorem_ledger"] == "2/9" and result["ledger_change_recommended"] == "none", "result ledger")


def main() -> None:
    require(digest_path(PREDECESSOR) == EXPECTED_PREDECESSOR_SHA256, "predecessor file pin")
    predecessor = json.loads(PREDECESSOR.read_text(encoding="utf-8"))
    artifact = json.loads(FRONTIER.read_text(encoding="utf-8"))
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    result = json.loads(RESULT.read_text(encoding="utf-8"))
    validate_manifest(manifest)
    validate(artifact, predecessor)
    validate_result(result, artifact, manifest)
    rejected, total = hostile_mutations(artifact, predecessor)
    require(rejected == total, f"hostile mutations rejected {rejected}/{total}")
    print("PASS exact affine source structure independently reconstructed")
    print("block_degree_sets=[[1,2],[1,2],[0,1,2]]")
    print("per_variable_max_exponents=[2,1,2,2,2,2,1,2,1]")
    print("terms_non_222=97 terms_with_square=44")
    print(f"hostile_mutations_rejected={rejected}/{total}")
    print(f"frontier_sha256={digest_path(FRONTIER)}")
    print("ledger=2/9")


if __name__ == "__main__":
    main()
