#!/usr/bin/env python3
"""Independent replay of the final open-t coefficient-endpoint u-section lift."""

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
ENDPOINT_ONLY = HERE / "data" / "DIAG3_PAIR_GLOBAL_FOUR_SUPPORT_ENDPOINT_U_SECTION_V_LIFT.json"
COEFFICIENT_ONLY = HERE / "data" / "DIAG3_PAIR_GLOBAL_FOUR_SUPPORT_COEFFICIENT_ONLY_U_SECTION_V_LIFT.json"
CERTIFICATE = HERE / "data" / "DIAG3_PAIR_GLOBAL_FOUR_SUPPORT_COEFFICIENT_ENDPOINT_U_SECTION_V_LIFT.json"

FORMAT = "diag3-pair-global-row2599-four-support-coefficient-endpoint-u-section-v-lift-v1"
SHARD_FORMAT = (
    "diag3-pair-global-row2599-four-support-coefficient-endpoint-u-section-v-lift-shard-v1"
)
OPEN_SHARD_FORMAT = "diag3-pair-global-row2599-four-support-open-sector-lift-shard-v1"
OPEN_V_SHARD_FORMAT = "diag3-pair-global-row2599-four-support-open-cell-v-lift-shard-v1"
SHARD_COUNT = 32
SECTOR_COUNT = 1_694
SECTION_COUNT = 132_134

COUNT_CHANGE = regular.COUNT_CHANGE
COEFFICIENT = regular.COEFFICIENT
ENDPOINT = regular.ENDPOINT
TARGET_REASONS = {COEFFICIENT | ENDPOINT, COUNT_CHANGE | COEFFICIENT | ENDPOINT}
NEXT_STAGE = (
    "lift the 261571 base cells over all algebraic t sections, then construct "
    "global gluing, labels, and closure data"
)
THEOREM_EFFECT = (
    "Exact bounded degree-drop, endpoint-attachment, and fiber-wide-zero "
    "analysis completes the final 4582 open-t algebraic-u v fibers and 108170 "
    "cells; all 132134 such sections are now complete, while algebraic-t v "
    "lifts, global gluing, labels, middle-rank replay, and diagonal three remain "
    "open; honest 9DVL score remains 2/9."
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
    compressed = bytearray(gzip.compress(encoded, compresslevel=9, mtime=0))
    # zlib stamps byte 9 per host; these fixtures canonically pin the Unix value.
    compressed[9] = 0x03
    require(
        compressed[:10] == b"\x1f\x8b\x08\x00\x00\x00\x00\x00\x02\x03",
        "unexpected canonical gzip header",
    )
    return bytes(compressed)


def independent_endpoint_owner_map(projection, open_v):
    degrees = {
        row["id"]: row["fiber_degree"]
        for row in projection["fiber_walls"]["catalog"]
    }
    owners = defaultdict(list)
    serial = []
    for row in open_v["v_endpoint_audit"]["factorizations"]:
        for factor_id, multiplicity in row["base_factors"]:
            owner = (row["wall_id"], row["endpoint"], multiplicity, degrees[row["wall_id"]])
            owners[factor_id].append(owner)
            serial.append([factor_id, *owner])
    for rows in owners.values():
        rows.sort()
    serial.sort()
    return owners, serial


def independent_coefficient_factor_map(events):
    answer = defaultdict(set)
    for factor_id, rows in events.items():
        for kind, owners, _multiplicity, _projection_id in rows:
            if kind == "coefficient":
                answer[tuple(owners)].add(factor_id)
    return {owner: tuple(sorted(factors)) for owner, factors in answer.items()}


def classify(left, right, current_events, endpoint_owners, factor_id):
    reason = 0
    if len(left) != len(right):
        reason |= COUNT_CHANGE
    if any(event[0] != "resultant" for event in current_events):
        reason |= COEFFICIENT
    if factor_id in endpoint_owners:
        reason |= ENDPOINT
    return reason


EXPECTED_ROLES = {
    35: {(0, 0, "endpoint_constant")},
    56: {(12, 1, "unbounded_leading")},
    72: {
        (14, 0, "endpoint_constant"),
        (17, 0, "fiber_wide_zero"),
        (21, 1, "unbounded_leading"),
    },
}
EXPECTED_OWNERS = {
    35: {(0, 0, 1, 1), (15, 1, 1, 1)},
    56: {(13, 1, 1, 1), (16, 1, 1, 1)},
    72: {
        (14, 0, 1, 1),
        (17, 0, 1, 0),
        (17, 1, 1, 0),
        (18, 1, 1, 1),
        (19, 1, 1, 1),
    },
}


def validate_coefficient_roles(
    factor_id,
    coefficient_rows,
    coefficient_factors,
    wall_degrees,
    wall_coefficients,
    left_set,
    right_set,
):
    roles = []
    for _kind, owners, multiplicity, _projection_id in coefficient_rows:
        wall_id, power = owners
        degree = wall_degrees[wall_id]
        token = (wall_id, 0)
        require(multiplicity == 1, "coefficient multiplicity")
        require(power in wall_coefficients[wall_id], "missing wall coefficient")
        require(
            regular.reduce_boundary(wall_coefficients[wall_id][power]),
            "zero source coefficient",
        )
        require(
            factor_id in coefficient_factors.get((wall_id, power), ()),
            "target does not own coefficient",
        )
        if degree == 0:
            role = "fiber_wide_zero"
            require(power == 0 and token not in left_set | right_set, "bad fiber-wide zero")
            other_factors = ()
        elif power == 0:
            role = "endpoint_constant"
            require(degree == 1 and token in left_set ^ right_set, "bad endpoint constant")
            require(
                regular.reduce_boundary(wall_coefficients[wall_id][1]),
                "zero leading coefficient",
            )
            other_factors = coefficient_factors.get((wall_id, 1), ())
            require(factor_id not in other_factors, "leading coefficient also vanishes")
        else:
            role = "unbounded_leading"
            require(power == degree == 1, "unsupported leading drop")
            require(token not in left_set | right_set, "degree-drop root is bounded")
            require(
                regular.reduce_boundary(wall_coefficients[wall_id][0]),
                "zero degree-drop constant",
            )
            other_factors = coefficient_factors.get((wall_id, 0), ())
            require(factor_id not in other_factors, "constant also vanishes")
        roles.append((wall_id, power, role, other_factors))
    require(
        {(wall, power, role) for wall, power, role, _ in roles}
        == EXPECTED_ROLES[factor_id],
        "coefficient-role pattern",
    )
    return tuple(sorted(roles))


def validate_endpoint_attachments(factor_id, owners, left_set, right_set):
    require(set(owners) == EXPECTED_OWNERS[factor_id], "endpoint-owner pattern")
    attachments = []
    degree_zero = []
    for wall_id, boundary, multiplicity, degree in owners:
        token = (wall_id, 0)
        require(multiplicity == 1, "endpoint multiplicity")
        if degree == 0:
            require(token not in left_set | right_set, "degree-zero endpoint token")
            degree_zero.append((wall_id, boundary))
        else:
            require(degree == 1, "nonlinear endpoint owner")
            require((token in left_set) != (token in right_set), "non-crossing endpoint")
            attachments.append(
                (wall_id, boundary, "exit" if token in left_set else "entry")
            )
    require(
        left_set ^ right_set == {(wall, 0) for wall, _, _ in attachments},
        "endpoint-token symmetric difference",
    )
    return tuple(sorted(attachments)), tuple(sorted(degree_zero))


def verify_invisible_resultants(common, permitted, seen):
    common_walls = {token[0] for token in common}
    for owners, multiplicity in (permitted - seen).items():
        require(
            not multiplicity or not set(owners) <= common_walls,
            "invisible resultant has two common owners",
        )


def string_census(counter):
    return {",".join(map(str, key)): value for key, value in sorted(counter.items())}


def replay(
    sectors,
    sector_ids,
    catalog,
    events,
    endpoint_owners,
    coefficient_factors,
    wall_degrees,
    wall_coefficients,
):
    shards = [[] for _ in range(SHARD_COUNT)]
    factor_census = Counter()
    role_census = Counter()
    attachment_census = Counter()
    pattern_census = Counter()
    prior_census = Counter()
    completed = coefficient_count = resultant_count = inversion_count = group_count = 0
    points = strips = fiber_wide = 0

    for sector_id, (stack, identifiers) in enumerate(zip(sectors, sector_ids, strict=True)):
        require(len(identifiers) == len(stack) + 1, "strip adjacency")
        completed_rows = []
        for root_index, root in enumerate(stack):
            factor_id = root[0]
            left = catalog[identifiers[root_index]]
            right = catalog[identifiers[root_index + 1]]
            current_events = events[factor_id]
            require(current_events and all(event[2] == 1 for event in current_events), "raw events")
            reason = classify(left, right, current_events, endpoint_owners, factor_id)
            if reason not in TARGET_REASONS:
                prior_census[reason] += 1
                continue
            require(factor_id in EXPECTED_ROLES, "unexpected target factor")
            left_set = set(left)
            right_set = set(right)
            coefficient_rows = [event for event in current_events if event[0] == "coefficient"]
            roles = validate_coefficient_roles(
                factor_id,
                coefficient_rows,
                coefficient_factors,
                wall_degrees,
                wall_coefficients,
                left_set,
                right_set,
            )
            attachments, degree_zero = validate_endpoint_attachments(
                factor_id, endpoint_owners[factor_id], left_set, right_set
            )
            if factor_id == 72:
                require(degree_zero == ((17, 0), (17, 1)), "fiber-wide endpoints")
                fiber_wide += 1
            else:
                require(not degree_zero, "unexpected degree-zero owner")

            common = left_set & right_set
            edges = regular.inversions(left, right)
            groups = regular.collision_components(edges)
            seen = Counter(
                tuple(sorted((first[0], second[0]))) for first, second in edges
            )
            permitted = Counter(
                tuple(sorted(event[1]))
                for event in current_events
                if event[0] == "resultant"
            )
            regular.verify_inversion_owners(seen, permitted)
            verify_invisible_resultants(common, permitted, seen)
            require(all(set(group) <= common for group in groups), "non-common collision token")
            section_points = len(common) - sum(len(group) - 1 for group in groups)
            section_strips = section_points + 1
            group_sizes = tuple(sorted(len(group) for group in groups))
            completed_rows.append(
                [
                    root_index,
                    factor_id,
                    [[wall, power, role, list(other)] for wall, power, role, other in roles],
                    [[wall, boundary, direction] for wall, boundary, direction in attachments],
                    [list(owner) for owner in degree_zero],
                    len(permitted),
                    len(edges),
                    len(groups),
                    section_points,
                    section_strips,
                ]
            )
            completed += 1
            factor_census[factor_id] += 1
            for wall, power, role, other in roles:
                role_census[(factor_id, wall, power, role, other)] += 1
            for wall, boundary, direction in attachments:
                attachment_census[(factor_id, wall, boundary, direction)] += 1
            pattern_census[(
                factor_id,
                len(left),
                len(right),
                len(common),
                len(edges),
                group_sizes,
                section_points,
                section_strips,
            )] += 1
            coefficient_count += len(coefficient_rows)
            resultant_count += len(permitted)
            inversion_count += len(edges)
            group_count += len(groups)
            points += section_points
            strips += section_strips

        shard_index = SHARD_COUNT * sector_id // SECTOR_COUNT
        shards[shard_index].append({"completed": completed_rows, "remaining": []})

    require(prior_census == {0: 120_174, 5: 3_990, 2: 3_388}, "prior partition")
    require(completed == 4_582, "completed count")
    require(sum(prior_census.values()) + completed == SECTION_COUNT, "full partition")
    partition = [row for shard in shards for row in shard]
    return {
        "shards": shards,
        "partition_sha256": digest(partition),
        "factor_census": {str(k): v for k, v in sorted(factor_census.items())},
        "role_census": string_census(role_census),
        "attachment_census": string_census(attachment_census),
        "pattern_census": string_census(pattern_census),
        "completed": completed,
        "coefficient_count": coefficient_count,
        "attachment_count": sum(attachment_census.values()),
        "fiber_wide": fiber_wide,
        "resultant_count": resultant_count,
        "inversion_count": inversion_count,
        "group_count": group_count,
        "points": points,
        "strips": strips,
    }


def verify_shards(candidate, observed):
    expected_manifest = []
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
            "DIAG3_PAIR_GLOBAL_FOUR_SUPPORT_COEFFICIENT_ENDPOINT_U_SECTION_V_LIFT_"
            f"SHARD_{index:02d}_OF_{SHARD_COUNT}.json.gz"
        )
        require((CERTIFICATE.parent / name).read_bytes() == expected_bytes, "shard bytes")
        expected_manifest.append({
            "index": index,
            "path": name,
            "sector_start": sector_start,
            "sector_end": sector_end,
            "bytes": len(expected_bytes),
            "sha256": sha256(expected_bytes).hexdigest(),
        })
    expected = {"format": SHARD_FORMAT, "shard_count": SHARD_COUNT, "shards": expected_manifest}
    require(candidate["artifact_shards"] == expected, "shard manifest")
    return expected


def validate_claims(candidate, observed):
    require(candidate["format"] == FORMAT and candidate["status"] == "PROVED", "format/status")
    require(candidate["scope"] == {
        "all_open_t_algebraic_u_section_v_lifts": "COMPLETE",
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
        "coefficient_only_semantic_sha256",
    ):
        require(source[key] == observed[key], f"source {key}")
    require(source["prior_residual_sections"] == 4_582, "prior residue")
    lift = candidate["coefficient_endpoint_u_section_v_lift"]
    require(lift["completed_sections"] == observed["completed"] == 4_582, "completed")
    require(lift["remaining_open_t_algebraic_u_sections"] == 0, "residue")
    require(lift["completed_factor_census"] == observed["factor_census"] == {"35": 1_694, "56": 1_694, "72": 1_194}, "factor census")
    require(lift["coefficient_role_census"] == observed["role_census"], "role census")
    require(lift["endpoint_attachment_census"] == observed["attachment_census"], "attachment census")
    require(lift["event_inversion_group_pattern_census"] == observed["pattern_census"], "pattern census")
    require(lift["simple_coefficient_events"] == observed["coefficient_count"] == 6_970, "coefficient events")
    require(lift["simple_endpoint_attachments"] == observed["attachment_count"] == 10_358, "attachments")
    require(lift["fiber_wide_zero_wall_sections"] == observed["fiber_wide"] == 1_194, "fiber-wide zero")
    require(lift["completed_raw_resultant_events"] == observed["resultant_count"] == 21_910, "resultants")
    require(lift["visible_inversion_edges"] == observed["inversion_count"] == 14_896, "inversions")
    require(lift["interior_collision_groups"] == observed["group_count"] == 10_586, "groups")
    require(lift["section_v_root_points"] == observed["points"] == 51_794, "points")
    require(lift["section_open_v_strips"] == observed["strips"] == 56_376, "strips")
    require(lift["lifted_cells"] == observed["points"] + observed["strips"] == 108_170, "cells")
    for key in ("raw_event_map_sha256", "endpoint_owner_map_sha256", "coefficient_factor_map_sha256", "partition_sha256"):
        require(lift[key] == observed[key], key)
    require(candidate["artifact_shards"] == observed["artifact_shards"], "shards")
    require(candidate["semantic_sha256"] == observed["semantic_sha256"], "semantic digest")
    require(candidate["cumulative_open_t_algebraic_u_section_v_lift"] == {
        "completed_sections": 132_134,
        "section_v_root_points": 1_957_856,
        "section_open_v_strips": 2_089_990,
        "lifted_cells": 4_047_846,
    }, "cumulative census")
    require(candidate["resource_effect"] == {
        "prior_residual_ceiling": 4_582,
        "sections_examined": 4_582,
        "ceiling_not_triggered": True,
        "next_stage": NEXT_STAGE,
    }, "resource effect")
    require(candidate["generator_dependency"]["python"].startswith("3.12."), "python")
    require(candidate["generator_dependency"]["independent_verifier"] == "STRUCTURAL_REPLAY_WITHOUT_FINAL_PRODUCER_IMPORT", "dependency")
    require(candidate["theorem_effect"] == THEOREM_EFFECT, "theorem effect")


def main():
    candidate = json.loads(CERTIFICATE.read_bytes())
    projection = json.loads(PROJECTION.read_bytes())
    base = json.loads(gzip.decompress(BASE.read_bytes()))
    open_record = json.loads(OPEN.read_bytes())
    open_v = json.loads(OPEN_V.read_bytes())
    regular_record = json.loads(REGULAR.read_bytes())
    endpoint_record = json.loads(ENDPOINT_ONLY.read_bytes())
    coefficient_record = json.loads(COEFFICIENT_ONLY.read_bytes())
    require(all(record["status"] == "PROVED" for record in (projection, base, open_record, open_v, regular_record, endpoint_record, coefficient_record)), "source status")
    require(coefficient_record["coefficient_only_u_section_v_lift"]["remaining_sections"] == 4_582, "coefficient residue")
    regular.open_v_verifier.replay_endpoint_factorizations(projection, base, open_v)
    events, event_serial = regular.independent_event_map(projection, base)
    endpoint_owners, endpoint_serial = independent_endpoint_owner_map(projection, open_v)
    coefficient_factors = independent_coefficient_factor_map(events)
    coefficient_serial = [[list(owner), list(factors)] for owner, factors in sorted(coefficient_factors.items())]
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
        endpoint_owners,
        coefficient_factors,
        wall_degrees,
        wall_coefficients,
    )
    manifest = verify_shards(candidate, replayed)
    semantic_payload = {
        "coefficient_only_semantic_sha256": coefficient_record["semantic_sha256"],
        "raw_event_map_sha256": digest(event_serial),
        "endpoint_owner_map_sha256": digest(endpoint_serial),
        "coefficient_factor_map_sha256": digest(coefficient_serial),
        "partition_sha256": replayed["partition_sha256"],
        "factor_census": replayed["factor_census"],
        "role_census": replayed["role_census"],
        "attachment_census": replayed["attachment_census"],
        "pattern_census": replayed["pattern_census"],
    }
    observed = {
        **replayed,
        "projection_semantic_sha256": projection["semantic_sha256"],
        "base_projection_semantic_sha256": base["semantic_sha256"],
        "open_sector_lift_semantic_sha256": open_record["semantic_sha256"],
        "open_cell_v_lift_semantic_sha256": open_v["semantic_sha256"],
        "regular_u_section_semantic_sha256": regular_record["semantic_sha256"],
        "endpoint_u_section_semantic_sha256": endpoint_record["semantic_sha256"],
        "coefficient_only_semantic_sha256": coefficient_record["semantic_sha256"],
        "raw_event_map_sha256": digest(event_serial),
        "endpoint_owner_map_sha256": digest(endpoint_serial),
        "coefficient_factor_map_sha256": digest(coefficient_serial),
        "artifact_shards": manifest,
        "semantic_sha256": digest(semantic_payload),
    }
    validate_claims(candidate, observed)

    mutations = []
    for path, value in (
        (("scope", "all_open_t_algebraic_u_section_v_lifts"), "NOT_YET_CONSTRUCTED"),
        (("scope", "algebraic_t_section_v_lift"), "COMPLETE"),
        (("scope", "global_gluing_and_closure_data"), "COMPLETE"),
        (("scope", "honest_9dvl_score"), "3/9"),
        (("coefficient_endpoint_u_section_v_lift", "completed_sections"), 4_581),
        (("coefficient_endpoint_u_section_v_lift", "remaining_open_t_algebraic_u_sections"), 1),
        (("coefficient_endpoint_u_section_v_lift", "simple_coefficient_events"), 6_969),
        (("coefficient_endpoint_u_section_v_lift", "simple_endpoint_attachments"), 10_357),
        (("coefficient_endpoint_u_section_v_lift", "fiber_wide_zero_wall_sections"), 1_193),
        (("coefficient_endpoint_u_section_v_lift", "completed_raw_resultant_events"), 21_909),
        (("coefficient_endpoint_u_section_v_lift", "visible_inversion_edges"), 14_895),
        (("coefficient_endpoint_u_section_v_lift", "interior_collision_groups"), 10_585),
        (("coefficient_endpoint_u_section_v_lift", "lifted_cells"), 108_169),
        (("coefficient_endpoint_u_section_v_lift", "partition_sha256"), "0" * 64),
        (("cumulative_open_t_algebraic_u_section_v_lift", "completed_sections"), 132_133),
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

    structural_canaries = [
        (35, [("coefficient", (0, 1), 1, 35)], set(), {(0, 0)}),
        (56, [("coefficient", (12, 1), 1, 57)], {(12, 0)}, {(12, 0)}),
        (72, [("coefficient", (17, 0), 2, 73)], set(), set()),
    ]
    for factor_id, rows, left_set, right_set in structural_canaries:
        try:
            validate_coefficient_roles(
                factor_id,
                rows,
                coefficient_factors,
                wall_degrees,
                wall_coefficients,
                left_set,
                right_set,
            )
        except AssertionError:
            rejected += 1
        else:
            raise AssertionError("coefficient-role canary survived")
    try:
        validate_endpoint_attachments(35, endpoint_owners[35][:-1], set(), {(0, 0), (15, 0)})
    except AssertionError:
        rejected += 1
    else:
        raise AssertionError("endpoint-owner canary survived")
    try:
        verify_invisible_resultants({(1, 0), (2, 0)}, Counter({(1, 2): 1}), Counter())
    except AssertionError:
        rejected += 1
    else:
        raise AssertionError("invisible-resultant canary survived")

    print("PASS independent coefficient, endpoint, and bounded-token reconstruction")
    print("PASS final 4582 open-t algebraic-u sections -> 108170 lifted cells")
    print("PASS all 132134 open-t algebraic-u section v lifts complete -> 4047846 cells")
    print("PASS exact factor census: 35:1694, 56:1694, 72:1194")
    print(f"PASS {rejected}/{len(mutations) + 5} hostile mutations rejected")
    print(
        "SCOPE all open-t algebraic-u v fibers complete; algebraic-t lifts, "
        "global gluing, labels, middle rank, and diagonal three remain open; "
        "honest 9DVL 2/9"
    )


if __name__ == "__main__":
    main()
