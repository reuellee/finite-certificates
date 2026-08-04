#!/usr/bin/env python3
"""Exact local COM diamond and two proof-safe smooth-wall no-go models.

The row-2599 transverse node realizes all nine sign covectors on its two
distinct global residual factor coordinates.  The script verifies face
symmetry, strong elimination, and the partial-cube distance condition there.

Two elementary exact polynomial models then show why a nonvanishing pivot
derivative for each individual wall does not imply either COM axiom in a
global restricted arrangement.  They are logical no-go models, not 9DVL
counterexamples and not claimed to occur among the row-2599 factors.
"""

from __future__ import annotations

from collections import deque
from fractions import Fraction
from itertools import product
from pathlib import Path

import numpy as np

import DIAG9_GRAPH_verify_row2599_node as node


HERE = Path(__file__).resolve().parent
GLOBAL = HERE / "data" / "DIAG9_GRAPH_global_factor_census.npz"
NODE = HERE / "data" / "DIAG9_GRAPH_row2599_node_roadmap.npz"
EXPECTED_FACTOR_IDS = (1657, 12874)


def compose(left, right):
    return tuple(
        first if first else second for first, second in zip(left, right)
    )


def face_symmetry(covectors):
    covectors = set(covectors)
    for left in covectors:
        for right in covectors:
            target = compose(left, tuple(-value for value in right))
            if target not in covectors:
                return False, (left, right, target)
    return True, None


def strong_elimination(covectors):
    covectors = set(covectors)
    for left in covectors:
        for right in covectors:
            separation = tuple(
                index
                for index, (first, second) in enumerate(zip(left, right))
                if first * second == -1
            )
            composed = compose(left, right)
            for eliminated in separation:
                witnesses = tuple(
                    candidate
                    for candidate in covectors
                    if candidate[eliminated] == 0
                    and all(
                        first * second == -1
                        or candidate[index] == composed[index]
                        for index, (first, second) in enumerate(zip(left, right))
                    )
                )
                if not witnesses:
                    return False, (left, right, eliminated)
    return True, None


def shortest_distances(vertex_count, edges, source):
    adjacency = [[] for _ in range(vertex_count)]
    for left, right in edges:
        adjacency[left].append(right)
        adjacency[right].append(left)
    distance = [None] * vertex_count
    distance[source] = 0
    queue = deque([source])
    while queue:
        left = queue.popleft()
        for right in adjacency[left]:
            if distance[right] is None:
                distance[right] = distance[left] + 1
                queue.append(right)
    return tuple(distance)


def global_factor_ids():
    with np.load(GLOBAL, allow_pickle=False) as source:
        occurrence = tuple(
            tuple(map(int, row)) for row in source["occurrence_fourset"]
        )
        occurrence_factor = tuple(map(int, source["occurrence_factor"]))
        multiplicity = tuple(map(int, source["factor_multiplicity"]))
    with np.load(NODE, allow_pickle=False) as source:
        offsets = tuple(map(int, source["branch_offset"]))
        branch_foursets = tuple(
            tuple(map(int, row)) for row in source["branch_fourset"]
        )
    lookup = dict(zip(occurrence, occurrence_factor, strict=True))
    answer = []
    for branch in range(2):
        classes = {
            lookup[fourset]
            for fourset in branch_foursets[offsets[branch] : offsets[branch + 1]]
        }
        if len(classes) != 1:
            raise AssertionError("local branch has several global factors")
        factor = classes.pop()
        if multiplicity[factor] != 65:
            raise AssertionError("local branch is not a size-65 factor class")
        answer.append(factor)
    return tuple(answer)


def verify_row2599_diamond():
    factors = global_factor_ids()
    if factors != EXPECTED_FACTOR_IDS or len(set(factors)) != 2:
        raise AssertionError("wrong global factor pair at the row-2599 node")

    cell_signs = tuple(node.sign_pair(point) for point in node.cell_points())
    wall_signs = tuple(node.sign_pair(point) for point in node.wall_points())
    all_covectors = set(cell_signs) | set(wall_signs) | {(0, 0)}
    expected = set(product((-1, 0, 1), repeat=2))
    if all_covectors != expected:
        raise AssertionError("transverse node does not realize the full diamond")

    first = node.CENTERED_BRANCHES[0]
    second = node.CENTERED_BRANCHES[1]
    jacobian = (
        first[(1, 0)] * second[(0, 1)]
        - second[(1, 0)] * first[(0, 1)]
    )
    if not jacobian:
        raise AssertionError("node branch gradients are dependent")

    face_ok, face_failure = face_symmetry(all_covectors)
    elimination_ok, elimination_failure = strong_elimination(all_covectors)
    if not face_ok:
        raise AssertionError(f"local face symmetry failed: {face_failure}")
    if not elimination_ok:
        raise AssertionError(
            f"local strong elimination failed: {elimination_failure}"
        )

    # The four generic chambers form an isometric square in their two sign
    # coordinates: graph distance is exactly Hamming distance.
    edges = tuple(node.GRAPH_EDGES)
    for source in range(4):
        distance = shortest_distances(4, edges, source)
        for target in range(4):
            hamming = sum(
                left != right
                for left, right in zip(cell_signs[source], cell_signs[target])
            )
            if distance[target] != hamming:
                raise AssertionError("local chamber four-cycle is not a partial cube")


def polynomial_sign(pair, kind):
    x_value, y_value = pair
    if kind == "tangent_first":
        value = y_value
    elif kind == "tangent_second":
        value = y_value - x_value * x_value
    elif kind == "strip_first":
        value = y_value
    elif kind == "strip_second":
        value = x_value + y_value * y_value - 1
    else:
        raise ValueError(kind)
    return 1 if value > 0 else -1 if value < 0 else 0


def verify_smooth_no_go_models():
    # Face-symmetry no-go on all of R^2:
    # q1=y and q2=y-x^2 both have the constant nonzero y-pivot derivative 1.
    tangent_witnesses = {
        (1, 1): (Fraction(0), Fraction(1)),
        (1, -1): (Fraction(1), Fraction(1, 2)),
        (-1, -1): (Fraction(0), Fraction(-1)),
        (0, -1): (Fraction(1), Fraction(0)),
        (1, 0): (Fraction(1), Fraction(1)),
        (0, 0): (Fraction(0), Fraction(0)),
    }
    for signs, point in tangent_witnesses.items():
        actual = (
            polynomial_sign(point, "tangent_first"),
            polynomial_sign(point, "tangent_second"),
        )
        if actual != signs:
            raise AssertionError("wrong tangent-model sign witness")
    tangent_covectors = set(tangent_witnesses)
    face_ok, _ = face_symmetry(tangent_covectors)
    target = compose((0, 0), tuple(-value for value in (1, -1)))
    if face_ok or target != (-1, 1) or target in tangent_covectors:
        raise AssertionError("tangent model did not expose face-symmetry failure")
    # Completeness is elementary: y<0 and y-x^2>0 would force y>x^2>=0.

    # Strong-elimination no-go on U=(-1/2,1/2) x R:
    # q1=y has y-pivot 1 and q2=x+y^2-1 has x-pivot 1.
    positive = (Fraction(0), Fraction(2))
    negative = (Fraction(0), Fraction(-2))
    signs_positive = (
        polynomial_sign(positive, "strip_first"),
        polynomial_sign(positive, "strip_second"),
    )
    signs_negative = (
        polynomial_sign(negative, "strip_first"),
        polynomial_sign(negative, "strip_second"),
    )
    if signs_positive != (1, 1) or signs_negative != (-1, 1):
        raise AssertionError("wrong strip-model endpoint signs")
    # Eliminating coordinate one requires (0,+).  But q1=0 forces y=0,
    # and throughout the strip q2=x-1<-1/2.
    if not Fraction(1, 2) - 1 < 0:
        raise AssertionError("strip-model elimination bound changed")


def main():
    verify_row2599_diamond()
    verify_smooth_no_go_models()
    print("PASS: row-2599 node realizes the full 3^2 covector diamond")
    print("PASS: local face symmetry and strong elimination hold exactly")
    print("PASS: its four-chamber graph is an isometric square")
    print("NO-GO: nonzero pivot derivatives alone imply neither FS nor SE")
    print("SCOPE: the no-go models are not claimed to be residual-wall instances")


if __name__ == "__main__":
    main()
