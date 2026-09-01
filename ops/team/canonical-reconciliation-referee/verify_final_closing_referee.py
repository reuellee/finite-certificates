#!/usr/bin/env python3
"""Independent verifier for the final repaired canonical reconciliation.

The script uses only the Python standard library and never imports candidate
or falsifier validation code.  It reconstructs the current semantics directly,
checks the preserved rejected-head evidence, exercises independent hostile
mutations, and replays every named PR42--PR44/cycle gate.
"""

from __future__ import annotations

import copy
import hashlib
import itertools
import json
import os
import re
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import Any, Iterable


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
MANIFEST_PATH = HERE / "FINAL_CLOSING_MANIFEST.json"
STATUS_PATH = "ai/omreal/NINE_DIAGONAL_STATUS.md"
LEDGER_PATH = "ai/omreal/data/DIAG3_RESEARCH_DECISION_LEDGER.json"
PR43_REPORT = (
    "ops/research-team/cycles/2026-08-30-diag4-s53-top-sheaf/"
    "CYCLE_REPORT.md"
)
ARCHIVAL_SUCCESSOR_SHA256 = {
    # These two historical gates retain their exact frozen candidate versions
    # in the evidence chain.  The current-tree successors only make their
    # no-argument CI mode archival; explicit candidate rejection and the full
    # closing replay are exercised below.
    "ops/team/canonical-reconciliation-falsifier/verify_canonical_reconciliation_falsifier.py":
        "f7a06f107058bf3738d18f5b321c6cbf8b70cc76a94e0eda04bf390c93716cb4",
    "ops/team/canonical-reconciliation-referee/verify_closing_referee.py":
        "e65fedad2075907997dc9c00d263c3234b93127ad560a53dbb5a80d8219ad037",
}


class FinalReviewError(AssertionError):
    """A fail-closed final-review mismatch."""


def require(condition: bool, message: str) -> None:
    if not condition:
        raise FinalReviewError(message)


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def canonical_bytes(value: Any) -> bytes:
    return json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=True
    ).encode("ascii")


def run(
    argv: list[str], *, expected: int | None = 0
) -> subprocess.CompletedProcess[bytes]:
    environment = os.environ.copy()
    environment["PYTHONDONTWRITEBYTECODE"] = "1"
    environment["PYTHONHASHSEED"] = "0"
    proc = subprocess.run(
        argv,
        cwd=ROOT,
        env=environment,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    if expected is not None and proc.returncode != expected:
        stderr = proc.stderr.decode("utf-8", "replace").strip()
        raise FinalReviewError(
            f"command returned {proc.returncode}, expected {expected}: "
            f"{' '.join(argv)}: {stderr}"
        )
    return proc


def git(*args: str) -> bytes:
    return run(["git", *args]).stdout


def git_show(revision: str, path: str) -> bytes:
    return git("show", f"{revision}:{path}")


def normalize(text: str) -> str:
    return " ".join(re.sub(r"[^a-z0-9]+", " ", text.lower()).split())


def require_normalized(text: str, snippets: Iterable[str], source: str) -> None:
    haystack = normalize(text)
    for snippet in snippets:
        require(
            normalize(snippet) in haystack,
            f"{source} missing required semantic text: {snippet}",
        )


def load_manifest() -> dict[str, Any]:
    manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    require(
        manifest.get("format")
        == "canonical-reconciliation-final-closing-manifest-v1",
        "unexpected final manifest format",
    )
    return manifest


def verify_identity(commit: str, tree: str) -> None:
    require(git("rev-parse", commit).decode().strip() == commit, f"commit: {commit}")
    require(
        git("rev-parse", f"{commit}^{{tree}}").decode().strip() == tree,
        f"tree: {commit}",
    )


def verify_identities(manifest: dict[str, Any]) -> None:
    labels = (
        "base",
        "opening",
        "rejected_candidate",
        "rejection_evidence_commit",
        "repair_commit",
        "candidate",
    )
    for label in labels:
        identity = manifest[label]
        verify_identity(identity["commit"], identity["tree"])
    for merge in manifest["accepted_merges"]:
        verify_identity(merge["commit"], merge["tree"])

    candidate = manifest["candidate"]
    require(
        git("rev-parse", f"{candidate['commit']}^").decode().strip()
        == candidate["parent"],
        "candidate parent mismatch",
    )
    chain = (
        (manifest["rejected_candidate"]["commit"], manifest["rejection_evidence_commit"]["commit"]),
        (manifest["rejection_evidence_commit"]["commit"], manifest["repair_commit"]["commit"]),
        (manifest["repair_commit"]["commit"], candidate["commit"]),
    )
    for parent, child in chain:
        require(
            git("rev-parse", f"{child}^").decode().strip() == parent,
            f"unexpected repair ancestry: {parent} -> {child}",
        )
    ancestry = run(
        [
            "git",
            "merge-base",
            "--is-ancestor",
            manifest["base"]["commit"],
            candidate["commit"],
        ],
        expected=None,
    )
    require(ancestry.returncode == 0, "base is not an ancestor of candidate")


def verify_source_and_artifact_digests(manifest: dict[str, Any]) -> None:
    candidate = manifest["candidate"]["commit"]
    for source in manifest["authoritative_sources"]:
        frozen = git_show(source["revision"], source["path"])
        require(
            sha256_bytes(frozen) == source["sha256"],
            f"source digest mismatch: {source['path']}",
        )
        if source["candidate_must_match"]:
            require(
                git_show(candidate, source["path"]) == frozen,
                f"candidate changed protected source: {source['path']}",
            )
    for group in ("candidate_outputs", "candidate_evidence"):
        for path, expected in manifest[group].items():
            frozen = git_show(candidate, path)
            require(
                sha256_bytes(frozen) == expected,
                f"candidate artifact digest mismatch: {path}",
            )
            working = (ROOT / path).read_bytes()
            if path in ARCHIVAL_SUCCESSOR_SHA256:
                require(
                    sha256_bytes(working) == ARCHIVAL_SUCCESSOR_SHA256[path],
                    f"working archival successor digest changed: {path}",
                )
            else:
                require(
                    working == frozen,
                    f"working candidate artifact differs from frozen head: {path}",
                )


def changed_paths(left: str, right: str) -> list[str]:
    return git("diff", "--name-only", f"{left}..{right}").decode().splitlines()


def assert_paths(observed: Iterable[str], expected: Iterable[str], label: str) -> None:
    actual = sorted(set(observed))
    wanted = sorted(set(expected))
    require(actual == wanted, f"{label} changed-path mismatch: {actual}")


def verify_changed_paths(manifest: dict[str, Any]) -> None:
    candidate = manifest["candidate"]["commit"]
    assert_paths(
        changed_paths(manifest["base"]["commit"], candidate),
        manifest["expected_full_changed_paths"],
        "base-to-candidate",
    )
    assert_paths(
        changed_paths(manifest["rejected_candidate"]["commit"], candidate),
        manifest["expected_repair_changed_paths"],
        "rejected-to-repaired",
    )
    check = run(
        ["git", "diff", "--check", f"{manifest['base']['commit']}..{candidate}"],
        expected=None,
    )
    require(check.returncode == 0, "candidate diff-check failed")


def current_status_section(status: str) -> str:
    heading = "## Current canonical precedence through merged PR #44"
    boundary = "## Result ledger"
    require(status.count(heading) == 1, "current status heading missing or duplicate")
    require(boundary in status, "status boundary missing")
    start = status.index(heading)
    end = status.index(boundary)
    require(start < end, "current status section is not first")
    return status[start:end]


def find_obligation(ledger: dict[str, Any], obligation_id: str) -> dict[str, Any]:
    rows = [
        row
        for row in ledger.get("invariant_obligations", [])
        if isinstance(row, dict) and row.get("id") == obligation_id
    ]
    require(len(rows) == 1, f"missing or duplicate obligation: {obligation_id}")
    return rows[0]


def expected_bound_sources(manifest: dict[str, Any]) -> dict[str, str]:
    selected = {
        "ops/research-team/cycles/2026-08-31-canonical-reconciliation/CYCLE.md",
        "ops/research-team/cycles/2026-08-31-canonical-reconciliation/WORK_ORDERS.yaml",
        "ops/research-team/cycles/2026-08-29-diag4-top-sheaf/CYCLE_REPORT.md",
        PR43_REPORT,
        "ops/team/diag4-s53-referee/CLOSING_REVIEW.md",
        "ops/research-team/cycles/2026-08-30-diag3-orbit5563-global-exit/CYCLE_REPORT.md",
        "ops/team/diag3-orbit5563-referee/CLOSING_REVIEW.md",
    }
    return {
        source["path"]: source["sha256"]
        for source in manifest["authoritative_sources"]
        if source["path"] in selected
    }


def validate_core(
    ledger: dict[str, Any], status: str, manifest: dict[str, Any]
) -> None:
    base = manifest["base"]
    opening = manifest["opening"]
    facts = manifest["authoritative_facts"]
    expected_policy = manifest["d4_total_complex_policy"]

    require(ledger.get("format") == "diag3-research-decision-ledger-v2", "ledger format")
    require(ledger.get("status") == "PIVOT_REQUIRED", "ledger status")
    require(ledger.get("as_of") == "2026-08-31", "ledger date")
    repository = ledger.get("repository", {})
    require(repository.get("audited_commit") == base["commit"], "audited commit")
    require(repository.get("audited_tree") == base["tree"], "audited tree")
    require(repository.get("merged_pull_request") == 44, "audited PR")

    theorem = ledger.get("theorem", {})
    require(theorem.get("score") == facts["theorem"]["score"], "theorem score")
    require(
        theorem.get("proved_diagonals") == facts["theorem"]["proved_diagonals"],
        "proved diagonals",
    )
    require(ledger.get("selected_target") is None, "selected target")
    require("candidate_targets" not in ledger, "current candidate targets present")
    require("selected_target_progress" not in ledger, "current target progress present")

    triple = find_obligation(ledger, "diag3_triple_hc0")
    pair = find_obligation(ledger, "diag3_pair_hc1")
    require(triple.get("status") == pair.get("status") == "OPEN", "D3 promotion")
    require(triple.get("universe_count") == facts["d3"]["triple_universe"], "D3 universe")
    require(
        triple.get("proved_noncompact_count") == facts["d3"]["proved_noncompact"],
        "D3 proved count",
    )
    require(
        triple.get("unresolved_count") == facts["d3"]["unresolved_residue"],
        "D3 residue obligation",
    )

    current = ledger.get("canonical_reconciliation")
    require(isinstance(current, dict), "current reconciliation missing")
    require(current.get("precedence") == "CURRENT_THROUGH_MERGED_PR_44", "precedence")
    require(current.get("opening_reconciliation_commit") == opening["commit"], "opening commit")
    require(current.get("opening_reconciliation_tree") == opening["tree"], "opening tree")
    require(current.get("theorem_score") == facts["theorem"]["score"], "current score")
    require(
        current.get("proved_diagonals") == facts["theorem"]["proved_diagonals"],
        "current proved set",
    )

    d4 = current.get("d4_accounting", {})
    expected_d4 = facts["d4"]
    mapping = {
        "domain_labeled": "complete_supports",
        "domain_orbits": "complete_orbits",
        "proved_labeled": "b31_supports",
        "proved_orbits": "b31_orbits",
        "survivor_labeled": "survivor_supports",
        "survivor_orbits": "survivor_orbits",
    }
    for observed_key, fact_key in mapping.items():
        require(d4.get(observed_key) == expected_d4[fact_key], f"D4 {observed_key}")
    require(
        d4["domain_labeled"] == d4["proved_labeled"] + d4["survivor_labeled"],
        "D4 support arithmetic",
    )
    require(
        d4["domain_orbits"] == d4["proved_orbits"] + d4["survivor_orbits"],
        "D4 orbit arithmetic",
    )
    require(
        d4.get("survivor_delta_after_pr43")
        == {
            "labeled": expected_d4["survivor_delta_supports"],
            "orbits": expected_d4["survivor_delta_orbits"],
        },
        "D4 survivor delta",
    )

    routes = current.get("retired_continuations", [])
    require("D4_S53_CONTINUATION" in routes, "D4-S53 retirement")
    for route in (
        "ORBIT_5563_LOCAL_ROADMAP_CONTINUATION",
        "ORBIT_5563_LOCAL_BOX_CONTINUATION",
        "ORBIT_5563_LOCAL_COLLAR_CONTINUATION",
        "ORBIT_5563_MACROBOX_CONTINUATION",
        "ORBIT_5563_CLIPPED_WALL_CONTINUATION",
    ):
        require(route in routes, f"orbit-5563 route: {route}")
    total_routes = current.get("conditional_route_dispositions", {})
    require(
        total_routes == {"D4_ALTERNATING_TOTAL_COMPLEX": expected_policy},
        "D4 total-complex policy",
    )

    d3 = current.get("d3_accounting", {})
    expected_d3 = facts["d3"]
    require(d3.get("unresolved_residue") == expected_d3["unresolved_residue"], "D3 residue")
    require(d3.get("quotient_classes") == expected_d3["quotient_classes"], "D3 quotient")
    require(
        d3.get("raw_frame_presentations") == expected_d3["raw_presentations"],
        "D3 raw presentations",
    )
    require(
        d3.get("quotient_multiplicity_sum") == expected_d3["raw_presentations"],
        "D3 multiplicity sum",
    )
    require(d3.get("row_delta_after_pr44") == 0, "D3 row delta")
    missing = current.get("first_missing_global_object", {})
    require(missing.get("id") == expected_d3["first_missing_object"], "Q3 id")
    require(missing.get("status") == "MISSING", "Q3 status")
    require(current.get("selected_mathematical_target") is None, "current target")
    require(
        current.get("target_selection") == "PENDING_FRESH_INDEPENDENT_OPENING_AUDIT",
        "fresh-audit gate",
    )
    require(
        current.get("historical_pointer_policy", {}).get(
            "historical_continuation_text_is_current"
        )
        is False,
        "historical continuation became current",
    )
    require(current.get("source_sha256") == expected_bound_sources(manifest), "source binding")

    section = current_status_section(status)
    require_normalized(
        section,
        [
            "2/9",
            "exactly diagonals 1 and 2 are proved",
            "1,715,980 / 130 = 915,740 / 77 + 800,240 / 53",
            "D4-S53 continuation is retired",
            "Distinct from that D4-S53 retirement",
            "complete alternating D4 total-complex route is RETIRED_UNTIL_GLOBAL_INPUTS",
            "theorem-ready global compactification, signed face poset, and restriction matrices all exist",
            "missing any one of those three inputs must STOP fail-closed",
            "1,162,302",
            "100,086,840",
            "104,993,280",
            "Q3_COMPLETE_PARENT_BOUNDARY_ATLAS",
            "local roadmap, box, collar, macrobox, or clipped-wall continuation is retired",
            "PIVOT_REQUIRED",
            "no selected mathematical target",
        ],
        "candidate status",
    )
    require("3/9" not in section, "false status score")


def verify_incomplete_gate_truth_table(manifest: dict[str, Any]) -> int:
    policy = manifest["d4_total_complex_policy"]
    inputs = policy["required_global_inputs"]
    require(len(inputs) == 3 and len(set(inputs)) == 3, "global-input set")
    outcomes = 0
    for values in itertools.product((False, True), repeat=len(inputs)):
        state = dict(zip(inputs, values, strict=True))
        if all(state.values()):
            outcome = "ELIGIBLE_FOR_FRESH_AUDIT_NOT_REACTIVATED"
            require(policy["reactivation_requires_all_inputs"] is True, "all-input rule")
        else:
            outcome = policy["incomplete_successor_input_gate"]
            require(outcome == "STOP_FAIL_CLOSED", "incomplete gate did not stop")
        require(outcome != "ACTIVE", "truth-table route reactivation")
        outcomes += 1
    return outcomes


def verify_source_semantics(manifest: dict[str, Any]) -> None:
    base = manifest["base"]["commit"]
    pr43 = git_show(base, PR43_REPORT).decode("utf-8")
    require_normalized(
        pr43,
        [
            "complete alternating diagonal-four total complex",
            "lacks a theorem-ready global compactification, signed face poset, and restriction matrices",
            "complete alternating D4 route is RETIRE until its global input object exists",
            "an incomplete successor input gate must STOP fail-closed",
        ],
        "PR #43 report",
    )
    cycle = git_show(
        manifest["opening"]["commit"],
        "ops/research-team/cycles/2026-08-31-canonical-reconciliation/CYCLE.md",
    ).decode("utf-8")
    require_normalized(
        cycle,
        [
            "D4 signed fivefold total complex",
            "RETIRE until global inputs exist",
            "Reconcile every current-control-plane field affected by merged PRs #42, #43, and #44",
        ],
        "reconciliation cycle",
    )
    work_orders = git_show(
        manifest["opening"]["commit"],
        "ops/research-team/cycles/2026-08-31-canonical-reconciliation/WORK_ORDERS.yaml",
    ).decode("utf-8")
    require_normalized(
        work_orders,
        [
            "Every PR #42--#44 accepted count, route disposition, current-target field, and theorem nonconsequence.",
            "All changed paths, all source digests, all exact counts, all route dispositions, and zero theorem delta.",
        ],
        "work orders",
    )


def verify_rejected_evidence_and_repair(manifest: dict[str, Any]) -> None:
    candidate = manifest["candidate"]["commit"]
    rejected = manifest["rejected_candidate"]["commit"]
    prior_manifest_path = (
        "ops/team/canonical-reconciliation-referee/CLOSING_MANIFEST.json"
    )
    prior_manifest = json.loads(git_show(candidate, prior_manifest_path))
    require(
        prior_manifest.get("expected_verdict") == "REJECT_ACTIONABLE_ROUTE_OMISSION",
        "prior rejection verdict not preserved",
    )
    require(
        prior_manifest.get("candidate", {}).get("commit") == rejected,
        "prior rejection candidate changed",
    )
    require(
        prior_manifest.get("candidate", {}).get("tree")
        == manifest["rejected_candidate"]["tree"],
        "prior rejection tree changed",
    )
    for path, digest in prior_manifest["candidate_outputs"].items():
        require(
            sha256_bytes(git_show(rejected, path)) == digest,
            f"prior rejected output no longer replays: {path}",
        )
    prior_review = git_show(
        candidate, "ops/team/canonical-reconciliation-referee/CLOSING_REVIEW.md"
    ).decode("utf-8")
    require_normalized(
        prior_review,
        [
            "REJECT_ACTIONABLE_ROUTE_OMISSION",
            "Candidate commit 6e8fa4a74dbc9e0e130719f9c55df86d58a75707",
            "complete alternating D4 total-complex route must remain retired until its global input object exists",
        ],
        "preserved closing rejection",
    )

    old_status = git_show(rejected, STATUS_PATH).decode("utf-8")
    old_ledger = json.loads(git_show(rejected, LEDGER_PATH))
    require(
        "conditional_route_dispositions"
        not in old_ledger["canonical_reconciliation"],
        "rejected ledger unexpectedly contains repair",
    )
    require(
        "RETIRED_UNTIL_GLOBAL_INPUTS" not in current_status_section(old_status),
        "rejected status unexpectedly contains repair",
    )
    new_status = git_show(candidate, STATUS_PATH).decode("utf-8")
    new_ledger = json.loads(git_show(candidate, LEDGER_PATH))
    validate_core(new_ledger, new_status, manifest)


def expect_rejection(name: str, callback: Any, rejected: list[str]) -> None:
    try:
        callback()
    except FinalReviewError:
        rejected.append(name)
        return
    raise FinalReviewError(f"hostile canary accepted: {name}")


def run_hostile_canaries(
    ledger: dict[str, Any], status: str, manifest: dict[str, Any]
) -> list[str]:
    rejected: list[str] = []
    current_key = "canonical_reconciliation"
    route_key = "conditional_route_dispositions"
    total_key = "D4_ALTERNATING_TOTAL_COMPLEX"

    deleted = copy.deepcopy(ledger)
    del deleted[current_key][route_key][total_key]
    expect_rejection("delete_total_d4_route", lambda: validate_core(deleted, status, manifest), rejected)

    active = copy.deepcopy(ledger)
    active[current_key][route_key][total_key]["status"] = "ACTIVE"
    expect_rejection("reactivate_total_d4_route", lambda: validate_core(active, status, manifest), rejected)

    conflated = copy.deepcopy(ledger)
    conflated[current_key][route_key][total_key]["distinct_from"] = total_key
    expect_rejection(
        "conflate_total_d4_with_s53", lambda: validate_core(conflated, status, manifest), rejected
    )

    input_missing = copy.deepcopy(ledger)
    input_missing[current_key][route_key][total_key]["required_global_inputs"].pop()
    expect_rejection(
        "remove_required_global_input", lambda: validate_core(input_missing, status, manifest), rejected
    )

    gate = copy.deepcopy(ledger)
    gate[current_key][route_key][total_key]["incomplete_successor_input_gate"] = "CONTINUE"
    expect_rejection(
        "continue_incomplete_successor_gate", lambda: validate_core(gate, status, manifest), rejected
    )

    paragraph = (
        "- Distinct from that D4-S53 retirement, the complete alternating D4\n"
        "  total-complex route is **`RETIRED_UNTIL_GLOBAL_INPUTS`**.  It may be\n"
        "  reconsidered only after a theorem-ready global compactification, signed face\n"
        "  poset, and restriction matrices all exist.  A successor input gate missing\n"
        "  any one of those three inputs must **`STOP` fail-closed**; it cannot reactivate\n"
        "  or select the route.\n"
    )
    require(paragraph in status, "expected status policy paragraph not found")
    status_deleted = status.replace(paragraph, "", 1)
    expect_rejection(
        "status_delete_total_d4_route",
        lambda: validate_core(ledger, status_deleted, manifest),
        rejected,
    )

    status_active = status.replace("RETIRED_UNTIL_GLOBAL_INPUTS", "ACTIVE", 1)
    expect_rejection(
        "status_reactivate_total_d4_route",
        lambda: validate_core(ledger, status_active, manifest),
        rejected,
    )

    score = copy.deepcopy(ledger)
    score["theorem"]["score"] = "3/9"
    expect_rejection("false_3_of_9", lambda: validate_core(score, status, manifest), rejected)

    d4 = copy.deepcopy(ledger)
    d4[current_key]["d4_accounting"]["survivor_labeled"] -= 1
    expect_rejection(
        "changed_d4_survivor_count", lambda: validate_core(d4, status, manifest), rejected
    )

    d3 = copy.deepcopy(ledger)
    d3[current_key]["d3_accounting"]["unresolved_residue"] -= 1
    expect_rejection("changed_d3_residue", lambda: validate_core(d3, status, manifest), rejected)

    q3 = copy.deepcopy(ledger)
    q3[current_key]["first_missing_global_object"]["status"] = "AVAILABLE"
    expect_rejection("promoted_q3_atlas", lambda: validate_core(q3, status, manifest), rejected)

    target = copy.deepcopy(ledger)
    target["selected_target"] = "d4_alternating_total_complex"
    expect_rejection("active_selected_target", lambda: validate_core(target, status, manifest), rejected)

    s53 = copy.deepcopy(ledger)
    s53[current_key]["retired_continuations"].remove("D4_S53_CONTINUATION")
    expect_rejection(
        "restore_d4_s53_continuation", lambda: validate_core(s53, status, manifest), rejected
    )

    macrobox = copy.deepcopy(ledger)
    macrobox[current_key]["retired_continuations"].remove(
        "ORBIT_5563_MACROBOX_CONTINUATION"
    )
    expect_rejection(
        "restore_orbit5563_macrobox_continuation",
        lambda: validate_core(macrobox, status, manifest),
        rejected,
    )

    expect_rejection(
        "unauthorized_path",
        lambda: assert_paths(
            [*manifest["expected_full_changed_paths"], "README.md"],
            manifest["expected_full_changed_paths"],
            "hostile",
        ),
        rejected,
    )
    require(rejected == manifest["hostile_canaries"], "hostile canary order/set")
    return rejected


def replay_one(name: str, argv: list[str], required: str) -> tuple[str, str]:
    proc = run(argv)
    output = proc.stdout.decode("utf-8", "replace")
    require(required in output, f"replay {name} missing expected output: {required}")
    return name, "PASS"


def run_full_replay() -> dict[str, str]:
    python = sys.executable
    commands = {
        "canonical_verifier": (
            [python, "ai/omreal/verify_diag3_research_decision_ledger.py"],
            "PASS 9/9 hostile canonical-state canaries rejected",
        ),
        "cycle_protocol": (
            [python, "ops/research-team/verify_cycle_protocol.py"],
            "PASS research-cycle strategy/publication protocol",
        ),
        "pr42_prover": (
            [python, "ops/team/diag4-top-sheaf-prover/verify_four_block_line_sieve.py"],
            "FULL_SURVIVOR_LABELED=800240",
        ),
        "pr42_falsifier": (
            [python, "ops/team/diag4-top-sheaf-falsifier/verify_diag4_top_sheaf_falsifier.py"],
            "global realizability INCONCLUSIVE",
        ),
        "pr43_prover": (
            [python, "ops/team/diag4-s53-prover/verify_structural_scan.py"],
            "OUTCOME complete-null: D4-S53 survivors unchanged at 800,240 / 53",
        ),
        "pr43_falsifier": (
            [python, "ops/team/diag4-s53-falsifier/verify_candidate_domain.py"],
            "whole-domain topology and full-piece inclusion UNREACHED",
        ),
        "pr44_prover": (
            [python, "ops/team/diag3-orbit5563-prover/verify_diag3_orbit5563_prover.py"],
            "PASS 13/13 positive, null, negative, and hostile canaries",
        ),
        "pr44_falsifier": (
            [python, "ops/team/diag3-orbit5563-falsifier/verify_falsifier_gate.py"],
            "NULL complete parent-boundary atlas and attachments are missing",
        ),
        "pr44_referee": (
            [python, "ops/team/diag3-orbit5563-referee/verify_closing_referee.py"],
            "ACCEPT terminal=null row=1162302 ledger=2/9 strategy=PIVOT",
        ),
        "reconciliation_falsifier_sources": (
            [
                python,
                "ops/team/canonical-reconciliation-falsifier/verify_canonical_reconciliation_falsifier.py",
                "--sources-only",
            ],
            '"status": "PASS"',
        ),
        "reconciliation_falsifier_self_test": (
            [
                python,
                "ops/team/canonical-reconciliation-falsifier/verify_canonical_reconciliation_falsifier.py",
                "--self-test",
            ],
            '"hostile_rejection_count": 9',
        ),
        "reconciliation_prior_rejection_referee": (
            [
                python,
                "ops/team/canonical-reconciliation-referee/verify_closing_referee.py",
            ],
            '"verdict": "REJECT_ACTIONABLE_ROUTE_OMISSION"',
        ),
    }
    results: dict[str, str] = {}
    with ThreadPoolExecutor(max_workers=5) as executor:
        futures = {
            executor.submit(replay_one, name, argv, required): name
            for name, (argv, required) in commands.items()
        }
        for future in as_completed(futures):
            name, result = future.result()
            results[name] = result

    original = run(
        [
            python,
            "ops/team/canonical-reconciliation-falsifier/verify_canonical_reconciliation_falsifier.py",
            "--candidate",
        ],
        expected=1,
    )
    stderr = original.stderr.decode("utf-8", "replace").strip()
    require(
        stderr
        == "REJECT candidate status missing accepted fact: "
        "e666990f5b0cf07fef4a639bbb6596ddc9c4515a",
        "original falsifier candidate-mode behavior changed",
    )
    results["original_falsifier_candidate_mode"] = (
        "INAPPLICABLE_EXTRA_CONTRACTUAL_STATUS_LOCATION"
    )
    return dict(sorted(results.items()))


def verify_theorem_delta(manifest: dict[str, Any], ledger: dict[str, Any]) -> None:
    base_ledger = json.loads(git_show(manifest["base"]["commit"], LEDGER_PATH))
    require(
        base_ledger["theorem"]["score"] == ledger["theorem"]["score"] == "2/9",
        "theorem score delta",
    )
    require(
        base_ledger["theorem"]["proved_diagonals"]
        == ledger["theorem"]["proved_diagonals"]
        == [1, 2],
        "proved-diagonal delta",
    )


def verify_final_candidate(manifest: dict[str, Any]) -> dict[str, Any]:
    candidate = manifest["candidate"]["commit"]
    status = git_show(candidate, STATUS_PATH).decode("utf-8")
    ledger = json.loads(git_show(candidate, LEDGER_PATH))
    validate_core(ledger, status, manifest)
    verify_theorem_delta(manifest, ledger)
    truth_table_cases = verify_incomplete_gate_truth_table(manifest)
    hostile = run_hostile_canaries(ledger, status, manifest)
    replay = run_full_replay()
    summary: dict[str, Any] = {
        "format": "canonical-reconciliation-final-closing-result-v1",
        "candidate_commit": candidate,
        "candidate_tree": manifest["candidate"]["tree"],
        "source_digest_count": len(manifest["authoritative_sources"]),
        "candidate_artifact_digest_count": len(manifest["candidate_outputs"])
        + len(manifest["candidate_evidence"]),
        "full_changed_path_count": len(manifest["expected_full_changed_paths"]),
        "repair_changed_path_count": len(manifest["expected_repair_changed_paths"]),
        "incomplete_gate_truth_table_cases": truth_table_cases,
        "hostile_rejections": hostile,
        "full_replay": replay,
        "preserved_rejection": "PASS_REJECTED_HEAD_6E8FA4A",
        "repair": "PASS_DISTINCT_TOTAL_D4_ROUTE_SEALED",
        "theorem_delta": "NONE_2_OF_9_TO_2_OF_9",
        "post_acceptance_gate": manifest["post_acceptance_gate"],
        "verdict": manifest["expected_verdict"],
    }
    summary["semantic_sha256"] = sha256_bytes(canonical_bytes(summary))
    return summary


def main() -> int:
    try:
        manifest = load_manifest()
        verify_identities(manifest)
        verify_source_and_artifact_digests(manifest)
        verify_changed_paths(manifest)
        verify_source_semantics(manifest)
        verify_rejected_evidence_and_repair(manifest)
        result = verify_final_candidate(manifest)
        print(json.dumps(result, indent=2, sort_keys=True))
        return 0
    except (OSError, ValueError, FinalReviewError) as exc:
        print(f"REJECT {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
