#!/usr/bin/env python3
"""Independent replay of the bounded triple multibox frontier canary.

This verifier does not import the frontier producer.  It reconstructs the
source polynomials, parent brackets, fixed projection minor, deterministic
direction choice, one-bisection policy, exact interval records, corridor
partition, and first parent-wall frontier from pinned repository inputs.
"""

from __future__ import annotations

from copy import deepcopy
from fractions import Fraction
import hashlib
from itertools import product
import json
from pathlib import Path
import sys


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE))

import verify_diag3_triple_local_roadmap_canary as base  # noqa: E402


CERTIFICATE = ROOT / "ops/team/triple-frontier/DIAG3_TRIPLE_FRONTIER_MULTIBOX_CANARY.json"
LEDGER = HERE / "data/DIAG3_RESEARCH_DECISION_LEDGER.json"
BASE_CERTIFICATE = HERE / "data/DIAG3_TRIPLE_LOCAL_ROADMAP_CANARY.json"
SCHEMA = "diag3-triple-frontier-multibox-canary-v1"
BASE_REVISION = "ec362dba8a912bc4749c004641aee2da0a88dc05"
RESIDUE_COUNT = 1_162_302
RESIDUE_DIGEST = "a76a7c2cd6631c2d9724b450540bec7f3be6c106a41ae41f1736bbd2755a5ca4"
EXPECTED_SOURCE_HASHES = {
    "decision_ledger_sha256": "5841dfbb55aa0d8c580b394b50beff54d607ce86b77683985c2d977c03050e14",
    "critical_system_sha256": "c9244a47ded5736e7afe724a9914e75631a22b78653442e88c14f5c397919eb8",
    "source_mapping_gate_sha256": "8ad62abdd3bd7d9bc14e5bfec3e407f3c07fd740a5475d1243e8dbb9e08d8692",
    "base_registration_sha256": "94224ab5f5f64d8a7e14e3d5d382c5cdc96292d9a455520c3c76e003b77eddb3",
    "base_certificate_sha256": "0ee63d4049278c41b8fdd611aacdbe56b188dc1225bd1b9dc18dc37fb2746c27",
}
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
EXPECTED_SUBDIVISION_AXES = (
    None, None, None, None, None,
    0, 0, 0, 0, 0, 0, 0, 0, 0,
    2, 2, 2, 2, 2,
    6,
)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for block in iter(lambda: source.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def encoded(value: Fraction) -> str:
    return base.encoded(value)


def semantic_digest(candidate: dict) -> str:
    payload = dict(candidate)
    payload.pop("semantic_sha256", None)
    return hashlib.sha256(
        json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()


def rectangular_interval(polynomial, bounds):
    """Direct sparse-monomial interval evaluation on a rational rectangle."""

    result = (Fraction(0), Fraction(0))
    for monomial, coefficient in polynomial.items():
        term = (coefficient, coefficient)
        for (lower, upper), exponent in zip(bounds, monomial, strict=True):
            power = base.power_interval(lower, upper, exponent)
            term = base.product_interval(term, power)
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


def records_digest(domain: bytes, records) -> str:
    digest = hashlib.sha256(domain + b"\0")
    for record in records:
        digest.update(json.dumps(record, separators=(",", ":")).encode("ascii"))
        digest.update(b"\n")
    return digest.hexdigest()


def verify_source_accounting(candidate):
    authenticated = candidate["authenticated_sources"]
    expected_paths = {
        "decision_ledger": "ai/omreal/data/DIAG3_RESEARCH_DECISION_LEDGER.json",
        "critical_system": "ai/omreal/data/DIAG3_triple_fullspace_critical_h1.json",
        "source_mapping_gate": "ai/omreal/data/DIAG3_triple_fullspace_feasibility_gate.json",
        "base_registration": "ai/omreal/data/DIAG3_TRIPLE_LOCAL_ROADMAP_REGISTRATION.json",
        "base_certificate": "ai/omreal/data/DIAG3_TRIPLE_LOCAL_ROADMAP_CANARY.json",
    }
    for key, value in expected_paths.items():
        if authenticated[key] != value:
            raise AssertionError(f"source path changed: {key}")
    actual_hashes = {
        "decision_ledger_sha256": sha256(LEDGER),
        "critical_system_sha256": sha256(base.SYSTEM),
        "source_mapping_gate_sha256": sha256(base.SOURCE_GATE),
        "base_registration_sha256": sha256(base.REGISTRATION),
        "base_certificate_sha256": sha256(BASE_CERTIFICATE),
    }
    if actual_hashes != EXPECTED_SOURCE_HASHES:
        raise AssertionError(f"pinned source hash changed: {actual_hashes}")
    for key, value in EXPECTED_SOURCE_HASHES.items():
        if authenticated[key] != value:
            raise AssertionError(f"certificate source digest changed: {key}")
    if authenticated["named_factor_presentation"] != [5563, 16134, 19284]:
        raise AssertionError("named presentation changed")
    if authenticated["canonical_unresolved_row"] != [5563, 4373, 23221]:
        raise AssertionError("canonical row changed")
    if authenticated["unresolved_residue_count"] != RESIDUE_COUNT:
        raise AssertionError("residue count changed")
    if authenticated["unresolved_residue_source_order_sha256"] != RESIDUE_DIGEST:
        raise AssertionError("residue digest changed")

    ledger = json.loads(LEDGER.read_text(encoding="utf-8"))
    obligation = next(
        item for item in ledger["invariant_obligations"]
        if item["id"] == "diag3_triple_hc0"
    )
    if (
        obligation["status"],
        obligation["universe_count"],
        obligation["proved_noncompact_count"],
        obligation["unresolved_count"],
    ) != ("OPEN", 79_102_449, 77_940_147, RESIDUE_COUNT):
        raise AssertionError("canonical triple accounting changed")

    base_candidate = json.loads(BASE_CERTIFICATE.read_text(encoding="utf-8"))
    base.verify_candidate(base_candidate)


def reconstruct_corridor(candidate):
    registration = json.loads(base.REGISTRATION.read_text(encoding="utf-8"))
    source = json.loads(base.SYSTEM.read_text(encoding="ascii"))
    center0 = tuple(Fraction(value) for value in registration["fixed_box"]["center"])
    radius = Fraction(registration["fixed_box"]["radius"])
    residuals = tuple(
        base.decode_polynomial(record["terms"])
        for record in source["equations"][:3]
    )
    projection_columns = tuple(
        registration["fixed_projection"]["fiber_columns_zero_based"]
    )
    if projection_columns != (3, 4, 7):
        raise AssertionError("fixed projection changed")
    projection_minor = base.jacobian_minor(residuals, projection_columns)
    parent_brackets = base.parent_brackets()
    base_parent_signs = tuple(
        base.interval_sign(base.direct_interval(polynomial, center0, radius))
        for _label, polynomial in parent_brackets
    )
    projection_sign = base.interval_sign(
        base.direct_interval(projection_minor, center0, radius)
    )
    if not all(base_parent_signs) or projection_sign != -1:
        raise AssertionError("base strict signs changed")

    branch = candidate["branch_selection"]
    expected_order = [
        [coordinate, direction]
        for coordinate in range(9)
        for direction in (-1, 1)
    ]
    if branch != {
        "rule": (
            "choose smallest-family closure only if a canonical materialized final-residue "
            "presentation stream exists; otherwise choose the multibox projection canary"
        ),
        "materialized_1162302_row_presentation_stream": False,
        "selected": "MULTIBOX_PROJECTION_CANARY",
        "direction_order": expected_order,
        "chosen_axis_zero_based": 0,
        "chosen_direction": -1,
        "chosen_variable": "a",
    }:
        raise AssertionError("deterministic branch or direction selection changed")
    if "unavailable `1,162,302`-row final-residue stream" not in (
        HERE / "DIAG3_TRIPLE_LOCAL_ROADMAP_CANARY.md"
    ).read_text(encoding="utf-8"):
        raise AssertionError("branch-selection premise changed")

    adjacent = list(center0)
    adjacent[0] -= 2 * radius
    adjacent = tuple(adjacent)
    if tuple(
        base.interval_sign(base.direct_interval(polynomial, adjacent, radius))
        for _label, polynomial in parent_brackets
    ) != base_parent_signs:
        raise AssertionError("lexicographically first adjacent parent box changed")
    if base.interval_sign(base.direct_interval(projection_minor, adjacent, radius)) != -1:
        raise AssertionError("lexicographically first adjacent projection box changed")

    corridor = candidate["corridor"]
    macroboxes = corridor["macroboxes"]
    if len(macroboxes) != 20 or corridor["accepted_macrobox_count"] != 20:
        raise AssertionError("accepted macrobox count changed")
    if len(EXPECTED_SUBDIVISION_AXES) != 20:
        raise AssertionError("internal subdivision fixture changed")

    all_parent_records = []
    all_projection_records = []
    closest = None
    accepted_centers = []
    for macro_index, (macro, expected_axis) in enumerate(
        zip(macroboxes, EXPECTED_SUBDIVISION_AXES, strict=True)
    ):
        center = list(center0)
        center[0] -= 2 * radius * macro_index
        center = tuple(center)
        accepted_centers.append(center)
        expected_macro = {
            "index": macro_index,
            "center": [encoded(value) for value in center],
            "radius": encoded(radius),
            "subdivision_axis_zero_based": expected_axis,
            "certificate_box_count": 1 if expected_axis is None else 2,
        }
        if macro != expected_macro:
            raise AssertionError(f"macrobox record changed at {macro_index}")

        for parent_index, (label, polynomial) in enumerate(parent_brackets):
            interval = base.direct_interval(polynomial, center, radius)
            sign = base.interval_sign(interval)
            if sign != base_parent_signs[parent_index]:
                raise AssertionError(f"accepted macrobox crosses parent wall: {macro_index}/{label}")
            record = [macro_index, label, encoded(interval[0]), encoded(interval[1]), sign]
            all_parent_records.append(record)
            margin = interval[0] if sign > 0 else -interval[1]
            key = (margin, macro_index, label)
            if closest is None or key < closest[0]:
                closest = (key, record)

        # Recompute the first successful subdivision axis.  This verifies the
        # deterministic minimality claim, not only the stored chosen split.
        actual_axis = None
        actual_children = None
        for split_axis in (None, *range(9)):
            sides = (0,) if split_axis is None else (0, 1)
            children = []
            for side in sides:
                bounds = child_bounds(center, radius, split_axis, side)
                interval = rectangular_interval(projection_minor, bounds)
                sign = base.interval_sign(interval)
                children.append((side, bounds, interval, sign))
            if all(row[3] == projection_sign for row in children):
                actual_axis = split_axis
                actual_children = children
                break
        if actual_axis != expected_axis or actual_children is None:
            raise AssertionError(f"minimal subdivision changed at macrobox {macro_index}")
        for side, bounds, interval, sign in actual_children:
            child_center = tuple((lower + upper) / 2 for lower, upper in bounds)
            child_radii = tuple((upper - lower) / 2 for lower, upper in bounds)
            all_projection_records.append(
                {
                    "macro_index": macro_index,
                    "child_side": side,
                    "subdivision_axis_zero_based": actual_axis,
                    "center": [encoded(value) for value in child_center],
                    "coordinate_radii": [encoded(value) for value in child_radii],
                    "projection_minor_interval": [encoded(interval[0]), encoded(interval[1])],
                    "projection_minor_sign": sign,
                }
            )

    if corridor["projection_records"] != all_projection_records:
        raise AssertionError("projection interval records changed")
    if corridor["accepted_certificate_box_count"] != len(all_projection_records) != 35:
        raise AssertionError("certificate-box count changed")
    parent_digest = records_digest(
        b"diag3-triple-frontier-parent-interval-records-v1", all_parent_records
    )
    projection_digest = records_digest(
        b"diag3-triple-frontier-projection-records-v1", all_projection_records
    )
    if corridor["parent_interval_record_sha256"] != parent_digest:
        raise AssertionError("parent interval record digest changed")
    if corridor["projection_interval_record_sha256"] != projection_digest:
        raise AssertionError("projection interval record digest changed")
    if corridor["closest_parent_interval_record"] != closest[1]:
        raise AssertionError("closest parent interval changed")
    if corridor["parent_interval_record_count"] != 1_400:
        raise AssertionError("parent interval count changed")
    if corridor["parent_brackets_per_macrobox"] != 70:
        raise AssertionError("parent bracket census changed")
    sign_digest = hashlib.sha256(
        b"diag3-triple-frontier-parent-sign-vector-v1\0"
        + bytes(int(value > 0) for value in base_parent_signs)
    ).hexdigest()
    if corridor["common_parent_sign_vector_sha256"] != sign_digest:
        raise AssertionError("parent sign vector digest changed")

    lowers = [Fraction(row["projection_minor_interval"][0]) for row in all_projection_records]
    uppers = [Fraction(row["projection_minor_interval"][1]) for row in all_projection_records]
    if corridor["projection_interval_envelope"] != [encoded(min(lowers)), encoded(max(uppers))]:
        raise AssertionError("projection interval envelope changed")
    if max(uppers) >= 0:
        raise AssertionError("projection minor is not sign-definite on the corridor")

    union_bounds = [
        [
            encoded(min(center[index] - radius for center in accepted_centers)),
            encoded(max(center[index] + radius for center in accepted_centers)),
        ]
        for index in range(9)
    ]
    if corridor["union_coordinate_bounds"] != union_bounds:
        raise AssertionError("corridor union bounds changed")
    if (
        corridor["geometric_outer_facets"],
        corridor["macro_adjacency_seams"],
        corridor["intra_macro_subdivision_seams"],
        corridor["all_parent_brackets_same_sign"],
    ) != (18, 19, 15, True):
        raise AssertionError("corridor partition accounting changed")

    fixed_projection = candidate["fixed_projection"]
    if fixed_projection != {
        "fiber_columns_zero_based": [3, 4, 7],
        "fiber_variables": ["d", "e", "h"],
        "projection_minor_terms": 147,
        "projection_minor_sha256": base.polynomial_digest(
            b"diag3-local-projection-minor-v1", projection_minor
        ),
        "projection_minor_sign": -1,
    }:
        raise AssertionError("fixed projection accounting changed")

    return center0, radius, parent_brackets, base_parent_signs


def verify_frontier(candidate, center0, radius, parent_brackets, base_parent_signs):
    frontier = candidate["frontier"]
    center = list(center0)
    center[0] -= 40 * radius
    center = tuple(center)
    failures = []
    for index, (label, polynomial) in enumerate(parent_brackets):
        interval = base.direct_interval(polynomial, center, radius)
        sign = base.interval_sign(interval)
        if sign != base_parent_signs[index]:
            failures.append((label, polynomial, interval, sign))
    if len(failures) != 1 or failures[0][0] != "3468":
        raise AssertionError("first parent frontier changed")
    label, polynomial, interval, sign = failures[0]
    if polynomial != {
        (0, 0, 0, 0, 0, 0, 1, 0, 0): Fraction(1),
        (1, 0, 0, 0, 0, 0, 0, 0, 0): Fraction(-1),
    }:
        raise AssertionError("[3468] is no longer g-a")
    bounds = macro_bounds(center, radius)
    vertices = []
    for bits in product((0, 1), repeat=9):
        point = tuple(bound[bit] for bound, bit in zip(bounds, bits, strict=True))
        vertices.append((base.evaluate(polynomial, point), bits, point))
    minimum = min(vertices, key=lambda row: (row[0], row[1]))
    maximum = max(vertices, key=lambda row: (row[0], row[1]))
    if (minimum[0], maximum[0]) != (Fraction(-11, 448), Fraction(3, 448)):
        raise AssertionError("frontier vertex range changed")
    interpolation = -minimum[0] / (maximum[0] - minimum[0])
    wall_point = tuple(
        left + interpolation * (right - left)
        for left, right in zip(minimum[2], maximum[2], strict=True)
    )
    if base.evaluate(polynomial, wall_point):
        raise AssertionError("frontier wall witness is not exact")
    expected_crossing = {
        "label": label,
        "terms": len(polynomial),
        "polynomial_sha256": base.polynomial_digest(
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
        "opposite_vertex_signs": True,
        "zero_segment_parameter": encoded(interpolation),
        "exact_parent_wall_point": [encoded(value) for value in wall_point],
    }
    if frontier != {
        "kind": "FIRST_EXACT_PARENT_WALL_INTERSECTION",
        "macro_index": 20,
        "center": [encoded(value) for value in center],
        "radius": encoded(radius),
        "same_sign_parent_brackets": 69,
        "failed_parent_brackets": [expected_crossing],
        "projection_test_after_parent_failure": "NOT_RUN_BY_STOP_RULE",
    }:
        raise AssertionError("frontier certificate changed")


def verify_scope(candidate):
    if candidate["topological_consequence"] != (
        "Every connected component of the named triple-zero set restricted to the "
        "accepted 20-macrobox rectangular corridor meets one of the 18 geometric "
        "outer facets; the component through the registered exact zero is nonvacuous."
    ):
        raise AssertionError("topological consequence changed")
    if candidate["scope_and_nonconsequences"] != {
        "complete_named_factor_orbits_closed": 0,
        "global_parent_cell_coverage_claimed": False,
        "s8_transport_claimed": False,
        "genuine_parent_infinity_reached": False,
        "artificial_outer_facets": 18,
        "unresolved_triple_orbits_before": RESIDUE_COUNT,
        "unresolved_triple_orbits_after": RESIDUE_COUNT,
        "score_before": "2/9",
        "score_after": "2/9",
    }:
        raise AssertionError("scope or theorem accounting changed")
    if candidate["canaries"] != {
        "positive_base_box_replayed": True,
        "positive_first_adjacent_box_certified": True,
        "null_first_parent_wall_frontier_stops_extension": True,
        "negative_compact_sphere_projection_sign_refused": True,
        "hostile_mutations_declared": HOSTILE_MUTATIONS,
    }:
        raise AssertionError("canary declaration changed")


def verify_candidate(candidate):
    if candidate["schema"] != SCHEMA:
        raise AssertionError("schema changed")
    if candidate["status"] != "PROVED_MULTIBOX_LOCAL_BOUNDARY_COVERAGE_WITH_PARENT_WALL_FRONTIER":
        raise AssertionError("status changed")
    if candidate["track_id"] != "cycle-20260828-prover-triple-frontier":
        raise AssertionError("track id changed")
    if candidate["base_revision"] != BASE_REVISION:
        raise AssertionError("base revision changed")
    verify_source_accounting(candidate)
    replay = reconstruct_corridor(candidate)
    verify_frontier(candidate, *replay)
    verify_scope(candidate)
    if candidate["semantic_sha256"] != semantic_digest(candidate):
        raise AssertionError("semantic digest changed")
    expected_keys = {
        "schema", "status", "track_id", "base_revision", "branch_selection",
        "authenticated_sources", "fixed_projection", "corridor", "frontier",
        "topological_consequence", "scope_and_nonconsequences", "canaries",
        "semantic_sha256",
    }
    if set(candidate) != expected_keys:
        raise AssertionError("top-level schema changed")


def resign(candidate):
    candidate["semantic_sha256"] = semantic_digest(candidate)


def verify_hostile_mutations(certificate):
    mutations = []

    def add(name, mutate):
        candidate = deepcopy(certificate)
        mutate(candidate)
        resign(candidate)
        mutations.append((name, candidate))

    add("accepted_macrobox_count", lambda row: row["corridor"].__setitem__("accepted_macrobox_count", 21))
    add("corridor_axis", lambda row: row["branch_selection"].__setitem__("chosen_axis_zero_based", 1))
    add("subdivision_axis", lambda row: row["corridor"]["macroboxes"][14].__setitem__("subdivision_axis_zero_based", 0))
    add("projection_interval", lambda row: row["corridor"]["projection_records"][0].__setitem__("projection_minor_interval", ["-1", "1"]))
    add("parent_record_digest", lambda row: row["corridor"].__setitem__("parent_interval_record_sha256", "0" * 64))
    add("frontier_factor", lambda row: row["frontier"]["failed_parent_brackets"][0].__setitem__("label", "3467"))
    add("frontier_zero_witness", lambda row: row["frontier"]["failed_parent_brackets"][0]["exact_parent_wall_point"].__setitem__(0, "-1"))
    add("global_parent_coverage_claim", lambda row: row["scope_and_nonconsequences"].__setitem__("global_parent_cell_coverage_claimed", True))
    add("unresolved_count_reduction", lambda row: row["scope_and_nonconsequences"].__setitem__("unresolved_triple_orbits_after", RESIDUE_COUNT - 1))
    add("theorem_score", lambda row: row["scope_and_nonconsequences"].__setitem__("score_after", "3/9"))
    if [name for name, _row in mutations] != HOSTILE_MUTATIONS:
        raise AssertionError("hostile mutation ordering changed")
    for name, candidate in mutations:
        try:
            verify_candidate(candidate)
        except (AssertionError, KeyError, TypeError, ValueError):
            continue
        raise AssertionError(f"hostile mutation accepted: {name}")
    return len(mutations)


def compact_sphere_negative_canary():
    pivot = {(1, 0, 0): Fraction(2)}
    interval = base.direct_interval(
        pivot, (Fraction(0), Fraction(0), Fraction(0)), Fraction(1)
    )
    if interval != (Fraction(-2), Fraction(2)) or base.interval_sign(interval):
        raise AssertionError("compact sphere received a false projection certificate")


def main():
    certificate = json.loads(CERTIFICATE.read_text(encoding="utf-8"))
    verify_candidate(certificate)
    rejected = verify_hostile_mutations(certificate)
    compact_sphere_negative_canary()
    print("PASS independent deterministic 20-macrobox / 35-certificate-box replay")
    print("PASS parent signs: 1400/1400 strict on accepted corridor")
    print("PASS fixed projection minor: 35/35 exact intervals strictly negative")
    print("PASS exact first frontier: macrobox 20 intersects parent wall [3468]=g-a")
    print("PASS boundary accounting: 18 outer facets / 19 macro seams / 15 split seams")
    print("PASS compact-sphere negative canary refused")
    print(f"PASS hostile mutations rejected {rejected}/{rejected}")
    print("THEOREM every restricted component meets the 20-macrobox corridor boundary")
    print("SCOPE no complete orbit; unresolved=1162302; score=2/9")


if __name__ == "__main__":
    main()
