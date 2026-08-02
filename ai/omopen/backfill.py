#!/usr/bin/env python3
"""Emit certificates for the rows the sweep decided but never wrote down.

`certaudit.py` found 9,276,454 certificate records covering 9,276,454
distinct catalog rows -- 141 short of the 9,276,595 the status array marks
decided, all 141 of them REALIZABLE(walk).  Nothing is wrong with those
rows: the sweep's shared `Z.dat` still holds the realization it found for
each one, only the JSONL line was lost (a worker's buffer at shutdown).

So the fix needs no search.  Read `Z[row]` -- READ-ONLY, the sweep is not
running -- recompute all 126 brackets exactly, and if they match the
catalog chirotope, write the certificate this directory's checkers accept.
Any row whose stored matrix does NOT verify is realized from scratch with
weapon A instead, and that is reported separately, because a stored matrix
that fails its own brackets would be a real defect rather than a lost line.

    python backfill.py
"""

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
import weaponA                                              # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, 'data')
N, R = 9, 4


def main():
    with open(os.path.join(DATA, 'certaudit.json')) as fh:
        aud = json.load(fh)
    rows = aud['missing_rows_sample']
    if len(rows) != aud['rows_missing']:
        raise SystemExit('certaudit.json truncated the missing list '
                         '(%d of %d); widen the sample before running this'
                         % (len(rows), aud['rows_missing']))
    print('backfilling %d rows' % len(rows))

    arrays = catalog.arrays()
    Z = arrays['Z']
    st = np.asarray(arrays['st'])
    CHI = catalog.chi_of_rows(rows)
    g9 = weaponA.rz.Geom(N, R)
    S = None
    out = os.path.join(DATA, 'certs_backfill.jsonl')
    open(out, 'w').close()

    from_store, from_search, failed = 0, 0, []
    t0 = time.time()
    for r, chi in zip(rows, CHI):
        M = np.asarray(Z[r], dtype=np.int64)
        rec = None
        if weaponA.brackets_ok(M, chi, g9):
            rec = weaponA.realizable_record(N, R, catalog.chi_string(chi), M)
            from_store += 1
        else:
            if S is None:
                S = weaponA.Searcher(seed=20260802)
            W, log = S.attack(chi, budget=120.0, row=int(r), arrays=arrays)
            if W is not None:
                rec = weaponA.realizable_record(
                    N, R, catalog.chi_string(chi), W)
                from_search += 1
            else:
                failed.append(int(r))
        if rec is not None:
            rec['row'] = int(r)
            rec['status'] = catalog.STATUS[int(st[r])]
            with open(out, 'a') as fh:
                fh.write(json.dumps(rec) + '\n')

    print('  verified straight from the sweep\'s stored Z.dat : %d'
          % from_store)
    print('  re-realized with weapon A (stored matrix bad)   : %d'
          % from_search)
    print('  still unrealized                                : %d %s'
          % (len(failed), failed[:10]))
    print('  %.1f s -> %s' % (time.time() - t0, os.path.basename(out)))
    json.dump({'rows': len(rows), 'from_store': from_store,
               'from_search': from_search, 'failed': failed},
              open(os.path.join(DATA, 'backfill.json'), 'w'), indent=1)
    return 0 if not failed else 1


if __name__ == '__main__':
    sys.exit(main())
