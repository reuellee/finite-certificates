#!/usr/bin/env python3
"""Fail-closed verifier for the D3 theorem-leverage audit opening."""

from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[4]
CYCLE = Path(__file__).resolve().parent
AUDIT_PATH = CYCLE / "OPENING_AUDIT.json"


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def validate(audit: dict) -> None:
    require(audit["base_revision"] == "98ed8d36f08f13305d226d3d3770e71542a0a408", "base revision")
    require(audit["base_tree"] == "52a03a10b62e54a9ff5aa4e59dbbc2af9a69eeab", "base tree")
    require(audit["opening_ledger"] == "2/9", "opening ledger")
    require(audit["proved_diagonals"] == [1, 2], "proved diagonals")
    require(audit["selected_construction_count"] == 0, "construction must remain unopened")

    distance = audit["proof_distance"]
    expected_distance = {
        "opening_score": "2/9",
        "score_deficit": 1,
        "goal_score": "3/9",
        "named_invariants": ["diag3_pair_hc1", "diag3_triple_hc0"],
        "open_load_bearing_obligations": 7,
        "certified_exhaustive_residual": "UNKNOWN",
        "global_coverage": "UNKNOWN",
        "same_blocker_streak": 3,
        "zero_ledger_streak": 6,
    }
    for key, value in expected_distance.items():
        require(distance[key] == value, f"proof-distance {key}")
    require(len(audit["comparable_closing_vectors"]) == 3, "three comparable vectors")
    require([row["zero_ledger_streak"] for row in audit["comparable_closing_vectors"]] == [4, 5, 6], "comparable zero-ledger streak")

    state = audit["pinned_d3_state"]
    expected_state = {
        "compactification_chart_count": 64,
        "compactification_support_face_count": 3375,
        "excluded_support_face_count": 3364,
        "nonexcluded_support_face_count": 11,
        "remaining_candidate_factor_face_pairs": 196064,
        "remaining_mixed_residual_restrictions": 70218,
        "base_cells": 527533,
        "open_sector_base_cells": 265962,
        "algebraic_t_base_cells": 261571,
        "open_base_lifted_cells": 4496636,
        "open_t_algebraic_u_lifted_cells": 4047846,
        "algebraic_t_lifted_cells": 8390619,
        "all_local_lifted_cells": 16935101,
        "unresolved_local_v_fibers": 0,
        "global_adjacencies": 0,
        "global_strict_closure_pairs": 0,
        "global_strict_closure_triples": 0,
        "global_parent_infinity_cells": 0,
        "extension_signature_universe": 97224,
        "triple_unresolved_rows": 1162302,
    }
    require(state == expected_state, "pinned D3 state")
    require(state["open_sector_base_cells"] + state["algebraic_t_base_cells"] == state["base_cells"], "base-cell partition")
    require(state["open_base_lifted_cells"] + state["open_t_algebraic_u_lifted_cells"] + state["algebraic_t_lifted_cells"] == state["all_local_lifted_cells"], "lifted-cell partition")

    require(len(audit["end_to_end_obligations"]) == 7, "seven obligations")
    require([row["route"] for row in audit["route_tournament"]] == [
        "DIRECT_GLOBAL_MASTER_CLOSURE",
        "COMPONENT_COSHEAF_STRUCTURAL_COMPRESSION",
        "EXACT_COUNTEREXAMPLE_OR_RETIREMENT",
        "D9_B_UV_01_BASELINE",
    ], "route tournament")
    require(not any(row["construction_ready"] for row in audit["route_tournament"]), "no route ready at opening")

    for relative, expected in audit["pins"].items():
        path = ROOT / relative
        require(path.is_file(), f"missing pin {relative}")
        require(sha256(path) == expected, f"pin drift {relative}")

    ledger = load(ROOT / "ai/omreal/data/DIAG3_RESEARCH_DECISION_LEDGER.json")
    require(ledger["theorem"]["score"] == "2/9", "decision-ledger score")
    obligations = {row["id"]: row for row in ledger["invariant_obligations"]}
    require(obligations["diag3_triple_hc0"]["status"] == "OPEN", "triple invariant")
    require(obligations["diag3_pair_hc1"]["status"] == "OPEN", "pair invariant")
    require(obligations["diag3_pair_hc1"]["current_global_adjacencies"] == 0, "global adjacency")
    require(obligations["diag3_pair_hc1"]["current_global_strict_closure_pairs"] == 0, "global closure pairs")
    require(obligations["diag3_pair_hc1"]["current_global_strict_closure_triples"] == 0, "global closure triples")
    require(obligations["diag3_pair_hc1"]["current_parent_infinity_cells"] == 0, "global infinity")

    pilot = load(ROOT / "ai/omreal/data/DIAG3_COMPONENT_COSHEAF_PILOT.json")
    require(pilot["status"] == "BOUNDED_NO_GO", "cosheaf status")
    require(pilot["decision"]["promote_existing_manifests_as_master_closure_replacement"] is False, "cosheaf promotion")
    require(pilot["decision"]["result"] == "BOUNDED_NO_GO", "cosheaf result")

    lift = load(ROOT / "ai/omreal/data/DIAG3_PAIR_GLOBAL_FOUR_SUPPORT_ALGEBRAIC_T_COEFFICIENT_ENDPOINT_U_POINT_V_LIFT.json")
    require(lift["scope"]["all_algebraic_t_v_lifts"] == "COMPLETE", "algebraic-t lifts")
    require(lift["scope"]["global_gluing_and_closure_data"] == "NOT_CLAIMED", "gluing must remain open")
    require(lift["cumulative_algebraic_t_v_lift"]["lifted_cells"] == 8390619, "algebraic-t lifted count")


def hostile_canaries(audit: dict) -> int:
    rejected = 0
    mutations = [
        ("ledger", lambda x: x.__setitem__("opening_ledger", "3/9")),
        ("construction", lambda x: x.__setitem__("selected_construction_count", 1)),
        ("residual", lambda x: x["proof_distance"].__setitem__("certified_exhaustive_residual", 527533)),
        ("coverage", lambda x: x["proof_distance"].__setitem__("global_coverage", "527533/527533")),
        ("obligations", lambda x: x["proof_distance"].__setitem__("open_load_bearing_obligations", 6)),
        ("base_cells", lambda x: x["pinned_d3_state"].__setitem__("base_cells", 527532)),
        ("lifted_cells", lambda x: x["pinned_d3_state"].__setitem__("algebraic_t_lifted_cells", 8390618)),
        ("global_pair", lambda x: x["pinned_d3_state"].__setitem__("global_strict_closure_pairs", 1)),
        ("route_ready", lambda x: x["route_tournament"][0].__setitem__("construction_ready", True)),
    ]
    for name, mutate in mutations:
        candidate = copy.deepcopy(audit)
        mutate(candidate)
        try:
            validate(candidate)
        except AssertionError:
            rejected += 1
        else:
            raise AssertionError(f"hostile mutation accepted: {name}")
    return rejected


def main() -> None:
    audit = load(AUDIT_PATH)
    validate(audit)
    rejected = hostile_canaries(audit)
    print(f"PASS D3 leverage opening: 2/9, 7 obligations, UNKNOWN global residual, {rejected}/9 hostiles rejected")


if __name__ == "__main__":
    main()
