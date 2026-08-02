#!/usr/bin/env python3
"""Does the float64 completion LP ever DISAGREE with the exact oracle?

The float LP in `weaponA._lp_interior` is "exactly verified success,
heuristic numerical failure" (OPEN_ATTACK.md s3.1).  The regime where the
heuristic failure is expected to bite is LARGE INTEGER ENTRIES: deletion
entries reach 2**22, so the 3x3 minors that make up the completion rows can
exceed 2**68 and float64 cannot represent them, let alone their near
cancellations at t ~ 0.

Fresh (8,4) realizations do not live in that regime.  WALKED configurations
(deep in a hill-climb, entries at the 2**22 cap) and configurations
TRANSPORTED from the sweep's store do.  This probe samples all three and
compares, per configuration:

    float:  weaponA._lp_interior(A) -> t > 0 ?
    exact:  exactlp.exact_feasible(A) -> 'FEASIBLE' ?

A disagreement in the direction float=infeasible / exact=FEASIBLE is a
completion the bulk search would have thrown away.  It is also, directly, a
realization of the class.

    python probe_exact_vs_float.py [--rows 12] [--steps 40] [--out FILE]
"""

import argparse
import json
import os
import statistics
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


def probe(nrows, steps, seed, out):
    rows = catalog.rows_with_status(catalog.OPEN)
    rng = np.random.default_rng(seed)
    pick = rng.choice(len(rows), size=min(nrows, len(rows)), replace=False)
    rows = np.asarray(rows)[np.sort(pick)]
    CHI = catalog.chi_of_rows(rows)
    arrays = catalog.arrays()
    S = weaponA.Searcher(seed=seed)

    stats = {}                       # regime -> [n, agree, f_only, e_only]
    disagreements = []
    times = {}

    def record(regime, A, entry_max):
        d = stats.setdefault(regime, [0, 0, 0, 0])
        t0 = time.time()
        x, t = weaponA._lp_interior(A)
        tf = time.time() - t0
        t0 = time.time()
        st, cert = exactlp.exact_feasible(A)
        te = time.time() - t0
        times.setdefault(regime, [[], []])
        times[regime][0].append(tf)
        times[regime][1].append(te)
        fl = bool(x is not None and t is not None and t > 0)
        ex = (st == 'FEASIBLE')
        d[0] += 1
        if fl == ex:
            d[1] += 1
        elif fl and not ex:
            d[2] += 1
        else:
            d[3] += 1
        return fl, ex, cert, entry_max

    for r, chi in zip(rows, CHI):
        r = int(r)
        dels = [weaponA.Deletion(chi, S.g9, S.g8, p) for p in range(9)]

        # ---- regime 1: fresh (8,4) realizations (small entries) --------
        for dele in dels[:3]:
            Y = S.fresh_deletion(dele, seed=r * 13 + dele.p)
            if Y is None or not weaponA.brackets_ok(Y, dele.chi8, S.g8):
                continue
            Zi = np.array(dele.embed(Y, [0] * 4).tolist(), dtype=np.int64)
            A, _ = weaponA.completion_rows(Zi, chi, S.g9, dele.p)
            em = int(np.abs(Y).max())
            fl, ex, cert, _ = record('fresh', A, em)
            if fl != ex:
                disagreements.append(dict(row=r, p=dele.p, regime='fresh',
                                          float_feasible=fl, exact=ex,
                                          entry_max=em,
                                          x=[int(v) for v in cert]
                                          if ex else None))

            # ---- regime 2: WALKED, deep, large entries -----------------
            Yw = Y
            blk = ()
            for k in range(steps):
                Yw = S.walk_deletion(Yw, dele, steps=1, blockers=blk)
                if k % 8 != 7:
                    continue
                if not weaponA.brackets_ok(Yw, dele.chi8, S.g8):
                    break
                Zi = np.array(dele.embed(Yw, [0] * 4).tolist(), dtype=np.int64)
                A, bs = weaponA.completion_rows(Zi, chi, S.g9, dele.p)
                em = int(np.abs(Yw).max())
                fl, ex, cert, _ = record('walk%d' % steps, A, em)
                if fl != ex:
                    disagreements.append(
                        dict(row=r, p=dele.p, regime='walk',
                             float_feasible=fl, exact=ex, entry_max=em,
                             step=k,
                             Y=[[int(v) for v in rr] for rr in Yw],
                             x=[int(v) for v in cert] if ex else None))
                if ex:
                    break

        # ---- regime 3: transported from the sweep's store --------------
        for (W, j) in S.store_mutants(r, chi, arrays, kids=None):
            for p in S.g9.bases0[j]:
                dele = dels[p]
                Yw = dele.restrict(W)
                Zi = np.array(dele.embed(Yw, [0] * 4).tolist(), dtype=np.int64)
                A, _ = weaponA.completion_rows(Zi, chi, S.g9, p)
                em = int(np.abs(Yw).max())
                fl, ex, cert, _ = record('store', A, em)
                if fl != ex:
                    disagreements.append(
                        dict(row=r, p=int(p), regime='store',
                             float_feasible=fl, exact=ex, entry_max=em,
                             Y=[[int(v) for v in rr] for rr in Yw],
                             x=[int(v) for v in cert] if ex else None))

    res = {'rows_sampled': [int(v) for v in rows], 'steps': steps,
           'seed': seed, 'regimes': {}, 'disagreements': disagreements}
    print('%-10s %8s %8s %10s %10s   %-22s %-22s' %
          ('regime', 'n', 'agree', 'f>e', 'e>f', 'float s (med/max)',
           'exact s (med/max)'))
    for k in sorted(stats):
        n, ag, fo, eo = stats[k]
        tf, te = times[k]
        print('%-10s %8d %8d %10d %10d   %10.4f %10.4f  %10.4f %10.4f'
              % (k, n, ag, fo, eo, statistics.median(tf), max(tf),
                 statistics.median(te), max(te)))
        res['regimes'][k] = {'n': n, 'agree': ag, 'float_only': fo,
                             'exact_only': eo,
                             'float_median_s': statistics.median(tf),
                             'exact_median_s': statistics.median(te)}
    print('\ntotal disagreements: %d' % len(disagreements))
    for d in disagreements[:20]:
        print('  row %d p %d regime %s float=%s exact=%s entrymax=%d'
              % (d['row'], d['p'], d['regime'], d['float_feasible'],
                 d['exact'], d['entry_max']))
    if out:
        with open(out, 'w') as fh:
            json.dump(res, fh, indent=1)
        print('wrote %s' % out)
    return res


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--rows', type=int, default=12)
    ap.add_argument('--steps', type=int, default=40)
    ap.add_argument('--seed', type=int, default=20260802)
    ap.add_argument('--out', default=os.path.join(HERE, 'data',
                                                  'probe_exact_vs_float.json'))
    a = ap.parse_args()
    probe(a.rows, a.steps, a.seed, a.out)


if __name__ == '__main__':
    main()
