#!/usr/bin/env python3
"""Exact witness-exchange repair of a realized generic 4+5 birth.

One of the ten abstract survivors in
``verify_diag2_generic_birth_pattern_reduction.py`` is genuinely realizable:
the displayed type-50 wall and partner supports are strict positive circuits
for two valid extensions, but their selected witnesses conflict on all 56
ordered elementary shears.  This verifier proves exact parent uniformity,
genericity of the residual wall, both circuit signs, and the selected-witness
failure.  It then enumerates the complete derived-arrangement tope table and
uses the circuit-free escape characterization to prove that the full escape
masks intersect in 51 oriented directions.

The point refutes the stronger arbitrary-selected-witness theorem.  It is not
a counterexample to the full common-shear strategy or to diagonal two.
"""

from fractions import Fraction
import hashlib
from itertools import combinations

import DIAG2_PIVOT_LABELED_PAIR_ORBITS_VERIFY as labeled
import DIAG9_GRAPH_exact_topes as exact_topes
import four_chart_gate as gate
import verify_diag2_canonical_robust_edges as wall_tools
import verify_diag2_escape_set_topes as escape
import verify_diag2_moving_witness_shear as moving


FORMAT = b"diag2-generic-birth-exchange-repair-v3\0"
WALL_TYPE = 50
WALL_FACTOR = 5563
PARTNER_TEXT = "356/247/167/148/258"
RHO = 4380492134087405
ETA = 13817772255984237

POINT = tuple(
    Fraction(value)
    for value in (
        "2574354/734987",
        "-206747/385594",
        "888999/373972",
        "-9029165101298939406043/1506368035830677386928",
        "-101013711008/11454876655",
        "-881637/996208",
        "-686811/867154",
        "-486314/994133",
        "-36178/872041",
    )
)

EXPECTED_PARENT = (
    "++-+-+++-+++-++-+--+---+-+---+---++-+--+--++-+--------+-++--+--++--+++"
)
EXPECTED_EXTENSIONS = 60008
EXPECTED_TOPES = 26110
EXPECTED_RHO_MASK = 0xFED7FFF9BBA5E769656AF4894856
EXPECTED_ETA_MASK = 0xFFFC4A5756FFFFFFFFFFFFFFEFA9
EXPECTED_INTERSECTION = 0xFED44A5112A5E769656AF4894800
GERM_PIVOT = 3
GERM_EPSILON = Fraction(1, 1 << 16)
GERM_SIDE_SUPPORTS = (
    ("negative", -1, "123/145/246/368/378"),
    ("positive", 1, "123/124/145/246/378"),
)
CHILD_CERTIFICATES = (
    (
        "rho-only",
        (
            (3, 7, 7, 0, 10, -4, -32, -20, 32),
            (-14, -31, 1, 8, 32, 18, -4, 3, -7),
            (-18, 19, -8, 1, -7, 27, 9, -32, 12),
            (-32, -32, 2, 1, -24, -32, 15, -10, 20),
        ),
        RHO,
        ETA,
        "123/124/246/167/568",
        (
            139400812577690,
            -563602170585140,
            -262769935232476100,
            16823613852314000,
            -17351904013478815,
        ),
    ),
    (
        "eta-only",
        (
            (32, 32, -2, -18, 14, 26, -12, 5, 8),
            (-9, -14, -21, 32, 10, 32, 32, 14, 8),
            (-17, 9, 4, 14, 1, 6, -30, -32, 32),
            (5, -30, 32, 13, 16, -9, -25, 22, 5),
        ),
        ETA,
        RHO,
        "123/124/145/246/368",
        (
            -285214587653819520,
            364230132298187520,
            -1049882582058886080,
            -596567983396418760,
            -170775760774004352,
        ),
    ),
)
EXPECTED_DIGEST = (
    "67d6640c8516ed3e7eac0dfcb95da2413a1d96453f1089387eb41dcbcd853a62"
)


def parse_support(text):
    return tuple(
        sorted(
            moving.TRIPLE_INDEX[tuple(map(int, token))]
            for token in text.split("/")
        )
    )


def determinant(matrix):
    return exact_topes.determinant(tuple(tuple(row) for row in matrix))


def raw_circuit(rows, support):
    """Return a nonzero exact kernel vector in support order."""

    selected = tuple(rows[index] for index in support)
    if len(support) == 5:
        coefficients = tuple(
            (-1 if omitted & 1 else 1)
            * determinant(
                tuple(
                    tuple(
                        selected[column][coordinate]
                        for column in range(5)
                        if column != omitted
                    )
                    for coordinate in range(4)
                )
            )
            for omitted in range(5)
        )
    elif len(support) == 4:
        coefficients = None
        for coordinates in combinations(range(4), 3):
            candidate = tuple(
                (-1 if omitted & 1 else 1)
                * determinant(
                    tuple(
                        tuple(
                            selected[column][coordinate]
                            for column in range(4)
                            if column != omitted
                        )
                        for coordinate in coordinates
                    )
                )
                for omitted in range(4)
            )
            if any(candidate):
                coefficients = candidate
                break
        if coefficients is None:
            raise AssertionError("wall support has rank below three")
    else:
        raise ValueError("expected a four- or five-support")

    relation = tuple(
        sum(
            coefficient * selected[position][coordinate]
            for position, coefficient in enumerate(coefficients)
        )
        for coordinate in range(4)
    )
    if any(relation) or any(value == 0 for value in coefficients):
        raise AssertionError((support, coefficients, relation))
    return coefficients


def positive(signature, support, coefficients):
    twisted = tuple(
        coefficient * moving.signature_sign(signature, index)
        for index, coefficient in zip(support, coefficients, strict=True)
    )
    return all(value > 0 for value in twisted) or all(value < 0 for value in twisted)


def residual_factor_zeros(factor_polynomials, values):
    """Evaluate all sparse residual factors over QQ by clearing denominators."""

    numerators = tuple(value.numerator for value in values)
    denominators = tuple(value.denominator for value in values)
    zeros = []
    for factor_id, polynomial in enumerate(factor_polynomials):
        degrees = tuple(
            max(monomial[index] for monomial in polynomial)
            for index in range(9)
        )
        total = 0
        for monomial, coefficient in polynomial.items():
            term = int(coefficient)
            for index, exponent in enumerate(monomial):
                term *= (
                    numerators[index] ** exponent
                    * denominators[index] ** (degrees[index] - exponent)
                )
            total += term
        if total == 0:
            zeros.append(factor_id)
    return tuple(zeros)


def support_drop_germ(
    parent,
    factor_polynomial,
    point,
    pivot,
    epsilon,
    signature,
    wall,
    side_supports,
):
    """Certify a transverse wall and strict five-circuit on both sides."""

    coefficient, _constant = wall_tools.affine_parts(factor_polynomial, pivot)
    coefficient_value = wall_tools.evaluate(coefficient, point)
    if not coefficient_value:
        raise AssertionError("the residual wall is not transverse in its affine pivot")

    records = []
    for label, side, support_text in side_supports:
        perturbed = list(point)
        perturbed[pivot] += side * epsilon
        perturbed = tuple(perturbed)
        factor_value = wall_tools.evaluate(factor_polynomial, perturbed)
        if factor_value != side * epsilon * coefficient_value:
            raise AssertionError(f"{label} perturbation has the wrong wall value")

        matrix = wall_tools.integer_matrix(perturbed)
        parent_signs = exact_topes.parent_signs(matrix)
        if 0 in parent_signs:
            raise AssertionError(f"{label} perturbation has a nonuniform parent")
        current_parent = "".join("+" if value > 0 else "-" for value in parent_signs)
        if current_parent != parent:
            raise AssertionError(f"{label} perturbation changed the parent chirotope")
        rows = exact_topes.derived_rows(matrix, normalize=False)
        support = parse_support(support_text)
        if len(support) != 5 or not set(wall) < set(support):
            raise AssertionError(f"{label} support does not extend the wall circuit")
        coefficients = raw_circuit(rows, support)
        if not positive(signature, support, coefficients):
            raise AssertionError(f"{label} side lost its strict positive circuit")
        records.append((label, side, support, coefficients, factor_value))
    return pivot, epsilon, coefficient_value, tuple(records)


def semantic_digest(
    parent,
    extensions,
    wall,
    partner,
    wall_coefficients,
    partner_coefficients,
    topes,
    rho_mask,
    eta_mask,
    germ_record,
    exclusive_records,
):
    digest = hashlib.sha256()
    digest.update(FORMAT)
    for value in POINT:
        digest.update(str(value.numerator).encode("ascii") + b"/")
        digest.update(str(value.denominator).encode("ascii") + b"\0")
    digest.update(parent.encode("ascii") + b"\0")
    for signature in sorted(map(int, extensions)):
        digest.update(signature.to_bytes(8, "little"))
    for support in (wall, partner):
        digest.update(bytes(support))
    for coefficients in (wall_coefficients, partner_coefficients):
        for coefficient in coefficients:
            digest.update(str(coefficient).encode("ascii") + b"\0")
    for tope in sorted(map(int, topes)):
        digest.update(tope.to_bytes(8, "little"))
    digest.update(RHO.to_bytes(8, "little"))
    digest.update(ETA.to_bytes(8, "little"))
    digest.update(rho_mask.to_bytes(16, "little"))
    digest.update(eta_mask.to_bytes(16, "little"))
    pivot, epsilon, coefficient_value, side_records = germ_record
    digest.update(pivot.to_bytes(1, "little"))
    for value in (epsilon, coefficient_value):
        digest.update(str(value.numerator).encode("ascii") + b"/")
        digest.update(str(value.denominator).encode("ascii") + b"\0")
    for label, side, support, coefficients, factor_value in side_records:
        digest.update(label.encode("ascii") + b"\0")
        digest.update(int(side).to_bytes(1, "little", signed=True))
        digest.update(bytes(support))
        for value in (*coefficients, factor_value):
            digest.update(str(value).encode("ascii") + b"\0")
    for (
        label,
        child,
        present,
        absent,
        absent_support,
        absent_coefficients,
    ) in exclusive_records:
        digest.update(label.encode("ascii") + b"\0")
        for row in child:
            for value in row:
                digest.update(int(value).to_bytes(16, "little", signed=True))
        digest.update(present.to_bytes(8, "little"))
        digest.update(absent.to_bytes(8, "little"))
        digest.update(bytes(absent_support))
        for coefficient in absent_coefficients:
            digest.update(str(coefficient).encode("ascii") + b"\0")
    return digest.hexdigest()


def exclusive_child_records(parent):
    records = []
    for (
        label,
        child,
        present,
        absent,
        absent_support_text,
        expected_absent_coefficients,
    ) in CHILD_CERTIFICATES:
        matrix = tuple(tuple(row[:8]) for row in child)
        extension = tuple(row[8] for row in child)
        parent_signs = exact_topes.parent_signs(matrix)
        if 0 in parent_signs:
            raise AssertionError(f"{label} child has a nonuniform parent")
        current_parent = "".join("+" if value > 0 else "-" for value in parent_signs)
        if current_parent != parent:
            raise AssertionError(f"{label} child has the wrong parent chirotope")
        rows = exact_topes.derived_rows(matrix, normalize=False)
        extension_values = tuple(
            exact_topes.dot(row, extension) for row in rows
        )
        if not all(extension_values):
            raise AssertionError(f"{label} child is not a uniform extension")
        actual_present = sum(
            (value > 0) << index
            for index, value in enumerate(extension_values)
        )
        if actual_present != present:
            raise AssertionError(f"{label} child realizes the wrong signature")

        absent_support = parse_support(absent_support_text)
        absent_coefficients = raw_circuit(rows, absent_support)
        if absent_coefficients != expected_absent_coefficients:
            raise AssertionError(f"{label} reciprocal circuit coefficients changed")
        if not positive(absent, absent_support, absent_coefficients):
            raise AssertionError(f"{label} reciprocal badness circuit is not positive")
        records.append(
            (
                label,
                child,
                present,
                absent,
                absent_support,
                absent_coefficients,
            )
        )
    return tuple(records)


def main():
    wall_supports = labeled.occurrence_representatives()
    wall = wall_supports[WALL_TYPE]
    partner = parse_support(PARTNER_TEXT)

    matrix = wall_tools.integer_matrix(POINT)
    parent_signs = exact_topes.parent_signs(matrix)
    if 0 in parent_signs:
        raise AssertionError("the displayed parent point is not uniform")
    parent = "".join("+" if value > 0 else "-" for value in parent_signs)
    if parent != EXPECTED_PARENT:
        raise AssertionError("the displayed parent chirotope changed")

    _unused, extensions = gate.enumerate_extensions(parent)
    extensions = tuple(map(int, extensions))
    if len(extensions) != EXPECTED_EXTENSIONS:
        raise AssertionError("the exact extension census changed")
    if RHO not in extensions or ETA not in extensions:
        raise AssertionError("the displayed signatures are not valid extensions")

    factor_ids, factor_polynomials = wall_tools.canonical_data()
    if factor_ids[WALL_TYPE] != WALL_FACTOR:
        raise AssertionError("the canonical type-50 factor changed")
    zeros = residual_factor_zeros(factor_polynomials, POINT)
    if zeros != (WALL_FACTOR,):
        raise AssertionError(("the point is not on one generic residual wall", zeros))
    germ_record = support_drop_germ(
        parent,
        factor_polynomials[WALL_FACTOR],
        POINT,
        GERM_PIVOT,
        GERM_EPSILON,
        RHO,
        wall,
        GERM_SIDE_SUPPORTS,
    )

    raw_rows = exact_topes.derived_rows(matrix, normalize=False)
    wall_coefficients = raw_circuit(raw_rows, wall)
    partner_coefficients = raw_circuit(raw_rows, partner)
    if not positive(RHO, wall, wall_coefficients):
        raise AssertionError("rho does not make the wall circuit positive")
    if not positive(ETA, partner, partner_coefficients):
        raise AssertionError("eta does not make the partner circuit positive")
    if moving.compatible_shears((RHO, ETA), (wall, partner)):
        raise AssertionError("the selected witness pair acquired a compatible shear")

    rows = exact_topes.derived_rows(matrix)
    topes = exact_topes.enumerate_topes(rows, dimension=4)
    exact_topes.verify_topes(rows, topes)
    if len(topes) != EXPECTED_TOPES or len(set(topes)) != EXPECTED_TOPES:
        raise AssertionError("the complete wall-tope census changed")
    if RHO in topes or ETA in topes:
        raise AssertionError("a displayed bad signature became feasible")

    prepared = escape.prepare_directions(tuple(topes))
    rho_mask = escape.escape_mask(RHO, prepared)
    eta_mask = escape.escape_mask(ETA, prepared)
    intersection = rho_mask & eta_mask
    if rho_mask != EXPECTED_RHO_MASK or eta_mask != EXPECTED_ETA_MASK:
        raise AssertionError("a full escape mask changed")
    if intersection != EXPECTED_INTERSECTION:
        raise AssertionError("the full escape-mask intersection changed")

    exclusive_records = exclusive_child_records(parent)

    digest = semantic_digest(
        parent,
        extensions,
        wall,
        partner,
        wall_coefficients,
        partner_coefficients,
        topes,
        rho_mask,
        eta_mask,
        germ_record,
        exclusive_records,
    )
    if EXPECTED_DIGEST is not None and digest != EXPECTED_DIGEST:
        raise AssertionError("the exchange-repair semantic digest changed")

    common = tuple(
        escape.DIRECTIONS[index]
        for index in range(len(escape.DIRECTIONS))
        if (intersection >> index) & 1
    )
    print("PASS exact uniform generic type-50 wall; sole zero factor", WALL_FACTOR)
    print("PASS transverse support-drop germ with a strict rho circuit on both sides")
    print("PASS exact child matrices: feasibility regions proper and incomparable")
    print("PASS valid extensions and strict positive 4+5 selected witnesses")
    print("PASS selected-witness compatible ordered shears: 0/56")
    print("PASS complete wall topes:", len(topes))
    print(
        "PASS full escape masks:",
        rho_mask.bit_count(),
        eta_mask.bit_count(),
        "intersection",
        intersection.bit_count(),
    )
    print("COMMON ORIENTED SHEARS", common)
    print("SEMANTIC DIGEST", digest)
    print("SCOPE witness-exchange repair at one exact wall point; not diagonal two")


if __name__ == "__main__":
    main()
