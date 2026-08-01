#!/usr/bin/env python3
"""Single-element minors of uniform chirotopes, and their identification.

WHAT THIS FILE DOES
===================
Given a uniform rank-r chirotope chi on E = {1..n} as a sign string over the
C(n,r) bases in COLEX order, produce

  * DELETION   chi \\ e   -- rank r, ground set E \\ {e}, relabelled to
                            {1..n-1} by the unique order-preserving bijection
  * CONTRACTION chi / e  -- rank r-1, ground set E \\ {e}, same relabelling

and identify the resulting class against a catalog of canonical keys.

WHY THE DELETION IS A SUBSEQUENCE
---------------------------------
Let phi: E \\ {e} -> {1..n-1} be the order-preserving bijection.  A basis of
chi \\ e is an r-subset B of E \\ {e}; by definition (chi\\e)(phi B) = chi(B)
where both tuples are written in ascending order.  Because phi is
order-preserving it maps ascending tuples to ascending tuples, so NO
permutation sign appears.  Colex order compares reversed tuples
lexicographically, and phi is a strictly increasing map, so it also preserves
colex order.  Hence:

    the sign string of chi \\ e is exactly the subsequence of the sign string
    of chi at the positions of the bases avoiding e, in the same order.

That is `DEL_IDX[e]` below, computed once from the two colex orders and then
cross-checked against an independently built position map (`_check_del_idx`).

CONTRACTION
-----------
(chi / e)(x_1 .. x_{r-1}) = chi(e, x_1 .. x_{r-1}) for x_i in E \\ {e}
ascending.  Sorting (e, x_1 .. x_{r-1}) into ascending order costs the sign
of that permutation, which is (-1)^{#{i : x_i < e}}; this is `CON_SGN[e]`.
(The global sign of a contraction is a convention -- both chi/e and -chi/e
are the same UOM -- and identification is by G'-class, which contains the
global sign, so the convention cannot affect any verdict here.)

TRUST BOUNDARY
--------------
Canonicalization is delegated to `ai/omgamma/coverage_checker.py`
(`build_tables`, `canon_batch`, `encode_keys`, `gp_parities`, `gp_valid`),
the standalone checker that shares no code with omgamma's generator side.
The same decoder was already the one `ai/omreal` used, so the (4,8) catalog
keys, the sweep's (4,9) keys and the keys computed here are all in one
convention by construction.

`bfcanon.py` in this directory is an INDEPENDENT canonicalizer written from
the group definition (maximum over the whole of Gbar, no colour refinement,
no echelon sign lattice); it is used to spot-check that the partition
induced here is the right one.
"""

import os
import sys
from itertools import combinations

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(HERE, '..', '..'))
OMGAMMA = os.path.join(REPO, 'ai', 'omgamma')
OMREAL = os.path.join(REPO, 'ai', 'omreal')
DATA = os.path.join(OMGAMMA, 'data')


def cc():
    """Import ai/omgamma/coverage_checker.py (the reused, independent decoder)."""
    if OMGAMMA not in sys.path:
        sys.path.insert(0, OMGAMMA)
    import coverage_checker                                # noqa: E402
    return coverage_checker


_T = {}


def tables(n, r):
    key = (n, r)
    if key not in _T:
        _T[key] = cc().build_tables(n, r)
    return _T[key]


def colex(n, r):
    return sorted(combinations(range(1, n + 1), r), key=lambda t: tuple(reversed(t)))


def signs_from_string(s):
    a = np.frombuffer(s.strip().encode(), dtype=np.uint8)
    if not np.isin(a, [ord('+'), ord('-')]).all():
        raise ValueError('sign string contains something other than + and -')
    return np.where(a == ord('+'), np.int8(1), np.int8(-1))


def string_from_signs(chi):
    return ''.join('+' if v > 0 else '-' for v in np.asarray(chi))


def bits_from_string(s):
    """'++-+' -> uint8 array of 1/0 (the encoding coverage_checker uses)."""
    a = np.frombuffer(s.strip().encode(), dtype=np.uint8)
    if not np.isin(a, [ord('+'), ord('-')]).all():
        raise ValueError('sign string contains something other than + and -')
    return (a == ord('+')).astype(np.uint8)


# ----------------------------------------------------------------------
# the minor index tables
# ----------------------------------------------------------------------

def deletion_tables(n, r):
    """DEL_IDX[e-1] = positions of the (n,r) colex bases avoiding e, in the
    colex order of the (n-1, r) bases they become."""
    big = colex(n, r)
    small = colex(n - 1, r)
    spos = {B: j for j, B in enumerate(small)}
    out = np.empty((n, len(small)), dtype=np.int32)
    for e in range(1, n + 1):
        phi = {}
        k = 0
        for x in range(1, n + 1):
            if x != e:
                k += 1
                phi[x] = k
        row = np.full(len(small), -1, dtype=np.int32)
        for j, B in enumerate(big):
            if e in B:
                continue
            row[spos[tuple(phi[x] for x in B)]] = j
        if (row < 0).any():
            raise AssertionError('deletion index table incomplete')
        out[e - 1] = row
    return out


def _check_del_idx(n, r, DEL):
    """Independent rebuild of DEL_IDX: filter the big colex list, then assert
    the surviving subsequence is already in the small colex order."""
    big = colex(n, r)
    small = colex(n - 1, r)
    for e in range(1, n + 1):
        keep = [j for j, B in enumerate(big) if e not in B]
        if len(keep) != len(small):
            raise AssertionError('wrong count of surviving bases')
        phi = {}
        k = 0
        for x in range(1, n + 1):
            if x != e:
                k += 1
                phi[x] = k
        img = [tuple(phi[x] for x in big[j]) for j in keep]
        if img != small:
            raise AssertionError(
                'the surviving subsequence is NOT the small colex order at e=%d' % e)
        if not np.array_equal(np.asarray(keep, dtype=np.int32), DEL[e - 1]):
            raise AssertionError('DEL_IDX disagrees with the filtered order at e=%d' % e)
    return True


def contraction_tables(n, r):
    """(CON_IDX, CON_SGN): (chi/e) at small basis j is
    CON_SGN[e-1, j] * chi[CON_IDX[e-1, j]]."""
    big = colex(n, r)
    bpos = {B: j for j, B in enumerate(big)}
    small = colex(n - 1, r - 1)
    idx = np.empty((n, len(small)), dtype=np.int32)
    sgn = np.empty((n, len(small)), dtype=np.int8)
    for e in range(1, n + 1):
        inv = {}
        k = 0
        for x in range(1, n + 1):
            if x != e:
                k += 1
                inv[k] = x
        for j, Bs in enumerate(small):
            orig = tuple(inv[x] for x in Bs)
            below = sum(1 for x in orig if x < e)
            full = tuple(sorted(orig + (e,)))
            idx[e - 1, j] = bpos[full]
            sgn[e - 1, j] = -1 if (below % 2) else 1
    return idx, sgn


# ----------------------------------------------------------------------
# batch minor extraction
# ----------------------------------------------------------------------

class Minors(object):
    """All single-element deletions / contractions of (n, r) chirotopes."""

    def __init__(self, n, r, check=True):
        self.n, self.r = n, r
        self.DEL = deletion_tables(n, r)
        self.CON_IDX, self.CON_SGN = contraction_tables(n, r)
        if check:
            _check_del_idx(n, r, self.DEL)

    def deletions_bits(self, S):
        """(B, M) uint8 sign bits -> (B, n, M') uint8 sign bits."""
        S = np.asarray(S, dtype=np.uint8)
        return S[:, self.DEL]                       # (B, n, M')

    def contractions_bits(self, S):
        """(B, M) uint8 sign bits -> (B, n, M'') uint8 sign bits.

        A sign of -1 in CON_SGN flips the bit."""
        S = np.asarray(S, dtype=np.uint8)
        flip = (self.CON_SGN < 0).astype(np.uint8)  # (n, M'')
        return S[:, self.CON_IDX] ^ flip[None, :, :]


# ----------------------------------------------------------------------
# canonical keys
# ----------------------------------------------------------------------

def canon_keys(n, r, S, batch=1000):
    """(B, M) uint8 sign bits -> (hi, lo, nargmax, valid) uint64/int64/bool.

    Batched to keep the placement enumeration inside canon_batch bounded.
    """
    C = cc()
    T = tables(n, r)
    S = np.ascontiguousarray(np.asarray(S, dtype=np.uint8))
    B = len(S)
    hi = np.empty(B, dtype=np.uint64)
    lo = np.empty(B, dtype=np.uint64)
    na = np.empty(B, dtype=np.int64)
    va = np.empty(B, dtype=bool)
    for a in range(0, B, batch):
        b = min(a + batch, B)
        h, l, c, v, _tot, _wp, _wc = C.canon_batch(T, S[a:b].copy())
        hi[a:b], lo[a:b], na[a:b], va[a:b] = h, l, c, v
    return hi, lo, na, va


def gp_ok(n, r, S):
    """(B, M) uint8 sign bits -> (B,) bool: every 3-term GP condition holds."""
    C = cc()
    T = tables(n, r)
    p1, p2, p3 = C.gp_parities(T, np.asarray(S, dtype=np.uint8))
    return C.gp_valid(p1, p2, p3)


def catalog_keys(n, r, path=None):
    """Canonical (hi, lo) for every line of data/cat_<r>_<n>.txt, plus the
    strings.  The catalog lines are themselves canonical representatives, so
    this is also a fixed-point check on the canonicalizer."""
    path = path or os.path.join(DATA, 'cat_%d_%d.txt' % (r, n))
    lines = [ln.strip() for ln in open(path) if ln.strip()]
    S = np.array([bits_from_string(ln) for ln in lines], dtype=np.uint8)
    hi, lo, na, va = canon_keys(n, r, S)
    if not va.all():
        raise AssertionError('catalog contains an invalid chirotope')
    # fixed-point check: the canonical key of a catalog rep must decode back
    # to the rep itself.
    D = cc().decode_keys(tables(n, r), hi, lo)
    if not np.array_equal(D, S):
        bad = int(np.flatnonzero((D != S).any(axis=1))[0])
        raise AssertionError('catalog line %d is not its own canonical key' % bad)
    return lines, hi, lo, na


def key128(hi, lo):
    """A single Python int per row, for dict keys."""
    return (int(hi) << 64) | int(lo)
