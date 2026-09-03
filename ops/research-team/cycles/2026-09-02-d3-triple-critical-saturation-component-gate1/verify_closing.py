#!/usr/bin/env python3
"""Verify the final D3 component-saturation close from the working tree."""

from __future__ import annotations

from hashlib import sha256
import json
from pathlib import Path
import subprocess


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
MANIFEST = HERE / "CLOSING_MANIFEST.json"
BASE = "ba87af7b1ac58d22c0622c908e31dc8ec03d24fa"
START = "0095ea4b3abaa8a4cc5181b837838385e4b3d7d9"
REFEREE = "02fe7d131289ecffbd29e81876814b10db55cd30"
CANONICAL = "ai/omreal/data/CANONICAL_RESEARCH_STATE_V10.json"


def require(condition: bool, marker: str) -> None:
    if not condition:
        raise AssertionError(marker)


def digest_path(path: Path) -> str:
    return sha256(path.read_bytes()).hexdigest()


def git(*arguments: str, binary: bool = False):
    return subprocess.check_output(["git", *arguments], cwd=ROOT, text=not binary)


def run(path: str) -> str:
    completed = subprocess.run(
        ["python", "-B", path], cwd=ROOT, text=True, capture_output=True
    )
    require(completed.returncode == 0, f"replay failed: {path}\n{completed.stdout}\n{completed.stderr}")
    return completed.stdout.strip()


def main() -> None:
    closing = json.loads(MANIFEST.read_text(encoding="ascii"))
    require(closing["cycle_id"] == HERE.name, "cycle id")
    require(closing["canonical_base"]["commit"] == BASE, "base")
    require(closing["cycle_start_head"]["commit"] == START, "start")
    require(closing["role_history"]["closing_referee"]["commit"] == REFEREE, "referee")
    require(git("merge-base", "--is-ancestor", REFEREE, "HEAD").strip() == "", "referee ancestry")

    for relative, expected in closing["evidence_pins"].items():
        path = ROOT / relative
        require(path.stat().st_size == expected["bytes"], f"evidence bytes: {relative}")
        require(digest_path(path) == expected["sha256"], f"evidence digest: {relative}")

    current_canonical = (ROOT / CANONICAL).read_bytes()
    base_canonical = git("show", f"{BASE}:{CANONICAL}", binary=True)
    require(current_canonical == base_canonical, "canonical V10 changed")
    changed = [line for line in git("diff", "--name-only", START, "HEAD").splitlines() if line]
    prefixes = (
        HERE.relative_to(ROOT).as_posix() + "/",
        "ops/team/d3-triple-critical-saturation-constructor/",
        "ops/team/d3-triple-critical-saturation-falsifier/",
        "ops/team/d3-triple-critical-saturation-independent-verifier/",
        "ops/team/d3-triple-critical-saturation-closing-referee/",
    )
    require(all(path.startswith(prefixes) for path in changed), "path outside governed surfaces")

    result = closing["result"]
    require(result["classification"] == "NULL", "classification")
    require(result["q0"] == "NULL_INDEPENDENTLY_CONFIRMED", "Q0")
    require(result["q1"] == "DENIED", "Q1")
    require(result["raw_research_saturation_run"] is False, "raw saturation")
    require(result["opening_ledger"] == result["closing_ledger"] == "2/9", "ledger")
    require(result["ledger_delta"] == "0/9", "ledger delta")
    require(result["opening_triple_source_residual"] == result["closing_triple_source_residual"] == 1_162_302, "residual")
    require(result["source_residual_delta"] == 0, "residual delta")
    require(result["opening_load_bearing_obligations"] == result["closing_load_bearing_obligations"] == 7, "obligations")
    require(result["obligation_delta"] == 0, "obligation delta")
    require(result["pair_residual"] == result["pair_coverage"] == "UNKNOWN", "pair accounting")
    require(result["trajectory"] == "STALLED", "trajectory")
    require(result["automatic_strategy_reset"] == "FIRED", "reset")
    require(result["strategy_action"] == "STOP", "action")
    require(result["same_route_continue"] is False, "same route")
    require(result["selected_successor"] == "NONE", "successor")
    require(result["opening_vector"][-2:] == result["mid_cycle_vector"][-2:] == [7, 10], "opening streaks")
    require(result["closing_vector"][-2:] == [8, 11], "closing streaks")

    require(closing["q0_gate_table"]["EXACT_SOURCE_IDEAL_AND_DIGESTS"] == "PASS", "source gate")
    require(closing["q0_gate_table"]["FINITE_ORDERED_SATURATOR_LEDGER"] == "PASS_62_OF_62", "wall gate")
    require(closing["q0_gate_table"]["CONTAINMENT_IDENTITY_AND_ATTACHMENT_CLASS_PER_REMOVED_COMPONENT"].startswith("FAIL"), "attachment gate")
    require(closing["q0_gate_table"]["NUMERIC_LOCAL_RESOURCE_FORECAST"].startswith("FAIL"), "forecast gate")
    require(closing["mid_cycle"]["minimum_decrease_still_reachable_under_fixed_ceiling"] is False, "mid-cycle decrease")
    require(closing["mid_cycle"]["action"] == "FREEZE_Q0_NULL_AND_STOP", "mid-cycle action")
    require(closing["resource_accounting"]["research_ideal_saturation_runs"] == 0, "research saturation count")
    require(closing["resource_accounting"]["raw_groebner_or_rur_runs"] == 0, "raw solve count")
    require(closing["resource_accounting"]["cloud_workers"] == 0, "cloud")
    require(closing["resource_accounting"]["external_spend_usd"] == 0, "spend")
    require(closing["resource_accounting"]["github_writes"] == 0, "GitHub")
    require(closing["publication"]["github_mode"] == "READ_ONLY", "publication mode")
    require(closing["verification"]["lean"].startswith("DEFERRED"), "Lean scope")

    outputs = [
        run("ops/research-team/cycles/2026-09-02-d3-triple-critical-saturation-component-gate1/verify_opening_state.py"),
        run("ops/team/d3-triple-critical-saturation-constructor/verify_saturation_contract.py"),
        run("ops/team/d3-triple-critical-saturation-falsifier/falsify_q0.py"),
        run("ops/team/d3-triple-critical-saturation-independent-verifier/verify_q0.py"),
        run("ops/team/d3-triple-critical-saturation-closing-referee/verify_close.py"),
    ]
    require(all(output for output in outputs), "empty replay output")
    print("PASS D3 saturation final close: all evidence pins and governed paths")
    print("PASS opening, constructor, falsifier, Q0 verifier, and closing referee replays")
    print("NULL / STALLED / STOP / NONE; Q1 DENIED; LEDGER 2/9; RESIDUAL 1162302")


if __name__ == "__main__":
    main()

