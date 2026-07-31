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
      table sums arithmetically to that same target.

WHAT IT DOES NOT VERIFY.  It does not recompute the extension counts E(c)
themselves; check (f) only confirms that the tracked table adds up.  Check
(b) is relative to the manifest's convention: the unrestricted maximum over
all of S_n is not computable at this scale (~1.5 s/class, ~160 CPU-days),
so the certified statement is "extremal under the documented colour-
restricted convention".  That convention is a well-defined function of the
G'-orbit -- see canonical_convention() -- which is all the distinctness
argument needs, but the reader has to read those forty lines rather than
take a one-word "canonical" on trust.

USAGE
  python coverage_checker.py --artifact data/coverage_4_9              # full
  python coverage_checker.py --artifact data/coverage_4_9 --sample 100000
  python coverage_checker.py --artifact data/coverage_4_9 --cheap-only
  python coverage_checker.py --artifact data/coverage_4_9 \
        --extcount data/extcount_4_9.jsonl --workers 4 --state .covstate
  python coverage_checker.py --canary --artifact data/coverage_4_9 \
        --work data/canary_coverage        # sabotage suite; must REJECT
  python coverage_checker.py --artifact data/coverage_4_9 --show 0

Checks (a),(b),(d) are sharded, run on at most --workers processes
(default 4), and checkpointed: each finished shard drops a small JSON in
--state, and a re-run skips it.  Checks (c),(e) are cheap and always run
over every row.
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
    if man.get('complete'):
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
    jobs = []
    done = []
    for s in range(nsh):
        a, b = s * shard_size, min((s + 1) * shard_size, len(rows))
        sp = (os.path.join(statedir, f"shard_{tag}_{s:05d}.json")
              if statedir else None)
        if sp and os.path.exists(sp):
            with open(sp) as f:
                done.append(json.load(f))
            continue
        rr = rows[a:b]
        jobs.append((s, rr, key_hi[rr], key_lo[rr], stab[rr]))
    if done:
        print(f"  resuming: {len(done)} shard(s) already checkpointed")
    t0 = time.time()
    results = list(done)
    if jobs:
        if workers <= 1:
            _init(n, r)
            for j in jobs:
                results.append(_one(j, statedir, tag, quiet, t0,
                                    len(jobs), len(results) - len(done)))
        else:
            import multiprocessing as mp
            ctx = mp.get_context('spawn')
            with ctx.Pool(workers, initializer=_init,
                          initargs=(n, r)) as pool:
                k = 0
                for res in pool.imap_unordered(check_shard, jobs):
                    k += 1
                    _save(res, statedir, tag)
                    results.append(res)
                    if not quiet:
                        el = time.time() - t0
                        print(f"    shard {res['shard']:5d}  "
                              f"{res['nrows']} rows  {res['seconds']:.0f}s "
                              f"| {k}/{len(jobs)}  elapsed {el:.0f}s",
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

def _write_artifact(path, man, key_hi, key_lo, stab, fix_totals):
    """Write a (possibly sabotaged) artifact with a SELF-CONSISTENT
    manifest: all SHA-256 values are recomputed, so no canary is caught
    merely by a stale hash.  `fix_totals` also recomputes count/mass, which
    isolates the mathematical checks from check (e)."""
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
    with open(os.path.join(path, "MANIFEST.json"), "w") as f:
        json.dump(m, f, indent=1)
    return path


def _resort(key_hi, key_lo, stab):
    o = np.lexsort((key_lo, key_hi))
    return key_hi[o], key_lo[o], stab[o]


def _run_all(adir, workers, statedir, shard_size, extcount=None):
    rep = Report()
    man, kh, kl, st = load_artifact(adir, rep)
    cheap_checks(man, kh, kl, st, rep)
    rows = np.arange(len(kh), dtype=np.int64)
    run_expensive(man, kh, kl, st, rows, rep, workers, statedir,
                  shard_size, quiet=True)
    if extcount:
        extcount_check(extcount, man['n'], man['r'], rep)
    return rep


def canaries(adir, work, nrows, workers):
    """Build sabotaged copies of a small sub-artifact and require rejection.

    Every sabotage is shipped with a REGENERATED, internally consistent
    manifest (fresh SHA-256s), i.e. we assume an adversary who can rewrite
    the manifest.  A checker that only compared hashes would pass all of
    these.  Canary 6 is the exception: it leaves a stale hash in place, to
    confirm the integrity path itself works.
    """
    rep0 = Report()
    man, KH, KL, ST = load_artifact(adir, rep0)
    if rep0.fail:
        raise SystemExit("base artifact failed its own integrity check")
    T = build_tables(man['n'], man['r'])
    kh, kl, st = KH[:nrows].copy(), KL[:nrows].copy(), ST[:nrows].copy()
    base = os.path.join(work, "control")
    sub = json.loads(json.dumps(man))
    sub['complete'] = False
    sub['provenance'] = {'note': f'canary sub-artifact: first {nrows} rows'}
    _write_artifact(base, sub, kh, kl, st, fix_totals=True)

    outcomes = []

    def trial(name, path, expect_checks):
        print(f"\n--- canary: {name}")
        rep = _run_all(path, workers, None, 100000)
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

    print("\n--- control: untampered sub-artifact (must PASS)")
    repc = _run_all(base, workers, None, 100000)
    outcomes.append({'canary': 'control (untampered)',
                     'rejected': bool(repc.fail), 'fired': repc.fail,
                     'expected_one_of': [], 'pass': not repc.fail})
    print(f"  -> {'ACCEPTED' if not repc.fail else 'REJECTED'}")

    # 1. duplicated key (kept sorted, totals repaired: only (c) can fire)
    a, b, c = kh.copy(), kl.copy(), st.copy()
    a[7] = a[6]
    b[7] = b[6]
    c[7] = c[6]
    p = _write_artifact(os.path.join(work, "dup_key"), sub, a, b, c, True)
    trial("duplicated key", p, ["(c)"])

    # 2. non-canonical key: replace one key by another member of its orbit
    a, b, c = kh.copy(), kl.copy(), st.copy()
    i = 11
    S = decode_keys(T, a[i:i + 1], b[i:i + 1])
    alt = None
    for perm in permutations(range(1, T['n'] + 1)):
        PL = np.array([perm], dtype=np.uint8)
        R = sign_max(T, relabel_batch(T, S, np.array([0]), PL))
        h, l = encode_keys(T, R)
        if (h[0], l[0]) != (a[i], b[i]):
            alt = (h[0], l[0])
            break
    a[i], b[i] = alt
    a, b, c = _resort(a, b, c)
    p = _write_artifact(os.path.join(work, "noncanonical"), sub, a, b, c,
                        True)
    trial("non-canonical key (same orbit, different representative)", p,
          ["(b)"])

    # 3. corrupted stabilizer order, with the manifest mass repaired so
    #    that only the recomputation can catch it
    a, b, c = kh.copy(), kl.copy(), st.copy()
    j = int(np.flatnonzero(c == c.min())[0])
    c[j] = c[j] * 2
    p = _write_artifact(os.path.join(work, "bad_stab"), sub, a, b, c, True)
    trial("corrupted stabilizer order (mass repaired to match)", p, ["(d)"])

    # 4. GP-invalid key: flip a NON-mutable basis, so validity really breaks
    a, b, c = kh.copy(), kl.copy(), st.copy()
    i = 23
    S = decode_keys(T, a[i:i + 1], b[i:i + 1])
    p1, p2, p3 = gp_parities(T, S)
    mut = mutable_mask(T, p1, p2, p3)[0]
    jbad = int(np.flatnonzero(~mut)[0])
    S[0, jbad] ^= 1
    h, l = encode_keys(T, S)
    a[i], b[i] = h[0], l[0]
    a, b, c = _resort(a, b, c)
    p = _write_artifact(os.path.join(work, "gp_invalid"), sub, a, b, c, True)
    trial("GP-invalid key (flipped a non-mutable basis)", p, ["(a)"])

    # 5. truncated file: rows dropped, manifest totals NOT repaired
    a, b, c = kh[:-500].copy(), kl[:-500].copy(), st[:-500].copy()
    p = _write_artifact(os.path.join(work, "truncated"), sub, a, b, c, False)
    trial("truncated artifact (500 rows dropped, mass short)", p,
          ["(e)"])

    # 6. stale hash: data changed, manifest hashes left alone
    src = os.path.join(work, "stale_hash")
    os.makedirs(src, exist_ok=True)
    a, b, c = kh.copy(), kl.copy(), st.copy()
    c[3] = 4 if c[3] != 4 else 6
    n, r = man['n'], man['r']
    np.savez_compressed(os.path.join(src, f"coverage_{r}_{n}.npz"),
                        key_hi=a, key_lo=b, stab=c)
    with open(os.path.join(base, "MANIFEST.json")) as f:
        stale = json.load(f)         # the CONTROL's manifest, left untouched
    with open(os.path.join(src, "MANIFEST.json"), "w") as f:
        json.dump(stale, f, indent=1)
    trial("stale SHA-256 (integrity path)", src, ["(0)"])

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
    ap.add_argument("--sample", type=int, default=0,
                    help="check (a),(b),(d) on N pseudorandom rows only")
    ap.add_argument("--seed", type=int, default=20260731)
    ap.add_argument("--cheap-only", action="store_true")
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
    print(f"  (n,r) = ({man['n']},{man['r']}), {len(kh)} rows, "
          f"kappa = {build_tables(man['n'], man['r'])['kappa']}")
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
    if not a.cheap_only:
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
        print("  --cheap-only: checks (a),(b),(d) NOT run")

    print("\n================ RESULT ================")
    print(f"  {len(rep.ok)} checks passed, {len(rep.fail)} failed")
    for f in rep.fail:
        print(f"    FAILED: {f}")
    print("=======================================")
    sys.exit(1 if rep.fail else 0)


if __name__ == "__main__":
    main()
