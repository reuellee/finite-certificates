#!/usr/bin/env python3
"""Fail-closed opening audit for the factor-19069 factored-barrier gate."""

from __future__ import annotations

from copy import deepcopy
from hashlib import sha256
import json
from pathlib import Path
import subprocess


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
AUDIT = HERE / "OPENING_AUDIT.json"
BASE = "b71c139a3c64cde3442252f8f3d46f2d893978c5"
TREE = "7a9da9f02369831bd34bc22f39a0bbad57725522"
TARGET = "D9_ROW2599_FACTOR19069_FACTORED_BARRIER_COMPONENT_SAMPLER_GATE1"
BRANCH = "research/local-d9-factor19069-factored-barrier-gate1-20260901"


class Reject(AssertionError):
    pass


def require(condition: bool, message: str) -> None:
    if not condition:
        raise Reject(message)


def git(*arguments: str, binary: bool = False):
    result = subprocess.check_output(["git", *arguments], cwd=ROOT, text=not binary)
    return result if binary else result.strip()


def frozen_bytes(path: str) -> bytes:
    return git("show", f"{BASE}:{path}", binary=True)


def validate(candidate: dict) -> None:
    require(candidate["format"] == "d9-factor19069-factored-barrier-opening-audit-v1", "format")
    require(candidate["base_revision"] == BASE, "base revision")
    require(candidate["base_tree"] == TREE, "base tree")
    require(candidate["successor_branch"] == BRANCH, "successor branch")
    require(candidate["opening_ledger"] == "2/9", "ledger")
    require(candidate["predecessor_verdict"] == "PIVOT", "predecessor verdict")
    require(candidate["selected_target"] == TARGET, "selected target")
    require(candidate["selected_count"] == 1, "selected count")
    target = candidate["target"]
    require(target["parent_index"] == 2599, "parent")
    require(target["factor_id"] == 19069, "factor")
    require(target["parent_sign_factors"] == 70, "parent factor count")
    require(target["skeleton_edges"] == 40, "skeleton edge count")
    require(target["barrier"] == "B=product_I H_I", "barrier")
    require(target["barrier_representation"] == "FACTORED_CIRCUIT", "barrier representation")
    require(target["interior_critical_equations"] == "f=0 AND dB_wedge_df=0", "critical equations")
    require(target["requires_positive_dimensional_critical_pieces"] is True, "positive dimensional pieces")
    require(target["requires_connected_parent_component_paths"] is True, "parent component paths")
    require(target["requires_all_parent_sign_boundary_strata"] is True, "boundary strata")
    require(target["requires_exact_attachment_classification"] is True, "attachment classification")
    ceiling = candidate["resource_ceiling"]
    require(ceiling["max_exact_solver_component_nodes"] == 500000, "solver ceiling")
    require(ceiling["paid_external_compute"] is False, "external compute")
    require(len(candidate["prohibited_routes"]) == 6, "prohibited routes")
    durable = candidate["durable_checkpoint"]
    require(durable["project_root"] == r"E:\Projects\9DVL Research", "durable root")
    require(durable["mounted_recovery_root"] == r"G:\My Drive\Projects\research-backups", "recovery root")
    require(durable["drive_connector_used"] is False, "Drive connector")
    require(durable["drive_mirror_optional"] is True, "optional mirror")
    require(durable["verify_length_and_sha256"] is True, "mirror verification")
    require(durable["github_write"] is False, "GitHub mode")


def hostile_mutations(stored: dict) -> None:
    mutations = []
    candidate = deepcopy(stored); candidate["base_revision"] = "0" * 40; mutations.append((candidate, "base revision"))
    candidate = deepcopy(stored); candidate["successor_branch"] += "-drift"; mutations.append((candidate, "successor branch"))
    candidate = deepcopy(stored); candidate["opening_ledger"] = "3/9"; mutations.append((candidate, "ledger"))
    candidate = deepcopy(stored); candidate["selected_count"] = 2; mutations.append((candidate, "selected count"))
    candidate = deepcopy(stored); candidate["target"]["parent_sign_factors"] = 69; mutations.append((candidate, "parent factor count"))
    candidate = deepcopy(stored); candidate["target"]["barrier_representation"] = "EXPANDED"; mutations.append((candidate, "barrier representation"))
    candidate = deepcopy(stored); candidate["target"]["requires_positive_dimensional_critical_pieces"] = False; mutations.append((candidate, "positive dimensional pieces"))
    candidate = deepcopy(stored); candidate["target"]["requires_connected_parent_component_paths"] = False; mutations.append((candidate, "parent component paths"))
    candidate = deepcopy(stored); candidate["target"]["requires_all_parent_sign_boundary_strata"] = False; mutations.append((candidate, "boundary strata"))
    candidate = deepcopy(stored); candidate["target"]["requires_exact_attachment_classification"] = False; mutations.append((candidate, "attachment classification"))
    candidate = deepcopy(stored); candidate["resource_ceiling"]["paid_external_compute"] = True; mutations.append((candidate, "external compute"))
    candidate = deepcopy(stored); candidate["durable_checkpoint"]["drive_connector_used"] = True; mutations.append((candidate, "Drive connector"))
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
        require(sha256(frozen_bytes(path)).hexdigest() == expected, f"source pin {path}")
    canonical = json.loads(frozen_bytes("ai/omreal/data/CANONICAL_RESEARCH_STATE_V6.json").decode("utf-8"))
    require(canonical["status"] == "PIVOT_REQUIRED", "canonical status")
    require(canonical["theorem"]["score"] == "2/9", "canonical ledger")
    require(canonical["theorem"]["proved_diagonals"] == [1, 2], "proved diagonals")
    require(canonical["selected_successor"]["id"] == TARGET, "canonical successor")
    predecessor = json.loads(frozen_bytes("ops/team/d9-factor19069-active-margin-referee/RESULT.json").decode("utf-8"))
    require(predecessor["verdict"] == "ACCEPT", "predecessor acceptance")
    require(predecessor["closing_strategy_verdict"] == "PIVOT", "predecessor pivot")
    require(predecessor["theorem_ledger"] == "2/9", "predecessor ledger")
    require(predecessor["precise_successor"].startswith(TARGET), "predecessor successor")
    hostile_mutations(audit)
    print("PASS D9 factor-19069 factored-barrier gate-1 opening audit")
    print("base=b71c139 tree=7a9da9f parent=2599 factor=19069 parents=70 skeleton=40")
    print("opening_hostile_mutations=13 ledger=2/9 drive_connector=false github_write=false")


if __name__ == "__main__":
    main()
