#!/usr/bin/env python3
"""Independent fail-closed verifier for canonical post-PR-44 reconciliation.

This script uses only the Python standard library.  It does not import the
canonical ledger verifier, a candidate producer, or either prior worker's
acceptance logic.
"""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import subprocess
import sys
from pathlib import Path
from typing import Any, Iterable


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
MANIFEST_PATH = HERE / "SOURCE_MANIFEST.json"
STATUS_PATH = ROOT / "ai/omreal/NINE_DIAGONAL_STATUS.md"
LEDGER_PATH = ROOT / "ai/omreal/data/DIAG3_RESEARCH_DECISION_LEDGER.json"


class VerificationError(AssertionError):
    """A fail-closed verification defect."""


def require(condition: bool, message: str) -> None:
    if not condition:
        raise VerificationError(message)


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def canonical_bytes(value: Any) -> bytes:
    return json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=True
    ).encode("ascii")


def run_git(*args: str, check: bool = True) -> bytes:
    proc = subprocess.run(
        ["git", *args],
        cwd=ROOT,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    if check and proc.returncode != 0:
        raise VerificationError(
            f"git {' '.join(args)} failed: {proc.stderr.decode('utf-8', 'replace').strip()}"
        )
    return proc.stdout


def git_file(revision: str, path: str) -> bytes:
    return run_git("show", f"{revision}:{path}")


def load_manifest() -> dict[str, Any]:
    manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    sealed = copy.deepcopy(manifest)
    observed = sealed.pop("manifest_semantic_sha256")
    expected = sha256_bytes(canonical_bytes(sealed))
    require(observed == expected, "source manifest semantic digest mismatch")
    require(
        manifest["schema"]
        == "9dvl-canonical-reconciliation-falsifier-source-manifest-v1",
        "unexpected source manifest schema",
    )
    return manifest


def verify_commit(commit: str, tree: str) -> None:
    observed_commit = run_git("rev-parse", commit).decode().strip()
    observed_tree = run_git("rev-parse", f"{commit}^{{tree}}").decode().strip()
    require(observed_commit == commit, f"commit identity mismatch: {commit}")
    require(observed_tree == tree, f"tree identity mismatch at {commit}")


def verify_sources(manifest: dict[str, Any]) -> dict[str, str]:
    base = manifest["base"]
    verify_commit(base["canonical_revision"], base["canonical_tree"])
    verify_commit(base["opening_revision"], base["opening_tree"])
    for merge in manifest["accepted_merges"]:
        verify_commit(merge["commit"], merge["tree"])

    observed: dict[str, str] = {}
    for source in manifest["sources"]:
        path = source["path"]
        frozen = git_file(source["revision"], path)
        digest = sha256_bytes(frozen)
        require(digest == source["sha256"], f"frozen source digest mismatch: {path}")
        if source["working_tree_must_match"]:
            current = (ROOT / path).read_bytes()
            require(current == frozen, f"protected frozen source changed: {path}")
        observed[path] = digest
    return observed


def require_all(text: str, snippets: Iterable[str], source: str) -> None:
    for snippet in snippets:
        require(snippet in text, f"{source} missing accepted fact: {snippet}")


def reconstruct_facts(manifest: dict[str, Any]) -> dict[str, Any]:
    base = manifest["base"]["canonical_revision"]

    def frozen_text(path: str) -> str:
        return git_file(base, path).decode("utf-8")

    pr42 = frozen_text(
        "ops/research-team/cycles/2026-08-29-diag4-top-sheaf/CYCLE_REPORT.md"
    )
    pr42_review = frozen_text(
        "ops/team/diag4-strategy-referee/FINAL_DELTA_REREVIEW.md"
    )
    pr43 = frozen_text(
        "ops/research-team/cycles/2026-08-30-diag4-s53-top-sheaf/CYCLE_REPORT.md"
    )
    pr43_review = frozen_text("ops/team/diag4-s53-referee/CLOSING_REVIEW.md")
    pr44 = frozen_text(
        "ops/research-team/cycles/2026-08-30-diag3-orbit5563-global-exit/CYCLE_REPORT.md"
    )
    pr44_review = frozen_text("ops/team/diag3-orbit5563-referee/CLOSING_REVIEW.md")

    require_all(
        pr42,
        [
            "`915,740 / 77` certified and `800,240 / 53` surviving",
            "`1,715,980` supports in",
            "`130` orbits to `800,240` supports in `53` B31-resistant orbits",
            "The theorem ledger remains `2/9`",
            "mandatory `PIVOT`.",
        ],
        "PR #42 report",
    )
    require_all(
        pr42_review,
        [
            "**ACCEPT.**",
            "D4-SP, fivefold restriction exactness, diagonal four, and the theorem ledger",
            "remain open.  The honest score remains `2/9`.",
            "The honest score remains `2/9`.",
        ],
        "PR #42 review",
    )
    require_all(
        pr43,
        [
            "`1,715,980 / 130 = 915,740 / 77 + 800,240 / 53`",
            "The survivor delta is zero",
            "supports and zero orbits.",
            "no further D4-S53 cycle may start",
            "`PIVOT` away from D4-S53",
            "the score remains `2/9`",
        ],
        "PR #43 report",
    )
    require_all(
        pr43_review,
        [
            "`800,240 / 53`",
            "split `4+49`",
            "forces **`PIVOT`**, and no further D4-S53 cycle may start",
            "ledger delta is `0` (`2/9` remains)",
        ],
        "PR #43 review",
    )
    require_all(
        pr44,
        [
            "2,604 realizable unlabelled parent types × 40,320 frames",
            "100,086,840",
            "104,993,280",
            "`Q3_COMPLETE_PARENT_BOUNDARY_ATLAS`",
            "count remains `1,162,302`, the theorem ledger remains `2/9`",
            "`RETIRE`** further local roadmap, box, collar, macrobox, clipped-wall",
            "This report does not select or authorize that next target.",
        ],
        "PR #44 report",
    )
    require_all(
        pr44_review,
        [
            "Final verdict: **ACCEPT_TERMINAL_NULL_WITH_MANDATORY_PIVOT**.",
            "`77,940,147 / 79,102,449`, residue `1,162,302`, ledger `2/9`",
            "`100,086,840`",
            "`104,993,280`",
            "`Q3_COMPLETE_PARENT_BOUNDARY_ATLAS`",
            "NONE; `2/9 -> 2/9`",
            "it must not continue",
            "this residue through another local roadmap, box, collar, macrobox, or clipped-",
        ],
        "PR #44 review",
    )

    histogram = [
        (1, 2382, 96042240),
        (2, 183, 3689280),
        (3, 10, 134400),
        (4, 16, 161280),
        (6, 3, 20160),
        (8, 6, 30240),
        (12, 1, 3360),
        (16, 1, 2520),
        (24, 2, 3360),
    ]
    parent_types = sum(types for _, types, _ in histogram)
    quotient_classes = sum(classes for _, _, classes in histogram)
    raw_presentations = sum(order * classes for order, _, classes in histogram)
    require(parent_types == 2604, "D3 parent histogram mismatch")
    require(quotient_classes == 100086840, "D3 quotient histogram mismatch")
    require(raw_presentations == 104993280, "D3 raw multiplicity mismatch")
    require(parent_types * 40320 == raw_presentations, "D3 product identity mismatch")

    reconstructed = {
        "theorem": {"score": "2/9", "proved_diagonals": [1, 2], "delta": "NONE"},
        "d4": {
            "complete_supports": 1715980,
            "complete_orbits": 130,
            "b31_supports": 915740,
            "b31_orbits": 77,
            "survivor_supports": 800240,
            "survivor_orbits": 53,
            "survivor_delta_supports": 0,
            "survivor_delta_orbits": 0,
            "size_four_survivor_orbits": 4,
            "size_five_survivor_orbits": 49,
            "d4_s53_status": "OPEN",
            "d4_sp_status": "OPEN",
            "diagonal_four_status": "OPEN",
        },
        "d3": {
            "parent_types": parent_types,
            "frames_per_parent": 40320,
            "raw_presentations": raw_presentations,
            "quotient_classes": quotient_classes,
            "hard_triple_stabilizer_order": 1,
            "hard_triple_orbit_size": 40320,
            "triple_universe": 79102449,
            "proved_noncompact": 77940147,
            "triple_residue": 79102449 - 77940147,
            "first_missing_object": "Q3_COMPLETE_PARENT_BOUNDARY_ATLAS",
        },
    }
    require(
        reconstructed["d4"]["b31_supports"]
        + reconstructed["d4"]["survivor_supports"]
        == reconstructed["d4"]["complete_supports"],
        "D4 support arithmetic mismatch",
    )
    require(
        reconstructed["d4"]["b31_orbits"]
        + reconstructed["d4"]["survivor_orbits"]
        == reconstructed["d4"]["complete_orbits"],
        "D4 orbit arithmetic mismatch",
    )
    require(reconstructed == manifest["facts"], "manifest fact reconstruction mismatch")
    return reconstructed


def validate_status(text: str, contract: dict[str, Any]) -> None:
    require_all(
        text,
        [
            "2/9",
            "1,715,980 / 130 = 915,740 / 77 + 800,240 / 53",
            "100,086,840",
            "104,993,280",
            "1,162,302",
            "Q3_COMPLETE_PARENT_BOUNDARY_ATLAS",
            "PIVOT_REQUIRED",
            "e666990f5b0cf07fef4a639bbb6596ddc9c4515a",
        ],
        "candidate status",
    )
    lower = text.lower()
    require("3/9" not in text, "candidate status falsely promotes score to 3/9")
    require("no selected mathematical target" in lower, "status selects a mathematical target")
    require("no further d4-s53 cycle" in lower, "status permits D4-S53 continuation")
    require(
        all(word in lower for word in ("roadmap", "box", "collar", "macrobox", "clipped-wall", "retire")),
        "status omits the orbit-5563 local-route retirement",
    )
    require(contract["state"] in text, "status/contract state mismatch")


def find_obligation(ledger: dict[str, Any], obligation_id: str) -> dict[str, Any]:
    rows = [
        row
        for row in ledger.get("invariant_obligations", [])
        if isinstance(row, dict) and row.get("id") == obligation_id
    ]
    require(len(rows) == 1, f"missing or duplicate obligation: {obligation_id}")
    return rows[0]


def validate_ledger(ledger: dict[str, Any], contract: dict[str, Any]) -> None:
    require(ledger.get("status") == "PIVOT_REQUIRED", "ledger is not PIVOT_REQUIRED")
    require(ledger.get("as_of") == "2026-08-31", "ledger as_of is not reconciled")
    repository = ledger.get("repository", {})
    require(
        repository.get("audited_commit") == contract["canonical_revision"],
        "stale canonical repository head",
    )
    require(
        repository.get("audited_tree") == contract["canonical_tree"],
        "canonical repository tree missing or stale",
    )
    require(repository.get("merged_pull_request") == 44, "ledger does not reach PR #44")

    theorem = ledger.get("theorem", {})
    require(theorem.get("score") == "2/9", "false theorem score")
    require(theorem.get("proved_diagonals") == [1, 2], "proved-diagonal set changed")
    require(theorem.get("active_diagonal") == 3, "D3 obligation identity changed")
    require(ledger.get("selected_target") is None, "an old mathematical target remains active")
    selected = [
        row.get("id")
        for row in ledger.get("candidate_targets", [])
        if isinstance(row, dict) and row.get("selected")
    ]
    require(not selected, f"candidate target remains selected: {selected}")

    triple = find_obligation(ledger, "diag3_triple_hc0")
    require(triple.get("status") == "OPEN", "D3 triple obligation was promoted")
    require(triple.get("universe_count") == 79102449, "D3 universe count changed")
    require(triple.get("proved_noncompact_count") == 77940147, "D3 proved count changed")
    require(triple.get("unresolved_count") == 1162302, "D3 residue count changed")
    pair = find_obligation(ledger, "diag3_pair_hc1")
    require(pair.get("status") == "OPEN", "D3 pair obligation was promoted")

    require(
        ledger.get("canonical_reconciliation") == contract,
        "versioned canonical reconciliation contract missing or changed",
    )
    progress = ledger.get("selected_target_progress")
    if progress not in (None, {}):
        require(isinstance(progress, dict), "selected_target_progress has invalid type")
        require(
            progress.get("status") in {"HISTORICAL", "HISTORICAL_FROZEN", "RETIRED_HISTORY"},
            "old selected-target progress is still governing",
        )
        require("next_stage" not in progress, "old macrobox next_stage remains active")

    serialized = json.dumps(ledger, sort_keys=True)
    require("3/9" not in serialized, "ledger contains false 3/9 score")
    d4 = contract["d4"]
    require(d4["next_d4_s53_cycle"] == "PROHIBITED", "D4-S53 continuation allowed")
    require(
        contract["d3"]["first_missing_object_status"] == "MISSING_FAIL_CLOSED",
        "Q3 blocker was promoted or omitted",
    )
    require(
        contract["route_dispositions"]["orbit_5563_local_roadmap_box_collar_macrobox_clipped_wall"]
        == "RETIRED",
        "orbit-5563 local continuation not retired",
    )


def is_allowed_path(path: str, manifest: dict[str, Any]) -> bool:
    allowed = manifest["allowed_changes"]
    return path in allowed["exact_paths"] or any(
        path.startswith(prefix) for prefix in allowed["prefixes"]
    )


def validate_changed_paths(paths: Iterable[str], manifest: dict[str, Any]) -> None:
    rejected = sorted(path for path in paths if path and not is_allowed_path(path, manifest))
    require(not rejected, f"unapproved changed paths: {rejected}")


def changed_paths_from_git(manifest: dict[str, Any]) -> list[str]:
    opening = manifest["base"]["opening_revision"]
    tracked = run_git("diff", "--name-only", f"{opening}..HEAD").decode().splitlines()
    status = run_git("status", "--porcelain", "--untracked-files=all").decode().splitlines()
    untracked_or_modified = [line[3:] for line in status if len(line) >= 4]
    return sorted(set(tracked + untracked_or_modified))


def synthetic_ledger(contract: dict[str, Any]) -> dict[str, Any]:
    return {
        "format": "diag3-research-decision-ledger-v2",
        "status": "PIVOT_REQUIRED",
        "as_of": "2026-08-31",
        "repository": {
            "full_name": "reuellee/finite-certificates",
            "default_branch": "main",
            "audited_commit": contract["canonical_revision"],
            "audited_tree": contract["canonical_tree"],
            "merged_pull_request": 44,
        },
        "theorem": {
            "id": "9DVL",
            "score": "2/9",
            "proved_diagonals": [1, 2],
            "active_diagonal": 3,
        },
        "invariant_obligations": [
            {
                "id": "diag3_triple_hc0",
                "status": "OPEN",
                "universe_count": 79102449,
                "proved_noncompact_count": 77940147,
                "unresolved_count": 1162302,
            },
            {"id": "diag3_pair_hc1", "status": "OPEN"},
        ],
        "candidate_targets": [],
        "selected_target": None,
        "selected_target_progress": {"status": "HISTORICAL_FROZEN"},
        "canonical_reconciliation": copy.deepcopy(contract),
    }


def synthetic_status() -> str:
    return """# Nine-Diagonal Vanishing: proof status and exact remaining targets

## Canonical state through merged PR #44

Canonical revision `e666990f5b0cf07fef4a639bbb6596ddc9c4515a`.
State: `PIVOT_REQUIRED`; no selected mathematical target. The ledger is 2/9.
The D4 identity is `1,715,980 / 130 = 915,740 / 77 + 800,240 / 53`.
No further D4-S53 cycle is permitted.
The D3 quotient has 100,086,840 classes and raw sum 104,993,280; the residue
is 1,162,302. The first blocker is `Q3_COMPLETE_PARENT_BOUNDARY_ATLAS`.
Further orbit-5563 local roadmap, box, collar, macrobox, and clipped-wall work
is retired pending a fresh strategy audit.
"""


def expect_rejection(name: str, callback: Any, rejected: list[str]) -> None:
    try:
        callback()
    except VerificationError:
        rejected.append(name)
        return
    raise VerificationError(f"hostile canary accepted: {name}")


def run_self_test(manifest: dict[str, Any], facts: dict[str, Any]) -> dict[str, Any]:
    contract = manifest["candidate_contract"]
    good = synthetic_ledger(contract)
    validate_ledger(good, contract)
    validate_status(synthetic_status(), contract)

    rejected: list[str] = []

    stale = copy.deepcopy(good)
    stale["repository"]["audited_commit"] = "e8600495e70e6f5548cb0c73e0cfd2f33faacc0b"
    stale["repository"]["merged_pull_request"] = 37
    expect_rejection("stale_pr37_head", lambda: validate_ledger(stale, contract), rejected)

    active = copy.deepcopy(good)
    active["selected_target"] = "fullsupport_master_closure_compiler"
    expect_rejection("active_old_target", lambda: validate_ledger(active, contract), rejected)

    macrobox = copy.deepcopy(good)
    macrobox["selected_target_progress"] = {
        "status": "HISTORICAL_FROZEN",
        "next_stage": "search macroboxes 0..5",
    }
    expect_rejection("macrobox_continuation", lambda: validate_ledger(macrobox, contract), rejected)

    d4_continue = copy.deepcopy(good)
    d4_continue["canonical_reconciliation"]["d4"]["next_d4_s53_cycle"] = "CONTINUE"
    expect_rejection("d4_s53_continuation", lambda: validate_ledger(d4_continue, contract), rejected)

    score = copy.deepcopy(good)
    score["theorem"]["score"] = "3/9"
    expect_rejection("false_3_of_9", lambda: validate_ledger(score, contract), rejected)

    d3_count = copy.deepcopy(good)
    d3_count["invariant_obligations"][0]["unresolved_count"] = 1162301
    expect_rejection("changed_d3_count", lambda: validate_ledger(d3_count, contract), rejected)

    d4_count = copy.deepcopy(good)
    d4_count["canonical_reconciliation"]["d4"]["survivor_supports"] = 800239
    expect_rejection("changed_d4_count", lambda: validate_ledger(d4_count, contract), rejected)

    q3 = copy.deepcopy(good)
    q3["canonical_reconciliation"]["d3"]["first_missing_object_status"] = "PASS"
    expect_rejection("missing_q3_blocker", lambda: validate_ledger(q3, contract), rejected)

    expect_rejection(
        "unapproved_path",
        lambda: validate_changed_paths(["README.md"], manifest),
        rejected,
    )

    require(rejected == manifest["hostile_canaries"], "hostile canary order/set mismatch")
    summary: dict[str, Any] = {
        "schema": "9dvl-canonical-reconciliation-falsifier-replay-v1",
        "source_fact_sha256": sha256_bytes(canonical_bytes(facts)),
        "synthetic_positive_control": "PASS",
        "hostile_rejections": rejected,
        "hostile_rejection_count": len(rejected),
        "candidate_reviewed": False,
        "ledger_change_recommended": "NONE",
    }
    summary["semantic_sha256"] = sha256_bytes(canonical_bytes(summary))
    return summary


def validate_candidate(manifest: dict[str, Any]) -> dict[str, Any]:
    contract = manifest["candidate_contract"]
    status = STATUS_PATH.read_text(encoding="utf-8")
    ledger = json.loads(LEDGER_PATH.read_text(encoding="utf-8"))
    validate_status(status, contract)
    validate_ledger(ledger, contract)
    paths = changed_paths_from_git(manifest)
    validate_changed_paths(paths, manifest)
    summary: dict[str, Any] = {
        "schema": "9dvl-canonical-reconciliation-falsifier-candidate-v1",
        "candidate_head": run_git("rev-parse", "HEAD").decode().strip(),
        "candidate_tree": run_git("rev-parse", "HEAD^{tree}").decode().strip(),
        "changed_paths": paths,
        "status": "PASS",
        "ledger_change_recommended": "NONE",
    }
    summary["semantic_sha256"] = sha256_bytes(canonical_bytes(summary))
    return summary


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Replay frozen reconciliation sources and hostile canaries by default; "
            "use --candidate only while evaluating a live candidate surface."
        )
    )
    modes = parser.add_mutually_exclusive_group()
    modes.add_argument("--sources-only", action="store_true")
    modes.add_argument("--self-test", action="store_true")
    modes.add_argument("--candidate", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        manifest = load_manifest()
        source_digests = verify_sources(manifest)
        facts = reconstruct_facts(manifest)
        if args.sources_only:
            result: dict[str, Any] = {
                "schema": "9dvl-canonical-reconciliation-falsifier-sources-v1",
                "source_count": len(source_digests),
                "fact_sha256": sha256_bytes(canonical_bytes(facts)),
                "status": "PASS",
            }
            result["semantic_sha256"] = sha256_bytes(canonical_bytes(result))
        elif args.self_test or not args.candidate:
            # Repository-wide CI discovers every verify_*.py with no flags.
            # Once a rejected candidate has been superseded, that default must
            # authenticate the frozen rejection gate rather than apply its
            # intentionally presentation-specific live-candidate contract to
            # the current accepted surface.  Explicit --candidate semantics
            # remain unchanged for the closing-referee replay below.
            result = run_self_test(manifest, facts)
        else:
            result = validate_candidate(manifest)
        print(json.dumps(result, sort_keys=True, indent=2))
        return 0
    except (OSError, ValueError, VerificationError) as exc:
        print(f"REJECT {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
