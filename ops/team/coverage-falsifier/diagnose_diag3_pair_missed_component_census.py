#!/usr/bin/env python3
"""Exact bounded red-team census for row-2599 source-skeleton misses.

This does not attempt global CAD.  It replays two accepted exact source cubes,
then applies exact Sturm counts to the 40 retained source segments.  The result
is deliberately fail-closed: the 123 full-cube corner witnesses are *not*
promoted to parent-cell witnesses because their opposite signs occur only at
the two parent-infeasible cube vertices.
"""

from __future__ import annotations

from fractions import Fraction
from hashlib import sha256
import json
from pathlib import Path
import sys


HERE = Path(__file__).resolve()
REPO = HERE.parents[3]
OMREAL = REPO / "ai" / "omreal"
sys.path.insert(0, str(OMREAL))

import DIAG2_PIVOT_LABELED_PAIR_ORBITS_VERIFY as labeled  # noqa: E402
import DIAG9_GRAPH_verify_row2599_slice as sturm  # noqa: E402
import diag3_pair_parent_source_block_bridge_core as bridge  # noqa: E402
import diag3_pair_parent_source_transition_core as transition  # noqa: E402
import diag3_pair_source_cube_feasibility_core as half_cube  # noqa: E402
import verify_diag3_pair_fullsupport_safe_segment_walls as safe  # noqa: E402
import verify_diag3_pair_global_parent_face_gate as gate  # noqa: E402


COVER = OMREAL / "data" / "DIAG3_PAIR_FULLSUPPORT_SEGMENT_COVER.json"
EXPECTED = {
    "candidate_count": 17_824,
    "known_crossed_count": 10_844,
    "base_open_count": 6_980,
    "selected_edge_count": 40,
    "half_cube_occurring_count": 4_450,
    "half_cube_new_count": 0,
    "full_cube_new_corner_count": 123,
    "full_cube_new_corner_digest":
        "16a8aa0c7aa1c49452dfc2b3f557453619027196aa0344f73200e45b114f3eca",
    "strict_full_cube_vertex_masks": (0, 1, 2, 3, 5, 7),
    "unsafe_full_cube_vertex_masks": (4, 6),
}


def exact_value(polynomial, point):
    answer = Fraction(0)
    for exponent, coefficient in polynomial.items():
        term = Fraction(coefficient)
        for coordinate, power in zip(point, exponent, strict=True):
            term *= coordinate**power
        answer += term
    return answer


def digest_ids(domain: bytes, identifiers) -> str:
    state = sha256(domain + b"\0")
    for identifier in sorted(identifiers):
        state.update(int(identifier).to_bytes(4, "little"))
    return state.hexdigest()


def root_count_open(polynomial) -> int:
    coefficients = tuple(map(Fraction, polynomial))
    if not coefficients:
        raise AssertionError("identically zero retained-edge restriction")
    left = sturm.polynomial_value(coefficients, Fraction(0))
    right = sturm.polynomial_value(coefficients, Fraction(1))
    if left == 0 or right == 0:
        raise AssertionError("retained-edge endpoint is a residual zero")
    return sturm.root_count(coefficients, Fraction(0), Fraction(1))


def main():
    _matrices, points, _packed, states, _hamming, _multiplicity = (
        transition.exact_inputs()
    )
    candidates = tuple(gate.parse_candidates())
    _types, _terms, factors = labeled.factor_polynomials()
    cover = json.loads(COVER.read_text(encoding="utf-8"))
    selected = tuple(cover["source_bank"]["selected_edge_indices"])

    known = {
        factor_id
        for factor_id in candidates
        if any(states[left, factor_id] != states[right, factor_id]
               for left, right in safe.EDGES)
    }
    base_open = set(candidates) - known
    assert len(candidates) == EXPECTED["candidate_count"]
    assert len(known) == EXPECTED["known_crossed_count"]
    assert len(base_open) == EXPECTED["base_open_count"]
    assert len(selected) == EXPECTED["selected_edge_count"]

    records = [
        json.loads(line)
        for line in gate.CATALOG.read_text(encoding="utf-8").splitlines()
        if line
    ]
    parents, _parent_digest = gate.parent_polynomials(records[2599])
    source, target = points[0], points[152]
    full_vertices = tuple(
        bridge.hybrid_vertex(source, target, mask) for mask in range(8)
    )
    strict_masks = tuple(
        mask
        for mask, point in enumerate(full_vertices)
        if all(
            target_sign * exact_value(polynomial, point) > 0
            for _label, target_sign, polynomial, _terms in parents
        )
    )
    unsafe_masks = tuple(mask for mask in range(8) if mask not in strict_masks)
    assert strict_masks == EXPECTED["strict_full_cube_vertex_masks"]
    assert unsafe_masks == EXPECTED["unsafe_full_cube_vertex_masks"]

    full_cube_new = []
    for factor_id in sorted(base_open):
        signs = tuple(
            1 if (value := exact_value(factors[factor_id], point)) > 0
            else -1 if value < 0 else 0
            for point in full_vertices
        )
        if -1 in signs and 1 in signs:
            strict_signs = {signs[mask] for mask in strict_masks}
            if len(strict_signs) != 1 or 0 in strict_signs:
                raise AssertionError(
                    f"factor {factor_id} already changes sign at strict cube vertices"
                )
            strict_sign = next(iter(strict_signs))
            if any(
                signs[mask] not in (strict_sign, 0) for mask in strict_masks
            ):
                raise AssertionError("strict-vertex accounting failure")
            if not any(signs[mask] == -strict_sign for mask in unsafe_masks):
                raise AssertionError("opposite sign is not confined to unsafe vertices")
            full_cube_new.append(factor_id)

    assert len(full_cube_new) == EXPECTED["full_cube_new_corner_count"]
    full_digest = digest_ids(
        b"diag3-source-cube-walls-not-safe-segment-crossed-v1",
        full_cube_new,
    )
    assert full_digest == EXPECTED["full_cube_new_corner_digest"]

    retained_root_counts = {}
    for factor_id in full_cube_new:
        total = 0
        for edge_index in selected:
            left, right = safe.EDGES[edge_index]
            total += root_count_open(
                safe.segment_power(factors[factor_id], points[left], points[right])
            )
        retained_root_counts[factor_id] = total
    if any(retained_root_counts.values()):
        raise AssertionError("a full-cube candidate actually meets a retained edge")

    half_occurring = []
    half_unresolved = []
    for factor_id in candidates:
        restriction = half_cube.restrict_cube(
            factors[factor_id], source, target
        )
        status, _depth, _visited = half_cube.classify_bernstein(
            *half_cube.bernstein_control(restriction)
        )
        if status == "NONEMPTY_CORNER":
            half_occurring.append(factor_id)
        elif not status.startswith("EMPTY_"):
            half_unresolved.append(factor_id)
    half_new = sorted(set(half_occurring) - known)
    assert not half_unresolved
    assert len(half_occurring) == EXPECTED["half_cube_occurring_count"]
    assert len(half_new) == EXPECTED["half_cube_new_count"]

    print("PASS exact 17,824-factor / 105-edge source-bank reconstruction")
    print("PASS exact 4,450-wall strict-parent half-cube census; 0 new factors")
    print("PASS 123 oversized-cube corner factors absent from all 40 retained edges")
    print("PASS exact Sturm count 0 on all 123 x 40 retained closed segments")
    print("PASS opposite corner signs confined to parent-unsafe masks 4 and 6")
    print("FULL_CUBE_NEW_IDS_SHA256", full_digest)
    print(
        "SCOPE bounded null only: cube interiors and the global strict-parent "
        "cell remain unclassified; no missed component is proved"
    )


if __name__ == "__main__":
    main()
