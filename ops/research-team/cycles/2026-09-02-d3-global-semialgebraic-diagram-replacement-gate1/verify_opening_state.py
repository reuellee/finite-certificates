#!/usr/bin/env python3
"""Fail-closed replay for the D3 global formula-diagram cycle opening."""

from __future__ import annotations

import copy
import hashlib
import json
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[4]
CYCLE = Path(__file__).resolve().parent
OPENING = CYCLE / "OPENING_STATE.json"
BASE = "0b8141223193c1ea2a1b4fce8e862466749f8b6b"
BASE_TREE = "faad8f9e78bd54435ee6212535198a08c0e3fe76"
VECTOR = [
    "2/9", 1, "diag3_pair_hc1_AND_diag3_triple_hc0", 7,
    "UNKNOWN", "UNKNOWN", 6, 9,
]


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def git_tree(revision: str) -> str:
    return subprocess.check_output(
        ["git", "rev-parse", f"{revision}^{{tree}}"],
        cwd=ROOT,
        text=True,
    ).strip()


def validate(opening: dict) -> None:
    require(opening["format"] == "d3-global-semialgebraic-diagram-replacement-opening-v1", "format")
    require(opening["cycle_id"] == "2026-09-02-d3-global-semialgebraic-diagram-replacement-gate1", "cycle id")
    require(opening["base_revision"] == BASE, "base revision")
    require(opening["base_tree"] == BASE_TREE, "base tree")
    require(git_tree(BASE) == BASE_TREE, "repository base tree")
    require(opening["branch"] == "research/local-d3-global-semialgebraic-replacement-gate1-20260902", "branch")

    canonical = opening["canonical_state"]
    expected_canonical = {
        "path": "ai/omreal/data/CANONICAL_RESEARCH_STATE_V9.json",
        "status": "STOPPED",
        "opening_ledger": "2/9",
        "proved_diagonals": [1, 2],
        "open_load_bearing_obligations": 7,
        "pair_residual": "UNKNOWN",
        "pair_coverage": "UNKNOWN",
        "same_blocker_streak": 6,
        "zero_ledger_streak": 9,
        "edited_by_cycle": False,
    }
    require(canonical == expected_canonical, "canonical opening summary")

    state = load(ROOT / canonical["path"])
    require(state["status"] == "STOPPED", "V9 status")
    require(state["theorem"]["score"] == "2/9", "V9 ledger")
    require(state["theorem"]["proved_diagonals"] == [1, 2], "V9 proved diagonals")
    require(state["open_obligations"]["load_bearing_count"] == 7, "V9 obligations")
    require(state["open_obligations"]["pair_residual"] == "UNKNOWN", "V9 pair residual")
    require(state["open_obligations"]["pair_coverage"] == "UNKNOWN", "V9 pair coverage")
    require(state["proof_distance"]["same_blocker_streak_closing"] == 6, "V9 blocker streak")
    require(state["proof_distance"]["zero_ledger_streak_closing"] == 9, "V9 ledger streak")
    require(state["process_gates"]["active_research_cycle_exists"] is False, "V9 predecessor active cycle")
    require(state["selected_next_target"]["construction_authorized"] is False, "V9 predecessor construction")

    reopen = opening["reopen_gate"]
    require(all(reopen[key] is True for key in (
        "new_explicit_user_authority",
        "new_governed_cycle",
        "predeclared_theorem_level_strict_decrease",
        "fresh_opening_audit",
        "independent_replay_required",
    )), "reopen gate")
    require(reopen["concrete_finite_route"] == "GLOBAL_CLOSED_FORMULA_DIAGRAM_PLUS_BASU_KARISANI_HOMOLOGICAL_2_SIMPLICIAL_REPLACEMENT", "finite route")

    strategy = opening["strategy"]
    require(strategy["action"] == "PIVOT", "strategy action")
    require(strategy["selected_target"] == "D3_B0_GLOBAL_SEMIALGEBRAIC_DIAGRAM_SIMPLICIAL_REPLACEMENT_GATE1", "selected target")
    require(strategy["selected_construction_count_at_opening"] == 0, "no Q1 construction at opening")
    require(strategy["qualification_active"] is True, "Q0 active")
    require(strategy["full_scope_construction_active"] is False, "Q1 closed")
    expected_routes = [
        "GLOBAL_CLOSED_FORMULA_DIAGRAM_HOMOLOGICAL_2_SIMPLICIAL_REPLACEMENT",
        "FRONTIER_CONDITION_CAD_DIRECT_MASTER_CLOSURE",
        "UNIVERSAL_MIXED_CARRIER_THEOREM_A",
        "TRIPLE_COMPONENT_ATLAS_OR_RESIDUAL_SAMPLING",
        "EXACT_COUNTEREXAMPLE_OR_ROUTE_RETIREMENT",
    ]
    require([row["id"] for row in strategy["route_tournament"]] == expected_routes, "route tournament")
    require(strategy["route_tournament"][0]["disposition"] == "SELECTED", "selected route")
    require(all(row["disposition"] != "SELECTED" for row in strategy["route_tournament"][1:]), "one selected route")

    distance = opening["proof_distance"]
    require(distance["opening_vector"] == VECTOR, "opening proof vector")
    require(distance["comparable_closing_vectors"] == [
        ["2/9", 1, "diag3_pair_hc1_AND_diag3_triple_hc0", 7, "UNKNOWN", "UNKNOWN", 4, 7],
        ["2/9", 1, "diag3_pair_hc1_AND_diag3_triple_hc0", 7, "UNKNOWN", "UNKNOWN", 5, 8],
        VECTOR,
    ], "comparable vectors")
    require(distance["minimum_acceptable_decrease"] == "FULL_SCOPE_SIMPLICIAL_PAIR_DIAGRAM_INDEPENDENT_HOMOLOGICAL_2_COMPARISON_AND_EXACT_ZERO_PAIR_KERNEL_CLOSE_DIAG3_PAIR_HC1_VIA_ALTERNATE_EDGE_AND_REDUCE_7_TO_AT_MOST_6", "minimum decrease")
    require(distance["qualification_has_theorem_credit"] is False, "Q0 credit")
    require(distance["partial_coverage_has_theorem_credit"] is False, "partial credit")
    require(distance["ledger_promotion_at_opening"] is False, "opening promotion")

    scope = opening["quantified_scope"]
    require(scope["realizable_unlabelled_parent_types"] == 2604, "parent count")
    for key in (
        "all_required_labelled_frames",
        "all_realization_components",
        "one_simultaneous_formula_diagram",
        "closed_compact_parent_and_true_infinity",
        "bad_pair_triple_union_and_filtration_terms",
        "exclusive_pair_relative_subspaces",
        "parent_and_witness_rank_distinct",
        "bypass_must_be_independently_proved_strictly_smaller",
    ):
        require(scope[key] is True, f"scope {key}")
    require(scope["alternate_pair_edge"] == "diag3_pair_formula_diagram_comparison", "alternate edge")
    require(scope["literal_O1_through_O5_claimed"] is False, "literal O1-O5 claim")
    require(scope["samples_or_local_atlases_sufficient"] is False, "sample scope")

    q0 = opening["q0"]
    require(q0["status"] == "ACTIVE", "Q0 status")
    require(q0["theorem_credit"] == "NONE", "Q0 theorem credit")
    require(q0["requires_formula_derived_output"] is True, "formula-derived output")
    require(q0["requires_independent_trace"] is True, "independent trace")
    require(len(q0["canaries"]) == 5, "Q0 canaries")
    require(q0["no_backend_failure_label"] == "NULL_NO_EXECUTABLE_REPLACEMENT_BACKEND", "backend null label")
    require((q0["laptop_hours"], q0["max_ram_gib"], q0["max_scratch_gib"], q0["max_repairs"]) == (8, 32, 25, 1), "Q0 ceiling")
    q1 = opening["q1"]
    require(q1 == {
        "status": "CLOSED_CONDITIONAL",
        "activation_requires_independent_q0_pass": True,
        "activation_requires_in_ceiling_n_over_n_forecast": True,
        "partial_results_are_progress": False,
    }, "Q1 gate")

    cloud = opening["cloud"]
    require(cloud["status"] == "AVAILABLE_NOT_ACTIVATED", "cloud status")
    require((cloud["provider"], cloud["project"], cloud["zone"]) == ("GCE", "project-ebd5a273-53ea-4c8b-81a", "us-central1-a"), "cloud target")
    require(cloud["instance_prefix"] == "d3-srep-gate1-20260902-", "cloud prefix")
    require((cloud["machine_type"], cloud["vcpus"], cloud["memory_gib"], cloud["boot_disk_gib"]) == ("n2-highcpu-16", 16, 16, 30), "cloud shape")
    require((cloud["max_elapsed_hours"], cloud["max_cycle_spend_usd"]) == (4, 5), "cloud ceiling")
    require(cloud["preemptible_quota_observed"] == 0, "spot quota")
    require(cloud["existing_instances_in_scope"] is False, "existing instances")
    require(cloud["known_existing_instance_out_of_scope"] == "claude-control", "known out-of-scope instance")
    require(cloud["must_delete_instance_and_disk"] is True, "cloud deletion")
    require(cloud["stopping_is_cleanup"] is False, "cloud stop semantics")
    require(cloud["activation_requires_hashed_job_manifest"] is True, "cloud preflight")
    require(cloud["activation_requires_cloud_side_ttl_watchdog"] is True, "cloud TTL watchdog")

    tooling = opening["tooling"]
    require(tooling == {
        "wolfram_exact_rcf_lane": "AVAILABLE",
        "wsl_exact_cas_core": "PASS",
        "baker_frontier_cad_source": "ACQUIRED_NOT_SELECTED",
        "baker_frontier_cad_build": "NOT_QUALIFIED_MISSING_BIN_CSH",
        "general_simplicial_replacement_backend": "NOT_FOUND_AT_OPENING",
    }, "tooling state")

    authority = opening["authority"]
    require(authority["human_review_available"] is False, "human review")
    require(authority["independent_machine_replay_required"] is True, "machine replay")
    require(authority["github_mode"] == "READ_ONLY", "GitHub mode")
    require(authority["github_write"] is False, "GitHub write")
    require(authority["network_research_allowed"] is True, "network research")
    require(authority["connected_exact_computation_allowed"] is True, "connected computation")
    require(authority["single_ephemeral_cloud_worker_allowed_conditionally"] is True, "cloud authority")
    for key in ("canonical_theorem_files_writable", "canonical_state_writable", "theorem_ledger_writable"):
        require(authority[key] is False, f"authority {key}")

    recovery = opening["recovery_checkpoint"]
    require(recovery["bytes"] == 134422661, "recovery bytes")
    require(recovery["sha256"] == "33bec64bf1a3cefef5b848cd581edc5808e0d3152fd8a150de00faf4b1714ee8", "recovery digest")
    require(recovery["bundle_verify"] == "PASS_COMPLETE_HISTORY", "bundle verification")
    require(recovery["manifest_sha256"] == "b77f91b2b053d545b829df169308e5cb47c673039fd5af831f30fe6504ddac65", "recovery manifest")

    require(len(opening["source_pins"]) == 21, "source pin count")
    seen = set()
    for pin in opening["source_pins"]:
        path = ROOT / pin["path"]
        require(pin["path"] not in seen, f"duplicate pin {pin['path']}")
        seen.add(pin["path"])
        require(path.is_file(), f"missing pin {pin['path']}")
        require(path.stat().st_size == pin["bytes"], f"byte drift {pin['path']}")
        require(sha256(path) == pin["sha256"], f"hash drift {pin['path']}")


def hostile_canaries(opening: dict) -> int:
    mutations = [
        lambda x: x.__setitem__("base_revision", "0" * 40),
        lambda x: x["canonical_state"].__setitem__("opening_ledger", "3/9"),
        lambda x: x["canonical_state"].__setitem__("status", "ACTIVE"),
        lambda x: x["canonical_state"].__setitem__("open_load_bearing_obligations", 6),
        lambda x: x["canonical_state"].__setitem__("pair_residual", 0),
        lambda x: x["strategy"].__setitem__("action", "CONTINUE"),
        lambda x: x["strategy"].__setitem__("selected_construction_count_at_opening", 1),
        lambda x: x["strategy"].__setitem__("full_scope_construction_active", True),
        lambda x: x["proof_distance"].__setitem__("qualification_has_theorem_credit", True),
        lambda x: x["proof_distance"]["opening_vector"].__setitem__(3, 6),
        lambda x: x["quantified_scope"].__setitem__("realizable_unlabelled_parent_types", 2603),
        lambda x: x["quantified_scope"].__setitem__("all_realization_components", False),
        lambda x: x["quantified_scope"].__setitem__("literal_O1_through_O5_claimed", True),
        lambda x: x["quantified_scope"].__setitem__("bypass_must_be_independently_proved_strictly_smaller", False),
        lambda x: x["quantified_scope"].__setitem__("alternate_pair_edge", "global_gluing"),
        lambda x: x["quantified_scope"].__setitem__("samples_or_local_atlases_sufficient", True),
        lambda x: x["q0"].__setitem__("theorem_credit", "GLOBAL_GLUE"),
        lambda x: x["q0"].__setitem__("requires_formula_derived_output", False),
        lambda x: x["q0"]["canaries"].pop(),
        lambda x: x["q0"].__setitem__("laptop_hours", 80),
        lambda x: x["q1"].__setitem__("status", "ACTIVE"),
        lambda x: x["cloud"].__setitem__("status", "ACTIVE"),
        lambda x: x["cloud"].__setitem__("project", "other-project"),
        lambda x: x["cloud"].__setitem__("instance_prefix", "claude-"),
        lambda x: x["cloud"].__setitem__("machine_type", "n2-highcpu-32"),
        lambda x: x["cloud"].__setitem__("max_cycle_spend_usd", 50),
        lambda x: x["cloud"].__setitem__("existing_instances_in_scope", True),
        lambda x: x["cloud"].__setitem__("must_delete_instance_and_disk", False),
        lambda x: x["cloud"].__setitem__("stopping_is_cleanup", True),
        lambda x: x["cloud"].__setitem__("activation_requires_cloud_side_ttl_watchdog", False),
        lambda x: x["tooling"].__setitem__("general_simplicial_replacement_backend", "QUALIFIED"),
        lambda x: x["authority"].__setitem__("human_review_available", True),
        lambda x: x["authority"].__setitem__("github_write", True),
        lambda x: x["authority"].__setitem__("canonical_state_writable", True),
        lambda x: x["source_pins"][0].__setitem__("sha256", "0" * 64),
    ]
    rejected = 0
    for index, mutate in enumerate(mutations):
        candidate = copy.deepcopy(opening)
        mutate(candidate)
        try:
            validate(candidate)
        except AssertionError:
            rejected += 1
        else:
            raise AssertionError(f"hostile opening mutation accepted: {index}")
    return rejected


def main() -> None:
    opening = load(OPENING)
    validate(opening)
    rejected = hostile_canaries(opening)
    print(
        "PASS D3 global formula-diagram opening: "
        f"Q0 active, Q1 closed, cloud inactive, {rejected}/{rejected} hostiles rejected"
    )


if __name__ == "__main__":
    main()
