#!/usr/bin/env python3
"""Exact single-variable affine-fiber closure of the relative-label residue.

`DIAG2_PIVOT_LABELED_PAIR_THEOREM.md` certifies 9,361 of the 9,476 unordered
relative-label residual-factor pair orbits as noncompact, leaving a 115-orbit
residue entirely inside the three factor families 49, 50, 51 (pair types
(49,50), (49,51), (50,50), (50,51), (51,51)).

This checker applies a cheaper, more general sufficient condition than any
previously used certificate family, and shows it closes all but four of the
6,890 candidate pairs across those five factor-type combinations (a superset
of the 115-orbit residue: most of the 6,890 already had a certificate from
`DIAG2_PIVOT_LABELED_PAIR_ORBITS_VERIFY.py`, this checker just gives an
independent, cheaper proof that also happens to cover them).

The condition: eliminate the first wall's pivot variable using its own
residual equation (linear in that variable, exactly as in
`verify_diag2_pivot_49_pair_saturation.py`, generalized here to a pivot whose
coefficient is a nonconstant bracket rather than the unit coefficient q_49
happens to have), then check whether the resulting restricted polynomial is
affine (degree <= 1) in ANY one of its remaining 8 variables. If it is, the
following two already-established repository lemmas combine to prove every
connected component of the common zero locus, intersected with the open
uniform parent cell, is noncompact:

  * the fixed-minor noncompactness lemma (`RESIDUAL_STRATUM_NONCOMPACTNESS.md`
    section 1): a single nowhere-vanishing partial derivative on a component
    makes projection dropping that coordinate a local diffeomorphism onto a
    nonempty open (hence noncompact) subset of R^7;
  * the fiber-linear escape (`DIAG2_PIVOT_49_PAIR_SATURATION.md` section 3):
    if that partial derivative (the affine coefficient) instead vanishes at a
    point of the component, the whole coordinate line through that point lies
    in the (purely algebraic) zero set. Intersect that line with the open
    parent cell FIRST and take the connected piece J through the point (the
    component C is a component of zero-set-intersect-X, so J -- connected,
    inside zero-set-intersect-X, meeting C -- lies inside C by maximality of
    connected components). J is nonempty and open in the line, hence either
    unbounded (so C, containing J, is unbounded too -- not compact) or
    missing a limit point at a parent-bracket zero (so that point is a limit
    point of C not in C, so C is not closed, hence not compact).

Combined, these cover every point of a hypothetical compact component, so
"affine in some variable" alone -- no ideal saturation, no smoothness
certificate -- is sufficient for noncompactness. This is strictly weaker
input than what `verify_diag2_pivot_49_pair_saturation.py` establishes (that
script additionally proves the localized critical ideal is the unit ideal,
giving the stronger "smooth 7-manifold" conclusion for its seven cases), but
it is far cheaper to check and, empirically, almost universal in this family.

Exactly four candidate pairs are NOT affine in any variable:
(50,7861), (50,7977), (50,12128), (50,20046), all of type (50,50)/(50,51).
This checker independently re-confirms, via the existing all-frame
certificate audit, that these four are genuinely unresolved by every prior
certificate mechanism too -- they are not a rank drop or a compact
component, only the residue of every method tried so far, exactly as
`DIAG2_PIVOT_LABELED_PAIR_THEOREM.md`'s own convention requires.

This does not promote diagonal two. Pair-wall noncompactness -- however it is
proved -- is necessary but not sufficient: a compact simultaneous-bad
component for diagonal two could still be assembled by gluing several
noncompact pair-wall pieces together across shared points where two DIFFERENT
residual factors both vanish (an internal transition, not a parent-bracket
boundary). That gluing/cycling question is untouched by this checker. See
`NINE_DIAGONAL_STATUS.md`'s "Surviving strategies" section 6 and
`DIAG2_PIVOT_ALL_COMPACT_SECOND_WALL.md`.
"""

from __future__ import annotations

import sys
from pathlib import Path


HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import DIAG2_PIVOT_LABELED_PAIR_ORBITS_VERIFY as labeled  # noqa: E402
import DIAG2_PIVOT_REPRESENTATIVE_GRADIENT_VERIFY as representative  # noqa: E402
import verify_residual_log_binomials as poly  # noqa: E402


VARS = "abcdefghi"
ZERO_MONOMIAL = (0,) * 9

# Pivot variable for each canonical residual wall type: the coordinate each
# q_k is exactly linear in, independently re-derived below (asserted, not
# assumed) rather than copied from verify_derived_walls.py's PIVOT table.
PIVOT_VAR = {
    36: "a", 37: "a", 38: "a", 39: "a", 41: "a", 42: "a",
    44: "d", 46: "a", 47: "a", 48: "a", 49: "d", 50: "d", 51: "f",
}

TARGET_GROUPS = ((49, 50), (49, 51), (50, 50), (50, 51), (51, 51))
EXPECTED_GROUP_SIZES = {
    (49, 50): 2544,
    (49, 51): 1284,
    (50, 50): 1411,
    (50, 51): 1272,
    (51, 51): 379,
}
EXPECTED_TOTAL = 6890
EXPECTED_AFFINE_COUNT = 6886
EXPECTED_EXCEPTIONS = ((50, 7861), (50, 7977), (50, 12128), (50, 20046))


def build_residual():
    a, b, c, d, e, f, g, h, i = (poly.variable(index) for index in range(9))
    add, mul, sub, neg = poly.add, poly.multiply, poly.subtract, poly.negative
    return {
        36: add(sub(sub(mul(a, f), mul(c, d)), f), c),
        37: add(
            add(add(sub(mul(a, e), mul(a, f)), sub(b, mul(b, d))), sub(mul(c, d), c)),
            sub(f, e),
        ),
        38: add(
            add(
                add(
                    add(add(mul(a, e, i), neg(mul(a, f, h))), add(neg(mul(b, d, i)), mul(b, f, g))),
                    add(neg(mul(b, f)), mul(b, i)),
                ),
                add(add(mul(c, d, h), neg(mul(c, e, g))), add(mul(c, e), neg(mul(c, h)))),
            ),
            add(neg(mul(e, i)), mul(f, h)),
        ),
        39: add(
            add(add(sub(mul(a, f), mul(a, i)), neg(mul(c, d, i))), add(mul(c, f, g), neg(mul(c, f)))),
            add(add(mul(c, i), mul(d, i)), neg(mul(f, g))),
        ),
        41: add(add(sub(mul(a, e), a), sub(c, mul(c, d))), sub(d, e)),
        42: add(
            add(add(sub(mul(a, e), mul(a, h)), neg(mul(c, d, h))), add(mul(c, e, g), neg(mul(c, e)))),
            add(add(mul(c, h), mul(d, h)), neg(mul(e, g))),
        ),
        44: add(
            add(
                add(
                    add(add(mul(a, e, i), neg(mul(a, e))), add(neg(mul(a, f, h)), mul(a, f))),
                    sub(mul(a, h), mul(a, i)),
                ),
                add(
                    add(mul(c, d, h), neg(mul(c, d, i))),
                    add(neg(mul(c, e, g)), mul(c, e)),
                ),
            ),
            add(
                add(add(mul(c, f, g), neg(mul(c, f))), sub(mul(c, i), mul(c, h))),
                add(
                    add(sub(mul(d, i), mul(d, h)), sub(mul(e, g), mul(e, i))),
                    sub(mul(f, h), mul(f, g)),
                ),
            ),
        ),
        46: add(sub(mul(a, f), mul(b, f)), sub(mul(c, e), mul(c, d))),
        47: add(sub(mul(a, f), mul(b, f)), sub(mul(c, e), mul(c, d))),
        48: add(add(a, mul(b, c)), neg(add(b, c))),
        49: add(add(mul(b, f), d), neg(add(b, f))),
        50: add(add(mul(b, f), mul(d, i)), neg(add(mul(b, i), mul(f, g)))),
        51: add(
            add(
                add(add(mul(a, b, f), neg(mul(a, c, e))), sub(mul(a, c, h), mul(a, f, h))),
                add(neg(mul(b, b, f)), mul(b, c, e)),
            ),
            add(
                add(neg(mul(b, c, g)), mul(b, f, h)),
                sub(mul(c, e, g), mul(c, e, h)),
            ),
        ),
    }


RESIDUAL = build_residual()


def check_residual_against_sympy():
    """Independent cross-check of RESIDUAL against a from-scratch sympy
    expansion of the same 13 formulas (transcribed from `verify_derived_walls
    .py`'s human-readable sympy table), catching any transcription slip in
    the dict-poly construction above."""

    import sympy as sp

    va, vb, vc, vd, ve, vf, vg, vh, vi = sp.symbols("a b c d e f g h i")
    sympy_vars = (va, vb, vc, vd, ve, vf, vg, vh, vi)
    sympy_residual = {
        36: va * vf - vc * vd + vc - vf,
        37: va * ve - va * vf - vb * vd + vb + vc * vd - vc - ve + vf,
        38: va * ve * vi - va * vf * vh - vb * vd * vi + vb * vf * vg - vb * vf + vb * vi
            + vc * vd * vh - vc * ve * vg + vc * ve - vc * vh - ve * vi + vf * vh,
        39: va * vf - va * vi - vc * vd * vi + vc * vf * vg - vc * vf + vc * vi + vd * vi - vf * vg,
        41: va * ve - va - vc * vd + vc + vd - ve,
        42: va * ve - va * vh - vc * vd * vh + vc * ve * vg - vc * ve + vc * vh + vd * vh - ve * vg,
        44: va * ve * vi - va * ve - va * vf * vh + va * vf + va * vh - va * vi + vc * vd * vh - vc * vd * vi
            - vc * ve * vg + vc * ve + vc * vf * vg - vc * vf - vc * vh + vc * vi - vd * vh + vd * vi
            + ve * vg - ve * vi - vf * vg + vf * vh,
        46: va * vf - vb * vf - vc * vd + vc * ve,
        47: va * vf - vb * vf - vc * vd + vc * ve,
        48: va + vb * vc - vb - vc,
        49: vb * vf - vb + vd - vf,
        50: vb * vf - vb * vi + vd * vi - vf * vg,
        51: va * vb * vf - va * vc * ve + va * vc * vh - va * vf * vh - vb ** 2 * vf
            + vb * vc * ve - vb * vc * vg + vb * vf * vh + vc * ve * vg - vc * ve * vh,
    }

    def to_dict_poly(expr):
        out = {}
        for monom, coeff in sp.Poly(sp.expand(expr), *sympy_vars).terms():
            out[tuple(int(v) for v in monom)] = int(coeff)
        return out

    for kind in RESIDUAL:
        if to_dict_poly(sympy_residual[kind]) != poly.clean(RESIDUAL[kind]):
            raise AssertionError(f"RESIDUAL[{kind}] does not match the independent sympy expansion")


def primitive(polynomial):
    import math

    polynomial = poly.clean(dict(polynomial))
    if not polynomial:
        return polynomial
    divisor = 0
    for coefficient in polynomial.values():
        divisor = math.gcd(divisor, abs(coefficient))
    if divisor > 1:
        polynomial = {m: c // divisor for m, c in polynomial.items()}
    leading_monomial = max(
        polynomial,
        key=lambda m: (sum(m), tuple(-m[i] for i in reversed(range(9)))),
    )
    if polynomial[leading_monomial] < 0:
        polynomial = {m: -c for m, c in polynomial.items()}
    return polynomial


def power(polynomial, exponent):
    answer = poly.constant(1)
    for _ in range(exponent):
        answer = poly.multiply(answer, polynomial)
    return answer


def eliminate(k, target_polynomial):
    """Eliminate PIVOT_VAR[k] from target_polynomial using q_k = 0.

    q_k is exactly linear in its pivot p: q_k = U*p + V, with U,V independent
    of p (checked below). On q_k=0, p = -V/U; to eliminate p from a second
    polynomial P without introducing fractions, compute

        raw = U^E * P(p -> -V/U),      E = max degree of p in P,

    an honest integer polynomial. U is itself a signed bracket product
    (nonzero throughout the uniform realizable cell), so this scaling never
    introduces or removes zeros on the locus that matters.
    """

    p_index = VARS.index(PIVOT_VAR[k])
    q_k = RESIDUAL[k]
    U = representative.derivative(q_k, p_index)
    if any(monomial[p_index] for monomial in U):
        raise AssertionError(f"pivot {PIVOT_VAR[k]} still present in dq_{k}")
    V = {mono: coeff for mono, coeff in q_k.items() if mono[p_index] == 0}
    rebuilt = poly.add(poly.multiply(U, poly.variable(p_index)), V)
    if poly.clean(rebuilt) != poly.clean(q_k):
        raise AssertionError(f"q_{k} is not exactly U*p + V for pivot {PIVOT_VAR[k]}")

    E = max((mono[p_index] for mono in target_polynomial), default=0)
    neg_V = poly.negative(V)
    raw = poly.constant(0)
    for monomial, coefficient in target_polynomial.items():
        e = monomial[p_index]
        base = list(monomial)
        base[p_index] = 0
        raw = poly.add(
            raw,
            poly.multiply(
                {tuple(base): coefficient}, power(neg_V, e), power(U, E - e)
            ),
        )
    return poly.clean(raw)


def affine_variables(k, restricted):
    # An empty (identically zero) restricted polynomial would mean the
    # "second wall" vanishes everywhere q_k does -- a degenerate, not
    # genuinely distinct, pair -- and every remaining variable would
    # trivially read as degree 0 (vacuously "affine"), silently
    # misclassifying an empty/degenerate locus as a real escape. Reject that
    # case explicitly rather than let it pass by default=0. (Swept over all
    # 6,890 candidates below: this never actually triggers.)
    if not restricted:
        raise AssertionError(f"degenerate (identically zero) restricted polynomial for type {k}")
    pivot = PIVOT_VAR[k]
    return tuple(
        v
        for v in VARS
        if v != pivot
        and max((mono[VARS.index(v)] for mono in restricted), default=0) <= 1
    )


def check_affine_detector_canaries():
    """A checker that always reports 'affine' is worthless. Confirm the
    detector correctly distinguishes an affine coordinate from a
    non-affine one on two hand-built polynomials before trusting it on the
    real data. (A variable absent from the polynomial entirely -- degree 0 --
    correctly counts as affine too: it gives an even more immediate escape,
    since the whole fiber through any zero is then automatically a zero.
    The canaries therefore test membership, not the full returned set.)"""

    x0, x1 = poly.variable(0), poly.variable(1)
    truly_affine = poly.add(x0, power(x1, 5))  # degree 1 in a, degree 5 in b
    detected = affine_variables(49, truly_affine)
    if "a" not in detected:
        raise AssertionError("canary failed: degree-1 variable not detected as affine")
    if "b" in detected:
        raise AssertionError("canary failed: degree-5 variable wrongly detected as affine")
    nowhere_affine_in_ab = poly.add(power(x0, 2), power(x1, 2), poly.constant(1))
    detected2 = affine_variables(49, nowhere_affine_in_ab)
    if {"a", "b"} & set(detected2):
        raise AssertionError("canary failed: degree-2 variable wrongly detected as affine")


def main():
    check_residual_against_sympy()
    print("PASS: 13 RESIDUAL dict-polys independently match sympy expansions of the derived-wall formulas")
    check_affine_detector_canaries()
    print("PASS: affine-variable detector canaries (known-affine / known-non-affine) both correct")

    occurrences, occurrence_factor, factor_polynomial = labeled.factor_polynomials()
    pair_orbits, _ordered_counts, _orbit_sizes = labeled.pair_orbit_representatives(
        occurrences, occurrence_factor
    )
    _representatives, _stabilizers, factor_alignment, _factor_occurrence, _orbit_sizes2 = (
        labeled.factor_orbit_data(occurrences, occurrence_factor)
    )
    factor_type = {factor: kind for factor, (kind, _align) in factor_alignment.items()}

    groups: dict[tuple[int, int], list[tuple[int, int]]] = {}
    for kind, second in pair_orbits:
        key = tuple(sorted((kind, factor_type[second])))
        if key in TARGET_GROUPS:
            groups.setdefault(key, []).append((kind, second))

    group_sizes = {key: len(groups.get(key, ())) for key in TARGET_GROUPS}
    if group_sizes != EXPECTED_GROUP_SIZES:
        raise AssertionError(f"candidate group sizes changed: {group_sizes}")
    print("PASS: 6,890 candidate pairs across the five hard factor-type families:", group_sizes)

    exceptions = []
    affine_count = 0
    total = 0
    for key in TARGET_GROUPS:
        for kind, second in groups[key]:
            total += 1
            restricted = primitive(eliminate(kind, factor_polynomial[second]))
            if affine_variables(kind, restricted):
                affine_count += 1
            else:
                exceptions.append((kind, second))

    if total != EXPECTED_TOTAL:
        raise AssertionError(f"wrong candidate total: {total}")
    if affine_count != EXPECTED_AFFINE_COUNT:
        raise AssertionError(f"affine-fiber count changed: {affine_count}")
    if tuple(sorted(exceptions)) != EXPECTED_EXCEPTIONS:
        raise AssertionError(f"exception list changed: {sorted(exceptions)}")

    print(f"PASS: {affine_count}/{total} candidate pairs are affine in some non-pivot variable")
    print("THEOREM: every one of those", affine_count, "pair-wall common-zero loci is noncompact")
    print("STATUS exceptions (not affine in any variable):", exceptions)

    audit = labeled.audit_pairs(
        EXPECTED_EXCEPTIONS,
        factor_polynomial,
        occurrences,
        occurrence_factor,
        all_frames=True,
        progress=False,
    )
    certified, residue = audit[:2]
    if certified or tuple(sorted(residue)) != EXPECTED_EXCEPTIONS:
        raise AssertionError("the four exceptions are not genuinely unresolved by prior certificates")
    print("PASS: all four exceptions independently reconfirmed unresolved by every prior certificate family")
    print(
        "STATUS certified relative-label pair orbits: 9472/9476 "
        "(9361 prior + 111 newly closed here, all within the former 115-orbit residue); residue: 4"
    )
    print("CAVEAT: pair-wall noncompactness (by any method) does not by itself promote diagonal two")
    print("CAVEAT: diagonal two still requires global decorated transition-cycle acyclicity")


if __name__ == "__main__":
    main()
