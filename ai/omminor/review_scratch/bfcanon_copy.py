#!/usr/bin/env python3
"""INDEPENDENT canonical form: the maximum over the WHOLE group, brute force.

This file shares no code with `ai/omgamma/coverage_checker.py`.  It does not
compute mutable bases, does not refine colours, does not build a sign
lattice and does not use an echelon basis.  It rebuilds the colex basis
order and the action of

    G' = S_n x {0,1}^n x {0,1}

from the definition in OMGAMMA.md section 2, enumerates ALL n! * 2^n * 2
group elements, and returns the maximum of the resulting sign strings under
a fixed total order.  That maximum is by construction a function of the
G'-orbit alone, so two chirotopes have the same brute-force form IFF they
are in the same class.

It is NOT the same canonical form as coverage_checker's key: that one
maximises only over relabellings that respect the colour partition, so the
two forms can differ on a class whose colour-inadmissible relabellings reach
a larger string.  What must agree is the induced PARTITION, and that is what
this file is used to check.

Cost is about 8 s per (8,4) chirotope (40 320 * 512 * 70 byte-operations),
so it is a spot-check tool, not a pipeline.
"""

import os
import sys
from itertools import combinations, permutations

import numpy as np


def colex(n, r):
    return sorted(combinations(range(1, n + 1), r), key=lambda t: tuple(reversed(t)))


def perm_tables(n, r):
    """(P, M) int32 source index and (P, M) uint8 sign-flip bit, one row per
    permutation of {1..n}.

    (sigma . chi)(x_1..x_r) = chi(sigma^{-1} x_1 .. sigma^{-1} x_r).  With
    B = (b_1 < .. < b_r) a colex basis, sigma^{-1}B is a set; sorting it
    costs the sign of the sorting permutation.
    """
    bas = colex(n, r)
    pos = {B: j for j, B in enumerate(bas)}
    M = len(bas)
    perms = list(permutations(range(1, n + 1)))
    IDX = np.empty((len(perms), M), dtype=np.int32)
    SGN = np.empty((len(perms), M), dtype=np.uint8)
    for p, sigma in enumerate(perms):
        # sigma sends i -> sigma[i-1]; sigma^{-1} sends sigma[i-1] -> i
        inv = [0] * (n + 1)
        for i in range(1, n + 1):
            inv[sigma[i - 1]] = i
        for j, B in enumerate(bas):
            img = [inv[b] for b in B]
            # bubble sort, counting inversions
            sg = 0
            a = list(img)
            for i in range(1, len(a)):
                k = i
                while k > 0 and a[k - 1] > a[k]:
                    a[k - 1], a[k] = a[k], a[k - 1]
                    sg ^= 1
                    k -= 1
            IDX[p, j] = pos[tuple(a)]
            SGN[p, j] = sg
    return IDX, SGN


def sign_tables(n, r):
    """(2^n * 2, M) uint8: the XOR mask of every (reorientation, global sign)."""
    bas = colex(n, r)
    M = len(bas)
    out = np.empty((1 << (n + 1), M), dtype=np.uint8)
    for e in range(1 << n):
        row = np.zeros(M, dtype=np.uint8)
        for j, B in enumerate(bas):
            row[j] = bin(e & sum(1 << (b - 1) for b in B)).count('1') & 1
        out[e] = row
        out[e | (1 << n)] = row ^ 1
    return out


class BF(object):
    def __init__(self, n, r):
        self.n, self.r = n, r
        self.IDX, self.SGN = perm_tables(n, r)
        self.SIG = sign_tables(n, r)
        self.M = self.IDX.shape[1]

    def form(self, bits, chunk=1000):
        """bits: (M,) uint8 of 1/0 -> (hi, lo) ints, the maximum over G'."""
        bits = np.asarray(bits, dtype=np.uint8)
        M = self.M
        h = M // 2
        best = (-1, -1)
        for a in range(0, len(self.IDX), chunk):
            b = min(a + chunk, len(self.IDX))
            R = bits[self.IDX[a:b]] ^ self.SGN[a:b]          # (k, M)
            X = R[:, None, :] ^ self.SIG[None, :, :]         # (k, 512, M)
            X = X.reshape(-1, M)
            hi = np.zeros(len(X), dtype=np.uint64)
            for j in range(h):
                hi = (hi << np.uint64(1)) | X[:, j].astype(np.uint64)
            mh = hi.max()
            sel = hi == mh
            lo = np.zeros(int(sel.sum()), dtype=np.uint64)
            Xs = X[sel]
            for j in range(h, M):
                lo = (lo << np.uint64(1)) | Xs[:, j].astype(np.uint64)
            cand = (int(mh), int(lo.max()))
            if cand > best:
                best = cand
        return best


def bits_from_string(s):
    a = np.frombuffer(s.strip().encode(), dtype=np.uint8)
    return (a == ord('+')).astype(np.uint8)


if __name__ == '__main__':
    # smoke test at (4,6): the brute-force partition must have exactly the
    # published number of classes, and must be invariant under the action.
    import itertools
    import random
    n, r = 6, 3
    bf = BF(n, r)
    M = bf.M
    print('(%d,%d): M=%d, %d permutations, %d sign elements'
          % (r, n, M, len(bf.IDX), len(bf.SIG)))
    # enumerate all valid uniform chirotopes at (6,3) by brute force
    bas = colex(n, r)
    pos = {B: j for j, B in enumerate(bas)}
    rels = []
    for L in combinations(range(1, n + 1), r - 2):
        rest = [x for x in range(1, n + 1) if x not in L]
        for a, b, c, d in combinations(rest, 4):
            trip = []
            for (x, y, z, w, ex) in ((a, b, c, d, 1), (a, c, b, d, -1), (a, d, b, c, 1)):
                def ss(t):
                    aa = list(t); sg = 1
                    for i in range(1, len(aa)):
                        k = i
                        while k > 0 and aa[k - 1] > aa[k]:
                            aa[k - 1], aa[k] = aa[k], aa[k - 1]; sg = -sg; k -= 1
                    return tuple(aa), sg
                s1, g1 = ss(L + (x, y)); s2, g2 = ss(L + (z, w))
                trip.append((pos[s1], pos[s2], ex * g1 * g2))
            rels.append(trip)
    forms = set()
    nvalid = 0
    for v in range(1 << M):
        chi = np.array([1 if (v >> j) & 1 else -1 for j in range(M)], dtype=np.int8)
        ok = True
        for trip in rels:
            s = [t[2] * int(chi[t[0]]) * int(chi[t[1]]) for t in trip]
            if s[0] == s[1] == s[2]:
                ok = False
                break
        if not ok:
            continue
        nvalid += 1
        forms.add(bf.form((chi > 0).astype(np.uint8), chunk=720))
    print('valid uniform chirotopes: %d ; brute-force classes: %d (published 4)'
          % (nvalid, len(forms)))
    sys.exit(0 if len(forms) == 4 else 1)
