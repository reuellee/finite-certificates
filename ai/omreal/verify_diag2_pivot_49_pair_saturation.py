#!/usr/bin/env python3
"""Exact uniform-locus saturation of the seven type-(49,49) pair residues.

The all-frame relative-label audit leaves seven pair orbits of factor type
(49,49).  Put the first wall in its canonical frame,

    q_49 = b*f + d - b - f = 0,

and eliminate d = b + f - b*f.  For each second wall this verifier forms the
restricted polynomial r in the eight free coordinates and proves

    <r, dr/da, dr/db, dr/dc, dr/de, dr/df, dr/dg, dr/dh, dr/di>

is the unit ideal after localizing at all parent brackets.  The calculation
uses exact integer pseudo-reduction, exact S-polynomials, and division only
by checked parent-bracket factors.  Reaching 1 is therefore a finite
saturation certificate that the two wall gradients have rank two everywhere
on the uniform common-zero locus.

Every r is affine-linear in g.  Smoothness plus this fiber-linearity gives a
proper escape from every common-zero component: at a zero of the g
coefficient the whole local g-fiber lies in the zero set, while otherwise a
hypothetical compact component projects locally diffeomorphically to a
nonempty compact open subset of R^7.  Thus all seven pair-wall components are
noncompact.
"""

from __future__ import annotations

import hashlib
import heapq
import math
from pathlib import Path
import sys


HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import DIAG2_PIVOT_LABELED_PAIR_ORBITS_VERIFY as labeled  # noqa: E402
import DIAG2_PIVOT_REPRESENTATIVE_GRADIENT_VERIFY as representative  # noqa: E402
import DIAG2_PIVOT_REPRESENTATIVE_TRIPLES_VERIFY as triples  # noqa: E402
import verify_residual_log_binomials as poly  # noqa: E402


ZERO_MONOMIAL = (0,) * 9
ACTIVE_VARIABLES = (0, 1, 2, 4, 5, 6, 7, 8)
# Graded reverse lexicographic order with a presentation chosen to keep every
# exact certificate short.  The omitted d coordinate is retained harmlessly
# in the order so all polynomials use the repository-wide nine-tuples.
MONOMIAL_ORDER = "giahcefbd"
ORDER_INDICES = tuple("abcdefghi".index(value) for value in MONOMIAL_ORDER)

# (original residue second-factor ID, stabilizer-equivalent target ID).
RESIDUE_TARGETS = (
    (8213, 22372),
    (8217, 25501),
    (8220, 20698),
    (8221, 20753),
    (17797, 21972),
    (17802, 21863),
    (21722, 21862),
)

# target: (restricted terms, degree, basis size including 1, S-pairs used,
#          bracket divisions, terminal provenance, exact trace digest)
EXPECTED = {
    22372: (
        26, 5, 7, 0, 3,
        ("generator", 6, ("1247", "1267")),
        "1691a3954394a332d2f48e880028ab7e8ec7bb52a5a1662cfd73e43d66791f14",
    ),
    25501: (
        16, 5, 8, 0, 4,
        ("generator", 7, ("1237", "1468")),
        "28a7ecc130dd32bf7606f5d92e36b951172496ba95d06137944fefbcbe6bba79",
    ),
    20698: (
        26, 5, 9, 0, 4,
        ("generator", 8, ("1247", "1467")),
        "3737517d7e507a9ebd7cbd6d6fc5606dff605ce8c43346ee28e49711bd0d4d70",
    ),
    20753: (
        16, 5, 7, 0, 3,
        ("generator", 6, ("1247", "1267")),
        "4aa6947f2f6e4878dc80ad2bd04044d7bc13a6c05bd1f6d317bf9357afea6bb9",
    ),
    21972: (
        22, 6, 5, 0, 5,
        ("generator", 4, ("1246", "1348", "2367", "2378")),
        "cc918d699ec7e8f936cb012f08c0cdf677a2f5bc5e79c975bbee912a6c95e270",
    ),
    21863: (
        52, 6, 10, 1, 5,
        ("spoly", 1, 8, ("1257", "2468", "1478")),
        "8afa8f557d1240101cc54568b58cde491aca9ea3042c36419ce006169fa56078",
    ),
    21862: (
        52, 6, 22, 19, 9,
        ("spoly", 14, 16, ("1248", "1257", "4678")),
        "3872029e26a46215831487c377b77789e2da7b9290050b2504134ce3e4031ded",
    ),
}


def monomial_order(monomial):
    return (
        sum(monomial),
        tuple(-monomial[index] for index in reversed(ORDER_INDICES)),
    )


def leading(polynomial):
    return max(polynomial, key=monomial_order)


def primitive(polynomial):
    polynomial = poly.clean(polynomial)
    if not polynomial:
        return polynomial
    divisor = 0
    for coefficient in polynomial.values():
        divisor = math.gcd(divisor, abs(coefficient))
    if divisor > 1:
        polynomial = {
            monomial: coefficient // divisor
            for monomial, coefficient in polynomial.items()
        }
    if polynomial[leading(polynomial)] < 0:
        polynomial = poly.negative(polynomial)
    return polynomial


def power(polynomial, exponent):
    answer = poly.constant(1)
    for _ in range(exponent):
        answer = poly.multiply(answer, polynomial)
    return answer


def q49_graph_value():
    b = poly.variable(1)
    f = poly.variable(5)
    return poly.add(b, f, poly.negative(poly.multiply(b, f)))


def substitute_d_raw(polynomial):
    graph_value = q49_graph_value()
    answer = poly.constant(0)
    for monomial, coefficient in polynomial.items():
        exponent = monomial[3]
        base = list(monomial)
        base[3] = 0
        answer = poly.add(
            answer,
            poly.multiply(
                {tuple(base): coefficient},
                power(graph_value, exponent),
            ),
        )
    return poly.clean(answer)


def substitute_d(polynomial):
    return primitive(substitute_d_raw(polynomial))


def q49_quotient_witness(polynomial, restricted):
    """Return Q for the raw q_49 graph remainder, checking it exactly."""

    graph_value = q49_graph_value()
    raw_restricted = substitute_d_raw(polynomial)
    if primitive(raw_restricted) != restricted:
        raise AssertionError("wrong primitive q_49 graph remainder")
    d = poly.variable(3)
    q49 = poly.subtract(d, graph_value)
    quotient = poly.constant(0)
    for monomial, coefficient in polynomial.items():
        exponent = monomial[3]
        if not exponent:
            continue
        base = list(monomial)
        base[3] = 0
        for index in range(exponent):
            d_exponent = [0] * 9
            d_exponent[3] = exponent - 1 - index
            quotient = poly.add(
                quotient,
                poly.multiply(
                    {tuple(base): coefficient},
                    {tuple(d_exponent): 1},
                    power(graph_value, index),
                ),
            )
    if poly.subtract(polynomial, raw_restricted) != poly.multiply(q49, quotient):
        raise AssertionError("wrong q_49 graph-remainder identity")
    return quotient


def restricted_parent_brackets():
    answer = []
    seen = set()
    for label, bracket, _sign in labeled.parent_bracket_factors():
        bracket = primitive(substitute_d(bracket))
        if not bracket:
            raise AssertionError(f"parent bracket {label} vanishes on q_49")
        if len(bracket) == 1 and ZERO_MONOMIAL in bracket:
            continue
        key = tuple(sorted(bracket.items()))
        if key in seen:
            continue
        seen.add(key)
        answer.append((label, bracket))
    answer.sort(key=lambda item: (len(item[1]), item[0]))
    if len(answer) != 62:
        raise AssertionError("wrong restricted parent-bracket factor count")
    return tuple(answer)


def monomial_divides(left, right):
    return all(first <= second for first, second in zip(left, right))


def monomial_quotient(numerator, denominator):
    return tuple(
        first - second for first, second in zip(numerator, denominator)
    )


def monomial_lcm(left, right):
    return tuple(max(first, second) for first, second in zip(left, right))


def relatively_prime(left, right):
    return all(not min(first, second) for first, second in zip(left, right))


def multiply_term(polynomial, monomial, coefficient):
    return {
        tuple(first + second for first, second in zip(source, monomial)):
            value * coefficient
        for source, value in polynomial.items()
    }


def pseudo_reduce(polynomial, basis):
    """Exact rational normal form represented by primitive integer data."""

    polynomial = primitive(dict(polynomial))
    remainder = {}
    while polynomial:
        lead = leading(polynomial)
        reducer = next(
            (
                candidate
                for candidate in basis
                if monomial_divides(leading(candidate), lead)
            ),
            None,
        )
        if reducer is None:
            remainder[lead] = polynomial.pop(lead)
            continue
        reducer_lead = leading(reducer)
        left_coefficient = polynomial[lead]
        right_coefficient = reducer[reducer_lead]
        divisor = math.gcd(abs(left_coefficient), abs(right_coefficient))
        scale = abs(right_coefficient) // divisor
        if scale != 1:
            remainder = {
                monomial: scale * value
                for monomial, value in remainder.items()
            }
        polynomial = poly.subtract(
            poly.multiply(poly.constant(scale), polynomial),
            multiply_term(
                reducer,
                monomial_quotient(lead, reducer_lead),
                (1 if right_coefficient > 0 else -1)
                * left_coefficient
                // divisor,
            ),
        )
        common = 0
        for coefficient in tuple(polynomial.values()) + tuple(remainder.values()):
            common = math.gcd(common, abs(coefficient))
        if common > 1:
            polynomial = {
                monomial: value // common
                for monomial, value in polynomial.items()
            }
            remainder = {
                monomial: value // common
                for monomial, value in remainder.items()
            }
    return primitive(remainder)


def s_polynomial(left, right):
    left_lead = leading(left)
    right_lead = leading(right)
    common = monomial_lcm(left_lead, right_lead)
    left_coefficient = left[left_lead]
    right_coefficient = right[right_lead]
    divisor = math.gcd(abs(left_coefficient), abs(right_coefficient))
    return primitive(
        poly.subtract(
            multiply_term(
                left,
                monomial_quotient(common, left_lead),
                abs(right_coefficient) // divisor,
            ),
            multiply_term(
                right,
                monomial_quotient(common, right_lead),
                (1 if right_coefficient > 0 else -1)
                * left_coefficient
                // divisor,
            ),
        )
    )


def saturate_parent_units(polynomial, brackets):
    labels = []
    changed = True
    while polynomial and changed:
        changed = False
        for label, bracket in brackets:
            quotient = triples.exact_divide(polynomial, bracket)
            if quotient is None:
                continue
            polynomial = primitive(quotient)
            labels.append(label)
            changed = True
            break
    return polynomial, tuple(labels)


def localized_normal_form(polynomial, basis, brackets):
    labels = []
    while polynomial:
        polynomial = pseudo_reduce(polynomial, basis)
        polynomial, stripped = saturate_parent_units(polynomial, brackets)
        labels.extend(stripped)
        if not stripped:
            break
    return primitive(polynomial), tuple(labels)


def signature(polynomial):
    return tuple(sorted(polynomial.items()))


def localized_unit_certificate(generators, brackets):
    """Run bounded Buchberger reduction until the localized ideal contains 1."""

    basis = []
    history = []
    for source, generator in enumerate(generators):
        reduced, labels = localized_normal_form(generator, basis, brackets)
        if not reduced:
            continue
        basis.append(reduced)
        history.append(("generator", source, labels, reduced))
        if reduced == {ZERO_MONOMIAL: 1}:
            return tuple(basis), tuple(history), 0

    queue = []
    serial = 0
    for right in range(len(basis)):
        for left in range(right):
            if relatively_prime(leading(basis[left]), leading(basis[right])):
                continue
            common = monomial_lcm(leading(basis[left]), leading(basis[right]))
            heapq.heappush(queue, (sum(common), serial, left, right))
            serial += 1
    processed = 0
    known = {signature(polynomial) for polynomial in basis}
    while queue and processed < 1000 and len(basis) < 100:
        _degree, _serial, left, right = heapq.heappop(queue)
        processed += 1
        candidate, labels = localized_normal_form(
            s_polynomial(basis[left], basis[right]), basis, brackets
        )
        if not candidate or signature(candidate) in known:
            continue
        known.add(signature(candidate))
        index = len(basis)
        basis.append(candidate)
        history.append(("spoly", left, right, labels, candidate))
        if candidate == {ZERO_MONOMIAL: 1}:
            return tuple(basis), tuple(history), processed
        for old in range(index):
            if relatively_prime(leading(basis[old]), leading(candidate)):
                continue
            common = monomial_lcm(leading(basis[old]), leading(candidate))
            heapq.heappush(queue, (sum(common), serial, old, index))
            serial += 1
    raise AssertionError("bounded localized Buchberger search did not reach 1")


def trace_digest(history):
    payload = [
        (entry[:-1], tuple(sorted(entry[-1].items()))) for entry in history
    ]
    return hashlib.sha256(repr(payload).encode("ascii")).hexdigest()


def verify_residue_and_frames(
    occurrences,
    occurrence_factor,
    factor_polynomial,
):
    pair_orbits, _ordered_counts, _orbit_sizes = labeled.pair_orbit_representatives(
        occurrences, occurrence_factor
    )
    residue_pairs = tuple((49, source) for source, _target in RESIDUE_TARGETS)
    if not set(residue_pairs).issubset(pair_orbits):
        raise AssertionError("listed type-(49,49) pairs are not orbit representatives")

    audit = labeled.audit_pairs(
        residue_pairs,
        factor_polynomial,
        occurrences,
        occurrence_factor,
        all_frames=True,
        progress=False,
    )
    certified, residue = audit[:2]
    if certified or residue != residue_pairs:
        raise AssertionError("the seven pairs changed under the earlier certificate audit")

    factor_occurrence = labeled.factor_action_is_well_defined(
        occurrences, occurrence_factor
    )
    canonical, alignments, stabilizers = labeled.canonical_anchor_alignments(
        occurrences,
        occurrence_factor,
        factor_occurrence,
    )
    first = canonical[49]
    variables = tuple(poly.variable(index) for index in range(9))
    _a, b, _c, d, _e, f, _g, _h, _i = variables
    expected_q49 = poly.add(
        poly.multiply(b, f), d, poly.negative(b), poly.negative(f)
    )
    if first != 2267 or factor_polynomial[first] != expected_q49:
        raise AssertionError("canonical type-49 anchor changed")

    for source, target in RESIDUE_TARGETS:
        if source not in alignments[49]:
            raise AssertionError(f"factor {source} is not in the type-49 orbit")
        targets = {
            labeled.transform_factor(
                source,
                symmetry,
                factor_occurrence,
                occurrence_factor,
            )
            for symmetry in stabilizers[49]
        }
        if target not in targets:
            raise AssertionError(
                f"target {target} does not preserve the canonical type-49 anchor"
            )
    return first


def main():
    occurrences, occurrence_factor, factor_polynomial = labeled.factor_polynomials()
    first = verify_residue_and_frames(
        occurrences,
        occurrence_factor,
        factor_polynomial,
    )
    brackets = restricted_parent_brackets()
    reports = []
    for source, target in RESIDUE_TARGETS:
        restricted = substitute_d(factor_polynomial[target])
        q49_quotient_witness(factor_polynomial[target], restricted)
        if any(monomial[6] > 1 for monomial in restricted):
            raise AssertionError(f"restricted factor {target} is not affine in g")
        restricted_terms = len(restricted)
        restricted_degree = max(map(sum, restricted))
        generators = (dict(restricted),) + tuple(
            representative.derivative(restricted, variable)
            for variable in ACTIVE_VARIABLES
        )
        basis, history, processed = localized_unit_certificate(
            generators, brackets
        )
        if basis[-1] != {ZERO_MONOMIAL: 1}:
            raise AssertionError(f"factor {target} did not saturate to 1")
        report = (
            restricted_terms,
            restricted_degree,
            len(basis),
            processed,
            sum(len(entry[-2]) for entry in history),
            history[-1][:-1],
            trace_digest(history),
        )
        if report != EXPECTED[target]:
            raise AssertionError(
                f"saturation trace changed for target {target}: "
                f"found {report!r}, expected {EXPECTED[target]!r}"
            )
        reports.append((source, target, report))

    print("PASS canonical type-49 anchor factor:", first)
    print("PASS earlier all-frame residue cases:", tuple(source for source, _ in RESIDUE_TARGETS))
    print(
        "PASS stabilizer-equivalent saturation targets:",
        tuple(target for _, target in RESIDUE_TARGETS),
    )
    print("PASS restricted nonconstant parent-bracket units:", len(brackets))
    print("PASS localized critical ideals equal the unit ideal:", len(reports))
    print(
        "PASS bounded exact saturation traces:",
        [
            (source, report[2], report[3])
            for source, _target, report in reports
        ],
    )
    print("THEOREM all seven type-(49,49) pair-wall components are smooth and noncompact")
    print("STATUS certified relative-label pair orbits: 9361/9476; residue: 115")
    print("CAVEAT diagonal two still requires global decorated transition-cycle acyclicity")


if __name__ == "__main__":
    main()
