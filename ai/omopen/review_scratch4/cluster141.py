#!/usr/bin/env python3
"""Refine the missing-row clustering diagnostic.

do_chunk processes rows in WAVE-RANK order (rows of a fixed depth, sorted by
absolute row index), sliced into consecutive chunks of `chunk` (default
8000) rows apiece.  Rows of one chunk are therefore consecutive in WAVE
RANK, not in absolute row index (since same-depth rows are a sparse,
scattered subset of 0..NROWS-1).  So the right clustering tests are:
  (a) do the 141 missing rows concentrate in a small number of DEPTH values
      (consistent with a small number of kill events, one wave in flight
      each time), vs spread over all 27 depths ~uniformly?
  (b) within a depth, gap-cluster the missing rows' absolute indices with a
      generous threshold and see if they form a handful of tight
      neighborhoods (consistent with one lost chunk-tail buffer each) vs.
      being spread uniformly through that depth's row range.
"""
import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
STATE = os.path.normpath(os.path.join(HERE, '..', '..', 'omreal', 'sweep_state'))
NROWS = 9276595

with open(os.path.join(HERE, 'my_certaudit_result.json')) as fh:
    aud = json.load(fh)
miss = np.array(sorted(aud['missing_rows_all']), dtype=np.int64)
print('missing rows: %d' % len(miss))

depth = np.load(os.path.join(STATE, 'depth.npy'), mmap_mode='r')
dmiss = np.asarray(depth[miss])
u, c = np.unique(dmiss, return_counts=True)
print('\nby DEPTH:')
for d, cnt in zip(u.tolist(), c.tolist()):
    print('   depth %2d : %d missing rows' % (d, cnt))
print('distinct depths touched: %d of max depth %d' % (len(u), int(depth[:].max())))

# gap-cluster with a generous threshold (rows in the same wave-rank chunk
# come from a *sparse* same-depth subsequence -- allow a wide gap)
for THRESH in (50, 500, 5000, 50000):
    runs = []
    cur = [int(miss[0])]
    for v in miss[1:].tolist():
        if v - cur[-1] <= THRESH:
            cur.append(v)
        else:
            runs.append(cur)
            cur = [v]
    runs.append(cur)
    sizes = sorted((len(r) for r in runs), reverse=True)
    print('\ngap threshold %d : %d clusters, sizes (desc, top 20): %s'
          % (THRESH, len(runs), sizes[:20]))

# also: within EACH depth, are the rows for that depth themselves clustered?
print('\nper-depth clustering (gap threshold 20000 on absolute row index):')
for d in u.tolist():
    rows_d = sorted(int(v) for v in miss[dmiss == d].tolist())
    runs = []
    cur = [rows_d[0]]
    for v in rows_d[1:]:
        if v - cur[-1] <= 20000:
            cur.append(v)
        else:
            runs.append(cur)
            cur = [v]
    runs.append(cur)
    print('  depth %2d: %d rows -> %d clusters, sizes %s, span %d..%d'
          % (d, len(rows_d), len(runs), sorted((len(r) for r in runs), reverse=True),
             rows_d[0], rows_d[-1]))
