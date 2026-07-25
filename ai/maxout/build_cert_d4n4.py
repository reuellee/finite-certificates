"""Exactify the d=4, n=4 zonoboxtope with 32 vertices.
1) Round V, lam to small rationals; 2) check count still 32 (float);
3) find witness direction per point via perceptron; 4) verify ALL strict
inequalities in exact Fraction arithmetic; 5) dump certificate JSON.
"""
import numpy as np
from fractions import Fraction
import json, itertools, sys

D = "/home/reuellee_gmail_com/ai-certificates/conjecture-harvest"
V = np.load(D + "/V44.npy"); lam = np.load(D + "/lam44.npy")
n, d = V.shape

def pts_float(V, lam):
    S = np.array(list(itertools.product([-1, 1], repeat=n)), dtype=float)
    return np.vstack([S @ V, S @ (lam[:, None] * V)]), S

def count(P, ndirs=200000):
    rng = np.random.default_rng(1)
    hits = set()
    for _ in range(4):
        C = rng.standard_normal((ndirs // 4, P.shape[1]))
        M = C @ P.T
        idx = np.argmax(M, axis=1)
        hits.update(idx.tolist())
    return len(hits)

# --- step 1: rationalize, retry with growing denominators
for den in [20, 50, 200, 1000, 100000]:
    Vr = np.array([[Fraction(x).limit_denominator(den) for x in row] for row in V], dtype=object)
    lr = np.array([Fraction(x).limit_denominator(den) for x in lam], dtype=object)
    Vf = Vr.astype(float); lf = lr.astype(float)
    c = count(pts_float(Vf, lf)[0])
    print(f"den={den}: float count after rounding = {c}")
    if c == 32:
        break
assert c == 32, "rounding destroyed extremality"

# --- step 2: exact points
S = list(itertools.product([-1, 1], repeat=n))
P_exact = []
for scale in [np.array([Fraction(1)] * n, dtype=object), lr]:
    for s in S:
        p = [sum(Fraction(s[i]) * scale[i] * Vr[i, j] for i in range(n)) for j in range(d)]
        P_exact.append(p)
assert len(P_exact) == 32
# distinctness
assert len({tuple(p) for p in P_exact}) == 32, "duplicate points"

Pf = np.array([[float(x) for x in p] for p in P_exact])

# --- step 3: witness directions (perceptron on margins), then rationalize + exact check
witnesses = []
for i in range(32):
    diffs = Pf[i] - np.delete(Pf, i, axis=0)          # want c . diff > 0 for all
    c_vec = diffs.mean(axis=0)
    for it in range(200000):
        m = diffs @ c_vec
        j = np.argmin(m)
        if m[j] > 1e-6 * np.linalg.norm(c_vec):
            break
        c_vec = c_vec + diffs[j]
    else:
        sys.exit(f"no witness found for point {i}")
    c_vec /= np.abs(c_vec).max()
    # rationalize and verify exactly
    ok = False
    for den in [1000, 100000, 10**8]:
        cr = [Fraction(x).limit_denominator(den) for x in c_vec]
        vals = [sum(cr[k] * P_exact[j][k] for k in range(d)) for j in range(32)]
        target = vals[i]
        if all(vals[j] < target for j in range(32) if j != i):
            ok = True
            break
    if not ok:
        sys.exit(f"exact witness verification failed for point {i}")
    witnesses.append([str(x) for x in cr])
    print(f"point {i}: exact witness OK")

cert = {
    "d": d, "n": n,
    "V": [[str(x) for x in row] for row in Vr],
    "lam": [str(x) for x in lr],
    "witnesses": witnesses,
}
with open(D + "/cert_d4n4.json", "w") as f:
    json.dump(cert, f, indent=1)
print("certificate written")
