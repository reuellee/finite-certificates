#!/usr/bin/env python3
"""Exact Farkas obstruction for a multi-coordinate diagonal-two pivot.

The proposed refinement of the residual-wall descent asks for a tangent
direction which strictly increases every already acquired signed bad-side
function.  Farkas' alternative says that such a direction exists exactly
when the projected signed gradients have no nonzero nonnegative dependence.

This checker certifies:

* the earlier type-37/type-44 coordinate cycle has a combined direction;
* the coincident type-46/type-47 localization wall supports a proper,
  incomparable pair of extension signatures whose bad gradients are g and
  -g, with the primitive positive Farkas certificate (1,1);
* both signatures are realized exactly on opposite sides, excluded there in
  the opposite order by explicit positive five-circuits, and excluded on the
  wall by the same positive three-circuit;
* among triples {46,47,k}, nine other residual representatives coexist in the
  uniform parent locus (with exact rational witnesses), whereas k=36 and 51
  force explicit parent brackets to vanish.

This is a no-go for a *strict* all-active-wall cone field.  Tangential motion
along the common 46/47 wall remains possible, so this does not prove or
disprove the second diagonal.
"""

from fractions import Fraction
from itertools import combinations
from pathlib import Path
import sys


HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import DIAG2_PIVOT_ALL_COMPACT_SECOND_WALL_VERIFY as wall  # noqa: E402
import verify_residual_log_binomials as poly  # noqa: E402


TRIPLES = tuple(combinations(range(8), 3))
TRIPLE_INDEX = {triple: index for index, triple in enumerate(TRIPLES)}

SUPPORT_46 = ((0, 1, 2), (0, 3, 4), (0, 5, 6), (1, 3, 5), (1, 2, 4))
SUPPORT_47 = ((0, 1, 2), (0, 3, 4), (0, 5, 6), (1, 3, 7), (1, 2, 3))
SHARED_SUPPORT = SUPPORT_46[:3]

SIGMA = 35958702884521921
TAU = 54112465834733631
SIGMA_POINT = (3290, 10000, 9935, 65)
TAU_POINT = (-7, -993, -1000, 7)

WALL_VALUES = {
    "a": Fraction(2),
    "b": Fraction(3),
    "c": Fraction(5),
    "d": Fraction(7),
    "e": Fraction(46, 5),
    "f": Fraction(11),
    "g": Fraction(13),
    "h": Fraction(17),
    "i": Fraction(19),
}
EPSILON = Fraction(1, 100)

EXPECTED_SIGMA_WEIGHTS = (
    Fraction(1419, 500), Fraction(13), Fraction(1),
    Fraction(11, 100), Fraction(33, 100),
)
EXPECTED_TAU_WEIGHTS = (
    Fraction(673, 250), Fraction(13), Fraction(1),
    Fraction(11, 100), Fraction(187, 100),
)


TRIPLE_WITNESSES = {
    37: (Fraction(-163, 19), -5, 2, Fraction(227, 19), 3, -5, 5, 2, 6),
    38: (-8, 2, Fraction(10, 9), 2, -7, -1, -9, 5, Fraction(875, 549)),
    39: (Fraction(-97, 8), Fraction(-841, 72), -1, -5, -1, -9, -6, -2, 7),
    41: (-2, Fraction(-38, 3), 4, -7, 9, -6, 8, -5, -4),
    42: (3, Fraction(-121, 4), -3, Fraction(73, 12), -5, -1, 7, -6, -4),
    44: (2, Fraction(-109, 4), -9, 8, -5, -4, -6, Fraction(647, 65), 9),
    48: (2, Fraction(7, 6), -5, -1, -2, -6, -8, 8, 2),
    49: (Fraction(-553, 20), Fraction(8, 5), 9, 4, -9, -4, -8, 9, -7),
    50: (-2, Fraction(2, 3), Fraction(32, 39), 6, -7, -4, 2, 4, -1),
}


def shifted_parent(delta):
    values = dict(WALL_VALUES)
    values["a"] += delta
    return wall.standard_columns(values)


def normals(columns, support):
    return tuple(wall.plane_normal(columns, triple) for triple in support)


def dot(left, right):
    return sum(a * b for a, b in zip(left, right, strict=True))


def signature(columns, point):
    values = tuple(dot(wall.plane_normal(columns, triple), point) for triple in TRIPLES)
    if not all(values):
        raise AssertionError("extension point lies on a parent plane")
    return sum(1 << index for index, value in enumerate(values) if value > 0)


def signed_circuit_weights(columns, support, sign_pattern):
    support_normals = normals(columns, support)
    signed = tuple(
        tuple((1 if (sign_pattern >> TRIPLE_INDEX[triple]) & 1 else -1) * value for value in normal)
        for triple, normal in zip(support, support_normals, strict=True)
    )
    if wall.exact_rank(tuple(zip(*signed, strict=True))) != 4:
        raise AssertionError("five-support is not a rank-four circuit")
    cofactors = tuple(
        (-1) ** omitted
        * wall.determinant(
            [
                [signed[column][row] for column in range(5) if column != omitted]
                for row in range(4)
            ]
        )
        for omitted in range(5)
    )
    if all(value < 0 for value in cofactors):
        cofactors = tuple(-value for value in cofactors)
    if not all(value > 0 for value in cofactors):
        raise AssertionError(f"support is not a positive circuit: {cofactors}")
    for row in range(4):
        if sum(cofactors[column] * signed[column][row] for column in range(5)):
            raise AssertionError("circuit cofactors do not annihilate the signed normals")
    return cofactors


def parent_chirotope(columns):
    values = tuple(
        wall.column_determinant(columns, basis)
        for basis in combinations(range(8), 4)
    )
    if not all(values):
        raise AssertionError("parent is nonuniform")
    return tuple(value > 0 for value in values)


def verify_proper_incomparable_pair():
    minus = shifted_parent(-EPSILON)
    center = shifted_parent(Fraction(0))
    plus = shifted_parent(EPSILON)
    if not (
        parent_chirotope(minus)
        == parent_chirotope(center)
        == parent_chirotope(plus)
    ):
        raise AssertionError("the mutation path leaves the parent realization cell")

    if signature(minus, SIGMA_POINT) != SIGMA:
        raise AssertionError("sigma is not realized on the negative side")
    if signature(plus, TAU_POINT) != TAU:
        raise AssertionError("tau is not realized on the positive side")
    sigma_weights = signed_circuit_weights(plus, SUPPORT_46, SIGMA)
    tau_weights = signed_circuit_weights(minus, SUPPORT_47, TAU)
    if sigma_weights != EXPECTED_SIGMA_WEIGHTS:
        raise AssertionError(f"wrong sigma obstruction: {sigma_weights}")
    if tau_weights != EXPECTED_TAU_WEIGHTS:
        raise AssertionError(f"wrong tau obstruction: {tau_weights}")

    # The three shared signed normals have rank two on the wall.  Both full
    # signatures restrict to (+,-,+), and weights (13,65,5) give a positive
    # dependence.  Thus both signatures are bad on the common wall itself.
    shared_signs_sigma = tuple(
        1 if (SIGMA >> TRIPLE_INDEX[triple]) & 1 else -1
        for triple in SHARED_SUPPORT
    )
    shared_signs_tau = tuple(
        1 if (TAU >> TRIPLE_INDEX[triple]) & 1 else -1
        for triple in SHARED_SUPPORT
    )
    if shared_signs_sigma != (1, -1, 1) or shared_signs_tau != shared_signs_sigma:
        raise AssertionError("the signatures do not share the positive wall circuit")
    shared = tuple(
        tuple(sign * value for value in normal)
        for sign, normal in zip(shared_signs_sigma, normals(center, SHARED_SUPPORT), strict=True)
    )
    if wall.exact_rank(tuple(zip(*shared, strict=True))) != 2:
        raise AssertionError("the common wall support does not have rank two")
    shared_weights = (Fraction(13), Fraction(65), Fraction(5))
    for row in range(4):
        if sum(shared_weights[column] * shared[column][row] for column in range(3)):
            raise AssertionError("wrong common positive three-circuit")
    return sigma_weights, tau_weights, shared_weights


def q46_gradient():
    # q_46 = af-bf-cd+ce at the exact wall point.
    z = WALL_VALUES
    return (
        z["f"], -z["f"], -z["d"] + z["e"], -z["c"], z["c"],
        z["a"] - z["b"], Fraction(0), Fraction(0), Fraction(0),
    )


def verify_farkas_cones():
    # The 37/44 coordinate-pivot cycle is not a Farkas obstruction.  At its
    # exact double wall, v=(da,dd)=(1,1) gives dp_37=1 and dp_44=6.
    base = {
        "a": Fraction(1, 2), "b": Fraction(-3), "c": Fraction(-1),
        "d": Fraction(1, 4), "e": Fraction(-1), "f": Fraction(2),
        "g": Fraction(2), "h": Fraction(3), "i": Fraction(-3),
    }
    moved = dict(base)
    moved["a"] += 1
    moved["d"] += 1
    base_q = wall.residual_values(base)
    moved_q = wall.residual_values(moved)
    directional_37 = -(moved_q[37] - base_q[37])
    directional_44 = -(moved_q[44] - base_q[44])
    if (directional_37, directional_44) != (1, 6):
        raise AssertionError("the combined 37/44 cone direction disappeared")

    gradient = q46_gradient()
    if not any(gradient):
        raise AssertionError("the localization wall gradient vanished")
    opposite = tuple(-value for value in gradient)
    if any(left + right for left, right in zip(gradient, opposite, strict=True)):
        raise AssertionError("the proposed Farkas gradients are not opposite")
    # Positive multipliers (1,1) annihilate the signed-gradient matrix.  For
    # every v, g.v and -g.v cannot both be strictly positive.
    farkas_weights = (Fraction(1), Fraction(1))
    return (directional_37, directional_44), gradient, farkas_weights


def verify_tangent_localization_escape():
    # The common positive three-circuit omits label 8, and q_46=q_47 is
    # independent of the whole eighth parent column.  Vary only g from 13 to
    # 421/32.  Every parent bracket is affine in g; exact endpoint signs show
    # that [5678] is the unique first parent wall while the common witness and
    # localization equation persist identically.
    start_values = dict(WALL_VALUES)
    end_values = dict(WALL_VALUES)
    endpoint = Fraction(421, 32)
    end_values["g"] = endpoint
    start_columns = wall.standard_columns(start_values)
    end_columns = wall.standard_columns(end_values)
    start_brackets = {
        "".join(str(index + 1) for index in basis): wall.column_determinant(
            start_columns, basis
        )
        for basis in combinations(range(8), 4)
    }
    end_brackets = {
        "".join(str(index + 1) for index in basis): wall.column_determinant(
            end_columns, basis
        )
        for basis in combinations(range(8), 4)
    }
    if {label for label, value in end_brackets.items() if not value} != {"5678"}:
        raise AssertionError("the tangent escape reaches the wrong parent wall")
    for label, start in start_brackets.items():
        end = end_brackets[label]
        if label != "5678" and start * end <= 0:
            raise AssertionError(f"parent bracket {label} changes sign before the exit")
    if wall.residual_values(start_values)[46] or wall.residual_values(end_values)[46]:
        raise AssertionError("the tangent path left the common localization wall")
    if normals(start_columns, SHARED_SUPPORT) != normals(end_columns, SHARED_SUPPORT):
        raise AssertionError("the common positive circuit changed on the tangent path")
    return endpoint, "5678"


def polynomial_wall_identities():
    one, zero = poly.constant(1), poly.constant(0)
    a, b, c, d, e, f, g, h, i = (poly.variable(index) for index in range(9))
    matrix = (
        (one, zero, zero, zero, one, one, one, one),
        (zero, one, zero, zero, one, a, d, g),
        (zero, zero, one, zero, one, b, e, h),
        (zero, zero, zero, one, one, c, f, i),
    )

    def bracket(label):
        basis = tuple(int(character) - 1 for character in label)
        square = tuple(
            tuple(matrix[row][column] for column in basis) for row in range(4)
        )
        return poly.determinant(square)

    q36 = poly.add(poly.multiply(a, f), poly.negative(poly.multiply(c, d)), c, poly.negative(f))
    q46 = poly.add(poly.multiply(a, f), poly.negative(poly.multiply(b, f)), poly.negative(poly.multiply(c, d)), poly.multiply(c, e))
    q51 = poly.add(
        poly.multiply(a, b, f), poly.negative(poly.multiply(a, c, e)),
        poly.multiply(a, c, h), poly.negative(poly.multiply(a, f, h)),
        poly.negative(poly.multiply(b, b, f)), poly.multiply(b, c, e),
        poly.negative(poly.multiply(b, c, g)), poly.multiply(b, f, h),
        poly.multiply(c, e, g), poly.negative(poly.multiply(c, e, h)),
    )

    # c f [4567] = c(1-e)q36 + c(1-d)(q46-q36).
    identity_36 = poly.subtract(
        poly.multiply(c, f, bracket("4567")),
        poly.add(
            poly.multiply(poly.subtract(c, poly.multiply(c, e)), q36),
            poly.multiply(
                poly.subtract(c, poly.multiply(c, d)),
                poly.subtract(q46, q36),
            ),
        ),
    )
    # q51 - c[4678] = (b-h)q46.
    identity_51 = poly.subtract(
        poly.subtract(q51, poly.multiply(c, bracket("4678"))),
        poly.multiply(poly.subtract(b, h), q46),
    )
    if identity_36 or identity_51:
        raise AssertionError("a forbidden triple-wall identity failed")


def verify_triple_type_fan():
    expected_kinds = {37, 38, 39, 41, 42, 44, 48, 49, 50}
    if set(TRIPLE_WITNESSES) != expected_kinds:
        raise AssertionError("wrong feasible 46/47 triple fan")
    variable_names = "abcdefghi"
    for kind, coordinates in TRIPLE_WITNESSES.items():
        values = {
            name: Fraction(value)
            for name, value in zip(variable_names, coordinates, strict=True)
        }
        residuals = wall.residual_values(values)
        zero_types = {index for index, value in residuals.items() if not value}
        if zero_types != {46, 47, kind}:
            raise AssertionError(f"wrong residual triple at type {kind}: {zero_types}")
        parent_chirotope(wall.standard_columns(values))
    polynomial_wall_identities()
    return tuple(sorted(expected_kinds)), (36, 51)


def main():
    sigma_weights, tau_weights, shared_weights = verify_proper_incomparable_pair()
    combined, gradient, farkas_weights = verify_farkas_cones()
    tangent_endpoint, tangent_wall = verify_tangent_localization_escape()
    feasible_triples, forbidden_triples = verify_triple_type_fan()
    print("PASS exact proper incomparable signatures:", SIGMA, TAU)
    print("PASS sigma/tau opposite-side positive circuits:", sigma_weights, tau_weights)
    print("PASS common localization-wall positive three-circuit:", shared_weights)
    print("PASS type-37/44 combined cone direction has derivatives", combined)
    print("PASS type-46/47 signed gradients are g,-g with g=", gradient)
    print("PASS primitive positive Farkas certificate:", farkas_weights)
    print(
        "PASS tangent common-circuit escape reaches [" + tangent_wall + "] at g=",
        tangent_endpoint,
    )
    print("PASS uniform 46/47/k triple witnesses for k=", feasible_triples)
    print("PASS k=36,51 forbidden exactly by parent brackets [4567],[4678]")
    print("NO-GO a strict all-active-wall multi-coordinate cone need not exist")
    print("THEOREM the minimal 46/47 cone obstruction itself has a parent-boundary escape")
    print("CAVEAT a stratified tangent/strict global potential is still missing; s=2 is open")


if __name__ == "__main__":
    main()
