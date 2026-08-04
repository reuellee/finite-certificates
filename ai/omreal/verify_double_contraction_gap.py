#!/usr/bin/env python3
"""Exact verifier for a gap inside one literal double-contraction fiber.

This sharpens ``verify_seeat_residence_nonconvex.py`` without claiming that
the complete double-contraction fiber is disconnected.  Let ``L,R`` be the
two stored positions of parent element 1 and put ``p=L-R``.  The affine family

    e(u) = 2 R + u p,          0 <= u <= 2,

lies in one contraction-height fiber for the uniform extension ``p``.  After
also contracting fixed parent element 2, its rank-two quotient is literally
constant.  The stored second signature is feasible at ``u=0,2``.

At the middle chart, rows 0,4,13,44,51 of its signed derived-normal matrix
form a positive circuit.  Every row is affine in ``u``.  This verifier
interpolates the five alternating cofactor polynomials exactly and proves
their positivity on ``[1/2,3/2]`` by positive Bernstein coefficients.  Hence
Gordan's alternative makes the second signature infeasible throughout that
closed interval.  Its intersection with this affine line segment therefore
has at least two components.

The theorem is a no-go result for a cellwise-convex or cellwise-acyclic proof
based only on affine slices.  A path in the full double-contraction fiber may
still go around the certified gap, so this is not a 9DVL counterexample.
"""

from fractions import Fraction
from math import comb

import numpy as np

import verify_seeat_residence_nonconvex as residence


BAD_SUPPORT = (0, 4, 13, 44, 51)
BAD_INTERVAL = (Fraction(1, 2), Fraction(3, 2))
INTERPOLATION_DEGREE = 4


def solve_square(matrix, vector):
    """Solve one nonsingular square rational system by Gauss--Jordan."""
    augmented = [
        [Fraction(value) for value in row] + [Fraction(rhs)]
        for row, rhs in zip(matrix, vector, strict=True)
    ]
    size = len(augmented)
    for column in range(size):
        pivot = next(
            (row for row in range(column, size) if augmented[row][column]),
            None,
        )
        if pivot is None:
            raise AssertionError("singular interpolation system")
        augmented[column], augmented[pivot] = augmented[pivot], augmented[column]
        scale = augmented[column][column]
        augmented[column] = [value / scale for value in augmented[column]]
        for row in range(size):
            if row == column or not augmented[row][column]:
                continue
            scale = augmented[row][column]
            augmented[row] = [
                value - scale * pivot_value
                for value, pivot_value in zip(
                    augmented[row], augmented[column], strict=True
                )
            ]
    return [augmented[row][-1] for row in range(size)]


def interpolate(values):
    """Interpolate a degree-at-most-four polynomial at u=0,...,4."""
    size = INTERPOLATION_DEGREE + 1
    vandermonde = [
        [Fraction(point) ** degree for degree in range(size)]
        for point in range(size)
    ]
    return solve_square(vandermonde, values)


def evaluate(polynomial, point):
    point = Fraction(point)
    total = Fraction(0)
    for coefficient in reversed(polynomial):
        total = total * point + coefficient
    return total


def bernstein_coefficients(polynomial, left, right):
    """Return degree-four Bernstein coefficients on ``[left,right]``."""
    degree = INTERPOLATION_DEGREE
    width = right - left
    power = [Fraction(0)] * (degree + 1)
    for exponent, coefficient in enumerate(polynomial):
        for variable_exponent in range(exponent + 1):
            power[variable_exponent] += (
                coefficient
                * comb(exponent, variable_exponent)
                * left ** (exponent - variable_exponent)
                * width**variable_exponent
            )
    return [
        sum(
            power[exponent]
            * Fraction(comb(index, exponent), comb(degree, exponent))
            for exponent in range(index + 1)
        )
        for index in range(degree + 1)
    ]


def parent_at(fixed, deleted, right, contraction_column, parameter):
    position = 2 * right + int(parameter) * contraction_column
    return residence.insert(fixed, deleted, position)


def positive_circuit_weights(parent, signature):
    """Return the five signed alternating cofactors on ``BAD_SUPPORT``."""
    _, rows = residence.signed_rows(parent, signature)
    weights = []
    for omitted in range(len(BAD_SUPPORT)):
        minor = [
            rows[BAD_SUPPORT[index]]
            for index in range(len(BAD_SUPPORT))
            if index != omitted
        ]
        # The common orientation is the negative of the usual alternating
        # cofactor vector at the stored midpoint.
        weights.append(-((-1) ** omitted) * residence.determinant(minor))
    return weights, rows


def main():
    certificate = np.load(residence.CERTIFICATE, allow_pickle=False)
    fixed = certificate["fixed"]
    deleted = int(certificate["deleted"].item())
    left = certificate["left"]
    right = certificate["right"]
    midpoint = certificate["midpoint"]
    sigma2 = int(certificate["signature"].item())
    if deleted != 0:
        raise AssertionError("this certificate expects deleted parent element 1")

    contraction_column = left - right
    if not np.array_equal(midpoint, 2 * right + contraction_column):
        raise AssertionError("stored midpoint is not e(1)")

    endpoint_parents = (
        parent_at(fixed, deleted, right, contraction_column, 0),
        parent_at(fixed, deleted, right, contraction_column, 2),
    )
    endpoint_witnesses = (
        certificate["right_point"],
        certificate["left_point"],
    )
    expected_parent = residence.parent_signs_and_rows(
        residence.insert(fixed, deleted, left)
    )[0]

    # Every parent bracket is affine in u.  Equal nonzero endpoint signs prove
    # that the whole segment stays in the same uniform parent realization
    # chamber.  The same argument applies to the first extension column p.
    sigma1 = None
    for parent, witness in zip(endpoint_parents, endpoint_witnesses, strict=True):
        parent_signs, sigma2_rows = residence.signed_rows(parent, sigma2)
        if parent_signs != expected_parent:
            raise AssertionError("endpoint left the row-2599 chamber")
        if not residence.strict_witness(sigma2_rows, witness):
            raise AssertionError("invalid endpoint witness for sigma2")
        current_sigma1 = residence.extension_signature(parent, contraction_column)
        if sigma1 is None:
            sigma1 = current_sigma1
        elif current_sigma1 != sigma1:
            raise AssertionError("sigma1 changes between the endpoints")

    # Check the affine endpoint-sign argument basis by basis, independently of
    # the chirotope string comparison above.
    endpoint_parent_values = []
    for parent in endpoint_parents:
        endpoint_parent_values.append(
            [
                residence.determinant(parent[:, np.asarray(basis) - 1].tolist())
                for basis in residence.BASES
            ]
        )
    if any(
        left_value == 0
        or right_value == 0
        or (left_value > 0) != (right_value > 0)
        for left_value, right_value in zip(
            endpoint_parent_values[0], endpoint_parent_values[1], strict=True
        )
    ):
        raise AssertionError("a parent bracket can vanish on the segment")

    # Contract p and fixed parent element 2.  All remaining quotient columns
    # are fixed; the only moving column differs from e(0)=2R by u*p.  The
    # following exact mixed brackets also verify that this rank-two quotient
    # is uniform.
    contracted_parent = endpoint_parents[0][:, 1]
    remaining = (0, 2, 3, 4, 5, 6, 7)
    contraction_values = []
    for parameter in (0, 1, 2):
        parent = parent_at(fixed, deleted, right, contraction_column, parameter)
        values = []
        for first_index, first in enumerate(remaining):
            for second in remaining[first_index + 1 :]:
                values.append(
                    residence.determinant(
                        np.column_stack(
                            (
                                contraction_column,
                                contracted_parent,
                                parent[:, first],
                                parent[:, second],
                            )
                        ).tolist()
                    )
                )
        contraction_values.append(values)
    if not all(value != 0 for value in contraction_values[0]):
        raise AssertionError("double contraction is not uniform")
    if not (
        contraction_values[0]
        == contraction_values[1]
        == contraction_values[2]
    ):
        raise AssertionError("rank-two quotient changes along the line")

    # Each signed derived normal is affine in u.  This makes every four-row
    # cofactor a polynomial of degree at most four.
    row_samples = []
    weight_samples = []
    for parameter in range(7):
        parent = parent_at(fixed, deleted, right, contraction_column, parameter)
        weights, rows = positive_circuit_weights(parent, sigma2)
        row_samples.append(rows)
        weight_samples.append(weights)
    for row_index in range(len(residence.TRIPLES)):
        for coordinate in range(4):
            if (
                row_samples[2][row_index][coordinate]
                - 2 * row_samples[1][row_index][coordinate]
                + row_samples[0][row_index][coordinate]
                != 0
            ):
                raise AssertionError("a derived-normal coefficient is not affine")

    weight_polynomials = []
    for circuit_index in range(len(BAD_SUPPORT)):
        polynomial = interpolate(
            [weight_samples[point][circuit_index] for point in range(5)]
        )
        if any(
            evaluate(polynomial, point) != weight_samples[point][circuit_index]
            for point in range(7)
        ):
            raise AssertionError("cofactor interpolation failed")
        bernstein = bernstein_coefficients(polynomial, *BAD_INTERVAL)
        if not all(coefficient > 0 for coefficient in bernstein):
            raise AssertionError("positive circuit does not persist on the interval")
        weight_polynomials.append(polynomial)

    # At u=1 these cofactors reproduce the stored Gordan vector with one
    # common positive factor.  This ties the continuum calculation directly
    # to the original certificate rather than merely finding another circuit.
    stored_weights = [
        int(certificate["midpoint_gordan"][row]) for row in BAD_SUPPORT
    ]
    midpoint_weights = [evaluate(polynomial, 1) for polynomial in weight_polynomials]
    ratios = {
        Fraction(weight, stored)
        for weight, stored in zip(midpoint_weights, stored_weights, strict=True)
    }
    if len(ratios) != 1 or next(iter(ratios)) <= 0:
        raise AssertionError("middle cofactor circuit differs from the stored witness")

    # The alternating-cofactor identity is polynomial of degree at most five.
    # Verify all its coefficients vanish by interpolation at six exact points.
    for coordinate in range(4):
        dependence_values = []
        for parameter in range(6):
            dependence_values.append(
                sum(
                    weight_samples[parameter][index]
                    * row_samples[parameter][BAD_SUPPORT[index]][coordinate]
                    for index in range(len(BAD_SUPPORT))
                )
            )
        degree_five_vandermonde = [
            [Fraction(point) ** degree for degree in range(6)]
            for point in range(6)
        ]
        polynomial = solve_square(degree_five_vandermonde, dependence_values)
        if any(polynomial):
            raise AssertionError("cofactor vector does not annihilate the rows")

    print("PASS the full affine segment stays in one uniform row-2599 chamber")
    print("PASS p=L-R realizes one uniform sigma1 along the full segment")
    print("PASS contracting p and parent 2 gives one fixed uniform rank-two base")
    print("PASS sigma2 is feasible at u=0 and u=2")
    print("PASS one positive five-row circuit persists for 1/2 <= u <= 3/2")
    print("THEOREM: sigma2 feasibility has a disconnected line slice in that double fiber")
    print("NOTE: the full double-contraction fiber may still connect around the gap")


if __name__ == "__main__":
    main()
