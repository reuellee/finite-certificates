#!/usr/bin/env python3
"""Independent, from-scratch re-verification of the (3,5) upper-bound certificate library.

    python independent_audit.py                 # full library, ~single process
    python independent_audit.py --resume        # resume from checkpoint
    python independent_audit.py --canaries-only # canary battery only
    python independent_audit.py --limit 500     # first 500 records per bundle (timing)

Python standard library ONLY (fractions is not even needed: everything below is
exact integer arithmetic).  No numpy, no scipy, no sympy.  This file imports
nothing from `ai/maxout` -- in particular nothing from `gp_degree3_search.py`,
`coefficientwise_search.py`, `common.py`, `gp_all_d2_sweep.py`,
`k0_cellwide_sweep.py`, `split02_cellwide_sweep.py`, or
`audit_all_certificates.py`.  It reads the serialized certificate artifacts and
re-proves every certificate with a different algorithm.

===============================================================================
WHY THIS FILE EXISTS
===============================================================================

The shipped all-library auditor `stage2c2_gpt/audit_all_certificates.py` imports
`quotient_matrix` and `normal_forms` from the *generator*
`stage2c2_gpt/gp_degree3_search.py`.  The quotient-ring half of every check --
the half that turns a fixed-realization Gordan vector into a *cell-wide* one --
therefore inherits any systematic error in the generator's Groebner-basis
machinery over the signed-D Pluecker ideal.  Its second half (specialization at
the reference matrix U_ints against an independently written row builder) is
sound but, as shown by canary C8 below, provably cannot detect a multiplier that
is a valid Gordan vector at U_ints yet not valid across the cell.

This file re-proves the *cell-wide* property by a route that shares no algebra
with the generator: no Groebner basis, no normal forms, no signed-D quotient
ring, no polynomial reduction of any kind.

===============================================================================
1. WHAT A CERTIFICATE CLAIMS  (the row model -- the theorem's statement)
===============================================================================

Fix five directions u_0..u_4 in R^3 with all ten determinants nonzero.  Write
PAIRS for the ten pairs (i,j), i<j, in lexicographic order and TRIPLES for the
ten triples in lexicographic order.  Put C_ij = u_i x u_j and
D_tij = |det(u_t, u_i, u_j)|.  A "labeled side pattern" sigma is 20 bits, two
per pair class: bit 2c is the sign on the ray +C_ij, bit 2c+1 the sign on -C_ij
(set bit = +1, clear bit = -1).  A "split" s is a vector in {+1,-1}^5.

The cap-attainment system B(sigma, s) has 25 rows and 8 columns
(x = (T_0,T_1,T_2,w_0..w_4)):

    row(class c=(i,j), ray r in {+1,-1}) =
        [ sigma_side * r * C_ij   |   sigma_side * s_t * D_tij   (t=0..4) ]
        with D_tij := 0 for t in {i,j}
    row(weight t) = [ 0,0,0 | e_t ]

(CAPSTONE.md section 1; maxout35note.tex section 2.)  A Gordan certificate is
y >= 0, y != 0 with B^T y = 0; it proves B x > 0 is strictly infeasible, i.e.
that a 44-vertex instance with this (sigma, s) cannot exist.

A certificate is *cell-wide* when the 25 multipliers are polynomials with
nonnegative coefficients in the ten formal variables D = (D_012,...,D_234)
(side multipliers homogeneous of degree d, weight multipliers of degree d+1)
such that B^T y = 0 holds at *every* configuration U' whose chirotope equals the
reference chirotope chi_ref -- not merely at the reference U_ints.  Since every
D_T is strictly positive at every such U', nonnegative coefficients plus a
nonempty support give y >= 0 and y != 0 automatically; the content is B^T y = 0.

===============================================================================
2. THE TEN IDENTITIES  (derived here, not imported)
===============================================================================

Only three of B's eight columns (the T block) involve the cross products C_ij,
which are not polynomials in D.  Dot the 3-vector T-equation with u_t:

    <u_t, C_ij> = <u_t, u_i x u_j> = det(u_t, u_i, u_j)
                = sgn(perm sorting (t,i,j)) * chi_{tij} * D_tij ,

and D_tij vanishes when t is i or j.  Because u_0..u_4 span R^3 whenever some
3x3 determinant is nonzero, the vanishing of all five dotted equations is
EQUIVALENT to the vanishing of the 3-vector T-equation.  So B^T y = 0 becomes
ten polynomial identities in Z[D_012,...,D_234], all homogeneous of degree
e = d+1, indexed by t = 0..4:

    F_T[t]  =  sum over sides (c=(i,j), r), t not in {i,j}, of
               y_side * sigma_side * r * sgn(t,i,j) * chi_{tij} * D_tij
    F_W[t]  =  sum over sides (c=(i,j), r), t not in {i,j}, of
               y_side * sigma_side * s_t * D_tij        +   y_weight[t]

The certificate is cell-wide iff all ten vanish at D = D(U') for every U'
realizing chi_ref.

===============================================================================
3. THE DECISION PROCEDURE  (this is the genuinely independent part)
===============================================================================

Let Phi be the ring homomorphism  Q[D_012,...,D_234] -> Q[x_00,...,x_42]
sending D_T to chi_T * det_T(x), where x is a symbolic 5x3 matrix and det_T is
the 3x3 minor on rows T.  Write G = Phi(F).

  LEMMA (exactness of the test).  F vanishes at D(U') for every configuration
  U' realizing chi_ref  <==>  G is the zero polynomial in the 15 entries of x.

  Proof.  (<=) trivial.  (=>) The set R = {x in R^15 : sign det_T(x) = chi_T for
  all ten T} is defined by ten strict inequalities, hence is open, and it is
  nonempty (U_ints lies in it).  For x in R we have |det_T(x)| = chi_T det_T(x),
  so G(x) = F(D(x)) = 0 on R.  A real polynomial vanishing on a nonempty open
  subset of R^15 is identically zero.  QED

Note this is an *equivalence*: G == 0 is exactly the cell-wide condition.  The
generator's criterion -- membership of F in the ideal generated by the signed-D
three-term Pluecker relations -- is a priori only *sufficient* (the two coincide
because the Pluecker ideal is prime, but this file never needs that theorem).

Deciding "G == 0" exactly and finitely.  Let M_e be the number of monomials of
degree e in ten variables and let K_e = ker(Phi restricted to degree e).  For a
configuration V in Z^{5x3} let ev(V) in Z^{M_e} be the vector of values of all
degree-e monomials at the point D_T = chi_T det_T(V).  Stack N such rows into
E in Z^{N x M_e}.  Then, always, K_e is contained in ker E.  Certify the
converse as follows.

  (a) Verify SYMBOLICALLY, by explicit expansion in Z[x_00..x_42], that each of
      the five signed three-term Pluecker relations R_a (derived here from the
      classical relation, not copied) satisfies Phi(R_a) = 0.  Hence every
      monomial multiple m*R_a with deg m = e-2 lies in K_e.
  (b) Let J be the matrix whose rows are those multiples, and let
      r = rank J, rho = rank E.  Ranks are computed by Gaussian elimination
      modulo a prime p, which yields LOWER bounds on the ranks over Q.
  (c) rank_Q(J) <= dim K_e (by (a)) and rank_Q(E) <= M_e - dim K_e (each row of
      E annihilates K_e).  Therefore

          M_e = rho + r <= rank_Q(E) + rank_Q(J) <= (M_e - dim K_e) + dim K_e
              = M_e,

      so if the computed rho + r equals M_e, every inequality is an equality and
          ker E  =  K_e   exactly.

  (d) The audit then keeps rho rows of E that were independent mod p (hence
      independent over Q, hence spanning the same row space) and tests
      E' F = 0 in EXACT INTEGER arithmetic.  By (c) this is equivalent to
      F in K_e, i.e. to G == 0, i.e. to cell-wideness.

No Groebner basis, no normal form, no standard-monomial/straightening theory, no
Hilbert function is used or assumed anywhere.  The classical Hilbert values
(10, 50, 175, 490 for e = 1,2,3,4) are recomputed by the audit as *predictions
to confirm*, and reported, but the certification above does not use them.

Additionally the audit specializes every certificate at the reference U_ints and
at two FRESH integer realizations of chi_ref found by this file, and checks
y >= 0, y != 0 and B^T y = 0 there against the 25x8 row builder written above.
The fresh-realization layer is redundant given the lemma but is an independent
cross-check of the whole decoding/building pipeline.

===============================================================================
4. WHAT ELSE IS CHECKED
===============================================================================

* Coverage completeness (the shipped auditor does not check this).  The
  combinatorial structure -- 22 chambers, the chamber/side incidence, and the
  33,140 valid labeled side patterns -- is DERIVED HERE from U_ints alone, with
  an exact proof of completeness of the chamber list (each of the 32 candidate
  sign vectors gets either an explicit rational interior point or an explicit
  Gordan vector proving its cone is empty; Gordan's theorem makes these mutually
  exclusive and exhaustive).  For each of the four split representatives the
  audit then verifies that the set of sigmas carrying a verified certificate is
  EXACTLY the set of 33,140 valid sigmas -- no gap, no duplicate.

* Canaries.  Nine deliberate corruptions must be REJECTED, and the report
  records which layer caught each one.  Canary C8 is constructed to pass the
  reference-specialization layer exactly (it is a genuine Gordan vector at
  U_ints) while failing cell-wideness -- a concrete demonstration that the
  shipped auditor's independently-written half cannot close finding 1 on its
  own.  Two machinery controls check the reduction is neither vacuous nor
  over-strict: a known Pluecker multiple must PASS, a pseudorandom vector must
  FAIL.

===============================================================================
5. RESIDUAL TRUST BOUNDARY  (what this file does NOT re-prove)
===============================================================================

1. The 25x8 row model of section 1.  This is the *statement* of the theorem
   being certified (CAPSTONE.md section 1 / maxout35note.tex section 2), not
   generator code; it is re-implemented here from that prose specification.  If
   the row model itself misrepresents the geometry, no auditor of the
   certificate library can detect it.

2. The serialization layout of the sparse certificates: variables are ordered
   side-major (20 sides x monomials of degree d, monomials enumerated as
   `itertools.combinations_with_replacement(range(10), d)` exponent vectors),
   then weight-major (5 rows x monomials of degree d+1).  This is a data format,
   not a mathematical claim, and it is self-validating: canary C7 rotates the
   monomial order by one position and reports the resulting rejection rate.

3. The DEFINITION of a valid labeled side pattern (every chamber must see both
   signs among its incident sides), and the reduction of the theorem to the four
   split representatives.  Both are prose steps of the proof (CAPSTONE.md
   sections 1, 3.2-3.4) checked elsewhere; this file re-derives the resulting
   combinatorial objects but does not re-derive the reduction.

4. The 121 `EXACT_DEGREE_NO_GO` entries in `gp_degree3_results.json.gz` are
   counted but NOT re-verified: their separating functionals are indexed by the
   generator's quotient-matrix row keys, so verifying them would require
   reproducing exactly the construction this file is meant to avoid.  They are
   negative results ("no certificate exists at this degree") and carry no weight
   in the upper bound.

Item 4 of the boundary in earlier drafts -- the reference chirotope chi_ref --
has been retired: this file computes it from U_ints and cross-checks it against
the `chirotope_signs` field shipped in `gp_degree3_results.json.gz`.
"""
from __future__ import annotations

import argparse
import gzip
import hashlib
import itertools
import json
import os
import random
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
MAXOUT = HERE.parent
STAGE = MAXOUT / "stage2c2_gpt"

REPORT_PATH = HERE / "independent_audit_report.json"
PROGRESS_PATH = HERE / "independent_audit_progress.json"

PAIRS = tuple(itertools.combinations(range(5), 2))
TRIPLES = tuple(itertools.combinations(range(5), 3))
TRIPLE_INDEX = {t: i for i, t in enumerate(TRIPLES)}
MASK20 = (1 << 20) - 1

# Primes for the rank computations.  Any prime works for the sandwich argument
# of section 3(b-c); several are listed so a bad reduction can be retried.
RANK_PRIMES = (2147483647, 2147483629, 2147483587)

# Deterministic seeds, recorded in the report.
SEED_EVAL_POINTS = 20260731
SEED_FRESH = 991
SEED_CANARY = 4242


# ---------------------------------------------------------------------------
# exact vector algebra over Z
# ---------------------------------------------------------------------------

def cross(a, b):
    return (a[1] * b[2] - a[2] * b[1],
            a[2] * b[0] - a[0] * b[2],
            a[0] * b[1] - a[1] * b[0])


def dot(a, b):
    return a[0] * b[0] + a[1] * b[1] + a[2] * b[2]


def det3(a, b, c):
    return dot(a, cross(b, c))


def sort_sign(triple):
    """Sign of the permutation that sorts a 3-tuple of distinct integers."""
    a, b, c = triple
    inv = (a > b) + (a > c) + (b > c)
    return -1 if inv % 2 else 1


def monomials(degree):
    """Exponent vectors of every degree-`degree` monomial in ten variables.

    Order: `itertools.combinations_with_replacement(range(10), degree)`.
    This is the serialization convention of the certificate artifacts
    (trust-boundary item 2); canary C7 tests that a wrong order is rejected.
    """
    if degree == 0:
        return ((0,) * 10,)
    out = []
    for factors in itertools.combinations_with_replacement(range(10), degree):
        exponent = [0] * 10
        for f in factors:
            exponent[f] += 1
        out.append(tuple(exponent))
    return tuple(out)


def mono_value(mono, dvals):
    v = 1
    for idx, ex in enumerate(mono):
        if ex:
            v *= dvals[idx] ** ex
    return v


def add_unit(mono, index):
    out = list(mono)
    out[index] += 1
    return tuple(out)


# ---------------------------------------------------------------------------
# tiny exact multivariate polynomial ring over Z, used only for the five
# symbolic Pluecker verifications (15 variables x_{a,c}, a in 0..4, c in 0..2)
# ---------------------------------------------------------------------------

def poly_add(p, q, scale=1):
    for k, v in q.items():
        n = p.get(k, 0) + scale * v
        if n:
            p[k] = n
        elif k in p:
            del p[k]
    return p


def poly_mul(p, q):
    out = {}
    for k1, v1 in p.items():
        for k2, v2 in q.items():
            k = tuple(a + b for a, b in zip(k1, k2))
            n = out.get(k, 0) + v1 * v2
            if n:
                out[k] = n
            elif k in out:
                del out[k]
    return out


def symbolic_det(triple):
    """det of rows `triple` of the symbolic 5x3 matrix, as a poly in 15 vars."""
    a, b, c = triple

    def var(row, col):
        e = [0] * 15
        e[3 * row + col] = 1
        return tuple(e)

    out = {}
    for perm in itertools.permutations(range(3)):
        sgn = sort_sign(perm)
        key = tuple(
            x + y + z for x, y, z in zip(var(a, perm[0]), var(b, perm[1]),
                                         var(c, perm[2]))
        )
        out[key] = out.get(key, 0) + sgn
    return {k: v for k, v in out.items() if v}


# ---------------------------------------------------------------------------
# reference configuration, chirotope, chambers, valid sigmas
# ---------------------------------------------------------------------------

class Reference:
    """Everything derived from the integer configuration U_ints alone."""

    def __init__(self, u_ints):
        self.U = tuple(tuple(int(v) for v in row) for row in u_ints)
        if len(self.U) != 5 or any(len(r) != 3 for r in self.U):
            raise ValueError("U_ints must be a 5x3 integer matrix")
        self.det = {}
        for t in TRIPLES:
            d = det3(self.U[t[0]], self.U[t[1]], self.U[t[2]])
            if d == 0:
                raise ValueError("reference configuration is not uniform")
            self.det[t] = d
        self.chi = tuple(1 if self.det[t] > 0 else -1 for t in TRIPLES)
        self.dabs = tuple(abs(self.det[t]) for t in TRIPLES)
        self.chambers, self.incidence, self.chamber_proofs = self._chambers()
        self.masks = tuple(sum(1 << s for s in inc) for inc in self.incidence)
        self.valid = self._valid_sigmas()

    # -- chambers of the central arrangement {u_i^perp}, with completeness proof
    def _chambers(self):
        rays = {}
        for c, (i, j) in enumerate(PAIRS):
            C = cross(self.U[i], self.U[j])
            rays[2 * c] = C
            rays[2 * c + 1] = tuple(-v for v in C)

        chambers, incidence, proofs = [], [], []
        for eps in itertools.product((-1, 1), repeat=5):
            sides = []
            for c, (i, j) in enumerate(PAIRS):
                for r in (0, 1):
                    side = 2 * c + r
                    v = rays[side]
                    ok = True
                    for t in range(5):
                        if t in (i, j):
                            continue
                        d = dot(self.U[t], v)
                        if d == 0 or (1 if d > 0 else -1) != eps[t]:
                            ok = False
                            break
                    if ok:
                        sides.append(side)
            witness = None
            if sides:
                x = [0, 0, 0]
                for s in sides:
                    v = rays[s]
                    for a in range(3):
                        x[a] += v[a]
                vals = [dot(self.U[t], x) for t in range(5)]
                if all(v != 0 and (1 if v > 0 else -1) == eps[t]
                       for t, v in enumerate(vals)):
                    witness = tuple(x)
            if witness is not None:
                chambers.append(eps)
                incidence.append(tuple(sorted(sides)))
                proofs.append(("REALIZED", list(witness)))
                continue
            gordan = self._gordan_empty(eps)
            if gordan is None:
                raise AssertionError(
                    f"sign vector {eps} decided by neither witness nor Gordan "
                    "vector; chamber enumeration is not proven complete"
                )
            proofs.append(("EMPTY", gordan))
        if len(chambers) != 22:
            raise AssertionError(f"expected 22 chambers, derived {len(chambers)}")
        return tuple(chambers), tuple(incidence), tuple(proofs)

    def _gordan_empty(self, eps):
        """A nonnegative nonzero y with sum y_i eps_i u_i = 0 (Gordan: proves
        {x : eps_i <u_i,x> > 0} is empty).  Support 4 suffices: the u_i are in
        general position, so every extreme ray of {y>=0, sum y_i v_i = 0} has
        support exactly four."""
        v = [tuple(eps[i] * c for c in self.U[i]) for i in range(5)]
        for sub in itertools.combinations(range(5), 4):
            a, b, c, d = (v[k] for k in sub)
            y = (det3(b, c, d), -det3(a, c, d), det3(a, b, d), -det3(a, b, c))
            if all(t > 0 for t in y):
                coeff = y
            elif all(t < 0 for t in y):
                coeff = tuple(-t for t in y)
            else:
                continue
            total = [0, 0, 0]
            for k, idx in enumerate(sub):
                for m in range(3):
                    total[m] += coeff[k] * v[idx][m]
            if total != [0, 0, 0]:
                raise AssertionError("Cramer null-combination identity failed")
            out = [0] * 5
            for k, idx in enumerate(sub):
                out[idx] = coeff[k]
            return out
        return None

    def _valid_sigmas(self):
        """A sigma is valid iff every chamber sees both signs among the sides
        incident to it (CAPSTONE.md section 1)."""
        masks = self.masks
        out = []
        for bits in range(1 << 20):
            for m in masks:
                v = bits & m
                if v == 0 or v == m:
                    break
            else:
                out.append(bits)
        return frozenset(out)

    # -- the 25 x 8 row model (section 1 of the docstring)
    def rows(self, bits, split, config=None):
        U = self.U if config is None else config
        dabs = {}
        for t in TRIPLES:
            dabs[t] = abs(det3(U[t[0]], U[t[1]], U[t[2]]))
        out = []
        for c, (i, j) in enumerate(PAIRS):
            C = cross(U[i], U[j])
            for ray, side in ((1, 2 * c), (-1, 2 * c + 1)):
                sg = 1 if (bits >> side) & 1 else -1
                weights = [0 if t in (i, j)
                           else sg * split[t] * dabs[tuple(sorted((t, i, j)))]
                           for t in range(5)]
                out.append(tuple([sg * ray * C[a] for a in range(3)] + weights))
        for t in range(5):
            out.append(tuple([0, 0, 0] + [1 if q == t else 0 for q in range(5)]))
        return tuple(out)


# ---------------------------------------------------------------------------
# Pluecker relations, derived here from the classical three-term relation
# ---------------------------------------------------------------------------

def plucker_relations(chi):
    """The five signed-D three-term Pluecker relations, as dicts
    {degree-2 exponent vector: integer coefficient}.

    Classical relation, for a fixed index a and b<c<d<e the others:
        [abc][ade] - [abd][ace] + [abe][acd] = 0 ,
    where [xyz] = det(u_x,u_y,u_z).  Substituting
    [xyz] = sgn(sort) * chi_sorted * D_sorted turns it into a relation in D.
    """
    def bracket(idx):
        tri = tuple(sorted(idx))
        return sort_sign(idx) * chi[TRIPLE_INDEX[tri]], TRIPLE_INDEX[tri]

    relations = []
    for a in range(5):
        b, c, d, e = [i for i in range(5) if i != a]
        rel = {}
        for sign, (p, q) in ((1, ((a, b, c), (a, d, e))),
                             (-1, ((a, b, d), (a, c, e))),
                             (1, ((a, b, e), (a, c, d)))):
            s1, i1 = bracket(p)
            s2, i2 = bracket(q)
            mono = [0] * 10
            mono[i1] += 1
            mono[i2] += 1
            mono = tuple(mono)
            v = rel.get(mono, 0) + sign * s1 * s2
            if v:
                rel[mono] = v
            elif mono in rel:
                del rel[mono]
        relations.append(rel)
    return tuple(relations)


def verify_plucker_symbolically(relations, chi):
    """Expand Phi(R_a) in Z[x_00..x_42] and require the zero polynomial."""
    detpoly = []
    for k, t in enumerate(TRIPLES):
        p = symbolic_det(t)
        if chi[k] < 0:
            p = {key: -v for key, v in p.items()}
        detpoly.append(p)
    for rel in relations:
        total = {}
        for mono, coeff in rel.items():
            term = {(0,) * 15: coeff}
            for idx, ex in enumerate(mono):
                for _ in range(ex):
                    term = poly_mul(term, detpoly[idx])
            poly_add(total, term)
        if total:
            return False
    return True


# ---------------------------------------------------------------------------
# rank certification and the cell-wide membership test
# ---------------------------------------------------------------------------

def rank_mod_p(rows, ncols, p, target=None):
    """Gaussian elimination mod p.  Returns (rank, indices of rows that raised
    the rank).  Pivot rows are stored keyed by their pivot column and each has
    zeros strictly to the left of its pivot, so a single increasing scan fully
    reduces any vector -- no back-substitution needed."""
    pivot = {}
    chosen = []
    for ri, row in enumerate(rows):
        cur = [v % p for v in row]
        col = 0
        newpiv = None
        while col < ncols:
            v = cur[col]
            if v:
                pr = pivot.get(col)
                if pr is None:
                    newpiv = col
                    break
                f = v
                cur[col:] = [(a - f * b) % p for a, b in zip(cur[col:], pr[col:])]
            col += 1
        if newpiv is None:
            continue
        inv = pow(cur[newpiv], p - 2, p)
        if inv != 1:
            cur[newpiv:] = [(v * inv) % p for v in cur[newpiv:]]
        pivot[newpiv] = cur
        chosen.append(ri)
        if target is not None and len(pivot) >= target:
            break
    return len(pivot), chosen


def hilbert_g35(e):
    """Weyl dimension of the GL_5 irrep (e,e,e,0,0) = classical value of
    dim (C[p]/I_Pluecker)_e for G(3,5).  Used ONLY as a prediction to confirm."""
    lam = (e, e, e, 0, 0)
    num, den = 1, 1
    for i in range(5):
        for j in range(i + 1, 5):
            num *= lam[i] - lam[j] + (j - i)
            den *= j - i
    assert num % den == 0
    return num // den


class DegreeContext:
    """Certified machinery for one homogeneous degree e = d+1."""

    def __init__(self, e, reference, relations, log=print):
        self.e = e
        self.monos = monomials(e)
        self.index = {m: i for i, m in enumerate(self.monos)}
        self.M = len(self.monos)
        self.reference = reference

        # (b) rank of the span of monomial multiples of the Pluecker relations
        jrows = []
        for m in monomials(e - 2) if e >= 2 else ():
            for rel in relations:
                row = [0] * self.M
                for mono, coeff in rel.items():
                    prod = tuple(a + b for a, b in zip(mono, m))
                    row[self.index[prod]] += coeff
                jrows.append(row)
        self.n_plucker_rows = len(jrows)

        # (d) evaluation rows at pseudorandom integer configurations
        rng = random.Random(SEED_EVAL_POINTS + 1000 * e)
        chi = reference.chi
        self.points = []
        erows = []
        attempts = 0
        while len(erows) < 4 * self.M + 40 and attempts < 200000:
            attempts += 1
            V = tuple(tuple(rng.randint(-4, 4) for _ in range(3))
                      for _ in range(5))
            dvals = []
            ok = True
            for k, t in enumerate(TRIPLES):
                d = det3(V[t[0]], V[t[1]], V[t[2]])
                if d == 0:
                    ok = False
                    break
                dvals.append(chi[k] * d)
            if not ok:
                continue
            self.points.append(V)
            erows.append([mono_value(m, dvals) for m in self.monos])

        self.certified = False
        for p in RANK_PRIMES:
            r, _ = rank_mod_p(jrows, self.M, p) if jrows else (0, [])
            target = self.M - r
            rho, chosen = rank_mod_p(erows, self.M, p, target=target)
            if rho + r == self.M:
                self.prime = p
                self.rank_plucker = r
                self.rank_eval = rho
                self.rows = [erows[i] for i in chosen]
                self.point_indices = chosen
                self.certified = True
                break
        if not self.certified:
            raise AssertionError(
                f"degree {e}: rank sandwich did not close "
                f"(M={self.M}); refusing to certify"
            )

        # column-major copy for the fast sparse test
        self.cols = [tuple(row[j] for row in self.rows) for j in range(self.M)]
        self.hilbert_prediction = hilbert_g35(e)
        log(f"  degree e={e}: M={self.M} rank(J)={self.rank_plucker} "
            f"rank(E)={self.rank_eval} sandwich OK "
            f"(classical Hilbert value {self.hilbert_prediction}: "
            f"{'match' if self.rank_eval == self.hilbert_prediction else 'MISMATCH'})")

    def in_kernel(self, poly):
        """True iff `poly` (dict monomial -> int) lies in ker Phi_e, i.e. iff
        its image under Phi is the zero polynomial in the 15 configuration
        entries.  Exact integer arithmetic."""
        terms = [(self.index[m], c) for m, c in poly.items() if c]
        if not terms:
            return True
        if len(terms) == 1:
            return False          # a single nonzero monomial never vanishes
        cols = self.cols
        n = len(self.rows)
        acc = [0] * n
        for j, c in terms:
            col = cols[j]
            acc = [a + c * b for a, b in zip(acc, col)]
        return not any(acc)


# ---------------------------------------------------------------------------
# certificate decoding, identity construction, verification layers
# ---------------------------------------------------------------------------

class Decoder:
    def __init__(self, side_degree):
        self.d = side_degree
        self.side_monos = monomials(side_degree)
        self.weight_monos = monomials(side_degree + 1)
        self.ns = len(self.side_monos)
        self.nw = len(self.weight_monos)
        self.n_vars = 20 * self.ns + 5 * self.nw

    def decode(self, cert):
        """[(variable index, integer coefficient)] -> (side terms, weight terms).

        side term = (side index 0..19, exponent vector of degree d, coeff)
        weight term = (t 0..4, exponent vector of degree d+1, coeff)
        Raises ValueError on any malformed entry.
        """
        seen = set()
        sides, weights = [], []
        for entry in cert:
            if len(entry) != 2:
                raise ValueError("certificate entry is not a pair")
            vi, c = int(entry[0]), entry[1]
            if not isinstance(c, int) or isinstance(c, bool):
                raise ValueError("non-integer coefficient")
            if vi < 0 or vi >= self.n_vars:
                raise ValueError("variable index out of range")
            if vi in seen:
                raise ValueError("duplicate variable index")
            seen.add(vi)
            if vi < 20 * self.ns:
                side, mi = divmod(vi, self.ns)
                sides.append((side, self.side_monos[mi], c))
            else:
                w = vi - 20 * self.ns
                t, mi = divmod(w, self.nw)
                weights.append((t, self.weight_monos[mi], c))
        return sides, weights


def build_identities(bits, split, sides, weights, chi):
    """The ten polynomials F_T[0..4], F_W[0..4] of docstring section 2.

    Returns (list of ten dicts, number of terms emitted).  The term count is a
    structural invariant: 6 per side entry, 1 per weight entry.
    """
    T = [dict() for _ in range(5)]
    W = [dict() for _ in range(5)]
    emitted = 0
    for side, mono, c in sides:
        cls = side >> 1
        i, j = PAIRS[cls]
        sg = 1 if (bits >> side) & 1 else -1
        ray = 1 if side % 2 == 0 else -1
        for t in range(5):
            if t == i or t == j:
                continue
            tri = (t, i, j) if t < i else ((i, t, j) if t < j else (i, j, t))
            k = TRIPLE_INDEX[tri]
            m2 = add_unit(mono, k)
            ts = sg * ray * sort_sign((t, i, j)) * chi[k] * c
            v = T[t].get(m2, 0) + ts
            if v:
                T[t][m2] = v
            elif m2 in T[t]:
                del T[t][m2]
            ws = sg * split[t] * c
            v = W[t].get(m2, 0) + ws
            if v:
                W[t][m2] = v
            elif m2 in W[t]:
                del W[t][m2]
            emitted += 2
    for t, mono, c in weights:
        v = W[t].get(mono, 0) + c
        if v:
            W[t][mono] = v
        elif mono in W[t]:
            del W[t][mono]
        emitted += 1
    return T + W, emitted


class Auditor:
    LAYERS = ("DECODE", "COEFF", "KERNEL", "SPEC_REF", "SPEC_FRESH")

    def __init__(self, reference, log=print):
        self.ref = reference
        self.log = log
        self.relations = plucker_relations(reference.chi)
        if not verify_plucker_symbolically(self.relations, reference.chi):
            raise AssertionError(
                "Phi(R_a) != 0: the signed-D Pluecker relations do not vanish "
                "on the configuration space -- refusing to proceed"
            )
        self.contexts = {}
        self.decoders = {}
        self.realizations = [("U_ints", reference.U)] + [
            (f"fresh{i}", V) for i, V in enumerate(self._fresh(2))
        ]
        self.dvals = []
        for name, V in self.realizations:
            dv = tuple(abs(det3(V[t[0]], V[t[1]], V[t[2]])) for t in TRIPLES)
            self.dvals.append(dv)
        self.rowcache = {}
        self.monocache = [dict() for _ in self.realizations]
        self._check_sigma_factorization()
        # {"family"|"explicit": {number of non-vanishing written identities:
        #  how many certificates}}.  A count of 0 means every identity was
        #  already the zero polynomial as written (this is exactly what the
        #  closed-form family certificates do -- they need no Pluecker
        #  reduction at all); a count > 0 means the certificate's identities
        #  are genuinely nonzero polynomials that vanish only on the Pluecker
        #  variety, i.e. the new algebra actually did work.
        self.identity_stats = {"family": {}, "explicit": {}}

    def _check_sigma_factorization(self):
        """Runtime proof of the caching identity used by `_base`: for every
        sigma, split, realization and side,
            Reference.rows(sigma,...)[side] == sigma_side * rows(all-plus,...).
        Checked, not asserted in prose."""
        rng = random.Random(12345)
        for ri, (_, V) in enumerate(self.realizations):
            for _ in range(8):
                bits = rng.randrange(1 << 20)
                split = tuple(rng.choice((-1, 1)) for _ in range(5))
                a = self.ref.rows(bits, split, V)
                b = self.ref.rows(MASK20, split, V)
                for side in range(20):
                    sg = 1 if (bits >> side) & 1 else -1
                    if a[side] != tuple(sg * v for v in b[side]):
                        raise AssertionError("sigma does not factor out of the "
                                             "row model")
                if a[20:] != b[20:]:
                    raise AssertionError("weight rows depend on sigma")

    def _fresh(self, n):
        """Fresh integer realizations of chi_ref, found by rejection sampling."""
        rng = random.Random(SEED_FRESH)
        chi = self.ref.chi
        out = []
        tries = 0
        while len(out) < n and tries < 4000000:
            tries += 1
            V = tuple(tuple(rng.randint(-9, 9) for _ in range(3))
                      for _ in range(5))
            ok = True
            for k, t in enumerate(TRIPLES):
                d = det3(V[t[0]], V[t[1]], V[t[2]])
                if d == 0 or (1 if d > 0 else -1) != chi[k]:
                    ok = False
                    break
            if ok and V not in out and V != self.ref.U:
                out.append(V)
        if len(out) < n:
            raise AssertionError("could not find fresh realizations of chi_ref")
        return out

    def context(self, e):
        ctx = self.contexts.get(e)
        if ctx is None:
            ctx = DegreeContext(e, self.ref, self.relations, log=self.log)
            self.contexts[e] = ctx
        return ctx

    def decoder(self, d):
        dec = self.decoders.get(d)
        if dec is None:
            dec = Decoder(d)
            self.decoders[d] = dec
        return dec

    def _base(self, split, ri):
        """The 25x8 row matrix at sigma = all-plus, from the authoritative row
        builder.  Every row of B(sigma, s) is sigma_side times the
        corresponding all-plus row -- the sigma dependence of the model is
        exactly one global sign per side row -- so caching this by (split,
        realization) costs 12 matrices instead of one per certificate while
        still using `Reference.rows` verbatim."""
        key = (split, ri)
        r = self.rowcache.get(key)
        if r is None:
            r = self.ref.rows(MASK20, split, self.realizations[ri][1])
            self.rowcache[key] = r
        return r

    def _mval(self, mono, ri):
        cache = self.monocache[ri]
        v = cache.get(mono)
        if v is None:
            v = mono_value(mono, self.dvals[ri])
            cache[mono] = v
        return v

    def verify(self, bits, split, cert, side_degree, monomial_shift=0):
        """Run every layer.  Returns (set of failing layer names, info dict)."""
        fails = set()
        info = {}
        try:
            dec = self.decoder(side_degree)
            sides, weights = dec.decode(cert)
            if monomial_shift:
                ns, nw = dec.ns, dec.nw
                sm, wm = dec.side_monos, dec.weight_monos
                sides = [(s, sm[(sm.index(m) + monomial_shift) % ns], c)
                         for s, m, c in sides]
                weights = [(t, wm[(wm.index(m) + monomial_shift) % nw], c)
                           for t, m, c in weights]
        except ValueError as exc:
            return {"DECODE"}, {"decode_error": str(exc)}

        coeffs = [c for _, _, c in sides] + [c for _, _, c in weights]
        if not coeffs or any(c < 0 for c in coeffs) or not any(c > 0
                                                              for c in coeffs):
            fails.add("COEFF")

        e = side_degree + 1
        ctx = self.context(e)
        polys, emitted = build_identities(bits, split, sides, weights,
                                          self.ref.chi)
        if emitted != 6 * len(sides) + len(weights):
            fails.add("KERNEL")
            info["structural"] = "identity term count invariant violated"
        nontrivial = sum(1 for p in polys if p)
        info["nontrivial_identities"] = nontrivial
        info["max_identity_terms"] = max((len(p) for p in polys), default=0)
        for p in polys:
            if not ctx.in_kernel(p):
                fails.add("KERNEL")
                break

        for ri in range(len(self.realizations)):
            ys, yw = {}, {}
            for side, mono, c in sides:
                ys[side] = ys.get(side, 0) + c * self._mval(mono, ri)
            for t, mono, c in weights:
                yw[t] = yw.get(t, 0) + c * self._mval(mono, ri)
            layer = "SPEC_REF" if ri == 0 else "SPEC_FRESH"
            vals = list(ys.values()) + list(yw.values())
            if any(v < 0 for v in vals) or not any(v > 0 for v in vals):
                fails.add(layer)
                continue
            base = self._base(split, ri)
            total = [0] * 8
            for side, val in ys.items():
                if not val:
                    continue
                v = val if (bits >> side) & 1 else -val
                row = base[side]
                for col in range(8):
                    e = row[col]
                    if e:
                        total[col] += v * e
            for t, val in yw.items():
                row = base[20 + t]
                for col in range(8):
                    e = row[col]
                    if e:
                        total[col] += val * e
            if any(total):
                fails.add(layer)
        return fails, info


# ---------------------------------------------------------------------------
# the closed-form single-class family
# ---------------------------------------------------------------------------

def family_class(bits, split):
    """Index of a pair class witnessing the single-class criterion, or None.

    Criterion (CAPSTONE.md section 2): a class (i,j) whose two side signs agree
    (common value q) with q * s_t = -1 for every t outside {i,j}.
    """
    for c, (i, j) in enumerate(PAIRS):
        sp = 1 if (bits >> (2 * c)) & 1 else -1
        sm = 1 if (bits >> (2 * c + 1)) & 1 else -1
        if sp != sm:
            continue
        if all(sp * split[t] == -1 for t in range(5) if t != i and t != j):
            return c
    return None


def family_certificate(cls):
    """The closed-form certificate as a sparse vector in the SAME serialization
    the shards use, at side degree 0:  y_{ij,+} = y_{ij,-} = 1 and
    y_{w,t} = 2 * D_tij for t outside {i,j}.  Verified by the same pipeline."""
    i, j = PAIRS[cls]
    out = [[2 * cls, 1], [2 * cls + 1, 1]]
    for t in range(5):
        if t == i or t == j:
            continue
        k = TRIPLE_INDEX[tuple(sorted((t, i, j)))]
        out.append([20 + 10 * t + k, 2])
    return out


# ---------------------------------------------------------------------------
# bundle plumbing
# ---------------------------------------------------------------------------

def load_gz(path):
    with gzip.open(path, "rt", encoding="utf-8") as h:
        return json.load(h)


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


SPLIT_NAMES = {
    (-1, -1, -1, -1, -1): "empty",
    (1, -1, -1, -1, -1): "{0}",
    (1, 1, -1, -1, -1): "{0,1}",
    (1, -1, 1, -1, -1): "{0,2}",
}


def as_split(value):
    if isinstance(value, str):
        value = json.loads(value)
    return tuple(int(v) for v in value)


# ---------------------------------------------------------------------------
# canaries
# ---------------------------------------------------------------------------

def run_canaries(auditor, samples, log=print):
    """`samples` is a list of (tag, bits, split, cert, side_degree) known-good
    certificates, one or more per bundle.  Every mutation must be REJECTED."""
    rng = random.Random(SEED_CANARY)
    results = []

    def record(name, tag, fails, expect_reject=True, note=""):
        rejected = bool(fails)
        results.append({
            "canary": name, "sample": tag,
            "rejected": rejected,
            "caught_by": sorted(fails),
            "expected": "REJECT" if expect_reject else "ACCEPT",
            "ok": rejected == expect_reject,
            "note": note,
        })

    # 0. the unmutated samples must be ACCEPTED
    for tag, bits, split, cert, d in samples:
        fails, _ = auditor.verify(bits, split, cert, d)
        record("C0_unmutated_control", tag, fails, expect_reject=False)

    for tag, bits, split, cert, d in samples:
        # 1. corrupt a coefficient
        k = rng.randrange(len(cert))
        m = [list(x) for x in cert]
        m[k][1] += 1
        fails, _ = auditor.verify(bits, split, m, d)
        record("C1_corrupt_coefficient", tag, fails)

        # 2. drop a term
        k = rng.randrange(len(cert))
        m = [list(x) for x in cert if x[0] != cert[k][0]]
        fails, _ = auditor.verify(bits, split, m, d)
        record("C2_drop_term", tag, fails)

        # 3. permute a monomial (same row, different monomial slot)
        dec = auditor.decoder(d)
        m = [list(x) for x in cert]
        for idx, (vi, c) in enumerate(cert):
            if vi < 20 * dec.ns and dec.ns > 1:
                side, mi = divmod(vi, dec.ns)
                m[idx][0] = side * dec.ns + (mi + 1) % dec.ns
                break
            if vi >= 20 * dec.ns and dec.nw > 1:
                w = vi - 20 * dec.ns
                t, mi = divmod(w, dec.nw)
                m[idx][0] = 20 * dec.ns + t * dec.nw + (mi + 1) % dec.nw
                break
        fails, _ = auditor.verify(bits, split, m, d)
        record("C3_permute_monomial", tag, fails)

        # 4. negate a sign
        k = rng.randrange(len(cert))
        m = [list(x) for x in cert]
        m[k][1] = -m[k][1]
        fails, _ = auditor.verify(bits, split, m, d)
        record("C4_negate_coefficient", tag, fails)

        # 5. wrong system: flip the sigma bit of a side the certificate USES.
        #    Provably fatal: if side l = (class (i,j), ray) carries multiplier
        #    y_l != 0, flipping sigma_l turns F_W[t] (t outside {i,j}) from 0
        #    into -2*y_l*sigma_l*s_t*D_tij, a nonzero polynomial all of whose
        #    coefficients have one sign; such a polynomial is strictly nonzero
        #    at every realization (all D_T > 0), so it is not in ker Phi.
        #    (Flipping the sign of an UNUSED side is not an error at all: the
        #    certificate genuinely certifies that system too, which is why this
        #    canary must be targeted.)
        dec = auditor.decoder(d)
        used_sides = sorted({vi // dec.ns for vi, _ in cert
                             if vi < 20 * dec.ns})
        if used_sides:
            side = used_sides[rng.randrange(len(used_sides))]
            fails, _ = auditor.verify(bits ^ (1 << side), split, cert, d)
            record("C5_flip_sigma_of_used_side", tag, fails)

        # 6. wrong split, targeted at a weight row the certificate USES.
        #    Provably fatal: flipping s_t leaves every identity but F_W[t]
        #    alone and turns F_W[t] from 0 into 2*y_{w,t}, which is nonzero
        #    with nonnegative coefficients whenever the certificate has a
        #    weight multiplier on row t.
        used_w = sorted({(vi - 20 * dec.ns) // dec.nw for vi, _ in cert
                         if vi >= 20 * dec.ns})
        if used_w:
            t = used_w[rng.randrange(len(used_w))]
            bad = tuple(-v if k == t else v for k, v in enumerate(split))
            fails, _ = auditor.verify(bits, bad, cert, d)
            record("C6_flip_split_of_used_weight_row", tag, fails)

    # 7. decode canary: rotate the monomial order by one position
    shifted = 0
    for tag, bits, split, cert, d in samples:
        fails, _ = auditor.verify(bits, split, cert, d, monomial_shift=1)
        shifted += 1 if fails else 0
    results.append({
        "canary": "C7_rotate_monomial_order", "sample": "all",
        "rejected": shifted == len(samples),
        "caught_by": ["KERNEL/SPEC (decode convention)"],
        "expected": "REJECT",
        "ok": shifted == len(samples),
        "note": f"{shifted}/{len(samples)} rejected when the monomial "
                f"enumeration order is rotated by one",
    })

    # 8. THE decisive canary: a mutation that is a genuine Gordan vector at
    #    U_ints (so the shipped auditor's independent half accepts it) but is
    #    not cell-wide.  Construction: scale the whole certificate by
    #    B = m'(D_ref) and move one side term from monomial m to a different
    #    monomial m' with coefficient c*m(D_ref); the specialized row value is
    #    unchanged, so B^T y = 0 still holds exactly at U_ints.
    built = 0
    for tag, bits, split, cert, d in samples:
        dec = auditor.decoder(d)
        if dec.ns < 2:
            continue
        target = None
        for idx, (vi, c) in enumerate(cert):
            if vi < 20 * dec.ns:
                target = (idx, vi, c)
                break
        if target is None:
            continue
        idx, vi, c = target
        side, mi = divmod(vi, dec.ns)
        used = {v for v, _ in cert}
        made = None
        for step in range(1, dec.ns):
            mj = (mi + step) % dec.ns
            if side * dec.ns + mj in used:
                continue
            A = auditor._mval(dec.side_monos[mi], 0)
            Bv = auditor._mval(dec.side_monos[mj], 0)
            mut = [[v, x * Bv] for v, x in cert]
            del mut[idx]
            mut.append([side * dec.ns + mj, c * A])
            fails, _ = auditor.verify(bits, split, mut, d)
            made = fails
            if "KERNEL" in fails and "SPEC_REF" not in fails:
                break
        if made is None:
            continue
        built += 1
        record("C8_gordan_at_Uref_but_not_cellwide", tag, made,
               note="passes COEFF and SPEC_REF (the only independently written "
                    "layer of the shipped auditor) by construction; must be "
                    "caught by KERNEL")
    if built == 0:
        results.append({"canary": "C8_gordan_at_Uref_but_not_cellwide",
                        "sample": "-", "rejected": False, "caught_by": [],
                        "expected": "REJECT", "ok": False,
                        "note": "could not construct the canary"})

    # 9. transplant a good certificate onto the strictly-feasible system
    #    (sigma_bits = 0, split = {0}), which provably admits no Gordan vector.
    for tag, bits, split, cert, d in samples[:4]:
        fails, _ = auditor.verify(0, (1, -1, -1, -1, -1), cert, d)
        record("C9_transplant_onto_infeasible_system", tag, fails)

    # machinery controls
    controls = []
    for e, ctx in sorted(auditor.contexts.items()):
        if e >= 2:
            m0 = monomials(e - 2)[0]
            rel = auditor.relations[0]
            poly = {}
            for mono, coeff in rel.items():
                poly[tuple(a + b for a, b in zip(mono, m0))] = coeff
            ok = ctx.in_kernel(poly)
            controls.append({"control": f"plucker_multiple_in_kernel_e{e}",
                             "expected": "PASS",
                             "result": "PASS" if ok else "FAIL", "ok": ok})
        rnd = random.Random(SEED_CANARY + e)
        poly = {}
        for _ in range(6):
            poly[ctx.monos[rnd.randrange(ctx.M)]] = rnd.randrange(1, 20)
        ok = not ctx.in_kernel(poly)
        controls.append({"control": f"random_vector_not_in_kernel_e{e}",
                         "expected": "FAIL",
                         "result": "FAIL" if ok else "PASS", "ok": ok})
        controls.append({
            "control": f"rank_sandwich_e{e}",
            "expected": f"rank(E)+rank(J)=={ctx.M}",
            "result": f"{ctx.rank_eval}+{ctx.rank_plucker}=="
                      f"{ctx.rank_eval + ctx.rank_plucker}",
            "ok": ctx.rank_eval + ctx.rank_plucker == ctx.M,
            "classical_hilbert_value": ctx.hilbert_prediction,
            "matches_classical": ctx.rank_eval == ctx.hilbert_prediction,
        })
    return results, controls


# ---------------------------------------------------------------------------
# main audit
# ---------------------------------------------------------------------------

BUNDLES = [
    ("sweep0", STAGE / "gp_all_d2_shard_00_of_04.json.gz"),
    ("sweep1", STAGE / "gp_all_d2_shard_01_of_04.json.gz"),
    ("sweep2", STAGE / "gp_all_d2_shard_02_of_04.json.gz"),
    ("sweep3", STAGE / "gp_all_d2_shard_03_of_04.json.gz"),
    ("k0", STAGE / "k0_cellwide_shard_00_of_01.json.gz"),
    ("split02_0", HERE / "split02_cellwide_shard_00_of_04.json.gz"),
    ("split02_1", HERE / "split02_cellwide_shard_01_of_04.json.gz"),
    ("split02_2", HERE / "split02_cellwide_shard_02_of_04.json.gz"),
    ("split02_3", HERE / "split02_cellwide_shard_03_of_04.json.gz"),
    ("gp_targets", STAGE / "gp_degree3_results.json.gz"),
    ("family_k12", None),
]


def atomic_write_json(path, payload):
    tmp = Path(str(path) + ".tmp")
    tmp.write_text(json.dumps(payload, indent=1, sort_keys=True),
                   encoding="utf-8")
    os.replace(tmp, path)


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--resume", action="store_true")
    ap.add_argument("--canaries-only", action="store_true")
    ap.add_argument("--limit", type=int, default=None,
                    help="audit at most N records per bundle (timing runs)")
    ap.add_argument("--report", default=str(REPORT_PATH))
    ap.add_argument("--progress", default=str(PROGRESS_PATH))
    ap.add_argument("--checkpoint-every", type=int, default=5000)
    args = ap.parse_args()

    t0 = time.time()
    log = lambda *a, **k: print(*a, flush=True, **k)
    log("independent_audit.py -- stdlib-only re-verification of the "
        "(3,5) upper-bound certificate library")

    inputs = {}
    for name, path in BUNDLES:
        if path is None:
            continue
        if not path.exists():
            raise SystemExit(f"missing artifact: {path}")
        inputs[str(path.relative_to(MAXOUT.parent.parent))] = {
            "sha256": sha256(path), "bytes": path.stat().st_size}

    # U_ints comes from the artifacts themselves; all bundles must agree.
    u_seen = None
    for name, path in BUNDLES:
        if path is None:
            continue
        head = load_gz(path)
        u = tuple(tuple(int(v) for v in row) for row in head["U_ints"])
        if u_seen is None:
            u_seen = u
        elif u != u_seen:
            raise SystemExit(f"{name}: U_ints disagrees with earlier bundles")
        del head

    log("deriving reference structure from U_ints ...")
    ref = Reference(u_seen)
    log(f"  chirotope signs {list(ref.chi)}")
    log(f"  {len(ref.chambers)} chambers (completeness proven), "
        f"{len(ref.valid)} valid labeled side patterns")

    gp_head = load_gz(STAGE / "gp_degree3_results.json.gz")
    chi_shipped = tuple(int(v) for v in gp_head["chirotope_signs"])
    chi_match = chi_shipped == ref.chi
    log(f"  chirotope cross-check against gp_degree3_results.json.gz: "
        f"{'MATCH' if chi_match else 'MISMATCH'}")

    # optional read-only cross-check of the derived combinatorics
    xcheck = {"available": False}
    refstruct = MAXOUT / "stage2b_gpt" / "reference_structure.json"
    if refstruct.exists():
        rs = json.loads(refstruct.read_text(encoding="utf-8"))
        theirs = sorted(
            (tuple(int(v) for v in c), tuple(sorted(int(s) for s in inc)))
            for c, inc in zip(rs["chambers"], rs["chamber_side_incidence"]))
        mine = sorted(zip(ref.chambers, ref.incidence))
        vb = set()
        for r in rs["global_flip_representatives"]:
            vb.add(int(r))
            vb.add(int(r) ^ MASK20)
        xcheck = {"available": True,
                  "chambers_and_incidence_identical": theirs == mine,
                  "valid_sigma_set_identical": vb == set(ref.valid),
                  "note": "read-only cross-check; the audit does not depend "
                          "on this file"}
        log(f"  cross-check vs stage2b_gpt/reference_structure.json: "
            f"chambers {'OK' if theirs == mine else 'MISMATCH'}, "
            f"valid sigmas {'OK' if vb == set(ref.valid) else 'MISMATCH'}")

    log("verifying the five signed-D Pluecker relations symbolically ...")
    auditor = Auditor(ref, log=log)
    log("  Phi(R_a) = 0 for a = 0..4  (expansion in Z[x_00..x_42])")
    log(f"  fresh realizations of chi_ref: "
        f"{[list(map(list, V)) for _, V in auditor.realizations[1:]]}")

    counts = {}
    failures = []
    coverage = {}          # split name -> {"family": set, "explicit": set}

    def cover(split, bits, kind):
        name = SPLIT_NAMES.get(tuple(split), str(tuple(split)))
        entry = coverage.setdefault(name, {"family": set(), "explicit": set(),
                                           "duplicates": 0})
        if bits in entry["family"] or bits in entry["explicit"]:
            entry["duplicates"] += 1
        entry[kind].add(bits)

    def note(tag, status, **extra):
        key = f"{tag}:{status}"
        counts[key] = counts.get(key, 0) + 1
        if status != "OK" and len(failures) < 200:
            entry = {"bundle": tag, "status": status}
            entry.update(extra)
            failures.append(entry)

    state = {"completed": [], "counts": {}, "coverage": {}}
    if args.resume and Path(args.progress).exists():
        state = json.loads(Path(args.progress).read_text(encoding="utf-8"))
        counts.update(state.get("counts", {}))
        for name, entry in state.get("coverage", {}).items():
            coverage[name] = {"family": set(entry["family"]),
                              "explicit": set(entry["explicit"]),
                              "duplicates": entry.get("duplicates", 0)}
        log(f"resumed: {len(state['completed'])} bundles already complete")

    processed = [0]

    def maybe_checkpoint(force=False):
        processed[0] += 1
        if not force and processed[0] % args.checkpoint_every:
            return
        atomic_write_json(args.progress, {
            "completed": state["completed"],
            "counts": counts,
            "coverage": {k: {"family": sorted(v["family"]),
                             "explicit": sorted(v["explicit"]),
                             "duplicates": v["duplicates"]}
                         for k, v in coverage.items()},
            "elapsed": time.time() - t0,
        })

    def audit_record(tag, bits, split, cert, side_degree, kind):
        fails, info = auditor.verify(bits, split, cert, side_degree)
        hist = auditor.identity_stats[kind]
        n = info.get("nontrivial_identities", -1)
        hist[n] = hist.get(n, 0) + 1
        if fails:
            note(tag, "|".join(sorted(fails)), sigma_bits=bits,
                 split=list(split), side_degree=side_degree, detail=info)
        else:
            note(tag, "OK")
            cover(split, bits, kind)
        maybe_checkpoint()

    samples = []

    if not args.canaries_only:
        for tag, path in BUNDLES:
            if tag in state["completed"]:
                continue
            log(f"[{time.time()-t0:7.1f}s] bundle {tag} ...")

            if tag == "family_k12":
                n = 0
                for bits in sorted(ref.valid):
                    for k in (1, 2):
                        split = tuple(1 if t < k else -1 for t in range(5))
                        cls = family_class(bits, split)
                        if cls is None:
                            continue
                        cert = family_certificate(cls)
                        if len(samples) < 24 and n == 0:
                            samples.append((f"{tag}:k{k}", bits, split,
                                            cert, 0))
                        audit_record(f"famk{k}", bits, split, cert, 0,
                                     "family")
                        n += 1
                        if args.limit and n >= args.limit:
                            break
                    if args.limit and n >= args.limit:
                        break
                state["completed"].append(tag)
                maybe_checkpoint(force=True)
                continue

            data = load_gz(path)

            if tag == "gp_targets":
                n = 0
                for rec in data["results"]:
                    outcome = rec["outcome"]
                    status = outcome["status"]
                    if status != "EXACT_CELLWIDE_CERTIFICATE":
                        note("gp_targets_nogo", status)
                        continue
                    target = rec["target"]
                    split = as_split(target["split"])
                    bits = int(target["sigma_bits"])
                    d = int(rec["degree"])
                    expect = 20 * len(monomials(d)) + 5 * len(monomials(d + 1))
                    if int(outcome.get("n_variables", expect)) != expect:
                        note("gp_targets", "NVARS_MISMATCH")
                        continue
                    if len(samples) < 24:
                        samples.append((f"{tag}:d{d}", bits, split,
                                        outcome["certificate"], d))
                    fails, info = auditor.verify(bits, split,
                                                 outcome["certificate"], d)
                    hist = auditor.identity_stats["explicit"]
                    nn = info.get("nontrivial_identities", -1)
                    hist[nn] = hist.get(nn, 0) + 1
                    if fails:
                        note(f"gp_targets_d{d}", "|".join(sorted(fails)),
                             sigma_bits=bits, target=target.get("id"),
                             detail=info)
                    else:
                        note(f"gp_targets_d{d}", "OK")
                    maybe_checkpoint()
                    n += 1
                    if args.limit and n >= args.limit:
                        break
                # the negative canary's exact strict-primal witness
                note("gp_targets_canary", check_negative_canary(ref))
                state["completed"].append(tag)
                maybe_checkpoint(force=True)
                del data
                continue

            shard_degree = int(data.get("degree", 2))
            shard_split = data.get("split")
            n = 0
            for rec in data["results"]:
                outcome = rec["outcome"]
                status = outcome["status"]
                if "split" in rec:
                    split = as_split(rec["split"])
                    if shard_split is not None and split != as_split(shard_split):
                        note(tag, "SPLIT_MISMATCH")
                        continue
                elif shard_split is not None:
                    split = as_split(shard_split)
                    if "k" in rec:
                        k = int(rec["k"])
                        if split != tuple(1 if t < k else -1
                                          for t in range(5)):
                            note(tag, "K_SPLIT_MISMATCH")
                            continue
                else:
                    k = int(rec["k"])
                    if k not in (0, 1, 2):
                        note(tag, "BAD_K")
                        continue
                    split = tuple(1 if t < k else -1 for t in range(5))
                bits = int(rec["sigma_bits"])
                if bits not in ref.valid:
                    note(tag, "SIGMA_NOT_VALID")
                    continue
                if status == "FAMILY_SINGLE_CLASS":
                    cls = family_class(bits, split)
                    if cls is None:
                        note(tag + "fam", "FAMILY_CRITERION_FAIL")
                        continue
                    cert, d, kind = family_certificate(cls), 0, "family"
                elif status == "EXACT_CELLWIDE_CERTIFICATE":
                    cert = outcome["certificate"]
                    d = int(outcome.get("degree", shard_degree))
                    kind = "explicit"
                else:
                    note(tag, f"UNEXPECTED_STATUS:{status}")
                    continue
                if len(samples) < 24 and n < 2:
                    samples.append((f"{tag}", bits, split, cert, d))
                sub = tag + ("fam" if kind == "family" else "")
                audit_record(sub, bits, split, cert, d, kind)
                n += 1
                if args.limit and n >= args.limit:
                    break
            state["completed"].append(tag)
            maybe_checkpoint(force=True)
            del data

    # ---- coverage completeness -------------------------------------------
    coverage_report = {}
    valid = set(ref.valid)
    for name, entry in sorted(coverage.items()):
        covered = entry["family"] | entry["explicit"]
        coverage_report[name] = {
            "n_valid_sigma": len(valid),
            "n_family": len(entry["family"]),
            "n_explicit": len(entry["explicit"]),
            "n_covered": len(covered),
            "missing_valid_sigma": len(valid - covered),
            "covered_but_not_valid": len(covered - valid),
            "duplicate_certifications": entry["duplicates"],
            "complete": covered == valid,
        }
    partial = bool(args.limit or args.canaries_only)
    coverage_ok = (not partial and len(coverage_report) == 4
                   and all(v["complete"] for v in coverage_report.values()))

    # ---- canaries ---------------------------------------------------------
    if not samples:
        samples = collect_samples(auditor, ref)
    for e in (1, 3):
        auditor.context(e)
    log(f"[{time.time()-t0:7.1f}s] canary battery on {len(samples)} samples ...")
    canaries, controls = run_canaries(auditor, samples, log=log)
    canary_ok = all(c["ok"] for c in canaries) and all(c["ok"]
                                                       for c in controls)
    for c in canaries:
        if not c["ok"]:
            log(f"  CANARY FAILURE: {c}")
    for c in controls:
        if not c["ok"]:
            log(f"  CONTROL FAILURE: {c}")

    # ---- old-auditor comparison ------------------------------------------
    comparison = compare_to_old_auditor(counts, partial)

    total = sum(v for k, v in counts.items()
                if k.endswith(":OK"))
    n_fail = sum(v for k, v in counts.items() if not k.endswith(":OK")
                 and not k.startswith("gp_targets_nogo"))
    verdict = ("PASS" if (n_fail == 0 and canary_ok and chi_match
                          and (coverage_ok or partial))
               else "FAIL")

    report = {
        "schema": 1,
        "tool": "ai/maxout/capstone/independent_audit.py",
        "generated_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "python": sys.version.split()[0],
        "dependencies": "python standard library only",
        "argv": sys.argv[1:],
        "inputs": inputs,
        "reference": {
            "U_ints": [list(r) for r in ref.U],
            "source": "read from the certificate artifacts themselves",
            "chirotope_signs_derived": list(ref.chi),
            "chirotope_signs_shipped": list(chi_shipped),
            "chirotope_match": chi_match,
            "n_chambers": len(ref.chambers),
            "chamber_completeness": "each of the 32 sign vectors carries either "
                                    "an explicit integer interior point or an "
                                    "explicit Gordan vector (mutually exclusive "
                                    "by Gordan's theorem)",
            "n_valid_sigma": len(ref.valid),
            "cross_check_reference_structure_json": xcheck,
        },
        "algebra": {
            "criterion": "F is cell-wide iff Phi(F) is the zero polynomial in "
                         "the 15 configuration entries; decided by exact "
                         "integer evaluation against a rank-certified set of "
                         "evaluation functionals",
            "plucker_relations_verified_symbolically": True,
            "seed_evaluation_points": SEED_EVAL_POINTS,
            "evaluation_point_rule": "random.Random(SEED+1000*e), entries "
                                     "uniform in [-4,4], skipping degenerate "
                                     "configurations",
            "seed_fresh_realizations": SEED_FRESH,
            "fresh_realizations": [[list(r) for r in V]
                                   for _, V in auditor.realizations[1:]],
            "degrees": {
                str(e): {
                    "n_monomials": ctx.M,
                    "rank_evaluation_rows": ctx.rank_eval,
                    "rank_plucker_multiples": ctx.rank_plucker,
                    "sandwich_closes": ctx.rank_eval + ctx.rank_plucker == ctx.M,
                    "rank_prime": ctx.prime,
                    "n_plucker_generator_rows": ctx.n_plucker_rows,
                    "classical_hilbert_value": ctx.hilbert_prediction,
                    "matches_classical": ctx.rank_eval == ctx.hilbert_prediction,
                } for e, ctx in sorted(auditor.contexts.items())
            },
        },
        "counts": dict(sorted(counts.items())),
        "coverage": coverage_report,
        "coverage_complete": coverage_ok,
        "canaries": canaries,
        "machinery_controls": controls,
        "canaries_ok": canary_ok,
        "old_auditor_comparison": comparison,
        "non_vacuity": {
            "explanation": "number of the ten identity polynomials that are "
                           "nonzero AS WRITTEN (before any use of the Pluecker "
                           "variety) per certificate.  A 0 means the identity "
                           "is ordinary polynomial cancellation needing no "
                           "Pluecker input -- exactly what the closed-form "
                           "family certificates do.  A positive count means "
                           "the certificate really relies on the Pluecker "
                           "relations and the new algebra had work to do.",
            "family": {str(k): v for k, v in
                       sorted(auditor.identity_stats["family"].items())},
            "explicit": {str(k): v for k, v in
                         sorted(auditor.identity_stats["explicit"].items())},
            "explicit_needing_plucker": sum(
                v for k, v in auditor.identity_stats["explicit"].items()
                if k > 0),
            "explicit_total": sum(auditor.identity_stats["explicit"].values()),
        },
        "partial_run": partial,
        "totals": {"checks_ok": total, "checks_failed": n_fail},
        "failures": failures,
        "elapsed_seconds": round(time.time() - t0, 1),
        "verdict": verdict,
    }
    atomic_write_json(args.report, report)
    log(f"\nINDEPENDENT AUDIT {verdict}: {total} checks OK, {n_fail} failed, "
        f"{time.time()-t0:.0f}s")
    log(f"report written to {args.report}")
    return 0 if verdict == "PASS" else 1


def check_negative_canary(ref):
    """The strict primal witness of the deliberately-infeasible control system
    (sigma_bits = 0, split = {0}) shipped in gp_degree3_results.json.gz.  A
    strictly feasible x proves, by Gordan, that no certificate can exist there."""
    from fractions import Fraction
    x = [Fraction(v) for v in
         ("0", "0", "0", "1", "1619/440", "447/88", "1201/440", "1")]
    rows = ref.rows(0, (1, -1, -1, -1, -1))
    margins = [sum(Fraction(a) * b for a, b in zip(row, x)) for row in rows]
    return "OK" if min(margins) > 0 else "NEGATIVE_CANARY_WITNESS_NOT_STRICT"


def collect_samples(auditor, ref):
    """Fallback sample collector for --canaries-only."""
    out = []
    for tag, path in BUNDLES:
        if path is None or tag == "gp_targets":
            continue
        data = load_gz(path)
        shard_degree = int(data.get("degree", 2))
        shard_split = data.get("split")
        n = 0
        for rec in data["results"]:
            outcome = rec["outcome"]
            if "split" in rec:
                split = as_split(rec["split"])
            elif shard_split is not None:
                split = as_split(shard_split)
            else:
                k = int(rec["k"])
                split = tuple(1 if t < k else -1 for t in range(5))
            bits = int(rec["sigma_bits"])
            if outcome["status"] == "FAMILY_SINGLE_CLASS":
                cls = family_class(bits, split)
                if cls is None:
                    continue
                out.append((tag + "fam", bits, split,
                            family_certificate(cls), 0))
            else:
                out.append((tag, bits, split, outcome["certificate"],
                            int(outcome.get("degree", shard_degree))))
            n += 1
            if n >= 2:
                break
        del data
    return out


def compare_to_old_auditor(counts, partial=False):
    """Read (not run) the shipped auditor's committed report and line the counts
    up.  Disagreement is a finding; a superset is not."""
    path = STAGE / "audit_all_report.json"
    if not path.exists():
        return {"available": False}
    old = json.loads(path.read_text(encoding="utf-8"))
    mapping = {
        "sweep0:OK": "sweep0:OK", "sweep1:OK": "sweep1:OK",
        "sweep2:OK": "sweep2:OK", "sweep3:OK": "sweep3:OK",
        "k0fam:OK": "k0fam:OK", "k0gp:OK": "k0:OK",
        "famk1:OK": "famk1:OK", "famk2:OK": "famk2:OK",
        "prior120:OK": "gp_targets_d2:OK",
        "s02fam:OK": None, "s02gp2:OK": None,
    }
    rows = []
    agree = True
    for their_key, my_key in mapping.items():
        theirs = old["counts"].get(their_key, 0)
        if their_key == "s02fam:OK":
            mine = sum(counts.get(f"split02_{i}fam:OK", 0) for i in range(4))
        elif their_key == "s02gp2:OK":
            mine = sum(counts.get(f"split02_{i}:OK", 0) for i in range(4))
        else:
            mine = counts.get(my_key, 0)
        rows.append({"old_tag": their_key, "old_count": theirs,
                     "this_audit": mine, "agree": theirs == mine})
        agree = agree and theirs == mine
    return {
        "available": True,
        "meaningful": not partial,
        "old_report": str(path.name),
        "old_verdict": old.get("verdict"),
        "old_total": old.get("total_audited"),
        "rows": rows,
        "all_counts_agree": agree and not partial,
        "note": ("PARTIAL RUN -- counts are not comparable. " if partial
                 else "") +
                "this audit additionally verifies the degree-0/1/3 entries of "
                "gp_degree3_results.json.gz, which the shipped auditor skips, "
                "and additionally proves coverage completeness; its totals are "
                "therefore a superset, not a disagreement",
    }


if __name__ == "__main__":
    sys.exit(main())
