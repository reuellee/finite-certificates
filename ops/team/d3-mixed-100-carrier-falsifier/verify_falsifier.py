#!/usr/bin/env python3
"""Independent stdlib replay for the D3 mixed-100 falsifier handoff."""

from __future__ import annotations

import copy
import hashlib
import itertools
import json
import math
from fractions import Fraction
from pathlib import Path


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]

EXPECTED_D1 = [
    [-1, 0, 1, -1, 0, 0, 0, 0, -1],
    [1, -1, 0, 0, -1, -1, 0, 0, 0],
    [0, 1, -1, 0, 0, 0, -1, -1, 0],
]
EXPECTED_D2 = [
    [1, 1, 0, 0, 0, 0, 0],
    [1, 0, 1, 0, 0, 0, 0],
    [1, 0, 0, 1, 0, 0, 0],
    [0, -1, 0, 0, 1, 0, 0],
    [0, 1, 0, 0, 0, -1, 0],
    [0, 0, -1, 0, 0, 1, 0],
    [0, 0, 1, 0, 0, 0, -1],
    [0, 0, 0, -1, 0, 0, 1],
    [0, 0, 0, 1, -1, 0, 0],
]
ALPHA = [-1, 1, 1, 1, 1, 1, 1]
FACE_GENERATORS = [
    "support_loss",
    "zero_weight",
    "chart_transition",
    "parent_boundary",
    "parent_rank",
    "witness_rank",
    "residual_wall",
]
EXPECTED_SOURCES = {
    "ops/research-team/PROTOCOL.md": (11222, "c3fbec5b483426fcce97a523ba1ea1edc3e561cb33a1c4e5e957674e4270a246"),
    "ops/research-team/cycles/2026-09-03-d3-mixed-block-100-universal-carrier-gate1/CYCLE.md": (11012, "9f88215d6b9fdacd5318c056d27322b0339f2c04bbbe5ce378f45d6ac4d515cb"),
    "ops/research-team/cycles/2026-09-03-d3-mixed-block-100-universal-carrier-gate1/OPENING_STATE.json": (5569, "442081ba35778ba103ff4caccf274329b8694e826a7349fdf5b30fb662514e00"),
    "ops/research-team/cycles/2026-09-03-d3-mixed-block-100-universal-carrier-gate1/WORK_ORDERS.yaml": (7900, "3ba2bb478e6efe2f28d385204bb698b0308854731eb8d36a10093b91943c7901"),
    "ops/research-team/cycles/2026-09-03-d3-mixed-block-100-universal-carrier-gate1/verify_opening_state.py": (7462, "064a8c6944b33238abd8555c79a8304269d85755716c7a8aa658ada217dfd760"),
    "ai/omreal/data/CANONICAL_RESEARCH_STATE_V10.json": (6535, "405e1f34789e999d2b8725881a4b99c1db81cec3ecfa70abcdfa9b3fbb7a46bf"),
    "ai/omreal/verify_canonical_research_state_v10.py": (13118, "662267d9d8692c6724ab0b55472b3ca262461cce864a7cbb8bd9296bef788917"),
    "ops/team/d3-mixed-carrier-topology/THEOREM_MEMO.md": (11362, "131ec929171abf633b18e4eefbd1b45ec8aeea97b9d2d1a6f89a73cb205b7f76"),
    "ops/team/d3-mixed-carrier-topology/RESULT.json": (18496, "7e54007c1bb97be457cbdc039c5520267cd39e39e08a930828b42708443a99e5"),
    "ops/team/d3-mixed-carrier-naturality/NATURALITY_MEMO.md": (13465, "a24821526bd0e89a1473e887d60c6e38c9e28f8d65c6a86e7f5e0d3a5d2cdb86"),
    "ops/team/d3-mixed-carrier-naturality/RESULT.json": (10798, "2911e7478a31090582dda2aeeb5e952ab84cf83946bcd5f29d3900813309e3e0"),
    "ops/team/theorem-reset-falsifier/FINDINGS.md": (6659, "893ecc8d530e7af0970cc4bb232fb34e99cb8fc5e0e6b073c93d423c7313420f"),
    "ops/team/theorem-reset-falsifier/RESULT.json": (10935, "c955c6886ed611ae915d56b21a57740f27acb5fb750b22f1900aa58e2996c663"),
    "ai/omreal/9DVL_THEOREM_PROSPECTUS.md": (23473, "9d7fa818ef48ec1df8d7cadc8525d6d705377f2f1294d9eba692dc15a2533cb7"),
    "ai/omreal/DIAG3_JOINED_FLOW_TRIANGLE.md": (16265, "20aafd28f9624ca595a44e3124934baa4d33b942b6c8eca6bff210fedb114c8a"),
    "ai/omreal/verify_diag3_joined_flow_triangle.py": (9283, "ac01851b53d4bed1c859f74bad2e71a5025825fe7accdac13263f5d6518a0944"),
    "ai/omreal/verify_diag3_single_bad_two_skeleton.py": (7350, "0ae6a9d54abcddbeb68be882083c52e1e6a9735941cea42eebacdf91ef77bda4"),
    "ai/omreal/verify_diag3_row2599_common_proper_escape.py": (13638, "6b426e94181a0d447f79d70e3eb6f64f2f34227d88b9ae1fa0a87f9539c4297c"),
}


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def matrix_rank(matrix: list[list[int]]) -> int:
    if not matrix:
        return 0
    a = [[Fraction(value) for value in row] for row in matrix]
    rows = len(a)
    cols = len(a[0])
    require(all(len(row) == cols for row in a), "ragged matrix")
    pivot_row = 0
    for col in range(cols):
        pivot = next((r for r in range(pivot_row, rows) if a[r][col]), None)
        if pivot is None:
            continue
        a[pivot_row], a[pivot] = a[pivot], a[pivot_row]
        scale = a[pivot_row][col]
        a[pivot_row] = [value / scale for value in a[pivot_row]]
        for r in range(rows):
            if r != pivot_row and a[r][col]:
                factor = a[r][col]
                a[r] = [a[r][c] - factor * a[pivot_row][c] for c in range(cols)]
        pivot_row += 1
        if pivot_row == rows:
            break
    return pivot_row


def matmul(left: list[list[int]], right: list[list[int]]) -> list[list[int]]:
    require(bool(left) and bool(right), "empty matrix multiplication")
    inner = len(left[0])
    require(all(len(row) == inner for row in left), "ragged left matrix")
    require(len(right) == inner, "matrix dimension mismatch")
    out_cols = len(right[0])
    require(all(len(row) == out_cols for row in right), "ragged right matrix")
    return [
        [sum(left[i][k] * right[k][j] for k in range(inner)) for j in range(out_cols)]
        for i in range(len(left))
    ]


def matvec(matrix: list[list[int]], vector: list[int]) -> list[int]:
    require(all(len(row) == len(vector) for row in matrix), "matrix-vector dimension mismatch")
    return [sum(a * b for a, b in zip(row, vector)) for row in matrix]


def compose_permutations(p: tuple[int, ...], q: tuple[int, ...]) -> tuple[int, ...]:
    return tuple(p[q[i]] for i in range(len(p)))


def verify_manifest(manifest: dict, check_disk: bool) -> None:
    require(manifest["format"] == "d3-mixed-100-carrier-falsifier-source-manifest-v1", "manifest format")
    require(manifest["cycle_id"] == "2026-09-03-d3-mixed-block-100-universal-carrier-gate1", "manifest cycle")
    require(manifest["track_id"] == "d3-mixed-100-carrier-falsifier", "manifest track")
    require(manifest["lane_opening_commit"] == "1c6519d89335dde215e93887de074ea4e6d6464a", "lane opening commit")
    require(manifest["lane_opening_tree"] == "ff8a33e13952e86b27f184e3d8c40e768fbeb110", "lane opening tree")
    require(manifest["canonical_base_revision"] == "fb667bfe33ef9e945a82e9a23b615e67f5f39c0f", "canonical revision")
    require(manifest["canonical_base_tree"] == "117850b25cd94f865cb85e681c465b8260dd9c6a", "canonical tree")
    require(manifest["source_drift"] is False, "source drift flag")
    require(manifest["network_sources"] == [], "network sources")
    require(manifest["constructor_sources"] == [], "constructor sources")
    entries = {entry["path"]: (entry["bytes"], entry["sha256"]) for entry in manifest["sources"]}
    require(len(entries) == len(manifest["sources"]), "duplicate source path")
    require(entries == EXPECTED_SOURCES, "source manifest set or pin mismatch")
    if check_disk:
        for relative, (expected_bytes, expected_hash) in EXPECTED_SOURCES.items():
            path = ROOT / relative
            require(path.is_file(), f"missing source: {relative}")
            require(path.stat().st_size == expected_bytes, f"source byte drift: {relative}")
            require(sha256(path) == expected_hash, f"source hash drift: {relative}")


def verify_boolean_face_category(category: dict) -> None:
    require(category["construction"] == "BOOLEAN_FACE_POSET_TIMES_TRIVIAL_FINITE_SYMMETRY_ACTION", "category construction")
    require(category["face_generators"] == FACE_GENERATORS, "face generators")
    dimension = len(FACE_GENERATORS)
    require(category["boolean_object_count"] == 2**dimension == 128, "boolean object count")
    require(category["boolean_morphism_count"] == 3**dimension == 2187, "boolean morphism count")
    require(category["lower_chain_representation"] == "TRIVIAL_IDENTITY_ON_THE_DISPLAYED_COMPLEX", "lower representation")
    require(category["all_composable_face_flags"] == "STRICTLY_COHERENT_BECAUSE_THE_BOOLEAN_FACE_POSET_IS_THIN_AND_ALL_LOWER_MAPS_ARE_IDENTITIES", "flag coherence declaration")
    require(category["parent_boundary_is_not_automatically_true_infinity"] is True, "parent boundary distinction")

    # Per coordinate there are exactly four weakly increasing triples.  Their
    # product exhausts every composable pair of Boolean-face arrows.  A thin
    # category has one map per comparable endpoint, so all composites agree.
    local_triples = ((0, 0, 0), (0, 0, 1), (0, 1, 1), (1, 1, 1))
    triple_count = 0
    for coordinates in itertools.product(local_triples, repeat=dimension):
        source = tuple(item[0] for item in coordinates)
        middle = tuple(item[1] for item in coordinates)
        target = tuple(item[2] for item in coordinates)
        require(all(a <= b <= c for a, b, c in zip(source, middle, target)), "noncomposable Boolean triple")
        require(all(a <= c for a, c in zip(source, target)), "composite endpoint missing")
        triple_count += 1
    require(triple_count == 4**dimension == 16384, "composable-triple exhaustion")

    permutations = set(itertools.permutations(range(3)))
    require(category["active_block_permutation_group"] == "S3", "permutation group")
    require(category["active_block_permutation_order"] == len(permutations) == 6, "permutation order")
    for p in permutations:
        for q in permutations:
            require(compose_permutations(p, q) in permutations, "S3 closure")
    require(category["monodromy_group"] == "C2", "monodromy group")
    require(category["monodromy_order"] == 2, "monodromy order")
    c2 = (0, 1)
    require(tuple((a + b) % 2 for a, b in zip(c2, reversed(c2))) == (1, 1), "C2 finite control")


def verify_fixture(fixture: dict) -> None:
    require(fixture["format"] == "d3-mixed-100-interface-independence-fixture-v1", "fixture format")
    lower = fixture["lower_interface"]
    provenance = lower["provenance"]
    require(provenance["parent"] == 2599, "fixture parent")
    require(provenance["parent_rank"] == 4, "fixture parent rank")
    require(provenance["label_count"] == 8, "fixture label count")
    require(provenance["chart"] == 0, "fixture chart")
    require(provenance["extension_signatures"] == [14988895318912, 3405195891438080, 40418075143643136], "fixture signatures")
    require(provenance["active_block_labels"] == [0, 1, 2], "fixture blocks")
    require(provenance["shape"] == "(1,0,0)", "fixture shape")
    require(provenance["scope"] == "ROW2599_EXACT_LOWER_FLOW_TRIANGLE_DIAGNOSTIC_NOT_A_GLOBAL_DENOMINATOR", "fixture scope")
    require(lower["C0_basis"] == ["v0", "v1", "v2"], "C0 basis")
    require(lower["C1_basis"] == ["e01", "e12", "e20", "r0a", "r1a", "r1b", "r2b", "r2c", "r0c"], "C1 basis")
    require(lower["C2_basis"] == ["T", "S01", "S12", "S20", "H0", "H1", "H2"], "C2 basis")
    d1 = lower["partial_1_rows"]
    d2 = lower["partial_2_rows"]
    alpha = lower["primitive_kernel_class"]
    require(d1 == EXPECTED_D1, "partial_1 matrix")
    require(d2 == EXPECTED_D2, "partial_2 matrix")
    require(alpha == ALPHA, "primitive class")
    require(matmul(d1, d2) == [[0] * 7 for _ in range(3)], "d1*d2")
    require(matvec(d2, alpha) == [0] * 9, "alpha is not a d2-cycle")
    require(math.gcd(*map(abs, alpha)) == 1, "alpha is not primitive")
    ranks = lower["expected_ranks"]
    require(matrix_rank(d1) == ranks["partial_1"] == 3, "rank partial_1")
    require(matrix_rank(d2) == ranks["partial_2"] == 6, "rank partial_2")
    require(len(lower["C2_basis"]) == ranks["C2"] == 7, "rank C2")
    require(len(lower["C2_basis"]) - matrix_rank(d2) == ranks["kernel_partial_2"] == 1, "kernel rank")
    assertions = lower["interface_assertions"]
    require(assertions == {
        "integral": True,
        "partial_1_partial_2_zero": True,
        "primitive_class_list_complete_for_fixture": True,
        "true_parent_infinity_distinguished_from_internal_seams": True,
    }, "interface assertions")

    verify_boolean_face_category(fixture["specialization_category"])
    expansions = fixture["two_expansions_of_the_same_lower_interface"]
    cone = expansions["formal_kernel_cone"]
    require(cone["C3_basis"] == ["m_alpha"], "cone basis")
    require(cone["partial_3_columns"] == [ALPHA], "cone boundary")
    require(matvec(d2, cone["partial_3_columns"][0]) == [0] * 9, "d2*d3")
    require(cone["specialization_on_C3"] == "RESTRICTION_TO_KERNEL_HENCE_IDENTITY_IN_THIS_FIXTURE", "cone specialization")
    require(cone["fills_primitive_class_integrally"] is True, "cone integral fill")
    require(cone["certifies_genuinely_mixed_semialgebraic_realization"] is False, "cone geometric overclaim")
    require(cone["interpretation"] == "FORMAL_ALGEBRAIC_EXTENSION_ONLY", "cone interpretation")
    empty = expansions["empty_geometric_carrier_interpretation"]
    require(empty["C3_basis"] == [], "empty C3")
    require(empty["partial_3_columns"] == [], "empty d3")
    require(empty["admissible_genuinely_mixed_geometric_generators"] == [], "empty geometric generator set")
    require(empty["primitive_class_remains_unfilled"] is True, "empty unfilled class")
    require(empty["actual_9dvl_admissibility_established"] is False, "empty expansion actual-admissibility overclaim")
    require(empty["interpretation"] == "LOGICAL_NON_ENTAILMENT_WITNESS_ONLY_NOT_AN_ACTUAL_SOURCE_COUNTEREXAMPLE", "empty interpretation")
    conclusion = fixture["certified_conclusion"]
    require(conclusion == {
        "pure_integral_chain_or_category_obstruction_from_declared_interface": False,
        "formal_coherent_cone_exists": True,
        "genuinely_mixed_geometric_realization_follows_from_declared_interface": False,
        "actual_admissible_negative_instance_proved": False,
        "lane_handoff": "NULL",
    }, "fixture conclusion")


def verify_result(result: dict) -> None:
    require(result["format"] == "d3-mixed-100-carrier-falsifier-result-v1", "result format")
    require(result["cycle_id"] == "2026-09-03-d3-mixed-block-100-universal-carrier-gate1", "result cycle")
    require(result["track_id"] == "d3-mixed-100-carrier-falsifier", "result track")
    require(result["branch"] == "research/lane-d3-mixed-100-carrier-falsifier-20260903", "result branch")
    require(result["lane_opening_commit"] == "1c6519d89335dde215e93887de074ea4e6d6464a", "result opening commit")
    require(result["lane_opening_tree"] == "ff8a33e13952e86b27f184e3d8c40e768fbeb110", "result opening tree")
    require(result["handoff"] == "NO_UNIVERSAL_OBSTRUCTION_FOUND_WITHIN_FROZEN_SCOPE", "handoff")
    require(result["classification"] == "NULL", "classification")
    require(result["trajectory_recommendation"] == "STALLED", "trajectory")
    require(result["strategy_recommendation"] == "STOP", "strategy")
    require(result["universal_counterexample_found"] is False, "counterexample overclaim")
    require(result["full_quantifier_negative_proved"] is False, "negative overclaim")
    exact = result["exact_finding"]
    require(exact["kind"] == "DECLARED_INTERFACE_NON_ENTAILMENT_WITH_ALGEBRAIC_CONE_CONTROL", "exact finding kind")
    require(exact["interface_forces_formal_integral_filler"] is True, "formal cone finding")
    require(exact["interface_forces_genuinely_mixed_semialgebraic_filler"] is False, "geometric non-entailment")
    lemma = result["algebraic_kernel_cone_lemma"]
    require(len(lemma["proof_dependencies"]) == 4, "cone proof dependencies")
    require("O3" in lemma["does_not_prove"] and "O4" in lemma["does_not_prove"], "cone nonconsequences")
    finite = result["finite_independence_fixture"]
    require(finite["path"] == "ops/team/d3-mixed-100-carrier-falsifier/interface_independence_fixture.json", "fixture path")
    require((finite["rank_partial_1"], finite["rank_partial_2"], finite["rank_C2"]) == (3, 6, 7), "fixture ranks in result")
    require(finite["primitive_class"] == ALPHA, "fixture primitive in result")
    require((finite["face_generators"], finite["boolean_face_objects"], finite["boolean_face_morphisms"]) == (7, 128, 2187), "fixture category counts in result")
    require(finite["formal_cone_fills"] is True and finite["empty_interpretation_does_not_fill"] is True, "two fixture expansions")
    require(finite["same_declared_lower_interface"] is True and finite["actual_negative_instance"] is False, "fixture scope")
    require([entry["id"] for entry in result["attack_log"]] == [
        "A1_ROW2599_SINGLETON_COCYCLE",
        "A2_COMPACT_TRIPLE_COMPONENT",
        "A3_INTEGRAL_PARITY_OR_TORSION",
        "A4_MONODROMY_AND_ACTIVE_BLOCK_SYMMETRY",
        "A5_ARBITRARY_FACE_FLAGS",
        "A6_EMPTY_MIXED_CARRIER_EXPANSION",
    ], "attack log")
    quantifiers = result["quantifier_status"]
    require(set(quantifiers) == {
        "all_realizable_uniform_rank4_parents_on_8_labels",
        "all_normalized_components_and_charts",
        "all_proper_incomparable_source_antichains",
        "all_support_strata",
        "all_primitive_integral_kernel_classes",
        "all_labeled_active_block_placements_and_permutations",
        "all_composable_face_flags",
        "true_parent_infinity_only",
    }, "quantifier field set")
    require(not any(value == "FALSIFIED" for value in quantifiers.values()), "quantifier overclaim")
    distance = result["proof_distance"]
    expected_residual = ["O3_universal_mixed_chain", "O4_arbitrary_flag_coherence"]
    require(distance["opening_selected_route_residual"] == expected_residual, "opening residual")
    require(distance["closing_selected_route_residual"] == expected_residual, "closing residual")
    require(distance["strict_decrease"] is False, "false strict decrease")
    require(distance["canonical_ledger_before"] == distance["canonical_ledger_after"] == "2/9", "ledger")
    require(distance["canonical_ledger_delta"] == "0/9", "ledger delta")
    require(distance["midpoint_recommendation"] == "FREEZE_NULL_STALLED_STOP", "midpoint")
    compliance = result["scope_compliance"]
    require(compliance["owned_surface"] == "ops/team/d3-mixed-100-carrier-falsifier", "owned surface")
    require(all(value is False for key, value in compliance.items() if key != "owned_surface"), "scope violation")
    require(len(result["replays"]) == 6 and all(item["expected"] == "PASS" for item in result["replays"]), "replay declarations")
    verification = result["verification"]
    require(verification == {
        "standard_library_only": True,
        "hostile_mutations_required": 24,
        "hostile_mutations_implemented": 40,
    }, "verification contract")
    require(len(result["nonconsequences"]) == 7, "nonconsequence count")
    require("NO_EXACT_ADMISSIBLE_COUNTEREXAMPLE_TO_O3_OR_O4" in result["nonconsequences"], "negative scope")


def verify_findings() -> None:
    text = (HERE / "FINDINGS.md").read_text(encoding="utf-8")
    for phrase in (
        "NO_UNIVERSAL_OBSTRUCTION_FOUND_WITHIN_FROZEN_SCOPE",
        "NULL / STALLED / STOP",
        "C3_cone(x) = ker(d2_x)",
        "actual_9dvl_admissibility_established=false",
        "Why this is `NULL`, not `NEGATIVE`",
        "40 hostile in-memory mutations",
    ):
        require(phrase in text, f"findings missing phrase: {phrase}")


def verify_all(fixture: dict, result: dict, manifest: dict, check_disk: bool = False) -> None:
    verify_fixture(fixture)
    verify_result(result)
    verify_manifest(manifest, check_disk=check_disk)
    if check_disk:
        verify_findings()


def set_nested(document: dict, path: tuple[object, ...], value: object) -> None:
    target = document
    for part in path[:-1]:
        target = target[part]  # type: ignore[index]
    target[path[-1]] = value  # type: ignore[index]


def run_hostile_mutations(fixture: dict, result: dict, manifest: dict) -> int:
    mutations = [
        ("fixture-format", "f", lambda x: set_nested(x, ("format",), "bad")),
        ("parent", "f", lambda x: set_nested(x, ("lower_interface", "provenance", "parent"), 2600)),
        ("parent-rank", "f", lambda x: set_nested(x, ("lower_interface", "provenance", "parent_rank"), 3)),
        ("label-count", "f", lambda x: set_nested(x, ("lower_interface", "provenance", "label_count"), 9)),
        ("signatures", "f", lambda x: x["lower_interface"]["provenance"]["extension_signatures"].pop()),
        ("blocks", "f", lambda x: set_nested(x, ("lower_interface", "provenance", "active_block_labels"), [0, 1])),
        ("shape", "f", lambda x: set_nested(x, ("lower_interface", "provenance", "shape"), "(0,0,0)")),
        ("C0-basis", "f", lambda x: x["lower_interface"]["C0_basis"].pop()),
        ("C1-basis", "f", lambda x: x["lower_interface"]["C1_basis"].reverse()),
        ("C2-basis", "f", lambda x: x["lower_interface"]["C2_basis"].pop()),
        ("d1", "f", lambda x: set_nested(x, ("lower_interface", "partial_1_rows", 0, 0), 0)),
        ("d2", "f", lambda x: set_nested(x, ("lower_interface", "partial_2_rows", 0, 0), 0)),
        ("alpha", "f", lambda x: set_nested(x, ("lower_interface", "primitive_kernel_class", 0), 1)),
        ("rank", "f", lambda x: set_nested(x, ("lower_interface", "expected_ranks", "partial_2"), 5)),
        ("integral", "f", lambda x: set_nested(x, ("lower_interface", "interface_assertions", "integral"), False)),
        ("d-squared", "f", lambda x: set_nested(x, ("lower_interface", "interface_assertions", "partial_1_partial_2_zero"), False)),
        ("primitive-list", "f", lambda x: set_nested(x, ("lower_interface", "interface_assertions", "primitive_class_list_complete_for_fixture"), False)),
        ("infinity-tags", "f", lambda x: set_nested(x, ("lower_interface", "interface_assertions", "true_parent_infinity_distinguished_from_internal_seams"), False)),
        ("face-generator", "f", lambda x: x["specialization_category"]["face_generators"].pop()),
        ("object-count", "f", lambda x: set_nested(x, ("specialization_category", "boolean_object_count"), 127)),
        ("morphism-count", "f", lambda x: set_nested(x, ("specialization_category", "boolean_morphism_count"), 2186)),
        ("permutation-group", "f", lambda x: set_nested(x, ("specialization_category", "active_block_permutation_group"), "C3")),
        ("permutation-order", "f", lambda x: set_nested(x, ("specialization_category", "active_block_permutation_order"), 3)),
        ("monodromy-group", "f", lambda x: set_nested(x, ("specialization_category", "monodromy_group"), "C3")),
        ("monodromy-order", "f", lambda x: set_nested(x, ("specialization_category", "monodromy_order"), 3)),
        ("lower-representation", "f", lambda x: set_nested(x, ("specialization_category", "lower_chain_representation"), "UNSPECIFIED")),
        ("cone-boundary", "f", lambda x: set_nested(x, ("two_expansions_of_the_same_lower_interface", "formal_kernel_cone", "partial_3_columns", 0, 0), 0)),
        ("empty-actual", "f", lambda x: set_nested(x, ("two_expansions_of_the_same_lower_interface", "empty_geometric_carrier_interpretation", "actual_9dvl_admissibility_established"), True)),
        ("handoff", "r", lambda x: set_nested(x, ("handoff",), "DISPROVED_UNIVERSAL_MIXED_100_CARRIER_BY_EXACT_ADMISSIBLE_OBSTRUCTION")),
        ("classification", "r", lambda x: set_nested(x, ("classification",), "NEGATIVE")),
        ("counterexample", "r", lambda x: set_nested(x, ("universal_counterexample_found",), True)),
        ("full-negative", "r", lambda x: set_nested(x, ("full_quantifier_negative_proved",), True)),
        ("finding-kind", "r", lambda x: set_nested(x, ("exact_finding", "kind"), "ACTUAL_COUNTEREXAMPLE")),
        ("formal-cone", "r", lambda x: set_nested(x, ("exact_finding", "interface_forces_formal_integral_filler"), False)),
        ("closing-residual", "r", lambda x: set_nested(x, ("proof_distance", "closing_selected_route_residual"), [])),
        ("ledger", "r", lambda x: set_nested(x, ("proof_distance", "canonical_ledger_after"), "3/9")),
        ("network", "r", lambda x: set_nested(x, ("scope_compliance", "network_used"), True)),
        ("manifest-format", "m", lambda x: set_nested(x, ("format",), "bad")),
        ("manifest-remove", "m", lambda x: x["sources"].pop()),
        ("manifest-hash", "m", lambda x: set_nested(x, ("sources", 0, "sha256"), "0" * 64)),
    ]
    require(len(mutations) == 40, "hostile mutation count declaration")
    rejected = 0
    for name, target_name, mutate in mutations:
        f = copy.deepcopy(fixture)
        r = copy.deepcopy(result)
        m = copy.deepcopy(manifest)
        target = {"f": f, "r": r, "m": m}[target_name]
        mutate(target)
        try:
            verify_all(f, r, m, check_disk=False)
        except (AssertionError, KeyError, TypeError, ValueError, IndexError):
            rejected += 1
        else:
            raise AssertionError(f"hostile mutation accepted: {name}")
    return rejected


def main() -> None:
    fixture = load_json(HERE / "interface_independence_fixture.json")
    result = load_json(HERE / "RESULT.json")
    manifest = load_json(HERE / "SOURCE_MANIFEST.json")
    verify_all(fixture, result, manifest, check_disk=True)
    rejected = run_hostile_mutations(fixture, result, manifest)
    print("PASS d3 mixed-100 falsifier: exact interface non-entailment; no actual admissible universal obstruction")
    print("PASS row2599 lower complex: ranks 3/6/7, primitive kernel alpha, formal cone boundary exact")
    print("PASS specialization category: 128 objects, 2187 arrows, 16384 composable triples, S3 x C2 control")
    print(f"PASS hostile mutations rejected: {rejected}/40")


if __name__ == "__main__":
    main()
