"""Search harness for Conjecture 6.6 part 1 at n=7,8 (d=3 zonoboxtopes).

SEARCH TOOL ONLY - floats + scipy. Nothing here is part of any verified claim;
the final instance is rationalized and certified exactly by the standalone
verifier.

Model (paper eq. (24), NO centering assumption): segments I_i = conv{p_i, q_i}
i.e. midpoint m_i + [-u_i, u_i]; coefficients a_i, b_i >= 0.
  Z^a = sum a_i I_i   (center sum a_i m_i, generators a_i u_i)
  Z^b = sum b_i I_i
  Q   = conv(Z^a u Z^b)
Every vertex of Q is a sign point of Z^a or of Z^b (2^{n+1} candidates).
This strictly generalizes the 2026-07-25 attack's centered family (m_i = 0),
which froze the relative offset between the two zonotopes at zero - the
paper's own Prop 6.5 sampling uses segment endpoints on the unit sphere,
i.e. generic midpoints. Lemma 6.2 says disjoint supports (a'_i b'_i = 0)
are WLOG, so seeds use a half/half split.

Usage: python search_maxout67.py sanity | n7 | n8 [seconds]
"""
import sys, time, json
import numpy as np
from scipy.spatial import ConvexHull

rng = np.random.default_rng()


def signs(n):
    S = np.array(np.meshgrid(*([[-1.0, 1.0]] * n), indexing="ij")).reshape(n, -1).T
    return S  # (2^n, n)


_SIGN_CACHE = {}


def candidates(M, U, a, b):
    """All 2^{n+1} candidate points (sign points of Z^a and Z^b)."""
    n = len(a)
    if n not in _SIGN_CACHE:
        _SIGN_CACHE[n] = signs(n)
    S = _SIGN_CACHE[n]
    ca, cb = (a[:, None] * M).sum(0), (b[:, None] * M).sum(0)
    Pa = ca + S @ (a[:, None] * U)
    Pb = cb + S @ (b[:, None] * U)
    return np.vstack([Pa, Pb])


def nverts(M, U, a, b):
    P = candidates(M, U, a, b)
    P = np.unique(np.round(P, 9), axis=0)   # dups would corrupt the count
    if len(P) < 4:
        return len(P)
    try:
        return len(ConvexHull(P).vertices)  # NO joggle: QJ splits near-dups
    except Exception:
        return 0                            # degenerate (flat) - worthless


def rand_instance(n, split=None, centered=False):
    """Prop 6.5-style seed. The paper samples FACTORED data (Lemma 6.2):
    residual weights alpha on the first k segments, beta on the rest, plus
    the common zonotope sum max(a'_i,b'_i) I_i. Mapping back to form (24):
      a_i = 2*alpha_i (i<k),  a_i = beta_i  (i>=k)
      b_i = alpha_i   (i<k),  b_i = 2*beta_i(i>=k)
    so BOTH zonotopes carry all n generators, at 2:1 / 1:2 weight ratios."""
    p = rng.normal(size=(n, 3)); p /= np.linalg.norm(p, axis=1, keepdims=True)
    q = rng.normal(size=(n, 3)); q /= np.linalg.norm(q, axis=1, keepdims=True)
    M, U = (p + q) / 2, (p - q) / 2
    if centered:
        M = np.zeros_like(M)
    k = split if split is not None else n // 2
    al = rng.uniform(0.2, 1.0, k)
    be = rng.uniform(0.2, 1.0, n - k)
    a = np.concatenate([2 * al, be])
    b = np.concatenate([al, 2 * be])
    return M, U, a, b


def climb(M, U, a, b, seconds, step0=0.25, report=None):
    best = nverts(M, U, a, b)
    t0 = time.time(); step = step0
    while time.time() - t0 < seconds:
        M2 = M + rng.normal(scale=step, size=M.shape) * (rng.random(M.shape) < 0.3)
        U2 = U + rng.normal(scale=step, size=U.shape) * (rng.random(U.shape) < 0.3)
        a2 = np.maximum(a + rng.normal(scale=step, size=a.shape) * (a > 0) * (rng.random(a.shape) < 0.3), 0)
        b2 = np.maximum(b + rng.normal(scale=step, size=b.shape) * (b > 0) * (rng.random(b.shape) < 0.3), 0)
        v = nverts(M2, U2, a2, b2)
        if v >= best:
            if v > best and report:
                report(v)
            M, U, a, b, best = M2, U2, a2, b2, v
            step = min(step * 1.05, step0)
        else:
            step = max(step * 0.995, 0.01)
    return best, (M, U, a, b)


def multistart(n, target, seconds_total, restart_s=20, centered=False, splits=None):
    best_overall, best_data = 0, None
    t0 = time.time()
    splits = splits or [n // 2]
    while time.time() - t0 < seconds_total:
        sp = splits[rng.integers(len(splits))]
        M, U, a, b = rand_instance(n, split=sp, centered=centered)
        v, data = climb(M, U, a, b, restart_s)
        if v > best_overall:
            best_overall, best_data = v, data
            print(f"  [{time.time()-t0:6.0f}s] new best n={n}: {v} (split {sp})", flush=True)
        if best_overall >= target:
            print(f"  TARGET {target} REACHED", flush=True)
            break
    return best_overall, best_data


def save(data, path):
    M, U, a, b = data
    json.dump(dict(M=M.tolist(), U=U.tolist(), a=a.tolist(), b=b.tolist()),
              open(path, "w"), indent=1)
    print(f"saved {path}")


if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "sanity"
    budget = int(sys.argv[2]) if len(sys.argv) > 2 else 120
    if mode == "sanity":
        # Must reproduce the paper's proven maxima 16/26/44/60 and never exceed.
        want = {3: 16, 4: 26, 5: 44, 6: 60}
        for n, w in want.items():
            v, data = multistart(n, w, budget, restart_s=10)
            flag = "OK" if v == w else ("EXCEEDS?!" if v > w else "short")
            print(f"n={n}: reached {v}, proven max {w} -> {flag}", flush=True)
    elif mode == "n7":
        v, data = multistart(7, 88, budget, restart_s=25, splits=[3, 2])
        print(f"n=7 best: {v}/88 (cap; odd-case conjectured max)")
        if data is not None and v >= 84:
            save(data, "best_n7.json")
    elif mode == "n8":
        v, data = multistart(8, 112, budget, restart_s=25, splits=[4, 3])
        print(f"n=8 best: {v} (conjectured max 110; >=112 REFUTES part 1)")
        if data is not None and v >= 100:
            save(data, "best_n8.json")
