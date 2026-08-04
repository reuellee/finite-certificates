#!/usr/bin/env python3
"""Exact Farkas audit of the four canonical rank-two triple witnesses.

This checker is deliberately local to the twelve canonical residual
polynomials.  It does not enumerate relative labeled S_8 occurrences and it
does not prove the second diagonal.

For each exact rank-two witness from
DIAG2_PIVOT_REPRESENTATIVE_TRIPLES_VERIFY.py it computes the primitive row
dependence among the three residual gradients.  It then compares the two
Farkas-positive orientations with the orientation in which all three
nonzero residual coordinates are positive.  Only (39,48,50) is a common
three-wall point.  Its positive dependence persists on an exact tangent
segment to the parent boundary, together with three displayed positive
wall circuits.
"""

from fractions import Fraction
from functools import reduce
from itertools import combinations, product
from math import gcd, lcm
from pathlib import Path
import sys


HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import DIAG2_PIVOT_ALL_COMPACT_SECOND_WALL_VERIFY as wall  # noqa: E402
import DIAG2_PIVOT_REPRESENTATIVE_GRADIENT_VERIFY as pair  # noqa: E402
import DIAG2_PIVOT_REPRESENTATIVE_TRIPLES_VERIFY as triples  # noqa: E402


EXPECTED = {
    (37, 41, 46): {
        "values": (Fraction(-51, 5), Fraction(-136, 9), Fraction(16, 45)),
        "relation": (8, -2, 17),
        "positive_orientations": ((1, -1, 1), (-1, 1, -1)),
    },
    (37, 46, 49): {
        "values": (Fraction(15, 8), Fraction(-25, 8), Fraction(-35, 2)),
        "relation": (6, -6, 1),
        "positive_orientations": ((1, -1, 1), (-1, 1, -1)),
    },
    (39, 48, 50): {
        "values": (Fraction(0), Fraction(0), Fraction(0)),
        "relation": (1, 3, 2),
        "positive_orientations": ((1, 1, 1), (-1, -1, -1)),
    },
    (41, 46, 49): {
        "values": (Fraction(-5, 8), Fraction(405, 256), Fraction(-21, 256)),
        "relation": (3, 1, -15),
        "positive_orientations": ((1, 1, -1), (-1, -1, 1)),
    },
}


def primitive_integer(values):
    denominator = reduce(lcm, (value.denominator for value in values), 1)
    integers = [int(value * denominator) for value in values]
    divisor = reduce(gcd, (abs(value) for value in integers if value))
    integers = [value // divisor for value in integers]
    if next(value for value in integers if value) < 0:
        integers = [-value for value in integers]
    return tuple(integers)


def gradient_relation(jacobian):
    """Return the primitive dependence of three rank-two rows."""

    for left, right in combinations(range(9), 2):
        cofactors = (
            jacobian[1][left] * jacobian[2][right]
            - jacobian[1][right] * jacobian[2][left],
            jacobian[2][left] * jacobian[0][right]
            - jacobian[2][right] * jacobian[0][left],
            jacobian[0][left] * jacobian[1][right]
            - jacobian[0][right] * jacobian[1][left],
        )
        if any(cofactors):
            relation = primitive_integer(cofactors)
            if any(
                sum(relation[row] * jacobian[row][column] for row in range(3))
                for column in range(9)
            ):
                raise AssertionError("computed row cofactors do not annihilate the Jacobian")
            return relation
    raise AssertionError("the residual gradients have rank below two")


def positive_orientations(relation):
    """Orientations s for which {s_i grad(q_i)} has a positive dependence."""

    result = []
    for orientation in product((-1, 1), repeat=3):
        signed_relation = tuple(
            coefficient * sign
            for coefficient, sign in zip(relation, orientation, strict=True)
        )
        if all(value > 0 for value in signed_relation) or all(
            value < 0 for value in signed_relation
        ):
            result.append(orientation)
    return tuple(sorted(result, reverse=True))


def verify_gradient_audit():
    residual, brackets = pair.polynomial_data()
    results = {}
    for kinds, point in triples.RANK_DROP_WITNESSES.items():
        if any(triples.evaluate(bracket, point) == 0 for bracket in brackets.values()):
            raise AssertionError(f"rank-drop witness {kinds} left the uniform locus")
        values = tuple(triples.evaluate(residual[kind], point) for kind in kinds)
        jacobian = tuple(
            tuple(
                triples.evaluate(pair.derivative(residual[kind], variable), point)
                for variable in range(9)
            )
            for kind in kinds
        )
        relation = gradient_relation(jacobian)
        orientations = positive_orientations(relation)
        expected = EXPECTED[kinds]
        if values != expected["values"]:
            raise AssertionError(f"wrong residual values for {kinds}: {values}")
        if relation != expected["relation"]:
            raise AssertionError(f"wrong gradient relation for {kinds}: {relation}")
        if orientations != expected["positive_orientations"]:
            raise AssertionError(f"wrong Farkas orientations for {kinds}: {orientations}")

        # Away from the walls, the only orientation whose signed residuals
        # p_i=s_i q_i are all strictly positive is sign(q).  For the three
        # nonzero witnesses this orientation is not Farkas-positive.
        if all(values):
            active = tuple(1 if value > 0 else -1 for value in values)
            if active in orientations:
                raise AssertionError(f"{kinds} unexpectedly obstructs its strict active cone")
        elif kinds != (39, 48, 50) or any(values):
            raise AssertionError("unexpected partial residual-wall witness")
        results[kinds] = values, relation, orientations
    return results


BASE = {
    "a": Fraction(-1), "b": Fraction(2), "c": Fraction(3),
    "d": Fraction(4), "e": Fraction(-5), "f": Fraction(2),
    "g": Fraction(7), "h": Fraction(-4), "i": Fraction(5),
}


# Each entry is (plane support, signed dependence coefficients).  A coefficient
# c means that sign(c) times that plane normal occurs with positive weight
# |c|.  Type 39 has already dropped its zero-coefficient plane 124.
WALL_CIRCUITS = {
    39: (((1, 2, 3), (3, 5, 6), (3, 7, 8)), (12, 3, -2)),
    48: (((1, 2, 3), (1, 4, 5), (2, 4, 6), (3, 5, 6)), (2, -2, -2, 1)),
    50: (((1, 2, 3), (1, 4, 5), (2, 4, 6), (3, 7, 8)), (3, 3, 3, -1)),
}


def columns_at(h_value):
    values = dict(BASE)
    values["h"] = h_value
    return wall.standard_columns(values), values


def bracket_values(columns):
    return {
        "".join(str(index + 1) for index in basis): wall.column_determinant(
            columns, basis
        )
        for basis in combinations(range(8), 4)
    }


def verify_wall_circuits(columns):
    for kind, (support, coefficients) in WALL_CIRCUITS.items():
        normals = tuple(
            wall.plane_normal(columns, tuple(label - 1 for label in plane))
            for plane in support
        )
        if wall.exact_rank(normals) != len(support) - 1:
            raise AssertionError(f"type-{kind} wall circuit is not support-minimal")
        if any(
            sum(
                coefficient * normal[coordinate]
                for coefficient, normal in zip(coefficients, normals, strict=True)
            )
            for coordinate in range(4)
        ):
            raise AssertionError(f"wrong signed wall circuit for type {kind}")
        if not all(abs(coefficient) > 0 for coefficient in coefficients):
            raise AssertionError("a displayed minimal circuit has zero weight")


def verify_tangent_escape():
    start_h = Fraction(-4)
    end_h = Fraction(-5)
    start_columns, start_values = columns_at(start_h)
    end_columns, end_values = columns_at(end_h)

    for values in (start_values, end_values):
        residuals = wall.residual_values(values)
        if any(residuals[kind] for kind in (39, 48, 50)):
            raise AssertionError("the h-segment left the common residual triple wall")

    start_brackets = bracket_values(start_columns)
    end_brackets = bracket_values(end_columns)
    if not all(start_brackets.values()):
        raise AssertionError("the triple-wall start is not a uniform parent")
    if {label for label, value in end_brackets.items() if not value} != {"2478"}:
        raise AssertionError("the h-segment reaches the wrong parent boundary")
    for label, start in start_brackets.items():
        end = end_brackets[label]
        if label != "2478" and start * end <= 0:
            raise AssertionError(f"parent bracket {label} changes sign before the exit")

    # Plane normals are affine in h.  The same dependence holds at both
    # endpoints, hence throughout the segment; all its coefficients are fixed
    # and nonzero, so the corresponding signed positive circuits persist.
    verify_wall_circuits(start_columns)
    verify_wall_circuits(end_columns)
    return start_h, end_h, "2478"


def main():
    results = verify_gradient_audit()
    start_h, end_h, boundary = verify_tangent_escape()
    for kinds, (values, relation, orientations) in results.items():
        print(
            "PASS", kinds, "q=", values, "relation=", relation,
            "positive orientations=", orientations,
        )
    print("THEOREM only (39,48,50) is a common three-wall witness among the four")
    print("PASS exact positive wall circuits for canonical supports 39,48,50")
    print(f"PASS tangent escape h={start_h} to {end_h} reaches [{boundary}]=0")
    print("CAVEAT canonical local audit only; no proper-pair or diagonal-two theorem")


if __name__ == "__main__":
    main()
