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
EXPECTED_SELECTED = 335
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


EXPECTED_HISTORICAL_REPLAYS = {'ops/research-team/cycles/2026-09-02-d3-triple-critical-saturation-component-gate1/verify_closing.py': ('fb667bfe33ef9e945a82e9a23b615e67f5f39c0f',
                                                                                                         '117850b25cd94f865cb85e681c465b8260dd9c6a',
                                                                                                         '9aad6afa23345fc0c239755c9a68cfdac51d9955e9c859d4923caaa548bf415f',
                                                                                                         '9aad6afa23345fc0c239755c9a68cfdac51d9955e9c859d4923caaa548bf415f'),
 'ops/research-team/cycles/2026-09-03-d3-mixed-block-100-universal-carrier-gate1/verify_closing_candidate.py': ('a10a47d1e934e4296b9612ccbde6d0b1a74a88bb',
                                                                                                                'eead48c4263f85cb71b0617213011fe5dcae89bf',
                                                                                                                '0b6565f3cbaad6d269f80d024e4c12adb240101fb4aa558f5663ad3e289201ee',
                                                                                                                '0b6565f3cbaad6d269f80d024e4c12adb240101fb4aa558f5663ad3e289201ee'),
 'ops/research-team/cycles/2026-09-03-d3-mixed-block-100-universal-carrier-gate1/verify_final_closing.py': ('a10a47d1e934e4296b9612ccbde6d0b1a74a88bb',
                                                                                                            'eead48c4263f85cb71b0617213011fe5dcae89bf',
                                                                                                            '995d496296cd854e4e6a388faaf1ef1c68b2b30d62b4a59a230b4b9018df86be',
                                                                                                            'a052179d1b02b67f07691e8d8058c161019b83241acc5f061defc09303250637'),
 'ops/research-team/cycles/2026-09-03-d3-mixed-block-100-universal-carrier-gate1/verify_mid_cycle.py': ('a10a47d1e934e4296b9612ccbde6d0b1a74a88bb',
                                                                                                        'eead48c4263f85cb71b0617213011fe5dcae89bf',
                                                                                                        '136976e4b84c5d227014b03d2e5f4ecced04b26d76ccbe71b77f64d8e1bfa22d',
                                                                                                        '136976e4b84c5d227014b03d2e5f4ecced04b26d76ccbe71b77f64d8e1bfa22d'),
 'ops/research-team/cycles/2026-09-03-d3-mixed-block-100-universal-carrier-gate1/verify_opening_state.py': ('a10a47d1e934e4296b9612ccbde6d0b1a74a88bb',
                                                                                                            'eead48c4263f85cb71b0617213011fe5dcae89bf',
                                                                                                            '064a8c6944b33238abd8555c79a8304269d85755716c7a8aa658ada217dfd760',
                                                                                                            '064a8c6944b33238abd8555c79a8304269d85755716c7a8aa658ada217dfd760'),
 'ops/research-team/cycles/2026-09-04-d3-block-gordan-compact-relative-source-gate1/verify_opening_state.py': ('843eac01cbb0a8c0a84840e286a7a42943bcac9c',
                                                                                                               'adcf9402cb7daf6b1491b05b493f5c44162d75be',
                                                                                                               '09022ae540fcf673dbfeb4e4765c508063f29436f05b5fa83b420787aca8b0a4',
                                                                                                               '09022ae540fcf673dbfeb4e4765c508063f29436f05b5fa83b420787aca8b0a4'),
 'ops/team/d3-mixed-100-carrier-constructor/verify_constructor.py': ('a10a47d1e934e4296b9612ccbde6d0b1a74a88bb',
                                                                     'eead48c4263f85cb71b0617213011fe5dcae89bf',
                                                                     '5cb3cf0ebacf5a40027096e9a1a1c82550f706c31abbbd3c0c4d18bc8a4a2c1c',
                                                                     '5cb3cf0ebacf5a40027096e9a1a1c82550f706c31abbbd3c0c4d18bc8a4a2c1c'),
 'ops/team/d3-mixed-100-carrier-falsifier/verify_falsifier.py': ('a10a47d1e934e4296b9612ccbde6d0b1a74a88bb',
                                                                 'eead48c4263f85cb71b0617213011fe5dcae89bf',
                                                                 '690f735f5efd7c4ffb7ddd666dc76a597ce299363f861a269456a9ec1709ba14',
                                                                 '690f735f5efd7c4ffb7ddd666dc76a597ce299363f861a269456a9ec1709ba14'),
 'ops/team/d3-mixed-100-independent-verifier/verify_independent.py': ('a10a47d1e934e4296b9612ccbde6d0b1a74a88bb',
                                                                      'eead48c4263f85cb71b0617213011fe5dcae89bf',
                                                                      '1f6399d8ad7fe0c893a1919ebb26a43075ed894f7aeb4c739ff6b0f13d7e572a',
                                                                      '1f6399d8ad7fe0c893a1919ebb26a43075ed894f7aeb4c739ff6b0f13d7e572a')}
EXPECTED_VERIFIER_ARGUMENTS = {'ops/team/d3-satinj-referee/verify_frozen_candidates.py': ('--prover-revision',
                                                            '3c3ccbcac95fe05543a870c86da1b2d29342f526',
                                                            '--falsifier-revision',
                                                            '1f8be67c47679d4283edec4b67ba3ae70c1c4818')}

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
    historical_replays = literal_dict(tree, "HISTORICAL_REPLAYS")
    verifier_arguments = literal_dict(tree, "VERIFIER_ARGUMENTS")
    if historical_replays != EXPECTED_HISTORICAL_REPLAYS:
        raise AssertionError("exact historical replay mapping changed")
    if verifier_arguments != EXPECTED_VERIFIER_ARGUMENTS:
        raise AssertionError("exact verifier argument mapping changed")
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

    if not set(historical_replays) <= selected:
        raise AssertionError("historical replay was excluded from selected gates")
    if not set(verifier_arguments) <= selected:
        raise AssertionError("argument-bound verifier was excluded from selected gates")
    if set(historical_replays) & set(verifier_arguments):
        raise AssertionError("ambiguous replay and argument route")
    for path, pins in historical_replays.items():
        if len(pins) != 4 or tuple(map(len, pins)) != (40, 40, 64, 64):
            raise AssertionError("historical replay pin format")
        if any(set(pin) - set("0123456789abcdef") for pin in pins):
            raise AssertionError("historical replay pin alphabet")
        if hashlib.sha256((ROOT / path).read_bytes()).hexdigest() != pins[2]:
            raise AssertionError(f"current historical verifier bytes changed: {path}")
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
