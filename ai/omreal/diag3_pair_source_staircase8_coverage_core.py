#!/usr/bin/env python3
"""Exact feasibility and outer-boundary coverage on an eight-box staircase."""

from __future__ import annotations

from collections import Counter
from fractions import Fraction
from hashlib import sha256
from itertools import product
from pathlib import Path
import json
import sys


HERE = Path(__file__).resolve().parent
OUTPUT = HERE / "data" / "DIAG3_PAIR_SOURCE_STAIRCASE8_COVERAGE_0_152.json"
FORMAT = "diag3-pair-source-staircase8-coverage-v1"
STATUS = "EXACT_SOURCE_STAIRCASE8_OUTER_BOUNDARY_COVERAGE"
SOURCE_CHART = 0
TARGET_CHART = 152
HEIGHTS = (
    Fraction(9, 512),
    Fraction(103, 512),
    Fraction(379, 1024),
    Fraction(539, 1024),
    Fraction(343, 512),
    Fraction(823, 1024),
    Fraction(475, 512),
)
BOXES = tuple(
    (
        f"s{index:02d}",
        (Fraction(index, 16), Fraction(0), Fraction(0)),
        (Fraction(index + 1, 16), Fraction(1), height),
    )
    for index, height in enumerate(HEIGHTS)
) + (
    (
        "s07plus",
        (Fraction(7, 16), Fraction(0), Fraction(0)),
        (Fraction(1), Fraction(1), Fraction(1)),
    ),
)
OLD_STAIRCASE_VOLUME = Fraction(373, 512)
OLD_STAIRCASE_OCCURRING = 5_106
OLD_STEPS = (
    (Fraction(0), Fraction(1, 8), Fraction(1, 64)),
    (Fraction(1, 8), Fraction(1, 4), Fraction(5, 16)),
    (Fraction(1, 4), Fraction(3, 8), Fraction(5, 8)),
    (Fraction(3, 8), Fraction(1, 2), Fraction(7, 8)),
    (Fraction(1, 2), Fraction(1), Fraction(1)),
)

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


def staircase_height(boxes, coordinate):
    return max(
        ends[2]
        for _name, starts, ends in boxes
        if starts[0] <= coordinate <= ends[0]
    )


def old_staircase_is_contained():
    endpoints = sorted(
        {value for start, end, _height in OLD_STEPS for value in (start, end)}
        | {value for _name, starts, ends in BOXES for value in (starts[0], ends[0])}
    )
    for left, right in zip(endpoints, endpoints[1:]):
        midpoint = (left + right) / 2
        old_height = max(
            height for start, end, height in OLD_STEPS if start <= midpoint <= end
        )
        if staircase_height(BOXES, midpoint) < old_height:
            return False
    return True


def semantic_polynomial(digest, polynomial):
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
    occurring = []
    zero_free = []
    unresolved = []
    maximum_visited = 0
    semantic = sha256(
        b"diag3-source-staircase8-box-classification-v1\0" + name.encode("ascii") + b"\0"
    )
    for value in (*starts, *ends):
        semantic.update(cube.fraction_text(value).encode("ascii") + b"\0")
    for offset, factor_id in enumerate(candidates, start=1):
        restricted = cube.restrict_cube(
            polynomials[factor_id], source, target, starts, ends
        )
        if not restricted:
            raise AssertionError(f"{name} factor {factor_id} restricts identically to zero")
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
        elif status.startswith("EMPTY_"):
            zero_free.append(factor_id)
        else:
            unresolved.append(factor_id)
        semantic.update(factor_id.to_bytes(4, "little"))
        semantic.update(bytes(degrees))
        semantic.update(depth.to_bytes(2, "little"))
        semantic.update(visited.to_bytes(8, "little"))
        semantic.update(status.encode("ascii") + b"\0")
        semantic_polynomial(semantic, restricted)
        if progress and offset % 4000 == 0:
            print(f"{name}: classified {offset}/{len(candidates)} wall restrictions", flush=True)
    if unresolved:
        raise AssertionError(f"{name} unresolved wall restrictions: {unresolved}")
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
                b"diag3-source-staircase8-box-occurring-v1\0" + name.encode("ascii"),
                occurring,
            ),
            "zero_free_factor_ids_sha256": cube.id_digest(
                b"diag3-source-staircase8-box-zero-free-v1\0" + name.encode("ascii"),
                zero_free,
            ),
            "classification_semantic_sha256": semantic.hexdigest(),
        },
        "_occurring_ids": occurring,
        "_zero_free_ids": zero_free,
    }


def build_record(progress=False):
    _matrices, points, _packed, _states, _hamming, _multiplicity = transition.exact_inputs()
    source, target = points[SOURCE_CHART], points[TARGET_CHART]
    rows = [json.loads(line) for line in bridge.safe.CATALOG.read_text().splitlines() if line]
    parents, parent_digest = gate.parent_polynomials(rows[2599])
    candidates = gate.parse_candidates()
    _types, _terms, polynomials = labeled.factor_polynomials()
    ambient = json.loads(
        (HERE / "data" / "DIAG3_PAIR_FULL_HYBRID_CUBE_TOPOLOGY_0_152.json").read_text()
    )

    box_records = []
    union_occurring = set()
    zero_free_on_all = set(candidates)
    total_volume = Fraction(0)
    for name, starts, ends in BOXES:
        record = build_box(
            name,
            starts,
            ends,
            source,
            target,
            parents,
            parent_digest,
            candidates,
            polynomials,
            progress,
        )
        union_occurring.update(record.pop("_occurring_ids"))
        zero_free_on_all.intersection_update(record.pop("_zero_free_ids"))
        total_volume += box_volume(starts, ends)
        box_records.append(record)
        if progress:
            print(
                f"{name}: {record['wall_feasibility']['occurring_walls']} occurring",
                flush=True,
            )
    union_occurring = sorted(union_occurring)
    zero_free_on_all = sorted(zero_free_on_all)
    if set(union_occurring) & set(zero_free_on_all):
        raise AssertionError("staircase occurring and zero-free sets overlap")
    if len(union_occurring) + len(zero_free_on_all) != len(candidates):
        raise AssertionError("staircase union accounting is incomplete")
    if total_volume != Fraction(12_817, 16_384):
        raise AssertionError("wrong staircase volume")
    if not old_staircase_is_contained():
        raise AssertionError("the eight-box staircase does not contain the five-box staircase")
    if len(union_occurring) < OLD_STAIRCASE_OCCURRING:
        raise AssertionError("new staircase cannot lose factors from the contained old staircase")
    if ambient["wall_component_coverage"]["adaptive_critical_systems_unresolved"]:
        raise AssertionError("ambient component theorem dependency is unresolved")

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
            "parent_parameter_coverage": "COMPLETE_ON_DECLARED_EIGHT_BOX_SOURCE_STAIRCASE",
            "wall_feasibility_coverage": "COMPLETE_ON_EACH_SOURCE_BOX",
            "wall_component_coverage": "EVERY_RESTRICTED_WALL_COMPONENT_MEETS_STAIRCASE_OUTER_BOUNDARY",
            "internal_seams_required": False,
            "global_parent_cell_coverage": "NOT_CLAIMED",
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
                b"diag3-source-staircase8-union-occurring-v1", union_occurring
            ),
            "staircase_zero_free_factor_ids_sha256": cube.id_digest(
                b"diag3-source-staircase8-all-zero-free-v1", zero_free_on_all
            ),
            "outer_boundary_component_coverage": "PROVED_BY_AMBIENT_FULL_CUBE_TRANSFER",
            "global_missed_component_theorem": "OPEN",
        },
        "yield_gate": {
            "contains_five_box_staircase": True,
            "previous_exact_volume": cube.fraction_text(OLD_STAIRCASE_VOLUME),
            "exact_volume_gain": cube.fraction_text(total_volume - OLD_STAIRCASE_VOLUME),
            "previous_distinct_occurring_walls": OLD_STAIRCASE_OCCURRING,
            "additional_distinct_occurring_walls": len(union_occurring) - OLD_STAIRCASE_OCCURRING,
            "decision": "STOP_FURTHER_DYADIC_STAIRCASE_REFINEMENT",
            "reason": "The exact volume gain adds too few distinct occurring factors to justify another refinement layer; the invariant gap is global missed-component coverage, not local box feasibility.",
        },
        "ambient_topology_dependency": {
            "format": ambient["format"],
            "occurring_walls": ambient["wall_feasibility"]["occurring_walls"],
            "classification_semantic_sha256": ambient["wall_feasibility"]["classification_semantic_sha256"],
            "critical_semantic_sha256": ambient["wall_component_coverage"]["critical_semantic_sha256"],
            "component_conclusion": ambient["wall_component_coverage"]["conclusion"],
        },
        "boxes": box_records,
        "theorem_effect": "Enlarges the exact parent-safe source volume to 12817/16384 and removes internal seams from component coverage, but adds only 33 distinct occurring factors and does not close the global parent-cell missed-component theorem; honest 9DVL score remains 2/9.",
    }
