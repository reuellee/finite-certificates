#!/usr/bin/env python3
"""Exact information no-go for full-support source-skeleton coverage.

This is deliberately not a counterexample among the 26,740 accepted primitive
residual factors.  It proves that even complete restriction data on the exact
40-edge skeleton cannot, by itself, imply that every ambient wall component
meets that skeleton.  The countermodel multiplies an actual crossed primitive
factor by a positive-on-skeleton rational sphere factor.  Off the skeleton it
has one extra compact component wholly inside the strict parent cell.
"""

from __future__ import annotations

import argparse
from copy import deepcopy
from fractions import Fraction
from hashlib import sha256
from itertools import product
import json
from pathlib import Path
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[3]
HERE = ROOT / "ai" / "omreal"
DATA = HERE / "data"
OUTPUT = Path(__file__).with_name("DIAG3_PAIR_SKELETON_INCIDENCE_NO_GO.json")

BASE_REVISION = "ec362dba8a912bc4749c004641aee2da0a88dc05"
FORMAT = "diag3-pair-skeleton-incidence-information-no-go-v1"
PARENT = 2599
SOURCE_FACTOR = 137
CENTER_CHART = 9
BOX_HALF_WIDTH = Fraction(1, 4096)
SPHERE_RADIUS = Fraction(1, 8192)

COVER = DATA / "DIAG3_PAIR_FULLSUPPORT_SEGMENT_COVER.json"
SKELETON = DATA / "DIAG3_PAIR_FULLSUPPORT_LABELED_SKELETON_EDGE27_EDGE39.json"
COLLAR = DATA / "DIAG3_PAIR_FULLSUPPORT_COMPONENT_COLLAR.json"
LEDGER = DATA / "DIAG3_RESEARCH_DECISION_LEDGER.json"
EXPECTED_INPUT_DIGESTS = {
    "segment_cover": "19248dd148d1fd002931ed5f48197869dd42c68a513376e1a4d6941389bda307",
    "combined_two_edge_skeleton": "dcb707220df3e61b1a94eeedcf8e46b6602f30d405f4a92fc542c0f52f672806",
    "component_collar": "5930cc19019470fdfdf55d67523f6c4211ccf5b540f5c2bb5df36c64db75d7bd",
    "decision_ledger": "7922d769aa30a84c5d208dec92d2e78d5c7744cc6184ea1d42aaeadf947761b3",
}

sys.path.insert(0, str(HERE))
import DIAG2_PIVOT_LABELED_PAIR_ORBITS_VERIFY as labeled  # noqa: E402
import diag3_pair_parent_source_transition_core as transition  # noqa: E402
import verify_diag3_pair_fullsupport_safe_segment_walls as safe  # noqa: E402
import verify_diag3_pair_global_parent_face_gate as gate  # noqa: E402


def require(condition, message):
    if not condition:
        raise AssertionError(message)


def qtext(value):
    value = Fraction(value)
    return str(value.numerator) if value.denominator == 1 else f"{value.numerator}/{value.denominator}"


def file_sha256(path):
    state = sha256()
    with Path(path).open("rb") as source:
        for block in iter(lambda: source.read(1 << 20), b""):
            state.update(block)
    return state.hexdigest()


def revision_file_sha256(revision, path):
    """Hash the discovery input at its pinned revision, not descendant metadata."""
    relative = Path(path).relative_to(ROOT).as_posix()
    payload = subprocess.check_output(
        ["git", "show", f"{revision}:{relative}"],
        cwd=ROOT,
    )
    return sha256(payload).hexdigest()


def canonical_digest(value):
    return sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":")).encode("ascii")
    ).hexdigest()


def semantic_seal(record):
    payload = deepcopy(record)
    payload.pop("semantic_sha256", None)
    return canonical_digest(payload)


def multiply(values):
    answer = Fraction(1)
    for value in values:
        answer *= value
    return answer


def evaluate(polynomial, point):
    return sum(
        (
            Fraction(coefficient)
            * multiply(coordinate**exponent for coordinate, exponent in zip(point, monomial, strict=True))
            for monomial, coefficient in polynomial.items()
        ),
        Fraction(),
    )


def dot(left, right):
    return sum((a * b for a, b in zip(left, right, strict=True)), Fraction())


def closest_segment_distance_squared(center, left, right):
    direction = tuple(b - a for a, b in zip(left, right, strict=True))
    denominator = dot(direction, direction)
    require(denominator > 0, "collapsed source edge")
    parameter = dot(tuple(c - a for c, a in zip(center, left, strict=True)), direction) / denominator
    parameter = max(Fraction(), min(Fraction(1), parameter))
    closest = tuple(a + parameter * d for a, d in zip(left, direction, strict=True))
    delta = tuple(c - x for c, x in zip(center, closest, strict=True))
    return parameter, dot(delta, delta)


def signed_box_summary(polynomial, sign, center, half_width):
    rows = []
    for bits in product((-1, 1), repeat=9):
        point = tuple(
            coordinate + bit * half_width
            for coordinate, bit in zip(center, bits, strict=True)
        )
        rows.append((sign * evaluate(polynomial, point), bits))
    minimum, minimizing_bits = min(rows)
    require(minimum > 0, "box sign gate failed")
    return {
        "minimum_signed_vertex_value": qtext(minimum),
        "minimizing_vertex_signs": list(minimizing_bits),
        "vertex_count": len(rows),
    }


def base_revision_is_ancestor():
    """Keep the discovery base pinned while allowing later integration commits."""
    return subprocess.run(
        ["git", "merge-base", "--is-ancestor", BASE_REVISION, "HEAD"],
        cwd=ROOT,
        check=False,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    ).returncode == 0


def exact_sources():
    matrices, points, _packed, _states, _hamming, _multiplicity = transition.exact_inputs()
    require(matrices.shape == (178, 4, 8) and len(points) == 178, "point bank census")
    records = [
        json.loads(line)
        for line in gate.CATALOG.read_text(encoding="utf-8").splitlines()
        if line
    ]
    parents, parent_digest = gate.parent_polynomials(records[gate.PARENT])
    factor_types, _factor_terms, factors = labeled.factor_polynomials()
    require(len(factors) == 26_740 and len(parents) == 70, "polynomial census")
    return points, parents, parent_digest, factor_types, factors


def build_record():
    require(base_revision_is_ancestor(), "pinned base revision is not an ancestor")
    raw_inputs = {
        "segment_cover": file_sha256(COVER),
        "combined_two_edge_skeleton": file_sha256(SKELETON),
        "component_collar": file_sha256(COLLAR),
        "decision_ledger": revision_file_sha256(BASE_REVISION, LEDGER),
    }
    require(raw_inputs == EXPECTED_INPUT_DIGESTS, "pinned input digest moved")

    cover = json.loads(COVER.read_text(encoding="utf-8"))
    selected_indices = tuple(cover["source_bank"]["selected_edge_indices"])
    selected_pairs = tuple(map(tuple, cover["source_bank"]["selected_chart_pairs"]))
    require(len(selected_indices) == len(selected_pairs) == 40, "selected cover size")
    require(
        selected_pairs == tuple(safe.EDGES[index] for index in selected_indices),
        "selected edge identity",
    )

    points, parents, parent_digest, factor_types, factors = exact_sources()
    center = points[CENTER_CHART]
    source_factor = factors[SOURCE_FACTOR]
    require(max(sum(monomial) for monomial in source_factor) == 1, "source factor degree")
    require(len(source_factor) == 2, "source factor term count")
    center_factor_value = evaluate(source_factor, center)
    require(center_factor_value > 0, "source factor center sign")

    parent_minima = []
    for label, target, polynomial, _terms in parents:
        summary = signed_box_summary(polynomial, target, center, BOX_HALF_WIDTH)
        parent_minima.append({"parent_bracket": label, "target_sign": target, **summary})
    factor_box = signed_box_summary(source_factor, 1, center, BOX_HALF_WIDTH)

    distance_rows = []
    crossing_edges = []
    for edge_index, (left_chart, right_chart) in zip(selected_indices, selected_pairs, strict=True):
        parameter, distance_squared = closest_segment_distance_squared(
            center, points[left_chart], points[right_chart]
        )
        require(distance_squared > SPHERE_RADIUS**2, "sphere meets retained skeleton")
        left_value = evaluate(source_factor, points[left_chart])
        right_value = evaluate(source_factor, points[right_chart])
        if left_value * right_value < 0:
            crossing_edges.append(edge_index)
        distance_rows.append(
            {
                "edge_index": edge_index,
                "charts": [left_chart, right_chart],
                "closest_parameter": qtext(parameter),
                "distance_squared": qtext(distance_squared),
            }
        )
    closest_row = min(distance_rows, key=lambda row: Fraction(row["distance_squared"]))
    require(crossing_edges == [22, 60, 61, 83, 86, 98], "source factor crossing pattern")
    require(SPHERE_RADIUS < BOX_HALF_WIDTH, "sphere not contained in safe box")

    center_zero_parameter, center_zero_distance = closest_segment_distance_squared(
        points[0], points[selected_pairs[0][0]], points[selected_pairs[0][1]]
    )
    require(center_zero_distance == 0 and center_zero_parameter == 0, "null canary setup")
    require(Fraction(closest_row["distance_squared"]) < 1, "large-radius canary setup")

    parent_minima_payload = [
        [row["parent_bracket"], row["target_sign"], row["minimum_signed_vertex_value"], row["minimizing_vertex_signs"]]
        for row in parent_minima
    ]
    distance_payload = [
        [row["edge_index"], *row["charts"], row["closest_parameter"], row["distance_squared"]]
        for row in distance_rows
    ]
    record = {
        "format": FORMAT,
        "status": "EXACT_INFORMATION_NO_GO_FOR_SKELETON_ONLY_COMPONENT_INFERENCE",
        "base_revision": BASE_REVISION,
        "target_ledger_id": "diag3_pair_hc1",
        "inputs": {
            **raw_inputs,
            "parent_catalog": file_sha256(gate.CATALOG),
            "point_bank": file_sha256(transition.POINT_BANK),
            "factor_polynomial_source": file_sha256(HERE / "DIAG2_PIVOT_LABELED_PAIR_ORBITS_VERIFY.py"),
            "parent_polynomial_semantic_sha256": parent_digest,
        },
        "strict_parent_box": {
            "parent_index": PARENT,
            "center_chart": CENTER_CHART,
            "center": [qtext(value) for value in center],
            "half_width": qtext(BOX_HALF_WIDTH),
            "dimension": 9,
            "parent_bracket_count": len(parents),
            "vertices_checked_per_bracket": 512,
            "certificate": "Each target-signed parent bracket is multiaffine, so its values on the box lie in the convex hull of its 512 exact vertex values.",
            "minima_sha256": canonical_digest(parent_minima_payload),
            "global_minimum": min(
                (
                    {
                        "parent_bracket": row["parent_bracket"],
                        "target_sign": row["target_sign"],
                        "value": row["minimum_signed_vertex_value"],
                        "vertex_signs": row["minimizing_vertex_signs"],
                    }
                    for row in parent_minima
                ),
                key=lambda row: Fraction(row["value"]),
            ),
        },
        "actual_source_factor": {
            "factor_id": SOURCE_FACTOR,
            "orbit_type": list(factor_types[SOURCE_FACTOR]),
            "degree": 1,
            "term_count": 2,
            "center_value": qtext(center_factor_value),
            "positive_safe_box": factor_box,
            "retained_crossing_edges": crossing_edges,
        },
        "sphere_factor": {
            "definition": "q(x)=sum_{j=0}^8 (x_j-center_j)^2-(1/8192)^2",
            "radius": qtext(SPHERE_RADIUS),
            "zero_set": "S^8",
            "connected": True,
            "compact": True,
            "contained_in_strict_parent_box": True,
            "disjoint_from_actual_source_factor_zero_set": True,
            "meets_retained_skeleton": False,
            "meets_parent_boundary": False,
        },
        "skeleton_separation": {
            "retained_edges": len(distance_rows),
            "distance_rows_sha256": canonical_digest(distance_payload),
            "closest_edge": closest_row,
            "radius_squared": qtext(SPHERE_RADIUS**2),
            "all_edge_distances_strictly_greater_than_radius": True,
        },
        "countermodel": {
            "definition": "H(x)=F_137(x)*q(x)",
            "on_skeleton": "q>0, hence H and F_137 have exactly the same signs, zeros, root order, and root multiplicities on all 40 retained edges.",
            "off_skeleton": "Z(H) contains the compact connected sphere Z(q), which is disjoint from Z(F_137), the retained skeleton, and the parent boundary.",
            "logical_consequence": "Parent-safe factor incidence, or even complete exact restriction roadmaps on the finite skeleton, does not imply ambient component coverage.",
        },
        "scope": {
            "actual_primitive_residual_factor_counterexample": False,
            "actual_factor_component_coverage_decided": False,
            "global_parent_cell_coverage": False,
            "pair_branch_closed": False,
            "honest_9dvl_score": "2/9",
            "proved_nonconsequence": "No upgrade from skeleton-only data without an off-skeleton theorem tied to the pinned primitive polynomial family.",
        },
        "required_missing_hypothesis": {
            "alternatives": [
                "A source-specific theorem proving each actual residual wall component meets the skeleton or genuine parent boundary.",
                "A boundary-aware polar/critical-point roadmap meeting every component, with exact continuation to the skeleton or a tagged parent wall.",
                "A stronger source-specific connectedness/graph theorem for every actual primitive residual wall in the strict parent cell.",
            ],
            "recommended_next_experiment": "Run a global Bernstein pivot/monotonicity screen on the 10844 crossed factors, then build relative polar-anchor certificates only for the residue; do not compile the remaining 38 skeleton edges first.",
        },
        "canaries": {
            "positive": "center chart 9, box half-width 1/4096, sphere radius 1/8192 passes",
            "negative": "radius 1 is rejected because the exact closest retained-edge distance squared is less than 1",
            "null": "center chart 0 is rejected because it is a retained-edge endpoint and has distance zero",
            "hostile": [
                "changed pinned input digest",
                "claim that H is an accepted primitive residual factor",
                "claim of actual-factor component coverage",
                "claim of global parent-cell coverage",
                "pair-branch closure",
                "promotion to 3/9",
            ],
        },
    }
    record["semantic_sha256"] = semantic_seal(record)
    return record


def verify_record(record, expected=None):
    require(record.get("semantic_sha256") == semantic_seal(record), "semantic seal")
    if expected is None:
        expected = build_record()
    require(record == expected, "complete exact record equality")


def hostile_replay(record, expected):
    mutations = []
    for name, mutate in (
        ("input digest", lambda row: row["inputs"].__setitem__("segment_cover", "0" * 64)),
        ("actual primitive", lambda row: row["scope"].__setitem__("actual_primitive_residual_factor_counterexample", True)),
        ("actual coverage", lambda row: row["scope"].__setitem__("actual_factor_component_coverage_decided", True)),
        ("global coverage", lambda row: row["scope"].__setitem__("global_parent_cell_coverage", True)),
        ("pair closure", lambda row: row["scope"].__setitem__("pair_branch_closed", True)),
        ("score promotion", lambda row: row["scope"].__setitem__("honest_9dvl_score", "3/9")),
    ):
        candidate = deepcopy(record)
        mutate(candidate)
        candidate["semantic_sha256"] = semantic_seal(candidate)
        try:
            verify_record(candidate, expected)
        except AssertionError:
            mutations.append(name)
        else:
            raise AssertionError(f"hostile mutation accepted: {name}")
    require(len(mutations) == 6, "hostile mutation census")
    return mutations


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    arguments = parser.parse_args()
    expected = build_record()
    if arguments.write:
        OUTPUT.write_text(json.dumps(expected, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    record = json.loads(OUTPUT.read_text(encoding="utf-8"))
    verify_record(record, expected)
    rejected = hostile_replay(record, expected)
    print(
        "PASS exact skeleton-incidence information no-go: "
        f"parent_brackets=70 edges=40 source_factor={SOURCE_FACTOR} "
        f"sphere=S^8 hostile_rejected={len(rejected)} actual_claim=OPEN"
    )


if __name__ == "__main__":
    main()
