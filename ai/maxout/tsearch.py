"""T-search for extremal (3,n)-zonoboxtopes (Conjecture 6.6.1).

Key reduction (this attack): with shared directions u_i, weights al (A-side)
/ be (B-side) and arbitrary segment midpoints, the midpoints enter the
bicoloring functional ONLY through the single vector
    T = sum_A al_i m_i - sum_B be_j m_j  in R^3.
Chamber eps of the central arrangement {u_i-perp} is bicolored iff
    s_eps = T + w_eps  avoids  K_eps u -K_eps,
where w_eps = sum_A al_i eps_i u_i - sum_B be_j eps_j u_j and
K_eps = cone{eps_i u_i}.  f0(Q) = #chambers + #bicolored; the cap needs
every chamber bicolored.  The centered family is exactly T = 0.

SEARCH TOOL ONLY (floats). Usage:
  python tsearch.py <n> <target> [seconds] [out.json]
"""
import sys, time, json
import numpy as np
from scipy.optimize import linprog

rng = np.random.default_rng()


def chambers(U):
    n = len(U)
    dirs = []
    for i in range(n):
        for j in range(i + 1, n):
            r = np.cross(U[i], U[j])
            nr = np.linalg.norm(r)
            if nr > 1e-12:
                r = r / nr
                for _ in range(8):
                    dirs.append(r + rng.normal(scale=1e-4, size=3))
    dirs += list(rng.normal(size=(6 * n * n, 3)))
    C = {}
    for c in dirs:
        d = U @ c
        if np.all(np.abs(d) > 1e-9):
            C[tuple(np.sign(d).astype(int))] = True
    return [np.array(e) for e in C]


def in_cone(s, G):
    """s in cone(rows of G)? LP feasibility, exact-ish."""
    m = len(G)
    r = linprog(c=np.zeros(m), A_eq=G.T, b_eq=s,
                bounds=[(0, None)] * m, method="highs")
    return r.status == 0


def bicolored_T(T, w, G):
    s = T + w
    if np.linalg.norm(s) < 1e-10:
        return False                      # degenerate: not general position
    return not (in_cone(s, G) or in_cone(-s, G))


def count_T(T, ws, Gs):
    return sum(bicolored_T(T, w, G) for w, G in zip(ws, Gs))


def prep(U, al, be, k):
    ch = chambers(U)
    ws, Gs = [], []
    for eps in ch:
        w = ((al[:, None] * (eps[:k, None] * U[:k])).sum(0)
             - (be[:, None] * (eps[k:, None] * U[k:])).sum(0))
        ws.append(w)
        Gs.append(eps[:, None] * U)
    return ch, ws, Gs


def opt_T(ws, Gs, tries=250, refine=120):
    scale = np.mean([np.linalg.norm(w) for w in ws]) + 1e-9
    best, bT = -1, np.zeros(3)
    for _ in range(tries):
        T = rng.normal(scale=scale * rng.uniform(0.05, 1.5), size=3)
        v = count_T(T, ws, Gs)
        if v > best:
            best, bT = v, T
    step = scale * 0.3
    for _ in range(refine):
        T = bT + rng.normal(scale=step, size=3)
        v = count_T(T, ws, Gs)
        if v > best:
            best, bT = v, T
            step *= 1.1
        else:
            step = max(step * 0.97, scale * 0.005)
    return best, bT


def structured_U(n, k, tilt, jitter):
    U = np.zeros((n, 3))
    for t in range(k):
        th = np.pi * t / k
        U[t] = [np.cos(th), np.sin(th), tilt * (1 if t % 2 else -1)]
    for t in range(n - k):
        th = np.pi * t / (n - k) + np.pi / (2 * max(k, n - k))
        U[k + t] = [np.cos(th), np.sin(th), tilt * (1 if t % 2 else -1)]
    U += rng.normal(scale=jitter, size=U.shape)
    return U / np.linalg.norm(U, axis=1, keepdims=True)


def run(n, target, seconds, out=None):
    t0 = time.time()
    best_all, best_pack = 0, None
    nth = 2 * (1 + (n - 1) + (n - 1) * (n - 2) // 2)
    while time.time() - t0 < seconds and best_all < target:
        k = n // 2 if rng.random() < 0.6 else n - n // 2
        if rng.random() < 0.6:
            U = structured_U(n, k, tilt=rng.uniform(0.15, 0.7),
                             jitter=rng.uniform(0.005, 0.08))
        else:
            U = rng.normal(size=(n, 3))
            U /= np.linalg.norm(U, axis=1, keepdims=True)
        al = np.ones(k) * rng.uniform(0.7, 1.3, k)
        be = np.ones(n - k) * rng.uniform(0.7, 1.3, n - k)
        ch, ws, Gs = prep(U, al, be, k)
        if len(ch) != nth:
            continue                       # degenerate arrangement
        nb, T = opt_T(ws, Gs)
        v = len(ch) + nb
        # weight-polish around the best T
        for _ in range(40):
            al2 = np.maximum(al + rng.normal(scale=0.08, size=al.shape), 0.05)
            be2 = np.maximum(be + rng.normal(scale=0.08, size=be.shape), 0.05)
            _, ws2, Gs2 = None, [], []
            for eps in ch:
                w = ((al2[:, None] * (eps[:k, None] * U[:k])).sum(0)
                     - (be2[:, None] * (eps[k:, None] * U[k:])).sum(0))
                ws2.append(w); Gs2.append(eps[:, None] * U)
            nb2, T2 = opt_T(ws2, Gs2, tries=60, refine=60)
            if nb2 > nb:
                nb, T, al, be, ws, Gs = nb2, T2, al2, be2, ws2, Gs2
        v = len(ch) + nb
        if v > best_all:
            best_all = v
            best_pack = dict(U=U.tolist(), al=al.tolist(), be=be.tolist(),
                             k=int(k), T=T.tolist(), chambers=len(ch),
                             bicolored=int(nb))
            print(f"  [{time.time()-t0:5.0f}s] best {v}/{target} "
                  f"({nb}/{len(ch)} chambers bicolored, k={k})", flush=True)
    if out and best_pack:
        json.dump(best_pack, open(out, "w"), indent=1)
        print("saved", out)
    return best_all


if __name__ == "__main__":
    n = int(sys.argv[1]); target = int(sys.argv[2])
    seconds = int(sys.argv[3]) if len(sys.argv) > 3 else 180
    out = sys.argv[4] if len(sys.argv) > 4 else None
    print("final best:", run(n, target, seconds, out))
