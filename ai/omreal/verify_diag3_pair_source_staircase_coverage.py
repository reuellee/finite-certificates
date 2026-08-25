#!/usr/bin/env python3
"""Independent hostile replay of the chart-0/chart-152 source staircase."""

from __future__ import annotations

from collections import Counter
from copy import deepcopy
from fractions import Fraction
from hashlib import sha256
from itertools import product
from pathlib import Path
import json
import sys


HERE = Path(__file__).resolve().parent
CERTIFICATE = HERE / "data" / "DIAG3_PAIR_SOURCE_STAIRCASE_COVERAGE_0_152.json"
BOXES = (
    ("x0", (Fraction(0), Fraction(0), Fraction(0)), (Fraction(1, 8), Fraction(1), Fraction(1, 64))),
    ("x1", (Fraction(1, 8), Fraction(0), Fraction(0)), (Fraction(1, 4), Fraction(1), Fraction(5, 16))),
    ("x2", (Fraction(1, 4), Fraction(0), Fraction(0)), (Fraction(3, 8), Fraction(1), Fraction(5, 8))),
    ("x3", (Fraction(3, 8), Fraction(0), Fraction(0)), (Fraction(1, 2), Fraction(1), Fraction(7, 8))),
    ("x4", (Fraction(1, 2), Fraction(0), Fraction(0)), (Fraction(1), Fraction(1), Fraction(1))),
)
CRITICAL_AXIS_PAIRS = ((1, 2), (0, 2), (0, 1))

sys.path.insert(0, str(HERE))
import DIAG2_PIVOT_LABELED_PAIR_ORBITS_VERIFY as labeled  # noqa: E402
import diag3_pair_parent_source_block_bridge_core as bridge  # noqa: E402
import diag3_pair_parent_source_transition_core as transition  # noqa: E402
import verify_diag3_pair_global_parent_face_gate as gate  # noqa: E402
import verify_diag3_pair_source_block_cube_feasibility as base  # noqa: E402


def volume(starts, ends):
    answer = Fraction(1)
    for start, end in zip(starts, ends):
        answer *= end - start
    return answer


def semantic_polynomial(digest, polynomial):
    digest.update(repr(base.normalized_integer(polynomial)).encode("ascii"))


def rebuild_box(name, starts, ends, source, target, parents, parent_digest, candidates, polynomials):
    vertices = tuple(product((Fraction(0), Fraction(1)), repeat=3))
    parent_degrees = Counter()
    minimum = None
    minimum_label = None
    for label, target_sign, polynomial, _terms in parents:
        restricted = base.pullback(polynomial, source, target, starts, ends)
        degrees = tuple(max(index[axis] for index in restricted) for axis in range(3))
        parent_degrees[degrees] += 1
        assert all(degree <= 1 for degree in degrees)
        signed = tuple(target_sign * base.value_at(restricted, vertex) for vertex in vertices)
        assert min(signed) > 0
        if minimum is None or min(signed) < minimum:
            minimum = min(signed)
            minimum_label = label

    degree_census = Counter()
    status_census = Counter()
    depth_census = Counter()
    occurring_degrees = Counter()
    occurring = []
    zero_free = []
    unresolved = []
    graph_type = []
    hard = []
    hard_polynomials = {}
    maximum_visited = 0
    classification_semantic = sha256(
        b"diag3-source-staircase-box-classification-v1\0" + name.encode("ascii") + b"\0"
    )
    for value in (*starts, *ends):
        classification_semantic.update(base.fraction_text(value).encode("ascii") + b"\0")
    for factor_id in candidates:
        restricted = base.pullback(polynomials[factor_id], source, target, starts, ends)
        assert restricted
        degrees = tuple(max(index[axis] for index in restricted) for axis in range(3))
        degree_census[degrees] += 1
        if degrees == (0, 0, 0):
            status, depth, visited = "EMPTY_CONSTANT", 0, 1
        else:
            status, depth, visited = base.decide(*base.controls(restricted))
        status_census[status] += 1
        depth_census[status, depth] += 1
        maximum_visited = max(maximum_visited, visited)
        if status == "NONEMPTY_CORNER":
            occurring.append(factor_id)
            occurring_degrees[degrees] += 1
            if min(degrees) <= 1:
                graph_type.append(factor_id)
            else:
                hard.append(factor_id)
                hard_polynomials[factor_id] = restricted
        elif status.startswith("EMPTY_"):
            zero_free.append(factor_id)
        else:
            unresolved.append(factor_id)
        classification_semantic.update(factor_id.to_bytes(4, "little"))
        classification_semantic.update(bytes(degrees))
        classification_semantic.update(depth.to_bytes(2, "little"))
        classification_semantic.update(visited.to_bytes(8, "little"))
        classification_semantic.update(status.encode("ascii") + b"\0")
        semantic_polynomial(classification_semantic, restricted)
    assert not unresolved

    critical_depth_census = Counter()
    selected_axis_pair_census = Counter()
    attempt_result_census = Counter()
    critical_maximum_visited = 0
    critical_maximum_total_visited = 0
    critical_unresolved = []
    critical_semantic = sha256(
        b"diag3-source-staircase-adaptive-critical-system-v1\0"
        + name.encode("ascii")
        + b"\0"
    )
    for factor_id in hard:
        polynomial = hard_polynomials[factor_id]
        selected = None
        total_visited = 0
        critical_semantic.update(factor_id.to_bytes(4, "little"))
        for axes in CRITICAL_AXIS_PAIRS:
            system = (polynomial, *(base.derivative(polynomial, axis) for axis in axes))
            empty, depth, visited = base.critical_system_empty(system)
            total_visited += visited
            critical_maximum_visited = max(critical_maximum_visited, visited)
            attempt_result_census["EMPTY" if empty else "UNRESOLVED"] += 1
            critical_semantic.update(bytes((*axes, empty, depth)))
            critical_semantic.update(visited.to_bytes(8, "little"))
            for equation in system:
                semantic_polynomial(critical_semantic, equation)
            if empty:
                selected = (axes, depth)
                break
        critical_maximum_total_visited = max(critical_maximum_total_visited, total_visited)
        if selected is None:
            critical_unresolved.append(factor_id)
        else:
            axes, depth = selected
            selected_axis_pair_census[",".join(map(str, axes))] += 1
            critical_depth_census[depth] += 1
    assert not critical_unresolved

    return {
        "box_id": name,
        "block_parameter_intervals": [
            f"{base.fraction_text(start)}..{base.fraction_text(end)}"
            for start, end in zip(starts, ends)
        ],
        "exact_volume": base.fraction_text(volume(starts, ends)),
        "parent_cube": {
            "parent_brackets": len(parents),
            "parent_polynomial_digest": parent_digest,
            "restriction_tridegree_census": {
                ",".join(map(str, degrees)): count
                for degrees, count in sorted(parent_degrees.items())
            },
            "strict_vertices": len(vertices),
            "minimum_signed_vertex_margin": base.fraction_text(minimum),
            "minimum_margin_bracket": minimum_label,
            "coverage_argument": "trilinear Bernstein coefficients are the eight positive vertex values",
        },
        "wall_feasibility": {
            "candidate_factors": len(candidates),
            "restriction_tridegree_census": {
                ",".join(map(str, degrees)): count
                for degrees, count in sorted(degree_census.items())
            },
            "status_census": dict(sorted(status_census.items())),
            "classification_depth_census": {
                f"{status}:{depth}": count
                for (status, depth), count in sorted(depth_census.items())
            },
            "occurring_walls": len(occurring),
            "zero_free_walls": len(zero_free),
            "unresolved_walls": len(unresolved),
            "maximum_subboxes_visited_for_one_wall": maximum_visited,
            "occurring_factor_ids_sha256": base.digest_ids(
                b"diag3-source-staircase-box-occurring-v1\0" + name.encode("ascii"), occurring
            ),
            "zero_free_factor_ids_sha256": base.digest_ids(
                b"diag3-source-staircase-box-zero-free-v1\0" + name.encode("ascii"), zero_free
            ),
            "classification_semantic_sha256": classification_semantic.hexdigest(),
        },
        "wall_component_coverage": {
            "occurring_tridegree_census": {
                ",".join(map(str, degrees)): count
                for degrees, count in sorted(occurring_degrees.items())
            },
            "graph_type_occurring_walls": len(graph_type),
            "fully_triquadratic_occurring_walls": len(hard),
            "adaptive_critical_systems_proved_empty": len(hard),
            "adaptive_critical_systems_unresolved": len(critical_unresolved),
            "selected_derivative_axis_pair_census": dict(sorted(selected_axis_pair_census.items())),
            "critical_attempt_result_census": dict(sorted(attempt_result_census.items())),
            "selected_critical_depth_census": {
                str(depth): count for depth, count in sorted(critical_depth_census.items())
            },
            "maximum_subboxes_visited_for_one_critical_attempt": critical_maximum_visited,
            "maximum_total_subboxes_visited_for_one_factor": critical_maximum_total_visited,
            "graph_type_factor_ids_sha256": base.digest_ids(
                b"diag3-source-staircase-box-graph-v1\0" + name.encode("ascii"), graph_type
            ),
            "fully_triquadratic_factor_ids_sha256": base.digest_ids(
                b"diag3-source-staircase-box-triquadratic-v1\0" + name.encode("ascii"), hard
            ),
            "critical_semantic_sha256": critical_semantic.hexdigest(),
            "conclusion": "EVERY_OCCURRING_WALL_COMPONENT_MEETS_THIS_BOX_BOUNDARY",
        },
        "_occurring": occurring,
        "_zero_free": zero_free,
    }


def reconstruct():
    _matrices, points, _packed, _states, _hamming, _multiplicity = transition.exact_inputs()
    source = points[0]
    target = points[152]
    rows = [json.loads(line) for line in bridge.safe.CATALOG.read_text().splitlines() if line]
    parents, parent_digest = gate.parent_polynomials(rows[2599])
    candidates = gate.parse_candidates()
    _types, _terms, polynomials = labeled.factor_polynomials()
    box_records = []
    union_occurring = set()
    zero_free_on_all = set(candidates)
    total_volume = Fraction(0)
    for name, starts, ends in BOXES:
        record = rebuild_box(
            name, starts, ends, source, target, parents, parent_digest, candidates, polynomials
        )
        union_occurring.update(record.pop("_occurring"))
        zero_free_on_all.intersection_update(record.pop("_zero_free"))
        total_volume += volume(starts, ends)
        box_records.append(record)
    union_occurring = sorted(union_occurring)
    zero_free_on_all = sorted(zero_free_on_all)
    assert not set(union_occurring) & set(zero_free_on_all)
    assert len(union_occurring) + len(zero_free_on_all) == len(candidates)
    return {
        "format": "diag3-pair-source-staircase-component-coverage-v1",
        "status": "EXACT_SOURCE_STAIRCASE_BOXWISE_WALL_COMPONENT_COVERAGE",
        "scope": {
            "parent_index": 2599,
            "source_chart": 0,
            "target_chart": 152,
            "varying_column_blocks": [0, 1, 2],
            "source_boxes": 5,
            "exact_parameter_volume": base.fraction_text(total_volume),
            "full_hybrid_cube_volume_fraction": base.fraction_text(total_volume),
            "parent_parameter_coverage": "COMPLETE_ON_DECLARED_FIVE_BOX_SOURCE_STAIRCASE",
            "wall_feasibility_coverage": "COMPLETE_ON_EACH_SOURCE_BOX",
            "wall_component_coverage": "EVERY_OCCURRING_WALL_COMPONENT_MEETS_ITS_SOURCE_BOX_BOUNDARY",
            "source_skeleton_coverage": "UNION_OF_ALL_FIVE_BOX_BOUNDARIES",
            "global_parent_cell_coverage": "NOT_CLAIMED",
            "staircase_global_boundary_coverage": "NOT_CLAIMED",
        },
        "summary": {
            "boxes": 5,
            "box_factor_restrictions_replayed": 5 * len(candidates),
            "parent_bracket_box_restrictions_replayed": 5 * len(parents),
            "strict_parent_vertices_replayed": 40,
            "staircase_occurring_walls": len(union_occurring),
            "zero_free_on_all_staircase_boxes": len(zero_free_on_all),
            "unresolved_box_factor_restrictions": 0,
            "staircase_occurring_factor_ids_sha256": base.digest_ids(
                b"diag3-source-staircase-union-occurring-v1", union_occurring
            ),
            "staircase_zero_free_factor_ids_sha256": base.digest_ids(
                b"diag3-source-staircase-all-zero-free-v1", zero_free_on_all
            ),
            "boxwise_component_coverage": "PROVED",
            "global_missed_component_theorem": "OPEN",
        },
        "boxes": box_records,
        "proof": {
            "graph_type_argument": "A restriction affine in one parameter either contains a full boundary-meeting fiber or projects locally as a graph, excluding a compact interior component.",
            "adaptive_critical_argument": "A compact component has an extremum in every coordinate; for any chosen omitted coordinate it contains a zero of p and the derivatives in the other two coordinates. One exactly empty chosen system therefore excludes compact components.",
            "staircase_skeleton_argument": "Each boxwise wall component meets the union of the five box boundaries; internal seams remain part of this declared source skeleton.",
        },
        "theorem_effect": "Exact parent residence, complete wall feasibility, and boxwise wall-component boundary coverage on a 373/512-volume source staircase; global pair coverage and the independent triple obligation remain open; honest 9DVL score remains 2/9.",
    }


def validate(candidate, expected):
    assert candidate == expected
    assert candidate["scope"]["exact_parameter_volume"] == "373/512"
    assert candidate["summary"]["box_factor_restrictions_replayed"] == 89_120
    assert candidate["summary"]["parent_bracket_box_restrictions_replayed"] == 350
    assert candidate["summary"]["strict_parent_vertices_replayed"] == 40
    assert candidate["summary"]["unresolved_box_factor_restrictions"] == 0
    assert candidate["summary"]["staircase_occurring_walls"] + candidate["summary"]["zero_free_on_all_staircase_boxes"] == 17_824
    assert [box["wall_feasibility"]["occurring_walls"] for box in candidate["boxes"]] == [1_546, 2_069, 2_770, 3_300, 4_450]
    assert [box["wall_component_coverage"]["graph_type_occurring_walls"] for box in candidate["boxes"]] == [1_317, 1_780, 2_407, 2_883, 3_889]
    assert [box["wall_component_coverage"]["fully_triquadratic_occurring_walls"] for box in candidate["boxes"]] == [229, 289, 363, 417, 561]
    assert candidate["boxes"][3]["wall_component_coverage"]["selected_derivative_axis_pair_census"] == {"0,2": 1, "1,2": 416}
    assert candidate["boxes"][3]["wall_component_coverage"]["critical_attempt_result_census"] == {"EMPTY": 417, "UNRESOLVED": 1}
    assert candidate["scope"]["global_parent_cell_coverage"] == "NOT_CLAIMED"
    assert candidate["scope"]["staircase_global_boundary_coverage"] == "NOT_CLAIMED"


def main():
    stored = json.loads(CERTIFICATE.read_text())
    expected = reconstruct()
    validate(stored, expected)
    mutations = []
    for path, value in (
        (("format",), "corrupted"),
        (("scope", "exact_parameter_volume"), "1"),
        (("scope", "global_parent_cell_coverage"), "COMPLETE"),
        (("scope", "staircase_global_boundary_coverage"), "COMPLETE"),
        (("summary", "box_factor_restrictions_replayed"), 89_119),
        (("summary", "staircase_occurring_walls"), 17_824),
        (("summary", "staircase_occurring_factor_ids_sha256"), "0" * 64),
        (("boxes", 0, "block_parameter_intervals"), ["0..1", "0..1", "0..1"]),
        (("boxes", 1, "parent_cube", "strict_vertices"), 7),
        (("boxes", 2, "wall_feasibility", "occurring_walls"), 2_771),
        (("boxes", 3, "wall_component_coverage", "selected_derivative_axis_pair_census"), {"1,2": 417}),
        (("boxes", 3, "wall_component_coverage", "adaptive_critical_systems_unresolved"), 1),
        (("boxes", 4, "wall_component_coverage", "critical_semantic_sha256"), "0" * 64),
        (("boxes", 4, "wall_component_coverage", "conclusion"), "COMPLETE"),
    ):
        mutation = deepcopy(stored)
        target = mutation
        for key in path[:-1]:
            target = target[key]
        target[path[-1]] = value
        mutations.append(mutation)
    rejected = 0
    for mutation in mutations:
        try:
            validate(mutation, expected)
        except AssertionError:
            rejected += 1
    assert rejected == len(mutations)
    print("PASS five exact parent-resident source boxes cover parameter volume 373/512")
    print("PASS 89,120 box-factor restrictions decided with zero unresolved")
    print("PASS adaptive critical systems cover 1,859 fully triquadratic box occurrences")
    print("PASS every occurring component meets its source-box boundary")
    print(f"PASS {rejected}/{len(mutations)} hostile corruptions rejected")
    print("SCOPE boxwise source-skeleton coverage; global parent missed-component theorem open; honest 9DVL 2/9")


if __name__ == "__main__":
    main()
