#!/usr/bin/env python3
"""THE EXACT GATE -- weapon A with `exactlp.exact_feasible` as its oracle.

OPEN_ATTACK.md s3.1 records the scope of the float64 completion LP:

    exactly verified success, HEURISTIC numerical failure

and states the rule that follows: *"exact rational feasibility ... before
declaring a cone empty ... is required before any future run reports a class
as STILL_OPEN on numerical grounds."*  `exactlp.py` was written to close
that gap.  This file is where it is used.

WHAT THIS CHANGES, AND WHAT IT CANNOT
=====================================
For one eight-point configuration Y and one element p, "does Y extend to a
realization of chi?" is `A x > 0` with A the exact integer 4-column matrix
of 3x3 minors of Y.  `exactlp.exact_feasible(A)` decides that in rational
arithmetic and returns a self-verified integer certificate either way:

  FEASIBLE    an integer x with A x > 0 -- the ninth column, exactly, with
              NO rounding step and NO size cap.  This is strictly stronger
              than the float path, which (i) proposes x in float64,
              (ii) rounds it against a fixed ladder of denominators and
              gives up if none lands (`weaponA._round_positive`), and
              (iii) discards the completed matrix outright if any entry
              exceeds 2**22 (`weaponA._shrink`).  Channels (ii) and (iii)
              can each throw away a genuine realization; neither exists
              here.
  INFEASIBLE  a nonnegative integer lambda != 0 with A^T lambda = 0 -- a
              Gordan certificate that THIS Y does not extend.

**The negative direction never decides the class.**  A class is a set of
sign conditions; a configuration Y is one point of the nine-dimensional
realization space of chi\\p.  Ten thousand exact INFEASIBLE certificates
prove ten thousand statements about points, and nothing about chi.  So the
verdict emitted here is only ever

    REALIZABLE   (an exact integer 4x9 matrix), or
    STILL_OPEN   (with n_exact_infeasible and deletions_covered recorded)

and NEVER NON_REALIZABLE.  That asymmetry is the whole reason this file
exists: it removes float64 from the *success* path's failure modes and it
makes the recorded negative evidence exact, but it does not turn a search
into a proof.

lambda IS THE BLOCKER INFORMATION
=================================
The float path guesses which columns hold the cone shut by looking at rows
that are tight at the LP optimum, to within 1e-9.  The exact certificate
does better: the support of lambda is an explicit positive dependence among
the rows, i.e. a combinatorial core of the infeasibility.  The elements
appearing in those bases are the ones worth moving, and they are named
exactly rather than by a tolerance.

    python exactgate.py run --todo FILE [--budget 300] [--per-p 24]
    python exactgate.py run --rows 46731,69368 --budget 300
"""

import argparse
import json
import math
import os
import sys
import time

sys.dont_write_bytecode = True
for _v in ('OMP_NUM_THREADS', 'MKL_NUM_THREADS', 'OPENBLAS_NUM_THREADS',
           'NUMEXPR_NUM_THREADS'):
    os.environ.setdefault(_v, '1')

import numpy as np                                          # noqa: E402

import catalog                                              # noqa: E402
import exactlp                                              # noqa: E402
import weaponA                                              # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, 'data')
N, R = 9, 4


# ======================================================================
# big-integer exact bracket check -- no int64, no numpy dtype limits
# ======================================================================

def _det4(M):
    """4x4 determinant of a list of 4 rows of python ints (Laplace on the
    first two rows via complementary 2x2 minors)."""
    a, b, c, d = M
    out = 0
    # expand over pairs of columns from rows (a, b)
    for i in range(4):
        for j in range(i + 1, 4):
            top = a[i] * b[j] - a[j] * b[i]
            if not top:
                continue
            k, l = [t for t in range(4) if t != i and t != j]
            bot = c[k] * d[l] - c[l] * d[k]
            # generalized Laplace along rows {0,1}: the sign of the term for
            # column pair {i<j} is (-1)^((0+1)+(i+j)) = (-1)^(i+j+1).
            sgn = -1 if ((i + j + 1) & 1) else 1
            out += sgn * top * bot
    return out


def brackets_ok_big(Zcols, chi, bases0):
    """Zcols: list of 9 columns, each a list of 4 python ints.
    bases0: the C(9,4) bases in the catalog's colex order.
    Returns True iff every bracket is nonzero and has chi's sign."""
    for idx, B in enumerate(bases0):
        M = [[Zcols[b][i] for b in B] for i in range(4)]
        d = _det4(M)
        if d == 0:
            return False
        if (1 if d > 0 else -1) != int(chi[idx]):
            return False
    return True


def _gcd_reduce_cols(Zcols):
    out = []
    for col in Zcols:
        g = 0
        for v in col:
            g = math.gcd(g, abs(v))
        out.append([v // g for v in col] if g > 1 else list(col))
    return out


# ======================================================================
# the exact completion oracle
# ======================================================================

class ExactSearcher(object):

    def __init__(self, seed=20260802, cap=1 << 26):
        self.base = weaponA.Searcher(seed=seed)
        self.g9, self.g8 = self.base.g9, self.base.g8
        self.rng = self.base.rng
        self.cap = cap
        self.n_lp = 0
        self.n_inf = 0

    # ---- one exact completion test ------------------------------------

    def complete_exact(self, Ycols, dele, chi):
        """Ycols: 8 columns of python ints realizing chi\\p.
        Returns (status, payload, blockers).
          ('FEASIBLE',   Zcols(9), ())      an exact realization of chi
          ('INFEASIBLE', lam,      blockers)
          ('REJECT',     None,     ())      x found but brackets disagreed
        """
        p = dele.p
        Z = [None] * N
        for k, q in enumerate(dele.keep):
            Z[q] = list(Ycols[k])
        Z[p] = [0, 0, 0, 0]
        Zi = np.array([[Z[q][i] for q in range(N)] for i in range(R)],
                      dtype=object)
        A, bs = weaponA.completion_rows(Zi, chi, self.g9, p)
        self.n_lp += 1
        st, cert = exactlp.exact_feasible(A)
        if st == 'INFEASIBLE':
            self.n_inf += 1
            el = set()
            for i, w in enumerate(cert):
                if w:
                    for q in self.g9.bases0[int(bs[i])]:
                        if q != p:
                            el.add(int(q))
            return 'INFEASIBLE', [int(v) for v in cert], tuple(sorted(el))
        Z[p] = [int(v) for v in cert]
        Zc = _gcd_reduce_cols(Z)
        if not brackets_ok_big(Zc, chi, self.g9.bases0):
            return 'REJECT', None, ()
        return 'FEASIBLE', Zc, ()

    # ---- sampling inside the deletion's realization space --------------

    def walk_big(self, Ycols, dele, steps=1, blockers=()):
        """weaponA.walk_deletion with a larger size cap.

        The cap here only shapes WHICH configurations get sampled -- it never
        rejects a completion, because the completion test above has no cap at
        all.  It is raised from 2**22 to 2**26 so the walk can reach
        configurations the float path could not hold.
        """
        Y = np.array([[Ycols[k][i] for k in range(len(Ycols))]
                      for i in range(R)], dtype=np.int64)
        pref = [dele.keep.index(b) for b in blockers if b in dele.keep]
        for _ in range(steps):
            if pref and self.rng.random() < 0.7:
                q = int(pref[int(self.rng.integers(len(pref)))])
            else:
                q = int(self.rng.integers(self.g8.n))
            A, _ = weaponA.completion_rows(Y, dele.chi8, self.g8, q)
            obj = self.rng.normal(size=R)
            mf = float(self.rng.choice([0.02, 0.08, 0.25, 0.6]))
            x, t = weaponA._lp_interior(A, obj=obj, cap=1.0, margin_frac=mf)
            if x is None or t is None or t <= 0:
                continue
            y = weaponA._round_positive(A, x)
            if y is None:
                continue
            Z = Y.copy()
            Z[:, q] = y
            Z2 = weaponA._shrink(Z, cap=self.cap)
            if Z2 is None:
                continue
            if weaponA.brackets_ok(Z2, dele.chi8, self.g8):
                Y = Z2
        return [[int(Y[i][k]) for i in range(R)] for k in range(Y.shape[1])]

    # ---- the per-class driver -----------------------------------------

    def attack(self, chi, row=None, arrays=None, kids=None, budget=300.0,
               per_p=24, depth=12, keep_certs=6):
        chi = np.asarray(chi, dtype=np.int8)
        t0 = time.time()
        dels = [weaponA.Deletion(chi, self.g9, self.g8, p) for p in range(N)]
        log = {'exact_lp': 0, 'exact_infeasible': 0, 'reject': 0,
               'deletions_covered': set(), 'sources': {}, 'per_p': {}}
        keep = []

        def note(src, st, p):
            d = log['sources'].setdefault(src, [0, 0])
            d[0] += 1
            if st == 'FEASIBLE':
                d[1] += 1
            if st == 'INFEASIBLE':
                log['deletions_covered'].add(int(p))
                log['per_p'][int(p)] = log['per_p'].get(int(p), 0) + 1

        def test(Ycols, dele, src, blockers):
            st, payload, blk = self.complete_exact(Ycols, dele, chi)
            note(src, st, dele.p)
            if st == 'REJECT':
                log['reject'] += 1
            if st == 'INFEASIBLE' and len(keep) < keep_certs:
                keep.append({'p': int(dele.p), 'source': src,
                             'Y': [list(c) for c in Ycols],
                             'lambda': payload})
            return st, payload, (blk if st == 'INFEASIBLE' else blockers)

        # --- source: the sweep's stored neighbours -----------------------
        if arrays is not None and row is not None:
            for (W, j) in self.base.store_mutants(row, chi, arrays, kids):
                Wc = [[int(W[i][q]) for i in range(R)] for q in range(N)]
                for p in self.g9.bases0[j]:
                    dele = dels[p]
                    Y = [Wc[q] for q in dele.keep]
                    st, payload, blk = test(Y, dele, 'store', ())
                    if st == 'FEASIBLE':
                        log['found'] = 'store'
                        return payload, self._fin(log, t0)
                    for _ in range(depth):
                        Y = self.walk_big(Y, dele, steps=1, blockers=blk)
                        st, payload, blk = test(Y, dele, 'store_walk', blk)
                        if st == 'FEASIBLE':
                            log['found'] = 'store_walk'
                            return payload, self._fin(log, t0)
                        if time.time() - t0 > 0.30 * budget:
                            break
                if time.time() - t0 > 0.30 * budget:
                    break

        # --- source: fresh deletion realizations + guided walks ----------
        seed = 0
        while time.time() - t0 < budget:
            for dele in dels:
                if time.time() - t0 > budget:
                    break
                seed += 1
                Y8 = self.base.fresh_deletion(dele,
                                              seed=seed * 7919 + dele.p)
                if Y8 is None or not weaponA.brackets_ok(Y8, dele.chi8,
                                                         self.g8):
                    continue
                Y = [[int(Y8[i][k]) for i in range(R)]
                     for k in range(Y8.shape[1])]
                st, payload, blk = test(Y, dele, 'fresh', ())
                if st == 'FEASIBLE':
                    log['found'] = 'fresh'
                    return payload, self._fin(log, t0)
                for _ in range(per_p):
                    Y = self.walk_big(Y, dele, steps=1, blockers=blk)
                    st, payload, blk = test(Y, dele, 'walk', blk)
                    if st == 'FEASIBLE':
                        log['found'] = 'walk'
                        return payload, self._fin(log, t0)
                    if time.time() - t0 > budget:
                        break
        log['found'] = None
        log['certs'] = keep
        return None, self._fin(log, t0)

    def _fin(self, log, t0):
        log['exact_lp'] = self.n_lp
        log['exact_infeasible'] = self.n_inf
        log['deletions_covered'] = sorted(log['deletions_covered'])
        log['seconds'] = round(time.time() - t0, 2)
        return log


# ======================================================================
# driver
# ======================================================================

def cmd_run(a):
    os.makedirs(DATA, exist_ok=True)
    if a.todo:
        todo = []
        with open(a.todo) as fh:
            for line in fh:
                p = line.split()
                if len(p) == 3:
                    todo.append((int(p[0]), int(p[1]), p[2]))
    else:
        want = {int(x) for x in a.rows.split(',')}
        todo = [t for t in _snapshot() if t[0] in want]
    if a.nshards > 1:
        todo = [t for i, t in enumerate(todo) if i % a.nshards == a.shard]
    tag = '%s_s%d' % (a.tag, a.shard)
    out_res = os.path.join(DATA, 'exactgate_%s.jsonl' % tag)
    out_real = os.path.join(DATA, 'exactgate_realizable_%s.jsonl' % tag)
    out_inf = os.path.join(DATA, 'exactgate_infeasible_%s.jsonl' % tag)

    arrays = catalog.arrays()
    kidx = None
    op = os.path.join(DATA, 'child_order.npy')
    sp = os.path.join(DATA, 'child_start.npy')
    if os.path.exists(op):
        kidx = (np.load(op, mmap_mode='r'), np.load(sp, mmap_mode='r'))
    S = ExactSearcher(seed=a.seed + 1000 * a.shard, cap=1 << a.cap_bits)

    print('exact gate: %d rows, budget %.0f s each' % (len(todo), a.budget),
          flush=True)
    for k, (row, depth, chis) in enumerate(todo):
        chi = np.array([1 if c == '+' else -1 for c in chis], dtype=np.int8)
        S.n_lp = S.n_inf = 0
        kids = None
        if kidx is not None:
            order, start = kidx
            kids = order[int(start[row]):int(start[row + 1])]
        Zc, log = S.attack(chi, row=row, arrays=arrays, kids=kids,
                           budget=a.budget, per_p=a.per_p, depth=a.depth)
        rec = {'row': row, 'depth': depth, 'chi': chis,
               'budget': a.budget,
               'verdict': 'REALIZABLE' if Zc is not None else 'STILL_OPEN',
               'exact_lp': log['exact_lp'],
               'exact_infeasible': log['exact_infeasible'],
               'deletions_covered': log['deletions_covered'],
               'rejects': log['reject'],
               'per_deletion_infeasible': log['per_p'],
               'sources': log['sources'],
               'found': log.get('found'),
               'seconds': log['seconds']}
        with open(out_res, 'a') as fh:
            fh.write(json.dumps(rec) + '\n')
        if Zc is not None:
            mat = [[Zc[q][i] for q in range(N)] for i in range(R)]
            with open(out_real, 'a') as fh:
                fh.write(json.dumps({'n': N, 'r': R, 'chi': chis,
                                     'verdict': 'REALIZABLE',
                                     'matrix': mat}) + '\n')
        else:
            with open(out_inf, 'a') as fh:
                fh.write(json.dumps({'n': N, 'r': R, 'chi': chis, 'row': row,
                                     'verdict': 'NO_COMPLETION_FOR_THESE_'
                                                'CONFIGURATIONS',
                                     'note': 'each record proves only that '
                                             'the named Y does not extend; '
                                             'this is NOT a statement about '
                                             'the class',
                                     'certs': log.get('certs', [])}) + '\n')
        print('[%3d/%3d] row %8d d%02d  %-11s  exactLP %6d (inf %6d, '
              'p covered %d/9)  %6.1f s  %s'
              % (k + 1, len(todo), row, depth, rec['verdict'],
                 rec['exact_lp'], rec['exact_infeasible'],
                 len(rec['deletions_covered']), rec['seconds'],
                 rec['found'] or ''), flush=True)


def _snapshot():
    out = []
    with open(os.path.join(DATA, 'open_set.txt')) as fh:
        for line in fh:
            p = line.split()
            if len(p) == 3:
                out.append((int(p[0]), int(p[1]), p[2]))
    return out


def _selftest():
    """The oracle must reproduce known realizations and must never mint one
    whose brackets disagree."""
    import random
    print('exactgate self-test')
    ok = 0
    rows = catalog.rows_with_status(catalog.REPAIR)[:8]
    CHI = catalog.chi_of_rows(rows)
    arrays = catalog.arrays()
    S = ExactSearcher(seed=5)
    for r, chi in zip(rows, CHI):
        S.n_lp = S.n_inf = 0
        Zc, log = S.attack(chi, row=int(r), arrays=arrays, budget=60.0,
                           per_p=12, depth=8)
        if Zc is None:
            print('  row %d NOT realized (%s)' % (r, log['seconds']))
            continue
        # independent re-check with the big-int determinant
        if brackets_ok_big(Zc, chi, S.g9.bases0):
            ok += 1
        else:
            print('  *** row %d minted a BAD matrix' % r)
            return 1
    print('  reproduced %d/%d REALIZABLE(repair) classes with the exact '
          'oracle' % (ok, len(rows)))

    # the big-int determinant must agree with numpy on small matrices
    rng = random.Random(11)
    for _ in range(200):
        M = [[rng.randint(-9, 9) for _ in range(4)] for _ in range(4)]
        a = _det4(M)
        b = int(round(float(np.linalg.det(np.array(M, dtype=np.float64)))))
        if a != b:
            print('  *** _det4 disagrees with numpy: %r %s %s' % (M, a, b))
            return 1
    print('  _det4 agrees with numpy.linalg.det on 200 random 4x4 matrices')

    # ---- SOUNDNESS, and it is the fatal one ---------------------------
    # On a class the sweep certified NON_REALIZABLE, no eight-point
    # configuration can extend -- so every exact test must come back
    # INFEASIBLE, and the oracle must never mint a matrix.  This exercises
    # the INFEASIBLE path far harder than any OPEN class does, and a single
    # FEASIBLE here would mean either the certificate machinery or the
    # sweep is wrong.
    bad = catalog.rows_with_status(catalog.NONREAL)[:10]
    CHI = catalog.chi_of_rows(bad)
    minted, n_lp, n_inf = 0, 0, 0
    for r, chi in zip(bad, CHI):
        S.n_lp = S.n_inf = 0
        Zc, log = S.attack(chi, row=int(r), arrays=arrays, budget=20.0,
                           per_p=10, depth=6)
        n_lp += log['exact_lp']
        n_inf += log['exact_infeasible']
        if Zc is not None:
            minted += 1
            print('  *** FATAL: minted a realization for NON_REALIZABLE '
                  'row %d' % r)
    print('  NON_REALIZABLE control: %d exact LPs, %d INFEASIBLE '
          '(%.1f%%), %d realizations minted (must be 0)'
          % (n_lp, n_inf, 100.0 * n_inf / max(n_lp, 1), minted))
    good = (ok == len(rows)) and minted == 0 and n_inf == n_lp
    print('exactgate self-test: %s' % ('PASS' if good else '*** FAIL ***'))
    return 0 if good else 1


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest='cmd', required=True)
    r = sub.add_parser('run')
    r.add_argument('--todo', default=None)
    r.add_argument('--rows', default=None)
    r.add_argument('--tag', default='g1')
    r.add_argument('--shard', type=int, default=0)
    r.add_argument('--nshards', type=int, default=1)
    r.add_argument('--budget', type=float, default=300.0)
    r.add_argument('--per-p', type=int, default=24)
    r.add_argument('--depth', type=int, default=12)
    r.add_argument('--cap-bits', type=int, default=26)
    r.add_argument('--seed', type=int, default=20260802)
    r.set_defaults(fn=cmd_run)
    t = sub.add_parser('selftest')
    t.set_defaults(fn=lambda a: sys.exit(_selftest()))
    a = ap.parse_args()
    a.fn(a)


if __name__ == '__main__':
    main()
