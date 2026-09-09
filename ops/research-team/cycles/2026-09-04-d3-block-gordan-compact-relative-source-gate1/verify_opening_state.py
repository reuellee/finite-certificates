#!/usr/bin/env python3
"""Verify the D3 compact-relative block-Gordan source opening contract."""

from __future__ import annotations

import copy
import hashlib
import json
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[4]
CYCLE_DIR = Path(__file__).resolve().parent
STATE = CYCLE_DIR / "OPENING_STATE.json"
GRAPH = CYCLE_DIR / "OBLIGATION_GRAPH.json"
BASE = "5587d2da0e6e7a03a716f7e25ddbd98a82f4af28"
BASE_TREE = "3c6647af475ace9c1a4d77a2af169a0076344af1"
OPEN_VECTOR = [
    "2/9", 1, ["diag3_pair_hc1", "diag3_triple_hc0"],
    7, "UNKNOWN", "UNKNOWN", 9, 12,
]
SELECTED = ["global_gluing", "extension_labels", "strict_closure", "relative_infinity"]
POSITIVE_TOKEN = "PROVED_GLOBAL_FINITE_RELATIVE_BLOCK_GORDAN_SOURCE"


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def git(*args: str) -> str:
    return subprocess.check_output(["git", *args], cwd=ROOT, text=True).strip()


def validate(data: dict, *, check_files: bool = True) -> None:
    require(data["format"] == "d3-bg-compact-relative-source-opening-v1", "format")
    require(
        data["cycle_id"] == "2026-09-04-d3-block-gordan-compact-relative-source-gate1",
        "cycle id",
    )

    auth = data["authorization"]
    require(auth["user_execution_authority_received"] is True, "user authority")
    require(auth["read_only_primary_source_research"] is True, "read-only literature scope")
    for key in ("author_contact", "github_write", "external_compute", "canonical_ledger_edit"):
        require(auth[key] is False, f"authority restriction {key}")

    repo = data["repository"]
    require(repo["base_revision"] == BASE and repo["base_tree"] == BASE_TREE, "base pins")
    require(repo["concurrent_successor_cycles"] == [], "concurrent successors")
    require(repo["historical_worktrees_are_frozen_evidence"] is True, "historical scope")
    if check_files:
        require(git("rev-parse", f"{BASE}^{{tree}}") == BASE_TREE, "Git base tree")
        require(git("merge-base", "--is-ancestor", BASE, "HEAD") == "", "base ancestry")

    canonical = data["canonical"]
    require(canonical["status"] == "STOPPED", "V11 status")
    require(canonical["selected_next_target"] == "NONE", "V11 successor")
    require(canonical["score"] == "2/9", "ledger")
    require(canonical["proved_diagonals"] == [1, 2], "proved diagonals")
    require(canonical["open_diagonals"] == [3, 4, 5, 6, 7, 8, 9], "open diagonals")
    require(canonical["pair_residual"] == canonical["pair_coverage"] == "UNKNOWN", "pair accounting")
    require(
        canonical["triple_settled"] + canonical["triple_residual"]
        == canonical["triple_total"] == 79102449,
        "triple accounting",
    )
    require(canonical["same_blocker_streak"] == 9, "blocker streak")
    require(canonical["zero_ledger_streak"] == 12, "zero-ledger streak")

    new_input = data["new_input"]
    require(new_input["id"] == "FULL_SOURCE_DERIVED_PROPER_FUNCTORIAL_BLOCK_GORDAN_TOTAL_SPACE", "new input")
    require(new_input["distinction"] == "USE_GAMMA_S_GEOMETRY_NOT_REDUCED_L_SOURCE_INTERFACE", "route distinction")
    for key in ("source_derived", "proper_over_bad_union", "functorial_by_zero_padding"):
        require(new_input[key] is True, f"new input property {key}")
    require(new_input["fixed_fiber_convexity_alone_claims_vanishing"] is False, "no convexity overclaim")

    strategy = data["strategy"]
    require(strategy["verdict"] == "PIVOT_SELECT_D3_BLOCK_GORDAN_COMPACT_RELATIVE_SOURCE", "strategy verdict")
    require(
        strategy["selected_target"]
        == "D3_BLOCK_GORDAN_COMPACT_RELATIVE_SOURCE_THEOREM_OR_OBSTRUCTION_GATE1",
        "target",
    )
    require(strategy["selected_count"] == 1 and strategy["same_route_continue"] is False, "single pivot")
    require(len(strategy["alternatives_compared"]) >= 5, "strategy alternatives")

    proof = data["proof_distance"]
    require(proof["opening_vector"] == OPEN_VECTOR, "opening vector")
    require(proof["selected_route_open_residual"] == SELECTED, "selected residual")
    require(proof["selected_route_open_count"] == 4, "selected residual count")
    require(proof["positive_load_bearing_count"] == 3, "positive load-bearing count")
    require(proof["positive_ledger"] == "2/9", "no positive ledger promotion")
    require(proof["local_or_formal_progress_counts"] is False, "no local credit")

    quantifiers = data["quantifiers"]
    require(len(quantifiers) == 8 and all(value is True for value in quantifiers.values()), "quantifiers")

    endpoint = data["positive_endpoint"]
    require(endpoint["token"] == POSITIVE_TOKEN, "positive token")
    require(len(endpoint["required_clauses"]) == 5, "five clauses")
    require(endpoint["closes"] == SELECTED, "positive closes")
    require(
        endpoint["does_not_close"]
        == ["middle_rank_replay", "diag3_pair_hc1", "diag3_triple_hc0", "diag3"],
        "nonconsequences",
    )

    ceiling = data["resource_ceiling"]
    require(ceiling["wall_seconds"] == 21600, "wall ceiling")
    require(ceiling["lane_peak_ram_gib"] == 16 and ceiling["new_scratch_gib"] == 2, "memory/scratch")
    require(ceiling["producer_handoffs"] == 2 and ceiling["verifier_directed_repairs"] == 1, "handoffs")
    require(ceiling["cloud_workers"] == 0 and ceiling["external_spend_usd"] == 0, "external resources")
    require(ceiling["bulk_semialgebraic_execution"] is False, "no bulk execution")

    pins = data["source_pins"]
    require(len(pins) == 10, "source pin count")
    if check_files:
        for relative, expected in pins.items():
            path = ROOT / relative
            require(path.is_file(), f"missing source {relative}")
            require(sha256(path) == expected, f"source drift {relative}")

        live = json.loads((ROOT / canonical["state"]).read_text(encoding="utf-8"))
        require(live["status"] == "STOPPED", "live canonical status")
        require(live["selected_next_target"]["id"] == "NONE", "live canonical target")
        require(live["theorem"]["score"] == "2/9", "live ledger")
        require(live["proof_distance"]["current_vector"] == OPEN_VECTOR, "live proof vector")
        require(live["open_obligations"]["load_bearing_count"] == 7, "live obligations")

        graph = json.loads(GRAPH.read_text(encoding="utf-8"))
        require(graph["opening_load_bearing_count"] == 7, "graph opening count")
        require(graph["positive_close_load_bearing_count"] == 3, "graph positive count")
        nodes = graph["nodes"]
        closing = [n["id"] for n in nodes if n.get("positive_gate_effect") == "CLOSE"]
        remaining = [n["id"] for n in nodes if n.get("load_bearing") and n.get("positive_gate_effect") == "OPEN"]
        require(closing == SELECTED, "graph closing nodes")
        require(remaining == ["middle_rank_replay", "diag3_pair_hc1", "diag3_triple_hc0"], "graph remaining nodes")
        require(["finite_relative_source", "diag3"] in graph["forbidden_edges"], "graph anti-promotion edge")

        cycle_text = (CYCLE_DIR / "CYCLE.md").read_text(encoding="utf-8")
        theorem_text = (CYCLE_DIR / "THEOREM_CANDIDATE.md").read_text(encoding="utf-8")
        literature_text = (CYCLE_DIR / "LITERATURE_SCOPE.md").read_text(encoding="utf-8")
        require("NOT INDEPENDENTLY ACCEPTED" in theorem_text, "draft status")
        require("does not prove" in theorem_text.lower(), "theorem nonconsequence")
        require("No parallel worker was started" in cycle_text, "role execution honesty")
        require("supporting evidence only" in literature_text, "literature scope")


def hostile_replay(data: dict) -> int:
    mutations: list[dict] = []

    def add(path: tuple[str, ...], value: object) -> None:
        candidate = copy.deepcopy(data)
        node = candidate
        for key in path[:-1]:
            node = node[key]
        node[path[-1]] = value
        mutations.append(candidate)

    add(("authorization", "user_execution_authority_received"), False)
    add(("authorization", "read_only_primary_source_research"), False)
    add(("authorization", "author_contact"), True)
    add(("authorization", "github_write"), True)
    add(("authorization", "external_compute"), True)
    add(("authorization", "canonical_ledger_edit"), True)
    add(("repository", "base_revision"), "0" * 40)
    add(("repository", "base_tree"), "0" * 40)
    add(("repository", "concurrent_successor_cycles"), ["duplicate"])
    add(("canonical", "status"), "ACTIVE")
    add(("canonical", "selected_next_target"), "AUTOMATIC")
    add(("canonical", "score"), "3/9")
    add(("canonical", "pair_residual"), 0)
    add(("canonical", "triple_residual"), 0)
    add(("canonical", "same_blocker_streak"), 0)
    add(("canonical", "zero_ledger_streak"), 0)
    add(("new_input", "source_derived"), False)
    add(("new_input", "proper_over_bad_union"), False)
    add(("new_input", "functorial_by_zero_padding"), False)
    add(("new_input", "fixed_fiber_convexity_alone_claims_vanishing"), True)
    add(("strategy", "selected_count"), 2)
    add(("strategy", "same_route_continue"), True)
    add(("proof_distance", "opening_vector"), ["3/9"])
    add(("proof_distance", "selected_route_open_count"), 0)
    add(("proof_distance", "positive_load_bearing_count"), 0)
    add(("proof_distance", "positive_ledger"), "3/9")
    add(("proof_distance", "local_or_formal_progress_counts"), True)
    add(("quantifiers", "all_2604_realizable_uniform_rank4_parent_classes"), False)
    add(("quantifiers", "all_normalized_realization_components"), False)
    add(("quantifiers", "all_seven_nonempty_signature_subsets"), False)
    add(("quantifiers", "all_subdiagram_inclusions_simultaneous"), False)
    add(("quantifiers", "true_parent_infinity_only"), False)
    add(("positive_endpoint", "token"), "PROVED_DIAG3")
    add(("positive_endpoint", "closes"), SELECTED + ["diag3_pair_hc1"])
    add(("positive_endpoint", "does_not_close"), [])
    add(("resource_ceiling", "cloud_workers"), 1)
    add(("resource_ceiling", "external_spend_usd"), 1)
    add(("resource_ceiling", "bulk_semialgebraic_execution"), True)

    rejected = 0
    for candidate in mutations:
        try:
            validate(candidate, check_files=False)
        except (AssertionError, KeyError, subprocess.CalledProcessError):
            rejected += 1
    require(rejected == len(mutations), "hostile mutation escaped")
    return rejected


def main() -> None:
    data = json.loads(STATE.read_text(encoding="utf-8"))
    validate(data)
    rejected = hostile_replay(data)
    print("PASS D3 compact-relative block-Gordan source opening")
    print(f"PASS source pins {len(data['source_pins'])}/{len(data['source_pins'])}")
    print(f"PASS hostile mutations rejected {rejected}/{rejected}")
    print("OPEN 2/9; load-bearing 7; pair UNKNOWN/UNKNOWN; streaks 9/12")
    print("TARGET structural residual 4/4 -> 0/4 or exact obstruction")
    print("NO ledger, middle-rank, pair, triple, or D3 promotion at opening")


if __name__ == "__main__":
    main()
