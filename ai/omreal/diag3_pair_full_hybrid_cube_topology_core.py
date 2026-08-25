#!/usr/bin/env python3
"""Exact ambient zero-set topology on the chart-0/chart-152 hybrid cube."""

from __future__ import annotations

from collections import Counter
from fractions import Fraction
from hashlib import sha256
from itertools import product
from pathlib import Path
import json
import sys


HERE = Path(__file__).resolve().parent
OUTPUT = HERE / "data" / "DIAG3_PAIR_FULL_HYBRID_CUBE_TOPOLOGY_0_152.json"
FORMAT = "diag3-pair-full-hybrid-cube-topology-v1"
STATUS = "EXACT_AMBIENT_HYBRID_CUBE_WALL_COMPONENT_COVERAGE"
SOURCE_CHART = 0
TARGET_CHART = 152
STARTS = (Fraction(0), Fraction(0), Fraction(0))
ENDS = (Fraction(1), Fraction(1), Fraction(1))
CRITICAL_AXIS_PAIRS = ((1, 2), (0, 2), (0, 1))

sys.path.insert(0, str(HERE))
import DIAG2_PIVOT_LABELED_PAIR_ORBITS_VERIFY as labeled  # noqa: E402
import diag3_pair_parent_source_block_bridge_core as bridge  # noqa: E402
import diag3_pair_parent_source_transition_core as transition  # noqa: E402
import diag3_pair_source_cube_feasibility_core as cube  # noqa: E402
import verify_diag3_pair_global_parent_face_gate as gate  # noqa: E402


def semantic_polynomial(digest, polynomial):
    digest.update(repr(cube.canonical_integer(polynomial)).encode("ascii"))


def build_record(progress=False):
    _matrices, points, _packed, _states, _hamming, _multiplicity = transition.exact_inputs()
    source, target = points[SOURCE_CHART], points[TARGET_CHART]
    rows = [json.loads(line) for line in bridge.safe.CATALOG.read_text().splitlines() if line]
    parents, parent_digest = gate.parent_polynomials(rows[2599])
    vertices = tuple(product((Fraction(0), Fraction(1)), repeat=3))
    parent_failures = []
    parent_degrees = Counter()
    for label, target_sign, polynomial, _terms in parents:
        restricted = cube.restrict_cube(polynomial, source, target, STARTS, ENDS)
        degrees = tuple(max(index[axis] for index in restricted) for axis in range(3))
        parent_degrees[degrees] += 1
        if any(degree > 1 for degree in degrees):
            raise AssertionError(f"parent bracket {label} is not trilinear")
        for vertex in vertices:
            signed = target_sign * cube.evaluate_trivariate(restricted, vertex)
            if signed <= 0:
                parent_failures.append(
                    {
                        "block_vertex": list(map(int, vertex)),
                        "bracket": label,
                        "signed_value": cube.fraction_text(signed),
                    }
                )

    candidates = gate.parse_candidates()
    _types, _terms, polynomials = labeled.factor_polynomials()
    degree_census = Counter()
    occurring_degree_census = Counter()
    status_census = Counter()
    depth_census = Counter()
    occurring = []
    zero_free = []
    unresolved = []
    graph_type = []
    triquadratic = []
    triquadratic_polynomials = {}
    maximum_visited = 0
    classification_semantic = sha256(b"diag3-full-hybrid-cube-classification-v1\0")
    for offset, factor_id in enumerate(candidates, start=1):
        restricted = cube.restrict_cube(
            polynomials[factor_id], source, target, STARTS, ENDS
        )
        if not restricted:
            raise AssertionError(f"factor {factor_id} restricts identically to zero")
        degrees = tuple(max(index[axis] for index in restricted) for axis in range(3))
        degree_census[degrees] += 1
        if degrees == (0, 0, 0):
            status, depth, visited = "EMPTY_CONSTANT", 0, 1
        else:
            status, depth, visited = cube.classify_bernstein(
                *cube.bernstein_control(restricted)
            )
        status_census[status] += 1
        depth_census[status, depth] += 1
        maximum_visited = max(maximum_visited, visited)
        if status == "NONEMPTY_CORNER":
            occurring.append(factor_id)
            occurring_degree_census[degrees] += 1
            if min(degrees) <= 1:
                graph_type.append(factor_id)
            else:
                triquadratic.append(factor_id)
                triquadratic_polynomials[factor_id] = restricted
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
        if progress and offset % 4000 == 0:
            print(f"classified {offset}/{len(candidates)} full-cube walls", flush=True)
    if unresolved:
        raise AssertionError(f"unresolved full-cube restrictions: {unresolved}")

    selected_pair_census = Counter()
    attempt_result_census = Counter()
    selected_depth_census = Counter()
    critical_unresolved = []
    maximum_attempt_visited = 0
    maximum_total_visited = 0
    critical_semantic = sha256(b"diag3-full-hybrid-cube-adaptive-critical-v1\0")
    for factor_id in triquadratic:
        polynomial = triquadratic_polynomials[factor_id]
        selected = None
        total_visited = 0
        critical_semantic.update(factor_id.to_bytes(4, "little"))
        for axes in CRITICAL_AXIS_PAIRS:
            system = (
                polynomial,
                *(cube.derivative(polynomial, axis) for axis in axes),
            )
            empty, depth, visited = cube.exclude_critical_system(system)
            total_visited += visited
            maximum_attempt_visited = max(maximum_attempt_visited, visited)
            attempt_result_census["EMPTY" if empty else "UNRESOLVED"] += 1
            critical_semantic.update(bytes((*axes, empty, depth)))
            critical_semantic.update(visited.to_bytes(8, "little"))
            for equation in system:
                semantic_polynomial(critical_semantic, equation)
            if empty:
                selected = axes, depth
                break
        maximum_total_visited = max(maximum_total_visited, total_visited)
        if selected is None:
            critical_unresolved.append(factor_id)
        else:
            axes, depth = selected
            selected_pair_census[",".join(map(str, axes))] += 1
            selected_depth_census[depth] += 1
    if critical_unresolved:
        raise AssertionError(f"unresolved full-cube critical systems: {critical_unresolved}")

    return {
        "format": FORMAT,
        "status": STATUS,
        "scope": {
            "parent_index": 2599,
            "source_chart": SOURCE_CHART,
            "target_chart": TARGET_CHART,
            "varying_column_blocks": [0, 1, 2],
            "block_parameter_intervals": ["0..1", "0..1", "0..1"],
            "ambient_hybrid_cube_coverage": "COMPLETE",
            "parent_residence": "FALSE_AT_TWO_VERTICES_AND_NOT_REQUIRED_FOR_THIS_AMBIENT_TOPOLOGY_CLAIM",
            "wall_component_coverage": "EVERY_OCCURRING_RESTRICTED_WALL_COMPONENT_MEETS_FULL_HYBRID_CUBE_BOUNDARY",
            "global_parent_cell_coverage": "NOT_CLAIMED",
        },
        "parent_residence_no_go": {
            "parent_brackets": len(parents),
            "parent_polynomial_digest": parent_digest,
            "restriction_tridegree_census": {
                ",".join(map(str, degrees)): count
                for degrees, count in sorted(parent_degrees.items())
            },
            "tested_signed_vertex_values": len(parents) * len(vertices),
            "parent_safe_vertices": len(vertices) - len({tuple(row["block_vertex"]) for row in parent_failures}),
            "failed_vertices": len({tuple(row["block_vertex"]) for row in parent_failures}),
            "failed_signed_vertex_values": parent_failures,
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
                b"diag3-full-hybrid-cube-occurring-v1", occurring
            ),
            "zero_free_factor_ids_sha256": cube.id_digest(
                b"diag3-full-hybrid-cube-zero-free-v1", zero_free
            ),
            "classification_semantic_sha256": classification_semantic.hexdigest(),
        },
        "wall_component_coverage": {
            "occurring_tridegree_census": {
                ",".join(map(str, degrees)): count
                for degrees, count in sorted(occurring_degree_census.items())
            },
            "graph_type_occurring_walls": len(graph_type),
            "fully_triquadratic_occurring_walls": len(triquadratic),
            "adaptive_critical_systems_proved_empty": len(triquadratic),
            "adaptive_critical_systems_unresolved": len(critical_unresolved),
            "selected_derivative_axis_pair_census": dict(sorted(selected_pair_census.items())),
            "critical_attempt_result_census": dict(sorted(attempt_result_census.items())),
            "selected_critical_depth_census": {
                str(depth): count for depth, count in sorted(selected_depth_census.items())
            },
            "maximum_subboxes_visited_for_one_critical_attempt": maximum_attempt_visited,
            "maximum_total_subboxes_visited_for_one_factor": maximum_total_visited,
            "graph_type_factor_ids_sha256": cube.id_digest(
                b"diag3-full-hybrid-cube-graph-v1", graph_type
            ),
            "fully_triquadratic_factor_ids_sha256": cube.id_digest(
                b"diag3-full-hybrid-cube-triquadratic-v1", triquadratic
            ),
            "critical_semantic_sha256": critical_semantic.hexdigest(),
            "conclusion": "EVERY_OCCURRING_RESTRICTED_WALL_COMPONENT_MEETS_FULL_HYBRID_CUBE_BOUNDARY",
        },
        "transfer": {
            "lemma": "For a closed semialgebraic subregion S of the hybrid cube, a component of Z intersect S that avoids boundary(S) would be a full-cube component avoiding the cube boundary; semialgebraic components are path connected.",
            "source_staircase_effect": "EVERY_RESTRICTED_WALL_COMPONENT_IN_ANY_PARENT_SAFE_SOURCE_STAIRCASE_MEETS_ITS_TRUE_OUTER_BOUNDARY",
            "internal_seams_required": False,
        },
        "theorem_effect": "Removes internal box seams from the source-staircase wall-component claim, but does not prove that every global row-2599 parent-cell wall component meets the source family; honest 9DVL score remains 2/9.",
    }
