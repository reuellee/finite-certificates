#!/usr/bin/env python3
"""Deterministic frozen-head closing referee for singular-df gate 1."""

from __future__ import annotations

from collections import Counter
from copy import deepcopy
import hashlib
import json
import os
from pathlib import Path
import subprocess


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
CYCLE_ID = "2026-09-01-d9-row2599-factor19069-singular-df-multihomogeneous-gate1"
CYCLE = ROOT / "ops" / "research-team" / "cycles" / CYCLE_ID
CANDIDATE = "be63abbb49b23134df615eefd646fe6f1c2863e7"
CANDIDATE_TREE = "bd9e78d8f640a2bf8c2d69afb70f3e571878b963"
EVIDENCE = "47f8b5ff93332cf49afd231747512d04c9ee172a"
EVIDENCE_TREE = "6ebf243d211e7ce6f1383318f015209891b2d213"
PREDECESSOR = "ops/team/d9-factor19069-critical-equidim-constructor/CRITICAL_EQUIDIM_FRONTIER.json"
FRONTIER = "ops/team/d9-factor19069-singular-df-multihomogeneous-constructor/SINGULAR_DF_MULTIHOMOGENEOUS_FRONTIER.json"
CONSTRUCTOR_RESULT = "ops/team/d9-factor19069-singular-df-multihomogeneous-constructor/RESULT.json"
FALSIFIER_RESULT = "ops/team/d9-factor19069-singular-df-multihomogeneous-falsifier/RESULT.json"
CERTIFICATE_RESULT = "ops/team/d9-factor19069-singular-df-multihomogeneous-certificate/RESULT.json"
RESULT = HERE / "RESULT.json"
HOSTILE = HERE / "HOSTILE_TESTS.json"
PORTABILITY_EDITED_CODE_PATHS = frozenset(
    {
        "ops/team/d9-factor19069-singular-df-multihomogeneous-constructor/build_singular_df_multihomogeneous_frontier.py",
        "ops/team/d9-factor19069-singular-df-multihomogeneous-constructor/verify_singular_df_multihomogeneous_frontier.py",
        "ops/team/d9-factor19069-singular-df-multihomogeneous-falsifier/verify_singular_df_multihomogeneous_falsifier.py",
        "ops/team/d9-factor19069-singular-df-multihomogeneous-certificate/verify_singular_df_certificate.py",
    }
)
VARIABLES = tuple("abcdefghi")
BLOCKS = ((0, 1, 2), (3, 4, 5), (6, 7, 8))
EXPECTED_DERIVATIVE_COUNTS = [54, 44, 54, 50, 50, 50, 36, 61, 36]
SUCCESSOR = "D9_ROW2599_FACTOR19069_EXPLICIT_TRIHOMOGENIZED_JACOBIAN_CHART_DECOMPOSITION_GATE1"


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
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("ascii")


def semantic(value: dict) -> str:
    item = deepcopy(value)
    item.pop("semantic_sha256", None)
    return digest(canonical(item))


def frozen_bytes(path: str) -> bytes:
    return git("show", f"{CANDIDATE}:{path}", binary=True)


def frozen_json(path: str):
    return json.loads(frozen_bytes(path))


def derivative(records: list[dict], coordinate: int) -> list[dict]:
    output = []
    for record in records:
        exponents = list(record["exponents"])
        power = exponents[coordinate]
        if power:
            exponents[coordinate] -= 1
            output.append({"exponents": exponents, "coefficient": record["coefficient"] * power})
    return output


def validate_result(value: dict) -> None:
    require(value["format"] == "d9-factor19069-singular-df-multihomogeneous-referee-result-v1", "format")
    require(value["reviewed_revision"] == CANDIDATE, "candidate revision")
    require(value["reviewed_tree"] == CANDIDATE_TREE, "candidate tree")
    require(value["closing_evidence_revision"] == EVIDENCE, "closing evidence revision")
    require(value["closing_evidence_tree"] == EVIDENCE_TREE, "closing evidence tree")
    require(value["verdict"] == "ACCEPT_FAIL_CLOSED_NULL", "verdict")
    require(value["accepted_classification"] == "EXACT_SOURCE_STRUCTURE_FALSIFICATION_FAIL_CLOSED_NULL", "classification")
    require(value["accepted_endpoint"].endswith("COMPONENT_OR_PARENT_SATURATION_BRANCH"), "endpoint")
    require(value["first_unresolved_branch_id"] == "MH-B00-AFFINE-SOURCE-STRUCTURE-CONTRACT", "branch id")
    require(value["first_unresolved_branch_semantic_sha256"] == "73be706424b840acac8130f703649621a3092844bfefd3d25aa765e44f49712d", "branch hash")
    require(len(value["gates"]) == 13 and all(value["gates"].values()), "gates")
    source = value["exact_source"]
    require(source["factor_terms"] == 108 and source["total_degree_support"] == [4, 5, 6], "source census")
    require(source["block_degree_support"] == [[1, 2], [1, 2], [0, 1, 2]], "block support")
    require(source["variable_degree_maxima"] == [2, 1, 2, 2, 2, 2, 1, 2, 1], "variable maxima")
    require(source["affine_block_multihomogeneous"] is False, "affine homogeneity")
    require(source["affine_multiaffine"] is False, "affine multiaffinity")
    require(source["jacobian_generator_count"] == 10 and source["derivative_term_counts"] == EXPECTED_DERIVATIVE_COUNTS, "Jacobian generators")
    tri = value["trihomogenization"]
    require(tri["ring"] == "Q[a,b,c,u,d,e,f,v,g,h,i,w]" and tri["variables"] == 12, "trihomogenization ring")
    require(tri["homogenizers"] == ["u", "v", "w"] and tri["block_degree"] == [2, 2, 2] and tri["term_count"] == 108, "trihomogenization census")
    require(tri["dehomogenization_exact"] is True, "dehomogenization")
    require(tri["used_as_decomposition_or_saturation_certificate"] is False, "trihomogenization scope")
    decomp = value["decomposition_and_saturation"]
    require(decomp["characteristic_zero_decomposition_started"] is False, "decomposition started")
    require(decomp["resolved_component_count"] == 0 and decomp["pending_component_count"].startswith("UNKNOWN_"), "component census")
    require(decomp["component_invariants"] == "UNRESOLVED", "component invariants")
    require(decomp["parent_factors_retained"] == 70 and decomp["componentwise_parent_factor_tests_completed"] == 0, "saturation")
    require(decomp["strict_real_residence"] == "UNRESOLVED", "strict real residence")
    require(decomp["connected_row2599_parent_tag"] == "UNRESOLVED", "connected parent tag")
    require(decomp["singular_or_boundary_strata_discarded"] == 0, "strata")
    strata = value["preserved_strata"]
    require(strata == {"proper_nonexcluded_boundary_candidates": 10, "ambient_support_strata": 3375, "fixed_skeleton_edges": 40, "fixed_skeleton_parent_tag_checks": 2800, "predecessor_null_frontier_preserved_exactly": True}, "preserved strata")
    require(value["endpoint_accounting"] == {"positive": False, "negative": False, "null": True, "timeout": False}, "endpoint accounting")
    require(value["closing_hostile_mutations"] == {"rejected": 24, "total": 24}, "hostile count")
    require(value["clean_replay"] == {"no_local": True, "no_hardlinks": True, "worktree_clean": True, "same_file_id": False}, "clean replay")
    require(value["ledger_delta"] == "none" and value["theorem_ledger"] == "2/9", "ledger")
    require(value["diagonal_nine"] == "OPEN", "diagonal nine")
    require(len(value["nonconsequences"]) == 8 and "NO_THEOREM_LEDGER_PROMOTION" in value["nonconsequences"], "nonconsequences")
    require(value["closing_strategy_verdict"] == "PIVOT", "strategy")
    require(value["retired_route"] == "AFFINE_MULTIHOMOGENEOUS_OR_MULTIAFFINE_DECOMPOSITION_AS_STATED", "retired route")
    require(value["precise_successor"] == SUCCESSOR and value["sole_successor_count"] == 1, "successor")
    require(value["github_write"] is False, "GitHub mode")


def hostile_tests(stored: dict) -> list[str]:
    mutations = [
        ("candidate_revision_drift", lambda x: x.__setitem__("reviewed_revision", "0" * 40)),
        ("candidate_tree_drift", lambda x: x.__setitem__("reviewed_tree", "0" * 40)),
        ("closing_evidence_revision_drift", lambda x: x.__setitem__("closing_evidence_revision", "0" * 40)),
        ("classification_invention", lambda x: x.__setitem__("accepted_classification", "COMPLETE")),
        ("endpoint_substitution", lambda x: x.__setitem__("accepted_endpoint", "POSITIVE")),
        ("branch_hash_drift", lambda x: x.__setitem__("first_unresolved_branch_semantic_sha256", "0" * 64)),
        ("affine_homogeneity_overclaim", lambda x: x["exact_source"].__setitem__("affine_block_multihomogeneous", True)),
        ("affine_multiaffinity_overclaim", lambda x: x["exact_source"].__setitem__("affine_multiaffine", True)),
        ("trihomogenization_scope_overclaim", lambda x: x["trihomogenization"].__setitem__("used_as_decomposition_or_saturation_certificate", True)),
        ("dehomogenization_loss", lambda x: x["trihomogenization"].__setitem__("dehomogenization_exact", False)),
        ("decomposition_started_overclaim", lambda x: x["decomposition_and_saturation"].__setitem__("characteristic_zero_decomposition_started", True)),
        ("component_count_invention", lambda x: x["decomposition_and_saturation"].__setitem__("resolved_component_count", 1)),
        ("component_invariant_invention", lambda x: x["decomposition_and_saturation"].__setitem__("component_invariants", "COMPLETE")),
        ("saturation_overclaim", lambda x: x["decomposition_and_saturation"].__setitem__("componentwise_parent_factor_tests_completed", 70)),
        ("parent_factor_loss", lambda x: x["decomposition_and_saturation"].__setitem__("parent_factors_retained", 69)),
        ("strict_real_residence_overclaim", lambda x: x["decomposition_and_saturation"].__setitem__("strict_real_residence", "PROVED")),
        ("connected_parent_tag_overclaim", lambda x: x["decomposition_and_saturation"].__setitem__("connected_row2599_parent_tag", "ATTACHED")),
        ("boundary_stratum_loss", lambda x: x["decomposition_and_saturation"].__setitem__("singular_or_boundary_strata_discarded", 1)),
        ("positive_endpoint_overclaim", lambda x: x["endpoint_accounting"].__setitem__("positive", True)),
        ("negative_endpoint_overclaim", lambda x: x["endpoint_accounting"].__setitem__("negative", True)),
        ("timeout_endpoint_overclaim", lambda x: x["endpoint_accounting"].__setitem__("timeout", True)),
        ("ledger_promotion", lambda x: x.__setitem__("theorem_ledger", "3/9")),
        ("diagonal_nine_overclaim", lambda x: x.__setitem__("diagonal_nine", "PROVED")),
        ("successor_ambiguity", lambda x: x.__setitem__("sole_successor_count", 2)),
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
    require(subprocess.run(["git", "merge-base", "--is-ancestor", CANDIDATE, EVIDENCE], cwd=ROOT).returncode == 0, "candidate ancestry")
    evidence_delta = git("diff", "--name-only", CANDIDATE, EVIDENCE).splitlines()
    require(evidence_delta == [f"ops/research-team/cycles/{CYCLE_ID}/CANDIDATE_MANIFEST.json", f"ops/research-team/cycles/{CYCLE_ID}/CLEAN_REPLAY.json"], "closing evidence delta")

    manifest = json.loads(git("show", f"{EVIDENCE}:ops/research-team/cycles/{CYCLE_ID}/CANDIDATE_MANIFEST.json"))
    require(manifest["candidate_revision"] == CANDIDATE and manifest["candidate_tree"] == CANDIDATE_TREE, "manifest candidate")
    require(manifest["accepted_classification"] == "EXACT_SOURCE_STRUCTURE_FALSIFICATION_FAIL_CLOSED_NULL", "manifest classification")
    require(manifest["resolved_component_count"] == 0 and manifest["componentwise_parent_factor_tests_completed"] == 0, "manifest zero claims")
    require(manifest["strict_real_residence"] == "UNRESOLVED" and manifest["connected_parent_component_tag"] == "UNRESOLVED", "manifest nonclaims")
    require(manifest["ledger_delta"] == "none" and manifest["theorem_ledger"] == "2/9", "manifest ledger")
    require(manifest["precise_successor"] == SUCCESSOR, "manifest successor")
    require(PORTABILITY_EDITED_CODE_PATHS <= set(manifest["pins"]), "portability code pin census")
    for path, expected in manifest["pins"].items():
        blob = frozen_bytes(path)
        require(digest(blob) == expected, f"candidate pin {path}")
        if path not in PORTABILITY_EDITED_CODE_PATHS:
            require((ROOT / path).read_bytes() == blob, f"post-candidate drift {path}")

    opening = frozen_json(f"ops/research-team/cycles/{CYCLE_ID}/OPENING_AUDIT.json")
    require(opening["selected_count"] == 1 and opening["opening_ledger"] == "2/9", "opening target")
    require(opening["target"]["parent_sign_factors"] == 70 and opening["target"]["ambient_parameter_dimension"] == 9, "opening scope")
    graph = frozen_json(f"ops/research-team/cycles/{CYCLE_ID}/OBLIGATION_GRAPH.json")
    require(graph["promotion_gate"] == "INDEPENDENTLY_REPLAYED_UNIVERSAL_DIAGONAL_CERTIFICATE_ONLY", "promotion gate")
    require(len(graph["nodes"]) == 10 and len(graph["edges"]) == 9, "obligation graph")

    predecessor = frozen_json(PREDECESSOR)
    factor = predecessor["factor_circuit"]["wall_polynomial"]["sparse_polynomial"]
    require(len(factor) == 108 and digest(canonical(factor)) == "b997e1dcc7216f595610633de99dd3459658cef28676fa748d79c2ba4ac0f3dc", "factor reconstruction")
    require(sorted({sum(r["exponents"]) for r in factor}) == [4, 5, 6], "total degree support")
    supports = [sorted({sum(r["exponents"][i] for i in block) for r in factor}) for block in BLOCKS]
    require(supports == [[1, 2], [1, 2], [0, 1, 2]], "block supports")
    maxima = [max(r["exponents"][i] for r in factor) for i in range(9)]
    require(maxima == [2, 1, 2, 2, 2, 2, 1, 2, 1], "affine multiaffinity rejection")
    derivatives = [derivative(factor, i) for i in range(9)]
    require([len(value) for value in derivatives] == EXPECTED_DERIVATIVE_COUNTS, "derivative reconstruction")

    frontier = frozen_json(FRONTIER)
    require(frontier["semantic_sha256"] == semantic(frontier), "frontier semantic seal")
    structure = frontier["exact_affine_source_structure"]
    require(structure["block_degree_sets"] == supports and structure["affine_block_homogeneous_of_degree_2_2_2"] is False and structure["affine_multiaffine"] is False, "source verdict")
    tri = structure["canonical_trihomogenization"]
    expected_tri = [{"coefficient": r["coefficient"], "exponents_a_b_c_d_e_f_g_h_i": r["exponents"], "homogenizer_exponents_u_v_w": [2 - sum(r["exponents"][i] for i in block) for block in BLOCKS]} for r in factor]
    require(tri["ring"] == "Q[a,b,c,u,d,e,f,v,g,h,i,w]" and tri["terms"] == expected_tri, "exact trihomogenization")
    require(tri["dehomogenization_identity"].endswith("=f_19069") and tri["not_used_as_a_decomposition_certificate"] is True, "trihomogenization scope")
    ideal = frontier["original_singular_jacobian_ideal"]
    require(ideal["generator_count"] == 10 and ideal["inverse_variables"] == 0, "Jacobian scope")
    require([g["sparse_polynomial"] for g in ideal["generators"][1:]] == derivatives, "Jacobian exactness")
    branch = frontier["decomposition_frontier"]["branches"][0]
    require(branch["characteristic_zero_decomposition_started"] is False and branch["component_count"] is None, "decomposition stop")
    require(branch["componentwise_parent_factor_tests_completed"] == 0 and branch["strict_real_residence_status"] == "PENDING" and branch["connected_row2599_parent_tag_status"] == "PENDING", "downstream nonclaims")
    incidence = frontier["parent_factor_incidence_frontier"]
    parents = predecessor["factor_circuit"]["parent_factor_nodes"]
    require(len(incidence["records"]) == len(parents) == 70 and incidence["completed_component_factor_pairs"] == 0, "parent census")
    require([r["sparse_polynomial"] for r in incidence["records"]] == [p["sparse_polynomial"] for p in parents], "parent preservation")
    require(frontier["preserved_null_frontier"] == predecessor["verified_null_frontier"], "null preservation")
    require(frontier["preserved_boundary_frontier"] == predecessor["true_boundary_frontier"], "boundary preservation")
    require(frontier["preserved_fixed_skeleton_accounting"] == predecessor["fixed_skeleton_accounting"], "skeleton preservation")
    require(frontier["endpoint_accounting"] == {"negative": "NOT_REACHED_NO_EXACT_POSITIVE_DIMENSIONAL_REAL_STRICT_COMPONENT", "null": "REACHED_EXACT_SOURCE_STRUCTURE_MISMATCH_HASH_PINNED", "positive": "NOT_REACHED_NO_STRICT_SINGULAR_EMPTINESS_PROOF", "timeout": "NOT_REACHED"}, "frontier endpoints")

    constructor = frozen_json(CONSTRUCTOR_RESULT)
    falsifier = frozen_json(FALSIFIER_RESULT)
    certificate = frozen_json(CERTIFICATE_RESULT)
    require(constructor["resolved_component_count"] == 0 and constructor["componentwise_parent_factor_tests_completed"] == 0, "constructor scope")
    require(falsifier["endpoint_accounting"] == {"positive": False, "negative": False, "null": True, "timeout": False, "first_unresolved_branch": "AFFINE_BLOCK_STRUCTURE_PRECONDITION"}, "falsifier endpoints")
    require(falsifier["hostile_mutations_rejected"] == 59 and falsifier["ledger_promotion_recommended"] is False, "falsifier hostile ledger")
    require(certificate["hostile_tests"]["rejected"] == 35 and certificate["certificate_gates"]["strict_parent_emptiness_certified"] is False, "certificate scope")
    require(certificate["ledger_after"] == "2/9" and certificate["ledger_change_recommended"] is False, "certificate ledger")

    clean = json.loads(git("show", f"{EVIDENCE}:ops/research-team/cycles/{CYCLE_ID}/CLEAN_REPLAY.json"))
    require(clean["candidate_revision"] == CANDIDATE and clean["candidate_tree"] == CANDIDATE_TREE, "clean candidate")
    require("--no-hardlinks --no-local" in clean["clone_mode"], "clean clone mode")
    require(clean["results"]["worktree_clean"] is True and clean["results"]["source_and_replay_same_file_id"] is False, "clean recorded result")
    replay_path_checked = optional_replay_path_recheck(clean)

    stored = json.loads(RESULT.read_text(encoding="utf-8"))
    validate_result(stored)
    rejected = hostile_tests(stored)
    hostile = json.loads(HOSTILE.read_text(encoding="utf-8"))
    require(hostile["tests"] == rejected and hostile["rejected"] == hostile["total"] == 24, "hostile artifact")
    print("PASS frozen candidate, exact source/trihomogenization, preserved fail-closed frontier")
    print(f"PASS frozen clean-replay evidence, external_replay_path_rechecked={str(replay_path_checked).lower()}, 24 hostile mutations, ledger 2/9 delta none")
    print(f"PASS sole successor={SUCCESSOR}")


if __name__ == "__main__":
    main()
