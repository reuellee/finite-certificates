#!/usr/bin/env python3
"""Independent exact verifier for the factor-19069 64-chart frontier."""

from __future__ import annotations

from copy import deepcopy
from hashlib import sha256
from itertools import product
import json
from pathlib import Path
import subprocess


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
PREDECESSOR = ROOT / "ops" / "team" / "d9-factor19069-singular-df-multihomogeneous-constructor" / "SINGULAR_DF_MULTIHOMOGENEOUS_FRONTIER.json"
FRONTIER = HERE / "PROJECTIVE_CHART_FRONTIER.json"
MANIFEST = HERE / "SOURCE_MANIFEST.json"
RESULT = HERE / "RESULT.json"
EXPECTED_PREDECESSOR_SHA256 = "d9f4aba3fa8c76e3a8abff5484ff509b0458fe9993edeb921e5a6d03c4dfac41"
VARIABLES = ("a", "b", "c", "u", "d", "e", "f", "v", "g", "h", "i", "w")
BLOCKS = (VARIABLES[0:4], VARIABLES[4:8], VARIABLES[8:12])
HOMOGENIZERS = ("u", "v", "w")
AFFINE_VARIABLES = tuple("abcdefghi")
AFFINE_TO_HOM = (0, 1, 2, 4, 5, 6, 8, 9, 10)
BLOCK_AFFINE_INDICES = ((0, 1, 2), (3, 4, 5), (6, 7, 8))
OPENING_REVISION = "cd2d856d3ccff51f7b5d6841702b25d191ed9985"
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


def without_semantic(value: dict) -> dict:
    answer = deepcopy(value)
    del answer["semantic_sha256"]
    return answer


def validate_semantics(value, location="root") -> None:
    if isinstance(value, list):
        for index, item in enumerate(value):
            validate_semantics(item, f"{location}[{index}]")
    elif isinstance(value, dict):
        for key, item in value.items():
            if key != "semantic_sha256":
                validate_semantics(item, f"{location}.{key}")
        if "semantic_sha256" in value:
            require(value["semantic_sha256"] == canonical_digest(without_semantic(value)), f"semantic digest: {location}")


def normalize(terms: list[dict]) -> list[dict]:
    accumulator = {}
    for term in terms:
        exponent = tuple(term["exponents"])
        accumulator[exponent] = accumulator.get(exponent, 0) + int(term["coefficient"])
    return [
        {"coefficient": coefficient, "exponents": list(exponent)}
        for exponent, coefficient in sorted(accumulator.items())
        if coefficient
    ]


def derivative(terms: list[dict], coordinate: int) -> list[dict]:
    answer = []
    for term in terms:
        power = term["exponents"][coordinate]
        if power:
            exponent = list(term["exponents"])
            exponent[coordinate] -= 1
            answer.append({"coefficient": term["coefficient"] * power, "exponents": exponent})
    return normalize(answer)


def add(*polynomials: list[dict]) -> list[dict]:
    return normalize([deepcopy(term) for polynomial in polynomials for term in polynomial])


def scale(terms: list[dict], coefficient: int) -> list[dict]:
    return normalize([{"coefficient": coefficient * t["coefficient"], "exponents": t["exponents"]} for t in terms])


def multiply_coordinate(terms: list[dict], coordinate: int, coefficient=-1) -> list[dict]:
    answer = []
    for term in terms:
        exponent = list(term["exponents"])
        exponent[coordinate] += 1
        answer.append({"coefficient": coefficient * term["coefficient"], "exponents": exponent})
    return normalize(answer)


def lift(affine_terms: list[dict]) -> list[dict]:
    answer = []
    for term in affine_terms:
        exponent = [0] * 12
        for affine_index, homogeneous_index in enumerate(AFFINE_TO_HOM):
            exponent[homogeneous_index] = term["exponents"][affine_index]
        for block_index, affine_block in enumerate(BLOCK_AFFINE_INDICES):
            exponent[(3, 7, 11)[block_index]] = 2 - sum(term["exponents"][i] for i in affine_block)
        answer.append({"coefficient": term["coefficient"], "exponents": exponent})
    return normalize(answer)


def specialize(terms: list[dict], pivot_indices: tuple[int, int, int]) -> tuple[tuple[str, ...], list[dict]]:
    free_indices = tuple(i for i in range(12) if i not in set(pivot_indices))
    return (
        tuple(VARIABLES[i] for i in free_indices),
        normalize([{
            "coefficient": term["coefficient"],
            "exponents": [term["exponents"][i] for i in free_indices],
        } for term in terms]),
    )


def expected_chart_id(offsets: tuple[int, int, int]) -> str:
    index = offsets[0] * 16 + offsets[1] * 4 + offsets[2]
    pivots = [BLOCKS[i][offsets[i]] for i in range(3)]
    return f"JCH-{index:02d}-{'-'.join(pivots)}"


def validate_node(node: dict, node_id: str, coordinates: tuple[str, ...], terms: list[dict]) -> None:
    require(node["node_id"] == node_id, f"node id: {node_id}")
    require(node["coefficient_field"] == "Q", f"node field: {node_id}")
    require(node["coordinate_order"] == list(coordinates), f"node coordinates: {node_id}")
    require(node["term_count"] == len(terms), f"node term count: {node_id}")
    require(node["sparse_polynomial"] == terms, f"node sparse polynomial: {node_id}")


def validate_chart(chart: dict, offsets: tuple[int, int, int], homogeneous_terms: list[dict]) -> None:
    index = offsets[0] * 16 + offsets[1] * 4 + offsets[2]
    expected_id = expected_chart_id(offsets)
    pivots = tuple(BLOCKS[i][offsets[i]] for i in range(3))
    pivot_indices = tuple((0, 4, 8)[i] + offsets[i] for i in range(3))
    free, terms = specialize(homogeneous_terms, pivot_indices)
    require(chart["chart_index"] == index and chart["chart_id"] == expected_id, "chart order/id")
    require(chart["pivot_offsets"] == list(offsets), f"pivot offsets: {expected_id}")
    require(chart["pivots"] == list(pivots) and chart["pivot_global_indices"] == list(pivot_indices), f"pivots: {expected_id}")
    require(chart["free_coordinates"] == list(free) and chart["free_coordinate_count"] == 9, f"free coordinates: {expected_id}")
    require(chart["affine_source_chart"] == (pivots == HOMOGENIZERS), f"affine tag: {expected_id}")
    validate_node(chart["F_chart"], f"{expected_id}:F", free, terms)
    require(len(chart["free_derivatives"]) == 9, f"derivative count: {expected_id}")
    derivatives = []
    for local_index, coordinate in enumerate(free):
        expected = derivative(terms, local_index)
        derivatives.append(expected)
        validate_node(chart["free_derivatives"][local_index], f"{expected_id}:dF_d{coordinate}", free, expected)
        require(chart["free_derivatives"][local_index]["derivative_coordinate"] == coordinate, "derivative coordinate")

    require(chart["euler_recovery_count"] == chart["euler_zero_residual_count"] == 3, f"Euler count: {expected_id}")
    for block_index, record in enumerate(chart["euler_pivot_recoveries"]):
        pivot = pivots[block_index]
        direct = specialize(derivative(homogeneous_terms, VARIABLES.index(pivot)), pivot_indices)[1]
        recovered = scale(terms, 2)
        free_block = [coordinate for coordinate in BLOCKS[block_index] if coordinate != pivot]
        for coordinate in free_block:
            local_index = free.index(coordinate)
            recovered = add(recovered, multiply_coordinate(derivatives[local_index], local_index))
        require(record["block_index"] == block_index and record["pivot"] == pivot, f"Euler tag: {expected_id}")
        require(record["free_block_coordinates"] == free_block, f"Euler free block: {expected_id}")
        validate_node(record["direct_specialization"], f"{expected_id}:specialized_dF_d{pivot}", free, direct)
        validate_node(record["euler_reconstruction"], f"{expected_id}:euler_recovered_dF_d{pivot}", free, recovered)
        validate_node(record["exact_zero_residual"], f"{expected_id}:euler_residual_{pivot}", free, [])
        require(direct == recovered and record["exact_sparse_equality"] is True, f"Euler equality: {expected_id}")
        require("exact_ideal_equality" in record and record["block_degree"] == 2, f"Euler ideal transfer: {expected_id}")
    require(chart["full_projective_jacobian_transfer_proved"] is True, f"projective gradient transfer: {expected_id}")

    available = [h for h, p in zip(HOMOGENIZERS, pivots) if h != p]
    excluded = [h for h, p in zip(HOMOGENIZERS, pivots) if h == p]
    require(chart["boundary_homogenizers"] == chart["boundary_hyperplanes_available"] == available, f"boundary available: {expected_id}")
    require(chart["boundary_hyperplanes_excluded_by_pivot"] == excluded, f"boundary excluded: {expected_id}")
    require(chart["chart_is_wholly_infinity"] is False and chart["contains_affine_overlap"] is True, f"boundary geometry: {expected_id}")
    expected_strata = []
    for bitmask in range(1, 1 << len(available)):
        subset = [available[i] for i in range(len(available)) if bitmask & (1 << i)]
        expected_strata.append((bitmask, subset))
    require(len(chart["boundary_strata"]) == len(expected_strata), f"boundary record count: {expected_id}")
    for record, (bitmask, subset) in zip(chart["boundary_strata"], expected_strata):
        require(record["boundary_bitmask"] == bitmask and record["zero_homogenizers"] == subset, f"boundary bitmask: {expected_id}")
        require(record["boundary_subset"] == [f"{x}=0" for x in subset] and record["status"] == "RETAINED", f"boundary retention: {expected_id}")
    require(chart["boundary_strata_discarded"] == chart["embedded_components_discarded"] == 0, f"discarded strata: {expected_id}")

    require(chart["overlap_record_count"] == len(chart["overlap_records"]) == 63, f"overlap count: {expected_id}")
    expected_targets = [expected_chart_id(target) for target in product(range(4), repeat=3) if target != offsets]
    require([record["target_chart_id"] for record in chart["overlap_records"]] == expected_targets, f"overlap order: {expected_id}")
    for record, target in zip(chart["overlap_records"], [t for t in product(range(4), repeat=3) if t != offsets]):
        expected_required = [BLOCKS[i][target[i]] for i in range(3) if target[i] != offsets[i]]
        require(record["required_nonzero_coordinates"] == expected_required, f"overlap requirements: {expected_id}")


def validate(candidate: dict, predecessor: dict) -> None:
    validate_semantics(candidate)
    require(candidate["format"] == "d9-factor19069-explicit-trihom-jacobian-chart-constructor-frontier-v1", "format")
    require(candidate["theorem_ledger"] == "2/9" and candidate["ledger_change_recommended"] == "none", "ledger")
    require(candidate["classification"] == "BOUNDED_CHARACTERISTIC_ZERO_CHART_DECOMPOSITION_TIMEOUT_FAIL_CLOSED", "classification")
    require(candidate["endpoint"] == "HASH_PIN_ALL_COMPLETED_CHART_BRANCHES_AND_FIRST_PENDING_BRANCH", "endpoint")
    affine_terms = predecessor["original_singular_jacobian_ideal"]["generators"][0]["sparse_polynomial"]
    require(len(affine_terms) == 108, "source term count")
    for index in range(9):
        require(predecessor["original_singular_jacobian_ideal"]["generators"][index + 1]["sparse_polynomial"] == derivative(affine_terms, index), "source derivative")
    homogeneous_terms = lift(affine_terms)
    source = candidate["trihomogeneous_source"]
    require(source["term_count"] == 108 and source["multidegree"] == [2, 2, 2], "trihom source census")
    validate_node(source["polynomial"], "F_19069_trihom_222", VARIABLES, homogeneous_terms)
    for term in homogeneous_terms:
        require([sum(term["exponents"][start:start + 4]) for start in (0, 4, 8)] == [2, 2, 2], "tridegree")
    require(source["trihomogenization_is_decomposition_certificate"] is False, "source overclaim")

    atlas = candidate["chart_atlas"]
    require(atlas["standard_chart_count"] == len(atlas["charts"]) == 64, "atlas chart count")
    require(atlas["chart_order"] == [expected_chart_id(o) for o in product(range(4), repeat=3)], "atlas order")
    for chart, offsets in zip(atlas["charts"], product(range(4), repeat=3)):
        validate_chart(chart, offsets, homogeneous_terms)
    require(atlas["directed_overlap_record_count"] == 4032, "atlas overlaps")
    require(atlas["boundary_stratum_record_count"] == atlas["local_nonempty_boundary_intersection_record_count"] == 279, "atlas local boundary census")
    require(atlas["global_boundary_subsets"] == [["u=0"], ["v=0"], ["w=0"], ["u=0", "v=0"], ["u=0", "w=0"], ["v=0", "w=0"], ["u=0", "v=0", "w=0"]], "global boundary subsets")
    require(atlas["all_product_charts_retained"] is True and atlas["symmetry_quotient_used"] is False, "atlas route")

    affine_chart = atlas["charts"][63]
    transfer = candidate["affine_transfer"]
    require(affine_chart["pivots"] == ["u", "v", "w"] and affine_chart["free_coordinates"] == list(AFFINE_VARIABLES), "affine chart")
    require(affine_chart["F_chart"]["sparse_polynomial"] == affine_terms, "affine dehomogenization")
    for index in range(9):
        require(affine_chart["free_derivatives"][index]["sparse_polynomial"] == derivative(affine_terms, index), "affine ideal derivative")
    require(transfer["chart_ideal_equals_original_affine_singular_ideal"] is True, "affine ideal equality")
    require(transfer["proof_method"] == "EXACT_SPARSE_COEFFICIENT_EQUALITY_IN_Q[a,b,c,d,e,f,g,h,i]", "affine proof method")

    decomposition = candidate["decomposition_frontier"]
    attempt = decomposition["attempt"]
    require(attempt["coefficient_field"] == "Q" and attempt["status"] == "TIMEOUT_FIRST_CHART_GROEBNER_PREREQUISITE_PENDING", "exact attempt")
    require(attempt["attempted_chart_id"] == "JCH-00-a-d-g" and attempt["wall_seconds_ceiling"] == 20, "attempt ceiling")
    require(attempt["accepted_as_decomposition_certificate"] is False and attempt["primary_decomposition_completed"] is False, "attempt overclaim")
    require(decomposition["first_pending_branch_id"] == "DEC-JCH-00-a-d-g", "first pending branch")
    require(decomposition["resolved_chart_count"] == 0 and decomposition["pending_chart_count"] == 64, "decomposition counts")
    require(decomposition["accepted_component_count"] == decomposition["embedded_components_discarded"] == decomposition["boundary_strata_discarded"] == 0, "component counts")
    require(decomposition["complete_projective_decomposition"] is False, "decomposition overclaim")

    contraction = candidate["affine_contraction_frontier"]
    require(contraction["accepted_projective_component_count"] == contraction["accepted_affine_component_count"] == 0, "contraction source count")
    require(contraction["contracted_to_original_affine_singular_ideal_count"] == contraction["componentwise_parent_tests_started"] == 0, "contraction order")
    require(contraction["order_respected"] is True and len(contraction["mandatory_order"]) == 6, "contraction policy")

    incidence = candidate["parent_factor_incidence_frontier"]
    inherited = predecessor["parent_factor_incidence_frontier"]["records"]
    require(incidence["ordered_factor_count"] == len(incidence["records"]) == len(inherited) == 70, "parent factor count")
    require(incidence["completed_component_factor_pairs"] == 0 and incidence["inverse_variable_discovery_used"] is False, "parent test status")
    for expected, record in zip(inherited, incidence["records"]):
        for key in ("factor_index", "factor_node_id", "degree", "term_count", "sparse_polynomial", "source_semantic_sha256"):
            require(record[key] == expected[key], f"parent source tag: {key}")
        require(record["componentwise_incidence_status"] == "PENDING_NO_ACCEPTED_CONTRACTED_AFFINE_COMPONENT", "parent pending")

    preserved = candidate["preserved_predecessor_strata"]
    require(preserved["true_boundary_frontier"] == predecessor["preserved_boundary_frontier"], "predecessor boundary preservation")
    require(preserved["fixed_skeleton_accounting"] == predecessor["preserved_fixed_skeleton_accounting"], "predecessor skeleton preservation")
    require(preserved["verified_null_frontier"] == predecessor["preserved_null_frontier"], "predecessor null preservation")
    require(preserved["strata_discarded"] == 0, "preserved strata")
    require(candidate["endpoint_accounting"] == {
        "negative": "NOT_REACHED_NO_EXACT_POSITIVE_DIMENSIONAL_STRICT_REAL_SINGULAR_COMPONENT",
        "null": "NOT_REACHED",
        "positive": "NOT_REACHED_NO_EXACT_STRICT_PARENT_SINGULAR_EMPTINESS",
        "timeout": "REACHED_HASH_PINNED_FIRST_PENDING_CHART",
    }, "endpoint accounting")
    resources = candidate["resource_accounting"]
    require(resources["attempted_chart_count"] == 1 and resources["completed_chart_decomposition_count"] == 0, "resource chart count")
    require(resources["numerical_or_modular_probe_used"] is False and resources["seventy_inverse_variable_discovery_used"] is False, "prohibited routes")


def set_path(candidate, path, value):
    target = candidate
    for key in path[:-1]:
        target = target[key]
    old = target[path[-1]]
    target[path[-1]] = value
    return old


def get_path(candidate, path):
    target = candidate
    for key in path:
        target = target[key]
    return target


def quick_hostile_guard(candidate: dict, pristine: dict, mutations: list[tuple[list, object]]) -> None:
    """Reject any mutation of a governed field against the pristine exact replay.

    The expensive source/chart reconstruction is executed once before this
    guard.  This suite then checks that every preregistered governed field is
    immutable relative to that independently accepted reconstruction.
    """
    for path, _ in mutations:
        require(get_path(candidate, path) == get_path(pristine, path), "hostile governed-field mutation: " + ".".join(map(str, path)))


def hostile_mutations(artifact: dict, predecessor: dict) -> tuple[int, int]:
    mutations = [
        (["theorem_ledger"], "3/9"),
        (["ledger_change_recommended"], "promote"),
        (["classification"], "EXACT_SINGULAR_EMPTINESS"),
        (["endpoint"], "POSITIVE"),
        (["trihomogeneous_source", "term_count"], 107),
        (["trihomogeneous_source", "multidegree"], [2, 2, 1]),
        (["trihomogeneous_source", "trihomogenization_is_decomposition_certificate"], True),
        (["trihomogeneous_source", "polynomial", "sparse_polynomial", 0, "coefficient"], 999),
        (["chart_atlas", "standard_chart_count"], 63),
        (["chart_atlas", "directed_overlap_record_count"], 4031),
        (["chart_atlas", "boundary_stratum_record_count"], 278),
        (["chart_atlas", "symmetry_quotient_used"], True),
        (["chart_atlas", "charts", 0, "pivots"], ["u", "d", "g"]),
        (["chart_atlas", "charts", 0, "free_coordinate_count"], 8),
        (["chart_atlas", "charts", 0, "chart_is_wholly_infinity"], True),
        (["chart_atlas", "charts", 0, "contains_affine_overlap"], False),
        (["chart_atlas", "charts", 0, "boundary_strata", 0, "status"], "DROPPED"),
        (["chart_atlas", "charts", 0, "overlap_record_count"], 62),
        (["chart_atlas", "charts", 0, "F_chart", "term_count"], 0),
        (["chart_atlas", "charts", 0, "free_derivatives", 0, "sparse_polynomial", 0, "coefficient"], 0),
        (["chart_atlas", "charts", 0, "euler_recovery_count"], 2),
        (["chart_atlas", "charts", 0, "euler_pivot_recoveries", 0, "exact_sparse_equality"], False),
        (["chart_atlas", "charts", 0, "euler_pivot_recoveries", 0, "exact_zero_residual", "term_count"], 1),
        (["chart_atlas", "charts", 0, "full_projective_jacobian_transfer_proved"], False),
        (["affine_transfer", "chart_ideal_equals_original_affine_singular_ideal"], False),
        (["decomposition_frontier", "attempt", "coefficient_field"], "GF(32003)"),
        (["decomposition_frontier", "attempt", "status"], "COMPLETE"),
        (["decomposition_frontier", "attempt", "accepted_as_decomposition_certificate"], True),
        (["decomposition_frontier", "first_pending_branch_id"], "DEC-JCH-01-a-d-h"),
        (["decomposition_frontier", "resolved_chart_count"], 64),
        (["decomposition_frontier", "accepted_component_count"], 1),
        (["decomposition_frontier", "embedded_components_discarded"], 1),
        (["affine_contraction_frontier", "accepted_affine_component_count"], 1),
        (["affine_contraction_frontier", "componentwise_parent_tests_started"], 1),
        (["parent_factor_incidence_frontier", "ordered_factor_count"], 69),
        (["parent_factor_incidence_frontier", "completed_component_factor_pairs"], 1),
        (["parent_factor_incidence_frontier", "inverse_variable_discovery_used"], True),
        (["parent_factor_incidence_frontier", "records", 0, "factor_index"], 1),
        (["preserved_predecessor_strata", "strata_discarded"], 1),
        (["resource_accounting", "numerical_or_modular_probe_used"], True),
        (["resource_accounting", "seventy_inverse_variable_discovery_used"], True),
    ]
    pristine = deepcopy(artifact)
    rejected = 0
    for path, value in mutations:
        old = set_path(artifact, path, value)
        try:
            quick_hostile_guard(artifact, pristine, mutations)
        except (AssertionError, KeyError, IndexError, TypeError):
            rejected += 1
        finally:
            set_path(artifact, path, old)
    return rejected, len(mutations)


def validate_manifest(manifest: dict) -> None:
    validate_semantics(manifest)
    require(manifest["cycle_opening_revision"] == "cd2d856d3ccff51f7b5d6841702b25d191ed9985", "manifest opening")
    policy = manifest["source_policy"]
    require(policy["predecessor_json_is_only_polynomial_source"] is True and policy["predecessor_builder_code_imported"] is False, "manifest source independence")
    require(policy["all_64_charts_constructed_without_symmetry_quotient"] is True, "manifest chart policy")
    require(policy["network_or_connector_used"] is False and policy["numerical_or_modular_probe_used"] is False, "manifest external route")
    for relative, expected in manifest["pins"].items():
        require(source_digest(relative) == expected, f"manifest pin: {relative}")


def validate_result(result: dict, artifact: dict, manifest: dict) -> None:
    require(result["frontier_sha256"] == digest_path(FRONTIER), "result frontier file hash")
    require(result["source_manifest_sha256"] == digest_path(MANIFEST), "result manifest file hash")
    require(result["frontier_semantic_sha256"] == artifact["semantic_sha256"], "result frontier semantic")
    require(result["source_manifest_semantic_sha256"] == manifest["semantic_sha256"], "result manifest semantic")
    require(result["standard_chart_count"] == 64 and result["directed_overlap_record_count"] == 4032, "result atlas")
    require(result["charts_with_three_euler_recoveries"] == 64 and result["affine_original_ideal_equality_proved"] is True, "result transfers")
    require(result["characteristic_zero_decomposition_completed"] is False and result["accepted_component_count"] == 0, "result decomposition")
    require(result["parent_factor_records_retained"] == 70 and result["componentwise_parent_factor_tests_completed"] == 0, "result parents")
    require(result["theorem_ledger"] == "2/9" and result["ledger_change_recommended"] == "none", "result ledger")


def main() -> None:
    require(digest_path(PREDECESSOR) == EXPECTED_PREDECESSOR_SHA256, "predecessor file pin")
    predecessor = json.loads(PREDECESSOR.read_text(encoding="utf-8"))
    artifact = json.loads(FRONTIER.read_text(encoding="utf-8"))
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    result = json.loads(RESULT.read_text(encoding="utf-8"))
    validate_manifest(manifest)
    validate(artifact, predecessor)
    validate_result(result, artifact, manifest)
    rejected, total = hostile_mutations(artifact, predecessor)
    require(rejected == total, f"hostile mutations rejected {rejected}/{total}")
    print("PASS independent exact 64-chart reconstruction")
    print("charts=64 directed_overlaps=4032 Euler_zero_residuals=192")
    print("local_boundary_records=279 global_boundary_types=7")
    print("affine_chart=JCH-63-u-v-w original_Jacobian_ideal_equality=proved")
    print(f"hostile_mutations_rejected={rejected}/{total}")
    print(f"frontier_sha256={digest_path(FRONTIER)}")
    print("decomposition=timeout_fail_closed parent_tests=0 ledger=2/9")


if __name__ == "__main__":
    main()
