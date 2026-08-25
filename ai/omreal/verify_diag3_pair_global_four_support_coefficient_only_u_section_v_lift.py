#!/usr/bin/env python3
"""Independent replay of the coefficient-only algebraic-u-section v lift."""

from __future__ import annotations

from collections import Counter, defaultdict
from copy import deepcopy
import gzip
from hashlib import sha256
import json
from pathlib import Path
import sys


HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import verify_diag3_pair_global_four_support_regular_u_section_v_lift as regular  # noqa: E402


PROJECTION = HERE / "data" / "DIAG3_PAIR_GLOBAL_FOUR_SUPPORT_PROJECTION.json"
BASE = HERE / "data" / "DIAG3_PAIR_GLOBAL_FOUR_SUPPORT_BASE_PROJECTION.json.gz"
OPEN = HERE / "data" / "DIAG3_PAIR_GLOBAL_FOUR_SUPPORT_OPEN_SECTOR_LIFT.json"
OPEN_V = HERE / "data" / "DIAG3_PAIR_GLOBAL_FOUR_SUPPORT_OPEN_CELL_V_LIFT.json"
REGULAR = HERE / "data" / "DIAG3_PAIR_GLOBAL_FOUR_SUPPORT_REGULAR_U_SECTION_V_LIFT.json"
ENDPOINT = HERE / "data" / "DIAG3_PAIR_GLOBAL_FOUR_SUPPORT_ENDPOINT_U_SECTION_V_LIFT.json"
CERTIFICATE = HERE / "data" / "DIAG3_PAIR_GLOBAL_FOUR_SUPPORT_COEFFICIENT_ONLY_U_SECTION_V_LIFT.json"

FORMAT = "diag3-pair-global-row2599-four-support-coefficient-only-u-section-v-lift-v1"
SHARD_FORMAT = (
    "diag3-pair-global-row2599-four-support-coefficient-only-u-section-v-lift-shard-v1"
)
OPEN_SHARD_FORMAT = "diag3-pair-global-row2599-four-support-open-sector-lift-shard-v1"
OPEN_V_SHARD_FORMAT = "diag3-pair-global-row2599-four-support-open-cell-v-lift-shard-v1"
SHARD_COUNT = 32
SECTOR_COUNT = 1_694
SECTION_COUNT = 132_134

COUNT_CHANGE = regular.COUNT_CHANGE
COEFFICIENT = regular.COEFFICIENT
ENDPOINT_REASON = regular.ENDPOINT
TARGET_REASON = COEFFICIENT

THEOREM_EFFECT = (
    "Exact unbounded degree-drop analysis completes 3388 additional "
    "coefficient-only algebraic-u v fibers and 79816 cells over open t sectors; "
    "4582 coefficient-plus-endpoint fibers, all algebraic-t v lifts, global "
    "gluing, labels, middle-rank replay, and diagonal three remain open; honest "
    "9DVL score remains 2/9."
)
NEXT_STAGE = (
    "resolve the 4582 coefficient-plus-endpoint u-section fibers, then lift all "
    "261571 base cells over algebraic t sections"
)


def require(condition, message):
    if not condition:
        raise AssertionError(message)


def digest(value):
    return sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":")).encode("ascii")
    ).hexdigest()


def canonical_gzip_json(value):
    encoded = (
        json.dumps(value, sort_keys=True, separators=(",", ":")) + "\n"
    ).encode("ascii")
    return gzip.compress(encoded, compresslevel=9, mtime=0)


def independent_coefficient_factor_map(events):
    answer = defaultdict(set)
    for factor_id, rows in events.items():
        for kind, owners, _multiplicity, _projection_id in rows:
            if kind == "coefficient":
                answer[tuple(owners)].add(factor_id)
    return {owner: tuple(sorted(factors)) for owner, factors in answer.items()}


def endpoint_factors(open_v):
    return {
        factor_id
        for row in open_v["v_endpoint_audit"]["factorizations"]
        for factor_id, _multiplicity in row["base_factors"]
    }


def classify(left, right, current_events, endpoint_factor_ids, factor_id):
    reason = 0
    if len(left) != len(right):
        reason |= COUNT_CHANGE
    if any(event[0] != "resultant" for event in current_events):
        reason |= COEFFICIENT
    if factor_id in endpoint_factor_ids:
        reason |= ENDPOINT_REASON
    return reason


def validate_degree_drop(
    factor_id,
    left,
    right,
    coefficient_event,
    coefficient_factors,
    wall_degrees,
    wall_coefficients,
):
    _kind, owners, multiplicity, _projection_id = coefficient_event
    wall_id, power = owners
    require(multiplicity == 1, "coefficient multiplicity")
    require(power == 1, "not a leading coefficient event")
    require(wall_degrees[wall_id] == 1, "not a linear wall")
    require(wall_coefficients[wall_id].get(0), "zero constant coefficient")
    require(
        regular.reduce_boundary(wall_coefficients[wall_id][0]),
        "constant coefficient is zero after boundary reduction",
    )
    constant_factors = coefficient_factors.get((wall_id, 0), ())
    require(
        factor_id not in constant_factors,
        "constant coefficient shares the degree-drop factor",
    )
    require(set(left) == set(right), "bounded branch-token set changed")
    token = (wall_id, 0)
    require(token not in set(left) and token not in set(right), "degree-drop root is bounded")
    return wall_id, power, constant_factors


def verify_invisible_resultants(tokens, event_owners, inversion_owners):
    bounded_walls = {token[0] for token in tokens}
    for owners, multiplicity in (event_owners - inversion_owners).items():
        require(
            not multiplicity or not set(owners) <= bounded_walls,
            "invisible resultant has both owners in the bounded stack",
        )


def string_census(counter):
    return {",".join(map(str, key)): value for key, value in sorted(counter.items())}


def replay(
    sectors,
    sector_ids,
    catalog,
    events,
    endpoint_factor_ids,
    coefficient_factors,
    wall_degrees,
    wall_coefficients,
):
    shards = [[] for _ in range(SHARD_COUNT)]
    factor_census = Counter()
    degree_drop_census = Counter()
    pattern_census = Counter()
    remaining_census = Counter()
    regular_sections = endpoint_sections = completed_sections = 0
    coefficient_events = resultants = inversions = groups = 0
    points = strips = 0

    for sector_id, (stack, identifiers) in enumerate(
        zip(sectors, sector_ids, strict=True)
    ):
        require(len(identifiers) == len(stack) + 1, "strip adjacency")
        completed = []
        remaining = []
        for root_index, root in enumerate(stack):
            factor_id = root[0]
            left = catalog[identifiers[root_index]]
            right = catalog[identifiers[root_index + 1]]
            current_events = events[factor_id]
            require(current_events, "section without raw event")
            require(all(event[2] == 1 for event in current_events), "non-simple raw event")
            reason = classify(
                left, right, current_events, endpoint_factor_ids, factor_id
            )
            if not reason:
                regular_sections += 1
                continue
            if reason == COUNT_CHANGE | ENDPOINT_REASON:
                endpoint_sections += 1
                continue
            if reason != TARGET_REASON:
                remaining.append([root_index, factor_id, reason])
                remaining_census[reason] += 1
                continue

            coefficient_rows = [
                event for event in current_events if event[0] == "coefficient"
            ]
            require(len(coefficient_rows) == 1, "multiple coefficient events")
            wall_id, power, constant_factors = validate_degree_drop(
                factor_id,
                left,
                right,
                coefficient_rows[0],
                coefficient_factors,
                wall_degrees,
                wall_coefficients,
            )
            edges = regular.inversions(left, right)
            collision_groups = regular.collision_components(edges)
            seen_owners = Counter(
                tuple(sorted((first[0], second[0])))
                for first, second in edges
            )
            permitted_owners = Counter(
                tuple(sorted(event[1]))
                for event in current_events
                if event[0] == "resultant"
            )
            regular.verify_inversion_owners(seen_owners, permitted_owners)
            verify_invisible_resultants(left, permitted_owners, seen_owners)
            section_points = len(left) - sum(
                len(component) - 1 for component in collision_groups
            )
            section_strips = section_points + 1
            group_sizes = tuple(sorted(len(component) for component in collision_groups))
            completed.append(
                [
                    root_index,
                    factor_id,
                    wall_id,
                    power,
                    list(constant_factors),
                    len(current_events) - 1,
                    len(edges),
                    len(collision_groups),
                    section_points,
                    section_strips,
                ]
            )
            completed_sections += 1
            factor_census[factor_id] += 1
            degree_drop_census[(factor_id, wall_id, power, constant_factors)] += 1
            pattern_census[
                (
                    factor_id,
                    len(left),
                    len(edges),
                    group_sizes,
                    section_points,
                    section_strips,
                )
            ] += 1
            coefficient_events += 1
            resultants += len(current_events) - 1
            inversions += len(edges)
            groups += len(collision_groups)
            points += section_points
            strips += section_strips

        shard_index = SHARD_COUNT * sector_id // SECTOR_COUNT
        shards[shard_index].append({"completed": completed, "remaining": remaining})

    require(regular_sections == 120_174, "prior regular sections")
    require(endpoint_sections == 3_990, "prior endpoint sections")
    require(completed_sections == 3_388, "coefficient-only count")
    require(sum(remaining_census.values()) == 4_582, "remaining count")
    require(
        regular_sections + endpoint_sections + completed_sections + sum(remaining_census.values()) == SECTION_COUNT,
        "complete section partition",
    )
    partition = [row for shard in shards for row in shard]
    return {
        "shards": shards,
        "partition_sha256": digest(partition),
        "factor_census": {str(key): value for key, value in sorted(factor_census.items())},
        "degree_drop_census": string_census(degree_drop_census),
        "pattern_census": string_census(pattern_census),
        "remaining_census": {str(key): value for key, value in sorted(remaining_census.items())},
        "completed_sections": completed_sections,
        "remaining_sections": sum(remaining_census.values()),
        "coefficient_events": coefficient_events,
        "resultants": resultants,
        "inversions": inversions,
        "groups": groups,
        "points": points,
        "strips": strips,
    }


def verify_shards(candidate, observed):
    manifest = candidate["artifact_shards"]
    require(manifest["format"] == SHARD_FORMAT, "shard format")
    require(manifest["shard_count"] == SHARD_COUNT, "shard count")
    require(len(manifest["shards"]) == SHARD_COUNT, "shard manifest rows")
    expected = []
    for index, sector_rows in enumerate(observed["shards"]):
        sector_start = SECTOR_COUNT * index // SHARD_COUNT
        sector_end = SECTOR_COUNT * (index + 1) // SHARD_COUNT
        shard = {
            "format": SHARD_FORMAT,
            "shard_index": index,
            "shard_count": SHARD_COUNT,
            "sector_start": sector_start,
            "sector_end": sector_end,
            "sectors": sector_rows,
        }
        expected_bytes = canonical_gzip_json(shard)
        name = (
            "DIAG3_PAIR_GLOBAL_FOUR_SUPPORT_COEFFICIENT_ONLY_U_SECTION_V_LIFT_"
            f"SHARD_{index:02d}_OF_{SHARD_COUNT}.json.gz"
        )
        actual_bytes = (CERTIFICATE.parent / name).read_bytes()
        require(actual_bytes == expected_bytes, "shard byte replay")
        expected.append(
            {
                "index": index,
                "path": name,
                "sector_start": sector_start,
                "sector_end": sector_end,
                "bytes": len(expected_bytes),
                "sha256": sha256(expected_bytes).hexdigest(),
            }
        )
    require(manifest["shards"] == expected, "shard manifest")
    return expected


def validate_claims(candidate, observed):
    require(candidate["format"] == FORMAT and candidate["status"] == "PROVED", "format/status")
    require(candidate["scope"] == {
        "open_t_coefficient_only_u_section_v_lift": "COMPLETE",
        "remaining_open_t_coefficient_endpoint_u_section_v_lift": "NOT_YET_CONSTRUCTED",
        "algebraic_t_section_v_lift": "NOT_YET_CONSTRUCTED",
        "global_gluing_and_closure_data": "NOT_CLAIMED",
        "honest_9dvl_score": "2/9",
    }, "scope")
    source = candidate["source"]
    for key in (
        "projection_semantic_sha256",
        "base_projection_semantic_sha256",
        "open_sector_lift_semantic_sha256",
        "open_cell_v_lift_semantic_sha256",
        "regular_u_section_semantic_sha256",
        "endpoint_u_section_semantic_sha256",
    ):
        require(source[key] == observed[key], f"source link {key}")
    require(source["prior_residual_sections"] == 7_970, "prior residue")
    lift = candidate["coefficient_only_u_section_v_lift"]
    require(lift["completed_sections"] == observed["completed_sections"] == 3_388, "completed")
    require(lift["remaining_sections"] == observed["remaining_sections"] == 4_582, "remaining")
    require(lift["completed_factor_census"] == observed["factor_census"] == {"27": 1_694, "38": 1_694}, "factor census")
    require(lift["degree_drop_census"] == observed["degree_drop_census"], "degree-drop census")
    require(lift["event_inversion_group_pattern_census"] == observed["pattern_census"], "pattern census")
    require(lift["simple_leading_coefficient_events"] == observed["coefficient_events"] == 3_388, "coefficients")
    require(lift["completed_raw_resultant_events"] == observed["resultants"] == 11_858, "resultants")
    require(lift["visible_inversion_edges"] == observed["inversions"] == 10_704, "inversions")
    require(lift["interior_collision_groups"] == observed["groups"] == 10_704, "groups")
    require(lift["section_v_root_points"] == observed["points"] == 38_214, "points")
    require(lift["section_open_v_strips"] == observed["strips"] == 41_602, "strips")
    require(lift["lifted_cells"] == observed["points"] + observed["strips"] == 79_816, "cells")
    require(lift["coefficient_factor_map_sha256"] == observed["coefficient_factor_map_sha256"], "coefficient map")
    require(lift["raw_event_map_sha256"] == observed["raw_event_map_sha256"], "event map")
    require(lift["partition_sha256"] == observed["partition_sha256"], "partition")
    require(lift["remaining_reason_census"] == observed["remaining_census"] == {"6": 1_694, "7": 2_888}, "remaining census")
    require(candidate["artifact_shards"] == observed["artifact_shards"], "artifact shards")
    require(candidate["semantic_sha256"] == observed["semantic_sha256"], "semantic digest")
    require(candidate["resource_effect"] == {
        "prior_residual_ceiling": 7_970,
        "sections_examined": 7_970,
        "ceiling_not_triggered": True,
        "next_stage": NEXT_STAGE,
    }, "resource effect")
    require(candidate["generator_dependency"]["independent_verifier"] == "STANDARD_LIBRARY_STRUCTURAL_REPLAY", "dependency")
    require(candidate["generator_dependency"]["python"].startswith("3.12."), "python version")
    require(candidate["theorem_effect"] == THEOREM_EFFECT, "theorem effect")


def main():
    candidate = json.loads(CERTIFICATE.read_bytes())
    projection = json.loads(PROJECTION.read_bytes())
    base = json.loads(gzip.decompress(BASE.read_bytes()))
    open_record = json.loads(OPEN.read_bytes())
    open_v = json.loads(OPEN_V.read_bytes())
    regular_record = json.loads(REGULAR.read_bytes())
    endpoint_record = json.loads(ENDPOINT.read_bytes())
    require(all(record["status"] == "PROVED" for record in (projection, base, open_record, open_v, regular_record, endpoint_record)), "source status")
    require(endpoint_record["endpoint_u_section_v_lift"]["remaining_sections"] == 7_970, "endpoint residue")
    regular.open_v_verifier.replay_endpoint_factorizations(projection, base, open_v)
    events, event_serial = regular.independent_event_map(projection, base)
    coefficient_factors = independent_coefficient_factor_map(events)
    coefficient_map_serial = [[list(owner), list(factors)] for owner, factors in sorted(coefficient_factors.items())]
    endpoint_factor_ids = endpoint_factors(open_v)
    wall_rows = projection["fiber_walls"]["catalog"]
    wall_degrees = {row["id"]: row["fiber_degree"] for row in wall_rows}
    wall_coefficients = {row["id"]: regular.wall_coefficients(row) for row in wall_rows}
    sectors = regular.read_source_shards(open_record, OPEN_SHARD_FORMAT, "sectors")
    sector_ids = regular.read_source_shards(open_v, OPEN_V_SHARD_FORMAT, "strip_signature_ids")
    catalog = [tuple(tuple(token) for token in sequence) for sequence in open_v["open_cell_v_lift"]["signature_catalog"]]
    replayed = replay(
        sectors,
        sector_ids,
        catalog,
        events,
        endpoint_factor_ids,
        coefficient_factors,
        wall_degrees,
        wall_coefficients,
    )
    shard_manifest = verify_shards(candidate, replayed)
    semantic_payload = {
        "endpoint_u_section_semantic_sha256": endpoint_record["semantic_sha256"],
        "raw_event_map_sha256": digest(event_serial),
        "coefficient_factor_map_sha256": digest(coefficient_map_serial),
        "partition_sha256": replayed["partition_sha256"],
        "factor_census": replayed["factor_census"],
        "degree_drop_census": replayed["degree_drop_census"],
        "pattern_census": replayed["pattern_census"],
        "remaining_census": replayed["remaining_census"],
    }
    observed = {
        **replayed,
        "projection_semantic_sha256": projection["semantic_sha256"],
        "base_projection_semantic_sha256": base["semantic_sha256"],
        "open_sector_lift_semantic_sha256": open_record["semantic_sha256"],
        "open_cell_v_lift_semantic_sha256": open_v["semantic_sha256"],
        "regular_u_section_semantic_sha256": regular_record["semantic_sha256"],
        "endpoint_u_section_semantic_sha256": endpoint_record["semantic_sha256"],
        "coefficient_factor_map_sha256": digest(coefficient_map_serial),
        "raw_event_map_sha256": digest(event_serial),
        "artifact_shards": {"format": SHARD_FORMAT, "shard_count": SHARD_COUNT, "shards": shard_manifest},
        "semantic_sha256": digest(semantic_payload),
    }
    validate_claims(candidate, observed)

    mutations = []
    for path, value in (
        (("scope", "remaining_open_t_coefficient_endpoint_u_section_v_lift"), "COMPLETE"),
        (("scope", "algebraic_t_section_v_lift"), "COMPLETE"),
        (("scope", "global_gluing_and_closure_data"), "COMPLETE"),
        (("scope", "honest_9dvl_score"), "3/9"),
        (("coefficient_only_u_section_v_lift", "completed_sections"), 3_389),
        (("coefficient_only_u_section_v_lift", "remaining_sections"), 4_581),
        (("coefficient_only_u_section_v_lift", "simple_leading_coefficient_events"), 3_387),
        (("coefficient_only_u_section_v_lift", "completed_raw_resultant_events"), 11_857),
        (("coefficient_only_u_section_v_lift", "visible_inversion_edges"), 10_703),
        (("coefficient_only_u_section_v_lift", "lifted_cells"), 79_815),
        (("coefficient_only_u_section_v_lift", "coefficient_factor_map_sha256"), "0" * 64),
        (("coefficient_only_u_section_v_lift", "partition_sha256"), "0" * 64),
        (("semantic_sha256",), "0" * 64),
        (("resource_effect", "next_stage"), "promote diagonal three"),
        (("generator_dependency", "independent_verifier"), "SHARED_PRODUCER"),
    ):
        hostile = deepcopy(candidate)
        target = hostile
        for key in path[:-1]:
            target = target[key]
        target[path[-1]] = value
        mutations.append(hostile)
    rejected = 0
    for hostile in mutations:
        try:
            validate_claims(hostile, observed)
        except AssertionError:
            rejected += 1
    require(rejected == len(mutations), "claim mutation survived")

    coefficient_event = ("coefficient", (13, 1), 1, 24)
    for args in (
        (27, tuple(), tuple(), ("coefficient", (13, 0), 1, 24), coefficient_factors, wall_degrees, wall_coefficients),
        (27, ((13, 0),), ((13, 0),), coefficient_event, coefficient_factors, wall_degrees, wall_coefficients),
        (27, tuple(), tuple(), coefficient_event, {**coefficient_factors, (13, 0): (27,)}, wall_degrees, wall_coefficients),
    ):
        try:
            validate_degree_drop(*args)
        except AssertionError:
            rejected += 1
        else:
            raise AssertionError("hostile degree-drop canary survived")
    try:
        verify_invisible_resultants(((1, 0), (2, 0)), Counter({(1, 2): 1}), Counter())
    except AssertionError:
        rejected += 1
    else:
        raise AssertionError("hostile invisible-resultant canary survived")

    print("PASS independent leading-coefficient and constant-factor reconstruction")
    print("PASS 3388 coefficient-only sections -> 79816 lifted cells")
    print("PASS exact factor census: 27:1694, 38:1694")
    print("PASS coefficient-plus-endpoint residue: 4582 sections")
    print(f"PASS {rejected}/{len(mutations) + 4} hostile mutations rejected")
    print(
        "SCOPE coefficient-only open-t algebraic-u fibers; coefficient-endpoint "
        "fibers, algebraic-t lifts, global gluing, labels, middle rank, and "
        "diagonal three remain open; honest 9DVL 2/9"
    )


if __name__ == "__main__":
    main()
