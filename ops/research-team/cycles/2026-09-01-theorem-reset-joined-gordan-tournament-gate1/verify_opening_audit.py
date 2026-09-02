#!/usr/bin/env python3
from __future__ import annotations

from copy import deepcopy
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[4]
HERE = Path(__file__).resolve().parent
BASE = "3689b5344dfed38468639d0e92b48f0b5fc4ebc8"
TREE = "ef14ccd9b844dae5e9b535310122251ca0e86bfb"
TRIPLE_DIGEST = "a76a7c2cd6631c2d9724b450540bec7f3be6c106a41ae41f1736bbd2755a5ca4"


def require(condition: bool, label: str) -> None:
    if not condition:
        raise AssertionError(label)


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def check(data: dict) -> None:
    require(data["base_revision"] == BASE, "base revision")
    require(data["base_tree"] == TREE, "base tree")
    require(data["opening_ledger"] == "2/9", "opening ledger")
    require(data["goal_ledger"] == "3/9", "goal ledger")
    require(data["opening_verdict"] == "PIVOT", "opening verdict")
    require(data["selected_construction_count"] == 0, "zero construction targets")
    distance = data["proof_distance"]
    expected = ("2/9", 1, 7, "UNKNOWN", "UNKNOWN", 4, 7)
    actual = (
        distance["opening_score"], distance["score_deficit"],
        distance["open_load_bearing_obligations"],
        distance["certified_exhaustive_residual"], distance["global_coverage"],
        distance["same_blocker_streak"], distance["zero_ledger_streak"],
    )
    require(actual == expected, "opening vector")
    triple = data["triple_global_accounting"]
    require(triple["settled_orbits"] + triple["residual_orbits"] == triple["source_orbits"], "triple partition")
    require((triple["settled_orbits"], triple["source_orbits"]) == (77_940_147, 79_102_449), "triple coverage")
    require(triple["source_order_residual_semantic_sha256"] == TRIPLE_DIGEST, "triple semantic digest")
    require(triple["globally_attached_source_denominator"] is True, "triple source attachment")
    require(triple["triple_only_closure_promotes_d3"] is False, "triple-only nonpromotion")
    joined = data["joined_gordan_clause_baseline"]
    require(joined["denominator"] == 10 and len(joined["clauses"]) == 10, "ten joined clauses")
    require(len(set(joined["clauses"])) == 10, "unique joined clauses")
    require(joined["provisional_universally_proved"] == ["(0)", "(1)", "(2)"], "provisional 3/10")
    require(joined["independent_rebaseline_required"] is True, "rebaseline gate")
    require(joined["end_to_end_d3_denominator"] is False, "no false D3 denominator")
    require(joined["critical_missing_clause"] == "(1,0,0)", "critical mixed clause")
    routes = data["route_tournament"]
    require(len(routes) == 6, "six theorem routes")
    require(all(len(row["scores"]) == 8 for row in routes), "all protocol scores")
    require(all(not row["construction_ready"] for row in routes), "no route ready")
    obligations = data["end_to_end_obligations"]
    require(len(obligations) == 7, "seven load-bearing obligations")
    require(sum(row["id"] == "diag3_triple_hc0" and row["residual"] == 1_162_302 for row in obligations) == 1, "triple obligation")
    for relative, expected_sha in data["pins"].items():
        require(sha(ROOT / relative) == expected_sha, f"pin {relative}")


def main() -> None:
    data = json.loads((HERE / "OPENING_AUDIT.json").read_text(encoding="utf-8"))
    check(data)
    env = os.environ.copy()
    env.update({"GIT_CONFIG_COUNT": "1", "GIT_CONFIG_KEY_0": "safe.directory", "GIT_CONFIG_VALUE_0": str(ROOT)})
    head = subprocess.run(["git", "rev-parse", BASE], cwd=ROOT, env=env, check=True, capture_output=True, text=True).stdout.strip()
    tree = subprocess.run(["git", "rev-parse", f"{BASE}^{{tree}}"], cwd=ROOT, env=env, check=True, capture_output=True, text=True).stdout.strip()
    require(head == BASE and tree == TREE, "immutable base identity")
    protocol = subprocess.run([sys.executable, "ops/research-team/verify_cycle_protocol.py"], cwd=ROOT, env=env, check=True, capture_output=True, text=True)
    require("PASS research-cycle strategy/convergence/storage/publication protocol" in protocol.stdout, "protocol replay")
    mutations = []
    for mutate in (
        lambda x: x.__setitem__("base_tree", "0" * 40),
        lambda x: x.__setitem__("opening_ledger", "3/9"),
        lambda x: x.__setitem__("selected_construction_count", 1),
        lambda x: x["proof_distance"].__setitem__("same_blocker_streak", 3),
        lambda x: x["proof_distance"].__setitem__("zero_ledger_streak", 6),
        lambda x: x["triple_global_accounting"].__setitem__("residual_orbits", 1_162_301),
        lambda x: x["triple_global_accounting"].__setitem__("triple_only_closure_promotes_d3", True),
        lambda x: x["joined_gordan_clause_baseline"].__setitem__("denominator", 9),
        lambda x: x["joined_gordan_clause_baseline"].__setitem__("end_to_end_d3_denominator", True),
        lambda x: x["route_tournament"].pop(),
        lambda x: x["end_to_end_obligations"].pop(),
        lambda x: x["pins"].__setitem__("ops/research-team/PROTOCOL.md", "0" * 64),
    ):
        candidate = deepcopy(data)
        mutate(candidate)
        mutations.append(candidate)
    rejected = 0
    for candidate in mutations:
        try:
            check(candidate)
        except (AssertionError, KeyError):
            rejected += 1
    require(rejected == len(mutations), "hostile mutations")
    print("PASS theorem-reset opening audit")
    print(f"PASS hostile mutations rejected {rejected}/{len(mutations)}")
    print("OPEN vector 2/9 deficit=1 obligations=7 pair_residual=UNKNOWN pair_coverage=UNKNOWN streaks=4,7")
    print("TRIPLE coverage=77940147/79102449 residual=1162302 attached-source; closing alone does not promote D3")
    print("JOINED provisional=3/10 requires independent universal rebaseline; not end-to-end D3")
    print("CONSTRUCTION targets=0")


if __name__ == "__main__":
    main()
