#!/usr/bin/env python3
"""WEAPON B1 -- non-realizability in EXPONENT space, and its exact negation.

Given a chirotope chi and a support level, `gplib.IneqSystem` produces the
strict inequalities  v_i . u > 0  that every realization's
u = (log|bracket|) must satisfy.  Gordan's theorem (1873) says EXACTLY ONE
of these holds:

    (G)  there is w >= 0, w != 0, with  sum_i w_i v_i = 0
    (W)  there is u  with  v_i . u > 0  for every i

(G) is a final polynomial: 0 = sum_i w_i (v_i . u) > 0 for any realization,
so the class is NON-REALIZABLE.  At level L0 -- three-term Grassmann-Plucker
relations only -- (G) is precisely the biquadratic final polynomial of
Bokowski and Richter-Gebert that `ai/omreal/bfp.py` searches for.

(W) is the part this project did not have, and it is what makes an OPEN
class a scientific object rather than a gap in a search.  A verified
rational u is a PROOF that the class has no biquadratic final polynomial --
not "we looked and did not find one".  Without it, "non-realizable with no
BFP" cannot be claimed, because bfp.py returning None conflates an
infeasible LP with a failed exact reconstruction.

BOTH directions are searched in floating point and then REPRODUCED IN EXACT
ARITHMETIC:

  (G)  the LP's support is fed to an exact rational null-space computation;
       the emitted weights are integers and sum_i w_i v_i = 0 is an integer
       identity.
  (W)  the LP's u is scaled and rounded to integers and  V u > 0  is
       re-checked as an integer matrix-vector product.  The rounding is
       safe by construction: each |v_i|_1 = 4, so rounding u to k/D moves
       v_i . u by at most 2/D, and we demand a margin above that.

Neither certificate depends on the LP being right about anything.
"""

import os

for _v in ('OMP_NUM_THREADS', 'MKL_NUM_THREADS', 'OPENBLAS_NUM_THREADS',
           'NUMEXPR_NUM_THREADS'):
    os.environ.setdefault(_v, '1')

import math                                                 # noqa: E402
from fractions import Fraction                              # noqa: E402

import numpy as np                                          # noqa: E402
from scipy.optimize import linprog                          # noqa: E402

import gplib                                                # noqa: E402

LEVELS = {
    'L0': ('gp3',),                        # exactly ai/omreal/bfp.py's support
    'L1': ('gp3', 'pl4', 'pl5'),           # + the 4- and 5-term exchange family
}


class Support(object):
    """The identity table for one (n, r) and one level, built once."""

    def __init__(self, n, r, level='L0', verify=True, trials=60):
        if level not in LEVELS:
            raise ValueError('unknown level %r' % level)
        self.n, self.r, self.level = n, r, level
        self.idents, self.bases, self.bidx = gplib.build_identities(
            n, r, LEVELS[level])
        self.M = len(self.bases)
        self.verified = None
        if verify:
            tr, fails = gplib.verify_identities(self.idents, n, r, self.bases,
                                                trials=trials)
            if fails:
                raise SystemExit('IDENTITY TABLE IS WRONG at (%d,%d) %s: %r'
                                 % (r, n, level, fails[:3]))
            self.verified = tr

    def system(self, chi):
        return gplib.IneqSystem.build(self.idents, chi, self.M)


# ----------------------------------------------------------------------
# exact rational linear algebra
# ----------------------------------------------------------------------

def _rref(rows, ncol):
    """Reduced row echelon form over Q.  rows: list of lists of Fraction."""
    m = len(rows)
    piv = []
    r = 0
    for c in range(ncol):
        p = None
        for i in range(r, m):
            if rows[i][c]:
                p = i
                break
        if p is None:
            continue
        rows[r], rows[p] = rows[p], rows[r]
        inv = 1 / rows[r][c]
        rows[r] = [v * inv for v in rows[r]]
        for i in range(m):
            if i != r and rows[i][c]:
                f = rows[i][c]
                rows[i] = [a - f * b for a, b in zip(rows[i], rows[r])]
        piv.append(c)
        r += 1
        if r == m:
            break
    return rows, piv, r


def exact_nullspace(A, ncol):
    """Basis of {x : A x = 0} over Q.  A is a list of lists of Fraction."""
    rows = [list(row) for row in A]
    rows, piv, rank = _rref(rows, ncol)
    free = [c for c in range(ncol) if c not in set(piv)]
    basis = []
    for f in free:
        x = [Fraction(0)] * ncol
        x[f] = Fraction(1)
        for i, c in enumerate(piv):
            x[c] = -rows[i][f]
        basis.append(x)
    return basis


def _to_ints(w):
    den = 1
    for v in w:
        den = den * v.denominator // math.gcd(den, v.denominator)
    wi = [int(v * den) for v in w]
    g = 0
    for v in wi:
        g = math.gcd(g, abs(v))
    if g > 1:
        wi = [v // g for v in wi]
    return wi


def exact_positive_kernel(V, sup):
    """Integer w > 0 on `sup` with sum_i w_i V[i] = 0, or None.

    Uses the exact null space of V_sup^T.  A one-dimensional kernel is the
    common case and is decided outright; otherwise the caller trims.
    """
    k = len(sup)
    if k == 0:
        return None
    A = []
    for j in range(V.shape[1]):
        row = [Fraction(int(V[i][j])) for i in sup]
        if any(row):
            A.append(row)
    ns = exact_nullspace(A, k)
    if len(ns) != 1:
        return None
    w = ns[0]
    if all(v < 0 for v in w):
        w = [-v for v in w]
    if any(v <= 0 for v in w):
        return None
    return _to_ints(w)


# ----------------------------------------------------------------------
# (G) the Gordan vector
# ----------------------------------------------------------------------

def find_gordan(chi, sup, tol=1e-9, max_trim=8, sys=None):
    """Search for a Gordan vector.  Returns (cert, info).

    cert = {'terms': [(identity index, big, small, weight), ...], 'level': ...}
    """
    S = sys if sys is not None else sup.system(chi)
    info = {'level': sup.level, 'nrows': int(S.V.shape[0]),
            'nident': len(sup.idents), 'lp': None}
    if S.contradiction is not None:
        # every term of one identity carries the same sign: a sum of
        # strictly positive numbers cannot vanish.  The Gordan vector is the
        # trivial one over that identity's own inequalities -- but there are
        # none (no odd term), so we report it separately.
        info['all_same_identity'] = S.contradiction
    if S.V.shape[0] == 0:
        return None, info
    m = S.V.shape[0]
    Aeq = np.vstack([S.V.T.astype(np.float64), np.ones((1, m))])
    beq = np.zeros(sup.M + 1)
    beq[-1] = 1.0
    res = linprog(np.zeros(m), A_eq=Aeq, b_eq=beq, bounds=[(0, None)] * m,
                  method='highs')
    info['lp'] = int(res.status)
    if not res.success:
        return None, info
    lam = np.asarray(res.x)
    order = np.argsort(-lam)
    supp = [int(i) for i in order if lam[i] > tol]
    info['lp_support'] = len(supp)
    if not supp:
        return None, info
    for trim in range(min(max_trim, len(supp))):
        cand = supp[:len(supp) - trim] if trim else supp
        w = exact_positive_kernel(S.V, cand)
        if w is not None:
            terms = [(S.meta[i][0], S.meta[i][1], S.meta[i][2], int(x))
                     for i, x in zip(cand, w)]
            info['support'] = len(cand)
            return {'terms': terms, 'level': sup.level}, info
    info['exact_failed'] = True
    return None, info


# ----------------------------------------------------------------------
# (W) the exact witness that NO Gordan vector exists
# ----------------------------------------------------------------------

def find_witness(chi, sup, denom=(1 << 20, 1 << 30, 1 << 40), sys=None):
    """Search for exact integer u with V u > 0 componentwise.

    Returns (u_int, info).  u_int is a list of M python ints; the scale is
    irrelevant (the system is homogeneous).  A returned u PROVES, by
    Gordan's theorem, that the class has no final polynomial over this
    support -- in particular at level L0, no biquadratic final polynomial.
    """
    S = sys if sys is not None else sup.system(chi)
    info = {'level': sup.level, 'nrows': int(S.V.shape[0]), 'lp': None}
    if S.contradiction is not None:
        info['all_same_identity'] = S.contradiction
        return None, info               # non-realizable outright
    m, M = S.V.shape
    if m == 0:
        info['empty'] = True
        return None, info
    # maximise the margin t subject to V u >= t, |u| <= 1, t <= 1
    # variables: u (M), t (1)
    A_ub = np.hstack([-S.V.astype(np.float64), np.ones((m, 1))])
    b_ub = np.zeros(m)
    c = np.zeros(M + 1)
    c[-1] = -1.0
    bounds = [(-1.0, 1.0)] * M + [(None, 1.0)]
    res = linprog(c, A_ub=A_ub, b_ub=b_ub, bounds=bounds, method='highs')
    info['lp'] = int(res.status)
    if not res.success:
        return None, info
    u = np.asarray(res.x[:M])
    t = float(res.x[M])
    info['margin'] = t
    if t <= 0:
        return None, info
    Vi = S.V.astype(np.int64)
    for D in denom:
        ui = np.rint(u * D).astype(np.int64)
        val = Vi @ ui
        if (val > 0).all():
            g = 0
            for v in ui.tolist():
                g = math.gcd(g, abs(int(v)))
            if g > 1:
                ui = ui // g
            info['denom'] = int(D)
            info['min_slack'] = int((S.V.astype(np.int64) @ ui).min())
            return [int(v) for v in ui], info
    info['round_failed'] = True
    return None, info


# ----------------------------------------------------------------------
# certificate records
# ----------------------------------------------------------------------

def gordan_record(n, r, chi_str, cert, sup):
    """The omopen NON_REALIZABLE record for a Gordan vector."""
    terms = []
    for (q, big, small, w) in cert['terms']:
        idt = sup.idents[q]
        terms.append({'rel': idt.spec, 'big': int(big), 'small': int(small),
                      'w': int(w)})
    return {'n': n, 'r': r, 'chi': chi_str, 'verdict': 'NON_REALIZABLE',
            'method': 'GORDAN', 'level': cert['level'], 'terms': terms}


def gordan_record_bfp(n, r, chi_str, cert, sup):
    """The same certificate in ai/omreal/checkcert.py's `bfp` schema.

    Only possible when every identity used is a three-term relation, i.e.
    at level L0 -- which is the point: a level-0 certificate produced here
    can be handed to the project's existing independent checker.
    """
    out = []
    for (q, big, small, w) in cert['terms']:
        idt = sup.idents[q]
        if idt.spec['kind'] != 'gp3':
            return None
        out.append({'L': list(idt.spec['L']), 'abcd': list(idt.spec['abcd']),
                    'big': int(big), 'small': int(small), 'w': int(w)})
    return {'n': n, 'r': r, 'chi': chi_str, 'verdict': 'NON_REALIZABLE',
            'bfp': out}


def witness_record(n, r, chi_str, u, sup):
    """The certificate that NO final polynomial of Gordan type exists.

    `families` is carried explicitly, not the level name: the checker must
    rebuild the whole inequality system itself from the families, so the
    record cannot understate the support it claims to have ruled out.
    """
    return {'n': n, 'r': r, 'chi': chi_str, 'verdict': 'NO_FINAL_POLYNOMIAL',
            'method': 'GORDAN_WITNESS', 'level': sup.level,
            'families': list(LEVELS[sup.level]), 'u': list(u)}


def contradiction_record(n, r, chi_str, q, sup):
    """One identity all of whose terms carry the same sign under chi."""
    idt = sup.idents[q]
    return {'n': n, 'r': r, 'chi': chi_str, 'verdict': 'NON_REALIZABLE',
            'method': 'MONOCHROME', 'level': sup.level, 'rel': idt.spec}
