#!/usr/bin/env python3
"""Independent fail-closed audit of the JSON-to-Lean node-data bridge."""

from __future__ import annotations

import ast
import copy
from hashlib import sha256
import json
from pathlib import Path
import re


HERE = Path(__file__).resolve().parent
CERTIFICATE = HERE / "data" / "DIAG3_PAIR_MASTER_CLOSURE_NODE_CANARY.json"
LEAN_DATA = HERE.parent.parent / "formal" / "lean" / "NineDVLFormal" / "GeneratedNodeData.lean"

CELL_TO_SIMPLEX = {
    "v": [0], "p0": [1], "p1": [2], "p2": [3], "p3": [4],
    "w0": [0, 1], "w3": [0, 2], "w1": [0, 3], "w2": [0, 4],
    "b0": [1, 2], "b1": [2, 3], "b2": [3, 4], "b3": [1, 4],
    "c0": [0, 1, 2], "c1": [0, 2, 3], "c2": [0, 3, 4], "c3": [0, 1, 4],
}


class BridgeError(AssertionError):
    pass


def require(condition, message):
    if not condition:
        raise BridgeError(message)


def declarations(source: str) -> dict:
    result = {}
    pattern = re.compile(r"^def (\w+)\s*(?:\([^\n]*\))?\s*:[^:]+:=\s*(.+)$", re.MULTILINE)
    for name, expression in pattern.findall(source):
        translated = re.sub(r"\btrue\b", "True", expression)
        translated = re.sub(r"\bfalse\b", "False", translated)
        result[name] = ast.literal_eval(translated)
    return result


def incidence_matrix(boundary, lower_key, upper_key, entries_key):
    lower = boundary[lower_key]
    upper = boundary[upper_key]
    entries = {(row, column): int(value) for row, column, value in boundary[entries_key]}
    return [[entries.get((row, column), 0) for column in upper] for row in lower]


def validate(record: dict, data: dict, digest: str) -> None:
    require(record["format"] == "diag3-pair-master-closure-certificate-v1", "format")
    require(record["status"] == "LOCAL_EXACT_CANARY", "status")
    require(data["sourceFormat"] == record["format"], "Lean format")
    require(data["sourceStatus"] == record["status"], "Lean status")
    require(data["certificateSha256"] == digest, "certificate byte digest")
    require(data["formatVersion"] == 1, "Lean format version")

    scope = record["scope"]
    require(data["parentIndex"] == scope["parent_index"] == 2599, "parent")
    require(data["support"] == scope["support"] == [15, 15, 15], "support")
    require(scope["local_parameter_coverage"] == "COMPLETE", "JSON local coverage")
    require(scope["global_parameter_coverage"] == "NOT_CLAIMED", "JSON global coverage")
    require(data["localCoverage"] is True, "Lean local coverage")
    require(data["globalCoverage"] is False, "Lean global coverage")

    cell_ids = [cell["id"] for cell in record["cells"]]
    require(len(cell_ids) == len(set(cell_ids)) == 17, "cell census")
    require(set(cell_ids) == set(CELL_TO_SIMPLEX), "cell identifiers")
    require(data["masterCells"] == [CELL_TO_SIMPLEX[item] for item in cell_ids], "cell simplices")
    require(
        data["scopeBoundary"] == [CELL_TO_SIMPLEX[item] for item in record["scope_boundary_subcomplex"]],
        "scope boundary",
    )
    require(
        data["parentInfinity"] == [CELL_TO_SIMPLEX[item] for item in record["parent_infinity_subcomplex"]],
        "parent infinity",
    )

    profiles = record["signature_profile_source"]["profiles"]
    require(
        data["profileCensus"]
        == [(row["feasible_chamber_mask"], row["signature_count"]) for row in profiles],
        "profile census",
    )
    require(sum(count for _profile, count in data["profileCensus"]) == 97_224, "profile universe")

    boundary = record["integral_boundary"]
    require(data["integralD1"] == incidence_matrix(boundary, "c0_basis", "c1_basis", "d1_entries"), "d1")
    require(data["integralD2"] == incidence_matrix(boundary, "c1_basis", "c2_basis", "d2_entries"), "d2")


def assert_rejected(record, data, digest, label):
    try:
        validate(record, data, digest)
    except (BridgeError, KeyError, TypeError, ValueError):
        return
    raise AssertionError(f"hostile bridge mutation was accepted: {label}")


def main() -> None:
    source = CERTIFICATE.read_bytes()
    record = json.loads(source)
    data = declarations(LEAN_DATA.read_text(encoding="utf-8"))
    digest = sha256(source).hexdigest()
    validate(record, data, digest)

    corrupt = copy.deepcopy(data)
    corrupt["globalCoverage"] = True
    assert_rejected(record, corrupt, digest, "promoted global coverage")

    corrupt = copy.deepcopy(record)
    corrupt["scope"]["global_parameter_coverage"] = "COMPLETE"
    assert_rejected(corrupt, data, digest, "promoted JSON global coverage")

    corrupt = copy.deepcopy(record)
    corrupt["scope_boundary_subcomplex"].pop()
    assert_rejected(corrupt, data, digest, "truncated scope boundary")

    corrupt = copy.deepcopy(record)
    corrupt["signature_profile_source"]["profiles"][0]["signature_count"] -= 1
    assert_rejected(corrupt, data, digest, "corrupt profile census")

    corrupt = copy.deepcopy(record)
    corrupt["integral_boundary"]["d2_entries"][0][2] *= -1
    assert_rejected(corrupt, data, digest, "corrupt integral incidence")

    corrupt = copy.deepcopy(data)
    corrupt["certificateSha256"] = "0" * 64
    assert_rejected(record, corrupt, digest, "corrupt byte digest")

    print("PASS independent JSON-to-Lean node-data bridge audit")
    print("PASS exact byte digest, scope, 17 cells, six profiles, and integral incidence")
    print("PASS 6/6 hostile bridge mutations rejected")


if __name__ == "__main__":
    main()
