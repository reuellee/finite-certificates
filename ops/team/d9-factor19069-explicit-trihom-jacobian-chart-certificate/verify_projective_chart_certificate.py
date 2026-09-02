#!/usr/bin/env python3
"""Producer-independent certificate for the factor-19069 chart frontier.

The frozen critical-equidimensional predecessor is the only polynomial
source.  No constructor, falsifier, or predecessor-certificate Python is
imported.  Every one of the 64 standard product charts is rebuilt with exact
integer sparse arithmetic, including its ten Jacobian generators and the
three Euler identities that recover the omitted pivot derivatives.

Downstream geometric claims deliberately fail closed.  A component
decomposition, affine contraction, 70-factor incidence result, real
residence claim, or connected-parent tag is accepted only when a dedicated
exact witness validator exists here.  This gate has no such completed
witness validator, so all such positive claims are rejected.
"""

from __future__ import annotations

import argparse
import ast
from collections import Counter
from copy import deepcopy
from hashlib import sha256
from itertools import combinations, product
import json
from pathlib import Path
import subprocess
import sys


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
CYCLE_ID = "2026-09-01-d9-row2599-factor19069-explicit-trihom-jacobian-chart-gate1"
CONSTRUCTOR_TRACK = "d9-factor19069-explicit-trihom-jacobian-chart-constructor"
CERTIFICATE_TRACK = "d9-factor19069-explicit-trihom-jacobian-chart-certificate"
TARGET = "D9_ROW2599_FACTOR19069_EXPLICIT_TRIHOMOGENIZED_JACOBIAN_CHART_DECOMPOSITION_GATE1"
BASE_REVISION = "4aee0aac6e80d053cf1751eac766280873656909"
BASE_TREE = "bfaff6f29b032ef6f81fa11a97063b01d74db8f7"
OPENING_REVISION = "cd2d856d3ccff51f7b5d6841702b25d191ed9985"
HISTORICAL_CONTROL_PATHS = {
    "ops/research-team/PROTOCOL.md",
    "ops/research-team/verify_cycle_protocol.py",
    "ops/team/d9-factor19069-singular-df-multihomogeneous-certificate/RESULT.json",
}
FROZEN_VERIFIER_SHA256 = "822b5c21fb4f738e62c9111c165fc4c447e4b6d46707b5dace7b9ae753db455a"
OPENING_LEDGER = "2/9"
LEDGER_DELTA = "0/9"

AFFINE_VARIABLES = tuple("abcdefghi")
HOMOGENEOUS_VARIABLES = ("a", "b", "c", "u", "d", "e", "f", "v", "g", "h", "i", "w")
BLOCK_VARIABLES = (("a", "b", "c", "u"), ("d", "e", "f", "v"), ("g", "h", "i", "w"))
BLOCK_INDICES = ((0, 1, 2, 3), (4, 5, 6, 7), (8, 9, 10, 11))
AFFINE_BLOCK_INDICES = ((0, 1, 2), (3, 4, 5), (6, 7, 8))
HOMOGENIZERS = ("u", "v", "w")
AFFINE_TO_HOMOGENEOUS = (0, 1, 2, 4, 5, 6, 8, 9, 10)

POSITIVE_ENDPOINT = "EXACT_SINGULAR_EMPTINESS_ON_STRICT_CONNECTED_ROW2599_PARENT_COMPONENT"
NEGATIVE_ENDPOINT = "EXACT_POSITIVE_DIMENSIONAL_REAL_SINGULAR_COMPONENT_WITH_ALL_STRICT_SIGNS_AND_CONNECTED_PARENT_TAG"
NULL_ENDPOINT = "FIRST_SOURCE_PINNED_UNRESOLVED_PROJECTIVE_CHART_DECOMPOSITION_OR_AFFINE_CONTRACTION_BRANCH"
TIMEOUT_ENDPOINT = "HASH_PIN_ALL_COMPLETED_CHART_BRANCHES_AND_FIRST_PENDING_BRANCH"

CYCLE = ROOT / "ops" / "research-team" / "cycles" / CYCLE_ID
OPENING = CYCLE / "OPENING_AUDIT.json"
FROZEN_SOURCE = ROOT / "ops" / "team" / "d9-factor19069-critical-equidim-constructor" / "CRITICAL_EQUIDIM_FRONTIER.json"
PREDECESSOR_FRONTIER = ROOT / "ops" / "team" / "d9-factor19069-singular-df-multihomogeneous-constructor" / "SINGULAR_DF_MULTIHOMOGENEOUS_FRONTIER.json"
PREDECESSOR_RECONSTRUCTION = ROOT / "ops" / "team" / "d9-factor19069-singular-df-multihomogeneous-certificate" / "SOURCE_RECONSTRUCTION.json"
CONSTRUCTOR = ROOT / "ops" / "team" / CONSTRUCTOR_TRACK
FRONTIER = CONSTRUCTOR / "PROJECTIVE_CHART_FRONTIER.json"
CONSTRUCTOR_MANIFEST = CONSTRUCTOR / "SOURCE_MANIFEST.json"
CONSTRUCTOR_RESULT = CONSTRUCTOR / "RESULT.json"
SOURCE_ARTIFACT = HERE / "SOURCE_RECONSTRUCTION.json"
SOURCE_MANIFEST = HERE / "SOURCE_MANIFEST.json"
HOSTILE_ARTIFACT = HERE / "HOSTILE_TESTS.json"
RESULT = HERE / "RESULT.json"
FINDINGS = HERE / "FINDINGS.md"

PINNED_INPUTS = {
    f"ops/research-team/cycles/{CYCLE_ID}/CYCLE.md": "4f0f6841c483a0832e39b170eb1e5c041cabc214f5733f5a21b81ee849b58dba",
    f"ops/research-team/cycles/{CYCLE_ID}/OPENING_AUDIT.json": "e513ef2f63f616cd06d3d5a27884a9919077ea1044132970de1d9691d09bbb55",
    f"ops/research-team/cycles/{CYCLE_ID}/OBLIGATION_GRAPH.json": "aedd5404ead4d36498da8a63e21d71f45a018ed2e6d2c14ea11300744545b9be",
    f"ops/research-team/cycles/{CYCLE_ID}/WORK_ORDERS.yaml": "b501084a2c5f2e8f7be24c446a0d7d20729d4689076a5316fca4c81a1b42caad",
    "ops/research-team/PROTOCOL.md": "54f1a15b7774085005707727780b266ffbd4a8edc4687fe14e1e6bc76d229031",
    "ops/research-team/verify_cycle_protocol.py": "4d9e16daed0de08af415e95c746803b512ea8b92c452df6df2c9e09fdcd3b7d1",
    "ops/team/d9-factor19069-critical-equidim-constructor/CRITICAL_EQUIDIM_FRONTIER.json": "4d7f4f21d0a5ab59ae42fa265d5a3cf851fa74dd1ff7069cd19209ec897d3a33",
    "ops/team/d9-factor19069-singular-df-multihomogeneous-constructor/SINGULAR_DF_MULTIHOMOGENEOUS_FRONTIER.json": "d9f4aba3fa8c76e3a8abff5484ff509b0458fe9993edeb921e5a6d03c4dfac41",
    "ops/team/d9-factor19069-singular-df-multihomogeneous-certificate/SOURCE_RECONSTRUCTION.json": "a185cb07fe1b10c34bf17116a262652070a068f6afffb2f7753600e0daaf1afd",
}

EXPECTED_AFFINE_FACTOR_DIGEST = "b997e1dcc7216f595610633de99dd3459658cef28676fa748d79c2ba4ac0f3dc"
EXPECTED_AFFINE_DERIVATIVES = {
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
    """An exact certificate gate rejected untrusted input."""


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


def seal(value: dict) -> dict:
    value["semantic_sha256"] = semantic_digest(value)
    return value


def file_digest(path: Path) -> str:
    return sha256(path.read_bytes()).hexdigest()


def source_digest(relative: str) -> str:
    if relative in HISTORICAL_CONTROL_PATHS:
        frozen = subprocess.check_output(
            ["git", "show", f"{OPENING_REVISION}:{relative}"], cwd=ROOT
        )
        return sha256(frozen).hexdigest()
    return file_digest(ROOT / relative)


def read_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, value) -> None:
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def normalize_sparse(records: list[dict], arity: int) -> list[dict]:
    combined: dict[tuple[int, ...], int] = {}
    for record in records:
        require(set(record) == {"exponents", "coefficient"}, "sparse record schema")
        exponent = tuple(record["exponents"])
        coefficient = record["coefficient"]
        require(len(exponent) == arity, "sparse exponent arity")
        require(all(type(value) is int and value >= 0 for value in exponent), "sparse exponent domain")
        require(type(coefficient) is int, "sparse coefficient domain")
        combined[exponent] = combined.get(exponent, 0) + coefficient
    return [
        {"exponents": list(exponent), "coefficient": coefficient}
        for exponent, coefficient in sorted(combined.items())
        if coefficient
    ]


def derivative(records: list[dict], coordinate: int) -> list[dict]:
    arity = len(records[0]["exponents"]) if records else 0
    differentiated = []
    for record in records:
        exponent = list(record["exponents"])
        power = exponent[coordinate]
        if power:
            exponent[coordinate] -= 1
            differentiated.append({"exponents": exponent, "coefficient": record["coefficient"] * power})
    return normalize_sparse(differentiated, arity)


def add_sparse(*polynomials: list[dict]) -> list[dict]:
    arity = len(polynomials[0][0]["exponents"]) if polynomials and polynomials[0] else 0
    return normalize_sparse([record for polynomial in polynomials for record in polynomial], arity)


def scale_sparse(polynomial: list[dict], coefficient: int) -> list[dict]:
    return [
        {"exponents": list(record["exponents"]), "coefficient": coefficient * record["coefficient"]}
        for record in polynomial
        if coefficient * record["coefficient"]
    ]


def multiply_coordinate(polynomial: list[dict], coordinate: int) -> list[dict]:
    multiplied = []
    for record in polynomial:
        exponent = list(record["exponents"])
        exponent[coordinate] += 1
        multiplied.append({"exponents": exponent, "coefficient": record["coefficient"]})
    return multiplied


def specialize_pivots(polynomial: list[dict], pivot_indices: tuple[int, int, int]) -> list[dict]:
    keep = [index for index in range(12) if index not in pivot_indices]
    specialized = [
        {
            "exponents": [record["exponents"][index] for index in keep],
            "coefficient": record["coefficient"],
        }
        for record in polynomial
    ]
    return normalize_sparse(specialized, 9)


def homogenize(affine: list[dict]) -> list[dict]:
    homogeneous = []
    for record in affine:
        affine_exponent = record["exponents"]
        exponent = [0] * 12
        for source_index, target_index in enumerate(AFFINE_TO_HOMOGENEOUS):
            exponent[target_index] = affine_exponent[source_index]
        exponent[3] = 2 - sum(affine_exponent[index] for index in AFFINE_BLOCK_INDICES[0])
        exponent[7] = 2 - sum(affine_exponent[index] for index in AFFINE_BLOCK_INDICES[1])
        exponent[11] = 2 - sum(affine_exponent[index] for index in AFFINE_BLOCK_INDICES[2])
        require(min(exponent) >= 0, "nonnegative homogenizer exponents")
        homogeneous.append({"exponents": exponent, "coefficient": record["coefficient"]})
    return normalize_sparse(homogeneous, 12)


def polynomial_record(node_id: str, polynomial: list[dict]) -> dict:
    return seal({
        "node_id": node_id,
        "term_count": len(polynomial),
        "sparse_sha256": canonical_digest(polynomial),
        "sparse_polynomial": polynomial,
    })


def all_nonempty_subsets(values: list[str]) -> list[list[str]]:
    return [list(choice) for size in range(1, len(values) + 1) for choice in combinations(values, size)]


def reconstruct_source() -> dict:
    for relative, expected in PINNED_INPUTS.items():
        require((ROOT / relative).is_file(), f"pinned input exists {relative}")
        require(source_digest(relative) == expected, f"pinned input digest {relative}")

    opening = read_json(OPENING)
    require(opening["cycle_id"] == CYCLE_ID, "opening cycle")
    require(opening["base_revision"] == BASE_REVISION and opening["base_tree"] == BASE_TREE, "opening base")
    require(opening["opening_ledger"] == OPENING_LEDGER, "opening ledger")
    require(opening["selected_target"] == TARGET and opening["selected_count"] == 1, "opening target")
    target = opening["target"]
    require(target["factor_id"] == 19069 and target["parent_index"] == 2599, "opening source identity")
    require(target["standard_chart_count"] == 64 and target["chart_jacobian_generators"] == 10, "opening chart contract")
    require(target["multidegree"] == [2, 2, 2], "opening multidegree")

    predecessor = read_json(FROZEN_SOURCE)
    require(predecessor["semantic_sha256"] == semantic_digest(predecessor), "frozen predecessor semantic seal")
    require(predecessor["target"]["factor_id"] == 19069, "frozen predecessor factor")
    require(predecessor["target"]["barrier_parent_factor_count"] == 70, "frozen predecessor parent factors")
    circuit = predecessor["factor_circuit"]
    wall = circuit["wall_polynomial"]
    require(wall["node_id"] == "f_19069", "frozen wall node")
    affine = normalize_sparse(wall["sparse_polynomial"], 9)
    require(affine == wall["sparse_polynomial"], "affine source canonical sparse order")
    require(len(affine) == 108 and canonical_digest(affine) == EXPECTED_AFFINE_FACTOR_DIGEST, "affine source identity")

    predecessor_trihom = read_json(PREDECESSOR_FRONTIER)["exact_affine_source_structure"]["canonical_trihomogenization"]
    prior_reconstruction = read_json(PREDECESSOR_RECONSTRUCTION)
    homogeneous = homogenize(affine)
    predecessor_terms = []
    for record in predecessor_trihom["terms"]:
        exponent = [0] * 12
        for source_index, target_index in enumerate(AFFINE_TO_HOMOGENEOUS):
            exponent[target_index] = record["exponents_a_b_c_d_e_f_g_h_i"][source_index]
        exponent[3], exponent[7], exponent[11] = record["homogenizer_exponents_u_v_w"]
        predecessor_terms.append({"exponents": exponent, "coefficient": record["coefficient"]})
    require(homogeneous == normalize_sparse(predecessor_terms, 12), "independent trihomogenization equals frozen predecessor")
    require(prior_reconstruction["canonical_trihomogenization"]["term_count"] == 108, "prior reconstruction term census")
    require(all(
        [sum(record["exponents"][index] for index in block) for block in BLOCK_INDICES] == [2, 2, 2]
        for record in homogeneous
    ), "exact trihomogeneous degree")

    affine_derivatives = []
    stored_derivatives = circuit["wall_derivative_nodes"]
    require(len(stored_derivatives) == 9, "stored affine derivative count")
    for coordinate, variable in enumerate(AFFINE_VARIABLES):
        value = derivative(affine, coordinate)
        expected_count, expected_digest = EXPECTED_AFFINE_DERIVATIVES[variable]
        require(len(value) == expected_count and canonical_digest(value) == expected_digest, f"affine derivative {variable}")
        require(stored_derivatives[coordinate]["sparse_polynomial"] == value, f"stored derivative equality {variable}")
        affine_derivatives.append(polynomial_record(f"df_d{variable}", value))

    homogeneous_derivatives = [derivative(homogeneous, index) for index in range(12)]
    charts = []
    chart_ids = []
    boundary_histogram = Counter()
    boundary_divisor_chart_incidences = 0
    boundary_stratum_chart_incidences = 0
    for chart_index, pivots in enumerate(product(*BLOCK_VARIABLES)):
        pivot_indices = tuple(HOMOGENEOUS_VARIABLES.index(pivot) for pivot in pivots)
        free_indices = [index for index in range(12) if index not in pivot_indices]
        free_variables = [HOMOGENEOUS_VARIABLES[index] for index in free_indices]
        chart_id = "CH-" + "-".join(pivots)
        chart_ids.append(chart_id)
        chart_polynomial = specialize_pivots(homogeneous, pivot_indices)
        free_derivatives = [derivative(chart_polynomial, index) for index in range(9)]
        generators = [polynomial_record("F_chart", chart_polynomial)]
        generators.extend(
            polynomial_record(f"dF_d{variable}", value)
            for variable, value in zip(free_variables, free_derivatives)
        )

        euler_records = []
        for block_index, (block, pivot, pivot_global_index) in enumerate(zip(BLOCK_VARIABLES, pivots, pivot_indices)):
            pivot_derivative = specialize_pivots(homogeneous_derivatives[pivot_global_index], pivot_indices)
            rhs_terms = [scale_sparse(chart_polynomial, 2)]
            free_block_variables = [variable for variable in block if variable != pivot]
            for variable in free_block_variables:
                local_index = free_variables.index(variable)
                rhs_terms.append(scale_sparse(multiply_coordinate(free_derivatives[local_index], local_index), -1))
            rhs = add_sparse(*rhs_terms)
            require(pivot_derivative == rhs, f"Euler transfer {chart_id} block {block_index}")
            euler_records.append(seal({
                "block_index": block_index,
                "block_variables": list(block),
                "pivot": pivot,
                "free_block_variables": free_block_variables,
                "identity": f"dF_d{pivot}|chart = 2*F_chart - sum(x*dF_dx for x in free block coordinates)",
                "pivot_derivative_term_count": len(pivot_derivative),
                "pivot_derivative_sparse_sha256": canonical_digest(pivot_derivative),
                "rhs_sparse_sha256": canonical_digest(rhs),
                "identity_exact": True,
            }))

        boundary_coordinates = [
            homogenizer
            for pivot, homogenizer in zip(pivots, HOMOGENIZERS)
            if pivot != homogenizer
        ]
        boundary_histogram[len(boundary_coordinates)] += 1
        boundary_divisor_chart_incidences += len(boundary_coordinates)
        admitted_strata = all_nonempty_subsets(boundary_coordinates)
        boundary_stratum_chart_incidences += len(admitted_strata)
        chart = {
            "chart_index": chart_index,
            "chart_id": chart_id,
            "pivots_set_to_one": list(pivots),
            "pivot_global_indices": list(pivot_indices),
            "free_variables": free_variables,
            "free_global_indices": free_indices,
            "ring": "Q[" + ",".join(free_variables) + "]",
            "affine_u_v_w_chart": list(pivots) == list(HOMOGENIZERS),
            "chart_polynomial": polynomial_record("F_chart", chart_polynomial),
            "jacobian_ideal": seal({
                "generator_count": 10,
                "generator_node_ids": [record["node_id"] for record in generators],
                "generators": generators,
                "all_nine_free_derivatives_reconstructed": True,
            }),
            "euler_transfer": euler_records,
            "boundary": seal({
                "infinity_capable_block_count": len(boundary_coordinates),
                "free_homogenizer_coordinates": boundary_coordinates,
                "boundary_divisor_equations": [f"{coordinate}=0" for coordinate in boundary_coordinates],
                "admitted_nonempty_boundary_strata": admitted_strata,
                "boundary_strata_discarded": 0,
            }),
        }
        charts.append(seal(chart))

    require(len(charts) == 64 and len(set(chart_ids)) == 64, "64 unique chart records")
    require(dict(sorted(boundary_histogram.items())) == {0: 1, 1: 9, 2: 27, 3: 27}, "boundary chart histogram")
    require(boundary_divisor_chart_incidences == 144, "boundary divisor chart incidences")
    require(boundary_stratum_chart_incidences == 279, "boundary stratum chart incidences")

    affine_chart = next(chart for chart in charts if chart["affine_u_v_w_chart"])
    require(affine_chart["chart_id"] == "CH-u-v-w", "affine chart identity")
    require(affine_chart["free_variables"] == list(AFFINE_VARIABLES), "affine chart coordinate order")
    require(affine_chart["chart_polynomial"]["sparse_polynomial"] == affine, "affine dehomogenization equality")
    affine_chart_derivatives = affine_chart["jacobian_ideal"]["generators"][1:]
    require(
        [record["sparse_polynomial"] for record in affine_chart_derivatives]
        == [record["sparse_polynomial"] for record in affine_derivatives],
        "affine singular ideal generator equality",
    )

    boundary_types = []
    for size in range(1, 4):
        for subset in combinations(HOMOGENIZERS, size):
            compatible_chart_count = (3 ** size) * (4 ** (3 - size))
            boundary_types.append({
                "homogenizers_zero": list(subset),
                "codimension_in_product": size,
                "compatible_standard_charts": compatible_chart_count,
            })
    require(sum(record["compatible_standard_charts"] for record in boundary_types) == 279, "global boundary strata accounting")

    source = {
        "format": "d9-factor19069-explicit-trihom-jacobian-chart-source-reconstruction-v1",
        "cycle_id": CYCLE_ID,
        "track_id": CERTIFICATE_TRACK,
        "base_revision": BASE_REVISION,
        "base_tree": BASE_TREE,
        "pins": dict(sorted(PINNED_INPUTS.items())),
        "source_policy": {
            "constructor_code_imported": False,
            "constructor_acceptance_imported": False,
            "falsifier_code_imported": False,
            "predecessor_certificate_code_imported": False,
            "network_or_connector_used": False,
            "external_algebra_service_used": False,
            "numerical_or_modular_inference_used": False,
            "seventy_inverse_variable_discovery_used": False,
        },
        "affine_factor": polynomial_record("f_19069", affine),
        "affine_derivatives": affine_derivatives,
        "trihomogeneous_source": seal({
            "ring": "Q[a,b,c,u,d,e,f,v,g,h,i,w]",
            "blocks": [list(block) for block in BLOCK_VARIABLES],
            "block_degree": [2, 2, 2],
            "term_count": len(homogeneous),
            "sparse_sha256": canonical_digest(homogeneous),
            "sparse_polynomial": homogeneous,
            "dehomogenization_identity": "F(a,b,c,1,d,e,f,1,g,h,i,1)=f_19069",
            "dehomogenization_verified_exactly": True,
            "not_a_decomposition_certificate": True,
        }),
        "chart_cover": seal({
            "ambient": "(P^3)^3",
            "standard_chart_count": 64,
            "chart_order": chart_ids,
            "charts": charts,
            "aggregate_chart_semantic_sha256": canonical_digest([chart["semantic_sha256"] for chart in charts]),
            "chart_jacobian_generator_count_each": 10,
            "euler_identity_count_each": 3,
            "all_chart_polynomials_reconstructed": True,
            "all_chart_jacobian_generators_reconstructed": True,
            "all_euler_identities_verified": True,
        }),
        "affine_transfer": seal({
            "chart_id": "CH-u-v-w",
            "free_variables": list(AFFINE_VARIABLES),
            "chart_polynomial_equals_affine_factor": True,
            "nine_chart_derivatives_equal_affine_derivatives": True,
            "chart_jacobian_ideal_equals_original_affine_singular_ideal": True,
            "generator_count": 10,
            "original_affine_ideal_semantic_sha256": canonical_digest([
                affine, *[record["sparse_polynomial"] for record in affine_derivatives]
            ]),
        }),
        "boundary_accounting": seal({
            "affine_pivot_chart_count": 1,
            "charts_admitting_at_least_one_infinity_divisor": 63,
            "charts_by_infinity_capable_block_count": [
                {"count": boundary_histogram[index], "infinity_capable_block_count": index}
                for index in range(4)
            ],
            "boundary_divisor_chart_incidences": boundary_divisor_chart_incidences,
            "global_nonempty_boundary_stratum_types": boundary_types,
            "global_nonempty_boundary_stratum_type_count": 7,
            "boundary_stratum_chart_incidences": boundary_stratum_chart_incidences,
            "infinity_or_boundary_strata_discarded": 0,
        }),
        "parent_factor_count_preserved_from_frozen_source": len(circuit["parent_factor_nodes"]),
        "exact_scope": {
            "source_reconstruction_certified": True,
            "complete_64_chart_cover_certified": True,
            "chart_jacobian_and_euler_transfer_certified": True,
            "affine_singular_ideal_equality_certified": True,
            "boundary_chart_accounting_certified": True,
            "characteristic_zero_component_decomposition_certified": False,
            "affine_component_contraction_certified": False,
            "componentwise_all_70_parent_factor_tests_certified": False,
            "strict_real_residence_certified": False,
            "connected_parent_tag_certified": False,
            "universal_diagonal_certificate": False,
        },
    }
    return seal(source)


def independence_audit() -> None:
    syntax = ast.parse(Path(__file__).read_text(encoding="utf-8"))
    imported = []
    for node in ast.walk(syntax):
        if isinstance(node, ast.Import):
            imported.extend(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom):
            imported.append(node.module or "")
    forbidden = ("constructor", "falsifier", "singular_df_certificate", "critical_equidim_certificate")
    require(not any(any(token in name for token in forbidden) for name in imported), "producer-independent imports")


def check_semantic_seals(value, location: str = "frontier") -> None:
    if isinstance(value, dict):
        if "semantic_sha256" in value:
            require(value["semantic_sha256"] == semantic_digest(value), f"semantic seal {location}")
        for key, child in value.items():
            check_semantic_seals(child, f"{location}.{key}")
    elif isinstance(value, list):
        for index, child in enumerate(value):
            check_semantic_seals(child, f"{location}[{index}]")


def constructor_chart_id(index: int, pivots: list[str] | tuple[str, ...]) -> str:
    return f"JCH-{index:02d}-" + "-".join(pivots)


def expected_overlap_records(source_index: int, source_pivots: list[str]) -> list[dict]:
    records = []
    all_pivots = list(product(*BLOCK_VARIABLES))
    for target_index, target_pivots in enumerate(all_pivots):
        if target_index == source_index:
            continue
        transitions = []
        required = []
        for block_index, (source_pivot, target_pivot) in enumerate(zip(source_pivots, target_pivots)):
            if source_pivot != target_pivot:
                required.append(target_pivot)
                transitions.append({
                    "block_index": block_index,
                    "required_nonzero_source_coordinate": target_pivot,
                    "source_pivot": source_pivot,
                    "target_normalization_scale": f"1/{target_pivot}",
                    "target_pivot": target_pivot,
                })
        records.append({
            "block_transitions": transitions,
            "overlap_status": "EXPLICIT_NONEMPTY_PRINCIPAL_OPEN_WHEN_REQUIREMENTS_HOLD",
            "required_nonzero_coordinates": required,
            "target_chart_id": constructor_chart_id(target_index, target_pivots),
        })
    return records


def validate_candidate(candidate: dict, source: dict, *, verify_seals: bool = True) -> dict:
    require(isinstance(candidate, dict), "frontier object")
    if verify_seals:
        check_semantic_seals(candidate)
    require(candidate["format"] == "d9-factor19069-explicit-trihom-jacobian-chart-constructor-frontier-v1", "frontier format")
    require(candidate["cycle_id"] == CYCLE_ID and candidate["track_id"] == CONSTRUCTOR_TRACK, "frontier identity")
    require(candidate["base_revision"] == BASE_REVISION and candidate["base_tree"] == BASE_TREE, "frontier base")
    require(candidate["opening_revision"] == "cd2d856d3ccff51f7b5d6841702b25d191ed9985", "frontier opening revision")
    require(candidate["opening_tree"] == "6014474550142ec47f9280a123dc77bf403d1d0a", "frontier opening tree")
    require(candidate["classification"] == "BOUNDED_CHARACTERISTIC_ZERO_CHART_DECOMPOSITION_TIMEOUT_FAIL_CLOSED", "frontier classification")
    require(candidate["outcome"] == "pass" and candidate["endpoint"] == TIMEOUT_ENDPOINT, "frontier timeout endpoint")

    binding = candidate["predecessor_binding"]
    require(binding["path"] == PREDECESSOR_FRONTIER.relative_to(ROOT).as_posix(), "predecessor path")
    require(binding["file_sha256"] == PINNED_INPUTS[binding["path"]], "predecessor byte binding")
    require(binding["predecessor_semantic_sha256"] == read_json(PREDECESSOR_FRONTIER)["semantic_sha256"], "predecessor semantic binding")

    trihom = candidate["trihomogeneous_source"]
    expected_homogeneous = source["trihomogeneous_source"]["sparse_polynomial"]
    require(trihom["ring"] == "Q[a,b,c,u,d,e,f,v,g,h,i,w]", "trihomogeneous ring")
    require(trihom["blocks"] == [list(block) for block in BLOCK_VARIABLES] and trihom["multidegree"] == [2, 2, 2], "trihomogeneous blocks")
    require(trihom["term_count"] == 108, "trihomogeneous term census")
    require(trihom["polynomial"]["sparse_polynomial"] == expected_homogeneous, "trihomogeneous exact sparse source")
    require(trihom["polynomial"]["term_count"] == 108, "trihomogeneous polynomial census")
    require(trihom["affine_source_is_homogeneous"] is False and trihom["affine_source_is_multiaffine"] is False, "affine source flags")
    require(trihom["dehomogenization_exact_sparse_equality"] is True, "dehomogenization equality")
    require(trihom["trihomogenization_is_decomposition_certificate"] is False, "trihomogenization scope")

    atlas = candidate["chart_atlas"]
    expected_candidate_ids = [
        constructor_chart_id(index, record["pivots_set_to_one"])
        for index, record in enumerate(source["chart_cover"]["charts"])
    ]
    require(atlas["ambient"] == "(P^3)^3" and atlas["block_coordinate_order"] == [list(block) for block in BLOCK_VARIABLES], "atlas ambient")
    require(atlas["standard_chart_count"] == 64 and len(atlas["charts"]) == 64, "atlas chart count")
    require(atlas["chart_order"] == expected_candidate_ids, "atlas chart order")
    require(atlas["affine_chart_id"] == "JCH-63-u-v-w", "atlas affine chart")
    require(atlas["directed_overlap_record_count"] == 4032, "atlas directed overlap count")
    require(atlas["charts_intersecting_at_least_one_boundary_hyperplane"] == 63, "atlas boundary chart count")
    require(atlas["local_nonempty_boundary_intersection_record_count"] == 279, "atlas boundary incidence count")
    require(atlas["expected_local_nonempty_boundary_intersection_record_count"] == 279, "atlas expected boundary incidence count")
    require(atlas["global_nonempty_boundary_type_count"] == 7, "atlas global boundary type count")
    require(atlas["global_boundary_types"] == all_nonempty_subsets(list(HOMOGENIZERS)), "atlas global boundary types")
    require(atlas["all_available_boundary_strata_retained"] is True and atlas["all_product_charts_retained"] is True, "atlas retention")
    require(atlas["symmetry_quotient_used"] is False, "atlas no symmetry quotient")

    decomposition = candidate["decomposition_frontier"]
    require(decomposition["required_characteristic"] == 0 and decomposition["coefficient_field"] == "Q", "decomposition coefficient field")
    require(decomposition["complete_projective_decomposition"] is False, "decomposition fail closed")
    require(decomposition["accepted_component_count"] == 0 and decomposition["resolved_chart_count"] == 0, "decomposition accepted count")
    require(decomposition["pending_chart_count"] == 64, "decomposition pending count")
    require(decomposition["embedded_components_discarded"] == 0 and decomposition["boundary_strata_discarded"] == 0, "decomposition strata retention")
    require(decomposition["branch_order"] == [identifier.replace("JCH-", "DEC-JCH-") for identifier in expected_candidate_ids], "decomposition branch order")
    require(decomposition["first_pending_branch_id"] == "DEC-JCH-00-a-d-g", "first pending branch")
    first_pending = decomposition["first_pending_branch"]
    require(first_pending["semantic_sha256"] == decomposition["first_pending_branch_semantic_sha256"], "first pending branch seal binding")
    require(first_pending["chart_id"] == "JCH-00-a-d-g" and first_pending["status"] == "TIMEOUT_FIRST_CHART_GROEBNER_PREREQUISITE_PENDING", "first pending status")
    require(first_pending["complete_primary_or_equidimensional_decomposition"] is False, "first pending incomplete")
    require(first_pending["component_count"] is None and first_pending["accepted_components"] == [], "first pending components")
    require(first_pending["embedded_component_accounting_completed"] is False, "first pending embedded accounting")
    require(first_pending["singular_or_boundary_strata_discarded"] == 0, "first pending strata")
    attempt = decomposition["attempt"]
    require(attempt["accepted_as_decomposition_certificate"] is False and attempt["primary_decomposition_completed"] is False, "attempt not certificate")
    require(attempt["component_count"] is None and attempt["embedded_component_count"] is None, "attempt component unknowns")
    require(attempt["attempted_chart_id"] == "JCH-00-a-d-g" and attempt["status"] == "TIMEOUT_FIRST_CHART_GROEBNER_PREREQUISITE_PENDING", "attempt frontier")
    require(attempt["coefficient_field"] == "Q" and attempt["ceiling_triggered"] == "WALL_SECONDS", "attempt exact bounded scope")
    require(decomposition["groebner_basis_is_not_a_primary_decomposition"] is True, "Groebner scope")

    contraction = candidate["affine_contraction_frontier"]
    for key in ("accepted_affine_component_count", "accepted_projective_component_count", "componentwise_parent_tests_started", "contracted_to_original_affine_singular_ideal_count"):
        require(contraction[key] == 0, f"contraction fail closed {key}")
    require(contraction["order_respected"] is True, "contraction order")
    require(contraction["pending_reason"] == "NO_COMPLETE_CHARACTERISTIC_ZERO_CHART_DECOMPOSITION", "contraction pending reason")

    incidence = candidate["parent_factor_incidence_frontier"]
    require(incidence["ordered_factor_count"] == 70 and len(incidence["records"]) == 70, "parent factor count")
    require(incidence["accepted_contracted_component_count"] == 0 and incidence["completed_component_factor_pairs"] == 0, "parent incidence fail closed")
    require(incidence["required_tests_per_future_contracted_component"] == 70, "parent test requirement")
    require(incidence["inverse_variable_discovery_used"] is False, "no inverse discovery")
    require(incidence["source_parent_factor_tags_preserved"] is True and incidence["source_record_order_preserved"] is True, "parent tag preservation")
    frozen_parent_nodes = read_json(FROZEN_SOURCE)["factor_circuit"]["parent_factor_nodes"]
    for index, (record, node) in enumerate(zip(incidence["records"], frozen_parent_nodes)):
        require(record["factor_index"] == index and record["factor_node_id"] == node["node_id"], f"parent identity {index}")
        require(record["sparse_polynomial"] == node["sparse_polynomial"], f"parent sparse polynomial {index}")
        require(record["degree"] == node["degree"] and record["term_count"] == node["term_count"], f"parent census {index}")
        require(record["source_semantic_sha256"] == canonical_digest(node["sparse_polynomial"]), f"parent source digest {index}")
        require(record["componentwise_incidence_status"] == "PENDING_NO_ACCEPTED_CONTRACTED_AFFINE_COMPONENT", f"parent incidence pending {index}")
        require(record["strict_sign_status"] == "PENDING_NO_ACCEPTED_CONTRACTED_AFFINE_COMPONENT", f"parent sign pending {index}")
        require(record["boundary_stratum_status"] == "PRESERVED_SOURCE_TAG_NO_COMPONENT_TEST", f"parent boundary tag {index}")

    predecessor = read_json(PREDECESSOR_FRONTIER)
    preserved = candidate["preserved_predecessor_strata"]
    require(preserved["verified_null_frontier"] == predecessor["preserved_null_frontier"], "preserved null frontier")
    require(preserved["true_boundary_frontier"] == predecessor["preserved_boundary_frontier"], "preserved boundary frontier")
    require(preserved["fixed_skeleton_accounting"] == predecessor["preserved_fixed_skeleton_accounting"], "preserved skeleton accounting")
    require(preserved["source_tags_preserved"] is True and preserved["strata_discarded"] == 0, "preserved source tags")

    require(candidate["endpoint_accounting"] == {
        "negative": "NOT_REACHED_NO_EXACT_POSITIVE_DIMENSIONAL_STRICT_REAL_SINGULAR_COMPONENT",
        "null": "NOT_REACHED",
        "positive": "NOT_REACHED_NO_EXACT_STRICT_PARENT_SINGULAR_EMPTINESS",
        "timeout": "REACHED_HASH_PINNED_FIRST_PENDING_CHART",
    }, "endpoint accounting")
    resources = candidate["resource_accounting"]
    require(resources["attempted_chart_count"] == 1 and resources["completed_chart_decomposition_count"] == 0, "resource chart counts")
    for key in ("network_or_connector_used", "numerical_or_modular_probe_used", "paid_external_compute_used", "seventy_inverse_variable_discovery_used"):
        require(resources[key] is False, f"resource scope {key}")
    require(candidate["theorem_ledger"] == OPENING_LEDGER and candidate["ledger_change_recommended"] == "none", "ledger unchanged")
    expected_nonconsequences = {
        "NO_COMPLETE_CHARACTERISTIC_ZERO_PROJECTIVE_CHART_DECOMPOSITION",
        "NO_PRIMARY_OR_EQUIDIMENSIONAL_COMPONENT_CENSUS",
        "NO_EMBEDDED_COMPONENT_COMPLETENESS_CLAIM",
        "NO_OVERLAP_DEDUPLICATED_PROJECTIVE_COMPONENTS",
        "NO_ACCEPTED_AFFINE_COMPONENT_CONTRACTIONS",
        "NO_COMPONENTWISE_TESTS_AGAINST_THE_70_PARENT_FACTORS",
        "NO_STRICT_REAL_RESIDENCE_OR_CONNECTED_PARENT_TAG",
        "NO_STRICT_PARENT_SINGULAR_EMPTINESS_CERTIFICATE",
        "NO_THEOREM_LEVEL_COUNTEREXAMPLE",
        "NO_DIAGONAL_9_PROOF_OR_COUNTEREXAMPLE",
        "NO_9DVL_SCORE_CHANGE",
    }
    require(set(candidate["nonconsequences"]) == expected_nonconsequences and len(candidate["nonconsequences"]) == len(expected_nonconsequences), "nonconsequences")

    source_charts = source["chart_cover"]["charts"]
    for index, (chart, expected) in enumerate(zip(atlas["charts"], source_charts)):
        pivots = expected["pivots_set_to_one"]
        expected_id = expected_candidate_ids[index]
        require(chart["chart_index"] == index and chart["chart_id"] == expected_id, f"chart identity {index}")
        require(chart["pivots"] == pivots and chart["pivot_global_indices"] == expected["pivot_global_indices"], f"chart pivots {index}")
        require(chart["pivot_offsets"] == [list(block).index(pivot) for block, pivot in zip(BLOCK_VARIABLES, pivots)], f"chart pivot offsets {index}")
        require(chart["pivot_substitution"] == {pivot: 1 for pivot in pivots}, f"chart pivot substitution {index}")
        require(chart["free_coordinates"] == expected["free_variables"] and chart["free_coordinate_count"] == 9, f"chart free coordinates {index}")
        require(chart["affine_source_chart"] == expected["affine_u_v_w_chart"], f"chart affine flag {index}")
        require(chart["forced_nonzero_original_coordinates"] == [pivot for pivot in pivots if pivot in AFFINE_VARIABLES], f"chart forced coordinates {index}")
        require(chart["coverage_tag"] == "STANDARD_PRODUCT_CHART_D(" + "*".join(pivots) + ")", f"chart coverage tag {index}")

        expected_polynomial = expected["chart_polynomial"]["sparse_polynomial"]
        require(chart["F_chart"]["coordinate_order"] == expected["free_variables"], f"chart polynomial coordinates {index}")
        require(chart["F_chart"]["sparse_polynomial"] == expected_polynomial, f"chart polynomial {index}")
        require(chart["F_chart"]["term_count"] == len(expected_polynomial), f"chart polynomial census {index}")
        expected_derivatives = expected["jacobian_ideal"]["generators"][1:]
        require(len(chart["free_derivatives"]) == 9, f"chart derivative count {index}")
        for local_index, (actual_derivative, expected_derivative) in enumerate(zip(chart["free_derivatives"], expected_derivatives)):
            variable = expected["free_variables"][local_index]
            require(actual_derivative["derivative_coordinate"] == variable and actual_derivative["derivative_coordinate_index"] == local_index, f"chart derivative tag {index}:{variable}")
            require(actual_derivative["coordinate_order"] == expected["free_variables"], f"chart derivative coordinates {index}:{variable}")
            require(actual_derivative["sparse_polynomial"] == expected_derivative["sparse_polynomial"], f"chart derivative polynomial {index}:{variable}")
            require(actual_derivative["term_count"] == expected_derivative["term_count"], f"chart derivative census {index}:{variable}")
        jacobian = chart["chart_jacobian_ideal"]
        require(jacobian["generator_count"] == 10 and jacobian["coefficient_field"] == "Q", f"chart Jacobian count {index}")
        require(jacobian["ring"] == "Q[" + ",".join(expected["free_variables"]) + "]", f"chart Jacobian ring {index}")
        require(jacobian["generator_node_ids"] == [chart["F_chart"]["node_id"], *[record["node_id"] for record in chart["free_derivatives"]]], f"chart Jacobian generators {index}")

        require(chart["euler_recovery_count"] == 3 and chart["euler_zero_residual_count"] == 3, f"Euler count {index}")
        require(chart["full_projective_jacobian_transfer_proved"] is True, f"Euler transfer claim {index}")
        require(len(chart["euler_pivot_recoveries"]) == 3, f"Euler records {index}")
        for block_index, (actual_euler, expected_euler) in enumerate(zip(chart["euler_pivot_recoveries"], expected["euler_transfer"])):
            pivot = pivots[block_index]
            require(actual_euler["block_index"] == block_index and actual_euler["block_degree"] == 2 and actual_euler["pivot"] == pivot, f"Euler tags {index}:{block_index}")
            require(actual_euler["free_block_coordinates"] == expected_euler["free_block_variables"], f"Euler free block {index}:{block_index}")
            require(actual_euler["direct_specialization"]["sparse_polynomial"] == actual_euler["euler_reconstruction"]["sparse_polynomial"], f"Euler direct equality {index}:{block_index}")
            require(canonical_digest(actual_euler["direct_specialization"]["sparse_polynomial"]) == expected_euler["pivot_derivative_sparse_sha256"], f"Euler independent equality {index}:{block_index}")
            require(actual_euler["exact_zero_residual"]["sparse_polynomial"] == [] and actual_euler["exact_zero_residual"]["term_count"] == 0, f"Euler zero residual {index}:{block_index}")
            require(actual_euler["exact_sparse_equality"] is True, f"Euler exact flag {index}:{block_index}")
            require(actual_euler["exact_ideal_equality"] == "<F_CHART,NINE_FREE_DERIVATIVES>=<ALL_TWELVE_SPECIALIZED_HOMOGENEOUS_DERIVATIVES>", f"Euler ideal equality {index}:{block_index}")

        expected_available = expected["boundary"]["free_homogenizer_coordinates"]
        expected_excluded = [homogenizer for pivot, homogenizer in zip(pivots, HOMOGENIZERS) if pivot == homogenizer]
        require(chart["boundary_hyperplanes_available"] == expected_available and chart["boundary_hyperplanes_excluded_by_pivot"] == expected_excluded, f"boundary divisors {index}")
        require(chart["boundary_homogenizers"] == expected_available, f"boundary homogenizers {index}")
        require(chart["chart_is_wholly_infinity"] is False and chart["contains_affine_overlap"] is True, f"chart is not wholly infinity {index}")
        expected_strata = []
        for mask in range(1, 1 << len(expected_available)):
            subset = [coordinate for bit, coordinate in enumerate(expected_available) if mask & (1 << bit)]
            expected_strata.append({
                "boundary_bitmask": mask,
                "boundary_subset": [f"{value}=0" for value in subset],
                "retention_status": "RETAINED_FOR_EXACT_CHART_DECOMPOSITION",
                "status": "RETAINED",
                "stratum_tag": "BOUNDARY_" + "_".join(value.upper() for value in subset) + "_ZERO",
                "zero_homogenizers": subset,
            })
        require(chart["boundary_strata"] == expected_strata, f"boundary strata {index}")
        require(chart["boundary_retention_status"] == "ALL_AVAILABLE_INFINITY_BOUNDARY_STRATA_RETAINED", f"boundary retention {index}")
        require(chart["boundary_strata_discarded"] == 0 and chart["embedded_components_discarded"] == 0, f"chart discarded strata {index}")
        require(chart["accepted_components"] == [], f"chart accepted components {index}")
        require(chart["component_decomposition_status"] in {"TIMEOUT_FIRST_CHART_GROEBNER_PREREQUISITE_PENDING", "NOT_STARTED_AFTER_FIRST_PENDING_CHART_STOP_RULE"}, f"chart decomposition status {index}")
        expected_overlaps = expected_overlap_records(index, pivots)
        require(chart["overlap_record_count"] == 63 and chart["overlap_records"] == expected_overlaps, f"chart overlaps {index}")

    affine = candidate["affine_transfer"]
    require(affine["chart_id"] == "JCH-63-u-v-w" and affine["pivot_substitution"] == {"u": 1, "v": 1, "w": 1}, "affine transfer chart")
    require(affine["free_coordinate_order"] == list(AFFINE_VARIABLES), "affine transfer coordinates")
    for key in ("F_chart_equals_original_f_19069", "nine_chart_derivatives_equal_original_affine_derivatives", "chart_ideal_equals_original_affine_singular_ideal"):
        require(affine[key] is True, f"affine transfer {key}")
    require(affine["chart_ideal_generator_count"] == 10 and affine["original_ideal_generator_count"] == 10, "affine ideal counts")
    require(affine["proof_method"] == "EXACT_SPARSE_COEFFICIENT_EQUALITY_IN_Q[a,b,c,d,e,f,g,h,i]", "affine proof method")

    return {
        "classification": "ACCEPTED_EXACT_64_CHART_RECONSTRUCTION_FAIL_CLOSED_TIMEOUT_FRONTIER",
        "source_reconstructed": True,
        "trihomogeneous_source_certified": True,
        "chart_count_certified": 64,
        "chart_jacobian_generator_count_each": 10,
        "Euler_identities_certified": 192,
        "directed_overlap_records_certified": 4032,
        "affine_original_ideal_equality_certified": True,
        "boundary_chart_count_certified": 63,
        "boundary_stratum_chart_incidences_certified": 279,
        "characteristic_zero_decomposition_certified": False,
        "component_contraction_certified": False,
        "all_70_parent_factor_tests_certified": False,
        "strict_real_residence_certified": False,
        "connected_parent_tag_certified": False,
        "universal_diagonal_certificate": False,
        "ledger_delta": LEDGER_DELTA,
    }


def validate_constructor_companions(candidate: dict) -> dict:
    require(CONSTRUCTOR_MANIFEST.is_file() and CONSTRUCTOR_RESULT.is_file(), "constructor companions exist")
    manifest = read_json(CONSTRUCTOR_MANIFEST)
    require(manifest["semantic_sha256"] == semantic_digest(manifest), "constructor manifest seal")
    require(manifest["format"] == "d9-factor19069-explicit-trihom-jacobian-chart-constructor-source-manifest-v1", "constructor manifest format")
    require(manifest["cycle_id"] == CYCLE_ID and manifest["track_id"] == CONSTRUCTOR_TRACK, "constructor manifest identity")
    require(manifest["canonical_base_revision"] == BASE_REVISION and manifest["canonical_base_tree"] == BASE_TREE, "constructor manifest base")
    require(manifest["cycle_opening_revision"] == candidate["opening_revision"] and manifest["cycle_opening_tree"] == candidate["opening_tree"], "constructor manifest opening")
    for relative, expected in manifest["pins"].items():
        require((ROOT / relative).is_file() and source_digest(relative) == expected, f"constructor manifest pin {relative}")
    policy = manifest["source_policy"]
    require(policy["all_64_charts_constructed_without_symmetry_quotient"] is True, "constructor chart policy")
    for key in ("network_or_connector_used", "numerical_or_modular_probe_used", "predecessor_builder_code_imported", "seventy_inverse_variable_discovery_used", "trihomogenization_used_as_decomposition_certificate"):
        require(policy[key] is False, f"constructor policy {key}")
    require(candidate["source_manifest_semantic_sha256"] == manifest["semantic_sha256"], "frontier manifest binding")

    result = read_json(CONSTRUCTOR_RESULT)
    require(result["format"] == "d9-factor19069-explicit-trihom-jacobian-chart-constructor-result-v1", "constructor result format")
    require(result["cycle_id"] == CYCLE_ID and result["track_id"] == CONSTRUCTOR_TRACK, "constructor result identity")
    require(result["frontier_sha256"] == file_digest(FRONTIER) and result["frontier_semantic_sha256"] == candidate["semantic_sha256"], "constructor result frontier binding")
    require(result["source_manifest_sha256"] == file_digest(CONSTRUCTOR_MANIFEST) and result["source_manifest_semantic_sha256"] == manifest["semantic_sha256"], "constructor result manifest binding")
    require(result["classification"] == candidate["classification"] and result["endpoint"] == TIMEOUT_ENDPOINT, "constructor result endpoint")
    require(result["standard_chart_count"] == 64 and result["charts_with_three_euler_recoveries"] == 64, "constructor result chart census")
    require(result["directed_overlap_record_count"] == 4032 and result["boundary_strata_discarded"] == 0, "constructor result overlap boundary")
    require(result["characteristic_zero_decomposition_completed"] is False and result["accepted_component_count"] == 0, "constructor result decomposition")
    require(result["accepted_affine_component_contractions"] == 0 and result["componentwise_parent_factor_tests_completed"] == 0, "constructor result downstream")
    require(result["theorem_ledger"] == OPENING_LEDGER and result["ledger_change_recommended"] == "none", "constructor result ledger")
    require(set(result["nonconsequences"]) == set(candidate["nonconsequences"]), "constructor result nonconsequences")
    return {
        "frontier_sha256": file_digest(FRONTIER),
        "frontier_semantic_sha256": candidate["semantic_sha256"],
        "manifest_sha256": file_digest(CONSTRUCTOR_MANIFEST),
        "manifest_semantic_sha256": manifest["semantic_sha256"],
        "result_sha256": file_digest(CONSTRUCTOR_RESULT),
    }


def hostile_mutations(candidate: dict, source: dict) -> list[dict]:
    tests = []

    def mutate(name: str, change) -> None:
        hostile = deepcopy(candidate)
        change(hostile)
        try:
            validate_candidate(hostile, source, verify_seals=False)
        except Reject as error:
            tests.append({"name": name, "rejected": True, "marker": str(error)})
        else:
            tests.append({"name": name, "rejected": False, "marker": "UNSOUND_ACCEPTANCE"})

    mutate("cycle identity drift", lambda value: value.__setitem__("cycle_id", "wrong-cycle"))
    mutate("constructor track drift", lambda value: value.__setitem__("track_id", "wrong-track"))
    mutate("base revision drift", lambda value: value.__setitem__("base_revision", "0" * 40))
    mutate("opening tree drift", lambda value: value.__setitem__("opening_tree", "0" * 40))
    mutate("trihomogeneous coefficient mutation", lambda value: value["trihomogeneous_source"]["polynomial"]["sparse_polynomial"][0].__setitem__("coefficient", 17))
    mutate("trihomogeneous multidegree mutation", lambda value: value["trihomogeneous_source"].__setitem__("multidegree", [2, 2, 3]))
    mutate("dehomogenization overclaim mutation", lambda value: value["trihomogeneous_source"].__setitem__("dehomogenization_exact_sparse_equality", False))
    mutate("trihomogenization decomposition overclaim", lambda value: value["trihomogeneous_source"].__setitem__("trihomogenization_is_decomposition_certificate", True))
    mutate("chart omission", lambda value: value["chart_atlas"]["charts"].pop())
    mutate("chart order mutation", lambda value: value["chart_atlas"]["chart_order"].reverse())
    mutate("chart pivot mutation", lambda value: value["chart_atlas"]["charts"][0]["pivots"].__setitem__(0, "b"))
    mutate("chart polynomial coefficient mutation", lambda value: value["chart_atlas"]["charts"][0]["F_chart"]["sparse_polynomial"][0].__setitem__("coefficient", 19))
    mutate("chart polynomial term omission", lambda value: value["chart_atlas"]["charts"][1]["F_chart"]["sparse_polynomial"].pop())
    mutate("free derivative coefficient mutation", lambda value: value["chart_atlas"]["charts"][2]["free_derivatives"][0]["sparse_polynomial"][0].__setitem__("coefficient", 23))
    mutate("free derivative omission", lambda value: value["chart_atlas"]["charts"][3]["free_derivatives"].pop())
    mutate("Jacobian generator count mutation", lambda value: value["chart_atlas"]["charts"][4]["chart_jacobian_ideal"].__setitem__("generator_count", 9))
    mutate("Euler direct specialization mutation", lambda value: value["chart_atlas"]["charts"][5]["euler_pivot_recoveries"][0]["direct_specialization"]["sparse_polynomial"][0].__setitem__("coefficient", 29))
    mutate("Euler reconstruction mutation", lambda value: value["chart_atlas"]["charts"][6]["euler_pivot_recoveries"][1]["euler_reconstruction"]["sparse_polynomial"][0].__setitem__("coefficient", 31))
    mutate("Euler nonzero residual", lambda value: value["chart_atlas"]["charts"][7]["euler_pivot_recoveries"][2]["exact_zero_residual"]["sparse_polynomial"].append({"exponents": [0] * 9, "coefficient": 1}))
    mutate("Euler recovery count mutation", lambda value: value["chart_atlas"]["charts"][8].__setitem__("euler_recovery_count", 2))
    mutate("full Jacobian transfer removal", lambda value: value["chart_atlas"]["charts"][9].__setitem__("full_projective_jacobian_transfer_proved", False))
    mutate("affine ideal equality removal", lambda value: value["affine_transfer"].__setitem__("chart_ideal_equals_original_affine_singular_ideal", False))
    mutate("affine chart tag mutation", lambda value: value["chart_atlas"].__setitem__("affine_chart_id", "JCH-00-a-d-g"))
    mutate("boundary divisor omission", lambda value: value["chart_atlas"]["charts"][0]["boundary_hyperplanes_available"].pop())
    mutate("boundary stratum omission", lambda value: value["chart_atlas"]["charts"][0]["boundary_strata"].pop())
    mutate("boundary incidence count mutation", lambda value: value["chart_atlas"].__setitem__("local_nonempty_boundary_intersection_record_count", 278))
    mutate("boundary discard overclaim", lambda value: value["decomposition_frontier"].__setitem__("boundary_strata_discarded", 1))
    mutate("overlap omission", lambda value: value["chart_atlas"]["charts"][0]["overlap_records"].pop())
    mutate("directed overlap count mutation", lambda value: value["chart_atlas"].__setitem__("directed_overlap_record_count", 4031))
    mutate("complete decomposition overclaim", lambda value: value["decomposition_frontier"].__setitem__("complete_projective_decomposition", True))
    mutate("accepted component overclaim", lambda value: value["decomposition_frontier"].__setitem__("accepted_component_count", 1))
    mutate("resolved chart overclaim", lambda value: value["decomposition_frontier"].__setitem__("resolved_chart_count", 1))
    mutate("embedded component discard", lambda value: value["decomposition_frontier"].__setitem__("embedded_components_discarded", 1))
    mutate("affine contraction overclaim", lambda value: value["affine_contraction_frontier"].__setitem__("accepted_affine_component_count", 1))
    mutate("contraction order violation", lambda value: value["affine_contraction_frontier"].__setitem__("order_respected", False))
    mutate("parent factor record omission", lambda value: value["parent_factor_incidence_frontier"]["records"].pop())
    mutate("component-parent test overclaim", lambda value: value["parent_factor_incidence_frontier"].__setitem__("completed_component_factor_pairs", 70))
    mutate("inverse-variable discovery route", lambda value: value["parent_factor_incidence_frontier"].__setitem__("inverse_variable_discovery_used", True))
    mutate("strict sign completion overclaim", lambda value: value["parent_factor_incidence_frontier"]["records"][0].__setitem__("strict_sign_status", "COMPLETE"))
    mutate("preserved stratum discard", lambda value: value["preserved_predecessor_strata"].__setitem__("strata_discarded", 1))
    mutate("positive endpoint overclaim", lambda value: value["endpoint_accounting"].__setitem__("positive", "REACHED"))
    mutate("timeout endpoint removal", lambda value: value["endpoint_accounting"].__setitem__("timeout", "NOT_REACHED"))
    mutate("numerical inference route", lambda value: value["resource_accounting"].__setitem__("numerical_or_modular_probe_used", True))
    mutate("connector scope drift", lambda value: value["resource_accounting"].__setitem__("network_or_connector_used", True))
    mutate("ledger promotion", lambda value: value.__setitem__("ledger_change_recommended", "promote"))
    mutate("ledger state drift", lambda value: value.__setitem__("theorem_ledger", "3/9"))

    require(len(tests) >= 24, "hostile test count")
    accepted = [record["name"] for record in tests if not record["rejected"]]
    require(not accepted, "hostile mutation acceptance: " + ", ".join(accepted))
    return tests


def build_source_manifest(source: dict, companions: dict) -> dict:
    pins = dict(PINNED_INPUTS)
    pins[FRONTIER.relative_to(ROOT).as_posix()] = companions["frontier_sha256"]
    pins[CONSTRUCTOR_MANIFEST.relative_to(ROOT).as_posix()] = companions["manifest_sha256"]
    pins[CONSTRUCTOR_RESULT.relative_to(ROOT).as_posix()] = companions["result_sha256"]
    pins[SOURCE_ARTIFACT.relative_to(ROOT).as_posix()] = file_digest(SOURCE_ARTIFACT)
    pins[Path(__file__).resolve().relative_to(ROOT).as_posix()] = FROZEN_VERIFIER_SHA256
    return seal({
        "format": "d9-factor19069-explicit-trihom-jacobian-chart-certificate-source-manifest-v1",
        "cycle_id": CYCLE_ID,
        "track_id": CERTIFICATE_TRACK,
        "base_revision": BASE_REVISION,
        "base_tree": BASE_TREE,
        "pins": dict(sorted(pins.items())),
        "independent_source_reconstruction_semantic_sha256": source["semantic_sha256"],
        "constructor_frontier_semantic_sha256": companions["frontier_semantic_sha256"],
        "constructor_manifest_semantic_sha256": companions["manifest_semantic_sha256"],
        "source_policy": {
            "constructor_code_imported": False,
            "constructor_acceptance_imported": False,
            "falsifier_code_imported": False,
            "predecessor_certificate_code_imported": False,
            "network_or_connector_used": False,
            "external_algebra_service_used": False,
            "numerical_or_modular_inference_used": False,
            "seventy_inverse_variable_discovery_used": False,
        },
    })


def build_result(candidate: dict, source: dict, verdict: dict, companions: dict, tests: list[dict], manifest: dict) -> dict:
    return seal({
        "format": "d9-factor19069-explicit-trihom-jacobian-chart-certificate-result-v1",
        "cycle_id": CYCLE_ID,
        "track_id": CERTIFICATE_TRACK,
        "constructor_frontier": FRONTIER.relative_to(ROOT).as_posix(),
        "constructor_frontier_sha256": companions["frontier_sha256"],
        "constructor_frontier_semantic_sha256": candidate["semantic_sha256"],
        "constructor_companions": companions,
        "source_reconstruction_sha256": file_digest(SOURCE_ARTIFACT),
        "source_reconstruction_semantic_sha256": source["semantic_sha256"],
        "source_manifest_semantic_sha256": manifest["semantic_sha256"],
        "classification": verdict["classification"],
        "certificate_gates": verdict,
        "hostile_tests": {
            "required": 24,
            "run": len(tests),
            "rejected": sum(record["rejected"] for record in tests),
        },
        "outcome": "pass",
        "endpoint": TIMEOUT_ENDPOINT,
        "positive_endpoint_reached": False,
        "negative_endpoint_reached": False,
        "null_endpoint_reached": False,
        "timeout_endpoint_reached": True,
        "ledger_before": OPENING_LEDGER,
        "ledger_after": OPENING_LEDGER,
        "ledger_delta": LEDGER_DELTA,
        "ledger_change_recommended": "none",
        "nonconsequences": candidate["nonconsequences"],
    })


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source-only", action="store_true")
    parser.add_argument("--no-write", action="store_true")
    arguments = parser.parse_args()
    independence_audit()
    source = reconstruct_source()
    if not arguments.no_write:
        write_json(SOURCE_ARTIFACT, source)
    print("PASS independent exact source and 64-chart reconstruction")
    print(f"charts: {source['chart_cover']['standard_chart_count']}; Euler identities: 192")
    print("boundary chart histogram: 0:1, 1:9, 2:27, 3:27")
    if arguments.source_only:
        return 0
    require(FRONTIER.is_file(), "constructor frontier exists")
    candidate = read_json(FRONTIER)
    verdict = validate_candidate(candidate, source)
    companions = validate_constructor_companions(candidate)
    tests = hostile_mutations(candidate, source)
    manifest = build_source_manifest(source, companions)
    result = build_result(candidate, source, verdict, companions, tests, manifest)
    if not arguments.no_write:
        write_json(SOURCE_MANIFEST, manifest)
        write_json(HOSTILE_ARTIFACT, seal({
            "format": "d9-factor19069-explicit-trihom-jacobian-chart-certificate-hostile-tests-v1",
            "cycle_id": CYCLE_ID,
            "track_id": CERTIFICATE_TRACK,
            "tests": tests,
        }))
        write_json(RESULT, result)
        FINDINGS.write_text(
            "# Producer-independent explicit trihomogeneous chart certificate\n\n"
            "Verdict: **accepted exact 64-chart reconstruction with a fail-closed timeout frontier**.\n\n"
            "The frozen 108-term affine factor was independently rebuilt from the critical-equidimensional predecessor. "
            "Its canonical 12-variable trihomogenization has exact multidegree `(2,2,2)` and dehomogenizes term-for-term "
            "to `f_19069`; this equality is not treated as a decomposition certificate.\n\n"
            "All 64 standard product charts were independently reconstructed.  Every chart has `F_chart` plus its nine "
            "free-coordinate derivatives, and all 192 pivot-derivative Euler identities have zero sparse residual.  The "
            "`u=v=w=1` chart equals the original affine ten-generator singular ideal exactly.  The certificate also checked "
            "all 4,032 directed overlap tags.\n\n"
            "Boundary is divisor-local, not a chart-level infinity label.  There is one affine pivot chart, 63 charts that "
            "admit at least one boundary divisor, 144 boundary-divisor/chart incidences, seven global nonempty boundary types, "
            "and 279 chart-local nonempty boundary-stratum records.  None was discarded.\n\n"
            "The first chart's characteristic-zero Groebner prerequisite hit the recorded 20-second wall ceiling.  Therefore "
            "no chart decomposition, embedded-component census, overlap-deduplicated component list, affine contraction, "
            "componentwise 70-factor test, strict-real residence result, or connected row-2599 parent tag is certified.  "
            f"All {len(tests)} substantive hostile mutations were rejected.  The theorem ledger remains `2/9` with delta `0/9`.\n",
            encoding="utf-8",
        )
    print("PASS producer-independent explicit trihomogeneous chart certificate")
    print(f"hostile mutations rejected: {len(tests)}/{len(tests)}")
    print("ledger: 2/9 -> 2/9")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (Reject, KeyError, TypeError, ValueError, json.JSONDecodeError) as error:
        print(f"FAIL: {error}", file=sys.stderr)
        raise SystemExit(1)
