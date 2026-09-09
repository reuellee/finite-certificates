#!/usr/bin/env python3
"""Verify the final independently reviewed D3 mixed-(1,0,0) close."""

from __future__ import annotations

from hashlib import sha256
import json
from pathlib import Path
import subprocess
import tempfile


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
MANIFEST = HERE / "CLOSING_MANIFEST.json"
REFEREE = "3f7c58a46aa4e8ebf6394b7ce7a8e4593f034f3a"
FINAL_CLOSE = "a10a47d1e934e4296b9612ccbde6d0b1a74a88bb"
FINAL_CLOSE_TREE = "eead48c4263f85cb71b0617213011fe5dcae89bf"
ALLOWED_PREFIXES = (
    HERE.relative_to(ROOT).as_posix() + "/",
    "ops/team/d3-mixed-100-carrier-constructor/",
    "ops/team/d3-mixed-100-carrier-falsifier/",
    "ops/team/d3-mixed-100-independent-verifier/",
    "ops/team/d3-mixed-100-closing-referee/",
)
PREDECESSOR_REPORT = "ops/research-team/cycles/2026-09-02-d3-triple-critical-saturation-component-gate1/CYCLE_REPORT.md"


def require(ok: bool, message: str) -> None:
    if not ok:
        raise AssertionError(message)


def digest(path: Path) -> str:
    return sha256(path.read_bytes()).hexdigest()


def git(*args: str) -> str:
    return subprocess.check_output(["git", *args], cwd=ROOT, text=True).strip()


def run(relative: str) -> str:
    completed = subprocess.run(["python", "-B", relative], cwd=ROOT, text=True, capture_output=True)
    require(completed.returncode == 0, f"replay failed {relative}\n{completed.stdout}\n{completed.stderr}")
    return completed.stdout.strip()


def replay_frozen_close() -> None:
    """Replay the immutable close when invoked from a legitimate successor."""
    require(git("rev-parse", f"{FINAL_CLOSE}^{{tree}}") == FINAL_CLOSE_TREE, "final close tree")
    require(git("merge-base", "--is-ancestor", FINAL_CLOSE, "HEAD") == "", "final close ancestry")
    with tempfile.TemporaryDirectory(prefix="d3-mixed-100-close-") as temporary:
        checkout = Path(temporary) / "checkout"
        added = False
        try:
            subprocess.run(
                ["git", "worktree", "add", "--detach", str(checkout), FINAL_CLOSE],
                cwd=ROOT,
                check=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
            )
            added = True
            completed = subprocess.run(
                ["python", "-B", str(HERE.relative_to(ROOT) / Path(__file__).name)],
                cwd=checkout,
                text=True,
                capture_output=True,
            )
            require(
                completed.returncode == 0,
                f"frozen close replay failed\n{completed.stdout}\n{completed.stderr}",
            )
            require("PASS final D3 mixed-(1,0,0) close" in completed.stdout, "frozen close output")
        finally:
            if added:
                subprocess.run(
                    ["git", "worktree", "remove", "--force", str(checkout)],
                    cwd=ROOT,
                    check=True,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                )
    print("PASS frozen final D3 mixed-(1,0,0) close from successor state")
    print("NULL / STALLED / STOP / NONE; O3/O4 2/2 OPEN; LEDGER 2/9")


def main() -> None:
    if git("rev-parse", "HEAD") != FINAL_CLOSE or git("status", "--porcelain"):
        replay_frozen_close()
        return
    data = json.loads(MANIFEST.read_text(encoding="ascii"))
    require(data["format"] == "d3-mixed-100-final-closing-manifest-v1", "format")
    require(data["cycle_id"] == HERE.name, "cycle")
    for key in ("base", "opening", "frozen_candidate"):
        item = data[key]
        require(git("rev-parse", f'{item["revision"]}^{{tree}}') == item["tree"], key)
    referee = data["closing_referee"]
    require(referee["integrated_revision"] == REFEREE, "referee integration")
    require(git("rev-parse", f"{REFEREE}^{{tree}}") == referee["integrated_tree"], "referee tree")
    require(git("merge-base", "--is-ancestor", REFEREE, "HEAD") == "", "referee ancestry")
    require(referee["verdict"] == "ACCEPT_EXACT_FROZEN_NULL_STALLED_STOP_NONE", "referee verdict")

    for relative, expected in data["evidence_pins"].items():
        path = ROOT / relative
        require(path.stat().st_size == expected["bytes"], f"bytes {relative}")
        require(digest(path) == expected["sha256"], f"digest {relative}")

    changed = git("diff", "--name-only", data["base"]["revision"], "HEAD").splitlines()
    require(all(path == PREDECESSOR_REPORT or path.startswith(ALLOWED_PREFIXES) for path in changed), "governed paths")

    result = data["result"]
    require(result["classification"] == "NULL", "classification")
    require(result["trajectory"] == "STALLED" and result["strategy_action"] == "STOP", "strategy")
    require(result["selected_successor"] == "NONE" and result["same_route_continue"] is False, "successor")
    require(result["positive_token"] is None and result["negative_token"] is None, "tokens")
    require(result["O3"] == result["O4"] == "OPEN", "O3/O4")
    require(result["opening_ledger"] == result["closing_ledger"] == "2/9" and result["ledger_delta"] == "0/9", "ledger")
    require(result["opening_load_bearing_obligations"] == result["closing_load_bearing_obligations"] == 7, "obligations")
    require(result["pair_residual"] == result["pair_coverage"] == "UNKNOWN", "pair")
    require(result["triple_residual"] == 1162302, "triple")
    require(result["opening_vector"] == result["midpoint_vector"], "midpoint")
    require(result["closing_vector"][-2:] == [9, 12], "closing streaks")
    require(result["selected_route_opening"] == result["selected_route_closing"], "route residual")
    require(result["minimum_decrease_met"] is False, "minimum decrease")

    boundary = data["exact_boundary"]
    require(boundary["formal_kernel_cone_exact"] is True, "formal cone")
    require(boundary["formal_kernel_cone_geometric_mixed_proper"] is False, "geometric scope")
    require(boundary["declared_interface_entails_geometric_carrier"] is False, "non-entailment")
    require(boundary["empty_carrier_is_actual_admissible_9dvl_instance"] is False, "empty model")
    require(boundary["full_negative_proved"] is False and boundary["bounded_repair"] is False, "negative/repair")

    verification = data["verification"]
    require(verification["closing_referee_hostiles"] == 57, "referee hostiles")
    require(verification["clean_no_hardlink_replay"] is True and verification["human_review"] is False, "review scope")
    resources = data["resources"]
    require(resources["opening_to_referee_integration_seconds"] == 2654, "elapsed")
    require(resources["opening_to_referee_integration_seconds"] < resources["governed_ceiling_seconds"] == 14400, "ceiling")
    require(resources["constructor_handoffs"] == 1 and resources["verifier_directed_repairs"] == 0, "handoffs")
    require(resources["research_saturation_cad_srep_jobs"] == resources["cloud_workers"] == resources["external_spend_usd"] == 0, "compute scope")
    require(all(value is False for value in data["scope"].values()), "scope")
    require(data["publication"]["github_mode"] == "READ_ONLY" and data["publication"]["connector_use"] is False, "publication")
    require(len(data["nonconsequences"]) == 8, "nonconsequences")

    replays = [
        "ops/research-team/cycles/2026-09-03-d3-mixed-block-100-universal-carrier-gate1/verify_opening_state.py",
        "ops/team/d3-mixed-100-carrier-constructor/verify_constructor.py",
        "ops/team/d3-mixed-100-carrier-falsifier/verify_falsifier.py",
        "ops/research-team/cycles/2026-09-03-d3-mixed-block-100-universal-carrier-gate1/verify_mid_cycle.py",
        "ops/team/d3-mixed-100-independent-verifier/verify_independent.py",
        "ops/research-team/cycles/2026-09-03-d3-mixed-block-100-universal-carrier-gate1/verify_closing_candidate.py",
        "ops/team/d3-mixed-100-closing-referee/verify_close.py",
        "ops/research-team/verify_cycle_protocol.py",
    ]
    outputs = [run(path) for path in replays]
    require(all(outputs), "replay outputs")
    print("PASS final D3 mixed-(1,0,0) close and governed paths")
    print("PASS opening, constructor, falsifier, midpoint, verifier, candidate, referee, and protocol")
    print("NULL / STALLED / STOP / NONE; O3/O4 2/2 OPEN; LEDGER 2/9")


if __name__ == "__main__":
    main()
