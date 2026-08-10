#!/usr/bin/env python3
"""Exact safe-loss separator bifurcation at extremal parent 187.

The complete all-parent atlas has three antipodal pair orbits of minimum
escape overlap six at catalog parent 187.  This checker puts that exact
parent into the standard nine-coordinate chart and constructs an isolated
type-50 residual edge.  Across the edge, every new minimal separator for the
six tracked endpoints contains an old minimal separator.  The tope-restriction
criterion then makes every escape mask monotone: the common overlap cannot
decrease.  One pair crosses from the four-singleton regime to a dominated
non-singleton regime and its overlap rises from six to nine.

This is one exact labeled residual edge, not universal transition coverage
and not a proof of diagonal two.
"""

from __future__ import annotations

from fractions import Fraction
import hashlib
from math import lcm

import DIAG2_PIVOT_LABELED_PAIR_ORBITS_VERIFY as labeled
import DIAG9_GRAPH_exact_topes as exact_topes
import DIAG9_GRAPH_parent860_star as coordinate_star
import verify_diag2_common_shear_parent2604 as parent2604
import verify_diag2_escape_minimal_separators as minimal
import verify_diag2_escape_set_topes as escape
import verify_diag2_near_counterexample_separators as near_separators


PARENT_INDEX = 187
VARIABLE = 4  # e in the standard a,...,i chart
FACTOR_ID = 11_045
FACTOR_KIND = 50
FACTOR_OCCURRENCE = (1, 28, 33, 49)
EPSILON = Fraction(1, 100_000)
EXPECTED_ROOT = Fraction(
    -525_662_980_838_944_803_588_912_159_332_931_345_235_344,
    41_907_898_019_468_964_511_553_138_173_016_456_983_893_305,
)
EXPECTED_MAPPED_PAIRS = (
    (41_791_434_804_464_172, 69_849_397_930_972_629, 6),
    (41_224_216_731_022_549, 41_224_087_949_575_724, 6),
    (68_230_936_274_949_461, 70_482_716_760_692_055, 6),
)
EXPECTED_EXCHANGE = (2, 2)
EXPECTED_SIDE_OVERLAPS = ((9, 6, 6), (6, 6, 6))
EXPECTED_SIDE_ESCAPE_SIZES = (
    ((61, 56), (56, 56), (56, 56)),
    ((56, 56), (56, 56), (56, 56)),
)
EXPECTED_DIGEST = "fbd1109b668d41da64b1657a37d9b12b602ec68ab30a4650f051aacb88c6ee2a"


def determinant(matrix):
    matrix = tuple(tuple(map(Fraction, row)) for row in matrix)
    if len(matrix) == 1:
        return matrix[0][0]
    return sum(
        (-1 if column & 1 else 1)
        * value
        * determinant(
            tuple(row[:column] + row[column + 1 :] for row in matrix[1:])
        )
        for column, value in enumerate(matrix[0])
    )


def invert(square):
    size = len(square)
    work = [
        list(map(Fraction, row))
        + [Fraction(int(row_index == column)) for column in range(size)]
        for row_index, row in enumerate(square)
    ]
    for column in range(size):
        pivot = next(
            row for row in range(column, size) if work[row][column]
        )
        work[column], work[pivot] = work[pivot], work[column]
        scale = work[column][column]
        work[column] = [value / scale for value in work[column]]
        for row in range(size):
            if row == column:
                continue
            scale = work[row][column]
            work[row] = [
                value - scale * pivot_value
                for value, pivot_value in zip(work[row], work[column])
            ]
    return tuple(tuple(row[size:]) for row in work)


def normalize_parent(parent):
    """Return standard coordinates and the induced extension-sign action."""

    source = tuple(tuple(map(Fraction, row)) for row in parent)
    basis = tuple(tuple(row[column] for column in range(4)) for row in source)
    inverse = invert(basis)
    reduced = tuple(
        tuple(
            sum(
                inverse[row][inner] * source[inner][column]
                for inner in range(4)
            )
            for column in range(8)
        )
        for row in range(4)
    )
    fifth = tuple(reduced[row][4] for row in range(4))
    if not all(fifth):
        raise AssertionError("the fifth frame column has a zero coordinate")
    matrix = [
        [reduced[row][column] / fifth[row] for column in range(8)]
        for row in range(4)
    ]
    column_scales = [Fraction(1)] * 8
    for column in range(4):
        matrix[column][column] *= fifth[column]
        column_scales[column] = fifth[column]
    for column in range(5, 8):
        scale = matrix[0][column]
        if not scale:
            raise AssertionError("a nonframe column is at projective infinity")
        for row in range(4):
            matrix[row][column] /= scale
        column_scales[column] = 1 / scale

    expected_prefix = (
        (1, 0, 0, 0, 1),
        (0, 1, 0, 0, 1),
        (0, 0, 1, 0, 1),
        (0, 0, 0, 1, 1),
    )
    prefix = tuple(
        tuple(matrix[row][column] for column in range(5))
        for row in range(4)
    )
    if prefix != expected_prefix:
        raise AssertionError("projective normalization missed the standard frame")
    coordinates = tuple(
        matrix[row][column]
        for column in range(5, 8)
        for row in range(1, 4)
    )

    left_map = tuple(
        tuple(inverse[row][column] / fifth[row] for column in range(4))
        for row in range(4)
    )
    left_sign = 1 if determinant(left_map) > 0 else -1
    multipliers = []
    for triple in exact_topes.TRIPLES:
        sign = left_sign
        for column in triple:
            sign *= 1 if column_scales[column] > 0 else -1
        multipliers.append(sign)
    return coordinates, tuple(multipliers)


def map_signature(signature, multipliers):
    answer = 0
    for index, multiplier in enumerate(multipliers):
        source_sign = 1 if signature & (1 << index) else -1
        if source_sign * multiplier > 0:
            answer |= 1 << index
    return answer


def polynomial_value(polynomial, parameter):
    answer = Fraction(0)
    for coefficient in reversed(polynomial):
        answer = answer * parameter + coefficient
    return answer


def sign(value):
    return (value > 0) - (value < 0)


def integer_matrix(coordinates):
    rational = coordinate_star.matrix_from_coordinates(coordinates)
    return tuple(tuple(map(int, row)) for row in rational)


def tope_table(coordinates, expected_parent, label):
    matrix = integer_matrix(coordinates)
    if exact_topes.parent_signs(matrix) != expected_parent:
        raise AssertionError(f"{label}: endpoint left the parent cell")
    rows = exact_topes.derived_rows(matrix)
    topes = exact_topes.enumerate_topes(rows, dimension=4)
    exact_topes.verify_topes(rows, topes)
    if len(topes) != 26_112:
        raise AssertionError(f"{label}: endpoint is not a generic residual chamber")
    return tuple(sorted(topes))


def separator_profile(signature, indexes):
    answer = []
    for source in range(1, 9):
        _raw, separators = minimal.minimal_separators(
            signature, indexes[source]
        )
        answer.append(
            tuple(
                tuple(minimal.support_indices(separator))
                for separator in separators
            )
        )
    return tuple(answer)


def dominates(old_profile, new_profile):
    """Every new separator contains an old separator, source by source."""

    for old_family, new_family in zip(old_profile, new_profile, strict=True):
        old_sets = tuple(map(frozenset, old_family))
        for new_separator in map(frozenset, new_family):
            if not any(old_separator <= new_separator for old_separator in old_sets):
                return False
    return True


def semantic_digest(center, sides, topes, records):
    digest = hashlib.sha256()
    digest.update(b"diag2-extremal-safe-loss-edge-v1\0")
    for point in (center,) + sides:
        for value in point:
            digest.update(str(value.numerator).encode("ascii") + b"/")
            digest.update(str(value.denominator).encode("ascii") + b"\0")
    for table in topes:
        for tope in table:
            digest.update(int(tope).to_bytes(8, "little"))
    for side_records in records:
        for signature, mask, profile in side_records:
            digest.update(int(signature).to_bytes(8, "little"))
            digest.update(int(mask).to_bytes(16, "little"))
            digest.update(repr(profile).encode("ascii") + b"\0")
    return digest.hexdigest()


def main():
    atlas, by_index, active = near_separators.load_atlas()
    del atlas
    task = by_index[PARENT_INDEX]
    atlas_record = active[PARENT_INDEX]
    raw_pairs = tuple(
        tuple(pair) for pair in atlas_record["pairs"] if pair[2] == 6
    )
    if len(raw_pairs) != 3:
        raise AssertionError("parent 187 no longer has three overlap-six pairs")

    coordinates, multipliers = normalize_parent(task["matrix"])
    pairs = tuple(
        (map_signature(left, multipliers), map_signature(right, multipliers), overlap)
        for left, right, overlap in raw_pairs
    )
    if pairs != EXPECTED_MAPPED_PAIRS:
        raise AssertionError(f"mapped parent-187 pair atlas changed: {pairs}")

    occurrences, occurrence_factor, factor_polynomials = labeled.factor_polynomials()
    _representatives, _stabilizers, alignment, factor_occurrence, _sizes = (
        labeled.factor_orbit_data(occurrences, occurrence_factor)
    )
    if alignment[FACTOR_ID][0] != FACTOR_KIND:
        raise AssertionError("selected residual factor changed incidence type")
    if factor_occurrence[FACTOR_ID] != FACTOR_OCCURRENCE:
        raise AssertionError("selected residual factor occurrence changed")

    restrictions = tuple(
        coordinate_star.restrict_polynomial(polynomial, VARIABLE, coordinates)
        for polynomial in factor_polynomials
    )
    target = restrictions[FACTOR_ID]
    if len(target) != 2 or target[1] != 1:
        raise AssertionError("selected type-50 restriction is not monic affine")
    root = -target[0]
    if root != EXPECTED_ROOT:
        raise AssertionError(f"selected residual root changed: {root}")

    center = list(coordinates)
    center[VARIABLE] += root
    center = tuple(center)
    minus = list(center)
    plus = list(center)
    minus[VARIABLE] -= EPSILON
    plus[VARIABLE] += EPSILON
    sides = (tuple(minus), tuple(plus))

    center_signs = tuple(
        sign(polynomial_value(polynomial, root))
        for polynomial in restrictions
    )
    if tuple(index for index, value in enumerate(center_signs) if not value) != (
        FACTOR_ID,
    ):
        raise AssertionError("wall center does not have one residual zero")
    side_signs = tuple(
        tuple(
            sign(polynomial_value(polynomial, root + direction * EPSILON))
            for polynomial in restrictions
        )
        for direction in (-1, 1)
    )
    if any(not value for signs in side_signs for value in signs):
        raise AssertionError("a selected endpoint lies on a residual wall")
    changed = tuple(
        index
        for index, values in enumerate(zip(*side_signs, strict=True))
        if values[0] != values[1]
    )
    if changed != (FACTOR_ID,):
        raise AssertionError(f"endpoint perturbation flips factors {changed}")
    if any(
        center_signs[index] != side_signs[0][index]
        or center_signs[index] != side_signs[1][index]
        for index in range(len(restrictions))
        if index != FACTOR_ID
    ):
        raise AssertionError("a nonselected factor changes in the wall germ")

    center_parent = exact_topes.parent_signs(integer_matrix(center))
    side_topes = tuple(
        tope_table(point, center_parent, label)
        for point, label in zip(sides, ("minus", "plus"), strict=True)
    )
    minus_set, plus_set = map(set, side_topes)
    exchange = (len(minus_set - plus_set), len(plus_set - minus_set))
    if exchange != EXPECTED_EXCHANGE:
        raise AssertionError(f"residual tope exchange changed: {exchange}")

    records = []
    side_overlaps = []
    side_escape_sizes = []
    for table in side_topes:
        if any(signature in table for pair in pairs for signature in pair[:2]):
            raise AssertionError("a tracked endpoint ceased to be bad")
        prepared = escape.prepare_directions(table)
        indexes = minimal.build_source_indexes(table)
        side_records = []
        by_signature = {}
        for signature in sorted({value for pair in pairs for value in pair[:2]}):
            mask = escape.escape_mask(signature, prepared)
            profile = separator_profile(signature, indexes)
            minimal_mask = minimal.escape_mask_from_minimal_separators(
                signature, indexes
            )[0]
            if mask != minimal_mask:
                raise AssertionError("minimal separators reconstructed a wrong mask")
            side_records.append((signature, mask, profile))
            by_signature[signature] = (mask, profile)
        records.append(tuple(side_records))
        overlaps = []
        sizes = []
        for left, right, _expected in pairs:
            left_mask = by_signature[left][0]
            right_mask = by_signature[right][0]
            overlaps.append((left_mask & right_mask).bit_count())
            sizes.append((left_mask.bit_count(), right_mask.bit_count()))
        side_overlaps.append(tuple(overlaps))
        side_escape_sizes.append(tuple(sizes))

    if tuple(side_overlaps) != EXPECTED_SIDE_OVERLAPS:
        raise AssertionError(f"edge overlap profile changed: {side_overlaps}")
    if tuple(side_escape_sizes) != EXPECTED_SIDE_ESCAPE_SIZES:
        raise AssertionError(f"edge escape-size profile changed: {side_escape_sizes}")

    minus_records = {signature: (mask, profile) for signature, mask, profile in records[0]}
    plus_records = {signature: (mask, profile) for signature, mask, profile in records[1]}
    if set(minus_records) != set(plus_records):
        raise AssertionError("the two edge decorations disagree")
    strict = 0
    for signature in sorted(plus_records):
        plus_mask, plus_profile = plus_records[signature]
        minus_mask, minus_profile = minus_records[signature]
        if not dominates(plus_profile, minus_profile):
            raise AssertionError("a safe-loss separator lacks an old subset")
        if plus_mask & ~minus_mask:
            raise AssertionError("separator dominance failed escape monotonicity")
        strict += plus_mask != minus_mask
    if strict != 1:
        raise AssertionError("the safe-loss edge should strictly expand one endpoint")

    digest = semantic_digest(center, sides, side_topes, tuple(records))
    if digest != EXPECTED_DIGEST:
        raise AssertionError(f"safe-loss semantic digest changed: {digest}")

    print("PASS parent 187 has three mapped overlap-six pair orbits")
    print(
        "PASS isolated type-50 factor 11045 at one exact rational wall root; "
        "endpoint exchange 2/2"
    )
    print("PASS all six tracked endpoints remain bad on both sides")
    print("PASS every minus-side separator contains a plus-side separator")
    print("THEOREM all six escape masks are monotone across the safe-loss edge")
    print("THEOREM tracked pair overlaps: (6,6,6) -> (9,6,6)")
    print("SEMANTIC", digest)
    print("SCOPE one exact labeled type-50 edge; diagonal two remains open")


if __name__ == "__main__":
    main()
