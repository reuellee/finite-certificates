#!/usr/bin/env python3
"""Standard-library replay of simple-crossing algebraic section lifts."""

from __future__ import annotations

from collections import Counter, defaultdict
from fractions import Fraction
import gzip
from hashlib import sha256
import json
from pathlib import Path
import sys


HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import verify_diag3_pair_global_four_support_base_projection as projection_replay  # noqa: E402


BASE = HERE / "data" / "DIAG3_PAIR_GLOBAL_FOUR_SUPPORT_BASE_PROJECTION.json.gz"
ROOTS = HERE / "data" / "DIAG3_PAIR_GLOBAL_FOUR_SUPPORT_ROOT_ISOLATION.json.gz"
OPEN = HERE / "data" / "DIAG3_PAIR_GLOBAL_FOUR_SUPPORT_OPEN_SECTOR_LIFT.json"
CERTIFICATE = HERE / "data" / "DIAG3_PAIR_GLOBAL_FOUR_SUPPORT_SIMPLE_SECTION_LIFT.json"
FORMAT = "diag3-pair-global-row2599-four-support-simple-section-lift-v1"


def require(condition, message):
    if not condition:
        raise AssertionError(message)


def digest(value):
    return sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":")).encode("ascii")
    ).hexdigest()


def load_sequences(manifest):
    sectors = []
    for row in manifest["artifact_shards"]["shards"]:
        compressed = (OPEN.parent / row["path"]).read_bytes()
        require(len(compressed) == row["bytes"], "open-sector shard bytes")
        require(sha256(compressed).hexdigest() == row["sha256"], "open-sector shard digest")
        shard = json.loads(gzip.decompress(compressed))
        require(shard["sector_start"] == len(sectors), "open-sector shard coverage")
        sectors.extend(shard["sectors"])
    require(digest(sectors) == manifest["open_sector_lift"]["sectors_sha256"], "open-sector sequence digest")
    return [[entry[0] for entry in sector] for sector in sectors]


def transition_window(left, right):
    prefix = 0
    while prefix < min(len(left), len(right)) and left[prefix] == right[prefix]:
        prefix += 1
    suffix = 0
    while (
        suffix < min(len(left) - prefix, len(right) - prefix)
        and left[-1 - suffix] == right[-1 - suffix]
    ):
        suffix += 1
    return (
        prefix,
        left[prefix : len(left) - suffix if suffix else len(left)],
        right[prefix : len(right) - suffix if suffix else len(right)],
    )


def factorization_for(key, projection_index, rows):
    require(key in projection_index, "projection obligation missing")
    row = rows[projection_index[key]]
    return {factor["id"]: factor["multiplicity"] for factor in row["factors"]}


def strip_raw_boundary(polynomial):
    polynomial = projection_replay.primitive_univariate(polynomial)
    while polynomial[0] == 0:
        polynomial = polynomial[1:]
    while sum(polynomial) == 0:
        polynomial = projection_replay.primitive_univariate(
            projection_replay.polynomial_divide_exact(polynomial, [-1, 1])
        )
    return polynomial


def factor_multiplicity(polynomial, factor):
    polynomial = [Fraction(value) for value in polynomial]
    factor = [Fraction(value) for value in factor]
    multiplicity = 0
    while True:
        quotient, remainder = projection_replay.divide_over_q(polynomial, factor)
        if remainder != [0]:
            return multiplicity
        polynomial = quotient
        multiplicity += 1


def validate_claims(candidate, observed):
    require(candidate["format"] == FORMAT, "wrong certificate format")
    require(candidate["status"] == "PROVED", "wrong proof status")
    scope = candidate["scope"]
    require(scope["simple_transversal_algebraic_t_section_lifts"] == "COMPLETE", "false simple-section scope")
    require(scope["remaining_algebraic_t_section_lifts"] == "NOT_YET_CONSTRUCTED", "false remaining scope")
    require(scope["v_fiber_lift"] == "NOT_YET_CONSTRUCTED", "false fiber scope")
    require(scope["global_parent_cell_coverage"] == "NOT_CLAIMED", "false global scope")
    require(scope["honest_9dvl_score"] == "2/9", "dishonest theorem score")
    require(candidate["source"]["base_projection_semantic_sha256"] == observed["base_semantic"], "base source")
    require(candidate["source"]["root_isolation_semantic_sha256"] == observed["root_semantic"], "root source")
    require(candidate["source"]["open_sector_lift_semantic_sha256"] == observed["open_semantic"], "open source")
    lift = candidate["simple_section_lift"]
    require(lift["simple_transversal_crossing_sections"] == 1_022, "crossing count")
    require(lift["resultant_multiplicity_one_sections"] == 1_022, "resultant multiplicity")
    require(lift["sections_with_nonresultant_event"] == 0, "exceptional event")
    require(lift["section_u_root_points"] == 84_794, "section root points")
    require(lift["section_u_strips"] == 85_816, "section strips")
    require(lift["section_base_cells"] == 170_610, "section cells")
    require(lift["minimum_adjacent_sector_root_count"] == 54, "minimum roots")
    require(lift["maximum_adjacent_sector_root_count"] == 109, "maximum roots")
    require(lift["crossings_sha256"] == observed["crossings_digest"], "crossing digest")
    require(candidate["remaining_frontier"] == {"remaining_algebraic_t_sections": 671, "census": {"complex_same_count_transition": 251, "no_visible_stack_change": 406, "root_count_change": 14}}, "remaining frontier")
    require(candidate["semantic_sha256"] == observed["semantic"], "semantic digest")
    require(candidate["resource_effect"]["ceiling_not_triggered"] is True, "cell ceiling")


def main():
    base = json.loads(gzip.decompress(BASE.read_bytes()))
    roots = json.loads(gzip.decompress(ROOTS.read_bytes()))
    open_lift = json.loads(OPEN.read_bytes())
    stored = json.loads(CERTIFICATE.read_bytes())
    require(roots["source"]["semantic_sha256"] == base["semantic_sha256"], "root source chain")
    require(open_lift["source"]["root_isolation_semantic_sha256"] == roots["semantic_sha256"], "open source chain")

    base_catalog = [
        projection_replay.parse_bivariate(row["polynomial"])
        for row in base["base_factorization"]["catalog"]
    ]
    coefficient_rows = [
        projection_replay.coefficients_in_u(polynomial)
        for polynomial in base_catalog
    ]
    unique_projection, _kind_census, _pair_count, zero_resultants = (
        projection_replay.reconstruct_projection(base_catalog)
    )
    require(zero_resultants == 0, "zero source resultant")
    projection_index = {key: index for index, key in enumerate(unique_projection)}
    factorization_rows = base["second_projection"]["factorizations"]
    univariate_factors = [
        row["coefficients_low_to_high"]
        for row in base["second_projection"]["catalog"]
    ]

    exceptional = defaultdict(set)
    for base_id, rows in enumerate(coefficient_rows):
        for polynomial in rows:
            key = projection_replay.strip_square_boundary_squarefree(polynomial)
            if key is not None:
                for factor_id in factorization_for(key, projection_index, factorization_rows):
                    exceptional[factor_id].add("coefficient")
        if len(rows) >= 3:
            key = projection_replay.strip_square_boundary_squarefree(
                projection_replay.discriminant(rows)
            )
            if key is not None:
                for factor_id in factorization_for(key, projection_index, factorization_rows):
                    exceptional[factor_id].add("discriminant")
    for row in open_lift["bounded_u_boundary_audit"]["factorizations"]:
        for factor in row["factors"]:
            exceptional[factor["id"]].add("u1_boundary")

    sequences = load_sequences(open_lift)
    section_rows = roots["root_isolation"]["sections"]
    observed_crossings = []
    remaining_census = Counter()
    total_root_points = 0
    total_strips = 0
    resultant_cache = {}
    for section_id, (section, left, right) in enumerate(
        zip(section_rows, sequences[:-1], sequences[1:], strict=True)
    ):
        position, left_window, right_window = transition_window(left, right)
        simple = (
            len(left_window) == len(right_window) == 2
            and left_window == list(reversed(right_window))
            and left_window[0] != left_window[1]
        )
        if not simple:
            if left == right:
                remaining_census["no_visible_stack_change"] += 1
            elif len(left) == len(right):
                remaining_census["complex_same_count_transition"] += 1
            else:
                remaining_census["root_count_change"] += 1
            continue
        pair = tuple(sorted(left_window))
        if pair not in resultant_cache:
            resultant_cache[pair] = strip_raw_boundary(
                projection_replay.sylvester_resultant(
                    coefficient_rows[pair[0]], coefficient_rows[pair[1]]
                )
            )
        projection_factor_id = section["factor_id"]
        require(
            factor_multiplicity(
                resultant_cache[pair], univariate_factors[projection_factor_id]
            )
            == 1,
            "crossing resultant is not simple",
        )
        require(not exceptional[projection_factor_id], "crossing has nonresultant event")
        root_count = len(left)
        total_root_points += root_count - 1
        total_strips += root_count
        observed_crossings.append(
            [
                section_id,
                projection_factor_id,
                section["factor_root_index"],
                position,
                left_window[0],
                left_window[1],
                root_count,
            ]
        )

    require(observed_crossings == stored["simple_section_lift"]["crossings"], "crossing rows")
    require(total_root_points == 84_794 and total_strips == 85_816, "section cell totals")
    require(dict(sorted(remaining_census.items())) == stored["remaining_frontier"]["census"], "remaining census")
    observed = {
        "base_semantic": base["semantic_sha256"],
        "root_semantic": roots["semantic_sha256"],
        "open_semantic": open_lift["semantic_sha256"],
        "crossings_digest": digest(observed_crossings),
        "semantic": digest(
            {
                "base_projection_semantic_sha256": base["semantic_sha256"],
                "root_isolation_semantic_sha256": roots["semantic_sha256"],
                "open_sector_lift_semantic_sha256": open_lift["semantic_sha256"],
                "crossings": observed_crossings,
            }
        ),
    }
    validate_claims(stored, observed)

    mutations = (
        (("status",), "OPEN"),
        (("scope", "simple_transversal_algebraic_t_section_lifts"), "PARTIAL"),
        (("scope", "remaining_algebraic_t_section_lifts"), "COMPLETE"),
        (("scope", "honest_9dvl_score"), "3/9"),
        (("source", "open_sector_lift_semantic_sha256"), "0" * 64),
        (("simple_section_lift", "simple_transversal_crossing_sections"), 1_021),
        (("simple_section_lift", "resultant_multiplicity_one_sections"), 1_021),
        (("simple_section_lift", "sections_with_nonresultant_event"), 1),
        (("simple_section_lift", "section_base_cells"), 170_609),
        (("simple_section_lift", "crossings_sha256"), "0" * 64),
        (("semantic_sha256",), "0" * 64),
        (("resource_effect", "ceiling_not_triggered"), False),
    )
    rejected = 0
    for path, value in mutations:
        target = stored
        for key in path[:-1]:
            target = target[key]
        original = target[path[-1]]
        target[path[-1]] = value
        try:
            validate_claims(stored, observed)
        except AssertionError:
            rejected += 1
        finally:
            target[path[-1]] = original
    require(rejected == len(mutations), "a hostile simple-section mutation survived")

    print("PASS 1022 simple adjacent swaps -> multiplicity-one swapped-pair resultants")
    print("PASS zero coefficient/discriminant/u=1 events on the simple crossing sections")
    print("PASS 84794 section root points + 85816 strips = 170610 algebraic-section cells")
    print("PASS remaining exact frontier: 406 unchanged + 251 complex + 14 count-changing = 671")
    print(f"PASS {rejected}/{len(mutations)} hostile mutations rejected")
    print("SCOPE simple transversal algebraic sections only; 671 sections and global pair complex remain open; honest 9DVL 2/9")


if __name__ == "__main__":
    main()
