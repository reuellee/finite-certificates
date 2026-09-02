#!/usr/bin/env python3
"""Deterministic constructor self-check for the critical-equidim frontier."""

from __future__ import annotations

from copy import deepcopy
import json

import build_critical_equidim_frontier as build


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def validate(candidate: dict, expected: dict) -> None:
    semantic = deepcopy(candidate)
    claimed = semantic.pop("semantic_sha256")
    require(build.canonical_digest(semantic) == claimed, "frontier semantic digest")
    require(candidate == expected, "source-derived frontier replay")
    require(candidate["endpoint"] == "HASH_PIN_FIRST_UNRESOLVED_SATURATED_IDEAL_BRANCH", "endpoint")
    require(candidate["theorem_ledger"] == "2/9", "ledger")
    require(candidate["ledger_change_recommended"] == "none", "ledger delta")

    circuit = candidate["factor_circuit"]
    require(len(circuit["parent_factor_nodes"]) == 70, "factor count")
    require(circuit["barrier"]["expanded_polynomial_present"] is False, "barrier expansion")
    require(circuit["barrier"]["total_degree"] == 90, "barrier degree")
    require(len(circuit["wedge_equation_nodes"]) == 36, "inherited wedge count")

    localized = candidate["localized_critical_ideal"]
    require(len(localized["inverse_relations"]) == 70, "inverse relation count")
    require(len(localized["inverse_variables"]) == 70, "inverse variable count")
    require(len(localized["log_gradient_nodes"]) == 9, "log gradient count")
    require(all(len(node["summands"]) == 70 for node in localized["log_gradient_nodes"]), "log summands")
    require(len(localized["localized_wedge_nodes"]) == 36, "localized wedge count")
    require(localized["lambda_replacement_used"] is False, "lambda overreach")
    require(localized["singular_df_zero_branch_retained"] is True, "singular loss")
    require(localized["barrier_product_expanded"] is False, "localized barrier expansion")

    frontier = candidate["equidimensional_branch_frontier"]
    require(frontier["resolved_branch_count"] == 0, "resolved branch overclaim")
    require(frontier["pending_branch_count"] == 10, "pending branch count")
    require(frontier["first_unresolved_branch_id"] == "EQ-B00-SINGULAR-DF-ZERO", "first branch")
    require(frontier["scheme_decomposition_claimed"] is False, "scheme decomposition overclaim")
    require(frontier["zero_dimensional_status"] == "NOT_PROVED", "zero-dimensional overclaim")
    singular = frontier["branches"][0]
    require(singular["generator_count"] == 80, "singular generator count")
    require(singular["complex_dimension"] is None, "singular dimension overclaim")
    require(singular["degree"] is None, "singular degree overclaim")
    require(singular["multiplicity_data"] is None, "singular multiplicity overclaim")

    boundary = candidate["true_boundary_frontier"]
    require(boundary["proper_nonexcluded_candidate_strata"] == 10, "boundary strata count")
    require(len(boundary["records"]) == 10, "boundary records")
    require(boundary["wall_component_residence_classified_strata"] == 0, "boundary overclaim")
    selector = candidate["strict_parent_component_selector"]
    require(len(selector["strict_inequalities"]) == 70, "parent inequalities")
    require(selector["complex_localization_does_not_prove_real_residence"] is True, "real residence overclaim")
    require(candidate["verified_null_frontier"]["edge39_anchor_is_barrier_critical_sample"] is False, "edge39 overclaim")
    require(candidate["resource_accounting"]["barrier_expansion_nodes"] == 0, "resource expansion")
    require(candidate["resource_accounting"]["equidimensional_decomposition_nodes_completed"] == 0, "decomposition node overclaim")


def mutation_tests(expected: dict) -> int:
    mutations = []

    def add(name, mutate):
        candidate = deepcopy(expected)
        mutate(candidate)
        mutations.append((name, candidate))

    add("endpoint", lambda c: c.__setitem__("endpoint", "PROVE_STRICT_CRITICAL_LOCUS_ZERO_DIMENSIONAL_WITH_COMPLETE_REAL_ROOT_COUNT_FRONTIER"))
    add("ledger", lambda c: c.__setitem__("theorem_ledger", "3/9"))
    add("factor loss", lambda c: c["factor_circuit"]["parent_factor_nodes"].pop())
    add("barrier expansion", lambda c: c["factor_circuit"]["barrier"].__setitem__("expanded_polynomial_present", True))
    add("barrier degree", lambda c: c["factor_circuit"]["barrier"].__setitem__("total_degree", 89))
    add("inverse loss", lambda c: c["localized_critical_ideal"]["inverse_relations"].pop())
    add("inverse variable drift", lambda c: c["localized_critical_ideal"]["inverse_variables"].__setitem__(0, "z_bad"))
    add("log summand loss", lambda c: c["localized_critical_ideal"]["log_gradient_nodes"][0]["summands"].pop())
    add("localized wedge loss", lambda c: c["localized_critical_ideal"]["localized_wedge_nodes"].pop())
    add("lambda overreach", lambda c: c["localized_critical_ideal"].__setitem__("lambda_replacement_used", True))
    add("singular branch loss", lambda c: c["equidimensional_branch_frontier"]["branches"].pop(0))
    add("first branch drift", lambda c: c["equidimensional_branch_frontier"].__setitem__("first_unresolved_branch_id", "EQ-B01-REGULAR-PIVOT-a"))
    add("dimension overclaim", lambda c: c["equidimensional_branch_frontier"]["branches"][0].__setitem__("complex_dimension", 0))
    add("degree overclaim", lambda c: c["equidimensional_branch_frontier"]["branches"][0].__setitem__("degree", 1))
    add("multiplicity overclaim", lambda c: c["equidimensional_branch_frontier"]["branches"][0].__setitem__("multiplicity_data", [1]))
    add("zero-dimensional overclaim", lambda c: c["equidimensional_branch_frontier"].__setitem__("zero_dimensional_status", "PROVED"))
    add("boundary loss", lambda c: c["true_boundary_frontier"]["records"].pop())
    add("parent sign loss", lambda c: c["strict_parent_component_selector"]["strict_inequalities"].pop())
    add("real residence overclaim", lambda c: c["strict_parent_component_selector"].__setitem__("complex_localization_does_not_prove_real_residence", False))
    add("edge39 critical overreach", lambda c: c["verified_null_frontier"].__setitem__("edge39_anchor_is_barrier_critical_sample", True))
    add("source semantic drift", lambda c: c.__setitem__("source_manifest_semantic_sha256", "0" * 64))
    add("frontier semantic drift", lambda c: c.__setitem__("semantic_sha256", "f" * 64))

    rejected = 0
    for name, candidate in mutations:
        try:
            validate(candidate, expected)
        except AssertionError:
            rejected += 1
        else:
            raise AssertionError(f"hostile mutation accepted: {name}")
    require(rejected == len(mutations) == 22, "hostile mutation census")
    return rejected


def main() -> None:
    audit = json.loads(build.OPENING_AUDIT.read_text(encoding="utf-8"))
    predecessor = json.loads(build.PREDECESSOR.read_text(encoding="utf-8"))
    manifest = build.build_source_manifest(audit)
    expected = build.build_artifact(predecessor, manifest)
    stored = json.loads(build.OUTPUT.read_text(encoding="utf-8"))
    validate(stored, expected)

    stored_manifest = json.loads(build.MANIFEST.read_text(encoding="utf-8"))
    require(stored_manifest == manifest, "source manifest replay")
    result = json.loads(build.RESULT.read_text(encoding="utf-8"))
    require(result == build.build_result(expected, manifest), "result replay")
    rejected = mutation_tests(expected)
    print(f"PASS hostile_mutations={rejected}/22")
    print(f"frontier_semantic_sha256={stored['semantic_sha256']}")
    print("first_unresolved_branch=EQ-B00-SINGULAR-DF-ZERO ledger=2/9")


if __name__ == "__main__":
    main()
