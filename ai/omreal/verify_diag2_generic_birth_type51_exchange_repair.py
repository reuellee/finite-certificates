#!/usr/bin/env python3
"""Second exact realized generic-birth obstruction and full-mask repair.

The second type-51 abstract survivor is realized at one uniform point of only
the canonical type-51 residual wall.  Its displayed selected circuit pair has
no compatible ordered shear, while its complete escape masks intersect in 80
oriented directions and together cover all 112 directions.
"""

from fractions import Fraction
import hashlib
from math import gcd

import DIAG2_PIVOT_LABELED_PAIR_ORBITS_VERIFY as labeled
import DIAG9_GRAPH_exact_topes as exact_topes
import four_chart_gate as gate
import verify_diag2_canonical_robust_edges as wall_tools
import verify_diag2_escape_set_topes as escape
import verify_diag2_generic_birth_exchange_repair as base
import verify_diag2_moving_witness_shear as moving


FORMAT = b"diag2-generic-birth-type51-exchange-repair-v3\0"
WALL_TYPE = 51
WALL_FACTOR = 18606
PARTNER_TEXT = "356/347/157/258/178"
RHO = 31372044921362707
ETA = 28905737156930761
POINT = tuple(
    Fraction(value)
    for value in (
        "11446597/990248",
        "-408305/876768",
        "-466319/817739",
        "1583353/502340",
        "-684317/588564",
        "-2154225755070779293978436076818878095622/3858482500362358061802956970572674848747",
        "9113705/976432",
        "-1770162/842723",
        "-225502/277953",
    )
)
EXPECTED_PARENT = (
    "++-+--++--+--++-++-++--++-++-+--+-+-++-++--++-+--+--+-+---++++++---+--"
)
EXPECTED_EXTENSIONS = 64904
EXPECTED_TOPES = 26110
EXPECTED_RHO_MASK = 0xFFFFFFFFE6D5E7AB6FFFFEB7EAF6
EXPECTED_ETA_MASK = 0xFFFD6F6FFFFFFD7ED9FFFFFFFFFF
EXPECTED_INTERSECTION = 0xFFFD6F6FE6D5E52A49FFFEB7EAF6
GERM_PIVOT = 5
GERM_EPSILON = Fraction(1, 1 << 16)
GERM_SIDE_SUPPORTS = (
    ("negative", -1, "123/124/145/267/468"),
    ("positive", 1, "123/145/167/267/468"),
)
CHILD_CERTIFICATES = (
    (
        "rho-only",
        (
            (-32, 16, -9, -3, -32, 7, -19, 14, -19),
            (3, 17, -23, 3, 9, 18, 32, 32, 7),
            (8, 10, 32, -4, 8, 32, 5, -1, -32),
            (3, -32, 3, -8, -28, 7, 20, 10, 22),
        ),
        RHO,
        ETA,
        "123/134/347/358",
        (29054093673, 164924651589, 284440152594, 54270683038),
    ),
    (
        "eta-only",
        (
            (-32, 28, -14, 7, -32, 9, -1, 25, 3),
            (12, 3, -17, 6, 12, 7, 32, 32, -16),
            (5, 32, 32, -13, 6, 32, -2, -4, -4),
            (3, -22, 7, -32, -25, 4, 27, 18, 8),
        ),
        ETA,
        RHO,
        "123/124/145/167",
        (598426376412, 392323435709, 1037609589735, 491346379323),
    ),
)
EXPECTED_DIGEST = (
    "1957aa0e56d82d362c77fb5f1a4b6e457066df2b3141c1550f51d094ea0d9801"
)


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
        bad_support,
        bad_weights,
        margins,
    ) in exclusive_records:
        digest.update(label.encode("ascii") + b"\0")
        for row in child:
            for value in row:
                digest.update(int(value).to_bytes(8, "little", signed=True))
        digest.update(present.to_bytes(8, "little"))
        digest.update(absent.to_bytes(8, "little"))
        digest.update(bytes(bad_support))
        for weight in bad_weights:
            digest.update(str(weight).encode("ascii") + b"\0")
        for margin in margins:
            digest.update(str(margin).encode("ascii") + b"\0")
    return digest.hexdigest()


def exclusive_child_records(parent):
    records = []
    for (
        label,
        child,
        present,
        absent,
        bad_support_text,
        expected_bad_weights,
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
        values = tuple(
            sum(row[coordinate] * extension[coordinate] for coordinate in range(4))
            for row in rows
        )
        margins = tuple(
            moving.signature_sign(present, index) * value
            for index, value in enumerate(values)
        )
        if not all(margin > 0 for margin in margins):
            raise AssertionError(f"{label} child does not realize its displayed signature")

        bad_support = base.parse_support(bad_support_text)
        coefficients = base.raw_circuit(rows, bad_support)
        twisted = tuple(
            coefficient * moving.signature_sign(absent, index)
            for index, coefficient in zip(bad_support, coefficients, strict=True)
        )
        if all(value < 0 for value in twisted):
            twisted = tuple(-value for value in twisted)
        if not all(value > 0 for value in twisted):
            raise AssertionError(f"{label} opposite-signature circuit is not positive")
        divisor = 0
        for value in twisted:
            divisor = gcd(divisor, value)
        bad_weights = tuple(value // divisor for value in twisted)
        if bad_weights != expected_bad_weights:
            raise AssertionError(f"{label} opposite-signature circuit weights changed")
        records.append(
            (
                label,
                child,
                present,
                absent,
                bad_support,
                bad_weights,
                margins,
            )
        )
    return tuple(records)


def main():
    wall = labeled.occurrence_representatives()[WALL_TYPE]
    partner = base.parse_support(PARTNER_TEXT)
    matrix = wall_tools.integer_matrix(POINT)
    parent_signs = exact_topes.parent_signs(matrix)
    if 0 in parent_signs:
        raise AssertionError("the type-51 parent point is not uniform")
    parent = "".join("+" if value > 0 else "-" for value in parent_signs)
    if parent != EXPECTED_PARENT:
        raise AssertionError("the type-51 parent chirotope changed")

    _unused, extensions = gate.enumerate_extensions(parent)
    extensions = tuple(map(int, extensions))
    if len(extensions) != EXPECTED_EXTENSIONS:
        raise AssertionError("the type-51 extension census changed")
    if RHO not in extensions or ETA not in extensions:
        raise AssertionError("the type-51 signatures are not valid extensions")

    factor_ids, factor_polynomials = wall_tools.canonical_data()
    if factor_ids[WALL_TYPE] != WALL_FACTOR:
        raise AssertionError("the canonical type-51 factor changed")
    zeros = base.residual_factor_zeros(factor_polynomials, POINT)
    if zeros != (WALL_FACTOR,):
        raise AssertionError(("the point is not on one generic residual wall", zeros))
    germ_record = base.support_drop_germ(
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
    wall_coefficients = base.raw_circuit(raw_rows, wall)
    partner_coefficients = base.raw_circuit(raw_rows, partner)
    if not base.positive(RHO, wall, wall_coefficients):
        raise AssertionError("rho does not make the type-51 wall circuit positive")
    if not base.positive(ETA, partner, partner_coefficients):
        raise AssertionError("eta does not make the type-51 partner circuit positive")
    if moving.compatible_shears((RHO, ETA), (wall, partner)):
        raise AssertionError("the selected type-51 witnesses acquired a shear")

    rows = exact_topes.derived_rows(matrix)
    topes = exact_topes.enumerate_topes(rows, dimension=4)
    exact_topes.verify_topes(rows, topes)
    if len(topes) != EXPECTED_TOPES or len(set(topes)) != EXPECTED_TOPES:
        raise AssertionError("the complete type-51 wall-tope census changed")
    if RHO in topes or ETA in topes:
        raise AssertionError("a displayed type-51 bad signature became feasible")

    prepared = escape.prepare_directions(tuple(topes))
    rho_mask = escape.escape_mask(RHO, prepared)
    eta_mask = escape.escape_mask(ETA, prepared)
    intersection = rho_mask & eta_mask
    union = rho_mask | eta_mask
    if rho_mask != EXPECTED_RHO_MASK or eta_mask != EXPECTED_ETA_MASK:
        raise AssertionError("a type-51 full escape mask changed")
    if intersection != EXPECTED_INTERSECTION:
        raise AssertionError("the type-51 escape-mask intersection changed")
    if union != (1 << len(escape.DIRECTIONS)) - 1:
        raise AssertionError("the type-51 mask union no longer covers 112 directions")

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
        raise AssertionError("the type-51 exchange-repair digest changed")

    print("PASS exact uniform generic type-51 wall; sole zero factor", WALL_FACTOR)
    print("PASS transverse support-drop germ with a strict rho circuit on both sides")
    print("PASS exact child certificates: feasibility regions proper and incomparable")
    print("PASS valid extensions and strict positive selected witnesses")
    print("PASS selected-witness compatible ordered shears: 0/56")
    print("PASS complete wall topes:", len(topes))
    print(
        "PASS full escape masks:",
        rho_mask.bit_count(),
        eta_mask.bit_count(),
        "intersection",
        intersection.bit_count(),
        "union",
        union.bit_count(),
    )
    print("SEMANTIC DIGEST", digest)
    print("SCOPE second witness-exchange repair point; not diagonal two")


if __name__ == "__main__":
    main()
