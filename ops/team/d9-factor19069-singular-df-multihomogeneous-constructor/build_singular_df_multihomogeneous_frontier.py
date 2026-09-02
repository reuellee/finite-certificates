#!/usr/bin/env python3
"""Build the exact factor-19069 affine source-structure frontier.

This builder is deliberately standard-library-only.  It reconstructs the
original nine-variable Jacobian ideal from the accepted predecessor's sparse
factor circuit and checks the selected cycle's claimed block homogeneity and
multiaffinity before attempting a decomposition.  The governed stop rule says
to stop on source drift, so a failed structure check is recorded as the first
fail-closed branch; it is never repaired by a numerical/modular calculation or
by the prohibited 70-inverse-variable discovery route.
"""

from __future__ import annotations

import argparse
from collections import Counter
from copy import deepcopy
from hashlib import sha256
import json
from pathlib import Path
import subprocess


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
CYCLE_ID = "2026-09-01-d9-row2599-factor19069-singular-df-multihomogeneous-gate1"
CYCLE = ROOT / "ops" / "research-team" / "cycles" / CYCLE_ID
PREDECESSOR = (
    ROOT
    / "ops"
    / "team"
    / "d9-factor19069-critical-equidim-constructor"
    / "CRITICAL_EQUIDIM_FRONTIER.json"
)
MANIFEST = HERE / "SOURCE_MANIFEST.json"
FRONTIER = HERE / "SINGULAR_DF_MULTIHOMOGENEOUS_FRONTIER.json"
RESULT = HERE / "RESULT.json"

VARIABLES = tuple("abcdefghi")
BLOCKS = ((0, 1, 2), (3, 4, 5), (6, 7, 8))
BLOCK_NAMES = ("abc", "def", "ghi")
BLOCK_BOUND = (2, 2, 2)
OPENING_REVISION = "a2860f3f6436f573a913fc8ca6312b944212aadd"
OPENING_TREE = "56f179cea8b8664156ee2dfcd6a9052d95e3b78e"
BASE_REVISION = "9c9a78c4225a39803a0a5ac7e4e204d9b9f3773d"
BASE_TREE = "af4bdbfc8f89e950936d59e6b0737b12eb5bdfb5"
PREDECESSOR_SHA256 = "4d7f4f21d0a5ab59ae42fa265d5a3cf851fa74dd1ff7069cd19209ec897d3a33"
PREDECESSOR_SEMANTIC_SHA256 = "28b4e989b42b526adf7b65e2c5f03d75396280d97f435faa03928a4f6f5228ae"
FACTOR_CIRCUIT_SEMANTIC_SHA256 = "0e10d3d4692a53a6040ea8822be05376775e9c674c74d532f42236d3dfb1a7cf"
MAX_EXACT_NODES = 500_000
HISTORICAL_CONTROL_PATHS = {
    "ops/research-team/PROTOCOL.md",
    "ops/research-team/verify_cycle_protocol.py",
}

EXTRA_PINS = {
    f"ops/research-team/cycles/{CYCLE_ID}/CYCLE.md":
        "9c8a51c141c8ab4742d580e50508f8cc544c6d6f211fe4b785b675f9c74f8055",
    f"ops/research-team/cycles/{CYCLE_ID}/OPENING_AUDIT.json":
        "d6fc28140be34ef7c77527ae3ef001ded849f269ffa0d92c541a4899262b4c3d",
    f"ops/research-team/cycles/{CYCLE_ID}/OBLIGATION_GRAPH.json":
        "6a01553079cb350f6a681bc5d19c8a584d3153eb106f49ff943ed4f1e99e709b",
    f"ops/research-team/cycles/{CYCLE_ID}/WORK_ORDERS.yaml":
        "921046f85cfe3bb83b9ac79a449e11a04d75074c1aa617e5118cb94e854243d5",
    "ops/team/d9-factor19069-critical-equidim-constructor/CRITICAL_EQUIDIM_FRONTIER.json":
        PREDECESSOR_SHA256,
    "ops/team/d9-factor19069-critical-equidim-constructor/SOURCE_MANIFEST.json":
        "06efc5d65274d7179728b9b89a1788ea4d33812bfb24ecd5235bdd0d294bd75b",
    "ops/team/d9-factor19069-critical-equidim-constructor/RESULT.json":
        "35619e34566ed01cfc749217e2b7f40842263e14108663d27b24687a6d7c7c6d",
    "ops/team/d9-factor19069-critical-equidim-certificate/RESULT.json":
        "48d45553f1910d08ed9d2af2fec29f9ef2b469665515670c3a523f02530f96c8",
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
    return sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":")).encode("ascii")
    ).hexdigest()


def json_bytes(value) -> bytes:
    return (json.dumps(value, indent=2, sort_keys=True) + "\n").encode("utf-8")


def sparse_derivative(terms: list[dict], coordinate: int) -> list[dict]:
    answer: dict[tuple[int, ...], int] = {}
    for term in terms:
        exponent = term["exponents"][coordinate]
        if exponent == 0:
            continue
        reduced = list(term["exponents"])
        reduced[coordinate] -= 1
        monomial = tuple(reduced)
        answer[monomial] = answer.get(monomial, 0) + term["coefficient"] * exponent
    return [
        {"coefficient": coefficient, "exponents": list(monomial)}
        for monomial, coefficient in sorted(answer.items())
        if coefficient
    ]


def block_degree(exponents: list[int]) -> tuple[int, int, int]:
    return tuple(sum(exponents[index] for index in block) for block in BLOCKS)


def counted_records(counter: Counter) -> list[dict]:
    return [
        {"degree": list(key) if isinstance(key, tuple) else key, "term_count": count}
        for key, count in sorted(counter.items())
    ]


def build_manifest(audit: dict) -> dict:
    require(audit["base_revision"] == BASE_REVISION, "base revision drift")
    require(audit["base_tree"] == BASE_TREE, "base tree drift")
    require(audit["opening_ledger"] == "2/9", "opening ledger drift")
    target = audit["target"]
    require(target["factor_id"] == 19069, "factor id drift")
    require(target["original_ring"] == "Q[a,b,c,d,e,f,g,h,i]", "ring drift")
    require(target["source_block_partition"] == [["a", "b", "c"], ["d", "e", "f"], ["g", "h", "i"]], "block partition drift")
    require(target["source_multidegree"] == [2, 2, 2], "declared multidegree drift")
    require(target["source_multiaffine_claim_requires_exact_check"] is True, "multiaffine check contract drift")
    require(target["parent_sign_factors"] == 70, "parent factor count drift")
    require(target["requires_characteristic_zero_decomposition"] is True, "decomposition obligation drift")

    pins = dict(audit["pins"])
    pins.update(EXTRA_PINS)
    for relative, expected in pins.items():
        require(source_digest(relative) == expected, f"source pin drift: {relative}")
    manifest = {
        "format": "d9-factor19069-singular-df-multihomogeneous-constructor-source-manifest-v1",
        "track_id": "d9-factor19069-singular-df-multihomogeneous-constructor",
        "cycle_id": CYCLE_ID,
        "cycle_opening_revision": OPENING_REVISION,
        "cycle_opening_tree": OPENING_TREE,
        "canonical_base_revision": BASE_REVISION,
        "canonical_base_tree": BASE_TREE,
        "pins": dict(sorted(pins.items())),
        "source_policy": {
            "predecessor_frontier_is_frozen_accepted_source": True,
            "producer_code_imported": False,
            "network_or_connector_used": False,
            "external_compute_used": False,
            "numerical_or_modular_probe_used": False,
            "seventy_inverse_variable_discovery_used": False,
        },
    }
    manifest["semantic_sha256"] = canonical_digest(manifest)
    return manifest


def reconstruct_source(predecessor: dict) -> tuple[dict, list[dict], dict]:
    require(predecessor["semantic_sha256"] == PREDECESSOR_SEMANTIC_SHA256, "predecessor semantic drift")
    require(predecessor["factor_circuit_semantic_sha256"] == FACTOR_CIRCUIT_SEMANTIC_SHA256, "factor circuit semantic drift")
    require(predecessor["theorem_ledger"] == "2/9", "predecessor ledger drift")
    circuit = predecessor["factor_circuit"]
    wall = circuit["wall_polynomial"]
    terms = deepcopy(wall["sparse_polynomial"])
    require(wall["node_id"] == "f_19069", "wall node drift")
    require(len(terms) == wall["term_count"] == 108, "wall term count drift")
    require(max(sum(term["exponents"]) for term in terms) == wall["degree"] == 6, "wall total-degree bound drift")
    require(wall["multidegree"] == [2, 2, 2], "stored multidegree tag drift")
    require(len(circuit["parent_factor_nodes"]) == 70, "parent factor count drift")

    derivatives = []
    for coordinate, variable in enumerate(VARIABLES):
        sparse = sparse_derivative(terms, coordinate)
        inherited = circuit["wall_derivative_nodes"][coordinate]
        require(inherited["coordinate_index"] == coordinate, "derivative coordinate drift")
        require(inherited["sparse_polynomial"] == sparse, f"df/d{variable} drift")
        node = {
            "node_id": f"df_d{variable}",
            "coordinate": variable,
            "coordinate_index": coordinate,
            "term_count": len(sparse),
            "sparse_polynomial": sparse,
        }
        node["semantic_sha256"] = canonical_digest(node)
        derivatives.append(node)

    total_degree_counts = Counter(sum(term["exponents"]) for term in terms)
    block_counts = Counter(block_degree(term["exponents"]) for term in terms)
    block_sets = [
        sorted({block_degree(term["exponents"])[block_index] for term in terms})
        for block_index in range(3)
    ]
    max_exponents = [max(term["exponents"][index] for term in terms) for index in range(9)]
    squared_term_count = sum(max(term["exponents"]) > 1 for term in terms)
    non_222_count = sum(block_degree(term["exponents"]) != BLOCK_BOUND for term in terms)
    first_non_222 = next(term for term in terms if block_degree(term["exponents"]) != BLOCK_BOUND)
    first_squared = next(term for term in terms if max(term["exponents"]) > 1)

    homogenized = []
    for term in terms:
        degree = block_degree(term["exponents"])
        homogenized.append(
            {
                "coefficient": term["coefficient"],
                "exponents_a_b_c_d_e_f_g_h_i": term["exponents"],
                "homogenizer_exponents_u_v_w": [BLOCK_BOUND[i] - degree[i] for i in range(3)],
            }
        )
    require(all(all(value >= 0 for value in term["homogenizer_exponents_u_v_w"]) for term in homogenized), "homogenization bound")

    structure = {
        "coefficient_field": "Q",
        "affine_ring": "Q[a,b,c,d,e,f,g,h,i]",
        "block_partition": [list(name) for name in BLOCK_NAMES],
        "stored_multidegree_tag": list(BLOCK_BOUND),
        "stored_multidegree_tag_exact_interpretation": "COORDINATEWISE_BLOCK_DEGREE_BOUND_NOT_AFFINE_BLOCK_HOMOGENEITY",
        "term_count": len(terms),
        "total_degree_bound": 6,
        "total_degree_distribution": counted_records(total_degree_counts),
        "block_degree_sets": block_sets,
        "block_degree_vector_distribution": counted_records(block_counts),
        "per_variable_max_exponents": dict(zip(VARIABLES, max_exponents)),
        "per_variable_exponent_sets": {
            variable: sorted({term["exponents"][coordinate] for term in terms})
            for coordinate, variable in enumerate(VARIABLES)
        },
        "affine_block_homogeneous_of_degree_2_2_2": False,
        "terms_not_of_block_degree_2_2_2": non_222_count,
        "first_exact_block_homogeneity_counterexample": {
            **deepcopy(first_non_222),
            "block_degree": list(block_degree(first_non_222["exponents"])),
        },
        "affine_multiaffine": False,
        "terms_with_at_least_one_squared_variable": squared_term_count,
        "first_exact_multiaffinity_counterexample": deepcopy(first_squared),
        "canonical_trihomogenization": {
            "ring": "Q[a,b,c,u,d,e,f,v,g,h,i,w]",
            "homogenizers": ["u", "v", "w"],
            "term_count": len(homogenized),
            "block_degree": list(BLOCK_BOUND),
            "terms": homogenized,
            "dehomogenization_identity": "F(a,b,c,1,d,e,f,1,g,h,i,1)=f_19069",
            "does_not_imply_affine_multiaffinity": True,
            "not_used_as_a_decomposition_certificate": True,
        },
    }
    structure["semantic_sha256"] = canonical_digest(structure)
    wall_source = {
        "node_id": "f_19069",
        "term_count": 108,
        "sparse_polynomial": terms,
    }
    wall_source["semantic_sha256"] = canonical_digest(wall_source)
    return wall_source, derivatives, structure


def parent_factor_frontier(predecessor: dict) -> list[dict]:
    records = []
    for index, factor in enumerate(predecessor["factor_circuit"]["parent_factor_nodes"]):
        require(factor["node_id"].startswith(f"H_{index:02d}_"), "parent factor order drift")
        record = {
            "factor_index": index,
            "factor_node_id": factor["node_id"],
            "degree": factor["degree"],
            "term_count": factor["term_count"],
            "sparse_polynomial": deepcopy(factor["sparse_polynomial"]),
            "source_semantic_sha256": canonical_digest(factor["sparse_polynomial"]),
            "componentwise_incidence_status": "PENDING_NO_COMPONENT_DECOMPOSITION",
            "strict_sign_status": "PENDING",
            "boundary_stratum_status": "RETAINED_FROM_PINNED_PREDECESSOR",
        }
        record["semantic_sha256"] = canonical_digest(record)
        records.append(record)
    require(len(records) == 70, "parent frontier count")
    return records


def build_frontier(predecessor: dict, manifest: dict) -> dict:
    wall, derivatives, structure = reconstruct_source(predecessor)
    parents = parent_factor_frontier(predecessor)
    jacobian = {
        "coefficient_field": "Q",
        "ring": "Q[a,b,c,d,e,f,g,h,i]",
        "monomial_order_reserved_for_future_decomposition": "graded_reverse_lexicographic_with_variable_precedence_a_b_c_d_e_f_g_h_i",
        "generators": [wall, *derivatives],
        "generator_node_ids": ["f_19069", *(f"df_d{variable}" for variable in VARIABLES)],
        "generator_count": 10,
        "derivatives_rebuilt_from_sparse_source": True,
        "inverse_variables": 0,
    }
    jacobian["semantic_sha256"] = canonical_digest(jacobian)

    branch = {
        "branch_id": "MH-B00-AFFINE-SOURCE-STRUCTURE-CONTRACT",
        "branch_kind": "PREREGISTERED_EXACT_SOURCE_STRUCTURE_CHECK",
        "coefficient_field": "Q",
        "input_ideal_semantic_sha256": jacobian["semantic_sha256"],
        "status": "UNRESOLVED_FAIL_CLOSED_SOURCE_STRUCTURE_MISMATCH",
        "reason": "THE_EXACT_AFFINE_FACTOR_IS_NEITHER_BLOCK_HOMOGENEOUS_OF_DEGREE_2_2_2_NOR_MULTIAFFINE_IN_a_THROUGH_i",
        "affine_block_homogeneous_claim": False,
        "affine_multiaffine_claim": False,
        "characteristic_zero_decomposition_started": False,
        "characteristic_zero_decomposition_completed": False,
        "component_count": None,
        "embedded_component_count": None,
        "dimensions": None,
        "degrees": None,
        "multiplicities": None,
        "componentwise_parent_factor_tests_completed": 0,
        "componentwise_parent_factor_tests_pending_per_future_component": 70,
        "strict_real_residence_status": "PENDING",
        "connected_row2599_parent_tag_status": "PENDING",
        "stop_rule_invoked": "STOP_ON_SOURCE_DRIFT",
    }
    branch["semantic_sha256"] = canonical_digest(branch)

    artifact = {
        "format": "d9-factor19069-singular-df-multihomogeneous-constructor-frontier-v1",
        "track_id": "d9-factor19069-singular-df-multihomogeneous-constructor",
        "cycle_id": CYCLE_ID,
        "opening_revision": OPENING_REVISION,
        "opening_tree": OPENING_TREE,
        "base_revision": BASE_REVISION,
        "base_tree": BASE_TREE,
        "outcome": "pass",
        "classification": "EXACT_SOURCE_STRUCTURE_FALSIFICATION_FAIL_CLOSED_NULL",
        "endpoint": "HASH_PIN_FIRST_UNRESOLVED_MULTIHOMOGENEOUS_SINGULAR_BRANCH",
        "source_manifest_semantic_sha256": manifest["semantic_sha256"],
        "predecessor_binding": {
            "path": "ops/team/d9-factor19069-critical-equidim-constructor/CRITICAL_EQUIDIM_FRONTIER.json",
            "sha256": PREDECESSOR_SHA256,
            "semantic_sha256": PREDECESSOR_SEMANTIC_SHA256,
            "factor_circuit_semantic_sha256": FACTOR_CIRCUIT_SEMANTIC_SHA256,
        },
        "exact_affine_source_structure": structure,
        "original_singular_jacobian_ideal": jacobian,
        "decomposition_frontier": {
            "branch_order": [branch["branch_id"]],
            "branches": [branch],
            "first_unresolved_branch_id": branch["branch_id"],
            "first_unresolved_branch_semantic_sha256": branch["semantic_sha256"],
            "resolved_component_count": 0,
            "pending_component_count": "UNKNOWN_BECAUSE_DECOMPOSITION_NOT_STARTED_AFTER_MANDATORY_SOURCE_STOP",
            "embedded_components_discarded": 0,
            "singular_or_boundary_strata_discarded": 0,
        },
        "parent_factor_incidence_frontier": {
            "ordered_factor_count": 70,
            "records": parents,
            "completed_component_factor_pairs": 0,
            "pending_factor_count_per_future_component": 70,
            "inverse_variable_discovery_used": False,
            "componentwise_saturation_may_be_used_only_after_exact_components_exist": True,
        },
        "preserved_boundary_frontier": deepcopy(predecessor["true_boundary_frontier"]),
        "preserved_fixed_skeleton_accounting": deepcopy(predecessor["fixed_skeleton_accounting"]),
        "preserved_null_frontier": deepcopy(predecessor["verified_null_frontier"]),
        "endpoint_accounting": {
            "positive": "NOT_REACHED_NO_STRICT_SINGULAR_EMPTINESS_PROOF",
            "negative": "NOT_REACHED_NO_EXACT_POSITIVE_DIMENSIONAL_REAL_STRICT_COMPONENT",
            "null": "REACHED_EXACT_SOURCE_STRUCTURE_MISMATCH_HASH_PINNED",
            "timeout": "NOT_REACHED",
        },
        "resource_accounting": {
            "resource_ceiling": {
                "wall_minutes": 75,
                "cpu_hours": 5,
                "memory_gib": 16,
                "max_exact_algebra_component_nodes": MAX_EXACT_NODES,
            },
            "exact_source_terms_checked": 108,
            "exact_derivatives_reconstructed": 9,
            "exact_jacobian_generators_constructed": 10,
            "parent_factor_nodes_preserved": 70,
            "component_decomposition_nodes_used": 0,
            "component_factor_pairs_tested": 0,
            "external_compute_used": False,
            "network_or_connector_used": False,
            "numerical_or_modular_probe_used": False,
            "seventy_inverse_variable_discovery_used": False,
            "ceiling_crossed": False,
        },
        "exact_consequence": "THE_PINNED_108_TERM_AFFINE_FACTOR_HAS_BLOCK_DEGREE_BOUNDS_2_2_2_BUT_IS_NOT_BLOCK_HOMOGENEOUS_AND_IS_NOT_MULTIAFFINE_IN_THE_ORIGINAL_NINE_COORDINATES",
        "nonconsequences": [
            "NO_CHARACTERISTIC_ZERO_PRIMARY_OR_EQUIDIMENSIONAL_DECOMPOSITION_OF_THE_SINGULAR_IDEAL",
            "NO_SINGULAR_COMPONENT_EQUATIONS_DIMENSIONS_DEGREES_OR_MULTIPLICITIES",
            "NO_COMPONENTWISE_PARENT_FACTOR_SATURATION_OR_INCIDENCE_CLASSIFICATION",
            "NO_STRICT_REAL_SINGULAR_COMPONENT_RESIDENCE_CLASSIFICATION",
            "NO_CONNECTED_ROW2599_PARENT_COMPONENT_TAG_FOR_A_SINGULAR_COMPONENT",
            "NO_SINGULAR_BRANCH_EMPTINESS_CERTIFICATE",
            "NO_THEOREM_LEVEL_COUNTEREXAMPLE",
            "NO_DIAGONAL_9_PROOF_OR_COUNTEREXAMPLE",
            "NO_9DVL_SCORE_CHANGE",
        ],
        "ledger_change_recommended": "none",
        "theorem_ledger": "2/9",
    }
    artifact["decomposition_frontier"]["semantic_sha256"] = canonical_digest(artifact["decomposition_frontier"])
    artifact["parent_factor_incidence_frontier"]["semantic_sha256"] = canonical_digest(artifact["parent_factor_incidence_frontier"])
    artifact["preserved_boundary_frontier_semantic_sha256"] = canonical_digest(artifact["preserved_boundary_frontier"])
    artifact["preserved_fixed_skeleton_semantic_sha256"] = canonical_digest(artifact["preserved_fixed_skeleton_accounting"])
    artifact["preserved_null_frontier_semantic_sha256"] = canonical_digest(artifact["preserved_null_frontier"])
    artifact["semantic_sha256"] = canonical_digest(artifact)
    return artifact


def build_result(artifact: dict, manifest: dict) -> dict:
    branch = artifact["decomposition_frontier"]["branches"][0]
    structure = artifact["exact_affine_source_structure"]
    return {
        "format": "d9-factor19069-singular-df-multihomogeneous-constructor-result-v1",
        "track_id": artifact["track_id"],
        "cycle_id": CYCLE_ID,
        "opening_revision": OPENING_REVISION,
        "opening_tree": OPENING_TREE,
        "outcome": "pass",
        "classification": artifact["classification"],
        "endpoint": artifact["endpoint"],
        "frontier_sha256": digest_path(FRONTIER),
        "frontier_semantic_sha256": artifact["semantic_sha256"],
        "source_manifest_sha256": digest_path(MANIFEST),
        "source_manifest_semantic_sha256": manifest["semantic_sha256"],
        "original_singular_ideal_semantic_sha256": artifact["original_singular_jacobian_ideal"]["semantic_sha256"],
        "source_structure_semantic_sha256": structure["semantic_sha256"],
        "first_unresolved_branch_id": branch["branch_id"],
        "first_unresolved_branch_semantic_sha256": branch["semantic_sha256"],
        "factor19069_terms": 108,
        "block_degree_sets": structure["block_degree_sets"],
        "per_variable_max_exponents": structure["per_variable_max_exponents"],
        "terms_not_of_block_degree_2_2_2": structure["terms_not_of_block_degree_2_2_2"],
        "terms_with_at_least_one_squared_variable": structure["terms_with_at_least_one_squared_variable"],
        "affine_block_homogeneous_of_degree_2_2_2": False,
        "affine_multiaffine": False,
        "characteristic_zero_decomposition_completed": False,
        "resolved_component_count": 0,
        "componentwise_parent_factor_tests_completed": 0,
        "parent_factor_tags_retained": 70,
        "true_boundary_candidate_strata_retained": 10,
        "singular_or_boundary_strata_discarded": 0,
        "inverse_variable_discovery_used": False,
        "ledger_change_recommended": "none",
        "theorem_ledger": "2/9",
        "nonconsequences": artifact["nonconsequences"],
    }


def write_or_check(path: Path, payload: bytes, check: bool) -> None:
    if check:
        require(path.read_bytes() == payload, f"byte replay drift: {path.name}")
    else:
        path.write_bytes(payload)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    require(digest_path(PREDECESSOR) == PREDECESSOR_SHA256, "predecessor file drift")
    audit = json.loads((CYCLE / "OPENING_AUDIT.json").read_text(encoding="utf-8"))
    predecessor = json.loads(PREDECESSOR.read_text(encoding="utf-8"))
    manifest = build_manifest(audit)
    artifact = build_frontier(predecessor, manifest)
    write_or_check(MANIFEST, json_bytes(manifest), args.check)
    write_or_check(FRONTIER, json_bytes(artifact), args.check)
    result = build_result(artifact, manifest)
    write_or_check(RESULT, json_bytes(result), args.check)
    print(f"frontier_semantic_sha256={artifact['semantic_sha256']}")
    print(f"source_structure_semantic_sha256={artifact['exact_affine_source_structure']['semantic_sha256']}")
    print(f"first_unresolved_branch={artifact['decomposition_frontier']['first_unresolved_branch_id']}")
    print("endpoint=HASH_PIN_FIRST_UNRESOLVED_MULTIHOMOGENEOUS_SINGULAR_BRANCH ledger=2/9")


if __name__ == "__main__":
    main()
