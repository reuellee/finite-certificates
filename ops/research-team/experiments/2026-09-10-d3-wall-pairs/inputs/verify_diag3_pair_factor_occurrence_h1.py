#!/usr/bin/env python3
"""Exact same-factor occurrence-support H1 audit for diagonal three.

At a generic primitive factor wall, retain the circuit supports supplied by
all labeled occurrences of that factor.  Two supports span an occurrence
edge when their union has at most six normals; three span a triangle when
all three edges exist and their union has at most seven normals.  This is
the support bound for the single-block witness two-skeleton.

The checker proves that the common active occurrence complex for one or two
arbitrary block signings has integral H1=0 for all six factor kinds.  It also
pins a realizable rank-three countermodel showing that the special rank-two
flat of kind 38, not generic oriented-matroid realizability, is essential.
No specialization or parent-infinity incidence is asserted.
"""

from __future__ import annotations

from itertools import combinations
from pathlib import Path
import sys


HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import BLOCK_GORDAN_MONOCHROMATIC_WALL_STARS as wall_stars  # noqa: E402
import DIAG2_PIVOT_LABELED_PAIR_ORBITS_VERIFY as labeled  # noqa: E402
import DIAG9_GRAPH_exact_topes as exact_topes  # noqa: E402
import prototype_koszul_circuits as koszul  # noqa: E402
import verify_diag2_canonical_robust_edges as robust  # noqa: E402


MULTIPLE_KINDS = (36, 38, 48)
SINGLETON_KINDS = (49, 50, 51)
EXPECTED_SUPPORT_COUNTS = {36: 31, 38: 15, 48: 2}


def occurrence_supports():
    occurrences, occurrence_factor, factor_polynomials = labeled.factor_polynomials()
    factor_ids, canonical_polynomials = robust.canonical_data()
    if factor_polynomials != canonical_polynomials:
        raise AssertionError("global factor polynomial order changed")
    answer = {}
    for kind in MULTIPLE_KINDS:
        witness = robust.construct_witness(kind, factor_ids, factor_polynomials)
        normals = exact_topes.derived_rows(
            robust.integer_matrix(witness.center), normalize=False
        )
        members = (
            occurrence
            for occurrence in occurrences
            if occurrence_factor[occurrence] == factor_ids[kind]
        )
        supports = tuple(
            sorted(
                {
                    wall_stars.node_wall_circuit(occurrence, normals)
                    for occurrence in members
                }
            )
        )
        if len(supports) != EXPECTED_SUPPORT_COUNTS[kind]:
            raise AssertionError(f"kind {kind} occurrence support count changed")
        answer[kind] = (supports, normals)
    for kind in SINGLETON_KINDS:
        members = tuple(
            occurrence
            for occurrence in occurrences
            if occurrence_factor[occurrence] == factor_ids[kind]
        )
        if len(members) != 1:
            raise AssertionError(f"kind {kind} is no longer a singleton occurrence")
    return answer


def verify_kind36(supports) -> None:
    """Every induced occurrence subcomplex is a union of simplex 2-skeleta."""

    central = tuple(support for support in supports if len(support) == 3)
    if central != ((0, 9, 32),):
        raise AssertionError("kind-36 central support changed")
    central_set = set(central[0])
    families = []
    for omitted in central[0]:
        core = central_set - {omitted}
        family = tuple(
            support
            for support in supports
            if len(support) == 4
            and core.issubset(support)
            and omitted not in support
        )
        if len(family) != 10:
            raise AssertionError("kind-36 support family is not K5 choose 2")
        outer = set().union(*(set(support) - core for support in family))
        if len(outer) != 5 or {
            frozenset(set(support) - core) for support in family
        } != {frozenset(pair) for pair in combinations(outer, 2)}:
            raise AssertionError("kind-36 support family lost its K5 structure")
        if any(len(set(left) | set(right)) > 6 for left, right in combinations(family, 2)):
            raise AssertionError("kind-36 family lost a witness edge")
        if any(
            len(set().union(*map(set, triple))) > 7
            for triple in combinations(family, 3)
        ):
            raise AssertionError("kind-36 family lost a witness triangle")
        if any(len(central_set | set(support)) > 6 for support in family):
            raise AssertionError("kind-36 central support lost a family edge")
        if any(
            len(central_set | set(left) | set(right)) > 7
            for left, right in combinations(family, 2)
        ):
            raise AssertionError("kind-36 central cone lost a triangle")
        families.append(family)
    if set().union(*map(set, families)) != set(supports) - set(central):
        raise AssertionError("kind-36 families do not cover all occurrences")
    for first, second in combinations(families, 2):
        if any(len(set(left) | set(right)) <= 6 for left in first for right in second):
            raise AssertionError("kind-36 distinct families acquired a cross edge")


def verify_kind48(supports) -> None:
    if len(set(supports[0]) | set(supports[1])) != 8:
        raise AssertionError("kind-48 disjoint occurrence canary changed")


OUTER_EDGES = tuple(combinations(range(6), 2))


def line_pattern(cut: int, signing: int) -> int:
    """Positive kind-38 occurrence edges in the rank-two-flat normal form."""

    mask = 0
    for index, (left, right) in enumerate(OUTER_EDGES):
        left_sign = 1 if signing >> left & 1 else -1
        right_sign = 1 if signing >> right & 1 else -1
        if right < cut:
            active = left_sign == 1 and right_sign == -1
        elif left >= cut:
            active = left_sign == -1 and right_sign == 1
        else:
            active = left_sign == -1 and right_sign == -1
        if active:
            mask |= 1 << index
    return mask


def active_indices(mask: int):
    return tuple(index for index in range(15) if mask >> index & 1)


def verify_unit_triangle_fillers(mask: int) -> int:
    """Fill every missing matching triangle by three unit triangles."""

    matching = 0
    active = active_indices(mask)
    for triple in combinations(active, 3):
        endpoints = set().union(*(set(OUTER_EDGES[index]) for index in triple))
        if len(endpoints) != 6:
            continue
        matching += 1
        filler = next(
            (index for index in active if index not in triple),
            None,
        )
        if filler is None:
            raise AssertionError(
                "a common active perfect matching has no unit triangle filler"
            )
        # Any fourth edge on the same six vertices joins two matching edges.
        # Hence each of (a,b,f), (b,c,f), (c,a,f) has at most five endpoints
        # and is an allowed support triangle.  The tetrahedron boundary
        # identity fills the missing (a,b,c) boundary over Z.
        for left, right in combinations(triple, 2):
            union = set(OUTER_EDGES[left]) | set(OUTER_EDGES[right]) | set(
                OUTER_EDGES[filler]
            )
            if len(union) > 5:
                raise AssertionError("the proposed unit filler is not a triangle")
    return matching


def verify_kind38(supports, normals) -> tuple[int, int, int]:
    core = set.intersection(*(set(support) for support in supports))
    if core != {9, 55}:
        raise AssertionError("kind-38 common core changed")
    outer_normals = sorted(set().union(*map(set, supports)) - core)
    if len(outer_normals) != 6:
        raise AssertionError("kind-38 outer-normal count changed")
    outer_pairs = {
        frozenset(set(support) - core) for support in supports
    }
    if outer_pairs != {
        frozenset(pair) for pair in combinations(outer_normals, 2)
    }:
        raise AssertionError("kind-38 supports are not all outer pairs")
    common_parent_line = set.intersection(
        *(set(koszul.TRIPLES[index]) for index in outer_normals)
    )
    if common_parent_line != {1, 2}:
        raise AssertionError("kind-38 six-normal rank-two flat changed")
    if any(len(set(left) | set(right)) > 6 for left, right in combinations(supports, 2)):
        raise AssertionError("kind-38 occurrence graph is not complete")

    all_single = set()
    all_common = set()
    matching_cycles = 0
    for cut in range(7):
        patterns = {line_pattern(cut, signing) for signing in range(64)}
        if len(patterns) != 58:
            raise AssertionError("wrong one-block kind-38 line-pattern count")
        common_patterns = {left & right for left in patterns for right in patterns}
        if len(common_patterns) != 180:
            raise AssertionError("wrong two-block kind-38 intersection count")
        for mask in common_patterns:
            matching_cycles += verify_unit_triangle_fillers(mask)
        all_single.update(patterns)
        all_common.update(common_patterns)
    if (len(all_single), len(all_common), matching_cycles) != (172, 487, 105):
        raise AssertionError("kind-38 universal line census changed")

    # Anchor the universal line normal form to the exact canonical factor
    # wall.  In its projective line order the outer normals are as below and
    # the core-difference ray lies in gap one.  Direct positive-circuit
    # enumeration over all eight signing bits must give precisely the same
    # 58 support patterns as the symbolic line rule.
    line_order = (0, 4, 10, 35, 1, 20)
    pair_index = {
        frozenset(set(support) - core): index
        for index, support in enumerate(supports)
    }
    expected_patterns = set()
    for signing in range(64):
        line_mask = line_pattern(1, signing)
        support_mask = 0
        for edge_index, (left, right) in enumerate(OUTER_EDGES):
            if line_mask >> edge_index & 1:
                support_mask |= 1 << pair_index[
                    frozenset((line_order[left], line_order[right]))
                ]
        expected_patterns.add(support_mask)
    signed_normals = sorted(core | set(outer_normals))
    signing_position = {normal: index for index, normal in enumerate(signed_normals)}
    direct_patterns = set()
    for signing in range(1 << len(signed_normals)):
        signature = sum(
            ((signing >> signing_position[normal]) & 1) << normal
            for normal in signed_normals
        )
        direct_patterns.add(
            sum(
                (1 << index)
                for index, support in enumerate(supports)
                if wall_stars.positive_circuit(normals, signature, support)
            )
        )
    if direct_patterns != expected_patterns or len(direct_patterns) != 58:
        raise AssertionError("kind-38 exact wall does not match the line normal form")
    return len(all_single), len(all_common), matching_cycles


def determinant3(columns) -> int:
    a, b, c = columns
    return (
        a[0] * (b[1] * c[2] - b[2] * c[1])
        - b[0] * (a[1] * c[2] - a[2] * c[1])
        + c[0] * (a[1] * b[2] - a[2] * b[1])
    )


def positive_four_circuit(matrix, support, reorientation: int) -> bool:
    coefficients = []
    for omitted, label in enumerate(support):
        columns = tuple(
            tuple(matrix[row][other] for row in range(3))
            for other in support
            if other != label
        )
        coefficient = (-1 if omitted & 1 else 1) * determinant3(columns)
        if reorientation >> label & 1:
            coefficient = -coefficient
        coefficients.append(coefficient)
    return all(value > 0 for value in coefficients) or all(
        value < 0 for value in coefficients
    )


def generic_rank3_countermodel() -> None:
    """Realizability alone permits the unfilled three-matching cycle."""

    matrix = (
        (1, 0, 0, 1, -8, -2, 8, 8),
        (0, 1, 0, -1, -8, -8, 4, 1),
        (0, 0, 1, 1, 3, 1, 7, 6),
    )
    if any(
        determinant3(
            tuple(tuple(matrix[row][label] for row in range(3)) for label in triple)
        )
        == 0
        for triple in combinations(range(8), 3)
    ):
        raise AssertionError("rank-three countermodel is not uniform")
    core = (0, 1)
    reorientation = 85  # flip labels 0,2,4,6
    outer = tuple(range(2, 8))
    active = tuple(
        pair
        for pair in combinations(outer, 2)
        if positive_four_circuit(
            matrix, tuple(sorted(core + pair)), reorientation
        )
    )
    if active != ((2, 3), (4, 5), (6, 7)):
        raise AssertionError("generic rank-three matching canary changed")
    # The three support vertices have all three pair edges (union size six),
    # but no triangle (union size eight), so their integral H1 is Z.
    supports = tuple(tuple(sorted(core + pair)) for pair in active)
    if any(len(set(left) | set(right)) != 6 for left, right in combinations(supports, 2)):
        raise AssertionError("rank-three canary lost a cycle edge")
    if len(set().union(*map(set, supports))) != 8:
        raise AssertionError("rank-three canary unexpectedly acquired a triangle")


def main() -> None:
    records = occurrence_supports()
    verify_kind36(records[36][0])
    single, common, matching = verify_kind38(*records[38])
    verify_kind48(records[48][0])
    generic_rank3_countermodel()
    print("PASS kind36 every active induced occurrence complex has unit H1=0")
    print(
        "PASS kind38 rank-two-flat line census:",
        single,
        "one-block patterns,",
        common,
        "two-block patterns,",
        matching,
        "matching cycles unit-filled",
    )
    print("PASS kind48 and singleton factor kinds have no occurrence H1")
    print("NO-GO generic realizable rank three permits an unfilled matching H1=Z")
    print("SCOPE generic same-factor occurrence supports; no specialization/infinity/beta rank")


if __name__ == "__main__":
    main()
