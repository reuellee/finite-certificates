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
BASE_TREE = "ef14ccd9b844dae5e9b535310122251ca0e86bfb"
OPENING = "d4f83ffedc13f2fc07a2c8cd39a03cec8550da22"
OPENING_TREE = "97ab517bfe5bf8b3b93e7d604690c4d6a1342c43"
EVIDENCE = "5277886b1171f15b8e486d5e62212515534e5944"
EVIDENCE_TREE = "ed5e6359122bc167898f9d6b8f2c60904ff0125c"
CHECKPOINT = "ebbe79cbc8a2b490ff1d9e77dde1cafb57d8a1e8"
CHECKPOINT_TREE = "b0ee5a5890715704fa10b839979e5100fc7740bb"
OPEN_VECTOR = ["2/9", 1, "diag3_pair_hc1_AND_diag3_triple_hc0", 7, "UNKNOWN", "UNKNOWN", 4, 7]
CLOSE_VECTOR = ["2/9", 1, "diag3_pair_hc1_AND_diag3_triple_hc0", 7, "UNKNOWN", "UNKNOWN", 5, 8]


def require(condition: bool, label: str) -> None:
    if not condition:
        raise AssertionError(label)


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load(name: str) -> dict:
    return json.loads((HERE / name).read_text(encoding="utf-8"))


def validate(checkpoint: dict, closing: dict) -> None:
    require(checkpoint["base_revision"] == closing["base_revision"] == BASE, "base")
    require(checkpoint["base_tree"] == closing["base_tree"] == BASE_TREE, "base tree")
    require(checkpoint["opening_revision"] == closing["opening_revision"] == OPENING, "opening")
    require(checkpoint["opening_tree"] == closing["opening_tree"] == OPENING_TREE, "opening tree")
    require(checkpoint["integrated_lane_head"] == closing["integrated_evidence_revision"] == EVIDENCE, "evidence")
    require(checkpoint["integrated_lane_tree"] == closing["integrated_evidence_tree"] == EVIDENCE_TREE, "evidence tree")
    require(closing["checkpoint_revision"] == CHECKPOINT and closing["checkpoint_tree"] == CHECKPOINT_TREE, "checkpoint revision")
    require(checkpoint["opening_vector"] == checkpoint["checkpoint_vector"] == OPEN_VECTOR, "checkpoint vector")
    require(closing["opening_vector"] == closing["checkpoint_vector"] == OPEN_VECTOR, "closing open/checkpoint vector")
    require(closing["closing_vector"] == CLOSE_VECTOR, "closing vector")
    require(checkpoint["minimum_acceptable_delta_met"] is False, "checkpoint minimum")
    require(checkpoint["minimum_acceptable_delta_reachable_inside_remaining_ceiling"] is False, "checkpoint reachability")
    decision = checkpoint["checkpoint_decision"]
    require(decision["stop_discovery"] is True and decision["resource_ceiling_enlarged"] is False, "midpoint stop")
    require(decision["construction_started"] is False and decision["same_route_continue_allowed"] is False, "no construction/continue")
    require(sum(row["hostile_mutations_rejected"] for row in checkpoint["lane_verdicts"]) == 64, "lane hostile total")
    require(closing["opening_ledger"] == closing["closing_ledger"] == "2/9", "ledger")
    require(closing["ledger_delta"] == "0/9" and closing["theorem_promotion"] == "NONE", "ledger delta")
    require(closing["minimum_acceptable_delta_met"] is False, "minimum delta")
    require(closing["trajectory_classification"] == "STALLED", "trajectory")
    require(closing["overall_handoff"] == "NULL" and closing["tournament_winner"] == "NONE", "overall handoff")
    reset = closing["automatic_strategy_reset"]
    require(reset == {"fired": True, "triggers": ["EIGHT_CONSECUTIVE_ZERO_LEDGER_CYCLES_AT_CLOSE", "FIVE_CYCLE_SAME_BLOCKER_STREAK_AT_CLOSE", "REPEATED_UNKNOWN_PAIR_RESIDUAL_AND_COVERAGE", "PREREGISTERED_DECREASE_UNREACHABLE_AT_MIDPOINT"], "same_route_continue_allowed": False, "action": "STOP"}, "reset")
    triple = closing["triple_global_accounting"]
    require(triple["coverage_opening"] == triple["coverage_closing"] == "77940147/79102449", "triple coverage")
    require(triple["residual_opening"] == triple["residual_closing"] == 1_162_302 and triple["residual_delta"] == 0, "triple residual")
    joined = closing["joined_gordan_accounting"]
    require(joined["formal_face_type_denominator"] == 10, "joined denominator")
    require(joined["opening_universal_coverage"] == joined["closing_universal_coverage"] == "3/10", "joined coverage")
    require(joined["new_universal_clause"] == "NONE", "joined delta")
    require(not joined["globally_attached"] and not joined["end_to_end_d3_denominator"] and not joined["bounded_chain"], "joined scope")
    canary = closing["exact_canary"]
    require((canary["rank_partial_1"], canary["rank_partial_2"], canary["rank_C2"]) == (3, 6, 7), "canary ranks")
    require(canary["relative_homology"] == {"H0": "0", "H1": "0", "H2": "Z"}, "canary homology")
    require(canary["primitive_h2_relation"] == [-1, 1, 1, 1, 1, 1, 1], "primitive relation")
    require(canary["genuine_mixed_block_carrier_nonexistence_proved"] is False and canary["d3_counterexample"] is False, "canary scope")
    routes = closing["route_dispositions"]
    require(len(routes) == 6 and all(len(row["scores"]) == 8 for row in routes), "route scores")
    require([row["handoff"] for row in routes] == ["NULL", "NULL", "NULL", "NEGATIVE", "NULL", "TIMEOUT"], "route handoffs")
    require(all(not row["successor_eligible"] for row in routes), "route eligibility")
    require(len(closing["obligation_delta"]) == 7 and all(row["delta"] in ("UNCHANGED", 0) for row in closing["obligation_delta"]), "obligation delta")
    bar = closing["successor_bar"]
    require(bar["eligible_route_count"] == 0 and bar["selected_construction_target"] == bar["selected_successor"] == "NONE", "successor")
    require(bar["construction_started"] is False, "construction")
    require(closing["storage"] == {"output_root": "E:\\Projects\\9DVL Research\\outputs", "native_g_mirror": "DEFERRED_ACCESS_DENIED_IN_SANDBOX_TO_COORDINATING_USER_CONTEXT", "google_drive_connector_used": False, "approval_requested": False, "github_write": False}, "storage")
    for relative, digest in closing["evidence_pins"].items():
        require(sha(ROOT / relative) == digest, f"evidence pin {relative}")


def replay(relative: str, marker: str, env: dict[str, str]) -> None:
    result = subprocess.run([sys.executable, relative], cwd=ROOT, env=env, check=True, capture_output=True, text=True)
    require(marker in result.stdout, f"replay {relative}")


def main() -> None:
    checkpoint = load("MID_CYCLE_CHECKPOINT.json")
    closing = load("CLOSING_CANDIDATE.json")
    validate(checkpoint, closing)
    env = os.environ.copy()
    env.update({"GIT_CONFIG_COUNT": "1", "GIT_CONFIG_KEY_0": "safe.directory", "GIT_CONFIG_VALUE_0": str(ROOT), "PYTHONDONTWRITEBYTECODE": "1"})
    for revision, tree in ((BASE, BASE_TREE), (OPENING, OPENING_TREE), (EVIDENCE, EVIDENCE_TREE), (CHECKPOINT, CHECKPOINT_TREE)):
        actual = subprocess.run(["git", "rev-parse", f"{revision}^{{tree}}"], cwd=ROOT, env=env, check=True, capture_output=True, text=True).stdout.strip()
        require(actual == tree, f"git tree {revision}")
    replay("ops/research-team/cycles/2026-09-01-theorem-reset-joined-gordan-tournament-gate1/verify_opening_audit.py", "PASS theorem-reset opening audit", env)
    replay("ops/team/theorem-reset-prover-strategy/verify_prover_strategy.py", "PASS 26/26 hostile mutations rejected", env)
    replay("ops/team/theorem-reset-falsifier/verify_falsifier.py", "PASS hostile mutations rejected: 18", env)
    replay("ops/team/theorem-reset-independent-verifier/verify_independent.py", "PASS hostile mutations rejected 20/20", env)
    replay("ops/research-team/verify_cycle_protocol.py", "PASS research-cycle strategy/convergence/storage/publication protocol", env)
    mutations = []
    mutation_fns = (
        lambda c: c.__setitem__("base_tree", "0" * 40),
        lambda c: c.__setitem__("closing_ledger", "3/9"),
        lambda c: c.__setitem__("ledger_delta", "1/9"),
        lambda c: c.__setitem__("trajectory_classification", "CONVERGING"),
        lambda c: c.__setitem__("tournament_winner", "D3_JOINED_GORDAN_TEN_CLAUSE_THEOREM"),
        lambda c: c["closing_vector"].__setitem__(6, 4),
        lambda c: c["closing_vector"].__setitem__(7, 7),
        lambda c: c["triple_global_accounting"].__setitem__("residual_closing", 1_162_301),
        lambda c: c["joined_gordan_accounting"].__setitem__("closing_universal_coverage", "4/10"),
        lambda c: c["joined_gordan_accounting"].__setitem__("globally_attached", True),
        lambda c: c["exact_canary"].__setitem__("genuine_mixed_block_carrier_nonexistence_proved", True),
        lambda c: c["route_dispositions"].pop(),
        lambda c: c["route_dispositions"][0].__setitem__("successor_eligible", True),
        lambda c: c["route_dispositions"][5].__setitem__("handoff", "POSITIVE"),
        lambda c: c["obligation_delta"].pop(),
        lambda c: c["successor_bar"].__setitem__("eligible_route_count", 1),
        lambda c: c["successor_bar"].__setitem__("selected_successor", "JOINED"),
        lambda c: c["successor_bar"].__setitem__("construction_started", True),
        lambda c: c["storage"].__setitem__("google_drive_connector_used", True),
        lambda c: c["evidence_pins"].__setitem__("ops/team/theorem-reset-prover-strategy/RESULT.json", "0" * 64),
    )
    for fn in mutation_fns:
        c = deepcopy(closing)
        fn(c)
        mutations.append(c)
    rejected = 0
    for candidate in mutations:
        try:
            validate(checkpoint, candidate)
        except (AssertionError, KeyError, IndexError):
            rejected += 1
    require(rejected == len(mutations), "hostile mutations")
    print("PASS theorem-reset closing candidate")
    print(f"PASS hostile mutations rejected {rejected}/{len(mutations)}")
    print("VECTORS opening=(2/9,1,7,UNKNOWN,UNKNOWN,4,7) closing=(2/9,1,7,UNKNOWN,UNKNOWN,5,8)")
    print("HANDOFFS NULL/NULL/NULL/NEGATIVE/NULL/TIMEOUT")
    print("STALLED winner=NONE successor=NONE ledger_delta=0/9")
    print("STORAGE G_MIRROR_DEFERRED_ACCESS_DENIED connector=false approval=false")


if __name__ == "__main__":
    main()

