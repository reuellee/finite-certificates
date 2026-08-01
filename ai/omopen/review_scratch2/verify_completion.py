#!/usr/bin/env python3
"""REVIEW (Fable): the completion-LP completeness claim (weapon A).

My own construction throughout: the constraint row for basis B containing p
is  chi(B) * v  with  v[m] = det4(X with column p := e_m), columns taken in
sorted basis order -- computed directly from the definition, so no cofactor
sign conventions are shared with weaponA.completion_rows.

  C1  POSITIVE completeness: for every shipped certificate Z and every
      p in 1..9, the deletion Y = Z minus column p must admit a completion,
      and the LP must find margin > 0; my own integer rounding must produce
      an exact completion whose full 126-bracket chirotope (my det code)
      equals chi.  126 x 9 = 1134 instances.
  C2  NEGATIVE direction, made exact: manufacture infeasible instances by
      demanding a DIFFERENT open class's signs on the completion (Y from
      cert i, demands from cert j).  Whenever the float LP reports margin
      <= 0, reconstruct an EXACT rational Farkas/Gordan certificate
      w >= 0, w != 0, sum_i w_i A_i = 0 (Fraction arithmetic), which proves
      the strict cone really is empty -- the float "no" verified exactly.
"""
import json
import os
import sys
from fractions import Fraction
from itertools import combinations, permutations

for _v in ('OMP_NUM_THREADS', 'MKL_NUM_THREADS', 'OPENBLAS_NUM_THREADS',
           'NUMEXPR_NUM_THREADS'):
    os.environ.setdefault(_v, '1')
sys.dont_write_bytecode = True

import numpy as np                                          # noqa: E402
from scipy.optimize import linprog                          # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
OMOPEN = os.path.dirname(HERE)
DATA = os.path.join(OMOPEN, 'data')
N, R = 9, 4

BASES = sorted(combinations(range(1, N + 1), R), key=lambda t: t[::-1])
BIDX = {B: j for j, B in enumerate(BASES)}
PERMS4 = [(p, (1 if sum(1 for i in range(4) for j in range(i + 1, 4)
                        if p[i] > p[j]) % 2 == 0 else -1))
          for p in permutations(range(4))]


def det4(cols):
    t = 0
    for p, s in PERMS4:
        t += s * cols[0][p[0]] * cols[1][p[1]] * cols[2][p[2]] * cols[3][p[3]]
    return t


def completion_rows_mine(Mx, chi, p):
    """chi: list of +-1 in colex order; p: element 1..9.  Rows are exact
    python ints; row.x > 0 for all rows <=> setting column p := x gives
    every basis containing p its demanded sign."""
    cols = [[int(Mx[i][j]) for i in range(4)] for j in range(9)]
    rows = []
    for j, B in enumerate(BASES):
        if p not in B:
            continue
        v = []
        for m in range(4):
            e = [0, 0, 0, 0]
            e[m] = 1
            v.append(det4([e if b == p else cols[b - 1] for b in B]))
        c = chi[j]
        rows.append([c * t for t in v])
    return rows


def lp_margin(rows):
    A = np.array(rows, dtype=np.float64)
    nrm = np.linalg.norm(A, axis=1)
    An = A / nrm[:, None]
    m = len(rows)
    Aub = np.hstack([-An, np.ones((m, 1))])
    c = np.zeros(5)
    c[-1] = -1.0
    res = linprog(c, A_ub=Aub, b_ub=np.zeros(m),
                  bounds=[(-1.0, 1.0)] * 4 + [(None, 1.0)], method='highs')
    if not res.success:
        return None, None
    return np.asarray(res.x[:4]), float(res.x[4])


def round_exact(rows, x):
    import math
    mx = float(np.abs(x).max())
    if mx <= 0:
        return None
    xs = x / mx
    for D in (1 << 6, 1 << 10, 1 << 14, 1 << 18, 1 << 24, 1 << 30, 1 << 38):
        y = [int(v) for v in np.rint(xs * D)]
        if not any(y):
            continue
        g = 0
        for v in y:
            g = math.gcd(g, abs(v))
        if g > 1:
            y = [v // g for v in y]
        if all(sum(a * b for a, b in zip(row, y)) > 0 for row in rows):
            return y
    return None


certs = [json.loads(l) for l in open(os.path.join(DATA,
                                                  'certs_realizable.jsonl'))]


def chi_list(s):
    return [1 if ch == '+' else -1 for ch in s]


def chi_of_matrix(Mx):
    cols = [[Mx[i][j] for i in range(4)] for j in range(9)]
    out = []
    for B in BASES:
        d = det4([cols[b - 1] for b in B])
        if d == 0:
            return None
        out.append('+' if d > 0 else '-')
    return ''.join(out)


# ---- C1 --------------------------------------------------------------
tot = ok_margin = ok_complete = 0
for c in certs:
    chi = chi_list(c['chi'])
    Mx = [list(map(int, row)) for row in c['matrix']]
    for p in range(1, 10):
        tot += 1
        rows = completion_rows_mine(Mx, chi, p)
        assert len(rows) == 56
        x, t = lp_margin(rows)
        if x is None or t <= 0:
            print('    C1 FAIL: cert chi %s... p=%d margin %s'
                  % (c['chi'][:16], p, t))
            continue
        ok_margin += 1
        y = round_exact(rows, x)
        if y is None:
            print('    C1 FAIL: rounding failed at p=%d' % p)
            continue
        M2 = [row[:] for row in Mx]
        for i in range(4):
            M2[i][p - 1] = y[i]
        if chi_of_matrix(M2) == c['chi']:
            ok_complete += 1
        else:
            print('    C1 FAIL: completed matrix wrong at p=%d' % p)
print('  [%s] C1: completion LP feasible with margin > 0 on %d/%d '
      '(cert, p) instances; exact integer completion re-verified on %d/%d'
      % ('ok ' if ok_margin == tot == ok_complete else 'FAIL',
         ok_margin, tot, ok_complete, tot))

# ---- C2 --------------------------------------------------------------
def exact_farkas(rows, seed=0):
    """w >= 0 rational, not all 0, with sum w_i rows_i = 0; via float LP on
    the support then exact Fraction elimination.  Retries with random
    objectives to land on different vertices.  Returns w or None."""
    A = np.array(rows, dtype=np.float64)
    m = len(rows)
    Aeq = np.vstack([A.T, np.ones((1, m))])
    beq = np.zeros(5)
    beq[-1] = 1.0
    rndl = np.random.default_rng(seed)
    for attempt in range(8):
        obj = np.zeros(m) if attempt == 0 else rndl.random(m)
        res = linprog(obj, A_eq=Aeq, b_eq=beq, bounds=[(0, None)] * m,
                      method='highs')
        if not res.success:
            continue
        w = _reconstruct(rows, np.asarray(res.x))
        if w is not None:
            return w
    return None


def _reconstruct(rows, lam):
    sup = [i for i in np.argsort(-lam) if lam[i] > 1e-9]
    # exact: solve [rows_sup^T; 1] w = [0; 1] over Q
    for trim in range(0, min(6, len(sup))):
        cand = sup[:len(sup) - trim] if trim else sup
        k = len(cand)
        Aq = [[Fraction(rows[i][j]) for i in cand] for j in range(4)]
        Aq.append([Fraction(1)] * k)
        rhs = [Fraction(0)] * 4 + [Fraction(1)]
        # gaussian elimination
        mm = len(Aq)
        piv = []
        r = 0
        for cc in range(k):
            pr = None
            for i in range(r, mm):
                if Aq[i][cc]:
                    pr = i
                    break
            if pr is None:
                continue
            Aq[r], Aq[pr] = Aq[pr], Aq[r]
            rhs[r], rhs[pr] = rhs[pr], rhs[r]
            inv = 1 / Aq[r][cc]
            Aq[r] = [v * inv for v in Aq[r]]
            rhs[r] = rhs[r] * inv
            for i in range(mm):
                if i != r and Aq[i][cc]:
                    f = Aq[i][cc]
                    Aq[i] = [a - f * b for a, b in zip(Aq[i], Aq[r])]
                    rhs[i] = rhs[i] - f * rhs[r]
            piv.append(cc)
            r += 1
        for i in range(r, mm):
            if rhs[i] != 0 and not any(Aq[i]):
                break
        else:
            if len(piv) == k:
                w = [Fraction(0)] * k
                for i, cc in enumerate(piv):
                    w[cc] = rhs[i]
                if all(v >= 0 for v in w) and any(v > 0 for v in w):
                    # exact re-check
                    for j in range(4):
                        if sum(w[t] * rows[cand[t]][j]
                               for t in range(k)) != 0:
                            break
                    else:
                        return [(cand[t], w[t]) for t in range(k)
                                if w[t] > 0]
    return None


import random
rnd = random.Random(2026)
n_neg = n_inf = n_exact = 0
tries = 0
while n_inf < 12 and tries < 60:
    tries += 1
    i, j = rnd.sample(range(126), 2)
    p = rnd.randint(1, 9)
    chi_j = chi_list(certs[j]['chi'])
    Mx = [list(map(int, row)) for row in certs[i]['matrix']]
    rows = completion_rows_mine(Mx, chi_j, p)
    x, t = lp_margin(rows)
    n_neg += 1
    if x is None or t <= 1e-9:
        n_inf += 1
        w = exact_farkas(rows)
        if w is not None:
            n_exact += 1
print('  [%s] C2: %d cross-class instances tried, %d infeasible by the '
      'float LP, %d of those PROVEN empty by an exact rational Farkas '
      'certificate' % ('ok ' if n_inf and n_exact == n_inf else 'WARN',
                       n_neg, n_inf, n_exact))
print('\nCOMPLETION-LP VERIFICATION DONE')
