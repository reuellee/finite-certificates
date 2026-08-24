#!/usr/bin/env python3
"""Independent standard-library replay of the regular algebraic-u v-lift."""

from __future__ import annotations

from collections import Counter, defaultdict
from copy import deepcopy
from fractions import Fraction
import gzip
from hashlib import sha256
import json
from math import gcd, lcm
from pathlib import Path
import sys


HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import verify_diag3_pair_global_four_support_open_cell_v_lift as open_v_verifier  # noqa: E402


PROJECTION = HERE / "data" / "DIAG3_PAIR_GLOBAL_FOUR_SUPPORT_PROJECTION.json"
BASE = HERE / "data" / "DIAG3_PAIR_GLOBAL_FOUR_SUPPORT_BASE_PROJECTION.json.gz"
ROOTS = HERE / "data" / "DIAG3_PAIR_GLOBAL_FOUR_SUPPORT_ROOT_ISOLATION.json.gz"
OPEN = HERE / "data" / "DIAG3_PAIR_GLOBAL_FOUR_SUPPORT_OPEN_SECTOR_LIFT.json"
OPEN_V = HERE / "data" / "DIAG3_PAIR_GLOBAL_FOUR_SUPPORT_OPEN_CELL_V_LIFT.json"
CERTIFICATE = HERE / "data" / "DIAG3_PAIR_GLOBAL_FOUR_SUPPORT_REGULAR_U_SECTION_V_LIFT.json"
FORMAT = "diag3-pair-global-row2599-four-support-regular-u-section-v-lift-v1"
SHARD_FORMAT = (
    "diag3-pair-global-row2599-four-support-regular-u-section-v-lift-shard-v1"
)
OPEN_SHARD_FORMAT = "diag3-pair-global-row2599-four-support-open-sector-lift-shard-v1"
OPEN_V_SHARD_FORMAT = "diag3-pair-global-row2599-four-support-open-cell-v-lift-shard-v1"
SHARD_COUNT = 32
SECTOR_COUNT = 1_694
SECTION_COUNT = 132_134

COUNT_CHANGE = 1
COEFFICIENT = 2
ENDPOINT = 4
SQUARE_FACETS = (
    ("u=0", {(1, 0): 1}, 0, 1),
    ("u=1", {(0, 0): 1, (1, 0): -1}, 0, -1),
    ("t=0", {(0, 1): 1}, 1, 1),
    ("t=1", {(0, 0): 1, (0, 1): -1}, 1, -1),
)

THEOREM_EFFECT = (
    "Exact v-fiber lifts are complete for 120174 of the 132134 algebraic u "
    "sections over open t sectors, contributing 3739392 regular cells; 11960 "
    "coefficient or endpoint/count-change fibers, all algebraic-t v lifts, "
    "global gluing, labels, middle-rank replay, and diagonal three remain open; "
    "honest 9DVL score remains 2/9."
)
NEXT_STAGE = (
    "resolve the 11960 coefficient or endpoint/count-change u-section fibers, "
    "then lift all base cells over algebraic t sections"
)


def require(condition, message):
    if not condition:
        raise AssertionError(message)


def digest(value):
    return sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":")).encode("ascii")
    ).hexdigest()


def canonical_gzip_json(value):
    encoded = (
        json.dumps(value, sort_keys=True, separators=(",", ":")) + "\n"
    ).encode("ascii")
    return gzip.compress(encoded, compresslevel=9, mtime=0)


def canonical(polynomial):
    cleaned = {
        exponent: Fraction(value)
        for exponent, value in polynomial.items()
        if value
    }
    if not cleaned:
        return {}
    denominator = 1
    for value in cleaned.values():
        denominator = lcm(denominator, value.denominator)
    integer = {
        exponent: int(value * denominator)
        for exponent, value in cleaned.items()
    }
    divisor = 0
    for value in integer.values():
        divisor = gcd(divisor, abs(value))
    integer = {exponent: value // max(divisor, 1) for exponent, value in integer.items()}
    if integer[max(integer)] < 0:
        integer = {exponent: -value for exponent, value in integer.items()}
    return integer


def divide_linear(polynomial, factor, axis, leading):
    dimension = len(next(iter(polynomial)))
    work = Counter({term: Fraction(value) for term, value in polynomial.items()})
    quotient = Counter()
    while work:
        candidates = [term for term in work if term[axis]]
        if not candidates:
            break
        term = max(candidates, key=lambda exponent: (exponent[axis], exponent))
        target = list(term)
        target[axis] -= 1
        target = tuple(target)
        coefficient = work[term] / leading
        quotient[target] += coefficient
        for exponent, value in factor.items():
            output = tuple(
                target[index] + exponent[index] for index in range(dimension)
            )
            work[output] -= coefficient * value
            if not work[output]:
                del work[output]
    return dict(quotient), dict(work)


def reduce_boundary(polynomial):
    if not polynomial:
        return {}
    dimension = len(next(iter(polynomial)))
    minimum = tuple(
        min(exponent[axis] for exponent in polynomial)
        for axis in range(dimension)
    )
    current = canonical(
        {
            tuple(
                exponent[axis] - minimum[axis]
                for axis in range(dimension)
            ): coefficient
            for exponent, coefficient in polynomial.items()
        }
    )
    changed = True
    while changed:
        changed = False
        for _name, factor, axis, leading in SQUARE_FACETS:
            quotient, remainder = divide_linear(
                current, factor, axis, leading
            )
            if not remainder:
                current = canonical(quotient)
                changed = True
                break
    return current


def polynomial_rows(polynomial):
    return [
        {"exponent": list(exponent), "coefficient": str(coefficient)}
        for exponent, coefficient in sorted(polynomial.items())
    ]


def wall_coefficients(row):
    answer = defaultdict(Counter)
    for term in row["polynomial"]:
        degree_u, degree_t, degree_v = term["exponent"]
        answer[degree_v][(degree_u, degree_t)] += Fraction(term["coefficient"])
    return {
        power: {exponent: value for exponent, value in polynomial.items() if value}
        for power, polynomial in answer.items()
    }


def multiply(left, right):
    answer = Counter()
    for left_exponent, left_value in left.items():
        for right_exponent, right_value in right.items():
            answer[
                (
                    left_exponent[0] + right_exponent[0],
                    left_exponent[1] + right_exponent[1],
                )
            ] += left_value * right_value
    return {key: value for key, value in answer.items() if value}


def add(*rows):
    answer = Counter()
    for polynomial, scale in rows:
        for exponent, value in polynomial.items():
            answer[exponent] += scale * value
    return {key: value for key, value in answer.items() if value}


def independent_event_map(source, base):
    """Reconstruct raw event ownership without importing the new producer."""

    by_projection = {
        row["source_projection_id"]: tuple(
            (factor["id"], factor["multiplicity"])
            for factor in row["factors"]
        )
        for row in base["base_factorization"]["factorizations"]
    }
    require(len(by_projection) == 136, "base factorization coverage")

    pending = []

    def register(kind, owners, polynomial):
        reduced = reduce_boundary(polynomial)
        if not reduced:
            return
        pending.append((kind, tuple(owners), tuple(sorted(canonical(reduced).items()))))

    parsed = []
    for row in source["fiber_walls"]["catalog"]:
        parsed.append((row["id"], row["fiber_degree"], wall_coefficients(row)))
        for power, coefficient in wall_coefficients(row).items():
            register("coefficient", (row["id"], power), coefficient)

    linear = [row for row in parsed if row[1] == 1]
    quadratic_rows = [row for row in parsed if row[1] == 2]
    require(len(linear) == 20 and len(quadratic_rows) == 1, "fiber census")
    for left_index, left in enumerate(linear):
        for right in linear[left_index + 1 :]:
            left_id, _degree, left_coefficients = left
            right_id, _degree, right_coefficients = right
            register(
                "resultant",
                (left_id, right_id),
                add(
                    (
                        multiply(
                            left_coefficients.get(1, {}),
                            right_coefficients.get(0, {}),
                        ),
                        1,
                    ),
                    (
                        multiply(
                            right_coefficients.get(1, {}),
                            left_coefficients.get(0, {}),
                        ),
                        -1,
                    ),
                ),
            )

    quadratic_id, _degree, quadratic = quadratic_rows[0]
    register(
        "discriminant",
        (quadratic_id,),
        add(
            (multiply(quadratic.get(1, {}), quadratic.get(1, {})), 1),
            (multiply(quadratic.get(2, {}), quadratic.get(0, {})), -4),
        ),
    )
    for linear_id, _degree, coefficients in linear:
        leading = coefficients.get(1, {})
        constant = coefficients.get(0, {})
        register(
            "resultant",
            (linear_id, quadratic_id),
            add(
                (
                    multiply(
                        quadratic.get(2, {}), multiply(constant, constant)
                    ),
                    1,
                ),
                (
                    multiply(
                        quadratic.get(1, {}), multiply(leading, constant)
                    ),
                    -1,
                ),
                (
                    multiply(
                        quadratic.get(0, {}), multiply(leading, leading)
                    ),
                    1,
                ),
            ),
        )

    unique = sorted({key for _kind, _owners, key in pending})
    require(len(unique) == 136, "first projection catalog")
    key_to_projection = {key: index for index, key in enumerate(unique)}
    projection_catalog = [
        {"id": index, "polynomial": polynomial_rows(dict(key))}
        for index, key in enumerate(unique)
    ]
    require(
        digest(projection_catalog) == source["projection"]["catalog_sha256"],
        "independent projection catalog digest",
    )
    semantic = sha256(
        b"diag3-four-support-projection-v1\0"
        + json.dumps(
            {
                "walls": source["fiber_walls"]["catalog"],
                "projection": projection_catalog,
            },
            sort_keys=True,
            separators=(",", ":"),
        ).encode("ascii")
    ).hexdigest()
    require(semantic == source["semantic_sha256"], "independent projection semantic replay")

    raw = []
    for kind, owners, key in pending:
        projection_id = key_to_projection[key]
        for factor_id, multiplicity in by_projection[projection_id]:
            raw.append(
                (factor_id, kind, owners, multiplicity, projection_id)
            )

    by_factor = defaultdict(list)
    for factor_id, kind, owners, multiplicity, projection_id in raw:
        by_factor[factor_id].append((kind, owners, multiplicity, projection_id))
    for factor_id in by_factor:
        by_factor[factor_id].sort()
    serial = [
        [
            factor_id,
            [
                [kind, list(owners), multiplicity, projection_id]
                for kind, owners, multiplicity, projection_id in rows
            ],
        ]
        for factor_id, rows in sorted(by_factor.items())
    ]
    return by_factor, serial


def read_source_shards(record, expected_format, field):
    manifest = record["artifact_shards"]
    require(manifest["format"] == expected_format, "source shard format")
    require(manifest["shard_count"] == SHARD_COUNT, "source shard count")
    require(len(manifest["shards"]) == SHARD_COUNT, "source shard rows")
    result = []
    for index, metadata in enumerate(manifest["shards"]):
        sector_start = SECTOR_COUNT * index // SHARD_COUNT
        sector_end = SECTOR_COUNT * (index + 1) // SHARD_COUNT
        require(metadata["index"] == index, "source shard index")
        require(metadata["sector_start"] == sector_start, "source shard start")
        require(metadata["sector_end"] == sector_end, "source shard end")
        compressed = (OPEN.parent / metadata["path"]).read_bytes()
        require(len(compressed) == metadata["bytes"], "source shard bytes")
        require(
            sha256(compressed).hexdigest() == metadata["sha256"],
            "source shard digest",
        )
        shard = json.loads(gzip.decompress(compressed))
        require(canonical_gzip_json(shard) == compressed, "noncanonical source shard")
        require(shard["format"] == expected_format, "source internal format")
        require(shard["shard_index"] == index, "source internal index")
        require(shard["shard_count"] == SHARD_COUNT, "source internal count")
        require(shard["sector_start"] == sector_start, "source internal start")
        require(shard["sector_end"] == sector_end, "source internal end")
        result.extend(shard[field])
        require(len(result) == sector_end, "source shard gap")
    require(len(result) == SECTOR_COUNT, "source sector coverage")
    return result


def inversions(left, right):
    left_position = {token: index for index, token in enumerate(left)}
    right_position = {token: index for index, token in enumerate(right)}
    common = set(left_position) & set(right_position)
    result = set()
    for first in common:
        for second in common:
            if first >= second:
                continue
            left_sign = left_position[first] - left_position[second]
            right_sign = right_position[first] - right_position[second]
            if left_sign * right_sign < 0:
                result.add((first, second))
    return result


def collision_components(edges):
    adjacency = defaultdict(set)
    for left, right in edges:
        adjacency[left].add(right)
        adjacency[right].add(left)
    components = []
    seen = set()
    for token in sorted(adjacency):
        if token in seen:
            continue
        todo = [token]
        component = set()
        while todo:
            current = todo.pop()
            if current in component:
                continue
            component.add(current)
            seen.add(current)
            todo.extend(adjacency[current] - component)
        complete_edges = {
            (left, right)
            for left in component
            for right in component
            if left < right
        }
        require(complete_edges <= edges, "collision component is not complete")
        components.append(component)
    return components


def verify_inversion_owners(seen_owners, permitted_owners):
    require(
        not (seen_owners - permitted_owners),
        "inversion without its resultant",
    )


def verify_invisible_resultants(left, event_owners, inversion_owners):
    bounded_walls = {token[0] for token in left}
    for owners, multiplicity in (event_owners - inversion_owners).items():
        require(
            not multiplicity or not set(owners) <= bounded_walls,
            "invisible simple resultant has both owners in the bounded stack",
        )


def replay_partition(sectors, sector_ids, catalog, events, endpoint_factors):
    shard_sectors = [[] for _ in range(SHARD_COUNT)]
    completed_census = Counter()
    residual_census = Counter()
    raw_kind_census = Counter()
    completed_sections = completed_events = visible_inversions = groups = 0
    points = strips = maximum_events = 0
    for sector_id, (stack, identifiers) in enumerate(
        zip(sectors, sector_ids, strict=True)
    ):
        require(len(identifiers) == len(stack) + 1, "adjacent strip coverage")
        completed = []
        unresolved = []
        for root_index, root in enumerate(stack):
            factor_id = root[0]
            left = catalog[identifiers[root_index]]
            right = catalog[identifiers[root_index + 1]]
            current_events = events[factor_id]
            require(current_events, "section without a raw event")
            require(
                all(event[2] == 1 for event in current_events),
                "non-simple raw event",
            )
            maximum_events = max(maximum_events, len(current_events))
            kinds = Counter(event[0] for event in current_events)
            raw_kind_census.update(kinds)
            reason = 0
            if len(left) != len(right):
                reason |= COUNT_CHANGE
            if set(kinds) - {"resultant"}:
                reason |= COEFFICIENT
            if factor_id in endpoint_factors:
                reason |= ENDPOINT

            edges = inversions(left, right)
            current_groups = collision_components(edges)
            seen_owners = Counter(
                tuple(sorted((first[0], second[0])))
                for first, second in edges
            )
            permitted_owners = Counter(
                tuple(sorted(event[1]))
                for event in current_events
                if event[0] == "resultant"
            )
            verify_inversion_owners(seen_owners, permitted_owners)
            if reason:
                unresolved.append([root_index, factor_id, reason])
                residual_census[reason] += 1
                continue

            require(
                set(left) == set(right),
                "regular section changed its bounded branch tokens",
            )
            verify_invisible_resultants(
                left, permitted_owners, seen_owners
            )

            section_points = len(left) - sum(
                len(component) - 1 for component in current_groups
            )
            section_strips = section_points + 1
            completed.append(
                [
                    root_index,
                    factor_id,
                    len(current_events),
                    len(edges),
                    len(current_groups),
                    section_points,
                    section_strips,
                ]
            )
            completed_census[
                (len(current_events), len(edges), len(current_groups))
            ] += 1
            completed_sections += 1
            completed_events += len(current_events)
            visible_inversions += len(edges)
            groups += len(current_groups)
            points += section_points
            strips += section_strips

        shard_index = SHARD_COUNT * sector_id // SECTOR_COUNT
        shard_sectors[shard_index].append(
            {"completed": completed, "unresolved": unresolved}
        )

    require(
        completed_sections + sum(residual_census.values()) == SECTION_COUNT,
        "section partition",
    )
    partition = [row for shard in shard_sectors for row in shard]
    return {
        "shards": shard_sectors,
        "partition": partition,
        "partition_sha256": digest(partition),
        "completed_census": {
            ",".join(map(str, key)): value
            for key, value in sorted(completed_census.items())
        },
        "residual_census": {
            str(key): value for key, value in sorted(residual_census.items())
        },
        "raw_kind_census": dict(sorted(raw_kind_census.items())),
        "completed_sections": completed_sections,
        "unresolved_sections": SECTION_COUNT - completed_sections,
        "completed_events": completed_events,
        "visible_inversions": visible_inversions,
        "groups": groups,
        "points": points,
        "strips": strips,
        "maximum_events": maximum_events,
    }


def verify_result_shards(candidate, replay):
    manifest = candidate["artifact_shards"]
    require(manifest["format"] == SHARD_FORMAT, "result shard format")
    require(manifest["shard_count"] == SHARD_COUNT, "result shard count")
    require(len(manifest["shards"]) == SHARD_COUNT, "result shard rows")
    expected_manifest = []
    for index, sector_rows in enumerate(replay["shards"]):
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
        expected_bytes = canonical_gzip_json(shard)
        name = (
            "DIAG3_PAIR_GLOBAL_FOUR_SUPPORT_REGULAR_U_SECTION_V_LIFT_"
            f"SHARD_{index:02d}_OF_{SHARD_COUNT}.json.gz"
        )
        actual_bytes = (CERTIFICATE.parent / name).read_bytes()
        require(actual_bytes == expected_bytes, "result shard replay")
        expected_manifest.append(
            {
                "index": index,
                "path": name,
                "sector_start": sector_start,
                "sector_end": sector_end,
                "bytes": len(expected_bytes),
                "sha256": sha256(expected_bytes).hexdigest(),
            }
        )
    require(manifest["shards"] == expected_manifest, "result shard manifest")
    return expected_manifest


def validate_claims(candidate, observed):
    require(candidate["format"] == FORMAT, "wrong format")
    require(candidate["status"] == "PROVED", "wrong status")
    scope = candidate["scope"]
    require(
        scope["open_t_raw_resultant_regular_u_section_v_lift"] == "COMPLETE",
        "regular-section scope",
    )
    require(
        scope["remaining_open_t_algebraic_u_section_v_lift"]
        == "NOT_YET_CONSTRUCTED",
        "false residual claim",
    )
    require(
        scope["algebraic_t_section_v_lift"] == "NOT_YET_CONSTRUCTED",
        "false algebraic-t claim",
    )
    require(
        scope["global_gluing_and_closure_data"] == "NOT_CLAIMED",
        "false global claim",
    )
    require(scope["honest_9dvl_score"] == "2/9", "dishonest score")
    source = candidate["source"]
    for name in (
        "projection_semantic_sha256",
        "base_projection_semantic_sha256",
        "open_sector_lift_semantic_sha256",
        "open_cell_v_lift_semantic_sha256",
    ):
        require(source[name] == observed[name], f"bad source link: {name}")
    require(source["open_t_sectors"] == SECTOR_COUNT, "source sectors")
    require(source["algebraic_u_sections"] == SECTION_COUNT, "source sections")

    lift = candidate["regular_u_section_v_lift"]
    require(lift["completed_sections"] == observed["completed_sections"] == 120_174, "completed sections")
    require(lift["unresolved_sections"] == observed["unresolved_sections"] == 11_960, "unresolved sections")
    require(lift["completed_fraction"] == "60087/66067", "completion fraction")
    require(lift["all_raw_event_multiplicities_one"] is True, "raw multiplicity")
    require(lift["maximum_raw_events_on_one_section"] == observed["maximum_events"] == 10, "maximum events")
    require(lift["raw_event_kind_incidences"] == observed["raw_kind_census"], "raw event census")
    require(lift["completed_raw_resultant_events"] == observed["completed_events"] == 183_374, "completed events")
    require(lift["visible_inversion_edges"] == observed["visible_inversions"] == 169_750, "inversions")
    require(lift["interior_collision_groups"] == observed["groups"] == 148_896, "collision groups")
    require(lift["section_v_root_points"] == observed["points"] == 1_809_609, "root points")
    require(lift["section_open_v_strips"] == observed["strips"] == 1_929_783, "open strips")
    require(lift["lifted_cells"] == observed["points"] + observed["strips"] == 3_739_392, "lifted cells")
    require(lift["endpoint_base_factors"] == observed["endpoint_factor_count"] == 7, "endpoint factors")
    require(lift["completed_event_inversion_group_census"] == observed["completed_census"], "completion census")
    require(
        lift["residual_reason_bitmask"]
        == {
            "1": "adjacent interior-v root counts differ",
            "2": "a raw coefficient event is present",
            "4": "a v=0 or v=1 endpoint factor is present",
        },
        "reason vocabulary",
    )
    require(lift["residual_reason_census"] == observed["residual_census"], "residual census")
    require(lift["raw_event_map_sha256"] == observed["raw_event_map_sha256"], "event map digest")
    require(lift["partition_sha256"] == observed["partition_sha256"], "partition digest")
    require(candidate["artifact_shards"] == observed["artifact_shards"], "artifact manifest")
    dependency = candidate["generator_dependency"]
    require(
        set(dependency) == {"independent_verifier", "python"}
        and dependency["independent_verifier"]
        == "STANDARD_LIBRARY_STRUCTURAL_REPLAY"
        and dependency["python"].startswith("3.12."),
        "generator dependency marker",
    )
    require(candidate["semantic_sha256"] == observed["semantic_sha256"], "semantic digest")
    require(candidate["resource_effect"]["sections_examined"] == SECTION_COUNT, "resource count")
    require(
        candidate["resource_effect"]["algebraic_u_section_ceiling"]
        == SECTION_COUNT,
        "resource ceiling value",
    )
    require(candidate["resource_effect"]["ceiling_not_triggered"] is True, "resource ceiling")
    require(candidate["resource_effect"]["next_stage"] == NEXT_STAGE, "next stage")
    require(candidate["theorem_effect"] == THEOREM_EFFECT, "theorem effect")


def main():
    candidate = json.loads(CERTIFICATE.read_bytes())
    projection = json.loads(PROJECTION.read_bytes())
    base = json.loads(gzip.decompress(BASE.read_bytes()))
    roots = json.loads(gzip.decompress(ROOTS.read_bytes()))
    open_record = json.loads(OPEN.read_bytes())
    open_v = json.loads(OPEN_V.read_bytes())
    require(
        projection["status"]
        == base["status"]
        == roots["status"]
        == open_record["status"]
        == open_v["status"]
        == "PROVED",
        "source status",
    )
    require(
        base["source"]["semantic_sha256"] == projection["semantic_sha256"],
        "base-to-projection semantic link",
    )
    require(
        base["source"]["projection_catalog_sha256"]
        == projection["projection"]["catalog_sha256"],
        "base-to-projection catalog link",
    )
    require(
        roots["source"]["semantic_sha256"] == base["semantic_sha256"],
        "roots-to-base semantic link",
    )
    require(
        open_record["source"]["base_projection_semantic_sha256"]
        == base["semantic_sha256"]
        and open_record["source"]["root_isolation_semantic_sha256"]
        == roots["semantic_sha256"],
        "open-sector source chain",
    )
    require(
        open_v["source"]["projection_semantic_sha256"]
        == projection["semantic_sha256"]
        and open_v["source"]["base_projection_semantic_sha256"]
        == base["semantic_sha256"]
        and open_v["source"]["root_isolation_semantic_sha256"]
        == roots["semantic_sha256"]
        and open_v["source"]["open_sector_lift_semantic_sha256"]
        == open_record["semantic_sha256"],
        "open-v source chain",
    )
    open_v_verifier.replay_endpoint_factorizations(projection, base, open_v)
    require(
        digest(open_v["v_endpoint_audit"]["factorizations"])
        == open_v["v_endpoint_audit"]["factorizations_sha256"],
        "endpoint digest",
    )

    events, event_serial = independent_event_map(projection, base)
    endpoint_factors = {
        factor_id
        for row in open_v["v_endpoint_audit"]["factorizations"]
        for factor_id, _multiplicity in row["base_factors"]
    }
    sectors = read_source_shards(open_record, OPEN_SHARD_FORMAT, "sectors")
    sector_ids = read_source_shards(
        open_v, OPEN_V_SHARD_FORMAT, "strip_signature_ids"
    )
    catalog = [
        tuple(tuple(token) for token in sequence)
        for sequence in open_v["open_cell_v_lift"]["signature_catalog"]
    ]
    replay = replay_partition(sectors, sector_ids, catalog, events, endpoint_factors)
    artifact_manifest = verify_result_shards(candidate, replay)
    semantic_payload = {
        "projection_semantic_sha256": projection["semantic_sha256"],
        "base_projection_semantic_sha256": base["semantic_sha256"],
        "open_sector_lift_semantic_sha256": open_record["semantic_sha256"],
        "open_cell_v_lift_semantic_sha256": open_v["semantic_sha256"],
        "raw_event_map_sha256": digest(event_serial),
        "endpoint_factorizations_sha256": open_v["v_endpoint_audit"][
            "factorizations_sha256"
        ],
        "partition_sha256": replay["partition_sha256"],
        "completed_census": replay["completed_census"],
        "residual_census": replay["residual_census"],
    }
    observed = {
        **replay,
        "projection_semantic_sha256": projection["semantic_sha256"],
        "base_projection_semantic_sha256": base["semantic_sha256"],
        "open_sector_lift_semantic_sha256": open_record["semantic_sha256"],
        "open_cell_v_lift_semantic_sha256": open_v["semantic_sha256"],
        "endpoint_factor_count": len(endpoint_factors),
        "raw_event_map_sha256": digest(event_serial),
        "artifact_shards": {
            "format": SHARD_FORMAT,
            "shard_count": SHARD_COUNT,
            "shards": artifact_manifest,
        },
        "semantic_sha256": digest(semantic_payload),
    }
    validate_claims(candidate, observed)

    mutations = []
    for path, value in (
        (("scope", "remaining_open_t_algebraic_u_section_v_lift"), "COMPLETE"),
        (("scope", "algebraic_t_section_v_lift"), "COMPLETE"),
        (("scope", "global_gluing_and_closure_data"), "COMPLETE"),
        (("scope", "honest_9dvl_score"), "3/9"),
        (("regular_u_section_v_lift", "completed_sections"), 120_175),
        (("regular_u_section_v_lift", "unresolved_sections"), 11_959),
        (("regular_u_section_v_lift", "completed_raw_resultant_events"), 183_373),
        (("regular_u_section_v_lift", "visible_inversion_edges"), 169_749),
        (("regular_u_section_v_lift", "interior_collision_groups"), 148_895),
        (("regular_u_section_v_lift", "lifted_cells"), 3_739_391),
        (("regular_u_section_v_lift", "raw_event_map_sha256"), "0" * 64),
        (("regular_u_section_v_lift", "partition_sha256"), "0" * 64),
        (("semantic_sha256",), "0" * 64),
        (("resource_effect", "next_stage"), "promote diagonal three"),
        (("resource_effect", "algebraic_u_section_ceiling"), 132_133),
        (("generator_dependency", "independent_verifier"), "SHARED_PRODUCER"),
    ):
        hostile = deepcopy(candidate)
        target = hostile
        for key in path[:-1]:
            target = target[key]
        target[path[-1]] = value
        mutations.append(hostile)
    rejected = 0
    for hostile in mutations:
        try:
            validate_claims(hostile, observed)
        except AssertionError:
            rejected += 1
    require(rejected == len(mutations), "hostile claim mutation survived")

    corrupted_shard = deepcopy(replay["shards"][0])
    corrupted_shard[0]["completed"][0][-1] += 1
    require(
        canonical_gzip_json(
            {
                "format": SHARD_FORMAT,
                "shard_index": 0,
                "shard_count": SHARD_COUNT,
                "sector_start": 0,
                "sector_end": SECTOR_COUNT // SHARD_COUNT,
                "sectors": corrupted_shard,
            }
        )
        != (CERTIFICATE.parent / artifact_manifest[0]["path"]).read_bytes(),
        "hostile shard corruption survived",
    )
    rejected += 1

    try:
        verify_invisible_resultants(
            ((1, 0), (2, 0)),
            Counter({(1, 2): 1}),
            Counter(),
        )
    except AssertionError:
        rejected += 1
    else:
        raise AssertionError("hostile bounded invisible-resultant canary survived")

    try:
        collision_components({((1, 0), (2, 0)), ((2, 0), (3, 0))})
    except AssertionError:
        rejected += 1
    else:
        raise AssertionError("hostile non-clique collision canary survived")

    try:
        verify_inversion_owners(Counter({(1, 2): 1}), Counter())
    except AssertionError:
        rejected += 1
    else:
        raise AssertionError("hostile unowned-inversion canary survived")

    print("PASS exact raw coefficient/resultant/discriminant event reconstruction")
    print("PASS 44 v-endpoint factorizations and 7 endpoint base factors")
    print("PASS 132134/132134 algebraic-u sections partitioned fail-closed")
    print("PASS 120174 raw-resultant regular sections -> 3739392 lifted cells")
    print("PASS residual frontier: 11960 coefficient or endpoint/count-change sections")
    print(f"PASS {rejected}/{len(mutations) + 4} hostile mutations rejected")
    print(
        "SCOPE open-t algebraic-u regular fibers only; remaining fibers, "
        "algebraic-t lifts, global gluing, labels, middle rank, and diagonal "
        "three remain open; honest 9DVL 2/9"
    )


if __name__ == "__main__":
    main()
