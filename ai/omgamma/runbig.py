"""Disk-based, level-synchronous, multiprocess BFS over Gamma_hat(n,r)
with FULL-EDGE + FULL-STABILIZER holonomy harvesting and mass-formula
termination.

Phase 1 (in-master): BFS with voltage/stabilizer harvesting up to a class
cap (early diagnostics; the root's stabilizer is always captured).
Phase 2 (parallel workers, master merge): level-synchronous expansion.
Workers canonicalize every mutation of every frontier class and return
per-edge records (key, canonical mask, stab order, parent, flip, voltage).
The master:
  * assigns ids to fresh classes, extends the spanning tree and the
    compact transport arrays (tau);
  * for edges hitting known classes, harvests the holonomy element
    tau_p * t * tau_c'^{-1} into H (until H = Gbar, after which
    harvesting short-circuits);
  * for every fresh class with a NONTRIVIAL Gbar-stabilizer (flagged by
    stab_order_exact > 2^kappa) re-canonicalizes the representative in
    the master and harvests tau_c u tau_c^{-1} for its stabilizer
    generators -- Lemma 2 needs BOTH families (ERRATUM 2026-07-31: the
    original phase 2 harvested only the edge family, which made the
    harvested H a strict lower bound and produced a spuriously trivial
    sign part at (9,4); see OMGAMMA.md Sec. 8);
  * accumulates the exact orbit-stabilizer mass and stops when it equals
    the precomputed target N_chi(n,r): then EVERY isomorphism class has
    been discovered (mass identity) and Gamma_hat is connected.
If the frontier empties with mass < target, Gamma_hat is disconnected or
the pipeline is broken -- loudly fatal either way.

--resume rebuilds the state from data/big_<r>_<n>/level_*.npz (see
bigstate.py), gates it against meta.json, backfills the stabilizer
generators of every already-known class, and continues from the last
completed level.  The EDGE generators of the earlier levels are not on
disk, so a resumed run's H is a lower bound: sound for a POSITIVE verdict
(H full => connected) but NOT for a negative one.  For a negative verdict
run --holopass first (re-expands earlier levels for harvesting only).

Usage:
  python runbig.py <r> <n> <workers> [phase1cap] [--phase1-only]
  python runbig.py <r> <n> <workers> --resume
  python runbig.py <r> <n> <workers> --holopass <lo> <hi>
State dir: data/big_<r>_<n>/
"""
import gc
import json
import os
import sys
import time
from collections import deque
from math import comb, factorial
from multiprocessing import Pool

import numpy as np

from core import mutable_bases_np, g_identity
from canon import canonical, _sign_kernel
from flip import Holonomy, bar_compose, bar_inverse, normalize
from bigstate import load_state, verify_sample, compose_rows

MAX_CHUNK_CLASSES = 2000       # bounds worker + IPC memory
PEND_CAP = 200_000             # bounded in-level holonomy buffer


def key_to_u64pair(can, M):
    return (can >> 64) & ((1 << 64) - 1), can & ((1 << 64) - 1)


def mask_to_u64pair(mask):
    return (mask >> 64) & ((1 << 64) - 1), mask & ((1 << 64) - 1)


def pack2(a):
    a = np.ascontiguousarray(a, dtype=np.uint64)
    return a.view([('hi', np.uint64), ('lo', np.uint64)]).reshape(-1)


def merge_sorted(a, b):
    """Merge two sorted, mutually DISJOINT packed-key arrays in O(|a|+|b|)
    (no re-sort of the big array; keeps peak memory at one extra copy)."""
    if len(a) == 0:
        return b.copy()
    if len(b) == 0:
        return a
    pos = np.searchsorted(a, b)
    tot = len(a) + len(b)
    out = np.empty(tot, dtype=a.dtype)
    dst = pos + np.arange(len(b), dtype=np.int64)
    out[dst] = b
    m = np.ones(tot, dtype=bool)
    m[dst] = False
    out[m] = a
    return out


def is_member(sorted_keys, pk):
    """Bool mask: which entries of pk occur in the sorted array."""
    if len(sorted_keys) == 0:
        return np.zeros(len(pk), dtype=bool)
    pos = np.searchsorted(sorted_keys, pk)
    np.clip(pos, 0, len(sorted_keys) - 1, out=pos)
    return sorted_keys[pos] == pk


# ---------------------------------------------------------------- worker

_W = {}


def _winit(n, r):
    _W['n'] = n
    _W['r'] = r
    from core import gp3_conditions, _np_tables
    gp3_conditions(n, r)
    _np_tables(n, r)


def _wexpand(args):
    n, r = _W['n'], _W['r']
    ids, mhi, mlo = args
    K = []
    CM = []
    ST = []
    PAR = []
    FLIP = []
    SIG = []
    EPS = []
    nedges = 0
    for t in range(len(ids)):
        chi = (int(mhi[t]) << 64) | int(mlo[t])
        cid = int(ids[t])
        for j in mutable_bases_np(n, r, chi):
            psi = chi ^ (1 << j)
            res = canonical(n, r, psi, want_witness=True)
            tvol = bar_inverse(n, res['g'])
            K.append(key_to_u64pair(res['can'], comb(n, r)))
            CM.append(mask_to_u64pair(res['canmask']))
            ST.append(res['stab_order_exact'])
            PAR.append(cid)
            FLIP.append(j)
            SIG.append(tvol[0])
            EPS.append(tvol[1])
            nedges += 1
    return (np.array(K, dtype=np.uint64).reshape(-1, 2),
            np.array(CM, dtype=np.uint64).reshape(-1, 2),
            np.array(ST, dtype=np.uint32),
            np.array(PAR, dtype=np.int64),
            np.array(FLIP, dtype=np.uint8),
            np.array(SIG, dtype=np.uint8).reshape(-1, _W['n']),
            np.array(EPS, dtype=np.uint16),
            nedges)


# ---------------------------------------------------------------- phase 1

def phase1(n, r, cap, hol):
    start = (1 << comb(n, r)) - 1
    res0 = canonical(n, r, start)
    classes = {res0['can']: 0}
    reps = [res0['canmask']]
    tau = [normalize(n, g_identity(n))]
    tree = [None]
    for u in res0['stab']:
        hol.add(bar_compose(n, bar_compose(n, tau[0], u),
                            bar_inverse(n, tau[0])), prov=('stab', 0))
    queue = [0]
    qi = 0
    nedges = 0
    while qi < len(queue) and len(reps) < cap and not hol.full():
        c = queue[qi]
        qi += 1
        chi = reps[c]
        for j in mutable_bases_np(n, r, chi):
            psi = chi ^ (1 << j)
            resm = canonical(n, r, psi)
            kk = resm['can']
            t = bar_inverse(n, resm['g'])
            nedges += 1
            if kk not in classes:
                cid = len(reps)
                classes[kk] = cid
                reps.append(resm['canmask'])
                tau.append(bar_compose(n, tau[c], t))
                tree.append((c, j, t))
                queue.append(cid)
                for u in resm['stab']:
                    hol.add(bar_compose(n, bar_compose(n, tau[cid], u),
                                        bar_inverse(n, tau[cid])),
                            prov=('stab', cid))
            else:
                c2 = classes[kk]
                h = bar_compose(n, bar_compose(n, tau[c], t),
                                bar_inverse(n, tau[c2]))
                hol.add(h, prov=('edge', c, j, c2))
    return classes, reps, tau, tree, queue[qi:], nedges


# ---------------------------------------------------------------- main

def write_hol_files(outdir, hol, extra):
    p_ord, p_full, u_dim, u_full = hol.status()
    info = {'perm_order': p_ord, 'S_n': p_full,
            'sign_dim': u_dim, 'n': u_full,
            'H_equals_Gbar': hol.full()}
    info.update(extra)
    with open(f"{outdir}/holonomy.json", "w") as f:
        json.dump(info, f, indent=1)
    with open(f"{outdir}/gens.txt", "w") as f:
        for prov, g, _grew in hol.elems:
            sig, eps, s = g
            f.write(f"{'|'.join(map(str, prov))} "
                    f"{','.join(map(str, sig))} {eps} {s}\n")
    try:
        ex, exdim = hol.sign_exhibits()
        with open(f"{outdir}/exhibits.txt", "w") as f:
            for w, v in ex:
                f.write(f"{v} {','.join(map(str, w))}\n")
        print(f"sign exhibits written (dim {exdim})", flush=True)
    except Exception as e:
        print("exhibit generation failed:", e, flush=True)


def harvest_stab(n, r, hol, local, gids, masks, keys, stab, tau_sig,
                 tau_eps, trivial):
    """Lemma 2 family (i): tau_c u tau_c^{-1} for u in Stab_Gbar(chi_c).

    `local` indexes the arrays (masks/keys/stab/tau_*), `gids` gives the
    matching GLOBAL class ids used in the certificate provenance.
    Only classes with stab_order_exact > trivial can contribute (their
    Gbar-stabilizer is nontrivial); for those the master re-canonicalizes
    the stored representative -- which also re-verifies its key and its
    stabilizer order, a free integrity check.
    """
    ngen = 0
    ident = tuple(range(1, n + 1))
    for li, gi in zip(np.asarray(local).tolist(),
                      np.asarray(gids).tolist()):
        mv = (int(masks[li, 0]) << 64) | int(masks[li, 1])
        res = canonical(n, r, mv, want_witness=True)
        kv = (int(keys[li, 0]) << 64) | int(keys[li, 1])
        if res['can'] != kv or res['stab_order_exact'] != int(stab[li]):
            raise RuntimeError(
                f"class {gi}: stored key/stabilizer disagrees with a fresh "
                f"canonicalization — state is corrupt")
        tau = (tuple(int(x) for x in tau_sig[li]), int(tau_eps[li]), 0)
        taui = bar_inverse(n, tau)
        for u in res['stab']:
            h = bar_compose(n, bar_compose(n, tau, u), taui)
            if h[0] == ident and h[1] == 0:
                continue
            hol.add(h, prov=('stab', int(gi)))
            ngen += 1
    return ngen


def try_saturate(hol, limit=60_000_000):
    """Run the EXACT staged Schreier completion of the sign part early.

    Sound at any time: saturate() only adds elements that provably lie in
    <harvested> (Schreier generators over a transversal + the P-orbit
    closure of pure-sign elements, both of which are conjugates/products
    of harvested elements).  Running it per level lets H reach Gbar as
    soon as it mathematically has, after which ALL harvesting -- the
    per-edge Python loop, the pending buffer and the tau bookkeeping --
    short-circuits.  Without it the master keeps harvesting millions of
    edges per level whose contribution is already implied.
    """
    t0 = time.time()
    try:
        hol.saturate(limit=limit)
    except RuntimeError:
        return hol.full(), time.time() - t0
    return hol.full(), time.time() - t0


def _submit_window(pool, tasks, pending, window):
    while len(pending) < window:
        try:
            pending.append(pool.apply_async(_wexpand, (next(tasks),)))
        except StopIteration:
            break


def main(r, n, nw, cap=4000, phase1_only=False, resume=False,
         holopass=None):
    t00 = time.time()
    M = comb(n, r)
    kappa = len(_sign_kernel(n, r))
    trivial_stab = 1 << kappa
    if phase1_only:
        target = None
    else:
        with open(f"data/mass_target_{r}_{n}.json") as f:
            target = int(json.load(f)['N_chi'])
    Gn = factorial(n) * (1 << (n + 1))
    full_eps = (1 << n) - 1
    outdir = f"data/big_{r}_{n}"
    os.makedirs(outdir, exist_ok=True)

    hol = Holonomy(n)
    stab_gens = 0
    pend_dropped = 0
    harvested_edges = 0
    resumed_from = None

    if resume or holopass:
        print(f"resuming from {outdir}", flush=True)
        st = load_state(r, n, outdir)
        verify_sample(st, nsample=200)
        resumed_from = st['level']
        keys = st['keys']
        masks = st['masks']
        stabs = st['stab']
        tau_sig = st['tau_sig']
        tau_eps = st['tau_eps']
        known = st['known']
        known_ids = st['known_ids'].astype(np.int64)
        total_mass = st['total_mass']
        total_classes = st['total_classes']
        total_edges = st['total_edges']
        level = st['level']
        fr_ids = st['frontier_ids']
        fr_masks = st['frontier_masks'].copy()
        # backfill Lemma-2 family (i) for every already-known class
        t0 = time.time()
        cids = np.flatnonzero(stabs > trivial_stab)
        stab_gens += harvest_stab(n, r, hol, cids, cids, masks, keys,
                                  stabs, tau_sig, tau_eps, trivial_stab)
        print(f"resume: backfilled {stab_gens} stabilizer generators from "
              f"{len(cids)} classes ({time.time()-t0:.0f}s); "
              f"hol {hol.status()}", flush=True)
        isfull, dt = try_saturate(hol)
        print(f"resume: exact saturation -> hol {hol.status()}, "
              f"full={isfull} ({dt:.0f}s)", flush=True)
        if holopass:
            return holonomy_pass(r, n, nw, holopass, st, hol, outdir,
                                 stab_gens, t00)
        del st['keys'], st['masks'], st['parent'], st['flip']
        del st['sigma'], st['eps'], st['stab'], st
        del keys, masks, stabs
        gc.collect()
    else:
        import glob as _glob
        for stale in _glob.glob(f"{outdir}/level_*.npz"):
            if not stale.endswith("level_000.npz"):
                os.remove(stale)

        print(f"phase 1: harvesting holonomy (cap {cap})", flush=True)
        classes, reps, tau, tree, unexpanded, nedges = phase1(n, r, cap,
                                                              hol)
        p_ord, p_full, u_dim, u_full = hol.status()
        print(f"phase 1 done: {len(reps)} classes, {nedges} edges, "
              f"holonomy pi(H) {p_ord}/{p_full}, sign {u_dim}/{u_full}, "
              f"full={hol.full()}  ({time.time()-t00:.0f}s)", flush=True)

        allkeys = np.zeros((len(reps), 2), dtype=np.uint64)
        for k, cid in classes.items():
            allkeys[cid] = key_to_u64pair(k, M)
        masks = np.array([mask_to_u64pair(m) for m in reps],
                         dtype=np.uint64)
        stabs = np.array([canonical(n, r, m)['stab_order_exact']
                          for m in reps], dtype=np.uint32)
        parent = np.array([-1 if td is None else td[0] for td in tree],
                          dtype=np.int64)
        flips = np.array([0 if td is None else td[1] for td in tree],
                         dtype=np.uint8)
        sigs = np.array([tuple(range(1, n + 1)) if td is None else td[2][0]
                         for td in tree], dtype=np.uint8)
        epss = np.array([0 if td is None else td[2][1] for td in tree],
                        dtype=np.uint16)
        np.savez_compressed(f"{outdir}/level_000.npz", keys=allkeys,
                            masks=masks, stab=stabs, parent=parent,
                            flip=flips, sigma=sigs, eps=epss)

        tau_sig = np.array([t[0] for t in tau], dtype=np.uint8)
        tau_eps = np.array([t[1] for t in tau], dtype=np.uint32)

        kp = pack2(allkeys.copy())
        order = np.argsort(kp, kind='stable')
        known = kp[order]
        known_ids = np.arange(len(reps), dtype=np.int64)[order]
        total_mass = 0
        for stv in stabs:
            total_mass += Gn // int(stv)
        total_classes = len(reps)
        total_edges = nedges
        fr_ids = np.array(unexpanded, dtype=np.int64)
        fr_masks = masks[fr_ids]
        level = 0
        del classes, reps, tau, tree, allkeys, parent, flips, sigs, epss
        gc.collect()

        if phase1_only:
            print(f"phase1-only: {total_classes} classes, mass "
                  f"{total_mass}; exiting before phase 2", flush=True)
            write_hol_files(outdir, hol, {'harvest_classes': total_classes,
                                          'harvest_edges': nedges,
                                          'phase': 1})
            return
        print(f"target mass {target}; after phase1 mass {total_mass} "
              f"({100*total_mass/target:.2f}%)", flush=True)

    if resume:
        print(f"target mass {target}; resumed mass {total_mass} "
              f"({100*total_mass/target:.4f}%) at level {level}, "
              f"frontier {len(fr_ids)}", flush=True)

    session_edges = 0
    ident = tuple(range(1, n + 1))
    with Pool(nw, initializer=_winit, initargs=(n, r)) as pool:
        while total_mass < target and len(fr_ids) > 0:
            level += 1
            t0 = time.time()
            csz = max(200, min(MAX_CHUNK_CLASSES,
                               len(fr_ids) // (nw * 8) + 1))
            nchunks = (len(fr_ids) + csz - 1) // csz

            def _tasks():
                for i in range(0, len(fr_ids), csz):
                    sl = slice(i, i + csz)
                    yield (fr_ids[sl], fr_masks[sl, 0], fr_masks[sl, 1])

            tasks = _tasks()
            pending = deque()
            _submit_window(pool, tasks, pending, nw * 2)

            NK, NC, NS, NP, NF, NSG, NE = [], [], [], [], [], [], []
            lvl_edges = 0
            nnew = 0
            # in-level dedupe: sorted packed keys of the classes already
            # accepted at THIS level (numpy, not a bytes dict).  A small
            # sorted buffer absorbs each chunk; it is merged into the big
            # sorted array only when it grows past LVL_BUF, so the cost is
            # O(level_size) merges instead of one per chunk.
            lvl_sorted = np.zeros(0, dtype=known.dtype)
            lvl_buf = np.zeros(0, dtype=known.dtype)
            LVL_BUF = 65536
            pend = [] if not hol.full() else None   # bounded buffer
            npend = 0

            while pending:
                (K, CM, ST, PAR, FL, SG, EP, ne) = pending.popleft().get()
                _submit_window(pool, tasks, pending, nw * 2)
                lvl_edges += ne
                if len(K) == 0:
                    continue
                pk = pack2(K)
                pos = np.searchsorted(known, pk)
                np.clip(pos, 0, len(known) - 1, out=pos)
                isold = known[pos] == pk
                if not hol.full():
                    oldidx = np.flatnonzero(isold)
                    cids = known_ids[pos[oldidx]]
                    for t2, cid2 in zip(oldidx.tolist(), cids.tolist()):
                        if hol.full():
                            break
                        pid = int(PAR[t2])
                        tvol = (tuple(int(x) for x in SG[t2]),
                                int(EP[t2]), 0)
                        taup = (tuple(int(x) for x in tau_sig[pid]),
                                int(tau_eps[pid]), 0)
                        tauc = (tuple(int(x) for x in tau_sig[cid2]),
                                int(tau_eps[cid2]), 0)
                        h = bar_compose(n, bar_compose(n, taup, tvol),
                                        bar_inverse(n, tauc))
                        hol.add(h, prov=('edge', pid, int(FL[t2]),
                                         int(cid2)))
                        harvested_edges += 1
                idxf = np.flatnonzero(~isold)
                if len(idxf):
                    pkf = pk[idxf]
                    # (a) against classes already accepted at this level
                    dup_lvl = (is_member(lvl_sorted, pkf) |
                               is_member(lvl_buf, pkf))
                    cand = np.flatnonzero(~dup_lvl)
                    # (b) against each other, keeping the FIRST occurrence
                    if len(cand):
                        pc = pkf[cand]
                        srt = np.argsort(pc, kind='stable')
                        ss = pc[srt]
                        firstmask = np.ones(len(ss), dtype=bool)
                        if len(ss) > 1:
                            firstmask[1:] = ss[1:] != ss[:-1]
                        keep_local = np.sort(srt[firstmask])
                        dupmask = np.ones(len(cand), dtype=bool)
                        dupmask[keep_local] = False
                        keep = idxf[cand[keep_local]]
                        dup_here = idxf[cand[dupmask]]
                    else:
                        keep = np.zeros(0, dtype=np.int64)
                        dup_here = np.zeros(0, dtype=np.int64)
                    dup_all = np.concatenate(
                        [idxf[np.flatnonzero(dup_lvl)], dup_here])
                    if pend is not None and len(dup_all):
                        room = PEND_CAP - npend
                        if room <= 0:
                            pend_dropped += len(dup_all)
                        else:
                            take = dup_all[:room]
                            pend_dropped += len(dup_all) - len(take)
                            pend.append((PAR[take].copy(),
                                         FL[take].copy(),
                                         pk[take].copy(),
                                         SG[take].copy(),
                                         EP[take].copy()))
                            npend += len(take)
                    if len(keep):
                        NK.append(K[keep])
                        NC.append(CM[keep])
                        NS.append(ST[keep])
                        NP.append(PAR[keep])
                        NF.append(FL[keep])
                        NSG.append(SG[keep])
                        NE.append(EP[keep])
                        nnew += len(keep)
                        lvl_buf = merge_sorted(lvl_buf, np.sort(pk[keep]))
                        if len(lvl_buf) > LVL_BUF:
                            lvl_sorted = merge_sorted(lvl_sorted, lvl_buf)
                            lvl_buf = np.zeros(0, dtype=known.dtype)
                del K, CM, ST, PAR, FL, SG, EP, pk, pos, isold
            total_edges += lvl_edges
            session_edges += lvl_edges
            del lvl_sorted, lvl_buf

            if NK:
                K = np.concatenate(NK)
                CM = np.concatenate(NC)
                ST = np.concatenate(NS)
                PAR = np.concatenate(NP)
                FL = np.concatenate(NF)
                SG = np.concatenate(NSG)
                EP = np.concatenate(NE)
                del NK, NC, NS, NP, NF, NSG, NE
                ids = np.arange(total_classes, total_classes + nnew,
                                dtype=np.int64)
                np.savez_compressed(f"{outdir}/level_{level:03d}.npz",
                                    keys=K, masks=CM, stab=ST, parent=PAR,
                                    flip=FL, sigma=SG, eps=EP, ids=ids)
                if not hol.full():
                    newsig, neweps = compose_rows(n, tau_sig[PAR],
                                                  tau_eps[PAR], SG, EP,
                                                  full_eps)
                    tau_sig = np.concatenate([tau_sig, newsig])
                    tau_eps = np.concatenate([tau_eps, neweps])
                    del newsig, neweps
                    hs = np.flatnonzero(ST > trivial_stab)
                    if len(hs):
                        stab_gens += harvest_stab(
                            n, r, hol, hs, ids[hs], CM, K, ST,
                            tau_sig[total_classes:],
                            tau_eps[total_classes:], trivial_stab)
                total_classes += nnew
                uq, ct = np.unique(ST, return_counts=True)
                for s2, c2 in zip(uq.tolist(), ct.tolist()):
                    total_mass += (Gn // int(s2)) * int(c2)
                # merge the new block into the known index (O(N), no
                # re-sort of the big array)
                pkn = pack2(K)
                srt = np.argsort(pkn, kind='stable')
                ns = pkn[srt]
                nid = ids[srt]
                posm = np.searchsorted(known, ns)
                tot = len(known) + len(ns)
                newknown = np.empty(tot, dtype=known.dtype)
                newids = np.empty(tot, dtype=np.int64)
                dst = posm + np.arange(len(ns), dtype=np.int64)
                newknown[dst] = ns
                newids[dst] = nid
                keepmask = np.ones(tot, dtype=bool)
                keepmask[dst] = False
                newknown[keepmask] = known
                newids[keepmask] = known_ids
                known = newknown
                known_ids = newids
                del pkn, srt, ns, nid, posm, dst, keepmask, newknown, newids
                fr_ids = ids
                fr_masks = CM.astype(np.uint64)
                del K, CM, ST, PAR, FL, SG, EP
            else:
                fr_ids = np.array([], dtype=np.int64)
                fr_masks = np.zeros((0, 2), dtype=np.uint64)

            # in-level duplicate edges: resolve child ids, then harvest
            if pend and not hol.full():
                for (P_, F_, KK_, SG_, EP_) in pend:
                    if hol.full():
                        break
                    p3 = np.searchsorted(known, KK_)
                    np.clip(p3, 0, len(known) - 1, out=p3)
                    good = known[p3] == KK_
                    cid3 = known_ids[p3]
                    for t2 in np.flatnonzero(good).tolist():
                        if hol.full():
                            break
                        pid = int(P_[t2])
                        tvol = (tuple(int(x) for x in SG_[t2]),
                                int(EP_[t2]), 0)
                        taup = (tuple(int(x) for x in tau_sig[pid]),
                                int(tau_eps[pid]), 0)
                        tauc = (tuple(int(x) for x in tau_sig[int(cid3[t2])]),
                                int(tau_eps[int(cid3[t2])]), 0)
                        h = bar_compose(n, bar_compose(n, taup, tvol),
                                        bar_inverse(n, tauc))
                        hol.add(h, prov=('edge', pid, int(F_[t2]),
                                         int(cid3[t2])))
                        harvested_edges += 1
            pend = None
            gc.collect()
            sat_dt = 0.0
            if not hol.full():
                _isfull, sat_dt = try_saturate(hol)

            pct = 100 * total_mass / target
            p_ord = hol.P.order()
            print(f"level {level}: +{nnew} classes "
                  f"(total {total_classes}), {lvl_edges} edges "
                  f"({total_edges} total), mass {pct:.4f}%, "
                  f"hol {p_ord}/{factorial(n)}|{hol.U.dim()}/{n}"
                  f"{' FULL' if hol.full() else ''}, "
                  f"stabgens {stab_gens}, edgegens {harvested_edges}, "
                  f"penddrop {pend_dropped}, sat {sat_dt:.0f}s, "
                  f"{time.time()-t0:.0f}s", flush=True)
            with open(f"{outdir}/meta.json", "w") as f:
                json.dump({'level': level,
                           'total_classes': total_classes,
                           'total_edges_expanded': total_edges,
                           'total_mass': str(total_mass),
                           'target_mass': str(target),
                           'complete': total_mass == target,
                           'hol_perm_order': p_ord,
                           'hol_sign_dim': hol.U.dim(),
                           'hol_full': hol.full(),
                           'stab_gens': stab_gens,
                           'edge_gens': harvested_edges,
                           'pend_dropped': pend_dropped,
                           'resumed_from_level': resumed_from},
                          f, indent=1)

    done = (total_mass == target)
    print(f"BFS finished: {total_classes} classes, mass "
          f"{'==' if done else '!='} target, "
          f"{time.time()-t00:.0f}s total", flush=True)
    if not done and len(fr_ids) == 0:
        print("!!! frontier empty but mass < target: "
              "Gamma_hat DISCONNECTED or pipeline bug — investigate")
    if total_mass > target:
        print("!!! mass EXCEEDS target: pipeline bug — investigate")

    try:
        hol.saturate(limit=200_000_000)
        exact = True
    except RuntimeError:
        hol.close(rounds=4000)
        exact = False
    p_ord, p_full, u_dim, u_full = hol.status()
    print(f"final holonomy: pi(H) {p_ord}/{p_full}, sign {u_dim}/{u_full}"
          f", exact={exact}, edge_gens={harvested_edges}, "
          f"stab_gens={stab_gens}, pend_dropped={pend_dropped}",
          flush=True)
    write_hol_files(outdir, hol, {'phase': 2, 'exact_sign': exact,
                                  'harvested_edges': harvested_edges,
                                  'stab_gens': stab_gens,
                                  'pend_dropped': pend_dropped,
                                  'resumed_from_level': resumed_from})

    summary = {
        'n': n, 'r': r, 'classes': total_classes,
        'complete_by_mass': done,
        'gamma_hat_connected': done,
        'H_equals_Gbar': hol.full(),
        'gamma_bar_connected': done and hol.full(),
        'gamma_tilde_connected': done and p_ord == p_full,
        'edges_expanded': total_edges,
        'session_edges': session_edges,
        'resumed_from_level': resumed_from,
        'holonomy_is_lower_bound': resumed_from is not None,
        'seconds': time.time() - t00,
    }
    with open(f"{outdir}/summary.json", "w") as f:
        json.dump(summary, f, indent=1)
    print(json.dumps(summary, indent=1))


# ------------------------------------------------------- completing pass

def holonomy_pass(r, n, nw, rng, st, hol, outdir, stab_gens, t00):
    """Re-expand classes [lo,hi) for HOLONOMY HARVESTING ONLY.

    No class discovery: every mutation must land on an already-known key
    (asserted -- which makes this pass a closure certificate for the class
    list on that range as well).  This is what a resumed run needs before
    any DISCONNECTION claim, since the edge generators of the levels
    completed before the resume are not on disk.
    """
    lo, hi = rng
    hi = min(hi, st['total_classes'])
    known = st['known']
    known_ids = st['known_ids'].astype(np.int64)
    tau_sig, tau_eps = st['tau_sig'], st['tau_eps']
    masks = st['masks']
    harvested = 0
    nedges = 0
    unknown = 0
    print(f"holonomy pass over classes [{lo},{hi}) with {nw} workers",
          flush=True)
    csz = max(200, min(MAX_CHUNK_CLASSES, (hi - lo) // (nw * 8) + 1))
    ids_all = np.arange(lo, hi, dtype=np.int64)

    def _tasks():
        for i in range(0, len(ids_all), csz):
            sl = slice(i, i + csz)
            yield (ids_all[sl], masks[lo:hi][sl, 0], masks[lo:hi][sl, 1])

    t0 = time.time()
    with Pool(nw, initializer=_winit, initargs=(n, r)) as pool:
        tasks = _tasks()
        pending = deque()
        _submit_window(pool, tasks, pending, nw * 2)
        done_cls = 0
        while pending:
            (K, CM, ST, PAR, FL, SG, EP, ne) = pending.popleft().get()
            _submit_window(pool, tasks, pending, nw * 2)
            nedges += ne
            if len(K) == 0:
                continue
            pk = pack2(K)
            pos = np.searchsorted(known, pk)
            np.clip(pos, 0, len(known) - 1, out=pos)
            ok = known[pos] == pk
            unknown += int((~ok).sum())
            cid = known_ids[pos]
            for t2 in np.flatnonzero(ok).tolist():
                pid = int(PAR[t2])
                c2 = int(cid[t2])
                tvol = (tuple(int(x) for x in SG[t2]), int(EP[t2]), 0)
                taup = (tuple(int(x) for x in tau_sig[pid]),
                        int(tau_eps[pid]), 0)
                tauc = (tuple(int(x) for x in tau_sig[c2]),
                        int(tau_eps[c2]), 0)
                h = bar_compose(n, bar_compose(n, taup, tvol),
                                bar_inverse(n, tauc))
                hol.add(h, prov=('edge', pid, int(FL[t2]), c2))
                harvested += 1
            done_cls += csz
            if done_cls % (csz * 40) == 0:
                print(f"  holopass {done_cls}/{hi-lo} classes, {nedges} "
                      f"edges, hol {hol.status()}, unknown {unknown}, "
                      f"{time.time()-t0:.0f}s", flush=True)
    try:
        hol.saturate(limit=200_000_000)
        exact = True
    except RuntimeError:
        hol.close(rounds=4000)
        exact = False
    p_ord, p_full, u_dim, u_full = hol.status()
    print(f"holonomy pass done: {nedges} edges, {harvested} generators, "
          f"{unknown} edges to UNKNOWN keys, pi(H) {p_ord}/{p_full}, "
          f"sign {u_dim}/{u_full}, exact={exact}, "
          f"{time.time()-t00:.0f}s", flush=True)
    write_hol_files(outdir, hol,
                    {'phase': 'holopass', 'range': [lo, hi],
                     'edges': nedges, 'generators': harvested,
                     'stab_gens': stab_gens,
                     'edges_to_unknown_keys': unknown,
                     'exact_sign': exact})
    with open(f"{outdir}/holopass_{lo}_{hi}.json", "w") as f:
        json.dump({'lo': lo, 'hi': hi, 'edges': nedges,
                   'generators': harvested,
                   'edges_to_unknown_keys': unknown,
                   'perm_order': p_ord, 'sign_dim': u_dim,
                   'H_equals_Gbar': hol.full(),
                   'closure_certified': unknown == 0}, f, indent=1)


if __name__ == "__main__":
    r = int(sys.argv[1])
    n = int(sys.argv[2])
    nw = int(sys.argv[3])
    args = sys.argv[4:]
    resume = "--resume" in args
    p1 = "--phase1-only" in args
    hp = None
    if "--holopass" in args:
        i = args.index("--holopass")
        hp = (int(args[i + 1]), int(args[i + 2]))
    capv = 4000
    for a in args:
        if not a.startswith("--") and a.isdigit():
            capv = int(a)
            break
    main(r, n, nw, capv, phase1_only=p1, resume=resume, holopass=hp)
