#!/usr/bin/env python3
"""Import original research commits from the pinned publication bundle."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import subprocess

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
BUNDLE_SHA256 = "22d52dc10d943241ee7dc90c319c9c1d8f995d1c50616e339f0f4b59c044226a"
REVIEWED = "4e9b79480529473889b82048570af3bc1d6b1faf"
TREE = "75f9e2f1622f8123bd520d34ae3359d644c181fd"
PREFIX = "refs/research-evidence/2026-09-09/"


def git(*args: str) -> str:
    return subprocess.check_output(["git", *args], cwd=ROOT, text=True).strip()


def main() -> None:
    manifest = json.loads((HERE / "provenance/EVIDENCE_MANIFEST.json").read_text())
    bundle = ROOT / manifest["bundle"]["path"]
    assert git("rev-parse", "--is-shallow-repository") == "false", "full clone required"
    assert manifest["reviewed_commit"] == REVIEWED and manifest["reviewed_tree"] == TREE
    assert bundle.stat().st_size == manifest["bundle"]["size_bytes"]
    assert hashlib.sha256(bundle.read_bytes()).hexdigest() == BUNDLE_SHA256
    assert manifest["bundle"]["sha256"] == BUNDLE_SHA256
    for commit in manifest["bundle"]["prerequisites"]:
        assert git("cat-file", "-t", commit) == "commit", "missing public ancestor"
    subprocess.run(["git", "bundle", "verify", str(bundle)], cwd=ROOT, check=True,
                   stdout=subprocess.DEVNULL)
    actual = dict(line.split(" ", 1)[::-1] for line in git("bundle", "list-heads", str(bundle)).splitlines())
    expected = {entry["ref"]: entry["commit"] for entry in manifest["bundle"]["refs"]}
    assert actual == expected, "bundle ref census changed"
    subprocess.run(["git", "fetch", "--quiet", "--no-tags", str(bundle),
                    "refs/*:" + PREFIX + "*"], cwd=ROOT, check=True)
    for ref, commit in expected.items():
        assert ref.startswith("refs/")
        assert git("rev-parse", PREFIX + ref[5:]) == commit
    assert git("rev-parse", REVIEWED + "^{tree}") == TREE
    print(f"PASS imported {len(expected)} pinned research refs; reviewed tree {TREE}")


if __name__ == "__main__":
    main()
