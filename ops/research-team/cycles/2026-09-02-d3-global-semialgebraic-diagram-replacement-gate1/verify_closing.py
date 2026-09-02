#!/usr/bin/env python3
"""Fail-closed integration checks for the D3 formula-replacement close."""

from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path
import subprocess
from typing import Any, Callable


CYCLE = Path(__file__).resolve().parent
ROOT = CYCLE.parents[3]
MANIFEST = CYCLE / "CLOSING_MANIFEST.json"
REPORT = CYCLE / "CYCLE_REPORT.md"
BASE = "0b8141223193c1ea2a1b4fce8e862466749f8b6b"
OPENING_VECTOR = [
    "2/9", 1, ["diag3_pair_hc1", "diag3_triple_hc0"],
    7, "UNKNOWN", "UNKNOWN", 6, 9,
]
CLOSING_VECTOR = [
    "2/9", 1, ["diag3_pair_hc1", "diag3_triple_hc0"],
    7, "UNKNOWN", "UNKNOWN", 7, 10,
]
REPORT_PHRASES = (
    "## Mandatory solution-convergence verdict",
    "Opening proof-distance vector",
    "Closing proof-distance vector",
    "Mid-cycle convergence check",
    "Trajectory classification",
    "Automatic strategy-reset result",
    "Same-route continuation justified",
    "NULL_NO_EXECUTABLE_REPLACEMENT_BACKEND / STALLED / STOP",
    "Q0_NULL_INDEPENDENTLY_CONFIRMED; THEOREM_CREDIT=NONE",
    "Selected successor: `NONE`",
    "zero instances and zero disks",
    "READ_ONLY_EXISTING_INSTANCE_SCOPE_BREACH",
    "## Role assignments and independence",
    "## Mandatory post-cycle strategy evaluation",
)


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def git(*args: str) -> str:
    result = subprocess.run(
        ["git", *args], cwd=ROOT, check=True,
        stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True,
    )
    return result.stdout.strip()


def validate(document: dict[str, Any], *, external: bool) -> None:
    require(document["format"] == "d3-global-semialgebraic-diagram-replacement-closing-v1", "format")
    require(document["cycle_id"] == "2026-09-02-d3-global-semialgebraic-diagram-replacement-gate1", "cycle")
    require(document["canonical_base"]["commit"] == BASE, "base commit")
    require(document["canonical_base"]["tree"] == "faad8f9e78bd54435ee6212535198a08c0e3fe76", "base tree")
    require(document["canonical_base"]["status"] == "STOPPED", "base status")
    require(document["canonical_base"]["edited_by_cycle"] is False, "canonical edited")

    q0 = document["q0_history"]
    require(q0["producer_handoff"] == "NULL_NO_EXECUTABLE_REPLACEMENT_BACKEND", "producer handoff")
    require(q0["falsifier_handoff"] == "CANARY_PACKAGE_SOUND_ONLY", "falsifier scope")
    require(q0["independent_verdict"] == "Q0_NULL_INDEPENDENTLY_CONFIRMED", "q0 verdict")
    require(q0["q0_pass"] is False and q0["q1_eligible"] is False, "q0/q1 flags")
    require(q0["theorem_credit"] == "NONE", "q0 theorem credit")

    referee = document["independent_closing_referee"]
    require(referee["verdict"] == "ACCEPT_FROZEN_MIDPOINT_CLOSE_STALLED_STOP", "referee verdict")
    require(referee["pins_reconstructed_from_git"] == 7, "referee pins")
    require(referee["hostile_mutations_rejected"] == referee["hostile_mutations_total"] == 22, "referee hostiles")
    require(referee["human_review"] is False, "human review")

    result = document["result"]
    require(result["classification"] == "NULL", "classification")
    require(result["opening_ledger"] == result["closing_ledger"] == "2/9", "ledger")
    require(result["ledger_delta"] == "0/9", "ledger delta")
    require(result["opening_load_bearing_obligations"] == 7, "opening obligations")
    require(result["closing_load_bearing_obligations"] == 7, "closing obligations")
    require(result["obligation_delta"] == 0, "obligation delta")
    require(result["pair_residual"] == result["pair_coverage"] == "UNKNOWN", "pair unknowns")
    require(result["theorem_promotion"] == "NONE", "theorem promotion")
    require(result["trajectory"] == "STALLED", "trajectory")
    require(result["automatic_strategy_reset"] == "FIRED", "strategy reset")
    require(result["strategy_action"] == "STOP", "strategy action")
    require(result["same_route_continue"] is False, "same-route continuation")
    require(result["selected_successor"] == "NONE", "successor")
    require(result["opening_vector"] == result["midpoint_vector"] == OPENING_VECTOR, "opening/midpoint vector")
    require(result["closing_vector"] == CLOSING_VECTOR, "closing vector")

    missing = document["first_missing_prerequisites"]
    require("NO_EXECUTABLE" in missing["replacement_backend"], "backend boundary")
    require("MISSING" in missing["global_denominator"], "denominator")
    require("MISSING" in missing["closed_formulas"], "closed formulas")
    require(missing["parameters"] == {"N": None, "s": None, "d": None, "k": "178_TEMPLATE_ONLY"}, "parameters")
    require(missing["numeric_full_scope_forecast"] is None, "forecast")

    cloud = document["cloud"]
    require(cloud["activation"] == "DENIED_Q0_GATE_FAILED", "cloud activation")
    require(cloud["used"] is False and cloud["actual_spend_usd"] == 0, "cloud usage")
    require(cloud["cycle_instances_created"] == 0, "cloud creation")
    require(cloud["cycle_prefix_instances_after"] == 0, "cloud instances")
    require(cloud["cycle_prefix_disks_after"] == 0, "cloud disks")
    require(cloud["existing_claude_control"] == "NO_MUTATION_FINAL_STATE_NOT_ASSERTED", "existing instance")
    require(cloud["read_only_existing_instance_inspection_deviation"] is True, "inspection deviation")
    require(cloud["cloud_policy_clean_pass"] is False, "cloud compliance")
    require(cloud["deviation_effect"] == "INDEPENDENTLY_REINFORCES_STOP", "deviation effect")

    require(document["publication"]["github_write"] is False, "github write")
    require(document["publication"]["google_drive_connector_used"] is False, "drive connector")
    require("NO_HUMAN_REVIEW" in document["nonconsequences"], "human nonconsequence")
    require("NO_ROUTE_DISPROOF_OR_RETIREMENT" in document["nonconsequences"], "retirement boundary")
    require("NO_CLEAN_CLOUD_SCOPE_COMPLIANCE_CLAIM" in document["nonconsequences"], "cloud scope boundary")

    if external:
        for relative, pin in document["evidence_pins"].items():
            data = (ROOT / relative).read_bytes()
            require(len(data) == pin["bytes"], f"byte pin: {relative}")
            require(sha256(data) == pin["sha256"], f"hash pin: {relative}")

        producer = json.loads((ROOT / "ops/team/d3-global-srep-formula-compiler/RESULT.json").read_text())
        q0_referee = json.loads((ROOT / "ops/team/d3-global-srep-independent-verifier/RESULT.json").read_text())
        close_referee = json.loads((ROOT / "ops/team/d3-global-srep-closing-referee/RESULT.json").read_text())
        midpoint = json.loads((CYCLE / "MIDPOINT.json").read_text())
        cloud_live_record = json.loads((CYCLE / "CLOUD_PREFLIGHT.json").read_text())
        cloud_correction = json.loads((CYCLE / "CLOUD_SCOPE_CORRECTION.json").read_text())
        require(producer["q0_pass"] is False and producer["q1_eligible"] is False, "producer cross-check")
        require(producer["partial_basu_karisani_parameters"]["N"] is None, "producer N")
        require(producer["partial_basu_karisani_parameters"]["s"] is None, "producer s")
        require(producer["partial_basu_karisani_parameters"]["d"] is None, "producer d")
        require(q0_referee["verdict"] == q0["independent_verdict"], "q0 referee cross-check")
        require(close_referee["verdict"] == referee["verdict"], "closing referee cross-check")
        require(midpoint["q1_activation"] == "DENIED", "midpoint q1")
        require(cloud_live_record["activation"] == cloud["activation"], "cloud record cross-check")
        require(cloud_correction["deviation"]["classification"] == "READ_ONLY_EXISTING_INSTANCE_SCOPE_BREACH", "cloud correction")
        require(cloud_correction["effect_on_close"]["cloud_policy_clean_pass"] is False, "cloud correction compliance")

        report = REPORT.read_text(encoding="utf-8")
        for phrase in REPORT_PHRASES:
            require(phrase in report, f"report phrase: {phrase}")
        require("PENDING_REFEREE" not in report, "pending referee token")
        require((CYCLE / "make_recovery_bundle.py").is_file(), "recovery generator")
        require(git("diff", "--name-only", BASE, "--", "ai/omreal") == "", "protected ai/omreal surface changed")
        canonical = (ROOT / "ai/omreal/data/CANONICAL_RESEARCH_STATE_V9.json").read_bytes()
        base_canonical = subprocess.run(
            ["git", "show", f"{BASE}:ai/omreal/data/CANONICAL_RESEARCH_STATE_V9.json"],
            cwd=ROOT, check=True, stdout=subprocess.PIPE,
        ).stdout
        require(canonical == base_canonical, "canonical V9 drift")


Mutation = Callable[[dict[str, Any]], None]


def set_path(*keys_and_value: Any) -> Mutation:
    *keys, value = keys_and_value
    def mutate(document: dict[str, Any]) -> None:
        target: Any = document
        for key in keys[:-1]:
            target = target[key]
        target[keys[-1]] = value
    return mutate


HOSTILES: tuple[tuple[str, Mutation], ...] = (
    ("positive", set_path("result", "classification", "POSITIVE")),
    ("ledger", set_path("result", "closing_ledger", "3/9")),
    ("ledger_delta", set_path("result", "ledger_delta", "1/9")),
    ("obligation_close", set_path("result", "closing_load_bearing_obligations", 6)),
    ("obligation_delta", set_path("result", "obligation_delta", -1)),
    ("residual", set_path("result", "pair_residual", 0)),
    ("coverage", set_path("result", "pair_coverage", "COMPLETE")),
    ("promotion", set_path("result", "theorem_promotion", "D3")),
    ("trajectory", set_path("result", "trajectory", "CONVERGING")),
    ("no_reset", set_path("result", "automatic_strategy_reset", "NOT_FIRED")),
    ("continue", set_path("result", "strategy_action", "CONTINUE")),
    ("same_route", set_path("result", "same_route_continue", True)),
    ("successor", set_path("result", "selected_successor", "Q1")),
    ("closing_vector", set_path("result", "closing_vector", OPENING_VECTOR)),
    ("q0_pass", set_path("q0_history", "q0_pass", True)),
    ("q1", set_path("q0_history", "q1_eligible", True)),
    ("theorem_credit", set_path("q0_history", "theorem_credit", "PAIR")),
    ("human", set_path("independent_closing_referee", "human_review", True)),
    ("invent_N", set_path("first_missing_prerequisites", "parameters", "N", 1)),
    ("invent_forecast", set_path("first_missing_prerequisites", "numeric_full_scope_forecast", 1)),
    ("cloud_use", set_path("cloud", "used", True)),
    ("cloud_spend", set_path("cloud", "actual_spend_usd", 1)),
    ("cloud_instance", set_path("cloud", "cycle_prefix_instances_after", 1)),
    ("cloud_disk", set_path("cloud", "cycle_prefix_disks_after", 1)),
    ("touch_existing", set_path("cloud", "existing_claude_control", "MODIFIED")),
    ("hide_inspection", set_path("cloud", "read_only_existing_instance_inspection_deviation", False)),
    ("fake_cloud_compliance", set_path("cloud", "cloud_policy_clean_pass", True)),
    ("github_write", set_path("publication", "github_write", True)),
    ("connector", set_path("publication", "google_drive_connector_used", True)),
    ("canonical_edit", set_path("canonical_base", "edited_by_cycle", True)),
)


def run_hostiles(pristine: dict[str, Any]) -> None:
    escaped: list[str] = []
    for name, mutation in HOSTILES:
        hostile = copy.deepcopy(pristine)
        mutation(hostile)
        try:
            validate(hostile, external=False)
        except (AssertionError, KeyError, TypeError):
            continue
        escaped.append(name)
    require(not escaped, "hostile mutations accepted: " + ", ".join(escaped))


def main() -> None:
    document = json.loads(MANIFEST.read_text(encoding="utf-8"))
    validate(document, external=True)
    print(f"PASS closing evidence pins: {len(document['evidence_pins'])}/{len(document['evidence_pins'])}")
    print("PASS Q0 null, Q1 denied, zero theorem and obligation delta")
    print("PASS cloud unused with zero cycle instances/disks; read-only scope breach disclosed")
    print("PASS canonical V9 and all ai/omreal paths unchanged from base")
    print("PASS report convergence labels and recovery plan")
    run_hostiles(document)
    print(f"PASS hostile mutations rejected: {len(HOSTILES)}/{len(HOSTILES)}")
    print("VERDICT NULL / STALLED / STOP; THEOREM_CREDIT=NONE")


if __name__ == "__main__":
    main()
