#!/usr/bin/env python3
"""Fail-closed audit for research cycles governed by PROTOCOL.md.

Cycles dated 2026-08-29 or later must carry an opening strategy comparison,
a bounded target, a closing strategy gate, and the standing publication
authorization in every work order.  The audit deliberately uses only the
standard library so it can run in the repository-wide verifier suite.
"""

from __future__ import annotations

from pathlib import Path
import re


ROOT = Path(__file__).resolve().parents[2]
TEAM_ROOT = ROOT / "ops" / "research-team"
CYCLES_ROOT = TEAM_ROOT / "cycles"
FIRST_GOVERNED_CYCLE = "2026-08-29-"

AUTHORIZATION_PHRASES = (
    "public GitHub repository reuellee/finite-certificates",
    "run or rerun CI",
    "merge only after required checks pass",
    "Projects/research-backups",
    "does not permit publishing secrets",
    "paid external compute or paid APIs",
    "force-pushing",
    "do not substitute gh",
    "they may not merge or change the theorem ledger",
)

CYCLE_PHRASES = (
    "Canonical base revision:",
    "Opening theorem ledger:",
    "## Mandatory opening strategy evaluation",
    "## Bounded target",
    "## Obligation graph",
    "## Resource ceiling",
    "## Publication authority",
    "## Closing requirements",
    "CONTINUE",
    "PIVOT",
    "RETIRE",
)

WORK_ORDER_PHRASES = (
    "base_revision:",
    "opening_ledger:",
    "publication_authorization:",
    "strategy_gate:",
    "opening_verdict:",
    "closing_required: true",
    "stagnation_rule:",
    "work_orders:",
    "resource_ceiling:",
    "stop_rule:",
    "prohibited_scope:",
)


def require_phrases(text: str, phrases: tuple[str, ...], label: str) -> None:
    missing = [phrase for phrase in phrases if phrase not in text]
    if missing:
        raise AssertionError(f"{label}: missing required phrases {missing}")


def audit_cycle(cycle_dir: Path) -> tuple[int, int]:
    cycle_path = cycle_dir / "CYCLE.md"
    work_orders_path = cycle_dir / "WORK_ORDERS.yaml"
    if not cycle_path.is_file() or not work_orders_path.is_file():
        raise AssertionError(
            f"{cycle_dir.name}: governed cycle requires CYCLE.md and WORK_ORDERS.yaml"
        )

    cycle_text = cycle_path.read_text(encoding="utf-8")
    work_orders_text = work_orders_path.read_text(encoding="utf-8")
    require_phrases(cycle_text, CYCLE_PHRASES, cycle_dir.name)
    require_phrases(work_orders_text, WORK_ORDER_PHRASES, cycle_dir.name)
    require_phrases(work_orders_text, AUTHORIZATION_PHRASES, cycle_dir.name)

    base_match = re.search(r"^base_revision:\s*([0-9a-f]{40})$", work_orders_text, re.M)
    if base_match is None:
        raise AssertionError(f"{cycle_dir.name}: base_revision must be a full SHA-1")
    if base_match.group(1) not in cycle_text:
        raise AssertionError(f"{cycle_dir.name}: CYCLE.md and work-order base disagree")

    tracks = len(re.findall(r"^\s+- track_id:\s*\S+", work_orders_text, re.M))
    auth_uses = len(
        re.findall(
            r"^\s+publication_authorization:\s*\*publication_authorization\s*$",
            work_orders_text,
            re.M,
        )
    )
    if tracks < 3:
        raise AssertionError(f"{cycle_dir.name}: expected coordinator-separated research roles")
    if auth_uses != tracks:
        raise AssertionError(
            f"{cycle_dir.name}: publication authorization appears in {auth_uses}/{tracks} work orders"
        )
    return tracks, auth_uses


def hostile_canaries() -> None:
    good_cycle = "\n".join(CYCLE_PHRASES)
    for phrase in CYCLE_PHRASES:
        try:
            require_phrases(good_cycle.replace(phrase, "", 1), CYCLE_PHRASES, "hostile")
        except AssertionError:
            continue
        raise AssertionError(f"hostile cycle canary accepted removal of {phrase!r}")

    good_authorization = "\n".join(AUTHORIZATION_PHRASES)
    for phrase in AUTHORIZATION_PHRASES:
        try:
            require_phrases(
                good_authorization.replace(phrase, "", 1),
                AUTHORIZATION_PHRASES,
                "hostile",
            )
        except AssertionError:
            continue
        raise AssertionError(f"hostile authorization canary accepted removal of {phrase!r}")


def main() -> None:
    protocol = TEAM_ROOT / "PROTOCOL.md"
    if not protocol.is_file():
        raise AssertionError("missing ops/research-team/PROTOCOL.md")
    protocol_text = protocol.read_text(encoding="utf-8")
    require_phrases(
        protocol_text,
        (
            "## 2. Mandatory pre-cycle strategy evaluation",
            "## 4. Mandatory post-cycle strategy evaluation",
            "## 5. Evidence and publication gates",
            "two consecutive cycles",
        ),
        "PROTOCOL.md",
    )

    governed = sorted(
        path
        for path in CYCLES_ROOT.iterdir()
        if path.is_dir() and path.name >= FIRST_GOVERNED_CYCLE
    )
    if not governed:
        raise AssertionError("no governed research cycles discovered")

    track_count = 0
    for cycle_dir in governed:
        tracks, _ = audit_cycle(cycle_dir)
        track_count += tracks
    hostile_canaries()
    print(
        "PASS research-cycle strategy/publication protocol:",
        len(governed),
        "cycles,",
        track_count,
        "authorized work orders",
    )


if __name__ == "__main__":
    main()
