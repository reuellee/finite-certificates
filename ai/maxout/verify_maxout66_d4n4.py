"""Standalone EXACT verification: smallest open case of Conjecture 6.6(2),
"Maxout Polytopes" (Balakin, Cox, Loho, Sturmfels, arXiv:2509.21286).

Claim verified: there exists a (4,4,1)-maxout polytope ((4,4)-zonoboxtope)
with 32 = 4 * sum_{k=0}^{3} C(3,k) vertices, i.e. the conjectured maximum
(= the absolute cap) is ACHIEVED at d=4, n=4.

Construction: P = conv( Z_a u Z_b ),  Z_a = sum_i [-v_i, v_i],
Z_b = sum_i [-lam_i v_i, lam_i v_i]  (line segments I_i = [-v_i, v_i],
a_i = 1, b_i = lam_i >= 0; corresponding generators parallel), v_i in Q^4.

Proof logic (all arithmetic exact, fractions.Fraction):
  * The candidate point set of conv(A u B) for polytopes A,B is
    vert(A) u vert(B) subseteq the 2^n sign-points of each zonotope;
    hence f0(P) <= 32 always, and f0(P) = 32 iff all 32 sign-points are
    vertices of P.
  * For each of the 32 sign-points p we check a witness direction c with
    c.p > c.q for every other candidate point q (strict, exact). This
    proves p is a vertex of conv(all 32 points) = P.
Exit code 0 + PASS iff all checks succeed; nonzero + FAIL otherwise.
"""
import json, itertools, os, sys
from fractions import Fraction

HERE = os.path.dirname(os.path.abspath(__file__))
with open(os.path.join(HERE, "cert_d4n4.json")) as f:
    cert = json.load(f)

d, n = cert["d"], cert["n"]
V = [[Fraction(x) for x in row] for row in cert["V"]]
lam = [Fraction(x) for x in cert["lam"]]
W = [[Fraction(x) for x in w] for w in cert["witnesses"]]

def fail(msg):
    print("FAIL:", msg)
    sys.exit(1)

if d != 4 or n != 4:
    fail("certificate is not for (d,n)=(4,4)")
if not all(l >= 0 for l in lam):
    fail("scalings must be nonnegative")

# all 2^n sign points of Z_a (scale 1) and Z_b (scale lam)
signs = list(itertools.product([-1, 1], repeat=n))
pts = []
for scale in ([Fraction(1)] * n, lam):
    for s in signs:
        pts.append(tuple(sum(Fraction(s[i]) * scale[i] * V[i][j]
                             for i in range(n)) for j in range(d)))

if len(pts) != 32:
    fail("expected 32 candidate points")
if len(set(pts)) != 32:
    fail("candidate points not distinct")
if len(W) != 32:
    fail("expected 32 witness directions")

for i, (p, c) in enumerate(zip(pts, W)):
    vi = sum(c[k] * p[k] for k in range(d))
    for j, q in enumerate(pts):
        if j == i:
            continue
        if sum(c[k] * q[k] for k in range(d)) >= vi:
            fail(f"witness {i} does not strictly separate point {i} from point {j}")

cap = 4 * sum(1 if k == 0 else
              __import__("math").comb(n - 1, k) for k in range(d))
print(f"All 32 candidate points certified as vertices (exact rational arithmetic).")
print(f"f0 = 32 = 4 * sum_(k=0..3) C(3,k) = conjectured maximum for (4,4,1)-maxout polytopes.")
print("Smallest open case of Conjecture 6.6(2) of arXiv:2509.21286: CONFIRMED (achievability).")
print("PASS")
sys.exit(0)
