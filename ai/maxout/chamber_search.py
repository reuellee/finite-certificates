"""Chamber-based search for extremal (3,n)-zonoboxtopes (Conjecture 6.6.1).

Theory (paper Prop 6.3 / Cor 6.4, specialized to zonoboxtopes): Z^a and Z^b
share generator DIRECTIONS u_i (weights/midpoints differ), so they are
normally equivalent; the normal fan is the central arrangement {u_i-perp}.
For each full-dim chamber, with sign vector eps:

  f0(Q) = f0(Z) + #{eps : the linear functional s_eps changes sign on N_eps}

where N_eps = {c : eps_i <u_i,c> >= 0} and
  s_eps = sum_A alpha_i (m_i + eps_i u_i) - sum_B beta_j (m_j + eps_j u_j)
        = (vertex of Z_A at eps) - (vertex of Z_B at eps).

A chamber is 'bicolored' iff both {c in N_eps : <s_eps,c> > 0} and {< 0} are
nonempty (two small LPs). Search maximizes  f0(Z) + #bicolored.

SEARCH TOOL ONLY (floats). Final instances are certified exactly elsewhere.
Usage: python chamber_search.py <n> <target> [seconds] [out.json]
"""
import sys, time, json
import numpy as np
from scipy.optimize import linprog

rng = np.random.default_rng()


def chambers(U):
    """Sign vectors of the full-dim cells of the central arrangement {u_i-perp},
    via ray sampling on cross products (exact enough for generic U)."""
    n = len(U)
    rays = []
    for i in range(n):
        for j in range(i + 1, n):
            r = np.cross(U[i], U[j])
            nr = np.linalg.norm(r)
            if nr > 1e-12:
                rays.append(r / nr)
    # perturb each ray into the adjacent cells + add random directions
    C = set()
    dirs = []
    for r in rays:
        for _ in range(6):
            dirs.append(r + rng.normal(scale=1e-4, size=3))
    dirs += list(rng.normal(size=(4 * n * n, 3)))
    for c in dirs:
        s = np.sign(U @ c)
        if np.all(np.abs(U @ c) > 1e-9):
            C.add(tuple(int(x) for x in s))
    return [np.array(c) for c in C if tuple(-np.array(c)) not in
            {tuple(x) for x in list(C)[:0]}] or [np.array(c) for c in C]


def bicolored(U, eps, s, tol=1e-9):
    """Both strict LPs feasible? Normalize with sum-constraint trick:
    maximize t s.t. eps_i<u_i,c> >= t, sign*<s,c> >= t, |c|_inf <= 1."""
    n = len(U)
    ok = []
    for sign in (+1.0, -1.0):
        # vars: c (3), t (1). maximize t -> minimize -t
        A_ub = np.zeros((n + 1 + 6, 4))
        b_ub = np.zeros(n + 1 + 6)
        A_ub[:n, :3] = -(eps[:, None] * U)
        A_ub[:n, 3] = 1.0
        A_ub[n, :3] = -sign * s
        A_ub[n, 3] = 1.0
        A_ub[n + 1:n + 4, :3] = np.eye(3); b_ub[n + 1:n + 4] = 1.0
        A_ub[n + 4:, :3] = -np.eye(3); b_ub[n + 4:] = 1.0
        r = linprog(c=[0, 0, 0, -1.0], A_ub=A_ub, b_ub=b_ub,
                    bounds=[(None, None)] * 3 + [(None, None)],
                    method="highs")
        ok.append(r.status == 0 and r.x is not None and r.x[3] > tol)
    return ok[0] and ok[1]


def score(M, U, al, be, A_idx, B_idx, chset):
    nb = 0
    for eps in chset:
        s = ((al[:, None] * (M[A_idx] + eps[A_idx, None] * U[A_idx])).sum(0)
             - (be[:, None] * (M[B_idx] + eps[B_idx, None] * U[B_idx])).sum(0))
        if bicolored(U, eps, s):
            nb += 1
    return len(chset) + nb, nb


def n_chambers_theory(n):
    return 2 * (1 + (n - 1) + (n - 1) * (n - 2) // 2)


def rand_config(n, k):
    U = rng.normal(size=(n, 3)); U /= np.linalg.norm(U, axis=1, keepdims=True)
    M = rng.normal(scale=0.5, size=(n, 3))
    al = rng.uniform(0.3, 1.0, k)
    be = rng.uniform(0.3, 1.0, n - k)
    return M, U, al, be


def structured_config(n, k, tilt=0.35, jitter=0.02):
    """d=2-extremal analogue: A-directions a fan in the xy-plane (half-turn),
    B-directions the interleaved fan, both tilted into z alternately."""
    U = np.zeros((n, 3))
    for t in range(k):
        th = np.pi * t / k
        U[t] = [np.cos(th), np.sin(th), tilt * (1 if t % 2 else -1)]
    for t in range(n - k):
        th = np.pi * t / (n - k) + np.pi / (2 * max(k, n - k))
        U[k + t] = [np.cos(th), np.sin(th), tilt * (1 if t % 2 else -1)]
    U += rng.normal(scale=jitter, size=U.shape)
    U /= np.linalg.norm(U, axis=1, keepdims=True)
    M = rng.normal(scale=0.1, size=(n, 3))
    al = np.ones(k) + rng.normal(scale=jitter, size=k)
    be = np.ones(n - k) + rng.normal(scale=jitter, size=n - k)
    return M, U, al, be


def climb(n, k, M, U, al, be, seconds):
    A_idx = np.arange(k); B_idx = np.arange(k, n)
    chset = chambers(U)
    best, nb = score(M, U, al, be, A_idx, B_idx, chset)
    t0 = time.time(); step = 0.15
    while time.time() - t0 < seconds:
        which = rng.random()
        M2, U2, al2, be2 = M.copy(), U.copy(), al.copy(), be.copy()
        if which < 0.45:
            M2 += rng.normal(scale=step, size=M.shape) * (rng.random(M.shape) < 0.4)
        elif which < 0.75:
            al2 = np.maximum(al + rng.normal(scale=step, size=al.shape) * (rng.random(al.shape) < 0.5), 1e-3)
            be2 = np.maximum(be + rng.normal(scale=step, size=be.shape) * (rng.random(be.shape) < 0.5), 1e-3)
        else:
            U2 += rng.normal(scale=step * 0.4, size=U.shape) * (rng.random(U.shape) < 0.3)
            U2 /= np.linalg.norm(U2, axis=1, keepdims=True)
        ch2 = chambers(U2) if which >= 0.75 else chset
        v, nb2 = score(M2, U2, al2, be2, A_idx, B_idx, ch2)
        if v >= best:
            M, U, al, be, chset = M2, U2, al2, be2, ch2
            if v > best:
                print(f"    climb -> {v} (chambers {len(ch2)}, bicolored {nb2})", flush=True)
            best = v
            step = min(step * 1.1, 0.3)
        else:
            step = max(step * 0.99, 0.005)
    return best, (M, U, al, be)


def run(n, target, seconds, out=None):
    kk = n // 2
    t0 = time.time(); best_overall, best_data = 0, None
    while time.time() - t0 < seconds and best_overall < target:
        mode = rng.random()
        k = kk if rng.random() < 0.7 else (n - kk)
        M, U, al, be = (structured_config(n, k) if mode < 0.5
                        else rand_config(n, k))
        v, data = climb(n, k, M, U, al, be, min(30, seconds))
        if v > best_overall:
            best_overall, best_data = v, (data, k)
            print(f"  [{time.time()-t0:5.0f}s] best {v}/{target} "
                  f"(theory chambers {n_chambers_theory(n)})", flush=True)
    if out and best_data:
        (M, U, al, be), k = best_data
        json.dump(dict(M=M.tolist(), U=U.tolist(), al=al.tolist(),
                       be=be.tolist(), k=int(k)), open(out, "w"), indent=1)
        print("saved", out)
    return best_overall


if __name__ == "__main__":
    n = int(sys.argv[1]); target = int(sys.argv[2])
    seconds = int(sys.argv[3]) if len(sys.argv) > 3 else 120
    out = sys.argv[4] if len(sys.argv) > 4 else None
    print(f"n={n} target={target} (chambers should be {n_chambers_theory(n)})")
    print("final best:", run(n, target, seconds, out))
