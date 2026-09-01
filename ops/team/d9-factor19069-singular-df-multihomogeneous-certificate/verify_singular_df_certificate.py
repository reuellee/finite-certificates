#!/usr/bin/env python3
"""Independent exact verifier for factor 19069's singular-df gate.

The verifier treats the constructor payload as untrusted data and imports no
constructor, falsifier, or predecessor-certificate code.  It reconstructs the
108-term polynomial and all nine derivatives from the frozen predecessor
artifact.  In particular, it checks the *sets* of affine block degrees and
the per-variable degree bounds instead of confusing maximum block degrees
with homogeneity or maximum variable degrees with multiaffinity.

The candidate-specific checks deliberately fail closed.  A source-premise
rejection is certifiable as a null handoff; strict-parent emptiness, a complete
characteristic-zero decomposition, real residence, or a connected-component
tag are not certifiable unless every corresponding exact witness is present.
"""

from __future__ import annotations

import argparse
import ast
from copy import deepcopy
from hashlib import sha256
import json
from math import gcd
from pathlib import Path
import sys
from collections import Counter


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
CYCLE_ID = "2026-09-01-d9-row2599-factor19069-singular-df-multihomogeneous-gate1"
TRACK_ID = "d9-factor19069-singular-df-multihomogeneous-constructor"
CERT_TRACK_ID = "d9-factor19069-singular-df-multihomogeneous-certificate"
TARGET = "D9_ROW2599_FACTOR19069_SINGULAR_DF_MULTIHOMOGENEOUS_DECOMPOSITION_GATE1"
VARIABLES = tuple("abcdefghi")
BLOCKS = ((0, 1, 2), (3, 4, 5), (6, 7, 8))
OPENING_LEDGER = "2/9"
LEDGER_DELTA = "0/9"
POSITIVE = "PROVE_SINGULAR_BRANCH_EMPTY_ON_STRICT_CONNECTED_ROW2599_PARENT_COMPONENT"
NEGATIVE = "EXHIBIT_EXACT_POSITIVE_DIMENSIONAL_REAL_SINGULAR_COMPONENT_ON_STRICT_CONNECTED_ROW2599_PARENT_COMPONENT"
NULL = "HASH_PIN_FIRST_UNRESOLVED_MULTIHOMOGENEOUS_SINGULAR_COMPONENT_OR_PARENT_SATURATION_BRANCH"
TIMEOUT = "HASH_PIN_COMPLETED_AND_PENDING_MULTIHOMOGENEOUS_SINGULAR_DECOMPOSITION_FRONTIER"

CYCLE = ROOT / "ops" / "research-team" / "cycles" / CYCLE_ID
OPENING = CYCLE / "OPENING_AUDIT.json"
PREDECESSOR = ROOT / "ops" / "team" / "d9-factor19069-critical-equidim-constructor" / "CRITICAL_EQUIDIM_FRONTIER.json"
CONSTRUCTOR = ROOT / "ops" / "team" / TRACK_ID
FRONTIER_CANDIDATES = (
    CONSTRUCTOR / "SINGULAR_DF_MULTIHOMOGENEOUS_FRONTIER.json",
    CONSTRUCTOR / "SINGULAR_DF_FRONTIER.json",
)
SOURCE_ARTIFACT = HERE / "SOURCE_RECONSTRUCTION.json"
SOURCE_MANIFEST = HERE / "SOURCE_MANIFEST.json"
HOSTILE_ARTIFACT = HERE / "HOSTILE_TESTS.json"
RESULT = HERE / "RESULT.json"
FINDINGS = HERE / "FINDINGS.md"

PINNED_INPUTS = {
    f"ops/research-team/cycles/{CYCLE_ID}/OPENING_AUDIT.json": "d6fc28140be34ef7c77527ae3ef001ded849f269ffa0d92c541a4899262b4c3d",
    f"ops/research-team/cycles/{CYCLE_ID}/CYCLE.md": "9c8a51c141c8ab4742d580e50508f8cc544c6d6f211fe4b785b675f9c74f8055",
    f"ops/research-team/cycles/{CYCLE_ID}/OBLIGATION_GRAPH.json": "6a01553079cb350f6a681bc5d19c8a584d3153eb106f49ff943ed4f1e99e709b",
    f"ops/research-team/cycles/{CYCLE_ID}/WORK_ORDERS.yaml": "921046f85cfe3bb83b9ac79a449e11a04d75074c1aa617e5118cb94e854243d5",
    "ops/research-team/PROTOCOL.md": "54f1a15b7774085005707727780b266ffbd4a8edc4687fe14e1e6bc76d229031",
    "ops/research-team/verify_cycle_protocol.py": "4d9e16daed0de08af415e95c746803b512ea8b92c452df6df2c9e09fdcd3b7d1",
    "ops/team/d9-factor19069-critical-equidim-constructor/CRITICAL_EQUIDIM_FRONTIER.json": "4d7f4f21d0a5ab59ae42fa265d5a3cf851fa74dd1ff7069cd19209ec897d3a33",
    "ops/team/d9-factor19069-critical-equidim-constructor/SOURCE_MANIFEST.json": "06efc5d65274d7179728b9b89a1788ea4d33812bfb24ecd5235bdd0d294bd75b",
    "ai/omreal/data/DIAG3_PAIR_GLOBAL_row2599_candidate_factors.bin": "adb2e7257457f158e809450683c46fe7ecafdbdd4a7efdf9ac630e8a4f0fb03f",
}

EXPECTED_FACTOR_DIGEST = "b997e1dcc7216f595610633de99dd3459658cef28676fa748d79c2ba4ac0f3dc"
EXPECTED_DERIVATIVES = {
    "a": (54, "b1048204971754cfd4f001abf68ad2488d6037b3334777a8763bb022b3fabb00"),
    "b": (44, "4c9db67ab330fe23417dcd64e57b7e792c64020f87176e1807464f365a5280ad"),
    "c": (54, "b05fa546338d4481eaadd570669f9516419b59298cbc29c71757c36ba0175cf5"),
    "d": (50, "c6fa25aa86cbd43ab9e47d67361393dd7c3d7486b8665150e69a3ccbf3ba9ee4"),
    "e": (50, "43b217a3004285953c015bcd3b0f9bf73108d012bdb8e4124bbde07ed92f62d5"),
    "f": (50, "4237f35ca439ad8edeb331a4a8f55c80cd18aba032dc749b3fd2bc2fd1c5042f"),
    "g": (36, "569b2483ca9f359b0b3bedc8eed1519c06f9249ed20baa49f11284753e0ef20f"),
    "h": (61, "f7eacc121b4fa89f518e33a04a5fef79c0c1e9e968de436c5a5fe87640b1676b"),
    "i": (36, "7201162b7637d313aa6a9463cdbb2eec37f4cd8fda2d2bc0b83a108aede03f72"),
}


class Reject(AssertionError):
    """A certificate gate rejected untrusted data."""


def require(condition: bool, marker: str) -> None:
    if not condition:
        raise Reject(marker)


def canonical_bytes(value) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("ascii")


def canonical_digest(value) -> str:
    return sha256(canonical_bytes(value)).hexdigest()


def semantic_digest(value: dict) -> str:
    unsealed = deepcopy(value)
    unsealed.pop("semantic_sha256", None)
    return canonical_digest(unsealed)


def file_digest(path: Path) -> str:
    return sha256(path.read_bytes()).hexdigest()


def read_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, value) -> None:
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def normalize_sparse(records: list[dict]) -> list[dict]:
    combined: dict[tuple[int, ...], int] = {}
    for record in records:
        require(set(record) == {"exponents", "coefficient"}, "sparse record schema")
        exponent = tuple(record["exponents"])
        coefficient = record["coefficient"]
        require(len(exponent) == 9, "sparse exponent arity")
        require(all(type(value) is int and value >= 0 for value in exponent), "sparse exponent domain")
        require(type(coefficient) is int, "sparse coefficient domain")
        combined[exponent] = combined.get(exponent, 0) + coefficient
    return [
        {"exponents": list(exponent), "coefficient": coefficient}
        for exponent, coefficient in sorted(combined.items())
        if coefficient
    ]


def derivative(records: list[dict], coordinate: int) -> list[dict]:
    differentiated = []
    for record in records:
        exponent = list(record["exponents"])
        power = exponent[coordinate]
        if power:
            exponent[coordinate] -= 1
            differentiated.append(
                {"exponents": exponent, "coefficient": record["coefficient"] * power}
            )
    return normalize_sparse(differentiated)


def exact_profile(records: list[dict]) -> dict:
    coefficients = [abs(record["coefficient"]) for record in records]
    content = 0
    for coefficient in coefficients:
        content = gcd(content, coefficient)
    block_vectors = Counter(
        tuple(sum(record["exponents"][index] for index in block) for block in BLOCKS)
        for record in records
    )
    total_degrees = Counter(sum(record["exponents"]) for record in records)
    return {
        "term_count": len(records),
        "coefficient_content": content,
        "total_degree_support": sorted({sum(record["exponents"]) for record in records}),
        "block_total_degree_support": [
            sorted({sum(record["exponents"][index] for index in block) for record in records})
            for block in BLOCKS
        ],
        "variable_degree_maxima": [
            max(record["exponents"][index] for record in records) for index in range(9)
        ],
        "per_variable_exponent_sets": {
            variable: sorted({record["exponents"][index] for record in records})
            for index, variable in enumerate(VARIABLES)
        },
        "block_degree_vector_distribution": [
            {"degree": list(degree), "term_count": count}
            for degree, count in sorted(block_vectors.items())
        ],
        "total_degree_distribution": [
            {"degree": degree, "term_count": count}
            for degree, count in sorted(total_degrees.items())
        ],
        "terms_not_of_block_degree_2_2_2": sum(degree != (2, 2, 2) for degree in block_vectors.elements()),
        "terms_with_at_least_one_squared_variable": sum(
            any(exponent >= 2 for exponent in record["exponents"]) for record in records
        ),
    }


def source_reconstruction() -> dict:
    for relative, expected in PINNED_INPUTS.items():
        require(file_digest(ROOT / relative) == expected, f"source pin {relative}")

    opening = read_json(OPENING)
    require(opening["cycle_id"] == CYCLE_ID, "opening cycle")
    require(opening["base_revision"] == "9c9a78c4225a39803a0a5ac7e4e204d9b9f3773d", "opening revision")
    require(opening["base_tree"] == "af4bdbfc8f89e950936d59e6b0737b12eb5bdfb5", "opening tree")
    require(opening["opening_ledger"] == OPENING_LEDGER, "opening ledger")
    require(opening["selected_target"] == TARGET and opening["selected_count"] == 1, "opening target")
    require(opening["target"]["parent_index"] == 2599, "opening parent")
    require(opening["target"]["factor_id"] == 19069, "opening factor")
    require(opening["target"]["verified_wall_term_count"] == 108, "opening term count")
    require(opening["target"]["parent_sign_factors"] == 70, "opening parent factor count")

    predecessor = read_json(PREDECESSOR)
    require(predecessor["semantic_sha256"] == semantic_digest(predecessor), "predecessor semantic digest")
    require(predecessor["target"]["factor_id"] == 19069, "predecessor factor")
    require(predecessor["target"]["barrier_parent_factor_count"] == 70, "predecessor parent factor count")
    circuit = predecessor["factor_circuit"]
    wall = circuit["wall_polynomial"]
    require(wall["node_id"] == "f_19069", "predecessor wall node")
    factor = normalize_sparse(wall["sparse_polynomial"])
    require(factor == wall["sparse_polynomial"], "factor sparse canonical order")
    require(canonical_digest(factor) == EXPECTED_FACTOR_DIGEST, "factor sparse identity")

    profile = exact_profile(factor)
    require(profile["term_count"] == 108, "factor term census")
    require(profile["coefficient_content"] == 1, "factor primitive content")
    require(profile["total_degree_support"] == [4, 5, 6], "factor affine total degree support")
    require(profile["block_total_degree_support"] == [[1, 2], [1, 2], [0, 1, 2]], "factor block degree support")
    require(profile["variable_degree_maxima"] == [2, 1, 2, 2, 2, 2, 1, 2, 1], "factor variable degree maxima")
    homogenization = [
        {
            "coefficient": record["coefficient"],
            "exponents_a_b_c_d_e_f_g_h_i": record["exponents"],
            "homogenizer_exponents_u_v_w": [
                2 - sum(record["exponents"][index] for index in block) for block in BLOCKS
            ],
        }
        for record in factor
    ]
    require(all(all(value >= 0 for value in record["homogenizer_exponents_u_v_w"]) for record in homogenization), "trihomogenization nonnegative exponents")

    derivatives = []
    predecessor_derivatives = circuit["wall_derivative_nodes"]
    require(len(predecessor_derivatives) == 9, "predecessor derivative count")
    for coordinate, variable in enumerate(VARIABLES):
        sparse_derivative = derivative(factor, coordinate)
        term_count, expected_digest = EXPECTED_DERIVATIVES[variable]
        actual_digest = canonical_digest(sparse_derivative)
        require(len(sparse_derivative) == term_count, f"derivative {variable} term count")
        require(actual_digest == expected_digest, f"derivative {variable} identity")
        stored = predecessor_derivatives[coordinate]
        require(stored["coordinate_index"] == coordinate, f"predecessor derivative {variable} coordinate")
        require(stored["node_id"] == f"df_d{variable}", f"predecessor derivative {variable} node")
        require(stored["sparse_polynomial"] == sparse_derivative, f"predecessor derivative {variable} content")
        derivatives.append(
            {"coordinate": variable, "term_count": term_count, "sparse_sha256": actual_digest}
        )

    parent_nodes = circuit["parent_factor_nodes"]
    require(len(parent_nodes) == 70, "predecessor exact parent node count")
    require(len({node["node_id"] for node in parent_nodes}) == 70, "predecessor unique parent nodes")

    return {
        "format": "d9-factor19069-singular-df-source-reconstruction-v1",
        "cycle_id": CYCLE_ID,
        "track_id": CERT_TRACK_ID,
        "source_policy": {
            "constructor_code_imported": False,
            "predecessor_certificate_code_imported": False,
            "network_or_connector_used": False,
            "numerical_or_modular_inference_used": False,
            "seventy_inverse_discovery_used": False,
        },
        "pins": dict(sorted(PINNED_INPUTS.items())),
        "factor": {
            "factor_id": 19069,
            "ambient_ring": "Q[a,b,c,d,e,f,g,h,i]",
            "sparse_sha256": EXPECTED_FACTOR_DIGEST,
            **profile,
        },
        "derivatives": derivatives,
        "parent_factor_count": 70,
        "exact_structural_verdict": {
            "affine_three_block_homogeneous_of_multidegree_2_2_2": False,
            "affine_multiaffine": False,
            "maximum_block_degree_bound": [2, 2, 2],
            "explicit_homogenization_reconstructed": True,
            "classification": "OPENING_PREMISE_FALSE_AS_AFFINE_STATEMENT",
            "first_unresolved_branch": "EXPLICIT_THREE_BLOCK_HOMOGENIZATION_OR_REVISED_NONHOMOGENEOUS_DECOMPOSITION_NOT_SUPPLIED",
        },
        "canonical_trihomogenization": {
            "ring": "Q[a,b,c,u,d,e,f,v,g,h,i,w]",
            "homogenizers": ["u", "v", "w"],
            "block_degree": [2, 2, 2],
            "term_count": 108,
            "terms": homogenization,
            "dehomogenization_identity": "F(a,b,c,1,d,e,f,1,g,h,i,1)=f_19069",
        },
    }


def locate_frontier(explicit: Path | None = None) -> Path:
    if explicit is not None:
        require(explicit.is_file(), "explicit frontier exists")
        return explicit
    existing = [path for path in FRONTIER_CANDIDATES if path.is_file()]
    if len(existing) == 1:
        return existing[0]
    json_candidates = []
    if CONSTRUCTOR.is_dir():
        json_candidates = [
            path for path in CONSTRUCTOR.glob("*FRONTIER*.json")
            if path.name not in {"RESULT.json", "SOURCE_MANIFEST.json"}
        ]
    require(len(json_candidates) == 1, "unique constructor frontier")
    return json_candidates[0]


def find_records(value, key: str):
    """Yield values stored under *key* anywhere in a JSON tree."""
    if isinstance(value, dict):
        for name, child in value.items():
            if name == key:
                yield child
            yield from find_records(child, key)
    elif isinstance(value, list):
        for child in value:
            yield from find_records(child, key)


def require_no_truthy(candidate: dict, keys: tuple[str, ...], marker: str) -> None:
    for key in keys:
        for value in find_records(candidate, key):
            require(value in (False, None, "NOT_PROVED", "INCOMPLETE", "UNRESOLVED", "FAIL_CLOSED"), marker)


def validate_candidate(candidate: dict, source: dict) -> dict:
    """Validate the exact fail-closed constructor frontier."""
    require(isinstance(candidate, dict), "frontier object")
    require(candidate.get("semantic_sha256") == semantic_digest(candidate), "frontier semantic digest")

    def check_seals(value, location="frontier"):
        if isinstance(value, dict):
            if "semantic_sha256" in value:
                require(value["semantic_sha256"] == semantic_digest(value), f"nested semantic digest {location}")
            for key, child in value.items():
                check_seals(child, f"{location}.{key}")
        elif isinstance(value, list):
            for index, child in enumerate(value):
                check_seals(child, f"{location}[{index}]")

    for section_name in (
        "exact_affine_source_structure",
        "original_singular_jacobian_ideal",
        "decomposition_frontier",
        "parent_factor_incidence_frontier",
    ):
        section = candidate[section_name]
        require(section["semantic_sha256"] == semantic_digest(section), f"section semantic digest {section_name}")
    require(candidate.get("format") == "d9-factor19069-singular-df-multihomogeneous-constructor-frontier-v1", "frontier format")
    require(candidate.get("cycle_id") == CYCLE_ID, "frontier cycle")
    require(candidate.get("track_id") == TRACK_ID, "frontier track")
    require(candidate.get("base_revision") == "9c9a78c4225a39803a0a5ac7e4e204d9b9f3773d", "frontier base revision")
    require(candidate.get("base_tree") == "af4bdbfc8f89e950936d59e6b0737b12eb5bdfb5", "frontier base tree")
    require(candidate.get("opening_revision") == "a2860f3f6436f573a913fc8ca6312b944212aadd", "frontier opening revision")
    require(candidate.get("opening_tree") == "56f179cea8b8664156ee2dfcd6a9052d95e3b78e", "frontier opening tree")
    require(candidate.get("classification") == "EXACT_SOURCE_STRUCTURE_FALSIFICATION_FAIL_CLOSED_NULL", "frontier classification")
    require(candidate.get("outcome") == "pass", "frontier mechanical outcome")
    require(candidate.get("endpoint") == "HASH_PIN_FIRST_UNRESOLVED_MULTIHOMOGENEOUS_SINGULAR_BRANCH", "frontier null endpoint")

    predecessor = read_json(PREDECESSOR)
    binding = candidate["predecessor_binding"]
    require(binding["path"] == PREDECESSOR.relative_to(ROOT).as_posix(), "predecessor path")
    require(binding["sha256"] == PINNED_INPUTS[binding["path"]], "predecessor byte pin")
    require(binding["factor_circuit_semantic_sha256"] == predecessor["factor_circuit_semantic_sha256"], "predecessor factor circuit pin")

    structure = candidate["exact_affine_source_structure"]
    profile = source["factor"]
    require(structure["coefficient_field"] == "Q" and structure["affine_ring"] == "Q[a,b,c,d,e,f,g,h,i]", "source ring")
    require(structure["block_partition"] == [list(VARIABLES[0:3]), list(VARIABLES[3:6]), list(VARIABLES[6:9])], "source block partition")
    require(structure["block_degree_sets"] == profile["block_total_degree_support"], "source block degree sets")
    require(structure["affine_block_homogeneous_of_degree_2_2_2"] is False, "source affine block homogeneity")
    require(structure["affine_multiaffine"] is False, "source affine multiaffinity")
    require(structure["stored_multidegree_tag"] == [2, 2, 2], "source stored multidegree tag")
    require(structure["stored_multidegree_tag_exact_interpretation"] == "COORDINATEWISE_BLOCK_DEGREE_BOUND_NOT_AFFINE_BLOCK_HOMOGENEITY", "source multidegree interpretation")
    require(structure["term_count"] == 108 and structure["total_degree_bound"] == 6, "source census")
    require(structure["block_degree_vector_distribution"] == profile["block_degree_vector_distribution"], "source block vector distribution")
    require(structure["total_degree_distribution"] == profile["total_degree_distribution"], "source total degree distribution")
    require(structure["per_variable_exponent_sets"] == profile["per_variable_exponent_sets"], "source exponent sets")
    require(structure["per_variable_max_exponents"] == dict(zip(VARIABLES, profile["variable_degree_maxima"])), "source variable maxima")
    require(structure["terms_not_of_block_degree_2_2_2"] == profile["terms_not_of_block_degree_2_2_2"] == 97, "source nonhomogeneous census")
    require(structure["terms_with_at_least_one_squared_variable"] == profile["terms_with_at_least_one_squared_variable"] == 44, "source nonmultiaffine census")

    factor = predecessor["factor_circuit"]["wall_polynomial"]["sparse_polynomial"]
    first_nonhomogeneous = next(record for record in factor if [sum(record["exponents"][i] for i in block) for block in BLOCKS] != [2, 2, 2])
    require(structure["first_exact_block_homogeneity_counterexample"] == {
        "coefficient": first_nonhomogeneous["coefficient"],
        "exponents": first_nonhomogeneous["exponents"],
        "block_degree": [sum(first_nonhomogeneous["exponents"][i] for i in block) for block in BLOCKS],
    }, "source block homogeneity counterexample")
    first_squared = next(record for record in factor if any(value >= 2 for value in record["exponents"]))
    require(structure["first_exact_multiaffinity_counterexample"] == first_squared, "source multiaffinity counterexample")

    homogenization = structure["canonical_trihomogenization"]
    expected_homogenization = source["canonical_trihomogenization"]
    for key in ("ring", "homogenizers", "block_degree", "term_count", "terms", "dehomogenization_identity"):
        require(homogenization[key] == expected_homogenization[key], f"trihomogenization {key}")
    require(homogenization["does_not_imply_affine_multiaffinity"] is True, "homogenization nonimplication")
    require(homogenization["not_used_as_a_decomposition_certificate"] is True, "homogenization decomposition scope")

    ideal = candidate["original_singular_jacobian_ideal"]
    require(ideal["coefficient_field"] == "Q" and ideal["ring"] == "Q[a,b,c,d,e,f,g,h,i]", "Jacobian ideal ring")
    require(ideal["inverse_variables"] == 0, "Jacobian ideal inverse variables")
    require(ideal["generator_count"] == 10, "Jacobian ideal generator count")
    require(ideal["generator_node_ids"] == ["f_19069", *[f"df_d{variable}" for variable in VARIABLES]], "Jacobian generator ids")
    require(ideal["derivatives_rebuilt_from_sparse_source"] is True, "Jacobian derivative provenance")
    require(ideal["monomial_order_reserved_for_future_decomposition"] == "graded_reverse_lexicographic_with_variable_precedence_a_b_c_d_e_f_g_h_i", "Jacobian monomial order")
    generators = ideal["generators"]
    require(len(generators) == 10, "Jacobian generator records")
    require(generators[0]["node_id"] == "f_19069" and generators[0]["sparse_polynomial"] == factor and generators[0]["term_count"] == 108, "Jacobian wall generator")
    require(generators[0]["semantic_sha256"] == semantic_digest(generators[0]), "Jacobian wall seal")
    for index, variable in enumerate(VARIABLES):
        generator = generators[index + 1]
        expected = derivative(factor, index)
        require(generator["node_id"] == f"df_d{variable}" and generator["coordinate"] == variable and generator["coordinate_index"] == index, f"Jacobian derivative {variable} tags")
        require(generator["sparse_polynomial"] == expected and generator["term_count"] == len(expected), f"Jacobian derivative {variable}")

    decomposition = candidate["decomposition_frontier"]
    require(decomposition["branch_order"] == ["MH-B00-AFFINE-SOURCE-STRUCTURE-CONTRACT"], "decomposition branch order")
    require(decomposition["resolved_component_count"] == 0, "decomposition resolved count")
    require(decomposition["pending_component_count"] == "UNKNOWN_BECAUSE_DECOMPOSITION_NOT_STARTED_AFTER_MANDATORY_SOURCE_STOP", "decomposition pending count")
    require(decomposition["embedded_components_discarded"] == 0 and decomposition["singular_or_boundary_strata_discarded"] == 0, "decomposition stratum retention")
    require(decomposition["first_unresolved_branch_id"] == "MH-B00-AFFINE-SOURCE-STRUCTURE-CONTRACT", "first unresolved branch")
    branches = decomposition["branches"]
    require(len(branches) == 1, "decomposition branch count")
    branch = branches[0]
    require(branch["semantic_sha256"] == decomposition["first_unresolved_branch_semantic_sha256"], "decomposition first branch pin")
    require(branch["input_ideal_semantic_sha256"] == ideal["semantic_sha256"], "decomposition ideal pin")
    require(branch["status"] == "UNRESOLVED_FAIL_CLOSED_SOURCE_STRUCTURE_MISMATCH", "decomposition branch status")
    require(branch["stop_rule_invoked"] == "STOP_ON_SOURCE_DRIFT", "decomposition stop rule")
    require(branch["characteristic_zero_decomposition_started"] is False and branch["characteristic_zero_decomposition_completed"] is False, "decomposition not performed")
    require(branch["component_count"] is None and branch["embedded_component_count"] is None, "decomposition component unknowns")
    require(branch["dimensions"] is None and branch["degrees"] is None and branch["multiplicities"] is None, "decomposition invariant unknowns")
    require(branch["componentwise_parent_factor_tests_completed"] == 0 and branch["componentwise_parent_factor_tests_pending_per_future_component"] == 70, "decomposition saturation frontier")
    require(branch["strict_real_residence_status"] == "PENDING" and branch["connected_row2599_parent_tag_status"] == "PENDING", "decomposition real connected frontier")

    incidence = candidate["parent_factor_incidence_frontier"]
    require(incidence["ordered_factor_count"] == 70 and incidence["completed_component_factor_pairs"] == 0, "parent incidence counts")
    require(incidence["pending_factor_count_per_future_component"] == 70, "parent incidence pending count")
    require(incidence["inverse_variable_discovery_used"] is False, "parent incidence inverse route")
    require(incidence["componentwise_saturation_may_be_used_only_after_exact_components_exist"] is True, "parent incidence componentwise scope")
    parent_nodes = predecessor["factor_circuit"]["parent_factor_nodes"]
    records = incidence["records"]
    require(len(records) == 70, "parent incidence record count")
    for index, (record, node) in enumerate(zip(records, parent_nodes)):
        require(record["factor_index"] == index and record["factor_node_id"] == node["node_id"], f"parent record {index} identity")
        require(record["sparse_polynomial"] == node["sparse_polynomial"], f"parent record {index} polynomial")
        require(record["degree"] == node["degree"] and record["term_count"] == node["term_count"], f"parent record {index} census")
        require(record["source_semantic_sha256"] == canonical_digest(node["sparse_polynomial"]), f"parent record {index} source digest")
        require(record["componentwise_incidence_status"] == "PENDING_NO_COMPONENT_DECOMPOSITION", f"parent record {index} incidence status")
        require(record["strict_sign_status"] == "PENDING", f"parent record {index} sign status")
        require(record["boundary_stratum_status"] == "RETAINED_FROM_PINNED_PREDECESSOR", f"parent record {index} boundary status")

    require(candidate["preserved_null_frontier"] == predecessor["verified_null_frontier"], "preserved null frontier")
    require(candidate["preserved_boundary_frontier"] == predecessor["true_boundary_frontier"], "preserved boundary frontier")
    require(candidate["preserved_fixed_skeleton_accounting"] == predecessor["fixed_skeleton_accounting"], "preserved skeleton frontier")
    require(candidate["preserved_null_frontier_semantic_sha256"] == canonical_digest(candidate["preserved_null_frontier"]), "preserved null digest")
    require(candidate["preserved_boundary_frontier_semantic_sha256"] == canonical_digest(candidate["preserved_boundary_frontier"]), "preserved boundary digest")
    require(candidate["preserved_fixed_skeleton_semantic_sha256"] == canonical_digest(candidate["preserved_fixed_skeleton_accounting"]), "preserved skeleton digest")

    require(candidate["endpoint_accounting"] == {
        "negative": "NOT_REACHED_NO_EXACT_POSITIVE_DIMENSIONAL_REAL_STRICT_COMPONENT",
        "null": "REACHED_EXACT_SOURCE_STRUCTURE_MISMATCH_HASH_PINNED",
        "positive": "NOT_REACHED_NO_STRICT_SINGULAR_EMPTINESS_PROOF",
        "timeout": "NOT_REACHED",
    }, "endpoint accounting")
    require(candidate["exact_consequence"] == "THE_PINNED_108_TERM_AFFINE_FACTOR_HAS_BLOCK_DEGREE_BOUNDS_2_2_2_BUT_IS_NOT_BLOCK_HOMOGENEOUS_AND_IS_NOT_MULTIAFFINE_IN_THE_ORIGINAL_NINE_COORDINATES", "exact consequence")
    expected_nonconsequences = {
        "NO_CHARACTERISTIC_ZERO_PRIMARY_OR_EQUIDIMENSIONAL_DECOMPOSITION_OF_THE_SINGULAR_IDEAL",
        "NO_SINGULAR_COMPONENT_EQUATIONS_DIMENSIONS_DEGREES_OR_MULTIPLICITIES",
        "NO_COMPONENTWISE_PARENT_FACTOR_SATURATION_OR_INCIDENCE_CLASSIFICATION",
        "NO_STRICT_REAL_SINGULAR_COMPONENT_RESIDENCE_CLASSIFICATION",
        "NO_CONNECTED_ROW2599_PARENT_COMPONENT_TAG_FOR_A_SINGULAR_COMPONENT",
        "NO_SINGULAR_BRANCH_EMPTINESS_CERTIFICATE",
        "NO_THEOREM_LEVEL_COUNTEREXAMPLE",
        "NO_DIAGONAL_9_PROOF_OR_COUNTEREXAMPLE",
        "NO_9DVL_SCORE_CHANGE",
    }
    require(set(candidate["nonconsequences"]) == expected_nonconsequences and len(candidate["nonconsequences"]) == len(expected_nonconsequences), "nonconsequences")
    resources = candidate["resource_accounting"]
    require(resources["ceiling_crossed"] is False, "resource ceiling")
    require(resources["exact_source_terms_checked"] == 108 and resources["exact_derivatives_reconstructed"] == 9 and resources["exact_jacobian_generators_constructed"] == 10, "resource exact work")
    require(resources["component_decomposition_nodes_used"] == 0 and resources["component_factor_pairs_tested"] == 0, "resource downstream work")
    require(resources["parent_factor_nodes_preserved"] == 70, "resource parent preservation")
    for key in ("external_compute_used", "network_or_connector_used", "numerical_or_modular_probe_used", "seventy_inverse_variable_discovery_used"):
        require(resources[key] is False, f"resource scope {key}")
    require(candidate["theorem_ledger"] == OPENING_LEDGER and candidate["ledger_change_recommended"] == "none", "frontier ledger")

    return {
        "classification": "ACCEPTED_FAIL_CLOSED_SOURCE_PREMISE_FRONTIER",
        "source_factor_sha256": source["factor"]["sparse_sha256"],
        "affine_multihomogeneous": False,
        "affine_multiaffine": False,
        "characteristic_zero_decomposition_certified": False,
        "strict_parent_emptiness_certified": False,
        "real_or_connected_tag_certified": False,
        "ledger_delta": LEDGER_DELTA,
    }


def independence_audit() -> None:
    syntax = ast.parse(Path(__file__).read_text(encoding="utf-8"))
    imported = []
    for node in ast.walk(syntax):
        if isinstance(node, ast.Import):
            imported.extend(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom):
            imported.append(node.module or "")
    forbidden = ("constructor", "falsifier", "critical_equidim_certificate", "factored_barrier_certificate")
    require(not any(any(token in name for token in forbidden) for name in imported), "producer-independent imports")


def set_semantic(candidate: dict) -> dict:
    candidate["semantic_sha256"] = semantic_digest(candidate)
    return candidate


def reseal_all(value):
    if isinstance(value, dict):
        for child in value.values():
            reseal_all(child)
        if "semantic_sha256" in value:
            value["semantic_sha256"] = semantic_digest(value)
    elif isinstance(value, list):
        for child in value:
            reseal_all(child)


def hostile_mutations(candidate: dict, source: dict) -> list[dict]:
    """Run independent adversarial mutations; every mutation must reject."""
    tests = []

    def mutate(name: str, change, *, reseal: bool = True) -> None:
        hostile = deepcopy(candidate)
        change(hostile)
        if reseal:
            reseal_all(hostile)
        try:
            validate_candidate(hostile, source)
        except Reject as error:
            tests.append({"name": name, "rejected": True, "marker": str(error)})
        else:
            tests.append({"name": name, "rejected": False, "marker": "UNSOUND_ACCEPTANCE"})

    mutate("cycle drift", lambda value: value.__setitem__("cycle_id", "wrong-cycle"))
    mutate("track drift", lambda value: value.__setitem__("track_id", "wrong-track"))
    mutate("base revision drift", lambda value: value.__setitem__("base_revision", "0" * 40))
    mutate("opening tree drift", lambda value: value.__setitem__("opening_tree", "0" * 40))
    mutate("affine block homogeneity overclaim", lambda value: value["exact_affine_source_structure"].__setitem__("affine_block_homogeneous_of_degree_2_2_2", True))
    mutate("affine multiaffinity overclaim", lambda value: value["exact_affine_source_structure"].__setitem__("affine_multiaffine", True))
    mutate("block support mutation", lambda value: value["exact_affine_source_structure"].__setitem__("block_degree_sets", [[2], [2], [2]]))
    mutate("variable degree mutation", lambda value: value["exact_affine_source_structure"]["per_variable_max_exponents"].__setitem__("a", 1))
    mutate("total degree mutation", lambda value: value["exact_affine_source_structure"].__setitem__("total_degree_distribution", [{"degree": 6, "term_count": 108}]))
    mutate("homogenization mutation", lambda value: value["exact_affine_source_structure"]["canonical_trihomogenization"]["terms"][0]["homogenizer_exponents_u_v_w"].__setitem__(0, 0))
    mutate("factor coefficient mutation", lambda value: value["original_singular_jacobian_ideal"]["generators"][0]["sparse_polynomial"][0].__setitem__("coefficient", 1))
    mutate("derivative omission", lambda value: value["original_singular_jacobian_ideal"]["generators"][1]["sparse_polynomial"].pop())
    mutate("inverse-variable discovery", lambda value: value["original_singular_jacobian_ideal"].__setitem__("inverse_variables", 70))
    mutate("characteristic-zero started overclaim", lambda value: value["decomposition_frontier"]["branches"][0].__setitem__("characteristic_zero_decomposition_started", True))
    mutate("characteristic-zero completion overclaim", lambda value: value["decomposition_frontier"]["branches"][0].__setitem__("characteristic_zero_decomposition_completed", True))
    mutate("embedded component omission", lambda value: value["decomposition_frontier"].__setitem__("embedded_components_discarded", 1))
    mutate("component census overclaim", lambda value: value["decomposition_frontier"]["branches"][0].__setitem__("component_count", 0))
    mutate("component invariant overclaim", lambda value: value["decomposition_frontier"]["branches"][0].__setitem__("dimensions", []))
    mutate("70-factor saturation overclaim", lambda value: value["decomposition_frontier"]["branches"][0].__setitem__("componentwise_parent_factor_tests_completed", 70))
    mutate("strict real residence overclaim", lambda value: value["decomposition_frontier"]["branches"][0].__setitem__("strict_real_residence_status", "COMPLETE"))
    mutate("connected parent tag overclaim", lambda value: value["decomposition_frontier"]["branches"][0].__setitem__("connected_row2599_parent_tag_status", "COMPLETE"))
    mutate("boundary stratum omission", lambda value: value["decomposition_frontier"].__setitem__("singular_or_boundary_strata_discarded", 1))
    mutate("parent record omission", lambda value: value["parent_factor_incidence_frontier"]["records"].pop())
    mutate("parent polynomial mutation", lambda value: value["parent_factor_incidence_frontier"]["records"][1]["sparse_polynomial"][0].__setitem__("coefficient", 7))
    mutate("parent incidence route overclaim", lambda value: value["parent_factor_incidence_frontier"].__setitem__("inverse_variable_discovery_used", True))
    mutate("preserved null omission", lambda value: value["preserved_null_frontier"].__setitem__("connected_components_sampled", 1))
    mutate("preserved boundary omission", lambda value: value["preserved_boundary_frontier"]["records"].pop())
    mutate("positive endpoint overclaim", lambda value: value["endpoint_accounting"].__setitem__("positive", "REACHED"))
    mutate("negative endpoint overclaim", lambda value: value["endpoint_accounting"].__setitem__("negative", "REACHED"))
    mutate("ledger promotion", lambda value: value.__setitem__("ledger_change_recommended", "promote"))
    mutate("ledger state drift", lambda value: value.__setitem__("theorem_ledger", "3/9"))
    mutate("numerical inference promotion", lambda value: value["resource_accounting"].__setitem__("numerical_or_modular_probe_used", True))
    mutate("70-inverse discovery route", lambda value: value["resource_accounting"].__setitem__("seventy_inverse_variable_discovery_used", True))
    mutate("connector scope drift", lambda value: value["resource_accounting"].__setitem__("network_or_connector_used", True))
    mutate("semantic seal corruption", lambda value: value.__setitem__("semantic_sha256", "0" * 64), reseal=False)

    require(len(tests) >= 18, "hostile test count")
    accepted = [test["name"] for test in tests if not test["rejected"]]
    require(not accepted, "hostile mutation acceptance: " + ", ".join(accepted))
    return tests


def validate_constructor_companions(frontier: Path, candidate: dict) -> dict:
    manifest_path = CONSTRUCTOR / "SOURCE_MANIFEST.json"
    result_path = CONSTRUCTOR / "RESULT.json"
    require(manifest_path.is_file() and result_path.is_file(), "constructor companion files")
    manifest = read_json(manifest_path)
    require(manifest["semantic_sha256"] == semantic_digest(manifest), "constructor manifest semantic digest")
    require(manifest["format"] == "d9-factor19069-singular-df-multihomogeneous-constructor-source-manifest-v1", "constructor manifest format")
    require(manifest["cycle_id"] == CYCLE_ID and manifest["track_id"] == TRACK_ID, "constructor manifest identity")
    require(manifest["canonical_base_revision"] == "9c9a78c4225a39803a0a5ac7e4e204d9b9f3773d" and manifest["canonical_base_tree"] == "af4bdbfc8f89e950936d59e6b0737b12eb5bdfb5", "constructor manifest base")
    require(manifest["cycle_opening_revision"] == "a2860f3f6436f573a913fc8ca6312b944212aadd" and manifest["cycle_opening_tree"] == "56f179cea8b8664156ee2dfcd6a9052d95e3b78e", "constructor manifest opening")
    for relative, expected in manifest["pins"].items():
        require((ROOT / relative).is_file() and file_digest(ROOT / relative) == expected, f"constructor manifest pin {relative}")
    policy = manifest["source_policy"]
    for key in ("external_compute_used", "network_or_connector_used", "numerical_or_modular_probe_used", "producer_code_imported", "seventy_inverse_variable_discovery_used"):
        require(policy[key] is False, f"constructor manifest policy {key}")
    require(policy["predecessor_frontier_is_frozen_accepted_source"] is True, "constructor frozen predecessor policy")
    require(candidate["source_manifest_semantic_sha256"] == manifest["semantic_sha256"], "frontier manifest semantic binding")

    result = read_json(result_path)
    require(result["format"] == "d9-factor19069-singular-df-multihomogeneous-constructor-result-v1", "constructor result format")
    require(result["cycle_id"] == CYCLE_ID and result["track_id"] == TRACK_ID, "constructor result identity")
    require(result["frontier_sha256"] == file_digest(frontier), "constructor result frontier byte binding")
    require(result["frontier_semantic_sha256"] == candidate["semantic_sha256"], "constructor result frontier semantic binding")
    require(result["source_manifest_sha256"] == file_digest(manifest_path), "constructor result manifest byte binding")
    require(result["source_manifest_semantic_sha256"] == manifest["semantic_sha256"], "constructor result manifest semantic binding")
    require(result["source_structure_semantic_sha256"] == candidate["exact_affine_source_structure"]["semantic_sha256"], "constructor result source structure binding")
    require(result["original_singular_ideal_semantic_sha256"] == candidate["original_singular_jacobian_ideal"]["semantic_sha256"], "constructor result ideal binding")
    require(result["first_unresolved_branch_semantic_sha256"] == candidate["decomposition_frontier"]["first_unresolved_branch_semantic_sha256"], "constructor result first branch binding")
    require(result["classification"] == candidate["classification"] and result["endpoint"] == candidate["endpoint"], "constructor result endpoint")
    require(result["theorem_ledger"] == OPENING_LEDGER and result["ledger_change_recommended"] == "none", "constructor result ledger")
    require(set(result["nonconsequences"]) == set(candidate["nonconsequences"]), "constructor result nonconsequences")
    return {
        "frontier_sha256": file_digest(frontier),
        "manifest_sha256": file_digest(manifest_path),
        "manifest_semantic_sha256": manifest["semantic_sha256"],
        "result_sha256": file_digest(result_path),
    }


def build_source_manifest(frontier: Path, candidate: dict, companions: dict, source: dict) -> dict:
    pins = dict(PINNED_INPUTS)
    pins[frontier.relative_to(ROOT).as_posix()] = companions["frontier_sha256"]
    pins[(CONSTRUCTOR / "SOURCE_MANIFEST.json").relative_to(ROOT).as_posix()] = companions["manifest_sha256"]
    pins[(CONSTRUCTOR / "RESULT.json").relative_to(ROOT).as_posix()] = companions["result_sha256"]
    pins[Path(__file__).resolve().relative_to(ROOT).as_posix()] = file_digest(Path(__file__).resolve())
    manifest = {
        "format": "d9-factor19069-singular-df-multihomogeneous-certificate-source-manifest-v1",
        "cycle_id": CYCLE_ID,
        "track_id": CERT_TRACK_ID,
        "pins": dict(sorted(pins.items())),
        "constructor_frontier_semantic_sha256": candidate["semantic_sha256"],
        "constructor_manifest_semantic_sha256": companions["manifest_semantic_sha256"],
        "independent_source_reconstruction_semantic_sha256": source["semantic_sha256"],
        "source_policy": {
            "constructor_code_imported": False,
            "falsifier_code_imported": False,
            "predecessor_certificate_code_imported": False,
            "network_or_connector_used": False,
            "external_compute_used": False,
            "numerical_or_modular_inference_used": False,
            "seventy_inverse_discovery_used": False,
        },
    }
    manifest["semantic_sha256"] = semantic_digest(manifest)
    return manifest


def self_fixture() -> dict:
    """Minimal honest null payload used only to test verifier rejection power."""
    fixture = {
        "format": "d9-factor19069-singular-df-multihomogeneous-frontier-v1",
        "cycle_id": CYCLE_ID,
        "track_id": TRACK_ID,
        "target": {
            "parent_index": 2599,
            "factor_id": 19069,
            "ambient_parameter_dimension": 9,
            "parent_sign_factors": 70,
        },
        "classification": "NULL_FAIL_CLOSED_SOURCE_PREMISE_FALSE",
        "outcome": "NULL",
        "endpoint": NULL,
        "block_total_degree_support": [[1, 2], [1, 2], [0, 1, 2]],
        "variable_degree_maxima": [2, 1, 2, 2, 2, 2, 1, 2, 1],
        "total_degree_support": [4, 5, 6],
        "affine_three_block_homogeneous_of_multidegree_2_2_2": False,
        "affine_multiaffine": False,
        "characteristic_zero_decomposition_complete": False,
        "embedded_components_complete": False,
        "all_components_accounted": False,
        "component_invariants_complete": False,
        "all_70_parent_factor_saturations_complete": False,
        "strict_real_residence_complete": False,
        "connected_parent_tag_complete": False,
        "boundary_strata_complete": False,
        "singular_branch_empty_on_strict_parent": False,
        "numerical_inference_used": False,
        "modular_inference_promoted": False,
        "seventy_inverse_discovery_used": False,
        "network_or_connector_used": False,
        "theorem_ledger": OPENING_LEDGER,
        "ledger_delta": LEDGER_DELTA,
        "ledger_change_recommended": False,
        "nonconsequences": [
            "NO_COMPLETE_CHARACTERISTIC_ZERO_SINGULAR_DECOMPOSITION",
            "NO_COMPONENTWISE_70_FACTOR_SATURATION_CONCLUSION",
            "NO_STRICT_REAL_OR_CONNECTED_PARENT_TAG",
            "NO_DIAGONAL_NINE_THEOREM_OR_COUNTEREXAMPLE",
        ],
    }
    return set_semantic(fixture)


def build_result(frontier: Path, frontier_payload: dict, verdict: dict, source: dict, tests: list[dict]) -> dict:
    result = {
        "format": "d9-factor19069-singular-df-multihomogeneous-certificate-result-v1",
        "cycle_id": CYCLE_ID,
        "track_id": CERT_TRACK_ID,
        "constructor_frontier": frontier.relative_to(ROOT).as_posix(),
        "constructor_frontier_sha256": file_digest(frontier),
        "constructor_frontier_semantic_sha256": frontier_payload["semantic_sha256"],
        "source_reconstruction_sha256": canonical_digest(source),
        "classification": verdict["classification"],
        "exact_source_verdict": source["exact_structural_verdict"],
        "derivative_term_counts": {record["coordinate"]: record["term_count"] for record in source["derivatives"]},
        "certificate_gates": verdict,
        "hostile_tests": {"required": 18, "run": len(tests), "rejected": sum(test["rejected"] for test in tests)},
        "outcome": "NULL",
        "endpoint": NULL,
        "positive_endpoint_reached": False,
        "negative_endpoint_reached": False,
        "timeout_endpoint_reached": False,
        "ledger_before": OPENING_LEDGER,
        "ledger_after": OPENING_LEDGER,
        "ledger_delta": LEDGER_DELTA,
        "ledger_change_recommended": False,
        "nonconsequences": [
            "NO_COMPLETE_CHARACTERISTIC_ZERO_PRIMARY_OR_EQUIDIMENSIONAL_DECOMPOSITION",
            "NO_COMPLETE_COMPONENT_EMBEDDED_BOUNDARY_CENSUS",
            "NO_COMPLETE_COMPONENTWISE_SATURATION_AGAINST_ALL_70_PARENT_FACTORS",
            "NO_STRICT_REAL_RESIDENCE_OR_CONNECTED_ROW2599_PARENT_TAG",
            "NO_STRICT_PARENT_SINGULAR_BRANCH_EMPTINESS",
            "NO_UNIVERSAL_DIAGONAL_CERTIFICATE",
            "NO_THEOREM_LEDGER_PROMOTION",
        ],
    }
    result["semantic_sha256"] = semantic_digest(result)
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--frontier", type=Path)
    parser.add_argument("--self-test-only", action="store_true")
    parser.add_argument("--no-write", action="store_true")
    arguments = parser.parse_args()

    independence_audit()
    source = source_reconstruction()
    source["semantic_sha256"] = semantic_digest(source)
    frontier = locate_frontier(arguments.frontier)
    candidate = read_json(frontier)
    verdict = validate_candidate(candidate, source)
    companions = validate_constructor_companions(frontier, candidate)
    tests = hostile_mutations(candidate, source)
    if arguments.self_test_only:
        print(f"PASS exact constructor frontier, source reconstruction, companions, and {len(tests)} hostile mutations")
        return 0

    source_manifest = build_source_manifest(frontier, candidate, companions, source)
    result = build_result(frontier, candidate, verdict, source, tests)
    result["constructor_companion_sha256"] = companions
    result["source_manifest_semantic_sha256"] = source_manifest["semantic_sha256"]
    result["semantic_sha256"] = semantic_digest(result)
    if not arguments.no_write:
        write_json(SOURCE_ARTIFACT, source)
        write_json(SOURCE_MANIFEST, source_manifest)
        hostile = {
            "format": "d9-factor19069-singular-df-certificate-hostile-tests-v1",
            "cycle_id": CYCLE_ID,
            "track_id": CERT_TRACK_ID,
            "tests": tests,
        }
        hostile["semantic_sha256"] = semantic_digest(hostile)
        write_json(HOSTILE_ARTIFACT, hostile)
        write_json(RESULT, result)
        FINDINGS.write_text(
            "# Producer-independent singular-df certificate findings\n\n"
            "Verdict: **accepted fail-closed null frontier**.\n\n"
            "The frozen 108-term primitive factor and all nine derivatives were rebuilt exactly, without importing producer code. "
            "The affine polynomial is not three-block homogeneous and is not multiaffine: its block-degree supports are "
            "`{1,2} x {1,2} x {0,1,2}`, its total degrees are `4,5,6`, and the variable maxima are "
            "`(2,1,2,2,2,2,1,2,1)`.  The supplied 12-variable trihomogenization was independently reconstructed and dehomogenizes exactly, "
            "but is correctly not used as a decomposition certificate.\n\n"
            "The constructor therefore stopped at `MH-B00-AFFINE-SOURCE-STRUCTURE-CONTRACT`.  No characteristic-zero component decomposition, "
            "embedded-prime census, dimension/degree/multiplicity result, componentwise 70-factor saturation, strict real residence, or connected "
            "row-2599 parent tag is certified.  All 70 parent records and the predecessor null, boundary, and skeleton frontiers remain byte/semantic bound.\n\n"
            f"Adversarial replay rejected all {len(tests)} hostile mutations, including source, derivative, component, embedded/boundary, saturation, "
            "real/connected-tag, scope, endpoint, and ledger overclaims.  The theorem ledger remains `2/9` with delta `0/9`.\n",
            encoding="utf-8",
        )
    print("PASS producer-independent factor-19069 singular-df fail-closed certificate")
    print(f"source premise: {source['exact_structural_verdict']['classification']}")
    print(f"hostile mutations rejected: {len(tests)}/{len(tests)}")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (Reject, KeyError, TypeError, ValueError, json.JSONDecodeError) as error:
        print(f"FAIL: {error}", file=sys.stderr)
        raise SystemExit(1)
