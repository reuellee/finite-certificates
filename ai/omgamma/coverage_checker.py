"""STANDALONE checker for the omgamma (r,n) coverage certificate.

This file imports NOTHING from this project -- not core.py, canon.py,
flip.py, runbig.py, bigstate.py, ext_count.py, checker*.py.  Only numpy and
the standard library.  Every table it needs (colex basis order, the
three-term Grassmann-Pluecker conditions, the sign lattice, the group
action) is rebuilt here from the definitions restated below, so that a
defect shared with the search programs cannot hide.  The independence is
enforced at run time, not just asserted: `_assert_independent()` refuses to
run if any module loaded into the interpreter resolves to a .py file
sitting next to this one.

WHAT THE CERTIFICATE IS.  `tree_<r>_<n>.npz` -- about 10.4 MB, tracked in
git -- holds only

    the key of the root class, and per class the PARENT class and the
    MUTATED BASIS that reached it,

in the canonical tree order described in MANIFEST.json.  It does not hold
the class keys, the stabilizer orders, the depths or the edge voltages:
this checker DERIVES all of those.  From the parent's chirotope, flipping
the recorded basis gives a chirotope in the child's orbit, and the child's
key is the canonical representative of that orbit -- computed here by the
same exhaustive enumeration that used to be used to check a recorded key.
That is why the certificate fits in a repository while the arrays it
replaces (62 MB of keys and 83 MB of witness data) do not.

WHAT IT VERIFIES, in exact integer arithmetic:

  (0) every file listed in MANIFEST.json has the recorded SHA-256, and each
      array of the certificate has the recorded raw-buffer SHA-256;
  (a) every reconstructed chirotope is a VALID uniform chirotope -- all
      three-term Grassmann-Pluecker sign conditions hold.  For a non-root
      row this is applied to mu_{B_flip[i]}(chi_parent[i]) BEFORE
      canonicalization, so it is exactly the statement that flip[i] is a
      mutable basis of the parent, i.e. that the recorded edge is a real
      mutation edge;
  (b) the ROOT key is EXTREMAL in its own orbit under the convention
      recorded in the manifest (restated in `canonical_convention.__doc__`
      below).  Every other key is not checked for extremality but
      CONSTRUCTED as the extremal representative of its orbit, by
      enumerating every admissible relabelling and maximising over the sign
      lattice.  Either way the key is a well-defined function of the
      G'-orbit, which is what makes distinct keys certify distinct classes;
  (c) the reconstructed keys are pairwise DISTINCT (sorted, then checked
      strictly increasing).  This is what makes the list a list of distinct
      CLASSES rather than of chirotopes;
  (d) every stabilizer order is |Stab_{G'}(chi)| computed here by exhaustive
      enumeration of the admissible relabellings (orbit-stabilizer on the
      colour-restricted transversal: |Stab| = 2^kappa times the number of
      admissible relabellings attaining the maximum), every order divides
      |G'|, and the resulting histogram is the one the manifest declares;
  (e) the orbit masses sum to the manifest total, and -- when the manifest
      declares the artifact complete -- to 1,722,704,635,330,560 with a
      count of 9,276,595;
  (f) OPTIONAL (--extcount FILE): the tracked single-element extension
      table sums arithmetically to that same target;
  (g) the certificate decodes to a genuine spanning TREE: the packed
      streams are well formed (exact bit lengths, zero padding, one gap bit
      per row, every mutated-basis index < M), parent[i] < i for every row
      but the root -- so the parent map is acyclic and every row reaches
      row 0, the unique parentless row -- and the rows are in the canonical
      order, strictly increasing in (depth, parent, flip).  An independent
      pointer-doubling pass confirms that ancestor chains terminate at row
      0;
  (h) every reconstructed tree edge satisfies the MUTATION IDENTITY.  The
      canonicalization of row i produces a group element; this checker
      reads that element off as (sigma_i, eps_i, gsgn_i) and an INDEPENDENT
      implementation of the group action (`apply_voltage`, built from the
      formula in the manifest, using the inverse permutation and a
      reorientation-parity table rather than the placement machinery)
      confirms, exactly as 126-bit sign vectors,
          (sigma_i, eps_i, gsgn_i) . chi_i  ==  mu_{B_flip[i]}(chi_parent).

WHY (a)+(c)+(d)+(e)+(g)+(h) CERTIFY THAT THE QUOTIENT GRAPH IS CONNECTED
AND COMPLETE.  Vertices of the quotient graph are G'-orbits of uniform
chirotopes; two orbits are adjacent when some representative of one is a
single-basis sign flip of a representative of the other.

  * (a) makes each reconstructed edge real: mu_{B_flip[i]}(chi_parent) is a
    valid chirotope, so B_flip[i] really is a mutable basis of the parent,
    and chi_i -- being the canonical representative of that mutant's orbit
    -- really is an adjacent class.  (h) re-derives the group element
    relating them through a second implementation, so a defect in the
    canonicalization machinery cannot manufacture a false adjacency.
  * (g) makes the edge set a spanning tree on the listed rows.  parent[i]
    strictly precedes i, so the parent map cannot cycle and iterating it
    from any row reaches row 0.  Hence ALL listed rows lie in ONE connected
    component of the quotient graph.
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
catalog, by contrast, is certified outright by (a)+(g)+(h) and does not
depend on the target at all.  Check (b) is relative to the manifest's
convention: the unrestricted maximum over all of S_n is not computable at
this scale (~1.5 s/class, ~160 CPU-days), so the certified statement is
"extremal under the documented colour-restricted convention".  That
convention is a well-defined function of the G'-orbit -- see
canonical_convention() -- which is all the distinctness argument needs, but
the reader has to read those forty lines rather than take a one-word
"canonical" on trust.  Finally, the keys and stabilizer orders are now
DERIVED here rather than checked against independently recorded values:
that removes an adversary's freedom to misreport them, but it also removes
the old agreement between two implementations.  `--legacy-crosscheck DIR`
restores that agreement for anyone holding the (untracked) arrays the
search programs wrote.

USAGE
  python coverage_checker.py --artifact data/coverage_4_9              # full
  python coverage_checker.py --artifact data/coverage_4_9 --prefix 200000
  python coverage_checker.py --artifact data/coverage_4_9 --structure-only
  python coverage_checker.py --artifact data/coverage_4_9 \
        --extcount data/extcount_4_9.jsonl --workers 2 --state .covstate
  python coverage_checker.py --canary --artifact data/coverage_4_9 \
        --work data/canary_coverage        # sabotage suite; must REJECT
  python coverage_checker.py --artifact data/coverage_4_9 \
        --legacy-crosscheck data/coverage_4_9
  python coverage_checker.py --artifact data/coverage_4_9 --show-root

The reconstruction proceeds one depth level at a time -- every row of a
level has its parent in the level before, so the level can be done in
parallel -- is sharded, runs on at most --workers processes (default 2),
and is checkpointed: with --state, each finished shard drops a small JSON
and its keys into memory-mapped files, and a re-run skips it.  Checks (0)
and (g) are cheap and always run; (c),(d),(e) run over every reconstructed
row once the reconstruction is done.
"""
import argparse
import hashlib
import io
import json
import os
import sys
import time
import zipfile
from itertools import combinations, permutations
from math import comb, factorial

import numpy as np
from numpy.lib import format as npformat

TARGET_MASS_4_9 = 1722704635330560
TARGET_COUNT_4_9 = 9276595
TREE_FORMAT = "omgamma-tree-v1"
FIXED_ZIP_DATE = (1980, 1, 1, 0, 0, 0)

# names this checker must never end up sharing code with, whatever the
# files next to it happen to be called
FORBIDDEN_MODULES = ('core', 'canon', 'flip', 'runbig', 'bigstate',
                     'ext_count', 'checker', 'checker_fast', 'extend',
                     'certify', 'export_coverage', 'export_subcert')


def _assert_independent():
    """Refuse to run if any generator-side module has been loaded.

    Two tests, because either alone is evadable: no module may resolve to a
    .py file sitting next to this one (a renamed generator would still be
    caught), and no module may carry one of the known generator names (a
    generator imported from elsewhere on sys.path would still be caught).
    """
    mine = os.path.realpath(os.path.abspath(__file__))
    here = os.path.dirname(mine)
    try:
        siblings = {os.path.realpath(os.path.join(here, f))
                    for f in os.listdir(here) if f.endswith('.py')} - {mine}
    except OSError:
        siblings = set()
    bad = []
    for name, mod in list(sys.modules.items()):
        f = getattr(mod, '__file__', None)
        if f:
            try:
                rp = os.path.realpath(f)
            except OSError:
                continue
            if rp in siblings:
                bad.append(f"{name} ({rp})")
        if name.split('.')[0] in FORBIDDEN_MODULES and name != '__main__':
            bad.append(name)
    if bad:
        raise SystemExit(
            "INDEPENDENCE VIOLATION: this checker shares code with the "
            "project it is supposed to check: " + ", ".join(sorted(set(bad))))


_assert_independent()


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
    # span is reached greedily from the reduced echelon form.  Each
    # echelon row carries the combination of GENERATORS that produced it
    # -- bit (i-1) for "element i reoriented", bit n for the global sign
    # -- so that the group element applied by sign_max can be read off.
    cols = []
    for i in range(1, n + 1):
        v = np.zeros(M, dtype=np.uint8)
        for j, B in enumerate(bases):
            if i in B:
                v[j] = 1
        cols.append((v, 1 << (i - 1)))
    cols.append((np.ones(M, dtype=np.uint8), 1 << n))
    ech = []
    for v, c in cols:
        v = v.copy()
        for p, w, cw in ech:
            if v[p]:
                v ^= w
                c ^= cw
        nz = np.flatnonzero(v)
        if len(nz):
            ech.append((int(nz[0]), v, c))
    ech.sort(key=lambda t: t[0])
    for a in range(len(ech) - 1, -1, -1):
        pa, wa, ca = ech[a]
        for b in range(a):
            pb, wb, cb = ech[b]
            if wb[pa]:
                ech[b] = (pb, wb ^ wa, cb ^ ca)
    T['PIV'] = np.array([p for p, _, _ in ech], dtype=np.int64)
    T['ECH'] = (np.array([w for _, w, _ in ech], dtype=np.uint8)
                if ech else np.zeros((0, M), dtype=np.uint8))
    T['ECHC'] = np.array([c for _, _, c in ech], dtype=np.uint32)
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
    buf[:, :8] = np.asarray(key_hi).astype('>u8').view(np.uint8).reshape(B, 8)
    buf[:, 8:] = np.asarray(key_lo).astype('>u8').view(np.uint8).reshape(B, 8)
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
    """In place: replace each row by the maximum of its sign-coset.

    Returns, per row, the combination of sign generators applied: bit (i-1)
    for "element i reoriented", bit n for the global sign.  The element it
    names is not unique (2^kappa of them act trivially); any representative
    is a legitimate witness, and check (h) verifies the one returned.
    """
    ECH, PIV, ECHC = T['ECH'], T['PIV'], T['ECHC']
    C = np.zeros(len(S), dtype=np.uint32)
    for t in range(len(PIV)):
        m = S[:, PIV[t]] == 0
        if m.any():
            S[m] ^= ECH[t]
            C[m] ^= ECHC[t]
    return C


def apply_voltage(T, S, sigma, eps, gsgn):
    """(P,M) uint8: the image of each row of S under (sigma, eps, gsgn).

    The action is the one recorded in the manifest,
        ((sig,eps,s).chi)(y_1,..,y_r)
            = (-1)^s (-1)^{|eps cap {y_1..y_r}|}
              chi(sig^{-1}y_1, ..., sig^{-1}y_r),
    with sigma[i][x-1] = sig(x) and bit (x-1) of eps meaning "element x is
    reoriented".  Rebuilt here from that formula: gather the source basis
    sig^{-1}(B_j), pay the sorting sign, then the reorientation parity on
    the TARGET basis B_j, then the global sign.  Deliberately a DIFFERENT
    implementation from relabel_batch + sign_max: check (h) plays the two
    against each other.
    """
    n, r, M = T['n'], T['r'], T['M']
    P = len(S)
    inv = np.zeros((P, n), dtype=np.int64)          # inv[:,p-1] = sig^{-1}(p)
    np.put_along_axis(inv, np.asarray(sigma).astype(np.int64) - 1,
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
    out ^= T['EPSTAB'][np.asarray(eps).astype(np.intp)]
    out ^= (np.asarray(gsgn).astype(np.uint8) & 1)[:, None]
    return out


def voltage_of(T, PL, combo):
    """The group element applied by the canonicalization, and its inverse.

    `PL[b]` is the winning placement, PL[b][p-1] being the ground-set
    element that ends up at position p, and `combo[b]` the sign combination
    sign_max applied.  The canonicalization computed
        chi_child = g . psi,   g = (sigma, eps, s),
    with sigma the INVERSE of the placement (relabel_batch evaluates chi at
    the placement, and the action evaluates at sig^{-1}).  Returns
        (g_sigma, g_eps, g_sgn, v_sigma, v_eps, v_sgn)
    with v = g^{-1} = (sigma^{-1}, sigma^{-1}(eps), s), so that
        v . chi_child = psi = mu_{B_flip}(chi_parent),
    which is the identity as the manifest displays it.
    """
    n = T['n']
    P = len(PL)
    placed = np.asarray(PL).astype(np.int64)     # placed[:,p-1] = element at p
    g_sigma = np.zeros((P, n), dtype=np.int64)
    np.put_along_axis(g_sigma, placed - 1,
                      np.tile(np.arange(1, n + 1, dtype=np.int64), (P, 1)),
                      axis=1)
    cb = np.asarray(combo).astype(np.int64)
    g_eps = cb & ((1 << n) - 1)
    g_sgn = ((cb >> n) & 1).astype(np.uint8)
    # (sigma^{-1}(eps))_x = eps_{sigma(x)}
    bits = (g_eps[:, None] >> (g_sigma - 1)) & 1
    v_eps = (bits << np.arange(n, dtype=np.int64)).sum(axis=1)
    return g_sigma, g_eps, g_sgn, placed, v_eps, g_sgn


def selftest_action(T, rep):
    """Data-independent self-test of the conventions, before any artifact.

    The reconstruction rests on three separate pieces of code agreeing:
    relabel_batch is the action of the inverse of the placement, XOR by an
    echelon row is the action of the sign element its combination names,
    and apply_voltage implements the action from the formula.  This pins
    them against each other on pseudorandom sign vectors.  It uses no
    artifact, so it cannot be tuned to the data.
    """
    rng = np.random.default_rng(20260731)
    n, M = T['n'], T['M']
    B = 24
    S = rng.integers(0, 2, size=(B, M), dtype=np.uint8)
    PL = np.array([rng.permutation(np.arange(1, n + 1, dtype=np.uint8))
                   for _ in range(B)], dtype=np.uint8)
    cls = np.arange(B, dtype=np.intp)

    # 1. relabel_batch == the action of the inverse placement
    R0 = relabel_batch(T, S, cls, PL)
    sig = np.zeros((B, n), dtype=np.int64)
    np.put_along_axis(sig, PL.astype(np.int64) - 1,
                      np.tile(np.arange(1, n + 1, dtype=np.int64), (B, 1)),
                      axis=1)
    R1 = apply_voltage(T, S, sig, np.zeros(B, np.int64), np.zeros(B, np.uint8))
    rep.check("self-test: relabelling and the group action agree "
              "(two implementations)", bool((R0 == R1).all()))

    # 2. XOR by a sign-lattice element == the action it names
    R = R0.copy()
    combo = sign_max(T, R)
    g_sigma, g_eps, g_sgn, v_sigma, v_eps, v_sgn = voltage_of(T, PL, combo)
    R2 = apply_voltage(T, S, g_sigma, g_eps, g_sgn)
    rep.check("self-test: the recovered group element reproduces the "
              "canonicalisation", bool((R == R2).all()))

    # 3. the recovered inverse really inverts it
    R3 = apply_voltage(T, R, v_sigma, v_eps, v_sgn)
    rep.check("self-test: its recorded inverse maps the canonical form "
              "back (this is the form check (h) verifies)",
              bool((R3 == S).all()))

    # 4. a single reorientation is the corresponding column XOR
    x = 1 + int(rng.integers(0, n))
    col = (T['INB'][:, x - 1] > 0).astype(np.uint8)
    R4 = apply_voltage(T, S, np.tile(np.arange(1, n + 1), (B, 1)),
                       np.full(B, 1 << (x - 1), dtype=np.int64),
                       np.zeros(B, np.uint8))
    rep.check(f"self-test: reorienting element {x} flips exactly the bases "
              "containing it", bool((R4 == (S ^ col[None, :])).all()))

    # 5. the sign lattice really is spanned by those generators
    rep.check(f"self-test: sign lattice has rank {len(T['PIV'])} and "
              f"kappa = {T['kappa']}",
              len(T['PIV']) + T['kappa'] == T['n'] + 1)


# ======================================================================
# canonicalization of a batch: the heart of the reconstruction
# ======================================================================

PLACEMENT_CAP = 32768


def canon_batch(T, PSI, cap=PLACEMENT_CAP):
    """Canonical key, stabilizer count and witness for each row of PSI.

    Returns (hi, lo, nargmax, valid, nplacements, win_placement, win_combo).
    Placements are processed in blocks of at most `cap`, so a class as
    symmetric as the alternating matroid (362,880 admissible relabellings)
    costs bounded memory rather than a gigabyte.

    A row whose chirotope is INVALID is not canonicalized at all: it is
    given the identity placement and a stabilizer count of 1.  Its derived
    key is meaningless -- but so is the whole certificate, since check (a)
    has already failed on it, and the verdict is FAIL either way.  The
    reason to short-circuit is that an invalid chirotope has no mutable
    bases, hence one colour class and n! admissible relabellings, so a
    corrupt or hostile certificate would otherwise cost hours instead of
    failing promptly.
    """
    B = len(PSI)
    n = T['n']
    p1, p2, p3 = gp_parities(T, PSI)
    valid = gp_valid(p1, p2, p3)
    mut = mutable_mask(T, p1, p2, p3)
    del p1, p2, p3
    cols = colours_batch(T, mut)
    del mut
    ident = tuple(range(1, n + 1))
    PLl = []
    npl = np.empty(B, dtype=np.int64)
    for i, col in enumerate(cols):
        pl = placements(T, col) if valid[i] else [ident]
        npl[i] = len(pl)
        PLl.extend(pl)
    tot = int(npl.sum())
    PLa = np.array(PLl, dtype=np.uint8)
    del PLl
    cls = np.repeat(np.arange(B, dtype=np.intp), npl)

    best_hi = np.zeros(B, dtype=np.uint64)
    best_lo = np.zeros(B, dtype=np.uint64)
    cnt = np.zeros(B, dtype=np.int64)
    seen = np.zeros(B, dtype=bool)
    win_pl = np.zeros((B, n), dtype=np.uint8)
    win_combo = np.zeros(B, dtype=np.uint32)

    for a in range(0, tot, cap):
        b = min(a + cap, tot)
        cc = cls[a:b]
        R = relabel_batch(T, PSI, cc, PLa[a:b])
        combo = sign_max(T, R)
        hi, lo = encode_keys(T, R)
        del R
        urows, ustart = np.unique(cc, return_index=True)
        seglen = np.diff(np.append(ustart, b - a))
        assert (seglen > 0).all()
        mh = np.maximum.reduceat(hi, ustart)
        mhe = np.repeat(mh, seglen)
        ml = np.maximum.reduceat(np.where(hi == mhe, lo, np.uint64(0)), ustart)
        mle = np.repeat(ml, seglen)
        win = (hi == mhe) & (lo == mle)
        nwin = np.add.reduceat(win.astype(np.int64), ustart)
        widx = np.flatnonzero(win)
        first = widx[np.searchsorted(widx, ustart)]
        cur_hi, cur_lo, sn = best_hi[urows], best_lo[urows], seen[urows]
        better = (~sn) | (mh > cur_hi) | ((mh == cur_hi) & (ml > cur_lo))
        same = sn & (mh == cur_hi) & (ml == cur_lo)
        rb = urows[better]
        best_hi[rb] = mh[better]
        best_lo[rb] = ml[better]
        cnt[rb] = nwin[better]
        win_pl[rb] = PLa[a + first[better]]
        win_combo[rb] = combo[first[better]]
        seen[rb] = True
        rs = urows[same]
        cnt[rs] += nwin[same]
    return best_hi, best_lo, cnt, valid, tot, win_pl, win_combo


# ======================================================================
# the sharded reconstruction: checks (a),(b),(d),(h) on one shard
# ======================================================================

_T = None


def _init(n, r):
    global _T
    _assert_independent()
    _T = build_tables(n, r)


def recon_shard(job):
    """job = (shard_id, row0, parent_key_hi, parent_key_lo, flip).

    For each row: flip the recorded basis of the parent chirotope, check the
    result is a valid uniform chirotope (a), canonicalize it into the class
    key and stabilizer order (b),(d), and verify the group element the
    canonicalization used against an independent implementation of the
    action (h).
    """
    sid, row0, pkh, pkl, fl = job
    T = _T
    t0 = time.time()
    nr = len(fl)
    out_hi = np.empty(nr, dtype=np.uint64)
    out_lo = np.empty(nr, dtype=np.uint64)
    out_st = np.empty(nr, dtype=np.uint32)
    res = {'shard': int(sid), 'row0': int(row0), 'nrows': int(nr),
           'n_bad_gp': 0, 'bad_gp': [], 'n_bad_edge': 0, 'bad_edge': [],
           'n_placements': 0}
    CH = 1024
    for a in range(0, nr, CH):
        b = min(a + CH, nr)
        PSI = decode_keys(T, pkh[a:b], pkl[a:b])
        PSI[np.arange(b - a), fl[a:b].astype(np.intp)] ^= 1
        hi, lo, cnt, valid, tot, wpl, wcombo = canon_batch(T, PSI)
        res['n_placements'] += tot
        for i in np.flatnonzero(~valid).tolist():
            res['n_bad_gp'] += 1
            if len(res['bad_gp']) < 40:
                res['bad_gp'].append(int(row0 + a + i))
        out_hi[a:b] = hi
        out_lo[a:b] = lo
        st = (1 << T['kappa']) * cnt
        out_st[a:b] = np.minimum(st, np.iinfo(np.uint32).max)
        # (h): the identity, through the independent action implementation
        _, _, _, v_sigma, v_eps, v_sgn = voltage_of(T, wpl, wcombo)
        CHILD = decode_keys(T, hi, lo)
        BACK = apply_voltage(T, CHILD, v_sigma, v_eps, v_sgn)
        del CHILD
        bad = (BACK != PSI).any(axis=1)
        del BACK, PSI
        for i in np.flatnonzero(bad).tolist():
            res['n_bad_edge'] += 1
            if len(res['bad_edge']) < 40:
                res['bad_edge'].append(int(row0 + a + i))
    res['seconds'] = time.time() - t0
    return res, out_hi, out_lo, out_st


# ======================================================================
# reading the certificate
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
    def __init__(self, verbose=True):
        self.fail = []
        self.ok = []
        self.verbose = verbose

    def check(self, name, cond, detail=""):
        if cond:
            self.ok.append(name)
            if self.verbose:
                print(f"  [ OK ] {name}" + (f"  {detail}" if detail else ""))
        else:
            self.fail.append(name)
            print(f"  [FAIL] {name}" + (f"  {detail}" if detail else ""))
        return bool(cond)


TREE_ARRAYS = ('format', 'params', 'root_key', 'gap_nbits', 'gap_bits',
               'flip_bits')


def load_manifest(adir):
    with open(os.path.join(adir, "MANIFEST.json")) as f:
        return json.load(f)


def check_files(adir, man, rep):
    """(0) the tracked files, and any legacy array that happens to be here."""
    for fn, info in man.get('files', {}).items():
        p = os.path.join(adir, fn)
        if not os.path.exists(p):
            rep.check(f"(0) file {fn} present", False, "missing")
            continue
        got = sha256_file(p)
        rep.check(f"(0) SHA-256 of {fn}", got == info['sha256'],
                  "" if got == info['sha256'] else f"got {got[:16]}...")
        rep.check(f"(0) size of {fn}",
                  os.path.getsize(p) == info['bytes'])
    for fn, info in man.get('legacy_files', {}).items():
        p = os.path.join(adir, fn)
        if not os.path.exists(p):
            print(f"  [note] legacy array {fn} is not here; it is not "
                  f"needed and not tracked")
            continue
        got = sha256_file(p)
        rep.check(f"(0) SHA-256 of legacy file {fn}", got == info['sha256'])


def load_tree(adir, man, rep):
    """Decode the certificate.  Returns a dict or None if it is malformed.

    Every structural precondition is a check, not an assumption: a
    malformed stream must FAIL loudly rather than silently truncate.
    """
    tm = man.get('tree')
    if not tm:
        rep.check("(0) the manifest declares a tree certificate", False,
                  "no 'tree' section")
        return None
    p = os.path.join(adir, tm['file'])
    if not os.path.exists(p):
        rep.check(f"(0) certificate {tm['file']} present", False, "missing")
        return None
    z = np.load(p)
    for k in TREE_ARRAYS:
        if k not in z.files:
            rep.check(f"(0) certificate array {k} present", False, "missing")
            return None
        got = sha256_array(z[k])
        rep.check(f"(0) raw SHA-256 of certificate array {k}",
                  got == man.get('tree_array_sha256', {}).get(k))
    fmt = str(z['format'])
    if not rep.check("(g) certificate format tag", fmt == TREE_FORMAT,
                     f"{fmt!r}"):
        return None
    params = np.asarray(z['params']).astype(np.int64)
    if not rep.check("(g) certificate params are [n, r, count]",
                     params.shape == (3,) and params[0] > 0 and
                     params[1] > 0 and params[2] > 0, str(params.tolist())):
        return None
    n, r, N = int(params[0]), int(params[1]), int(params[2])
    ok = rep.check("(g) certificate (n,r,count) agree with the manifest",
                   n == man['n'] and r == man['r'] and
                   N == int(tm.get('count', N)),
                   f"({n},{r},{N})")
    if not ok:
        return None
    M = comb(n, r)
    rk = np.asarray(z['root_key']).astype(np.uint64)
    if not rep.check("(g) root key is a pair of uint64",
                     rk.shape == (2,)):
        return None

    # --- the parent gap stream ---------------------------------------
    nb = np.asarray(z['gap_nbits']).astype(np.int64)
    if not rep.check("(g) gap_nbits is a single integer", nb.shape == (1,)):
        return None
    nbits = int(nb[0])
    gb = np.asarray(z['gap_bits']).astype(np.uint8)
    if not rep.check("(g) gap stream length matches gap_nbits",
                     len(gb) == (nbits + 7) // 8,
                     f"{len(gb)} bytes for {nbits} bits"):
        return None
    bits = np.unpackbits(gb, bitorder='big')
    if not rep.check("(g) gap stream padding is zero",
                     not bool(bits[nbits:].any())):
        return None
    ones = np.flatnonzero(bits[:nbits])
    del bits
    if not rep.check("(g) gap stream carries exactly one bit per non-root "
                     "row", len(ones) == N - 1,
                     f"{len(ones)} vs {N-1}"):
        return None
    parent = (ones - np.arange(N - 1, dtype=np.int64))
    del ones

    # --- the mutated-basis indices ------------------------------------
    fbits = np.asarray(z['flip_bits']).astype(np.uint8)
    need = 7 * (N - 1)
    if not rep.check("(g) flip stream length is 7 bits per non-root row",
                     len(fbits) == (need + 7) // 8,
                     f"{len(fbits)} bytes for {need} bits"):
        return None
    fb = np.unpackbits(fbits, bitorder='big')
    if not rep.check("(g) flip stream padding is zero",
                     not bool(fb[need:].any())):
        return None
    v = fb[:need].reshape(N - 1, 7)
    del fb
    flip = np.zeros(N - 1, dtype=np.uint8)
    for k in range(7):
        flip = (flip << np.uint8(1)) | v[:, k]
    del v
    if not rep.check(f"(g) every mutated-basis index is < {M}",
                     bool((flip < M).all()),
                     f"max {int(flip.max()) if N > 1 else 0}"):
        return None
    return {'n': n, 'r': r, 'count': N, 'root_key': rk,
            'parent': parent, 'flip': flip}


def structure_checks(T, man, tree, rep):
    """(g): the certificate decodes to a spanning tree in canonical order.

    Returns the depth-block boundaries (which the reconstruction needs) or
    None.
    """
    N = tree['count']
    par = tree['parent']
    flip = tree['flip']
    if N == 1:
        rep.check("(g) a one-row certificate is the root alone", True)
        return [0, 1]
    rows = np.arange(1, N, dtype=np.int64)
    ok = rep.check("(g) every parent pointer strictly precedes its row "
                   "(so the parent map is acyclic and row 0 is the unique "
                   "parentless row)", bool((par < rows).all() and
                                           (par >= 0).all()),
                   "" if bool((par < rows).all() and (par >= 0).all()) else
                   f"{int(((par >= rows) | (par < 0)).sum())} violations")
    if not ok:
        return None
    if not rep.check("(g) the parent array is nondecreasing, as the "
                     "canonical order requires",
                     bool((np.diff(par) >= 0).all())):
        return None

    # depth blocks: the children of a contiguous block are contiguous
    bounds = [0, 1]
    while bounds[-1] < N:
        s, e = bounds[-2], bounds[-1]
        lo = int(np.searchsorted(par, s, 'left')) + 1
        hi = int(np.searchsorted(par, e, 'left')) + 1
        if lo != e:
            rep.check("(g) the rows of each depth follow those of the "
                      "previous depth", False,
                      f"depth block [{s},{e}) has children starting at {lo}")
            return None
        if hi <= e:
            rep.check("(g) no depth level is empty while rows remain",
                      False, f"block [{s},{e}) has no children but "
                             f"{N-e} rows remain")
            return None
        bounds.append(hi)
    depth = np.zeros(N, dtype=np.int64)
    for d in range(1, len(bounds) - 1):
        depth[bounds[d]:bounds[d + 1]] = d
    rep.check("(g) depth[i] = depth[parent[i]] + 1 for every non-root row",
              bool((depth[1:] == depth[par] + 1).all()),
              f"max depth {len(bounds)-2}")
    if man.get('tree', {}).get('max_depth') is not None:
        rep.check("(g) the manifest's max_depth is the computed one",
                  int(man['tree']['max_depth']) == len(bounds) - 2,
                  f"manifest {man['tree']['max_depth']}, "
                  f"computed {len(bounds)-2}")
    # canonical order: strictly increasing in (depth, parent, flip).
    # Compared field by field rather than packed into one integer: a
    # hostile certificate could have depths large enough to overflow the
    # packing, and this check has to hold on hostile input too.
    d0, d1 = depth[1:-1], depth[2:]
    p0, p1 = par[:-1], par[1:]
    f0 = flip[:-1].astype(np.int64)
    f1 = flip[1:].astype(np.int64)
    inc = ((d1 > d0) | ((d1 == d0) &
                        ((p1 > p0) | ((p1 == p0) & (f1 > f0)))))
    nbad = int((~inc).sum())
    del inc, d0, d1, p0, p1, f0, f1
    rep.check("(g) rows are in the canonical order, strictly increasing in "
              "(depth, parent, mutated basis) -- so no reordering or "
              "duplicated edge can pass unnoticed", nbad == 0,
              f"{nbad} rows out of order" if nbad else f"{N} rows")

    # independent confirmation: iterate the parent map by doubling.  A cap
    # is mandatory -- a cycle converges to the cycle instead of diverging,
    # so an uncapped loop would hang and a lenient one would be a hole.
    anc = np.concatenate(([np.int64(0)], par))
    cap = max(4, int(np.ceil(np.log2(max(N, 2)))) + 2)
    reached = False
    rounds = 0
    for rounds in range(1, cap + 1):
        if bool((anc == 0).all()):
            reached = True
            break
        anc = anc[anc]
    del anc
    rep.check("(g) every row's ancestor chain terminates at row 0 "
              "(pointer doubling)", reached,
              f"{rounds} rounds, cap {cap}" if reached else
              f"NOT reached within {cap} doublings")
    return bounds


# ======================================================================
# the reconstruction driver
# ======================================================================

def _state_paths(statedir):
    return (os.path.join(statedir, "recon_key_hi.bin"),
            os.path.join(statedir, "recon_key_lo.bin"),
            os.path.join(statedir, "recon_stab.bin"),
            os.path.join(statedir, "recon_tag.json"))


def reconstruct(T, man, tree, bounds, rep, workers, statedir, shard_size,
                nrows=0, quiet=False):
    """Rebuild every key and stabilizer order.  Returns (key_hi, key_lo, stab).

    Depth level by depth level: every row of a level has its parent in the
    level before it, so a level can be split over processes freely, and the
    barrier between levels is what the dependency requires.
    """
    N = tree['count'] if not nrows else min(nrows, tree['count'])
    parent, flip = tree['parent'], tree['flip']
    n, r = T['n'], T['r']
    tag = hashlib.sha256(
        (json.dumps(man.get('tree_array_sha256', {}), sort_keys=True) +
         str(N) + str(shard_size)).encode()).hexdigest()[:12]

    key_hi = key_lo = stab = None
    if statedir:
        os.makedirs(statedir, exist_ok=True)
        ph, pl, ps, pt = _state_paths(statedir)
        want = {'tag': tag, 'count': int(N)}
        have = None
        if os.path.exists(pt):
            try:
                with open(pt) as f:
                    have = json.load(f)
            except ValueError:
                have = None
        mode = 'r+' if (have == want and all(os.path.exists(x)
                                             for x in (ph, pl, ps))) else 'w+'
        key_hi = np.memmap(ph, dtype=np.uint64, mode=mode, shape=(N,))
        key_lo = np.memmap(pl, dtype=np.uint64, mode=mode, shape=(N,))
        stab = np.memmap(ps, dtype=np.uint32, mode=mode, shape=(N,))
        if mode == 'w+':
            with open(pt, "w") as f:
                json.dump(want, f)
    else:
        key_hi = np.zeros(N, dtype=np.uint64)
        key_lo = np.zeros(N, dtype=np.uint64)
        stab = np.zeros(N, dtype=np.uint32)

    # --- the root -----------------------------------------------------
    rk = tree['root_key']
    try:
        PSI0 = decode_keys(T, rk[0:1], rk[1:2])
    except ValueError as exc:
        rep.check("(a) the root key decodes to a sign vector on the bases",
                  False, str(exc))
        return None
    hi, lo, cnt, valid, tot, wpl, wcombo = canon_batch(T, PSI0)
    rep.check("(a) the root key is a valid uniform chirotope", bool(valid[0]))
    same = bool(hi[0] == rk[0] and lo[0] == rk[1])
    rep.check("(b) the root key is extremal in its own orbit (manifest "
              "convention); every other key is CONSTRUCTED as the extremal "
              "representative of its orbit", same,
              "" if same else f"canonical form is {int(hi[0])}*2^64+"
                              f"{int(lo[0])}, not the recorded root key")
    key_hi[0], key_lo[0] = rk[0], rk[1]
    stab[0] = (1 << T['kappa']) * int(cnt[0])
    del PSI0

    # --- shard list, deterministic so that resume is exact -------------
    shards = []
    for d in range(1, len(bounds) - 1):
        a0, b0 = bounds[d], min(bounds[d + 1], N)
        if a0 >= N:
            break
        for a in range(a0, b0, shard_size):
            shards.append((d, a, min(a + shard_size, b0)))
    todo, done = [], []
    for sid, (d, a, b) in enumerate(shards):
        sp = (os.path.join(statedir, f"rshard_{tag}_{sid:05d}.json")
              if statedir else None)
        if sp and os.path.exists(sp):
            try:
                with open(sp) as f:
                    done.append(json.load(f))
                continue
            except ValueError:
                pass
        todo.append(sid)
    if done:
        print(f"  resuming: {len(done)} of {len(shards)} shard(s) "
              f"checkpointed")
    results = list(done)
    todoset = set(todo)
    t0 = time.time()
    pool = None
    try:
        if workers > 1 and todo:
            import multiprocessing as mp
            ctx = mp.get_context('spawn')
            pool = ctx.Pool(workers, initializer=_init, initargs=(n, r))
        elif todo:
            _init(n, r)
        for d in range(1, len(bounds) - 1):
            ids = [sid for sid, (dd, a, b) in enumerate(shards)
                   if dd == d and sid in todoset]
            if not ids:
                continue
            jobs = []
            for sid in ids:
                _, a, b = shards[sid]
                pr = parent[a - 1:b - 1]
                jobs.append((sid, a, np.ascontiguousarray(key_hi[pr]),
                             np.ascontiguousarray(key_lo[pr]),
                             np.ascontiguousarray(flip[a - 1:b - 1])))
            it = (pool.imap_unordered(recon_shard, jobs) if pool
                  else (recon_shard(j) for j in jobs))
            for res, ohi, olo, ost in it:
                a = res['row0']
                b = a + res['nrows']
                key_hi[a:b] = ohi
                key_lo[a:b] = olo
                stab[a:b] = ost
                if statedir:
                    key_hi.flush()
                    key_lo.flush()
                    stab.flush()
                    with open(os.path.join(
                            statedir,
                            f"rshard_{tag}_{res['shard']:05d}.json"),
                            "w") as f:
                        json.dump(res, f)
                results.append(res)
                if not quiet:
                    print(f"    depth {d:2d} shard {res['shard']:5d}  "
                          f"rows {a}..{b}  {res['seconds']:.0f}s  | "
                          f"elapsed {time.time()-t0:.0f}s", flush=True)
    finally:
        if pool is not None:
            pool.close()
            pool.join()

    tot = sum(x['nrows'] for x in results)
    bg = sum(x['n_bad_gp'] for x in results)
    be = sum(x['n_bad_edge'] for x in results)
    npl = sum(x['n_placements'] for x in results)
    ex = []
    for x in results:
        ex += x['bad_gp'][:5]
    if not quiet:
        print(f"  {tot} classes reconstructed in {time.time()-t0:.0f}s "
              f"({npl} admissible relabellings enumerated, "
              f"{npl/max(tot,1):.3f} per class)")
    rep.check(f"(a) all {tot} reconstructed mutants "
              "mu_flip(chi_parent) are valid uniform chirotopes -- so every "
              "recorded flip really is a mutable basis of its parent",
              bg == 0, f"{bg} invalid, e.g. rows {ex[:5]}" if bg else "")
    ex = []
    for x in results:
        ex += x['bad_edge'][:5]
    rep.check(f"(h) all {tot} tree edges satisfy the mutation identity "
              "(sigma,eps,gsgn).chi_child = mu_flip(chi_parent), verified "
              "by an independent implementation of the action", be == 0,
              f"{be} broken, e.g. rows {ex[:5]}" if be else "")
    if bg == 0 and be == 0 and not rep.fail and not quiet:
        print(f"  => all {tot + 1} listed classes are joined to row 0 by "
              f"paths of certified mutation edges: ONE component.")
    return key_hi, key_lo, stab


# ======================================================================
# cheap checks over the reconstructed catalog
# ======================================================================

def catalog_checks(man, key_hi, key_lo, stab, rep, complete):
    n, r = man['n'], man['r']
    Gn = factorial(n) * (1 << (n + 1))
    N = len(key_hi)
    order = np.lexsort((key_lo, key_hi))
    sh = np.ascontiguousarray(key_hi)[order]
    sl = np.ascontiguousarray(key_lo)[order]
    del order
    inc = ((sh[1:] > sh[:-1]) | ((sh[1:] == sh[:-1]) & (sl[1:] > sl[:-1])))
    nbad = int((~inc).sum())
    del inc, sh, sl
    rep.check("(c) the reconstructed keys are pairwise DISTINCT (sorted, "
              "then strictly increasing)", nbad == 0,
              f"{nbad} repeats" if nbad else f"{N} keys")
    uniq, cnt = np.unique(np.ascontiguousarray(stab), return_counts=True)
    mass = 0
    div_ok = True
    for u, c in zip(uniq.tolist(), cnt.tolist()):
        if u == 0 or Gn % u:
            div_ok = False
            continue
        mass += (Gn // int(u)) * int(c)
    rep.check("(d) every stabilizer order recomputed here divides |G'|",
              div_ok, f"orders seen: {uniq.tolist()}")
    hist = {str(int(u)): int(c) for u, c in zip(uniq.tolist(), cnt.tolist())}
    if complete and 'stab_histogram' in man:
        rep.check("(d) the recomputed stabilizer histogram is the one the "
                  "manifest declares", hist == man['stab_histogram'],
                  str(hist))
    if complete:
        rep.check("(e) count matches manifest", N == man['count'],
                  f"{N} vs {man['count']}")
        rep.check("(e) orbit masses sum to the manifest total",
                  str(mass) == str(man['mass_total']),
                  f"{mass} vs {man['mass_total']}")
    else:
        print(f"  [note] partial artifact: {N} rows, mass {mass}, "
              f"stabilizers {hist}")
    if complete and man.get('complete') and (r, n) == (4, 9):
        rep.check("(e) mass equals the (4,9) target "
                  f"{TARGET_MASS_4_9}", mass == TARGET_MASS_4_9)
        rep.check(f"(e) count equals {TARGET_COUNT_4_9}",
                  N == TARGET_COUNT_4_9)
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


def legacy_crosscheck(ldir, man, key_hi, key_lo, stab, rep):
    """Compare the reconstruction with the arrays the search programs wrote.

    NOT part of the certificate chain: a reader who clones the repository
    does not have these arrays and does not need them.  What it adds is the
    agreement of two unrelated implementations -- canon.py's pruned search,
    which produced the recorded keys and stabilizer orders, and this
    checker's exhaustive enumeration, which now derives them.
    """
    r, n = man['r'], man['n']
    p = os.path.join(ldir, f"coverage_{r}_{n}.npz")
    if not os.path.exists(p):
        rep.check(f"(x) legacy array {p} present", False, "missing")
        return
    z = np.load(p)
    lh, ll, ls = z['key_hi'], z['key_lo'], z['stab']
    for nm, arr in (('key_hi', lh), ('key_lo', ll), ('stab', ls)):
        got = sha256_array(arr)
        rep.check(f"(x) raw SHA-256 of legacy array {nm}",
                  got == man.get('array_sha256', {}).get(nm))
    if len(lh) != len(key_hi):
        rep.check("(x) legacy array has the same number of rows", False,
                  f"{len(lh)} vs {len(key_hi)}")
        return
    o = np.lexsort((np.ascontiguousarray(key_lo),
                    np.ascontiguousarray(key_hi)))
    sh = np.ascontiguousarray(key_hi)[o]
    sl = np.ascontiguousarray(key_lo)[o]
    ss = np.ascontiguousarray(stab)[o]
    rep.check("(x) the reconstructed keys are exactly the recorded ones",
              bool((sh == lh).all() and (sl == ll).all()))
    rep.check("(x) the reconstructed stabilizer orders are exactly the "
              "recorded ones", bool((ss == ls.astype(np.uint32)).all()))


# ======================================================================
# canaries
# ======================================================================

def _pack_tree(root_key, parent, flip, n, r):
    """Encode a (possibly sabotaged) tree.  Mirrors export_coverage.py."""
    N = len(parent) + 1
    par = np.asarray(parent, dtype=np.int64)
    base = np.concatenate(([np.int64(0)], par))
    gaps = np.diff(base)
    if (gaps < 0).any():
        # a non-monotone parent array cannot be gap-coded; shift so that
        # the stream still decodes (to something wrong, which is the point)
        raise ValueError("parent array is not nondecreasing")
    nbits = int((N - 1) + int(par[-1]))
    bits = np.zeros(nbits, dtype=np.uint8)
    bits[np.cumsum(gaps + 1) - 1] = 1
    fb = np.zeros((N - 1, 7), dtype=np.uint8)
    f = np.asarray(flip, dtype=np.uint8)
    for k in range(7):
        fb[:, 6 - k] = (f >> k) & 1
    return {
        'format': np.array(TREE_FORMAT),
        'params': np.array([n, r, N], dtype=np.int64),
        'root_key': np.asarray(root_key, dtype=np.uint64),
        'gap_nbits': np.array([nbits], dtype=np.int64),
        'gap_bits': np.packbits(bits, bitorder='big'),
        'flip_bits': np.packbits(fb.ravel(), bitorder='big'),
    }


def _save_npz(path, arrays):
    with zipfile.ZipFile(path, 'w', compression=zipfile.ZIP_STORED) as zf:
        for name, arr in arrays.items():
            buf = io.BytesIO()
            npformat.write_array(buf, np.asanyarray(arr), allow_pickle=False)
            zi = zipfile.ZipInfo(name + '.npy', date_time=FIXED_ZIP_DATE)
            zi.compress_type = zipfile.ZIP_STORED
            zi.external_attr = 0o600 << 16
            zf.writestr(zi, buf.getvalue())


def _write_artifact(path, man, arrays, T, repair=True, stale_from=None):
    """Write a certificate directory with a SELF-CONSISTENT manifest.

    Every SHA-256 is recomputed, and with `repair` the count, mass and
    stabilizer histogram are recomputed too -- from a reconstruction of the
    sabotaged tree, i.e. we assume an adversary who can rewrite the whole
    manifest.  A checker that compared only hashes, or only totals, would
    pass; each canary has to be caught by a substantive check.
    """
    os.makedirs(path, exist_ok=True)
    n, r = man['n'], man['r']
    tn = os.path.join(path, f"tree_{r}_{n}.npz")
    _save_npz(tn, arrays)
    m = json.loads(json.dumps(man))
    m.pop('legacy_files', None)
    m.pop('array_sha256', None)
    m.pop('witness_array_sha256', None)
    m.pop('witness', None)
    m['tree'] = json.loads(json.dumps(man.get('tree', {})))
    m['tree']['file'] = os.path.basename(tn)
    m['tree']['count'] = int(arrays['params'][2])
    m['tree'].pop('max_depth', None)
    m['tree']['root_key_hi'] = int(arrays['root_key'][0])
    m['tree']['root_key_lo'] = int(arrays['root_key'][1])
    if repair:
        tot = _repair_totals(m, arrays, T)
        m['count'], m['mass_total'], m['stab_histogram'] = tot
    m['tree_array_sha256'] = {k: sha256_array(v) for k, v in arrays.items()}
    m['files'] = {os.path.basename(tn): {
        'sha256': sha256_file(tn), 'bytes': os.path.getsize(tn)}}
    if stale_from is not None:
        with open(os.path.join(stale_from, "MANIFEST.json")) as f:
            m = json.load(f)                 # deliberately NOT refreshed
    with open(os.path.join(path, "MANIFEST.json"), "w") as f:
        json.dump(m, f, indent=1)
    return path


def _repair_totals(man, arrays, T):
    """Reconstruct a sabotaged tree far enough to state its own totals.

    If the sabotaged tree cannot be decoded or reconstructed at all, this
    falls back to the PARENT manifest's totals, which will not match the
    sabotaged data.  That is the conservative direction -- the canary is
    then caught by (e) rather than by the check it was aimed at -- but it
    means a canary built through this path passes for the wrong reason.
    None of the twelve currently reaches it (each is either repaired or
    explicitly built with repair=False); a new one that does should be
    rewritten rather than left to fall through here.
    """
    rep = Report(verbose=False)
    tree = {'n': man['n'], 'r': man['r'],
            'count': int(arrays['params'][2]),
            'root_key': np.asarray(arrays['root_key'], dtype=np.uint64),
            'parent': None, 'flip': None}
    bits = np.unpackbits(arrays['gap_bits'], bitorder='big')
    nbits = int(arrays['gap_nbits'][0])
    ones = np.flatnonzero(bits[:nbits])
    tree['parent'] = ones - np.arange(len(ones), dtype=np.int64)
    v = np.unpackbits(arrays['flip_bits'], bitorder='big')
    v = v[:7 * (tree['count'] - 1)].reshape(-1, 7)
    fl = np.zeros(tree['count'] - 1, dtype=np.uint8)
    for k in range(7):
        fl = (fl << np.uint8(1)) | v[:, k]
    tree['flip'] = fl
    bounds = structure_checks(T, man, tree, rep)
    if bounds is None:
        return int(tree['count']), man['mass_total'], man['stab_histogram']
    out = reconstruct(T, man, tree, bounds, rep, 1, "", 1 << 30, quiet=True)
    if out is None:
        return int(tree['count']), man['mass_total'], man['stab_histogram']
    _, _, stab = out
    Gn = factorial(man['n']) * (1 << (man['n'] + 1))
    uniq, cnt = np.unique(stab, return_counts=True)
    mass = 0
    for u, c in zip(uniq.tolist(), cnt.tolist()):
        if u and Gn % u == 0:
            mass += (Gn // int(u)) * int(c)
    return (int(tree['count']), str(mass),
            {str(int(u)): int(c) for u, c in zip(uniq.tolist(), cnt.tolist())})


def _run_all(adir, workers=1, extcount=None):
    rep = Report(verbose=False)
    man = load_manifest(adir)
    check_files(adir, man, rep)
    tree = load_tree(adir, man, rep)
    if tree is None:
        return rep
    T = build_tables(tree['n'], tree['r'])
    bounds = structure_checks(T, man, tree, rep)
    if bounds is None:
        return rep
    out = reconstruct(T, man, tree, bounds, rep, workers, "", 1 << 30,
                      quiet=True)
    if out is None:
        return rep
    key_hi, key_lo, stab = out
    catalog_checks(man, key_hi, key_lo, stab, rep, True)
    if extcount:
        extcount_check(extcount, man['n'], man['r'], rep)
    return rep


def _decode(arrays):
    """(root_key, parent, flip) from a packed dict, for tampering."""
    N = int(arrays['params'][2])
    bits = np.unpackbits(arrays['gap_bits'], bitorder='big')
    ones = np.flatnonzero(bits[:int(arrays['gap_nbits'][0])])
    parent = ones - np.arange(len(ones), dtype=np.int64)
    v = np.unpackbits(arrays['flip_bits'],
                      bitorder='big')[:7 * (N - 1)].reshape(-1, 7)
    flip = np.zeros(N - 1, dtype=np.uint8)
    for k in range(7):
        flip = (flip << np.uint8(1)) | v[:, k]
    return np.asarray(arrays['root_key']).copy(), parent, flip


def canaries(adir, work, nrows, workers):
    """Sabotage a small sub-certificate and require rejection.

    The sub-certificate is the first `nrows` rows of the canonical order.
    Because parent[i] < i, a prefix is closed under `parent`, so it is a
    complete certificate in its own right: a root, a spanning tree, and
    (after reconstruction) a catalog of distinct classes.

    Three of the eleven sabotages the previous, 145 MB format admitted have
    no analogue here, and the reason is the point of the new format: a
    corrupted stabilizer order, a corrupted edge voltage and a second
    parentless row are not expressible, because the certificate does not
    carry stabilizer orders or voltages and its root is structurally
    unique.  Their nearest analogues (a corrupted manifest histogram, a
    corrupted mutated-basis index, a parent that does not precede its row)
    are included instead.
    """
    rep0 = Report(verbose=False)
    man = load_manifest(adir)
    check_files(adir, man, rep0)
    tree = load_tree(adir, man, rep0)
    if tree is None or rep0.fail:
        raise SystemExit("base certificate failed its own integrity check: "
                         + str(rep0.fail))
    n, r = tree['n'], tree['r']
    T = build_tables(n, r)
    M = T['M']
    NS = min(nrows, tree['count'])
    root_key = tree['root_key'].copy()
    parent = tree['parent'][:NS - 1].copy()
    flip = tree['flip'][:NS - 1].copy()
    sub = json.loads(json.dumps(man))
    sub['complete'] = False
    sub['provenance'] = {'note': f'canary sub-certificate: the first {NS} '
                                 f'rows of the canonical tree order'}
    base = _write_artifact(os.path.join(work, "control"), sub,
                           _pack_tree(root_key, parent, flip, n, r), T)

    # the reconstructed sub-catalog, used to design semantically real
    # sabotages (and to assert at construction time that they bite)
    reptmp = Report(verbose=False)
    tsub = {'n': n, 'r': r, 'count': NS, 'root_key': root_key,
            'parent': parent, 'flip': flip}
    bounds = structure_checks(T, man, tsub, reptmp)
    khi, klo, kst = reconstruct(T, man, tsub, bounds, reptmp, 1, "", 1 << 30,
                                quiet=True)
    khi = np.array(khi)
    klo = np.array(klo)
    present = {(int(a), int(b)) for a, b in zip(khi, klo)}

    outcomes = []

    def trial(name, path, expect):
        print(f"\n--- canary: {name}")
        rep = _run_all(path)
        fired = list(rep.fail)
        good = bool(fired) and any(any(f.startswith(e) for f in fired)
                                   for e in expect)
        print(f"  -> {'REJECTED' if fired else 'ACCEPTED'}; "
              f"checks that fired: {fired}")
        outcomes.append({'canary': name, 'rejected': bool(fired),
                         'fired': fired, 'expected_one_of': expect,
                         'pass': good})
        return good

    print("\n--- control: untampered sub-certificate (must PASS)")
    repc = _run_all(base)
    outcomes.append({'canary': 'control (untampered)',
                     'rejected': bool(repc.fail), 'fired': repc.fail,
                     'expected_one_of': [], 'pass': not repc.fail})
    print(f"  -> {'ACCEPTED' if not repc.fail else 'REJECTED'}"
          f"{'' if not repc.fail else '  ' + str(repc.fail)}")

    def mutable_of(row):
        S = decode_keys(T, khi[row:row + 1], klo[row:row + 1])
        p1, p2, p3 = gp_parities(T, S)
        return S, mutable_mask(T, p1, p2, p3)[0]

    def class_of(row, j):
        """The key that mutating basis j of row `row` leads to."""
        S, _ = mutable_of(row)
        S[0, j] ^= 1
        hi, lo, cnt, valid, _, _, _ = canon_batch(T, S)
        return (int(hi[0]), int(lo[0])), bool(valid[0])

    # 1. a duplicated class: re-point a leaf edge at a class already listed
    #    (the analogue of the old "duplicated key")
    f2 = flip.copy()
    hit = None
    for i in range(NS - 2, max(NS - 4000, 0), -1):
        row, par = i + 1, int(parent[i])
        S, mut = mutable_of(par)
        for j in np.flatnonzero(mut).tolist():
            if j == int(flip[i]):
                continue
            k, ok = class_of(par, j)
            if ok and k in present:
                f2[i] = j
                hit = (row, int(flip[i]), j)
                break
        if hit:
            break
    assert hit, "no re-pointable edge onto an already-listed class"
    p = _write_artifact(os.path.join(work, "dup_class"), sub,
                        _pack_tree(root_key, parent, f2, n, r), T)
    trial(f"duplicated class (row {hit[0]}: mutate {hit[1]} -> {hit[2]}, "
          f"landing on a class already listed)", p, ["(c)"])

    # 2. corrupted root key: another representative of the SAME orbit, so
    #    only the extremality check can see it
    alt = None
    S0 = decode_keys(T, root_key[0:1], root_key[1:2])
    for k, perm in enumerate(permutations(range(1, n + 1))):
        PL = np.array([perm], dtype=np.uint8)
        R = relabel_batch(T, S0, np.array([0]), PL)
        sign_max(T, R)
        h, l = encode_keys(T, R)
        if (h[0], l[0]) != (root_key[0], root_key[1]):
            alt = (h[0], l[0])
            break
        if k > 5000:
            break
    if alt is None:                    # the root may be a fixed point of
        for j in range(M):             # every relabelling: use a sign coset
            R = S0.copy()
            R[0, j] ^= 1
            h, l = encode_keys(T, R)
            if (h[0], l[0]) != (root_key[0], root_key[1]):
                alt = (h[0], l[0])
                break
    assert alt is not None
    p = _write_artifact(os.path.join(work, "bad_root"), sub,
                        _pack_tree(np.array(alt, dtype=np.uint64), parent,
                                   flip, n, r), T)
    trial("corrupted root key (a different representative of its orbit)",
          p, ["(b)"])

    # 3. corrupted stabilizer histogram in the manifest.  The old format
    #    stored stabilizer orders and one could be corrupted; here they are
    #    derived, so the only thing left to corrupt is the manifest's claim.
    pth = os.path.join(work, "bad_stabhist")
    _write_artifact(pth, sub, _pack_tree(root_key, parent, flip, n, r), T)
    with open(os.path.join(pth, "MANIFEST.json")) as f:
        mm = json.load(f)
    h = dict(mm['stab_histogram'])
    kk = sorted(h, key=lambda s: int(s))[0]
    h[kk] = h[kk] - 1
    h['24'] = h.get('24', 0) + 1
    mm['stab_histogram'] = h
    with open(os.path.join(pth, "MANIFEST.json"), "w") as f:
        json.dump(mm, f, indent=1)
    trial("corrupted stabilizer histogram in the manifest", pth, ["(d)"])

    # 4. GP-invalid mutant: point an edge at a NON-mutable basis, so the
    #    reconstructed chirotope really is invalid.  Sabotage a row of the
    #    deepest level, which has no descendants inside the prefix, so that
    #    exactly one row is affected and the canary is sharp.
    f3 = flip.copy()
    hit = None
    for i in range(NS - 2, max(NS - 4000, -1), -1):
        par = int(parent[i])
        S, mut = mutable_of(par)
        nm = np.flatnonzero(~mut)
        if len(nm):
            f3[i] = int(nm[0])
            hit = (i + 1, par, int(nm[0]))
            break
    assert hit, "no class with a non-mutable basis in the prefix"
    p = _write_artifact(os.path.join(work, "gp_invalid"), sub,
                        _pack_tree(root_key, parent, f3, n, r), T)
    trial(f"Grassmann-Pluecker-invalid mutant (row {hit[0]}: basis "
          f"{hit[2]} of class {hit[1]} is not mutable)", p, ["(a)"])

    # 5. truncated certificate: trailing rows dropped, totals NOT repaired.
    #    A prefix is parent-closed, so the tree still checks out and only
    #    the arithmetic can fire.
    K = max(2, NS - 500)
    pth = os.path.join(work, "truncated")
    arr = _pack_tree(root_key, parent[:K - 1], flip[:K - 1], n, r)
    _write_artifact(pth, sub, arr, T, repair=False)
    with open(os.path.join(pth, "MANIFEST.json")) as f:
        mm = json.load(f)
    mm['count'] = NS               # the manifest still claims the full size
    mm['complete'] = True
    mm['mass_total'] = str(sum(
        (factorial(n) * (1 << (n + 1))) // int(u) * int(c)
        for u, c in zip(*np.unique(np.array(kst), return_counts=True))))
    mm['stab_histogram'] = {
        str(int(u)): int(c)
        for u, c in zip(*np.unique(np.array(kst), return_counts=True))}
    with open(os.path.join(pth, "MANIFEST.json"), "w") as f:
        json.dump(mm, f, indent=1)
    trial(f"truncated certificate ({NS-K} rows dropped, totals not "
          f"repaired)", pth, ["(g)", "(e)"])

    # 6. stale SHA-256: data changed, manifest hashes left alone
    src = os.path.join(work, "stale_hash")
    f4 = flip.copy()
    f4[NS - 2] = (int(f4[NS - 2]) + 1) % M
    _write_artifact(src, sub, _pack_tree(root_key, parent, f4, n, r), T,
                    stale_from=base)
    trial("stale SHA-256 (integrity path)", src, ["(0)"])

    # 7. a parent pointer that does not precede its row: in this format
    #    that is the ONLY way to attempt a cycle, and the only way to
    #    attempt a second root
    p2 = parent.copy()
    p2[NS - 2] = NS - 1                 # the last row pointing at itself
    p = _write_artifact(os.path.join(work, "self_parent"), sub,
                        _pack_tree(root_key, p2, flip, n, r), T,
                        repair=False)
    trial(f"parent that does not precede its row (row {NS-1} -> {NS-1}); "
          f"neither a cycle nor a second root is otherwise expressible",
          p, ["(g)"])

    # 8. a permutation of the parent array that preserves its MULTISET,
    #    with the rows re-sorted into canonical order afterwards so that
    #    the structural checks cannot see it.  Both rows are taken from
    #    the deepest level, so nothing below them changes and the sabotage
    #    is exactly two edges; it is asserted here to be semantically real
    #    -- one of the two new edges must be invalid or must land on a
    #    class already listed -- so that it cannot be a vacuous no-op.
    dep = np.zeros(NS, dtype=np.int64)
    for d in range(1, len(bounds) - 1):
        dep[bounds[d]:min(bounds[d + 1], NS)] = d
    last = int(dep[NS - 1])
    alo = max(int(bounds[last]) - 1, 0)   # first parent-index of that level
    edges = {(int(parent[i]), int(flip[i])) for i in range(NS - 1)}
    p3, f5 = parent.copy(), flip.copy()
    found = None
    for a in range(NS - 2, alo - 1, -1):
        for b in range(a - 1, alo - 1, -1):
            if p3[a] == p3[b]:
                continue
            if ((int(p3[b]), int(f5[a])) in edges or
                    (int(p3[a]), int(f5[b])) in edges):
                continue                  # would be caught by (g) instead
            k1, ok1 = class_of(int(p3[b]), int(f5[a]))
            k2, ok2 = class_of(int(p3[a]), int(f5[b]))
            why = []
            if not ok1 or not ok2:
                why.append("invalid")
            if (ok1 and k1 in present) or (ok2 and k2 in present):
                why.append("duplicate")
            if why:
                found = (a, b, "/".join(why))
                break
        if found:
            break
    assert found, "no semantically real parent swap found"
    a, b = found[0], found[1]
    p3[a], p3[b] = p3[b], p3[a]
    o = np.lexsort((f5.astype(np.int64), p3))
    p = _write_artifact(os.path.join(work, "parent_perm"), sub,
                        _pack_tree(root_key, p3[o], f5[o], n, r), T)
    trial(f"parent multiset preserved but the tree changed (rows {a+1} and "
          f"{b+1} swap parents -> {found[2]}, then re-sorted into canonical "
          f"order)", p, ["(c)", "(a)", "(e)"])

    # 9. a re-pointed parent at the SAME depth: the tree shape, every depth
    #    and the canonical order all survive, so only the mathematics can
    #    catch it
    p4, f6 = parent.copy(), flip.copy()
    found = None
    cands = np.unique(p4[alo:]).tolist()
    for a in range(NS - 2, alo - 1, -1):
        fallback = None
        for q in cands:
            if q == int(p4[a]) or (int(q), int(f6[a])) in edges:
                continue
            k, ok = class_of(int(q), int(f6[a]))
            if ok and k in present:      # prefer a duplicate: it exercises
                found = (a, int(p4[a]), q, "duplicate")   # (c), where the
                break                                     # swap above
            if not ok and fallback is None:               # exercises (a)
                fallback = (a, int(p4[a]), q, "invalid")
        if found is None:
            found = fallback
        if found:
            break
    assert found, "no semantically real re-pointing found"
    p4[found[0]] = found[2]
    o = np.lexsort((f6.astype(np.int64), p4))
    p = _write_artifact(os.path.join(work, "wrong_parent"), sub,
                        _pack_tree(root_key, p4[o], f6[o], n, r), T)
    trial(f"re-pointed parent at the same depth (row {found[0]+1}: "
          f"{found[1]} -> {found[2]} -> {found[3]}), re-sorted into "
          f"canonical order", p, ["(c)", "(a)", "(e)"])

    # 10. malformed stream: the gap bitmap carries the wrong number of bits
    arr = _pack_tree(root_key, parent, flip, n, r)
    bits = np.unpackbits(arr['gap_bits'], bitorder='big')
    nb = int(arr['gap_nbits'][0])
    z = int(np.flatnonzero(bits[:nb] == 0)[0])
    bits[z] = 1                          # one extra "child"
    arr['gap_bits'] = np.packbits(bits, bitorder='big')
    p = _write_artifact(os.path.join(work, "malformed_gap"), sub, arr, T,
                        repair=False)
    trial("malformed gap stream (one extra one-bit, so the row count no "
          "longer matches)", p, ["(g)"])

    # 11. an out-of-range mutated-basis index (7 bits admit 126 and 127,
    #     which are not basis indices)
    f6 = flip.copy()
    f6[3] = 127
    arr = _pack_tree(root_key, parent, f6, n, r)
    p = _write_artifact(os.path.join(work, "flip_range"), sub, arr, T,
                        repair=False)
    trial("out-of-range mutated-basis index (127)", p, ["(g)"])

    # 12. rows out of canonical order (two adjacent rows swapped)
    p5 = parent.copy()
    f7 = flip.copy()
    a = None
    for k in range(NS - 2):
        if p5[k] == p5[k + 1] and f7[k] != f7[k + 1]:
            a = k
            break
    if a is not None:
        f7[a], f7[a + 1] = f7[a + 1], f7[a]
        arr = _pack_tree(root_key, p5, f7, n, r)
        p = _write_artifact(os.path.join(work, "unordered"), sub, arr, T,
                            repair=False)
        trial(f"rows out of canonical order (rows {a+1},{a+2} swapped)", p,
              ["(g)"])

    print("\n================ CANARY SUMMARY ================")
    allok = True
    for o in outcomes:
        allok &= o['pass']
        print(f"  {'PASS' if o['pass'] else 'FAIL'}  {o['canary']}: "
              f"{'rejected' if o['rejected'] else 'accepted'}"
              f"  {o['fired'] if o['fired'] else ''}")
    print("================================================")
    return allok, outcomes


# ======================================================================

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--artifact", required=True)
    ap.add_argument("--prefix", type=int, default=0,
                    help="reconstruct only the first N rows of the "
                         "canonical order (itself a complete certificate)")
    ap.add_argument("--structure-only", action="store_true",
                    help="run only (0) and (g): no reconstruction")
    ap.add_argument("--workers", type=int, default=2)
    ap.add_argument("--shard-size", type=int, default=100000)
    ap.add_argument("--state", default="")
    ap.add_argument("--extcount", default="")
    ap.add_argument("--legacy-crosscheck", default="")
    ap.add_argument("--canary", action="store_true")
    ap.add_argument("--work", default="data/canary_coverage")
    ap.add_argument("--canary-rows", type=int, default=20000)
    ap.add_argument("--show-root", action="store_true")
    a = ap.parse_args()
    a.workers = max(1, min(2, a.workers))     # 2 is the memory-safe maximum

    _assert_independent()

    if a.canary:
        ok, _ = canaries(a.artifact, a.work, a.canary_rows, a.workers)
        print("CANARY SUITE:", "PASS" if ok else "FAIL")
        sys.exit(0 if ok else 1)

    rep = Report()
    print(f"artifact: {a.artifact}")
    man = load_manifest(a.artifact)
    check_files(a.artifact, man, rep)
    tree = load_tree(a.artifact, man, rep)
    if tree is None:
        print("\n================ RESULT ================")
        print(f"  {len(rep.ok)} checks passed, {len(rep.fail)} failed")
        for f in rep.fail:
            print(f"    FAILED: {f}")
        sys.exit(1)
    T = build_tables(tree['n'], tree['r'])
    print(f"  (n,r) = ({tree['n']},{tree['r']}), {tree['count']} rows, "
          f"kappa = {T['kappa']}")
    if a.show_root:
        key = (int(tree['root_key'][0]) << 64) | int(tree['root_key'][1])
        s = ''.join('+' if (key >> (T['M'] - 1 - j)) & 1 else '-'
                    for j in range(T['M']))
        print(f"  root key: {key}\n  {s}")
        return
    selftest_action(T, rep)
    bounds = structure_checks(T, man, tree, rep)
    if bounds is None:
        print("\n================ RESULT ================")
        print(f"  {len(rep.ok)} checks passed, {len(rep.fail)} failed")
        for f in rep.fail:
            print(f"    FAILED: {f}")
        sys.exit(1)
    if a.extcount:
        extcount_check(a.extcount, man['n'], man['r'], rep)
    if a.structure_only:
        print("  --structure-only: no reconstruction, so checks "
              "(a),(b),(c),(d),(e),(h) are NOT run")
    else:
        N = tree['count']
        full = not a.prefix or a.prefix >= N
        if full:
            print(f"  FULL mode: reconstructing all {N} classes")
        else:
            print(f"  PREFIX mode: the first {a.prefix} of {N} rows -- a "
                  f"complete certificate for a smaller catalog, but NOT "
                  f"the (4,9) coverage claim")
        out = reconstruct(T, man, tree, bounds, rep, a.workers, a.state,
                          a.shard_size, nrows=0 if full else a.prefix)
        if out is not None:
            key_hi, key_lo, stab = out
            catalog_checks(man, key_hi, key_lo, stab, rep, full)
            if a.legacy_crosscheck:
                if full:
                    legacy_crosscheck(a.legacy_crosscheck, man, key_hi,
                                      key_lo, stab, rep)
                else:
                    print("  [note] --legacy-crosscheck needs a full run")

    print("\n================ RESULT ================")
    print(f"  {len(rep.ok)} checks passed, {len(rep.fail)} failed")
    for f in rep.fail:
        print(f"    FAILED: {f}")
    print("=======================================")
    sys.exit(1 if rep.fail else 0)


if __name__ == "__main__":
    main()
