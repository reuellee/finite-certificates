#!/usr/bin/env python3
"""Independent frozen-object closing referee for the boundary-type gate.

The verifier intentionally reconstructs the sparse algebra from the pinned
predecessor JSON.  It does not import constructor, falsifier, or certificate
acceptance code.  All candidate material is read from immutable Git objects;
therefore this file remains runnable after cherry-pick onto an integration
branch or in a clean clone that has the reviewed objects.
"""

from __future__ import annotations

from copy import deepcopy
from hashlib import sha256
import itertools
import json
import os
from pathlib import Path
import re
import subprocess


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
CYCLE_ID = "2026-09-01-d9-row2599-factor19069-homogenizer-boundary-type-stratification-gate1"
CYCLE_DIR = ROOT / "ops" / "research-team" / "cycles" / CYCLE_ID
BASE = "0ffb0295d74e6c50a3c198b67c9821d2fe2e2760"
BASE_TREE = "d01cfbbe04f721496a91d13f85d3688262869ac0"
CANDIDATE = "a8ae8f9a73c1be1b53a928dd92dc9a5d02b54cf6"
CANDIDATE_TREE = "23e251a4af6cd4ae45315cc8bbcdd590d449555e"
CLOSING = "5061ffab4f04356dc9b641985e8b9dffaf279057"
CLOSING_TREE = "3103148c1c0915eff02d518b0332fbb515511781"
CORRECTION = "192bea3afdd7c06aa52e479acb681c2fa2d06e69"
CORRECTION_TREE = "b98dc3f9020db03b6b4a0a387ad0421a054870c0"
CONSTRUCTOR_SNAPSHOT = "25757510dd88e8b7bbe5668c89f93b2a46b264de"
CONSTRUCTOR_SNAPSHOT_TREE = "47395637cc10c2bd736530719b6e2f3cf57b1629"
TARGET = "D9_ROW2599_FACTOR19069_HOMOGENIZER_BOUNDARY_TYPE_STRATIFICATION_GATE1"
SUCCESSOR = "D9_ROW2599_FACTOR19069_UV_AMBIENT_SINGULAR_PARENT_EXCLUSION_GATE1"
ACTIVE_SUCCESSOR = "D3_COVERAGE_CERTIFIED_GLOBAL_MASTER_CLOSURE_GLUE_LABEL_STRICT_CLOSURE_THEOREM_LEVERAGE_AUDIT_GATE1"
PENDING = "B-UV-01-unclassified-ambient-components"
PENDING_SHA = "2747fcc6923b44996bfe79c0d06d2f88169f9fedea465cdecaa3c104bcf6b8b5"
ORDER = ("a", "b", "c", "u", "d", "e", "f", "v", "g", "h", "i", "w")
AFFINE_ORDER = ("a", "b", "c", "d", "e", "f", "g", "h", "i")
BLOCKS = (("a", "b", "c", "u"), ("d", "e", "f", "v"), ("g", "h", "i", "w"))
TYPES = (("u", "v", "w"), ("u", "v"), ("u", "w"), ("v", "w"), ("u",), ("v",), ("w",))
TYPE_IDS = tuple("_".join(item) for item in TYPES)
TERM_COUNTS = (11, 37, 23, 23, 64, 69, 47)
INCIDENCE_COUNTS = (27, 36, 36, 36, 48, 48, 48)
PREDECESSOR_PATH = "ops/team/d9-factor19069-explicit-trihom-jacobian-chart-constructor/PROJECTIVE_CHART_FRONTIER.json"
FRONTIER_PATH = "ops/team/d9-factor19069-homogenizer-boundary-constructor/HOMOGENIZER_BOUNDARY_TYPE_FRONTIER.json"
CONSTRUCTOR_RESULT_PATH = "ops/team/d9-factor19069-homogenizer-boundary-constructor/RESULT.json"
CERTIFICATE_RESULT_PATH = "ops/team/d9-factor19069-homogenizer-boundary-certificate/RESULT.json"
COMPARISON_PATH = "ops/team/d9-factor19069-homogenizer-boundary-certificate/CANDIDATE_COMPARISON.json"
DELTA_PATH = "ops/team/d9-factor19069-homogenizer-boundary-falsifier/CANDIDATE_DELTA_RESULT.json"
MANIFEST_PATH = f"ops/research-team/cycles/{CYCLE_ID}/CANDIDATE_MANIFEST.json"
CLEAN_PATH = f"ops/research-team/cycles/{CYCLE_ID}/CLEAN_REPLAY.json"
REPORT_PATH = f"ops/research-team/cycles/{CYCLE_ID}/CYCLE_REPORT.md"
OPENING_PATH = f"ops/research-team/cycles/{CYCLE_ID}/OPENING_AUDIT.json"
EXPECTED_ATTACKS = (
    "moved-candidate-revision", "moved-candidate-tree", "moved-closing-revision",
    "moved-closing-tree", "source-term-drift", "type-omission", "type-order-drift",
    "incidence-drift", "ambient-derivative-drift", "normal-derivative-loss",
    "factor-sign-drift", "parent-factor-sign-drift", "false-radicality",
    "false-multiplicity", "missing-deepest-seed", "missing-ambient-child",
    "false-uv-dimension", "false-uv-degree", "false-uv-exhaustion",
    "residual-hash-drift", "false-overlap-quotient", "false-affine-acceptance",
    "false-70-parent-completion", "false-strict-real-tag", "false-connected-tag",
    "positive-endpoint-inflation", "negative-endpoint-inflation",
    "null-endpoint-erasure", "ledger-inflation", "wrong-successor-count",
    "wrong-successor-target", "revived-retired-route", "clean-replay-same-file",
    "clean-replay-dirty", "candidate-pin-drift", "certificate-scope-inflation",
    "continued-local-route-after-ledger-stagnation", "deferred-route-promoted-active",
    "missing-fresh-theorem-leverage-audit", "wrong-diagonal3-global-priority",
)

Poly = dict[tuple[int, ...], int]


class Reject(AssertionError):
    pass


def require(condition: bool, message: str) -> None:
    if not condition:
        raise Reject(message)


def git(*args: str, binary: bool = False) -> bytes | str:
    value = subprocess.check_output(
        ["git", "-c", f"safe.directory={ROOT.as_posix()}", *args],
        cwd=ROOT,
        text=not binary,
    )
    return value if binary else value.strip()


def frozen_bytes(revision: str, path: str) -> bytes:
    return git("show", f"{revision}:{path}", binary=True)  # type: ignore[return-value]


def frozen_json(revision: str, path: str) -> dict:
    return json.loads(frozen_bytes(revision, path))


def digest(data: bytes) -> str:
    return sha256(data).hexdigest()


def canonical(value: object) -> bytes:
    return (json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True) + "\n").encode("ascii")


def semantic(value: dict) -> str:
    item = deepcopy(value)
    item.pop("semantic_sha256", None)
    return digest(canonical(item))


def normalize(poly: Poly) -> Poly:
    return {m: c for m, c in poly.items() if c}


def sparse_terms(terms: list[dict], arity: int = 12) -> Poly:
    out: Poly = {}
    previous = None
    for term in terms:
        exponent = tuple(term["exponents"])
        require(len(exponent) == arity and all(isinstance(x, int) and x >= 0 for x in exponent), "invalid sparse exponent")
        require(previous is None or previous < exponent, "sparse order or duplicate drift")
        previous = exponent
        coefficient = term["coefficient"]
        require(isinstance(coefficient, int) and coefficient != 0, "invalid sparse coefficient")
        out[exponent] = coefficient
    return out


def sparse_record(record: dict, arity: int = 12) -> Poly:
    require(record["coefficient_field"] == "Q", "coefficient field drift")
    expected_order = list(ORDER if arity == 12 else AFFINE_ORDER)
    require(record["coordinate_order"] == expected_order, "coordinate order drift")
    value = sparse_terms(record["sparse_polynomial"], arity)
    require(record["term_count"] == len(value), "polynomial term count drift")
    require(record["semantic_sha256"] == semantic(record), "polynomial semantic drift")
    return value


def add(*polys: Poly) -> Poly:
    out: Poly = {}
    for poly in polys:
        for monomial, coefficient in poly.items():
            out[monomial] = out.get(monomial, 0) + coefficient
    return normalize(out)


def scale(poly: Poly, coefficient: int) -> Poly:
    return normalize({m: coefficient * c for m, c in poly.items()})


def multiply(left: Poly, right: Poly) -> Poly:
    out: Poly = {}
    for lm, lc in left.items():
        for rm, rc in right.items():
            key = tuple(a + b for a, b in zip(lm, rm))
            out[key] = out.get(key, 0) + lc * rc
    return normalize(out)


def mono(coefficient: int = 1, **powers: int) -> Poly:
    exponent = tuple(powers.get(name, 0) for name in ORDER)
    return {exponent: coefficient} if coefficient else {}


def derivative(poly: Poly, variable: str) -> Poly:
    index = ORDER.index(variable)
    out: Poly = {}
    for monomial, coefficient in poly.items():
        if monomial[index]:
            reduced = list(monomial)
            power = reduced[index]
            reduced[index] -= 1
            key = tuple(reduced)
            out[key] = out.get(key, 0) + coefficient * power
    return normalize(out)


def restrict_zero(poly: Poly, variables: tuple[str, ...]) -> Poly:
    indices = tuple(ORDER.index(name) for name in variables)
    return {m: c for m, c in poly.items() if all(m[index] == 0 for index in indices)}


def lift_parent(record: dict) -> Poly:
    value = sparse_terms(record["sparse_polynomial"], 9)
    out: Poly = {}
    for monomial, coefficient in value.items():
        exponent = [0] * 12
        for name, power in zip(AFFINE_ORDER, monomial):
            exponent[ORDER.index(name)] = power
        out[tuple(exponent)] = coefficient
    return out


def package_from_frozen_objects() -> dict:
    return {
        "manifest": frozen_json(CORRECTION, MANIFEST_PATH),
        "clean": frozen_json(CLOSING, CLEAN_PATH),
        "report": frozen_bytes(CORRECTION, REPORT_PATH).decode("utf-8"),
        "opening": frozen_json(CANDIDATE, OPENING_PATH),
        "frontier": frozen_json(CANDIDATE, FRONTIER_PATH),
        "constructor_result": frozen_json(CANDIDATE, CONSTRUCTOR_RESULT_PATH),
        "certificate": frozen_json(CANDIDATE, CERTIFICATE_RESULT_PATH),
        "comparison": frozen_json(CANDIDATE, COMPARISON_PATH),
        "delta": frozen_json(CANDIDATE, DELTA_PATH),
        "candidate_revision": CANDIDATE,
        "candidate_tree": CANDIDATE_TREE,
        "closing_revision": CLOSING,
        "closing_tree": CLOSING_TREE,
        "correction_revision": CORRECTION,
        "correction_tree": CORRECTION_TREE,
        "referee_strategy": "RETIRE_DEFER_FACTOR19069_BOUNDARY_DECOMPOSITION",
        "selected_active_successor": ACTIVE_SUCCESSOR,
        "selected_active_successor_count": 1,
        "fresh_theorem_leverage_audit_required": True,
        "next_active_priority": "DIAGONAL_3_COVERAGE_CERTIFIED_GLOBAL_MASTER_CLOSURE_GLUING_LABELS_STRICT_CLOSURE",
    }


def reconstruct_context(opening: dict) -> dict:
    require(opening["base_revision"] == BASE and opening["base_tree"] == BASE_TREE, "opening base drift")
    require(opening["selected_target"] == TARGET and opening["selected_count"] == 1, "opening target drift")
    require(opening["opening_ledger"] == "2/9", "opening ledger drift")
    for path, expected in opening["pins"].items():
        require(digest(frozen_bytes(BASE, path)) == expected, f"opening source pin drift: {path}")
    predecessor = frozen_json(BASE, PREDECESSOR_PATH)
    source_record = predecessor["trihomogeneous_source"]["polynomial"]
    require(source_record["coordinate_order"] == list(ORDER), "source coordinate order")
    source = sparse_terms(source_record["sparse_polynomial"])
    require(len(source) == source_record["term_count"] == 108, "source term census")
    require(all(sum(m[0:4]) == sum(m[4:8]) == sum(m[8:12]) == 2 for m in source), "source multidegree")
    atlas = predecessor["chart_atlas"]
    require(atlas["standard_chart_count"] == len(atlas["charts"]) == 64, "chart census")
    require(atlas["directed_overlap_record_count"] == sum(c["overlap_record_count"] for c in atlas["charts"]) == 4032, "overlap census")
    require(all(c["overlap_record_count"] == len(c["overlap_records"]) == 63 for c in atlas["charts"]), "per-chart overlap census")
    require(atlas["boundary_stratum_record_count"] == sum(len(c["boundary_strata"]) for c in atlas["charts"]) == 279, "atlas incidence census")
    require(predecessor["parent_factor_incidence_frontier"]["ordered_factor_count"] == 70, "predecessor parent census")
    parents = predecessor["parent_factor_incidence_frontier"]["records"]
    require(len(parents) == 70 and [p["factor_index"] for p in parents] == list(range(70)), "ordered parent factors")
    canonical_state = frozen_json(BASE, "ai/omreal/data/CANONICAL_RESEARCH_STATE_V6.json")
    require(canonical_state["theorem"]["score"] == "2/9", "canonical ledger")
    require(canonical_state["theorem"]["diagonal_nine"] == "OPEN", "canonical diagonal nine")
    require(canonical_state["theorem"]["theorem_level_counterexample"] == "NOT_FOUND", "canonical theorem counterexample")
    return {"predecessor": predecessor, "source": source, "parents": parents}


def validate_type_records(frontier: dict, context: dict) -> tuple[int, int, int]:
    source = context["source"]
    predecessor = context["predecessor"]
    records = frontier["boundary_type_records"]
    require(frontier["boundary_type_count"] == len(records) == 7, "boundary type count")
    require(frontier["boundary_type_order"] == list(TYPE_IDS), "boundary type order")
    tangent_total = normal_total = ambient_total = 0
    for index, (record, zeros, term_count, incidence_count) in enumerate(zip(records, TYPES, TERM_COUNTS, INCIDENCE_COUNTS)):
        type_id = TYPE_IDS[index]
        require(record["type_index"] == index and record["type_id"] == type_id, f"type identity {type_id}")
        require(record["zero_homogenizers"] == list(zeros), f"type zeros {type_id}")
        restricted = restrict_zero(source, zeros)
        require(len(restricted) == term_count, f"restricted term census {type_id}")
        require(sparse_record(record["restricted_source"]) == restricted, f"restricted source {type_id}")
        ambient = record["ambient_singularity"]
        require(ambient["derivative_count"] == len(ambient["restricted_derivatives"]) == 12, f"ambient derivative census {type_id}")
        ambient_map = {}
        for variable, item in zip(ORDER, ambient["restricted_derivatives"]):
            require(item["variable"] == variable, f"ambient derivative order {type_id}")
            value = sparse_record(item["polynomial"])
            require(value == restrict_zero(derivative(source, variable), zeros), f"ambient derivative {type_id}/{variable}")
            ambient_map[variable] = value
        tangents = tuple(variable for variable in ORDER if variable not in zeros)
        stratum = record["stratum_singularity"]
        require(stratum["tangent_variables"] == list(tangents), f"tangent variables {type_id}")
        require(stratum["derivative_count"] == len(stratum["derivatives"]) == len(tangents), f"tangent census {type_id}")
        require(stratum["tangent_transfer_exact_sparse_equality"] is True, f"tangent transfer flag {type_id}")
        require(stratum["normal_derivatives_are_not_stratum_generators"] is True, f"normal distinction {type_id}")
        for variable, item in zip(tangents, stratum["derivatives"]):
            require(item["variable"] == variable, f"stratum derivative order {type_id}")
            value = sparse_record(item["polynomial"])
            require(value == derivative(restricted, variable) == ambient_map[variable], f"restrict/differentiate identity {type_id}/{variable}")
        expected = []
        for chart in predecessor["chart_atlas"]["charts"]:
            for stratum_record in chart["boundary_strata"]:
                if tuple(stratum_record["zero_homogenizers"]) == zeros:
                    expected.append((chart["chart_index"], chart["chart_id"], tuple(chart["pivots"]), semantic(stratum_record)))
        stored = [(item["chart_index"], item["chart_id"], tuple(item["pivots"]), item["source_stratum_semantic_sha256"]) for item in record["chart_incidences"]]
        require(len(expected) == incidence_count == record["chart_incidence_count"] == len(stored), f"incidence count {type_id}")
        require(stored == expected, f"incidence records {type_id}")
        overlap = record["overlap_deduplication"]
        require(overlap["representatives_quotiented"] == 0 and overlap["overlap_unit_certificates"] == [], f"overlap nonclaim {type_id}")
        require(record["semantic_sha256"] == semantic(record), f"type semantic {type_id}")
        tangent_total += len(tangents)
        normal_total += len(zeros)
        ambient_total += 12
    require([len(restrict_zero(source, zeros)) for zeros in TYPES] == list(TERM_COUNTS), "restricted source census")
    require(sum(INCIDENCE_COUNTS) == frontier["boundary_stratum_chart_incidence_count"] == 279, "total incidences")
    require(tangent_total == 72 and normal_total == 12 and ambient_total == 84, "derivative census")
    return tangent_total, normal_total, ambient_total


def validate_deepest(frontier: dict, context: dict) -> None:
    parents = context["parents"]
    deepest = frontier["deepest_branch_frontier"]
    factorization = deepest["factorization"]
    h = mono(h=1)
    linear = add(mono(a=1, f=1), mono(-1, c=1, d=1))
    determinant = add(
        mono(a=1, e=1, i=1), mono(-1, a=1, f=1, h=1),
        mono(-1, b=1, d=1, i=1), mono(b=1, f=1, g=1),
        mono(c=1, d=1, h=1), mono(-1, c=1, e=1, g=1),
    )
    restricted = sparse_record(frontier["boundary_type_records"][0]["restricted_source"])
    require(len(restricted) == 11 and restricted == scale(multiply(multiply(h, linear), determinant), -1), "deepest factorization")
    require(sparse_record(factorization["h"]) == h, "deepest h factor")
    require(sparse_record(factorization["L"]) == linear, "deepest L factor")
    require(sparse_record(factorization["C"]) == determinant, "deepest C factor")
    require(factorization["exact_sparse_identity"] is True, "factor identity status")
    require(factorization["factor_irreducibility_asserted"] is False, "false irreducibility")
    require(factorization["scheme_multiplicity_asserted"] is False, "false scheme multiplicity")
    require(lift_parent(parents[8]) == h and parents[8]["factor_node_id"] == "H_08_1248", "parent H08 match")
    require(lift_parent(parents[22]) == scale(linear, -1) and parents[22]["factor_node_id"] == "H_22_1367", "parent H22 signed match")
    require(lift_parent(parents[34]) == determinant and parents[34]["factor_node_id"] == "H_34_1678", "parent H34 match")
    matches = factorization["parent_factor_matches"]
    require([m["parent_factor_index"] for m in matches] == [8, 22, 34], "deepest parent indices")
    require([m["parent_factor_node_id"] for m in matches] == ["H_08_1248", "H_22_1367", "H_34_1678"], "deepest parent ids")
    require(matches[1]["relationship"] == "EXACT_SPARSE_NEGATIVE_EQUALITY_PARENT_EQUALS_MINUS_L", "deepest factor sign")
    require(factorization["entire_deepest_source_excluded_from_strict_parent"] is True, "deepest parent exclusion")

    cover = deepest["stratum_singular_set_cover"]
    require(cover["seed_count"] == deepest["completed_source_factor_seed_count"] == 5, "five seed census")
    require("NO_PRIMARY_DECOMPOSITION_CLAIM" in cover["scope"], "five seed scope")
    queued = deepest["queued_seed_branches"]
    require(len(queued) == 4, "queued seed census")
    require([item["branch_id"] for item in queued] == ["B-UVW-02-h-C", "B-UVW-03-L-C", "B-UVW-04-SingL", "B-UVW-05-SingC"], "seed order")
    require([item["equations"] for item in queued] == [["h", "C"], ["a*f-c*d", "C"], ["a", "c", "d", "f"], ["ALL_NINE_2x2_MINORS_OF_MATRIX_[[a,b,c],[d,e,f],[g,h,i]]"]], "seed equations")
    # Sing(L) is contained in V(L,C), while dC/dh=-L and row expansion
    # C=a*dC/da+b*dC/db+c*dC/dc put Sing(C) in V(L,C).
    require(restrict_zero(linear, ("a", "c", "d", "f")) == {}, "SingL lies in L")
    require(restrict_zero(determinant, ("a", "c", "d", "f")) == {}, "SingL lies in C")
    require(derivative(determinant, "h") == scale(linear, -1), "SingC forces L")
    row_expansion = add(multiply(mono(a=1), derivative(determinant, "a")), multiply(mono(b=1), derivative(determinant, "b")), multiply(mono(c=1), derivative(determinant, "c")))
    require(row_expansion == determinant, "determinant row Euler identity")
    require(all(item["status"].startswith("COMPLETED_PROJECTIVE_INFINITY_AND_STRICT_PARENT_EXCLUSION") for item in queued), "seed completion statuses")

    records = frontier["boundary_type_records"][0]["ambient_singularity"]["restricted_derivatives"]
    normals = {item["variable"]: sparse_record(item["polynomial"]) for item in records if item["variable"] in ("u", "v", "w")}
    d_minus_f = add(mono(d=1), mono(-1, f=1))
    s_factor = add(mono(a=1, h=1), mono(-1, a=1, i=1), mono(-1, b=1, g=1), mono(b=1, i=1), mono(c=1, g=1), mono(-1, c=1, h=1))
    require(normals["u"] == scale(multiply(multiply(h, d_minus_f), determinant), -1), "normal u identity")
    require(normals["v"] == scale(multiply(multiply(h, linear), s_factor), -1), "normal v identity")
    processed = deepest["processed_seed"]
    transfer = processed["ambient_normal_transfer"]
    quotient = sparse_record(transfer["dF_dw_quotient_by_L"])
    remainder = sparse_record(transfer["dF_dw_remainder"])
    require(normals["w"] == add(multiply(quotient, linear), remainder), "normal w division identity")
    q_record = processed["ambient_children"][1]["Q"]
    q_poly = sparse_record(q_record)
    require(remainder == multiply(mono(e=1), q_poly), "normal w eQ remainder")
    children = processed["ambient_children"]
    require(deepest["completed_ambient_child_count"] == len(children) == 2, "two child census")
    require([child["branch_id"] for child in children] == ["B-UVW-01a-h-L-e", "B-UVW-01b-h-L-Q"], "two child order")
    require(all(child["projective_infinity_only"] is True and child["parent_factor_tests_required"] == 0 for child in children), "projective child scope")
    require(all(child["parent_exclusion"] == ["H_08_1248", "H_22_1367"] for child in children), "child parent exclusions")
    require(children[0]["dimension"] == 3 and children[0]["degree"] is None and children[0]["multiplicity"] is None, "first child invariants")
    require(children[1]["dimension"] is None and children[1]["degree"] is None and children[1]["multiplicity"] is None, "second child nonclaims")
    require(deepest["type_classification"] == "COMPLETE_PROJECTIVE_INFINITY_AND_STRICT_PARENT_EXCLUSION", "deepest classification")


def validate_uv_and_endpoint(frontier: dict, context: dict) -> None:
    parents = context["parents"]
    uv_record = frontier["boundary_type_records"][1]
    family_zeros = ("u", "v", "b", "c", "e", "f")
    require(restrict_zero(sparse_record(uv_record["restricted_source"]), family_zeros) == {}, "uv family source")
    derivatives = [sparse_record(item["polynomial"]) for item in uv_record["ambient_singularity"]["restricted_derivatives"]]
    require(len(derivatives) == 12 and all(restrict_zero(poly, family_zeros) == {} for poly in derivatives), "uv all twelve derivatives")
    uv = frontier["u_v_branch_frontier"]
    require(uv["completed_known_branch_count"] == len(uv["completed_known_branches"]) == 1, "uv known branch census")
    require(uv["component_completeness_proved"] is False, "uv false exhaustion")
    branch = uv["completed_known_branches"][0]
    require(branch["branch_id"] == "B-UV-00-linear-P3-family", "uv branch identity")
    require(branch["global_homogeneous_equations"] == list(family_zeros), "uv branch equations")
    require(branch["dimension"] == 3 and branch["degree"] == 1, "uv P3 invariants")
    require(branch["multiplicity"] is None and "NO_SCHEME_MULTIPLICITY_ASSERTION" in branch["multiplicity_nonclaim"], "uv multiplicity nonclaim")
    require(branch["standard_chart_witness"]["pivot_values"] == {"a": 1, "d": 1, "w": 1}, "uv standard chart")
    require(restrict_zero(lift_parent(parents[22]), family_zeros) == {}, "uv H22 exclusion")
    require(branch["strict_parent_exclusion"]["parent_factor_node_id"] == "H_22_1367", "uv parent tag")
    require(branch["semantic_sha256"] == semantic(branch), "uv branch semantic")

    pending = frontier["first_pending_branch"]
    require(pending["branch_id"] == PENDING and pending["type_id"] == "u_v", "pending branch identity")
    require(pending["known_branch_exhausts_ambient_ideal"] is False, "pending exhaustion")
    require(pending["ambient_equation_count"] == 12 and len(pending["ambient_equation_node_ids"]) == 12, "pending ambient equations")
    require(pending["stratum_equation_count"] == 10, "pending stratum equations")
    require(len(pending["unresolved_obligations"]) == 5, "pending obligations")
    require(pending["semantic_sha256"] == semantic(pending) == PENDING_SHA, "pending semantic hash")
    require(uv["first_pending_branch_id"] == PENDING and uv["first_pending_branch_semantic_sha256"] == PENDING_SHA, "uv pending binding")
    endpoint = frontier["endpoint_accounting"]
    require(endpoint["positive"].startswith("NOT_REACHED") and endpoint["negative"].startswith("NOT_REACHED"), "endpoint inflation")
    require(endpoint["null"].startswith("REACHED") and endpoint["timeout"].startswith("NOT_REACHED"), "null/timeout accounting")
    require(endpoint["completed_boundary_types"] == 1 and endpoint["completed_deepest_source_factor_seeds"] == 5 and endpoint["completed_u_v_known_branches"] == 1, "completed endpoint census")
    require(endpoint["first_pending_branch_id"] == PENDING and endpoint["first_pending_branch_semantic_sha256"] == PENDING_SHA, "endpoint pending binding")
    parent = frontier["parent_factor_frontier"]
    require(parent["ordered_parent_factor_count"] == 70, "retained parent count")
    require(parent["accepted_affine_branch_count"] == 0 and parent["completed_branch_parent_factor_pairs"] == 0, "false affine acceptance")
    overlap = frontier["overlap_accounting"]
    require(overlap == {"inherited_directed_overlap_records": 4032, "representatives_quotiented": 0, "explicit_overlap_unit_certificates": 0, "unsupported_deduplications": 0}, "overlap accounting")


def validate_protocol_target_only() -> None:
    opening = frozen_json(CANDIDATE, OPENING_PATH)
    protocol_path = "ops/research-team/PROTOCOL.md"
    verifier_path = "ops/research-team/verify_cycle_protocol.py"
    protocol_bytes = frozen_bytes(BASE, protocol_path)
    verifier_bytes = frozen_bytes(BASE, verifier_path)
    require(digest(protocol_bytes) == opening["pins"][protocol_path], "target protocol bytes moved")
    require(digest(verifier_bytes) == opening["pins"][verifier_path], "protocol verifier bytes moved")
    namespace: dict = {"__name__": "frozen_target_protocol_verifier", "__file__": str(ROOT / verifier_path)}
    exec(compile(verifier_bytes, verifier_path, "exec"), namespace)
    cycle_text = frozen_bytes(CANDIDATE, f"ops/research-team/cycles/{CYCLE_ID}/CYCLE.md").decode("utf-8")
    orders_text = frozen_bytes(CANDIDATE, f"ops/research-team/cycles/{CYCLE_ID}/WORK_ORDERS.yaml").decode("utf-8")
    protocol_text = protocol_bytes.decode("utf-8")
    namespace["require_phrases"](cycle_text, namespace["CYCLE_PHRASES"], CYCLE_ID)
    namespace["require_phrases"](orders_text, namespace["WORK_ORDER_PHRASES"], CYCLE_ID)
    namespace["require_phrases_collapsed"](orders_text, namespace["CURRENT_AUTHORIZATION_PHRASES"], CYCLE_ID)
    expected_auth = namespace["protocol_authorization"](protocol_text, namespace["CURRENT_AUTHORIZATION_MARKER"])
    actual_auth = namespace["work_order_authorization"](orders_text, CYCLE_ID)
    require(expected_auth == actual_auth, "target-only authorization drift")
    tracks = len(re.findall(r"^\s+- track_id:\s*\S+", orders_text, re.M))
    auth_uses = len(re.findall(r"^\s+publication_authorization:\s*\*publication_authorization\s*$", orders_text, re.M))
    require((tracks, auth_uses) == (4, 4), "target-only protocol lane census")
    namespace["hostile_canaries"]()


def validate_package(package: dict, context: dict, run_protocol: bool = False) -> None:
    require(package["candidate_revision"] == CANDIDATE and package["candidate_tree"] == CANDIDATE_TREE, "candidate object moved")
    require(package["closing_revision"] == CLOSING and package["closing_tree"] == CLOSING_TREE, "closing object moved")
    require(package["correction_revision"] == CORRECTION and package["correction_tree"] == CORRECTION_TREE, "strategy correction object moved")
    manifest = package["manifest"]
    require(manifest["candidate_revision"] == CANDIDATE and manifest["candidate_tree"] == CANDIDATE_TREE, "manifest candidate pin")
    require(manifest["accepted_endpoint"] == "FIRST_SOURCE_PINNED_UNRESOLVED_TYPE_OR_BRANCH_CLASSIFICATION", "manifest endpoint")
    require(manifest["first_pending_branch_id"] == PENDING and manifest["first_pending_branch_semantic_sha256"] == PENDING_SHA, "manifest pending")
    require(manifest["exact_boundary_frontier"] == {"trihomogeneous_source_terms": 108, "boundary_type_count": 7, "restricted_source_term_counts": list(TERM_COUNTS), "tangent_derivative_transfer_identities": 72, "restricted_normal_derivatives": 12, "full_restricted_derivatives": 84, "standard_chart_count": 64, "directed_overlap_records": 4032, "boundary_stratum_chart_incidences": 279, "parent_factor_records_retained": 70}, "manifest exact census")
    partial = manifest["partial_closures"]
    require(partial["deepest_type_completed"] is True and partial["deepest_set_theoretic_seed_count"] == 5 and partial["deepest_ambient_child_count"] == 2, "manifest deepest closure")
    require(partial["u_v_known_branch_dimension"] == 3 and partial["u_v_known_branch_degree"] == 1 and partial["u_v_known_branch_all_twelve_derivatives_zero"] is True, "manifest uv branch")
    require(partial["u_v_known_branch_excluded_by"] == "H_22_1367" and partial["u_v_known_branch_exhausts_ambient_ideal"] is False, "manifest uv scope")
    require(manifest["endpoint_accounting"] == {"positive": False, "negative": False, "null": True, "timeout": False}, "manifest endpoints")
    require(manifest["ledger_delta"] == "none" and manifest["theorem_ledger"] == "2/9" and manifest["diagonal_nine"] == "OPEN", "manifest ledger")
    require(manifest["proposed_closing_strategy_verdict"] == "RETIRE_DEFER", "corrected frozen strategy")
    require(manifest["active_route_disposition"] == "RETIRE_DEFER_FACTOR19069_BOUNDARY_DECOMPOSITION_AFTER_CYCLES_4_THROUGH_9_REMAINED_2_OF_9", "corrected route disposition")
    require(manifest["deferred_exact_resumption_record"] == SUCCESSOR and manifest["deferred_resumption_first_pending_branch"] == PENDING, "deferred exact resumption")
    require(manifest["selected_next_active_cycle"] == ACTIVE_SUCCESSOR and manifest["selected_next_active_cycle_kind"] == "FRESH_THEOREM_LEVERAGE_STRATEGY_AUDIT", "corrected active successor")
    require(manifest["proposed_sole_successor_count"] == 1, "corrected active successor count")
    require(package["referee_strategy"] == "RETIRE_DEFER_FACTOR19069_BOUNDARY_DECOMPOSITION", "corrected referee strategy")
    require(package["selected_active_successor"] == ACTIVE_SUCCESSOR and package["selected_active_successor_count"] == 1, "selected active D3 audit")
    require(package["fresh_theorem_leverage_audit_required"] is True, "fresh theorem-leverage audit")
    require(package["next_active_priority"] == "DIAGONAL_3_COVERAGE_CERTIFIED_GLOBAL_MASTER_CLOSURE_GLUING_LABELS_STRICT_CLOSURE", "diagonal-3 global priority")
    required_nonconsequences = {"NO_COMPLETE_SEVEN_TYPE_BRANCH_CLASSIFICATION", "NO_OVERLAP_DEDUPLICATION", "NO_ACCEPTED_AFFINE_SINGULAR_BRANCH", "NO_COMPLETE_70_PARENT_FACTOR_CENSUS_FOR_AN_AFFINE_BRANCH", "NO_STRICT_REAL_RESIDENCE_OR_CONNECTED_PARENT_TAG", "NO_DIAGONAL_9_PROOF_OR_COUNTEREXAMPLE", "NO_9DVL_SCORE_CHANGE"}
    require(required_nonconsequences.issubset(set(manifest["nonconsequences"])), "manifest nonconsequences")
    for path, expected in manifest["pins"].items():
        require(digest(frozen_bytes(CANDIDATE, path)) == expected, f"candidate manifest pin drift: {path}")

    frontier = package["frontier"]
    require(frontier["base_revision"] == BASE and frontier["base_tree"] == BASE_TREE, "frontier base")
    require(frontier["outcome"] == "pass" and frontier["theorem_ledger"] == "2/9" and frontier["ledger_change_recommended"] == "none", "frontier outcome/ledger")
    require(frontier["endpoint"] == "FIRST_SOURCE_PINNED_UNRESOLVED_TYPE_OR_BRANCH_CLASSIFICATION", "frontier endpoint")
    projection = deepcopy(frontier)
    stored_semantic = projection.pop("semantic_sha256")
    projection["resource_accounting"].pop("first_build_elapsed_seconds", None)
    require(digest(canonical(projection)) == stored_semantic, "frontier semantic drift")
    validate_type_records(frontier, context)
    validate_deepest(frontier, context)
    validate_uv_and_endpoint(frontier, context)
    resource = frontier["resource_accounting"]
    require(resource["exact_algebra_branch_nodes"] == 13135 <= resource["exact_algebra_branch_node_ceiling"] == 350000, "resource nodes")
    require(resource["ceiling_hit"] is False and resource["whole_atlas_groebner_retry_used"] is False, "resource/retired route")
    require(resource["numerical_or_modular_probe_used"] is False and resource["network_or_connector_used"] is False, "forbidden inference")

    constructor = package["constructor_result"]
    require(constructor["outcome"] == "pass" and constructor["theorem_ledger"] == "2/9", "constructor result")
    require(constructor["first_pending_branch_id"] == PENDING and constructor["first_pending_branch_semantic_sha256"] == PENDING_SHA, "constructor pending")
    require(constructor["accepted_affine_branch_count"] == 0 and constructor["overlap_representatives_quotiented"] == 0, "constructor downstream scope")
    certificate = package["certificate"]
    require(certificate["outcome"] == "pass" and certificate["classification"] == "ACCEPT_FROZEN_CONSTRUCTOR_EXACT_PARTIAL_FRONTIER_FAIL_CLOSED_NULL", "certificate outcome")
    require(certificate["hostile_tests"] == {"rejected": 60, "required": 24, "run": 60}, "certificate hostile census")
    require(certificate["positive_endpoint_reached"] is False and certificate["negative_endpoint_reached"] is False and certificate["null_endpoint_reached"] is True and certificate["timeout_endpoint_reached"] is False, "certificate endpoints")
    gates = certificate["certificate_gates"]
    require(gates["ambient_component_decomposition_complete"] is False and gates["branch_overlap_deduplication_performed"] is False, "certificate incomplete census")
    require(gates["affine_pullback_classifications_complete"] is False and gates["all_70_parent_factor_classifications_complete"] is False, "certificate affine/parent nonclaims")
    require(gates["strict_real_residence_complete"] is False and gates["connected_parent_tags_complete"] is False, "certificate residence nonclaims")
    require(gates["universal_diagonal_certificate"] is False, "certificate universal nonclaim")
    comparison = package["comparison"]
    scope = comparison["accepted_candidate_scope"]
    require(scope["restricted_sources_compared"] == 7 and scope["ambient_derivatives_compared"] == 84 and scope["normal_derivatives_compared"] == 12, "comparison derivative census")
    require(scope["chart_incidences_compared"] == 279 and scope["deepest_set_theoretic_seed_cover_size"] == 5 and scope["deepest_ambient_children_compared"] == 2, "comparison closure census")
    require(scope["complete_seven_type_component_classification"] is False and scope["overlap_representatives_quotiented"] == 0 and scope["accepted_affine_branch_count"] == 0, "comparison bounded scope")
    require(scope["universal_diagonal_certificate"] is False, "comparison universal nonclaim")
    delta = package["delta"]
    require(delta["outcome"] == "pass" and delta["hostile_mutations_rejected"] == 50, "falsifier delta")
    require(delta["first_pending_branch_id"] == PENDING and delta["first_pending_branch_semantic_sha256"] == PENDING_SHA, "delta pending")
    require(delta["ledger_delta"] == "none" and delta["theorem_ledger"] == "2/9", "delta ledger")
    require(delta["accepted_affine_branch_count"] == 0 and delta["overlap_representatives_quotiented"] == 0, "delta downstream scope")

    clean = package["clean"]
    require(clean["candidate_revision"] == CANDIDATE and clean["candidate_tree"] == CANDIDATE_TREE, "clean replay pin")
    require("--no-hardlinks --no-local" in clean["clone_mode"], "clean clone mode")
    results = clean["results"]
    require(results["worktree_clean"] is True and results["source_result_hardlink_count"] == results["replay_result_hardlink_count"] == 1, "clean replay link/status")
    require(results["source_and_replay_same_file_id"] is False and results["source_and_replay_result_bytes_equal"] is True, "clean replay identity")
    require(results["replay_result_sha256"] == digest(frozen_bytes(CANDIDATE, CONSTRUCTOR_RESULT_PATH)), "clean replay result bytes")
    require(clean["classification"].startswith("CLEAN_REPLAY_ACCEPTS_EXACT_SEVEN_TYPE"), "clean replay classification")
    report = package["report"]
    for phrase in (CANDIDATE, CANDIDATE_TREE, "Closing ledger: `2/9`", PENDING, PENDING_SHA, SUCCESSOR, ACTIVE_SUCCESSOR, "exactly one selected next active cycle", "No theorem-level counterexample was found", "No sampler-only"):
        require(phrase in report, f"draft report omission: {phrase}")
    require("ledger remains **`2/9`**" in report and "Ledger delta: **none**" in report, "draft ledger honesty")
    collapsed_report = " ".join(report.split())
    require("Closing strategy recommendation: **`RETIRE / DEFER`**" in collapsed_report, "corrected RETIRE/DEFER absent")
    require("cycles 4 through 9 all retained the ledger at `2/9`" in collapsed_report, "program stagnation record absent")
    require("It is not the selected next active cycle" in collapsed_report, "deferred D9 scope absent")
    if run_protocol:
        validate_protocol_target_only()


def mutate_path(package: dict, path: tuple, value) -> dict:
    item = deepcopy(package)
    target = item
    for key in path[:-1]:
        target = target[key]
    target[path[-1]] = value
    return item


def hostile_mutations(package: dict, context: dict) -> list[str]:
    cases: list[tuple[str, dict]] = []
    add_case = lambda name, path, value: cases.append((name, mutate_path(package, path, value)))
    add_case("moved-candidate-revision", ("candidate_revision",), "0" * 40)
    add_case("moved-candidate-tree", ("candidate_tree",), "0" * 40)
    add_case("moved-closing-revision", ("closing_revision",), "0" * 40)
    add_case("moved-closing-tree", ("closing_tree",), "0" * 40)
    add_case("source-term-drift", ("manifest", "exact_boundary_frontier", "trihomogeneous_source_terms"), 107)
    item = deepcopy(package); item["frontier"]["boundary_type_records"].pop(); cases.append(("type-omission", item))
    add_case("type-order-drift", ("frontier", "boundary_type_order"), ["u", "v", "w"])
    add_case("incidence-drift", ("frontier", "boundary_type_records", 3, "chart_incidence_count"), 35)
    add_case("ambient-derivative-drift", ("frontier", "boundary_type_records", 1, "ambient_singularity", "restricted_derivatives", 0, "polynomial", "sparse_polynomial", 0, "coefficient"), 99)
    add_case("normal-derivative-loss", ("frontier", "boundary_type_records", 1, "stratum_singularity", "normal_derivatives_are_not_stratum_generators"), False)
    add_case("factor-sign-drift", ("frontier", "deepest_branch_frontier", "factorization", "L", "sparse_polynomial", 0, "coefficient"), 1)
    add_case("parent-factor-sign-drift", ("frontier", "deepest_branch_frontier", "factorization", "parent_factor_matches", 1, "relationship"), "EXACT_SPARSE_EQUALITY")
    add_case("false-radicality", ("frontier", "deepest_branch_frontier", "factorization", "factor_irreducibility_asserted"), True)
    add_case("false-multiplicity", ("frontier", "deepest_branch_frontier", "factorization", "scheme_multiplicity_asserted"), True)
    item = deepcopy(package); item["frontier"]["deepest_branch_frontier"]["queued_seed_branches"].pop(); cases.append(("missing-deepest-seed", item))
    item = deepcopy(package); item["frontier"]["deepest_branch_frontier"]["processed_seed"]["ambient_children"].pop(); cases.append(("missing-ambient-child", item))
    add_case("false-uv-dimension", ("frontier", "u_v_branch_frontier", "completed_known_branches", 0, "dimension"), 2)
    add_case("false-uv-degree", ("frontier", "u_v_branch_frontier", "completed_known_branches", 0, "degree"), 2)
    add_case("false-uv-exhaustion", ("frontier", "u_v_branch_frontier", "component_completeness_proved"), True)
    add_case("residual-hash-drift", ("frontier", "first_pending_branch", "semantic_sha256"), "0" * 64)
    add_case("false-overlap-quotient", ("frontier", "overlap_accounting", "representatives_quotiented"), 1)
    add_case("false-affine-acceptance", ("frontier", "parent_factor_frontier", "accepted_affine_branch_count"), 1)
    add_case("false-70-parent-completion", ("certificate", "certificate_gates", "all_70_parent_factor_classifications_complete"), True)
    add_case("false-strict-real-tag", ("certificate", "certificate_gates", "strict_real_residence_complete"), True)
    add_case("false-connected-tag", ("certificate", "certificate_gates", "connected_parent_tags_complete"), True)
    add_case("positive-endpoint-inflation", ("manifest", "endpoint_accounting", "positive"), True)
    add_case("negative-endpoint-inflation", ("manifest", "endpoint_accounting", "negative"), True)
    add_case("null-endpoint-erasure", ("manifest", "endpoint_accounting", "null"), False)
    add_case("ledger-inflation", ("manifest", "theorem_ledger"), "3/9")
    add_case("wrong-successor-count", ("manifest", "proposed_sole_successor_count"), 2)
    add_case("wrong-successor-target", ("manifest", "selected_next_active_cycle"), "D3_WRONG_SUCCESSOR")
    add_case("revived-retired-route", ("manifest", "selected_next_active_cycle"), "D9_ROW2599_FACTOR19069_BLIND_WHOLE_ATLAS_GROEBNER_RETRY")
    add_case("clean-replay-same-file", ("clean", "results", "source_and_replay_same_file_id"), True)
    add_case("clean-replay-dirty", ("clean", "results", "worktree_clean"), False)
    first_pin = next(iter(package["manifest"]["pins"]))
    add_case("candidate-pin-drift", ("manifest", "pins", first_pin), "0" * 64)
    add_case("certificate-scope-inflation", ("comparison", "accepted_candidate_scope", "complete_seven_type_component_classification"), True)
    add_case("continued-local-route-after-ledger-stagnation", ("referee_strategy",), "CONTINUE_FACTOR19069_BOUNDARY_DECOMPOSITION")
    add_case("deferred-route-promoted-active", ("selected_active_successor",), SUCCESSOR)
    add_case("missing-fresh-theorem-leverage-audit", ("fresh_theorem_leverage_audit_required",), False)
    add_case("wrong-diagonal3-global-priority", ("next_active_priority",), "MORE_LOCAL_D9_DECOMPOSITION")
    require(tuple(name for name, _ in cases) == EXPECTED_ATTACKS, "hostile attack registry drift")
    rejected = []
    for name, candidate in cases:
        try:
            validate_package(candidate, context, run_protocol=False)
        except (Reject, KeyError, IndexError, TypeError):
            rejected.append(name)
            continue
        raise Reject(f"hostile mutation accepted: {name}")
    return rejected


def optional_replay_path_recheck(clean: dict) -> bool:
    replay = Path(clean["replay_path"])
    source_result = ROOT / CONSTRUCTOR_RESULT_PATH
    replay_result = replay / CONSTRUCTOR_RESULT_PATH
    if not replay.is_dir() or not replay_result.is_file():
        return False
    require(git("-C", str(replay), "rev-parse", "HEAD") == CANDIDATE, "external replay head")
    require(git("-C", str(replay), "rev-parse", "HEAD^{tree}") == CANDIDATE_TREE, "external replay tree")
    require(git("-C", str(replay), "status", "--porcelain=v1") == "", "external replay dirty")
    source_stat = os.stat(source_result)
    replay_stat = os.stat(replay_result)
    require(source_stat.st_nlink == replay_stat.st_nlink == 1, "external replay hardlink count")
    require(not os.path.samefile(source_result, replay_result), "external replay same file")
    require(source_result.read_bytes() == replay_result.read_bytes(), "external replay bytes")
    return True


def validate_result_files(rejected: list[str]) -> None:
    hostile = json.loads((HERE / "HOSTILE_TESTS.json").read_text(encoding="utf-8"))
    result = json.loads((HERE / "RESULT.json").read_text(encoding="utf-8"))
    require(hostile["required"] == 24 and hostile["run"] == hostile["rejected"] == len(rejected), "referee hostile count")
    require([item["name"] for item in hostile["tests"]] == rejected, "referee hostile names")
    require(all(item["status"] == "REJECTED" for item in hostile["tests"]), "referee hostile statuses")
    require(result["verdict"] == "ACCEPT_EXACT_BOUNDED_NULL_FRONTIER_WITH_CORRECTED_RETIRE_DEFER_D3_AUDIT_PIVOT", "referee verdict")
    require(result["closing_evidence_gate"] == "PASS_AFTER_FROZEN_STRATEGY_CORRECTION", "closing evidence gate")
    require(result["frozen_closing_revision"] == CLOSING and result["frozen_closing_tree"] == CLOSING_TREE, "result closing pin")
    require(result["frozen_strategy_correction_revision"] == CORRECTION and result["frozen_strategy_correction_tree"] == CORRECTION_TREE, "result correction pin")
    require(result["frozen_candidate_revision"] == CANDIDATE and result["frozen_candidate_tree"] == CANDIDATE_TREE, "result candidate pin")
    require(result["endpoint"] == "FIRST_SOURCE_PINNED_UNRESOLVED_TYPE_OR_BRANCH_CLASSIFICATION", "result endpoint")
    require(result["first_pending_branch_id"] == PENDING and result["first_pending_branch_semantic_sha256"] == PENDING_SHA, "result pending")
    require(result["ledger_delta"] == "none" and result["theorem_ledger"] == "2/9", "result ledger")
    require(result["strategy_verdict"] == "RETIRE_DEFER_FACTOR19069_BOUNDARY_DECOMPOSITION", "result strategy")
    require(result["deferred_exact_resumption_record"] == SUCCESSOR, "deferred resumption record")
    require(result["selected_active_successor"] == ACTIVE_SUCCESSOR and result["selected_active_successor_count"] == 1, "active D3 audit successor")
    require(result["next_active_cycle_gate"] == "FRESH_THEOREM_LEVERAGE_STRATEGY_AUDIT_REQUIRED", "next active gate")
    require(result["next_active_cycle_priority"] == "DIAGONAL_3_COVERAGE_CERTIFIED_GLOBAL_MASTER_CLOSURE_GLUING_LABELS_STRICT_CLOSURE", "next active priority")
    require(result["hostile_mutations_rejected"] == len(rejected), "result hostile count")


def main() -> None:
    require(git("rev-parse", f"{BASE}^{{commit}}") == BASE and git("rev-parse", f"{BASE}^{{tree}}") == BASE_TREE, "base Git object")
    require(git("rev-parse", f"{CANDIDATE}^{{commit}}") == CANDIDATE and git("rev-parse", f"{CANDIDATE}^{{tree}}") == CANDIDATE_TREE, "candidate Git object")
    require(git("rev-parse", f"{CLOSING}^{{commit}}") == CLOSING and git("rev-parse", f"{CLOSING}^{{tree}}") == CLOSING_TREE, "closing Git object")
    require(git("rev-parse", f"{CORRECTION}^{{commit}}") == CORRECTION and git("rev-parse", f"{CORRECTION}^{{tree}}") == CORRECTION_TREE, "strategy correction Git object")
    require(git("rev-parse", f"{CONSTRUCTOR_SNAPSHOT}^{{tree}}") == CONSTRUCTOR_SNAPSHOT_TREE, "constructor snapshot Git object")
    require(git("merge-base", "--is-ancestor", BASE, CANDIDATE) == "", "base/candidate ancestry")
    require(git("merge-base", "--is-ancestor", CANDIDATE, CLOSING) == "", "candidate/closing ancestry")
    require(git("merge-base", "--is-ancestor", CLOSING, CORRECTION) == "", "closing/correction ancestry")
    package = package_from_frozen_objects()
    context = reconstruct_context(package["opening"])
    validate_package(package, context, run_protocol=True)
    rejected = hostile_mutations(package, context)
    replay_path_checked = optional_replay_path_recheck(package["clean"])
    validate_result_files(rejected)
    print("PASS independent frozen closing referee")
    print(f"closing={CLOSING[:12]} tree={CLOSING_TREE[:12]} candidate={CANDIDATE[:12]} types=7 derivatives=84 incidences=279")
    print(f"deepest_seeds=5 ambient_children=2 uv_P3=dimension3_degree1 pending={PENDING_SHA[:12]}")
    print(f"hostile_mutations={len(rejected)} replay_path_rechecked={str(replay_path_checked).lower()} ledger=2/9 verdict=ACCEPT_CORRECTED_RETIRE_DEFER active_successor_count=1")


if __name__ == "__main__":
    main()
