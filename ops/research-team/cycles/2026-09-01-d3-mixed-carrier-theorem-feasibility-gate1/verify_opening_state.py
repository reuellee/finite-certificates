#!/usr/bin/env python3
"""Fail-closed verifier for the nested A/B/C D3 feasibility opening.

Only the standard library is used.  The live file is byte-sealed, while the
hostile suite disables that seal and tests the logical checks themselves.
"""

from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path
import subprocess
import sys
from typing import Any, Callable


HERE = Path(__file__).resolve().parent
REPO = HERE.parents[3]
STATE_PATH = HERE / "OPENING_STATE.json"
BASE_COMMIT = "9116771ba80ed3d033516d0dd666b34348aad348"
BASE_TREE = "a64438426dc792af67d5ccc0dd2f4d1231dbaa14"
STATE_SHA256 = "778d638d83f04a8beecbc400bb6ffc268698b694a8d2647e3da91ff5e8bb74d0"
CHARTER_PATH = (
    "ops/research-team/cycles/"
    "2026-09-01-d3-mixed-carrier-theorem-feasibility-gate1/CYCLE.md"
)
CHARTER_SHA256 = "f7fcb36b2a734ae89188ae347eb332b59a0169aaefbccf07702619760371ba81"

TOP_LEVEL_KEYS = {
    "format", "cycle_id", "mode", "opening_action", "canonical_base",
    "canonical_opening", "strategy_evaluation", "selected_target",
    "opening_facts", "proof_distance", "handoffs", "roles",
    "deliverable_ceiling", "midpoint", "stop_rules", "authority",
    "charter", "source_pins",
}

DOMAIN = {
    "parents": "ALL_REALIZABLE_UNIFORM_RANK4_PARENTS_ON_8_AND_NORMALIZED_REALIZATION_CELLS",
    "signature_families": "ALL_PROPER_ANTICHAINS_OF_PAIRWISE_INCOMPARABLE_PROPER_EXTENSION_SIGNATURES",
    "active_block_range": [1, 3],
    "shape_quotient": "MODULO_ACTIVE_BLOCK_PERMUTATION_WITH_ALL_LABELED_INSTANCES_COVERED",
    "supports": "ALL_ADMISSIBLE_WITNESS_SUPPORT_STRATA",
    "subdivision": "ONE_SIMULTANEOUS_SUBDIVISION_FOR_ALL_BLOCKS_WEIGHTS_SUPPORTS_CHARTS_AND_BOUNDARIES",
    "coherence": "ALL_ARBITRARY_COMPOSABLE_FACE_CHAINS_NOT_ONLY_CODIMENSION_ONE_SQUARES",
    "rank_drop_policy": "PARENT_MATRIX_RANK_DROP_AND_WITNESS_MATRIX_OR_SUPPORT_RANK_DROP_ARE_DISTINCT_STRATA",
}

A_OBLIGATIONS = [
    "FINITE_GENUINELY_MIXED_INTEGRAL_CHAIN_FAMILY",
    "PRIMITIVE_BOUNDARY_MINUS1_PLUS1_PLUS1_PLUS1_PLUS1_PLUS1_PLUS1",
    "CERTIFIED_LOWER_JOINED_OR_GENUINE_TRUE_PARENT_BOUNDARY_TERMS",
    "SUPPORT_ZERO_WEIGHT_CHART_MONODROMY_PARENT_BOUNDARY_AND_WITNESS_SPECIALIZATION",
    "SIMULTANEOUS_SUBDIVISION",
    "ARBITRARY_FACE_CHAIN_COHERENCE",
    "ACTIVE_BLOCK_PERMUTATION_EQUIVARIANCE",
    "PARENT_VERSUS_WITNESS_RANK_DROP_DISTINCTION",
]
A_FORBIDDEN = [
    "NO_GLOBAL_RANK_CLAIM",
    "NO_PAIR_KERNEL_EXACTNESS_CLAIM",
    "NO_TRIPLE_ESCAPE_CLAIM",
    "NO_D3_OR_LEDGER_CLAIM",
]
TEN_SHAPES = [
    "(0)", "(1)", "(0,0)", "(2)", "(1,0)", "(0,0,0)",
    "(3)", "(2,0)", "(1,1)", "(1,0,0)",
]
MISSING_SHAPES = [
    "(0,0)", "(1,0)", "(0,0,0)", "(3)", "(2,0)", "(1,1)",
    "(1,0,0)",
]
B_OBLIGATIONS = [
    "COMPLETE_SOURCE_DERIVED_JOINED_RELATIVE_COMPLEX",
    "STABLE_PARENT_SIGNATURE_BLOCK_SUPPORT_ORIENTATION_AND_INFINITY_PROVENANCE",
    "ONE_SIMULTANEOUS_SUBDIVISION",
    "ARBITRARY_FACE_CHAIN_COHERENCE_AND_D_SQUARED_ZERO",
    "FILTRATION_PRESERVING_COMPARISON_TO_ACTUAL_COMPACTIFIED_JOINED_CECH_COMPLEX",
    "RATIONAL_PAIR_KERNEL_EXACTNESS",
]
C_FORBIDDEN_ESCAPE = [
    "WITNESS_SUPPORT_LOSS", "WITNESS_KERNEL_RANK_DROP", "ZERO_BLOCK_WEIGHT",
    "ARTIFICIAL_BOX_BOUNDARY", "TARGET_A_BOUNDARY_BOOKKEEPING",
    "TARGET_B_RELATIVE_QUOTIENT", "CONVEX_BLOCK_MASS_TRANSFER",
]
FORBIDDEN_CREDIT = [
    "LOCAL_ONLY_CHAIN_OR_ROW2599_GENERALIZATION",
    "FINITE_SAMPLE_OR_CHARTWISE_ONLY",
    "SINGLETON_ROOT_OR_ONE_FIXED_BAD_BLOCK_FILLER",
    "SEPARATE_PER_BLOCK_SUBDIVISIONS",
    "CODIMENSION_ONE_ONLY_COHERENCE",
    "UNTRACKED_ACTIVE_BLOCK_PERMUTATION",
    "NON_ANTICHAIN_OR_IMPROPER_SIGNATURE_DOMAIN",
    "PARENT_AND_WITNESS_RANK_DROP_CONFLATION",
    "ARTIFICIAL_OR_CLIPPED_BOUNDARY",
    "UNCOMPARED_PARTIAL_COMPLEX_USED_FOR_PAIR_EXACTNESS",
    "TARGET_A_OR_B_USED_AS_TARGET_C_ESCAPE",
]

STOP_RULES = [
    "BASE_TREE_LEDGER_OR_SOURCE_PIN_DRIFT",
    "LOCAL_ROW2599_SAMPLED_OR_CHARTWISE_CHAIN_OFFERED_AS_COMPLETE_PROOF_PROGRAM",
    "SINGLETON_ROOT_ONE_BLOCK_COLLAR_MACROBOX_CLIPPED_OR_ARTIFICIAL_BOUNDARY_SUBSTITUTE",
    "PROPER_ANTICHAIN_R1_TO_3_PERMUTATION_OR_ALL_LABELED_INSTANCE_SCOPE_OMITTED",
    "SEPARATE_PER_BLOCK_SUBDIVISION_OR_CODIMENSION_ONE_ONLY_COHERENCE",
    "PARENT_MATRIX_AND_WITNESS_MATRIX_OR_SUPPORT_RANK_DROP_CONFLATED",
    "TRUE_PARENT_INFINITY_REPLACED_BY_LOCAL_CUTOFF",
    "A_ASSUMES_COMPLETE_B_OR_B_FAILS_TO_CONSTRUCT_AND_VERIFY_L_SOURCE",
    "A_ASSERTS_GLOBAL_RANK_PAIR_KERNEL_TRIPLE_ESCAPE_OR_D3",
    "PAIR_KERNEL_INFERRED_FROM_A_LOCAL_H2_ANONYMOUS_TAXONOMY_OR_UNCOMPARED_PARTIAL_COMPLEX",
    "B_OMITS_MISSING_FACE_TYPE_SOURCE_PROVENANCE_OR_FILTRATION_PRESERVING_COMPARISON",
    "C_INFERRED_FROM_A_BOUNDARY_B_QUOTIENT_WITNESS_DEGENERATION_SUPPORT_LOSS_OR_CONVEX_MASS_TRANSFER",
    "JOINED_3_OF_10_USED_AS_END_TO_END_DENOMINATOR",
    "TRIPLE_ONLY_ACCOUNTING_USED_WHILE_PAIR_BRANCH_IS_OMITTED",
    "CONSTRUCTION_ATLAS_CENSUS_BROAD_SAMPLE_THIRD_PASS_OR_CEILING_ENLARGEMENT",
    "LANE_SELF_CERTIFICATION_OR_REFEREE_IMPORTS_PRODUCER_ACCEPTANCE",
    "POSITIVE_PROGRAM_RELABELED_AS_PROOF_OR_A_ONLY_CONTINUATION",
    "CANONICAL_STATE_LEDGER_STATUS_EDIT_OR_THEOREM_PROMOTION",
    "GITHUB_CONNECTOR_NETWORK_PAID_EXTERNAL_COMPUTE_OR_IRREVERSIBLE_MUTATION",
]

SOURCE_PINS = [
    ("ops/research-team/PROTOCOL.md", 11222,
     "c3fbec5b483426fcce97a523ba1ea1edc3e561cb33a1c4e5e957674e4270a246"),
    ("ops/research-team/cycles/2026-09-01-theorem-reset-joined-gordan-tournament-gate1/CLOSING_MANIFEST.json", 4187,
     "2ef455643cc1a20812ea76a57ec650d6b251b522049851913aeedc7bcffccaea"),
    ("ops/research-team/cycles/2026-09-01-theorem-reset-joined-gordan-tournament-gate1/CYCLE_REPORT.md", 10862,
     "ccb34a1b416bd65920a0b50f780e66292eece697847afe8042b4d7a2fd6a0df0"),
    ("ops/team/theorem-reset-prover-strategy/FINDINGS.md", 10081,
     "4ce7b6504cb07f75779660f0a7d04681a7e98bb5d0a72e3fb9b2884267ace9b1"),
    ("ops/team/theorem-reset-falsifier/FINDINGS.md", 6659,
     "893ecc8d530e7af0970cc4bb232fb34e99cb8fc5e0e6b073c93d423c7313420f"),
    ("ai/omreal/DIAG3_JOINED_FLOW_TRIANGLE.md", 16265,
     "20aafd28f9624ca595a44e3124934baa4d33b942b6c8eca6bff210fedb114c8a"),
    ("ai/omreal/verify_diag3_joined_flow_triangle.py", 9283,
     "ac01851b53d4bed1c859f74bad2e71a5025825fe7accdac13263f5d6518a0944"),
    ("ai/omreal/DIAG3_SINGLE_BAD_TWO_SKELETON.md", 13943,
     "141da1b6d9fcd4f601e79871aaa5d06cb98721ece928a0d0d5af83518bddf71f"),
    ("ai/omreal/verify_diag3_single_bad_two_skeleton.py", 7350,
     "0ae6a9d54abcddbeb68be882083c52e1e6a9735941cea42eebacdf91ef77bda4"),
    ("ai/omreal/DIAG3_ARCHITECTURE_ADVERSARIAL_AUDIT.md", 12448,
     "046dc84c138cbbed9add0946392d72ddb3b73b332ddb4c9029ea54348a85562e"),
    ("ai/omreal/DIAG3_GLOBAL_EXIT_CRITERION.md", 7170,
     "0a372197a49f4a767c06b23a6df830ef2784e7fe653b4b3eb1a506eec0518e27"),
    ("ai/omreal/NINE_DIAGONAL_STATUS.md", 135472,
     "07c146e835f6a62c29ab653d353d73469df1e6022018ffec76f6775b65ca7ae2"),
    ("ai/omreal/data/DIAG3_RESEARCH_DECISION_LEDGER.json", 90677,
     "73b0b742d6336d754ae99b7054858a3a3c96b3aaf1601b2228c076a732903d6e"),
]
PIN_OBJECTS = [
    {"path": path, "bytes": size, "sha256": sha}
    for path, size, sha in SOURCE_PINS
]


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def eq(errors: list[str], label: str, actual: Any, expected: Any) -> None:
    if actual != expected:
        errors.append(f"{label}: expected {expected!r}, got {actual!r}")


def get(document: Any, *path: Any) -> Any:
    cursor = document
    try:
        for key in path:
            cursor = cursor[key]
        return cursor
    except (KeyError, IndexError, TypeError):
        return None


def git(*args: str) -> str:
    result = subprocess.run(
        ["git", *args], cwd=REPO, check=False, text=True,
        stdout=subprocess.PIPE, stderr=subprocess.PIPE, encoding="utf-8",
    )
    if result.returncode:
        raise RuntimeError(result.stderr.strip() or "git failed")
    return result.stdout.strip()


def validate(document: Any, *, external: bool) -> list[str]:
    errors: list[str] = []
    if not isinstance(document, dict):
        return ["opening state is not an object"]
    eq(errors, "top-level keys", set(document), TOP_LEVEL_KEYS)
    eq(errors, "format", document.get("format"),
       "d3-mixed-carrier-theorem-feasibility-opening-v1")
    eq(errors, "cycle id", document.get("cycle_id"),
       "2026-09-01-d3-mixed-carrier-theorem-feasibility-gate1")
    eq(errors, "mode", document.get("mode"),
       "BOUNDED_THEOREM_FIRST_FEASIBILITY_NOT_CONSTRUCTION")
    eq(errors, "action", document.get("opening_action"), "PIVOT")
    eq(errors, "base", document.get("canonical_base"), {
        "commit": BASE_COMMIT, "tree": BASE_TREE,
        "subject": "research: close theorem-level strategy reset",
        "immutable": True,
    })
    eq(errors, "canonical opening", document.get("canonical_opening"), {
        "ledger": "2/9", "proved_diagonals": [1, 2], "promotion": "NONE",
        "status": "PIVOT_REQUIRED", "concurrent_authoritative_cycles": [],
    })

    strategy = document.get("strategy_evaluation", {})
    eq(errors, "selected strategy id", get(strategy, "routes", 0, "id"),
       "D3_NESTED_A_B_C_THEOREM_FEASIBILITY")
    eq(errors, "selected strategy disposition",
       get(strategy, "routes", 0, "disposition"), "SELECTED_FEASIBILITY_ONLY")
    eq(errors, "strategy construction readiness",
       strategy.get("construction_ready"), False)
    eq(errors, "selection reason", strategy.get("selection_reason"),
       "USER_SELECTED_THEOREM_FIRST_PLAN_AFTER_PREDECESSOR_STOP_WITH_A_AS_A_CONDITIONAL_FEASIBILITY_INPUT_TO_B_AND_C_AS_AN_INDEPENDENT_D3_BRANCH")

    target = document.get("selected_target", {})
    eq(errors, "target id", target.get("id"),
       "D3_NESTED_A_B_C_THEOREM_FEASIBILITY")
    eq(errors, "selected target count", target.get("selected_count"), 1)
    eq(errors, "decision kind", target.get("decision_kind"),
       "COMPLETE_FINITE_PROOF_PROGRAM_OR_SCOPED_UNIVERSAL_NO_GO")
    eq(errors, "domain", target.get("domain"), DOMAIN)

    a = target.get("target_a", {})
    eq(errors, "A id", a.get("id"), "A_UNIVERSAL_MIXED_100_CHAIN_SPECIALIZATION")
    eq(errors, "A kind", a.get("kind"),
       "CONDITIONAL_INTEGRAL_CHAIN_THEOREM_PROGRAM")
    eq(errors, "A interface", a.get("declared_input_interface"),
       "L_SOURCE_LABELED_LOWER_JOINED_GENERATORS_ORIENTATIONS_BOUNDARY_TAGS_AND_SPECIALIZATION_MAPS")
    eq(errors, "A cannot assume B",
       a.get("interface_hypotheses_may_assume_complete_b"), False)
    eq(errors, "B constructs A interface",
       a.get("b_must_construct_and_verify_interface_from_sources"), True)
    eq(errors, "A shape", a.get("face_shape"), "(1,0,0)_AND_PERMUTATIONS")
    eq(errors, "A obligations", a.get("required_program_obligations"), A_OBLIGATIONS)
    eq(errors, "A forbidden consequences", a.get("forbidden_consequences"),
       A_FORBIDDEN)

    b = target.get("target_b", {})
    eq(errors, "B id", b.get("id"),
       "B_COMPLETE_SOURCE_DERIVED_JOINED_COMPARISON")
    eq(errors, "B constructs L_source",
       b.get("constructs_and_verifies_l_source_before_invoking_a"), True)
    eq(errors, "B coefficient domains", b.get("coefficient_domains"),
       ["Z_FOR_RELATIVE_COMPLEX", "Q_FOR_PAIR_KERNEL"])
    eq(errors, "B r range", b.get("active_block_range"), [1, 3])
    eq(errors, "B ten shapes", b.get("ten_shapes_modulo_permutation"), TEN_SHAPES)
    eq(errors, "B all labeled instances", b.get("all_labeled_instances_required"),
       True)
    eq(errors, "B missing shapes", b.get("still_missing_shapes"), MISSING_SHAPES)
    eq(errors, "B obligations", b.get("required_program_obligations"),
       B_OBLIGATIONS)
    eq(errors, "B pair kernel", b.get("pair_kernel_statement"),
       "ker[direct_sum_(i<j) H_c^1(B_i intersect B_j;Q) -> H_c^1(B_0 intersect B_1 intersect B_2;Q)] = 0")
    eq(errors, "A does not imply B", b.get("implied_by_a_alone"), False)
    eq(errors, "B does not imply C", b.get("implies_target_c"), False)

    c = target.get("target_c", {})
    eq(errors, "C id", c.get("id"),
       "C_INDEPENDENT_TRIPLE_COMPONENT_TRUE_INFINITY_ESCAPE")
    eq(errors, "C independence", c.get("independent_of_target_b"), True)
    eq(errors, "C component statement", c.get("statement"),
       "EVERY_CONNECTED_COMPONENT_OF_THE_ACTUAL_TRIPLE_BAD_INTERSECTION_ESCAPES_TO_CERTIFIED_TRUE_PARENT_INFINITY")
    eq(errors, "C cohomology statement", c.get("cohomology_statement"),
       "H_c^0(B_0 intersect B_1 intersect B_2;Q) = 0")
    eq(errors, "C actual compactification",
       c.get("actual_parent_compactification_required"), True)
    eq(errors, "C forbidden substitutes", c.get("forbidden_escape_substitutes"),
       C_FORBIDDEN_ESCAPE)

    completion = target.get("completion_logic", {})
    eq(errors, "A nested in B",
       completion.get("a_is_conditional_prerequisite_inside_b"), True)
    eq(errors, "A-only classification", completion.get("a_alone_classification"),
       "INFORMATIONAL_STOP")
    eq(errors, "B branch", completion.get("b_closes_only"), "diag3_pair_hc1")
    eq(errors, "C branch", completion.get("c_closes_only"), "diag3_triple_hc0")
    eq(errors, "D3 B+C gate", completion.get("d3_requires"),
       ["B_PROVED_AND_REPLAYED", "C_PROVED_AND_REPLAYED"])
    eq(errors, "positive is not proof",
       completion.get("positive_feasibility_is_proof"), False)
    eq(errors, "positive no distance decrease",
       completion.get("positive_feasibility_decreases_proof_distance"), False)
    eq(errors, "diagnostic", target.get("diagnostic"), {
        "id": "ROW2599_CHART_ZERO_FLOW_TRIANGLE",
        "scope": "DIAGNOSTIC_ONLY_NOT_DENOMINATOR_OR_REPRESENTATIVE_REDUCTION",
        "permitted_use": "TEST_LOCAL_PRIMITIVE_CHAIN_AND_FALSIFY_SINGLETON_ONLY_ARCHITECTURES",
    })
    eq(errors, "forbidden credit", target.get("forbidden_credit"),
       FORBIDDEN_CREDIT)
    eq(errors, "feasibility only", target.get("feasibility_only"), True)
    eq(errors, "construction authorization",
       target.get("construction_authorized"), False)
    eq(errors, "construction started", target.get("construction_started"), False)

    facts = document.get("opening_facts", {})
    eq(errors, "taxonomy coverage", get(facts, "joined_clause_taxonomy", "coverage"),
       "3/10")
    eq(errors, "taxonomy not denominator",
       get(facts, "joined_clause_taxonomy", "end_to_end_d3_denominator"), False)
    eq(errors, "canary role", get(facts, "flow_triangle_canary", "role"),
       "DIAGNOSTIC_ONLY")
    eq(errors, "canary not reduction",
       get(facts, "flow_triangle_canary", "is_global_denominator_or_representative_reduction"), False)
    eq(errors, "canary primitive",
       get(facts, "flow_triangle_canary", "primitive_generator"),
       [-1, 1, 1, 1, 1, 1, 1])
    eq(errors, "triple residual", get(facts, "triple_only_accounting", "residual"),
       1162302)
    eq(errors, "triple alone no promotion",
       get(facts, "triple_only_accounting", "promotes_d3_alone"), False)

    proof = document.get("proof_distance", {})
    eq(errors, "opening vector", proof.get("opening_vector"),
       ["2/9", 1, "diag3_pair_hc1_AND_diag3_triple_hc0", 7,
        "UNKNOWN", "UNKNOWN", 5, 8])
    eq(errors, "positive classification",
       proof.get("positive_feasibility_classification"), "INFORMATIONAL")
    eq(errors, "A-only stop", proof.get("a_only_close_action"), "STOP")
    eq(errors, "scoped negative", proof.get("negative_retires_only_named_level"),
       True)
    eq(errors, "pair independent",
       proof.get("pair_branch_remains_independently_load_bearing"), True)
    eq(errors, "taxonomy not measure",
       proof.get("joined_3_of_10_is_end_to_end_measure"), False)

    handoffs = document.get("handoffs", {})
    eq(errors, "handoff labels", handoffs.get("allowed_labels"),
       ["POSITIVE", "NEGATIVE", "NULL", "TIMEOUT"])
    eq(errors, "one label", handoffs.get("exactly_one_label_per_lane"), True)
    eq(errors, "ABC status", handoffs.get("abc_program_status_vector_required"),
       True)
    positive = handoffs.get("positive", {})
    for requirement in (
        "COMPLETE_FINITE_DEPENDENCY_CLOSED_PROOF_PROGRAM_FROM_A_INTO_B",
        "SEPARATE_COMPLETE_FINITE_DEPENDENCY_CLOSED_PROOF_PROGRAM_FOR_C",
        "B_PROGRAM_INCLUDES_L_SOURCE_CONSTRUCTION_ALL_TEN_SHAPES_COMPARISON_AND_PAIR_KERNEL",
        "C_PROGRAM_INDEPENDENTLY_REACHES_ACTUAL_TRUE_PARENT_INFINITY",
    ):
        if requirement not in positive.get("requires", []):
            errors.append(f"positive missing {requirement}")
    eq(errors, "positive not proof", positive.get("is_a_theorem_proof"), False)
    eq(errors, "positive proves nothing", positive.get("proves_a_b_c_d3_or_9dvl"),
       False)
    eq(errors, "A-only not positive", positive.get("a_only_is_positive"), False)
    eq(errors, "A-only positive disposition",
       positive.get("a_only_classification_and_action"), "INFORMATIONAL_STOP")
    negative = handoffs.get("negative", {})
    eq(errors, "ansatz not universal",
       negative.get("one_ansatz_failure_is_sufficient"), False)
    eq(errors, "negative is scoped",
       negative.get("negative_at_one_level_refutes_other_levels_or_d3"), False)
    if "RETIREMENT_SCOPED_ONLY_TO_NAMED_LEVEL_AND_FORMULATION" not in negative.get("requires", []):
        errors.append("negative retirement scope missing")
    eq(errors, "local null",
       get(handoffs, "null", "local_only_chain_classification"), "NULL")
    eq(errors, "timeout no relabel",
       get(handoffs, "timeout", "incomplete_work_may_be_relabelled_positive"), False)

    roles = document.get("roles", [])
    eq(errors, "role ids", [role.get("id") for role in roles], [
        "TOPOLOGY_CONSTRUCTION", "OBSTRUCTION_FALSIFIER",
        "SEMIALGEBRAIC_NATURALITY", "REFEREE",
    ] if isinstance(roles, list) else [])
    if isinstance(roles, list) and len(roles) == 4:
        eq(errors, "roles independent", [role.get("independent") for role in roles],
           [True, True, True, True])
        eq(errors, "topology acyclic map",
           roles[0].get("maps_a_into_b_prerequisites_without_assuming_b"), True)
        eq(errors, "topology no rank",
           roles[0].get("may_assert_global_rank_pair_kernel_or_triple_escape"), False)
        eq(errors, "falsifier scoped",
           roles[1].get("must_scope_retirement_to_named_level"), True)
        eq(errors, "naturality no A-to-C conflation",
           roles[2].get("a_true_boundary_bookkeeping_proves_c_escape"), False)
        eq(errors, "naturality rank distinction",
           roles[2].get("must_distinguish_parent_and_witness_rank_drop"), True)
        eq(errors, "referee positive semantics",
           roles[3].get("positive_means_complete_finite_proof_program_not_proof"), True)
        eq(errors, "referee ABC statuses",
           roles[3].get("separate_a_b_c_program_statuses_required"), True)
        eq(errors, "referee no producer imports",
           roles[3].get("producer_acceptance_import_allowed"), False)

    ceiling = document.get("deliverable_ceiling", {})
    eq(errors, "timebox unit", ceiling.get("timebox_unit"), "HANDOFF_ROUNDS")
    eq(errors, "one initial round",
       ceiling.get("initial_handoff_rounds_per_discovery_lane"), 1)
    eq(errors, "one revision",
       ceiling.get("maximum_referee_directed_revision_rounds_per_discovery_lane"), 1)
    eq(errors, "no third pass", ceiling.get("third_research_pass_allowed"), False)
    eq(errors, "nine proof obligations",
       ceiling.get("topology_max_named_proof_obligations"), 9)
    for field in (
        "new_atlas_allowed", "global_census_allowed", "broad_sampling_allowed",
        "unbounded_search_allowed", "network_or_external_solver_allowed",
        "paid_or_external_compute_allowed", "ceiling_extendable",
    ):
        eq(errors, f"ceiling {field}", ceiling.get(field), False)

    midpoint = document.get("midpoint", {})
    midpoint_requirements = midpoint.get("continue_iff", [])
    for requirement in (
        "A_B_AND_C_EACH_HAVE_FINITE_DEPENDENCY_LIST_WITH_NO_UNNAMED_CLASSIFICATION_OR_CENSUS",
        "A_HAS_ACYCLIC_L_SOURCE_INTERFACE_PROPER_ANTICHAIN_R1_TO_3_PERMUTATION_SIMULTANEOUS_SUBDIVISION_AND_ARBITRARY_CHAIN_COHERENCE_WITH_NO_RANK_CLAIM",
        "B_HAS_FINITE_OBLIGATIONS_FOR_L_SOURCE_ALL_LABELED_TEN_SHAPES_SOURCE_PROVENANCE_COMPARISON_AND_PAIR_KERNEL",
        "C_HAS_SEPARATE_ROUTE_FROM_ACTUAL_TRIPLE_COMPONENTS_TO_CERTIFIED_TRUE_PARENT_INFINITY_NOT_A_OR_B_BOOKKEEPING",
    ):
        if requirement not in midpoint_requirements:
            errors.append(f"midpoint missing {requirement}")
    eq(errors, "midpoint A-only stop", midpoint.get("a_only_action"),
       "INFORMATIONAL_STOP")
    eq(errors, "midpoint positive not progress",
       midpoint.get("positive_program_is_theorem_progress"), False)
    eq(errors, "stop rules", document.get("stop_rules"), STOP_RULES)

    authority = document.get("authority", {})
    for field in (
        "canonical_theorem_files_writable", "theorem_ledger_writable",
        "canonical_state_writable", "theorem_promotion_allowed",
        "positive_feasibility_is_theorem_proof",
        "positive_handoff_proves_d3_or_9dvl", "connector_use_allowed",
        "network_use_allowed", "external_mutation_allowed",
    ):
        eq(errors, f"authority {field}", authority.get(field), False)
    eq(errors, "required closing ledger", authority.get("closing_ledger_required"),
       "2/9")
    eq(errors, "required delta", authority.get("ledger_delta_required"), "0/9")
    eq(errors, "authority A-only stop",
       authority.get("a_only_classification_and_action"), "INFORMATIONAL_STOP")
    eq(errors, "authority B+C gate",
       authority.get("d3_closure_requires_proved_replayed_b_and_c"), True)

    eq(errors, "charter declaration", document.get("charter"), {
        "path": CHARTER_PATH, "sha256": CHARTER_SHA256,
    })
    eq(errors, "source pins", document.get("source_pins"), PIN_OBJECTS)

    if external:
        try:
            eq(errors, "base commit object", git("rev-parse", BASE_COMMIT),
               BASE_COMMIT)
            eq(errors, "base tree object",
               git("rev-parse", f"{BASE_COMMIT}^{{tree}}"), BASE_TREE)
        except (OSError, RuntimeError) as exc:
            errors.append(f"git verification: {exc}")
        charter = REPO / CHARTER_PATH
        if not charter.is_file():
            errors.append("charter missing")
        else:
            eq(errors, "charter hash", sha256(charter), CHARTER_SHA256)
            text = charter.read_text(encoding="utf-8")
            fragments = [
                "### Target A: universal mixed chain and specialization theorem",
                "conditional on a declared lower-skeleton/source interface",
                "may not assume that the complete complex",
                "### Target B: complete source-derived joined comparison theorem",
                "every labeled instance with `1 <= r <= 3`",
                "all ten joined",
                "filtration-preserving comparison",
                "rational pair-kernel",
                "### Target C: independent triple-component escape theorem",
                "triple-bad intersection escapes to genuine true parent infinity",
                "Only independently accepted B and C together can close D3",
                "row-2599 chart-zero flow triangle is diagnostic only",
                "proper antichain",
                "simultaneous",
                "arbitrary composable face chain",
                "Parent-matrix rank drop",
                "complete finite proof-program, not a theorem proof",
                "A alone is `INFORMATIONAL / STOP`",
                "uncompared partial complex",
            ]
            for fragment in fragments:
                if fragment not in text:
                    errors.append(f"charter missing fragment: {fragment}")
        for source_path, expected_bytes, expected_sha in SOURCE_PINS:
            path = REPO / source_path
            if not path.is_file():
                errors.append(f"source missing: {source_path}")
                continue
            eq(errors, f"source bytes {source_path}", path.stat().st_size,
               expected_bytes)
            eq(errors, f"source hash {source_path}", sha256(path), expected_sha)
        close_path = REPO / SOURCE_PINS[1][0]
        if close_path.is_file():
            try:
                close = json.loads(close_path.read_text(encoding="utf-8"))
                result = close.get("result", {})
                eq(errors, "predecessor ledger", result.get("closing_ledger"),
                   "2/9")
                eq(errors, "predecessor action", result.get("strategy_action"),
                   "STOP")
                eq(errors, "predecessor successor", result.get("selected_successor"),
                   "NONE")
            except (OSError, json.JSONDecodeError) as exc:
                errors.append(f"predecessor parse: {exc}")
    return errors


def set_path(path: tuple[Any, ...], value: Any) -> Callable[[dict[str, Any]], None]:
    def mutation(document: dict[str, Any]) -> None:
        cursor: Any = document
        for key in path[:-1]:
            cursor = cursor[key]
        cursor[path[-1]] = value
    return mutation


def pop_path(path: tuple[Any, ...], index: int = -1) -> Callable[[dict[str, Any]], None]:
    def mutation(document: dict[str, Any]) -> None:
        cursor: Any = document
        for key in path:
            cursor = cursor[key]
        cursor.pop(index)
    return mutation


HOSTILES: list[tuple[str, Callable[[dict[str, Any]], None]]] = [
    ("base drift", set_path(("canonical_base", "commit"), "0" * 40)),
    ("ledger promotion", set_path(("canonical_opening", "ledger"), "3/9")),
    ("construction route", set_path(("strategy_evaluation", "construction_ready"), True)),
    ("wrong route", set_path(("selected_target", "id"), "A_ONLY")),
    ("improper signatures", set_path(("selected_target", "domain", "signature_families"), "ANY")),
    ("r equals three only", set_path(("selected_target", "domain", "active_block_range"), [3, 3])),
    ("unlabeled quotient", set_path(("selected_target", "domain", "shape_quotient"), "ANONYMOUS")),
    ("separate subdivision", set_path(("selected_target", "domain", "subdivision"), "PER_BLOCK")),
    ("codimension one only", set_path(("selected_target", "domain", "coherence"), "SQUARES_ONLY")),
    ("rank drops conflated", set_path(("selected_target", "domain", "rank_drop_policy"), "CONFLATED")),
    ("A assumes B", set_path(("selected_target", "target_a", "interface_hypotheses_may_assume_complete_b"), True)),
    ("B need not construct interface", set_path(("selected_target", "target_a", "b_must_construct_and_verify_interface_from_sources"), False)),
    ("A loses simultaneous", pop_path(("selected_target", "target_a", "required_program_obligations"), 4)),
    ("A loses arbitrary chain", pop_path(("selected_target", "target_a", "required_program_obligations"), 5)),
    ("A gains rank claim", pop_path(("selected_target", "target_a", "forbidden_consequences"), 0)),
    ("A gains escape claim", pop_path(("selected_target", "target_a", "forbidden_consequences"), 2)),
    ("B invokes A circularly", set_path(("selected_target", "target_b", "constructs_and_verifies_l_source_before_invoking_a"), False)),
    ("B wrong r range", set_path(("selected_target", "target_b", "active_block_range"), [2, 3])),
    ("B drops a shape", pop_path(("selected_target", "target_b", "ten_shapes_modulo_permutation"), 6)),
    ("B not all labeled", set_path(("selected_target", "target_b", "all_labeled_instances_required"), False)),
    ("B forgets missing type", pop_path(("selected_target", "target_b", "still_missing_shapes"), 3)),
    ("B drops comparison", pop_path(("selected_target", "target_b", "required_program_obligations"), 4)),
    ("B drops kernel", pop_path(("selected_target", "target_b", "required_program_obligations"), 5)),
    ("A implies B", set_path(("selected_target", "target_b", "implied_by_a_alone"), True)),
    ("B implies C", set_path(("selected_target", "target_b", "implies_target_c"), True)),
    ("C depends on B", set_path(("selected_target", "target_c", "independent_of_target_b"), False)),
    ("C not actual parent", set_path(("selected_target", "target_c", "actual_parent_compactification_required"), False)),
    ("witness loss becomes infinity", pop_path(("selected_target", "target_c", "forbidden_escape_substitutes"), 0)),
    ("A boundary proves C", pop_path(("selected_target", "target_c", "forbidden_escape_substitutes"), 4)),
    ("B quotient proves C", pop_path(("selected_target", "target_c", "forbidden_escape_substitutes"), 5)),
    ("A-only continuation", set_path(("selected_target", "completion_logic", "a_alone_classification"), "CONTINUE")),
    ("D3 needs B only", pop_path(("selected_target", "completion_logic", "d3_requires"), 1)),
    ("positive is proof", set_path(("selected_target", "completion_logic", "positive_feasibility_is_proof"), True)),
    ("positive decreases", set_path(("selected_target", "completion_logic", "positive_feasibility_decreases_proof_distance"), True)),
    ("row2599 global", set_path(("selected_target", "diagnostic", "scope"), "GLOBAL_DENOMINATOR")),
    ("allow separate subdivisions", pop_path(("selected_target", "forbidden_credit"), 3)),
    ("canary becomes reduction", set_path(("opening_facts", "flow_triangle_canary", "is_global_denominator_or_representative_reduction"), True)),
    ("positive convergence", set_path(("proof_distance", "positive_feasibility_classification"), "CONVERGING")),
    ("A continues", set_path(("proof_distance", "a_only_close_action"), "CONTINUE")),
    ("negative broad retirement", set_path(("proof_distance", "negative_retires_only_named_level"), False)),
    ("no ABC status", set_path(("handoffs", "abc_program_status_vector_required"), False)),
    ("positive lacks C program", pop_path(("handoffs", "positive", "requires"), 1)),
    ("positive calls itself proof", set_path(("handoffs", "positive", "is_a_theorem_proof"), True)),
    ("A-only positive", set_path(("handoffs", "positive", "a_only_is_positive"), True)),
    ("negative unscoped", pop_path(("handoffs", "negative", "requires"), 3)),
    ("negative refutes D3", set_path(("handoffs", "negative", "negative_at_one_level_refutes_other_levels_or_d3"), True)),
    ("topology assumes rank", set_path(("roles", 0, "may_assert_global_rank_pair_kernel_or_triple_escape"), True)),
    ("topology cyclic", set_path(("roles", 0, "maps_a_into_b_prerequisites_without_assuming_b"), False)),
    ("falsifier broad retirement", set_path(("roles", 1, "must_scope_retirement_to_named_level"), False)),
    ("naturality conflates C", set_path(("roles", 2, "a_true_boundary_bookkeeping_proves_c_escape"), True)),
    ("naturality conflates rank", set_path(("roles", 2, "must_distinguish_parent_and_witness_rank_drop"), False)),
    ("referee positive theorem", set_path(("roles", 3, "positive_means_complete_finite_proof_program_not_proof"), False)),
    ("third pass", set_path(("deliverable_ceiling", "third_research_pass_allowed"), True)),
    ("census", set_path(("deliverable_ceiling", "global_census_allowed"), True)),
    ("external solver", set_path(("deliverable_ceiling", "network_or_external_solver_allowed"), True)),
    ("midpoint omits C", pop_path(("midpoint", "continue_iff"), 3)),
    ("midpoint A continues", set_path(("midpoint", "a_only_action"), "CONTINUE")),
    ("positive called progress", set_path(("midpoint", "positive_program_is_theorem_progress"), True)),
    ("drop partial-complex stop", pop_path(("stop_rules",), 9)),
    ("canonical writes", set_path(("authority", "canonical_state_writable"), True)),
    ("authority calls proof", set_path(("authority", "positive_feasibility_is_theorem_proof"), True)),
    ("authority drops C", set_path(("authority", "d3_closure_requires_proved_replayed_b_and_c"), False)),
    ("charter drift", set_path(("charter", "sha256"), "f" * 64)),
    ("source drift", set_path(("source_pins", 0, "sha256"), "e" * 64)),
    ("unknown field", lambda d: d.__setitem__("construction", {})),
]


def run_hostiles(pristine: dict[str, Any]) -> None:
    escaped: list[str] = []
    for label, mutation in HOSTILES:
        hostile = copy.deepcopy(pristine)
        mutation(hostile)
        if not validate(hostile, external=False):
            escaped.append(label)
    if escaped:
        raise AssertionError("hostile mutations accepted: " + ", ".join(escaped))
    print(f"PASS hostile mutations rejected {len(HOSTILES)}/{len(HOSTILES)}")


def main() -> int:
    try:
        raw = STATE_PATH.read_bytes()
        document = json.loads(raw.decode("utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        print(f"FAIL opening state load: {exc}", file=sys.stderr)
        return 1
    if hashlib.sha256(raw).hexdigest() != STATE_SHA256:
        print("FAIL OPENING_STATE.json byte seal changed", file=sys.stderr)
        return 1
    errors = validate(document, external=True)
    if errors:
        for error in errors:
            print(f"FAIL {error}", file=sys.stderr)
        return 1
    try:
        run_hostiles(document)
    except AssertionError as exc:
        print(f"FAIL {exc}", file=sys.stderr)
        return 1
    print(f"PASS immutable base {BASE_COMMIT} / {BASE_TREE}")
    print("PASS nested A -> B and independent C feasibility contract")
    print("PASS A has no rank claim; only proved B+C can close D3")
    print("PASS proper antichains, 1<=r<=3 modulo permutations, simultaneous subdivision")
    print("PASS arbitrary face-chain coherence and parent/witness rank-drop distinction")
    print("PASS positive is a finite proof-program, not a proof; A-only is INFORMATIONAL/STOP")
    print(f"PASS source pins {len(SOURCE_PINS)}/{len(SOURCE_PINS)}")
    print("PASS opening state")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
