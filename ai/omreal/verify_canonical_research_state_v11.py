#!/usr/bin/env python3
"""Verify the reconciled post-V10 9DVL STOP/NONE canonical state."""

from __future__ import annotations

from copy import deepcopy
from hashlib import sha256
import json
from pathlib import Path
import subprocess


ROOT = Path(__file__).resolve().parents[2]
STATE_PATH = ROOT / "ai/omreal/data/CANONICAL_RESEARCH_STATE_V11.json"
CLOSE = "a10a47d1e934e4296b9612ccbde6d0b1a74a88bb"
CLOSE_TREE = "eead48c4263f85cb71b0617213011fe5dcae89bf"
TRIPLE_CLOSE = "fb667bfe33ef9e945a82e9a23b615e67f5f39c0f"
TRIPLE_TREE = "117850b25cd94f865cb85e681c465b8260dd9c6a"
MIXED_REFEREE = "3f7c58a46aa4e8ebf6394b7ce7a8e4593f034f3a"
MIXED_REFEREE_TREE = "27d4ef884bb42ad8687e4a6e9eb44d38b30fe4a5"

V10_VECTOR = [
    "2/9", 1, ["diag3_pair_hc1", "diag3_triple_hc0"], 7,
    "UNKNOWN", "UNKNOWN", 7, 10,
]
TRIPLE_VECTOR = [
    "2/9", 1, ["diag3_pair_hc1", "diag3_triple_hc0"], 7,
    "UNKNOWN", "UNKNOWN", 8, 11,
]
CURRENT_VECTOR = [
    "2/9", 1, ["diag3_pair_hc1", "diag3_triple_hc0"], 7,
    "UNKNOWN", "UNKNOWN", 9, 12,
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
REOPEN = [
    "NEW_GOVERNED_CYCLE_WITH_EXPLICIT_USER_AUTHORITY",
    "GENUINELY_NEW_THEOREM_CAPABLE_INPUT",
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
        ["git", "show", f"{commit}:{path}"],
        cwd=ROOT,
        check=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    ).stdout


def git_text(*args: str) -> str:
    return subprocess.run(
        ["git", *args],
        cwd=ROOT,
        check=True,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    ).stdout.strip()


def exact_keys(value: dict, expected: set[str], label: str) -> None:
    require(set(value) == expected, label)


def validate(candidate: dict) -> None:
    exact_keys(candidate, {
        "format", "status", "as_of", "repository", "predecessor",
        "authoritative_history", "theorem", "proof_distance",
        "open_obligations", "completed_post_v10_gates",
        "selected_next_target", "process_gates", "source_pins",
    }, "top-level keys")
    require(candidate["format"] == "9dvl-canonical-research-state-v11", "format")
    require(candidate["status"] == "STOPPED", "status")
    require(candidate["as_of"] == "2026-09-03", "date")

    repository = candidate["repository"]
    require(repository["branch"] == "research/local-9dvl-post-mixed-100-stop-v11-20260903", "branch")
    require(repository["canonical_evidence_close_commit"] == CLOSE, "close commit")
    require(repository["canonical_evidence_close_tree"] == CLOSE_TREE, "close tree")
    require(repository["latest_integrated_referee_commit"] == MIXED_REFEREE, "referee commit")
    require(repository["latest_integrated_referee_tree"] == MIXED_REFEREE_TREE, "referee tree")
    require(repository["github_write"] is False, "GitHub write")
    require(repository["drive_recovery_bundle_verified"] is True, "recovery bundle")
    require(repository["network_research"] is False, "network research")
    require(repository["author_contact"] is False, "author contact")
    require(repository["user_scope"] == "9DVL_ONLY", "user scope")

    predecessor = candidate["predecessor"]
    require(predecessor["path"] == "ai/omreal/data/CANONICAL_RESEARCH_STATE_V10.json", "predecessor path")
    require(predecessor["sha256"] == candidate["source_pins"][predecessor["path"]], "predecessor pin")
    require(predecessor["v10_automatic_reopening_authorized"] is False, "V10 reopening")
    require(type(predecessor["post_v10_closed_cycle_count"]) is int, "cycle count type")
    require(predecessor["post_v10_closed_cycle_count"] == 2, "cycle count")

    history = candidate["authoritative_history"]
    require(type(history) is list and len(history) == 2, "history census")
    triple, mixed = history
    require(triple["id"] == "2026-09-02-d3-triple-critical-saturation-component-gate1", "triple id")
    require(triple["closing_commit"] == TRIPLE_CLOSE and triple["closing_tree"] == TRIPLE_TREE, "triple close")
    require(triple["q0"] == "NULL_INDEPENDENTLY_CONFIRMED" and triple["q1"] == "DENIED", "triple Q0/Q1")
    require(triple["trajectory"] == "STALLED" and triple["strategy_action"] == "STOP", "triple strategy")
    require(triple["selected_successor"] == "NONE" and triple["same_route_continue"] is False, "triple successor")
    require(triple["opening_vector"] == V10_VECTOR and triple["closing_vector"] == TRIPLE_VECTOR, "triple vectors")

    require(mixed["id"] == "2026-09-03-d3-mixed-block-100-universal-carrier-gate1", "mixed id")
    require(mixed["closing_commit"] == CLOSE and mixed["closing_tree"] == CLOSE_TREE, "mixed close")
    require(mixed["integrated_referee_commit"] == MIXED_REFEREE, "mixed referee")
    require(mixed["integrated_referee_tree"] == MIXED_REFEREE_TREE, "mixed referee tree")
    require(mixed["classification"] == "NULL", "mixed classification")
    require(mixed["trajectory"] == "STALLED" and mixed["strategy_action"] == "STOP", "mixed strategy")
    require(mixed["selected_successor"] == "NONE" and mixed["same_route_continue"] is False, "mixed successor")
    require(mixed["positive_token"] is None and mixed["negative_token"] is None, "mixed tokens")
    require(mixed["O3"] == mixed["O4"] == "OPEN", "O3/O4")
    require(mixed["opening_vector"] == TRIPLE_VECTOR and mixed["closing_vector"] == CURRENT_VECTOR, "mixed vectors")

    theorem = candidate["theorem"]
    require(theorem["score"] == "2/9" and theorem["proved_diagonals"] == [1, 2], "ledger")
    require(theorem["open_diagonals"] == [3, 4, 5, 6, 7, 8, 9], "open diagonals")
    require(theorem["promotion"] == "NONE", "promotion")
    require(theorem["theorem_level_counterexample"] == "NOT_FOUND", "counterexample")

    distance = candidate["proof_distance"]
    require(distance["v10_closing_vector"] == V10_VECTOR, "V10 vector")
    require(distance["triple_saturation_closing_vector"] == TRIPLE_VECTOR, "triple vector")
    require(distance["mixed_100_closing_vector"] == CURRENT_VECTOR, "mixed vector")
    require(distance["current_vector"] == CURRENT_VECTOR, "current vector")
    require(distance["ledger_delta_since_v10"] == "0/9", "ledger delta")
    require(type(distance["load_bearing_obligation_delta_since_v10"]) is int, "obligation delta type")
    require(distance["load_bearing_obligation_delta_since_v10"] == 0, "obligation delta")
    require(type(distance["certified_residual_delta_since_v10"]) is int, "residual delta type")
    require(distance["certified_residual_delta_since_v10"] == 0, "residual delta")
    require(distance["minimum_acceptable_decrease_met"] is False, "minimum decrease")
    require(distance["same_blocker_streak_closing"] == 9, "blocker streak")
    require(distance["zero_ledger_streak_closing"] == 12, "ledger streak")

    obligations = candidate["open_obligations"]
    require(obligations["load_bearing_count"] == 7, "obligation count")
    require(obligations["pair_residual"] == obligations["pair_coverage"] == "UNKNOWN", "pair scope")
    require(obligations["triple_source_total"] == 79_102_449, "triple total")
    require(obligations["triple_source_settled"] == 77_940_147, "triple settled")
    require(obligations["triple_source_residual"] == 1_162_302, "triple residual")
    require(obligations["triple_source_total"] - obligations["triple_source_settled"] == obligations["triple_source_residual"], "triple arithmetic")
    require(obligations["triple_source_is_component_denominator"] is False, "component scope")
    require([row["id"] for row in obligations["items"]] == OBLIGATIONS, "obligation ids")
    require(all(row["status"] == "INCONCLUSIVE" and row["delta"] == "UNCHANGED" for row in obligations["items"]), "obligation state")

    gates = candidate["completed_post_v10_gates"]
    saturation = gates["triple_component_saturation"]
    require(saturation["authorization_status"] == "CONSUMED", "saturation authorization")
    require(saturation["q0_pass"] is False and saturation["q1_activated"] is False, "saturation Q0/Q1")
    require(saturation["raw_research_saturation_run"] is False, "raw saturation")
    require(saturation["theorem_credit"] == "NONE", "saturation credit")
    carrier = gates["mixed_100_universal_carrier"]
    require(carrier["authorization_status"] == "CONSUMED", "carrier authorization")
    require(carrier["universal_O3_O4_proof"] is False, "carrier proof")
    require(carrier["exact_universal_obstruction"] is False, "carrier obstruction")
    require(carrier["theorem_credit"] == "NONE", "carrier credit")

    selected = candidate["selected_next_target"]
    require(selected["id"] == "NONE", "selected target")
    require(type(selected["eligible_successor_count"]) is int, "successor count type")
    require(selected["eligible_successor_count"] == 0, "successor count")
    require(selected["strategy_action"] == "STOP", "next strategy")
    require(selected["construction_authorized"] is False, "construction authorization")
    require(selected["automatic_reopening_authorized"] is False, "automatic reopening")
    require(selected["reopen_requires"] == REOPEN, "reopening contract")
    require(len(selected["prohibited_automatic_continuations"]) == 7, "prohibited census")

    process = candidate["process_gates"]
    require(process["v11_is_current_target_selector"] is True, "V11 authority")
    require(process["v10_is_immutable_historical_input"] is True, "V10 history")
    for key in (
        "active_research_cycle_exists", "active_target_exists",
        "same_route_continue_allowed", "mathematical_construction_authorized",
        "theorem_credit_authorized", "ledger_promotion_authorized",
        "network_research_authorized", "author_contact_authorized",
    ):
        require(process[key] is False, key)
    require(process["github_remains_read_only"] is True, "GitHub mode")
    require(process["work_scope_is_9dvl_only"] is True, "work scope")


def validate_sources(candidate: dict) -> None:
    require(git_text("rev-parse", f"{CLOSE}^{{tree}}") == CLOSE_TREE, "frozen close tree")
    require(git_text("rev-parse", f"{TRIPLE_CLOSE}^{{tree}}") == TRIPLE_TREE, "triple close tree")
    require(git_text("rev-parse", f"{MIXED_REFEREE}^{{tree}}") == MIXED_REFEREE_TREE, "referee tree")
    for path, expected in candidate["source_pins"].items():
        require(sha256(git_bytes(CLOSE, path)).hexdigest() == expected, f"source pin {path}")

    triple_base = "ops/research-team/cycles/2026-09-02-d3-triple-critical-saturation-component-gate1/"
    triple = parse_json(git_bytes(CLOSE, triple_base + "CLOSING_MANIFEST.json"))
    triple_result = triple["result"]
    require(triple_result["q0"] == "NULL_INDEPENDENTLY_CONFIRMED", "source triple Q0")
    require(triple_result["q1"] == "DENIED" and triple_result["raw_research_saturation_run"] is False, "source triple Q1")
    require(triple_result["opening_vector"] == V10_VECTOR and triple_result["closing_vector"] == TRIPLE_VECTOR, "source triple vectors")
    require(triple_result["trajectory"] == "STALLED" and triple_result["strategy_action"] == "STOP", "source triple strategy")

    triple_referee = parse_json(git_bytes(CLOSE, "ops/team/d3-triple-critical-saturation-closing-referee/RESULT.json"))
    require(triple_referee["status"] == "PASS", "triple referee status")
    require(triple_referee["verdict"] == "ACCEPT_FROZEN_Q0_NULL_CLOSE_STALLED_STOP", "triple referee verdict")
    require(triple_referee["hostile_mutations"]["rejected"] == 22, "triple referee hostiles")

    mixed_base = "ops/research-team/cycles/2026-09-03-d3-mixed-block-100-universal-carrier-gate1/"
    mixed = parse_json(git_bytes(CLOSE, mixed_base + "CLOSING_MANIFEST.json"))
    mixed_result = mixed["result"]
    require(mixed_result["classification"] == "NULL", "source mixed classification")
    require(mixed_result["trajectory"] == "STALLED" and mixed_result["strategy_action"] == "STOP", "source mixed strategy")
    require(mixed_result["opening_vector"] == TRIPLE_VECTOR and mixed_result["closing_vector"] == CURRENT_VECTOR, "source mixed vectors")
    require(mixed_result["O3"] == mixed_result["O4"] == "OPEN", "source O3/O4")
    require(mixed["exact_boundary"]["full_negative_proved"] is False, "source mixed negative")

    independent = parse_json(git_bytes(CLOSE, "ops/team/d3-mixed-100-independent-verifier/RESULT.json"))
    require(independent["status"] == "PASS", "mixed independent status")
    require(independent["verdict"] == "NULL_STALLED_STOP_INDEPENDENTLY_CONFIRMED", "mixed independent verdict")
    require(independent["hostile_mutations"]["implemented"] == 45, "mixed independent hostiles")

    referee = parse_json(git_bytes(CLOSE, "ops/team/d3-mixed-100-closing-referee/RESULT.json"))
    require(referee["status"] == "PASS", "mixed referee status")
    require(referee["verdict"] == "ACCEPT_EXACT_FROZEN_NULL_STALLED_STOP_NONE", "mixed referee verdict")
    require(referee["hostile_mutations"]["rejected"] == 57, "mixed referee hostiles")


def validate_docs() -> None:
    paths = [
        ROOT / "README.md",
        ROOT / "ai/omreal/RESEARCH_OPERATING_SYSTEM.md",
        ROOT / "ai/omreal/NINE_DIAGONAL_STATUS_V8.md",
        ROOT / "ai/omreal/9DVL_THEOREM_PROSPECTUS.md",
    ]
    for path in paths:
        text = " ".join(path.read_text(encoding="utf-8").split())
        require("CANONICAL_RESEARCH_STATE_V11.json" in text, f"V11 pointer {path.name}")
        require("2/9" in text, f"ledger {path.name}")
    readme = paths[0].read_text(encoding="utf-8")
    operating = paths[1].read_text(encoding="utf-8")
    status = " ".join(paths[2].read_text(encoding="utf-8").split())
    require("NINE_DIAGONAL_STATUS_V8.md" in readme, "README status pointer")
    require("verify_canonical_research_state_v11.py" in readme, "README verifier pointer")
    require("verify_canonical_research_state_v11.py" in operating, "operating-system verifier pointer")
    require("NULL / STALLED / STOP / NONE" in status, "status disposition")
    require("9, 12" in status, "status streaks")
    require("No research cycle, target, construction, or automatic successor is active" in status, "status no active target")


def hostile_mutations(stored: dict) -> int:
    changes = [
        (("format",), "9dvl-canonical-research-state-v10"),
        (("status",), "ACTIVE"),
        (("repository", "canonical_evidence_close_commit"), "0" * 40),
        (("repository", "github_write"), True),
        (("repository", "network_research"), True),
        (("predecessor", "post_v10_closed_cycle_count"), True),
        (("authoritative_history", 0, "q0"), "PASS"),
        (("authoritative_history", 0, "q1"), "ACTIVE"),
        (("authoritative_history", 0, "closing_vector"), V10_VECTOR),
        (("authoritative_history", 1, "classification"), "POSITIVE"),
        (("authoritative_history", 1, "O3"), "PROVED"),
        (("authoritative_history", 1, "negative_token"), "NEGATIVE"),
        (("authoritative_history", 1, "strategy_action"), "CONTINUE"),
        (("theorem", "score"), "3/9"),
        (("theorem", "proved_diagonals"), [1, 2, 3]),
        (("proof_distance", "current_vector"), TRIPLE_VECTOR),
        (("proof_distance", "ledger_delta_since_v10"), "1/9"),
        (("proof_distance", "load_bearing_obligation_delta_since_v10"), False),
        (("proof_distance", "same_blocker_streak_closing"), 8),
        (("open_obligations", "load_bearing_count"), 6),
        (("open_obligations", "pair_residual"), 0),
        (("open_obligations", "triple_source_residual"), 0),
        (("open_obligations", "triple_source_is_component_denominator"), True),
        (("completed_post_v10_gates", "triple_component_saturation", "q0_pass"), True),
        (("completed_post_v10_gates", "triple_component_saturation", "raw_research_saturation_run"), True),
        (("completed_post_v10_gates", "mixed_100_universal_carrier", "universal_O3_O4_proof"), True),
        (("selected_next_target", "eligible_successor_count"), True),
        (("selected_next_target", "construction_authorized"), True),
        (("selected_next_target", "automatic_reopening_authorized"), True),
        (("process_gates", "v11_is_current_target_selector"), False),
        (("process_gates", "active_research_cycle_exists"), True),
        (("process_gates", "theorem_credit_authorized"), True),
        (("process_gates", "work_scope_is_9dvl_only"), False),
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
        "PASS canonical V11 STOP/NONE; ledger 2/9; two post-V10 gates NULL; "
        f"{rejected}/{rejected} hostile mutations rejected"
    )


if __name__ == "__main__":
    main()
