#!/usr/bin/env python3
"""Diagnostics for the (4,9) residue -- what ARE the classes we cannot settle?

    python diag.py deletions certs.jsonl [--limit N]
    python diag.py hammer    certs.jsonl [--limit N] [--tries T] [--sweeps S]

deletions
    For each class, delete each of the 9 elements in turn and settle the
    resulting uniform (4,8) class with the SAME pipeline.  The (4,8)
    pipeline is exhaustively validated (2628/2628 settled, matching the
    published 2604/24), so this profile is exact.

    Why it matters twice over:
      * a non-realizable deletion PROVES the 9-element class non-realizable;
      * the GP relations of a deletion are a SUBSET of the class's, so a
        BFP for the deletion is already a BFP for the class.  Hence a
        residue class must have all 9 deletions realizable, and a
        BFP-certified class whose deletions are all realizable is one where
        BFP found a genuinely 9-element obstruction.  The split between
        those two tells us whether BFP is still doing new work at n = 9.

hammer
    Re-run the realization search on residue classes at a much larger
    budget, to separate "the searcher gave up" from "there is nothing to
    find".
"""

import argparse
import json
import sys
import time
from itertools import combinations

import numpy as np

sys.path.insert(0, __file__.rsplit('\\', 1)[0].rsplit('/', 1)[0])
import omdecode                                            # noqa: E402
import realize as rz                                       # noqa: E402
import bfp as bfpmod                                       # noqa: E402


def deletion_map(n, r):
    """For each k, the (M8,) index array picking chi(4,9) -> chi(4,8)."""
    b9 = sorted(combinations(range(1, n + 1), r), key=lambda t: tuple(reversed(t)))
    i9 = {B: j for j, B in enumerate(b9)}
    b8 = sorted(combinations(range(1, n), r), key=lambda t: tuple(reversed(t)))
    out = []
    for k in range(1, n + 1):
        keep = [x for x in range(1, n + 1) if x != k]
        idx = np.array([i9[tuple(keep[x - 1] for x in B)] for B in b8],
                       dtype=np.int64)
        out.append(idx)
    return out


def settle(chi, geom, gp, tries=4, sweeps=30, rerolls=5):
    Z, _ = rz.realize(chi, geom, tries=tries, sweeps=sweeps, rerolls=rerolls)
    if Z is not None:
        return 'R'
    cert, _ = bfpmod.find_bfp(chi, gp)
    return 'N' if cert is not None else '?'


def cmd_deletions(recs, limit):
    n, r = 9, 4
    dm = deletion_map(n, r)
    g8 = rz.Geom(8, 4)
    gp8 = bfpmod.GPSystem(8, 4)
    buckets = {}
    for verdict in ('RESIDUE', 'NON_REALIZABLE', 'REALIZABLE'):
        sel = [x for x in recs if x['verdict'] == verdict][:limit]
        if not sel:
            continue
        prof = {}
        for rec in sel:
            chi = omdecode.signs_from_string(rec['chi'])
            res = ''.join(settle(chi[dm[k]], g8, gp8) for k in range(n))
            key = (res.count('R'), res.count('N'), res.count('?'))
            prof[key] = prof.get(key, 0) + 1
        buckets[verdict] = (len(sel), prof)
        print('%-16s %d classes; deletion profiles (nR,nN,n?) -> count:'
              % (verdict, len(sel)))
        for k in sorted(prof, key=lambda t: -prof[t]):
            print('     %s  %d' % (k, prof[k]))
    return buckets


def cmd_hammer(recs, limit, tries, sweeps, rerolls):
    g = rz.Geom(9, 4)
    sel = [x for x in recs if x['verdict'] == 'RESIDUE'][:limit]
    got, ts = 0, []
    for i, rec in enumerate(sel):
        chi = omdecode.signs_from_string(rec['chi'])
        t0 = time.perf_counter()
        Z, _ = rz.realize(chi, g, tries=tries, sweeps=sweeps, rerolls=rerolls,
                          seed=555000 + i)
        ts.append(time.perf_counter() - t0)
        if Z is not None:
            got += 1
            print(json.dumps({'n': 9, 'r': 4, 'chi': rec['chi'],
                              'verdict': 'REALIZABLE',
                              'matrix': [[int(v) for v in row] for row in Z]}),
                  file=open('hammer_wins.jsonl', 'a'))
        if (i + 1) % 5 == 0:
            print('  %d/%d  realized %d   mean %.1f s'
                  % (i + 1, len(sel), got, float(np.mean(ts))), flush=True)
    print('HAMMER tries=%d sweeps=%d: %d/%d residue classes realized, '
          'mean %.1f s/class' % (tries, sweeps, got, len(sel), float(np.mean(ts))))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('cmd', choices=('deletions', 'hammer'))
    ap.add_argument('certs')
    ap.add_argument('--limit', type=int, default=40)
    ap.add_argument('--tries', type=int, default=60)
    ap.add_argument('--sweeps', type=int, default=250)
    ap.add_argument('--rerolls', type=int, default=12)
    a = ap.parse_args()
    recs = [json.loads(l) for l in open(a.certs) if l.strip()]
    if a.cmd == 'deletions':
        cmd_deletions(recs, a.limit)
    else:
        cmd_hammer(recs, a.limit, a.tries, a.sweeps, a.rerolls)


if __name__ == '__main__':
    main()
