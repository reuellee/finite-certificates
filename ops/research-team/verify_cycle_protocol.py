#!/usr/bin/env python3
"""Fail-closed audit for research cycles governed by PROTOCOL.md.

Cycles dated 2026-08-29 or later must carry an opening strategy comparison,
a bounded target, a closing strategy gate, and the authorization that applied
when the cycle opened.  Historical GitHub-publication authority is preserved
through 2026-08-31; cycles from 2026-09-01 onward are Library-first and keep
GitHub read-only.  Cycles based on a revision containing the mandatory
solution-convergence protocol must also carry an opening proof-distance
contract and, when closed, a convergence verdict.  The audit deliberately
uses only the standard library so it can run in the repository-wide verifier
suite.
"""

from __future__ import annotations

from pathlib import Path
import re
import subprocess


ROOT = Path(__file__).resolve().parents[2]
TEAM_ROOT = ROOT / "ops" / "research-team"
CYCLES_ROOT = TEAM_ROOT / "cycles"
FIRST_GOVERNED_CYCLE = "2026-08-29-"
CURRENT_AUTHORIZATION_START = "2026-09-01-"

LEGACY_AUTHORIZATION_MARKER = (
    "The historical publication authorization preserved verbatim for cycles dated"
)
CURRENT_AUTHORIZATION_MARKER = (
    "The current storage and publication authorization to copy verbatim into every"
)
SOLUTION_CONVERGENCE_PROTOCOL_MARKER = (
    "## 3. Mandatory solution-convergence gate"
)

LEGACY_AUTHORIZATION_PHRASES = (
    "public GitHub repository `reuellee/finite-certificates`",
    "run or rerun CI",
    "merge only after required checks pass",
    "`Projects/research-backups`",
    "does not permit publishing secrets",
    "paid external compute or paid APIs",
    "force-pushing",
    "do not substitute `gh`",
)

CURRENT_AUTHORIZATION_PHRASES = (
    "ChatGPT Library as the canonical durable working branch",
    "Google Drive `Projects/research-backups`",
    "GitHub is read-only",
    "do not push commits",
    "trigger or rerun CI",
    "until a new explicit user instruction",
    "Local scratch is ephemeral and is not an authority",
    "paid external compute or paid APIs",
    "force-pushing",
)

NATIVE_STORAGE_AUTHORIZATION_PHRASES = (
    "saved local Codex project",
    "native-filesystem recovery mirror",
    r"G:\My Drive\Projects\research-backups",
    "Never invoke the Google Drive connector",
    "never block on connector approval",
    "GitHub is read-only",
    "paid/external compute",
    "force-push",
)

CYCLE_PHRASES = (
    "Canonical base revision:",
    "Opening theorem ledger:",
    "## Mandatory opening strategy evaluation",
    "Ledger leverage",
    "Quantifier readiness",
    "Coverage burden",
    "Terminality",
    "Structural compression",
    "Independent verification",
    "Resource / information",
    "Stagnation risk",
    "## Bounded target",
    "## Obligation graph",
    "## Canonical input accounting",
    "## Concurrency and non-overlap",
    "## Roles",
    "## Resource ceiling",
    "## Closing requirements",
    "CONTINUE",
    "PIVOT",
    "RETIRE",
    "STOP",
)

WORK_ORDER_PHRASES = (
    "base_revision:",
    "opening_ledger:",
    "strategy_gate:",
    "opening_verdict:",
    "closing_required: true",
    "stagnation_rule:",
    "work_orders:",
    "resource_ceiling:",
    "stop_rule:",
    "prohibited_scope:",
    "worker_restrictions:",
)

CONVERGENCE_CYCLE_PHRASES = (
    "## Mandatory solution-convergence evaluation",
    "Proof-distance vector",
    "Score deficit",
    "Open load-bearing obligations",
    "Certified exhaustive residual",
    "Global coverage",
    "Same-blocker streak",
    "Zero-ledger streak",
    "Convergence hypothesis",
    "Minimum acceptable decrease",
    "Mid-cycle convergence check",
    "Automatic strategy-reset rule",
)

CONVERGENCE_WORK_ORDER_PHRASES = (
    "solution_convergence_gate:",
    "proof_distance:",
    "opening_score:",
    "score_deficit:",
    "open_load_bearing_obligations:",
    "certified_exhaustive_residual:",
    "global_coverage:",
    "same_blocker_streak:",
    "zero_ledger_streak:",
    "convergence_hypothesis:",
    "minimum_acceptable_delta:",
    "mid_cycle_checkpoint:",
    "closing_classification_required: true",
    "automatic_pivot_rule:",
)

CONVERGENCE_REPORT_PHRASES = (
    "## Mandatory solution-convergence verdict",
    "Opening proof-distance vector",
    "Closing proof-distance vector",
    "Mid-cycle convergence check",
    "Trajectory classification",
    "Automatic strategy-reset result",
    "Same-route continuation justified",
)


def require_phrases(text: str, phrases: tuple[str, ...], label: str) -> None:
    missing = [phrase for phrase in phrases if phrase not in text]
    if missing:
        raise AssertionError(f"{label}: missing required phrases {missing}")


def require_any_phrase(text: str, phrases: tuple[str, ...], label: str) -> None:
    if not any(phrase in text for phrase in phrases):
        raise AssertionError(f"{label}: missing every accepted phrase {phrases}")


def require_phrases_collapsed(
    text: str, phrases: tuple[str, ...], label: str
) -> None:
    collapsed = " ".join(text.split())
    missing = [
        phrase for phrase in phrases if " ".join(phrase.split()) not in collapsed
    ]
    if missing:
        raise AssertionError(f"{label}: missing required phrases {missing}")


def protocol_authorization(text: str, marker: str) -> str:
    marker_index = text.find(marker)
    if marker_index < 0:
        raise AssertionError("PROTOCOL.md: missing standing authorization marker")
    lines = text[marker_index:].splitlines()
    quoted: list[str] = []
    for line in lines:
        if line.startswith("> "):
            quoted.append(line[2:])
        elif quoted:
            break
    if not quoted:
        raise AssertionError("PROTOCOL.md: missing standing authorization quote")
    return "\n".join(quoted)


def work_order_authorization(text: str, label: str, anchor: str) -> str:
    marker = f"{anchor}: &{anchor} |\n"
    if marker not in text:
        raise AssertionError(f"{label}: missing publication authorization anchor")
    block = text.split(marker, 1)[1]
    quoted: list[str] = []
    for line in block.splitlines():
        if line.startswith("  "):
            quoted.append(line[2:])
        else:
            break
    if not quoted:
        raise AssertionError(f"{label}: empty publication authorization anchor")
    return "\n".join(quoted)


def protocol_at_revision(revision: str, label: str) -> str:
    commit = subprocess.run(
        ["git", "cat-file", "-e", f"{revision}^{{commit}}"],
        cwd=ROOT,
        check=False,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    if commit.returncode != 0:
        raise AssertionError(f"{label}: unknown base revision {revision}")
    result = subprocess.run(
        ["git", "show", f"{revision}:ops/research-team/PROTOCOL.md"],
        cwd=ROOT,
        check=False,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    if result.returncode != 0:
        # The earliest governed cycles predate the repository protocol file.
        # They remain covered by the historical phrase checks above.
        return ""
    return result.stdout


def audit_cycle(cycle_dir: Path, protocol_text: str) -> tuple[int, int]:
    cycle_path = cycle_dir / "CYCLE.md"
    work_orders_path = cycle_dir / "WORK_ORDERS.yaml"
    if not cycle_path.is_file() or not work_orders_path.is_file():
        raise AssertionError(
            f"{cycle_dir.name}: governed cycle requires CYCLE.md and WORK_ORDERS.yaml"
        )

    cycle_text = cycle_path.read_text(encoding="utf-8")
    work_orders_text = work_orders_path.read_text(encoding="utf-8")
    require_phrases(cycle_text, CYCLE_PHRASES, cycle_dir.name)
    require_any_phrase(
        cycle_text,
        ("## Publication authority", "## Storage and publication authority"),
        cycle_dir.name,
    )
    require_phrases(work_orders_text, WORK_ORDER_PHRASES, cycle_dir.name)
    current_epoch = cycle_dir.name >= CURRENT_AUTHORIZATION_START
    if "storage_authorization: &storage_authorization |" in work_orders_text:
        authorization_anchor = "storage_authorization"
        require_phrases_collapsed(
            work_orders_text,
            NATIVE_STORAGE_AUTHORIZATION_PHRASES,
            cycle_dir.name,
        )
        work_order_authorization(
            work_orders_text, cycle_dir.name, authorization_anchor
        )
    else:
        authorization_anchor = "publication_authorization"
        authorization_phrases = (
            CURRENT_AUTHORIZATION_PHRASES
            if current_epoch
            else LEGACY_AUTHORIZATION_PHRASES
        )
        authorization_marker = (
            CURRENT_AUTHORIZATION_MARKER
            if current_epoch
            else LEGACY_AUTHORIZATION_MARKER
        )
        if current_epoch:
            require_phrases_collapsed(
                work_orders_text, authorization_phrases, cycle_dir.name
            )
        else:
            require_phrases(work_orders_text, authorization_phrases, cycle_dir.name)
        expected_authorization = protocol_authorization(
            protocol_text, authorization_marker
        )
        actual_authorization = work_order_authorization(
            work_orders_text, cycle_dir.name, authorization_anchor
        )
        if actual_authorization != expected_authorization:
            raise AssertionError(
                f"{cycle_dir.name}: epoch authorization is not verbatim"
            )

    base_match = re.search(r"^base_revision:\s*([0-9a-f]{40})$", work_orders_text, re.M)
    if base_match is None:
        raise AssertionError(f"{cycle_dir.name}: base_revision must be a full SHA-1")
    base_revision = base_match.group(1)
    if base_revision not in cycle_text:
        raise AssertionError(f"{cycle_dir.name}: CYCLE.md and work-order base disagree")

    base_protocol = protocol_at_revision(base_revision, cycle_dir.name)
    convergence_governed = (
        SOLUTION_CONVERGENCE_PROTOCOL_MARKER in base_protocol
    )
    if convergence_governed:
        require_phrases(
            cycle_text,
            CONVERGENCE_CYCLE_PHRASES,
            f"{cycle_dir.name} convergence opening",
        )
        require_phrases(
            work_orders_text,
            CONVERGENCE_WORK_ORDER_PHRASES,
            f"{cycle_dir.name} convergence work orders",
        )
        cycle_report_path = cycle_dir / "CYCLE_REPORT.md"
        if cycle_report_path.is_file():
            require_phrases(
                cycle_report_path.read_text(encoding="utf-8"),
                CONVERGENCE_REPORT_PHRASES,
                f"{cycle_dir.name} convergence report",
            )

    tracks = len(re.findall(r"^\s+- track_id:\s*\S+", work_orders_text, re.M))
    auth_uses = len(
        re.findall(
            rf"^\s+{authorization_anchor}:\s*\*{authorization_anchor}\s*$",
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

    for heading in (
        "## Publication authority",
        "## Storage and publication authority",
    ):
        require_any_phrase(heading, (heading,), "hostile authority heading")
    try:
        require_any_phrase(
            "## Unrelated heading",
            ("## Publication authority", "## Storage and publication authority"),
            "hostile authority heading",
        )
    except AssertionError:
        pass
    else:
        raise AssertionError("hostile authority-heading canary accepted no authority")

    for phrases in (
        LEGACY_AUTHORIZATION_PHRASES,
        CURRENT_AUTHORIZATION_PHRASES,
        NATIVE_STORAGE_AUTHORIZATION_PHRASES,
    ):
        good_authorization = "\n".join(phrases)
        for phrase in phrases:
            try:
                require_phrases(
                    good_authorization.replace(phrase, "", 1),
                    phrases,
                    "hostile",
                )
            except AssertionError:
                continue
            raise AssertionError(
                f"hostile authorization canary accepted removal of {phrase!r}"
            )

    for phrases in (
        CONVERGENCE_CYCLE_PHRASES,
        CONVERGENCE_WORK_ORDER_PHRASES,
        CONVERGENCE_REPORT_PHRASES,
    ):
        good = "\n".join(phrases)
        for phrase in phrases:
            try:
                require_phrases(good.replace(phrase, "", 1), phrases, "hostile")
            except AssertionError:
                continue
            raise AssertionError(
                f"hostile convergence canary accepted removal of {phrase!r}"
            )


def main() -> None:
    protocol = TEAM_ROOT / "PROTOCOL.md"
    if not protocol.is_file():
        raise AssertionError("missing ops/research-team/PROTOCOL.md")
    protocol_text = protocol.read_text(encoding="utf-8")
    require_phrases(
        protocol_text,
        (
            "## 2. Mandatory pre-cycle strategy evaluation",
            SOLUTION_CONVERGENCE_PROTOCOL_MARKER,
            "## 5. Mandatory post-cycle strategy evaluation",
            "## 6. Evidence, storage, and publication gates",
            "two consecutive cycles",
            "three consecutive zero-ledger cycles",
            "mid-cycle convergence check",
            LEGACY_AUTHORIZATION_MARKER,
            CURRENT_AUTHORIZATION_MARKER,
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
        tracks, _ = audit_cycle(cycle_dir, protocol_text)
        track_count += tracks
    hostile_canaries()
    print(
        "PASS research-cycle strategy/convergence/storage/publication protocol:",
        len(governed),
        "cycles,",
        track_count,
        "authorized work orders",
    )


if __name__ == "__main__":
    main()
