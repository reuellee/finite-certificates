"""Constructs and verifies an EXPLICIT degree-<=3 Keller non-automorphism.

Background: the Bass-Connell-Wright / Yagzhev degree reduction says JC reduces to
maps of degree <= 3 (in more variables). Since JC is now false (Alpoge 2026-07-20,
dim 3), an explicit degree-3 counterexample must exist. This script constructs one
MECHANICALLY from the dim-3 counterexample and verifies it in exact arithmetic.

Method (witness-preserving stable equivalence). Start from the normalized map
Ft = (R/2, Q, P) on C^3 (det Jac = 1, Ft(0)=0, JFt(0)=I, three-point collision).
Repeat:
  * stabilize:      G := G + new identity component  z_j  (det, injectivity unchanged)
  * inner elementary e_in : z_j -> z_j + u(x)   (right-composition G := G o e_in),
    so component j becomes  z_j + u;  u a monomial of degree >= 2.
  * outer elementary e_out: w_i -> w_i - c * w_a * w_b  (left-composition),
    which replaces, in component i, the high monomial  c*u*v  (where slots a,b carry
    z_a + u, z_b + v) by the lower-degree terms  -c*(z_a*v + z_b*u + z_a*z_b).
Each step composes G with an explicit triangular (hence det-1) polynomial
automorphism on one side or the other, so:
  det Jac G = det Jac Ft = 1  identically (chain rule + det of triangular
  elementary = 1; side conditions asserted below), and the three witness points are
  transported by the exact inverses of the inner automorphisms.
Every degree->=4 monomial is split u*v with deg u = ceil(d/2), deg v = floor(d/2),
which strictly decreases the maximal degree per pass; the loop ends with deg G <= 3.

Verified at the end (exact arithmetic):
  V1  every component has total degree <= 3;
  V2  G(0) = 0 and Jac G(0) = I  (so G = X + H2 + H3);
  V3  the three transported witness points are pairwise distinct and have the SAME
      image under G  => G is not injective, hence not an automorphism;
  V4  side conditions of every elementary step held (asserted during construction),
      hence det Jac G = 1 identically; additionally det Jac G is spot-checked
      exactly at several rational points.
Result: an explicit Keller map G = X + H (deg <= 3) of C^N which is NOT an
automorphism -- a counterexample to JC in the classical degree-3 reduced form.
"""
import itertools, random
import sympy as sp

random.seed(0)

# ---------- base map ----------
def sym(i):
    return sp.Symbol('v%d' % i)

V = [sym(0), sym(1), sym(2)]
x, y, z = V
A = 1 + x*y
B = A**2*z + y**2*(4 + 3*x*y)
P = sp.expand(A*B)
Q = sp.expand(y + 3*x*B)
R = sp.expand(2*x - 3*x**2*y - x**3*z)
G = [sp.expand(R/2), Q, P]                       # det Jac = 1 (verified in verify_base.py)
pts = [[sp.Integer(0), sp.Integer(0), sp.Rational(-1, 4)],
       [sp.Integer(1), sp.Rational(-3, 2), sp.Rational(13, 2)],
       [sp.Integer(-1), sp.Rational(3, 2), sp.Rational(13, 2)]]

base_J = sp.Matrix([[sp.diff(f, v) for v in V] for f in G])
assert sp.expand(base_J.det()) == 1

# ---------- machinery ----------
def stab():
    """Add an identity component (stable equivalence)."""
    j = len(V)
    V.append(sym(j))
    G.append(V[j])
    for p in pts:
        p.append(sp.Integer(0))
    return j

def rin(j, u):
    """Right-compose with elementary  v_j -> v_j + u.  (det 1, triangular)."""
    assert V[j] not in u.free_symbols            # side condition: triangular
    sub = {V[j]: V[j] + u}
    for i in range(len(G)):
        if V[j] in G[i].free_symbols:
            G[i] = sp.expand(G[i].subs(sub))
    for p in pts:                                # transport witness by e_in^{-1}
        p[j] = p[j] - u.subs(dict(zip(V, p)))

def lsub(i, a, b, c):
    """Left-compose with elementary  w_i -> w_i - c*w_a*w_b.  (det 1)."""
    assert i != a and i != b                     # side condition: triangular
    G[i] = sp.expand(G[i] - c*G[a]*G[b])
    # witness points unchanged (domain-side untouched); images stay equal.

def high_terms():
    out = []
    for i, g in enumerate(G):
        pol = sp.Poly(g, *V)
        for mono, coeff in zip(pol.monoms(), pol.coeffs()):
            if sum(mono) >= 4:
                out.append((i, coeff, mono))
    return out

def mono_expr(mono):
    return sp.prod([V[k]**e for k, e in enumerate(mono) if e], start=sp.Integer(1))

def split(mono):
    """Split exponent vector into u,v with deg u = ceil(d/2) (both >= 2)."""
    flat = []
    for k, e in enumerate(mono):
        flat += [k]*e
    d = len(flat)
    ku = (d + 1)//2
    def pack(idxs):
        m = [0]*len(V)
        for k in idxs:
            m[k] += 1
        return tuple(m)
    return pack(flat[:ku]), pack(flat[ku:])

# ---------- reduction loop ----------
npass = 0
while True:
    hi = high_terms()
    if not hi:
        break
    npass += 1
    maxdeg = max(sum(m) for _, _, m in hi)
    # create slots for all needed factors (dedupe within pass)
    slots = {}
    needed = []
    for i, c, m in hi:
        u, v = split(m)
        needed.append((i, c, u, v))
        for f in (u, v):
            if f not in slots:
                slots[f] = None
    for f in slots:
        j = stab()
        rin(j, mono_expr(f))                     # component j becomes z_j + f
        slots[f] = j
    for i, c, u, v in needed:
        lsub(i, slots[u], slots[v], c)
    print("pass %d: killed %d monomials (maxdeg %d), added %d vars -> dim %d"
          % (npass, len(needed), maxdeg, len(slots), len(V)))

N = len(V)
print("final dimension N =", N)

# ---------- verification ----------
ok = True

# V1: degree <= 3
degs = [sp.total_degree(sp.Poly(g, *V)) for g in G]
print("V1 max component degree:", max(degs))
ok &= max(degs) <= 3

# V2: G(0)=0 and JG(0)=I
zero = dict(zip(V, [0]*N))
ok2 = all(g.subs(zero) == 0 for g in G)
lin_ok = True
for i, g in enumerate(G):
    lin = sum(sp.diff(g, v).subs(zero)*v for v in V)
    lin_ok &= sp.expand(lin - V[i]) == 0
print("V2 G(0)=0:", ok2, "| linear part = identity:", lin_ok)
ok &= ok2 and lin_ok

# V3: witness points distinct, equal images
imgs = []
for p in pts:
    sub = dict(zip(V, p))
    imgs.append(tuple(sp.nsimplify(g.subs(sub)) for g in G))
distinct = len({tuple(p) for p in pts}) == 3
same = imgs[0] == imgs[1] == imgs[2]
print("V3 distinct points:", distinct, "| equal images:", same)
ok &= distinct and same

# V4: exact spot-checks of det Jac G = 1 at random rational points
# (identically 1 by the verified elementary factorization; chain rule)
Jg = sp.Matrix([[sp.diff(g, v) for v in V] for g in G])
for trial in range(3):
    sub = dict(zip(V, [sp.Rational(random.randint(-4, 4), random.randint(1, 3))
                       for _ in range(N)]))
    d = Jg.subs(sub).det()
    print("V4 det Jac G at random rational point:", d)
    ok &= (d == 1)

print("PASS" if ok else "FAIL")

# ---------- dump the map for downstream use ----------
with open('deg3_map.py', 'w', newline='\n') as f:
    f.write("# Auto-generated by verify_deg3_keller.py: explicit degree-<=3 Keller\n"
            "# non-automorphism G = X + H on C^%d with three-point collision.\n" % N)
    f.write("N = %d\n" % N)
    f.write("components = [\n")
    for g in G:
        f.write("    %r,\n" % str(g))
    f.write("]\n")
    f.write("points = [\n")
    for p in pts:
        f.write("    [%s],\n" % ", ".join("'%s'" % str(c) for c in p))
    f.write("]\n")
print("wrote deg3_map.py")
