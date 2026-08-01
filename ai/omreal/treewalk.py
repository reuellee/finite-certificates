#!/usr/bin/env python3
"""Realize the catalogue by WALKING the certified mutation tree, not by
searching each class from scratch.

    python treewalk.py verify   --rows 2000        # the group identity
    python treewalk.py walk     --maxdepth 12      # walk a subtree, measure
    python treewalk.py walk     --maxdepth 27 --out certs.jsonl

WHY THIS EXISTS
===============
`pilot.py` treats every one of the 9 276 595 classes as an independent
search problem.  That is what makes the sweep expensive: the hard classes
are hard precisely because a from-scratch search has to find a tiny region
of realization space.

But omgamma already shipped a certified MUTATION SPANNING TREE over the
whole catalogue (`witness_4_9.npz`, max depth 27).  For every non-root row
i it records a parent, a basis `flip[i]`, and a group element
g = (sigma, eps, gsgn) with the EXACT identity

    g . chi_i  =  mu_{B_flip[i]} ( chi_parent[i] )

so chi_i and its parent differ by one bracket sign, up to relabelling and
reorientation.  If the parent is realized by Z_p, then realizing the child
is not a search at all: it is ONE WALL CROSSING from a configuration that
is already in the right place -- push bracket flip[i] through zero while
the other C(n,r)-1 hold, then undo g.

The pilot found the same structure the hard way: stalled searches sit at
exactly one wrong bracket, i.e. they have realized a mutant and cannot
cross.  Here the mutant is handed to us, already realized, by the tree.

Statefulness is the price: a child needs its parent first.  But the tree
has depth 27, so the walk is 27 waves and every row within a wave is
independent -- and the frontier is the only thing that must be resident.
"""

import argparse
import json
import os
import sys
import time
from itertools import combinations

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import omdecode                                            # noqa: E402
import realize as rz                                       # noqa: E402

DATA = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                    '..', 'omgamma', 'data', 'coverage_4_9')
N, R = 9, 4


# ----------------------------------------------------------------------
# the G' action, on chirotopes and on matrices
# ----------------------------------------------------------------------

class Action(object):
    """((sig,eps,s).chi)(x_1..x_r) = (-1)^s (-1)^{|eps cap x|} chi(sig^-1 x)

    (MANIFEST.json, conventions.group).  Elements are 1..n; sigma[x-1] is
    sigma(x); eps is a bitmask with bit (x-1) set iff x is reoriented.
    """

    def __init__(self, n=N, r=R):
        self.n, self.r = n, r
        self.bases = sorted(combinations(range(1, n + 1), r),
                            key=lambda t: tuple(reversed(t)))
        self.idx = {B: j for j, B in enumerate(self.bases)}
        self.M = len(self.bases)
        self.BAS = np.array(self.bases, dtype=np.int64)

    def on_chi(self, chi, sigma, eps, gsgn):
        inv = np.empty(self.n + 1, dtype=np.int64)
        for x in range(1, self.n + 1):
            inv[int(sigma[x - 1])] = x
        out = np.empty(self.M, dtype=np.int8)
        gs = -1 if gsgn else 1
        for j, B in enumerate(self.bases):
            t = [int(inv[b]) for b in B]
            sg = 1
            for a in range(1, len(t)):
                b = a
                while b > 0 and t[b - 1] > t[b]:
                    t[b - 1], t[b] = t[b], t[b - 1]
                    sg = -sg
                    b -= 1
            par = 1
            for b in B:
                if (eps >> (b - 1)) & 1:
                    par = -par
            out[j] = gs * par * sg * chi[self.idx[tuple(t)]]
        return out

    def on_matrix(self, X, sigma, eps, gsgn):
        """If X realizes chi, this realizes (sigma,eps,gsgn).chi.

        Column k of X is element k+1; it becomes column sigma(k+1), negated
        if sigma(k+1) is reoriented.  A global sign flips one row, which
        negates every bracket.
        """
        Y = np.empty_like(X)
        for k in range(1, self.n + 1):
            s = int(sigma[k - 1])
            col = X[:, k - 1]
            Y[:, s - 1] = -col if ((eps >> (s - 1)) & 1) else col
        if gsgn:
            Y = Y.copy()
            Y[0, :] = -Y[0, :]
        return Y

    def inverse_params(self, sigma, eps, gsgn):
        """Parameters of g^{-1}."""
        inv = np.empty(self.n, dtype=np.uint8)
        for x in range(1, self.n + 1):
            inv[int(sigma[x - 1]) - 1] = x
        # reorienting x then relabelling by sigma is reorienting sigma(x);
        # so the inverse reorients sigma^{-1} of each set bit
        e2 = 0
        for x in range(1, self.n + 1):
            if (eps >> (x - 1)) & 1:
                e2 |= 1 << (int(inv[x - 1]) - 1)
        return inv, e2, gsgn


# ----------------------------------------------------------------------
# data
# ----------------------------------------------------------------------

def load(verify_hashes=True):
    hi, lo, stab = omdecode.load_coverage_4_9(verify=verify_hashes)
    w = np.load(os.path.join(DATA, 'witness_4_9.npz'))
    man = json.load(open(os.path.join(DATA, 'MANIFEST.json')))
    if verify_hashes:
        import hashlib
        want = man['witness_array_sha256']
        for k in ('parent', 'flip', 'sigma', 'eps', 'gsgn', 'depth'):
            got = hashlib.sha256(np.ascontiguousarray(w[k]).tobytes()).hexdigest()
            if got != want[k]:
                raise SystemExit('witness array %r hash mismatch' % k)
        print('witness arrays: all six SHA-256 match MANIFEST.json')
    return hi, lo, stab, w, man


# ----------------------------------------------------------------------
# verify the identity the walk depends on
# ----------------------------------------------------------------------

def cmd_verify(a):
    hi, lo, stab, w, man = load()
    act = Action()
    root = man['witness']['root_row']
    rng = np.random.default_rng(a.seed)
    rows = rng.choice(len(hi), size=a.rows, replace=False)
    rows = np.array([r for r in rows if r != root])
    parent, flip = w['parent'], w['flip']
    sig, eps, gsg = w['sigma'], w['eps'], w['gsgn']
    ok = 0
    t0 = time.time()
    B = 2000
    for s in range(0, len(rows), B):
        sl = rows[s:s + B]
        CHI = omdecode.signs_from_keys(N, R, hi[sl], lo[sl])
        P = parent[sl]
        CHP = omdecode.signs_from_keys(N, R, hi[P], lo[P])
        for k, i in enumerate(sl):
            lhs = act.on_chi(CHI[k], sig[i], int(eps[i]), int(gsg[i]))
            rhs = CHP[k].copy()
            rhs[int(flip[i])] = -rhs[int(flip[i])]
            if np.array_equal(lhs, rhs):
                ok += 1
    print('IDENTITY  g . chi_i == mu_flip(chi_parent):  %d/%d rows  (%.1f s)'
          % (ok, len(rows), time.time() - t0))
    if ok != len(rows):
        raise SystemExit('the walk cannot be trusted: identity failed')

    # and the matrix action must implement the same thing
    geom = rz.Geom(N, R)
    rng2 = np.random.default_rng(5)
    bad = 0
    for _ in range(a.matrix_tests):
        X = rng2.integers(-40, 41, size=(R, N))
        chi = rz.exact_bracket_signs(X, geom)
        if chi is None:
            continue
        i = int(rows[rng2.integers(len(rows))])
        Y = act.on_matrix(X, sig[i], int(eps[i]), int(gsg[i]))
        want = act.on_chi(chi, sig[i], int(eps[i]), int(gsg[i]))
        got = rz.exact_bracket_signs(Y, geom)
        if got is None or not np.array_equal(got, want):
            bad += 1
    print('MATRIX ACTION agrees with the chirotope action: %d failures in %d'
          % (bad, a.matrix_tests))
    if bad:
        raise SystemExit('matrix action is wrong')

    # and the inverse must undo it
    bad = 0
    for _ in range(a.matrix_tests):
        X = rng2.integers(-40, 41, size=(R, N))
        chi = rz.exact_bracket_signs(X, geom)
        if chi is None:
            continue
        i = int(rows[rng2.integers(len(rows))])
        Y = act.on_matrix(X, sig[i], int(eps[i]), int(gsg[i]))
        s2, e2, g2 = act.inverse_params(sig[i], int(eps[i]), int(gsg[i]))
        Z = act.on_matrix(Y, s2, e2, g2)
        if not np.array_equal(rz.exact_bracket_signs(Z, geom), chi):
            bad += 1
    print('INVERSE ACTION round-trips: %d failures in %d' % (bad, a.matrix_tests))
    if bad:
        raise SystemExit('inverse action is wrong')
    print('\nthe walk\'s three algebraic prerequisites all hold.')


# ----------------------------------------------------------------------
# the walk
# ----------------------------------------------------------------------

def cross_from(Zp, chi_target_mut, geom, rng, j):
    """Zp realizes chi_p; return a float config realizing mu_j(chi_p)."""
    X = Zp.astype(np.float64)
    nn = np.linalg.norm(X, axis=0, keepdims=True)
    nn[nn == 0] = 1.0
    X = X / nn
    if len(rz._wrong(chi_target_mut, X, geom)) != 1:
        return None
    if rz._cross_wall(chi_target_mut, X, geom, rng):
        return X
    return None


def cmd_walk(a):
    hi, lo, stab, w, man = load(verify_hashes=not a.fast)
    act = Action()
    geom = rz.Geom(N, R)
    root = man['witness']['root_row']
    parent, flip, depth = w['parent'], w['flip'], w['depth']
    sig, eps, gsg = w['sigma'], w['eps'], w['gsgn']
    rng = np.random.default_rng(0)

    order = np.argsort(depth, kind='stable')
    order = order[depth[order] <= a.maxdepth]
    print('walking %d rows (depth <= %d) of %d' % (len(order), a.maxdepth, len(hi)))

    Zs = {}
    chi_root = omdecode.signs_from_keys(N, R, hi[root:root + 1], lo[root:root + 1])[0]
    Z0, _ = rz.realize(chi_root, geom, tries=6, sweeps=40)
    if Z0 is None:
        raise SystemExit('could not realize the root')
    Zs[int(root)] = Z0
    print('root realized, entries |.|<=%d' % np.abs(Z0).max())

    fh = open(a.out, 'w') if a.out else None
    if fh:
        fh.write(json.dumps({'n': N, 'r': R,
                             'chi': omdecode.string_from_signs(chi_root),
                             'verdict': 'REALIZABLE',
                             'matrix': [[int(v) for v in r] for r in Z0]}) + '\n')
    nwalk = nfall = nfail = 0
    t_walk = t_fall = 0.0
    t0 = time.time()
    B = 4096
    for s in range(0, len(order), B):
        sl = order[s:s + B]
        CHI = omdecode.signs_from_keys(N, R, hi[sl], lo[sl])
        for k, i in enumerate(sl):
            i = int(i)
            if i == root:
                continue
            chi = CHI[k]
            p = int(parent[i])
            j = int(flip[i])
            Zp = Zs.get(p)
            Zi = None
            if Zp is not None:
                t1 = time.perf_counter()
                # target for the crossing: mu_j(chi_p) = g . chi_i
                mut = act.on_chi(chi, sig[i], int(eps[i]), int(gsg[i]))
                X = cross_from(Zp, mut, geom, rng, j)
                if X is not None:
                    s2, e2, g2 = act.inverse_params(sig[i], int(eps[i]), int(gsg[i]))
                    Xi = act.on_matrix(X, s2, e2, g2)
                    Zi, _D = rz._rationalise(Xi, chi, geom)
                t_walk += time.perf_counter() - t1
                if Zi is not None:
                    nwalk += 1
            if Zi is None:
                t1 = time.perf_counter()
                Zi, _ = rz.realize(chi, geom, tries=2, sweeps=15, rerolls=3,
                                   wall_budget=3, seed=i)
                t_fall += time.perf_counter() - t1
                if Zi is not None:
                    nfall += 1
                else:
                    nfail += 1
            if Zi is not None:
                chk = rz.exact_bracket_signs(Zi, geom)
                if chk is None or not np.array_equal(chk, chi):
                    raise SystemExit('row %d: matrix does not realize the class' % i)
                Zs[i] = Zi
                if fh:
                    fh.write(json.dumps(
                        {'n': N, 'r': R, 'chi': omdecode.string_from_signs(chi),
                         'verdict': 'REALIZABLE',
                         'matrix': [[int(v) for v in r] for r in Zi]}) + '\n')
        done = nwalk + nfall + nfail
        print('  %7d rows | walk %d (%.1f ms) | fallback %d (%.0f ms) | '
              'unrealized %d | %.0f s'
              % (done, nwalk, 1000 * t_walk / max(nwalk + nfail, 1), nfall,
                 1000 * t_fall / max(nfall + nfail, 1), nfail, time.time() - t0),
              flush=True)
    if fh:
        fh.close()
    tot = nwalk + nfall + nfail
    print('\nWALK RESULT over %d rows (depth <= %d)' % (tot, a.maxdepth))
    print('  crossed from parent   %7d  (%.2f%%)  %.1f ms each'
          % (nwalk, 100.0 * nwalk / max(tot, 1), 1000 * t_walk / max(nwalk, 1)))
    print('  fell back to search   %7d  (%.2f%%)  %.0f ms each'
          % (nfall, 100.0 * nfall / max(tot, 1), 1000 * t_fall / max(nfall, 1)))
    print('  unrealized            %7d  (%.2f%%)' % (nfail, 100.0 * nfail / max(tot, 1)))
    per = (t_walk + t_fall) / max(tot, 1)
    print('  end-to-end            %.1f ms/class  ->  %.0f core-hours for 9 276 595'
          % (1000 * per, per * 9276595 / 3600))



def cmd_probe(a):
    """Crossing success rate at ARBITRARY depth, without walking there.

    Walking to depth 27 means walking everything, so a depth-limited walk
    can only ever measure the shallow part of the tree -- where almost all
    classes live near the root's generic configuration.  This probe instead
    samples rows UNIFORMLY over the whole catalogue, realizes each row's
    PARENT from scratch, and then attempts exactly the crossing the walk
    would attempt.  It is if anything pessimistic: a searched realization
    of the parent is a generic point of its realization space, whereas the
    real walk arrives already pressed against the wall it just crossed.
    """
    hi, lo, stab, w, man = load(verify_hashes=not a.fast)
    act = Action()
    geom = rz.Geom(N, R)
    root = man['witness']['root_row']
    parent, flip, depth = w['parent'], w['flip'], w['depth']
    sig, eps, gsg = w['sigma'], w['eps'], w['gsgn']
    rng = np.random.default_rng(a.seed)
    rows = rng.choice(len(hi), size=a.rows, replace=False)
    rows = np.array([r for r in rows if r != root])
    import collections
    by = collections.defaultdict(lambda: [0, 0, 0])   # depth-bucket: n, parent-ok, crossed
    tp = tc = 0.0
    fh = open(a.out, 'w') if a.out else None
    for n_i, i in enumerate(rows):
        i = int(i)
        p = int(parent[i])
        d = int(depth[i])
        b = (d // 4) * 4
        by[b][0] += 1
        CH = omdecode.signs_from_keys(N, R, hi[[i, p]], lo[[i, p]])
        chi, chip = CH[0], CH[1]
        t1 = time.perf_counter()
        Zp, _ = rz.realize(chip, geom, tries=3, sweeps=25, rerolls=5,
                           wall_budget=4, seed=i)
        tp += time.perf_counter() - t1
        if Zp is None:
            continue
        by[b][1] += 1
        t1 = time.perf_counter()
        mut = act.on_chi(chi, sig[i], int(eps[i]), int(gsg[i]))
        X = cross_from(Zp, mut, geom, rng, int(flip[i]))
        Zi = None
        if X is not None:
            s2, e2, g2 = act.inverse_params(sig[i], int(eps[i]), int(gsg[i]))
            Zi, _D = rz._rationalise(act.on_matrix(X, s2, e2, g2), chi, geom)
        tc += time.perf_counter() - t1
        if Zi is not None:
            chk = rz.exact_bracket_signs(Zi, geom)
            if chk is None or not np.array_equal(chk, chi):
                raise SystemExit('probe produced a bad matrix at row %d' % i)
            by[b][2] += 1
            if fh:
                fh.write(json.dumps(
                    {'n': N, 'r': R, 'chi': omdecode.string_from_signs(chi),
                     'verdict': 'REALIZABLE',
                     'matrix': [[int(v) for v in r] for r in Zi]}) + chr(10))
        if (n_i + 1) % 200 == 0:
            tot = sum(v[0] for v in by.values())
            pk = sum(v[1] for v in by.values())
            cr = sum(v[2] for v in by.values())
            print('  %5d probed | parent realized %d | crossed %d (%.1f%% of those)'
                  % (tot, pk, cr, 100.0 * cr / max(pk, 1)), flush=True)
    if fh:
        fh.close()
    print('')
    print('%-12s %7s %9s %9s' % ('depth', 'probed', 'parent ok', 'crossed'))
    for b in sorted(by):
        n0, n1, n2 = by[b]
        print('  %2d-%-7d %7d %9d %9d  (%.1f%% of parent-ok)'
              % (b, b + 3, n0, n1, n2, 100.0 * n2 / max(n1, 1)))
    tot = sum(v[0] for v in by.values())
    pk = sum(v[1] for v in by.values())
    cr = sum(v[2] for v in by.values())
    print('')
    print('CROSSING SUCCESS %d/%d = %.2f%% of rows whose parent we could realize'
          % (cr, pk, 100.0 * cr / max(pk, 1)))
    print('  parent realize %.0f ms   crossing %.1f ms'
          % (1000 * tp / max(tot, 1), 1000 * tc / max(pk, 1)))


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest='cmd', required=True)
    v = sub.add_parser('verify')
    v.add_argument('--rows', type=int, default=2000)
    v.add_argument('--seed', type=int, default=3)
    v.add_argument('--matrix-tests', type=int, default=25)
    v.set_defaults(fn=cmd_verify)
    k = sub.add_parser('walk')
    k.add_argument('--maxdepth', type=int, default=12)
    k.add_argument('--out', default=None)
    k.add_argument('--fast', action='store_true', help='skip hash verification')
    k.set_defaults(fn=cmd_walk)
    q = sub.add_parser('probe')
    q.add_argument('--rows', type=int, default=1500)
    q.add_argument('--seed', type=int, default=17)
    q.add_argument('--out', default=None)
    q.add_argument('--fast', action='store_true')
    q.set_defaults(fn=cmd_probe)
    a = ap.parse_args()
    a.fn(a)


if __name__ == '__main__':
    main()
