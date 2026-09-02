"""Constructs and verifies an EXPLICIT cubic-homogeneous (Yagzhev/Bass-Connell-
Wright form) Keller non-automorphism  L = X + N',  N' cubic homogeneous with
J(N') nilpotent, det Jac L = 1, together with THREE distinct rational points
sharing one image.

Input: deg3_map.py (the 27-dim degree-<=3 Keller non-automorphism built by
verify_deg3_keller.py from the Alpoge dim-3 counterexample; G27 = X + F2 + F3,
det Jac = 1, identity linear part, 3-point rational collision).

Construction = Bass-Connell-Wright, Bull. AMS 7 (1982), proof of Theorem (2.1),
Steps 2-3 (all witness-preserving):
  Step 2 (doubling; BCW p.306): on k^{2n} with coordinates (X, Y):
        F'(X,Y) := (X + F2(X) + Y,  Y - F3(X))
    Indeed F' = G(1) o (F (+) id_n) o H(1) with the elementary automorphisms
    G(T) = (X + T*Y, Y), H(T) = (X, Y - T*F3(X)); so F' is Keller with
    det Jac F' = det Jac F = 1, and witnesses transport through H(1)^{-1}:
        (p, 0) |-> (p, F3(p)).
    Writing F' = (X,Y) + N, N = (F2(X)+Y, -F3(X)):  J(E'(T)) = I + T*J(N) is
    invertible over k[T] (see chain below), hence J(N) is NILPOTENT (BCW Lemma 4.1).
  Step 3 (homogenization; BCW p.306-307): with a new variable T,
        L(X,Y,T) := (X + T^2*Y + T*F2(X),  Y - F3(X),  T)
    i.e. L = (X,Y,T) + N'(X,Y,T), N' = (N_(1)T^2 + N_(2)T + N_(3), 0): every
    nonlinear monomial has total degree exactly 3, linear part = identity.
    BCW's graded-ring lemma: J(N) nilpotent => J_{(X,Y)}(N'(T)) nilpotent, so
        det Jac L = det(I + J(N'(T))) = 1  identically.
    At T = 1: L(X,Y,1) = (F'(X,Y), 1), so the three witnesses become
        (p, F3(p), 1)  -- distinct, same image.

Everything finitely checkable is verified below in exact arithmetic:
  C1  the factorization F' = G(1) o (F (+) id) o H(1)  (symbolic identity);
  C2  the scaling identity J(E(T))(x) = (Jac F)(T x) entrywise, where
      E(T) = X + T*F2 + T^2*F3  (this + det Jac F = 1 gives det J(E(T)) = 1,
      hence det J(E'(T)) = 1, hence J(N) nilpotent by BCW Lemma 4.1, hence
      J(N') nilpotent by the graded lemma -- the only non-computational steps
      are these two classical lemmas);
  C3  L is cubic homogeneous with identity linear part, L(X,Y,1) = (F'(X,Y),1);
  C4  the three witness points are distinct and have equal images under L;
  C5  spot checks: det Jac L = 1 exactly at random rational points, and
      J(N')(random rational point)^56 = 0 (pointwise nilpotency).
"""
import random
import sympy as sp

random.seed(11)

ns = {}
exec(open('deg3_map.py').read(), ns)
n = ns['N']
X = [sp.Symbol('v%d' % i) for i in range(n)]
Gc = [sp.expand(sp.sympify(c, dict((str(v), v) for v in X))) for c in ns['components']]
pts = [[sp.nsimplify(c) for c in p] for p in ns['points']]

ok = True

# split F = X + F2 + F3
F2, F3 = [], []
for i, g in enumerate(Gc):
    pol = sp.Poly(g, *X)
    f2 = f3 = sp.Integer(0)
    for mono, c in zip(pol.monoms(), pol.coeffs()):
        d = sum(mono)
        m = sp.prod([X[k]**e for k, e in enumerate(mono) if e], start=sp.Integer(1))
        if d == 1:
            assert m == X[i] and c == 1, "linear part not identity"
        elif d == 2:
            f2 += c*m
        elif d == 3:
            f3 += c*m
        else:
            raise AssertionError("degree > 3 in input")
    F2.append(sp.expand(f2))
    F3.append(sp.expand(f3))

Y = [sp.Symbol('w%d' % i) for i in range(n)]
T = sp.Symbol('T')

# ---- C1: factorization of the doubling step ----
# H(1): (X, Y - F3(X));  then F (+) id;  then G(1): (X + Y, Y)
mid = Gc + [Y[i] - F3[i] for i in range(n)]              # (F(X), Y - F3(X))
lhs = [sp.expand(mid[i] + mid[n + i]) for i in range(n)] + \
      [sp.expand(mid[n + i]) for i in range(n)]          # G(1) applied
Fp = [sp.expand(X[i] + F2[i] + Y[i]) for i in range(n)] + \
     [sp.expand(Y[i] - F3[i]) for i in range(n)]
c1 = all(sp.expand(lhs[i] - Fp[i]) == 0 for i in range(2*n))
print("C1 factorization F' = G(1) o (F+id) o H(1):", c1)
ok &= c1

# ---- C2: J(E(T))(x) = (Jac F)(Tx) entrywise ----
c2 = True
subTX = dict(zip(X, [T*v for v in X]))
for i in range(n):
    for j in range(n):
        lhs_e = sp.diff(X[i] + T*F2[i] + T**2*F3[i], X[j])
        rhs_e = sp.diff(Gc[i], X[j]).subs(subTX)
        if sp.expand(lhs_e - rhs_e) != 0:
            c2 = False
print("C2 scaling identity J(E(T))(x) = JF(Tx):", c2)
ok &= c2

# ---- C3: the cubic homogeneous map L on 2n+1 variables ----
W = X + Y + [T]
L = [sp.expand(X[i] + T**2*Y[i] + T*F2[i]) for i in range(n)] + \
    [sp.expand(Y[i] - F3[i]) for i in range(n)] + [T]
hom = True
for i, comp in enumerate(L):
    pol = sp.Poly(comp - W[i], *W)
    if comp - W[i] != 0:
        hom &= all(sum(m) == 3 for m in pol.monoms())
lin_id = True
zero = dict(zip(W, [0]*(2*n + 1)))
for i, comp in enumerate(L):
    lin = sum(sp.diff(comp, v).subs(zero)*v for v in W)
    lin_id &= sp.expand(lin - W[i]) == 0
sec = all(sp.expand(L[i].subs({T: 1}) - Fp[i]) == 0 for i in range(2*n))
print("C3 cubic homogeneous:", hom, "| identity linear part:", lin_id,
      "| L(.,.,1) = (F'(.), 1):", sec)
ok &= hom and lin_id and sec

# ---- C4: witnesses ----
wit = []
for p in pts:
    subp = dict(zip(X, p))
    wit.append(list(p) + [sp.nsimplify(F3[i].subs(subp)) for i in range(n)] + [1])
imgs = []
for wv in wit:
    sub = dict(zip(W, wv))
    imgs.append(tuple(sp.nsimplify(comp.subs(sub)) for comp in L))
distinct = len({tuple(wv) for wv in wit}) == 3
same = imgs[0] == imgs[1] == imgs[2]
print("C4 witnesses distinct:", distinct, "| equal images:", same)
ok &= distinct and same

# ---- C5: spot checks ----
JL = sp.Matrix([[sp.diff(comp, v) for v in W] for comp in L])
Np = [sp.expand(L[i] - W[i]) for i in range(2*n + 1)]
JN = sp.Matrix([[sp.diff(comp, v) for v in W] for comp in Np])
for trial in range(2):
    sub = dict(zip(W, [sp.Rational(random.randint(-3, 3), random.randint(1, 2))
                       for _ in W]))
    d = JL.subs(sub).det()
    print("C5 det Jac L at random rational point:", d)
    ok &= (d == 1)
# pointwise nilpotency of J(N') at a random rational point (repeated squaring)
sub = dict(zip(W, [sp.Rational(random.randint(-2, 2), random.randint(1, 2))
                   for _ in W]))
M = JN.subs(sub)
k = 1
while k < 2*n + 2:
    M = M*M
    k *= 2
nil = (M == sp.zeros(2*n + 1, 2*n + 1))
print("C5 J(N')(pt)^%d = 0:" % k, nil)
ok &= nil

print("PASS" if ok else "FAIL")

# ---- dump ----
with open('cubic_map.py', 'w', newline='\n') as f:
    f.write("# Auto-generated by verify_cubic_homogeneous.py: explicit cubic-\n"
            "# homogeneous Keller non-automorphism L = X + N' on C^%d (BCW form),\n"
            "# det Jac = 1, J(N') nilpotent, with a 3-point rational collision.\n"
            % (2*n + 1))
    f.write("N = %d\n" % (2*n + 1))
    names = ['v%d' % i for i in range(2*n + 1)]
    ren = dict(zip([str(v) for v in W], names))
    f.write("components = [\n")
    for comp in L:
        s = str(comp)
        # rename w_i -> v_{n+i}, T -> v_{2n}
        import re
        s = re.sub(r'\bw(\d+)\b', lambda mo: 'v%d' % (n + int(mo.group(1))), s)
        s = re.sub(r'\bT\b', 'v%d' % (2*n), s)
        f.write("    %r,\n" % s)
    f.write("]\n")
    f.write("points = [\n")
    for wv in wit:
        f.write("    [%s],\n" % ", ".join("'%s'" % str(c) for c in wv))
    f.write("]\n")
print("wrote cubic_map.py (dimension %d)" % (2*n + 1))
