#!/usr/bin/env python3
"""Exact replay of the parent-860 mask-6 barycentric singular disk."""

from __future__ import annotations

import argparse
from collections import Counter, defaultdict
import copy
from fractions import Fraction
import hashlib
import json
from math import comb
import multiprocessing
import os
from pathlib import Path
import subprocess
import sys

import numpy as np
import sympy as sp


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
OMREAL = ROOT / "ai" / "omreal"
DATA = OMREAL / "data"
sys.path.insert(0, str(OMREAL))

import DIAG2_PIVOT_LABELED_PAIR_ORBITS_VERIFY as labeled  # noqa: E402
import DIAG2_PIVOT_REPRESENTATIVE_GRADIENT_VERIFY as representative  # noqa: E402
import DIAG9_GRAPH_parent860_star as star  # noqa: E402
import DIAG9_GRAPH_parent860_star_repair as repair  # noqa: E402
import DIAG9_GRAPH_verify_row2599_slice as sturm  # noqa: E402


CERTIFICATE = HERE / "DIAG8_MASK6_BARYCENTRIC_FAN_CERTIFICATE.json"
NONVACUITY = ROOT / "ops/team/diag8-mask6-nonvacuity/DIAG8_MASK6_NONVACUITY_CERTIFICATE.npz"
NONVACUITY_VERIFIER = ROOT / "ops/team/diag8-mask6-nonvacuity/verify_diag8_mask6_nonvacuity.py"
ALL_STRATA = OMREAL / "NINTH_DIAGONAL_SAFE_GRAPH.md"
CERTIFICATE_SHA256 = "b5ead7b0ed6ac6a5cb50ab715110e302772f49e43b2419cd54c98228937627cb"
STAR_SHA256 = "9274371ec45baee318cd160f931344f37dc5031acc13d63c16099534b8896f4b"
REPAIR_SHA256 = "f3ebf1f3a9b458663a12b042e68194aa24c4b55689cf85344e2d98f81aec3d11"
NONVACUITY_SHA256 = "ac86ed2966cf4646dd2241caee4d938aefb9ec70b27a91df8795ad992993c7c5"
ALL_STRATA_SHA256 = "8af233ced03055881572353d26d6f3a7d931649a9456fe7018cbc31202f4556e"
FACTOR_DIGEST = "71e01e0847e15f8bb21b50c6c3e2f69675bdd9ad9143d7b694aa8d6552cbcc06"
LOOP = (4, 11, 12, 14, 13, 23)
FAMILY = (
    34_895_220_708_312_748,
    34_850_557_309_758_184,
    34_850_557_307_726_570,
    34_850_557_039_028_936,
    34_850_539_394_645_193,
    34_850_144_722_168_960,
    34_754_553_013_114_532,
    34_206_807_699_455_377,
)
ACTIVE = (16_573, 19_721)
EXPECTED_FACTOR_SIGNS = {
    16_573: (0, 0, 1, 1, 0, 0),
    19_721: (1, 1, 1, 0, 0, 0),
}
EXPECTED_DERIVATIVES = {
    16_573: ((-1, -1), (-1, 1), (1, 1), (1, 1), (1, -1), (-1, -1)),
    19_721: ((1, 1), (1, 1), (1, -1), (-1, -1), (-1, -1), (-1, 1)),
}
EXPECTED_OUTER = ((), (16_573,), (), (19_721,), (16_573,), (19_721,))
EXPECTED_RADIAL = ((16_573,), (16_573,), (), (), (19_721,), (16_573, 19_721))
EXPECTED_VERTEX_SIGNS = ((-1, 1), (-1, 1), (1, 1), (1, 1), (1, -1), (-1, -1))
EXPECTED_ARCS = {
    16_573: ("outer_1", "radial_1", "radial_0", "radial_5", "outer_4"),
    19_721: ("outer_3", "radial_4", "radial_5", "outer_5"),
}

FACTOR_POLYNOMIALS = ()
TRIANGLES = ()


class Reject(AssertionError):
    """Fail-closed fan-certificate rejection."""


def require(condition, message):
    if not condition:
        raise Reject(message)


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def multiply(left, right):
    answer = [Fraction(0)] * (len(left) + len(right) - 1)
    for first, left_value in enumerate(left):
        for second, right_value in enumerate(right):
            answer[first + second] += left_value * right_value
    return answer


def multiply_bivariate(left, right):
    answer = defaultdict(Fraction)
    for (first_u, first_v), left_value in left.items():
        for (second_u, second_v), right_value in right.items():
            answer[first_u + second_u, first_v + second_v] += left_value * right_value
    return dict(answer)


def affine_power(intercept, slope, exponent):
    return [
        Fraction(comb(exponent, degree))
        * intercept ** (exponent - degree)
        * slope**degree
        for degree in range(exponent + 1)
    ]


def affine_triangle_power(constant, u_coefficient, v_coefficient, exponent):
    answer = {}
    for u_degree in range(exponent + 1):
        for v_degree in range(exponent - u_degree + 1):
            constant_degree = exponent - u_degree - v_degree
            multinomial = comb(exponent, u_degree) * comb(exponent - u_degree, v_degree)
            answer[u_degree, v_degree] = (
                Fraction(multinomial)
                * constant**constant_degree
                * u_coefficient**u_degree
                * v_coefficient**v_degree
            )
    return answer


def triangle_power(polynomial, triangle):
    origin, u_vertex, v_vertex = triangle
    answer = defaultdict(Fraction)
    for monomial, coefficient in polynomial.items():
        term = {(0, 0): Fraction(coefficient)}
        for variable, exponent in enumerate(monomial):
            if exponent:
                term = multiply_bivariate(
                    term,
                    affine_triangle_power(
                        origin[variable],
                        u_vertex[variable] - origin[variable],
                        v_vertex[variable] - origin[variable],
                        exponent,
                    ),
                )
        for key, value in term.items():
            answer[key] += value
    return {key: value for key, value in answer.items() if value}


def triangle_bernstein(power):
    degree = max(first + second for first, second in power)
    answer = []
    for u_index in range(degree + 1):
        for v_index in range(degree - u_index + 1):
            value = Fraction(0)
            for (u_degree, v_degree), coefficient in power.items():
                if u_degree <= u_index and v_degree <= v_index:
                    denominator = comb(degree, u_degree) * comb(degree - u_degree, v_degree)
                    value += coefficient * Fraction(
                        comb(u_index, u_degree) * comb(v_index, v_degree), denominator
                    )
            answer.append(value)
    return tuple(answer)


def bernstein_sign(power):
    coefficients = triangle_bernstein(power)
    if all(value > 0 for value in coefficients):
        return 1
    if all(value < 0 for value in coefficients):
        return -1
    return 0


def derivative(power, axis):
    answer = {}
    for (u_degree, v_degree), value in power.items():
        exponent = (u_degree, v_degree)[axis]
        if exponent:
            key = (u_degree - 1, v_degree) if axis == 0 else (u_degree, v_degree - 1)
            answer[key] = exponent * value
    return answer


def restrict_segment(polynomial, source, target):
    direction = tuple(right - left for left, right in zip(source, target))
    answer = [Fraction(0)]
    for monomial, coefficient in polynomial.items():
        term = [Fraction(1)]
        for variable, exponent in enumerate(monomial):
            if exponent:
                term = multiply(
                    term,
                    affine_power(source[variable], direction[variable], exponent),
                )
        term = [Fraction(coefficient) * value for value in term]
        if len(term) > len(answer):
            answer.extend([Fraction(0)] * (len(term) - len(answer)))
        for degree, value in enumerate(term):
            answer[degree] += value
    while answer and not answer[-1]:
        answer.pop()
    require(answer, "segment lies identically on a residual factor")
    return tuple(answer)


def factor_sign_task(index):
    return index, tuple(
        bernstein_sign(triangle_power(FACTOR_POLYNOMIALS[index], triangle))
        for triangle in TRIANGLES
    )


def load_geometry():
    require(sha256(star.ROADMAP) == STAR_SHA256, "coordinate-star bytes moved")
    require(sha256(repair.CERTIFICATE) == REPAIR_SHA256, "repair bytes moved")
    with np.load(star.ROADMAP, allow_pickle=False) as source:
        stored = {name: source[name] for name in source.files}
    points = list(repair.vertex_points(stored))
    with np.load(repair.CERTIFICATE, allow_pickle=False) as source:
        for numerators, denominators in zip(
            source["new_cell_coordinate_numerator"],
            source["new_cell_coordinate_denominator"],
        ):
            points.append(
                tuple(
                    Fraction(int(numerator), int(denominator))
                    for numerator, denominator in zip(numerators, denominators)
                )
            )
    center = tuple(
        sum(points[vertex][coordinate] for vertex in LOOP) / len(LOOP)
        for coordinate in range(9)
    )
    triangles = tuple(
        (center, points[left], points[right])
        for left, right in zip(LOOP, LOOP[1:] + LOOP[:1])
    )
    return tuple(points), center, triangles


def audit_all_factors(triangles, workers):
    global FACTOR_POLYNOMIALS, TRIANGLES
    _occurrences, _occurrence_factor, FACTOR_POLYNOMIALS = labeled.factor_polynomials()
    FACTOR_POLYNOMIALS = tuple(FACTOR_POLYNOMIALS)
    TRIANGLES = triangles
    pool = None
    if workers == 1:
        results = map(factor_sign_task, range(len(FACTOR_POLYNOMIALS)))
    else:
        pool = multiprocessing.get_context("fork").Pool(workers)
        results = pool.imap(factor_sign_task, range(len(FACTOR_POLYNOMIALS)), chunksize=20)
    census = Counter()
    active = {}
    digest = hashlib.sha256(b"diag8-mask6-fan-factor-signs-v1\0")
    try:
        for index, signs in results:
            digest.update(index.to_bytes(2, "little"))
            digest.update(bytes(value + 1 for value in signs))
            census[signs] += 1
            if 0 in signs:
                active[index] = signs
    finally:
        if pool is not None:
            pool.close()
            pool.join()
    require(len(FACTOR_POLYNOMIALS) == 26_740, "factor count")
    require(
        census
        == Counter(
            {
                (-1,) * 6: 13_712,
                (1,) * 6: 13_026,
                EXPECTED_FACTOR_SIGNS[16_573]: 1,
                EXPECTED_FACTOR_SIGNS[19_721]: 1,
            }
        ),
        "factor sign census",
    )
    require(active == EXPECTED_FACTOR_SIGNS, "active factor set")
    require(digest.hexdigest() == FACTOR_DIGEST, "factor semantic digest")
    return census, active


def audit_parent(triangles):
    _residual, brackets = representative.polynomial_data()
    require(len(brackets) == 70, "parent bracket count")
    for triangle in triangles:
        census = Counter(
            bernstein_sign(triangle_power(polynomial, triangle))
            for polynomial in brackets.values()
        )
        require(census == Counter({-1: 37, 1: 33}), "parent fan safety")


def audit_derivatives(triangles):
    observed = {}
    for factor in ACTIVE:
        observed[factor] = tuple(
            (
                bernstein_sign(derivative(triangle_power(FACTOR_POLYNOMIALS[factor], triangle), 0)),
                bernstein_sign(derivative(triangle_power(FACTOR_POLYNOMIALS[factor], triangle), 1)),
            )
            for triangle in triangles
        )
    require(observed == EXPECTED_DERIVATIVES, "active-wall monotonicity")
    return observed


def root_profile(source, target):
    answer = []
    for factor in ACTIVE:
        polynomial = restrict_segment(FACTOR_POLYNOMIALS[factor], source, target)
        count = sturm.root_count(polynomial, Fraction(0), Fraction(1))
        require(count in (0, 1), "multiple active roots on fan edge")
        if count:
            answer.append(factor)
    return tuple(answer)


def audit_boundary(points, center):
    outer = tuple(
        root_profile(points[left], points[right])
        for left, right in zip(LOOP, LOOP[1:] + LOOP[:1])
    )
    radial = tuple(root_profile(center, points[vertex]) for vertex in LOOP)
    require(outer == EXPECTED_OUTER, "outer root profile")
    require(radial == EXPECTED_RADIAL, "radial root profile")
    vertex_signs = tuple(
        tuple(
            1 if star.evaluate(FACTOR_POLYNOMIALS[factor], points[vertex]) > 0 else -1
            for factor in ACTIVE
        )
        for vertex in LOOP
    )
    require(vertex_signs == EXPECTED_VERTEX_SIGNS, "loop sector profile")
    return outer, radial, vertex_signs


def sympy_expression(power, u, v):
    return sum(
        sp.Rational(value.numerator, value.denominator) * u**u_degree * v**v_degree
        for (u_degree, v_degree), value in power.items()
    )


def sympy_univariate(poly, variable):
    return tuple(
        Fraction(int(value.p), int(value.q))
        for value in reversed(sp.Poly(poly, variable).all_coeffs())
    )


def isolate_unique_root(polynomial):
    require(sturm.root_count(polynomial, Fraction(0), Fraction(1)) == 1, "resultant root count")
    lower, upper = Fraction(0), Fraction(1)
    for _ in range(40):
        middle = (lower + upper) / 2
        left_count = sturm.root_count(polynomial, lower, middle)
        require(left_count in (0, 1), "resultant bisection")
        if left_count:
            upper = middle
        else:
            lower = middle
    return lower, upper


def interval_multiply(left, right):
    products = (
        left[0] * right[0], left[0] * right[1], left[1] * right[0], left[1] * right[1]
    )
    return min(products), max(products)


def interval_polynomial(polynomial, box, variable):
    coefficients = sympy_univariate(polynomial, variable)
    answer = (coefficients[-1], coefficients[-1])
    for coefficient in reversed(coefficients[:-1]):
        answer = interval_multiply(answer, box)
        answer = answer[0] + coefficient, answer[1] + coefficient
    return answer


def interval_divide(numerator, denominator):
    require(not (denominator[0] <= 0 <= denominator[1]), "interval division by zero")
    quotients = (
        numerator[0] / denominator[0], numerator[0] / denominator[1],
        numerator[1] / denominator[0], numerator[1] / denominator[1],
    )
    return min(quotients), max(quotients)


def audit_nodes(triangles):
    u, v = sp.symbols("u v")
    summaries = []
    for triangle_index in (4, 5):
        first = sympy_expression(
            triangle_power(FACTOR_POLYNOMIALS[16_573], triangles[triangle_index]), u, v
        )
        second = sympy_expression(
            triangle_power(FACTOR_POLYNOMIALS[19_721], triangles[triangle_index]), u, v
        )
        resultant = sp.resultant(first, second, v)
        resultant_poly = sympy_univariate(resultant, u)
        require(len(resultant_poly) == 5, "resultant degree")
        u_box = isolate_unique_root(resultant_poly)
        subresultants = sp.subresultants(first, second, v)
        linear = sp.Poly(subresultants[-2], v)
        require(linear.degree() == 1, "linear subresultant")
        coefficient_box = interval_polynomial(linear.coeff_monomial(v), u_box, u)
        constant_box = interval_polynomial(linear.coeff_monomial(1), u_box, u)
        v_box = interval_divide((-constant_box[1], -constant_box[0]), coefficient_box)
        if triangle_index == 4:
            require(Fraction(0) < v_box[0] <= v_box[1], "node v lower")
            require(u_box[1] + v_box[1] < 1, "node outside triangle")
            summaries.append((4, 1, "INTERIOR"))
        else:
            require(v_box[1] < 0, "triangle-5 resultant root not excluded")
            summaries.append((5, 0, "V_NEGATIVE"))
    return tuple(summaries)


def audit_arrangement(outer, radial, vertex_signs, nodes):
    arcs = {}
    for factor in ACTIVE:
        adjacency = defaultdict(set)
        active_triangles = 0
        for triangle in range(6):
            incident = []
            if factor in outer[triangle]:
                incident.append(f"outer_{triangle}")
            if factor in radial[triangle]:
                incident.append(f"radial_{triangle}")
            if factor in radial[(triangle + 1) % 6]:
                incident.append(f"radial_{(triangle + 1) % 6}")
            if EXPECTED_FACTOR_SIGNS[factor][triangle] == 0:
                require(len(incident) == 2, "active triangle is not one regular arc")
                adjacency[incident[0]].add(incident[1])
                adjacency[incident[1]].add(incident[0])
                active_triangles += 1
            else:
                require(not incident, "sign-definite triangle has a wall root")
        outer_nodes = sorted(node for node in adjacency if node.startswith("outer_"))
        require(len(outer_nodes) == 2, "active wall is not boundary-to-boundary")
        require(all(len(adjacency[node]) == 1 for node in outer_nodes), "outer degree")
        require(
            all(
                len(neighbors) == 2
                for node, neighbors in adjacency.items()
                if node.startswith("radial_")
            ),
            "radial wall incidence",
        )
        start = EXPECTED_ARCS[factor][0]
        path = [start]
        previous = None
        current = start
        while True:
            choices = adjacency[current] - ({previous} if previous is not None else set())
            if not choices:
                break
            require(len(choices) == 1, "wall branch in incidence graph")
            following = next(iter(choices))
            path.append(following)
            previous, current = current, following
        require(current in outer_nodes and current != start, "arc endpoint")
        require(len(path) - 1 == active_triangles, "arc omitted a triangle")
        require(len(set(path)) == len(path), "arc incidence cycle")
        arcs[factor] = tuple(path)
    require(arcs == EXPECTED_ARCS, "global active-wall arcs")
    endpoint_order = tuple(
        factor
        for _index, factor in sorted(
            (int(node.split("_")[1]), factor)
            for factor, arc in arcs.items()
            for node in (arc[0], arc[-1])
        )
    )
    require(endpoint_order == (16_573, 19_721, 16_573, 19_721), "arc endpoints do not alternate")
    interior_nodes = sum(count for _triangle, count, kind in nodes if kind == "INTERIOR")
    require(interior_nodes == 1, "interior node census")
    sector_count = 1 + 1 + (interior_nodes + 1)
    require(sector_count == 4, "sector Euler count")
    require(
        set(vertex_signs) == {(-1, -1), (-1, 1), (1, -1), (1, 1)},
        "not every sector meets the loop",
    )
    return arcs, sector_count


def oriented_edge(left, right):
    return ((left, right), 1) if left < right else ((right, left), -1)


def audit_chain():
    center = -1
    boundary = Counter()
    for left, right in zip(LOOP, LOOP[1:] + LOOP[:1]):
        for source, target, coefficient in (
            (left, right, 1), (center, right, -1), (center, left, 1)
        ):
            edge, orientation = oriented_edge(source, target)
            boundary[edge] += coefficient * orientation
    boundary = Counter({edge: value for edge, value in boundary.items() if value})
    expected = Counter()
    for left, right in zip(LOOP, LOOP[1:] + LOOP[:1]):
        edge, orientation = oriented_edge(left, right)
        expected[edge] += orientation
    expected = Counter({edge: value for edge, value in expected.items() if value})
    require(boundary == expected, "singular fan boundary")
    require(all(center not in edge for edge in boundary), "radial edge did not cancel")
    return tuple(zip(LOOP, LOOP[1:] + LOOP[:1]))


def validate_certificate(certificate, observed):
    require(certificate["format"] == "diag8-mask6-barycentric-fan-v2", "format")
    require(certificate["parent_index"] == 860, "parent")
    require(tuple(certificate["loop_vertices"]) == LOOP, "loop")
    require(tuple(certificate["family"]) == FAMILY, "family")
    require(certificate["nonvacuity_certificate_sha256"] == NONVACUITY_SHA256, "nonvacuity pointer")
    require(
        certificate["parent_brackets"]
        == {"count": 70, "triangle_sign_census": {"negative": 37, "positive": 33}, "unresolved": 0},
        "parent summary",
    )
    residual = certificate["residual_factors"]
    require(
        (residual["count"], residual["uniform_negative"], residual["uniform_positive"])
        == (26_740, 13_712, 13_026),
        "factor summary",
    )
    require(residual["semantic_sha256"] == FACTOR_DIGEST, "factor digest summary")
    require(
        {int(key): tuple(value) for key, value in residual["active"].items()}
        == EXPECTED_FACTOR_SIGNS,
        "active summary",
    )
    require(
        {int(key): tuple(map(tuple, value)) for key, value in certificate["active_derivative_signs"].items()}
        == EXPECTED_DERIVATIVES,
        "derivative summary",
    )
    require(tuple(map(tuple, certificate["boundary_profiles"]["outer"])) == EXPECTED_OUTER, "outer summary")
    require(tuple(map(tuple, certificate["boundary_profiles"]["radial"])) == EXPECTED_RADIAL, "radial summary")
    require(tuple(map(tuple, certificate["loop_vertex_active_signs"])) == EXPECTED_VERTEX_SIGNS, "vertex summary")
    require(
        certificate["arrangement"]
        == {
            "factor_16573_arc": list(observed["arcs"][16_573]),
            "factor_19721_arc": list(observed["arcs"][19_721]),
            "interior_nodes": [{"triangle": 4, "factors": [16_573, 19_721], "count": 1}],
            "triangle_5_resultant_root": "outside_standard_triangle_v_negative",
            "sector_count": observed["sector_count"],
            "every_sector_meets_loop": True,
        },
        "arrangement summary",
    )
    require(observed["nodes"] == ((4, 1, "INTERIOR"), (5, 0, "V_NEGATIVE")), "node replay")
    chain = certificate["chain"]
    require(chain["triangle_count"] == 6 and chain["radial_edges_cancel"] is True, "chain summary")
    require(tuple(map(tuple, chain["boundary"])) == observed["chain"], "chain boundary summary")
    require(certificate["result"] == "MASK6_LOOP_BOUNDS_EXACT_SINGULAR_DISK_FOR_CERTIFIED_EIGHT_FAMILY", "result")
    require(certificate["theorem_delta"] == "none", "theorem delta")


def hostile_canaries(certificate, observed):
    mutations = []
    candidate = copy.deepcopy(certificate)
    candidate["residual_factors"]["active"]["16573"][0] = 1
    mutations.append(("active_factor", candidate))
    candidate = copy.deepcopy(certificate)
    candidate["parent_brackets"]["unresolved"] = 1
    mutations.append(("parent", candidate))
    candidate = copy.deepcopy(certificate)
    candidate["boundary_profiles"]["radial"][5] = [16_573]
    mutations.append(("wall_incidence", candidate))
    candidate = copy.deepcopy(certificate)
    candidate["arrangement"]["interior_nodes"] = []
    mutations.append(("node", candidate))
    candidate = copy.deepcopy(certificate)
    candidate["arrangement"]["factor_16573_arc"][2] = "radial_2"
    mutations.append(("arc", candidate))
    candidate = copy.deepcopy(certificate)
    candidate["chain"]["boundary"][0] = [4, 12]
    mutations.append(("boundary", candidate))
    candidate = copy.deepcopy(certificate)
    candidate["family"][0] ^= 1
    mutations.append(("family", candidate))
    candidate = copy.deepcopy(certificate)
    candidate["theorem_delta"] = "diagonal_8_proved"
    mutations.append(("promotion", candidate))
    rejected = []
    for name, candidate in mutations:
        try:
            validate_certificate(candidate, observed)
        except (KeyError, Reject, TypeError):
            rejected.append(name)
        else:
            raise Reject(f"hostile canary accepted: {name}")
    return tuple(rejected)


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--workers", type=int, default=min(4, os.cpu_count() or 1))
    return parser.parse_args()


def main():
    args = parse_args()
    require(1 <= args.workers <= 8, "worker count")
    require(sha256(CERTIFICATE) == CERTIFICATE_SHA256, "fan certificate bytes moved")
    require(sha256(NONVACUITY) == NONVACUITY_SHA256, "nonvacuity bytes moved")
    require(sha256(ALL_STRATA) == ALL_STRATA_SHA256, "all-strata theorem source moved")
    theorem = ALL_STRATA.read_text(encoding="utf-8")
    require("**All-strata gluing theorem.**" in theorem, "all-strata theorem missing")
    replay = subprocess.run(
        [sys.executable, str(NONVACUITY_VERIFIER)],
        cwd=ROOT,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
        env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"},
    )
    require(replay.returncode == 0, "nonvacuity replay")
    points, center, triangles = load_geometry()
    audit_parent(triangles)
    census, active = audit_all_factors(triangles, args.workers)
    derivatives = audit_derivatives(triangles)
    outer, radial, vertex_signs = audit_boundary(points, center)
    nodes = audit_nodes(triangles)
    arcs, sector_count = audit_arrangement(outer, radial, vertex_signs, nodes)
    chain = audit_chain()
    observed = {
        "census": census, "active": active, "derivatives": derivatives,
        "outer": outer, "radial": radial, "vertex_signs": vertex_signs,
        "nodes": nodes, "arcs": arcs, "sector_count": sector_count, "chain": chain,
    }
    certificate = json.loads(CERTIFICATE.read_text(encoding="utf-8"))
    validate_certificate(certificate, observed)
    rejected = hostile_canaries(certificate, observed)
    print("PASS exact parent-860 mask-6 barycentric fan")
    print("PASS parent brackets: 70/70 on six rational triangles")
    print("PASS residual factors: 26738 sign-definite + 2 active")
    print("PASS active arrangement: two boundary-to-boundary arcs / one node / four sectors")
    print("PASS singular-chain boundary: six radial cancellations")
    print("PASS hostile canaries:", len(rejected), "/", len(rejected))
    print("THEOREM mask-6 loop bounds for one certified proper incomparable eight-family")
    print("SCOPE parent 860 bounded discriminator; honest 9DVL score remains 2/9")


if __name__ == "__main__":
    main()
