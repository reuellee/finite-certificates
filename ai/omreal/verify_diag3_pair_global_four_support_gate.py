#!/usr/bin/env python3
"""Independent replay of the first-four-support parent and wall gate."""

from __future__ import annotations

from copy import deepcopy
from fractions import Fraction
import json
from pathlib import Path
import sys


HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import diag3_pair_global_four_support_core as producer  # noqa: E402
import verify_diag3_pair_global_parent_face_gate as gate  # noqa: E402
from exact_semialgebraic import evaluate  # noqa: E402


CERTIFICATE = HERE / "data" / "DIAG3_PAIR_GLOBAL_FOUR_SUPPORT_GATE.json"


def parse_polynomial(rows):
    return {
        tuple(row["exponent"]): Fraction(row["coefficient"])
        for row in rows
    }


def require(condition, message):
    if not condition:
        raise AssertionError(message)


def validate(candidate, expected):
    require(candidate == expected, "stored four-support certificate does not replay")
    require(candidate["format"] == producer.FORMAT, "wrong format")
    require(candidate["status"] == "PROVED", "proof status changed")
    scope = candidate["scope"]
    require(scope["parent_parameter_coverage"] == "COMPLETE_ON_BOTH_FIRST_FOUR_SUPPORT_PARENT_CLOSURES", "parent coverage")
    require(scope["residual_interior_feasibility"] == "COMPLETE_ON_BOTH_SQUARE_PYRAMIDS", "residual feasibility")
    require(scope["residual_arrangement_cellulation"] == "NOT_YET_CONSTRUCTED", "false arrangement claim")
    require(scope["global_parent_cell_coverage"] == "NOT_CLAIMED", "false global claim")
    require(scope["honest_9dvl_score"] == "2/9", "dishonest score")

    pyramid = candidate["common_square_pyramid"]
    require(pyramid["tetrahedron_count"] == 2, "tetrahedron count")
    require(pyramid["boundary_facets"] == ["g=0", "a=1", "h=1", "a=g", "h=g"], "facet census")
    require([row["parent_dimension"] for row in candidate["parent_domains"]] == [3, 3], "parent dimensions")
    require([row["equality"] for row in candidate["parent_domains"]] == ["g=i", "d=g"], "parent equalities")

    rows = candidate["support_residual_analyses"]
    require([row["ambient_mixed_residual_restrictions"] for row in rows] == [3_996, 4_021], "mixed restrictions")
    require([row["parent_equality_state_census"] for row in rows] == [
        {"identically_zero": 548, "one_signed": 27, "mixed": 3_421},
        {"identically_zero": 656, "one_signed": 29, "mixed": 3_336},
    ], "parent-equality census")
    require([row["interior_class_census"] for row in rows] == [
        {"empty": 43, "nonempty": 25, "unresolved": 0},
        {"empty": 24, "nonempty": 16, "unresolved": 0},
    ], "interior class census")
    require([row["interior_factor_census"] for row in rows] == [
        {"empty": 3_093, "nonempty": 328},
        {"empty": 3_139, "nonempty": 197},
    ], "interior factor census")

    combined = candidate["combined_compression"]
    require(combined["ambient_mixed_restrictions"] == 8_017, "combined mixed count")
    require(combined["distinct_parent_reduced_zero_sets"] == 94, "parent-reduced zero sets")
    require(combined["common_parent_reduced_zero_sets"] == 14, "common zero sets")
    require(combined["distinct_active_remainders_before_positive_quotient"] == 26, "active remainder count")
    require(combined["distinct_active_walls_after_positive_quotient"] == 22, "active wall count")
    require(combined["common_active_walls_after_positive_quotient"] == 4, "common active walls")
    require(combined["active_interior_factor_union_count"] == 436, "active factor union")
    require(combined["unresolved_interior_zero_sets"] == 0, "unresolved interior walls")
    require(len(candidate["active_wall_catalog"]) == 22, "active wall catalog")


def independent_pyramid_replay(record):
    """Replay the exact two-tetrahedron coverage formulas."""

    tetrahedra = record["common_square_pyramid"]["tetrahedra"]
    expected = [
        [["0", "0", "0"], ["1", "0", "0"], ["1", "0", "1"], ["1", "1", "1"]],
        [["0", "0", "0"], ["0", "0", "1"], ["1", "0", "1"], ["1", "1", "1"]],
    ]
    require(tetrahedra == expected, "pyramid tetrahedra changed")
    tested = 0
    for denominator in (4, 8, 16):
        for g_index in range(denominator + 1):
            for a_index in range(g_index, denominator + 1):
                for h_index in range(g_index, denominator + 1):
                    a = Fraction(a_index, denominator)
                    g = Fraction(g_index, denominator)
                    h = Fraction(h_index, denominator)
                    if a >= h:
                        weights = (1 - a, a - h, h - g, g)
                        vertices = producer.PYRAMID_TETRAHEDRA[0]
                    else:
                        weights = (1 - h, h - a, a - g, g)
                        vertices = producer.PYRAMID_TETRAHEDRA[1]
                    require(all(value >= 0 for value in weights), "negative barycentric weight")
                    require(sum(weights) == 1, "barycentric weights do not sum to one")
                    reconstructed = tuple(
                        sum(weights[index] * vertices[index][axis] for index in range(4))
                        for axis in range(3)
                    )
                    require(reconstructed == (a, g, h), "pyramid point not reconstructed")
                    tested += 1
    return tested


def independent_parent_equality_replay(record):
    records = [json.loads(line) for line in gate.CATALOG.read_text().splitlines() if line]
    parents, _digest = gate.parent_polynomials(records[gate.PARENT])
    by_label = {label: (target, polynomial) for label, target, polynomial, _terms in parents}
    claims = (
        ((3, 1, 15), "1358", "3578", 6, 8),
        ((3, 3, 7), "3478", "3578", 6, 3),
    )
    for face, positive_label, negative_label, left_axis, right_axis in claims:
        restricted = []
        for label in (positive_label, negative_label):
            target, polynomial = by_label[label]
            value = producer.restrict(polynomial, face)
            restricted.append({term: target * coefficient for term, coefficient in value.items()})
        first = restricted[0]
        second = restricted[1]
        require(first == {tuple(int(index == left_axis) for index in range(9)): 1, tuple(int(index == right_axis) for index in range(9)): -1}, f"first equality bracket changed: {face}")
        require(second == {term: -coefficient for term, coefficient in first.items()}, f"opposite equality bracket changed: {face}")
    require([row["parent_brackets_replayed"] for row in record["parent_domains"]] == [70, 70], "parent replay count")


def independent_active_wall_witnesses(record):
    points = tuple(
        (Fraction(a, 16), Fraction(g, 16), Fraction(h, 16))
        for g in range(1, 16)
        for a in range(g + 1, 16)
        for h in range(g + 1, 16)
    )
    keys = set()
    for row in record["active_wall_catalog"]:
        polynomial = parse_polynomial(row["polynomial"])
        key = tuple(sorted(producer.canonical(polynomial).items()))
        require(key not in keys, "duplicate active wall")
        keys.add(key)
        signs = set()
        for point in points:
            value = evaluate(polynomial, point)
            signs.add(1 if value > 0 else -1 if value < 0 else 0)
        require(0 in signs or {-1, 1} <= signs, "active wall lacks exact strict-interior witness")
    return len(keys)


def main():
    stored = json.loads(CERTIFICATE.read_text())
    expected = producer.build_record()
    validate(stored, expected)
    grid_points = independent_pyramid_replay(stored)
    independent_parent_equality_replay(stored)
    active = independent_active_wall_witnesses(stored)

    mutations = []
    for path, value in (
        (("scope", "parent_parameter_coverage"), "SAMPLED"),
        (("scope", "residual_arrangement_cellulation"), "COMPLETE"),
        (("scope", "global_parent_cell_coverage"), "COMPLETE"),
        (("scope", "honest_9dvl_score"), "3/9"),
        (("common_square_pyramid", "tetrahedron_count"), 1),
        (("parent_domains", 0, "parent_dimension"), 4),
        (("parent_domains", 1, "equality"), "NONE"),
        (("support_residual_analyses", 0, "ambient_mixed_residual_restrictions"), 3_995),
        (("support_residual_analyses", 1, "interior_class_census", "unresolved"), 1),
        (("combined_compression", "distinct_active_walls_after_positive_quotient"), 21),
        (("combined_compression", "active_wall_catalog_sha256"), "0" * 64),
        (("resource_contract", "maximum_atomic_tetrahedra"), 0),
    ):
        candidate = deepcopy(stored)
        target = candidate
        for key in path[:-1]:
            target = target[key]
        target[path[-1]] = value
        mutations.append(candidate)
    rejected = 0
    for candidate in mutations:
        try:
            validate(candidate, expected)
        except AssertionError:
            rejected += 1
    require(rejected == len(mutations), "a hostile mutation survived")

    print("PASS exact square-pyramid coverage on", grid_points, "independent rational points")
    print("PASS paired parent brackets force g=i and d=g")
    print("PASS 8017 mixed restrictions -> 94 parent-reduced zero sets ->", active, "active walls")
    print("PASS zero unresolved interior wall classes")
    print(f"PASS {rejected}/{len(mutations)} hostile mutations rejected")
    print("SCOPE first two parent-support closures only; arrangement and global pair complex remain open; honest 9DVL 2/9")


if __name__ == "__main__":
    main()
