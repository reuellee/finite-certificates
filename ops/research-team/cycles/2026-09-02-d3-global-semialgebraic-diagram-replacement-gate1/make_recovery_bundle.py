#!/usr/bin/env python3
"""Create and mirror a complete-history recovery bundle for the final close."""

from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import uuid


REPO = Path(__file__).resolve().parents[4]
EXPECTED_REPO = Path(r"E:\Projects\9DVL Research\finite-certificates")
OUTPUT_ROOT = Path(r"E:\Projects\9DVL Research\outputs")
MIRROR_ROOT = Path(r"G:\My Drive\Projects\research-backups")
BRANCH = "research/local-d3-global-semialgebraic-replacement-gate1-20260902"


def run(*args: str) -> str:
    completed = subprocess.run(
        args,
        cwd=REPO,
        check=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
    )
    return completed.stdout.strip()


def digest(path: Path) -> str:
    hasher = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            hasher.update(chunk)
    return hasher.hexdigest()


def main() -> None:
    if REPO != EXPECTED_REPO.resolve():
        raise SystemExit(f"refusing unexpected repository root: {REPO}")
    if run("git", "status", "--porcelain"):
        raise SystemExit("refusing to bundle a dirty worktree")
    if run("git", "branch", "--show-current") != BRANCH:
        raise SystemExit("refusing unexpected branch")

    commit = run("git", "rev-parse", "HEAD")
    tree = run("git", "show", "-s", "--format=%T", "HEAD")
    stem = f"9dvl-d3-global-srep-gate1-{commit[:7]}-20260902"
    bundle = (OUTPUT_ROOT / f"{stem}.bundle").resolve()
    manifest = (OUTPUT_ROOT / f"{stem}-manifest.json").resolve()
    mirror_bundle = (MIRROR_ROOT / bundle.name).resolve()
    mirror_manifest = (MIRROR_ROOT / manifest.name).resolve()

    if bundle.parent != OUTPUT_ROOT.resolve() or manifest.parent != OUTPUT_ROOT.resolve():
        raise SystemExit("refusing output path outside the authorized output root")
    if mirror_bundle.parent != MIRROR_ROOT.resolve() or mirror_manifest.parent != MIRROR_ROOT.resolve():
        raise SystemExit("refusing mirror path outside the authorized mirror root")
    for target in (bundle, manifest, mirror_bundle, mirror_manifest):
        if target.exists():
            raise SystemExit(f"refusing to overwrite existing recovery artifact: {target}")

    OUTPUT_ROOT.mkdir(parents=True, exist_ok=True)
    MIRROR_ROOT.mkdir(parents=True, exist_ok=True)
    nonce = uuid.uuid4().hex
    temp_bundle = (OUTPUT_ROOT / f".{bundle.name}.{nonce}.tmp").resolve()
    temp_manifest = (OUTPUT_ROOT / f".{manifest.name}.{nonce}.tmp").resolve()
    temp_mirror_bundle = (MIRROR_ROOT / f".{bundle.name}.{nonce}.tmp").resolve()
    temp_mirror_manifest = (MIRROR_ROOT / f".{manifest.name}.{nonce}.tmp").resolve()
    temps = (temp_bundle, temp_manifest, temp_mirror_bundle, temp_mirror_manifest)
    finals = (bundle, manifest, mirror_bundle, mirror_manifest)
    for target in temps:
        if target.parent not in (OUTPUT_ROOT.resolve(), MIRROR_ROOT.resolve()):
            raise SystemExit(f"refusing temporary path outside authorized roots: {target}")
        if target.exists():
            raise SystemExit(f"refusing unexpected temporary collision: {target}")

    published: list[Path] = []
    try:
        # BRANCH is checked before and after creation; list-heads must bind the
        # bundle's advertised branch ref to the exact commit captured above.
        require_branch_commit = run("git", "rev-parse", BRANCH)
        if require_branch_commit != commit:
            raise RuntimeError("branch moved before bundle creation")
        run("git", "bundle", "create", str(temp_bundle), BRANCH)
        verify_output = run("git", "bundle", "verify", str(temp_bundle))
        if "complete history" not in verify_output.lower():
            raise RuntimeError("git bundle verify did not certify complete history")
        list_heads = run("git", "bundle", "list-heads", str(temp_bundle))
        expected_head = f"{commit} refs/heads/{BRANCH}"
        if expected_head not in list_heads.splitlines():
            raise RuntimeError("bundle does not advertise the captured branch commit")
        if run("git", "rev-parse", "HEAD") != commit or run("git", "rev-parse", BRANCH) != commit:
            raise RuntimeError("HEAD or branch moved during bundle creation")

        bundle_sha = digest(temp_bundle)
        bundle_bytes = temp_bundle.stat().st_size
        shutil.copy2(temp_bundle, temp_mirror_bundle)
        if temp_mirror_bundle.stat().st_size != bundle_bytes or digest(temp_mirror_bundle) != bundle_sha:
            raise RuntimeError("temporary mirror bundle verification failed")

        # The true flag is written only to temporary manifests.  Those bytes
        # are mirrored and checked before any final artifact name is published.
        record = {
            "format": "d3-global-srep-recovery-manifest-v1",
            "cycle_id": "2026-09-02-d3-global-semialgebraic-diagram-replacement-gate1",
            "branch": BRANCH,
            "commit": commit,
            "tree": tree,
            "bundle": {
                "local_path": str(bundle),
                "mirror_path": str(mirror_bundle),
                "bytes": bundle_bytes,
                "sha256": bundle_sha,
                "advertised_head": expected_head,
                "git_bundle_verify": "PASS_COMPLETE_HISTORY",
            },
            "manifest_mirror_verified_after_write": True,
            "github_write": False,
            "google_drive_connector_used": False,
        }
        temp_manifest.write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8")
        shutil.copy2(temp_manifest, temp_mirror_manifest)
        manifest_sha = digest(temp_manifest)
        if digest(temp_mirror_manifest) != manifest_sha:
            raise RuntimeError("temporary mirror manifest verification failed")

        # Atomic renames occur within each volume.  If any publication or
        # final verification fails, only the exact artifacts from this run
        # are removed, leaving the command safely rerunnable.
        for temporary, final in (
            (temp_bundle, bundle),
            (temp_mirror_bundle, mirror_bundle),
            (temp_manifest, manifest),
            (temp_mirror_manifest, mirror_manifest),
        ):
            # os.rename is intentionally non-overwriting on the Windows host;
            # it cannot replace a final artifact created by another process
            # after the initial existence check.
            os.rename(temporary, final)
            published.append(final)

        if bundle.stat().st_size != bundle_bytes or digest(bundle) != bundle_sha:
            raise RuntimeError("published local bundle verification failed")
        if mirror_bundle.stat().st_size != bundle_bytes or digest(mirror_bundle) != bundle_sha:
            raise RuntimeError("published mirror bundle verification failed")
        if digest(manifest) != manifest_sha or digest(mirror_manifest) != manifest_sha:
            raise RuntimeError("published manifest verification failed")
        if run("git", "rev-parse", "HEAD") != commit:
            raise RuntimeError("HEAD moved before recovery publication completed")
    except BaseException:
        for target in (*temps, *published):
            if target.parent in (OUTPUT_ROOT.resolve(), MIRROR_ROOT.resolve()):
                target.unlink(missing_ok=True)
        raise

    print(json.dumps({
        "commit": commit,
        "tree": tree,
        "bundle": str(bundle),
        "mirror_bundle": str(mirror_bundle),
        "bytes": bundle_bytes,
        "sha256": bundle_sha,
        "manifest": str(manifest),
        "mirror_manifest": str(mirror_manifest),
        "bundle_verify": record["bundle"]["git_bundle_verify"],
        "manifest_sha256": manifest_sha,
    }, indent=2))


if __name__ == "__main__":
    main()
