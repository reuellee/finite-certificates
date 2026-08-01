#!/usr/bin/env python3
"""WEAPON B2 -- general final polynomials, in COEFFICIENT space.

THE DIFFERENCE FROM WEAPON B1, WHICH MATTERS
============================================
A biquadratic final polynomial (`gordan.py`) lives in EXPONENT space: it
uses only the magnitudes |bracket|, takes logarithms, and finds a positive
combination of the resulting linear inequalities that vanishes.  It throws
away the actual arithmetic of the Grassmann-Plucker relations and keeps
only "this product dominates that one".

A final polynomial in the sense of Bokowski and Sturmfels keeps the
arithmetic and throws away the ordering.  Substitute

    y_B = chi(B) * [B],      so every realization has y > 0,

and each bracket identity becomes  R_j(y) = sum_k s_jk y_P y_Q = 0  with
s_jk = +-1 read off from chi.  Take any polynomial combination

    P  =  sum_{j, m}  lambda_{j,m} * m * R_j        (m a bracket monomial)

If every coefficient of P, expanded in the monomial basis, has the same
weak sign and at least one is strict, then for y > 0 we get P(y) != 0 --
while P(y) = 0 because every R_j vanishes on a realization.  So no
realization exists.  Degree 2 is m = 1; degree 3 is m a single bracket.

NEITHER METHOD CONTAINS THE OTHER.  A Gordan vector is a statement about
sums of EXPONENT VECTORS cancelling in Z^126; a final polynomial is a
statement about MONOMIALS cancelling.  {y1y2, y3y4} and {y1y3, y2y4} have
the same exponent sum and are different monomials, so the two conditions
are genuinely different and the task's framing of BFP as "the degree-2
special case" of this hierarchy is not right.  That is why this file's
failure on a class is reported as a measurement, not as a bug, while
`gordan.py` failing on a certified non-realizable class WOULD be a bug.

EXACTNESS
=========
The LP is a search over floating point.  Any certificate it proposes is
rebuilt exactly: the support is re-solved as a rational linear system, the
coefficients are emitted as integer numerator/denominator pairs, and the
whole polynomial is re-expanded over Q before the record is written.  The
independent checker `fpcheck.py` then does it a third time from the
combinatorial data alone.
"""

import os
import sys

sys.dont_write_bytecode = True
for _v in ('OMP_NUM_THREADS', 'MKL_NUM_THREADS', 'OPENBLAS_NUM_THREADS',
           'NUMEXPR_NUM_THREADS'):
    os.environ.setdefault(_v, '1')

import math                                                 # noqa: E402
from fractions import Fraction                              # noqa: E402

import numpy as np                                          # noqa: E402
from scipy.optimize import linprog                          # noqa: E402
from scipy.sparse import coo_matrix                         # noqa: E402

import gplib                                                # noqa: E402
import gordan                                               # noqa: E402

BUDGET = 300.0


# ----------------------------------------------------------------------
# the monomial expansion
# ----------------------------------------------------------------------

def build_system(idents, chi, degree, multipliers=None):
    """Columns (j, mult) -> the coefficient vector of mult * R_j.

    Returns (A, cols, mons) with A a scipy COO matrix (nmon x ncol), cols a
    list of (identity index, multiplier tuple) and mons the monomial list.
    """
    if degree < 2:
        raise ValueError('degree must be >= 2')
    if degree == 2:
        mults = [()]
    else:
        if multipliers is None:
            raise ValueError('degree > 2 needs an explicit multiplier set')
        mults = [tuple(m) for m in multipliers]
    sgn = [gplib.term_signs(idt, chi) for idt in idents]
    mon_id = {}
    rows, colsi, vals = [], [], []
    cols = []
    for idt_i, idt in enumerate(idents):
        s = sgn[idt_i]
        for mu in mults:
            c = len(cols)
            cols.append((idt_i, mu))
            for k, (_, i, j) in enumerate(idt.terms):
                mon = tuple(sorted(mu + (i, j)))
                mi = mon_id.get(mon)
                if mi is None:
                    mi = len(mon_id)
                    mon_id[mon] = mi
                rows.append(mi)
                colsi.append(c)
                vals.append(float(s[k]))
    nmon = len(mon_id)
    A = coo_matrix((vals, (rows, colsi)), shape=(nmon, len(cols))).tocsr()
    A.sum_duplicates()
    mons = [None] * nmon
    for m, i in mon_id.items():
        mons[i] = m
    return A, cols, mons


def _lp(A, tol=1e-7):
    """min 1^T A lam  s.t.  A lam <= 0,  -1 <= lam <= 1.

    The feasible set is a cone intersected with a box, so the optimum is
    negative iff a final polynomial exists.
    """
    ncol = A.shape[1]
    c = np.asarray(A.sum(axis=0)).ravel()
    res = linprog(c, A_ub=A, b_ub=np.zeros(A.shape[0]),
                  bounds=[(-1.0, 1.0)] * ncol, method='highs')
    if not res.success:
        return None, res
    if res.fun >= -tol:
        return None, res
    return np.asarray(res.x), res


# ----------------------------------------------------------------------
# exact reconstruction
# ----------------------------------------------------------------------

def _expand_exact(Acsc, sup, wq):
    """Exact {monomial index: Fraction} for sum_j wq[j] * column sup[j].

    Sparse throughout: the degree-3 system has ~290 000 monomial rows and
    ~159 000 columns, so densifying it would cost gigabytes.
    """
    g = {}
    ip, ix, dv = Acsc.indptr, Acsc.indices, Acsc.data
    for t, j in enumerate(sup):
        v = wq[t]
        if v == 0:
            continue
        for q in range(ip[j], ip[j + 1]):
            i = int(ix[q])
            g[i] = g.get(i, Fraction(0)) + v * int(round(float(dv[q])))
    return {i: v for i, v in g.items() if v != 0}


def _sign_ok(g):
    if not g:
        return False
    pos = any(v > 0 for v in g.values())
    neg = any(v < 0 for v in g.values())
    return not (pos and neg)


def _reduce(Acsc, sup, wq, g):
    """Greedily drop generators while the polynomial stays one-signed and
    nonzero.  A cone LP returns a vertex, whose support can run to thousands
    of columns; the certificate that comes out of this is typically a
    handful, which is what makes it readable and cheap to re-check.

    Each removal touches only the few monomials of one column, so the test
    is O(1) amortised rather than a re-expansion.
    """
    want_neg = any(v < 0 for v in g.values())
    g = dict(g)
    ip, ix, dv = Acsc.indptr, Acsc.indices, Acsc.data
    keep = list(range(len(sup)))
    order = sorted(keep, key=lambda t: abs(wq[t]))
    live = set(keep)
    nz = sum(1 for v in g.values() if v != 0)
    for t in order:
        j, v = sup[t], wq[t]
        if v == 0:
            live.discard(t)
            continue
        delta = {}
        for q in range(ip[j], ip[j + 1]):
            i = int(ix[q])
            delta[i] = delta.get(i, Fraction(0)) + v * int(round(float(dv[q])))
        ok = True
        dnz = 0
        for i, dvl in delta.items():
            new = g.get(i, Fraction(0)) - dvl
            if (new > 0) if want_neg else (new < 0):
                ok = False
                break
            was = g.get(i, Fraction(0)) != 0
            now = new != 0
            dnz += int(now) - int(was)
        if not ok or nz + dnz <= 0:
            continue
        for i, dvl in delta.items():
            g[i] = g.get(i, Fraction(0)) - dvl
        nz += dnz
        live.discard(t)
    idx = sorted(live)
    return [sup[t] for t in idx], [wq[t] for t in idx]


def _exact_from_support(A, lam, tol, cap=400):
    """Rebuild an exact rational lambda from the LP's float solution.

    Two attempts, cheapest first:

    1. round lambda itself to rationals with a small denominator and expand
       exactly.  The LP optimum of a cone LP is a vertex, so the entries are
       often already simple, and this settles the easy cases (including the
       positive control) in microseconds;
    2. otherwise, hold the active monomials at exactly zero and search the
       exact null space of the active submatrix, guided by the float
       solution.  Capped: a support of more than `cap` columns makes the
       rational elimination the dominant cost and is reported as a failure
       of the search rather than pursued.
    """
    ncol = A.shape[1]
    Acsc = A.tocsc()
    big = float(np.abs(lam).max())
    for frac in (0.5, 0.2, 0.05, 0.01, 0.0):
        thr = max(tol, frac * big)
        sup = [j for j in range(ncol) if abs(lam[j]) > thr]
        if not sup:
            continue
        for D in (1, 2, 4, 12, 60, 2520):
            wq = [Fraction(int(round(lam[j] * D)), D) for j in sup]
            if all(v == 0 for v in wq):
                continue
            g = _expand_exact(Acsc, sup, wq)
            if _sign_ok(g):
                for _ in range(4):
                    m = len(sup)
                    sup, wq = _reduce(Acsc, sup, wq,
                                      _expand_exact(Acsc, sup, wq))
                    if len(sup) == m:
                        break
                lamq = [Fraction(0)] * ncol
                for t, j in enumerate(sup):
                    lamq[j] = wq[t]
                return lamq
    sup = [j for j in range(ncol) if abs(lam[j]) > tol]
    if not sup or len(sup) > cap:
        return None
    gam = np.asarray(A.dot(lam)).ravel()
    scale = max(1e-12, float(np.abs(gam).max()))
    # only rows touched by the support can constrain it
    touched = set()
    ip, ix = Acsc.indptr, Acsc.indices
    for j in sup:
        touched.update(int(v) for v in ix[ip[j]:ip[j + 1]])
    act = [i for i in sorted(touched) if abs(gam[i]) <= tol * scale]
    dense = {}
    for t, j in enumerate(sup):
        for q in range(ip[j], ip[j + 1]):
            dense[(int(ix[q]), t)] = int(round(float(Acsc.data[q])))
    Asub = [[Fraction(dense.get((i, t), 0)) for t in range(len(sup))]
            for i in act]
    if Asub:
        ns = gordan.exact_nullspace(Asub, len(sup))
    else:
        ns = [[Fraction(1) if t == q else Fraction(0)
               for t in range(len(sup))] for q in range(len(sup))]
    if not ns:
        return None
    Bm = np.array([[float(v) for v in b] for b in ns]).T      # (|sup|, k)
    target = np.array([lam[j] for j in sup])
    try:
        coef, *_ = np.linalg.lstsq(Bm, target, rcond=None)
    except np.linalg.LinAlgError:
        return None
    for D in (1, 2, 6, 12, 60, 360, 2520, 27720, 1 << 20):
        cf = [Fraction(int(round(v * D)), D) for v in coef]
        if all(v == 0 for v in cf):
            continue
        wq = [Fraction(0)] * len(sup)
        for b, w in zip(ns, cf):
            if w == 0:
                continue
            for t in range(len(sup)):
                wq[t] += w * b[t]
        g = _expand_exact(Acsc, sup, wq)
        if not g:
            continue
        pos = any(v > 0 for v in g.values())
        neg = any(v < 0 for v in g.values())
        if pos and neg:
            continue
        lamq = [Fraction(0)] * ncol
        for t, j in enumerate(sup):
            lamq[j] = wq[t]
        return lamq
    return None


# ----------------------------------------------------------------------
# the search
# ----------------------------------------------------------------------

def find_fp(chi, degree=2, level='L0', budget=BUDGET, multipliers=None,
            sup=None, tol=1e-7, nmult=0, seed=0):
    """Search for a final polynomial of the given degree.

    Returns (cert, info).  cert = {'gens': [(identity index, mult tuple,
    Fraction coefficient), ...], 'degree': d, 'level': level}.
    """
    import time
    t0 = time.time()
    if sup is None:
        sup = gordan.Support(9 if len(chi) == 126 else 8, 4, level,
                             verify=False)
    idents = sup.idents
    info = {'degree': degree, 'level': level, 'nident': len(idents)}
    if degree > 2 and multipliers is None:
        rng = np.random.default_rng(seed)
        M = sup.M
        if nmult and nmult < M:
            pick = rng.choice(M, nmult, replace=False)
            multipliers = [(int(b),) for b in sorted(pick)]
        else:
            multipliers = [(b,) for b in range(M)]
    A, cols, mons = build_system(idents, chi, degree, multipliers)
    info['ncol'] = A.shape[1]
    info['nmon'] = A.shape[0]
    lam, res = _lp(A, tol)
    info['lp_obj'] = None if res is None else float(getattr(res, 'fun', 0.0))
    info['lp_status'] = None if res is None else int(res.status)
    info['seconds'] = round(time.time() - t0, 2)
    if lam is None:
        return None, info
    lamq = _exact_from_support(A, lam, tol)
    if lamq is None:
        info['exact_failed'] = True
        info['seconds'] = round(time.time() - t0, 2)
        return None, info
    den = 1
    for v in lamq:
        den = den * v.denominator // math.gcd(den, v.denominator)
    gens = [(cols[j][0], cols[j][1], int(v * den))
            for j, v in enumerate(lamq) if v != 0]
    info['support'] = len(gens)
    info['seconds'] = round(time.time() - t0, 2)
    return {'gens': gens, 'degree': degree, 'level': level, 'den': den}, info


def positive_control(chi, sup, want=('pl',)):
    """A rigged instance the search MUST solve, to prove the machinery works.

    Flip bracket signs of `chi` until one relation's terms all carry the same
    sign.  The resulting sign vector is no longer a chirotope, but it is
    certainly not the sign vector of any real configuration -- and the
    one-generator final polynomial P = +-R_j proves exactly that.  If the LP
    and the exact reconstruction cannot find that, they are broken, and the
    negative results below would mean nothing.

    Returns (rigged chi, cert, info).
    """
    chi = np.asarray(chi, dtype=np.int8).copy()
    for q, idt in enumerate(sup.idents):
        if idt.spec['kind'] not in want and want:
            continue
        used = set()
        ok = True
        for (e, i, j) in idt.terms:
            if i in used or j in used:
                ok = False
                break
            used.add(i)
            used.add(j)
        if not ok:
            continue
        c = chi.copy()
        for (e, i, j) in idt.terms:
            if e * int(c[i]) * int(c[j]) < 0:
                c[i] = -c[i]
        s = gplib.term_signs(idt, c)
        if not all(v > 0 for v in s):
            continue
        cert, info = find_fp(c, degree=2, sup=sup)
        info['rigged_identity'] = q
        return c, cert, info
    return None, None, {'no_candidate': True}


def fp_record(n, r, chi_str, cert, degree, sup):
    gens = []
    for (j, mu, num) in cert['gens']:
        gens.append({'rel': sup.idents[j].spec,
                     'mult': [list(sup.bases[b]) for b in mu],
                     'c': [int(num), 1]})
    return {'n': n, 'r': r, 'chi': chi_str, 'verdict': 'NON_REALIZABLE',
            'method': 'FP', 'degree': degree, 'level': cert['level'],
            'gens': gens}
