#!/usr/bin/env python3
"""Build the algebraic-t/open-u-strip v-lift certificate."""

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

import build_diag3_pair_global_four_support_regular_u_section_v_lift as regular  # noqa: E402
import diag3_pair_global_four_support_projection_core as projection_core  # noqa: E402


OUTPUT = DATA / "DIAG3_PAIR_GLOBAL_FOUR_SUPPORT_ALGEBRAIC_T_OPEN_U_STRIP_V_LIFT.json"
FORMAT = "diag3-pair-global-row2599-four-support-algebraic-t-open-u-strip-v-lift-v1"
SHARD_FORMAT = FORMAT + "-shard"
SHARD_COUNT = 32
SECTION_COUNT = 1_693


def load(name: str):
    path = DATA / name
    payload = gzip.decompress(path.read_bytes()) if path.suffix == ".gz" else path.read_bytes()
    return json.loads(payload)


def load_sharded(record, field: str):
    rows = []
    for metadata in record["artifact_shards"]["shards"]:
        shard = json.loads(gzip.decompress((DATA / metadata["path"]).read_bytes()))
        rows.extend(shard[field])
    return rows


def digest(value) -> str:
    return sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":")).encode("ascii")
    ).hexdigest()


def canonical_gzip_json(value) -> bytes:
    encoded = (json.dumps(value, sort_keys=True, separators=(",", ":")) + "\n").encode(
        "ascii"
    )
    compressed = bytearray(gzip.compress(encoded, compresslevel=9, mtime=0))
    # zlib stamps byte 9 per host; these fixtures canonically pin the Unix value.
    compressed[9] = 0x03
    if compressed[:10] != b"\x1f\x8b\x08\x00\x00\x00\x00\x00\x02\x03":
        raise AssertionError("unexpected canonical gzip header")
    return bytes(compressed)


def collapse_groups(sequence, components):
    component_by_index = {}
    for raw_component in components:
        component = tuple(sorted(raw_component))
        if tuple(range(component[0], component[-1] + 1)) != component:
            raise AssertionError("noncontiguous collision component")
        for index in component:
            if index in component_by_index:
                raise AssertionError("overlapping collision components")
            component_by_index[index] = component
    answer = []
    index = 0
    while index < len(sequence):
        component = component_by_index.get(index)
        if component is None:
            answer.append((sequence[index],))
            index += 1
        else:
            if index != component[0]:
                raise AssertionError("noncanonical collision component")
            answer.append(tuple(sequence[item] for item in component))
            index = component[-1] + 1
    return answer


def occurrence_tokens(sequence):
    counts = Counter()
    answer = []
    for factor_id in sequence:
        answer.append((factor_id, counts[factor_id]))
        counts[factor_id] += 1
    return answer


def strip_indices_after_collisions(sequence, components):
    internal = set()
    for component in components:
        component = tuple(sorted(component))
        internal.update(range(component[0] + 1, component[-1] + 1))
    return [index for index in range(len(sequence) + 1) if index not in internal]


def direct_transport_maps(left, right, left_components):
    left_tokens = occurrence_tokens(left)
    right_tokens = occurrence_tokens(right)
    if Counter(left_tokens) != Counter(right_tokens):
        raise AssertionError("unequal direct-transport root multisets")
    right_position = {token: index for index, token in enumerate(right_tokens)}
    right_components = []
    for component in left_components:
        positions = tuple(sorted(right_position[left_tokens[index]] for index in component))
        if tuple(range(positions[0], positions[-1] + 1)) != positions:
            raise AssertionError("right collision group is noncontiguous")
        right_components.append(positions)
    return (
        strip_indices_after_collisions(left, left_components),
        strip_indices_after_collisions(right, right_components),
    )


def align_side(sequence, point_groups):
    """Count and reconstruct monotone assignments by dynamic programming."""

    states = {(0, 0): (1, None)}
    for point_index, owners in enumerate(point_groups):
        owner_set = set(owners)
        for _unused, root_index in [key for key in states if key[0] == point_index]:
            path_count, _previous = states[(point_index, root_index)]
            for width in range(4 * len(owners) + 1):
                end = root_index + width
                if end > len(sequence):
                    break
                if set(sequence[root_index:end]) - owner_set:
                    continue
                key = (point_index + 1, end)
                previous_count, previous = states.get(key, (0, None))
                states[key] = (
                    min(2, previous_count + path_count),
                    previous if previous is not None else (root_index, width),
                )
    terminal = (len(point_groups), len(sequence))
    if terminal not in states:
        return 0, None
    solution_count = states[terminal][0]
    widths = [0] * len(point_groups)
    point_index, root_index = terminal
    while point_index:
        previous = states[(point_index, root_index)][1]
        if previous is None:
            raise AssertionError("missing alignment predecessor")
        prior_root, width = previous
        widths[point_index - 1] = width
        point_index -= 1
        root_index = prior_root
    indices = [0]
    for width in widths:
        indices.append(indices[-1] + width)
    return solution_count, indices


def inversion_pairs(left, right):
    common = set(left) & set(right)
    left_position = {token: index for index, token in enumerate(left) if token in common}
    right_position = {token: index for index, token in enumerate(right) if token in common}
    return {
        tuple(sorted((first, second)))
        for first in common
        for second in common
        if first < second
        and (left_position[first] - left_position[second])
        * (right_position[first] - right_position[second])
        < 0
    }


def section_signature(section_id, left, right):
    if left == right:
        return "transport", tuple((token,) for token in left)
    if section_id == 960:
        pair = ((1, 0), (6, 0))
        if Counter(left) != Counter(right) or inversion_pairs(left, right) != {pair}:
            raise AssertionError("section 960 inversion changed")
        positions = sorted(left.index(token) for token in pair)
        if positions[1] != positions[0] + 1:
            raise AssertionError("section 960 collision is nonadjacent")
        groups = [(token,) for token in left]
        groups[positions[0] : positions[1] + 1] = [pair]
        return "interior_collision", tuple(groups)
    if section_id == 1193:
        if Counter(left) - Counter(right) != Counter({(6, 0): 1}):
            raise AssertionError("section 1193 lost-token census changed")
        if Counter(right) - Counter(left):
            raise AssertionError("section 1193 gained a token")
        if tuple(token for token in left if token != (6, 0)) != right:
            raise AssertionError("section 1193 order changed")
        return "upper_endpoint_exit", tuple((token,) for token in right)
    raise AssertionError(f"unclassified transport discrepancy in section {section_id}")


def reconstruct_groups(sequences, simple, invisible, multi, residual, final):
    point_groups = {}
    boundary_groups = {}
    direct_maps = {}
    tranche = {}
    for row in simple["simple_section_lift"]["crossings"]:
        section_id, _factor, _root, position, _left, _right, _count = row
        components = [(position, position + 1)]
        point_groups[section_id] = collapse_groups(sequences[section_id], components)
        direct_maps[section_id] = direct_transport_maps(
            sequences[section_id], sequences[section_id + 1], components
        )
        tranche[section_id] = "simple"
    for row in invisible["invisible_section_lift"]["completed"]:
        section_id = row[0]
        point_groups[section_id] = collapse_groups(sequences[section_id], [])
        direct_maps[section_id] = direct_transport_maps(
            sequences[section_id], sequences[section_id + 1], []
        )
        tranche[section_id] = "invisible"
    for row in multi["multi_section_lift"]["completed"]:
        section_id = row[0]
        point_groups[section_id] = collapse_groups(sequences[section_id], row[8])
        direct_maps[section_id] = direct_transport_maps(
            sequences[section_id], sequences[section_id + 1], row[8]
        )
        tranche[section_id] = "multi"
    for row in residual["regular_residual_section_lift"]["unchanged"]:
        section_id = row[0]
        point_groups[section_id] = collapse_groups(sequences[section_id], [])
        direct_maps[section_id] = direct_transport_maps(
            sequences[section_id], sequences[section_id + 1], []
        )
        tranche[section_id] = "regular_unchanged"
    for row in residual["regular_residual_section_lift"]["same_count"]:
        section_id = row[0]
        point_groups[section_id] = collapse_groups(sequences[section_id], row[10])
        direct_maps[section_id] = direct_transport_maps(
            sequences[section_id], sequences[section_id + 1], row[10]
        )
        tranche[section_id] = "regular_same_count"
    for row in final["final_section_lift"]["sections"]:
        section_id = row["section_id"]
        point_groups[section_id] = [tuple(point["owners"]) for point in row["points"]]
        boundary_groups[section_id] = (
            tuple(row["boundary_zero_factors"]["u=0"]),
            tuple(row["boundary_zero_factors"]["u=1"]),
        )
        tranche[section_id] = "final_" + row["kind"]
    if set(point_groups) != set(range(SECTION_COUNT)):
        raise AssertionError("base section partition is incomplete")
    return point_groups, boundary_groups, direct_maps, tranche


def exact_event_proofs(projection, base, roots, open_v, final, raw_events):
    walls = {row["id"]: row for row in projection["fiber_walls"]["catalog"]}
    wall1 = walls[1]
    wall6 = walls[6]
    expected1 = [
        {"coefficient": "-1", "exponent": [0, 0, 1]},
        {"coefficient": "1", "exponent": [0, 1, 0]},
    ]
    expected6 = [
        {"coefficient": "1", "exponent": [0, 0, 1]},
        {"coefficient": "-2", "exponent": [0, 1, 1]},
        {"coefficient": "-1", "exponent": [0, 2, 0]},
        {"coefficient": "1", "exponent": [0, 2, 1]},
    ]
    if wall1["polynomial"] != expected1 or wall6["polynomial"] != expected6:
        raise AssertionError("event wall polynomial changed")
    base_factors = {row["id"]: row for row in base["base_factorization"]["catalog"]}
    if base_factors[9]["polynomial"] != [
        {"coefficient": "1", "exponent": [0, 0]},
        {"coefficient": "-3", "exponent": [0, 1]},
        {"coefficient": "1", "exponent": [0, 2]},
    ]:
        raise AssertionError("collision base factor changed")
    if raw_events[9] != [("resultant", (1, 6), 1, 7)]:
        raise AssertionError("collision raw-event ownership changed")
    t_factors = {row["id"]: row for row in base["second_projection"]["catalog"]}
    sections = roots["root_isolation"]["sections"]
    if sections[960] != {
        "factor_id": 1646,
        "factor_root_index": 0,
        "id": 960,
        "left": "5702887/14930352",
        "right": "9227465/24157817",
    } or t_factors[1646]["coefficients_low_to_high"] != [1, -3, 1]:
        raise AssertionError("section 960 root certificate changed")
    if sections[1193] != {
        "factor_id": 557,
        "factor_root_index": 0,
        "id": 1193,
        "left": "1/2",
        "right": "1/2",
    } or t_factors[557]["coefficients_low_to_high"] != [-1, 2]:
        raise AssertionError("section 1193 root certificate changed")
    final_rows = {row["section_id"]: row for row in final["final_section_lift"]["sections"]}
    if final["final_section_lift"]["vertical_zero_factor_incidences"] != 1:
        raise AssertionError("vertical-zero incidence is not globally unique")
    if final_rows[960]["vertical_zero_factors"] != [9]:
        raise AssertionError("section 960 vertical event changed")
    t_only_endpoints = [
        row
        for row in open_v["v_endpoint_audit"]["factorizations"]
        if row["t_factors"]
    ]
    if t_only_endpoints != [
        {
            "base_factors": [],
            "boundary_factors": {},
            "endpoint": 1,
            "t_factors": [[557, 1]],
            "wall_id": 6,
        }
    ]:
        raise AssertionError("t-only endpoint event is not globally unique")
    return {
        "section_960_interior_collision": {
            "section_id": 960,
            "t_factor_id": 1646,
            "t_polynomial_low_to_high": [1, -3, 1],
            "isolating_interval": ["5702887/14930352", "9227465/24157817"],
            "fiber_wall_ids": [1, 6],
            "source_active_wall_ids": [5, 2],
            "wall_1_equation": "-v+t",
            "wall_6_equation": "(1-t)^2*v-t^2",
            "linear_v_resultant_low_to_high": [0, -1, 3, -1],
            "resultant_factorization": "-t*(1-3*t+t^2)",
            "common_root": "v=t",
            "common_root_location": "0<v<1",
            "open_u_strips": 48,
        },
        "section_1193_upper_endpoint_exit": {
            "section_id": 1193,
            "t_factor_id": 557,
            "t_polynomial_low_to_high": [-1, 2],
            "exact_t": "1/2",
            "fiber_wall_id": 6,
            "wall_equation": "(1-t)^2*v-t^2",
            "root_formula": "v=(t/(1-t))^2",
            "upper_endpoint_evaluation": "1-2*t",
            "left_sector": "0<v<1",
            "section": "v=1 boundary (not an interior root)",
            "right_sector": "v>1",
            "open_u_strips": 35,
        },
    }


def main():
    projection = load("DIAG3_PAIR_GLOBAL_FOUR_SUPPORT_PROJECTION.json")
    base = load("DIAG3_PAIR_GLOBAL_FOUR_SUPPORT_BASE_PROJECTION.json.gz")
    roots = load("DIAG3_PAIR_GLOBAL_FOUR_SUPPORT_ROOT_ISOLATION.json.gz")
    open_base = load("DIAG3_PAIR_GLOBAL_FOUR_SUPPORT_OPEN_SECTOR_LIFT.json")
    open_v = load("DIAG3_PAIR_GLOBAL_FOUR_SUPPORT_OPEN_CELL_V_LIFT.json")
    simple = load("DIAG3_PAIR_GLOBAL_FOUR_SUPPORT_SIMPLE_SECTION_LIFT.json")
    invisible = load("DIAG3_PAIR_GLOBAL_FOUR_SUPPORT_INVISIBLE_SECTION_LIFT.json")
    multi = load("DIAG3_PAIR_GLOBAL_FOUR_SUPPORT_MULTI_SECTION_LIFT.json")
    residual = load("DIAG3_PAIR_GLOBAL_FOUR_SUPPORT_REGULAR_RESIDUAL_SECTION_LIFT.json")
    final = load("DIAG3_PAIR_GLOBAL_FOUR_SUPPORT_FINAL_SECTION_LIFT.json")
    sources = (projection, base, roots, open_base, open_v, simple, invisible, multi, residual, final)
    if not all(record["status"] == "PROVED" for record in sources):
        raise AssertionError("unproved source artifact")

    source_projection = projection_core.build_record(include_catalog=True)
    if source_projection["semantic_sha256"] != projection["semantic_sha256"]:
        raise AssertionError("projection source regeneration changed")
    raw_events, raw_event_serial = regular.raw_event_map(source_projection, base)
    proofs = exact_event_proofs(projection, base, roots, open_v, final, raw_events)

    sectors = load_sharded(open_base, "sectors")
    signature_ids = load_sharded(open_v, "strip_signature_ids")
    if len(sectors) != 1_694 or len(signature_ids) != 1_694:
        raise AssertionError("open-sector coverage changed")
    sequences = [[entry[0] for entry in sector] for sector in sectors]
    source_catalog = [
        tuple(tuple(token) for token in signature)
        for signature in open_v["open_cell_v_lift"]["signature_catalog"]
    ]
    point_groups, boundary_groups, direct_maps, tranche = reconstruct_groups(
        sequences, simple, invisible, multi, residual, final
    )

    section_catalog = []
    section_catalog_ids = {}
    rows = []
    event_census = Counter()
    tranche_census = Counter()
    pattern_census = Counter()
    base_points = base_strips = v_points = v_strips = 0
    unique_alignments = 0
    for section_id in range(SECTION_COUNT):
        groups = point_groups[section_id]
        base_points += len(groups)
        base_strips += len(groups) + 1
        if section_id in direct_maps:
            left_map, right_map = direct_maps[section_id]
        else:
            lower, upper = boundary_groups.get(section_id, ((), ()))
            augmented = [lower, *groups, upper] if lower or upper else groups
            left_count, left_map = align_side(sequences[section_id], augmented)
            right_count, right_map = align_side(sequences[section_id + 1], augmented)
            if left_count != 1 or right_count != 1:
                raise AssertionError(f"section {section_id} alignment is not unique")
            unique_alignments += 1
            if lower or upper:
                left_map = left_map[1:-1]
                right_map = right_map[1:-1]
        if len(left_map) != len(groups) + 1 or len(right_map) != len(groups) + 1:
            raise AssertionError("strip alignment length changed")
        section_ids = []
        for left_index, right_index in zip(left_map, right_map, strict=True):
            left = source_catalog[signature_ids[section_id][left_index]]
            right = source_catalog[signature_ids[section_id + 1][right_index]]
            event, signature = section_signature(section_id, left, right)
            catalog_id = section_catalog_ids.get(signature)
            if catalog_id is None:
                catalog_id = len(section_catalog)
                section_catalog_ids[signature] = catalog_id
                section_catalog.append(
                    [[list(token) for token in group] for group in signature]
                )
            section_ids.append(catalog_id)
            points = len(signature)
            v_points += points
            v_strips += points + 1
            event_census[event] += 1
            tranche_census[(tranche[section_id], event)] += 1
            pattern_census[(event, len(left), len(right), points, points + 1)] += 1
        rows.append([section_id, tranche[section_id], left_map, right_map, section_ids])

    if (base_points, base_strips) != (129_939, 131_632):
        raise AssertionError("algebraic-t base-cell census changed")
    if event_census != {
        "transport": 131_549,
        "interior_collision": 48,
        "upper_endpoint_exit": 35,
    }:
        raise AssertionError("transport residue changed")
    if (v_points, v_strips, v_points + v_strips) != (2_143_770, 2_275_402, 4_419_172):
        raise AssertionError("lifted-cell census changed")

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
            "sections": rows[section_start:section_end],
        }
        compressed = canonical_gzip_json(shard)
        name = (
            "DIAG3_PAIR_GLOBAL_FOUR_SUPPORT_ALGEBRAIC_T_OPEN_U_STRIP_V_LIFT_"
            f"SHARD_{index:02d}_OF_{SHARD_COUNT}.json.gz"
        )
        (DATA / name).write_bytes(compressed)
        shard_metadata.append(
            {
                "index": index,
                "path": name,
                "section_start": section_start,
                "section_end": section_end,
                "bytes": len(compressed),
                "sha256": sha256(compressed).hexdigest(),
            }
        )

    event_census_json = dict(sorted(event_census.items()))
    tranche_census_json = {
        f"{key[0]},{key[1]}": value for key, value in sorted(tranche_census.items())
    }
    pattern_census_json = {
        ",".join(map(str, key)): value for key, value in sorted(pattern_census.items())
    }
    partition_sha256 = digest(rows)
    catalog_sha256 = digest(section_catalog)
    semantic_payload = {
        "final_section_lift_semantic_sha256": final["semantic_sha256"],
        "raw_event_map_sha256": digest(raw_event_serial),
        "partition_sha256": partition_sha256,
        "section_signature_catalog_sha256": catalog_sha256,
        "event_census": event_census_json,
        "tranche_event_census": tranche_census_json,
        "signature_pattern_census": pattern_census_json,
        "exact_event_proofs": proofs,
    }
    record = {
        "format": FORMAT,
        "status": "PROVED",
        "scope": {
            "algebraic_t_open_u_strip_v_lifts": "COMPLETE",
            "algebraic_t_u_point_v_lifts": "NOT_YET_CONSTRUCTED",
            "global_gluing_and_closure_data": "NOT_CLAIMED",
            "honest_9dvl_score": "2/9",
        },
        "source": {
            "projection_semantic_sha256": projection["semantic_sha256"],
            "base_projection_semantic_sha256": base["semantic_sha256"],
            "root_isolation_semantic_sha256": roots["semantic_sha256"],
            "open_sector_lift_semantic_sha256": open_base["semantic_sha256"],
            "open_cell_v_lift_semantic_sha256": open_v["semantic_sha256"],
            "simple_section_lift_semantic_sha256": simple["semantic_sha256"],
            "invisible_section_lift_semantic_sha256": invisible["semantic_sha256"],
            "multi_section_lift_semantic_sha256": multi["semantic_sha256"],
            "regular_residual_section_lift_semantic_sha256": residual["semantic_sha256"],
            "final_section_lift_semantic_sha256": final["semantic_sha256"],
        },
        "algebraic_t_open_u_strip_v_lift": {
            "t_sections": SECTION_COUNT,
            "base_u_root_points": base_points,
            "completed_open_u_strips": base_strips,
            "remaining_algebraic_t_u_point_cells": base_points,
            "unique_final_alignment_sections": unique_alignments,
            "adjacent_signature_agreements": event_census["transport"],
            "exact_residual_strips": event_census["interior_collision"]
            + event_census["upper_endpoint_exit"],
            "event_census": event_census_json,
            "tranche_event_census": tranche_census_json,
            "signature_pattern_census": pattern_census_json,
            "section_v_root_points": v_points,
            "section_open_v_strips": v_strips,
            "lifted_cells": v_points + v_strips,
            "raw_event_map_sha256": digest(raw_event_serial),
            "partition_sha256": partition_sha256,
            "section_signature_catalog": section_catalog,
            "section_signature_catalog_sha256": catalog_sha256,
        },
        "exact_event_proofs": proofs,
        "artifact_shards": {
            "format": SHARD_FORMAT,
            "shard_count": SHARD_COUNT,
            "shards": shard_metadata,
        },
        "semantic_sha256": digest(semantic_payload),
        "resource_effect": {
            "prior_algebraic_t_base_cells": 261_571,
            "completed_open_u_strip_cells": base_strips,
            "remaining_algebraic_t_u_point_cells": base_points,
            "next_stage": (
                "lift the remaining 129939 algebraic-t u-point base cells, then "
                "construct global gluing, labels, and closure data"
            ),
        },
        "generator_dependency": {
            "python": sys.version.split()[0],
            "independent_verifier": "STRUCTURAL_REPLAY_WITHOUT_PRODUCER_IMPORT",
        },
        "theorem_effect": (
            "All 131632 open-u strips over algebraic-t sections are lifted into "
            "4419172 cells; 129939 algebraic-t u-point cells, global gluing, labels, "
            "middle-rank replay, and both diagonal-three invariant obligations remain "
            "open; honest 9DVL score remains 2/9."
        ),
    }
    OUTPUT.write_text(
        json.dumps(record, sort_keys=True, separators=(",", ":")) + "\n",
        encoding="ascii",
    )
    print("WROTE", OUTPUT)
    print("BASE_STRIPS", base_strips, "REMAINING_U_POINTS", base_points)
    print("V_POINTS", v_points, "V_STRIPS", v_strips, "CELLS", v_points + v_strips)
    print("EVENTS", event_census_json)
    print("SIGNATURE_CATALOG", len(section_catalog), catalog_sha256)


if __name__ == "__main__":
    main()
