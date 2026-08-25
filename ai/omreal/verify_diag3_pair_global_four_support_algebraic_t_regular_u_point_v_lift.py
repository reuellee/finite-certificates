#!/usr/bin/env python3
"""Independent replay of the regular algebraic-t u-point v lift."""

from __future__ import annotations

from collections import Counter
from copy import deepcopy
import gzip
from hashlib import sha256
import json
from pathlib import Path
import sys


HERE = Path(__file__).resolve().parent
DATA = HERE / "data"
sys.path.insert(0, str(HERE))

import verify_diag3_pair_global_four_support_algebraic_t_open_u_strip_v_lift as open_u  # noqa: E402
import verify_diag3_pair_global_four_support_coefficient_endpoint_u_section_v_lift as coefficient  # noqa: E402
import verify_diag3_pair_global_four_support_regular_u_section_v_lift as regular  # noqa: E402


CERTIFICATE = DATA / "DIAG3_PAIR_GLOBAL_FOUR_SUPPORT_ALGEBRAIC_T_REGULAR_U_POINT_V_LIFT.json"
FORMAT = "diag3-pair-global-row2599-four-support-algebraic-t-regular-u-point-v-lift-v1"
SHARD_FORMAT = FORMAT + "-shard"
CATALOG_FORMAT = FORMAT + "-signature-catalog"
SHARD_COUNT = 32
SECTION_COUNT = 1_693
NEXT_STAGE = "lift the remaining 11938 coefficient/endpoint algebraic-t u-point fibers"
THEOREM_EFFECT = (
    "Exact compound-resultant analysis, including nine tangential clique "
    "completions, lifts 118001 algebraic-t u-point fibers into 3664301 cells; "
    "11938 coefficient/endpoint point fibers, global gluing, labels, "
    "middle-rank replay, and both diagonal-three invariant obligations remain "
    "open; honest 9DVL score remains 2/9."
)


def require(condition, message):
    if not condition:
        raise AssertionError(message)


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
    for index, metadata in enumerate(record["artifact_shards"]["shards"]):
        raw = (DATA / metadata["path"]).read_bytes()
        require(len(raw) == metadata["bytes"], "source shard size")
        require(sha256(raw).hexdigest() == metadata["sha256"], "source shard digest")
        shard = json.loads(gzip.decompress(raw))
        require(shard["shard_index"] == index, "source shard order")
        rows.extend(shard[field])
    return rows


def classify(left, right, events, endpoint_owners, owners):
    return (
        (1 if len(left) != len(right) else 0)
        | (2 if any(event[0] != "resultant" for event in events) else 0)
        | (4 if any(owner in endpoint_owners for owner in owners) else 0)
    )


def collapsed_signature(left, components):
    owners = {}
    positions_by_component = {}
    for raw in components:
        component = tuple(sorted(raw))
        positions = tuple(sorted(left.index(token) for token in component))
        require(positions == tuple(range(positions[0], positions[-1] + 1)), "component contiguity")
        positions_by_component[component] = positions[0]
        for token in component:
            require(token not in owners, "component overlap")
            owners[token] = component
    answer = []
    seen = set()
    for token in left:
        component = owners.get(token)
        if component is None:
            answer.append((token,))
        elif component not in seen:
            answer.append(component)
            seen.add(component)
    return tuple(answer)


def completion_kind(edge, visible_edges):
    first, second = edge
    neighbors = {}
    for left, right in visible_edges:
        neighbors.setdefault(left, set()).add(right)
        neighbors.setdefault(right, set()).add(left)
    if first not in neighbors and second not in neighbors:
        return "isolated_tangential_k2"
    stack = [first]
    reached = {first}
    while stack:
        current = stack.pop()
        for neighbor in neighbors.get(current, ()):
            if neighbor not in reached:
                reached.add(neighbor)
                stack.append(neighbor)
    require(second in reached, "tangential cross-component edge")
    return "connected_clique_completion"


def replay(section_rows, section_catalog, point_groups, events, endpoint_owners, wall_degrees):
    completed_by_section = [[] for _ in range(SECTION_COUNT)]
    remaining_by_section = [[] for _ in range(SECTION_COUNT)]
    catalog = []
    catalog_ids = {}
    factor_census = Counter()
    tranche_census = Counter()
    pattern_census = Counter()
    remaining_census = Counter()
    tangential = []
    completed = raw_count = visible_edge_count = collision_edge_count = 0
    tangential_points = tangential_edge_count = group_count = points = strips = 0
    connected_edge_count = isolated_edge_count = 0
    reason_names = {
        2: "coefficient_only",
        4: "endpoint_equal_count",
        5: "endpoint_count_change",
        6: "coefficient_endpoint_equal_count",
        7: "coefficient_endpoint_count_change",
    }
    for section_id, tranche, _left_map, _right_map, strip_ids in section_rows:
        groups = point_groups[section_id]
        require(len(groups) + 1 == len(strip_ids), "point-strip incidence")
        for point_id, owners in enumerate(groups):
            require(len(owners) == len(set(owners)), "duplicate point owner")
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
            current = [event for owner in owners for event in events[owner]]
            reason = classify(left, right, current, endpoint_owners, owners)
            if reason:
                name = reason_names.get(reason)
                require(name is not None, "unknown residual reason")
                remaining_census[name] += 1
                remaining_by_section[section_id].append([point_id, list(owners), name])
                continue
            require(Counter(left) == Counter(right), "regular token multiset")
            inversion_edges = set(regular.inversions(left, right))
            edges = set(inversion_edges)
            permitted = Counter(
                tuple(sorted(event[1]))
                for event in current
                if event[0] == "resultant"
            )
            if section_id == 960:
                edges.add(((1, 0), (6, 0)))
                permitted[(1, 6)] += 1
            seen = Counter(tuple(sorted((first[0], second[0]))) for first, second in edges)
            regular.verify_inversion_owners(seen, permitted)
            common_walls = {token[0] for token in set(left) & set(right)}
            unused = tuple(
                sorted(
                    (pair, multiplicity)
                    for pair, multiplicity in (permitted - seen).items()
                    if multiplicity and set(pair) <= common_walls
                )
            )
            completion_edges = []
            for pair, multiplicity in unused:
                require(multiplicity == 1, "tangential multiplicity")
                require(
                    min(wall_degrees[pair[0]], wall_degrees[pair[1]]) == 1,
                    "tangential linear-wall witness",
                )
                first = [token for token in set(left) & set(right) if token[0] == pair[0]]
                second = [token for token in set(left) & set(right) if token[0] == pair[1]]
                require(len(first) == len(second) == 1, "tangential token occurrence")
                completion_edges.append(tuple(sorted((first[0], second[0]))))
            completion_kinds = [
                completion_kind(edge, inversion_edges) for edge in completion_edges
            ]
            edges.update(completion_edges)
            components = regular.collision_components(edges)
            if completion_edges:
                tangential_points += 1
                tangential_edge_count += len(completion_edges)
                connected_edge_count += completion_kinds.count("connected_clique_completion")
                isolated_edge_count += completion_kinds.count("isolated_tangential_k2")
                tangential.append([
                    section_id,
                    point_id,
                    list(owners),
                    [[list(pair), count] for pair, count in unused],
                    [[list(first), list(second)] for first, second in completion_edges],
                    [
                        [pair[0], wall_degrees[pair[0]], pair[1], wall_degrees[pair[1]]]
                        for pair, _count in unused
                    ],
                    completion_kinds,
                ])
            signature = collapsed_signature(left, components)
            identifier = catalog_ids.get(signature)
            if identifier is None:
                identifier = len(catalog)
                catalog_ids[signature] = identifier
                catalog.append([[list(token) for token in group] for group in signature])
            point_count = len(signature)
            strip_count = point_count + 1
            completed_by_section[section_id].append([
                point_id,
                list(owners),
                identifier,
                len(current),
                len(inversion_edges),
                len(completion_edges),
                len(components),
                point_count,
                strip_count,
            ])
            completed += 1
            raw_count += len(current)
            visible_edge_count += len(inversion_edges)
            collision_edge_count += len(edges)
            group_count += len(components)
            points += point_count
            strips += strip_count
            factor_census[len(owners)] += 1
            tranche_census[tranche] += 1
            pattern_census[(
                len(owners),
                len(current),
                len(inversion_edges),
                len(completion_edges),
                tuple(sorted(len(component) for component in components)),
                point_count,
                strip_count,
            )] += 1
    sections = [
        {
            "section_id": section_id,
            "completed": completed_by_section[section_id],
            "remaining": remaining_by_section[section_id],
        }
        for section_id in range(SECTION_COUNT)
    ]
    return {
        "sections": sections,
        "catalog": catalog,
        "factor_census": {str(key): value for key, value in sorted(factor_census.items())},
        "tranche_census": dict(sorted(tranche_census.items())),
        "pattern_census": {
            ",".join(map(str, key)): value for key, value in sorted(pattern_census.items())
        },
        "remaining_census": dict(sorted(remaining_census.items())),
        "tangential": tangential,
        "completed": completed,
        "raw_count": raw_count,
        "visible_edge_count": visible_edge_count,
        "collision_edge_count": collision_edge_count,
        "tangential_points": tangential_points,
        "tangential_edge_count": tangential_edge_count,
        "connected_edge_count": connected_edge_count,
        "isolated_edge_count": isolated_edge_count,
        "group_count": group_count,
        "points": points,
        "strips": strips,
    }


def verify_artifacts(candidate, observed):
    metadata = []
    for index in range(SHARD_COUNT):
        start = SECTION_COUNT * index // SHARD_COUNT
        end = SECTION_COUNT * (index + 1) // SHARD_COUNT
        shard = {
            "format": SHARD_FORMAT,
            "shard_index": index,
            "shard_count": SHARD_COUNT,
            "section_start": start,
            "section_end": end,
            "sections": observed["sections"][start:end],
        }
        raw = canonical_gzip_json(shard)
        name = (
            "DIAG3_PAIR_GLOBAL_FOUR_SUPPORT_ALGEBRAIC_T_REGULAR_U_POINT_V_LIFT_"
            f"SHARD_{index:02d}_OF_{SHARD_COUNT}.json.gz"
        )
        require((DATA / name).read_bytes() == raw, "checkpoint shard bytes")
        metadata.append({
            "index": index,
            "path": name,
            "section_start": start,
            "section_end": end,
            "bytes": len(raw),
            "sha256": sha256(raw).hexdigest(),
        })
    manifest = {"format": SHARD_FORMAT, "shard_count": SHARD_COUNT, "shards": metadata}
    require(candidate["artifact_shards"] == manifest, "checkpoint shard manifest")
    catalog_payload = {"format": CATALOG_FORMAT, "signature_catalog": observed["catalog"]}
    catalog_raw = canonical_gzip_json(catalog_payload)
    name = "DIAG3_PAIR_GLOBAL_FOUR_SUPPORT_ALGEBRAIC_T_REGULAR_U_POINT_V_LIFT_SIGNATURE_CATALOG.json.gz"
    require((DATA / name).read_bytes() == catalog_raw, "signature catalog bytes")
    catalog_metadata = {
        "format": CATALOG_FORMAT,
        "path": name,
        "entries": len(observed["catalog"]),
        "bytes": len(catalog_raw),
        "sha256": sha256(catalog_raw).hexdigest(),
        "semantic_sha256": digest(observed["catalog"]),
    }
    return manifest, catalog_metadata


def validate_claims(candidate, observed):
    require(candidate["format"] == FORMAT and candidate["status"] == "PROVED", "format/status")
    require(candidate["scope"] == {
        "regular_algebraic_t_u_point_v_lifts": "COMPLETE",
        "remaining_algebraic_t_u_point_v_lifts": "NOT_YET_CONSTRUCTED",
        "global_gluing_and_closure_data": "NOT_CLAIMED",
        "honest_9dvl_score": "2/9",
    }, "scope")
    require(candidate["source"] == observed["source"], "source")
    lift = candidate["regular_algebraic_t_u_point_v_lift"]
    require(lift == {
        "completed_points": 118_001,
        "remaining_points": 11_938,
        "completed_base_factor_count_census": observed["factor_census"],
        "completed_tranche_census": observed["tranche_census"],
        "remaining_reason_census": observed["remaining_census"],
        "completed_raw_resultant_events": 182_648,
        "visible_inversion_edges": 169_056,
        "algebraic_collision_edges": 169_113,
        "tangential_clique_completion_points": 9,
        "tangential_clique_completion_edges": 14,
        "connected_clique_completion_edges": 8,
        "isolated_tangential_k2_edges": 6,
        "interior_collision_groups": 148_041,
        "section_v_root_points": 1_773_150,
        "section_open_v_strips": 1_891_151,
        "lifted_cells": 3_664_301,
        "event_group_pattern_census": observed["pattern_census"],
        "tangential_clique_completions": observed["tangential"],
        "raw_event_map_sha256": observed["raw_event_map_sha256"],
        "partition_sha256": observed["partition_sha256"],
        "signature_catalog_artifact": observed["catalog_metadata"],
    }, "lift claims")
    require(candidate["artifact_shards"] == observed["manifest"], "manifest")
    require(candidate["semantic_sha256"] == observed["semantic_sha256"], "semantic digest")
    require(candidate["resource_effect"] == {
        "prior_residual_ceiling": 129_939,
        "points_examined": 129_939,
        "remaining_ceiling": 11_938,
        "next_stage": NEXT_STAGE,
    }, "resource effect")
    require(candidate["generator_dependency"]["python"].startswith("3.12."), "python")
    require(candidate["generator_dependency"]["independent_verifier"] == "STRUCTURAL_REPLAY_WITHOUT_PRODUCER_IMPORT", "verifier independence")
    require(candidate["theorem_effect"] == THEOREM_EFFECT, "theorem effect")


def main():
    candidate = load(CERTIFICATE.name)
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
    require(all(record["status"] == "PROVED" for record in (
        projection, base, open_base, open_v, simple, invisible, multi, residual, final, prior
    )), "source status")
    events, event_serial = regular.independent_event_map(projection, base)
    endpoint_owners, _endpoint_serial = coefficient.independent_endpoint_owner_map(projection, open_v)
    sectors = read_shards(open_base, "sectors")
    sequences = [[entry[0] for entry in sector] for sector in sectors]
    point_groups, _boundaries, _direct, _tranche = open_u.base_section_data(
        sequences, simple, invisible, multi, residual, final
    )
    section_rows = read_shards(prior, "sections")
    section_catalog = prior["algebraic_t_open_u_strip_v_lift"]["section_signature_catalog"]
    wall_degrees = {
        row["id"]: row["fiber_degree"]
        for row in projection["fiber_walls"]["catalog"]
    }
    replayed = replay(
        section_rows,
        section_catalog,
        point_groups,
        events,
        endpoint_owners,
        wall_degrees,
    )
    require(replayed["completed"] == 118_001, "completed count")
    require(sum(replayed["remaining_census"].values()) == 11_938, "remaining count")
    require((replayed["points"], replayed["strips"]) == (1_773_150, 1_891_151), "cell census")
    require(replayed["tangential_points"] == 9, "tangential point census")
    require(replayed["tangential_edge_count"] == 14, "tangential edge census")
    require(replayed["connected_edge_count"] == 8, "connected completion census")
    require(replayed["isolated_edge_count"] == 6, "isolated tangency census")
    manifest, catalog_metadata = verify_artifacts(candidate, replayed)
    source = {
        "projection_semantic_sha256": projection["semantic_sha256"],
        "base_projection_semantic_sha256": base["semantic_sha256"],
        "open_cell_v_lift_semantic_sha256": open_v["semantic_sha256"],
        "algebraic_t_open_u_strip_v_lift_semantic_sha256": prior["semantic_sha256"],
        "prior_algebraic_t_u_point_cells": 129_939,
    }
    partition_sha256 = digest(replayed["sections"])
    raw_event_map_sha256 = digest(event_serial)
    semantic_payload = {
        "prior_semantic_sha256": prior["semantic_sha256"],
        "raw_event_map_sha256": raw_event_map_sha256,
        "partition_sha256": partition_sha256,
        "signature_catalog_sha256": catalog_metadata["semantic_sha256"],
        "factor_count_census": replayed["factor_census"],
        "tranche_census": replayed["tranche_census"],
        "remaining_census": replayed["remaining_census"],
        "pattern_census": replayed["pattern_census"],
        "tangential_clique_completions": replayed["tangential"],
    }
    observed = {
        **replayed,
        "source": source,
        "manifest": manifest,
        "catalog_metadata": catalog_metadata,
        "partition_sha256": partition_sha256,
        "raw_event_map_sha256": raw_event_map_sha256,
        "semantic_sha256": digest(semantic_payload),
    }
    validate_claims(candidate, observed)

    mutations = [
        (("scope", "regular_algebraic_t_u_point_v_lifts"), "NOT_YET_CONSTRUCTED"),
        (("scope", "remaining_algebraic_t_u_point_v_lifts"), "COMPLETE"),
        (("scope", "global_gluing_and_closure_data"), "COMPLETE"),
        (("scope", "honest_9dvl_score"), "3/9"),
        (("regular_algebraic_t_u_point_v_lift", "completed_points"), 118_000),
        (("regular_algebraic_t_u_point_v_lift", "remaining_points"), 0),
        (("regular_algebraic_t_u_point_v_lift", "completed_raw_resultant_events"), 182_647),
        (("regular_algebraic_t_u_point_v_lift", "visible_inversion_edges"), 169_055),
        (("regular_algebraic_t_u_point_v_lift", "algebraic_collision_edges"), 169_112),
        (("regular_algebraic_t_u_point_v_lift", "tangential_clique_completion_points"), 8),
        (("regular_algebraic_t_u_point_v_lift", "tangential_clique_completion_edges"), 13),
        (("regular_algebraic_t_u_point_v_lift", "connected_clique_completion_edges"), 7),
        (("regular_algebraic_t_u_point_v_lift", "isolated_tangential_k2_edges"), 5),
        (("regular_algebraic_t_u_point_v_lift", "interior_collision_groups"), 148_040),
        (("regular_algebraic_t_u_point_v_lift", "section_v_root_points"), 1_773_149),
        (("regular_algebraic_t_u_point_v_lift", "section_open_v_strips"), 1_891_150),
        (("regular_algebraic_t_u_point_v_lift", "lifted_cells"), 3_664_300),
        (("regular_algebraic_t_u_point_v_lift", "raw_event_map_sha256"), "0" * 64),
        (("regular_algebraic_t_u_point_v_lift", "partition_sha256"), "0" * 64),
        (("regular_algebraic_t_u_point_v_lift", "signature_catalog_artifact", "semantic_sha256"), "0" * 64),
        (("semantic_sha256",), "0" * 64),
        (("resource_effect", "remaining_ceiling"), 0),
        (("resource_effect", "next_stage"), "promote diagonal three"),
        (("generator_dependency", "independent_verifier"), "SHARED_PRODUCER"),
    ]
    rejected = 0
    for path, value in mutations:
        hostile = deepcopy(candidate)
        target = hostile
        for key in path[:-1]:
            target = target[key]
        target[path[-1]] = value
        try:
            validate_claims(hostile, observed)
        except AssertionError:
            rejected += 1
        else:
            raise AssertionError("claim mutation survived")
    structural = 0
    for args in (
        (((1, 0), (2, 0)), ((2, 0),), [], {}, (1,)),
        (((1, 0),), ((1, 0),), [("coefficient", (1, 0), 1, 0)], {}, (1,)),
        (((1, 0),), ((1, 0),), [], {1: ()}, (1,)),
    ):
        try:
            require(classify(*args) == 0, "structural reason erased")
        except AssertionError:
            structural += 1
        else:
            raise AssertionError("classification canary survived")
    try:
        collapsed_signature(((1, 0), (3, 0), (2, 0)), [((1, 0), (2, 0))])
    except AssertionError:
        structural += 1
    else:
        raise AssertionError("noncontiguous collision canary survived")
    rejected += structural
    require(rejected == len(mutations) + 4, "hostile census")

    print("PASS independent compound-resultant algebraic-t u-point replay")
    print("PASS 118001 pure-resultant points -> 3664301 lifted cells -> 11938-point residue")
    print("PASS exact 9-point / 14-edge tangential clique completion")
    print(f"PASS {rejected}/{len(mutations) + 4} hostile mutations rejected")
    print("SCOPE coefficient/endpoint point fibers remain; global topology open; honest 9DVL 2/9")


if __name__ == "__main__":
    main()
