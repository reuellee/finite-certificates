#!/usr/bin/env python3
"""Exact coordinate-star training roadmap through catalog parent 860.

The dual-master strategy needs proof-producing finite chamber data before a
global Morse rule can be synthesized.  This checker constructs the smallest
nontrivial parent-860 instance which is complete on its stated domain: the
union of the nine coordinate segments of radius 10^-4 through one normalized
exact realization of catalog parent 860.

All 26,740 primitive residual factors are restricted to every segment.  Exact
Sturm counts and disjoint rational boxes cover every crossing.  One complete
derived-arrangement tope enumeration labels each open one-dimensional cell.
The nine central cells are identified at their common chart, giving a finite
tree.  The resulting support masks are then searched for a shortest exact
failure of naive connected-subtree routing.

This is a complete roadmap of the displayed coordinate star, not a cover of
the nine-dimensional parent realization space and not a 9DVL verdict.
"""

from __future__ import annotations

import argparse
from collections import Counter, deque
from fractions import Fraction
import hashlib
from math import comb, gcd
from pathlib import Path
import sys

import numpy as np


HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import DIAG2_PIVOT_LABELED_PAIR_ORBITS_VERIFY as labeled  # noqa: E402
import DIAG2_PIVOT_REPRESENTATIVE_GRADIENT_VERIFY as representative  # noqa: E402
import DIAG9_GRAPH_exact_topes as topes  # noqa: E402
import DIAG9_GRAPH_verify_row2599_line as line_verify  # noqa: E402
import DIAG9_GRAPH_verify_row2599_slice as sturm  # noqa: E402
import verify_diag9_parent_ranking as ranking  # noqa: E402


DATA = HERE / "data"
ROADMAP = DATA / "DIAG9_GRAPH_parent860_coordinate_star.npz"
GRAPH = DATA / "DIAG9_GRAPH_parent860_coordinate_star_graph.npz"
FORMAT = "diag9-parent860-coordinate-star-v1"
GRAPH_FORMAT = "diag9-labeled-master-tree-v1"
PARENT_INDEX = 860
VARIABLE_NAMES = "abcdefghi"
FRAME_PERMUTATION = (5, 0, 1, 3, 4, 2, 6, 7)
SEGMENT = (Fraction(-1, 10_000), Fraction(1, 10_000))
ISOLATION_WIDTH = Fraction(1, 10**14)
EXPECTED_VERTEX_COUNT = 23
EXPECTED_EDGE_COUNT = 22
EXPECTED_ROOT_COUNTS = (5, 1, 2, 4, 0, 4, 3, 1, 2)
EXPECTED_SHORTEST_DISCONNECTED = (1, (1,), 30768)
EXPECTED_DIGEST = "391e1ee3c8e416f927d0d9b0dd02f7411e7bf061802b5ffcebf20d2ae60af6a8"


def lcm(left, right):
    return abs(left * right) // gcd(left, right)


def invert(square):
    size = len(square)
    work = [
        list(map(Fraction, row))
        + [Fraction(int(row_index == column)) for column in range(size)]
        for row_index, row in enumerate(square)
    ]
    for column in range(size):
        pivot = next(
            (row for row in range(column, size) if work[row][column]), None
        )
        if pivot is None:
            raise AssertionError("singular projective frame")
        work[column], work[pivot] = work[pivot], work[column]
        scale = work[column][column]
        work[column] = [value / scale for value in work[column]]
        for row in range(size):
            if row == column:
                continue
            scale = work[row][column]
            work[row] = [
                value - scale * pivot_value
                for value, pivot_value in zip(work[row], work[column])
            ]
    return tuple(tuple(row[size:]) for row in work)


def normalized_parent():
    """Put the relabeled exact parent into the repository's nine-coordinate frame."""

    source = tuple(tuple(map(Fraction, row)) for row in ranking.EXPECTED_PARENT860_MATRIX)
    permuted = tuple(
        tuple(row[column] for column in FRAME_PERMUTATION) for row in source
    )
    basis = tuple(tuple(row[column] for column in range(4)) for row in permuted)
    inverse = invert(basis)
    reduced = tuple(
        tuple(
            sum(inverse[row][inner] * permuted[inner][column] for inner in range(4))
            for column in range(8)
        )
        for row in range(4)
    )
    fifth = tuple(reduced[row][4] for row in range(4))
    if not all(fifth):
        raise AssertionError("chosen fifth frame column has a zero coordinate")
    matrix = [
        [reduced[row][column] / fifth[row] for column in range(8)]
        for row in range(4)
    ]
    for column in range(4):
        for row in range(4):
            matrix[row][column] *= fifth[column]
    for column in range(5, 8):
        scale = matrix[0][column]
        if not scale:
            raise AssertionError("nonframe column is at projective infinity")
        for row in range(4):
            matrix[row][column] /= scale
    matrix = tuple(tuple(row) for row in matrix)
    expected_prefix = (
        (1, 0, 0, 0, 1),
        (0, 1, 0, 0, 1),
        (0, 0, 1, 0, 1),
        (0, 0, 0, 1, 1),
    )
    if tuple(tuple(matrix[row][column] for column in range(5)) for row in range(4)) != expected_prefix:
        raise AssertionError("projective normalization missed the standard frame")
    coordinates = tuple(
        matrix[row][column]
        for column in range(5, 8)
        for row in range(1, 4)
    )
    expected = tuple(
        map(
            Fraction,
            (
                "40/7729",
                "20720/22139",
                "-9136/33929",
                "14980/50917",
                "184820/145847",
                "12164/31931",
                "-1910/7847",
                "9970/22477",
                "1962/4921",
            ),
        )
    )
    if coordinates != expected:
        raise AssertionError("parent-860 normalized coordinates changed")
    return coordinates


def matrix_from_coordinates(coordinates):
    a, b, c, d, e, f, g, h, i = map(Fraction, coordinates)
    rational = (
        (1, 0, 0, 0, 1, 1, 1, 1),
        (0, 1, 0, 0, 1, a, d, g),
        (0, 0, 1, 0, 1, b, e, h),
        (0, 0, 0, 1, 1, c, f, i),
    )
    result = [[0] * 8 for _ in range(4)]
    for column in range(8):
        denominator = 1
        for row in range(4):
            denominator = lcm(denominator, Fraction(rational[row][column]).denominator)
        for row in range(4):
            result[row][column] = int(Fraction(rational[row][column]) * denominator)
    return tuple(tuple(row) for row in result)


def evaluate(polynomial, coordinates):
    answer = Fraction(0)
    for monomial, coefficient in polynomial.items():
        term = Fraction(coefficient)
        for variable, exponent in enumerate(monomial):
            if exponent:
                term *= coordinates[variable] ** exponent
        answer += term
    return answer


def restrict_polynomial(polynomial, variable, base):
    """Substitute x_variable=base+t and all other coordinates by base."""

    coefficients = {}
    for monomial, coefficient in polynomial.items():
        fixed = Fraction(coefficient)
        for index, exponent in enumerate(monomial):
            if index != variable and exponent:
                fixed *= base[index] ** exponent
        exponent = monomial[variable]
        for degree in range(exponent + 1):
            coefficients[degree] = coefficients.get(degree, Fraction(0)) + (
                fixed
                * comb(exponent, degree)
                * base[variable] ** (exponent - degree)
            )
    result = [
        coefficients.get(degree, Fraction(0))
        for degree in range(max(coefficients, default=0) + 1)
    ]
    while result and not result[-1]:
        result.pop()
    if not result:
        raise AssertionError("base chart lies identically on a residual factor")
    leading = result[-1]
    return tuple(value / leading for value in result)


def split_point(polynomial, left, right):
    for numerator in range(1, 32):
        candidate = (left * (32 - numerator) + right * numerator) / 32
        if sturm.polynomial_value(polynomial, candidate):
            return candidate
    raise AssertionError("could not find a nonroot rational subdivision point")


def isolate_roots(polynomial, left, right):
    total = sturm.root_count(polynomial, left, right)
    answer = []
    queue = deque(((left, right, total),))
    while queue:
        lower, upper, count = queue.popleft()
        if not count:
            continue
        if count == 1 and upper - lower <= ISOLATION_WIDTH:
            answer.append((lower, upper))
            continue
        middle = split_point(polynomial, lower, upper)
        first = sturm.root_count(polynomial, lower, middle)
        second = sturm.root_count(polynomial, middle, upper)
        if first + second != count:
            raise AssertionError("Sturm subdivision lost a root")
        queue.append((lower, middle, first))
        queue.append((middle, upper, second))
    return tuple(sorted(answer))


def crossing_groups(factor_polynomials, variable, base):
    restrictions = {}
    for factor, polynomial in enumerate(factor_polynomials):
        restriction = restrict_polynomial(polynomial, variable, base)
        restrictions.setdefault(restriction, []).append(factor)

    roots = []
    for polynomial, factors in restrictions.items():
        if len(polynomial) <= 1:
            continue
        for box in isolate_roots(polynomial, *SEGMENT):
            roots.append(
                {
                    "polynomials": [polynomial],
                    "factors": list(factors),
                    "lower": box[0],
                    "upper": box[1],
                }
            )
    roots.sort(key=lambda item: (item["lower"], item["upper"]))

    # Narrow boxes are disjoint for this generic coordinate star.  If this
    # assertion ever fails, the verifier must be upgraded to group a genuine
    # simultaneous crossing by a common polynomial gcd.
    for left, right in zip(roots, roots[1:]):
        if left["upper"] >= right["lower"]:
            common = line_verify.polynomial_gcd(
                left["polynomials"][0], right["polynomials"][0]
            )
            overlap = (max(left["lower"], right["lower"]), min(left["upper"], right["upper"]))
            if overlap[0] >= overlap[1] or sturm.root_count(common, *overlap) != 1:
                raise AssertionError("distinct coordinate-line roots need finer boxes")
            raise AssertionError("coordinate line contains an unimplemented simultaneous crossing")

    for root in roots:
        polynomial = root["polynomials"][0]
        if sturm.root_count(polynomial, root["lower"], root["upper"]) != 1:
            raise AssertionError("stored crossing box does not isolate one root")
    if sum(
        sturm.root_count(polynomial, *SEGMENT)
        for polynomial in restrictions
        if len(polynomial) > 1
    ) != len(roots):
        raise AssertionError("coordinate-line root census changed")
    return tuple(roots), restrictions


def cell_samples(roots):
    def simple_between(left, right):
        midpoint = (left + right) / 2
        for bound in (10**6, 10**8, 10**10, 10**12, 10**14, 10**16):
            candidate = midpoint.limit_denominator(bound)
            if left < candidate < right:
                return candidate
        return midpoint

    samples = [simple_between(SEGMENT[0], roots[0]["lower"])] if roots else [Fraction(0)]
    for left, right in zip(roots, roots[1:]):
        samples.append(simple_between(left["upper"], right["lower"]))
    if roots:
        samples.append(simple_between(roots[-1]["upper"], SEGMENT[1]))
    central = next(
        index
        for index, sample in enumerate(samples)
        if (
            (index == 0 or roots[index - 1]["upper"] < 0)
            and (index == len(roots) or 0 < roots[index]["lower"])
        )
    )
    samples[central] = Fraction(0)
    return tuple(samples), central


def exact_topes(base, variable, parameter, expected_parent):
    coordinates = list(base)
    coordinates[variable] += parameter
    matrix = matrix_from_coordinates(coordinates)
    if topes.parent_signs(matrix) != expected_parent:
        raise AssertionError("coordinate-star sample leaves parent 860")
    rows = topes.derived_rows(matrix)
    result = topes.enumerate_topes(rows, dimension=4)
    topes.verify_topes(rows, result)
    if len(result) != 26_112:
        raise AssertionError("coordinate-star sample is not a generic chamber")
    return tuple(sorted(result))


def connected_mask(mask, graph):
    vertices = [vertex for vertex in range(len(graph)) if mask & (1 << vertex)]
    if not vertices:
        return True
    seen = {vertices[0]}
    queue = deque(vertices[:1])
    while queue:
        vertex = queue.popleft()
        for neighbor in graph[vertex]:
            if mask & (1 << neighbor) and neighbor not in seen:
                seen.add(neighbor)
                queue.append(neighbor)
    return len(seen) == len(vertices)


def shortest_disconnected_intersection(patterns, graph, maximum_size=9):
    """Find a shortest disconnected intersection, without antichain assumptions."""

    full = (1 << len(graph)) - 1
    patterns = tuple(sorted(set(patterns) - {0, full}))
    representative = {pattern: index for index, pattern in enumerate(patterns)}
    reached = {full: ()}
    frontier = {full: ()}
    for depth in range(1, maximum_size + 1):
        following = {}
        for mask, witness in frontier.items():
            for pattern in patterns:
                reduced = mask & pattern
                if not reduced or reduced in reached or reduced in following:
                    continue
                candidate = witness + (representative[pattern],)
                if not connected_mask(reduced, graph):
                    return depth, candidate, reduced
                following[reduced] = candidate
        reached.update(following)
        frontier = following
        if not frontier:
            break
    return None, (), 0


def signature_patterns(cell_topes):
    patterns = {}
    for vertex, signatures in enumerate(cell_topes):
        bit = 1 << vertex
        for signature in signatures:
            patterns[signature] = patterns.get(signature, 0) | bit
    return patterns


def support_matrix(patterns, vertex_count):
    full = (1 << vertex_count) - 1
    proper = tuple(sorted(set(patterns.values()) - {0, full}))
    return proper, np.asarray(
        tuple(
            tuple((pattern >> vertex) & 1 for vertex in range(vertex_count))
            for pattern in proper
        ),
        dtype=np.uint8,
    )


def string_array(values):
    return np.asarray(tuple(str(value) for value in values))


def semantic_digest(payload):
    digest = hashlib.sha256()
    for name in sorted(payload):
        array = np.asarray(payload[name])
        digest.update(name.encode("ascii"))
        digest.update(str(array.dtype).encode("ascii"))
        digest.update(repr(array.shape).encode("ascii"))
        digest.update(array.tobytes())
    return digest.hexdigest()


def reconstruct(progress=True):
    base = normalized_parent()
    base_matrix = matrix_from_coordinates(base)
    expected_parent = topes.parent_signs(base_matrix)
    occurrences, occurrence_factor, factor_polynomials = labeled.factor_polynomials()
    if len(occurrences) != 84_840 or len(factor_polynomials) != 26_740:
        raise AssertionError("global residual factor census changed")

    _residual, brackets = representative.polynomial_data()
    base_bracket_signs = {
        label: evaluate(polynomial, base) > 0
        for label, polynomial in brackets.items()
    }
    if not all(evaluate(polynomial, base) for polynomial in factor_polynomials):
        raise AssertionError("parent-860 base chart lies on a residual wall")

    base_rows = topes.derived_rows(base_matrix)
    base_topes = topes.enumerate_topes(base_rows, dimension=4)
    topes.verify_topes(base_rows, base_topes)
    cell_topes = [tuple(sorted(base_topes))]
    if len(cell_topes[0]) != 26_112:
        raise AssertionError("parent-860 base chart has wrong tope count")
    vertex_variable = [-1]
    vertex_parameter = [Fraction(0)]
    edges = []
    edge_variable = []
    edge_factor_groups = []
    box_variable = []
    box_lower = []
    box_upper = []

    for variable in range(9):
        roots, restrictions = crossing_groups(factor_polynomials, variable, base)
        if len(roots) != EXPECTED_ROOT_COUNTS[variable]:
            raise AssertionError(
                f"coordinate {VARIABLE_NAMES[variable]} has {len(roots)} roots"
            )
        # Parent brackets are affine in one coordinate.  Equal nonzero signs
        # at both endpoints certify the whole segment remains in this cell.
        for label, polynomial in brackets.items():
            restriction = restrict_polynomial(polynomial, variable, base)
            if sturm.root_count(restriction, *SEGMENT):
                raise AssertionError(f"parent bracket {label} crosses the star")
            for endpoint in SEGMENT:
                coordinates = list(base)
                coordinates[variable] += endpoint
                if (evaluate(polynomial, coordinates) > 0) != base_bracket_signs[label]:
                    raise AssertionError("parent bracket endpoint sign changed")

        samples, central = cell_samples(roots)
        local_vertices = []
        for sample_index, parameter in enumerate(samples):
            if sample_index == central:
                local_vertices.append(0)
                continue
            vertex = len(cell_topes)
            local_vertices.append(vertex)
            vertex_variable.append(variable)
            vertex_parameter.append(parameter)
            cell_topes.append(exact_topes(base, variable, parameter, expected_parent))
            if progress:
                print(
                    f"parent-860 star labels {len(cell_topes)}/{EXPECTED_VERTEX_COUNT}",
                    flush=True,
                )
        for index, root in enumerate(roots):
            left = local_vertices[index]
            right = local_vertices[index + 1]
            edges.append((min(left, right), max(left, right)))
            edge_variable.append(variable)
            edge_factor_groups.append(tuple(sorted(root["factors"])))
            box_variable.append(variable)
            box_lower.append(root["lower"])
            box_upper.append(root["upper"])

    if len(cell_topes) != EXPECTED_VERTEX_COUNT or len(edges) != EXPECTED_EDGE_COUNT:
        raise AssertionError("parent-860 coordinate-star size changed")
    if len(set(edges)) != len(edges):
        raise AssertionError("coordinate-star graph has duplicate edges")
    graph = [[] for _ in cell_topes]
    for left, right in edges:
        graph[left].append(right)
        graph[right].append(left)
    if sum(len(row) for row in graph) != 2 * (len(graph) - 1):
        raise AssertionError("coordinate-star graph is not a tree")
    if not connected_mask((1 << len(graph)) - 1, graph):
        raise AssertionError("coordinate-star graph is disconnected")

    patterns = signature_patterns(cell_topes)
    proper, support = support_matrix(patterns, len(graph))
    disconnected = shortest_disconnected_intersection(patterns.values(), graph)
    if disconnected != EXPECTED_SHORTEST_DISCONNECTED:
        raise AssertionError(
            f"coordinate-star routing obstruction changed: {disconnected}"
        )
    flat_edge_factors = []
    edge_factor_offset = [0]
    for group in edge_factor_groups:
        flat_edge_factors.extend(group)
        edge_factor_offset.append(len(flat_edge_factors))

    _representatives, _stabilizers, factor_alignment, _factor_occurrence, _sizes = (
        labeled.factor_orbit_data(occurrences, occurrence_factor)
    )
    with np.load(labeled.global_factors.CERTIFICATE, allow_pickle=False) as source:
        factor_multiplicity = tuple(map(int, source["factor_multiplicity"]))
    edge_factor_type = tuple(
        factor_alignment[factor][0] for factor in flat_edge_factors
    )
    edge_factor_multiplicity = tuple(
        factor_multiplicity[factor] for factor in flat_edge_factors
    )
    pattern_representative = {
        pattern: min(
            signature
            for signature, observed in patterns.items()
            if observed == pattern
        )
        for pattern in proper
    }
    disconnected_signatures = tuple(
        pattern_representative[proper[index]] for index in disconnected[1]
    )

    payload = {
        "format": np.asarray(FORMAT),
        "parent_index": np.asarray(PARENT_INDEX, dtype=np.uint16),
        "frame_permutation": np.asarray(FRAME_PERMUTATION, dtype=np.uint8),
        "base_numerator": string_array(value.numerator for value in base),
        "base_denominator": string_array(value.denominator for value in base),
        "segment_numerator": np.asarray(
            tuple(value.numerator for value in SEGMENT), dtype=np.int64
        ),
        "segment_denominator": np.asarray(
            tuple(value.denominator for value in SEGMENT), dtype=np.int64
        ),
        "box_variable": np.asarray(box_variable, dtype=np.int8),
        "box_lower_numerator": string_array(value.numerator for value in box_lower),
        "box_lower_denominator": string_array(value.denominator for value in box_lower),
        "box_upper_numerator": string_array(value.numerator for value in box_upper),
        "box_upper_denominator": string_array(value.denominator for value in box_upper),
        "vertex_variable": np.asarray(vertex_variable, dtype=np.int8),
        "vertex_parameter_numerator": string_array(
            value.numerator for value in vertex_parameter
        ),
        "vertex_parameter_denominator": string_array(
            value.denominator for value in vertex_parameter
        ),
        "edge": np.asarray(edges, dtype=np.uint8),
        "edge_variable": np.asarray(edge_variable, dtype=np.int8),
        "edge_factor_offset": np.asarray(edge_factor_offset, dtype=np.uint16),
        "edge_factor": np.asarray(flat_edge_factors, dtype=np.uint16),
        "edge_factor_type": np.asarray(edge_factor_type, dtype=np.uint8),
        "edge_factor_multiplicity": np.asarray(
            edge_factor_multiplicity, dtype=np.uint8
        ),
        "cell_tope": np.asarray(cell_topes, dtype=np.uint64),
        "signature": np.asarray(tuple(sorted(patterns)), dtype=np.uint64),
        "signature_pattern": np.asarray(
            tuple(patterns[signature] for signature in sorted(patterns)),
            dtype=np.uint32,
        ),
        "proper_pattern": np.asarray(proper, dtype=np.uint32),
        "proper_pattern_representative_signature": np.asarray(
            tuple(pattern_representative[pattern] for pattern in proper),
            dtype=np.uint64,
        ),
        "shortest_disconnected_size": np.asarray(
            disconnected[0] or 0, dtype=np.uint8
        ),
        "shortest_disconnected_pattern_indices": np.asarray(
            disconnected[1], dtype=np.uint16
        ),
        "shortest_disconnected_signatures": np.asarray(
            disconnected_signatures, dtype=np.uint64
        ),
        "shortest_disconnected_mask": np.asarray(disconnected[2], dtype=np.uint32),
    }
    graph_payload = {
        "format": np.asarray(GRAPH_FORMAT),
        "edge": np.asarray(edges, dtype=np.int64),
        "support": support,
        "tree_edge": np.asarray(edges, dtype=np.int64),
    }
    return payload, graph_payload, patterns, disconnected


def compare_payload(stored, replay):
    if set(stored) != set(replay):
        raise AssertionError("parent-860 star certificate fields changed")
    for name in sorted(replay):
        if not np.array_equal(np.asarray(stored[name]), np.asarray(replay[name])):
            raise AssertionError(f"parent-860 star field changed: {name}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--build", action="store_true")
    args = parser.parse_args()

    replay, graph, patterns, disconnected = reconstruct(progress=True)
    digest = semantic_digest(replay)
    if EXPECTED_DIGEST is not None and digest != EXPECTED_DIGEST:
        raise AssertionError("parent-860 coordinate-star semantic digest changed")
    if args.build:
        DATA.mkdir(parents=True, exist_ok=True)
        np.savez_compressed(ROADMAP, **replay)
        np.savez_compressed(GRAPH, **graph)
        print("WROTE", ROADMAP)
        print("WROTE", GRAPH)
    else:
        with np.load(ROADMAP, allow_pickle=False) as source:
            stored = {name: source[name] for name in source.files}
        with np.load(GRAPH, allow_pickle=False) as source:
            stored_graph = {name: source[name] for name in source.files}
        compare_payload(stored, replay)
        compare_payload(stored_graph, graph)

    multiplicity = Counter(patterns.values())
    print("PASS exact projective/reorientation normalization of catalog parent 860")
    print("PASS all 26,740 factor restrictions on nine coordinate segments")
    print("PASS exact residual root counts:", EXPECTED_ROOT_COUNTS)
    print(
        "PASS complete labeled coordinate-star tree:",
        EXPECTED_VERTEX_COUNT,
        "chambers and",
        EXPECTED_EDGE_COUNT,
        "crossings",
    )
    print("PASS supported signatures:", len(patterns))
    print("PASS distinct proper coordinate-star patterns:", len(replay["proper_pattern"]))
    print("PASS support-pattern multiplicities:", dict(sorted(multiplicity.items())))
    if disconnected[0] is None:
        print("THEOREM every intersection of at most nine sampled supports is connected")
    else:
        print(
            "COUNTEREXAMPLE shortest disconnected sampled-support intersection:",
            disconnected,
        )
        print("NO-GO naive connected-subtree routing already fails on the exact star")
    print("SEMANTIC SHA256:", digest)
    print("SCOPE complete on the coordinate star; not a parent-space roadmap or 9DVL verdict")


if __name__ == "__main__":
    main()
