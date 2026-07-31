"""Export the (r,n) coverage artifact.

Reads the level_*.npz checkpoints of a completed runbig.py campaign and emits

    <out>/tree_<r>_<n>.npz          THE CERTIFICATE (small, tracked in git):
                                    the root key + per class (parent, flip)
    <out>/coverage_<r>_<n>.npz      legacy: key_hi, key_lo (uint64), stab
    <out>/witness_<r>_<n>.npz       legacy: parent, flip, sigma, eps, gsgn,
                                    depth
    <out>/MANIFEST.json             conventions, counts, mass, SHA-256s

THE COMPACT CERTIFICATE.  The two legacy arrays total ~145 MB, which is too
much for a repository.  They are also redundant: the mutation identity

    (sigma_i, eps_i, gsgn_i) . chi_i  ==  mu_{B_flip[i]} ( chi_parent[i] )

says that chi_i lies in the G'-orbit of mu_{B_flip[i]}(chi_parent[i]), and
the class key is by construction a function of that orbit alone.  Read as a
DERIVATION rather than as a check, it means the tree determines the keys:
from the root key, and per class the parent and the mutated basis, every
chirotope is computable, its canonical key follows from the canonicalization
the checker already performs, and the stabilizer order from the same argmax
count.  Depth and the voltage are likewise derivable.  So the irreducible
core of the artifact is (root key, parent, flip) -- about 10.4 MB packed --
and `coverage_checker.py` reconstructs the rest.

ROW ORDER.  Rows are in the CANONICAL TREE ORDER: sorted by (depth, position
of parent, mutated-basis index), the root first.  This is a function of the
tree alone (an induction on depth), it makes `parent` strictly precede its
row and globally nondecreasing -- which is what makes the tree a 2.3 MB gap
bitmap -- and it lets the checker verify the layout, so that no reordering
of the rows can pass unnoticed.  A PREFIX of this order is closed under
`parent`, hence is itself a complete certificate for a smaller catalog.

The legacy arrays are still written (they are what `--legacy-crosscheck`
compares the reconstruction against) but they are not needed to check the
certificate and are not tracked.

THE WITNESS.  Row i of the witness refers to row i of the coverage array.
For every non-root row it records

    parent[i]  the coverage row of the class the search reached i from,
    flip[i]    the colex index of the basis that was mutated,
    sigma[i]   a permutation of 1..n, sigma[i][x-1] = sigma(x),
    eps[i]     a reorientation bitmask, bit (x-1) = element x reoriented,
    gsgn[i]    the global sign s in {0,1},
    depth[i]   the distance from row i to the root in the parent forest,

with the defining identity, in exact integer arithmetic,

    (sigma[i], eps[i], gsgn[i]) . chi_i  ==  mu_{B_flip[i]} ( chi_parent[i] )

where chi_i is the chirotope decoded from key i and mu_B negates the sign
on basis B.  In the language of the note that group element is precisely
the VOLTAGE of the mutation edge (parent[i] -> i).  The root carries
parent = -1 and the sentinel values flip = 0, sigma = identity, eps = 0,
gsgn = 0, depth = 0.

This script is generator-side: it only *transports* data that runbig.py
produced, and re-derives gsgn (which runbig.py does not store, because it
works with chirotopes only up to global sign).  It aborts if the identity
above fails for any row, but that abort is a sanity gate, not a check: the
checking is coverage_checker.py's job.

Usage:  python export_coverage.py 4 9 data/big_4_9 data/coverage_4_9
"""
import glob
import hashlib
import io
import json
import os
import sys
import time
import zipfile
from itertools import combinations
from math import comb, factorial

import numpy as np
from numpy.lib import format as npformat

TREE_FORMAT = "omgamma-tree-v1"
FIXED_ZIP_DATE = (1980, 1, 1, 0, 0, 0)


def sha256_file(path, bufsize=1 << 20):
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        while True:
            chunk = f.read(bufsize)
            if not chunk:
                break
            h.update(chunk)
    return h.hexdigest()


def sha256_array(a):
    """SHA-256 of the raw little-endian C-contiguous buffer of `a`."""
    return hashlib.sha256(np.ascontiguousarray(a).tobytes()).hexdigest()


def colex_bases(n, r):
    return sorted(combinations(range(1, n + 1), r),
                  key=lambda t: tuple(reversed(t)))


def key_string(key, M):
    return ''.join('+' if (key >> (M - 1 - j)) & 1 else '-'
                   for j in range(M))


# ----------------------------------------------------------------------
# group action on decoded sign vectors (used only to re-derive gsgn and to
# gate the export; coverage_checker.py rebuilds all of this independently)
# ----------------------------------------------------------------------

def action_tables(n, r):
    bases = colex_bases(n, r)
    M = len(bases)
    TAB = np.full((n + 1,) * r, -1, dtype=np.int32)
    for j, B in enumerate(bases):
        TAB[B] = j
    BAS = np.array(bases, dtype=np.int64)
    bm = np.zeros(M, dtype=np.int64)
    for j, B in enumerate(bases):
        for x in B:
            bm[j] |= 1 << (x - 1)
    EPSTAB = np.zeros((1 << n, M), dtype=np.uint8)
    for e in range(1 << n):
        EPSTAB[e] = [bin(e & int(bm[j])).count('1') & 1 for j in range(M)]
    return {'n': n, 'r': r, 'M': M, 'BAS': BAS, 'TAB': TAB, 'EPSTAB': EPSTAB}


def decode(A, key_hi, key_lo):
    """(B,) uint64 pairs -> (B,M) uint8, column j = [chi(B_j) = +1]."""
    B = len(key_hi)
    buf = np.empty((B, 16), dtype=np.uint8)
    buf[:, :8] = key_hi.astype('>u8').view(np.uint8).reshape(B, 8)
    buf[:, 8:] = key_lo.astype('>u8').view(np.uint8).reshape(B, 8)
    bits = np.unpackbits(buf, axis=1, bitorder='big')
    return np.ascontiguousarray(bits[:, 128 - A['M']:])


def act(A, S, sigma, eps):
    """Apply (sigma, eps, 0) to each row of S (same length)."""
    n, r, M = A['n'], A['r'], A['M']
    P = len(S)
    inv = np.zeros((P, n), dtype=np.int64)          # inv[:,p-1] = sig^{-1}(p)
    np.put_along_axis(inv, sigma.astype(np.int64) - 1,
                      np.tile(np.arange(1, n + 1, dtype=np.int64), (P, 1)),
                      axis=1)
    idx = (A['BAS'] - 1).ravel()
    img = inv[:, idx].reshape(P, M, r)
    par = np.zeros((P, M), dtype=np.uint8)
    for a in range(r):
        for b in range(a + 1, r):
            par ^= (img[:, :, a] > img[:, :, b])
    srt = np.sort(img, axis=2)
    tgt = A['TAB'][tuple(srt[:, :, a] for a in range(r))]
    out = np.take_along_axis(S, tgt.astype(np.intp), axis=1) ^ par
    out ^= A['EPSTAB'][eps.astype(np.intp)]
    return out


# ----------------------------------------------------------------------
# the compact certificate: canonical tree order, then a bit-level packing
# ----------------------------------------------------------------------

def canonical_tree_order(parent, flip, depth):
    """Positions of the rows in the canonical tree order.

    Row 0 is the root; the rows of depth d follow, ordered by (position of
    parent, mutated basis).  Defined by induction on depth, so it depends
    only on the tree, not on the order the search happened to discover
    classes in.  Returns (pos, blocks) with blocks[d] the first position of
    depth d and blocks[-1] = N.
    """
    N = len(parent)
    D = int(depth.max())
    pos = np.full(N, -1, dtype=np.int64)
    root = int(np.flatnonzero(parent < 0)[0])
    pos[root] = 0
    nxt = 1
    blocks = [0, 1]
    for d in range(1, D + 1):
        ids = np.flatnonzero(depth == d)
        ids = ids[np.lexsort((flip[ids], pos[parent[ids]]))]
        pos[ids] = np.arange(nxt, nxt + len(ids), dtype=np.int64)
        nxt += len(ids)
        blocks.append(nxt)
    if nxt != N or int((pos < 0).sum()):
        raise SystemExit("canonical order did not cover every row")
    return pos, blocks


def pack_tree(root_key, parent, flip, n, r):
    """(root key, parent, flip) -> the arrays of the certificate.

    `parent` is nondecreasing and parent[i] < i, so the whole parent map is
    a monotone gap bitmap: for each row i = 1..N-1 in order, write
    parent[i]-parent[i-1] zero bits (parent[0] := 0) and then a single one
    bit.  `flip` is packed at 7 bits per row, most significant bit first.
    """
    N = len(parent)
    par = parent[1:].astype(np.int64)
    if not (par < np.arange(1, N)).all():
        raise SystemExit("parent does not strictly precede its row")
    if not (np.diff(par) >= 0).all():
        raise SystemExit("parent is not nondecreasing in canonical order")
    gaps = np.diff(np.concatenate(([0], par)))
    nbits = int((N - 1) + int(par[-1]))
    bits = np.zeros(nbits, dtype=np.uint8)
    bits[np.cumsum(gaps + 1) - 1] = 1
    if int(bits.sum()) != N - 1:
        raise SystemExit("gap bitmap does not carry one bit per row")
    fb = np.zeros((N - 1, 7), dtype=np.uint8)
    f = flip[1:]
    if int(f.max()) >= comb(n, r):
        raise SystemExit("flip index out of range")
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


def save_npz_deterministic(path, arrays):
    """A .npz written STORED (no compression) with a fixed timestamp.

    The payload is already bit-packed, so there is nothing for a compressor
    to find; storing it means the file does not depend on the zlib version
    and is byte-for-byte reproducible.  `np.load` reads it normally.
    """
    with zipfile.ZipFile(path, 'w', compression=zipfile.ZIP_STORED) as zf:
        for name, arr in arrays.items():
            buf = io.BytesIO()
            npformat.write_array(buf, np.asanyarray(arr), allow_pickle=False)
            zi = zipfile.ZipInfo(name + '.npy', date_time=FIXED_ZIP_DATE)
            zi.compress_type = zipfile.ZIP_STORED
            zi.external_attr = 0o600 << 16
            zf.writestr(zi, buf.getvalue())


def main(r, n, indir, outdir):
    t0 = time.time()
    M = comb(n, r)
    Gn = factorial(n) * (1 << (n + 1))            # |G'| = n! * 2^n * 2
    os.makedirs(outdir, exist_ok=True)

    files = sorted(glob.glob(os.path.join(indir, "level_*.npz")))
    if not files:
        raise SystemExit(f"no level files in {indir}")
    lv = [int(os.path.basename(p)[6:9]) for p in files]
    if lv != list(range(len(files))):
        raise SystemExit(f"level files not contiguous: {lv}")
    with open(os.path.join(indir, "meta.json")) as f:
        meta = json.load(f)
    if not meta.get('complete'):
        raise SystemExit("meta.json does not say complete=true; refusing")

    N = int(meta['total_classes'])
    key_hi = np.empty(N, dtype=np.uint64)
    key_lo = np.empty(N, dtype=np.uint64)
    stab = np.empty(N, dtype=np.uint8)
    par_id = np.empty(N, dtype=np.int32)      # in BFS-id space
    flip = np.empty(N, dtype=np.uint8)
    sigma = np.empty((N, n), dtype=np.uint8)
    eps = np.empty(N, dtype=np.uint16)
    bounds = []
    off = 0
    for p in files:
        z = np.load(p)
        k = z['keys']
        m = len(k)
        if off + m > N:
            raise SystemExit("more rows than meta.json declares")
        key_hi[off:off + m] = k[:, 0]
        key_lo[off:off + m] = k[:, 1]
        s = z['stab']
        if s.max() > 255:
            raise SystemExit("stabilizer order exceeds uint8")
        stab[off:off + m] = s.astype(np.uint8)
        pa = z['parent']
        if pa.max() >= off + m or (off and pa.min() < 0):
            raise SystemExit("parent pointer out of range")
        par_id[off:off + m] = pa.astype(np.int32)
        flip[off:off + m] = z['flip']
        sigma[off:off + m] = z['sigma']
        e = z['eps']
        if int(e.max()) >= (1 << n):
            raise SystemExit("eps out of range")
        eps[off:off + m] = e.astype(np.uint16)
        bounds.append((off, off + m))
        off += m
        del z, k, s, pa, e
        print(f"  read {os.path.basename(p)}: {m}", flush=True)
    if off != N:
        raise SystemExit(f"row count {off} != meta {N}")
    print(f"  {N} rows, {time.time()-t0:.0f}s", flush=True)

    # --- depth in the parent forest, in BFS-id order -------------------
    depth = np.zeros(N, dtype=np.int32)
    roots = np.flatnonzero(par_id < 0)
    if roots.tolist() != [0]:
        raise SystemExit(f"expected exactly one root at id 0, got {roots}")
    a0, b0 = bounds[0]
    for c in range(1, b0):                    # level 0 is an internal chain
        p = int(par_id[c])
        if not 0 <= p < c:
            raise SystemExit(f"level-0 parent {p} of {c} is not earlier")
        depth[c] = depth[p] + 1
    for (a, b) in bounds[1:]:
        pp = par_id[a:b].astype(np.intp)
        if pp.min() < 0 or pp.max() >= a:
            raise SystemExit("parent pointer outside the earlier levels")
        depth[a:b] = depth[pp] + 1
    maxdepth = int(depth.max())
    if maxdepth >= (1 << 16):
        raise SystemExit("tree depth exceeds uint16")
    print(f"  spanning tree: 1 root, max depth {maxdepth}", flush=True)

    # --- THE COMPACT CERTIFICATE, in canonical tree order --------------
    tpos, tblocks = canonical_tree_order(par_id.astype(np.int64), flip, depth)
    tparent = np.empty(N, dtype=np.int64)
    tflip = np.empty(N, dtype=np.uint8)
    tdepth = np.empty(N, dtype=np.int64)
    tparent[tpos] = np.where(par_id < 0, -1,
                             tpos[np.maximum(par_id, 0).astype(np.intp)])
    tflip[tpos] = flip
    tdepth[tpos] = depth
    troot = int(np.flatnonzero(par_id < 0)[0])
    root_key = np.array([key_hi[troot], key_lo[troot]], dtype=np.uint64)
    # gates: the layout the certificate's encoding and the checker rely on
    if int(tparent[0]) != -1:
        raise SystemExit("the root is not row 0 of the canonical order")
    if not bool((tparent[1:] < np.arange(1, N)).all()):
        raise SystemExit("parent does not strictly precede its row")
    if not bool((tdepth[1:] == tdepth[tparent[1:]] + 1).all()):
        raise SystemExit("depth is not parent-depth + 1 in canonical order")
    lexkey = ((tdepth[1:] << 40) | (tparent[1:] << 7) | tflip[1:])
    if not bool((np.diff(lexkey) > 0).all()):
        raise SystemExit("rows are not strictly ordered by "
                         "(depth, parent, flip)")
    del lexkey
    tree_arrays = pack_tree(root_key, tparent, tflip, n, r)
    tnpz = os.path.join(outdir, f"tree_{r}_{n}.npz")
    save_npz_deterministic(tnpz, tree_arrays)
    tsize = os.path.getsize(tnpz)
    print(f"  wrote {tnpz}: {tsize/1e6:.2f} MB "
          f"(root key {int(root_key[0])}*2^64+{int(root_key[1])})", flush=True)

    # --- sort by key, and carry the witness along ---------------------
    order = np.lexsort((key_lo, key_hi))
    row_of_id = np.empty(N, dtype=np.int32)
    row_of_id[order] = np.arange(N, dtype=np.int32)
    key_hi = key_hi[order]
    key_lo = key_lo[order]
    stab = stab[order]
    flip = flip[order]
    sigma = sigma[order]
    eps = eps[order]
    depth = depth[order].astype(np.uint16)
    pid = par_id[order]
    del par_id
    parent = np.where(pid < 0, np.int32(-1),
                      row_of_id[np.maximum(pid, 0)]).astype(np.int32)
    del pid, row_of_id, order
    root_row = int(np.flatnonzero(parent < 0)[0])
    if int((parent < 0).sum()) != 1:
        raise SystemExit("remapped forest does not have exactly one root")
    flip[root_row] = 0
    sigma[root_row] = np.arange(1, n + 1, dtype=np.uint8)
    eps[root_row] = 0
    if int(depth[root_row]) != 0:
        raise SystemExit("root does not have depth 0")
    nr = np.ones(N, dtype=bool)
    nr[root_row] = False
    if not bool((depth[nr] == depth[parent[nr].astype(np.intp)] + 1).all()):
        raise SystemExit("depth is not parent-depth + 1 after remapping")
    del nr

    inc = ((key_hi[1:] > key_hi[:-1]) |
           ((key_hi[1:] == key_hi[:-1]) & (key_lo[1:] > key_lo[:-1])))
    if not bool(inc.all()):
        raise SystemExit("keys are not pairwise distinct after sorting")
    del inc

    uniq, cnt = np.unique(stab, return_counts=True)
    hist = {int(u): int(c) for u, c in zip(uniq.tolist(), cnt.tolist())}
    mass = 0
    for u, c in hist.items():
        if Gn % u:
            raise SystemExit(f"stabilizer order {u} does not divide |G'|")
        mass += (Gn // u) * c
    print(f"  mass {mass}  (meta {meta['total_mass']})", flush=True)
    if mass != int(meta['total_mass']):
        raise SystemExit("recomputed mass disagrees with meta.json")

    npz = os.path.join(outdir, f"coverage_{r}_{n}.npz")
    np.savez_compressed(npz, key_hi=key_hi, key_lo=key_lo, stab=stab)
    size = os.path.getsize(npz)
    print(f"  wrote {npz}: {size/1e6:.1f} MB", flush=True)

    # --- derive gsgn, and gate the whole witness on the identity ------
    A = action_tables(n, r)
    gsgn = np.zeros(N, dtype=np.uint8)
    CH = 65536
    t1 = time.time()
    for a in range(0, N, CH):
        b = min(a + CH, N)
        S = decode(A, key_hi[a:b], key_lo[a:b])
        R = act(A, S, sigma[a:b], eps[a:b])
        del S
        pr = parent[a:b].astype(np.intp)
        pr_safe = np.maximum(pr, 0)
        P = decode(A, key_hi[pr_safe], key_lo[pr_safe])
        P[np.arange(b - a), flip[a:b].astype(np.intp)] ^= 1
        same = (R == P).all(axis=1)
        comp = (R == (P ^ 1)).all(axis=1)
        del R, P
        isroot = pr < 0
        ok = np.where(isroot, True, same | comp)
        if not bool(ok.all()):
            i = a + int(np.flatnonzero(~ok)[0])
            raise SystemExit(f"mutation identity fails at row {i}")
        gsgn[a:b] = np.where(comp & ~isroot, 1, 0).astype(np.uint8)
        if (a // CH) % 40 == 0:
            print(f"    voltage identity: {b}/{N} "
                  f"({time.time()-t1:.0f}s)", flush=True)
    gsgn[root_row] = 0
    print(f"  voltage identity holds for all {N} rows "
          f"({time.time()-t1:.0f}s); gsgn=1 on {int(gsgn.sum())}",
          flush=True)

    wnpz = os.path.join(outdir, f"witness_{r}_{n}.npz")
    np.savez_compressed(wnpz, parent=parent, flip=flip, sigma=sigma,
                        eps=eps, gsgn=gsgn, depth=depth)
    wsize = os.path.getsize(wnpz)
    wraw = sum(int(x.nbytes) for x in (parent, flip, sigma, eps, gsgn,
                                       depth))
    print(f"  wrote {wnpz}: {wsize/1e6:.1f} MB "
          f"(raw {wraw/1e6:.1f} MB)", flush=True)

    examples = []
    for i in (0, N // 2, N - 1):
        key = (int(key_hi[i]) << 64) | int(key_lo[i])
        examples.append({'row': int(i), 'key_hi': int(key_hi[i]),
                         'key_lo': int(key_lo[i]),
                         'sign_string': key_string(key, M),
                         'stab': int(stab[i])})

    man = {
        "artifact": f"omgamma coverage certificate ({r},{n})",
        "format_version": 2,
        "n": n, "r": r, "M_bases": M,
        "count": int(N),
        "complete": True,
        "mass_total": str(mass),
        "mass_target": str(meta.get('target_mass', mass)),
        "group_order_Gprime": str(Gn),
        "stab_histogram": {str(k): v for k, v in sorted(hist.items())},
        "conventions": {
            "ground_set": "E = {1,...,n}",
            "basis_order":
                "the C(n,r) r-subsets of E in COLEX order: A < B iff "
                "max(A xor B) in B; equivalently sort each ascending "
                "r-tuple by its reversal.  Index j runs 0..M-1.",
            "chirotope":
                "a uniform chirotope chi is evaluated on ascending "
                "r-tuples and takes values in {+1,-1}; it is valid iff "
                "every three-term Grassmann-Pluecker condition holds: for "
                "every (r-2)-subset L and every a<b<c<d disjoint from L, "
                "the three terms chi(L,a,b)chi(L,c,d), "
                "-chi(L,a,c)chi(L,b,d), chi(L,a,d)chi(L,b,c) are not all "
                "equal.",
            "key_encoding":
                "key is a 126-bit unsigned integer with bit (M-1-j) equal "
                "to 1 iff chi(B_j) = +1, B_j the j-th basis in colex "
                "order.  So the most significant bit is basis 0 and "
                "integer order on keys is lexicographic order on the "
                "sign string '+' > '-'.  Stored split as "
                "key = key_hi*2^64 + key_lo.",
            "group":
                "G' = S_n x {0,1}^n x {0,1} acting on the left by "
                "((sig,eps,s).chi)(x_1..x_r) = (-1)^s "
                "(-1)^{|eps cap {x_1..x_r}|} chi(sig^{-1}x_1,..,"
                "sig^{-1}x_r).  |G'| = n! 2^(n+1).  The recorded stab is "
                "the order of the stabilizer of chi in G' (which contains "
                "the 2^kappa elements acting trivially on every "
                "chirotope; here kappa = 1, so the minimum is 2).",
            "canonical_form":
                "IMPORTANT -- the keys are extremal in their orbit under "
                "a COLOUR-RESTRICTED relabelling set, not under all of "
                "S_n.  Precisely: (1) call a basis MUTABLE if flipping "
                "its sign leaves a valid uniform chirotope; (2) set "
                "deg(i) = #mutable bases containing i and m2(i,j) = "
                "#mutable bases containing both i and j; (3) colour the "
                "ground set by col_0(i) = deg(i), then refine at most 3 "
                "times by col_{t+1}(i) = rank of (col_t(i), sorted "
                "multiset over j != i of (m2(i,j), col_t(j))) among the "
                "n composite values, ranks assigned by ascending sort, "
                "stopping early if the number of distinct colours did not "
                "grow (the assignment is kept, then the loop stops); "
                "(4) order the colour classes by (class size ascending, "
                "colour rank ascending) and let them occupy the "
                "positions 1..n in that order; (5) the key is the "
                "MAXIMUM, over all relabellings sending each colour class "
                "onto its designated block of positions and over all of "
                "{0,1}^n x {0,1}, of the resulting key integer.  Because "
                "the colouring is invariant under reorientation and "
                "global negation and equivariant under relabelling, this "
                "is a well-defined function of the G'-orbit, so distinct "
                "keys certify distinct classes.  The unrestricted maximum "
                "over all of S_n would be a cleaner convention but costs "
                "about 1.5 s per class, i.e. some 160 CPU-days here.",
            "stab_semantics":
                "stab[i] = 2^kappa * #{relabellings in the set of step "
                "(5) that attain the maximum} = |Stab_{G'}(chi)|.",
        },
        "sorted": "strictly increasing in the 126-bit key",
        "files": {},
        "legacy_files": {},
        "tree": {
            "file": os.path.basename(tnpz),
            "purpose":
                "THE CERTIFICATE.  The root key together with, per class, "
                "the parent class and the mutated basis.  Everything else "
                "-- the class keys, the stabilizer orders, the depths and "
                "the edge voltages -- is DERIVED from it by "
                "coverage_checker.py, which is why the certificate fits in "
                "the repository while the two arrays below do not.",
            "count": int(N),
            "root_key_hi": int(root_key[0]),
            "root_key_lo": int(root_key[1]),
            "max_depth": maxdepth,
            "row_order":
                "CANONICAL TREE ORDER: row 0 is the root; the rows of depth "
                "d follow those of depth d-1, ordered by (position of "
                "parent, mutated-basis index).  This is defined by "
                "induction on depth, so it is a function of the tree alone. "
                " It makes parent[i] < i and the parent array nondecreasing, "
                "and every prefix of it is closed under `parent`, hence is "
                "itself a complete certificate for a smaller catalog.",
            "arrays": {
                "format": f"0-d unicode array, the string {TREE_FORMAT!r}",
                "params": "int64[3] = [n, r, count]",
                "root_key": "uint64[2] = [hi, lo]; the 126-bit key of row 0 "
                            "under conventions.key_encoding",
                "gap_nbits": "int64[1]; the exact length in bits of the "
                             "parent gap stream",
                "gap_bits": "uint8[ceil(gap_nbits/8)]; the parent gap "
                            "stream packed MSB-first",
                "flip_bits": "uint8[ceil(7*(count-1)/8)]; the mutated-basis "
                             "indices, 7 bits each, MSB-first",
            },
            "decoding":
                "PARENT: unpack gap_bits MSB-first, keep the first "
                "gap_nbits bits (the padding must be zero), and let "
                "p_0 < ... < p_{count-2} be the positions of the one bits "
                "(there must be exactly count-1 of them); then "
                "parent[k+1] = p_k - k.  Equivalently the stream writes, "
                "for each row i = 1..count-1 in order, "
                "parent[i]-parent[i-1] zeros (with parent[0] := 0) followed "
                "by a single one.  FLIP: unpack flip_bits MSB-first, keep "
                "the first 7*(count-1) bits, read them as (count-1) "
                "big-endian 7-bit integers; flip[i] for i = 1..count-1 must "
                "be < M_bases.  Row 0 is the root and has neither.",
            "reconstruction":
                "chi_0 is decoded from root_key.  For i = 1,2,...: "
                "psi_i = mu_{B_flip[i]}(chi_parent[i]) -- flip the sign of "
                "the flip[i]-th basis of the parent chirotope -- which must "
                "be a VALID uniform chirotope, and chi_i is the canonical "
                "representative of the G'-orbit of psi_i under "
                "conventions.canonical_form, with stab[i] the size of that "
                "orbit's stabilizer read off the same maximisation.  "
                "parent[i] < i, so this terminates; the rows of one depth "
                "can be done in parallel.",
            "why_this_is_a_certificate":
                "psi_i valid means flip[i] really is a mutable basis of the "
                "parent, so parent[i] and i are adjacent in the mutation "
                "graph on classes; parent[i] < i with a single parentless "
                "row makes the edges a spanning tree, so all listed classes "
                "lie in ONE component.  The keys are a function of the "
                "G'-orbit, so distinct keys certify distinct classes, and "
                "the orbit masses summing to the target certifies that "
                "there are no others.",
        },
        "array_sha256": {
            "key_hi": sha256_array(key_hi),
            "key_lo": sha256_array(key_lo),
            "stab": sha256_array(stab),
        },
        "tree_array_sha256": {k: sha256_array(v)
                              for k, v in tree_arrays.items()},
        "array_sha256_note":
            "SHA-256 of the raw little-endian C-contiguous buffer of each "
            "array (numpy .tobytes()), so the hashes survive repacking of "
            "the .npz container.  `array_sha256` and `witness_array_sha256` "
            "pin the LEGACY arrays, which are not tracked and are not "
            "needed to check the certificate; `tree_array_sha256` pins the "
            "certificate itself.",
        "witness": {
            "file": os.path.basename(wnpz),
            "purpose":
                "a mutation SPANNING TREE over the same rows: it certifies "
                "REACHABILITY, i.e. that all listed classes lie in ONE "
                "connected component of the mutation graph on classes.  "
                "The coverage array alone certifies the catalog (valid, "
                "pairwise inequivalent, exact stabilizers, right mass); it "
                "says nothing about how the classes are joined to each "
                "other.",
            "indexing":
                "row i of every witness array refers to row i of "
                f"{os.path.basename(npz)}, i.e. to the class with key "
                "key_hi[i]*2^64 + key_lo[i].",
            "arrays": {
                "parent": "int32; the row this class was reached from, "
                          "-1 at the unique root",
                "flip": "uint8; colex index of the mutated basis "
                        "(0..M-1)",
                "sigma": "uint8 (N,n); a permutation of 1..n, "
                         "sigma[i][x-1] = sigma(x)",
                "eps": "uint16; reorientation bitmask, bit (x-1) set iff "
                       "element x is reoriented",
                "gsgn": "uint8; the global sign s in {0,1}",
                "depth": "uint16; distance from row i to the root along "
                         "parent pointers",
            },
            "identity":
                "for every non-root row i, with chi_i the chirotope "
                "decoded from key i, B_j the j-th basis in colex order "
                "and mu_B the sign flip on B, EXACTLY: "
                "(sigma[i], eps[i], gsgn[i]) . chi_i "
                "= mu_{B_flip[i]} ( chi_parent[i] ), the group acting as "
                "recorded under conventions.group.  Equivalently, the "
                "recorded element is the VOLTAGE of the mutation edge "
                "parent[i] -> i.",
            "why_this_certifies_reachability":
                "the identity exhibits mu_{B_flip[i]}(chi_parent[i]) as a "
                "G'-translate of chi_i, hence (i) B_flip[i] really is a "
                "mutable basis of chi_parent[i] -- the mutant is valid "
                "because chi_i is valid and G' preserves validity -- and "
                "(ii) rows parent[i] and i are adjacent in the mutation "
                "graph on G'-classes.  depth[root]=0 with "
                "depth[i]=depth[parent[i]]+1 makes the parent map "
                "strictly depth-decreasing, so it is acyclic and every "
                "row reaches the unique root.  Therefore all "
                f"{N} listed classes lie in one connected component.",
            "root_row": root_row,
            "max_depth": maxdepth,
            "root_sentinels":
                "at the root, parent=-1, flip=0, sigma=identity, eps=0, "
                "gsgn=0, depth=0; the identity is not asserted there.",
        },
        "witness_array_sha256": {
            "parent": sha256_array(parent),
            "flip": sha256_array(flip),
            "sigma": sha256_array(sigma),
            "eps": sha256_array(eps),
            "gsgn": sha256_array(gsgn),
            "depth": sha256_array(depth),
        },
        "examples": examples,
        "provenance": {
            "source": f"{indir}/level_*.npz produced by runbig.py {r} {n}",
            "source_meta": meta,
            "exported_by": "export_coverage.py",
        },
        "how_to_obtain": (
            f"{os.path.basename(tnpz)} ({tsize/1e6:.2f} MB) IS tracked in "
            "git together with this MANIFEST.json, so the certificate can "
            "be checked directly after cloning the repository: `python "
            f"coverage_checker.py --artifact {outdir}`.  The two LEGACY "
            f"arrays {os.path.basename(npz)} ({size/1e6:.1f} MB) and "
            f"{os.path.basename(wnpz)} ({wsize/1e6:.1f} MB) are NOT tracked "
            "(see .gitignore) and are NOT needed: the checker reconstructs "
            "their contents from the certificate.  They exist only so that "
            "`--legacy-crosscheck` can compare the reconstruction against "
            "what the search programs actually recorded; to regenerate "
            f"them run `python runbig.py {r} {n} <workers>` (about 4 h on 4 "
            f"cores; it writes {indir}/level_*.npz) and then `python "
            f"export_coverage.py {r} {n} {indir} {outdir}`.  Every "
            "array_sha256 value is a SHA-256 of a raw array buffer and must "
            "reproduce exactly; the certificate .npz is written STORED with "
            "a fixed timestamp, so its FILE hash reproduces too."),
        "checker": "coverage_checker.py (imports nothing from this project)",
    }
    man['files'][os.path.basename(tnpz)] = {
        "sha256": sha256_file(tnpz), "bytes": tsize}
    man['legacy_files'][os.path.basename(npz)] = {
        "sha256": sha256_file(npz), "bytes": size}
    man['legacy_files'][os.path.basename(wnpz)] = {
        "sha256": sha256_file(wnpz), "bytes": wsize}

    mpath = os.path.join(outdir, "MANIFEST.json")
    with open(mpath, "w") as f:
        json.dump(man, f, indent=1)
    print(f"  wrote {mpath}")
    print(f"done in {time.time()-t0:.0f}s")


if __name__ == "__main__":
    main(int(sys.argv[1]), int(sys.argv[2]), sys.argv[3], sys.argv[4])
