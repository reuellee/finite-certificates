#!/usr/bin/env python3
"""Independent fail-closed replay for the roadmap representation canaries."""

from __future__ import annotations

from copy import deepcopy
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
TRACK = ROOT / "ops/team/d9-component-roadmap-certificate"
CONTRACT_PATH = TRACK / "ROADMAP_CANARY_CONTRACT.json"


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def canonical_sha256(value: object) -> str:
    encoded = json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(encoded).hexdigest()


def file_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def component_count(configuration: dict, sign: str) -> int:
    vertices = {
        vertex["id"]
        for vertex in configuration["vertices"]
        if vertex["active_sign"] == sign
    }
    adjacency = {vertex: set() for vertex in vertices}
    for edge in configuration["edges"]:
        left, right = edge["ends"]
        if left in vertices and right in vertices:
            adjacency[left].add(right)
            adjacency[right].add(left)

    unseen = set(vertices)
    components = 0
    while unseen:
        components += 1
        stack = [unseen.pop()]
        while stack:
            current = stack.pop()
            for neighbor in adjacency[current]:
                if neighbor in unseen:
                    unseen.remove(neighbor)
                    stack.append(neighbor)
    return components


def restrict_derivative_to_parameterization(
    monomials: list[dict], variable_index: int, parameterization: dict, variables: list[str]
) -> list[tuple[int, tuple[int, ...]]]:
    restricted: list[tuple[int, tuple[int, ...]]] = []
    for monomial in monomials:
        coefficient = monomial["coefficient"]
        exponents = list(monomial["exponents"])
        power = exponents[variable_index]
        if power == 0:
            continue
        coefficient *= power
        exponents[variable_index] -= 1
        vanishes = any(
            parameterization[variable] == "0" and exponents[index] > 0
            for index, variable in enumerate(variables)
        )
        if not vanishes:
            restricted.append((coefficient, tuple(exponents)))
    return restricted


def validate(contract: dict, sources: dict[str, dict]) -> None:
    require(contract["format"] == "d9-component-roadmap-canary-contract-v1", "format")
    require(
        contract["scope"] == "REPRESENTATION_CANARIES_ONLY_NO_CRITICAL_SYSTEM_ENUMERATION",
        "scope",
    )

    for relative, expected in contract["source_pins"].items():
        path = ROOT / relative
        require(path.is_file(), f"missing source {relative}")
        require(file_sha256(path) == expected, f"source drift {relative}")

    schema = contract["roadmap_schema"]
    required = set(schema["required_top_level_fields"])
    require("global_adjacency" in required, "global adjacency field")
    require("component_partition" in required, "component partition field")
    require("critical_strata" in required, "critical strata field")
    require("boundary_residence" in required, "boundary residence field")
    require("incident_branch_germs" in schema["critical_stratum_fields"], "branch germs")

    frontier = sources["frontier"]
    pair = frontier["local_memory_counterpair"]
    alias = contract["aliasing_canary"]
    require(
        canonical_sha256(pair["shared_local_observation"])
        == alias["shared_local_observation_sha256"],
        "shared local observation",
    )
    require(
        canonical_sha256(pair["cut_configuration"])
        == alias["cut_configuration_sha256"],
        "cut global adjacency",
    )
    require(
        canonical_sha256(pair["noncut_configuration"])
        == alias["noncut_configuration_sha256"],
        "noncut global adjacency",
    )
    require(
        component_count(pair["cut_configuration"], "+")
        == alias["expected_positive_components"]["TWO_POSITIVE_CYCLES"],
        "cut component count",
    )
    require(
        component_count(pair["noncut_configuration"], "+")
        == alias["expected_positive_components"]["ONE_POSITIVE_CYCLE"],
        "noncut component count",
    )
    require(alias["required_discriminator"] == "FULL_GLOBAL_ADJACENCY_DIGEST", "global adjacency discriminator")

    state = sources["state"]
    structural = state["completed_cycle"]["structural_gate"]
    projection = contract["projection_canary"]
    require(structural["first_projection_gap_type"] == projection["residual_type"], "projection type")
    require(
        structural["first_projection_gap_polynomial"] == projection["projected_polynomial"],
        "projection polynomial",
    )
    require(structural["parent_brackets_checked"] == projection["absent_parent_brackets"], "parent inventory")
    require(
        structural["global_residual_factors_checked"]
        == projection["absent_global_residual_factors"],
        "residual inventory",
    )
    require(
        structural["first_layer_new_irreducibles"]
        == projection["first_layer_new_irreducibles"],
        "projection frontier",
    )
    require(
        projection["policy"] == "ON_DEMAND_FACTOR_REGISTRY_EXTENSION_REQUIRED",
        "projection registry policy",
    )

    boundary_source = sources["boundary"]
    boundary = contract["boundary_canary"]
    require(boundary_source["active_factor"]["factor_id"] == boundary["factor_id"], "boundary factor")
    require(boundary_source["active_factor"]["polynomial"] == boundary["polynomial"], "boundary polynomial")
    require(
        boundary_source["boundary_incidence"]["recursive_parent_bracket"]
        == boundary["recursive_parent_facet"],
        "boundary facet",
    )
    require(boundary_source["parent"]["chart_count"] == boundary["boundary_charts"], "boundary charts")
    require(boundary["strict_open_parent_crossing"] is False, "strict parent residence")
    require(boundary["global_separator"] is False, "global separator")
    require(boundary["required_residence"] == "RECURSIVE_BOUNDARY_ONLY", "boundary residence")
    gate = boundary_source["strict_parent_separator_gate"]
    require(gate["witness_separates_strict_parent"] is False, "source strict-parent gate")

    singularity = contract["singularity_canary"]
    variables = singularity["variables"]
    parameterization = singularity["zero_locus_parameterization"]
    for index in range(len(variables)):
        derivative = restrict_derivative_to_parameterization(
            singularity["polynomial_monomials"], index, parameterization, variables
        )
        require(not derivative, f"gradient does not vanish along singular locus variable {index}")
    derived_dimension = sum(value == "FREE" for value in parameterization.values())
    require(
        singularity["expected_critical_locus_dimension"] == derived_dimension,
        "critical locus dimension",
    )
    require(singularity["positive_dimensional"] is True, "positive-dimensional locus")
    require(
        singularity["required_treatment"]
        == "REGISTER_AS_POSITIVE_DIMENSIONAL_CRITICAL_STRATUM",
        "singularity treatment",
    )

    scope = contract["claim_scope"]
    require(scope["critical_enumeration_authorized"] is False, "premature enumeration")
    require(scope["fixed_domain_connectivity_proved"] is False, "fixed-domain overclaim")
    require(scope["diagonal_9_proved"] is False, "diagonal-nine overclaim")
    require(scope["theorem_ledger"] == "2/9", "ledger")


def hostile_mutations(contract: dict, sources: dict[str, dict]) -> None:
    mutations: list[tuple[str, str, object]] = []

    erased_adjacency = deepcopy(contract)
    erased_adjacency["aliasing_canary"]["noncut_configuration_sha256"] = "00"
    mutations.append(("erase_global_adjacency", "noncut global adjacency", erased_adjacency))

    erased_projection = deepcopy(contract)
    erased_projection["projection_canary"]["projected_polynomial"] = "c*d-c"
    mutations.append(("erase_novel_factor", "projection polynomial", erased_projection))

    false_interior = deepcopy(contract)
    false_interior["boundary_canary"]["strict_open_parent_crossing"] = True
    mutations.append(("promote_boundary_wall", "strict parent residence", false_interior))

    collapsed_singularity = deepcopy(contract)
    collapsed_singularity["singularity_canary"]["expected_critical_locus_dimension"] = 0
    mutations.append(("collapse_singular_locus", "critical locus dimension", collapsed_singularity))

    theorem_overclaim = deepcopy(contract)
    theorem_overclaim["claim_scope"]["diagonal_9_proved"] = True
    mutations.append(("promote_fixed_domain", "diagonal-nine overclaim", theorem_overclaim))

    for name, expected, mutated in mutations:
        try:
            validate(mutated, sources)
        except ValueError as error:
            require(expected in str(error), f"{name}: wrong rejection {error}")
        else:
            raise ValueError(f"{name}: hostile mutation accepted")


def main() -> None:
    contract = json.loads(CONTRACT_PATH.read_text())
    sources = {
        "frontier": json.loads(
            (ROOT / "ops/team/d9-universal-cut-circuits/FINITE_GRAMMAR_FRONTIER.json").read_text()
        ),
        "boundary": json.loads(
            (ROOT / "ops/team/d9-universal-cut-boundary/BOUNDARY_TRANSPORT_COUNTEREXAMPLE.json").read_text()
        ),
        "state": json.loads(
            (ROOT / "ai/omreal/data/CANONICAL_RESEARCH_STATE_V4.json").read_text()
        ),
    }
    validate(contract, sources)
    hostile_mutations(contract, sources)
    print("PASS D9 component-roadmap representation canaries")
    print("aliasing=2/1 projection=c*d-c+f boundary=8552@1237 singular_dimension=1")
    print("hostile_mutations=5 critical_enumeration=DENIED_PENDING_CONSTRUCTIVE_GATE")


if __name__ == "__main__":
    main()

