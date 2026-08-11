#!/usr/bin/env python3
"""Exact bounded audit of the standard-Cremona diagonal-three frontier.

This verifier does not close any diagonal-three factor triple.  It classifies
the pullbacks of the 70 target parent brackets under coordinatewise
reciprocity and proves that the resulting internal frontiers are not
exceptional fibers of that map.  It also replays the six-hard-canary affine
no-go; ``--full`` adds the slower exact triangular-unit screen.
"""

from __future__ import annotations

import argparse
from collections import Counter
from fractions import Fraction
import hashlib
from itertools import combinations, permutations, product
import struct
from pathlib import Path
import sys


HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import DIAG2_PIVOT_LABELED_PAIR_ORBITS_VERIFY as labeled  # noqa: E402
import DIAG2_PIVOT_REPRESENTATIVE_GRADIENT_VERIFY as gradient  # noqa: E402
import DIAG2_PIVOT_REPRESENTATIVE_TRIPLES_VERIFY as triples  # noqa: E402
import DIAG9_GRAPH_global_factor_census as global_factors  # noqa: E402
import verify_diag3_projective_column_fiber_scan as column_scan  # noqa: E402


CENTER = frozenset(range(4))
FACTOR_COUNT = 26_740
CANARY_FRAME_COUNT = 241_920
CANARY_DIGEST = "fd688604376a65eddc8adac7dd1f1ad8bbc82444e3499e2ee7bf551f91d5da38"
BRACKET_PULLBACK_DIGEST = "6d0aa74b3025c80eff8dc8bc6eacdcb3e2e70f197b8a4972ddfa50e4a0b4b791"
NOVEL_PULLBACK_DIGEST = "3e7e5e874b16067e168e33442f2520085b2d8907a9cf4295e39014e6caaed026"
FACTOR_PULLBACK_DIGEST = "d32e5db4412a43906dac4ec26b3c6aba94ead8086a5a4370ecc46c3f7f9f6255"
TRIANGULAR_DIGEST = "dcffbf90c0fd9fdd926d2a28906b6d297ce1df223cfd65b42b45a4a8a349f08d"

EXPECTED_CLASSIFICATION = {
    (4, "unit"): 1,
    (3, "unit"): 16,
    (2, "parent"): 36,
    (1, "novel"): 16,
    (0, "novel"): 1,
}
EXPECTED_DIVISION_TESTS = 243_954
EXPECTED_AFFINE_FACTORS = 14_601
EXPECTED_AFFINE_BITS = 243_705
EXPECTED_TRIANGULAR = (3_175, 7_260, 12_879, 41_400)

HARD = (
    (2_277, 390, 22_507),
    (5_563, 16_134, 19_284),
    (12_985, 16_183, 7_196),
    (20_355, 5_442, 5_949),
    (9_667, 16_486, 26_315),
    (9_758, 24_338, 15_810),
)

# Exact source-uniform points on the two novel target-frontier orbits.
WITNESSES = {
    (0, 4, 5, 6): (
        Fraction(-8, 13), Fraction(-6), Fraction(4), Fraction(-4),
        Fraction(3), Fraction(2), Fraction(-7), Fraction(8), Fraction(5),
    ),
    (4, 5, 6, 7): (
        Fraction(200, 71), Fraction(5), Fraction(3), Fraction(4),
        Fraction(-7), Fraction(6), Fraction(-4), Fraction(9), Fraction(-9),
    ),
}
EXPECTED_WITNESS_MARGINS = {
    (0, 4, 5, 6): Fraction(8, 13),
    (4, 5, 6, 7): Fraction(13, 71),
}


def reciprocal_polynomial(polynomial):
    """Return x^m p(1/x), primitive-normalized, for componentwise max m."""

    if not polynomial:
        return {}
    maxima = tuple(max(monomial[index] for monomial in polynomial) for index in range(9))
    answer = {
        tuple(maxima[index] - monomial[index] for index in range(9)): coefficient
        for monomial, coefficient in polynomial.items()
    }
    return global_factors.primitive(answer)


def family_digest(tagged_polynomials):
    """Architecture-independent exact sparse-polynomial digest."""

    hasher = hashlib.sha256()
    hasher.update(struct.pack("<I", len(tagged_polynomials)))
    for tag, polynomial in tagged_polynomials:
        hasher.update(struct.pack("<I", tag))
        hasher.update(struct.pack("<I", len(polynomial)))
        for monomial, coefficient in sorted(polynomial.items()):
            hasher.update(struct.pack("<9Bq", *monomial, int(coefficient)))
    return hasher.hexdigest()


def evaluate(polynomial, point):
    answer = Fraction(0)
    for monomial, coefficient in polynomial.items():
        term = Fraction(coefficient)
        for coordinate, exponent in zip(point, monomial):
            term *= coordinate ** exponent
        answer += term
    return answer


def all_brackets():
    matrix = global_factors.normalized_matrix()
    return tuple(
        (
            basis,
            global_factors.primitive(global_factors.square_minor(matrix, basis)),
        )
        for basis in combinations(range(8), 4)
    )


def stabilizer_orbits():
    """Return the S4(center) x S4(complement) orbits on four-subsets."""

    actions = []
    for left, right in product(permutations(range(4)), permutations(range(4, 8))):
        actions.append(left + right)
    unseen = set(combinations(range(8), 4))
    answer = []
    while unseen:
        seed = min(unseen)
        orbit = {
            tuple(sorted(permutation[index] for index in seed))
            for permutation in actions
        }
        unseen.difference_update(orbit)
        answer.append((len(set(seed) & CENTER), len(orbit)))
    answer.sort(reverse=True)
    expected = [(4, 1), (3, 16), (2, 36), (1, 16), (0, 1)]
    if answer != expected:
        raise AssertionError(f"standard-Cremona bracket orbits changed: {answer}")
    return answer


def frontier_census(brackets, primal_factors):
    source_nonconstant = {
        global_factors.polynomial_key(polynomial)
        for _basis, polynomial in brackets
        if global_factors.total_degree(polynomial) > 0
    }
    pullbacks = tuple(
        (basis, reciprocal_polynomial(polynomial))
        for basis, polynomial in brackets
    )
    classification = Counter()
    novel = []
    for basis, pullback in pullbacks:
        overlap = len(set(basis) & CENTER)
        key = global_factors.polynomial_key(pullback)
        if overlap >= 3:
            kind = "unit"
            if global_factors.total_degree(pullback) != 0:
                raise AssertionError(f"nonconstant supposed Cremona unit at {basis}")
        elif overlap == 2:
            kind = "parent"
            if key not in source_nonconstant:
                raise AssertionError(f"two-center pullback is not a parent bracket: {basis}")
        else:
            kind = "novel"
            if key in source_nonconstant:
                raise AssertionError(f"novel pullback equals a parent bracket: {basis}")
            novel.append((basis, pullback))
        classification[(overlap, kind)] += 1
    if dict(classification) != EXPECTED_CLASSIFICATION:
        raise AssertionError(f"Cremona frontier classification changed: {classification}")

    tagged = tuple(
        (sum(1 << index for index in basis), polynomial)
        for basis, polynomial in pullbacks
    )
    novel_tagged = tuple(
        (sum(1 << index for index in basis), polynomial)
        for basis, polynomial in novel
    )
    if family_digest(tagged) != BRACKET_PULLBACK_DIGEST:
        raise AssertionError("standard-Cremona bracket-pullback digest changed")
    if family_digest(novel_tagged) != NOVEL_PULLBACK_DIGEST:
        raise AssertionError("standard-Cremona novel-frontier digest changed")

    # "Novel" is checked in the localized factor sense: none of these 17
    # polynomials has a known nonconstant parent bracket or any of the 26,740
    # primitive residual factors as an exact polynomial divisor.
    parent_polynomials = tuple(
        polynomial for _basis, polynomial in brackets
        if global_factors.total_degree(polynomial) > 0
    )
    tests = 0
    for basis, polynomial in novel:
        degree = global_factors.total_degree(polynomial)
        for candidate in parent_polynomials + primal_factors:
            if global_factors.total_degree(candidate) > degree:
                continue
            tests += 1
            if global_factors.divide_exact(polynomial, candidate) is not None:
                raise AssertionError(
                    f"supposed novel frontier {basis} has a known factor"
                )
    if tests != EXPECTED_DIVISION_TESTS:
        raise AssertionError(f"frontier exact-division accounting changed: {tests}")

    # Both novel stabilizer orbits really occur inside the source uniform
    # torus; they are not hidden source parent boundaries.
    bracket_by_basis = dict(brackets)
    pullback_by_basis = dict(pullbacks)
    for basis, point in WITNESSES.items():
        if any(coordinate == 0 for coordinate in point):
            raise AssertionError("Cremona witness left the coordinate torus")
        if evaluate(pullback_by_basis[basis], point):
            raise AssertionError(f"target frontier witness misses {basis}")
        margin = min(abs(evaluate(polynomial, point)) for polynomial in bracket_by_basis.values())
        if margin != EXPECTED_WITNESS_MARGINS[basis]:
            raise AssertionError(f"source-uniform witness margin changed at {basis}: {margin}")

    print(
        "PASS standard-Cremona target brackets",
        "units 17 parent 36 residual 0 novel 17",
    )
    print(
        "PASS two novel frontier orbits meet the source uniform torus",
        "margins 8/13 13/71",
    )
    print(
        "PASS novel-frontier exact divisor no-go",
        tests, "parent/residual trials",
    )


def factor_action_data():
    occurrences, occurrence_factor, primal = labeled.factor_polynomials()
    factor_occurrence = labeled.factor_action_is_well_defined(
        occurrences, occurrence_factor
    )
    return occurrences, occurrence_factor, factor_occurrence, primal


def canary_frames(occurrences, occurrence_factor, factor_occurrence):
    rows = set()
    for permutation in permutations(range(8)):
        mapping = labeled.triple_map(permutation)
        for canary in HARD:
            rows.add(tuple(
                labeled.transform_factor(
                    factor, mapping, factor_occurrence, occurrence_factor
                )
                for factor in canary
            ))
    rows = tuple(sorted(rows))
    raw = struct.pack("<I", len(rows)) + b"".join(
        struct.pack("<HHH", *row) for row in rows
    )
    if len(rows) != CANARY_FRAME_COUNT or hashlib.sha256(raw).hexdigest() != CANARY_DIGEST:
        raise AssertionError("six-canary S8 source accounting changed")
    return rows


def affinity_no_go(polynomials, rows):
    masks = tuple(column_scan.affinity_mask(polynomial) for polynomial in polynomials)
    accounting = (
        sum(bool(mask) for mask in masks),
        sum(mask.bit_count() for mask in masks),
    )
    if accounting != (EXPECTED_AFFINE_FACTORS, EXPECTED_AFFINE_BITS):
        raise AssertionError(f"standard-Cremona affinity census changed: {accounting}")
    for row in rows:
        if masks[row[0]] & masks[row[1]] & masks[row[2]]:
            raise AssertionError(f"standard-Cremona affine hard-canary survivor: {row}")
    print(
        "PASS standard-Cremona square-affine hard-canary no-go",
        len(rows), "rows", EXPECTED_AFFINE_BITS, "bits",
    )


def triangular_no_go(polynomials, rows):
    parent_factors = labeled.parent_bracket_factors()
    features = []
    classes = Counter()
    for polynomial in polynomials:
        zero_mask = 0
        unit_mask = 0
        for variable in range(9):
            derivative = gradient.derivative(polynomial, variable)
            if not derivative:
                zero_mask |= 1 << variable
            elif triples.bracket_factorization(
                derivative, parent_factors, depth=20
            ) is not None:
                unit_mask |= 1 << variable
        feature = (zero_mask, unit_mask)
        features.append(feature)
        classes[feature] += 1
    accounting = (
        len(classes),
        sum(bool(unit) for _zero, unit in features),
        sum(unit.bit_count() for _zero, unit in features),
        sum(zero.bit_count() for zero, _unit in features),
    )
    raw = struct.pack("<I", len(features)) + b"".join(
        struct.pack("<HH", *feature) for feature in features
    )
    digest = hashlib.sha256(raw).hexdigest()
    if accounting != EXPECTED_TRIANGULAR or digest != TRIANGULAR_DIGEST:
        raise AssertionError(f"standard-Cremona triangular census changed: {accounting}/{digest}")
    survivors = [
        row for row in rows if column_scan.triangular_works(row, features)
    ]
    if survivors:
        raise AssertionError(f"standard-Cremona triangular hard-canary survivor: {survivors[:3]}")
    print(
        "PASS standard-Cremona triangular hard-canary no-go",
        len(rows), "rows", digest,
    )


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--full", action="store_true",
        help="also replay the slower exact triangular-unit canary screen",
    )
    arguments = parser.parse_args()

    brackets = all_brackets()
    stabilizer_orbits()
    occurrences, occurrence_factor, factor_occurrence, primal = factor_action_data()
    frontier_census(brackets, primal)

    transformed = tuple(reciprocal_polynomial(polynomial) for polynomial in primal)
    tagged = tuple(enumerate(transformed))
    if len(transformed) != FACTOR_COUNT or family_digest(tagged) != FACTOR_PULLBACK_DIGEST:
        raise AssertionError("standard-Cremona factor-pullback database changed")
    if any(reciprocal_polynomial(polynomial) != global_factors.primitive(source)
           for polynomial, source in zip(transformed, primal)):
        raise AssertionError("coordinatewise reciprocal polynomial transform is not involutive")

    rows = canary_frames(occurrences, occurrence_factor, factor_occurrence)
    affinity_no_go(transformed, rows)
    if arguments.full:
        triangular_no_go(transformed, rows)
    else:
        print("SCOPE compact mode skips the slower triangular-unit no-go")

    # On (R*)^9 the coordinate map x_i -> 1/x_i is its own inverse, with
    # Jacobian determinant -product(x_i^-2).  Hence every fiber, including
    # one over a novel target-nonuniform divisor, is a singleton.
    print("NO_GO standard Cremona has no positive-dimensional exceptional fiber on the source torus")
    print("SCOPE no triple-factor noncompactness theorem is claimed")


if __name__ == "__main__":
    main()
