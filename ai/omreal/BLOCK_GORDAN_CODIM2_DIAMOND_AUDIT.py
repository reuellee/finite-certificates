#!/usr/bin/env python3
"""Exact codimension-two block-Gordan and cluster-route audit.

The exact row-2599 transverse node has two branches with 65 labeled
residual occurrences each.  This verifier classifies all 65*65 cross-branch
pairs under S_8, checks their support overlaps and the complete local
signature-pattern algebra, and verifies that the base-level bad-locus unions
are disks.  It also performs two exact no-go checks for interpreting the
residual identities as a universal Gr(4,8) cluster exchange system:

* the normalized residual formulas fail the Z^8 Pluecker grading except for
  type 42; and
* type 42 is an arbitrary S_8 relabel of the full-support quadratic cluster
  polynomial, but not a dihedral relabel in the standard cyclic cluster
  structure.

Finally, the complete labeled residual census has 1,554 distinct Z^8 degree
vectors, versus the known 174 cubic Gr(4,8) cluster variables.  This count is
an exact obstruction to covering every labeled residual determinant by the
cubic cluster-variable list.

The accompanying proof gives the conditional universal diamond: two
support-carried mutation composites into one nonempty node polytope are
chain-homotopic by the acyclic-carrier theorem because every coordinate
restriction is a convex polytope (or empty).  The verifier does not assert
the missing common-carrier premise for every wall pair.
"""

from collections import Counter, defaultdict
from itertools import combinations, permutations
from pathlib import Path
import sys

import numpy as np


HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import prototype_koszul_circuits as koszul  # noqa: E402
import verify_residual_log_binomials as logbin  # noqa: E402


NODE = HERE / "data" / "DIAG9_GRAPH_row2599_node_roadmap.npz"

EXPECTED_BRANCH_TYPES = {
    36: 12,
    37: 6,
    39: 3,
    41: 12,
    44: 12,
    46: 8,
    47: 12,
}
EXPECTED_DEGREE_COUNTS = {
    36: 1120,
    37: 168,
    38: 70,
    39: 168,
    41: 168,
    42: 70,
    44: 70,
    46: 1120,
    47: 168,
    48: 28,
    49: 168,
    50: 70,
    51: 70,
}

BINOMIALS = {
    36: ("1245", "2367", "1234", "1367"),
    37: ("1234", "1567", "1245", "2567"),
    38: ("1234", "1678", "1245", "2678"),
    39: ("1234", "3678", "1236", "3578"),
    41: ("1234", "3567", "1257", "3456"),
    42: ("1356", "2478", "1478", "2356"),
    44: ("1234", "5678", "1256", "3578"),
    46: ("1245", "1367", "1234", "1267"),
    47: ("1245", "1367", "1234", "1267"),
    48: ("1234", "1356", "1246", "2356"),
    49: ("1234", "1357", "1246", "2357"),
    50: ("1246", "2378", "1234", "1378"),
}
TRINOMIAL_51 = (
    (1, "1236", "4678"),
    (-1, "1267", "2468"),
    (-1, "1367", "2468"),
)


def node_branches(certificate):
    offsets = tuple(map(int, certificate["branch_offset"]))
    flat = tuple(tuple(map(int, row)) for row in certificate["branch_fourset"])
    if offsets != (0, 65, 130):
        raise AssertionError("wrong 65+65 branch offsets")
    return tuple(
        flat[offsets[index] : offsets[index + 1]]
        for index in range(2)
    )


def verify_node_supports(certificate):
    branches = node_branches(certificate)
    for branch in branches:
        types = Counter(koszul.wall_orbit(tuple(sorted(row))) for row in branch)
        if types != Counter(EXPECTED_BRANCH_TYPES):
            raise AssertionError(f"wrong branch wall-type census {types}")

    overlaps = Counter(
        len(set(first) & set(second))
        for first in branches[0]
        for second in branches[1]
    )
    if overlaps != Counter({0: 3990, 1: 235}):
        raise AssertionError(f"wrong cross-branch support overlaps {overlaps}")
    return branches


def zero_based_edges(fourset):
    return tuple(
        sorted(tuple(value - 1 for value in koszul.TRIPLES[index]) for index in fourset)
    )


def relabel(edges, permutation):
    return tuple(
        sorted(
            tuple(sorted(permutation[vertex] for vertex in edge))
            for edge in edges
        )
    )


def orbit_pair_census(branches):
    label_permutations = tuple(permutations(range(8)))
    representatives = {
        kind: tuple(
            sorted(
                tuple(int(character) - 1 for character in edge)
                for edge in koszul.REPRESENTATIVE_TEXT.split()[kind].split("/")
            )
        )
        for kind in koszul.RESIDUAL
    }
    stabilizers = {
        kind: tuple(
            permutation
            for permutation in label_permutations
            if relabel(representative, permutation) == representative
        )
        for kind, representative in representatives.items()
    }
    triple_index = {
        tuple(value - 1 for value in triple): index
        for index, triple in enumerate(koszul.TRIPLES)
    }

    edge_branches = tuple(
        tuple(zero_based_edges(row) for row in branch) for branch in branches
    )
    alignment = {}
    for branch in edge_branches:
        for edges in branch:
            if edges in alignment:
                continue
            kind = koszul.wall_orbit(tuple(triple_index[edge] for edge in edges))
            target = representatives[kind]
            permutation = next(
                candidate
                for candidate in label_permutations
                if relabel(edges, candidate) == target
            )
            alignment[edges] = kind, permutation

    def ordered_key(first, second):
        kind, permutation = alignment[first]
        moved = relabel(second, permutation)
        return kind, min(relabel(moved, symmetry) for symmetry in stabilizers[kind])

    def unordered_key(first, second):
        return min(ordered_key(first, second), ordered_key(second, first))

    all_orbits = Counter(
        unordered_key(first, second)
        for first in edge_branches[0]
        for second in edge_branches[1]
    )
    if len(all_orbits) != 2145 or Counter(all_orbits.values()) != Counter({2: 2080, 1: 65}):
        raise AssertionError("wrong S8 cross-branch pair-orbit census")

    overlap_orbits = Counter(
        unordered_key(first, second)
        for first in edge_branches[0]
        for second in edge_branches[1]
        if len(set(first) & set(second)) == 1
    )
    if len(overlap_orbits) != 121 or Counter(overlap_orbits.values()) != Counter({2: 114, 1: 7}):
        raise AssertionError("wrong S8 overlapping-pair orbit census")


def connected_mask(mask):
    edges = ((0, 1), (1, 2), (2, 3), (3, 0))
    vertices = {vertex for vertex in range(4) if mask & (1 << vertex)}
    if not vertices:
        return True
    seen = {min(vertices)}
    while True:
        expanded = seen | {
            right for left, right in edges if left in seen and right in vertices
        } | {
            left for left, right in edges if right in seen and left in vertices
        }
        if expanded == seen:
            return seen == vertices
        seen = expanded


def verify_signature_diamond(certificate):
    patterns = Counter(map(int, certificate["signature_pattern"]))
    expected = Counter({15: 25_968, 3: 72, 6: 72, 9: 72, 12: 72})
    if patterns != expected:
        raise AssertionError(f"wrong row-node signature patterns {patterns}")

    feasible_generators = {3, 6, 9, 12}
    intersection_closure = {15}
    for pattern in feasible_generators:
        intersection_closure |= {
            old & pattern for old in tuple(intersection_closure)
        }
    if intersection_closure != {0, 1, 2, 3, 4, 6, 8, 9, 12, 15}:
        raise AssertionError("wrong feasible intersection closure")
    if any(mask and not connected_mask(mask) for mask in intersection_closure):
        raise AssertionError("a local common-feasibility support is disconnected")

    bad_generators = {15 ^ pattern for pattern in feasible_generators}
    union_closure = {0}
    for pattern in bad_generators:
        union_closure |= {old | pattern for old in tuple(union_closure)}
    if union_closure != {0, 3, 6, 7, 9, 11, 12, 13, 14, 15}:
        raise AssertionError("wrong bad-locus union closure")
    if any(mask and not connected_mask(mask) for mask in union_closure):
        raise AssertionError("a local bad-locus union support is disconnected")


def boundary_degree(*brackets):
    return tuple(
        sum(str(label) in bracket for bracket in brackets)
        for label in range(1, 9)
    )


def verify_normalized_grading_no_go():
    homogeneous = set()
    for kind, (first, second, third, fourth) in BINOMIALS.items():
        if boundary_degree(first, second) == boundary_degree(third, fourth):
            homogeneous.add(kind)
    if homogeneous != {42}:
        raise AssertionError(f"wrong normalized homogeneous residual types {homogeneous}")

    trinomial_degrees = tuple(
        boundary_degree(first, second)
        for _, first, second in TRINOMIAL_51
    )
    if len(set(trinomial_degrees)) == 1:
        raise AssertionError("normalized type-51 identity unexpectedly has one Z8 degree")


def residual_degree_census():
    by_type = defaultdict(set)
    labeled = 0
    for fourset in combinations(range(len(koszul.TRIPLES)), 4):
        kind = koszul.wall_orbit(fourset)
        if kind not in koszul.RESIDUAL:
            continue
        degree = [0] * 8
        for normal in fourset:
            for label in koszul.TRIPLES[normal]:
                degree[label - 1] += 1
        by_type[kind].add(tuple(degree))
        labeled += 1
    counts = {kind: len(values) for kind, values in by_type.items()}
    if labeled != 84_840 or counts != EXPECTED_DEGREE_COUNTS:
        raise AssertionError("wrong labeled residual degree census")
    if len(set().union(*by_type.values())) != 1_554:
        raise AssertionError("wrong global residual Z8-degree count")


def normalized_brackets():
    one, zero = logbin.constant(1), logbin.constant(0)
    a, b, c, d, e, f, g, h, i = (
        logbin.variable(index) for index in range(9)
    )
    matrix = (
        (one, zero, zero, zero, one, one, one, one),
        (zero, one, zero, zero, one, a, d, g),
        (zero, zero, one, zero, one, b, e, h),
        (zero, zero, zero, one, one, c, f, i),
    )
    return {
        basis: logbin.determinant(
            tuple(tuple(matrix[row][column] for column in basis) for row in range(4))
        )
        for basis in combinations(range(8), 4)
    }


def permutation_sign(values):
    inversions = sum(
        values[left] > values[right]
        for left in range(len(values))
        for right in range(left + 1, len(values))
    )
    return -1 if inversions & 1 else 1


def verify_type42_cluster_orbit():
    brackets = normalized_brackets()

    def product(first, second):
        return logbin.multiply(brackets[tuple(first)], brackets[tuple(second)])

    q42 = logbin.subtract(
        product((0, 2, 4, 5), (1, 3, 6, 7)),
        product((0, 3, 6, 7), (1, 2, 4, 5)),
    )
    # The standard full-support quadratic Gr(4,8) cluster polynomial.
    cluster_terms = (
        (1, (0, 1, 2, 3), (4, 5, 6, 7)),
        (-1, (0, 1, 2, 4), (3, 5, 6, 7)),
        (1, (0, 1, 2, 5), (3, 4, 6, 7)),
    )

    def relabeled(permutation):
        result = {}
        for coefficient, first, second in cluster_terms:
            moved_first = tuple(permutation[index] for index in first)
            moved_second = tuple(permutation[index] for index in second)
            sign = permutation_sign(moved_first) * permutation_sign(moved_second)
            term = product(sorted(moved_first), sorted(moved_second))
            result = logbin.add(
                result,
                {
                    monomial: coefficient * sign * value
                    for monomial, value in term.items()
                },
            )
        return result

    dihedral = []
    for shift in range(8):
        dihedral.append(tuple((label + shift) % 8 for label in range(8)))
        dihedral.append(tuple((shift - label) % 8 for label in range(8)))
    if any(
        value == q42 or value == logbin.negative(q42)
        for value in map(relabeled, dihedral)
    ):
        raise AssertionError("type 42 is unexpectedly a cyclic cluster relabel")

    all_matches = sum(
        value == q42 or value == logbin.negative(q42)
        for value in map(relabeled, permutations(range(8)))
    )
    if all_matches != 144:
        raise AssertionError("wrong arbitrary-S8 type-42 cluster-polynomial orbit")


def verify_integral_square_filler():
    # Boundary of an oriented square with cyclic edges e01,e12,e23,e30.
    d2 = ((1,), (1,), (1,), (1,))
    d1 = (
        (-1, 0, 0, 1),
        (1, -1, 0, 0),
        (0, 1, -1, 0),
        (0, 0, 1, -1),
    )
    composite = tuple(
        sum(d1[row][column] * d2[column][0] for column in range(4))
        for row in range(4)
    )
    if composite != (0, 0, 0, 0):
        raise AssertionError("square filler boundary does not square to zero")
    if koszul.matrix_rank(d1) != 3 or koszul.matrix_rank(d2) != 1:
        raise AssertionError("integral square filler is not an acyclic disk")


def main():
    certificate = np.load(NODE, allow_pickle=False)
    branches = verify_node_supports(certificate)
    orbit_pair_census(branches)
    verify_signature_diamond(certificate)
    verify_normalized_grading_no_go()
    residual_degree_census()
    verify_type42_cluster_orbit()
    verify_integral_square_filler()

    print("PASS: each row-2599 branch has the exact 7-type 65-wall census")
    print("PASS: 3,990 disjoint and 235 one-overlap cross-branch pairs")
    print("PASS: 2,145 S8 pair orbits; 121 overlap orbits")
    print("PASS: every local feasibility intersection and bad union is a disk or empty")
    print("PASS: normalized residual identities fail Z8 cluster grading except type 42")
    print("PASS: type 42 is S8-related but not dihedrally related to the cyclic cluster variable")
    print("PASS: 84,840 residuals have 1,554 distinct global Z8 degrees")
    print("THEOREM: the exact row-2599 two-wall node has a commuting base diamond")
    print("NO-GO: cluster square/pentagon coherence is not universal for residual walls")
    print("SCOPE: the support-carried fiber diamond remains conditional")


if __name__ == "__main__":
    main()
