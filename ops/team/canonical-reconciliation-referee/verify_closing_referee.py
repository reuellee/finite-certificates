#!/usr/bin/env python3
"""Independent exact-head verifier for the canonical reconciliation rejection.

This verifier is intentionally standard-library only.  It reads the frozen
candidate with ``git show`` and does not import either worker's acceptance
logic.  Exit zero means that the exact candidate was successfully shown to
have the one actionable route-disposition omission recorded by the referee;
it does not mean that the candidate is accepted.
"""

from __future__ import annotations

import copy
import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path
from typing import Any, Iterable


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
MANIFEST_PATH = HERE / "CLOSING_MANIFEST.json"
STATUS_PATH = "ai/omreal/NINE_DIAGONAL_STATUS.md"
LEDGER_PATH = "ai/omreal/data/DIAG3_RESEARCH_DECISION_LEDGER.json"
CANONICAL_VERIFIER = "ai/omreal/verify_diag3_research_decision_ledger.py"
PROTOCOL_VERIFIER = "ops/research-team/verify_cycle_protocol.py"
FALSIFIER_VERIFIER = (
    "ops/team/canonical-reconciliation-falsifier/"
    "verify_canonical_reconciliation_falsifier.py"
)
PR43_REPORT = (
    "ops/research-team/cycles/2026-08-30-diag4-s53-top-sheaf/"
    "CYCLE_REPORT.md"
)


class ReviewError(AssertionError):
    """A fail-closed closing-review failure."""


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ReviewError(message)


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def canonical_bytes(value: Any) -> bytes:
    return json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=True
    ).encode("ascii")


def run(
    argv: list[str], *, expected: int | None = 0
) -> subprocess.CompletedProcess[bytes]:
    proc = subprocess.run(
        argv,
        cwd=ROOT,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    if expected is not None and proc.returncode != expected:
        stderr = proc.stderr.decode("utf-8", "replace").strip()
        raise ReviewError(
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
        needle = normalize(snippet)
        require(needle in haystack, f"{source} missing accepted fact: {snippet}")


def verify_identity(commit: str, tree: str) -> None:
    observed_commit = git("rev-parse", commit).decode().strip()
    observed_tree = git("rev-parse", f"{commit}^{{tree}}").decode().strip()
    require(observed_commit == commit, f"commit identity mismatch: {commit}")
    require(observed_tree == tree, f"tree identity mismatch: {commit}")


def load_manifest() -> dict[str, Any]:
    manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    require(
        manifest.get("format")
        == "canonical-reconciliation-closing-referee-manifest-v1",
        "unexpected closing manifest format",
    )
    return manifest


def verify_identities(manifest: dict[str, Any]) -> None:
    for label in ("base", "opening", "candidate"):
        identity = manifest[label]
        verify_identity(identity["commit"], identity["tree"])
    candidate = manifest["candidate"]
    parent = git("rev-parse", f"{candidate['commit']}^").decode().strip()
    require(parent == candidate["parent"], "candidate parent mismatch")
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
    require(ancestry.returncode == 0, "canonical base is not a candidate ancestor")
    for merge in manifest["accepted_merges"]:
        verify_identity(merge["commit"], merge["tree"])


def verify_source_digests(manifest: dict[str, Any]) -> None:
    candidate = manifest["candidate"]["commit"]
    for source in manifest["authoritative_sources"]:
        frozen = git_show(source["revision"], source["path"])
        require(
            sha256_bytes(frozen) == source["sha256"],
            f"frozen source digest mismatch: {source['path']}",
        )
        if source["candidate_must_match"]:
            require(
                git_show(candidate, source["path"]) == frozen,
                f"candidate changed protected source: {source['path']}",
            )
    for group in ("candidate_outputs", "candidate_evidence"):
        for path, expected in manifest[group].items():
            require(
                sha256_bytes(git_show(candidate, path)) == expected,
                f"candidate artifact digest mismatch: {path}",
            )


def assert_changed_paths(paths: Iterable[str], expected: Iterable[str]) -> None:
    observed = sorted(set(paths))
    wanted = sorted(set(expected))
    require(observed == wanted, f"candidate changed-path mismatch: {observed}")


def verify_changed_paths(manifest: dict[str, Any]) -> None:
    paths = git(
        "diff",
        "--name-only",
        f"{manifest['base']['commit']}..{manifest['candidate']['commit']}",
    ).decode().splitlines()
    assert_changed_paths(paths, manifest["expected_changed_paths"])


def current_status_section(status: str) -> str:
    heading = "## Current canonical precedence through merged PR #44"
    end = "## Result ledger"
    require(status.count(heading) == 1, "current status heading missing or duplicate")
    require(end in status, "status result-ledger boundary missing")
    start_index = status.index(heading)
    end_index = status.index(end)
    require(start_index < end_index, "current status section is not first")
    return status[start_index:end_index]


def find_obligation(ledger: dict[str, Any], obligation_id: str) -> dict[str, Any]:
    rows = [
        row
        for row in ledger.get("invariant_obligations", [])
        if isinstance(row, dict) and row.get("id") == obligation_id
    ]
    require(len(rows) == 1, f"missing or duplicate obligation: {obligation_id}")
    return rows[0]


def validate_core(
    ledger: dict[str, Any], status: str, manifest: dict[str, Any]
) -> None:
    facts = manifest["authoritative_facts"]
    candidate = manifest["candidate"]
    base = manifest["base"]
    opening = manifest["opening"]

    require(ledger.get("format") == "diag3-research-decision-ledger-v2", "not v2")
    require(ledger.get("status") == "PIVOT_REQUIRED", "ledger not PIVOT_REQUIRED")
    require(ledger.get("as_of") == "2026-08-31", "ledger date is stale")
    repository = ledger.get("repository", {})
    require(repository.get("audited_commit") == base["commit"], "stale base commit")
    require(repository.get("audited_tree") == base["tree"], "stale base tree")
    require(repository.get("merged_pull_request") == 44, "ledger does not reach PR #44")

    theorem = ledger.get("theorem", {})
    require(theorem.get("score") == facts["theorem"]["score"], "theorem score changed")
    require(
        theorem.get("proved_diagonals") == facts["theorem"]["proved_diagonals"],
        "proved diagonals changed",
    )
    require(ledger.get("selected_target") is None, "old selected target is active")
    require("candidate_targets" not in ledger, "current candidate targets remain")
    require("selected_target_progress" not in ledger, "current target progress remains")

    triple = find_obligation(ledger, "diag3_triple_hc0")
    pair = find_obligation(ledger, "diag3_pair_hc1")
    require(triple.get("status") == "OPEN", "D3 triple obligation promoted")
    require(pair.get("status") == "OPEN", "D3 pair obligation promoted")
    require(triple.get("universe_count") == facts["d3"]["triple_universe"], "D3 universe")
    require(
        triple.get("proved_noncompact_count") == facts["d3"]["proved_noncompact"],
        "D3 proved count",
    )
    require(
        triple.get("unresolved_count") == facts["d3"]["unresolved_residue"],
        "D3 residue",
    )

    current = ledger.get("canonical_reconciliation")
    require(isinstance(current, dict), "current reconciliation object missing")
    require(current.get("precedence") == "CURRENT_THROUGH_MERGED_PR_44", "precedence")
    require(
        current.get("opening_reconciliation_commit") == opening["commit"],
        "opening commit mismatch",
    )
    require(
        current.get("opening_reconciliation_tree") == opening["tree"],
        "opening tree mismatch",
    )
    require(current.get("theorem_score") == facts["theorem"]["score"], "current score")
    require(
        current.get("proved_diagonals") == facts["theorem"]["proved_diagonals"],
        "current proved diagonals",
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
        "D4 PR43 survivor delta",
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
    require(d3.get("row_delta_after_pr44") == 0, "D3 row delta changed")
    missing = current.get("first_missing_global_object", {})
    require(missing.get("id") == expected_d3["first_missing_object"], "Q3 blocker id")
    require(missing.get("status") == "MISSING", "Q3 blocker promoted")

    routes = current.get("retired_continuations", [])
    require("D4_S53_CONTINUATION" in routes, "D4-S53 continuation restored")
    for route in (
        "ORBIT_5563_LOCAL_ROADMAP_CONTINUATION",
        "ORBIT_5563_LOCAL_BOX_CONTINUATION",
        "ORBIT_5563_LOCAL_COLLAR_CONTINUATION",
        "ORBIT_5563_MACROBOX_CONTINUATION",
        "ORBIT_5563_CLIPPED_WALL_CONTINUATION",
    ):
        require(route in routes, f"retired route missing: {route}")
    require(current.get("selected_mathematical_target") is None, "current target selected")
    require(
        current.get("target_selection") == "PENDING_FRESH_INDEPENDENT_OPENING_AUDIT",
        "fresh opening audit gate missing",
    )
    policy = current.get("historical_pointer_policy", {})
    require(
        policy.get("historical_continuation_text_is_current") is False,
        "historical continuation text became current",
    )

    expected_source_hashes = {
        source["path"]: source["sha256"]
        for source in manifest["authoritative_sources"]
        if source["path"]
        in {
            "ops/research-team/cycles/2026-08-31-canonical-reconciliation/CYCLE.md",
            "ops/research-team/cycles/2026-08-31-canonical-reconciliation/WORK_ORDERS.yaml",
            "ops/research-team/cycles/2026-08-29-diag4-top-sheaf/CYCLE_REPORT.md",
            PR43_REPORT,
            "ops/team/diag4-s53-referee/CLOSING_REVIEW.md",
            "ops/research-team/cycles/2026-08-30-diag3-orbit5563-global-exit/CYCLE_REPORT.md",
            "ops/team/diag3-orbit5563-referee/CLOSING_REVIEW.md",
        }
    }
    require(current.get("source_sha256") == expected_source_hashes, "source binding changed")

    section = current_status_section(status)
    require_normalized(
        section,
        [
            "2/9",
            "exactly diagonals 1 and 2 are proved",
            "1,715,980 / 130 = 915,740 / 77 + 800,240 / 53",
            "1,162,302",
            "100,086,840",
            "104,993,280",
            "Q3_COMPLETE_PARENT_BOUNDARY_ATLAS",
            "PIVOT_REQUIRED",
            "no selected mathematical target",
            "local roadmap, box, collar, macrobox, or clipped-wall continuation is retired",
        ],
        "candidate current status",
    )
    require("3/9" not in section, "status falsely promotes theorem score")
    require(candidate["commit"] not in section, "candidate improperly self-identifies")


def flatten_semantic_strings(value: Any, path: tuple[str, ...] = ()) -> Iterable[str]:
    if isinstance(value, dict):
        for key, item in value.items():
            yield from flatten_semantic_strings(item, (*path, str(key)))
    elif isinstance(value, list):
        for item in value:
            yield from flatten_semantic_strings(item, path)
    else:
        yield normalize(" ".join((*path, str(value))))


def has_d4_total_complex_retirement(status: str, current: dict[str, Any]) -> bool:
    section = normalize(current_status_section(status))
    status_match = all(token in section for token in ("d4", "total complex", "retir")) and (
        "global input" in section or "global compactification" in section
    )
    object_match = any(
        all(token in text for token in ("d4", "total", "complex", "retir"))
        and ("global" in text or "continuation" in text)
        for text in flatten_semantic_strings(current)
    )
    return status_match or object_match


def verify_source_semantics(manifest: dict[str, Any]) -> None:
    base = manifest["base"]["commit"]
    pr43 = git_show(base, PR43_REPORT).decode("utf-8")
    require_normalized(
        pr43,
        [
            "The complete alternating diagonal-four total complex has high theoretical leverage but lacks a theorem-ready global compactification, signed face poset, and restriction matrices.",
            "the complete alternating D4 route is RETIRE until its global input object exists",
            "an incomplete successor input gate must STOP fail-closed",
        ],
        "PR #43 cycle report",
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
    orders = git_show(
        manifest["opening"]["commit"],
        "ops/research-team/cycles/2026-08-31-canonical-reconciliation/WORK_ORDERS.yaml",
    ).decode("utf-8")
    require_normalized(
        orders,
        [
            "Every PR #42--#44 accepted count, route disposition, current-target field, and theorem nonconsequence.",
            "All changed paths, all source digests, all exact counts, all route dispositions, and zero theorem delta.",
        ],
        "reconciliation work orders",
    )


def expect_rejection(name: str, callback: Any, rejected: list[str]) -> None:
    try:
        callback()
    except ReviewError:
        rejected.append(name)
        return
    raise ReviewError(f"hostile canary accepted: {name}")


def run_hostile_canaries(
    ledger: dict[str, Any], status: str, manifest: dict[str, Any]
) -> list[str]:
    rejected: list[str] = []

    stale = copy.deepcopy(ledger)
    stale["repository"]["audited_commit"] = "e8600495e70e6f5548cb0c73e0cfd2f33faacc0b"
    expect_rejection("stale_base_identity", lambda: validate_core(stale, status, manifest), rejected)

    score = copy.deepcopy(ledger)
    score["theorem"]["score"] = "3/9"
    expect_rejection("false_3_of_9", lambda: validate_core(score, status, manifest), rejected)

    target = copy.deepcopy(ledger)
    target["selected_target"] = "fullsupport_master_closure_compiler"
    expect_rejection("active_old_target", lambda: validate_core(target, status, manifest), rejected)

    d4 = copy.deepcopy(ledger)
    d4["canonical_reconciliation"]["d4_accounting"]["survivor_labeled"] -= 1
    expect_rejection(
        "changed_d4_survivor_count", lambda: validate_core(d4, status, manifest), rejected
    )

    d3 = copy.deepcopy(ledger)
    d3["canonical_reconciliation"]["d3_accounting"]["unresolved_residue"] -= 1
    expect_rejection("changed_d3_residue", lambda: validate_core(d3, status, manifest), rejected)

    q3 = copy.deepcopy(ledger)
    q3["canonical_reconciliation"]["first_missing_global_object"]["status"] = "AVAILABLE"
    expect_rejection("promoted_q3_atlas", lambda: validate_core(q3, status, manifest), rejected)

    d4_route = copy.deepcopy(ledger)
    d4_route["canonical_reconciliation"]["retired_continuations"].remove(
        "D4_S53_CONTINUATION"
    )
    expect_rejection(
        "restored_d4_s53_continuation",
        lambda: validate_core(d4_route, status, manifest),
        rejected,
    )

    local_route = copy.deepcopy(ledger)
    local_route["canonical_reconciliation"]["retired_continuations"].remove(
        "ORBIT_5563_MACROBOX_CONTINUATION"
    )
    expect_rejection(
        "restored_orbit5563_macrobox_continuation",
        lambda: validate_core(local_route, status, manifest),
        rejected,
    )

    source = copy.deepcopy(ledger)
    source["canonical_reconciliation"]["source_sha256"][PR43_REPORT] = "0" * 64
    expect_rejection("changed_source_digest", lambda: validate_core(source, status, manifest), rejected)

    expect_rejection(
        "unauthorized_path",
        lambda: assert_changed_paths(
            [*manifest["expected_changed_paths"], "README.md"],
            manifest["expected_changed_paths"],
        ),
        rejected,
    )
    require(rejected == manifest["hostile_canaries"], "hostile canary set/order mismatch")
    return rejected


def verify_worker_replays() -> dict[str, str]:
    commands = {
        "canonical_verifier": [sys.executable, CANONICAL_VERIFIER],
        "cycle_protocol": [sys.executable, PROTOCOL_VERIFIER],
        "falsifier_sources": [sys.executable, FALSIFIER_VERIFIER, "--sources-only"],
        "falsifier_self_test": [sys.executable, FALSIFIER_VERIFIER, "--self-test"],
    }
    results: dict[str, str] = {}
    for name, argv in commands.items():
        proc = run(argv)
        output = proc.stdout.decode("utf-8", "replace")
        require(output.strip(), f"empty replay output: {name}")
        results[name] = "PASS"
    candidate = run([sys.executable, FALSIFIER_VERIFIER, "--candidate"], expected=1)
    error = candidate.stderr.decode("utf-8", "replace").strip()
    require(
        error
        == "REJECT candidate status missing accepted fact: "
        "e666990f5b0cf07fef4a639bbb6596ddc9c4515a",
        "unexpected falsifier candidate-mode rejection",
    )
    results["falsifier_candidate_mode"] = "REJECT_NONAUTHORITATIVE_STATUS_LOCATION"
    return results


def verify_falsifier_arbitration(manifest: dict[str, Any]) -> None:
    candidate = manifest["candidate"]["commit"]
    findings = git_show(
        candidate, "ops/team/canonical-reconciliation-falsifier/FINDINGS.md"
    ).decode("utf-8")
    verifier = git_show(candidate, FALSIFIER_VERIFIER).decode("utf-8")
    require_normalized(
        findings,
        [
            "These are intentionally strict schema assumptions, independently chosen without seeing the prover candidate",
            "A semantically equivalent candidate using a different schema will reject and requires explicit coordinator/referee adjudication",
        ],
        "falsifier findings",
    )
    require(
        '"e666990f5b0cf07fef4a639bbb6596ddc9c4515a"' in verifier,
        "falsifier literal-status requirement not found",
    )
    require(
        'ledger.get("canonical_reconciliation") == contract' in verifier,
        "falsifier exact-object requirement not found",
    )


def verify_expected_rejection(manifest: dict[str, Any]) -> dict[str, Any]:
    candidate = manifest["candidate"]["commit"]
    status_bytes = git_show(candidate, STATUS_PATH)
    ledger_bytes = git_show(candidate, LEDGER_PATH)
    status = status_bytes.decode("utf-8")
    ledger = json.loads(ledger_bytes)

    for path, expected in manifest["candidate_outputs"].items():
        working = (ROOT / path).read_bytes()
        require(sha256_bytes(working) == expected, f"working candidate surface changed: {path}")

    validate_core(ledger, status, manifest)
    base_ledger = json.loads(git_show(manifest["base"]["commit"], LEDGER_PATH))
    require(
        base_ledger["theorem"]["score"] == ledger["theorem"]["score"] == "2/9",
        "theorem delta is not zero",
    )
    require(
        base_ledger["theorem"]["proved_diagonals"]
        == ledger["theorem"]["proved_diagonals"]
        == [1, 2],
        "proved-diagonal delta is not zero",
    )

    current = ledger["canonical_reconciliation"]
    require(
        not has_d4_total_complex_retirement(status, current),
        "expected route omission is not present",
    )
    repaired_discriminator = copy.deepcopy(current)
    repaired_discriminator["retired_continuations"].append(
        "D4_ALTERNATING_TOTAL_COMPLEX_CONTINUATION"
    )
    require(
        has_d4_total_complex_retirement(status, repaired_discriminator),
        "next discriminator does not detect the missing route",
    )

    rejected = run_hostile_canaries(ledger, status, manifest)
    replay = verify_worker_replays()
    summary: dict[str, Any] = {
        "format": "canonical-reconciliation-closing-referee-result-v1",
        "candidate_commit": candidate,
        "candidate_tree": manifest["candidate"]["tree"],
        "source_digest_count": len(manifest["authoritative_sources"]),
        "changed_path_count": len(manifest["expected_changed_paths"]),
        "hostile_rejections": rejected,
        "worker_replays": replay,
        "falsifier_schema_arbitration": "NONAUTHORITATIVE_PRESENTATION_ASSUMPTIONS",
        "actionable_defect": "D4_ALTERNATING_TOTAL_COMPLEX_RETIREMENT_OMITTED",
        "theorem_delta": "NONE_2_OF_9_TO_2_OF_9",
        "verdict": manifest["expected_verdict"],
    }
    summary["semantic_sha256"] = sha256_bytes(canonical_bytes(summary))
    return summary


def main() -> int:
    try:
        manifest = load_manifest()
        verify_identities(manifest)
        verify_source_digests(manifest)
        verify_changed_paths(manifest)
        verify_source_semantics(manifest)
        verify_falsifier_arbitration(manifest)
        result = verify_expected_rejection(manifest)
        print(json.dumps(result, indent=2, sort_keys=True))
        return 0
    except (OSError, ValueError, ReviewError) as exc:
        print(f"FAIL_CLOSED {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
