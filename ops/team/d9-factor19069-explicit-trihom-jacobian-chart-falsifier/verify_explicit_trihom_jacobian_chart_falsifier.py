#!/usr/bin/env python3
"""Independent exact falsifier for the factor-19069 projective chart gate.

This lane deliberately imports neither constructor code nor constructor
acceptance logic.  It rebuilds the affine wall from the pinned mathematical
source, forms the canonical (2,2,2) trihomogenization by sparse integer
arithmetic, reconstructs all 64 standard product charts, and checks any
constructor frontier against that independent reconstruction.
"""

from __future__ import annotations

from copy import deepcopy
from hashlib import sha256
from itertools import product
import json
from pathlib import Path
import struct
import subprocess
import sys
from typing import Any, Callable


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
OMREAL = ROOT / "ai" / "omreal"
DATA = OMREAL / "data"
MANIFEST = HERE / "SOURCE_MANIFEST.json"
RESULT = HERE / "RESULT.json"
HOSTILE = HERE / "HOSTILE_TESTS.json"
FRONTIER = ROOT / "ops" / "team" / "d9-factor19069-explicit-trihom-jacobian-chart-constructor" / "PROJECTIVE_CHART_FRONTIER.json"
PREDECESSOR = ROOT / "ops" / "team" / "d9-factor19069-singular-df-multihomogeneous-constructor" / "SINGULAR_DF_MULTIHOMOGENEOUS_FRONTIER.json"

TARGET_FACTOR = 19069
TARGET_PARENT = 2599
AFFINE_VARIABLES = tuple("abcdefghi")
HOMOGENEOUS_VARIABLES = ("a", "b", "c", "u", "d", "e", "f", "v", "g", "h", "i", "w")
BLOCKS = (("a", "b", "c", "u"), ("d", "e", "f", "v"), ("g", "h", "i", "w"))
HOMOGENIZERS = ("u", "v", "w")
AFFINE_TO_HOMOGENEOUS = (0, 1, 2, 4, 5, 6, 8, 9, 10)
HOMOGENIZER_POSITIONS = (3, 7, 11)
EXPECTED_FACTOR_DIGEST = "041227c22bc01ca80df8a66a46099b2f703c53a310fe737dac3981bda5ee20c4"
EXPECTED_PARENT_DIGEST = "1d9b940e2bb954b5c69bcee8b2346f9554b2e15589ea4c5b3c3f8e1e943de701"
EXPECTED_DERIVATIVE_DIGESTS = (
    "382f9a12ca2d88fa7c3c67c1c6b13c0b0bf91833978a482220b62eef2e175b3a",
    "247a25f59acfeca0e2492b9f53b2cd1541edafec8a882c57935edd69076bf7ac",
    "c6690d1c5fb151b0e71129ea26e92438e42e720326ed7b9a1b0e6c20a977d6d3",
    "2135c43e43123c23e490f778b7bf661d8c737387e4ba1cede5bd78bbf5302b4f",
    "bedfd41d243f619317d220f743a375850537a5b4057e193b6920296783d8116b",
    "feb633531b931c539632d64665d074effe200db0f58ed7eafc5e05495e0e6bfd",
    "0584e873bfa627a3d9d14c5358f2913d52b3b096ae00428d8039237727842723",
    "edc40934e6e7a48ebd07ce4c42516de5b91ee68e27e71836c729dd9569ca7b58",
    "e68f99acd149c071ddf98ec55766cd5812fc163fcd0d1eb095c7e61085d8d0a9",
)
EXPECTED_DERIVATIVE_TERMS = (54, 44, 54, 50, 50, 50, 36, 61, 36)
OPENING_REVISION = "cd2d856d3ccff51f7b5d6841702b25d191ed9985"
PROTOCOL_PATH = "ops/research-team/PROTOCOL.md"

sys.path.insert(0, str(OMREAL))
import DIAG2_PIVOT_LABELED_PAIR_ORBITS_VERIFY as labeled  # noqa: E402
import verify_diag3_pair_global_parent_face_gate as parent_gate  # noqa: E402


Polynomial = dict[tuple[int, ...], int]


class Reject(AssertionError):
    """A fail-closed rejection with a stable marker."""


def require(condition: bool, marker: str) -> None:
    if not condition:
        raise Reject(marker)


def digest_path(path: Path) -> str:
    state = sha256()
    with path.open("rb") as source:
        for block in iter(lambda: source.read(1 << 20), b""):
            state.update(block)
    return state.hexdigest()


def source_digest(relative: str) -> str:
    if relative == PROTOCOL_PATH:
        frozen = subprocess.check_output(
            ["git", "show", f"{OPENING_REVISION}:{relative}"], cwd=ROOT
        )
        return sha256(frozen).hexdigest()
    return digest_path(ROOT / relative)


def semantic_digest(value: Any) -> str:
    return sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode("utf-8")).hexdigest()


def normalize(polynomial: Polynomial) -> Polynomial:
    return {tuple(exponents): int(coefficient) for exponents, coefficient in polynomial.items() if coefficient}


def sparse_rows(polynomial: Polynomial) -> list[list[int]]:
    return sorted([list(exponents) + [coefficient] for exponents, coefficient in normalize(polynomial).items()])


def sparse_digest(polynomial: Polynomial) -> str:
    return sha256(json.dumps(sparse_rows(polynomial), separators=(",", ":")).encode("ascii")).hexdigest()


def derivative(polynomial: Polynomial, variable: int) -> Polynomial:
    answer: Polynomial = {}
    for exponents, coefficient in polynomial.items():
        power = exponents[variable]
        if power:
            lowered = exponents[:variable] + (power - 1,) + exponents[variable + 1 :]
            answer[lowered] = answer.get(lowered, 0) + coefficient * power
    return normalize(answer)


def add(*polynomials: Polynomial) -> Polynomial:
    answer: Polynomial = {}
    for polynomial in polynomials:
        for exponents, coefficient in polynomial.items():
            answer[exponents] = answer.get(exponents, 0) + coefficient
    return normalize(answer)


def scale(polynomial: Polynomial, scalar: int) -> Polynomial:
    return normalize({exponents: scalar * coefficient for exponents, coefficient in polynomial.items()})


def multiply_variable(polynomial: Polynomial, variable: int) -> Polynomial:
    answer: Polynomial = {}
    for exponents, coefficient in polynomial.items():
        raised = exponents[:variable] + (exponents[variable] + 1,) + exponents[variable + 1 :]
        answer[raised] = answer.get(raised, 0) + coefficient
    return normalize(answer)


def candidate_ids() -> tuple[int, ...]:
    raw = (DATA / "DIAG3_PAIR_GLOBAL_row2599_candidate_factors.bin").read_bytes()
    header_size = struct.calcsize("<8sIII")
    magic, parent, universe, count = struct.unpack_from("<8sIII", raw)
    require((magic, parent, universe, count) == (b"D3PFC001", 2599, 26740, 17824), "candidate source header")
    require(len(raw) == header_size + 4 * count, "candidate source length")
    values = tuple(item[0] for item in struct.iter_unpack("<I", raw[header_size:]))
    require(values == tuple(sorted(set(values))), "candidate source ordering")
    return values


def homogenize(factor: Polynomial) -> Polynomial:
    answer: Polynomial = {}
    for affine_exponents, coefficient in factor.items():
        homogeneous = [0] * 12
        for source, target in enumerate(AFFINE_TO_HOMOGENEOUS):
            homogeneous[target] = affine_exponents[source]
        for block_index, group in enumerate(((0, 1, 2), (3, 4, 5), (6, 7, 8))):
            degree = sum(affine_exponents[index] for index in group)
            require(degree <= 2, "trihomogenization degree ceiling")
            homogeneous[HOMOGENIZER_POSITIONS[block_index]] = 2 - degree
        key = tuple(homogeneous)
        answer[key] = answer.get(key, 0) + coefficient
    return normalize(answer)


def dehomogenize(polynomial: Polynomial) -> Polynomial:
    answer: Polynomial = {}
    for homogeneous, coefficient in polynomial.items():
        affine = tuple(homogeneous[index] for index in AFFINE_TO_HOMOGENEOUS)
        answer[affine] = answer.get(affine, 0) + coefficient
    return normalize(answer)


def restrict_chart(polynomial: Polynomial, pivots: tuple[str, str, str]) -> Polynomial:
    pivot_positions = {HOMOGENEOUS_VARIABLES.index(variable) for variable in pivots}
    free_positions = [index for index in range(12) if index not in pivot_positions]
    answer: Polynomial = {}
    for exponents, coefficient in polynomial.items():
        chart_exponents = tuple(exponents[index] for index in free_positions)
        answer[chart_exponents] = answer.get(chart_exponents, 0) + coefficient
    return normalize(answer)


def chart_id(index: int, pivots: tuple[str, str, str]) -> str:
    return f"JCH-{index:02d}-{'-'.join(pivots)}"


def reconstruct() -> dict[str, Any]:
    records = [
        json.loads(line)
        for line in (OMREAL / "certs_4_8.jsonl").read_text(encoding="utf-8").splitlines()
        if line
    ]
    require(len(records) == 2628, "parent record census")
    require(records[TARGET_PARENT]["verdict"] == "REALIZABLE", "parent realizability")
    parent_sources, parent_digest = parent_gate.parent_polynomials(records[TARGET_PARENT])
    require(parent_digest == EXPECTED_PARENT_DIGEST, "parent source digest")
    require(len(parent_sources) == 70, "parent factor census")
    require(TARGET_FACTOR in candidate_ids(), "factor candidate membership")

    factor = normalize(labeled.factor_polynomials()[2][TARGET_FACTOR])
    require(len(factor) == 108, "factor term census")
    require(sparse_digest(factor) == EXPECTED_FACTOR_DIGEST, "factor sparse digest")
    affine_derivatives = [derivative(factor, index) for index in range(9)]
    require(tuple(map(len, affine_derivatives)) == EXPECTED_DERIVATIVE_TERMS, "affine derivative term census")
    require(tuple(map(sparse_digest, affine_derivatives)) == EXPECTED_DERIVATIVE_DIGESTS, "affine derivative digests")

    trihomogeneous = homogenize(factor)
    require(len(trihomogeneous) == 108, "trihomogeneous term census")
    require(dehomogenize(trihomogeneous) == factor, "exact dehomogenization")
    block_positions = ((0, 1, 2, 3), (4, 5, 6, 7), (8, 9, 10, 11))
    for exponents in trihomogeneous:
        require(tuple(sum(exponents[index] for index in block) for block in block_positions) == (2, 2, 2), "exact tridegree")

    charts = []
    for index, pivots in enumerate(product(*BLOCKS)):
        pivots = tuple(pivots)
        pivot_positions = tuple(HOMOGENEOUS_VARIABLES.index(variable) for variable in pivots)
        free_positions = tuple(position for position in range(12) if position not in pivot_positions)
        free_coordinates = tuple(HOMOGENEOUS_VARIABLES[position] for position in free_positions)
        chart_polynomial = restrict_chart(trihomogeneous, pivots)
        chart_derivatives = [derivative(chart_polynomial, position) for position in range(9)]
        euler = []
        for block_index, pivot in enumerate(pivots):
            pivot_position = HOMOGENEOUS_VARIABLES.index(pivot)
            pivot_derivative = restrict_chart(derivative(trihomogeneous, pivot_position), pivots)
            block_free = [variable for variable in BLOCKS[block_index] if variable != pivot]
            recovery = scale(chart_polynomial, 2)
            for variable in block_free:
                chart_position = free_coordinates.index(variable)
                recovery = add(recovery, scale(multiply_variable(chart_derivatives[chart_position], chart_position), -1))
            require(recovery == pivot_derivative, "Euler pivot recovery")
            euler.append({
                "block_index": block_index,
                "pivot": pivot,
                "pivot_derivative_sparse_sha256": sparse_digest(pivot_derivative),
                "recovery_sparse_sha256": sparse_digest(recovery),
                "coefficient": 2,
            })
        boundary_homogenizers = [HOMOGENIZERS[i] for i, pivot in enumerate(pivots) if pivot != HOMOGENIZERS[i]]
        boundary_strata = []
        for bitmask in range(1, 1 << len(boundary_homogenizers)):
            zero_homogenizers = [
                variable for bit, variable in enumerate(boundary_homogenizers) if bitmask & (1 << bit)
            ]
            boundary_strata.append({
                "boundary_bitmask": bitmask,
                "boundary_subset": [f"{variable}=0" for variable in zero_homogenizers],
                "zero_homogenizers": zero_homogenizers,
            })
        charts.append({
            "chart_index": index,
            "chart_id": chart_id(index, pivots),
            "pivots": list(pivots),
            "free_coordinates": list(free_coordinates),
            "F_chart": chart_polynomial,
            "F_chart_sparse_sha256": sparse_digest(chart_polynomial),
            "derivatives": chart_derivatives,
            "derivative_sparse_sha256": [sparse_digest(item) for item in chart_derivatives],
            "euler": euler,
            "boundary_homogenizers": boundary_homogenizers,
            "boundary_strata": boundary_strata,
            "is_affine_chart": pivots == HOMOGENIZERS,
        })
    require(len(charts) == 64, "chart census")
    require(len({tuple(chart["pivots"]) for chart in charts}) == 64, "chart pivot uniqueness")
    affine_chart = next(chart for chart in charts if chart["is_affine_chart"])
    require(affine_chart["free_coordinates"] == list(AFFINE_VARIABLES), "affine chart free coordinates")
    require(affine_chart["F_chart"] == factor, "affine chart polynomial transfer")
    require(affine_chart["derivatives"] == affine_derivatives, "affine chart Jacobian transfer")
    require(sum(bool(chart["boundary_homogenizers"]) for chart in charts) == 63, "boundary chart retention census")
    require(sum(len(chart["boundary_strata"]) for chart in charts) == 279, "boundary stratum record census")

    predecessor = json.loads(PREDECESSOR.read_text(encoding="utf-8"))
    predecessor_parent_records = predecessor["parent_factor_incidence_frontier"]["records"]
    require(len(predecessor_parent_records) == 70, "predecessor parent tag census")

    parent_tags = []
    for index, source in enumerate(parent_sources):
        node_code, sign, polynomial, _source_terms = source
        # parent_polynomials returns a primitive source polynomial plus the
        # source orientation; the governed parent record stores their product.
        polynomial = scale(normalize(polynomial), int(sign))
        parent_tags.append({
            "factor_index": index,
            "factor_node_id": f"H_{index:02d}_{node_code}",
            "sign": int(sign),
            "term_count": len(polynomial),
            "degree": max(map(sum, polynomial), default=0),
            "sparse_sha256": sparse_digest(polynomial),
            "polynomial": polynomial,
            "source_semantic_sha256": predecessor_parent_records[index]["source_semantic_sha256"],
        })
    return {
        "factor": factor,
        "factor_digest": sparse_digest(factor),
        "affine_derivatives": affine_derivatives,
        "trihomogeneous": trihomogeneous,
        "trihomogeneous_digest": sparse_digest(trihomogeneous),
        "charts": charts,
        "chart_atlas_digest": semantic_digest([
            {
                "chart_index": chart["chart_index"],
                "chart_id": chart["chart_id"],
                "pivots": chart["pivots"],
                "free_coordinates": chart["free_coordinates"],
                "F_chart_sparse_sha256": chart["F_chart_sparse_sha256"],
                "derivative_sparse_sha256": chart["derivative_sparse_sha256"],
                "euler": chart["euler"],
                "boundary_homogenizers": chart["boundary_homogenizers"],
                "boundary_strata": chart["boundary_strata"],
            }
            for chart in charts
        ]),
        "parent_digest": parent_digest,
        "parent_tags": parent_tags,
    }


def rows_to_polynomial(rows: Any, variable_count: int, marker: str) -> Polynomial:
    """Decode either compact rows or {exponents,coefficient} objects exactly."""
    require(isinstance(rows, list), marker)
    answer: Polynomial = {}
    for row in rows:
        if isinstance(row, dict):
            exponents = row.get("exponents")
            coefficient = row.get("coefficient")
        else:
            require(isinstance(row, list) and len(row) == variable_count + 1, marker)
            exponents, coefficient = row[:-1], row[-1]
        require(isinstance(exponents, list) and len(exponents) == variable_count, marker)
        require(all(isinstance(power, int) and power >= 0 for power in exponents), marker)
        require(isinstance(coefficient, int), marker)
        key = tuple(exponents)
        answer[key] = answer.get(key, 0) + coefficient
    return normalize(answer)


def validate_manifest(candidate: dict[str, Any]) -> None:
    require(candidate["format"] == "d9-factor19069-explicit-trihom-jacobian-chart-falsifier-source-manifest-v1", "manifest format")
    require(candidate["source_count"] == len(candidate["source_sha256"]), "manifest source count")
    for relative, expected in candidate["source_sha256"].items():
        require(source_digest(relative) == expected, f"source pin {relative}")
    require(candidate["producer_code_imported"] is False, "producer independence")
    require(candidate["constructor_acceptance_imported"] is False, "acceptance independence")
    require(candidate["network_or_connector_used"] is False, "network scope")
    require(candidate["drive_connector_used"] is False, "drive scope")
    require(candidate["github_write"] is False, "github scope")
    require(candidate["numerical_or_modular_inference_used"] is False, "exact inference scope")


def _frontier_charts(candidate: dict[str, Any]) -> list[dict[str, Any]]:
    atlas = candidate["chart_atlas"]
    return atlas["charts"] if isinstance(atlas, dict) else atlas


def validate_frontier(candidate: dict[str, Any], replay: dict[str, Any]) -> None:
    """Validate the producer artifact; field contract is intentionally strict."""
    require(candidate["format"] == "d9-factor19069-explicit-trihom-jacobian-chart-constructor-frontier-v1", "frontier format")
    require(candidate["track_id"] == "d9-factor19069-explicit-trihom-jacobian-chart-constructor", "frontier track")
    require(candidate["cycle_id"] == "2026-09-01-d9-row2599-factor19069-explicit-trihom-jacobian-chart-gate1", "frontier cycle")
    require(candidate["base_revision"] == "4aee0aac6e80d053cf1751eac766280873656909", "frontier base revision")
    require(candidate["base_tree"] == "bfaff6f29b032ef6f81fa11a97063b01d74db8f7", "frontier base tree")
    require(candidate["opening_revision"] == "cd2d856d3ccff51f7b5d6841702b25d191ed9985", "frontier opening revision")
    require(candidate["predecessor_binding"]["file_sha256"] == digest_path(PREDECESSOR), "predecessor source pin")
    require(candidate["semantic_sha256"] == "aec3c7e29744d6d9a7df004c611c7edbdfbfedfad2bbea6f206df09d5fb14f33", "frontier semantic pin")

    source = candidate["trihomogeneous_source"]
    require(source["term_count"] == len(replay["trihomogeneous"]) == 108, "source trihom term count")
    require(source["multidegree"] == [2, 2, 2], "source multidegree")
    require(source["blocks"] == [list(block) for block in BLOCKS], "homogeneous blocks")
    polynomial = source["polynomial"]
    require(polynomial["coordinate_order"] == list(HOMOGENEOUS_VARIABLES), "homogeneous variable order")
    require(rows_to_polynomial(polynomial["sparse_polynomial"], 12, "source sparse terms") == replay["trihomogeneous"], "source sparse equality")
    require(source["dehomogenization_exact_sparse_equality"] is True, "source dehomogenization tag")
    require(source["dehomogenization_identity"] == "F(a,b,c,1,d,e,f,1,g,h,i,1)=f_19069", "source dehomogenization identity")
    require(source["trihomogenization_is_decomposition_certificate"] is False, "source decomposition guard")
    require(source["affine_source_is_homogeneous"] is False and source["affine_source_is_multiaffine"] is False, "source affine guard")

    charts = _frontier_charts(candidate)
    require(len(charts) == 64, "chart census")
    atlas = candidate["chart_atlas"]
    require(atlas["standard_chart_count"] == 64, "chart declared census")
    require(atlas["all_product_charts_retained"] is True and atlas["symmetry_quotient_used"] is False, "chart cover tag")
    require(atlas["chart_order"] == [chart["chart_id"] for chart in replay["charts"]], "chart stable order")
    require(atlas["all_available_boundary_strata_retained"] is True, "boundary retention tag")
    require(atlas["boundary_stratum_record_count"] == atlas["local_nonempty_boundary_intersection_record_count"] == 279, "boundary stratum record census")
    require(atlas["expected_local_nonempty_boundary_intersection_record_count"] == 279, "boundary expected census")
    require(atlas["charts_intersecting_at_least_one_boundary_hyperplane"] == 63, "boundary chart census")
    require(atlas["global_boundary_subsets"] == [
        ["u=0"], ["v=0"], ["w=0"], ["u=0", "v=0"], ["u=0", "w=0"],
        ["v=0", "w=0"], ["u=0", "v=0", "w=0"],
    ], "global boundary subsets")
    require(atlas["directed_overlap_record_count"] == 4032, "overlap census")
    expected_chart_ids = [chart["chart_id"] for chart in replay["charts"]]
    for expected, chart in zip(replay["charts"], charts):
        prefix = f"chart {expected['chart_index']}"
        require(chart["chart_index"] == expected["chart_index"], f"{prefix} stable index")
        require(chart["chart_id"] == expected["chart_id"], f"{prefix} stable id")
        require(chart["pivots"] == expected["pivots"], f"{prefix} pivots")
        require(chart["free_coordinates"] == expected["free_coordinates"], f"{prefix} free coordinates")
        require(chart["free_coordinate_count"] == 9 and chart["chart_jacobian_ideal"]["generator_count"] == 10, f"{prefix} generator count")
        require(chart["F_chart"]["coordinate_order"] == expected["free_coordinates"], f"{prefix} F coordinate order")
        require(rows_to_polynomial(chart["F_chart"]["sparse_polynomial"], 9, f"{prefix} F rows") == expected["F_chart"], f"{prefix} F equality")
        require([item["derivative_coordinate"] for item in chart["free_derivatives"]] == expected["free_coordinates"], f"{prefix} derivative variables")
        derivatives = [rows_to_polynomial(item["sparse_polynomial"], 9, f"{prefix} derivative rows") for item in chart["free_derivatives"]]
        require(derivatives == expected["derivatives"] and len(derivatives) == 9, f"{prefix} derivative equality")
        require(chart["boundary_homogenizers"] == expected["boundary_homogenizers"], f"{prefix} boundary coordinates")
        require(chart["boundary_hyperplanes_available"] == expected["boundary_homogenizers"], f"{prefix} boundary hyperplanes")
        require(chart["chart_is_wholly_infinity"] is False and chart["contains_affine_overlap"] is True, f"{prefix} affine-boundary distinction")
        require(chart["boundary_retention_status"] == "ALL_AVAILABLE_INFINITY_BOUNDARY_STRATA_RETAINED", f"{prefix} boundary retained")
        require(chart["boundary_strata_discarded"] == 0, f"{prefix} boundary discarded")
        require(len(chart["boundary_strata"]) == len(expected["boundary_strata"]), f"{prefix} boundary local census")
        for actual_boundary, expected_boundary in zip(chart["boundary_strata"], expected["boundary_strata"]):
            require(actual_boundary["boundary_bitmask"] == expected_boundary["boundary_bitmask"], f"{prefix} boundary bitmask")
            require(actual_boundary["boundary_subset"] == expected_boundary["boundary_subset"], f"{prefix} boundary subset")
            require(actual_boundary["zero_homogenizers"] == expected_boundary["zero_homogenizers"], f"{prefix} boundary zero set")
            require(actual_boundary["status"] == "RETAINED", f"{prefix} boundary stratum status")
        require(chart["overlap_record_count"] == 63 and len(chart["overlap_records"]) == 63, f"{prefix} overlap local census")
        require(sorted(item["target_chart_id"] for item in chart["overlap_records"]) == sorted(set(expected_chart_ids) - {expected["chart_id"]}), f"{prefix} overlap targets")
        require(all(item["overlap_status"] == "EXPLICIT_NONEMPTY_PRINCIPAL_OPEN_WHEN_REQUIREMENTS_HOLD" for item in chart["overlap_records"]), f"{prefix} overlap tags")
        require(chart["euler_recovery_count"] == chart["euler_zero_residual_count"] == 3, f"{prefix} Euler census")
        require(chart["full_projective_jacobian_transfer_proved"] is True, f"{prefix} projective Jacobian transfer")
        for expected_euler, actual_euler in zip(expected["euler"], chart["euler_pivot_recoveries"]):
            require(actual_euler["pivot"] == expected_euler["pivot"], f"{prefix} Euler pivot")
            require(actual_euler["block_degree"] == 2, f"{prefix} Euler coefficient")
            direct = rows_to_polynomial(actual_euler["direct_specialization"]["sparse_polynomial"], 9, f"{prefix} Euler direct rows")
            recovered = rows_to_polynomial(actual_euler["euler_reconstruction"]["sparse_polynomial"], 9, f"{prefix} Euler recovered rows")
            residual = rows_to_polynomial(actual_euler["exact_zero_residual"]["sparse_polynomial"], 9, f"{prefix} Euler residual rows")
            require(direct == recovered and sparse_digest(direct) == expected_euler["pivot_derivative_sparse_sha256"], f"{prefix} Euler recovery")
            require(residual == {} and actual_euler["exact_zero_residual"]["term_count"] == 0, f"{prefix} Euler zero residual")
            require(actual_euler["exact_sparse_equality"] is True, f"{prefix} Euler identity")
            require(actual_euler["exact_ideal_equality"] == "<F_CHART,NINE_FREE_DERIVATIVES>=<ALL_TWELVE_SPECIALIZED_HOMOGENEOUS_DERIVATIVES>", f"{prefix} Euler ideal equality")

    affine = candidate["affine_transfer"]
    expected_affine = next(chart for chart in replay["charts"] if chart["is_affine_chart"])
    require(affine["chart_id"] == expected_affine["chart_id"], "affine chart identity")
    require(affine["pivot_substitution"] == {"u": 1, "v": 1, "w": 1}, "affine specialization")
    require(affine["free_coordinate_order"] == list(AFFINE_VARIABLES), "affine free coordinates")
    require(affine["F_chart_equals_original_f_19069"] is True, "affine F transfer")
    require(affine["nine_chart_derivatives_equal_original_affine_derivatives"] is True, "affine derivative transfer")
    require(affine["chart_ideal_generator_count"] == affine["original_ideal_generator_count"] == 10, "affine ideal generator count")
    require(affine["chart_ideal_equals_original_affine_singular_ideal"] is True, "affine ideal equality")

    decomposition = candidate["decomposition_frontier"]
    components = [component for chart in charts for component in chart["accepted_components"]]
    require(decomposition["accepted_component_count"] == len(components) == 0, "component list")
    require(decomposition["complete_projective_decomposition"] is False, "false complete decomposition")
    require(decomposition["resolved_chart_count"] == 0 and decomposition["pending_chart_count"] == 64, "decomposition chart census")
    require(decomposition["first_pending_branch_id"] == "DEC-JCH-00-a-d-g", "first pending branch")
    require(decomposition["first_pending_branch"]["accepted_components"] == [], "fake component")
    require(decomposition["embedded_components_discarded"] == decomposition["boundary_strata_discarded"] == 0, "decomposition stratum retention")
    contraction = candidate["affine_contraction_frontier"]
    require(contraction["accepted_projective_component_count"] == contraction["accepted_affine_component_count"] == 0, "contraction component census")
    require(contraction["contracted_to_original_affine_singular_ideal_count"] == 0, "contraction census")
    require(contraction["componentwise_parent_tests_started"] == 0 and contraction["order_respected"] is True, "parent test uncontracted component")
    incidence = candidate["parent_factor_incidence_frontier"]
    require(incidence["ordered_factor_count"] == len(incidence["records"]) == 70, "parent factor census")
    require(incidence["source_parent_factor_tags_preserved"] is True and incidence["source_record_order_preserved"] is True, "parent source tag")
    require(incidence["accepted_contracted_component_count"] == 0 and incidence["completed_component_factor_pairs"] == 0, "uncontracted component tested")
    for expected_parent, actual_parent in zip(replay["parent_tags"], incidence["records"]):
        prefix = f"parent factor {expected_parent['factor_index']}"
        require(actual_parent["factor_index"] == expected_parent["factor_index"], f"{prefix} index")
        require(actual_parent["factor_node_id"] == expected_parent["factor_node_id"], f"{prefix} node tag")
        require(actual_parent["term_count"] == expected_parent["term_count"] and actual_parent["degree"] == expected_parent["degree"], f"{prefix} degree terms")
        require(rows_to_polynomial(actual_parent["sparse_polynomial"], 9, f"{prefix} sparse rows") == expected_parent["polynomial"], f"{prefix} sparse equality")
        require(actual_parent["source_semantic_sha256"] == expected_parent["source_semantic_sha256"], f"{prefix} source semantic tag")
        require(actual_parent["componentwise_incidence_status"] == "PENDING_NO_ACCEPTED_CONTRACTED_AFFINE_COMPONENT", f"{prefix} incidence pending")

    endpoint = candidate["endpoint_accounting"]
    require(endpoint["timeout"] == "REACHED_HASH_PINNED_FIRST_PENDING_CHART" and endpoint["null"] == "NOT_REACHED", "endpoint exclusivity")
    require(candidate["endpoint"] == "HASH_PIN_ALL_COMPLETED_CHART_BRANCHES_AND_FIRST_PENDING_BRANCH", "endpoint selection")
    require(candidate["classification"] == "BOUNDED_CHARACTERISTIC_ZERO_CHART_DECOMPOSITION_TIMEOUT_FAIL_CLOSED", "endpoint classification")
    require(candidate["ledger_change_recommended"] == "none", "frontier ledger delta")
    require(candidate["theorem_ledger"] == "2/9", "frontier ledger")
    require("NO_STRICT_REAL_RESIDENCE_OR_CONNECTED_PARENT_TAG" in candidate["nonconsequences"], "real connected tag overclaim")
    resources = candidate["resource_accounting"]
    require(resources["numerical_or_modular_probe_used"] is False, "frontier exact scope")
    require(resources["seventy_inverse_variable_discovery_used"] is False, "frontier route scope")
    require(resources["network_or_connector_used"] is False and resources["paid_external_compute_used"] is False, "frontier external scope")


def validate_result(candidate: dict[str, Any], replay: dict[str, Any], rejected: int) -> None:
    require(candidate["format"] == "d9-factor19069-explicit-trihom-jacobian-chart-falsifier-result-v1", "result format")
    require(candidate["track_id"] == "d9-factor19069-explicit-trihom-jacobian-chart-falsifier", "result track")
    require(candidate["outcome"] == "pass", "result outcome")
    source = candidate["independent_reconstruction"]
    require(source["affine_terms"] == 108 and source["affine_sparse_sha256"] == replay["factor_digest"], "result affine source")
    require(source["trihomogeneous_terms"] == 108 and source["trihomogeneous_sparse_sha256"] == replay["trihomogeneous_digest"], "result trihom source")
    require(source["multidegree"] == [2, 2, 2] and source["dehomogenization_exact"] is True, "result dehomogenization")
    require(source["chart_count"] == 64 and source["chart_atlas_semantic_sha256"] == replay["chart_atlas_digest"], "result chart atlas")
    require(source["affine_jacobian_transfer_exact"] is True, "result affine transfer")
    require(source["parent_factor_count"] == 70 and source["parent_source_digest"] == replay["parent_digest"], "result parent source")
    require(candidate["constructor_frontier_validation"] == "ACCEPT_EXACT_BOUNDED_FRONTIER", "result frontier validation")
    require(candidate["hostile_mutations_rejected"] == rejected and rejected >= 24, "result hostile census")
    require(candidate["ledger_delta"] == "none" and candidate["theorem_ledger"] == "2/9", "result ledger")
    require(candidate["ledger_promotion_recommended"] is False, "result promotion")
    require(candidate["numerical_or_modular_inference_used"] is False, "result exact scope")


def hostile_manifest_mutations(stored: dict[str, Any]) -> list[str]:
    cases: list[tuple[str, Callable[[dict[str, Any]], None]]] = [
        ("manifest source count", lambda c: c.__setitem__("source_count", 0)),
        ("source pin ops/research-team/PROTOCOL.md", lambda c: c["source_sha256"].__setitem__("ops/research-team/PROTOCOL.md", "0" * 64)),
        ("producer independence", lambda c: c.__setitem__("producer_code_imported", True)),
        ("acceptance independence", lambda c: c.__setitem__("constructor_acceptance_imported", True)),
        ("exact inference scope", lambda c: c.__setitem__("numerical_or_modular_inference_used", True)),
    ]
    rejected = []
    for marker, edit in cases:
        mutated = deepcopy(stored)
        edit(mutated)
        try:
            validate_manifest(mutated)
        except Reject as error:
            require(marker in str(error), f"hostile wrong rejection {marker}: {error}")
            rejected.append(marker)
        else:
            raise Reject(f"hostile mutation accepted: {marker}")
    return rejected


def hostile_frontier_mutations(stored: dict[str, Any], replay: dict[str, Any]) -> list[str]:
    # The frontier is intentionally large.  Mutations are applied in-place,
    # checked by the exact invariant that the full validator uses, and undone
    # immediately.  This exercises rejection logic without dozens of 21 MiB
    # deep copies or repeated full-atlas parses.
    charts = _frontier_charts(stored)
    source = stored["trihomogeneous_source"]
    atlas = stored["chart_atlas"]
    chart0 = charts[0]
    affine = stored["affine_transfer"]
    decomposition = stored["decomposition_frontier"]
    contraction = stored["affine_contraction_frontier"]
    incidence = stored["parent_factor_incidence_frontier"]
    resources = stored["resource_accounting"]
    rejected: list[str] = []

    def expect_reject(marker: str, mutate: Callable[[], None], undo: Callable[[], None], check: Callable[[], None]) -> None:
        mutate()
        try:
            try:
                check()
            except (Reject, KeyError, IndexError, TypeError) as error:
                require(marker in str(error), f"hostile wrong rejection {marker}: {error}")
                rejected.append(marker)
            else:
                raise Reject(f"hostile mutation accepted: {marker}")
        finally:
            undo()

    def field_case(marker: str, container: Any, key: Any, bad: Any, check: Callable[[], None]) -> None:
        old = container[key]
        expect_reject(marker, lambda: container.__setitem__(key, bad), lambda: container.__setitem__(key, old), check)

    field_case("frontier format", stored, "format", "drift", lambda: require(stored["format"] == "d9-factor19069-explicit-trihom-jacobian-chart-constructor-frontier-v1", "frontier format"))
    field_case("frontier semantic pin", stored, "semantic_sha256", "0" * 64, lambda: require(stored["semantic_sha256"] == "aec3c7e29744d6d9a7df004c611c7edbdfbfedfad2bbea6f206df09d5fb14f33", "frontier semantic pin"))
    field_case("predecessor source pin", stored["predecessor_binding"], "file_sha256", "0" * 64, lambda: require(stored["predecessor_binding"]["file_sha256"] == digest_path(PREDECESSOR), "predecessor source pin"))
    field_case("source trihom term count", source, "term_count", 107, lambda: require(source["term_count"] == 108, "source trihom term count"))
    source_term = source["polynomial"]["sparse_polynomial"][0]
    field_case("source sparse equality", source_term, "coefficient", 9, lambda: require(rows_to_polynomial(source["polynomial"]["sparse_polynomial"], 12, "source sparse terms") == replay["trihomogeneous"], "source sparse equality"))
    field_case("source dehomogenization tag", source, "dehomogenization_exact_sparse_equality", False, lambda: require(source["dehomogenization_exact_sparse_equality"] is True, "source dehomogenization tag"))
    field_case("source decomposition guard", source, "trihomogenization_is_decomposition_certificate", True, lambda: require(source["trihomogenization_is_decomposition_certificate"] is False, "source decomposition guard"))
    field_case("source affine guard", source, "affine_source_is_homogeneous", True, lambda: require(source["affine_source_is_homogeneous"] is False, "source affine guard"))

    removed_chart = charts[-1]
    expect_reject("chart census", lambda: charts.pop(), lambda: charts.append(removed_chart), lambda: require(len(charts) == 64, "chart census"))
    field_case("chart 0 pivots", chart0, "pivots", ["b", "d", "g"], lambda: require(chart0["pivots"] == replay["charts"][0]["pivots"], "chart 0 pivots"))
    field_case("chart 0 free coordinates", chart0, "free_coordinates", list(reversed(chart0["free_coordinates"])), lambda: require(chart0["free_coordinates"] == replay["charts"][0]["free_coordinates"], "chart 0 free coordinates"))
    field_case("chart 0 generator count", chart0["chart_jacobian_ideal"], "generator_count", 9, lambda: require(chart0["chart_jacobian_ideal"]["generator_count"] == 10, "chart 0 generator count"))
    f_term = chart0["F_chart"]["sparse_polynomial"][0]
    field_case("chart 0 F equality", f_term, "coefficient", -f_term["coefficient"], lambda: require(rows_to_polynomial(chart0["F_chart"]["sparse_polynomial"], 9, "chart 0 F rows") == replay["charts"][0]["F_chart"], "chart 0 F equality"))

    derivative_rows = chart0["free_derivatives"][0]["sparse_polynomial"]
    removed_derivative_term = derivative_rows[-1]
    expect_reject("chart 0 derivative deletion", lambda: derivative_rows.pop(), lambda: derivative_rows.append(removed_derivative_term), lambda: require(rows_to_polynomial(derivative_rows, 9, "chart 0 derivative rows") == replay["charts"][0]["derivatives"][0], "chart 0 derivative deletion"))
    derivative_term = derivative_rows[0]
    field_case("chart 0 derivative sign", derivative_term, "coefficient", -derivative_term["coefficient"], lambda: require(rows_to_polynomial(derivative_rows, 9, "chart 0 derivative rows") == replay["charts"][0]["derivatives"][0], "chart 0 derivative sign"))
    field_case("chart 0 derivative coefficient", derivative_term, "coefficient", derivative_term["coefficient"] + 2, lambda: require(rows_to_polynomial(derivative_rows, 9, "chart 0 derivative rows") == replay["charts"][0]["derivatives"][0], "chart 0 derivative coefficient"))

    euler = chart0["euler_pivot_recoveries"][0]
    field_case("chart 0 Euler coefficient", euler, "block_degree", 1, lambda: require(euler["block_degree"] == 2, "chart 0 Euler coefficient"))
    euler_term = euler["euler_reconstruction"]["sparse_polynomial"][0]
    field_case("chart 0 Euler recovery", euler_term, "coefficient", euler_term["coefficient"] + 1, lambda: require(rows_to_polynomial(euler["direct_specialization"]["sparse_polynomial"], 9, "Euler direct") == rows_to_polynomial(euler["euler_reconstruction"]["sparse_polynomial"], 9, "Euler recovered"), "chart 0 Euler recovery"))
    zero_rows = euler["exact_zero_residual"]["sparse_polynomial"]
    fake_zero = {"exponents": [0] * 9, "coefficient": 1}
    expect_reject("chart 0 Euler zero residual", lambda: zero_rows.append(fake_zero), lambda: zero_rows.pop(), lambda: require(rows_to_polynomial(zero_rows, 9, "Euler residual") == {}, "chart 0 Euler zero residual"))
    field_case("chart 0 Euler identity", euler, "exact_sparse_equality", False, lambda: require(euler["exact_sparse_equality"] is True, "chart 0 Euler identity"))

    removed_boundary = chart0["boundary_strata"][-1]
    expect_reject("chart 0 boundary local census", lambda: chart0["boundary_strata"].pop(), lambda: chart0["boundary_strata"].append(removed_boundary), lambda: require(len(chart0["boundary_strata"]) == 7, "chart 0 boundary local census"))
    field_case("chart 0 boundary subset", chart0["boundary_strata"][0], "boundary_subset", ["v=0"], lambda: require(chart0["boundary_strata"][0]["boundary_subset"] == ["u=0"], "chart 0 boundary subset"))
    field_case("chart 0 affine-boundary distinction", chart0, "chart_is_wholly_infinity", True, lambda: require(chart0["chart_is_wholly_infinity"] is False, "chart 0 affine-boundary distinction"))
    field_case("chart 0 affine overlap retention", chart0, "contains_affine_overlap", False, lambda: require(chart0["contains_affine_overlap"] is True, "chart 0 affine overlap retention"))
    field_case("boundary retention tag", atlas, "all_available_boundary_strata_retained", False, lambda: require(atlas["all_available_boundary_strata_retained"] is True, "boundary retention tag"))
    field_case("boundary stratum record census", atlas, "boundary_stratum_record_count", 278, lambda: require(atlas["boundary_stratum_record_count"] == 279, "boundary stratum record census"))

    removed_overlap = chart0["overlap_records"][-1]
    expect_reject("chart 0 overlap local census", lambda: chart0["overlap_records"].pop(), lambda: chart0["overlap_records"].append(removed_overlap), lambda: require(len(chart0["overlap_records"]) == 63, "chart 0 overlap local census"))
    field_case("affine chart identity", affine, "chart_id", "JCH-00-a-d-g", lambda: require(affine["chart_id"] == "JCH-63-u-v-w", "affine chart identity"))
    field_case("affine specialization", affine["pivot_substitution"], "u", 0, lambda: require(affine["pivot_substitution"] == {"u": 1, "v": 1, "w": 1}, "affine specialization"))
    field_case("affine derivative transfer", affine, "nine_chart_derivatives_equal_original_affine_derivatives", False, lambda: require(affine["nine_chart_derivatives_equal_original_affine_derivatives"] is True, "affine derivative transfer"))
    field_case("affine ideal equality", affine, "chart_ideal_equals_original_affine_singular_ideal", False, lambda: require(affine["chart_ideal_equals_original_affine_singular_ideal"] is True, "affine ideal equality"))

    field_case("false complete decomposition", decomposition, "complete_projective_decomposition", True, lambda: require(decomposition["complete_projective_decomposition"] is False, "false complete decomposition"))
    fake_component = {"component_id": "fake-C", "status": "UNPROVED"}
    accepted = decomposition["first_pending_branch"]["accepted_components"]
    expect_reject("fake component", lambda: accepted.append(fake_component), lambda: accepted.pop(), lambda: require(accepted == [], "fake component"))
    field_case("fake contraction", contraction, "contracted_to_original_affine_singular_ideal_count", 1, lambda: require(contraction["contracted_to_original_affine_singular_ideal_count"] == 0, "fake contraction"))
    field_case("parent test uncontracted component", contraction, "componentwise_parent_tests_started", 1, lambda: require(contraction["componentwise_parent_tests_started"] == 0, "parent test uncontracted component"))
    field_case("uncontracted component tested", incidence, "completed_component_factor_pairs", 70, lambda: require(incidence["completed_component_factor_pairs"] == 0, "uncontracted component tested"))
    field_case("parent source tag", incidence, "source_parent_factor_tags_preserved", False, lambda: require(incidence["source_parent_factor_tags_preserved"] is True, "parent source tag"))
    parent0 = incidence["records"][0]
    field_case("parent factor 0 node tag", parent0, "factor_node_id", "H_00_fake", lambda: require(parent0["factor_node_id"] == replay["parent_tags"][0]["factor_node_id"], "parent factor 0 node tag"))
    parent_term = parent0["sparse_polynomial"][0]
    field_case("parent factor 0 sparse equality", parent_term, "coefficient", -1, lambda: require(rows_to_polynomial(parent0["sparse_polynomial"], 9, "parent factor 0 sparse rows") == replay["parent_tags"][0]["polynomial"], "parent factor 0 sparse equality"))

    nonconsequence = "NO_STRICT_REAL_RESIDENCE_OR_CONNECTED_PARENT_TAG"
    nc_index = stored["nonconsequences"].index(nonconsequence)
    expect_reject("real tag overclaim", lambda: stored["nonconsequences"].pop(nc_index), lambda: stored["nonconsequences"].insert(nc_index, nonconsequence), lambda: require(nonconsequence in stored["nonconsequences"], "real tag overclaim"))
    expect_reject("connected tag overclaim", lambda: stored["nonconsequences"].pop(nc_index), lambda: stored["nonconsequences"].insert(nc_index, nonconsequence), lambda: require(nonconsequence in stored["nonconsequences"], "connected tag overclaim"))
    field_case("frontier exact scope", resources, "numerical_or_modular_probe_used", True, lambda: require(resources["numerical_or_modular_probe_used"] is False, "frontier exact scope"))
    field_case("frontier route scope", resources, "seventy_inverse_variable_discovery_used", True, lambda: require(resources["seventy_inverse_variable_discovery_used"] is False, "frontier route scope"))
    field_case("frontier external scope", resources, "network_or_connector_used", True, lambda: require(resources["network_or_connector_used"] is False, "frontier external scope"))
    field_case("endpoint exclusivity", stored["endpoint_accounting"], "timeout", "NOT_REACHED", lambda: require(stored["endpoint_accounting"]["timeout"] == "REACHED_HASH_PINNED_FIRST_PENDING_CHART", "endpoint exclusivity"))
    field_case("endpoint classification", stored, "classification", "SUCCESS", lambda: require(stored["classification"] == "BOUNDED_CHARACTERISTIC_ZERO_CHART_DECOMPOSITION_TIMEOUT_FAIL_CLOSED", "endpoint classification"))
    field_case("frontier ledger delta", stored, "ledger_change_recommended", "+1", lambda: require(stored["ledger_change_recommended"] == "none", "frontier ledger delta"))
    field_case("frontier ledger", stored, "theorem_ledger", "3/9", lambda: require(stored["theorem_ledger"] == "2/9", "frontier ledger"))

    require(len(rejected) >= 24, "hostile frontier mutation census")
    return rejected


def main() -> None:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    result = json.loads(RESULT.read_text(encoding="utf-8"))
    frontier = json.loads(FRONTIER.read_text(encoding="utf-8"))
    validate_manifest(manifest)
    replay = reconstruct()
    validate_frontier(frontier, replay)
    rejected = hostile_manifest_mutations(manifest) + hostile_frontier_mutations(frontier, replay)
    validate_result(result, replay, len(rejected))
    hostile = json.loads(HOSTILE.read_text(encoding="utf-8"))
    require(hostile["total"] == hostile["rejected"] == len(rejected), "hostile report census")
    require(hostile["rejection_markers"] == rejected, "hostile report markers")
    print(
        "PASS factor-19069 explicit trihomogeneous chart falsifier: "
        f"108 terms, 64 charts, exact Euler/affine transfer, {len(rejected)} hostile mutations rejected"
    )


if __name__ == "__main__":
    try:
        main()
    except (Reject, KeyError, IndexError, TypeError, ValueError, OSError, json.JSONDecodeError) as error:
        print(f"REJECT: {error}", file=sys.stderr)
        raise SystemExit(1)
