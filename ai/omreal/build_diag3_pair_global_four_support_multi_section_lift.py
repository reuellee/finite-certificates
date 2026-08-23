#!/usr/bin/env python3
"""Build exact multi-crossing lifts for same-count algebraic t sections."""

from __future__ import annotations

from collections import Counter, defaultdict
import gzip
from hashlib import sha256
import json
from pathlib import Path
import sys

import sympy as sp


HERE = Path(__file__).resolve().parent
BASE = HERE / "data" / "DIAG3_PAIR_GLOBAL_FOUR_SUPPORT_BASE_PROJECTION.json.gz"
ROOTS = HERE / "data" / "DIAG3_PAIR_GLOBAL_FOUR_SUPPORT_ROOT_ISOLATION.json.gz"
OPEN = HERE / "data" / "DIAG3_PAIR_GLOBAL_FOUR_SUPPORT_OPEN_SECTOR_LIFT.json"
SIMPLE = HERE / "data" / "DIAG3_PAIR_GLOBAL_FOUR_SUPPORT_SIMPLE_SECTION_LIFT.json"
INVISIBLE = HERE / "data" / "DIAG3_PAIR_GLOBAL_FOUR_SUPPORT_INVISIBLE_SECTION_LIFT.json"
OUTPUT = HERE / "data" / "DIAG3_PAIR_GLOBAL_FOUR_SUPPORT_MULTI_SECTION_LIFT.json"
FORMAT = "diag3-pair-global-row2599-four-support-multi-section-lift-v1"
u, t = sp.symbols("u t")


def digest(value):
    return sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":")).encode("ascii")
    ).hexdigest()


def occurrence_tokens(sequence):
    counts = Counter()
    answer = []
    for factor_id in sequence:
        answer.append((factor_id, counts[factor_id]))
        counts[factor_id] += 1
    return answer


def inversion_edges(left, right):
    left_tokens = occurrence_tokens(left)
    right_tokens = occurrence_tokens(right)
    if Counter(left_tokens) != Counter(right_tokens):
        return left_tokens, []
    positions = {token: index for index, token in enumerate(right_tokens)}
    return left_tokens, [
        (left_index, right_index)
        for left_index in range(len(left_tokens))
        for right_index in range(left_index + 1, len(left_tokens))
        if positions[left_tokens[left_index]] > positions[left_tokens[right_index]]
    ]


def clique_components(vertex_count, edges):
    parents = list(range(vertex_count))

    def find(item):
        while parents[item] != item:
            parents[item] = parents[parents[item]]
            item = parents[item]
        return item

    def union(left, right):
        left, right = find(left), find(right)
        if left != right:
            parents[right] = left

    active = set()
    for left, right in edges:
        active.update((left, right))
        union(left, right)
    groups = defaultdict(set)
    for item in active:
        groups[find(item)].add(item)
    components = sorted(tuple(sorted(group)) for group in groups.values())
    for component in components:
        actual = sum(
            left in component and right in component for left, right in edges
        )
        expected = len(component) * (len(component) - 1) // 2
        if actual != expected:
            raise AssertionError("inversion component is not a clique")
    return components


def main():
    sys.path.insert(0, str(HERE))
    import build_diag3_pair_global_four_support_invisible_section_lift as invisible_builder

    base = json.loads(gzip.decompress(BASE.read_bytes()))
    roots = json.loads(gzip.decompress(ROOTS.read_bytes()))
    open_lift = json.loads(OPEN.read_bytes())
    simple = json.loads(SIMPLE.read_bytes())
    invisible = json.loads(INVISIBLE.read_bytes())
    if invisible["source"]["simple_section_lift_semantic_sha256"] != simple["semantic_sha256"]:
        raise AssertionError("invisible-section source changed")

    polynomials = [
        sum(
            sp.Integer(term["coefficient"])
            * u ** term["exponent"][0]
            * t ** term["exponent"][1]
            for term in row["polynomial"]
        )
        for row in base["base_factorization"]["catalog"]
    ]
    catalog = {
        tuple(row["coefficients_low_to_high"]): row["id"]
        for row in base["second_projection"]["catalog"]
    }
    incidence = defaultdict(list)
    for base_id, polynomial in enumerate(polynomials):
        coefficients = list(reversed(sp.Poly(polynomial, u).all_coeffs()))
        for degree_u, coefficient in enumerate(coefficients):
            invisible_builder.add_event(
                incidence, catalog, "coefficient", (base_id, degree_u), coefficient
            )
        if sp.degree(polynomial, u) >= 2:
            invisible_builder.add_event(
                incidence,
                catalog,
                "discriminant",
                (base_id, -1),
                sp.discriminant(polynomial, u),
            )
    for left in range(len(polynomials)):
        for right in range(left + 1, len(polynomials)):
            invisible_builder.add_event(
                incidence,
                catalog,
                "resultant",
                (left, right),
                sp.resultant(polynomials[left], polynomials[right], u),
            )

    boundary = defaultdict(list)
    for row in open_lift["bounded_u_boundary_audit"]["factorizations"]:
        for factor in row["factors"]:
            boundary[factor["id"]].append(
                (row["base_factor_id"], factor["multiplicity"])
            )
    sequences = invisible_builder.load_sequences(open_lift)
    sections = roots["root_isolation"]["sections"]
    already_complete = {
        row[0] for row in simple["simple_section_lift"]["crossings"]
    } | {
        row[0]
        for row in invisible["invisible_section_lift"]["completed"]
    }

    completed = []
    profile_census = Counter()
    excluded = Counter()
    total_events = total_inversions = total_groups = 0
    root_points = strips = 0
    for section_id, (section, left, right) in enumerate(
        zip(sections, sequences[:-1], sequences[1:], strict=True)
    ):
        if section_id in already_complete or left == right or len(left) != len(right):
            continue
        factor_id = section["factor_id"]
        events = incidence[factor_id]
        if boundary[factor_id]:
            excluded["boundary"] += 1
            continue
        if any(kind != "resultant" for kind, _owner, _multiplicity in events):
            excluded["nonresultant"] += 1
            continue
        if any(multiplicity != 1 for _kind, _owner, multiplicity in events):
            excluded["multiplicity"] += 1
            continue

        tokens, edges = inversion_edges(left, right)
        event_owners = Counter(tuple(sorted(owner)) for _kind, owner, _multiplicity in events)
        inversion_owners = Counter(
            tuple(sorted((tokens[left_index][0], tokens[right_index][0])))
            for left_index, right_index in edges
        )
        if inversion_owners - event_owners:
            raise AssertionError("visible inversion lacks its raw resultant event")
        components = clique_components(len(tokens), edges)
        section_points = len(left) - sum(len(component) - 1 for component in components)
        section_strips = section_points + 1
        profile = "+".join(map(str, sorted(map(len, components))))
        profile_census[profile] += 1
        total_events += len(events)
        total_inversions += len(edges)
        total_groups += len(components)
        root_points += section_points
        strips += section_strips
        completed.append(
            [
                section_id,
                factor_id,
                section["factor_root_index"],
                len(left),
                len(events),
                len(edges),
                section_points,
                section_strips,
                [list(component) for component in components],
            ]
        )

    if len(completed) != 240 or excluded != {"nonresultant": 7, "multiplicity": 4}:
        raise AssertionError("multi-section frontier changed")
    if (total_events, total_inversions, total_groups) != (1549, 1390, 549):
        raise AssertionError("multi-event accounting changed")
    if (root_points, strips) != (19922, 20162):
        raise AssertionError("multi-section cell accounting changed")
    semantic_payload = {
        "invisible_section_lift_semantic_sha256": invisible["semantic_sha256"],
        "completed": completed,
    }
    record = {
        "format": FORMAT,
        "status": "PROVED",
        "scope": {
            "pure_resultant_same_count_multi_section_lifts": "COMPLETE",
            "remaining_algebraic_t_section_lifts": "NOT_YET_CONSTRUCTED",
            "v_fiber_lift": "NOT_YET_CONSTRUCTED",
            "global_parent_cell_coverage": "NOT_CLAIMED",
            "honest_9dvl_score": "2/9",
        },
        "source": {
            "base_projection_semantic_sha256": base["semantic_sha256"],
            "root_isolation_semantic_sha256": roots["semantic_sha256"],
            "open_sector_lift_semantic_sha256": open_lift["semantic_sha256"],
            "simple_section_lift_semantic_sha256": simple["semantic_sha256"],
            "invisible_section_lift_semantic_sha256": invisible["semantic_sha256"],
        },
        "multi_section_lift": {
            "completed_same_count_sections": len(completed),
            "raw_resultant_events": total_events,
            "visible_inversion_edges": total_inversions,
            "interior_collision_groups": total_groups,
            "all_raw_event_multiplicities_one": True,
            "sections_with_coefficient_discriminant_or_boundary_event": 0,
            "component_size_profile_census": dict(sorted(profile_census.items())),
            "section_u_root_points": root_points,
            "section_u_strips": strips,
            "section_base_cells": root_points + strips,
            "completed_sha256": digest(completed),
            "completed": completed,
        },
        "remaining_frontier": {
            "remaining_algebraic_t_sections": 68,
            "census": {
                "complex_unchanged_stack": 43,
                "complex_same_count_transition": 11,
                "root_count_change": 14,
            },
        },
        "semantic_sha256": digest(semantic_payload),
        "resource_effect": {
            "multi_section_cell_ceiling": 100_000,
            "actual_multi_section_cells": root_points + strips,
            "ceiling_not_triggered": root_points + strips < 100_000,
            "next_stage": "resolve 43 complex unchanged stacks, 11 exceptional same-count transitions, and 14 root-count changes",
        },
        "generator_dependency": {
            "python": sys.version.split()[0],
            "sympy": sp.__version__,
            "independent_verifier": "STANDARD_LIBRARY_ONLY",
        },
        "theorem_effect": "Pure-resultant same-count algebraic fibers are complete for 240 simultaneous multi-crossing sections; 68 algebraic sections, v lifting, global gluing, and the diagonal-three invariant remain open; honest 9DVL score remains 2/9.",
    }
    OUTPUT.write_text(
        json.dumps(record, sort_keys=True, separators=(",", ":")) + "\n",
        encoding="ascii",
    )
    print("WROTE", OUTPUT)
    print("COMPLETED", len(completed), "EVENTS", total_events, "INVERSIONS", total_inversions)
    print("COLLISION_GROUPS", total_groups)
    print("SECTION_CELLS", root_points, "+", strips, "=", root_points + strips)
    print("REMAINING 43 + 11 + 14 = 68")


if __name__ == "__main__":
    main()
