#!/usr/bin/env python3
"""PART B #2 -- independent re-derivation of certaudit.py's reconciliation,
from the raw shard files and st.dat, using the reviewer's OWN parsing
(full json.loads, not certaudit.py's byte-offset heuristic) and the
reviewer's OWN validated key encoding (mycodec.py, cross-checked in
codec_crosscheck.py against 20,000 real rows and 200,000 random patterns).

Does NOT import certaudit.py.  Uses numpy only for the catalog arrays
(hi.npy/lo.npy/st.dat, generic uint64/uint8 storage) and a sort+searchsorted
join -- a different join strategy from certaudit.py's own sort+searchsorted
is not really available that is meaningfully "more independent" (it is a
generic algorithm, not project logic), so what is actually independent here
is: full JSON parsing instead of byte-offset slicing, the reviewer's own
encode formula (validated separately), and fresh Python code for every
step, including the duplicate/missing analysis and the row-clustering
diagnostic the sweep49.py write-ordering bug (see PART A writeup) predicts.
"""
import glob
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
STATE = os.path.normpath(os.path.join(HERE, '..', '..', 'omreal', 'sweep_state'))
CERTS = os.path.join(STATE, 'certs')
NROWS, M = 9276595, 126

_TR = str.maketrans('+-', '10')


def key_of_str(chi_str):
    """chi string -> (hi, lo) uint64 pair, via the reviewer's OWN validated
    formula (same semantics as mycodec.encode_key, fast path)."""
    v = int(chi_str.translate(_TR), 2)
    return v >> 64, v & 0xFFFFFFFFFFFFFFFF


def main():
    t0 = time.time()
    hi = np.asarray(np.load(os.path.join(STATE, 'hi.npy'), mmap_mode='r'))
    lo = np.asarray(np.load(os.path.join(STATE, 'lo.npy'), mmap_mode='r'))
    st = np.asarray(np.memmap(os.path.join(STATE, 'st.dat'), dtype=np.uint8,
                              mode='r', shape=(NROWS,)))
    assert len(hi) == NROWS and len(lo) == NROWS

    cat = np.zeros(NROWS, dtype=[('hi', '<u8'), ('lo', '<u8')])
    cat['hi'] = hi
    cat['lo'] = lo
    order = np.argsort(cat, order=('hi', 'lo'))
    scat = cat[order]
    # sanity: catalog keys must themselves be unique (distinct classes)
    dup_in_catalog = int((scat[1:] == scat[:-1]).sum())
    print('[B2] catalog keys sorted; duplicate keys IN THE CATALOG ITSELF: %d'
          % dup_in_catalog)
    print('     (%.1f s)' % (time.time() - t0))

    paths = sorted(glob.glob(os.path.join(CERTS, '*.jsonl')))
    n = 0
    all_hi = []
    all_lo = []
    all_kind = []
    residue_rows_claimed = []
    parse_fail = 0
    t1 = time.time()
    for p in paths:
        cnt = 0
        with open(p, 'r') as fh:
            for line in fh:
                line = line.strip()
                if not line:
                    continue
                try:
                    rec = json.loads(line)
                except Exception:
                    parse_fail += 1
                    continue
                chi = rec.get('chi')
                if chi is None or len(chi) != M:
                    parse_fail += 1
                    continue
                a, b = key_of_str(chi)
                all_hi.append(a)
                all_lo.append(b)
                v = rec.get('verdict')
                all_kind.append(1 if v == 'REALIZABLE' else
                                 (3 if v == 'NON_REALIZABLE' else 4))
                if v == 'RESIDUE' and 'row' in rec:
                    residue_rows_claimed.append(int(rec['row']))
                n += 1
                cnt += 1
        print('  %-16s %9d records (cumulative %d, %.1f s)'
              % (os.path.basename(p), cnt, n, time.time() - t1))

    ck = np.zeros(n, dtype=[('hi', '<u8'), ('lo', '<u8')])
    ck['hi'] = np.array(all_hi, dtype=np.uint64)
    ck['lo'] = np.array(all_lo, dtype=np.uint64)
    kind = np.array(all_kind, dtype=np.uint8)
    print('[B2] parsed %d certificate records (parse failures: %d)  (%.1f s)'
          % (n, parse_fail, time.time() - t1))

    pos = np.searchsorted(scat, ck)
    pos = np.clip(pos, 0, NROWS - 1)
    hitmask = (scat['hi'][pos] == ck['hi']) & (scat['lo'][pos] == ck['lo'])
    rows = order[pos]
    rows_matched = rows.copy()
    rows_matched[~hitmask] = -1

    print('[B2] certificates: %d;  matched to a catalog row: %d;  unmatched: %d'
          % (n, int(hitmask.sum()), int((~hitmask).sum())))
    if (~hitmask).any():
        bad_idx = np.flatnonzero(~hitmask)[:10]
        print('     first unmatched keys:', [(int(ck['hi'][i]), int(ck['lo'][i]))
                                              for i in bad_idx])

    covered = np.zeros(NROWS, dtype=np.int32)
    good_rows = rows_matched[hitmask]
    np.add.at(covered, good_rows, 1)
    dup = int((covered > 1).sum())
    miss = np.flatnonzero(covered == 0)
    print('[B2] rows with >=1 certificate: %d;  rows with >1 (DUPLICATED): %d;  '
          'rows with 0 (MISSING): %d'
          % (int((covered > 0).sum()), dup, len(miss)))

    if dup:
        dup_rows = np.flatnonzero(covered > 1)[:10]
        print('     first duplicated rows:', dup_rows.tolist(),
              'counts:', covered[dup_rows].tolist())

    # status breakdown of the missing rows
    by_status = {}
    names = {0: 'TODO', 1: 'REALIZABLE(walk)', 2: 'REALIZABLE(repair)',
             3: 'NON_REALIZABLE', 4: 'OPEN'}
    for k, nm in names.items():
        by_status[nm] = int((st[miss] == k).sum())
    print('[B2] missing rows by sweep status: %s' % by_status)

    # row-index clustering diagnostic: contiguous runs vs scattered.
    # This directly tests the "buffer-tail lost at a kill point" mechanism
    # sweep49.py's do_chunk write-ordering predicts (see PART A writeup):
    # Z[i] and st[i] are durable per-row writes, but the JSONL text is
    # buffered and flushed only once per whole CHUNK, so loss should show
    # up as a handful of near-contiguous ROW INDICES (the tail of whichever
    # chunk was in flight when a worker was stopped), not as independent
    # uniformly-scattered draws.
    miss_sorted = np.sort(miss)
    if len(miss_sorted) > 1:
        gaps = np.diff(miss_sorted)
        runs = 1 + int((gaps > 1).sum())
        print('[B2] missing-row clustering: %d missing rows fall into %d '
              'maximal runs of consecutive row indices' % (len(miss_sorted), runs))
        # describe each run
        run_starts = [0] + list(np.flatnonzero(gaps > 1) + 1)
        run_ends = list(np.flatnonzero(gaps > 1) + 1) + [len(miss_sorted)]
        runs_desc = []
        for s, e in zip(run_starts, run_ends):
            runs_desc.append((int(miss_sorted[s]), int(miss_sorted[e - 1]), e - s))
        print('     runs (first_row, last_row, length):')
        for rr in runs_desc[:60]:
            print('      ', rr)
        if len(runs_desc) > 60:
            print('      ... and %d more runs' % (len(runs_desc) - 60))

    # cross-check: RESIDUE rows explicitly named in records vs "missing"
    # rows/rows with status OPEN
    print('[B2] RESIDUE records with an explicit row field: %d, distinct: %d'
          % (len(residue_rows_claimed), len(set(residue_rows_claimed))))

    out = {
        'certificates': int(n),
        'parse_failures': int(parse_fail),
        'matched': int(hitmask.sum()),
        'unmatched': int((~hitmask).sum()),
        'rows_covered': int((covered > 0).sum()),
        'rows_duplicated': dup,
        'rows_missing': int(len(miss)),
        'missing_by_status': by_status,
        'missing_rows_all': [int(v) for v in miss_sorted.tolist()],
        'duplicate_in_catalog_itself': dup_in_catalog,
        'seconds': round(time.time() - t0, 1),
    }
    with open(os.path.join(HERE, 'my_certaudit_result.json'), 'w') as fh:
        json.dump(out, fh, indent=1)
    print('\n[B2] wrote my_certaudit_result.json (%.1f s total)'
          % (time.time() - t0))


if __name__ == '__main__':
    main()
