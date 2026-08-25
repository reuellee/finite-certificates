#!/usr/bin/env python3
"""Standard-library replay of regular residual algebraic-section lifts."""

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
MULTI = HERE / "data" / "DIAG3_PAIR_GLOBAL_FOUR_SUPPORT_MULTI_SECTION_LIFT.json"
CERTIFICATE = HERE / "data" / "DIAG3_PAIR_GLOBAL_FOUR_SUPPORT_REGULAR_RESIDUAL_SECTION_LIFT.json"
FORMAT = "diag3-pair-global-row2599-four-support-regular-residual-section-lift-v1"


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
        left_root, right_root = root(left), root(right)
        if left_root != right_root:
            parent[right_root] = left_root
    active = {item for edge in edges for item in edge}
    groups = defaultdict(set)
    for item in active:
        groups[root(item)].add(item)
    answer = sorted(tuple(sorted(group)) for group in groups.values())
    for group in answer:
        edge_count = sum(left in group and right in group for left, right in edges)
        require(
            edge_count == len(group) * (len(group) - 1) // 2,
            "nonclique collision group",
        )
    return answer


def validate_claims(candidate, observed):
    require(candidate["format"] == FORMAT and candidate["status"] == "PROVED", "format/status")
    scope = candidate["scope"]
    require(scope["regular_residual_algebraic_t_section_lifts"] == "COMPLETE", "completed scope")
    require(scope["remaining_algebraic_t_section_lifts"] == "NOT_YET_CONSTRUCTED", "remaining scope")
    require(scope["v_fiber_lift"] == "NOT_YET_CONSTRUCTED", "v scope")
    require(scope["global_parent_cell_coverage"] == "NOT_CLAIMED", "global scope")
    require(scope["honest_9dvl_score"] == "2/9", "dishonest score")
    source = candidate["source"]
    for key, value in observed["sources"].items():
        require(source[key] == value, f"{key} source")
    lift = candidate["regular_residual_section_lift"]
    require(lift["completed_sections"] == 40, "completed count")
    require(lift["completed_unchanged_sections"] == 36, "unchanged count")
    require(lift["completed_same_count_sections"] == 4, "same-count count")
    require(lift["raw_events"] == 197, "event count")
    require(lift["simple_resultant_events"] == 193, "resultant count")
    require(lift["harmless_nonleading_coefficient_events"] == 4, "coefficient count")
    require(lift["visible_inversion_edges"] == 30, "inversion count")
    require(lift["invisible_simple_resultant_events"] == 163, "invisible count")
    require(lift["interior_collision_groups"] == 12, "group count")
    require(lift["same_count_component_size_profile_census"] == observed["profiles"], "profiles")
    require(lift["section_u_root_points"] == 2285, "root points")
    require(lift["section_u_strips"] == 2325, "strips")
    require(lift["section_base_cells"] == 4610, "cells")
    require(lift["completed_sha256"] == observed["completed_digest"], "completed digest")
    require(lift["unchanged"] == observed["unchanged"], "unchanged rows")
    require(lift["same_count"] == observed["same_count"], "same-count rows")
    require(
        candidate["remaining_frontier"]
        == {
            "remaining_algebraic_t_sections": 28,
            "census": {
                "complex_same_count_transition": 7,
                "complex_unchanged_stack": 7,
                "root_count_change": 14,
            },
        },
        "remaining frontier",
    )
    require(candidate["semantic_sha256"] == observed["semantic"], "semantic")
    require(candidate["resource_effect"]["ceiling_not_triggered"] is True, "ceiling")


def main():
    base = json.loads(gzip.decompress(BASE.read_bytes()))
    roots = json.loads(gzip.decompress(ROOTS.read_bytes()))
    open_lift = json.loads(OPEN.read_bytes())
    simple = json.loads(SIMPLE.read_bytes())
    invisible = json.loads(INVISIBLE.read_bytes())
    multi = json.loads(MULTI.read_bytes())
    stored = json.loads(CERTIFICATE.read_bytes())

    base_catalog = [
        projection.parse_bivariate(row["polynomial"])
        for row in base["base_factorization"]["catalog"]
    ]
    coefficients = [projection.coefficients_in_u(polynomial) for polynomial in base_catalog]
    u_degrees = [len(rows) - 1 for rows in coefficients]
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
    } | {
        row[0] for row in multi["multi_section_lift"]["completed"]
    }

    unchanged = []
    same_count = []
    newly_complete = set()
    remaining = Counter()
    profiles = Counter()
    total_events = total_resultants = total_coefficients = 0
    total_inversions = total_groups = total_invisible = 0
    root_points = strips = 0
    for section_id, (section, left, right) in enumerate(
        zip(sections, sequences[:-1], sequences[1:], strict=True)
    ):
        if section_id in already_complete:
            continue
        factor_id = section["factor_id"]
        events = incidence[factor_id]
        no_boundary = not boundary[factor_id]
        all_simple_resultants = bool(events) and all(
            kind == "resultant" and multiplicity == 1
            for kind, _owner, multiplicity in events
        )
        if left == right and no_boundary and all_simple_resultants:
            points = len(left)
            section_strips = points + 1
            unchanged.append(
                [section_id, factor_id, section["factor_root_index"], len(left), len(events), points, section_strips]
            )
            newly_complete.add(section_id)
            total_events += len(events)
            total_resultants += len(events)
            total_invisible += len(events)
            root_points += points
            strips += section_strips
            continue

        if left != right and len(left) == len(right) and no_boundary:
            coefficient_events = [event for event in events if event[0] == "coefficient"]
            resultant_events = [event for event in events if event[0] == "resultant"]
            harmless_coefficients = bool(coefficient_events) and all(
                multiplicity == 1 and owner[1] < u_degrees[owner[0]]
                for _kind, owner, multiplicity in coefficient_events
            )
            regular_events = (
                len(events) == len(coefficient_events) + len(resultant_events)
                and all(multiplicity == 1 for _kind, _owner, multiplicity in resultant_events)
            )
            if harmless_coefficients and regular_events:
                root_tokens, edges = inversions(left, right)
                event_owners = Counter(tuple(sorted(owner)) for _kind, owner, _mult in resultant_events)
                visible_owners = Counter(
                    tuple(sorted((root_tokens[left_index][0], root_tokens[right_index][0])))
                    for left_index, right_index in edges
                )
                require(not (visible_owners - event_owners), "visible inversion without simple resultant")
                groups = components(len(root_tokens), edges)
                points = len(left) - sum(len(group) - 1 for group in groups)
                section_strips = points + 1
                invisible_count = len(resultant_events) - len(edges)
                profile = "+".join(map(str, sorted(map(len, groups))))
                profiles[profile] += 1
                same_count.append(
                    [
                        section_id,
                        factor_id,
                        section["factor_root_index"],
                        len(left),
                        len(coefficient_events),
                        len(resultant_events),
                        len(edges),
                        invisible_count,
                        points,
                        section_strips,
                        [list(group) for group in groups],
                    ]
                )
                newly_complete.add(section_id)
                total_events += len(events)
                total_resultants += len(resultant_events)
                total_coefficients += len(coefficient_events)
                total_inversions += len(edges)
                total_groups += len(groups)
                total_invisible += invisible_count
                root_points += points
                strips += section_strips

    for section_id, (left, right) in enumerate(zip(sequences[:-1], sequences[1:], strict=True)):
        if section_id in already_complete or section_id in newly_complete:
            continue
        if left == right:
            remaining["complex_unchanged_stack"] += 1
        elif len(left) == len(right):
            remaining["complex_same_count_transition"] += 1
        else:
            remaining["root_count_change"] += 1

    require((len(unchanged), len(same_count)) == (36, 4), "regular residual census")
    require(remaining == {"complex_unchanged_stack": 7, "complex_same_count_transition": 7, "root_count_change": 14}, "remaining census")
    require((total_events, total_resultants, total_coefficients) == (197, 193, 4), "event accounting")
    require((total_inversions, total_invisible, total_groups) == (30, 163, 12), "collision accounting")
    require((root_points, strips) == (2285, 2325), "cell accounting")
    observed = {
        "sources": {
            "base_projection_semantic_sha256": base["semantic_sha256"],
            "root_isolation_semantic_sha256": roots["semantic_sha256"],
            "open_sector_lift_semantic_sha256": open_lift["semantic_sha256"],
            "simple_section_lift_semantic_sha256": simple["semantic_sha256"],
            "invisible_section_lift_semantic_sha256": invisible["semantic_sha256"],
            "multi_section_lift_semantic_sha256": multi["semantic_sha256"],
        },
        "profiles": dict(sorted(profiles.items())),
        "unchanged": unchanged,
        "same_count": same_count,
        "completed_digest": digest({"unchanged": unchanged, "same_count": same_count}),
        "semantic": digest(
            {
                "multi_section_lift_semantic_sha256": multi["semantic_sha256"],
                "unchanged": unchanged,
                "same_count": same_count,
            }
        ),
    }
    validate_claims(stored, observed)
    mutations = (
        (("status",), "OPEN"),
        (("scope", "regular_residual_algebraic_t_section_lifts"), "PARTIAL"),
        (("scope", "remaining_algebraic_t_section_lifts"), "COMPLETE"),
        (("scope", "honest_9dvl_score"), "3/9"),
        (("regular_residual_section_lift", "completed_sections"), 39),
        (("regular_residual_section_lift", "simple_resultant_events"), 192),
        (("regular_residual_section_lift", "harmless_nonleading_coefficient_events"), 5),
        (("regular_residual_section_lift", "invisible_simple_resultant_events"), 162),
        (("regular_residual_section_lift", "section_base_cells"), 4609),
        (("regular_residual_section_lift", "completed_sha256"), "0" * 64),
        (("remaining_frontier", "remaining_algebraic_t_sections"), 27),
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
    require(rejected == len(mutations), "hostile regular-residual mutation survived")
    print("PASS 36 unchanged + 4 same-count = 40 regular residual sections")
    print("PASS 193 simple resultants + 4 harmless nonleading coefficients = 197 raw events")
    print("PASS 30 visible inversions + 163 invisible simple resultants; 12 collision cliques")
    print("PASS 2285 root points + 2325 strips = 4610 regular residual cells")
    print("PASS remaining exact frontier: 7 complex unchanged + 7 exceptional same-count + 14 count-changing = 28")
    print(f"PASS {rejected}/{len(mutations)} hostile mutations rejected")
    print("SCOPE regular residual fibers only; 28 algebraic sections and global pair complex remain open; honest 9DVL 2/9")


if __name__ == "__main__":
    main()
