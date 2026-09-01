#!/usr/bin/env python3
"""Independent path attack on the two D9 CEGAR separator claims."""

from __future__ import annotations

from copy import deepcopy
import hashlib
import json
from pathlib import Path
import subprocess
import sys


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
RESULT = HERE / "RESULT.json"

PINS = {
    "ai/omreal/data/ninth_candidate_12_37_path.npz": "8db38e00d9bf8701558c27cd4ede3e024db8953ea3ef9873bf0b4fc65ad6bcda",
    "ai/omreal/data/ninth_candidate_37_176_path.npz": "3c37c3c0d5de159bec9d48eeaaf57bccbe07c2f3aeb0ede9d4b1ddbae2bd3507",
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


def replay(arguments: list[str], endpoint_marker: str, segment_marker: str) -> None:
    process = subprocess.run(
        [sys.executable, "-u", *arguments], cwd=ROOT,
        text=True, capture_output=True,
    )
    require(process.returncode == 0, f"path replay failed: {process.stderr[-1000:]}")
    require(endpoint_marker in process.stdout, "path endpoint marker")
    require(segment_marker in process.stdout, "path segment marker")
    require("SCOPE: this refutes only the sampled separator candidate" in process.stdout,
            "path scope marker")


def validate(candidate: dict) -> None:
    require(candidate["format"] == "d9-fixed-domain-cegar-falsifier-result-v1", "format")
    require(candidate["classification"] == "TWO_EXACT_PATH_REPAIRS_AND_GLOBAL_SCOPE_NULL", "classification")
    require(candidate["exact_path_repairs"] == 2, "path repair count")
    require(candidate["path_segments"] == 45522, "path segment count")
    require(candidate["source_realized_counterexamples"] == 0, "counterexample count")
    require(candidate["complete_fixed_domain_candidate_generator"] is False, "generator scope")
    require(candidate["global_common_feasibility_connectivity"] == "UNPROVED", "connectivity scope")
    require(candidate["theorem_ledger"] == "2/9", "ledger")
    require(candidate["ledger_change_recommended"] == "none", "ledger delta")
    require(candidate["github_write"] is False, "GitHub authority")


def hostile_mutations(stored: dict) -> None:
    mutations = []
    candidate = deepcopy(stored); candidate["classification"] = "D9_COUNTEREXAMPLE"; mutations.append((candidate, "classification"))
    candidate = deepcopy(stored); candidate["exact_path_repairs"] = 1; mutations.append((candidate, "path repair count"))
    candidate = deepcopy(stored); candidate["source_realized_counterexamples"] = 1; mutations.append((candidate, "counterexample count"))
    candidate = deepcopy(stored); candidate["complete_fixed_domain_candidate_generator"] = True; mutations.append((candidate, "generator scope"))
    candidate = deepcopy(stored); candidate["global_common_feasibility_connectivity"] = "PROVED"; mutations.append((candidate, "connectivity scope"))
    candidate = deepcopy(stored); candidate["theorem_ledger"] = "3/9"; mutations.append((candidate, "ledger"))
    candidate = deepcopy(stored); candidate["github_write"] = True; mutations.append((candidate, "GitHub authority"))
    for candidate, marker in mutations:
        try:
            validate(candidate)
        except Reject as error:
            require(marker in str(error), f"wrong hostile rejection: {error}")
            continue
        raise Reject(f"hostile mutation accepted: {marker}")


def main() -> None:
    for path, expected in PINS.items():
        require(sha256(ROOT / path) == expected, f"source pin {path}")
    replay(
        ["ai/omreal/verify_ninth_candidate_path.py"],
        "charts 12 and 37 lie in one component of F_S",
        "exact 3009 segment rational bridge",
    )
    replay(
        ["ai/omreal/verify_ninth_candidate_generic.py", "path",
         "ai/omreal/data/ninth_candidate_37_176_path.npz"],
        "charts 37 and 176 lie in one component of F_S",
        "exact 3009 segment rational bridge",
    )
    result = json.loads(RESULT.read_text(encoding="utf-8"))
    validate(result)
    hostile_mutations(result)
    print("PASS D9 fixed-domain CEGAR falsifier")
    print("separator_claims_refuted=2 exact_path_segments=45522")
    print("hostile_mutations=7 ledger=2/9 global_connectivity=UNPROVED")


if __name__ == "__main__":
    main()
