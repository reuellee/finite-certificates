#!/usr/bin/env python3
"""Fail-closed verifier for the D9 component-roadmap opening contract."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[4]
CYCLE = ROOT / "ops/research-team/cycles/2026-09-01-d9-component-roadmap"
BASE = "a6cae1e774420a96ca0ba8b76ee990c3e0b11bdc"
TREE = "d99658f9ecde22fa3386d769a2fe72ea407a8ec1"
STATE_SHA = "6b22f3f8da550fa14ea13700ff632eb3db53c40316a0e1844a7762784cfaf811"
TARGET = "D9_COMPONENT_COMPLETE_ROADMAP_GATE1"


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(f"FAIL: {message}")


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    audit = json.loads((CYCLE / "OPENING_AUDIT.json").read_text())
    orders = (CYCLE / "WORK_ORDERS.yaml").read_text()
    cycle = (CYCLE / "CYCLE.md").read_text()
    tournament = (CYCLE / "STRATEGY_TOURNAMENT.md").read_text()

    require(audit["format"] == "9dvl-d9-component-roadmap-opening-v1", "format")
    canonical = audit["canonical_base"]
    require(canonical["revision"] == BASE, "base revision")
    require(canonical["tree"] == TREE, "base tree")
    require(canonical["ledger"] == "2/9", "opening ledger")
    require(canonical["state"] == "PIVOT_REQUIRED", "opening state")
    require(canonical["canonical_state_sha256"] == STATE_SHA, "state pin")
    require(audit["selected_target"] == TARGET, "selected target")
    require(audit["opening_verdict"] == "PIVOT_SELECT", "opening verdict")

    contract = audit["target_contract"]
    require(contract["domain"] == "ROW_2599_S12_37_ACTIVE_SECTOR_3539_FACTOR_CLASSES", "domain")
    require(contract["theorem_promotion_authorized"] is False, "promotion scope")
    require(len(contract["prohibited_claims"]) >= 6, "prohibited claims")

    gate = audit["opening_gate"]
    require(gate["wall_hours"] == 4, "wall hours")
    require(gate["cpu_hours"] == 24, "cpu hours")
    require(gate["memory_gib"] == 16, "memory")
    require(gate["deterministic_perturbations"] == 1, "perturbation count")
    require(gate["max_exact_critical_systems"] == 100000, "system ceiling")
    require(gate["max_certificate_bytes"] == 500000000, "certificate ceiling")
    require(gate["critical_enumeration_authorized_before_canaries"] is False, "canary gate")
    require(len(gate["required_canaries"]) == 4, "canary count")

    for rel, expected in audit["source_pins"].items():
        path = ROOT / rel
        require(path.is_file(), f"missing source {rel}")
        require(sha256(path) == expected, f"source drift {rel}")

    tracks = [
        "d9-component-roadmap-constructor",
        "d9-component-roadmap-falsifier",
        "d9-component-roadmap-certificate",
        "d9-component-roadmap-referee",
    ]
    for track in tracks:
        require(f"track_id: {track}" in orders, f"missing work order {track}")

    require("GitHub is read-only" in orders, "publication authority")
    require("100000 systems" in orders, "system ceiling prose")
    require("36" in tournament and "33" in tournament and "32" in tournament, "strategy scores")
    require("Aliasing" in cycle and "Projection closure" in cycle, "first two canaries")
    require("Boundary residence" in cycle and "Singularity" in cycle, "last two canaries")
    require("No fixed-domain endpoint changes the theorem ledger" in cycle, "scope nonconsequence")

    print("PASS D9 component-roadmap opening audit")
    print(f"base={BASE} tree={TREE} ledger=2/9")
    print(f"target={TARGET} canaries=4 systems=100000 bytes=500000000")


if __name__ == "__main__":
    main()

