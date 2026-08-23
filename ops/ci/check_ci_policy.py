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

from classify_changes import (  # noqa: E402
    FORMAT,
    SLOW_INPUT_DEPENDENCIES,
    SPECIAL_VERIFIERS,
    classify,
    run_all,
)
from check_gate_results import (  # noqa: E402
    ALWAYS_JOBS,
    EXHAUSTIVE_JOBS,
    FLAG_TO_JOB,
    FULL_EXHAUSTIVE_OR_FLAG_TO_JOB,
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
        "exhaustive",
        "external_changed",
        "maxout",
        "diag2_atlas",
        "labeled_pairs",
        "source_block_labels",
        "parent860",
    }
    actual = {key for key in keys if plan[key]}
    assert actual == expected, (path, expected, actual)


def classifier_canaries() -> None:
    for proof_input, verifiers in SLOW_INPUT_DEPENDENCIES.items():
        assert (ROOT / proof_input).is_file(), proof_input
        assert verifiers, proof_input
        for verifier in verifiers:
            target = ROOT / verifier
            assert target.is_file(), (proof_input, verifier)
            assert target.name in run_all.SLOW, (proof_input, verifier)
            assert target.name not in SPECIAL_VERIFIERS, (proof_input, verifier)

    expect("README.md")
    expect(".github/workflows/verify.yml")
    expect("ai/maxout/capstone/certificates.json", "proof_change", "maxout")
    expect("ai/maxout/stage2c2_gpt/gp_degree3_results.json.gz", "proof_change", "maxout")
    expect("ai/omreal/data/unmapped_certificate.bin", "proof_change", "exhaustive")
    expect("ai/omreal/data/unmapped_certificate.tsv", "proof_change", "exhaustive")
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
        "exhaustive",
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
        "exhaustive",
        "parent860",
    )
    deleted = classify(("ai/omreal/data/deleted_then_ignored.json",), "pull_request")
    assert deleted["proof_change"] is True and deleted["exhaustive"] is True
    deleted_slow = classify(
        ("ai/omreal/verify_diag3_pair_source_square_coverage.py",),
        "pull_request",
    )
    assert "ai/omreal/verify_diag3_pair_source_square_coverage.py" in deleted_slow["slow_verifiers"]

    minimal = classify(("ai/omminor/data/minimal_sweep.txt",), "pull_request")
    assert minimal["slow_changed"] is True
    assert "ai/omminor/verify_minimal.py" in minimal["slow_verifiers"]
    fold = classify(
        ("ai/omreal/data/DIAG3_triple_fold_boundary_chain.json",),
        "pull_request",
    )
    assert "ai/omreal/verify_diag3_triple_concurrence_local_fold_cell.py" in fold["slow_verifiers"]
    plane = classify(
        ("ai/omreal/data/DIAG9_GRAPH_parent860_plane_projection_frontier.json",),
        "pull_request",
    )
    assert plane["parent860"] is True and plane["slow_changed"] is True
    assert "ai/omreal/verify_diag9_parent860_plane_projection.py" in plane["slow_verifiers"]
    druzkowski = classify(("jacobian/druzkowski_map.py",), "pull_request")
    assert druzkowski["slow_changed"] is True
    assert "jacobian/verify_druzkowski.py" in druzkowski["slow_verifiers"]
    cubic = classify(("jacobian/cubic_map.py",), "pull_request")
    assert cubic["slow_changed"] is True
    assert "jacobian/verify_druzkowski.py" in cubic["slow_verifiers"]
    deg3 = classify(("jacobian/deg3_map.py",), "pull_request")
    assert deg3["proof_change"] is True and deg3["slow_changed"] is False

    for validator in (
        ROOT / "jacobian" / "verify_deg3_keller.py",
        ROOT / "jacobian" / "verify_cubic_homogeneous.py",
        ROOT / "jacobian" / "verify_druzkowski.py",
    ):
        source = validator.read_text(encoding="utf-8")
        assert "--regenerate-artifact" in source, validator
        assert "committed artifact matches exact reconstruction" in source, validator

    catalog = classify(("ai/omreal/certs_4_8.jsonl",), "pull_request")
    assert catalog["proof_change"] is True and catalog["slow_changed"] is True
    assert "ai/omreal/verify_diag9_parent_ranking.py" in catalog["slow_verifiers"]
    external = classify(
        ("ai/omreal/verify_diag3_triple_common_scaling_no_go.py",),
        "pull_request",
    )
    assert external["proof_change"] is True and external["external_changed"] is True
    shared = classify(("ai/omreal/four_chart_gate.py",), "pull_request")
    assert shared["diag2_atlas"] is True and shared["slow_changed"] is True
    assert "ai/omreal/verify_diag2_canonical_robust_edges.py" in shared["slow_verifiers"]
    assert "ai/omreal/verify_diag2_escape_set_atlas178.py" not in shared["slow_verifiers"]
    bfp = classify(("ai/omreal/bfp.py",), "pull_request")
    assert "ai/omminor/verify_minimal.py" in bfp["slow_verifiers"]
    rur = classify(
        ("ai/omreal/data/DIAG3_concurrence_ramification_rur.py",),
        "pull_request",
    )
    assert "ai/omreal/verify_diag3_triple_concurrence_local_fold_cell.py" in rur["slow_verifiers"]
    minorlib = classify(("ai/omminor/minorlib.py",), "pull_request")
    assert "ai/omminor/verify_minimal.py" in minorlib["slow_verifiers"]
    assert "ai/omreal/verify_four_chart_obstruction.py" in minorlib["slow_verifiers"]
    delegated = classify(
        ("ai/omreal/verify_diag2_pivot_all_pair_fibers.py",),
        "pull_request",
    )
    assert delegated["labeled_pairs"] is True
    assert "ai/omreal/verify_diag2_pivot_all_pair_fibers.py" not in delegated["slow_verifiers"]
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
        "python ops/ci/reject_external_verifier_change.py",
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
    classifier_source = (HERE / "classify_changes.py").read_text(encoding="utf-8")
    assert '"--no-renames"' in classifier_source


def final_gate_canaries() -> None:
    optional = (
        tuple(FLAG_TO_JOB.values())
        + tuple(FULL_OR_FLAG_TO_JOB.values())
        + tuple(FULL_EXHAUSTIVE_OR_FLAG_TO_JOB.values())
        + EXHAUSTIVE_JOBS
        + FULL_JOBS
    )

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

    unknown = classify(("ai/omreal/data/unmapped_certificate.bin",), "pull_request")
    fallback_jobs = (
        "fast-suite",
        "suite-shards",
        *FULL_EXHAUSTIVE_OR_FLAG_TO_JOB.values(),
    )
    assert audit(unknown, results(*fallback_jobs)) == []
    assert audit(unknown, results("fast-suite")), "must reject skipped exhaustive fallback"

    full = classify((), "workflow_dispatch")
    full_jobs = (
        tuple(FULL_OR_FLAG_TO_JOB.values())
        + tuple(FULL_EXHAUSTIVE_OR_FLAG_TO_JOB.values())
        + EXHAUSTIVE_JOBS
        + FULL_JOBS
    )
    assert audit(full, results(*full_jobs)) == []


def main() -> int:
    classifier_canaries()
    workflow_contract()
    final_gate_canaries()
    print("PASS CI routing canaries and stable final-gate contract")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
