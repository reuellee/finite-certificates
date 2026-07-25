"""Explicit endomorphism of the Weyl algebra A_3 / the symplectic Poisson algebra
C[x1,x2,x3,xi1,xi2,xi3] built from the normalized Jacobian counterexample
Ft = (R/2, Q, P)  (det Jac = 1, Ft(0)=0, JFt(0)=I).

Construction (the classical one used in the proof "Dixmier conjecture_n => JC_n"):
    phi(x_i)  = Ft_i(x)
    phi(d_i)  = D_i := sum_j W_ij(x) d_j ,   W := (JFt^T)^{-1} = adj(JFt)^T  (polynomial!)

We verify in exact arithmetic that phi preserves ALL defining relations of A_3:
    (R1) [phi(x_i), phi(x_j)] = 0                    (trivial: functions commute)
    (R2) [phi(d_i), phi(x_j)] = delta_ij             <=>  W * JFt^T = I
    (R3) [phi(d_i), phi(d_j)] = 0                    <=>  the vector fields D_i
         pairwise commute: sum_k (W_ik dW_jl/dx_k - W_jk dW_il/dx_k) = 0 for all l.
(D_i are first-order operators with coefficients in x only, so their operator
commutator equals the Lie bracket of the corresponding vector fields; no ordering
corrections occur. Hence (R1)-(R3) certify that phi extends to an algebra
endomorphism of A_3.)

The SAME data defines a Poisson endomorphism Phi of (C[x,xi], canonical bracket):
    Phi: x_i -> Ft_i(x),  xi_i -> sum_j W_ij(x) xi_j,
i.e. the cotangent lift  Psi(a, b) = (Ft(a), W(a) b)  on C^6.  (R2),(R3) are exactly
the bracket relations {Phi(xi_i), Phi(x_j)} = delta_ij, {Phi(xi_i), Phi(xi_j)} = 0.

NON-AUTOMORPHY:
  * Poisson case (self-contained): Psi: C^6 -> C^6 is NOT injective — we exhibit
    distinct points with equal images below (using the 3-point collision of Ft and
    b-fibers matched through W(a)^{-1} = JFt(a)^T). A C-algebra endomorphism of a
    polynomial ring whose associated variety map is non-injective is not an
    automorphism. Hence the Poisson conjecture (every Poisson endomorphism of the
    symplectic polynomial algebra in 2n variables is an automorphism) FAILS for n=3.
  * Weyl case: by the classical theorem DC_n => JC_n (proved exactly via this phi:
    if phi were an automorphism of A_3, Ft would be a polynomial automorphism),
    phi is NOT an automorphism of A_3; hence the Dixmier conjecture fails for A_3.
    (That step is cited, not re-verified here; everything computational IS verified.)
"""
import sympy as sp

x1, x2, x3 = sp.symbols('x1 x2 x3')
X = (x1, x2, x3)
A = 1 + x1*x2
B = A**2*x3 + x2**2*(4 + 3*x1*x2)
P = sp.expand(A*B)
Q = sp.expand(x2 + 3*x1*B)
R = sp.expand(2*x1 - 3*x1**2*x2 - x1**3*x3)
Ft = [sp.expand(R/2), Q, P]                     # normalized: det = 1

ok = True

J = sp.Matrix([[sp.diff(f, v) for v in X] for f in Ft])
det = sp.expand(J.det())
print("det JFt =", det)
ok &= (det == 1)

# W = (JFt^T)^{-1} = adjugate(JFt)^T since det = 1  -> polynomial entries
W = J.adjugate().T.applyfunc(sp.expand)

# (R2): W * J^T = I
R2 = sp.expand(W * J.T) == sp.eye(3)
print("(R2) [phi(d_i), phi(x_j)] = delta_ij :", R2)
ok &= R2

# entries polynomial (they are, by construction from adjugate) — print degrees
print("deg W entries:", [[sp.total_degree(sp.Poly(W[i, j], *X)) if W[i, j] != 0 else 0
                          for j in range(3)] for i in range(3)])

# (R3): pairwise Lie brackets of D_i = sum_k W[i,k] d_k vanish
R3 = True
for i in range(3):
    for j in range(i + 1, 3):
        for l in range(3):
            c = sum(W[i, k]*sp.diff(W[j, l], X[k]) - W[j, k]*sp.diff(W[i, l], X[k])
                    for k in range(3))
            R3 &= (sp.expand(c) == 0)
print("(R3) [phi(d_i), phi(d_j)] = 0 :", R3)
ok &= R3

# Non-injectivity of the cotangent lift Psi(a,b) = (Ft(a), W(a) b) on C^6:
pts = [(0, 0, sp.Rational(-1, 4)),
       (1, sp.Rational(-3, 2), sp.Rational(13, 2)),
       (-1, sp.Rational(3, 2), sp.Rational(13, 2))]
eta = sp.Matrix([1, 2, 3])                       # arbitrary covector target
sources, images = [], []
for pt in pts:
    sub = dict(zip(X, pt))
    Ja = J.subs(sub)
    b = Ja.T * eta                               # b = JFt(a)^T eta  = W(a)^{-1} eta
    src = tuple(pt) + tuple(b)
    img = tuple(f.subs(sub) for f in Ft) + tuple((W.subs(sub) * b))
    sources.append(src)
    images.append(tuple(sp.nsimplify(v) for v in img))
print("three distinct C^6 points:", sources)
print("common image:", images[0])
ok &= (images[0] == images[1] == images[2])
ok &= len(set(sources)) == 3

print("PASS" if ok else "FAIL")
