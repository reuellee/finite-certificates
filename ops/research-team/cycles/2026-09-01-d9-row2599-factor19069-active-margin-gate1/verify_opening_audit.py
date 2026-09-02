#!/usr/bin/env python3
"""Fail-closed opening audit for the factor-19069 active-margin gate."""

from __future__ import annotations

from copy import deepcopy
import hashlib
import json
from pathlib import Path
import subprocess


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
AUDIT = HERE / "OPENING_AUDIT.json"
BASE = "b14e5bd0158752f96a9534b484ef2195626bd14c"
TREE = "b942da304007bb4d9437ec7575c420fc6073814b"
TARGET = "D9_ROW2599_FACTOR19069_PROJECTION_FREE_ACTIVE_MARGIN_COMPONENT_GATE1"


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


def frozen_bytes(path: str) -> bytes:
    return git("show", f"{BASE}:{path}", binary=True)


def validate(candidate: dict) -> None:
    require(candidate["format"] == "d9-factor19069-active-margin-opening-audit-v1", "format")
    require(candidate["base_revision"] == BASE, "base revision")
    require(candidate["base_tree"] == TREE, "base tree")
    require(candidate["opening_ledger"] == "2/9", "ledger")
    require(candidate["predecessor_verdict"] == "PIVOT", "predecessor verdict")
    require(candidate["selected_target"] == TARGET, "selected target")
    require(candidate["selected_count"] == 1, "selected count")
    target = candidate["target"]
    require(target["parent_index"] == 2599, "parent")
    require(target["factor_id"] == 19069, "factor")
    require(target["parent_sign_tags"] == 70, "parent sign tags")
    require(target["skeleton_edges"] == 40, "skeleton edges")
    require(target["requires_connected_parent_component_tag"] is True, "parent component tag")
    require(target["requires_all_true_boundary_strata"] is True, "true boundary strata")
    require(candidate["resource_ceiling"]["max_exact_systems"] == 100000, "system ceiling")
    require(candidate["resource_ceiling"]["paid_external_compute"] is False, "external compute")
    require(len(candidate["prohibited_routes"]) == 4, "prohibited routes")
    durable = candidate["durable_checkpoint"]
    require(durable["project_root"] == r"E:\Projects\9DVL Research", "durable root")
    require(durable["no_hardlinks"] is True, "no hardlinks")
    require(durable["github_write"] is False, "GitHub mode")


def hostile_mutations(stored: dict) -> None:
    mutations = []
    candidate = deepcopy(stored); candidate["base_revision"] = "0" * 40; mutations.append((candidate, "base revision"))
    candidate = deepcopy(stored); candidate["opening_ledger"] = "3/9"; mutations.append((candidate, "ledger"))
    candidate = deepcopy(stored); candidate["selected_count"] = 2; mutations.append((candidate, "selected count"))
    candidate = deepcopy(stored); candidate["target"]["parent_sign_tags"] = 69; mutations.append((candidate, "parent sign tags"))
    candidate = deepcopy(stored); candidate["target"]["requires_connected_parent_component_tag"] = False; mutations.append((candidate, "parent component tag"))
    candidate = deepcopy(stored); candidate["target"]["requires_all_true_boundary_strata"] = False; mutations.append((candidate, "true boundary strata"))
    candidate = deepcopy(stored); candidate["resource_ceiling"]["paid_external_compute"] = True; mutations.append((candidate, "external compute"))
    candidate = deepcopy(stored); candidate["durable_checkpoint"]["github_write"] = True; mutations.append((candidate, "GitHub mode"))
    for candidate, marker in mutations:
        try:
            validate(candidate)
        except Reject as error:
            require(marker in str(error), f"wrong hostile rejection: {error}")
            continue
        raise Reject(f"hostile mutation accepted: {marker}")


def main() -> None:
    require(git("rev-parse", f"{BASE}^{{commit}}") == BASE, "base commit")
    require(git("rev-parse", f"{BASE}^{{tree}}") == TREE, "base tree")
    audit = json.loads(AUDIT.read_text(encoding="utf-8"))
    validate(audit)
    for path, expected in audit["pins"].items():
        require(hashlib.sha256(frozen_bytes(path)).hexdigest() == expected, f"source pin {path}")
    canonical = json.loads(frozen_bytes(
        "ai/omreal/data/CANONICAL_RESEARCH_STATE_V5.json"
    ).decode("utf-8"))
    require(canonical["status"] == "PIVOT_REQUIRED", "canonical status")
    require(canonical["theorem"]["score"] == "2/9", "canonical ledger")
    require(canonical["theorem"]["proved_diagonals"] == [1, 2], "proved diagonals")
    require(canonical["selected_successor"]["id"] == TARGET, "canonical successor")
    predecessor = json.loads(frozen_bytes(
        "ops/team/d9-fixed-domain-cegar-referee/RESULT.json"
    ).decode("utf-8"))
    require(predecessor["verdict"] == "ACCEPT", "predecessor acceptance")
    require(predecessor["closing_strategy_verdict"] == "PIVOT", "predecessor pivot")
    require(predecessor["theorem_ledger"] == "2/9", "predecessor ledger")
    require(predecessor["precise_successor"].startswith(TARGET), "predecessor successor")
    hostile_mutations(audit)
    print("PASS D9 factor-19069 active-margin gate-1 opening audit")
    print("base=b14e5bd tree=b942da3 parent=2599 factor=19069 tags=70 skeleton=40")
    print("opening_hostile_mutations=8 ledger=2/9 github_write=false")


if __name__ == "__main__":
    main()
