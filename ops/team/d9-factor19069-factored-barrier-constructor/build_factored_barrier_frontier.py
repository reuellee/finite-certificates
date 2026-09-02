#!/usr/bin/env python3
"""Build the exact factor-19069 factored-barrier frontier.

The artifact constructed here is deliberately fail-closed.  It reconstructs
the seventy signed parent factors and factor 19069 from pinned repository
sources, emits the *circuit* for ``B = product H_I`` and for all coefficients
of ``dB wedge df``, and records the first component-sampling obligation that
has not been discharged.  It never expands B and it does not infer global
component coverage from the already certified edge-39 wall root.
"""

from __future__ import annotations

from collections import Counter
from fractions import Fraction
from hashlib import sha256
import ast
import json
from math import comb
from pathlib import Path
import subprocess
import sys

import numpy as np


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
OMREAL = ROOT / "ai" / "omreal"
DATA = OMREAL / "data"
CYCLE = (
    ROOT
    / "ops"
    / "research-team"
    / "cycles"
    / "2026-09-01-d9-row2599-factor19069-factored-barrier-gate1"
)
OUTPUT = HERE / "FACTORED_BARRIER_FRONTIER.json"
MANIFEST = HERE / "SOURCE_MANIFEST.json"

sys.path.insert(0, str(OMREAL))

import DIAG2_PIVOT_LABELED_PAIR_ORBITS_VERIFY as labeled  # noqa: E402
import DIAG9_GRAPH_verify_row2599_slice as sturm  # noqa: E402
import verify_diag3_pair_global_face_bernstein_atlas as bernstein  # noqa: E402
import verify_diag3_pair_global_parent_face_gate as gate  # noqa: E402


OPENING_REVISION = "d12dbaf7cfb7312d9d603c8938dd8ad6ce62166e"
OPENING_TREE = "221e574fd705aff50f667ebc72345a36afc4f5d7"
BASE_REVISION = "b71c139a3c64cde3442252f8f3d46f2d893978c5"
BASE_TREE = "7a9da9f02369831bd34bc22f39a0bbad57725522"
TARGET_FACTOR = 19069
VARIABLES = tuple("abcdefghi")
FULL_SUPPORT = (15, 15, 15)
MAX_COMPONENT_NODES = 500_000
ISOLATION_WIDTH = Fraction(1, 1 << 22)

SOURCE_PINS = {
    "ops/research-team/cycles/2026-09-01-d9-row2599-factor19069-factored-barrier-gate1/OPENING_AUDIT.json": "fa6338b7a42fa333e32c27916dbea0f1c9f50f0eeb4cbbe016cf04f59782cace",
    "ops/research-team/cycles/2026-09-01-d9-row2599-factor19069-factored-barrier-gate1/CYCLE.md": "32f38adfb370a4c82b33640863ac41674707cec2254cd0a80d0aa2f46829585f",
    "ops/research-team/cycles/2026-09-01-d9-row2599-factor19069-factored-barrier-gate1/WORK_ORDERS.yaml": "7feb9e3ee717dd68f224886ce2e4fa1be78e869a9ee2ee708171988ac9eec6e0",
    "ops/research-team/cycles/2026-09-01-d9-row2599-factor19069-active-margin-gate1/CYCLE_REPORT.md": "0f57afe7ff32ec4c56766907caae73cab3fa788762e7086a000b689ae3d39203",
    "ops/team/d9-factor19069-active-margin-referee/RESULT.json": "29993b134fdebfbc3ae88f1cf9e2603de15990bb048ca38be3ea9b8bd3158dca",
    "ops/team/d9-factor19069-active-margin-constructor/ACTIVE_MARGIN_FRONTIER.json": "0875dd345a307bf9c4e33287cc13df1e6944c902d8a84c419a35cf9ddccbd243",
    "ops/team/d9-factor19069-active-margin-certificate/RESULT.json": "b853e56aa9ffcb5e37126169652f49fc8ff735e53cbb1ac86d96d53fcdf8ebcc",
    "ai/omreal/DIAG2_PIVOT_LABELED_PAIR_ORBITS_VERIFY.py": "8f51cf73ea75b4de7baf38af19b6e4cc941293edb82216a4aa00feef83c38e26",
    "ai/omreal/verify_diag3_pair_global_parent_face_gate.py": "64e94f55d2495c365128523ae1d8d2a7a9b9fc38e260d9a113834b836083be97",
    "ai/omreal/verify_diag3_pair_global_face_bernstein_atlas.py": "b54a74ba9ef4d1065728541f54c2cdc744638e2fa3e84d67da29a2cbe3ca3fb0",
    "ai/omreal/verify_diag3_pair_fullsupport_safe_segment_walls.py": "ea45d9541543207447fa3a8f3066dbc7716da68e46a90447283f0007322a3d1f",
    "ai/omreal/DIAG9_GRAPH_verify_row2599_slice.py": "8f550b570fa2a1352e5f7e5f251125df3af9ec87587b3da589fc25d46c15dedb",
    "ai/omreal/diag3_pair_parent_source_transition_core.py": "966a3e87b90affd984755bd4896db67aa7ae9b36f9fed97381b8f2d9f73a8dd1",
    "ai/omreal/data/DIAG3_PAIR_FULLSUPPORT_COMPONENT_COLLAR.json": "5930cc19019470fdfdf55d67523f6c4211ccf5b540f5c2bb5df36c64db75d7bd",
    "ai/omreal/data/DIAG3_PAIR_FULLSUPPORT_SEGMENT_COVER.json": "19248dd148d1fd002931ed5f48197869dd42c68a513376e1a4d6941389bda307",
    "ai/omreal/data/DIAG3_PAIR_GLOBAL_row2599_compactification_atlas.json": "956fbe7e5c7b1e04c8873ed9c0f3de9cb5420e3e06f1d5fae4c60f4e0571b364",
    "ai/omreal/data/DIAG3_PAIR_GLOBAL_row2599_parent_face_gate.json": "cc279d125605b45d25a3a01f462ad051038102f2bf12574f494a9d261bfc7401",
    "ai/omreal/certs_4_8.jsonl": "c55e805d60d8086bcb84a312f2103a9973fc2691d0fd97f3d9a1d9809d2b163b",
    "ai/omreal/data/DIAG3_PAIR_GLOBAL_row2599_candidate_factors.bin": "adb2e7257457f158e809450683c46fe7ecafdbdd4a7efdf9ac630e8a4f0fb03f",
    "ai/omreal/data/DIAG9_GRAPH_row2599_factor_states.npz": "f44b1fccfb4e61273aeceb8796a18098d82c48473e257556ce3d2a22f99b0bcf",
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


def canonical_digest(value) -> str:
    return sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":")).encode("ascii")
    ).hexdigest()


def git(*arguments: str) -> str:
    return subprocess.check_output(["git", *arguments], cwd=ROOT, text=True).strip()


def fraction_text(value: Fraction) -> str:
    return str(value.numerator) if value.denominator == 1 else f"{value.numerator}/{value.denominator}"


def polynomial_degree(polynomial: dict) -> int:
    return max(map(sum, polynomial))


def source_literal(path: Path, name: str):
    """Read a literal assignment without executing the source module."""

    syntax = ast.parse(path.read_text(encoding="utf-8"))
    for node in syntax.body:
        if isinstance(node, ast.Assign) and any(
            isinstance(target, ast.Name) and target.id == name for target in node.targets
        ):
            return ast.literal_eval(node.value)
    raise AssertionError(f"missing literal source constant {name}")


def mul_linear(polynomial, constant, linear):
    answer = [Fraction(0)] * (len(polynomial) + 1)
    for index, coefficient in enumerate(polynomial):
        answer[index] += coefficient * constant
        answer[index + 1] += coefficient * linear
    return answer


def segment_power(polynomial, left, right):
    answer = [Fraction(0)] * (polynomial_degree(polynomial) + 1)
    difference = tuple(r - l for l, r in zip(left, right, strict=True))
    for monomial, coefficient in polynomial.items():
        term = [Fraction(coefficient)]
        for coordinate, exponent in enumerate(monomial):
            for _ in range(exponent):
                term = mul_linear(term, left[coordinate], difference[coordinate])
        for index, value in enumerate(term):
            answer[index] += value
    while len(answer) > 1 and answer[-1] == 0:
        answer.pop()
    return answer


def restrict_power(coefficients, left, right):
    scale = right - left
    answer = [Fraction(0)] * len(coefficients)
    for power, coefficient in enumerate(coefficients):
        for index in range(power + 1):
            answer[index] += coefficient * comb(power, index) * left ** (power - index) * scale ** index
    while len(answer) > 1 and answer[-1] == 0:
        answer.pop()
    return answer


def univariate_bernstein(coefficients):
    degree = len(coefficients) - 1
    if degree == 0:
        return tuple(coefficients)
    return tuple(
        sum(
            coefficients[index] * Fraction(comb(position, index), comb(degree, index))
            for index in range(position + 1)
        )
        for position in range(degree + 1)
    )


def positive_unit(coefficients) -> bool:
    stack = [(Fraction(0), Fraction(1), 0)]
    while stack:
        left, right, depth = stack.pop()
        bernstein_coefficients = univariate_bernstein(restrict_power(coefficients, left, right))
        if all(value > 0 for value in bernstein_coefficients):
            continue
        if any(value < 0 for value in bernstein_coefficients) or depth >= 8:
            return False
        middle = (left + right) / 2
        stack.extend(((left, middle, depth + 1), (middle, right, depth + 1)))
    return True


def nonroot_split(polynomial, left, right):
    for numerator, denominator in ((1, 2), (1, 3), (2, 3), (2, 5), (3, 5), (1, 4), (3, 4)):
        middle = left + (right - left) * Fraction(numerator, denominator)
        if sturm.polynomial_value(polynomial, middle):
            return middle
    raise AssertionError("could not select rational root-isolation split")


def isolate_roots(polynomial):
    total = sturm.root_count(polynomial, Fraction(0), Fraction(1))
    stack = [(Fraction(0), Fraction(1), total)]
    answer = []
    while stack:
        left, right, count = stack.pop()
        if count == 0:
            continue
        if count == 1 and right - left <= ISOLATION_WIDTH:
            answer.append((left, right))
            continue
        middle = nonroot_split(polynomial, left, right)
        left_count = sturm.root_count(polynomial, left, middle)
        right_count = sturm.root_count(polynomial, middle, right)
        require(left_count + right_count == count, "root isolation lost a root")
        stack.append((middle, right, right_count))
        stack.append((left, middle, left_count))
    answer.sort()
    require(len(answer) == total, "root isolation census")
    return answer


def sparse_polynomial(polynomial: dict) -> list[dict]:
    return [
        {"exponents": list(monomial), "coefficient": int(coefficient)}
        for monomial, coefficient in sorted(polynomial.items())
        if coefficient
    ]


def derivative(polynomial: dict, coordinate: int) -> dict:
    answer = {}
    for monomial, coefficient in polynomial.items():
        exponent = monomial[coordinate]
        if exponent:
            reduced = list(monomial)
            reduced[coordinate] -= 1
            reduced = tuple(reduced)
            answer[reduced] = answer.get(reduced, 0) + coefficient * exponent
    return {monomial: coefficient for monomial, coefficient in answer.items() if coefficient}


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


def divide_one_minus_t(polynomial) -> tuple[Fraction, ...]:
    """Divide an ascending coefficient vector exactly by (1-t)."""

    polynomial = tuple(map(Fraction, polynomial))
    require(len(polynomial) >= 2, "constant polynomial cannot have endpoint root")
    quotient = [polynomial[0]]
    for index in range(1, len(polynomial) - 1):
        quotient.append(polynomial[index] + quotient[-1])
    require(polynomial[-1] == -quotient[-1], "nonexact (1-t) division")
    while len(quotient) > 1 and quotient[-1] == 0:
        quotient.pop()
    return tuple(quotient)


def strict_segment_certificate(polynomial) -> dict:
    """Prove q(t)>0 for 0<=t<1, allowing a root only at t=1."""

    polynomial = tuple(map(Fraction, polynomial))
    require(sturm.polynomial_value(polynomial, Fraction(0)) > 0, "path does not start strict")
    endpoint_multiplicity = 0
    reduced = polynomial
    while sturm.polynomial_value(reduced, Fraction(1)) == 0:
        reduced = divide_one_minus_t(reduced)
        endpoint_multiplicity += 1
    require(sturm.polynomial_value(reduced, Fraction(0)) > 0, "reduced start sign")
    require(sturm.polynomial_value(reduced, Fraction(1)) > 0, "reduced endpoint sign")
    open_roots = sturm.root_count(reduced, Fraction(0), Fraction(1))
    require(open_roots == 0, "parent factor changes sign on boundary path")
    return {
        "endpoint_zero_multiplicity": endpoint_multiplicity,
        "reduced_open_root_count": open_roots,
    }


def restriction_state(polynomial: dict, multidegree, face) -> str:
    signs = {
        1 if coefficient > 0 else -1
        for monomial, coefficient in polynomial.items()
        if all(
            support & ~allowed == 0
            for support, allowed in zip(
                bernstein.term_support(monomial, multidegree), face, strict=True
            )
        )
    }
    if not signs:
        return "IDENTICALLY_ZERO"
    if signs == {1}:
        return "BERNSTEIN_POSITIVE"
    if signs == {-1}:
        return "BERNSTEIN_NEGATIVE"
    require(signs == {-1, 1}, "invalid restriction sign set")
    return "BERNSTEIN_MIXED_UNRESOLVED"


def build_manifest() -> dict:
    require(git("rev-parse", f"{OPENING_REVISION}^{{tree}}") == OPENING_TREE, "opening tree drift")
    require(git("rev-parse", f"{BASE_REVISION}^{{tree}}") == BASE_TREE, "base tree drift")
    actual = {relative: digest_path(ROOT / relative) for relative in SOURCE_PINS}
    require(actual == SOURCE_PINS, "source pin drift")
    manifest = {
        "format": "d9-factor19069-factored-barrier-source-manifest-v1",
        "track_id": "d9-factor19069-factored-barrier-constructor",
        "opening_revision": OPENING_REVISION,
        "opening_tree": OPENING_TREE,
        "base_revision": BASE_REVISION,
        "base_tree": BASE_TREE,
        "source_sha256": actual,
        "source_count": len(actual),
        "drive_connector_used": False,
        "github_write": False,
    }
    manifest["semantic_sha256"] = canonical_digest(manifest)
    return manifest


def build() -> tuple[dict, dict]:
    manifest = build_manifest()
    records = [
        json.loads(line)
        for line in gate.CATALOG.read_text(encoding="utf-8").splitlines()
        if line
    ]
    parents, parent_sign_digest = gate.parent_polynomials(records[2599])
    require(len(parents) == 70, "parent factor census")
    candidates = gate.parse_candidates()
    _occurrences, _occurrence_factor, factors = labeled.factor_polynomials()
    require(TARGET_FACTOR in candidates, "factor 19069 left candidate universe")
    factor = factors[TARGET_FACTOR]
    factor_multidegree = tuple(
        max(sum(monomial[index] for index in group) for monomial in factor)
        for group in bernstein.GROUPS
    )
    require(polynomial_degree(factor) == 6, "factor degree")
    require(factor_multidegree == (2, 2, 2), "factor multidegree")
    require(len(factor) == 108, "factor term census")

    signed_parents = tuple(
        (label, {monomial: target * coefficient for monomial, coefficient in polynomial.items()})
        for label, target, polynomial, _terms in parents
    )
    factor_nodes = []
    for index, ((label, signed), (_source_label, target, polynomial, _terms)) in enumerate(
        zip(signed_parents, parents, strict=True)
    ):
        require(label == _source_label, "parent ordering drift")
        factor_nodes.append(
            {
                "node_id": f"H_{index:02d}_{label}",
                "label": label,
                "source_target_sign": target,
                "degree": polynomial_degree(signed),
                "term_count": len(signed),
                "sparse_polynomial": sparse_polynomial(signed),
            }
        )
    factor_node_ids = [node["node_id"] for node in factor_nodes]
    derivative_nodes = []
    nonzero_derivative_terms = Counter()
    for coordinate, variable in enumerate(VARIABLES):
        summands = []
        for factor_index, (_label, signed) in enumerate(signed_parents):
            differentiated = derivative(signed, coordinate)
            nonzero_derivative_terms[variable] += bool(differentiated)
            summands.append(
                {
                    "differentiated_factor_index": factor_index,
                    "derivative_sparse_polynomial": sparse_polynomial(differentiated),
                    "multiply_all_factor_indices_except": factor_index,
                }
            )
        derivative_nodes.append(
            {
                "node_id": f"dB_d{variable}",
                "coordinate_index": coordinate,
                "operation": "SUM_OVER_ALL_70_FACTORS_OF_DH_I_TIMES_PRODUCT_J_NE_I_H_J",
                "summands": summands,
            }
        )
    require(all(len(node["summands"]) == 70 for node in derivative_nodes), "dB factor loss")
    factor_derivatives = [
        {
            "node_id": f"df_d{variable}",
            "coordinate_index": coordinate,
            "sparse_polynomial": sparse_polynomial(derivative(factor, coordinate)),
        }
        for coordinate, variable in enumerate(VARIABLES)
    ]
    wedge_nodes = [
        {
            "node_id": f"wedge_{VARIABLES[left]}_{VARIABLES[right]}",
            "coordinate_pair": [left, right],
            "operation": "dB_left*df_right-dB_right*df_left",
            "inputs": [
                f"dB_d{VARIABLES[left]}",
                f"df_d{VARIABLES[right]}",
                f"dB_d{VARIABLES[right]}",
                f"df_d{VARIABLES[left]}",
            ],
        }
        for left in range(9)
        for right in range(left + 1, 9)
    ]
    require(len(wedge_nodes) == 36, "wedge equation census")
    circuit = {
        "format": "factor-circuit-dB-wedge-df-v1",
        "coordinates": list(VARIABLES),
        "wall_polynomial": {
            "node_id": "f_19069",
            "degree": 6,
            "multidegree": [2, 2, 2],
            "term_count": 108,
            "sparse_polynomial": sparse_polynomial(factor),
        },
        "barrier": {
            "node_id": "B",
            "operation": "PRODUCT",
            "ordered_factor_node_ids": factor_node_ids,
            "factor_count": 70,
            "total_degree": sum(polynomial_degree(polynomial) for _label, polynomial in signed_parents),
            "expanded_polynomial_present": False,
        },
        "parent_factor_nodes": factor_nodes,
        "barrier_derivative_nodes": derivative_nodes,
        "wall_derivative_nodes": factor_derivatives,
        "wedge_equation_nodes": wedge_nodes,
        "equation_contract": "f_19069=0 AND all_36_coefficients_of_dB_wedge_df=0",
    }
    require(circuit["barrier"]["total_degree"] == 90, "barrier degree")
    circuit_digest = canonical_digest(circuit)

    with np.load(gate.POINT_BANK, allow_pickle=False) as source:
        matrices = np.asarray(source["chart_matrix"], dtype=np.int64)
    require(matrices.shape == (178, 4, 8), "row-2599 point-bank shape")
    points = tuple(gate.normalized_values(matrix.tolist()) for matrix in matrices)
    edges = tuple(source_literal(OMREAL / "verify_diag3_pair_fullsupport_safe_segment_walls.py", "EDGES"))
    require(len(edges) == 105, "source edge census")
    cover = json.loads((DATA / "DIAG3_PAIR_FULLSUPPORT_SEGMENT_COVER.json").read_text(encoding="utf-8"))
    selected = tuple(cover["source_bank"]["selected_edge_indices"])
    require(len(selected) == 40, "skeleton census")
    path_tag_checks = 0
    for edge_index in selected:
        left, right = edges[edge_index]
        for _label, signed in signed_parents:
            require(positive_unit(segment_power(signed, points[left], points[right])), "skeleton parent path")
            path_tag_checks += 1
    root_counts = {}
    edge39_sample = None
    for edge_index in selected:
        left, right = edges[edge_index]
        restricted = primitive_univariate(segment_power(factor, points[left], points[right]))
        require(sturm.polynomial_value(restricted, Fraction(0)) != 0, "skeleton start root")
        require(sturm.polynomial_value(restricted, Fraction(1)) != 0, "skeleton end root")
        root_counts[str(edge_index)] = sturm.root_count(restricted, Fraction(0), Fraction(1))
        if edge_index == 39:
            intervals = isolate_roots(restricted)
            require(len(intervals) == 1, "edge39 isolating interval")
            interval = intervals[0]
            edge39_sample = {
                "sample_id": "WALL_ANCHOR_EDGE39_ROOT0",
                "kind": "RATIONAL_UNIVARIATE_POINT_ON_FIXED_SKELETON",
                "edge_index": 39,
                "edge_source_vertices": [left, right],
                "parameter_minimal_polynomial_coefficients_ascending": list(restricted),
                "parameter_isolating_interval": list(map(fraction_text, interval)),
                "coordinate_map": [
                    {
                        "constant": fraction_text(points[left][coordinate]),
                        "linear": fraction_text(points[right][coordinate] - points[left][coordinate]),
                    }
                    for coordinate in range(9)
                ],
                "attachment": "LIES_ON_FIXED_SKELETON_EDGE_39",
                "barrier_critical_sample": False,
            }
    require([int(edge) for edge, count in root_counts.items() if count] == [39], "rooted skeleton edges")
    require(root_counts["39"] == 1, "edge39 root count")
    require(edge39_sample is not None, "edge39 sample missing")

    parent_face = json.loads((DATA / "DIAG3_PAIR_GLOBAL_row2599_parent_face_gate.json").read_text(encoding="utf-8"))
    pinned_sample = gate.normalized_values(records[2599]["matrix"])
    boundary_records = []
    for record in parent_face["nonexcluded_support_faces"]:
        face = tuple(record["support"])
        if face == FULL_SUPPORT:
            continue
        witness = tuple(map(Fraction, record["witness"]))
        per_factor_path = []
        path_status = "CERTIFIED_LINEAR_PATH_FROM_PINNED_SAMPLE_IN_P_FOR_0_LE_T_LT_1"
        first_path_rejection = None
        for label, signed in signed_parents:
            restricted_path = segment_power(signed, pinned_sample, witness)
            try:
                certificate = strict_segment_certificate(restricted_path)
                per_factor_path.append({"label": label, **certificate})
            except AssertionError as error:
                path_status = "TESTED_LINEAR_PATH_REJECTED_NO_ALTERNATIVE_EXACT_PATH_CERTIFIED"
                first_path_rejection = {
                    "label": label,
                    "reason": str(error),
                    "restricted_signed_parent_polynomial_coefficients_ascending": [
                        fraction_text(value) for value in restricted_path
                    ],
                    "tested_parent_factors_before_rejection": len(per_factor_path),
                }
                break
        boundary_records.append(
            {
                "support": list(face),
                "dimension": record["dimension"],
                "parent_support_gate_classification": record["classification"].upper(),
                "factor19069_restriction": restriction_state(factor, factor_multidegree, face),
                "witness": list(map(fraction_text, witness)),
                "witness_zero_parent_factors": record["witness_zero_parent_brackets"],
                "parent_component_closure_path": {
                    "status": path_status,
                    "path": "x(t)=(1-t)*pinned_parent_sample+t*witness",
                    "parameter_domain": "0<=t<1",
                    "parent_factor_proof_count": len(per_factor_path),
                    "parent_factor_proof_semantic_sha256": canonical_digest(per_factor_path),
                    "first_rejection": first_path_rejection,
                },
                "wall_component_residence": "UNCLASSIFIED_FAIL_CLOSED",
            }
        )
    require(len(boundary_records) == 10, "proper boundary candidate census")
    boundary_counts = Counter(record["factor19069_restriction"] for record in boundary_records)
    require(boundary_counts == {"IDENTICALLY_ZERO": 8, "BERNSTEIN_MIXED_UNRESOLVED": 2}, "boundary factor census")

    critical_system = {
        "stratum_id": "FB-C0-STRICT-INTERIOR-FULL-SUPPORT",
        "support": list(FULL_SUPPORT),
        "ambient_dimension": 9,
        "equalities": ["f_19069=0", "all_36_coefficients_of_dB_wedge_df=0"],
        "strict_inequalities": [f"{node_id}>0" for node_id in factor_node_ids],
        "connected_parent_selector": "EXACT_PATH_IN_STRICT_PARENT_SIGN_SET_TO_PINNED_SAMPLE_REQUIRED",
        "factor_circuit_semantic_sha256": circuit_digest,
        "possible_component_dimensions": list(range(0, 9)),
        "singular_wall_pieces_included": True,
        "positive_dimensional_pieces_required": True,
        "component_decomposition_status": "UNSAMPLED_FAIL_CLOSED",
    }
    critical_system["semantic_sha256"] = canonical_digest(critical_system)
    first_boundary = boundary_records[0]
    frontier = {
        "format": "d9-factor19069-factored-barrier-frontier-v1",
        "track_id": "d9-factor19069-factored-barrier-constructor",
        "opening_revision": OPENING_REVISION,
        "opening_tree": OPENING_TREE,
        "base_revision": BASE_REVISION,
        "base_tree": BASE_TREE,
        "target": {
            "parent_index": 2599,
            "factor_id": TARGET_FACTOR,
            "parent_sign_factors": 70,
            "fixed_skeleton_edges": 40,
            "ambient_parameter_dimension": 9,
            "parent_sign_digest": parent_sign_digest,
        },
        "source_manifest_semantic_sha256": manifest["semantic_sha256"],
        "factor_circuit": circuit,
        "factor_circuit_semantic_sha256": circuit_digest,
        "circuit_census": {
            "parent_factor_nodes": 70,
            "parent_sparse_terms": sum(len(node["sparse_polynomial"]) for node in factor_nodes),
            "barrier_total_degree": 90,
            "dB_coordinate_nodes": 9,
            "dB_summands": 630,
            "nonzero_dH_factors_by_coordinate": dict(sorted(nonzero_derivative_terms.items())),
            "df_coordinate_nodes": 9,
            "wedge_equation_nodes": 36,
            "expanded_barrier_monomials": None,
            "expanded_product_used": False,
        },
        "strict_interior_critical_frontier": {
            "systems": [critical_system],
            "systems_constructed": 1,
            "connected_components_sampled": 0,
            "zero_dimensional_components_sampled": 0,
            "positive_dimensional_components_sampled": 0,
            "singular_pieces_discarded": 0,
            "first_unsampled_component_or_stratum": {
                "kind": "EXACT_SEMIALGEBRAIC_STRATUM_PENDING_CONNECTED_COMPONENT_DECOMPOSITION",
                "stratum_id": critical_system["stratum_id"],
                "stratum_semantic_sha256": critical_system["semantic_sha256"],
                "reason": "NO_PRODUCER_INDEPENDENT_EXACT_CONNECTED_COMPONENT_DECOMPOSITION_OR_THOM_ENCODING_WAS_COMPLETED_UNDER_THE_CEILING",
            },
        },
        "true_boundary_frontier": {
            "compactification_model": "(Delta^3)^3",
            "atlas_charts": 64,
            "ambient_product_support_strata": 3375,
            "parent_bernstein_excluded_support_strata": 3364,
            "proper_nonexcluded_candidate_strata": 10,
            "records": boundary_records,
            "certified_witness_paths_to_pinned_parent_closure": sum(
                record["parent_component_closure_path"]["status"].startswith("CERTIFIED")
                for record in boundary_records
            ),
            "wall_component_residence_classified_strata": 0,
            "first_unclassified_boundary_stratum": {
                "support": first_boundary["support"],
                "factor19069_restriction": first_boundary["factor19069_restriction"],
                "obligation": "DECOMPOSE_PARENT_RESIDENT_BOUNDARY_WALL_GERM_AND_ATTACH_IT_TO_AN_INTERIOR_WALL_COMPONENT",
                "record_semantic_sha256": canonical_digest(first_boundary),
            },
            "true_parent_boundary_kept_distinct_from": [
                "SOLVER_BOUNDARY",
                "BOX_BOUNDARY",
                "COLLAR_BOUNDARY",
                "SKELETON_EDGE_ENDPOINT",
            ],
        },
        "fixed_skeleton_accounting": {
            "all_40_edges_retain_all_70_parent_tags": True,
            "parent_path_tag_checks": path_tag_checks,
            "factor19069_open_root_counts_by_edge": root_counts,
            "exact_attached_wall_anchor": edge39_sample,
            "global_wall_component_count": None,
            "global_attached_component_count": None,
            "global_unattached_component_count": None,
            "attachment_classification_complete": False,
        },
        "resource_accounting": {
            "max_exact_solver_component_nodes": MAX_COMPONENT_NODES,
            "exact_solver_component_nodes_used": 0,
            "ceiling_crossed": False,
            "stop_trigger": "MISSING_EXACT_CRITICAL_LOCUS_COMPONENT_DECOMPOSITION_AND_PATH_CERTIFICATE",
            "paid_or_external_compute": False,
        },
        "endpoint": "HASH_PINNED_FACTORED_BARRIER_CRITICAL_COMPONENT_FRONTIER_WITH_FIRST_UNSAMPLED_COMPONENT",
        "classification": "EXACT_FAIL_CLOSED_FACTORED_BARRIER_COMPONENT_NULL",
        "exact_consequences": [
            "SOURCE_DERIVED_70_FACTOR_BARRIER_CIRCUIT_CONSTRUCTED_WITHOUT_EXPANSION",
            "ALL_36_EXACT_dB_WEDGE_df_CIRCUIT_EQUATIONS_CONSTRUCTED",
            "STRICT_INTERIOR_CRITICAL_STRATUM_HASH_PINNED_WITH_ZERO_AND_POSITIVE_DIMENSION_OBLIGATIONS",
            "TEN_NONEXCLUDED_PROPER_SUPPORT_STRATA_RETAINED_WITH_CONNECTED_PARENT_WITNESS_PATH_STATUS",
            "EXACT_EDGE39_WALL_ANCHOR_REPLAYED_WITHOUT_GLOBAL_COMPONENT_INFERENCE",
        ],
        "nonconsequences": [
            "NO_CONNECTED_COMPONENT_DECOMPOSITION_OF_THE_BARRIER_CRITICAL_LOCUS",
            "NO_CRITICAL_COMPONENT_SAMPLE_OR_THOM_ENCODING",
            "NO_COMPLETE_BOUNDARY_WALL_GERM_TO_INTERIOR_COMPONENT_CLASSIFICATION",
            "NO_GLOBAL_FACTOR19069_WALL_COMPONENT_COUNT",
            "NO_COMPLETE_COMPONENT_TO_SKELETON_ATTACHMENT_CLASSIFICATION",
            "NO_DIAGONAL_9_PROOF_OR_COUNTEREXAMPLE",
            "NO_9DVL_SCORE_CHANGE",
        ],
        "fail_closed_controls": [
            "OPENING_REVISION_TREE_PIN",
            "BASE_REVISION_TREE_PIN",
            "ALL_SOURCE_SHA256_PINS",
            "TARGET_FACTOR_MEMBERSHIP",
            "FACTOR_DEGREE_MULTIDEGREE_TERM_CENSUS",
            "SEVENTY_ORDERED_SIGNED_PARENT_FACTORS",
            "NO_EXPANDED_BARRIER_FIELD",
            "NINE_COMPLETE_dB_SUMS_EACH_WITH_SEVENTY_TERMS",
            "THIRTY_SIX_WEDGE_EQUATIONS",
            "SINGULAR_PIECES_INCLUDED",
            "POSITIVE_DIMENSIONAL_PIECES_REQUIRED",
            "CONNECTED_PARENT_SELECTOR_REQUIRED",
            "ALL_TRUE_BOUNDARY_CANDIDATES_RETAINED",
            "ARTIFICIAL_BOUNDARIES_DISTINCT",
            "FORTY_EDGE_SEVENTY_PARENT_PATH_REPLAY",
            "EDGE39_EXACT_ROOT_IS_LOCAL_ONLY",
            "GLOBAL_ATTACHMENT_REMAINS_INCOMPLETE",
            "LEDGER_REMAINS_TWO_OF_NINE",
        ],
        "producer_independent_certificate_present": False,
        "ledger_change_recommended": "none",
        "theorem_ledger": "2/9",
    }
    frontier["semantic_sha256"] = canonical_digest(frontier)
    return manifest, frontier


def main() -> None:
    manifest, frontier = build()
    MANIFEST.write_bytes((json.dumps(manifest, indent=2, sort_keys=True) + "\n").encode("utf-8"))
    OUTPUT.write_bytes((json.dumps(frontier, indent=2, sort_keys=True) + "\n").encode("utf-8"))
    boundary = frontier["true_boundary_frontier"]
    print("PASS source-derived B=product(H_I): factors=70 degree=90 expanded=false")
    print("PASS exact dB wedge df circuit: dB_summands=630 wedge_equations=36")
    print(
        "PASS boundary candidate paths",
        f"{boundary['certified_witness_paths_to_pinned_parent_closure']}/10",
    )
    print("PASS local skeleton anchor: edge39 roots=1; global inference=false")
    print("NULL first_unsampled=FB-C0-STRICT-INTERIOR-FULL-SUPPORT ledger=2/9")


if __name__ == "__main__":
    main()
