#!/usr/bin/env python3
"""Fail-closed replay of the D9 fixed-domain gate-2 opening contract."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
AUDIT = HERE / "OPENING_AUDIT.json"


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for block in iter(lambda: source.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def main() -> None:
    audit = json.loads(AUDIT.read_text(encoding="utf-8"))
    require(
        audit["format"] == "d9-fixed-domain-incidence-gate2-opening-audit-v1",
        "format",
    )
    require(
        audit["base_revision"] == "32e2b37bf54c53982cb58a3b8d026734f9ab1113",
        "base revision",
    )
    require(
        audit["base_tree"] == "689d1a5fb981fd2d52f7adb88721d9c7d3a01228",
        "base tree",
    )
    require(audit["opening_ledger"] == "2/9", "ledger")
    require(audit["opening_verdict"] == "CONTINUE", "opening verdict")
    require(
        audit["selected_target"] == "D9_FIXED_DOMAIN_INCIDENCE_GATE2",
        "target",
    )
    ceilings = audit["ceilings"]
    require(ceilings["label_permutations"] == 40_320, "permutation ceiling")
    require(ceilings["active_factors"] == 3_539, "factor ceiling")
    require(ceilings["low_degree_factors"] == 83, "low-degree ceiling")
    require(ceilings["total_systems"] == 100_000, "system ceiling")
    require(ceilings["remaining_pair_systems"] == 96_461, "pair budget")
    for relative, expected in audit["source_pins"].items():
        path = ROOT / relative
        require(path.is_file(), f"missing source {relative}")
        require(sha256(path) == expected, f"source drift {relative}")
    require(
        audit["authorization"]
        == {
            "critical_enumeration": False,
            "ledger_change": False,
            "github_write": False,
        },
        "authorization",
    )
    print("PASS D9 fixed-domain incidence gate-2 opening audit")
    print("base=32e2b37 ledger=2/9 critical_enumeration=DENIED")


if __name__ == "__main__":
    main()
