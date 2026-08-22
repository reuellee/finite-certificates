#!/usr/bin/env python3
"""Replay exact toolkit canaries and reject hostile semantic mutations."""

from __future__ import annotations

from copy import deepcopy
from fractions import Fraction
from pathlib import Path
import json

import build_exact_semialgebraic_toolkit_canaries as builder
import exact_semialgebraic as exact


CERTIFICATE = Path(__file__).resolve().parent / "data" / "EXACT_SEMIALGEBRAIC_TOOLKIT_CANARIES.json"


def parse_point(values):
    return tuple(Fraction(value) for value in values)


def parse_polynomial(rows):
    return {
        tuple(row["exponent"]): Fraction(row["coefficient"])
        for row in rows
    }


def validate(candidate, expected):
    assert candidate == expected
    assert candidate["arithmetic"] == "EXACT_RATIONAL"
    assert candidate["decision_policy"] == "FAIL_CLOSED"
    examples = candidate["examples"]
    assert examples["positive_quadratic_2d"]["classification"]["status"] == "EMPTY_BERNSTEIN"
    assert examples["crossing_line_2d"]["classification"]["status"] == "NONEMPTY_CORNER"
    assert examples["interior_circle_2d"]["classification"]["status"] == "NONEMPTY_CORNER"
    assert examples["interior_circle_2d"]["classification"]["depth"] > 0
    assert examples["noncompact_hyperboloid_3d"]["critical_exclusion"]["proved_empty"] is True
    assert examples["compact_sphere_3d_hostile"]["critical_exclusion"]["proved_empty"] is False
    assert candidate["scope"]["independent_certificate_replay"] == "STILL_REQUIRED"
    assert candidate["scope"]["global_topology_from_local_boxes"] == "NOT_CLAIMED"


def main():
    stored = json.loads(CERTIFICATE.read_text())
    expected = builder.build_record()
    validate(stored, expected)

    # Analytic checks do not trust the classifier for the existence witnesses.
    for name in (
        "crossing_line_2d",
        "interior_circle_2d",
        "noncompact_hyperboloid_3d",
        "compact_sphere_3d_hostile",
    ):
        example = stored["examples"][name]
        polynomial = parse_polynomial(example["polynomial"])
        assert exact.evaluate(polynomial, parse_point(example["analytic_witness"])) == 0

    # Exact affine-map and normalization contracts used by downstream producers.
    affine_source = {(1, 0): Fraction(2), (0, 1): Fraction(-3), (0, 0): Fraction(5)}
    pulled = exact.affine_pullback(
        affine_source,
        (Fraction(1), Fraction(2)),
        ((Fraction(2), Fraction(0)), (Fraction(0), Fraction(-1))),
    )
    assert pulled == {(0, 0): Fraction(1), (1, 0): Fraction(4), (0, 1): Fraction(3)}
    assert exact.canonical_integer(affine_source) == exact.canonical_integer(
        {index: Fraction(-7, 3) * value for index, value in affine_source.items()}
    )
    assert exact.exclude_system(({},), max_depth=1) == (False, 0, 1)

    mutations = []
    for path, value in (
        (("arithmetic",), "FLOAT64"),
        (("decision_policy",), "ASSUME_EMPTY_AT_BUDGET"),
        (("examples", "positive_quadratic_2d", "classification", "status"), "NONEMPTY_CORNER"),
        (("examples", "interior_circle_2d", "classification", "depth"), 0),
        (("examples", "noncompact_hyperboloid_3d", "critical_exclusion", "proved_empty"), False),
        (("examples", "compact_sphere_3d_hostile", "critical_exclusion", "proved_empty"), True),
        (("scope", "independent_certificate_replay"), "NOT_REQUIRED"),
        (("scope", "global_topology_from_local_boxes"), "PROVED"),
    ):
        mutation = deepcopy(stored)
        target = mutation
        for key in path[:-1]:
            target = target[key]
        target[path[-1]] = value
        mutations.append(mutation)
    rejected = 0
    for mutation in mutations:
        try:
            validate(mutation, expected)
        except AssertionError:
            rejected += 1
    assert rejected == len(mutations)

    print("PASS exact affine pullback, normalization, and tensor-Bernstein primitives")
    print("PASS 2D empty, crossing, and subdivision-required occurrence canaries")
    print("PASS 3D noncompact critical-system exclusion")
    print("PASS compact-sphere hostile canary remains unresolved")
    print(f"PASS {rejected}/{len(mutations)} hostile semantic mutations rejected")
    print("SCOPE producer toolkit only; independent certificate replay remains required")


if __name__ == "__main__":
    main()
