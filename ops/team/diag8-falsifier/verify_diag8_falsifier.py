#!/usr/bin/env python3
"""Exact adversarial replay for the diagonal-eight strategy-reset cycle.

This checker deliberately separates three evidence classes:

* exact geometry on the certified parent-860 a/g polygon;
* exact finite topology on stored parent-860 and row-2599 artifacts; and
* a minimal abstract labelled-complex countermodel.

Nothing here proves or disproves diagonal eight globally.  In particular, the
parent-860 repaired network has neither full-dimensional coverage nor a
complete codimension-two complex.
"""

from __future__ import annotations

from collections import Counter, defaultdict
from fractions import Fraction
from itertools import combinations
import json
from math import comb
from pathlib import Path
import sys

import numpy as np


HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
OMREAL = REPO / "ai" / "omreal"
DATA = OMREAL / "data"
sys.path.insert(0, str(OMREAL))

import DIAG2_PIVOT_LABELED_PAIR_ORBITS_VERIFY as labeled  # noqa: E402
import DIAG2_PIVOT_REPRESENTATIVE_GRADIENT_VERIFY as representative  # noqa: E402
import DIAG9_GRAPH_parent860_star as star  # noqa: E402
import DIAG9_GRAPH_parent860_star_repair as repair  # noqa: E402
import DIAG9_GRAPH_verify_row2599_slice as sturm  # noqa: E402


REPAIR = DATA / "DIAG9_GRAPH_parent860_star_repair.npz"
NODE = DATA / "DIAG9_GRAPH_row2599_node_roadmap.npz"
ANTICHAINS = (
    DATA / "ninth_candidate_12_37_antichain.npz",
    DATA / "ninth_candidate_37_176_antichain.npz",
)
COUNTERMODEL = HERE / "COUNTERMODEL.json"

MASK3_PATTERN = 3_539_150
MASK6_PATTERN = 8_419_376
MASK3_CYCLE = (1, 2, 3, 18, 17)
MASK6_CYCLE = (4, 11, 12, 14, 13, 23)
ACTIVE_FACTORS = (16_573, 22_629)


def matrix_rank(matrix):
    """Exact rank over Q."""
    if not matrix:
        return 0
    rows = [[Fraction(value) for value in row] for row in matrix]
    row_count = len(rows)
    column_count = len(rows[0])
    pivot_row = 0
    for column in range(column_count):
        pivot = next(
            (row for row in range(pivot_row, row_count) if rows[row][column]),
            None,
        )
        if pivot is None:
            continue
        rows[pivot_row], rows[pivot] = rows[pivot], rows[pivot_row]
        scale = rows[pivot_row][column]
        rows[pivot_row] = [value / scale for value in rows[pivot_row]]
        for row in range(row_count):
            if row != pivot_row and rows[row][column]:
                scale = rows[row][column]
                rows[row] = [
                    left - scale * right
                    for left, right in zip(rows[row], rows[pivot_row])
                ]
        pivot_row += 1
        if pivot_row == row_count:
            break
    return pivot_row


def beta1(vertices, edges, faces=()):
    """First Betti number of an oriented finite 2-complex over Q."""
    vertices = tuple(vertices)
    edges = tuple(tuple(edge) for edge in edges)
    faces = tuple(tuple(face) for face in faces)
    vertex_position = {vertex: index for index, vertex in enumerate(vertices)}
    if len(vertex_position) != len(vertices):
        raise AssertionError("duplicate vertex")
    normalized_edges = {}
    boundary1 = [[0] * len(edges) for _ in vertices]
    for edge_index, (left, right) in enumerate(edges):
        if left == right or left not in vertex_position or right not in vertex_position:
            raise AssertionError("invalid edge")
        key = frozenset((left, right))
        if key in normalized_edges:
            raise AssertionError("duplicate unoriented edge")
        normalized_edges[key] = (edge_index, left, right)
        boundary1[vertex_position[left]][edge_index] = -1
        boundary1[vertex_position[right]][edge_index] = 1

    boundary2 = [[0] * len(faces) for _ in edges]
    for face_index, face in enumerate(faces):
        if len(face) < 3 or len(set(face)) != len(face):
            raise AssertionError("invalid face boundary")
        for left, right in zip(face, face[1:] + face[:1]):
            key = frozenset((left, right))
            if key not in normalized_edges:
                raise AssertionError("face uses a missing edge")
            edge_index, stored_left, stored_right = normalized_edges[key]
            boundary2[edge_index][face_index] += (
                1 if (left, right) == (stored_left, stored_right) else -1
            )

    for vertex_row in range(len(vertices)):
        for face_column in range(len(faces)):
            if sum(
                boundary1[vertex_row][edge] * boundary2[edge][face_column]
                for edge in range(len(edges))
            ):
                raise AssertionError("boundary squared is nonzero")
    return len(edges) - matrix_rank(boundary1) - matrix_rank(boundary2)


def induced_graph(mask, edges, vertex_count):
    vertices = tuple(vertex for vertex in range(vertex_count) if (mask >> vertex) & 1)
    kept_edges = tuple(
        (left, right)
        for left, right in edges
        if ((mask >> left) & 1) and ((mask >> right) & 1)
    )
    return vertices, kept_edges


def multiply(left, right):
    answer = [Fraction(0)] * (len(left) + len(right) - 1)
    for first, left_value in enumerate(left):
        for second, right_value in enumerate(right):
            answer[first + second] += left_value * right_value
    return answer


def affine_power(intercept, slope, exponent):
    return [
        Fraction(comb(exponent, degree))
        * intercept ** (exponent - degree)
        * slope**degree
        for degree in range(exponent + 1)
    ]


def rectangle_power_coefficients(polynomial, base, bounds):
    """Power coefficients after mapping the unit square to an a/g rectangle."""
    (a_lower, a_upper), (g_lower, g_upper) = bounds
    answer = defaultdict(Fraction)
    for monomial, coefficient in polynomial.items():
        fixed = Fraction(coefficient)
        a_part = [Fraction(1)]
        g_part = [Fraction(1)]
        for variable, exponent in enumerate(monomial):
            if not exponent:
                continue
            if variable == 0:
                a_part = multiply(
                    a_part,
                    affine_power(a_lower, a_upper - a_lower, exponent),
                )
            elif variable == 6:
                g_part = multiply(
                    g_part,
                    affine_power(g_lower, g_upper - g_lower, exponent),
                )
            else:
                fixed *= base[variable] ** exponent
        for a_degree, a_value in enumerate(a_part):
            for g_degree, g_value in enumerate(g_part):
                answer[a_degree, g_degree] += fixed * a_value * g_value
    return dict(answer)


def absolute_bivariate_coefficients(polynomial, base):
    answer = defaultdict(Fraction)
    for monomial, coefficient in polynomial.items():
        fixed = Fraction(coefficient)
        for variable, exponent in enumerate(monomial):
            if variable not in (0, 6) and exponent:
                fixed *= base[variable] ** exponent
        answer[monomial[0], monomial[6]] += fixed
    return {key: value for key, value in answer.items() if value}


def bernstein_coefficients(power):
    a_degree = max(first for first, _second in power)
    g_degree = max(second for _first, second in power)
    answer = []
    for a_index in range(a_degree + 1):
        for g_index in range(g_degree + 1):
            value = Fraction(0)
            for (first, second), coefficient in power.items():
                if first <= a_index and second <= g_index:
                    value += (
                        coefficient
                        * Fraction(comb(a_index, first), comb(a_degree, first))
                        * Fraction(comb(g_index, second), comb(g_degree, second))
                    )
            answer.append(value)
    return tuple(answer)


def bernstein_sign(polynomial, base, bounds):
    coefficients = bernstein_coefficients(
        rectangle_power_coefficients(polynomial, base, bounds)
    )
    if all(value > 0 for value in coefficients):
        return 1
    if all(value < 0 for value in coefficients):
        return -1
    return 0


def multiply_bivariate(left, right):
    answer = defaultdict(Fraction)
    for (first_a, first_g), left_value in left.items():
        for (second_a, second_g), right_value in right.items():
            answer[first_a + second_a, first_g + second_g] += left_value * right_value
    return dict(answer)


def affine_triangle_power(constant, u_coefficient, v_coefficient, exponent):
    answer = {}
    for u_degree in range(exponent + 1):
        for v_degree in range(exponent - u_degree + 1):
            constant_degree = exponent - u_degree - v_degree
            multinomial = (
                comb(exponent, u_degree)
                * comb(exponent - u_degree, v_degree)
            )
            answer[u_degree, v_degree] = (
                Fraction(multinomial)
                * constant**constant_degree
                * u_coefficient**u_degree
                * v_coefficient**v_degree
            )
    return answer


def triangle_power_coefficients(polynomial, base, triangle):
    """Power coefficients after mapping the standard simplex to a triangle."""
    origin, u_vertex, v_vertex = triangle
    answer = defaultdict(Fraction)
    for monomial, coefficient in polynomial.items():
        fixed = Fraction(coefficient)
        for variable, exponent in enumerate(monomial):
            if variable not in (0, 6) and exponent:
                fixed *= base[variable] ** exponent
        term = {(0, 0): fixed}
        if monomial[0]:
            term = multiply_bivariate(
                term,
                affine_triangle_power(
                    origin[0],
                    u_vertex[0] - origin[0],
                    v_vertex[0] - origin[0],
                    monomial[0],
                ),
            )
        if monomial[6]:
            term = multiply_bivariate(
                term,
                affine_triangle_power(
                    origin[1],
                    u_vertex[1] - origin[1],
                    v_vertex[1] - origin[1],
                    monomial[6],
                ),
            )
        for key, value in term.items():
            answer[key] += value
    return dict(answer)


def triangle_bernstein_coefficients(power):
    degree = max(first + second for first, second in power)
    answer = []
    for u_index in range(degree + 1):
        for v_index in range(degree - u_index + 1):
            value = Fraction(0)
            for (u_degree, v_degree), coefficient in power.items():
                if u_degree <= u_index and v_degree <= v_index:
                    denominator = (
                        comb(degree, u_degree)
                        * comb(degree - u_degree, v_degree)
                    )
                    value += coefficient * Fraction(
                        comb(u_index, u_degree) * comb(v_index, v_degree),
                        denominator,
                    )
            answer.append(value)
    return tuple(answer)


def triangle_sign(polynomial, base, triangle):
    coefficients = triangle_bernstein_coefficients(
        triangle_power_coefficients(polynomial, base, triangle)
    )
    if all(value > 0 for value in coefficients):
        return 1
    if all(value < 0 for value in coefficients):
        return -1
    return 0


def point(base, variable, displacement):
    answer = list(base)
    answer[variable] += displacement
    return tuple(answer)


def restrict_segment(polynomial, source, target):
    direction = tuple(right - left for left, right in zip(source, target))
    result = [Fraction(0)]
    for monomial, coefficient in polynomial.items():
        fixed = Fraction(coefficient)
        term = [Fraction(1)]
        for variable, exponent in enumerate(monomial):
            if not exponent:
                continue
            term = multiply(
                term,
                affine_power(source[variable], direction[variable], exponent),
            )
        term = [fixed * value for value in term]
        if len(term) > len(result):
            result.extend([Fraction(0)] * (len(term) - len(result)))
        for degree, value in enumerate(term):
            result[degree] += value
    while result and not result[-1]:
        result.pop()
    if not result:
        raise AssertionError("segment lies identically on a polynomial")
    leading = result[-1]
    return tuple(value / leading for value in result)


def boundary_profile(polynomials, boundary):
    profile = []
    for factor in ACTIVE_FACTORS:
        restriction = restrict_segment(polynomials[factor], *boundary)
        roots = star.isolate_roots(restriction, Fraction(0), Fraction(1))
        for lower, upper in roots:
            profile.append((lower, upper, factor))
    profile.sort()
    if any(left[1] >= right[0] for left, right in zip(profile, profile[1:])):
        raise AssertionError("boundary roots are not separated")
    return tuple(factor for _lower, _upper, factor in profile)


def verify_parent860_polygon(polynomials, brackets):
    base = star.normalized_parent()
    a1 = Fraction(-43, 586_726)
    a3 = Fraction(-1, 84_724)
    g18 = Fraction(-15, 429_241)
    g17 = Fraction(-64, 757_309)
    polygon = (
        point(base, 0, a1),
        point(base, 0, a3),
        point(base, 6, g18),
        point(base, 6, g17),
    )
    polygon_2d = tuple((value[0], value[6]) for value in polygon)
    triangles = (
        (polygon_2d[0], polygon_2d[1], polygon_2d[2]),
        (polygon_2d[0], polygon_2d[2], polygon_2d[3]),
    )
    bounds = (
        tuple(sorted((base[0] + a1, base[0]))),
        tuple(sorted((base[6] + g17, base[6]))),
    )

    factor_signs = Counter()
    unresolved = []
    for factor, polynomial in enumerate(polynomials):
        signs = tuple(triangle_sign(polynomial, base, triangle) for triangle in triangles)
        if signs == (1, 1):
            factor_signs[1] += 1
        elif signs == (-1, -1):
            factor_signs[-1] += 1
        else:
            unresolved.append(factor)
    if factor_signs != Counter({-1: 13_712, 1: 13_026}):
        raise AssertionError("factor Bernstein census changed")
    if tuple(unresolved) != ACTIVE_FACTORS:
        raise AssertionError(f"unexpected polygon factors: {unresolved}")

    rectangle_bracket_signs = Counter(
        bernstein_sign(polynomial, base, bounds) for polynomial in brackets.values()
    )
    if rectangle_bracket_signs != Counter({-1: 37, 1: 33}):
        raise AssertionError("parent bracket is unresolved on the bounding rectangle")

    bracket_signs = Counter()
    for polynomial in brackets.values():
        signs = tuple(triangle_sign(polynomial, base, triangle) for triangle in triangles)
        if signs not in ((1, 1), (-1, -1)):
            raise AssertionError("parent bracket is unresolved on the polygon")
        bracket_signs[signs[0]] += 1
    if bracket_signs != Counter({-1: 37, 1: 33}):
        raise AssertionError("parent-bracket Bernstein census changed")

    profiles = tuple(
        boundary_profile(polynomials, (left, right))
        for left, right in zip(polygon, polygon[1:] + polygon[:1])
    )
    if profiles != ((16_573, 22_629), (), (16_573,), (22_629,)):
        raise AssertionError(f"polygon boundary profile changed: {profiles}")

    first = absolute_bivariate_coefficients(polynomials[16_573], base)
    second = absolute_bivariate_coefficients(polynomials[22_629], base)
    if set(second) != {(0, 0), (1, 0)}:
        raise AssertionError("factor 22629 is no longer an affine a-wall")
    a_node = -second[0, 0] / second[1, 0]
    if not base[0] + a1 < a_node < base[0] + a3:
        raise AssertionError("node a-coordinate left the polygon top span")

    g_polynomial = []
    for degree in range(max(g for _a, g in first) + 1):
        g_polynomial.append(
            first.get((0, degree), Fraction(0))
            + a_node * first.get((1, degree), Fraction(0))
        )
    while g_polynomial and not g_polynomial[-1]:
        g_polynomial.pop()
    if len(g_polynomial) != 3:
        raise AssertionError("node equation is no longer quadratic in g")

    a_delta = a_node - base[0]
    outer_g_delta = (a_delta - a1) * g17 / (-a1)
    g_lower = base[6] + outer_g_delta
    g_upper = base[6]
    if sturm.root_count(g_polynomial, g_lower, g_upper) != 1:
        raise AssertionError("polygon does not contain exactly one transverse node")
    derivative = (
        g_polynomial[1] + 2 * g_polynomial[2] * g_lower,
        g_polynomial[1] + 2 * g_polynomial[2] * g_upper,
    )
    if not (all(value < 0 for value in derivative) or all(value > 0 for value in derivative)):
        raise AssertionError("node transversality is unresolved")

    # The other active wall is a graph a=a(g) throughout the rectangle.
    a_slope = (
        first.get((1, 0), Fraction(0))
        + first.get((1, 1), Fraction(0)) * bounds[1][0],
        first.get((1, 0), Fraction(0))
        + first.get((1, 1), Fraction(0)) * bounds[1][1],
    )
    if not (all(value < 0 for value in a_slope) or all(value > 0 for value in a_slope)):
        raise AssertionError("factor 16573 is not a graph on the rectangle")
    return profiles


def maximum_antichain(patterns):
    best = ()
    checked_at_eight = 0
    antichains_at_eight = 0
    for size in range(1, len(patterns) + 1):
        for chosen in combinations(range(len(patterns)), size):
            if size == 8:
                checked_at_eight += 1
            incomparable = all(
                (patterns[left] & patterns[right])
                not in (patterns[left], patterns[right])
                for left, right in combinations(chosen, 2)
            )
            if incomparable:
                best = chosen
                if size == 8:
                    antichains_at_eight += 1
    return best, checked_at_eight, antichains_at_eight


def verify_parent860_network():
    with np.load(REPAIR, allow_pickle=False) as source:
        if str(source["format"].item()) != repair.FORMAT:
            raise AssertionError("wrong parent-860 repair format")
        edges = tuple(tuple(map(int, edge)) for edge in source["augmented_edge"])
        signatures = tuple(map(int, source["signature"]))
        signature_patterns = tuple(map(int, source["signature_pattern"]))
        proper_patterns = tuple(map(int, source["proper_pattern"]))
    if len(edges) != 39 or len(signatures) != 26_264 or len(proper_patterns) != 12:
        raise AssertionError("parent-860 network dimensions changed")

    all_vertices = tuple(range(24))
    if beta1(all_vertices, edges) != 16:
        raise AssertionError("parent-860 graph cycle rank changed")
    best, checked, antichains = maximum_antichain(proper_patterns)
    if len(best) != 6 or checked != comb(12, 8) or antichains:
        raise AssertionError("artifact-internal dominance width changed")

    results = []
    for pattern, cycle in (
        (MASK3_PATTERN, MASK3_CYCLE),
        (MASK6_PATTERN, MASK6_CYCLE),
    ):
        if pattern not in proper_patterns:
            raise AssertionError("expected support pattern disappeared")
        vertices, induced_edges = induced_graph(pattern, edges, 24)
        if beta1(vertices, induced_edges) != 1:
            raise AssertionError("expected network loop disappeared")
        for left, right in zip(cycle, cycle[1:] + cycle[:1]):
            if frozenset((left, right)) not in map(frozenset, induced_edges):
                raise AssertionError("stored loop edge disappeared")
        cycle_mask = sum(1 << vertex for vertex in cycle)
        common = tuple(
            signature
            for signature, support in zip(signatures, signature_patterns)
            if support & cycle_mask == cycle_mask
        )
        if len(common) != 26_038:
            raise AssertionError("loop common-label census changed")
        results.append((vertices, induced_edges, common))

    # The exact a/g polygon supplies the missing node dual cell for mask 3.
    vertices, induced_edges, _common = results[0]
    if beta1(vertices, induced_edges, (MASK3_CYCLE,)) != 0:
        raise AssertionError("the certified mask-3 face did not kill its loop")
    return len(best), checked, results


NODE_WALLS = ((0, 3), (1, 2), (2, 3), (0, 1))


def node_beta(mask):
    vertices, edges = induced_graph(mask, NODE_WALLS, 4)
    faces = ((0, 1, 2, 3),) if mask == 0b1111 else ()
    return beta1(vertices, edges, faces)


def verify_row2599_node():
    with np.load(NODE, allow_pickle=False) as source:
        if str(source["format"].item()) != "diag9-row2599-transverse-node-v1":
            raise AssertionError("wrong row-2599 node format")
        signatures = tuple(map(int, source["signature"]))
        patterns = tuple(map(int, source["signature_pattern"]))
        closure = tuple(map(int, source["intersection_closure"]))
    if any(node_beta(mask) for mask in closure):
        raise AssertionError("row-2599 node closure acquired H1")
    signature_pattern = dict(zip(signatures, patterns))

    checked = 0
    family_masks = []
    for certificate_path in ANTICHAINS:
        with np.load(certificate_path, allow_pickle=False) as certificate:
            if int(certificate["parent_index"].item()) != 2599:
                raise AssertionError("antichain belongs to the wrong parent")
            family = tuple(map(int, certificate["signature"]))
        if len(family) != 9:
            raise AssertionError("expected a certified nine-antichain")
        for chosen in combinations(family, 8):
            mask = 0b1111
            for signature in chosen:
                mask &= signature_pattern.get(signature, 0)
            if mask not in closure or node_beta(mask):
                raise AssertionError("certified eight-subfamily has local H1")
            family_masks.append(mask)
            checked += 1
    if checked != 18:
        raise AssertionError("wrong eight-subfamily exhaustion count")
    return closure, tuple(family_masks)


def verify_countermodel(payload):
    if payload.get("format") != "diag8-labelled-complex-countermodel-v1":
        raise AssertionError("wrong abstract-countermodel format")
    vertices = tuple(payload["vertices"])
    edges = tuple(tuple(edge) for edge in payload["edges"])
    faces = tuple(tuple(face) for face in payload["faces"])
    labels = {name: frozenset(support) for name, support in payload["labels"].items()}
    if len(vertices) != 8 or len(labels) != 8:
        raise AssertionError("countermodel is not the claimed minimal size")
    universe = frozenset(vertices)
    if any(not support or support == universe or not support <= universe for support in labels.values()):
        raise AssertionError("countermodel has an improper label")
    if any(
        left <= right or right <= left
        for left, right in combinations(labels.values(), 2)
    ):
        raise AssertionError("countermodel labels are not an antichain")

    common = set.intersection(*(set(support) for support in labels.values()))
    if common != set(payload["claimed_common_cycle"]):
        raise AssertionError("countermodel common support changed")
    common_edges = tuple(edge for edge in edges if set(edge) <= common)
    common_faces = tuple(face for face in faces if set(face) <= common)
    if beta1(tuple(common), common_edges, common_faces) != payload["claimed_beta1"]:
        raise AssertionError("countermodel H1 claim failed")

    # Cell labels are, by construction, the intersection of their vertex
    # labels.  This is the combinatorial all-strata/cell-induced axiom.
    vertex_labels = {
        vertex: frozenset(name for name, support in labels.items() if vertex in support)
        for vertex in vertices
    }
    for cell in edges + faces:
        cell_label = set.intersection(*(set(vertex_labels[vertex]) for vertex in cell))
        for name, support in labels.items():
            if (name in cell_label) != (set(cell) <= support):
                raise AssertionError("countermodel is not cell-induced")

    # The ambient complex collapses to a point: delete the four marker leaves,
    # then use the three free outer edges to delete the wheel faces; what
    # remains is the three-spoke tree.
    marker_edges = {frozenset(("b0", f"m{index}")) for index in range(4)}
    if not marker_edges <= {frozenset(edge) for edge in edges}:
        raise AssertionError("countermodel marker leaves changed")
    outer_edges = {frozenset(("b0", "b1")), frozenset(("b1", "b2")), frozenset(("b2", "b0"))}
    if not all(sum(edge <= set(face) for face in faces) == 1 for edge in outer_edges):
        raise AssertionError("countermodel wheel lacks free outer edges")

    # Vertex minimality within this labelled-simplicial architecture: nonzero
    # simplicial H1 needs at least three common vertices.  Eight incomparable
    # label supports need at least five varying vertices, since the largest
    # antichain on four bits has size C(4,2)=6 < 8 (Sperner).
    four_bit_best, _checked, _at_eight = maximum_antichain(tuple(range(1 << 4)))
    if len(four_bit_best) != 6 or comb(4, 2) != 6 or 3 + 5 != len(vertices):
        raise AssertionError("countermodel minimality arithmetic changed")
    return labels


def expect_failure(function, *args):
    try:
        function(*args)
    except AssertionError:
        return
    raise AssertionError("hostile canary was accepted")


def run_canaries(countermodel):
    if beta1((0, 1, 2), ((0, 1), (1, 2))) != 0:
        raise AssertionError("known-tree canary failed")
    if beta1((0, 1, 2), ((0, 1), (1, 2), (2, 0)), ((0, 1, 2),)) != 0:
        raise AssertionError("filled-cycle canary failed")
    if beta1((0, 1, 2), ((0, 1), (1, 2), (2, 0))) != 1:
        raise AssertionError("missing-two-cell canary failed")
    hostile = json.loads(json.dumps(countermodel))
    hostile["labels"]["rho0"].remove("b0")
    expect_failure(verify_countermodel, hostile)


def main():
    occurrences, occurrence_factor, polynomials = labeled.factor_polynomials()
    if len(polynomials) != 26_740 or len(occurrences) != 84_840:
        raise AssertionError("global factor universe changed")
    _residual, brackets = representative.polynomial_data()
    if len(brackets) != 70:
        raise AssertionError("parent bracket universe changed")

    profiles = verify_parent860_polygon(polynomials, brackets)
    width, width_checks, network_results = verify_parent860_network()
    closure, family_masks = verify_row2599_node()
    countermodel = json.loads(COUNTERMODEL.read_text(encoding="utf-8"))
    verify_countermodel(countermodel)
    run_canaries(countermodel)

    print("PASS geometric: parent-860 a/g rectangle is parent-safe")
    print("PASS geometric: 26,738/26,740 factors are triangle-Bernstein sign-definite")
    print("PASS geometric: only factors 16573 and 22629 meet the polygon")
    print("PASS geometric: boundary profiles", profiles)
    print("PASS geometric: the two walls have one transverse node inside the polygon")
    print("FINITE-EXACT: mask-3 network beta1=1 is killed by its node dual 2-cell")
    print("FINITE-EXACT: mask-6 network beta1=1 remains a codimension-two discriminator")
    print("FINITE-EXACT: each loop has", len(network_results[0][2]), "common stored labels")
    print("FINITE-EXACT: local parent-860 pattern width", width, "after", width_checks, "size-8 tests")
    print("FINITE-EXACT: row-2599 node closure", closure, "has beta1=0")
    print("FINITE-EXACT: 18 certified global-antichain eight-subfamilies tested; masks", family_masks)
    print("ABSTRACT-DISPROVED: 8-vertex cell-induced antichain complex has beta1=1")
    print("PASS canaries: known_tree, filled_cycle, missing_two_cell, hostile_label_mutation")
    print("SCOPE: no geometric diagonal-eight counterexample and no global proof")


if __name__ == "__main__":
    main()
