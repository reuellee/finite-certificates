#!/usr/bin/env python3
"""Bracket identities for (n, r), and the sign-inequalities they force.

WHY THIS FILE EXISTS
====================
`ai/omreal/bfp.py` searches for a biquadratic final polynomial using ONE
family of bracket identities: the three-term Grassmann-Plucker relations

    [Lab][Lcd] - [Lac][Lbd] + [Lad][Lbc] = 0        (|L| = r-2).

That is the standard BFP support.  A class the sweep leaves OPEN has no
Gordan vector over that support.  To attack it from the non-realizable
side we need MORE valid identities, so this file generates the whole
one-step Plucker/exchange family

    sum_{k=0}^{r} (-1)^k [a_1 .. a_{r-1} b_k] [b_0 .. b^_k .. b_r] = 0

for every 3-subset A = {a_1<a_2<a_3} and 5-subset B = {b_0<..<b_4} of the
ground set (r = 4 here; the code is written for general r).  Terms whose
first bracket repeats an index vanish, so

    |A cap B| = 2  ->  3 terms   (exactly the classical GP relations)
    |A cap B| = 1  ->  4 terms
    |A cap B| = 0  ->  5 terms
    |A cap B| = 3  ->  2 terms, and they cancel: the identity is trivial

THE INEQUALITIES
================
Substitute [B] = chi(B) * y_B, so a realization has every y_B > 0.  An
identity becomes  sum_k s_k y_{P_k} y_{Q_k} = 0  with s_k = +-1 read off
from chi.  Then:

* if every s_k agrees, a sum of strictly positive numbers is zero: the
  class is non-realizable outright (`all_same` below).  This cannot happen
  for a 3-term relation of a valid chirotope, but it can for 4 and 5.
* if exactly one s_k is the odd one out, that term equals the sum of the
  others, so it STRICTLY dominates each of them:
      y_{P_big} y_{Q_big}  >  y_{P_k} y_{Q_k}   for every other k.
  In logs u = log y that is  v . u > 0  with
      v = e_{P_big} + e_{Q_big} - e_{P_k} - e_{Q_k}   in Z^M.
* otherwise (a 2-2 or 3-2 split) the identity forces no single-term
  domination and contributes nothing.

Collecting all such v is the "wider biquadratic support"; a nonnegative
nonzero w with sum_i w_i v_i = 0 is a Gordan vector and proves
non-realizability, exactly as in `bfp.py` but over a larger cone.

WHAT IS *NOT* HERE, AND WHY
===========================
Two strengthenings look attractive and are both worthless; the derivations
are in `OPEN_ATTACK.md` s3.4.  (i) |big| = |s1| + |s2| also gives the AM-GM
bound 2(u_p+u_q) >= 2 log 2 + (u_s+u_t+u_u+u_v), but the left side is the
sum of two inequalities already in the cone, so the constant cannot be
used.  (ii) The upper bound |big| < 2 max(|s1|,|s2|) is disjunctive and,
whichever branch you pick, has the wrong Farkas sign: the homogeneous
system is invariant under u -> t u for t > 0, so any solution can be shrunk
until every such upper bound holds.  Neither adds a single certificate.

TRUST
=====
Every identity this file emits is checked to be an EXACT polynomial
identity: `verify_identities()` evaluates it on random integer r x n
matrices with exact integer determinants and demands the sum be exactly 0.
A sign error here would invent invalid inequalities, which would let the
LP "prove" a realizable class non-realizable -- the single most dangerous
failure mode in this directory, so it is tested at the source and again by
sabotage canaries downstream.
"""

import os

for _v in ('OMP_NUM_THREADS', 'MKL_NUM_THREADS', 'OPENBLAS_NUM_THREADS',
           'NUMEXPR_NUM_THREADS'):
    os.environ.setdefault(_v, '1')

from itertools import combinations                          # noqa: E402

import numpy as np                                          # noqa: E402


# ----------------------------------------------------------------------
# bases and sorting signs
# ----------------------------------------------------------------------

def colex_bases(n, r):
    """The C(n,r) r-subsets of {1..n} as ascending tuples, in colex order."""
    return sorted(combinations(range(1, n + 1), r),
                  key=lambda t: tuple(reversed(t)))


def sort_sign(t):
    """(sorted tuple, sign of the sorting permutation), or (None, 0) if a
    value repeats."""
    a = list(t)
    sg = 1
    for i in range(1, len(a)):
        j = i
        while j > 0 and a[j - 1] > a[j]:
            a[j - 1], a[j] = a[j], a[j - 1]
            sg = -sg
            j -= 1
    for i in range(1, len(a)):
        if a[i - 1] == a[i]:
            return None, 0
    return tuple(a), sg


def det_int(m):
    """Exact determinant of a square matrix of python ints (cofactor)."""
    k = len(m)
    if k == 1:
        return m[0][0]
    if k == 2:
        return m[0][0] * m[1][1] - m[0][1] * m[1][0]
    tot = 0
    for c in range(k):
        if m[0][c] == 0:
            continue
        minor = [[m[i][j] for j in range(k) if j != c] for i in range(1, k)]
        t = m[0][c] * det_int(minor)
        tot += t if (c % 2 == 0) else -t
    return tot


# ----------------------------------------------------------------------
# the identity family
# ----------------------------------------------------------------------

class Identity(object):
    """sum_k eps_k [B_{k,0}] [B_{k,1}] = 0, with B's given as basis indices.

    `spec` is the JSON-able provenance: {'kind': 'pl', 'A': [...], 'B': [...]}
    for the one-step exchange family, or {'kind':'gp3','L':[..],'abcd':[..]}
    for the classical three-term relations (emitted in the SAME term order
    as ai/omreal/bfp.py so that a level-0 certificate can also be handed to
    ai/omreal/checkcert.py).
    """

    __slots__ = ('terms', 'spec')

    def __init__(self, terms, spec):
        self.terms = tuple(terms)            # ((eps, i, j), ...)
        self.spec = spec

    def key(self):
        """Order-independent identity of the relation, up to a global sign.

        Two identities are the same relation iff their term sets agree up to
        a global sign flip; normalise by making the first term positive.
        """
        t = sorted((min(i, j), max(i, j), e) for (e, i, j) in self.terms)
        if t[0][2] < 0:
            t = [(i, j, -e) for (i, j, e) in t]
        return tuple(t)

    def __len__(self):
        return len(self.terms)


def gp3_identities(n, r, bidx):
    """The classical three-term relations, term order (ab|cd), (ac|bd), (ad|bc)
    with the middle term carrying the explicit minus -- bit-for-bit the
    convention of ai/omreal/bfp.py and ai/omreal/checkcert.py."""
    out = []
    for L in combinations(range(1, n + 1), r - 2):
        rest = [x for x in range(1, n + 1) if x not in L]
        for a, b, c, d in combinations(rest, 4):
            terms = []
            for (x, y, z, w, ex) in ((a, b, c, d, 1), (a, c, b, d, -1),
                                     (a, d, b, c, 1)):
                s1, g1 = sort_sign(L + (x, y))
                s2, g2 = sort_sign(L + (z, w))
                terms.append((ex * g1 * g2, bidx[s1], bidx[s2]))
            out.append(Identity(terms, {'kind': 'gp3', 'L': list(L),
                                        'abcd': [a, b, c, d]}))
    return out


def exchange_identity(A, B, r, bidx):
    """sum_k (-1)^k [A b_k][B \\ b_k] = 0 for a (r-1)-tuple A and (r+1)-tuple B.

    Returns an Identity with the vanishing terms dropped, or None if fewer
    than three terms survive (two-term relations are trivially 0 = 0).
    """
    terms = []
    for k, bk in enumerate(B):
        s1, g1 = sort_sign(tuple(A) + (bk,))
        if s1 is None:
            continue
        rest = tuple(x for x in B if x != bk)
        s2, g2 = sort_sign(rest)
        if s2 is None:
            continue
        e = (-1 if (k & 1) else 1) * g1 * g2
        terms.append((e, bidx[s1], bidx[s2]))
    if len(terms) < 3:
        return None
    return Identity(terms, {'kind': 'pl', 'A': list(A), 'B': list(B)})


def build_identities(n, r, families=('gp3', 'pl4', 'pl5')):
    """All requested identities, de-duplicated by `Identity.key()`.

    'gp3' -> the 1260 classical three-term relations at (9,4)
    'pl4' -> |A cap B| = 1, four surviving terms
    'pl5' -> A and B disjoint, five terms
    """
    bas = colex_bases(n, r)
    bidx = {B: j for j, B in enumerate(bas)}
    out, seen = [], set()

    def add(idt):
        if idt is None:
            return
        k = idt.key()
        if k in seen:
            return
        seen.add(k)
        out.append(idt)

    if 'gp3' in families:
        for idt in gp3_identities(n, r, bidx):
            add(idt)
    want = set()
    if 'pl4' in families:
        want.add(1)
    if 'pl5' in families:
        want.add(0)
    if want:
        for A in combinations(range(1, n + 1), r - 1):
            sA = set(A)
            for B in combinations(range(1, n + 1), r + 1):
                t = len(sA & set(B))
                if t in want:
                    add(exchange_identity(A, B, r, bidx))
    return out, bas, bidx


# ----------------------------------------------------------------------
# the identity table must actually be a set of identities
# ----------------------------------------------------------------------

def verify_identities(idents, n, r, bas, trials=200, seed=20260801,
                      lo=-30, hi=31, verbose=False):
    """Evaluate every identity on random integer r x n matrices, exactly.

    Returns (nchecked, failures) where failures is a list of
    (identity index, trial, value != 0).  A single failure invalidates every
    inequality this file would emit, so callers should treat it as fatal.
    """
    rng = np.random.default_rng(seed)
    fails = []
    for t in range(trials):
        X = rng.integers(lo, hi, size=(r, n))
        Xl = [[int(v) for v in row] for row in X]
        br = []
        for Bs in bas:
            br.append(det_int([[Xl[i][b - 1] for b in Bs] for i in range(r)]))
        if any(v == 0 for v in br):
            continue                     # not uniform; identities still hold,
        for q, idt in enumerate(idents):  # but keep the sample generic
            s = 0
            for (e, i, j) in idt.terms:
                s += e * br[i] * br[j]
            if s != 0:
                fails.append((q, t, s))
                if len(fails) > 20:
                    return trials, fails
    if verbose:
        print('verified %d identities on %d random integer configurations: '
              '%d failures' % (len(idents), trials, len(fails)))
    return trials, fails


# ----------------------------------------------------------------------
# chi -> strict inequalities in log space
# ----------------------------------------------------------------------

def term_signs(idt, chi):
    """The sign s_k of term k after substituting [B] = chi(B) y_B."""
    return [e * int(chi[i]) * int(chi[j]) for (e, i, j) in idt.terms]


def odd_one_out(sgn):
    """Index of the unique term whose sign differs from all others, or
    -1 if the split is not (len-1, 1), or -2 if every sign agrees."""
    p = [k for k, s in enumerate(sgn) if s > 0]
    m = [k for k, s in enumerate(sgn) if s < 0]
    if not p or not m:
        return -2
    if len(p) == 1:
        return p[0]
    if len(m) == 1:
        return m[0]
    return -1


class IneqSystem(object):
    """The strict inequalities  v . u > 0  a chirotope forces, over a chosen
    identity support.

    Attributes
    ----------
    V     (m, M) int8    the exponent vectors
    meta  list of (identity index, big term, small term)
    idents  the identity table (indices in `meta` point into it)
    contradiction  None, or an identity index whose terms all share a sign
                   (an immediate proof of non-realizability)
    """

    def __init__(self, idents, M):
        self.idents = idents
        self.M = M
        self.V = np.zeros((0, M), dtype=np.int8)
        self.meta = []
        self.contradiction = None

    @classmethod
    def build(cls, idents, chi, M):
        self = cls(idents, M)
        rows, meta = [], []
        for q, idt in enumerate(idents):
            sgn = term_signs(idt, chi)
            k = odd_one_out(sgn)
            if k == -2:
                if self.contradiction is None:
                    self.contradiction = q
                continue
            if k < 0:
                continue
            eb, ib, jb = idt.terms[k]
            for l in range(len(idt.terms)):
                if l == k:
                    continue
                _, il, jl = idt.terms[l]
                v = np.zeros(M, dtype=np.int8)
                v[ib] += 1
                v[jb] += 1
                v[il] -= 1
                v[jl] -= 1
                # A ZERO ROW IS KEPT ON PURPOSE.  v = 0 means the dominating
                # term and a dominated term are the SAME monomial, so the
                # identity says a nonempty sum of strictly positive numbers
                # is zero: w = e_i is then a one-term Gordan vector.
                # (ai/omreal/bfp.py silently drops such rows.  It cannot
                # matter at level L0 -- the six brackets of a three-term
                # relation are pairwise distinct -- and it cannot matter for
                # the exchange families either, since a zero row there would
                # force A subset B, excluded by |A cap B| <= r-2.  The guard
                # is here so that a future family cannot lose a certificate
                # quietly.)
                rows.append(v)
                meta.append((q, k, l))
        if rows:
            self.V = np.array(rows, dtype=np.int8)
        self.meta = meta
        return self


# ----------------------------------------------------------------------
# self-test
# ----------------------------------------------------------------------

def _selftest():
    ok = True
    for (n, r) in ((9, 4), (8, 4), (9, 3), (10, 3)):
        idents, bas, bidx = build_identities(n, r)
        by = {}
        for idt in idents:
            by[len(idt)] = by.get(len(idt), 0) + 1
        n3 = sum(1 for i in idents if i.spec['kind'] == 'gp3')
        from math import comb
        want3 = comb(n, r - 2) * comb(n - r + 2, 4)
        print('(%d,%d): %d identities, by term count %s; gp3 %d (expect %d)'
              % (r, n, len(idents), dict(sorted(by.items())), n3, want3))
        ok = ok and (n3 == want3)
        tr, fails = verify_identities(idents, n, r, bas, trials=60)
        print('    exact identity test on %d random integer configs: %s'
              % (tr, 'PASS' if not fails else 'FAIL %r' % fails[:3]))
        ok = ok and not fails
    # a deliberately corrupted identity must be caught by the same test
    idents, bas, bidx = build_identities(9, 4, families=('gp3',))
    bad = list(idents)
    t = list(bad[7].terms)
    t[0] = (-t[0][0], t[0][1], t[0][2])
    bad[7] = Identity(t, bad[7].spec)
    tr, fails = verify_identities(bad, 9, 4, bas, trials=5)
    print('sabotaged identity (one flipped eps) is caught: %s'
          % ('YES' if fails else 'NO'))
    ok = ok and bool(fails)
    return ok


if __name__ == '__main__':
    import sys
    sys.exit(0 if _selftest() else 1)
