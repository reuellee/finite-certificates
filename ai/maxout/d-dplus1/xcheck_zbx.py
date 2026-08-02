"""Independent check of the (d,d+1)-zonoboxtope claim.

Builds the paper's construction from its OWN formulas (eqns 11-14), then
counts vertices with THIS REPO's exact counter (ai/alphaevolve/zbx.py),
which was written weeks earlier and shares no code with verify_d_dplus1.py.
Claim under test: f0 = 2^(d+2) - 6, and in particular 58 at d=4.
"""
import sys, os
from fractions import Fraction as F
sys.dont_write_bytecode = True
sys.path.insert(0, os.path.abspath(os.path.join(
    os.path.dirname(__file__), '..', 'finite-certificates', 'ai', 'alphaevolve')))
import zbx

def build(d):
    n = d + 1
    U = [[F(1) if j == i else F(0) for j in range(d)] for i in range(n - 1)]
    U.append([F(-1)] * d)                                   # eqn (11)
    p = [F(2 * i) for i in range(n)]                          # eqn (12)
    q = [F(2 * i + 3) for i in range(n - 1)] + [F(1)]
    t = [(p[i] + q[i]) / 2 for i in range(n)]                 # eqn (13)
    dl = [(p[i] - q[i]) / 2 for i in range(n)]
    b = [F(2 * n)] * n
    a = [b[i] + dl[i] for i in range(n)]
    T = [sum(t[i] * U[i][j] for i in range(n)) for j in range(d)]
    M = [[T[j] / dl[0] for j in range(d)]] + [[F(0)] * d for _ in range(n - 1)]
    return M, U, a, b, T

print('%3s %3s %10s %10s %10s %s' % ('d', 'n', 'zbx exact', 'claim', 'conj (2)', 'T'))
for d in (2, 3, 4, 5):
    M, U, a, b, T = build(d)
    got = zbx.nverts_exact(M, U, a, b)
    claim = (1 << (d + 2)) - 6
    conj = 4 * sum(__import__('math').comb(d, k) for k in range(d))   # 4*sum_{k<d} C(n-1,k), n-1=d
    print('%3d %3d %10d %10d %10d %s' % (d, d + 1, got, claim, conj,
                                         [str(x) for x in T]))
    assert got == claim, 'MISMATCH at d=%d: %d vs %d' % (d, got, claim)
print('\nAll dimensions agree with 2^(d+2)-6, counted by this repo\'s independent exact counter.')
