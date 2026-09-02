#!/usr/bin/env python3
"""Build the bounded exact D9 fixed-domain CEGAR seed frontier."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import subprocess
import sys

import numpy as np


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
DATA = ROOT / "ai" / "omreal" / "data"
OUTPUT = HERE / "CEGAR_FRONTIER.json"
RESULT = HERE / "RESULT.json"

BASE = "a5990bff953432a49cfa186f78e25efdb7df280b"
BASE_TREE = "96e75f55512f6abbc09749509a45b63adebfa456"
OPENING = "6fc3d4d8c4d235dbb262e56abfccb7c32dad1a39"
OPENING_TREE = "71ced64b12ace616e641befd5624f3b8653d217a"

PINS = {
    "ninth_candidate_12_37_antichain.npz": "11ca66549982ec40ce8425d2caed45b418edb73c4eb415a45b39d57e481bd1e4",
    "ninth_candidate_12_37_path.npz": "8db38e00d9bf8701558c27cd4ede3e024db8953ea3ef9873bf0b4fc65ad6bcda",
    "ninth_candidate_37_176_antichain.npz": "fe7bb166b5a151262c665875d32de49d7e8a330cf11b26609458af6b2661a59f",
    "ninth_candidate_37_176_path.npz": "3c37c3c0d5de159bec9d48eeaaf57bccbe07c2f3aeb0ede9d4b1ddbae2bd3507",
}

SEEDS = (
    {
        "id": "ROW2599_12_37",
        "antichain": "ninth_candidate_12_37_antichain.npz",
        "path": "ninth_candidate_12_37_path.npz",
        "endpoints": [12, 37],
        "segments": 22_711,
        "antichain_command": ["ai/omreal/verify_ninth_candidate_antichain.py"],
        "path_command": ["ai/omreal/verify_ninth_candidate_path.py"],
    },
    {
        "id": "ROW2599_37_176",
        "antichain": "ninth_candidate_37_176_antichain.npz",
        "path": "ninth_candidate_37_176_path.npz",
        "endpoints": [37, 176],
        "segments": 22_811,
        "antichain_command": [
            "ai/omreal/verify_ninth_candidate_generic.py", "antichain",
            "ai/omreal/data/ninth_candidate_37_176_antichain.npz",
        ],
        "path_command": [
            "ai/omreal/verify_ninth_candidate_generic.py", "path",
            "ai/omreal/data/ninth_candidate_37_176_path.npz",
        ],
    },
)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for block in iter(lambda: source.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def semantic_sha256(candidate: dict) -> str:
    payload = dict(candidate)
    payload.pop("semantic_sha256", None)
    raw = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(raw).hexdigest()


def run(arguments: list[str], markers: tuple[str, ...]) -> str:
    process = subprocess.run(
        [sys.executable, "-u", *arguments], cwd=ROOT, text=True,
        capture_output=True,
    )
    if process.returncode:
        raise RuntimeError(process.stderr[-2000:])
    for marker in markers:
        if marker not in process.stdout:
            raise RuntimeError(f"missing replay marker {marker!r}")
    return hashlib.sha256(process.stdout.encode()).hexdigest()


def main() -> None:
    for name, expected in PINS.items():
        if sha256(DATA / name) != expected:
            raise RuntimeError(f"pinned source drift: {name}")

    records = []
    for seed in SEEDS:
        antichain = np.load(DATA / seed["antichain"], allow_pickle=False)
        path = np.load(DATA / seed["path"], allow_pickle=False)
        signatures = [int(value) for value in antichain["signature"]]
        if signatures != [int(value) for value in path["signature"]]:
            raise RuntimeError(f"signature mismatch: {seed['id']}")
        if int(antichain["parent_index"].item()) != 2599:
            raise RuntimeError("wrong parent")
        if [int(value) for value in path["endpoint"]] != seed["endpoints"]:
            raise RuntimeError("wrong endpoints")
        segments = sum(
            len(path[field]) for field in
            ("update_col_a", "bridge_col", "update_col_b")
        )
        if segments != seed["segments"]:
            raise RuntimeError("wrong segment census")
        antichain_stdout = run(
            seed["antichain_command"],
            ("all nine regions are nonempty and proper",
             "proper pairwise-incomparable family"),
        )
        path_stdout = run(
            seed["path_command"],
            ("every segment changes one column", "lie in one component of F_S"),
        )
        records.append({
            "id": seed["id"],
            "parent_index": 2599,
            "endpoints": seed["endpoints"],
            "signature_count": len(signatures),
            "signatures": signatures,
            "antichain_chart_count": len(antichain["chart_index"]),
            "feasibility_or_gordan_entries": 63,
            "ordered_incomparability_clauses": 72,
            "path_segments": segments,
            "theorem_domain_input": "EXACT_NONEMPTY_PROPER_PAIRWISE_INCOMPARABLE",
            "separator_disposition": "EXACT_PATH_REPAIR",
            "endpoint_pair_same_component": True,
            "source_realized_counterexample": False,
            "antichain_replay_stdout_sha256": antichain_stdout,
            "path_replay_stdout_sha256": path_stdout,
        })

    frontier = {
        "format": "d9-fixed-domain-cegar-frontier-v1",
        "cycle_id": "2026-09-01-d9-fixed-domain-cegar-gate1",
        "base_revision": BASE,
        "base_tree": BASE_TREE,
        "opening_revision": OPENING,
        "opening_tree": OPENING_TREE,
        "selected_target": "D9_FIXED_DOMAIN_COUNTEREXAMPLE_CEGAR_GATE1",
        "scope": {
            "classification": "TWO_COMMITTED_EXACT_ROW2599_STRESS_FAMILIES_ONLY",
            "complete_committed_seed_frontier": True,
            "complete_fixed_domain_candidate_generator": False,
            "complete_parent_chamber_coverage": False,
            "all_parent_coverage": False,
        },
        "seeds": records,
        "aggregate": {
            "seed_families": 2,
            "feasibility_or_gordan_entries": 126,
            "ordered_incomparability_clauses": 144,
            "path_segments": 45_522,
            "exact_path_repairs": 2,
            "source_realized_counterexamples": 0,
            "unclassified_seeds": 0,
        },
        "endpoint": "COMMITTED_CEGAR_SEED_FRONTIER_EXACTLY_REPAIRED",
        "classification": "EXACT_NULL_NO_D9_COUNTEREXAMPLE",
        "ledger_delta": "none",
        "theorem_ledger": "2/9",
        "nonconsequences": [
            "NO_EXHAUSTIVE_FIXED_DOMAIN_CANDIDATE_GENERATOR",
            "NO_COMPLETE_PARENT_CHAMBER_COVERAGE",
            "NO_GLOBAL_COMMON_FEASIBILITY_CONNECTIVITY",
            "NO_DIAGONAL_9_PROOF_OR_COUNTEREXAMPLE",
            "NO_9DVL_SCORE_CHANGE",
        ],
    }
    frontier["semantic_sha256"] = semantic_sha256(frontier)
    OUTPUT.write_text(json.dumps(frontier, indent=2) + "\n", encoding="utf-8")

    result = {
        "format": "d9-fixed-domain-cegar-constructor-result-v1",
        "track_id": "d9-fixed-domain-cegar-constructor",
        "outcome": "inconclusive",
        "endpoint": frontier["endpoint"],
        "classification": frontier["classification"],
        "frontier_sha256": sha256(OUTPUT),
        "frontier_semantic_sha256": frontier["semantic_sha256"],
        "seed_families": 2,
        "exact_path_repairs": 2,
        "source_realized_counterexamples": 0,
        "complete_fixed_domain_candidate_generator": False,
        "ledger_change_recommended": "none",
        "next_action": "Retire another sampled-separator CEGAR seed cycle and pivot to a projection-free adaptive component decomposition with a complete parent-residence invariant.",
        "github_write": False,
    }
    RESULT.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print("WROTE exact D9 fixed-domain CEGAR frontier")
    print("seeds=2 path_repairs=2 segments=45522 counterexamples=0")
    print("endpoint=EXACT_NULL_NO_D9_COUNTEREXAMPLE ledger=2/9")


if __name__ == "__main__":
    main()
