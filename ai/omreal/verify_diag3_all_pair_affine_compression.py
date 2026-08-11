#!/usr/bin/env python3
"""Uniform sequential-affine compression of all 9,476 factor-pair orbits.

The earlier pair theorem uses six certificate families.  This checker gives
one algebraic presentation for every unordered relative-label factor pair:
put either factor into a canonical graph frame with parent-bracket-unit
slope, solve it, and the other restricted factor is affine in at least one
remaining coordinate.  The iterated affine-fiber lemma then reproves that
every pair zero-set component is noncompact.

This is a compression handle for the triple endpoint, not a triple theorem
and not a proof of the third diagonal.
"""

from __future__ import annotations

from collections import Counter
import hashlib
from pathlib import Path
import sys


HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import DIAG2_PIVOT_LABELED_PAIR_ORBITS_VERIFY as labeled  # noqa: E402
import DIAG2_PIVOT_REPRESENTATIVE_TRIPLES_VERIFY as triples  # noqa: E402
import verify_diag2_pivot_all_pair_fibers as fibers  # noqa: E402
import verify_residual_log_binomials as poly  # noqa: E402


PIVOT = {36: 0, 38: 0, 48: 0, 49: 3, 50: 3, 51: 5}
VARIABLES = "abcdefghi"
EXPECTED_ANCHORS = {36: 647, 38: 236, 48: 328, 49: 5_203, 50: 2_682, 51: 380}
EXPECTED_AFFINE_COUNTS = {1: 11, 2: 69, 3: 209, 4: 607, 5: 1_179, 6: 1_894, 7: 2_307, 8: 3_200}
EXPECTED_MAXIMUM_DEGREES = {1: 3_200, 2: 5_111, 3: 1_120, 4: 44, 5: 1}
EXPECTED_REVERSED = (
    (38, 6_386, 48, 14_554),
    (38, 6_510, 48, 3_552),
    (50, 20_046, 51, 5_956),
)
EXPECTED_DIGEST = "a28270e870ff2cb2a81a25a395f573fa95de63dc46b52a212a22779e92445847"


def candidate(
    kind,
    partner,
    canonical,
    stabilizers,
    factor_polynomial,
    factor_occurrence,
    occurrence_factor,
):
    pivot = PIVOT[kind]
    slope, constant = fibers.pivot_split(factor_polynomial[canonical[kind]], pivot)
    numerator = poly.negative(constant)
    targets = {
        labeled.transform_factor(
            partner, symmetry, factor_occurrence, occurrence_factor
        )
        for symmetry in stabilizers[kind]
    }
    reports = []
    for target in sorted(targets):
        restricted = fibers.graph_restrict(
            factor_polynomial[target], pivot, slope, numerator
        )
        degrees = fibers.coordinate_degrees(restricted, pivot)
        affine = tuple(
            index
            for index, degree in zip(
                (value for value in range(9) if value != pivot), degrees
            )
            if degree <= 1
        )
        reports.append(
            (
                0 if affine else 1,
                -len(affine),
                max(degrees),
                len(restricted),
                max(map(sum, restricted)),
                target,
                affine,
                degrees,
                restricted,
            )
        )
    return min(reports, key=lambda report: report[:6])


def main():
    occurrences, occurrence_factor, factor_polynomial = labeled.factor_polynomials()
    pair_orbits, _ordered_counts, _orbit_sizes = labeled.pair_orbit_representatives(
        occurrences, occurrence_factor
    )
    factor_occurrence = labeled.factor_action_is_well_defined(
        occurrences, occurrence_factor
    )
    canonical, _anchor_alignments, stabilizers = labeled.canonical_anchor_alignments(
        occurrences, occurrence_factor, factor_occurrence
    )
    representatives, _full_stabilizers, alignment, _factor_occurrence, _sizes = (
        labeled.factor_orbit_data(occurrences, occurrence_factor)
    )
    if any(canonical[kind] != representatives[kind] for kind in PIVOT):
        raise AssertionError("canonical anchors changed")

    parent_factors = labeled.parent_bracket_factors()
    slope_certificates = {}
    for kind, pivot in PIVOT.items():
        slope, constant = fibers.pivot_split(
            factor_polynomial[canonical[kind]], pivot
        )
        if poly.add(
            poly.multiply(slope, poly.variable(pivot)), constant
        ) != factor_polynomial[canonical[kind]]:
            raise AssertionError(f"type-{kind} graph split changed the equation")
        certificate = triples.bracket_factorization(slope, parent_factors, depth=12)
        if certificate is None:
            raise AssertionError(f"type-{kind} graph slope is not a parent unit")
        slope_certificates[kind] = certificate

    reversed_pairs = []
    anchor_counts = Counter()
    affine_counts = Counter()
    maximum_degrees = Counter()
    digest = hashlib.sha256()
    digest.update(b"diag3-all-pair-sequential-affine-v1\0")

    for kind, second in pair_orbits:
        first = canonical[kind]
        report = candidate(
            kind,
            second,
            canonical,
            stabilizers,
            factor_polynomial,
            factor_occurrence,
            occurrence_factor,
        )
        anchor_kind = kind
        if report[0]:
            second_kind, mapping = alignment[second]
            if labeled.transform_factor(
                second, mapping, factor_occurrence, occurrence_factor
            ) != canonical[second_kind]:
                raise AssertionError("reverse alignment missed its canonical anchor")
            partner = labeled.transform_factor(
                first, mapping, factor_occurrence, occurrence_factor
            )
            report = candidate(
                second_kind,
                partner,
                canonical,
                stabilizers,
                factor_polynomial,
                factor_occurrence,
                occurrence_factor,
            )
            anchor_kind = second_kind
            reversed_pairs.append((kind, second, second_kind, partner))
        if report[0] or not report[6]:
            raise AssertionError(f"pair {(kind, second)} has no affine presentation")

        (
            _failure,
            _negative_affine_count,
            maximum_degree,
            terms,
            total_degree,
            target,
            affine,
            degrees,
            restricted,
        ) = report
        anchor_counts[anchor_kind] += 1
        affine_counts[len(affine)] += 1
        maximum_degrees[maximum_degree] += 1
        record = (
            (kind, second),
            anchor_kind,
            target,
            PIVOT[anchor_kind],
            tuple(VARIABLES[index] for index in affine),
            degrees,
            terms,
            total_degree,
            maximum_degree,
            tuple(sorted(restricted.items())),
        )
        digest.update(repr(record).encode("ascii"))

    if dict(sorted(anchor_counts.items())) != EXPECTED_ANCHORS:
        raise AssertionError(f"anchor counts changed: {anchor_counts}")
    if dict(sorted(affine_counts.items())) != EXPECTED_AFFINE_COUNTS:
        raise AssertionError(f"affine-coordinate counts changed: {affine_counts}")
    if dict(sorted(maximum_degrees.items())) != EXPECTED_MAXIMUM_DEGREES:
        raise AssertionError(f"maximum-degree counts changed: {maximum_degrees}")
    if tuple(reversed_pairs) != EXPECTED_REVERSED:
        raise AssertionError(f"reversed pairs changed: {reversed_pairs}")
    semantic = digest.hexdigest()
    if semantic != EXPECTED_DIGEST:
        raise AssertionError(f"semantic digest changed: {semantic}")

    print("PASS graph-anchor slopes are parent-bracket units:", slope_certificates)
    print("PASS sequential-affine pair orbits:", len(pair_orbits))
    print("PASS presentation anchors:", dict(sorted(anchor_counts.items())))
    print("PASS affine-coordinate counts:", dict(sorted(affine_counts.items())))
    print("PASS maximum-degree counts:", dict(sorted(maximum_degrees.items())))
    print("PASS reversed anchors:", tuple(reversed_pairs))
    print("SEMANTIC", semantic)
    print("THEOREM every factor-pair orbit has a sequential affine presentation")
    print("CAVEAT this does not classify triple-factor zero sets")


if __name__ == "__main__":
    main()
