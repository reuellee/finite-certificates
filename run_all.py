#!/usr/bin/env python3
"""Run every self-contained verify_*.py in the tree; exit nonzero if any fails.

--fast skips the slow verifiers, including the expensive diagonal-two
atlases, canonical-edge, mutation-square, separator, and saturation replays.

--ci-delegated additionally skips verifiers that the required GitHub workflow
runs in their own jobs.  Verifiers that deliberately require a regenerable
external artifact are always reported and skipped; invoke those directly with
the pinned argument documented in their proof note.  Historical or checkout-
context-bound verifiers are reported and skipped by exact repository path.
Every such exclusion has one or more selected branch-neutral replacement gates
declared in ``ARCHIVAL_REPLACEMENTS``; current successors remain live.
``--shard INDEX/COUNT`` deterministically partitions the selected verifier
universe.  The unsharded command remains exhaustive.  ``--list-shards COUNT``
emits the exact partition without running verifiers so CI can independently
audit union and disjointness before starting expensive jobs.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import time

SLOW = {
    "verify_diag2_canonical_robust_edges.py",
    "verify_diag2_escape_minimal_separators.py",
    "verify_diag2_near_counterexample_atlas.py",
    "verify_diag2_near_counterexample_separators.py",
    "verify_diag2_singleton_four_obstruction.py",
    "verify_diag2_escape_set_atlas178.py",
    "verify_diag2_escape_set_mutation_square.py",
    "verify_diag2_extremal_coordinate_survey.py",
    "verify_diag2_extremal_line_transition_census.py",
    "verify_diag2_extremal_safe_loss_edge.py",
    "verify_diag2_extremal_transition_disk_geometry.py",
    "verify_diag2_extremal_transition_disk_seeds.py",
    "verify_diag2_extremal_undominated_birth_edge.py",
    "verify_diag2_generic_birth_pattern_reduction.py",
    "verify_diag2_generic_birth_exchange_repair.py",
    "verify_diag2_generic_birth_circuit_exchange.py",
    "verify_diag2_generic_birth_type51_exchange_repair.py",
    "verify_diag2_pivot_49_50_pair_saturation.py",
    "verify_diag2_robust_mutation_squares.py",
    "verify_diag3_ordered_root_atlas178.py",
    "verify_diag3_all_pair_affine_compression.py",
    "verify_diag3_component_cosheaf_pilot.py",
    "verify_diag3_pair_factor_root_switch.py",
    "verify_diag3_pair_global_atlas_schema.py",
    "verify_diag3_pair_fullsupport_parent_product_signs.py",
    "verify_diag3_pair_fullsupport_component_collar.py",
    "verify_diag3_pair_fullsupport_labeled_skeleton.py",
    "verify_diag3_pair_parent_source_EDGE39_0_113.py",
    "verify_diag3_pair_fullsupport_segment_cover.py",
    "verify_diag3_pair_residual_wall_adjacency.py",
    "verify_diag3_pair_source_staircase8_coverage.py",
    "verify_diag3_pair_source_staircase_coverage.py",
    "verify_diag3_pair_atlas_tangential_fill.py",
    "verify_diag3_pair_tangential_frontier.py",
    "verify_diag3_polynomial_multivector_height_screen.py",
    "verify_diag3_projective_column_fiber_scan.py",
    "verify_diag3_triple_direct_final_affinity.py",
    "verify_diag3_triple_primitive_final_direction.py",
    "verify_diag3_triple_primitive_final_support3.py",
    "verify_diag3_triple_gale_canary_no_go.py",
    "verify_diag8_mask6_barycentric_fan.py",
    "verify_druzkowski.py",
    "verify_sae_circuit.py",
}
CI_DELEGATED = {
    "verify_diag2_escape_set_atlas178.py",
    "verify_diag3_ordered_root_atlas178.py",
    "verify_diag3_pair_parent_source_block_labels.py",
    "verify_diag3_pair_parent_source_EDGE39_0_113.py",
}
EXTERNAL_INPUT = {
    "verify_diag3_triple_common_scaling_no_go.py": (
        "requires pinned 6,973,816-byte final-residue argument; "
        "direct replay documented in DIAG3_TRIPLE_COMMON_SCALING_NO_GO.md"
    ),
}
ARCHIVAL_INPUT = {
    "ai/omreal/verify_canonical_research_state_v2.py": (
        "historical post-mask-6 checkpoint is current-authority-context-bound; "
        "selected portable reconciliation and mask-6 gates replace its replay"
    ),
    "ai/omreal/verify_canonical_research_state_v3.py": (
        "historical post-normal-link checkpoint depends on checkout-local history; "
        "the selected portable predecessor gate replaces its replay"
    ),
    "ops/research-team/cycles/2026-09-01-d9-component-roadmap/verify_opening_audit.py": (
        "historical opening audit pins a superseded governance worktree; "
        "the selected branch-neutral roadmap certificate replaces it"
    ),
    "ops/research-team/cycles/2026-09-01-d9-row2599-factor19069-critical-equidim-gate1/verify_opening_audit.py": (
        "historical factor-19069 opening audit requires its exact lane branch; "
        "the selected branch-neutral critical-equidimension certificate replaces it"
    ),
    "ops/research-team/cycles/2026-09-01-d9-row2599-factor19069-explicit-trihom-jacobian-chart-gate1/verify_opening_audit.py": (
        "historical factor-19069 opening audit requires its exact lane branch; "
        "selected branch-neutral certificate and referee gates replace it"
    ),
    "ops/research-team/cycles/2026-09-01-d9-row2599-factor19069-homogenizer-boundary-type-stratification-gate1/verify_opening_audit.py": (
        "historical factor-19069 opening audit requires its exact lane branch; "
        "selected branch-neutral certificate and referee gates replace it"
    ),
    "ops/research-team/cycles/2026-09-01-d9-row2599-factor19069-singular-df-multihomogeneous-gate1/verify_opening_audit.py": (
        "historical factor-19069 opening audit requires its exact lane branch; "
        "selected branch-neutral certificate and referee gates replace it"
    ),
    "ops/research-team/cycles/2026-09-01-d9-universal-cut/verify_closing_candidate.py": (
        "historical cycle wrapper replays a superseded opening worktree; "
        "selected universal-cut certificate and referee gates replace it"
    ),
    "ops/research-team/cycles/2026-09-01-d9-universal-cut/verify_opening_audit.py": (
        "historical opening audit pins a superseded governance worktree; "
        "selected universal-cut certificate and referee gates replace it"
    ),
    "ops/research-team/cycles/2026-09-01-diag9-s1237-normal-link/verify_cycle_report.py": (
        "historical cycle report pins superseded authority prose; "
        "the selected portable predecessor gate replaces it"
    ),
    "ops/research-team/cycles/2026-09-01-diag9-s1237-normal-link/verify_opening_audit.py": (
        "historical opening audit pins a superseded governance worktree; "
        "the selected portable predecessor gate replaces it"
    ),
    "ops/team/canonical-reconciliation-falsifier/verify_canonical_reconciliation_falsifier.py": (
        "archival PR45 audit is covered by the explicit pinned-bundle final-closing replay; "
        "current successor state is governed separately"
    ),
    "ops/team/canonical-reconciliation-falsifier/verify_repaired_candidate_semantics.py": (
        "archival PR45 audit is covered by the explicit pinned-bundle final-closing replay; "
        "current successor state is governed separately"
    ),
    "ops/team/canonical-reconciliation-referee/verify_closing_referee.py": (
        "archival PR45 audit is covered by the explicit pinned-bundle final-closing replay; "
        "current successor state is governed separately"
    ),
    "ops/team/canonical-reconciliation-referee/verify_final_closing_referee.py": (
        "archival PR45 audit is replayed explicitly from the pinned evidence bundle; "
        "current successor state is governed separately"
    ),
    "ops/team/d3-mixed-carrier-referee/verify_referee.py": (
        "historical referee requires its exact lane branch and mutable lane head; "
        "the selected canonical V9 gate replaces it from frozen evidence"
    ),
    "ops/team/d9-factor19069-homogenizer-boundary-falsifier/verify_homogenizer_boundary_falsifier.py": (
        "historical falsifier requires its exact lane branch; selected branch-neutral "
        "homogenizer-boundary certificate and referee gates replace it"
    ),
    "ops/team/diag9-s1237-normal-link-referee/verify_closing_referee.py": (
        "historical referee replays checkout-bound opening and worktree state; "
        "the selected portable predecessor gate replaces it"
    ),
}
ARCHIVAL_REPLACEMENTS = {
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
ROOT = Path(__file__).resolve().parent
TIMEOUT_SECONDS = 1_200


def parser() -> argparse.ArgumentParser:
    answer = argparse.ArgumentParser(description=__doc__)
    answer.add_argument("--fast", action="store_true")
    answer.add_argument("--ci-delegated", action="store_true")
    answer.add_argument(
        "--shard",
        metavar="INDEX/COUNT",
        help="run one zero-based deterministic shard",
    )
    answer.add_argument(
        "--list-shards",
        type=int,
        metavar="COUNT",
        help="emit the deterministic selected-universe partition and exit",
    )
    answer.add_argument("--json", action="store_true", help="JSON shard listing")
    return answer


def discover() -> tuple[Path, ...]:
    return tuple(
        sorted(
            path
            for path in ROOT.rglob("verify_*.py")
            if path.is_file()
        )
    )


def selected(paths, *, fast: bool, ci_delegated: bool):
    chosen = []
    skipped = []
    for path in paths:
        reason = None
        relative = path.relative_to(ROOT).as_posix()
        if relative in ARCHIVAL_INPUT:
            reason = ARCHIVAL_INPUT[relative]
        elif path.name in EXTERNAL_INPUT:
            reason = EXTERNAL_INPUT[path.name]
        elif fast and path.name in SLOW:
            reason = "--fast"
        elif ci_delegated and path.name in CI_DELEGATED:
            reason = "--ci-delegated; separate required CI job"
        if reason is None:
            chosen.append(path)
        else:
            skipped.append((path, reason))
    return tuple(chosen), tuple(skipped)


def shard_partition(paths: tuple[Path, ...], count: int) -> tuple[tuple[Path, ...], ...]:
    if count < 1:
        raise ValueError("shard count must be positive")
    # Greedy longest-processing-time scheduling with a deliberately coarse,
    # repository-pinned cost class.  This balances known slow replays without
    # making correctness depend on unstable wall-clock timing.
    buckets: list[list[Path]] = [[] for _ in range(count)]
    loads = [0] * count
    ordered = sorted(
        paths,
        key=lambda path: (-(20 if path.name in SLOW else 1), path.relative_to(ROOT).as_posix()),
    )
    for path in ordered:
        index = min(range(count), key=lambda item: (loads[item], item))
        buckets[index].append(path)
        loads[index] += 20 if path.name in SLOW else 1
    return tuple(tuple(sorted(bucket)) for bucket in buckets)


def shard_manifest(partition):
    shards = [
        [path.relative_to(ROOT).as_posix() for path in bucket]
        for bucket in partition
    ]
    canonical = "".join(
        f"{index}\0{path}\n"
        for index, bucket in enumerate(shards)
        for path in bucket
    ).encode("utf-8")
    return {
        "format": "finite-certificates-verifier-shards-v1",
        "shard_count": len(shards),
        "selected_verifier_count": sum(map(len, shards)),
        "partition_sha256": hashlib.sha256(canonical).hexdigest(),
        "shards": shards,
    }


def parse_shard(value: str) -> tuple[int, int]:
    try:
        left, right = value.split("/", 1)
        index, count = int(left), int(right)
    except (AttributeError, TypeError, ValueError) as error:
        raise ValueError("--shard must have form INDEX/COUNT") from error
    if count < 1 or not 0 <= index < count:
        raise ValueError("shard index must satisfy 0 <= INDEX < COUNT")
    return index, count


def main() -> int:
    arguments = parser().parse_args()
    paths, skipped = selected(
        discover(), fast=arguments.fast, ci_delegated=arguments.ci_delegated
    )
    if arguments.list_shards is not None:
        manifest = shard_manifest(shard_partition(paths, arguments.list_shards))
        if arguments.json:
            print(json.dumps(manifest, sort_keys=True, separators=(",", ":")))
        else:
            print("SHARD_MANIFEST", manifest["partition_sha256"])
            for index, bucket in enumerate(manifest["shards"]):
                print(f"SHARD {index}/{manifest['shard_count']} {len(bucket)}")
                for path in bucket:
                    print(" ", path)
        return 0

    if arguments.json:
        parser().error("--json requires --list-shards")
    if arguments.shard:
        try:
            index, count = parse_shard(arguments.shard)
        except ValueError as error:
            parser().error(str(error))
        partition = shard_partition(paths, count)
        paths = partition[index]
        manifest = shard_manifest(partition)
        print(
            f"SHARD {index}/{count} {len(paths)} verifiers; "
            f"manifest {manifest['partition_sha256']}",
            flush=True,
        )
    for path, reason in skipped:
        print(f"SKIP  {path.relative_to(ROOT)} ({reason})", flush=True)

    fails = []
    started = time.monotonic()
    for path in paths:
        relative = path.relative_to(ROOT)
        verifier_started = time.monotonic()
        print(f"START {relative}", flush=True)
        try:
            result = subprocess.run(
                [sys.executable, path.name],
                cwd=path.parent,
                capture_output=True,
                text=True,
                timeout=TIMEOUT_SECONDS,
            )
        except subprocess.TimeoutExpired as error:
            elapsed = time.monotonic() - verifier_started
            fails.append(path)
            print(f"TIMEOUT {relative} {elapsed:.1f}s", flush=True)
            stdout = error.stdout or ""
            stderr = error.stderr or ""
            if isinstance(stdout, bytes):
                stdout = stdout.decode("utf-8", errors="replace")
            if isinstance(stderr, bytes):
                stderr = stderr.decode("utf-8", errors="replace")
            print(stdout[-800:], stderr[-800:], flush=True)
            continue
        elapsed = time.monotonic() - verifier_started
        status = "PASS" if result.returncode == 0 else "FAIL"
        print(f"{status}  {relative} {elapsed:.1f}s", flush=True)
        if result.returncode != 0:
            fails.append(path)
            print(result.stdout[-800:], result.stderr[-800:], flush=True)

    elapsed = time.monotonic() - started
    print(
        f"\n{len(paths)} verifiers run, {len(skipped)} skipped, "
        f"{len(fails)} failed in {elapsed:.1f}s",
        flush=True,
    )
    return 1 if fails else 0


if __name__ == "__main__":
    raise SystemExit(main())
