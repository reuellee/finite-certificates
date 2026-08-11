#!/usr/bin/env python3
"""Exact no-go for naive bracket complementation in the diagonal-three scan.

The six bracket formulas below are identities in the standard normalized
chart.  Their summands do not have a common column multidegree.  Consequently
``p_I -> epsilon(I,I^c) p_(I^c)`` cannot be applied termwise while ignoring
the independent column rescalings used to return a Gale kernel to that chart.

For each residual kind used by the proposed scan, this replay reconstructs an
isolated exact point on the canonical primitive wall, applies the normalized
Gale involution, and evaluates the proposed naive complement polynomial.  A
correct transported wall equation would vanish at that dual point; all six
naive equations are nonzero.
"""

from __future__ import annotations

from fractions import Fraction
from itertools import combinations
from pathlib import Path
import sys


HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import DIAG9_GRAPH_global_factor_census as global_factors  # noqa: E402
import verify_diag2_canonical_robust_edges as robust  # noqa: E402


KINDS = (36, 38, 48, 49, 50, 51)

# These are exactly the normalized-chart formulas used by the rejected
# complement-affinity proposal.  Labels are zero based.
BRACKET_TERMS = {
    36: (
        (1, (0, 1, 3, 4), (1, 2, 5, 6)),
        (-1, (0, 1, 2, 3), (0, 2, 5, 6)),
    ),
    38: (
        (1, (0, 1, 2, 3), (0, 5, 6, 7)),
        (-1, (0, 1, 3, 4), (1, 5, 6, 7)),
    ),
    48: (
        (1, (0, 1, 2, 3), (0, 2, 4, 5)),
        (-1, (0, 1, 3, 5), (1, 2, 4, 5)),
    ),
    49: (
        (1, (0, 1, 2, 3), (0, 2, 4, 6)),
        (-1, (0, 1, 3, 5), (1, 2, 4, 6)),
    ),
    50: (
        (1, (0, 1, 3, 5), (1, 2, 6, 7)),
        (-1, (0, 1, 2, 3), (0, 2, 6, 7)),
    ),
    51: (
        (1, (0, 1, 2, 5), (3, 5, 6, 7)),
        (-1, (0, 1, 5, 6), (1, 3, 5, 7)),
        (-1, (0, 2, 5, 6), (1, 3, 5, 7)),
    ),
}

EXPECTED_NAIVE_VALUES = {
    36: Fraction(
        2_445_220_799_311_878_372_850_757_363,
        18_497_268_337_304_663_233_593_750,
    ),
    38: Fraction(5_494_536, 625_391),
    48: Fraction(
        -815_479_488_745_033_943_194_802_740_351_071,
        266_952_215_436_751_962_521_600,
    ),
    49: Fraction(
        -135_759_141_170_787_087_315_115_021_718_125,
        3_497_241_587_119_871_786_809_435_503,
    ),
    50: Fraction(
        300_531_811_265_199_952_441_442_530_507,
        20_142_719_979_344_170_772_256_000,
    ),
    51: Fraction(538_250_129_705_829_241_371, 62_002_104_663_783_125),
}


def permutation_sign(sequence) -> int:
    return -1 if sum(
        sequence[left] > sequence[right]
        for left in range(len(sequence))
        for right in range(left + 1, len(sequence))
    ) & 1 else 1


def gale_basis(basis):
    complement = tuple(index for index in range(8) if index not in basis)
    return permutation_sign(tuple(basis) + complement), complement


def polynomial_from_terms(terms, brackets, transform):
    answer = {}
    for coefficient, left, right in terms:
        left_sign, left = transform(left)
        right_sign, right = transform(right)
        answer = global_factors.add(
            answer,
            global_factors.multiply(brackets[left], brackets[right]),
            coefficient * left_sign * right_sign,
        )
    return global_factors.primitive(answer)


def evaluate(polynomial, values):
    answer = Fraction(0)
    for monomial, coefficient in polynomial.items():
        term = Fraction(coefficient)
        for value, exponent in zip(values, monomial, strict=True):
            term *= value ** exponent
        answer += term
    return answer


def inverse(matrix):
    size = len(matrix)
    work = [
        [Fraction(value) for value in row]
        + [Fraction(row_index == column) for column in range(size)]
        for row_index, row in enumerate(matrix)
    ]
    for column in range(size):
        pivot = next(
            (row for row in range(column, size) if work[row][column]), None
        )
        if pivot is None:
            raise AssertionError("Gale parent frame became singular")
        work[column], work[pivot] = work[pivot], work[column]
        pivot_value = work[column][column]
        work[column] = [value / pivot_value for value in work[column]]
        for row in range(size):
            if row == column or not work[row][column]:
                continue
            scale = work[row][column]
            work[row] = [
                value - scale * pivot_value
                for value, pivot_value in zip(
                    work[row], work[column], strict=True
                )
            ]
    return tuple(tuple(row[size:]) for row in work)


def normalized_gale(values):
    """Return standard-chart coordinates of the Gale kernel of [I|A]."""

    columns = robust.standard_columns(
        dict(zip(robust.VARIABLES, values, strict=True))
    )
    parent = tuple(zip(*columns, strict=True))
    block = tuple(tuple(row[column] for column in range(4, 8)) for row in parent)

    # N=[-A^T|I] is an unnormalized Gale kernel.  Its first frame is -A^T.
    first_frame = tuple(
        tuple(-block[column][row] for column in range(4))
        for row in range(4)
    )
    last_block = inverse(first_frame)

    # First left-multiply by (-A^T)^(-1).  Diagonal row scalings then make
    # column 5 all ones; compensating scales restore columns 1--4 to I.
    # Finally scale columns 6--8 to make their first coordinate one.
    fifth = tuple(last_block[row][0] for row in range(4))
    if not all(fifth):
        raise AssertionError("dual chart misses the column-5 normalization")
    normalized_last = []
    for column in range(4):
        vector = tuple(
            last_block[row][column] / fifth[row] for row in range(4)
        )
        if column:
            if not vector[0]:
                raise AssertionError("dual chart misses a leading-one normalization")
            vector = tuple(value / vector[0] for value in vector)
        normalized_last.append(vector)
    if normalized_last[0] != (1, 1, 1, 1):
        raise AssertionError("dual column 5 is not normalized")
    if tuple(vector[0] for vector in normalized_last) != (1, 1, 1, 1):
        raise AssertionError("dual columns 5--8 lost their leading ones")
    return tuple(
        normalized_last[column][row]
        for column in range(1, 4)
        for row in range(1, 4)
    )


def column_multidegree(left, right):
    return tuple(int(label in left) + int(label in right) for label in range(8))


def main():
    factor_ids, factor_polynomials = robust.canonical_data()
    matrix = global_factors.normalized_matrix()
    brackets = {
        basis: global_factors.square_minor(matrix, basis)
        for basis in combinations(range(8), 4)
    }
    parent_brackets = global_factors.bracket_records(matrix)

    for kind in KINDS:
        terms = BRACKET_TERMS[kind]
        degrees = {
            column_multidegree(left, right) for _coefficient, left, right in terms
        }
        if len(degrees) == 1:
            raise AssertionError(f"kind {kind} unexpectedly became column homogeneous")

        wall = robust.construct_witness(kind, factor_ids, factor_polynomials)
        factor = factor_polynomials[wall.factor_id]
        if evaluate(factor, wall.center):
            raise AssertionError(f"kind {kind} canonical point left its factor wall")

        # Pin that the bracket formula is the actual canonical primitive
        # factor before testing its rejected termwise complement transform.
        primal = polynomial_from_terms(
            terms, brackets, lambda basis: (1, tuple(basis))
        )
        primal_quotient, _primal_units = global_factors.strip_parent_units(
            primal, parent_brackets
        )
        if global_factors.polynomial_key(primal_quotient) != (
            global_factors.polynomial_key(factor)
        ):
            raise AssertionError(f"kind {kind} bracket identity changed")

        naive = polynomial_from_terms(terms, brackets, gale_basis)
        naive_quotient, _naive_units = global_factors.strip_parent_units(
            naive, parent_brackets
        )
        dual = normalized_gale(wall.center)
        if normalized_gale(dual) != wall.center:
            raise AssertionError(f"kind {kind} normalized Gale map is not involutive")
        value = evaluate(naive_quotient, dual)
        if value != EXPECTED_NAIVE_VALUES[kind] or not value:
            raise AssertionError(f"kind {kind} naive dual value changed: {value}")
        print(
            "PASS naive-complement no-go kind",
            kind,
            "factor",
            wall.factor_id,
            "q(center)=0 naive(D(center))=",
            value,
        )

    print("PASS all six formulas have unequal column multidegrees")
    print("PASS exact normalized Gale involution at all six isolated wall centers")
    print("NO-GO termwise bracket complementation omits normalization weights")


if __name__ == "__main__":
    main()
