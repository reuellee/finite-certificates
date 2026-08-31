#!/usr/bin/env python3
"""Schema-neutral, exact-head replay for the repaired reconciliation candidate.

This verifier uses only the Python standard library.  It reads the reviewed
candidate with ``git show`` and does not import either canonical verifier or
the original falsifier verifier.  Their executions are supplemental controls.
"""

from __future__ import annotations

import copy
import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path
from typing import Any, Callable


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]

CANDIDATE = "77ea32c05eefd312a15ae0096e2990621da03a84"
CANDIDATE_TREE = "669c6782874b2d8de97f0d78a5ee86cb5c0c3fcc"
REPAIR = "ca6a154899fea133920dfa435a597632bf03728d"
REPAIR_TREE = "00bc0e4affed33ed29e7dee5ba17f0c3d4b5e3fd"
REJECTION_REVIEW = "3f764ce3e6fce92f984d0cf8249321452e7934c2"
REJECTION_REVIEW_TREE = "de18908882290dd304f2558daf439a18d170d077"
REJECTED_CANDIDATE = "6e8fa4a74dbc9e0e130719f9c55df86d58a75707"
REJECTED_TREE = "10fd994ccc89b722cd92118759cee65fc8a1906c"
OPENING = "e548a28832232a34ed9e408224f6e16a9ebc9e4b"
OPENING_TREE = "99d7c10657088d6cebc7c80568f7224d1079af7c"
BASE = "e666990f5b0cf07fef4a639bbb6596ddc9c4515a"
BASE_TREE = "444f8a7e50ec58e4d97a71744090d7ed60330f19"
PR42 = "aa784af939b55d3503e4782a9d65a9b06cf81ce0"
PR42_TREE = "6aa36a92c5e5d2e420ec660a1ad2c2be2b06a561"
PR43 = "9332f507996a8594883619cb530565ced79b59eb"
PR43_TREE = "692d173462497cb645127ea1ced6cbe40aba4d5a"

STATUS_PATH = "ai/omreal/NINE_DIAGONAL_STATUS.md"
LEDGER_PATH = "ai/omreal/data/DIAG3_RESEARCH_DECISION_LEDGER.json"
CANONICAL_VERIFIER_PATH = "ai/omreal/verify_diag3_research_decision_ledger.py"
ORIGINAL_FALSIFIER_PATH = (
    "ops/team/canonical-reconciliation-falsifier/"
    "verify_canonical_reconciliation_falsifier.py"
)

SOURCE_SHA256 = {
    "ops/research-team/PROTOCOL.md": (
        BASE,
        "7b3fe051677d31748d483de006d9cfc97d26518f5103016371ed7ccee469654c",
        True,
    ),
    STATUS_PATH: (
        BASE,
        "f4360254e5c7e624b9c9194bb7cb0b3844d5fe3201ec9bc688c2f18d37276782",
        False,
    ),
    LEDGER_PATH: (
        BASE,
        "5841dfbb55aa0d8c580b394b50beff54d607ce86b77683985c2d977c03050e14",
        False,
    ),
    CANONICAL_VERIFIER_PATH: (
        BASE,
        "32d778a2c4e1a4844b77649e7a82c4829da0cb4c4f293f0938e898d167c67ede",
        False,
    ),
    "ops/research-team/cycles/2026-08-29-diag4-top-sheaf/CYCLE_REPORT.md": (
        BASE,
        "26383e2c2bd4306fc1f10f94aa695df2844865821912c8aa10aaae979d7e2923",
        True,
    ),
    "ops/team/diag4-strategy-referee/FINAL_DELTA_REREVIEW.md": (
        BASE,
        "dc36cd3b95eb949e41e1a2c12b8ace8b87f15f16af5487acc16c3642b8bca434",
        True,
    ),
    "ops/research-team/cycles/2026-08-30-diag4-s53-top-sheaf/CYCLE_REPORT.md": (
        BASE,
        "e6f717a85dd078fcfcac87fbad0221801ad580cba408bccc7103c5a17c4027d2",
        True,
    ),
    "ops/team/diag4-s53-referee/CLOSING_REVIEW.md": (
        BASE,
        "7eabc7700ea0a6e2dde0b05eab698b3bff98911c07aa11dc0a12250cacda7e4c",
        True,
    ),
    "ops/research-team/cycles/2026-08-30-diag3-orbit5563-global-exit/CYCLE_REPORT.md": (
        BASE,
        "a2baf8cf0a8e0cfdfc845f38569557e95e2953995ad8964b912ef8738ffa7c5f",
        True,
    ),
    "ops/team/diag3-orbit5563-referee/CLOSING_REVIEW.md": (
        BASE,
        "e1801e2782445374f606dfeef51f24694edaaaf494581ee1956738ae74d67a35",
        True,
    ),
    "ops/research-team/cycles/2026-08-31-canonical-reconciliation/CYCLE.md": (
        OPENING,
        "8ea47d432e74fd67e727516a8bc23a3a0c62476bc6b08d6e36ef783eac87e1a8",
        True,
    ),
    "ops/research-team/cycles/2026-08-31-canonical-reconciliation/WORK_ORDERS.yaml": (
        OPENING,
        "cf5b3768af0bafef63853b023ad03e97d0be5e2221d38dd6e1f55afc4352d499",
        True,
    ),
}

LEDGER_SOURCE_SHA256 = {
    path: digest
    for path, (_, digest, _) in SOURCE_SHA256.items()
    if path
    in {
        "ops/research-team/cycles/2026-08-31-canonical-reconciliation/CYCLE.md",
        "ops/research-team/cycles/2026-08-31-canonical-reconciliation/WORK_ORDERS.yaml",
        "ops/research-team/cycles/2026-08-29-diag4-top-sheaf/CYCLE_REPORT.md",
        "ops/research-team/cycles/2026-08-30-diag4-s53-top-sheaf/CYCLE_REPORT.md",
        "ops/team/diag4-s53-referee/CLOSING_REVIEW.md",
        "ops/research-team/cycles/2026-08-30-diag3-orbit5563-global-exit/CYCLE_REPORT.md",
        "ops/team/diag3-orbit5563-referee/CLOSING_REVIEW.md",
    }
}

CANDIDATE_OUTPUT_SHA256 = {
    STATUS_PATH: "a5865422b3337aba0ccd71eb02c1d521c201f4c338b9a2054afa0d21923e35b0",
    LEDGER_PATH: "73b0b742d6336d754ae99b7054858a3a3c96b3aaf1601b2228c076a732903d6e",
    CANONICAL_VERIFIER_PATH: (
        "3353ed3f7f185034f97a3e440e7957ebcf4046032a8fbf20bbc5d7e445060491"
    ),
}

PRESERVED_REJECTION_SHA256 = {
    ORIGINAL_FALSIFIER_PATH: (
        "d482fa2337e0df542c9b550cd1b894aa7845d76200196071f8b51ad9d82cb840"
    ),
    "ops/team/canonical-reconciliation-falsifier/CANDIDATE_REVIEW.md": (
        "9cb60fc5f89857c97be2b36a48746ab005aa866c4befd1e6148654c1c30a7e2e"
    ),
    "ops/team/canonical-reconciliation-falsifier/CANDIDATE_HANDOFF.yaml": (
        "1adb7d13c83ae683b73b4cb36d636502d267d37771ac68427ec8f71509ed3e7a"
    ),
    "ops/team/canonical-reconciliation-referee/CLOSING_REVIEW.md": (
        "2a7e79b451fc5cd01ec62d739019967998d4825cd4c34ef6962750ffeb3edf04"
    ),
    "ops/team/canonical-reconciliation-referee/CLOSING_HANDOFF.yaml": (
        "fc920833045b91768ecc524449e379ca549092279eae93843f3db6ced8ee7d80"
    ),
    "ops/team/canonical-reconciliation-referee/CLOSING_MANIFEST.json": (
        "3c62bc8c943cf8582c40609634a5ad185dc51d8c0a6e723095b2d58abe1ebd9f"
    ),
    "ops/team/canonical-reconciliation-referee/verify_closing_referee.py": (
        "9d14f0a0afa988f76d1ff86e92f2064958b6cee87f750da51fcd82da6db4c83c"
    ),
}

REQUIRED_LOCAL_RETIREMENTS = {
    "D4_S53_CONTINUATION",
    "ORBIT_5563_LOCAL_ROADMAP_CONTINUATION",
    "ORBIT_5563_LOCAL_BOX_CONTINUATION",
    "ORBIT_5563_LOCAL_COLLAR_CONTINUATION",
    "ORBIT_5563_MACROBOX_CONTINUATION",
    "ORBIT_5563_CLIPPED_WALL_CONTINUATION",
}

REQUIRED_TOTAL_INPUTS = {
    "THEOREM_READY_GLOBAL_COMPACTIFICATION",
    "SIGNED_FACE_POSET",
    "RESTRICTION_MATRICES",
}

ALLOWED_EXACT_PATHS = {
    STATUS_PATH,
    LEDGER_PATH,
    CANONICAL_VERIFIER_PATH,
    "ops/research-team/cycles/2026-08-31-canonical-reconciliation/CYCLE_REPORT.md",
}
ALLOWED_PREFIXES = (
    "ops/team/canonical-reconciliation-prover/",
    "ops/team/canonical-reconciliation-falsifier/",
    "ops/team/canonical-reconciliation-referee/",
)

ORIGINAL_REJECTION = (
    "REJECT candidate status missing accepted fact: "
    "e666990f5b0cf07fef4a639bbb6596ddc9c4515a"
)


class VerificationError(AssertionError):
    """Fail-closed semantic verification failure."""


def require(condition: bool, message: str) -> None:
    if not condition:
        raise VerificationError(message)


def sha256(data: bytes) -> str:
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
            f"git {' '.join(args)} failed: "
            f"{proc.stderr.decode('utf-8', 'replace').strip()}"
        )
    return proc.stdout


def git_show(revision: str, path: str) -> bytes:
    return run_git("show", f"{revision}:{path}")


def verify_commit(commit: str, tree: str) -> None:
    require(run_git("rev-parse", commit).decode().strip() == commit, f"commit {commit}")
    observed = run_git("rev-parse", f"{commit}^{{tree}}").decode().strip()
    require(observed == tree, f"tree mismatch at {commit}: {observed}")


def verify_identity_and_history() -> None:
    for commit, tree in (
        (PR42, PR42_TREE),
        (PR43, PR43_TREE),
        (BASE, BASE_TREE),
        (OPENING, OPENING_TREE),
        (REJECTED_CANDIDATE, REJECTED_TREE),
        (REJECTION_REVIEW, REJECTION_REVIEW_TREE),
        (REPAIR, REPAIR_TREE),
        (CANDIDATE, CANDIDATE_TREE),
    ):
        verify_commit(commit, tree)

    require(run_git("rev-parse", f"{CANDIDATE}^").decode().strip() == REPAIR, "candidate parent")
    require(run_git("rev-parse", f"{REPAIR}^").decode().strip() == REJECTION_REVIEW, "repair parent")
    require(
        run_git("rev-parse", f"{REJECTION_REVIEW}^").decode().strip()
        == REJECTED_CANDIDATE,
        "rejection-review parent",
    )
    for ancestor in (
        PR42,
        PR43,
        BASE,
        OPENING,
        REJECTED_CANDIDATE,
        REJECTION_REVIEW,
        REPAIR,
    ):
        run_git("merge-base", "--is-ancestor", ancestor, CANDIDATE)


def verify_sources() -> None:
    for path, (revision, expected, protected) in SOURCE_SHA256.items():
        frozen = git_show(revision, path)
        require(sha256(frozen) == expected, f"source digest: {path}")
        if protected:
            candidate_bytes = git_show(CANDIDATE, path)
            require(candidate_bytes == frozen, f"protected source changed: {path}")


def candidate_bytes(path: str) -> bytes:
    data = git_show(CANDIDATE, path)
    require(sha256(data) == CANDIDATE_OUTPUT_SHA256[path], f"candidate digest: {path}")
    current = (ROOT / path).read_bytes()
    require(current == data, f"review worktree differs from candidate: {path}")
    return data


def verify_rejection_history() -> None:
    for path, expected in PRESERVED_REJECTION_SHA256.items():
        data = git_show(CANDIDATE, path)
        require(sha256(data) == expected, f"rejection artifact changed: {path}")
    review = git_show(
        CANDIDATE,
        "ops/team/canonical-reconciliation-falsifier/CANDIDATE_REVIEW.md",
    ).decode("utf-8")
    require("REJECT_ACTIONABLE_ROUTE_OMISSION" in review, "old rejection verdict missing")
    require(REJECTED_CANDIDATE in review and REJECTED_TREE in review, "old head missing")


def normalized(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def validate_status(text: str) -> None:
    heading = "## Current canonical precedence through merged PR #44"
    require(text.count(heading) == 1, "current status heading")
    require("## Result ledger" in text, "result-ledger boundary")
    current = text[text.index(heading) : text.index("## Result ledger")]
    flat = normalized(current)
    lower = flat.lower()
    for token in (
        "1,715,980 / 130 = 915,740 / 77 + 800,240 / 53",
        "1,162,302",
        "100,086,840",
        "104,993,280",
        "Q3_COMPLETE_PARENT_BOUNDARY_ATLAS",
        "PIVOT_REQUIRED",
        "RETIRED_UNTIL_GLOBAL_INPUTS",
        "STOP` fail-closed",
    ):
        require(token in current or token in flat, f"status token: {token}")
    require("the theorem ledger is unchanged at **2/9**" in lower, "status score")
    require("any further d4-s53 continuation is **retired**" in lower, "D4-S53 status")
    require("distinct from that d4-s53 retirement" in lower, "routes not distinct")
    require("complete alternating d4 total-complex route" in lower, "total D4 route")
    require("theorem-ready global compactification" in lower, "global compactification")
    require("signed face poset" in lower, "signed face poset")
    require("restriction matrices" in lower, "restriction matrices")
    require("no selected mathematical target" in lower, "null target status")
    require(
        all(word in lower for word in ("roadmap", "box", "collar", "macrobox", "clipped-wall", "retired")),
        "orbit-5563 retirements",
    )
    require("3/9" not in current, "false status score")
    require("d4-s53 continuation is **active**" not in lower, "D4-S53 reactivated")
    require("total-complex route is **`active`**" not in lower, "total D4 reactivated")


def find_obligation(ledger: dict[str, Any], obligation_id: str) -> dict[str, Any]:
    rows = [
        row
        for row in ledger.get("invariant_obligations", [])
        if isinstance(row, dict) and row.get("id") == obligation_id
    ]
    require(len(rows) == 1, f"obligation {obligation_id}")
    return rows[0]


def validate_ledger(ledger: dict[str, Any]) -> None:
    require(ledger.get("format") == "diag3-research-decision-ledger-v2", "ledger format")
    require(ledger.get("status") == "PIVOT_REQUIRED", "ledger status")
    require(ledger.get("as_of") == "2026-08-31", "ledger date")
    repository = ledger.get("repository", {})
    require(repository.get("audited_commit") == BASE, "canonical commit")
    require(repository.get("audited_tree") == BASE_TREE, "canonical tree")
    require(repository.get("merged_pull_request") == 44, "merged PR")

    theorem = ledger.get("theorem", {})
    require(theorem.get("score") == "2/9", "theorem score")
    require(theorem.get("proved_diagonals") == [1, 2], "proved diagonals")
    require(theorem.get("active_diagonal") == 3, "active diagonal")
    require(ledger.get("selected_target") is None, "selected target")

    current = ledger.get("canonical_reconciliation", {})
    require(current.get("precedence") == "CURRENT_THROUGH_MERGED_PR_44", "precedence")
    require(current.get("theorem_score") == "2/9", "current score")
    require(current.get("proved_diagonals") == [1, 2], "current proved diagonals")
    require(current.get("selected_mathematical_target") is None, "current target")
    require(
        current.get("target_selection") == "PENDING_FRESH_INDEPENDENT_OPENING_AUDIT",
        "target selection",
    )

    d4 = current.get("d4_accounting", {})
    expected_d4 = {
        "domain_labeled": 1715980,
        "domain_orbits": 130,
        "proved_labeled": 915740,
        "proved_orbits": 77,
        "survivor_labeled": 800240,
        "survivor_orbits": 53,
    }
    for key, value in expected_d4.items():
        require(d4.get(key) == value, f"D4 {key}")
    require(d4.get("survivor_delta_after_pr43") == {"labeled": 0, "orbits": 0}, "D4 delta")
    require(d4["domain_labeled"] == d4["proved_labeled"] + d4["survivor_labeled"], "D4 support arithmetic")
    require(d4["domain_orbits"] == d4["proved_orbits"] + d4["survivor_orbits"], "D4 orbit arithmetic")

    d3 = current.get("d3_accounting", {})
    expected_d3 = {
        "unresolved_residue": 1162302,
        "quotient_classes": 100086840,
        "raw_frame_presentations": 104993280,
        "quotient_multiplicity_sum": 104993280,
        "row_delta_after_pr44": 0,
    }
    for key, value in expected_d3.items():
        require(d3.get(key) == value, f"D3 {key}")
    require(d3["raw_frame_presentations"] == d3["quotient_multiplicity_sum"], "D3 raw sum")

    q3 = current.get("first_missing_global_object", {})
    require(q3.get("id") == "Q3_COMPLETE_PARENT_BOUNDARY_ATLAS", "Q3 id")
    require(q3.get("status") == "MISSING", "Q3 status")

    retired = current.get("retired_continuations", [])
    require(isinstance(retired, list), "retirement list")
    require(REQUIRED_LOCAL_RETIREMENTS.issubset(set(retired)), "local route retirement")
    require("D4_S53_CONTINUATION_ACTIVE" not in retired, "D4-S53 active")

    total = current.get("conditional_route_dispositions", {}).get(
        "D4_ALTERNATING_TOTAL_COMPLEX", {}
    )
    require(total.get("status") == "RETIRED_UNTIL_GLOBAL_INPUTS", "total D4 status")
    require(total.get("distinct_from") == "D4_S53_CONTINUATION", "route distinction")
    require(set(total.get("required_global_inputs", [])) == REQUIRED_TOTAL_INPUTS, "total D4 inputs")
    require(total.get("incomplete_successor_input_gate") == "STOP_FAIL_CLOSED", "input gate")
    require(total.get("reactivation_requires_all_inputs") is True, "reactivation gate")

    history = current.get("historical_pointer_policy", {})
    require(history.get("historical_continuation_text_is_current") is False, "history authority")
    require(current.get("source_sha256") == LEDGER_SOURCE_SHA256, "ledger source binding")

    triple = find_obligation(ledger, "diag3_triple_hc0")
    require(triple.get("status") == "OPEN", "triple obligation")
    require(
        (
            triple.get("universe_count"),
            triple.get("proved_noncompact_count"),
            triple.get("unresolved_count"),
        )
        == (79102449, 77940147, 1162302),
        "triple counts",
    )
    pair = find_obligation(ledger, "diag3_pair_hc1")
    require(pair.get("status") == "OPEN", "pair obligation")


def validate_canonical_verifier(text: str) -> None:
    continuation_block = re.search(
        r"RETIRED_CONTINUATIONS\s*=\s*\[(.*?)\]\n", text, flags=re.DOTALL
    )
    require(continuation_block is not None, "canonical verifier retirement constant")
    require(
        '"D4_S53_CONTINUATION"' in continuation_block.group(1),
        "canonical verifier D4-S53 retirement",
    )
    required = (
        "D4_TOTAL_COMPLEX_DISPOSITION",
        '"status": "RETIRED_UNTIL_GLOBAL_INPUTS"',
        '"distinct_from": "D4_S53_CONTINUATION"',
        '"incomplete_successor_input_gate": "STOP_FAIL_CLOSED"',
        '"reactivation_requires_all_inputs": True',
        'current["retired_continuations"] == RETIRED_CONTINUATIONS',
        '"D4_ALTERNATING_TOTAL_COMPLEX": D4_TOTAL_COMPLEX_DISPOSITION',
        '"d4-total-complex-reactivation"',
        '"hostile canary accepted: d4-total-complex-omission"',
        '"RETIRED_UNTIL_GLOBAL_INPUTS"',
        '"STOP` fail-closed"',
        '"PASS 9/9 hostile canonical-state canaries rejected"',
    )
    for token in required:
        require(token in text, f"canonical verifier token: {token}")


def is_allowed_path(path: str) -> bool:
    return path in ALLOWED_EXACT_PATHS or path.startswith(ALLOWED_PREFIXES)


def changed_paths() -> list[str]:
    paths = run_git("diff", "--name-only", f"{OPENING}..{CANDIDATE}").decode().splitlines()
    require(len(paths) == 18, f"changed path count: {len(paths)}")
    require(not [path for path in paths if not is_allowed_path(path)], "unapproved changed path")
    return paths


def run_candidate_native_verifier() -> None:
    proc = subprocess.run(
        [sys.executable, CANONICAL_VERIFIER_PATH],
        cwd=ROOT,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        check=False,
    )
    require(proc.returncode == 0, f"candidate verifier: {proc.stderr.strip()}")
    require("PASS 9/9 hostile canonical-state canaries rejected" in proc.stdout, "native canaries")


def run_original_negative_control() -> None:
    proc = subprocess.run(
        [sys.executable, ORIGINAL_FALSIFIER_PATH, "--candidate"],
        cwd=ROOT,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        check=False,
    )
    require(proc.returncode == 1, "original candidate gate no longer rejects")
    require(proc.stderr.strip() == ORIGINAL_REJECTION, "original rejection changed")


def expect_rejection(
    name: str, callback: Callable[[], None], rejected: list[str]
) -> None:
    try:
        callback()
    except VerificationError:
        rejected.append(name)
        return
    raise VerificationError(f"hostile canary accepted: {name}")


def replace_required(text: str, old: str, new: str) -> str:
    require(old in text, f"mutation source missing: {old}")
    return text.replace(old, new, 1)


def run_hostile_canaries(
    status: str,
    ledger: dict[str, Any],
    verifier: str,
    paths: list[str],
) -> list[str]:
    rejected: list[str] = []

    d4_status_phrase = "any further D4-S53 continuation is **retired**"
    expect_rejection(
        "status_d4_s53_deletion",
        lambda: validate_status(replace_required(status, d4_status_phrase, "")),
        rejected,
    )
    expect_rejection(
        "status_d4_s53_reactivation",
        lambda: validate_status(
            replace_required(status, d4_status_phrase, "D4-S53 continuation is **active**")
        ),
        rejected,
    )
    expect_rejection(
        "status_total_d4_deletion",
        lambda: validate_status(
            replace_required(status, "RETIRED_UNTIL_GLOBAL_INPUTS", "OMITTED")
        ),
        rejected,
    )
    expect_rejection(
        "status_total_d4_reactivation",
        lambda: validate_status(
            replace_required(status, "RETIRED_UNTIL_GLOBAL_INPUTS", "ACTIVE")
        ),
        rejected,
    )

    d4_deleted = copy.deepcopy(ledger)
    d4_deleted["canonical_reconciliation"]["retired_continuations"].remove(
        "D4_S53_CONTINUATION"
    )
    expect_rejection("ledger_d4_s53_deletion", lambda: validate_ledger(d4_deleted), rejected)

    d4_active = copy.deepcopy(ledger)
    d4_routes = d4_active["canonical_reconciliation"]["retired_continuations"]
    d4_routes[d4_routes.index("D4_S53_CONTINUATION")] = "D4_S53_CONTINUATION_ACTIVE"
    expect_rejection("ledger_d4_s53_reactivation", lambda: validate_ledger(d4_active), rejected)

    total_deleted = copy.deepcopy(ledger)
    del total_deleted["canonical_reconciliation"]["conditional_route_dispositions"][
        "D4_ALTERNATING_TOTAL_COMPLEX"
    ]
    expect_rejection("ledger_total_d4_deletion", lambda: validate_ledger(total_deleted), rejected)

    total_active = copy.deepcopy(ledger)
    total_active["canonical_reconciliation"]["conditional_route_dispositions"][
        "D4_ALTERNATING_TOTAL_COMPLEX"
    ]["status"] = "ACTIVE"
    expect_rejection("ledger_total_d4_reactivation", lambda: validate_ledger(total_active), rejected)

    expect_rejection(
        "verifier_d4_s53_deletion",
        lambda: validate_canonical_verifier(
            replace_required(verifier, '"D4_S53_CONTINUATION"', '"OMITTED"')
        ),
        rejected,
    )
    expect_rejection(
        "verifier_d4_s53_reactivation",
        lambda: validate_canonical_verifier(
            replace_required(
                verifier, '"D4_S53_CONTINUATION"', '"D4_S53_CONTINUATION_ACTIVE"'
            )
        ),
        rejected,
    )
    expect_rejection(
        "verifier_total_d4_deletion",
        lambda: validate_canonical_verifier(
            replace_required(verifier, '"D4_ALTERNATING_TOTAL_COMPLEX"', '"OMITTED"')
        ),
        rejected,
    )
    expect_rejection(
        "verifier_total_d4_reactivation",
        lambda: validate_canonical_verifier(
            replace_required(
                verifier,
                '"status": "RETIRED_UNTIL_GLOBAL_INPUTS"',
                '"status": "ACTIVE"',
            )
        ),
        rejected,
    )

    score = copy.deepcopy(ledger)
    score["theorem"]["score"] = "3/9"
    expect_rejection("false_3_of_9", lambda: validate_ledger(score), rejected)

    d4_count = copy.deepcopy(ledger)
    d4_count["canonical_reconciliation"]["d4_accounting"]["survivor_labeled"] -= 1
    expect_rejection("changed_d4_count", lambda: validate_ledger(d4_count), rejected)

    d3_count = copy.deepcopy(ledger)
    d3_count["canonical_reconciliation"]["d3_accounting"]["quotient_classes"] -= 1
    expect_rejection("changed_d3_count", lambda: validate_ledger(d3_count), rejected)

    residue = copy.deepcopy(ledger)
    residue["canonical_reconciliation"]["d3_accounting"]["unresolved_residue"] -= 1
    expect_rejection("changed_d3_residue", lambda: validate_ledger(residue), rejected)

    q3 = copy.deepcopy(ledger)
    q3["canonical_reconciliation"]["first_missing_global_object"]["status"] = "AVAILABLE"
    expect_rejection("promoted_q3", lambda: validate_ledger(q3), rejected)

    target = copy.deepcopy(ledger)
    target["selected_target"] = "fullsupport_master_closure_compiler"
    expect_rejection("active_old_target", lambda: validate_ledger(target), rejected)

    source = copy.deepcopy(ledger)
    first_source = next(iter(source["canonical_reconciliation"]["source_sha256"]))
    source["canonical_reconciliation"]["source_sha256"][first_source] = "0" * 64
    expect_rejection("changed_source_digest", lambda: validate_ledger(source), rejected)

    expect_rejection(
        "unapproved_path",
        lambda: require(not [p for p in paths + ["README.md"] if not is_allowed_path(p)], "path"),
        rejected,
    )
    return rejected


def main() -> int:
    try:
        verify_identity_and_history()
        verify_sources()
        verify_rejection_history()
        status = candidate_bytes(STATUS_PATH).decode("utf-8")
        ledger = json.loads(candidate_bytes(LEDGER_PATH).decode("utf-8"))
        verifier = candidate_bytes(CANONICAL_VERIFIER_PATH).decode("utf-8")
        paths = changed_paths()
        validate_status(status)
        validate_ledger(ledger)
        validate_canonical_verifier(verifier)
        run_candidate_native_verifier()
        run_original_negative_control()
        rejected = run_hostile_canaries(status, ledger, verifier, paths)
        require(len(rejected) == 20, f"hostile rejection count: {len(rejected)}")

        result: dict[str, Any] = {
            "schema": "canonical-reconciliation-repaired-falsifier-v1",
            "reviewed_commit": CANDIDATE,
            "reviewed_tree": CANDIDATE_TREE,
            "verdict": "ACCEPT_REPAIRED_CANONICAL_RECONCILIATION",
            "source_count": len(SOURCE_SHA256),
            "changed_path_count": len(paths),
            "native_candidate_canaries": "PASS_9_OF_9",
            "independent_hostile_rejections": rejected,
            "independent_hostile_rejection_count": len(rejected),
            "original_candidate_gate": "EXPECTED_NONAUTHORITATIVE_REJECT",
            "rejected_head_history": "PRESERVED_AND_ANCESTRAL",
            "theorem_score": "2/9",
            "theorem_delta": "NONE",
            "ledger_change_recommended": "NONE",
        }
        result["semantic_sha256"] = sha256(canonical_bytes(result))
        print(json.dumps(result, sort_keys=True, indent=2))
        return 0
    except (KeyError, OSError, ValueError, VerificationError) as exc:
        print(f"REJECT {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
