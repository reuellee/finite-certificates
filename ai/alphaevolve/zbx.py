"""Zonoboxtope vertex counting: fast float count (search) + EXACT count (gate).

Model (paper eq. (24), Balakin-Cox-Loho-Sturmfels arXiv:2509.21286 §6, as in
`../maxout/search_maxout67.py`): segments I_i = m_i + [-u_i, u_i], i = 1..n, in
R^d; nonnegative coefficient vectors a, b.

    Z^a = sum_i a_i I_i,   Z^b = sum_i b_i I_i,   Q = conv(Z^a u Z^b)

Every vertex of Q is a sign point of Z^a or of Z^b, so the candidate set is the
2^(n+1) points  (sum_i c_i m_i) + sum_i s_i c_i u_i,  s in {-1,1}^n, c in {a,b}.
f0(Q) = number of DISTINCT candidates that are extreme in the candidate set.

`nverts_float` is qhull on rounded floats -- fine for steering a search, never
for a claim.  `nverts_exact` decides extremality with exact Fraction arithmetic
(phase-1 simplex, Bland's rule) and is what gates every reported record.
"""
import itertools
from fractions import Fraction
from math import gcd

import numpy as np
from scipy.spatial import ConvexHull

_SIGNS = {}


def signs(n):
    if n not in _SIGNS:
        _SIGNS[n] = np.array(list(itertools.product([-1.0, 1.0], repeat=n)))
    return _SIGNS[n]


def candidates_float(M, U, a, b):
    M, U = np.asarray(M, float), np.asarray(U, float)
    a, b = np.asarray(a, float), np.asarray(b, float)
    S = signs(len(a))
    return np.vstack([(a[:, None] * M).sum(0) + S @ (a[:, None] * U),
                      (b[:, None] * M).sum(0) + S @ (b[:, None] * U)])


def nverts_float(M, U, a, b):
    """Search-time score.  Dedup at 1e-9, no joggle (joggling double-counts)."""
    try:
        P = candidates_float(M, U, a, b)
    except Exception:                                            # noqa: BLE001
        return 0
    if not np.all(np.isfinite(P)):
        return 0
    P = np.unique(np.round(P, 9), axis=0)
    if len(P) <= P.shape[1]:
        return len(P)
    try:
        return int(len(ConvexHull(P).vertices))
    except Exception:                                            # noqa: BLE001
        return 0


# ------------------------------------------------------------------ exact
def candidates_exact(M, U, a, b):
    n, d = len(a), len(M[0])
    M = [[Fraction(x) for x in r] for r in M]
    U = [[Fraction(x) for x in r] for r in U]
    a = [Fraction(x) for x in a]
    b = [Fraction(x) for x in b]
    pts = []
    for coef in (a, b):
        cen = [sum(coef[i] * M[i][j] for i in range(n)) for j in range(d)]
        for s in itertools.product((-1, 1), repeat=n):
            pts.append(tuple(cen[j] + sum(s[i] * coef[i] * U[i][j]
                                          for i in range(n))
                             for j in range(d)))
    return pts


def in_convex_hull(p, Q):
    """Exact: is p in conv(Q)?  Phase-1 simplex over Fractions, Bland's rule."""
    d, m = len(p), len(Q)
    if m == 0:
        return False
    rows = [[Q[j][k] for j in range(m)] for k in range(d)]
    rhs = [p[k] for k in range(d)]
    rows.append([Fraction(1)] * m)           # sum of multipliers = 1
    rhs.append(Fraction(1))
    r = d + 1
    for i in range(r):                       # make the RHS nonnegative
        if rhs[i] < 0:
            rows[i] = [-x for x in rows[i]]
            rhs[i] = -rhs[i]
    # tableau: m real columns, r artificial columns, then the RHS
    T = [rows[i] + [Fraction(int(t == i)) for t in range(r)] + [rhs[i]]
         for i in range(r)]
    basis = list(range(m, m + r))            # artificials
    ncols = m + r
    guard = 0
    while True:
        guard += 1
        if guard > 20000:
            raise RuntimeError("phase-1 simplex did not terminate")
        # phase-1 cost is 1 on artificials, 0 on reals, so the reduced cost of
        # column j is  c_j - sum_{i : basis[i] is artificial} T[i][j].
        art_rows = [i for i in range(r) if basis[i] >= m]
        if not art_rows:
            return True                      # every artificial already left
        inbasis = set(basis)
        bland = guard > 400                  # anti-cycling fallback
        enter, most = -1, Fraction(0)
        for j in range(ncols):
            if j in inbasis:
                continue
            s = Fraction(0)
            for i in art_rows:
                s += T[i][j]
            red = Fraction(int(j >= m)) - s
            if red < 0:
                if bland:
                    enter = j                # Bland: lowest index, terminates
                    break
                if red < most:
                    most, enter = red, j     # Dantzig: steepest, much faster
        if enter < 0:
            break
        leave, best = -1, None
        for i in range(r):
            if T[i][enter] > 0:
                ratio = T[i][ncols] / T[i][enter]
                if best is None or ratio < best or (
                        ratio == best and basis[i] < basis[leave]):
                    best, leave = ratio, i
        if leave < 0:
            break                            # unbounded (cannot happen here)
        piv = T[leave][enter]
        T[leave] = [x / piv for x in T[leave]]
        for i in range(r):
            if i != leave and T[i][enter] != 0:
                f = T[i][enter]
                T[i] = [x - f * y for x, y in zip(T[i], T[leave])]
        basis[leave] = enter
    obj = sum(T[i][ncols] for i in range(r) if basis[i] >= m)
    return obj == 0


def _integerise(pts):
    """Scale all points by the common denominator.  Extremality is invariant
    under a positive scaling, and integer coordinates keep the exact simplex
    from drowning in denominator growth (orders of magnitude faster)."""
    den = 1
    for p in pts:
        for x in p:
            den = den * x.denominator // gcd(den, x.denominator)
    return [tuple(Fraction(x.numerator * (den // x.denominator)) for x in p)
            for p in pts]


def nverts_exact(M, U, a, b, return_pts=False):
    """EXACT f0.  Deduplicates candidates, then tests extremality of each."""
    pts = _integerise(candidates_exact(M, U, a, b))
    uniq = sorted(set(pts))
    verts = [i for i, p in enumerate(uniq)
             if not in_convex_hull(p, [q for j, q in enumerate(uniq) if j != i])]
    if return_pts:
        return len(verts), uniq, verts
    return len(verts)


def cap(d, n):
    """Absolute cap 4 * sum_{k<d} C(n-1,k) (paper's zonotope vertex bound)."""
    from math import comb
    return 4 * sum(comb(n - 1, k) for k in range(d))
