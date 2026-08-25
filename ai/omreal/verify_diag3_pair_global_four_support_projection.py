#!/usr/bin/env python3
"""Independent replay of the four-support cube/fiber projection preflight."""

from __future__ import annotations

from copy import deepcopy
from fractions import Fraction
import json
from pathlib import Path
import sys


HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import diag3_pair_global_four_support_projection_core as producer  # noqa: E402


CERTIFICATE = HERE / "data" / "DIAG3_PAIR_GLOBAL_FOUR_SUPPORT_PROJECTION.json"


def require(condition, message):
    if not condition:
        raise AssertionError(message)


def parse_polynomial(rows):
    return {
        tuple(row["exponent"]): Fraction(row["coefficient"])
        for row in rows
    }


def validate(candidate, expected):
    require(candidate == expected, "stored projection certificate does not replay")
    require(candidate["format"] == producer.FORMAT, "wrong format")
    require(candidate["status"] == "PROVED", "wrong proof status")
    scope = candidate["scope"]
    require(scope["cube_parameterization"] == "INTERIOR_BIJECTION_WITH_TOP_FACE_COLLAPSED_TO_APEX", "cube map scope")
    require(scope["fiber_projection_family"] == "COMPLETE_FOR_THE_22_ACTIVE_WALL_POLYNOMIALS", "projection completeness")
    require(scope["base_sign_invariant_cad"] == "NOT_YET_CONSTRUCTED", "false CAD claim")
    require(scope["global_parent_cell_coverage"] == "NOT_CLAIMED", "false global claim")
    require(scope["honest_9dvl_score"] == "2/9", "dishonest score")
    require(candidate["cube_map"]["boundary_factor_census"] == {"t=1": 19}, "cube boundary factors")
    require(candidate["cube_map"]["distinct_transformed_walls"] == 22, "transformed wall count")
    fibers = candidate["fiber_walls"]
    require({key: fibers[key] for key in ("independent_of_v", "linear_in_v", "quadratic_in_v", "higher_degree_in_v")} == {
        "independent_of_v": 1,
        "linear_in_v": 20,
        "quadratic_in_v": 1,
        "higher_degree_in_v": 0,
    }, "fiber degree census")
    require(len(fibers["catalog"]) == 22, "fiber catalog")
    projection = candidate["projection"]
    require(projection["raw_nonzero_polynomial_count"] == 255, "raw projection count")
    require(projection["raw_kind_census"] == {
        "coefficient": 44,
        "linear_linear_resultant": 190,
        "linear_quadratic_resultant": 20,
        "quadratic_discriminant": 1,
    }, "projection-kind census")
    require(projection["identically_zero_pair_resultants"] == 0, "zero pair resultant")
    require(projection["distinct_boundary_reduced_polynomial_count"] == 136, "distinct projection count")
    require(candidate["resource_effect"]["actual_distinct_projection_polynomials"] == 136, "resource count")
    require(candidate["resource_effect"]["ceiling_not_triggered"] is True, "projection ceiling")


def independent_cube_map_replay():
    tested = 0
    for denominator in (4, 8, 16):
        for u_index in range(denominator + 1):
            for t_index in range(denominator):
                for v_index in range(denominator + 1):
                    u = Fraction(u_index, denominator)
                    t = Fraction(t_index, denominator)
                    v = Fraction(v_index, denominator)
                    a = t + (1 - t) * u
                    g = t
                    h = t + (1 - t) * v
                    require(0 <= g <= a <= 1 and 0 <= g <= h <= 1, "cube point left pyramid")
                    require((a - g) / (1 - g) == u, "u inverse failed")
                    require((h - g) / (1 - g) == v, "v inverse failed")
                    tested += 1
    return tested


def independent_fiber_degree_replay(record):
    census = {0: 0, 1: 0, 2: 0}
    keys = set()
    for row in record["fiber_walls"]["catalog"]:
        polynomial = parse_polynomial(row["polynomial"])
        degree = max(exponent[2] for exponent in polynomial)
        require(degree == row["fiber_degree"], "stored fiber degree changed")
        require(degree <= 2, "fiber degree exceeds two")
        census[degree] += 1
        key = tuple(sorted(producer.canonical(polynomial).items()))
        require(key not in keys, "duplicate transformed fiber wall")
        keys.add(key)
    require(census == {0: 1, 1: 20, 2: 1}, "independent fiber census")
    return len(keys)


def main():
    stored = json.loads(CERTIFICATE.read_text())
    expected = producer.build_record()
    validate(stored, expected)
    points = independent_cube_map_replay()
    walls = independent_fiber_degree_replay(stored)

    mutations = []
    for path, value in (
        (("scope", "cube_parameterization"), "SAMPLED"),
        (("scope", "base_sign_invariant_cad"), "COMPLETE"),
        (("scope", "global_parent_cell_coverage"), "COMPLETE"),
        (("scope", "honest_9dvl_score"), "3/9"),
        (("cube_map", "boundary_factor_census", "t=1"), 18),
        (("cube_map", "distinct_transformed_walls"), 21),
        (("fiber_walls", "linear_in_v"), 21),
        (("fiber_walls", "higher_degree_in_v"), 1),
        (("projection", "identically_zero_pair_resultants"), 1),
        (("projection", "distinct_boundary_reduced_polynomial_count"), 135),
        (("projection", "catalog_sha256"), "0" * 64),
        (("resource_effect", "ceiling_not_triggered"), False),
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
    require(rejected == len(mutations), "a hostile projection mutation survived")

    print("PASS cube/pyramid interior bijection on", points, "exact rational points")
    print("PASS", walls, "walls: 1 base-only + 20 linear fibers + 1 quadratic fiber")
    print("PASS 255 projection obligations -> 136 distinct boundary-reduced polynomials")
    print("PASS projection ceiling not triggered")
    print(f"PASS {rejected}/{len(mutations)} hostile mutations rejected")
    print("SCOPE projection preflight only; base CAD, lifted cells, and global pair complex remain open; honest 9DVL 2/9")


if __name__ == "__main__":
    main()
