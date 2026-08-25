#!/usr/bin/env python3
"""Build the endpoint-only count-change algebraic-u-section v lift.

This checkpoint attaches precisely the residual open-t algebraic-u sections
whose only non-regular feature is one simple v=0 or v=1 crossing.  Sections
carrying a coefficient event remain fail-closed.
"""

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
OUTPUT = HERE / "data" / "DIAG3_PAIR_GLOBAL_FOUR_SUPPORT_ENDPOINT_U_SECTION_V_LIFT.json"

FORMAT = "diag3-pair-global-row2599-four-support-endpoint-u-section-v-lift-v1"
SHARD_FORMAT = (
    "diag3-pair-global-row2599-four-support-endpoint-u-section-v-lift-shard-v1"
)
SHARD_COUNT = 32
SECTOR_COUNT = 1_694
SECTION_COUNT = 132_134

COUNT_CHANGE = regular.COUNT_CHANGE
COEFFICIENT = regular.COEFFICIENT
ENDPOINT = regular.ENDPOINT
TARGET_REASON = COUNT_CHANGE | ENDPOINT


def digest(value) -> str:
    return sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":")).encode("ascii")
    ).hexdigest()


def canonical_gzip_json(value) -> bytes:
    encoded = (
        json.dumps(value, sort_keys=True, separators=(",", ":")) + "\n"
    ).encode("ascii")
    return gzip.compress(encoded, compresslevel=9, mtime=0)


def endpoint_owner_map(projection, open_v):
    """Map each base factor to the exact bounded-fiber endpoint owners."""

    wall_degree = {
        row["id"]: row["fiber_degree"]
        for row in projection["fiber_walls"]["catalog"]
    }
    owners = defaultdict(list)
    serial = []
    for row in open_v["v_endpoint_audit"]["factorizations"]:
        for factor_id, multiplicity in row["base_factors"]:
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


def reason_for(left, right, current_events, endpoint_owners, factor_id):
    reason = 0
    if len(left) != len(right):
        reason |= COUNT_CHANGE
    if any(event[0] != "resultant" for event in current_events):
        reason |= COEFFICIENT
    if factor_id in endpoint_owners:
        reason |= ENDPOINT
    return reason


def analyze(sectors, sector_ids, signature_catalog, events, endpoint_owners):
    shards = [[] for _ in range(SHARD_COUNT)]
    factor_census = Counter()
    attachment_census = Counter()
    pattern_census = Counter()
    remaining_census = Counter()
    regular_sections = completed_sections = 0
    raw_events = inversions = collision_groups = 0
    root_points = strips = 0

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
            if not current_events:
                raise AssertionError("u section has no raw projection event")
            if any(event[2] != 1 for event in current_events):
                raise AssertionError("higher-multiplicity u-section event")

            reason = reason_for(
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
            if len(owners) != 1:
                raise AssertionError("endpoint-only factor has multiple endpoint owners")
            endpoint_wall, endpoint, multiplicity, degree = owners[0]
            if multiplicity != 1 or degree != 1:
                raise AssertionError("endpoint-only attachment is not a simple linear root")
            endpoint_token = (endpoint_wall, 0)
            left_set = set(left)
            right_set = set(right)
            symmetric_difference = left_set ^ right_set
            if symmetric_difference != {endpoint_token}:
                raise AssertionError("root-count change is not the certified endpoint token")
            if (endpoint_token in left_set) == (endpoint_token in right_set):
                raise AssertionError("endpoint token does not cross exactly one side")
            direction = "exit" if endpoint_token in left_set else "entry"

            edges = regular.inversion_edges(left, right)
            groups = regular.clique_components(edges)
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
            common = left_set & right_set
            bounded_walls = {token[0] for token in common}
            for pair, count in (event_owners - inversion_owners).items():
                if count and set(pair) <= bounded_walls:
                    raise AssertionError(
                        "invisible resultant has both owners in the common bounded stack"
                    )
            if any(endpoint_token in group for group in groups):
                raise AssertionError("endpoint token was incorrectly counted as interior")

            section_points = len(common) - sum(len(group) - 1 for group in groups)
            section_strips = section_points + 1
            group_sizes = tuple(sorted(len(group) for group in groups))
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
            inversions += len(edges)
            collision_groups += len(groups)
            root_points += section_points
            strips += section_strips

        shard_index = SHARD_COUNT * sector_id // SECTOR_COUNT
        shards[shard_index].append(
            {"completed": completed, "remaining": remaining}
        )

    if regular_sections != 120_174:
        raise AssertionError("prior regular-section count changed")
    if completed_sections != 3_990:
        raise AssertionError("endpoint-only completion count changed")
    if sum(remaining_census.values()) != 7_970:
        raise AssertionError("coefficient-event residue changed")
    if regular_sections + completed_sections + sum(remaining_census.values()) != SECTION_COUNT:
        raise AssertionError("u-section partition changed")
    return {
        "shards": shards,
        "factor_census": factor_census,
        "attachment_census": attachment_census,
        "pattern_census": pattern_census,
        "remaining_census": remaining_census,
        "regular_sections": regular_sections,
        "completed_sections": completed_sections,
        "raw_events": raw_events,
        "inversions": inversions,
        "collision_groups": collision_groups,
        "root_points": root_points,
        "strips": strips,
    }


def string_census(counter):
    return {",".join(map(str, key)): value for key, value in sorted(counter.items())}


def main():
    projection = json.loads(PROJECTION.read_bytes())
    base = json.loads(gzip.decompress(BASE.read_bytes()))
    open_record = json.loads(OPEN.read_bytes())
    open_v = json.loads(OPEN_V.read_bytes())
    regular_record = json.loads(REGULAR.read_bytes())
    if not (
        projection["status"]
        == base["status"]
        == open_record["status"]
        == open_v["status"]
        == regular_record["status"]
        == "PROVED"
    ):
        raise AssertionError("bad source status")
    source = projection_core.build_record(include_catalog=True)
    if source["semantic_sha256"] != projection["semantic_sha256"]:
        raise AssertionError("projection source changed")

    events, event_serial = regular.raw_event_map(source, base)
    endpoint_owners, endpoint_serial = endpoint_owner_map(source, open_v)
    sectors = regular.load_shard_field(open_record, "sectors")
    sector_ids = regular.load_shard_field(open_v, "strip_signature_ids")
    signature_catalog = [
        tuple(tuple(token) for token in sequence)
        for sequence in open_v["open_cell_v_lift"]["signature_catalog"]
    ]
    observed = analyze(
        sectors, sector_ids, signature_catalog, events, endpoint_owners
    )
    if observed["factor_census"] != {12: 1_194, 57: 1_694, 86: 1_102}:
        raise AssertionError("endpoint-only factor census changed")
    if observed["remaining_census"] != {
        COEFFICIENT: 3_388,
        COEFFICIENT | ENDPOINT: 1_694,
        COUNT_CHANGE | COEFFICIENT | ENDPOINT: 2_888,
    }:
        raise AssertionError("remaining coefficient-event census changed")

    shard_rows = []
    partition = []
    for shard_index, sector_rows in enumerate(observed["shards"]):
        sector_start = SECTOR_COUNT * shard_index // SHARD_COUNT
        sector_end = SECTOR_COUNT * (shard_index + 1) // SHARD_COUNT
        shard = {
            "format": SHARD_FORMAT,
            "shard_index": shard_index,
            "shard_count": SHARD_COUNT,
            "sector_start": sector_start,
            "sector_end": sector_end,
            "sectors": sector_rows,
        }
        compressed = canonical_gzip_json(shard)
        name = (
            "DIAG3_PAIR_GLOBAL_FOUR_SUPPORT_ENDPOINT_U_SECTION_V_LIFT_"
            f"SHARD_{shard_index:02d}_OF_{SHARD_COUNT}.json.gz"
        )
        (OUTPUT.parent / name).write_bytes(compressed)
        shard_rows.append(
            {
                "index": shard_index,
                "path": name,
                "sector_start": sector_start,
                "sector_end": sector_end,
                "bytes": len(compressed),
                "sha256": sha256(compressed).hexdigest(),
            }
        )
        partition.extend(sector_rows)

    factor_census = {str(key): value for key, value in sorted(observed["factor_census"].items())}
    attachment_census = string_census(observed["attachment_census"])
    pattern_census = string_census(observed["pattern_census"])
    remaining_census = {
        str(key): value for key, value in sorted(observed["remaining_census"].items())
    }
    semantic_payload = {
        "regular_u_section_semantic_sha256": regular_record["semantic_sha256"],
        "raw_event_map_sha256": digest(event_serial),
        "endpoint_owner_map_sha256": digest(endpoint_serial),
        "partition_sha256": digest(partition),
        "factor_census": factor_census,
        "attachment_census": attachment_census,
        "pattern_census": pattern_census,
        "remaining_census": remaining_census,
    }
    record = {
        "format": FORMAT,
        "status": "PROVED",
        "scope": {
            "open_t_endpoint_only_count_change_u_section_v_lift": "COMPLETE",
            "remaining_open_t_coefficient_event_u_section_v_lift": "NOT_YET_CONSTRUCTED",
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
            "prior_regular_sections": observed["regular_sections"],
            "prior_residual_sections": 11_960,
        },
        "endpoint_u_section_v_lift": {
            "completed_sections": observed["completed_sections"],
            "remaining_sections": sum(observed["remaining_census"].values()),
            "completed_factor_census": factor_census,
            "attachment_census": attachment_census,
            "event_inversion_group_pattern_census": pattern_census,
            "completed_raw_resultant_events": observed["raw_events"],
            "visible_inversion_edges": observed["inversions"],
            "interior_collision_groups": observed["collision_groups"],
            "section_v_root_points": observed["root_points"],
            "section_open_v_strips": observed["strips"],
            "lifted_cells": observed["root_points"] + observed["strips"],
            "endpoint_owner_map_sha256": digest(endpoint_serial),
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
            "prior_residual_ceiling": 11_960,
            "sections_examined": 11_960,
            "ceiling_not_triggered": True,
            "next_stage": (
                "resolve the 7970 coefficient-event u-section fibers, then "
                "lift all 261571 base cells over algebraic t sections"
            ),
        },
        "generator_dependency": {
            "python": sys.version.split()[0],
            "independent_verifier": "STANDARD_LIBRARY_STRUCTURAL_REPLAY",
        },
        "theorem_effect": (
            "Exact endpoint attachments complete 3990 additional algebraic-u "
            "v fibers and 120468 cells over open t sectors; 7970 coefficient-"
            "event fibers, all algebraic-t v lifts, global gluing, labels, "
            "middle-rank replay, and diagonal three remain open; honest 9DVL "
            "score remains 2/9."
        ),
    }
    OUTPUT.write_text(
        json.dumps(record, sort_keys=True, separators=(",", ":")) + "\n",
        encoding="ascii",
    )
    print("WROTE", OUTPUT)
    print("COMPLETED", observed["completed_sections"], "REMAINING", sum(observed["remaining_census"].values()))
    print("V_POINTS", observed["root_points"], "V_STRIPS", observed["strips"], "CELLS", observed["root_points"] + observed["strips"])


if __name__ == "__main__":
    main()
