"""STANDALONE checker for the omgamma (r,n) coverage certificate.

This file imports NOTHING from this project -- not core.py, canon.py,
flip.py, runbig.py, bigstate.py, ext_count.py, checker*.py.  Only numpy and
the standard library.  Every table it needs (colex basis order, the
three-term Grassmann-Pluecker conditions, the sign lattice, the group
action) is rebuilt here from the definitions restated below, so that a
defect shared with the search programs cannot hide.

WHAT IT VERIFIES, in exact integer arithmetic, over the artifact written by
export_coverage.py:

  (0) every file listed in MANIFEST.json has the recorded SHA-256, and each
      array has the recorded raw-buffer SHA-256;
  (a) every key decodes to a VALID uniform chirotope -- all three-term
      Grassmann-Pluecker sign conditions hold;
  (b) every key is EXTREMAL in its own orbit under the convention recorded
      in the manifest (restated in `canonical_convention.__doc__` below) --
      no admissible relabelling/reorientation of the key produces a larger
      key, and at least one attains it.  This is what makes the list a list
      of distinct CLASSES rather than of chirotopes;
  (c) the keys are strictly increasing, hence sorted AND pairwise distinct;
  (d) each recorded stabilizer order equals |Stab_{G'}(chi)| recomputed here
      by exhaustive enumeration of the admissible relabellings (orbit-
      stabilizer on the colour-restricted transversal: |Stab| = 2^kappa
      times the number of admissible relabellings attaining the maximum);
  (e) the orbit masses sum to the manifest total, and -- when the manifest
      declares the artifact complete -- to 1,722,704,635,330,560 with a
      count of 9,276,595;
  (f) OPTIONAL (--extcount FILE): the tracked single-element extension
      table sums arithmetically to that same target;
  (g) the REACHABILITY WITNESS is a genuine spanning tree: the recorded
      group elements are group elements (sigma a permutation, eps a
      reorientation mask, gsgn a global sign), the parent pointers stay in
      range, there is EXACTLY ONE parentless row, and depth[root] = 0 with
      depth[i] = depth[parent[i]] + 1 everywhere else -- so the parent map
      strictly decreases depth, is acyclic, and every row reaches the root.
      An independent pointer-doubling pass confirms that ancestor chains
      terminate at that same root;
  (h) every recorded tree edge is a genuine MUTATION edge of the quotient
      graph:  for every non-root row i,
          (sigma[i], eps[i], gsgn[i]) . chi_i  ==  mu_{B_flip[i]}(chi_p),
      p = parent[i], exactly, as 126-bit sign vectors.

WHY (a)+(b)+(c)+(d)+(e)+(g)+(h) CERTIFY THAT THE QUOTIENT GRAPH IS
CONNECTED AND COMPLETE.  Vertices of the quotient graph are G'-orbits of
uniform chirotopes; two orbits are adjacent when some representative of
one is a single-basis sign flip of a representative of the other.

  * (h) makes each recorded edge real.  The identity exhibits
    mu_{B_flip[i]}(chi_p) as the image of chi_i under an element of G'.
    Validity is G'-invariant and chi_i is valid by (a), so the mutant is
    valid: B_flip[i] really is a mutable basis of chi_p, and the classes
    of rows p and i really are adjacent.  (No separate mutability check is
    needed, and none is done.)
  * (g) makes the edge set a spanning tree on the listed rows.  A strictly
    depth-decreasing parent map cannot cycle, and iterating it from any
    row must terminate -- at the unique parentless row.  Hence ALL listed
    rows lie in ONE connected component of the quotient graph.
  * (b)+(c)+(d) make the list a list of distinct classes carrying their
    true stabilizer orders, and (e) makes their orbit masses sum to the
    number of labelled uniform chirotopes.  A class outside the list would
    contribute mass of its own, so the sum would fall short: given the
    target, the list is COMPLETE.
  * One component + complete = the quotient graph is connected.

WHAT IT DOES NOT VERIFY.  It does not recompute the extension counts E(c)
themselves; check (f) only confirms that the tracked table adds up.  The
target 1,722,704,635,330,560 enters as a constant.  So the COMPLETENESS
half of the argument above -- and only that half -- remains conditional on
a number this program does not derive.  One-componentness of the listed
catalog, by contrast, is certified outright by (g)+(h) and does not depend
on the target at all.  Check (b) is relative to the manifest's convention:
the unrestricted maximum over all of S_n is not computable at this scale
(~1.5 s/class, ~160 CPU-days), so the certified statement is "extremal
under the documented colour-restricted convention".  That convention is a
well-defined function of the G'-orbit -- see canonical_convention() --
which is all the distinctness argument needs, but the reader has to read
those forty lines rather than take a one-word "canonical" on trust.

USAGE
  python coverage_checker.py --artifact data/coverage_4_9              # full
  python coverage_checker.py --artifact data/coverage_4_9 --sample 100000
  python coverage_checker.py --artifact data/coverage_4_9 --cheap-only
  python coverage_checker.py --artifact data/coverage_4_9 \
        --extcount data/extcount_4_9.jsonl --workers 2 --state .covstate
  python coverage_checker.py --artifact data/coverage_4_9 --witness-only
  python coverage_checker.py --canary --artifact data/coverage_4_9 \
        --work data/canary_coverage        # sabotage suite; must REJECT
  python coverage_checker.py --artifact data/coverage_4_9 --show 0

Checks (a),(b),(d) and (h) are sharded, run on at most --workers processes
(default 4), and checkpointed: each finished shard drops a small JSON in
--state, and a re-run skips it.  Checks (c),(e),(g) are cheap and always
run over every row.
"""
import argparse
import hashlib
import json
import os
import sys
import time
from itertools import combinations, permutations
from math import comb, factorial

import numpy as np

TARGET_MASS_4_9 = 1722704635330560
TARGET_COUNT_4_9 = 9276595


# ======================================================================
# tables, rebuilt from the definitions
# ======================================================================

def build_tables(n, r):
    """All combinatorial tables, from scratch."""
    T = {'n': n, 'r': r}
    bases = sorted(combinations(range(1, n + 1), r),
                   key=lambda t: tuple(reversed(t)))
    T['bases'] = bases
    M = len(bases)
    T['M'] = M
    assert M == comb(n, r)
    bidx = {B: j for j, B in enumerate(bases)}
    T['BAS'] = np.array(bases, dtype=np.uint8)                  # (M,r)
    tab = np.full((n + 1,) * r, -1, dtype=np.int32)
    for j, B in enumerate(bases):
        tab[B] = j
    T['TAB'] = tab

    # --- three-term Grassmann-Pluecker conditions ---------------------
    # For (r-2)-set L and a<b<c<d in the complement the three terms are
    #   T1 = chi(L,a,b)chi(L,c,d),  T2 = -chi(L,a,c)chi(L,b,d),
    #   T3 = chi(L,a,d)chi(L,b,c),
    # and validity (uniform case) is "not all three equal".  Writing the
    # stored bit of a basis as 1 for +1, the parity p_k = 0 means T_k=+1;
    # p_k is an XOR of the two stored bits and a constant absorbing the
    # tuple-sorting signs (and the explicit minus in T2).
    conds = []
    for L in combinations(range(1, n + 1), r - 2):
        rest = [x for x in range(1, n + 1) if x not in L]
        for a, b, c, d in combinations(rest, 4):
            e = {}
            for (x, y) in ((a, b), (c, d), (a, c), (b, d), (a, d), (b, c)):
                st, sg = _sort_sign(L + (x, y))
                e[(x, y)] = (bidx[st], 0 if sg > 0 else 1)
            (i1, n1), (i2, n2) = e[(a, b)], e[(c, d)]
            (i3, n3), (i4, n4) = e[(a, c)], e[(b, d)]
            (i5, n5), (i6, n6) = e[(a, d)], e[(b, c)]
            conds.append((i1, i2, n1 ^ n2,
                          i3, i4, n3 ^ n4 ^ 1,          # the explicit minus
                          i5, i6, n5 ^ n6))
    T['C'] = (np.array(conds, dtype=np.int32) if conds
              else np.zeros((0, 9), dtype=np.int32))
    per = [[] for _ in range(M)]
    for k, (i1, i2, _, i3, i4, _, i5, i6, _) in enumerate(conds):
        for i, slot in ((i1, 0), (i2, 0), (i3, 1),
                        (i4, 1), (i5, 2), (i6, 2)):
            per[i].append(3 * k + slot)
    if conds:
        L0 = len(per[0])
        assert all(len(p) == L0 for p in per), "condition table not uniform"
        T['SLOT'] = np.array(per, dtype=np.int32)               # (M, L0)
    else:
        T['SLOT'] = np.zeros((M, 0), dtype=np.int32)

    # --- sign lattice: reduced row echelon over F2, colex order --------
    # Reorienting element i flips chi on every basis containing i; the
    # global sign flips all M.  The maximum of an affine coset of this
    # span is reached greedily from the reduced echelon form.
    cols = []
    for i in range(1, n + 1):
        v = np.zeros(M, dtype=np.uint8)
        for j, B in enumerate(bases):
            if i in B:
                v[j] = 1
        cols.append(v)
    cols.append(np.ones(M, dtype=np.uint8))
    ech = []
    for v in cols:
        v = v.copy()
        for p, w in ech:
            if v[p]:
                v ^= w
        nz = np.flatnonzero(v)
        if len(nz):
            ech.append((int(nz[0]), v))
    ech.sort(key=lambda t: t[0])
    for a in range(len(ech) - 1, -1, -1):
        pa, wa = ech[a]
        for b in range(a):
            pb, wb = ech[b]
            if wb[pa]:
                ech[b] = (pb, wb ^ wa)
    T['PIV'] = np.array([p for p, _ in ech], dtype=np.int64)
    T['ECH'] = (np.array([w for _, w in ech], dtype=np.uint8)
                if ech else np.zeros((0, M), dtype=np.uint8))
    T['kappa'] = (n + 1) - len(ech)          # dim of the trivially-acting part

    # --- element / pair incidence -------------------------------------
    INB = np.zeros((M, n), dtype=np.int16)
    for j, B in enumerate(bases):
        for x in B:
            INB[j, x - 1] = 1
    T['INB'] = INB
    prs = list(combinations(range(n), 2))
    T['PAIRS'] = prs
    PR = np.zeros((M, len(prs)), dtype=np.int16)
    for j, B in enumerate(bases):
        for q, (x, y) in enumerate(prs):
            if (x + 1) in B and (y + 1) in B:
                PR[j, q] = 1
    T['PR'] = PR
    T['PI'] = np.array([p[0] for p in prs], dtype=np.int64)
    T['PJ'] = np.array([p[1] for p in prs], dtype=np.int64)

    # --- reorientation parity per (eps, basis) ------------------------
    # reorienting the set eps multiplies chi(B) by (-1)^{|eps cap B|};
    # bit (x-1) of eps means "element x is reoriented".
    bm = np.zeros(M, dtype=np.int64)
    for j, B in enumerate(bases):
        for x in B:
            bm[j] |= 1 << (x - 1)
    T['BASMASK'] = bm
    if n <= 20 and (1 << n) * M <= (1 << 26):
        E = np.zeros((1 << n, M), dtype=np.uint8)
        for e in range(1 << n):
            E[e] = [bin(e & int(bm[j])).count('1') & 1 for j in range(M)]
        T['EPSTAB'] = E
    else:                                    # not needed at this scale
        T['EPSTAB'] = None
    return T


def _sort_sign(t):
    a = list(t)
    sg = 1
    for i in range(1, len(a)):
        j = i
        while j > 0 and a[j - 1] > a[j]:
            a[j - 1], a[j] = a[j], a[j - 1]
            sg = -sg
            j -= 1
    return tuple(a), sg


def canonical_convention():
    """The canonical convention, restated (see MANIFEST.json).

    1. A basis is MUTABLE if flipping its sign leaves a valid uniform
       chirotope.  Mutability is invariant under reorientation and global
       negation, and equivariant under relabelling.
    2. deg(i)   = #mutable bases containing i
       m2(i,j)  = #mutable bases containing both i and j.
    3. col_0(i) = deg(i).  Refine at most 3 times:
         comp(i)     = ( col_t(i), sorted multiset over j != i of
                         (m2(i,j), col_t(j)) )
         col_{t+1}(i)= rank of comp(i) among the n composite values,
                       ranks 0,1,... assigned by ascending sort.
       Assign col_{t+1}; then, if the number of distinct colours did not
       increase, stop.
    4. Order the colour classes by (class size ascending, colour rank
       ascending); they occupy positions 1..n in that order.
    5. The canonical key is the MAXIMUM, over all relabellings sending each
       colour class onto its designated block of positions and over all
       reorientations and the global sign, of the resulting key integer.
       |Stab_{G'}| = 2^kappa * #(relabellings attaining that maximum).

    Steps 1-4 depend only on the G'-orbit, so step 5 is a well-defined
    function of the orbit: distinct keys certify distinct classes.
    """


# ======================================================================
# per-batch primitives
# ======================================================================

def decode_keys(T, key_hi, key_lo):
    """(B,) uint64 pairs -> (B,M) uint8 sign bits, bit j = [chi(B_j)=+1]."""
    B = len(key_hi)
    buf = np.empty((B, 16), dtype=np.uint8)
    buf[:, :8] = key_hi.astype('>u8').view(np.uint8).reshape(B, 8)
    buf[:, 8:] = key_lo.astype('>u8').view(np.uint8).reshape(B, 8)
    bits = np.unpackbits(buf, axis=1, bitorder='big')      # (B,128)
    pad = 128 - T['M']
    if bits[:, :pad].any():
        raise ValueError("key has bits above position M-1")
    return np.ascontiguousarray(bits[:, pad:])


def encode_keys(T, S):
    """(P,M) uint8 sign bits -> (hi, lo) uint64 arrays."""
    P = len(S)
    pad = 128 - T['M']
    full = np.zeros((P, 128), dtype=np.uint8)
    full[:, pad:] = S
    packed = np.packbits(full, axis=1, bitorder='big')     # (P,16)
    hi = np.ascontiguousarray(packed[:, :8]).view('>u8').ravel().astype(
        np.uint64)
    lo = np.ascontiguousarray(packed[:, 8:]).view('>u8').ravel().astype(
        np.uint64)
    return hi, lo


def gp_parities(T, S):
    C = T['C']
    if len(C) == 0:
        z = np.zeros((len(S), 0), dtype=np.uint8)
        return z, z, z
    c1 = C[:, 2].astype(np.uint8)[None, :]
    c2 = C[:, 5].astype(np.uint8)[None, :]
    c3 = C[:, 8].astype(np.uint8)[None, :]
    p1 = S[:, C[:, 0]] ^ S[:, C[:, 1]] ^ c1
    p2 = S[:, C[:, 3]] ^ S[:, C[:, 4]] ^ c2
    p3 = S[:, C[:, 6]] ^ S[:, C[:, 7]] ^ c3
    return p1, p2, p3


def gp_valid(p1, p2, p3):
    """(B,) bool: no condition has all three terms equal."""
    if p1.shape[1] == 0:
        return np.ones(len(p1), dtype=bool)
    return ~(((p1 == p2) & (p2 == p3)).any(axis=1))


def mutable_mask(T, p1, p2, p3):
    """(B,M) bool: flipping basis j keeps every condition satisfied."""
    B = len(p1)
    if p1.shape[1] == 0:
        return np.ones((B, T['M']), dtype=bool)
    nc = p1.shape[1]
    bad = np.empty((B, 3 * nc), dtype=bool)
    bad[:, 0::3] = (p2 == p3) & (p1 != p2)
    bad[:, 1::3] = (p1 == p3) & (p2 != p1)
    bad[:, 2::3] = (p1 == p2) & (p3 != p1)
    return ~bad[:, T['SLOT']].any(axis=2)


def colours_batch(T, mut):
    """(B,M) bool mutability -> list of B colour lists (ints), rounds<=3."""
    n = T['n']
    mi = mut.astype(np.int16)
    deg = mi @ T['INB']                          # (B,n)
    pr = mi @ T['PR']                            # (B,npairs)
    B = len(mut)
    m2 = np.zeros((B, n, n), dtype=np.int32)
    m2[:, T['PI'], T['PJ']] = pr
    m2[:, T['PJ'], T['PI']] = pr
    degl = deg.tolist()
    m2l = m2.tolist()
    rng = range(n)
    out = []
    for b in range(B):
        col = degl[b]
        m2b = m2l[b]
        for _ in range(3):
            comp = []
            for i in rng:
                row = m2b[i]
                sig = sorted(row[j] * 128 + col[j] for j in rng if j != i)
                comp.append((col[i],) + tuple(sig))
            rank = {v: t for t, v in enumerate(sorted(set(comp)))}
            new = [rank[c] for c in comp]
            stable = len(set(new)) == len(set(col))
            col = new
            if stable:
                break
        out.append(col)
    return out


def placements(T, col):
    """All admissible relabellings for one class.

    Returns a list of tuples `placed` with placed[p-1] = the ground-set
    element (1-based) occupying position p.
    """
    n = T['n']
    blocks = {}
    for i in range(1, n + 1):
        blocks.setdefault(col[i - 1], []).append(i)
    order = sorted(blocks, key=lambda c: (len(blocks[c]), c))
    out = [()]
    for c in order:
        nxt = []
        for pre in out:
            for tup in permutations(blocks[c]):
                nxt.append(pre + tup)
        out = nxt
    return out


def relabel_batch(T, S, cls, PL):
    """(P,M) relabelled sign bits.  PL[(p)] = placement, cls[p] = row of S."""
    r, M = T['r'], T['M']
    P = len(PL)
    idx = (T['BAS'].astype(np.int64) - 1).ravel()
    img = PL[:, idx].reshape(P, M, r)                  # original labels
    par = np.zeros((P, M), dtype=np.uint8)
    for a in range(r):
        for b in range(a + 1, r):
            par ^= (img[:, :, a] > img[:, :, b])
    srt = np.sort(img, axis=2)
    tgt = T['TAB'][tuple(srt[:, :, a] for a in range(r))]   # (P,M)
    return np.take_along_axis(S[cls], tgt.astype(np.intp), axis=1) ^ par


def sign_max(T, S):
    """In place: replace each row by the maximum of its sign-coset."""
    ECH, PIV = T['ECH'], T['PIV']
    for t in range(len(PIV)):
        m = S[:, PIV[t]] == 0
        if m.any():
            S[m] ^= ECH[t]
    return S


# ======================================================================
# the expensive checks (a),(b),(d) on one shard
# ======================================================================

_T = None


def _init(n, r):
    global _T
    _T = build_tables(n, r)


def check_shard(job):
    """job = (shard_id, rows, key_hi, key_lo, stab).  Returns a dict."""
    sid, rows, key_hi, key_lo, stab = job
    T = _T
    t0 = time.time()
    res = {'shard': sid, 'nrows': int(len(rows)),
           'bad_gp': [], 'bad_canon': [], 'bad_stab': [],
           'n_bad_gp': 0, 'n_bad_canon': 0, 'n_bad_stab': 0,
           'n_placements': 0}
    CH = 1024
    for a in range(0, len(rows), CH):
        b = min(a + CH, len(rows))
        kh = key_hi[a:b]
        kl = key_lo[a:b]
        st = stab[a:b]
        S = decode_keys(T, kh, kl)
        p1, p2, p3 = gp_parities(T, S)
        ok = gp_valid(p1, p2, p3)
        for i in np.flatnonzero(~ok).tolist():
            res['n_bad_gp'] += 1
            if len(res['bad_gp']) < 40:
                res['bad_gp'].append(int(rows[a + i]))
        mut = mutable_mask(T, p1, p2, p3)
        del p1, p2, p3
        cols = colours_batch(T, mut)
        del mut
        PLl = []
        clsl = []
        starts = np.empty(b - a, dtype=np.int64)
        pos = 0
        for i, col in enumerate(cols):
            pl = placements(T, col)
            starts[i] = pos
            pos += len(pl)
            PLl.extend(pl)
            clsl.extend([i] * len(pl))
        res['n_placements'] += pos
        PL = np.array(PLl, dtype=np.uint8)
        cls = np.array(clsl, dtype=np.intp)
        R = relabel_batch(T, S, cls, PL)
        sign_max(T, R)
        hi, lo = encode_keys(T, R)
        del R
        KH = kh[cls].astype(np.uint64)
        KL = kl[cls].astype(np.uint64)
        eq = (hi == KH) & (lo == KL)
        gt = (hi > KH) | ((hi == KH) & (lo > KL))
        neq = np.add.reduceat(eq.astype(np.int64), starts)
        ngt = np.add.reduceat(gt.astype(np.int64), starts)
        # (b): the stored key is attained and never beaten
        badc = (ngt > 0) | (neq == 0)
        for i in np.flatnonzero(badc).tolist():
            res['n_bad_canon'] += 1
            if len(res['bad_canon']) < 40:
                res['bad_canon'].append(
                    {'row': int(rows[a + i]), 'beaten': int(ngt[i]),
                     'attained': int(neq[i])})
        # (d): |Stab| = 2^kappa * #argmax
        got = (1 << T['kappa']) * neq
        bads = got != st.astype(np.int64)
        for i in np.flatnonzero(bads).tolist():
            res['n_bad_stab'] += 1
            if len(res['bad_stab']) < 40:
                res['bad_stab'].append(
                    {'row': int(rows[a + i]), 'recorded': int(st[i]),
                     'recomputed': int(got[i])})
    res['seconds'] = time.time() - t0
    return res


# ======================================================================
# (g),(h): the mutation spanning-tree (reachability) witness
# ======================================================================

WITNESS_ARRAYS = ('parent', 'flip', 'sigma', 'eps', 'gsgn', 'depth')


def apply_voltage(T, S, sigma, eps, gsgn):
    """(P,M) uint8: the image of each row of S under (sigma, eps, gsgn).

    The action is the one recorded in the manifest,
        ((sig,eps,s).chi)(y_1,..,y_r)
            = (-1)^s (-1)^{|eps cap {y_1..y_r}|}
              chi(sig^{-1}y_1, ..., sig^{-1}y_r),
    with sigma[i][x-1] = sig(x) and bit (x-1) of eps meaning "element x is
    reoriented".  Rebuilt here from that formula: gather the source basis
    sig^{-1}(B_j), pay the sorting sign, then the reorientation parity on
    the TARGET basis B_j, then the global sign.
    """
    n, r, M = T['n'], T['r'], T['M']
    P = len(S)
    inv = np.zeros((P, n), dtype=np.int64)          # inv[:,p-1] = sig^{-1}(p)
    np.put_along_axis(inv, sigma.astype(np.int64) - 1,
                      np.tile(np.arange(1, n + 1, dtype=np.int64), (P, 1)),
                      axis=1)
    idx = (T['BAS'].astype(np.int64) - 1).ravel()
    img = inv[:, idx].reshape(P, M, r)
    par = np.zeros((P, M), dtype=np.uint8)
    for a in range(r):
        for b in range(a + 1, r):
            par ^= (img[:, :, a] > img[:, :, b])
    srt = np.sort(img, axis=2)
    tgt = T['TAB'][tuple(srt[:, :, a] for a in range(r))]
    out = np.take_along_axis(S, tgt.astype(np.intp), axis=1) ^ par
    out ^= T['EPSTAB'][eps.astype(np.intp)]
    out ^= (gsgn.astype(np.uint8) & 1)[:, None]
    return out


def witness_shard(job):
    """job = (sid, rows, ckh, ckl, pkh, pkl, flip, sigma, eps, gsgn).

    Verifies, for each row i of the shard,
        (sigma,eps,gsgn) . chi_i == mu_{B_flip}(chi_parent)
    as 126-bit sign vectors, exactly.
    """
    sid, rows, ckh, ckl, pkh, pkl, flip, sigma, eps, gsgn = job
    T = _T
    t0 = time.time()
    res = {'shard': sid, 'nrows': int(len(rows)), 'n_bad_edge': 0,
           'bad_edge': []}
    CH = 8192
    for a in range(0, len(rows), CH):
        b = min(a + CH, len(rows))
        S = decode_keys(T, ckh[a:b], ckl[a:b])
        R = apply_voltage(T, S, sigma[a:b], eps[a:b], gsgn[a:b])
        del S
        P = decode_keys(T, pkh[a:b], pkl[a:b])
        P[np.arange(b - a), flip[a:b].astype(np.intp)] ^= 1
        bad = (R != P).any(axis=1)
        del R, P
        for i in np.flatnonzero(bad).tolist():
            res['n_bad_edge'] += 1
            if len(res['bad_edge']) < 40:
                res['bad_edge'].append(int(rows[a + i]))
    res['seconds'] = time.time() - t0
    return res


def tree_checks(T, N, W, rep, man=None):
    """(g): the witness is a spanning TREE on the N listed rows.

    Returns (runnable, root): `runnable` says whether check (h) can be
    attempted at all (shapes and parent range sane); `root` is the unique
    parentless row when there is exactly one.
    """
    n, M = T['n'], T['M']
    parent, flip = W['parent'], W['flip']
    sigma, eps, gsgn, depth = (W['sigma'], W['eps'], W['gsgn'], W['depth'])

    shapes = (len(parent) == N and len(flip) == N and len(eps) == N and
              len(gsgn) == N and len(depth) == N and
              tuple(sigma.shape) == (N, n))
    rep.check("(g) witness has exactly one row per listed class", shapes,
              "" if shapes else
              f"N={N}, parent={len(parent)}, sigma={tuple(sigma.shape)}")
    if not shapes:
        return False, None

    srt = np.sort(sigma.astype(np.int64), axis=1)
    perm_ok = bool((srt == np.arange(1, n + 1, dtype=np.int64)).all())
    del srt
    rep.check("(g) every recorded sigma is a permutation of 1..n", perm_ok)
    rep.check(f"(g) every recorded eps is a reorientation mask < 2^{n}",
              bool((eps.astype(np.int64) < (1 << n)).all()))
    rep.check("(g) every recorded global sign is 0 or 1",
              bool((gsgn.astype(np.int64) <= 1).all()))
    rep.check(f"(g) every recorded mutated basis index is < {M}",
              bool((flip.astype(np.int64) < M).all()))

    pr = parent.astype(np.int64)
    isroot = pr < 0
    nroots = int(isroot.sum())
    rep.check("(g) exactly one parentless row (a tree, not a forest)",
              nroots == 1, f"{nroots} parentless rows")
    range_ok = bool(((pr >= -1) & (pr < N)).all())
    rep.check("(g) every parent pointer lands inside the artifact",
              range_ok, "" if range_ok else
              f"min {int(pr.min())}, max {int(pr.max())}")
    if not range_ok:
        return False, None
    if nroots != 1:
        return True, None
    root = int(np.flatnonzero(isroot)[0])

    d = depth.astype(np.int64)
    rep.check("(g) the root has depth 0", int(d[root]) == 0,
              f"depth[root={root}] = {int(d[root])}")
    nz = ~isroot
    good = d[nz] == d[pr[nz]] + 1
    nbad = int((~good).sum())
    del good
    rep.check("(g) depth[i] = depth[parent[i]] + 1 for every non-root row "
              "(the parent map strictly decreases depth, hence is acyclic)",
              nbad == 0,
              f"{nbad} violations" if nbad else f"max depth {int(d.max())}")
    del d, nz

    # independent confirmation: iterate the parent map by doubling.  A cap
    # is mandatory -- a cycle converges to the cycle instead of diverging,
    # so an uncapped loop would hang and a lenient one would be a hole.
    anc = pr.copy()
    anc[root] = root
    cap = max(4, int(np.ceil(np.log2(max(N, 2)))) + 2)
    reached = False
    rounds = 0
    for rounds in range(1, cap + 1):
        if bool((anc == root).all()):
            reached = True
            break
        anc = anc[anc]
    del anc
    rep.check("(g) every row's ancestor chain terminates at that one root "
              "(pointer doubling)", reached,
              f"{rounds} rounds, cap {cap}" if reached else
              f"NOT reached within {cap} doublings (cycle or second root)")

    # the manifest asserts these two; recompute rather than believe them
    w = (man or {}).get('witness') or {}
    if 'root_row' in w:
        rep.check("(g) the manifest's root_row is the computed root",
                  int(w['root_row']) == root,
                  f"manifest {w['root_row']}, computed {root}")
    if 'max_depth' in w:
        md = int(W['depth'].max())
        rep.check("(g) the manifest's max_depth is the computed one",
                  int(w['max_depth']) == md,
                  f"manifest {w['max_depth']}, computed {md}")
    return True, root


def run_witness(T, man, key_hi, key_lo, W, rep, workers, statedir,
                shard_size, quiet=False):
    """(g) then (h) over every non-root row."""
    N = len(key_hi)
    if T['EPSTAB'] is None:
        rep.check("(g),(h) reachability witness", False,
                  f"n = {T['n']} is too large for the reorientation table "
                  "this checker builds; not attempted")
        return
    runnable, root = tree_checks(T, N, W, rep, man)
    if not runnable:
        rep.check("(h) tree mutation identity", False,
                  "not attempted: the witness failed its structural checks")
        return
    parent = W['parent'].astype(np.int64)
    rows = np.flatnonzero(parent >= 0).astype(np.int64)
    n, r = man['n'], man['r']
    nsh = max(1, (len(rows) + shard_size - 1) // shard_size)
    if statedir:
        os.makedirs(statedir, exist_ok=True)
    tag = hashlib.sha256(
        (json.dumps(man.get('witness_array_sha256', {}), sort_keys=True) +
         man['array_sha256']['key_hi'] + str(len(rows)) + str(shard_size)
         ).encode()).hexdigest()[:12]
    todo, done = [], []
    for s in range(nsh):
        sp = (os.path.join(statedir, f"wshard_{tag}_{s:05d}.json")
              if statedir else None)
        if sp and os.path.exists(sp):
            with open(sp) as f:
                done.append(json.load(f))
            continue
        todo.append(s)

    def make(s):
        """One payload at a time: the parent keys are gathered here, and
        materializing all shards up front would duplicate the key array."""
        a, b = s * shard_size, min((s + 1) * shard_size, len(rows))
        rr = rows[a:b]
        pp = parent[rr]
        return (s, rr, key_hi[rr], key_lo[rr], key_hi[pp], key_lo[pp],
                W['flip'][rr], W['sigma'][rr], W['eps'][rr], W['gsgn'][rr])

    if done:
        print(f"  resuming: {len(done)} witness shard(s) checkpointed")
    t0 = time.time()
    results = list(done)
    if todo:
        if workers <= 1:
            _init(n, r)
            for s in todo:
                res = witness_shard(make(s))
                _wsave(res, statedir, tag)
                results.append(res)
                if not quiet:
                    print(f"    wshard {res['shard']:5d}  {res['nrows']} "
                          f"rows  {res['seconds']:.0f}s | elapsed "
                          f"{time.time()-t0:.0f}s", flush=True)
        else:
            import multiprocessing as mp
            ctx = mp.get_context('spawn')
            with ctx.Pool(workers, initializer=_init,
                          initargs=(n, r)) as pool:
                k = 0
                for res in pool.imap_unordered(witness_shard,
                                               (make(s) for s in todo)):
                    k += 1
                    _wsave(res, statedir, tag)
                    results.append(res)
                    if not quiet:
                        print(f"    wshard {res['shard']:5d}  "
                              f"{res['nrows']} rows  {res['seconds']:.0f}s "
                              f"| {k}/{len(todo)}  elapsed "
                              f"{time.time()-t0:.0f}s", flush=True)
    tot = sum(x['nrows'] for x in results)
    be = sum(x['n_bad_edge'] for x in results)
    ex = []
    for x in results:
        ex += x['bad_edge'][:5]
    print(f"  {tot} tree edges checked in {time.time()-t0:.0f}s")
    rep.check(f"(h) all {tot} tree edges satisfy the mutation identity "
              "(sigma,eps,gsgn).chi_child = mu_flip(chi_parent)", be == 0,
              f"{be} broken, e.g. rows {ex[:5]}" if be else "")
    if be == 0 and root is not None and not rep.fail:
        print(f"  => all {tot + 1} listed classes are joined to row {root} "
              f"by paths of certified mutation edges: ONE component.")


def _wsave(res, statedir, tag):
    if statedir:
        with open(os.path.join(statedir,
                               f"wshard_{tag}_{res['shard']:05d}.json"),
                  "w") as f:
            json.dump(res, f)


# ======================================================================
# cheap checks and driver
# ======================================================================

def sha256_file(path, bufsize=1 << 20):
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        while True:
            c = f.read(bufsize)
            if not c:
                break
            h.update(c)
    return h.hexdigest()


def sha256_array(a):
    return hashlib.sha256(np.ascontiguousarray(a).tobytes()).hexdigest()


class Report:
    def __init__(self):
        self.fail = []
        self.ok = []

    def check(self, name, cond, detail=""):
        if cond:
            self.ok.append(name)
            print(f"  [ OK ] {name}" + (f"  {detail}" if detail else ""))
        else:
            self.fail.append(name)
            print(f"  [FAIL] {name}" + (f"  {detail}" if detail else ""))
        return cond


def load_artifact(adir, rep, verify_hashes=True):
    mpath = os.path.join(adir, "MANIFEST.json")
    with open(mpath) as f:
        man = json.load(f)
    n, r = man['n'], man['r']
    for fn, info in man['files'].items():
        p = os.path.join(adir, fn)
        if not os.path.exists(p):
            rep.check(f"(0) file {fn} present", False, "missing")
            continue
        got = sha256_file(p)
        rep.check(f"(0) SHA-256 of {fn}", got == info['sha256'],
                  "" if got == info['sha256'] else f"got {got[:16]}...")
        rep.check(f"(0) size of {fn}",
                  os.path.getsize(p) == info['bytes'])
    npz = os.path.join(adir, f"coverage_{r}_{n}.npz")
    z = np.load(npz)
    key_hi = z['key_hi']
    key_lo = z['key_lo']
    stab = z['stab']
    for nm, arr in (('key_hi', key_hi), ('key_lo', key_lo), ('stab', stab)):
        got = sha256_array(arr)
        rep.check(f"(0) raw SHA-256 of array {nm}",
                  got == man['array_sha256'][nm])
    return man, key_hi, key_lo, stab


def load_witness(adir, man, rep):
    """Load and hash-check the reachability witness, or return None."""
    w = man.get('witness')
    if not w:
        return None
    p = os.path.join(adir, w['file'])
    if not os.path.exists(p):
        rep.check(f"(0) witness file {w['file']} present", False, "missing")
        return None
    z = np.load(p)
    W = {}
    for k in WITNESS_ARRAYS:
        if k not in z.files:
            rep.check(f"(0) witness array {k} present", False, "missing")
            return None
        W[k] = z[k]
        got = sha256_array(W[k])
        rep.check(f"(0) raw SHA-256 of witness array {k}",
                  got == man.get('witness_array_sha256', {}).get(k))
    return W


def cheap_checks(man, key_hi, key_lo, stab, rep):
    n, r = man['n'], man['r']
    Gn = factorial(n) * (1 << (n + 1))
    N = len(key_hi)
    rep.check("(c) three arrays have equal length",
              len(key_lo) == N and len(stab) == N)
    inc = ((key_hi[1:] > key_hi[:-1]) |
           ((key_hi[1:] == key_hi[:-1]) & (key_lo[1:] > key_lo[:-1])))
    nbad = int((~inc).sum())
    rep.check("(c) keys strictly increasing (sorted AND pairwise distinct)",
              nbad == 0, f"{nbad} non-increasing steps" if nbad else
              f"{N} keys")
    del inc
    rep.check("(e) count matches manifest", N == man['count'],
              f"{N} vs {man['count']}")
    uniq, cnt = np.unique(stab, return_counts=True)
    mass = 0
    div_ok = True
    for u, c in zip(uniq.tolist(), cnt.tolist()):
        if u == 0 or Gn % u:
            div_ok = False
            continue
        mass += (Gn // int(u)) * int(c)
    rep.check("(e) every stabilizer order divides |G'|", div_ok,
              f"orders seen: {uniq.tolist()}")
    rep.check("(e) orbit masses sum to the manifest total",
              str(mass) == str(man['mass_total']),
              f"{mass} vs {man['mass_total']}")
    if man.get('complete') and (r, n) == (4, 9):
        rep.check("(e) mass equals the (4,9) target "
                  f"{TARGET_MASS_4_9}", mass == TARGET_MASS_4_9)
        rep.check(f"(e) count equals {TARGET_COUNT_4_9}",
                  N == TARGET_COUNT_4_9)
    hist = {str(int(u)): int(c) for u, c in zip(uniq.tolist(), cnt.tolist())}
    if 'stab_histogram' in man:
        rep.check("(e) stabilizer histogram matches manifest",
                  hist == man['stab_histogram'], str(hist))
    return mass


def extcount_check(path, n, r, rep):
    """(f) the tracked extension table sums to the target."""
    Gm = factorial(n - 1) * (1 << n)          # |G'_{n-1}|
    tot = 0
    rows = 0
    seen = set()
    with open(path) as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            d = json.loads(line)
            if d['i'] in seen:
                rep.check("(f) extension table has no duplicate parents",
                          False, f"parent {d['i']} twice")
                return
            seen.add(d['i'])
            if Gm % d['stab']:
                rep.check("(f) parent stabilizer divides |G'_{n-1}|", False)
                return
            tot += (Gm // int(d['stab'])) * int(d['E'])
            rows += 1
    rep.check(f"(f) extension table has contiguous parent ids 0..{rows-1}",
              seen == set(range(rows)), f"{rows} rows")
    rep.check("(f) extension table sums to the target mass",
              tot == TARGET_MASS_4_9, f"{tot} vs {TARGET_MASS_4_9}")


def run_expensive(man, key_hi, key_lo, stab, rows, rep, workers, statedir,
                  shard_size, quiet=False):
    n, r = man['n'], man['r']
    nsh = (len(rows) + shard_size - 1) // shard_size
    if statedir:
        os.makedirs(statedir, exist_ok=True)
    tag = hashlib.sha256(
        (man['array_sha256']['key_hi'] + str(len(rows)) +
         str(int(rows[0])) + str(int(rows[-1])) + str(shard_size)
         ).encode()).hexdigest()[:12]
    todo = []
    done = []
    for s in range(nsh):
        sp = (os.path.join(statedir, f"shard_{tag}_{s:05d}.json")
              if statedir else None)
        if sp and os.path.exists(sp):
            with open(sp) as f:
                done.append(json.load(f))
            continue
        todo.append(s)

    def make(s):
        """Built one at a time: materializing every shard payload up front
        would duplicate the whole key array in RAM."""
        a, b = s * shard_size, min((s + 1) * shard_size, len(rows))
        rr = rows[a:b]
        return (s, rr, key_hi[rr], key_lo[rr], stab[rr])

    if done:
        print(f"  resuming: {len(done)} shard(s) already checkpointed")
    t0 = time.time()
    results = list(done)
    if todo:
        if workers <= 1:
            _init(n, r)
            for s in todo:
                results.append(_one(make(s), statedir, tag, quiet, t0,
                                    len(todo), len(results) - len(done)))
        else:
            import multiprocessing as mp
            ctx = mp.get_context('spawn')
            with ctx.Pool(workers, initializer=_init,
                          initargs=(n, r)) as pool:
                k = 0
                for res in pool.imap_unordered(check_shard,
                                               (make(s) for s in todo)):
                    k += 1
                    _save(res, statedir, tag)
                    results.append(res)
                    if not quiet:
                        el = time.time() - t0
                        print(f"    shard {res['shard']:5d}  "
                              f"{res['nrows']} rows  {res['seconds']:.0f}s "
                              f"| {k}/{len(todo)}  elapsed {el:.0f}s",
                              flush=True)
    tot = sum(x['nrows'] for x in results)
    bg = sum(x['n_bad_gp'] for x in results)
    bc = sum(x['n_bad_canon'] for x in results)
    bs = sum(x['n_bad_stab'] for x in results)
    npl = sum(x['n_placements'] for x in results)
    print(f"  {tot} rows checked in {time.time()-t0:.0f}s "
          f"({npl} admissible relabellings enumerated, "
          f"{npl/max(tot,1):.3f} per class)")
    ex = []
    for x in results:
        ex += x['bad_gp'][:5]
    rep.check(f"(a) all {tot} keys are valid uniform chirotopes", bg == 0,
              f"{bg} invalid, e.g. rows {ex[:5]}" if bg else "")
    ex = []
    for x in results:
        ex += x['bad_canon'][:5]
    rep.check(f"(b) all {tot} keys extremal in their orbit "
              f"(manifest convention)", bc == 0,
              f"{bc} non-extremal, e.g. {ex[:3]}" if bc else "")
    ex = []
    for x in results:
        ex += x['bad_stab'][:5]
    rep.check(f"(d) all {tot} stabilizer orders exact", bs == 0,
              f"{bs} wrong, e.g. {ex[:3]}" if bs else "")
    return tot


def _save(res, statedir, tag):
    if statedir:
        with open(os.path.join(statedir,
                               f"shard_{tag}_{res['shard']:05d}.json"),
                  "w") as f:
            json.dump(res, f)


def _one(j, statedir, tag, quiet, t0, njobs, k):
    res = check_shard(j)
    _save(res, statedir, tag)
    if not quiet:
        print(f"    shard {res['shard']:5d}  {res['nrows']} rows  "
              f"{res['seconds']:.0f}s | elapsed {time.time()-t0:.0f}s",
              flush=True)
    return res


# ======================================================================
# canaries
# ======================================================================

def _write_artifact(path, man, key_hi, key_lo, stab, fix_totals, W=None):
    """Write a (possibly sabotaged) artifact with a SELF-CONSISTENT
    manifest: all SHA-256 values are recomputed -- for the witness arrays
    too -- so no canary is caught merely by a stale hash.  `fix_totals`
    also recomputes count/mass, which isolates the mathematical checks
    from check (e)."""
    os.makedirs(path, exist_ok=True)
    n, r = man['n'], man['r']
    npz = os.path.join(path, f"coverage_{r}_{n}.npz")
    np.savez_compressed(npz, key_hi=key_hi, key_lo=key_lo, stab=stab)
    m = json.loads(json.dumps(man))
    if fix_totals:
        Gn = factorial(n) * (1 << (n + 1))
        uniq, cnt = np.unique(stab, return_counts=True)
        mass = sum((Gn // int(u)) * int(c)
                   for u, c in zip(uniq.tolist(), cnt.tolist()))
        m['count'] = int(len(key_hi))
        m['mass_total'] = str(mass)
        m['stab_histogram'] = {str(int(u)): int(c)
                               for u, c in zip(uniq.tolist(), cnt.tolist())}
    m['array_sha256'] = {'key_hi': sha256_array(key_hi),
                         'key_lo': sha256_array(key_lo),
                         'stab': sha256_array(stab)}
    m['files'] = {os.path.basename(npz): {
        'sha256': sha256_file(npz), 'bytes': os.path.getsize(npz)}}
    if W is not None:
        wn = os.path.join(path, f"witness_{r}_{n}.npz")
        np.savez_compressed(wn, **{k: W[k] for k in WITNESS_ARRAYS})
        m.setdefault('witness', {})
        m['witness'] = json.loads(json.dumps(man.get('witness', {})))
        m['witness']['file'] = os.path.basename(wn)
        pr = W['parent'].astype(np.int64)
        rr = np.flatnonzero(pr < 0)
        m['witness']['root_row'] = int(rr[0]) if len(rr) else -1
        m['witness']['max_depth'] = int(W['depth'].max())
        m['witness_array_sha256'] = {k: sha256_array(W[k])
                                     for k in WITNESS_ARRAYS}
        m['files'][os.path.basename(wn)] = {
            'sha256': sha256_file(wn), 'bytes': os.path.getsize(wn)}
    else:
        m.pop('witness', None)
        m.pop('witness_array_sha256', None)
    with open(os.path.join(path, "MANIFEST.json"), "w") as f:
        json.dump(m, f, indent=1)
    return path


def _subtree_rows(W, K):
    """The K rows closest to the root, as a set closed under `parent`.

    Taking every row of depth < d plus some rows of depth d is closed
    under the parent map, since a parent has strictly smaller depth.
    """
    d = W['depth'].astype(np.int64)
    order = np.lexsort((np.arange(len(d)), d))
    return np.sort(order[:min(K, len(d))]).astype(np.int64)


def _restrict_witness(W, sel):
    """Restrict the witness to `sel` (sorted, parent-closed) and remap."""
    N = len(W['parent'])
    pos = np.full(N, -1, dtype=np.int64)
    pos[sel] = np.arange(len(sel), dtype=np.int64)
    pr = W['parent'].astype(np.int64)[sel]
    newpar = np.where(pr < 0, -1, pos[np.maximum(pr, 0)])
    if int((newpar < 0).sum()) != 1:
        raise RuntimeError("sub-artifact selection is not parent-closed")
    return {'parent': newpar.astype(np.int32),
            'flip': W['flip'][sel].copy(),
            'sigma': W['sigma'][sel].copy(),
            'eps': W['eps'][sel].copy(),
            'gsgn': W['gsgn'][sel].copy(),
            'depth': W['depth'][sel].copy()}


def _edge_holds(T, key_hi, key_lo, W, i):
    """True iff the recorded tree edge at row i satisfies the identity."""
    p = int(W['parent'][i])
    if p < 0:
        return True
    S = decode_keys(T, key_hi[i:i + 1], key_lo[i:i + 1])
    R = apply_voltage(T, S, W['sigma'][i:i + 1], W['eps'][i:i + 1],
                      W['gsgn'][i:i + 1])
    P = decode_keys(T, key_hi[p:p + 1], key_lo[p:p + 1])
    P[0, int(W['flip'][i])] ^= 1
    return bool((R == P).all())


def _resort(key_hi, key_lo, stab, W=None):
    o = np.lexsort((key_lo, key_hi))
    if W is None:
        return key_hi[o], key_lo[o], stab[o], None
    inv = np.empty(len(o), dtype=np.int64)
    inv[o] = np.arange(len(o), dtype=np.int64)
    pr = W['parent'].astype(np.int64)[o]
    NW = {k: W[k][o].copy() for k in WITNESS_ARRAYS}
    NW['parent'] = np.where(pr < 0, -1,
                            inv[np.maximum(pr, 0)]).astype(np.int32)
    return key_hi[o], key_lo[o], stab[o], NW


def _run_all(adir, workers, statedir, shard_size, extcount=None):
    rep = Report()
    man, kh, kl, st = load_artifact(adir, rep)
    W = load_witness(adir, man, rep)
    cheap_checks(man, kh, kl, st, rep)
    rows = np.arange(len(kh), dtype=np.int64)
    run_expensive(man, kh, kl, st, rows, rep, workers, statedir,
                  shard_size, quiet=True)
    if W is not None:
        T = build_tables(man['n'], man['r'])
        run_witness(T, man, kh, kl, W, rep, workers, statedir, shard_size,
                    quiet=True)
    if extcount:
        extcount_check(extcount, man['n'], man['r'], rep)
    return rep


def canaries(adir, work, nrows, workers):
    """Build sabotaged copies of a small sub-artifact and require rejection.

    The sub-artifact is the `nrows` rows nearest the root in the witness
    tree, so it is itself a complete artifact: a sorted key list AND a
    spanning tree on exactly those rows.

    Sabotages 1-4 and 7-11 are shipped with a REGENERATED, internally
    consistent manifest (fresh SHA-256s for the coverage arrays AND the
    witness arrays) and with count/mass repaired, i.e. we assume an
    adversary who can rewrite the manifest.  A checker that compared only
    hashes, or only totals, would pass every one of them; each has to be
    caught by a substantive mathematical check.  Two are deliberately
    different: 5 (truncation) leaves the totals unrepaired and is meant to
    be caught by the count/mass arithmetic of check (e), and 6 leaves a
    stale hash in place and is meant to be caught by the integrity path,
    check (0).
    """
    rep0 = Report()
    man, KH, KL, ST = load_artifact(adir, rep0)
    W0 = load_witness(adir, man, rep0)
    if rep0.fail:
        raise SystemExit("base artifact failed its own integrity check")
    T = build_tables(man['n'], man['r'])
    M = T['M']
    if W0 is None:
        print("  NOTE: this artifact carries no reachability witness; "
              "only canaries 1-6 will be built")
        sel = np.arange(min(nrows, len(KH)), dtype=np.int64)
        W = None
    else:
        sel = _subtree_rows(W0, nrows)
        W = _restrict_witness(W0, sel)
    kh, kl, st = KH[sel].copy(), KL[sel].copy(), ST[sel].copy()
    NS = len(kh)
    base = os.path.join(work, "control")
    sub = json.loads(json.dumps(man))
    sub['complete'] = False
    sub['provenance'] = {'note': f'canary sub-artifact: {NS} rows nearest '
                                 f'the root of the witness tree'}
    _write_artifact(base, sub, kh, kl, st, True, W)

    outcomes = []

    def trial(name, path, expect_checks):
        print(f"\n--- canary: {name}")
        rep = _run_all(path, 1, None, 100000)
        fired = [f for f in rep.fail]
        good = len(fired) > 0 and any(
            any(f.startswith(e) for f in fired) for e in expect_checks)
        print(f"  -> {'REJECTED' if fired else 'ACCEPTED'}; "
              f"checks that fired: {fired}")
        outcomes.append({'canary': name, 'rejected': bool(fired),
                         'fired': fired,
                         'expected_one_of': expect_checks,
                         'pass': bool(good)})
        return good

    def cw():
        return None if W is None else {k: W[k].copy()
                                       for k in WITNESS_ARRAYS}

    print("\n--- control: untampered sub-artifact (must PASS)")
    repc = _run_all(base, 1, None, 100000)
    outcomes.append({'canary': 'control (untampered)',
                     'rejected': bool(repc.fail), 'fired': repc.fail,
                     'expected_one_of': [], 'pass': not repc.fail})
    print(f"  -> {'ACCEPTED' if not repc.fail else 'REJECTED'}")

    # 1. duplicated key (kept sorted, totals repaired: only (c) can fire)
    a, b, c = kh.copy(), kl.copy(), st.copy()
    a[7] = a[6]
    b[7] = b[6]
    c[7] = c[6]
    p = _write_artifact(os.path.join(work, "dup_key"), sub, a, b, c, True,
                        cw())
    trial("duplicated key", p, ["(c)"])

    # 2. non-canonical key: replace one key by another member of its orbit
    a, b, c, w = kh.copy(), kl.copy(), st.copy(), cw()
    i, alt = None, None
    for cand in range(11, min(NS, 400)):        # a very symmetric class may
        S = decode_keys(T, a[cand:cand + 1], b[cand:cand + 1])
        for k, perm in enumerate(permutations(range(1, T['n'] + 1))):
            if k > 4000:                        # have few distinct images
                break
            PL = np.array([perm], dtype=np.uint8)
            R = sign_max(T, relabel_batch(T, S, np.array([0]), PL))
            h, l = encode_keys(T, R)
            if (h[0], l[0]) != (a[cand], b[cand]):
                i, alt = cand, (h[0], l[0])
                break
        if alt is not None:
            break
    assert alt is not None, "no non-canonical orbit member found"
    a[i], b[i] = alt
    a, b, c, w = _resort(a, b, c, w)
    p = _write_artifact(os.path.join(work, "noncanonical"), sub, a, b, c,
                        True, w)
    trial("non-canonical key (same orbit, different representative)", p,
          ["(b)"])

    # 3. corrupted stabilizer order, with the manifest mass repaired so
    #    that only the recomputation can catch it
    a, b, c = kh.copy(), kl.copy(), st.copy()
    j = int(np.flatnonzero(c == c.min())[0])
    c[j] = c[j] * 2
    p = _write_artifact(os.path.join(work, "bad_stab"), sub, a, b, c, True,
                        cw())
    trial("corrupted stabilizer order (mass repaired to match)", p, ["(d)"])

    # 4. GP-invalid key: flip a NON-mutable basis, so validity really breaks
    a, b, c, w = kh.copy(), kl.copy(), st.copy(), cw()
    i, jbad, S = None, None, None
    for cand in range(23, min(NS, 400)):     # a class could in principle
        S = decode_keys(T, a[cand:cand + 1], b[cand:cand + 1])
        p1, p2, p3 = gp_parities(T, S)       # have every basis mutable
        nm = np.flatnonzero(~mutable_mask(T, p1, p2, p3)[0])
        if len(nm):
            i, jbad = cand, int(nm[0])
            break
    assert jbad is not None, "no class with a non-mutable basis found"
    S[0, jbad] ^= 1
    h, l = encode_keys(T, S)
    a[i], b[i] = h[0], l[0]
    a, b, c, w = _resort(a, b, c, w)
    p = _write_artifact(os.path.join(work, "gp_invalid"), sub, a, b, c,
                        True, w)
    trial("GP-invalid key (flipped a non-mutable basis)", p, ["(a)"])

    # 5. truncated file: rows dropped, manifest totals NOT repaired.  The
    #    dropped rows are LEAVES of the witness tree, so what remains is
    #    still a valid spanning tree and only the arithmetic can fire.
    if W is None:
        a, b, c, w = kh[:-500].copy(), kl[:-500].copy(), st[:-500].copy(), \
            None
    else:
        pr = W['parent'].astype(np.int64)
        haschild = np.zeros(NS, dtype=bool)
        haschild[pr[pr >= 0]] = True
        leaves = np.flatnonzero(~haschild)
        keep = np.setdiff1d(np.arange(NS, dtype=np.int64), leaves[-500:])
        a, b, c = kh[keep].copy(), kl[keep].copy(), st[keep].copy()
        w = _restrict_witness(W, keep)
    p = _write_artifact(os.path.join(work, "truncated"), sub, a, b, c,
                        False, w)
    trial("truncated artifact (500 leaf rows dropped, mass short)", p,
          ["(e)"])

    # 6. stale hash: data changed, manifest hashes left alone
    src = os.path.join(work, "stale_hash")
    os.makedirs(src, exist_ok=True)
    a, b, c = kh.copy(), kl.copy(), st.copy()
    c[3] = 4 if c[3] != 4 else 6
    n, r = man['n'], man['r']
    np.savez_compressed(os.path.join(src, f"coverage_{r}_{n}.npz"),
                        key_hi=a, key_lo=b, stab=c)
    if W is not None:
        np.savez_compressed(os.path.join(src, f"witness_{r}_{n}.npz"),
                            **{k: W[k] for k in WITNESS_ARRAYS})
    with open(os.path.join(base, "MANIFEST.json")) as f:
        stale = json.load(f)         # the CONTROL's manifest, left untouched
    with open(os.path.join(src, "MANIFEST.json"), "w") as f:
        json.dump(stale, f, indent=1)
    trial("stale SHA-256 (integrity path)", src, ["(0)"])

    if W is not None:
        _witness_canaries(T, work, sub, kh, kl, st, W, M, trial)

    print("\n================ CANARY SUMMARY ================")
    allok = True
    for o in outcomes:
        allok &= o['pass']
        print(f"  {'PASS' if o['pass'] else 'FAIL'}  {o['canary']}: "
              f"{'rejected' if o['rejected'] else 'accepted'}"
              f"  {o['fired'] if o['fired'] else ''}")
    print("================================================")
    return allok, outcomes


def _witness_canaries(T, work, sub, kh, kl, st, W, M, trial):
    """Canaries 7-11: sabotage the reachability witness itself.

    Each sabotage is asserted to be SEMANTICALLY REAL at construction time
    -- for 8, 9 and 11 we recompute the mutation identity here and require
    that it now fails -- so that none of them is a no-op absorbed by a
    stabilizer or by the trivially-acting reorientation.
    """
    NS = len(kh)
    d = W['depth'].astype(np.int64)
    pr = W['parent'].astype(np.int64)
    root = int(np.flatnonzero(pr < 0)[0])

    def cw():
        return {k: W[k].copy() for k in WITNESS_ARRAYS}

    # 7. re-pointed parent creating a cycle
    w = cw()
    v = int(np.flatnonzero(d >= 2)[0])          # v's parent is not the root
    u = int(pr[v])
    w['parent'][u] = v
    assert int(w['parent'][v]) == u and u != root
    p = _write_artifact(os.path.join(work, "cycle"), sub, kh, kl, st, True,
                        w)
    trial(f"re-pointed parent creating a cycle ({u} <-> {v})", p, ["(g)"])

    # 8. corrupted voltage: a single reoriented element added or removed
    w = cw()
    i = int(np.flatnonzero(pr >= 0)[len(np.flatnonzero(pr >= 0)) // 2])
    hit = None
    for bit in range(T['n']):                   # eps ^ (all ones) is a NO-OP
        w['eps'][i] = W['eps'][i] ^ (1 << bit)  # when r is even: use 1 bit
        if not _edge_holds(T, kh, kl, w, i):
            hit = bit
            break
    assert hit is not None, "no single-bit eps change breaks the identity"
    p = _write_artifact(os.path.join(work, "bad_voltage"), sub, kh, kl, st,
                        True, w)
    trial(f"corrupted voltage (row {i}, eps bit {hit} flipped)", p, ["(h)"])

    # 9. wrong mutated-basis index
    w = cw()
    j = int(np.flatnonzero(pr >= 0)[3])
    hit = None
    for k in range(1, M):
        w['flip'][j] = (int(W['flip'][j]) + k) % M
        if not _edge_holds(T, kh, kl, w, j):
            hit = int(w['flip'][j])
            break
    assert hit is not None
    p = _write_artifact(os.path.join(work, "bad_flip"), sub, kh, kl, st,
                        True, w)
    trial(f"wrong mutated-basis index (row {j}: "
          f"{int(W['flip'][j])} -> {hit})", p, ["(h)"])

    # 10. a second parentless node: the forest is no longer a tree
    w = cw()
    haschild = np.zeros(NS, dtype=bool)
    haschild[pr[pr >= 0]] = True
    leaf = int(np.flatnonzero(~haschild & (pr >= 0))[0])
    w['parent'][leaf] = -1
    w['depth'][leaf] = 0
    p = _write_artifact(os.path.join(work, "two_roots"), sub, kh, kl, st,
                        True, w)
    trial(f"second parentless node (row {leaf}), depth repaired to match",
          p, ["(g)"])

    # 11. parent re-pointed to another node at the SAME depth: the tree
    #     structure and every depth relation still hold, so only the
    #     mutation identity can catch it
    w = cw()
    tgt = None
    for i in np.flatnonzero(d >= 1).tolist():
        cand = np.flatnonzero((d == d[i] - 1) &
                              (np.arange(NS) != pr[i]))
        for c2 in cand[:8].tolist():
            w['parent'][i] = c2
            if not _edge_holds(T, kh, kl, w, i):
                tgt = (i, int(pr[i]), c2)
                break
            w['parent'][i] = pr[i]
        if tgt:
            break
    assert tgt is not None
    p = _write_artifact(os.path.join(work, "wrong_parent"), sub, kh, kl,
                        st, True, w)
    trial(f"parent re-pointed to a same-depth node (row {tgt[0]}: "
          f"{tgt[1]} -> {tgt[2]}); tree intact, identity broken", p,
          ["(h)"])


# ======================================================================

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--artifact", required=True)
    ap.add_argument("--sample", type=int, default=0,
                    help="check (a),(b),(d) on N pseudorandom rows only")
    ap.add_argument("--seed", type=int, default=20260731)
    ap.add_argument("--cheap-only", action="store_true")
    ap.add_argument("--witness-only", action="store_true",
                    help="run only (0),(c),(e),(g),(h)")
    ap.add_argument("--no-witness", action="store_true")
    ap.add_argument("--workers", type=int, default=4)
    ap.add_argument("--shard-size", type=int, default=100000)
    ap.add_argument("--state", default="")
    ap.add_argument("--extcount", default="")
    ap.add_argument("--canary", action="store_true")
    ap.add_argument("--work", default="data/canary_coverage")
    ap.add_argument("--canary-rows", type=int, default=20000)
    ap.add_argument("--show", type=int, default=-1)
    a = ap.parse_args()
    a.workers = max(1, min(4, a.workers))

    if a.canary:
        ok, _ = canaries(a.artifact, a.work, a.canary_rows, a.workers)
        print("CANARY SUITE:", "PASS" if ok else "FAIL")
        sys.exit(0 if ok else 1)

    rep = Report()
    print(f"artifact: {a.artifact}")
    man, kh, kl, st = load_artifact(a.artifact, rep)
    W = None if a.no_witness else load_witness(a.artifact, man, rep)
    print(f"  (n,r) = ({man['n']},{man['r']}), {len(kh)} rows, "
          f"kappa = {build_tables(man['n'], man['r'])['kappa']}")
    if W is None and not a.no_witness:
        print("  NOTE: no reachability witness in this artifact -- "
              "checks (g),(h) NOT run, so nothing here certifies that the "
              "listed classes form ONE component of the mutation graph.")
    if a.show >= 0:
        T = build_tables(man['n'], man['r'])
        i = a.show
        key = (int(kh[i]) << 64) | int(kl[i])
        s = ''.join('+' if (key >> (T['M'] - 1 - j)) & 1 else '-'
                    for j in range(T['M']))
        print(f"  row {i}: stab={int(st[i])}\n  {s}")
        return
    cheap_checks(man, kh, kl, st, rep)
    if a.extcount:
        extcount_check(a.extcount, man['n'], man['r'], rep)
    if not a.cheap_only and not a.witness_only:
        N = len(kh)
        if a.sample and a.sample < N:
            rng = np.random.default_rng(a.seed)
            rows = np.sort(rng.choice(N, size=a.sample, replace=False))
            print(f"  SAMPLE mode: {a.sample} of {N} rows "
                  f"(seed {a.seed}) for checks (a),(b),(d)")
        else:
            rows = np.arange(N, dtype=np.int64)
            print(f"  FULL mode: all {N} rows for checks (a),(b),(d)")
        run_expensive(man, kh, kl, st, rows, rep, a.workers, a.state,
                      a.shard_size)
    else:
        print("  checks (a),(b),(d) NOT run "
              f"({'--cheap-only' if a.cheap_only else '--witness-only'})")

    if W is not None and not a.cheap_only:
        print(f"  witness: {len(W['parent'])} rows, "
              f"reachability checks (g),(h)")
        if a.witness_only or a.sample:
            print("  CAVEAT: (h) shows the parent's mutant is a "
                  "G'-translate of the child; that it is a VALID chirotope "
                  "-- hence a real mutation edge -- follows from check (a), "
                  "which this invocation did not run over every row.")
        run_witness(build_tables(man['n'], man['r']), man, kh, kl, W, rep,
                    a.workers, a.state, a.shard_size)
    elif W is not None:
        print("  --cheap-only: checks (g),(h) NOT run")

    print("\n================ RESULT ================")
    print(f"  {len(rep.ok)} checks passed, {len(rep.fail)} failed")
    for f in rep.fail:
        print(f"    FAILED: {f}")
    print("=======================================")
    sys.exit(1 if rep.fail else 0)


if __name__ == "__main__":
    main()
