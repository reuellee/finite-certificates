"""FAST standalone certificate checker (numpy).  Same verification
semantics as checker.py (V1-V5) but vectorized so that the (9,4)
certificate (~9.3M classes) verifies in minutes.  Independent
implementations throughout: its own colex ranking (combinatorial number
system), its own GP condition table derived from the axiom, its own
4-permutation parity LUT, its own group ops.  checker.py (pure python)
remains the reference for small certificates; both must agree.

Usage: python checker_fast.py <n> <r> <reps> <tree> <gens> <exhibits>
Files may be .gz.  reps: one +/- string per line.  tree/gens/exhibits:
same text formats as checker.py.
Exit 0 iff all checks pass.
"""
import gzip
import sys
import time
from itertools import combinations, permutations
from math import comb, factorial

import numpy as np


def op(path):
    return gzip.open(path, 'rt') if path.endswith('.gz') else open(path)


# ------------------------------------------------- independent structure

def colex_bases(n, r):
    return sorted(combinations(range(1, n + 1), r),
                  key=lambda B: tuple(sorted(B, reverse=True)))


def colex_rank_vec(np_sorted_rows, r):
    """colex rank of each sorted row via combinatorial number system:
    rank = sum_k C(row[k]-1, k+1)."""
    K = np_sorted_rows.shape[0]
    out = np.zeros(K, dtype=np.int64)
    maxv = int(np_sorted_rows.max()) if K else 1
    for k in range(r):
        vals = np_sorted_rows[:, k].astype(np.int64) - 1
        # C(vals, k+1) via lookup
        lut = np.array([comb(v, k + 1) for v in range(maxv + 1)],
                       dtype=np.int64)
        out += lut[vals]
    return out


def parity_lut_4(r):
    """LUT: argsort pattern code -> parity (0 even, 1 odd) for r-tuples."""
    lut = {}
    for p in permutations(range(r)):
        inv = sum(1 for i in range(r) for j in range(i + 1, r)
                  if p[i] > p[j])
        code = 0
        for x in p:
            code = code * r + x
        lut[code] = inv & 1
    arr = np.zeros(r ** r, dtype=np.uint8)
    for c, v in lut.items():
        arr[c] = v
    return arr


def fail(msg):
    print("CHECK FAILED:", msg)
    sys.exit(1)


def main(n, r, repsfile, treefile, gensfile, exfile):
    t0 = time.time()
    bases = colex_bases(n, r)
    M = len(bases)
    BAS = np.array(bases, dtype=np.int64)          # (M, r)
    PLUT = parity_lut_4(r)

    # ---- load reps as bit matrix (K, M) uint8, 1 = '+'
    rows = []
    with op(repsfile) as f:
        for line in f:
            line = line.strip()
            if line:
                if len(line) != M or set(line) - {'+', '-'}:
                    fail("malformed rep line")
                rows.append(np.frombuffer(line.encode(), dtype=np.uint8))
    S = np.vstack(rows)
    B = (S == ord('+')).astype(np.uint8)           # (K, M)
    K = B.shape[0]
    print(f"[fast] {K} reps loaded ({time.time()-t0:.0f}s)", flush=True)

    # ---- V1: GP conditions (derived here from the axiom)
    idx = {tuple(b): i for i, b in enumerate(bases)}
    conds = []
    E = range(1, n + 1)

    def sval(tup):
        t = tuple(sorted(tup))
        inv = sum(1 for i in range(len(tup))
                  for j in range(i + 1, len(tup)) if tup[i] > tup[j])
        return idx[t], inv & 1

    for lam in combinations(E, r - 2):
        rest = [x for x in E if x not in lam]
        for a, b, c, d in combinations(rest, 4):
            i1, s1 = sval(lam + (a, b))
            i2, s2 = sval(lam + (c, d))
            i3, s3 = sval(lam + (a, c))
            i4, s4 = sval(lam + (b, d))
            i5, s5 = sval(lam + (a, d))
            i6, s6 = sval(lam + (b, c))
            conds.append((i1, i2, s1 ^ s2, i3, i4, s3 ^ s4 ^ 1,
                          i5, i6, s5 ^ s6))
    C = np.array(conds, dtype=np.int64)
    blk = max(1, 20_000_000 // max(len(conds), 1))
    for lo in range(0, K, blk):
        Bb = B[lo:lo + blk]
        P1 = Bb[:, C[:, 0]] ^ Bb[:, C[:, 1]] ^ C[:, 2].astype(np.uint8)
        P2 = Bb[:, C[:, 3]] ^ Bb[:, C[:, 4]] ^ C[:, 5].astype(np.uint8)
        P3 = Bb[:, C[:, 6]] ^ Bb[:, C[:, 7]] ^ C[:, 8].astype(np.uint8)
        badrow = ((P1 == P2) & (P2 == P3)).any(axis=1)
        if badrow.any():
            fail(f"rep {lo + int(np.argmax(badrow))} violates GP")
    print(f"[fast] V1 ok: all reps satisfy GP ({time.time()-t0:.0f}s)",
          flush=True)

    # ---- load tree
    par = np.full(K, -1, dtype=np.int64)
    flip = np.zeros(K, dtype=np.int64)
    sig = np.zeros((K, n), dtype=np.int64)
    eps = np.zeros(K, dtype=np.int64)
    gs = np.zeros(K, dtype=np.int64)
    seen = np.zeros(K, dtype=bool)
    with op(treefile) as f:
        for line in f:
            parts = line.split()
            if not parts:
                continue
            cid = int(parts[0])
            if seen[cid]:
                fail("duplicate tree line")
            seen[cid] = True
            if parts[1] == 'root':
                if cid != 0:
                    fail("root must be class 0")
                sig[cid] = np.arange(1, n + 1)
                continue
            par[cid] = int(parts[1])
            flip[cid] = int(parts[2])
            sig[cid] = [int(x) for x in parts[3].split(',')]
            eps[cid] = int(parts[4])
            gs[cid] = int(parts[5])
    if not seen.all():
        fail("tree does not cover all classes")
    if not (par[1:] < np.arange(1, K)).all():
        fail("tree not topologically ordered")
    print(f"[fast] tree loaded ({time.time()-t0:.0f}s)", flush=True)

    # ---- V2 vectorized: for each edge, act (sigma,eps,s) on rep[child]
    # and compare with rep[parent] xor bit(flip), allowing global flip.
    # new(Bset) = (-1)^(s + |eps cap Bset| + sortparity) chi(sigma^-1 Bset)
    # Equivalently push forward: for each source basis Bk of the child,
    # its image sorted set has index via colex rank and sign via parity.
    blk2 = max(1, 4_000_000 // M)
    powers = (r ** np.arange(r - 1, -1, -1)).astype(np.int64)
    for lo in range(1, K, blk2):
        hi = min(K, lo + blk2)
        ids = np.arange(lo, hi)
        sg = sig[ids]                                  # (m, n)
        img = sg[:, BAS - 1]                           # (m, M, r) images
        srt = np.sort(img, axis=2)
        arg = np.argsort(img, axis=2, kind='stable')
        code = (arg * powers).sum(axis=2)              # (m, M)
        par4 = PLUT[code]                              # (m, M) sort parity
        # eps contribution: popcount of eps over image elements
        ep = eps[ids][:, None]                         # (m, 1)
        ebits = np.zeros(img.shape[:2], dtype=np.uint8)
        for k in range(r):
            ebits ^= ((ep >> (srt[:, :, k] - 1)) & 1).astype(np.uint8)
        tgt_idx = colex_rank_vec(srt.reshape(-1, r), r).reshape(
            srt.shape[0], M)
        childbits = B[ids]                             # (m, M)
        val = childbits ^ par4 ^ ebits ^ (gs[ids][:, None] & 1).astype(
            np.uint8)
        out = np.zeros_like(val)
        np.put_along_axis(out, tgt_idx, val, axis=1)
        # compare with parent xor flip-bit
        pb = B[par[ids]].copy()
        pb[np.arange(hi - lo), flip[ids]] ^= 1
        eq = (out == pb).all(axis=1)
        eqneg = (out ^ 1 == pb).all(axis=1)
        okv = eq | eqneg
        if not okv.all():
            fail(f"tree edge fails at class {int(ids[np.argmax(~okv)])}")
    print(f"[fast] V2 ok: all {K-1} tree edges verified "
          f"({time.time()-t0:.0f}s)", flush=True)

    # ---- transports, gens, exhibits: reuse the (slow, tiny) logic by
    # delegating to checker.py's implementation-free parts is not allowed
    # (independence); reimplement compactly here.
    def compose(g1, g2):
        s1, e1, x1 = g1
        s2, e2, x2 = g2
        sg_ = tuple(s1[s2[i] - 1] for i in range(n))
        e = e1
        for i in range(n):
            if (e2 >> i) & 1:
                e ^= 1 << (s1[i] - 1)
        return (sg_, e, x1 ^ x2)

    def inverse(g):
        sgg, e, s = g
        inv = [0] * n
        for i in range(n):
            inv[sgg[i] - 1] = i + 1
        e2 = 0
        for i in range(n):
            if (e >> i) & 1:
                e2 |= 1 << (inv[i] - 1)
        return (tuple(inv), e2, s)

    def act_bits(g, bits):
        sgg, e, s = g
        im = np.array(sgg, dtype=np.int64)[BAS - 1]
        srt = np.sort(im, axis=1)
        arg = np.argsort(im, axis=1, kind='stable')
        code = (arg * powers).sum(axis=1)
        p4 = PLUT[code]
        eb = np.zeros(M, dtype=np.uint8)
        for k in range(r):
            eb ^= ((e >> (srt[:, k] - 1)) & 1).astype(np.uint8)
        tgt = colex_rank_vec(srt, r)
        val = bits ^ p4 ^ eb ^ (s & 1)
        out = np.zeros_like(val)
        out[tgt] = val
        return out

    tau = [None] * K
    tau[0] = (tuple(range(1, n + 1)), 0, 0)
    for cid in range(1, K):
        tau[cid] = compose(tau[par[cid]],
                           (tuple(int(x) for x in sig[cid]),
                            int(eps[cid]), int(gs[cid])))
        if cid % 1000000 == 0:
            print(f"[fast] transports ... {cid}/{K}", flush=True)
    print(f"[fast] transports done ({time.time()-t0:.0f}s)", flush=True)

    gens = []
    with op(gensfile) as f:
        for line in f:
            parts = line.split()
            if not parts:
                continue
            prov = parts[0].split('|')
            h = (tuple(int(x) for x in parts[1].split(',')),
                 int(parts[2]), int(parts[3]))
            if prov[0] == 'stab':
                c = int(prov[1])
                u = compose(compose(inverse(tau[c]), h), tau[c])
                img = act_bits(u, B[c])
                if not ((img == B[c]).all() or (img ^ 1 == B[c]).all()):
                    fail(f"stab gen at class {c} fails")
            elif prov[0] == 'edge':
                c, j, c2 = int(prov[1]), int(prov[2]), int(prov[3])
                t = compose(compose(inverse(tau[c]), h), tau[c2])
                img = act_bits(t, B[c2])
                pb = B[c].copy()
                pb[j] ^= 1
                if not ((img == pb).all() or (img ^ 1 == pb).all()):
                    fail(f"edge gen ({c},{j},{c2}) fails")
            else:
                fail("unknown provenance")
            gens.append(h)
    print(f"[fast] V3 ok: {len(gens)} generators verified "
          f"({time.time()-t0:.0f}s)", flush=True)

    # V4: order of <perm parts> via orbit-stabilizer chain (own impl)
    def group_order(perms):
        perms = [tuple(p) for p in perms
                 if tuple(p) != tuple(range(1, n + 1))]
        if not perms:
            return 1

        def helper(gens_, pts):
            if not gens_ or not pts:
                return 1
            p = pts[0]
            orb = {p: tuple(range(1, n + 1))}
            fr = [p]
            while fr:
                x = fr.pop()
                tx = orb[x]
                for g in gens_:
                    y = g[x - 1]
                    if y not in orb:
                        orb[y] = tuple(g[tx[i] - 1] for i in range(n))
                        fr.append(y)
            stab = set()
            for x, tx in orb.items():
                for g in gens_:
                    y = g[x - 1]
                    ty = orb[y]
                    tyi = [0] * n
                    for i in range(n):
                        tyi[ty[i] - 1] = i + 1
                    w = tuple(g[tx[i] - 1] for i in range(n))
                    sgen = tuple(tyi[w[i] - 1] for i in range(n))
                    if sgen != tuple(range(1, n + 1)):
                        stab.add(sgen)
            return len(orb) * helper(sorted(stab), pts[1:])

        return helper(perms, list(range(1, n + 1)))

    order = group_order([g[0] for g in gens])
    if order != factorial(n):
        fail(f"perm parts generate order {order} != {factorial(n)}")
    print(f"[fast] V4 ok: S_{n} generated (order {order})", flush=True)

    # V5 exhibits
    basis = {}

    def gadd(v):
        while v:
            p = v.bit_length() - 1
            if p in basis:
                v ^= basis[p]
            else:
                basis[p] = v
                return True
        return False

    gadd((1 << n) - 1)
    with op(exfile) as f:
        for line in f:
            parts = line.split()
            if not parts:
                continue
            word = [int(x) for x in parts[1].split(',')]
            g = (tuple(range(1, n + 1)), 0, 0)
            for idx2 in word:
                fpart = gens[idx2] if idx2 >= 0 else inverse(
                    gens[-idx2 - 1])
                g = compose(g, fpart)
            if g[0] != tuple(range(1, n + 1)):
                fail("exhibit not pure sign")
            gadd(g[1])
    if len(basis) != n:
        fail(f"sign dim {len(basis)} != {n}")
    print(f"[fast] V5 ok: sign space full ({time.time()-t0:.0f}s)")
    print(f"[fast] ALL CHECKS PASSED on {K} classes.")
    return 0


if __name__ == "__main__":
    sys.exit(main(int(sys.argv[1]), int(sys.argv[2]), sys.argv[3],
                  sys.argv[4], sys.argv[5], sys.argv[6]))
