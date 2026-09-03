#!/usr/bin/env python3
"""Independent frozen-candidate closing referee for the D3 saturation cycle."""

from __future__ import annotations

import argparse
from copy import deepcopy
from hashlib import sha256
import json
from pathlib import Path
import subprocess


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
CANDIDATE_COMMIT = "0aaa07dc7ae91cdb3ee386c9b7362e650347bdba"
CANDIDATE_TREE = "29bc16c551e43ae0a33ab624a09a4e31f6b546c6"
CANDIDATE_PARENT = "e65f844a4fdb82f5850b9b27eff0dc54274dd735"
CYCLE_ROOT = "ops/research-team/cycles/2026-09-02-d3-triple-critical-saturation-component-gate1"
START_COMMIT = "0095ea4b3abaa8a4cc5181b837838385e4b3d7d9"
BASE_COMMIT = "ba87af7b1ac58d22c0622c908e31dc8ec03d24fa"
CANONICAL = "ai/omreal/data/CANONICAL_RESEARCH_STATE_V10.json"
OUTPUT = HERE / "RESULT.json"


class Reject(AssertionError):
    pass


def require(condition: bool, marker: str) -> None:
    if not condition:
        raise Reject(marker)


def git(*arguments: str, binary: bool = False):
    return subprocess.check_output(["git", *arguments], cwd=ROOT, text=not binary)


def frozen_bytes(path: str, revision: str = CANDIDATE_COMMIT) -> bytes:
    return git("show", f"{revision}:{path}", binary=True)


def frozen_json(path: str) -> tuple[bytes, dict]:
    data = frozen_bytes(path)
    return data, json.loads(data.decode("ascii"))


def digest(data: bytes) -> str:
    return sha256(data).hexdigest()


def pin(path: str) -> tuple[bytes, dict]:
    data = frozen_bytes(path)
    return data, {"bytes": len(data), "sha256": digest(data)}


def reconstruct() -> dict:
    require(git("rev-parse", CANDIDATE_COMMIT).strip() == CANDIDATE_COMMIT, "candidate commit")
    require(git("rev-parse", f"{CANDIDATE_COMMIT}^{{tree}}").strip() == CANDIDATE_TREE, "candidate tree")
    require(git("rev-parse", f"{CANDIDATE_COMMIT}^").strip() == CANDIDATE_PARENT, "candidate parent")

    paths = {
        "closing_candidate": f"{CYCLE_ROOT}/CLOSING_CANDIDATE.json",
        "mid_cycle": f"{CYCLE_ROOT}/MID_CYCLE_CHECKPOINT.json",
        "resources": f"{CYCLE_ROOT}/RESOURCE_ACCOUNTING.json",
        "cycle_policy": f"{CYCLE_ROOT}/CYCLE.md",
        "work_orders": f"{CYCLE_ROOT}/WORK_ORDERS.yaml",
        "opening": f"{CYCLE_ROOT}/OPENING_STATE.json",
        "cycle_report": f"{CYCLE_ROOT}/CYCLE_REPORT.md",
        "constructor": "ops/team/d3-triple-critical-saturation-constructor/RESULT.json",
        "falsifier": "ops/team/d3-triple-critical-saturation-falsifier/RESULT.json",
        "q0_verifier": "ops/team/d3-triple-critical-saturation-independent-verifier/RESULT.json",
        "canonical_v10": CANONICAL,
    }
    pins = {}
    raw = {}
    for name, path in paths.items():
        data, pins[name] = pin(path)
        raw[name] = data

    candidate = json.loads(raw["closing_candidate"].decode("ascii"))
    midpoint = json.loads(raw["mid_cycle"].decode("ascii"))
    resources = json.loads(raw["resources"].decode("ascii"))
    opening = json.loads(raw["opening"].decode("ascii"))
    constructor = json.loads(raw["constructor"].decode("ascii"))
    falsifier = json.loads(raw["falsifier"].decode("ascii"))
    verifier = json.loads(raw["q0_verifier"].decode("ascii"))
    report = raw["cycle_report"].decode("utf-8")

    for path, expected in candidate["evidence_pins"].items():
        data = frozen_bytes(path)
        require(len(data) == expected["bytes"], f"candidate evidence bytes: {path}")
        require(digest(data) == expected["sha256"], f"candidate evidence digest: {path}")

    canonical_base = frozen_bytes(CANONICAL, BASE_COMMIT)
    require(raw["canonical_v10"] == canonical_base, "canonical V10 changed")
    changed = [
        line.strip()
        for line in git("diff", "--name-only", START_COMMIT, CANDIDATE_COMMIT).splitlines()
        if line.strip()
    ]
    allowed_prefixes = (
        CYCLE_ROOT + "/",
        "ops/team/d3-triple-critical-saturation-constructor/",
        "ops/team/d3-triple-critical-saturation-falsifier/",
        "ops/team/d3-triple-critical-saturation-independent-verifier/",
    )
    require(all(path.startswith(allowed_prefixes) for path in changed), "changed path outside owned surfaces")

    require(opening["base"]["commit"] == BASE_COMMIT, "base commit")
    require(opening["base"]["ledger"] == "2/9", "opening ledger")
    require(opening["q0"]["status"] == "OPEN", "opening Q0")
    require(opening["q1"]["status"] == "DENIED_PENDING_Q0", "opening Q1")
    require(constructor["accepted"] is False, "constructor self acceptance")
    require(constructor["q1_status"].startswith("DENIED"), "constructor Q1")
    require(falsifier["verdict"] == "Q0_NULL_MINIMUM_DECREASE_NOT_REACHABLE", "falsifier")
    require(falsifier["hostile_mutations"]["rejected"] == 27, "falsifier hostiles")
    require(verifier["verdict"] == "Q0_NULL_INDEPENDENTLY_CONFIRMED", "independent verifier")
    require(verifier["accepted"] is False, "independent acceptance")
    require(verifier["q1_status"] == "DENIED", "independent Q1")
    require(verifier["hostile_mutations"]["rejected"] == 22, "independent hostiles")

    require(midpoint["q0"]["q0_status"] == "NULL", "midpoint Q0")
    require(midpoint["q1_activation"] == "DENIED", "midpoint Q1")
    require(midpoint["raw_research_saturation_run"] is False, "midpoint raw solve")
    require(midpoint["minimum_decrease_still_reachable_under_fixed_ceiling"] is False, "midpoint decrease")
    require(midpoint["mandatory_mid_cycle_action"] == "FREEZE_Q0_NULL_AND_STOP", "midpoint action")
    require(midpoint["resource_forecast"]["unallocated_seconds_after_saturation_forecast"] == 1_800, "forecast remainder")
    require(len(midpoint["resource_forecast"]["unforecasted_endpoint_obligations"]) == 5, "unforecasted obligations")

    result = candidate["result"]
    require(result["classification"] == "NULL", "classification")
    require(result["q0"] == "NULL_INDEPENDENTLY_CONFIRMED", "closing Q0")
    require(result["q1"] == "DENIED", "closing Q1")
    require(result["raw_research_saturation_run"] is False, "closing raw solve")
    require(result["opening_ledger"] == result["closing_ledger"] == "2/9", "ledger")
    require(result["ledger_delta"] == "0/9", "ledger delta")
    require(result["opening_triple_source_residual"] == result["closing_triple_source_residual"] == 1_162_302, "residual")
    require(result["source_residual_delta"] == 0, "residual delta")
    require(result["opening_load_bearing_obligations"] == result["closing_load_bearing_obligations"] == 7, "obligations")
    require(result["obligation_delta"] == 0, "obligation delta")
    require(result["pair_residual"] == result["pair_coverage"] == "UNKNOWN", "pair denominator")
    require(result["trajectory"] == "STALLED", "trajectory")
    require(result["automatic_strategy_reset"] == "FIRED", "strategy reset")
    require(result["strategy_action"] == "STOP", "strategy action")
    require(result["same_route_continue"] is False, "same route")
    require(result["selected_successor"] == "NONE", "successor")
    require(result["theorem_credit"] == "NONE", "theorem credit")

    proof = candidate["proof_distance"]
    require(proof["opening_vector"] == proof["mid_cycle_vector"], "opening-midpoint vector")
    require(proof["opening_vector"][-2:] == [7, 10], "opening streaks")
    require(proof["closing_vector"][-2:] == [8, 11], "closing streaks")
    require(proof["closing_vector"][:6] == proof["opening_vector"][:6], "proof-distance invariants")
    require(proof["minimum_decrease_achieved"] is False, "minimum decrease")

    require(resources["execution"]["research_ideal_saturation_runs"] == 0, "research saturation count")
    require(resources["execution"]["raw_groebner_or_rur_runs"] == 0, "raw solve count")
    require(resources["external"]["network_research_used"] is False, "network")
    require(resources["external"]["cloud_workers_created"] == 0, "cloud")
    require(resources["external"]["actual_spend_usd"] == 0, "spend")
    require(resources["external"]["github_writes"] == 0, "GitHub")
    require(resources["external"]["author_contacts"] == 0, "author contact")
    require("Lean is a suitable downstream trust layer" in report, "Lean scope note")
    require("NULL / STALLED / STOP" in report, "report status")
    require("STOP / NONE" in report, "report verdict")

    return {
        "format": "d3-triple-critical-saturation-independent-closing-referee-v1",
        "track_id": "d3-triple-critical-saturation-closing-referee",
        "status": "PASS",
        "verdict": "ACCEPT_FROZEN_Q0_NULL_CLOSE_STALLED_STOP",
        "candidate_commit": CANDIDATE_COMMIT,
        "candidate_tree": CANDIDATE_TREE,
        "candidate_parent": CANDIDATE_PARENT,
        "pins": pins,
        "protected_surface_check": {
            "canonical_v10_byte_identical_to_base": True,
            "changed_paths_from_cycle_start": len(changed),
            "all_changed_paths_inside_owned_surfaces": True,
        },
        "independent_closing_reconstruction": {
            "q0": "NULL_INDEPENDENTLY_CONFIRMED",
            "q1": "DENIED",
            "raw_research_saturation_run": False,
            "theorem_delta": 0,
            "source_residual_delta": 0,
            "obligation_delta": 0,
            "opening_vector": proof["opening_vector"],
            "mid_cycle_vector": proof["mid_cycle_vector"],
            "closing_vector": proof["closing_vector"],
            "trajectory": "STALLED",
            "automatic_strategy_reset": "FIRED",
            "strategy_action": "STOP",
            "same_route_continue": False,
            "selected_successor": "NONE",
            "theorem_credit": "NONE",
        },
        "scope": [
            "Independent machine closing review; no human review is claimed.",
            "Accepts only the frozen NULL/STALLED/STOP close with no Q1 run or theorem delta.",
            "Lean is reserved as a downstream checker after exact CAS certificates exist, not counted as present-cycle evidence.",
            "Does not edit canonical state, activate Q1, or select a successor.",
        ],
    }


def validate_close(value: dict) -> None:
    reconstructed = value["independent_closing_reconstruction"]
    require(value["verdict"] == "ACCEPT_FROZEN_Q0_NULL_CLOSE_STALLED_STOP", "verdict")
    require(value["protected_surface_check"]["canonical_v10_byte_identical_to_base"] is True, "canonical")
    require(value["protected_surface_check"]["all_changed_paths_inside_owned_surfaces"] is True, "owned paths")
    require(reconstructed["q0"] == "NULL_INDEPENDENTLY_CONFIRMED", "Q0")
    require(reconstructed["q1"] == "DENIED", "Q1")
    require(reconstructed["raw_research_saturation_run"] is False, "raw run")
    require(reconstructed["theorem_delta"] == reconstructed["source_residual_delta"] == reconstructed["obligation_delta"] == 0, "deltas")
    require(reconstructed["opening_vector"][-2:] == [7, 10], "opening streak")
    require(reconstructed["closing_vector"][-2:] == [8, 11], "closing streak")
    require(reconstructed["trajectory"] == "STALLED", "trajectory")
    require(reconstructed["automatic_strategy_reset"] == "FIRED", "reset")
    require(reconstructed["strategy_action"] == "STOP", "action")
    require(reconstructed["same_route_continue"] is False, "continue")
    require(reconstructed["selected_successor"] == "NONE", "successor")
    require(reconstructed["theorem_credit"] == "NONE", "credit")


def hostile_closes(result: dict) -> list[dict]:
    cases: list[tuple[str, dict]] = []

    def change(identifier: str, path: tuple[str, ...], replacement) -> None:
        candidate = deepcopy(result)
        cursor = candidate
        for key in path[:-1]:
            cursor = cursor[key]
        cursor[path[-1]] = replacement
        cases.append((identifier, candidate))

    change("accept_q0", ("independent_closing_reconstruction", "q0"), "ACCEPTED")
    change("activate_q1", ("independent_closing_reconstruction", "q1"), "ACTIVE")
    change("invent_raw_run", ("independent_closing_reconstruction", "raw_research_saturation_run"), True)
    change("invent_theorem_delta", ("independent_closing_reconstruction", "theorem_delta"), 1)
    change("invent_residual_delta", ("independent_closing_reconstruction", "source_residual_delta"), -1)
    change("invent_obligation_delta", ("independent_closing_reconstruction", "obligation_delta"), -1)
    change("opening_streak_drift", ("independent_closing_reconstruction", "opening_vector"), ["2/9", 1, ["diag3_pair_hc1", "diag3_triple_hc0"], 7, "UNKNOWN", "UNKNOWN", 6, 9])
    change("closing_streak_drift", ("independent_closing_reconstruction", "closing_vector"), ["2/9", 1, ["diag3_pair_hc1", "diag3_triple_hc0"], 7, "UNKNOWN", "UNKNOWN", 7, 10])
    change("converging", ("independent_closing_reconstruction", "trajectory"), "CONVERGING")
    change("informational", ("independent_closing_reconstruction", "trajectory"), "INFORMATIONAL")
    change("disable_reset", ("independent_closing_reconstruction", "automatic_strategy_reset"), "NOT_FIRED")
    change("continue", ("independent_closing_reconstruction", "strategy_action"), "CONTINUE")
    change("pivot", ("independent_closing_reconstruction", "strategy_action"), "PIVOT")
    change("retire", ("independent_closing_reconstruction", "strategy_action"), "RETIRE")
    change("same_route", ("independent_closing_reconstruction", "same_route_continue"), True)
    change("successor", ("independent_closing_reconstruction", "selected_successor"), "D3_SATURATION_GATE2")
    change("grant_credit", ("independent_closing_reconstruction", "theorem_credit"), "ROW_REMOVAL")
    change("canonical_drift", ("protected_surface_check", "canonical_v10_byte_identical_to_base"), False)
    change("path_escape", ("protected_surface_check", "all_changed_paths_inside_owned_surfaces"), False)
    change("verdict_promotion", ("verdict",), "ACCEPT_CONVERGING_CONTINUE")
    change("timeout_instead_of_null", ("independent_closing_reconstruction", "q0"), "TIMEOUT")
    change("q1_null_instead_of_denied", ("independent_closing_reconstruction", "q1"), "NULL")

    rejected = []
    for identifier, candidate in cases:
        try:
            validate_close(candidate)
        except (AssertionError, KeyError, TypeError):
            rejected.append({"id": identifier, "rejected": True})
            continue
        raise AssertionError(f"hostile close accepted: {identifier}")
    require(len(rejected) == 22, "hostile close census")
    return rejected


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true")
    arguments = parser.parse_args()
    result = reconstruct()
    validate_close(result)
    hostiles = hostile_closes(result)
    result["hostile_mutations"] = {
        "rejected": len(hostiles),
        "total": len(hostiles),
        "all_rejected": True,
        "results": hostiles,
    }
    if arguments.write:
        OUTPUT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="ascii")
    print("PASS frozen closing reconstruction: 11 pins and protected canonical V10")
    print(f"PASS {len(hostiles)}/{len(hostiles)} hostile closing mutations rejected")
    print("ACCEPT Q0 NULL / Q1 DENIED / STALLED / STOP / NONE")


if __name__ == "__main__":
    main()
