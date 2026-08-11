#!/usr/bin/env python3
"""Exact ordered two-root carrier audit on the 178 stored row-2599 charts.

For each exact chart, take the bad-signature pair stored as the minimum
elementary escape-overlap witness in ``DIAG2_ESCAPE_SET_atlas178_summary``.
Build its common elementary-root graph.  Two vertices are adjacent when one
common ordering of their shears has a nonempty positive Gordan face for both
signatures after the full ``Lambda^3`` inverse transport, including the
bilinear ``u*v`` term.

The semantic digest pins the signatures, common 112-bit vertex mask, and
complete unordered joint-edge list for every chart.  This is an exact finite
theorem about one stored minimum pair at each of 178 point charts.  The charts
are not a coverage-certified atlas of the parent cell, and this checker does
not prove the third diagonal or a universal carrier theorem.
"""

from __future__ import annotations

import argparse
from collections import Counter
from concurrent.futures import ProcessPoolExecutor, as_completed
import hashlib
import json
from pathlib import Path
import sys

import numpy as np


HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import DIAG9_GRAPH_exact_topes as exact_topes  # noqa: E402
import verify_diag2_escape_set_topes as escape  # noqa: E402
import verify_diag2_moving_witness_shear as moving  # noqa: E402


ATLAS = HERE / "data" / "seeat_parent2599_upper178.npz"
SUMMARY = HERE / "data" / "DIAG2_ESCAPE_SET_atlas178_summary.json"
EXPECTED_CHARTS = 178
EXPECTED_VERTEX_HISTOGRAM = {6: 32, 8: 81, 9: 30, 10: 24, 11: 11}
EXPECTED_CANDIDATE_EDGE_HISTOGRAM = {
    15: 32,
    28: 81,
    35: 25,
    36: 5,
    45: 24,
    54: 11,
}
EXPECTED_JOINT_EDGE_HISTOGRAM = {
    9: 13,
    11: 8,
    14: 2,
    15: 9,
    22: 10,
    24: 6,
    26: 18,
    27: 6,
    28: 57,
    29: 2,
    30: 4,
    32: 1,
    35: 7,
    39: 5,
    40: 8,
    41: 7,
    43: 4,
    52: 11,
}
EXPECTED_MINIMUM_JOINT_EDGES = 9
EXPECTED_MINIMUM_VERTEX_DEGREE = 2
EXPECTED_MAXIMUM_VERTEX_DEGREE = 10
EXPECTED_SEMANTIC_DIGEST = (
    "7a3beb589109c8343be17084514eadd778f5eb6ebb918f0d67dafc05120d78ef"
)
CHART57_SIGNATURES = (1_211_253_791_914_816, 3_827_403_733_557_248)
CHART57_ISOLATED_DIRECTION = (3, 6, 1)


def independent(left, right):
    """Return whether the two signed roots span distinct root lines."""
    return left[:2] != right[:2]


def commuting(left, right):
    """Return whether the two elementary root matrices commute."""
    return left[0] != right[1] and right[0] != left[1]


def transformed_basis(label, first, second):
    """Expand ``g^-1 e_label`` for ``g=(1+uN_first)(1+vN_second)``.

    A tuple ``(target,u_degree,v_degree,coefficient)`` represents one term.
    The inverse factors act in the order
    ``(1-vN_second)(1-uN_first)e_label``.
    """
    terms = [(label, 0, 0, 1)]
    for (u_degree, v_degree), direction in (
        ((1, 0), first),
        ((0, 1), second),
    ):
        source, target, parameter_sign = direction
        expanded = list(terms)
        for current, old_u, old_v, coefficient in terms:
            if current == source:
                expanded.append(
                    (
                        target,
                        old_u + u_degree,
                        old_v + v_degree,
                        -parameter_sign * coefficient,
                    )
                )
        terms = expanded
    return terms


def safe_rows(signature, first, second):
    """Rows whose complete ordered third-compound transport stays orthant-safe."""
    safe = 0
    for source_index, triple in enumerate(moving.TRIPLES):
        coefficients = {}
        factors = [transformed_basis(label, first, second) for label in triple]
        for left in factors[0]:
            for middle in factors[1]:
                for right in factors[2]:
                    sequence = (left[0], middle[0], right[0])
                    if len(set(sequence)) != 3:
                        continue
                    target_index = moving.TRIPLE_INDEX[tuple(sorted(sequence))]
                    monomial = (
                        left[1] + middle[1] + right[1],
                        left[2] + middle[2] + right[2],
                    )
                    coefficient = (
                        left[3]
                        * middle[3]
                        * right[3]
                        * moving.orientation_sign(sequence)
                    )
                    key = (target_index, monomial)
                    coefficients[key] = coefficients.get(key, 0) + coefficient

        source_sign = moving.signature_sign(signature, source_index)
        good = True
        for (target_index, monomial), coefficient in coefficients.items():
            if monomial == (0, 0) or coefficient == 0:
                continue
            orthant_sign = (
                source_sign
                * moving.signature_sign(signature, target_index)
                * coefficient
            )
            if orthant_sign < 0:
                good = False
                break
        if good:
            safe |= 1 << source_index
    return safe


def has_positive_dependence(signature, kept, topes):
    """Apply strict Gordan duality using the complete derived-tope table."""
    return not any(((tope ^ signature) & kept) == 0 for tope in topes)


def order_works(signatures, first_index, second_index, topes):
    first = escape.DIRECTIONS[first_index]
    second = escape.DIRECTIONS[second_index]
    return all(
        has_positive_dependence(
            signature,
            safe_rows(signature, first, second),
            topes,
        )
        for signature in signatures
    )


def components(vertices, edges):
    adjacency = {vertex: set() for vertex in vertices}
    for left, right in edges:
        adjacency[left].add(right)
        adjacency[right].add(left)
    remaining = set(vertices)
    answer = []
    while remaining:
        component = set()
        stack = [min(remaining)]
        while stack:
            current = stack.pop()
            if current not in remaining:
                continue
            remaining.remove(current)
            component.add(current)
            stack.extend(adjacency[current] & remaining)
        answer.append(tuple(sorted(component)))
    return tuple(answer), adjacency


def audit_chart(chart):
    payload = json.loads(SUMMARY.read_text(encoding="utf-8"))
    summary = payload["results"][chart]
    if int(summary["chart"]) != chart:
        raise AssertionError("stored summary is not in chart order")
    signatures = (int(summary["overlap_left"]), int(summary["overlap_right"]))
    with np.load(ATLAS, allow_pickle=False) as source:
        matrix = source["chart_matrix"][chart]

    rows = exact_topes.derived_rows(matrix)
    enumerated = exact_topes.enumerate_topes(rows, dimension=4)
    exact_topes.verify_topes(rows, enumerated)
    topes = tuple(enumerated)
    if len(topes) != 26_112:
        raise AssertionError(f"chart {chart}: wrong complete-tope count")

    prepared = escape.prepare_directions(topes)
    masks = tuple(escape.escape_mask(signature, prepared) for signature in signatures)
    common_mask = masks[0] & masks[1]
    vertices = tuple(index for index in range(112) if (common_mask >> index) & 1)
    if len(vertices) != int(summary["minimum_overlap"]):
        raise AssertionError(f"chart {chart}: stored overlap witness changed")

    candidates = []
    edges = []
    for offset, left in enumerate(vertices):
        for right in vertices[offset + 1 :]:
            if not independent(escape.DIRECTIONS[left], escape.DIRECTIONS[right]):
                continue
            candidates.append((left, right))
            if order_works(signatures, left, right, topes) or order_works(
                signatures, right, left, topes
            ):
                edges.append((left, right))

    component_sets, adjacency = components(vertices, edges)
    degrees = tuple(len(adjacency[vertex]) for vertex in vertices)
    if len(component_sets) != 1:
        raise AssertionError(
            f"chart {chart}: disconnected ordered-root graph {component_sets}"
        )
    return {
        "chart": chart,
        "left": signatures[0],
        "right": signatures[1],
        "common_mask": common_mask,
        "vertices": len(vertices),
        "candidate_edges": len(candidates),
        "joint_edges": len(edges),
        "minimum_degree": min(degrees),
        "maximum_degree": max(degrees),
        "edges": tuple(edges),
    }


def semantic_digest(records):
    digest = hashlib.sha256()
    digest.update(b"diag3-ordered-root-atlas178-minimum-pairs-v1\0")
    for record in sorted(records, key=lambda row: row["chart"]):
        for key in ("chart", "left", "right"):
            digest.update(int(record[key]).to_bytes(8, "little", signed=False))
        digest.update(int(record["common_mask"]).to_bytes(16, "little", signed=False))
        digest.update(len(record["edges"]).to_bytes(2, "little", signed=False))
        for left, right in record["edges"]:
            digest.update(bytes((left, right)))
    return digest.hexdigest()


def verify_chart57_commuting_no_go(records):
    record = records[57]
    if (record["left"], record["right"]) != CHART57_SIGNATURES:
        raise AssertionError("chart-57 minimum pair changed")
    vertices = tuple(
        index for index in range(112) if (record["common_mask"] >> index) & 1
    )
    commuting_edges = tuple(
        edge
        for edge in record["edges"]
        if commuting(escape.DIRECTIONS[edge[0]], escape.DIRECTIONS[edge[1]])
    )
    component_sets, _ = components(vertices, commuting_edges)
    isolated = escape.DIRECTION_INDEX[CHART57_ISOLATED_DIRECTION]
    if (
        len(vertices),
        len(record["edges"]),
        len(commuting_edges),
        tuple(sorted(map(len, component_sets))),
    ) != (9, 26, 24, (1, 8)):
        raise AssertionError("chart-57 commuting-only component census changed")
    if (isolated,) not in component_sets:
        raise AssertionError("chart-57 isolated commuting root changed")


def full_audit(records):
    vertex_histogram = dict(sorted(Counter(r["vertices"] for r in records).items()))
    candidate_histogram = dict(
        sorted(Counter(r["candidate_edges"] for r in records).items())
    )
    joint_histogram = dict(
        sorted(Counter(r["joint_edges"] for r in records).items())
    )
    minimum_joint_edges = min(r["joint_edges"] for r in records)
    minimum_vertex_degree = min(r["minimum_degree"] for r in records)
    maximum_vertex_degree = max(r["maximum_degree"] for r in records)
    digest = semantic_digest(records)

    if vertex_histogram != EXPECTED_VERTEX_HISTOGRAM:
        raise AssertionError("vertex histogram changed")
    if candidate_histogram != EXPECTED_CANDIDATE_EDGE_HISTOGRAM:
        raise AssertionError("candidate-edge histogram changed")
    if joint_histogram != EXPECTED_JOINT_EDGE_HISTOGRAM:
        raise AssertionError("joint-edge histogram changed")
    if minimum_joint_edges != EXPECTED_MINIMUM_JOINT_EDGES:
        raise AssertionError("minimum joint-edge count changed")
    if minimum_vertex_degree != EXPECTED_MINIMUM_VERTEX_DEGREE:
        raise AssertionError("minimum vertex degree changed")
    if maximum_vertex_degree != EXPECTED_MAXIMUM_VERTEX_DEGREE:
        raise AssertionError("maximum vertex degree changed")
    if digest != EXPECTED_SEMANTIC_DIGEST:
        raise AssertionError(f"semantic digest changed: {digest}")
    verify_chart57_commuting_no_go(records)

    print("VERTEX_HISTOGRAM", vertex_histogram)
    print("CANDIDATE_EDGE_HISTOGRAM", candidate_histogram)
    print("JOINT_EDGE_HISTOGRAM", joint_histogram)
    print("MIN_JOINT_EDGES", minimum_joint_edges)
    print("MIN_VERTEX_DEGREE", minimum_vertex_degree)
    print("MAX_VERTEX_DEGREE", maximum_vertex_degree)
    print("SEMANTIC_DIGEST", digest)
    print("PASS chart 57 commuting-only graph has components 8+1")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--workers", type=int, default=4)
    parser.add_argument("--limit", type=int, default=EXPECTED_CHARTS)
    args = parser.parse_args()
    if not 1 <= args.limit <= EXPECTED_CHARTS:
        raise ValueError("--limit must lie in 1..178")
    if not 1 <= args.workers <= 4:
        raise ValueError("--workers must lie in 1..4")

    records = []
    with ProcessPoolExecutor(max_workers=args.workers) as executor:
        futures = {
            executor.submit(audit_chart, chart): chart
            for chart in range(args.limit)
        }
        for future in as_completed(futures):
            records.append(future.result())
    records.sort(key=lambda row: row["chart"])

    print("PASS connected exact ordered-root graphs on", len(records), "charts")
    if args.limit == EXPECTED_CHARTS:
        full_audit(records)
    else:
        print("SCOPE smoke prefix only; full histogram and digest pins not applied")
    print("CAVEAT stored point pairs are not a parent-cell coverage theorem")


if __name__ == "__main__":
    main()
