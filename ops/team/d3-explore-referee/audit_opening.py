#!/usr/bin/env python3
"""Independent read-only audit of the pinned exploration opening."""
import hashlib
import json
import pathlib
import subprocess

ROOT = pathlib.Path(__file__).resolve().parents[3]
OPENING = "c27a36d6e3f47a2b4c7bb017774cbe5df30abdc2"
CYCLE = "ops/research-team/cycles/2026-09-09-exploration"


def git(*args):
    return subprocess.check_output(["git", "-C", str(ROOT), *args])


def blob(path, revision=OPENING):
    return git("show", f"{revision}:{path}")


def main():
    opening = json.loads(blob(f"{CYCLE}/OPENING_STATE.json"))
    manifest = json.loads(blob(f"{CYCLE}/SOURCE_MANIFEST.json"))
    latest_path = "ops/research-team/cycles/2026-09-09-saturation-injectivity/CLOSING_STATE.json"
    latest = json.loads(blob(latest_path))
    legacy = json.loads(blob("ai/omreal/data/CANONICAL_RESEARCH_STATE_V11.json"))
    ledger = json.loads(blob("ai/omreal/data/DIAG3_RESEARCH_DECISION_LEDGER.json"))
    assert opening["base_revision"] == manifest["base_revision"]
    assert opening["base_tree"] == manifest["base_tree"]
    assert git("rev-parse", f'{opening["base_revision"]}^{{tree}}').decode().strip() == opening["base_tree"]
    assert git("rev-parse", f"{OPENING}^").decode().strip() == opening["base_revision"]
    pins = {}
    for path, expected in manifest["sha256"].items():
        at_opening = hashlib.sha256(blob(path)).hexdigest()
        at_base = hashlib.sha256(blob(path, opening["base_revision"])).hexdigest()
        working = hashlib.sha256((ROOT / path).read_bytes()).hexdigest()
        assert at_opening == at_base == working == expected, path
        pins[path] = expected
    assert latest["ledger"] == legacy["theorem"]["score"] == ledger["theorem"]["score"] == opening["ledger"] == "2/9"
    assert latest["proved_diagonals"] == [1, 2]
    assert opening["proof_distance"] == latest["closing_proof_distance"]
    assert len(latest["open_obligations"]) == opening["proof_distance"][3] == 7
    assert latest["pair_global_coverage"] == latest["pair_residual"] == "UNKNOWN"
    counts = latest["source_counts"]
    assert counts["total"] - counts["settled"] == counts["residual"] == 1162302
    assert counts["is_component_denominator"] is False
    assert opening["user_authorized_discovery_without_complete_global_architecture"] is True
    assert opening["github_mode"] == "READ_ONLY"
    print(json.dumps({
        "verdict": "READY_FOR_FROZEN_CANDIDATES",
        "opening_revision": OPENING,
        "opening_tree": git("rev-parse", f"{OPENING}^{{tree}}").decode().strip(),
        "base_revision": opening["base_revision"],
        "base_tree": opening["base_tree"],
        "source_sha256": pins,
        "latest_authority": latest_path,
        "ledger": opening["ledger"],
        "proof_distance": opening["proof_distance"],
        "legacy_v11_streaks": legacy["proof_distance"]["current_vector"][-2:],
        "source_counts": counts,
        "global_pair_coverage": "UNKNOWN",
        "global_component_denominator": "UNKNOWN",
        "discovery_authorized_without_complete_global_proof_architecture": True,
        "candidate_promotion_review": "PENDING",
        "archive_reassembly": "COORDINATOR_REPORTED; NOT INDEPENDENTLY REPEATED",
        "producer_acceptance_imports": []
    }, indent=2))


if __name__ == "__main__":
    main()
