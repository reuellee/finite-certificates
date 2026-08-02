"""The decisive independent test of the upper-bound argument.

The draft's chain is:  f0(Q) = R + #bicolored chambers   (eqn 10, from
[BCLS Prop 6.3]) with the ray values  g(e_i - e_j) = p_i - q_j  (eqn 8).
Neither is re-derived here; instead both are tested END TO END on RANDOM
instances: compute p,q from the draft's own eqn (7), predict the vertex
count combinatorially, and compare against this repo's exact geometric
counter zbx.nverts_exact, which knows nothing about p, q or chambers.

If eqn (8) or eqn (10) were wrong, these two numbers would disagree.
Also reports whether any random instance EXCEEDS 2^(d+2)-6 (it must not).
"""
import sys, os, random, itertools
from fractions import Fraction as F
sys.dont_write_bytecode = True
sys.path.insert(0, os.path.abspath(os.path.join(
    os.path.dirname(__file__), '..', 'finite-certificates', 'ai', 'alphaevolve')))
import zbx

def solve(A, y):                      # exact linear solve, A is d x d
    d = len(A); M = [row[:] + [y[i]] for i, row in enumerate(A)]
    for c in range(d):
        piv = next((r for r in range(c, d) if M[r][c] != 0), None)
        if piv is None: return None
        M[c], M[piv] = M[piv], M[c]
        pv = M[c][c]
        M[c] = [v / pv for v in M[c]]
        for r in range(d):
            if r != c and M[r][c]:
                f = M[r][c]
                M[r] = [M[r][k] - f * M[c][k] for k in range(d + 1)]
    return [M[i][d] for i in range(d)]

def trial(d, rng):
    n = d + 1
    while True:
        U = [[F(rng.randint(-6, 6)) for _ in range(d)] for _ in range(n)]
        # circuit c with sum c_i u_i = 0 ; solve using first d rows
        A = [[U[i][j] for i in range(d)] for j in range(d)]
        rhs = [-U[n - 1][j] for j in range(d)]
        c = solve(A, rhs)
        if c is None or any(x == 0 for x in c): continue
        import itertools as _it
        def _det(A):
            A=[r[:] for r in A]; k=len(A); D=F(1)
            for i in range(k):
                pv=next((r for r in range(i,k) if A[r][i]!=0),None)
                if pv is None: return F(0)
                if pv!=i: A[i],A[pv]=A[pv],A[i]; D=-D
                D*=A[i][i]
                for r in range(i+1,k):
                    f=A[r][i]/A[i][i]
                    A[r]=[A[r][t2]-f*A[i][t2] for t2 in range(k)]
            return D
        if any(_det([U[i] for i in S])==0 for S in _it.combinations(range(n),d)): continue
        c = c + [F(1)]
        if any(x < 0 for x in c):                      # flip u_i to make c_i>0
            U = [[-v for v in U[i]] if c[i] < 0 else U[i] for i in range(n)]
            c = [abs(x) for x in c]
        a = [F(rng.randint(1, 9)) for _ in range(n)]
        b = [F(rng.randint(1, 9)) for _ in range(n)]
        dl = [a[i] - b[i] for i in range(n)]
        if any(x == 0 for x in dl): continue
        M = [[F(rng.randint(-4, 4)) for _ in range(d)] for _ in range(n)]
        T = [sum(dl[i] * M[i][j] for i in range(n)) for j in range(d)]
        # t with U^T t = T : solve d equations from the d coords
        At = [[U[i][j] for i in range(n)] for j in range(d)]   # d x n, underdetermined
        # pick t supported on first d generators
        Ad = [[U[i][j] for i in range(d)] for j in range(d)]
        td = solve(Ad, T)
        if td is None: continue
        t = td + [F(0)]
        # eqn (7): p_i = (t_i + d_i)/c_i, q_i = (t_i - d_i)/c_i.  This form -- and
        # only this form -- is invariant under t -> t + lambda*c, the free choice
        # in U^T t = T, since both shift by lambda and only differences matter.
        p = [(t[i] + dl[i]) / c[i] for i in range(n)]
        q = [(t[i] - dl[i]) / c[i] for i in range(n)]
        vals = p + q
        if len(set(vals)) != len(vals): continue
        return U, a, b, M, p, q

def predict(p, q, n):
    R = 2 ** n - 2
    bi = 0
    for mask in range(1, (1 << n) - 1):
        P = [i for i in range(n) if mask >> i & 1]
        C = [i for i in range(n) if not mask >> i & 1]
        v = [p[i] - q[j] for i in P for j in C]
        if any(x > 0 for x in v) and any(x < 0 for x in v): bi += 1
    return R, bi

rng = random.Random(20260802)
print('%2s %5s %8s %8s %8s %8s' % ('d', 'trial', 'zbx f0', 'R+bicol', 'agree', 'cap'))
allok = True
for d in (2, 3, 4):
    cap = (1 << (d + 2)) - 6
    for k in range(6 if d < 4 else 4):
        U, a, b, M, p, q = trial(d, rng)
        got = zbx.nverts_exact(M, U, a, b)
        R, bi = predict(p, q, d + 1)
        ok = (got == R + bi)
        allok &= ok and got <= cap
        print('%2d %5d %8d %8d %8s %8d%s' % (d, k, got, R + bi, ok, cap,
              '  <-- EXCEEDS CAP!' if got > cap else ''))
print('\nformula holds on every random instance:', allok)
