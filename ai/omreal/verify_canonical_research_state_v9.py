#!/usr/bin/env python3
"""Independently verify the fail-closed post-feasibility 9DVL state."""

from __future__ import annotations

from copy import deepcopy
from hashlib import sha256
import json
from pathlib import Path
import re
import subprocess


ROOT = Path(__file__).resolve().parents[2]
STATE_PATH = ROOT / "ai/omreal/data/CANONICAL_RESEARCH_STATE_V9.json"

CLOSE = "c06884abf64ab761e1430012653e4d851da3a0f3"
CLOSE_TREE = "6cb091f3cc7a7dd32d801dce662aa610b49af41f"
REFEREE = "4f72cf633eba01d50c0fa806da79bb7a2f19a2f8"
REFEREE_TREE = "e527e6d8483e6a38b2f274fe11913989d7164d2b"
BRANCH = "research/local-9dvl-post-mixed-carrier-stop-v9-20260901"
PROGRAM = "D3_NESTED_A_B_C_THEOREM_FEASIBILITY_ROUND1"
STATE_DIGEST = "4a17caa5f648b2fff0cd77467dab1f3c761e2770f7b539bbc57ac634baf58d67"

OPENING_VECTOR = [
    "2/9", 1, "diag3_pair_hc1_AND_diag3_triple_hc0", 7,
    "UNKNOWN", "UNKNOWN", 5, 8,
]
CLOSING_VECTOR = [
    "2/9", 1, "diag3_pair_hc1_AND_diag3_triple_hc0", 7,
    "UNKNOWN", "UNKNOWN", 6, 9,
]
OBLIGATION_IDS = [
    "global_gluing",
    "extension_labels",
    "strict_closure",
    "relative_infinity",
    "middle_rank_replay",
    "diag3_pair_hc1",
    "diag3_triple_hc0",
]
OBLIGATION_ROWS = [
    {"id": "global_gluing", "status": "INCONCLUSIVE", "delta": "UNCHANGED", "requires": []},
    {"id": "extension_labels", "status": "INCONCLUSIVE", "delta": "UNCHANGED", "requires": ["global_gluing"]},
    {"id": "strict_closure", "status": "INCONCLUSIVE", "delta": "UNCHANGED", "requires": ["global_gluing", "extension_labels"]},
    {"id": "relative_infinity", "status": "INCONCLUSIVE", "delta": "UNCHANGED", "requires": ["strict_closure"]},
    {"id": "middle_rank_replay", "status": "INCONCLUSIVE", "delta": "UNCHANGED", "requires": ["strict_closure", "relative_infinity"]},
    {"id": "diag3_pair_hc1", "status": "INCONCLUSIVE", "delta": "UNCHANGED", "requires": ["middle_rank_replay"]},
    {"id": "diag3_triple_hc0", "status": "INCONCLUSIVE", "delta": "UNCHANGED", "residual_source_orbits": 1_162_302, "requires": ["triple_source_denominator"]},
]
FIRST_MISSING = {
    "A": "UNIVERSAL_GENUINELY_MIXED_CHAIN_ASSIGNMENT_ON_ONE_SIMULTANEOUS_SOURCE_SUBDIVISION_WITH_ARBITRARY_FACE_CHAIN_COHERENCE",
    "B": "FINITE_EXHAUSTIVE_L_SOURCE_AND_FILTRATION_PRESERVING_COMPARISON_TO_THE_ACTUAL_COMPACTIFIED_BAD_UNION",
    "C": "COMPLETE_STABLE_COMPONENT_IDENTITIES_AND_SOUND_CONTINUATIONS_TO_CERTIFIED_TRUE_PARENT_INFINITY",
}
REOPEN_REQUIRES = [
    "NEW_EXPLICIT_USER_AUTHORITY",
    "NEW_GOVERNED_CYCLE",
    "CONCRETE_FINITE_ROUTE_FOR_ONE_FIRST_MISSING_GLOBAL_EDGE",
    "PREDECLARED_THEOREM_LEVEL_STRICT_DECREASE",
    "FRESH_CANONICAL_OPENING_AUDIT_AND_INDEPENDENT_REPLAY",
]
PROHIBITED = [
    "REPEAT_D3_NESTED_A_B_C_THEOREM_FEASIBILITY_ROUND1",
    "LOCAL_MIXED_CARRIER_OR_CHART_REFINEMENT",
    "TRIPLE_ATLAS_GROWTH_WITHOUT_COMPONENT_COMPLETE_GLOBAL_ATTACHMENT",
    "FACTOR19069_OR_RESIDUAL_SAMPLING",
    "LEDGER_PROMOTION_FROM_FEASIBILITY_OR_LOCAL_EVIDENCE",
]
SOURCE_PINS = {
    "ai/omreal/data/CANONICAL_RESEARCH_STATE_V8.json": "e356d00108e46be82937b18146ca47039d506ea378d489dc392d7a2ee3f865e4",
    "ops/research-team/cycles/2026-09-01-d3-mixed-carrier-theorem-feasibility-gate1/CLOSING_MANIFEST.json": "e321eb89397c1549a39d2e3b757014bdd2d283fe098ee3ded23c57078a872f48",
    "ops/research-team/cycles/2026-09-01-d3-mixed-carrier-theorem-feasibility-gate1/CLOSING_CANDIDATE.json": "135328356b754f97ae631bee441ae8d3c0be5ddbd0ab427bfaac344244da94fc",
    "ops/research-team/cycles/2026-09-01-d3-mixed-carrier-theorem-feasibility-gate1/CYCLE_REPORT.md": "1ecd782da68eb7a5e3a41052b916726aabed815e1dc50822d98d1f35078fc6e4",
    "ops/team/d3-mixed-carrier-topology/RESULT.json": "7e54007c1bb97be457cbdc039c5520267cd39e39e08a930828b42708443a99e5",
    "ops/team/d3-mixed-carrier-topology/THEOREM_MEMO.md": "131ec929171abf633b18e4eefbd1b45ec8aeea97b9d2d1a6f89a73cb205b7f76",
    "ops/team/d3-mixed-carrier-falsifier/RESULT.json": "89f54c80234dd74f763b390a1da86de2359a99684e3920e57cec284e6fd08480",
    "ops/team/d3-mixed-carrier-falsifier/OBSTRUCTION_DOSSIER.md": "de7e1d5c2758786852cbb1cf684f3af8cbf44ab4df124c7053b60534b1317936",
    "ops/team/d3-mixed-carrier-naturality/RESULT.json": "2911e7478a31090582dda2aeeb5e952ab84cf83946bcd5f29d3900813309e3e0",
    "ops/team/d3-mixed-carrier-naturality/NATURALITY_MEMO.md": "a24821526bd0e89a1473e887d60c6e38c9e28f8d65c6a86e7f5e0d3a5d2cdb86",
    "ops/team/d3-mixed-carrier-referee/RESULT.json": "b30b46c8a01eaf393c881c3de9a1550536d5f0daa4c6d3c649fcdedc249b5fe5",
    "ops/team/d3-mixed-carrier-referee/REVIEW.md": "fa2d5894954c17c4c2edab93b991f7ee93f3c2680dcbdedea259daf711adb0ea",
    "ops/team/d3-mixed-carrier-referee/verify_referee.py": "f4367e95184b9722a821aeea44281e9b365831b35e32a7dad2bdbcaf8e23b0a6",
}
EXPECTED_STATE_HOSTILES = 59
EXPECTED_AUTHORITY_HOSTILES = 7


class AuditError(RuntimeError):
    pass


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AuditError(message)


def canonical_digest(value: object) -> str:
    payload = json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    return sha256(payload).hexdigest()


def reject_duplicate_keys(pairs: list[tuple[str, object]]) -> dict:
    result: dict = {}
    for key, value in pairs:
        require(key not in result, f"duplicate JSON key: {key}")
        result[key] = value
    return result


def parse_json(payload: str | bytes) -> dict:
    return json.loads(payload, object_pairs_hook=reject_duplicate_keys)


def load_json(path: Path) -> dict:
    return parse_json(path.read_text(encoding="utf-8"))


def git_text(*args: str) -> str:
    proc = subprocess.run(
        ["git", *args], cwd=ROOT, check=True, stdout=subprocess.PIPE,
        stderr=subprocess.PIPE, text=True,
    )
    return proc.stdout.strip()


def frozen(path: str) -> bytes:
    proc = subprocess.run(
        ["git", "show", f"{CLOSE}:{path}"], cwd=ROOT, check=True,
        stdout=subprocess.PIPE, stderr=subprocess.PIPE,
    )
    return proc.stdout


def frozen_json(path: str) -> dict:
    return parse_json(frozen(path))


def exact_keys(value: dict, expected: set[str], message: str) -> None:
    require(set(value) == expected, message)


def require_typed_equal(actual: object, expected: object, message: str) -> None:
    require(type(actual) is type(expected) and actual == expected, message)


def require_typed_vector(actual: list, expected: list, message: str) -> None:
    require(len(actual) == len(expected), message)
    for index, (left, right) in enumerate(zip(actual, expected)):
        require_typed_equal(left, right, f"{message} element {index}")


def validate_semantics(candidate: dict) -> None:
    exact_keys(candidate, {
        "format", "status", "as_of", "repository", "predecessor",
        "authoritative_cycle", "theorem", "proof_distance",
        "open_obligations", "completed_feasibility_program",
        "selected_next_target", "process_gates", "source_pins",
    }, "top-level keys")
    require(candidate["format"] == "9dvl-canonical-research-state-v9", "format")
    require(candidate["status"] == "STOPPED", "status")
    require(candidate["as_of"] == "2026-09-01", "date")

    repository = candidate["repository"]
    exact_keys(repository, {
        "full_name", "branch", "evidence_close_branch",
        "canonical_evidence_close_commit", "canonical_evidence_close_tree",
        "integrated_referee_commit", "integrated_referee_tree",
        "github_mode", "github_write", "drive_connector_used", "network_used",
    }, "repository keys")
    require(repository["full_name"] == "reuellee/finite-certificates", "repository")
    require(repository["branch"] == BRANCH, "branch")
    require(repository["evidence_close_branch"] == "research/local-d3-mixed-carrier-theorem-feasibility-gate1-20260901", "evidence branch")
    require(repository["canonical_evidence_close_commit"] == CLOSE, "close commit")
    require(repository["canonical_evidence_close_tree"] == CLOSE_TREE, "close tree")
    require(repository["integrated_referee_commit"] == REFEREE, "referee commit")
    require(repository["integrated_referee_tree"] == REFEREE_TREE, "referee tree")
    require(repository["github_mode"] == "READ_ONLY_UNTIL_NEW_EXPLICIT_USER_INSTRUCTION", "GitHub mode")
    require(repository["github_write"] is False, "GitHub write")
    require(repository["drive_connector_used"] is False, "Drive connector")
    require(repository["network_used"] is False, "network")

    predecessor = candidate["predecessor"]
    exact_keys(predecessor, {
        "path", "sha256", "policy", "v8_one_round_authorization",
        "v8_target_activation_disposition",
    }, "predecessor keys")
    require(predecessor["path"] == "ai/omreal/data/CANONICAL_RESEARCH_STATE_V8.json", "predecessor path")
    require(predecessor["sha256"] == SOURCE_PINS[predecessor["path"]], "predecessor pin")
    require(predecessor["policy"] == "IMMUTABLE_PRE_MIXED_CARRIER_CLOSE_CANONICAL_STATE", "predecessor policy")
    require(predecessor["v8_one_round_authorization"] == "CONSUMED_BY_AUTHORITATIVE_CYCLE_CLOSE", "V8 authorization")
    require(predecessor["v8_target_activation_disposition"] == "DEACTIVATED_AFTER_NULL_STOP_NONE_CLOSE_TARGETS_REMAIN_MATHEMATICALLY_OPEN", "V8 target disposition")

    cycle = candidate["authoritative_cycle"]
    exact_keys(cycle, {
        "id", "opening_commit", "opening_tree", "closing_commit",
        "closing_tree", "referee_commit", "referee_tree",
        "referee_verdict", "discovery_handoffs", "referee_handoff",
        "cycle_handoff", "trajectory", "strategy_action",
        "selected_successor", "construction_started",
    }, "cycle keys")
    require(cycle["id"] == "2026-09-01-d3-mixed-carrier-theorem-feasibility-gate1", "cycle id")
    require(cycle["opening_commit"] == "dd86907bebbfaaac9caee4e1d93dc77bc9f3ad8b", "cycle opening commit")
    require(cycle["opening_tree"] == "a59d740c008ae04accf200a8373d16b4d9c70ae4", "cycle opening tree")
    require(cycle["closing_commit"] == CLOSE and cycle["closing_tree"] == CLOSE_TREE, "cycle close")
    require(cycle["referee_commit"] == REFEREE and cycle["referee_tree"] == REFEREE_TREE, "cycle referee")
    require(cycle["referee_verdict"] == "ACCEPT_FROZEN_CANDIDATE_FAIL_CLOSED", "referee verdict")
    require(cycle["discovery_handoffs"] == {"topology": "NULL", "falsifier": "NULL", "naturality": "NULL"}, "discovery handoffs")
    require(cycle["referee_handoff"] == cycle["cycle_handoff"] == "NULL", "closing handoffs")
    require(cycle["trajectory"] == "STALLED" and cycle["strategy_action"] == "STOP", "trajectory")
    require(cycle["selected_successor"] == "NONE" and cycle["construction_started"] is False, "successor")

    theorem = candidate["theorem"]
    exact_keys(theorem, {
        "id", "score", "proved_diagonals", "diagonal_three",
        "diagonal_nine", "promotion", "theorem_level_counterexample",
    }, "theorem keys")
    require(theorem["id"] == "9DVL" and theorem["score"] == "2/9", "theorem ledger")
    require(theorem["proved_diagonals"] == [1, 2], "proved diagonals")
    require(all(type(value) is int for value in theorem["proved_diagonals"]), "proved diagonal types")
    require(theorem["diagonal_three"] == theorem["diagonal_nine"] == "OPEN", "open diagonals")
    require(theorem["promotion"] == "NONE", "theorem promotion")
    require(theorem["theorem_level_counterexample"] == "NOT_FOUND", "counterexample scope")

    distance = candidate["proof_distance"]
    exact_keys(distance, {
        "opening_vector", "checkpoint_vector", "closing_vector", "delta",
        "minimum_acceptable_decrease_met", "same_blocker_streak_closing",
        "zero_ledger_streak_closing",
    }, "proof-distance keys")
    require_typed_vector(distance["opening_vector"], OPENING_VECTOR, "opening vector")
    require_typed_vector(distance["checkpoint_vector"], OPENING_VECTOR, "checkpoint vector")
    require_typed_vector(distance["closing_vector"], CLOSING_VECTOR, "closing vector")
    require_typed_equal(distance["delta"], 0, "proof-distance delta")
    require(distance["minimum_acceptable_decrease_met"] is False, "minimum decrease")
    require_typed_equal(distance["same_blocker_streak_closing"], 6, "same-blocker streak")
    require_typed_equal(distance["zero_ledger_streak_closing"], 9, "zero-ledger streak")

    obligations = candidate["open_obligations"]
    exact_keys(obligations, {
        "load_bearing_count", "pair_residual", "pair_coverage",
        "triple_source_total", "triple_source_settled",
        "triple_source_residual", "triple_source_is_component_denominator",
        "items",
    }, "obligation keys")
    require_typed_equal(obligations["load_bearing_count"], 7, "obligation count")
    require(obligations["pair_residual"] == obligations["pair_coverage"] == "UNKNOWN", "pair frontier")
    require_typed_equal(obligations["triple_source_total"], 79_102_449, "triple total")
    require_typed_equal(obligations["triple_source_settled"], 77_940_147, "triple settled")
    require_typed_equal(obligations["triple_source_residual"], 1_162_302, "triple residual")
    require(obligations["triple_source_is_component_denominator"] is False, "triple component denominator")
    require(obligations["items"] == OBLIGATION_ROWS, "obligation rows")
    require_typed_equal(obligations["items"][-1]["residual_source_orbits"], 1_162_302, "obligation residual")
    for index, row in enumerate(obligations["items"]):
        expected = {"id", "status", "delta", "requires"}
        if index == len(obligations["items"]) - 1:
            expected.add("residual_source_orbits")
        exact_keys(row, expected, f"obligation item {index} keys")

    program = candidate["completed_feasibility_program"]
    exact_keys(program, {
        "id", "authorization_status", "rounds_authorized",
        "rounds_completed", "overall_handoff",
        "positive_finite_program_found", "universal_negative_found",
        "targets", "dependency_logic", "nonconsequences",
    }, "program keys")
    require(program["id"] == PROGRAM, "program id")
    require(program["authorization_status"] == "CONSUMED", "program authorization")
    require_typed_equal(program["rounds_authorized"], 1, "authorized round count")
    require_typed_equal(program["rounds_completed"], 1, "completed round count")
    require(program["overall_handoff"] == "NULL", "program handoff")
    require(program["positive_finite_program_found"] is False, "positive program scope")
    require(program["universal_negative_found"] is False, "negative program scope")
    require(set(program["targets"]) == {"A", "B", "C"}, "target set")
    exact_keys(program["targets"]["A"], {
        "status", "complete_finite_program", "theorem_proved_or_refuted",
        "first_missing",
    }, "target A keys")
    exact_keys(program["targets"]["B"], {
        "status", "complete_finite_program", "theorem_proved_or_refuted",
        "rational_pair_kernel_proved", "first_missing",
    }, "target B keys")
    exact_keys(program["targets"]["C"], {
        "status", "complete_finite_program", "theorem_proved_or_refuted",
        "triple_escape_proved", "first_missing",
    }, "target C keys")
    for name, target in program["targets"].items():
        require(target["status"] == "NULL", f"target {name} status")
        require(target["complete_finite_program"] is False, f"target {name} program")
        require(target["theorem_proved_or_refuted"] is False, f"target {name} theorem scope")
        require(target["first_missing"] == FIRST_MISSING[name], f"target {name} first missing")
    require(program["targets"]["B"]["rational_pair_kernel_proved"] is False, "pair kernel")
    require(program["targets"]["C"]["triple_escape_proved"] is False, "triple escape")
    logic = program["dependency_logic"]
    exact_keys(logic, {
        "target_a_is_conditional_subproblem_inside_target_b",
        "target_a_alone_proves_no_global_pair_rank",
        "target_c_is_independent_of_targets_a_and_b",
        "only_actual_proved_and_replayed_b_plus_c_can_close_d3",
        "feasibility_handoffs_have_theorem_credit",
    }, "dependency-logic keys")
    require(logic["target_a_is_conditional_subproblem_inside_target_b"] is True, "A/B nesting")
    require(logic["target_a_alone_proves_no_global_pair_rank"] is True, "A nonconsequence")
    require(logic["target_c_is_independent_of_targets_a_and_b"] is True, "C independence")
    require(logic["only_actual_proved_and_replayed_b_plus_c_can_close_d3"] is True, "B plus C gate")
    require(logic["feasibility_handoffs_have_theorem_credit"] is False, "feasibility credit")
    require(program["nonconsequences"] == [
        "NO_PROOF_OR_REFUTATION_OF_A_B_C_D3_OR_9DVL",
        "NO_COMPLETE_FINITE_PROOF_PROGRAM",
        "NO_PAIR_OR_TRIPLE_OBLIGATION_CLOSED",
        "NO_LEDGER_CHANGE",
        "NO_CONSTRUCTION",
        "NO_SUCCESSOR_AUTHORIZATION",
        "NO_THEOREM_PROMOTION",
    ], "nonconsequences")

    selected = candidate["selected_next_target"]
    exact_keys(selected, {
        "id", "eligible_successor_count", "strategy_action",
        "construction_authorized", "automatic_reopening_authorized",
        "reason", "reopen_requires", "prohibited_automatic_continuations",
    }, "selected-target keys")
    require(selected["id"] == "NONE", "selected target")
    require_typed_equal(selected["eligible_successor_count"], 0, "eligible successor count")
    require(selected["strategy_action"] == "STOP", "next strategy")
    require(selected["construction_authorized"] is False, "construction authorization")
    require(selected["automatic_reopening_authorized"] is False, "automatic reopening")
    require(selected["reason"] == "THE_ONLY_V8_FEASIBILITY_ROUND_CLOSED_NULL_STALLED_WITHOUT_PROOF_DISTANCE_DECREASE_OR_FULL_SCOPE_NEGATIVE", "selection reason")
    require(selected["reopen_requires"] == REOPEN_REQUIRES, "reopen contract")
    require(selected["prohibited_automatic_continuations"] == PROHIBITED, "prohibited continuations")

    gates = candidate["process_gates"]
    exact_keys(gates, {
        "v9_is_current_target_selector", "v8_is_immutable_historical_input",
        "v8_one_round_authorization_is_consumed",
        "active_research_cycle_exists", "active_target_exists",
        "same_route_continue_allowed", "mathematical_construction_authorized",
        "carrier_or_atlas_enumeration_authorized",
        "theorem_credit_authorized", "ledger_promotion_authorized",
        "github_remains_read_only", "drive_connector_must_not_be_used",
    }, "process-gate keys")
    require(gates["v9_is_current_target_selector"] is True, "V9 authority")
    require(gates["v8_is_immutable_historical_input"] is True, "V8 history")
    require(gates["v8_one_round_authorization_is_consumed"] is True, "V8 consumed")
    for key in (
        "active_research_cycle_exists",
        "active_target_exists",
        "same_route_continue_allowed",
        "mathematical_construction_authorized",
        "carrier_or_atlas_enumeration_authorized",
        "theorem_credit_authorized",
        "ledger_promotion_authorized",
    ):
        require(gates[key] is False, key)
    require(gates["github_remains_read_only"] is True, "GitHub gate")
    require(gates["drive_connector_must_not_be_used"] is True, "Drive gate")
    require(candidate["source_pins"] == SOURCE_PINS, "source pins")


def validate_integrity(candidate: dict) -> None:
    require(canonical_digest(candidate) == STATE_DIGEST, "canonical state digest")


def validate_frozen_sources(candidate: dict) -> None:
    require(git_text("rev-parse", f"{CLOSE}^{{tree}}") == CLOSE_TREE, "frozen close tree")
    require(git_text("rev-parse", f"{REFEREE}^{{tree}}") == REFEREE_TREE, "frozen referee tree")
    require(git_text("merge-base", "--is-ancestor", REFEREE, CLOSE) == "", "referee ancestry")
    for path, expected in SOURCE_PINS.items():
        require(sha256(frozen(path)).hexdigest() == expected, f"frozen source pin {path}")

    v8 = frozen_json("ai/omreal/data/CANONICAL_RESEARCH_STATE_V8.json")
    require(v8["status"] == "PIVOT_REQUIRED" and v8["theorem"]["score"] == "2/9", "V8 ledger")
    require(v8["bounded_feasibility_program"]["authorization"]["proof_program_feasibility_analysis"] is True, "V8 opening authority")
    require(v8["bounded_feasibility_program"]["round_bounds"]["feasibility_rounds"] == 1, "V8 one-round bound")

    cycle_path = "ops/research-team/cycles/2026-09-01-d3-mixed-carrier-theorem-feasibility-gate1/"
    manifest = frozen_json(cycle_path + "CLOSING_MANIFEST.json")
    result = manifest["result"]
    require(result["closing_ledger"] == "2/9" and result["ledger_delta"] == "0/9", "manifest ledger")
    require(result["trajectory"] == "STALLED" and result["strategy_action"] == "STOP", "manifest strategy")
    require(result["selected_successor"] == "NONE" and result["construction_started"] is False, "manifest successor")
    require(result["opening_vector"] == result["checkpoint_vector"] == OPENING_VECTOR, "manifest opening vector")
    require(result["closing_vector"] == CLOSING_VECTOR, "manifest closing vector")
    require(manifest["handoffs"] == {
        "topology": "NULL",
        "falsifier": "NULL",
        "naturality": "NULL",
        "referee": "NULL",
        "cycle": "NULL",
        "positive_finite_program_found": False,
        "universal_negative_found": False,
    }, "manifest handoffs")
    require(manifest["measures"]["triple_residual_is_component_denominator"] is False, "manifest component scope")
    require(manifest["publication"] == {
        "github_mode": "READ_ONLY",
        "github_write": False,
        "google_drive_connector_used": False,
        "network_used": False,
        "external_solver_used": False,
    }, "manifest publication")
    require(manifest["referee_pins"] == {
        "ops/team/d3-mixed-carrier-referee/RESULT.json": SOURCE_PINS["ops/team/d3-mixed-carrier-referee/RESULT.json"],
        "ops/team/d3-mixed-carrier-referee/REVIEW.md": SOURCE_PINS["ops/team/d3-mixed-carrier-referee/REVIEW.md"],
        "ops/team/d3-mixed-carrier-referee/verify_referee.py": SOURCE_PINS["ops/team/d3-mixed-carrier-referee/verify_referee.py"],
    }, "manifest referee pins")

    closing = frozen_json(cycle_path + "CLOSING_CANDIDATE.json")
    require(closing["trajectory_classification"] == "STALLED", "candidate trajectory")
    require(closing["overall_handoff"] == "NULL" and closing["strategy_action"] == "STOP", "candidate strategy")
    require(closing["selected_successor"] == "NONE" and closing["construction_started"] is False, "candidate successor")
    require(closing["automatic_reset"]["same_blocker_streak_closing"] == 6, "candidate blocker streak")
    require(closing["automatic_reset"]["zero_ledger_streak_closing"] == 9, "candidate ledger streak")
    require(closing["next_strategy"]["eligible_successor_count"] == 0, "candidate successor count")
    require(closing["next_strategy"]["construction_authorized"] is False, "candidate construction")
    producer_paths = [
        "ops/team/d3-mixed-carrier-topology/RESULT.json",
        "ops/team/d3-mixed-carrier-topology/THEOREM_MEMO.md",
        "ops/team/d3-mixed-carrier-falsifier/RESULT.json",
        "ops/team/d3-mixed-carrier-falsifier/OBSTRUCTION_DOSSIER.md",
        "ops/team/d3-mixed-carrier-naturality/RESULT.json",
        "ops/team/d3-mixed-carrier-naturality/NATURALITY_MEMO.md",
    ]
    require(closing["evidence_pins"] == {path: SOURCE_PINS[path] for path in producer_paths}, "candidate producer pins")
    for name, target in closing["program_status"].items():
        if name in FIRST_MISSING:
            require(target["status"] == "NULL", f"candidate target {name}")
            require(target["first_missing"] == FIRST_MISSING[name], f"candidate first missing {name}")

    lane_paths = {
        "topology": "ops/team/d3-mixed-carrier-topology/RESULT.json",
        "falsifier": "ops/team/d3-mixed-carrier-falsifier/RESULT.json",
        "naturality": "ops/team/d3-mixed-carrier-naturality/RESULT.json",
    }
    for name, path in lane_paths.items():
        require(frozen_json(path)["handoff"] == "NULL", f"{name} lane handoff")
    require(frozen_json(lane_paths["falsifier"])["universal_negative_found"] is False, "falsifier scope")

    referee = frozen_json("ops/team/d3-mixed-carrier-referee/RESULT.json")
    require(referee["review_verdict"] == "ACCEPT_FROZEN_CANDIDATE_FAIL_CLOSED", "referee verdict")
    require(referee["referee_handoff"] == referee["cycle_handoff"] == "NULL", "referee handoffs")
    require(referee["trajectory"]["classification"] == "STALLED", "referee trajectory")
    require(referee["next_strategy"]["decision"] == "STOP", "referee decision")
    require(referee["next_strategy"]["selected_successor"] == "NONE", "referee successor")
    require(referee["hostile_mutations"]["rejected"] == 87, "referee hostiles")
    require(referee["evidence_pins"] == {path: SOURCE_PINS[path] for path in producer_paths}, "referee producer pins")

    report = frozen(cycle_path + "CYCLE_REPORT.md").decode("utf-8")
    require("Automatic strategy-reset result: **`STOP`**" in report, "report STOP")
    require("Selected successor: `NONE`" in report, "report successor")
    require("Reopening requires a new governed" in report, "report reopen gate")
    require(candidate["predecessor"]["sha256"] == sha256(frozen(candidate["predecessor"]["path"])).hexdigest(), "predecessor source")


def current_status_docs() -> dict[str, str]:
    return {
        "README": (ROOT / "README.md").read_text(encoding="utf-8"),
        "operating system": (ROOT / "ai/omreal/RESEARCH_OPERATING_SYSTEM.md").read_text(encoding="utf-8"),
        "status V6": (ROOT / "ai/omreal/NINE_DIAGONAL_STATUS_V6.md").read_text(encoding="utf-8"),
        "prospectus": (ROOT / "ai/omreal/9DVL_THEOREM_PROSPECTUS.md").read_text(encoding="utf-8"),
    }


def validate_authority_docs(surfaces: dict[str, str]) -> None:
    exact_keys(surfaces, {"README", "operating system", "status V6", "prospectus"}, "authority surface keys")
    normalized = {name: " ".join(text.split()) for name, text in surfaces.items()}
    for name, text in normalized.items():
        require("CANONICAL_RESEARCH_STATE_V9.json" in text, f"{name} V9 pointer")
    readme = normalized["README"]
    operating_system = normalized["operating system"]
    status = normalized["status V6"]
    prospectus = normalized["prospectus"]
    require("The only selected work is one bounded" not in readme, "README stale active round")
    require("V8 authorizes only one bounded" not in operating_system, "operating-system stale authority")
    require("`STOP / NONE`" in readme, "README STOP/NONE")
    require("NINE_DIAGONAL_STATUS_V6.md" in readme, "README V6 pointer")
    require("verify_canonical_research_state_v9.py" in readme, "README V9 verifier")
    require("verify_canonical_research_state_v9.py" in operating_system, "operating-system V9 verifier")
    require("marks the only V8 round consumed" in operating_system, "operating-system consumed round")
    require("selects no active target" in operating_system, "operating-system no active target")
    require("authorization is consumed" in status, "status consumed authority")
    require("No research target or construction cycle is active" in status, "status no active target")
    require("Post-cycle disposition" in prospectus, "prospectus close notice")
    require("V9 selects no active research target" in prospectus, "prospectus no active target")
    combined = "\n".join(normalized.values())
    for stale in (
        "V8 is current authority",
        "V8 round remains authorized",
        "Target A is selected",
        "construction is authorized",
        "automatic reopening is authorized",
    ):
        require(stale not in combined, f"stale authority claim: {stale}")
    lowered = combined.lower()
    for pattern in (
        r"\bv8\b.{0,40}\b(?:is|remains)\b.{0,20}\bcurrent authority\b",
        r"\bv8\b.{0,80}\bround\b.{0,40}\b(?:is|remains)\b.{0,20}\bauthoriz",
        r"\btarget a\b.{0,40}\b(?:is|remains)\b.{0,20}\bselected\b",
        r"\bconstruction\b.{0,20}\b(?:is|remains)\b.{0,20}\bauthoriz",
        r"\bautomatic reopening\b.{0,20}\b(?:is|remains)\b.{0,20}\bauthoriz",
    ):
        require(re.search(pattern, lowered) is None, f"stale authority pattern: {pattern}")


def hostile_authority_docs(surfaces: dict[str, str]) -> int:
    mutations: list[dict[str, str]] = []

    candidate = deepcopy(surfaces)
    candidate["README"] = candidate["README"].replace("NINE_DIAGONAL_STATUS_V6.md", "NINE_DIAGONAL_STATUS_V5.md")
    mutations.append(candidate)
    for surface, claim in (
        ("README", "V8 is current authority"),
        ("operating system", "V8 round remains authorized"),
        ("status V6", "Target A is selected"),
        ("status V6", "construction is authorized"),
        ("prospectus", "automatic reopening is authorized"),
    ):
        candidate = deepcopy(surfaces)
        candidate[surface] += "\n" + claim + "\n"
        mutations.append(candidate)
    candidate = deepcopy(surfaces)
    candidate["README"] += "\nV8 remains the current authority and its bounded round remains authorized.\n"
    mutations.append(candidate)

    rejected = 0
    for candidate in mutations:
        try:
            validate_authority_docs(candidate)
        except AuditError:
            rejected += 1
    require(len(mutations) == EXPECTED_AUTHORITY_HOSTILES, "authority hostile census")
    require(rejected == EXPECTED_AUTHORITY_HOSTILES, "authority hostile accepted")
    return rejected


def hostile_mutations(stored: dict) -> int:
    mutations: list[dict] = []

    def add(path: tuple[object, ...], value: object) -> None:
        candidate = deepcopy(stored)
        cursor = candidate
        for key in path[:-1]:
            cursor = cursor[key]
        cursor[path[-1]] = value
        mutations.append(candidate)

    add(("format",), "9dvl-canonical-research-state-v8")
    add(("status",), "ACTIVE")
    add(("repository", "branch"), "research/local-d3-mixed-carrier-theorem-feasibility-gate1-20260901")
    add(("repository", "canonical_evidence_close_commit"), "0" * 40)
    add(("repository", "canonical_evidence_close_tree"), "0" * 40)
    add(("repository", "github_mode"), "WRITE_ALLOWED")
    add(("repository", "github_write"), True)
    add(("repository", "drive_connector_used"), True)
    add(("predecessor", "sha256"), "0" * 64)
    add(("predecessor", "v8_one_round_authorization"), "ACTIVE")
    add(("authoritative_cycle", "trajectory"), "CONVERGING")
    add(("authoritative_cycle", "strategy_action"), "CONTINUE")
    add(("authoritative_cycle", "discovery_handoffs", "topology"), "POSITIVE")
    add(("authoritative_cycle", "selected_successor"), PROGRAM)
    add(("authoritative_cycle", "construction_started"), True)
    add(("theorem", "score"), "3/9")
    add(("theorem", "proved_diagonals"), [1, 2, 3])
    add(("theorem", "promotion"), "DIAGONAL_3")
    add(("proof_distance", "closing_vector"), OPENING_VECTOR)
    add(("proof_distance", "delta"), 1)
    add(("proof_distance", "delta"), False)
    add(("proof_distance", "closing_vector", 1), True)
    add(("proof_distance", "minimum_acceptable_decrease_met"), True)
    add(("open_obligations", "load_bearing_count"), 6)
    add(("open_obligations", "pair_residual"), 0)
    add(("open_obligations", "triple_source_residual"), 0)
    add(("open_obligations", "triple_source_is_component_denominator"), True)
    add(("open_obligations", "items", 0, "status"), "PROVED")
    add(("open_obligations", "items", 0, "requires"), ["bogus"])
    add(("open_obligations", "items", 6, "residual_source_orbits"), 0)
    add(("completed_feasibility_program", "authorization_status"), "ACTIVE")
    add(("completed_feasibility_program", "rounds_authorized"), True)
    add(("completed_feasibility_program", "rounds_completed"), True)
    add(("completed_feasibility_program", "rounds_completed"), 0)
    add(("completed_feasibility_program", "overall_handoff"), "POSITIVE")
    add(("completed_feasibility_program", "positive_finite_program_found"), True)
    add(("completed_feasibility_program", "universal_negative_found"), True)
    add(("completed_feasibility_program", "targets", "A", "status"), "POSITIVE")
    add(("completed_feasibility_program", "targets", "B", "rational_pair_kernel_proved"), True)
    add(("completed_feasibility_program", "targets", "C", "triple_escape_proved"), True)
    add(("completed_feasibility_program", "dependency_logic", "target_a_alone_proves_no_global_pair_rank"), False)
    add(("completed_feasibility_program", "dependency_logic", "feasibility_handoffs_have_theorem_credit"), True)
    add(("selected_next_target", "id"), "TARGET_A")
    add(("selected_next_target", "eligible_successor_count"), False)
    add(("selected_next_target", "eligible_successor_count"), 1)
    add(("selected_next_target", "strategy_action"), "PIVOT")
    add(("selected_next_target", "construction_authorized"), True)
    add(("selected_next_target", "automatic_reopening_authorized"), True)
    add(("selected_next_target", "reopen_requires"), [])
    add(("selected_next_target", "prohibited_automatic_continuations"), [])
    add(("process_gates", "v8_one_round_authorization_is_consumed"), False)
    add(("process_gates", "active_research_cycle_exists"), True)
    add(("process_gates", "active_target_exists"), True)
    add(("process_gates", "same_route_continue_allowed"), True)
    add(("process_gates", "mathematical_construction_authorized"), True)
    add(("process_gates", "theorem_credit_authorized"), True)
    add(("process_gates", "ledger_promotion_authorized"), True)

    candidate = deepcopy(stored)
    candidate["source_pins"].pop(next(iter(candidate["source_pins"])))
    mutations.append(candidate)

    rejected = 0
    for candidate in mutations:
        try:
            validate_semantics(candidate)
        except AuditError:
            rejected += 1
    try:
        parse_json('{"status":"STOPPED","status":"ACTIVE"}')
    except AuditError:
        rejected += 1
    require(len(mutations) + 1 == EXPECTED_STATE_HOSTILES, "state hostile census")
    require(rejected == EXPECTED_STATE_HOSTILES, "state hostile mutation accepted")
    return rejected


def main() -> None:
    stored = load_json(STATE_PATH)
    validate_semantics(stored)
    validate_integrity(stored)
    validate_frozen_sources(stored)
    authority = current_status_docs()
    validate_authority_docs(authority)
    state_rejected = hostile_mutations(stored)
    authority_rejected = hostile_authority_docs(authority)
    rejected = state_rejected + authority_rejected
    print(
        "PASS canonical V9 STOP/NONE; ledger 2/9; "
        f"authorization consumed; {state_rejected}/{EXPECTED_STATE_HOSTILES} state and "
        f"{authority_rejected}/{EXPECTED_AUTHORITY_HOSTILES} authority hostiles rejected "
        f"({rejected} total)"
    )


if __name__ == "__main__":
    main()
