"""Rebuild the full runbig.py BFS state from the level_*.npz checkpoints.

Used by  runbig.py --resume  and by the standalone holonomy passes.

What is rebuilt, and from what:
  keys / masks / stab / parent / flip / sigma / eps : read verbatim
  ids                                : implicit (contiguous, verified)
  tau (transports)                   : RECOMPUTED by walking the saved
                                       spanning tree from the root
                                       (tau_c = tau_parent o t), never
                                       read from disk -- nothing else is
                                       trustworthy
  total_mass, total_classes          : recomputed and gated against
                                       meta.json (abort on mismatch)
  frontier                           : the classes discovered at the last
                                       completed level

Everything is exact integer arithmetic; the vectorized composition is the
same formula as core.g_compose (checked against it in selftest()).
"""
import glob
import json
import os
from math import comb, factorial

import numpy as np


def compose_rows(n, psig, peps, tsig, teps, full_eps):
    """Vectorized  (psig,peps) o (tsig,teps)  in Gbar (s = 0, eps mod 1^n).

    psig/tsig: (m,n) uint8 1-based perms; peps/teps: (m,) integer masks.
    Mirrors core.g_compose: sigma = psig o tsig, eps = peps XOR psig(teps).
    """
    newsig = np.take_along_axis(psig, (tsig.astype(np.intp) - 1), axis=1)
    m = len(psig)
    bits = ((teps.astype(np.uint32)[:, None] >>
             np.arange(n, dtype=np.uint32)[None, :]) & 1).astype(bool)
    shifted = (np.uint32(1) << (psig.astype(np.uint32) - 1))
    contrib = np.where(bits, shifted, np.uint32(0))
    e = peps.astype(np.uint32) ^ np.bitwise_xor.reduce(contrib, axis=1)
    e2 = e ^ np.uint32(full_eps)
    e = np.minimum(e, e2)
    assert len(e) == m
    return newsig.astype(np.uint8), e


def selftest_compose(n=9, trials=200, seed=1):
    """compose_rows must agree with core.g_compose + flip.normalize."""
    from core import g_compose
    from flip import normalize
    rng = np.random.default_rng(seed)
    full = (1 << n) - 1
    ps = np.zeros((trials, n), dtype=np.uint8)
    ts = np.zeros((trials, n), dtype=np.uint8)
    pe = np.zeros(trials, dtype=np.uint32)
    te = np.zeros(trials, dtype=np.uint32)
    for i in range(trials):
        ps[i] = rng.permutation(n) + 1
        ts[i] = rng.permutation(n) + 1
        pe[i] = min(int(rng.integers(0, 1 << n)),
                    int(rng.integers(0, 1 << n)) ^ full)
        te[i] = int(rng.integers(0, 1 << n))
    cs, ce = compose_rows(n, ps, pe, ts, te, full)
    for i in range(trials):
        g = normalize(n, g_compose(n,
                                   (tuple(int(x) for x in ps[i]),
                                    int(pe[i]), 0),
                                   (tuple(int(x) for x in ts[i]),
                                    int(te[i]), 0)))
        assert tuple(int(x) for x in cs[i]) == g[0], (i, cs[i], g)
        assert int(ce[i]) == g[1], (i, ce[i], g)
    return True


def load_state(r, n, outdir, meta_gate=True, verbose=True):
    """Returns a dict with the rebuilt BFS state.  Raises on any mismatch."""
    files = sorted(glob.glob(f"{outdir}/level_*.npz"))
    if not files:
        raise RuntimeError(f"no level files in {outdir}")
    levels = [int(os.path.basename(p)[6:9]) for p in files]
    if levels != list(range(len(files))):
        raise RuntimeError(f"level files not contiguous: {levels}")
    with open(f"{outdir}/meta.json") as f:
        meta = json.load(f)
    if meta_gate and meta['level'] != levels[-1]:
        raise RuntimeError(
            f"meta.json level {meta['level']} != last level file "
            f"{levels[-1]} — checkpoint torn; delete the trailing level "
            f"file or fix meta before resuming")

    Gn = factorial(n) * (1 << (n + 1))
    full_eps = (1 << n) - 1

    K, MK, ST, PA, FL, SG, EP = [], [], [], [], [], [], []
    off = 0
    lvl_bounds = []
    for lv, path in zip(levels, files):
        z = np.load(path)
        m = len(z['keys'])
        if lv > 0:
            ids = z['ids']
            if not np.array_equal(ids,
                                  np.arange(off, off + m, dtype=ids.dtype)):
                raise RuntimeError(f"level {lv}: ids not contiguous "
                                   f"from {off}")
        K.append(z['keys'])
        MK.append(z['masks'])
        ST.append(z['stab'])
        PA.append(z['parent'])
        FL.append(z['flip'])
        SG.append(z['sigma'])
        EP.append(z['eps'])
        lvl_bounds.append((off, off + m))
        off += m
        if verbose:
            print(f"  [resume] level {lv:3d}: +{m} (total {off})",
                  flush=True)
    keys = np.concatenate(K)
    masks = np.concatenate(MK)
    stab = np.concatenate(ST)
    parent = np.concatenate(PA)
    flip = np.concatenate(FL)
    sigma = np.concatenate(SG)
    eps = np.concatenate(EP)
    del K, MK, ST, PA, FL, SG, EP
    total_classes = len(keys)

    # mass (exact, python ints)
    uniq, cnt = np.unique(stab, return_counts=True)
    total_mass = 0
    for s, c in zip(uniq.tolist(), cnt.tolist()):
        total_mass += (Gn // int(s)) * int(c)

    if meta_gate:
        if total_classes != int(meta['total_classes']):
            raise RuntimeError(
                f"class count {total_classes} != meta "
                f"{meta['total_classes']}")
        if total_mass != int(meta['total_mass']):
            raise RuntimeError(
                f"recomputed mass {total_mass} != meta {meta['total_mass']}")

    # transports: walk the saved spanning tree from the root
    tau_sig = np.zeros((total_classes, n), dtype=np.uint8)
    tau_eps = np.zeros(total_classes, dtype=np.uint32)
    tau_sig[0] = np.arange(1, n + 1, dtype=np.uint8)
    tau_eps[0] = 0
    if lvl_bounds[0][1] > 1:
        # phase-1 classes: parents are inside level 0 and are always
        # smaller ids (BFS order), so a sequential sweep is required
        for c in range(1, lvl_bounds[0][1]):
            p = int(parent[c])
            assert 0 <= p < c, (c, p)
            cs, ce = compose_rows(n, tau_sig[p:p + 1], tau_eps[p:p + 1],
                                  sigma[c:c + 1], eps[c:c + 1], full_eps)
            tau_sig[c] = cs[0]
            tau_eps[c] = ce[0]
    for (a, b) in lvl_bounds[1:]:
        par = parent[a:b]
        if par.min() < 0 or par.max() >= a:
            raise RuntimeError("parent pointer outside earlier levels")
        cs, ce = compose_rows(n, tau_sig[par], tau_eps[par],
                              sigma[a:b], eps[a:b], full_eps)
        tau_sig[a:b] = cs
        tau_eps[a:b] = ce

    # sorted key index
    kp = keys.view([('hi', np.uint64), ('lo', np.uint64)]).reshape(-1)
    order = np.argsort(kp, kind='stable')
    known = kp[order].copy()
    known_ids = np.arange(total_classes, dtype=np.int64)[order]
    del order
    if len(np.unique(known)) != total_classes:
        raise RuntimeError("duplicate canonical keys in the level files")

    a, b = lvl_bounds[-1]
    state = {
        'n': n, 'r': r, 'meta': meta,
        'keys': keys, 'masks': masks, 'stab': stab, 'parent': parent,
        'flip': flip, 'sigma': sigma, 'eps': eps,
        'tau_sig': tau_sig, 'tau_eps': tau_eps,
        'known': known, 'known_ids': known_ids,
        'total_classes': total_classes, 'total_mass': total_mass,
        'total_edges': int(meta.get('total_edges_expanded', 0)),
        'level': levels[-1], 'lvl_bounds': lvl_bounds,
        'frontier_ids': np.arange(a, b, dtype=np.int64),
        'frontier_masks': masks[a:b],
    }
    if verbose:
        print(f"  [resume] rebuilt {total_classes} classes, mass "
              f"{total_mass} (gate OK), frontier {b-a} at level "
              f"{levels[-1]}", flush=True)
    return state


def verify_sample(state, nsample=200, seed=12345, verbose=True):
    """Spot-check the rebuilt state against a fresh canonicalization:
    for random classes, re-canonicalize the stored mask (key + stabilizer
    order must match) and re-verify the tree mutation identity
    rep[parent] ^ bit_j  ==  t . rep[child]  (as pairs)."""
    from canon import canonical
    from core import g_apply
    n, r = state['n'], state['r']
    M = comb(n, r)
    rng = np.random.default_rng(seed)
    N = state['total_classes']
    idx = rng.choice(N, size=min(nsample, N), replace=False)
    bad = 0
    for c in idx.tolist():
        mv = (int(state['masks'][c, 0]) << 64) | int(state['masks'][c, 1])
        res = canonical(n, r, mv, want_witness=False)
        kv = (int(state['keys'][c, 0]) << 64) | int(state['keys'][c, 1])
        if res['can'] != kv:
            print(f"  !! class {c}: canonical key mismatch")
            bad += 1
            continue
        if res['canmask'] != mv:
            print(f"  !! class {c}: stored mask is not canonical")
            bad += 1
        if res['stab_order_exact'] != int(state['stab'][c]):
            print(f"  !! class {c}: stabilizer order mismatch")
            bad += 1
        p = int(state['parent'][c])
        if p < 0:
            continue
        pv = (int(state['masks'][p, 0]) << 64) | int(state['masks'][p, 1])
        psi = pv ^ (1 << int(state['flip'][c]))
        t = (tuple(int(x) for x in state['sigma'][c]),
             int(state['eps'][c]), 0)
        img = g_apply(n, r, t, mv)
        if img != psi and (img ^ ((1 << M) - 1)) != psi:
            print(f"  !! class {c}: tree mutation identity fails")
            bad += 1
    if verbose:
        print(f"  [resume] sample check: {len(idx)} classes, "
              f"{bad} failures", flush=True)
    if bad:
        raise RuntimeError("resume sample verification FAILED")
    return len(idx)


if __name__ == "__main__":
    import sys
    selftest_compose()
    print("compose_rows selftest OK")
    if len(sys.argv) > 2:
        r, n = int(sys.argv[1]), int(sys.argv[2])
        st = load_state(r, n, f"data/big_{r}_{n}")
        verify_sample(st, nsample=int(sys.argv[3])
                      if len(sys.argv) > 3 else 200)
