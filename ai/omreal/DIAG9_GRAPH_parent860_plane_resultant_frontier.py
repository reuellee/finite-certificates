#!/usr/bin/env python3
"""Exact pair-resultant frontier for the parent-860 open plane triangle.

The depth-eight Bernstein cover proves that only its co-leaf factor pairs can
intersect.  This script computes the exact ``i``-resultant for every such pair
using closed formulas for affine/quadratic polynomials.  The output measures
the remaining one-dimensional projection workload without launching a full
CAD.  It is an exact stop/frontier certificate, not an atlas claim.
"""

from __future__ import annotations

import argparse
from collections import Counter
from fractions import Fraction
import hashlib
import json
from math import gcd, lcm
from pathlib import Path
import sys


HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import DIAG9_GRAPH_parent860_plane_bernstein_cover as cover  # noqa: E402
import DIAG9_GRAPH_verify_row2599_slice as sturm  # noqa: E402


DEPTH = 8
ARTIFACT = HERE / "data" / "DIAG9_GRAPH_parent860_plane_projection_frontier.json"
FORMAT = "diag9-parent860-plane-projection-frontier-v1"


def clean(polynomial):
    answer = list(polynomial)
    while answer and not answer[-1]:
        answer.pop()
    return tuple(answer)


def add(left, right, scale=1):
    return clean(
        tuple(
            (left[index] if index < len(left) else 0)
            + scale * (right[index] if index < len(right) else 0)
            for index in range(max(len(left), len(right)))
        )
    )


def multiply(left, right):
    if not left or not right:
        return ()
    answer = [0] * (len(left) + len(right) - 1)
    for i, first in enumerate(left):
        for j, second in enumerate(right):
            answer[i + j] += first * second
    return clean(answer)


def power(polynomial, exponent):
    answer = (1,)
    for _ in range(exponent):
        answer = multiply(answer, polynomial)
    return answer


def primitive(polynomial):
    polynomial = clean(polynomial)
    if not polynomial:
        return ()
    denominator = 1
    for value in polynomial:
        denominator = lcm(denominator, Fraction(value).denominator)
    integer = [int(Fraction(value) * denominator) for value in polynomial]
    divisor = 0
    for value in integer:
        divisor = gcd(divisor, abs(value))
    integer = [value // divisor for value in integer]
    if integer[-1] < 0:
        integer = [-value for value in integer]
    return tuple(integer)


def coefficients_in_i(polynomial):
    values = dict(polynomial)
    degree_i = max((monomial[1] for monomial in values), default=0)
    rows = []
    for i_degree in range(degree_i + 1):
        h_degree = max(
            (monomial[0] for monomial in values if monomial[1] == i_degree),
            default=-1,
        )
        rows.append(
            clean(
                tuple(values.get((degree, i_degree), 0) for degree in range(h_degree + 1))
            )
        )
    while rows and not rows[-1]:
        rows.pop()
    return tuple(rows)


def resultant(left, right):
    """Resultant in ``i``; coefficients are ascending polynomials in ``h``."""

    left = coefficients_in_i(left)
    right = coefficients_in_i(right)
    m = len(left) - 1
    n = len(right) - 1
    if m < 0 or n < 0:
        raise AssertionError("zero plane factor")
    if m == 0 and n == 0:
        return ()  # distinct vertical irreducible lines do not meet
    if m == 0:
        return primitive(power(left[0], n))
    if n == 0:
        return primitive(power(right[0], m))
    if m == 1 and n == 1:
        return primitive(add(multiply(left[1], right[0]), multiply(left[0], right[1]), -1))
    if m == 1 and n == 2:
        # b2*a0^2 - b1*a0*a1 + b0*a1^2
        answer = multiply(right[2], power(left[0], 2))
        answer = add(answer, multiply(right[1], multiply(left[0], left[1])), -1)
        answer = add(answer, multiply(right[0], power(left[1], 2)))
        return primitive(answer)
    if m == 2 and n == 1:
        # a2*b0^2 - a1*b0*b1 + a0*b1^2
        answer = multiply(left[2], power(right[0], 2))
        answer = add(answer, multiply(left[1], multiply(right[0], right[1])), -1)
        answer = add(answer, multiply(left[0], power(right[1], 2)))
        return primitive(answer)
    if m == 2 and n == 2:
        # Res(a*i^2+b*i+c, d*i^2+e*i+f)
        c, b, a = left
        f, e, d = right
        first = add(multiply(a, f), multiply(c, d), -1)
        second = add(multiply(a, e), multiply(b, d), -1)
        third = add(multiply(b, f), multiply(c, e), -1)
        return primitive(add(power(first, 2), multiply(second, third), -1))
    raise AssertionError(f"unexpected i-degrees {(m, n)}")


def divide_linear(polynomial, root):
    polynomial = tuple(map(Fraction, polynomial))
    quotient = [Fraction(0)] * (len(polynomial) - 1)
    quotient[-1] = polynomial[-1]
    for degree in range(len(quotient) - 1, 0, -1):
        quotient[degree - 1] = polynomial[degree] + root * quotient[degree]
    if polynomial[0] + root * quotient[0]:
        raise AssertionError("inexact endpoint linear division")
    return clean(quotient)


def strip_endpoint_roots(polynomial, endpoints):
    polynomial = tuple(map(Fraction, polynomial))
    multiplicity = [0, 0]
    for index, endpoint in enumerate(endpoints):
        while len(polynomial) > 1 and sturm.polynomial_value(polynomial, endpoint) == 0:
            polynomial = divide_linear(polynomial, endpoint)
            multiplicity[index] += 1
    return polynomial, tuple(multiplicity)


def digest_rows(rows):
    digest = hashlib.sha256()
    for row in rows:
        values = row if isinstance(row, (tuple, list)) else (row,)
        digest.update(",".join(map(str, values)).encode("ascii"))
        digest.update(b"\n")
    return digest.hexdigest()


def fraction_text(value):
    value = Fraction(value)
    return f"{value.numerator}/{value.denominator}"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--build", action="store_true")
    args = parser.parse_args()
    result = cover.build(DEPTH, progress=True, include_boundary=False)
    polynomials = result["active_polynomial"]
    unique = set()
    degree = Counter()
    constant = 0
    zero = 0
    max_bits = 0
    for index, (left, right) in enumerate(result["candidate_pairs"], 1):
        polynomial = resultant(polynomials[left], polynomials[right])
        if not polynomial:
            zero += 1
            continue
        if len(polynomial) == 1:
            constant += 1
            continue
        unique.add(polynomial)
        degree[len(polynomial) - 1] += 1
        max_bits = max(max_bits, *(abs(value).bit_length() for value in polynomial))
        if index % 50_000 == 0:
            print(f"resultants {index}/{len(result['candidate_pairs'])}", flush=True)

    unique_degree = Counter(len(polynomial) - 1 for polynomial in unique)
    census = result["projection_census"]
    parent_vertices = census["vertices"]
    horizontal = (min(point[0] for point in parent_vertices), max(point[0] for point in parent_vertices))
    root_bearing = Counter()
    root_bearing_polynomials = []
    root_count_census = Counter()
    total_roots = 0
    endpoint_multiplicity = Counter()
    for index, polynomial in enumerate(sorted(unique), 1):
        stripped, endpoint = strip_endpoint_roots(polynomial, horizontal)
        endpoint_multiplicity[endpoint] += 1
        roots = sturm.root_count(stripped, *horizontal) if len(stripped) > 1 else 0
        root_count_census[roots] += 1
        if roots:
            root_bearing[len(polynomial) - 1] += 1
            root_bearing_polynomials.append(polynomial)
            total_roots += roots
        if index % 50_000 == 0:
            print(f"Sturm {index}/{len(unique)}", flush=True)
    classification = []
    interior_set = set(census["interior_plane_factors"])
    boundary_set = set(census["boundary_only_factors"])
    active_set = set(census["active_plane_factors"])
    for factors in census["factor_to_plane"]:
        if not factors:
            classification.append("constant")
        elif factors[0] in interior_set:
            classification.append("interior")
        elif factors[0] in boundary_set:
            classification.append("boundary_only")
        elif factors[0] in active_set:
            raise AssertionError("closed-active factor classification gap")
        else:
            classification.append("excluded")
    global_pairs = tuple(
        (result["active_factor"][left], result["active_factor"][right])
        for left, right in result["candidate_pairs"]
    )
    payload = {
        "format": FORMAT,
        "status": "EXACT_PROJECTION_FRONTIER",
        "as_of": "2026-08-23",
        "scope": {
            "parent": 860,
            "plane_variables": ["h", "i"],
            "honest_9dvl_score": "2/9",
            "coverage_certified_atlas": False,
            "claim": "exact plane-factor, Bernstein-pair, and univariate resultant/root-count frontier only",
        },
        "parent_triangle": {
            "vertices": [[fraction_text(value) for value in point] for point in parent_vertices],
            "distinct_halfspaces": len(census["halfspaces"]),
        },
        "plane_projection": {
            "primitive_global_factors": len(census["factor_to_plane"]),
            "constant_restrictions": census["constant_restrictions"],
            "distinct_irreducible_restrictions": len(census["plane_sources"]),
            "degree_census": {str(key): value for key, value in sorted(census["degree_census"].items())},
            "closed_triangle_factors": len(census["active_plane_factors"]),
            "open_triangle_factors": len(census["interior_plane_factors"]),
            "boundary_only_factors": len(census["boundary_only_factors"]),
            "exact_constant_sign_exclusions": {str(key): value for key, value in sorted(census["excluded_sign"].items())},
            "classification_sha256": digest_rows(enumerate(classification)),
            "open_factor_ids_sha256": digest_rows((factor,) for factor in result["active_factor"]),
        },
        "bernstein_cover": {
            "depth": DEPTH,
            "total_leaves": 4**DEPTH,
            "occupied_leaves": len(result["leaf_factors"]),
            "factor_leaf_incidences": sum(result["factor_leaf_count"]),
            "factor_leaf_count_range": [min(result["factor_leaf_count"]), max(result["factor_leaf_count"])],
            "maximum_factors_in_leaf": max(map(len, result["leaf_factors"].values())),
            "all_curve_pairs": result["total_pairs"],
            "candidate_pairs": len(result["candidate_pairs"]),
            "excluded_pairs": result["total_pairs"] - len(result["candidate_pairs"]),
            "candidate_global_pairs_sha256": digest_rows(global_pairs),
        },
        "resultant_frontier": {
            "constant_pair_resultants": constant,
            "vertical_vertical_nonintersections": zero,
            "nonconstant_occurrences": sum(degree.values()),
            "occurrence_degree_census": {str(key): value for key, value in sorted(degree.items())},
            "distinct_primitive_resultants": len(unique),
            "distinct_degree_census": {str(key): value for key, value in sorted(unique_degree.items())},
            "maximum_coefficient_bits": max_bits,
            "distinct_resultants_sha256": digest_rows(sorted(unique)),
            "resultants_with_open_horizontal_roots": sum(root_bearing.values()),
            "root_bearing_degree_census": {str(key): value for key, value in sorted(root_bearing.items())},
            "open_root_count_census": {str(key): value for key, value in sorted(root_count_census.items())},
            "total_open_horizontal_roots_by_polynomial": total_roots,
            "root_bearing_resultants_sha256": digest_rows(root_bearing_polynomials),
            "endpoint_root_multiplicity_patterns": {str(key): value for key, value in sorted(endpoint_multiplicity.items())},
        },
        "decision": {
            "stop_rule_triggered": "projection-growth frontier",
            "next_target": "sharded exact isolation and common-i validation for the root-bearing resultant catalog",
            "forbidden_inference": "the projection census is not a chamber atlas and does not prove diagonal nine",
        },
    }
    payload["semantic_sha256"] = hashlib.sha256(
        json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()
    if args.build:
        ARTIFACT.parent.mkdir(parents=True, exist_ok=True)
        ARTIFACT.write_text(json.dumps(payload, sort_keys=True, separators=(",", ":")) + "\n")
        print("WROTE", ARTIFACT)
    else:
        stored = json.loads(ARTIFACT.read_text())
        if stored != payload:
            raise AssertionError("stored parent-860 projection frontier changed")

    print("PASS exact Bernstein candidate pairs:", len(result["candidate_pairs"]))
    print("PASS constant pair resultants:", constant)
    print("PASS vertical/vertical nonintersections:", zero)
    print("PASS nonconstant pair-resultant occurrences:", sum(degree.values()))
    print("PASS occurrence degree census:", dict(sorted(degree.items())))
    print("PASS distinct primitive pair resultants:", len(unique))
    print("PASS distinct degree census:", dict(sorted(unique_degree.items())))
    print("PASS maximum primitive coefficient bits:", max_bits)
    print("PASS resultants with open horizontal roots:", sum(root_bearing.values()))
    print("PASS root-bearing degree census:", dict(sorted(root_bearing.items())))
    print("PASS open-root-count census:", dict(sorted(root_count_census.items())))
    print("PASS total distinct open horizontal roots by polynomial:", total_roots)
    print("PASS endpoint-root multiplicity patterns:", {str(key): value for key, value in sorted(endpoint_multiplicity.items())})
    print("SEMANTIC SHA256:", payload["semantic_sha256"])
    print("SCOPE projection frontier only; common-i validation, root isolation and chamber atlas remain open")


if __name__ == "__main__":
    main()
