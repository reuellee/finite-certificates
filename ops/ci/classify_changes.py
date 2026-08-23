#!/usr/bin/env python3
"""Deterministically map a Git diff to the exact CI tiers it requires.

The classifier is intentionally repository-owned instead of embedding path logic in
GitHub Actions expressions.  That makes the routing policy locally testable and gives
the final gate a single source of truth.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import re
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

import run_all  # noqa: E402


FORMAT = "finite-certificates-ci-plan-v3"
FULL_EVENTS = frozenset({"schedule", "workflow_dispatch"})
NON_PROOF_SUFFIXES = frozenset({".md"})
CODE_SUFFIXES = frozenset({".py", ".sage", ".sh", ".toml", ".yaml", ".yml"})
ROOT_PROOF_FILES = frozenset({"requirements.txt", "run_all.py"})

# Slow verifiers are outside the bounded suite.  Every committed input consumed
# only by one of them must be declared here.  Unknown non-code proof artifacts
# fail closed by requesting the exhaustive shards; this manifest keeps common
# certificate changes targeted while remaining auditable.
SLOW_INPUT_DEPENDENCIES = {
    "ai/omminor/data/minimal_sweep.txt": (
        "ai/omminor/verify_minimal.py",
    ),
    "ai/omreal/certs_4_8.jsonl": (
        "ai/omminor/verify_minimal.py",
        "ai/omreal/verify_diag2_common_shear_parent2604.py",
        "ai/omreal/verify_diag3_pair_fullsupport_block_symmetry.py",
        "ai/omreal/verify_diag3_pair_fullsupport_safe_segment_walls.py",
        "ai/omreal/verify_diag3_pair_global_compactification_atlas.py",
        "ai/omreal/verify_diag3_pair_global_parent_face_gate.py",
        "ai/omreal/verify_diag3_triple_rank_drop_parent_atlas.py",
        "ai/omreal/verify_diag9_parent_ranking.py",
        "ai/omreal/verify_seeat.py",
    ),
    "ai/omreal/data/DIAG3_triple_fold_boundary_chain.json": (
        "ai/omreal/verify_diag3_triple_concurrence_local_fold_cell.py",
    ),
    "ai/omreal/data/DIAG9_GRAPH_parent860_plane_projection_frontier.json": (
        "ai/omreal/verify_diag9_parent860_plane_projection.py",
    ),
    "jacobian/druzkowski_map.py": (
        "jacobian/verify_druzkowski.py",
    ),
    "jacobian/cubic_map.py": (
        "jacobian/verify_druzkowski.py",
    ),
}

# These slow verifiers have purpose-built jobs with the right dependencies and
# worker counts.  Do not run a second copy in the changed-slow-verifier job.
SPECIAL_VERIFIERS = frozenset(
    {
        "verify_diag2_escape_set_atlas178.py",
        "verify_diag2_pivot_49_pair_saturation.py",
        "verify_diag2_pivot_all_pair_fibers.py",
        "verify_diag3_ordered_root_atlas178.py",
        "verify_diag3_pair_parent_source_block_labels.py",
    }
)

DIAG2_ATLAS_MARKERS = (
    "DIAG2_ESCAPE_SET_atlas178",
    "DIAG9_GRAPH_exact_topes",
    "four_chart_gate",
    "seeat_parent2599_upper178",
    "verify_diag2_escape_set_atlas178",
    "verify_diag2_escape_set_topes",
    "verify_diag2_moving_witness_shear",
    "verify_diag3_ordered_root_atlas178",
)
LABELED_PAIR_MARKERS = (
    "DIAG2_PIVOT_LABELED_PAIR",
    "DIAG2_PIVOT_REPRESENTATIVE_GRADIENT",
    "DIAG2_PIVOT_REPRESENTATIVE_TRIPLES",
    "DIAG2_PIVOT_pair_classification",
    "DIAG9_GRAPH_global_factor_census",
    "prototype_koszul_circuits",
    "verify_diag2_pivot_49_pair_saturation",
    "verify_diag2_pivot_all_pair_fibers",
    "verify_residual_log_binomials",
)
SOURCE_BLOCK_MARKERS = (
    "DIAG3_PAIR_PARENT_SOURCE_BLOCK_LABELS",
    "diag3_pair_parent_source_block_labels_core",
    "verify_diag3_pair_parent_source_block_labels",
)
PARENT860_MARKERS = (
    "DIAG2_PIVOT_LABELED_PAIR",
    "DIAG2_PIVOT_REPRESENTATIVE_GRADIENT",
    "DIAG2_PIVOT_REPRESENTATIVE_TRIPLES",
    "DIAG9_GRAPH_exact_topes",
    "DIAG9_GRAPH_parent860_",
    "DIAG9_GRAPH_verify_row2599_line",
    "DIAG9_GRAPH_verify_row2599_slice",
    "verify_diag9_parent_ranking",
)


def is_proof_input(path: str) -> bool:
    """Fail closed for non-document changes in the two executable proof trees."""
    item = Path(path)
    if path in ROOT_PROOF_FILES:
        return True
    if not (path.startswith("ai/") or path.startswith("jacobian/")):
        return False
    return item.suffix.lower() not in NON_PROOF_SUFFIXES


def has_marker(paths: tuple[str, ...], markers: tuple[str, ...]) -> bool:
    return any(marker in path for path in paths for marker in markers)


def slow_verifier_paths(paths: tuple[str, ...]) -> tuple[str, ...]:
    """Find changed slow verifiers and direct slow dependants of changed modules."""
    selected: set[str] = set()
    for raw in paths:
        selected.update(SLOW_INPUT_DEPENDENCIES.get(raw, ()))

    changed_modules: set[str] = set()
    for raw in paths:
        path = Path(raw)
        if path.suffix == ".py":
            changed_modules.add(path.stem)
        if (
            path.name in run_all.SLOW
            and path.name not in SPECIAL_VERIFIERS
        ):
            selected.add(raw)

    for verifier in ROOT.rglob("verify_*.py"):
        if verifier.name not in run_all.SLOW or verifier.name in SPECIAL_VERIFIERS:
            continue
        relative = verifier.relative_to(ROOT)
        if not changed_modules:
            continue
        source = verifier.read_text(encoding="utf-8")
        for module in changed_modules:
            pattern = (
                rf"(?:\bimport\s+(?:[A-Za-z_]\w*\.)*{re.escape(module)}\b|"
                rf"\bfrom\s+(?:[A-Za-z_]\w*\.)*{re.escape(module)}\s+import\b)"
            )
            if re.search(pattern, source):
                selected.add(relative.as_posix())
                break
    return tuple(sorted(selected))


def classify(paths: tuple[str, ...], event: str) -> dict[str, object]:
    canonical = tuple(sorted(set(paths)))
    proof_paths = tuple(path for path in canonical if is_proof_input(path))
    omreal_proof = tuple(path for path in proof_paths if path.startswith("ai/omreal/"))
    slow = slow_verifier_paths(canonical)
    external_changed = any(
        Path(path).name in run_all.EXTERNAL_INPUT for path in proof_paths
    )
    declared_slow_inputs = set(SLOW_INPUT_DEPENDENCIES).intersection(proof_paths)
    undeclared_artifacts = tuple(
        path
        for path in proof_paths
        if Path(path).suffix.lower() not in CODE_SUFFIXES
        and path not in declared_slow_inputs
        and not path.startswith("ai/maxout/")
    )
    return {
        "format": FORMAT,
        "event": event,
        "full": event in FULL_EVENTS,
        "exhaustive": bool(undeclared_artifacts),
        "changed_count": len(canonical),
        "proof_change": bool(proof_paths),
        "slow_changed": bool(slow),
        "external_changed": external_changed,
        "slow_verifiers": list(slow),
        "undeclared_artifacts": list(undeclared_artifacts),
        "maxout": any(path.startswith("ai/maxout/") for path in proof_paths),
        "diag2_atlas": has_marker(omreal_proof, DIAG2_ATLAS_MARKERS),
        "labeled_pairs": has_marker(omreal_proof, LABELED_PAIR_MARKERS),
        "source_block_labels": has_marker(omreal_proof, SOURCE_BLOCK_MARKERS),
        "parent860": has_marker(omreal_proof, PARENT860_MARKERS),
        "changed_paths": list(canonical),
    }


def valid_commit(revision: str) -> bool:
    if not revision or set(revision) == {"0"}:
        return False
    result = subprocess.run(
        ["git", "cat-file", "-e", f"{revision}^{{commit}}"],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )
    return result.returncode == 0


def changed_paths(base: str, head: str) -> tuple[str, ...]:
    if not valid_commit(head):
        raise ValueError(f"head revision is unavailable: {head!r}")
    if valid_commit(base):
        # Disable rename collapsing so both the removed proof path and its new
        # destination are classified.  Otherwise a rename from a proof tree to
        # an archive/non-proof path could hide the deletion.
        command = [
            "git",
            "diff",
            "--no-renames",
            "--name-only",
            "--diff-filter=ACDMRTUXB",
            base,
            head,
        ]
    else:
        # The first push to a branch can carry an all-zero `before` SHA.  Treat
        # every tracked path as changed rather than risk a false-negative route.
        command = ["git", "ls-tree", "-r", "--name-only", head]
    output = subprocess.check_output(command, cwd=ROOT, text=True)
    return tuple(line for line in output.splitlines() if line)


def write_github_outputs(plan: dict[str, object], destination: Path) -> None:
    keys = (
        "full",
        "exhaustive",
        "proof_change",
        "slow_changed",
        "external_changed",
        "maxout",
        "diag2_atlas",
        "labeled_pairs",
        "source_block_labels",
        "parent860",
    )
    with destination.open("a", encoding="utf-8") as stream:
        for key in keys:
            stream.write(f"{key}={str(bool(plan[key])).lower()}\n")
        stream.write(f"changed_count={plan['changed_count']}\n")


def write_summary(plan: dict[str, object], destination: Path) -> None:
    enabled = [
        key
        for key in (
            "proof_change",
            "exhaustive",
            "slow_changed",
            "external_changed",
            "maxout",
            "diag2_atlas",
            "labeled_pairs",
            "source_block_labels",
            "parent860",
        )
        if plan[key]
    ]
    tier = "full replay" if plan["full"] else "pull-request/push gate"
    with destination.open("a", encoding="utf-8") as stream:
        stream.write("## Verification plan\n\n")
        stream.write(f"Tier: **{tier}**  \n")
        stream.write(f"Changed paths: **{plan['changed_count']}**  \n")
        stream.write(f"Targeted scopes: **{', '.join(enabled) if enabled else 'none'}**\n")


def parser() -> argparse.ArgumentParser:
    answer = argparse.ArgumentParser(description=__doc__)
    answer.add_argument("--event", required=True)
    answer.add_argument("--base", default="")
    answer.add_argument("--head", default="HEAD")
    answer.add_argument("--path", action="append", dest="paths")
    answer.add_argument("--github-output", type=Path)
    answer.add_argument("--github-summary", type=Path)
    answer.add_argument("--json", action="store_true")
    return answer


def main() -> int:
    arguments = parser().parse_args()
    if arguments.paths is not None:
        paths = tuple(arguments.paths)
    elif arguments.event in FULL_EVENTS:
        paths = ()
    else:
        paths = changed_paths(arguments.base, arguments.head)
    plan = classify(paths, arguments.event)
    if arguments.github_output:
        write_github_outputs(plan, arguments.github_output)
    if arguments.github_summary:
        write_summary(plan, arguments.github_summary)
    if arguments.json or not arguments.github_output:
        print(json.dumps(plan, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
