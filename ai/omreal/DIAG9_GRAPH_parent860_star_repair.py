#!/usr/bin/env python3
"""Counterexample-guided exact repair of the parent-860 coordinate star.

``DIAG9_GRAPH_parent860_star.py`` finds a one-signature disconnected support
on the exact coordinate-star tree.  This checker applies the intended
heuristic-to-exact loop:

* join repeated exact tope states by ten straight segments;
* add six lowest-complexity cross-state segments in two CEGIS rounds; and
* audit every segment against all 26,740 residual factors and every parent
  bracket by exact univariate Sturm counts.

Ten segments are residual-free, five cross one isolated residual wall, and
one crosses two isolated walls.  The two-wall segment contributes one new
generic cell, whose complete derived-tope label is enumerated exactly.  The
resulting finite network is then relabeled and searched again for disconnected
common supports.

This is a proof-producing heuristic pilot on a finite embedded network.  It
does not prove coverage of the nine-dimensional parent cell or any 9DVL
diagonal.
"""

from __future__ import annotations

import argparse
from collections import Counter
from fractions import Fraction
import hashlib
from math import comb
from pathlib import Path
import sys

import numpy as np


HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import DIAG2_PIVOT_LABELED_PAIR_ORBITS_VERIFY as labeled  # noqa: E402
import DIAG2_PIVOT_REPRESENTATIVE_GRADIENT_VERIFY as representative  # noqa: E402
import DIAG9_GRAPH_exact_topes as topes  # noqa: E402
import DIAG9_GRAPH_parent860_star as star  # noqa: E402
import DIAG9_GRAPH_verify_row2599_slice as sturm  # noqa: E402


CERTIFICATE = star.DATA / "DIAG9_GRAPH_parent860_star_repair.npz"
FORMAT = "diag9-parent860-star-repair-v1"

# First ten pairs have identical complete tope labels.  The last six are
# counterexample-guided cross-state repairs.
CHORDS = (
    (3, 6),
    (3, 7),
    (3, 18),
    (3, 20),
    (3, 21),
    (4, 11),
    (8, 10),
    (8, 16),
    (12, 14),
    (19, 22),
    (2, 8),
    (15, 17),
    (1, 17),
    (13, 19),
    (9, 19),
    # Second CEGIS round: join the isolated two-signature middle cell.
    (23, 4),
)
EXPECTED_ROOT_FACTORS = (
    (),
    (),
    (),
    (),
    (),
    (),
    (),
    (),
    (),
    (),
    (15250,),
    (15250,),
    (22629,),
    (16573, 16249),
    (22629,),
    (19721,),
)
EXPECTED_ROOT_DEGREES = (
    (),
    (),
    (),
    (),
    (),
    (),
    (),
    (),
    (),
    (),
    (2,),
    (1,),
    (1,),
    (3, 1),
    (1,),
    (2,),
)
EXPECTED_DIGEST = "3311c16bd553024891fc2cdcd68f2591135a43911146df221b4e1aa01672076e"


def multiply(left, right):
    result = [Fraction(0)] * (len(left) + len(right) - 1)
    for first, left_value in enumerate(left):
        for second, right_value in enumerate(right):
            result[first + second] += left_value * right_value
    return result


def affine_power(intercept, slope, exponent):
    return [
        Fraction(comb(exponent, degree))
        * intercept ** (exponent - degree)
        * slope**degree
        for degree in range(exponent + 1)
    ]


def restrict_segment(polynomial, source, target):
    direction = tuple(right - left for left, right in zip(source, target))
    changed = tuple(index for index, value in enumerate(direction) if value)
    result = [Fraction(0)]
    for monomial, coefficient in polynomial.items():
        fixed = Fraction(coefficient)
        term = [Fraction(1)]
        for variable, exponent in enumerate(monomial):
            if not exponent:
                continue
            if variable in changed:
                term = multiply(
                    term,
                    affine_power(source[variable], direction[variable], exponent),
                )
            else:
                fixed *= source[variable] ** exponent
        term = [fixed * value for value in term]
        if len(term) > len(result):
            result.extend([Fraction(0)] * (len(term) - len(result)))
        for degree, value in enumerate(term):
            result[degree] += value
    while result and not result[-1]:
        result.pop()
    if not result:
        raise AssertionError("repair segment lies identically on a factor")
    leading = result[-1]
    return tuple(value / leading for value in result)


def vertex_points(stored):
    base = list(star.normalized_parent())
    variables = tuple(map(int, stored["vertex_variable"]))
    parameters = tuple(
        Fraction(int(numerator), int(denominator))
        for numerator, denominator in zip(
            stored["vertex_parameter_numerator"],
            stored["vertex_parameter_denominator"],
        )
    )
    answer = []
    for variable, parameter in zip(variables, parameters):
        point = base[:]
        if variable >= 0:
            point[variable] += parameter
        answer.append(tuple(point))
    return tuple(answer)


def simple_between(left, right):
    midpoint = (left + right) / 2
    for bound in (10**6, 10**8, 10**10, 10**12, 10**14, 10**16):
        candidate = midpoint.limit_denominator(bound)
        if left < candidate < right:
            return candidate
    return midpoint


def exact_topes(coordinates, expected_parent):
    matrix = star.matrix_from_coordinates(coordinates)
    if topes.parent_signs(matrix) != expected_parent:
        raise AssertionError("repair sample leaves parent 860")
    rows = topes.derived_rows(matrix)
    result = topes.enumerate_topes(rows, dimension=4)
    topes.verify_topes(rows, result)
    if len(result) != 26_112:
        raise AssertionError("repair sample is not a generic chamber")
    return tuple(sorted(result))


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
    with np.load(star.ROADMAP, allow_pickle=False) as source:
        stored = {name: source[name] for name in source.files}
    if str(stored["format"].item()) != star.FORMAT:
        raise AssertionError("wrong parent-860 star certificate")
    points = list(vertex_points(stored))
    cell_topes = [tuple(map(int, row)) for row in stored["cell_tope"]]
    expected_parent = topes.parent_signs(star.matrix_from_coordinates(points[0]))
    occurrences, occurrence_factor, factor_polynomials = labeled.factor_polynomials()
    _residual, brackets = representative.polynomial_data()

    chord_root_offset = [0]
    chord_root_factor = []
    chord_root_degree = []
    chord_root_lower = []
    chord_root_upper = []
    chord_cell_offset = [0]
    chord_cell_vertex = []
    new_cell_coordinates = []
    augmented_edges = [tuple(map(int, edge)) for edge in stored["edge"]]

    for chord_index, (left, right) in enumerate(CHORDS):
        source, target = points[left], points[right]
        roots = []
        for factor, polynomial in enumerate(factor_polynomials):
            restriction = restrict_segment(polynomial, source, target)
            if len(restriction) <= 1:
                continue
            for lower, upper in star.isolate_roots(
                restriction, Fraction(0), Fraction(1)
            ):
                roots.append(
                    (lower, upper, factor, len(restriction) - 1, restriction)
                )
        roots.sort(key=lambda item: (item[0], item[1], item[2]))
        if any(first[1] >= second[0] for first, second in zip(roots, roots[1:])):
            raise AssertionError("repair segment has an unresolved simultaneous root")
        factors = tuple(root[2] for root in roots)
        degrees = tuple(root[3] for root in roots)
        if factors != EXPECTED_ROOT_FACTORS[chord_index]:
            raise AssertionError(
                f"repair chord {CHORDS[chord_index]} root factors changed: {factors}"
            )
        if degrees != EXPECTED_ROOT_DEGREES[chord_index]:
            raise AssertionError("repair chord root degrees changed")
        if not roots and cell_topes[left] != cell_topes[right]:
            raise AssertionError("residual-free repair chord changed its tope label")
        for label, polynomial in brackets.items():
            restriction = restrict_segment(polynomial, source, target)
            if len(restriction) > 1 and sturm.root_count(
                restriction, Fraction(0), Fraction(1)
            ):
                raise AssertionError(
                    f"repair chord {CHORDS[chord_index]} crosses bracket {label}"
                )

        path = [left]
        for first, second in zip(roots, roots[1:]):
            parameter = simple_between(first[1], second[0])
            coordinates = tuple(
                start + parameter * (finish - start)
                for start, finish in zip(source, target)
            )
            vertex = len(cell_topes)
            path.append(vertex)
            chord_cell_vertex.append(vertex)
            cell_topes.append(exact_topes(coordinates, expected_parent))
            points.append(coordinates)
            new_cell_coordinates.append(coordinates)
        path.append(right)
        augmented_edges.extend(
            (min(first, second), max(first, second))
            for first, second in zip(path, path[1:])
        )

        for lower, upper, factor, degree, _restriction in roots:
            chord_root_factor.append(factor)
            chord_root_degree.append(degree)
            chord_root_lower.append(lower)
            chord_root_upper.append(upper)
        chord_root_offset.append(len(chord_root_factor))
        chord_cell_offset.append(len(chord_cell_vertex))
        if progress:
            print(
                f"repair chord {chord_index + 1}/{len(CHORDS)}:",
                CHORDS[chord_index],
                "roots",
                factors,
                flush=True,
            )

    if len(set(augmented_edges)) != len(augmented_edges):
        raise AssertionError("repair graph has a duplicate edge")
    graph = [[] for _ in cell_topes]
    for left, right in augmented_edges:
        graph[left].append(right)
        graph[right].append(left)
    patterns = star.signature_patterns(cell_topes)
    proper, support = star.support_matrix(patterns, len(graph))
    disconnected = star.shortest_disconnected_intersection(
        patterns.values(), graph, maximum_size=len(proper)
    )

    # The CEGIS target is first to repair every individual signature support.
    disconnected_individual = tuple(
        pattern for pattern in proper if not star.connected_mask(pattern, graph)
    )
    if disconnected_individual:
        raise AssertionError(
            f"CEGIS repair left individual residues: {disconnected_individual}"
        )
    if disconnected[0] is not None:
        raise AssertionError(f"CEGIS repair left a finite-family residue: {disconnected}")
    payload = {
        "format": np.asarray(FORMAT),
        "chord": np.asarray(CHORDS, dtype=np.uint8),
        "chord_root_offset": np.asarray(chord_root_offset, dtype=np.uint8),
        "chord_root_factor": np.asarray(chord_root_factor, dtype=np.uint16),
        "chord_root_degree": np.asarray(chord_root_degree, dtype=np.uint8),
        "chord_root_lower_numerator": string_array(
            value.numerator for value in chord_root_lower
        ),
        "chord_root_lower_denominator": string_array(
            value.denominator for value in chord_root_lower
        ),
        "chord_root_upper_numerator": string_array(
            value.numerator for value in chord_root_upper
        ),
        "chord_root_upper_denominator": string_array(
            value.denominator for value in chord_root_upper
        ),
        "chord_cell_offset": np.asarray(chord_cell_offset, dtype=np.uint8),
        "chord_cell_vertex": np.asarray(chord_cell_vertex, dtype=np.uint8),
        "new_cell_tope": np.asarray(
            cell_topes[star.EXPECTED_VERTEX_COUNT :], dtype=np.uint64
        ),
        "new_cell_coordinate_numerator": np.asarray(
            tuple(
                tuple(str(value.numerator) for value in coordinates)
                for coordinates in new_cell_coordinates
            )
        ),
        "new_cell_coordinate_denominator": np.asarray(
            tuple(
                tuple(str(value.denominator) for value in coordinates)
                for coordinates in new_cell_coordinates
            )
        ),
        "augmented_edge": np.asarray(augmented_edges, dtype=np.uint8),
        "signature": np.asarray(tuple(sorted(patterns)), dtype=np.uint64),
        "signature_pattern": np.asarray(
            tuple(patterns[signature] for signature in sorted(patterns)),
            dtype=np.uint32,
        ),
        "proper_pattern": np.asarray(proper, dtype=np.uint32),
        "disconnected_individual_pattern": np.asarray(
            disconnected_individual, dtype=np.uint32
        ),
        "shortest_disconnected_size": np.asarray(
            disconnected[0] or 0, dtype=np.uint8
        ),
        "shortest_disconnected_pattern_indices": np.asarray(
            disconnected[1], dtype=np.uint16
        ),
        "shortest_disconnected_mask": np.asarray(
            disconnected[2], dtype=np.uint32
        ),
        "support": support,
    }
    return payload, patterns, disconnected, disconnected_individual


def compare_payload(stored, replay):
    if set(stored) != set(replay):
        raise AssertionError("parent-860 repair fields changed")
    for name in sorted(replay):
        if not np.array_equal(np.asarray(stored[name]), np.asarray(replay[name])):
            raise AssertionError(f"parent-860 repair field changed: {name}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--build", action="store_true")
    args = parser.parse_args()

    replay, patterns, disconnected, disconnected_individual = reconstruct()
    digest = semantic_digest(replay)
    if EXPECTED_DIGEST is not None and digest != EXPECTED_DIGEST:
        raise AssertionError("parent-860 star-repair semantic digest changed")
    if args.build:
        star.DATA.mkdir(parents=True, exist_ok=True)
        np.savez_compressed(CERTIFICATE, **replay)
        print("WROTE", CERTIFICATE)
    else:
        with np.load(CERTIFICATE, allow_pickle=False) as source:
            stored = {name: source[name] for name in source.files}
        compare_payload(stored, replay)

    print("PASS exact all-factor root coverage for", len(CHORDS), "repair chords")
    print("PASS residual-free same-state chords: 10")
    print("PASS one-wall cross-state chords: 5")
    print("PASS two-wall cross-state chords: 1")
    print("PASS augmented generic chambers:", len(replay["new_cell_tope"]))
    print("PASS augmented supported signatures:", len(patterns))
    print("PASS augmented proper support patterns:", len(replay["proper_pattern"]))
    if len(disconnected_individual):
        print("RESIDUE disconnected individual supports:", disconnected_individual)
    else:
        print("THEOREM every individual signature support is connected on the repaired network")
    if disconnected[0] is None:
        print("THEOREM every finite intersection of network supports is connected")
    else:
        print("NEXT COUNTEREXAMPLE shortest disconnected intersection:", disconnected)
    print("SEMANTIC SHA256:", digest)
    print("SCOPE exact finite network inside parent 860; no global 9DVL verdict")


if __name__ == "__main__":
    main()
