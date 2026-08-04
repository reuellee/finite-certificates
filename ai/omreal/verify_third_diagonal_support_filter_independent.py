#!/usr/bin/env python3
"""Independent exact audit of ``verify_third_diagonal_support_filter.cpp``.

This checker deliberately does not import any of the project classifiers and
does not use the C++ checker's table of thirteen residual orbit indices.  It
reconstructs the calculation as follows.

* The 52 orbits of four triples are obtained directly from the S_8 action.
* A fresh symbolic 4-by-8 chart classifies each orbit determinant as zero, a
  product of localized parent-bracket factors, or genuinely residual.
* Five-support genericity is tested with packed integer degree and codegree
  counters, while the common-apex ``delta`` test uses ordered forbidden-edge
  masks.
* Survivor orbits are recomputed with NumPy group actions, and ``beta`` is the
  exact rational rank of the centered incidence matrix computed by SymPy.

Thus the implementation, triple order, residual classification, genericity
test, and rank routine are independent of the C++ verifier.  The two programs
share only the mathematical definitions being audited.
"""

from collections import Counter
from itertools import combinations, permutations

import numpy as np
import sympy as sp


TRIPLES = tuple(combinations(range(8), 3))
TRIPLE_INDEX = {triple: index for index, triple in enumerate(TRIPLES)}
EDGE_BITS = tuple(1 << index for index in range(56))


def build_group_action():
    """Return all 40,320 label permutations on the 56 triples."""
    maps = np.empty((40_320, 56), dtype=np.uint8)
    for row, permutation in enumerate(permutations(range(8))):
        maps[row] = [
            TRIPLE_INDEX[tuple(sorted(permutation[vertex] for vertex in triple))]
            for triple in TRIPLES
        ]
    assert row == 40_319
    return maps


def indices_of(mask):
    indices = []
    while mask:
        bit = mask & -mask
        indices.append(bit.bit_length() - 1)
        mask ^= bit
    return indices


def orbit_images(mask, bit_maps):
    """Compute one exact S_8 orbit as 56-bit integer masks."""
    columns = indices_of(mask)
    images = np.bitwise_or.reduce(bit_maps[:, columns], axis=1)
    return {int(image) for image in np.unique(images)}


def symbolic_wall_classifier():
    """Build an independent localization classifier for four-normal walls."""
    variables = sp.symbols("a b c d e f g h i")
    a, b, c, d, e, f, g, h, i = variables
    chart = sp.Matrix([
        [1, 0, 0, 0, 1, 1, 1, 1],
        [0, 1, 0, 0, 1, a, d, g],
        [0, 0, 1, 0, 1, b, e, h],
        [0, 0, 0, 1, 1, c, f, i],
    ])

    def normalize_factor(expression):
        return sp.Poly(expression, *variables, domain=sp.QQ).monic().as_expr()

    unit_factors = set()
    for basis in combinations(range(8), 4):
        bracket = sp.expand(chart[:, basis].det())
        assert bracket != 0
        _, factors = sp.factor_list(bracket, *variables)
        unit_factors.update(normalize_factor(factor) for factor, _ in factors)

    normals = []
    for triple in TRIPLES:
        columns = chart[:, triple]
        normals.append(sp.Matrix([
            (-1) ** (row + 3)
            * columns.extract(
                [other for other in range(4) if other != row], range(3)
            ).det()
            for row in range(4)
        ]))

    def classify(edge_indices):
        determinant = sp.expand(
            sp.Matrix.hstack(*(normals[index] for index in edge_indices)).det()
        )
        if determinant == 0:
            return "zero"
        _, factors = sp.factor_list(determinant, *variables)
        nonunits = [
            (normalize_factor(factor), exponent)
            for factor, exponent in factors
            if normalize_factor(factor) not in unit_factors
        ]
        if not nonunits:
            return "unit"
        # The result below is not assumed by the classification: assert the
        # empirically recovered residual is one square-free irreducible atom.
        assert len(nonunits) == 1 and nonunits[0][1] == 1
        return "residual"

    return classify


def structural_four(edge_indices):
    """The independent incidence criterion for an identically zero wall."""
    edges = [set(TRIPLES[index]) for index in edge_indices]
    if set.intersection(*edges):
        return True
    return any(
        sum(pair <= edge for edge in edges) >= 3
        for pair in map(set, combinations(range(8), 2))
    )


def classify_four_orbits(bit_maps):
    """Recover all four-support orbit types and all labeled residual walls."""
    classify_symbolically = symbolic_wall_classifier()
    remaining = {
        sum(EDGE_BITS[index] for index in support)
        for support in combinations(range(56), 4)
    }
    type_orbits = Counter()
    type_labeled = Counter()
    residual_four = set()

    while remaining:
        representative = remaining.pop()
        orbit = orbit_images(representative, bit_maps)
        assert orbit - {representative} <= remaining
        remaining.difference_update(orbit)
        indices = indices_of(representative)
        wall_type = classify_symbolically(indices)
        assert (wall_type == "zero") == structural_four(indices)
        type_orbits[wall_type] += 1
        type_labeled[wall_type] += len(orbit)
        if wall_type == "residual":
            residual_four.update(orbit)

    assert type_orbits == {"zero": 14, "unit": 25, "residual": 13}
    assert type_labeled == {
        "zero": 58_660,
        "unit": 223_790,
        "residual": 84_840,
    }
    assert len(residual_four) == 84_840
    return residual_four, type_orbits, type_labeled


# Three-bit fields have no carries because a five-support gives degrees at
# most five.  A field is >=4 exactly when its high bit is set; it is >=3 when
# either its high bit is set or both low bits are set.
VERTEX_CODES = tuple(sum(1 << (3 * vertex) for vertex in triple) for triple in TRIPLES)
VERTEX_MASKS = tuple(sum(1 << vertex for vertex in triple) for triple in TRIPLES)
VERTEX_HIGH = sum(1 << (3 * vertex + 2) for vertex in range(8))

PAIRS = tuple(combinations(range(8), 2))
PAIR_INDEX = {pair: index for index, pair in enumerate(PAIRS)}
PAIR_CODES = tuple(
    sum(1 << (3 * PAIR_INDEX[pair]) for pair in combinations(triple, 2))
    for triple in TRIPLES
)
PAIR_LOW = sum(1 << (3 * pair) for pair in range(28))
PAIR_HIGH = sum(1 << (3 * pair + 2) for pair in range(28))


def generic_five(indices):
    vertex_sum = sum(VERTEX_CODES[index] for index in indices)
    if vertex_sum & VERTEX_HIGH:
        return False
    pair_sum = sum(PAIR_CODES[index] for index in indices)
    return not (
        pair_sum & PAIR_HIGH
        or (pair_sum & PAIR_LOW) & ((pair_sum >> 1) & PAIR_LOW)
    )


FORBIDDEN = tuple(
    tuple(
        sum(
            EDGE_BITS[index]
            for index, triple in enumerate(TRIPLES)
            if moving in triple and apex not in triple
        )
        for moving in range(8)
    )
    for apex in range(8)
)


def delta_of(mask):
    best = 0
    for apex in range(8):
        dominated = 0
        for moving in range(8):
            if moving != apex and not mask & FORBIDDEN[apex][moving]:
                dominated += 1
        best = max(best, dominated)
        if best >= 3:
            return 3
    return best


def exact_beta(mask):
    indices = indices_of(mask)
    base = [int(vertex in TRIPLES[indices[0]]) for vertex in range(8)]
    rows = [
        [int(vertex in TRIPLES[index]) - base[vertex] for vertex in range(8)]
        for index in indices[1:]
    ]
    return 4 - sp.Matrix(rows).rank()


def support_census(residual_four):
    generic = 0
    covers = 0
    killed_delta = 0
    killed_unit = 0
    survivors = set()
    raw_strata = Counter()

    for indices in combinations(range(56), 5):
        if not generic_five(indices):
            continue
        generic += 1
        coverage = 0
        mask = 0
        for index in indices:
            coverage |= VERTEX_MASKS[index]
            mask |= EDGE_BITS[index]
        if coverage != 0xFF:
            continue
        covers += 1
        delta = delta_of(mask)
        if delta >= 3:
            killed_delta += 1
            continue
        residuals = sum(
            (mask ^ EDGE_BITS[index]) in residual_four for index in indices
        )
        if residuals == 0:
            killed_unit += 1
            continue
        raw_strata[delta, residuals] += 1
        survivors.add(mask)

    assert generic == 2_021_992
    assert covers == 1_099_560
    assert killed_delta == 339_360
    assert killed_unit == 0
    assert len(survivors) == 760_200
    return survivors, raw_strata, (generic, covers, killed_delta, killed_unit)


def survivor_orbits(survivors, residual_four, bit_maps):
    remaining = set(survivors)
    labeled = Counter()
    orbit_counts = Counter()
    beta_one_representatives = []

    while remaining:
        representative = remaining.pop()
        orbit = orbit_images(representative, bit_maps)
        assert orbit - {representative} <= remaining
        remaining.difference_update(orbit)
        delta = delta_of(representative)
        beta = exact_beta(representative)
        residuals = sum(
            (representative ^ EDGE_BITS[index]) in residual_four
            for index in indices_of(representative)
        )
        labeled[delta, beta, residuals] += len(orbit)
        orbit_counts[delta, beta] += 1
        if beta == 1:
            beta_one_representatives.append(representative)

    expected_labeled = {
        (1, 0, 3): 20_160,
        (1, 0, 4): 5_040,
        (1, 0, 5): 40_320,
        (2, 0, 1): 58_800,
        (2, 0, 2): 260_400,
        (2, 0, 3): 272_160,
        (2, 0, 4): 15_120,
        (2, 0, 5): 85_680,
        (2, 1, 4): 2_520,
    }
    assert labeled == expected_labeled
    assert orbit_counts == {(1, 0): 5, (2, 0): 39, (2, 1): 1}
    assert len(beta_one_representatives) == 1
    return labeled, orbit_counts, beta_one_representatives[0]


def support_text(mask):
    return "/".join(
        "".join(str(vertex + 1) for vertex in TRIPLES[index])
        for index in indices_of(mask)
    )


def main():
    group_maps = build_group_action()
    bit_maps = np.left_shift(np.uint64(1), group_maps.astype(np.uint64))
    residual_four, type_orbits, type_labeled = classify_four_orbits(bit_maps)
    survivors, raw_strata, totals = support_census(residual_four)
    labeled, orbit_counts, beta_one = survivor_orbits(
        survivors, residual_four, bit_maps
    )

    assert sum(raw_strata.values()) == sum(labeled.values()) == 760_200
    collapsed = Counter()
    for (delta, _beta, residuals), count in labeled.items():
        collapsed[delta, residuals] += count
    assert raw_strata == collapsed

    print(f"four-wall orbits={dict(type_orbits)} labeled={dict(type_labeled)}")
    print(
        "generic=%d covers=%d killed_delta=%d killed_all_unit=%d" % totals
    )
    for key in sorted(labeled):
        print(
            "labeled delta=%d beta=%d residuals=%d count=%d"
            % (*key, labeled[key])
        )
    for key in sorted(orbit_counts):
        print("orbits delta=%d beta=%d count=%d" % (*key, orbit_counts[key]))
    print("BETA1_REP_IN_LEX_TRIPLE_ORDER:", support_text(beta_one))
    print("SURVIVORS: labeled=760200 orbits=45")
    print("PASS: independent exact audit of third-diagonal support filter")


if __name__ == "__main__":
    main()
