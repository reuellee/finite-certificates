#!/usr/bin/env python3
"""Build the final coefficient/endpoint algebraic-t u-point v-lift tranche."""

from __future__ import annotations

from collections import Counter, defaultdict
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

import build_diag3_pair_global_four_support_algebraic_t_regular_u_point_v_lift as prior  # noqa: E402
import build_diag3_pair_global_four_support_coefficient_only_u_section_v_lift as coefficient  # noqa: E402
import build_diag3_pair_global_four_support_endpoint_u_section_v_lift as endpoint  # noqa: E402
import build_diag3_pair_global_four_support_regular_u_section_v_lift as regular  # noqa: E402
import diag3_pair_global_four_support_projection_core as projection_core  # noqa: E402


PREFIX = (
    "DIAG3_PAIR_GLOBAL_FOUR_SUPPORT_"
    "ALGEBRAIC_T_COEFFICIENT_ENDPOINT_U_POINT_V_LIFT"
)
OUTPUT = DATA / f"{PREFIX}.json"
FORMAT = (
    "diag3-pair-global-row2599-four-support-"
    "algebraic-t-coefficient-endpoint-u-point-v-lift-v1"
)
SHARD_FORMAT = FORMAT + "-shard"
CATALOG_FORMAT = FORMAT + "-signature-catalog"
SHARD_COUNT = 32
SECTION_COUNT = 1_693
RESIDUAL_COUNT = 11_938

REASON_NAMES = {
    2: "coefficient_only",
    4: "endpoint_equal_count",
    5: "endpoint_count_change",
    6: "coefficient_endpoint_equal_count",
    7: "coefficient_endpoint_count_change",
}

EXPECTED_COEFFICIENT_ROLES = {
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
    for metadata in record["artifact_shards"]["shards"]:
        shard = json.loads(gzip.decompress((DATA / metadata["path"]).read_bytes()))
        rows.extend(shard[field])
    return rows


def string_census(counter):
    return {
        ",".join(map(str, key if isinstance(key, tuple) else (key,))): value
        for key, value in sorted(counter.items())
    }


def polynomial_specialization(terms, t_value, include_v):
    result = {}
    for term in terms:
        exponent = term["exponent"]
        if include_v:
            u_power, t_power, v_power = exponent
        else:
            u_power, t_power = exponent
            v_power = 0
        key = (u_power, v_power)
        result[key] = result.get(key, Fraction()) + (
            Fraction(term["coefficient"]) * t_value**t_power
        )
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


def endpoint_tangency_proof(projection, base, roots):
    section = roots["root_isolation"]["sections"][550]
    if section != {
        "factor_id": 712,
        "factor_root_index": 0,
        "id": 550,
        "left": "1/4",
        "right": "1/4",
    }:
        raise AssertionError("endpoint-tangency t section changed")
    t_factors = {row["id"]: row for row in base["second_projection"]["catalog"]}
    if t_factors[712]["coefficients_low_to_high"] != [-1, 4]:
        raise AssertionError("endpoint-tangency t factor changed")
    walls = {row["id"]: row for row in projection["fiber_walls"]["catalog"]}
    base_factors = {row["id"]: row for row in base["base_factorization"]["catalog"]}
    wall = polynomial_specialization(
        walls[21]["polynomial"], Fraction(1, 4), include_v=True
    )
    factor = polynomial_specialization(
        base_factors[86]["polynomial"], Fraction(1, 4), include_v=False
    )
    constant = coefficient_list(wall, 0)
    leading = coefficient_list(wall, 1)
    endpoint_value = [
        left + right for left, right in zip(constant, leading, strict=True)
    ]
    factor_value = coefficient_list(factor, 0)
    if integer_scale(constant) != [-1, -6, -9]:
        raise AssertionError("special wall constant specialization changed")
    if integer_scale(leading) != [-3, 30, -27]:
        raise AssertionError("special wall leading specialization changed")
    if endpoint_value != [-value for value in factor_value]:
        raise AssertionError("special endpoint does not equal minus base factor 86")
    if factor_value != [
        Fraction(1, 16),
        Fraction(-3, 8),
        Fraction(9, 16),
    ]:
        raise AssertionError("special base factor has the wrong exact scale")
    if integer_scale(factor_value) != [1, -6, 9]:
        raise AssertionError("special base factor is not (1-3u)^2")
    leading_at_root = sum(
        value * Fraction(1, 3) ** power
        for power, value in enumerate(leading)
    )
    if leading_at_root != Fraction(1, 16):
        raise AssertionError("special wall leading coefficient is not positive")
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


def coefficient_roles(
    owners,
    current_events,
    coefficient_factors,
    wall_degrees,
    left_set,
    right_set,
):
    roles = []
    by_factor = defaultdict(set)
    for factor_id, event in current_events:
        if event[0] != "coefficient":
            continue
        _kind, (wall_id, power), multiplicity, _projection_id = event
        if multiplicity != 1:
            raise AssertionError("non-simple coefficient event")
        degree = wall_degrees[wall_id]
        token = (wall_id, 0)
        if degree == 0:
            if power != 0 or token in left_set or token in right_set:
                raise AssertionError("bad fiber-wide-zero coefficient event")
            role = "fiber_wide_zero"
        elif power == 0:
            if degree != 1 or token not in left_set ^ right_set:
                raise AssertionError("constant drop is not an endpoint crossing")
            role = "endpoint_constant"
        elif power == degree == 1:
            if token in left_set or token in right_set:
                raise AssertionError("leading-drop root remains bounded")
            role = "unbounded_leading"
        else:
            raise AssertionError("unsupported coefficient event")
        opposite = tuple(
            sorted(
                set(owners)
                & set(coefficient_factors.get((wall_id, 1 - power), ()))
            )
        )
        if opposite:
            raise AssertionError("compound coefficient event makes a hidden zero wall")
        roles.append((factor_id, wall_id, power, role))
        by_factor[factor_id].add((wall_id, power, role))
    for factor_id, observed in by_factor.items():
        if observed != EXPECTED_COEFFICIENT_ROLES.get(factor_id):
            raise AssertionError("coefficient-role pattern changed")
    return tuple(sorted(roles))


def endpoint_attachments(
    section_id,
    point_id,
    owners,
    endpoint_owners,
    left_set,
    right_set,
):
    rows = [
        (factor_id, *row)
        for factor_id in owners
        for row in endpoint_owners.get(factor_id, ())
    ]
    attachments = []
    fiber_wide = []
    endpoint_tokens = set()
    for factor_id, wall_id, boundary, multiplicity, degree in rows:
        if multiplicity != 1:
            raise AssertionError("non-simple endpoint event")
        token = (wall_id, 0)
        if degree == 0:
            if token in left_set or token in right_set:
                raise AssertionError("degree-zero wall emitted a bounded token")
            fiber_wide.append((factor_id, wall_id, boundary))
            continue
        if degree != 1:
            raise AssertionError("unsupported endpoint wall degree")
        if token in endpoint_tokens:
            raise AssertionError("duplicate endpoint token owner")
        endpoint_tokens.add(token)
        if token in left_set ^ right_set:
            direction = "exit" if token in left_set else "entry"
            attachments.append((factor_id, wall_id, boundary, direction))
        elif (
            section_id,
            point_id,
            factor_id,
            wall_id,
            boundary,
        ) == (550, 30, 86, 21, 1):
            attachments.append(
                (factor_id, wall_id, boundary, "tangent_outside")
            )
        else:
            raise AssertionError("endpoint event did not own a token change")
    changed_tokens = {
        (wall_id, 0)
        for _factor_id, wall_id, _boundary, direction in attachments
        if direction != "tangent_outside"
    }
    if left_set ^ right_set != changed_tokens:
        raise AssertionError("endpoint attachments do not own the token difference")
    return tuple(sorted(attachments)), tuple(sorted(fiber_wide))


def component_kind(edge, base_edges):
    first, second = edge
    neighbors = defaultdict(set)
    for left, right in base_edges:
        neighbors[left].add(right)
        neighbors[right].add(left)
    if first not in neighbors and second not in neighbors:
        return "isolated"
    frontier = [first]
    seen = {first}
    while frontier:
        current = frontier.pop()
        for neighbor in neighbors[current]:
            if neighbor not in seen:
                seen.add(neighbor)
                frontier.append(neighbor)
    if second not in seen:
        raise AssertionError("completion edge joins distinct visible components")
    return "connected_clique_completion"


def analyze(
    section_rows,
    prior_sections,
    section_catalog,
    events,
    endpoint_owners,
    coefficient_factors,
    wall_degrees,
):
    signature_catalog = []
    signature_ids = {}
    section_records = []
    reason_census = Counter()
    tranche_census = Counter()
    factor_count_census = Counter()
    coefficient_role_census = Counter()
    endpoint_attachment_census = Counter()
    fiber_wide_census = Counter()
    pattern_census = Counter()
    completion_rows = []
    completed = raw_resultants = visible_edges = persistent_edges = 0
    completion_edges = connected_completion_edges = 0
    isolated_k2_edges = isolated_k3_edges = collision_edges = collision_groups = 0
    points = strips = special_tangencies = section_960_points = 0

    for section_row, prior_section in zip(
        section_rows, prior_sections, strict=True
    ):
        section_id, tranche, _left_map, _right_map, strip_ids = section_row
        if prior_section["section_id"] != section_id:
            raise AssertionError("prior section order changed")
        completed_rows = []
        for point_id, raw_owners, reason_name in prior_section["remaining"]:
            owners = tuple(raw_owners)
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
            current_events = [
                (factor_id, event)
                for factor_id in owners
                for event in events[factor_id]
            ]
            reason = prior.classify(
                left,
                right,
                [event for _factor_id, event in current_events],
                endpoint_owners,
                owners,
            )
            if REASON_NAMES.get(reason) != reason_name:
                raise AssertionError("prior residual reason changed")
            left_set = set(left)
            right_set = set(right)
            common = left_set & right_set
            roles = coefficient_roles(
                owners,
                current_events,
                coefficient_factors,
                wall_degrees,
                left_set,
                right_set,
            )
            attachments, fiber_wide = endpoint_attachments(
                section_id,
                point_id,
                owners,
                endpoint_owners,
                left_set,
                right_set,
            )
            special_tangencies += sum(
                direction == "tangent_outside"
                for _factor, _wall, _endpoint, direction in attachments
            )

            inversions = set(regular.inversion_edges(left, right))
            base_edges = set(inversions)
            permitted = Counter(
                tuple(sorted(event[1]))
                for _factor_id, event in current_events
                if event[0] == "resultant"
            )
            persistent = []
            if section_id == 960:
                edge = ((1, 0), (6, 0))
                base_edges.add(edge)
                permitted[(1, 6)] += 1
                persistent.append(edge)
                section_960_points += 1
            seen = Counter(
                tuple(sorted((first[0], second[0])))
                for first, second in base_edges
            )
            if seen - permitted:
                raise AssertionError("visible collision lacks a raw resultant")
            common_walls = {token[0] for token in common}
            unused = tuple(
                sorted(
                    (pair, multiplicity)
                    for pair, multiplicity in (permitted - seen).items()
                    if multiplicity and set(pair) <= common_walls
                )
            )
            current_completions = []
            completion_kinds = []
            for pair, multiplicity in unused:
                if multiplicity != 1:
                    raise AssertionError("non-simple tangential completion")
                if min(wall_degrees[pair[0]], wall_degrees[pair[1]]) != 1:
                    raise AssertionError("tangential completion lacks a linear wall")
                first = [token for token in common if token[0] == pair[0]]
                second = [token for token in common if token[0] == pair[1]]
                if len(first) != 1 or len(second) != 1:
                    raise AssertionError("ambiguous tangential root occurrence")
                edge = tuple(sorted((first[0], second[0])))
                current_completions.append(edge)
                completion_kinds.append(component_kind(edge, base_edges))
            isolated = [
                edge
                for edge, kind in zip(
                    current_completions, completion_kinds, strict=True
                )
                if kind == "isolated"
            ]
            isolated_components = regular.clique_components(set(isolated))
            if any(len(component) not in {2, 3} for component in isolated_components):
                raise AssertionError("unsupported isolated tangential component")
            current_edges = base_edges | set(current_completions)
            components = regular.clique_components(current_edges)
            left_common = tuple(token for token in left if token in common)
            right_common = tuple(token for token in right if token in common)
            signature = prior.collapse_signature(left_common, components)
            if signature != prior.collapse_signature(right_common, components):
                raise AssertionError("collapsed point signatures disagree")
            identifier = signature_ids.get(signature)
            if identifier is None:
                identifier = len(signature_catalog)
                signature_ids[signature] = identifier
                signature_catalog.append(
                    [
                        [list(token) for token in component]
                        for component in signature
                    ]
                )
            point_count = len(signature)
            strip_count = point_count + 1
            completed_rows.append(
                [
                    point_id,
                    list(owners),
                    reason_name,
                    identifier,
                    [
                        [factor, wall, power, role]
                        for factor, wall, power, role in roles
                    ],
                    [
                        [factor, wall, boundary, direction]
                        for factor, wall, boundary, direction in attachments
                    ],
                    [list(row) for row in fiber_wide],
                    len(current_events),
                    len(inversions),
                    len(persistent),
                    len(current_completions),
                    [len(component) for component in isolated_components],
                    len(components),
                    point_count,
                    strip_count,
                ]
            )
            completed += 1
            raw_resultants += sum(
                event[0] == "resultant"
                for _factor_id, event in current_events
            )
            visible_edges += len(inversions)
            persistent_edges += len(persistent)
            completion_edges += len(current_completions)
            connected_completion_edges += completion_kinds.count(
                "connected_clique_completion"
            )
            isolated_k2_edges += sum(
                len(component) == 2 for component in isolated_components
            )
            isolated_k3_edges += sum(
                3 if len(component) == 3 else 0
                for component in isolated_components
            )
            collision_edges += len(current_edges)
            collision_groups += len(components)
            points += point_count
            strips += strip_count
            reason_census[reason_name] += 1
            tranche_census[tranche] += 1
            factor_count_census[len(owners)] += 1
            for role in roles:
                coefficient_role_census[role] += 1
            for attachment in attachments:
                endpoint_attachment_census[attachment] += 1
            for row in fiber_wide:
                fiber_wide_census[row] += 1
            pattern_census[
                (
                    reason_name,
                    len(owners),
                    len(left),
                    len(right),
                    len(current_events),
                    len(inversions),
                    len(persistent),
                    len(current_completions),
                    tuple(sorted(len(component) for component in components)),
                    point_count,
                    strip_count,
                )
            ] += 1
            if current_completions:
                completion_rows.append(
                    [
                        section_id,
                        point_id,
                        list(owners),
                        [
                            [list(first), list(second)]
                            for first, second in current_completions
                        ],
                        completion_kinds,
                        [list(component) for component in isolated_components],
                    ]
                )
        section_records.append(
            {"section_id": section_id, "completed": completed_rows, "remaining": []}
        )

    expected_reasons = {
        "coefficient_endpoint_count_change": 2_888,
        "coefficient_endpoint_equal_count": 1_692,
        "coefficient_only": 3_380,
        "endpoint_count_change": 3_976,
        "endpoint_equal_count": 2,
    }
    if completed != RESIDUAL_COUNT or dict(sorted(reason_census.items())) != expected_reasons:
        raise AssertionError("coefficient/endpoint residual partition changed")
    if (points, strips, points + strips) != (147_604, 159_542, 307_146):
        raise AssertionError("coefficient/endpoint point-cell census changed")
    if (
        completion_edges,
        connected_completion_edges,
        isolated_k2_edges,
        isolated_k3_edges,
    ) != (10, 6, 1, 3):
        raise AssertionError("residual tangential-completion census changed")
    if special_tangencies != 1 or section_960_points != 4:
        raise AssertionError("special endpoint/persistent collision census changed")
    return {
        "section_records": section_records,
        "signature_catalog": signature_catalog,
        "reason_census": reason_census,
        "tranche_census": tranche_census,
        "factor_count_census": factor_count_census,
        "coefficient_role_census": coefficient_role_census,
        "endpoint_attachment_census": endpoint_attachment_census,
        "fiber_wide_census": fiber_wide_census,
        "pattern_census": pattern_census,
        "completion_rows": completion_rows,
        "completed": completed,
        "raw_resultants": raw_resultants,
        "visible_edges": visible_edges,
        "persistent_edges": persistent_edges,
        "completion_edges": completion_edges,
        "connected_completion_edges": connected_completion_edges,
        "isolated_k2_edges": isolated_k2_edges,
        "isolated_k3_edges": isolated_k3_edges,
        "collision_edges": collision_edges,
        "collision_groups": collision_groups,
        "points": points,
        "strips": strips,
        "special_tangencies": special_tangencies,
        "section_960_points": section_960_points,
    }


def main():
    projection = load("DIAG3_PAIR_GLOBAL_FOUR_SUPPORT_PROJECTION.json")
    base = load("DIAG3_PAIR_GLOBAL_FOUR_SUPPORT_BASE_PROJECTION.json.gz")
    roots = load("DIAG3_PAIR_GLOBAL_FOUR_SUPPORT_ROOT_ISOLATION.json.gz")
    open_v = load("DIAG3_PAIR_GLOBAL_FOUR_SUPPORT_OPEN_CELL_V_LIFT.json")
    open_u = load("DIAG3_PAIR_GLOBAL_FOUR_SUPPORT_ALGEBRAIC_T_OPEN_U_STRIP_V_LIFT.json")
    prior_record = load(
        "DIAG3_PAIR_GLOBAL_FOUR_SUPPORT_ALGEBRAIC_T_REGULAR_U_POINT_V_LIFT.json"
    )
    if not all(
        record["status"] == "PROVED"
        for record in (projection, base, roots, open_v, open_u, prior_record)
    ):
        raise AssertionError("unproved source artifact")
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
        row["id"]: row["fiber_degree"]
        for row in source["fiber_walls"]["catalog"]
    }
    tangency_proof = endpoint_tangency_proof(projection, base, roots)
    section_rows = read_shards(open_u, "sections")
    prior_sections = read_shards(prior_record, "sections")
    section_catalog = open_u[
        "algebraic_t_open_u_strip_v_lift"
    ]["section_signature_catalog"]
    observed = analyze(
        section_rows,
        prior_sections,
        section_catalog,
        events,
        endpoint_owners,
        coefficient_factors,
        wall_degrees,
    )

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
            "sections": observed["section_records"][section_start:section_end],
        }
        raw = canonical_gzip_json(shard)
        name = f"{PREFIX}_SHARD_{index:02d}_OF_{SHARD_COUNT}.json.gz"
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
    catalog_name = f"{PREFIX}_SIGNATURE_CATALOG.json.gz"
    (DATA / catalog_name).write_bytes(catalog_raw)
    catalog_metadata = {
        "format": CATALOG_FORMAT,
        "path": catalog_name,
        "entries": len(observed["signature_catalog"]),
        "bytes": len(catalog_raw),
        "sha256": sha256(catalog_raw).hexdigest(),
        "semantic_sha256": digest(observed["signature_catalog"]),
    }

    reason_census = dict(sorted(observed["reason_census"].items()))
    tranche_census = dict(sorted(observed["tranche_census"].items()))
    factor_count_census = {
        str(key): value
        for key, value in sorted(observed["factor_count_census"].items())
    }
    coefficient_role_census = string_census(
        observed["coefficient_role_census"]
    )
    endpoint_attachment_census = string_census(
        observed["endpoint_attachment_census"]
    )
    fiber_wide_census = string_census(observed["fiber_wide_census"])
    pattern_census = string_census(observed["pattern_census"])
    partition_sha256 = digest(observed["section_records"])
    semantic_payload = {
        "prior_semantic_sha256": prior_record["semantic_sha256"],
        "raw_event_map_sha256": digest(event_serial),
        "endpoint_owner_map_sha256": digest(endpoint_serial),
        "coefficient_factor_map_sha256": digest(coefficient_serial),
        "partition_sha256": partition_sha256,
        "signature_catalog_sha256": catalog_metadata["semantic_sha256"],
        "reason_census": reason_census,
        "coefficient_role_census": coefficient_role_census,
        "endpoint_attachment_census": endpoint_attachment_census,
        "tangential_completion_rows": observed["completion_rows"],
        "endpoint_tangency_proof": tangency_proof,
    }
    record = {
        "format": FORMAT,
        "status": "PROVED",
        "scope": {
            "all_algebraic_t_u_point_v_lifts": "COMPLETE",
            "all_algebraic_t_v_lifts": "COMPLETE",
            "global_gluing_and_closure_data": "NOT_CLAIMED",
            "honest_9dvl_score": "2/9",
        },
        "source": {
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
        },
        "coefficient_endpoint_algebraic_t_u_point_v_lift": {
            "completed_points": observed["completed"],
            "remaining_algebraic_t_u_points": 0,
            "completed_reason_census": reason_census,
            "completed_tranche_census": tranche_census,
            "completed_base_factor_count_census": factor_count_census,
            "coefficient_role_census": coefficient_role_census,
            "endpoint_attachment_census": endpoint_attachment_census,
            "fiber_wide_zero_endpoint_census": fiber_wide_census,
            "event_group_pattern_census": pattern_census,
            "completed_raw_resultant_events": observed["raw_resultants"],
            "visible_inversion_edges": observed["visible_edges"],
            "persistent_section_960_edges": observed["persistent_edges"],
            "tangential_clique_completion_edges": observed["completion_edges"],
            "connected_clique_completion_edges": observed[
                "connected_completion_edges"
            ],
            "isolated_tangential_k2_edges": observed["isolated_k2_edges"],
            "isolated_tangential_k3_edges": observed["isolated_k3_edges"],
            "algebraic_collision_edges": observed["collision_edges"],
            "interior_collision_groups": observed["collision_groups"],
            "section_v_root_points": observed["points"],
            "section_open_v_strips": observed["strips"],
            "lifted_cells": observed["points"] + observed["strips"],
            "special_endpoint_tangencies": observed["special_tangencies"],
            "endpoint_tangency_proof": tangency_proof,
            "tangential_clique_completions": observed["completion_rows"],
            "raw_event_map_sha256": digest(event_serial),
            "endpoint_owner_map_sha256": digest(endpoint_serial),
            "coefficient_factor_map_sha256": digest(coefficient_serial),
            "partition_sha256": partition_sha256,
            "signature_catalog_artifact": catalog_metadata,
        },
        "cumulative_algebraic_t_v_lift": {
            "base_cells": 261_571,
            "open_u_strip_base_cells": 131_632,
            "algebraic_u_point_base_cells": 129_939,
            "regular_point_v_lift_cells": 3_664_301,
            "coefficient_endpoint_point_v_lift_cells": 307_146,
            "open_u_strip_v_lift_cells": 4_419_172,
            "lifted_cells": 8_390_619,
        },
        "artifact_shards": {
            "format": SHARD_FORMAT,
            "shard_count": SHARD_COUNT,
            "shards": shard_metadata,
        },
        "semantic_sha256": digest(semantic_payload),
        "resource_effect": {
            "prior_residual_ceiling": RESIDUAL_COUNT,
            "points_examined": RESIDUAL_COUNT,
            "remaining_ceiling": 0,
            "next_stage": (
                "construct global gluing, labels, closure, and middle-rank replay "
                "over the complete local v-lift atlas"
            ),
        },
        "generator_dependency": {
            "python": sys.version.split()[0],
            "independent_verifier": "STRUCTURAL_REPLAY_WITHOUT_PRODUCER_IMPORT",
        },
        "theorem_effect": (
            "Exact coefficient, endpoint, fiber-wide-zero, endpoint-tangency, "
            "and compound-resultant analysis lifts the final 11938 algebraic-t "
            "u-point fibers into 307146 cells. All 261571 algebraic-t base cells "
            "now have local v lifts, totaling 8390619 cells, while global "
            "gluing, labels, closure, middle-rank replay, and both diagonal-three "
            "invariant obligations remain open; honest 9DVL score remains 2/9."
        ),
    }
    OUTPUT.write_text(
        json.dumps(record, sort_keys=True, separators=(",", ":")) + "\n",
        encoding="ascii",
    )
    print("WROTE", OUTPUT)
    print("COMPLETED", observed["completed"], "REMAINING", 0)
    print(
        "V_POINTS",
        observed["points"],
        "V_STRIPS",
        observed["strips"],
        "CELLS",
        observed["points"] + observed["strips"],
    )
    print(
        "COLLISION_EDGES",
        observed["collision_edges"],
        "GROUPS",
        observed["collision_groups"],
        "COMPLETIONS",
        observed["completion_edges"],
        "CONNECTED",
        observed["connected_completion_edges"],
        "ISOLATED_K2",
        observed["isolated_k2_edges"],
        "ISOLATED_K3_EDGES",
        observed["isolated_k3_edges"],
    )
    print("SIGNATURE_CATALOG", catalog_metadata)
    print("CUMULATIVE_ALGEBRAIC_T_CELLS", 8_390_619)


if __name__ == "__main__":
    main()
