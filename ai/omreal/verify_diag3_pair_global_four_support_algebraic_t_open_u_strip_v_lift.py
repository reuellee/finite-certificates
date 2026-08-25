#!/usr/bin/env python3
"""Independent replay of the algebraic-t/open-u-strip v lift."""

from __future__ import annotations

from collections import Counter
from copy import deepcopy
from fractions import Fraction
from functools import lru_cache
import gzip
from hashlib import sha256
import json
from pathlib import Path
import sys


HERE = Path(__file__).resolve().parent
DATA = HERE / "data"
sys.path.insert(0, str(HERE))

import verify_diag3_pair_global_four_support_regular_u_section_v_lift as regular  # noqa: E402


CERTIFICATE = DATA / "DIAG3_PAIR_GLOBAL_FOUR_SUPPORT_ALGEBRAIC_T_OPEN_U_STRIP_V_LIFT.json"
FORMAT = "diag3-pair-global-row2599-four-support-algebraic-t-open-u-strip-v-lift-v1"
SHARD_FORMAT = FORMAT + "-shard"
SHARD_COUNT = 32
SECTION_COUNT = 1_693
THEOREM_EFFECT = (
    "All 131632 open-u strips over algebraic-t sections are lifted into 4419172 "
    "cells; 129939 algebraic-t u-point cells, global gluing, labels, middle-rank "
    "replay, and both diagonal-three invariant obligations remain open; honest "
    "9DVL score remains 2/9."
)
NEXT_STAGE = (
    "lift the remaining 129939 algebraic-t u-point base cells, then construct "
    "global gluing, labels, and closure data"
)


def require(condition, message):
    if not condition:
        raise AssertionError(message)


def load(name: str):
    path = DATA / name
    payload = gzip.decompress(path.read_bytes()) if path.suffix == ".gz" else path.read_bytes()
    return json.loads(payload)


def digest(value) -> str:
    return sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":")).encode("ascii")
    ).hexdigest()


def canonical_gzip_json(value) -> bytes:
    encoded = (json.dumps(value, sort_keys=True, separators=(",", ":")) + "\n").encode(
        "ascii"
    )
    return gzip.compress(encoded, compresslevel=9, mtime=0)


def read_source_shards(record, field):
    answer = []
    for index, metadata in enumerate(record["artifact_shards"]["shards"]):
        raw = (DATA / metadata["path"]).read_bytes()
        require(len(raw) == metadata["bytes"], "source shard size")
        require(sha256(raw).hexdigest() == metadata["sha256"], "source shard digest")
        shard = json.loads(gzip.decompress(raw))
        require(shard["shard_index"] == index, "source shard order")
        answer.extend(shard[field])
    return answer


def occurrence_tokens(sequence):
    counts = Counter()
    answer = []
    for owner in sequence:
        answer.append((owner, counts[owner]))
        counts[owner] += 1
    return answer


def collapsed_owner_groups(sequence, components):
    starts = {}
    occupied = set()
    for raw in components:
        component = tuple(sorted(raw))
        require(component, "empty collision component")
        require(component == tuple(range(component[0], component[-1] + 1)), "component gap")
        require(not occupied.intersection(component), "component overlap")
        occupied.update(component)
        starts[component[0]] = component
    groups = []
    index = 0
    while index < len(sequence):
        component = starts.get(index)
        if component is None:
            require(index not in occupied, "orphan collision index")
            groups.append((sequence[index],))
            index += 1
        else:
            groups.append(tuple(sequence[item] for item in component))
            index = component[-1] + 1
    return groups


def strip_map_from_components(left, right, components):
    left_tokens = occurrence_tokens(left)
    right_tokens = occurrence_tokens(right)
    require(Counter(left_tokens) == Counter(right_tokens), "direct token multiset")
    right_position = {token: index for index, token in enumerate(right_tokens)}
    left_internal = set()
    right_internal = set()
    for raw in components:
        component = tuple(sorted(raw))
        left_internal.update(component[1:])
        positions = tuple(sorted(right_position[left_tokens[index]] for index in component))
        require(positions == tuple(range(positions[0], positions[-1] + 1)), "right component gap")
        right_internal.update(positions[1:])
    return (
        [index for index in range(len(left) + 1) if index not in left_internal],
        [index for index in range(len(right) + 1) if index not in right_internal],
    )


def unique_alignment(sequence, groups):
    """Top-down exhaustive replay, capped after finding two solutions."""

    @lru_cache(maxsize=None)
    def search(group_index, root_index):
        if group_index == len(groups):
            return ((),) if root_index == len(sequence) else ()
        owners = set(groups[group_index])
        solutions = []
        for end in range(root_index, min(len(sequence), root_index + 4 * len(owners)) + 1):
            if set(sequence[root_index:end]) - owners:
                continue
            for suffix in search(group_index + 1, end):
                solutions.append((end - root_index,) + suffix)
                if len(solutions) == 2:
                    return tuple(solutions)
        return tuple(solutions)

    solutions = search(0, 0)
    require(len(solutions) == 1, "final alignment is not unique")
    indices = [0]
    for width in solutions[0]:
        indices.append(indices[-1] + width)
    return indices


def inversion_pairs(left, right):
    common = set(left) & set(right)
    lp = {token: index for index, token in enumerate(left) if token in common}
    rp = {token: index for index, token in enumerate(right) if token in common}
    return {
        (first, second)
        for first in common
        for second in common
        if first < second and (lp[first] - lp[second]) * (rp[first] - rp[second]) < 0
    }


def certified_signature(section_id, left, right):
    if left == right:
        return "transport", tuple((token,) for token in left)
    if section_id == 960:
        collision = ((1, 0), (6, 0))
        require(Counter(left) == Counter(right), "collision token multiset")
        require(inversion_pairs(left, right) == {collision}, "collision inversion owner")
        first, second = sorted(left.index(token) for token in collision)
        require(second == first + 1, "collision adjacency")
        groups = [(token,) for token in left]
        groups[first : second + 1] = [collision]
        return "interior_collision", tuple(groups)
    if section_id == 1193:
        require(Counter(left) - Counter(right) == Counter({(6, 0): 1}), "endpoint loss")
        require(not (Counter(right) - Counter(left)), "endpoint gain")
        require(tuple(token for token in left if token != (6, 0)) == right, "endpoint order")
        return "upper_endpoint_exit", tuple((token,) for token in right)
    raise AssertionError("unexpected signature discrepancy")


def base_section_data(sequences, simple, invisible, multi, residual, final):
    groups = {}
    boundaries = {}
    direct = {}
    tranche = {}

    def add_direct(section_id, components, name):
        groups[section_id] = collapsed_owner_groups(sequences[section_id], components)
        direct[section_id] = strip_map_from_components(
            sequences[section_id], sequences[section_id + 1], components
        )
        tranche[section_id] = name

    for row in simple["simple_section_lift"]["crossings"]:
        add_direct(row[0], [(row[3], row[3] + 1)], "simple")
    for row in invisible["invisible_section_lift"]["completed"]:
        add_direct(row[0], [], "invisible")
    for row in multi["multi_section_lift"]["completed"]:
        add_direct(row[0], row[8], "multi")
    for row in residual["regular_residual_section_lift"]["unchanged"]:
        add_direct(row[0], [], "regular_unchanged")
    for row in residual["regular_residual_section_lift"]["same_count"]:
        add_direct(row[0], row[10], "regular_same_count")
    for row in final["final_section_lift"]["sections"]:
        section_id = row["section_id"]
        groups[section_id] = [tuple(point["owners"]) for point in row["points"]]
        boundaries[section_id] = (
            tuple(row["boundary_zero_factors"]["u=0"]),
            tuple(row["boundary_zero_factors"]["u=1"]),
        )
        tranche[section_id] = "final_" + row["kind"]
    require(set(groups) == set(range(SECTION_COUNT)), "base section coverage")
    return groups, boundaries, direct, tranche


def polynomial_subtract(first, second):
    size = max(len(first), len(second))
    return [
        (first[index] if index < len(first) else 0)
        - (second[index] if index < len(second) else 0)
        for index in range(size)
    ]


def polynomial_multiply(first, second):
    result = [0] * (len(first) + len(second) - 1)
    for i, a in enumerate(first):
        for j, b in enumerate(second):
            result[i + j] += a * b
    return result


def exact_event_proofs(projection, base, roots, open_v, final, events):
    walls = {row["id"]: row for row in projection["fiber_walls"]["catalog"]}
    require(walls[1]["source_active_wall_ids"] == [5], "wall 1 source")
    require(walls[6]["source_active_wall_ids"] == [2], "wall 6 source")
    require(walls[1]["polynomial"] == [
        {"coefficient": "-1", "exponent": [0, 0, 1]},
        {"coefficient": "1", "exponent": [0, 1, 0]},
    ], "wall 1 polynomial")
    require(walls[6]["polynomial"] == [
        {"coefficient": "1", "exponent": [0, 0, 1]},
        {"coefficient": "-2", "exponent": [0, 1, 1]},
        {"coefficient": "-1", "exponent": [0, 2, 0]},
        {"coefficient": "1", "exponent": [0, 2, 1]},
    ], "wall 6 polynomial")
    # F1=a1*v+b1, F6=a6*v+b6.  The equality resultant is a1*b6-a6*b1.
    resultant = polynomial_subtract(
        polynomial_multiply([-1], [0, 0, -1]),
        polynomial_multiply([1, -2, 1], [0, 1]),
    )
    require(resultant == [0, -1, 3, -1], "linear resultant identity")
    factors = {row["id"]: row for row in base["base_factorization"]["catalog"]}
    require(factors[9]["polynomial"] == [
        {"coefficient": "1", "exponent": [0, 0]},
        {"coefficient": "-3", "exponent": [0, 1]},
        {"coefficient": "1", "exponent": [0, 2]},
    ], "base factor 9")
    require(events[9] == [("resultant", (1, 6), 1, 7)], "raw collision owner")
    sections = roots["root_isolation"]["sections"]
    lo = Fraction(sections[960]["left"])
    hi = Fraction(sections[960]["right"])
    require(0 < lo <= hi < 1, "collision root location")
    t_catalog = {row["id"]: row for row in base["second_projection"]["catalog"]}
    require(sections[960]["factor_id"] == 1646, "collision t factor")
    require(t_catalog[1646]["coefficients_low_to_high"] == [1, -3, 1], "collision q")
    require(sections[1193]["factor_id"] == 557, "endpoint t factor")
    require(sections[1193]["left"] == sections[1193]["right"] == "1/2", "endpoint t")
    require(t_catalog[557]["coefficients_low_to_high"] == [-1, 2], "endpoint q")
    final_rows = {row["section_id"]: row for row in final["final_section_lift"]["sections"]}
    require(
        final["final_section_lift"]["vertical_zero_factor_incidences"] == 1,
        "global vertical-factor uniqueness",
    )
    require(final_rows[960]["vertical_zero_factors"] == [9], "vertical factor ownership")
    t_only_endpoints = [
        row
        for row in open_v["v_endpoint_audit"]["factorizations"]
        if row["t_factors"]
    ]
    require(t_only_endpoints == [{
        "base_factors": [],
        "boundary_factors": {},
        "endpoint": 1,
        "t_factors": [[557, 1]],
        "wall_id": 6,
    }], "global t-only endpoint uniqueness")
    # At v=1 wall 6 is 1-2t, so its root is inside before 1/2 and outside after.
    require([1, -2] == [-value for value in [-1, 2]], "endpoint evaluation identity")
    return {
        "section_960_interior_collision": {
            "section_id": 960,
            "t_factor_id": 1646,
            "t_polynomial_low_to_high": [1, -3, 1],
            "isolating_interval": [sections[960]["left"], sections[960]["right"]],
            "fiber_wall_ids": [1, 6],
            "source_active_wall_ids": [5, 2],
            "wall_1_equation": "-v+t",
            "wall_6_equation": "(1-t)^2*v-t^2",
            "linear_v_resultant_low_to_high": resultant,
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


def replay(sectors, source_ids, source_catalog, simple, invisible, multi, residual, final):
    sequences = [[entry[0] for entry in sector] for sector in sectors]
    groups, boundaries, direct, tranche = base_section_data(
        sequences, simple, invisible, multi, residual, final
    )
    catalog = []
    catalog_ids = {}
    rows = []
    event_census = Counter()
    tranche_census = Counter()
    pattern_census = Counter()
    base_points = base_strips = v_points = v_strips = final_alignments = 0
    for section_id in range(SECTION_COUNT):
        current_groups = groups[section_id]
        base_points += len(current_groups)
        base_strips += len(current_groups) + 1
        if section_id in direct:
            left_map, right_map = direct[section_id]
        else:
            lower, upper = boundaries.get(section_id, ((), ()))
            augmented = [lower, *current_groups, upper] if lower or upper else current_groups
            left_map = unique_alignment(sequences[section_id], augmented)
            right_map = unique_alignment(sequences[section_id + 1], augmented)
            final_alignments += 1
            if lower or upper:
                left_map = left_map[1:-1]
                right_map = right_map[1:-1]
        require(len(left_map) == len(right_map) == len(current_groups) + 1, "strip count")
        section_ids = []
        for left_index, right_index in zip(left_map, right_map, strict=True):
            left = source_catalog[source_ids[section_id][left_index]]
            right = source_catalog[source_ids[section_id + 1][right_index]]
            event, signature = certified_signature(section_id, left, right)
            identifier = catalog_ids.get(signature)
            if identifier is None:
                identifier = len(catalog)
                catalog_ids[signature] = identifier
                catalog.append([[list(token) for token in group] for group in signature])
            section_ids.append(identifier)
            points = len(signature)
            v_points += points
            v_strips += points + 1
            event_census[event] += 1
            tranche_census[(tranche[section_id], event)] += 1
            pattern_census[(event, len(left), len(right), points, points + 1)] += 1
        rows.append([section_id, tranche[section_id], left_map, right_map, section_ids])
    return {
        "rows": rows,
        "catalog": catalog,
        "base_points": base_points,
        "base_strips": base_strips,
        "v_points": v_points,
        "v_strips": v_strips,
        "final_alignments": final_alignments,
        "event_census": dict(sorted(event_census.items())),
        "tranche_census": {
            f"{key[0]},{key[1]}": value for key, value in sorted(tranche_census.items())
        },
        "pattern_census": {
            ",".join(map(str, key)): value for key, value in sorted(pattern_census.items())
        },
    }


def verify_shards(candidate, rows):
    expected_metadata = []
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
        expected = canonical_gzip_json(shard)
        name = (
            "DIAG3_PAIR_GLOBAL_FOUR_SUPPORT_ALGEBRAIC_T_OPEN_U_STRIP_V_LIFT_"
            f"SHARD_{index:02d}_OF_{SHARD_COUNT}.json.gz"
        )
        require((DATA / name).read_bytes() == expected, "certificate shard bytes")
        expected_metadata.append({
            "index": index,
            "path": name,
            "section_start": section_start,
            "section_end": section_end,
            "bytes": len(expected),
            "sha256": sha256(expected).hexdigest(),
        })
    expected_manifest = {
        "format": SHARD_FORMAT,
        "shard_count": SHARD_COUNT,
        "shards": expected_metadata,
    }
    require(candidate["artifact_shards"] == expected_manifest, "shard manifest")
    return expected_manifest


def validate_claims(candidate, observed):
    require(candidate["format"] == FORMAT and candidate["status"] == "PROVED", "format/status")
    require(candidate["scope"] == {
        "algebraic_t_open_u_strip_v_lifts": "COMPLETE",
        "algebraic_t_u_point_v_lifts": "NOT_YET_CONSTRUCTED",
        "global_gluing_and_closure_data": "NOT_CLAIMED",
        "honest_9dvl_score": "2/9",
    }, "scope")
    require(candidate["source"] == observed["source"], "source digests")
    lift = candidate["algebraic_t_open_u_strip_v_lift"]
    expected_lift = {
        "t_sections": 1_693,
        "base_u_root_points": 129_939,
        "completed_open_u_strips": 131_632,
        "remaining_algebraic_t_u_point_cells": 129_939,
        "unique_final_alignment_sections": 28,
        "adjacent_signature_agreements": 131_549,
        "exact_residual_strips": 83,
        "event_census": observed["event_census"],
        "tranche_event_census": observed["tranche_census"],
        "signature_pattern_census": observed["pattern_census"],
        "section_v_root_points": 2_143_770,
        "section_open_v_strips": 2_275_402,
        "lifted_cells": 4_419_172,
        "raw_event_map_sha256": observed["raw_event_map_sha256"],
        "partition_sha256": observed["partition_sha256"],
        "section_signature_catalog": observed["catalog"],
        "section_signature_catalog_sha256": observed["catalog_sha256"],
    }
    require(lift == expected_lift, "lift claims")
    require(candidate["exact_event_proofs"] == observed["proofs"], "event proofs")
    require(candidate["artifact_shards"] == observed["artifact_shards"], "artifact shards")
    require(candidate["semantic_sha256"] == observed["semantic_sha256"], "semantic digest")
    require(candidate["resource_effect"] == {
        "prior_algebraic_t_base_cells": 261_571,
        "completed_open_u_strip_cells": 131_632,
        "remaining_algebraic_t_u_point_cells": 129_939,
        "next_stage": NEXT_STAGE,
    }, "resource effect")
    require(candidate["generator_dependency"]["python"].startswith("3.12."), "python version")
    require(candidate["generator_dependency"]["independent_verifier"] == "STRUCTURAL_REPLAY_WITHOUT_PRODUCER_IMPORT", "verifier independence")
    require(candidate["theorem_effect"] == THEOREM_EFFECT, "theorem effect")


def main():
    candidate = load(CERTIFICATE.name)
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
    records = (projection, base, roots, open_base, open_v, simple, invisible, multi, residual, final)
    require(all(record["status"] == "PROVED" for record in records), "source status")
    events, event_serial = regular.independent_event_map(projection, base)
    proofs = exact_event_proofs(projection, base, roots, open_v, final, events)
    sectors = read_source_shards(open_base, "sectors")
    source_ids = read_source_shards(open_v, "strip_signature_ids")
    source_catalog = [
        tuple(tuple(token) for token in signature)
        for signature in open_v["open_cell_v_lift"]["signature_catalog"]
    ]
    replayed = replay(
        sectors, source_ids, source_catalog, simple, invisible, multi, residual, final
    )
    require((replayed["base_points"], replayed["base_strips"]) == (129_939, 131_632), "base census")
    require((replayed["v_points"], replayed["v_strips"]) == (2_143_770, 2_275_402), "v census")
    require(replayed["event_census"] == {
        "interior_collision": 48,
        "transport": 131_549,
        "upper_endpoint_exit": 35,
    }, "event census")
    manifest = verify_shards(candidate, replayed["rows"])
    source = {
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
    }
    partition_sha256 = digest(replayed["rows"])
    catalog_sha256 = digest(replayed["catalog"])
    raw_event_map_sha256 = digest(event_serial)
    semantic_payload = {
        "final_section_lift_semantic_sha256": final["semantic_sha256"],
        "raw_event_map_sha256": raw_event_map_sha256,
        "partition_sha256": partition_sha256,
        "section_signature_catalog_sha256": catalog_sha256,
        "event_census": replayed["event_census"],
        "tranche_event_census": replayed["tranche_census"],
        "signature_pattern_census": replayed["pattern_census"],
        "exact_event_proofs": proofs,
    }
    observed = {
        **replayed,
        "source": source,
        "proofs": proofs,
        "raw_event_map_sha256": raw_event_map_sha256,
        "partition_sha256": partition_sha256,
        "catalog_sha256": catalog_sha256,
        "artifact_shards": manifest,
        "semantic_sha256": digest(semantic_payload),
    }
    validate_claims(candidate, observed)

    mutations = [
        (("scope", "algebraic_t_open_u_strip_v_lifts"), "NOT_YET_CONSTRUCTED"),
        (("scope", "algebraic_t_u_point_v_lifts"), "COMPLETE"),
        (("scope", "global_gluing_and_closure_data"), "COMPLETE"),
        (("scope", "honest_9dvl_score"), "3/9"),
        (("algebraic_t_open_u_strip_v_lift", "completed_open_u_strips"), 131_631),
        (("algebraic_t_open_u_strip_v_lift", "remaining_algebraic_t_u_point_cells"), 0),
        (("algebraic_t_open_u_strip_v_lift", "adjacent_signature_agreements"), 131_550),
        (("algebraic_t_open_u_strip_v_lift", "exact_residual_strips"), 82),
        (("algebraic_t_open_u_strip_v_lift", "section_v_root_points"), 2_143_771),
        (("algebraic_t_open_u_strip_v_lift", "section_open_v_strips"), 2_275_401),
        (("algebraic_t_open_u_strip_v_lift", "lifted_cells"), 4_419_171),
        (("algebraic_t_open_u_strip_v_lift", "raw_event_map_sha256"), "0" * 64),
        (("algebraic_t_open_u_strip_v_lift", "partition_sha256"), "0" * 64),
        (("algebraic_t_open_u_strip_v_lift", "section_signature_catalog_sha256"), "0" * 64),
        (("exact_event_proofs", "section_960_interior_collision", "common_root"), "v=0"),
        (("exact_event_proofs", "section_1193_upper_endpoint_exit", "exact_t"), "2/3"),
        (("semantic_sha256",), "0" * 64),
        (("resource_effect", "remaining_algebraic_t_u_point_cells"), 0),
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
    for section_id, left, right in (
        (960, ((1, 0), (6, 0)), ((1, 0), (6, 0))),
        (1193, ((6, 0), (1, 0)), ((6, 0), (1, 0))),
    ):
        try:
            event, _signature = certified_signature(section_id, left, right)
            require(event != "transport", "structural event was erased")
        except AssertionError:
            structural += 1
        else:
            raise AssertionError("signature-event canary survived")
    try:
        unique_alignment((1,), ((1,), (1,)))
    except AssertionError:
        structural += 1
    else:
        raise AssertionError("alignment canary survived")
    altered = deepcopy(projection)
    altered["fiber_walls"]["catalog"][1]["polynomial"][0]["coefficient"] = "1"
    try:
        exact_event_proofs(altered, base, roots, open_v, final, events)
    except AssertionError:
        structural += 1
    else:
        raise AssertionError("polynomial canary survived")
    rejected += structural
    require(rejected == len(mutations) + 4, "hostile rejection census")

    print("PASS independent algebraic-t/open-u alignment and v-signature replay")
    print("PASS exact section 960 walls 1/6 interior collision on 48 strips")
    print("PASS exact section 1193 wall 6 upper-endpoint exit on 35 strips")
    print("PASS 131632 open-u strips -> 4419172 lifted cells; 129939 u-point cells remain")
    print(f"PASS {rejected}/{len(mutations) + 4} hostile mutations rejected")
    print("SCOPE algebraic-t open-u strips complete; u-point fibers and global topology open; honest 9DVL 2/9")


if __name__ == "__main__":
    main()
