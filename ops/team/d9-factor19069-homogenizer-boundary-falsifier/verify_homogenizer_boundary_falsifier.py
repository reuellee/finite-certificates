#!/usr/bin/env python3
"""Independent exact falsifier baseline for the factor-19069 boundary gate.

This lane imports neither current-cycle constructor code nor constructor
acceptance logic.  It rebuilds factor 19069 from the pinned mathematical
sources, trihomogenizes it by sparse integer arithmetic, reconstructs every
nonempty homogenizer boundary restriction and both Jacobian semantics, and
rebuilds the chart-incidence and parent-factor records.  Constructor-dependent
branch classifications remain explicitly unevaluated and fail closed.
"""

from __future__ import annotations

import argparse
from copy import deepcopy
from hashlib import sha256
from itertools import combinations, product
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
CYCLE = ROOT / "ops" / "research-team" / "cycles" / "2026-09-01-d9-row2599-factor19069-homogenizer-boundary-type-stratification-gate1"
PREDECESSOR = ROOT / "ops" / "team" / "d9-factor19069-explicit-trihom-jacobian-chart-constructor" / "PROJECTIVE_CHART_FRONTIER.json"

MANIFEST = HERE / "SOURCE_MANIFEST.json"
RECONSTRUCTION = HERE / "INDEPENDENT_RECONSTRUCTION.json"
HOSTILE = HERE / "HOSTILE_TESTS.json"
RESULT = HERE / "RESULT.json"
FINDINGS = HERE / "FINDINGS.md"

BASE_REVISION = "0ffb0295d74e6c50a3c198b67c9821d2fe2e2760"
BASE_TREE = "d01cfbbe04f721496a91d13f85d3688262869ac0"
OPENING_REVISION = "ff71f37eaafef17d57edda374508f7a8c7d38207"
OPENING_TREE = "4cb7c001243f3e1eb14d0a5867330c198c5dd381"
AUDITED_OPENING_REVISION = "aad8e1efa5a45e47c9f924dce5263a07996a10e9"
AUDITED_OPENING_TREE = "8b8fcd6652a0245df9b2a7f262f4c48bb5fdc883"
LANE_BRANCH = "research/lane-d9-boundary-falsifier-20260901"
CYCLE_ID = "2026-09-01-d9-row2599-factor19069-homogenizer-boundary-type-stratification-gate1"
TRACK_ID = "d9-factor19069-homogenizer-boundary-falsifier"
TARGET = "D9_ROW2599_FACTOR19069_HOMOGENIZER_BOUNDARY_TYPE_STRATIFICATION_GATE1"

AFFINE_VARIABLES = tuple("abcdefghi")
HOMOGENEOUS_VARIABLES = ("a", "b", "c", "u", "d", "e", "f", "v", "g", "h", "i", "w")
BLOCKS = (("a", "b", "c", "u"), ("d", "e", "f", "v"), ("g", "h", "i", "w"))
HOMOGENIZERS = ("u", "v", "w")
AFFINE_POSITIONS = (0, 1, 2, 4, 5, 6, 8, 9, 10)
HOMOGENIZER_POSITIONS = (3, 7, 11)
TYPE_ORDER = (("u", "v", "w"), ("u", "v"), ("u", "w"), ("v", "w"), ("u",), ("v",), ("w",))
TYPE_IDS = ("u_v_w", "u_v", "u_w", "v_w", "u", "v", "w")

EXPECTED_FACTOR_DIGEST = "041227c22bc01ca80df8a66a46099b2f703c53a310fe737dac3981bda5ee20c4"
EXPECTED_PARENT_DIGEST = "1d9b940e2bb954b5c69bcee8b2346f9554b2e15589ea4c5b3c3f8e1e943de701"
EXPECTED_PREDECESSOR_SHA256 = "815edf97a68a049f8fb6749adf948cc406ec7a258de480cf3ada3e301ca6de67"

INPUT_PATHS = (
    "ops/research-team/PROTOCOL.md",
    f"ops/research-team/cycles/{CYCLE_ID}/CYCLE.md",
    f"ops/research-team/cycles/{CYCLE_ID}/WORK_ORDERS.yaml",
    f"ops/research-team/cycles/{CYCLE_ID}/OPENING_AUDIT.json",
    f"ops/research-team/cycles/{CYCLE_ID}/OBLIGATION_GRAPH.json",
    f"ops/research-team/cycles/{CYCLE_ID}/verify_opening_audit.py",
    "ops/research-team/cycles/2026-09-01-d9-row2599-factor19069-explicit-trihom-jacobian-chart-gate1/CYCLE_REPORT.md",
    "ops/team/d9-factor19069-explicit-trihom-jacobian-chart-constructor/PROJECTIVE_CHART_FRONTIER.json",
    "ops/team/d9-factor19069-explicit-trihom-jacobian-chart-certificate/RESULT.json",
    "ops/team/d9-factor19069-explicit-trihom-jacobian-chart-falsifier/RESULT.json",
    "ops/team/d9-factor19069-explicit-trihom-jacobian-chart-referee/RESULT.json",
    "ai/omreal/DIAG2_PIVOT_LABELED_PAIR_ORBITS_VERIFY.py",
    "ai/omreal/verify_diag3_pair_global_parent_face_gate.py",
    "ai/omreal/certs_4_8.jsonl",
    "ai/omreal/data/DIAG3_PAIR_GLOBAL_row2599_candidate_factors.bin",
    "ai/omreal/data/DIAG3_PAIR_GLOBAL_row2599_compactification_atlas.json",
    "ai/omreal/data/DIAG3_PAIR_GLOBAL_row2599_parent_face_gate.json",
    "ai/omreal/data/DIAG9_GRAPH_row2599_factor_states.npz",
)

Polynomial = dict[tuple[int, ...], int]


class Reject(AssertionError):
    """Stable fail-closed rejection."""


def require(condition: bool, marker: str) -> None:
    if not condition:
        raise Reject(marker)


def digest_path(path: Path) -> str:
    state = sha256()
    with path.open("rb") as source:
        for block in iter(lambda: source.read(1 << 20), b""):
            state.update(block)
    return state.hexdigest()


def semantic_digest(value: Any) -> str:
    encoded = json.dumps(value, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return sha256(encoded).hexdigest()


def git(*arguments: str) -> str:
    return subprocess.check_output(
        ["git", "-c", f"safe.directory={ROOT.as_posix()}", *arguments],
        cwd=ROOT,
        text=True,
    ).strip()


def normalize(polynomial: Polynomial) -> Polynomial:
    return {tuple(exponents): int(coefficient) for exponents, coefficient in polynomial.items() if coefficient}


def rows(polynomial: Polynomial) -> list[list[int]]:
    return sorted([list(exponents) + [coefficient] for exponents, coefficient in normalize(polynomial).items()])


def decode_rows(value: Any, variable_count: int, marker: str) -> Polynomial:
    require(isinstance(value, list), marker)
    answer: Polynomial = {}
    for row in value:
        if isinstance(row, dict):
            exponents, coefficient = row.get("exponents"), row.get("coefficient")
        else:
            require(isinstance(row, list) and len(row) == variable_count + 1, marker)
            exponents, coefficient = row[:-1], row[-1]
        require(isinstance(exponents, list) and len(exponents) == variable_count, marker)
        require(all(isinstance(power, int) and power >= 0 for power in exponents), marker)
        require(isinstance(coefficient, int), marker)
        key = tuple(exponents)
        answer[key] = answer.get(key, 0) + coefficient
    return normalize(answer)


def sparse_digest(polynomial: Polynomial) -> str:
    return sha256(json.dumps(rows(polynomial), separators=(",", ":")).encode("ascii")).hexdigest()


def derivative(polynomial: Polynomial, position: int) -> Polynomial:
    answer: Polynomial = {}
    for exponents, coefficient in polynomial.items():
        power = exponents[position]
        if power:
            lowered = exponents[:position] + (power - 1,) + exponents[position + 1 :]
            answer[lowered] = answer.get(lowered, 0) + coefficient * power
    return normalize(answer)


def multiply(left: Polynomial, right: Polynomial) -> Polynomial:
    answer: Polynomial = {}
    for left_exponents, left_coefficient in left.items():
        for right_exponents, right_coefficient in right.items():
            exponents = tuple(a + b for a, b in zip(left_exponents, right_exponents, strict=True))
            answer[exponents] = answer.get(exponents, 0) + left_coefficient * right_coefficient
    return normalize(answer)


def scale(polynomial: Polynomial, scalar: int) -> Polynomial:
    return normalize({exponents: scalar * coefficient for exponents, coefficient in polynomial.items()})


def restrict_zero(polynomial: Polynomial, zero_positions: tuple[int, ...]) -> Polynomial:
    return {exponents: coefficient for exponents, coefficient in polynomial.items() if all(exponents[p] == 0 for p in zero_positions)}


def homogenize(affine: Polynomial) -> Polynomial:
    answer: Polynomial = {}
    affine_blocks = ((0, 1, 2), (3, 4, 5), (6, 7, 8))
    for affine_exponents, coefficient in affine.items():
        homogeneous = [0] * 12
        for source, target in enumerate(AFFINE_POSITIONS):
            homogeneous[target] = affine_exponents[source]
        for block_index, positions in enumerate(affine_blocks):
            degree = sum(affine_exponents[position] for position in positions)
            require(degree <= 2, "source trihomogenization degree ceiling")
            homogeneous[HOMOGENIZER_POSITIONS[block_index]] = 2 - degree
        key = tuple(homogeneous)
        answer[key] = answer.get(key, 0) + coefficient
    return normalize(answer)


def dehomogenize(homogeneous: Polynomial) -> Polynomial:
    answer: Polynomial = {}
    for exponents, coefficient in homogeneous.items():
        key = tuple(exponents[position] for position in AFFINE_POSITIONS)
        answer[key] = answer.get(key, 0) + coefficient
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


def monomial12(**powers: int) -> tuple[int, ...]:
    return tuple(powers.get(variable, 0) for variable in HOMOGENEOUS_VARIABLES)


def build_deepest(restricted: Polynomial, parents: list[dict[str, Any]]) -> dict[str, Any]:
    minus_h = {monomial12(h=1): -1}
    minor = {monomial12(a=1, f=1): 1, monomial12(c=1, d=1): -1}
    determinant = {
        monomial12(a=1, e=1, i=1): 1,
        monomial12(a=1, f=1, h=1): -1,
        monomial12(b=1, d=1, i=1): -1,
        monomial12(b=1, f=1, g=1): 1,
        monomial12(c=1, d=1, h=1): 1,
        monomial12(c=1, e=1, g=1): -1,
    }
    product_polynomial = multiply(multiply(minus_h, minor), determinant)
    require(product_polynomial == restricted, "deepest exact factorization")
    parent_08 = decode_rows(parents[8]["sparse_polynomial"], 9, "parent H_08")
    parent_22 = decode_rows(parents[22]["sparse_polynomial"], 9, "parent H_22")
    parent_34 = decode_rows(parents[34]["sparse_polynomial"], 9, "parent H_34")
    def affine_projection(polynomial: Polynomial) -> Polynomial:
        return {
            tuple(exponents[position] for position in AFFINE_POSITIONS): coefficient
            for exponents, coefficient in polynomial.items()
        }
    require(parents[8]["factor_node_id"] == "H_08_1248" and parent_08 == affine_projection(scale(minus_h, -1)), "deepest parent H_08 sign")
    require(parents[22]["factor_node_id"] == "H_22_1367" and parent_22 == affine_projection(scale(minor, -1)), "deepest parent H_22 sign")
    require(parents[34]["factor_node_id"] == "H_34_1678" and parent_34 == affine_projection(determinant), "deepest parent H_34 sign")
    parent_product = multiply(multiply(parent_08, parent_22), parent_34)
    require(parent_product == affine_projection(restricted), "deepest parent product equality")
    factor_records = [
        {"factor_id": "minus_h", "sparse_polynomial": rows(minus_h), "multidegree": [0, 0, 1], "factor_multiplicity": 1, "projective_hypersurface_dimension": 5, "strict_parent_excluded_by": "H_08_1248"},
        {"factor_id": "minor_af_cd", "sparse_polynomial": rows(minor), "multidegree": [1, 1, 0], "factor_multiplicity": 1, "projective_hypersurface_dimension": 5, "strict_parent_excluded_by": "H_22_1367"},
        {"factor_id": "det_3x3", "sparse_polynomial": rows(determinant), "multidegree": [1, 1, 1], "factor_multiplicity": 1, "projective_hypersurface_dimension": 5, "strict_parent_excluded_by": "H_34_1678"},
    ]
    return {
        "identity": "F|u=v=w=0=-h*(a*f-c*d)*(a*e*i-a*f*h-b*d*i+b*f*g+c*d*h-c*e*g)",
        "exact_sparse_equality": True,
        "restricted_term_count": len(restricted),
        "restricted_sparse_sha256": sparse_digest(restricted),
        "factors": factor_records,
        "factor_count": 3,
        "factor_multiplicities_exact": True,
        "required_set_theoretic_singular_branch_seeds": [
            {"branch_id": "PAIR_h_minor", "equation_factor_ids": ["minus_h", "minor_af_cd"], "excluded_by_parent_factor_node_ids": ["H_08_1248", "H_22_1367"], "strict_parent_exclusion_exact": True, "dimension_degree_multiplicity_status": "UNRESOLVED_FAIL_CLOSED"},
            {"branch_id": "PAIR_h_det", "equation_factor_ids": ["minus_h", "det_3x3"], "excluded_by_parent_factor_node_ids": ["H_08_1248", "H_34_1678"], "strict_parent_exclusion_exact": True, "dimension_degree_multiplicity_status": "UNRESOLVED_FAIL_CLOSED"},
            {"branch_id": "PAIR_minor_det", "equation_factor_ids": ["minor_af_cd", "det_3x3"], "excluded_by_parent_factor_node_ids": ["H_22_1367", "H_34_1678"], "strict_parent_exclusion_exact": True, "dimension_degree_multiplicity_status": "UNRESOLVED_FAIL_CLOSED"},
        ],
        "required_branch_seed_count": 3,
        "parent_factor_matches": [
            {"factor_id": "minus_h", "parent_factor_node_id": "H_08_1248", "factor_equals_parent_times_scalar": -1, "exact_sparse_equality": True, "parent_sparse_sha256": parents[8]["sparse_sha256"]},
            {"factor_id": "minor_af_cd", "parent_factor_node_id": "H_22_1367", "factor_equals_parent_times_scalar": -1, "exact_sparse_equality": True, "parent_sparse_sha256": parents[22]["sparse_sha256"]},
            {"factor_id": "det_3x3", "parent_factor_node_id": "H_34_1678", "factor_equals_parent_times_scalar": 1, "exact_sparse_equality": True, "parent_sparse_sha256": parents[34]["sparse_sha256"]},
        ],
        "parent_product_exactly_equals_deepest_restriction": True,
        "strict_parent_exclusion": {
            "classification": "ENTIRE_UVW_RESTRICTED_HYPERSURFACE_EXCLUDED_BY_PARENT_FACTORS_8_22_34",
            "exact": True,
            "reason": "F|uvw=H_08_1248*H_22_1367*H_34_1678, while every strict parent point has all 70 oriented parent factors nonzero",
            "excluded_parent_factor_indices": [8, 22, 34],
            "all_three_source_factor_branches_excluded": True,
            "all_three_required_pairwise_singular_seeds_excluded": True,
            "scope": "DEEPEST_UVW_RESTRICTED_SOURCE_HYPERSURFACE_ONLY",
        },
        "set_theoretic_cover_only": True,
        "scheme_radicality_certified": False,
        "singular_scheme_multiplicities_certified": False,
        "determinant_singular_rank_leq_one_is_contained_in_minor_det_seed": True,
        "minor_singular_linear_space_is_contained_in_minor_det_seed": True,
    }


def polynomial_record(polynomial: Polynomial) -> dict[str, Any]:
    return {"term_count": len(polynomial), "sparse_sha256": sparse_digest(polynomial), "sparse_polynomial": rows(polynomial)}


def build_boundary_records(homogeneous: Polynomial) -> list[dict[str, Any]]:
    answer = []
    for type_id, zero_variables in zip(TYPE_IDS, TYPE_ORDER, strict=True):
        zero_positions = tuple(HOMOGENEOUS_VARIABLES.index(variable) for variable in zero_variables)
        tangent_positions = tuple(position for position in range(12) if position not in zero_positions)
        restricted = restrict_zero(homogeneous, zero_positions)
        ambient_derivatives = [restrict_zero(derivative(homogeneous, position), zero_positions) for position in range(12)]
        stratum_derivatives = [derivative(restricted, position) for position in tangent_positions]
        for tangent_position, stratum_derivative in zip(tangent_positions, stratum_derivatives, strict=True):
            require(stratum_derivative == ambient_derivatives[tangent_position], f"tangent derivative transfer {type_id}")
        normal_derivatives = [ambient_derivatives[position] for position in zero_positions]
        require(all(normal_derivatives), f"normal derivative nonzero {type_id}")
        answer.append({
            "type_id": type_id,
            "zero_homogenizers": list(zero_variables),
            "zero_positions": list(zero_positions),
            "restricted_source": polynomial_record(restricted),
            "ambient_singularity_semantics": {
                "generators": "F|S plus all twelve (dF/dx)|S generators",
                "generator_count_before_zero_collection": 13,
                "derivatives": [
                    {"coordinate": variable, "term_count": len(polynomial), "sparse_sha256": sparse_digest(polynomial)}
                    for variable, polynomial in zip(HOMOGENEOUS_VARIABLES, ambient_derivatives, strict=True)
                ],
                "semantic_sha256": semantic_digest([rows(restricted)] + [rows(value) for value in ambient_derivatives]),
            },
            "stratum_singularity_semantics": {
                "generators": "F|S plus tangent derivatives d(F|S)/dx for x not in S",
                "generator_count_before_zero_collection": 1 + len(tangent_positions),
                "tangent_coordinates": [HOMOGENEOUS_VARIABLES[position] for position in tangent_positions],
                "derivatives": [
                    {"coordinate": HOMOGENEOUS_VARIABLES[position], "term_count": len(polynomial), "sparse_sha256": sparse_digest(polynomial)}
                    for position, polynomial in zip(tangent_positions, stratum_derivatives, strict=True)
                ],
                "semantic_sha256": semantic_digest([rows(restricted)] + [rows(value) for value in stratum_derivatives]),
            },
            "derivative_transfer": {
                "differentiate_then_restrict_for_ambient": True,
                "restrict_then_differentiate_for_stratum": True,
                "tangent_derivatives_exactly_equal": True,
                "normal_derivatives_must_not_be_discarded_from_ambient": True,
                "normal_derivatives": [
                    {"coordinate": HOMOGENEOUS_VARIABLES[position], "term_count": len(polynomial), "sparse_sha256": sparse_digest(polynomial)}
                    for position, polynomial in zip(zero_positions, normal_derivatives, strict=True)
                ],
            },
        })
    return answer


def chart_id(index: int, pivots: tuple[str, str, str]) -> str:
    return f"JCH-{index:02d}-{'-'.join(pivots)}"


def build_atlas() -> dict[str, Any]:
    charts = []
    incidences = []
    for index, pivots in enumerate(product(*BLOCKS)):
        pivots = tuple(pivots)
        available = tuple(HOMOGENIZERS[block] for block in range(3) if pivots[block] != HOMOGENIZERS[block])
        local_types = []
        for bitmask in range(1, 1 << len(available)):
            zero_variables = tuple(variable for bit, variable in enumerate(available) if bitmask & (1 << bit))
            local_types.append(list(zero_variables))
            incidences.append({"chart_id": chart_id(index, pivots), "zero_homogenizers": list(zero_variables)})
        charts.append({
            "chart_index": index,
            "chart_id": chart_id(index, pivots),
            "pivots": list(pivots),
            "available_boundary_homogenizers": list(available),
            "local_nonempty_boundary_types": local_types,
        })
    overlap_records = []
    for source in charts:
        for target in charts:
            if source["chart_id"] == target["chart_id"]:
                continue
            source_units = []
            target_units = []
            for block in range(3):
                if source["pivots"][block] != target["pivots"][block]:
                    source_units.append(target["pivots"][block])
                    target_units.append(source["pivots"][block])
            require(source_units and len(source_units) == len(target_units), "overlap invertible units")
            overlap_records.append([source["chart_id"], target["chart_id"], source_units, target_units])
    type_counts = {
        type_id: sum(1 for incidence in incidences if tuple(incidence["zero_homogenizers"]) == zero_variables)
        for type_id, zero_variables in zip(TYPE_IDS, TYPE_ORDER, strict=True)
    }
    require(type_counts == {"u_v_w": 27, "u_v": 36, "u_w": 36, "v_w": 36, "u": 48, "v": 48, "w": 48}, "boundary incidence type census")
    require(len(charts) == 64 and len(incidences) == 279 and len(overlap_records) == 4032, "atlas census")
    return {
        "standard_chart_count": 64,
        "charts": charts,
        "boundary_stratum_chart_incidence_count": 279,
        "incidences": incidences,
        "type_incidence_counts_deepest_first": type_counts,
        "directed_overlap_record_count": 4032,
        "directed_overlap_semantic_sha256": semantic_digest(overlap_records),
        "overlap_contract": {
            "every_nonidentity_overlap_has_source_and_target_invertible_units": True,
            "deduplication_requires_explicit_overlap_units": True,
            "deduplication_records_evaluated": 0,
            "deduplication_status": "NO_CONSTRUCTOR_BRANCH_DEDUPLICATION_AVAILABLE_FAIL_CLOSED",
        },
    }


def load_exact_sources() -> tuple[Polynomial, list[dict[str, Any]], str]:
    sys.path.insert(0, str(OMREAL))
    import DIAG2_PIVOT_LABELED_PAIR_ORBITS_VERIFY as labeled  # noqa: PLC0415
    import verify_diag3_pair_global_parent_face_gate as parent_gate  # noqa: PLC0415

    require(19069 in candidate_ids(), "factor candidate membership")
    factor = normalize(labeled.factor_polynomials()[2][19069])
    require(len(factor) == 108, "source affine term census")
    require(sparse_digest(factor) == EXPECTED_FACTOR_DIGEST, "source affine sparse digest")

    records = [json.loads(line) for line in (OMREAL / "certs_4_8.jsonl").read_text(encoding="utf-8").splitlines() if line]
    require(len(records) == 2628 and records[2599]["verdict"] == "REALIZABLE", "parent catalog record")
    sources, parent_digest = parent_gate.parent_polynomials(records[2599])
    require(len(sources) == 70 and parent_digest == EXPECTED_PARENT_DIGEST, "parent exact source census")
    parents = []
    for index, (node_code, sign, polynomial, _terms) in enumerate(sources):
        oriented = scale(normalize(polynomial), int(sign))
        parents.append({
            "factor_index": index,
            "factor_node_id": f"H_{index:02d}_{node_code}",
            "source_orientation": int(sign),
            "degree": max(map(sum, oriented), default=0),
            "term_count": len(oriented),
            "sparse_sha256": sparse_digest(oriented),
            "sparse_polynomial": rows(oriented),
        })
    return factor, parents, parent_digest


def validate_predecessor(homogeneous: Polynomial, atlas: dict[str, Any], parents: list[dict[str, Any]]) -> dict[str, Any]:
    require(digest_path(PREDECESSOR) == EXPECTED_PREDECESSOR_SHA256, "predecessor frontier pin")
    predecessor = json.loads(PREDECESSOR.read_text(encoding="utf-8"))
    require(predecessor["outcome"] == "pass" and predecessor["theorem_ledger"] == "2/9", "predecessor fail-closed outcome")
    require(predecessor["endpoint"] == "HASH_PIN_ALL_COMPLETED_CHART_BRANCHES_AND_FIRST_PENDING_BRANCH", "predecessor timeout endpoint")
    source = predecessor["trihomogeneous_source"]
    require(decode_rows(source["polynomial"]["sparse_polynomial"], 12, "predecessor source sparse") == homogeneous, "predecessor source exact equality")
    inherited = predecessor["chart_atlas"]
    require(inherited["standard_chart_count"] == len(inherited["charts"]) == 64, "predecessor chart census")
    require(inherited["directed_overlap_record_count"] == 4032, "predecessor overlap census")
    require(inherited["boundary_stratum_record_count"] == 279, "predecessor incidence census")
    for expected, actual in zip(atlas["charts"], inherited["charts"], strict=True):
        require(actual["chart_id"] == expected["chart_id"] and actual["pivots"] == expected["pivots"], "predecessor chart identity")
        require([item["zero_homogenizers"] for item in actual["boundary_strata"]] == expected["local_nonempty_boundary_types"], "predecessor local boundary incidence")
    parent_records = predecessor["parent_factor_incidence_frontier"]["records"]
    require(len(parent_records) == len(parents) == 70, "predecessor parent census")
    for expected, actual in zip(parents, parent_records, strict=True):
        require(actual["factor_index"] == expected["factor_index"] and actual["factor_node_id"] == expected["factor_node_id"], "predecessor parent identity")
        require(decode_rows(actual["sparse_polynomial"], 9, "predecessor parent sparse") == decode_rows(expected["sparse_polynomial"], 9, "independent parent sparse"), "predecessor parent exact equality")
    return {
        "file_sha256": EXPECTED_PREDECESSOR_SHA256,
        "exact_source_equal": True,
        "all_64_chart_identities_equal": True,
        "all_279_boundary_incidences_equal": True,
        "all_70_parent_records_equal": True,
        "timeout_frontier_not_promoted_to_completeness": True,
    }


def build_reconstruction() -> dict[str, Any]:
    factor, parents, parent_digest = load_exact_sources()
    homogeneous = homogenize(factor)
    require(len(homogeneous) == 108 and dehomogenize(homogeneous) == factor, "source exact trihomogenization")
    for exponents in homogeneous:
        degrees = tuple(sum(exponents[start : start + 4]) for start in (0, 4, 8))
        require(degrees == (2, 2, 2), "source exact tridegree")
    boundaries = build_boundary_records(homogeneous)
    atlas = build_atlas()
    deepest = build_deepest(decode_rows(boundaries[0]["restricted_source"]["sparse_polynomial"], 12, "deepest source"), parents)
    predecessor_binding = validate_predecessor(homogeneous, atlas, parents)
    exact_nodes = 108 + sum(record["restricted_source"]["term_count"] for record in boundaries)
    exact_nodes += sum(
        derivative_record["term_count"]
        for record in boundaries
        for semantic in (record["ambient_singularity_semantics"], record["stratum_singularity_semantics"])
        for derivative_record in semantic["derivatives"]
    )
    exact_nodes += sum(parent["term_count"] for parent in parents) + 64 + 279 + 4032
    return {
        "format": "d9-factor19069-homogenizer-boundary-falsifier-reconstruction-v1",
        "cycle_id": CYCLE_ID,
        "track_id": TRACK_ID,
        "target": TARGET,
        "base_revision": BASE_REVISION,
        "base_tree": BASE_TREE,
        "audited_opening_revision": AUDITED_OPENING_REVISION,
        "lane_branch": LANE_BRANCH,
        "independence": {
            "constructor_code_imported": False,
            "constructor_acceptance_logic_imported": False,
            "current_cycle_constructor_artifact_read": False,
            "predecessor_artifact_used_only_as_pinned_comparison": True,
        },
        "affine_source": {"coordinate_order": list(AFFINE_VARIABLES), **polynomial_record(factor)},
        "trihomogeneous_source": {
            "coordinate_order": list(HOMOGENEOUS_VARIABLES),
            "blocks": [list(block) for block in BLOCKS],
            "multidegree": [2, 2, 2],
            "dehomogenization_exact": True,
            **polynomial_record(homogeneous),
        },
        "boundary_type_order": list(TYPE_IDS),
        "boundary_type_count": 7,
        "boundary_types": boundaries,
        "deepest_factorization": deepest,
        "chart_atlas": atlas,
        "parent_source": {
            "parent_index": 2599,
            "ordered_factor_count": 70,
            "parent_sign_digest": parent_digest,
            "source_order_preserved": True,
            "records": parents,
        },
        "predecessor_binding": predecessor_binding,
        "claim_guard": {
            "constructor_candidate_evaluated": False,
            "constructor_dependent_branch_classification": "UNAVAILABLE_FAIL_CLOSED",
            "accepted_affine_pullback_branch_count": 0,
            "complete_componentwise_parent_factor_test_count": 0,
            "strict_real_residence_certified": False,
            "connected_row2599_parent_tag_certified": False,
            "unsupported_radicality_claim_made": False,
            "unsupported_multiplicity_claim_made": False,
            "deepest_restricted_source_hypersurface_parent_exclusion_certified": True,
            "deepest_required_source_factor_branch_seeds_parent_excluded": True,
            "deepest_ambient_singular_scheme_complete": False,
            "remaining_six_type_ambient_singular_branches_complete": False,
            "positive_endpoint": "NOT_REACHED",
            "negative_endpoint": "NOT_REACHED",
            "null_endpoint": "NOT_REACHED_NO_CONSTRUCTOR_BRANCH_PRESENT",
            "timeout_endpoint": "NOT_REACHED_FALSIFIER_BASELINE_COMPLETED_WITHIN_CEILING",
            "selected_endpoint": "INDEPENDENT_FALSIFIER_BASELINE_ONLY",
        },
        "scope": {
            "numerical_inference_used": False,
            "modular_inference_used": False,
            "sampled_inference_used": False,
            "network_or_connector_used": False,
            "google_drive_connector_used": False,
            "google_drive_mirror_written": False,
            "github_write_used": False,
            "retired_routes_used": [],
        },
        "resource_accounting": {
            "exact_algebra_branch_nodes": exact_nodes,
            "node_ceiling": 500000,
            "within_node_ceiling": exact_nodes <= 500000,
            "memory_ceiling_gib": 8,
            "sympy_used": False,
            "arithmetic": "standard-library sparse integer arithmetic plus pinned exact repository source modules",
        },
        "classification": "INDEPENDENT_EXACT_FALSIFIER_BASELINE_PASS_CONSTRUCTOR_CLAIMS_UNEVALUATED_FAIL_CLOSED",
        "ledger_delta": "none",
        "theorem_ledger": "2/9",
        "ledger_promotion_recommended": False,
    }


def build_manifest() -> dict[str, Any]:
    pins = {relative: digest_path(ROOT / relative) for relative in INPUT_PATHS}
    pins[(HERE / "verify_homogenizer_boundary_falsifier.py").relative_to(ROOT).as_posix()] = digest_path(HERE / "verify_homogenizer_boundary_falsifier.py")
    return {
        "format": "d9-factor19069-homogenizer-boundary-falsifier-source-manifest-v1",
        "cycle_id": CYCLE_ID,
        "track_id": TRACK_ID,
        "base_revision": BASE_REVISION,
        "base_tree": BASE_TREE,
        "opening_revision": OPENING_REVISION,
        "opening_tree": OPENING_TREE,
        "audited_opening_revision": AUDITED_OPENING_REVISION,
        "audited_opening_tree": AUDITED_OPENING_TREE,
        "lane_branch": LANE_BRANCH,
        "source_count": len(pins),
        "source_sha256": pins,
        "reconstruction_sha256": digest_path(RECONSTRUCTION),
        "producer_code_imported": False,
        "constructor_acceptance_imported": False,
        "current_cycle_constructor_artifact_read": False,
        "numerical_or_modular_or_sampled_inference_used": False,
        "network_or_connector_used": False,
        "google_drive_connector_used": False,
        "github_write_used": False,
        "python_runtime_used": r"C:\Users\reuel\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe",
        "sympy_used": False,
    }


def validate_manifest(candidate: dict[str, Any]) -> None:
    require(candidate["format"] == "d9-factor19069-homogenizer-boundary-falsifier-source-manifest-v1", "manifest format")
    require(candidate["cycle_id"] == CYCLE_ID and candidate["track_id"] == TRACK_ID, "manifest identity")
    require(candidate["base_revision"] == BASE_REVISION and candidate["base_tree"] == BASE_TREE, "manifest base")
    require(candidate["opening_revision"] == OPENING_REVISION and candidate["opening_tree"] == OPENING_TREE, "manifest opening")
    require(candidate["audited_opening_revision"] == AUDITED_OPENING_REVISION and candidate["audited_opening_tree"] == AUDITED_OPENING_TREE, "manifest audited opening")
    require(candidate["lane_branch"] == LANE_BRANCH, "manifest lane branch")
    require(candidate["source_count"] == len(candidate["source_sha256"]), "manifest source count")
    for relative, expected in candidate["source_sha256"].items():
        require(digest_path(ROOT / relative) == expected, f"manifest source pin {relative}")
    require(candidate["reconstruction_sha256"] == digest_path(RECONSTRUCTION), "manifest reconstruction pin")
    require(candidate["producer_code_imported"] is False, "manifest producer independence")
    require(candidate["constructor_acceptance_imported"] is False, "manifest acceptance independence")
    require(candidate["current_cycle_constructor_artifact_read"] is False, "manifest constructor artifact isolation")
    require(candidate["numerical_or_modular_or_sampled_inference_used"] is False, "manifest exact inference scope")
    require(candidate["network_or_connector_used"] is False, "manifest external scope")
    require(candidate["google_drive_connector_used"] is False, "manifest drive scope")
    require(candidate["github_write_used"] is False, "manifest github scope")
    require(candidate["sympy_used"] is False, "manifest runtime scope")


def validate_reconstruction(candidate: dict[str, Any], expected: dict[str, Any]) -> None:
    require(candidate["format"] == expected["format"], "reconstruction format")
    require(candidate["cycle_id"] == CYCLE_ID and candidate["track_id"] == TRACK_ID and candidate["target"] == TARGET, "reconstruction identity")
    require(candidate["base_revision"] == BASE_REVISION and candidate["base_tree"] == BASE_TREE, "reconstruction base")
    require(candidate["lane_branch"] == LANE_BRANCH, "reconstruction lane branch")
    require(candidate["independence"] == expected["independence"], "reconstruction independence")
    require(candidate["affine_source"] == expected["affine_source"], "affine source exact equality")
    require(candidate["trihomogeneous_source"] == expected["trihomogeneous_source"], "trihomogeneous source exact equality")
    require(candidate["boundary_type_order"] == list(TYPE_IDS) and candidate["boundary_type_count"] == 7, "boundary type census and order")
    require(len(candidate["boundary_types"]) == 7, "boundary record census")
    for actual, wanted in zip(candidate["boundary_types"], expected["boundary_types"], strict=True):
        require(actual == wanted, f"boundary record {wanted['type_id']}")
    require(candidate["deepest_factorization"] == expected["deepest_factorization"], "deepest factorization and branches")
    atlas = candidate["chart_atlas"]
    wanted_atlas = expected["chart_atlas"]
    require(atlas["standard_chart_count"] == 64 and atlas["charts"] == wanted_atlas["charts"], "atlas chart census")
    require(atlas["boundary_stratum_chart_incidence_count"] == 279 and atlas["incidences"] == wanted_atlas["incidences"], "atlas incidence census")
    require(atlas["type_incidence_counts_deepest_first"] == wanted_atlas["type_incidence_counts_deepest_first"], "atlas type incidence counts")
    require(atlas["directed_overlap_record_count"] == 4032 and atlas["directed_overlap_semantic_sha256"] == wanted_atlas["directed_overlap_semantic_sha256"], "atlas overlap census")
    require(atlas["overlap_contract"] == wanted_atlas["overlap_contract"], "overlap invertible-unit contract")
    parent = candidate["parent_source"]
    wanted_parent = expected["parent_source"]
    require(parent["parent_index"] == 2599 and parent["ordered_factor_count"] == 70, "parent factor census")
    require(parent["parent_sign_digest"] == EXPECTED_PARENT_DIGEST, "parent sign digest")
    require(parent["source_order_preserved"] is True, "parent source order")
    require(parent["records"] == wanted_parent["records"], "parent records exact equality")
    require(candidate["predecessor_binding"] == expected["predecessor_binding"], "predecessor binding")
    require(candidate["claim_guard"] == expected["claim_guard"], "constructor-dependent claim guard")
    require(candidate["scope"] == expected["scope"], "scope guard")
    require(candidate["resource_accounting"] == expected["resource_accounting"], "resource accounting")
    require(candidate["classification"] == expected["classification"], "classification honesty")
    require(candidate["ledger_delta"] == "none" and candidate["theorem_ledger"] == "2/9", "ledger guard")
    require(candidate["ledger_promotion_recommended"] is False, "promotion guard")


def hostile_mutations(manifest: dict[str, Any], reconstruction: dict[str, Any], expected: dict[str, Any]) -> list[str]:
    rejected: list[str] = []

    manifest_cases: list[tuple[str, Callable[[dict[str, Any]], None]]] = [
        ("manifest source count", lambda value: value.__setitem__("source_count", 0)),
        ("manifest source pin", lambda value: value["source_sha256"].__setitem__("ops/research-team/PROTOCOL.md", "0" * 64)),
        ("manifest producer independence", lambda value: value.__setitem__("producer_code_imported", True)),
        ("manifest acceptance independence", lambda value: value.__setitem__("constructor_acceptance_imported", True)),
        ("manifest constructor artifact isolation", lambda value: value.__setitem__("current_cycle_constructor_artifact_read", True)),
        ("manifest exact inference scope", lambda value: value.__setitem__("numerical_or_modular_or_sampled_inference_used", True)),
        ("manifest external scope", lambda value: value.__setitem__("network_or_connector_used", True)),
        ("manifest drive scope", lambda value: value.__setitem__("google_drive_connector_used", True)),
        ("manifest github scope", lambda value: value.__setitem__("github_write_used", True)),
    ]
    for marker, edit in manifest_cases:
        mutated = deepcopy(manifest)
        edit(mutated)
        try:
            validate_manifest(mutated)
        except Reject as error:
            require(marker in str(error), f"wrong hostile rejection {marker}: {error}")
            rejected.append(marker)
        else:
            raise Reject(f"hostile mutation accepted {marker}")

    boundary = reconstruction["boundary_types"]
    deepest = reconstruction["deepest_factorization"]
    atlas = reconstruction["chart_atlas"]
    parent = reconstruction["parent_source"]
    claim = reconstruction["claim_guard"]
    scope = reconstruction["scope"]
    resources = reconstruction["resource_accounting"]
    cases: list[tuple[str, Callable[[dict[str, Any]], None]]] = [
        ("reconstruction identity", lambda value: value.__setitem__("target", "wrong")),
        ("reconstruction base", lambda value: value.__setitem__("base_revision", "0" * 40)),
        ("reconstruction independence", lambda value: value["independence"].__setitem__("constructor_code_imported", True)),
        ("affine source exact equality", lambda value: value["affine_source"].__setitem__("term_count", 107)),
        ("affine source exact equality", lambda value: value["affine_source"]["sparse_polynomial"][0].__setitem__(9, value["affine_source"]["sparse_polynomial"][0][9] + 1)),
        ("trihomogeneous source exact equality", lambda value: value["trihomogeneous_source"].__setitem__("multidegree", [2, 2, 1])),
        ("trihomogeneous source exact equality", lambda value: value["trihomogeneous_source"].__setitem__("dehomogenization_exact", False)),
        ("boundary type census and order", lambda value: value.__setitem__("boundary_type_order", ["u", "v", "w"])),
        ("boundary record census", lambda value: value["boundary_types"].pop()),
        ("boundary record u_v_w", lambda value: value["boundary_types"][0]["restricted_source"].__setitem__("term_count", 12)),
        ("boundary record u_v_w", lambda value: value["boundary_types"][0]["derivative_transfer"].__setitem__("differentiate_then_restrict_for_ambient", False)),
        ("boundary record u_v", lambda value: value["boundary_types"][1]["stratum_singularity_semantics"].__setitem__("generator_count_before_zero_collection", 12)),
        ("boundary record u_w", lambda value: value["boundary_types"][2]["derivative_transfer"].__setitem__("tangent_derivatives_exactly_equal", False)),
        ("boundary record v_w", lambda value: value["boundary_types"][3]["ambient_singularity_semantics"]["derivatives"][0].__setitem__("term_count", 0)),
        ("boundary record u", lambda value: value["boundary_types"][4].__setitem__("zero_homogenizers", ["v"])),
        ("boundary record v", lambda value: value["boundary_types"][5]["derivative_transfer"].__setitem__("normal_derivatives_must_not_be_discarded_from_ambient", False)),
        ("boundary record w", lambda value: value["boundary_types"][6]["restricted_source"].__setitem__("sparse_sha256", "0" * 64)),
        ("deepest factorization and branches", lambda value: value["deepest_factorization"].__setitem__("exact_sparse_equality", False)),
        ("deepest factorization and branches", lambda value: value["deepest_factorization"]["factors"][0].__setitem__("factor_multiplicity", 2)),
        ("deepest factorization and branches", lambda value: value["deepest_factorization"]["required_set_theoretic_singular_branch_seeds"].pop()),
        ("deepest factorization and branches", lambda value: value["deepest_factorization"].__setitem__("scheme_radicality_certified", True)),
        ("deepest factorization and branches", lambda value: value["deepest_factorization"]["strict_parent_exclusion"].__setitem__("all_three_source_factor_branches_excluded", False)),
        ("atlas chart census", lambda value: value["chart_atlas"].__setitem__("standard_chart_count", 63)),
        ("atlas chart census", lambda value: value["chart_atlas"]["charts"][0].__setitem__("pivots", ["b", "d", "g"])),
        ("atlas incidence census", lambda value: value["chart_atlas"].__setitem__("boundary_stratum_chart_incidence_count", 278)),
        ("atlas incidence census", lambda value: value["chart_atlas"]["incidences"].pop()),
        ("atlas type incidence counts", lambda value: value["chart_atlas"]["type_incidence_counts_deepest_first"].__setitem__("u_v_w", 26)),
        ("atlas overlap census", lambda value: value["chart_atlas"].__setitem__("directed_overlap_record_count", 4031)),
        ("overlap invertible-unit contract", lambda value: value["chart_atlas"]["overlap_contract"].__setitem__("deduplication_requires_explicit_overlap_units", False)),
        ("parent factor census", lambda value: value["parent_source"].__setitem__("ordered_factor_count", 69)),
        ("parent sign digest", lambda value: value["parent_source"].__setitem__("parent_sign_digest", "0" * 64)),
        ("parent source order", lambda value: value["parent_source"].__setitem__("source_order_preserved", False)),
        ("parent records exact equality", lambda value: value["parent_source"]["records"][0]["sparse_polynomial"][0].__setitem__(9, value["parent_source"]["records"][0]["sparse_polynomial"][0][9] + 1)),
        ("predecessor binding", lambda value: value["predecessor_binding"].__setitem__("all_279_boundary_incidences_equal", False)),
        ("constructor-dependent claim guard", lambda value: value["claim_guard"].__setitem__("constructor_candidate_evaluated", True)),
        ("constructor-dependent claim guard", lambda value: value["claim_guard"].__setitem__("accepted_affine_pullback_branch_count", 1)),
        ("constructor-dependent claim guard", lambda value: value["claim_guard"].__setitem__("complete_componentwise_parent_factor_test_count", 70)),
        ("constructor-dependent claim guard", lambda value: value["claim_guard"].__setitem__("strict_real_residence_certified", True)),
        ("constructor-dependent claim guard", lambda value: value["claim_guard"].__setitem__("connected_row2599_parent_tag_certified", True)),
        ("constructor-dependent claim guard", lambda value: value["claim_guard"].__setitem__("remaining_six_type_ambient_singular_branches_complete", True)),
        ("constructor-dependent claim guard", lambda value: value["claim_guard"].__setitem__("positive_endpoint", "REACHED")),
        ("constructor-dependent claim guard", lambda value: value["claim_guard"].__setitem__("negative_endpoint", "REACHED")),
        ("scope guard", lambda value: value["scope"].__setitem__("numerical_inference_used", True)),
        ("scope guard", lambda value: value["scope"].__setitem__("modular_inference_used", True)),
        ("scope guard", lambda value: value["scope"].__setitem__("sampled_inference_used", True)),
        ("scope guard", lambda value: value["scope"].__setitem__("retired_routes_used", ["BLIND_WHOLE_ATLAS_GROEBNER_RETRY"])),
        ("resource accounting", lambda value: value["resource_accounting"].__setitem__("exact_algebra_branch_nodes", 500001)),
        ("classification honesty", lambda value: value.__setitem__("classification", "SUCCESS")),
        ("ledger guard", lambda value: value.__setitem__("theorem_ledger", "3/9")),
        ("promotion guard", lambda value: value.__setitem__("ledger_promotion_recommended", True)),
    ]
    del boundary, deepest, atlas, parent, claim, scope, resources
    for marker, edit in cases:
        mutated = deepcopy(reconstruction)
        edit(mutated)
        try:
            validate_reconstruction(mutated, expected)
        except Reject as error:
            require(marker in str(error), f"wrong hostile rejection {marker}: {error}")
            rejected.append(marker)
        else:
            raise Reject(f"hostile mutation accepted {marker}")
    require(len(rejected) >= 24, "hostile mutation census")
    return rejected


def write_json(path: Path, value: Any) -> None:
    with path.open("w", encoding="utf-8", newline="\n") as target:
        target.write(json.dumps(value, indent=2, sort_keys=True) + "\n")


def validate_repository_state() -> None:
    require(git("rev-parse", f"{BASE_REVISION}^{{commit}}") == BASE_REVISION, "base commit")
    require(git("rev-parse", f"{BASE_REVISION}^{{tree}}") == BASE_TREE, "base tree")
    require(git("rev-parse", f"{OPENING_REVISION}^{{commit}}") == OPENING_REVISION, "opening commit")
    require(git("rev-parse", f"{OPENING_REVISION}^{{tree}}") == OPENING_TREE, "opening tree")
    require(git("rev-parse", f"{AUDITED_OPENING_REVISION}^{{commit}}") == AUDITED_OPENING_REVISION, "audited opening commit")
    require(git("rev-parse", f"{AUDITED_OPENING_REVISION}^{{tree}}") == AUDITED_OPENING_TREE, "audited opening tree")
    require(git("branch", "--show-current") == LANE_BRANCH, "lane branch")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true", help="write deterministic lane artifacts")
    arguments = parser.parse_args()
    validate_repository_state()
    expected = build_reconstruction()
    if arguments.write:
        write_json(RECONSTRUCTION, expected)
        manifest = build_manifest()
        write_json(MANIFEST, manifest)
        rejected = hostile_mutations(manifest, expected, expected)
        hostile = {
            "format": "d9-factor19069-homogenizer-boundary-falsifier-hostile-tests-v1",
            "cycle_id": CYCLE_ID,
            "track_id": TRACK_ID,
            "total": len(rejected),
            "rejected": len(rejected),
            "rejection_markers": rejected,
        }
        write_json(HOSTILE, hostile)
        result = {
            "format": "d9-factor19069-homogenizer-boundary-falsifier-result-v1",
            "cycle_id": CYCLE_ID,
            "track_id": TRACK_ID,
            "outcome": "pass",
            "classification": expected["classification"],
            "independent_reconstruction_sha256": digest_path(RECONSTRUCTION),
            "source_manifest_sha256": digest_path(MANIFEST),
            "hostile_tests_sha256": digest_path(HOSTILE),
            "hostile_mutations_rejected": len(rejected),
            "source_term_count": 108,
            "boundary_type_count": 7,
            "boundary_type_order": list(TYPE_IDS),
            "deepest_restriction_term_count": expected["deepest_factorization"]["restricted_term_count"],
            "chart_count": 64,
            "boundary_stratum_chart_incidence_count": 279,
            "parent_factor_count": 70,
            "deepest_source_factor_classification": "ENTIRE_UVW_RESTRICTED_HYPERSURFACE_EXCLUDED_BY_PARENT_FACTORS_8_22_34",
            "other_type_ambient_singular_branch_status": "UNAVAILABLE_FAIL_CLOSED",
            "constructor_candidate_evaluated": False,
            "constructor_dependent_claim_status": "UNAVAILABLE_FAIL_CLOSED",
            "ledger_delta": "none",
            "theorem_ledger": "2/9",
            "ledger_promotion_recommended": False,
            "google_drive_connector_used": False,
            "github_write_used": False,
        }
        write_json(RESULT, result)

    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    reconstruction = json.loads(RECONSTRUCTION.read_text(encoding="utf-8"))
    hostile = json.loads(HOSTILE.read_text(encoding="utf-8"))
    result = json.loads(RESULT.read_text(encoding="utf-8"))
    validate_manifest(manifest)
    validate_reconstruction(reconstruction, expected)
    rejected = hostile_mutations(manifest, reconstruction, expected)
    require(hostile["total"] == hostile["rejected"] == len(rejected), "hostile report census")
    require(hostile["rejection_markers"] == rejected, "hostile report markers")
    require(result["outcome"] == "pass" and result["classification"] == expected["classification"], "result classification")
    require(result["independent_reconstruction_sha256"] == digest_path(RECONSTRUCTION), "result reconstruction pin")
    require(result["source_manifest_sha256"] == digest_path(MANIFEST), "result manifest pin")
    require(result["hostile_tests_sha256"] == digest_path(HOSTILE), "result hostile pin")
    require(result["hostile_mutations_rejected"] == len(rejected), "result hostile census")
    require(result["source_term_count"] == 108 and result["boundary_type_count"] == 7, "result source census")
    require(result["chart_count"] == 64 and result["boundary_stratum_chart_incidence_count"] == 279, "result atlas census")
    require(result["parent_factor_count"] == 70, "result parent census")
    require(result["deepest_source_factor_classification"] == "ENTIRE_UVW_RESTRICTED_HYPERSURFACE_EXCLUDED_BY_PARENT_FACTORS_8_22_34", "result deepest classification")
    require(result["other_type_ambient_singular_branch_status"] == "UNAVAILABLE_FAIL_CLOSED", "result other type fail closed")
    require(result["constructor_candidate_evaluated"] is False and result["constructor_dependent_claim_status"] == "UNAVAILABLE_FAIL_CLOSED", "result constructor fail closed")
    require(result["ledger_delta"] == "none" and result["theorem_ledger"] == "2/9" and result["ledger_promotion_recommended"] is False, "result ledger guard")
    findings = FINDINGS.read_text(encoding="utf-8").lower()
    for phrase in ("seven boundary types", "derivative-before-restriction", "invertible overlap units", "all 70 parent factors", "constructor-dependent"):
        require(phrase in findings, f"findings phrase {phrase}")
    print(
        "PASS factor-19069 homogenizer-boundary falsifier baseline: "
        f"108 terms, 7 exact restrictions, 64 charts/279 incidences, 70 parents, {len(rejected)} hostile mutations rejected; constructor claims fail closed"
    )


if __name__ == "__main__":
    try:
        main()
    except (Reject, KeyError, IndexError, TypeError, ValueError, OSError, json.JSONDecodeError, subprocess.CalledProcessError) as error:
        print(f"REJECT: {error}", file=sys.stderr)
        raise SystemExit(1)
