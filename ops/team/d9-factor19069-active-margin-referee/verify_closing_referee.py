#!/usr/bin/env python3
"""Frozen-head closing referee for factor-19069 active-margin gate 1."""

from __future__ import annotations

from copy import deepcopy
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
CYCLE = ROOT / "ops" / "research-team" / "cycles" / "2026-09-01-d9-row2599-factor19069-active-margin-gate1"
RESULT = HERE / "RESULT.json"
MANIFEST = CYCLE / "CLOSING_MANIFEST.json"
REPORT = CYCLE / "CYCLE_REPORT.md"
CLEAN = CYCLE / "CLEAN_REPLAY.json"
CANDIDATE = "d9c43724ba0b82f3aeee69b4afa205bad2aa27f9"
CANDIDATE_TREE = "72ec9cffdb00969ae534daf742b45d05f4d8350a"


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


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def validate(candidate: dict) -> None:
    require(candidate["format"] == "d9-factor19069-active-margin-referee-result-v1", "format")
    require(candidate["reviewed_revision"] == CANDIDATE, "reviewed revision")
    require(candidate["reviewed_tree"] == CANDIDATE_TREE, "reviewed tree")
    require(candidate["verdict"] == "ACCEPT", "verdict")
    require(candidate["accepted_classification"] == "EXACT_FAIL_CLOSED_PARENT_RESIDENCE_NULL", "classification")
    require(candidate["accepted_endpoint"].endswith("FIRST_UNCLASSIFIED_STRATUM"), "endpoint")
    require(all(candidate["gates"].values()), "gates")
    require(candidate["closing_hostile_mutations"] == {"rejected": 10, "total": 10}, "closing hostile mutations")
    require(candidate["component_samples"] == 0, "component samples")
    require(candidate["global_component_classification"] == "ABSENT_FAIL_CLOSED", "component classification")
    require(candidate["ledger_delta"] == "none", "ledger delta")
    require(candidate["theorem_ledger"] == "2/9", "ledger")
    require(candidate["diagonal_nine"] == "OPEN", "diagonal nine")
    require(candidate["closing_strategy_verdict"] == "PIVOT", "strategy verdict")
    require(candidate["retired_route"] == "UNFILTERED_NONSMOOTH_ACTIVE_SET_ENUMERATION_FOR_FACTOR19069", "retired route")
    require(candidate["precise_successor"].startswith("D9_ROW2599_FACTOR19069_FACTORED_BARRIER_COMPONENT_SAMPLER_GATE1"), "successor")
    require(candidate["github_write"] is False, "GitHub mode")


def hostile_mutations(stored: dict) -> None:
    mutations = []
    altered = deepcopy(stored); altered["reviewed_revision"] = "0" * 40; mutations.append((altered, "reviewed revision"))
    altered = deepcopy(stored); altered["verdict"] = "REJECT"; mutations.append((altered, "verdict"))
    altered = deepcopy(stored); altered["accepted_classification"] = "COMPLETE"; mutations.append((altered, "classification"))
    altered = deepcopy(stored); altered["gates"]["clean_replay"] = False; mutations.append((altered, "gates"))
    altered = deepcopy(stored); altered["component_samples"] = 1; mutations.append((altered, "component samples"))
    altered = deepcopy(stored); altered["global_component_classification"] = "ALL_ATTACHED"; mutations.append((altered, "component classification"))
    altered = deepcopy(stored); altered["theorem_ledger"] = "3/9"; mutations.append((altered, "ledger"))
    altered = deepcopy(stored); altered["diagonal_nine"] = "PROVED"; mutations.append((altered, "diagonal nine"))
    altered = deepcopy(stored); altered["closing_strategy_verdict"] = "CONTINUE"; mutations.append((altered, "strategy verdict"))
    altered = deepcopy(stored); altered["precise_successor"] = "SAMPLE_ANOTHER_SEPARATOR"; mutations.append((altered, "successor"))
    for candidate, marker in mutations:
        try:
            validate(candidate)
        except Reject as error:
            require(marker in str(error), f"wrong hostile rejection {marker}: {error}")
            continue
        raise Reject(f"hostile mutation accepted: {marker}")


def replay(script: str) -> None:
    environment = dict(os.environ)
    environment["PYTHONDONTWRITEBYTECODE"] = "1"
    subprocess.run([sys.executable, "-u", script], cwd=ROOT, env=environment, check=True)


def main() -> None:
    require(git("rev-parse", f"{CANDIDATE}^{{tree}}") == CANDIDATE_TREE, "candidate tree")
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    require(manifest["reviewed_revision"] == CANDIDATE, "manifest revision")
    require(manifest["reviewed_tree"] == CANDIDATE_TREE, "manifest tree")
    for path, expected in manifest["pins"].items():
        frozen = git("show", f"{CANDIDATE}:{path}", binary=True)
        require(sha256(frozen) == expected, f"candidate pin {path}")
        require((ROOT / path).read_bytes() == frozen, f"post-candidate drift {path}")
    clean = json.loads(CLEAN.read_text(encoding="utf-8"))
    require(clean["candidate_revision"] == CANDIDATE, "clean revision")
    require(clean["candidate_tree"] == CANDIDATE_TREE, "clean tree")
    require(clean["results"]["worktree_clean"] is True, "clean worktree")
    require(all(value != "FAIL" for value in clean["results"].values()), "clean results")
    replay("ops/research-team/cycles/2026-09-01-d9-row2599-factor19069-active-margin-gate1/verify_opening_audit.py")
    replay("ai/omreal/verify_diag3_pair_fullsupport_component_collar.py")
    replay("ops/team/d9-factor19069-active-margin-falsifier/verify_active_margin_falsifier.py")
    replay("ops/team/d9-factor19069-active-margin-certificate/verify_active_margin_certificate.py")
    report = REPORT.read_text(encoding="utf-8")
    for required in (
        CANDIDATE,
        CANDIDATE_TREE,
        "Closing ledger: `2/9`",
        "EXACT_FAIL_CLOSED_PARENT_RESIDENCE_NULL",
        "75,816,847,319",
        "Ledger delta: **none**",
        "D9_ROW2599_FACTOR19069_FACTORED_BARRIER_COMPONENT_SAMPLER_GATE1",
        "GitHub remained read-only",
    ):
        require(required in report, f"report field {required}")
    stored = json.loads(RESULT.read_text(encoding="utf-8"))
    validate(stored)
    hostile_mutations(stored)
    print("PASS frozen-head factor-19069 active-margin closing referee")
    print("PASS exact null, clean replay, ledger delta none, strategy PIVOT")
    print("PASS closing_hostile_mutations=10 successor=FACTORED_BARRIER_COMPONENT_SAMPLER")


if __name__ == "__main__":
    main()
