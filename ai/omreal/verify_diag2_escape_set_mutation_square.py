#!/usr/bin/env python3
"""Exact common-shear audit around one generic type-37/type-44 node.

The stored 44->37->44 label cycle is deliberately nongeneric with respect to
all labeled residual factors.  This checker constructs a nearby exact node at
which precisely the canonical type-37 and type-44 factors vanish, verifies
the four adjacent compound chambers, and measures the complete-tope and
escape-mask changes across every edge.

This is a local mutation theorem/no-go, not residual-chamber coverage.
"""

from __future__ import annotations

from fractions import Fraction
import hashlib
from itertools import combinations
from math import comb, lcm

import DIAG2_PIVOT_LABELED_PAIR_ORBITS_VERIFY as labeled
import DIAG9_GRAPH_exact_topes as exact_topes
import four_chart_gate as gate
import verify_diag2_escape_set_atlas178 as atlas178
import verify_diag2_escape_set_topes as escape
from DIAG2_PIVOT_ALL_COMPACT_SECOND_WALL_VERIFY import (
    column_determinant,
    standard_columns,
)


VARIABLES = "abcdefghi"
CENTER = {
    key: Fraction(value)
    for key, value in {
        "a": "104671347209/204100224200",
        "b": "-2983/1000",
        "c": "-509/500",
        "d": "66134514061/255125280250",
        "e": "-991/1000",
        "f": "1997/1000",
        "g": "2007/1000",
        "h": "3009/1000",
        "i": "-2987/1000",
    }.items()
}
EPSILON = Fraction(1, 10**9)
EXPECTED_FACTOR_IDS = (2342, 3487)
EXPECTED_VALID = 75_026
EXPECTED_BAD = 48_914
EXPECTED_COMMON_BAD = 48_842
EXPECTED_DIGEST = "cfcaa8d8794655e9b8c480b40156ed044904530aa30354d0f52785403eb289ef"
EXPECTED_GERM_DIGEST = (
    "09de27c3c7460eee5ef8ffa5a3bab4c64dbe9337444aeeffa519751696b7ee0a"
)
EXPECTED_GERM_COUNTS = {
    "segments": 4,
    "target_linear_checks": 8,
    "residual_sign_checks": 106_952,
    "parent_sign_checks": 280,
    "maximum_residual_degree": 3,
    "maximum_parent_degree": 1,
    "maximum_subdivision_depth": 0,
    "subdivision_leaves": 107_232,
}


def poly_trim(polynomial):
    answer = [Fraction(value) for value in polynomial]
    while len(answer) > 1 and not answer[-1]:
        answer.pop()
    return tuple(answer or (Fraction(0),))


def poly_add(left, right):
    size = max(len(left), len(right))
    return poly_trim(
        (left[index] if index < len(left) else 0)
        + (right[index] if index < len(right) else 0)
        for index in range(size)
    )


def poly_multiply(left, right):
    answer = [Fraction(0)] * (len(left) + len(right) - 1)
    for left_degree, left_value in enumerate(left):
        for right_degree, right_value in enumerate(right):
            answer[left_degree + right_degree] += left_value * right_value
    return poly_trim(answer)


def poly_determinant(matrix):
    """Exact determinant over Q[t], used only for parent brackets."""
    if not matrix:
        return (Fraction(1),)
    answer = (Fraction(0),)
    for column, entry in enumerate(matrix[0]):
        minor = [row[:column] + row[column + 1 :] for row in matrix[1:]]
        term = poly_multiply(entry, poly_determinant(minor))
        if column & 1:
            term = tuple(-value for value in term)
        answer = poly_add(answer, term)
    return poly_trim(answer)


def segment_polynomial(polynomial, left, right):
    """Substitute ``left+t*(right-left)`` into a sparse 9-variate polynomial."""
    answer = (Fraction(0),)
    for monomial, coefficient in polynomial.items():
        term = (Fraction(coefficient),)
        for variable, exponent in zip(VARIABLES, monomial, strict=True):
            if not exponent:
                continue
            origin = left[variable]
            delta = right[variable] - origin
            factor = tuple(
                Fraction(comb(exponent, degree))
                * origin ** (exponent - degree)
                * delta**degree
                for degree in range(exponent + 1)
            )
            term = poly_multiply(term, factor)
        answer = poly_add(answer, term)
    return poly_trim(answer)


def bernstein_coefficients(polynomial):
    """Power-to-Bernstein conversion on [0,1], in the actual degree."""
    degree = len(polynomial) - 1
    return tuple(
        sum(
            polynomial[power]
            * Fraction(comb(index, power), comb(degree, power))
            for power in range(index + 1)
        )
        for index in range(degree + 1)
    )


def subdivide_bernstein_half(coefficients):
    """Exact de Casteljau subdivision of Bernstein data at t=1/2."""
    levels = [tuple(coefficients)]
    while len(levels[-1]) > 1:
        previous = levels[-1]
        levels.append(
            tuple(
                (previous[index] + previous[index + 1]) / 2
                for index in range(len(previous) - 1)
            )
        )
    degree = len(coefficients) - 1
    left = tuple(levels[level][0] for level in range(degree + 1))
    right = tuple(levels[degree - index][index] for index in range(degree + 1))
    return left, right


def certify_bernstein_sign(polynomial, desired, maximum_depth=16):
    """Prove a strict sign on [0,1] by exact subdivided Bernstein hulls."""
    if desired not in (-1, 1):
        raise AssertionError("desired sign must be +/-1")
    initial = bernstein_coefficients(poly_trim(polynomial))

    def recurse(coefficients, depth):
        if all(desired * value > 0 for value in coefficients):
            return depth, 1
        if depth == maximum_depth:
            raise AssertionError(
                "Bernstein sign subdivision did not certify the segment"
            )
        left, right = subdivide_bernstein_half(coefficients)
        left_depth, left_leaves = recurse(left, depth + 1)
        right_depth, right_leaves = recurse(right, depth + 1)
        return max(left_depth, right_depth), left_leaves + right_leaves

    return recurse(initial, 0)


def segment_parent_bracket(left, right, basis):
    left_columns = standard_columns(left)
    right_columns = standard_columns(right)
    matrix = [
        [
            poly_trim(
                (
                    left_columns[column][row],
                    right_columns[column][row] - left_columns[column][row],
                )
            )
            for column in basis
        ]
        for row in range(4)
    ]
    return poly_determinant(matrix)


def update_polynomial_digest(digest, polynomial):
    digest.update(len(polynomial).to_bytes(2, "little"))
    for coefficient in polynomial:
        digest.update(str(coefficient.numerator).encode("ascii") + b"/")
        digest.update(str(coefficient.denominator).encode("ascii") + b";")


def verify_local_germ_segments(factor_polynomials, factor_ids, values, sign_pairs):
    """Certify that four exact samples lie in the four local node germs.

    Every non-target residual factor and all 70 parent brackets receive a
    strict exact Bernstein sign certificate on the radial segment from
    ``CENTER``.  The two target factors are checked to be the intended linear
    transverse coordinates on each segment.
    """
    if set(values) != set(sign_pairs):
        raise AssertionError("segment sample/sign labels disagree")
    target_ids = set(factor_ids)
    digest = hashlib.sha256(b"diag2-generic-37-44-local-germs-v1\0")
    residual_checks = 0
    parent_checks = 0
    maximum_residual_degree = 0
    maximum_parent_degree = 0
    maximum_subdivision_depth = 0
    subdivision_leaves = 0

    for name in sign_pairs:
        point = values[name]
        expected_target_signs = sign_pairs[name]
        digest.update(str(name).encode("ascii") + b"\0")
        for factor_id, polynomial in enumerate(factor_polynomials):
            restricted = segment_polynomial(polynomial, CENTER, point)
            update_polynomial_digest(digest, restricted)
            maximum_residual_degree = max(
                maximum_residual_degree, len(restricted) - 1
            )
            if factor_id in target_ids:
                target_index = factor_ids.index(factor_id)
                expected = (
                    Fraction(0),
                    expected_target_signs[target_index] * EPSILON,
                )
                if restricted != expected:
                    raise AssertionError(
                        f"target factor {factor_id} is not the intended linear "
                        f"coordinate on segment {name}: {restricted}"
                    )
                continue
            desired = 1 if restricted[0] > 0 else -1
            if not restricted[0]:
                raise AssertionError(
                    f"nontarget residual factor {factor_id} vanishes at CENTER"
                )
            depth, leaves = certify_bernstein_sign(restricted, desired)
            maximum_subdivision_depth = max(maximum_subdivision_depth, depth)
            subdivision_leaves += leaves
            residual_checks += 1

        for basis in combinations(range(8), 4):
            restricted = segment_parent_bracket(CENTER, point, basis)
            update_polynomial_digest(digest, restricted)
            maximum_parent_degree = max(maximum_parent_degree, len(restricted) - 1)
            desired = 1 if restricted[0] > 0 else -1
            if not restricted[0]:
                raise AssertionError(f"parent bracket {basis} vanishes at CENTER")
            depth, leaves = certify_bernstein_sign(restricted, desired)
            maximum_subdivision_depth = max(maximum_subdivision_depth, depth)
            subdivision_leaves += leaves
            parent_checks += 1

    report = {
        "segments": len(values),
        "target_linear_checks": len(values) * len(factor_ids),
        "residual_sign_checks": residual_checks,
        "parent_sign_checks": parent_checks,
        "maximum_residual_degree": maximum_residual_degree,
        "maximum_parent_degree": maximum_parent_degree,
        "maximum_subdivision_depth": maximum_subdivision_depth,
        "subdivision_leaves": subdivision_leaves,
        "digest": digest.hexdigest(),
    }
    if (
        {key: report[key] for key in EXPECTED_GERM_COUNTS}
        != EXPECTED_GERM_COUNTS
    ):
        raise AssertionError(f"generic local-germ certificate counts changed: {report}")
    if report["digest"] != EXPECTED_GERM_DIGEST:
        raise AssertionError(f"generic local-germ certificate changed: {report}")
    return report


def evaluate(polynomial, values):
    answer = Fraction(0)
    for monomial, coefficient in polynomial.items():
        term = Fraction(coefficient)
        for variable, exponent in zip(VARIABLES, monomial, strict=True):
            term *= values[variable] ** exponent
        answer += term
    return answer


def affine_gradient(polynomial, variable):
    shifted = dict(CENTER)
    shifted[variable] += 1
    return evaluate(polynomial, shifted) - evaluate(polynomial, CENTER)


def adjacent_point(first_sign, second_sign, factors):
    first, second = factors
    first_a = affine_gradient(first, "a")
    first_d = affine_gradient(first, "d")
    second_a = affine_gradient(second, "a")
    second_d = affine_gradient(second, "d")
    determinant = first_a * second_d - first_d * second_a
    if not determinant:
        raise AssertionError("the type-37/type-44 node is not transverse")
    first_value = first_sign * EPSILON
    second_value = second_sign * EPSILON
    delta_a = (first_value * second_d - first_d * second_value) / determinant
    delta_d = (first_a * second_value - first_value * second_a) / determinant
    answer = dict(CENTER)
    answer["a"] += delta_a
    answer["d"] += delta_d
    if evaluate(first, answer) != first_value:
        raise AssertionError("wrong type-37 side value")
    if evaluate(second, answer) != second_value:
        raise AssertionError("wrong type-44 side value")
    return answer


def integer_matrix(values):
    columns = []
    for column in standard_columns(values):
        denominator = 1
        for value in column:
            denominator = lcm(denominator, value.denominator)
        columns.append(tuple(int(value * denominator) for value in column))
    return tuple(
        tuple(columns[column][row] for column in range(8)) for row in range(4)
    )


def combined_digest(chambers, edge_reports):
    digest = hashlib.sha256()
    digest.update(b"diag2-escape-mutation-square-v1\0")
    for name in ("++", "+-", "--", "-+"):
        report = chambers[name]
        digest.update(name.encode("ascii") + b"\0")
        digest.update(bytes.fromhex(report["escape_digest"]))
        for key in ("topes", "bad", "minimum_escape", "minimum_overlap"):
            digest.update(int(report[key]).to_bytes(8, "little"))
    for report in edge_reports:
        digest.update(repr(report).encode("ascii") + b"\0")
    return digest.hexdigest()


def main():
    occurrences, occurrence_factor, factor_polynomials = labeled.factor_polynomials()
    representatives = labeled.occurrence_representatives()
    factor_ids = (
        occurrence_factor[representatives[37]],
        occurrence_factor[representatives[44]],
    )
    if factor_ids != EXPECTED_FACTOR_IDS:
        raise AssertionError(f"canonical factor IDs changed: {factor_ids}")
    factors = tuple(factor_polynomials[index] for index in factor_ids)

    center_zeros = tuple(
        index
        for index, polynomial in enumerate(factor_polynomials)
        if evaluate(polynomial, CENTER) == 0
    )
    if center_zeros != factor_ids:
        raise AssertionError(f"the proposed node has extra residual zeros: {center_zeros}")
    center_brackets = tuple(
        column_determinant(standard_columns(CENTER), basis)
        for basis in combinations(range(8), 4)
    )
    if not all(center_brackets):
        raise AssertionError("the proposed node lies on a parent wall")

    sign_pairs = {"++": (1, 1), "+-": (1, -1), "--": (-1, -1), "-+": (-1, 1)}
    values = {
        name: adjacent_point(first, second, factors)
        for name, (first, second) in sign_pairs.items()
    }
    germ_report = verify_local_germ_segments(
        factor_polynomials, factor_ids, values, sign_pairs
    )
    matrices = {name: integer_matrix(point) for name, point in values.items()}
    parent_signs = exact_topes.parent_signs(matrices["++"])
    for name, matrix in matrices.items():
        if exact_topes.parent_signs(matrix) != parent_signs:
            raise AssertionError(f"chamber {name} changed parent chirotope")

    factor_signs = {
        name: tuple(evaluate(polynomial, point) > 0 for polynomial in factor_polynomials)
        for name, point in values.items()
    }
    edges = (
        ("++", "+-", factor_ids[1]),
        ("+-", "--", factor_ids[0]),
        ("--", "-+", factor_ids[1]),
        ("-+", "++", factor_ids[0]),
    )
    for left, right, expected_factor in edges:
        changed = tuple(
            index
            for index, (first, second) in enumerate(
                zip(factor_signs[left], factor_signs[right], strict=True)
            )
            if first != second
        )
        if changed != (expected_factor,):
            raise AssertionError(f"edge {left}->{right} flips factors {changed}")

    parent = "".join("+" if sign > 0 else "-" for sign in parent_signs)
    _, signatures = gate.enumerate_extensions(parent)
    if len(signatures) != EXPECTED_VALID:
        raise AssertionError("mutation-square extension count changed")

    chambers = {}
    records_by_chamber = {}
    topes_by_chamber = {}
    for name in ("++", "+-", "--", "-+"):
        rows = exact_topes.derived_rows(matrices[name])
        enumerated = exact_topes.enumerate_topes(rows, dimension=4)
        exact_topes.verify_topes(rows, enumerated)
        topes = set(enumerated)
        if len(topes) != 26_112:
            raise AssertionError(f"chamber {name} has wrong tope count")
        prepared = escape.prepare_directions(topes)
        records = [
            (signature, escape.escape_mask(signature, prepared))
            for signature in signatures
            if signature not in topes
        ]
        if len(records) != EXPECTED_BAD:
            raise AssertionError(f"chamber {name} has wrong bad count")
        if escape.prove_pairwise_intersection(records) is not None:
            raise AssertionError(f"chamber {name} has a disjoint escape pair")
        minimum_overlap, _witness = atlas178.minimum_pair_overlap(records)
        report = {
            "topes": len(topes),
            "bad": len(records),
            "minimum_escape": min(mask.bit_count() for _, mask in records),
            "minimum_overlap": minimum_overlap,
            "escape_digest": escape.semantic_digest(
                f"diag2-mutation-square-{name}", records
            ),
        }
        if (report["minimum_escape"], report["minimum_overlap"]) != (52, 8):
            raise AssertionError(f"chamber {name} quantitative margin changed")
        chambers[name] = report
        records_by_chamber[name] = dict(records)
        topes_by_chamber[name] = topes

    expected_edges = (
        ("++", "+-", 72, 72, 1_410, 27, 26),
        ("+-", "--", 72, 72, 1_238, 28, 27),
        ("--", "-+", 72, 72, 1_410, 26, 27),
        ("-+", "++", 72, 72, 1_238, 27, 28),
    )
    edge_reports = []
    for expected in expected_edges:
        left, right = expected[:2]
        removed = len(topes_by_chamber[left] - topes_by_chamber[right])
        added = len(topes_by_chamber[right] - topes_by_chamber[left])
        common = set(records_by_chamber[left]) & set(records_by_chamber[right])
        if len(common) != EXPECTED_COMMON_BAD:
            raise AssertionError(f"edge {left}->{right} common-bad count changed")
        changed = 0
        maximum_loss = 0
        maximum_gain = 0
        for signature in common:
            first = records_by_chamber[left][signature]
            second = records_by_chamber[right][signature]
            changed += first != second
            maximum_loss = max(maximum_loss, (first & ~second).bit_count())
            maximum_gain = max(maximum_gain, (second & ~first).bit_count())
        report = (
            left,
            right,
            removed,
            added,
            changed,
            maximum_loss,
            maximum_gain,
        )
        if report != expected:
            raise AssertionError(f"edge mutation summary changed: {report}")
        edge_reports.append(report)

    digest = combined_digest(chambers, tuple(edge_reports))
    if EXPECTED_DIGEST is not None and digest != EXPECTED_DIGEST:
        raise AssertionError(f"mutation-square digest changed: {digest}")
    print("PASS exact generic node has only residual factors 2342/3487")
    print("PASS four sample segments stay in their local node germs:", germ_report)
    print("PASS four adjacent chambers have 26,112 topes and only intended edge flips")
    print("PASS all 48,914 bad-signature escape families pairwise intersect; minimum 8")
    print("PASS each generic edge exchanges 72 topes per side:", tuple(edge_reports))
    print("SEMANTIC", digest)
    print("SCOPE one exact mutation square; no residual-chamber coverage")


if __name__ == "__main__":
    main()
