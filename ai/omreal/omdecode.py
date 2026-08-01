#!/usr/bin/env python3
"""Catalog access for ai/omreal -- REUSED DECODER, nothing else.

PROVENANCE / TRUST BOUNDARY
===========================
Every routine in this file that turns catalog bytes into a chirotope is a
thin wrapper over ``ai/omgamma/coverage_checker.py``.  We import and call:

    coverage_checker.build_tables(n, r)   -- colex basis order, the 3-term
                                             Grassmann-Pluecker table T['C']
    coverage_checker.decode_keys(T, hi, lo)
    coverage_checker.gp_parities(T, S)
    coverage_checker.gp_valid(p1, p2, p3)

and NOTHING else from that project.  We deliberately do NOT import
omgamma's generator side (core/canon/flip/runbig/...); coverage_checker
refuses to load if any of those are already imported, which is a feature.

We do NOT inherit omgamma's realizability opinion, because it has none:
omgamma is purely combinatorial (mutation-graph connectivity).  The
realizability verdicts produced by ai/omreal are new and are re-checked by
``checkcert.py``, which shares NO code with this file or with omgamma --
it rederives the colex order, the GP relations and the determinant signs
from scratch in the standard library.

Catalogs used
-------------
  ai/omgamma/data/cat_3_8.txt   135 classes, one sign string per line
  ai/omgamma/data/cat_3_9.txt   4382
  ai/omgamma/data/cat_4_8.txt   2628
  ai/omgamma/data/coverage_4_9/coverage_4_9.npz
        key_hi/key_lo/stab, 9,276,595 rows.  MANIFEST.json calls this the
        LEGACY artifact (tree_4_9.npz is THE certificate) but pins the
        SHA-256 of these three raw arrays under `array_sha256`, so we
        verify those hashes before sampling.  Replaying the tree to
        regenerate the same keys costs hours; the hash check buys the same
        provenance for a second.
"""

import hashlib
import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
OMGAMMA = os.path.normpath(os.path.join(HERE, '..', 'omgamma'))
DATA = os.path.join(OMGAMMA, 'data')


def _cc():
    """Import ai/omgamma/coverage_checker.py (the reused decoder)."""
    if OMGAMMA not in sys.path:
        sys.path.insert(0, OMGAMMA)
    import coverage_checker           # noqa: E402
    return coverage_checker


_TABLES = {}


def tables(n, r):
    """coverage_checker.build_tables(n, r), memoised."""
    key = (n, r)
    if key not in _TABLES:
        _TABLES[key] = _cc().build_tables(n, r)
    return _TABLES[key]


def bases(n, r):
    """The C(n,r) bases as ascending tuples, in COLEX order."""
    return tables(n, r)['bases']


# ----------------------------------------------------------------------
# chirotopes as +-1 int8 vectors over the colex bases
# ----------------------------------------------------------------------

def signs_from_string(s):
    """'++-+...' -> int8 array of +-1, one entry per colex basis."""
    a = np.frombuffer(s.strip().encode(), dtype=np.uint8)
    if not np.isin(a, [ord('+'), ord('-')]).all():
        raise ValueError('sign string contains something other than + and -')
    return np.where(a == ord('+'), np.int8(1), np.int8(-1))


def string_from_signs(chi):
    return ''.join('+' if v > 0 else '-' for v in chi)


def signs_from_keys(n, r, key_hi, key_lo):
    """(B,) uint64 pairs -> (B, M) int8 array of +-1."""
    T = tables(n, r)
    S = _cc().decode_keys(T, np.asarray(key_hi, dtype=np.uint64),
                          np.asarray(key_lo, dtype=np.uint64))
    return np.where(S == 1, np.int8(1), np.int8(-1))


def keys_from_signs(n, r, CHI):
    """(B,M) +-1 -> (hi, lo) uint64 arrays, MANIFEST key_encoding."""
    T = tables(n, r)
    S = (np.asarray(CHI) > 0).astype(np.uint8)
    return _cc().encode_keys(T, S)


def gp_check(n, r, CHI):
    """(B,) bool: every 3-term GP condition holds (uniform chirotope)."""
    T = tables(n, r)
    S = (np.asarray(CHI) > 0).astype(np.uint8)
    p1, p2, p3 = _cc().gp_parities(T, S)
    return _cc().gp_valid(p1, p2, p3)


def gp_parity_table(n, r, chi):
    """For ONE chirotope: (C, P) with C = T['C'] and P = (nc,3) parities.

    Parity 0 means that term of the relation  T1 + T2 + T3 = 0  is +1.
    Uniform validity is exactly "no row of P is constant".
    """
    T = tables(n, r)
    S = (np.asarray(chi) > 0).astype(np.uint8)[None, :]
    p1, p2, p3 = _cc().gp_parities(T, S)
    P = np.stack([p1[0], p2[0], p3[0]], axis=1)
    return T['C'], P


# ----------------------------------------------------------------------
# catalog loading
# ----------------------------------------------------------------------

def load_catalog_txt(n, r):
    """Small catalogs shipped as one sign string per line."""
    path = os.path.join(DATA, 'cat_%d_%d.txt' % (r, n))
    with open(path) as fh:
        lines = [ln.strip() for ln in fh if ln.strip()]
    M = len(bases(n, r))
    out = np.empty((len(lines), M), dtype=np.int8)
    for i, ln in enumerate(lines):
        if len(ln) != M:
            raise ValueError('%s line %d: length %d, expected %d'
                             % (path, i, len(ln), M))
        out[i] = signs_from_string(ln)
    return out


COVERAGE_49 = os.path.join(DATA, 'coverage_4_9', 'coverage_4_9.npz')
MANIFEST_49 = os.path.join(DATA, 'coverage_4_9', 'MANIFEST.json')


def load_coverage_4_9(verify=True):
    """(key_hi, key_lo, stab) for the 9,276,595 (4,9) classes.

    With verify=True the SHA-256 of each raw array is checked against
    MANIFEST.json['array_sha256'] -- the same manifest that pins the tree
    certificate -- so a corrupted or substituted npz is caught here.
    """
    man = json.load(open(MANIFEST_49))
    z = np.load(COVERAGE_49)
    arrays = {k: z[k] for k in ('key_hi', 'key_lo', 'stab')}
    if verify:
        want = man['array_sha256']
        for k, a in arrays.items():
            got = hashlib.sha256(np.ascontiguousarray(a).tobytes()).hexdigest()
            if got != want[k]:
                raise ValueError('coverage_4_9.npz array %r hash mismatch:\n'
                                 '  manifest %s\n  actual   %s'
                                 % (k, want[k], got))
    if len(arrays['key_hi']) != man['count']:
        raise ValueError('row count != manifest count')
    return arrays['key_hi'], arrays['key_lo'], arrays['stab']
