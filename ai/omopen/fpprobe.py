#!/usr/bin/env python3
"""How far does the coefficient-space final polynomial hierarchy get?

    python fpprobe.py [--limit N] [--deg3] [--l1deg3]

Runs weapon B2 (`fpoly.py`) over the OPEN classes and, as controls, over
classes the sweep certified NON_REALIZABLE and REALIZABLE.  The point is a
measurement, not a certificate: the answer this produces is expected to be
"nothing at these degrees", and the value is in knowing that rather than
assuming it.

Also reports the structural fact that makes the degree-2 rung vacuous over
the three-term relations, and checks it: the monomial {B, B'} of a term of
a three-term relation determines the relation, because L = B cap B' and
{a,b,c,d} = B triangle B'.  So no two of the 1260 relations share a
monomial, the incidence matrix has exactly one nonzero per row, and
A lambda <= 0 forces lambda = 0 for every chirotope.
"""

import argparse
import json
import os
import sys
import time

sys.dont_write_bytecode = True
for _v in ('OMP_NUM_THREADS', 'MKL_NUM_THREADS', 'OPENBLAS_NUM_THREADS',
           'NUMEXPR_NUM_THREADS'):
    os.environ.setdefault(_v, '1')

import numpy as np                                          # noqa: E402

import catalog                                              # noqa: E402
import fpoly                                                # noqa: E402
import gordan                                               # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, 'data')
N, R = 9, 4


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--limit', type=int, default=25)
    ap.add_argument('--deg3', action='store_true')
    ap.add_argument('--l1deg3', action='store_true')
    a = ap.parse_args()

    sup = {lv: gordan.Support(N, R, lv, verify=False) for lv in ('L0', 'L1')}
    out = {'when': time.strftime('%Y-%m-%dT%H:%M:%S'), 'limit': a.limit}

    # the structural fact, checked
    rng = np.random.default_rng(5)
    c0 = catalog.chi_of_rows(
        rng.choice(catalog.rows_with_status(catalog.WALK), 1))[0]
    A, cols, mons = fpoly.build_system(sup['L0'].idents, c0, 2)
    out['deg2_L0_incidence'] = {'monomials': int(A.shape[0]),
                                'columns': int(A.shape[1]),
                                'nonzeros': int(A.nnz),
                                'one_per_row': bool(A.nnz == A.shape[0])}
    print('degree-2 over the three-term relations: %d monomials, %d columns, '
          '%d nonzeros -> %s'
          % (A.shape[0], A.shape[1], A.nnz,
             'exactly one column per monomial, so the LP is INFEASIBLE for '
             'every chirotope' if A.nnz == A.shape[0] else 'shared monomials'))

    # the positive control
    rigged, cert, info = fpoly.positive_control(c0, sup['L1'])
    out['positive_control'] = {'found': cert is not None,
                               'generators': info.get('support'),
                               'seconds': info.get('seconds')}
    print('positive control (a rigged monochrome relation): %s, %s generators'
          % ('FOUND' if cert else 'NOT FOUND', info.get('support')))
    if cert is not None:
        with open(os.path.join(DATA, 'fp_positive_control.jsonl'), 'w') as fh:
            fh.write(json.dumps(fpoly.fp_record(
                N, R, catalog.chi_string(rigged), cert, 2, sup['L1'])) + '\n')

    # the populations
    pops = {}
    if os.path.exists(os.path.join(DATA, 'open_set.txt')):
        rows, CH = [], []
        for line in open(os.path.join(DATA, 'open_set.txt')):
            p = line.split()
            if len(p) == 3:
                rows.append(int(p[0]))
                CH.append(np.array([1 if ch == '+' else -1 for ch in p[2]],
                                   dtype=np.int8))
        pops['OPEN'] = (rows[:a.limit], CH[:a.limit])
    for tag, st in (('NON_REALIZABLE', catalog.NONREAL),
                    ('REALIZABLE', catalog.WALK)):
        r = rng.choice(catalog.rows_with_status(st), a.limit, replace=False)
        pops[tag] = ([int(x) for x in r], list(catalog.chi_of_rows(r)))

    plan = [(2, 'L0'), (2, 'L1')]
    if a.deg3:
        plan.append((3, 'L0'))
    if a.l1deg3:
        plan.append((3, 'L1'))
    out['runs'] = []
    found_path = os.path.join(DATA, 'fp_found.jsonl')
    open(found_path, 'w').close()
    for tag, (rows, CH) in pops.items():
        for (d, lv) in plan:
            hit = 0
            t0 = time.time()
            last = {}
            for c in CH:
                cert, info = fpoly.find_fp(c, degree=d, level=lv,
                                           sup=sup[lv])
                hit += cert is not None
                last = info
                if cert is not None:
                    # ANY hit must be independently checkable, and a hit on a
                    # REALIZABLE class would be fatal -- so every one is
                    # written out with the population it came from.
                    r = fpoly.fp_record(N, R, catalog.chi_string(c), cert,
                                        d, sup[lv])
                    r['population'] = tag
                    with open(found_path, 'a') as fh:
                        fh.write(json.dumps(r) + '\n')
            rec = {'population': tag, 'degree': d, 'level': lv,
                   'n': len(CH), 'found': hit,
                   'columns': last.get('ncol'), 'monomials': last.get('nmon'),
                   'seconds_each': round((time.time() - t0) / max(len(CH), 1), 2)}
            out['runs'].append(rec)
            print('%-16s FP(%d) at %s: %d/%d found  (%d columns, %d monomials, '
                  '%.2f s each)' % (tag, d, lv, hit, len(CH),
                                    last.get('ncol') or -1,
                                    last.get('nmon') or -1,
                                    rec['seconds_each']), flush=True)
    with open(os.path.join(DATA, 'fp_probe.json'), 'w') as fh:
        json.dump(out, fh, indent=1)
    print('-> data/fp_probe.json')


if __name__ == '__main__':
    main()
