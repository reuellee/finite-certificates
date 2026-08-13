#!/usr/bin/env python3
"""Exact affine-fiber closure of every labeled residual-factor pair orbit.

The exhaustive relative-label audit leaves 122 pair orbits after fixed-minor,
translation, and torus certificates.  Put the first factor into its canonical
graph frame, solve its distinguished affine pivot, and restrict the second
factor to that graph.  Every residue has a stabilizer-equivalent presentation
which is affine in at least one of the remaining graph coordinates.  One case
requires reversing the pair and using the type-51 factor as the graph anchor.

An affine equation C(w)*x+D(w)=0 in an open graph domain has no compact
component.  Where C=0 its entire open vertical fiber is present; where C is
nonzero it is a graph over an open subset of R^7.  This checker certifies the
finite algebraic input to that argument.  Together with the earlier audit it
settles all 9,476 unordered labeled factor-pair orbits.
"""

from __future__ import annotations

from collections import Counter
import hashlib
import math
from pathlib import Path
import sys

import numpy as np


HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import DIAG2_PIVOT_LABELED_PAIR_ORBITS_VERIFY as labeled  # noqa: E402
import DIAG2_PIVOT_REPRESENTATIVE_GRADIENT_VERIFY as gradient  # noqa: E402
import verify_residual_log_binomials as poly  # noqa: E402


CERTIFICATE = HERE / "data" / "DIAG2_PIVOT_pair_classification.npz"
EXPECTED_CERTIFICATE_SHA256 = (
    "a12680b52ace15096437e5cbcfcbdb6d888c9d61a2bccf8a2d336fa5be6b7025"
)
EXPECTED_MODE_COUNTS = {0: 122, 1: 7_217, 2: 1_091, 3: 918, 4: 124, 5: 4}
EXPECTED_REANCHORED = ((50, 20_046),)
EXPECTED_DIGEST = "af0fa699771292f5cca65510f32cf5c007034f4c9fdac5c3c3a49f0dfcd65846"
PIVOT = {49: 3, 50: 3, 51: 5}
VARIABLES = "abcdefghi"
ZERO_MONOMIAL = (0,) * 9


def primitive(polynomial):
    polynomial = poly.clean(polynomial)
    if not polynomial:
        return polynomial
    divisor = 0
    for coefficient in polynomial.values():
        divisor = math.gcd(divisor, abs(coefficient))
    if divisor > 1:
        polynomial = {
            monomial: coefficient // divisor
            for monomial, coefficient in polynomial.items()
        }
    first = max(polynomial)
    if polynomial[first] < 0:
        polynomial = poly.negative(polynomial)
    return polynomial


def power(polynomial, exponent):
    answer = poly.constant(1)
    for _ in range(exponent):
        answer = poly.multiply(answer, polynomial)
    return answer


def pivot_split(polynomial, pivot):
    if any(monomial[pivot] > 1 for monomial in polynomial):
        raise AssertionError("canonical residual anchor is not pivot-affine")
    # Preserve the common normalization of slope and constant.  Normalizing
    # them independently can flip only one sign (types 36, 38, and 51 do
    # exactly that), replacing A*x+B=0 by the wrong graph A*x-B=0.
    slope = gradient.derivative(polynomial, pivot)
    constant = {
        monomial: coefficient
        for monomial, coefficient in polynomial.items()
        if monomial[pivot] == 0
    }
    if not slope:
        raise AssertionError("canonical residual anchor has zero graph slope")
    return slope, constant


def graph_restrict(polynomial, pivot, slope, numerator):
    """Return slope^m p(x_pivot=numerator/slope), primitively."""

    degree = max((monomial[pivot] for monomial in polynomial), default=0)
    answer = poly.constant(0)
    for monomial, coefficient in polynomial.items():
        exponent = monomial[pivot]
        base = list(monomial)
        base[pivot] = 0
        answer = poly.add(
            answer,
            poly.multiply(
                {tuple(base): coefficient},
                power(numerator, exponent),
                power(slope, degree - exponent),
            ),
        )
    return primitive(answer)


def coordinate_degrees(polynomial, omitted):
    return tuple(
        max((monomial[index] for monomial in polynomial), default=0)
        for index in range(9)
        if index != omitted
    )


def expected_anchor_slope(kind):
    variables = tuple(poly.variable(index) for index in range(9))
    a, b, _c, _d, _e, _f, _g, h, i = variables
    if kind == 49:
        return poly.constant(1)
    if kind == 50:
        return i
    if kind == 51:
        return poly.negative(
            poly.multiply(poly.subtract(a, b), poly.subtract(h, b))
        )
    raise AssertionError(f"unexpected residue anchor {kind}")


def candidate_presentations(
    anchor_kind,
    partner,
    canonical,
    stabilizers,
    factor_polynomial,
    factor_occurrence,
    occurrence_factor,
):
    pivot = PIVOT[anchor_kind]
    anchor = canonical[anchor_kind]
    slope, constant = pivot_split(factor_polynomial[anchor], pivot)
    if poly.add(
        poly.multiply(slope, poly.variable(pivot)), constant
    ) != factor_polynomial[anchor]:
        raise AssertionError(f"type-{anchor_kind} graph split changed the equation")
    if slope != expected_anchor_slope(anchor_kind):
        raise AssertionError(f"type-{anchor_kind} graph slope changed")
    numerator = poly.negative(constant)
    targets = {
        labeled.transform_factor(
            partner,
            symmetry,
            factor_occurrence,
            occurrence_factor,
        )
        for symmetry in stabilizers[anchor_kind]
    }
    answer = []
    for target in sorted(targets):
        restricted = graph_restrict(
            factor_polynomial[target], pivot, slope, numerator
        )
        if not restricted:
            raise AssertionError("distinct residual factors restricted identically")
        degrees = coordinate_degrees(restricted, pivot)
        affine = tuple(
            index
            for index, degree in zip(
                (value for value in range(9) if value != pivot), degrees
            )
            if degree <= 1
        )
        answer.append(
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
    return min(answer, key=lambda item: item[:6])


def load_classification(pair_orbits):
    digest = hashlib.sha256(CERTIFICATE.read_bytes()).hexdigest()
    if digest != EXPECTED_CERTIFICATE_SHA256:
        raise AssertionError("pair-classification artifact SHA-256 changed")
    with np.load(CERTIFICATE, allow_pickle=False) as source:
        if set(source.files) != {
            "pair_kind",
            "pair_second_factor",
            "classification",
        }:
            raise AssertionError("pair-classification artifact fields changed")
        kinds = source["pair_kind"]
        seconds = source["pair_second_factor"]
        classification = source["classification"]
    artifact_pairs = tuple(
        (int(kind), int(second)) for kind, second in zip(kinds, seconds)
    )
    if artifact_pairs != pair_orbits:
        raise AssertionError("pair-classification orbit order changed")
    mode_counts = dict(sorted(Counter(map(int, classification)).items()))
    if mode_counts != EXPECTED_MODE_COUNTS:
        raise AssertionError(f"pair-classification mode counts changed: {mode_counts}")
    residue = tuple(
        pair
        for pair, mode in zip(artifact_pairs, classification)
        if int(mode) == 0
    )
    residue_digest = hashlib.sha256(repr(residue).encode("ascii")).hexdigest()
    if residue_digest != labeled.EXPECTED_ALL_FRAME_RESIDUE_DIGEST:
        raise AssertionError("pair-classification residue digest changed")
    return residue, mode_counts


def semantic_digest(reports):
    digest = hashlib.sha256()
    digest.update(b"diag2-all-pair-affine-fibers-v1\0")
    for report in reports:
        digest.update(repr(report).encode("ascii"))
    return digest.hexdigest()


def main():
    occurrences, occurrence_factor, factor_polynomial = labeled.factor_polynomials()
    pair_orbits, _ordered_counts, _orbit_sizes = labeled.pair_orbit_representatives(
        occurrences, occurrence_factor
    )
    residue, mode_counts = load_classification(pair_orbits)
    factor_occurrence = labeled.factor_action_is_well_defined(
        occurrences, occurrence_factor
    )
    canonical, _alignments, stabilizers = labeled.canonical_anchor_alignments(
        occurrences,
        occurrence_factor,
        factor_occurrence,
    )
    (
        representatives,
        _full_stabilizers,
        factor_alignment,
        _factor_occurrence,
        _orbit_sizes,
    ) = labeled.factor_orbit_data(occurrences, occurrence_factor)
    for kind in PIVOT:
        if canonical[kind] != representatives[kind]:
            raise AssertionError("canonical graph and pair-orbit anchors diverged")

    reports = []
    reanchored = []
    anchor_counts = Counter()
    affine_counts = Counter()
    for original_kind, second in residue:
        first = canonical[original_kind]
        candidate = candidate_presentations(
            original_kind,
            second,
            canonical,
            stabilizers,
            factor_polynomial,
            factor_occurrence,
            occurrence_factor,
        )
        anchor_kind = original_kind
        if candidate[0]:
            second_kind, mapping = factor_alignment[second]
            if second_kind not in PIVOT:
                raise AssertionError("residue cannot be reversed to a graph anchor")
            if labeled.transform_factor(
                second, mapping, factor_occurrence, occurrence_factor
            ) != canonical[second_kind]:
                raise AssertionError("reverse graph alignment missed its anchor")
            partner = labeled.transform_factor(
                first, mapping, factor_occurrence, occurrence_factor
            )
            candidate = candidate_presentations(
                second_kind,
                partner,
                canonical,
                stabilizers,
                factor_polynomial,
                factor_occurrence,
                occurrence_factor,
            )
            anchor_kind = second_kind
            reanchored.append((original_kind, second))
        if candidate[0] or not candidate[6]:
            raise AssertionError(f"pair {(original_kind, second)} has no affine fiber")

        (
            _failure,
            _negative_affine_count,
            maximum_coordinate_degree,
            terms,
            total_degree,
            target,
            affine,
            degrees,
            restricted,
        ) = candidate
        anchor_counts[anchor_kind] += 1
        affine_counts[len(affine)] += 1
        reports.append(
            (
                (original_kind, second),
                anchor_kind,
                target,
                PIVOT[anchor_kind],
                tuple(VARIABLES[index] for index in affine),
                degrees,
                terms,
                total_degree,
                maximum_coordinate_degree,
                tuple(sorted(restricted.items())),
            )
        )

    if tuple(reanchored) != EXPECTED_REANCHORED:
        raise AssertionError(f"reanchored residue changed: {reanchored}")
    digest = semantic_digest(reports)
    if EXPECTED_DIGEST is not None and digest != EXPECTED_DIGEST:
        raise AssertionError(f"affine-fiber semantic digest changed: {digest}")

    print("PASS stored 9,476-orbit classification modes:", mode_counts)
    print("PASS pre-saturation residue digest:", labeled.EXPECTED_ALL_FRAME_RESIDUE_DIGEST)
    print("PASS affine graph presentations for residue pairs:", len(reports))
    print("PASS presentation anchors:", dict(sorted(anchor_counts.items())))
    print("PASS affine-coordinate counts:", dict(sorted(affine_counts.items())))
    print("PASS unique reversed anchor:", tuple(reanchored))
    print("SEMANTIC SHA256:", digest)
    print("THEOREM every one of 9,476 labeled factor-pair zero sets has no compact component")
    print("CAVEAT bounded sign chambers and global decorated cycles still obstruct diagonal two")


if __name__ == "__main__":
    main()
