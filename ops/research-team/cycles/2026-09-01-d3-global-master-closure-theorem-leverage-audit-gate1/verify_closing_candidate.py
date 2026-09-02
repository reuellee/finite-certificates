#!/usr/bin/env python3
"""Verify the frozen D3 leverage checkpoint and closing candidate."""

from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[4]
CYCLE = Path(__file__).resolve().parent


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def validate(checkpoint: dict, closing: dict) -> None:
    base = "98ed8d36f08f13305d226d3d3770e71542a0a408"
    tree = "52a03a10b62e54a9ff5aa4e59dbbc2af9a69eeab"
    require(checkpoint["base_revision"] == closing["base_revision"] == base, "base revision")
    require(checkpoint["base_tree"] == closing["base_tree"] == tree, "base tree")
    require(checkpoint["integrated_lane_head"] == closing["integrated_evidence_revision"], "integrated revision")
    require(checkpoint["integrated_lane_tree"] == closing["integrated_evidence_tree"], "integrated tree")

    opening = ["2/9", 1, "diag3_pair_hc1_AND_diag3_triple_hc0", 7, "UNKNOWN", "UNKNOWN", 3, 6]
    closing_vector = ["2/9", 1, "diag3_pair_hc1_AND_diag3_triple_hc0", 7, "UNKNOWN", "UNKNOWN", 4, 7]
    require(checkpoint["opening_vector"] == checkpoint["checkpoint_vector"] == opening, "checkpoint vector")
    require(closing["opening_vector"] == opening, "closing opening vector")
    require(closing["closing_vector"] == closing_vector, "closing vector")
    require(checkpoint["minimum_acceptable_delta_reachable_inside_remaining_ceiling"] is False, "checkpoint reachability")
    require(checkpoint["checkpoint_decision"] == {
        "stop_discovery": True,
        "construction_started": False,
        "resource_ceiling_enlarged": False,
        "same_route_continue_allowed": False,
        "automatic_reset_fired": True,
        "required_close": "STALLED__NONE_STOP",
    }, "checkpoint decision")
    require(sum(row["hostile_mutations_rejected"] for row in checkpoint["lane_verdicts"]) == 100, "hostile total")

    require(closing["opening_ledger"] == closing["closing_ledger"] == "2/9", "ledger")
    require(closing["ledger_delta"] == "0/9" and closing["theorem_promotion"] == "NONE", "ledger delta")
    require(closing["minimum_acceptable_delta_met"] is False, "minimum delta")
    require(closing["trajectory_classification"] == "STALLED", "trajectory")
    require(closing["automatic_strategy_reset"]["fired"] is True, "automatic reset")
    require(closing["automatic_strategy_reset"]["same_route_continue_allowed"] is False, "same-route continuation")
    require(closing["automatic_strategy_reset"]["action"] == "STOP", "reset action")
    require(len(closing["obligation_delta"]) == 7, "obligation count")
    require(all(row["delta"] in ("UNCHANGED", 0) for row in closing["obligation_delta"]), "obligation delta")
    require([row["route"] for row in closing["route_dispositions"]] == [
        "DIRECT_GLOBAL_MASTER_CLOSURE",
        "COMPONENT_COSHEAF_STRUCTURAL_COMPRESSION",
        "EXACT_COUNTEREXAMPLE_OR_RETIREMENT",
        "D9_B_UV_01_LOW_LEVERAGE_BASELINE",
    ], "route order")
    require(not any(row["construction_eligible"] for row in closing["route_dispositions"]), "route eligibility")
    bar = closing["successor_bar"]
    require(bar == {
        "theorem_level_quantifier_attachment_proved": False,
        "certified_finite_exhaustive_progress_measure_proved": False,
        "preregistered_bounded_decrease_proved": False,
        "eligible_route_count": 0,
        "selected_construction_target": "NONE",
        "selected_successor": "NONE / STOP",
    }, "successor bar")
    require(closing["construction_started"] is False, "construction scope")
    require(len(closing["nonconsequences"]) == 10, "nonconsequences")

    require(set(closing["evidence_pins"]) == {
        "ops/team/d3-global-closure-leverage-audit/RESULT.json",
        "ops/team/d3-global-closure-leverage-audit/verify_strategy_audit.py",
        "ops/team/d3-global-closure-leverage-falsifier/RESULT.json",
        "ops/team/d3-global-closure-leverage-falsifier/verify_d3_global_closure_leverage_falsifier.py",
        "ops/team/d3-global-closure-leverage-certificate/RESULT.json",
        "ops/team/d3-global-closure-leverage-certificate/verify_certificate.py",
    }, "evidence pin set")
    for relative, digest in closing["evidence_pins"].items():
        path = ROOT / relative
        require(path.is_file(), f"missing evidence {relative}")
        require(sha256(path) == digest, f"evidence drift {relative}")


def hostile_canaries(checkpoint: dict, closing: dict) -> int:
    mutations = [
        lambda c: c.__setitem__("closing_ledger", "3/9"),
        lambda c: c.__setitem__("ledger_delta", "1/9"),
        lambda c: c.__setitem__("trajectory_classification", "CONVERGING"),
        lambda c: c.__setitem__("minimum_acceptable_delta_met", True),
        lambda c: c["closing_vector"].__setitem__(3, 6),
        lambda c: c["closing_vector"].__setitem__(4, 527533),
        lambda c: c["closing_vector"].__setitem__(5, "527533/527533"),
        lambda c: c["automatic_strategy_reset"].__setitem__("fired", False),
        lambda c: c["automatic_strategy_reset"].__setitem__("same_route_continue_allowed", True),
        lambda c: c["successor_bar"].__setitem__("eligible_route_count", 1),
        lambda c: c["successor_bar"].__setitem__("selected_construction_target", "DIRECT"),
        lambda c: c.__setitem__("construction_started", True),
        lambda c: c["route_dispositions"][0].__setitem__("construction_eligible", True),
        lambda c: c["obligation_delta"][0].__setitem__("delta", "CLOSED"),
        lambda c: c["evidence_pins"].pop("ops/team/d3-global-closure-leverage-certificate/RESULT.json"),
    ]
    rejected = 0
    for mutate in mutations:
        candidate = copy.deepcopy(closing)
        mutate(candidate)
        try:
            validate(checkpoint, candidate)
        except (AssertionError, KeyError):
            rejected += 1
        else:
            raise AssertionError("hostile closing mutation accepted")
    return rejected


def main() -> None:
    checkpoint = load(CYCLE / "MID_CYCLE_CHECKPOINT.json")
    closing = load(CYCLE / "CLOSING_CANDIDATE.json")
    validate(checkpoint, closing)
    rejected = hostile_canaries(checkpoint, closing)
    print(
        "PASS D3 closing candidate: 2/9 -> 2/9; 7 obligations; "
        f"UNKNOWN global residual; 0 eligible successors; STALLED / STOP; {rejected}/15 hostiles rejected"
    )


if __name__ == "__main__":
    main()
