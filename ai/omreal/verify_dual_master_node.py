#!/usr/bin/env python3
"""Independent topological replay of the row-2599 transverse-node labels.

The geometry and exact derived topes are reconstructed by
``DIAG9_GRAPH_verify_row2599_node.py``.  This verifier deliberately imports
none of that code.  It reads the stored exact label artifact, rechecks its
lower-stratum gluing, and proves that every finite common-feasibility locus
on the certified disk is empty or an intersection of affine halfspaces with
the disk, hence convex and contractible.

This is a local codimension-two regression for the dual master-cell program.
It is not a global 9DVL verdict.
"""

from __future__ import annotations

from collections import Counter
from fractions import Fraction
from itertools import combinations
from pathlib import Path

import numpy as np


HERE = Path(__file__).resolve().parent
CERTIFICATE = HERE / "data" / "DIAG9_GRAPH_row2599_node_roadmap.npz"
FORMAT = "diag9-row2599-transverse-node-v1"

# The four open chambers have these (q_0,q_1) signs in cyclic order.
CELL_SIGNS = ((1, 1), (1, -1), (-1, -1), (-1, 1))

# The stored wall order is fixed by the original exact certificate format.
WALL_ADJACENCY = ((0, 3), (1, 2), (2, 3), (0, 1))

FULL_MASK = (1 << len(CELL_SIGNS)) - 1
HALFSPACE_MASK = {
    (0, 1): 0b0011,
    (0, -1): 0b1100,
    (1, 1): 0b1001,
    (1, -1): 0b0110,
}
EXPECTED_MULTIPLICITY = Counter(
    {0b1111: 25_968, 0b0011: 72, 0b0110: 72, 0b1100: 72, 0b1001: 72}
)


def fraction(certificate, prefix):
    return Fraction(
        int(certificate[f"{prefix}_num"].item()),
        int(certificate[f"{prefix}_den"].item()),
    )


def intersection(sets):
    sets = tuple(sets)
    if not sets:
        return set()
    return set.intersection(*(set(value) for value in sets))


def signature_patterns(cells):
    patterns = {}
    for cell_index, labels in enumerate(cells):
        for signature in labels:
            patterns[signature] = patterns.get(signature, 0) | (1 << cell_index)
    return patterns


def closure(generators):
    answer = {FULL_MASK}
    for generator in generators:
        answer |= {old & generator for old in tuple(answer)}
    return answer


def mask_from_constraints(constraints):
    signs = {}
    for coordinate, wanted in constraints:
        old = signs.get(coordinate)
        if old is not None and old != wanted:
            return 0
        signs[coordinate] = wanted
    mask = 0
    for cell_index, cell_signs in enumerate(CELL_SIGNS):
        if all(cell_signs[coordinate] == wanted for coordinate, wanted in signs.items()):
            mask |= 1 << cell_index
    return mask


def verify_halfspace_closure(proper_masks):
    expected = set(HALFSPACE_MASK.values())
    if set(proper_masks) != expected:
        raise AssertionError("proper supports are not the four affine halfspaces")

    generators = tuple(HALFSPACE_MASK.items())
    observed = {FULL_MASK}
    for subset_mask in range(1 << len(generators)):
        constraints = []
        chamber_mask = FULL_MASK
        for generator_index, (constraint, generator_mask) in enumerate(generators):
            if (subset_mask >> generator_index) & 1:
                constraints.append(constraint)
                chamber_mask &= generator_mask
        expected_mask = mask_from_constraints(constraints)
        if chamber_mask != expected_mask:
            raise AssertionError("mask intersection disagrees with strict halfspaces")
        observed.add(chamber_mask)

    expected_closure = {0, 1, 2, 3, 4, 6, 8, 9, 12, 15}
    if observed != expected_closure:
        raise AssertionError("wrong affine-halfspace intersection closure")
    return tuple(sorted(observed))


def verify_labels(cells, walls, node):
    if tuple(map(len, cells)) != (26_112,) * 4:
        raise AssertionError("wrong chamber tope counts")
    if tuple(map(len, walls)) != (26_040,) * 4:
        raise AssertionError("wrong wall tope counts")
    if len(node) != 25_968:
        raise AssertionError("wrong node tope count")

    for wall, (left, right) in zip(walls, WALL_ADJACENCY):
        if set(wall) != set(cells[left]) & set(cells[right]):
            raise AssertionError("wall labels are not adjacent-chamber intersections")
    if set(node) != intersection(cells):
        raise AssertionError("node label is not the four-chamber intersection")
    if any(set(node) != set(left) & set(right) for left, right in combinations(walls, 2)):
        raise AssertionError("node label is not every two-wall intersection")

    patterns = signature_patterns(cells)
    if Counter(patterns.values()) != EXPECTED_MULTIPLICITY:
        raise AssertionError("wrong chamber-support multiplicities")
    proper = tuple(sorted(set(patterns.values()) - {FULL_MASK}))
    halfspace_closure = verify_halfspace_closure(proper)
    if closure(set(patterns.values())) != set(halfspace_closure):
        raise AssertionError("signature intersections exceed the halfspace closure")
    return patterns, halfspace_closure


def expect_failure(function, *args):
    try:
        function(*args)
    except AssertionError:
        return
    raise AssertionError("deliberately invalid canary was accepted")


def run_canaries(cells, walls, node):
    # A diagonal two-chamber support is not one affine branch halfspace.
    expect_failure(verify_halfspace_closure, (3, 5, 6, 9, 12))

    # Adding a chamber-only label to a nonincident wall must break gluing.
    corrupted = [set(value) for value in walls]
    chamber_only = next(iter(set(cells[0]) - set(cells[3])))
    corrupted[0].add(chamber_only)
    expect_failure(verify_labels, cells, tuple(corrupted), node)


def main():
    certificate = np.load(CERTIFICATE, allow_pickle=False)
    if str(certificate["format"].item()) != FORMAT:
        raise AssertionError("wrong certificate format")

    center_s = fraction(certificate, "center_s")
    center_u = fraction(certificate, "center_u")
    branches = tuple(tuple(map(int, row)) for row in certificate["branch_affine"])
    if len(branches) != 2:
        raise AssertionError("expected exactly two affine branches")
    for constant, s_coefficient, u_coefficient in branches:
        if constant + s_coefficient * center_s + u_coefficient * center_u != 0:
            raise AssertionError("stored branch misses the exact node")
    jacobian = branches[0][1] * branches[1][2] - branches[0][2] * branches[1][1]
    if jacobian == 0 or jacobian != int(certificate["jacobian"].item()):
        raise AssertionError("stored branches are not exactly transverse")

    for prefix in ("other_margin", "branch0_margin", "branch1_margin", "bracket_margin"):
        if fraction(certificate, prefix) <= 1:
            raise AssertionError(f"{prefix} does not certify nonvanishing")

    cells = tuple(tuple(map(int, row)) for row in certificate["cell_tope"])
    walls = tuple(tuple(map(int, row)) for row in certificate["wall_tope"])
    node = tuple(map(int, certificate["node_tope"]))
    patterns, halfspace_closure = verify_labels(cells, walls, node)

    signatures = tuple(map(int, certificate["signature"]))
    if signatures != tuple(sorted(patterns)):
        raise AssertionError("stored signature union disagrees")
    stored_patterns = tuple(map(int, certificate["signature_pattern"]))
    if stored_patterns != tuple(patterns[signature] for signature in signatures):
        raise AssertionError("stored signature masks disagree")
    if tuple(map(int, certificate["intersection_closure"])) != halfspace_closure:
        raise AssertionError("stored intersection closure disagrees")
    if len(certificate["disconnected_closure"]):
        raise AssertionError("stored artifact claims a disconnected intersection")

    run_canaries(cells, walls, node)

    print("PASS: two exact affine branches are transverse at the stored node")
    print("PASS: exact chamber, wall, and node labels satisfy all gluing identities")
    print("PASS: individual proper supports are exactly the four strict halfspaces")
    print("PASS: diagonal-mask and corrupted-wall canaries are rejected")
    print(f"PASS: all-family intersection closure {halfspace_closure}")
    print("THEOREM: every finite common-feasibility locus on the disk is empty or convex")
    print("SCOPE: local row-2599 disk; no global 9DVL diagonal is claimed")


if __name__ == "__main__":
    main()
