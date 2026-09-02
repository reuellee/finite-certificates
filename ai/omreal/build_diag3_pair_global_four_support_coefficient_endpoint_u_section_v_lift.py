#!/usr/bin/env python3
"""Build the final coefficient-plus-endpoint open-t algebraic-u v lift."""

from __future__ import annotations

from collections import Counter, defaultdict
import gzip
from hashlib import sha256
import json
from pathlib import Path
import sys


HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import build_diag3_pair_global_four_support_regular_u_section_v_lift as regular  # noqa: E402
import build_diag3_pair_global_four_support_endpoint_u_section_v_lift as endpoint  # noqa: E402
import build_diag3_pair_global_four_support_coefficient_only_u_section_v_lift as coefficient  # noqa: E402
import diag3_pair_global_four_support_projection_core as projection_core  # noqa: E402


PROJECTION = HERE / "data" / "DIAG3_PAIR_GLOBAL_FOUR_SUPPORT_PROJECTION.json"
BASE = HERE / "data" / "DIAG3_PAIR_GLOBAL_FOUR_SUPPORT_BASE_PROJECTION.json.gz"
OPEN = HERE / "data" / "DIAG3_PAIR_GLOBAL_FOUR_SUPPORT_OPEN_SECTOR_LIFT.json"
OPEN_V = HERE / "data" / "DIAG3_PAIR_GLOBAL_FOUR_SUPPORT_OPEN_CELL_V_LIFT.json"
REGULAR = HERE / "data" / "DIAG3_PAIR_GLOBAL_FOUR_SUPPORT_REGULAR_U_SECTION_V_LIFT.json"
ENDPOINT = HERE / "data" / "DIAG3_PAIR_GLOBAL_FOUR_SUPPORT_ENDPOINT_U_SECTION_V_LIFT.json"
COEFFICIENT_ONLY = HERE / "data" / "DIAG3_PAIR_GLOBAL_FOUR_SUPPORT_COEFFICIENT_ONLY_U_SECTION_V_LIFT.json"
OUTPUT = HERE / "data" / "DIAG3_PAIR_GLOBAL_FOUR_SUPPORT_COEFFICIENT_ENDPOINT_U_SECTION_V_LIFT.json"

FORMAT = "diag3-pair-global-row2599-four-support-coefficient-endpoint-u-section-v-lift-v1"
SHARD_FORMAT = (
    "diag3-pair-global-row2599-four-support-coefficient-endpoint-u-section-v-lift-shard-v1"
)
SHARD_COUNT = 32
SECTOR_COUNT = 1_694
SECTION_COUNT = 132_134

COUNT_CHANGE = regular.COUNT_CHANGE
COEFFICIENT = regular.COEFFICIENT
ENDPOINT_REASON = regular.ENDPOINT
TARGET_REASONS = {
    COEFFICIENT | ENDPOINT_REASON,
    COUNT_CHANGE | COEFFICIENT | ENDPOINT_REASON,
}


def digest(value) -> str:
    return sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":")).encode("ascii")
    ).hexdigest()


def canonical_gzip_json(value) -> bytes:
    encoded = (
        json.dumps(value, sort_keys=True, separators=(",", ":")) + "\n"
    ).encode("ascii")
    compressed = bytearray(gzip.compress(encoded, compresslevel=9, mtime=0))
    # zlib stamps byte 9 per host; these fixtures canonically pin the Unix value.
    compressed[9] = 0x03
    if compressed[:10] != b"\x1f\x8b\x08\x00\x00\x00\x00\x00\x02\x03":
        raise AssertionError("unexpected canonical gzip header")
    return bytes(compressed)


def reason_for(left, right, current_events, endpoint_owners, factor_id):
    reason = 0
    if len(left) != len(right):
        reason |= COUNT_CHANGE
    if any(event[0] != "resultant" for event in current_events):
        reason |= COEFFICIENT
    if factor_id in endpoint_owners:
        reason |= ENDPOINT_REASON
    return reason


def coefficient_roles(
    factor_id,
    coefficient_rows,
    coefficient_factors,
    wall_degrees,
    left_set,
    right_set,
):
    expected = {
        35: {(0, 0, "endpoint_constant")},
        56: {(12, 1, "unbounded_leading")},
        72: {
            (14, 0, "endpoint_constant"),
            (17, 0, "fiber_wide_zero"),
            (21, 1, "unbounded_leading"),
        },
    }
    roles = []
    for _kind, owners, multiplicity, _projection_id in coefficient_rows:
        wall_id, power = owners
        if multiplicity != 1:
            raise AssertionError("non-simple coefficient factor")
        degree = wall_degrees[wall_id]
        token = (wall_id, 0)
        if degree == 0:
            role = "fiber_wide_zero"
            if power != 0 or token in left_set or token in right_set:
                raise AssertionError("bad fiber-wide zero")
            other_factors = ()
        elif power == 0:
            role = "endpoint_constant"
            if degree != 1 or token not in left_set ^ right_set:
                raise AssertionError("constant drop is not an endpoint crossing")
            other_factors = coefficient_factors.get((wall_id, 1), ())
            if factor_id in other_factors:
                raise AssertionError("endpoint wall also loses its leading coefficient")
        elif power == degree == 1:
            role = "unbounded_leading"
            if token in left_set or token in right_set:
                raise AssertionError("leading-drop root remains bounded")
            other_factors = coefficient_factors.get((wall_id, 0), ())
            if factor_id in other_factors:
                raise AssertionError("degree-drop constant also vanishes")
        else:
            raise AssertionError("unsupported coefficient event")
        roles.append((wall_id, power, role, other_factors))
    if {(wall, power, role) for wall, power, role, _ in roles} != expected[factor_id]:
        raise AssertionError("coefficient-role pattern changed")
    return tuple(sorted(roles))


def endpoint_attachments(factor_id, owners, left_set, right_set):
    expected_owner_rows = {
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
    if set(owners) != expected_owner_rows[factor_id]:
        raise AssertionError("endpoint-owner pattern changed")
    attachments = []
    degree_zero_owners = []
    for wall_id, boundary, multiplicity, degree in owners:
        if multiplicity != 1:
            raise AssertionError("non-simple endpoint factor")
        token = (wall_id, 0)
        if degree == 0:
            if token in left_set or token in right_set:
                raise AssertionError("degree-zero wall emitted a root token")
            degree_zero_owners.append((wall_id, boundary))
            continue
        if degree != 1 or (token in left_set) == (token in right_set):
            raise AssertionError("endpoint owner is not one simple crossing")
        direction = "exit" if token in left_set else "entry"
        attachments.append((wall_id, boundary, direction))
    symmetric_difference = left_set ^ right_set
    if symmetric_difference != {(wall_id, 0) for wall_id, _, _ in attachments}:
        raise AssertionError("endpoint attachments do not own the token difference")
    return tuple(sorted(attachments)), tuple(sorted(degree_zero_owners))


def analyze(
    sectors,
    sector_ids,
    signature_catalog,
    events,
    endpoint_owners,
    coefficient_factors,
    wall_degrees,
):
    shards = [[] for _ in range(SHARD_COUNT)]
    factor_census = Counter()
    role_census = Counter()
    attachment_census = Counter()
    pattern_census = Counter()
    prior_census = Counter()
    completed_sections = coefficient_events = resultant_events = 0
    inversions = groups = points = strips = fiber_wide_zero_sections = 0

    for sector_id, (stack, identifiers) in enumerate(
        zip(sectors, sector_ids, strict=True)
    ):
        if len(identifiers) != len(stack) + 1:
            raise AssertionError("open-v stack adjacency changed")
        completed = []
        for root_index, root in enumerate(stack):
            factor_id = root[0]
            left = signature_catalog[identifiers[root_index]]
            right = signature_catalog[identifiers[root_index + 1]]
            current_events = events[factor_id]
            if not current_events or any(event[2] != 1 for event in current_events):
                raise AssertionError("bad raw event list")
            reason = reason_for(left, right, current_events, endpoint_owners, factor_id)
            if reason not in TARGET_REASONS:
                prior_census[reason] += 1
                continue
            if factor_id not in {35, 56, 72}:
                raise AssertionError("unexpected coefficient-endpoint factor")

            left_set = set(left)
            right_set = set(right)
            coefficient_rows = [
                event for event in current_events if event[0] == "coefficient"
            ]
            roles = coefficient_roles(
                factor_id,
                coefficient_rows,
                coefficient_factors,
                wall_degrees,
                left_set,
                right_set,
            )
            attachments, degree_zero_owners = endpoint_attachments(
                factor_id, endpoint_owners[factor_id], left_set, right_set
            )
            if factor_id == 72:
                if degree_zero_owners != ((17, 0), (17, 1)):
                    raise AssertionError("fiber-wide wall endpoint audit changed")
                fiber_wide_zero_sections += 1
            elif degree_zero_owners:
                raise AssertionError("unexpected degree-zero endpoint owner")

            common = left_set & right_set
            edges = regular.inversion_edges(left, right)
            collision_groups = regular.clique_components(edges)
            inversion_owners = Counter(
                tuple(sorted((first[0], second[0]))) for first, second in edges
            )
            event_owners = Counter(
                tuple(sorted(event[1]))
                for event in current_events
                if event[0] == "resultant"
            )
            if inversion_owners - event_owners:
                raise AssertionError("visible inversion lacks a raw resultant")
            common_walls = {token[0] for token in common}
            for pair, count in (event_owners - inversion_owners).items():
                if count and set(pair) <= common_walls:
                    raise AssertionError("invisible resultant has two common owners")
            if any(not set(group) <= common for group in collision_groups):
                raise AssertionError("endpoint token entered an interior collision")

            section_points = len(common) - sum(
                len(group) - 1 for group in collision_groups
            )
            section_strips = section_points + 1
            group_sizes = tuple(sorted(len(group) for group in collision_groups))
            completed.append(
                [
                    root_index,
                    factor_id,
                    [[wall, power, role, list(other)] for wall, power, role, other in roles],
                    [[wall, boundary, direction] for wall, boundary, direction in attachments],
                    [list(owner) for owner in degree_zero_owners],
                    len(event_owners),
                    len(edges),
                    len(collision_groups),
                    section_points,
                    section_strips,
                ]
            )
            completed_sections += 1
            factor_census[factor_id] += 1
            for wall, power, role, other in roles:
                role_census[(factor_id, wall, power, role, other)] += 1
            for wall, boundary, direction in attachments:
                attachment_census[(factor_id, wall, boundary, direction)] += 1
            pattern_census[
                (
                    factor_id,
                    len(left),
                    len(right),
                    len(common),
                    len(edges),
                    group_sizes,
                    section_points,
                    section_strips,
                )
            ] += 1
            coefficient_events += len(coefficient_rows)
            resultant_events += len(event_owners)
            inversions += len(edges)
            groups += len(collision_groups)
            points += section_points
            strips += section_strips

        shard_index = SHARD_COUNT * sector_id // SECTOR_COUNT
        shards[shard_index].append({"completed": completed, "remaining": []})

    if prior_census != {0: 120_174, 5: 3_990, 2: 3_388}:
        raise AssertionError("prior completed partition changed")
    if completed_sections != 4_582 or sum(prior_census.values()) + completed_sections != SECTION_COUNT:
        raise AssertionError("final open-t u-section partition changed")
    return {
        "shards": shards,
        "factor_census": factor_census,
        "role_census": role_census,
        "attachment_census": attachment_census,
        "pattern_census": pattern_census,
        "completed_sections": completed_sections,
        "coefficient_events": coefficient_events,
        "resultant_events": resultant_events,
        "inversions": inversions,
        "groups": groups,
        "points": points,
        "strips": strips,
        "fiber_wide_zero_sections": fiber_wide_zero_sections,
    }


def string_census(counter):
    return {",".join(map(str, key)): value for key, value in sorted(counter.items())}


def main():
    projection = json.loads(PROJECTION.read_bytes())
    base = json.loads(gzip.decompress(BASE.read_bytes()))
    open_record = json.loads(OPEN.read_bytes())
    open_v = json.loads(OPEN_V.read_bytes())
    regular_record = json.loads(REGULAR.read_bytes())
    endpoint_record = json.loads(ENDPOINT.read_bytes())
    coefficient_record = json.loads(COEFFICIENT_ONLY.read_bytes())
    records = (
        projection,
        base,
        open_record,
        open_v,
        regular_record,
        endpoint_record,
        coefficient_record,
    )
    if not all(record["status"] == "PROVED" for record in records):
        raise AssertionError("bad source status")
    source = projection_core.build_record(include_catalog=True)
    if source["semantic_sha256"] != projection["semantic_sha256"]:
        raise AssertionError("projection source changed")
    events, event_serial = regular.raw_event_map(source, base)
    endpoint_owners, endpoint_serial = endpoint.endpoint_owner_map(source, open_v)
    coefficient_factors = coefficient.coefficient_factor_map(events)
    coefficient_serial = [
        [list(owner), list(factors)]
        for owner, factors in sorted(coefficient_factors.items())
    ]
    wall_degrees = {
        row["id"]: row["fiber_degree"] for row in source["fiber_walls"]["catalog"]
    }
    sectors = regular.load_shard_field(open_record, "sectors")
    sector_ids = regular.load_shard_field(open_v, "strip_signature_ids")
    signature_catalog = [
        tuple(tuple(token) for token in sequence)
        for sequence in open_v["open_cell_v_lift"]["signature_catalog"]
    ]
    observed = analyze(
        sectors,
        sector_ids,
        signature_catalog,
        events,
        endpoint_owners,
        coefficient_factors,
        wall_degrees,
    )
    if observed["factor_census"] != {35: 1_694, 56: 1_694, 72: 1_194}:
        raise AssertionError("final factor census changed")

    shard_rows = []
    partition = []
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
        compressed = canonical_gzip_json(shard)
        name = (
            "DIAG3_PAIR_GLOBAL_FOUR_SUPPORT_COEFFICIENT_ENDPOINT_U_SECTION_V_LIFT_"
            f"SHARD_{index:02d}_OF_{SHARD_COUNT}.json.gz"
        )
        (OUTPUT.parent / name).write_bytes(compressed)
        shard_rows.append(
            {
                "index": index,
                "path": name,
                "sector_start": sector_start,
                "sector_end": sector_end,
                "bytes": len(compressed),
                "sha256": sha256(compressed).hexdigest(),
            }
        )
        partition.extend(sector_rows)

    factor_census = {
        str(key): value for key, value in sorted(observed["factor_census"].items())
    }
    role_census = string_census(observed["role_census"])
    attachment_census = string_census(observed["attachment_census"])
    pattern_census = string_census(observed["pattern_census"])
    semantic_payload = {
        "coefficient_only_semantic_sha256": coefficient_record["semantic_sha256"],
        "raw_event_map_sha256": digest(event_serial),
        "endpoint_owner_map_sha256": digest(endpoint_serial),
        "coefficient_factor_map_sha256": digest(coefficient_serial),
        "partition_sha256": digest(partition),
        "factor_census": factor_census,
        "role_census": role_census,
        "attachment_census": attachment_census,
        "pattern_census": pattern_census,
    }
    record = {
        "format": FORMAT,
        "status": "PROVED",
        "scope": {
            "all_open_t_algebraic_u_section_v_lifts": "COMPLETE",
            "algebraic_t_section_v_lift": "NOT_YET_CONSTRUCTED",
            "global_gluing_and_closure_data": "NOT_CLAIMED",
            "honest_9dvl_score": "2/9",
        },
        "source": {
            "projection_semantic_sha256": projection["semantic_sha256"],
            "base_projection_semantic_sha256": base["semantic_sha256"],
            "open_sector_lift_semantic_sha256": open_record["semantic_sha256"],
            "open_cell_v_lift_semantic_sha256": open_v["semantic_sha256"],
            "regular_u_section_semantic_sha256": regular_record["semantic_sha256"],
            "endpoint_u_section_semantic_sha256": endpoint_record["semantic_sha256"],
            "coefficient_only_semantic_sha256": coefficient_record["semantic_sha256"],
            "prior_residual_sections": 4_582,
        },
        "coefficient_endpoint_u_section_v_lift": {
            "completed_sections": observed["completed_sections"],
            "remaining_open_t_algebraic_u_sections": 0,
            "completed_factor_census": factor_census,
            "coefficient_role_census": role_census,
            "endpoint_attachment_census": attachment_census,
            "event_inversion_group_pattern_census": pattern_census,
            "simple_coefficient_events": observed["coefficient_events"],
            "simple_endpoint_attachments": sum(observed["attachment_census"].values()),
            "fiber_wide_zero_wall_sections": observed["fiber_wide_zero_sections"],
            "completed_raw_resultant_events": observed["resultant_events"],
            "visible_inversion_edges": observed["inversions"],
            "interior_collision_groups": observed["groups"],
            "section_v_root_points": observed["points"],
            "section_open_v_strips": observed["strips"],
            "lifted_cells": observed["points"] + observed["strips"],
            "raw_event_map_sha256": digest(event_serial),
            "endpoint_owner_map_sha256": digest(endpoint_serial),
            "coefficient_factor_map_sha256": digest(coefficient_serial),
            "partition_sha256": digest(partition),
        },
        "cumulative_open_t_algebraic_u_section_v_lift": {
            "completed_sections": SECTION_COUNT,
            "section_v_root_points": 1_809_609 + 58_239 + 38_214 + observed["points"],
            "section_open_v_strips": 1_929_783 + 62_229 + 41_602 + observed["strips"],
            "lifted_cells": 3_739_392 + 120_468 + 79_816 + observed["points"] + observed["strips"],
        },
        "artifact_shards": {
            "format": SHARD_FORMAT,
            "shard_count": SHARD_COUNT,
            "shards": shard_rows,
        },
        "semantic_sha256": digest(semantic_payload),
        "resource_effect": {
            "prior_residual_ceiling": 4_582,
            "sections_examined": 4_582,
            "ceiling_not_triggered": True,
            "next_stage": (
                "lift the 261571 base cells over all algebraic t sections, then "
                "construct global gluing, labels, and closure data"
            ),
        },
        "generator_dependency": {
            "python": sys.version.split()[0],
            "independent_verifier": "STRUCTURAL_REPLAY_WITHOUT_FINAL_PRODUCER_IMPORT",
        },
        "theorem_effect": (
            "Exact bounded degree-drop, endpoint-attachment, and fiber-wide-zero "
            "analysis completes the final 4582 open-t algebraic-u v fibers and "
            "108170 cells; all 132134 such sections are now complete, while "
            "algebraic-t v lifts, global gluing, labels, middle-rank replay, and "
            "diagonal three remain open; honest 9DVL score remains 2/9."
        ),
    }
    OUTPUT.write_text(
        json.dumps(record, sort_keys=True, separators=(",", ":")) + "\n",
        encoding="ascii",
    )
    print("WROTE", OUTPUT)
    print("COMPLETED", observed["completed_sections"], "REMAINING", 0)
    print(
        "V_POINTS",
        observed["points"],
        "V_STRIPS",
        observed["strips"],
        "CELLS",
        observed["points"] + observed["strips"],
    )
    print("CUMULATIVE_CELLS", record["cumulative_open_t_algebraic_u_section_v_lift"]["lifted_cells"])


if __name__ == "__main__":
    main()
