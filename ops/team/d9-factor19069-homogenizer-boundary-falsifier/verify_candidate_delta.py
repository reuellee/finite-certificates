#!/usr/bin/env python3
"""Independent frozen-candidate attack for the homogenizer-boundary gate.

The candidate frontier and result are read as inert JSON from the frozen git
revision.  No constructor code or acceptance logic is imported.  Exact source
polynomials are rebuilt through the already independent falsifier machinery.
This verifier intentionally has no branch-name requirement, so it replays on
the integration branch and in clean clones containing the frozen revision.
"""

from __future__ import annotations

import argparse
from copy import deepcopy
from hashlib import sha256
import json
from pathlib import Path
import subprocess
import sys
from typing import Any, Callable


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(HERE))
import verify_homogenizer_boundary_falsifier as baseline  # noqa: E402

CANDIDATE_REVISION = "25757510dd88e8b7bbe5668c89f93b2a46b264de"
CANDIDATE_TREE = "47395637cc10c2bd736530719b6e2f3cf57b1629"
CYCLE_ID = "2026-09-01-d9-row2599-factor19069-homogenizer-boundary-type-stratification-gate1"
TRACK_ID = "d9-factor19069-homogenizer-boundary-falsifier"
FRONTIER_PATH = "ops/team/d9-factor19069-homogenizer-boundary-constructor/HOMOGENIZER_BOUNDARY_TYPE_FRONTIER.json"
CONSTRUCTOR_RESULT_PATH = "ops/team/d9-factor19069-homogenizer-boundary-constructor/RESULT.json"
CONSTRUCTOR_MANIFEST_PATH = "ops/team/d9-factor19069-homogenizer-boundary-constructor/SOURCE_MANIFEST.json"
EXPECTED_FRONTIER_SHA256 = "18b0f7bf939646b884f05dc55832b509a54574cf3c2498461839f3c906418a6d"
EXPECTED_RESULT_SHA256 = "d7ad15fd2bc49b25334f836a34de2cc25d75a903902545ac354bded3a919db8b"
EXPECTED_MANIFEST_SHA256 = "0e39b510708b6792c02dfdc537290b10d9897fad7b4a7b5a2f26987ae5ff9083"
EXPECTED_FRONTIER_SEMANTIC = "70d980c28c536dd10a679ac086939fadcf78722dd68839658062948c1e0dd5ec"
EXPECTED_PENDING_SEMANTIC = "2747fcc6923b44996bfe79c0d06d2f88169f9fedea465cdecaa3c104bcf6b8b5"
EXPECTED_KNOWN_UV_SEMANTIC = "f5bc2dcb0047f494f420a8383ce0aedf9d369af5588ed27848577f5c7ad22097"
VERDICT = "ACCEPT_EXACT_BOUNDED_NULL_FRONTIER_WITH_DEEPEST_AND_UV_PARTIAL_CLOSURES_FAIL_CLOSED"

DELTA = HERE / "CANDIDATE_DELTA.json"
DELTA_MANIFEST = HERE / "CANDIDATE_DELTA_MANIFEST.json"
DELTA_HOSTILE = HERE / "CANDIDATE_DELTA_HOSTILE_TESTS.json"
DELTA_RESULT = HERE / "CANDIDATE_DELTA_RESULT.json"

LOCAL_INPUTS = (
    "ops/research-team/PROTOCOL.md",
    f"ops/research-team/cycles/{CYCLE_ID}/CYCLE.md",
    f"ops/research-team/cycles/{CYCLE_ID}/WORK_ORDERS.yaml",
    f"ops/research-team/cycles/{CYCLE_ID}/OPENING_AUDIT.json",
    f"ops/research-team/cycles/{CYCLE_ID}/OBLIGATION_GRAPH.json",
    "ops/team/d9-factor19069-homogenizer-boundary-falsifier/INDEPENDENT_RECONSTRUCTION.json",
    "ops/team/d9-factor19069-homogenizer-boundary-falsifier/SOURCE_MANIFEST.json",
    "ops/team/d9-factor19069-homogenizer-boundary-falsifier/RESULT.json",
    "ops/team/d9-factor19069-homogenizer-boundary-falsifier/verify_homogenizer_boundary_falsifier.py",
)


class Reject(AssertionError):
    pass


def require(condition: bool, marker: str) -> None:
    if not condition:
        raise Reject(marker)


def git_bytes(*arguments: str) -> bytes:
    return subprocess.check_output(
        ["git", "-c", f"safe.directory={ROOT.as_posix()}", *arguments],
        cwd=ROOT,
    )


def git_text(*arguments: str) -> str:
    return git_bytes(*arguments).decode("utf-8").strip()


def frozen_bytes(path: str) -> bytes:
    return git_bytes("show", f"{CANDIDATE_REVISION}:{path}")


def frozen_json(path: str) -> dict[str, Any]:
    return json.loads(frozen_bytes(path).decode("utf-8"))


def digest_bytes(value: bytes) -> str:
    return sha256(value).hexdigest()


def digest_path(path: Path) -> str:
    state = sha256()
    with path.open("rb") as source:
        for block in iter(lambda: source.read(1 << 20), b""):
            state.update(block)
    return state.hexdigest()


def semantic_digest(value: Any) -> str:
    return sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode("utf-8")).hexdigest()


def polynomial(record: dict[str, Any], marker: str) -> baseline.Polynomial:
    require(record["coordinate_order"] == list(baseline.HOMOGENEOUS_VARIABLES), marker)
    answer = baseline.decode_rows(record["sparse_polynomial"], 12, marker)
    require(record["term_count"] == len(answer), marker)
    return answer


def add(*polynomials: baseline.Polynomial) -> baseline.Polynomial:
    answer: baseline.Polynomial = {}
    for item in polynomials:
        for exponents, coefficient in item.items():
            answer[exponents] = answer.get(exponents, 0) + coefficient
    return baseline.normalize(answer)


def monomial(**powers: int) -> baseline.Polynomial:
    return {tuple(powers.get(variable, 0) for variable in baseline.HOMOGENEOUS_VARIABLES): 1}


def divide_monomial(polynomial_value: baseline.Polynomial, variable: str) -> baseline.Polynomial:
    position = baseline.HOMOGENEOUS_VARIABLES.index(variable)
    require(all(exponents[position] > 0 for exponents in polynomial_value), f"exact factor {variable}")
    return {
        exponents[:position] + (exponents[position] - 1,) + exponents[position + 1 :]: coefficient
        for exponents, coefficient in polynomial_value.items()
    }


def affine_projection(polynomial_value: baseline.Polynomial) -> baseline.Polynomial:
    return {
        tuple(exponents[position] for position in baseline.AFFINE_POSITIONS): coefficient
        for exponents, coefficient in polynomial_value.items()
    }


def build_context() -> dict[str, Any]:
    factor, parents, parent_digest = baseline.load_exact_sources()
    homogeneous = baseline.homogenize(factor)
    atlas = baseline.build_atlas()
    return {
        "factor": factor,
        "parents": parents,
        "parent_digest": parent_digest,
        "homogeneous": homogeneous,
        "atlas": atlas,
    }


def validate_repository() -> None:
    require(git_text("rev-parse", f"{CANDIDATE_REVISION}^{{commit}}") == CANDIDATE_REVISION, "candidate commit")
    require(git_text("rev-parse", f"{CANDIDATE_REVISION}^{{tree}}") == CANDIDATE_TREE, "candidate tree")
    require(digest_bytes(frozen_bytes(FRONTIER_PATH)) == EXPECTED_FRONTIER_SHA256, "candidate frontier file pin")
    require(digest_bytes(frozen_bytes(CONSTRUCTOR_RESULT_PATH)) == EXPECTED_RESULT_SHA256, "candidate result file pin")
    require(digest_bytes(frozen_bytes(CONSTRUCTOR_MANIFEST_PATH)) == EXPECTED_MANIFEST_SHA256, "candidate manifest file pin")


def validate_boundary_records(frontier: dict[str, Any], context: dict[str, Any]) -> list[int]:
    records = frontier["boundary_type_records"]
    require(frontier["boundary_type_order"] == list(baseline.TYPE_IDS), "boundary type order")
    require(frontier["boundary_type_count"] == len(records) == 7, "boundary record count")
    term_counts = []
    atlas_charts = {chart["chart_id"]: chart for chart in context["atlas"]["charts"]}
    expected_incidence_counts = (27, 36, 36, 36, 48, 48, 48)
    for index, (record, type_id, zero_variables) in enumerate(zip(records, baseline.TYPE_IDS, baseline.TYPE_ORDER, strict=True)):
        prefix = f"boundary {type_id}"
        require(record["type_id"] == type_id and record["type_index"] == index, f"{prefix} identity")
        require(record["zero_homogenizers"] == list(zero_variables), f"{prefix} zero set")
        zero_positions = tuple(baseline.HOMOGENEOUS_VARIABLES.index(variable) for variable in zero_variables)
        tangent_positions = tuple(position for position in range(12) if position not in zero_positions)
        restricted = baseline.restrict_zero(context["homogeneous"], zero_positions)
        require(polynomial(record["restricted_source"], f"{prefix} restricted source") == restricted, f"{prefix} restricted source")
        term_counts.append(len(restricted))

        ambient = record["ambient_singularity"]
        require(ambient["definition"] == "RESTRICT_ALL_TWELVE_PARTIALS_OF_FULL_F_AFTER_DIFFERENTIATION", f"{prefix} ambient semantics")
        require(ambient["derivative_count"] == len(ambient["restricted_derivatives"]) == 12, f"{prefix} ambient derivative count")
        for position, derivative_record in enumerate(ambient["restricted_derivatives"]):
            variable = baseline.HOMOGENEOUS_VARIABLES[position]
            require(derivative_record["variable"] == variable, f"{prefix} ambient derivative order")
            expected_derivative = baseline.restrict_zero(baseline.derivative(context["homogeneous"], position), zero_positions)
            require(polynomial(derivative_record["polynomial"], f"{prefix} ambient derivative {variable}") == expected_derivative, f"{prefix} ambient derivative {variable}")

        stratum = record["stratum_singularity"]
        require(stratum["definition"] == "DIFFERENTIATE_RESTRICTED_SOURCE_ONLY_IN_TANGENT_COORDINATES", f"{prefix} stratum semantics")
        require(stratum["normal_derivatives_are_not_stratum_generators"] is True, f"{prefix} ambient stratum distinction")
        require(stratum["tangent_transfer_exact_sparse_equality"] is True, f"{prefix} tangent transfer tag")
        tangent_variables = [baseline.HOMOGENEOUS_VARIABLES[position] for position in tangent_positions]
        require(stratum["tangent_variables"] == tangent_variables, f"{prefix} tangent variables")
        require(stratum["derivative_count"] == len(stratum["derivatives"]) == len(tangent_positions), f"{prefix} stratum derivative count")
        for position, derivative_record in zip(tangent_positions, stratum["derivatives"], strict=True):
            variable = baseline.HOMOGENEOUS_VARIABLES[position]
            require(derivative_record["variable"] == variable, f"{prefix} stratum derivative order")
            expected_derivative = baseline.derivative(restricted, position)
            require(polynomial(derivative_record["polynomial"], f"{prefix} stratum derivative {variable}") == expected_derivative, f"{prefix} stratum derivative {variable}")

        require(record["chart_incidence_count"] == len(record["chart_incidences"]) == expected_incidence_counts[index], f"{prefix} chart incidence count")
        expected_charts = [chart for chart in context["atlas"]["charts"] if all(variable in chart["available_boundary_homogenizers"] for variable in zero_variables)]
        require(len(expected_charts) == expected_incidence_counts[index], f"{prefix} independent incidence count")
        for actual, expected_chart in zip(record["chart_incidences"], expected_charts, strict=True):
            require(actual["chart_id"] in atlas_charts and actual["chart_id"] == expected_chart["chart_id"], f"{prefix} chart incidence identity")
            require(actual["chart_index"] == expected_chart["chart_index"] and actual["pivots"] == expected_chart["pivots"], f"{prefix} chart incidence pivots")
            require(actual["zero_homogenizers"] == list(zero_variables), f"{prefix} chart incidence type")
        overlap = record["overlap_deduplication"]
        require(overlap["representatives_quotiented"] == 0 and overlap["overlap_unit_certificates"] == [], f"{prefix} no overlap quotient")

        factors = record["factor_records"]
        if factors:
            factor_product: baseline.Polynomial = {tuple([0] * 12): 1}
            for factor_record in factors:
                factor_product = baseline.multiply(factor_product, polynomial(factor_record, f"{prefix} factor record"))
            require(baseline.scale(factor_product, -1) == restricted, f"{prefix} exact queued factorization")
            require("EXACT_FACTOR_IDENTITY" in record["factorization_status"], f"{prefix} factorization status")
        else:
            require(record["factorization_status"] == "NO_NONTRIVIAL_FACTOR_IDENTITY_ASSERTED" or type_id == "u_v_w", f"{prefix} factor nonclaim")
        require(record["processing_status"] == "EXACT_SOURCE_AND_JACOBIAN_DATA_COMPLETE", f"{prefix} processing status")
    require(term_counts == [11, 37, 23, 23, 64, 69, 47], "boundary restriction term counts")
    require(sum(expected_incidence_counts) == frontier["boundary_stratum_chart_incidence_count"] == 279, "boundary total incidence count")
    return term_counts


def validate_deepest(frontier: dict[str, Any], context: dict[str, Any]) -> dict[str, Any]:
    deep_record = frontier["boundary_type_records"][0]
    restricted = polynomial(deep_record["restricted_source"], "deepest restricted source")
    deep = frontier["deepest_branch_frontier"]
    factorization = deep["factorization"]
    h = polynomial(factorization["h"], "deepest h")
    L = polynomial(factorization["L"], "deepest L")
    C = polynomial(factorization["C"], "deepest C")
    require(h == monomial(h=1), "deepest h exact")
    expected_L = add(monomial(a=1, f=1), baseline.scale(monomial(c=1, d=1), -1))
    expected_C = {
        baseline.monomial12(a=1, e=1, i=1): 1,
        baseline.monomial12(a=1, f=1, h=1): -1,
        baseline.monomial12(b=1, d=1, i=1): -1,
        baseline.monomial12(b=1, f=1, g=1): 1,
        baseline.monomial12(c=1, d=1, h=1): 1,
        baseline.monomial12(c=1, e=1, g=1): -1,
    }
    require(L == expected_L and C == expected_C, "deepest L C exact")
    require(baseline.scale(baseline.multiply(baseline.multiply(h, L), C), -1) == restricted, "deepest product identity")
    require(factorization["exact_sparse_identity"] is True and factorization["factor_irreducibility_asserted"] is False and factorization["scheme_multiplicity_asserted"] is False, "deepest factor nonclaims")

    parents = context["parents"]
    parent08 = baseline.decode_rows(parents[8]["sparse_polynomial"], 9, "parent H08")
    parent22 = baseline.decode_rows(parents[22]["sparse_polynomial"], 9, "parent H22")
    parent34 = baseline.decode_rows(parents[34]["sparse_polynomial"], 9, "parent H34")
    require(parents[8]["factor_node_id"] == "H_08_1248" and parent08 == affine_projection(h), "deepest parent H08")
    require(parents[22]["factor_node_id"] == "H_22_1367" and parent22 == baseline.scale(affine_projection(L), -1), "deepest parent H22")
    require(parents[34]["factor_node_id"] == "H_34_1678" and parent34 == affine_projection(C), "deepest parent H34")
    matches = factorization["parent_factor_matches"]
    require([item["parent_factor_node_id"] for item in matches] == ["H_08_1248", "H_22_1367", "H_34_1678"], "deepest parent match identities")
    require(factorization["entire_deepest_source_excluded_from_strict_parent"] is True, "deepest strict parent source exclusion")

    cover = deep["stratum_singular_set_cover"]
    require(cover["seed_count"] == 5, "deepest five seed count")
    require(cover["scope"] == "SET_THEORETIC_COVER_IN_CHARACTERISTIC_ZERO;_NO_PRIMARY_DECOMPOSITION_CLAIM", "deepest set theoretic scope")
    processed = deep["processed_seed"]
    queued = deep["queued_seed_branches"]
    require(processed["branch_id"] == "B-UVW-01-h-L", "deepest processed seed")
    require([item["branch_id"] for item in queued] == ["B-UVW-02-h-C", "B-UVW-03-L-C", "B-UVW-04-SingL", "B-UVW-05-SingC"], "deepest queued seed identities")
    require([item["equations"] for item in queued[:3]] == [["h", "C"], ["a*f-c*d", "C"], ["a", "c", "d", "f"]], "deepest queued seed equations")
    require(queued[3]["equations"] == ["ALL_NINE_2x2_MINORS_OF_MATRIX_[[a,b,c],[d,e,f],[g,h,i]]"], "deepest SingC equations")
    require(all(item["strict_parent_exclusion"]["status"] == "PROVED" for item in queued), "deepest queued parent exclusions")
    # Reconciliation: Sing(L) lies in V(L,C), since a=c=d=f=0 forces both;
    # Sing(C) lies in V(L,C), since dC/dh=-L and Euler gives C=0.
    dC_dh = baseline.derivative(C, baseline.HOMOGENEOUS_VARIABLES.index("h"))
    require(dC_dh == baseline.scale(L, -1), "deepest SingC implies L")
    euler_C = add(*(
        baseline.multiply(monomial(**{variable: 1}), baseline.derivative(C, baseline.HOMOGENEOUS_VARIABLES.index(variable)))
        for variable in baseline.AFFINE_VARIABLES
    ))
    require(euler_C == baseline.scale(C, 3), "deepest SingC Euler implies C")
    sing_l_zero = tuple(baseline.HOMOGENEOUS_VARIABLES.index(variable) for variable in ("a", "c", "d", "f"))
    require(baseline.restrict_zero(L, sing_l_zero) == {} and baseline.restrict_zero(C, sing_l_zero) == {}, "deepest SingL contained in L C")

    normals = {
        item["variable"]: baseline.restrict_zero(
            baseline.derivative(context["homogeneous"], baseline.HOMOGENEOUS_VARIABLES.index(item["variable"])),
            tuple(baseline.HOMOGENEOUS_VARIABLES.index(variable) for variable in ("u", "v", "w")),
        )
        for item in deep_record["ambient_singularity"]["restricted_derivatives"]
    }
    require(divide_monomial(normals["u"], "h") is not None and divide_monomial(normals["v"], "h") is not None, "deepest h L normal vanish")
    transfer = processed["ambient_normal_transfer"]
    quotient = polynomial(transfer["dF_dw_quotient_by_L"], "deepest dFdw quotient")
    remainder = polynomial(transfer["dF_dw_remainder"], "deepest dFdw remainder")
    child_q = polynomial(processed["ambient_children"][1]["Q"], "deepest child Q")
    eQ = baseline.multiply(monomial(e=1), child_q)
    require(remainder == eQ, "deepest dFdw remainder eQ")
    require(normals["w"] == add(baseline.multiply(quotient, L), eQ), "deepest dFdw split identity")
    require(processed["ambient_cover_identity"] == "V(h,L,e*Q)=V(h,L,e) union V(h,L,Q)", "deepest ambient child cover")
    children = processed["ambient_children"]
    require(deep["completed_ambient_child_count"] == len(children) == 2, "deepest ambient child count")
    require([child["branch_id"] for child in children] == ["B-UVW-01a-h-L-e", "B-UVW-01b-h-L-Q"], "deepest ambient child identities")
    require(children[0]["equations"] == ["h", "a*f-c*d", "e"] and children[0]["dimension"] == 3 and children[0]["degree"] is None, "deepest first child invariants")
    require(children[1]["equations"] == ["h", "a*f-c*d", "Q"] and children[1]["dimension"] is None and children[1]["degree"] is None, "deepest second child nonclaims")
    require(all(child["projective_infinity_only"] is True and child["parent_factor_tests_required"] == 0 for child in children), "deepest child projective exclusion")
    require(deep["completed_source_factor_seed_count"] == 5, "deepest completed seed count")
    return {
        "candidate_seed_count": 5,
        "prior_pairwise_seed_count": 3,
        "five_seed_cover_exact": True,
        "SingL_contained_in_pair_L_C": True,
        "SingC_contained_in_pair_L_C": True,
        "five_seed_union_equals_prior_three_pairwise_seed_union": True,
        "scheme_radicality_or_primary_decomposition_claimed": False,
        "strict_parent_excluded_seed_count": 5,
        "ambient_child_count": 2,
        "ambient_child_split_identity_exact": True,
    }


def validate_uv(frontier: dict[str, Any], context: dict[str, Any]) -> dict[str, Any]:
    uv_record = frontier["boundary_type_records"][1]
    zero_positions = tuple(baseline.HOMOGENEOUS_VARIABLES.index(variable) for variable in ("u", "v"))
    restricted = baseline.restrict_zero(context["homogeneous"], zero_positions)
    family_zero_variables = ("b", "c", "u", "e", "f", "v")
    family_zero_positions = tuple(baseline.HOMOGENEOUS_VARIABLES.index(variable) for variable in family_zero_variables)
    require(baseline.restrict_zero(restricted, family_zero_positions) == {}, "uv family restricted source membership")
    ambient_derivatives = [
        baseline.restrict_zero(baseline.derivative(context["homogeneous"], position), zero_positions)
        for position in range(12)
    ]
    require(all(baseline.restrict_zero(item, family_zero_positions) == {} for item in ambient_derivatives), "uv family all twelve ambient derivatives")

    uv = frontier["u_v_branch_frontier"]
    require(uv["completed_known_branch_count"] == len(uv["completed_known_branches"]) == 1, "uv known branch count")
    known = uv["completed_known_branches"][0]
    require(known["branch_id"] == "B-UV-00-linear-P3-family" and known["semantic_sha256"] == EXPECTED_KNOWN_UV_SEMANTIC, "uv known branch identity")
    require(known["global_homogeneous_equations"] == ["u", "v", "b", "c", "e", "f"], "uv family equations")
    require(known["ambient_singular_membership"] == "ALL_TWELVE_RESTRICTED_FULL_DERIVATIVES_SUBSTITUTE_TO_EXACT_ZERO", "uv ambient membership claim")
    require(known["dimension"] == 3 and known["degree"] == 1 and known["multiplicity"] is None, "uv family invariants")
    witness = known["standard_chart_witness"]
    require(witness["pivots"] == ["a", "d", "w"] and witness["pivot_values"] == {"a": 1, "d": 1, "w": 1} and witness["free_parameters"] == ["g", "h", "i"], "uv standard chart witness")
    parent22 = baseline.decode_rows(context["parents"][22]["sparse_polynomial"], 9, "uv parent H22")
    affine_family_zeros = tuple(baseline.AFFINE_VARIABLES.index(variable) for variable in ("b", "c", "e", "f"))
    require(baseline.restrict_zero(parent22, affine_family_zeros) == {}, "uv H22 exact exclusion")
    exclusion = known["strict_parent_exclusion"]
    require(exclusion["parent_factor_node_id"] == "H_22_1367" and exclusion["status"] == "PROVED", "uv H22 exclusion claim")
    require(known["status"] == "COMPLETED_EXACT_POSITIVE_DIMENSIONAL_STRICT_PARENT_EXCLUDED_BRANCH", "uv branch status")
    require(known["affine_pullback"].startswith("NOT_ACCEPTED"), "uv no affine acceptance")
    require(uv["component_completeness_proved"] is False, "uv completeness nonclaim")

    pending = frontier["first_pending_branch"]
    require(pending["branch_id"] == "B-UV-01-unclassified-ambient-components", "pending branch identity")
    require(pending["type_id"] == "u_v" and pending["status"] == "FIRST_SOURCE_PINNED_UNRESOLVED_BRANCH_FAIL_CLOSED", "pending branch status")
    require(pending["known_branch_exhausts_ambient_ideal"] is False, "pending known branch nonexhaustion")
    require(pending["ambient_equation_count"] == 12 and pending["stratum_equation_count"] == 10, "pending equation counts")
    require(pending["ambient_equation_node_ids"] == [f"AD-1-{variable}" for variable in baseline.HOMOGENEOUS_VARIABLES], "pending ambient equation identities")
    require(pending["completed_known_branch_semantic_sha256"] == EXPECTED_KNOWN_UV_SEMANTIC, "pending known branch binding")
    require(pending["semantic_sha256"] == EXPECTED_PENDING_SEMANTIC, "pending semantic hash")
    require(uv["first_pending_branch_semantic_sha256"] == EXPECTED_PENDING_SEMANTIC, "uv pending hash binding")
    independent_pending_payload_sha256 = semantic_digest({key: value for key, value in pending.items() if key != "semantic_sha256"})
    return {
        "branch_id": known["branch_id"],
        "all_twelve_ambient_derivatives_zero_exact": True,
        "isomorphic_to_P3": True,
        "dimension": 3,
        "degree": 1,
        "scheme_multiplicity_claimed": False,
        "strict_parent_excluded_by": "H_22_1367",
        "accepted_affine_pullback": False,
        "known_branch_exhausts_ambient_ideal": False,
        "first_pending_branch_id": pending["branch_id"],
        "candidate_pending_semantic_sha256": pending["semantic_sha256"],
        "independent_pending_payload_sha256": independent_pending_payload_sha256,
    }


def evaluate(frontier: dict[str, Any], result: dict[str, Any], context: dict[str, Any]) -> dict[str, Any]:
    require(frontier["format"] == "d9-factor19069-homogenizer-boundary-type-constructor-frontier-v1", "frontier format")
    require(frontier["cycle_id"] == CYCLE_ID and frontier["track_id"] == "d9-factor19069-homogenizer-boundary-constructor", "frontier identity")
    require(frontier["base_revision"] == baseline.BASE_REVISION and frontier["base_tree"] == baseline.BASE_TREE, "frontier base")
    require(frontier["opening_revision"] == baseline.AUDITED_OPENING_REVISION and frontier["opening_tree"] == baseline.AUDITED_OPENING_TREE, "frontier opening")
    require(frontier["semantic_sha256"] == EXPECTED_FRONTIER_SEMANTIC, "frontier semantic pin")
    source = frontier["source_binding"]
    require(source["term_count"] == 108 and source["multidegree"] == [2, 2, 2] and source["reconstructed_from_pinned_source"] is True, "frontier source binding")
    term_counts = validate_boundary_records(frontier, context)
    deepest = validate_deepest(frontier, context)
    uv = validate_uv(frontier, context)

    overlap = frontier["overlap_accounting"]
    require(overlap == {"explicit_overlap_unit_certificates": 0, "inherited_directed_overlap_records": 4032, "representatives_quotiented": 0, "unsupported_deduplications": 0}, "frontier zero overlap quotient")
    parent = frontier["parent_factor_frontier"]
    require(parent["ordered_parent_factor_count"] == 70, "frontier parent count")
    require(parent["accepted_affine_branch_count"] == 0 and parent["completed_branch_parent_factor_pairs"] == 0, "frontier zero affine branch")
    require(parent["policy"] == "PULLBACK_TO_AFFINE_SINGULAR_IDEAL_BEFORE_ALL_70_PARENT_TESTS", "frontier parent test order")

    pending = frontier["first_pending_branch"]
    endpoint = frontier["endpoint_accounting"]
    require(endpoint["positive"].startswith("NOT_REACHED") and endpoint["negative"].startswith("NOT_REACHED"), "endpoint positive negative honesty")
    require(endpoint["null"] == "REACHED;FIRST_SOURCE_PINNED_UNRESOLVED_u_v_AMBIENT_BRANCH", "endpoint null honesty")
    require(endpoint["timeout"].startswith("NOT_REACHED"), "endpoint timeout honesty")
    require(endpoint["completed_boundary_types"] == 1 and endpoint["completed_deepest_source_factor_seeds"] == 5 and endpoint["completed_u_v_known_branches"] == 1, "endpoint completed census")
    require(endpoint["first_pending_branch_id"] == pending["branch_id"] and endpoint["first_pending_branch_semantic_sha256"] == EXPECTED_PENDING_SEMANTIC, "endpoint pending binding")
    require(frontier["endpoint"] == "FIRST_SOURCE_PINNED_UNRESOLVED_TYPE_OR_BRANCH_CLASSIFICATION", "frontier selected endpoint")
    require(frontier["classification"] == "DEEPEST_TYPE_EXCLUDED_BY_PINNED_PARENT_FACTORS_THEN_FIRST_u_v_BRANCH_UNRESOLVED_FAIL_CLOSED", "frontier classification")
    require(frontier["ledger_change_recommended"] == "none" and frontier["theorem_ledger"] == "2/9", "frontier ledger")
    resources = frontier["resource_accounting"]
    require(resources["ceiling_hit"] is False and resources["exact_algebra_branch_nodes"] == 13135 and resources["exact_algebra_branch_nodes"] <= resources["exact_algebra_branch_node_ceiling"], "frontier resource accounting")
    require(resources["numerical_or_modular_probe_used"] is False and resources["whole_atlas_groebner_retry_used"] is False and resources["network_or_connector_used"] is False, "frontier prohibited scope")

    require(result["format"] == "d9-factor19069-homogenizer-boundary-type-constructor-result-v1", "constructor result format")
    require(result["outcome"] == "pass" and result["classification"] == frontier["classification"], "constructor result classification")
    require(result["boundary_type_count"] == 7 and result["restricted_source_term_counts"] == term_counts, "constructor result source census")
    require(result["completed_deepest_source_factor_seeds"] == 5 and result["completed_u_v_known_branches"] == 1, "constructor result completed census")
    require(result["first_pending_branch_id"] == pending["branch_id"] and result["first_pending_branch_semantic_sha256"] == EXPECTED_PENDING_SEMANTIC, "constructor result pending hash")
    require(result["overlap_representatives_quotiented"] == 0 and result["accepted_affine_branch_count"] == 0 and result["completed_affine_branch_parent_factor_pairs"] == 0, "constructor result zero downstream")
    require(result["endpoint"] == frontier["endpoint"] and result["ledger_change_recommended"] == "none" and result["theorem_ledger"] == "2/9", "constructor result endpoint ledger")
    require("NO_COMPLETE_SEVEN_TYPE_BRANCH_CLASSIFICATION" in result["nonconsequences"] and "NO_UNSUPPORTED_RADICALITY_DEGREE_OR_MULTIPLICITY_CLAIM" in result["nonconsequences"], "constructor result nonconsequences")

    return {
        "format": "d9-factor19069-homogenizer-boundary-falsifier-candidate-delta-v1",
        "cycle_id": CYCLE_ID,
        "track_id": TRACK_ID,
        "candidate_revision": CANDIDATE_REVISION,
        "candidate_tree": CANDIDATE_TREE,
        "candidate_frontier_sha256": EXPECTED_FRONTIER_SHA256,
        "candidate_result_sha256": EXPECTED_RESULT_SHA256,
        "candidate_frontier_semantic_sha256": EXPECTED_FRONTIER_SEMANTIC,
        "source_and_derivative_evaluation": {
            "boundary_type_count": 7,
            "boundary_type_order": list(baseline.TYPE_IDS),
            "restricted_source_term_counts": term_counts,
            "all_seven_restricted_sources_exact": True,
            "all_84_restricted_full_derivatives_exact": True,
            "all_tangent_derivatives_exact": True,
            "ambient_stratum_semantics_distinct": True,
            "boundary_stratum_chart_incidence_count": 279,
            "queued_factor_identities_exact_where_asserted": True,
        },
        "deepest_evaluation": deepest,
        "u_v_evaluation": uv,
        "endpoint_evaluation": {
            "positive": "NOT_REACHED",
            "negative": "NOT_REACHED",
            "null": "REACHED_FIRST_PINNED_UNRESOLVED_u_v_AMBIENT_BRANCH",
            "timeout": "NOT_REACHED",
            "completed_boundary_types": 1,
            "overlap_representatives_quotiented": 0,
            "accepted_affine_branch_count": 0,
            "ledger_delta": "none",
            "theorem_ledger": "2/9",
        },
        "producer_code_imported": False,
        "producer_acceptance_logic_imported": False,
        "numerical_modular_or_sampled_inference_used": False,
        "google_drive_connector_used": False,
        "github_write_used": False,
        "verdict": VERDICT,
    }


def hostile_mutations(frontier: dict[str, Any], result: dict[str, Any], context: dict[str, Any]) -> list[str]:
    cases: list[tuple[str, Callable[[dict[str, Any], dict[str, Any]], None]]] = [
        ("frontier format", lambda f, r: f.__setitem__("format", "wrong")),
        ("frontier semantic pin", lambda f, r: f.__setitem__("semantic_sha256", "0" * 64)),
        ("frontier source binding", lambda f, r: f["source_binding"].__setitem__("term_count", 107)),
        ("boundary record count", lambda f, r: f["boundary_type_records"].pop()),
        ("boundary u_v_w restricted source", lambda f, r: f["boundary_type_records"][0]["restricted_source"]["sparse_polynomial"][0].__setitem__("coefficient", 9)),
        ("boundary u_v_w ambient derivative a", lambda f, r: f["boundary_type_records"][0]["ambient_singularity"]["restricted_derivatives"][0]["polynomial"]["sparse_polynomial"][0].__setitem__("coefficient", 9)),
        ("boundary u_v ambient stratum distinction", lambda f, r: f["boundary_type_records"][1]["stratum_singularity"].__setitem__("normal_derivatives_are_not_stratum_generators", False)),
        ("boundary u_w exact queued factorization", lambda f, r: f["boundary_type_records"][2]["factor_records"][2]["sparse_polynomial"][0].__setitem__("coefficient", 9)),
        ("boundary v_w chart incidence count", lambda f, r: f["boundary_type_records"][3].__setitem__("chart_incidence_count", 35)),
        ("boundary u no overlap quotient", lambda f, r: f["boundary_type_records"][4]["overlap_deduplication"].__setitem__("representatives_quotiented", 1)),
        ("boundary v tangent transfer tag", lambda f, r: f["boundary_type_records"][5]["stratum_singularity"].__setitem__("tangent_transfer_exact_sparse_equality", False)),
        ("boundary w exact queued factorization", lambda f, r: f["boundary_type_records"][6]["factor_records"][1]["sparse_polynomial"][0].__setitem__("coefficient", 9)),
        ("deepest five seed count", lambda f, r: f["deepest_branch_frontier"]["stratum_singular_set_cover"].__setitem__("seed_count", 3)),
        ("deepest set theoretic scope", lambda f, r: f["deepest_branch_frontier"]["stratum_singular_set_cover"].__setitem__("scope", "PRIMARY_DECOMPOSITION")),
        ("deepest queued seed identities", lambda f, r: f["deepest_branch_frontier"]["queued_seed_branches"][0].__setitem__("branch_id", "fake")),
        ("deepest queued seed equations", lambda f, r: f["deepest_branch_frontier"]["queued_seed_branches"][2].__setitem__("equations", ["a"])),
        ("deepest queued parent exclusions", lambda f, r: f["deepest_branch_frontier"]["queued_seed_branches"][3]["strict_parent_exclusion"].__setitem__("status", "PENDING")),
        ("deepest dFdw split identity", lambda f, r: f["deepest_branch_frontier"]["processed_seed"]["ambient_normal_transfer"]["dF_dw_quotient_by_L"]["sparse_polynomial"][0].__setitem__("coefficient", 9)),
        ("deepest dFdw remainder", lambda f, r: f["deepest_branch_frontier"]["processed_seed"]["ambient_normal_transfer"]["dF_dw_remainder"]["sparse_polynomial"][0].__setitem__("coefficient", 9)),
        ("deepest ambient child count", lambda f, r: f["deepest_branch_frontier"].__setitem__("completed_ambient_child_count", 1)),
        ("deepest ambient child identities", lambda f, r: f["deepest_branch_frontier"]["processed_seed"]["ambient_children"][1].__setitem__("branch_id", "fake")),
        ("deepest first child invariants", lambda f, r: f["deepest_branch_frontier"]["processed_seed"]["ambient_children"][0].__setitem__("dimension", 4)),
        ("deepest second child nonclaims", lambda f, r: f["deepest_branch_frontier"]["processed_seed"]["ambient_children"][1].__setitem__("degree", 2)),
        ("deepest child projective exclusion", lambda f, r: f["deepest_branch_frontier"]["processed_seed"]["ambient_children"][0].__setitem__("projective_infinity_only", False)),
        ("uv family equations", lambda f, r: f["u_v_branch_frontier"]["completed_known_branches"][0]["global_homogeneous_equations"].pop()),
        ("uv ambient membership claim", lambda f, r: f["u_v_branch_frontier"]["completed_known_branches"][0].__setitem__("ambient_singular_membership", "SAMPLED")),
        ("uv family invariants", lambda f, r: f["u_v_branch_frontier"]["completed_known_branches"][0].__setitem__("degree", 2)),
        ("uv H22 exclusion claim", lambda f, r: f["u_v_branch_frontier"]["completed_known_branches"][0]["strict_parent_exclusion"].__setitem__("parent_factor_node_id", "H_21_fake")),
        ("uv completeness nonclaim", lambda f, r: f["u_v_branch_frontier"].__setitem__("component_completeness_proved", True)),
        ("pending branch identity", lambda f, r: f["first_pending_branch"].__setitem__("branch_id", "fake")),
        ("pending known branch nonexhaustion", lambda f, r: f["first_pending_branch"].__setitem__("known_branch_exhausts_ambient_ideal", True)),
        ("pending semantic hash", lambda f, r: f["first_pending_branch"].__setitem__("semantic_sha256", "0" * 64)),
        ("frontier zero overlap quotient", lambda f, r: f["overlap_accounting"].__setitem__("representatives_quotiented", 1)),
        ("frontier zero affine branch", lambda f, r: f["parent_factor_frontier"].__setitem__("accepted_affine_branch_count", 1)),
        ("endpoint positive negative honesty", lambda f, r: f["endpoint_accounting"].__setitem__("positive", "REACHED")),
        ("endpoint null honesty", lambda f, r: f["endpoint_accounting"].__setitem__("null", "NOT_REACHED")),
        ("endpoint timeout honesty", lambda f, r: f["endpoint_accounting"].__setitem__("timeout", "REACHED")),
        ("frontier classification", lambda f, r: f.__setitem__("classification", "COMPLETE")),
        ("frontier ledger", lambda f, r: f.__setitem__("theorem_ledger", "3/9")),
        ("frontier prohibited scope", lambda f, r: f["resource_accounting"].__setitem__("whole_atlas_groebner_retry_used", True)),
        ("constructor result pending hash", lambda f, r: r.__setitem__("first_pending_branch_semantic_sha256", "0" * 64)),
        ("constructor result zero downstream", lambda f, r: r.__setitem__("accepted_affine_branch_count", 1)),
        ("constructor result endpoint ledger", lambda f, r: r.__setitem__("ledger_change_recommended", "+1")),
        ("constructor result nonconsequences", lambda f, r: r["nonconsequences"].remove("NO_COMPLETE_SEVEN_TYPE_BRANCH_CLASSIFICATION")),
    ]
    rejected = []
    for marker, edit in cases:
        mutated_frontier = deepcopy(frontier)
        mutated_result = deepcopy(result)
        edit(mutated_frontier, mutated_result)
        try:
            evaluate(mutated_frontier, mutated_result, context)
        except Reject as error:
            require(marker in str(error), f"wrong hostile rejection {marker}: {error}")
            rejected.append(marker)
        else:
            raise Reject(f"hostile mutation accepted {marker}")
    require(len(rejected) >= 24, "delta hostile mutation census")
    return rejected


def build_manifest() -> dict[str, Any]:
    pins = {relative: digest_path(ROOT / relative) for relative in LOCAL_INPUTS}
    script_relative = (HERE / "verify_candidate_delta.py").relative_to(ROOT).as_posix()
    pins[script_relative] = digest_path(HERE / "verify_candidate_delta.py")
    return {
        "format": "d9-factor19069-homogenizer-boundary-falsifier-candidate-delta-manifest-v1",
        "cycle_id": CYCLE_ID,
        "track_id": TRACK_ID,
        "candidate_revision": CANDIDATE_REVISION,
        "candidate_tree": CANDIDATE_TREE,
        "frozen_constructor_sha256": {
            FRONTIER_PATH: EXPECTED_FRONTIER_SHA256,
            CONSTRUCTOR_RESULT_PATH: EXPECTED_RESULT_SHA256,
            CONSTRUCTOR_MANIFEST_PATH: EXPECTED_MANIFEST_SHA256,
        },
        "source_count": len(pins),
        "source_sha256": pins,
        "candidate_delta_sha256": digest_path(DELTA),
        "constructor_code_imported": False,
        "constructor_acceptance_logic_imported": False,
        "branch_name_required": False,
        "numerical_modular_or_sampled_inference_used": False,
        "network_or_connector_used": False,
        "google_drive_connector_used": False,
        "github_write_used": False,
    }


def validate_manifest(candidate: dict[str, Any]) -> None:
    require(candidate["format"] == "d9-factor19069-homogenizer-boundary-falsifier-candidate-delta-manifest-v1", "delta manifest format")
    require(candidate["candidate_revision"] == CANDIDATE_REVISION and candidate["candidate_tree"] == CANDIDATE_TREE, "delta manifest candidate")
    require(candidate["source_count"] == len(candidate["source_sha256"]), "delta manifest source count")
    for relative, expected in candidate["source_sha256"].items():
        require(digest_path(ROOT / relative) == expected, f"delta manifest source pin {relative}")
    require(candidate["frozen_constructor_sha256"] == {FRONTIER_PATH: EXPECTED_FRONTIER_SHA256, CONSTRUCTOR_RESULT_PATH: EXPECTED_RESULT_SHA256, CONSTRUCTOR_MANIFEST_PATH: EXPECTED_MANIFEST_SHA256}, "delta manifest frozen pins")
    require(candidate["candidate_delta_sha256"] == digest_path(DELTA), "delta manifest artifact pin")
    for key in ("constructor_code_imported", "constructor_acceptance_logic_imported", "numerical_modular_or_sampled_inference_used", "network_or_connector_used", "google_drive_connector_used", "github_write_used"):
        require(candidate[key] is False, f"delta manifest scope {key}")
    require(candidate["branch_name_required"] is False, "delta manifest portable branch mode")


def validate_delta(candidate: dict[str, Any], expected: dict[str, Any]) -> None:
    require(candidate == expected, "candidate delta exact equality")
    require(candidate["verdict"] == VERDICT, "candidate delta verdict")
    require(candidate["endpoint_evaluation"]["ledger_delta"] == "none" and candidate["endpoint_evaluation"]["theorem_ledger"] == "2/9", "candidate delta ledger")


def write_json(path: Path, value: Any) -> None:
    with path.open("w", encoding="utf-8", newline="\n") as target:
        target.write(json.dumps(value, indent=2, sort_keys=True) + "\n")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    arguments = parser.parse_args()
    validate_repository()
    frontier = frozen_json(FRONTIER_PATH)
    constructor_result = frozen_json(CONSTRUCTOR_RESULT_PATH)
    context = build_context()
    expected = evaluate(frontier, constructor_result, context)
    if arguments.write:
        write_json(DELTA, expected)
        write_json(DELTA_MANIFEST, build_manifest())
        rejected = hostile_mutations(frontier, constructor_result, context)
        write_json(DELTA_HOSTILE, {
            "format": "d9-factor19069-homogenizer-boundary-falsifier-candidate-delta-hostile-tests-v1",
            "cycle_id": CYCLE_ID,
            "track_id": TRACK_ID,
            "total": len(rejected),
            "rejected": len(rejected),
            "rejection_markers": rejected,
        })
        write_json(DELTA_RESULT, {
            "format": "d9-factor19069-homogenizer-boundary-falsifier-candidate-delta-result-v1",
            "cycle_id": CYCLE_ID,
            "track_id": TRACK_ID,
            "candidate_revision": CANDIDATE_REVISION,
            "candidate_tree": CANDIDATE_TREE,
            "outcome": "pass",
            "verdict": VERDICT,
            "candidate_delta_sha256": digest_path(DELTA),
            "candidate_delta_manifest_sha256": digest_path(DELTA_MANIFEST),
            "candidate_delta_hostile_tests_sha256": digest_path(DELTA_HOSTILE),
            "hostile_mutations_rejected": len(rejected),
            "completed_boundary_types": 1,
            "deepest_source_factor_seed_count": 5,
            "deepest_ambient_child_count": 2,
            "completed_u_v_known_branch_count": 1,
            "first_pending_branch_id": "B-UV-01-unclassified-ambient-components",
            "first_pending_branch_semantic_sha256": EXPECTED_PENDING_SEMANTIC,
            "overlap_representatives_quotiented": 0,
            "accepted_affine_branch_count": 0,
            "ledger_delta": "none",
            "theorem_ledger": "2/9",
            "google_drive_connector_used": False,
            "github_write_used": False,
        })

    delta = json.loads(DELTA.read_text(encoding="utf-8"))
    manifest = json.loads(DELTA_MANIFEST.read_text(encoding="utf-8"))
    hostile = json.loads(DELTA_HOSTILE.read_text(encoding="utf-8"))
    result = json.loads(DELTA_RESULT.read_text(encoding="utf-8"))
    validate_delta(delta, expected)
    validate_manifest(manifest)
    rejected = hostile_mutations(frontier, constructor_result, context)
    require(hostile["total"] == hostile["rejected"] == len(rejected) and hostile["rejection_markers"] == rejected, "delta hostile report")
    require(result["outcome"] == "pass" and result["verdict"] == VERDICT, "delta result verdict")
    require(result["candidate_delta_sha256"] == digest_path(DELTA) and result["candidate_delta_manifest_sha256"] == digest_path(DELTA_MANIFEST) and result["candidate_delta_hostile_tests_sha256"] == digest_path(DELTA_HOSTILE), "delta result artifact pins")
    require(result["hostile_mutations_rejected"] == len(rejected), "delta result hostile count")
    require(result["first_pending_branch_semantic_sha256"] == EXPECTED_PENDING_SEMANTIC, "delta result pending hash")
    require(result["overlap_representatives_quotiented"] == result["accepted_affine_branch_count"] == 0, "delta result downstream zero")
    require(result["ledger_delta"] == "none" and result["theorem_ledger"] == "2/9", "delta result ledger")
    print(
        "PASS frozen candidate delta: seven exact source/Jacobian records, five-seed reconciliation, "
        f"two ambient children, exact uv P3 family, pinned residual, {len(rejected)} hostile mutations; ledger 2/9"
    )


if __name__ == "__main__":
    try:
        main()
    except (Reject, baseline.Reject, KeyError, IndexError, TypeError, ValueError, OSError, json.JSONDecodeError, subprocess.CalledProcessError) as error:
        print(f"REJECT: {error}", file=sys.stderr)
        raise SystemExit(1)
