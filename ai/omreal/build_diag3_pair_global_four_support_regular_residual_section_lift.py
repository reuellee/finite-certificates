#!/usr/bin/env python3
"""Build exact lifts for regular residual four-support algebraic sections."""

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
MULTI = HERE / "data" / "DIAG3_PAIR_GLOBAL_FOUR_SUPPORT_MULTI_SECTION_LIFT.json"
OUTPUT = HERE / "data" / "DIAG3_PAIR_GLOBAL_FOUR_SUPPORT_REGULAR_RESIDUAL_SECTION_LIFT.json"
FORMAT = "diag3-pair-global-row2599-four-support-regular-residual-section-lift-v1"
u, t = sp.symbols("u t")


def digest(value):
    return sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":")).encode("ascii")
    ).hexdigest()


def main():
    sys.path.insert(0, str(HERE))
    import build_diag3_pair_global_four_support_invisible_section_lift as event_builder
    import build_diag3_pair_global_four_support_multi_section_lift as multi_builder

    base = json.loads(gzip.decompress(BASE.read_bytes()))
    roots = json.loads(gzip.decompress(ROOTS.read_bytes()))
    open_lift = json.loads(OPEN.read_bytes())
    simple = json.loads(SIMPLE.read_bytes())
    invisible = json.loads(INVISIBLE.read_bytes())
    multi = json.loads(MULTI.read_bytes())
    if multi["source"]["invisible_section_lift_semantic_sha256"] != invisible["semantic_sha256"]:
        raise AssertionError("multi-section source changed")

    polynomials = [
        sum(
            sp.Integer(term["coefficient"])
            * u ** term["exponent"][0]
            * t ** term["exponent"][1]
            for term in row["polynomial"]
        )
        for row in base["base_factorization"]["catalog"]
    ]
    u_degrees = [int(sp.degree(polynomial, u)) for polynomial in polynomials]
    catalog = {
        tuple(row["coefficients_low_to_high"]): row["id"]
        for row in base["second_projection"]["catalog"]
    }
    incidence = defaultdict(list)
    for base_id, polynomial in enumerate(polynomials):
        coefficients = list(reversed(sp.Poly(polynomial, u).all_coeffs()))
        for degree_u, coefficient in enumerate(coefficients):
            event_builder.add_event(
                incidence, catalog, "coefficient", (base_id, degree_u), coefficient
            )
        if u_degrees[base_id] >= 2:
            event_builder.add_event(
                incidence,
                catalog,
                "discriminant",
                (base_id, -1),
                sp.discriminant(polynomial, u),
            )
    for left in range(len(polynomials)):
        for right in range(left + 1, len(polynomials)):
            event_builder.add_event(
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
    sequences = event_builder.load_sequences(open_lift)
    sections = roots["root_isolation"]["sections"]
    already_complete = {
        row[0] for row in simple["simple_section_lift"]["crossings"]
    } | {
        row[0] for row in invisible["invisible_section_lift"]["completed"]
    } | {
        row[0] for row in multi["multi_section_lift"]["completed"]
    }

    unchanged = []
    same_count = []
    remaining = Counter()
    profile_census = Counter()
    total_events = total_resultants = total_coefficients = 0
    total_inversions = total_groups = total_invisible_resultants = 0
    root_points = strips = 0
    newly_complete = set()
    for section_id, (section, left, right) in enumerate(
        zip(sections, sequences[:-1], sequences[1:], strict=True)
    ):
        if section_id in already_complete:
            continue
        factor_id = section["factor_id"]
        events = incidence[factor_id]
        no_boundary = not boundary[factor_id]
        all_simple_resultants = bool(events) and all(
            kind == "resultant" and multiplicity == 1
            for kind, _owner, multiplicity in events
        )
        if left == right and no_boundary and all_simple_resultants:
            points = len(left)
            section_strips = points + 1
            unchanged.append(
                [
                    section_id,
                    factor_id,
                    section["factor_root_index"],
                    len(left),
                    len(events),
                    points,
                    section_strips,
                ]
            )
            newly_complete.add(section_id)
            total_events += len(events)
            total_resultants += len(events)
            total_invisible_resultants += len(events)
            root_points += points
            strips += section_strips
            continue

        if left != right and len(left) == len(right) and no_boundary:
            coefficient_events = [event for event in events if event[0] == "coefficient"]
            resultant_events = [event for event in events if event[0] == "resultant"]
            harmless_coefficients = bool(coefficient_events) and all(
                multiplicity == 1 and owner[1] < u_degrees[owner[0]]
                for _kind, owner, multiplicity in coefficient_events
            )
            regular_events = (
                len(events) == len(coefficient_events) + len(resultant_events)
                and all(multiplicity == 1 for _kind, _owner, multiplicity in resultant_events)
            )
            if harmless_coefficients and regular_events:
                tokens, edges = multi_builder.inversion_edges(left, right)
                event_owners = Counter(
                    tuple(sorted(owner))
                    for _kind, owner, _multiplicity in resultant_events
                )
                inversion_owners = Counter(
                    tuple(sorted((tokens[left_index][0], tokens[right_index][0])))
                    for left_index, right_index in edges
                )
                if inversion_owners - event_owners:
                    raise AssertionError("visible inversion lacks its simple resultant")
                components = multi_builder.clique_components(len(tokens), edges)
                points = len(left) - sum(len(component) - 1 for component in components)
                section_strips = points + 1
                invisible_resultants = len(resultant_events) - len(edges)
                profile = "+".join(map(str, sorted(map(len, components))))
                profile_census[profile] += 1
                same_count.append(
                    [
                        section_id,
                        factor_id,
                        section["factor_root_index"],
                        len(left),
                        len(coefficient_events),
                        len(resultant_events),
                        len(edges),
                        invisible_resultants,
                        points,
                        section_strips,
                        [list(component) for component in components],
                    ]
                )
                newly_complete.add(section_id)
                total_events += len(events)
                total_resultants += len(resultant_events)
                total_coefficients += len(coefficient_events)
                total_inversions += len(edges)
                total_groups += len(components)
                total_invisible_resultants += invisible_resultants
                root_points += points
                strips += section_strips
                continue

    for section_id, (left, right) in enumerate(zip(sequences[:-1], sequences[1:], strict=True)):
        if section_id in already_complete or section_id in newly_complete:
            continue
        if left == right:
            remaining["complex_unchanged_stack"] += 1
        elif len(left) == len(right):
            remaining["complex_same_count_transition"] += 1
        else:
            remaining["root_count_change"] += 1

    if len(unchanged) != 36 or len(same_count) != 4:
        raise AssertionError("regular residual tranche changed")
    if remaining != {
        "complex_unchanged_stack": 7,
        "complex_same_count_transition": 7,
        "root_count_change": 14,
    }:
        raise AssertionError("regular residual frontier changed")
    semantic_payload = {
        "multi_section_lift_semantic_sha256": multi["semantic_sha256"],
        "unchanged": unchanged,
        "same_count": same_count,
    }
    record = {
        "format": FORMAT,
        "status": "PROVED",
        "scope": {
            "regular_residual_algebraic_t_section_lifts": "COMPLETE",
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
            "multi_section_lift_semantic_sha256": multi["semantic_sha256"],
        },
        "regular_residual_section_lift": {
            "completed_sections": len(unchanged) + len(same_count),
            "completed_unchanged_sections": len(unchanged),
            "completed_same_count_sections": len(same_count),
            "raw_events": total_events,
            "simple_resultant_events": total_resultants,
            "harmless_nonleading_coefficient_events": total_coefficients,
            "visible_inversion_edges": total_inversions,
            "invisible_simple_resultant_events": total_invisible_resultants,
            "interior_collision_groups": total_groups,
            "same_count_component_size_profile_census": dict(sorted(profile_census.items())),
            "section_u_root_points": root_points,
            "section_u_strips": strips,
            "section_base_cells": root_points + strips,
            "completed_sha256": digest({"unchanged": unchanged, "same_count": same_count}),
            "unchanged": unchanged,
            "same_count": same_count,
        },
        "remaining_frontier": {
            "remaining_algebraic_t_sections": sum(remaining.values()),
            "census": dict(sorted(remaining.items())),
        },
        "semantic_sha256": digest(semantic_payload),
        "resource_effect": {
            "regular_residual_section_cell_ceiling": 100_000,
            "actual_regular_residual_section_cells": root_points + strips,
            "ceiling_not_triggered": root_points + strips < 100_000,
            "next_stage": "resolve 7 complex unchanged stacks, 7 exceptional same-count transitions, and 14 root-count changes",
        },
        "generator_dependency": {
            "python": sys.version.split()[0],
            "sympy": sp.__version__,
            "independent_verifier": "STANDARD_LIBRARY_ONLY",
        },
        "theorem_effect": "Regular residual algebraic fibers are complete for 36 unchanged stacks and 4 same-count transitions; 28 algebraic sections, v lifting, global gluing, and the diagonal-three invariant remain open; honest 9DVL score remains 2/9.",
    }
    OUTPUT.write_text(
        json.dumps(record, sort_keys=True, separators=(",", ":")) + "\n",
        encoding="ascii",
    )
    print("WROTE", OUTPUT)
    print("COMPLETED", len(unchanged), "+", len(same_count), "=", len(unchanged) + len(same_count))
    print("EVENTS", total_events, "RESULTANTS", total_resultants, "COEFFICIENTS", total_coefficients)
    print("VISIBLE", total_inversions, "INVISIBLE", total_invisible_resultants, "GROUPS", total_groups)
    print("SECTION_CELLS", root_points, "+", strips, "=", root_points + strips)
    print("REMAINING 7 + 7 + 14 =", sum(remaining.values()))


if __name__ == "__main__":
    main()
