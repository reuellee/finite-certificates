#!/usr/bin/env python3
"""Deterministic frozen-head referee for the explicit Jacobian-chart gate."""

from __future__ import annotations

from copy import deepcopy
import hashlib
import json
import os
from pathlib import Path
import subprocess


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
CYCLE_ID = "2026-09-01-d9-row2599-factor19069-explicit-trihom-jacobian-chart-gate1"
CYCLE = ROOT / "ops" / "research-team" / "cycles" / CYCLE_ID
CANDIDATE = "5428e6232a3303d0188b2fee022968ae830d3b03"
CANDIDATE_TREE = "b32c190d662559ef2f2f80538595cf411fc26b54"
EVIDENCE = "0388fb316603bfd85fe7e9c2983a6f38f39643aa"
EVIDENCE_TREE = "f0a1ead500ad108c4e412c433eebbe5906dd998e"
FRONTIER = "ops/team/d9-factor19069-explicit-trihom-jacobian-chart-constructor/PROJECTIVE_CHART_FRONTIER.json"
CONSTRUCTOR_RESULT = "ops/team/d9-factor19069-explicit-trihom-jacobian-chart-constructor/RESULT.json"
FALSIFIER_RESULT = "ops/team/d9-factor19069-explicit-trihom-jacobian-chart-falsifier/RESULT.json"
CERTIFICATE_RESULT = "ops/team/d9-factor19069-explicit-trihom-jacobian-chart-certificate/RESULT.json"
SUCCESSOR = "D9_ROW2599_FACTOR19069_HOMOGENIZER_BOUNDARY_TYPE_STRATIFICATION_GATE1"
FACTORIZATION = "-h*(a*f-c*d)*(a*e*i-a*f*h-b*d*i+b*f*g+c*d*h-c*e*g)"
RESULT = HERE / "RESULT.json"
HOSTILE = HERE / "HOSTILE_TESTS.json"
PORTABILITY_EDITED_CODE_PATHS = frozenset(
    {
        "ops/team/d9-factor19069-explicit-trihom-jacobian-chart-constructor/build_projective_chart_frontier.py",
        "ops/team/d9-factor19069-explicit-trihom-jacobian-chart-constructor/verify_projective_chart_frontier.py",
        "ops/team/d9-factor19069-explicit-trihom-jacobian-chart-falsifier/verify_explicit_trihom_jacobian_chart_falsifier.py",
        "ops/team/d9-factor19069-explicit-trihom-jacobian-chart-certificate/verify_projective_chart_certificate.py",
    }
)


class Reject(AssertionError):
    pass


def require(condition: bool, marker: str) -> None:
    if not condition:
        raise Reject(marker)


def git(*args: str, binary: bool = False):
    value = subprocess.check_output(["git", *args], cwd=ROOT, text=not binary)
    return value if binary else value.strip()


def replay_git(replay: Path, *args: str) -> str:
    resolved = replay.resolve()
    return subprocess.check_output(
        ["git", "-c", f"safe.directory={resolved.as_posix()}", *args],
        cwd=resolved,
        text=True,
    ).strip()


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def canonical(value) -> bytes:
    return json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=True
    ).encode("ascii")


def semantic(value: dict) -> str:
    item = deepcopy(value)
    item.pop("semantic_sha256", None)
    return digest(canonical(item))


def frozen_bytes(path: str) -> bytes:
    return git("show", f"{CANDIDATE}:{path}", binary=True)


def frozen_json(path: str):
    return json.loads(frozen_bytes(path))


def evidence_json(path: str):
    return json.loads(git("show", f"{EVIDENCE}:{path}", binary=True))


def monomial(names: list[str], **powers: int) -> tuple[int, ...]:
    return tuple(powers.get(name, 0) for name in names)


def multiply(left: dict, right: dict) -> dict:
    output: dict[tuple[int, ...], int] = {}
    for a, ca in left.items():
        for b, cb in right.items():
            exponent = tuple(x + y for x, y in zip(a, b))
            output[exponent] = output.get(exponent, 0) + ca * cb
    return {exponent: coefficient for exponent, coefficient in output.items() if coefficient}


def validate_result(value: dict) -> None:
    require(
        value["format"]
        == "d9-factor19069-explicit-trihom-jacobian-chart-referee-result-v1",
        "format",
    )
    require(value["reviewed_revision"] == CANDIDATE, "candidate revision")
    require(value["reviewed_tree"] == CANDIDATE_TREE, "candidate tree")
    require(value["closing_evidence_revision"] == EVIDENCE, "evidence revision")
    require(value["closing_evidence_tree"] == EVIDENCE_TREE, "evidence tree")
    require(value["verdict"] == "ACCEPT_FAIL_CLOSED_TIMEOUT_FRONTIER", "verdict")
    require(
        value["accepted_classification"]
        == "EXACT_64_CHART_RECONSTRUCTION_BOUNDED_CHARACTERISTIC_ZERO_TIMEOUT_FAIL_CLOSED",
        "classification",
    )
    require(
        value["accepted_endpoint"]
        == "HASH_PIN_ALL_COMPLETED_CHART_BRANCHES_AND_FIRST_PENDING_BRANCH",
        "endpoint",
    )
    require(value["first_pending_branch_id"] == "DEC-JCH-00-a-d-g", "branch id")
    require(
        value["first_pending_branch_semantic_sha256"]
        == "abfc0e6ecf60da4924c0991e8f78ea6df06a3270353eeedba411096ee3727725",
        "branch hash",
    )
    require(len(value["gates"]) == 15 and all(value["gates"].values()), "gates")
    require(
        value["exact_chart_frontier"]
        == {
            "trihomogeneous_source_terms": 108,
            "trihomogeneous_multidegree": [2, 2, 2],
            "dehomogenization_exact": True,
            "standard_chart_count": 64,
            "free_coordinates_per_chart": 9,
            "chart_jacobian_generators_each": 10,
            "directed_overlap_records": 4032,
            "Euler_zero_residuals": 192,
            "boundary_capable_charts": 63,
            "boundary_stratum_chart_incidences": 279,
            "global_nonempty_homogenizer_boundary_types": 7,
            "affine_chart_id": "JCH-63-u-v-w",
            "affine_original_ideal_equality": True,
            "parent_factor_records_retained": 70,
        },
        "chart frontier",
    )
    require(
        value["decomposition_frontier"]
        == {
            "coefficient_field": "QQ",
            "monomial_order": "grevlex",
            "attempted_chart": "JCH-00-a-d-g",
            "wall_seconds": 20,
            "status": "TIMEOUT_FIRST_CHART_GROEBNER_PREREQUISITE_PENDING",
            "complete_projective_decomposition": False,
            "accepted_projective_components": 0,
            "accepted_affine_component_contractions": 0,
            "componentwise_parent_factor_tests_completed": 0,
            "embedded_or_boundary_strata_discarded": 0,
        },
        "decomposition frontier",
    )
    require(
        value["endpoint_accounting"]
        == {"positive": False, "negative": False, "null": False, "timeout": True},
        "endpoint accounting",
    )
    require(value["closing_hostile_mutations"] == {"rejected": 33, "total": 33}, "hostile count")
    require(
        value["clean_replay"]
        == {
            "no_local": True,
            "no_hardlinks": True,
            "worktree_clean": True,
            "same_file_id": False,
        },
        "clean replay",
    )
    require(value["ledger_delta"] == "none" and value["theorem_ledger"] == "2/9", "ledger")
    require(value["diagonal_nine"] == "OPEN", "diagonal nine")
    require(
        len(value["nonconsequences"]) == 11
        and "NO_9DVL_SCORE_CHANGE" in value["nonconsequences"],
        "nonconsequences",
    )
    require(value["closing_strategy_verdict"] == "PIVOT", "strategy")
    require(
        value["retired_route"] == "BLIND_UNDIFFERENTIATED_GROEBNER_BUDGET_ESCALATION",
        "retired route",
    )
    require(value["precise_successor"] == SUCCESSOR, "successor")
    require(value["sole_successor_count"] == 1, "successor count")
    design = value["successor_design"]
    require(
        design["structural_change"]
        == "STRATIFY_THE_SEVEN_NONEMPTY_HOMOGENIZER_BOUNDARY_TYPES_BEFORE_CHARTWISE_DECOMPOSITION",
        "successor structural change",
    )
    require(design["deepest_restriction_term_count"] == 11, "deepest term count")
    require(design["deepest_restriction_exact_factorization"] == FACTORIZATION, "deepest factorization")
    require(value["discovery_repair_used"] is False, "discovery repair")
    require(value["drive_connector_used"] is False, "Drive connector")
    require(value["github_write"] is False, "GitHub mode")


def hostile_tests(stored: dict) -> list[str]:
    mutations = [
        ("candidate_revision_drift", lambda x: x.__setitem__("reviewed_revision", "0" * 40)),
        ("candidate_tree_drift", lambda x: x.__setitem__("reviewed_tree", "0" * 40)),
        ("closing_evidence_revision_drift", lambda x: x.__setitem__("closing_evidence_revision", "0" * 40)),
        ("verdict_overclaim", lambda x: x.__setitem__("verdict", "PROVE_DIAGONAL_NINE")),
        ("classification_overclaim", lambda x: x.__setitem__("accepted_classification", "COMPLETE_DECOMPOSITION")),
        ("endpoint_substitution", lambda x: x.__setitem__("accepted_endpoint", "POSITIVE")),
        ("pending_branch_drift", lambda x: x.__setitem__("first_pending_branch_id", "DEC-JCH-01-a-d-h")),
        ("pending_hash_drift", lambda x: x.__setitem__("first_pending_branch_semantic_sha256", "0" * 64)),
        ("source_term_drift", lambda x: x["exact_chart_frontier"].__setitem__("trihomogeneous_source_terms", 107)),
        ("chart_count_drift", lambda x: x["exact_chart_frontier"].__setitem__("standard_chart_count", 63)),
        ("overlap_loss", lambda x: x["exact_chart_frontier"].__setitem__("directed_overlap_records", 4031)),
        ("Euler_loss", lambda x: x["exact_chart_frontier"].__setitem__("Euler_zero_residuals", 191)),
        ("boundary_incidence_loss", lambda x: x["exact_chart_frontier"].__setitem__("boundary_stratum_chart_incidences", 278)),
        ("boundary_type_loss", lambda x: x["exact_chart_frontier"].__setitem__("global_nonempty_homogenizer_boundary_types", 6)),
        ("affine_ideal_loss", lambda x: x["exact_chart_frontier"].__setitem__("affine_original_ideal_equality", False)),
        ("parent_record_loss", lambda x: x["exact_chart_frontier"].__setitem__("parent_factor_records_retained", 69)),
        ("decomposition_complete_overclaim", lambda x: x["decomposition_frontier"].__setitem__("complete_projective_decomposition", True)),
        ("component_invention", lambda x: x["decomposition_frontier"].__setitem__("accepted_projective_components", 1)),
        ("affine_contraction_invention", lambda x: x["decomposition_frontier"].__setitem__("accepted_affine_component_contractions", 1)),
        ("parent_test_invention", lambda x: x["decomposition_frontier"].__setitem__("componentwise_parent_factor_tests_completed", 70)),
        ("embedded_loss", lambda x: x["decomposition_frontier"].__setitem__("embedded_or_boundary_strata_discarded", 1)),
        ("positive_endpoint_overclaim", lambda x: x["endpoint_accounting"].__setitem__("positive", True)),
        ("negative_endpoint_overclaim", lambda x: x["endpoint_accounting"].__setitem__("negative", True)),
        ("null_endpoint_overclaim", lambda x: x["endpoint_accounting"].__setitem__("null", True)),
        ("timeout_endpoint_loss", lambda x: x["endpoint_accounting"].__setitem__("timeout", False)),
        ("ledger_promotion", lambda x: x.__setitem__("theorem_ledger", "3/9")),
        ("diagonal_nine_overclaim", lambda x: x.__setitem__("diagonal_nine", "PROVED")),
        ("replay_hardlink_alias", lambda x: x["clean_replay"].__setitem__("same_file_id", True)),
        ("successor_ambiguity", lambda x: x.__setitem__("sole_successor_count", 2)),
        ("successor_route_repetition", lambda x: x["successor_design"].__setitem__("structural_change", "INCREASE_GROEBNER_TIMEOUT")),
        ("deepest_term_drift", lambda x: x["successor_design"].__setitem__("deepest_restriction_term_count", 12)),
        ("deepest_factorization_drift", lambda x: x["successor_design"].__setitem__("deepest_restriction_exact_factorization", "0")),
        ("github_write", lambda x: x.__setitem__("github_write", True)),
    ]
    rejected = []
    for name, change in mutations:
        value = deepcopy(stored)
        change(value)
        try:
            validate_result(value)
        except Reject:
            rejected.append(name)
        else:
            raise Reject(f"hostile accepted {name}")
    return rejected


def optional_replay_path_recheck(clean: dict) -> bool:
    replay = Path(clean["replay_path"]).resolve()
    source_result = ROOT / CERTIFICATE_RESULT
    replay_result = replay / CERTIFICATE_RESULT
    if not replay.is_dir() or not replay_result.is_file():
        return False
    require(replay_git(replay, "rev-parse", "HEAD") == CANDIDATE, "external replay head")
    require(replay_git(replay, "rev-parse", "HEAD^{tree}") == CANDIDATE_TREE, "external replay tree")
    require(replay_git(replay, "status", "--porcelain=v1") == "", "external replay status")
    require(source_result.stat().st_nlink == replay_result.stat().st_nlink == 1, "external replay hardlinks")
    require(not os.path.samefile(source_result, replay_result), "external replay file identity")
    require(
        source_result.read_bytes()
        == replay_result.read_bytes()
        == frozen_bytes(CERTIFICATE_RESULT),
        "external replay bytes",
    )
    return True


def main() -> None:
    require(git("rev-parse", f"{CANDIDATE}^{{tree}}") == CANDIDATE_TREE, "candidate tree object")
    require(git("rev-parse", f"{EVIDENCE}^{{tree}}") == EVIDENCE_TREE, "evidence tree object")
    require(
        subprocess.run(
            ["git", "merge-base", "--is-ancestor", CANDIDATE, EVIDENCE], cwd=ROOT
        ).returncode
        == 0,
        "candidate ancestry",
    )
    evidence_delta = git("diff", "--name-only", CANDIDATE, EVIDENCE).splitlines()
    require(
        evidence_delta
        == [
            f"ops/research-team/cycles/{CYCLE_ID}/CANDIDATE_MANIFEST.json",
            f"ops/research-team/cycles/{CYCLE_ID}/CLEAN_REPLAY.json",
        ],
        "closing evidence delta",
    )

    manifest_path = f"ops/research-team/cycles/{CYCLE_ID}/CANDIDATE_MANIFEST.json"
    clean_path = f"ops/research-team/cycles/{CYCLE_ID}/CLEAN_REPLAY.json"
    manifest = evidence_json(manifest_path)
    require(manifest["candidate_revision"] == CANDIDATE, "manifest candidate")
    require(manifest["candidate_tree"] == CANDIDATE_TREE, "manifest tree")
    require(manifest["accepted_classification"].endswith("TIMEOUT_FAIL_CLOSED"), "manifest classification")
    require(manifest["first_pending_branch_id"] == "DEC-JCH-00-a-d-g", "manifest branch")
    require(manifest["endpoint_accounting"] == {"positive": False, "negative": False, "null": False, "timeout": True}, "manifest endpoints")
    require(manifest["precise_successor"] == SUCCESSOR, "manifest successor")
    require(manifest["successor_design"]["selected_count"] == 1, "manifest successor count")
    require(manifest["successor_design"]["deepest_restriction_term_count"] == 11, "manifest deepest terms")
    require(manifest["successor_design"]["deepest_restriction_exact_factorization"] == FACTORIZATION, "manifest factorization")
    require(PORTABILITY_EDITED_CODE_PATHS <= set(manifest["pins"]), "portability code pin census")
    for path, expected in manifest["pins"].items():
        blob = frozen_bytes(path)
        require(digest(blob) == expected, f"candidate pin {path}")
        if path not in PORTABILITY_EDITED_CODE_PATHS:
            require((ROOT / path).read_bytes() == blob, f"post-candidate drift {path}")

    opening = frozen_json(f"ops/research-team/cycles/{CYCLE_ID}/OPENING_AUDIT.json")
    require(opening["selected_count"] == 1 and opening["opening_ledger"] == "2/9", "opening target")
    require(opening["target"]["standard_chart_count"] == 64, "opening chart scope")
    require(opening["target"]["parent_sign_factors"] == 70, "opening parent scope")
    graph = frozen_json(f"ops/research-team/cycles/{CYCLE_ID}/OBLIGATION_GRAPH.json")
    require(graph["promotion_gate"] == "INDEPENDENTLY_REPLAYED_UNIVERSAL_DIAGONAL_CERTIFICATE_ONLY", "promotion gate")

    frontier = frozen_json(FRONTIER)
    require(frontier["semantic_sha256"] == semantic(frontier), "frontier semantic seal")
    require(frontier["theorem_ledger"] == "2/9" and frontier["ledger_change_recommended"] == "none", "frontier ledger")
    source = frontier["trihomogeneous_source"]
    require(source["term_count"] == 108 and source["multidegree"] == [2, 2, 2], "source census")
    require(source["dehomogenization_exact_sparse_equality"] is True, "dehomogenization")
    require(source["trihomogenization_is_decomposition_certificate"] is False, "source scope")
    polynomial = source["polynomial"]
    names = polynomial["coordinate_order"]
    require(names == ["a", "b", "c", "u", "d", "e", "f", "v", "g", "h", "i", "w"], "coordinate order")
    require(polynomial["term_count"] == len(polynomial["sparse_polynomial"]) == 108, "polynomial terms")
    blocks = ((0, 1, 2, 3), (4, 5, 6, 7), (8, 9, 10, 11))
    for record in polynomial["sparse_polynomial"]:
        require([sum(record["exponents"][i] for i in block) for block in blocks] == [2, 2, 2], "term multidegree")

    atlas = frontier["chart_atlas"]
    charts = atlas["charts"]
    require(atlas["standard_chart_count"] == len(charts) == 64, "chart census")
    require([chart["chart_index"] for chart in charts] == list(range(64)), "chart order")
    require(all(chart["free_coordinate_count"] == len(chart["free_coordinates"]) == 9 for chart in charts), "free coordinates")
    require(all(chart["chart_jacobian_ideal"]["generator_count"] == 10 for chart in charts), "Jacobian generators")
    require(all(chart["euler_recovery_count"] == chart["euler_zero_residual_count"] == 3 for chart in charts), "Euler recovery")
    require(sum(chart["euler_zero_residual_count"] for chart in charts) == 192, "Euler census")
    require(all(chart["full_projective_jacobian_transfer_proved"] is True for chart in charts), "projective transfer")
    require(sum(chart["overlap_record_count"] for chart in charts) == 4032, "overlap census")
    require(all(chart["overlap_record_count"] == len(chart["overlap_records"]) == 63 for chart in charts), "overlap records")
    require(sum(len(chart["boundary_strata"]) for chart in charts) == 279, "boundary incidence census")
    require(sum(bool(chart["boundary_strata"]) for chart in charts) == 63, "boundary-capable charts")
    require(all(chart["boundary_strata_discarded"] == 0 for chart in charts), "boundary retention")
    require(atlas["directed_overlap_record_count"] == 4032, "atlas overlaps")
    require(atlas["local_nonempty_boundary_intersection_record_count"] == 279, "atlas boundary records")
    require(atlas["global_nonempty_boundary_type_count"] == 7, "boundary types")
    require(
        atlas["global_boundary_types"]
        == [["u"], ["v"], ["w"], ["u", "v"], ["u", "w"], ["v", "w"], ["u", "v", "w"]],
        "boundary type list",
    )

    transfer = frontier["affine_transfer"]
    require(transfer["chart_id"] == "JCH-63-u-v-w", "affine chart")
    require(transfer["F_chart_equals_original_f_19069"] is True, "affine F transfer")
    require(transfer["nine_chart_derivatives_equal_original_affine_derivatives"] is True, "affine derivative transfer")
    require(transfer["chart_ideal_equals_original_affine_singular_ideal"] is True, "affine ideal equality")

    decomposition = frontier["decomposition_frontier"]
    attempt = decomposition["attempt"]
    require(decomposition["required_characteristic"] == 0 and decomposition["coefficient_field"] == "Q", "characteristic zero")
    require(decomposition["complete_projective_decomposition"] is False, "decomposition incomplete")
    require(decomposition["resolved_chart_count"] == 0 and decomposition["pending_chart_count"] == 64, "decomposition census")
    require(decomposition["accepted_component_count"] == 0, "accepted components")
    require(decomposition["embedded_components_discarded"] == decomposition["boundary_strata_discarded"] == 0, "decomposition strata")
    require(attempt["attempted_chart_id"] == "JCH-00-a-d-g", "attempted chart")
    require(attempt["monomial_order"] == "grevlex" and attempt["wall_seconds_ceiling"] == 20, "attempt budget")
    require(attempt["status"] == "TIMEOUT_FIRST_CHART_GROEBNER_PREREQUISITE_PENDING", "attempt status")
    require(attempt["primary_decomposition_completed"] is False and attempt["accepted_as_decomposition_certificate"] is False, "attempt nonclaim")
    branch = decomposition["first_pending_branch"]
    require(branch["branch_id"] == "DEC-JCH-00-a-d-g" and branch["chart_id"] == "JCH-00-a-d-g", "first pending branch")
    require(branch["semantic_sha256"] == "abfc0e6ecf60da4924c0991e8f78ea6df06a3270353eeedba411096ee3727725", "first pending hash")
    require(branch["accepted_components"] == [] and branch["component_count"] is None, "pending branch components")

    contraction = frontier["affine_contraction_frontier"]
    require(contraction["accepted_projective_component_count"] == 0, "projective component count")
    require(contraction["accepted_affine_component_count"] == 0, "affine component count")
    require(contraction["contracted_to_original_affine_singular_ideal_count"] == 0, "contraction count")
    require(contraction["componentwise_parent_tests_started"] == 0, "parent tests started")
    parents = frontier["parent_factor_incidence_frontier"]
    require(parents["ordered_factor_count"] == len(parents["records"]) == 70, "parent records")
    require(parents["completed_component_factor_pairs"] == 0, "parent pairs")
    require(parents["accepted_contracted_component_count"] == 0, "parent component count")
    require(parents["inverse_variable_discovery_used"] is False, "inverse discovery")
    require(
        frontier["endpoint_accounting"]
        == {
            "negative": "NOT_REACHED_NO_EXACT_POSITIVE_DIMENSIONAL_STRICT_REAL_SINGULAR_COMPONENT",
            "null": "NOT_REACHED",
            "positive": "NOT_REACHED_NO_EXACT_STRICT_PARENT_SINGULAR_EMPTINESS",
            "timeout": "REACHED_HASH_PINNED_FIRST_PENDING_CHART",
        },
        "frontier endpoints",
    )

    index = {name: position for position, name in enumerate(names)}
    restriction = {
        tuple(record["exponents"]): record["coefficient"]
        for record in polynomial["sparse_polynomial"]
        if record["exponents"][index["u"]]
        == record["exponents"][index["v"]]
        == record["exponents"][index["w"]]
        == 0
    }
    left = {monomial(names, h=1): -1}
    middle = {monomial(names, a=1, f=1): 1, monomial(names, c=1, d=1): -1}
    right = {
        monomial(names, a=1, e=1, i=1): 1,
        monomial(names, a=1, f=1, h=1): -1,
        monomial(names, b=1, d=1, i=1): -1,
        monomial(names, b=1, f=1, g=1): 1,
        monomial(names, c=1, d=1, h=1): 1,
        monomial(names, c=1, e=1, g=1): -1,
    }
    expected_restriction = multiply(multiply(left, middle), right)
    require(len(restriction) == len(expected_restriction) == 11, "deepest restriction terms")
    require(restriction == expected_restriction, "deepest restriction factorization")

    constructor = frozen_json(CONSTRUCTOR_RESULT)
    falsifier = frozen_json(FALSIFIER_RESULT)
    certificate = frozen_json(CERTIFICATE_RESULT)
    require(constructor["standard_chart_count"] == 64 and constructor["accepted_component_count"] == 0, "constructor scope")
    require(constructor["componentwise_parent_factor_tests_completed"] == 0 and constructor["theorem_ledger"] == "2/9", "constructor ledger")
    require(falsifier["hostile_mutations_rejected"] == 53, "falsifier hostile")
    require(falsifier["endpoint_accounting"] == {"positive": False, "negative": False, "null": False, "timeout": True, "first_unresolved_branch": "DEC-JCH-00-a-d-g:CHARACTERISTIC_ZERO_GROEBNER_PREREQUISITE"}, "falsifier endpoints")
    require(falsifier["theorem_ledger"] == "2/9" and falsifier["ledger_promotion_recommended"] is False, "falsifier ledger")
    require(certificate["hostile_tests"]["rejected"] == certificate["hostile_tests"]["run"] == 46, "certificate hostile")
    require(certificate["timeout_endpoint_reached"] is True and certificate["certificate_gates"]["characteristic_zero_decomposition_certified"] is False, "certificate timeout")
    require(certificate["ledger_after"] == "2/9" and certificate["ledger_change_recommended"] == "none", "certificate ledger")

    clean = evidence_json(clean_path)
    require(clean["candidate_revision"] == CANDIDATE and clean["candidate_tree"] == CANDIDATE_TREE, "clean candidate")
    require("--no-hardlinks --no-local" in clean["clone_mode"], "clean clone mode")
    require(clean["results"]["worktree_clean"] is True, "clean recorded status")
    require(clean["results"]["source_and_replay_same_file_id"] is False, "clean recorded identity")
    replay_path_checked = optional_replay_path_recheck(clean)

    stored = json.loads(RESULT.read_text(encoding="utf-8"))
    validate_result(stored)
    rejected = hostile_tests(stored)
    hostile = json.loads(HOSTILE.read_text(encoding="utf-8"))
    require(hostile["tests"] == rejected, "hostile order")
    require(hostile["rejected"] == hostile["total"] == 33, "hostile artifact")
    print("PASS frozen candidate: 108 terms, 64 charts, 4032 overlaps, 192 Euler residuals")
    print("PASS 279 boundary incidences, exact affine transfer, QQ/grevlex timeout at JCH-00-a-d-g")
    print(f"PASS zero components/tests, 33 hostile mutations, frozen clean-replay evidence, external_replay_path_rechecked={str(replay_path_checked).lower()}, ledger 2/9")
    print(f"PASS sole successor={SUCCESSOR}; deepest boundary restriction=11 terms exact factorization")


if __name__ == "__main__":
    main()
