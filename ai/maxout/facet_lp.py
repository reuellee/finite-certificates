"""Facet-coloring LP: complete method for fixed directions U.

Facts used (all from the paper's Section 5/6 framework, specialized):
- Facet classes of the zonotope Z = antipodal pairs of facet normals
  r_ij = u_i x u_j (generic U): C(n,2) classes.
- The 'color' of facet class (i,j) is sign<s_eps(r), r_ij>, where
  eps(r)_k = sign<u_k, r_ij> for k != i,j (the i,j terms vanish).  This sign
  is GLOBAL (shared by the 4 chambers around the ray), linear in (T,al,be).
- Chamber eps is bicolored iff among its rays both signs occur (as seen with
  the chamber's orientation of each ray).
- Cap attained iff EVERY chamber is bicolored.

Method: enumerate sigma in {+-}^C(n,2) (with pruning), keep those making all
chambers mixed, and for each solve one LP over x = (T(3), al(k), be(n-k)).
Feasible LP -> exact-cap instance.  For fixed U this is COMPLETE: if no
(sigma, LP) is feasible, this U cannot attain the cap (up to the delta
margin and genericity).

SEARCH TOOL ONLY (floats).  Usage:
  python facet_lp.py <n> <k> <seconds> [seed_json] [out.json]
"""
import sys, json, time, itertools
import numpy as np
from scipy.optimize import linprog

rng = np.random.default_rng()


def build(U, k):
    """Facet SIDES (two per antipodal class: chambers seeing +r vs -r have
    INDEPENDENT colors when T != 0), their constraint rows, and the
    chamber->side incidence."""
    n = len(U)
    classes = []          # (i, j, r, row_plus, row_minus)
    for i in range(n):
        for j in range(i + 1, n):
            r = np.cross(U[i], U[j])
            nr = np.linalg.norm(r)
            if nr < 1e-10:
                return None
            r = r / nr
            d = U @ r
            if np.any((np.abs(d) < 1e-9) & (np.arange(n) != i) & (np.arange(n) != j)):
                return None                    # non-generic: 3 coplanar dirs
            wrow = np.zeros(n)
            for t in range(n):
                if t in (i, j):
                    continue
                c = np.sign(d[t]) * d[t]       # |<u_t, r>|
                wrow[t] = c if t < k else -c
            rp = np.concatenate([r, wrow])     # <T,r> + W
            rm = np.concatenate([-r, wrow])    # -<T,r> + W  (antipodal side)
            classes.append((i, j, r, rp, rm))
    # chambers via sampling
    dirs = [c[2] + rng.normal(scale=1e-4, size=3) for c in classes for _ in range(8)]
    dirs += [-d for d in dirs] + list(rng.normal(size=(6 * n * n, 3)))
    cham = {}
    for c in dirs:
        d = U @ c
        if np.all(np.abs(d) > 1e-9):
            cham[tuple(np.sign(d).astype(int))] = True
    chambers = [np.array(e) for e in cham]
    # chamber -> list of SIDE indices (side = 2*ci for +r, 2*ci+1 for -r)
    ch_rays = []
    for eps in chambers:
        lst = []
        for ci, (i, j, r, _, _) in enumerate(classes):
            d = eps * (U @ r)
            mask = np.ones(n, bool); mask[[i, j]] = False
            if np.all(d[mask] > 1e-9):
                lst.append(2 * ci)
            elif np.all(d[mask] < -1e-9):
                lst.append(2 * ci + 1)
        if len(lst) < 3:
            return None
        ch_rays.append(lst)
    return classes, chambers, ch_rays


def lp_for_sigma(classes, sigma, n, k, delta=1e-3, wlo=0.1, whi=3.0):
    """sigma has one sign per SIDE (2 per class: rows rp, rm)."""
    A_ub, b_ub = [], []
    for ci, item in enumerate(classes):
        for side, row in ((0, item[3]), (1, item[4])):
            sg = sigma[2 * ci + side]
            A_ub.append(-sg * row); b_ub.append(-delta)
    bounds = [(None, None)] * 3 + [(wlo, whi)] * n
    r = linprog(c=np.zeros(3 + n), A_ub=np.array(A_ub), b_ub=b_ub,
                bounds=bounds, method="highs")
    return (r.x if r.status == 0 else None)


def valid_sigmas(ch_rays, nsides, limit, t0, seconds):
    """Randomized DFS over side-sign assignments; chamber constraint =
    not-all-equal over the chamber's sides."""
    out = []
    sig = [0] * nsides
    # order sides by how many chambers they touch (most constrained first)
    touch = [0] * nsides
    for lst in ch_rays:
        for s in lst:
            touch[s] += 1
    order = sorted(range(nsides), key=lambda s: -touch[s])

    def prune_ok():
        for lst in ch_rays:
            vals = [sig[s] for s in lst]
            if 0 not in vals and len(set(vals)) < 2:
                return False
        return True

    def rec(pos):
        if len(out) >= limit or time.time() - t0 > seconds:
            return
        if pos == nsides:
            out.append(tuple(sig)); return
        first = 1 if rng.random() < 0.5 else -1
        for v in (first, -first):
            sig[order[pos]] = v
            if prune_ok():
                rec(pos + 1)
            sig[order[pos]] = 0
            if len(out) >= limit:
                return

    rec(0)
    return out


def try_U(U, k, t0, seconds, delta=1e-3, wlo=0.02, whi=10.0):
    """Branch-and-bound over side signs with LP pruning of partial
    assignments. COMPLETE for this U (up to delta margin) within budget."""
    n = len(U)
    built = build(U, k)
    if built is None:
        return None
    classes, chambers, ch_rays = built
    nch = 2 * (1 + (n - 1) + (n - 1) * (n - 2) // 2)
    if len(chambers) != nch:
        return None
    nsides = 2 * len(classes)
    rows = []
    for item in classes:
        rows += [item[3], item[4]]
    rows = [r / np.linalg.norm(r) for r in rows]   # sign constraints are
    # scale-free per row; without this, near-coplanar (extremal-looking)
    # configs get spuriously infeasible margins
    touch = [0] * nsides
    for lst in ch_rays:
        for sd in lst:
            touch[sd] += 1
    order = sorted(range(nsides), key=lambda sd: -touch[sd])
    bounds = [(None, None)] * 3 + [(wlo, whi)] * n
    sig = [0] * nsides
    sol = [None]

    def partial_lp():
        A_ub, b_ub = [], []
        for sd in range(nsides):
            if sig[sd] != 0:
                A_ub.append(-sig[sd] * rows[sd]); b_ub.append(-delta)
        if not A_ub:
            return True
        r = linprog(c=np.zeros(3 + n), A_ub=np.array(A_ub), b_ub=b_ub,
                    bounds=bounds, method="highs")
        return r.x if r.status == 0 else None

    def nae_ok():
        for lst in ch_rays:
            vals = [sig[sd] for sd in lst]
            if 0 not in vals and len(set(vals)) < 2:
                return False
        return True

    def rec(pos):
        if sol[0] is not None or time.time() - t0 > seconds:
            return
        if pos == nsides:
            x = partial_lp()
            if x is not None and not isinstance(x, bool):
                sol[0] = x
            return
        first = 1 if rng.random() < 0.5 else -1
        for v in (first, -first):
            sig[order[pos]] = v
            if nae_ok() and partial_lp() is not None:
                rec(pos + 1)
            sig[order[pos]] = 0
            if sol[0] is not None:
                return

    rec(0)
    if sol[0] is None:
        return None
    x = sol[0]
    return dict(U=U.tolist(), T=list(map(float, x[:3])),
                al=list(map(float, x[3:3 + k])),
                be=list(map(float, x[3 + k:])), k=int(k), chambers=nch)


def main():
    n = int(sys.argv[1]); k = int(sys.argv[2]); seconds = int(sys.argv[3])
    seed = sys.argv[4] if len(sys.argv) > 4 and sys.argv[4] != "-" else None
    out = sys.argv[5] if len(sys.argv) > 5 else f"cap_n{n}.json"
    t0 = time.time()
    tried = 0
    while time.time() - t0 < seconds:
        tried += 1
        if seed and tried == 1:
            U = np.array(json.load(open(seed))["U"])
        else:
            U = rng.normal(size=(n, 3))
            U /= np.linalg.norm(U, axis=1, keepdims=True)
        res = try_U(U, k, t0, seconds)
        if res:
            json.dump(res, open(out, "w"), indent=1)
            print(f"CAP ATTAINED at n={n} (U try {tried}); saved {out}")
            return
        if tried % 5 == 0:
            print(f"  [{time.time()-t0:5.0f}s] {tried} U's exhausted, none feasible",
                  flush=True)
    print(f"no cap instance found ({tried} U's)")


if __name__ == "__main__":
    main()
