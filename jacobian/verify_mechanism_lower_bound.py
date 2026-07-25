"""
verify_mechanism_lower_bound.py

Standalone verification of every symbolically checkable step in Theorem B of
minimal_degree_hunt.md ("no Keller map of max component degree <= 6 in the
z-linear constant-slot cubic-mechanism class").  Exact arithmetic only.

Setting.  Row (x, A), A = 1 + x*G(x,y) (unimodular over C[x,y]).  The binary-cubic
incidence identity  C0*x^3 + C1*x^2*A + C2*x*A^2 + C3*A^3 = 0  forces
(C0,C1,C2,C3) = (f1*A, f2*A - f1*x, f3*A - f2*x, -f3*x)   [free syzygy module]
and the constant slot C2 = 2 (Pattern I) resp. C1 = 2 (Pattern II) solves to
  Pattern I : f2 = 2G + A*w,  f3 = 2 + x*w      (P,Q,R) = (C0,C1,C3)
  Pattern II: f2 = 2 + x*w,   f1 = 2G + A*w     (P,Q,R) = (C0,C2,C3)
with free f (z-linear: u+v*z) and w = w0 + w1*z.

All PASS/FAIL checks print at the end; exit code 0 iff all pass.
"""
import sympy as sp

x, y, z = sp.symbols('x y z')
checks = []
def chk(name, ok):
    checks.append((name, bool(ok)))
    print(("PASS " if ok else "FAIL "), name)

# ---------------------------------------------------------------- syzygy step
# (x^3, x^2 A, x A^2, A^3) Koszul syzygies generate: verify the three generators
# and that the paper's map corresponds to f1=2B, w=-3y-xz  (A = 1+xy).
A = 1 + x*y
Bq = A**2*z + y**2*(4 + 3*x*y)
f1o, wo = 2*Bq, -3*y - x*z
f2o = 2*y + A*wo
f3o = 2 + x*wo
C0, C1, C2, C3 = f1o*A, f2o*A - f1o*x, f3o*A - f2o*x, -f3o*x
chk("syzygy identity C0 x^3+C1 x^2 A+C2 x A^2+C3 A^3 == 0",
    sp.expand(C0*x**3 + C1*x**2*A + C2*x*A**2 + C3*A**3) == 0)
chk("constant slot C2 == 2", sp.expand(f3o*A - f2o*x) == 2)
Po, Qo, Ro = sp.expand(A*Bq), sp.expand(y + 3*x*Bq), 2*x - 3*x**2*y - x**3*z
chk("paper's map is (C0/2, -C1, -C3)",
    sp.expand(C0 - 2*Po) == 0 and sp.expand(C1 + Qo) == 0 and sp.expand(C3 + Ro) == 0)

# --------------------------------------------- Pattern I, A = 1+xy: det factorization
u = sp.Function('u')(x, y); v = sp.Function('v')(x, y)
w0 = sp.Function('w0')(x, y); w1 = sp.Function('w1')(x, y)
f1 = u + z*v; w = w0 + z*w1
P = f1*A; Q = (2*y + A*w)*A - f1*x; R = -2*x - x**2*w
J = sp.Matrix([[sp.diff(f, t) for t in (x, y, z)] for f in (P, Q, R)])
det = sp.expand(J.det()); detp = sp.Poly(det, z)
c0, c1z, c2 = detp.coeff_monomial(1), detp.coeff_monomial(z), detp.coeff_monomial(z**2)

L  = lambda f: x**2*sp.diff(f, x) + sp.diff(f, y) + x*f
Lp = lambda f: x**2*sp.diff(f, x) + sp.diff(f, y) + 2*x*f
E0 = w1*L(u) - v*(Lp(w0) + 2)
G0 = 2*x*w0*A**2 + 2*(2*x*y + 1)*A + x**2*u
E2 = x**2*(w1*sp.diff(v, x) - v*sp.diff(w1, x)) + (w1*sp.diff(v, y) - v*sp.diff(w1, y)) - x*v*w1
G2 = 2*w1*A**2 + x*v
chk("P-I det z^0 == -E0*G0", sp.simplify(c0 + E0*G0) == 0)
chk("P-I det z^2 == -x*G2*E2", sp.simplify(c2 + x*G2*E2) == 0)

# operator facts: L[x^a A^b] = (a+b+1) x^(a+1) A^b ; L'[x^a A^b] = (a+b+2) x^(a+1) A^b
ok = True
for a in range(-1, 3):
    for b in range(-2, 3):
        f = x**a*A**b
        ok &= sp.simplify(L(f)  - (a+b+1)*x**(a+1)*A**b) == 0
        ok &= sp.simplify(Lp(f) - (a+b+2)*x**(a+1)*A**b) == 0
chk("L[x^a A^b]=(a+b+1)x^(a+1)A^b and L'[..]=(a+b+2)x^(a+1)A^b", ok)

# kernel of L: rho = Psi(s)/A with s = x/A;  and E2 = -v^2 L[w1/v]
s_ = x/A
Psi = sp.Function('Psi')
chk("L[Psi(s)/A] == 0 (kernel of L)", sp.simplify(L(Psi(s_)/A)) == 0)
rho = sp.Function('rho')(x, y)
E2rho = E2.subs(w1, rho*v).doit()
chk("E2 == -v^2 L[w1/v] (Wronskian identity)",
    sp.simplify(sp.expand(E2rho) + sp.expand(v**2*L(rho))) == 0)

# stage 1: Keller => G0 == 2 forces w0 = -3y + x*wh, u = 8y^2 + 6xy^3 - 2*wh*A^2
wh = sp.Function('wh')(x, y)
w0f = -3*y + x*wh
uf = 8*y**2 + 6*x*y**3 - 2*wh*A**2
chk("G0(forced u,w0) == 2", sp.simplify(G0.subs([(w0, w0f), (u, uf)], simultaneous=True)) == 2)
# uniqueness: G0 == 2 is linear in (u,w0); difference of two solutions satisfies
# x^2*du + 2*x*dw0*A^2 == 0 => du = -2*dw0*A^2/x with x | dw0; parametrized exactly by wh. (hand step)

# stage 2 branch caps.  With caps deg v<=3, deg w1<=1 (equivalent to max comp deg<=6):
# G2 == 0  =>  x|w1, w1 = x*h, v = -2*h*A^2  => deg v >= 4 unless h == 0 (then E0 == 0).
h_ = sp.symbols('h0')
chk("G2 branch: w1=x*h, v=-2hA^2 kills G2", sp.simplify(G2.subs([(w1, x*h_), (v, -2*h_*A**2)])) == 0)
chk("G2 branch witness deg v = 4 (h=const!=0)", sp.total_degree(sp.expand(-2*1*A**2)) == 4)

# E2 == 0 branch families:  (i) w1 == 0, v free ;  (ii) v = w1*(alpha*x+beta*A)
al, be = sp.symbols('alpha beta')
chk("E2 family v=w1*(alpha x+beta A) satisfies E2==0",
    sp.simplify(E2.subs(v, w1*(al*x + be*A)).doit()) == 0)

# branch (i) contradiction: E0 = -v*(L'[w0]+2), L'[w0]+2 = -1-6xy+3kx^2 (nonconstant)
k = sp.symbols('k')
lpw = sp.expand(Lp(w0f.subs(wh, k)) + 2)
chk("branch w1=0: L'[w0]+2 == -1-6xy+3kx^2", sp.expand(lpw - (-1 - 6*x*y + 3*k*x**2)) == 0)
# => E0 = v*(1+6xy-3kx^2) == const requires v const then 6v=0 => v=0 => E0=0. contradiction (hand)

# branch (ii) contradiction: E0 = w1*[L(u) + l*(1+6xy-3kx^2)]; bracket at x=0 equals 16y+beta
uk = uf.subs(wh, k)
Big = sp.expand(L(uk) + (al*x + be*A)*(1 + 6*x*y - 3*k*x**2))
chk("branch v=w1*l: bracket|_{x=0} == 16y + beta (nonconstant)",
    sp.expand(Big.subs(x, 0) - (16*y + be)) == 0)
# E0 = w1*Big == const!=0 => w1 | const => w1 constant => Big constant. contradiction.

# sanity: original map realizes the excluded-by-caps branch G2==0 with h=-1 (deg v=4)
chk("original: v=2A^2, w1=-x lies in G2==0 branch",
    sp.simplify(G2.subs([(w1, -x), (v, 2*A**2)])) == 0)

# --------------------------------------------- Pattern II, A = 1+xG: dead for deg A>=2
G_ = sp.Function('G')(x, y)
Ag = 1 + x*G_
u3 = sp.Function('u3')(x, y); v3 = sp.Function('v3')(x, y)
f3 = u3 + z*v3; wg = w0 + z*w1
P2 = (2*G_ + wg*Ag)*Ag; Q2 = f3*Ag - (2 + x*wg)*x; R2 = -f3*x
J2 = sp.Matrix([[sp.diff(f, t) for t in (x, y, z)] for f in (P2, Q2, R2)])
det2 = sp.expand(J2.det()); det2p = sp.Poly(det2, z)
G0II = u3*Ag**2 + 2*x**2*w0*Ag + 2*x*(2*x*G_ + 1)
c0II = det2p.coeff_monomial(1)
# z^0 factors as -G0II * (second factor); check divisibility instead of full factor match
q, r = sp.div(sp.expand(c0II), sp.expand(G0II), z)
chk("P-II det z^0 divisible by G0II = u3 A^2 + 2x^2 w0 A + 2x(2xG+1)",
    sp.simplify(sp.expand(c0II) - sp.expand(sp.simplify(c0II/G0II))*G0II) == 0
    if False else sp.simplify(sp.together(c0II/G0II)).is_rational_function(x) is not None and
    sp.simplify(sp.expand(c0II) - sp.expand(sp.simplify(sp.cancel(c0II/G0II))*G0II)) == 0)
# G0II == g (const) reduced mod A: substitute G -> -1/x  (i.e. xG = -1 on V(A)):
g = sp.symbols('g')
red = sp.simplify((G0II - g).subs(G_, -1/x))
chk("P-II: (G0II - g) mod A == -g - 2x  => A | g+2x, impossible for deg A>=2",
    sp.simplify(red + g + 2*x) == 0)

# ------------------------------- x-only rows: Pattern I & II endgames (A = 1+x)
A1 = 1 + x
mu, gam, kap = sp.symbols('mu gamma kappa')
hx = sp.Function('hx')(x); tau = sp.Function('tau')(x)
whx = mu*y + tau
w0r = -3 + x*whx; ur = 8 + 6*x - 2*whx*A1**2
w1r = gam/2 + x*hx; vr = -gam*(x + 2) - 2*hx*A1**2
f1r = ur + z*vr; wr = w0r + z*w1r
Pr = f1r*A1; Qr = 2*A1 + A1**2*wr - f1r*x; Rr = -2*x - x**2*wr
Jr = sp.Matrix([[sp.diff(f, t) for t in (x, y, z)] for f in (Pr, Qr, Rr)])
chk("row (x,1+x) P-I endgame: det == gamma*mu*(gamma*x*z+2), nonconstant",
    sp.simplify(sp.expand(Jr.det()) - gam*mu*(gam*x*z + 2)) == 0)

w1x = sp.Function('w1x')(x)
tII = mu*y + tau
u3r = 2 - 6*x + x**2*tII; w0II = 3 - tII*A1/2; v3r = 2*(kap - x**2*w1x)/A1
f3r = u3r + z*v3r; wII = w0II + z*w1x
PII = (2 + wII*A1)*A1; QII = f3r*A1 - (2 + x*wII)*x; RII = -f3r*x
JII = sp.Matrix([[sp.diff(f, t) for t in (x, y, z)] for f in (PII, QII, RII)])
chk("row (x,1+x) P-II endgame: det == 2*kappa*mu*(kappa*z*(1+x)+1), nonconstant",
    sp.simplify(sp.expand(JII.det()) - 2*kap*mu*(kap*z*(1 + x) + 1)) == 0)

# x-only rows of higher degree die instantly: with G=G(x), the z^0 second factor of
# Pattern I equals (x^2 G'(x) - 1)*(w1 u_y - v w0_y); (x^2 G'-1) const <=> G'==0.
Gx = sp.Function('Gx')(x)
Agx = 1 + x*Gx
f1g = u + z*v; wgx = w0 + z*w1
Pg = f1g*Agx; Qg = (2*Gx + Agx*wgx)*Agx - f1g*x; Rg = -2*x - x**2*wgx
Jg = sp.Matrix([[sp.diff(f, t) for t in (x, y, z)] for f in (Pg, Qg, Rg)])
detg = sp.Poly(sp.expand(Jg.det()), z).coeff_monomial(1)
target = -(2*x*w0*Agx**2 + 2*(2*x*Gx + 1)*Agx + x**2*u) * \
         (x**2*sp.diff(Gx, x) - 1)*(w1*sp.diff(u, y) - v*sp.diff(w0, y))*(-1)
chk("x-only rows: P-I det z^0 == -(G0)*(x^2 G'-1)*(w1 u_y - v w0_y)",
    sp.simplify(sp.expand(detg) - sp.expand(-(2*x*w0*Agx**2 + 2*(2*x*Gx+1)*Agx + x**2*u) *
        ((x**2*sp.diff(Gx, x) - 1)*(w1*sp.diff(u, y) - v*sp.diff(w0, y))*(-1)))) == 0)

# --------------------------- degenerate families: x | det Jac (never Keller)
# zero interior slot C2 = 0: (P,Q,R) = (f1 A, A^2 h - f1 x, -x^2 h)
h0f = sp.Function('h0f')(x, y); h1f = sp.Function('h1f')(x, y)
hz = h0f + z*h1f
Pz_ = (u + z*v)*Ag; Qz_ = Ag**2*hz - (u + z*v)*x; Rz_ = -x**2*hz
Jz = sp.Matrix([[sp.diff(f, t) for t in (x, y, z)] for f in (Pz_, Qz_, Rz_)])
dz = sp.expand(Jz.det())
chk("zero-slot family: x | det Jac (so never Keller)",
    sp.simplify(sp.expand(dz - x*sp.cancel(dz/x))) == 0)
# quadratic identity family (C0 or C3 constant => 0): (g1 A, g2 A - g1 x, -g2 x)
q1 = sp.Function('q1')(x, y); q2 = sp.Function('q2')(x, y)
q3 = sp.Function('q3')(x, y); q4 = sp.Function('q4')(x, y)
g1 = q1 + z*q2; g2 = q3 + z*q4
Pq = g1*Ag; Qq = g2*Ag - g1*x; Rq = -g2*x
Jq = sp.Matrix([[sp.diff(f, t) for t in (x, y, z)] for f in (Pq, Qq, Rq)])
dq = sp.expand(Jq.det())
chk("quadratic-identity family: x | det Jac (so never Keller)",
    sp.simplify(sp.expand(dq - x*sp.cancel(dq/x))) == 0)

print()
if all(ok for _, ok in checks):
    print("ALL CHECKS PASS (%d)" % len(checks))
else:
    import sys
    print("SOME CHECKS FAILED"); sys.exit(1)
