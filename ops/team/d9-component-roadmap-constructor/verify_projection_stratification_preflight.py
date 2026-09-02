#!/usr/bin/env python3
"""Independent exact replay of the D9 roadmap constructive preflight."""

from __future__ import annotations

from collections import Counter
from copy import deepcopy
import contextlib
from io import StringIO
import hashlib
import json
from math import comb, gcd
from pathlib import Path
import sys


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
OM = ROOT / "ai/omreal"
PRIOR = ROOT / "ops/team/diag9-s1237-normal-link-prover"
PREFLIGHT = HERE / "PROJECTION_STRATIFICATION_PREFLIGHT.json"
EXPECTED_BASE = "90134ab3501eb77d56bbbf126817b41f5d2e6736"
EXPECTED_TREE = "348bad06165af070fab51fa74cdc727b898c8a02"


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for block in iter(lambda: source.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def census(values) -> dict[str, int]:
    return {
        str(key): count
        for key, count in sorted(Counter(values).items())
    }


def degree(polynomial: dict) -> int:
    return max(sum(exponent) for exponent in polynomial)


def independent_inventory():
    sys.path.insert(0, str(OM))
    with contextlib.redirect_stdout(StringIO()):
        import DIAG2_PIVOT_LABELED_PAIR_ORBITS_VERIFY as labeled
        import verify_diag3_pair_global_parent_face_gate as parent_gate

    inventory = json.loads(
        (PRIOR / "ACTIVE_LITERAL_INVENTORY.json").read_text(encoding="utf-8")
    )
    factor_ids = tuple(row["factor_id"] for row in inventory["literal_rows"])
    _occurrences, _mapping, factor_polynomials = labeled.factor_polynomials()
    records = [
        json.loads(line)
        for line in (OM / "certs_4_8.jsonl").read_text(encoding="utf-8").splitlines()
        if line
    ]
    parents, parent_sign_digest = parent_gate.parent_polynomials(
        records[parent_gate.PARENT]
    )
    return inventory, factor_ids, factor_polynomials, parents, parent_sign_digest


def validate(candidate: dict) -> None:
    require(candidate["format"] == "d9-component-roadmap-projection-stratification-preflight-v1", "format")
    require(candidate["base_revision"] == EXPECTED_BASE, "base revision")
    require(candidate["base_tree"] == EXPECTED_TREE, "base tree")
    require(candidate["scope"] == "EXACT_PREFLIGHT_NO_CRITICAL_SYSTEMS_SOLVED", "scope")
    for relative, expected in candidate["source_pins"].items():
        path = ROOT / relative
        require(path.is_file(), f"missing source {relative}")
        require(sha256(path) == expected, f"source drift {relative}")

    inventory, factor_ids, factor_polynomials, parents, parent_sign_digest = independent_inventory()
    domain = candidate["fixed_domain"]
    require(domain["parent_index"] == inventory["parent_index"] == 2599, "parent")
    require(domain["family"] == inventory["family"] == "S12,37", "family")
    require(domain["active_factor_classes"] == len(factor_ids) == 3_539, "factor census")
    require(domain["active_occurrences"] == inventory["occurrence_count"] == 6_167, "occurrence census")
    require(domain["parent_brackets"] == len(parents) == 70, "parent bracket census")
    require(domain["parent_sign_digest"] == parent_sign_digest, "parent sign digest")

    factor_degrees = [degree(factor_polynomials[index]) for index in factor_ids]
    factor_terms = [len(factor_polynomials[index]) for index in factor_ids]
    parent_degrees = [degree(polynomial) for _label, _sign, polynomial, _terms in parents]
    parent_terms = [len(polynomial) for _label, _sign, polynomial, _terms in parents]
    polynomials = candidate["polynomial_inventory"]
    require(polynomials["variables"] == list("abcdefghi"), "variables")
    require(polynomials["active_factor_degree_census"] == census(factor_degrees), "factor degree census")
    require(polynomials["active_factor_term_count_census"] == census(factor_terms), "factor term census")
    require(polynomials["active_factor_max_degree"] == max(factor_degrees), "factor max degree")
    require(polynomials["active_factor_max_terms"] == max(factor_terms), "factor max terms")
    require(polynomials["parent_degree_census"] == census(parent_degrees), "parent degree census")
    require(polynomials["parent_term_count_census"] == census(parent_terms), "parent term census")
    require(polynomials["factored_boundary_barrier_factors"] == 70, "barrier factors")
    require(polynomials["factored_boundary_barrier_total_degree"] == sum(parent_degrees), "barrier degree")
    require(polynomials["expanded_boundary_barrier_required"] is False, "expanded barrier")

    projection = candidate["projection"]
    vector = tuple(projection["primitive_integer_vector"])
    require(vector == tuple(1 << index for index in range(9)), "projection vector")
    require(gcd(*vector) == 1, "projection primitive")
    require(projection["equations_per_one_wall_system"] == 9, "one-wall equations")
    require(projection["genericity_discriminant_certificate"] == "ABSENT", "genericity status")
    require(projection["specialization_authorized"] is False, "projection specialization")

    frontier = candidate["stratification_frontier"]
    pair_count = comb(3_539, 2)
    require(frontier["one_wall_systems"] == 3_539, "one-wall system count")
    require(frontier["naive_pair_strata"] == pair_count == 6_260_491, "pair-stratum count")
    require(frontier["naive_one_and_two_wall_systems"] == pair_count + 3_539 == 6_264_030, "combined frontier")
    require(frontier["opening_system_ceiling"] == 100_000, "system ceiling")
    require(frontier["naive_frontier_exceeds_ceiling"] is True, "ceiling comparison")
    require(frontier["known_memoryless_local_candidates"] == 2_420, "local candidates")
    require(frontier["known_local_candidates_complete_for_global_multiwalls"] is False, "local completeness overclaim")
    require(frontier["required_filter"] == "SOURCE_DERIVED_COMPLETE_ACTIVE_MULTIWALL_INCIDENCE", "required filter")
    require(frontier["positive_dimensional_singular_strata_must_be_registered"] is True, "singular strata")

    require(candidate["endpoint"] == "STRATIFIED_SYSTEM_FRONTIER_EXCEEDS_GATE_WITHOUT_COMPLETE_INCIDENCE_FILTER", "endpoint")
    require(candidate["classification"] == "EXACT_FAIL_CLOSED_PREFLIGHT_NULL", "classification")
    require(candidate["critical_systems_solved"] == 0, "critical systems solved")
    require(candidate["critical_enumeration_authorized"] is False, "enumeration authorization")
    require(candidate["theorem_ledger"] == "2/9", "ledger")


def hostile_mutations(stored: dict) -> None:
    mutations = []
    candidate = deepcopy(stored); candidate["stratification_frontier"]["naive_pair_strata"] = 2_420; mutations.append((candidate, "pair-stratum count"))
    candidate = deepcopy(stored); candidate["stratification_frontier"]["known_local_candidates_complete_for_global_multiwalls"] = True; mutations.append((candidate, "local completeness overclaim"))
    candidate = deepcopy(stored); candidate["projection"]["genericity_discriminant_certificate"] = "PROVED"; mutations.append((candidate, "genericity status"))
    candidate = deepcopy(stored); candidate["critical_enumeration_authorized"] = True; mutations.append((candidate, "enumeration authorization"))
    candidate = deepcopy(stored); candidate["polynomial_inventory"]["factored_boundary_barrier_factors"] = 69; mutations.append((candidate, "barrier factors"))
    candidate = deepcopy(stored); candidate["theorem_ledger"] = "3/9"; mutations.append((candidate, "ledger"))

    rejected = 0
    for candidate, expected in mutations:
        try:
            validate(candidate)
        except ValueError as error:
            require(expected in str(error), f"wrong hostile rejection: {error}")
            rejected += 1
            continue
        raise ValueError(f"hostile mutation accepted: {expected}")
    require(rejected == 6, "hostile rejection census")


def main() -> None:
    stored = json.loads(PREFLIGHT.read_text(encoding="utf-8"))
    print("independently rebuilding polynomial inventories", flush=True)
    validate(stored)
    hostile_mutations(stored)
    frontier = stored["stratification_frontier"]
    print("PASS D9 roadmap projection/stratification preflight")
    print(
        "frontier",
        frontier["one_wall_systems"],
        frontier["naive_pair_strata"],
        frontier["opening_system_ceiling"],
    )
    print("hostile_mutations=6 critical_enumeration=DENIED ledger=2/9")


if __name__ == "__main__":
    main()
