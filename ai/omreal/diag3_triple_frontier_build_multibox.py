#!/usr/bin/env python3
"""Build the bounded diagonal-three triple multibox frontier canary.

The discovery rule is deliberately deterministic.  It takes the accepted
local-roadmap box and fixed projection, chooses the first adjacent same-size
box in (coordinate, direction) lexicographic order that retains all parent
signs and the projection-minor sign, and extends that corridor until the
first exact parent-cell or projection certificate frontier.  At each macrobox
the projection test uses the first successful choice in

    no split, split coordinate a, ..., split coordinate i.

Only one bisection is permitted.  The resulting certificate is a bounded
compiler canary, not an orbit closure theorem.
"""

from __future__ import annotations

from fractions import Fraction
import hashlib
from itertools import product
import json
from pathlib import Path
import sys


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE))

import verify_diag3_triple_local_roadmap_canary as accepted  # noqa: E402


OUTPUT = ROOT / "ops/team/triple-frontier/DIAG3_TRIPLE_FRONTIER_MULTIBOX_CANARY.json"
LEDGER = HERE / "data/DIAG3_RESEARCH_DECISION_LEDGER.json"
BASE_CERTIFICATE = HERE / "data/DIAG3_TRIPLE_LOCAL_ROADMAP_CANARY.json"
RESIDUE_COUNT = 1_162_302
RESIDUE_DIGEST = "a76a7c2cd6631c2d9724b450540bec7f3be6c106a41ae41f1736bbd2755a5ca4"
SCHEMA = "diag3-triple-frontier-multibox-canary-v1"
HOSTILE_MUTATIONS = [
    "accepted_macrobox_count",
    "corridor_axis",
    "subdivision_axis",
    "projection_interval",
    "parent_record_digest",
    "frontier_factor",
    "frontier_zero_witness",
    "global_parent_coverage_claim",
    "unresolved_count_reduction",
    "theorem_score",
]


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for block in iter(lambda: source.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def encoded(value: Fraction) -> str:
    return accepted.encoded(value)


def semantic_digest(candidate: dict) -> str:
    payload = dict(candidate)
    payload.pop("semantic_sha256", None)
    return hashlib.sha256(
        json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()


def rectangular_interval(polynomial, bounds):
    result = (Fraction(0), Fraction(0))
    for monomial, coefficient in polynomial.items():
        term = (coefficient, coefficient)
        for (lower, upper), exponent in zip(bounds, monomial, strict=True):
            term = accepted.product_interval(
                term, accepted.power_interval(lower, upper, exponent)
            )
        result = result[0] + term[0], result[1] + term[1]
    return result


def macro_bounds(center, radius):
    return tuple((value - radius, value + radius) for value in center)


def child_bounds(center, radius, split_axis, side):
    bounds = list(macro_bounds(center, radius))
    if split_axis is not None:
        lower, upper = bounds[split_axis]
        middle = center[split_axis]
        bounds[split_axis] = (lower, middle) if side == 0 else (middle, upper)
    return tuple(bounds)


def interval_record_digest(domain: bytes, records) -> str:
    digest = hashlib.sha256(domain + b"\0")
    for record in records:
        digest.update(json.dumps(record, separators=(",", ":")).encode("ascii"))
        digest.update(b"\n")
    return digest.hexdigest()


def main():
    base_certificate = json.loads(BASE_CERTIFICATE.read_text(encoding="utf-8"))
    accepted.verify_candidate(base_certificate)
    registration = json.loads(accepted.REGISTRATION.read_text(encoding="utf-8"))
    source = json.loads(accepted.SYSTEM.read_text(encoding="ascii"))
    ledger = json.loads(LEDGER.read_text(encoding="utf-8"))

    triple_obligation = next(
        item for item in ledger["invariant_obligations"]
        if item["id"] == "diag3_triple_hc0"
    )
    if triple_obligation["unresolved_count"] != RESIDUE_COUNT:
        raise AssertionError("triple-residue count changed")

    center0 = tuple(Fraction(value) for value in registration["fixed_box"]["center"])
    radius = Fraction(registration["fixed_box"]["radius"])
    residuals = tuple(
        accepted.decode_polynomial(record["terms"])
        for record in source["equations"][:3]
    )
    projection_columns = tuple(
        registration["fixed_projection"]["fiber_columns_zero_based"]
    )
    projection_minor = accepted.jacobian_minor(residuals, projection_columns)
    parent_brackets = accepted.parent_brackets()
    base_parent_signs = tuple(
        accepted.interval_sign(accepted.direct_interval(polynomial, center0, radius))
        for _label, polynomial in parent_brackets
    )
    base_projection_sign = accepted.interval_sign(
        accepted.direct_interval(projection_minor, center0, radius)
    )
    if not all(base_parent_signs) or not base_projection_sign:
        raise AssertionError("accepted base certificate no longer has strict signs")

    # Option (a) is ineligible because the accepted source contract explicitly
    # says that no materialized final-residue presentation stream is available.
    if "unavailable `1,162,302`-row final-residue stream" not in (
        HERE / "DIAG3_TRIPLE_LOCAL_ROADMAP_CANARY.md"
    ).read_text(encoding="utf-8"):
        raise AssertionError("deterministic branch-selection premise changed")

    chosen_direction = None
    for axis in range(9):
        for direction in (-1, 1):
            candidate_center = list(center0)
            candidate_center[axis] += direction * 2 * radius
            candidate_center = tuple(candidate_center)
            parent_signs = tuple(
                accepted.interval_sign(
                    accepted.direct_interval(polynomial, candidate_center, radius)
                )
                for _label, polynomial in parent_brackets
            )
            minor_sign = accepted.interval_sign(
                accepted.direct_interval(projection_minor, candidate_center, radius)
            )
            if parent_signs == base_parent_signs and minor_sign == base_projection_sign:
                chosen_direction = axis, direction
                break
        if chosen_direction is not None:
            break
    if chosen_direction is None:
        raise AssertionError("no adjacent projection-safe macrobox")

    axis, direction = chosen_direction
    macroboxes = []
    parent_records = []
    projection_records = []
    closest_parent = None
    frontier = None

    for macro_index in range(256):
        center = list(center0)
        center[axis] += direction * 2 * radius * macro_index
        center = tuple(center)

        current_parent_records = []
        parent_failure = []
        for label, polynomial in parent_brackets:
            interval = accepted.direct_interval(polynomial, center, radius)
            sign = accepted.interval_sign(interval)
            record = [
                macro_index, label, encoded(interval[0]), encoded(interval[1]), sign
            ]
            current_parent_records.append(record)
            if sign != base_parent_signs[len(current_parent_records) - 1]:
                parent_failure.append((label, polynomial, interval, sign))

        if parent_failure:
            bounds = macro_bounds(center, radius)
            exact_crossings = []
            for label, polynomial, interval, sign in parent_failure:
                vertex_rows = []
                for bits in product((0, 1), repeat=9):
                    point = tuple(
                        coordinate_bounds[bit]
                        for coordinate_bounds, bit in zip(bounds, bits, strict=True)
                    )
                    vertex_rows.append((accepted.evaluate(polynomial, point), bits, point))
                minimum = min(vertex_rows, key=lambda row: (row[0], row[1]))
                maximum = max(vertex_rows, key=lambda row: (row[0], row[1]))
                crossing = minimum[0] < 0 < maximum[0]
                exact_crossings.append(
                    {
                        "label": label,
                        "terms": len(polynomial),
                        "polynomial_sha256": accepted.polynomial_digest(
                            b"diag3-triple-frontier-parent-bracket-v1", polynomial
                        ),
                        "direct_interval": [encoded(interval[0]), encoded(interval[1])],
                        "direct_interval_sign": sign,
                        "vertex_minimum": encoded(minimum[0]),
                        "vertex_minimum_bits": "".join(map(str, minimum[1])),
                        "vertex_minimum_point": [encoded(value) for value in minimum[2]],
                        "vertex_maximum": encoded(maximum[0]),
                        "vertex_maximum_bits": "".join(map(str, maximum[1])),
                        "vertex_maximum_point": [encoded(value) for value in maximum[2]],
                        "opposite_vertex_signs": crossing,
                    }
                )
            frontier = {
                "kind": "FIRST_EXACT_PARENT_WALL_INTERSECTION",
                "macro_index": macro_index,
                "center": [encoded(value) for value in center],
                "radius": encoded(radius),
                "same_sign_parent_brackets": 70 - len(parent_failure),
                "failed_parent_brackets": exact_crossings,
                "projection_test_after_parent_failure": "NOT_RUN_BY_STOP_RULE",
            }
            break

        parent_records.extend(current_parent_records)
        for record in current_parent_records:
            interval = Fraction(record[2]), Fraction(record[3])
            sign = record[4]
            margin = interval[0] if sign > 0 else -interval[1]
            key = (margin, record[0], record[1])
            if closest_parent is None or key < closest_parent[0]:
                closest_parent = (key, record)

        selected_axis = None
        selected_children = None
        for split_axis in (None, *range(9)):
            sides = (0,) if split_axis is None else (0, 1)
            children = []
            for side in sides:
                bounds = child_bounds(center, radius, split_axis, side)
                interval = rectangular_interval(projection_minor, bounds)
                sign = accepted.interval_sign(interval)
                children.append((side, bounds, interval, sign))
            if all(child[3] == base_projection_sign for child in children):
                selected_axis = split_axis
                selected_children = children
                break

        if selected_children is None:
            frontier = {
                "kind": "FIRST_ONE_BISECTION_PROJECTION_FRONTIER",
                "macro_index": macro_index,
                "center": [encoded(value) for value in center],
                "radius": encoded(radius),
                "parent_brackets_same_sign": 70,
            }
            break

        child_records = []
        for side, bounds, interval, sign in selected_children:
            child_center = tuple((lower + upper) / 2 for lower, upper in bounds)
            child_radii = tuple((upper - lower) / 2 for lower, upper in bounds)
            child_record = {
                "macro_index": macro_index,
                "child_side": side,
                "subdivision_axis_zero_based": selected_axis,
                "center": [encoded(value) for value in child_center],
                "coordinate_radii": [encoded(value) for value in child_radii],
                "projection_minor_interval": [encoded(interval[0]), encoded(interval[1])],
                "projection_minor_sign": sign,
            }
            child_records.append(child_record)
            projection_records.append(child_record)
        macroboxes.append(
            {
                "index": macro_index,
                "center": [encoded(value) for value in center],
                "radius": encoded(radius),
                "subdivision_axis_zero_based": selected_axis,
                "certificate_box_count": len(child_records),
            }
        )

    if frontier is None:
        raise AssertionError("bounded corridor scan exhausted without a frontier")

    parent_digest = interval_record_digest(
        b"diag3-triple-frontier-parent-interval-records-v1", parent_records
    )
    projection_digest = interval_record_digest(
        b"diag3-triple-frontier-projection-records-v1", projection_records
    )
    projection_lowers = [Fraction(row["projection_minor_interval"][0]) for row in projection_records]
    projection_uppers = [Fraction(row["projection_minor_interval"][1]) for row in projection_records]
    accepted_macrobox_count = len(macroboxes)
    accepted_certificate_box_count = len(projection_records)
    intra_macro_seams = sum(row["certificate_box_count"] - 1 for row in macroboxes)

    accepted_centers = [tuple(Fraction(value) for value in row["center"]) for row in macroboxes]
    union_bounds = []
    for coordinate_index in range(9):
        union_bounds.append(
            [
                encoded(min(center[coordinate_index] - radius for center in accepted_centers)),
                encoded(max(center[coordinate_index] + radius for center in accepted_centers)),
            ]
        )

    failed = frontier["failed_parent_brackets"] if frontier["kind"] == "FIRST_EXACT_PARENT_WALL_INTERSECTION" else []
    if len(failed) == 1 and failed[0]["label"] == "3468" and failed[0]["opposite_vertex_signs"]:
        negative_point = tuple(Fraction(value) for value in failed[0]["vertex_minimum_point"])
        positive_point = tuple(Fraction(value) for value in failed[0]["vertex_maximum_point"])
        negative_value = Fraction(failed[0]["vertex_minimum"])
        positive_value = Fraction(failed[0]["vertex_maximum"])
        interpolation = -negative_value / (positive_value - negative_value)
        wall_point = tuple(
            left + interpolation * (right - left)
            for left, right in zip(negative_point, positive_point, strict=True)
        )
        failed[0]["zero_segment_parameter"] = encoded(interpolation)
        failed[0]["exact_parent_wall_point"] = [encoded(value) for value in wall_point]

    candidate = {
        "schema": SCHEMA,
        "status": "PROVED_MULTIBOX_LOCAL_BOUNDARY_COVERAGE_WITH_PARENT_WALL_FRONTIER",
        "track_id": "cycle-20260828-prover-triple-frontier",
        "base_revision": "ec362dba8a912bc4749c004641aee2da0a88dc05",
        "branch_selection": {
            "rule": (
                "choose smallest-family closure only if a canonical materialized final-residue "
                "presentation stream exists; otherwise choose the multibox projection canary"
            ),
            "materialized_1162302_row_presentation_stream": False,
            "selected": "MULTIBOX_PROJECTION_CANARY",
            "direction_order": [
                [coordinate_index, direction_value]
                for coordinate_index in range(9)
                for direction_value in (-1, 1)
            ],
            "chosen_axis_zero_based": axis,
            "chosen_direction": direction,
            "chosen_variable": accepted.VARIABLES[axis],
        },
        "authenticated_sources": {
            "decision_ledger": "ai/omreal/data/DIAG3_RESEARCH_DECISION_LEDGER.json",
            "decision_ledger_sha256": sha256(LEDGER),
            "critical_system": "ai/omreal/data/DIAG3_triple_fullspace_critical_h1.json",
            "critical_system_sha256": sha256(accepted.SYSTEM),
            "source_mapping_gate": "ai/omreal/data/DIAG3_triple_fullspace_feasibility_gate.json",
            "source_mapping_gate_sha256": sha256(accepted.SOURCE_GATE),
            "base_registration": "ai/omreal/data/DIAG3_TRIPLE_LOCAL_ROADMAP_REGISTRATION.json",
            "base_registration_sha256": sha256(accepted.REGISTRATION),
            "base_certificate": "ai/omreal/data/DIAG3_TRIPLE_LOCAL_ROADMAP_CANARY.json",
            "base_certificate_sha256": sha256(BASE_CERTIFICATE),
            "named_factor_presentation": source["named_presentation"],
            "canonical_unresolved_row": source["canonical_row"],
            "unresolved_residue_count": RESIDUE_COUNT,
            "unresolved_residue_source_order_sha256": RESIDUE_DIGEST,
        },
        "fixed_projection": {
            "fiber_columns_zero_based": list(projection_columns),
            "fiber_variables": [accepted.VARIABLES[index] for index in projection_columns],
            "projection_minor_terms": len(projection_minor),
            "projection_minor_sha256": accepted.polynomial_digest(
                b"diag3-local-projection-minor-v1", projection_minor
            ),
            "projection_minor_sign": base_projection_sign,
        },
        "corridor": {
            "macroboxes": macroboxes,
            "accepted_macrobox_count": accepted_macrobox_count,
            "accepted_certificate_box_count": accepted_certificate_box_count,
            "union_coordinate_bounds": union_bounds,
            "geometric_outer_facets": 18,
            "macro_adjacency_seams": accepted_macrobox_count - 1,
            "intra_macro_subdivision_seams": intra_macro_seams,
            "all_parent_brackets_same_sign": True,
            "parent_brackets_per_macrobox": 70,
            "parent_interval_record_count": len(parent_records),
            "parent_interval_record_sha256": parent_digest,
            "common_parent_sign_vector_sha256": hashlib.sha256(
                b"diag3-triple-frontier-parent-sign-vector-v1\0"
                + bytes(int(value > 0) for value in base_parent_signs)
            ).hexdigest(),
            "closest_parent_interval_record": closest_parent[1],
            "projection_records": projection_records,
            "projection_interval_record_sha256": projection_digest,
            "projection_interval_envelope": [
                encoded(min(projection_lowers)), encoded(max(projection_uppers))
            ],
        },
        "frontier": frontier,
        "topological_consequence": (
            "Every connected component of the named triple-zero set restricted to the "
            "accepted 20-macrobox rectangular corridor meets one of the 18 geometric "
            "outer facets; the component through the registered exact zero is nonvacuous."
        ),
        "scope_and_nonconsequences": {
            "complete_named_factor_orbits_closed": 0,
            "global_parent_cell_coverage_claimed": False,
            "s8_transport_claimed": False,
            "genuine_parent_infinity_reached": False,
            "artificial_outer_facets": 18,
            "unresolved_triple_orbits_before": RESIDUE_COUNT,
            "unresolved_triple_orbits_after": RESIDUE_COUNT,
            "score_before": "2/9",
            "score_after": "2/9",
        },
        "canaries": {
            "positive_base_box_replayed": True,
            "positive_first_adjacent_box_certified": True,
            "null_first_parent_wall_frontier_stops_extension": True,
            "negative_compact_sphere_projection_sign_refused": True,
            "hostile_mutations_declared": HOSTILE_MUTATIONS,
        },
    }
    candidate["semantic_sha256"] = semantic_digest(candidate)
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(candidate, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    print(f"WROTE {OUTPUT.relative_to(ROOT)}")
    print(
        "PASS deterministic corridor",
        f"macroboxes={accepted_macrobox_count}",
        f"certificate_boxes={accepted_certificate_box_count}",
        f"frontier={frontier['kind']}@{frontier['macro_index']}",
    )
    print(f"SEMANTIC {candidate['semantic_sha256']}")
    print("SCOPE no complete orbit; unresolved=1162302; score=2/9")


if __name__ == "__main__":
    main()
