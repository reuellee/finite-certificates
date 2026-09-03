#!/usr/bin/env python3
"""Frozen-input independent verifier for the D3 saturation Q0 gate.

The verifier reads producer and falsifier data directly from the frozen Git
commit.  It imports neither lane's code and cannot emit an acceptance token
for the guarded Q1 executor.  The canonical parent-wall source is imported
only after its frozen bytes are checked.
"""

from __future__ import annotations

import argparse
import ast
from copy import deepcopy
from hashlib import sha256
import json
from pathlib import Path
import subprocess
import sys


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
FROZEN_COMMIT = "2df3285c19b0c65127bd0acd79df2cc57f0d7752"
FROZEN_TREE = "67bc7fa65db3d45f42edf724d7c7f69cef8edbfc"
CONSTRUCTOR_COMMIT = "97787bed0afae6a2f7cb7d2edf9df4f54bbe97f9"
CONTRACT = "ops/team/d3-triple-critical-saturation-constructor/SATURATION_CONTRACT.json"
PRODUCER_RESULT = "ops/team/d3-triple-critical-saturation-constructor/RESULT.json"
RUNNER = "ops/team/d3-triple-critical-saturation-constructor/run_q1_saturation.py"
FALSIFIER_RESULT = "ops/team/d3-triple-critical-saturation-falsifier/RESULT.json"
SYSTEM = "ai/omreal/data/DIAG3_triple_fullspace_critical_h1.json"
WALL_SOURCE = "ai/omreal/DIAG2_PIVOT_LABELED_PAIR_ORBITS_VERIFY.py"
OPENING = "ops/research-team/cycles/2026-09-02-d3-triple-critical-saturation-component-gate1/OPENING_STATE.json"
OUTPUT = HERE / "RESULT.json"


class Reject(AssertionError):
    pass


def require(condition: bool, marker: str) -> None:
    if not condition:
        raise Reject(marker)


def git(*arguments: str, binary: bool = False):
    return subprocess.check_output(
        ["git", *arguments], cwd=ROOT, text=not binary
    )


def frozen_bytes(path: str) -> bytes:
    return git("show", f"{FROZEN_COMMIT}:{path}", binary=True)


def digest(data: bytes) -> str:
    return sha256(data).hexdigest()


def canonical_digest(value) -> str:
    return digest(json.dumps(value, sort_keys=True, separators=(",", ":")).encode("ascii"))


def parse_json(path: str) -> tuple[bytes, dict]:
    data = frozen_bytes(path)
    return data, json.loads(data.decode("ascii"))


def sparse(polynomial: dict) -> list[list]:
    return [[int(coefficient), list(monomial)] for monomial, coefficient in sorted(polynomial.items()) if coefficient]


def polynomial_degree(terms: list[list]) -> int | None:
    return max((sum(monomial) for _coefficient, monomial in terms), default=None)


def on_coordinate_space(terms: list[list], zero_indices: set[int]) -> bool:
    return all(any(monomial[index] for index in zero_indices) for _coefficient, monomial in terms)


def no_scratch_guard(source: str) -> bool:
    tree = ast.parse(source)
    forbidden_names = {"disk_usage", "getsize", "rglob", "scratch_bytes", "scratch_gib"}
    seen = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Name):
            seen.add(node.id)
        elif isinstance(node, ast.Attribute):
            seen.add(node.attr)
    return not bool(seen & forbidden_names)


def reconstruct() -> dict:
    require(git("rev-parse", FROZEN_COMMIT).strip() == FROZEN_COMMIT, "frozen commit")
    require(git("rev-parse", f"{FROZEN_COMMIT}^{{tree}}").strip() == FROZEN_TREE, "frozen tree")
    require(git("rev-parse", f"{FROZEN_COMMIT}^").strip() == CONSTRUCTOR_COMMIT, "frozen parent")

    contract_bytes, contract = parse_json(CONTRACT)
    producer_bytes, producer = parse_json(PRODUCER_RESULT)
    runner_bytes = frozen_bytes(RUNNER)
    runner_text = runner_bytes.decode("ascii")
    falsifier_bytes, falsifier = parse_json(FALSIFIER_RESULT)
    system_bytes, system = parse_json(SYSTEM)
    opening_bytes, opening = parse_json(OPENING)
    wall_source_bytes = frozen_bytes(WALL_SOURCE)

    body = deepcopy(contract)
    seal = body.pop("semantic_sha256")
    require(seal == canonical_digest(body), "contract semantic seal")
    require(contract["source_ideal"]["artifact_sha256"] == digest(system_bytes), "system byte pin")
    require(contract["source_ideal"]["artifact_semantic_sha256"] == canonical_digest(system), "system semantic pin")
    require(opening["base"]["ledger"] == "2/9", "opening ledger")
    require(opening["q0"]["status"] == "OPEN", "opening Q0")
    require(opening["q1"]["status"] == "DENIED_PENDING_Q0", "opening Q1")

    local_wall_source = ROOT / WALL_SOURCE
    require(local_wall_source.read_bytes() == wall_source_bytes, "wall source working-tree drift")
    sys.path.insert(0, str(ROOT / "ai" / "omreal"))
    import DIAG2_PIVOT_LABELED_PAIR_ORBITS_VERIFY as labeled  # noqa: E402

    expected_walls = [
        (label, sparse(polynomial), int(sign))
        for label, polynomial, sign in labeled.parent_bracket_factors()
    ]
    stages = contract["saturation_contract"]["stages"]
    require(len(expected_walls) == len(stages) == 62, "wall count")
    require(contract["saturation_contract"]["ordered"] is True, "ordered")
    require(contract["saturation_contract"]["anonymous_product_saturation_used"] is False, "anonymous product")
    materialized_attachment_stages = 0
    for index, (stage, expected) in enumerate(zip(stages, expected_walls, strict=True)):
        label, terms, sign = expected
        require(stage["stage_index"] == index, f"stage {index} index")
        require(stage["parent_bracket_label"] == label, f"stage {index} label")
        require(stage["sparse_polynomial"] == terms, f"stage {index} polynomial")
        require(stage["normalization_sign"] == sign, f"stage {index} sign")
        require(stage["attachment_class"] == "PARENT_WALL", f"stage {index} class")
        attachment = stage["component_attachment_contract"]
        require(
            attachment["set_identity"] == f"V(J_{index:02d})=V(J_{index + 1:02d}) union V(A_{index:02d})",
            f"stage {index} identity",
        )
        if attachment.get("removed_components") and attachment.get("exact_reduction_certificates"):
            materialized_attachment_stages += 1

    equations = system["equations"]
    require(len(equations) == 59, "formal generators")
    require(sum(bool(row["terms"]) for row in equations) == 55, "nonzero generators")
    require(sum(len(row["terms"]) for row in equations) == 14_741, "source terms")
    require(max(polynomial_degree(row["terms"]) or -1 for row in equations) == 8, "source degree")

    wall_map = {label: terms for label, terms, _sign in expected_walls}
    variable_index = {name: index for index, name in enumerate("abcdefghi")}
    expected_canaries = [(set("abcdf"), "1346"), (set("bcdef"), "1247")]
    canaries = contract["known_fourspace_canaries"]
    require(len(canaries) == 2, "four-space count")
    for canary, (coordinate_ideal, discriminating_wall) in zip(canaries, expected_canaries, strict=True):
        require(set(canary["coordinate_ideal"]) == coordinate_ideal, "coordinate ideal")
        indices = {variable_index[name] for name in coordinate_ideal}
        require(all(on_coordinate_space(row["terms"], indices) for row in equations), "four-space source vanishing")
        require(canary["discriminating_isolated_canary"]["parent_wall"] == discriminating_wall, "discriminating wall")
        require(on_coordinate_space(wall_map[discriminating_wall], indices), "wall containment")
    require(len(contract["hostile_boundary_canaries"]) == 3, "boundary canary count")
    require(all(row["accepted"] is False for row in contract["hostile_boundary_canaries"]), "false infinity")

    forecast = contract["numeric_local_resource_forecast"]
    require(forecast["ordered_saturation_stages"] == 62, "forecast stages")
    require(forecast["stage_wall_seconds"] == 62 * forecast["per_stage_wall_seconds"], "stage arithmetic")
    require(
        forecast["projected_total_wall_seconds"]
        == forecast["stage_wall_seconds"] + forecast["preflight_and_certificate_seconds"],
        "total arithmetic",
    )
    remaining_seconds = forecast["cycle_ceiling_wall_seconds"] - forecast["projected_total_wall_seconds"]
    require(remaining_seconds == 1_800, "remaining budget")

    unresolved_q1 = [
        "exact final dimension or emptiness",
        "complete real-root isolation",
        "parent-chamber classification",
        "sound true-parent-infinity continuation",
        "complete S8 orbit transfer",
    ]
    require(materialized_attachment_stages == 0, "unexpected materialized attachments")
    require(forecast["empirical_exact_cas_calibration_available"] is False, "unexpected solve calibration")
    require(forecast["confidence"] == "LOW", "unexpected forecast confidence")
    require(no_scratch_guard(runner_text), "unexpected scratch guard")
    require(
        "SATURATION_COMPLETE_Q1_STILL_REQUIRES_DIMENSION_REAL_ROOT_AND_ATTACHMENT_CHECKS" in runner_text,
        "runner endpoint marker",
    )
    require(producer["accepted"] is False and producer["q1_status"].startswith("DENIED"), "producer gate")
    require(falsifier["verdict"] == "Q0_NULL_MINIMUM_DECREASE_NOT_REACHABLE", "falsifier verdict")
    require(falsifier["hostile_mutations"]["rejected"] == 27, "falsifier hostiles")

    return {
        "format": "d3-triple-critical-saturation-independent-q0-verification-v1",
        "track_id": "d3-triple-critical-saturation-independent-verifier",
        "status": "PASS",
        "verdict": "Q0_NULL_INDEPENDENTLY_CONFIRMED",
        "accepted": False,
        "q0_status": "NULL",
        "q1_status": "DENIED",
        "independent_verifier": True,
        "frozen_evidence_commit": FROZEN_COMMIT,
        "frozen_evidence_tree": FROZEN_TREE,
        "inputs": {
            "contract": {"bytes": len(contract_bytes), "sha256": digest(contract_bytes)},
            "producer_result": {"bytes": len(producer_bytes), "sha256": digest(producer_bytes)},
            "runner": {"bytes": len(runner_bytes), "sha256": digest(runner_bytes)},
            "falsifier_result": {"bytes": len(falsifier_bytes), "sha256": digest(falsifier_bytes)},
            "system": {"bytes": len(system_bytes), "sha256": digest(system_bytes)},
            "opening": {"bytes": len(opening_bytes), "sha256": digest(opening_bytes)},
            "wall_source": {"bytes": len(wall_source_bytes), "sha256": digest(wall_source_bytes)},
        },
        "independent_reconstruction": {
            "formal_source_generators": 59,
            "nonzero_source_generators": 55,
            "source_sparse_terms": 14_741,
            "maximum_source_degree": 8,
            "ordered_parent_wall_stages": 62,
            "materialized_component_attachment_stages": materialized_attachment_stages,
            "known_fourspace_canaries": 2,
            "false_infinity_canaries": 3,
            "forecast_saturation_seconds": forecast["projected_total_wall_seconds"],
            "ceiling_seconds": forecast["cycle_ceiling_wall_seconds"],
            "unallocated_seconds_after_saturation_forecast": remaining_seconds,
            "unforecasted_q1_obligations": unresolved_q1,
            "scratch_ceiling_enforced_by_runner": False,
        },
        "first_failed_obligation": "END_TO_END_EXECUTABLE_COMPONENT_DECORATED_CONTRACT_WITH_CEILING_BOUND_Q1_PATH",
        "mid_cycle": {
            "minimum_decrease_still_reachable_inside_fixed_ceiling": False,
            "action": "FREEZE_Q0_NULL_AND_STOP",
            "reason": "The only numeric forecast consumes 210 of 240 minutes on saturation, is uncalibrated, omits five Q1 endpoint obligations, and lacks scratch-ceiling enforcement.",
        },
        "accounting": {
            "theorem_ledger_before": "2/9",
            "theorem_ledger_after": "2/9",
            "triple_source_residual_before": 1_162_302,
            "triple_source_residual_after": 1_162_302,
            "theorem_credit": "NONE",
            "trajectory": "STALLED",
            "strategy_action": "STOP",
        },
        "scope": [
            "Independent machine verification, not human review.",
            "Imports no constructor or falsifier code and reads their artifacts from frozen Git.",
            "No raw research saturation or RUR job was run because Q1 remains denied.",
            "Does not disprove the mathematical route or change any theorem/component/row claim.",
        ],
    }


def validate_decision(value: dict) -> None:
    require(value["accepted"] is False, "false Q0 acceptance")
    require(value["q0_status"] == "NULL", "Q0 status")
    require(value["q1_status"] == "DENIED", "Q1 status")
    require(value["independent_reconstruction"]["ordered_parent_wall_stages"] == 62, "stage claim")
    require(value["independent_reconstruction"]["materialized_component_attachment_stages"] == 0, "attachment claim")
    require(value["independent_reconstruction"]["unallocated_seconds_after_saturation_forecast"] == 1_800, "remaining time")
    require(value["independent_reconstruction"]["scratch_ceiling_enforced_by_runner"] is False, "scratch claim")
    require(len(value["independent_reconstruction"]["unforecasted_q1_obligations"]) == 5, "Q1 obligation count")
    require(value["mid_cycle"]["minimum_decrease_still_reachable_inside_fixed_ceiling"] is False, "mid-cycle reachability")
    require(value["mid_cycle"]["action"] == "FREEZE_Q0_NULL_AND_STOP", "mid-cycle action")
    require(value["accounting"]["theorem_ledger_before"] == value["accounting"]["theorem_ledger_after"] == "2/9", "ledger")
    require(value["accounting"]["triple_source_residual_before"] == value["accounting"]["triple_source_residual_after"] == 1_162_302, "residual")
    require(value["accounting"]["theorem_credit"] == "NONE", "theorem credit")
    require(value["accounting"]["trajectory"] == "STALLED", "trajectory")
    require(value["accounting"]["strategy_action"] == "STOP", "action")


def hostile_decisions(result: dict) -> list[dict]:
    cases: list[tuple[str, dict]] = []

    def change(identifier: str, path: tuple[str, ...], replacement) -> None:
        candidate = deepcopy(result)
        cursor = candidate
        for key in path[:-1]:
            cursor = cursor[key]
        cursor[path[-1]] = replacement
        cases.append((identifier, candidate))

    change("accept_q0", ("accepted",), True)
    change("pass_q0", ("q0_status",), "ACCEPTED")
    change("activate_q1", ("q1_status",), "ACTIVE")
    change("stage_loss", ("independent_reconstruction", "ordered_parent_wall_stages"), 61)
    change("invent_attachment", ("independent_reconstruction", "materialized_component_attachment_stages"), 62)
    change("invent_budget", ("independent_reconstruction", "unallocated_seconds_after_saturation_forecast"), 14_400)
    change("invent_scratch_guard", ("independent_reconstruction", "scratch_ceiling_enforced_by_runner"), True)
    change("omit_q1_tail", ("independent_reconstruction", "unforecasted_q1_obligations"), [])
    change("claim_reachable", ("mid_cycle", "minimum_decrease_still_reachable_inside_fixed_ceiling"), True)
    change("continue_action", ("mid_cycle", "action"), "ACTIVATE_Q1")
    change("promote_opening_ledger", ("accounting", "theorem_ledger_before"), "3/9")
    change("promote_closing_ledger", ("accounting", "theorem_ledger_after"), "3/9")
    change("shrink_opening_residual", ("accounting", "triple_source_residual_before"), 1_162_301)
    change("shrink_closing_residual", ("accounting", "triple_source_residual_after"), 1_162_301)
    change("grant_credit", ("accounting", "theorem_credit"), "ROW_REMOVAL")
    change("claim_converging", ("accounting", "trajectory"), "CONVERGING")
    change("same_route_continue", ("accounting", "strategy_action"), "CONTINUE")
    change("unknown_trajectory", ("accounting", "trajectory"), "INFORMATIONAL")
    change("pivot_without_target", ("accounting", "strategy_action"), "PIVOT")
    change("retire_without_counterexample", ("accounting", "strategy_action"), "RETIRE")
    change("null_as_timeout", ("q0_status",), "TIMEOUT")
    change("q1_as_null", ("q1_status",), "NULL")

    rejected = []
    for identifier, candidate in cases:
        try:
            validate_decision(candidate)
        except (AssertionError, KeyError, TypeError):
            rejected.append({"id": identifier, "rejected": True})
            continue
        raise AssertionError(f"hostile decision accepted: {identifier}")
    require(len(rejected) == 22, "hostile decision census")
    return rejected


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true")
    arguments = parser.parse_args()
    result = reconstruct()
    validate_decision(result)
    hostiles = hostile_decisions(result)
    result["hostile_mutations"] = {
        "rejected": len(hostiles),
        "total": len(hostiles),
        "all_rejected": True,
        "results": hostiles,
    }
    if arguments.write:
        OUTPUT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="ascii")
    print("PASS frozen-input reconstruction: 7 pins, 62 walls, 5 canaries")
    print(f"PASS {len(hostiles)}/{len(hostiles)} hostile gate mutations rejected")
    print("Q0 NULL INDEPENDENTLY CONFIRMED; Q1 DENIED; STALLED / STOP")


if __name__ == "__main__":
    main()
