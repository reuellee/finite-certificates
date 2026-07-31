"""Disk-based, level-synchronous, multiprocess BFS over Gamma_hat(n,r)
with early in-memory holonomy harvesting and mass-formula termination.

Phase 1 (in-master, single process): BFS with full voltage/stabilizer
harvesting until either the holonomy saturates to full (H = Gbar) or a
class cap is reached.  Phase 2 (parallel): level-synchronous expansion,
canonical keys only + tree records, until the accumulated mass equals the
target N_chi(n,r) (then every isomorphism class has been discovered and
Gamma_hat is connected), or the frontier empties (then, if mass < target,
Gamma_hat is DISCONNECTED or the pipeline is broken -- both loudly fatal).

Usage: python runbig.py <r> <n> <workers> [phase1cap]
Requires data/mass_target_<r>_<n>.json (from ext_count.py).
State dir: data/big_<r>_<n>/   (restartable per level)
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


# ---------------------------------------------------------------- helpers

def key_to_u64pair(can, M):
    """canonint (M<=128 bits) -> (hi, lo) uint64s."""
    return (can >> 64) & ((1 << 64) - 1), can & ((1 << 64) - 1)


def mask_to_u64pair(mask):
    return (mask >> 64) & ((1 << 64) - 1), mask & ((1 << 64) - 1)


def pack2(a):
    """(m,2) uint64 array -> 1-D void16 view for sort/searchsorted."""
    a = np.ascontiguousarray(a, dtype=np.uint64)
    return a.view([('hi', np.uint64), ('lo', np.uint64)]).reshape(-1)


# ---------------------------------------------------------------- worker

_W = {}


def _winit(n, r):
    _W['n'] = n
    _W['r'] = r
    # warm caches
    from core import gp3_conditions, _np_tables
    gp3_conditions(n, r)
    _np_tables(n, r)


def _wexpand(args):
    """Expand a chunk of classes.  Returns per-edge arrays."""
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
    """In-memory BFS with harvesting until holonomy full or cap classes.
    Returns (classes dict key->id, reps list, tau list, tree list,
    frontier ids not yet expanded, nedges)."""
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

def main(r, n, nw, cap=4000):
    t00 = time.time()
    M = comb(n, r)
    with open(f"data/mass_target_{r}_{n}.json") as f:
        target = int(json.load(f)['N_chi'])
    Gn = factorial(n) * (1 << (n + 1))
    outdir = f"data/big_{r}_{n}"
    os.makedirs(outdir, exist_ok=True)

    hol = Holonomy(n)
    print(f"phase 1: harvesting holonomy (cap {cap})", flush=True)
    classes, reps, tau, tree, unexpanded, nedges = phase1(n, r, cap, hol)
    try:
        hol.saturate(limit=80_000_000)
        hol.exact_lower = True
    except RuntimeError:
        hol.close(rounds=4000)
        hol.exact_lower = False
    p_ord, p_full, u_dim, u_full = hol.status()
    print(f"phase 1 done: {len(reps)} classes, {nedges} edges, "
          f"holonomy pi(H) {p_ord}/{p_full}, sign {u_dim}/{u_full}, "
          f"full={hol.full()}  ({time.time()-t00:.0f}s)", flush=True)
    with open(f"{outdir}/holonomy.json", "w") as f:
        json.dump({'perm_order': p_ord, 'S_n': p_full,
                   'sign_dim': u_dim, 'n': u_full,
                   'H_full_lower_bound_is_exact_subgroup': True,
                   'H_equals_Gbar': hol.full(),
                   'harvest_classes': len(reps),
                   'harvest_edges': nedges}, f, indent=1)
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

    # ---- initialize disk state from phase 1
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
    known = pack2(allkeys.copy())
    order = np.argsort(known)
    known = known[order]
    total_mass = 0
    for st in stabs:
        total_mass += Gn // int(st)
    total_classes = len(reps)
    total_edges = nedges

    # frontier: phase-1 unexpanded + none-expanded ids
    fr_ids = np.array(unexpanded, dtype=np.int64)
    fr_masks = masks[fr_ids]

    level = 0
    print(f"target mass {target}; after phase1 mass {total_mass} "
          f"({100*total_mass/target:.2f}%)", flush=True)

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
            NK = []
            NC = []
            NS = []
            NP = []
            NF = []
            NSG = []
            NE = []
            lvl_edges = 0
            seen_level = set()
            for (K, CM, ST, PAR, FL, SG, EP, ne) in \
                    pool.imap_unordered(_wexpand, chunks):
                lvl_edges += ne
                if len(K) == 0:
                    continue
                pk = pack2(K)
                # filter: not in known
                pos = np.searchsorted(known, pk)
                pos = np.clip(pos, 0, len(known) - 1)
                isold = known[pos] == pk
                fresh = ~isold
                if fresh.any():
                    idxf = np.flatnonzero(fresh)
                    kb = K[idxf]
                    keep = []
                    for t2 in range(len(idxf)):
                        bkey = kb[t2].tobytes()
                        if bkey not in seen_level:
                            seen_level.add(bkey)
                            keep.append(idxf[t2])
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
            if NK:
                K = np.concatenate(NK)
                CM = np.concatenate(NC)
                ST = np.concatenate(NS)
                PAR = np.concatenate(NP)
                FL = np.concatenate(NF)
                SG = np.concatenate(NSG)
                EP = np.concatenate(NE)
                # dedupe across batches (keep first)
                pk = pack2(K)
                order = np.argsort(pk, kind='stable')
                pk_s = pk[order]
                keep_s = np.ones(len(pk_s), dtype=bool)
                keep_s[1:] = pk_s[1:] != pk_s[:-1]
                sel = order[keep_s]
                sel.sort()
                K, CM, ST, PAR, FL, SG, EP = (K[sel], CM[sel], ST[sel],
                                              PAR[sel], FL[sel], SG[sel],
                                              EP[sel])
                ids = np.arange(total_classes, total_classes + len(K),
                                dtype=np.int64)
                np.savez_compressed(f"{outdir}/level_{level:03d}.npz",
                                    keys=K, masks=CM, stab=ST, parent=PAR,
                                    flip=FL, sigma=SG, eps=EP, ids=ids)
                total_classes += len(K)
                for st in ST:
                    total_mass += Gn // int(st)
                known = np.sort(np.concatenate([known, pack2(K)]))
                fr_ids = ids
                fr_masks = CM.astype(np.uint64)
            else:
                fr_ids = np.array([], dtype=np.int64)
                fr_masks = np.zeros((0, 2), dtype=np.uint64)
            pct = 100 * total_mass / target
            print(f"level {level}: +{0 if not NK else len(K)} classes "
                  f"(total {total_classes}), {lvl_edges} edges "
                  f"({total_edges} total), mass {pct:.4f}%, "
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
    main(r, n, nw, cap)
