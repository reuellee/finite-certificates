#!/usr/bin/env python3
"""Verify the D3 mixed-(1,0,0) theorem/obstruction opening contract."""

from __future__ import annotations

import copy
import hashlib
import json
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[4]
STATE = Path(__file__).with_name("OPENING_STATE.json")
BASE = "fb667bfe33ef9e945a82e9a23b615e67f5f39c0f"
BASE_TREE = "117850b25cd94f865cb85e681c465b8260dd9c6a"
OPEN_VECTOR = ["2/9", 1, ["diag3_pair_hc1", "diag3_triple_hc0"], 7, "UNKNOWN", "UNKNOWN", 8, 11]


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def git(*args: str) -> str:
    return subprocess.check_output(["git", *args], cwd=ROOT, text=True).strip()


def validate(data: dict) -> None:
    require(data["format"] == "d3-mixed-100-universal-carrier-opening-v1", "format")
    require(data["cycle_id"] == "2026-09-03-d3-mixed-block-100-universal-carrier-gate1", "cycle id")

    auth = data["authorization"]
    require(auth["user_execution_authority_received"] is True, "user authority")
    for key in ("author_contact", "network_research", "github_write", "external_compute", "canonical_ledger_edit"):
        require(auth[key] is False, f"authority restriction {key}")

    repo = data["repository"]
    require(repo["base_revision"] == BASE and repo["base_tree"] == BASE_TREE, "base pins")
    require(repo["concurrent_successor_cycles"] == [], "concurrent successors")
    require(repo["historical_worktrees_are_frozen_evidence"] is True, "historical worktree scope")
    require(git("rev-parse", f"{BASE}^{{tree}}") == BASE_TREE, "Git base tree")
    require(git("merge-base", "--is-ancestor", BASE, "HEAD") == "", "base ancestry")

    canonical = data["canonical"]
    require(canonical["score"] == "2/9", "ledger")
    require(canonical["proved_diagonals"] == [1, 2], "proved diagonals")
    require(canonical["open_diagonals"] == [3, 4, 5, 6, 7, 8, 9], "open diagonals")
    require(canonical["pair_residual"] == canonical["pair_coverage"] == "UNKNOWN", "pair accounting")
    require(canonical["triple_settled"] + canonical["triple_residual"] == canonical["triple_total"] == 79102449, "triple accounting")

    predecessor = data["predecessor_close"]
    require(predecessor == {
        "cycle_id": "2026-09-02-d3-triple-critical-saturation-component-gate1",
        "q0": "NULL", "q1": "DENIED", "trajectory": "STALLED",
        "action": "STOP", "successor": "NONE"
    }, "predecessor close")

    strategy = data["strategy"]
    require(strategy["verdict"] == "PIVOT_SELECT_D3_MIXED_100_UNIVERSAL_CARRIER_OR_OBSTRUCTION", "strategy verdict")
    require(strategy["selected_count"] == 1 and strategy["same_route_continue"] is False, "single pivot")
    require(len(strategy["alternatives_compared"]) >= 4, "strategy alternatives")

    proof = data["proof_distance"]
    require(proof["opening_vector"] == OPEN_VECTOR, "opening vector")
    require(proof["selected_route_open_residual"] == ["O3_universal_mixed_chain", "O4_arbitrary_flag_coherence"], "route residual")
    require(proof["selected_route_open_count"] == 2, "route residual count")
    require(proof["local_or_formal_progress_counts"] is False, "no local credit")

    quantifiers = data["quantifiers"]
    require(all(value is True for value in quantifiers.values()), "complete quantifiers")

    baseline = data["route_baseline"]
    require(baseline["formal_shape_count"] == 10, "shape count")
    require(baseline["formal_labeled_placements_one_three_block_family"] == 34, "placement count")
    require(baseline["provisional_universal_clauses"] == ["(0)", "(1)", "(2)"], "3/10 baseline")
    require(baseline["critical_open_clause"] == "(1,0,0)", "critical clause")
    for key in ("formal_taxonomy_is_global_denominator", "provisional_3_of_10_is_end_to_end_coverage", "row2599_canary_is_global_evidence"):
        require(baseline[key] is False, f"scope guard {key}")

    obligations = data["obligations"]
    require(sum(item.get("load_bearing", False) for item in obligations) == 7, "seven load-bearing obligations")
    require(all(item["class"] == "inconclusive" for item in obligations), "opening obligations inconclusive")
    require([item["id"] for item in obligations if item.get("selected_route")] == proof["selected_route_open_residual"], "route obligations")

    ceiling = data["resource_ceiling"]
    require(ceiling == {
        "wall_seconds": 14400, "lane_peak_ram_gib": 16, "new_scratch_gib": 2,
        "constructor_handoffs": 1, "verifier_directed_repairs": 1,
        "cloud_workers": 0, "external_spend_usd": 0
    }, "resource ceiling")

    pins = data["source_pins"]
    require(len(pins) == 11, "source pin count")
    for relative, expected in pins.items():
        path = ROOT / relative
        require(path.is_file(), f"missing source {relative}")
        require(sha256(path) == expected, f"source drift {relative}")


def hostile_replay(data: dict) -> int:
    mutations = []

    def add(path: tuple[str, ...], value: object) -> None:
        candidate = copy.deepcopy(data)
        node = candidate
        for key in path[:-1]:
            node = node[key]
        node[path[-1]] = value
        mutations.append(candidate)

    add(("authorization", "author_contact"), True)
    add(("authorization", "network_research"), True)
    add(("authorization", "github_write"), True)
    add(("authorization", "external_compute"), True)
    add(("authorization", "canonical_ledger_edit"), True)
    add(("repository", "base_revision"), "0" * 40)
    add(("repository", "base_tree"), "0" * 40)
    add(("repository", "concurrent_successor_cycles"), ["duplicate"])
    add(("canonical", "score"), "3/9")
    add(("canonical", "pair_residual"), 0)
    add(("canonical", "triple_residual"), 0)
    add(("predecessor_close", "q0"), "PASS")
    add(("predecessor_close", "q1"), "ACTIVE")
    add(("strategy", "same_route_continue"), True)
    add(("strategy", "selected_count"), 2)
    add(("proof_distance", "selected_route_open_count"), 0)
    add(("proof_distance", "local_or_formal_progress_counts"), True)
    add(("quantifiers", "all_composable_face_flags"), False)
    add(("quantifiers", "true_parent_infinity_only"), False)
    add(("route_baseline", "formal_taxonomy_is_global_denominator"), True)
    add(("route_baseline", "provisional_3_of_10_is_end_to_end_coverage"), True)
    add(("route_baseline", "row2599_canary_is_global_evidence"), True)
    add(("resource_ceiling", "cloud_workers"), 1)
    add(("resource_ceiling", "external_spend_usd"), 1)

    rejected = 0
    for candidate in mutations:
        try:
            validate(candidate)
        except (AssertionError, KeyError, subprocess.CalledProcessError):
            rejected += 1
    require(rejected == len(mutations), "hostile mutation escaped")
    return rejected


def main() -> None:
    data = json.loads(STATE.read_text(encoding="utf-8"))
    validate(data)
    rejected = hostile_replay(data)
    print("PASS D3 mixed-(1,0,0) opening state")
    print(f"PASS hostile mutations rejected {rejected}/{rejected}")
    print("OPEN 2/9; canonical obligations 7; pair UNKNOWN/UNKNOWN; streaks 8/11")
    print("ROUTE O3/O4 residual 2/2; formal 3/10 is not global coverage")
    print("ACTION PIVOT; Q0 theorem-or-obstruction only; construction denied")


if __name__ == "__main__":
    main()
