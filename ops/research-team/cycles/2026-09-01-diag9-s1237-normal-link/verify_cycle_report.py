#!/usr/bin/env python3
"""Fail-closed verifier for the closed D9 S12,37 normal-link cycle."""

from __future__ import annotations

from copy import deepcopy
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[4]
HERE = Path(__file__).resolve().parent
MANIFEST = HERE / "SOURCE_MANIFEST.json"
REPORT = HERE / "CYCLE_REPORT.md"
BASE = "c55d896cc5c0370e993b793992a2f05d894e0095"
OPENING = "c6bd7a6afeda0888fc950710b941cac6f6c9bf95"
REVIEWED = "5efbd07a25b818306f9fd22597fd81a0f2091309"
REFEREE = "ca730426cdd5847ae262ddc29c6f4ae98369eba3"
ENDPOINT = "NORMAL_LINK_REDUCTION_NO_GO"

EXPECTED_SOURCE_PINS = {
    "README.md": "ac98d240746c6914edf1436b3f454caff1b131367aaab78347e6323618b1a047",
    "ai/omreal/NINE_DIAGONAL_STATUS.md": "07c146e835f6a62c29ab653d353d73469df1e6022018ffec76f6775b65ca7ae2",
    "ai/omreal/RESEARCH_OPERATING_SYSTEM.md": "db5a279424bd3e3f7ce5b6d60dded30446e4b373d709d1bdf1d9b714b8495f20",
    "ai/omreal/data/CANONICAL_RESEARCH_STATE_V2.json": "508d5433d33eeb5be915e1749838d73541a8bd0055c74fac00bdb74ee28e930f",
    "ai/omreal/data/CANONICAL_RESEARCH_STATE_V3.json": "e37fad74fae83cf087b2010039e85122866c3b093e34227f28d12759be94a6cf",
    "ai/omreal/verify_canonical_research_state_v3.py": "90d00f1a5ae55f98720130fa94eebd0fc85f1e6e8a62a8295ebbce9ece5d6c03",
    "ops/research-team/PROTOCOL.md": "54f1a15b7774085005707727780b266ffbd4a8edc4687fe14e1e6bc76d229031",
    "ops/research-team/verify_cycle_protocol.py": "4d9e16daed0de08af415e95c746803b512ea8b92c452df6df2c9e09fdcd3b7d1",
    f"ops/research-team/cycles/{HERE.name}/CYCLE.md": "2a621a7eedf79a14733260cc16ef15c196bbe6e91b64267e71027ae45566702e",
    f"ops/research-team/cycles/{HERE.name}/OPENING_AUDIT.json": "07db9da58755354dd85685d0061554993aaa1e5f37e93e35290558bb6eecfaf4",
    f"ops/research-team/cycles/{HERE.name}/WORK_ORDERS.yaml": "1bef57f3c1f094abb906a90a8e6ae0e883abbdefb7ac26bd1f0ff768628afe26",
    f"ops/research-team/cycles/{HERE.name}/CYCLE_REPORT.md": "f61ae3bdb58c5192ccf3dee40eccbc587ace860a7e526aeebc6613d6485dc5e2",
    "ops/team/diag9-s1237-normal-link-certificate/RESULT.json": "8b932ec411fe9bc96d8bb895fccdcf7a63985df6ce4d35b38e2f53eef3afc010",
    "ops/team/diag9-s1237-normal-link-falsifier/RESULT.json": "15ce5c17a174ed6a82173d24a8f72d04da5962bcea9e87cf3648adb21351d46b",
    "ops/team/diag9-s1237-normal-link-prover/DIAG9_S1237_NORMAL_LINK_NO_GO.json": "8aa726c69b556f7c2d85f7f852cb88329da39dcd173294a7db7245f13e0d2d54",
    "ops/team/diag9-s1237-normal-link-referee/CLOSING_MANIFEST.json": "9462528276530db48de7ae53808c7290327698878380193bd3f55e208196376d",
    "ops/team/diag9-s1237-normal-link-referee/RESULT.json": "16be207c4abaddf52bd6b670c293159cb317e712c431597838b00e2815bb8902",
    "ops/team/diag9-s1237-normal-link-referee/verify_closing_referee.py": "92beba4be826c331c8e5c3835912a68fa27ffebf294e403fd32c8c6504f02d7c",
}


class Reject(AssertionError):
    """Fail-closed cycle-report rejection."""


def require(condition, message):
    if not condition:
        raise Reject(message)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def git(*arguments: str) -> str:
    return subprocess.run(
        ["git", *arguments], cwd=ROOT, check=True, capture_output=True, text=True
    ).stdout.strip()


def validate_manifest(manifest, check_files=True):
    require(set(manifest) == {
        "format", "cycle_id", "canonical_base", "opening_commit",
        "reviewed_math_commit", "referee_commit", "ledger", "endpoint",
        "source_pins", "nonconsequences",
    }, "manifest fields")
    require(manifest["format"] == "diag9-s1237-normal-link-cycle-source-manifest-v1", "format")
    require(manifest["cycle_id"] == HERE.name, "cycle id")
    require(manifest["canonical_base"] == BASE, "base")
    require(manifest["opening_commit"] == OPENING, "opening")
    require(manifest["reviewed_math_commit"] == REVIEWED, "reviewed head")
    require(manifest["referee_commit"] == REFEREE, "referee")
    require(manifest["ledger"] == "2/9", "ledger")
    require(manifest["endpoint"] == ENDPOINT, "endpoint")
    require(set(manifest["source_pins"]) == {
        "README.md",
        "ai/omreal/NINE_DIAGONAL_STATUS.md",
        "ai/omreal/RESEARCH_OPERATING_SYSTEM.md",
        "ai/omreal/data/CANONICAL_RESEARCH_STATE_V2.json",
        "ai/omreal/data/CANONICAL_RESEARCH_STATE_V3.json",
        "ai/omreal/verify_canonical_research_state_v3.py",
        "ops/research-team/PROTOCOL.md",
        "ops/research-team/verify_cycle_protocol.py",
        f"ops/research-team/cycles/{HERE.name}/CYCLE.md",
        f"ops/research-team/cycles/{HERE.name}/OPENING_AUDIT.json",
        f"ops/research-team/cycles/{HERE.name}/WORK_ORDERS.yaml",
        f"ops/research-team/cycles/{HERE.name}/CYCLE_REPORT.md",
        f"ops/research-team/cycles/{HERE.name}/verify_cycle_report.py",
        "ops/team/diag9-s1237-normal-link-certificate/RESULT.json",
        "ops/team/diag9-s1237-normal-link-falsifier/RESULT.json",
        "ops/team/diag9-s1237-normal-link-prover/DIAG9_S1237_NORMAL_LINK_NO_GO.json",
        "ops/team/diag9-s1237-normal-link-referee/CLOSING_MANIFEST.json",
        "ops/team/diag9-s1237-normal-link-referee/RESULT.json",
        "ops/team/diag9-s1237-normal-link-referee/verify_closing_referee.py",
    }, "source pin census")
    require(
        all(manifest["source_pins"].get(path) == digest for path, digest in EXPECTED_SOURCE_PINS.items()),
        "source pin values",
    )
    self_relative = f"ops/research-team/cycles/{HERE.name}/verify_cycle_report.py"
    require(
        manifest["source_pins"][self_relative] == sha256(Path(__file__)),
        "cycle verifier self pin",
    )
    require(set(manifest["nonconsequences"]) == {
        "NO_STRICT_OPEN_PARENT_SEPARATOR",
        "NO_WEIGHTED_RECURSIVE_LINK_CLASSIFICATION",
        "NO_COLLAR_OR_MINCUT",
        "NO_GLOBAL_D9_CONNECTIVITY_RESULT",
        "NO_LEDGER_CHANGE",
        "NO_GITHUB_WRITE",
    }, "nonconsequences")
    if check_files:
        for relative, expected in manifest["source_pins"].items():
            require(sha256(ROOT / relative) == expected, f"source drift {relative}")
        require(git("rev-parse", f"{BASE}^{{commit}}") == BASE, "base commit missing")
        require(git("rev-parse", f"{OPENING}^{{commit}}") == OPENING, "opening commit missing")
        require(git("rev-parse", f"{REVIEWED}^{{commit}}") == REVIEWED, "reviewed commit missing")
        require(git("rev-parse", f"{REFEREE}^{{commit}}") == REFEREE, "referee commit missing")


def validate_report():
    text = REPORT.read_text(encoding="utf-8")
    collapsed = " ".join(text.split())
    phrases = (
        "Canonical base revision:",
        "Opening theorem ledger: `2/9`",
        "Closing theorem ledger: `2/9`",
        "Exact ledger delta: `0`",
        "## Opening strategy evaluation",
        "## Role assignments and handoffs",
        "## Exact result",
        "3,539",
        "6,167",
        "5,026",
        "7,078",
        "140",
        "positive Gordan weights `(1,1)`",
        "factor 8552",
        "No strict open-parent crossing is claimed",
        "## Gate table",
        "## Obligation-graph delta",
        "## Invalidated assumptions and surviving blockers",
        "## Mandatory post-cycle strategy evaluation",
        "Post-cycle verdict: `RETIRE`",
        "`PIVOT_REQUIRED`",
        "There is no selected successor target",
        "## Publication revision and durable recovery",
        "GitHub publication revision: `NONE`",
        "Local scratch remains ephemeral and is not an authority",
        "8be4fbeb8bc41073871dd3b5126d805f3b0057a407ebfceac5ca77565e735774",
    )
    missing = [
        phrase for phrase in phrases
        if " ".join(phrase.split()) not in collapsed
    ]
    require(not missing, f"report missing phrases {missing}")


def hostile_canaries(manifest):
    cases = []
    candidate = deepcopy(manifest)
    candidate["ledger"] = "3/9"
    cases.append(("ledger", candidate))
    candidate = deepcopy(manifest)
    candidate["endpoint"] = "DIAGONAL_9_PROVED"
    cases.append(("endpoint", candidate))
    candidate = deepcopy(manifest)
    candidate["referee_commit"] = REVIEWED
    cases.append(("referee", candidate))
    candidate = deepcopy(manifest)
    candidate["source_pins"]["README.md"] = "0" * 64
    cases.append(("source", candidate))
    candidate = deepcopy(manifest)
    candidate["nonconsequences"].remove("NO_WEIGHTED_RECURSIVE_LINK_CLASSIFICATION")
    cases.append(("weighted", candidate))
    candidate = deepcopy(manifest)
    candidate["nonconsequences"].remove("NO_GITHUB_WRITE")
    cases.append(("github", candidate))
    for label, mutated in cases:
        try:
            validate_manifest(mutated, check_files=False)
        except (KeyError, Reject):
            continue
        raise Reject(f"hostile canary accepted: {label}")


def replay(relative: str, expected: str):
    result = subprocess.run(
        [sys.executable, str(ROOT / relative)], cwd=ROOT,
        capture_output=True, text=True, check=False,
        env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"},
    )
    require(result.returncode == 0, f"replay failed {relative}: {result.stderr[-500:]}")
    require(expected in result.stdout, f"replay output drift {relative}")


def main():
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    validate_manifest(manifest)
    validate_report()
    hostile_canaries(manifest)
    replay("ops/research-team/verify_cycle_protocol.py", "PASS research-cycle strategy/storage/publication protocol")
    replay(f"ops/research-team/cycles/{HERE.name}/verify_opening_audit.py", "PASS D9 S12,37 opening audit")
    replay("ai/omreal/verify_canonical_research_state_v3.py", "PASS canonical 9DVL research state v3")
    print("PASS closed D9 S12,37 normal-link cycle report")
    print("PASS exact local NORMAL_LINK_REDUCTION_NO_GO; ledger 2/9")
    print("PASS GitHub read-only; Library canonical; Drive recovery mirror")


if __name__ == "__main__":
    main()
