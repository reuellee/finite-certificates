#!/usr/bin/env python3
"""Fail-closed opening audit for the homogenizer boundary-type gate."""

from __future__ import annotations

from copy import deepcopy
from hashlib import sha256
import json
from pathlib import Path
import subprocess

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
AUDIT = HERE / "OPENING_AUDIT.json"
BASE = "0ffb0295d74e6c50a3c198b67c9821d2fe2e2760"
BASE_TREE = "d01cfbbe04f721496a91d13f85d3688262869ac0"
OPENING = "ff71f37eaafef17d57edda374508f7a8c7d38207"
OPENING_TREE = "4cb7c001243f3e1eb14d0a5867330c198c5dd381"
BRANCH = "research/local-d9-factor19069-homogenizer-boundary-type-stratification-gate1-20260901"
TARGET = "D9_ROW2599_FACTOR19069_HOMOGENIZER_BOUNDARY_TYPE_STRATIFICATION_GATE1"
CYCLE_ID = "2026-09-01-d9-row2599-factor19069-homogenizer-boundary-type-stratification-gate1"
FRONTIER = ROOT / "ops" / "team" / "d9-factor19069-explicit-trihom-jacobian-chart-constructor" / "PROJECTIVE_CHART_FRONTIER.json"
OPENING_DOCS = {
    "CYCLE.md": "17eabb966da4b6dc6468616fd4b90dea3dfe41672a881fe05e97f99e835e6809",
    "WORK_ORDERS.yaml": "1c894fbf181416e84c0ec0397c6a04f45400721871a9c40ad210dce8f2424230",
    "OBLIGATION_GRAPH.json": "f85c957eef37a3e991119057f28685f5d5e2208271da053b9e0294e03b530e35",
    "OPENING_AUDIT.json": "a430effec7a0defb5646be8d823c39e31aaf09227261e4d3fe816baba3903821",
}


class Reject(AssertionError):
    pass


def require(condition: bool, message: str) -> None:
    if not condition:
        raise Reject(message)


def git(*arguments: str, binary: bool = False):
    value = subprocess.check_output(
        ["git", "-c", f"safe.directory={ROOT.as_posix()}", *arguments],
        cwd=ROOT,
        text=not binary,
    )
    return value if binary else value.strip()


def digest(data: bytes) -> str:
    return sha256(data).hexdigest()


def frozen_bytes(revision: str, path: str) -> bytes:
    return git("show", f"{revision}:{path}", binary=True)


def validate(candidate: dict) -> None:
    require(candidate["format"] == "d9-factor19069-homogenizer-boundary-type-opening-audit-v1", "format")
    require(candidate["cycle_id"] == CYCLE_ID, "cycle")
    require(candidate["base_revision"] == BASE, "base revision")
    require(candidate["base_tree"] == BASE_TREE, "base tree")
    require(candidate["successor_branch"] == BRANCH, "branch")
    require(candidate["opening_ledger"] == "2/9", "ledger")
    require(candidate["predecessor_verdict"] == "ACCEPT_FAIL_CLOSED_TIMEOUT_FRONTIER_PIVOT", "predecessor")
    require(candidate["selected_target"] == TARGET, "target")
    require(candidate["selected_count"] == 1, "selected count")
    require(candidate["concurrent_authoritative_cycles"] == [], "concurrent cycles")
    require(candidate["inherited_protocol_debt"]["current_protocol_pinned_and_selected_cycle_audited"] is True, "protocol debt")

    target = candidate["target"]
    require(target["parent_index"] == 2599 and target["factor_id"] == 19069, "row/factor")
    require(target["homogeneous_ring"] == "Q[a,b,c,u,d,e,f,v,g,h,i,w]", "ring")
    require(target["multidegree"] == [2, 2, 2], "multidegree")
    require(target["verified_wall_term_count"] == 108, "source terms")
    require(target["standard_chart_count"] == 64, "charts")
    require(target["directed_overlap_records"] == 4032, "overlaps")
    require(target["boundary_stratum_chart_incidences"] == 279, "boundary incidences")
    require(target["boundary_type_count"] == 7, "boundary type count")
    require(target["processing_order"] == ["u_v_w", "u_v", "u_w", "v_w", "u", "v", "w"], "processing order")
    require(target["deepest_restriction_term_count"] == 11, "deepest term count")
    require(target["parent_sign_factors"] == 70, "parent factors")
    for key in (
        "requires_restrict_then_differentiate_semantics",
        "requires_ambient_and_stratum_singularity_distinction",
        "requires_complete_factor_branch_propagation",
        "requires_no_unsupported_radicality_or_multiplicity",
        "requires_explicit_overlap_units_for_deduplication",
        "requires_affine_pullback_before_parent_tests",
        "requires_all_70_parent_factor_tests",
        "requires_strict_real_residence",
        "requires_connected_parent_component_tags",
    ):
        require(target[key] is True, key)
    require(target["positive_endpoint"].startswith("COMPLETE_EXACT_SEVEN_TYPE"), "positive")
    require(target["negative_endpoint"].startswith("EXACT_STRICT_REAL_AFFINE"), "negative")
    require(target["null_endpoint"].startswith("FIRST_SOURCE_PINNED"), "null")
    require(target["timeout_endpoint"].startswith("HASH_PIN_ALL_COMPLETED"), "timeout")

    ceiling = candidate["resource_ceiling"]
    require(ceiling["wall_minutes"] == 120, "wall ceiling")
    require(ceiling["aggregate_cpu_hours"] == 8, "cpu ceiling")
    require(ceiling["max_exact_algebra_branch_nodes"] == 500000, "node ceiling")
    require(ceiling["paid_external_compute"] is False, "paid compute")
    require(len(candidate["prohibited_routes"]) == 11, "prohibited census")
    require("BLIND_WHOLE_ATLAS_GROEBNER_RETRY" in candidate["prohibited_routes"], "whole atlas route")
    require("NUMERICAL_OR_MODULAR_PROMOTION" in candidate["prohibited_routes"], "probe route")
    durable = candidate["durable_checkpoint"]
    require(durable["project_root"] == r"E:\Projects\9DVL Research", "project root")
    require(durable["local_output_root"] == r"E:\Projects\9DVL Research\outputs", "output root")
    require(durable["drive_connector_used"] is False, "connector")
    require(durable["drive_mirror_optional"] is True, "optional mirror")
    require(durable["github_write"] is False, "GitHub write")


def reconstruct_source() -> tuple[dict, dict[tuple[int, ...], int]]:
    predecessor = json.loads(FRONTIER.read_text(encoding="utf-8"))
    require(predecessor["outcome"] == "pass", "predecessor outcome")
    require(predecessor["theorem_ledger"] == "2/9", "predecessor ledger")
    require(predecessor["endpoint"] == "HASH_PIN_ALL_COMPLETED_CHART_BRANCHES_AND_FIRST_PENDING_BRANCH", "predecessor endpoint")
    tri = predecessor["trihomogeneous_source"]
    require(tri["term_count"] == 108, "trihom terms")
    require(tri["multidegree"] == [2, 2, 2], "trihom degree")
    require(tri["dehomogenization_exact_sparse_equality"] is True, "dehomogenization")
    require(tri["affine_source_is_homogeneous"] is False, "false homogeneity retained")
    require(tri["affine_source_is_multiaffine"] is False, "false multiaffinity retained")
    require(tri["trihomogenization_is_decomposition_certificate"] is False, "not decomposition")
    polynomial = tri["polynomial"]
    order = polynomial["coordinate_order"]
    require(order == ["a", "b", "c", "u", "d", "e", "f", "v", "g", "h", "i", "w"], "coordinate order")
    require(polynomial["term_count"] == len(polynomial["sparse_polynomial"]) == 108, "sparse source")
    expression: dict[tuple[int, ...], int] = {}
    for term in polynomial["sparse_polynomial"]:
        exponents = tuple(term["exponents"])
        require(sum(exponents[0:4]) == 2, "first block degree")
        require(sum(exponents[4:8]) == 2, "second block degree")
        require(sum(exponents[8:12]) == 2, "third block degree")
        expression[exponents] = expression.get(exponents, 0) + int(term["coefficient"])
    expression = {monomial: coefficient for monomial, coefficient in expression.items() if coefficient}
    require(len(expression) == 108, "source terms after collection")

    atlas = predecessor["chart_atlas"]
    require(atlas["standard_chart_count"] == len(atlas["charts"]) == 64, "chart census")
    require(atlas["directed_overlap_record_count"] == 4032, "overlap census")
    require(atlas["boundary_stratum_record_count"] == 279, "stratum census")
    require(atlas["global_nonempty_boundary_type_count"] == 7, "type census")
    require(atlas["all_product_charts_retained"] is True, "chart retention")
    require(atlas["all_available_boundary_strata_retained"] is True, "stratum retention")
    require(atlas["symmetry_quotient_used"] is False, "no symmetry quotient")
    return predecessor, expression


def multiply(left: dict[tuple[int, ...], int], right: dict[tuple[int, ...], int]) -> dict[tuple[int, ...], int]:
    result: dict[tuple[int, ...], int] = {}
    for left_monomial, left_coefficient in left.items():
        for right_monomial, right_coefficient in right.items():
            monomial = tuple(a + b for a, b in zip(left_monomial, right_monomial))
            result[monomial] = result.get(monomial, 0) + left_coefficient * right_coefficient
    return {monomial: coefficient for monomial, coefficient in result.items() if coefficient}


def monomial(**powers: int) -> tuple[int, ...]:
    order = "abcdefghi"
    return tuple(powers.get(name, 0) for name in order)


def validate_deepest(expression: dict[tuple[int, ...], int], candidate: dict) -> None:
    retained = [0, 1, 2, 4, 5, 6, 8, 9, 10]
    deepest = {
        tuple(exponents[index] for index in retained): coefficient
        for exponents, coefficient in expression.items()
        if exponents[3] == exponents[7] == exponents[11] == 0
    }
    require(len(deepest) == 11, "deepest restriction terms")
    minus_h = {monomial(h=1): -1}
    linear_minor = {monomial(a=1, f=1): 1, monomial(c=1, d=1): -1}
    cubic = {
        monomial(a=1, e=1, i=1): 1,
        monomial(a=1, f=1, h=1): -1,
        monomial(b=1, d=1, i=1): -1,
        monomial(b=1, f=1, g=1): 1,
        monomial(c=1, d=1, h=1): 1,
        monomial(c=1, e=1, g=1): -1,
    }
    expected = multiply(multiply(minus_h, linear_minor), cubic)
    require(deepest == expected, "deepest factorization")
    require(candidate["target"]["deepest_restriction_factorization"] == "-h*(a*f-c*d)*(a*e*i-a*f*h-b*d*i+b*f*g+c*d*h-c*e*g)", "factorization spelling")


def validate_pins(candidate: dict) -> None:
    for path, expected in candidate["pins"].items():
        require(digest(frozen_bytes(BASE, path)) == expected, f"pin drift: {path}")
    prefix = f"ops/research-team/cycles/{CYCLE_ID}/"
    for name, expected in OPENING_DOCS.items():
        require(digest(frozen_bytes(OPENING, prefix + name)) == expected, f"opening document drift: {name}")


def validate_selected_protocol() -> None:
    cycle = (HERE / "CYCLE.md").read_text(encoding="utf-8")
    orders = (HERE / "WORK_ORDERS.yaml").read_text(encoding="utf-8")
    for phrase in (
        "## Mandatory opening strategy evaluation",
        "## Bounded target",
        "## Obligation graph",
        "## Resource ceiling",
        "## Publication authority",
        "## Closing requirements",
        "Positive:",
        "Negative:",
        "Null:",
        "Timeout:",
    ):
        require(phrase in cycle, f"cycle protocol phrase: {phrase}")
    require(orders.count("track_id:") == 4, "work-order count")
    require(orders.count("publication_authorization: *publication_authorization") == 4, "authorization reuse")
    require("GitHub is read-only" in orders and "Google Drive connector" in orders, "operational authority")


def hostile_mutations(stored: dict) -> int:
    mutations = []

    def changed(path, value):
        item = deepcopy(stored)
        target = item
        for key in path[:-1]:
            target = target[key]
        target[path[-1]] = value
        mutations.append(item)

    changed(["base_revision"], "0" * 40)
    changed(["base_tree"], "0" * 40)
    changed(["opening_ledger"], "3/9")
    changed(["selected_count"], 2)
    changed(["concurrent_authoritative_cycles"], ["fake"])
    changed(["target", "factor_id"], 19068)
    changed(["target", "verified_wall_term_count"], 107)
    changed(["target", "standard_chart_count"], 63)
    changed(["target", "directed_overlap_records"], 4031)
    changed(["target", "boundary_stratum_chart_incidences"], 278)
    changed(["target", "boundary_type_count"], 6)
    changed(["target", "processing_order"], ["u", "v", "w"])
    changed(["target", "deepest_restriction_term_count"], 12)
    changed(["target", "parent_sign_factors"], 69)
    changed(["target", "requires_restrict_then_differentiate_semantics"], False)
    changed(["target", "requires_ambient_and_stratum_singularity_distinction"], False)
    changed(["target", "requires_complete_factor_branch_propagation"], False)
    changed(["target", "requires_no_unsupported_radicality_or_multiplicity"], False)
    changed(["target", "requires_explicit_overlap_units_for_deduplication"], False)
    changed(["target", "requires_affine_pullback_before_parent_tests"], False)
    changed(["target", "requires_all_70_parent_factor_tests"], False)
    changed(["resource_ceiling", "max_exact_algebra_branch_nodes"], 500001)
    changed(["durable_checkpoint", "drive_connector_used"], True)
    changed(["durable_checkpoint", "github_write"], True)
    altered = deepcopy(stored)
    altered["prohibited_routes"].remove("BLIND_WHOLE_ATLAS_GROEBNER_RETRY")
    mutations.append(altered)
    altered = deepcopy(stored)
    altered["pins"]["ops/research-team/PROTOCOL.md"] = "0" * 64
    mutations.append(altered)
    for index, mutation in enumerate(mutations):
        try:
            validate(mutation)
            validate_pins(mutation)
        except (Reject, KeyError):
            continue
        raise Reject(f"hostile mutation accepted: {index}")
    return len(mutations)


def main() -> None:
    stored = json.loads(AUDIT.read_text(encoding="utf-8"))
    require(git("rev-parse", f"{BASE}^{{commit}}") == BASE, "base commit")
    require(git("rev-parse", f"{BASE}^{{tree}}") == BASE_TREE, "base tree")
    require(git("rev-parse", f"{OPENING}^{{commit}}") == OPENING, "opening commit")
    require(git("rev-parse", f"{OPENING}^{{tree}}") == OPENING_TREE, "opening tree")
    require(git("branch", "--show-current") == BRANCH, "current branch")
    validate(stored)
    _, expression = reconstruct_source()
    validate_deepest(expression, stored)
    validate_pins(stored)
    validate_selected_protocol()
    count = hostile_mutations(stored)
    print("PASS homogenizer boundary-type gate-1 opening audit")
    print(f"base={BASE[:8]} tree={BASE_TREE[:8]} opening={OPENING[:8]} types=7 incidences=279 source_terms=108 parents=70")
    print(f"opening_hostile_mutations={count} deepest_terms=11 ledger=2/9 drive_connector=false github_write=false")


if __name__ == "__main__":
    main()
