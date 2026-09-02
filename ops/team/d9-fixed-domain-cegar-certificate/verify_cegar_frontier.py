#!/usr/bin/env python3
"""Producer-independent verifier for D9 fixed-domain CEGAR gate 1."""

from __future__ import annotations

from copy import deepcopy
import hashlib
import json
from pathlib import Path
import subprocess
import sys

import numpy as np


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
FRONTIER = ROOT / "ops/team/d9-fixed-domain-cegar-constructor/CEGAR_FRONTIER.json"
CONSTRUCTOR_RESULT = ROOT / "ops/team/d9-fixed-domain-cegar-constructor/RESULT.json"
FALSIFIER_RESULT = ROOT / "ops/team/d9-fixed-domain-cegar-falsifier/RESULT.json"
RESULT = HERE / "RESULT.json"

SOURCE_PINS = {
    "ai/omreal/data/ninth_candidate_12_37_antichain.npz": "11ca66549982ec40ce8425d2caed45b418edb73c4eb415a45b39d57e481bd1e4",
    "ai/omreal/data/ninth_candidate_12_37_path.npz": "8db38e00d9bf8701558c27cd4ede3e024db8953ea3ef9873bf0b4fc65ad6bcda",
    "ai/omreal/data/ninth_candidate_37_176_antichain.npz": "fe7bb166b5a151262c665875d32de49d7e8a330cf11b26609458af6b2661a59f",
    "ai/omreal/data/ninth_candidate_37_176_path.npz": "3c37c3c0d5de159bec9d48eeaaf57bccbe07c2f3aeb0ede9d4b1ddbae2bd3507",
    "ai/omreal/verify_ninth_candidate_antichain.py": "19060052bde9d29de3c91becf188d5f4b99c034bbf5a81db4206885bea28b395",
    "ai/omreal/verify_ninth_candidate_path.py": "283d9ead88881d2308d444eaffe172cb0414ef161215053271f5960116f544e6",
    "ai/omreal/verify_ninth_candidate_generic.py": "525aad040d9b38a1cb018439e44a36a0259265e8f603af975f6b6a785ea217ac",
}


class Reject(AssertionError):
    pass


def require(condition: bool, message: str) -> None:
    if not condition:
        raise Reject(message)


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


def replay(arguments: list[str], markers: tuple[str, ...]) -> None:
    process = subprocess.run(
        [sys.executable, "-u", *arguments], cwd=ROOT,
        text=True, capture_output=True,
    )
    require(process.returncode == 0, f"replay failed: {process.stderr[-1000:]}")
    for marker in markers:
        require(marker in process.stdout, f"missing replay marker {marker}")


def validate_frontier(candidate: dict) -> None:
    require(candidate["format"] == "d9-fixed-domain-cegar-frontier-v1", "frontier format")
    require(candidate["base_revision"] == "a5990bff953432a49cfa186f78e25efdb7df280b", "frontier base")
    require(candidate["opening_revision"] == "6fc3d4d8c4d235dbb262e56abfccb7c32dad1a39", "opening revision")
    scope = candidate["scope"]
    require(scope["complete_committed_seed_frontier"] is True, "seed frontier completeness")
    require(scope["complete_fixed_domain_candidate_generator"] is False, "candidate generator scope")
    require(scope["complete_parent_chamber_coverage"] is False, "parent coverage scope")
    require(scope["all_parent_coverage"] is False, "all-parent scope")
    require(len(candidate["seeds"]) == 2, "seed count")
    expected = [([12, 37], 22711), ([37, 176], 22811)]
    for seed, (endpoints, segments) in zip(candidate["seeds"], expected):
        require(seed["parent_index"] == 2599, "seed parent")
        require(seed["endpoints"] == endpoints, "seed endpoints")
        require(seed["signature_count"] == 9, "signature count")
        require(len(seed["signatures"]) == 9 and len(set(seed["signatures"])) == 9, "signature identity")
        require(seed["feasibility_or_gordan_entries"] == 63, "antichain entries")
        require(seed["ordered_incomparability_clauses"] == 72, "incomparability clauses")
        require(seed["path_segments"] == segments, "seed path segments")
        require(seed["theorem_domain_input"] == "EXACT_NONEMPTY_PROPER_PAIRWISE_INCOMPARABLE", "theorem input")
        require(seed["separator_disposition"] == "EXACT_PATH_REPAIR", "separator disposition")
        require(seed["endpoint_pair_same_component"] is True, "endpoint connectivity")
        require(seed["source_realized_counterexample"] is False, "counterexample flag")
    aggregate = candidate["aggregate"]
    require(aggregate == {
        "seed_families": 2,
        "feasibility_or_gordan_entries": 126,
        "ordered_incomparability_clauses": 144,
        "path_segments": 45522,
        "exact_path_repairs": 2,
        "source_realized_counterexamples": 0,
        "unclassified_seeds": 0,
    }, "aggregate census")
    require(candidate["endpoint"] == "COMMITTED_CEGAR_SEED_FRONTIER_EXACTLY_REPAIRED", "frontier endpoint")
    require(candidate["classification"] == "EXACT_NULL_NO_D9_COUNTEREXAMPLE", "frontier classification")
    require(candidate["ledger_delta"] == "none", "frontier ledger delta")
    require(candidate["theorem_ledger"] == "2/9", "frontier ledger")
    require("NO_DIAGONAL_9_PROOF_OR_COUNTEREXAMPLE" in candidate["nonconsequences"], "frontier nonconsequence")
    require(candidate["semantic_sha256"] == semantic_sha256(candidate), "semantic digest")


def validate_result(candidate: dict) -> None:
    require(candidate["format"] == "d9-fixed-domain-cegar-certificate-result-v1", "certificate format")
    require(candidate["verdict"] == "ACCEPT", "certificate verdict")
    require(candidate["accepted_endpoint"] == "COMMITTED_CEGAR_SEED_FRONTIER_EXACTLY_REPAIRED", "certificate endpoint")
    require(candidate["accepted_classification"] == "EXACT_NULL_NO_D9_COUNTEREXAMPLE", "certificate classification")
    independence = candidate["independence"]
    require(independence["new_producer_imported"] is False, "producer independence")
    require(independence["hostile_mutations_rejected"] == 12, "hostile census")
    require(candidate["seed_families"] == 2, "certificate seed count")
    require(candidate["exact_path_repairs"] == 2, "certificate path repairs")
    require(candidate["source_realized_counterexamples"] == 0, "certificate counterexamples")
    require(candidate["complete_fixed_domain_candidate_generator"] is False, "certificate generator scope")
    require(candidate["ledger_delta"] == "none", "certificate ledger delta")
    require(candidate["theorem_ledger"] == "2/9", "certificate ledger")
    require(candidate["github_write"] is False, "GitHub authority")


def hostile_mutations(stored: dict) -> None:
    mutations = []
    candidate = deepcopy(stored); candidate["base_revision"] = "0" * 40; mutations.append((candidate, "frontier base"))
    candidate = deepcopy(stored); candidate["scope"]["complete_fixed_domain_candidate_generator"] = True; mutations.append((candidate, "candidate generator scope"))
    candidate = deepcopy(stored); candidate["scope"]["complete_parent_chamber_coverage"] = True; mutations.append((candidate, "parent coverage scope"))
    candidate = deepcopy(stored); candidate["seeds"][0]["endpoints"] = [12, 38]; mutations.append((candidate, "seed endpoints"))
    candidate = deepcopy(stored); candidate["seeds"][0]["signature_count"] = 8; mutations.append((candidate, "signature count"))
    candidate = deepcopy(stored); candidate["seeds"][0]["path_segments"] = 22710; mutations.append((candidate, "seed path segments"))
    candidate = deepcopy(stored); candidate["seeds"][0]["separator_disposition"] = "COUNTEREXAMPLE"; mutations.append((candidate, "separator disposition"))
    candidate = deepcopy(stored); candidate["seeds"][1]["source_realized_counterexample"] = True; mutations.append((candidate, "counterexample flag"))
    candidate = deepcopy(stored); candidate["aggregate"]["unclassified_seeds"] = 1; mutations.append((candidate, "aggregate census"))
    candidate = deepcopy(stored); candidate["classification"] = "D9_COUNTEREXAMPLE"; mutations.append((candidate, "frontier classification"))
    candidate = deepcopy(stored); candidate["theorem_ledger"] = "3/9"; mutations.append((candidate, "frontier ledger"))
    candidate = deepcopy(stored); candidate["nonconsequences"].remove("NO_DIAGONAL_9_PROOF_OR_COUNTEREXAMPLE"); mutations.append((candidate, "frontier nonconsequence"))
    for candidate, marker in mutations:
        candidate["semantic_sha256"] = semantic_sha256(candidate)
        try:
            validate_frontier(candidate)
        except Reject as error:
            require(marker in str(error), f"wrong hostile rejection: {error}")
            continue
        raise Reject(f"hostile mutation accepted: {marker}")


def main() -> None:
    result = json.loads(RESULT.read_text(encoding="utf-8"))
    validate_result(result)
    for path, expected in SOURCE_PINS.items():
        require(sha256(ROOT / path) == expected, f"source pin {path}")
    for path, expected in result["pins"].items():
        require(sha256(ROOT / path) == expected, f"evidence pin {path}")

    # Reconstruct seed identities and path lengths directly from accepted data.
    for prefix, endpoints, segments in (
        ("12_37", [12, 37], 22711),
        ("37_176", [37, 176], 22811),
    ):
        antichain = np.load(ROOT / f"ai/omreal/data/ninth_candidate_{prefix}_antichain.npz", allow_pickle=False)
        path = np.load(ROOT / f"ai/omreal/data/ninth_candidate_{prefix}_path.npz", allow_pickle=False)
        require([int(value) for value in path["endpoint"]] == endpoints, "source endpoints")
        require(len(antichain["signature"]) == 9, "source signature count")
        require(sum(len(path[field]) for field in ("update_col_a", "bridge_col", "update_col_b")) == segments, "source path segments")

    replay(["ai/omreal/verify_ninth_candidate_antichain.py"],
           ("proper pairwise-incomparable family",))
    replay(["ai/omreal/verify_ninth_candidate_path.py"],
           ("charts 12 and 37 lie in one component of F_S",))
    replay(["ai/omreal/verify_ninth_candidate_generic.py", "antichain",
            "ai/omreal/data/ninth_candidate_37_176_antichain.npz"],
           ("proper pairwise-incomparable family",))
    replay(["ai/omreal/verify_ninth_candidate_generic.py", "path",
            "ai/omreal/data/ninth_candidate_37_176_path.npz"],
           ("charts 37 and 176 lie in one component of F_S",))

    frontier = json.loads(FRONTIER.read_text(encoding="utf-8"))
    validate_frontier(frontier)
    constructor = json.loads(CONSTRUCTOR_RESULT.read_text(encoding="utf-8"))
    require(constructor["classification"] == frontier["classification"], "constructor classification")
    require(constructor["frontier_sha256"] == sha256(FRONTIER), "constructor frontier pin")
    falsifier = json.loads(FALSIFIER_RESULT.read_text(encoding="utf-8"))
    require(falsifier["classification"] == "TWO_EXACT_PATH_REPAIRS_AND_GLOBAL_SCOPE_NULL", "falsifier classification")
    require(falsifier["global_common_feasibility_connectivity"] == "UNPROVED", "falsifier scope")
    hostile_mutations(frontier)
    print("PASS D9 fixed-domain CEGAR producer-independent certificate")
    print("seeds=2 path_repairs=2 counterexamples=0 segments=45522")
    print("hostile_mutations=12 ledger=2/9 scope=EXACT_NULL")


if __name__ == "__main__":
    main()
