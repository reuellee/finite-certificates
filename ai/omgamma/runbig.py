"""Disk-based, level-synchronous, multiprocess BFS over Gamma_hat(n,r)
with FULL-EDGE holonomy harvesting and mass-formula termination.

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
  * accumulates the exact orbit-stabilizer mass and stops when it equals
    the precomputed target N_chi(n,r): then EVERY isomorphism class has
    been discovered (mass identity) and Gamma_hat is connected.
If the frontier empties with mass < target, Gamma_hat is disconnected or
the pipeline is broken -- loudly fatal either way.

Usage: python runbig.py <r> <n> <workers> [phase1cap] [--phase1-only]
Requires data/mass_target_<r>_<n>.json (except --phase1-only).
State dir: data/big_<r>_<n>/
"""
import json
import os
import sys
import time
from math import comb, factorial
from multiprocessing import Pool

import numpy as np

from core import mutable_bases_np, g_identity
from canon import canonical
from flip import Holonomy, bar_compose, bar_inverse, normalize


def key_to_u64pair(can, M):
    return (can >> 64) & ((1 << 64) - 1), can & ((1 << 64) - 1)


def mask_to_u64pair(mask):
    return (mask >> 64) & ((1 << 64) - 1), mask & ((1 << 64) - 1)


def pack2(a):
    a = np.ascontiguousarray(a, dtype=np.uint64)
    return a.view([('hi', np.uint64), ('lo', np.uint64)]).reshape(-1)


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


def main(r, n, nw, cap=4000, phase1_only=False):
    t00 = time.time()
    M = comb(n, r)
    if phase1_only:
        target = None
    else:
        with open(f"data/mass_target_{r}_{n}.json") as f:
            target = int(json.load(f)['N_chi'])
    Gn = factorial(n) * (1 << (n + 1))
    full_eps = (1 << n) - 1
    outdir = f"data/big_{r}_{n}"
    os.makedirs(outdir, exist_ok=True)
    import glob as _glob
    for stale in _glob.glob(f"{outdir}/level_*.npz"):
        if not stale.endswith("level_000.npz"):
            os.remove(stale)

    hol = Holonomy(n)
    print(f"phase 1: harvesting holonomy (cap {cap})", flush=True)
    classes, reps, tau, tree, unexpanded, nedges = phase1(n, r, cap, hol)
    p_ord, p_full, u_dim, u_full = hol.status()
    print(f"phase 1 done: {len(reps)} classes, {nedges} edges, "
          f"holonomy pi(H) {p_ord}/{p_full}, sign {u_dim}/{u_full}, "
          f"full={hol.full()}  ({time.time()-t00:.0f}s)", flush=True)

    # ---- disk + array state from phase 1
    allkeys = np.zeros((len(reps), 2), dtype=np.uint64)
    for k, cid in classes.items():
        allkeys[cid] = key_to_u64pair(k, M)
    masks = np.array([mask_to_u64pair(m) for m in reps], dtype=np.uint64)
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

    # transports as compact arrays (normalized: s = 0, eps mod all-ones)
    tau_sig = np.array([t[0] for t in tau], dtype=np.uint8)
    tau_eps = np.array([t[1] for t in tau], dtype=np.uint32)

    kp = pack2(allkeys.copy())
    order = np.argsort(kp)
    known = kp[order]
    known_ids = np.arange(len(reps), dtype=np.int64)[order]
    total_mass = 0
    for st in stabs:
        total_mass += Gn // int(st)
    total_classes = len(reps)
    total_edges = nedges

    fr_ids = np.array(unexpanded, dtype=np.int64)
    fr_masks = masks[fr_ids]

    level = 0
    if phase1_only:
        print(f"phase1-only: {len(reps)} classes, mass {total_mass}; "
              "exiting before phase 2", flush=True)
        write_hol_files(outdir, hol, {'harvest_classes': len(reps),
                                      'harvest_edges': nedges,
                                      'phase': 1})
        return

    print(f"target mass {target}; after phase1 mass {total_mass} "
          f"({100*total_mass/target:.2f}%)", flush=True)

    def compose_arrays(psig, peps, tsig, teps):
        """(psig,peps) o (tsig,teps): perm arrays 1-based uint8."""
        csig = psig[tsig - 1]
        e = int(peps)
        te = int(teps)
        for i in range(n):
            if (te >> i) & 1:
                e ^= 1 << (int(psig[i]) - 1)
        e2 = e ^ full_eps
        if e2 < e:
            e = e2
        return csig, e

    harvested_edges = 0
    with Pool(nw, initializer=_winit, initargs=(n, r)) as pool:
        while total_mass < target and len(fr_ids) > 0:
            level += 1
            t0 = time.time()
            chunks = []
            csz = max(200, min(20000, len(fr_ids) // (nw * 6) + 1))
            for i in range(0, len(fr_ids), csz):
                sl = slice(i, i + csz)
                chunks.append((fr_ids[sl], fr_masks[sl, 0],
                               fr_masks[sl, 1]))
            NK, NC, NS, NP, NF, NSG, NE = [], [], [], [], [], [], []
            lvl_edges = 0
            seen_level = {}
            pend_hits = []     # (parent, flip, childid, sig-row, eps)
            for (K, CM, ST, PAR, FL, SG, EP, ne) in \
                    pool.imap_unordered(_wexpand, chunks):
                lvl_edges += ne
                if len(K) == 0:
                    continue
                pk = pack2(K)
                pos = np.searchsorted(known, pk)
                pos = np.clip(pos, 0, len(known) - 1)
                isold = known[pos] == pk
                # holonomy from edges to already-known classes: harvest
                # INLINE (tau of both endpoints already known)
                if not hol.full():
                    oldidx = np.flatnonzero(isold)
                    cids = known_ids[pos[oldidx]]
                    for t2, cid2 in zip(oldidx, cids):
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
                fresh = ~isold
                if fresh.any():
                    idxf = np.flatnonzero(fresh)
                    kb = K[idxf]
                    keep = []
                    for t2 in range(len(idxf)):
                        bkey = kb[t2].tobytes()
                        if bkey not in seen_level:
                            seen_level[bkey] = None
                            keep.append(idxf[t2])
                        elif not hol.full() and len(pend_hits) < 500000:
                            # duplicate within level: also a holonomy edge
                            pend_hits.append(
                                ('L', int(PAR[idxf[t2]]),
                                 int(FL[idxf[t2]]), kb[t2].tobytes(),
                                 SG[idxf[t2]].copy(),
                                 int(EP[idxf[t2]])))
                    if keep:
                        keep = np.array(keep, dtype=np.int64)
                        NK.append(K[keep])
                        NC.append(CM[keep])
                        NS.append(ST[keep])
                        NP.append(PAR[keep])
                        NF.append(FL[keep])
                        NSG.append(SG[keep])
                        NE.append(EP[keep])
            total_edges += lvl_edges

            nnew = 0
            if NK:
                K = np.concatenate(NK)
                CM = np.concatenate(NC)
                ST = np.concatenate(NS)
                PAR = np.concatenate(NP)
                FL = np.concatenate(NF)
                SG = np.concatenate(NSG)
                EP = np.concatenate(NE)
                nnew = len(K)
                ids = np.arange(total_classes, total_classes + nnew,
                                dtype=np.int64)
                np.savez_compressed(f"{outdir}/level_{level:03d}.npz",
                                    keys=K, masks=CM, stab=ST, parent=PAR,
                                    flip=FL, sigma=SG, eps=EP, ids=ids)
                # extend transports: tau_child = tau_parent o t
                newsig = np.zeros((nnew, n), dtype=np.uint8)
                neweps = np.zeros(nnew, dtype=np.uint32)
                for t2 in range(nnew):
                    cs, ce = compose_arrays(tau_sig[PAR[t2]],
                                            tau_eps[PAR[t2]],
                                            SG[t2], EP[t2])
                    newsig[t2] = cs
                    neweps[t2] = ce
                tau_sig = np.concatenate([tau_sig, newsig])
                tau_eps = np.concatenate([tau_eps, neweps])
                # id lookup for in-level keys
                pkn = pack2(K)
                for t2 in range(nnew):
                    seen_level[pkn[t2].tobytes()] = int(ids[t2])
                total_classes += nnew
                for st in ST:
                    total_mass += Gn // int(st)
                allk = np.concatenate([known, pkn])
                alli = np.concatenate([known_ids, ids])
                o2 = np.argsort(allk)
                known = allk[o2]
                known_ids = alli[o2]
                fr_ids = ids
                fr_masks = CM.astype(np.uint64)
            else:
                fr_ids = np.array([], dtype=np.int64)
                fr_masks = np.zeros((0, 2), dtype=np.uint64)

            # process holonomy hits now that in-level ids are assigned
            if pend_hits and not hol.full():
                for rec in pend_hits:
                    if hol.full():
                        break
                    if rec[0] == 'L':
                        _, pid, fl, bkey, sgrow, ep = rec
                        cid2 = seen_level.get(bkey)
                        if cid2 is None:
                            continue
                    else:
                        pid, fl, cid2, sgrow, ep = rec
                    tsig = tuple(int(x) for x in sgrow)
                    tvol = (tsig, int(ep), 0)
                    taup = (tuple(int(x) for x in tau_sig[pid]),
                            int(tau_eps[pid]), 0)
                    tauc = (tuple(int(x) for x in tau_sig[cid2]),
                            int(tau_eps[cid2]), 0)
                    h = bar_compose(n, bar_compose(n, taup, tvol),
                                    bar_inverse(n, tauc))
                    hol.add(h, prov=('edge', pid, fl, int(cid2)))
                    harvested_edges += 1
            pend_hits = None

            pct = 100 * total_mass / target
            p_ord = hol.P.order()
            print(f"level {level}: +{nnew} classes "
                  f"(total {total_classes}), {lvl_edges} edges "
                  f"({total_edges} total), mass {pct:.4f}%, "
                  f"hol {p_ord}/{factorial(n)}|{hol.U.dim()}/{n}"
                  f"{' FULL' if hol.full() else ''}, "
                  f"{time.time()-t0:.0f}s", flush=True)
            with open(f"{outdir}/meta.json", "w") as f:
                json.dump({'level': level,
                           'total_classes': total_classes,
                           'total_edges_expanded': total_edges,
                           'total_mass': str(total_mass),
                           'target_mass': str(target),
                           'complete': total_mass == target},
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

    # finalize holonomy exactly
    try:
        hol.saturate(limit=200_000_000)
        exact = True
    except RuntimeError:
        hol.close(rounds=4000)
        exact = False
    p_ord, p_full, u_dim, u_full = hol.status()
    print(f"final holonomy: pi(H) {p_ord}/{p_full}, sign {u_dim}/{u_full}"
          f", exact={exact}, harvested_edge_gens={harvested_edges}",
          flush=True)
    write_hol_files(outdir, hol, {'phase': 2, 'exact_sign': exact,
                                  'harvested_edges': harvested_edges})

    summary = {
        'n': n, 'r': r, 'classes': total_classes,
        'complete_by_mass': done,
        'gamma_hat_connected': done,
        'H_equals_Gbar': hol.full(),
        'gamma_bar_connected': done and hol.full(),
        'gamma_tilde_connected': done and p_ord == p_full,
        'edges_expanded': total_edges,
        'seconds': time.time() - t00,
    }
    with open(f"{outdir}/summary.json", "w") as f:
        json.dump(summary, f, indent=1)
    print(json.dumps(summary, indent=1))


if __name__ == "__main__":
    r = int(sys.argv[1])
    n = int(sys.argv[2])
    nw = int(sys.argv[3])
    cap = int(sys.argv[4]) if len(sys.argv) > 4 else 4000
    p1 = len(sys.argv) > 5 and sys.argv[5] == "--phase1-only"
    main(r, n, nw, cap, phase1_only=p1)
