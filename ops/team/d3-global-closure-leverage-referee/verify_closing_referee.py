#!/usr/bin/env python3
"""Independent fail-closed referee for the frozen D3 leverage audit."""

from __future__ import annotations

import copy
import json
import os
from pathlib import Path
import subprocess


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
CYCLE = ROOT / "ops/research-team/cycles/2026-09-01-d3-global-master-closure-theorem-leverage-audit-gate1"
RESULT_PATH = HERE / "RESULT.json"
REPLAY_PATH = HERE / "CLEAN_REPLAY.json"
FROZEN_COMMIT = "2426a20de8ad31d4b91e1a5ef337e99535b41f8b"
FROZEN_TREE = "98d2ab0262df1fe50ad6c6052ea77e8bb58989a2"
BASE_COMMIT = "98ed8d36f08f13305d226d3d3770e71542a0a408"
BASE_TREE = "52a03a10b62e54a9ff5aa4e59dbbc2af9a69eeab"


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def git(*args: str) -> str:
    return subprocess.run(
        ["git", *args], cwd=ROOT, check=True, capture_output=True,
        text=True, encoding="utf-8"
    ).stdout.strip()


def validate_sources() -> dict:
    ledger = load(ROOT / "ai/omreal/data/DIAG3_RESEARCH_DECISION_LEDGER.json")
    require(ledger["theorem"]["score"] == "2/9", "ledger score")
    require(ledger["theorem"]["proved_diagonals"] == [1, 2], "proved diagonals")
    obligations = {row["id"]: row for row in ledger["invariant_obligations"]}
    pair = obligations["diag3_pair_hc1"]
    triple = obligations["diag3_triple_hc0"]
    require(pair["status"] == triple["status"] == "OPEN", "D3 invariants")
    require((pair["current_global_adjacencies"], pair["current_global_strict_closure_pairs"],
             pair["current_global_strict_closure_triples"], pair["current_parent_infinity_cells"])
            == (0, 0, 0, 0), "global interface")
    require((triple["universe_count"], triple["proved_noncompact_count"], triple["unresolved_count"])
            == (79102449, 77940147, 1162302), "triple accounting")
    require(79102449 - 77940147 == 1162302, "triple identity")

    compact = load(ROOT / "ai/omreal/data/DIAG3_PAIR_GLOBAL_row2599_compactification_atlas.json")
    require((compact["chart_atlas"]["chart_count"], compact["chart_atlas"]["ordered_transition_count"])
            == (64, 4096), "compactification")
    face = load(ROOT / "ai/omreal/data/DIAG3_PAIR_GLOBAL_row2599_face_bernstein_atlas.json")
    require((face["candidate_count"], face["face_count"], face["factor_face_pair_count"])
            == (17824, 3375, 60156000), "face atlas")
    require(sum(face["state_counts"].values()) == 60156000, "face-state partition")
    parent = load(ROOT / "ai/omreal/data/DIAG3_PAIR_GLOBAL_row2599_parent_face_gate.json")
    require((parent["excluded_support_face_count"], parent["nonexcluded_support_face_count"],
             parent["remaining_candidate_factor_face_pair_count"],
             parent["remaining_mixed_residual_restriction_count"])
            == (3364, 11, 196064, 70218), "parent gate")

    gate = load(ROOT / "ai/omreal/data/DIAG3_PAIR_GLOBAL_FOUR_SUPPORT_GATE.json")
    require(gate["scope"]["global_parent_cell_coverage"] == "NOT_CLAIMED", "gate scope")
    require(gate["combined_compression"]["distinct_active_walls_after_positive_quotient"] == 22,
            "active wall count")
    open_lift = load(ROOT / "ai/omreal/data/DIAG3_PAIR_GLOBAL_FOUR_SUPPORT_OPEN_CELL_V_LIFT.json")
    algebraic_u = load(ROOT / "ai/omreal/data/DIAG3_PAIR_GLOBAL_FOUR_SUPPORT_COEFFICIENT_ENDPOINT_U_SECTION_V_LIFT.json")
    algebraic_t = load(ROOT / "ai/omreal/data/DIAG3_PAIR_GLOBAL_FOUR_SUPPORT_ALGEBRAIC_T_COEFFICIENT_ENDPOINT_U_POINT_V_LIFT.json")
    base_parts = (open_lift["open_cell_v_lift"]["open_base_cells"],
                  algebraic_u["cumulative_open_t_algebraic_u_section_v_lift"]["completed_sections"],
                  algebraic_t["cumulative_algebraic_t_v_lift"]["base_cells"])
    lift_parts = (open_lift["open_cell_v_lift"]["lifted_cells"],
                  algebraic_u["cumulative_open_t_algebraic_u_section_v_lift"]["lifted_cells"],
                  algebraic_t["cumulative_algebraic_t_v_lift"]["lifted_cells"])
    require(base_parts == (133828, 132134, 261571) and sum(base_parts) == 527533,
            "base-cell census")
    require(lift_parts == (4496636, 4047846, 8390619) and sum(lift_parts) == 16935101,
            "local lifted-cell census")
    require(algebraic_t["scope"]["global_gluing_and_closure_data"] == "NOT_CLAIMED",
            "algebraic-t scope")

    closure = load(ROOT / "ai/omreal/data/DIAG3_PAIR_GLOBAL_CLOSURE_OPEN_OBJECT.json")
    obs = closure["observations"]
    require((obs["atlas_assignment_count"], obs["certified_adjacency_edges_between_distinct_atlas_charts"],
             obs["certified_global_strict_closure_pairs"], obs["certified_global_strict_closure_triples"],
             obs["certified_parent_infinity_cells"]) == (97224, 0, 0, 0, 0), "closure open object")
    pilot = load(ROOT / "ai/omreal/data/DIAG3_COMPONENT_COSHEAF_PILOT.json")
    require(pilot["status"] == "BOUNDED_NO_GO", "cosheaf result")
    require(pilot["decision"]["promote_existing_manifests_as_master_closure_replacement"] is False,
            "cosheaf promotion scope")
    require(pilot["two_support_input_audit"]["all_inputs_missing_at_least_one_required_field"] is True,
            "cosheaf input contract")
    return {"base_cells": sum(base_parts), "lifted_cells": sum(lift_parts),
            "algebraic_t_lifted_cells": lift_parts[2], "triple_unresolved": 1162302}


def validate_result(result: dict) -> None:
    require(result["frozen_candidate"] == {"commit": FROZEN_COMMIT, "tree": FROZEN_TREE},
            "frozen candidate")
    require(result["canonical_base"] == {"commit": BASE_COMMIT, "tree": BASE_TREE}, "base")
    require(result["verdict"] == "ACCEPT_FROZEN_CANDIDATE_FAIL_CLOSED", "verdict")
    require(result["trajectory_classification"] == "STALLED", "trajectory")
    require(result["strategy_action"] == "STOP", "strategy action")
    require(result["ledger"] == {"opening": "2/9", "closing": "2/9", "delta": "0/9"}, "ledger")
    require(result["opening_vector"] == ["2/9", 1, "diag3_pair_hc1_AND_diag3_triple_hc0", 7,
                                          "UNKNOWN", "UNKNOWN", 3, 6], "opening vector")
    require(result["comparable_closing_vectors"] == [
        ["2/9", 1, "diag3_pair_hc1_AND_diag3_triple_hc0", 7, "UNKNOWN", "UNKNOWN", 1, 4],
        ["2/9", 1, "diag3_pair_hc1_AND_diag3_triple_hc0", 7, "UNKNOWN", "UNKNOWN", 2, 5],
        ["2/9", 1, "diag3_pair_hc1_AND_diag3_triple_hc0", 7, "UNKNOWN", "UNKNOWN", 3, 6],
    ], "comparable vectors")
    require(result["checkpoint_vector"] == result["opening_vector"], "checkpoint vector")
    require(result["closing_vector"] == ["2/9", 1, "diag3_pair_hc1_AND_diag3_triple_hc0", 7,
                                          "UNKNOWN", "UNKNOWN", 4, 7], "closing vector")
    require(result["minimum_acceptable_delta_met"] is False, "minimum delta")
    require(result["automatic_reset"] == {"fired": True, "same_route_continue_allowed": False,
                                            "action": "STOP"}, "automatic reset")
    require(len(result["obligations"]) == 7, "obligation count")
    require(all(row["opening"] == row["closing"] for row in result["obligations"]), "obligations unchanged")
    require([row["id"] for row in result["routes"]] == [
        "DIRECT_GLOBAL_MASTER_CLOSURE", "COMPONENT_COSHEAF_STRUCTURAL_COMPRESSION",
        "EXACT_COUNTEREXAMPLE_OR_RETIREMENT", "D9_B_UV_01_LOW_LEVERAGE_BASELINE"], "route order")
    require(not any(row["construction_eligible"] for row in result["routes"]), "route eligibility")
    require(result["successor_bar"] == {
        "theorem_level_quantifier_attachment_proved": False,
        "certified_finite_exhaustive_progress_measure_proved": False,
        "preregistered_bounded_decrease_proved": False,
        "eligible_construction_targets": 0,
        "selected_construction_target": "NONE",
        "selected_successor": "NONE / STOP",
    }, "successor bar")
    require(result["independent_reconstruction"] == validate_sources(), "source reconstruction")
    require(result["clean_replay"]["six_required_gates_passed"] is True, "six-gate replay")
    require(result["clean_replay"]["hardlink_identity_collisions"] == 0, "no-hardlink replay")
    require(result["hostile_mutations"]["required"] >= 20, "hostile minimum")
    require(result["hostile_mutations"]["rejected"] == result["hostile_mutations"]["required"],
            "hostile result")


def validate_cycle() -> None:
    opening = load(CYCLE / "OPENING_AUDIT.json")
    checkpoint = load(CYCLE / "MID_CYCLE_CHECKPOINT.json")
    closing = load(CYCLE / "CLOSING_CANDIDATE.json")
    require(opening["base_revision"] == checkpoint["base_revision"] == closing["base_revision"] == BASE_COMMIT,
            "cycle base revision")
    require(opening["base_tree"] == checkpoint["base_tree"] == closing["base_tree"] == BASE_TREE,
            "cycle base tree")
    require(closing["opening_ledger"] == closing["closing_ledger"] == "2/9", "cycle ledger")
    require(closing["ledger_delta"] == "0/9" and closing["theorem_promotion"] == "NONE", "cycle delta")
    require(closing["trajectory_classification"] == "STALLED", "cycle trajectory")
    require(checkpoint["minimum_acceptable_delta_reachable_inside_remaining_ceiling"] is False,
            "checkpoint reachability")
    require(checkpoint["checkpoint_decision"]["stop_discovery"] is True, "checkpoint stop")
    require(sum(row["hostile_mutations_rejected"] for row in checkpoint["lane_verdicts"]) == 100,
            "pre-referee hostile census")
    require(closing["successor_bar"]["eligible_route_count"] == 0, "candidate successor count")
    require(closing["successor_bar"]["selected_successor"] == "NONE / STOP", "candidate successor")
    require(git("rev-parse", f"{FROZEN_COMMIT}^{{tree}}") == FROZEN_TREE, "frozen tree")


def validate_replay(replay: dict) -> None:
    require(replay["clone"]["no_hardlinks_flag"] is True, "clone flag")
    require(replay["detached_head"] == FROZEN_COMMIT and replay["detached_tree"] == FROZEN_TREE,
            "replay head/tree")
    require(len(replay["required_verifiers"]) == 6, "six required verifiers")
    require(all(row["exit_code"] == 0 and row["status"] == "PASS" for row in replay["required_verifiers"]),
            "required replay status")
    require(replay["hardlink_check"]["matching_files_checked"] == 7, "hardlink file count")
    require(replay["hardlink_check"]["same_identity_count"] == 0, "hardlink identity")
    require(all(not row["same_identity"] and row["source_nlink"] == row["clone_nlink"] == 1
                for row in replay["hardlink_check"]["files"]), "hardlink details")
    require(replay["optional_legacy_replay"]["acceptance_dependency"] is False,
            "optional replay independence")


def hostile_canaries(result: dict) -> int:
    mutations = [
        lambda x: x["frozen_candidate"].__setitem__("commit", BASE_COMMIT),
        lambda x: x["frozen_candidate"].__setitem__("tree", BASE_TREE),
        lambda x: x.__setitem__("verdict", "PROMOTE"),
        lambda x: x.__setitem__("trajectory_classification", "CONVERGING"),
        lambda x: x.__setitem__("strategy_action", "CONTINUE"),
        lambda x: x["ledger"].__setitem__("closing", "3/9"),
        lambda x: x["ledger"].__setitem__("delta", "1/9"),
        lambda x: x["opening_vector"].__setitem__(3, 6),
        lambda x: x.__setitem__("checkpoint_vector", ["2/9", 1, "x", 6, 0, "1/1", 3, 6]),
        lambda x: x["closing_vector"].__setitem__(3, 6),
        lambda x: x["closing_vector"].__setitem__(4, 527533),
        lambda x: x["closing_vector"].__setitem__(5, "527533/527533"),
        lambda x: x.__setitem__("minimum_acceptable_delta_met", True),
        lambda x: x["automatic_reset"].__setitem__("fired", False),
        lambda x: x["automatic_reset"].__setitem__("same_route_continue_allowed", True),
        lambda x: x["automatic_reset"].__setitem__("action", "PIVOT_CONSTRUCTION"),
        lambda x: x["obligations"].pop(),
        lambda x: x["obligations"][0].__setitem__("closing", "PROVED"),
        lambda x: x["routes"].pop(),
        lambda x: x["routes"][0].__setitem__("construction_eligible", True),
        lambda x: x["successor_bar"].__setitem__("theorem_level_quantifier_attachment_proved", True),
        lambda x: x["successor_bar"].__setitem__("certified_finite_exhaustive_progress_measure_proved", True),
        lambda x: x["successor_bar"].__setitem__("preregistered_bounded_decrease_proved", True),
        lambda x: x["successor_bar"].__setitem__("eligible_construction_targets", 1),
        lambda x: x["successor_bar"].__setitem__("selected_construction_target", "DIRECT"),
        lambda x: x["successor_bar"].__setitem__("selected_successor", "DIRECT / CONTINUE"),
        lambda x: x["independent_reconstruction"].__setitem__("base_cells", 527532),
        lambda x: x["independent_reconstruction"].__setitem__("lifted_cells", 16935100),
        lambda x: x["clean_replay"].__setitem__("six_required_gates_passed", False),
        lambda x: x["clean_replay"].__setitem__("hardlink_identity_collisions", 1),
    ]
    rejected = 0
    for mutate in mutations:
        candidate = copy.deepcopy(result)
        mutate(candidate)
        try:
            validate_result(candidate)
        except (AssertionError, KeyError):
            rejected += 1
        else:
            raise AssertionError("hostile mutation accepted")
    return rejected


def main() -> None:
    result = load(RESULT_PATH)
    replay = load(REPLAY_PATH)
    validate_cycle()
    validate_replay(replay)
    validate_result(result)
    rejected = hostile_canaries(result)
    require(rejected == result["hostile_mutations"]["required"], "hostile declared count")
    print(
        "PASS frozen D3 closing referee: candidate 2426a20 / tree 98d2ab0; "
        "2/9 -> 2/9; 7 obligations; UNKNOWN/UNKNOWN; 0 targets; "
        f"STALLED / STOP / NONE; {rejected}/{rejected} hostiles rejected"
    )


if __name__ == "__main__":
    main()
