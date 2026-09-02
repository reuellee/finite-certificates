#!/usr/bin/env python3
"""Frozen-head closing referee for D9 fixed-domain CEGAR gate 1."""

from __future__ import annotations

from copy import deepcopy
import hashlib
import json
from pathlib import Path
import subprocess
import sys


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
FROZEN = "55d284e05ab506dc2789045b13f10c3a13afb3ad"
FROZEN_TREE = "5de3d0b4bda85a2a778e4e9c5d7aef040c41d155"
RESULT = HERE / "RESULT.json"

PINS = {
    "ops/research-team/cycles/2026-09-01-d9-fixed-domain-cegar-gate1/CYCLE.md": "791c5b0421ebb25c33daf589dcc639ea2757bdcfc78f145b1d76c5130ad0012d",
    "ops/research-team/cycles/2026-09-01-d9-fixed-domain-cegar-gate1/OPENING_AUDIT.json": "dbf9b8eefbd49272767616327452653a2a2590f1f2cc991b767c34dec06f70f0",
    "ops/research-team/cycles/2026-09-01-d9-fixed-domain-cegar-gate1/WORK_ORDERS.yaml": "f59b2acd3872b381ec4348c3714d6e860ae26fc2ab1478f30cac292470077ba8",
    "ops/research-team/cycles/2026-09-01-d9-fixed-domain-cegar-gate1/verify_opening_audit.py": "dd0b9a11822879d0a3ac6f56e47394eb0956e727a5f33308d5d9506e9fd64a93",
    "ops/team/d9-fixed-domain-cegar-constructor/CEGAR_FRONTIER.json": "d3d5b1e8f4fae15f651194a135954cd52b84e8ca209e4b64beafe8de35df5083",
    "ops/team/d9-fixed-domain-cegar-constructor/RESULT.json": "26951e9c69dc2e9b3ab79295c4f9c3218af4743208f4ee7fa8f4c09903f7f081",
    "ops/team/d9-fixed-domain-cegar-constructor/build_cegar_frontier.py": "9bcd2d944d3a6473d96e063f4a764a8c942cb8b0b4daeb9397694a8301dca84e",
    "ops/team/d9-fixed-domain-cegar-falsifier/RESULT.json": "cfea0970abe1aaf24c8bf597382ce7c9475e0a28fdfe7c9334f86eba1f32c638",
    "ops/team/d9-fixed-domain-cegar-falsifier/verify_counterexample_attack.py": "c161589be82b6249bdec4c4319923b9473805a68c04654dd69d7e8f9930ae2bf",
    "ops/team/d9-fixed-domain-cegar-certificate/RESULT.json": "a0c912d8525be8204f1ed7a469d0db9f20f4abf151f7c0ba7b63bc55919389e6",
    "ops/team/d9-fixed-domain-cegar-certificate/verify_cegar_frontier.py": "068d9ee83501c2c04bc414db4a65dda55cd9e09ac134825c90a97e638ba85ad0",
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


def frozen_bytes(path: str) -> bytes:
    return git("show", f"{FROZEN}:{path}", binary=True)


def frozen_json(path: str) -> dict:
    return json.loads(frozen_bytes(path).decode("utf-8"))


def replay(
    relative: str,
    markers: tuple[str, ...],
    *,
    pass_prefix: str | None = None,
) -> None:
    process = subprocess.run(
        [sys.executable, "-u", relative], cwd=ROOT,
        text=True, capture_output=True,
    )
    require(process.returncode == 0, f"replay failed {relative}: {process.stderr[-1000:]}")
    if pass_prefix is not None:
        require(
            process.stdout.startswith(pass_prefix),
            f"replay PASS prefix missing {relative}: {pass_prefix}",
        )
    for marker in markers:
        require(marker in process.stdout, f"replay marker missing {relative}: {marker}")


def validate(candidate: dict) -> None:
    require(candidate["format"] == "d9-fixed-domain-cegar-referee-result-v1", "format")
    require(candidate["reviewed_revision"] == FROZEN, "reviewed revision")
    require(candidate["reviewed_tree"] == FROZEN_TREE, "reviewed tree")
    require(candidate["verdict"] == "ACCEPT", "verdict")
    require(candidate["accepted_endpoint"] == "COMMITTED_CEGAR_SEED_FRONTIER_EXACTLY_REPAIRED", "endpoint")
    require(candidate["accepted_classification"] == "EXACT_NULL_NO_D9_COUNTEREXAMPLE", "classification")
    require(all(candidate["gates"].values()), "gate")
    require(candidate["closing_hostile_mutations"] == {"rejected": 8, "total": 8}, "closing hostile census")
    require(candidate["ledger_delta"] == "none", "ledger delta")
    require(candidate["theorem_ledger"] == "2/9", "ledger")
    require(candidate["diagonal_nine"] == "OPEN", "diagonal nine")
    require(candidate["closing_strategy_verdict"] == "PIVOT", "strategy verdict")
    require(candidate["retired_route"] == "SAMPLED_SEPARATOR_CEGAR_WITHOUT_COMPLETE_FIXED_DOMAIN_GENERATOR", "retired route")
    require("FACTOR19069_PROJECTION_FREE_ACTIVE_MARGIN_COMPONENT_GATE1" in candidate["precise_successor"], "precise successor")
    require(candidate["github_write"] is False, "GitHub authority")


def hostile_mutations(stored: dict) -> None:
    mutations = []
    candidate = deepcopy(stored); candidate["reviewed_revision"] = "0" * 40; mutations.append((candidate, "reviewed revision"))
    candidate = deepcopy(stored); candidate["verdict"] = "REJECT"; mutations.append((candidate, "verdict"))
    candidate = deepcopy(stored); candidate["gates"]["producer_independent_replay"] = False; mutations.append((candidate, "gate"))
    candidate = deepcopy(stored); candidate["accepted_classification"] = "D9_COUNTEREXAMPLE"; mutations.append((candidate, "classification"))
    candidate = deepcopy(stored); candidate["theorem_ledger"] = "3/9"; mutations.append((candidate, "ledger"))
    candidate = deepcopy(stored); candidate["closing_strategy_verdict"] = "CONTINUE"; mutations.append((candidate, "strategy verdict"))
    candidate = deepcopy(stored); candidate["precise_successor"] = "sample another pair"; mutations.append((candidate, "precise successor"))
    candidate = deepcopy(stored); candidate["github_write"] = True; mutations.append((candidate, "GitHub authority"))
    for candidate, marker in mutations:
        try:
            validate(candidate)
        except Reject as error:
            require(marker in str(error), f"wrong hostile rejection: {error}")
            continue
        raise Reject(f"hostile mutation accepted: {marker}")


def main() -> None:
    require(git("rev-parse", f"{FROZEN}^{{commit}}") == FROZEN, "frozen commit")
    require(git("rev-parse", f"{FROZEN}^{{tree}}") == FROZEN_TREE, "frozen tree")
    for path, expected in PINS.items():
        data = frozen_bytes(path)
        require(hashlib.sha256(data).hexdigest() == expected, f"frozen pin {path}")
        require((ROOT / path).read_bytes() == data, f"working candidate drift {path}")

    frontier = frozen_json("ops/team/d9-fixed-domain-cegar-constructor/CEGAR_FRONTIER.json")
    constructor = frozen_json("ops/team/d9-fixed-domain-cegar-constructor/RESULT.json")
    falsifier = frozen_json("ops/team/d9-fixed-domain-cegar-falsifier/RESULT.json")
    certificate = frozen_json("ops/team/d9-fixed-domain-cegar-certificate/RESULT.json")
    require(frontier["aggregate"]["seed_families"] == 2, "seed frontier")
    require(frontier["aggregate"]["exact_path_repairs"] == 2, "path repairs")
    require(frontier["aggregate"]["source_realized_counterexamples"] == 0, "counterexample census")
    require(frontier["scope"]["complete_fixed_domain_candidate_generator"] is False, "generator scope")
    require(constructor["classification"] == "EXACT_NULL_NO_D9_COUNTEREXAMPLE", "constructor endpoint")
    require(falsifier["global_common_feasibility_connectivity"] == "UNPROVED", "falsifier scope")
    require(certificate["independence"]["hostile_mutations_rejected"] == 12, "certificate mutations")

    replay(
        "ops/research-team/cycles/2026-09-01-d9-fixed-domain-cegar-gate1/verify_opening_audit.py",
        ("PASS D9 fixed-domain CEGAR gate-1 opening audit", "ledger=2/9"),
    )
    replay(
        "ops/team/d9-fixed-domain-cegar-falsifier/verify_counterexample_attack.py",
        ("PASS D9 fixed-domain CEGAR falsifier", "exact_path_segments=45522"),
    )
    replay(
        "ops/team/d9-fixed-domain-cegar-certificate/verify_cegar_frontier.py",
        ("PASS D9 fixed-domain CEGAR producer-independent certificate", "hostile_mutations=12"),
    )
    replay(
        "ops/research-team/verify_cycle_protocol.py",
        (),
        pass_prefix="PASS research-cycle ",
    )

    result = json.loads(RESULT.read_text(encoding="utf-8"))
    validate(result)
    hostile_mutations(result)
    print("PASS D9 fixed-domain CEGAR gate-1 closing referee")
    print("frozen=55d284e tree=5de3d0b endpoint=EXACT_NULL_NO_D9_COUNTEREXAMPLE")
    print("closing_hostile_mutations=8 ledger=2/9 verdict=PIVOT github_write=false")


if __name__ == "__main__":
    main()
