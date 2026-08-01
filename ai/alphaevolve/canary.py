"""Canaries for the AlphaEvolve evaluator.  NOTHING downstream is trustworthy
unless this exits 0.

Three checks, in the house style of `../maxout/` (positive AND must-fail):

 1. POSITIVE  -- the exact counter reproduces the certified counts of every
    certificate in ../maxout: 42, 58, 84, 104, 110 (and 32 at (4,4)).
 2. POSITIVE  -- the float counter (the one that actually steers the search)
    agrees with the exact counter on those same instances.
 3. MUST-FAIL -- the repo PROVED max f0(3,5) = 42 (capstone theorem).  Random
    and hill-climbed (3,5) instances are scored in bulk with the float counter;
    a single 43+ means the float counter over-counts, which is exactly the
    failure mode suspected of the paper.  Likewise no score may exceed the
    absolute cap 4*sum_{k<d} C(n-1,k) at any (d,n) probed.

Usage: python canary.py [n_random_35]
"""
import json
import os
import sys
from fractions import Fraction

import numpy as np

import zbx

HERE = os.path.dirname(os.path.abspath(__file__))
MAXOUT = os.path.join(HERE, "..", "maxout")
# the five {M,U,a,b}-form certificates checked by ../maxout/verify_c66_new_cases.py
# (cert_d4n4.json uses the older centered {V,lam} form and is not read here)
CERTS = [("cert_35_42.json", 3, 5, 42),
         ("cert_45_58.json", 4, 5, 58), ("cert_37_84.json", 3, 7, 84),
         ("cert_46_104.json", 4, 6, 104), ("cert_38_110.json", 3, 8, 110)]

fails = []


def check(cond, msg):
    print(("  ok   " if cond else "  FAIL ") + msg)
    if not cond:
        fails.append(msg)


print("1/3  exact counter vs the repo's certified counts")
for fname, d, n, f0 in CERTS:
    path = os.path.join(MAXOUT, fname)
    if not os.path.exists(path):
        check(False, f"{fname} missing")
        continue
    c = json.load(open(path))
    M = [[Fraction(x) for x in r] for r in c["M"]]
    U = [[Fraction(x) for x in r] for r in c["U"]]
    a = [Fraction(x) for x in c["a"]]
    b = [Fraction(x) for x in c["b"]]
    got = zbx.nverts_exact(M, U, a, b)
    check(got == f0, f"{fname}: exact f0 = {got} (certified {f0})")

print("2/3  float counter agrees with exact on the same instances")
for fname, d, n, f0 in CERTS:
    path = os.path.join(MAXOUT, fname)
    if not os.path.exists(path):
        continue
    c = json.load(open(path))
    fl = zbx.nverts_float([[float(Fraction(x)) for x in r] for r in c["M"]],
                          [[float(Fraction(x)) for x in r] for r in c["U"]],
                          [float(Fraction(x)) for x in c["a"]],
                          [float(Fraction(x)) for x in c["b"]])
    check(fl == f0, f"{fname}: float f0 = {fl} (certified {f0})")

print("3/3  MUST-FAIL canary: float counter must never exceed a proven maximum")
N = int(sys.argv[1]) if len(sys.argv) > 1 else 4000
rng = np.random.default_rng(20260801)
worst35, worst_cap = 0, []
for t in range(N):
    n, d = 5, 3
    p = rng.normal(size=(n, d)); p /= np.linalg.norm(p, axis=1, keepdims=True)
    q = rng.normal(size=(n, d)); q /= np.linalg.norm(q, axis=1, keepdims=True)
    M, U = (p + q) / 2, (p - q) / 2
    k = n // 2
    al, be = rng.uniform(0.2, 1.0, k), rng.uniform(0.2, 1.0, n - k)
    a = np.concatenate([2 * al, be]); b = np.concatenate([al, 2 * be])
    v = zbx.nverts_float(M, U, a, b)
    worst35 = max(worst35, v)
    # a short greedy climb, i.e. the regime the evaluator actually runs in
    for _ in range(60):
        M2 = M + rng.normal(scale=0.2, size=M.shape) * (rng.random(M.shape) < .3)
        U2 = U + rng.normal(scale=0.2, size=U.shape) * (rng.random(U.shape) < .3)
        a2 = np.maximum(a + rng.normal(scale=.2, size=a.shape) * (rng.random(a.shape) < .3), 0)
        b2 = np.maximum(b + rng.normal(scale=.2, size=b.shape) * (rng.random(b.shape) < .3), 0)
        v2 = zbx.nverts_float(M2, U2, a2, b2)
        if v2 >= v:
            M, U, a, b, v = M2, U2, a2, b2, v2
    worst35 = max(worst35, v)
check(worst35 <= 42,
      f"(3,5): highest float count over {N} random+climbed instances = "
      f"{worst35} (PROVEN max 42)")

for (d, n) in [(4, 5), (3, 7), (4, 6), (3, 8)]:
    hi = 0
    for t in range(400):
        p = rng.normal(size=(n, d)); p /= np.linalg.norm(p, axis=1, keepdims=True)
        q = rng.normal(size=(n, d)); q /= np.linalg.norm(q, axis=1, keepdims=True)
        k = n // 2
        al, be = rng.uniform(0.2, 1.0, k), rng.uniform(0.2, 1.0, n - k)
        hi = max(hi, zbx.nverts_float((p + q) / 2, (p - q) / 2,
                                      np.concatenate([2 * al, be]),
                                      np.concatenate([al, 2 * be])))
    check(hi <= zbx.cap(d, n),
          f"({d},{n}): max float count {hi} <= cap {zbx.cap(d, n)}")

print()
if fails:
    print(f"CANARY FAILED ({len(fails)}):")
    for f in fails:
        print("  -", f)
    sys.exit(1)
print("CANARY PASS - evaluator is trustworthy")
