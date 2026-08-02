#!/usr/bin/env python3
"""Are the completion rows the RIGHT rows?

Every exact INFEASIBLE certificate this session records is a true statement
about the integer matrix ``A`` that `weaponA.completion_rows` builds.  If
that construction had a sign or index convention wrong, the certificate
would still be internally valid and would still mean nothing.  Successes are
self-checking -- a FEASIBLE x is embedded and all 126 brackets are
recomputed -- but FAILURES are not, and failures are what a STILL_OPEN
verdict is made of.

So the rows are checked directly, against ground truth:

    take a KNOWN integer realization Z of chi;
    delete column p to get Y;
    build A = completion_rows(Y, chi, p);
    then A . Z[:, p] MUST be strictly positive in every coordinate,

because Z[:, p] is by construction a valid ninth point for Y.  This is an
exact integer test with no solver in it at all.  And as a second layer,
`exactlp.exact_feasible(A)` must return FEASIBLE on every one of those rows,
since a solution exists.

An INFEASIBLE verdict from a cone that provably contains a point, or a
nonpositive dot product, would invalidate every negative result in this
directory.

    python rowcheck.py [--limit 200]
"""

import argparse
import json
import os
import sys

sys.dont_write_bytecode = True
for _v in ('OMP_NUM_THREADS', 'MKL_NUM_THREADS', 'OPENBLAS_NUM_THREADS',
           'NUMEXPR_NUM_THREADS'):
    os.environ.setdefault(_v, '1')

import numpy as np                                          # noqa: E402

import exactlp                                              # noqa: E402
import weaponA                                              # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, 'data')
N, R = 9, 4


def run(files, limit):
    g9 = weaponA.rz.Geom(N, R)
    n_cls = n_pair = 0
    bad_dot = []
    bad_lp = []
    for f in files:
        if not os.path.exists(f):
            continue
        with open(f) as fh:
            for line in fh:
                line = line.strip()
                if not line:
                    continue
                rec = json.loads(line)
                if rec.get('verdict') != 'REALIZABLE':
                    continue
                if limit and n_cls >= limit:
                    break
                n_cls += 1
                chi = np.array([1 if c == '+' else -1 for c in rec['chi']],
                               dtype=np.int8)
                Z = [[int(v) for v in row] for row in rec['matrix']]
                for p in range(N):
                    # blank out column p: completion_rows ignores it anyway,
                    # but zeroing it makes the test honest about what Y is
                    Y = [list(row) for row in Z]
                    for i in range(R):
                        Y[i][p] = 0
                    A, bs = weaponA.completion_rows(
                        np.array(Y, dtype=object), chi, g9, p)
                    xp = [Z[i][p] for i in range(R)]
                    n_pair += 1
                    worst = None
                    for row in A:
                        s = sum(a * b for a, b in zip(row, xp))
                        if worst is None or s < worst:
                            worst = s
                        if s <= 0:
                            bad_dot.append((rec['chi'][:16], p, s))
                            break
                    st, cert = exactlp.exact_feasible(A)
                    if st != 'FEASIBLE':
                        bad_lp.append((rec['chi'][:16], p))
    return n_cls, n_pair, bad_dot, bad_lp


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--limit', type=int, default=200)
    ap.add_argument('files', nargs='*')
    a = ap.parse_args()
    files = a.files or [os.path.join(DATA, 'certs_realizable.jsonl'),
                        os.path.join(DATA, 'validation_realizable.jsonl')]
    n_cls, n_pair, bad_dot, bad_lp = run(files, a.limit)
    print('rowcheck: %d known realizations x 9 deletions = %d (Y, p) pairs'
          % (n_cls, n_pair))
    print('  A . x_p > 0 in every coordinate            : %d violations'
          % len(bad_dot))
    print('  exactlp says FEASIBLE on every such cone   : %d violations'
          % len(bad_lp))
    for b in bad_dot[:5]:
        print('    *** dot: %s... p=%d  min A.x = %s' % b)
    for b in bad_lp[:5]:
        print('    *** lp : %s... p=%d' % b)
    ok = not bad_dot and not bad_lp
    out = {'classes': n_cls, 'pairs': n_pair, 'bad_dot': bad_dot[:20],
           'bad_lp': bad_lp[:20], 'PASS': ok}
    with open(os.path.join(DATA, 'rowcheck.json'), 'w') as fh:
        json.dump(out, fh, indent=1)
    print('rowcheck: %s' % ('PASS' if ok else '*** FAIL ***'))
    return 0 if ok else 1


if __name__ == '__main__':
    sys.exit(main())
