#!/usr/bin/env python3
"""Standard-library verifier for the D3 mixed-100 constructor NULL handoff."""

from __future__ import annotations

from copy import deepcopy
from fractions import Fraction
from hashlib import sha256
import json
from pathlib import Path
import subprocess


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
RESULT_PATH = HERE / "RESULT.json"
MANIFEST_PATH = HERE / "SOURCE_MANIFEST.json"
MEMO_PATH = HERE / "THEOREM_ATTEMPT.md"


def read_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def file_sha256(path: Path) -> str:
    digest = sha256()
    with path.open("rb") as source:
        while block := source.read(1 << 20):
            digest.update(block)
    return digest.hexdigest()


def rank(matrix):
    if not matrix:
        return 0
    work = [[Fraction(value) for value in row] for row in matrix]
    rows, columns = len(work), len(work[0])
    pivot_row = 0
    for column in range(columns):
        pivot = next(
            (row for row in range(pivot_row, rows) if work[row][column]),
            None,
        )
        if pivot is None:
            continue
        work[pivot_row], work[pivot] = work[pivot], work[pivot_row]
        value = work[pivot_row][column]
        work[pivot_row] = [entry / value for entry in work[pivot_row]]
        for row in range(rows):
            if row == pivot_row or not work[row][column]:
                continue
            multiple = work[row][column]
            work[row] = [
                entry - multiple * pivot_entry
                for entry, pivot_entry in zip(work[row], work[pivot_row])
            ]
        pivot_row += 1
        if pivot_row == rows:
            break
    return pivot_row


def transpose(columns):
    return [list(row) for row in zip(*columns, strict=True)]


def multiply(left, right):
    if not left:
        return []
    return [
        [
            sum(left[i][k] * right[k][j] for k in range(len(right)))
            for j in range(len(right[0]))
        ]
        for i in range(len(left))
    ]


def verify_flow_disk(result):
    boundary_1 = [
        [-1, 0, +1, -1, 0, 0, 0, 0, -1],
        [+1, -1, 0, 0, -1, -1, 0, 0, 0],
        [0, +1, -1, 0, 0, 0, -1, -1, 0],
    ]
    boundary_2_columns = [
        [+1, +1, +1, 0, 0, 0, 0, 0, 0],
        [+1, 0, 0, -1, +1, 0, 0, 0, 0],
        [0, +1, 0, 0, 0, -1, +1, 0, 0],
        [0, 0, +1, 0, 0, 0, 0, -1, +1],
        [0, 0, 0, +1, 0, 0, 0, 0, -1],
        [0, 0, 0, 0, -1, +1, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, -1, +1, 0],
    ]
    boundary_2 = transpose(boundary_2_columns)
    assert multiply(boundary_1, boundary_2) == [[0] * 7 for _ in range(3)]
    assert rank(boundary_1) == 3
    assert rank(boundary_2) == 6
    relation = [-1, 1, 1, 1, 1, 1, 1]
    assert all(
        sum(boundary_2[row][column] * relation[column] for column in range(7)) == 0
        for row in range(9)
    )
    assert abs(relation[0]) == 1

    canary = result["row2599_diagnostic"]
    assert canary["parent"] == 2599 and canary["chart"] == 0
    assert canary["relative_chain_ranks"] == {"partial_1": 3, "partial_2": 6, "C2": 7}
    assert canary["relative_homology"] == {"H0": 0, "H1": 0, "H2": "Z"}
    assert canary["primitive_class"] == relation
    assert canary["singleton_nerve_cocycle_evaluation"] == 1
    assert canary["singleton_root_fixed_block_fillers_excluded"]
    assert not canary["genuinely_mixed_carrier_excluded"]
    assert canary["common_proper_triple_ray_exists"]
    assert canary["common_proper_ray_parent_wall"] == "[2467]"
    assert canary["comparison_incidences"] == {"certified": 4, "required": 6}
    assert canary["certified_mixed_d3_cells"] == 0
    assert not canary["absence_is_nonexistence_proof"]
    assert not canary["local_instance_proves_universal_target"]


def verify_manifest(manifest):
    assert manifest["format"] == "d3-mixed-100-carrier-constructor-source-manifest-v1"
    assert manifest["track_id"] == "d3-mixed-100-carrier-constructor"
    assert manifest["lane_opening_commit"] == "1c6519d89335dde215e93887de074ea4e6d6464a"
    assert manifest["lane_opening_tree"] == "ff8a33e13952e86b27f184e3d8c40e768fbeb110"
    assert manifest["canonical_base_commit"] == "fb667bfe33ef9e945a82e9a23b615e67f5f39c0f"
    assert manifest["canonical_base_tree"] == "117850b25cd94f865cb85e681c465b8260dd9c6a"

    sources = manifest["sources"]
    assert len(sources) == 22
    assert len({entry["path"] for entry in sources}) == len(sources)
    for entry in sources:
        path = ROOT / entry["path"]
        assert path.is_file(), entry["path"]
        assert path.stat().st_size == entry["bytes"], entry["path"]
        assert file_sha256(path) == entry["sha256"], entry["path"]

    commands = {entry["command"]: entry for entry in manifest["executions"]}
    assert len(commands) == 6
    assert all(entry["status"] == "PASS" for entry in commands.values())
    assert all(entry["acceptance_use"] for entry in commands.values())
    assert commands[
        "python -B ai/omreal/verify_diag3_joined_flow_triangle.py"
    ]["scope"] == "LOCAL_EXACT_FLOW_DISK_H2_AND_SINGLETON_ROOT_NO_GO_ONLY"
    assert commands[
        "python -B ai/omreal/verify_diag3_row2599_common_proper_escape.py"
    ]["scope"] == "LOCAL_COMMON_PROPER_TRIPLE_RAY_ONLY"

    restrictions = manifest["restrictions"]
    assert not any(restrictions.values())

    commit = subprocess.run(
        ["git", "cat-file", "-p", manifest["lane_opening_commit"]],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    ).stdout
    assert f"tree {manifest['lane_opening_tree']}" in commit
    assert f"parent {manifest['canonical_base_commit']}" in commit


def validate(result, manifest, check_files=True):
    assert result["format"] == "d3-mixed-100-carrier-constructor-result-v1"
    assert result["cycle_id"] == "2026-09-03-d3-mixed-block-100-universal-carrier-gate1"
    assert result["track_id"] == "d3-mixed-100-carrier-constructor"
    assert result["role"] == "constructive-prover"
    assert result["owned_surface"] == "ops/team/d3-mixed-100-carrier-constructor"
    assert result["frozen_base"]["lane_opening_commit"] == manifest["lane_opening_commit"]
    assert result["frozen_base"]["canonical_base_commit"] == manifest["canonical_base_commit"]
    assert manifest["sources"][0]["path"] == "ops/research-team/PROTOCOL.md"
    assert manifest["sources"][0]["sha256"] == (
        "c3fbec5b483426fcce97a523ba1ea1edc3e561cb33a1c4e5e957674e4270a246"
    )
    assert result["handoff"] == "NULL"
    assert result["assessment"] == "NULL_STALLED_STOP"
    assert result["positive_token"] is None and result["negative_token"] is None
    assert not result["constructor_self_acceptance"]

    edge = result["first_missing_edge"]
    assert edge["id"] == "O3_MIXED_GEOMETRIC_RELATIVE_BOUNDARY_SURJECTIVITY"
    assert edge["from"] == "DECLARED_L_SOURCE_INTERFACE"
    assert edge["to"] == "O3_universal_mixed_chain"
    assert not edge["proof_reachable_within_lane_ceiling"]

    target = result["target_status"]
    assert target["O3_universal_mixed_chain"] == "OPEN"
    assert target["O4_arbitrary_flag_coherence"] == "OPEN_BLOCKED_BEHIND_O3_AND_MIXED_FUNCTOR_DESCENT"
    assert not target["O3_proved"] and not target["O4_proved"]
    assert not target["full_quantifier_obstruction_proved"]
    assert not target["ansatz_failure_promoted_to_negative"]

    quantifiers = result["quantified_scope_preserved"]
    assert quantifiers["face_flags"] == "ALL_COMPOSABLE_FLAGS_NOT_ONLY_CODIMENSION_ONE"
    assert quantifiers["relative_infinity"] == "TRUE_PARENT_INFINITY_ONLY"
    assert len(quantifiers["specializations"]) == 9
    assert set(quantifiers["specializations"]) == {
        "SUPPORT_LOSS", "ZERO_WEIGHT", "CHART_TRANSITION", "MONODROMY",
        "PARENT_BOUNDARY", "PARENT_RANK", "WITNESS_RANK", "RESIDUAL_WALL",
        "ACTIVE_BLOCK_PERMUTATION",
    }

    interface = result["interface_audit"]
    assert len(interface["provided"]) == 7
    assert len(interface["not_provided_or_derived"]) == 7
    assert "FINITE_GEOMETRIC_MIXED_C3_FUNCTOR" in interface["not_provided_or_derived"]
    assert "RELATIVE_BOUNDARY_SURJECTIVITY_ON_RELEVANT_PRIMITIVES" in interface["not_provided_or_derived"]
    assert "NATURAL_RIGHT_INVERSE_OF_MIXED_RELATIVE_BOUNDARY" in interface["not_provided_or_derived"]
    assert not interface["lower_cycle_condition_is_sufficient_for_mixed_boundary"]

    reformulation = result["functorial_reformulation"]
    assert reformulation["required_natural_boundary"] == "b:M3_MIX_TO_Z2_REL"
    assert "b_COMPOSE_s_EQUALS_INCLUSION" in reformulation["required_natural_section"]
    assert not reformulation["interface_contains_required_new_functor"]
    assert not reformulation["interface_contains_required_natural_section"]

    witness = result["algebraic_axiom_independence_witness"]
    assert witness["role"] == "LOWER_CHAIN_AXIOM_INDEPENDENCE_ONLY_NOT_AN_ADMISSIBLE_L_SOURCE_COUNTEREXAMPLE"
    assert witness["ranks"] == {"C0": 0, "C1": 0, "C2": 1, "C3_supplied": 0}
    assert witness["primitive_alpha"] == [1]
    assert witness["d1_d2_zero"] and witness["alpha_is_primitive"]
    assert witness["H2"] == "Z"
    assert not witness["proves_algebraic_lower_axioms_imply_boundary"]
    assert not witness["source_derived_geometric_admissibility_claimed"]
    assert not witness["universal_negative_consequence"]

    routes = {row["id"]: row for row in result["candidate_routes"]}
    assert set(routes) == {
        "FORMAL_FUNCTORIAL_CONE", "ACYCLIC_CARRIER_EXTENSION",
        "ROW2599_COMMON_RAY_CONE", "OBJECTWISE_FILLERS_THEN_TRANSPORT",
    }
    assert all(not row["accepted_for_O3"] for row in routes.values())
    assert routes["FORMAL_FUNCTORIAL_CONE"]["algebraic_boundary_and_flag_coherence"] == "AVAILABLE_BY_SETTING_D3_EQUAL_Z2"
    assert "4_OF_6" in routes["ROW2599_COMMON_RAY_CONE"]["first_failure"]

    verify_flow_disk(result)

    naturality = result["naturality_frontier"]
    assert naturality["lower_face_category_exists_by_interface"]
    assert not any(
        naturality[key]
        for key in (
            "mixed_degree_three_face_functor_constructed",
            "natural_filler_section_constructed",
            "codimension_one_checks_suffice",
            "arbitrary_flag_equality_proved",
            "monodromy_descent_proved",
            "true_parent_infinity_properness_proved",
        )
    )

    distance = result["proof_distance"]
    assert distance["canonical_opening"] == distance["canonical_closing_recommendation"]
    assert distance["selected_route_opening"] == distance["selected_route_closing"]
    assert distance["selected_route_delta"] == 0
    assert not distance["minimum_acceptable_decrease_met"]
    assert distance["trajectory"] == "STALLED"
    assert not distance["same_route_continue"]
    assert distance["required_action"] == "STOP"

    guards = result["accounting_guards"]
    assert guards["formal_shape_count"] == 10
    assert guards["provisional_universal_shape_clauses"] == ["(0)", "(1)", "(2)"]
    assert guards["provisional_shape_ratio"] == "3/10"
    assert not guards["formal_taxonomy_is_global_denominator"]
    assert not guards["formal_taxonomy_is_end_to_end_coverage"]
    assert guards["pair_residual"] == guards["pair_coverage"] == "UNKNOWN"
    assert (guards["canonical_ledger_before"], guards["canonical_ledger_after"], guards["canonical_ledger_delta"]) == ("2/9", "2/9", "0/9")

    scope = result["scope_compliance"]
    assert scope["edited_only_owned_surface"]
    assert not any(value for key, value in scope.items() if key != "edited_only_owned_surface")
    assert len(result["replays"]) == 6
    assert all(row["status"] == "PASS" for row in result["replays"])
    assert "NO_EXACT_ADMISSIBLE_OBSTRUCTION_TO_THEIR_FULL_CONJUNCTION" in result["nonconsequences"]
    assert "NO_COUNTEREXAMPLE_TO_A_GENUINELY_MIXED_CARRIER" in result["nonconsequences"]
    assert "NO_LEDGER_CHANGE" in result["nonconsequences"]
    assert result["verification"]["standard_library_only"]
    assert result["verification"]["hostile_mutations_required"] == 30
    assert len(result["deliverables"]) == 4

    if check_files:
        verify_manifest(manifest)
        memo = MEMO_PATH.read_text(encoding="utf-8")
        for phrase in (
            "NULL / STALLED / STOP",
            "O3_MIXED_GEOMETRIC_RELATIVE_BOUNDARY_SURJECTIVITY",
            "not a negative result",
            "Formal functorial cone",
            "Acyclic-carrier extension",
            "Why the handoff is NULL rather than NEGATIVE",
            "Selected-route residual: `2/2 -> 2/2`",
        ):
            assert phrase in memo


def expect_reject(name, mutate, result, manifest):
    candidate_result = deepcopy(result)
    candidate_manifest = deepcopy(manifest)
    mutate(candidate_result, candidate_manifest)
    try:
        validate(candidate_result, candidate_manifest, check_files=False)
    except (AssertionError, KeyError, TypeError, ValueError):
        return
    raise AssertionError(f"hostile mutation accepted: {name}")


def main():
    result = read_json(RESULT_PATH)
    manifest = read_json(MANIFEST_PATH)
    validate(result, manifest, check_files=True)

    mutations = [
        ("promote-positive", lambda r, m: r.__setitem__("handoff", "POSITIVE")),
        ("promote-negative", lambda r, m: r.__setitem__("handoff", "NEGATIVE")),
        ("self-accept", lambda r, m: r.__setitem__("constructor_self_acceptance", True)),
        ("invent-positive-token", lambda r, m: r.__setitem__("positive_token", "PROVED")),
        ("prove-o3", lambda r, m: r["target_status"].__setitem__("O3_proved", True)),
        ("prove-o4", lambda r, m: r["target_status"].__setitem__("O4_proved", True)),
        ("claim-obstruction", lambda r, m: r["target_status"].__setitem__("full_quantifier_obstruction_proved", True)),
        ("ansatz-negative", lambda r, m: r["target_status"].__setitem__("ansatz_failure_promoted_to_negative", True)),
        ("move-first-edge", lambda r, m: r["first_missing_edge"].__setitem__("to", "O4_arbitrary_flag_coherence")),
        ("reachable-proof", lambda r, m: r["first_missing_edge"].__setitem__("proof_reachable_within_lane_ceiling", True)),
        ("drop-specialization", lambda r, m: r["quantified_scope_preserved"]["specializations"].pop()),
        ("codim-one-only", lambda r, m: r["quantified_scope_preserved"].__setitem__("face_flags", "CODIMENSION_ONE")),
        ("artificial-infinity", lambda r, m: r["quantified_scope_preserved"].__setitem__("relative_infinity", "LOCAL_BOX_FACE")),
        ("invent-mixed-c3", lambda r, m: r["interface_audit"]["not_provided_or_derived"].remove("FINITE_GEOMETRIC_MIXED_C3_FUNCTOR")),
        ("invent-surjectivity", lambda r, m: r["interface_audit"].__setitem__("lower_cycle_condition_is_sufficient_for_mixed_boundary", True)),
        ("invent-section", lambda r, m: r["functorial_reformulation"].__setitem__("interface_contains_required_natural_section", True)),
        ("promote-witness", lambda r, m: r["algebraic_axiom_independence_witness"].__setitem__("source_derived_geometric_admissibility_claimed", True)),
        ("witness-negative", lambda r, m: r["algebraic_axiom_independence_witness"].__setitem__("universal_negative_consequence", True)),
        ("accept-formal-cone", lambda r, m: r["candidate_routes"][0].__setitem__("accepted_for_O3", True)),
        ("accept-acyclic-template", lambda r, m: r["candidate_routes"][1].__setitem__("accepted_for_O3", True)),
        ("erase-h2", lambda r, m: r["row2599_diagnostic"]["relative_homology"].__setitem__("H2", 0)),
        ("nonprimitive-class", lambda r, m: r["row2599_diagnostic"]["primitive_class"].__setitem__(0, -2)),
        ("exclude-mixed", lambda r, m: r["row2599_diagnostic"].__setitem__("genuinely_mixed_carrier_excluded", True)),
        ("invent-incidences", lambda r, m: r["row2599_diagnostic"]["comparison_incidences"].__setitem__("certified", 6)),
        ("codim-suffices", lambda r, m: r["naturality_frontier"].__setitem__("codimension_one_checks_suffice", True)),
        ("close-route", lambda r, m: r["proof_distance"].__setitem__("selected_route_closing", [])),
        ("continue-route", lambda r, m: r["proof_distance"].__setitem__("same_route_continue", True)),
        ("false-denominator", lambda r, m: r["accounting_guards"].__setitem__("formal_taxonomy_is_global_denominator", True)),
        ("ledger-promotion", lambda r, m: r["accounting_guards"].__setitem__("canonical_ledger_after", "3/9")),
        ("corrupt-source-pin", lambda r, m: m["sources"][0].__setitem__("sha256", "0" * 64)),
    ]
    assert len(mutations) == result["verification"]["hostile_mutations_required"]
    for name, mutate in mutations:
        expect_reject(name, mutate, result, manifest)

    print("PASS 22 source hash/length pins and immutable lane opening")
    print("PASS exact flow disk: d1*d2=0, ranks 3/6, primitive H2=Z")
    print("PASS interface audit: lower functor supplied; mixed C3/boundary section absent")
    print("PASS logical scope: algebraic witness is not an admissible counterexample")
    print("PASS naturality scope: O4 open on arbitrary flags and monodromy")
    print("PASS proof distance: selected route 2/2 -> 2/2; ledger 2/9")
    print(f"PASS hostile mutations rejected: {len(mutations)}")
    print("VERDICT NULL / STALLED / STOP at O3 mixed relative-boundary surjectivity")


if __name__ == "__main__":
    main()
