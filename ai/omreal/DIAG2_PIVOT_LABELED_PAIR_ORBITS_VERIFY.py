#!/usr/bin/env python3
"""Exact relative-S8 residual-wall pair census and Jacobian audit.

The canonical residual-gradient theorem checks only the twelve distinct
polynomials in one normalization.  A second labeled wall is obtained by an
arbitrary relative permutation of the eight parent labels.  This verifier
closes that finite bookkeeping gap:

* quotient the 84,840 labeled occurrences by equality after localization at
  the parent brackets, obtaining 26,740 geometric residual factors;
* enumerate unordered pairs of distinct factors up to simultaneous S8;
* recover the primitive localized polynomial of each occurrence from the
  checked-in global factor census; and
* exhaust projective frames for exact parent-bracket-product Jacobian minors,
  common affine translations, and common weighted-torus escapes.

Each listed certificate proves every component of the common-zero set
noncompact.  Failure to find one is reported as residue, not as a rank drop
or compact component.
"""

from __future__ import annotations

import argparse
import hashlib
from collections import Counter
from fractions import Fraction
from itertools import combinations, permutations
from math import gcd, lcm
from pathlib import Path
import sys

import numpy as np


HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import DIAG2_PIVOT_REPRESENTATIVE_GRADIENT_VERIFY as representative  # noqa: E402
import DIAG2_PIVOT_REPRESENTATIVE_TRIPLES_VERIFY as triples  # noqa: E402
import DIAG9_GRAPH_global_factor_census as global_factors  # noqa: E402
import prototype_koszul_circuits as koszul  # noqa: E402
import verify_residual_log_binomials as poly  # noqa: E402


VARIABLE_NAMES = "abcdefghi"
EXPECTED_FACTOR_ORBIT_SIZES = {
    36: 840,
    38: 280,
    48: 420,
    49: 10_080,
    50: 10_080,
    51: 5_040,
}
EXPECTED_ORDERED_PAIR_ORBITS = {
    36: 654,
    38: 255,
    48: 361,
    49: 6_808,
    50: 6_913,
    51: 3_435,
}
EXPECTED_PAIR_ORBITS = 9_476
EXPECTED_PRIMARY_CERTIFICATES = 7_217
EXPECTED_REFRAMED_CERTIFICATES = 1_091
EXPECTED_RESIDUE = 1_168
EXPECTED_DIGEST = "df05bba9f0fa40f4ec5efa9296c40e44fecae06fae8bb0ae1b9f81706556bded"
EXPECTED_ALL_FRAME_CERTIFICATES = 918
EXPECTED_TRANSLATION_ESCAPES = 124
EXPECTED_SCALING_ESCAPES = 4
EXPECTED_PRE_SATURATION_RESIDUE = 122
EXPECTED_ALL_FRAME_DIGEST = "08d948e990c21a1ab7520e72f1ce885f36652273d953b95edb4caeba90ad7263"


def occurrence_representatives():
    triple_index = {
        tuple(value - 1 for value in triple): index
        for index, triple in enumerate(koszul.TRIPLES)
    }
    answer = {}
    tokens = koszul.REPRESENTATIVE_TEXT.split()
    for kind in sorted(koszul.RESIDUAL):
        edges = tuple(
            sorted(
                tuple(int(character) - 1 for character in edge)
                for edge in tokens[kind].split("/")
            )
        )
        answer[kind] = tuple(sorted(triple_index[edge] for edge in edges))
    return answer


TRIPLES = tuple(tuple(value - 1 for value in row) for row in koszul.TRIPLES)
TRIPLE_INDEX = {triple: index for index, triple in enumerate(TRIPLES)}


def triple_map(permutation):
    return tuple(
        TRIPLE_INDEX[tuple(sorted(permutation[value] for value in triple))]
        for triple in TRIPLES
    )


def label_action():
    maps = []
    inverse_maps = []
    for permutation in permutations(range(8)):
        mapping = triple_map(permutation)
        inverse = [0] * len(mapping)
        for source, target in enumerate(mapping):
            inverse[target] = source
        maps.append(mapping)
        inverse_maps.append(tuple(inverse))
    if len(set(maps)) != 40_320:
        raise AssertionError("the S8 action on triples is not faithful")
    return tuple(maps), tuple(inverse_maps)


def transform(occurrence, mapping):
    return tuple(sorted(mapping[index] for index in occurrence))


def factor_action_is_well_defined(occurrences, occurrence_factor):
    """Check equivariance on adjacent transpositions, which generate S8."""

    by_factor = {}
    for occurrence in occurrences:
        by_factor.setdefault(occurrence_factor[occurrence], []).append(occurrence)
    generators = []
    for index in range(7):
        permutation = list(range(8))
        permutation[index], permutation[index + 1] = (
            permutation[index + 1],
            permutation[index],
        )
        generators.append(triple_map(tuple(permutation)))
    for factor, members in by_factor.items():
        for generator in generators:
            images = {
                occurrence_factor[transform(member, generator)]
                for member in members
            }
            if len(images) != 1:
                raise AssertionError(
                    f"localized factor equality is not S8-equivariant at factor {factor}"
                )
    return {factor: members[0] for factor, members in by_factor.items()}


def transform_factor(factor, mapping, factor_occurrence, occurrence_factor):
    return occurrence_factor[transform(factor_occurrence[factor], mapping)]


def factor_orbit_data(occurrences, occurrence_factor):
    maps, inverse_maps = label_action()
    support_representatives = occurrence_representatives()
    factor_occurrence = factor_action_is_well_defined(
        occurrences, occurrence_factor
    )
    candidates = {}
    for kind, occurrence in support_representatives.items():
        factor = occurrence_factor[occurrence]
        candidates.setdefault(kind, factor)
    # Types 46 and 47 have different support orbits but the same localized
    # residual factor.  Keep type 46 as its stable orbit label.
    candidates.pop(47)
    if len(set(candidates.values())) != 12:
        raise AssertionError("canonical residuals do not give twelve factor orbits")
    # Arbitrary relabeling identifies several of the twelve normalized
    # formulas.  Retain the least canonical type in each full factor orbit.
    representatives = {}
    covered = set()
    for kind, factor in sorted(candidates.items()):
        if factor in covered:
            continue
        factor_orbit = {
            transform_factor(
                factor, mapping, factor_occurrence, occurrence_factor
            )
            for mapping in maps
        }
        representatives[kind] = factor
        covered.update(factor_orbit)
    stabilizers = {
        kind: tuple(
            mapping
            for mapping in maps
            if transform_factor(
                representative, mapping, factor_occurrence, occurrence_factor
            )
            == representative
        )
        for kind, representative in representatives.items()
    }

    alignment = {}
    for kind, representative in representatives.items():
        for mapping, inverse in zip(maps, inverse_maps):
            moved = transform_factor(
                representative, mapping, factor_occurrence, occurrence_factor
            )
            alignment.setdefault(moved, (kind, inverse))

    factor_set = frozenset(factor_occurrence)
    if frozenset(alignment) != factor_set:
        missing = len(factor_set - frozenset(alignment))
        extra = len(frozenset(alignment) - factor_set)
        raise AssertionError(
            f"residual factor orbit coverage changed: missing={missing}, extra={extra}"
        )
    orbit_sizes = Counter(kind for kind, _ in alignment.values())
    if sum(orbit_sizes.values()) != 26_740:
        raise AssertionError("wrong localized residual factor count")
    return (
        representatives,
        stabilizers,
        alignment,
        factor_occurrence,
        orbit_sizes,
    )


def ordered_key(
    first,
    second,
    stabilizers,
    alignment,
    factor_occurrence,
    occurrence_factor,
):
    kind, align = alignment[first]
    moved = transform_factor(
        second, align, factor_occurrence, occurrence_factor
    )
    canonical = min(
        transform_factor(
            moved, symmetry, factor_occurrence, occurrence_factor
        )
        for symmetry in stabilizers[kind]
    )
    return kind, canonical


def pair_orbit_representatives(occurrences, occurrence_factor):
    (
        representatives,
        stabilizers,
        alignment,
        factor_occurrence,
        orbit_sizes,
    ) = factor_orbit_data(occurrences, occurrence_factor)
    result = set()
    ordered_counts = {}
    for kind, first in representatives.items():
        second_orbits = {
            min(
                transform_factor(
                    second, symmetry, factor_occurrence, occurrence_factor
                )
                for symmetry in stabilizers[kind]
            )
            for second in factor_occurrence
            if second != first
        }
        ordered_counts[kind] = len(second_orbits)
        for second in second_orbits:
            forward = (kind, second)
            reverse = ordered_key(
                second,
                first,
                stabilizers,
                alignment,
                factor_occurrence,
                occurrence_factor,
            )
            result.add(min(forward, reverse))
    return tuple(sorted(result)), ordered_counts, dict(sorted(orbit_sizes.items()))


def cycle_type(permutation):
    seen = set()
    lengths = []
    for start in range(8):
        if start in seen:
            continue
        current = start
        length = 0
        while current not in seen:
            seen.add(current)
            current = permutation[current]
            length += 1
        lengths.append(length)
    return tuple(sorted(lengths, reverse=True))


def burnside_pair_orbit_count(
    occurrences, occurrence_factor
):
    """Independent conjugacy-class Burnside check for unordered pairs."""

    factor_occurrence = factor_action_is_well_defined(
        occurrences, occurrence_factor
    )
    classes = Counter()
    representatives = {}
    for permutation in permutations(range(8)):
        kind = cycle_type(permutation)
        classes[kind] += 1
        representatives.setdefault(kind, permutation)

    fixed_sum = 0
    pair_fixed_sum = 0
    for kind, multiplicity in classes.items():
        permutation = representatives[kind]
        square = tuple(permutation[permutation[index]] for index in range(8))
        mapping = triple_map(permutation)
        square_mapping = triple_map(square)
        fixed = sum(
            transform_factor(
                factor, mapping, factor_occurrence, occurrence_factor
            )
            == factor
            for factor in factor_occurrence
        )
        fixed_square = sum(
            transform_factor(
                factor, square_mapping, factor_occurrence, occurrence_factor
            )
            == factor
            for factor in factor_occurrence
        )
        fixed_pairs = fixed * (fixed - 1) // 2 + (fixed_square - fixed) // 2
        fixed_sum += multiplicity * fixed
        pair_fixed_sum += multiplicity * fixed_pairs
    if fixed_sum % 40_320 or pair_fixed_sum % 40_320:
        raise AssertionError("nonintegral Burnside orbit quotient")
    return fixed_sum // 40_320, pair_fixed_sum // 40_320


def factor_polynomials():
    with np.load(global_factors.CERTIFICATE, allow_pickle=False) as stored:
        occurrences = tuple(
            tuple(map(int, row)) for row in stored["occurrence_fourset"]
        )
        keys = global_factors.unflatten_keys(
            stored["factor_offset"],
            stored["factor_exponent"],
            stored["factor_coefficient"],
        )
        occurrence_factor_ids = tuple(map(int, stored["occurrence_factor"]))
    if len(occurrences) != 84_840 or len(keys) != 26_740:
        raise AssertionError("wrong global residual factor certificate dimensions")
    occurrence_factor = {
        occurrence: index
        for occurrence, index in zip(occurrences, occurrence_factor_ids)
    }
    if len(occurrence_factor) != len(occurrences):
        raise AssertionError("duplicate labeled residual occurrences")
    return occurrences, occurrence_factor, tuple(dict(key) for key in keys)


def parent_bracket_factors():
    records = global_factors.bracket_records(global_factors.normalized_matrix())
    brackets = {
        "".join(str(value + 1) for value in basis): polynomial
        for basis, polynomial in records
    }
    factors = triples.normalized_bracket_factors(brackets)
    if len(records) != 62 or len(factors) != 62:
        raise AssertionError("wrong nonconstant parent-bracket factor count")
    return factors


def jacobian_minor(first, second, variables):
    left, right = variables
    return poly.subtract(
        poly.multiply(
            representative.derivative(first, left),
            representative.derivative(second, right),
        ),
        poly.multiply(
            representative.derivative(first, right),
            representative.derivative(second, left),
        ),
    )


def direct_product_certificate(first, second, factors):
    for variables in combinations(range(9), 2):
        minor = jacobian_minor(first, second, variables)
        factorization = triples.bracket_factorization(minor, factors)
        if factorization is not None:
            return variables, factorization
    return None


def canonical_anchor_alignments(
    occurrences, occurrence_factor, factor_occurrence
):
    """One exact reframe taking each factor to each available canonical type."""

    maps, inverse_maps = label_action()
    support_representatives = occurrence_representatives()
    canonical = {
        kind: occurrence_factor[occurrence]
        for kind, occurrence in support_representatives.items()
        if kind != 47
    }
    alignments = {}
    stabilizers = {}
    for kind, factor in canonical.items():
        table = {}
        stabilizer = []
        for mapping, inverse in zip(maps, inverse_maps):
            moved = transform_factor(
                factor, mapping, factor_occurrence, occurrence_factor
            )
            table.setdefault(moved, inverse)
            if moved == factor:
                stabilizer.append(mapping)
        alignments[kind] = table
        stabilizers[kind] = tuple(stabilizer)
    if set().union(*(set(table) for table in alignments.values())) != set(
        factor_occurrence
    ):
        raise AssertionError("canonical reframe tables do not cover every factor")
    return canonical, alignments, stabilizers


def reframed_product_certificate(
    first,
    second,
    factors,
    factor_polynomial,
    occurrence_factor,
    factor_occurrence,
    canonical,
    anchor_alignments,
):
    """Try both pair orders and every canonical formula in the first orbit."""

    for swapped, (left, right) in enumerate(((first, second), (second, first))):
        for kind, table in anchor_alignments.items():
            mapping = table.get(left)
            if mapping is None:
                continue
            moved_left = transform_factor(
                left, mapping, factor_occurrence, occurrence_factor
            )
            moved_right = transform_factor(
                right, mapping, factor_occurrence, occurrence_factor
            )
            if moved_left != canonical[kind]:
                raise AssertionError("canonical reframe missed its target")
            certificate = direct_product_certificate(
                factor_polynomial[moved_left],
                factor_polynomial[moved_right],
                factors,
            )
            if certificate is not None:
                return kind, bool(swapped), certificate
    return None


def all_frame_product_certificate(
    first,
    second,
    factors,
    factor_polynomial,
    occurrence_factor,
    factor_occurrence,
    canonical,
    anchor_alignments,
    anchor_stabilizers,
):
    """Exhaust every projective frame taking either factor to a canonical type."""

    for swapped, (left, right) in enumerate(((first, second), (second, first))):
        for kind, table in anchor_alignments.items():
            mapping = table.get(left)
            if mapping is None:
                continue
            moved_left = transform_factor(
                left, mapping, factor_occurrence, occurrence_factor
            )
            moved_right = transform_factor(
                right, mapping, factor_occurrence, occurrence_factor
            )
            if moved_left != canonical[kind]:
                raise AssertionError("all-frame reframe missed its target")
            targets = {
                transform_factor(
                    moved_right,
                    symmetry,
                    factor_occurrence,
                    occurrence_factor,
                )
                for symmetry in anchor_stabilizers[kind]
            }
            for target in sorted(targets):
                if target == moved_right:
                    continue
                certificate = direct_product_certificate(
                    factor_polynomial[moved_left],
                    factor_polynomial[target],
                    factors,
                )
                if certificate is not None:
                    return kind, bool(swapped), target, certificate
    return None


def translation_rows(polynomial):
    rows = {}
    for variable in range(9):
        for monomial, coefficient in representative.derivative(
            polynomial, variable
        ).items():
            rows.setdefault(monomial, [0] * 9)[variable] += coefficient
    return tuple(tuple(row) for _, row in sorted(rows.items()) if any(row))


def rational_null_vector(matrix):
    rows = [[Fraction(value) for value in row] for row in matrix]
    pivot_columns = []
    pivot_row = 0
    for column in range(9):
        pivot = next(
            (index for index in range(pivot_row, len(rows)) if rows[index][column]),
            None,
        )
        if pivot is None:
            continue
        rows[pivot_row], rows[pivot] = rows[pivot], rows[pivot_row]
        scale = rows[pivot_row][column]
        rows[pivot_row] = [value / scale for value in rows[pivot_row]]
        for other in range(len(rows)):
            if other == pivot_row or not rows[other][column]:
                continue
            scale = rows[other][column]
            rows[other] = [
                left - scale * right
                for left, right in zip(rows[other], rows[pivot_row])
            ]
        pivot_columns.append(column)
        pivot_row += 1
        if pivot_row == len(rows):
            break
    free = next(
        (column for column in range(9) if column not in pivot_columns), None
    )
    if free is None:
        return None
    vector = [Fraction(0)] * 9
    vector[free] = 1
    for row, column in enumerate(pivot_columns):
        vector[column] = -rows[row][free]
    denominator = 1
    for value in vector:
        denominator = lcm(denominator, value.denominator)
    integers = [int(value * denominator) for value in vector]
    divisor = 0
    for value in integers:
        divisor = gcd(divisor, abs(value))
    integers = [value // divisor for value in integers]
    first = next(value for value in integers if value)
    if first < 0:
        integers = [-value for value in integers]
    return tuple(integers)


def translation_escape(first, second):
    vector = rational_null_vector(
        translation_rows(first) + translation_rows(second)
    )
    if vector is None:
        return None
    for polynomial in (first, second):
        directional = poly.constant(0)
        for variable, coefficient in enumerate(vector):
            if coefficient:
                directional = poly.add(
                    directional,
                    poly.multiply(
                        poly.constant(coefficient),
                        representative.derivative(polynomial, variable),
                    ),
                )
        if directional:
            raise AssertionError("translation-kernel vector does not annihilate factor")
    return vector


def homogeneity_rows(polynomial):
    monomials = sorted(polynomial)
    if not monomials:
        return ()
    base = monomials[0]
    return tuple(
        tuple(left - right for left, right in zip(monomial, base))
        for monomial in monomials[1:]
    )


def scaling_escape(first, second):
    vector = rational_null_vector(
        homogeneity_rows(first) + homogeneity_rows(second)
    )
    if vector is None:
        return None
    for polynomial in (first, second):
        weights = {
            sum(exponent * weight for exponent, weight in zip(monomial, vector))
            for monomial in polynomial
        }
        if len(weights) != 1:
            raise AssertionError("scaling-kernel vector is not a common weight")
    return vector


def all_frame_translation_escape(
    first,
    second,
    factor_polynomial,
    occurrence_factor,
    factor_occurrence,
    canonical,
    anchor_alignments,
    anchor_stabilizers,
):
    """Find a constant affine direction preserving both equations."""

    cache = {}
    for swapped, (left, right) in enumerate(((first, second), (second, first))):
        for kind, table in anchor_alignments.items():
            mapping = table.get(left)
            if mapping is None:
                continue
            moved_left = transform_factor(
                left, mapping, factor_occurrence, occurrence_factor
            )
            moved_right = transform_factor(
                right, mapping, factor_occurrence, occurrence_factor
            )
            if moved_left != canonical[kind]:
                raise AssertionError("translation-escape reframe missed its target")
            targets = {
                transform_factor(
                    moved_right,
                    symmetry,
                    factor_occurrence,
                    occurrence_factor,
                )
                for symmetry in anchor_stabilizers[kind]
            }
            for target in sorted(targets):
                key = moved_left, target
                if key not in cache:
                    cache[key] = translation_escape(
                        factor_polynomial[moved_left], factor_polynomial[target]
                    )
                vector = cache[key]
                if vector is not None:
                    return kind, bool(swapped), target, vector
    return None


def all_frame_scaling_escape(
    first,
    second,
    factor_polynomial,
    occurrence_factor,
    factor_occurrence,
    canonical,
    anchor_alignments,
    anchor_stabilizers,
):
    """Find a nontrivial coordinatewise torus preserving both zero sets."""

    cache = {}
    for swapped, (left, right) in enumerate(((first, second), (second, first))):
        for kind, table in anchor_alignments.items():
            mapping = table.get(left)
            if mapping is None:
                continue
            moved_left = transform_factor(
                left, mapping, factor_occurrence, occurrence_factor
            )
            moved_right = transform_factor(
                right, mapping, factor_occurrence, occurrence_factor
            )
            if moved_left != canonical[kind]:
                raise AssertionError("scaling-escape reframe missed its target")
            targets = {
                transform_factor(
                    moved_right,
                    symmetry,
                    factor_occurrence,
                    occurrence_factor,
                )
                for symmetry in anchor_stabilizers[kind]
            }
            for target in sorted(targets):
                key = moved_left, target
                if key not in cache:
                    cache[key] = scaling_escape(
                        factor_polynomial[moved_left], factor_polynomial[target]
                    )
                vector = cache[key]
                if vector is not None:
                    return kind, bool(swapped), target, vector
    return None


def audit_pairs(
    pair_orbits,
    factor_polynomial,
    occurrences,
    occurrence_factor,
    all_frames=False,
    progress=True,
):
    support_representatives = occurrence_representatives()
    representatives = {
        kind: occurrence_factor[occurrence]
        for kind, occurrence in support_representatives.items()
        if kind != 47
    }
    factors = parent_bracket_factors()
    factor_occurrence = factor_action_is_well_defined(
        occurrences, occurrence_factor
    )
    canonical, anchor_alignments, anchor_stabilizers = canonical_anchor_alignments(
        occurrences, occurrence_factor, factor_occurrence
    )
    certified = {}
    direct_count = 0
    reframed_count = 0
    all_frame_count = 0
    translation_count = 0
    scaling_count = 0
    residue = []
    for index, (kind, second) in enumerate(pair_orbits, 1):
        first = representatives[kind]
        first_polynomial = factor_polynomial[first]
        second_polynomial = factor_polynomial[second]
        certificate = direct_product_certificate(
            first_polynomial, second_polynomial, factors
        )
        if certificate is None:
            reframed = reframed_product_certificate(
                first,
                second,
                factors,
                factor_polynomial,
                occurrence_factor,
                factor_occurrence,
                canonical,
                anchor_alignments,
            )
            if reframed is None:
                if all_frames:
                    exhaustive = all_frame_product_certificate(
                        first,
                        second,
                        factors,
                        factor_polynomial,
                        occurrence_factor,
                        factor_occurrence,
                        canonical,
                        anchor_alignments,
                        anchor_stabilizers,
                    )
                else:
                    exhaustive = None
                if exhaustive is None:
                    if all_frames:
                        translation = all_frame_translation_escape(
                            first,
                            second,
                            factor_polynomial,
                            occurrence_factor,
                            factor_occurrence,
                            canonical,
                            anchor_alignments,
                            anchor_stabilizers,
                        )
                    else:
                        translation = None
                    if translation is not None:
                        certified[(kind, second)] = ("translation",) + translation
                        translation_count += 1
                    else:
                        if all_frames:
                            scaling = all_frame_scaling_escape(
                                first,
                                second,
                                factor_polynomial,
                                occurrence_factor,
                                factor_occurrence,
                                canonical,
                                anchor_alignments,
                                anchor_stabilizers,
                            )
                        else:
                            scaling = None
                        if scaling is not None:
                            certified[(kind, second)] = ("scaling",) + scaling
                            scaling_count += 1
                        else:
                            residue.append((kind, second))
                else:
                    certified[(kind, second)] = ("all_frames",) + exhaustive
                    all_frame_count += 1
            else:
                certified[(kind, second)] = ("reframed",) + reframed
                reframed_count += 1
        else:
            certified[(kind, second)] = ("direct",) + certificate
            direct_count += 1
        if progress and index % 500 == 0:
            print(
                f"audited {index}/{len(pair_orbits)} pair orbits: "
                f"certified={len(certified)}, residue={len(residue)}",
                flush=True,
            )
    return (
        certified,
        tuple(residue),
        direct_count,
        reframed_count,
        all_frame_count,
        translation_count,
        scaling_count,
    )


def semantic_digest(pair_orbits, certified, residue):
    digest = hashlib.sha256()
    residue = frozenset(residue)
    for key in pair_orbits:
        digest.update(repr(key).encode("ascii"))
        certificate = certified.get(key)
        if certificate is None:
            if key not in residue:
                raise AssertionError("unclassified pair orbit in digest")
            digest.update(b"R")
            continue
        digest.update(b"P")
        digest.update(repr(certificate).encode("ascii"))
    return digest.hexdigest()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--census-only",
        action="store_true",
        help="stop after the exact unordered S8 pair-orbit census",
    )
    parser.add_argument(
        "--all-frames",
        action="store_true",
        help="exhaust every stabilizer-equivalent canonical projective frame",
    )
    parser.add_argument(
        "--analysis-output",
        type=Path,
        help="optional NPZ path for the deterministic pair classification",
    )
    args = parser.parse_args()

    occurrences, occurrence_factor, factor_polynomial = factor_polynomials()
    pair_orbits, ordered_counts, orbit_sizes = pair_orbit_representatives(
        occurrences, occurrence_factor
    )
    burnside_factor_orbits, burnside_pair_orbits = burnside_pair_orbit_count(
        occurrences, occurrence_factor
    )
    if orbit_sizes != EXPECTED_FACTOR_ORBIT_SIZES:
        raise AssertionError("localized residual factor orbit sizes changed")
    if ordered_counts != EXPECTED_ORDERED_PAIR_ORBITS:
        raise AssertionError("ordered residual-factor pair orbit counts changed")
    if len(pair_orbits) != EXPECTED_PAIR_ORBITS:
        raise AssertionError("unordered residual-factor pair orbit count changed")
    if (burnside_factor_orbits, burnside_pair_orbits) != (6, EXPECTED_PAIR_ORBITS):
        raise AssertionError("anchored and Burnside pair-orbit censuses disagree")
    print("PASS labeled residual occurrences:", len(occurrences))
    print("PASS localized residual factors:", len(factor_polynomial))
    print("PASS factor-orbit sizes by canonical type:", orbit_sizes)
    print("PASS ordered pair-orbit counts by first wall type:", ordered_counts)
    print("PASS unordered distinct residual-factor pair orbits:", len(pair_orbits))
    print("PASS independent Burnside census: 6 factor orbits and", burnside_pair_orbits, "pair orbits")
    if args.census_only:
        return

    (
        certified,
        residue,
        direct_count,
        reframed_count,
        all_frame_count,
        translation_count,
        scaling_count,
    ) = audit_pairs(
        pair_orbits,
        factor_polynomial,
        occurrences,
        occurrence_factor,
        all_frames=args.all_frames,
    )
    digest = semantic_digest(pair_orbits, certified, residue)
    if direct_count != EXPECTED_PRIMARY_CERTIFICATES:
        raise AssertionError("primary canonical certificate count changed")
    if reframed_count != EXPECTED_REFRAMED_CERTIFICATES:
        raise AssertionError("reframed certificate count changed")
    if not args.all_frames:
        if len(residue) != EXPECTED_RESIDUE:
            raise AssertionError("reframed direct-product residue changed")
        if digest != EXPECTED_DIGEST:
            raise AssertionError("labeled-pair semantic digest changed")
    else:
        if all_frame_count != EXPECTED_ALL_FRAME_CERTIFICATES:
            raise AssertionError("full-frame certificate count changed")
        if translation_count != EXPECTED_TRANSLATION_ESCAPES:
            raise AssertionError("translation-escape count changed")
        if scaling_count != EXPECTED_SCALING_ESCAPES:
            raise AssertionError("scaling-escape count changed")
        if len(residue) != EXPECTED_PRE_SATURATION_RESIDUE:
            raise AssertionError("all-frame pair residue changed")
        if digest != EXPECTED_ALL_FRAME_DIGEST:
            raise AssertionError("all-frame labeled-pair semantic digest changed")

    (
        _representatives,
        _stabilizers,
        factor_alignment,
        _factor_occurrence,
        _orbit_sizes,
    ) = factor_orbit_data(occurrences, occurrence_factor)
    residue_types = Counter(
        (kind, factor_alignment[second][0]) for kind, second in residue
    )
    reframe_modes = Counter(
        (certificate[1], certificate[2])
        for certificate in certified.values()
        if certificate[0] == "reframed"
    )
    if args.analysis_output is not None:
        mode_code = {
            "direct": 1,
            "reframed": 2,
            "all_frames": 3,
            "translation": 4,
            "scaling": 5,
        }
        classification = np.asarray(
            [
                mode_code[certified[key][0]] if key in certified else 0
                for key in pair_orbits
            ],
            dtype=np.uint8,
        )
        args.analysis_output.parent.mkdir(parents=True, exist_ok=True)
        np.savez_compressed(
            args.analysis_output,
            pair_kind=np.asarray([key[0] for key in pair_orbits], dtype=np.uint8),
            pair_second_factor=np.asarray(
                [key[1] for key in pair_orbits], dtype=np.uint32
            ),
            classification=classification,
        )
        print("WROTE analysis classification:", args.analysis_output)
    print("PASS certified noncompact pair-wall orbits:", len(certified))
    print(
        "PASS exact parent-bracket-product Jacobian certificates:",
        direct_count + reframed_count + all_frame_count,
    )
    print("PASS certificates in primary canonical forms:", direct_count)
    print("PASS additional certificates after exact canonical reframing:", reframed_count)
    if args.all_frames:
        print("PASS additional certificates after full frame exhaustion:", all_frame_count)
        print("PASS common affine-translation escapes:", translation_count)
        print("PASS common weighted-torus escapes:", scaling_count)
    status_label = (
        "pre-saturation exact residue"
        if args.all_frames
        else "full exact residue"
    )
    print("STATUS", status_label + ":", len(residue))
    print(
        "STATUS residue by unordered factor-orbit types:",
        dict(sorted(residue_types.items())),
    )
    print(
        "PASS reframed certificates by (anchor type, swapped):",
        dict(sorted(reframe_modes.items())),
    )
    print("SEMANTIC SHA256:", digest)
    print("THEOREM every certified labeled pair-wall component is noncompact")
    print("CAVEAT residue means no listed certificate, not rank drop or compactness")


if __name__ == "__main__":
    main()
