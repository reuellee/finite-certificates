#!/usr/bin/env python3
"""Independent fail-closed referee for the frozen theorem-reset candidate.

Standard-library only.  The referee validates the immutable commit chain,
source/evidence pins, exact fail-closed scientific accounting, clean replay
record, and hostile mutations.  It never promotes a theorem or selects a
route.
"""

from __future__ import annotations

import copy
from functools import lru_cache
import hashlib
import json
import os
from pathlib import Path
import subprocess


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
CYCLE = ROOT / "ops/research-team/cycles/2026-09-01-theorem-reset-joined-gordan-tournament-gate1"
RESULT_PATH = HERE / "RESULT.json"
REPLAY_PATH = HERE / "CLEAN_REPLAY.json"

BASE = "3689b5344dfed38468639d0e92b48f0b5fc4ebc8"
BASE_TREE = "ef14ccd9b844dae5e9b535310122251ca0e86bfb"
OPENING = "d4f83ffedc13f2fc07a2c8cd39a03cec8550da22"
OPENING_TREE = "97ab517bfe5bf8b3b93e7d604690c4d6a1342c43"
PROVER_INTEGRATED = "9c7c6ab5ae56188614a9a9a99e224ddf639c30b6"
VERIFIER_INTEGRATED = "e8cf9348c83670a0d79d7f509601425c06e662c5"
EVIDENCE = "5277886b1171f15b8e486d5e62212515534e5944"
EVIDENCE_TREE = "ed5e6359122bc167898f9d6b8f2c60904ff0125c"
CHECKPOINT = "ebbe79cbc8a2b490ff1d9e77dde1cafb57d8a1e8"
CHECKPOINT_TREE = "b0ee5a5890715704fa10b839979e5100fc7740bb"
FROZEN = "627344866096af0eea2863af295d718237ca8d23"
FROZEN_TREE = "b5b254bcb94662f8ed3ff621334638cc89526ada"
DIGEST = "a76a7c2cd6631c2d9724b450540bec7f3be6c106a41ae41f1736bbd2755a5ca4"

ROUTES = [
    ("D3_JOINED_GORDAN_TEN_CLAUSE_THEOREM", [5, 2, 2, 4, 5, 4, 5, 3], "NULL"),
    ("D3_UNIFORM_Q3_COMPLETE_PARENT_BOUNDARY_ATLAS", [5, 3, 2, 5, 4, 4, 4, 4], "NULL"),
    ("D3_PAIR_GLOBAL_COMPRESSION_DESCENT_EQUIVALENCE", [5, 1, 1, 4, 5, 3, 4, 4], "NULL"),
    ("EXACT_COUNTEREXAMPLE_OR_ROUTE_RETIREMENT", [4, 3, 4, 5, 4, 5, 5, 1], "NEGATIVE"),
    ("D9_SIMULTANEOUS_INSERTION_2604_PARENT_THEOREM", [2, 2, 2, 4, 4, 4, 4, 4], "NULL"),
    ("D9_ACTUAL_ARRANGEMENT_SIGN_GEODESY", [2, 2, 1, 5, 5, 3, 2, 4], "TIMEOUT"),
]
OBLIGATIONS = [
    "global_gluing", "extension_labels", "strict_closure", "relative_infinity",
    "middle_rank_replay", "diag3_pair_hc1", "diag3_triple_hc0",
]
ISOLATED_LANES = [
    ("theorem-reset-prover-strategy",
     "6942b9faf15fa6b63f277c05f901f147bfa469fb", OPENING,
     "54e822ad91ef6168bef611cad7ee5e070b032839",
     "ops/team/theorem-reset-prover-strategy", PROVER_INTEGRATED,
     "d973ccf0b236990c259141078c613669c9f06026"),
    ("theorem-reset-falsifier",
     "f2f2d6d4bf6cdf06c6a7c9fe15d0f69a476d5077", OPENING,
     "3a0f62163c4d040195c62f51d5a76e6c60bbd20d",
     "ops/team/theorem-reset-falsifier", EVIDENCE,
     "5883c7f553136f0f513d9d4346da133b46a74940"),
    ("theorem-reset-independent-verifier",
     "b50cf74e6112429cda0e899093c749723d174470", OPENING,
     "f0c6b0ef3cbca02dc4f6ff66781cd86fa0594a1e",
     "ops/team/theorem-reset-independent-verifier", VERIFIER_INTEGRATED,
     "2374844259e92ad3565625896be1d599eb28700f"),
]


def expected_obligations() -> list[dict]:
    rows = [
        {"id": name, "opening": "INCONCLUSIVE", "closing": "INCONCLUSIVE", "delta": "UNCHANGED"}
        for name in OBLIGATIONS[:-1]
    ]
    rows.append({"id": "diag3_triple_hc0", "opening": 1162302, "closing": 1162302, "delta": 0})
    return rows


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def git(*args: str) -> str:
    return subprocess.run(
        ["git", *args], cwd=ROOT, check=True, capture_output=True,
        text=True, encoding="utf-8",
    ).stdout.strip()


def git_object_exists(revision: str) -> bool:
    env = os.environ.copy()
    env["GIT_NO_LAZY_FETCH"] = "1"
    return subprocess.run(
        ["git", "cat-file", "-e", f"{revision}^{{commit}}"],
        cwd=ROOT, check=False, capture_output=True, env=env,
    ).returncode == 0


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for block in iter(lambda: source.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def validate_git_chain() -> str:
    objects = {
        BASE: BASE_TREE, OPENING: OPENING_TREE, EVIDENCE: EVIDENCE_TREE,
        CHECKPOINT: CHECKPOINT_TREE, FROZEN: FROZEN_TREE,
    }
    for commit, tree in objects.items():
        require(git("rev-parse", f"{commit}^{{tree}}") == tree, f"tree {commit}")
    chain = [BASE, OPENING, PROVER_INTEGRATED, VERIFIER_INTEGRATED,
             EVIDENCE, CHECKPOINT, FROZEN]
    for parent, child in zip(chain, chain[1:]):
        require(git("rev-parse", f"{child}^") == parent, f"parent {child}")
    require(git("merge-base", "--is-ancestor", BASE, FROZEN) == "", "base ancestry")
    require(git("merge-base", "--is-ancestor", FROZEN, "HEAD") == "", "referee ancestry")

    checkpoint = load(CYCLE / "MID_CYCLE_CHECKPOINT.json")
    lane_verdicts = checkpoint["lane_verdicts"]
    require(len(lane_verdicts) == len(ISOLATED_LANES), "isolated lane count")
    availability = [git_object_exists(commit) for _, commit, *_ in ISOLATED_LANES]
    require(all(availability) or not any(availability), "partial isolated history")

    for row, lane in zip(lane_verdicts, ISOLATED_LANES):
        track, commit, parent, tree, surface, integrated, surface_tree = lane
        require(row["track"] == track, f"isolated track {track}")
        require(row["isolated_commit"] == commit, f"isolated commit pin {track}")
        require(row["isolated_tree"] == tree, f"isolated tree pin {track}")
        require(row["integrated_commit"] == integrated[:7], f"integrated commit pin {track}")
        require(git("rev-parse", f"{integrated}:{surface}") == surface_tree,
                f"integrated lane tree {surface}")
        if not all(availability):
            continue
        require(git("rev-parse", f"{commit}^") == parent, f"isolated parent {commit}")
        require(git("rev-parse", f"{commit}^{{tree}}") == tree, f"isolated tree {commit}")
        changed = git("diff-tree", "--no-commit-id", "--name-only", "-r", commit).splitlines()
        require(changed and all(path.startswith(surface + "/") for path in changed), f"lane scope {commit}")
        require(git("rev-parse", f"{commit}:{surface}") == git("rev-parse", f"{integrated}:{surface}"),
                f"integrated lane identity {surface}")
    return "FULL_ISOLATED_HISTORY" if all(availability) else "PINNED_ISOLATED_SURFACES"


@lru_cache(maxsize=1)
def validate_pins() -> dict:
    opening = load(CYCLE / "OPENING_AUDIT.json")
    for relative, expected in opening["pins"].items():
        require(sha256(ROOT / relative) == expected, f"opening pin {relative}")
    closing = load(CYCLE / "CLOSING_CANDIDATE.json")
    for relative, expected in closing["evidence_pins"].items():
        require(sha256(ROOT / relative) == expected, f"evidence pin {relative}")
    counts = {"opening": len(opening["pins"]), "evidence": len(closing["evidence_pins"])}
    for name in ("prover-strategy", "falsifier", "independent-verifier"):
        manifest = load(ROOT / f"ops/team/theorem-reset-{name}/SOURCE_MANIFEST.json")
        sources = manifest["sources"]
        rows = sources.items() if isinstance(sources, dict) else ((row["path"], row["sha256"]) for row in sources)
        count = 0
        for relative, expected in rows:
            require(sha256(ROOT / relative) == expected, f"{name} source pin {relative}")
            count += 1
        counts[name] = count
    return counts


@lru_cache(maxsize=1)
def validate_sources() -> dict:
    ledger = load(ROOT / "ai/omreal/data/DIAG3_RESEARCH_DECISION_LEDGER.json")
    require(ledger["theorem"]["score"] == "2/9", "canonical score")
    require(ledger["theorem"]["proved_diagonals"] == [1, 2], "proved diagonals")
    obligations = {row["id"]: row for row in ledger["invariant_obligations"]}
    pair = obligations["diag3_pair_hc1"]
    triple = obligations["diag3_triple_hc0"]
    require(pair["status"] == triple["status"] == "OPEN", "D3 obligations open")
    require((pair["current_global_adjacencies"], pair["current_global_strict_closure_pairs"],
             pair["current_global_strict_closure_triples"], pair["current_parent_infinity_cells"])
            == (0, 0, 0, 0), "pair global interface")
    require((triple["universe_count"], triple["proved_noncompact_count"], triple["unresolved_count"])
            == (79102449, 77940147, 1162302), "triple source accounting")
    require(79102449 - 77940147 == 1162302, "triple arithmetic")
    return {
        "ledger": "2/9", "proved_diagonals": [1, 2],
        "pair_global_interface": [0, 0, 0, 0],
        "triple_source_orbits": 79102449, "triple_settled_orbits": 77940147,
        "triple_residual_orbits": 1162302,
    }


def validate_cycle() -> None:
    opening = load(CYCLE / "OPENING_AUDIT.json")
    checkpoint = load(CYCLE / "MID_CYCLE_CHECKPOINT.json")
    closing = load(CYCLE / "CLOSING_CANDIDATE.json")
    graph = load(CYCLE / "OBLIGATION_GRAPH.json")

    require(opening["base_revision"] == checkpoint["base_revision"] == closing["base_revision"] == BASE,
            "base revision")
    require(opening["base_tree"] == checkpoint["base_tree"] == closing["base_tree"] == BASE_TREE,
            "base tree")
    require(checkpoint["opening_revision"] == closing["opening_revision"] == OPENING, "opening revision")
    require(checkpoint["integrated_lane_head"] == closing["integrated_evidence_revision"] == EVIDENCE,
            "evidence revision")
    require(closing["checkpoint_revision"] == CHECKPOINT, "checkpoint revision")
    require(closing["opening_ledger"] == closing["closing_ledger"] == "2/9", "ledger")
    require(closing["ledger_delta"] == "0/9" and closing["theorem_promotion"] == "NONE", "ledger delta")
    vectors = [
        ["2/9", 1, "diag3_pair_hc1_AND_diag3_triple_hc0", 7, "UNKNOWN", "UNKNOWN", 4, 7],
        ["2/9", 1, "diag3_pair_hc1_AND_diag3_triple_hc0", 7, "UNKNOWN", "UNKNOWN", 4, 7],
        ["2/9", 1, "diag3_pair_hc1_AND_diag3_triple_hc0", 7, "UNKNOWN", "UNKNOWN", 5, 8],
    ]
    require([closing["opening_vector"], closing["checkpoint_vector"], closing["closing_vector"]] == vectors,
            "proof-distance vectors")
    require(checkpoint["minimum_acceptable_delta_reachable_inside_remaining_ceiling"] is False,
            "midpoint reachability")
    decision = checkpoint["checkpoint_decision"]
    require(decision["stop_discovery"] is True and decision["resource_ceiling_enlarged"] is False,
            "midpoint stop")
    require(decision["construction_started"] is False, "midpoint construction")
    require(closing["minimum_acceptable_delta_met"] is False, "minimum decrease")
    require(closing["trajectory_classification"] == "STALLED", "trajectory")
    require(closing["tournament_winner"] == "NONE", "winner")

    triple = closing["triple_global_accounting"]
    require((triple["coverage_opening"], triple["coverage_closing"]) ==
            ("77940147/79102449", "77940147/79102449"), "triple coverage")
    require((triple["residual_opening"], triple["residual_closing"], triple["residual_delta"])
            == (1162302, 1162302, 0), "triple residual")
    require(triple["source_order_semantic_sha256"] == DIGEST, "triple semantic digest")
    joined = closing["joined_gordan_accounting"]
    require(joined["formal_face_type_denominator"] == 10, "joined denominator")
    require(joined["opening_universal_coverage"] == joined["closing_universal_coverage"] == "3/10",
            "joined coverage")
    require(joined["credited_universal_clauses"] == ["(0)", "(1)", "(2)"], "joined credit")
    require(joined["new_universal_clause"] == "NONE", "new joined clause")
    require(not joined["globally_attached"] and not joined["end_to_end_d3_denominator"] and not joined["bounded_chain"],
            "joined fail-closed scope")

    require(closing["obligation_delta"] == expected_obligations(), "obligations unchanged")
    load_bearing = [row["id"] for row in graph["nodes"] if row.get("load_bearing")]
    require(load_bearing == OBLIGATIONS, "graph load-bearing obligations")

    dispositions = closing["route_dispositions"]
    require(len(dispositions) == len(ROUTES), "route count")
    for row, (route, scores, handoff) in zip(dispositions, ROUTES):
        require(row["route"] == route and row["scores"] == scores and row["handoff"] == handoff,
                f"route {route}")
        require(len(row["scores"]) == 8 and row["successor_eligible"] is False,
                f"route score/eligibility {route}")
    require([row["handoff"] for row in dispositions] ==
            ["NULL", "NULL", "NULL", "NEGATIVE", "NULL", "TIMEOUT"], "handoff sequence")
    bar = closing["successor_bar"]
    require(bar == {
        "theorem_level_quantifier_attachment_proved": False,
        "certified_finite_end_to_end_denominator_and_coverage_proved": False,
        "bounded_strict_decrease_chain_proved": False,
        "eligible_route_count": 0,
        "selected_construction_target": "NONE",
        "selected_successor": "NONE",
        "construction_started": False,
    }, "successor bar")
    storage = closing["storage"]
    require(storage["native_g_mirror"] == "DEFERRED_ACCESS_DENIED_IN_SANDBOX_TO_COORDINATING_USER_CONTEXT",
            "G mirror status")
    require(storage["google_drive_connector_used"] is False and storage["approval_requested"] is False,
            "connector/approval status")


def validate_replay(replay: dict) -> None:
    require(replay["clone"]["no_hardlinks_flag"] is True and replay["clone"]["exit_code"] == 0,
            "no-hardlink clone")
    require(replay["detached_head"] == FROZEN and replay["detached_tree"] == FROZEN_TREE,
            "replay revision")
    require(replay["working_tree_status"] == "CLEAN_DETACHED_HEAD", "replay clean")
    require(len(replay["required_verifiers"]) == 10, "replay count")
    require(all(row["exit_code"] == 0 and row["status"] == "PASS"
                for row in replay["required_verifiers"]), "replay status")
    identities = replay["acceptance_file_identity_check"]
    require(identities["matching_files_checked"] == 14, "identity count")
    require(identities["same_identity_count"] == 0, "identity collisions")
    require(all(row["same_bytes"] and not row["same_identity"] and
                row["source_nlink"] == row["replay_nlink"] == 1
                for row in identities["files"]), "identity details")
    require(replay["optional_timeout"]["acceptance_dependency"] is False, "timeout independence")


def validate_result(result: dict) -> None:
    require(result["frozen_candidate"] == {"commit": FROZEN, "tree": FROZEN_TREE}, "result frozen")
    require(result["canonical_base"] == {"commit": BASE, "tree": BASE_TREE}, "result base")
    require(result["verdict"] == "ACCEPT_FROZEN_CANDIDATE_FAIL_CLOSED", "result verdict")
    require(result["trajectory_classification"] == "STALLED", "result trajectory")
    require(result["strategy_action"] == "STOP", "result action")
    require(result["ledger"] == {"opening": "2/9", "closing": "2/9", "delta": "0/9"}, "result ledger")
    expected_open = ["2/9", 1, "diag3_pair_hc1_AND_diag3_triple_hc0", 7, "UNKNOWN", "UNKNOWN", 4, 7]
    expected_close = ["2/9", 1, "diag3_pair_hc1_AND_diag3_triple_hc0", 7, "UNKNOWN", "UNKNOWN", 5, 8]
    require(result["opening_vector"] == result["checkpoint_vector"] == expected_open, "result open/checkpoint")
    require(result["closing_vector"] == expected_close, "result close")
    require(result["minimum_acceptable_delta_met"] is False, "result minimum")
    require(result["joined_measure"] == {
        "formal_clause_denominator": 10, "opening_coverage": "3/10", "closing_coverage": "3/10",
        "credited_clauses": ["(0)", "(1)", "(2)"], "new_clause": "NONE",
        "globally_attached": False, "end_to_end_d3_denominator": False, "bounded_chain": False,
    }, "result joined")
    require(result["triple_measure"] == {
        "coverage": "77940147/79102449", "opening_residual": 1162302,
        "closing_residual": 1162302, "residual_delta": 0,
        "source_order_semantic_sha256": DIGEST, "triple_only_promotes_d3": False,
    }, "result triple")
    require(result["obligations"] == expected_obligations(), "result obligations unchanged")
    require([(row["id"], row["scores"], row["handoff"]) for row in result["routes"]] == ROUTES,
            "result routes")
    require(all(row["successor_eligible"] is False for row in result["routes"]), "result route eligibility")
    require(result["handoff_sequence"] == ["NULL", "NULL", "NULL", "NEGATIVE", "NULL", "TIMEOUT"],
            "result handoffs")
    require(result["tournament_winner"] == "NONE" and result["selected_successor"] == "NONE",
            "result successor")
    require(result["construction_started"] is False, "result construction")
    require(result["independent_reconstruction"] == validate_sources(), "result source reconstruction")
    require(result["pin_counts"] == validate_pins(), "result pins")
    require(result["clean_replay"] == {"required_passed": 10, "required_total": 10,
                                        "acceptance_files_checked": 14, "identity_collisions": 0},
            "result replay summary")
    require(result["storage"] == {
        "native_g_mirror": "DEFERRED_ACCESS_DENIED_IN_SANDBOX_TO_COORDINATING_USER_CONTEXT",
        "google_drive_connector_used": False, "approval_requested": False,
        "github_write": False,
    }, "result storage")
    require(result["hostile_mutations"]["required"] >= 12, "result hostile minimum")
    require(result["hostile_mutations"]["rejected"] == result["hostile_mutations"]["required"],
            "result hostile count")


def hostile_canaries(result: dict) -> int:
    mutations = [
        lambda x: x["frozen_candidate"].__setitem__("commit", BASE),
        lambda x: x["frozen_candidate"].__setitem__("tree", BASE_TREE),
        lambda x: x.__setitem__("verdict", "PROMOTE"),
        lambda x: x.__setitem__("trajectory_classification", "CONVERGING"),
        lambda x: x.__setitem__("strategy_action", "CONTINUE"),
        lambda x: x["ledger"].__setitem__("closing", "3/9"),
        lambda x: x["ledger"].__setitem__("delta", "1/9"),
        lambda x: x["opening_vector"].__setitem__(3, 6),
        lambda x: x["checkpoint_vector"].__setitem__(4, 1162301),
        lambda x: x["closing_vector"].__setitem__(3, 6),
        lambda x: x["closing_vector"].__setitem__(4, 1162301),
        lambda x: x["closing_vector"].__setitem__(5, "1/1"),
        lambda x: x["closing_vector"].__setitem__(6, 4),
        lambda x: x["closing_vector"].__setitem__(7, 7),
        lambda x: x.__setitem__("minimum_acceptable_delta_met", True),
        lambda x: x["joined_measure"].__setitem__("closing_coverage", "4/10"),
        lambda x: x["joined_measure"].__setitem__("new_clause", "(1,0,0)"),
        lambda x: x["joined_measure"].__setitem__("globally_attached", True),
        lambda x: x["joined_measure"].__setitem__("end_to_end_d3_denominator", True),
        lambda x: x["joined_measure"].__setitem__("bounded_chain", True),
        lambda x: x["triple_measure"].__setitem__("closing_residual", 1162301),
        lambda x: x["triple_measure"].__setitem__("residual_delta", -1),
        lambda x: x["triple_measure"].__setitem__("source_order_semantic_sha256", "0" * 64),
        lambda x: x["obligations"].pop(),
        lambda x: x["obligations"][0].__setitem__("closing", "PROVED"),
        lambda x: x["routes"].pop(),
        lambda x: x["routes"][0]["scores"].__setitem__(1, 5),
        lambda x: x["routes"][0].__setitem__("handoff", "POSITIVE"),
        lambda x: x["routes"][0].__setitem__("successor_eligible", True),
        lambda x: x["handoff_sequence"].__setitem__(5, "NULL"),
        lambda x: x.__setitem__("tournament_winner", "D3_JOINED_GORDAN_TEN_CLAUSE_THEOREM"),
        lambda x: x.__setitem__("selected_successor", "D3_JOINED_GORDAN_TEN_CLAUSE_THEOREM"),
        lambda x: x.__setitem__("construction_started", True),
        lambda x: x["independent_reconstruction"].__setitem__("triple_residual_orbits", 1162301),
        lambda x: x["clean_replay"].__setitem__("required_passed", 9),
        lambda x: x["clean_replay"].__setitem__("identity_collisions", 1),
        lambda x: x["storage"].__setitem__("native_g_mirror", "VERIFIED"),
        lambda x: x["storage"].__setitem__("google_drive_connector_used", True),
        lambda x: x["storage"].__setitem__("approval_requested", True),
        lambda x: x["storage"].__setitem__("github_write", True),
    ]
    rejected = 0
    for index, mutate in enumerate(mutations, start=1):
        candidate = copy.deepcopy(result)
        mutate(candidate)
        try:
            validate_result(candidate)
        except (AssertionError, KeyError, IndexError):
            rejected += 1
        else:
            raise AssertionError(f"hostile mutation accepted: {index}")
    return rejected


def main() -> None:
    result = load(RESULT_PATH)
    replay = load(REPLAY_PATH)
    history_mode = validate_git_chain()
    validate_cycle()
    validate_replay(replay)
    validate_result(result)
    rejected = hostile_canaries(result)
    require(rejected == result["hostile_mutations"]["required"], "declared hostile count")
    print(
        "PASS theorem-reset closing referee: frozen 6273448 / b5b254b; "
        "2/9 -> 2/9; vectors 4,7 -> 5,8; 3/10 unchanged; residual 1162302; "
        "handoffs NULL/NULL/NULL/NEGATIVE/NULL/TIMEOUT; STALLED / NONE / NONE; "
        f"10/10 detached replays; 14/14 copied identities independent; {rejected}/{rejected} hostiles; "
        f"history {history_mode}"
    )


if __name__ == "__main__":
    main()
