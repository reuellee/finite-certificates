#!/usr/bin/env python3
"""Fail-closed opening audit for D9 fixed-domain CEGAR gate 1."""

from __future__ import annotations

from copy import deepcopy
import hashlib
import json
from pathlib import Path
import subprocess


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
AUDIT = HERE / "OPENING_AUDIT.json"
BASE = "a5990bff953432a49cfa186f78e25efdb7df280b"
TREE = "96e75f55512f6abbc09749509a45b63adebfa456"


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
    require(candidate["format"] == "d9-fixed-domain-cegar-opening-audit-v1", "format")
    require(candidate["base_revision"] == BASE, "base revision")
    require(candidate["base_tree"] == TREE, "base tree")
    require(candidate["opening_ledger"] == "2/9", "ledger")
    require(candidate["predecessor_verdict"] == "PIVOT", "predecessor verdict")
    tournament = candidate["tournament"]
    require(len(tournament["candidates"]) == 2, "candidate count")
    require(tournament["selected_count"] == 1, "selected count")
    require(tournament["selected"] == "EXACT_FIXED_DOMAIN_COUNTEREXAMPLE_CEGAR", "selection")
    require(tournament["candidates"][0]["net_score"] == 30, "CEGAR score")
    require(tournament["candidates"][1]["net_score"] == 20, "adaptive score")
    frontier = candidate["seed_frontier"]
    require(frontier["seed_count"] == 2, "seed count")
    require(frontier["endpoint_pairs"] == [[12, 37], [37, 176]], "endpoint pairs")
    require(frontier["path_segments"] == 45522, "path segment ceiling")
    require(frontier["complete_fixed_domain_generator"] is False, "scope guard")
    require(candidate["resource_ceiling"]["paid_external_compute"] is False, "external compute")
    require(len(candidate["prohibited_routes"]) == 4, "prohibited routes")


def hostile_mutations(stored: dict) -> None:
    mutations = []
    candidate = deepcopy(stored); candidate["base_revision"] = "0" * 40; mutations.append((candidate, "base revision"))
    candidate = deepcopy(stored); candidate["opening_ledger"] = "3/9"; mutations.append((candidate, "ledger"))
    candidate = deepcopy(stored); candidate["predecessor_verdict"] = "CONTINUE"; mutations.append((candidate, "predecessor verdict"))
    candidate = deepcopy(stored); candidate["tournament"]["selected_count"] = 2; mutations.append((candidate, "selected count"))
    candidate = deepcopy(stored); candidate["tournament"]["selected"] = "PROJECTION_FREE_ADAPTIVE_COMPONENT_DECOMPOSITION"; mutations.append((candidate, "selection"))
    candidate = deepcopy(stored); candidate["seed_frontier"]["complete_fixed_domain_generator"] = True; mutations.append((candidate, "scope guard"))
    candidate = deepcopy(stored); candidate["resource_ceiling"]["paid_external_compute"] = True; mutations.append((candidate, "external compute"))
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
        actual = hashlib.sha256(frozen_bytes(path)).hexdigest()
        require(actual == expected, f"source pin {path}")

    predecessor = json.loads(frozen_bytes(
        "ops/team/d9-fixed-domain-incidence-referee/RESULT.json"
    ).decode("utf-8"))
    require(predecessor["verdict"] == "ACCEPT", "predecessor acceptance")
    require(predecessor["closing_strategy_verdict"] == "PIVOT", "predecessor pivot")
    require(predecessor["theorem_ledger"] == "2/9", "predecessor ledger")
    canonical = json.loads(frozen_bytes(
        "ai/omreal/data/CANONICAL_RESEARCH_STATE_V4.json"
    ).decode("utf-8"))
    require(canonical["theorem"]["score"] == "2/9", "canonical ledger")
    require(canonical["theorem"]["proved_diagonals"] == [1, 2], "proved diagonals")
    hostile_mutations(audit)
    print("PASS D9 fixed-domain CEGAR gate-1 opening audit")
    print("base=a5990bf tree=96e75f5 selected=CEGAR candidates=2")
    print("opening_hostile_mutations=7 ledger=2/9 github_write=false")


if __name__ == "__main__":
    main()
