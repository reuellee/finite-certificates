#!/usr/bin/env python3
"""Verify the post-factor19069 canonical 9DVL research state V6."""

from __future__ import annotations

from copy import deepcopy
import hashlib
import json
from pathlib import Path
import subprocess


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
STATE = HERE / "data" / "CANONICAL_RESEARCH_STATE_V6.json"
REFEREE = "fee73c8d79a930cad044397d4ee221c06632d831"
REFEREE_TREE = "a9f4cda05620fc024cda7998fd45ee661a72fe51"


class Reject(AssertionError):
    pass


def require(condition: bool, message: str) -> None:
    if not condition:
        raise Reject(message)


def git(*arguments: str, binary: bool = False):
    result = subprocess.check_output(
        ["git", *arguments], cwd=ROOT, text=not binary
    )
    return result if binary else result.strip()


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def validate(candidate: dict) -> None:
    require(candidate["format"] == "9dvl-canonical-research-state-v6", "format")
    require(candidate["status"] == "PIVOT_REQUIRED", "status")
    repository = candidate["repository"]
    require(repository["branch"] == "research/local-d9-factor19069-gate1-20260901", "branch")
    require(repository["integrated_referee_commit"] == REFEREE, "referee commit")
    require(repository["integrated_referee_tree"] == REFEREE_TREE, "referee tree")
    require(repository["saved_project_root"] == r"E:\Projects\9DVL Research", "saved project")
    require(repository["drive_connector_used"] is False, "Drive connector")
    require(repository["github_mode"] == "READ_ONLY_UNTIL_NEW_EXPLICIT_USER_INSTRUCTION", "GitHub mode")
    theorem = candidate["theorem"]
    require(theorem["score"] == "2/9", "ledger")
    require(theorem["proved_diagonals"] == [1, 2], "proved diagonals")
    require(theorem["diagonal_nine"] == "OPEN", "diagonal nine")
    require(theorem["promotion"] == "NONE", "promotion")
    require(theorem["theorem_level_counterexample"] == "NOT_FOUND", "counterexample")
    cycle = candidate["completed_cycle"]
    require(cycle["selected_count"] == 1, "selected count")
    require(cycle["frontier"]["parent_sign_tags"] == 70, "parent tags")
    require(cycle["frontier"]["fixed_skeleton_edges"] == 40, "skeleton edges")
    require(cycle["frontier"]["first_support_size_exceeding_ceiling"] == 4, "ceiling crossing")
    require(cycle["frontier"]["component_samples"] == 0, "component samples")
    require(cycle["certificate_gate"]["producer_imported"] is False, "producer independence")
    require(cycle["referee_gate"]["clean_replay"] is True, "clean replay")
    require(cycle["route_disposition"].endswith("_RETIRED"), "route disposition")
    successor = candidate["selected_successor"]
    require(successor["id"] == "D9_ROW2599_FACTOR19069_FACTORED_BARRIER_COMPONENT_SAMPLER_GATE1", "successor")
    require(successor["strategy"] == "PROJECTION_FREE_FACTORED_BARRIER_COMPONENT_SAMPLING", "successor strategy")
    require("all 70 parent factors" in successor["quantified_target"], "successor quantifiers")
    require(len(successor["prohibited"]) == 5, "successor prohibitions")
    require(all(candidate["process_gates"].values()), "process gates")


def hostile_mutations(stored: dict) -> None:
    mutations = []
    altered = deepcopy(stored); altered["status"] = "COMPLETE"; mutations.append((altered, "status"))
    altered = deepcopy(stored); altered["repository"]["integrated_referee_commit"] = "0" * 40; mutations.append((altered, "referee commit"))
    altered = deepcopy(stored); altered["repository"]["drive_connector_used"] = True; mutations.append((altered, "Drive connector"))
    altered = deepcopy(stored); altered["repository"]["github_mode"] = "WRITE"; mutations.append((altered, "GitHub mode"))
    altered = deepcopy(stored); altered["theorem"]["score"] = "3/9"; mutations.append((altered, "ledger"))
    altered = deepcopy(stored); altered["theorem"]["diagonal_nine"] = "PROVED"; mutations.append((altered, "diagonal nine"))
    altered = deepcopy(stored); altered["completed_cycle"]["frontier"]["component_samples"] = 1; mutations.append((altered, "component samples"))
    altered = deepcopy(stored); altered["completed_cycle"]["referee_gate"]["clean_replay"] = False; mutations.append((altered, "clean replay"))
    altered = deepcopy(stored); altered["selected_successor"]["id"] = "SAMPLE_ANOTHER_SEPARATOR"; mutations.append((altered, "successor"))
    altered = deepcopy(stored); altered["process_gates"]["weak_parent_signs_are_not_connected_parent_closure_residence"] = False; mutations.append((altered, "process gates"))
    for candidate, marker in mutations:
        try:
            validate(candidate)
        except Reject as error:
            require(marker in str(error), f"wrong hostile rejection {marker}: {error}")
            continue
        raise Reject(f"hostile mutation accepted: {marker}")


def main() -> None:
    require(git("rev-parse", f"{REFEREE}^{{commit}}") == REFEREE, "referee existence")
    require(git("rev-parse", f"{REFEREE}^{{tree}}") == REFEREE_TREE, "referee tree")
    state = json.loads(STATE.read_text(encoding="utf-8"))
    validate(state)
    predecessor = ROOT / state["predecessor"]["path"]
    require(sha256(predecessor.read_bytes()) == state["predecessor"]["sha256"], "predecessor pin")
    for path, expected in state["pins"].items():
        frozen = git("show", f"{REFEREE}:{path}", binary=True)
        require(sha256(frozen) == expected, f"referee pin {path}")
        require((ROOT / path).read_bytes() == frozen, f"post-referee drift {path}")
    referee = json.loads(git(
        "show", f"{REFEREE}:ops/team/d9-factor19069-active-margin-referee/RESULT.json", binary=True
    ).decode("utf-8"))
    require(referee["verdict"] == "ACCEPT", "referee verdict")
    require(referee["theorem_ledger"] == "2/9", "referee ledger")
    require(referee["precise_successor"].startswith(state["selected_successor"]["id"]), "referee successor")
    hostile_mutations(state)
    print("PASS canonical 9DVL research state V6")
    print("referee=fee73c8 ledger=2/9 diagonal9=OPEN verdict=PIVOT")
    print("hostile_mutations=10 successor=FACTOR19069_FACTORED_BARRIER")


if __name__ == "__main__":
    main()
