#!/usr/bin/env python3
"""A reduction (NOT a closure) for residue pair (50,7977).

`DIAG2_AFFINE_FIBER_RESIDUE_CLOSURE.md` leaves four pairs unresolved by the
single-coordinate affine-fiber argument: (50,7861), (50,7977), (50,12128),
(50,20046). All four share a striking structural fact -- after eliminating
q_50's pivot `d`, the restricted second-wall polynomial `r` has total degree
exactly 2 jointly in the SAME pair of coordinates `(a,c)` (holding the other
six fixed), i.e. `r` is a genuine plane conic in `(a,c)` with coefficients
`A,B,C,D,E,F` polynomial in `(b,e,f,g,h,i)`:

    r = A*a^2 + B*a*c + C*c^2 + D*a + E*c + F.

For (50,7977) specifically, the conic's discriminant `B^2-4A*C` is an EXACT
PERFECT SQUARE `S^2` for an explicit polynomial `S`, checked below. A real
plane conic with discriminant `>= 0` is never a bounded ellipse or an
isolated point -- so this genuinely rules out the shape most compatible with
compactness.

An earlier version of this checker additionally claimed this proves
noncompactness, via an explicit ray along which `r` is affine in the motion
parameter. Adversarial review caught the gap, confirmed here: the ray's
slope (its t^1 coefficient, i.e. the directional derivative of `r` along the
ray) is NOT identically zero, so at a generic point the ray only touches
{r=0} at the starting point -- it is a transversal probe, not a path that
stays on the zero locus, and does not by itself give an escape.  See
DIAG2_CONIC_FACTORIZATION_ESCAPE.md section 1 for the precise gap and
section 2 for the (unfinished) correct route -- a rational parametrization
of the conic via a linear change of coordinates diagonalizing the quadratic
form, not attempted here.

This checker verifies only what is actually established: the conic
structure, the perfect-square discriminant identity, and (as a documented
negative fact, not a claimed positive one) that the transversal ray's slope
is nonzero. It does not print a noncompactness THEOREM line, and the honest
residue count is unchanged at 4.
"""

from __future__ import annotations

import sys
from pathlib import Path


HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import DIAG2_PIVOT_LABELED_PAIR_ORBITS_VERIFY as labeled  # noqa: E402
import DIAG2_PIVOT_REPRESENTATIVE_GRADIENT_VERIFY as representative  # noqa: E402
import verify_diag2_affine_fiber_residue_closure as closure  # noqa: E402
import verify_residual_log_binomials as poly  # noqa: E402


VARS = closure.VARS
TARGET_KIND = 50
TARGET_FACTOR = 7977
# The now-freed 'd' slot (eliminated via q_50) is repurposed to represent the
# motion parameter t, avoiding the need for a tenth polynomial variable.
A_INDEX, C_INDEX, T_INDEX = VARS.index("a"), VARS.index("c"), VARS.index("d")

EXPECTED_RESTRICTED_TERMS = 175
EXPECTED_DEGREE = 7


def power(p, n):
    r = poly.constant(1)
    for _ in range(n):
        r = poly.multiply(r, p)
    return r


def conic_coefficients(restricted):
    """Split `restricted` into A,B,C,D,E,F: the degree in (a,c) at each
    monomial must be exactly one of (2,0),(1,1),(0,2),(1,0),(0,1),(0,0) --
    i.e. `restricted` really is a genuine conic in (a,c), checked here
    rather than assumed."""

    buckets = {(2, 0): {}, (1, 1): {}, (0, 2): {}, (1, 0): {}, (0, 1): {}, (0, 0): {}}
    for monomial, coefficient in restricted.items():
        da, dc = monomial[A_INDEX], monomial[C_INDEX]
        key = (da, dc)
        if key not in buckets:
            raise AssertionError(f"restricted polynomial is not a plane conic in (a,c): degree {key}")
        base = list(monomial)
        base[A_INDEX] = 0
        base[C_INDEX] = 0
        base = tuple(base)
        buckets[key][base] = buckets[key].get(base, 0) + coefficient
    return tuple(poly.clean(buckets[key]) for key in ((2, 0), (1, 1), (0, 2), (1, 0), (0, 1), (0, 0)))


def discriminant_square_root():
    b, e, f, g, h, i = (poly.variable(idx) for idx in (1, 4, 5, 6, 7, 8))
    inner = poly.subtract(
        poly.add(poly.multiply(b, f, i), poly.multiply(b, i), poly.multiply(e, i, i), poly.multiply(f, g)),
        poly.add(poly.multiply(b, f), poly.multiply(b, i, i), poly.multiply(e, g, i), poly.multiply(f, i)),
    )
    return poly.multiply(i, poly.subtract(e, h), inner)


def main():
    occurrences, occurrence_factor, factor_polynomial = labeled.factor_polynomials()
    pair_orbits, _ordered_counts, _orbit_sizes = labeled.pair_orbit_representatives(
        occurrences, occurrence_factor
    )
    pair = (TARGET_KIND, TARGET_FACTOR)
    if pair not in pair_orbits:
        raise AssertionError("(50,7977) is not a pair-orbit representative")

    audit = labeled.audit_pairs(
        (pair,), factor_polynomial, occurrences, occurrence_factor, all_frames=True, progress=False,
    )
    certified, residue = audit[:2]
    if certified or residue != (pair,):
        raise AssertionError("(50,7977) is no longer unresolved by prior certificates")
    print("PASS: (50,7977) independently reconfirmed unresolved by every prior certificate family")

    restricted = closure.primitive(closure.eliminate(TARGET_KIND, factor_polynomial[TARGET_FACTOR]))
    if len(restricted) != EXPECTED_RESTRICTED_TERMS or max(map(sum, restricted)) != EXPECTED_DEGREE:
        raise AssertionError("restricted polynomial for (50,7977) changed")
    print(f"PASS: restricted polynomial has {len(restricted)} terms, degree {EXPECTED_DEGREE}")

    A, Bc, C, Dd, Ee, F = conic_coefficients(restricted)
    print("PASS: restricted polynomial is an exact plane conic in (a,c)")

    S = discriminant_square_root()
    lhs = poly.multiply(S, S)
    rhs = poly.subtract(poly.multiply(Bc, Bc), poly.multiply(poly.constant(4), A, C))
    if poly.subtract(lhs, rhs) != {}:
        raise AssertionError("S^2 != B^2-4AC: discriminant is not this perfect square")
    print("PASS: conic discriminant B^2-4AC is exactly S^2 for the displayed S (never negative)")
    print("REDUCTION: the (a,c)-conic is never a bounded ellipse for any values of (b,e,f,g,h,i)")

    a_var = poly.variable(A_INDEX)
    c_var = poly.variable(C_INDEX)
    t_var = poly.variable(T_INDEX)
    v_a = poly.subtract(S, Bc)
    v_c = poly.multiply(poly.constant(2), A)
    a_t = poly.add(a_var, poly.multiply(t_var, v_a))
    c_t = poly.add(c_var, poly.multiply(t_var, v_c))

    r_t = poly.clean(
        poly.add(
            poly.multiply(A, power(a_t, 2)),
            poly.multiply(Bc, a_t, c_t),
            poly.multiply(C, power(c_t, 2)),
            poly.multiply(Dd, a_t),
            poly.multiply(Ee, c_t),
            F,
        )
    )
    high_degree_in_t = {monomial: coeff for monomial, coeff in r_t.items() if monomial[T_INDEX] >= 2}
    if high_degree_in_t:
        raise AssertionError(f"escape ray is not affine in t: {len(high_degree_in_t)} degree>=2 terms survive")
    print("PASS: r is exactly affine (degree <=1) in t along the transversal ray (a + t(S-B), c + 2At)")

    slope = poly.add(
        poly.multiply(v_a, poly.add(poly.multiply(poly.constant(2), A, a_var), poly.multiply(Bc, c_var), Dd)),
        poly.multiply(v_c, poly.add(poly.multiply(Bc, a_var), poly.multiply(poly.constant(2), C, c_var), Ee)),
    )
    slope = poly.clean(slope)
    if not slope:
        raise AssertionError(
            "GAP CLOSED UNEXPECTEDLY: ray slope is identically zero -- if this ever fires, "
            "the argument DOES close after all and this file's status claims need updating"
        )
    print(
        f"GAP (documented, not closed): the ray's slope (directional derivative) has "
        f"{len(slope)} nonzero monomials -- it is NOT identically zero, so the ray does "
        f"NOT give a whole-line escape at a generic point"
    )

    print("STATUS canonical-presentation method: 9472/9476 (unchanged by this file); exceptions: 4")
    print("STATUS complete stabilizer-aware pair theorem: 9476/9476 (verified separately)")
    print("CAVEAT: this file does NOT close (50,7977) -- see the GAP line above and the .md section 1")
    print("CAVEAT: diagonal two still requires universal common-shear overlap or another global argument")


if __name__ == "__main__":
    main()
