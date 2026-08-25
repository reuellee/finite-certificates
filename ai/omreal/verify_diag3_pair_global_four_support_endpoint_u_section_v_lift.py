#!/usr/bin/env python3
"""Independent replay of the endpoint-only algebraic-u-section v lift."""

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
CERTIFICATE = HERE / "data" / "DIAG3_PAIR_GLOBAL_FOUR_SUPPORT_ENDPOINT_U_SECTION_V_LIFT.json"

FORMAT = "diag3-pair-global-row2599-four-support-endpoint-u-section-v-lift-v1"
SHARD_FORMAT = (
    "diag3-pair-global-row2599-four-support-endpoint-u-section-v-lift-shard-v1"
)
OPEN_SHARD_FORMAT = "diag3-pair-global-row2599-four-support-open-sector-lift-shard-v1"
OPEN_V_SHARD_FORMAT = "diag3-pair-global-row2599-four-support-open-cell-v-lift-shard-v1"
SHARD_COUNT = 32
SECTOR_COUNT = 1_694
SECTION_COUNT = 132_134

COUNT_CHANGE = regular.COUNT_CHANGE
COEFFICIENT = regular.COEFFICIENT
ENDPOINT = regular.ENDPOINT
TARGET_REASON = COUNT_CHANGE | ENDPOINT

THEOREM_EFFECT = (
    "Exact endpoint attachments complete 3990 additional algebraic-u v fibers "
    "and 120468 cells over open t sectors; 7970 coefficient-event fibers, all "
    "algebraic-t v lifts, global gluing, labels, middle-rank replay, and diagonal "
    "three remain open; honest 9DVL score remains 2/9."
)
NEXT_STAGE = (
    "resolve the 7970 coefficient-event u-section fibers, then lift all 261571 "
    "base cells over algebraic t sections"
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


def independent_endpoint_owner_map(projection, open_v):
    wall_degree = {
        row["id"]: row["fiber_degree"]
        for row in projection["fiber_walls"]["catalog"]
    }
    owners = defaultdict(list)
    serial = []
    for row in open_v["v_endpoint_audit"]["factorizations"]:
        for factor in row["base_factors"]:
            factor_id, multiplicity = factor
            owner = (
                row["wall_id"],
                row["endpoint"],
                multiplicity,
                wall_degree[row["wall_id"]],
            )
            owners[factor_id].append(owner)
            serial.append([factor_id, *owner])
    for factor_id in owners:
        owners[factor_id].sort()
    serial.sort()
    return owners, serial


def classify(left, right, current_events, endpoint_owners, factor_id):
    reason = 0
    if len(left) != len(right):
        reason |= COUNT_CHANGE
    if any(event[0] != "resultant" for event in current_events):
        reason |= COEFFICIENT
    if factor_id in endpoint_owners:
        reason |= ENDPOINT
    return reason


def validate_endpoint_attachment(left, right, owner):
    endpoint_wall, _endpoint, multiplicity, degree = owner
    require(multiplicity == 1, "endpoint factor multiplicity")
    require(degree == 1, "endpoint owner is not a linear v root")
    token = (endpoint_wall, 0)
    left_set = set(left)
    right_set = set(right)
    require(left_set ^ right_set == {token}, "wrong endpoint symmetric difference")
    require(
        (token in left_set) != (token in right_set),
        "endpoint token is not one-sided",
    )
    return token, "exit" if token in left_set else "entry"


def verify_invisible_common_resultants(common, event_owners, inversion_owners):
    bounded_walls = {token[0] for token in common}
    for owners, multiplicity in (event_owners - inversion_owners).items():
        require(
            not multiplicity or not set(owners) <= bounded_walls,
            "invisible resultant has both owners in the common bounded stack",
        )


def string_census(counter):
    return {",".join(map(str, key)): value for key, value in sorted(counter.items())}


def replay(sectors, sector_ids, catalog, events, endpoint_owners):
    shards = [[] for _ in range(SHARD_COUNT)]
    factor_census = Counter()
    attachment_census = Counter()
    pattern_census = Counter()
    remaining_census = Counter()
    regular_sections = completed_sections = 0
    raw_events = visible_inversions = collision_groups = 0
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
            require(
                all(event[2] == 1 for event in current_events),
                "non-simple raw event",
            )
            reason = classify(
                left, right, current_events, endpoint_owners, factor_id
            )
            if not reason:
                regular_sections += 1
                continue
            if reason != TARGET_REASON:
                remaining.append([root_index, factor_id, reason])
                remaining_census[reason] += 1
                continue

            owners = endpoint_owners[factor_id]
            require(len(owners) == 1, "multiple endpoint owners on target factor")
            owner = owners[0]
            endpoint_token, direction = validate_endpoint_attachment(
                left, right, owner
            )
            endpoint_wall, endpoint, _multiplicity, _degree = owner

            edges = regular.inversions(left, right)
            groups = regular.collision_components(edges)
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
            common = set(left) & set(right)
            verify_invisible_common_resultants(
                common, permitted_owners, seen_owners
            )
            require(
                all(endpoint_token not in group for group in groups),
                "endpoint token included in interior collision",
            )
            section_points = len(common) - sum(
                len(component) - 1 for component in groups
            )
            section_strips = section_points + 1
            group_sizes = tuple(sorted(len(component) for component in groups))
            completed.append(
                [
                    root_index,
                    factor_id,
                    endpoint_wall,
                    endpoint,
                    direction,
                    len(current_events),
                    len(edges),
                    len(groups),
                    section_points,
                    section_strips,
                ]
            )
            completed_sections += 1
            factor_census[factor_id] += 1
            attachment_census[(factor_id, endpoint_wall, endpoint, direction)] += 1
            pattern_census[
                (
                    factor_id,
                    len(left),
                    len(right),
                    len(edges),
                    group_sizes,
                    section_points,
                    section_strips,
                    direction,
                )
            ] += 1
            raw_events += len(current_events)
            visible_inversions += len(edges)
            collision_groups += len(groups)
            points += section_points
            strips += section_strips

        shard_index = SHARD_COUNT * sector_id // SECTOR_COUNT
        shards[shard_index].append(
            {"completed": completed, "remaining": remaining}
        )

    require(regular_sections == 120_174, "prior regular count")
    require(completed_sections == 3_990, "endpoint completion count")
    require(sum(remaining_census.values()) == 7_970, "remaining count")
    require(
        regular_sections + completed_sections + sum(remaining_census.values())
        == SECTION_COUNT,
        "complete section partition",
    )
    partition = [row for shard in shards for row in shard]
    return {
        "shards": shards,
        "partition_sha256": digest(partition),
        "factor_census": {str(key): value for key, value in sorted(factor_census.items())},
        "attachment_census": string_census(attachment_census),
        "pattern_census": string_census(pattern_census),
        "remaining_census": {str(key): value for key, value in sorted(remaining_census.items())},
        "regular_sections": regular_sections,
        "completed_sections": completed_sections,
        "remaining_sections": sum(remaining_census.values()),
        "raw_events": raw_events,
        "visible_inversions": visible_inversions,
        "collision_groups": collision_groups,
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
            "DIAG3_PAIR_GLOBAL_FOUR_SUPPORT_ENDPOINT_U_SECTION_V_LIFT_"
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
    require(candidate["format"] == FORMAT, "format")
    require(candidate["status"] == "PROVED", "status")
    require(
        candidate["scope"]
        == {
            "open_t_endpoint_only_count_change_u_section_v_lift": "COMPLETE",
            "remaining_open_t_coefficient_event_u_section_v_lift": "NOT_YET_CONSTRUCTED",
            "algebraic_t_section_v_lift": "NOT_YET_CONSTRUCTED",
            "global_gluing_and_closure_data": "NOT_CLAIMED",
            "honest_9dvl_score": "2/9",
        },
        "scope",
    )
    source = candidate["source"]
    for key in (
        "projection_semantic_sha256",
        "base_projection_semantic_sha256",
        "open_sector_lift_semantic_sha256",
        "open_cell_v_lift_semantic_sha256",
        "regular_u_section_semantic_sha256",
    ):
        require(source[key] == observed[key], f"source link {key}")
    require(source["prior_regular_sections"] == 120_174, "prior regular sections")
    require(source["prior_residual_sections"] == 11_960, "prior residue")

    lift = candidate["endpoint_u_section_v_lift"]
    require(lift["completed_sections"] == observed["completed_sections"] == 3_990, "completed sections")
    require(lift["remaining_sections"] == observed["remaining_sections"] == 7_970, "remaining sections")
    require(lift["completed_factor_census"] == observed["factor_census"] == {"12": 1_194, "57": 1_694, "86": 1_102}, "factor census")
    require(lift["attachment_census"] == observed["attachment_census"], "attachment census")
    require(lift["event_inversion_group_pattern_census"] == observed["pattern_census"], "pattern census")
    require(lift["completed_raw_resultant_events"] == observed["raw_events"] == 10_184, "raw events")
    require(lift["visible_inversion_edges"] == observed["visible_inversions"] == 9_951, "inversions")
    require(lift["interior_collision_groups"] == observed["collision_groups"] == 7_747, "groups")
    require(lift["section_v_root_points"] == observed["points"] == 58_239, "points")
    require(lift["section_open_v_strips"] == observed["strips"] == 62_229, "strips")
    require(lift["lifted_cells"] == observed["points"] + observed["strips"] == 120_468, "cells")
    require(lift["endpoint_owner_map_sha256"] == observed["endpoint_owner_map_sha256"], "endpoint digest")
    require(lift["raw_event_map_sha256"] == observed["raw_event_map_sha256"], "event digest")
    require(lift["partition_sha256"] == observed["partition_sha256"], "partition digest")
    require(lift["remaining_reason_census"] == observed["remaining_census"] == {"2": 3_388, "6": 1_694, "7": 2_888}, "remaining census")
    require(candidate["artifact_shards"] == observed["artifact_shards"], "artifact shards")
    require(candidate["semantic_sha256"] == observed["semantic_sha256"], "semantic digest")
    require(candidate["resource_effect"] == {
        "prior_residual_ceiling": 11_960,
        "sections_examined": 11_960,
        "ceiling_not_triggered": True,
        "next_stage": NEXT_STAGE,
    }, "resource effect")
    require(
        candidate["generator_dependency"]["independent_verifier"]
        == "STANDARD_LIBRARY_STRUCTURAL_REPLAY"
        and candidate["generator_dependency"]["python"].startswith("3.12."),
        "generator dependency",
    )
    require(candidate["theorem_effect"] == THEOREM_EFFECT, "theorem effect")


def main():
    candidate = json.loads(CERTIFICATE.read_bytes())
    projection = json.loads(PROJECTION.read_bytes())
    base = json.loads(gzip.decompress(BASE.read_bytes()))
    open_record = json.loads(OPEN.read_bytes())
    open_v = json.loads(OPEN_V.read_bytes())
    regular_record = json.loads(REGULAR.read_bytes())
    require(
        projection["status"]
        == base["status"]
        == open_record["status"]
        == open_v["status"]
        == regular_record["status"]
        == "PROVED",
        "source status",
    )
    require(base["source"]["semantic_sha256"] == projection["semantic_sha256"], "projection/base link")
    require(open_record["source"]["base_projection_semantic_sha256"] == base["semantic_sha256"], "base/open link")
    require(open_v["source"]["open_sector_lift_semantic_sha256"] == open_record["semantic_sha256"], "open/open-v link")
    require(regular_record["source"]["open_cell_v_lift_semantic_sha256"] == open_v["semantic_sha256"], "open-v/regular link")
    require(regular_record["regular_u_section_v_lift"]["unresolved_sections"] == 11_960, "prior residue count")
    regular.open_v_verifier.replay_endpoint_factorizations(projection, base, open_v)

    events, event_serial = regular.independent_event_map(projection, base)
    endpoint_owners, endpoint_serial = independent_endpoint_owner_map(
        projection, open_v
    )
    sectors = regular.read_source_shards(
        open_record, OPEN_SHARD_FORMAT, "sectors"
    )
    sector_ids = regular.read_source_shards(
        open_v, OPEN_V_SHARD_FORMAT, "strip_signature_ids"
    )
    catalog = [
        tuple(tuple(token) for token in sequence)
        for sequence in open_v["open_cell_v_lift"]["signature_catalog"]
    ]
    replayed = replay(sectors, sector_ids, catalog, events, endpoint_owners)
    shard_manifest = verify_shards(candidate, replayed)
    semantic_payload = {
        "regular_u_section_semantic_sha256": regular_record["semantic_sha256"],
        "raw_event_map_sha256": digest(event_serial),
        "endpoint_owner_map_sha256": digest(endpoint_serial),
        "partition_sha256": replayed["partition_sha256"],
        "factor_census": replayed["factor_census"],
        "attachment_census": replayed["attachment_census"],
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
        "endpoint_owner_map_sha256": digest(endpoint_serial),
        "raw_event_map_sha256": digest(event_serial),
        "artifact_shards": {
            "format": SHARD_FORMAT,
            "shard_count": SHARD_COUNT,
            "shards": shard_manifest,
        },
        "semantic_sha256": digest(semantic_payload),
    }
    validate_claims(candidate, observed)

    mutations = []
    for path, value in (
        (("scope", "remaining_open_t_coefficient_event_u_section_v_lift"), "COMPLETE"),
        (("scope", "algebraic_t_section_v_lift"), "COMPLETE"),
        (("scope", "global_gluing_and_closure_data"), "COMPLETE"),
        (("scope", "honest_9dvl_score"), "3/9"),
        (("endpoint_u_section_v_lift", "completed_sections"), 3_991),
        (("endpoint_u_section_v_lift", "remaining_sections"), 7_969),
        (("endpoint_u_section_v_lift", "completed_raw_resultant_events"), 10_183),
        (("endpoint_u_section_v_lift", "visible_inversion_edges"), 9_950),
        (("endpoint_u_section_v_lift", "interior_collision_groups"), 7_746),
        (("endpoint_u_section_v_lift", "lifted_cells"), 120_467),
        (("endpoint_u_section_v_lift", "endpoint_owner_map_sha256"), "0" * 64),
        (("endpoint_u_section_v_lift", "partition_sha256"), "0" * 64),
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

    for left, right, owner in (
        (((3, 0), (4, 0), (5, 0)), ((4, 0),), (3, 1, 1, 1)),
        (((3, 0),), tuple(), (3, 1, 2, 1)),
        (((3, 0),), tuple(), (3, 1, 1, 0)),
    ):
        try:
            validate_endpoint_attachment(left, right, owner)
        except AssertionError:
            rejected += 1
        else:
            raise AssertionError("hostile endpoint attachment survived")
    try:
        verify_invisible_common_resultants(
            {(1, 0), (2, 0)}, Counter({(1, 2): 1}), Counter()
        )
    except AssertionError:
        rejected += 1
    else:
        raise AssertionError("hostile invisible-resultant canary survived")

    print("PASS independent raw-event and endpoint-owner reconstruction")
    print("PASS 3990 endpoint-only count-change sections -> 120468 lifted cells")
    print("PASS exact factor census: 12:1194, 57:1694, 86:1102")
    print("PASS coefficient-event residue: 7970 sections")
    print(f"PASS {rejected}/{len(mutations) + 4} hostile mutations rejected")
    print(
        "SCOPE endpoint-only open-t algebraic-u fibers; coefficient fibers, "
        "algebraic-t lifts, global gluing, labels, middle rank, and diagonal "
        "three remain open; honest 9DVL 2/9"
    )


if __name__ == "__main__":
    main()
