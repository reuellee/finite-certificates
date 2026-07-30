"""Standalone EXACT verification: five zonoboxtope vertex-count certificates
for Conjecture 6.6 of "Maxout Polytopes" (Balakin-Cox-Loho-Sturmfels,
arXiv:2509.21286); see attack_c66_deficit.md.

  * (4,6): f0 = 104 = the conjectured maximum (= absolute cap) of part 2 --
    CONFIRMS that case (the second confirmed case of part 2, first with
    n > d).
  * (3,8): f0 = 110 = the conjectured even-n maximum of part 1 at the first
    n beyond the paper's DFS range -- CONFIRMS the achievability half
    (110 < cap 116, so the upper-bound half stays conjectural).
  * (3,5), (4,5), (3,7): best-known instances at the odd-n cases that
    resist their conjectured maxima -- certified LOWER BOUNDS 42, 58, 84
    (conjectured: 44, 60, 88).

What is PROVEN here, per instance, in exact Fraction arithmetic:
  * The candidate set (all 2^(n+1) sign points of the two zonotopes
    Z^a = sum_i a_i (m_i + [-u_i,u_i]), Z^b likewise) is pairwise DISTINCT,
    so "vertex of Q = conv(Z^a u Z^b)" = "extreme point of the candidate
    set" (every vertex of a hull-of-union is a vertex of one of the parts,
    and every zonotope vertex is a sign point).
  * Each claimed vertex has a witness direction c with c.p > c.q for every
    other candidate (strict, exact) -> p IS a vertex.
  * Each remaining candidate has an explicit convex combination of other
    candidates equal to it (coefficients >= 0 summing to 1, exact)
    -> p is NOT a vertex.
  * Hence f0(Q) EQUALS the claimed count. This certifies max f0(d,n) >= that
    count; it does not by itself bound max f0 from above.

Requirements: python3 stdlib only (fractions, json, itertools).
Exit 0 + PASS iff every check succeeds.
"""
import json, itertools, os, sys
from fractions import Fraction

HERE = os.path.dirname(os.path.abspath(__file__))
CERTS = [("cert_46_104.json", 4, 6, 104), ("cert_38_110.json", 3, 8, 110),
         ("cert_35_42.json", 3, 5, 42), ("cert_45_58.json", 4, 5, 58),
         ("cert_37_84.json", 3, 7, 84)]


def fail(msg):
    print("FAIL:", msg)
    sys.exit(1)


def comb(a, k):
    from math import comb as c
    return c(a, k)


total = 0
for fname, d, n, f0 in CERTS:
    path = os.path.join(HERE, fname)
    if not os.path.exists(path):
        fail(f"missing certificate {fname}")
    cert = json.load(open(path))
    if (cert["d"], cert["n"], cert["f0"]) != (d, n, f0):
        fail(f"{fname}: header mismatch")
    M = [[Fraction(x) for x in r] for r in cert["M"]]
    U = [[Fraction(x) for x in r] for r in cert["U"]]
    a = [Fraction(x) for x in cert["a"]]
    b = [Fraction(x) for x in cert["b"]]
    if not (len(M) == len(U) == len(a) == len(b) == n):
        fail(f"{fname}: instance arrays must have exactly n={n} rows")
    if any(len(r) != d for r in M + U):
        fail(f"{fname}: instance rows must have exactly d={d} coordinates")
    if not all(x >= 0 for x in a + b):
        fail(f"{fname}: coefficients must be nonnegative")

    # exact candidate points
    pts = []
    for coef in (a, b):
        cen = [sum(coef[i] * M[i][j] for i in range(n)) for j in range(d)]
        for s in itertools.product((-1, 1), repeat=n):
            pts.append(tuple(cen[j] + sum(s[i] * coef[i] * U[i][j]
                                          for i in range(n)) for j in range(d)))
    if len(pts) != 2 ** (n + 1):
        fail(f"{fname}: wrong candidate count")
    if len(set(pts)) != len(pts):
        fail(f"{fname}: candidate points not distinct")

    wit = {int(k): [Fraction(x) for x in v] for k, v in cert["witnesses"].items()}
    com = {int(k): [(int(j), Fraction(l)) for j, l in v]
           for k, v in cert["combos"].items()}
    if len(wit) != f0:
        fail(f"{fname}: expected {f0} witnesses, got {len(wit)}")
    if len(com) != len(pts) - f0:
        fail(f"{fname}: expected {len(pts)-f0} combo certificates")
    if set(wit) | set(com) != set(range(len(pts))) or set(wit) & set(com):
        fail(f"{fname}: witness/combo index sets must partition the candidates")

    for i, c in wit.items():
        if len(c) != d:
            fail(f"{fname}: witness {i} has wrong dimension")
        vi = sum(c[k] * pts[i][k] for k in range(d))
        for j, q in enumerate(pts):
            if j != i and sum(c[k] * q[k] for k in range(d)) >= vi:
                fail(f"{fname}: witness {i} not strict against {j}")

    for i, parts in com.items():
        if any(not isinstance(j, int) or j < 0 or j >= len(pts)
               for j, _ in parts):
            fail(f"{fname}: combo {i} has an out-of-range index")
        if any(j == i for j, _ in parts):
            fail(f"{fname}: combo {i} uses itself")
        if any(l < 0 for _, l in parts):
            fail(f"{fname}: combo {i} has a negative coefficient")
        if sum(l for _, l in parts) != 1:
            fail(f"{fname}: combo {i} coefficients do not sum to 1")
        for kdim in range(d):
            if sum(l * pts[j][kdim] for j, l in parts) != pts[i][kdim]:
                fail(f"{fname}: combo {i} does not reproduce the point")

    cap = 4 * sum(comb(n - 1, k) for k in range(d))
    print(f"({d},{n}): f0 = {f0} certified exactly (cap {cap}; "
          f"{len(wit)} vertices, {len(com)} non-vertices).")
    total += 1

print(f"\nAll {total} instances certified.")
print("(4,6): 104 = conjectured maximum ATTAINED -> that case of part 2 is")
print("confirmed (resolved, modulo the classical zonotope vertex bound).")
print("(3,8): 110 = conjectured even-n maximum ATTAINED -> achievability at")
print("the first n beyond the paper's DFS range confirmed.")
print("(3,5)/(4,5)/(3,7): certified lower bounds 42/58/84 vs conjectured")
print("44/60/88 -- lower bounds only; no upper bound is claimed here (see")
print("attack_c66_deficit.md for the odd-n search evidence).")
print("PASS")
sys.exit(0)
