#!/usr/bin/env python3
"""Build the exact 64-chart Jacobian frontier for factor 19069.

The source is reconstructed only from the pinned predecessor JSON.  The
builder constructs every standard chart of (P^3)^3, proves the three Euler
recoveries on every chart by sparse-polynomial equality, and checks that the
(u,v,w) chart is exactly the original affine Jacobian ideal.  A separately
bounded SymPy Groebner attempt is only a prerequisite to characteristic-zero
decomposition.  It is never interpreted as a primary decomposition.
"""

from __future__ import annotations

import argparse
from copy import deepcopy
from hashlib import sha256
from itertools import product
import json
from pathlib import Path
import subprocess
import sys


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
CYCLE_ID = "2026-09-01-d9-row2599-factor19069-explicit-trihom-jacobian-chart-gate1"
CYCLE = ROOT / "ops" / "research-team" / "cycles" / CYCLE_ID
PREDECESSOR = ROOT / "ops" / "team" / "d9-factor19069-singular-df-multihomogeneous-constructor" / "SINGULAR_DF_MULTIHOMOGENEOUS_FRONTIER.json"
FRONTIER = HERE / "PROJECTIVE_CHART_FRONTIER.json"
MANIFEST = HERE / "SOURCE_MANIFEST.json"
RESULT = HERE / "RESULT.json"

OPENING_REVISION = "cd2d856d3ccff51f7b5d6841702b25d191ed9985"
OPENING_TREE = "6014474550142ec47f9280a123dc77bf403d1d0a"
BASE_REVISION = "4aee0aac6e80d053cf1751eac766280873656909"
BASE_TREE = "bfaff6f29b032ef6f81fa11a97063b01d74db8f7"
PREDECESSOR_SHA256 = "d9f4aba3fa8c76e3a8abff5484ff509b0458fe9993edeb921e5a6d03c4dfac41"
PREDECESSOR_SEMANTIC_SHA256 = "d062fe00f8c7cd256c7aff13b559ead79de2539ac84579497348576acf2423e6"
VARIABLES = ("a", "b", "c", "u", "d", "e", "f", "v", "g", "h", "i", "w")
BLOCKS = (VARIABLES[0:4], VARIABLES[4:8], VARIABLES[8:12])
HOMOGENIZERS = ("u", "v", "w")
AFFINE_VARIABLES = tuple("abcdefghi")
AFFINE_TO_HOM = (0, 1, 2, 4, 5, 6, 8, 9, 10)
BLOCK_AFFINE_INDICES = ((0, 1, 2), (3, 4, 5), (6, 7, 8))
MAX_EXACT_NODES = 500_000
ATTEMPT_SECONDS = 20
HISTORICAL_CONTROL_PATHS = {
    "ops/research-team/PROTOCOL.md",
    "ops/research-team/verify_cycle_protocol.py",
    "ops/team/d9-factor19069-singular-df-multihomogeneous-certificate/RESULT.json",
}


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def digest_path(path: Path) -> str:
    state = sha256()
    with path.open("rb") as source:
        for block in iter(lambda: source.read(1 << 20), b""):
            state.update(block)
    return state.hexdigest()


def source_digest(relative: str) -> str:
    if relative in HISTORICAL_CONTROL_PATHS:
        frozen = subprocess.check_output(
            ["git", "show", f"{OPENING_REVISION}:{relative}"], cwd=ROOT
        )
        return sha256(frozen).hexdigest()
    return digest_path(ROOT / relative)


def canonical_digest(value) -> str:
    return sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode("ascii")).hexdigest()


def add_semantic(value: dict) -> dict:
    value["semantic_sha256"] = canonical_digest(value)
    return value


def without_semantic(value: dict) -> dict:
    answer = deepcopy(value)
    answer.pop("semantic_sha256", None)
    return answer


def json_bytes(value) -> bytes:
    return (json.dumps(value, indent=2, sort_keys=True) + "\n").encode("utf-8")


def sparse_normalize(terms: list[dict], exponent_key: str = "exponents") -> list[dict]:
    accumulator: dict[tuple[int, ...], int] = {}
    for term in terms:
        key = tuple(term[exponent_key])
        accumulator[key] = accumulator.get(key, 0) + int(term["coefficient"])
    return [
        {"coefficient": coefficient, "exponents": list(exponent)}
        for exponent, coefficient in sorted(accumulator.items())
        if coefficient
    ]


def sparse_derivative(terms: list[dict], coordinate: int) -> list[dict]:
    answer = []
    for term in terms:
        power = term["exponents"][coordinate]
        if power:
            exponent = list(term["exponents"])
            exponent[coordinate] -= 1
            answer.append({"coefficient": term["coefficient"] * power, "exponents": exponent})
    return sparse_normalize(answer)


def sparse_scale(terms: list[dict], coefficient: int) -> list[dict]:
    return sparse_normalize([
        {"coefficient": coefficient * term["coefficient"], "exponents": term["exponents"]}
        for term in terms
    ])


def sparse_add(*polynomials: list[dict]) -> list[dict]:
    return sparse_normalize([deepcopy(term) for polynomial in polynomials for term in polynomial])


def sparse_multiply_coordinate(terms: list[dict], coordinate: int, coefficient: int = 1) -> list[dict]:
    answer = []
    for term in terms:
        exponent = list(term["exponents"])
        exponent[coordinate] += 1
        answer.append({"coefficient": coefficient * term["coefficient"], "exponents": exponent})
    return sparse_normalize(answer)


def sparse_node(node_id: str, coordinate_order: tuple[str, ...], terms: list[dict], **extra) -> dict:
    node = {
        "node_id": node_id,
        "coefficient_field": "Q",
        "coordinate_order": list(coordinate_order),
        "term_count": len(terms),
        "sparse_polynomial": terms,
        **extra,
    }
    return add_semantic(node)


def lift_terms(affine_terms: list[dict]) -> list[dict]:
    lifted = []
    for term in affine_terms:
        exponent = [0] * 12
        for affine_index, hom_index in enumerate(AFFINE_TO_HOM):
            exponent[hom_index] = term["exponents"][affine_index]
        for block_index, block in enumerate(BLOCK_AFFINE_INDICES):
            exponent[(3, 7, 11)[block_index]] = 2 - sum(term["exponents"][i] for i in block)
        require(all(power >= 0 for power in exponent), "negative homogenizer exponent")
        lifted.append({"coefficient": term["coefficient"], "exponents": exponent})
    answer = sparse_normalize(lifted)
    require(len(answer) == 108, "trihomogenized term collision")
    return answer


def specialize_chart(terms: list[dict], pivot_indices: tuple[int, int, int]) -> tuple[tuple[str, ...], list[dict]]:
    pivot_set = set(pivot_indices)
    free_indices = tuple(index for index in range(12) if index not in pivot_set)
    free_coordinates = tuple(VARIABLES[index] for index in free_indices)
    specialized = []
    for term in terms:
        specialized.append({
            "coefficient": term["coefficient"],
            "exponents": [term["exponents"][index] for index in free_indices],
        })
    return free_coordinates, sparse_normalize(specialized)


def chart_id(pivot_offsets: tuple[int, int, int]) -> str:
    index = pivot_offsets[0] * 16 + pivot_offsets[1] * 4 + pivot_offsets[2]
    pivots = (BLOCKS[0][pivot_offsets[0]], BLOCKS[1][pivot_offsets[1]], BLOCKS[2][pivot_offsets[2]])
    return f"JCH-{index:02d}-{'-'.join(pivots)}"


def overlap_records(source_offsets: tuple[int, int, int]) -> list[dict]:
    source_pivots = tuple(BLOCKS[i][source_offsets[i]] for i in range(3))
    records = []
    for target_offsets in product(range(4), repeat=3):
        if target_offsets == source_offsets:
            continue
        target_pivots = tuple(BLOCKS[i][target_offsets[i]] for i in range(3))
        transitions = []
        for block_index, (source, target) in enumerate(zip(source_pivots, target_pivots)):
            if source != target:
                transitions.append({
                    "block_index": block_index,
                    "source_pivot": source,
                    "target_pivot": target,
                    "required_nonzero_source_coordinate": target,
                    "target_normalization_scale": f"1/{target}",
                })
        records.append({
            "target_chart_id": chart_id(target_offsets),
            "required_nonzero_coordinates": [item["required_nonzero_source_coordinate"] for item in transitions],
            "block_transitions": transitions,
            "overlap_status": "EXPLICIT_NONEMPTY_PRINCIPAL_OPEN_WHEN_REQUIREMENTS_HOLD",
        })
    require(len(records) == 63, "overlap count")
    return records


def boundary_records(pivots: tuple[str, str, str]) -> tuple[list[str], list[dict]]:
    available = [homogenizer for homogenizer, pivot in zip(HOMOGENIZERS, pivots) if homogenizer != pivot]
    records = []
    for bitmask in range(1, 1 << len(available)):
        subset = [available[index] for index in range(len(available)) if bitmask & (1 << index)]
        records.append({
            "boundary_bitmask": bitmask,
            "zero_homogenizers": subset,
            "boundary_subset": [f"{coordinate}=0" for coordinate in subset],
            "stratum_tag": "BOUNDARY_" + "_".join(subset).upper() + "_ZERO",
            "status": "RETAINED",
            "retention_status": "RETAINED_FOR_EXACT_CHART_DECOMPOSITION",
        })
    return available, records


def reconstruct_source(predecessor: dict) -> tuple[list[dict], list[dict], list[dict]]:
    require(predecessor["semantic_sha256"] == PREDECESSOR_SEMANTIC_SHA256, "predecessor semantic drift")
    require(predecessor["theorem_ledger"] == "2/9", "predecessor ledger drift")
    ideal = predecessor["original_singular_jacobian_ideal"]
    require(ideal["generator_count"] == 10 and ideal["inverse_variables"] == 0, "predecessor ideal drift")
    affine_terms = deepcopy(ideal["generators"][0]["sparse_polynomial"])
    require(len(affine_terms) == 108, "affine source term count")
    affine_derivatives = []
    for index, variable in enumerate(AFFINE_VARIABLES):
        derivative = sparse_derivative(affine_terms, index)
        inherited = ideal["generators"][index + 1]
        require(inherited["coordinate"] == variable, "affine derivative coordinate drift")
        require(inherited["sparse_polynomial"] == derivative, f"affine derivative drift: {variable}")
        affine_derivatives.append(derivative)
    parent_records = predecessor["parent_factor_incidence_frontier"]["records"]
    require(len(parent_records) == 70, "parent factor count")
    return affine_terms, affine_derivatives, deepcopy(parent_records)


def build_chart(offsets: tuple[int, int, int], homogeneous_terms: list[dict]) -> dict:
    index = offsets[0] * 16 + offsets[1] * 4 + offsets[2]
    pivots = tuple(BLOCKS[block][offsets[block]] for block in range(3))
    pivot_indices = tuple((0, 4, 8)[block] + offsets[block] for block in range(3))
    free_coordinates, chart_terms = specialize_chart(homogeneous_terms, pivot_indices)
    f_node = sparse_node(f"{chart_id(offsets)}:F", free_coordinates, chart_terms)
    derivative_nodes = []
    for coordinate_index, coordinate in enumerate(free_coordinates):
        derivative_nodes.append(sparse_node(
            f"{chart_id(offsets)}:dF_d{coordinate}",
            free_coordinates,
            sparse_derivative(chart_terms, coordinate_index),
            derivative_coordinate=coordinate,
            derivative_coordinate_index=coordinate_index,
        ))

    euler_records = []
    for block_index, pivot in enumerate(pivots):
        global_pivot_index = VARIABLES.index(pivot)
        _, direct_terms = specialize_chart(sparse_derivative(homogeneous_terms, global_pivot_index), pivot_indices)
        recovered = sparse_scale(chart_terms, 2)
        free_block = [coordinate for coordinate in BLOCKS[block_index] if coordinate != pivot]
        for coordinate in free_block:
            local_index = free_coordinates.index(coordinate)
            recovered = sparse_add(recovered, sparse_multiply_coordinate(
                derivative_nodes[local_index]["sparse_polynomial"], local_index, -1
            ))
        require(recovered == direct_terms, f"Euler recovery failed: {chart_id(offsets)} {pivot}")
        direct_node = sparse_node(
            f"{chart_id(offsets)}:specialized_dF_d{pivot}", free_coordinates, direct_terms,
            derivative_coordinate=pivot,
        )
        recovered_node = sparse_node(
            f"{chart_id(offsets)}:euler_recovered_dF_d{pivot}", free_coordinates, recovered,
            derivative_coordinate=pivot,
        )
        residual = sparse_add(direct_terms, sparse_scale(recovered, -1))
        require(residual == [], f"Euler residual nonzero: {chart_id(offsets)} {pivot}")
        residual_node = sparse_node(
            f"{chart_id(offsets)}:euler_residual_{pivot}", free_coordinates, residual,
            derivative_coordinate=pivot,
        )
        euler_records.append(add_semantic({
            "block_index": block_index,
            "pivot": pivot,
            "block_degree": 2,
            "identity": f"(dF/d{pivot})|_{pivot}=2*F_chart-sum(x*dF_chart/dx for free x in block {block_index})",
            "free_block_coordinates": free_block,
            "direct_specialization": direct_node,
            "euler_reconstruction": recovered_node,
            "exact_zero_residual": residual_node,
            "exact_sparse_equality": True,
            "forward_ideal_consequence": "PIVOT_DERIVATIVE_LIES_IN_<F_CHART,NINE_FREE_DERIVATIVES>",
            "converse_ideal_consequence": "2*F_CHART_LIES_IN_<ALL_TWELVE_SPECIALIZED_HOMOGENEOUS_DERIVATIVES>_SO_F_CHART_LIES_THERE_OVER_Q",
            "exact_ideal_equality": "<F_CHART,NINE_FREE_DERIVATIVES>=<ALL_TWELVE_SPECIALIZED_HOMOGENEOUS_DERIVATIVES>",
        }))

    available, strata = boundary_records(pivots)
    chart = {
        "chart_index": index,
        "chart_id": chart_id(offsets),
        "ambient": "(P^3)^3",
        "pivot_offsets": list(offsets),
        "pivots": list(pivots),
        "pivot_global_indices": list(pivot_indices),
        "pivot_substitution": {pivot: 1 for pivot in pivots},
        "free_coordinates": list(free_coordinates),
        "free_coordinate_count": 9,
        "coverage_tag": "STANDARD_PRODUCT_CHART_D(" + "*".join(pivots) + ")",
        "affine_source_chart": pivots == HOMOGENIZERS,
        "forced_nonzero_original_coordinates": [pivot for pivot in pivots if pivot not in HOMOGENIZERS],
        "boundary_homogenizers": available,
        "boundary_hyperplanes_available": available,
        "boundary_hyperplanes_excluded_by_pivot": [h for h, p in zip(HOMOGENIZERS, pivots) if h == p],
        "chart_is_wholly_infinity": False,
        "contains_affine_overlap": True,
        "boundary_strata": strata,
        "boundary_retention_status": "ALL_AVAILABLE_INFINITY_BOUNDARY_STRATA_RETAINED",
        "overlap_records": overlap_records(offsets),
        "overlap_record_count": 63,
        "F_chart": f_node,
        "free_derivatives": derivative_nodes,
        "chart_jacobian_ideal": {
            "ring": "Q[" + ",".join(free_coordinates) + "]",
            "coefficient_field": "Q",
            "generator_count": 10,
            "generator_node_ids": [f_node["node_id"]] + [node["node_id"] for node in derivative_nodes],
            "definition": "<F_chart, all nine free-coordinate derivatives>",
        },
        "euler_pivot_recoveries": euler_records,
        "euler_recovery_count": 3,
        "euler_zero_residual_count": 3,
        "full_projective_jacobian_transfer_proved": True,
        "component_decomposition_status": "PENDING_BOUNDED_CHARACTERISTIC_ZERO_ATTEMPT",
        "accepted_components": [],
        "embedded_components_discarded": 0,
        "boundary_strata_discarded": 0,
    }
    chart["chart_jacobian_ideal"] = add_semantic(chart["chart_jacobian_ideal"])
    return add_semantic(chart)


def build_manifest(audit: dict) -> dict:
    require(audit["base_revision"] == BASE_REVISION and audit["base_tree"] == BASE_TREE, "base drift")
    require(audit["opening_ledger"] == "2/9", "opening ledger drift")
    require(audit["target"]["standard_chart_count"] == 64, "chart contract drift")
    require(audit["target"]["parent_sign_factors"] == 70, "parent count contract drift")
    pins = dict(audit["pins"])
    for name in ("CYCLE.md", "OPENING_AUDIT.json", "OBLIGATION_GRAPH.json", "WORK_ORDERS.yaml"):
        relative = f"ops/research-team/cycles/{CYCLE_ID}/{name}"
        pins[relative] = digest_path(ROOT / relative)
    for relative, expected in pins.items():
        require(source_digest(relative) == expected, f"source pin drift: {relative}")
    require(pins[str(PREDECESSOR.relative_to(ROOT)).replace('\\', '/')] == PREDECESSOR_SHA256, "predecessor pin mismatch")
    return add_semantic({
        "format": "d9-factor19069-explicit-trihom-jacobian-chart-constructor-source-manifest-v1",
        "track_id": "d9-factor19069-explicit-trihom-jacobian-chart-constructor",
        "cycle_id": CYCLE_ID,
        "cycle_opening_revision": OPENING_REVISION,
        "cycle_opening_tree": OPENING_TREE,
        "canonical_base_revision": BASE_REVISION,
        "canonical_base_tree": BASE_TREE,
        "pins": dict(sorted(pins.items())),
        "source_policy": {
            "predecessor_json_is_only_polynomial_source": True,
            "predecessor_builder_code_imported": False,
            "all_64_charts_constructed_without_symmetry_quotient": True,
            "network_or_connector_used": False,
            "numerical_or_modular_probe_used": False,
            "seventy_inverse_variable_discovery_used": False,
            "trihomogenization_used_as_decomposition_certificate": False,
        },
    })


def sympy_worker(chart_index: int) -> None:
    import sympy as sp
    predecessor = json.loads(PREDECESSOR.read_text(encoding="utf-8"))
    affine_terms, _, _ = reconstruct_source(predecessor)
    homogeneous_terms = lift_terms(affine_terms)
    offsets = (chart_index // 16, (chart_index // 4) % 4, chart_index % 4)
    pivots = tuple((0, 4, 8)[block] + offsets[block] for block in range(3))
    free, terms = specialize_chart(homogeneous_terms, pivots)
    symbols = sp.symbols(" ".join(free))
    polynomial = sum(sp.Integer(t["coefficient"]) * sp.prod(s ** p for s, p in zip(symbols, t["exponents"])) for t in terms)
    generators = [polynomial] + [sp.diff(polynomial, symbol) for symbol in symbols]
    basis = sp.groebner(generators, *symbols, order="grevlex", domain=sp.QQ)
    basis_strings = [str(poly.as_expr()) for poly in basis.polys]
    payload = {
        "status": "GROEBNER_BASIS_COMPLETED_PRIMARY_DECOMPOSITION_STILL_PENDING",
        "basis_count": len(basis_strings),
        "basis_semantic_sha256": canonical_digest(basis_strings),
        "is_zero_dimensional": bool(basis.is_zero_dimensional),
    }
    print(json.dumps(payload, sort_keys=True))


def run_bounded_attempt(chart: dict) -> dict:
    command = [sys.executable, str(Path(__file__).resolve()), "--sympy-worker", str(chart["chart_index"])]
    base = {
        "attempted_chart_id": chart["chart_id"],
        "coefficient_field": "Q",
        "monomial_order": "grevlex",
        "engine": "SymPy exact Groebner over QQ in isolated subprocess",
        "purpose": "GROEBNER_PREREQUISITE_FOR_CHARACTERISTIC_ZERO_PRIMARY_DECOMPOSITION",
        "wall_seconds_ceiling": ATTEMPT_SECONDS,
        "exact_algebra_component_node_ceiling": MAX_EXACT_NODES,
        "primary_decomposition_completed": False,
        "component_count": None,
        "embedded_component_count": None,
        "accepted_as_decomposition_certificate": False,
    }
    try:
        completed = subprocess.run(command, capture_output=True, text=True, timeout=ATTEMPT_SECONDS, check=False)
    except subprocess.TimeoutExpired:
        return add_semantic({
            **base,
            "status": "TIMEOUT_FIRST_CHART_GROEBNER_PREREQUISITE_PENDING",
            "ceiling_triggered": "WALL_SECONDS",
            "subprocess_exit_code": None,
            "first_pending_stage": "CHARACTERISTIC_ZERO_GROEBNER_PREREQUISITE",
        })
    if completed.returncode != 0:
        return add_semantic({
            **base,
            "status": "FAIL_CLOSED_EXACT_ENGINE_ERROR",
            "ceiling_triggered": None,
            "subprocess_exit_code": completed.returncode,
            "stderr_sha256": sha256(completed.stderr.encode("utf-8")).hexdigest(),
            "first_pending_stage": "CHARACTERISTIC_ZERO_GROEBNER_PREREQUISITE",
        })
    payload = json.loads(completed.stdout.strip().splitlines()[-1])
    return add_semantic({
        **base,
        **payload,
        "ceiling_triggered": None,
        "subprocess_exit_code": 0,
        "first_pending_stage": "CHARACTERISTIC_ZERO_PRIMARY_AND_EMBEDDED_DECOMPOSITION",
    })


def build_frontier(predecessor: dict, manifest: dict, attempt: dict) -> dict:
    affine_terms, affine_derivatives, inherited_parent_records = reconstruct_source(predecessor)
    homogeneous_terms = lift_terms(affine_terms)
    homogeneous_node = sparse_node(
        "F_19069_trihom_222", VARIABLES, homogeneous_terms,
        multidegree=[2, 2, 2], blocks=[list(block) for block in BLOCKS],
    )
    for term in homogeneous_terms:
        require([sum(term["exponents"][i:i + 4]) for i in (0, 4, 8)] == [2, 2, 2], "tridegree failure")
    dehom_free, dehom_terms = specialize_chart(homogeneous_terms, (3, 7, 11))
    require(dehom_free == AFFINE_VARIABLES and dehom_terms == affine_terms, "affine dehomogenization failure")

    charts = [build_chart(offsets, homogeneous_terms) for offsets in product(range(4), repeat=3)]
    require([chart["chart_index"] for chart in charts] == list(range(64)), "chart stable order")
    require(len({tuple(chart["pivots"]) for chart in charts}) == 64, "chart cover duplicate")
    affine_chart = charts[63]
    require(affine_chart["pivots"] == ["u", "v", "w"], "affine chart position")
    require(affine_chart["F_chart"]["sparse_polynomial"] == affine_terms, "affine F equality")
    for index, derivative in enumerate(affine_derivatives):
        require(affine_chart["free_derivatives"][index]["sparse_polynomial"] == derivative, "affine derivative equality")

    for chart in charts:
        if chart["chart_id"] == attempt["attempted_chart_id"]:
            chart["component_decomposition_status"] = attempt["status"]
        else:
            chart["component_decomposition_status"] = "NOT_STARTED_AFTER_FIRST_PENDING_CHART_STOP_RULE"
        chart["semantic_sha256"] = canonical_digest(without_semantic(chart))

    atlas = add_semantic({
        "ambient": "(P^3)^3",
        "block_coordinate_order": [list(block) for block in BLOCKS],
        "standard_chart_count": 64,
        "chart_order": [chart["chart_id"] for chart in charts],
        "charts": charts,
        "directed_overlap_record_count": 64 * 63,
        "affine_chart_id": affine_chart["chart_id"],
        "charts_intersecting_at_least_one_boundary_hyperplane": sum(bool(c["boundary_hyperplanes_available"]) for c in charts),
        "local_nonempty_boundary_intersection_record_count": sum(len(c["boundary_strata"]) for c in charts),
        "expected_local_nonempty_boundary_intersection_record_count": 279,
        "boundary_stratum_record_count": sum(len(c["boundary_strata"]) for c in charts),
        "global_boundary_types": [
            ["u"], ["v"], ["w"], ["u", "v"], ["u", "w"], ["v", "w"], ["u", "v", "w"]
        ],
        "global_nonempty_boundary_type_count": 7,
        "global_boundary_subsets": [
            ["u=0"], ["v=0"], ["w=0"], ["u=0", "v=0"], ["u=0", "w=0"], ["v=0", "w=0"], ["u=0", "v=0", "w=0"]
        ],
        "all_product_charts_retained": True,
        "all_available_boundary_strata_retained": True,
        "symmetry_quotient_used": False,
    })
    require(atlas["local_nonempty_boundary_intersection_record_count"] == 279, "local boundary census")

    affine_transfer = add_semantic({
        "chart_id": affine_chart["chart_id"],
        "pivot_substitution": {"u": 1, "v": 1, "w": 1},
        "free_coordinate_order": list(AFFINE_VARIABLES),
        "F_chart_equals_original_f_19069": True,
        "nine_chart_derivatives_equal_original_affine_derivatives": True,
        "chart_ideal_equals_original_affine_singular_ideal": True,
        "original_ideal_generator_count": 10,
        "chart_ideal_generator_count": 10,
        "original_ideal_semantic_sha256": predecessor["original_singular_jacobian_ideal"]["semantic_sha256"],
        "chart_ideal_semantic_sha256": affine_chart["chart_jacobian_ideal"]["semantic_sha256"],
        "proof_method": "EXACT_SPARSE_COEFFICIENT_EQUALITY_IN_Q[a,b,c,d,e,f,g,h,i]",
    })

    first_branch = add_semantic({
        "branch_id": f"DEC-{attempt['attempted_chart_id']}",
        "chart_id": attempt["attempted_chart_id"],
        "status": attempt["status"],
        "first_pending_stage": attempt["first_pending_stage"],
        "attempt_semantic_sha256": attempt["semantic_sha256"],
        "characteristic_zero": True,
        "complete_primary_or_equidimensional_decomposition": False,
        "embedded_component_accounting_completed": False,
        "component_count": None,
        "accepted_components": [],
        "singular_or_boundary_strata_discarded": 0,
        "stop_rule": "HASH_PIN_FIRST_PENDING_CHART_AND_STOP_LATER_DECOMPOSITIONS",
    })
    branch_order = [f"DEC-{chart['chart_id']}" for chart in charts]
    decomposition = add_semantic({
        "coefficient_field": "Q",
        "required_characteristic": 0,
        "branch_order": branch_order,
        "attempt": attempt,
        "first_pending_branch": first_branch,
        "first_pending_branch_id": first_branch["branch_id"],
        "first_pending_branch_semantic_sha256": first_branch["semantic_sha256"],
        "resolved_chart_count": 0,
        "pending_chart_count": 64,
        "accepted_component_count": 0,
        "embedded_components_discarded": 0,
        "boundary_strata_discarded": 0,
        "complete_projective_decomposition": False,
        "groebner_basis_is_not_a_primary_decomposition": True,
    })

    parent_records = []
    for record in inherited_parent_records:
        inherited = deepcopy(record)
        inherited["componentwise_incidence_status"] = "PENDING_NO_ACCEPTED_CONTRACTED_AFFINE_COMPONENT"
        inherited["strict_sign_status"] = "PENDING_NO_ACCEPTED_CONTRACTED_AFFINE_COMPONENT"
        inherited["boundary_stratum_status"] = "PRESERVED_SOURCE_TAG_NO_COMPONENT_TEST"
        inherited["semantic_sha256"] = canonical_digest(without_semantic(inherited))
        parent_records.append(inherited)
    parent_frontier = add_semantic({
        "ordered_factor_count": 70,
        "records": parent_records,
        "source_record_order_preserved": True,
        "source_parent_factor_tags_preserved": True,
        "required_tests_per_future_contracted_component": 70,
        "accepted_contracted_component_count": 0,
        "completed_component_factor_pairs": 0,
        "testing_order_policy": "PULL_BACK_ACCEPTED_AFFINE_COMPONENT_TO_ORIGINAL_AFFINE_SINGULAR_IDEAL_BEFORE_ANY_PARENT_TEST",
        "inverse_variable_discovery_used": False,
    })
    contraction = add_semantic({
        "accepted_projective_component_count": 0,
        "accepted_affine_component_count": 0,
        "contracted_to_original_affine_singular_ideal_count": 0,
        "componentwise_parent_tests_started": 0,
        "pending_reason": "NO_COMPLETE_CHARACTERISTIC_ZERO_CHART_DECOMPOSITION",
        "mandatory_order": [
            "COMPLETE_EXACT_CHART_DECOMPOSITION",
            "DEDUPLICATE_ON_EXPLICIT_OVERLAPS_WITH_MULTIPLICITY_AND_BOUNDARY_TAGS",
            "RESTRICT_TO_AFFINE_u_v_w_NONZERO_LOCUS",
            "DEHOMOGENIZE_AND_CONTRACT_TO_Q[a,b,c,d,e,f,g,h,i]",
            "VERIFY_CONTAINMENT_IN_ORIGINAL_AFFINE_SINGULAR_IDEAL",
            "TEST_COMPONENTWISE_AGAINST_ALL_70_PARENT_FACTORS",
        ],
        "order_respected": True,
    })

    timeout = attempt["status"].startswith("TIMEOUT")
    endpoint = "HASH_PIN_ALL_COMPLETED_CHART_BRANCHES_AND_FIRST_PENDING_BRANCH" if timeout else "FIRST_SOURCE_PINNED_UNRESOLVED_PROJECTIVE_CHART_DECOMPOSITION_BRANCH"
    artifact = {
        "format": "d9-factor19069-explicit-trihom-jacobian-chart-constructor-frontier-v1",
        "track_id": "d9-factor19069-explicit-trihom-jacobian-chart-constructor",
        "cycle_id": CYCLE_ID,
        "opening_revision": OPENING_REVISION,
        "opening_tree": OPENING_TREE,
        "base_revision": BASE_REVISION,
        "base_tree": BASE_TREE,
        "outcome": "pass",
        "classification": "BOUNDED_CHARACTERISTIC_ZERO_CHART_DECOMPOSITION_TIMEOUT_FAIL_CLOSED" if timeout else "EXACT_CHART_CONSTRUCTION_COMPLETE_DECOMPOSITION_FAIL_CLOSED_NULL",
        "endpoint": endpoint,
        "theorem_ledger": "2/9",
        "ledger_change_recommended": "none",
        "source_manifest_semantic_sha256": manifest["semantic_sha256"],
        "predecessor_binding": {
            "path": str(PREDECESSOR.relative_to(ROOT)).replace("\\", "/"),
            "file_sha256": PREDECESSOR_SHA256,
            "predecessor_semantic_sha256": PREDECESSOR_SEMANTIC_SHA256,
        },
        "trihomogeneous_source": add_semantic({
            "ring": "Q[a,b,c,u,d,e,f,v,g,h,i,w]",
            "blocks": [list(block) for block in BLOCKS],
            "multidegree": [2, 2, 2],
            "term_count": 108,
            "polynomial": homogeneous_node,
            "dehomogenization_identity": "F(a,b,c,1,d,e,f,1,g,h,i,1)=f_19069",
            "dehomogenization_exact_sparse_equality": True,
            "affine_source_is_homogeneous": False,
            "affine_source_is_multiaffine": False,
            "trihomogenization_is_decomposition_certificate": False,
        }),
        "chart_atlas": atlas,
        "affine_transfer": affine_transfer,
        "decomposition_frontier": decomposition,
        "affine_contraction_frontier": contraction,
        "parent_factor_incidence_frontier": parent_frontier,
        "preserved_predecessor_strata": add_semantic({
            "true_boundary_frontier": deepcopy(predecessor["preserved_boundary_frontier"]),
            "fixed_skeleton_accounting": deepcopy(predecessor["preserved_fixed_skeleton_accounting"]),
            "verified_null_frontier": deepcopy(predecessor["preserved_null_frontier"]),
            "source_tags_preserved": True,
            "strata_discarded": 0,
        }),
        "endpoint_accounting": {
            "positive": "NOT_REACHED_NO_EXACT_STRICT_PARENT_SINGULAR_EMPTINESS",
            "negative": "NOT_REACHED_NO_EXACT_POSITIVE_DIMENSIONAL_STRICT_REAL_SINGULAR_COMPONENT",
            "null": "NOT_REACHED" if timeout else "REACHED_FIRST_SOURCE_PINNED_UNRESOLVED_PROJECTIVE_CHART_DECOMPOSITION_BRANCH",
            "timeout": "REACHED_HASH_PINNED_FIRST_PENDING_CHART" if timeout else "NOT_REACHED",
        },
        "resource_accounting": {
            "cycle_max_exact_algebra_component_nodes": MAX_EXACT_NODES,
            "decomposition_attempt_wall_seconds_ceiling": ATTEMPT_SECONDS,
            "attempted_chart_count": 1,
            "completed_chart_decomposition_count": 0,
            "sympy_external_venv_used": True,
            "network_or_connector_used": False,
            "paid_external_compute_used": False,
            "numerical_or_modular_probe_used": False,
            "seventy_inverse_variable_discovery_used": False,
        },
        "nonconsequences": [
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
        ],
    }
    return add_semantic(artifact)


def build_result(artifact: dict, manifest: dict) -> dict:
    frontier = artifact["decomposition_frontier"]
    return {
        "format": "d9-factor19069-explicit-trihom-jacobian-chart-constructor-result-v1",
        "track_id": artifact["track_id"],
        "cycle_id": CYCLE_ID,
        "opening_revision": OPENING_REVISION,
        "opening_tree": OPENING_TREE,
        "outcome": "pass",
        "classification": artifact["classification"],
        "endpoint": artifact["endpoint"],
        "frontier_sha256": digest_path(FRONTIER),
        "frontier_semantic_sha256": artifact["semantic_sha256"],
        "source_manifest_sha256": digest_path(MANIFEST),
        "source_manifest_semantic_sha256": manifest["semantic_sha256"],
        "trihomogeneous_source_terms": 108,
        "standard_chart_count": 64,
        "directed_overlap_record_count": 4032,
        "charts_with_three_euler_recoveries": 64,
        "affine_original_ideal_equality_proved": True,
        "characteristic_zero_decomposition_completed": False,
        "first_pending_branch_id": frontier["first_pending_branch_id"],
        "first_pending_branch_semantic_sha256": frontier["first_pending_branch_semantic_sha256"],
        "accepted_component_count": 0,
        "embedded_components_discarded": 0,
        "boundary_strata_discarded": 0,
        "accepted_affine_component_contractions": 0,
        "componentwise_parent_factor_tests_completed": 0,
        "parent_factor_records_retained": 70,
        "inverse_variable_discovery_used": False,
        "ledger_change_recommended": "none",
        "theorem_ledger": "2/9",
        "nonconsequences": artifact["nonconsequences"],
    }


def write_or_check(path: Path, payload: bytes, check: bool) -> None:
    if check:
        require(path.read_bytes() == payload, f"byte replay drift: {path.name}")
    else:
        path.write_bytes(payload)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--reuse-attempt", action="store_true")
    parser.add_argument("--sympy-worker", type=int)
    args = parser.parse_args()
    if args.sympy_worker is not None:
        sympy_worker(args.sympy_worker)
        return
    require(digest_path(PREDECESSOR) == PREDECESSOR_SHA256, "predecessor file drift")
    audit = json.loads((CYCLE / "OPENING_AUDIT.json").read_text(encoding="utf-8"))
    predecessor = json.loads(PREDECESSOR.read_text(encoding="utf-8"))
    manifest = build_manifest(audit)
    if args.check or args.reuse_attempt:
        saved = json.loads(FRONTIER.read_text(encoding="utf-8"))
        attempt = saved["decomposition_frontier"]["attempt"]
    else:
        affine_terms, _, _ = reconstruct_source(predecessor)
        first_chart = build_chart((0, 0, 0), lift_terms(affine_terms))
        attempt = run_bounded_attempt(first_chart)
    artifact = build_frontier(predecessor, manifest, attempt)
    write_or_check(MANIFEST, json_bytes(manifest), args.check)
    write_or_check(FRONTIER, json_bytes(artifact), args.check)
    result = build_result(artifact, manifest)
    write_or_check(RESULT, json_bytes(result), args.check)
    print(f"frontier_semantic_sha256={artifact['semantic_sha256']}")
    print(f"charts={artifact['chart_atlas']['standard_chart_count']} overlaps={artifact['chart_atlas']['directed_overlap_record_count']}")
    print(f"decomposition_attempt={attempt['status']}")
    print(f"first_pending_branch={artifact['decomposition_frontier']['first_pending_branch_id']}")
    print(f"endpoint={artifact['endpoint']} ledger=2/9")


if __name__ == "__main__":
    main()
