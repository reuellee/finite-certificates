#!/usr/bin/env python3
"""Exact replay of the primitive-direction double-graph structural layer."""

from __future__ import annotations

import hashlib
from math import comb
from pathlib import Path
import sys


HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import DIAG2_PIVOT_LABELED_PAIR_ORBITS_VERIFY as labeled  # noqa: E402
import DIAG2_PIVOT_REPRESENTATIVE_GRADIENT_VERIFY as gradient  # noqa: E402
import DIAG2_PIVOT_REPRESENTATIVE_TRIPLES_VERIFY as triples  # noqa: E402
import verify_diag2_pivot_all_pair_fibers as fibers  # noqa: E402
import verify_diag3_triple_double_graph_scan as double_graph  # noqa: E402
import verify_residual_log_binomials as poly  # noqa: E402


# Compact positive records: row, anchor/coset transport, second graph, sparse
# primitive direction, scalar, and complete restricted-parent product.
RECORDS = (
    ((5563, 2048, 8270), (1, 0, 0, 26168, 14805, 2, 4, 7, 1, 1, ('1346', '3478'))),
    ((5563, 2048, 8404), (1, 0, 0, 26168, 14694, 2, 4, 7, 1, 1, ('1346', '3478'))),
    ((5563, 2515, 18864), (0, 0, 0, 2515, 18864, 6, 4, 7, 1, 1, ('2367', '2456'))),
    ((5563, 2519, 12602), (0, 2, 0, 22812, 18864, 6, 4, 7, 1, -1, ('1236', '1237', '1238', '2456'))),
    ((5563, 2519, 13917), (0, 2, 0, 22812, 15003, 6, 4, 7, 1, -1, ('1236', '1237', '1238', '2456'))),
    ((5563, 5324, 11533), (1, 2, 0, 24358, 23255, 6, 4, 7, 1, -1, ('1237', '1246', '2356', '2358'))),
    ((5563, 5324, 11747), (1, 2, 0, 24358, 20518, 6, 4, 7, 1, -1, ('1237', '1246', '2356', '2358'))),
    ((5563, 5324, 12016), (1, 2, 0, 24358, 23279, 6, 4, 7, 1, -1, ('1237', '1246', '2356', '2358'))),
    ((5563, 5324, 12427), (1, 2, 0, 24358, 20519, 6, 4, 7, 1, -1, ('1237', '1246', '2356', '2358'))),
    ((5563, 5324, 21491), (1, 2, 0, 24358, 18864, 6, 4, 7, 1, -1, ('1237', '1246', '2356', '2358'))),
    ((5563, 5324, 22241), (1, 2, 0, 24358, 15003, 6, 4, 7, 1, -1, ('1237', '1246', '2356', '2358'))),
    ((5563, 6031, 21449), (2, 2, 1, 14135, 18864, 6, 4, 7, 1, -1, ('1236', '2357', '2456'))),
    ((5563, 6034, 23491), (2, 2, 1, 14076, 20518, 6, 4, 7, 1, -1, ('1236', '1237', '2358', '2456'))),
    ((5563, 6409, 17065), (0, 2, 1, 14135, 20518, 6, 4, 7, 1, -1, ('1236', '2357', '2456'))),
    ((5563, 6542, 21449), (2, 2, 1, 14076, 18864, 6, 4, 7, 1, -1, ('1236', '1237', '2358', '2456'))),
    ((5563, 6660, 17065), (0, 2, 1, 14135, 20519, 6, 4, 7, 1, -1, ('1236', '2357', '2456'))),
    ((5563, 6660, 22799), (0, 2, 1, 14076, 20519, 6, 4, 7, 1, -1, ('1236', '1237', '2358', '2456'))),
    ((5563, 8258, 20280), (2, 2, 1, 26100, 18864, 6, 4, 7, 1, -1, ('1237', '1246', '2368'))),
    ((5563, 8258, 21449), (2, 2, 1, 26107, 18864, 6, 4, 7, 1, -1, ('1237', '1238', '1246', '2356'))),
    ((5563, 8265, 20280), (2, 2, 1, 25315, 18864, 6, 4, 7, 1, -1, ('1237', '1246', '2356'))),
    ((5563, 8265, 21449), (2, 2, 1, 25210, 18864, 6, 4, 7, 1, 1, ('1246', '2367'))),
)

KIND = 50
FIRST_PIVOT = 3
EXPECTED_SEMANTIC = "68116c422a26d570de424cc510d397f2637cc205dbc6e6d97ba618be6daffd72"


def transform_factor(factor, mapping, factor_occurrence, occurrence_factor):
    occurrence = factor_occurrence[factor]
    return occurrence_factor[tuple(sorted(mapping[index] for index in occurrence))]


def directional(polynomial, left, right, sign):
    return poly.add(
        gradient.derivative(polynomial, left),
        poly.multiply(poly.constant(sign), gradient.derivative(polynomial, right)),
    )


def shear(polynomial, left, right, sign):
    """Pull back by x_left=t, x_right=s+sign*t (determinant one)."""
    answer = poly.constant(0)
    for monomial, coefficient in polynomial.items():
        left_exponent = monomial[left]
        right_exponent = monomial[right]
        base = list(monomial)
        base[left] = base[right] = 0
        for t_exponent in range(right_exponent + 1):
            transformed = list(base)
            transformed[left] = left_exponent + t_exponent
            transformed[right] = right_exponent - t_exponent
            value = coefficient * comb(right_exponent, t_exponent)
            if sign < 0 and t_exponent & 1:
                value = -value
            answer = poly.add(answer, {tuple(transformed): value})
    return answer


def replay_type50_overlap() -> int:
    coordinate_rows = double_graph.generic_certificate_rows()
    overlap = coordinate_rows & {row for row, _record in RECORDS}
    if len(overlap) != len(RECORDS):
        raise AssertionError("primitive-direction rows are not all subsumed")
    return len(overlap)


def main():
    occurrences, occurrence_factor, factor_polynomials = labeled.factor_polynomials()
    factor_occurrence = labeled.factor_action_is_well_defined(
        occurrences, occurrence_factor
    )
    canonical, alignments, stabilizers = labeled.canonical_anchor_alignments(
        occurrences, occurrence_factor, factor_occurrence
    )
    parents = labeled.parent_bracket_factors()
    anchor = factor_polynomials[canonical[KIND]]
    slope1, constant1 = fibers.pivot_split(anchor, FIRST_PIVOT)
    if poly.add(
        poly.multiply(slope1, poly.variable(FIRST_PIVOT)), constant1
    ) != anchor:
        raise AssertionError("first graph reconstruction changed")
    if triples.bracket_factorization(slope1, parents, depth=20) is None:
        raise AssertionError("first slope is not a parent unit")
    numerator1 = poly.negative(constant1)
    restricted = tuple(
        fibers.graph_restrict(polynomial, FIRST_PIVOT, slope1, numerator1)
        for polynomial in factor_polynomials
    )
    restricted_parents = {}
    for label, parent, _sign in parents:
        value = fibers.graph_restrict(parent, FIRST_PIVOT, slope1, numerator1)
        if not value:
            raise AssertionError(f"parent {label} vanishes on first graph")
        if len(value) == 1 and poly.ZERO_EXPONENT in value:
            continue
        restricted_parents[label] = value

    semantic = hashlib.sha256(b"diag3-primitive-direction-double-graph-exact-v1\0")
    seen = set()
    for number, (row, record) in enumerate(RECORDS):
        (
            anchor_index,
            symmetry_index,
            order,
            second_factor,
            third_factor,
            second_pivot,
            left,
            right,
            sign,
            scalar,
            labels,
        ) = record
        if row in seen or len(set(row)) != 3:
            raise AssertionError(f"bad row at record {number}")
        if (
            not 0 <= anchor_index < 3
            or not 0 <= symmetry_index < len(stabilizers[KIND])
            or order not in (0, 1)
            or not 0 <= second_factor < len(factor_polynomials)
            or not 0 <= third_factor < len(factor_polynomials)
            or second_factor == third_factor
            or not 0 <= second_pivot < 9
            or not 0 <= left < 9
            or not 0 <= right < 9
            or len({FIRST_PIVOT, second_pivot, left, right}) != 4
            or sign not in (-1, 1)
            or scalar == 0
        ):
            raise AssertionError(f"bad metadata at record {number}")
        seen.add(row)
        mapping = alignments[KIND].get(row[anchor_index])
        if mapping is None or transform_factor(
            row[anchor_index], mapping, factor_occurrence, occurrence_factor
        ) != canonical[KIND]:
            raise AssertionError(f"bad anchor at record {number}")
        moved = tuple(
            transform_factor(
                row[index], mapping, factor_occurrence, occurrence_factor
            )
            for index in range(3)
            if index != anchor_index
        )
        targets = tuple(
            transform_factor(
                factor,
                stabilizers[KIND][symmetry_index],
                factor_occurrence,
                occurrence_factor,
            )
            for factor in moved
        )
        if (second_factor, third_factor) != (
            targets[order], targets[1 - order]
        ):
            raise AssertionError(f"bad transport at record {number}")
        q2 = restricted[second_factor]
        slope2, constant2 = fibers.pivot_split(q2, second_pivot)
        if poly.add(
            poly.multiply(slope2, poly.variable(second_pivot)), constant2
        ) != q2:
            raise AssertionError(f"second graph reconstruction at record {number}")
        product = poly.constant(scalar)
        for label in labels:
            product = poly.multiply(product, restricted_parents[label])
        if product != slope2:
            raise AssertionError(f"false unit slope at record {number}")
        if directional(slope2, left, right, sign) or directional(
            constant2, left, right, sign
        ):
            raise AssertionError(f"false directional invariance at record {number}")
        q3 = restricted[third_factor]
        if directional(
            directional(q3, left, right, sign), left, right, sign
        ):
            raise AssertionError(f"false primitive-direction affinity at record {number}")
        final = fibers.graph_restrict(
            q3, second_pivot, slope2, poly.negative(constant2)
        )
        if directional(
            directional(final, left, right, sign), left, right, sign
        ):
            raise AssertionError(f"final direction transfer at record {number}")
        # Explicit GL_Z substitution; x_left is the new t coordinate.
        for polynomial in (slope2, constant2):
            if any(monomial[left] for monomial in shear(polynomial, left, right, sign)):
                raise AssertionError(f"unit graph depends on t at record {number}")
        for polynomial in (q3, final):
            if any(
                monomial[left] > 1
                for monomial in shear(polynomial, left, right, sign)
            ):
                raise AssertionError(f"transformed final is not affine at record {number}")
        semantic.update(repr((row, record)).encode("ascii"))
    digest = semantic.hexdigest()
    if digest != EXPECTED_SEMANTIC:
        raise AssertionError(f"primitive-direction semantic changed: {digest}")
    print("PASS primitive-direction double-graph rows", len(seen))
    print("SEMANTIC", digest)
    print(
        "PASS rows subsumed by tracked coordinate double graph",
        replay_type50_overlap(),
    )


if __name__ == "__main__":
    main()
