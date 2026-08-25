#!/usr/bin/env python3
"""Exact boxwise wall-component coverage on a parent-safe source staircase."""

from __future__ import annotations

from collections import Counter
from fractions import Fraction
from hashlib import sha256
from itertools import product
from pathlib import Path
import json
import sys


HERE = Path(__file__).resolve().parent
DATA = HERE / "data"
OUTPUT = DATA / "DIAG3_PAIR_SOURCE_STAIRCASE_COVERAGE_0_152.json"
FORMAT = "diag3-pair-source-staircase-component-coverage-v1"
STATUS = "EXACT_SOURCE_STAIRCASE_BOXWISE_WALL_COMPONENT_COVERAGE"
SOURCE_CHART = 0
TARGET_CHART = 152
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
import diag3_pair_source_cube_feasibility_core as cube  # noqa: E402
import verify_diag3_pair_global_parent_face_gate as gate  # noqa: E402


def interval_text(starts, ends):
    return [
        f"{cube.fraction_text(start)}..{cube.fraction_text(end)}"
        for start, end in zip(starts, ends)
    ]


def box_volume(starts, ends):
    answer = Fraction(1)
    for start, end in zip(starts, ends):
        answer *= end - start
    return answer


def semantic_update_polynomial(digest, polynomial):
    digest.update(repr(cube.canonical_integer(polynomial)).encode("ascii"))


def build_box(name, starts, ends, source, target, parents, parent_digest, candidates, polynomials, progress):
    vertices = tuple(product((Fraction(0), Fraction(1)), repeat=3))
    parent_degrees = Counter()
    minimum = None
    minimum_label = None
    for label, target_sign, polynomial, _terms in parents:
        restricted = cube.restrict_cube(polynomial, source, target, starts, ends)
        degrees = tuple(max(index[axis] for index in restricted) for axis in range(3))
        parent_degrees[degrees] += 1
        if any(degree > 1 for degree in degrees):
            raise AssertionError(f"{name} parent bracket {label} is not trilinear")
        signed = tuple(
            target_sign * cube.evaluate_trivariate(restricted, vertex)
            for vertex in vertices
        )
        if min(signed) <= 0:
            raise AssertionError(f"{name} parent bracket {label} fails at a box vertex")
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
    fully_triquadratic = []
    fully_triquadratic_polynomials = {}
    maximum_visited = 0
    classification_semantic = sha256(
        b"diag3-source-staircase-box-classification-v1\0" + name.encode("ascii") + b"\0"
    )
    for value in (*starts, *ends):
        classification_semantic.update(cube.fraction_text(value).encode("ascii") + b"\0")

    for offset, factor_id in enumerate(candidates, start=1):
        restricted = cube.restrict_cube(polynomials[factor_id], source, target, starts, ends)
        if not restricted:
            raise AssertionError(f"{name} factor {factor_id} restricts identically to zero")
        degrees = tuple(max(index[axis] for index in restricted) for axis in range(3))
        degree_census[degrees] += 1
        if degrees == (0, 0, 0):
            status, depth, visited = "EMPTY_CONSTANT", 0, 1
        else:
            status, depth, visited = cube.classify_bernstein(*cube.bernstein_control(restricted))
        status_census[status] += 1
        depth_census[status, depth] += 1
        maximum_visited = max(maximum_visited, visited)
        if status == "NONEMPTY_CORNER":
            occurring.append(factor_id)
            occurring_degrees[degrees] += 1
            if min(degrees) <= 1:
                graph_type.append(factor_id)
            else:
                fully_triquadratic.append(factor_id)
                fully_triquadratic_polynomials[factor_id] = restricted
        elif status.startswith("EMPTY_"):
            zero_free.append(factor_id)
        else:
            unresolved.append(factor_id)
        classification_semantic.update(factor_id.to_bytes(4, "little"))
        classification_semantic.update(bytes(degrees))
        classification_semantic.update(depth.to_bytes(2, "little"))
        classification_semantic.update(visited.to_bytes(8, "little"))
        classification_semantic.update(status.encode("ascii") + b"\0")
        semantic_update_polynomial(classification_semantic, restricted)
        if progress and offset % 4000 == 0:
            print(f"{name}: classified {offset}/{len(candidates)} wall restrictions", flush=True)
    if unresolved:
        raise AssertionError(f"{name} unresolved wall restrictions: {unresolved}")

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
    for factor_id in fully_triquadratic:
        polynomial = fully_triquadratic_polynomials[factor_id]
        selected = None
        total_visited = 0
        critical_semantic.update(factor_id.to_bytes(4, "little"))
        for axes in CRITICAL_AXIS_PAIRS:
            system = (polynomial, *(cube.derivative(polynomial, axis) for axis in axes))
            empty, depth, visited = cube.exclude_critical_system(system)
            total_visited += visited
            critical_maximum_visited = max(critical_maximum_visited, visited)
            attempt_result_census["EMPTY" if empty else "UNRESOLVED"] += 1
            critical_semantic.update(bytes((*axes, empty, depth)))
            critical_semantic.update(visited.to_bytes(8, "little"))
            for equation in system:
                semantic_update_polynomial(critical_semantic, equation)
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
    if critical_unresolved:
        raise AssertionError(f"{name} unresolved adaptive critical systems: {critical_unresolved}")

    return {
        "box_id": name,
        "block_parameter_intervals": interval_text(starts, ends),
        "exact_volume": cube.fraction_text(box_volume(starts, ends)),
        "parent_cube": {
            "parent_brackets": len(parents),
            "parent_polynomial_digest": parent_digest,
            "restriction_tridegree_census": {
                ",".join(map(str, degrees)): count
                for degrees, count in sorted(parent_degrees.items())
            },
            "strict_vertices": len(vertices),
            "minimum_signed_vertex_margin": cube.fraction_text(minimum),
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
            "occurring_factor_ids_sha256": cube.id_digest(
                b"diag3-source-staircase-box-occurring-v1\0" + name.encode("ascii"), occurring
            ),
            "zero_free_factor_ids_sha256": cube.id_digest(
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
            "fully_triquadratic_occurring_walls": len(fully_triquadratic),
            "adaptive_critical_systems_proved_empty": len(fully_triquadratic),
            "adaptive_critical_systems_unresolved": len(critical_unresolved),
            "selected_derivative_axis_pair_census": dict(sorted(selected_axis_pair_census.items())),
            "critical_attempt_result_census": dict(sorted(attempt_result_census.items())),
            "selected_critical_depth_census": {
                str(depth): count for depth, count in sorted(critical_depth_census.items())
            },
            "maximum_subboxes_visited_for_one_critical_attempt": critical_maximum_visited,
            "maximum_total_subboxes_visited_for_one_factor": critical_maximum_total_visited,
            "graph_type_factor_ids_sha256": cube.id_digest(
                b"diag3-source-staircase-box-graph-v1\0" + name.encode("ascii"), graph_type
            ),
            "fully_triquadratic_factor_ids_sha256": cube.id_digest(
                b"diag3-source-staircase-box-triquadratic-v1\0" + name.encode("ascii"), fully_triquadratic
            ),
            "critical_semantic_sha256": critical_semantic.hexdigest(),
            "conclusion": "EVERY_OCCURRING_WALL_COMPONENT_MEETS_THIS_BOX_BOUNDARY",
        },
        "_occurring_ids": occurring,
        "_zero_free_ids": zero_free,
    }


def build_record(progress=False):
    _matrices, points, _packed, _states, _hamming, _multiplicity = transition.exact_inputs()
    source = points[SOURCE_CHART]
    target = points[TARGET_CHART]
    records = [json.loads(line) for line in bridge.safe.CATALOG.read_text().splitlines() if line]
    parents, parent_digest = gate.parent_polynomials(records[2599])
    candidates = gate.parse_candidates()
    _types, _terms, polynomials = labeled.factor_polynomials()

    box_records = []
    union_occurring = set()
    zero_free_on_all = set(candidates)
    total_volume = Fraction(0)
    for name, starts, ends in BOXES:
        record = build_box(
            name, starts, ends, source, target, parents, parent_digest,
            candidates, polynomials, progress,
        )
        union_occurring.update(record.pop("_occurring_ids"))
        zero_free_on_all.intersection_update(record.pop("_zero_free_ids"))
        total_volume += box_volume(starts, ends)
        box_records.append(record)
        if progress:
            print(
                f"{name}: {record['wall_feasibility']['occurring_walls']} occurring; "
                f"{record['wall_component_coverage']['adaptive_critical_systems_proved_empty']} "
                "adaptive critical systems empty",
                flush=True,
            )

    union_occurring = sorted(union_occurring)
    zero_free_on_all = sorted(zero_free_on_all)
    if set(union_occurring) & set(zero_free_on_all):
        raise AssertionError("staircase occurring and globally zero-free ID sets overlap")
    if len(union_occurring) + len(zero_free_on_all) != len(candidates):
        raise AssertionError("staircase union accounting is incomplete")

    return {
        "format": FORMAT,
        "status": STATUS,
        "scope": {
            "parent_index": 2599,
            "source_chart": SOURCE_CHART,
            "target_chart": TARGET_CHART,
            "varying_column_blocks": [0, 1, 2],
            "source_boxes": len(BOXES),
            "exact_parameter_volume": cube.fraction_text(total_volume),
            "full_hybrid_cube_volume_fraction": cube.fraction_text(total_volume),
            "parent_parameter_coverage": "COMPLETE_ON_DECLARED_FIVE_BOX_SOURCE_STAIRCASE",
            "wall_feasibility_coverage": "COMPLETE_ON_EACH_SOURCE_BOX",
            "wall_component_coverage": "EVERY_OCCURRING_WALL_COMPONENT_MEETS_ITS_SOURCE_BOX_BOUNDARY",
            "source_skeleton_coverage": "UNION_OF_ALL_FIVE_BOX_BOUNDARIES",
            "global_parent_cell_coverage": "NOT_CLAIMED",
            "staircase_global_boundary_coverage": "NOT_CLAIMED",
        },
        "summary": {
            "boxes": len(BOXES),
            "box_factor_restrictions_replayed": len(BOXES) * len(candidates),
            "parent_bracket_box_restrictions_replayed": len(BOXES) * len(parents),
            "strict_parent_vertices_replayed": len(BOXES) * 8,
            "staircase_occurring_walls": len(union_occurring),
            "zero_free_on_all_staircase_boxes": len(zero_free_on_all),
            "unresolved_box_factor_restrictions": 0,
            "staircase_occurring_factor_ids_sha256": cube.id_digest(
                b"diag3-source-staircase-union-occurring-v1", union_occurring
            ),
            "staircase_zero_free_factor_ids_sha256": cube.id_digest(
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
