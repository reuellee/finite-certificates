#!/usr/bin/env python3
"""
verify_n2.py -- sympy sanity checks for n2_analysis.md
(structural transfer of the Alpoge n=3 Jacobian counterexample mechanism to n=2).

Checks (PASS/FAIL each, exit nonzero on any FAIL):

  [1] The n=3 counterexample: det Jac F == -2, the three witness points share
      one image, F is affine-linear in z, the z-coefficient row is
      (A^3, 3xA^2, -x^3), and (x, A) is a unimodular row over C[x,y].
  [2] The n=3 field identity 2ps^3 - qs^2 + 2s - r = 0 with s = x/A
      (the generic-degree-3 engine).
  [3] Prop. A identity: for F = (a(x)y+b(x), c(x)y+d(x)),
      det Jac F = (a'c - ac') y + (b'c - a d')   (exact, symbolic).
  [4] Wronskian identity (a/c)' = (a'c - ac')/c^2 (used in Prop. A's proof).
  [5] Prop. A normal forms are automorphisms: explicit inverses check out
      symbolically in both branches of the classification.
  [6] Deck-transformation determinant identity (det Jac sigma)*(det Jac F o sigma)
      = det Jac F, verified on the model double cover F=(x, y^2), sigma=(x,-y);
      and for that F the polynomial t with t^2 = h o F (h = q, squarefree) is
      t = y, with Z(det Jac F) = Z(t): etale-ness fails exactly on div(t),
      as Theorem C's proof predicts for any would-be generic-degree-2 map.
  [7] Scoping example: sigma(x,y) = (-x, 1/x^2 - y) is a birational involution
      of C^2, regular and FIXED-POINT-FREE off {x=0}, with sigma*(dx^dy) = dx^dy.
      So the soft constraints (L2)+(L3) alone do not yield a contradiction;
      the ramification argument of Theorem C is genuinely needed.
"""
import sys
import sympy as sp

x, y, z = sp.symbols('x y z')
p, q, r, s = sp.symbols('p q r s')

failures = []

def check(name, ok):
    print(f"[{'PASS' if ok else 'FAIL'}] {name}")
    if not ok:
        failures.append(name)

# ---------------------------------------------------------------- [1] n=3 map
A = 1 + x*y
B = A**2*z + y**2*(4 + 3*x*y)
P = A*B
Q = y + 3*x*B
R = 2*x - 3*x**2*y - x**3*z
F = sp.Matrix([P, Q, R])
J = F.jacobian([x, y, z])
check("n=3: det Jac F == -2 identically",
      sp.simplify(J.det()) == -2)

pts = [(0, 0, sp.Rational(-1, 4)),
       (1, sp.Rational(-3, 2), sp.Rational(13, 2)),
       (-1, sp.Rational(3, 2), sp.Rational(13, 2))]
imgs = [tuple(sp.simplify(c.subs({x: a, y: b, z: cc})) for c in (P, Q, R))
        for (a, b, cc) in pts]
check("n=3: three witness points share image (-1/4, 0, 0)",
      imgs[0] == imgs[1] == imgs[2] == (sp.Rational(-1, 4), 0, 0))

check("n=3: F is affine-linear in z (d^2F/dz^2 == 0)",
      all(sp.expand(sp.diff(c, z, 2)) == 0 for c in (P, Q, R)))

row = [sp.expand(sp.diff(c, z)) for c in (P, Q, R)]
check("n=3: z-coefficient row equals (A^3, 3xA^2, -x^3)",
      row == [sp.expand(A**3), sp.expand(3*x*A**2), sp.expand(-x**3)])

check("n=3: (x, A) unimodular over C[x,y]:  (-y)*x + 1*A == 1",
      sp.expand(-y*x + A) == 1)

# ------------------------------------------------- [2] generic-degree-3 engine
s_val = x / A
cubic = 2*P*s_val**3 - Q*s_val**2 + 2*s_val - R
check("n=3: field identity 2Ps^3 - Qs^2 + 2s - R == 0 with s = x/A",
      sp.simplify(cubic) == 0)

# --------------------------------------------- [3] Prop. A: y-affine Keller maps
N = 6  # generic coefficient degree; identity is degree-agnostic
acoef = sp.symbols(f'a0:{N+1}')
bcoef = sp.symbols(f'b0:{N+1}')
ccoef = sp.symbols(f'c0:{N+1}')
dcoef = sp.symbols(f'd0:{N+1}')
a = sum(acoef[i]*x**i for i in range(N+1))
b = sum(bcoef[i]*x**i for i in range(N+1))
c = sum(ccoef[i]*x**i for i in range(N+1))
d = sum(dcoef[i]*x**i for i in range(N+1))
F2 = sp.Matrix([a*y + b, c*y + d])
det2 = sp.expand(F2.jacobian([x, y]).det())
target = sp.expand((sp.diff(a, x)*c - a*sp.diff(c, x))*y
                   + (sp.diff(b, x)*c - a*sp.diff(d, x)))
check("Prop A: det Jac = (a'c - ac') y + (b'c - a d')  [generic deg 6 coeffs]",
      sp.simplify(det2 - target) == 0)

# ------------------------------------------------------- [4] Wronskian identity
check("Prop A: (a/c)' == (a'c - ac')/c^2  [rational identity]",
      sp.simplify(sp.diff(a/c, x) - (sp.diff(a, x)*c - a*sp.diff(c, x))/c**2) == 0)

# --------------------------------------------- [5] normal forms are invertible
# Branch 1 (c != 0): q = c0*y + d(x), p = mu*q + e1*x + e0, c0*e1 != 0.
mu, c0, e0, e1 = sp.symbols('mu c0 e0 e1')
d_generic = sum(dcoef[i]*x**i for i in range(6))
q1 = c0*y + d_generic
p1 = mu*q1 + e1*x + e0
det_b1 = sp.simplify(sp.Matrix([p1, q1]).jacobian([x, y]).det())
check("Prop A branch 1: det Jac == c0*e1 (nonzero constant)",
      det_b1 == c0*e1)
# explicit inverse: x = (p - mu*q - e0)/e1, y = (q - d(x))/c0
X1 = (p - mu*q - e0)/e1
Y1 = (q - d_generic.subs(x, X1))/c0
back = [sp.simplify(w.subs({p: p1, q: q1})) for w in (X1, Y1)]
check("Prop A branch 1: explicit inverse recovers (x, y)",
      back == [x, y])

# Branch 2 (c == 0): F = (a0*y + b(x), d1*x + d0), a0*d1 != 0.
a0, d0, d1 = sp.symbols('a0_ d0_ d1_')
b_generic = sum(bcoef[i]*x**i for i in range(6))
p2 = a0*y + b_generic
q2 = d1*x + d0
det_b2 = sp.simplify(sp.Matrix([p2, q2]).jacobian([x, y]).det())
check("Prop A branch 2: det Jac == -a0*d1 (nonzero constant)",
      det_b2 == -a0*d1)
X2 = (q - d0)/d1
Y2 = (p - b_generic.subs(x, X2))/a0
back2 = [sp.simplify(w.subs({p: p2, q: q2})) for w in (X2, Y2)]
check("Prop A branch 2: explicit inverse recovers (x, y)",
      back2 == [x, y])

# ---------------------------- [6] deck involution identities on model F=(x,y^2)
Fm = sp.Matrix([x, y**2])          # NOT Keller: the model of a degree-2 cover
sig = {x: x, y: -y}                # deck involution
check("model: F o sigma == F",
      [sp.simplify(c.subs(sig)) for c in Fm] == list(Fm))
Jf = Fm.jacobian([x, y]).det()      # 2y
Js = sp.Matrix([sig[x], sig[y]]).jacobian([x, y]).det()  # -1
check("model: (det J sigma)*(det J F o sigma) == det J F",
      sp.simplify(Js*Jf.subs(sig) - Jf) == 0)
# Theorem C data: h(p,q) = q is squarefree, t = y in C[x,y], t^2 = h o F.
t_poly = y
h_of_F = Fm[1]
check("model: t = y is a POLYNOMIAL with t^2 == h o F (h = q squarefree)",
      sp.expand(t_poly**2 - h_of_F) == 0)
check("model: Z(det Jac F) == Z(t): etale-ness fails exactly on div(t)",
      sp.simplify(Jf / t_poly) == 2)   # det = 2t, same zero divisor

# ------------------------------- [7] free, omega-preserving rational involution
sx, sy = -x, 1/x**2 - y
comp = (sx.subs({x: sx, y: sy}, simultaneous=True),
        sy.subs({x: sx, y: sy}, simultaneous=True))
check("scoping sigma: sigma o sigma == id  (birational involution)",
      sp.simplify(comp[0] - x) == 0 and sp.simplify(comp[1] - y) == 0)
Jsig = sp.Matrix([sx, sy]).jacobian([x, y]).det()
check("scoping sigma: sigma*(dx^dy) == dx^dy  (det Jac sigma == +1)",
      sp.simplify(Jsig) == 1)
fixed = sp.solve([sp.Eq(sx, x), sp.Eq(sy, y)], [x, y], dict=True)
check("scoping sigma: no fixed points where regular (only candidate x=0 = pole)",
      fixed == [])

# -----------------------------------------------------------------------------
print()
if failures:
    print(f"{len(failures)} check(s) FAILED:")
    for f in failures:
        print("  -", f)
    sys.exit(1)
print("All checks PASSED.")
sys.exit(0)
