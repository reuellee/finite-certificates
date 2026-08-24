#!/usr/bin/env python3
"""Build the regular algebraic-u-section v-lift over open t sectors.

Every u section in an open t sector is a simple root of one certified base
factor.  This checkpoint completes exactly the sections whose complete raw
event list consists of multiplicity-one pair resultants, whose two adjacent
open-cell v stacks have equal size, and which have no v-endpoint event.  The
remaining coefficient and endpoint/count-change fibers are preserved as an
exact fail-closed frontier.
"""

from __future__ import annotations

from collections import Counter, defaultdict
from fractions import Fraction
import gzip
from hashlib import sha256
import json
from pathlib import Path
import sys


HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import diag3_pair_global_four_support_projection_core as projection_core  # noqa: E402


PROJECTION = HERE / "data" / "DIAG3_PAIR_GLOBAL_FOUR_SUPPORT_PROJECTION.json"
BASE = HERE / "data" / "DIAG3_PAIR_GLOBAL_FOUR_SUPPORT_BASE_PROJECTION.json.gz"
OPEN = HERE / "data" / "DIAG3_PAIR_GLOBAL_FOUR_SUPPORT_OPEN_SECTOR_LIFT.json"
OPEN_V = HERE / "data" / "DIAG3_PAIR_GLOBAL_FOUR_SUPPORT_OPEN_CELL_V_LIFT.json"
OUTPUT = HERE / "data" / "DIAG3_PAIR_GLOBAL_FOUR_SUPPORT_REGULAR_U_SECTION_V_LIFT.json"
FORMAT = "diag3-pair-global-row2599-four-support-regular-u-section-v-lift-v1"
SHARD_FORMAT = (
    "diag3-pair-global-row2599-four-support-regular-u-section-v-lift-shard-v1"
)
SHARD_COUNT = 32
SECTOR_COUNT = 1_694
SECTION_COUNT = 132_134

COUNT_CHANGE = 1
COEFFICIENT = 2
ENDPOINT = 4


def digest(value) -> str:
    return sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":")).encode("ascii")
    ).hexdigest()


def canonical_gzip_json(value) -> bytes:
    encoded = (
        json.dumps(value, sort_keys=True, separators=(",", ":")) + "\n"
    ).encode("ascii")
    return gzip.compress(encoded, compresslevel=9, mtime=0)


def parse_projection_key(row):
    return tuple(
        sorted(
            (tuple(term["exponent"]), Fraction(term["coefficient"]))
            for term in row["polynomial"]
        )
    )


def parse_walls(source):
    walls = []
    for row in source["fiber_walls"]["catalog"]:
        polynomial = {
            tuple(term["exponent"]): Fraction(term["coefficient"])
            for term in row["polynomial"]
        }
        walls.append(
            (
                row["id"],
                row["fiber_degree"],
                projection_core.coefficients_in_v(polynomial),
            )
        )
    return walls


def raw_event_map(source, base):
    """Return every raw first-projection event indexed by base factor."""

    projection_keys = [
        parse_projection_key(row) for row in source["projection"]["catalog"]
    ]
    projection_id = {key: index for index, key in enumerate(projection_keys)}
    if len(projection_id) != 136:
        raise AssertionError("first-projection catalog changed")
    factorizations = {
        row["source_projection_id"]: tuple(
            (factor["id"], factor["multiplicity"])
            for factor in row["factors"]
        )
        for row in base["base_factorization"]["factorizations"]
    }

    events = []

    def append(kind, owners, polynomial):
        reduced, _boundary = projection_core.reduce_boundary(
            polynomial, projection_core.SQUARE_FACETS
        )
        if not reduced:
            return
        key = tuple(sorted(projection_core.canonical(reduced).items()))
        current_projection_id = projection_id[key]
        for factor_id, multiplicity in factorizations[current_projection_id]:
            events.append(
                (
                    factor_id,
                    kind,
                    tuple(owners),
                    multiplicity,
                    current_projection_id,
                )
            )

    walls = parse_walls(source)
    for wall_id, _degree, coefficients in walls:
        for power, polynomial in coefficients.items():
            append("coefficient", (wall_id, power), polynomial)

    linear = [row for row in walls if row[1] == 1]
    quadratic_rows = [row for row in walls if row[1] == 2]
    if len(linear) != 20 or len(quadratic_rows) != 1:
        raise AssertionError("fiber-degree census changed")
    for left in range(len(linear)):
        for right in range(left + 1, len(linear)):
            left_id, _left_degree, left_coefficients = linear[left]
            right_id, _right_degree, right_coefficients = linear[right]
            resultant = projection_core.add(
                (
                    projection_core.multiply(
                        left_coefficients.get(1, {}),
                        right_coefficients.get(0, {}),
                    ),
                    1,
                ),
                (
                    projection_core.multiply(
                        right_coefficients.get(1, {}),
                        left_coefficients.get(0, {}),
                    ),
                    -1,
                ),
            )
            append("resultant", (left_id, right_id), resultant)

    quadratic_id, _degree, quadratic = quadratic_rows[0]
    append(
        "discriminant",
        (quadratic_id,),
        projection_core.add(
            (
                projection_core.multiply(
                    quadratic.get(1, {}), quadratic.get(1, {})
                ),
                1,
            ),
            (
                projection_core.multiply(
                    quadratic.get(2, {}), quadratic.get(0, {})
                ),
                -4,
            ),
        ),
    )
    for linear_id, _degree, coefficients in linear:
        leading = coefficients.get(1, {})
        constant = coefficients.get(0, {})
        resultant = projection_core.add(
            (
                projection_core.multiply(
                    quadratic.get(2, {}),
                    projection_core.multiply(constant, constant),
                ),
                1,
            ),
            (
                projection_core.multiply(
                    quadratic.get(1, {}),
                    projection_core.multiply(leading, constant),
                ),
                -1,
            ),
            (
                projection_core.multiply(
                    quadratic.get(0, {}),
                    projection_core.multiply(leading, leading),
                ),
                1,
            ),
        )
        append("resultant", (linear_id, quadratic_id), resultant)

    by_factor = defaultdict(list)
    for factor_id, kind, owners, multiplicity, current_projection_id in events:
        by_factor[factor_id].append(
            (kind, owners, multiplicity, current_projection_id)
        )
    for factor_id in by_factor:
        by_factor[factor_id].sort()
    serial = [
        [
            factor_id,
            [
                [kind, list(owners), multiplicity, current_projection_id]
                for kind, owners, multiplicity, current_projection_id in rows
            ],
        ]
        for factor_id, rows in sorted(by_factor.items())
    ]
    return by_factor, serial


def load_shard_field(record, field):
    rows = []
    manifest = record["artifact_shards"]
    if manifest["shard_count"] != SHARD_COUNT:
        raise AssertionError("source shard count changed")
    for index, metadata in enumerate(manifest["shards"]):
        compressed = (OPEN.parent / metadata["path"]).read_bytes()
        if len(compressed) != metadata["bytes"]:
            raise AssertionError("source shard byte count changed")
        if sha256(compressed).hexdigest() != metadata["sha256"]:
            raise AssertionError("source shard digest changed")
        shard = json.loads(gzip.decompress(compressed))
        if shard["shard_index"] != index or shard["shard_count"] != SHARD_COUNT:
            raise AssertionError("source shard identity changed")
        rows.extend(shard[field])
    if len(rows) != SECTOR_COUNT:
        raise AssertionError("source sector count changed")
    return rows


def inversion_edges(left, right):
    left_position = {token: index for index, token in enumerate(left)}
    right_position = {token: index for index, token in enumerate(right)}
    common = set(left_position) & set(right_position)
    return {
        (first, second)
        for first in common
        for second in common
        if first < second
        and (left_position[first] - left_position[second])
        * (right_position[first] - right_position[second])
        < 0
    }


def clique_components(edges):
    graph = defaultdict(set)
    for left, right in edges:
        graph[left].add(right)
        graph[right].add(left)
    answer = []
    seen = set()
    for token in sorted(graph):
        if token in seen:
            continue
        stack = [token]
        component = set()
        while stack:
            current = stack.pop()
            if current in component:
                continue
            component.add(current)
            seen.add(current)
            stack.extend(graph[current] - component)
        expected = {
            (left, right)
            for left in component
            for right in component
            if left < right
        }
        if not expected <= edges:
            raise AssertionError("visible collision component is not a clique")
        answer.append(component)
    return answer


def analyze(sectors, sector_ids, signature_catalog, events, endpoint_factors):
    shards = [[] for _ in range(SHARD_COUNT)]
    completed_census = Counter()
    residual_census = Counter()
    raw_kind_incidences = Counter()
    completed_sections = completed_events = completed_inversions = 0
    completed_groups = root_points = strips = 0
    maximum_events = 0

    for sector_id, (stack, ids) in enumerate(zip(sectors, sector_ids, strict=True)):
        if len(ids) != len(stack) + 1:
            raise AssertionError("open v-stack adjacency changed")
        completed = []
        unresolved = []
        for root_index, root in enumerate(stack):
            factor_id = root[0]
            left = signature_catalog[ids[root_index]]
            right = signature_catalog[ids[root_index + 1]]
            current_events = events[factor_id]
            maximum_events = max(maximum_events, len(current_events))
            kinds = Counter(row[0] for row in current_events)
            raw_kind_incidences.update(kinds)

            reasons = 0
            if len(left) != len(right):
                reasons |= COUNT_CHANGE
            if any(kind != "resultant" for kind in kinds):
                reasons |= COEFFICIENT
            if factor_id in endpoint_factors:
                reasons |= ENDPOINT
            if not current_events:
                raise AssertionError("u section has no raw projection event")
            if any(row[2] != 1 for row in current_events):
                raise AssertionError("higher-multiplicity u-section event")

            inversions = inversion_edges(left, right)
            groups = clique_components(inversions)
            inversion_owners = Counter(
                tuple(sorted((left_token[0], right_token[0])))
                for left_token, right_token in inversions
            )
            event_owners = Counter(
                tuple(sorted(row[1]))
                for row in current_events
                if row[0] == "resultant"
            )
            if inversion_owners - event_owners:
                raise AssertionError("visible inversion lacks a raw resultant")

            if reasons:
                unresolved.append([root_index, factor_id, reasons])
                residual_census[reasons] += 1
                continue

            if set(left) != set(right):
                raise AssertionError("regular section changed its bounded branch tokens")
            bounded_walls = {token[0] for token in left}
            for owners, multiplicity in (event_owners - inversion_owners).items():
                if multiplicity and set(owners) <= bounded_walls:
                    raise AssertionError(
                        "invisible simple resultant has both owners in the bounded stack"
                    )

            section_points = len(left) - sum(len(group) - 1 for group in groups)
            section_strips = section_points + 1
            completed.append(
                [
                    root_index,
                    factor_id,
                    len(current_events),
                    len(inversions),
                    len(groups),
                    section_points,
                    section_strips,
                ]
            )
            completed_census[
                (len(current_events), len(inversions), len(groups))
            ] += 1
            completed_sections += 1
            completed_events += len(current_events)
            completed_inversions += len(inversions)
            completed_groups += len(groups)
            root_points += section_points
            strips += section_strips

        shard_index = SHARD_COUNT * sector_id // SECTOR_COUNT
        shards[shard_index].append(
            {"completed": completed, "unresolved": unresolved}
        )

    if completed_sections + sum(residual_census.values()) != SECTION_COUNT:
        raise AssertionError("u-section partition changed")
    return {
        "shards": shards,
        "completed_census": completed_census,
        "residual_census": residual_census,
        "raw_kind_incidences": raw_kind_incidences,
        "completed_sections": completed_sections,
        "completed_events": completed_events,
        "completed_inversions": completed_inversions,
        "completed_groups": completed_groups,
        "root_points": root_points,
        "strips": strips,
        "maximum_events": maximum_events,
    }


def main():
    projection = json.loads(PROJECTION.read_bytes())
    base = json.loads(gzip.decompress(BASE.read_bytes()))
    open_record = json.loads(OPEN.read_bytes())
    open_v = json.loads(OPEN_V.read_bytes())
    if not (
        projection["status"]
        == base["status"]
        == open_record["status"]
        == open_v["status"]
        == "PROVED"
    ):
        raise AssertionError("bad source status")
    source = projection_core.build_record(include_catalog=True)
    if source["semantic_sha256"] != projection["semantic_sha256"]:
        raise AssertionError("projection source changed")
    if open_v["source"]["open_sector_lift_semantic_sha256"] != open_record["semantic_sha256"]:
        raise AssertionError("open-v/open-sector source link changed")

    events, event_serial = raw_event_map(source, base)
    endpoint_factors = {
        factor_id
        for row in open_v["v_endpoint_audit"]["factorizations"]
        for factor_id, _multiplicity in row["base_factors"]
    }
    sectors = load_shard_field(open_record, "sectors")
    sector_ids = load_shard_field(open_v, "strip_signature_ids")
    signature_catalog = [
        tuple(tuple(token) for token in sequence)
        for sequence in open_v["open_cell_v_lift"]["signature_catalog"]
    ]
    observed = analyze(
        sectors, sector_ids, signature_catalog, events, endpoint_factors
    )
    if observed["completed_sections"] != 120_174:
        raise AssertionError("regular u-section completion count changed")
    if observed["residual_census"] != {
        COUNT_CHANGE | ENDPOINT: 3_990,
        COEFFICIENT: 3_388,
        COUNT_CHANGE | COEFFICIENT | ENDPOINT: 2_888,
        COEFFICIENT | ENDPOINT: 1_694,
    }:
        raise AssertionError("regular u-section frontier changed")

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
            "DIAG3_PAIR_GLOBAL_FOUR_SUPPORT_REGULAR_U_SECTION_V_LIFT_"
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

    completed_census = {
        ",".join(map(str, key)): value
        for key, value in sorted(observed["completed_census"].items())
    }
    residual_census = {
        str(key): value for key, value in sorted(observed["residual_census"].items())
    }
    semantic_payload = {
        "projection_semantic_sha256": projection["semantic_sha256"],
        "base_projection_semantic_sha256": base["semantic_sha256"],
        "open_sector_lift_semantic_sha256": open_record["semantic_sha256"],
        "open_cell_v_lift_semantic_sha256": open_v["semantic_sha256"],
        "raw_event_map_sha256": digest(event_serial),
        "endpoint_factorizations_sha256": open_v["v_endpoint_audit"][
            "factorizations_sha256"
        ],
        "partition_sha256": digest(partition),
        "completed_census": completed_census,
        "residual_census": residual_census,
    }
    record = {
        "format": FORMAT,
        "status": "PROVED",
        "scope": {
            "open_t_raw_resultant_regular_u_section_v_lift": "COMPLETE",
            "remaining_open_t_algebraic_u_section_v_lift": "NOT_YET_CONSTRUCTED",
            "algebraic_t_section_v_lift": "NOT_YET_CONSTRUCTED",
            "global_gluing_and_closure_data": "NOT_CLAIMED",
            "honest_9dvl_score": "2/9",
        },
        "source": {
            "projection_semantic_sha256": projection["semantic_sha256"],
            "base_projection_semantic_sha256": base["semantic_sha256"],
            "open_sector_lift_semantic_sha256": open_record["semantic_sha256"],
            "open_cell_v_lift_semantic_sha256": open_v["semantic_sha256"],
            "open_t_sectors": SECTOR_COUNT,
            "algebraic_u_sections": SECTION_COUNT,
        },
        "regular_u_section_v_lift": {
            "completed_sections": observed["completed_sections"],
            "unresolved_sections": SECTION_COUNT - observed["completed_sections"],
            "completed_fraction": "60087/66067",
            "all_raw_event_multiplicities_one": True,
            "maximum_raw_events_on_one_section": observed["maximum_events"],
            "raw_event_kind_incidences": dict(
                sorted(observed["raw_kind_incidences"].items())
            ),
            "completed_raw_resultant_events": observed["completed_events"],
            "visible_inversion_edges": observed["completed_inversions"],
            "interior_collision_groups": observed["completed_groups"],
            "section_v_root_points": observed["root_points"],
            "section_open_v_strips": observed["strips"],
            "lifted_cells": observed["root_points"] + observed["strips"],
            "endpoint_base_factors": len(endpoint_factors),
            "completed_event_inversion_group_census": completed_census,
            "residual_reason_bitmask": {
                "1": "adjacent interior-v root counts differ",
                "2": "a raw coefficient event is present",
                "4": "a v=0 or v=1 endpoint factor is present",
            },
            "residual_reason_census": residual_census,
            "raw_event_map_sha256": digest(event_serial),
            "partition_sha256": digest(partition),
        },
        "artifact_shards": {
            "format": SHARD_FORMAT,
            "shard_count": SHARD_COUNT,
            "shards": shard_rows,
        },
        "semantic_sha256": digest(semantic_payload),
        "resource_effect": {
            "algebraic_u_section_ceiling": SECTION_COUNT,
            "sections_examined": SECTION_COUNT,
            "ceiling_not_triggered": True,
            "next_stage": (
                "resolve the 11960 coefficient or endpoint/count-change u-section "
                "fibers, then lift all base cells over algebraic t sections"
            ),
        },
        "generator_dependency": {
            "python": sys.version.split()[0],
            "independent_verifier": "STANDARD_LIBRARY_STRUCTURAL_REPLAY",
        },
        "theorem_effect": (
            "Exact v-fiber lifts are complete for 120174 of the 132134 algebraic "
            "u sections over open t sectors, contributing 3739392 regular cells; "
            "11960 coefficient or endpoint/count-change fibers, all algebraic-t "
            "v lifts, global gluing, labels, middle-rank replay, and diagonal three "
            "remain open; honest 9DVL score remains 2/9."
        ),
    }
    OUTPUT.write_text(
        json.dumps(record, sort_keys=True, separators=(",", ":")) + "\n",
        encoding="ascii",
    )
    print("WROTE", OUTPUT)
    print(
        "COMPLETED",
        observed["completed_sections"],
        "UNRESOLVED",
        SECTION_COUNT - observed["completed_sections"],
    )
    print(
        "V_POINTS",
        observed["root_points"],
        "V_STRIPS",
        observed["strips"],
        "CELLS",
        observed["root_points"] + observed["strips"],
    )


if __name__ == "__main__":
    main()
