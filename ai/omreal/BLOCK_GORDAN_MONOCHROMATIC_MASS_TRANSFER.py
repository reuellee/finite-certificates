#!/usr/bin/env python3
"""Exact audit of monochromatic block-mass transfer and common-wall escape.

The support part checks that every individual positive residual-wall circuit
has three or four derived normals and therefore has a parent label of degree
at most one.  The row-2599 part gives
an actual proper pairwise-incomparable triple for which all three blocks die
across the same wall.  Hence partner-block transfer is genuinely unavailable,
while the common wall circuit supplies the pencil escape.
"""

from itertools import combinations
from pathlib import Path
import sys

import numpy as np


HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import BLOCK_GORDAN_MONOCHROMATIC_WALL_STARS as stars  # noqa: E402
import DIAG9_GRAPH_exact_topes as topes  # noqa: E402
import DIAG9_GRAPH_verify_row2599_node as node  # noqa: E402


SIGNATURES = (
    448607715549184,
    3826331369078784,
    31604296963587053,
)
SAMPLE_CHARTS = (1, 3, 4, 5)
EXPECTED_MASKS = (0b1010, 0b0100, 0b1001)
COMMON_WALL_CIRCUIT = (0, 18, 40)


def verify_universal_light_wall_circuit():
    degrees = {}
    for kind in sorted(stars.koszul.RESIDUAL):
        circuit = stars.wall_circuit(kind)
        if len(circuit) not in (3, 4):
            raise AssertionError("residual wall circuit has the wrong size")
        degree = stars.support_degree(circuit)
        if sum(degree) != 3 * len(circuit):
            raise AssertionError("wall-circuit incidence count changed")
        if min(degree) > 1:
            raise AssertionError("wall circuit has no degree-at-most-one label")
        degrees[kind] = degree
    return degrees


def verify_exact_antichain_masks():
    source = np.load(
        HERE / "data" / "seeat_parent2599_upper178.npz",
        allow_pickle=False,
    )
    chart_tope_sets = tuple(
        set(
            topes.parent_topes(
                source["chart_matrix"][chart_index], verify=False
            )
        )
        for chart_index in SAMPLE_CHARTS
    )
    masks = []
    for signature in SIGNATURES:
        mask = 0
        for bit, chart_topes in enumerate(chart_tope_sets):
            if signature in chart_topes:
                mask |= 1 << bit
        masks.append(mask)
    if tuple(masks) != EXPECTED_MASKS:
        raise AssertionError("exact four-chart masks changed")
    for left, right in combinations(masks, 2):
        if not (left & ~right and right & ~left):
            raise AssertionError("sample masks do not certify incomparability")
    return tuple(masks)


def verify_simultaneous_monochromatic_loss():
    certificate = np.load(node.ROADMAP, allow_pickle=False)
    patterns = {
        int(signature): int(pattern)
        for signature, pattern in zip(
            certificate["signature"],
            certificate["signature_pattern"],
            strict=True,
        )
    }
    if tuple(patterns.get(signature) for signature in SIGNATURES) != (3, 3, 3):
        raise AssertionError("selected signatures do not share node pattern 0011")

    wall_parent = node.rational_parent(*node.wall_points()[0])
    bad_parent = node.rational_parent(*node.cell_points()[3])
    feasible_parent = node.rational_parent(*node.cell_points()[0])
    expected_parent = topes.parent_signs(wall_parent)
    if topes.parent_signs(bad_parent) != expected_parent:
        raise AssertionError("bad-side sample leaves parent cell 2599")
    if topes.parent_signs(feasible_parent) != expected_parent:
        raise AssertionError("feasible-side sample leaves parent cell 2599")

    wall_normals = topes.derived_rows(wall_parent, normalize=False)
    bad_normals = topes.derived_rows(bad_parent, normalize=False)
    feasible_normals = topes.derived_rows(feasible_parent, normalize=False)
    counts = []
    for signature in SIGNATURES:
        if not stars.positive_circuit(
            wall_normals, signature, COMMON_WALL_CIRCUIT
        ):
            raise AssertionError("common wall circuit is not positive")
        bad_count = 0
        feasible_count = 0
        for auxiliary in range(56):
            if auxiliary in COMMON_WALL_CIRCUIT:
                continue
            support = tuple(sorted(COMMON_WALL_CIRCUIT + (auxiliary,)))
            bad_count += stars.positive_circuit(
                bad_normals, signature, support
            )
            feasible_count += stars.positive_circuit(
                feasible_normals, signature, support
            )
        if (bad_count, feasible_count) != (18, 0):
            raise AssertionError("monochromatic auxiliary count changed")
        counts.append((bad_count, feasible_count))

    degree = stars.support_degree(COMMON_WALL_CIRCUIT)
    if degree != (1, 1, 3, 1, 1, 1, 0, 1):
        raise AssertionError("common wall support degree changed")
    return degree, tuple(counts)


def verify_block_mass_chain_algebra():
    # Three coincident dying blocks have the ordinary augmented-simplex
    # incidence.  These are the singleton-to-pair and pair-to-triple maps.
    d0 = (
        (-1, 1, 0),
        (-1, 0, 1),
        (0, -1, 1),
    )
    d1 = ((1, -1, 1),)
    product = tuple(
        sum(d1[0][middle] * d0[middle][column] for middle in range(3))
        for column in range(3)
    )
    if product != (0, 0, 0):
        raise AssertionError("Cech incidence does not square to zero")
    # d1 is onto over Z and ker(d1) is generated by the first two columns of
    # d0; the displayed 2x2 determinant is a unit.
    determinant = d0[0][0] * d0[1][1] - d0[0][1] * d0[1][0]
    if determinant not in (-1, 1) or 1 not in tuple(map(abs, d1[0])):
        raise AssertionError("augmented simplex complex is not integrally exact")


def main():
    degrees = verify_universal_light_wall_circuit()
    masks = verify_exact_antichain_masks()
    degree, counts = verify_simultaneous_monochromatic_loss()
    verify_block_mass_chain_algebra()
    print("PASS: every residual wall circuit has a degree-at-most-one label")
    print("PASS: residual wall support degrees=" + str(degrees))
    print("PASS: exact row-2599 triple masks=" + str(masks))
    print("PASS: the three proper regions are pairwise incomparable")
    print("PASS: all three blocks share positive wall circuit (0,18,40)")
    print("PASS: common support degree=" + str(degree))
    print("PASS: bad/feasible auxiliary counts=" + str(counts))
    print("PASS: coincident-loss block incidence is integrally acyclic")
    print("THEOREM: the row-2599 all-block loss has a common pencil escape")
    print("SCOPE: partner transfer is universal; a common wall circuit is not yet universal")


if __name__ == "__main__":
    main()
