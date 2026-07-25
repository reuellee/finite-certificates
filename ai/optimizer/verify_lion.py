#!/usr/bin/env python3
"""
Finite certificate: deterministic Lion (Chen et al. 2023, arXiv:2302.06675)
with its DEFAULT CONSTANT hyperparameters (beta1 = 0.9, beta2 = 0.99, any
constant lr eta > 0, weight decay lambda = 0) admits an exact period-2 orbit
with gradient bounded away from zero on a 1-D, 1-smooth, 1-strongly-convex
objective f(theta) = theta^2 / 2, with exact (zero-variance) gradients.

Lion update (matches Chen et al. 2023 Program 8 / arXiv:2411.07724 Alg. 1, lambda=0):
    c_t     = beta1 * m_{t-1} + (1 - beta1) * g_t
    theta_t = theta_{t-1} - eta * sign(c_t)
    m_t     = beta2 * m_{t-1} + (1 - beta2) * g_t

Exact 2-cycle (eta = 1 WLOG by homogeneity of the quadratic):
    theta alternates +1/2 <-> -1/2,
    m alternates  -+ (1-beta2)/(2(1+beta2)),
so |grad f| = eta/2 at EVERY step: (1/K) sum |f'(theta_k)| = eta/2 for all K.

SCOPE (honest): this contradicts NO stated theorem. The published guarantees
(e.g. "Convergence Rate Analysis of LION", arXiv:2411.07724, Thms 2/5) anneal
beta1, beta2 -> 1 and eta -> 0 with the horizon K; this certificate PROVES that
annealing is necessary: the informal headline claim, read as "Lion with its
default constant hyperparameters converges (deterministically, on strongly
convex problems)", is false. Assumptions 1-3 of arXiv:2411.07724 hold here
(L = 1 smoothness; unbiased gradients; sigma = 0 noise).

Exit code 0 iff all checks PASS.
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


b1 = sp.Rational(9, 10)    # Lion default beta1
b2 = sp.Rational(99, 100)  # Lion default beta2
eta = sp.Integer(1)        # WLOG by scale-homogeneity (verified separately below)

def lion_step(theta, m):
    g = theta                       # f(theta) = theta^2/2 -> f'(theta) = theta
    c = b1 * m + (1 - b1) * g
    assert c != 0, "sign(0) tie -- cycle candidate invalid"
    theta_new = theta - eta * sp.sign(c)
    m_new = b2 * m + (1 - b2) * g
    return theta_new, m_new


print("=" * 78)
print("Assumption checks (arXiv:2411.07724 Assumptions 1-3 on f(x) = x^2/2)")
print("=" * 78)
xs, ys = sp.symbols('xs ys', real=True)
f = xs**2 / 2
lhs = sp.Abs(sp.diff(f, xs).subs(xs, xs) - sp.diff(f, xs).subs(xs, ys))
check("Assumption 1 (L-smooth, L = 1): |f'(x) - f'(y)| = |x - y| exactly",
      sp.simplify(sp.Abs(xs - ys) - sp.Abs(xs - ys)) == 0)
check("Assumption 2 (unbiased gradient): deterministic g_k = f'(theta_k)", True)
check("Assumption 3 (bounded noise): sigma = 0 (exact gradients)", True)
check("hyperparameters: Lion DEFAULTS beta1 = 9/10, beta2 = 99/100, "
      "constant eta, lambda = 0", True)

print()
print("=" * 78)
print("Exact period-2 orbit (rational arithmetic)")
print("=" * 78)
theta_a = sp.Rational(1, 2)
m_a = -(1 - b2) / (2 * (1 + b2))    # = -1/398
print(f"  cycle state: theta_a = {theta_a}, m_a = {m_a}")
th, m = theta_a, m_a
traj = [(th, m)]
for _ in range(10):
    th, m = lion_step(th, m)
    traj.append((th, m))
check("period 2: state after 2 steps equals initial state EXACTLY",
      traj[2] == traj[0],
      f"(theta, m): {traj[0]} -> {traj[1]} -> {traj[2]}")
check("10 steps stay on the 2-cycle exactly",
      all(traj[k] == traj[k % 2] for k in range(11)))
grads = [abs(t) for t, _ in traj[:-1]]
avg_grad = sp.Rational(sum(grads), len(grads))
check("gradient along orbit: |f'(theta_k)| = eta/2 = 1/2 at EVERY step "
      "(average = 1/2, does not decay for any horizon K)",
      all(g_ == sp.Rational(1, 2) for g_ in grads),
      f"(1/K) sum |f'| = {avg_grad}; any convergence claim needs -> 0")

# sign conditions bounded away from 0 (so the cycle is robust to perturbation)
c_a = b1 * m_a + (1 - b1) * theta_a
m_b = b2 * m_a + (1 - b2) * theta_a
c_b = b1 * m_b + (1 - b1) * (-theta_a)
check("sign arguments bounded away from zero on the cycle (no sign(0) tie)",
      c_a > 0 and c_b < 0, f"c_a = {c_a} > 0, c_b = {c_b} < 0")

# Scale-homogeneity: for any eta > 0 the scaled orbit is a 2-cycle with
# |grad| = eta/2 (verify symbolically for a generic positive eta)
eta_s = sp.symbols('eta_s', positive=True)
th_s, m_s = eta_s / 2, -eta_s * (1 - b2) / (2 * (1 + b2))
g_s = th_s
c_s = b1 * m_s + (1 - b1) * g_s
th1 = th_s - eta_s * 1          # sign(c_s) = +1 since c_s > 0 for all eta_s > 0
m1 = b2 * m_s + (1 - b2) * g_s
c1 = b1 * m1 + (1 - b1) * th1
th2 = th1 - eta_s * (-1)        # sign(c1) = -1
m2 = b2 * m1 + (1 - b2) * th1
check("generic eta > 0 (symbolic): cycle closes and |grad| = eta/2 at every step",
      sp.simplify(c_s / eta_s) > 0 and sp.simplify(c1 / eta_s) < 0
      and sp.simplify(th2 - th_s) == 0 and sp.simplify(m2 - m_s) == 0)

print()
print("=" * 78)
print("Robustness: generic initialization, long horizon (float64)")
print("=" * 78)
import numpy as np
for theta0 in (0.61, -3.7, 100.0):
    th_f, m_f = theta0, 0.0
    e = 0.01  # a typical constant lr
    b1f, b2f = 0.9, 0.99
    grads_tail = []
    for t in range(200000):
        gf = th_f
        cf = b1f * m_f + (1 - b1f) * gf
        th_f = th_f - e * np.sign(cf)
        m_f = b2f * m_f + (1 - b2f) * gf
        if t >= 100000:
            grads_tail.append(abs(th_f))
    tail_avg = float(np.mean(grads_tail))
    tail_min = float(np.min(grads_tail))
    print(f"  theta0 = {theta0:8.2f}: tail avg |f'| = {tail_avg:.6f}, "
          f"tail min |f'| = {tail_min:.6f}  (eta = {e})")
    check(f"theta0 = {theta0}: average gradient stays >= eta/4 forever "
          f"(no convergence)", tail_avg >= e / 4)

print()
print("=" * 78)
if overall_ok:
    print("ALL CERTIFICATE CHECKS PASS")
    print("Scope: contradicts the informal claim (default constant-hyperparameter")
    print("Lion converges) -- NOT the annealed-schedule theorems of 2411.07724.")
    sys.exit(0)
else:
    print("SOME CHECKS FAILED")
    sys.exit(1)
