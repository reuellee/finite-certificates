#!/usr/bin/env python3
"""
Finite certificates concerning "Convergence of Muon with Newton-Schulz"
(arXiv:2601.19156) and inexact-Muon analyses (Shulgin et al., arXiv:2510.19933),
as applied to Muon AS ACTUALLY DEPLOYED (Jordan et al. 2024: 5 Newton-Schulz
steps with tuned coefficients a,b,c = 3.4445, -4.7750, 2.0315).

Quoted target statements (extracted from arXiv:2601.19156 HTML):
  Polynomial analyzed:  p_kappa(lam) = sum_{s=0}^kappa c_s (1-lam)^s,
                        c_s = (2s)!/(4^s (s!)^2) > 0   [Taylor of 1/sqrt(lam)]
  Theorem 2 (decay):    delta_{t,q} <= delta_{t,0}^{(kappa+1)^q}
    where delta_{t,j} = ||Pi_t - X_{t,j} X_{t,j}^T||_op  (orthogonality residual)
  Theorem 1 (rate):     chi_q * O(sqrt(LD/T) + ...),  chi_q <= 1/sqrt(1 - delta_0^{(kappa+1)^q})
  Prescaling:           alpha_t = max{1, ||M_t||_F},  X_{t,0} = M_t / alpha_t.

CERT-M1: The Theorem-2 decay inequality is FALSE for the shipped Muon
         coefficients (degree-5 odd polynomial, i.e. kappa=2 slot):
         one exact-arithmetic step from delta_0 = 0 yields delta_1 = 508599/1000000 > 0.
         (The theorem as stated -- Taylor coefficients -- is NOT violated; the
         certificate shows it does not transfer to Muon as deployed.)

CERT-M2: No number of Newton-Schulz steps rescues the shipped coefficients.
         Exact argument: p(1) = 701/1000 != 1, so by continuity NO orbit can
         have delta_q -> 0 (if delta_q -> 0 then sigma_q -> 1, whence
         delta_{q+1} -> 508599/1000000, a contradiction). Hence chi_q -/-> 1
         (the paper's key mechanism) for deployed Muon, for ANY q.
         Supporting numerics: all positive fixed points of the singular-value
         map are unstable (exact multipliers > 1); the orbit from sigma = 1 is
         bounded, apparently chaotic, with delta_q in ~[0.0959, 0.51] over
         2*10^5 steps (never below 0.05).

CERT-M3 (degenerate family): explicit momentum matrix M_eps = diag(1/2, eps/2),
         eps = 10^-8 (no prescaling since ||M||_F <= 1). After the deployed
         q = 5 steps, the polar approximation error is > 0.9999 for BOTH the
         shipped and the paper's Taylor coefficients: any 'small additive
         inexactness' model (Shulgin et al.) is not satisfied by deployed NS on
         this input, and the paper's own Theorem 2 needs >= 35 NS steps (kappa=2)
         before delta <= 1/2. Type-4 certificate: assumption vacuous on an
         explicit family for the deployed iteration count.

CERT-M4 (vacuity note): Theorem 3.1 of "A Note on the Convergence of Muon"
         (arXiv:2502.02900) requires eta <= (1/(8L)) sqrt((1-2beta)/(2beta));
         for every beta >= 1/2 the admissible stepsize set is EMPTY -- in
         particular for Muon's default momentum beta = 0.95. (That theorem is
         about the nuclear-norm-scaled variant, and is vacuous over the entire
         practical momentum range.)

Exit code 0 iff all certificate checks PASS.
"""
import sys
import sympy as sp

overall_ok = True


def check(name, cond, detail=""):
    global overall_ok
    status = "PASS" if cond else "FAIL"
    if not cond:
        overall_ok = False
    print(f"[{status}] {name}")
    if detail:
        print(f"       {detail}")


# ----------------------------------------------------------------------------
# Definitions
# ----------------------------------------------------------------------------
# Shipped Muon Newton-Schulz step on a singular value x (odd quintic):
A = sp.Rational(34445, 10000)   # 3.4445
B = sp.Rational(-47750, 10000)  # -4.7750
C = sp.Rational(20315, 10000)   # 2.0315

x = sp.symbols('x')
p_shipped = A * x + B * x**3 + C * x**5

# Paper's Taylor polynomial, kappa = 2 (same degree, 5, as shipped):
lam = x**2
p_taylor2 = sp.expand(x * (1 + sp.Rational(1, 2) * (1 - lam)
                           + sp.Rational(3, 8) * (1 - lam)**2))

def f_shipped(v):
    return A * v + B * v**3 + C * v**5

def f_taylor2(v):
    l = v**2
    return v * (1 + sp.Rational(1, 2) * (1 - l) + sp.Rational(3, 8) * (1 - l)**2)

def delta_of(sv):
    """orthogonality residual for a diagonal X with singular value(s) sv:
    ||Pi - X X^T||_op = max_i |1 - sigma_i^2| over the support."""
    if not isinstance(sv, (list, tuple)):
        sv = [sv]
    return max(abs(1 - s**2) for s in sv)


print("=" * 78)
print("CERT-M1: one-step exact falsification of the Thm-2 decay law for")
print("         shipped Muon coefficients (a,b,c = 3.4445, -4.7750, 2.0315)")
print("=" * 78)
# Input: 1x1 matrix M = [1]. ||M||_F = 1 => alpha = max{1,1} = 1, X_0 = 1.
# delta_0 = |1 - 1^2| = 0. Theorem 2 (kappa=2, q=1) claims delta_1 <= 0^3 = 0.
x0 = sp.Integer(1)
d0 = delta_of(x0)
x1_ship = f_shipped(x0)          # = a + b + c = 701/1000 exactly
d1_ship = delta_of(x1_ship)      # = 1 - (701/1000)^2 = 508599/1000000
x1_tay = f_taylor2(x0)
d1_tay = delta_of(x1_tay)

print(f"  input X_0 = [1] (1x1), delta_0 = {d0}")
print(f"  shipped NS step: x_1 = {x1_ship} = {float(x1_ship):.6f}, "
      f"delta_1 = {d1_ship} = {float(d1_ship):.6f}")
print(f"  Taylor(kappa=2) NS step: x_1 = {x1_tay}, delta_1 = {d1_tay}")
check("assumption: input satisfies prescaling + delta_0 = 0 exactly", d0 == 0)
check("Taylor polynomial obeys Thm-2 law here (delta_1 <= delta_0^3 = 0)",
      d1_tay <= d0**3)
check("VIOLATION for shipped coefficients: delta_1 > delta_0^{(kappa+1)^q} = 0",
      d1_ship > 0,
      f"delta_1 = {d1_ship} (exact rational) -- decay law fails at q = 1")

print()
print("=" * 78)
print("CERT-M2: no number of NS steps orthogonalizes with shipped coefficients")
print("=" * 78)
# Fixed points of the singular-value map: solve p(x) = x exactly.
fps = sp.solve(sp.Eq(p_shipped, x), x)
real_pos_fps = [s for s in fps if s.is_real and s > 0]
dp = sp.diff(p_shipped, x)
print(f"  positive fixed points of shipped map: "
      f"{[sp.nsimplify(s) for s in real_pos_fps]}")
all_unstable = True
for s in real_pos_fps:
    slope = sp.simplify(dp.subs(x, s))
    slope_num = sp.N(abs(slope), 30)
    print(f"    x* = {sp.N(s, 12)}  |p'(x*)| = {slope_num}")
    if not (slope_num > 1):
        all_unstable = False
check("every positive fixed point is unstable (|p'(x*)| > 1, exact roots)",
      all_unstable)

# Exact obstruction: p(1) != 1 (and != -1), so delta_q -> 0 is impossible.
p_at_1 = f_shipped(sp.Integer(1))
d_next = delta_of(p_at_1)
print(f"  p(1) = {p_at_1} (exact); delta after a step from sigma = 1: {d_next}")
check("EXACT OBSTRUCTION: p(1) = 701/1000 != +-1, so no orbit can have "
      "delta_q -> 0 (chi_q -/-> 1 for any q)",
      p_at_1 != 1 and p_at_1 != -1 and d_next > sp.Rational(1, 2),
      "if delta_q -> 0 then sigma_q -> 1, whence delta_{q+1} -> "
      f"{d_next} > 1/2: contradiction")

# Long-horizon orbit from sigma = 1: 60-digit floats (2*10^4) + float64 (2*10^5).
prec = 60
xf = sp.Float(1, prec)
Af, Bf, Cf = (sp.Float(A, prec), sp.Float(B, prec), sp.Float(C, prec))
min_delta = None
NIT = 20000
for q in range(1, NIT + 1):
    xf = Af * xf + Bf * xf**3 + Cf * xf**5
    d = abs(1 - xf**2)
    if min_delta is None or d < min_delta:
        min_delta = d
import numpy as np
af, bf, cf = 3.4445, -4.7750, 2.0315
xv, mind64, maxd64 = 1.0, np.inf, 0.0
for q in range(200000):
    xv = af * xv + bf * xv**3 + cf * xv**5
    d = abs(1 - xv * xv)
    mind64, maxd64 = min(mind64, d), max(maxd64, d)
print(f"  min delta over 2*10^4 steps (60-digit): {sp.N(min_delta, 10)}")
print(f"  delta range over 2*10^5 steps (float64): "
      f"[{mind64:.6f}, {maxd64:.6f}]  (bounded, non-vanishing)")
check("orbit residual never falls below 0.05 over long horizons "
      "(supports: residual floor ~0.096, no orthogonalization)",
      min_delta > sp.Float('0.05') and mind64 > 0.05)

# Period-2 points of the shipped map: roots of (p(p(x))-x)/(p(x)-x).
g2 = sp.expand(p_shipped.subs(x, p_shipped) - x)
g1 = sp.expand(p_shipped - x)
quot, rem = sp.div(sp.Poly(g2, x), sp.Poly(g1, x))
r2 = [r for r in np.roots([float(c_) for c_ in quot.all_coeffs()])
      if abs(r.imag) < 1e-12 and r.real > 0]
stable2 = []
for r in sorted(set(round(r.real, 10) for r in r2)):
    m2 = abs(float(dp.subs(x, r)) * float(dp.subs(x, float(p_shipped.subs(x, r)))))
    print(f"  period-2 point x = {r:.6f}: multiplier |p'(x)p'(p(x))| = {m2:.4f}"
          f"{'  (stable)' if m2 < 1 else '  (unstable)'}")
    if m2 < 1:
        stable2.append(r)
msg2 = ("no stable period-2 orbit: dynamics chaotic within a band; "
        "residual floor persists") if not stable2 else "stable 2-cycle exists"
print(f"  -> {msg2}")

print()
print("=" * 78)
print("CERT-M3: degenerate family M_eps = diag(1/2, eps/2), eps = 1e-8;")
print("         deployed q = 5 steps; exact rational arithmetic")
print("=" * 78)
eps = sp.Rational(1, 10**8)
s1, s2 = sp.Rational(1, 2), eps / 2
frob2 = s1**2 + s2**2
check("assumption: ||M||_F <= 1 so alpha = max{1,||M||_F} = 1 (no rescale), "
      "Polar(M) = I_2", frob2 <= 1, f"||M||_F^2 = {float(frob2):.6f}")
for label, f_step in (("shipped", f_shipped), ("Taylor kappa=2", f_taylor2)):
    u, v = s1, s2
    for _ in range(5):
        u, v = f_step(u), f_step(v)
    polar_err = max(abs(1 - u), abs(1 - v))  # ||X_5 - Polar(M)||_op, diagonal
    print(f"  {label:15s}: sigma_1 -> {float(u):.6f}, "
          f"sigma_2 -> {float(v):.3e},  ||X_5 - Polar||_op = {float(polar_err):.10f}")
    check(f"{label}: polar error after deployed 5 steps > 0.9999 on this input "
          f"(exact rational)", polar_err > sp.Rational(9999, 10000))
# Paper's own Theorem-2 bound: need delta_0^{3^q} <= 1/2 with delta_0 = 1 - eps^2/4.
d0_fam = 1 - (eps / 2)**2
q_needed = sp.ceiling(sp.log(sp.log(2) / (-sp.log(d0_fam))) / sp.log(3))
print(f"  paper's Thm-2 bound needs q >= {q_needed} NS steps (kappa=2) for "
      f"delta <= 1/2 on this family; Muon deploys q = 5")
check("paper's own bound requires > 5 NS steps on this family (vacuous at "
      "deployed q = 5)", q_needed > 5)

print()
print("=" * 78)
print("CERT-M4: vacuity of Thm 3.1 stepsize condition (arXiv:2502.02900) for")
print("         all beta >= 1/2, incl. Muon default beta = 0.95")
print("=" * 78)
beta = sp.symbols('beta', positive=True)
expr = (1 - 2 * beta) / (2 * beta)
val_default = expr.subs(beta, sp.Rational(95, 100))
sol = sp.solve(expr >= 0, beta)
print(f"  condition: eta <= (1/(8L)) * sqrt((1-2beta)/(2beta))")
print(f"  (1-2beta)/(2beta) at beta = 0.95: {val_default} < 0 -> sqrt imaginary")
print(f"  nonnegativity of the radicand requires: {sol}")
check("admissible stepsize set is empty for every beta >= 1/2 "
      "(incl. deployed beta = 0.95)", val_default < 0)

print()
print("=" * 78)
if overall_ok:
    print("ALL CERTIFICATE CHECKS PASS")
    sys.exit(0)
else:
    print("SOME CHECKS FAILED")
    sys.exit(1)
