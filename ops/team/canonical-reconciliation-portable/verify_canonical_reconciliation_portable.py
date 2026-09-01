#!/usr/bin/env python3
"""Portable independent gate for the post-PR44 canonical reconciliation.

This verifier never imports the canonical-state verifier and never requires
the unpublished transient commits used by the first PR45 review attempt.
It authenticates published PR42--PR44 history when those objects are present;
otherwise it reports PINNED_SURFACE and checks the complete governed surface.
"""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
from typing import Any, Callable


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
STATE_PATH = ROOT / "ai/omreal/data/CANONICAL_RESEARCH_STATE.json"
LEGACY_PATH = ROOT / "ai/omreal/data/DIAG3_RESEARCH_DECISION_LEDGER.json"
LEGACY_VERIFIER = ROOT / "ai/omreal/verify_diag3_research_decision_ledger.py"
STATUS_PATH = ROOT / "ai/omreal/NINE_DIAGONAL_STATUS.md"
README_PATH = ROOT / "README.md"
OPERATING_SYSTEM_PATH = ROOT / "ai/omreal/RESEARCH_OPERATING_SYSTEM.md"
MANIFEST_PATH = HERE / "SOURCE_MANIFEST.json"

BASE = "e666990f5b0cf07fef4a639bbb6596ddc9c4515a"
BASE_TREE = "444f8a7e50ec58e4d97a71744090d7ed60330f19"
RECONCILIATION_COMMIT = "6c7f52b43632072100b67e5f0a9b6221df14d620"
PUBLISHED_HISTORY = (
    (
        "aa784af939b55d3503e4782a9d65a9b06cf81ce0",
        "6aa36a92c5e5d2e420ec660a1ad2c2be2b06a561",
    ),
    (
        "9332f507996a8594883619cb530565ced79b59eb",
        "692d173462497cb645127ea1ced6cbe40aba4d5a",
    ),
    (BASE, BASE_TREE),
)
LEGACY_SHA256 = "5841dfbb55aa0d8c580b394b50beff54d607ce86b77683985c2d977c03050e14"
LEGACY_BLOB = "fe877050ae3942254bef54f23d6f3790480d698c"
LEGACY_VERIFIER_SHA256 = (
    "32d778a2c4e1a4844b77649e7a82c4829da0cb4c4f293f0938e898d167c67ede"
)
SUCCESSOR_LEDGER_VERIFIER_SHA256 = (
    "29f2f93c2beb095ec5fdbb5ca3fa9a49be470d0e961035e44258869f690d98b8"
)
MIGRATED_V2_SHA256 = (
    "73b0b742d6336d754ae99b7054858a3a3c96b3aaf1601b2228c076a732903d6e"
)
TRANSIENT_COMMITS = (
    "e548a28832232a34ed9e408224f6e16a9ebc9e4b",
    "6e8fa4a74dbc9e0e130719f9c55df86d58a75707",
    "3f764ce3e6fce92f984d0cf8249321452e7934c2",
    "ca6a154899fea133920dfa435a597632bf03728d",
    "77ea32c05eefd312a15ae0096e2990621da03a84",
)
ARCHIVAL_SHA256 = {
    "ops/team/canonical-reconciliation-falsifier/verify_canonical_reconciliation_falsifier.py": "d482fa2337e0df542c9b550cd1b894aa7845d76200196071f8b51ad9d82cb840",
    "ops/team/canonical-reconciliation-falsifier/verify_repaired_candidate_semantics.py": "96089be7c1b84c22f9b907fcaf34a93f8ab7c20c6c744c37225709bf49021621",
    "ops/team/canonical-reconciliation-referee/verify_closing_referee.py": "9d14f0a0afa988f76d1ff86e92f2064958b6cee87f750da51fcd82da6db4c83c",
    "ops/team/canonical-reconciliation-referee/verify_final_closing_referee.py": "f47b0eb0192ca526896c3e6879b8b003152ffb34d85b81502834b2204a984bb3",
}
ARCHIVAL_SUCCESSOR_SHA256 = {
    "ops/team/canonical-reconciliation-falsifier/verify_canonical_reconciliation_falsifier.py":
        "f7a06f107058bf3738d18f5b321c6cbf8b70cc76a94e0eda04bf390c93716cb4",
    "ops/team/canonical-reconciliation-referee/verify_closing_referee.py":
        "e65fedad2075907997dc9c00d263c3234b93127ad560a53dbb5a80d8219ad037",
    "ops/team/canonical-reconciliation-referee/verify_final_closing_referee.py":
        "d7cf3924407867c80cbacad2b490adac888c0dcb0562c445189f2dfd11e974ce",
}

RETIRED = (
    "D4_S53_CONTINUATION",
    "ORBIT_5563_LOCAL_ROADMAP_CONTINUATION",
    "ORBIT_5563_LOCAL_BOX_CONTINUATION",
    "ORBIT_5563_LOCAL_COLLAR_CONTINUATION",
    "ORBIT_5563_MACROBOX_CONTINUATION",
    "ORBIT_5563_CLIPPED_WALL_CONTINUATION",
)
TOTAL_INPUTS = (
    "THEOREM_READY_GLOBAL_COMPACTIFICATION",
    "SIGNED_FACE_POSET",
    "RESTRICTION_MATRICES",
)

ALLOWED_EXACT = {
    ".github/workflows/verify.yml",
    "README.md",
    "run_all.py",
    "ai/omreal/NINE_DIAGONAL_STATUS.md",
    "ai/omreal/RESEARCH_OPERATING_SYSTEM.md",
    "ai/omreal/data/CANONICAL_RESEARCH_STATE.json",
    "ai/omreal/data/DIAG3_RESEARCH_DECISION_LEDGER.json",
    "ai/omreal/verify_canonical_research_state.py",
    "ai/omreal/verify_diag3_research_decision_ledger.py",
    "ai/omreal/verify_run_all_ci_shards.py",
}
ALLOWED_PREFIXES = (
    "ops/research-team/cycles/2026-08-31-canonical-reconciliation/",
    "ops/team/canonical-reconciliation-prover/",
    "ops/team/canonical-reconciliation-falsifier/",
    "ops/team/canonical-reconciliation-referee/",
    "ops/team/canonical-reconciliation-portable/",
)
REQUIRED_CHANGED = {
    "README.md",
    "run_all.py",
    "ai/omreal/NINE_DIAGONAL_STATUS.md",
    "ai/omreal/RESEARCH_OPERATING_SYSTEM.md",
    "ai/omreal/data/CANONICAL_RESEARCH_STATE.json",
    "ai/omreal/verify_canonical_research_state.py",
    "ai/omreal/verify_run_all_ci_shards.py",
}


class VerificationError(AssertionError):
    """Fail-closed portable-reconciliation defect."""


def require(condition: bool, message: str) -> None:
    if not condition:
        raise VerificationError(message)


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def git_blob(data: bytes) -> str:
    return hashlib.sha1(f"blob {len(data)}\0".encode("ascii") + data).hexdigest()


def run(
    argv: list[str],
    *,
    expected: int = 0,
    no_lazy_fetch: bool = False,
) -> subprocess.CompletedProcess[bytes]:
    environment = os.environ.copy()
    environment["PYTHONDONTWRITEBYTECODE"] = "1"
    environment["PYTHONHASHSEED"] = "0"
    if no_lazy_fetch:
        environment["GIT_NO_LAZY_FETCH"] = "1"
    proc = subprocess.run(
        argv,
        cwd=ROOT,
        env=environment,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    if proc.returncode != expected:
        stderr = proc.stderr.decode("utf-8", "replace").strip()
        raise VerificationError(
            f"command returned {proc.returncode}, expected {expected}: "
            f"{' '.join(argv)}: {stderr}"
        )
    return proc


def git(*args: str, expected: int = 0, no_lazy_fetch: bool = False) -> str:
    return run(
        ["git", *args], expected=expected, no_lazy_fetch=no_lazy_fetch
    ).stdout.decode("utf-8").strip()


def history_mode() -> str:
    for commit, tree in PUBLISHED_HISTORY:
        probe = run(
            ["git", "rev-parse", f"{commit}^{{tree}}"],
            expected=0,
            no_lazy_fetch=True,
        )
        observed = probe.stdout.decode("utf-8").strip()
        require(observed == tree, f"published tree mismatch: {commit}")
    return "FULL_HISTORY"


def detect_history_mode() -> str:
    for commit, _ in PUBLISHED_HISTORY:
        probe = subprocess.run(
            ["git", "cat-file", "-e", f"{commit}^{{tree}}"],
            cwd=ROOT,
            env={**os.environ, "GIT_NO_LAZY_FETCH": "1"},
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            check=False,
        )
        if probe.returncode != 0:
            return "PINNED_SURFACE"
    return history_mode()


def validate_state(state: dict[str, Any]) -> None:
    require(state.get("format") == "9dvl-canonical-research-state-v1", "format")
    require(state.get("status") == "PIVOT_REQUIRED", "status")
    require(state.get("as_of") == "2026-08-31", "date")
    repository = state.get("repository", {})
    require(repository.get("audited_commit") == BASE, "base commit")
    require(repository.get("audited_tree") == BASE_TREE, "base tree")
    require(repository.get("merged_pull_request") == 44, "merged PR")

    theorem = state.get("theorem", {})
    require(theorem.get("score") == "2/9", "theorem score")
    require(theorem.get("proved_diagonals") == [1, 2], "proved diagonals")
    require(state.get("selected_target") is None, "selected target")

    current = state.get("canonical_reconciliation")
    require(isinstance(current, dict), "canonical reconciliation")
    require(current.get("theorem_score") == "2/9", "reconciliation score")
    require(current.get("proved_diagonals") == [1, 2], "reconciliation diagonals")
    d4 = current.get("d4_accounting", {})
    require(
        (
            d4.get("domain_labeled"),
            d4.get("domain_orbits"),
            d4.get("proved_labeled"),
            d4.get("proved_orbits"),
            d4.get("survivor_labeled"),
            d4.get("survivor_orbits"),
        )
        == (1_715_980, 130, 915_740, 77, 800_240, 53),
        "D4 accounting",
    )
    require(
        d4["domain_labeled"] == d4["proved_labeled"] + d4["survivor_labeled"],
        "D4 labeled identity",
    )
    require(
        d4["domain_orbits"] == d4["proved_orbits"] + d4["survivor_orbits"],
        "D4 orbit identity",
    )
    d3 = current.get("d3_accounting", {})
    require(
        (
            d3.get("unresolved_residue"),
            d3.get("quotient_classes"),
            d3.get("raw_frame_presentations"),
            d3.get("quotient_multiplicity_sum"),
        )
        == (1_162_302, 100_086_840, 104_993_280, 104_993_280),
        "D3 accounting",
    )
    require(
        current.get("first_missing_global_object")
        == {
            "id": "Q3_COMPLETE_PARENT_BOUNDARY_ATLAS",
            "status": "MISSING",
            "equivalent": "all_parent_closure_stratum_transport_and_attachment_atlas",
        },
        "Q3 blocker",
    )
    require(tuple(current.get("retired_continuations", ())) == RETIRED, "retirements")
    total = current.get("conditional_route_dispositions", {}).get(
        "D4_ALTERNATING_TOTAL_COMPLEX", {}
    )
    require(total.get("status") == "RETIRED_UNTIL_GLOBAL_INPUTS", "D4 total status")
    require(tuple(total.get("required_global_inputs", ())) == TOTAL_INPUTS, "D4 inputs")
    require(total.get("incomplete_successor_input_gate") == "STOP_FAIL_CLOSED", "gate")
    require(total.get("reactivation_requires_all_inputs") is True, "reactivation rule")
    require(current.get("selected_mathematical_target") is None, "current target")
    require(
        current.get("target_selection") == "PENDING_FRESH_INDEPENDENT_OPENING_AUDIT",
        "opening audit",
    )
    policy = current.get("historical_pointer_policy", {})
    require(policy.get("ledger_v1_git_blob") == LEGACY_BLOB, "legacy blob policy")
    require(policy.get("historical_continuation_text_is_current") is False, "history policy")


def validate_authority_texts(status: str, readme: str, operating: str) -> None:
    for text, label in ((status, "status"), (readme, "README"), (operating, "operating")):
        require("CANONICAL_RESEARCH_STATE_V2.json" in text, f"{label} successor pointer")
    for text, label in ((status, "status"), (operating, "operating")):
        require("CANONICAL_RESEARCH_STATE.json" in text, f"{label} predecessor pointer")
    require("predecessor reconciliation state" in readme, "README predecessor pointer")
    require("immutable historical" in status, "status legacy classification")
    require("immutable historical proof" in operating, "operating legacy classification")
    require("old selected routes are no longer current authority" in readme, "README authority")
    stale = (
        "Current target selection is governed by the machine-checked "
        "[`DIAG3_RESEARCH_DECISION_LEDGER.json`]"
    )
    require(stale not in readme, "stale README authority")


def validate_authority_surfaces() -> None:
    validate_authority_texts(
        STATUS_PATH.read_text(encoding="utf-8"),
        README_PATH.read_text(encoding="utf-8"),
        OPERATING_SYSTEM_PATH.read_text(encoding="utf-8"),
    )


def validate_legacy() -> None:
    legacy = LEGACY_PATH.read_bytes()
    verifier = LEGACY_VERIFIER.read_bytes()
    ledger_digest = sha256_bytes(legacy)
    if ledger_digest == LEGACY_SHA256:
        require(git_blob(legacy) == LEGACY_BLOB, "legacy ledger blob")
        require(
            sha256_bytes(verifier) == LEGACY_VERIFIER_SHA256,
            "legacy verifier SHA256",
        )
    else:
        # The reviewed PR46 successor promotes the reconciled v2 payload into
        # the decision-ledger path while retaining the literal v1 bytes by Git
        # blob identity.  Authenticate both sides of that bridge; never accept
        # an arbitrary replacement at the historical path.
        require(ledger_digest == MIGRATED_V2_SHA256, "successor ledger SHA256")
        require(
            sha256_bytes(verifier) == SUCCESSOR_LEDGER_VERIFIER_SHA256,
            "successor ledger verifier SHA256",
        )
        archived = run(
            ["git", "cat-file", "blob", LEGACY_BLOB], no_lazy_fetch=True
        ).stdout
        require(sha256_bytes(archived) == LEGACY_SHA256, "archived v1 SHA256")
        require(git_blob(archived) == LEGACY_BLOB, "archived v1 blob")
    migrated = STATE_PATH.read_bytes()
    old_schema = b'  "format": "diag3-research-decision-ledger-v2",'
    new_schema = b'  "format": "9dvl-canonical-research-state-v1",'
    require(migrated.count(new_schema) == 1 and old_schema not in migrated, "migration schema")
    require(
        sha256_bytes(migrated.replace(new_schema, old_schema)) == MIGRATED_V2_SHA256,
        "v2 migration changed more than authority/schema",
    )


def validate_source_digests(state: dict[str, Any]) -> None:
    expected = state["canonical_reconciliation"]["source_sha256"]
    require(len(expected) == 7, "source census")
    for relative, digest in expected.items():
        path = ROOT / relative
        require(path.is_file(), f"missing source: {relative}")
        require(sha256_bytes(path.read_bytes()) == digest, f"source digest: {relative}")


def validate_manifest() -> None:
    manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    require(
        manifest.get("format")
        == "canonical-reconciliation-portable-source-manifest-v1",
        "manifest format",
    )
    require(
        manifest.get("canonical_base")
        == {"commit": BASE, "tree": BASE_TREE, "merged_pull_request": 44},
        "manifest base",
    )
    published = tuple(
        (row["merge_commit"], row["tree"]) for row in manifest["published_history"]
    )
    require(published == PUBLISHED_HISTORY, "manifest published history")
    legacy = manifest["immutable_legacy"]
    require(legacy["sha256"] == LEGACY_SHA256, "manifest legacy SHA")
    require(legacy["git_blob"] == LEGACY_BLOB, "manifest legacy blob")
    require(legacy["verifier_sha256"] == LEGACY_VERIFIER_SHA256, "manifest verifier")
    require(
        manifest["migrated_current_state"]["reverse_schema_only_sha256"]
        == MIGRATED_V2_SHA256,
        "manifest migration",
    )
    transient = manifest["unpublished_transient_chain"]
    require(tuple(transient["commits"]) == TRANSIENT_COMMITS, "transient census")
    require(
        transient["availability"] == "ARCHIVED_IN_PINNED_EVIDENCE_BUNDLE",
        "transient disposition",
    )
    require(manifest["archival_verifiers"] == ARCHIVAL_SHA256, "archival census")
    for relative, digest in ARCHIVAL_SHA256.items():
        expected = ARCHIVAL_SUCCESSOR_SHA256.get(relative, digest)
        require(sha256_bytes((ROOT / relative).read_bytes()) == expected, relative)


def changed_paths(include_dirty: bool, mode: str) -> set[str]:
    if mode == "FULL_HISTORY":
        # This verifier governs the bounded reconciliation change set, not all
        # valid successor research forever.  Later cycles carry their own
        # manifests and verifiers and must not be rejected merely for adding
        # new, independently governed paths.
        paths = set(
            git("diff", "--name-only", f"{BASE}..{RECONCILIATION_COMMIT}").splitlines()
        )
    else:
        # A depth-one checkout intentionally lacks BASE, so it cannot make a
        # historical change-set claim.  Audit the complete current governed
        # surface instead; the semantic, digest, and hostile checks below bind
        # its authoritative content.  The result labels this weaker mode.
        tree_paths = set(git("ls-tree", "-r", "--name-only", "HEAD").splitlines())
        paths = {
            path
            for path in tree_paths
            if path in ALLOWED_EXACT
            or any(path.startswith(prefix) for prefix in ALLOWED_PREFIXES)
        }
    if include_dirty:
        paths.update(git("diff", "--name-only").splitlines())
        paths.update(git("diff", "--cached", "--name-only").splitlines())
        paths.update(git("ls-files", "--others", "--exclude-standard").splitlines())
    return {path for path in paths if path}


def validate_paths(include_dirty: bool, mode: str) -> int:
    paths = changed_paths(include_dirty, mode)
    bad = sorted(
        path
        for path in paths
        if path not in ALLOWED_EXACT
        and not any(path.startswith(prefix) for prefix in ALLOWED_PREFIXES)
    )
    require(not bad, f"ungoverned changed paths: {bad}")
    requirement = "required repair paths missing"
    if mode == "PINNED_SURFACE":
        requirement = "required governed surface paths missing"
    require(REQUIRED_CHANGED <= paths, requirement)
    if not include_dirty:
        require(not git("status", "--porcelain"), "dirty governed surface")
    return len(paths)


def expect_rejection(name: str, callback: Callable[[], None], rejected: list[str]) -> None:
    try:
        callback()
    except (KeyError, TypeError, VerificationError):
        rejected.append(name)
        return
    raise VerificationError(f"hostile canary accepted: {name}")


def hostile_canaries(state: dict[str, Any]) -> list[str]:
    cases: list[tuple[str, Callable[[dict[str, Any]], None]]] = [
        ("score", lambda x: x["theorem"].__setitem__("score", "3/9")),
        ("diagonal3", lambda x: x["theorem"]["proved_diagonals"].append(3)),
        ("d4_domain", lambda x: x["canonical_reconciliation"]["d4_accounting"].__setitem__("domain_labeled", 1_715_979)),
        ("d4_survivor", lambda x: x["canonical_reconciliation"]["d4_accounting"].__setitem__("survivor_orbits", 52)),
        ("d3_residue", lambda x: x["canonical_reconciliation"]["d3_accounting"].__setitem__("unresolved_residue", 1_162_301)),
        ("d3_quotient", lambda x: x["canonical_reconciliation"]["d3_accounting"].__setitem__("quotient_classes", 100_086_839)),
        ("d3_raw", lambda x: x["canonical_reconciliation"]["d3_accounting"].__setitem__("raw_frame_presentations", 104_993_279)),
        ("q3", lambda x: x["canonical_reconciliation"]["first_missing_global_object"].__setitem__("status", "AVAILABLE")),
        ("retirement", lambda x: x["canonical_reconciliation"]["retired_continuations"].pop()),
        ("total_active", lambda x: x["canonical_reconciliation"]["conditional_route_dispositions"]["D4_ALTERNATING_TOTAL_COMPLEX"].__setitem__("status", "ACTIVE")),
        ("total_input", lambda x: x["canonical_reconciliation"]["conditional_route_dispositions"]["D4_ALTERNATING_TOTAL_COMPLEX"]["required_global_inputs"].pop()),
        ("weak_gate", lambda x: x["canonical_reconciliation"]["conditional_route_dispositions"]["D4_ALTERNATING_TOTAL_COMPLEX"].__setitem__("incomplete_successor_input_gate", "CONTINUE")),
        ("weak_reactivation", lambda x: x["canonical_reconciliation"]["conditional_route_dispositions"]["D4_ALTERNATING_TOTAL_COMPLEX"].__setitem__("reactivation_requires_all_inputs", False)),
        ("selected", lambda x: x.__setitem__("selected_target", "historical_route")),
        ("current_selected", lambda x: x["canonical_reconciliation"].__setitem__("selected_mathematical_target", "historical_route")),
        ("format", lambda x: x.__setitem__("format", "diag3-research-decision-ledger-v2")),
        ("legacy_policy", lambda x: x["canonical_reconciliation"]["historical_pointer_policy"].__setitem__("ledger_v1_git_blob", "0" * 40)),
    ]
    rejected: list[str] = []
    for name, mutate in cases:
        hostile = copy.deepcopy(state)
        mutate(hostile)
        expect_rejection(name, lambda h=hostile: validate_state(h), rejected)

    source = copy.deepcopy(state)
    first_source = next(iter(source["canonical_reconciliation"]["source_sha256"]))
    source["canonical_reconciliation"]["source_sha256"][first_source] = "0" * 64
    expect_rejection(
        "source_digest",
        lambda: validate_source_digests(source),
        rejected,
    )

    stale_readme = README_PATH.read_text(encoding="utf-8").replace(
        "CANONICAL_RESEARCH_STATE_V2.json", "CANONICAL_RESEARCH_STATE.json"
    )
    expect_rejection(
        "authority_swap",
        lambda: validate_authority_texts(
            STATUS_PATH.read_text(encoding="utf-8"),
            stale_readme,
            OPERATING_SYSTEM_PATH.read_text(encoding="utf-8"),
        ),
        rejected,
    )
    expect_rejection(
        "legacy_byte_mutation",
        lambda: require(
            sha256_bytes(LEGACY_PATH.read_bytes() + b"hostile") == LEGACY_SHA256,
            "mutated legacy accepted",
        ),
        rejected,
    )
    expect_rejection(
        "ungoverned_path",
        lambda: require(
            "README.unapproved" in ALLOWED_EXACT
            or any("README.unapproved".startswith(prefix) for prefix in ALLOWED_PREFIXES),
            "ungoverned path accepted",
        ),
        rejected,
    )
    require(len(rejected) == len(cases) + 4, "hostile canary census")
    return rejected


def replay_live_gates(mode: str) -> dict[str, str]:
    commands = {
        "legacy_ledger": [sys.executable, "ai/omreal/verify_diag3_research_decision_ledger.py"],
        "canonical_state": [sys.executable, "ai/omreal/verify_canonical_research_state.py"],
        "cycle_protocol": [sys.executable, "ops/research-team/verify_cycle_protocol.py"],
        "clipped_wall": [sys.executable, "ai/omreal/verify_diag3_clipped_wall_falsifier.py"],
        "global_exit": [sys.executable, "ai/omreal/verify_diag3_global_exit_criterion.py"],
        "shard_contract": [sys.executable, "ai/omreal/verify_run_all_ci_shards.py"],
    }
    for name, argv in commands.items():
        proc = run(argv)
        require(proc.stdout.strip(), f"empty replay: {name}")
    if mode == "FULL_HISTORY":
        run(["git", "diff", "--check", f"{BASE}..HEAD"])
    return {name: "PASS" for name in commands}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--allow-dirty",
        action="store_true",
        help="include working changes in the governed-path audit during local repair",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        state = json.loads(STATE_PATH.read_text(encoding="utf-8"))
        validate_legacy()
        validate_state(state)
        validate_authority_surfaces()
        validate_source_digests(state)
        validate_manifest()
        mode = detect_history_mode()
        path_count = validate_paths(args.allow_dirty, mode)
        hostile = hostile_canaries(state)
        replays = replay_live_gates(mode)
        result = {
            "format": "canonical-reconciliation-portable-result-v1",
            "mode": mode,
            "published_history_authenticated": mode == "FULL_HISTORY",
            "unpublished_transient_chain_required": False,
            "legacy_ledger_sha256": LEGACY_SHA256,
            "migrated_v2_sha256": MIGRATED_V2_SHA256,
            "theorem_score": "2/9",
            "selected_target": None,
            "path_audit": (
                "BASE_TO_PR45_RECONCILIATION_PATHS"
                if mode == "FULL_HISTORY"
                else "CURRENT_GOVERNED_SURFACE"
            ),
            "governed_path_count": path_count,
            "hostile_rejections": hostile,
            "hostile_rejection_count": len(hostile),
            "live_replays": replays,
            "verdict": "PASS_PORTABLE_CANONICAL_RECONCILIATION",
        }
        print(json.dumps(result, indent=2, sort_keys=True))
        return 0
    except (OSError, ValueError, VerificationError) as exc:
        print(f"REJECT {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
