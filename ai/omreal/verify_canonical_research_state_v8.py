#!/usr/bin/env python3
"""Verify the fail-closed post theorem-reset 9DVL canonical state V8."""

from __future__ import annotations

from copy import deepcopy
from hashlib import sha256
import json
from pathlib import Path
import subprocess


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
STATE_PATH = HERE / "data" / "CANONICAL_RESEARCH_STATE_V8.json"
FROZEN_CLOSE = "9116771ba80ed3d033516d0dd666b34348aad348"
FROZEN_CLOSE_TREE = "a64438426dc792af67d5ccc0dd2f4d1231dbaa14"
INTEGRATED_REFEREE = "fa9787b8295fae46a262d610698e7d21790c63bd"
INTEGRATED_REFEREE_TREE = "5f38b50568671b876aaaa1528a4aca7cb5e090eb"
V7_SUCCESSOR = "D9_ROW2599_FACTOR19069_FACTORED_CRITICAL_EQUIDIMENSIONAL_DECOMPOSITION_GATE1"
PROGRAM_ID = "D3_NESTED_A_B_C_THEOREM_FEASIBILITY_ROUND1"
TARGET_A = "A_UNIVERSAL_MIXED_CHAIN_CONSTRUCTION_SPECIALIZATION"
TARGET_B = "B_COMPLETE_SOURCE_DERIVED_JOINED_COMPLEX_PAIR_EXACTNESS"
TARGET_C = "C_ALL_COMPONENT_TRIPLE_TRUE_PARENT_INFINITY_ESCAPE"
PROGRAM_DIGEST = "2e16429975230582aa975f1c1be3b356137f42f4a6faf5b427ac703951ef3ed6"
OPEN_OBLIGATIONS_DIGEST = "64d7a8a2f35a84ce74cf5fe2972031a7d7a060da1944a9df2b3dcb8c9ced5e5d"
PROCESS_GATES_DIGEST = "5b397ce3696ec41419fc29b804562f8a68077b36d7aa2f8f3a07e847dcac30f6"

PINS = {
    "ai/omreal/data/CANONICAL_RESEARCH_STATE_V7.json": "4c5c75eaea78d005a664c61f43c2bb7559c890664e55fc2a947c4cc7e8811bcc",
    "ops/research-team/cycles/2026-09-01-theorem-reset-joined-gordan-tournament-gate1/CYCLE_REPORT.md": "ccb34a1b416bd65920a0b50f780e66292eece697847afe8042b4d7a2fd6a0df0",
    "ops/research-team/cycles/2026-09-01-theorem-reset-joined-gordan-tournament-gate1/CLOSING_MANIFEST.json": "2ef455643cc1a20812ea76a57ec650d6b251b522049851913aeedc7bcffccaea",
    "ops/research-team/cycles/2026-09-01-theorem-reset-joined-gordan-tournament-gate1/CLOSING_CANDIDATE.json": "5ff3c82930918daea52436fdcc7ab1c6da720bd913b8973dee714507df7de128",
    "ops/research-team/cycles/2026-09-01-theorem-reset-joined-gordan-tournament-gate1/OBLIGATION_GRAPH.json": "61327b143f339cfa99620f4b3ddd3218ba86d705b87c0fdda7e81da782ad3de1",
    "ops/team/theorem-reset-prover-strategy/RESULT.json": "bab28affb8a72d1ff86ed86a3bad9f0f9a41dd216826e4dca8889ca5e911eafb",
    "ops/team/theorem-reset-prover-strategy/FINDINGS.md": "4ce7b6504cb07f75779660f0a7d04681a7e98bb5d0a72e3fb9b2884267ace9b1",
    "ops/team/theorem-reset-closing-referee/RESULT.json": "4e20d66ee618df991fad56230484f21251515efd9673b84c1effb98662361a3a",
    "ops/team/theorem-reset-closing-referee/REVIEW.md": "582d67504f9421e5f96f30585dc94fb0fd5a4df68be443331bb09153a6c150eb",
    "ops/team/theorem-reset-closing-referee/CLEAN_REPLAY.json": "b1394e5e7b3e5b636eed689fa07036049215a79f144e9863414e992b66776f91",
}

LOAD_BEARING_IDS = [
    "global_gluing",
    "extension_labels",
    "strict_closure",
    "relative_infinity",
    "middle_rank_replay",
    "diag3_pair_hc1",
    "diag3_triple_hc0",
]

ALL_FACE_TYPES = ["(0)", "(1)", "(0,0)", "(2)", "(1,0)", "(0,0,0)", "(3)", "(2,0)", "(1,1)", "(1,0,0)"]
MISSING_LOWER_TYPES = ["(0,0)", "(1,0)", "(0,0,0)"]
MISSING_DIMENSION_THREE_TYPES = ["(3)", "(2,0)", "(1,1)", "(1,0,0)"]

PROHIBITED = [
    "TARGET_A_MIXED_FAMILY_ALONE_PROMOTED_TO_GLOBAL_RANK_OR_KERNEL_EXACTNESS",
    "TARGET_A_MIXED_FAMILY_ALONE_PROMOTED_TO_TRIPLE_ESCAPE",
    "ROW2599_PRIMITIVE_CLASS_PROMOTED_AS_ALL_RELEVANT_PRIMITIVE_CLASSES",
    "ONE_ORDERED_SIGNATURE_TRIPLE_OR_MINIMAL_SIGNATURE_SET_PROMOTED_AS_ALL_ADMISSIBLE_ANTICHAINS",
    "SEPARATE_INCOMPATIBLE_SUBDIVISIONS_PROMOTED_AS_ONE_SIMULTANEOUS_SUBDIVISION",
    "PAIRWISE_SPECIALIZATION_SQUARES_PROMOTED_AS_ITERATED_FACE_COHERENCE",
    "GENERIC_PARENT_ARGUMENT_PROMOTED_ACROSS_UNANALYZED_PARENT_RANK_DROP_STRATA",
    "FORMAL_TEN_TYPE_TAXONOMY_PROMOTED_AS_A_SOURCE_DERIVED_JOINED_COMPLEX",
    "MIXED_1_0_0_FACE_ALONE_PROMOTED_WHILE_LOWER_OR_OTHER_DIMENSION_THREE_TYPES_ARE_MISSING",
    "RANK_COUNT_PROMOTED_WITHOUT_D2_ZERO_RATIONAL_KERNEL_EXACTNESS_AND_BAD_UNION_COMPARISON",
    "ONE_ESCAPE_PATH_PER_TRIPLE_SOURCE_PROMOTED_AS_ALL_COMPONENT_ESCAPE",
    "LOCAL_RADIAL_CLIPPED_OR_AMBIENT_BOUNDARY_PROMOTED_AS_TRUE_PARENT_INFINITY",
    "TRIPLE_ONLY_CLOSURE_PROMOTED_TO_D3_WHILE_TARGET_B_IS_OPEN",
    "V7_FACTORED_CRITICAL_EQUIDIMENSIONAL_DECOMPOSITION_OR_BLIND_FACTOR19069_SAMPLING",
]


class Reject(AssertionError):
    """A fail-closed validation rejection."""


def require(condition: bool, message: str) -> None:
    if not condition:
        raise Reject(message)


def git(*arguments: str, binary: bool = False):
    output = subprocess.check_output(["git", *arguments], cwd=ROOT)
    return output if binary else output.decode("utf-8").strip()


def frozen(path: str) -> bytes:
    return git("show", f"{FROZEN_CLOSE}:{path}", binary=True)


def frozen_json(path: str) -> dict:
    return json.loads(frozen(path).decode("utf-8"))


def canonical_digest(value: object) -> str:
    encoded = json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=False
    ).encode("utf-8")
    return sha256(encoded).hexdigest()


def current_authority_surfaces() -> dict[str, str]:
    paths = {
        "readme": "README.md",
        "operating_system": "ai/omreal/RESEARCH_OPERATING_SYSTEM.md",
        "status_v5": "ai/omreal/NINE_DIAGONAL_STATUS_V5.md",
        "prospectus": "ai/omreal/9DVL_THEOREM_PROSPECTUS.md",
    }
    return {
        name: (ROOT / path).read_text(encoding="utf-8")
        for name, path in paths.items()
    }


def validate_authority_content(surfaces: dict[str, str]) -> None:
    normalized = {name: " ".join(text.split()) for name, text in surfaces.items()}
    readme = normalized["readme"]
    require("CANONICAL_RESEARCH_STATE_V8.json" in readme, "README V8 authority")
    require("NINE_DIAGONAL_STATUS_V5.md" in readme, "README V5 status")
    require("V8 authorizes one bounded three-target proof-program feasibility round" in readme, "README three-target scope")
    require("explicitly authorizes no mathematical construction or theorem credit" in readme, "README noncredit scope")

    operating = normalized["operating_system"]
    require("data/CANONICAL_RESEARCH_STATE_V8.json" in operating, "operating-system V8 authority")
    require("verify_canonical_research_state_v8.py" in operating, "operating-system V8 verifier")
    require("mixed-`(1,0,0)` chain subproblem" in operating, "operating-system target A")
    require("complete joined-complex/pair-kernel program" in operating, "operating-system target B")
    require("independent triple-component escape program" in operating, "operating-system target C")
    require("no mathematical construction or theorem credit" in operating, "operating-system noncredit scope")

    status = normalized["status_v5"]
    require("V8 selects one theorem-first feasibility round with three nested targets" in status, "status A/B/C program")
    require("A — mixed-chain subproblem" in status and "B — pair branch" in status and "C — triple branch" in status, "status target labels")
    require("`1 <= r <= 3`, modulo active-block permutation but covering every labeled instance" in status, "status face taxonomy scope")
    require("B must establish the source interface before invoking A" in status, "status noncircular interface")
    require("Only actual theorems B and C together could settle diagonal three" in status, "status B plus C logic")
    require("A alone does not define the global kernel, prove a rank identity, or imply triple escape" in status, "status A nonconsequences")

    prospectus = normalized["prospectus"]
    require("### Target A: universal mixed `(1,0,0)` chain construction" in prospectus, "prospectus target A")
    require("### Target B: complete joined complex and rational pair exactness" in prospectus, "prospectus target B")
    require("### Target C: independent triple-component escape" in prospectus, "prospectus target C")
    require("Target A may supply some `C_3` chains, but it does not supply this coverage or comparison theorem by itself" in prospectus, "prospectus A versus B scope")
    require("Only Targets B and C together" in prospectus, "prospectus B plus C logic")
    require("Target A is a high-leverage possible input to B, not a D3 theorem and not a substitute for C" in prospectus, "prospectus A nonconsequences")

    combined = "\n".join(normalized.values())
    forbidden = [
        "V7 is the current authority",
        "CANONICAL_RESEARCH_STATE_V7.json is the current authority",
        "V8 authorizes mathematical construction",
        "V8 authorizes theorem credit",
        "Target A alone proves D3",
        "Target A alone proves diagonal three",
        "Target A alone yields global rank",
        "Target A implies triple escape",
    ]
    require(not any(phrase in combined for phrase in forbidden), "stale authority or A overclaim")


def validate(candidate: dict) -> None:
    require(candidate["format"] == "9dvl-canonical-research-state-v8", "format")
    require(candidate["status"] == "PIVOT_REQUIRED", "status")
    require(candidate["as_of"] == "2026-09-01", "as-of date")

    repository = candidate["repository"]
    require(repository["branch"] == "research/local-d3-mixed-carrier-theorem-feasibility-gate1-20260901", "branch")
    require(repository["canonical_close_commit"] == FROZEN_CLOSE, "close revision")
    require(repository["canonical_close_tree"] == FROZEN_CLOSE_TREE, "close tree")
    require(repository["integrated_referee_commit"] == INTEGRATED_REFEREE, "referee revision")
    require(repository["integrated_referee_tree"] == INTEGRATED_REFEREE_TREE, "referee tree")
    require(repository["saved_project_root"] == r"E:\Projects\9DVL Research", "project root")
    require(repository["mounted_recovery_status"] == "UNAVAILABLE_ACCESS_DENIED_NONBLOCKING", "recovery status")
    require(repository["drive_connector_used"] is False, "Drive connector")
    require(repository["github_mode"].startswith("READ_ONLY"), "GitHub mode")

    predecessor = candidate["predecessor"]
    require(predecessor["path"] == "ai/omreal/data/CANONICAL_RESEARCH_STATE_V7.json", "predecessor path")
    require(predecessor["sha256"] == PINS[predecessor["path"]], "predecessor pin")
    require(predecessor["policy"] == "IMMUTABLE_PRE_THEOREM_RESET_CANONICAL_STATE", "predecessor policy")
    require(predecessor["v7_selected_successor_disposition"] == "SUPERSEDED_BY_LATER_STOP_NONE_CLOSE", "V7 successor disposition")
    authoritative_cycle = candidate["authoritative_theorem_reset_cycle"]
    require(authoritative_cycle["id"] == "2026-09-01-theorem-reset-joined-gordan-tournament-gate1", "authoritative cycle")
    require(authoritative_cycle["policy"] == "ACCEPT_STOP_NONE_CLOSE_AS_AUTHORITATIVE", "supersession policy")
    require(authoritative_cycle["v7_factor19069_successor_remains_selected"] is False, "stale V7 successor")

    theorem = candidate["theorem"]
    require(theorem["id"] == "9DVL", "theorem id")
    require(theorem["score"] == "2/9" and theorem["proved_diagonals"] == [1, 2], "ledger")
    require(theorem["diagonal_three"] == theorem["diagonal_nine"] == "OPEN", "open diagonals")
    require(theorem["promotion"] == "NONE", "promotion")
    require(theorem["theorem_level_counterexample"] == "NOT_FOUND", "counterexample")

    close = candidate["theorem_reset_close"]
    require(close["trajectory"] == "STALLED", "trajectory")
    require(close["strategy_action"] == "STOP", "strategy action")
    require(close["overall_handoff"] == "NULL", "handoff")
    require(close["tournament_winner"] == "NONE", "tournament winner")
    require(close["eligible_construction_targets"] == 0, "eligible construction targets")
    require(close["selected_successor"] == "NONE", "selected successor")
    require(close["construction_started"] is False, "construction started")
    require(close["ledger_delta"] == "0/9", "ledger delta")
    require(close["same_blocker_cycle_streak"] == 5 and close["zero_ledger_cycle_streak"] == 8, "stagnation streaks")
    require(close["opening_vector"] == ["2/9", 1, "diag3_pair_hc1_AND_diag3_triple_hc0", 7, "UNKNOWN", "UNKNOWN", 4, 7], "opening vector")
    require(close["closing_vector"] == ["2/9", 1, "diag3_pair_hc1_AND_diag3_triple_hc0", 7, "UNKNOWN", "UNKNOWN", 5, 8], "closing vector")

    joined = close["joined_gordan"]
    require(joined["formal_face_type_denominator"] == 10, "joined denominator")
    require(joined["credited_universal_clauses"] == ["(0)", "(1)", "(2)"], "joined clauses")
    require(joined["universal_coverage"] == "3/10", "joined coverage")
    require(joined["new_universal_clause"] == "NONE", "new joined clause")
    require(joined["globally_attached"] is False, "joined attachment")
    require(joined["end_to_end_d3_denominator"] is False, "joined end-to-end denominator")
    require(joined["bounded_decrease_chain"] is False, "joined bounded chain")
    require(joined["critical_open_clause"] == "(1,0,0)", "critical joined clause")

    triple = close["triple_accounting"]
    require(triple["source_orbits"] - triple["settled_orbits"] == triple["residual_orbits"] == 1162302, "triple residual")
    require(triple["coverage"] == "77940147/79102449", "triple coverage")
    require(triple["residual_delta"] == 0, "triple delta")
    require(triple["source_order_semantic_sha256"] == "a76a7c2cd6631c2d9724b450540bec7f3be6c106a41ae41f1736bbd2755a5ca4", "triple semantic pin")
    require(triple["triple_only_closure_promotes_d3"] is False, "triple-only promotion")

    canary = close["row2599_chart0_canary"]
    require((canary["rank_d1"], canary["rank_d2"], canary["rank_C2"]) == (3, 6, 7), "canary ranks")
    require(canary["relative_homology"] == {"H0": "0", "H1": "0", "H2": "Z"}, "canary homology")
    require(canary["primitive_h2_relation"] == [-1, 1, 1, 1, 1, 1, 1], "canary primitive relation")
    require(canary["singleton_nerve_cocycle_value"] == 1 and canary["singleton_root_filler_retired"] is True, "canary singleton no-go")
    require(canary["genuine_mixed_block_carrier_nonexistence_proved"] is False, "mixed-carrier nonexistence")
    require(canary["d3_or_9dvl_counterexample"] is False, "canary counterexample scope")

    open_obligations = candidate["open_obligations"]
    require(open_obligations["load_bearing_count"] == 7, "open obligation count")
    require(open_obligations["pair_residual"] == open_obligations["pair_coverage"] == "UNKNOWN", "pair frontier")
    items = open_obligations["items"]
    require([item["id"] for item in items] == LOAD_BEARING_IDS, "open obligation ids")
    require(all(item["status"] == "INCONCLUSIVE" for item in items), "open obligation status")
    require(all(item["delta"] == "UNCHANGED" for item in items[:-1]), "open obligation delta")
    require(items[-1]["delta"] == 0 and items[-1]["residual"] == 1162302, "triple obligation frontier")
    require(canonical_digest(open_obligations) == OPEN_OBLIGATIONS_DIGEST, "open obligations digest")

    program = candidate["bounded_feasibility_program"]
    require(program["id"] == PROGRAM_ID, "feasibility program")
    require(program["selection_class"] == "ONE_ROUND_THREE_TARGET_THEOREM_FEASIBILITY_PROGRAM", "selection class")
    correction = program["scope_correction"]
    require(correction["target_a_alone_yields_global_rank"] is False, "A rank nonconsequence")
    require(correction["target_a_alone_yields_triple_escape"] is False, "A triple nonconsequence")
    require(correction["target_a_alone_proves_d3"] is False, "A D3 nonconsequence")
    require(correction["row2599_chart0_role"] == "DIAGNOSTIC_CANARY_ONLY_NOT_A_UNIVERSAL_GENERATOR_OR_DENOMINATOR", "row2599 scope")
    require(correction["formal_joined_3_of_10_is_complete_complex"] is False, "formal taxonomy scope")
    require(correction["one_escape_witness_per_triple_source_is_all_component_escape"] is False, "all-component scope")

    authorization = program["authorization"]
    require(authorization["proof_program_feasibility_analysis"] is True, "feasibility authorization")
    require(authorization["mathematical_construction"] is False, "construction authorization")
    require(authorization["carrier_or_atlas_enumeration"] is False, "enumeration authorization")
    require(authorization["theorem_credit"] is False and authorization["ledger_promotion"] is False, "theorem credit")
    require(authorization["automatic_cycle_reopening"] is False, "automatic reopening")
    bounds = program["round_bounds"]
    require((bounds["feasibility_rounds"], bounds["named_targets"], bounds["construction_rounds"], bounds["exact_diagnostic_canaries"]) == (1, 3, 0, 1), "round bounds")
    require(bounds["resource_enlargement_allowed"] is False, "resource bound")
    require(bounds["broad_residual_enumeration_allowed"] is False and bounds["new_global_census_allowed"] is False, "enumeration bound")

    logic = program["dependency_logic"]
    require(logic["target_a_is_strict_subproblem_nested_inside_target_b"] is True, "A inside B")
    require(logic["target_a_is_conditional_on_a_declared_interface_not_on_target_b"] is True, "A conditional interface")
    require(logic["target_a_does_not_assert_that_its_interface_exists_or_is_complete"] is True, "A interface scope")
    require(logic["target_b_constructs_and_verifies_target_a_interface_before_invocation"] is True, "B verifies A interface")
    require(logic["target_a_does_not_define_or_exhaust_the_global_kernel"] is True, "A kernel scope")
    require(logic["target_b_must_supply_the_complete_complex_before_any_global_rank_claim"] is True, "B before rank")
    require(logic["target_c_is_independent_of_targets_a_and_b"] is True, "C independence")
    require(logic["future_actual_target_b_consequence"] == "diag3_pair_hc1", "B consequence")
    require(logic["future_actual_target_c_consequence"] == "diag3_triple_hc0", "C consequence")
    require(logic["future_d3_proof_condition"] == "ACTUAL_THEOREM_B_AND_ACTUAL_THEOREM_C", "B plus C D3 gate")
    require(logic["feasibility_of_b_and_c_counts_as_d3_proof"] is False, "feasibility is not proof")

    targets = program["targets"]
    require(list(targets) == ["A", "B", "C"], "target labels")
    target_a = targets["A"]
    require(target_a["id"] == TARGET_A and target_a["status"] == "OPEN_FEASIBILITY", "target A identity")
    require(target_a["kind"] == "CONDITIONAL_SUBPROBLEM_INVOKED_BY_B_AFTER_INTERFACE_VERIFICATION", "target A nesting")
    interface = target_a["conditional_interface"]
    require(interface["id"] == "A0_CANDIDATE_LOWER_SKELETON_SOURCE_INTERFACE", "A interface identity")
    require(len(interface["required_inputs"]) == 4, "A interface inputs")
    require("ORIENTED_D1_D2_WITH_D1_COMPOSED_WITH_D2_ZERO_AND_A_FINITE_LIST_OF_RELEVANT_PRIMITIVE_INTEGRAL_KERNEL_CLASSES" in interface["required_inputs"], "A interface kernel input")
    require("DECLARED_SIMULTANEOUS_SUBDIVISION_AND_ITERATED_FACE_SPECIALIZATION_CATEGORY" in interface["required_inputs"], "A interface coherence input")
    require(interface["target_a_may_assume_interface_axioms_for_its_conditional_analysis"] is True, "A conditional assumption")
    require(interface["target_a_may_assert_interface_existence_exhaustiveness_or_bad_union_comparison"] is False, "A interface nonconsequence")
    require(interface["target_b_must_construct_and_verify_this_interface"] is True, "B interface duty")
    require(len(target_a["universal_axes"]) == 6, "target A axes")
    require("EVERY_RELEVANT_PRIMITIVE_INTEGRAL_KERNEL_CLASS_NOT_ONLY_ROW2599" in target_a["universal_axes"], "all primitive classes")
    require("EVERY_SOURCE_DERIVED_ADMISSIBLE_ANTICHAIN_NOT_ONLY_MINIMAL_SIGNATURES_OR_ONE_ORDERED_TRIPLE" in target_a["universal_axes"], "antichain precision")
    require("EVERY_PARENT_STRATUM_INCLUDING_PARENT_RANK_DROP_STRATA" in target_a["universal_axes"], "A parent rank-drop")
    require("ONE_COMMON_SIMULTANEOUS_SUBDIVISION_FOR_CHAINS_FACES_AND_ALL_SPECIALIZATIONS" in target_a["required_precision"], "A simultaneous subdivision")
    require("ITERATED_FACE_COHERENCE_FOR_ALL_SPECIALIZATION_COMPOSITES_NOT_ONLY_PAIRWISE_SQUARES" in target_a["required_precision"], "A iterated coherence")
    require("ROW2599_SINGLETON_NERVE_NO_GO_USED_ONLY_AS_A_DIAGNOSTIC_TEST" in target_a["required_precision"], "A canary scope")
    require("NO_GLOBAL_KERNEL_EXACTNESS_OR_RANK_IDENTITY" in target_a["nonconsequences"], "A no rank")
    require("NO_TRIPLE_TRUE_PARENT_INFINITY_ESCAPE" in target_a["nonconsequences"], "A no triple escape")

    target_b = targets["B"]
    require(target_b["id"] == TARGET_B and target_b["status"] == "OPEN_FEASIBILITY", "target B identity")
    require(target_b["kind"] == "GLOBAL_PAIR_BRANCH_PREREQUISITE_CONTAINING_A", "target B kind")
    require(target_b["constructs_and_verifies_interface"] == "A0_CANDIDATE_LOWER_SKELETON_SOURCE_INTERFACE", "target B interface construction")
    require(target_b["invokes_conditionally_after_interface_verification"] == TARGET_A, "target B conditional invocation")
    require(target_b["dependency_order"] == ["B_CONSTRUCTS_AND_VERIFIES_A0_INTERFACE", "A_APPLIES_CONDITIONALLY_TO_VERIFIED_A0", "B_COMPLETES_ALL_FACE_TYPES_BAD_UNION_COMPARISON_AND_RATIONAL_PAIR_EXACTNESS"], "target B dependency order")
    faces = target_b["face_type_accounting"]
    require(faces["joined_dimension_formula"] == "k=(r-1)+sum(k_i)", "joined dimension formula")
    require(faces["active_block_count_range"] == [1, 3], "active-block range")
    require(faces["taxonomy_quotient"] == "SHAPES_MODULO_ACTIVE_BLOCK_PERMUTATION", "face taxonomy quotient")
    require(faces["labeled_instance_quantifier"] == "ALL_SOURCE_DERIVED_LABELED_INSTANCES_OF_EVERY_SHAPE", "labeled face instances")
    require(faces["all_types"] == ALL_FACE_TYPES, "all joined face types")
    require(faces["already_universally_credited"] == ["(0)", "(1)", "(2)"], "credited face types")
    require(faces["missing_lower_types"] == MISSING_LOWER_TYPES, "missing lower face types")
    require(faces["missing_dimension_three_types"] == MISSING_DIMENSION_THREE_TYPES, "missing dimension-three face types")
    require("COVER_EVERY_SOURCE_DERIVED_ADMISSIBLE_ANTICHAIN" in target_b["required_precision"], "B antichain precision")
    require("COMMON_SIMULTANEOUS_SUBDIVISION_ACROSS_ALL_FACE_TYPES_CHARTS_SUPPORTS_AND_SPECIALIZATIONS" in target_b["required_precision"], "B simultaneous subdivision")
    require("ITERATED_FACE_COHERENCE_AND_D2_ZERO_FOR_EVERY_FACE_FLAG" in target_b["required_precision"], "B iterated coherence")
    require("PARENT_RANK_DROP_STRATA_INCLUDED_WITH_SOURCE_NATURAL_ATTACHMENTS" in target_b["required_precision"], "B parent rank-drop")
    require("COVERAGE_OF_THE_ACTUAL_BAD_UNION_NOT_ONLY_FORMAL_JOINED_TUPLES" in target_b["required_precision"], "bad-union coverage")
    require("EXPLICIT_RELATIVE_CHAIN_COMPARISON_TO_THE_ACTUAL_BAD_UNION_WITH_THE_REQUIRED_HOMOLOGY_EQUIVALENCE" in target_b["required_precision"], "bad-union comparison")
    require("RATIONAL_PAIR_KERNEL_EXACTNESS_TRANSPORTED_THROUGH_THE_COMPARISON" in target_b["required_precision"], "rational pair exactness")
    require(target_b["rational_pair_kernel_exactness_statement"] == "For the complete comparison complex C_pair^0 --N--> C_pair^1 --M--> C_pair^2 over Q, M composed with N is zero and im_Q(N)=ker_Q(M), equivalently rank_Q(N)+rank_Q(M)=dim_Q(C_pair^1); the comparison to the actual bad union transports this exactness to diag3_pair_hc1.", "pair-kernel statement")
    require(target_b["future_actual_theorem_consequence_only"] == "diag3_pair_hc1", "B actual consequence")
    require("NO_D3_WITHOUT_ACTUAL_TARGET_C" in target_b["nonconsequences"], "B alone no D3")

    target_c = targets["C"]
    require(target_c["id"] == TARGET_C and target_c["status"] == "OPEN_FEASIBILITY", "target C identity")
    require(target_c["kind"] == "INDEPENDENT_GLOBAL_TRIPLE_BRANCH", "target C kind")
    require(target_c["depends_on"] == [] and target_c["independent_of"] == [TARGET_A, TARGET_B], "target C independence")
    c_sources = target_c["source_accounting"]
    require(c_sources["source_orbits"] - c_sources["settled_orbits"] == c_sources["residual_orbits"] == 1162302, "C residual")
    require(c_sources["coverage"] == "77940147/79102449", "C coverage")
    require("EVERY_CONNECTED_COMPONENT_NOT_ONE_WITNESS_PER_SOURCE_ORBIT" in target_c["required_precision"], "C all components")
    require("PATH_REMAINS_IN_THE_ACTUAL_TRIPLE_BAD_LOCUS_UNTIL_GENUINE_TRUE_PARENT_INFINITY" in target_c["required_precision"], "C true infinity")
    require("SIMULTANEOUS_WALL_SUPPORT_CHART_DIVISOR_CONCURRENCE_AND_PARENT_RANK_DROP_STRATA" in target_c["required_precision"], "C parent rank-drop")
    require("ITERATED_BOUNDARY_FACE_COHERENCE_UNDER_ALL_SPECIALIZATIONS" in target_c["required_precision"], "C iterated coherence")
    require(target_c["future_actual_theorem_consequence_only"] == "diag3_triple_hc0", "C actual consequence")
    require("NO_D3_WITHOUT_ACTUAL_TARGET_B" in target_c["nonconsequences"], "C alone no D3")
    require(program["prohibited_overclaims_and_continuations"] == PROHIBITED, "prohibited continuations")

    outcomes = program["outcome_gates"]
    a_only = outcomes["target_a_only_feasible"]
    require(a_only["verdict"] == "PARTIAL_FEASIBILITY_STOP_WITHOUT_SUCCESSOR", "A-only gate")
    require(a_only["global_rank_credit"] is False and a_only["triple_escape_credit"] is False, "A-only nonconsequences")
    full = outcomes["full_program_feasible"]
    require(full["verdict"] == "QUALIFY_FOR_SEPARATE_GOVERNED_PROOF_CYCLE_SELECTION_ONLY" and len(full["requires"]) == 4, "full-program gate")
    negative = outcomes["negative_feasibility"]
    require(negative["verdict"] == "RETIRE_ONLY_THE_EXACT_UNIVERSALLY_QUANTIFIED_TARGET_THAT_FAILS", "negative gate")
    require(negative["local_canary_or_one_ansatz_alone_suffices"] is False, "negative scope")
    null = outcomes["null_or_timeout"]
    require(null["verdict"] == "STOP_AT_ONE_ROUND_BOUND_WITHOUT_SUCCESSOR", "null/timeout gate")
    for outcome in outcomes.values():
        require(outcome["construction_authorized"] is False and outcome["theorem_credit"] is False and outcome["ledger_effect"] == "0/9", "outcome noncredit")
    require(canonical_digest(program) == PROGRAM_DIGEST, "feasibility program digest")

    gates = candidate["process_gates"]
    require(gates["later_stop_none_close_overrides_v7_selected_successor"] is True, "STOP/NONE precedence")
    require(gates["v8_authorizes_one_a_b_c_feasibility_round_only"] is True, "one-round gate")
    require(gates["no_mathematical_construction_under_v8"] is True, "feasibility-only gate")
    require(gates["no_theorem_or_ledger_credit_from_feasibility"] is True, "noncredit gate")
    require(gates["target_a_alone_has_no_global_rank_or_triple_escape_consequence"] is True, "A scope gate")
    require(gates["row2599_canary_is_diagnostic_or_falsifying_only"] is True, "local-canary gate")
    require(gates["complete_source_derived_complex_precedes_any_global_rank_claim"] is True, "complete-complex gate")
    require(gates["actual_target_b_and_actual_target_c_are_both_required_for_d3"] is True, "B plus C gate")
    require(gates["feasibility_handoffs_do_not_prove_target_b_target_c_or_d3"] is True, "feasibility scope gate")
    require(gates["positive_feasibility_requires_new_governed_proof_cycle_selection"] is True, "fresh selection gate")
    require(gates["ledger_promotion_requires_independently_replayed_universal_diagonal_certificate"] is True, "promotion gate")
    require(gates["failure_or_timeout_is_fail_closed_stop"] is True, "fail-closed gate")
    require(gates["github_remains_read_only"] is True and gates["drive_connector_must_not_be_used"] is True, "storage gates")
    require(canonical_digest(gates) == PROCESS_GATES_DIGEST, "process gates digest")
    require(candidate["source_pins"] == PINS, "source pins")


def validate_frozen_sources(state: dict) -> None:
    require(git("rev-parse", f"{FROZEN_CLOSE}^{{tree}}") == FROZEN_CLOSE_TREE, "frozen close tree")
    require(git("rev-parse", f"{INTEGRATED_REFEREE}^{{tree}}") == INTEGRATED_REFEREE_TREE, "integrated referee tree")
    for path, expected in PINS.items():
        require(sha256(frozen(path)).hexdigest() == expected, f"frozen source pin {path}")

    v7 = frozen_json("ai/omreal/data/CANONICAL_RESEARCH_STATE_V7.json")
    require(v7["status"] == "PIVOT_REQUIRED" and v7["theorem"]["score"] == "2/9", "V7 ledger")
    require(v7["selected_successor"]["id"] == V7_SUCCESSOR, "V7 stale successor source")

    cycle_path = "ops/research-team/cycles/2026-09-01-theorem-reset-joined-gordan-tournament-gate1/"
    manifest = frozen_json(cycle_path + "CLOSING_MANIFEST.json")
    result = manifest["result"]
    require(result["closing_ledger"] == "2/9" and result["ledger_delta"] == "0/9", "manifest ledger")
    require(result["trajectory"] == "STALLED" and result["strategy_action"] == "STOP", "manifest STOP")
    require(result["tournament_winner"] == result["selected_successor"] == "NONE", "manifest NONE")
    require(result["eligible_construction_targets"] == 0 and result["construction_started"] is False, "manifest construction")

    closing = frozen_json(cycle_path + "CLOSING_CANDIDATE.json")
    require(closing["automatic_strategy_reset"]["action"] == "STOP", "closing reset action")
    require(closing["automatic_strategy_reset"]["same_route_continue_allowed"] is False, "closing same-route gate")
    require(closing["successor_bar"]["selected_successor"] == "NONE" and closing["successor_bar"]["eligible_route_count"] == 0, "closing successor bar")
    require(closing["joined_gordan_accounting"]["critical_open_clause"] == "(1,0,0)", "closing mixed clause")

    referee = frozen_json("ops/team/theorem-reset-closing-referee/RESULT.json")
    require(referee["verdict"] == "ACCEPT_FROZEN_CANDIDATE_FAIL_CLOSED", "referee verdict")
    require(referee["strategy_action"] == "STOP" and referee["selected_successor"] == "NONE", "referee STOP/NONE")
    require(referee["successor_bar"]["eligible_route_count"] == 0, "referee successor bar")
    require(referee["hostile_mutations"] == {"required": 40, "rejected": 40, "accepted": 0}, "referee hostiles")

    prover = frozen_json("ops/team/theorem-reset-prover-strategy/RESULT.json")
    mixed = prover["mixed_block_1_0_0_analysis"]
    require(prover["strategy_recommendation"] == "STOP_WITHOUT_SUCCESSOR", "prover STOP")
    require(mixed["genuine_mixed_block_carrier_nonexistence_proved"] is False, "prover mixed scope")
    require(mixed["first_missing_theorem"].startswith("Construct a finite globally attached mixed-block relative three-cell family"), "prover missing theorem")
    require(mixed["global_partial3_rank_identity_proved"] is False, "prover rank scope")

    graph = frozen_json(cycle_path + "OBLIGATION_GRAPH.json")
    graph_load_bearing = [node["id"] for node in graph["nodes"] if node.get("load_bearing")]
    require(graph_load_bearing == LOAD_BEARING_IDS, "obligation graph")
    require(["joined_local_flow_disk", "joined_mixed_block_1_0_0"] in graph["forbidden_edges"], "local-to-global forbidden edge")

    report = frozen(cycle_path + "CYCLE_REPORT.md").decode("utf-8")
    require("Tournament winner: **`NONE`**." in report and "strategy verdict is **`STOP`**" in report, "cycle report STOP/NONE")
    require("globally attached mixed" in report and "`(1,0,0)` carrier" in report, "cycle report surviving target")
    require(state["predecessor"]["sha256"] == sha256(frozen(state["predecessor"]["path"])).hexdigest(), "predecessor frozen pin")


def hostile_mutations(stored: dict) -> int:
    mutations: list[tuple[dict, str]] = []

    def add(path: tuple[str, ...], value: object, marker: str) -> None:
        candidate = deepcopy(stored)
        cursor = candidate
        for key in path[:-1]:
            cursor = cursor[key]
        cursor[path[-1]] = value
        mutations.append((candidate, marker))

    add(("format",), "9dvl-canonical-research-state-v7", "format")
    add(("status",), "ACTIVE", "status")
    add(("repository", "canonical_close_commit"), "0" * 40, "close revision")
    add(("repository", "canonical_close_tree"), "0" * 40, "close tree")
    add(("repository", "branch"), "research/local-theorem-reset-joined-gordan-tournament-20260901", "branch")
    add(("repository", "drive_connector_used"), True, "Drive connector")
    add(("repository", "github_mode"), "WRITE_ALLOWED", "GitHub mode")
    add(("predecessor", "sha256"), "0" * 64, "predecessor pin")
    add(("predecessor", "v7_selected_successor_disposition"), "STILL_SELECTED", "V7 successor disposition")
    add(("authoritative_theorem_reset_cycle", "v7_factor19069_successor_remains_selected"), True, "stale V7 successor")
    add(("theorem", "score"), "3/9", "ledger")
    add(("theorem", "proved_diagonals"), [1, 2, 3], "ledger")
    add(("theorem", "promotion"), "DIAGONAL_3", "promotion")
    add(("theorem_reset_close", "trajectory"), "PROGRESS", "trajectory")
    add(("theorem_reset_close", "strategy_action"), "CONTINUE", "strategy action")
    add(("theorem_reset_close", "tournament_winner"), PROGRAM_ID, "tournament winner")
    add(("theorem_reset_close", "eligible_construction_targets"), 1, "eligible construction targets")
    add(("theorem_reset_close", "selected_successor"), PROGRAM_ID, "selected successor")
    add(("theorem_reset_close", "construction_started"), True, "construction started")
    add(("theorem_reset_close", "joined_gordan", "universal_coverage"), "4/10", "joined coverage")
    add(("theorem_reset_close", "joined_gordan", "new_universal_clause"), "(1,0,0)", "new joined clause")
    add(("theorem_reset_close", "joined_gordan", "globally_attached"), True, "joined attachment")
    add(("theorem_reset_close", "triple_accounting", "residual_orbits"), 0, "triple residual")
    add(("theorem_reset_close", "row2599_chart0_canary", "relative_homology"), {"H0": "0", "H1": "0", "H2": "0"}, "canary homology")
    add(("theorem_reset_close", "row2599_chart0_canary", "genuine_mixed_block_carrier_nonexistence_proved"), True, "mixed-carrier nonexistence")
    add(("open_obligations", "pair_residual"), 0, "pair frontier")

    candidate = deepcopy(stored)
    candidate["open_obligations"]["items"][0]["status"] = "PROVED"
    mutations.append((candidate, "open obligation status"))

    add(("bounded_feasibility_program", "id"), "CONSTRUCT_CARRIER_NOW", "feasibility program")
    add(("bounded_feasibility_program", "scope_correction", "target_a_alone_yields_global_rank"), True, "A rank nonconsequence")
    add(("bounded_feasibility_program", "scope_correction", "target_a_alone_yields_triple_escape"), True, "A triple nonconsequence")
    add(("bounded_feasibility_program", "scope_correction", "row2599_chart0_role"), "UNIVERSAL_GENERATOR", "row2599 scope")
    add(("bounded_feasibility_program", "scope_correction", "formal_joined_3_of_10_is_complete_complex"), True, "formal taxonomy scope")
    add(("bounded_feasibility_program", "scope_correction", "one_escape_witness_per_triple_source_is_all_component_escape"), True, "all-component scope")
    add(("bounded_feasibility_program", "authorization", "mathematical_construction"), True, "construction authorization")
    add(("bounded_feasibility_program", "authorization", "carrier_or_atlas_enumeration"), True, "enumeration authorization")
    add(("bounded_feasibility_program", "authorization", "theorem_credit"), True, "theorem credit")
    add(("bounded_feasibility_program", "authorization", "ledger_promotion"), True, "theorem credit")
    add(("bounded_feasibility_program", "authorization", "automatic_cycle_reopening"), True, "automatic reopening")
    add(("bounded_feasibility_program", "round_bounds", "feasibility_rounds"), 2, "round bounds")
    add(("bounded_feasibility_program", "round_bounds", "resource_enlargement_allowed"), True, "resource bound")
    add(("bounded_feasibility_program", "dependency_logic", "target_a_is_conditional_on_a_declared_interface_not_on_target_b"), False, "A conditional interface")
    add(("bounded_feasibility_program", "dependency_logic", "target_a_does_not_assert_that_its_interface_exists_or_is_complete"), False, "A interface scope")
    add(("bounded_feasibility_program", "dependency_logic", "target_b_constructs_and_verifies_target_a_interface_before_invocation"), False, "B verifies A interface")
    add(("bounded_feasibility_program", "dependency_logic", "target_b_must_supply_the_complete_complex_before_any_global_rank_claim"), False, "B before rank")
    add(("bounded_feasibility_program", "dependency_logic", "target_c_is_independent_of_targets_a_and_b"), False, "C independence")
    add(("bounded_feasibility_program", "dependency_logic", "future_d3_proof_condition"), "TARGET_A_ALONE", "B plus C D3 gate")
    add(("bounded_feasibility_program", "dependency_logic", "feasibility_of_b_and_c_counts_as_d3_proof"), True, "feasibility is not proof")

    add(("bounded_feasibility_program", "targets", "A", "kind"), "DEPENDS_ON_COMPLETED_B", "target A nesting")
    add(("bounded_feasibility_program", "targets", "A", "conditional_interface", "id"), "UNDECLARED_INTERFACE", "A interface identity")
    add(("bounded_feasibility_program", "targets", "A", "conditional_interface", "target_a_may_assume_interface_axioms_for_its_conditional_analysis"), False, "A conditional assumption")
    add(("bounded_feasibility_program", "targets", "A", "conditional_interface", "target_a_may_assert_interface_existence_exhaustiveness_or_bad_union_comparison"), True, "A interface nonconsequence")
    add(("bounded_feasibility_program", "targets", "A", "conditional_interface", "target_b_must_construct_and_verify_this_interface"), False, "B interface duty")

    candidate = deepcopy(stored)
    candidate["bounded_feasibility_program"]["targets"]["A"]["universal_axes"][0] = "ROW2599_ONLY"
    mutations.append((candidate, "all primitive classes"))
    candidate = deepcopy(stored)
    candidate["bounded_feasibility_program"]["targets"]["A"]["universal_axes"][1] = "ONE_ORDERED_TRIPLE"
    mutations.append((candidate, "antichain precision"))
    candidate = deepcopy(stored)
    candidate["bounded_feasibility_program"]["targets"]["A"]["required_precision"][1] = "SEPARATE_SUBDIVISIONS"
    mutations.append((candidate, "A simultaneous subdivision"))
    candidate = deepcopy(stored)
    candidate["bounded_feasibility_program"]["targets"]["A"]["required_precision"][2] = "PAIRWISE_SQUARES_ONLY"
    mutations.append((candidate, "A iterated coherence"))

    add(("bounded_feasibility_program", "targets", "B", "constructs_and_verifies_interface"), "NONE", "target B interface construction")
    add(("bounded_feasibility_program", "targets", "B", "invokes_conditionally_after_interface_verification"), "BEFORE_INTERFACE", "target B conditional invocation")
    add(("bounded_feasibility_program", "targets", "B", "dependency_order"), ["A_APPLIES_FIRST"], "target B dependency order")
    add(("bounded_feasibility_program", "targets", "B", "face_type_accounting", "joined_dimension_formula"), "k=sum(k_i)", "joined dimension formula")
    add(("bounded_feasibility_program", "targets", "B", "face_type_accounting", "active_block_count_range"), [1, 4], "active-block range")
    add(("bounded_feasibility_program", "targets", "B", "face_type_accounting", "taxonomy_quotient"), "LABELED_TYPES_ONLY", "face taxonomy quotient")
    add(("bounded_feasibility_program", "targets", "B", "face_type_accounting", "labeled_instance_quantifier"), "ONE_REPRESENTATIVE_PER_SHAPE", "labeled face instances")
    add(("bounded_feasibility_program", "targets", "B", "face_type_accounting", "missing_lower_types"), [], "missing lower face types")
    add(("bounded_feasibility_program", "targets", "B", "face_type_accounting", "missing_dimension_three_types"), ["(1,0,0)"], "missing dimension-three face types")
    add(("bounded_feasibility_program", "targets", "B", "rational_pair_kernel_exactness_statement"), "rank(d2)+rank(d3)=rank(C2) locally", "pair-kernel statement")

    candidate = deepcopy(stored)
    candidate["bounded_feasibility_program"]["targets"]["B"]["required_precision"][5] = "FORMAL_TUPLES_ONLY"
    mutations.append((candidate, "bad-union coverage"))
    candidate = deepcopy(stored)
    candidate["bounded_feasibility_program"]["targets"]["B"]["required_precision"][6] = "NO_COMPARISON_MAP"
    mutations.append((candidate, "bad-union comparison"))
    candidate = deepcopy(stored)
    candidate["bounded_feasibility_program"]["targets"]["B"]["required_precision"][8] = "RANK_COUNT_ONLY"
    mutations.append((candidate, "rational pair exactness"))

    add(("bounded_feasibility_program", "targets", "C", "depends_on"), [TARGET_B], "target C independence")
    add(("bounded_feasibility_program", "targets", "C", "source_accounting", "residual_orbits"), 0, "C residual")
    add(("bounded_feasibility_program", "targets", "C", "future_actual_theorem_consequence_only"), "D3", "C actual consequence")
    candidate = deepcopy(stored)
    candidate["bounded_feasibility_program"]["targets"]["C"]["required_precision"][0] = "ONE_WITNESS_PER_SOURCE"
    mutations.append((candidate, "C all components"))
    candidate = deepcopy(stored)
    candidate["bounded_feasibility_program"]["targets"]["C"]["required_precision"][2] = "LOCAL_RADIAL_EXIT"
    mutations.append((candidate, "C true infinity"))
    candidate = deepcopy(stored)
    candidate["bounded_feasibility_program"]["targets"]["C"]["required_precision"][3] = "GENERIC_PARENT_ONLY"
    mutations.append((candidate, "C parent rank-drop"))
    candidate = deepcopy(stored)
    candidate["bounded_feasibility_program"]["prohibited_overclaims_and_continuations"].pop()
    mutations.append((candidate, "prohibited continuations"))

    add(("bounded_feasibility_program", "outcome_gates", "target_a_only_feasible", "global_rank_credit"), True, "A-only nonconsequences")
    add(("bounded_feasibility_program", "outcome_gates", "full_program_feasible", "construction_authorized"), True, "outcome noncredit")
    add(("bounded_feasibility_program", "outcome_gates", "negative_feasibility", "local_canary_or_one_ansatz_alone_suffices"), True, "negative scope")
    add(("bounded_feasibility_program", "outcome_gates", "null_or_timeout", "verdict"), "CONTINUE", "null/timeout gate")
    add(("process_gates", "later_stop_none_close_overrides_v7_selected_successor"), False, "STOP/NONE precedence")
    add(("process_gates", "v8_authorizes_one_a_b_c_feasibility_round_only"), False, "one-round gate")
    add(("process_gates", "no_mathematical_construction_under_v8"), False, "feasibility-only gate")
    add(("process_gates", "no_theorem_or_ledger_credit_from_feasibility"), False, "noncredit gate")
    add(("process_gates", "target_a_alone_has_no_global_rank_or_triple_escape_consequence"), False, "A scope gate")
    add(("process_gates", "complete_source_derived_complex_precedes_any_global_rank_claim"), False, "complete-complex gate")
    add(("process_gates", "actual_target_b_and_actual_target_c_are_both_required_for_d3"), False, "B plus C gate")
    add(("process_gates", "feasibility_handoffs_do_not_prove_target_b_target_c_or_d3"), False, "feasibility scope gate")
    add(("process_gates", "ledger_promotion_requires_independently_replayed_universal_diagonal_certificate"), False, "promotion gate")

    candidate = deepcopy(stored)
    first_pin = next(iter(candidate["source_pins"]))
    candidate["source_pins"][first_pin] = "0" * 64
    mutations.append((candidate, "source pins"))

    for candidate, marker in mutations:
        try:
            validate(candidate)
        except Reject as error:
            require(marker in str(error), f"wrong hostile rejection {marker}: {error}")
            continue
        raise Reject(f"hostile mutation accepted: {marker}")
    return len(mutations)


def hostile_authority_mutations() -> int:
    stored = current_authority_surfaces()
    mutations: list[tuple[dict[str, str], str]] = []

    candidate = deepcopy(stored)
    candidate["readme"] = candidate["readme"].replace("CANONICAL_RESEARCH_STATE_V8.json", "CANONICAL_RESEARCH_STATE_V7.json")
    mutations.append((candidate, "README V8 authority"))
    candidate = deepcopy(stored)
    candidate["readme"] = candidate["readme"].replace("NINE_DIAGONAL_STATUS_V5.md", "NINE_DIAGONAL_STATUS.md")
    mutations.append((candidate, "README V5 status"))
    candidate = deepcopy(stored)
    candidate["operating_system"] = candidate["operating_system"].replace("verify_canonical_research_state_v8.py", "verify_canonical_research_state_v7.py")
    mutations.append((candidate, "operating-system V8 verifier"))
    candidate = deepcopy(stored)
    candidate["status_v5"] = candidate["status_v5"].replace("`1 <= r <= 3`", "`1 <= r <= 4`")
    mutations.append((candidate, "status face taxonomy scope"))
    candidate = deepcopy(stored)
    candidate["status_v5"] = candidate["status_v5"].replace("interface before invoking A.", "interface only after completed A.")
    mutations.append((candidate, "status noncircular interface"))
    candidate = deepcopy(stored)
    candidate["status_v5"] = candidate["status_v5"].replace("Only actual theorems B and C together could settle diagonal three.", "Target A alone proves diagonal three.")
    mutations.append((candidate, "status B plus C logic"))
    candidate = deepcopy(stored)
    candidate["prospectus"] = candidate["prospectus"].replace("**Only Targets B and C together**", "**Target A alone**")
    mutations.append((candidate, "prospectus B plus C logic"))
    candidate = deepcopy(stored)
    candidate["readme"] += "\nV7 is the current authority.\n"
    mutations.append((candidate, "stale authority or A overclaim"))

    for candidate, marker in mutations:
        try:
            validate_authority_content(candidate)
        except Reject as error:
            require(marker in str(error), f"wrong authority hostile rejection {marker}: {error}")
            continue
        raise Reject(f"authority hostile mutation accepted: {marker}")
    return len(mutations)


def main() -> None:
    state = json.loads(STATE_PATH.read_text(encoding="utf-8"))
    validate(state)
    validate_frozen_sources(state)
    authority = current_authority_surfaces()
    validate_authority_content(authority)
    hostile_count = hostile_mutations(state) + hostile_authority_mutations()
    print("PASS canonical 9DVL research state V8")
    print("ledger=2/9 status=PIVOT_REQUIRED close=STALLED/STOP/NONE")
    print(f"hostile_mutations={hostile_count} target=A_SUBPROBLEM_B_PAIR_COMPLEX_C_TRIPLE_ESCAPE_FEASIBILITY_ONLY")


if __name__ == "__main__":
    main()
