#!/usr/bin/env python3
"""Certificate 2: gradient x input AND Integrated Gradients assign EXACTLY ZERO
attribution to the sole causal feature and nonzero attribution to a provably
inert feature — one network covers both methods, exact sympy arithmetic.

NETWORK N2 (ReLU MLP, 2 inputs, 6 hidden units, 1 linear output; 18 params):
    Both inputs pass through identical 'tent' subnetworks
        t(z) = ReLU(z) - 2*ReLU(z - 1/2) + ReLU(z - 1)
    (t is the piecewise-linear tent: 0 for z<=0, peak 1/2 at z=1/2, 0 for z>=1,
     slope 0 for z>1 — a saturated/flat region, no kink at interior points.)
    f(x1, x2) = t(x1) + t(x2).

TASK / DISTRIBUTION D (finite, non-degenerate, all points at differentiable
    interior points of linear regions):
    x1 in {1/4, 2},  x2 in {1/4, 3/4}, uniform product (4 inputs).
    Behavior: f = t(x1) + 1/4, since t(1/4) = t(3/4) = 1/4 on x2's support.
    So the output is a nonconstant function of x1 ONLY:
        x1 = 1/4 -> f = 1/2;  x1 = 2 -> f = 1/4.

GROUND TRUTH (provable):
    x1 is causal at every input: swapping x1 between its two attested values
    changes f by exactly 1/4 at every point of D.
    x2 is causally inert on D: swapping x2 between its attested values
    (1/4 <-> 3/4) changes f by exactly 0 at every point of D.

REGISTERED METHODS (standard variants):
    (a) gradient x input (Shrikumar et al. 2016; Simonyan et al. 2013 saliency):
        A_i(x) = x_i * df/dx_i(x), features ranked by |A_i|.
    (b) Integrated Gradients (Sundararajan, Taly & Yan, ICML 2017), zero
        baseline x' = 0 (the paper's and Captum's default), straight-line path:
        IG_i(x) = (x_i - x'_i) * Integral_0^1 df/dx_i(x' + a(x - x')) da,
        features ranked by |IG_i|.  We compute the path integral EXACTLY by
        sympy piecewise integration (no Riemann approximation).

CERTIFIED MISMATCH (at the certified inputs X* = (2, 1/4) and (2, 3/4),
    i.e. half the support — and f is differentiable there, no kink excuse):
    grad x input = (0, 1/4) resp. (0, -3/4):  causal feature x1 gets EXACTLY 0
        (t is flat at x1=2), inert feature x2 gets nonzero.
    IG (zero baseline) = (0, 1/4):  IG_1 = t(2) - t(0) = 0 exactly (up-slope
        and down-slope of the tent cancel along the path), IG_2 = 1/4 != 0.
        Completeness holds: 0 + 1/4 = f(X*) - f(0).  Sensitivity(a) is NOT
        violated (f(2, x2) = f(0, x2)) — the axioms do not exclude this.
    Ranking by |attribution|: inert x2 STRICTLY ABOVE causal x1, both methods.
Exit nonzero if any exact claim fails.
"""
import sys
from sympy import symbols, Max, Rational, diff, integrate, simplify, Piecewise, S

x1, x2, a = symbols('x1 x2 a', real=True)
R = Rational

def relu(z):
    return Max(z, 0)

def tent(z):
    return relu(z) - 2 * relu(z - R(1, 2)) + relu(z - 1)

f = tent(x1) + tent(x2)

def fval(p1, p2):
    return f.subs({x1: p1, x2: p2})

fails = []
def check(name, cond):
    print(f"  [{'PASS' if cond else 'FAIL'}] {name}")
    if not cond:
        fails.append(name)

support1, support2 = [R(1, 4), 2], [R(1, 4), R(3, 4)]
D = [(p1, p2) for p1 in support1 for p2 in support2]

print("=== Ground truth on D (exact) ===")
for p in D:
    print(f"  f{p} = {fval(*p)}")
x1_causal = all(fval(support1[0], p2) - fval(support1[1], p2) == R(1, 4)
                for p2 in support2)
x2_inert = all(fval(p1, support2[0]) - fval(p1, support2[1]) == 0
               for p1 in support1)
check("x1 causal: every within-support x1 swap changes f by exactly 1/4", x1_causal)
check("x2 inert: every within-support x2 swap changes f by exactly 0", x2_inert)

# exact gradients via one-sided limits are unnecessary: all support points are
# interior to linear pieces; sympy diff + rewrite(Piecewise) evaluates exactly.
g1 = diff(f, x1).rewrite(Piecewise)
g2 = diff(f, x2).rewrite(Piecewise)

print("\n=== Method (a): gradient x input at certified inputs (x1 = 2) ===")
gxi_ok = True
for p2 in support2:
    A1 = simplify(2 * g1.subs({x1: 2, x2: p2}))
    A2 = simplify(p2 * g2.subs({x1: 2, x2: p2}))
    print(f"  at (2, {p2}):  A = ({A1}, {A2})")
    gxi_ok &= (A1 == 0) and (A2 != 0) and (abs(A2) > abs(A1))
check("grad x input: exactly 0 on causal x1, nonzero on inert x2, at BOTH "
      "certified inputs", gxi_ok)

print("\n=== Method (b): Integrated Gradients, zero baseline, exact path integral ===")
Xstar = (S(2), R(1, 4))
path = {x1: a * Xstar[0], x2: a * Xstar[1]}   # straight line from (0,0)
IG1 = simplify(Xstar[0] * integrate(g1.subs(path), (a, 0, 1)))
IG2 = simplify(Xstar[1] * integrate(g2.subs(path), (a, 0, 1)))
print(f"  at X* = {Xstar}:  IG = ({IG1}, {IG2})")
completeness = simplify(IG1 + IG2 - (fval(*Xstar) - fval(0, 0)))
check("IG completeness axiom holds exactly (sum = f(X*) - f(0))", completeness == 0)
check("IG assigns EXACTLY 0 to causal x1 and 1/4 to inert x2 at X*",
      IG1 == 0 and IG2 == R(1, 4))
check("both methods rank inert x2 strictly above causal x1 at X*",
      abs(IG2) > abs(IG1))

# interventional double-check at X*: x1 flip changes f, x2 flip does not
check("at X* itself: attested x1 flip changes f (1/4 -> 1/2); attested x2 "
      "flip changes nothing",
      fval(R(1, 4), R(1, 4)) - fval(*Xstar) == R(1, 4)
      and fval(2, R(3, 4)) == fval(*Xstar))

print()
if fails:
    print("FAIL:", fails); sys.exit(1)
print("PASS: certificate 2 verified — grad x input and IG (zero baseline) both "
      "assign exactly 0 to the sole causal feature and nonzero to the inert one "
      "at the certified inputs, with completeness intact.")
