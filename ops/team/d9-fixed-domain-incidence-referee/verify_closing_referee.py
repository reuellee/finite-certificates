#!/usr/bin/env python3
"""Frozen-head closing referee for D9 fixed-domain incidence gate 2."""

from __future__ import annotations

from copy import deepcopy
import hashlib
import json
from pathlib import Path
import subprocess
import sys


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
FROZEN = "527e1fa16f65fab40a6b67e4e657f4a657b43e57"
FROZEN_TREE = "585c13a9ec3f9f11c265e13b9c70d3c716a16c81"
RESULT = HERE / "RESULT.json"

PINS = {
    "ops/research-team/cycles/2026-09-01-d9-fixed-domain-incidence-gate2/CYCLE.md": "e57f3bb4ef2fc6157322c572aa9e7866ac23cf8e83e94af4f6c85df4c733b794",
    "ops/research-team/cycles/2026-09-01-d9-fixed-domain-incidence-gate2/OPENING_AUDIT.json": "12bd5a1debe1eb0b2b77cf66b0b604833178de4d07335feeeeb80692f16ac589",
    "ops/research-team/cycles/2026-09-01-d9-fixed-domain-incidence-gate2/WORK_ORDERS.yaml": "a85573622c5cfd51847da936ca53864f101a65a82cd47311afb105b66f51afd5",
    "ops/team/d9-fixed-domain-incidence-constructor/FIXED_DOMAIN_INCIDENCE_PREFLIGHT.json": "244a15ef91a50c6c232f6c04366954f043ecde8ba96e66060d7b8cdac5427bb5",
    "ops/team/d9-fixed-domain-incidence-constructor/RESULT.json": "87f456d471becafe38b7452047fc44f2ef1d6e819b48404bbdcf5e6c97308f4f",
    "ops/team/d9-fixed-domain-incidence-falsifier/RESULT.json": "d869e4df3dd28fc292f905f7fcc9dae0d6cfd17eebaa20f8b112e3466042ed35",
    "ops/team/d9-fixed-domain-incidence-certificate/RESULT.json": "11cbe52b142ba98677c7a1474c62ca3a8dc5bbebfb9462343db9717cd7c2c928",
    "ops/team/d9-fixed-domain-incidence-certificate/verify_gate2_preflight.py": "032eb3c79941ff1a82559b300492df78190dcbb2d3fabb60581a748411845ffb",
}


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
    return git("show", f"{FROZEN}:{path}", binary=True)


def frozen_json(path: str) -> dict:
    return json.loads(frozen_bytes(path).decode("utf-8"))


def replay(relative: str, expected: tuple[str, ...]) -> None:
    result = subprocess.run(
        [sys.executable, "-u", relative],
        cwd=ROOT,
        text=True,
        capture_output=True,
    )
    require(result.returncode == 0, f"replay failed {relative}: {result.stderr[-1000:]}")
    for marker in expected:
        require(marker in result.stdout, f"replay marker missing {relative}: {marker}")


def validate_result(candidate: dict) -> None:
    require(candidate["format"] == "d9-fixed-domain-incidence-referee-result-v1", "format")
    require(candidate["reviewed_revision"] == FROZEN, "reviewed revision")
    require(candidate["reviewed_tree"] == FROZEN_TREE, "reviewed tree")
    require(candidate["verdict"] == "ACCEPT", "verdict")
    require(candidate["accepted_endpoint"] == "LOW_DEGREE_PROJECTION_SPECIALIZATION_IS_NONGENERIC", "endpoint")
    require(candidate["accepted_classification"] == "EXACT_NEGATIVE_PROJECTION_ENDPOINT", "classification")
    require(all(candidate["gates"].values()), "gate")
    require(candidate["closing_hostile_mutations"] == {"rejected": 6, "total": 6}, "closing hostile census")
    require(candidate["ledger_delta"] == "none", "ledger delta")
    require(candidate["theorem_ledger"] == "2/9", "ledger")
    require(candidate["closing_strategy_verdict"] == "PIVOT", "strategy verdict")
    require("second constructive cycle" in candidate["pivot_reason"], "anti-stagnation reason")
    require(candidate["github_write"] is False, "GitHub authority")


def hostile_mutations(stored: dict) -> None:
    mutations = []
    candidate = deepcopy(stored); candidate["reviewed_revision"] = "0" * 40; mutations.append((candidate, "reviewed revision"))
    candidate = deepcopy(stored); candidate["verdict"] = "REJECT"; mutations.append((candidate, "verdict"))
    candidate = deepcopy(stored); candidate["gates"]["low_degree_projection_replay"] = False; mutations.append((candidate, "gate"))
    candidate = deepcopy(stored); candidate["theorem_ledger"] = "3/9"; mutations.append((candidate, "ledger"))
    candidate = deepcopy(stored); candidate["closing_strategy_verdict"] = "CONTINUE"; mutations.append((candidate, "strategy verdict"))
    candidate = deepcopy(stored); candidate["github_write"] = True; mutations.append((candidate, "GitHub authority"))
    for candidate, expected in mutations:
        try:
            validate_result(candidate)
        except Reject as error:
            require(expected in str(error), f"wrong hostile rejection: {error}")
            continue
        raise Reject(f"hostile mutation accepted: {expected}")


def main() -> None:
    require(git("rev-parse", f"{FROZEN}^{{commit}}") == FROZEN, "frozen commit")
    require(git("rev-parse", f"{FROZEN}^{{tree}}") == FROZEN_TREE, "frozen tree")
    for path, expected in PINS.items():
        data = frozen_bytes(path)
        require(hashlib.sha256(data).hexdigest() == expected, f"frozen pin {path}")
        require((ROOT / path).read_bytes() == data, f"working candidate drift {path}")

    preflight = frozen_json(
        "ops/team/d9-fixed-domain-incidence-constructor/FIXED_DOMAIN_INCIDENCE_PREFLIGHT.json"
    )
    constructor = frozen_json("ops/team/d9-fixed-domain-incidence-constructor/RESULT.json")
    falsifier = frozen_json("ops/team/d9-fixed-domain-incidence-falsifier/RESULT.json")
    certificate = frozen_json("ops/team/d9-fixed-domain-incidence-certificate/RESULT.json")
    require(preflight["fixed_domain"]["active_set_stabilizer_order"] == 1, "stabilizer")
    require(preflight["pair_frontier"]["fixed_domain_stabilizer_pair_orbits"] == 6_260_491, "pair frontier")
    require(preflight["projection_screen"]["status_census"] == {"GENERIC_EMPTY": 10, "NONGENERIC_POSITIVE_DIMENSION": 73}, "projection census")
    require(preflight["critical_enumeration_authorized"] is False, "critical authorization")
    require(constructor["classification"] == "EXACT_NEGATIVE_PROJECTION_ENDPOINT", "constructor endpoint")
    require(falsifier["classification"] == "FATAL_TO_SELECTED_QUOTIENT_AND_PROJECTION", "falsifier endpoint")
    require(falsifier["quotient_counterexample"]["image_is_active"] is False, "quotient witness")
    require(falsifier["projection_counterexample"]["wall_restriction_on_polar_space"] == "IDENTICALLY_ZERO", "projection witness")
    require(certificate["independence"]["hostile_mutations_rejected"] == 8, "certificate mutations")

    replay(
        "ops/research-team/cycles/2026-09-01-d9-fixed-domain-incidence-gate2/verify_opening_audit.py",
        ("PASS D9 fixed-domain incidence gate-2 opening audit", "ledger=2/9"),
    )
    replay(
        "ops/team/d9-fixed-domain-incidence-certificate/verify_gate2_preflight.py",
        ("PASS D9 fixed-domain incidence gate-2 preflight", "hostile_mutations=8", "ledger=2/9"),
    )
    replay(
        "ops/research-team/verify_cycle_protocol.py",
        ("PASS research-cycle strategy/storage/publication protocol",),
    )

    result = json.loads(RESULT.read_text(encoding="utf-8"))
    validate_result(result)
    hostile_mutations(result)
    print("PASS D9 fixed-domain incidence gate-2 closing referee")
    print("frozen=527e1fa tree=585c13a endpoint=EXACT_NEGATIVE_PROJECTION_ENDPOINT")
    print("closing_hostile_mutations=6 ledger=2/9 verdict=PIVOT github_write=false")


if __name__ == "__main__":
    main()
