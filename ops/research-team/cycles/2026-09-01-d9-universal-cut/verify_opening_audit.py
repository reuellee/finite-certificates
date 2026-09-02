#!/usr/bin/env python3
"""Fail-closed verifier for the universal D9 cut opening contract."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[4]
CYCLE = ROOT / "ops/research-team/cycles/2026-09-01-d9-universal-cut"
BASE = "cbe84ccd7273252c81fd4da17ee360a284d2a2a6"
TREE = "da3cd6feca1052ea14ed5036413c72b8f7fadc2a"
STATE_SHA = "e37fad74fae83cf087b2010039e85122866c3b093e34227f28d12759be94a6cf"
TARGET = "D9_UNIVERSAL_FEASIBLE_COMPONENT_CUT_GATE1"


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

    require(audit["format"] == "9dvl-d9-universal-cut-opening-v1", "format")
    canonical = audit["canonical_base"]
    require(canonical["revision"] == BASE, "base revision")
    require(canonical["tree"] == TREE, "base tree")
    require(canonical["ledger"] == "2/9", "opening ledger")
    require(canonical["state"] == "PIVOT_REQUIRED", "opening state")
    require(canonical["canonical_state_sha256"] == STATE_SHA, "state pin")
    require(audit["selected_target"] == TARGET, "selected target")
    require(audit["opening_verdict"] == "PIVOT_SELECT", "opening verdict")

    gate = audit["opening_gate"]
    require(gate["wall_hours"] == 12, "opening wall hours")
    require(gate["cpu_hours"] == 64, "opening cpu hours")
    require(gate["memory_gib"] == 16, "opening memory")
    require(gate["max_obstruction_types"] == 10000, "type ceiling")
    require(gate["max_exact_instances"] == 250000, "instance ceiling")
    require(gate["portable_replay_required"] is True, "portable replay")

    target = audit["target_contract"]
    require(target["positive_endpoint"] == "UNIVERSAL_D9_CUT_OBSTRUCTIONS_UNSAT", "positive endpoint")
    require(target["negative_endpoint"] == "EXACT_D9_TWO_COMPONENT_SEPARATOR", "negative endpoint")
    require(target["null_endpoint"] == "UNIVERSAL_CUT_SCHEMA_COVERAGE_GAP", "null endpoint")
    require(target["timeout_endpoint"] == "HASH_PINNED_D9_CUT_SCHEMA_FRONTIER", "timeout endpoint")
    require(len(target["prohibited_claims"]) >= 6, "prohibited claims")

    for rel, expected in audit["source_pins"].items():
        path = ROOT / rel
        require(path.is_file(), f"missing source {rel}")
        require(sha256(path) == expected, f"source drift {rel}")

    tracks = [
        "d9-universal-cut-prover",
        "d9-universal-cut-circuits",
        "d9-universal-cut-boundary",
        "d9-universal-cut-falsifier",
        "d9-universal-cut-certificate",
        "d9-universal-cut-referee",
    ]
    for track in tracks:
        require(f"track_id: {track}" in orders, f"missing work order {track}")
    require("GitHub is read-only" in orders, "authority")
    require("weighted-link continuation" in orders, "weighted-link prohibition")
    require("82.4" in tournament and "39.4" in tournament, "tournament binding")
    require("12-hour" in cycle and "ca730426" in cycle, "opening gate prose")

    print("PASS universal D9 cut opening audit")
    print(f"base={BASE} tree={TREE} ledger=2/9")
    print("target=D9_UNIVERSAL_FEASIBLE_COMPONENT_CUT_GATE1")
    print("tracks=6 opening_hours=12 max_types=10000 max_instances=250000")


if __name__ == "__main__":
    main()
