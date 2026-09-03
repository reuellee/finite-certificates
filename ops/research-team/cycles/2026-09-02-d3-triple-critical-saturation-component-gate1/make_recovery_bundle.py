#!/usr/bin/env python3
"""Create and optionally mirror the final local recovery bundle."""

from __future__ import annotations

import argparse
from hashlib import sha256
import json
from pathlib import Path
import shutil
import subprocess


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
OUTPUT_ROOT = ROOT.parent / "outputs"
MIRROR_ROOT = Path(r"G:\My Drive\Projects\research-backups")
DATE = "20260903"


def git(*arguments: str) -> str:
    return subprocess.check_output(["git", *arguments], cwd=ROOT, text=True).strip()


def sha(path: Path) -> str:
    return sha256(path.read_bytes()).hexdigest()


def verify_copy(source: Path, target: Path) -> None:
    if source.stat().st_size != target.stat().st_size or sha(source) != sha(target):
        raise AssertionError(f"mirror verification failed: {target}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--no-mirror", action="store_true")
    arguments = parser.parse_args()
    if git("status", "--porcelain"):
        raise AssertionError("recovery bundle requires a clean working tree")
    commit = git("rev-parse", "HEAD")
    tree = git("rev-parse", "HEAD^{tree}")
    short = commit[:7]
    stem = f"9dvl-d3-triple-critical-saturation-gate1-{short}-{DATE}"
    OUTPUT_ROOT.mkdir(parents=True, exist_ok=True)
    bundle = OUTPUT_ROOT / f"{stem}.bundle"
    manifest = OUTPUT_ROOT / f"{stem}-manifest.json"
    if bundle.exists() or manifest.exists():
        raise FileExistsError(f"recovery output already exists for {stem}")
    subprocess.run(["git", "bundle", "create", str(bundle), "--all"], cwd=ROOT, check=True)
    verification = subprocess.run(
        ["git", "bundle", "verify", str(bundle)], cwd=ROOT, check=True, text=True, capture_output=True
    )
    closing = HERE / "CLOSING_MANIFEST.json"
    verifier = HERE / "verify_closing.py"
    value = {
        "format": "d3-triple-critical-saturation-recovery-manifest-v1",
        "cycle_id": HERE.name,
        "branch": git("branch", "--show-current"),
        "final_commit": commit,
        "final_tree": tree,
        "bundle": {"path": str(bundle), "bytes": bundle.stat().st_size, "sha256": sha(bundle)},
        "closing_manifest": {"path": str(closing), "bytes": closing.stat().st_size, "sha256": sha(closing)},
        "closing_verifier": {"path": str(verifier), "bytes": verifier.stat().st_size, "sha256": sha(verifier)},
        "bundle_verify_stdout": verification.stdout.strip(),
        "bundle_verify_stderr": verification.stderr.strip(),
        "github_write": False,
        "google_drive_connector_used": False,
        "native_mirror": {"attempted": False, "available": MIRROR_ROOT.is_dir()},
    }
    manifest.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="ascii")
    if not arguments.no_mirror and MIRROR_ROOT.is_dir():
        target_bundle = MIRROR_ROOT / bundle.name
        target_manifest = MIRROR_ROOT / manifest.name
        if target_bundle.exists() or target_manifest.exists():
            raise FileExistsError(f"mirror output already exists for {stem}")
        shutil.copy2(bundle, target_bundle)
        shutil.copy2(manifest, target_manifest)
        verify_copy(bundle, target_bundle)
        verify_copy(manifest, target_manifest)
        value["native_mirror"] = {
            "attempted": True,
            "available": True,
            "bundle_path": str(target_bundle),
            "manifest_path": str(target_manifest),
            "bundle_bytes_equal": True,
            "bundle_sha256_equal": True,
            "manifest_bytes_equal_before_record_update": True,
            "manifest_sha256_equal_before_record_update": True,
        }
        manifest.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="ascii")
        shutil.copy2(manifest, target_manifest)
        verify_copy(manifest, target_manifest)
    print(f"BUNDLE {bundle}")
    print(f"MANIFEST {manifest}")
    print(f"COMMIT {commit}")
    print(f"TREE {tree}")
    print(f"SHA256 {sha(bundle)}")


if __name__ == "__main__":
    main()
