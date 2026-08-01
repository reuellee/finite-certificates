#!/usr/bin/env python3
"""WEAPON A -- realization search v2, built around ONE-POINT COMPLETION.

THE REFORMULATION
=================
The sweep realizes a class by crossing one wall from its spanning-tree
parent's realization, with a heuristic barrier method (`realize.cone_push`)
doing the crossing and a bounded repair ladder behind it.  When that ladder
fails the class is OPEN.  Piling on more of the same budget is not a
different experiment, so this file changes the question.

Fix an element p.  Let Y be an integer 4 x 8 configuration realizing the
DELETION chi\\p.  Every bracket of chi that avoids p is then already
correct, and the C(8,3) = 56 brackets that contain p are, as functions of
the missing column x_p, HOMOGENEOUS LINEAR:

    for each basis B = {p} u S,    sigma_B <v_S, x_p>  >  0,
    v_S from  det(x_{s1}, x_{s2}, x_{s3}, y) = <v_S, y>.

So "does this 8-point configuration extend to a realization of chi?" is a
single LP in four variables with 56 constraints -- and the LP is COMPLETE:
if its optimum margin is <= 0 then NO x_p completes this Y, full stop.  The
search therefore has an exact oracle at the last step, and the only
heuristic left is which Y to try.

Three things follow, and they are the reason this is stronger than more
budget:

* **Crossing a wall is the special case.**  If X realizes the mutant
  mu_j(chi) and p is one of the four elements of the flipped basis B_j,
  then X with column p deleted realizes chi\\p exactly.  So every crossing
  the sweep attempts is one (Y, p) pair here, and the LP answers it
  definitively where `cone_push` only answers it optimistically.
* **The deletions are easy, and there are nine of them.**  chi\\p is a
  uniform rank-4 chirotope on EIGHT elements; realizing one costs a few
  milliseconds where realizing chi costs seconds and usually fails.  Each
  fresh seed gives a genuinely different point of a 9-dimensional
  realization space, so Y can be sampled in bulk.  For every OPEN class all
  nine deletions are realizable (`ai/omminor/MINOR_THEORY.md` s4.3 measured
  451 of 451), so this source never runs dry.
* **Everything stays exact.**  Y is integer; the constraint rows are exact
  3x3 integer determinants; the LP is used only to propose x_p, which is
  rounded to integers and re-checked against the exact rows.  A float never
  touches a verdict.

SOURCES OF Y, in the order tried
--------------------------------
  T1  the sweep's stored realization of the class's TREE PARENT, pulled
      back through the witness group element -- an exact integer mutant of
      chi, restricted.
  T2  the same for every already-realized TREE CHILD.  (The witness arrays
      hand us the group element for both, so no canonicalization and no
      convention risk; the transported matrix is nevertheless re-checked
      bracket by bracket before use.)
  S1  fresh realizations of chi\\p for each p, many seeds.
  S2  fresh realizations of each MUTANT mu_j(chi), restricted.
  S3  a random walk inside the realization space of chi\\p: re-place one
      column at a time at the optimum of a random linear objective subject
      to keeping every bracket's sign and a positive margin.  This samples
      points a from-scratch search never returns.

A final `realize()` pass with a large budget is kept as a control: if it
ever succeeds where the structured search fails, the structure is wrong.
"""

import os
import sys

sys.dont_write_bytecode = True          # never leave __pycache__ in ai/omreal
for _v in ('OMP_NUM_THREADS', 'MKL_NUM_THREADS', 'OPENBLAS_NUM_THREADS',
           'NUMEXPR_NUM_THREADS'):
    os.environ.setdefault(_v, '1')

import math                                                 # noqa: E402
import time                                                 # noqa: E402

import numpy as np                                          # noqa: E402
from scipy.optimize import linprog                          # noqa: E402

import catalog                                              # noqa: E402

rz = catalog.realize_mod()
N, R = 9, 4


# ======================================================================
# exact integer linear algebra for the completion problem
# ======================================================================

def _det3(a):
    """3x3 determinant of a nested list of python ints."""
    return (a[0][0] * (a[1][1] * a[2][2] - a[1][2] * a[2][1])
            - a[0][1] * (a[1][0] * a[2][2] - a[1][2] * a[2][0])
            + a[0][2] * (a[1][0] * a[2][1] - a[1][1] * a[2][0]))


def completion_rows(X, chi, geom, p):
    """Exact integer rows A with  A x_p > 0  <=>  every basis containing p
    has the sign chi demands, given the other columns of X.

    X is an integer (r, n) array; column p is ignored.  Returns (A, bases)
    with A a list of lists of python ints.
    """
    r = geom.r
    rest = geom.pt_rest[p]                    # (K, r-1) other elements
    bs = geom.pt_b[p]                          # (K,) basis indices
    sg = geom.pt_sgn[p]                        # (K,) position sign
    Xl = [[int(v) for v in row] for row in np.asarray(X)]
    A = []
    for k in range(len(bs)):
        cols = [int(c) for c in rest[k]]
        # v[m] = (-1)^(m + r - 1) * det( rows != m of the (r-1) columns )
        v = []
        for m in range(r):
            sub = [[Xl[i][c] for c in cols] for i in range(r) if i != m]
            d = _det3(sub) if r == 4 else None
            v.append(-d if ((m + r - 1) & 1) else d)
        c = int(sg[k]) * int(chi[bs[k]])
        A.append([c * t for t in v])
    return A, bs


def _lp_interior(A, obj=None, cap=1.0, margin_frac=0.25):
    """max t  s.t.  (A/|a|) x >= t,  |x|_inf <= cap,  t <= 1   [obj is None]
    or  max <obj,x>  s.t. (A/|a|) x >= margin_frac * t0  [obj given].

    Returns (x, t) with t the achieved margin, or (None, None).

    `margin_frac` controls how close to the wall the exploratory move is
    allowed to sit.  It matters: a completion cone is empty because the
    other eight points are badly placed, and the configurations that open it
    are often near the boundary of the deletion's own realization space, not
    at its analytic centre.
    """
    Af = np.array(A, dtype=np.float64)
    m, d = Af.shape
    nrm = np.linalg.norm(Af, axis=1)
    if not np.isfinite(nrm).all() or (nrm <= 0).any():
        return None, None
    An = Af / nrm[:, None]
    if obj is None:
        Aub = np.hstack([-An, np.ones((m, 1))])
        c = np.zeros(d + 1)
        c[-1] = -1.0
        bounds = [(-cap, cap)] * d + [(None, 1.0)]
        res = linprog(c, A_ub=Aub, b_ub=np.zeros(m), bounds=bounds,
                      method='highs')
        if not res.success:
            return None, None
        return np.asarray(res.x[:d]), float(res.x[d])
    x0, t0 = _lp_interior(A, None, cap)
    if x0 is None or t0 <= 0:
        return x0, t0
    lo = margin_frac * t0
    res = linprog(-np.asarray(obj, dtype=np.float64), A_ub=-An,
                  b_ub=-lo * np.ones(m), bounds=[(-cap, cap)] * d,
                  method='highs')
    if not res.success:
        return x0, t0
    x = np.asarray(res.x)
    s = An @ x
    return x, float(s.min())


def _round_positive(A, x, denoms=(1 << 6, 1 << 10, 1 << 14, 1 << 18,
                                  1 << 24, 1 << 30, 1 << 38)):
    """Integer y ~ x with A y > 0 exactly, or None."""
    mx = float(np.abs(x).max())
    if not np.isfinite(mx) or mx <= 0:
        return None
    xs = x / mx
    for D in denoms:
        y = [int(v) for v in np.rint(xs * D)]
        g = 0
        for v in y:
            g = math.gcd(g, abs(v))
        if g > 1:
            y = [v // g for v in y]
        if not any(y):
            continue
        ok = True
        for row in A:
            s = 0
            for a, b in zip(row, y):
                s += a * b
            if s <= 0:
                ok = False
                break
        if ok:
            return y
    return None


def complete(X, chi, geom, p, want_blockers=False):
    """Try to place element p on the configuration X (whose other columns
    must already realize chi\\p).  Returns an integer (r,) column or None.

    The float LP is a proposal machine only: the returned column is checked
    against the exact integer rows before it is handed back, and the caller
    re-checks all C(n,r) brackets afterwards.

    When the LP says no -- and it says no COMPLETELY, the cone really is
    empty for this Y -- `want_blockers` also returns the elements that hold
    it shut: the ones appearing in the constraints that bind at the optimum.
    Those are the columns worth moving next, and moving them instead of a
    random column is what turns the random walk into a search.
    """
    A, bs = completion_rows(X, chi, geom, p)
    x, t = _lp_interior(A)
    if x is None:
        return None, 0.0, ()
    if t <= 0:
        blk = ()
        if want_blockers:
            Af = np.array(A, dtype=np.float64)
            nrm = np.linalg.norm(Af, axis=1)
            good = nrm > 0
            s = np.full(len(A), np.inf)
            s[good] = (Af[good] @ x) / nrm[good]
            tight = np.flatnonzero(s <= s.min() + 1e-9 * max(1.0, abs(t)))
            el = set()
            for i in tight[:12]:
                for q in geom.bases0[int(bs[i])]:
                    if q != p:
                        el.add(int(q))
            blk = tuple(sorted(el))
        return None, t, blk
    y = _round_positive(A, x)
    return y, t, ()


# ======================================================================
# exact configurations
# ======================================================================

def brackets_ok(Z, chi, geom):
    s = rz.exact_bracket_signs(np.asarray(Z, dtype=np.int64), geom)
    return s is not None and np.array_equal(s, np.asarray(chi, dtype=np.int8))


def _shrink(Z, cap=1 << 22):
    """Reduce each column by its gcd; None if entries are still too large."""
    Z = np.asarray(Z, dtype=object)
    out = np.empty_like(Z)
    for j in range(Z.shape[1]):
        col = [int(v) for v in Z[:, j]]
        g = 0
        for v in col:
            g = math.gcd(g, abs(v))
        if g > 1:
            col = [v // g for v in col]
        if max(abs(v) for v in col) > cap:
            return None
        out[:, j] = col
    return np.array(out.tolist(), dtype=np.int64)


class Deletion(object):
    """chi with element p removed: an (n-1)-element chirotope plus the map
    back to the original columns."""

    def __init__(self, chi, geom9, geom8, p):
        self.p = p
        self.keep = [q for q in range(geom9.n) if q != p]
        idx = []
        for B in geom8.bases0:
            idx.append(geom9.bidx[tuple(sorted(self.keep[b] for b in B))])
        self.idx = np.array(idx, dtype=np.int64)
        self.chi8 = np.asarray(chi)[self.idx].astype(np.int8)

    def embed(self, Y8, xp, r=R, n=N):
        """(r,8) integer + column -> the full (r,9) integer matrix."""
        Z = np.zeros((r, n), dtype=object)
        for k, q in enumerate(self.keep):
            Z[:, q] = [int(v) for v in np.asarray(Y8)[:, k]]
        Z[:, self.p] = [int(v) for v in xp]
        return Z

    def restrict(self, Z):
        return np.asarray(Z)[:, self.keep]


# ======================================================================
# the search
# ======================================================================

class Searcher(object):

    def __init__(self, seed=20260801, depth=8):
        self.g9 = rz.Geom(N, R)
        self.g8 = rz.Geom(N - 1, R)
        self.rng = np.random.default_rng(seed)
        self.lp_calls = 0
        self.depth = depth          # walk length per fresh deletion sample

    # ---- sources of exact 8-point deletion realizations ----------------

    def fresh_deletion(self, dele, seed, tries=1, sweeps=15, rerolls=3):
        """Realize chi\\p from scratch, as an (8,4) problem."""
        Y, _ = rz.realize(dele.chi8, self.g8, tries=tries, seed=seed,
                          sweeps=sweeps, rerolls=rerolls, wall_budget=2)
        if Y is None:
            return None
        return _shrink(Y)

    def walk_deletion(self, Y, dele, steps=1, cap=1.0, blockers=()):
        """Move inside the realization space of chi\\p: re-place one column
        at the optimum of a random objective, keeping every sign.

        `blockers` are ORIGINAL element indices that held the last completion
        LP shut; they are preferred over a uniformly random column, which is
        what makes the walk a descent rather than a diffusion.
        """
        Y = np.asarray(Y, dtype=np.int64).copy()
        pref = [dele.keep.index(b) for b in blockers if b in dele.keep]
        for _ in range(steps):
            if pref and self.rng.random() < 0.7:
                q = int(pref[int(self.rng.integers(len(pref)))])
            else:
                q = int(self.rng.integers(self.g8.n))
            A, _ = completion_rows(Y, dele.chi8, self.g8, q)
            obj = self.rng.normal(size=R)
            self.lp_calls += 1
            mf = float(self.rng.choice([0.02, 0.08, 0.25, 0.6]))
            x, t = _lp_interior(A, obj=obj, cap=cap, margin_frac=mf)
            if x is None or t <= 0:
                continue
            y = _round_positive(A, x)
            if y is None:
                continue
            Z = Y.copy()
            Z[:, q] = y
            Z2 = _shrink(Z)
            if Z2 is None:
                continue
            if brackets_ok(Z2, dele.chi8, self.g8):
                Y = Z2
        return Y

    # ---- the test -----------------------------------------------------

    def try_complete(self, Y, dele, chi, want_blockers=True):
        """One LP.  Returns an exact integer (r,9) realization of chi, or None."""
        Z = dele.embed(Y, [0] * R)
        Zi = np.array(Z.tolist(), dtype=np.int64)
        self.lp_calls += 1
        xp, t, blk = complete(Zi, chi, self.g9, dele.p,
                              want_blockers=want_blockers)
        if xp is None:
            return None, t, blk
        Zi[:, dele.p] = xp
        Zs = _shrink(Zi)
        if Zs is None:
            return None, t, blk
        if not brackets_ok(Zs, chi, self.g9):
            return None, t, blk
        return Zs, t, blk

    # ---- transported neighbours from the sweep's store -----------------

    def store_mutants(self, row, chi, arrays, kids=None, limit=24):
        """Exact integer realizations of MUTANTS of chi, from the sweep.

        Each is verified to differ from chi in exactly one bracket before it
        is used, so a group-convention error cannot propagate.
        """
        out = []
        tw = catalog.treewalk_mod()
        act = tw.Action()
        st, Z = arrays['st'], arrays['Z']
        par, flip = arrays['parent'], arrays['flip']
        sig, eps, gsg = arrays['sigma'], arrays['eps'], arrays['gsgn']
        cand = []
        p = int(par[row])
        if 0 <= p != row and int(st[p]) in (catalog.WALK, catalog.REPAIR):
            # g . chi_row = mu_flip(chi_parent)  =>  g^{-1} . chi_parent is a
            # mutant of chi_row
            s2, e2, g2 = act.inverse_params(sig[row], int(eps[row]),
                                            int(gsg[row]))
            cand.append((np.asarray(Z[p]), s2, e2, g2))
        for c in (kids if kids is not None else []):
            c = int(c)
            if int(st[c]) in (catalog.WALK, catalog.REPAIR):
                cand.append((np.asarray(Z[c]), sig[c], int(eps[c]),
                             int(gsg[c])))
            if len(cand) >= limit:
                break
        chi = np.asarray(chi, dtype=np.int8)
        for (Zp, s, e, g) in cand:
            W = act.on_matrix(np.asarray(Zp, dtype=np.int64), s, e, g)
            W = _shrink(W)
            if W is None:
                continue
            om = rz.exact_bracket_signs(W, self.g9)
            if om is None:
                continue
            diff = np.flatnonzero(om != chi)
            if len(diff) == 1:
                out.append((W, int(diff[0])))
        return out

    # ---- the driver ---------------------------------------------------

    def attack(self, chi, budget=60.0, row=None, arrays=None, kids=None,
               log=None):
        """Search for an exact integer realization of chi.  Returns (Z, log)."""
        chi = np.asarray(chi, dtype=np.int8)
        t0 = time.time()
        log = {} if log is None else log
        log.setdefault('sources', {})
        log.setdefault('lp_infeasible', 0)
        log.setdefault('lp_feasible', 0)
        dels = [Deletion(chi, self.g9, self.g8, p) for p in range(N)]

        def record(src, ok):
            d = log['sources'].setdefault(src, [0, 0])
            d[0] += 1
            d[1] += int(ok)

        state = {'blk': (), 't': None}

        def test(Y, dele, src):
            Z, t, blk = self.try_complete(Y, dele, chi)
            if t is not None and t > 0:
                log['lp_feasible'] += 1
            else:
                log['lp_infeasible'] += 1
                state['blk'] = blk
            state['t'] = t
            record(src, Z is not None)
            return Z

        def chase(Y, dele, src, depth, deadline):
            """HILL-CLIMB on the completion margin.

            The LP returns the best achievable margin for x_p even when it is
            negative, and that number is a real objective: it measures how
            far this eight-point configuration is from admitting the ninth
            point.  Proposing a move and keeping it only when the margin does
            not get much worse turns the walk from diffusion into a descent,
            with a Metropolis tail so it can still leave a local basin.
            """
            best = state['t'] if state['t'] is not None else -1.0
            cur = best
            for k in range(depth):
                Y2 = self.walk_deletion(Y, dele, steps=1,
                                        blockers=state['blk'])
                Z = test(Y2, dele, src)
                if Z is not None:
                    return Z, Y2
                t2 = state['t'] if state['t'] is not None else -1.0
                temp = 0.35 * (1.0 - k / float(max(depth, 1))) + 0.02
                if t2 >= cur or self.rng.random() < math.exp(
                        min(0.0, (t2 - cur) / (temp * max(abs(cur), 1e-6)))):
                    Y, cur = Y2, t2
                if time.time() - t0 > deadline:
                    break
            return None, Y

        # --- T1/T2: exact mutants from the sweep's store -----------------
        if arrays is not None and row is not None:
            for (W, j) in self.store_mutants(row, chi, arrays, kids):
                for p in self.g9.bases0[j]:
                    Z = test(dels[p].restrict(W), dels[p], 'store')
                    if Z is not None:
                        log['found'] = 'store'
                        log['time'] = time.time() - t0
                        return Z, log
                for p in self.g9.bases0[j]:
                    Z, _ = chase(dels[p].restrict(W), dels[p], 'store_walk',
                                 self.depth, 0.35 * budget)
                    if Z is not None:
                        log['found'] = 'store_walk'
                        log['time'] = time.time() - t0
                        return Z, log
                if time.time() - t0 > 0.35 * budget:
                    break

        # --- S1/S3: fresh deletion realizations, plus guided walks -------
        seed = 0
        while time.time() - t0 < 0.90 * budget:
            for dele in dels:
                if time.time() - t0 > 0.90 * budget:
                    break
                seed += 1
                Y = self.fresh_deletion(dele, seed=seed * 7919 + dele.p)
                if Y is None or not brackets_ok(Y, dele.chi8, self.g8):
                    record('fresh_fail', False)
                    continue
                Z = test(Y, dele, 'fresh')
                if Z is not None:
                    log['found'] = 'fresh'
                    log['time'] = time.time() - t0
                    return Z, log
                Z, _ = chase(Y, dele, 'walk', self.depth, 0.90 * budget)
                if Z is not None:
                    log['found'] = 'walk'
                    log['time'] = time.time() - t0
                    return Z, log

        # --- control: the project's own searcher, large budget -----------
        Z, _ = rz.realize(chi, self.g9, tries=4, seed=int(row or 0),
                          sweeps=40, rerolls=8, wall_budget=12)
        record('control', Z is not None)
        if Z is not None:
            log['found'] = 'control'
            log['time'] = time.time() - t0
            return _shrink(Z), log
        log['found'] = None
        log['time'] = time.time() - t0
        return None, log


def realizable_record(n, r, chi_str, Z):
    """The ai/omreal certificate schema, so checkcert.py accepts it."""
    return {'n': n, 'r': r, 'chi': chi_str, 'verdict': 'REALIZABLE',
            'matrix': [[int(v) for v in row] for row in np.asarray(Z)]}
