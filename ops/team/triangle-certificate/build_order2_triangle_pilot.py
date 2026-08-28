#!/usr/bin/env python3
"""Exact producer for the row-2599 chart-(0,89,113) triangle pilot.

The producer proves parent residence with exact simplex-Bernstein controls and
classifies each restricted residual factor as far as a bounded deterministic
subdivision permits.  It emits witnesses for interior zeroes, including those
whose factor is absent from both compiled source-edge roadmaps.

This is intentionally producer-side only.  A later referee must independently
replay the certificate without importing this module.
"""

from __future__ import annotations

import argparse
from copy import deepcopy
from fractions import Fraction
import hashlib
import json
from pathlib import Path
import sys

import numpy as np


ROOT = Path(__file__).resolve().parents[3]
OMREAL = ROOT / "ai" / "omreal"
sys.path.insert(0, str(OMREAL))
sys.path.insert(0, str(OMREAL / "exact_semialgebraic"))

import DIAG2_PIVOT_LABELED_PAIR_ORBITS_VERIFY as labeled  # noqa: E402
import tensor_bernstein as exact  # noqa: E402
import verify_diag3_pair_global_parent_face_gate as gate  # noqa: E402


FORMAT = "diag3-pair-row2599-order2-triangle-pilot-v1"
PREFIX = b"diag3-pair-row2599-order2-triangle-pilot-v1\0"
TRIANGLE = ((Fraction(0), Fraction(0)), (Fraction(1), Fraction(0)), (Fraction(0), Fraction(1)))
INPUTS = {
    "ai/omreal/certs_4_8.jsonl":
        "c55e805d60d8086bcb84a312f2103a9973fc2691d0fd97f3d9a1d9809d2b163b",
    "ai/omreal/data/seeat_parent2599_upper178.npz":
        "3b90799d26b7783e92c2ac697eaaf8b76d26a787f53205873b997657e114180a",
    "ai/omreal/data/DIAG9_GRAPH_global_factor_census.npz":
        "3984ce87e11fd59d804e59568177248e218cd1c7bb07aae0a9f9f746858728bc",
    "ai/omreal/data/DIAG3_PAIR_GLOBAL_row2599_candidate_factors.bin":
        "adb2e7257457f158e809450683c46fe7ecafdbdd4a7efdf9ac630e8a4f0fb03f",
    "ai/omreal/data/DIAG3_PAIR_FULLSUPPORT_LABELED_SKELETON.json":
        "5430bd79ae9ddee09ce9b393f018389be1210c250a7eb0d5486fab8e1294663d",
    "ai/omreal/data/DIAG3_PAIR_PARENT_SOURCE_TRANSITION_EDGE39_0_113.json":
        "cb6eebc0df9bfeae8055c81471f09d594f8116e002caf11f62f9e865b0936dd7",
    "ai/omreal/data/DIAG3_PAIR_FULLSUPPORT_LABELED_SKELETON_EDGE27_EDGE39.json":
        "dcb707220df3e61b1a94eeedcf8e46b6602f30d405f4a92fc542c0f52f672806",
    "ai/omreal/exact_semialgebraic/tensor_bernstein.py":
        "fe0274d19a27dc70707133c6bcaba9f976b7ba245568440b71b0c0275740272c",
}


def canonical(value: object) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode("utf-8")


def file_digest(path: Path) -> str:
    answer = hashlib.sha256()
    with path.open("rb") as source:
        for block in iter(lambda: source.read(1 << 20), b""):
            answer.update(block)
    return answer.hexdigest()


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def fraction_text(value: Fraction) -> str:
    value = Fraction(value)
    return str(value.numerator) if value.denominator == 1 else f"{value.numerator}/{value.denominator}"


def point_text(point) -> list[str]:
    return [fraction_text(value) for value in point]


def sign(value: Fraction) -> int:
    return 1 if value > 0 else -1 if value < 0 else 0


def barycentric(point) -> tuple[Fraction, Fraction, Fraction]:
    s, t = point
    return Fraction(1) - s - t, s, t


def strictly_interior(point) -> bool:
    return all(value > 0 for value in barycentric(point))


def open_segment_is_interior(left, right) -> bool:
    """Every open segment point is interior iff no barycentric face contains both ends."""

    return all(not (a == 0 and b == 0) for a, b in zip(barycentric(left), barycentric(right)))


def longest_edge(vertices):
    choices = []
    for left in range(3):
        for right in range(left + 1, 3):
            distance = sum((vertices[left][axis] - vertices[right][axis]) ** 2 for axis in range(2))
            choices.append((distance, -left, -right, left, right))
    return max(choices)[-2:]


def witness_from_vertices(polynomial, vertices):
    values = [exact.evaluate(polynomial, point) for point in vertices]
    for point, value in zip(vertices, values):
        if value == 0 and strictly_interior(point):
            return {
                "kind": "EXACT_INTERIOR_POINT",
                "point": point_text(point),
            }
    for left in range(len(vertices)):
        for right in range(left + 1, len(vertices)):
            if values[left] * values[right] < 0 and open_segment_is_interior(vertices[left], vertices[right]):
                return {
                    "kind": "OPPOSITE_SIGNS_ON_INTERIOR_OPEN_SEGMENT",
                    "left": point_text(vertices[left]),
                    "right": point_text(vertices[right]),
                    "left_sign": sign(values[left]),
                    "right_sign": sign(values[right]),
                }
    return None


def probe_points():
    points = [(Fraction(1, 3), Fraction(1, 3))]
    for exponent in (4, 8, 12):
        epsilon = Fraction(1, 1 << exponent)
        points.extend((
            (epsilon, epsilon),
            (Fraction(1) - 2 * epsilon, epsilon),
            (epsilon, Fraction(1) - 2 * epsilon),
        ))
    require(all(strictly_interior(point) for point in points), "probe interior")
    return tuple(points)


def classify_restriction(polynomial, max_depth: int):
    if not polynomial:
        return "INTERIOR_ZERO", {
            "kind": "IDENTICALLY_ZERO_RESTRICTION",
            "point": ["1/3", "1/3"],
        }, 0, 1

    probes = probe_points()
    witness = witness_from_vertices(polynomial, probes)
    if witness is not None:
        witness["source"] = "fixed_strict_interior_probe_bank"
        return "INTERIOR_ZERO", witness, 0, 1

    stack = [(TRIANGLE, 0)]
    unresolved_cells = 0
    deepest = 0
    visited = 0
    while stack:
        vertices, depth = stack.pop()
        visited += 1
        deepest = max(deepest, depth)
        witness = witness_from_vertices(polynomial, vertices)
        if witness is not None:
            witness["source"] = "deterministic_longest_edge_subdivision"
            return "INTERIOR_ZERO", witness, deepest, visited

        base = vertices[0]
        rows = tuple(
            tuple(vertices[target + 1][axis] - base[axis] for target in range(2))
            for axis in range(2)
        )
        pulled = exact.affine_pullback(polynomial, base, rows)
        if not pulled:
            # A full-dimensional subtriangle cannot carry an identically zero
            # restriction unless the entire two-variable polynomial is zero.
            return "INTERIOR_ZERO", {
                "kind": "IDENTICALLY_ZERO_SUBTRIANGLE",
                "point": point_text(tuple(sum(vertex[axis] for vertex in vertices) / 3 for axis in range(2))),
                "source": "deterministic_longest_edge_subdivision",
            }, deepest, visited
        controls, _degree = exact.simplex_bernstein_control(pulled)
        control_signs = {sign(value) for value in controls.values()}
        if 0 not in control_signs and len(control_signs) == 1:
            continue
        if depth >= max_depth:
            unresolved_cells += 1
            continue
        left, right = longest_edge(vertices)
        midpoint = tuple((vertices[left][axis] + vertices[right][axis]) / 2 for axis in range(2))
        first = list(vertices); first[left] = midpoint
        second = list(vertices); second[right] = midpoint
        stack.append((tuple(first), depth + 1))
        stack.append((tuple(second), depth + 1))

    if unresolved_cells:
        return "UNRESOLVED", {
            "reason_code": "MIXED_SIMPLEX_BERNSTEIN_AT_DEPTH_LIMIT",
            "unresolved_leaf_count": unresolved_cells,
        }, deepest, visited
    return "EMPTY_CLOSED_TRIANGLE", None, deepest, visited


def event_factor_sets(combined: dict) -> tuple[set[int], set[int]]:
    result = {27: set(), 39: set()}
    for cell in combined["compiled_regular_subcomplex"]["cells"]:
        cell_id = cell.get("id", "")
        if cell.get("kind") != "isolated_residual_event":
            continue
        for edge in result:
            if f":edge:{edge:03d}:" in cell_id:
                result[edge].add(int(cell["factor_id"]))
                break
    require(result[27] and result[39], "compiled event factor sets")
    return result[27], result[39]


def parent_certificate(parents, base, rows):
    records = []
    aggregate = hashlib.sha256(b"diag3-row2599-order2-triangle-parent-controls-v1\0")
    for label, target, polynomial, _terms in parents:
        signed = {monomial: Fraction(target * coefficient) for monomial, coefficient in polynomial.items()}
        pulled = exact.affine_pullback(signed, base, rows)
        controls, degree = exact.simplex_bernstein_control(pulled)
        require(all(value > 0 for value in controls.values()), f"parent bracket {label}")
        serial = [
            [list(index), fraction_text(value)]
            for index, value in sorted(controls.items())
        ]
        control_digest = hashlib.sha256(canonical(serial)).hexdigest()
        aggregate.update(label.encode("ascii") + b"\0" + bytes.fromhex(control_digest))
        records.append({
            "parent_bracket": label,
            "target_sign": target,
            "total_degree": degree,
            "control_count": len(controls),
            "minimum_positive_control": fraction_text(min(controls.values())),
            "controls_sha256": control_digest,
        })
    return records, aggregate.hexdigest()


def build(max_depth: int) -> dict:
    require(max_depth >= 0, "negative max depth")
    for relative, expected in INPUTS.items():
        require(file_digest(ROOT / relative) == expected, f"input digest {relative}")

    records = [json.loads(line) for line in gate.CATALOG.read_text().splitlines() if line]
    parents, parent_sign_digest = gate.parent_polynomials(records[2599])
    with np.load(gate.POINT_BANK, allow_pickle=False) as source:
        matrices = np.asarray(source["chart_matrix"], dtype=np.int64)
    points = tuple(gate.normalized_values(matrix.tolist()) for matrix in matrices)
    base = points[0]
    rows = tuple((points[89][axis] - base[axis], points[113][axis] - base[axis]) for axis in range(9))
    parent_rows, parent_control_digest = parent_certificate(parents, base, rows)

    combined = json.loads((ROOT / "ai/omreal/data/DIAG3_PAIR_FULLSUPPORT_LABELED_SKELETON_EDGE27_EDGE39.json").read_text())
    edge27_factors, edge39_factors = event_factor_sets(combined)
    candidates = gate.parse_candidates()
    _occurrences, _occurrence_factor, polynomials = labeled.factor_polynomials()

    interior_count = 0
    interior_by_witness: dict[int, list[int]] = {}
    witness_catalog = []
    witness_ids = {}
    empty_count = 0
    empty_by_proof: dict[tuple[int, int], list[int]] = {}
    unresolved_by_reason: dict[str, list] = {}
    deepest_census: dict[int, int] = {}
    visited_total = 0
    interior_absent_from_compiled_edges = []

    for factor_id in candidates:
        restricted = exact.affine_pullback(polynomials[factor_id], base, rows)
        status, proof, deepest, visited = classify_restriction(restricted, max_depth)
        deepest_census[deepest] = deepest_census.get(deepest, 0) + 1
        visited_total += visited
        if status == "INTERIOR_ZERO":
            key = canonical(proof)
            witness_id = witness_ids.get(key)
            if witness_id is None:
                witness_id = len(witness_catalog)
                witness_ids[key] = witness_id
                witness_catalog.append({"witness_id": witness_id, "proof": proof})
            interior_count += 1
            interior_by_witness.setdefault(witness_id, []).append(factor_id)
            if factor_id not in edge27_factors and factor_id not in edge39_factors:
                interior_absent_from_compiled_edges.append(factor_id)
        elif status == "EMPTY_CLOSED_TRIANGLE":
            empty_count += 1
            empty_by_proof.setdefault((deepest, visited), []).append(factor_id)
        else:
            code = proof["reason_code"]
            unresolved_by_reason.setdefault(code, []).append([
                factor_id,
                deepest,
                visited,
                proof["unresolved_leaf_count"],
            ])

    unresolved_count = sum(len(values) for values in unresolved_by_reason.values())
    require(interior_count + empty_count + unresolved_count == len(candidates), "classification accounting")

    record = {
        "format": FORMAT,
        "status": "EXACT_BOUNDED_TRIANGLE_CLASSIFICATION",
        "base_revision": "ec362dba8a912bc4749c004641aee2da0a88dc05",
        "inputs": INPUTS,
        "scope": {
            "ledger_id": "diag3_pair_hc1",
            "parent_index": 2599,
            "support": [15, 15, 15],
            "domain": "closed barycentric triangle conv(chart0,chart89,chart113)",
            "parameterization": "x(s,t)=chart0+s(chart89-chart0)+t(chart113-chart0)",
            "parameter_domain": "s>=0,t>=0,s+t<=1",
            "compiled_boundary_edges": {"t=0": 27, "s=0": 39},
            "third_boundary_edge": "chart89_to_chart113_NOT_COMPILED",
            "affine_square_promotion": False,
            "triangle_boundary_is_parent_infinity": False,
            "global_parent_cell_coverage": "NOT_CLAIMED",
            "global_component_coverage": "NOT_CLAIMED",
            "pair_branch_closed": False,
            "honest_9dvl_score": "2/9_UNCHANGED",
        },
        "exact_parent_residence": {
            "method": "exact triangular simplex-Bernstein controls on the whole closed triangle",
            "signed_parent_bracket_count": len(parent_rows),
            "all_controls_strictly_positive": True,
            "normalized_parent_signs_sha256": parent_sign_digest,
            "aggregate_controls_sha256": parent_control_digest,
            "brackets": parent_rows,
        },
        "classification_method": {
            "arithmetic": "EXACT_RATIONAL",
            "interior_probe_points": [point_text(point) for point in probe_points()],
            "subdivision": "deterministic_longest_edge_bisection",
            "max_depth": max_depth,
            "empty_rule": "one-signed nonzero simplex-Bernstein controls cover every leaf",
            "interior_zero_rule": "exact interior point zero or opposite endpoint signs on a segment whose open part lies in the triangle interior",
            "unresolved_rule": "mixed/zero Bernstein hull at max depth is retained without a zero claim",
        },
        "compiled_edge_accounting": {
            "edge27_distinct_factor_count": len(edge27_factors),
            "edge39_distinct_factor_count": len(edge39_factors),
            "union_distinct_factor_count": len(edge27_factors | edge39_factors),
            "edge27_factor_ids_sha256": hashlib.sha256(",".join(map(str, sorted(edge27_factors))).encode("ascii")).hexdigest(),
            "edge39_factor_ids_sha256": hashlib.sha256(",".join(map(str, sorted(edge39_factors))).encode("ascii")).hexdigest(),
        },
        "factor_classification": {
            "candidate_factor_count": len(candidates),
            "interior_zero_count": interior_count,
            "empty_closed_triangle_count": empty_count,
            "unresolved_count": unresolved_count,
            "witness_catalog": witness_catalog,
            "interior_zero_witness_groups": [
                {"witness_id": witness_id, "factor_ids": factor_ids}
                for witness_id, factor_ids in sorted(interior_by_witness.items())
            ],
            "empty_closed_triangle_proof_groups": [
                {"deepest_subdivision": key[0], "subtriangles_visited": key[1], "factor_ids": factor_ids}
                for key, factor_ids in sorted(empty_by_proof.items())
            ],
            "unresolved_by_reason": [
                {"reason_code": code, "records": values}
                for code, values in sorted(unresolved_by_reason.items())
            ],
            "deepest_subdivision_census": {str(key): value for key, value in sorted(deepest_census.items())},
            "total_subtriangles_visited": visited_total,
        },
        "interior_zero_absent_from_edges_27_39": {
            "count": len(interior_absent_from_compiled_edges),
            "factor_ids": interior_absent_from_compiled_edges,
            "proof_lookup": "factor_classification.interior_zero_witness_groups -> witness_catalog",
            "meaning": "Each factor has an exact interior zero witness but no event in either compiled edge roadmap.",
        },
        "producer_canaries": {
            "required_hostile_mutations": [
                "unsafe affine-square promotion",
                "triangle boundary treated as parent infinity",
                "global coverage claim",
                "pair closure claim",
                "3/9 score promotion",
                "factor or accounting digest corruption",
            ],
            "referee_replay": "REQUIRED_SEPARATELY",
        },
        "theorem_effect": (
            "Exact bounded order-two triangle pilot only; it does not certify global parent-cell or wall-component coverage, "
            "does not close diag3_pair_hc1, and leaves the honest 9DVL score at 2/9."
        ),
    }
    record["semantic_sha256"] = hashlib.sha256(PREFIX + canonical(record)).hexdigest()
    return record


def validate_producer_semantics(record: dict) -> None:
    require(record["format"] == FORMAT, "format")
    scope = record["scope"]
    require(scope["domain"] == "closed barycentric triangle conv(chart0,chart89,chart113)", "triangle domain")
    require(scope["affine_square_promotion"] is False, "unsafe square promotion")
    require(scope["triangle_boundary_is_parent_infinity"] is False, "false parent infinity")
    require(scope["global_parent_cell_coverage"] == "NOT_CLAIMED", "global parent coverage")
    require(scope["global_component_coverage"] == "NOT_CLAIMED", "global component coverage")
    require(scope["pair_branch_closed"] is False, "pair closure")
    require(scope["honest_9dvl_score"] == "2/9_UNCHANGED", "score promotion")
    require(record["inputs"] == INPUTS, "input/accounting digests")
    counts = record["factor_classification"]
    require(counts["interior_zero_count"] + counts["empty_closed_triangle_count"] + counts["unresolved_count"] == counts["candidate_factor_count"] == 17_824, "factor accounting")


def producer_canaries(record: dict) -> None:
    mutations = []
    changed = deepcopy(record); changed["scope"]["affine_square_promotion"] = True; mutations.append(changed)
    changed = deepcopy(record); changed["scope"]["triangle_boundary_is_parent_infinity"] = True; mutations.append(changed)
    changed = deepcopy(record); changed["scope"]["global_parent_cell_coverage"] = "COMPLETE"; mutations.append(changed)
    changed = deepcopy(record); changed["scope"]["global_component_coverage"] = "COMPLETE"; mutations.append(changed)
    changed = deepcopy(record); changed["scope"]["pair_branch_closed"] = True; mutations.append(changed)
    changed = deepcopy(record); changed["scope"]["honest_9dvl_score"] = "3/9"; mutations.append(changed)
    changed = deepcopy(record); changed["inputs"][next(iter(INPUTS))] = "0" * 64; mutations.append(changed)
    changed = deepcopy(record); changed["factor_classification"]["candidate_factor_count"] -= 1; mutations.append(changed)
    for changed in mutations:
        try:
            validate_producer_semantics(changed)
        except AssertionError:
            continue
        raise AssertionError("hostile producer mutation escaped")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--max-depth", type=int, default=3)
    arguments = parser.parse_args()
    record = build(arguments.max_depth)
    validate_producer_semantics(record)
    producer_canaries(record)
    print(json.dumps(record, sort_keys=True, separators=(",", ":")))


if __name__ == "__main__":
    main()
