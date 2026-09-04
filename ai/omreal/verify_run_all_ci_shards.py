#!/usr/bin/env python3
"""Independent union/disjointness audit for deterministic CI verifier shards."""

from __future__ import annotations

import ast
import hashlib
import json
from pathlib import Path
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[2]
RUN_ALL = ROOT / "run_all.py"
COUNTS = (1, 2, 4, 7, 8)
EXPECTED_SELECTED = 316
EXPECTED_CI_DELEGATED_PATHS = {
    "ai/omreal/verify_diag2_escape_set_atlas178.py",
    "ai/omreal/verify_diag3_ordered_root_atlas178.py",
    "ai/omreal/verify_diag3_pair_parent_source_EDGE39_0_113.py",
    "ai/omreal/verify_diag3_pair_parent_source_block_labels.py",
}
EXPECTED_EXTERNAL_PATHS = {
    "ai/omreal/verify_diag3_triple_common_scaling_no_go.py",
}
EXPECTED_ARCHIVAL_PATHS = {
    "ai/omreal/verify_canonical_research_state_v2.py",
    "ai/omreal/verify_canonical_research_state_v3.py",
    "ops/research-team/cycles/2026-09-01-d9-component-roadmap/verify_opening_audit.py",
    "ops/research-team/cycles/2026-09-01-d9-row2599-factor19069-critical-equidim-gate1/verify_opening_audit.py",
    "ops/research-team/cycles/2026-09-01-d9-row2599-factor19069-explicit-trihom-jacobian-chart-gate1/verify_opening_audit.py",
    "ops/research-team/cycles/2026-09-01-d9-row2599-factor19069-homogenizer-boundary-type-stratification-gate1/verify_opening_audit.py",
    "ops/research-team/cycles/2026-09-01-d9-row2599-factor19069-singular-df-multihomogeneous-gate1/verify_opening_audit.py",
    "ops/research-team/cycles/2026-09-01-d9-universal-cut/verify_closing_candidate.py",
    "ops/research-team/cycles/2026-09-01-d9-universal-cut/verify_opening_audit.py",
    "ops/research-team/cycles/2026-09-01-diag9-s1237-normal-link/verify_cycle_report.py",
    "ops/research-team/cycles/2026-09-01-diag9-s1237-normal-link/verify_opening_audit.py",
    "ops/team/canonical-reconciliation-falsifier/verify_canonical_reconciliation_falsifier.py",
    "ops/team/canonical-reconciliation-falsifier/verify_repaired_candidate_semantics.py",
    "ops/team/canonical-reconciliation-referee/verify_closing_referee.py",
    "ops/team/canonical-reconciliation-referee/verify_final_closing_referee.py",
    "ops/team/d3-mixed-carrier-referee/verify_referee.py",
    "ops/team/d9-factor19069-homogenizer-boundary-falsifier/verify_homogenizer_boundary_falsifier.py",
    "ops/team/diag9-s1237-normal-link-referee/verify_closing_referee.py",
}
EXPECTED_ARCHIVAL_REPLACEMENTS = {
    "ai/omreal/verify_canonical_research_state_v2.py": (
        "ops/team/canonical-reconciliation-portable/verify_canonical_reconciliation_portable.py",
        "ops/research-team/cycles/2026-08-31-diag8-mask6-cegar/verify_diag8_mask6_cycle_manifest.py",
    ),
    "ai/omreal/verify_canonical_research_state_v3.py": (
        "ops/team/d9-universal-cut-certificate/verify_portable_predecessor.py",
    ),
    "ops/research-team/cycles/2026-09-01-d9-component-roadmap/verify_opening_audit.py": (
        "ops/team/d9-component-roadmap-certificate/verify_roadmap_canary_contract.py",
    ),
    "ops/research-team/cycles/2026-09-01-d9-row2599-factor19069-critical-equidim-gate1/verify_opening_audit.py": (
        "ops/team/d9-factor19069-critical-equidim-certificate/verify_critical_equidim_certificate.py",
    ),
    "ops/research-team/cycles/2026-09-01-d9-row2599-factor19069-explicit-trihom-jacobian-chart-gate1/verify_opening_audit.py": (
        "ops/team/d9-factor19069-explicit-trihom-jacobian-chart-certificate/verify_projective_chart_certificate.py",
        "ops/team/d9-factor19069-explicit-trihom-jacobian-chart-referee/verify_closing_referee.py",
    ),
    "ops/research-team/cycles/2026-09-01-d9-row2599-factor19069-homogenizer-boundary-type-stratification-gate1/verify_opening_audit.py": (
        "ops/team/d9-factor19069-homogenizer-boundary-certificate/verify_homogenizer_boundary_certificate.py",
        "ops/team/d9-factor19069-homogenizer-boundary-referee/verify_closing_referee.py",
    ),
    "ops/research-team/cycles/2026-09-01-d9-row2599-factor19069-singular-df-multihomogeneous-gate1/verify_opening_audit.py": (
        "ops/team/d9-factor19069-singular-df-multihomogeneous-certificate/verify_singular_df_certificate.py",
        "ops/team/d9-factor19069-singular-df-multihomogeneous-referee/verify_closing_referee.py",
    ),
    "ops/research-team/cycles/2026-09-01-d9-universal-cut/verify_closing_candidate.py": (
        "ops/team/d9-universal-cut-certificate/verify_universal_cut_certificate.py",
        "ops/team/d9-universal-cut-referee/verify_closing_referee.py",
    ),
    "ops/research-team/cycles/2026-09-01-d9-universal-cut/verify_opening_audit.py": (
        "ops/team/d9-universal-cut-certificate/verify_universal_cut_certificate.py",
        "ops/team/d9-universal-cut-referee/verify_closing_referee.py",
    ),
    "ops/research-team/cycles/2026-09-01-diag9-s1237-normal-link/verify_cycle_report.py": (
        "ops/team/d9-universal-cut-certificate/verify_portable_predecessor.py",
    ),
    "ops/research-team/cycles/2026-09-01-diag9-s1237-normal-link/verify_opening_audit.py": (
        "ops/team/d9-universal-cut-certificate/verify_portable_predecessor.py",
    ),
    "ops/team/canonical-reconciliation-falsifier/verify_canonical_reconciliation_falsifier.py": (
        "ops/team/canonical-reconciliation-portable/verify_canonical_reconciliation_portable.py",
    ),
    "ops/team/canonical-reconciliation-falsifier/verify_repaired_candidate_semantics.py": (
        "ops/team/canonical-reconciliation-portable/verify_canonical_reconciliation_portable.py",
    ),
    "ops/team/canonical-reconciliation-referee/verify_closing_referee.py": (
        "ops/team/canonical-reconciliation-portable/verify_canonical_reconciliation_portable.py",
    ),
    "ops/team/canonical-reconciliation-referee/verify_final_closing_referee.py": (
        "ops/team/canonical-reconciliation-portable/verify_canonical_reconciliation_portable.py",
    ),
    "ops/team/d3-mixed-carrier-referee/verify_referee.py": (
        "ai/omreal/verify_canonical_research_state_v9.py",
    ),
    "ops/team/d9-factor19069-homogenizer-boundary-falsifier/verify_homogenizer_boundary_falsifier.py": (
        "ops/team/d9-factor19069-homogenizer-boundary-certificate/verify_homogenizer_boundary_certificate.py",
        "ops/team/d9-factor19069-homogenizer-boundary-referee/verify_closing_referee.py",
    ),
    "ops/team/diag9-s1237-normal-link-referee/verify_closing_referee.py": (
        "ops/team/d9-universal-cut-certificate/verify_portable_predecessor.py",
    ),
}


def literal_set(tree, name):
    for node in tree.body:
        if isinstance(node, ast.Assign):
            if any(isinstance(target, ast.Name) and target.id == name for target in node.targets):
                return set(ast.literal_eval(node.value))
    raise AssertionError(f"missing literal set {name}")


def literal_dict(tree, name):
    for node in tree.body:
        if isinstance(node, ast.Assign):
            if any(isinstance(target, ast.Name) and target.id == name for target in node.targets):
                return dict(ast.literal_eval(node.value))
    raise AssertionError(f"missing literal dict {name}")


def direct_selected():
    tree = ast.parse(RUN_ALL.read_text(encoding="utf-8"))
    delegated_names = literal_set(tree, "CI_DELEGATED")
    external_reasons = literal_dict(tree, "EXTERNAL_INPUT")
    archival_reasons = literal_dict(tree, "ARCHIVAL_INPUT")
    replacements = {
        path: tuple(values)
        for path, values in literal_dict(tree, "ARCHIVAL_REPLACEMENTS").items()
    }
    discovered = {
        path.relative_to(ROOT).as_posix()
        for path in ROOT.rglob("verify_*.py")
        if path.is_file()
    }
    delegated = {path for path in discovered if Path(path).name in delegated_names}
    external = {path for path in discovered if Path(path).name in external_reasons}
    archival = set(archival_reasons)

    if delegated != EXPECTED_CI_DELEGATED_PATHS:
        raise AssertionError("exact delegated verifier set changed")
    if external != EXPECTED_EXTERNAL_PATHS:
        raise AssertionError("exact external-input verifier set changed")
    if archival != EXPECTED_ARCHIVAL_PATHS:
        raise AssertionError("exact archival verifier set changed")
    if replacements != EXPECTED_ARCHIVAL_REPLACEMENTS:
        raise AssertionError("exact archival replacement mapping changed")
    if set(replacements) != archival:
        raise AssertionError("archival replacement domain is not exact")
    if delegated_names != {Path(path).name for path in EXPECTED_CI_DELEGATED_PATHS}:
        raise AssertionError("delegated basename declaration changed")
    if set(external_reasons) != {Path(path).name for path in EXPECTED_EXTERNAL_PATHS}:
        raise AssertionError("external-input basename declaration changed")
    if any(not isinstance(reason, str) or not reason.strip() for reason in external_reasons.values()):
        raise AssertionError("empty external-input reason")
    if any(not isinstance(reason, str) or not reason.strip() for reason in archival_reasons.values()):
        raise AssertionError("empty archival reason")

    exclusion_sets = (delegated, external, archival)
    for index, left in enumerate(exclusion_sets):
        for right in exclusion_sets[index + 1:]:
            if left & right:
                raise AssertionError("verifier exclusion sets are not pairwise disjoint")
    exclusions = delegated | external | archival
    if not exclusions <= discovered:
        raise AssertionError("declared exclusion is not discovered")
    selected = discovered - exclusions
    if len(selected) != EXPECTED_SELECTED:
        raise AssertionError("selected verifier census changed")
    if discovered - selected != exclusions:
        raise AssertionError("selected universe is not discovered minus exclusions")

    for historical, gates in replacements.items():
        if historical not in archival or not gates:
            raise AssertionError("invalid archival replacement entry")
        for gate in gates:
            if gate not in discovered:
                raise AssertionError(f"archival replacement is not discovered: {gate}")
            if gate not in selected:
                raise AssertionError(f"archival replacement is not selected: {gate}")
    return discovered, selected, delegated, external, archival, replacements


def manifest(count):
    command = [
        sys.executable,
        str(RUN_ALL),
        "--ci-delegated",
        "--list-shards",
        str(count),
        "--json",
    ]
    first = subprocess.check_output(command, cwd=ROOT, text=True)
    second = subprocess.check_output(command, cwd=ROOT, text=True)
    if first != second:
        raise AssertionError("shard manifest is nondeterministic")
    return json.loads(first)


def audit(payload, expected, count):
    if payload["format"] != "finite-certificates-verifier-shards-v1":
        raise AssertionError("wrong shard manifest format")
    if payload["shard_count"] != count or len(payload["shards"]) != count:
        raise AssertionError("wrong shard count")
    flat = [path for bucket in payload["shards"] for path in bucket]
    if len(flat) != len(set(flat)):
        raise AssertionError("verifier occurs in more than one shard")
    if set(flat) != expected:
        raise AssertionError("shard union does not equal selected verifier universe")
    if payload["selected_verifier_count"] != len(expected):
        raise AssertionError("selected verifier count changed")
    if any(bucket != sorted(bucket) for bucket in payload["shards"]):
        raise AssertionError("shard paths are not canonical")
    canonical = "".join(
        f"{index}\0{path}\n"
        for index, bucket in enumerate(payload["shards"])
        for path in bucket
    ).encode("utf-8")
    if hashlib.sha256(canonical).hexdigest() != payload["partition_sha256"]:
        raise AssertionError("partition digest mismatch")


def main():
    discovered, selected, delegated, external, archival, replacements = direct_selected()
    if len(delegated) != 4 or len(external) != 1 or len(archival) != 18:
        raise AssertionError("nonsharded verifier census changed")
    digests = {}
    for count in COUNTS:
        payload = manifest(count)
        audit(payload, selected, count)
        digests[str(count)] = payload["partition_sha256"]
    print("PASS deterministic shard manifests", digests)
    print("PASS exact union/disjointness", len(selected), "selected verifiers")
    print("PASS delegated verifier census", len(delegated))
    print("PASS explicit external-input verifier census", len(external))
    print("PASS archival verifier census", len(archival))
    print("PASS archival replacement coverage", len(replacements))


if __name__ == "__main__":
    main()
