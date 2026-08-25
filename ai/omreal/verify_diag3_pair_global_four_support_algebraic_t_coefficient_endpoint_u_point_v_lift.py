#!/usr/bin/env python3
"""Independent replay of the final algebraic-t u-point v-lift tranche."""

from __future__ import annotations

from collections import Counter, defaultdict
from copy import deepcopy
from fractions import Fraction
import gzip
from hashlib import sha256
import json
from math import lcm
from pathlib import Path
import sys


HERE = Path(__file__).resolve().parent
DATA = HERE / "data"
sys.path.insert(0, str(HERE))

import verify_diag3_pair_global_four_support_algebraic_t_regular_u_point_v_lift as prior  # noqa: E402
import verify_diag3_pair_global_four_support_coefficient_endpoint_u_section_v_lift as coefficient  # noqa: E402
import verify_diag3_pair_global_four_support_regular_u_section_v_lift as regular  # noqa: E402


PREFIX = (
    "DIAG3_PAIR_GLOBAL_FOUR_SUPPORT_"
    "ALGEBRAIC_T_COEFFICIENT_ENDPOINT_U_POINT_V_LIFT"
)
CERTIFICATE = DATA / f"{PREFIX}.json"
FORMAT = (
    "diag3-pair-global-row2599-four-support-"
    "algebraic-t-coefficient-endpoint-u-point-v-lift-v1"
)
SHARD_FORMAT = FORMAT + "-shard"
CATALOG_FORMAT = FORMAT + "-signature-catalog"
SHARD_COUNT = 32
SECTION_COUNT = 1_693
RESIDUAL_COUNT = 11_938
NEXT_STAGE = (
    "construct global gluing, labels, closure, and middle-rank replay "
    "over the complete local v-lift atlas"
)
THEOREM_EFFECT = (
    "Exact coefficient, endpoint, fiber-wide-zero, endpoint-tangency, "
    "and compound-resultant analysis lifts the final 11938 algebraic-t "
    "u-point fibers into 307146 cells. All 261571 algebraic-t base cells "
    "now have local v lifts, totaling 8390619 cells, while global "
    "gluing, labels, closure, middle-rank replay, and both diagonal-three "
    "invariant obligations remain open; honest 9DVL score remains 2/9."
)

REASON_NAMES = {
    2: "coefficient_only",
    4: "endpoint_equal_count",
    5: "endpoint_count_change",
    6: "coefficient_endpoint_equal_count",
    7: "coefficient_endpoint_count_change",
}
EXPECTED_ROLES = {
    27: {(13, 1, "unbounded_leading")},
    38: {(15, 1, "unbounded_leading")},
    35: {(0, 0, "endpoint_constant")},
    56: {(12, 1, "unbounded_leading")},
    72: {
        (14, 0, "endpoint_constant"),
        (17, 0, "fiber_wide_zero"),
        (21, 1, "unbounded_leading"),
    },
}


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
    encoded = (
        json.dumps(value, sort_keys=True, separators=(",", ":")) + "\n"
    ).encode("ascii")
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


def string_census(counter):
    return {
        ",".join(map(str, key if isinstance(key, tuple) else (key,))): value
        for key, value in sorted(counter.items())
    }


def specialize(terms, t_value, include_v):
    result = {}
    for term in terms:
        if include_v:
            u_power, t_power, v_power = term["exponent"]
        else:
            u_power, t_power = term["exponent"]
            v_power = 0
        result[(u_power, v_power)] = result.get(
            (u_power, v_power), Fraction()
        ) + Fraction(term["coefficient"]) * t_value**t_power
    return result


def coefficient_list(polynomial, v_power):
    degree = max(
        u_power
        for u_power, current_v_power in polynomial
        if current_v_power == v_power
    )
    return [
        polynomial.get((u_power, v_power), Fraction())
        for u_power in range(degree + 1)
    ]


def integer_scale(values):
    denominator = 1
    for value in values:
        denominator = lcm(denominator, value.denominator)
    return [int(value * denominator) for value in values]


def independent_tangency_proof(projection, base, roots):
    require(
        roots["root_isolation"]["sections"][550]
        == {
            "factor_id": 712,
            "factor_root_index": 0,
            "id": 550,
            "left": "1/4",
            "right": "1/4",
        },
        "special t section",
    )
    t_factors = {row["id"]: row for row in base["second_projection"]["catalog"]}
    require(
        t_factors[712]["coefficients_low_to_high"] == [-1, 4],
        "special t factor",
    )
    walls = {row["id"]: row for row in projection["fiber_walls"]["catalog"]}
    factors = {row["id"]: row for row in base["base_factorization"]["catalog"]}
    wall = specialize(walls[21]["polynomial"], Fraction(1, 4), True)
    factor = specialize(factors[86]["polynomial"], Fraction(1, 4), False)
    constant = coefficient_list(wall, 0)
    leading = coefficient_list(wall, 1)
    endpoint_value = [
        left + right for left, right in zip(constant, leading, strict=True)
    ]
    factor_value = coefficient_list(factor, 0)
    require(integer_scale(constant) == [-1, -6, -9], "special constant")
    require(integer_scale(leading) == [-3, 30, -27], "special leading")
    require(endpoint_value == [-value for value in factor_value], "endpoint identity")
    require(
        factor_value
        == [Fraction(1, 16), Fraction(-3, 8), Fraction(9, 16)],
        "exactly scaled square factor",
    )
    require(integer_scale(factor_value) == [1, -6, 9], "square factor")
    leading_at_root = sum(
        value * Fraction(1, 3) ** power
        for power, value in enumerate(leading)
    )
    require(leading_at_root == Fraction(1, 16), "positive special leading")
    return {
        "section_id": 550,
        "point_id": 30,
        "exact_t": "1/4",
        "exact_u": "1/3",
        "base_factor_id": 86,
        "fiber_wall_id": 21,
        "endpoint": 1,
        "wall_constant_at_t_scaled": integer_scale(constant),
        "wall_leading_at_t_scaled": integer_scale(leading),
        "endpoint_polynomial_at_t_scaled": integer_scale(endpoint_value),
        "base_factor_at_t_scaled": integer_scale(factor_value),
        "identity": "wall21(t=1/4,u,v=1)=-factor86(t=1/4,u)",
        "factorization": "factor86(t=1/4,u)=(1-3u)^2/16",
        "leading_at_t_u": "1/16",
        "root_location": "v>=1 on both adjacent u strips; v=1 only at u=1/3",
    }


def replay_coefficient_roles(
    owners,
    current,
    coefficient_factors,
    degrees,
    left_set,
    right_set,
):
    roles = []
    observed_by_factor = defaultdict(set)
    for factor_id, event in current:
        if event[0] != "coefficient":
            continue
        _kind, (wall, power), multiplicity, _projection_id = event
        require(multiplicity == 1, "coefficient multiplicity")
        degree = degrees[wall]
        token = (wall, 0)
        if degree == 0:
            require(
                power == 0 and token not in left_set | right_set,
                "fiber-wide coefficient role",
            )
            role = "fiber_wide_zero"
        elif power == 0:
            require(
                degree == 1 and token in left_set ^ right_set,
                "endpoint-constant coefficient role",
            )
            role = "endpoint_constant"
        else:
            require(
                power == degree == 1 and token not in left_set | right_set,
                "unbounded-leading coefficient role",
            )
            role = "unbounded_leading"
        require(
            not (
                set(owners)
                & set(coefficient_factors.get((wall, 1 - power), ()))
            ),
            "compound hidden zero wall",
        )
        row = (factor_id, wall, power, role)
        roles.append(row)
        observed_by_factor[factor_id].add((wall, power, role))
    for factor_id, observed in observed_by_factor.items():
        require(observed == EXPECTED_ROLES.get(factor_id), "coefficient pattern")
    return tuple(sorted(roles))


def replay_endpoint_attachments(
    section_id,
    point_id,
    owners,
    endpoint_owners,
    left_set,
    right_set,
):
    attachments = []
    fiber_wide = []
    seen_tokens = set()
    for factor_id in owners:
        for wall, boundary, multiplicity, degree in endpoint_owners.get(
            factor_id, ()
        ):
            require(multiplicity == 1, "endpoint multiplicity")
            token = (wall, 0)
            if degree == 0:
                require(token not in left_set | right_set, "degree-zero token")
                fiber_wide.append((factor_id, wall, boundary))
                continue
            require(degree == 1 and token not in seen_tokens, "endpoint owner")
            seen_tokens.add(token)
            if token in left_set ^ right_set:
                direction = "exit" if token in left_set else "entry"
            else:
                require(
                    (section_id, point_id, factor_id, wall, boundary)
                    == (550, 30, 86, 21, 1),
                    "unclassified endpoint tangency",
                )
                direction = "tangent_outside"
            attachments.append((factor_id, wall, boundary, direction))
    changed = {
        (wall, 0)
        for _factor, wall, _boundary, direction in attachments
        if direction != "tangent_outside"
    }
    require(left_set ^ right_set == changed, "endpoint token ownership")
    return tuple(sorted(attachments)), tuple(sorted(fiber_wide))


def completion_kind(edge, base_edges):
    first, second = edge
    adjacency = defaultdict(set)
    for left, right in base_edges:
        adjacency[left].add(right)
        adjacency[right].add(left)
    if first not in adjacency and second not in adjacency:
        return "isolated"
    todo = [first]
    seen = {first}
    while todo:
        current = todo.pop()
        for neighbor in adjacency[current]:
            if neighbor not in seen:
                seen.add(neighbor)
                todo.append(neighbor)
    require(second in seen, "cross-component completion")
    return "connected_clique_completion"


def replay(
    section_rows,
    prior_sections,
    source_catalog,
    events,
    endpoint_owners,
    coefficient_factors,
    degrees,
):
    catalog = []
    catalog_ids = {}
    sections = []
    reason_census = Counter()
    tranche_census = Counter()
    factor_count_census = Counter()
    role_census = Counter()
    attachment_census = Counter()
    fiber_wide_census = Counter()
    pattern_census = Counter()
    completion_rows = []
    completed = raw_count = inversion_count = persistent_count = 0
    completion_count = connected_count = isolated_k2 = isolated_k3_edges = 0
    edge_count = group_count = points = strips = tangencies = section_960 = 0

    for section_row, prior_section in zip(
        section_rows, prior_sections, strict=True
    ):
        section_id, tranche, _left_map, _right_map, strip_ids = section_row
        require(prior_section["section_id"] == section_id, "prior section order")
        completed_rows = []
        for point_id, raw_owners, reason_name in prior_section["remaining"]:
            owners = tuple(raw_owners)
            left = tuple(
                tuple(token)
                for group in source_catalog[strip_ids[point_id]]
                for token in group
            )
            right = tuple(
                tuple(token)
                for group in source_catalog[strip_ids[point_id + 1]]
                for token in group
            )
            current = [
                (factor_id, event)
                for factor_id in owners
                for event in events[factor_id]
            ]
            reason = prior.classify(
                left,
                right,
                [event for _factor, event in current],
                endpoint_owners,
                owners,
            )
            require(REASON_NAMES.get(reason) == reason_name, "residual reason")
            left_set, right_set = set(left), set(right)
            common = left_set & right_set
            roles = replay_coefficient_roles(
                owners,
                current,
                coefficient_factors,
                degrees,
                left_set,
                right_set,
            )
            attachments, fiber_wide = replay_endpoint_attachments(
                section_id,
                point_id,
                owners,
                endpoint_owners,
                left_set,
                right_set,
            )
            tangencies += sum(
                direction == "tangent_outside"
                for _factor, _wall, _boundary, direction in attachments
            )

            inversions = set(regular.inversions(left, right))
            base_edges = set(inversions)
            permitted = Counter(
                tuple(sorted(event[1]))
                for _factor, event in current
                if event[0] == "resultant"
            )
            persistent = []
            if section_id == 960:
                base_edges.add(((1, 0), (6, 0)))
                permitted[(1, 6)] += 1
                persistent.append(((1, 0), (6, 0)))
                section_960 += 1
            seen = Counter(
                tuple(sorted((first[0], second[0])))
                for first, second in base_edges
            )
            regular.verify_inversion_owners(seen, permitted)
            common_walls = {token[0] for token in common}
            unused = tuple(
                sorted(
                    (pair, multiplicity)
                    for pair, multiplicity in (permitted - seen).items()
                    if multiplicity and set(pair) <= common_walls
                )
            )
            completions = []
            kinds = []
            for pair, multiplicity in unused:
                require(multiplicity == 1, "completion multiplicity")
                require(min(degrees[pair[0]], degrees[pair[1]]) == 1, "linear witness")
                first = [token for token in common if token[0] == pair[0]]
                second = [token for token in common if token[0] == pair[1]]
                require(len(first) == len(second) == 1, "completion occurrence")
                edge = tuple(sorted((first[0], second[0])))
                completions.append(edge)
                kinds.append(completion_kind(edge, base_edges))
            isolated_edges = {
                edge
                for edge, kind in zip(completions, kinds, strict=True)
                if kind == "isolated"
            }
            isolated_components = regular.collision_components(isolated_edges)
            require(
                all(len(component) in {2, 3} for component in isolated_components),
                "isolated component size",
            )
            edges = base_edges | set(completions)
            components = regular.collision_components(edges)
            left_common = tuple(token for token in left if token in common)
            right_common = tuple(token for token in right if token in common)
            signature = prior.collapsed_signature(left_common, components)
            require(
                signature
                == prior.collapsed_signature(right_common, components),
                "collapsed signature agreement",
            )
            identifier = catalog_ids.get(signature)
            if identifier is None:
                identifier = len(catalog)
                catalog_ids[signature] = identifier
                catalog.append(
                    [[list(token) for token in component] for component in signature]
                )
            point_count = len(signature)
            strip_count = point_count + 1
            completed_rows.append(
                [
                    point_id,
                    list(owners),
                    reason_name,
                    identifier,
                    [list(row) for row in roles],
                    [list(row) for row in attachments],
                    [list(row) for row in fiber_wide],
                    len(current),
                    len(inversions),
                    len(persistent),
                    len(completions),
                    [len(component) for component in isolated_components],
                    len(components),
                    point_count,
                    strip_count,
                ]
            )
            completed += 1
            raw_count += sum(event[0] == "resultant" for _factor, event in current)
            inversion_count += len(inversions)
            persistent_count += len(persistent)
            completion_count += len(completions)
            connected_count += kinds.count("connected_clique_completion")
            isolated_k2 += sum(
                len(component) == 2 for component in isolated_components
            )
            isolated_k3_edges += sum(
                3 if len(component) == 3 else 0
                for component in isolated_components
            )
            edge_count += len(edges)
            group_count += len(components)
            points += point_count
            strips += strip_count
            reason_census[reason_name] += 1
            tranche_census[tranche] += 1
            factor_count_census[len(owners)] += 1
            for row in roles:
                role_census[row] += 1
            for row in attachments:
                attachment_census[row] += 1
            for row in fiber_wide:
                fiber_wide_census[row] += 1
            pattern_census[
                (
                    reason_name,
                    len(owners),
                    len(left),
                    len(right),
                    len(current),
                    len(inversions),
                    len(persistent),
                    len(completions),
                    tuple(sorted(len(component) for component in components)),
                    point_count,
                    strip_count,
                )
            ] += 1
            if completions:
                completion_rows.append(
                    [
                        section_id,
                        point_id,
                        list(owners),
                        [
                            [list(first), list(second)]
                            for first, second in completions
                        ],
                        kinds,
                        [
                            [list(token) for token in component]
                            for component in isolated_components
                        ],
                    ]
                )
        sections.append(
            {"section_id": section_id, "completed": completed_rows, "remaining": []}
        )
    return {
        "sections": sections,
        "catalog": catalog,
        "reason_census": dict(sorted(reason_census.items())),
        "tranche_census": dict(sorted(tranche_census.items())),
        "factor_count_census": {
            str(key): value for key, value in sorted(factor_count_census.items())
        },
        "role_census": string_census(role_census),
        "attachment_census": string_census(attachment_census),
        "fiber_wide_census": string_census(fiber_wide_census),
        "pattern_census": string_census(pattern_census),
        "completion_rows": completion_rows,
        "completed": completed,
        "raw_count": raw_count,
        "inversion_count": inversion_count,
        "persistent_count": persistent_count,
        "completion_count": completion_count,
        "connected_count": connected_count,
        "isolated_k2": isolated_k2,
        "isolated_k3_edges": isolated_k3_edges,
        "edge_count": edge_count,
        "group_count": group_count,
        "points": points,
        "strips": strips,
        "tangencies": tangencies,
        "section_960": section_960,
    }


def verify_artifacts(candidate, replayed):
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
            "sections": replayed["sections"][start:end],
        }
        raw = canonical_gzip_json(shard)
        name = f"{PREFIX}_SHARD_{index:02d}_OF_{SHARD_COUNT}.json.gz"
        require((DATA / name).read_bytes() == raw, "checkpoint shard bytes")
        metadata.append(
            {
                "index": index,
                "path": name,
                "section_start": start,
                "section_end": end,
                "bytes": len(raw),
                "sha256": sha256(raw).hexdigest(),
            }
        )
    manifest = {
        "format": SHARD_FORMAT,
        "shard_count": SHARD_COUNT,
        "shards": metadata,
    }
    require(candidate["artifact_shards"] == manifest, "shard manifest")
    payload = {"format": CATALOG_FORMAT, "signature_catalog": replayed["catalog"]}
    raw = canonical_gzip_json(payload)
    name = f"{PREFIX}_SIGNATURE_CATALOG.json.gz"
    require((DATA / name).read_bytes() == raw, "catalog bytes")
    catalog = {
        "format": CATALOG_FORMAT,
        "path": name,
        "entries": len(replayed["catalog"]),
        "bytes": len(raw),
        "sha256": sha256(raw).hexdigest(),
        "semantic_sha256": digest(replayed["catalog"]),
    }
    return manifest, catalog


def validate_claims(candidate, observed):
    require(
        candidate["format"] == FORMAT and candidate["status"] == "PROVED",
        "format/status",
    )
    require(
        candidate["scope"]
        == {
            "all_algebraic_t_u_point_v_lifts": "COMPLETE",
            "all_algebraic_t_v_lifts": "COMPLETE",
            "global_gluing_and_closure_data": "NOT_CLAIMED",
            "honest_9dvl_score": "2/9",
        },
        "scope",
    )
    require(candidate["source"] == observed["source"], "source")
    lift = candidate["coefficient_endpoint_algebraic_t_u_point_v_lift"]
    expected_lift = {
            "completed_points": 11_938,
            "remaining_algebraic_t_u_points": 0,
            "completed_reason_census": observed["reason_census"],
            "completed_tranche_census": observed["tranche_census"],
            "completed_base_factor_count_census": observed["factor_count_census"],
            "coefficient_role_census": observed["role_census"],
            "endpoint_attachment_census": observed["attachment_census"],
            "fiber_wide_zero_endpoint_census": observed["fiber_wide_census"],
            "event_group_pattern_census": observed["pattern_census"],
            "completed_raw_resultant_events": 44_506,
            "visible_inversion_edges": 36_053,
            "persistent_section_960_edges": 4,
            "tangential_clique_completion_edges": 10,
            "connected_clique_completion_edges": 6,
            "isolated_tangential_k2_edges": 1,
            "isolated_tangential_k3_edges": 3,
            "algebraic_collision_edges": 36_067,
            "interior_collision_groups": 29_203,
            "section_v_root_points": 147_604,
            "section_open_v_strips": 159_542,
            "lifted_cells": 307_146,
            "special_endpoint_tangencies": 1,
            "endpoint_tangency_proof": observed["tangency_proof"],
            "tangential_clique_completions": observed["completion_rows"],
            "raw_event_map_sha256": observed["raw_event_map_sha256"],
            "endpoint_owner_map_sha256": observed["endpoint_owner_map_sha256"],
            "coefficient_factor_map_sha256": observed[
                "coefficient_factor_map_sha256"
            ],
            "partition_sha256": observed["partition_sha256"],
            "signature_catalog_artifact": observed["catalog_metadata"],
        }
    if lift != expected_lift:
        different = {
            key: (lift.get(key), expected_lift.get(key))
            for key in set(lift) | set(expected_lift)
            if lift.get(key) != expected_lift.get(key)
        }
        raise AssertionError(f"lift claims: {different}")
    require(
        candidate["cumulative_algebraic_t_v_lift"]
        == {
            "base_cells": 261_571,
            "open_u_strip_base_cells": 131_632,
            "algebraic_u_point_base_cells": 129_939,
            "regular_point_v_lift_cells": 3_664_301,
            "coefficient_endpoint_point_v_lift_cells": 307_146,
            "open_u_strip_v_lift_cells": 4_419_172,
            "lifted_cells": 8_390_619,
        },
        "cumulative lift",
    )
    require(candidate["artifact_shards"] == observed["manifest"], "manifest")
    require(candidate["semantic_sha256"] == observed["semantic_sha256"], "semantic")
    require(
        candidate["resource_effect"]
        == {
            "prior_residual_ceiling": RESIDUAL_COUNT,
            "points_examined": RESIDUAL_COUNT,
            "remaining_ceiling": 0,
            "next_stage": NEXT_STAGE,
        },
        "resource effect",
    )
    require(candidate["generator_dependency"]["python"].startswith("3.12."), "python")
    require(
        candidate["generator_dependency"]["independent_verifier"]
        == "STRUCTURAL_REPLAY_WITHOUT_PRODUCER_IMPORT",
        "independence",
    )
    require(candidate["theorem_effect"] == THEOREM_EFFECT, "theorem effect")


def main():
    candidate = load(CERTIFICATE.name)
    projection = load("DIAG3_PAIR_GLOBAL_FOUR_SUPPORT_PROJECTION.json")
    base = load("DIAG3_PAIR_GLOBAL_FOUR_SUPPORT_BASE_PROJECTION.json.gz")
    roots = load("DIAG3_PAIR_GLOBAL_FOUR_SUPPORT_ROOT_ISOLATION.json.gz")
    open_v = load("DIAG3_PAIR_GLOBAL_FOUR_SUPPORT_OPEN_CELL_V_LIFT.json")
    open_u = load(
        "DIAG3_PAIR_GLOBAL_FOUR_SUPPORT_ALGEBRAIC_T_OPEN_U_STRIP_V_LIFT.json"
    )
    prior_record = load(
        "DIAG3_PAIR_GLOBAL_FOUR_SUPPORT_ALGEBRAIC_T_REGULAR_U_POINT_V_LIFT.json"
    )
    require(
        all(
            record["status"] == "PROVED"
            for record in (projection, base, roots, open_v, open_u, prior_record)
        ),
        "source status",
    )
    events, event_serial = regular.independent_event_map(projection, base)
    endpoint_owners, endpoint_serial = coefficient.independent_endpoint_owner_map(
        projection, open_v
    )
    coefficient_factors = coefficient.independent_coefficient_factor_map(events)
    coefficient_serial = [
        [list(owner), list(factors)]
        for owner, factors in sorted(coefficient_factors.items())
    ]
    degrees = {
        row["id"]: row["fiber_degree"]
        for row in projection["fiber_walls"]["catalog"]
    }
    tangency_proof = independent_tangency_proof(projection, base, roots)
    section_rows = read_shards(open_u, "sections")
    prior_sections = read_shards(prior_record, "sections")
    source_catalog = open_u[
        "algebraic_t_open_u_strip_v_lift"
    ]["section_signature_catalog"]
    replayed = replay(
        section_rows,
        prior_sections,
        source_catalog,
        events,
        endpoint_owners,
        coefficient_factors,
        degrees,
    )
    require(replayed["completed"] == RESIDUAL_COUNT, "completed count")
    require((replayed["points"], replayed["strips"]) == (147_604, 159_542), "cells")
    require(
        (
            replayed["completion_count"],
            replayed["connected_count"],
            replayed["isolated_k2"],
            replayed["isolated_k3_edges"],
        )
        == (10, 6, 1, 3),
        "completion census",
    )
    require(
        (replayed["tangencies"], replayed["section_960"]) == (1, 4),
        "special census",
    )
    manifest, catalog_metadata = verify_artifacts(candidate, replayed)
    source = {
        "projection_semantic_sha256": projection["semantic_sha256"],
        "base_projection_semantic_sha256": base["semantic_sha256"],
        "root_isolation_semantic_sha256": roots["semantic_sha256"],
        "open_cell_v_lift_semantic_sha256": open_v["semantic_sha256"],
        "algebraic_t_open_u_strip_v_lift_semantic_sha256": open_u[
            "semantic_sha256"
        ],
        "regular_algebraic_t_u_point_v_lift_semantic_sha256": prior_record[
            "semantic_sha256"
        ],
        "prior_residual_points": RESIDUAL_COUNT,
    }
    raw_event_map_sha256 = digest(event_serial)
    endpoint_owner_map_sha256 = digest(endpoint_serial)
    coefficient_factor_map_sha256 = digest(coefficient_serial)
    partition_sha256 = digest(replayed["sections"])
    semantic_payload = {
        "prior_semantic_sha256": prior_record["semantic_sha256"],
        "raw_event_map_sha256": raw_event_map_sha256,
        "endpoint_owner_map_sha256": endpoint_owner_map_sha256,
        "coefficient_factor_map_sha256": coefficient_factor_map_sha256,
        "partition_sha256": partition_sha256,
        "signature_catalog_sha256": catalog_metadata["semantic_sha256"],
        "reason_census": replayed["reason_census"],
        "coefficient_role_census": replayed["role_census"],
        "endpoint_attachment_census": replayed["attachment_census"],
        "tangential_completion_rows": replayed["completion_rows"],
        "endpoint_tangency_proof": tangency_proof,
    }
    observed = {
        **replayed,
        "source": source,
        "manifest": manifest,
        "catalog_metadata": catalog_metadata,
        "tangency_proof": tangency_proof,
        "raw_event_map_sha256": raw_event_map_sha256,
        "endpoint_owner_map_sha256": endpoint_owner_map_sha256,
        "coefficient_factor_map_sha256": coefficient_factor_map_sha256,
        "partition_sha256": partition_sha256,
        "semantic_sha256": digest(semantic_payload),
    }
    validate_claims(candidate, observed)

    mutations = [
        (("scope", "all_algebraic_t_u_point_v_lifts"), "NOT_YET_CONSTRUCTED"),
        (("scope", "all_algebraic_t_v_lifts"), "NOT_YET_CONSTRUCTED"),
        (("scope", "global_gluing_and_closure_data"), "COMPLETE"),
        (("scope", "honest_9dvl_score"), "3/9"),
        (("coefficient_endpoint_algebraic_t_u_point_v_lift", "completed_points"), 11_937),
        (("coefficient_endpoint_algebraic_t_u_point_v_lift", "remaining_algebraic_t_u_points"), 1),
        (("coefficient_endpoint_algebraic_t_u_point_v_lift", "completed_raw_resultant_events"), 44_505),
        (("coefficient_endpoint_algebraic_t_u_point_v_lift", "visible_inversion_edges"), 36_052),
        (("coefficient_endpoint_algebraic_t_u_point_v_lift", "persistent_section_960_edges"), 3),
        (("coefficient_endpoint_algebraic_t_u_point_v_lift", "tangential_clique_completion_edges"), 9),
        (("coefficient_endpoint_algebraic_t_u_point_v_lift", "connected_clique_completion_edges"), 5),
        (("coefficient_endpoint_algebraic_t_u_point_v_lift", "isolated_tangential_k2_edges"), 0),
        (("coefficient_endpoint_algebraic_t_u_point_v_lift", "isolated_tangential_k3_edges"), 2),
        (("coefficient_endpoint_algebraic_t_u_point_v_lift", "algebraic_collision_edges"), 36_066),
        (("coefficient_endpoint_algebraic_t_u_point_v_lift", "interior_collision_groups"), 29_202),
        (("coefficient_endpoint_algebraic_t_u_point_v_lift", "section_v_root_points"), 147_603),
        (("coefficient_endpoint_algebraic_t_u_point_v_lift", "section_open_v_strips"), 159_541),
        (("coefficient_endpoint_algebraic_t_u_point_v_lift", "lifted_cells"), 307_145),
        (("coefficient_endpoint_algebraic_t_u_point_v_lift", "special_endpoint_tangencies"), 0),
        (("coefficient_endpoint_algebraic_t_u_point_v_lift", "endpoint_tangency_proof", "identity"), "unproved"),
        (("coefficient_endpoint_algebraic_t_u_point_v_lift", "raw_event_map_sha256"), "0" * 64),
        (("coefficient_endpoint_algebraic_t_u_point_v_lift", "endpoint_owner_map_sha256"), "0" * 64),
        (("coefficient_endpoint_algebraic_t_u_point_v_lift", "coefficient_factor_map_sha256"), "0" * 64),
        (("coefficient_endpoint_algebraic_t_u_point_v_lift", "partition_sha256"), "0" * 64),
        (("coefficient_endpoint_algebraic_t_u_point_v_lift", "signature_catalog_artifact", "semantic_sha256"), "0" * 64),
        (("cumulative_algebraic_t_v_lift", "lifted_cells"), 8_390_618),
        (("semantic_sha256",), "0" * 64),
        (("resource_effect", "remaining_ceiling"), 1),
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
    for action in (
        lambda: prior.collapsed_signature(
            ((1, 0), (3, 0), (2, 0)), [{(1, 0), (2, 0)}]
        ),
        lambda: completion_kind(
            ((1, 0), (4, 0)), {((1, 0), (2, 0)), ((3, 0), (4, 0))}
        ),
    ):
        try:
            action()
        except AssertionError:
            structural += 1
        else:
            raise AssertionError("structural canary survived")
    rejected += structural
    require(rejected == len(mutations) + 2, "hostile census")

    print("PASS independent coefficient/endpoint algebraic-t u-point replay")
    print("PASS 11938 residual points -> 307146 lifted cells -> zero local-v residue")
    print("PASS exact endpoint tangency and 6 connected + K2 + K3 completions")
    print(f"PASS {rejected}/{len(mutations) + 2} hostile mutations rejected")
    print("SCOPE all local algebraic-t v lifts complete; global topology open; honest 9DVL 2/9")


if __name__ == "__main__":
    main()
