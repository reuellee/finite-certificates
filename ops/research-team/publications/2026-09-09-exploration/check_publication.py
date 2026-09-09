#!/usr/bin/env python3
"""Check publication scope and unchanged reviewed research bytes."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import subprocess

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
PREFIX = "ops/research-team/publications/2026-09-09-exploration/"
ADAPTERS = {"README.md", "run_all.py", "ai/omreal/verify_run_all_ci_shards.py",
            ".github/workflows/verify.yml"}


def main() -> None:
    manifest = json.loads((HERE / "provenance/EVIDENCE_MANIFEST.json").read_text())
    reviewed = manifest["reviewed_commit"]
    changed = subprocess.check_output(
        ["git", "diff", "--name-only", reviewed, "--"], cwd=ROOT, text=True).splitlines()
    assert all(path in ADAPTERS or path.startswith(PREFIX) for path in changed), changed
    checked = 0
    for entry in manifest["research_files"]:
        path = entry["path"]
        if path in ADAPTERS:
            continue
        data = (ROOT / path).read_bytes()
        assert len(data) == entry["size_bytes"], path
        assert hashlib.sha256(data).hexdigest() == entry["sha256"], path
        checked += 1
    state = json.loads((ROOT / "ops/research-team/cycles/2026-09-09-exploration/CLOSING_STATE.json").read_text())
    assert state["ledger"] == "2/9" and state["original_obligations_closed"] == 0
    assert len(state["open_obligations"]) == 7
    assert set(state["open_obligations"].values()) == {"INCONCLUSIVE"}
    assert state["source_counts"] == {"delta": 0, "is_component_denominator": False,
        "residual": 1162302, "settled": 77940147, "total": 79102449}
    assert state["verdict"] == "ACCEPT_SCOPED_AUXILIARY_RESULTS_ONLY"
    print(f"PASS publication scope; {checked} research files unchanged; ledger 2/9")


if __name__ == "__main__":
    main()
