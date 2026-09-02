#!/usr/bin/env python3
"""Verify the post-CEGAR canonical 9DVL research state V5."""

from __future__ import annotations

from copy import deepcopy
import hashlib
import json
from pathlib import Path
import subprocess


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
STATE = HERE / "data" / "CANONICAL_RESEARCH_STATE_V5.json"
REFEREE = "4feee2ba0d918a8b04bddb3bbd1897175dd35a97"
REFEREE_TREE = "842aedaa58e3ca5247d29a172ebd49f1d83bf61a"
PORTABILITY_EDITED_CODE_PATHS = {
    "ops/team/d9-fixed-domain-cegar-referee/verify_closing_referee.py",
}


class Reject(AssertionError):
    pass


def require(condition: bool, message: str) -> None:
    if not condition:
        raise Reject(message)


def git(*arguments: str, binary: bool = False):
    process = subprocess.check_output(
        ["git", *arguments], cwd=ROOT, text=not binary
    )
    return process if binary else process.strip()


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def validate(candidate: dict) -> None:
    require(candidate["format"] == "9dvl-canonical-research-state-v5", "format")
    require(candidate["status"] == "PIVOT_REQUIRED", "status")
    repository = candidate["repository"]
    require(repository["branch"] == "research/local-d9-pivot3-cegar-20260901", "branch")
    require(repository["reviewed_candidate_commit"] == "55d284e05ab506dc2789045b13f10c3a13afb3ad", "reviewed candidate")
    require(repository["integrated_referee_commit"] == REFEREE, "referee commit")
    require(repository["integrated_referee_tree"] == REFEREE_TREE, "referee tree")
    require(repository["github_mode"] == "READ_ONLY_UNTIL_NEW_EXPLICIT_USER_INSTRUCTION", "GitHub mode")
    theorem = candidate["theorem"]
    require(theorem["score"] == "2/9", "ledger")
    require(theorem["proved_diagonals"] == [1, 2], "proved diagonals")
    require(theorem["diagonal_nine"] == "OPEN", "diagonal nine")
    require(theorem["promotion"] == "NONE", "promotion")
    cycle = candidate["completed_cycle"]
    require(cycle["opening_tournament"]["selected_count"] == 1, "tournament selection")
    require(cycle["frontier"]["exact_path_repairs"] == 2, "path repairs")
    require(cycle["frontier"]["source_realized_counterexamples"] == 0, "counterexample count")
    require(cycle["frontier"]["complete_fixed_domain_candidate_generator"] is False, "generator scope")
    require(cycle["referee_gate"]["closing_strategy_verdict"] == "PIVOT", "strategy verdict")
    require("NO_DIAGONAL_9_PROOF_OR_COUNTEREXAMPLE" in cycle["nonconsequences"], "nonconsequence")
    require(cycle["route_disposition"].endswith("_RETIRED"), "route disposition")
    successor = candidate["selected_successor"]
    require(successor["id"] == "D9_ROW2599_FACTOR19069_PROJECTION_FREE_ACTIVE_MARGIN_COMPONENT_GATE1", "successor")
    require(successor["strategy"] == "PROJECTION_FREE_ADAPTIVE_COMPONENT_DECOMPOSITION", "successor strategy")
    require("all 70 parent-sign path tags" in successor["quantified_target"], "successor quantifiers")
    require(len(successor["prohibited"]) == 5, "successor prohibitions")
    require(all(candidate["process_gates"].values()), "process gate")


def hostile_mutations(stored: dict) -> None:
    mutations = []
    candidate = deepcopy(stored); candidate["status"] = "COMPLETE"; mutations.append((candidate, "status"))
    candidate = deepcopy(stored); candidate["repository"]["integrated_referee_commit"] = "0" * 40; mutations.append((candidate, "referee commit"))
    candidate = deepcopy(stored); candidate["repository"]["github_mode"] = "WRITE"; mutations.append((candidate, "GitHub mode"))
    candidate = deepcopy(stored); candidate["theorem"]["score"] = "3/9"; mutations.append((candidate, "ledger"))
    candidate = deepcopy(stored); candidate["theorem"]["diagonal_nine"] = "PROVED"; mutations.append((candidate, "diagonal nine"))
    candidate = deepcopy(stored); candidate["completed_cycle"]["frontier"]["complete_fixed_domain_candidate_generator"] = True; mutations.append((candidate, "generator scope"))
    candidate = deepcopy(stored); candidate["completed_cycle"]["referee_gate"]["closing_strategy_verdict"] = "CONTINUE"; mutations.append((candidate, "strategy verdict"))
    candidate = deepcopy(stored); candidate["selected_successor"]["id"] = "SAMPLE_ANOTHER_PAIR"; mutations.append((candidate, "successor"))
    for candidate, marker in mutations:
        try:
            validate(candidate)
        except Reject as error:
            require(marker in str(error), f"wrong hostile rejection: {error}")
            continue
        raise Reject(f"hostile mutation accepted: {marker}")


def main() -> None:
    require(git("rev-parse", f"{REFEREE}^{{commit}}") == REFEREE, "referee commit existence")
    require(git("rev-parse", f"{REFEREE}^{{tree}}") == REFEREE_TREE, "referee tree existence")
    state = json.loads(STATE.read_text(encoding="utf-8"))
    validate(state)
    predecessor_path = state["predecessor"]["path"]
    require(sha256((ROOT / predecessor_path).read_bytes()) == state["predecessor"]["sha256"], "predecessor pin")
    pins = state["pins"]
    require(
        PORTABILITY_EDITED_CODE_PATHS <= set(pins),
        "portability-edited pin census",
    )
    for path, expected in pins.items():
        frozen = git("show", f"{REFEREE}:{path}", binary=True)
        require(sha256(frozen) == expected, f"referee pin {path}")
        if path not in PORTABILITY_EDITED_CODE_PATHS:
            require((ROOT / path).read_bytes() == frozen, f"post-referee drift {path}")
    referee = json.loads(git(
        "show", f"{REFEREE}:ops/team/d9-fixed-domain-cegar-referee/RESULT.json",
        binary=True,
    ).decode("utf-8"))
    require(referee["verdict"] == "ACCEPT", "referee verdict")
    require(referee["theorem_ledger"] == "2/9", "referee ledger")
    require(referee["precise_successor"].startswith(state["selected_successor"]["id"]), "referee successor")
    hostile_mutations(state)
    print("PASS canonical 9DVL research state V5")
    print("referee=4feee2b ledger=2/9 diagonal9=OPEN verdict=PIVOT")
    print("hostile_mutations=8 successor=FACTOR19069_PROJECTION_FREE")


if __name__ == "__main__":
    main()
