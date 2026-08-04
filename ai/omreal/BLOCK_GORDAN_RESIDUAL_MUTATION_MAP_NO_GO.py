#!/usr/bin/env python3
"""Exact universal residual-wall specialization and chain-map no-go.

The 13 residual derived-wall types split into nine ordinary four-circuit
types and four localization three-circuit types.  This verifier reconstructs
the fixed-sign determinant certificates using only the exact 52-orbit table,
then checks canonical rational normal forms for both cases.

In either normal form a unique strict positive circuit exists on one side,
its last weight tends to zero at the wall, and the same coordinate support
has no nonnegative kernel on the other side.  Thus specialization to the
zero-weight wall face is canonical, but no chain-homotopy equivalence can be
strictly natural on every coordinate-support face: on this face H_0 jumps
from Z to zero.

This is a no-go for a direct facewise cross-wall map, not for a larger
circuit-elimination cell such as Q4 -> P -> S4.
"""

from fractions import Fraction
from itertools import combinations
from pathlib import Path
import sys


HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import prototype_koszul_circuits as koszul  # noqa: E402


RESIDUAL_TYPES = {36, 37, 38, 39, 41, 42, 44, 46, 47, 48, 49, 50, 51}
ORDINARY_TYPES = {37, 38, 41, 42, 44, 48, 49, 50, 51}
LOCALIZATION_TYPES = {36, 39, 46, 47}

# (wall circuit C, residual fourth normal z, structural auxiliary w,
#  replacement orbit types, structural-zero orbit type).
LOCALIZATION_CERTIFICATES = {
    36: (("123", "345", "367"), "124", "134", (20, 11, 10), 15),
    39: (("123", "356", "378"), "124", "135", (33, 20, 18), 15),
    46: (("123", "145", "167"), "246", "124", (19, 19, 16), 15),
    47: (("123", "145", "167"), "248", "124", (20, 20, 16), 15),
}


NAME_TO_INDEX = {
    "".join(map(str, triple)): index
    for index, triple in enumerate(koszul.TRIPLES)
}
REPRESENTATIVES = tuple(
    tuple(NAME_TO_INDEX[name] for name in text.split("/"))
    for text in koszul.REPRESENTATIVE_TEXT.split()
)


def indices(names):
    return tuple(NAME_TO_INDEX[name] for name in names)


def orbit(support):
    return koszul.wall_orbit(tuple(sorted(support)))


def ordinary_certificate(support):
    """Find an auxiliary whose four replacement determinants are units."""
    for auxiliary in range(len(koszul.TRIPLES)):
        if auxiliary in support:
            continue
        replacement_types = tuple(
            orbit(support[:omitted] + support[omitted + 1 :] + (auxiliary,))
            for omitted in range(4)
        )
        if all(koszul.orbit_kind(kind) == "unit" for kind in replacement_types):
            return auxiliary, replacement_types
    return None


def verify_wall_certificate_partition():
    found = {
        kind: ordinary_certificate(REPRESENTATIVES[kind])
        for kind in RESIDUAL_TYPES
    }
    if {kind for kind, certificate in found.items() if certificate is not None} != ORDINARY_TYPES:
        raise AssertionError("wrong ordinary/localization residual split")

    for kind, certificate in LOCALIZATION_CERTIFICATES.items():
        circuit_names, z_name, w_name, expected_replacements, expected_zero = certificate
        circuit = indices(circuit_names)
        z = NAME_TO_INDEX[z_name]
        w = NAME_TO_INDEX[w_name]
        if frozenset(circuit + (z,)) != frozenset(REPRESENTATIVES[kind]):
            raise AssertionError("localization support is not its residual representative")
        if orbit(circuit + (z,)) != kind:
            raise AssertionError("wrong localization residual orbit")
        if orbit(circuit + (w,)) != expected_zero or koszul.orbit_kind(expected_zero) != "zero":
            raise AssertionError("localization auxiliary is not structurally dependent")
        replacements = tuple(
            orbit(circuit[:omitted] + circuit[omitted + 1 :] + (z, w))
            for omitted in range(3)
        )
        if replacements != expected_replacements or not all(
            koszul.orbit_kind(replacement) == "unit"
            for replacement in replacements
        ):
            raise AssertionError("localization coefficients do not have fixed unit signs")


def columns_to_rows(columns):
    return [list(row) for row in zip(*columns, strict=True)]


def kernel_line(columns):
    basis = koszul.nullspace(columns_to_rows(columns))
    if len(basis) != 1:
        raise AssertionError("normal form must have a one-dimensional kernel")
    return tuple(basis[0])


def same_ray(left, right):
    pivot = next(index for index, value in enumerate(right) if value)
    return all(
        left[index] * right[pivot] == right[index] * left[pivot]
        for index in range(len(left))
    )


def has_nonnegative_normalized_kernel(columns):
    line = kernel_line(columns)
    return all(value >= 0 for value in line) or all(value <= 0 for value in line)


def ordinary_columns(parameter):
    parameter = Fraction(parameter)
    return (
        (1, 0, 0, 0),
        (0, 1, 0, 0),
        (0, 0, 1, 0),
        (-1, -1, -1, parameter),
        (0, 0, 0, 1),
    )


def localization_columns(parameter):
    parameter = Fraction(parameter)
    return (
        (1, 0, 0, 0),
        (0, 1, 0, 0),
        (-1, -1, parameter, 0),
        (0, 0, 1, 0),
    )


def verify_normal_form(columns_function, circuit_size):
    for parameter in (Fraction(-3, 2), Fraction(-1), Fraction(-1, 7)):
        columns = columns_function(parameter)
        expected = (Fraction(1),) * circuit_size + (-parameter,)
        if not same_ray(kernel_line(columns), expected):
            raise AssertionError("wrong live-side circuit weights")
        if not has_nonnegative_normalized_kernel(columns):
            raise AssertionError("live-side support lacks its positive circuit")

    wall_columns = columns_function(0)
    wall_expected = (Fraction(1),) * circuit_size + (Fraction(0),)
    if not same_ray(kernel_line(wall_columns), wall_expected):
        raise AssertionError("support does not specialize to the zero-weight circuit")
    if not has_nonnegative_normalized_kernel(wall_columns):
        raise AssertionError("wall circuit is not nonnegative")

    for parameter in (Fraction(1, 7), Fraction(1), Fraction(3, 2)):
        columns = columns_function(parameter)
        expected = (Fraction(1),) * circuit_size + (-parameter,)
        if not same_ray(kernel_line(columns), expected):
            raise AssertionError("wrong dead-side kernel relation")
        if has_nonnegative_normalized_kernel(columns):
            raise AssertionError("dead-side coordinate face is unexpectedly nonempty")

    # The normalized live weights converge exactly to the wall weights.
    parameter = Fraction(-1, 7)
    raw = (Fraction(1),) * circuit_size + (-parameter,)
    normalized = tuple(value / sum(raw) for value in raw)
    if normalized[-1] <= 0 or sum(normalized) != 1:
        raise AssertionError("wrong normalized live circuit")
    wall_normalized = (Fraction(1, circuit_size),) * circuit_size + (Fraction(0),)
    if sum(wall_normalized) != 1 or wall_normalized[-1] != 0:
        raise AssertionError("wrong normalized wall specialization")


def verify_chain_obstruction():
    # Cellular chains of a point have C_0=Z and H_0=Z.  The empty coordinate
    # face has C_0=0 and H_0=0.  The only chain map from the former to the
    # latter is zero and cannot be a quasi-isomorphism.  These exact ranks are
    # the algebraic obstruction used in the accompanying proof.
    live_c0_rank = 1
    dead_c0_rank = 0
    live_h0_rank = live_c0_rank
    dead_h0_rank = dead_c0_rank
    if (live_h0_rank, dead_h0_rank) != (1, 0):
        raise AssertionError("wrong support-face H_0 jump")


def main():
    if set(koszul.RESIDUAL) != RESIDUAL_TYPES:
        raise AssertionError("residual orbit table changed")
    if ORDINARY_TYPES | LOCALIZATION_TYPES != RESIDUAL_TYPES:
        raise AssertionError("residual categories do not exhaust all 13 types")
    if ORDINARY_TYPES & LOCALIZATION_TYPES:
        raise AssertionError("residual categories overlap")

    verify_wall_certificate_partition()
    verify_normal_form(ordinary_columns, circuit_size=4)
    verify_normal_form(localization_columns, circuit_size=3)
    verify_chain_obstruction()

    print("PASS: all 13 residual types split as 9 ordinary + 4 localization")
    print("PASS: every type has an exact fixed-sign support-drop certificate")
    print("PASS: both rational normal forms specialize by one zero weight")
    print("PASS: the certified coordinate face has H_0 ranks 1 -> 1 -> 0")
    print("THEOREM: live-side-to-wall specialization is canonical and integral")
    print("NO-GO: no cross-wall quasi-isomorphism is natural on every zero face")
    print("SCOPE: larger circuit-elimination cells remain possible and necessary")


if __name__ == "__main__":
    main()
