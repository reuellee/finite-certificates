#!/usr/bin/env python3
"""Reconcile the sweep's certificate shards against its status array.

Not part of deciding the residue -- this is the boundary statement the final
tally needs.  `st.dat` says how many rows the sweep DECIDED; the certificate
shards say how many decisions it WROTE DOWN.  Those are different claims and
an adversarial reviewer asks for both.

Method: each certificate carries the 126-sign chirotope string.  Re-encode it
into the catalog's 128-bit key (bit j = [chi(B_j) = +1], bases in colex
order) and match it against `sweep_state/{hi,lo}.npy`.  Read-only on
ai/omreal throughout; the only writes are into ai/omopen/data.

This is a RECONCILIATION count, not a validity check: it confirms every
decided row has exactly one certificate on file, and says nothing about
whether that certificate's `matrix`/`bfp` content is itself correct -- that
is checkcert.py/fpcheck.py/fastverify.py's job, run separately over the
same shards. (An earlier revision parsed by byte-offset substring search
instead of json.loads, which the 2026-08-03 adversarial review showed could
silently misclassify a corrupted or truncated record; switched to real JSON
parsing so a malformed line raises loudly instead. The review's own
independent full-corpus scan found 0 parse failures across all 9,276,454
lines either way, so this changes robustness, not any reported number.)

    python certaudit.py
"""

import glob
import json
import os
import sys
import time

sys.dont_write_bytecode = True
for _v in ('OMP_NUM_THREADS', 'MKL_NUM_THREADS', 'OPENBLAS_NUM_THREADS',
           'NUMEXPR_NUM_THREADS'):
    os.environ.setdefault(_v, '1')

import numpy as np                                          # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, 'data')
OMREAL = os.path.normpath(os.path.join(HERE, '..', 'omreal'))
STATE = os.path.join(OMREAL, 'sweep_state')
CERTS = os.path.join(STATE, 'certs')
NROWS, M = 9276595, 126
STATUS = {0: 'TODO', 1: 'REALIZABLE(walk)', 2: 'REALIZABLE(repair)',
          3: 'NON_REALIZABLE', 4: 'OPEN'}

# chi string -> 128-bit key, in two 64-bit halves.  A 126-character string of
# '+'/'-' becomes an integer whose bit (M-1-j) is 1 iff character j is '+'.
_TR = bytes.maketrans(b'+-', b'10')


def key_of(chi_bytes):
    v = int(chi_bytes.translate(_TR), 2)
    return v >> 64, v & 0xFFFFFFFFFFFFFFFF


def main():
    t0 = time.time()
    hi = np.load(os.path.join(STATE, 'hi.npy'), mmap_mode='r')
    lo = np.load(os.path.join(STATE, 'lo.npy'), mmap_mode='r')
    st = np.memmap(os.path.join(STATE, 'st.dat'), dtype=np.uint8, mode='r',
                   shape=(NROWS,))

    cat = np.zeros(NROWS, dtype=[('hi', '<u8'), ('lo', '<u8')])
    cat['hi'] = np.asarray(hi)
    cat['lo'] = np.asarray(lo)
    order = np.argsort(cat, order=('hi', 'lo'))
    scat = cat[order]
    print('catalog keys sorted (%.0f s)' % (time.time() - t0), flush=True)

    cap = 9600000
    ck = np.zeros(cap, dtype=[('hi', '<u8'), ('lo', '<u8')])
    kind = np.zeros(cap, dtype=np.uint8)      # 1 real, 3 nonreal, 4 residue
    n = 0
    for p in sorted(glob.glob(os.path.join(CERTS, '*.jsonl'))):
        with open(p, 'rb') as fh:
            for lineno, line in enumerate(fh, 1):
                if not line.strip():
                    continue
                rec = json.loads(line)          # raises loudly, not silently
                c = rec['chi'].encode('ascii')
                if len(c) != M:
                    raise ValueError('%s:%d: chi length %d != %d'
                                      % (p, lineno, len(c), M))
                a, b = key_of(c)
                ck[n] = (a, b)
                verdict = rec.get('verdict', '')
                if verdict == 'NON_REALIZABLE':
                    kind[n] = 3
                elif verdict == 'REALIZABLE':
                    kind[n] = 1
                else:
                    kind[n] = 4
                n += 1
        print('  %-18s cumulative %d records (%.0f s)'
              % (os.path.basename(p), n, time.time() - t0), flush=True)
    ck, kind = ck[:n], kind[:n]

    pos = np.searchsorted(scat, ck)
    pos = np.clip(pos, 0, NROWS - 1)
    hitmask = (scat['hi'][pos] == ck['hi']) & (scat['lo'][pos] == ck['lo'])
    rows = order[pos]
    rows[~hitmask] = -1
    print('certificates: %d;  matched to a catalog row: %d;  unmatched: %d'
          % (n, int(hitmask.sum()), int((~hitmask).sum())), flush=True)

    covered = np.zeros(NROWS, dtype=np.uint8)
    good = rows[hitmask]
    np.add.at(covered, good, 1)
    dup = int((covered > 1).sum())
    miss = np.flatnonzero(covered == 0)
    print('rows with >=1 certificate: %d;  rows with >1: %d;  rows with 0: %d'
          % (int((covered > 0).sum()), dup, len(miss)))

    stv = np.asarray(st)
    by = {}
    for k, nm in STATUS.items():
        by[nm] = int((stv[miss] == k).sum()) if len(miss) else 0
    print('missing rows by sweep status: %s' % by)

    # do the certificate verdicts agree with the status array?
    agree = {}
    kk = kind[hitmask]
    for k, nm in STATUS.items():
        sel = stv[good] == k
        if not sel.any():
            continue
        u, c = np.unique(kk[sel], return_counts=True)
        agree[nm] = {int(a): int(b) for a, b in zip(u, c)}
    print('certificate kind by sweep status (1=REALIZABLE, '
          '3=NON_REALIZABLE, 4=RESIDUE):')
    for k, v in agree.items():
        print('   %-20s %s' % (k, v))

    out = {'certificates': int(n),
           'matched': int(hitmask.sum()),
           'unmatched': int((~hitmask).sum()),
           'rows_covered': int((covered > 0).sum()),
           'rows_duplicated': dup,
           'rows_missing': len(miss),
           'missing_by_status': by,
           'missing_rows_sample': [int(v) for v in miss[:200]],
           'kind_by_status': {k: v for k, v in agree.items()},
           'seconds': round(time.time() - t0, 1)}
    with open(os.path.join(DATA, 'certaudit.json'), 'w') as fh:
        json.dump(out, fh, indent=1)
    print('\nwrote data/certaudit.json (%.0f s)' % (time.time() - t0))


if __name__ == '__main__':
    main()
