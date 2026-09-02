#!/usr/bin/env python3
"""Successor-level source replay for the D9 normal-link predecessor.

The immutable V3 state records historical referee identifier ca730426..., but
that object is absent from this repository.  This adapter never dereferences
it.  Instead it authenticates the V3 bytes and replays the reviewed 5efbd07...
mathematical surface through the pinned independent referee kernel.  The old
mutable top-level wrapper is deliberately not invoked.
"""

from __future__ import annotations

import argparse
import copy
import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
from typing import Any


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
ADAPTER_PATH = HERE / "PORTABLE_PREDECESSOR_ADAPTER.json"
STATE_PATH = ROOT / "ai/omreal/data/CANONICAL_RESEARCH_STATE_V3.json"

FORMAT = "9dvl-d9-normal-link-successor-portable-adapter-v1"
HISTORICAL_REFEREE = "ca730426cdd5847ae262ddc29c6f4ae98369eba3"
HISTORICAL_TREE = "56fe7f95a4e20dea581736cb5539abb502e05a63"
OPENING = "6cbd1b4a7d3ed61bee268b6b54cbfadeece90f0e"
OPENING_TREE = "84eaf80b30e1f366b8f959bd6435a217762636b3"
BASE = "cbe84ccd7273252c81fd4da17ee360a284d2a2a6"
BASE_TREE = "da3cd6feca1052ea14ed5036413c72b8f7fadc2a"
REVIEWED = "5efbd07a25b818306f9fd22597fd81a0f2091309"
REVIEWED_TREE = "b8cb35941043ff40be06cba98461ddab0ba14c8f"
REVIEWED_PARENT = "c6bd7a6afeda0888fc950710b941cac6f6c9bf95"
REVIEWED_PARENT_TREE = "9c2dbe39a3ea0f36e9e9c8f845e6f72e98526421"
STATE_SHA256 = "e37fad74fae83cf087b2010039e85122866c3b093e34227f28d12759be94a6cf"
KERNEL = ROOT / "ops/team/diag9-s1237-normal-link-referee/verify_closing_referee.py"
KERNEL_SHA256 = "5619d72de02663ca4205951e2cd8bf9a865c016f3c8390af4a9261afc164e8c5"
REQUIRED_GIT_OBJECTS = {
    OPENING: OPENING_TREE,
    BASE: BASE_TREE,
    REVIEWED: REVIEWED_TREE,
    REVIEWED_PARENT: REVIEWED_PARENT_TREE,
}
ENTRYPOINTS = [
    "validate_source_manifest",
    "rebuild_census",
    "replay_geometry",
    "validate_certificate_contract",
    "validate_closing_manifest",
    "hostile_canaries",
]


class PortableReplayError(AssertionError):
    """Fail-closed predecessor replay rejection."""


def require(condition: bool, message: str) -> None:
    if not condition:
        raise PortableReplayError(message)


def exact_keys(value: Any, expected: set[str], label: str) -> None:
    require(isinstance(value, dict), f"{label}: expected object")
    require(set(value) == expected, f"{label}: wrong fields")


def canonical_json(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode("ascii")


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def sha256_path(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for block in iter(lambda: source.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def object_digest(value: dict[str, Any]) -> str:
    candidate = copy.deepcopy(value)
    candidate["semantic_sha256"] = "0" * 64
    return sha256_bytes(
        b"9dvl-d9-normal-link-successor-portable-adapter-v1\0"
        + canonical_json(candidate)
    )


def git_tree(commit: str) -> str:
    require(commit in REQUIRED_GIT_OBJECTS, f"unregistered Git object dereference: {commit}")
    completed = subprocess.run(
        ["git", "rev-parse", f"{commit}^{{tree}}"],
        cwd=ROOT,
        env={"GIT_NO_LAZY_FETCH": "1"},
        capture_output=True,
        text=True,
        check=False,
    )
    require(completed.returncode == 0, f"required source object missing: {commit}")
    return completed.stdout.strip()


def validate_canonical_state(state: dict[str, Any]) -> None:
    require(sha256_path(STATE_PATH) == STATE_SHA256, "canonical V3 byte digest")
    require(state.get("format") == "9dvl-canonical-research-state-v3", "canonical V3 format")
    require(state.get("status") == "PIVOT_REQUIRED", "canonical V3 status")
    require(state.get("theorem") == {
        "id": "9DVL", "score": "2/9", "proved_diagonals": [1, 2],
        "active_diagonal": None, "promotion": "NONE",
    }, "canonical V3 theorem ledger")
    cycle = state.get("completed_cycle", {})
    require(cycle.get("reviewed_math_commit") == REVIEWED, "canonical V3 reviewed head")
    require(cycle.get("reviewed_math_tree") == REVIEWED_TREE, "canonical V3 reviewed tree")
    require(cycle.get("referee_commit") == HISTORICAL_REFEREE, "canonical V3 recorded referee identifier")
    require(cycle.get("referee_tree") == HISTORICAL_TREE, "canonical V3 recorded referee tree")
    require(cycle.get("exact_consequence") == "THE_TANGENTIAL_FOUR_SUPPORT_REDUCTION_AND_ORDINARY_COMMON_RADIAL_LINK_ARE_INVALID_FOR_THE_SELECTED_S1237_COLLAR_ROUTE", "canonical V3 consequence")
    require(cycle.get("route_disposition") == "SELECTED_NORMAL_LINK_GATE_CLOSED_NEGATIVELY_AND_ROUTE_RETIRED", "canonical V3 route disposition")
    require(state.get("selected_target") is None, "canonical V3 selected target")


def validate_adapter(adapter: dict[str, Any], *, check_files: bool = True, check_git: bool = True) -> None:
    exact_keys(
        adapter,
        {
            "format", "track_id", "target_id", "successor", "historical_referee",
            "canonical_state", "reviewed_math", "source_derived_replay",
            "exact_artifacts", "scope", "semantic_sha256",
        },
        "portable adapter",
    )
    require(adapter["format"] == FORMAT, "portable adapter: format")
    require(adapter["track_id"] == "d9-universal-cut-certificate", "portable adapter: track")
    require(adapter["target_id"] == "D9_UNIVERSAL_FEASIBLE_COMPONENT_CUT_GATE1", "portable adapter: target")
    require(adapter["successor"] == {
        "opening_commit": OPENING,
        "opening_tree": OPENING_TREE,
        "canonical_base_commit": BASE,
        "canonical_base_tree": BASE_TREE,
    }, "portable adapter: successor binding")
    require(adapter["historical_referee"] == {
        "recorded_identifier": HISTORICAL_REFEREE,
        "recorded_tree": HISTORICAL_TREE,
        "availability_at_opening": "ABSENT",
        "object_existence_claim": "NONE",
        "dereference_policy": "FORBIDDEN_AND_NOT_REQUIRED",
    }, "portable adapter: absent-object policy")
    require(adapter["canonical_state"] == {
        "path": "ai/omreal/data/CANONICAL_RESEARCH_STATE_V3.json",
        "sha256": STATE_SHA256,
        "format": "9dvl-canonical-research-state-v3",
        "historical_referee_binding": "RECORDED_IDENTIFIER_ONLY",
    }, "portable adapter: canonical-state binding")
    require(adapter["reviewed_math"] == {
        "head": REVIEWED,
        "tree": REVIEWED_TREE,
        "parent": REVIEWED_PARENT,
        "parent_tree": REVIEWED_PARENT_TREE,
        "endpoint": "NORMAL_LINK_REDUCTION_NO_GO",
        "classification": "FINITE_EXACT_LOCAL_NORMAL_LINK_ROUTE_NO_GO",
    }, "portable adapter: reviewed math")
    replay = adapter["source_derived_replay"]
    exact_keys(
        replay,
        {
            "kernel_path", "kernel_sha256", "entrypoints", "acceptance_logic",
            "mutable_wrapper", "active_factor_classes", "all_occurrences",
            "aligned_occurrences", "parent_inequalities",
            "hostile_mutations_rejected", "closing_semantic_sha256",
        },
        "portable adapter: source replay",
    )
    require(replay["kernel_path"] == "ops/team/diag9-s1237-normal-link-referee/verify_closing_referee.py", "portable adapter: kernel path")
    require(replay["kernel_sha256"] == KERNEL_SHA256, "portable adapter: kernel digest")
    require(replay["entrypoints"] == ENTRYPOINTS, "portable adapter: entrypoint boundary")
    require(replay["acceptance_logic"] == "PINNED_INDEPENDENT_REFEREE_KERNEL_ONLY", "portable adapter: acceptance logic")
    require(replay["mutable_wrapper"] == "NOT_INVOKED", "portable adapter: mutable wrapper")
    require((replay["active_factor_classes"], replay["all_occurrences"], replay["aligned_occurrences"], replay["parent_inequalities"], replay["hostile_mutations_rejected"]) == (3539, 6167, 5026, 70, 16), "portable adapter: exact census")
    require(replay["closing_semantic_sha256"] == "877ee39e97c9cc721fb2cc578618701953f8436fce128c3cba54fdf2026d4809", "portable adapter: closing digest")
    require(adapter["exact_artifacts"] == {
        "producer_no_go_sha256": "8aa726c69b556f7c2d85f7f852cb88329da39dcd173294a7db7245f13e0d2d54",
        "producer_semantic_sha256": "f2169e2bc90f9c92d49f754d695b34b9dc3da770a3aecf6bfb6e84a6cb80b747",
        "falsifier_result_sha256": "15ce5c17a174ed6a82173d24a8f72d04da5962bcea9e87cf3648adb21351d46b",
        "falsifier_semantic_sha256": "95631d5d6192e9ff86ab04a3bb065e849a4b592be24a752c1cade41d669cf666",
        "certificate_result_sha256": "8b932ec411fe9bc96d8bb895fccdcf7a63985df6ce4d35b38e2f53eef3afc010",
        "referee_result_sha256": "16be207c4abaddf52bd6b670c293159cb317e712c431597838b00e2815bb8902",
    }, "portable adapter: exact artifacts")
    require(adapter["scope"] == {
        "replayed": "THE_TWO_FROZEN_SOURCE_DERIVED_WITNESS_METHODS",
        "weighted_recursive_links": "OPEN",
        "strict_open_parent_crossing": "NOT_CLAIMED",
        "global_cut_coverage": "NOT_CLAIMED",
        "diagonal_9": "OPEN",
        "ledger": "2/9",
    }, "portable adapter: scope")
    require(adapter["semantic_sha256"] == object_digest(adapter), "portable adapter: semantic digest")

    if check_files:
        require(sha256_path(KERNEL) == KERNEL_SHA256, "portable adapter: kernel byte drift")
        state = json.loads(STATE_PATH.read_text(encoding="utf-8"))
        validate_canonical_state(state)
        byte_pins = {
            ROOT / "ops/team/diag9-s1237-normal-link-prover/DIAG9_S1237_NORMAL_LINK_NO_GO.json": adapter["exact_artifacts"]["producer_no_go_sha256"],
            ROOT / "ops/team/diag9-s1237-normal-link-falsifier/RESULT.json": adapter["exact_artifacts"]["falsifier_result_sha256"],
            ROOT / "ops/team/diag9-s1237-normal-link-certificate/RESULT.json": adapter["exact_artifacts"]["certificate_result_sha256"],
            ROOT / "ops/team/diag9-s1237-normal-link-referee/RESULT.json": adapter["exact_artifacts"]["referee_result_sha256"],
        }
        for path, expected in byte_pins.items():
            require(sha256_path(path) == expected, f"portable adapter: artifact drift {path.relative_to(ROOT)}")
    if check_git:
        require(HISTORICAL_REFEREE not in REQUIRED_GIT_OBJECTS, "portable adapter: absent historical object registered")
        for commit, tree in REQUIRED_GIT_OBJECTS.items():
            require(git_tree(commit) == tree, f"portable adapter: Git tree drift {commit}")


def import_kernel():
    require(sha256_path(KERNEL) == KERNEL_SHA256, "portable replay: kernel byte drift")
    specification = importlib.util.spec_from_file_location("d9_frozen_independent_referee", KERNEL)
    require(specification is not None and specification.loader is not None, "portable replay: cannot load kernel")
    module = importlib.util.module_from_spec(specification)
    specification.loader.exec_module(module)
    return module


def replay_source_kernel(adapter: dict[str, Any]) -> dict[str, Any]:
    kernel = import_kernel()
    kernel.validate_source_manifest()
    census = kernel.rebuild_census()
    geometry = kernel.replay_geometry(census)
    certificate = kernel.validate_certificate_contract(census)
    closing = kernel.load_json(kernel.CLOSING_MANIFEST)
    kernel.validate_closing_manifest(closing, census, geometry, certificate)
    rejected = kernel.hostile_canaries(closing, census, geometry, certificate)
    observed = {
        "active_factor_classes": census["active_factor_count"],
        "all_occurrences": census["all_occurrence_count"],
        "aligned_occurrences": census["aligned_occurrence_count"],
        "parent_inequalities": geometry["parent_inequality_count"],
        "hostile_mutations_rejected": rejected,
        "closing_semantic_sha256": closing["semantic_sha256"],
    }
    expected = {key: adapter["source_derived_replay"][key] for key in observed}
    require(observed == expected, "portable replay: source-derived result drift")
    return observed


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest-only", action="store_true")
    arguments = parser.parse_args()
    adapter = json.loads(ADAPTER_PATH.read_text(encoding="utf-8"))
    validate_adapter(adapter)
    print("PASS portable predecessor bindings; ca730426 is recorded as absent and never dereferenced")
    if arguments.manifest_only:
        print("PASS manifest-only portability gate")
        return
    observed = replay_source_kernel(adapter)
    print(
        "PASS source-derived predecessor replay",
        observed["active_factor_classes"], "classes /",
        observed["all_occurrences"], "occurrences /",
        observed["aligned_occurrences"], "aligned /",
        observed["parent_inequalities"], "parent inequalities /",
        observed["hostile_mutations_rejected"], "hostile rejections",
    )
    print("ACCEPT PORTABLE_PREDECESSOR_REPLAY NORMAL_LINK_REDUCTION_NO_GO")
    print("SCOPE local predecessor no-go only; weighted links, universal cut coverage, D9, and ledger remain open")


if __name__ == "__main__":
    main()
