"""Base verification of the Alpoge Jacobian-conjecture counterexample.

F = (P,Q,R): C^3 -> C^3, det Jac F = -2, and three rational points share one image.
Also verifies the normalized form Ft = L o F  (L(p,q,r) = (r/2, q, p)) from
Corollary 3.2 of the paper: det Jac Ft = 1, Ft(0)=0, Jac Ft(0) = I.
Exact arithmetic throughout.
"""
import sympy as sp

x, y, z = sp.symbols('x y z')
A = 1 + x*y
B = A**2*z + y**2*(4 + 3*x*y)
P = sp.expand(A*B)
Q = sp.expand(y + 3*x*B)
R = sp.expand(2*x - 3*x**2*y - x**3*z)
F = [P, Q, R]
V = (x, y, z)

ok = True

J = sp.Matrix([[sp.diff(f, v) for v in V] for f in F])
det = sp.expand(J.det())
print("det Jac F =", det)
ok &= (det == -2)

pts = [(0, 0, sp.Rational(-1, 4)),
       (1, sp.Rational(-3, 2), sp.Rational(13, 2)),
       (-1, sp.Rational(3, 2), sp.Rational(13, 2))]
imgs = []
for pt in pts:
    sub = dict(zip(V, pt))
    img = tuple(sp.nsimplify(f.subs(sub)) for f in F)
    imgs.append(img)
    print(pt, "->", img)
ok &= (imgs[0] == imgs[1] == imgs[2] == (sp.Rational(-1, 4), 0, 0))
ok &= len(set(pts)) == 3

# Normalized map Ft = (R/2, Q, P): det 1, fixes 0, identity linear part.
Ft = [sp.expand(R/2), Q, P]
Jt = sp.Matrix([[sp.diff(f, v) for v in V] for f in Ft])
dett = sp.expand(Jt.det())
print("det Jac Ft =", dett)
ok &= (dett == 1)
ok &= all(f.subs(dict(zip(V, (0, 0, 0)))) == 0 for f in Ft)
ok &= Jt.subs(dict(zip(V, (0, 0, 0)))) == sp.eye(3)
imgs_t = [tuple(f.subs(dict(zip(V, pt))) for f in Ft) for pt in pts]
ok &= (imgs_t[0] == imgs_t[1] == imgs_t[2])
print("common image under Ft:", imgs_t[0])

print("PASS" if ok else "FAIL")
