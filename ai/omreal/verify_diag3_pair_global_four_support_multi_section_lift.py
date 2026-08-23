#!/usr/bin/env python3
"""Standard-library replay of same-count multi-crossing section lifts."""

from __future__ import annotations

from collections import Counter, defaultdict
import gzip
from hashlib import sha256
import json
from pathlib import Path
import sys


HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import verify_diag3_pair_global_four_support_base_projection as projection  # noqa: E402
import verify_diag3_pair_global_four_support_simple_section_lift as simple_replay  # noqa: E402


BASE = HERE / "data" / "DIAG3_PAIR_GLOBAL_FOUR_SUPPORT_BASE_PROJECTION.json.gz"
ROOTS = HERE / "data" / "DIAG3_PAIR_GLOBAL_FOUR_SUPPORT_ROOT_ISOLATION.json.gz"
OPEN = HERE / "data" / "DIAG3_PAIR_GLOBAL_FOUR_SUPPORT_OPEN_SECTOR_LIFT.json"
SIMPLE = HERE / "data" / "DIAG3_PAIR_GLOBAL_FOUR_SUPPORT_SIMPLE_SECTION_LIFT.json"
INVISIBLE = HERE / "data" / "DIAG3_PAIR_GLOBAL_FOUR_SUPPORT_INVISIBLE_SECTION_LIFT.json"
CERTIFICATE = HERE / "data" / "DIAG3_PAIR_GLOBAL_FOUR_SUPPORT_MULTI_SECTION_LIFT.json"
FORMAT = "diag3-pair-global-row2599-four-support-multi-section-lift-v1"


def require(condition, message):
    if not condition:
        raise AssertionError(message)


def digest(value):
    return sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":")).encode("ascii")
    ).hexdigest()


def tokens(sequence):
    counts = Counter()
    answer = []
    for factor_id in sequence:
        answer.append((factor_id, counts[factor_id]))
        counts[factor_id] += 1
    return answer


def inversions(left, right):
    left_tokens = tokens(left)
    right_tokens = tokens(right)
    require(Counter(left_tokens) == Counter(right_tokens), "root occurrence census")
    positions = {token: index for index, token in enumerate(right_tokens)}
    edges = []
    for left_index in range(len(left_tokens)):
        for right_index in range(left_index + 1, len(left_tokens)):
            if positions[left_tokens[left_index]] > positions[left_tokens[right_index]]:
                edges.append((left_index, right_index))
    return left_tokens, edges


def components(vertex_count, edges):
    parent = list(range(vertex_count))

    def root(item):
        if parent[item] != item:
            parent[item] = root(parent[item])
        return parent[item]

    for left, right in edges:
        left, right = root(left), root(right)
        if left != right:
            parent[right] = left
    active = {item for edge in edges for item in edge}
    groups = defaultdict(set)
    for item in active:
        groups[root(item)].add(item)
    answer = sorted(tuple(sorted(group)) for group in groups.values())
    for group in answer:
        edge_count = sum(left in group and right in group for left, right in edges)
        require(edge_count == len(group) * (len(group) - 1) // 2, "nonclique collision group")
    return answer


def validate_claims(candidate, observed):
    require(candidate["format"] == FORMAT and candidate["status"] == "PROVED", "format/status")
    scope = candidate["scope"]
    require(scope["pure_resultant_same_count_multi_section_lifts"] == "COMPLETE", "completed scope")
    require(scope["remaining_algebraic_t_section_lifts"] == "NOT_YET_CONSTRUCTED", "remaining scope")
    require(scope["v_fiber_lift"] == "NOT_YET_CONSTRUCTED", "v scope")
    require(scope["global_parent_cell_coverage"] == "NOT_CLAIMED", "global scope")
    require(scope["honest_9dvl_score"] == "2/9", "dishonest score")
    source = candidate["source"]
    require(source["base_projection_semantic_sha256"] == observed["base_semantic"], "base source")
    require(source["root_isolation_semantic_sha256"] == observed["root_semantic"], "root source")
    require(source["open_sector_lift_semantic_sha256"] == observed["open_semantic"], "open source")
    require(source["simple_section_lift_semantic_sha256"] == observed["simple_semantic"], "simple source")
    require(source["invisible_section_lift_semantic_sha256"] == observed["invisible_semantic"], "invisible source")
    lift = candidate["multi_section_lift"]
    require(lift["completed_same_count_sections"] == 240, "section count")
    require(lift["raw_resultant_events"] == 1549, "event count")
    require(lift["visible_inversion_edges"] == 1390, "inversion count")
    require(lift["interior_collision_groups"] == 549, "group count")
    require(lift["all_raw_event_multiplicities_one"] is True, "raw multiplicity")
    require(lift["sections_with_coefficient_discriminant_or_boundary_event"] == 0, "exceptional event")
    require(lift["component_size_profile_census"] == observed["profiles"], "profile census")
    require(lift["section_u_root_points"] == observed["root_points"], "root points")
    require(lift["section_u_strips"] == observed["strips"], "strips")
    require(lift["section_base_cells"] == observed["root_points"] + observed["strips"], "cells")
    require(lift["completed_sha256"] == observed["completed_digest"], "completed digest")
    require(candidate["remaining_frontier"] == {"remaining_algebraic_t_sections": 68, "census": {"complex_unchanged_stack": 43, "complex_same_count_transition": 11, "root_count_change": 14}}, "remaining frontier")
    require(candidate["semantic_sha256"] == observed["semantic"], "semantic")
    require(candidate["resource_effect"]["ceiling_not_triggered"] is True, "ceiling")


def main():
    base = json.loads(gzip.decompress(BASE.read_bytes()))
    roots = json.loads(gzip.decompress(ROOTS.read_bytes()))
    open_lift = json.loads(OPEN.read_bytes())
    simple = json.loads(SIMPLE.read_bytes())
    invisible = json.loads(INVISIBLE.read_bytes())
    stored = json.loads(CERTIFICATE.read_bytes())

    base_catalog = [
        projection.parse_bivariate(row["polynomial"])
        for row in base["base_factorization"]["catalog"]
    ]
    coefficients = [projection.coefficients_in_u(polynomial) for polynomial in base_catalog]
    unique, _kinds, _pairs, zero = projection.reconstruct_projection(base_catalog)
    require(zero == 0, "zero resultant")
    projection_index = {key: index for index, key in enumerate(unique)}
    factorizations = base["second_projection"]["factorizations"]
    incidence = defaultdict(list)

    def append(kind, owner, raw):
        key = projection.strip_square_boundary_squarefree(raw)
        if key is None:
            return
        factor_ids = simple_replay.factorization_for(key, projection_index, factorizations)
        raw_reduced = simple_replay.strip_raw_boundary(raw)
        for factor_id in factor_ids:
            multiplicity = simple_replay.factor_multiplicity(
                raw_reduced,
                base["second_projection"]["catalog"][factor_id]["coefficients_low_to_high"],
            )
            incidence[factor_id].append((kind, owner, multiplicity))

    for base_id, rows in enumerate(coefficients):
        for degree_u, coefficient in enumerate(rows):
            append("coefficient", (base_id, degree_u), coefficient)
        if len(rows) >= 3:
            append("discriminant", (base_id, -1), projection.discriminant(rows))
    for left in range(len(coefficients)):
        for right in range(left + 1, len(coefficients)):
            append(
                "resultant",
                (left, right),
                projection.sylvester_resultant(coefficients[left], coefficients[right]),
            )

    boundary = defaultdict(list)
    for row in open_lift["bounded_u_boundary_audit"]["factorizations"]:
        for factor in row["factors"]:
            boundary[factor["id"]].append((row["base_factor_id"], factor["multiplicity"]))
    sequences = simple_replay.load_sequences(open_lift)
    sections = roots["root_isolation"]["sections"]
    already_complete = {
        row[0] for row in simple["simple_section_lift"]["crossings"]
    } | {
        row[0] for row in invisible["invisible_section_lift"]["completed"]
    }

    completed = []
    profiles = Counter()
    excluded = Counter()
    event_count = inversion_count = group_count = 0
    root_points = strips = 0
    for section_id, (section, left, right) in enumerate(
        zip(sections, sequences[:-1], sequences[1:], strict=True)
    ):
        if section_id in already_complete or left == right or len(left) != len(right):
            continue
        factor_id = section["factor_id"]
        events = incidence[factor_id]
        if boundary[factor_id]:
            excluded["boundary"] += 1
            continue
        if any(kind != "resultant" for kind, _owner, _multiplicity in events):
            excluded["nonresultant"] += 1
            continue
        if any(multiplicity != 1 for _kind, _owner, multiplicity in events):
            excluded["multiplicity"] += 1
            continue
        root_tokens, edges = inversions(left, right)
        event_owners = Counter(tuple(sorted(owner)) for _kind, owner, _multiplicity in events)
        visible_owners = Counter(
            tuple(sorted((root_tokens[left_index][0], root_tokens[right_index][0])))
            for left_index, right_index in edges
        )
        require(not (visible_owners - event_owners), "visible inversion without resultant")
        groups = components(len(root_tokens), edges)
        points = len(left) - sum(len(group) - 1 for group in groups)
        section_strips = points + 1
        profile = "+".join(map(str, sorted(map(len, groups))))
        profiles[profile] += 1
        event_count += len(events)
        inversion_count += len(edges)
        group_count += len(groups)
        root_points += points
        strips += section_strips
        completed.append(
            [
                section_id,
                factor_id,
                section["factor_root_index"],
                len(left),
                len(events),
                len(edges),
                points,
                section_strips,
                [list(group) for group in groups],
            ]
        )

    require(excluded == {"nonresultant": 7, "multiplicity": 4}, "excluded census")
    require(completed == stored["multi_section_lift"]["completed"], "completed rows")
    require((event_count, inversion_count, group_count) == (1549, 1390, 549), "event accounting")
    observed = {
        "base_semantic": base["semantic_sha256"],
        "root_semantic": roots["semantic_sha256"],
        "open_semantic": open_lift["semantic_sha256"],
        "simple_semantic": simple["semantic_sha256"],
        "invisible_semantic": invisible["semantic_sha256"],
        "profiles": dict(sorted(profiles.items())),
        "root_points": root_points,
        "strips": strips,
        "completed_digest": digest(completed),
        "semantic": digest({"invisible_section_lift_semantic_sha256": invisible["semantic_sha256"], "completed": completed}),
    }
    validate_claims(stored, observed)
    mutations = (
        (("status",), "OPEN"),
        (("scope", "pure_resultant_same_count_multi_section_lifts"), "PARTIAL"),
        (("scope", "remaining_algebraic_t_section_lifts"), "COMPLETE"),
        (("scope", "honest_9dvl_score"), "3/9"),
        (("multi_section_lift", "completed_same_count_sections"), 239),
        (("multi_section_lift", "raw_resultant_events"), 1548),
        (("multi_section_lift", "all_raw_event_multiplicities_one"), False),
        (("multi_section_lift", "sections_with_coefficient_discriminant_or_boundary_event"), 1),
        (("multi_section_lift", "completed_sha256"), "0" * 64),
        (("remaining_frontier", "remaining_algebraic_t_sections"), 67),
        (("semantic_sha256",), "0" * 64),
        (("resource_effect", "ceiling_not_triggered"), False),
    )
    rejected = 0
    for path, value in mutations:
        target = stored
        for key in path[:-1]:
            target = target[key]
        original = target[path[-1]]
        target[path[-1]] = value
        try:
            validate_claims(stored, observed)
        except AssertionError:
            rejected += 1
        finally:
            target[path[-1]] = original
    require(rejected == len(mutations), "hostile multi-section mutation survived")
    print("PASS 240 pure-resultant same-count algebraic sections")
    print("PASS 1549 raw-simple events -> 1390 visible inversions -> 549 collision cliques")
    print(f"PASS {root_points} root points + {strips} strips = {root_points + strips} multi-section cells")
    print("PASS remaining exact frontier: 43 complex unchanged + 11 exceptional same-count + 14 count-changing = 68")
    print(f"PASS {rejected}/{len(mutations)} hostile mutations rejected")
    print("SCOPE pure-resultant same-count fibers only; 68 algebraic sections and global pair complex remain open; honest 9DVL 2/9")


if __name__ == "__main__":
    main()
