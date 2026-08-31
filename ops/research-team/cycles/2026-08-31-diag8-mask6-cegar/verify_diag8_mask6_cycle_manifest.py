#!/usr/bin/env python3
"""Fail-closed source and scope audit for the D8 mask-6 CEGAR cycle."""

from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
MANIFEST = HERE / "SOURCE_MANIFEST.json"
FORMAT = "diag8-mask6-cegar-cycle-source-manifest-v2"
CONSEQUENCE = (
    "one globally proper pairwise-incomparable parent-860 eight-family has "
    "an exact singular disk bounded by the named mask-6 loop"
)
NONCONSEQUENCES = {
    "no parent-860 coverage",
    "no universal eight-family statement",
    "no diagonal-eight proof",
    "no change from the 2/9 theorem ledger",
}


class Reject(AssertionError):
    pass


def require(condition, message):
    if not condition:
        raise Reject(message)


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def audit_digest_map(mapping):
    require(mapping, "empty digest map")
    for relative, expected in mapping.items():
        require(len(expected) == 64, f"digest length: {relative}")
        path = ROOT / relative
        require(path.is_file(), f"missing source: {relative}")
        require(sha256(path) == expected, f"source digest moved: {relative}")


def validate(manifest, check_files=True):
    require(
        set(manifest)
        == {
            "format", "cycle_id", "canonical_commit", "canonical_tree",
            "opening_authority_sha256", "cycle_contract_sha256",
            "accepted_track_sha256", "mathematical_certificate_sha256",
            "successor_state_sha256", "literature", "exact_consequence",
            "nonconsequences",
        },
        "manifest field census",
    )
    require(manifest["format"] == FORMAT, "format")
    require(manifest["cycle_id"] == "2026-08-31-diag8-mask6-cegar", "cycle")
    require(manifest["canonical_commit"] == "6c7f52b43632072100b67e5f0a9b6221df14d620", "canonical commit")
    require(manifest["canonical_tree"] == "60866cb78e8aea3259cf376a4420e5370ab8c010", "canonical tree")
    require(manifest["exact_consequence"] == CONSEQUENCE, "consequence")
    require(set(manifest["nonconsequences"]) == NONCONSEQUENCES, "scope")
    literature = manifest["literature"]
    require(len(literature) == 2, "literature census")
    require(literature[0]["url"] == "https://link.springer.com/chapter/10.1007/10722167_15", "CEGAR source")
    require("no imported mathematical theorem" in literature[0]["use"], "CEGAR role")
    require(literature[1]["use"].endswith("not used in this cycle's proof"), "duality role")
    if check_files:
        for key in (
            "opening_authority_sha256", "cycle_contract_sha256",
            "accepted_track_sha256", "mathematical_certificate_sha256",
            "successor_state_sha256",
        ):
            audit_digest_map(manifest[key])


def hostile_canaries(manifest):
    mutations = []
    candidate = copy.deepcopy(manifest)
    candidate["canonical_commit"] = "0" * 40
    mutations.append(("commit", candidate))
    candidate = copy.deepcopy(manifest)
    candidate["exact_consequence"] = "diagonal eight proved"
    mutations.append(("consequence", candidate))
    candidate = copy.deepcopy(manifest)
    candidate["nonconsequences"].remove("no diagonal-eight proof")
    mutations.append(("promotion", candidate))
    candidate = copy.deepcopy(manifest)
    candidate["literature"][0]["use"] = "imported theorem"
    mutations.append(("analogy", candidate))
    candidate = copy.deepcopy(manifest)
    del candidate["opening_authority_sha256"]
    mutations.append(("field", candidate))
    rejected = []
    for name, candidate in mutations:
        try:
            validate(candidate, check_files=False)
        except (KeyError, Reject):
            rejected.append(name)
        else:
            raise Reject(f"hostile canary accepted: {name}")
    return tuple(rejected)


def main():
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    validate(manifest)
    rejected = hostile_canaries(manifest)
    print("PASS D8 mask-6 cycle source manifest")
    print("PASS opening authority, contracts, track results, certificates, and successor state")
    print("PASS CEGAR is method-only; exact consequence remains bounded")
    print("PASS hostile manifest canaries:", len(rejected), "/", len(rejected))


if __name__ == "__main__":
    main()
