#!/usr/bin/env python3
"""Independent hostile replay of the exact eight-box source staircase."""

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
CERTIFICATE = HERE / "data" / "DIAG3_PAIR_SOURCE_STAIRCASE8_COVERAGE_0_152.json"
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
OLD_VOLUME = Fraction(373, 512)
OLD_OCCURRING = 5_106
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
import verify_diag3_pair_full_hybrid_cube_topology as ambient  # noqa: E402
import verify_diag3_pair_global_parent_face_gate as gate  # noqa: E402
import verify_diag3_pair_source_block_cube_feasibility as base  # noqa: E402


def volume(starts, ends):
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


def assert_contains_old_staircase():
    endpoints = sorted(
        {value for start, end, _height in OLD_STEPS for value in (start, end)}
        | {value for _name, starts, ends in BOXES for value in (starts[0], ends[0])}
    )
    for left, right in zip(endpoints, endpoints[1:]):
        midpoint = (left + right) / 2
        old_height = max(
            height for start, end, height in OLD_STEPS if start <= midpoint <= end
        )
        assert staircase_height(BOXES, midpoint) >= old_height


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
        signed = tuple(
            target_sign * base.value_at(restricted, vertex) for vertex in vertices
        )
        assert min(signed) > 0
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
        semantic.update(base.fraction_text(value).encode("ascii") + b"\0")
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
    assert not unresolved
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
                b"diag3-source-staircase8-box-occurring-v1\0" + name.encode("ascii"),
                occurring,
            ),
            "zero_free_factor_ids_sha256": base.digest_ids(
                b"diag3-source-staircase8-box-zero-free-v1\0" + name.encode("ascii"),
                zero_free,
            ),
            "classification_semantic_sha256": semantic.hexdigest(),
        },
        "_occurring": occurring,
        "_zero_free": zero_free,
    }


def reconstruct():
    _matrices, points, _packed, _states, _hamming, _multiplicity = transition.exact_inputs()
    source, target = points[0], points[152]
    rows = [json.loads(line) for line in bridge.safe.CATALOG.read_text().splitlines() if line]
    parents, parent_digest = gate.parent_polynomials(rows[2599])
    candidates = gate.parse_candidates()
    _types, _terms, polynomials = labeled.factor_polynomials()
    ambient_record = ambient.reconstruct()
    ambient.validate(ambient_record, ambient_record)

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
    assert total_volume == Fraction(12_817, 16_384)
    assert_contains_old_staircase()
    assert len(union_occurring) >= OLD_OCCURRING
    return {
        "format": "diag3-pair-source-staircase8-coverage-v1",
        "status": "EXACT_SOURCE_STAIRCASE8_OUTER_BOUNDARY_COVERAGE",
        "scope": {
            "parent_index": 2599,
            "source_chart": 0,
            "target_chart": 152,
            "varying_column_blocks": [0, 1, 2],
            "source_boxes": len(BOXES),
            "exact_parameter_volume": base.fraction_text(total_volume),
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
            "staircase_occurring_factor_ids_sha256": base.digest_ids(
                b"diag3-source-staircase8-union-occurring-v1", union_occurring
            ),
            "staircase_zero_free_factor_ids_sha256": base.digest_ids(
                b"diag3-source-staircase8-all-zero-free-v1", zero_free_on_all
            ),
            "outer_boundary_component_coverage": "PROVED_BY_AMBIENT_FULL_CUBE_TRANSFER",
            "global_missed_component_theorem": "OPEN",
        },
        "yield_gate": {
            "contains_five_box_staircase": True,
            "previous_exact_volume": base.fraction_text(OLD_VOLUME),
            "exact_volume_gain": base.fraction_text(total_volume - OLD_VOLUME),
            "previous_distinct_occurring_walls": OLD_OCCURRING,
            "additional_distinct_occurring_walls": len(union_occurring) - OLD_OCCURRING,
            "decision": "STOP_FURTHER_DYADIC_STAIRCASE_REFINEMENT",
            "reason": "The exact volume gain adds too few distinct occurring factors to justify another refinement layer; the invariant gap is global missed-component coverage, not local box feasibility.",
        },
        "ambient_topology_dependency": {
            "format": ambient_record["format"],
            "occurring_walls": ambient_record["wall_feasibility"]["occurring_walls"],
            "classification_semantic_sha256": ambient_record["wall_feasibility"]["classification_semantic_sha256"],
            "critical_semantic_sha256": ambient_record["wall_component_coverage"]["critical_semantic_sha256"],
            "component_conclusion": ambient_record["wall_component_coverage"]["conclusion"],
        },
        "boxes": box_records,
        "theorem_effect": "Enlarges the exact parent-safe source volume to 12817/16384 and removes internal seams from component coverage, but adds only 33 distinct occurring factors and does not close the global parent-cell missed-component theorem; honest 9DVL score remains 2/9.",
    }


def validate(candidate, expected):
    assert candidate == expected
    assert candidate["scope"]["exact_parameter_volume"] == "12817/16384"
    assert candidate["summary"]["box_factor_restrictions_replayed"] == 142_592
    assert candidate["summary"]["parent_bracket_box_restrictions_replayed"] == 560
    assert candidate["summary"]["strict_parent_vertices_replayed"] == 64
    assert candidate["summary"]["staircase_occurring_walls"] == 5_139
    assert candidate["summary"]["zero_free_on_all_staircase_boxes"] == 12_685
    assert candidate["summary"]["unresolved_box_factor_restrictions"] == 0
    assert [box["wall_feasibility"]["occurring_walls"] for box in candidate["boxes"]] == [
        1_320, 1_677, 1_982, 2_314, 2_637, 2_956, 3_232, 4_610
    ]
    assert candidate["yield_gate"]["exact_volume_gain"] == "881/16384"
    assert candidate["yield_gate"]["additional_distinct_occurring_walls"] == 33
    assert candidate["yield_gate"]["decision"] == "STOP_FURTHER_DYADIC_STAIRCASE_REFINEMENT"
    assert candidate["scope"]["internal_seams_required"] is False
    assert candidate["scope"]["global_parent_cell_coverage"] == "NOT_CLAIMED"


def main():
    stored = json.loads(CERTIFICATE.read_text())
    expected = reconstruct()
    validate(stored, expected)
    mutations = []
    for path, value in (
        (("format",), "corrupted"),
        (("scope", "exact_parameter_volume"), "1"),
        (("scope", "internal_seams_required"), True),
        (("scope", "global_parent_cell_coverage"), "COMPLETE"),
        (("summary", "box_factor_restrictions_replayed"), 142_591),
        (("summary", "staircase_occurring_walls"), 5_140),
        (("summary", "staircase_occurring_factor_ids_sha256"), "0" * 64),
        (("yield_gate", "additional_distinct_occurring_walls"), 34),
        (("yield_gate", "decision"), "REFINE_TO_32_STEPS"),
        (("ambient_topology_dependency", "critical_semantic_sha256"), "0" * 64),
        (("boxes", 0, "parent_cube", "strict_vertices"), 7),
        (("boxes", 7, "wall_feasibility", "occurring_walls"), 4_611),
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
    print("PASS eight exact parent-resident source boxes cover volume 12817/16384")
    print("PASS 142,592 box-factor restrictions decided with zero unresolved")
    print("PASS 5,139 distinct occurring walls; 12,685 zero-free on all boxes")
    print("PASS ambient full-cube theorem transfers every component to the true outer boundary")
    print("PASS yield gate stops further dyadic staircase refinement after only 33 new factors")
    print(f"PASS {rejected}/{len(mutations)} hostile corruptions rejected")
    print("SCOPE enlarged source family only; global parent missed-component theorem open; honest 9DVL 2/9")


if __name__ == "__main__":
    main()
