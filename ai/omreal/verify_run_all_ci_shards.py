#!/usr/bin/env python3
"""Independent union/disjointness audit for deterministic CI verifier shards."""

from __future__ import annotations

import ast
import hashlib
import json
from pathlib import Path
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[2]
RUN_ALL = ROOT / "run_all.py"
COUNTS = (1, 2, 4, 7)


def literal_set(tree, name):
    for node in tree.body:
        if isinstance(node, ast.Assign):
            if any(isinstance(target, ast.Name) and target.id == name for target in node.targets):
                return set(ast.literal_eval(node.value))
    raise AssertionError(f"missing literal set {name}")


def direct_selected():
    tree = ast.parse(RUN_ALL.read_text(encoding="utf-8"))
    delegated = literal_set(tree, "CI_DELEGATED")
    discovered = {
        path.relative_to(ROOT).as_posix()
        for path in ROOT.rglob("verify_*.py")
        if path.is_file()
    }
    return discovered, {
        path for path in discovered if Path(path).name not in delegated
    }


def manifest(count):
    command = [
        sys.executable,
        str(RUN_ALL),
        "--ci-delegated",
        "--list-shards",
        str(count),
        "--json",
    ]
    first = subprocess.check_output(command, cwd=ROOT, text=True)
    second = subprocess.check_output(command, cwd=ROOT, text=True)
    if first != second:
        raise AssertionError("shard manifest is nondeterministic")
    return json.loads(first)


def audit(payload, expected, count):
    if payload["format"] != "finite-certificates-verifier-shards-v1":
        raise AssertionError("wrong shard manifest format")
    if payload["shard_count"] != count or len(payload["shards"]) != count:
        raise AssertionError("wrong shard count")
    flat = [path for bucket in payload["shards"] for path in bucket]
    if len(flat) != len(set(flat)):
        raise AssertionError("verifier occurs in more than one shard")
    if set(flat) != expected:
        raise AssertionError("shard union does not equal selected verifier universe")
    if payload["selected_verifier_count"] != len(expected):
        raise AssertionError("selected verifier count changed")
    if any(bucket != sorted(bucket) for bucket in payload["shards"]):
        raise AssertionError("shard paths are not canonical")
    canonical = "".join(
        f"{index}\0{path}\n"
        for index, bucket in enumerate(payload["shards"])
        for path in bucket
    ).encode("utf-8")
    if hashlib.sha256(canonical).hexdigest() != payload["partition_sha256"]:
        raise AssertionError("partition digest mismatch")


def main():
    discovered, selected = direct_selected()
    if len(discovered - selected) != 3:
        raise AssertionError("delegated verifier census changed")
    digests = {}
    for count in COUNTS:
        payload = manifest(count)
        audit(payload, selected, count)
        digests[str(count)] = payload["partition_sha256"]
    print("PASS deterministic shard manifests", digests)
    print("PASS exact union/disjointness", len(selected), "selected verifiers")
    print("PASS delegated verifier census", len(discovered - selected))


if __name__ == "__main__":
    main()
