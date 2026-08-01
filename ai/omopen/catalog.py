#!/usr/bin/env python3
"""READ-ONLY access to the (4,9) catalog and to the live sweep's state.

HARD CONSTRAINT: `ai/omreal` is being written by a running four-worker
sweep.  Nothing in this directory ever opens a file under `ai/omreal` for
writing, and the memmaps below are opened mode='r'.

`sweep49.py report --enumerate-open` would have enumerated the OPEN set for
us, but it WRITES `sweep_state/open_classes.txt`.  Under "write nothing"
that is not acceptable even though the sweep never reads that file, so the
enumeration is reimplemented here from the same two arrays it uses
(`st.dat` and the catalog keys).  The counts agree; see OPEN_ATTACK.md s2.1.
"""

import os
import sys

# Importing ai/omreal modules would otherwise drop .pyc files into
# ai/omreal/__pycache__, which is a WRITE into the read-only sweep
# directory.  Belt and braces: the caller is also told to export
# PYTHONDONTWRITEBYTECODE=1.
sys.dont_write_bytecode = True

for _v in ('OMP_NUM_THREADS', 'MKL_NUM_THREADS', 'OPENBLAS_NUM_THREADS',
           'NUMEXPR_NUM_THREADS'):
    os.environ.setdefault(_v, '1')

import numpy as np                                          # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
OMREAL = os.path.normpath(os.path.join(HERE, '..', 'omreal'))
STATE = os.path.join(OMREAL, 'sweep_state')
N, R, NROWS = 9, 4, 9276595

TODO, WALK, REPAIR, NONREAL, OPEN = 0, 1, 2, 3, 4
STATUS = {TODO: 'TODO', WALK: 'REALIZABLE(walk)', REPAIR: 'REALIZABLE(repair)',
          NONREAL: 'NON_REALIZABLE', OPEN: 'OPEN'}


def _omreal():
    if OMREAL not in sys.path:
        sys.path.insert(0, OMREAL)


def omdecode():
    _omreal()
    import omdecode as m
    return m


def realize_mod():
    _omreal()
    import realize as m
    return m


def treewalk_mod():
    _omreal()
    import treewalk as m
    return m


_C = {}


def arrays():
    """The sweep's shared arrays, memmapped READ-ONLY."""
    if not _C:
        L = lambda k: np.load(os.path.join(STATE, k + '.npy'), mmap_mode='r')
        for k in ('hi', 'lo', 'parent', 'flip', 'sigma', 'eps', 'gsgn',
                  'depth'):
            _C[k] = L(k)
        _C['st'] = np.memmap(os.path.join(STATE, 'st.dat'), dtype=np.uint8,
                             mode='r', shape=(NROWS,))
        _C['Z'] = np.memmap(os.path.join(STATE, 'Z.dat'), dtype=np.int32,
                            mode='r', shape=(NROWS, R, N))
    return _C


def status_counts():
    a = arrays()
    s = np.asarray(a['st'])
    return {k: int((s == k).sum()) for k in STATUS}


def rows_with_status(k):
    return np.flatnonzero(np.asarray(arrays()['st']) == k)


def chi_of_rows(rows):
    a = arrays()
    od = omdecode()
    rows = np.asarray(rows)
    return od.signs_from_keys(N, R, np.asarray(a['hi'][rows]),
                              np.asarray(a['lo'][rows]))


def chi_string(chi):
    return ''.join('+' if v > 0 else '-' for v in chi)


def children_index():
    """(order, start) so that children of row i are order[start[i]:start[i+1]].

    Built from `parent.npy`; ~9.3M int32 sort, about 1.5 s and 110 MB.
    """
    a = arrays()
    par = np.asarray(a['parent']).astype(np.int64)
    # the root carries parent = -1; give it a bucket of its own at the end so
    # it neither breaks bincount nor is counted as anyone's child
    par = np.where(par < 0, NROWS, par)
    order = np.argsort(par, kind='stable')
    cnt = np.bincount(par, minlength=NROWS + 1)[:NROWS]
    start = np.zeros(NROWS + 1, dtype=np.int64)
    np.cumsum(cnt, out=start[1:])
    return order, start
