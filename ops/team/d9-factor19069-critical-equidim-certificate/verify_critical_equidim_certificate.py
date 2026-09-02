#!/usr/bin/env python3
"""Producer-independent certificate for the factor-19069 equidimensional gate.

The constructor payload is data only.  This verifier imports no constructor,
falsifier, or predecessor-certificate module.  It rebuilds the ordered parent
factors and factor 19069 from the canonical mathematical sources, then checks
the saturated-ideal handoff and its exact fail-closed decomposition frontier.
"""

from __future__ import annotations

import ast
from copy import deepcopy
from hashlib import sha256
import json
from pathlib import Path
import subprocess
import sys


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
OMREAL = ROOT / "ai" / "omreal"
DATA = OMREAL / "data"
OPENING = ROOT / "ops" / "research-team" / "cycles" / "2026-09-01-d9-row2599-factor19069-critical-equidim-gate1" / "OPENING_AUDIT.json"
PREDECESSOR = ROOT / "ops" / "team" / "d9-factor19069-factored-barrier-constructor" / "FACTORED_BARRIER_FRONTIER.json"
CONSTRUCTOR = ROOT / "ops" / "team" / "d9-factor19069-critical-equidim-constructor"
FRONTIER = CONSTRUCTOR / "CRITICAL_EQUIDIM_FRONTIER.json"
CONSTRUCTOR_RESULT = CONSTRUCTOR / "RESULT.json"
CONSTRUCTOR_MANIFEST = CONSTRUCTOR / "SOURCE_MANIFEST.json"
RESULT = HERE / "RESULT.json"
BASE = "f196f949b2a2981ea1b21019e4a2bf56302a683a"
BASE_TREE = "7a5eaa91d1448defed2e77363b5e97cf93b97489"
REVIEWED = "951498b19c17886ffbf3b32d938dd741903d99a7"
REVIEWED_TREE = "f90cb55cdc51dd3ca0b077ba62e384e5df96e094"
HISTORICAL_CONTROL_PATHS = {
    "ops/research-team/PROTOCOL.md",
    "ops/research-team/verify_cycle_protocol.py",
    "ops/team/d9-factor19069-factored-barrier-referee/verify_closing_referee.py",
}
TARGET = "D9_ROW2599_FACTOR19069_FACTORED_CRITICAL_EQUIDIMENSIONAL_DECOMPOSITION_GATE1"
TARGET_FACTOR = 19069
VARIABLES = tuple("abcdefghi")
FULL_SUPPORT = [15, 15, 15]
POSITIVE = "PROVE_STRICT_CRITICAL_LOCUS_ZERO_DIMENSIONAL_WITH_COMPLETE_REAL_ROOT_COUNT_FRONTIER"
NEGATIVE = "EXHIBIT_EXACT_POSITIVE_DIMENSIONAL_REAL_CRITICAL_COMPONENT"
NULL = "HASH_PIN_FIRST_UNRESOLVED_SATURATED_IDEAL_BRANCH"
TIMEOUT = "HASH_PIN_COMPLETED_AND_PENDING_EQUIDIMENSIONAL_DECOMPOSITION_FRONTIER"
PREDECESSOR_SHA256 = "3f75eeb2f7433234206292012c527604517b516ee904e2ab1d1969e49ed1e8ca"
CONSTRUCTOR_PINS = {
    "ops/team/d9-factor19069-critical-equidim-constructor/CRITICAL_EQUIDIM_FRONTIER.json": "4d7f4f21d0a5ab59ae42fa265d5a3cf851fa74dd1ff7069cd19209ec897d3a33",
    "ops/team/d9-factor19069-critical-equidim-constructor/RESULT.json": "35619e34566ed01cfc749217e2b7f40842263e14108663d27b24687a6d7c7c6d",
    "ops/team/d9-factor19069-critical-equidim-constructor/SOURCE_MANIFEST.json": "06efc5d65274d7179728b9b89a1788ea4d33812bfb24ecd5235bdd0d294bd75b",
    "ops/team/d9-factor19069-critical-equidim-constructor/verify_critical_equidim_frontier.py": "3897be806048574e62b69f872050e176b9800db732ec626439c6a6f5ecaa5ab5",
}
CANONICAL_SOURCE_PINS = {
    "ai/omreal/DIAG2_PIVOT_LABELED_PAIR_ORBITS_VERIFY.py": "8f51cf73ea75b4de7baf38af19b6e4cc941293edb82216a4aa00feef83c38e26",
    "ai/omreal/verify_diag3_pair_global_parent_face_gate.py": "64e94f55d2495c365128523ae1d8d2a7a9b9fc38e260d9a113834b836083be97",
    "ai/omreal/certs_4_8.jsonl": "c55e805d60d8086bcb84a312f2103a9973fc2691d0fd97f3d9a1d9809d2b163b",
    "ai/omreal/data/DIAG3_PAIR_GLOBAL_row2599_candidate_factors.bin": "adb2e7257457f158e809450683c46fe7ecafdbdd4a7efdf9ac630e8a4f0fb03f",
    "ai/omreal/data/DIAG3_PAIR_GLOBAL_row2599_parent_face_gate.json": "cc279d125605b45d25a3a01f462ad051038102f2bf12574f494a9d261bfc7401",
    "ai/omreal/data/DIAG3_PAIR_GLOBAL_row2599_compactification_atlas.json": "956fbe7e5c7b1e04c8873ed9c0f3de9cb5420e3e06f1d5fae4c60f4e0571b364",
    "ai/omreal/data/DIAG3_PAIR_FULLSUPPORT_COMPONENT_COLLAR.json": "5930cc19019470fdfdf55d67523f6c4211ccf5b540f5c2bb5df36c64db75d7bd",
    "ai/omreal/data/DIAG3_PAIR_FULLSUPPORT_SEGMENT_COVER.json": "19248dd148d1fd002931ed5f48197869dd42c68a513376e1a4d6941389bda307",
    "ai/omreal/data/DIAG9_GRAPH_row2599_factor_states.npz": "f44b1fccfb4e61273aeceb8796a18098d82c48473e257556ce3d2a22f99b0bcf",
}

sys.path.insert(0, str(OMREAL))

import DIAG2_PIVOT_LABELED_PAIR_ORBITS_VERIFY as labeled  # noqa: E402
import verify_diag3_pair_global_parent_face_gate as parent_gate  # noqa: E402


class Reject(AssertionError):
    pass


def require(condition: bool, marker: str) -> None:
    if not condition:
        raise Reject(marker)


def digest(data: bytes) -> str:
    return sha256(data).hexdigest()


def digest_path(path: Path) -> str:
    return digest(path.read_bytes())


def canonical_digest(value) -> str:
    return digest(json.dumps(value, sort_keys=True, separators=(",", ":")).encode("ascii"))


def semantic_digest(value: dict) -> str:
    unsealed = deepcopy(value)
    unsealed.pop("semantic_sha256", None)
    return canonical_digest(unsealed)


def sparse(polynomial: dict) -> list[dict]:
    return [
        {"exponents": list(monomial), "coefficient": int(coefficient)}
        for monomial, coefficient in sorted(polynomial.items())
        if coefficient
    ]


def polynomial_degree(polynomial: dict) -> int:
    return max(map(sum, polynomial))


def derivative(polynomial: dict, coordinate: int) -> dict:
    answer = {}
    for monomial, coefficient in polynomial.items():
        power = monomial[coordinate]
        if power:
            reduced = list(monomial)
            reduced[coordinate] -= 1
            reduced = tuple(reduced)
            answer[reduced] = answer.get(reduced, 0) + coefficient * power
    return {monomial: coefficient for monomial, coefficient in answer.items() if coefficient}


def git(*arguments: str) -> str:
    return subprocess.check_output(["git", *arguments], cwd=ROOT, text=True).strip()


def frozen(relative: str) -> bytes:
    return subprocess.check_output(["git", "show", f"{REVIEWED}:{relative}"], cwd=ROOT)


def manifest_source_digest(relative: str) -> str:
    if relative in HISTORICAL_CONTROL_PATHS:
        frozen_protocol = subprocess.check_output(
            ["git", "show", f"{BASE}:{relative}"], cwd=ROOT
        )
        return digest(frozen_protocol)
    return digest_path(ROOT / relative)


def replay_sources() -> dict:
    for relative, expected in CANONICAL_SOURCE_PINS.items():
        require(digest_path(ROOT / relative) == expected, f"source pin {relative}")
    require(digest_path(PREDECESSOR) == PREDECESSOR_SHA256, "predecessor pin")

    records = [json.loads(line) for line in parent_gate.CATALOG.read_text(encoding="utf-8").splitlines() if line]
    parents, parent_sign_digest = parent_gate.parent_polynomials(records[2599])
    signed = [
        (label, sign, {monomial: sign * coefficient for monomial, coefficient in polynomial.items()})
        for label, sign, polynomial, _terms in parents
    ]
    require(len(signed) == 70 and len({label for label, _sign, _polynomial in signed}) == 70, "source factor count")
    require(sum(len(polynomial) for _label, _sign, polynomial in signed) == 209, "source parent term count")
    require(sum(polynomial_degree(polynomial) for _label, _sign, polynomial in signed) == 90, "source barrier degree")
    require(parent_sign_digest == "1d9b940e2bb954b5c69bcee8b2346f9554b2e15589ea4c5b3c3f8e1e943de701", "source parent digest")

    _occurrences, _occurrence_factor, factors = labeled.factor_polynomials()
    require(len(factors) == 26740, "source global factor count")
    factor = factors[TARGET_FACTOR]
    require(len(factor) == 108 and polynomial_degree(factor) == 6, "source factor 19069 census")
    require(canonical_digest(sparse(factor)) == "b997e1dcc7216f595610633de99dd3459658cef28676fa748d79c2ba4ac0f3dc", "source factor 19069 identity")

    predecessor = json.loads(PREDECESSOR.read_text(encoding="utf-8"))
    require(predecessor["semantic_sha256"] == semantic_digest(predecessor), "predecessor semantic digest")
    require(predecessor["target"]["factor_id"] == TARGET_FACTOR, "predecessor factor identity")
    require(predecessor["target"]["parent_sign_factors"] == 70, "predecessor parent count")
    require(predecessor["factor_circuit"]["barrier"]["expanded_polynomial_present"] is False, "predecessor unexpanded circuit")
    require(predecessor["factor_circuit"]["barrier"]["factor_count"] == 70, "predecessor circuit factor count")
    require(len(predecessor["factor_circuit"]["barrier_derivative_nodes"]) == 9, "predecessor derivative nodes")
    require(sum(len(node["summands"]) for node in predecessor["factor_circuit"]["barrier_derivative_nodes"]) == 630, "predecessor derivative summands")
    require(len(predecessor["factor_circuit"]["wedge_equation_nodes"]) == 36, "predecessor wedge count")
    require(predecessor["strict_interior_critical_frontier"]["systems"][0]["singular_wall_pieces_included"] is True, "predecessor singular scope")
    require(predecessor["true_boundary_frontier"]["proper_nonexcluded_candidate_strata"] == 10, "predecessor boundary scope")
    require(predecessor["fixed_skeleton_accounting"]["factor19069_open_root_counts_by_edge"]["39"] == 1, "predecessor edge39 null frontier")

    expected_nodes = [f"H_{index:02d}_{label}" for index, (label, _sign, _polynomial) in enumerate(signed)]
    return {
        "parents": signed,
        "parent_sign_digest": parent_sign_digest,
        "parent_sparse_digest": canonical_digest([sparse(polynomial) for _label, _sign, polynomial in signed]),
        "factor": factor,
        "factor_sparse_digest": canonical_digest(sparse(factor)),
        "expected_nodes": expected_nodes,
        "predecessor": predecessor,
    }


def independence_audit() -> None:
    syntax = ast.parse(Path(__file__).read_text(encoding="utf-8"))
    imported = []
    for node in ast.walk(syntax):
        if isinstance(node, ast.Import):
            imported.extend(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom):
            imported.append(node.module or "")
    forbidden = ("critical_equidim", "factored_barrier_certificate", "falsifier")
    require(not any(any(word in name for word in forbidden) for name in imported), "producer independence import")


def validate_factor_circuit(circuit: dict, replay: dict) -> None:
    require(circuit["format"] == "factor-circuit-dB-wedge-df-v1", "circuit format")
    require(circuit["coordinates"] == list(VARIABLES), "circuit coordinates")
    nodes = circuit["parent_factor_nodes"]
    require(len(nodes) == 70, "circuit parent factor count")
    for index, (node, (label, sign, polynomial)) in enumerate(zip(nodes, replay["parents"], strict=True)):
        expected_id = replay["expected_nodes"][index]
        require(node["node_id"] == expected_id and node["label"] == label, "circuit parent factor identity")
        require(node["source_target_sign"] == sign, "circuit parent factor sign")
        require(node["sparse_polynomial"] == sparse(polynomial), "circuit parent sparse polynomial")
        require(node["degree"] == polynomial_degree(polynomial) and node["term_count"] == len(polynomial), "circuit parent census")
    barrier = circuit["barrier"]
    require(barrier["node_id"] == "B" and barrier["operation"] == "PRODUCT", "circuit barrier node")
    require(barrier["ordered_factor_node_ids"] == replay["expected_nodes"] and barrier["factor_count"] == 70, "circuit barrier factors")
    require(barrier["expanded_polynomial_present"] is False, "circuit barrier unexpanded")
    require(barrier["total_degree"] == 90, "circuit barrier degree")

    derivatives = circuit["barrier_derivative_nodes"]
    require(len(derivatives) == 9, "circuit derivative coordinate count")
    for coordinate, node in enumerate(derivatives):
        require(node["coordinate_index"] == coordinate and node["node_id"] == f"dB_d{VARIABLES[coordinate]}", "circuit derivative identity")
        require(node["operation"] == "SUM_OVER_ALL_70_FACTORS_OF_DH_I_TIMES_PRODUCT_J_NE_I_H_J", "circuit derivative operation")
        require(len(node["summands"]) == 70, "circuit derivative summand count")
        for index, summand in enumerate(node["summands"]):
            require(summand["differentiated_factor_index"] == index and summand["multiply_all_factor_indices_except"] == index, "circuit derivative provenance")
            require(summand["derivative_sparse_polynomial"] == sparse(derivative(replay["parents"][index][2], coordinate)), "circuit derivative sparse polynomial")
    require(sum(len(node["summands"]) for node in derivatives) == 630, "circuit derivative total")

    wall = circuit["wall_polynomial"]
    require(wall["node_id"] == "f_19069" and wall["sparse_polynomial"] == sparse(replay["factor"]), "circuit wall identity")
    require(wall["degree"] == 6 and wall["multidegree"] == [2, 2, 2] and wall["term_count"] == 108, "circuit wall census")
    wall_derivatives = circuit["wall_derivative_nodes"]
    require(len(wall_derivatives) == 9, "circuit wall derivative count")
    for coordinate, node in enumerate(wall_derivatives):
        require(node["coordinate_index"] == coordinate and node["node_id"] == f"df_d{VARIABLES[coordinate]}", "circuit wall derivative identity")
        require(node["sparse_polynomial"] == sparse(derivative(replay["factor"], coordinate)), "circuit wall derivative polynomial")
    expected_pairs = [(left, right) for left in range(9) for right in range(left + 1, 9)]
    wedges = circuit["wedge_equation_nodes"]
    require(len(wedges) == 36, "circuit wedge count")
    for node, (left, right) in zip(wedges, expected_pairs, strict=True):
        x, y = VARIABLES[left], VARIABLES[right]
        require(node["coordinate_pair"] == [left, right] and node["node_id"] == f"wedge_{x}_{y}", "circuit wedge identity")
        require(node["inputs"] == [f"dB_d{x}", f"df_d{y}", f"dB_d{y}", f"df_d{x}"], "circuit wedge inputs")
    require(circuit["equation_contract"] == "f_19069=0 AND all_36_coefficients_of_dB_wedge_df=0", "circuit equation contract")


def validate_localized_ideal(ideal: dict, replay: dict) -> None:
    require(ideal["semantic_sha256"] == semantic_digest(ideal), "localized ideal semantic digest")
    require(ideal["format"] == "d9-factor19069-localized-critical-ideal-circuit-v1", "localized ideal format")
    require(ideal["base_variables"] == list(VARIABLES) and ideal["coefficient_field"] == "Q", "localized ideal ring")
    require(ideal["barrier_product_expanded"] is False and ideal["barrier_product_node"] == "B=PRODUCT_ORDERED(H_00,...,H_69)", "localized ideal unexpanded barrier")
    require(ideal["wall_generator_node_id"] == "f_19069", "localized ideal wall")
    inverse_variables = [f"y_{index:02d}" for index in range(70)]
    inverse_ids = [f"invrel_{index:02d}" for index in range(70)]
    require(ideal["inverse_variables"] == inverse_variables, "localized ideal inverse variables")
    require(len(ideal["inverse_relations"]) == 70, "localized ideal inverse count")
    for index, relation in enumerate(ideal["inverse_relations"]):
        factor_id = replay["expected_nodes"][index]
        expected = {
            "node_id": inverse_ids[index],
            "factor_node_id": factor_id,
            "inverse_variable": inverse_variables[index],
            "equation": f"{factor_id}*{inverse_variables[index]}-1=0",
        }
        require(relation == expected, "localized ideal inverse relation")

    require(len(ideal["log_gradient_nodes"]) == 9, "localized ideal log gradient count")
    for coordinate, node in enumerate(ideal["log_gradient_nodes"]):
        require(node["coordinate_index"] == coordinate and node["node_id"] == f"L_{VARIABLES[coordinate]}", "localized ideal log gradient identity")
        require(node["operation"] == "SUM_i_y_i_TIMES_dH_i" and len(node["summands"]) == 70, "localized ideal log gradient summands")
        for index, summand in enumerate(node["summands"]):
            require(summand["factor_index"] == index and summand["factor_node_id"] == replay["expected_nodes"][index], "localized ideal log gradient provenance")
            require(summand["inverse_variable"] == inverse_variables[index], "localized ideal log gradient inverse")
            require(summand["factor_derivative_sparse_polynomial"] == sparse(derivative(replay["parents"][index][2], coordinate)), "localized ideal log gradient polynomial")

    expected_pairs = [(left, right) for left in range(9) for right in range(left + 1, 9)]
    require(len(ideal["localized_wedge_nodes"]) == 36, "localized ideal wedge count")
    wedge_ids = []
    for node, (left, right) in zip(ideal["localized_wedge_nodes"], expected_pairs, strict=True):
        x, y = VARIABLES[left], VARIABLES[right]
        wedge_ids.append(f"logwedge_{x}_{y}")
        require(node == {"node_id": f"logwedge_{x}_{y}", "coordinate_pair": [left, right], "equation": f"L_{x}*df_d{y}-L_{y}*df_d{x}=0"}, "localized ideal wedge identity")
    require(ideal["generator_node_ids"] == ["f_19069", *inverse_ids, *wedge_ids] and ideal["generator_count"] == 107, "localized ideal generators")
    require(ideal["localization_contract"] == "<f_19069,H_i*y_i-1,logwedge_ij> in Q[x_0..x_8,y_00..y_69]", "localized ideal contract")
    require(ideal["saturation_contract"] == "<f_19069,W_ij>:(PRODUCT_i_H_i)^infinity", "localized ideal saturation")
    require(ideal["elimination_contract"] == "CONTRACT_TO_Q[x_0..x_8]_EQUALS_SATURATED_CRITICAL_IDEAL", "localized ideal elimination")
    require(len(ideal["elimination_faithfulness_proof"]) == 5, "localized ideal faithfulness")
    witness = ideal["derived_product_inverse_witness"]
    require(witness == {"derivation": "PRODUCT_OF_ALL_70_INVERSE_RELATIONS", "expanded_product_used": False, "identity": "B*(PRODUCT_i_y_i)-1=0", "inverse_circuit": "PRODUCT_i_y_i"}, "localized ideal nonboundary witness")
    require(ideal["lambda_replacement_used"] is False, "localized ideal lambda replacement")
    require(ideal["singular_df_zero_branch_retained"] is True, "localized ideal singular retention")


def branch_semantic(branch: dict) -> str:
    return semantic_digest(branch)


def validate_branch_frontier(frontier: dict) -> None:
    require(frontier["semantic_sha256"] == semantic_digest(frontier), "branch frontier semantic digest")
    require(frontier["format"] == "d9-factor19069-critical-equidim-branch-frontier-v1", "branch frontier format")
    branch_ids = ["EQ-B00-SINGULAR-DF-ZERO", *[f"EQ-B{index + 1:02d}-REGULAR-PIVOT-{coordinate}" for index, coordinate in enumerate(VARIABLES)]]
    require(frontier["branch_order"] == branch_ids, "branch frontier order")
    require(len(frontier["branches"]) == 10, "branch frontier count")
    inverse_ids = [f"invrel_{index:02d}" for index in range(70)]
    base_variables = list(VARIABLES)
    inverse_variables = [f"y_{index:02d}" for index in range(70)]

    singular = frontier["branches"][0]
    require(singular["semantic_sha256"] == branch_semantic(singular), "singular branch semantic digest")
    require(singular["branch_id"] == branch_ids[0] and singular["branch_kind"] == "CLOSED_SINGULAR_WALL_BRANCH_IN_NONBOUNDARY_LOCALIZATION", "singular branch identity")
    require(singular["coefficient_field"] == "Q" and singular["monomial_order"] == "graded_reverse_lexicographic", "singular branch ring")
    require(singular["variables"] == [*base_variables, *inverse_variables] and singular["variable_precedence"] == singular["variables"], "singular branch variables")
    require(singular["generator_node_ids"] == ["f_19069", *inverse_ids, *[f"df_d{x}" for x in VARIABLES]] and singular["generator_count"] == 80, "singular branch generators")
    require(singular["critical_wedges_status"] == "REDUNDANT_MODULO_ALL_NINE_df_GENERATORS", "singular branch wedge scope")
    require(singular["saturation_status"] == "EXACT_VIA_ALL_70_INVERSE_RELATIONS", "singular branch saturation")
    require(singular["equidimensional_decomposition_status"] == "UNRESOLVED_FAIL_CLOSED", "singular branch unresolved")
    require(singular["complex_dimension"] is None and singular["degree"] is None and singular["multiplicity_data"] is None, "singular branch unsupported invariants")
    require(singular["possible_complex_dimensions"] == ["EMPTY", *range(9)], "singular branch dimension frontier")
    require(singular["exact_real_strict_parent_point"] is None and singular["strict_parent_component_residence"] == "UNRESOLVED", "singular branch real residence")

    for pivot_index, branch in enumerate(frontier["branches"][1:]):
        coordinate = VARIABLES[pivot_index]
        require(branch["semantic_sha256"] == branch_semantic(branch), "regular branch semantic digest")
        require(branch["branch_id"] == branch_ids[pivot_index + 1] and branch["branch_kind"] == "LEX_FIRST_NONZERO_df_PIVOT_CHART", "regular branch identity")
        require(branch["coefficient_field"] == "Q" and branch["monomial_order"] == "graded_reverse_lexicographic", "regular branch ring")
        variables = [*base_variables, *inverse_variables, f"q_{coordinate}"]
        require(branch["variables"] == variables and branch["variable_precedence"] == variables, "regular branch variables")
        pairs = [(min(pivot_index, other), max(pivot_index, other)) for other in range(9) if other != pivot_index]
        wedge_ids = [f"logwedge_{VARIABLES[left]}_{VARIABLES[right]}" for left, right in pairs]
        expected_generators = ["f_19069", *inverse_ids, *[f"df_d{VARIABLES[index]}" for index in range(pivot_index)], f"pivot_invrel_{coordinate}", *wedge_ids]
        require(branch["generator_node_ids"] == expected_generators and branch["generator_count"] == 80 + pivot_index, "regular branch generators")
        require(branch["pivot_inverse_relation"] == f"pivot_invrel_{coordinate}:q_{coordinate}*df_d{coordinate}-1=0", "regular branch pivot saturation")
        require(branch["pivot_critical_equations"] == wedge_ids, "regular branch critical equations")
        require(branch["saturation_status"] == "EXACT_VIA_70_FACTOR_INVERSES_AND_PIVOT_INVERSE", "regular branch saturation")
        require(branch["equidimensional_decomposition_status"] == "PENDING_AFTER_FIRST_UNRESOLVED_BRANCH", "regular branch pending")
        require(branch["complex_dimension"] is None and branch["degree"] is None and branch["multiplicity_data"] is None, "regular branch unsupported invariants")
        require(branch["exact_real_strict_parent_point"] is None and branch["strict_parent_component_residence"] == "PENDING", "regular branch real residence")

    require(frontier["first_unresolved_branch_id"] == branch_ids[0], "branch frontier first unresolved")
    require(frontier["first_unresolved_branch_semantic_sha256"] == singular["semantic_sha256"], "branch frontier first pin")
    require(frontier["first_unresolved_obligation"] == "EXACT_EQUIDIMENSIONAL_DECOMPOSITION_OVER_Q_OF_THE_SATURATED_SINGULAR_WALL_BRANCH_WITH_DIMENSION_DEGREE_AND_MULTIPLICITY_DATA", "branch frontier obligation")
    require(frontier["cover_contract"] == "SINGULAR_df_ZERO_UNION_LEX_FIRST_NONZERO_df_REGULAR_CHARTS_COVERS_THE_LOCALIZED_CRITICAL_LOCUS_SET_THEORETICALLY", "branch frontier cover")
    require(frontier["resolved_branch_count"] == 0 and frontier["pending_branch_count"] == 10, "branch frontier accounting")
    require(frontier["scheme_decomposition_claimed"] is False, "branch frontier scheme claim")
    require(frontier["zero_dimensional_status"] == "NOT_PROVED", "branch frontier zero dimension")
    require(frontier["positive_dimensional_complex_piece_status"] == "UNRESOLVED", "branch frontier positive complex")
    require(frontier["positive_dimensional_real_strict_piece_status"] == "UNRESOLVED", "branch frontier positive real")
    require(frontier["complete_real_root_frontier_status"] == "NOT_CONSTRUCTED", "branch frontier real roots")


def validate_frontier(candidate: dict, replay: dict) -> None:
    require(candidate["semantic_sha256"] == semantic_digest(candidate), "frontier semantic digest")
    require(candidate["format"] == "d9-factor19069-critical-equidim-constructor-frontier-v1", "frontier format")
    require(candidate["cycle_id"] == "2026-09-01-d9-row2599-factor19069-critical-equidim-gate1", "frontier cycle")
    require(candidate["opening_revision"] == BASE and candidate["opening_tree"] == BASE_TREE, "frontier opening")
    require(candidate["track_id"] == "d9-factor19069-critical-equidim-constructor", "frontier track")
    require(candidate["outcome"] == "pass" and candidate["classification"] == "EXACT_FAIL_CLOSED_SATURATED_EQUIDIMENSIONAL_DECOMPOSITION_NULL", "frontier classification")
    require(candidate["endpoint"] == NULL, "frontier endpoint")
    require(candidate["theorem_ledger"] == "2/9" and candidate["ledger_change_recommended"] == "none", "frontier ledger")
    require(candidate["target"] == {"parent_index": 2599, "factor_id": 19069, "ambient_parameter_dimension": 9, "barrier_parent_factor_count": 70, "barrier_total_degree": 90, "barrier_representation": "UNEXPANDED_FACTORED_CIRCUIT", "wedge_equation_count": 36}, "frontier target")

    predecessor = replay["predecessor"]
    binding = candidate["predecessor_binding"]
    require(binding["frontier_sha256"] == PREDECESSOR_SHA256 and binding["frontier_semantic_sha256"] == predecessor["semantic_sha256"], "frontier predecessor pin")
    require(binding["factor_circuit_semantic_sha256"] == predecessor["factor_circuit_semantic_sha256"], "frontier predecessor circuit pin")
    require(binding["strict_interior_system_semantic_sha256"] == predecessor["strict_interior_critical_frontier"]["systems"][0]["semantic_sha256"], "frontier predecessor stratum pin")
    require(binding["verified_null_frontier_preserved"] is True, "frontier predecessor null preservation")

    validate_factor_circuit(candidate["factor_circuit"], replay)
    require(candidate["factor_circuit"] == predecessor["factor_circuit"], "frontier inherited circuit identity")
    require(candidate["factor_circuit_semantic_sha256"] == canonical_digest(candidate["factor_circuit"]), "frontier circuit semantic digest")
    validate_localized_ideal(candidate["localized_critical_ideal"], replay)
    validate_branch_frontier(candidate["equidimensional_branch_frontier"])

    selector = candidate["strict_parent_component_selector"]
    require(selector["strict_inequalities"] == [f"{node}>0" for node in replay["expected_nodes"]], "frontier parent inequalities")
    require(selector["connected_parent_selector"] == "EXACT_PATH_IN_STRICT_PARENT_SIGN_SET_TO_PINNED_SAMPLE_REQUIRED", "frontier parent selector")
    require(selector["source_derived_parent_tag"] == "ROW2599_PINNED_CONNECTED_PARENT_COMPONENT", "frontier parent tag")
    require(selector["complex_localization_does_not_prove_real_residence"] is True and selector["real_path_certificate_required_for_each_positive_dimensional_piece"] is True, "frontier real residence guard")
    singular = candidate["singular_strata_accounting"]
    require(singular == {"df_zero_branch_id": "EQ-B00-SINGULAR-DF-ZERO", "df_zero_branch_omitted": False, "lambda_only_replacement_prohibited": True, "singular_branch_real_residence": "UNRESOLVED"}, "frontier singular scope")

    require(candidate["true_boundary_frontier"] == predecessor["true_boundary_frontier"], "frontier boundary preservation")
    require(candidate["fixed_skeleton_accounting"] == predecessor["fixed_skeleton_accounting"], "frontier skeleton preservation")
    null = candidate["verified_null_frontier"]
    require(null["predecessor_strict_interior_critical_frontier"] == predecessor["strict_interior_critical_frontier"], "frontier critical null preservation")
    require(null["connected_components_sampled"] == 0 and null["positive_dimensional_components_sampled"] == 0, "frontier component sample scope")
    require(null["edge39_anchor_is_barrier_critical_sample"] is False and null["global_attachment_classification_complete"] is False, "frontier edge39 scope")

    resource = candidate["resource_accounting"]
    require(resource["barrier_expansion_nodes"] == 0, "frontier resource barrier expansion")
    require(resource["component_samples_computed"] == 0 and resource["equidimensional_decomposition_nodes_completed"] == 0, "frontier resource decomposition")
    require(resource["exploratory_sympy_probes_used_for_claims"] is False, "frontier resource exploratory inference")
    require(resource["ceiling_crossed"] is False, "frontier resource ceiling")
    require(resource["declared_exact_circuit_nodes_constructed"] == 1520 and resource["declared_exact_circuit_nodes_constructed"] <= resource["resource_ceiling"]["max_exact_algebra_component_nodes"], "frontier resource nodes")
    require(resource["first_pending_operation"] == "GREVLEX_EQUIDIMENSIONAL_DECOMPOSITION_OVER_Q_OF_EQ-B00-SINGULAR-DF-ZERO_IN_THE_79_VARIABLE_INVERSE_EXTENSION", "frontier resource first pending")
    raw = candidate["raw_wall_context_only"]
    require(raw["wall_node_id"] == "f_19069" and raw["total_degree"] == 6 and raw["ambient_affine_hypersurface_dimension"] == 8, "frontier raw wall context")
    require(raw["critical_branch_dimension_or_degree_claim"] is False, "frontier raw wall noninference")
    require(candidate["exact_consequence"] == "THE_SATURATED_FACTOR19069_CRITICAL_IDEAL_HAS_AN_EXACT_70_INVERSE_LOCALIZATION_CIRCUIT_AND_A_SINGULAR_FIRST_BRANCH_BUT_NO_BRANCH_DIMENSION_DEGREE_OR_MULTIPLICITY_IS_CERTIFIED", "frontier consequence")


def validate_constructor_handoff(frontier: dict) -> None:
    manifest = json.loads(CONSTRUCTOR_MANIFEST.read_text(encoding="utf-8"))
    require(manifest["semantic_sha256"] == semantic_digest(manifest), "constructor manifest semantic digest")
    require(manifest["format"] == "d9-factor19069-critical-equidim-constructor-source-manifest-v1", "constructor manifest format")
    require(manifest["opening_revision"] == BASE and manifest["opening_tree"] == BASE_TREE, "constructor manifest opening")
    require(manifest["source_policy"] == {"external_compute_used": False, "network_or_connector_used": False, "predecessor_frontier_is_frozen_accepted_source": True, "producer_code_imported": False}, "constructor manifest policy")
    for relative, expected in manifest["pins"].items():
        require(manifest_source_digest(relative) == expected, f"constructor manifest pin {relative}")

    result = json.loads(CONSTRUCTOR_RESULT.read_text(encoding="utf-8"))
    require(result["format"] == "d9-factor19069-critical-equidim-constructor-result-v1", "constructor result format")
    require(result["classification"] == frontier["classification"] and result["endpoint"] == frontier["endpoint"], "constructor result endpoint")
    require(result["frontier_sha256"] == digest_path(FRONTIER) and result["frontier_semantic_sha256"] == frontier["semantic_sha256"], "constructor result frontier pin")
    require(result["localized_critical_ideal_semantic_sha256"] == frontier["localized_critical_ideal"]["semantic_sha256"], "constructor result ideal pin")
    require(result["branch_frontier_semantic_sha256"] == frontier["equidimensional_branch_frontier"]["semantic_sha256"], "constructor result branch pin")
    require(result["first_unresolved_branch_id"] == "EQ-B00-SINGULAR-DF-ZERO" and result["first_unresolved_branch_semantic_sha256"] == frontier["equidimensional_branch_frontier"]["branches"][0]["semantic_sha256"], "constructor result first branch")
    require(result["resolved_branch_count"] == 0 and result["pending_branch_count"] == 10, "constructor result branch accounting")
    require(result["critical_dimensions_degrees_multiplicities_certified"] is False, "constructor result invariant scope")
    require(result["zero_dimensional_strict_locus_certified"] is False and result["exact_positive_dimensional_real_component_certified"] is False, "constructor result dimensional scope")
    require(result["barrier_expanded"] is False and result["singular_branch_retained"] is True, "constructor result circuit scope")
    require(result["parent_factor_tags_retained"] == 70 and result["true_boundary_candidate_strata_retained"] == 10, "constructor result strata scope")
    require(result["edge39_anchor_preserved_as_noncritical"] is True, "constructor result edge39 scope")
    require(result["theorem_ledger"] == "2/9" and result["ledger_change_recommended"] == "none", "constructor result ledger")


def reseal(candidate: dict) -> dict:
    if "localized_critical_ideal" in candidate:
        candidate["localized_critical_ideal"]["semantic_sha256"] = semantic_digest(candidate["localized_critical_ideal"])
    if "equidimensional_branch_frontier" in candidate:
        branches = candidate["equidimensional_branch_frontier"].get("branches", [])
        for branch in branches:
            branch["semantic_sha256"] = semantic_digest(branch)
        candidate["equidimensional_branch_frontier"]["semantic_sha256"] = semantic_digest(candidate["equidimensional_branch_frontier"])
    if "factor_circuit" in candidate:
        candidate["factor_circuit_semantic_sha256"] = canonical_digest(candidate["factor_circuit"])
    candidate["semantic_sha256"] = semantic_digest(candidate)
    return candidate


def hostile_mutations(stored: dict, replay: dict) -> list[str]:
    mutations: list[tuple[str, dict]] = []

    def add(marker: str, candidate: dict) -> None:
        mutations.append((marker, reseal(candidate)))

    candidate = deepcopy(stored); candidate["classification"] = "COMPLETE"; add("frontier classification", candidate)
    candidate = deepcopy(stored); candidate["endpoint"] = POSITIVE; add("frontier endpoint", candidate)
    candidate = deepcopy(stored); candidate["theorem_ledger"] = "3/9"; add("frontier ledger", candidate)
    candidate = deepcopy(stored); candidate["target"]["factor_id"] = 19068; add("frontier target", candidate)
    candidate = deepcopy(stored); candidate["predecessor_binding"]["frontier_sha256"] = "0" * 64; add("frontier predecessor pin", candidate)
    candidate = deepcopy(stored); candidate["factor_circuit"]["parent_factor_nodes"].pop(); add("circuit parent factor count", candidate)
    candidate = deepcopy(stored); candidate["factor_circuit"]["barrier"]["expanded_polynomial_present"] = True; add("circuit barrier unexpanded", candidate)
    candidate = deepcopy(stored); candidate["factor_circuit"]["wall_polynomial"]["sparse_polynomial"][0]["coefficient"] *= -1; add("circuit wall identity", candidate)
    candidate = deepcopy(stored); candidate["factor_circuit"]["barrier_derivative_nodes"][0]["summands"].pop(); add("circuit derivative summand count", candidate)
    candidate = deepcopy(stored); candidate["factor_circuit"]["wedge_equation_nodes"].pop(); add("circuit wedge count", candidate)
    candidate = deepcopy(stored); candidate["localized_critical_ideal"]["saturation_contract"] = "<f_19069>"; add("localized ideal saturation", candidate)
    candidate = deepcopy(stored); candidate["localized_critical_ideal"]["inverse_relations"].pop(); add("localized ideal inverse count", candidate)
    candidate = deepcopy(stored); candidate["localized_critical_ideal"]["inverse_relations"][0]["factor_node_id"] = "f_19069"; add("localized ideal inverse relation", candidate)
    candidate = deepcopy(stored); candidate["localized_critical_ideal"]["log_gradient_nodes"][0]["summands"][16]["factor_derivative_sparse_polynomial"] = []; add("localized ideal log gradient polynomial", candidate)
    candidate = deepcopy(stored); candidate["localized_critical_ideal"]["localized_wedge_nodes"].pop(); add("localized ideal wedge count", candidate)
    candidate = deepcopy(stored); candidate["localized_critical_ideal"]["lambda_replacement_used"] = True; add("localized ideal lambda replacement", candidate)
    candidate = deepcopy(stored); candidate["localized_critical_ideal"]["singular_df_zero_branch_retained"] = False; add("localized ideal singular retention", candidate)
    candidate = deepcopy(stored); candidate["equidimensional_branch_frontier"]["branch_order"].reverse(); add("branch frontier order", candidate)
    candidate = deepcopy(stored); candidate["equidimensional_branch_frontier"]["branches"].pop(); add("branch frontier count", candidate)
    candidate = deepcopy(stored); candidate["equidimensional_branch_frontier"]["branches"][0]["complex_dimension"] = 0; add("singular branch unsupported invariants", candidate)
    candidate = deepcopy(stored); candidate["equidimensional_branch_frontier"]["branches"][0]["degree"] = 1; add("singular branch unsupported invariants", candidate)
    candidate = deepcopy(stored); candidate["equidimensional_branch_frontier"]["branches"][0]["multiplicity_data"] = [1]; add("singular branch unsupported invariants", candidate)
    candidate = deepcopy(stored); candidate["equidimensional_branch_frontier"]["branches"][0]["exact_real_strict_parent_point"] = [0] * 9; add("singular branch real residence", candidate)
    candidate = deepcopy(stored); candidate["equidimensional_branch_frontier"]["branches"][1]["complex_dimension"] = 1; add("regular branch unsupported invariants", candidate)
    candidate = deepcopy(stored); candidate["equidimensional_branch_frontier"]["scheme_decomposition_claimed"] = True; add("branch frontier scheme claim", candidate)
    candidate = deepcopy(stored); candidate["equidimensional_branch_frontier"]["zero_dimensional_status"] = "PROVED"; add("branch frontier zero dimension", candidate)
    candidate = deepcopy(stored); candidate["equidimensional_branch_frontier"]["positive_dimensional_complex_piece_status"] = "EXCLUDED"; add("branch frontier positive complex", candidate)
    candidate = deepcopy(stored); candidate["equidimensional_branch_frontier"]["positive_dimensional_real_strict_piece_status"] = "EXCLUDED"; add("branch frontier positive real", candidate)
    candidate = deepcopy(stored); candidate["equidimensional_branch_frontier"]["complete_real_root_frontier_status"] = "COMPLETE"; add("branch frontier real roots", candidate)
    candidate = deepcopy(stored); candidate["equidimensional_branch_frontier"]["first_unresolved_branch_id"] = "EQ-B01-REGULAR-PIVOT-a"; add("branch frontier first unresolved", candidate)
    candidate = deepcopy(stored); candidate["equidimensional_branch_frontier"]["pending_branch_count"] = 9; add("branch frontier accounting", candidate)
    candidate = deepcopy(stored); candidate["strict_parent_component_selector"]["strict_inequalities"].pop(); add("frontier parent inequalities", candidate)
    candidate = deepcopy(stored); candidate["strict_parent_component_selector"]["connected_parent_selector"] = "SIGNS_ONLY"; add("frontier parent selector", candidate)
    candidate = deepcopy(stored); candidate["strict_parent_component_selector"]["source_derived_parent_tag"] = "AMBIENT_ORBIT"; add("frontier parent tag", candidate)
    candidate = deepcopy(stored); candidate["singular_strata_accounting"]["df_zero_branch_omitted"] = True; add("frontier singular scope", candidate)
    candidate = deepcopy(stored); candidate["true_boundary_frontier"]["records"].pop(); add("frontier boundary preservation", candidate)
    candidate = deepcopy(stored); candidate["true_boundary_frontier"]["true_parent_boundary_kept_distinct_from"].pop(); add("frontier boundary preservation", candidate)
    candidate = deepcopy(stored); candidate["fixed_skeleton_accounting"]["exact_attached_wall_anchor"]["barrier_critical_sample"] = True; add("frontier skeleton preservation", candidate)
    candidate = deepcopy(stored); candidate["verified_null_frontier"]["edge39_anchor_is_barrier_critical_sample"] = True; add("frontier edge39 scope", candidate)
    candidate = deepcopy(stored); candidate["resource_accounting"]["barrier_expansion_nodes"] = 1; add("frontier resource barrier expansion", candidate)
    candidate = deepcopy(stored); candidate["resource_accounting"]["component_samples_computed"] = 1; add("frontier resource decomposition", candidate)
    candidate = deepcopy(stored); candidate["resource_accounting"]["exploratory_sympy_probes_used_for_claims"] = True; add("frontier resource exploratory inference", candidate)
    candidate = deepcopy(stored); candidate["resource_accounting"]["declared_exact_circuit_nodes_constructed"] = 500001; add("frontier resource nodes", candidate)
    candidate = deepcopy(stored); candidate["raw_wall_context_only"]["critical_branch_dimension_or_degree_claim"] = True; add("frontier raw wall noninference", candidate)
    candidate = deepcopy(stored); candidate["exact_consequence"] = "ZERO_DIMENSIONAL"; add("frontier consequence", candidate)
    rejected = []
    for marker, candidate in mutations:
        try:
            validate_frontier(candidate, replay)
        except Reject as error:
            require(marker in str(error), f"wrong hostile rejection {marker}: {error}")
            rejected.append(marker)
            continue
        raise Reject(f"hostile mutation accepted: {marker}")
    return rejected


def validate_result(candidate: dict, frontier_sha256: str, hostile_count: int) -> None:
    require(candidate["semantic_sha256"] == semantic_digest(candidate), "result semantic digest")
    require(candidate["format"] == "d9-factor19069-critical-equidim-certificate-result-v1", "result format")
    require(candidate["track_id"] == "d9-factor19069-critical-equidim-certificate", "result track")
    require(candidate["reviewed_revision"] == REVIEWED and candidate["reviewed_tree"] == REVIEWED_TREE, "result reviewed head")
    require(candidate["producer_imported"] is False and candidate["falsifier_imported"] is False, "result independence")
    require(candidate["constructor_frontier_sha256"] == frontier_sha256, "result frontier pin")
    require(candidate["hostile_mutations"] == {"rejected": hostile_count, "total": hostile_count}, "result hostile count")
    require(candidate["theorem_ledger"] == "2/9" and candidate["ledger_change_recommended"] == "none", "result ledger")
    require(candidate["verdict"] == "ACCEPT" and candidate["classification"] == "ACCEPT_EXACT_FAIL_CLOSED_SATURATED_EQUIDIMENSIONAL_NULL", "result verdict")
    require(candidate["accepted_endpoint"] == NULL and candidate["first_unresolved_branch_id"] == "EQ-B00-SINGULAR-DF-ZERO", "result endpoint")
    require(candidate["zero_dimensionality_certified"] is False and candidate["positive_dimensional_real_component_certified"] is False, "result claim scope")
    require(candidate["resolved_branch_count"] == 0 and candidate["pending_branch_count"] == 10, "result branch accounting")
    require(candidate["first_unresolved_obligation"] == "EXACT_EQUIDIMENSIONAL_DECOMPOSITION_OVER_Q_OF_THE_SATURATED_SINGULAR_WALL_BRANCH_WITH_DIMENSION_DEGREE_AND_MULTIPLICITY_DATA", "result obligation")
    require(candidate["source_replay"] == {"parent_factors": 70, "parent_sparse_terms": 209, "barrier_total_degree": 90, "barrier_derivative_summands": 630, "wedge_equations": 36, "factor19069_terms": 108, "factor19069_degree": 6, "localized_inverse_relations": 70, "localized_log_gradient_summands": 630, "localized_wedge_equations": 36, "true_boundary_candidate_strata": 10, "skeleton_parent_tags": 2800}, "result source replay")


def main() -> None:
    require(git("rev-parse", f"{BASE}^{{commit}}") == BASE, "base commit")
    require(git("rev-parse", f"{BASE}^{{tree}}") == BASE_TREE, "base tree")
    require(git("rev-parse", f"{REVIEWED}^{{commit}}") == REVIEWED, "reviewed commit")
    require(git("rev-parse", f"{REVIEWED}^{{tree}}") == REVIEWED_TREE, "reviewed tree")
    for relative, expected in CONSTRUCTOR_PINS.items():
        require(digest(frozen(relative)) == expected, f"reviewed constructor pin {relative}")
        require((ROOT / relative).read_bytes() == frozen(relative), f"constructor worktree drift {relative}")
    opening = json.loads(OPENING.read_text(encoding="utf-8"))
    require(opening["base_revision"] == BASE and opening["base_tree"] == BASE_TREE, "opening base")
    require(opening["selected_target"] == TARGET and opening["selected_count"] == 1, "opening target")
    require(opening["opening_ledger"] == "2/9", "opening ledger")
    independence_audit()
    replay = replay_sources()
    frontier = json.loads(FRONTIER.read_text(encoding="utf-8"))
    validate_frontier(frontier, replay)
    validate_constructor_handoff(frontier)
    rejected = hostile_mutations(frontier, replay)
    result = json.loads(RESULT.read_text(encoding="utf-8"))
    validate_result(result, digest_path(FRONTIER), len(rejected))
    print("PASS producer-independent factor-19069 critical equidimensional certificate")
    print(f"PASS sources parents=70 terms=209 barrier_degree=90 factor19069_terms=108 hostile={len(rejected)}/{len(rejected)}")
    print(f"ACCEPT {result['accepted_endpoint']} only; ledger=2/9")


if __name__ == "__main__":
    main()
