#!/usr/bin/env python3
"""Non-realizability by biquadratic final polynomial (Bokowski / Richter-Gebert).

THE ARGUMENT
------------
Suppose chi is realized by X.  Write [B] for the bracket det X_B and
u_j = log|[B_j]|.  Every three-term Grassmann-Plucker relation

    e1 [Lab][Lcd] + e2 [Lac][Lbd] + e3 [Lad][Lbc] = 0        (e_k = +-1)

has its three signed terms summing to zero, and chi says which sign each
term carries.  Validity forbids all three from agreeing, so exactly one
term -- call it the BIG one -- has the sign opposite to the other two.
Then |big| = |other1| + |other2|, hence STRICTLY

    |big| > |other1|      and      |big| > |other2|,

and in logs each of those is a linear inequality  v . u > 0  with
v = e_{p}+e_{q} - e_{s}-e_{t} in Z^M.  Collect all of them into V.

If some w >= 0, w != 0 has  sum_i w_i v_i = 0  then no u can satisfy them
all (0 = sum w_i (v_i.u) > 0), so NO realization exists.  That w is the
certificate -- Gordan's theorem, exactly the shape ai/maxout used.

Finding w is an LP (scipy/HiGHS); the LP is only a SEARCH.  The w that is
emitted is recomputed in exact rational arithmetic on the LP's support and
shipped as integers, so `checkcert.py` can verify it with integer
arithmetic alone.

BFP IS INCOMPLETE FOR ORIENTED MATROIDS IN GENERAL.  Richter-Gebert's
published rank-(3,14) example is non-uniform, so it does not by itself
settle completeness on the uniform subclass processed here.  This search
makes no completeness assumption: failure to find a certificate is not a
realization proof, and the pipeline reports it as RESIDUE, never as
realizable.
"""

import math
from fractions import Fraction
from itertools import combinations

import numpy as np
from scipy.optimize import linprog


def _sort_sign(t):
    a = list(t)
    sg = 1
    for i in range(1, len(a)):
        j = i
        while j > 0 and a[j - 1] > a[j]:
            a[j - 1], a[j] = a[j], a[j - 1]
            sg = -sg
            j -= 1
    return tuple(a), sg


class GPSystem(object):
    """The three-term GP relations of (n, r) in a fixed, rederivable order.

    Elements are 1..n; bases are the C(n,r) r-subsets in COLEX order.
    Term k of a relation (L; a,b,c,d) is, for k = 0,1,2:
        k=0: +[Lab][Lcd]      k=1: -[Lac][Lbd]      k=2: +[Lad][Lbc]
    stored as (basis index, basis index, sign) with the sign absorbing both
    the tuple-sorting signs and the explicit minus at k=1.
    """

    def __init__(self, n, r):
        self.n, self.r = n, r
        bas = sorted(combinations(range(1, n + 1), r),
                     key=lambda t: tuple(reversed(t)))
        self.bases = bas
        self.M = len(bas)
        bidx = {B: j for j, B in enumerate(bas)}
        rel = []
        for L in combinations(range(1, n + 1), r - 2):
            rest = [x for x in range(1, n + 1) if x not in L]
            for a, b, c, d in combinations(rest, 4):
                trip = []
                for k, (x, y, z, w, ex) in enumerate(
                        ((a, b, c, d, 1), (a, c, b, d, -1), (a, d, b, c, 1))):
                    s1, g1 = _sort_sign(L + (x, y))
                    s2, g2 = _sort_sign(L + (z, w))
                    trip.append((bidx[s1], bidx[s2], ex * g1 * g2))
                rel.append((L, (a, b, c, d), tuple(trip)))
        self.rel = rel

    def term_signs(self, chi):
        """(nrel, 3) int8: the sign of each signed term under chi."""
        out = np.empty((len(self.rel), 3), dtype=np.int8)
        for i, (_, _, trip) in enumerate(self.rel):
            for k, (j1, j2, sg) in enumerate(trip):
                out[i, k] = sg * int(chi[j1]) * int(chi[j2])
        return out

    def inequalities(self, chi):
        """Rows v in Z^M with v.u > 0 forced by chi, plus their provenance.

        Returns (V, meta) with V an (m, M) int8 array and meta a list of
        (relation index, big term k, small term k).
        """
        ts = self.term_signs(chi)
        rows, meta = [], []
        for i in range(len(self.rel)):
            s = ts[i]
            if s[0] == s[1] == s[2]:
                raise ValueError('chirotope violates a GP relation at %d' % i)
            # the odd one out: the index whose sign differs from the other two
            if s[0] == s[1]:
                big = 2
            elif s[0] == s[2]:
                big = 1
            else:
                big = 0
            trip = self.rel[i][2]
            for small in range(3):
                if small == big:
                    continue
                v = np.zeros(self.M, dtype=np.int8)
                v[trip[big][0]] += 1
                v[trip[big][1]] += 1
                v[trip[small][0]] -= 1
                v[trip[small][1]] -= 1
                if not v.any():
                    continue
                rows.append(v)
                meta.append((i, big, small))
        return (np.array(rows, dtype=np.int8) if rows
                else np.zeros((0, self.M), dtype=np.int8)), meta


# ----------------------------------------------------------------------
# Gordan search + exact rational reconstruction
# ----------------------------------------------------------------------

def _exact_nonneg_kernel(V, sup):
    """Exact w>0 on `sup` with sum_i w_i V[i] = 0, normalised to integers.

    Solves  [V_sup^T ; 1^T] w = [0 ; 1]  over Q by Gaussian elimination.
    Returns an integer vector or None (non-unique, or some w_i <= 0).
    """
    k = len(sup)
    A = [[Fraction(int(V[i][j])) for i in sup] for j in range(V.shape[1])]
    A = [row for row in A if any(row)]
    A.append([Fraction(1)] * k)
    rhs = [Fraction(0)] * (len(A) - 1) + [Fraction(1)]
    m = len(A)
    piv = []
    r = 0
    for c in range(k):
        p = None
        for i in range(r, m):
            if A[i][c]:
                p = i
                break
        if p is None:
            continue
        A[r], A[p] = A[p], A[r]
        rhs[r], rhs[p] = rhs[p], rhs[r]
        inv = 1 / A[r][c]
        A[r] = [v * inv for v in A[r]]
        rhs[r] *= inv
        for i in range(m):
            if i != r and A[i][c]:
                f = A[i][c]
                A[i] = [a - f * b for a, b in zip(A[i], A[r])]
                rhs[i] -= f * rhs[r]
        piv.append(c)
        r += 1
        if r == m:
            break
    for i in range(r, m):
        if rhs[i] != 0 and not any(A[i]):
            return None                      # inconsistent
    if len(piv) != k:
        return None                          # under-determined: not unique
    w = [Fraction(0)] * k
    for i, c in enumerate(piv):
        w[c] = rhs[i]
    if any(v <= 0 for v in w):
        return None
    den = 1
    for v in w:
        den = den * v.denominator // math.gcd(den, v.denominator)
    wi = [int(v * den) for v in w]
    g = 0
    for v in wi:
        g = math.gcd(g, v)
    if g > 1:
        wi = [v // g for v in wi]
    return wi


def find_bfp(chi, gp, tol=1e-9):
    """Search for a biquadratic final polynomial for chi.

    Returns (cert, info).  cert is None when no BFP was found; otherwise it
    is a dict {'terms': [(rel_index, big, small, weight), ...]} with
    integer weights > 0.
    """
    V, meta = gp.inequalities(chi)
    info = {'nrows': len(V), 'lp': None}
    if len(V) == 0:
        return None, info
    m = len(V)
    Aeq = np.vstack([V.T.astype(np.float64), np.ones((1, m))])
    beq = np.zeros(gp.M + 1)
    beq[-1] = 1.0
    res = linprog(np.zeros(m), A_eq=Aeq, b_eq=beq,
                  bounds=[(0, None)] * m, method='highs')
    info['lp'] = res.status
    if not res.success:
        return None, info
    lam = np.asarray(res.x)
    order = np.argsort(-lam)
    sup = [int(i) for i in order if lam[i] > tol]
    if not sup:
        return None, info
    for trim in range(len(sup)):
        cand = sup[:len(sup) - trim] if trim else sup
        w = _exact_nonneg_kernel(V, cand)
        if w is not None:
            terms = [(meta[i][0], meta[i][1], meta[i][2], int(wi))
                     for i, wi in zip(cand, w)]
            info['support'] = len(cand)
            return {'terms': terms}, info
        if trim > 3:
            break
    info['exact_failed'] = True
    return None, info
