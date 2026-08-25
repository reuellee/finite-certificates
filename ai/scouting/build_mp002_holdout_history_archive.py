#!/usr/bin/env python3
"""Package the two pre-observation MP-002 commits as a minimal Git archive."""

from __future__ import annotations

import gzip
from hashlib import sha1
import io
from pathlib import Path
import subprocess
import tarfile
import zlib


HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
OUTPUT = HERE / "data" / "MP002_HOLDOUT_HISTORY.tar.gz"
REGISTRATION_COMMIT = "c818dd8415ffa3c1286f2d3200f93276f10ce98b"
FREEZE_COMMIT = "4ddd987d4f2cbc55459f557fc578ee7dec55806e"


def git(*args):
    return subprocess.run(
        ["git", *args], cwd=REPO, check=True, capture_output=True
    ).stdout


def object_id(revision):
    return git("rev-parse", revision).decode("ascii").strip()


def loose_object(identifier):
    kind = git("cat-file", "-t", identifier).decode("ascii").strip()
    data = git("cat-file", kind, identifier)
    payload = f"{kind} {len(data)}\0".encode("ascii") + data
    if sha1(payload).hexdigest() != identifier:
        raise AssertionError(f"Git object hash mismatch: {identifier}")
    return zlib.compress(payload, level=9)


def main():
    identifiers = {REGISTRATION_COMMIT, FREEZE_COMMIT}
    for commit in (REGISTRATION_COMMIT, FREEZE_COMMIT):
        for suffix in ("^{tree}", ":ai", ":ai/scouting", ":ai/scouting/data"):
            identifiers.add(object_id(commit + suffix))
    for commit, path in (
        (
            REGISTRATION_COMMIT,
            "ai/scouting/data/MP002_BLOCK_ROUTE_TRANSFER_REGISTRATION.json",
        ),
        (REGISTRATION_COMMIT, "ai/scouting/data/PROSPECTING_LEDGER.json"),
        (
            FREEZE_COMMIT,
            "ai/scouting/data/MP002_BLOCK_ROUTE_TRANSFER_PREDICTION.json",
        ),
        (FREEZE_COMMIT, "ai/scouting/explore_block_route_transfer.py"),
    ):
        identifiers.add(object_id(f"{commit}:{path}"))

    files = {
        "HEAD": b"ref: refs/heads/mp002-holdout-freeze\n",
        "config": (
            b"[core]\n"
            b"\trepositoryformatversion = 0\n"
            b"\tbare = true\n"
        ),
        "refs/heads/mp002-holdout-freeze": (FREEZE_COMMIT + "\n").encode(
            "ascii"
        ),
        "shallow": (REGISTRATION_COMMIT + "\n").encode("ascii"),
    }
    for identifier in identifiers:
        files[f"objects/{identifier[:2]}/{identifier[2:]}"] = loose_object(
            identifier
        )

    payload = io.BytesIO()
    with tarfile.open(fileobj=payload, mode="w", format=tarfile.PAX_FORMAT) as archive:
        for name, data in sorted(files.items()):
            info = tarfile.TarInfo(name)
            info.size = len(data)
            info.mode = 0o644
            info.mtime = 0
            info.uid = info.gid = 0
            info.uname = info.gname = ""
            archive.addfile(info, io.BytesIO(data))
    OUTPUT.write_bytes(
        gzip.compress(payload.getvalue(), compresslevel=9, mtime=0)
    )
    print("WROTE", OUTPUT, "OBJECTS", len(identifiers))


if __name__ == "__main__":
    main()
