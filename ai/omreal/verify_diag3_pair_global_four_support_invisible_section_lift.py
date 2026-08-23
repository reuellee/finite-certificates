#!/usr/bin/env python3
"""Standard-library replay of raw-simple constant-stack section lifts."""

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
CERTIFICATE = HERE / "data" / "DIAG3_PAIR_GLOBAL_FOUR_SUPPORT_INVISIBLE_SECTION_LIFT.json"
FORMAT = "diag3-pair-global-row2599-four-support-invisible-section-lift-v1"
KIND_CODE = {"coefficient": 0, "discriminant": 1, "resultant": 2}


def require(condition, message):
    if not condition:
        raise AssertionError(message)


def digest(value):
    return sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode("ascii")).hexdigest()


def validate_claims(candidate, observed):
    require(candidate["format"] == FORMAT and candidate["status"] == "PROVED", "format/status")
    scope = candidate["scope"]
    require(scope["raw_simple_constant_stack_algebraic_t_section_lifts"] == "COMPLETE", "false completed scope")
    require(scope["remaining_algebraic_t_section_lifts"] == "NOT_YET_CONSTRUCTED", "false remaining scope")
    require(scope["v_fiber_lift"] == "NOT_YET_CONSTRUCTED", "false v scope")
    require(scope["global_parent_cell_coverage"] == "NOT_CLAIMED", "false global scope")
    require(scope["honest_9dvl_score"] == "2/9", "dishonest score")
    for key in ("base_semantic", "root_semantic", "open_semantic", "simple_semantic"):
        source_key = {
            "base_semantic": "base_projection_semantic_sha256",
            "root_semantic": "root_isolation_semantic_sha256",
            "open_semantic": "open_sector_lift_semantic_sha256",
            "simple_semantic": "simple_section_lift_semantic_sha256",
        }[key]
        require(candidate["source"][source_key] == observed[key], f"source {key}")
    lift = candidate["invisible_section_lift"]
    require(lift["completed_constant_stack_sections"] == 363, "section count")
    require(lift["raw_event_kind_census"] == {"coefficient": 1, "discriminant": 6, "resultant": 356}, "kind census")
    require(lift["raw_event_multiplicity_one_sections"] == 363, "raw multiplicity")
    require(lift["u_boundary_event_sections"] == 0, "boundary event")
    require(lift["section_u_root_points"] == observed["root_points"], "root points")
    require(lift["section_u_strips"] == observed["strips"], "strips")
    require(lift["section_base_cells"] == observed["root_points"] + observed["strips"], "cells")
    require(lift["completed_sha256"] == observed["completed_digest"], "completed digest")
    require(candidate["remaining_frontier"] == {"remaining_algebraic_t_sections": 308, "census": {"complex_unchanged_stack": 43, "complex_same_count_transition": 251, "root_count_change": 14}}, "remaining frontier")
    require(candidate["semantic_sha256"] == observed["semantic"], "semantic")
    require(candidate["resource_effect"]["ceiling_not_triggered"] is True, "ceiling")


def main():
    base = json.loads(gzip.decompress(BASE.read_bytes()))
    roots = json.loads(gzip.decompress(ROOTS.read_bytes()))
    open_lift = json.loads(OPEN.read_bytes())
    simple = json.loads(SIMPLE.read_bytes())
    stored = json.loads(CERTIFICATE.read_bytes())
    base_catalog = [projection.parse_bivariate(row["polynomial"]) for row in base["base_factorization"]["catalog"]]
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
        factors = simple_replay.factorization_for(key, projection_index, factorizations)
        raw_reduced = simple_replay.strip_raw_boundary(raw)
        for factor_id in factors:
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
    completed = []
    kind_census = Counter()
    root_points = strips = unchanged_complex = 0
    for section_id, (section, left, right) in enumerate(
        zip(sections, sequences[:-1], sequences[1:], strict=True)
    ):
        if left != right:
            continue
        factor_id = section["factor_id"]
        events = incidence[factor_id]
        eligible = (
            len(events) == 1
            and events[0][2] == 1
            and not boundary[factor_id]
            and not (events[0][0] == "coefficient" and events[0][1][1] == 0)
        )
        if not eligible:
            unchanged_complex += 1
            continue
        kind, owner, _multiplicity = events[0]
        root_count = len(left)
        completed.append([section_id, factor_id, section["factor_root_index"], KIND_CODE[kind], owner[0], owner[1], root_count])
        kind_census[kind] += 1
        root_points += root_count
        strips += root_count + 1
    require(unchanged_complex == 43, "complex unchanged count")
    require(completed == stored["invisible_section_lift"]["completed"], "completed rows")
    require(dict(sorted(kind_census.items())) == stored["invisible_section_lift"]["raw_event_kind_census"], "kind census")
    observed = {
        "base_semantic": base["semantic_sha256"],
        "root_semantic": roots["semantic_sha256"],
        "open_semantic": open_lift["semantic_sha256"],
        "simple_semantic": simple["semantic_sha256"],
        "root_points": root_points,
        "strips": strips,
        "completed_digest": digest(completed),
        "semantic": digest({"open_sector_lift_semantic_sha256": open_lift["semantic_sha256"], "simple_section_lift_semantic_sha256": simple["semantic_sha256"], "completed": completed}),
    }
    validate_claims(stored, observed)
    mutations = (
        (("status",), "OPEN"),
        (("scope", "raw_simple_constant_stack_algebraic_t_section_lifts"), "PARTIAL"),
        (("scope", "remaining_algebraic_t_section_lifts"), "COMPLETE"),
        (("scope", "honest_9dvl_score"), "3/9"),
        (("invisible_section_lift", "completed_constant_stack_sections"), 362),
        (("invisible_section_lift", "raw_event_multiplicity_one_sections"), 362),
        (("invisible_section_lift", "u_boundary_event_sections"), 1),
        (("invisible_section_lift", "completed_sha256"), "0" * 64),
        (("remaining_frontier", "remaining_algebraic_t_sections"), 307),
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
    require(rejected == len(mutations), "hostile invisible-section mutation survived")
    print("PASS 363 unchanged stacks have one raw-simple nonboundary event")
    print("PASS event census: 356 resultants + 6 discriminants + 1 intermediate coefficient")
    print(f"PASS {root_points} root points + {strips} strips = {root_points + strips} constant-stack section cells")
    print("PASS remaining exact frontier: 43 complex unchanged + 251 complex + 14 count-changing = 308")
    print(f"PASS {rejected}/{len(mutations)} hostile mutations rejected")
    print("SCOPE raw-simple constant stacks only; 308 algebraic sections and global pair complex remain open; honest 9DVL 2/9")


if __name__ == "__main__":
    main()
