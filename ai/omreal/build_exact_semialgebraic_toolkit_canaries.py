#!/usr/bin/env python3
"""Build exact positive and hostile canaries for the reusable toolkit."""

from __future__ import annotations

from fractions import Fraction
from pathlib import Path
import json

import exact_semialgebraic as exact


OUTPUT = Path(__file__).resolve().parent / "data" / "EXACT_SEMIALGEBRAIC_TOOLKIT_CANARIES.json"


def polynomial_text(polynomial):
    return [
        {"exponent": list(exponent), "coefficient": fraction_text(coefficient)}
        for exponent, coefficient in sorted(polynomial.items())
    ]


def fraction_text(value):
    value = Fraction(value)
    return str(value.numerator) if value.denominator == 1 else f"{value.numerator}/{value.denominator}"


def classify(polynomial, max_depth=8):
    status, depth, visited = exact.classify_zero_set(
        *exact.bernstein_control(polynomial), max_depth=max_depth
    )
    return {"status": status, "depth": depth, "visited": visited}


def classify_simplex(polynomial, vertices, max_depth=8):
    status, depth, visited = exact.classify_simplex_zero_set(
        polynomial, vertices, max_depth=max_depth
    )
    return {"status": status, "depth": depth, "visited": visited}


def critical(polynomial, axis_sets, max_depth=5):
    result = exact.adaptive_critical_exclusion(
        polynomial, axis_sets, max_depth=max_depth
    )
    return {
        "proved_empty": result["proved_empty"],
        "selected_axes": list(result["selected_axes"]) if result["selected_axes"] else None,
        "selected_depth": result["selected_depth"],
        "total_visited": result["total_visited"],
        "attempts": [
            {
                **attempt,
                "axes": list(attempt["axes"]),
            }
            for attempt in result["attempts"]
        ],
    }


def build_record():
    positive = {
        (0, 0): Fraction(1),
        (2, 0): Fraction(1),
        (0, 2): Fraction(1),
    }
    line = {
        (0, 0): Fraction(-1, 2),
        (1, 0): Fraction(1),
        (0, 1): Fraction(1),
    }
    circle = {
        (0, 0): Fraction(7, 16),
        (1, 0): Fraction(-1),
        (0, 1): Fraction(-1),
        (2, 0): Fraction(1),
        (0, 2): Fraction(1),
    }
    hyperboloid = {
        (0, 0, 0): Fraction(7, 16),
        (1, 0, 0): Fraction(-1),
        (0, 1, 0): Fraction(-1),
        (0, 0, 1): Fraction(-1, 2),
        (2, 0, 0): Fraction(1),
        (0, 2, 0): Fraction(1),
        (0, 0, 2): Fraction(-1),
    }
    sphere = {
        (0, 0, 0): Fraction(11, 16),
        (1, 0, 0): Fraction(-1),
        (0, 1, 0): Fraction(-1),
        (0, 0, 1): Fraction(-1),
        (2, 0, 0): Fraction(1),
        (0, 2, 0): Fraction(1),
        (0, 0, 2): Fraction(1),
    }
    axis_sets = ((0, 1), (0, 2), (1, 2))
    triangle = ((0, 0), (1, 0), (0, 1))
    tetrahedron = ((0, 0, 0), (1, 0, 0), (0, 1, 0), (0, 0, 1))
    simplex_crossing = {
        (0, 0): Fraction(-1, 3),
        (1, 0): Fraction(1),
        (0, 1): Fraction(1),
    }
    simplex_sphere = {
        (0, 0, 0): Fraction(11, 64),
        (1, 0, 0): Fraction(-1, 2),
        (0, 1, 0): Fraction(-1, 2),
        (0, 0, 1): Fraction(-1, 2),
        (2, 0, 0): Fraction(1),
        (0, 2, 0): Fraction(1),
        (0, 0, 2): Fraction(1),
    }
    return {
        "format": "exact-semialgebraic-toolkit-canaries-v2",
        "arithmetic": "EXACT_RATIONAL",
        "decision_policy": "FAIL_CLOSED",
        "examples": {
            "positive_quadratic_2d": {
                "polynomial": polynomial_text(positive),
                "classification": classify(positive),
                "analytic_fact": "p=1+x^2+y^2 is strictly positive",
            },
            "crossing_line_2d": {
                "polynomial": polynomial_text(line),
                "classification": classify(line),
                "analytic_witness": ["0", "1/2"],
            },
            "interior_circle_2d": {
                "polynomial": polynomial_text(circle),
                "classification": classify(circle),
                "analytic_witness": ["1/2", "1/4"],
            },
            "noncompact_hyperboloid_3d": {
                "polynomial": polynomial_text(hyperboloid),
                "classification": classify(hyperboloid),
                "analytic_witness": ["3/4", "1/2", "0"],
                "critical_exclusion": critical(hyperboloid, axis_sets),
                "analytic_fact": "dx=dy=0 forces x=y=1/2, where p=-(z+1/4)^2",
            },
            "compact_sphere_3d_hostile": {
                "polynomial": polynomial_text(sphere),
                "classification": classify(sphere),
                "analytic_witness": ["3/4", "1/2", "1/2"],
                "critical_exclusion": critical(sphere, axis_sets),
                "analytic_fact": "p=0 is the radius-1/4 sphere centered at (1/2,1/2,1/2)",
            },
            "positive_quadratic_simplex_2d": {
                "polynomial": polynomial_text(positive),
                "vertices": [list(vertex) for vertex in triangle],
                "classification": classify_simplex(positive, triangle),
                "analytic_fact": "p=1+x^2+y^2 is strictly positive on the triangle",
            },
            "crossing_line_simplex_2d": {
                "polynomial": polynomial_text(simplex_crossing),
                "vertices": [list(vertex) for vertex in triangle],
                "classification": classify_simplex(simplex_crossing, triangle),
                "analytic_witness": ["1/3", "0"],
            },
            "compact_sphere_simplex_3d_hostile": {
                "polynomial": polynomial_text(simplex_sphere),
                "vertices": [list(vertex) for vertex in tetrahedron],
                "classification": classify_simplex(simplex_sphere, tetrahedron, max_depth=5),
                "analytic_witness": ["3/8", "1/4", "1/4"],
                "analytic_fact": "the radius-1/8 sphere centered at (1/4,1/4,1/4) lies inside the tetrahedron",
            },
        },
        "scope": {
            "producer_library": "exact_semialgebraic/tensor_bernstein.py",
            "independent_certificate_replay": "STILL_REQUIRED",
            "global_topology_from_local_boxes": "NOT_CLAIMED",
            "simplex_subdivision": "DETERMINISTIC_LONGEST_EDGE_BISECTION",
        },
    }


def main():
    OUTPUT.write_text(json.dumps(build_record(), indent=2, sort_keys=True) + "\n")
    print("WROTE", OUTPUT)


if __name__ == "__main__":
    main()
