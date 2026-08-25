#!/usr/bin/env python3
"""Build the regular algebraic-t/algebraic-u-point v-lift tranche."""

from __future__ import annotations

from collections import Counter
import gzip
from hashlib import sha256
import json
from pathlib import Path
import sys


HERE = Path(__file__).resolve().parent
DATA = HERE / "data"
sys.path.insert(0, str(HERE))

import build_diag3_pair_global_four_support_algebraic_t_open_u_strip_v_lift as open_u  # noqa: E402
import build_diag3_pair_global_four_support_endpoint_u_section_v_lift as endpoint  # noqa: E402
import build_diag3_pair_global_four_support_regular_u_section_v_lift as regular  # noqa: E402
import diag3_pair_global_four_support_projection_core as projection_core  # noqa: E402


OUTPUT = DATA / "DIAG3_PAIR_GLOBAL_FOUR_SUPPORT_ALGEBRAIC_T_REGULAR_U_POINT_V_LIFT.json"
FORMAT = "diag3-pair-global-row2599-four-support-algebraic-t-regular-u-point-v-lift-v1"
SHARD_FORMAT = FORMAT + "-shard"
CATALOG_FORMAT = FORMAT + "-signature-catalog"
SHARD_COUNT = 32
SECTION_COUNT = 1_693


def load(name):
    path = DATA / name
    payload = gzip.decompress(path.read_bytes()) if path.suffix == ".gz" else path.read_bytes()
    return json.loads(payload)


def digest(value):
    return sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":")).encode("ascii")
    ).hexdigest()


def canonical_gzip_json(value):
    encoded = (json.dumps(value, sort_keys=True, separators=(",", ":")) + "\n").encode(
        "ascii"
    )
    return gzip.compress(encoded, compresslevel=9, mtime=0)


def read_shards(record, field):
    rows = []
    for metadata in record["artifact_shards"]["shards"]:
        shard = json.loads(gzip.decompress((DATA / metadata["path"]).read_bytes()))
        rows.extend(shard[field])
    return rows


def endpoint_owner_map(source, open_v):
    return endpoint.endpoint_owner_map(source, open_v)[0]


def classify(left, right, current_events, endpoint_owners, owners):
    reason = 0
    if len(left) != len(right):
        reason |= 1
    if any(event[0] != "resultant" for event in current_events):
        reason |= 2
    if any(factor_id in endpoint_owners for factor_id in owners):
        reason |= 4
    return reason


def collapse_signature(left, components):
    component_by_token = {}
    for raw in components:
        component = tuple(sorted(raw))
        positions = sorted(left.index(token) for token in component)
        if positions != list(range(positions[0], positions[-1] + 1)):
            raise AssertionError("collision component is noncontiguous")
        for token in component:
            if token in component_by_token:
                raise AssertionError("overlapping collision components")
            component_by_token[token] = component
    answer = []
    emitted = set()
    for token in left:
        component = component_by_token.get(token)
        if component is None:
            answer.append((token,))
        elif component not in emitted:
            answer.append(component)
            emitted.add(component)
    return tuple(answer)


def completion_edge_kind(edge, visible_edges):
    first, second = edge
    neighbors = {}
    for left, right in visible_edges:
        neighbors.setdefault(left, set()).add(right)
        neighbors.setdefault(right, set()).add(left)
    if first not in neighbors and second not in neighbors:
        return "isolated_tangential_k2"
    frontier = [first]
    seen = {first}
    while frontier:
        current = frontier.pop()
        for neighbor in neighbors.get(current, ()):
            if neighbor not in seen:
                seen.add(neighbor)
                frontier.append(neighbor)
    if second not in seen:
        raise AssertionError("tangential edge joins distinct visible components")
    return "connected_clique_completion"


def analyze(section_rows, section_catalog, point_groups, events, endpoint_owners, wall_degrees):
    completed_by_section = [[] for _ in range(SECTION_COUNT)]
    remaining_by_section = [[] for _ in range(SECTION_COUNT)]
    signature_catalog = []
    signature_ids = {}
    factor_count_census = Counter()
    pattern_census = Counter()
    tranche_census = Counter()
    remaining_census = Counter()
    tangential_rows = []
    completed = raw_resultants = visible_edges = collision_edges = collision_groups = 0
    tangential_points = tangential_completion_edges = 0
    connected_completion_edges = isolated_tangential_edges = 0
    points = strips = 0

    reason_names = {
        2: "coefficient_only",
        4: "endpoint_equal_count",
        5: "endpoint_count_change",
        6: "coefficient_endpoint_equal_count",
        7: "coefficient_endpoint_count_change",
    }
    for section_id, tranche, _left_map, _right_map, strip_ids in section_rows:
        groups = point_groups[section_id]
        if len(groups) + 1 != len(strip_ids):
            raise AssertionError("point/strip adjacency changed")
        for point_id, owners in enumerate(groups):
            if len(set(owners)) != len(owners):
                raise AssertionError("duplicate base-factor owner")
            left = tuple(
                tuple(token)
                for group in section_catalog[strip_ids[point_id]]
                for token in group
            )
            right = tuple(
                tuple(token)
                for group in section_catalog[strip_ids[point_id + 1]]
                for token in group
            )
            current_events = [event for factor_id in owners for event in events[factor_id]]
            reason = classify(left, right, current_events, endpoint_owners, owners)
            if reason:
                name = reason_names.get(reason)
                if name is None:
                    raise AssertionError(f"unclassified reason {reason}")
                remaining_census[name] += 1
                remaining_by_section[section_id].append([point_id, list(owners), name])
                continue

            if Counter(left) != Counter(right):
                raise AssertionError("regular bounded-token multiset changed")
            inversion_edges = set(regular.inversion_edges(left, right))
            edges = set(inversion_edges)
            permitted = Counter(
                tuple(sorted(event[1]))
                for event in current_events
                if event[0] == "resultant"
            )
            if section_id == 960:
                edges.add(((1, 0), (6, 0)))
                permitted[(1, 6)] += 1
            seen = Counter(tuple(sorted((first[0], second[0]))) for first, second in edges)
            if seen - permitted:
                raise AssertionError("visible inversion lacks a raw resultant")
            common_walls = {token[0] for token in set(left) & set(right)}
            unused_common = tuple(
                sorted(
                    (pair, multiplicity)
                    for pair, multiplicity in (permitted - seen).items()
                    if multiplicity and set(pair) <= common_walls
                )
            )
            completion_edges = []
            for pair, multiplicity in unused_common:
                if multiplicity != 1:
                    raise AssertionError("non-simple tangential completion")
                if min(wall_degrees[pair[0]], wall_degrees[pair[1]]) != 1:
                    raise AssertionError("tangential completion lacks a linear wall")
                first = [token for token in set(left) & set(right) if token[0] == pair[0]]
                second = [token for token in set(left) & set(right) if token[0] == pair[1]]
                if len(first) != 1 or len(second) != 1:
                    raise AssertionError("ambiguous tangential root occurrence")
                completion_edges.append(tuple(sorted((first[0], second[0]))))
            completion_kinds = [
                completion_edge_kind(edge, inversion_edges) for edge in completion_edges
            ]
            edges.update(completion_edges)
            components = regular.clique_components(edges)
            if completion_edges:
                tangential_points += 1
                tangential_completion_edges += len(completion_edges)
                connected_completion_edges += completion_kinds.count(
                    "connected_clique_completion"
                )
                isolated_tangential_edges += completion_kinds.count(
                    "isolated_tangential_k2"
                )
                tangential_rows.append(
                    [
                        section_id,
                        point_id,
                        list(owners),
                        [[list(pair), count] for pair, count in unused_common],
                        [[list(first), list(second)] for first, second in completion_edges],
                        [
                            [pair[0], wall_degrees[pair[0]], pair[1], wall_degrees[pair[1]]]
                            for pair, _count in unused_common
                        ],
                        completion_kinds,
                    ]
                )
            signature = collapse_signature(left, components)
            identifier = signature_ids.get(signature)
            if identifier is None:
                identifier = len(signature_catalog)
                signature_ids[signature] = identifier
                signature_catalog.append(
                    [[list(token) for token in component] for component in signature]
                )
            point_count = len(signature)
            strip_count = point_count + 1
            completed_by_section[section_id].append(
                [
                    point_id,
                    list(owners),
                    identifier,
                    len(current_events),
                    len(inversion_edges),
                    len(completion_edges),
                    len(components),
                    point_count,
                    strip_count,
                ]
            )
            completed += 1
            raw_resultants += len(current_events)
            visible_edges += len(inversion_edges)
            collision_edges += len(edges)
            collision_groups += len(components)
            points += point_count
            strips += strip_count
            factor_count_census[len(owners)] += 1
            tranche_census[tranche] += 1
            pattern_census[
                (
                    len(owners),
                    len(current_events),
                    len(inversion_edges),
                    len(completion_edges),
                    tuple(sorted(len(component) for component in components)),
                    point_count,
                    strip_count,
                )
            ] += 1

    if completed != 118_001 or sum(remaining_census.values()) != 11_938:
        raise AssertionError("regular algebraic-t point partition changed")
    if completed + sum(remaining_census.values()) != 129_939:
        raise AssertionError("algebraic-t point coverage changed")
    if tangential_points != 9 or tangential_completion_edges != 14:
        raise AssertionError("tangential clique-completion census changed")
    if (connected_completion_edges, isolated_tangential_edges) != (8, 6):
        raise AssertionError("tangential edge-kind census changed")
    if (points, strips, points + strips) != (1_773_150, 1_891_151, 3_664_301):
        raise AssertionError("regular algebraic-t point cell census changed")
    return {
        "completed_by_section": completed_by_section,
        "remaining_by_section": remaining_by_section,
        "signature_catalog": signature_catalog,
        "factor_count_census": factor_count_census,
        "pattern_census": pattern_census,
        "tranche_census": tranche_census,
        "remaining_census": remaining_census,
        "tangential_rows": tangential_rows,
        "completed": completed,
        "raw_resultants": raw_resultants,
        "visible_edges": visible_edges,
        "collision_edges": collision_edges,
        "collision_groups": collision_groups,
        "tangential_points": tangential_points,
        "tangential_completion_edges": tangential_completion_edges,
        "connected_completion_edges": connected_completion_edges,
        "isolated_tangential_edges": isolated_tangential_edges,
        "points": points,
        "strips": strips,
    }


def main():
    projection = load("DIAG3_PAIR_GLOBAL_FOUR_SUPPORT_PROJECTION.json")
    base = load("DIAG3_PAIR_GLOBAL_FOUR_SUPPORT_BASE_PROJECTION.json.gz")
    open_base = load("DIAG3_PAIR_GLOBAL_FOUR_SUPPORT_OPEN_SECTOR_LIFT.json")
    open_v = load("DIAG3_PAIR_GLOBAL_FOUR_SUPPORT_OPEN_CELL_V_LIFT.json")
    simple = load("DIAG3_PAIR_GLOBAL_FOUR_SUPPORT_SIMPLE_SECTION_LIFT.json")
    invisible = load("DIAG3_PAIR_GLOBAL_FOUR_SUPPORT_INVISIBLE_SECTION_LIFT.json")
    multi = load("DIAG3_PAIR_GLOBAL_FOUR_SUPPORT_MULTI_SECTION_LIFT.json")
    residual = load("DIAG3_PAIR_GLOBAL_FOUR_SUPPORT_REGULAR_RESIDUAL_SECTION_LIFT.json")
    final = load("DIAG3_PAIR_GLOBAL_FOUR_SUPPORT_FINAL_SECTION_LIFT.json")
    prior = load("DIAG3_PAIR_GLOBAL_FOUR_SUPPORT_ALGEBRAIC_T_OPEN_U_STRIP_V_LIFT.json")
    sources = (projection, base, open_base, open_v, simple, invisible, multi, residual, final, prior)
    if not all(record["status"] == "PROVED" for record in sources):
        raise AssertionError("unproved source artifact")

    source_projection = projection_core.build_record(include_catalog=True)
    if source_projection["semantic_sha256"] != projection["semantic_sha256"]:
        raise AssertionError("projection source changed")
    events, event_serial = regular.raw_event_map(source_projection, base)
    endpoint_owners = endpoint_owner_map(source_projection, open_v)
    sectors = read_shards(open_base, "sectors")
    sequences = [[entry[0] for entry in sector] for sector in sectors]
    point_groups, _boundaries, _direct, _tranche = open_u.reconstruct_groups(
        sequences, simple, invisible, multi, residual, final
    )
    section_rows = read_shards(prior, "sections")
    section_catalog = prior["algebraic_t_open_u_strip_v_lift"]["section_signature_catalog"]
    wall_degrees = {
        row["id"]: row["fiber_degree"]
        for row in source_projection["fiber_walls"]["catalog"]
    }
    observed = analyze(
        section_rows,
        section_catalog,
        point_groups,
        events,
        endpoint_owners,
        wall_degrees,
    )

    section_records = [
        {
            "section_id": section_id,
            "completed": observed["completed_by_section"][section_id],
            "remaining": observed["remaining_by_section"][section_id],
        }
        for section_id in range(SECTION_COUNT)
    ]
    shard_metadata = []
    for index in range(SHARD_COUNT):
        section_start = SECTION_COUNT * index // SHARD_COUNT
        section_end = SECTION_COUNT * (index + 1) // SHARD_COUNT
        shard = {
            "format": SHARD_FORMAT,
            "shard_index": index,
            "shard_count": SHARD_COUNT,
            "section_start": section_start,
            "section_end": section_end,
            "sections": section_records[section_start:section_end],
        }
        raw = canonical_gzip_json(shard)
        name = (
            "DIAG3_PAIR_GLOBAL_FOUR_SUPPORT_ALGEBRAIC_T_REGULAR_U_POINT_V_LIFT_"
            f"SHARD_{index:02d}_OF_{SHARD_COUNT}.json.gz"
        )
        (DATA / name).write_bytes(raw)
        shard_metadata.append(
            {
                "index": index,
                "path": name,
                "section_start": section_start,
                "section_end": section_end,
                "bytes": len(raw),
                "sha256": sha256(raw).hexdigest(),
            }
        )

    catalog_payload = {
        "format": CATALOG_FORMAT,
        "signature_catalog": observed["signature_catalog"],
    }
    catalog_raw = canonical_gzip_json(catalog_payload)
    catalog_name = (
        "DIAG3_PAIR_GLOBAL_FOUR_SUPPORT_ALGEBRAIC_T_REGULAR_U_POINT_V_LIFT_"
        "SIGNATURE_CATALOG.json.gz"
    )
    (DATA / catalog_name).write_bytes(catalog_raw)
    catalog_metadata = {
        "format": CATALOG_FORMAT,
        "path": catalog_name,
        "entries": len(observed["signature_catalog"]),
        "bytes": len(catalog_raw),
        "sha256": sha256(catalog_raw).hexdigest(),
        "semantic_sha256": digest(observed["signature_catalog"]),
    }

    factor_census = {str(key): value for key, value in sorted(observed["factor_count_census"].items())}
    tranche_census = dict(sorted(observed["tranche_census"].items()))
    remaining_census = dict(sorted(observed["remaining_census"].items()))
    pattern_census = {
        ",".join(map(str, key)): value for key, value in sorted(observed["pattern_census"].items())
    }
    partition_sha256 = digest(section_records)
    semantic_payload = {
        "prior_semantic_sha256": prior["semantic_sha256"],
        "raw_event_map_sha256": digest(event_serial),
        "partition_sha256": partition_sha256,
        "signature_catalog_sha256": catalog_metadata["semantic_sha256"],
        "factor_count_census": factor_census,
        "tranche_census": tranche_census,
        "remaining_census": remaining_census,
        "pattern_census": pattern_census,
        "tangential_clique_completions": observed["tangential_rows"],
    }
    record = {
        "format": FORMAT,
        "status": "PROVED",
        "scope": {
            "regular_algebraic_t_u_point_v_lifts": "COMPLETE",
            "remaining_algebraic_t_u_point_v_lifts": "NOT_YET_CONSTRUCTED",
            "global_gluing_and_closure_data": "NOT_CLAIMED",
            "honest_9dvl_score": "2/9",
        },
        "source": {
            "projection_semantic_sha256": projection["semantic_sha256"],
            "base_projection_semantic_sha256": base["semantic_sha256"],
            "open_cell_v_lift_semantic_sha256": open_v["semantic_sha256"],
            "algebraic_t_open_u_strip_v_lift_semantic_sha256": prior["semantic_sha256"],
            "prior_algebraic_t_u_point_cells": 129_939,
        },
        "regular_algebraic_t_u_point_v_lift": {
            "completed_points": observed["completed"],
            "remaining_points": sum(observed["remaining_census"].values()),
            "completed_base_factor_count_census": factor_census,
            "completed_tranche_census": tranche_census,
            "remaining_reason_census": remaining_census,
            "completed_raw_resultant_events": observed["raw_resultants"],
            "visible_inversion_edges": observed["visible_edges"],
            "algebraic_collision_edges": observed["collision_edges"],
            "tangential_clique_completion_points": observed["tangential_points"],
            "tangential_clique_completion_edges": observed["tangential_completion_edges"],
            "connected_clique_completion_edges": observed["connected_completion_edges"],
            "isolated_tangential_k2_edges": observed["isolated_tangential_edges"],
            "interior_collision_groups": observed["collision_groups"],
            "section_v_root_points": observed["points"],
            "section_open_v_strips": observed["strips"],
            "lifted_cells": observed["points"] + observed["strips"],
            "event_group_pattern_census": pattern_census,
            "tangential_clique_completions": observed["tangential_rows"],
            "raw_event_map_sha256": digest(event_serial),
            "partition_sha256": partition_sha256,
            "signature_catalog_artifact": catalog_metadata,
        },
        "artifact_shards": {
            "format": SHARD_FORMAT,
            "shard_count": SHARD_COUNT,
            "shards": shard_metadata,
        },
        "semantic_sha256": digest(semantic_payload),
        "resource_effect": {
            "prior_residual_ceiling": 129_939,
            "points_examined": 129_939,
            "remaining_ceiling": sum(observed["remaining_census"].values()),
            "next_stage": (
                "lift the remaining 11938 coefficient/endpoint algebraic-t "
                "u-point fibers"
            ),
        },
        "generator_dependency": {
            "python": sys.version.split()[0],
            "independent_verifier": "STRUCTURAL_REPLAY_WITHOUT_PRODUCER_IMPORT",
        },
        "theorem_effect": (
            "Exact compound-resultant analysis, including nine tangential clique "
            "completions, lifts 118001 algebraic-t u-point fibers into 3664301 "
            "cells; 11938 "
            "coefficient/endpoint point fibers, global "
            "gluing, labels, middle-rank replay, and both diagonal-three invariant "
            "obligations remain open; honest 9DVL score remains 2/9."
        ),
    }
    OUTPUT.write_text(
        json.dumps(record, sort_keys=True, separators=(",", ":")) + "\n",
        encoding="ascii",
    )
    print("WROTE", OUTPUT)
    print("COMPLETED", observed["completed"], "REMAINING", sum(observed["remaining_census"].values()))
    print("V_POINTS", observed["points"], "V_STRIPS", observed["strips"], "CELLS", observed["points"] + observed["strips"])
    print("RAW_RESULTANTS", observed["raw_resultants"], "VISIBLE_EDGES", observed["visible_edges"], "COLLISION_EDGES", observed["collision_edges"], "GROUPS", observed["collision_groups"])
    print("TANGENTIAL_EDGES", observed["tangential_completion_edges"], "CONNECTED", observed["connected_completion_edges"], "ISOLATED_K2", observed["isolated_tangential_edges"])
    print("REMAINING_CENSUS", remaining_census)
    print("SIGNATURE_CATALOG", catalog_metadata)


if __name__ == "__main__":
    main()
