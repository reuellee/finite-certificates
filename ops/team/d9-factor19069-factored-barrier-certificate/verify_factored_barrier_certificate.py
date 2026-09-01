#!/usr/bin/env python3
"""Independent exact certificate for the factor-19069 barrier null envelope.

Constructor and falsifier files are frozen data only.  Acceptance is rebuilt
from the canonical row-2599 sources; neither producer module is imported.
"""

from __future__ import annotations

import ast
from collections import Counter
from copy import deepcopy
from fractions import Fraction
from hashlib import sha256
from itertools import combinations
import json
from pathlib import Path
import subprocess
import sys

import numpy as np


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
OMREAL = ROOT / "ai" / "omreal"
DATA = OMREAL / "data"
FRONTIER_PATH = "ops/team/d9-factor19069-factored-barrier-constructor/FACTORED_BARRIER_FRONTIER.json"
CONSTRUCTOR_RESULT_PATH = "ops/team/d9-factor19069-factored-barrier-constructor/RESULT.json"
CONSTRUCTOR_MANIFEST_PATH = "ops/team/d9-factor19069-factored-barrier-constructor/SOURCE_MANIFEST.json"
FALSIFIER_RESULT_PATH = "ops/team/d9-factor19069-factored-barrier-falsifier/RESULT.json"
FALSIFIER_MANIFEST_PATH = "ops/team/d9-factor19069-factored-barrier-falsifier/SOURCE_MANIFEST.json"
FALSIFIER_VERIFY_PATH = "ops/team/d9-factor19069-factored-barrier-falsifier/verify_factored_barrier_falsifier.py"
RESULT_PATH = HERE / "RESULT.json"
REVIEWED = "27f934f5030c2912fbe760656dd38a201ee2e31c"
REVIEWED_TREE = "b147b9658ed51b6c4c2730e628b38aec97178dd7"
OPENING = "d12dbaf7cfb7312d9d603c8938dd8ad6ce62166e"
OPENING_TREE = "221e574fd705aff50f667ebc72345a36afc4f5d7"
BASE = "b71c139a3c64cde3442252f8f3d46f2d893978c5"
BASE_TREE = "7a9da9f02369831bd34bc22f39a0bbad57725522"
TARGET_FACTOR = 19069
FULL_SUPPORT = (15, 15, 15)
GROUPS = ((0, 1, 2), (3, 4, 5), (6, 7, 8))
VARIABLES = tuple("abcdefghi")
PINS = {
    FRONTIER_PATH: "3f75eeb2f7433234206292012c527604517b516ee904e2ab1d1969e49ed1e8ca",
    CONSTRUCTOR_RESULT_PATH: "5d9357346077562824c4564829260d49b6fa62ceea38b7ae3f7fe5543dee029a",
    CONSTRUCTOR_MANIFEST_PATH: "17bc476bfc78d629353f4fe73d24495de40de5a926aa5e8df4ed524131b3d303",
    FALSIFIER_RESULT_PATH: "9af35e89fafd73e71d940750d1f49ae166cc3e634a3f8ea2e02d3371f0ddf022",
    FALSIFIER_MANIFEST_PATH: "5b8787839c2ac4d44850f05ab1e4fd3a47d80d47511a21020c13680872ca6172",
    FALSIFIER_VERIFY_PATH: "8dc7adc67aef34651ac3ce3e97f4abaa3030fbc7732fd0e3922d95af64425965",
}

sys.path.insert(0, str(OMREAL))

import DIAG2_PIVOT_LABELED_PAIR_ORBITS_VERIFY as labeled  # noqa: E402
import DIAG9_GRAPH_verify_row2599_slice as sturm  # noqa: E402
import verify_diag3_pair_global_face_bernstein_atlas as bernstein  # noqa: E402
import verify_diag3_pair_global_parent_face_gate as gate  # noqa: E402


class Reject(AssertionError):
    pass


def require(condition: bool, message: str) -> None:
    if not condition:
        raise Reject(message)


def git(*arguments: str, binary: bool = False):
    result = subprocess.check_output(["git", *arguments], cwd=ROOT, text=not binary)
    return result if binary else result.strip()


def frozen(path: str) -> bytes:
    return git("show", f"{REVIEWED}:{path}", binary=True)


def digest(value: bytes) -> str:
    return sha256(value).hexdigest()


def canonical_digest(value) -> str:
    return sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode("ascii")).hexdigest()


def semantic_digest(candidate: dict) -> str:
    unsealed = deepcopy(candidate)
    unsealed.pop("semantic_sha256", None)
    return canonical_digest(unsealed)


def sparse(polynomial: dict) -> list[dict]:
    return [
        {"exponents": list(monomial), "coefficient": int(coefficient)}
        for monomial, coefficient in sorted(polynomial.items())
        if coefficient
    ]


def derivative(polynomial: dict, coordinate: int) -> dict:
    answer = {}
    for monomial, coefficient in polynomial.items():
        power = monomial[coordinate]
        if power:
            reduced = list(monomial)
            reduced[coordinate] -= 1
            reduced = tuple(reduced)
            answer[reduced] = answer.get(reduced, 0) + coefficient * power
    return {monomial: coefficient for monomial, coefficient in answer.items() if coefficient}


def polynomial_degree(polynomial: dict) -> int:
    return max(map(sum, polynomial))


def multidegree(polynomial: dict) -> tuple[int, int, int]:
    return tuple(max(sum(monomial[index] for index in group) for monomial in polynomial) for group in GROUPS)


def fraction_text(value: Fraction) -> str:
    return str(value.numerator) if value.denominator == 1 else f"{value.numerator}/{value.denominator}"


def literal_assignment(path: Path, name: str):
    syntax = ast.parse(path.read_text(encoding="utf-8"))
    for node in syntax.body:
        if isinstance(node, ast.Assign) and any(
            isinstance(target, ast.Name) and target.id == name for target in node.targets
        ):
            return ast.literal_eval(node.value)
    raise Reject(f"missing literal assignment {name}")


def multiply_linear(polynomial, constant: Fraction, slope: Fraction):
    answer = [Fraction(0)] * (len(polynomial) + 1)
    for index, coefficient in enumerate(polynomial):
        answer[index] += coefficient * constant
        answer[index + 1] += coefficient * slope
    return answer


def segment_polynomial(polynomial: dict, left, right):
    answer = [Fraction(0)] * (polynomial_degree(polynomial) + 1)
    differences = tuple(r - l for l, r in zip(left, right, strict=True))
    for monomial, coefficient in polynomial.items():
        term = [Fraction(coefficient)]
        for coordinate, exponent in enumerate(monomial):
            for _ in range(exponent):
                term = multiply_linear(term, left[coordinate], differences[coordinate])
        for index, value in enumerate(term):
            answer[index] += value
    while len(answer) > 1 and answer[-1] == 0:
        answer.pop()
    return tuple(answer)


def positive_closed_segment(polynomial) -> None:
    polynomial = tuple(map(Fraction, polynomial))
    require(sturm.polynomial_value(polynomial, Fraction(0)) > 0, "source skeleton parent path")
    require(sturm.polynomial_value(polynomial, Fraction(1)) > 0, "source skeleton parent path")
    require(sturm.root_count(polynomial, Fraction(0), Fraction(1)) == 0, "source skeleton parent path")


def divide_one_minus_t(polynomial) -> tuple[Fraction, ...]:
    polynomial = tuple(map(Fraction, polynomial))
    require(len(polynomial) >= 2, "constant path polynomial")
    quotient = [polynomial[0]]
    for index in range(1, len(polynomial) - 1):
        quotient.append(polynomial[index] + quotient[-1])
    require(polynomial[-1] == -quotient[-1], "nonexact endpoint division")
    while len(quotient) > 1 and quotient[-1] == 0:
        quotient.pop()
    return tuple(quotient)


def strict_path_certificate(polynomial) -> dict:
    polynomial = tuple(map(Fraction, polynomial))
    require(sturm.polynomial_value(polynomial, Fraction(0)) > 0, "path start sign")
    multiplicity = 0
    reduced = polynomial
    while sturm.polynomial_value(reduced, Fraction(1)) == 0:
        reduced = divide_one_minus_t(reduced)
        multiplicity += 1
    require(sturm.polynomial_value(reduced, Fraction(0)) > 0, "reduced start sign")
    require(sturm.polynomial_value(reduced, Fraction(1)) > 0, "reduced endpoint sign")
    roots = sturm.root_count(reduced, Fraction(0), Fraction(1))
    require(roots == 0, "parent factor changes sign on boundary path")
    return {"endpoint_zero_multiplicity": multiplicity, "reduced_open_root_count": roots}


def factor_restriction_state(polynomial: dict, degrees, face) -> str:
    signs = {
        1 if coefficient > 0 else -1
        for monomial, coefficient in polynomial.items()
        if all(
            support & ~allowed == 0
            for support, allowed in zip(bernstein.term_support(monomial, degrees), face, strict=True)
        )
    }
    if not signs:
        return "IDENTICALLY_ZERO"
    if signs == {-1, 1}:
        return "BERNSTEIN_MIXED_UNRESOLVED"
    if signs == {1}:
        return "BERNSTEIN_POSITIVE"
    if signs == {-1}:
        return "BERNSTEIN_NEGATIVE"
    raise Reject("factor restriction state")


def primitive_univariate(coefficients) -> tuple[int, ...]:
    from math import gcd, lcm

    coefficients = list(map(Fraction, coefficients))
    while len(coefficients) > 1 and coefficients[-1] == 0:
        coefficients.pop()
    denominator = 1
    for coefficient in coefficients:
        denominator = lcm(denominator, coefficient.denominator)
    integers = [int(coefficient * denominator) for coefficient in coefficients]
    divisor = 0
    for coefficient in integers:
        divisor = gcd(divisor, abs(coefficient))
    integers = [coefficient // max(divisor, 1) for coefficient in integers]
    if integers and integers[-1] < 0:
        integers = [-coefficient for coefficient in integers]
    return tuple(integers)


def replay_sources() -> dict:
    records = [json.loads(line) for line in gate.CATALOG.read_text(encoding="utf-8").splitlines() if line]
    parents, parent_sign_digest = gate.parent_polynomials(records[2599])
    signed_parents = [
        (label, target, {monomial: target * coefficient for monomial, coefficient in polynomial.items()})
        for label, target, polynomial, _terms in parents
    ]
    require(len(signed_parents) == 70 and len({label for label, _target, _poly in signed_parents}) == 70, "source parent factors")
    _occurrences, _occurrence_factor, factors = labeled.factor_polynomials()
    factor = factors[TARGET_FACTOR]
    require(polynomial_degree(factor) == 6 and multidegree(factor) == (2, 2, 2) and len(factor) == 108, "source wall polynomial")

    parent_face = json.loads((DATA / "DIAG3_PAIR_GLOBAL_row2599_parent_face_gate.json").read_text(encoding="utf-8"))
    proper = [record for record in parent_face["nonexcluded_support_faces"] if tuple(record["support"]) != FULL_SUPPORT]
    require(len(proper) == 10, "source boundary candidates")
    pinned = gate.normalized_values(records[2599]["matrix"])
    path_records = []
    for record in proper:
        witness = tuple(map(Fraction, record["witness"]))
        proofs = []
        first = None
        for label, _target, polynomial in signed_parents:
            restricted = segment_polynomial(polynomial, pinned, witness)
            try:
                proofs.append({"label": label, **strict_path_certificate(restricted)})
            except Reject as error:
                first = {
                    "label": label,
                    "reason": str(error),
                    "restricted_signed_parent_polynomial_coefficients_ascending": list(map(fraction_text, restricted)),
                    "tested_parent_factors_before_rejection": len(proofs),
                }
                break
        path_records.append({
            "support": record["support"],
            "dimension": record["dimension"],
            "classification": record["classification"].upper(),
            "witness": list(map(fraction_text, witness)),
            "zero_parent_factors": record["witness_zero_parent_brackets"],
            "factor_state": factor_restriction_state(factor, (2, 2, 2), tuple(record["support"])),
            "proof_count": len(proofs),
            "proof_digest": canonical_digest(proofs),
            "first_rejection": first,
        })

    edges = tuple(literal_assignment(OMREAL / "verify_diag3_pair_fullsupport_safe_segment_walls.py", "EDGES"))
    with np.load(gate.POINT_BANK, allow_pickle=False) as source:
        matrices = np.asarray(source["chart_matrix"], dtype=np.int64)
    require(matrices.shape == (178, 4, 8), "source point-bank shape")
    points = tuple(gate.normalized_values(matrix.tolist()) for matrix in matrices)
    cover = json.loads((DATA / "DIAG3_PAIR_FULLSUPPORT_SEGMENT_COVER.json").read_text(encoding="utf-8"))
    selected = tuple(cover["source_bank"]["selected_edge_indices"])
    require(len(selected) == 40, "source skeleton edges")
    roots = {}
    parent_checks = 0
    for edge_index in selected:
        left, right = edges[edge_index]
        for _label, _target, polynomial in signed_parents:
            positive_closed_segment(segment_polynomial(polynomial, points[left], points[right]))
            parent_checks += 1
        restricted = segment_polynomial(factor, points[left], points[right])
        require(sturm.polynomial_value(restricted, Fraction(0)) != 0, "source edge endpoint")
        require(sturm.polynomial_value(restricted, Fraction(1)) != 0, "source edge endpoint")
        roots[str(edge_index)] = sturm.root_count(restricted, Fraction(0), Fraction(1))
    require(parent_checks == 2800, "source skeleton checks")
    require([int(edge) for edge, count in roots.items() if count] == [39] and roots["39"] == 1, "source rooted edge")
    return {
        "parents": signed_parents,
        "parent_sign_digest": parent_sign_digest,
        "factor": factor,
        "path_records": path_records,
        "parent_face": parent_face,
        "points": points,
        "roots": roots,
        "selected": selected,
        "edges": edges,
    }


def validate_frontier(candidate: dict, replay: dict) -> None:
    require(candidate["semantic_sha256"] == semantic_digest(candidate), "frontier semantic digest")
    require(candidate["format"] == "d9-factor19069-factored-barrier-frontier-v1", "frontier format")
    require(candidate["classification"] == "EXACT_FAIL_CLOSED_FACTORED_BARRIER_COMPONENT_NULL", "classification")
    require(candidate["endpoint"] == "HASH_PINNED_FACTORED_BARRIER_CRITICAL_COMPONENT_FRONTIER_WITH_FIRST_UNSAMPLED_COMPONENT", "endpoint")
    require(candidate["theorem_ledger"] == "2/9" and candidate["ledger_change_recommended"] == "none", "ledger")
    require(candidate["producer_independent_certificate_present"] is False, "premature certificate")
    target = candidate["target"]
    require(target["factor_id"] == TARGET_FACTOR and target["parent_sign_factors"] == 70, "target factor inventory")
    require(target["parent_sign_digest"] == replay["parent_sign_digest"], "parent sign digest")

    circuit = candidate["factor_circuit"]
    nodes = circuit["parent_factor_nodes"]
    require(len(nodes) == 70, "parent factor nodes")
    expected_ids = []
    total_degree = 0
    term_count = 0
    for index, (node, (label, target_sign, polynomial)) in enumerate(zip(nodes, replay["parents"], strict=True)):
        node_id = f"H_{index:02d}_{label}"
        expected_ids.append(node_id)
        require(node["node_id"] == node_id and node["label"] == label, "parent factor order")
        require(node["source_target_sign"] == target_sign, "parent factor sign")
        require(node["sparse_polynomial"] == sparse(polynomial), "parent factor polynomial")
        require(node["degree"] == polynomial_degree(polynomial) and node["term_count"] == len(polynomial), "parent factor census")
        total_degree += polynomial_degree(polynomial)
        term_count += len(polynomial)
    require(total_degree == 90 and term_count == 209, "barrier census")
    barrier = circuit["barrier"]
    require(barrier["ordered_factor_node_ids"] == expected_ids and barrier["factor_count"] == 70, "barrier factor order")
    require(barrier["expanded_polynomial_present"] is False, "expanded barrier")
    require(barrier["total_degree"] == 90, "barrier degree")

    derivatives = circuit["barrier_derivative_nodes"]
    require(len(derivatives) == 9, "barrier derivative coordinates")
    for coordinate, node in enumerate(derivatives):
        require(node["coordinate_index"] == coordinate and node["node_id"] == f"dB_d{VARIABLES[coordinate]}", "barrier derivative order")
        require(len(node["summands"]) == 70, "barrier derivative summands")
        for index, summand in enumerate(node["summands"]):
            require(summand["differentiated_factor_index"] == index and summand["multiply_all_factor_indices_except"] == index, "barrier derivative provenance")
            require(summand["derivative_sparse_polynomial"] == sparse(derivative(replay["parents"][index][2], coordinate)), "barrier derivative polynomial")
    require(sum(len(node["summands"]) for node in derivatives) == 630, "barrier derivative total")
    wall = circuit["wall_polynomial"]
    require(wall["sparse_polynomial"] == sparse(replay["factor"]), "wall polynomial")
    require(wall["degree"] == 6 and wall["multidegree"] == [2, 2, 2], "wall census")
    wall_derivatives = circuit["wall_derivative_nodes"]
    require(len(wall_derivatives) == 9, "wall derivative coordinates")
    for coordinate, node in enumerate(wall_derivatives):
        require(node["node_id"] == f"df_d{VARIABLES[coordinate]}", "wall derivative order")
        require(node["sparse_polynomial"] == sparse(derivative(replay["factor"], coordinate)), "wall derivative polynomial")
    wedge = circuit["wedge_equation_nodes"]
    require(len(wedge) == 36, "wedge equation count")
    for node, (left, right) in zip(wedge, combinations(range(9), 2), strict=True):
        require(node["coordinate_pair"] == [left, right], "wedge coordinate pair")
        require(node["inputs"] == [f"dB_d{VARIABLES[left]}", f"df_d{VARIABLES[right]}", f"dB_d{VARIABLES[right]}", f"df_d{VARIABLES[left]}"], "wedge inputs")
    require(candidate["factor_circuit_semantic_sha256"] == canonical_digest(circuit), "factor circuit digest")

    critical = candidate["strict_interior_critical_frontier"]
    require(critical["systems_constructed"] == 1 and len(critical["systems"]) == 1, "critical system count")
    system = critical["systems"][0]
    require(system["support"] == [15, 15, 15], "critical support")
    require(system["strict_inequalities"] == [f"{node}>0" for node in expected_ids], "critical parent inequalities")
    require(system["possible_component_dimensions"] == list(range(9)), "critical dimensions")
    require(system["singular_wall_pieces_included"] is True, "singular pieces")
    require(system["positive_dimensional_pieces_required"] is True, "positive dimensional pieces")
    require(system["connected_parent_selector"].startswith("EXACT_PATH"), "connected parent selector")
    require(system["component_decomposition_status"] == "UNSAMPLED_FAIL_CLOSED", "component decomposition")
    require(system["semantic_sha256"] == canonical_digest({key: value for key, value in system.items() if key != "semantic_sha256"}), "critical stratum digest")
    require(critical["connected_components_sampled"] == 0, "connected component samples")
    require(critical["zero_dimensional_components_sampled"] == 0, "zero dimensional samples")
    require(critical["positive_dimensional_components_sampled"] == 0, "positive dimensional samples")
    require(critical["first_unsampled_component_or_stratum"]["stratum_id"] == system["stratum_id"], "first unsampled stratum")

    boundary = candidate["true_boundary_frontier"]
    require(boundary["ambient_product_support_strata"] == 3375, "boundary total")
    require(boundary["parent_bernstein_excluded_support_strata"] == 3364, "boundary excluded")
    require(boundary["proper_nonexcluded_candidate_strata"] == 10, "boundary candidates")
    records = boundary["records"]
    require(len(records) == 10, "boundary records")
    for stored, source in zip(records, replay["path_records"], strict=True):
        require(stored["support"] == source["support"] and stored["dimension"] == source["dimension"], "boundary record support")
        require(stored["parent_support_gate_classification"] == source["classification"], "boundary classification")
        require(stored["factor19069_restriction"] == source["factor_state"], "boundary factor restriction")
        require(stored["witness"] == source["witness"] and stored["witness_zero_parent_factors"] == source["zero_parent_factors"], "boundary witness")
        path = stored["parent_component_closure_path"]
        require(path["parent_factor_proof_count"] == source["proof_count"], "boundary path proof count")
        require(path["parent_factor_proof_semantic_sha256"] == source["proof_digest"], "boundary path digest")
        require(path["first_rejection"] == source["first_rejection"], "boundary path rejection")
        expected_status = "CERTIFIED_LINEAR_PATH_FROM_PINNED_SAMPLE_IN_P_FOR_0_LE_T_LT_1" if source["first_rejection"] is None else "TESTED_LINEAR_PATH_REJECTED_NO_ALTERNATIVE_EXACT_PATH_CERTIFIED"
        require(path["status"] == expected_status, "boundary path status")
        require(stored["wall_component_residence"] == "UNCLASSIFIED_FAIL_CLOSED", "boundary wall residence")
    require(Counter(record["factor19069_restriction"] for record in records) == {"IDENTICALLY_ZERO": 8, "BERNSTEIN_MIXED_UNRESOLVED": 2}, "boundary factor census")
    certified = [record for record in records if record["parent_component_closure_path"]["status"].startswith("CERTIFIED")]
    require(len(certified) == 1 and certified[0]["support"] == [15, 7, 15], "certified boundary path")
    require(records[0]["support"] == [1, 1, 1] and records[0]["parent_component_closure_path"]["first_rejection"]["label"] == "2578", "first boundary obstruction")
    require(boundary["wall_component_residence_classified_strata"] == 0, "boundary residence count")
    require(boundary["true_parent_boundary_kept_distinct_from"] == ["SOLVER_BOUNDARY", "BOX_BOUNDARY", "COLLAR_BOUNDARY", "SKELETON_EDGE_ENDPOINT"], "artificial boundaries")

    skeleton = candidate["fixed_skeleton_accounting"]
    require(skeleton["parent_path_tag_checks"] == 2800 and skeleton["all_40_edges_retain_all_70_parent_tags"] is True, "skeleton parent tags")
    require(skeleton["factor19069_open_root_counts_by_edge"] == replay["roots"], "skeleton root census")
    require([int(edge) for edge, count in replay["roots"].items() if count] == [39], "rooted edge")
    anchor = skeleton["exact_attached_wall_anchor"]
    require(anchor["edge_index"] == 39 and anchor["attachment"].startswith("LIES_ON_FIXED_SKELETON"), "edge39 anchor")
    require(anchor["barrier_critical_sample"] is False, "edge39 globalization")
    left, right = replay["edges"][39]
    restricted = primitive_univariate(segment_polynomial(replay["factor"], replay["points"][left], replay["points"][right]))
    require(anchor["parameter_minimal_polynomial_coefficients_ascending"] == list(restricted), "edge39 polynomial")
    interval = tuple(map(Fraction, anchor["parameter_isolating_interval"]))
    require(sturm.root_count(tuple(map(Fraction, restricted)), *interval) == 1, "edge39 isolating interval")
    require(skeleton["global_wall_component_count"] is None and skeleton["global_attached_component_count"] is None and skeleton["global_unattached_component_count"] is None, "global component counts")
    require(skeleton["attachment_classification_complete"] is False, "attachment completeness")


def validate_handoffs(frontier: dict) -> None:
    constructor = json.loads(frozen(CONSTRUCTOR_RESULT_PATH).decode("utf-8"))
    falsifier = json.loads(frozen(FALSIFIER_RESULT_PATH).decode("utf-8"))
    require(constructor["classification"] == frontier["classification"], "constructor classification")
    require(constructor["frontier_sha256"] == PINS[FRONTIER_PATH], "constructor frontier pin")
    require(constructor["producer_independent_certificate_present"] is False, "constructor premature certificate")
    require(falsifier["classification"] == "EXACT_SCOPE_REJECTION_CONFIRMS_FACTORED_BARRIER_NULL", "falsifier classification")
    require(falsifier["retained_endpoint"] == frontier["endpoint"], "falsifier endpoint")
    require(falsifier["constructor_certified"] is False and falsifier["cycle_certificate_issued"] is False, "falsifier scope")
    require(falsifier["hostile_mutations"] == {"rejected": 25, "total": 25}, "falsifier hostile mutations")


def validate_result(candidate: dict) -> None:
    require(candidate["format"] == "d9-factor19069-factored-barrier-certificate-result-v1", "certificate format")
    require(candidate["reviewed_revision"] == REVIEWED and candidate["reviewed_tree"] == REVIEWED_TREE, "certificate frozen head")
    require(candidate["verdict"] == "ACCEPT" and candidate["classification"] == "ACCEPT_EXACT_FACTORED_BARRIER_NULL_ENVELOPE", "certificate verdict")
    require(candidate["accepted_endpoint"] == "HASH_PINNED_FACTORED_BARRIER_CRITICAL_COMPONENT_FRONTIER_WITH_FIRST_UNSAMPLED_COMPONENT", "certificate endpoint")
    require(candidate["producer_imported"] is False and candidate["falsifier_imported"] is False, "certificate independence")
    require(candidate["component_samples_certified"] == 0 and candidate["attachment_completeness_certified"] is False, "certificate scope")
    require(candidate["hostile_mutations"] == {"rejected": 22, "total": 22}, "certificate hostile mutations")
    require(candidate["theorem_ledger"] == "2/9" and candidate["ledger_change_recommended"] == "none", "certificate ledger")
    require(candidate["frozen_pins"] == PINS, "certificate pins")


def reseal(candidate: dict) -> dict:
    candidate["semantic_sha256"] = semantic_digest(candidate)
    return candidate


def hostile_mutations(stored: dict, replay: dict) -> list[str]:
    mutations = []
    def add(marker: str, candidate: dict) -> None:
        mutations.append((marker, reseal(candidate)))
    candidate = deepcopy(stored); candidate["classification"] = "COMPLETE"; add("classification", candidate)
    candidate = deepcopy(stored); candidate["endpoint"] = "COMPLETE"; add("endpoint", candidate)
    candidate = deepcopy(stored); candidate["target"]["parent_sign_factors"] = 69; add("target factor inventory", candidate)
    candidate = deepcopy(stored); candidate["factor_circuit"]["parent_factor_nodes"].pop(); add("parent factor nodes", candidate)
    candidate = deepcopy(stored); candidate["factor_circuit"]["barrier"]["expanded_polynomial_present"] = True; add("expanded barrier", candidate)
    candidate = deepcopy(stored); candidate["factor_circuit"]["barrier"]["total_degree"] = 89; add("barrier degree", candidate)
    candidate = deepcopy(stored); candidate["factor_circuit"]["barrier_derivative_nodes"][0]["summands"].pop(); add("barrier derivative summands", candidate)
    candidate = deepcopy(stored); candidate["factor_circuit"]["wedge_equation_nodes"].pop(); add("wedge equation count", candidate)
    candidate = deepcopy(stored); candidate["strict_interior_critical_frontier"]["connected_components_sampled"] = 1; add("connected component samples", candidate)
    candidate = deepcopy(stored); candidate["strict_interior_critical_frontier"]["zero_dimensional_components_sampled"] = 1; add("zero dimensional samples", candidate)
    candidate = deepcopy(stored); candidate["strict_interior_critical_frontier"]["positive_dimensional_components_sampled"] = 1; add("positive dimensional samples", candidate)
    candidate = deepcopy(stored); candidate["strict_interior_critical_frontier"]["systems"][0]["possible_component_dimensions"] = [0]; add("critical dimensions", candidate)
    candidate = deepcopy(stored); candidate["strict_interior_critical_frontier"]["systems"][0]["singular_wall_pieces_included"] = False; add("singular pieces", candidate)
    candidate = deepcopy(stored); candidate["strict_interior_critical_frontier"]["systems"][0]["connected_parent_selector"] = "SIGNS_ONLY"; add("connected parent selector", candidate)
    candidate = deepcopy(stored); candidate["true_boundary_frontier"]["proper_nonexcluded_candidate_strata"] = 9; add("boundary candidates", candidate)
    candidate = deepcopy(stored); candidate["true_boundary_frontier"]["records"].pop(); add("boundary records", candidate)
    candidate = deepcopy(stored); candidate["true_boundary_frontier"]["records"][-1]["parent_component_closure_path"]["status"] = "UNCLASSIFIED"; add("boundary path status", candidate)
    candidate = deepcopy(stored); candidate["true_boundary_frontier"]["records"][0]["parent_component_closure_path"]["first_rejection"]["label"] = "1234"; add("boundary path rejection", candidate)
    candidate = deepcopy(stored); candidate["true_boundary_frontier"]["records"][0]["wall_component_residence"] = "CLASSIFIED"; add("boundary wall residence", candidate)
    candidate = deepcopy(stored); candidate["fixed_skeleton_accounting"]["factor19069_open_root_counts_by_edge"]["39"] = 0; add("skeleton root census", candidate)
    candidate = deepcopy(stored); candidate["fixed_skeleton_accounting"]["attachment_classification_complete"] = True; add("attachment completeness", candidate)
    candidate = deepcopy(stored); candidate["theorem_ledger"] = "3/9"; add("ledger", candidate)
    rejected = []
    for marker, candidate in mutations:
        try:
            validate_frontier(candidate, replay)
        except Reject as error:
            require(marker in str(error), f"wrong hostile rejection {marker}: {error}")
            rejected.append(marker)
            continue
        raise Reject(f"hostile mutation accepted: {marker}")
    return rejected


def independence_audit() -> None:
    syntax = ast.parse(Path(__file__).read_text(encoding="utf-8"))
    imports = []
    for node in ast.walk(syntax):
        if isinstance(node, ast.Import):
            imports.extend(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom):
            imports.append(node.module or "")
    require(not any("factored_barrier" in name or "falsifier" in name for name in imports), "certificate independence import")


def main() -> None:
    require(git("rev-parse", f"{REVIEWED}^{{commit}}") == REVIEWED, "reviewed commit")
    require(git("rev-parse", f"{REVIEWED}^{{tree}}") == REVIEWED_TREE, "reviewed tree")
    require(git("rev-parse", f"{OPENING}^{{tree}}") == OPENING_TREE, "opening tree")
    require(git("rev-parse", f"{BASE}^{{tree}}") == BASE_TREE, "base tree")
    for path, expected in PINS.items():
        data = frozen(path)
        require(digest(data) == expected, f"frozen pin {path}")
        require((ROOT / path).read_bytes() == data, f"worktree drift {path}")
    independence_audit()
    manifest = json.loads(frozen(CONSTRUCTOR_MANIFEST_PATH).decode("utf-8"))
    require(manifest["source_count"] == 20, "source manifest count")
    require(manifest["semantic_sha256"] == canonical_digest({key: value for key, value in manifest.items() if key != "semantic_sha256"}), "source manifest digest")
    for path, expected in manifest["source_sha256"].items():
        require(digest(frozen(path)) == expected, f"source manifest pin {path}")
        require((ROOT / path).read_bytes() == frozen(path), f"source worktree drift {path}")
    frontier = json.loads(frozen(FRONTIER_PATH).decode("utf-8"))
    replay = replay_sources()
    validate_frontier(frontier, replay)
    validate_handoffs(frontier)
    result = json.loads(RESULT_PATH.read_text(encoding="utf-8"))
    validate_result(result)
    rejected = hostile_mutations(frontier, replay)
    print("PASS producer-independent factor-19069 factored-barrier null certificate")
    print("PASS sources=20 parents=70 dB=630 wedge=36 boundary=3375/3364/10 skeleton=2800 edge39=1")
    print(f"PASS hostile_mutations={len(rejected)}/22 rejected; no producer/falsifier imports")
    print("ACCEPT exact null envelope only; component_samples=0 attachment_complete=false ledger=2/9")


if __name__ == "__main__":
    main()
