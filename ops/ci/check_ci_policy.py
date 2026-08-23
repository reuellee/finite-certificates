#!/usr/bin/env python3
"""Canary audit for change routing and the final required-check contract."""

from __future__ import annotations

import ast
from pathlib import Path
import re
import sys


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE))

from classify_changes import FORMAT, classify, run_all  # noqa: E402
from check_gate_results import (  # noqa: E402
    ALWAYS_JOBS,
    FLAG_TO_JOB,
    FULL_JOBS,
    FULL_OR_FLAG_TO_JOB,
    audit,
)


WORKFLOW = ROOT / ".github" / "workflows" / "verify.yml"
EXPECTED_FAST_COUNT = 94
EXPECTED_FAST_MANIFEST = "4d03cbec17aaeae99329800c8c14664f5d827a48da5ec18a168956139015bf06"
WORKING_DIRECTORIES = (
    ROOT,
    ROOT / "ai" / "maxout",
    ROOT / "ai" / "maxout" / "capstone",
    ROOT / "ai" / "maxout" / "stage2c2_gpt",
)


def expect(path: str, *enabled: str) -> None:
    plan = classify((path,), "pull_request")
    assert plan["format"] == FORMAT
    expected = set(enabled)
    keys = {
        "proof_change",
        "maxout",
        "diag2_atlas",
        "labeled_pairs",
        "source_block_labels",
        "parent860",
    }
    actual = {key for key in keys if plan[key]}
    assert actual == expected, (path, expected, actual)


def classifier_canaries() -> None:
    expect("README.md")
    expect(".github/workflows/verify.yml")
    expect("ai/maxout/capstone/certificates.json", "proof_change", "maxout")
    expect(
        "ai/omreal/verify_diag2_escape_set_atlas178.py",
        "proof_change",
        "diag2_atlas",
    )
    expect(
        "ai/omreal/DIAG9_GRAPH_exact_topes.py",
        "proof_change",
        "diag2_atlas",
        "parent860",
    )
    expect(
        "ai/omreal/data/DIAG2_PIVOT_pair_classification.npz",
        "proof_change",
        "labeled_pairs",
    )
    expect(
        "ai/omreal/diag3_pair_parent_source_block_labels_core.py",
        "proof_change",
        "source_block_labels",
    )
    expect(
        "ai/omreal/data/DIAG9_GRAPH_parent860_star_repair.npz",
        "proof_change",
        "parent860",
    )
    expect("ai/maxout/stage2c2_gpt/audit_run.log")
    expect("ai/omgamma/data/big_4_9/level_000.npz")
    shared = classify(("ai/omreal/four_chart_gate.py",), "pull_request")
    assert shared["diag2_atlas"] is True and shared["slow_changed"] is True
    assert "ai/omreal/verify_diag2_canonical_robust_edges.py" in shared["slow_verifiers"]
    assert "ai/omreal/verify_diag2_escape_set_atlas178.py" not in shared["slow_verifiers"]
    full = classify((), "schedule")
    assert full["full"] is True and full["proof_change"] is False

    fast, _ = run_all.selected(run_all.discover(), fast=True, ci_delegated=True)
    manifest = run_all.shard_manifest(run_all.shard_partition(fast, 1))
    assert len(fast) == EXPECTED_FAST_COUNT
    assert manifest["partition_sha256"] == EXPECTED_FAST_MANIFEST


def workflow_contract() -> None:
    source = WORKFLOW.read_text(encoding="utf-8")
    required_fragments = (
        "pull_request:",
        "workflow_dispatch:",
        "schedule:",
        "permissions:\n  contents: read",
        "name: verifier suite (complete)",
        "if: always()",
        "python ops/ci/check_gate_results.py",
        "python ops/ci/check_ci_policy.py",
        "--fast --ci-delegated",
        "PYTHONDONTWRITEBYTECODE=1 python -u run_all.py",
        "--ci-delegated --shard ${{ matrix.shard }}/4",
    )
    for fragment in required_fragments:
        assert fragment in source, f"workflow contract missing {fragment!r}"
    assert re.search(r"(?m)^\s*pull_request_target\s*:", source) is None

    # Every embedded Python heredoc-free script reference must exist.  This
    # catches path typos without needing a third-party YAML package.
    for token in source.replace("\n", " ").split():
        if token.endswith(".py") and "${{" not in token:
            relative = token.strip("'\"()")
            candidates = tuple(directory / relative for directory in WORKING_DIRECTORIES)
            assert any(candidate.is_file() for candidate in candidates), (
                f"workflow references missing script: {token}"
            )

    ast.parse((HERE / "classify_changes.py").read_text(encoding="utf-8"))
    ast.parse((HERE / "run_changed_slow_verifiers.py").read_text(encoding="utf-8"))
    ast.parse((HERE / "check_gate_results.py").read_text(encoding="utf-8"))


def final_gate_canaries() -> None:
    optional = tuple(FLAG_TO_JOB.values()) + tuple(FULL_OR_FLAG_TO_JOB.values()) + FULL_JOBS

    def results(*successful: str) -> dict[str, dict[str, str]]:
        passed = set(successful) | set(ALWAYS_JOBS)
        return {
            job: {"result": "success" if job in passed else "skipped"}
            for job in tuple(ALWAYS_JOBS) + optional
        }

    docs = classify(("README.md",), "pull_request")
    assert audit(docs, results()) == []

    maxout = classify(("ai/maxout/capstone/certificates.json",), "pull_request")
    expected = ("fast-suite", "maxout-capstone")
    assert audit(maxout, results(*expected)) == []
    assert audit(maxout, results("fast-suite")), "must reject a skipped capstone audit"

    full = classify((), "workflow_dispatch")
    full_jobs = tuple(FULL_OR_FLAG_TO_JOB.values()) + FULL_JOBS
    assert audit(full, results(*full_jobs)) == []


def main() -> int:
    classifier_canaries()
    workflow_contract()
    final_gate_canaries()
    print("PASS CI routing canaries and stable final-gate contract")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
