import sympy as sp
x,y,z = sp.symbols('x y z')
A = 1 + x*y
B = A**2*z + y**2*(4+3*x*y)
P = A*B
Q = y + 3*x*B
R = 2*x - 3*x**2*y - x**3*z
J = sp.Matrix([[sp.diff(f,v) for v in (x,y,z)] for f in (P,Q,R)])
det = sp.expand(J.det())
print("det Jac =", det)
pts = [(0,0,sp.Rational(-1,4)), (1,sp.Rational(-3,2),sp.Rational(13,2)), (-1,sp.Rational(3,2),sp.Rational(13,2))]
for pt in pts:
    sub = {x:pt[0], y:pt[1], z:pt[2]}
    print(pt, "->", (P.subs(sub), Q.subs(sub), R.subs(sub)))
print("degrees:", [sp.total_degree(sp.expand(f)) for f in (P,Q,R)])
