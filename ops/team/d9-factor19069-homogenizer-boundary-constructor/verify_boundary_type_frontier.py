#!/usr/bin/env python3
"""Independent exact verifier for the constructor's boundary frontier."""

from __future__ import annotations

from copy import deepcopy
from hashlib import sha256
import json
from pathlib import Path
import subprocess


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
FRONTIER_PATH = HERE / "HOMOGENIZER_BOUNDARY_TYPE_FRONTIER.json"
MANIFEST_PATH = HERE / "SOURCE_MANIFEST.json"
RESULT_PATH = HERE / "RESULT.json"
PREDECESSOR_PATH = ROOT / "ops/team/d9-factor19069-explicit-trihom-jacobian-chart-constructor/PROJECTIVE_CHART_FRONTIER.json"
BASE = "0ffb0295d74e6c50a3c198b67c9821d2fe2e2760"
BASE_TREE = "d01cfbbe04f721496a91d13f85d3688262869ac0"
OPENING = "aad8e1efa5a45e47c9f924dce5263a07996a10e9"
OPENING_TREE = "8b8fcd6652a0245df9b2a7f262f4c48bb5fdc883"
ORDER = ("a", "b", "c", "u", "d", "e", "f", "v", "g", "h", "i", "w")
TYPES = (("u", "v", "w"), ("u", "v"), ("u", "w"), ("v", "w"), ("u",), ("v",), ("w",))
TERM_COUNTS = (11, 37, 23, 23, 64, 69, 47)
INCIDENCE_COUNTS = (27, 36, 36, 36, 48, 48, 48)
PRED_SHA = "815edf97a68a049f8fb6749adf948cc406ec7a258de480cf3ada3e301ca6de67"

Poly = dict[tuple[int, ...], int]


class Reject(AssertionError):
    pass


def require(condition: bool, message: str) -> None:
    if not condition:
        raise Reject(message)


def canonical(value: object) -> bytes:
    return (json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True) + "\n").encode()


def digest(data: bytes) -> str:
    return sha256(data).hexdigest()


def semantic(value: dict) -> str:
    item = deepcopy(value)
    item.pop("semantic_sha256", None)
    return digest(canonical(item))


def sparse(record: dict) -> Poly:
    require(record["coordinate_order"] == list(ORDER), "polynomial coordinate order")
    require(record["coefficient_field"] == "Q", "polynomial field")
    out: Poly = {}
    previous = None
    for term in record["sparse_polynomial"]:
        exponent = tuple(term["exponents"])
        require(len(exponent) == 12 and all(isinstance(x, int) and x >= 0 for x in exponent), "exponents")
        require(previous is None or previous < exponent, "sparse order/duplicate")
        previous = exponent
        coefficient = term["coefficient"]
        require(isinstance(coefficient, int) and coefficient != 0, "coefficient")
        out[exponent] = coefficient
    require(len(out) == record["term_count"], "term count")
    require(semantic(record) == record["semantic_sha256"], f"polynomial semantic {record['node_id']}")
    return out


def source_sparse(terms: list[dict]) -> Poly:
    out: Poly = {}
    for term in terms:
        exponent = tuple(term["exponents"])
        out[exponent] = out.get(exponent, 0) + int(term["coefficient"])
    return {m: c for m, c in out.items() if c}


def restrict(poly: Poly, zeros: tuple[str, ...]) -> Poly:
    indices = {ORDER.index(name) for name in zeros}
    return {m: c for m, c in poly.items() if all(m[index] == 0 for index in indices)}


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
    return {m: c for m, c in out.items() if c}


def add(*polys: Poly) -> Poly:
    out: Poly = {}
    for poly in polys:
        for monomial, coefficient in poly.items():
            out[monomial] = out.get(monomial, 0) + coefficient
    return {m: c for m, c in out.items() if c}


def scale(poly: Poly, coefficient: int) -> Poly:
    return {m: coefficient * c for m, c in poly.items() if coefficient * c}


def multiply(left: Poly, right: Poly) -> Poly:
    out: Poly = {}
    for lm, lc in left.items():
        for rm, rc in right.items():
            monomial = tuple(a + b for a, b in zip(lm, rm))
            out[monomial] = out.get(monomial, 0) + lc * rc
    return {m: c for m, c in out.items() if c}


def mono(coefficient: int = 1, **powers: int) -> Poly:
    exponent = tuple(powers.get(name, 0) for name in ORDER)
    return {exponent: coefficient} if coefficient else {}


def lift_parent(record: dict) -> Poly:
    affine = ("a", "b", "c", "d", "e", "f", "g", "h", "i")
    out: Poly = {}
    for term in record["sparse_polynomial"]:
        exponent = [0] * 12
        for name, power in zip(affine, term["exponents"]):
            exponent[ORDER.index(name)] = power
        out[tuple(exponent)] = term["coefficient"]
    return out


def git_bytes(revision: str, path: str) -> bytes:
    return subprocess.check_output(
        ["git", "-c", f"safe.directory={ROOT.as_posix()}", "show", f"{revision}:{path}"], cwd=ROOT
    )


def validate_manifest(manifest: dict) -> None:
    require(manifest["format"].endswith("source-manifest-v1"), "manifest format")
    require(manifest["canonical_base_revision"] == BASE, "manifest base")
    require(manifest["canonical_base_tree"] == BASE_TREE, "manifest tree")
    require(manifest["cycle_opening_revision"] == OPENING, "manifest opening")
    require(manifest["cycle_opening_tree"] == OPENING_TREE, "manifest opening tree")
    require(semantic(manifest) == manifest["semantic_sha256"], "manifest semantic")
    for path, expected in manifest["pins"].items():
        revision = OPENING if "homogenizer-boundary-type-stratification-gate1" in path else BASE
        require(digest(git_bytes(revision, path)) == expected, f"manifest pin {path}")
    policy = manifest["source_policy"]
    for key in (
        "predecessor_json_is_only_polynomial_source",
        "all_seven_boundary_types_reconstructed",
        "restrict_then_differentiate_semantics",
        "ambient_normal_derivatives_retained_separately",
    ):
        require(policy[key] is True, f"policy {key}")
    for key in (
        "whole_atlas_groebner_retry_used",
        "numerical_or_modular_probe_used",
        "network_or_connector_used",
        "unsupported_overlap_quotient_used",
    ):
        require(policy[key] is False, f"policy {key}")


def validate(frontier: dict, result: dict, predecessor: dict, source: Poly) -> None:
    require(frontier["format"].endswith("constructor-frontier-v1"), "frontier format")
    require(frontier["base_revision"] == BASE and frontier["base_tree"] == BASE_TREE, "base")
    require(frontier["opening_revision"] == OPENING and frontier["opening_tree"] == OPENING_TREE, "opening")
    require(frontier["outcome"] == "pass", "outcome")
    require(frontier["theorem_ledger"] == "2/9" and frontier["ledger_change_recommended"] == "none", "ledger")
    require(frontier["endpoint"] == "FIRST_SOURCE_PINNED_UNRESOLVED_TYPE_OR_BRANCH_CLASSIFICATION", "endpoint")
    require(frontier["classification"].startswith("DEEPEST_TYPE_EXCLUDED_BY_PINNED_PARENT_FACTORS"), "classification")
    projection = deepcopy(frontier)
    stored_semantic = projection.pop("semantic_sha256")
    projection["resource_accounting"].pop("first_build_elapsed_seconds", None)
    require(digest(canonical(projection)) == stored_semantic, "frontier semantic")
    require(frontier["source_binding"]["predecessor_frontier_sha256"] == PRED_SHA, "predecessor bind")
    require(frontier["source_binding"]["term_count"] == 108, "source count")
    require(frontier["source_binding"]["multidegree"] == [2, 2, 2], "source degree")
    require(frontier["boundary_type_count"] == 7, "type count")
    require(frontier["boundary_type_order"] == ["_".join(item) for item in TYPES], "type order")
    require(len(frontier["boundary_type_records"]) == 7, "type records")

    total_incidences = 0
    for index, (record, zeros, expected_terms, expected_incidences) in enumerate(
        zip(frontier["boundary_type_records"], TYPES, TERM_COUNTS, INCIDENCE_COUNTS)
    ):
        require(record["type_index"] == index and record["type_id"] == "_".join(zeros), "type identity")
        require(record["zero_homogenizers"] == list(zeros), "zero variables")
        reconstructed = restrict(source, zeros)
        require(len(reconstructed) == expected_terms, "reconstructed term count")
        require(sparse(record["restricted_source"]) == reconstructed, "restricted source")
        tangent = [name for name in ORDER if name not in zeros]
        ambient = record["ambient_singularity"]
        require(ambient["derivative_count"] == 12 and len(ambient["restricted_derivatives"]) == 12, "ambient derivatives")
        for name, item in zip(ORDER, ambient["restricted_derivatives"]):
            require(item["variable"] == name, "ambient variable order")
            require(sparse(item["polynomial"]) == restrict(derivative(source, name), zeros), "ambient derivative")
        stratum = record["stratum_singularity"]
        require(stratum["tangent_variables"] == tangent, "tangent order")
        require(stratum["derivative_count"] == len(tangent), "stratum derivative count")
        require(stratum["tangent_transfer_exact_sparse_equality"] is True, "tangent equality flag")
        require(stratum["normal_derivatives_are_not_stratum_generators"] is True, "normal distinction")
        for name, item in zip(tangent, stratum["derivatives"]):
            require(item["variable"] == name, "stratum variable order")
            value = sparse(item["polynomial"])
            require(value == derivative(reconstructed, name), "stratum derivative")
            require(value == restrict(derivative(source, name), zeros), "transfer")
        require(record["chart_incidence_count"] == expected_incidences, "incidence count")
        require(len(record["chart_incidences"]) == expected_incidences, "incidence records")
        actual = []
        for chart in predecessor["chart_atlas"]["charts"]:
            if any(tuple(item["zero_homogenizers"]) == zeros for item in chart["boundary_strata"]):
                actual.append((chart["chart_index"], chart["chart_id"], tuple(chart["pivots"])))
        stored = [(item["chart_index"], item["chart_id"], tuple(item["pivots"])) for item in record["chart_incidences"]]
        require(stored == actual, "incidence reconstruction")
        overlap = record["overlap_deduplication"]
        require(overlap["representatives_quotiented"] == 0, "type overlap quotient")
        require(overlap["overlap_unit_certificates"] == [], "type overlap certificates")
        require(semantic(record) == record["semantic_sha256"], "type semantic")
        total_incidences += expected_incidences
    require(total_incidences == frontier["boundary_stratum_chart_incidence_count"] == 279, "incidence total")

    deep_record = frontier["boundary_type_records"][0]
    deep = sparse(deep_record["restricted_source"])
    factors = frontier["deepest_branch_frontier"]["factorization"]
    h = sparse(factors["h"])
    linear = sparse(factors["L"])
    determinant = sparse(factors["C"])
    require(deep == scale(multiply(multiply(h, linear), determinant), -1), "deep factorization")
    require(factors["exact_sparse_identity"] is True, "factor identity flag")
    require(factors["factor_irreducibility_asserted"] is False, "irreducibility nonclaim")
    require(factors["scheme_multiplicity_asserted"] is False, "multiplicity nonclaim")
    parents = predecessor["parent_factor_incidence_frontier"]["records"]
    require(lift_parent(parents[8]) == h, "parent h equality")
    require(lift_parent(parents[22]) == scale(linear, -1), "parent L equality")
    require(lift_parent(parents[34]) == determinant, "parent C equality")
    require([item["parent_factor_node_id"] for item in factors["parent_factor_matches"]] == ["H_08_1248", "H_22_1367", "H_34_1678"], "parent match ids")
    require(factors["entire_deepest_source_excluded_from_strict_parent"] is True, "deep exclusion")
    deepest = frontier["deepest_branch_frontier"]
    require(deepest["type_classification"] == "COMPLETE_PROJECTIVE_INFINITY_AND_STRICT_PARENT_EXCLUSION", "deep classification")
    require(deepest["completed_source_factor_seed_count"] == 5, "seed count")
    require(len(deepest["queued_seed_branches"]) == 4, "other seeds")
    require(all(item["status"].startswith("COMPLETED") for item in deepest["queued_seed_branches"]), "seed completion")

    uv_frontier = frontier["u_v_branch_frontier"]
    require(uv_frontier["completed_known_branch_count"] == 1, "uv known branch count")
    require(uv_frontier["component_completeness_proved"] is False, "uv completeness nonclaim")
    uv_branch = uv_frontier["completed_known_branches"][0]
    require(uv_branch["branch_id"] == "B-UV-00-linear-P3-family", "uv branch id")
    require(uv_branch["global_homogeneous_equations"] == ["u", "v", "b", "c", "e", "f"], "uv branch equations")
    uv_zeros = ("u", "v", "b", "c", "e", "f")
    for item in frontier["boundary_type_records"][1]["ambient_singularity"]["restricted_derivatives"]:
        require(restrict(sparse(item["polynomial"]), uv_zeros) == {}, "uv family ambient membership")
    require(uv_branch["positive_dimensional"] is True and uv_branch["dimension"] == 3, "uv family dimension")
    require(uv_branch["degree"] == 1 and uv_branch["multiplicity"] is None, "uv family invariants")
    require(lift_parent(parents[22]) != {} and restrict(lift_parent(parents[22]), uv_zeros) == {}, "uv parent exclusion")
    require(uv_branch["strict_parent_exclusion"]["parent_factor_node_id"] == "H_22_1367", "uv parent id")
    require(semantic(uv_branch) == uv_branch["semantic_sha256"], "uv branch semantic")

    pending = frontier["first_pending_branch"]
    require(pending["branch_id"] == "B-UV-01-unclassified-ambient-components", "pending id")
    require(pending["type_id"] == "u_v", "pending type")
    require(pending["ambient_equation_count"] == 12 and pending["stratum_equation_count"] == 10, "pending equations")
    require(len(pending["unresolved_obligations"]) == 5, "pending obligations")
    require(pending["completed_known_branch_semantic_sha256"] == uv_branch["semantic_sha256"], "pending known branch link")
    require(pending["known_branch_exhausts_ambient_ideal"] is False, "pending exhaustion nonclaim")
    require(semantic(pending) == pending["semantic_sha256"], "pending semantic")
    endpoint = frontier["endpoint_accounting"]
    require(endpoint["completed_boundary_types"] == 1, "completed types")
    require(endpoint["completed_u_v_known_branches"] == 1, "completed uv known branches")
    require(endpoint["first_pending_branch_id"] == pending["branch_id"], "endpoint pending")
    require(endpoint["first_pending_branch_semantic_sha256"] == pending["semantic_sha256"], "endpoint pending semantic")
    require(endpoint["positive"].startswith("NOT_REACHED") and endpoint["negative"].startswith("NOT_REACHED"), "endpoint positive/negative")
    require(endpoint["null"].startswith("REACHED") and endpoint["timeout"].startswith("NOT_REACHED"), "endpoint null/timeout")
    parent = frontier["parent_factor_frontier"]
    require(parent["ordered_parent_factor_count"] == 70, "parent count")
    require(parent["accepted_affine_branch_count"] == 0, "affine branches")
    require(parent["completed_branch_parent_factor_pairs"] == 0, "parent pairs")
    overlap = frontier["overlap_accounting"]
    require(overlap == {"inherited_directed_overlap_records": 4032, "representatives_quotiented": 0, "explicit_overlap_unit_certificates": 0, "unsupported_deduplications": 0}, "overlap accounting")
    resource = frontier["resource_accounting"]
    require(0 < resource["exact_algebra_branch_nodes"] <= 350000, "node ceiling")
    require(resource["ceiling_hit"] is False, "ceiling")
    require(resource["whole_atlas_groebner_retry_used"] is False, "whole atlas")
    require(resource["numerical_or_modular_probe_used"] is False, "numerical")
    require(resource["network_or_connector_used"] is False, "network")

    require(result["format"].endswith("constructor-result-v1"), "result format")
    require(result["outcome"] == "pass" and result["theorem_ledger"] == "2/9", "result outcome")
    require(result["boundary_type_frontier_semantic_sha256"] == frontier["semantic_sha256"], "result frontier link")
    require(result["restricted_source_term_counts"] == list(TERM_COUNTS), "result terms")
    require(result["boundary_stratum_chart_incidence_count"] == 279, "result incidences")
    require(result["completed_boundary_types"] == 1, "result completed types")
    require(result["completed_u_v_known_branches"] == 1, "result uv branches")
    require(result["first_pending_branch_id"] == pending["branch_id"], "result pending")
    require(result["first_pending_branch_semantic_sha256"] == pending["semantic_sha256"], "result pending semantic")
    require(result["accepted_affine_branch_count"] == 0, "result affine")
    require(result["parent_factor_records_retained"] == 70, "result parents")
    require(result["overlap_representatives_quotiented"] == 0, "result overlaps")
    require(result["exact_algebra_branch_nodes"] == resource["exact_algebra_branch_nodes"], "result nodes")


def hostile_mutations(frontier: dict, result: dict, predecessor: dict, source: Poly) -> int:
    cases: list[tuple[dict, dict]] = []

    def fchange(path: list, value) -> None:
        f = deepcopy(frontier)
        r = deepcopy(result)
        target = f
        for key in path[:-1]:
            target = target[key]
        target[path[-1]] = value
        cases.append((f, r))

    def rchange(path: list, value) -> None:
        f = deepcopy(frontier)
        r = deepcopy(result)
        target = r
        for key in path[:-1]:
            target = target[key]
        target[path[-1]] = value
        cases.append((f, r))

    fchange(["base_revision"], "0" * 40)
    fchange(["base_tree"], "0" * 40)
    fchange(["theorem_ledger"], "3/9")
    fchange(["classification"], "COMPLETE")
    fchange(["boundary_type_count"], 6)
    fchange(["boundary_type_order"], ["u"])
    fchange(["source_binding", "term_count"], 107)
    fchange(["boundary_stratum_chart_incidence_count"], 278)
    fchange(["boundary_type_records", 0, "restricted_source", "term_count"], 12)
    fchange(["boundary_type_records", 0, "restricted_source", "sparse_polynomial", 0, "coefficient"], 99)
    fchange(["boundary_type_records", 1, "ambient_singularity", "derivative_count"], 11)
    fchange(["boundary_type_records", 1, "ambient_singularity", "restricted_derivatives", 0, "polynomial", "term_count"], 999)
    fchange(["boundary_type_records", 2, "stratum_singularity", "derivative_count"], 1)
    fchange(["boundary_type_records", 2, "stratum_singularity", "tangent_transfer_exact_sparse_equality"], False)
    fchange(["boundary_type_records", 2, "stratum_singularity", "normal_derivatives_are_not_stratum_generators"], False)
    fchange(["boundary_type_records", 3, "chart_incidence_count"], 35)
    fchange(["boundary_type_records", 4, "overlap_deduplication", "representatives_quotiented"], 1)
    fchange(["deepest_branch_frontier", "factorization", "exact_sparse_identity"], False)
    fchange(["deepest_branch_frontier", "factorization", "factor_irreducibility_asserted"], True)
    fchange(["deepest_branch_frontier", "factorization", "parent_factor_matches", 0, "parent_factor_node_id"], "fake")
    fchange(["deepest_branch_frontier", "factorization", "entire_deepest_source_excluded_from_strict_parent"], False)
    fchange(["deepest_branch_frontier", "completed_source_factor_seed_count"], 4)
    fchange(["u_v_branch_frontier", "completed_known_branch_count"], 0)
    fchange(["u_v_branch_frontier", "component_completeness_proved"], True)
    fchange(["u_v_branch_frontier", "completed_known_branches", 0, "dimension"], 2)
    fchange(["u_v_branch_frontier", "completed_known_branches", 0, "degree"], 2)
    fchange(["u_v_branch_frontier", "completed_known_branches", 0, "strict_parent_exclusion", "parent_factor_node_id"], "fake")
    fchange(["first_pending_branch", "branch_id"], "fake")
    fchange(["first_pending_branch", "ambient_equation_count"], 11)
    fchange(["first_pending_branch", "unresolved_obligations"], [])
    fchange(["endpoint_accounting", "completed_boundary_types"], 2)
    fchange(["parent_factor_frontier", "ordered_parent_factor_count"], 69)
    fchange(["parent_factor_frontier", "accepted_affine_branch_count"], 1)
    fchange(["overlap_accounting", "representatives_quotiented"], 1)
    fchange(["resource_accounting", "exact_algebra_branch_nodes"], 350001)
    fchange(["resource_accounting", "whole_atlas_groebner_retry_used"], True)
    fchange(["resource_accounting", "numerical_or_modular_probe_used"], True)
    fchange(["resource_accounting", "network_or_connector_used"], True)
    rchange(["theorem_ledger"], "3/9")
    rchange(["first_pending_branch_id"], "fake")
    rchange(["parent_factor_records_retained"], 69)
    rchange(["overlap_representatives_quotiented"], 1)

    for index, (f, r) in enumerate(cases):
        try:
            validate(f, r, predecessor, source)
        except (Reject, KeyError, IndexError, TypeError):
            continue
        raise Reject(f"hostile mutation accepted: {index}")
    return len(cases)


def main() -> None:
    manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    frontier = json.loads(FRONTIER_PATH.read_text(encoding="utf-8"))
    result = json.loads(RESULT_PATH.read_text(encoding="utf-8"))
    predecessor_raw = PREDECESSOR_PATH.read_bytes()
    require(digest(predecessor_raw) == PRED_SHA, "predecessor file pin")
    predecessor = json.loads(predecessor_raw)
    source_record = predecessor["trihomogeneous_source"]["polynomial"]
    require(source_record["coordinate_order"] == list(ORDER), "source order")
    source = source_sparse(source_record["sparse_polynomial"])
    require(len(source) == 108, "source terms")
    require(all(sum(m[0:4]) == sum(m[4:8]) == sum(m[8:12]) == 2 for m in source), "source multidegree")
    validate_manifest(manifest)
    require(result["source_manifest_semantic_sha256"] == manifest["semantic_sha256"], "result manifest link")
    validate(frontier, result, predecessor, source)
    count = hostile_mutations(frontier, result, predecessor, source)
    print("PASS independent exact homogenizer boundary constructor verification")
    print(
        f"types=7 terms={list(TERM_COUNTS)} incidences=279 deepest_parent_exclusions=3 "
        f"pending=B-UV-01-unclassified-ambient-components hostile_mutations={count} ledger=2/9"
    )


if __name__ == "__main__":
    main()
