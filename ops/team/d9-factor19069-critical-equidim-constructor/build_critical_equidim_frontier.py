#!/usr/bin/env python3
"""Build the exact factor-19069 saturated critical-ideal frontier.

The accepted artifact is standard-library-only.  It reconstructs all sparse
derivatives from the hash-pinned predecessor circuit, introduces one inverse
variable for each of the 70 parent factors, and records an eliminationally
faithful localization of the saturated ideal.  It does not expand the degree
90 barrier and it does not turn an incomplete decomposition into a dimension
or real-component claim.
"""

from __future__ import annotations

from copy import deepcopy
from hashlib import sha256
import argparse
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
CYCLE = (
    ROOT
    / "ops"
    / "research-team"
    / "cycles"
    / "2026-09-01-d9-row2599-factor19069-critical-equidim-gate1"
)
PREDECESSOR_DIR = ROOT / "ops" / "team" / "d9-factor19069-factored-barrier-constructor"
PREDECESSOR = PREDECESSOR_DIR / "FACTORED_BARRIER_FRONTIER.json"
OPENING_AUDIT = CYCLE / "OPENING_AUDIT.json"
OUTPUT = HERE / "CRITICAL_EQUIDIM_FRONTIER.json"
MANIFEST = HERE / "SOURCE_MANIFEST.json"
RESULT = HERE / "RESULT.json"

VARIABLES = tuple("abcdefghi")
OPENING_REVISION = "f196f949b2a2981ea1b21019e4a2bf56302a683a"
OPENING_TREE = "7a5eaa91d1448defed2e77363b5e97cf93b97489"
PREDECESSOR_SHA256 = "3f75eeb2f7433234206292012c527604517b516ee904e2ab1d1969e49ed1e8ca"
PREDECESSOR_SEMANTIC_SHA256 = "7686b6fe5af6b7d50418c105d2fe5036bf2c660dde1cfe70c0e1ab7a4ce8c50c"
FACTOR_CIRCUIT_SEMANTIC_SHA256 = "0e10d3d4692a53a6040ea8822be05376775e9c674c74d532f42236d3dfb1a7cf"
PREDECESSOR_STRATUM_SHA256 = "103ac3707fc12deeb74141ee916f42667f2210ad7fcf718b119eeaa58b62a6a0"
MAX_EXACT_NODES = 500_000


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def digest_path(path: Path) -> str:
    state = sha256()
    with path.open("rb") as source:
        for block in iter(lambda: source.read(1 << 20), b""):
            state.update(block)
    return state.hexdigest()


def canonical_digest(value) -> str:
    return sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":")).encode("ascii")
    ).hexdigest()


def sparse_derivative(terms: list[dict], coordinate: int) -> list[dict]:
    answer: dict[tuple[int, ...], int] = {}
    for term in terms:
        exponent = term["exponents"][coordinate]
        if not exponent:
            continue
        reduced = list(term["exponents"])
        reduced[coordinate] -= 1
        monomial = tuple(reduced)
        answer[monomial] = answer.get(monomial, 0) + term["coefficient"] * exponent
    return [
        {"exponents": list(monomial), "coefficient": coefficient}
        for monomial, coefficient in sorted(answer.items())
        if coefficient
    ]


def sparse_degree(terms: list[dict]) -> int:
    return max(sum(term["exponents"]) for term in terms)


def build_source_manifest(audit: dict) -> dict:
    require(audit["base_revision"] == OPENING_REVISION, "opening revision drift")
    require(audit["base_tree"] == OPENING_TREE, "opening tree drift")
    require(audit["opening_ledger"] == "2/9", "opening ledger drift")
    require(audit["target"]["factor_id"] == 19069, "factor drift")
    require(audit["target"]["parent_sign_factors"] == 70, "parent factor count drift")
    require(audit["target"]["wedge_equations"] == 36, "wedge count drift")
    require(
        audit["target"]["barrier_representation"] == "UNEXPANDED_FACTORED_CIRCUIT",
        "barrier representation drift",
    )
    require(
        audit["target"]["null_endpoint"] == "HASH_PIN_FIRST_UNRESOLVED_SATURATED_IDEAL_BRANCH",
        "null endpoint drift",
    )

    pins = dict(audit["pins"])
    pins.update(
        {
            "ops/research-team/cycles/2026-09-01-d9-row2599-factor19069-critical-equidim-gate1/OPENING_AUDIT.json": digest_path(OPENING_AUDIT),
            "ops/research-team/cycles/2026-09-01-d9-row2599-factor19069-critical-equidim-gate1/CYCLE.md": digest_path(CYCLE / "CYCLE.md"),
            "ops/research-team/cycles/2026-09-01-d9-row2599-factor19069-critical-equidim-gate1/WORK_ORDERS.yaml": digest_path(CYCLE / "WORK_ORDERS.yaml"),
        }
    )
    for relative, expected in pins.items():
        require(digest_path(ROOT / relative) == expected, f"source pin drift: {relative}")

    manifest = {
        "format": "d9-factor19069-critical-equidim-constructor-source-manifest-v1",
        "track_id": "d9-factor19069-critical-equidim-constructor",
        "opening_revision": OPENING_REVISION,
        "opening_tree": OPENING_TREE,
        "pins": dict(sorted(pins.items())),
        "source_policy": {
            "predecessor_frontier_is_frozen_accepted_source": True,
            "producer_code_imported": False,
            "network_or_connector_used": False,
            "external_compute_used": False,
        },
    }
    manifest["semantic_sha256"] = canonical_digest(manifest)
    return manifest


def validate_and_reconstruct_factor_circuit(predecessor: dict) -> tuple[dict, list[dict]]:
    require(predecessor["semantic_sha256"] == PREDECESSOR_SEMANTIC_SHA256, "predecessor semantic drift")
    require(
        predecessor["factor_circuit_semantic_sha256"] == FACTOR_CIRCUIT_SEMANTIC_SHA256,
        "factor circuit semantic drift",
    )
    require(predecessor["theorem_ledger"] == "2/9", "predecessor ledger drift")
    circuit = deepcopy(predecessor["factor_circuit"])
    factors = circuit["parent_factor_nodes"]
    require(len(factors) == 70, "parent factor count")
    require(circuit["barrier"]["factor_count"] == 70, "barrier factor count")
    require(circuit["barrier"]["total_degree"] == 90, "barrier degree")
    require(circuit["barrier"]["expanded_polynomial_present"] is False, "barrier expansion")
    require(len(circuit["barrier_derivative_nodes"]) == 9, "barrier derivative count")
    require(len(circuit["wall_derivative_nodes"]) == 9, "wall derivative count")
    require(len(circuit["wedge_equation_nodes"]) == 36, "inherited wedge count")

    ordered_ids = [factor["node_id"] for factor in factors]
    require(circuit["barrier"]["ordered_factor_node_ids"] == ordered_ids, "factor order drift")
    require(sum(factor["term_count"] for factor in factors) == 209, "parent sparse term count")
    require(sum(factor["degree"] for factor in factors) == 90, "parent degree sum")

    for coordinate, derivative_node in enumerate(circuit["barrier_derivative_nodes"]):
        require(derivative_node["coordinate_index"] == coordinate, "barrier derivative coordinate")
        require(len(derivative_node["summands"]) == 70, "barrier derivative summand count")
        for index, summand in enumerate(derivative_node["summands"]):
            require(summand["differentiated_factor_index"] == index, "dB factor index")
            require(summand["multiply_all_factor_indices_except"] == index, "dB product omission")
            expected = sparse_derivative(factors[index]["sparse_polynomial"], coordinate)
            require(summand["derivative_sparse_polynomial"] == expected, "dB sparse derivative drift")

    wall_terms = circuit["wall_polynomial"]["sparse_polynomial"]
    require(circuit["wall_polynomial"]["node_id"] == "f_19069", "wall identity")
    require(circuit["wall_polynomial"]["term_count"] == len(wall_terms) == 108, "wall term count")
    require(circuit["wall_polynomial"]["degree"] == sparse_degree(wall_terms) == 6, "wall degree")
    wall_derivatives = []
    for coordinate, node in enumerate(circuit["wall_derivative_nodes"]):
        expected = sparse_derivative(wall_terms, coordinate)
        require(node["coordinate_index"] == coordinate, "df coordinate")
        require(node["sparse_polynomial"] == expected, "df sparse derivative drift")
        wall_derivatives.append(deepcopy(node))
    return circuit, wall_derivatives


def build_localized_ideal(circuit: dict, wall_derivatives: list[dict]) -> dict:
    factors = circuit["parent_factor_nodes"]
    inverse_relations = []
    log_nodes = []
    for index, factor in enumerate(factors):
        inverse_relations.append(
            {
                "node_id": f"invrel_{index:02d}",
                "equation": f"{factor['node_id']}*y_{index:02d}-1=0",
                "factor_node_id": factor["node_id"],
                "inverse_variable": f"y_{index:02d}",
            }
        )
    for coordinate, variable in enumerate(VARIABLES):
        summands = []
        for index, factor in enumerate(factors):
            summands.append(
                {
                    "factor_index": index,
                    "factor_node_id": factor["node_id"],
                    "inverse_variable": f"y_{index:02d}",
                    "factor_derivative_sparse_polynomial": sparse_derivative(
                        factor["sparse_polynomial"], coordinate
                    ),
                }
            )
        log_nodes.append(
            {
                "node_id": f"L_{variable}",
                "coordinate_index": coordinate,
                "operation": "SUM_i_y_i_TIMES_dH_i",
                "summands": summands,
            }
        )

    localized_wedges = []
    for left in range(9):
        for right in range(left + 1, 9):
            localized_wedges.append(
                {
                    "node_id": f"logwedge_{VARIABLES[left]}_{VARIABLES[right]}",
                    "coordinate_pair": [left, right],
                    "equation": (
                        f"L_{VARIABLES[left]}*{wall_derivatives[right]['node_id']}"
                        f"-L_{VARIABLES[right]}*{wall_derivatives[left]['node_id']}=0"
                    ),
                }
            )
    require(len(localized_wedges) == 36, "localized wedge count")

    ideal = {
        "format": "d9-factor19069-localized-critical-ideal-circuit-v1",
        "coefficient_field": "Q",
        "base_variables": list(VARIABLES),
        "inverse_variables": [f"y_{index:02d}" for index in range(70)],
        "barrier_product_node": "B=PRODUCT_ORDERED(H_00,...,H_69)",
        "barrier_product_expanded": False,
        "wall_generator_node_id": "f_19069",
        "inverse_relations": inverse_relations,
        "log_gradient_nodes": log_nodes,
        "localized_wedge_nodes": localized_wedges,
        "generator_node_ids": [
            "f_19069",
            *(relation["node_id"] for relation in inverse_relations),
            *(node["node_id"] for node in localized_wedges),
        ],
        "generator_count": 107,
        "saturation_contract": "<f_19069,W_ij>:(PRODUCT_i_H_i)^infinity",
        "localization_contract": "<f_19069,H_i*y_i-1,logwedge_ij> in Q[x_0..x_8,y_00..y_69]",
        "elimination_contract": "CONTRACT_TO_Q[x_0..x_8]_EQUALS_SATURATED_CRITICAL_IDEAL",
        "elimination_faithfulness_proof": [
            "The 70 equations H_i*y_i-1 identify the extension ring with Q[x_0..x_8,(PRODUCT_i_H_i)^(-1)].",
            "In that localization y_i=H_i^(-1) and dB_k=B*SUM_i(y_i*dH_i/dx_k)=B*L_k.",
            "Therefore W_ij=(dB_i)(df_j)-(dB_j)(df_i)=B*(L_i*df_j-L_j*df_i).",
            "B is a unit in the inverse extension, so the original and localized wedge ideals coincide there.",
            "Contraction from the localization is saturation by PRODUCT_i_H_i; no coordinate projection or barrier expansion is used.",
        ],
        "derived_product_inverse_witness": {
            "inverse_circuit": "PRODUCT_i_y_i",
            "identity": "B*(PRODUCT_i_y_i)-1=0",
            "derivation": "PRODUCT_OF_ALL_70_INVERSE_RELATIONS",
            "expanded_product_used": False,
        },
        "lambda_replacement_used": False,
        "singular_df_zero_branch_retained": True,
    }
    ideal["semantic_sha256"] = canonical_digest(ideal)
    return ideal


def branch_with_digest(branch: dict) -> dict:
    branch = deepcopy(branch)
    branch["semantic_sha256"] = canonical_digest(branch)
    return branch


def build_branch_frontier(localized: dict, wall_derivatives: list[dict]) -> dict:
    inverse_ids = [relation["node_id"] for relation in localized["inverse_relations"]]
    df_ids = [node["node_id"] for node in wall_derivatives]
    singular = branch_with_digest(
        {
            "branch_id": "EQ-B00-SINGULAR-DF-ZERO",
            "branch_kind": "CLOSED_SINGULAR_WALL_BRANCH_IN_NONBOUNDARY_LOCALIZATION",
            "coefficient_field": "Q",
            "variables": [*VARIABLES, *(f"y_{index:02d}" for index in range(70))],
            "monomial_order": "graded_reverse_lexicographic",
            "variable_precedence": [*VARIABLES, *(f"y_{index:02d}" for index in range(70))],
            "generator_node_ids": ["f_19069", *inverse_ids, *df_ids],
            "generator_count": 80,
            "critical_wedges_status": "REDUNDANT_MODULO_ALL_NINE_df_GENERATORS",
            "saturation_status": "EXACT_VIA_ALL_70_INVERSE_RELATIONS",
            "equidimensional_decomposition_status": "UNRESOLVED_FAIL_CLOSED",
            "complex_dimension": None,
            "degree": None,
            "multiplicity_data": None,
            "possible_complex_dimensions": ["EMPTY", 0, 1, 2, 3, 4, 5, 6, 7, 8],
            "exact_real_strict_parent_point": None,
            "strict_parent_component_residence": "UNRESOLVED",
        }
    )

    regular = []
    for pivot in range(9):
        pivot_df = df_ids[pivot]
        critical_ids = [
            f"logwedge_{VARIABLES[min(pivot, other)]}_{VARIABLES[max(pivot, other)]}"
            for other in range(9)
            if other != pivot
        ]
        regular.append(
            branch_with_digest(
                {
                    "branch_id": f"EQ-B{pivot + 1:02d}-REGULAR-PIVOT-{VARIABLES[pivot]}",
                    "branch_kind": "LEX_FIRST_NONZERO_df_PIVOT_CHART",
                    "coefficient_field": "Q",
                    "variables": [
                        *VARIABLES,
                        *(f"y_{index:02d}" for index in range(70)),
                        f"q_{VARIABLES[pivot]}",
                    ],
                    "monomial_order": "graded_reverse_lexicographic",
                    "variable_precedence": [
                        *VARIABLES,
                        *(f"y_{index:02d}" for index in range(70)),
                        f"q_{VARIABLES[pivot]}",
                    ],
                    "generator_node_ids": [
                        "f_19069",
                        *inverse_ids,
                        *df_ids[:pivot],
                        f"pivot_invrel_{VARIABLES[pivot]}",
                        *critical_ids,
                    ],
                    "pivot_inverse_relation": (
                        f"pivot_invrel_{VARIABLES[pivot]}:"
                        f"q_{VARIABLES[pivot]}*{pivot_df}-1=0"
                    ),
                    "pivot_critical_equations": critical_ids,
                    "generator_count": 1 + 70 + pivot + 1 + 8,
                    "saturation_status": "EXACT_VIA_70_FACTOR_INVERSES_AND_PIVOT_INVERSE",
                    "equidimensional_decomposition_status": "PENDING_AFTER_FIRST_UNRESOLVED_BRANCH",
                    "complex_dimension": None,
                    "degree": None,
                    "multiplicity_data": None,
                    "exact_real_strict_parent_point": None,
                    "strict_parent_component_residence": "PENDING",
                }
            )
        )

    frontier = {
        "format": "d9-factor19069-critical-equidim-branch-frontier-v1",
        "cover_contract": (
            "SINGULAR_df_ZERO_UNION_LEX_FIRST_NONZERO_df_REGULAR_CHARTS_"
            "COVERS_THE_LOCALIZED_CRITICAL_LOCUS_SET_THEORETICALLY"
        ),
        "scheme_decomposition_claimed": False,
        "branch_order": [singular["branch_id"], *(branch["branch_id"] for branch in regular)],
        "branches": [singular, *regular],
        "resolved_branch_count": 0,
        "pending_branch_count": 10,
        "first_unresolved_branch_id": singular["branch_id"],
        "first_unresolved_branch_semantic_sha256": singular["semantic_sha256"],
        "first_unresolved_obligation": (
            "EXACT_EQUIDIMENSIONAL_DECOMPOSITION_OVER_Q_OF_THE_SATURATED_"
            "SINGULAR_WALL_BRANCH_WITH_DIMENSION_DEGREE_AND_MULTIPLICITY_DATA"
        ),
        "positive_dimensional_complex_piece_status": "UNRESOLVED",
        "positive_dimensional_real_strict_piece_status": "UNRESOLVED",
        "zero_dimensional_status": "NOT_PROVED",
        "complete_real_root_frontier_status": "NOT_CONSTRUCTED",
    }
    frontier["semantic_sha256"] = canonical_digest(frontier)
    return frontier


def build_artifact(predecessor: dict, manifest: dict) -> dict:
    circuit, wall_derivatives = validate_and_reconstruct_factor_circuit(predecessor)
    localized = build_localized_ideal(circuit, wall_derivatives)
    branches = build_branch_frontier(localized, wall_derivatives)
    predecessor_system = predecessor["strict_interior_critical_frontier"]["systems"][0]
    require(predecessor_system["semantic_sha256"] == PREDECESSOR_STRATUM_SHA256, "predecessor stratum drift")

    node_breakdown = {
        "parent_factor_nodes": 70,
        "barrier_product_nodes": 1,
        "inherited_barrier_derivative_summands": 630,
        "inherited_barrier_derivative_sum_nodes": 9,
        "wall_polynomial_nodes": 1,
        "wall_derivative_nodes": 9,
        "inherited_wedge_nodes": 36,
        "factor_inverse_relations": 70,
        "log_gradient_summands": 630,
        "log_gradient_sum_nodes": 9,
        "localized_wedge_nodes": 36,
        "branch_descriptors": 10,
        "regular_pivot_inverse_relations": 9,
    }
    require(sum(node_breakdown.values()) == 1520, "node accounting")

    artifact = {
        "format": "d9-factor19069-critical-equidim-constructor-frontier-v1",
        "track_id": "d9-factor19069-critical-equidim-constructor",
        "cycle_id": "2026-09-01-d9-row2599-factor19069-critical-equidim-gate1",
        "opening_revision": OPENING_REVISION,
        "opening_tree": OPENING_TREE,
        "classification": "EXACT_FAIL_CLOSED_SATURATED_EQUIDIMENSIONAL_DECOMPOSITION_NULL",
        "endpoint": "HASH_PIN_FIRST_UNRESOLVED_SATURATED_IDEAL_BRANCH",
        "outcome": "pass",
        "target": {
            "parent_index": 2599,
            "factor_id": 19069,
            "ambient_parameter_dimension": 9,
            "barrier_parent_factor_count": 70,
            "barrier_total_degree": 90,
            "barrier_representation": "UNEXPANDED_FACTORED_CIRCUIT",
            "wedge_equation_count": 36,
        },
        "source_manifest_semantic_sha256": manifest["semantic_sha256"],
        "predecessor_binding": {
            "frontier_sha256": PREDECESSOR_SHA256,
            "frontier_semantic_sha256": PREDECESSOR_SEMANTIC_SHA256,
            "factor_circuit_semantic_sha256": FACTOR_CIRCUIT_SEMANTIC_SHA256,
            "strict_interior_system_semantic_sha256": PREDECESSOR_STRATUM_SHA256,
            "verified_null_frontier_preserved": True,
        },
        "factor_circuit": circuit,
        "factor_circuit_semantic_sha256": FACTOR_CIRCUIT_SEMANTIC_SHA256,
        "localized_critical_ideal": localized,
        "equidimensional_branch_frontier": branches,
        "raw_wall_context_only": {
            "wall_node_id": "f_19069",
            "nonzero_sparse_polynomial": True,
            "ambient_affine_hypersurface_dimension": 8,
            "total_degree": 6,
            "critical_branch_dimension_or_degree_claim": False,
            "warning": "These hypersurface invariants do not resolve any saturated critical branch.",
        },
        "strict_parent_component_selector": {
            "strict_inequalities": predecessor_system["strict_inequalities"],
            "connected_parent_selector": predecessor_system["connected_parent_selector"],
            "source_derived_parent_tag": "ROW2599_PINNED_CONNECTED_PARENT_COMPONENT",
            "complex_localization_does_not_prove_real_residence": True,
            "real_path_certificate_required_for_each_positive_dimensional_piece": True,
        },
        "singular_strata_accounting": {
            "df_zero_branch_id": "EQ-B00-SINGULAR-DF-ZERO",
            "df_zero_branch_omitted": False,
            "lambda_only_replacement_prohibited": True,
            "singular_branch_real_residence": "UNRESOLVED",
        },
        "true_boundary_frontier": deepcopy(predecessor["true_boundary_frontier"]),
        "fixed_skeleton_accounting": deepcopy(predecessor["fixed_skeleton_accounting"]),
        "verified_null_frontier": {
            "predecessor_strict_interior_critical_frontier": deepcopy(
                predecessor["strict_interior_critical_frontier"]
            ),
            "connected_components_sampled": 0,
            "positive_dimensional_components_sampled": 0,
            "edge39_anchor_is_barrier_critical_sample": False,
            "global_attachment_classification_complete": False,
        },
        "resource_accounting": {
            "resource_ceiling": {
                "wall_minutes": 75,
                "cpu_hours": 5,
                "memory_gib": 16,
                "max_exact_algebra_component_nodes": MAX_EXACT_NODES,
            },
            "declared_exact_circuit_node_convention": node_breakdown,
            "declared_exact_circuit_nodes_constructed": 1520,
            "equidimensional_decomposition_nodes_completed": 0,
            "component_samples_computed": 0,
            "barrier_expansion_nodes": 0,
            "ceiling_crossed": False,
            "exploratory_sympy_probes_used_for_claims": False,
            "first_pending_operation": (
                "GREVLEX_EQUIDIMENSIONAL_DECOMPOSITION_OVER_Q_OF_"
                "EQ-B00-SINGULAR-DF-ZERO_IN_THE_79_VARIABLE_INVERSE_EXTENSION"
            ),
        },
        "exact_consequence": (
            "THE_SATURATED_FACTOR19069_CRITICAL_IDEAL_HAS_AN_EXACT_70_INVERSE_"
            "LOCALIZATION_CIRCUIT_AND_A_SINGULAR_FIRST_BRANCH_BUT_NO_BRANCH_"
            "DIMENSION_DEGREE_OR_MULTIPLICITY_IS_CERTIFIED"
        ),
        "nonconsequences": [
            "NO_EQUIDIMENSIONAL_DECOMPOSITION_OF_ANY_SATURATED_CRITICAL_BRANCH",
            "NO_PROOF_THAT_THE_STRICT_CRITICAL_LOCUS_IS_ZERO_DIMENSIONAL",
            "NO_COMPLETE_REAL_ROOT_COUNT_OR_THOM_FRONTIER",
            "NO_EXACT_POSITIVE_DIMENSIONAL_REAL_STRICT_CRITICAL_COMPONENT",
            "NO_CRITICAL_BRANCH_DEGREE_OR_MULTIPLICITY_DATA",
            "NO_SINGULAR_BRANCH_EMPTINESS_OR_REAL_RESIDENCE_CERTIFICATE",
            "NO_BOUNDARY_WALL_GERM_TO_INTERIOR_COMPONENT_CLASSIFICATION",
            "NO_GLOBAL_FACTOR19069_WALL_COMPONENT_OR_ATTACHMENT_COUNT",
            "NO_DIAGONAL_9_PROOF_OR_COUNTEREXAMPLE",
            "NO_9DVL_SCORE_CHANGE",
        ],
        "ledger_change_recommended": "none",
        "theorem_ledger": "2/9",
    }
    artifact["semantic_sha256"] = canonical_digest(artifact)
    return artifact


def build_result(artifact: dict, manifest: dict) -> dict:
    first = artifact["equidimensional_branch_frontier"]
    return {
        "format": "d9-factor19069-critical-equidim-constructor-result-v1",
        "track_id": "d9-factor19069-critical-equidim-constructor",
        "opening_revision": OPENING_REVISION,
        "opening_tree": OPENING_TREE,
        "outcome": "pass",
        "classification": artifact["classification"],
        "endpoint": artifact["endpoint"],
        "frontier_sha256": digest_path(OUTPUT),
        "frontier_semantic_sha256": artifact["semantic_sha256"],
        "source_manifest_sha256": digest_path(MANIFEST),
        "source_manifest_semantic_sha256": manifest["semantic_sha256"],
        "factor_circuit_semantic_sha256": FACTOR_CIRCUIT_SEMANTIC_SHA256,
        "localized_critical_ideal_semantic_sha256": artifact["localized_critical_ideal"]["semantic_sha256"],
        "branch_frontier_semantic_sha256": first["semantic_sha256"],
        "first_unresolved_branch_id": first["first_unresolved_branch_id"],
        "first_unresolved_branch_semantic_sha256": first["first_unresolved_branch_semantic_sha256"],
        "resolved_branch_count": 0,
        "pending_branch_count": 10,
        "critical_dimensions_degrees_multiplicities_certified": False,
        "exact_positive_dimensional_real_component_certified": False,
        "zero_dimensional_strict_locus_certified": False,
        "barrier_expanded": False,
        "singular_branch_retained": True,
        "true_boundary_candidate_strata_retained": 10,
        "parent_factor_tags_retained": 70,
        "edge39_anchor_preserved_as_noncritical": True,
        "ledger_change_recommended": "none",
        "theorem_ledger": "2/9",
        "nonconsequences": artifact["nonconsequences"],
    }


def json_bytes(value) -> bytes:
    return (json.dumps(value, indent=2, sort_keys=True) + "\n").encode("utf-8")


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
    audit = json.loads(OPENING_AUDIT.read_text(encoding="utf-8"))
    predecessor = json.loads(PREDECESSOR.read_text(encoding="utf-8"))
    manifest = build_source_manifest(audit)
    artifact = build_artifact(predecessor, manifest)

    write_or_check(MANIFEST, json_bytes(manifest), args.check)
    write_or_check(OUTPUT, json_bytes(artifact), args.check)
    result = build_result(artifact, manifest)
    write_or_check(RESULT, json_bytes(result), args.check)

    print(f"frontier_semantic_sha256={artifact['semantic_sha256']}")
    print(
        "first_unresolved_branch="
        f"{artifact['equidimensional_branch_frontier']['first_unresolved_branch_id']}"
    )
    print("endpoint=HASH_PIN_FIRST_UNRESOLVED_SATURATED_IDEAL_BRANCH ledger=2/9")


if __name__ == "__main__":
    main()
