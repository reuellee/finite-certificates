"""Export the (r,n) coverage artifact: every canonical class key + |Stab|.

Reads the level_*.npz checkpoints of a completed runbig.py campaign and emits

    <out>/coverage_<r>_<n>.npz      key_hi, key_lo (uint64), stab (uint8)
    <out>/MANIFEST.json             conventions, counts, mass, SHA-256s

sorted strictly increasingly by the 126-bit key, so that a third party can
verify distinctness, validity, canonicity and the stabilizer orders with
`coverage_checker.py` (which shares no code with any generator) or with
numpy alone.

This script is generator-side: it only *transports* data that runbig.py
produced.  Nothing here is a check; the checking is coverage_checker.py's
job.

Usage:  python export_coverage.py 4 9 data/big_4_9 data/coverage_4_9
"""
import glob
import hashlib
import json
import os
import sys
import time
from math import comb, factorial

import numpy as np


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
    from itertools import combinations
    return sorted(combinations(range(1, n + 1), r),
                  key=lambda t: tuple(reversed(t)))


def key_string(key, M):
    return ''.join('+' if (key >> (M - 1 - j)) & 1 else '-'
                   for j in range(M))


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

    KH, KL, ST = [], [], []
    for p in files:
        z = np.load(p)
        k = z['keys']
        KH.append(np.ascontiguousarray(k[:, 0]))
        KL.append(np.ascontiguousarray(k[:, 1]))
        s = z['stab']
        if s.max() > 255:
            raise SystemExit("stabilizer order exceeds uint8")
        ST.append(s.astype(np.uint8))
        print(f"  read {os.path.basename(p)}: {len(k)}", flush=True)
    key_hi = np.concatenate(KH)
    key_lo = np.concatenate(KL)
    stab = np.concatenate(ST)
    del KH, KL, ST
    N = len(key_hi)
    print(f"  {N} rows, {time.time()-t0:.0f}s", flush=True)

    if N != int(meta['total_classes']):
        raise SystemExit(f"row count {N} != meta {meta['total_classes']}")

    order = np.lexsort((key_lo, key_hi))
    key_hi = key_hi[order]
    key_lo = key_lo[order]
    stab = stab[order]
    del order

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

    examples = []
    for i in (0, N // 2, N - 1):
        key = (int(key_hi[i]) << 64) | int(key_lo[i])
        examples.append({'row': int(i), 'key_hi': int(key_hi[i]),
                         'key_lo': int(key_lo[i]),
                         'sign_string': key_string(key, M),
                         'stab': int(stab[i])})

    man = {
        "artifact": f"omgamma coverage certificate ({r},{n})",
        "format_version": 1,
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
        "array_sha256": {
            "key_hi": sha256_array(key_hi),
            "key_lo": sha256_array(key_lo),
            "stab": sha256_array(stab),
        },
        "array_sha256_note":
            "SHA-256 of the raw little-endian C-contiguous buffer of each "
            "array (numpy .tobytes()), so the hashes survive repacking of "
            "the .npz container.",
        "examples": examples,
        "provenance": {
            "source": f"{indir}/level_*.npz produced by runbig.py {r} {n}",
            "source_meta": meta,
            "exported_by": "export_coverage.py",
        },
        "how_to_obtain": (
            f"{os.path.basename(npz)} is {size/1e6:.1f} MB and is NOT "
            "tracked in git (see .gitignore); this MANIFEST.json is.  Two "
            "ways to get it.  (1) Regenerate: run "
            f"`python runbig.py {r} {n} <workers>` (about 4 h on 4 cores; "
            f"it writes {indir}/level_*.npz), then "
            f"`python export_coverage.py {r} {n} {indir} {outdir}`.  The "
            "array_sha256 values below pin the result: they are SHA-256 "
            "of the raw array buffers, so they must reproduce exactly, "
            "whereas the .npz file hash need not (savez_compressed "
            "records zip timestamps).  (2) Download the archived release "
            "attached to the repository and check it against the "
            "array_sha256 values below."),
        "checker": "coverage_checker.py (imports nothing from this project)",
    }
    man['files'][os.path.basename(npz)] = {
        "sha256": sha256_file(npz), "bytes": size}

    mpath = os.path.join(outdir, "MANIFEST.json")
    with open(mpath, "w") as f:
        json.dump(man, f, indent=1)
    print(f"  wrote {mpath}")
    print(f"done in {time.time()-t0:.0f}s")


if __name__ == "__main__":
    main(int(sys.argv[1]), int(sys.argv[2]), sys.argv[3], sys.argv[4])
