#!/usr/bin/env python3
"""PART B #3 (extended) -- the 141 backfilled rows are the LEAST independently
covered population: they never went through sweep49.py's own do_chunk
verification-then-write path in the normal sense (their JSONL line was lost
to the buffering gap identified in the Part A writeup), and their
certificate was reissued by backfill.py using realize.py's OWN
exact_bracket_signs function -- the same code the producer already trusts.

This script re-derives ALL 141 (not a sample) completely independently:
  1. read Z[row] DIRECTLY from the sweep's raw Z.dat memmap (int32, shape
     (NROWS,4,9)) -- bypassing certs_backfill.jsonl's own 'matrix' field
     entirely;
  2. decode row -> chirotope by reading hi.npy/lo.npy DIRECTLY and applying
     mycodec.decode_key (the reviewer's own, independently-validated
     codec) -- bypassing certs_backfill.jsonl's own 'chi' field entirely;
  3. recompute all 126 brackets with mycodec's Leibniz-expansion
     determinant and compare to the freshly-decoded chirotope;
  4. separately, ALSO check that certs_backfill.jsonl's stated chi/matrix
     for that row agree with what was independently derived in (1)/(2), so
     a mismatch between "what backfill.py wrote" and "what Z.dat/the
     catalog actually contain" cannot hide.
"""
import json
import os
import sys
import time

sys.dont_write_bytecode = True
os.environ.setdefault('PYTHONDONTWRITEBYTECODE', '1')
for _v in ('OMP_NUM_THREADS', 'MKL_NUM_THREADS', 'OPENBLAS_NUM_THREADS',
           'NUMEXPR_NUM_THREADS'):
    os.environ.setdefault(_v, '1')

import numpy as np                                          # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
OMREAL_SCRATCH = os.path.normpath(os.path.join(HERE, '..', '..', 'omreal', 'review_scratch'))
sys.path.insert(0, OMREAL_SCRATCH)
import mycodec as mc                                        # noqa: E402

STATE = os.path.normpath(os.path.join(HERE, '..', '..', 'omreal', 'sweep_state'))
DATA = os.path.normpath(os.path.join(HERE, '..', 'data'))
N, R, M, NROWS = 9, 4, 126, 9276595


def main():
    backfill_path = os.path.join(DATA, 'certs_backfill.jsonl')
    recs = {}
    with open(backfill_path) as fh:
        for line in fh:
            line = line.strip()
            if line:
                r = json.loads(line)
                recs[int(r['row'])] = r
    print('[B3-141] certs_backfill.jsonl has %d records' % len(recs))

    hi = np.load(os.path.join(STATE, 'hi.npy'), mmap_mode='r')
    lo = np.load(os.path.join(STATE, 'lo.npy'), mmap_mode='r')
    Z = np.memmap(os.path.join(STATE, 'Z.dat'), dtype=np.int32, mode='r',
                  shape=(NROWS, R, N))
    st = np.memmap(os.path.join(STATE, 'st.dat'), dtype=np.uint8, mode='r',
                   shape=(NROWS,))
    names = {0: 'TODO', 1: 'REALIZABLE(walk)', 2: 'REALIZABLE(repair)',
             3: 'NON_REALIZABLE', 4: 'OPEN'}

    bases = mc.colex_bases(N, R)
    n_ok = n_bad = 0
    bad = []
    t0 = time.time()
    for row in sorted(recs):
        rec = recs[row]
        # (2) decode the catalog row's chirotope DIRECTLY, my own codec
        my_chi = mc.decode_key(int(hi[row]), int(lo[row]), M)
        # (1) read the STORED matrix directly from Z.dat, bypassing the cert file
        Zrow = [[int(v) for v in Z[row][i]] for i in range(R)]
        my_sgs = mc.bracket_signs(Zrow, N, R, bases)
        want = [1 if c == '+' else -1 for c in my_chi]
        row_ok = True
        reasons = []
        if my_sgs is None:
            row_ok = False
            reasons.append('Z.dat matrix has a vanishing bracket')
        elif my_sgs != want:
            j = next(i for i in range(M) if my_sgs[i] != want[i])
            row_ok = False
            reasons.append('Z.dat matrix bracket %s (idx %d) sign %+d != '
                           'catalog-decoded %+d' % (bases[j], j, my_sgs[j], want[j]))
        # (4) cross-check backfill.py's OWN written record against ground truth
        if rec['chi'] != my_chi:
            row_ok = False
            reasons.append('certs_backfill.jsonl chi != my independent decode '
                           'of hi.npy/lo.npy for this row')
        rec_mat = [[int(v) for v in r_] for r_ in rec['matrix']]
        if rec_mat != Zrow:
            row_ok = False
            reasons.append('certs_backfill.jsonl matrix != Z.dat[row] '
                           '(the certificate does not match the sweep state)')
        sweep_status = names.get(int(st[row]), '?')
        if sweep_status != 'REALIZABLE(walk)':
            row_ok = False
            reasons.append('sweep status is %s, expected REALIZABLE(walk)' % sweep_status)
        if row_ok:
            n_ok += 1
        else:
            n_bad += 1
            bad.append({'row': row, 'reasons': reasons})

    dt = time.time() - t0
    print('[B3-141] checked all %d backfilled rows directly against Z.dat + '
          'hi.npy/lo.npy (%.1f s)' % (len(recs), dt))
    print('   fully independently verified : %d' % n_ok)
    print('   REJECTED                      : %d' % n_bad)
    if bad:
        print('\n   *** FAILURES ***')
        for b in bad[:30]:
            print('    ', b)

    ok = (n_bad == 0 and len(recs) == 141)
    print('\n[B3-141] %s' % ('ALL 141 INDEPENDENTLY CONFIRMED' if ok
                              else '*** PROBLEM -- SEE ABOVE ***'))
    out = {'n': len(recs), 'ok': n_ok, 'bad': n_bad, 'bad_rows': bad,
           'seconds': round(dt, 1)}
    with open(os.path.join(HERE, 'verify_141_backfill_result.json'), 'w') as fh:
        json.dump(out, fh, indent=1)
    return 0 if ok else 1


if __name__ == '__main__':
    sys.exit(main())
