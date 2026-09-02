#!/usr/bin/env python3
"""Verify the post-SREP fail-closed 9DVL canonical state."""

from __future__ import annotations

from copy import deepcopy
from hashlib import sha256
import json
from pathlib import Path
import subprocess


ROOT = Path(__file__).resolve().parents[2]
STATE_PATH = ROOT / "ai/omreal/data/CANONICAL_RESEARCH_STATE_V10.json"
CLOSE = "740bff688f6136e94ba4430cbe6bc1e85e692e7f"
CLOSE_TREE = "97ce7c4393547950ff061a30e444aca825d8ff2f"
REFEREE = "435f098d0ccd42f4dc2b7ddc5f3608ad2be7875b"
REFEREE_TREE = "32c9668a352a7fdcab9d84436ea5286ffae3b551"
OPENING_VECTOR = [
    "2/9", 1, ["diag3_pair_hc1", "diag3_triple_hc0"], 7,
    "UNKNOWN", "UNKNOWN", 6, 9,
]
CLOSING_VECTOR = [
    "2/9", 1, ["diag3_pair_hc1", "diag3_triple_hc0"], 7,
    "UNKNOWN", "UNKNOWN", 7, 10,
]
OBLIGATIONS = [
    "global_gluing",
    "extension_labels",
    "strict_closure",
    "relative_infinity",
    "middle_rank_replay",
    "diag3_pair_hc1",
    "diag3_triple_hc0",
]
PREREQUISITES = [
    "EXECUTABLE_INDEPENDENTLY_TRACEABLE_REPLACEMENT_BACKEND",
    "ALL_PARENT_PROPER_REGION_AND_PAIRWISE_INCOMPARABILITY_CLASSIFIER",
    "EXACT_QUANTIFIER_FREE_P_CLOSED_PARENT_COMPACTIFICATION_AND_TRUE_INFINITY",
]
REOPEN = [
    "NEW_EXPLICIT_USER_AUTHORITY",
    "NEW_GOVERNED_CYCLE",
    "CONCRETE_FINITE_ROUTE_FOR_ONE_FIRST_MISSING_GLOBAL_EDGE",
    "PREDECLARED_THEOREM_LEVEL_STRICT_DECREASE",
    "FRESH_CANONICAL_OPENING_AUDIT_AND_INDEPENDENT_REPLAY",
]


class AuditError(RuntimeError):
    pass


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AuditError(message)


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


def git_bytes(commit: str, path: str) -> bytes:
    return subprocess.run(
        ["git", "show", f"{commit}:{path}"], cwd=ROOT, check=True,
        stdout=subprocess.PIPE, stderr=subprocess.PIPE,
    ).stdout


def git_text(*args: str) -> str:
    return subprocess.run(
        ["git", *args], cwd=ROOT, check=True, text=True,
        stdout=subprocess.PIPE, stderr=subprocess.PIPE,
    ).stdout.strip()


def exact_keys(value: dict, expected: set[str], label: str) -> None:
    require(set(value) == expected, label)


def validate(candidate: dict) -> None:
    exact_keys(candidate, {
        "format", "status", "as_of", "repository", "predecessor",
        "authoritative_cycle", "theorem", "proof_distance",
        "open_obligations", "completed_replacement_gate",
        "selected_next_target", "process_gates", "source_pins",
    }, "top-level keys")
    require(candidate["format"] == "9dvl-canonical-research-state-v10", "format")
    require(candidate["status"] == "STOPPED", "status")
    require(candidate["as_of"] == "2026-09-02", "date")

    repository = candidate["repository"]
    require(repository["branch"] == "research/local-9dvl-post-srep-stop-v10-20260902", "branch")
    require(repository["canonical_evidence_close_commit"] == CLOSE, "close commit")
    require(repository["canonical_evidence_close_tree"] == CLOSE_TREE, "close tree")
    require(repository["integrated_referee_commit"] == REFEREE, "referee commit")
    require(repository["integrated_referee_tree"] == REFEREE_TREE, "referee tree")
    require(repository["github_write"] is False, "GitHub write")
    require(repository["drive_recovery_bundle_verified"] is True, "recovery bundle")
    require(repository["network_contact_with_authors"] is False, "author contact")

    predecessor = candidate["predecessor"]
    require(predecessor["path"] == "ai/omreal/data/CANONICAL_RESEARCH_STATE_V9.json", "predecessor path")
    require(predecessor["sha256"] == candidate["source_pins"][predecessor["path"]], "predecessor pin")
    require(predecessor["v9_automatic_reopening_authorized"] is False, "V9 reopening")
    require(predecessor["user_reopening_authority_received_after_close"] is True, "user authority")

    cycle = candidate["authoritative_cycle"]
    require(cycle["id"] == "2026-09-02-d3-global-semialgebraic-diagram-replacement-gate1", "cycle id")
    require(cycle["closing_commit"] == CLOSE and cycle["closing_tree"] == CLOSE_TREE, "cycle close")
    require(cycle["referee_commit"] == REFEREE and cycle["referee_tree"] == REFEREE_TREE, "cycle referee")
    require(cycle["q0_handoff"] == "NULL_NO_EXECUTABLE_REPLACEMENT_BACKEND", "Q0 handoff")
    require(cycle["independent_verdict"] == "Q0_NULL_INDEPENDENTLY_CONFIRMED", "Q0 review")
    require(cycle["trajectory"] == "STALLED" and cycle["strategy_action"] == "STOP", "cycle strategy")
    require(cycle["selected_successor"] == "NONE", "cycle successor")
    require(cycle["same_route_continue"] is False and cycle["construction_started"] is False, "cycle continuation")

    theorem = candidate["theorem"]
    require(theorem["score"] == "2/9" and theorem["proved_diagonals"] == [1, 2], "ledger")
    require(theorem["promotion"] == "NONE", "promotion")

    distance = candidate["proof_distance"]
    require(distance["opening_vector"] == OPENING_VECTOR, "opening vector")
    require(distance["closing_vector"] == CLOSING_VECTOR, "closing vector")
    require(type(distance["delta"]) is int and distance["delta"] == 0, "distance delta")
    require(distance["minimum_acceptable_decrease_met"] is False, "minimum decrease")
    require(distance["same_blocker_streak_closing"] == 7, "blocker streak")
    require(distance["zero_ledger_streak_closing"] == 10, "ledger streak")

    obligations = candidate["open_obligations"]
    require(obligations["load_bearing_count"] == 7, "obligation count")
    require(obligations["pair_residual"] == obligations["pair_coverage"] == "UNKNOWN", "pair scope")
    require(obligations["triple_source_total"] == 79_102_449, "triple total")
    require(obligations["triple_source_settled"] == 77_940_147, "triple settled")
    require(obligations["triple_source_residual"] == 1_162_302, "triple residual")
    require(obligations["triple_source_total"] - obligations["triple_source_settled"] == obligations["triple_source_residual"], "triple arithmetic")
    require(obligations["triple_source_is_component_denominator"] is False, "component scope")
    require([row["id"] for row in obligations["items"]] == OBLIGATIONS, "obligation ids")
    require(all(row["status"] == "INCONCLUSIVE" for row in obligations["items"]), "obligation status")

    gate = candidate["completed_replacement_gate"]
    require(gate["authorization_status"] == "CONSUMED", "gate authorization")
    require(gate["q0_pass"] is False and gate["q1_activated"] is False, "Q0/Q1")
    require(gate["theorem_credit"] == "NONE" and gate["cloud_used"] is False, "gate consequence")
    require(gate["first_missing_prerequisites"] == PREREQUISITES, "missing prerequisites")

    selected = candidate["selected_next_target"]
    require(selected["id"] == "NONE" and type(selected["eligible_successor_count"]) is int, "selected target")
    require(selected["eligible_successor_count"] == 0, "successor count")
    require(selected["strategy_action"] == "STOP", "next strategy")
    require(selected["construction_authorized"] is False, "construction authorization")
    require(selected["automatic_reopening_authorized"] is False, "automatic reopening")
    require(selected["reopen_requires"] == REOPEN, "reopening contract")

    gates = candidate["process_gates"]
    require(gates["v10_is_current_target_selector"] is True, "V10 authority")
    require(gates["v9_is_immutable_historical_input"] is True, "V9 history")
    for key in (
        "active_research_cycle_exists", "active_target_exists",
        "same_route_continue_allowed", "mathematical_construction_authorized",
        "theorem_credit_authorized", "ledger_promotion_authorized",
    ):
        require(gates[key] is False, key)
    require(gates["github_remains_read_only"] is True, "GitHub mode")
    require(gates["author_contact_prohibited_by_latest_user_instruction"] is True, "author-contact gate")


def validate_sources(candidate: dict) -> None:
    require(git_text("rev-parse", f"{CLOSE}^{{tree}}") == CLOSE_TREE, "frozen close tree")
    require(git_text("rev-parse", f"{REFEREE}^{{tree}}") == REFEREE_TREE, "frozen referee tree")
    for path, expected in candidate["source_pins"].items():
        require(sha256(git_bytes(CLOSE, path)).hexdigest() == expected, f"source pin {path}")

    base = "ops/research-team/cycles/2026-09-02-d3-global-semialgebraic-diagram-replacement-gate1/"
    manifest = parse_json(git_bytes(CLOSE, base + "CLOSING_MANIFEST.json"))
    result = manifest["result"]
    require(result["closing_ledger"] == "2/9" and result["ledger_delta"] == "0/9", "manifest ledger")
    require(result["trajectory"] == "STALLED" and result["strategy_action"] == "STOP", "manifest strategy")
    require(result["selected_successor"] == "NONE" and result["same_route_continue"] is False, "manifest successor")
    require(result["opening_vector"] == OPENING_VECTOR and result["closing_vector"] == CLOSING_VECTOR, "manifest vectors")
    require(manifest["q0_history"]["q0_pass"] is False and manifest["q0_history"]["q1_eligible"] is False, "manifest Q0")

    producer = parse_json(git_bytes(CLOSE, "ops/team/d3-global-srep-formula-compiler/RESULT.json"))
    require(producer["q0_classification"] == "NULL_NO_EXECUTABLE_REPLACEMENT_BACKEND", "producer Q0")
    require(producer["partial_basu_karisani_parameters"]["N"] is None, "producer N")
    require(producer["partial_basu_karisani_parameters"]["s"] is None, "producer s")
    require(producer["partial_basu_karisani_parameters"]["d"] is None, "producer d")


def validate_docs() -> None:
    paths = [
        ROOT / "README.md",
        ROOT / "ai/omreal/RESEARCH_OPERATING_SYSTEM.md",
        ROOT / "ai/omreal/NINE_DIAGONAL_STATUS_V7.md",
        ROOT / "ai/omreal/9DVL_THEOREM_PROSPECTUS.md",
    ]
    for path in paths:
        text = " ".join(path.read_text(encoding="utf-8").split())
        require("CANONICAL_RESEARCH_STATE_V10.json" in text, f"V10 pointer {path.name}")
        require("2/9" in text, f"ledger {path.name}")
    readme = paths[0].read_text(encoding="utf-8")
    require("NINE_DIAGONAL_STATUS_V7.md" in readme, "README status pointer")
    require("verify_canonical_research_state_v10.py" in readme, "README verifier pointer")


def hostile_mutations(stored: dict) -> int:
    changes = [
        (("format",), "9dvl-canonical-research-state-v9"),
        (("status",), "ACTIVE"),
        (("repository", "canonical_evidence_close_commit"), "0" * 40),
        (("repository", "github_write"), True),
        (("repository", "network_contact_with_authors"), True),
        (("predecessor", "user_reopening_authority_received_after_close"), False),
        (("authoritative_cycle", "q0_handoff"), "POSITIVE"),
        (("authoritative_cycle", "strategy_action"), "CONTINUE"),
        (("authoritative_cycle", "selected_successor"), "SREP_Q1"),
        (("theorem", "score"), "3/9"),
        (("proof_distance", "closing_vector"), OPENING_VECTOR),
        (("proof_distance", "delta"), False),
        (("proof_distance", "same_blocker_streak_closing"), 6),
        (("open_obligations", "load_bearing_count"), 6),
        (("open_obligations", "pair_residual"), 0),
        (("open_obligations", "triple_source_residual"), 0),
        (("open_obligations", "triple_source_is_component_denominator"), True),
        (("completed_replacement_gate", "q0_pass"), True),
        (("completed_replacement_gate", "q1_activated"), True),
        (("completed_replacement_gate", "cloud_used"), True),
        (("selected_next_target", "eligible_successor_count"), True),
        (("selected_next_target", "construction_authorized"), True),
        (("process_gates", "v10_is_current_target_selector"), False),
        (("process_gates", "mathematical_construction_authorized"), True),
        (("process_gates", "author_contact_prohibited_by_latest_user_instruction"), False),
    ]
    rejected = 0
    for path, value in changes:
        candidate = deepcopy(stored)
        cursor = candidate
        for key in path[:-1]:
            cursor = cursor[key]
        cursor[path[-1]] = value
        try:
            validate(candidate)
        except AuditError:
            rejected += 1
    try:
        parse_json('{"status":"STOPPED","status":"ACTIVE"}')
    except AuditError:
        rejected += 1
    require(rejected == len(changes) + 1, "hostile mutation accepted")
    return rejected


def main() -> None:
    state = load_json(STATE_PATH)
    validate(state)
    validate_sources(state)
    validate_docs()
    rejected = hostile_mutations(state)
    print(
        "PASS canonical V10 STOP/NONE; ledger 2/9; SREP Q0 NULL; "
        f"{rejected}/{rejected} hostile mutations rejected"
    )


if __name__ == "__main__":
    main()
