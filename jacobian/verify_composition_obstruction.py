"""
verify_composition_obstruction.py

Verifies the composition-reduction obstructions of minimal_degree_hunt.md
(Proposition 3) for the original counterexample F = (P,Q,R), deg = (7,6,4).

(a) Top forms: P7 = x^3y^3z, Q6 = 3x^3y^2z, R4 = -x^3z.
(b) No monomial cancellation in h(Q,R): distinct (a,b) with 6a+4b = d give
    distinct top monomials, so deg h(Q,R) attains max(6a+4b) over the support;
    since 6a+4b is even and 7a'+4b' never hits 6, 7a'+6b' never hits 4, no single
    elementary postcomposition (p,q,r) -> (p - h(q,r), q, r) etc. lowers any
    component degree.
(c) Affine postcomposition WLOG: if L is affine invertible and all components of
    L o F have degree <= 6 then all components of F do (components of F are
    affine combinations of those of L o F) -- contradiction with deg P = 7.
    Same argument applies to any target-side affine sandwich.
(d) Elementary precomposition z -> z + h(x,y): P o tau = P + A^3 h; the top of
    A^3 h is z-free while P7 = x^3y^3z, so no cancellation: deg(P o tau) >= 7
    for every h != 0, and = 7 for h = 0.  (Any degree h; rigorous.)
(e) Elementary precompositions y -> y + h(x,z) and x -> x + h(y,z) with
    deg h <= 3: exhaustive symbolic scan; no h makes all components deg <= 6.
    (deg h <= 3 is a searched bound, not a theorem.)
"""
import sympy as sp

x, y, z = sp.symbols('x y z')
A = 1 + x*y
B = A**2*z + y**2*(4 + 3*x*y)
P = sp.expand(A*B); Q = sp.expand(y + 3*x*B); R = sp.expand(2*x - 3*x**2*y - x**3*z)

ok_all = True
def chk(name, ok):
    global ok_all
    ok_all &= bool(ok)
    print(("PASS " if ok else "FAIL "), name)

def topform(f):
    p = sp.Poly(f, x, y, z); d = sp.total_degree(f)
    return sp.Add(*[c*x**m[0]*y**m[1]*z**m[2]
                    for m, c in zip(p.monoms(), p.coeffs()) if sum(m) == d]), d

(tP, dP), (tQ, dQ), (tR, dR) = topform(P), topform(Q), topform(R)
chk("degrees (7,6,4)", (dP, dQ, dR) == (7, 6, 4))
chk("top forms x^3y^3z, 3x^3y^2z, -x^3z",
    tP == x**3*y**3*z and tQ == 3*x**3*y**2*z and tR == -x**3*z)

# (b) semigroup + distinct-monomial check
tops = {}
distinct = True
for a in range(0, 8):
    for b in range(0, 12):
        d = 6*a + 4*b
        if d > 44: continue
        m = sp.expand(tQ**a * tR**b)
        if (d, sp.factor(m)) in tops.values():
            pass
        key = sp.Poly(m, x, y, z).monoms()[0]
        if key in tops and tops[key] != (a, b):
            distinct = False
        tops[key] = (a, b)
chk("tops of Q^aR^b are pairwise distinct monomials (no cancellation possible)", distinct)
chk("6a+4b never equals 7 (parity)", all(6*a+4*b != 7 for a in range(3) for b in range(3)))
chk("7a+4b never equals 6", all(7*a+4*b != 6 for a in range(2) for b in range(3)))
chk("7a+6b never equals 4", all(7*a+6*b != 4 for a in range(2) for b in range(2)))

# (d) z-type precomposition: P o tau = P + A^3 h exactly
h = sp.Function('h')(x, y)
chk("P(x,y,z+h) - P == A^3 h identically",
    sp.simplify(sp.expand(P.subs(z, z + h)) - P - A**3*h) == 0)

# (e) exhaustive deg<=3 scans for y- and x-type elementary precompositions
def scan(kind):
    if kind == 'y':
        basis = [x**i*z**j for i in range(4) for j in range(4) if i + j <= 3]; var = y
    else:
        basis = [y**i*z**j for i in range(4) for j in range(4) if i + j <= 3]; var = x
    cs = sp.symbols(f'd0:{len(basis)}')
    hh = sum(c*m for c, m in zip(cs, basis))
    eqs = set()
    for f in (P, Q, R):
        g = sp.expand(f.subs({var: var + hh}))
        p = sp.Poly(g, x, y, z)
        for m, c in zip(p.monoms(), p.coeffs()):
            if sum(m) >= 7:
                eqs.add(sp.expand(c))
    return sp.solve(list(eqs), list(cs), dict=True)

chk("y -> y+h(x,z), deg h<=3: no solution with all degrees <= 6", scan('y') == [])
chk("x -> x+h(y,z), deg h<=3: no solution with all degrees <= 6", scan('x') == [])

print()
print("ALL CHECKS PASS" if ok_all else "SOME CHECKS FAILED")
import sys; sys.exit(0 if ok_all else 1)
