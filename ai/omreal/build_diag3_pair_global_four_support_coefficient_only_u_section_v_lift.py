#!/usr/bin/env python3
"""Build the coefficient-only algebraic-u-section v lift over open t sectors."""

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
import diag3_pair_global_four_support_projection_core as projection_core  # noqa: E402


PROJECTION = HERE / "data" / "DIAG3_PAIR_GLOBAL_FOUR_SUPPORT_PROJECTION.json"
BASE = HERE / "data" / "DIAG3_PAIR_GLOBAL_FOUR_SUPPORT_BASE_PROJECTION.json.gz"
OPEN = HERE / "data" / "DIAG3_PAIR_GLOBAL_FOUR_SUPPORT_OPEN_SECTOR_LIFT.json"
OPEN_V = HERE / "data" / "DIAG3_PAIR_GLOBAL_FOUR_SUPPORT_OPEN_CELL_V_LIFT.json"
REGULAR = HERE / "data" / "DIAG3_PAIR_GLOBAL_FOUR_SUPPORT_REGULAR_U_SECTION_V_LIFT.json"
ENDPOINT = HERE / "data" / "DIAG3_PAIR_GLOBAL_FOUR_SUPPORT_ENDPOINT_U_SECTION_V_LIFT.json"
OUTPUT = HERE / "data" / "DIAG3_PAIR_GLOBAL_FOUR_SUPPORT_COEFFICIENT_ONLY_U_SECTION_V_LIFT.json"

FORMAT = "diag3-pair-global-row2599-four-support-coefficient-only-u-section-v-lift-v1"
SHARD_FORMAT = (
    "diag3-pair-global-row2599-four-support-coefficient-only-u-section-v-lift-shard-v1"
)
SHARD_COUNT = 32
SECTOR_COUNT = 1_694
SECTION_COUNT = 132_134

COUNT_CHANGE = regular.COUNT_CHANGE
COEFFICIENT = regular.COEFFICIENT
ENDPOINT_REASON = regular.ENDPOINT
TARGET_REASON = COEFFICIENT


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


def coefficient_factor_map(events):
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


def reason_for(left, right, current_events, endpoint_factor_ids, factor_id):
    reason = 0
    if len(left) != len(right):
        reason |= COUNT_CHANGE
    if any(event[0] != "resultant" for event in current_events):
        reason |= COEFFICIENT
    if factor_id in endpoint_factor_ids:
        reason |= ENDPOINT_REASON
    return reason


def string_census(counter):
    return {",".join(map(str, key)): value for key, value in sorted(counter.items())}


def analyze(
    sectors,
    sector_ids,
    signature_catalog,
    events,
    endpoint_factor_ids,
    coefficient_factors,
    wall_degrees,
):
    shards = [[] for _ in range(SHARD_COUNT)]
    factor_census = Counter()
    degree_drop_census = Counter()
    pattern_census = Counter()
    remaining_census = Counter()
    regular_sections = endpoint_sections = completed_sections = 0
    coefficient_events = resultant_events = inversions = groups = 0
    points = strips = 0

    for sector_id, (stack, identifiers) in enumerate(
        zip(sectors, sector_ids, strict=True)
    ):
        if len(identifiers) != len(stack) + 1:
            raise AssertionError("open-v stack adjacency changed")
        completed = []
        remaining = []
        for root_index, root in enumerate(stack):
            factor_id = root[0]
            left = signature_catalog[identifiers[root_index]]
            right = signature_catalog[identifiers[root_index + 1]]
            current_events = events[factor_id]
            if not current_events or any(event[2] != 1 for event in current_events):
                raise AssertionError("bad raw event list")
            reason = reason_for(
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
            if len(coefficient_rows) != 1:
                raise AssertionError("coefficient-only target has multiple degree drops")
            _kind, owners, multiplicity, _projection_id = coefficient_rows[0]
            wall_id, power = owners
            if multiplicity != 1 or power != 1 or wall_degrees[wall_id] != 1:
                raise AssertionError("target is not a simple linear leading-coefficient drop")
            constant_factors = coefficient_factors.get((wall_id, 0), ())
            if factor_id in constant_factors:
                raise AssertionError("constant coefficient vanishes on the degree-drop curve")
            if factor_id in endpoint_factor_ids:
                raise AssertionError("coefficient-only target also owns an endpoint")
            if set(left) != set(right):
                raise AssertionError("coefficient-only target changed bounded branch tokens")
            wall_token = (wall_id, 0)
            if wall_token in set(left) or wall_token in set(right):
                raise AssertionError("degree-dropping wall has a bounded adjacent root")

            edges = regular.inversion_edges(left, right)
            collision_groups = regular.clique_components(edges)
            inversion_owners = Counter(
                tuple(sorted((first[0], second[0])))
                for first, second in edges
            )
            event_owners = Counter(
                tuple(sorted(event[1]))
                for event in current_events
                if event[0] == "resultant"
            )
            if inversion_owners - event_owners:
                raise AssertionError("visible inversion lacks a raw resultant")
            bounded_walls = {token[0] for token in left}
            for pair, count in (event_owners - inversion_owners).items():
                if count and set(pair) <= bounded_walls:
                    raise AssertionError(
                        "invisible resultant has both owners in the bounded stack"
                    )
            section_points = len(left) - sum(
                len(group) - 1 for group in collision_groups
            )
            section_strips = section_points + 1
            group_sizes = tuple(sorted(len(group) for group in collision_groups))
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
            resultant_events += len(current_events) - 1
            inversions += len(edges)
            groups += len(collision_groups)
            points += section_points
            strips += section_strips

        shard_index = SHARD_COUNT * sector_id // SECTOR_COUNT
        shards[shard_index].append(
            {"completed": completed, "remaining": remaining}
        )

    if regular_sections != 120_174 or endpoint_sections != 3_990:
        raise AssertionError("prior completed partition changed")
    if completed_sections != 3_388 or sum(remaining_census.values()) != 4_582:
        raise AssertionError("coefficient-only partition changed")
    if regular_sections + endpoint_sections + completed_sections + sum(remaining_census.values()) != SECTION_COUNT:
        raise AssertionError("u-section partition changed")
    return {
        "shards": shards,
        "factor_census": factor_census,
        "degree_drop_census": degree_drop_census,
        "pattern_census": pattern_census,
        "remaining_census": remaining_census,
        "completed_sections": completed_sections,
        "coefficient_events": coefficient_events,
        "resultant_events": resultant_events,
        "inversions": inversions,
        "groups": groups,
        "points": points,
        "strips": strips,
    }


def main():
    projection = json.loads(PROJECTION.read_bytes())
    base = json.loads(gzip.decompress(BASE.read_bytes()))
    open_record = json.loads(OPEN.read_bytes())
    open_v = json.loads(OPEN_V.read_bytes())
    regular_record = json.loads(REGULAR.read_bytes())
    endpoint_record = json.loads(ENDPOINT.read_bytes())
    if not all(
        record["status"] == "PROVED"
        for record in (projection, base, open_record, open_v, regular_record, endpoint_record)
    ):
        raise AssertionError("bad source status")
    source = projection_core.build_record(include_catalog=True)
    if source["semantic_sha256"] != projection["semantic_sha256"]:
        raise AssertionError("projection source changed")
    events, event_serial = regular.raw_event_map(source, base)
    coefficient_factors = coefficient_factor_map(events)
    endpoint_factor_ids = endpoint_factors(open_v)
    wall_degrees = {
        row["id"]: row["fiber_degree"]
        for row in source["fiber_walls"]["catalog"]
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
        endpoint_factor_ids,
        coefficient_factors,
        wall_degrees,
    )
    if observed["factor_census"] != {27: 1_694, 38: 1_694}:
        raise AssertionError("coefficient-only factor census changed")
    if observed["remaining_census"] != {
        COEFFICIENT | ENDPOINT_REASON: 1_694,
        COUNT_CHANGE | COEFFICIENT | ENDPOINT_REASON: 2_888,
    }:
        raise AssertionError("remaining coefficient-endpoint census changed")

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
            "DIAG3_PAIR_GLOBAL_FOUR_SUPPORT_COEFFICIENT_ONLY_U_SECTION_V_LIFT_"
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

    factor_census = {str(key): value for key, value in sorted(observed["factor_census"].items())}
    degree_drop_census = string_census(observed["degree_drop_census"])
    pattern_census = string_census(observed["pattern_census"])
    remaining_census = {str(key): value for key, value in sorted(observed["remaining_census"].items())}
    coefficient_map_serial = [
        [list(owner), list(factors)]
        for owner, factors in sorted(coefficient_factors.items())
    ]
    semantic_payload = {
        "endpoint_u_section_semantic_sha256": endpoint_record["semantic_sha256"],
        "raw_event_map_sha256": digest(event_serial),
        "coefficient_factor_map_sha256": digest(coefficient_map_serial),
        "partition_sha256": digest(partition),
        "factor_census": factor_census,
        "degree_drop_census": degree_drop_census,
        "pattern_census": pattern_census,
        "remaining_census": remaining_census,
    }
    record = {
        "format": FORMAT,
        "status": "PROVED",
        "scope": {
            "open_t_coefficient_only_u_section_v_lift": "COMPLETE",
            "remaining_open_t_coefficient_endpoint_u_section_v_lift": "NOT_YET_CONSTRUCTED",
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
            "prior_residual_sections": 7_970,
        },
        "coefficient_only_u_section_v_lift": {
            "completed_sections": observed["completed_sections"],
            "remaining_sections": sum(observed["remaining_census"].values()),
            "completed_factor_census": factor_census,
            "degree_drop_census": degree_drop_census,
            "event_inversion_group_pattern_census": pattern_census,
            "simple_leading_coefficient_events": observed["coefficient_events"],
            "completed_raw_resultant_events": observed["resultant_events"],
            "visible_inversion_edges": observed["inversions"],
            "interior_collision_groups": observed["groups"],
            "section_v_root_points": observed["points"],
            "section_open_v_strips": observed["strips"],
            "lifted_cells": observed["points"] + observed["strips"],
            "coefficient_factor_map_sha256": digest(coefficient_map_serial),
            "raw_event_map_sha256": digest(event_serial),
            "partition_sha256": digest(partition),
            "remaining_reason_census": remaining_census,
        },
        "artifact_shards": {
            "format": SHARD_FORMAT,
            "shard_count": SHARD_COUNT,
            "shards": shard_rows,
        },
        "semantic_sha256": digest(semantic_payload),
        "resource_effect": {
            "prior_residual_ceiling": 7_970,
            "sections_examined": 7_970,
            "ceiling_not_triggered": True,
            "next_stage": (
                "resolve the 4582 coefficient-plus-endpoint u-section fibers, "
                "then lift all 261571 base cells over algebraic t sections"
            ),
        },
        "generator_dependency": {
            "python": sys.version.split()[0],
            "independent_verifier": "STANDARD_LIBRARY_STRUCTURAL_REPLAY",
        },
        "theorem_effect": (
            "Exact unbounded degree-drop analysis completes 3388 additional "
            "coefficient-only algebraic-u v fibers and 79816 cells over open t "
            "sectors; 4582 coefficient-plus-endpoint fibers, all algebraic-t v "
            "lifts, global gluing, labels, middle-rank replay, and diagonal three "
            "remain open; honest 9DVL score remains 2/9."
        ),
    }
    OUTPUT.write_text(
        json.dumps(record, sort_keys=True, separators=(",", ":")) + "\n",
        encoding="ascii",
    )
    print("WROTE", OUTPUT)
    print("COMPLETED", observed["completed_sections"], "REMAINING", sum(observed["remaining_census"].values()))
    print("V_POINTS", observed["points"], "V_STRIPS", observed["strips"], "CELLS", observed["points"] + observed["strips"])


if __name__ == "__main__":
    main()
