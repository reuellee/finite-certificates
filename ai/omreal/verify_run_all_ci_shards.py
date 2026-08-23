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
EXPECTED_DELEGATED = {
    "verify_diag2_escape_set_atlas178.py",
    "verify_diag2_pivot_49_pair_saturation.py",
    "verify_diag2_pivot_all_pair_fibers.py",
    "verify_diag3_ordered_root_atlas178.py",
    "verify_diag3_pair_parent_source_block_labels.py",
}
EXPECTED_EXTERNAL = {"verify_diag3_triple_common_scaling_no_go.py"}


def literal_set(tree, name):
    for node in tree.body:
        if isinstance(node, ast.Assign):
            if any(isinstance(target, ast.Name) and target.id == name for target in node.targets):
                return set(ast.literal_eval(node.value))
    raise AssertionError(f"missing literal set {name}")


def literal_dict(tree, name):
    for node in tree.body:
        if isinstance(node, ast.Assign):
            if any(isinstance(target, ast.Name) and target.id == name for target in node.targets):
                return dict(ast.literal_eval(node.value))
    raise AssertionError(f"missing literal dict {name}")


def direct_selected():
    tree = ast.parse(RUN_ALL.read_text(encoding="utf-8"))
    delegated = literal_set(tree, "CI_DELEGATED")
    external = set(literal_dict(tree, "EXTERNAL_INPUT"))
    discovered = {
        path.relative_to(ROOT).as_posix()
        for path in ROOT.rglob("verify_*.py")
        if path.is_file()
    }
    selected = {
        path
        for path in discovered
        if Path(path).name not in delegated | external
    }
    return discovered, selected, delegated, external


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
    discovered, selected, delegated, external = direct_selected()
    if delegated != EXPECTED_DELEGATED or external != EXPECTED_EXTERNAL:
        raise AssertionError("nonsharded verifier census changed")
    if len(discovered - selected) != len(delegated | external):
        raise AssertionError("delegated verifier census changed")
    digests = {}
    for count in COUNTS:
        payload = manifest(count)
        audit(payload, selected, count)
        digests[str(count)] = payload["partition_sha256"]
    print("PASS deterministic shard manifests", digests)
    print("PASS exact union/disjointness", len(selected), "selected verifiers")
    print("PASS delegated verifier census", len(delegated))
    print("PASS explicit external-input verifier census", len(external))


if __name__ == "__main__":
    main()
