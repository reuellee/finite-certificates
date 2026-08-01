#!/usr/bin/env python3
"""Realization search: chirotope -> an explicit INTEGER r x n matrix.

The search is a heuristic; the OUTPUT is not.  Whatever the heuristic
returns is rationalised and then verified with exact integer determinants,
so a returned matrix is a complete certificate of realizability and a
failure is only a failure of the search.

Method
------
Every bracket is multilinear, so with all columns but one held fixed the
conditions on the remaining column x_p are HOMOGENEOUS LINEAR:

    for each basis B containing p,   sigma_B * <v_{B\\p}, x_p>  >  0,
    v_S defined by  det(x_{s_1},...,x_{s_{r-1}}, y) = <v_S, y>,
    sigma_B = chi(B) * (-1)^(r-1-position of p in B).

So placing one point is "find a point in an open polyhedral cone", solved
here by a log-barrier Newton homotopy (`cone_center`) that returns the
ANALYTIC CENTRE of the cone -- deliberately, not a vertex: a well-centred
point keeps every bracket far from zero, which is what makes the later
rounding to rationals succeed with small denominators.

  build      place points r+1..n one at a time (each an easy cone problem)
  repair     coordinate descent: re-place each point in turn against all
             C(n-1,r-1) of its constraints until no bracket is wrong
  retry      random relabelling + random restarts

`cone_center` also returns a best-effort point when the cone is empty (the
minimiser of a smoothed hinge), which is what makes the repair sweep a
genuine descent on the number of wrong brackets rather than a no-op.
"""

import math
from itertools import combinations

import numpy as np


# ======================================================================
# exact integer determinants
# ======================================================================

def _det_int64(A):
    """(K,r,r) int64 -> (K,) int64 determinants, r in {1,2,3,4}."""
    r = A.shape[1]
    if r == 1:
        return A[:, 0, 0]
    if r == 2:
        return A[:, 0, 0] * A[:, 1, 1] - A[:, 0, 1] * A[:, 1, 0]
    if r == 3:
        return (A[:, 0, 0] * (A[:, 1, 1] * A[:, 2, 2] - A[:, 1, 2] * A[:, 2, 1])
                - A[:, 0, 1] * (A[:, 1, 0] * A[:, 2, 2] - A[:, 1, 2] * A[:, 2, 0])
                + A[:, 0, 2] * (A[:, 1, 0] * A[:, 2, 1] - A[:, 1, 1] * A[:, 2, 0]))
    if r == 4:
        def m2(i, j, ra, rb):
            return A[:, ra, i] * A[:, rb, j] - A[:, ra, j] * A[:, rb, i]
        return (m2(0, 1, 0, 1) * m2(2, 3, 2, 3)
                - m2(0, 2, 0, 1) * m2(1, 3, 2, 3)
                + m2(0, 3, 0, 1) * m2(1, 2, 2, 3)
                + m2(1, 2, 0, 1) * m2(0, 3, 2, 3)
                - m2(1, 3, 0, 1) * m2(0, 2, 2, 3)
                + m2(2, 3, 0, 1) * m2(0, 1, 2, 3))
    raise NotImplementedError('rank %d' % r)


def _det_py(rows):
    """Exact determinant of a small square matrix of Python ints."""
    m = [list(map(int, row)) for row in rows]
    k = len(m)
    sign, det = 1, 1
    prev = 1
    for i in range(k - 1):
        if m[i][i] == 0:
            for j in range(i + 1, k):
                if m[j][i] != 0:
                    m[i], m[j] = m[j], m[i]
                    sign = -sign
                    break
            else:
                return 0
        for j in range(i + 1, k):
            for l in range(i + 1, k):
                m[j][l] = (m[j][l] * m[i][i] - m[j][i] * m[i][l]) // prev
        prev = m[i][i]
    det = m[k - 1][k - 1]
    return sign * det


def exact_bracket_signs(Z, geom):
    """Z: (r,n) integer matrix -> (M,) int8 signs, or None if some
    bracket vanishes (the configuration is then not uniform)."""
    Z = np.asarray(Z, dtype=object) if Z.dtype == object else np.asarray(Z)
    r, n = geom.r, geom.n
    mx = max(abs(int(v)) for v in np.asarray(Z).ravel())
    bound = math.factorial(r) * (mx ** r if mx else 1)
    idx = geom.BAS                                    # (M,r) 0-based
    if bound < (1 << 62) and Z.dtype != object:
        A = np.asarray(Z, dtype=np.int64)[:, idx]     # (r, M, r)
        A = np.ascontiguousarray(A.transpose(1, 0, 2))
        d = _det_int64(A)
        if (d == 0).any():
            return None
        return np.where(d > 0, np.int8(1), np.int8(-1))
    Zl = [[int(v) for v in row] for row in np.asarray(Z)]
    out = np.empty(geom.M, dtype=np.int8)
    for j, B in enumerate(geom.bases0):
        d = _det_py([[Zl[i][b] for b in B] for i in range(r)])
        if d == 0:
            return None
        out[j] = 1 if d > 0 else -1
    return out


# ======================================================================
# geometry tables (colex, 0-based elements)
# ======================================================================

class Geom(object):
    def __init__(self, n, r):
        self.n, self.r = n, r
        bas = sorted(combinations(range(n), r), key=lambda t: tuple(reversed(t)))
        self.bases0 = bas
        self.M = len(bas)
        self.BAS = np.array(bas, dtype=np.int64)
        self.BMAX = self.BAS.max(axis=1)
        self.bidx = {B: j for j, B in enumerate(bas)}
        # per point: bases containing it, the other r-1 elements, position sign
        self.pt_b, self.pt_rest, self.pt_sgn = [], [], []
        for p in range(n):
            bs, rest, sg = [], [], []
            for j, B in enumerate(bas):
                if p in B:
                    k = B.index(p)
                    bs.append(j)
                    rest.append([x for x in B if x != p])
                    sg.append(-1 if ((r - 1 - k) & 1) else 1)
            self.pt_b.append(np.array(bs, dtype=np.int64))
            self.pt_rest.append(np.array(rest, dtype=np.int64))
            self.pt_sgn.append(np.array(sg, dtype=np.int8))
        # prefix masks: which of point p's bases live inside {0..q}
        self.pt_pref = []
        for p in range(n):
            mx = self.pt_rest[p].max(axis=1) if len(self.pt_rest[p]) else \
                np.zeros(0, dtype=np.int64)
            self.pt_pref.append(mx)

    def relabel(self, chi, perm):
        """The chirotope of the configuration whose element i is the old
        element perm[i]:  (perm.chi)(B) = sortsign(perm[B]) * chi(sorted perm[B]).

        So if Z realizes chi then Z[:, perm] realizes relabel(chi, perm),
        and conversely a matrix W realizing relabel(chi, perm) gives a
        matrix Z realizing chi via  Z[:, perm] = W.
        """
        out = np.empty(self.M, dtype=np.int8)
        for j, B in enumerate(self.bases0):
            t = [int(perm[x]) for x in B]
            sg = 1
            for a in range(1, len(t)):
                b = a
                while b > 0 and t[b - 1] > t[b]:
                    t[b - 1], t[b] = t[b], t[b - 1]
                    sg = -sg
                    b -= 1
            out[j] = sg * chi[self.bidx[tuple(t)]]
        return out


# ======================================================================
# the cone solver
# ======================================================================

def cone_center(A, z0=1.0, zmin=1e-10, shrink=0.1, newton=8, patience=3):
    """Find x with A x > 0 (rows of A need not be normalised).

    Returns (x, feasible).  x is the analytic centre of {A x > -z} for the
    smallest z reached, so when feasible=False it is still a sensible
    best-effort direction (few and shallow violations).

    Maximises  f(x) = sum_i log(a_i.x + z) - (m/2)|x|^2  by damped Newton,
    halving/shrinking z.  x = 0 is strictly feasible for every z > 0, so
    the homotopy always has a start.
    """
    A = np.asarray(A, dtype=np.float64)
    m, d = A.shape
    if m == 0:
        return np.ones(d), True
    nrm = np.linalg.norm(A, axis=1)
    good = nrm > 0
    if not good.all():
        # a zero row means the constraint cannot be satisfied at all
        return np.zeros(d), False
    An = A / nrm[:, None]
    x = np.zeros(d)
    eye = np.eye(d)
    z = float(z0)
    bestx, bestv, stall = x, m + 1, 0
    while True:
        for _ in range(newton):
            s = An @ x + z
            if s.min() <= 0:
                break
            inv = 1.0 / s
            g = An.T @ inv - m * x
            H = (An.T * (inv * inv)) @ An + m * eye
            try:
                dx = np.linalg.solve(H, g)
            except np.linalg.LinAlgError:
                break
            t = 1.0
            for _ in range(40):
                if (An @ (x + t * dx) + z).min() > 0:
                    break
                t *= 0.5
            else:
                break
            x = x + t * dx
            if np.linalg.norm(t * dx) < 1e-14 * (1.0 + np.linalg.norm(x)):
                break
        s0 = An @ x
        if s0.min() > 0:
            return x, True
        # keep the best-effort point: fewest violated constraints seen so
        # far.  Taking the LAST iterate instead would return something near
        # 0 (the regulariser wins once the cone is provably empty), which
        # makes the repair sweep a no-op rather than a descent.
        v = int((s0 <= 0).sum())
        if v < bestv:
            bestv, bestx, stall = v, x.copy(), 0
        else:
            stall += 1
            if stall >= patience:
                return bestx, False       # the cone looks empty; stop paying
        if z <= zmin:
            return bestx, False
        z = max(z * shrink, zmin * 0.5)


# ======================================================================
# realization search
# ======================================================================

def cone_push(A, j, t, x, newton=14, mu=None):
    """Maximise  t*(a_j.x) + sum_{i!=j} log(a_i.x) - (mu/2)|x|^2  from a
    point x with a_i.x > 0 for all i != j.

    This is the wall-crossing step.  When the search stalls with exactly one
    bracket wrong it has realized a MUTANT of the target: every sign is
    right except at one basis j.  Crossing that wall means driving a_j.x
    through zero while every other constraint stays strictly satisfied,
    which is what this objective does as t grows.  Returns x, or None.
    """
    A = np.asarray(A, dtype=np.float64)
    m, d = A.shape
    nrm = np.linalg.norm(A, axis=1)
    if (nrm <= 0).any():
        return None
    An = A / nrm[:, None]
    keep = np.ones(m, dtype=bool)
    keep[j] = False
    B = An[keep]
    if mu is None:
        mu = float(m)
    x = np.array(x, dtype=np.float64)
    nx = np.linalg.norm(x)
    if nx < 1e-12:
        return None
    x = x / nx
    if (B @ x).min() <= 0:
        return None
    eye = np.eye(d)
    aj = An[j]
    for _ in range(newton):
        s = B @ x
        inv = 1.0 / s
        g = t * aj + B.T @ inv - mu * x
        H = (B.T * (inv * inv)) @ B + mu * eye
        try:
            dx = np.linalg.solve(H, g)
        except np.linalg.LinAlgError:
            return None
        step = 1.0
        for _ in range(40):
            if (B @ (x + step * dx)).min() > 0:
                break
            step *= 0.5
        else:
            break
        x = x + step * dx
        if np.linalg.norm(step * dx) < 1e-14 * (1.0 + np.linalg.norm(x)):
            break
    return x if (B @ x).min() > 0 else None


def _cross_wall(chi, X, geom, rng, rounds=3,
                ts=(2.0, 8.0, 32.0, 128.0, 512.0, 2048.0, 8192.0, 32768.0)):
    """With exactly one bracket wrong, try to push through that wall."""
    bad = _wrong(chi, X, geom)
    if len(bad) != 1:
        return False
    j = int(bad[0])
    pts = list(geom.bases0[j])
    others = [p for p in range(geom.n) if p not in pts]
    for t in ts:
        for _ in range(rounds):
            for p in pts:
                A, bs = _constraints(chi, X, geom, p, with_bases=True)
                w = np.flatnonzero(bs == j)
                if len(w) != 1:
                    continue
                y = cone_push(A, int(w[0]), t, X[:, p])
                if y is not None:
                    X[:, p] = y / max(np.linalg.norm(y), 1e-300)
            if len(_wrong(chi, X, geom)) == 0:
                return True
            for p in others:
                A = _constraints(chi, X, geom, p)
                y, ok = cone_center(A)
                ny = np.linalg.norm(y)
                if ok and ny > 1e-12:
                    X[:, p] = y / ny
            bad = _wrong(chi, X, geom)
            if len(bad) == 0:
                return True
            if len(bad) != 1 or int(bad[0]) != j:
                return False          # lost the mutant; let the sweep resume
    return False


def _constraints(chi, X, geom, p, upto=None, with_bases=False):
    """Rows a_i with the conditions on column p being a_i . x_p > 0."""
    rest = geom.pt_rest[p]
    bs = geom.pt_b[p]
    sg = geom.pt_sgn[p]
    if upto is not None:
        keep = geom.pt_pref[p] <= upto
        rest, bs, sg = rest[keep], bs[keep], sg[keep]
    if len(bs) == 0:
        z = np.zeros((0, geom.r))
        return (z, bs) if with_bases else z
    r = geom.r
    Y = X[:, rest]                                # (r, K, r-1)
    Y = np.ascontiguousarray(Y.transpose(1, 0, 2))  # (K, r, r-1)
    K = Y.shape[0]
    V = np.empty((K, r))
    keeprows = np.arange(r)
    for mm in range(r):
        sub = Y[:, keeprows != mm, :]             # (K, r-1, r-1)
        V[:, mm] = np.linalg.det(sub) * (-1.0 if ((mm + r - 1) & 1) else 1.0)
    coef = (sg.astype(np.float64) * chi[bs].astype(np.float64))
    out = V * coef[:, None]
    return (out, bs) if with_bases else out


def _wrong(chi, X, geom, upto=None):
    """indices of bases whose float bracket sign disagrees with chi.
    With `upto` set, only bases inside {0..upto} are considered."""
    sel = geom.BAS if upto is None else geom.BAS[geom.BMAX <= upto]
    A = np.ascontiguousarray(X[:, sel].transpose(1, 0, 2))
    d = np.linalg.det(A)
    ref = chi if upto is None else chi[geom.BMAX <= upto]
    return np.flatnonzero(np.sign(d) != ref)


def _repair_prefix(chi, X, geom, k, rng, sweeps=20, jitter=0.6):
    """Move to a DIFFERENT point of the realization space of chi restricted
    to elements {0..k-1}: jitter those columns, then coordinate-descend
    until every bracket inside the prefix is right again.

    This is what makes the builder a real backtracking search -- when
    element k cannot be placed on top of the current sub-realization, the
    fix is to pick another sub-realization, not another random start.
    """
    saved = X.copy()
    for p in range(k):
        X[:, p] += jitter * rng.normal(size=geom.r)
        X[:, p] /= max(np.linalg.norm(X[:, p]), 1e-300)
    for _ in range(sweeps):
        if len(_wrong(chi, X, geom, upto=k - 1)) == 0:
            return True
        for p in rng.permutation(k):
            A = _constraints(chi, X, geom, int(p), upto=k - 1)
            x, ok = cone_center(A)
            nx = np.linalg.norm(x)
            if nx > 1e-12:
                X[:, int(p)] = x / nx
    if len(_wrong(chi, X, geom, upto=k - 1)) == 0:
        return True
    X[:, :] = saved
    return False


def _build(chi, geom, rng, rerolls=6):
    """Place elements r..n-1 one at a time, backtracking on the prefix."""
    n, r = geom.n, geom.r
    X = np.zeros((r, n))
    X[:, :r] = np.eye(r)
    for p in range(r, n):
        placed = False
        for attempt in range(rerolls + 1):
            A = _constraints(chi, X, geom, p, upto=p)
            x, ok = cone_center(A)
            if ok:
                X[:, p] = x / max(np.linalg.norm(x), 1e-300)
                placed = True
                break
            if attempt < rerolls:
                _repair_prefix(chi, X, geom, p, rng)
        if not placed:
            nx = np.linalg.norm(x)
            X[:, p] = (x / nx) if nx > 1e-12 else rng.normal(size=r)
    return X


def _search_float(chi, geom, rng, sweeps=40, rerolls=6, wall_budget=4):
    n, r = geom.n, geom.r
    X = _build(chi, geom, rng, rerolls=rerolls)
    best = len(_wrong(chi, X, geom))
    if best == 0:
        return X, 0
    bestX = X.copy()
    stall = 0
    for _ in range(sweeps):
        for p in rng.permutation(n):
            A = _constraints(chi, X, geom, int(p))
            x, ok = cone_center(A)
            nx = np.linalg.norm(x)
            if nx > 1e-12:
                X[:, int(p)] = x / nx
        w = len(_wrong(chi, X, geom))
        if w == 1 and wall_budget > 0:
            wall_budget -= 1
            if _cross_wall(chi, X, geom, rng):
                return X, 0
            w = len(_wrong(chi, X, geom))
        if w == 0:
            return X, 0
        if w < best:
            best, bestX, stall = w, X.copy(), 0
        else:
            stall += 1
            if stall >= 3:
                # kick the points that carry the wrong brackets
                bad = _wrong(chi, X, geom)
                pts = np.unique(geom.BAS[bad].ravel())
                X = bestX.copy()
                for p in pts:
                    X[:, p] += 0.35 * rng.normal(size=r)
                    X[:, p] /= max(np.linalg.norm(X[:, p]), 1e-300)
                stall = 0
    return bestX, best


def _rationalise(X, chi, geom, denoms=(8, 32, 256, 4096, 65536,
                                       1 << 20, 1 << 26, 1 << 32, 1 << 40)):
    col = np.abs(X).max(axis=0)
    col[col == 0] = 1.0
    Xs = X / col
    for D in denoms:
        Z = np.rint(Xs * D)
        if not np.isfinite(Z).all() or np.abs(Z).max() >= 2.0 ** 53:
            break
        Zi = Z.astype(np.int64)
        for j in range(Zi.shape[1]):
            g = np.gcd.reduce(np.abs(Zi[:, j]))
            if g > 1:
                Zi[:, j] //= g
        if (np.abs(Zi).max(axis=0) == 0).any():
            continue
        s = exact_bracket_signs(Zi, geom)
        if s is not None and np.array_equal(s, chi):
            return Zi, D
    return None, None


def realize(chi, geom, tries=6, seed=0, sweeps=40, rerolls=6, wall_budget=4):
    """Try to realize the chirotope `chi` (int8 +-1, colex order).

    Returns (Z, info) with Z an integer (r,n) numpy array whose exact
    bracket signs equal chi, or (None, info).
    """
    chi = np.asarray(chi, dtype=np.int8)
    g0 = int(chi[0])
    chin = (chi * g0).astype(np.int8)             # normalise chi[0] = +1
    rng = np.random.default_rng(seed)
    info = {'tries': 0, 'best_wrong': geom.M, 'denom': None}
    n = geom.n
    for t in range(tries):
        if t == 0:
            perm = np.arange(n)
            work = chin
        else:
            perm = rng.permutation(n)
            work = geom.relabel(chin, perm)
            if work[0] < 0:
                work = (-work).astype(np.int8)
        info['tries'] = t + 1
        X, wrong = _search_float(work, geom, rng, sweeps=sweeps, rerolls=rerolls,
                                 wall_budget=wall_budget)
        info['best_wrong'] = min(info['best_wrong'], wrong)
        if wrong:
            continue
        Zi, D = _rationalise(X, work, geom)
        if Zi is None:
            continue
        info['denom'] = D
        # undo the relabelling: column of element x is column perm^-1... ;
        # work = perm.chin means work's element i is chin's element perm[i]
        Z = np.empty_like(Zi)
        Z[:, perm] = Zi
        # undo any global-sign flips: recheck against the ORIGINAL chi
        s = exact_bracket_signs(Z, geom)
        if s is None:
            continue
        if np.array_equal(s, chi):
            return Z, info
        if np.array_equal(-s, chi):
            Z = Z.copy()
            Z[0, :] *= -1
            return Z, info
    return None, info
