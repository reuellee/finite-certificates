#!/usr/bin/env python3
"""Independent standard-library verifier for the D3 strategy-audit lane."""

from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path
from typing import Any


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
RESULT = HERE / "RESULT.json"

EXPECTED_PINS = {
    "ai/omreal/data/DIAG3_RESEARCH_DECISION_LEDGER.json": "73b0b742d6336d754ae99b7054858a3a3c96b3aaf1601b2228c076a732903d6e",
    "ai/omreal/data/DIAG3_PAIR_GLOBAL_CLOSURE_OPEN_OBJECT.json": "707a96f19f471af041d02bf22fc4267ddd4bf6b78cffde4783f660b645aed833",
    "ai/omreal/data/DIAG3_PAIR_GLOBAL_row2599_compactification_atlas.json": "956fbe7e5c7b1e04c8873ed9c0f3de9cb5420e3e06f1d5fae4c60f4e0571b364",
    "ai/omreal/data/DIAG3_PAIR_GLOBAL_row2599_face_bernstein_atlas.json": "5d8029d930cea0708f00c90cac69f87de7579118cd48a6995caf7b3be26e0822",
    "ai/omreal/data/DIAG3_PAIR_GLOBAL_row2599_parent_face_gate.json": "cc279d125605b45d25a3a01f462ad051038102f2bf12574f494a9d261bfc7401",
    "ai/omreal/data/DIAG3_PAIR_GLOBAL_FOUR_SUPPORT_GATE.json": "d9a16b39966cb1ce404b3df8362b722052fdc0854db331e5bc12aeec4ef9bcef",
    "ai/omreal/data/DIAG3_PAIR_GLOBAL_FOUR_SUPPORT_BASE_PROJECTION.json.gz": "9b595b61273b2d4ad1188eca8135b7c06162e75452a89a17ffb6725f0d461e82",
    "ai/omreal/data/DIAG3_PAIR_GLOBAL_FOUR_SUPPORT_ALGEBRAIC_T_COEFFICIENT_ENDPOINT_U_POINT_V_LIFT.json": "be3e1fc8aa66842961acb22f3740cc68aa99fca65f9fd5784352cd8f53703a5b",
    "ai/omreal/data/DIAG3_COMPONENT_COSHEAF_PILOT.json": "2fa847a3f7edf206db225d3a184f90c00c54b319ad2cdeaca39cb9ed9d5b0854",
    "ai/omreal/DIAG3_GLOBAL_EXIT_CRITERION.md": "0a372197a49f4a767c06b23a6df830ef2784e7fe653b4b3eb1a506eec0518e27",
    "ops/team/global-exit/GLOBAL_EXIT_FIXTURES.json": "4bc0331835c82f0eb3e98bc87d0c6a37683ef66298e430337c3c0661ddd4a029",
    "ops/team/d9-factor19069-homogenizer-boundary-certificate/RESULT.json": "7126a33933c6a26dbba259ba6bcf1f7cecbb332323d595a9bd23451b938c5a73",
}

ROUTE_IDS = [
    "DIRECT_GLOBAL_MASTER_CLOSURE",
    "COMPONENT_COSHEAF_STRUCTURAL_COMPRESSION",
    "EXACT_COUNTEREXAMPLE_OR_RETIREMENT",
    "D9_B_UV_01_LOW_LEVERAGE_BASELINE",
]

OBLIGATION_IDS = [
    "global_gluing",
    "extension_labels",
    "strict_closure",
    "relative_infinity",
    "middle_rank_replay",
    "diag3_pair_hc1",
    "diag3_triple_hc0",
]


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def load_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        while chunk := handle.read(1024 * 1024):
            digest.update(chunk)
    return digest.hexdigest()


def sources() -> dict[str, Any]:
    loaded: dict[str, Any] = {}
    for relative, expected in EXPECTED_PINS.items():
        path = ROOT / relative
        require(path.is_file(), f"missing source: {relative}")
        require(sha256(path) == expected, f"source drift: {relative}")
        if path.suffix == ".json":
            loaded[relative] = load_json(path)
    return loaded


def reconstruct(loaded: dict[str, Any]) -> dict[str, Any]:
    ledger = loaded["ai/omreal/data/DIAG3_RESEARCH_DECISION_LEDGER.json"]
    closure = loaded["ai/omreal/data/DIAG3_PAIR_GLOBAL_CLOSURE_OPEN_OBJECT.json"]
    compact = loaded["ai/omreal/data/DIAG3_PAIR_GLOBAL_row2599_compactification_atlas.json"]
    face = loaded["ai/omreal/data/DIAG3_PAIR_GLOBAL_row2599_face_bernstein_atlas.json"]
    parent = loaded["ai/omreal/data/DIAG3_PAIR_GLOBAL_row2599_parent_face_gate.json"]
    gate = loaded["ai/omreal/data/DIAG3_PAIR_GLOBAL_FOUR_SUPPORT_GATE.json"]
    final_v = loaded[
        "ai/omreal/data/DIAG3_PAIR_GLOBAL_FOUR_SUPPORT_ALGEBRAIC_T_COEFFICIENT_ENDPOINT_U_POINT_V_LIFT.json"
    ]
    pilot = loaded["ai/omreal/data/DIAG3_COMPONENT_COSHEAF_PILOT.json"]
    fixtures = loaded["ops/team/global-exit/GLOBAL_EXIT_FIXTURES.json"]
    d9 = loaded["ops/team/d9-factor19069-homogenizer-boundary-certificate/RESULT.json"]

    obligations = {row["id"]: row for row in ledger["invariant_obligations"]}
    pair = obligations["diag3_pair_hc1"]
    triple = obligations["diag3_triple_hc0"]
    progress = ledger["historical_selected_target_progress"]
    cosheaf = progress["thirty_fourth_pair_component_cosheaf_strategy_pilot"]
    base = pilot["two_support_input_audit"]["base_cell_partition"]
    lifted = pilot["two_support_input_audit"]["lifted_cell_partition"]
    observations = closure["observations"]

    require(base["open_t_open_u"] + base["open_t_algebraic_u"] + base["algebraic_t"] == base["total"], "base partition")
    require(lifted["open_t_open_u"] + lifted["open_t_algebraic_u"] + lifted["algebraic_t"] == lifted["total"], "lift partition")
    require(triple["universe_count"] - triple["proved_noncompact_count"] == triple["unresolved_count"], "triple accounting")
    require(final_v["cumulative_algebraic_t_v_lift"]["lifted_cells"] == lifted["algebraic_t"], "algebraic-t cross-check")
    require(cosheaf["base_cells"] == base["total"] and cosheaf["lifted_cells"] == lifted["total"], "ledger/pilot cross-check")

    fixture_replays = cosheaf["fixture_replay"]
    ordered_replays = sum(row["ordered_profile_triples"] for row in fixture_replays.values())
    require(ordered_replays == 952, "fixture rank replay sum")
    require(fixtures["pair_countermodel"]["unfilled"]["expected_h1_f2"] == 1, "unfilled H1")
    require(fixtures["pair_countermodel"]["filled"]["expected_h1_f2"] == 0, "filled H1")

    return {
        "score": ledger["theorem"]["score"],
        "proved_diagonals": ledger["theorem"]["proved_diagonals"],
        "pair_status": pair["status"],
        "triple_status": triple["status"],
        "chart_count": compact["chart_atlas"]["chart_count"],
        "transition_count": compact["chart_atlas"]["ordered_transition_count"],
        "support_face_count": face["face_count"],
        "infinity_face_count": face["infinity_face_count"],
        "excluded_face_count": parent["excluded_support_face_count"],
        "nonexcluded_face_count": parent["nonexcluded_support_face_count"],
        "remaining_pairs": parent["remaining_candidate_factor_face_pair_count"],
        "remaining_mixed": parent["remaining_mixed_residual_restriction_count"],
        "covered_parent_domains": len(gate["parent_domains"]),
        "active_walls": gate["combined_compression"]["distinct_active_walls_after_positive_quotient"],
        "global_parent_coverage": gate["scope"]["global_parent_cell_coverage"],
        "base": base,
        "lifted": lifted,
        "unresolved_local_v": cosheaf["unresolved_local_v_fibers"],
        "signature_universe": observations["atlas_assignment_count"],
        "global_adjacencies": observations["certified_adjacency_edges_between_distinct_atlas_charts"],
        "global_pairs": observations["certified_global_strict_closure_pairs"],
        "global_triples": observations["certified_global_strict_closure_triples"],
        "global_infinity": observations["certified_parent_infinity_cells"],
        "fixture_count": len(fixture_replays),
        "ordered_replays": ordered_replays,
        "specialization_maps": cosheaf["fixture_limit_census"]["component_specialization_maps"],
        "split_merge": cosheaf["fixture_limit_census"]["many_to_one_component_maps"],
        "cosheaf_result": pilot["decision"]["result"],
        "cosheaf_promotable": pilot["decision"]["promote_existing_manifests_as_master_closure_replacement"],
        "triple_universe": triple["universe_count"],
        "triple_proved": triple["proved_noncompact_count"],
        "triple_unresolved": triple["unresolved_count"],
        "d9_branch": d9["first_unresolved_branch"],
        "d9_ledger_delta": d9["ledger_delta"],
    }


def validate(record: dict[str, Any], facts: dict[str, Any], check_pins: bool = True) -> None:
    require(record["format"] == "d3-global-closure-leverage-strategy-audit-v1", "format")
    require(record["canonical_base_revision"] == "98ed8d36f08f13305d226d3d3770e71542a0a408", "base revision")
    require(record["canonical_base_tree"] == "52a03a10b62e54a9ff5aa4e59dbbc2af9a69eeab", "base tree")
    require(record["construction_performed"] is False, "construction prohibition")
    require(record["ledger_before"] == facts["score"] == "2/9", "opening ledger")
    require(record["ledger_after"] == "2/9" and record["ledger_delta"] == "0/9", "ledger delta")
    require(record["proved_diagonals"] == facts["proved_diagonals"] == [1, 2], "proved diagonals")

    pins = record["pinned_reconstruction"]
    expected_pins = {
        "compactification_chart_count": facts["chart_count"],
        "ordered_chart_transition_count": facts["transition_count"],
        "support_face_count": facts["support_face_count"],
        "infinity_support_face_count": facts["infinity_face_count"],
        "excluded_support_face_count": facts["excluded_face_count"],
        "nonexcluded_support_face_count": facts["nonexcluded_face_count"],
        "remaining_candidate_factor_face_pairs": facts["remaining_pairs"],
        "remaining_mixed_residual_restrictions": facts["remaining_mixed"],
        "covered_four_support_parent_domains": facts["covered_parent_domains"],
        "active_interior_wall_equations_on_covered_domains": facts["active_walls"],
        "global_parent_cell_coverage_claimed": facts["global_parent_coverage"] == "CLAIMED",
        "unresolved_local_v_fibers": facts["unresolved_local_v"],
        "extension_signature_universe": facts["signature_universe"],
        "certified_global_adjacencies": facts["global_adjacencies"],
        "certified_global_strict_closure_pairs": facts["global_pairs"],
        "certified_global_strict_closure_triples": facts["global_triples"],
        "certified_global_parent_infinity_cells": facts["global_infinity"],
        "component_cosheaf_fixture_count": facts["fixture_count"],
        "component_cosheaf_ordered_rank_replays": facts["ordered_replays"],
        "component_cosheaf_specialization_maps": facts["specialization_maps"],
        "component_cosheaf_nontrivial_split_merge_fixtures": facts["split_merge"],
        "triple_universe_count": facts["triple_universe"],
        "triple_proved_noncompact_count": facts["triple_proved"],
        "triple_unresolved_count": facts["triple_unresolved"],
    }
    for key, expected in expected_pins.items():
        require(pins[key] == expected, f"reconstructed field: {key}")
    require(pins["base_cell_partition"] == facts["base"], "base partition record")
    require(pins["local_lifted_cell_partition"] == facts["lifted"], "lift partition record")

    obligations = record["end_to_end_obligations"]
    require([row["id"] for row in obligations] == OBLIGATION_IDS, "seven obligations")
    require(all(row["status"] == "INCONCLUSIVE" for row in obligations), "obligations open")
    by_id = {row["id"]: row for row in obligations}
    require(by_id["global_gluing"]["certified_exhaustive_residual"] == "UNKNOWN", "gluing residual")
    require(by_id["extension_labels"]["candidate_label_universe"] == facts["signature_universe"], "label universe")
    require(by_id["strict_closure"]["certified_global_pairs"] == facts["global_pairs"], "closure pairs")
    require(by_id["strict_closure"]["certified_global_triples"] == facts["global_triples"], "closure triples")
    require(by_id["relative_infinity"]["certified_global_parent_infinity_cells"] == facts["global_infinity"], "infinity cells")
    require(by_id["middle_rank_replay"]["certified_global_rank_replays"] == 0, "global rank")
    require(by_id["middle_rank_replay"]["local_fixture_ordered_rank_replays"] == facts["ordered_replays"], "local ranks")
    require(facts["pair_status"] == "OPEN" and by_id["diag3_pair_hc1"]["certified_exhaustive_residual"] == "UNKNOWN", "pair open")
    require(facts["triple_status"] == "OPEN", "triple open")
    require(by_id["diag3_triple_hc0"]["certified_exhaustive_residual"] == facts["triple_unresolved"], "triple residual")
    require(by_id["diag3_triple_hc0"]["global_coverage"] == "77940147/79102449", "triple coverage")

    routes = record["route_tournament"]
    require([row["id"] for row in routes] == ROUTE_IDS, "exact four routes")
    require(all(row["credible"] is True for row in routes), "route credibility")
    require(all(len(row["scores"]) == 8 and all(1 <= n <= 5 for n in row["scores"]) for row in routes), "route scores")
    for route in routes:
        require(route["theorem_quantifier_attachment_proved"] is False, f"quantifier bar: {route['id']}")
        require(route["certified_finite_exhaustive_progress_measure_proved"] is False, f"measure bar: {route['id']}")
        require(route["preregistered_decrease_in_bounded_successor_chain_proved"] is False, f"decrease bar: {route['id']}")
        require(route["construction_eligible"] is False, f"eligibility: {route['id']}")
    counter = routes[2]
    require(counter["exact_retirement_already_supported"] == "GRAPH_ONLY_PAIR_CERTIFICATE", "countermodel scope")
    require(counter["d3_counterexample_supported"] is False, "no D3 counterexample")
    require(routes[3]["default_route"] is False, "D9 baseline only")
    require(facts["cosheaf_result"] == "BOUNDED_NO_GO" and facts["cosheaf_promotable"] is False, "cosheaf no-go")
    require(facts["d9_branch"] == "B-UV-01-unclassified-ambient-components" and facts["d9_ledger_delta"] == "0/9", "D9 baseline")

    bar = record["successor_bar"]
    eligible = [row for row in routes if row["construction_eligible"]]
    require(len(eligible) == bar["eligible_route_count"] == 0, "eligible count")
    require(bar["selected_construction_target"] == "NONE", "no construction target")
    require(bar["selected_successor"] == "NONE / STOP", "stop handoff")

    distance = record["proof_distance"]
    opening = distance["opening"]
    closing = distance["closing"]
    for key in ("score", "score_deficit_to_3_of_9", "named_invariants", "open_load_bearing_obligations", "certified_exhaustive_residual", "global_coverage"):
        require(opening[key] == closing[key], f"no false decrease: {key}")
    require(opening["open_load_bearing_obligations"] == 7, "opening obligations")
    require(distance["strict_decrease"] is False, "distance classification")
    require(record["classification"] == "STALLED" and record["strategy_verdict"] == "STOP", "closing verdict")

    reset = record["automatic_strategy_reset"]
    require(reset["fired"] is True, "reset fired")
    require(reset["same_route_continue_allowed"] is False, "no continue")
    require(reset["required_action"] == "PIVOT_OR_STOP" and reset["applied_action"] == "STOP", "reset action")
    require(record["verification"]["standard_library_only"] is True, "standard library declaration")
    require(record["verification"]["producer_acceptance_imported"] is False, "independence declaration")
    require(record["verification"]["hostile_mutations_required"] == 24, "mutation requirement")
    if check_pins:
        require(record["source_pins"] == EXPECTED_PINS, "source pins")


def hostile_replay(record: dict[str, Any], facts: dict[str, Any]) -> int:
    mutations: list[tuple[str, Any]] = []

    def add(name: str, mutate: Any) -> None:
        candidate = copy.deepcopy(record)
        mutate(candidate)
        mutations.append((name, candidate))

    add("score promotion", lambda r: r.__setitem__("ledger_after", "3/9"))
    add("ledger delta", lambda r: r.__setitem__("ledger_delta", "1/9"))
    add("chart count", lambda r: r["pinned_reconstruction"].__setitem__("compactification_chart_count", 63))
    add("base total", lambda r: r["pinned_reconstruction"]["base_cell_partition"].__setitem__("total", 527532))
    add("algebraic lift", lambda r: r["pinned_reconstruction"]["local_lifted_cell_partition"].__setitem__("algebraic_t", 8390618))
    add("global adjacency", lambda r: r["pinned_reconstruction"].__setitem__("certified_global_adjacencies", 1))
    add("obligation removal", lambda r: r.__setitem__("end_to_end_obligations", r["end_to_end_obligations"][:-1]))
    add("gluing finite", lambda r: r["end_to_end_obligations"][0].__setitem__("certified_exhaustive_residual", 0))
    add("labels covered", lambda r: r["end_to_end_obligations"][1].__setitem__("status", "FINITE_EXACT"))
    add("closure pair", lambda r: r["end_to_end_obligations"][2].__setitem__("certified_global_pairs", 1))
    add("infinity cell", lambda r: r["end_to_end_obligations"][3].__setitem__("certified_global_parent_infinity_cells", 1))
    add("global rank", lambda r: r["end_to_end_obligations"][4].__setitem__("certified_global_rank_replays", 1))
    add("pair closed", lambda r: r["end_to_end_obligations"][5].__setitem__("status", "PROVED"))
    add("triple residual", lambda r: r["end_to_end_obligations"][6].__setitem__("certified_exhaustive_residual", 1162301))
    add("route omitted", lambda r: r.__setitem__("route_tournament", r["route_tournament"][:3]))
    add("direct attached", lambda r: r["route_tournament"][0].__setitem__("theorem_quantifier_attachment_proved", True))
    add("cosheaf measure", lambda r: r["route_tournament"][1].__setitem__("certified_finite_exhaustive_progress_measure_proved", True))
    add("counter D3", lambda r: r["route_tournament"][2].__setitem__("d3_counterexample_supported", True))
    add("D9 default", lambda r: r["route_tournament"][3].__setitem__("default_route", True))
    add("eligible count", lambda r: r["successor_bar"].__setitem__("eligible_route_count", 1))
    add("selected target", lambda r: r["successor_bar"].__setitem__("selected_construction_target", "DIRECT_GLOBAL_MASTER_CLOSURE"))
    add("false decrease", lambda r: r["proof_distance"]["closing"].__setitem__("open_load_bearing_obligations", 6))
    add("converging", lambda r: r.__setitem__("classification", "CONVERGING"))
    add("pin drift", lambda r: r["source_pins"].__setitem__(next(iter(EXPECTED_PINS)), "0" * 64))

    require(len(mutations) == 24, "hostile mutation census")
    rejected = 0
    for name, candidate in mutations:
        try:
            validate(candidate, facts)
        except AssertionError:
            rejected += 1
        else:
            raise AssertionError(f"hostile mutation accepted: {name}")
    return rejected


def main() -> None:
    loaded = sources()
    facts = reconstruct(loaded)
    record = load_json(RESULT)
    validate(record, facts)
    rejected = hostile_replay(record, facts)
    print(
        "PASS D3 theorem-leverage audit: "
        f"64 charts, 527533 base cells, 16935101 local lifts, "
        f"7 open obligations, 4 routes, 0 eligible targets, {rejected}/24 mutations rejected; "
        "verdict STALLED / NONE / STOP"
    )


if __name__ == "__main__":
    main()
