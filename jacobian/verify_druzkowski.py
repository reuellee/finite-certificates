"""Constructs and verifies an EXPLICIT Druzkowski (cubic-linear) Keller
non-automorphism  G(y) = y + (Cy)^{*3}  (componentwise cube), with a rational
matrix C and three explicit rational points sharing one image.

Input: cubic_map.py  (an explicit cubic-homogeneous Keller non-automorphism
F = x + H on C^n with det Jac F = 1 and a 3-point collision, itself derived
mechanically from the Alpoge dim-3 counterexample).

Construction (self-certifying variant of the Druzkowski/Gorni-Zampieri pairing):
 1. Polarization: write each cubic monomial as a rational combination of cubes of
    rational linear forms:
        v^3          = v^3
        v^2 w        = [(v+w)^3 - (v-w)^3 - 2 w^3] / 6
        u v w        = [(u+v+w)^3 - (u+v-w)^3 - (u-v+w)^3 + (u-v-w)^3] / 24
    This yields H(x) = A((Bx)^{*3}) with B (m x n, rows = the linear forms) and
    A (n x m, rational coefficients).  Verified symbolically below.
 2. Set C := B A  (m x m) and G(y) := y + (Cy)^{*3} on C^m — a Druzkowski map.
 3. Intertwining: F(Ay) = Ay + A((BAy)^{*3}) = A(G(y)), i.e.  F o A = A o G.
 4. Keller: JG(y) = I_m + [3 diag((BAy)^{*2}) B] A, so by Sylvester's identity
    det(I_m + XA) = det(I_n + AX):
        det JG(y) = det(I_n + A 3diag((BAy)^{*2}) B) = det JF(Ay) = 1.
    (det JF = 1 is verified in the cubic input; Sylvester instance spot-checked.)
 5. Witnesses: if F(p) = F(q), pick any rational y_p with A y_p = p and set
        y_q := y_p + (Bp)^{*3} - (Bq)^{*3}.
    Then A y_q = q + [A((Bp)^{*3}) - A((Bq)^{*3}) - (q - p)] = q since
    A((Bp)^{*3}) - A((Bq)^{*3}) = H(p) - H(q) = (F(p)-p) - (F(q)-q) = q - p,
    and G(y_p) - G(y_q) = (y_p - y_q) + (Bp)^{*3} - (Bq)^{*3} = 0.  Also
    y_p != y_q (equality would force p = A y_p = A y_q = q).  Same for r.
Hence G is a Druzkowski Keller map on C^m that is NOT injective, hence not an
automorphism: an explicit counterexample to JC in Druzkowski's reduced form.
All checks below are in exact rational arithmetic.  The default mode also
requires the committed ``druzkowski_map.py`` to equal the reconstructed witness;
use ``--regenerate-artifact`` only when intentionally updating that artifact.
"""
import argparse
from pathlib import Path
import random
import sympy as sp

from artifact_io import read_literal_assignments

random.seed(7)

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument(
    "--regenerate-artifact",
    action="store_true",
    help="replace the committed witness with the exact reconstruction",
)
arguments = parser.parse_args()

ns = read_literal_assignments(
    Path(__file__).with_name("cubic_map.py"),
    {"N", "components", "points"},
)
n = ns['N']
V = [sp.Symbol('v%d' % i) for i in range(n)]
F = [sp.expand(sp.sympify(c, dict((str(v), v) for v in V))) for c in ns['components']]
pts = [[sp.nsimplify(c) for c in p] for p in ns['points']]

ok = True

# --- sanity on input: F = x + H, H cubic homogeneous ---
H = [sp.expand(F[i] - V[i]) for i in range(n)]
for h in H:
    if h != 0:
        pol = sp.Poly(h, *V)
        assert all(sum(m) == 3 for m in pol.monoms()), "input not cubic homogeneous"
print("input: cubic homogeneous map on C^%d" % n)

# --- polarization: H = A (B x)^{*3} ---
forms = {}      # tuple(coeffs) -> index
Acols = {}      # (i, j) -> coeff

def form_index(vec):
    key = tuple(vec)
    if key not in forms:
        forms[key] = len(forms)
    return forms[key]

def add(i, vec, c):
    j = form_index(vec)
    Acols[(i, j)] = Acols.get((i, j), 0) + c

def unit(k):
    e = [0]*n
    e[k] = 1
    return e

def comb(k1, s1, k2, s2, k3=None, s3=0):
    e = [0]*n
    e[k1] += s1
    e[k2] += s2
    if k3 is not None:
        e[k3] += s3
    return e

for i, h in enumerate(H):
    if h == 0:
        continue
    pol = sp.Poly(h, *V)
    for mono, c in zip(pol.monoms(), pol.coeffs()):
        idx = [k for k, e in enumerate(mono) if e]
        exps = [mono[k] for k in idx]
        if len(idx) == 1:                      # v^3
            add(i, unit(idx[0]), c)
        elif len(idx) == 2:                    # v^2 w  (v = square factor)
            if exps[0] == 2:
                v, w = idx[0], idx[1]
            else:
                v, w = idx[1], idx[0]
            add(i, comb(v, 1, w, 1), c/6)
            add(i, comb(v, 1, w, -1), -c/6)
            add(i, unit(w), -c/3)
        else:                                  # u v w
            u, v, w = idx
            add(i, comb(u, 1, v, 1, w, 1), c/24)
            add(i, comb(u, 1, v, 1, w, -1), -c/24)
            add(i, comb(u, 1, v, -1, w, 1), -c/24)
            add(i, comb(u, 1, v, -1, w, -1), c/24)

m = len(forms)
print("number of linear forms m =", m)
B = sp.zeros(m, n)
for key, j in forms.items():
    for k, c in enumerate(key):
        B[j, k] = c
A = sp.zeros(n, m)
for (i, j), c in Acols.items():
    A[i, j] = c

# Augment with n zero forms (columns e_i in A, zero rows in B): keeps the
# polarization identity (zero cubes contribute nothing), makes A surjective so
# that witness preimages A y = p exist, and only adds identity components
# y_j + (0)^3 to G (still Druzkowski form).
B = B.col_join(sp.zeros(n, n))
A = A.row_join(sp.eye(n))
m = m + n
print("augmented with %d zero forms -> m = %d" % (n, m))

# verify H(x) = A (Bx)^{*3} symbolically
xvec = sp.Matrix(V)
Bx = B * xvec
rec = A * sp.Matrix([Bx[j]**3 for j in range(m)])
polar_ok = all(sp.expand(rec[i] - H[i]) == 0 for i in range(n))
print("polarization identity H = A(Bx)^{*3}:", polar_ok)
ok &= polar_ok

# --- the Druzkowski map: G(y) = y + (Cy)^{*3}, represented by the matrix C ---
C = (B * A).applyfunc(sp.nsimplify)
print("Druzkowski map G = y + (Cy)^{*3} on C^%d built (matrix C explicit)" % m)

# --- witnesses ---
def cube_vec(v):
    return sp.Matrix([c**3 for c in v])

p0 = sp.Matrix(pts[0])
yp = A.solve_least_squares(p0) if False else None
# particular rational solution of A y = p0 via gauss_jordan_solve (set free vars 0)
sol, params = A.gauss_jordan_solve(p0)
yp = sol.subs({t: 0 for t in params})
assert sp.simplify(A*yp - p0) == sp.zeros(n, 1)

Bp = [B * sp.Matrix(pt) for pt in pts]
ys = [yp,
      yp + cube_vec(Bp[0]) - cube_vec(Bp[1]),
      yp + cube_vec(Bp[0]) - cube_vec(Bp[2])]
for k, pt in enumerate(pts):
    assert sp.simplify(A*ys[k] - sp.Matrix(pt)) == sp.zeros(n, 1)

imgs = []
for yv in ys:
    Cyv = C * yv
    imgs.append(tuple(sp.nsimplify(yv[j] + Cyv[j]**3) for j in range(m)))
distinct = len({tuple(yv) for yv in [tuple(v) for v in [list(y) for y in ys]]}) == 3
same = imgs[0] == imgs[1] == imgs[2]
print("witnesses distinct:", distinct, "| equal images:", same)
ok &= distinct and same

# --- Keller: Sylvester spot-check (exact, small random points) ---
# det JG(y) = det(I_m + 3 diag((BAy)^{*2}) B A) = det(I_n + A 3diag((BAy)^{*2}) B)
#           = det JF(Ay) = 1.
for trial in range(2):
    yv = sp.Matrix([sp.Rational(random.randint(-2, 2), random.randint(1, 2))
                    for _ in range(m)])
    u = C * yv
    D3 = sp.diag(*[3*u[j]**2 for j in range(m)])
    lhs_small = sp.eye(n) + A * D3 * B          # n x n exact det (cheap)
    xv = A * yv
    JF = sp.Matrix([[sp.diff(f, v) for v in V] for f in F])
    det_small = lhs_small.det()
    det_JF = JF.subs(dict(zip(V, list(xv)))).det()
    print("Sylvester RHS det(I_n + A D B) =", det_small, "| det JF(Ay) =", det_JF)
    ok &= (det_small == 1 and det_JF == 1)

artifact = Path(__file__).with_name("druzkowski_map.py")
expected = {
    "m": m,
    "C": [[str(C[i, j]) for j in range(m)] for i in range(m)],
    "points": [[str(c) for c in list(yv)] for yv in ys],
}


def render_artifact(values):
    return (
        "# Auto-generated: explicit Druzkowski counterexample G = y + (Cy)^{*3}\n"
        f"m = {values['m']}\n"
        f"C = {values['C']!r}\n"
        f"points = {values['points']!r}\n"
    )


if arguments.regenerate_artifact:
    if ok:
        artifact.write_text(render_artifact(expected), encoding="utf-8")
        print("wrote", artifact.name)
    else:
        print("refusing to regenerate artifact after a failed exact check")
else:
    try:
        committed = read_literal_assignments(artifact, set(expected))
        artifact_ok = committed == expected
    except (OSError, SyntaxError, ValueError) as exc:
        artifact_ok = False
        print("committed artifact error:", exc)
    print("committed artifact matches exact reconstruction:", artifact_ok)
    ok &= artifact_ok

print("PASS" if ok else "FAIL")
raise SystemExit(0 if ok else 1)
