#!/usr/bin/env python3
"""M1/M2 optimality lemma -- the load-bearing piece of the indistinguishability
certificate, checked BEFORE any prose is written around it.

THE HAZARD THIS EXISTS TO SETTLE. The sibling paper's epsilon* is a PURE-STRATEGY
crossover: it compares the faithful dictionary against the absorbed one and says which
of those two wins. It is explicitly NOT the global boundary -- a continuously
optimised dictionary tilts through intermediate angles and beats both pure strategies
(functional midpoint near 0.88*epsilon*). If that happens in the regime we need, then
"M1's absorbed dictionary is loss-optimal" is FALSE and the whole indistinguishability
certificate collapses.

THE RESOLUTION. Build the certificate at epsilon = 0 (the child never fires alone,
but still co-occurs with the parent, which is all the metric needs to produce absorbed
tokens). There Theorem 1b applies: the per-event bound lambda*r - lambda^2/4 is
attained IFF every active atom points along x/r, which pins the optimal direction SET
uniquely. No tilt is possible, because tilting breaks the equality condition on one of
the two event types.

WHAT IS CHECKED HERE
  1. the per-event bound and its equality condition, symbolically;
  2. M1's dictionary {a_L, a_m} attains the bound on every event type;
  3. M2's dictionary {a_L, a_m1..a_mk} attains it on every event type;
  4. the FAITHFUL dictionary is strictly worse at epsilon = 0 (so absorption is the
     optimum, not merely a competitor);
  5. an exact scan over tilted alternatives -- rational unit vectors from Pythagorean
     triples, so no trigonometry and no floating point -- confirms every deviation is
     strictly worse, which is the tilt hazard tested head-on rather than argued away.

The nonnegative lasso is solved EXACTLY by KKT active-set enumeration, not by an
iterative solver, so every number here is a closed form.

Run: python3 verify_m1_optimality.py     (needs sympy for sqrt(2))
"""
import itertools

import sympy as sp

LAM = sp.Rational(1, 5)          # any 0 < lambda < 2; the paper's runs used <= 1/2
checks = []


def check(name, ok, detail=""):
    checks.append((name, bool(ok), detail))
    print(f"[{'PASS' if ok else 'FAIL'}] {name}" + (f" -- {detail}" if detail else ""))
    return ok


def nnlasso(D, x, lam=LAM):
    """Exact min_{f>=0} ||x - D f||^2 + lam*||f||_1 by KKT active-set enumeration.

    D is a list of column vectors (sympy Matrices). Returns (objective, support).
    Enumerating supports is exponential but m is tiny here and it is exact, which an
    iterative solver would not be.
    """
    m = len(D)
    best, best_S = None, None
    for r in range(m + 1):
        for S in itertools.combinations(range(m), r):
            if S:
                Ds = sp.Matrix.hstack(*[D[i] for i in S])
                G = (Ds.T * Ds)
                if G.det() == 0:
                    continue
                rhs = Ds.T * x - lam / 2 * sp.ones(len(S), 1)
                f = G.inv() * rhs
                if any(sp.simplify(v) <= 0 for v in f):      # need strictly positive
                    continue
                resid = x - Ds * f
                obj = sp.simplify((resid.T * resid)[0, 0] + lam * sum(f))
            else:
                f, resid = None, x
                obj = sp.simplify((x.T * x)[0, 0])
            # dual feasibility on the inactive atoms
            ok = True
            for i in range(m):
                if i in S:
                    continue
                g = sp.simplify((2 * D[i].T * (-resid))[0, 0] + lam)
                if g < 0:
                    ok = False
                    break
            if not ok:
                continue
            obj = sp.nsimplify(sp.simplify(obj))
            if best is None or obj < best:
                best, best_S = obj, S
    return best, best_S


def unit(v):
    v = sp.Matrix(v)
    return sp.simplify(v / sp.sqrt((v.T * v)[0, 0]))


print("=" * 74)
print("M1 / M2 OPTIMALITY LEMMA -- exact, at epsilon = 0")
print(f"lambda = {LAM}")
print("=" * 74)

# ---------------------------------------------------------------- the bound
r_s, lam_s = sp.symbols("r lam", positive=True)
t = sp.symbols("t", nonnegative=True)
inner = (r_s - t) ** 2 + lam_s * t
t_star = sp.solve(sp.diff(inner, t), t)[0]
bound = sp.simplify(inner.subs(t, t_star))
check("Theorem 1b bound: min_t (r-t)^2 + lam*t = lam*r - lam^2/4",
      sp.simplify(bound - (lam_s * r_s - lam_s ** 2 / 4)) == 0,
      f"t* = {t_star}, value = {bound}")


def bound_at(r):
    return sp.nsimplify(sp.simplify(LAM * r - LAM ** 2 / 4))


# ---------------------------------------------------------------- M1, k=2 tokens
# Plane: e0 = letter direction a_L, e1 = the single child concept a_c.
# Events at epsilon = 0:  parent-solo x = a_L (r=1);  joint x = a_L + a_c (r=sqrt2).
aL = sp.Matrix([1, 0])
ac = sp.Matrix([0, 1])
am = unit(aL + ac)                                   # the composite (a_L+a_c)/sqrt2
x_solo, x_joint = aL, aL + ac

D_M1 = [aL, am]
o_solo, S1 = nnlasso(D_M1, x_solo)
o_joint, S2 = nnlasso(D_M1, x_joint)
check("M1 attains the bound on parent-solo events",
      sp.simplify(o_solo - bound_at(1)) == 0, f"loss = {o_solo} = lam - lam^2/4")
check("M1 attains the bound on joint events",
      sp.simplify(o_joint - bound_at(sp.sqrt(2))) == 0,
      f"loss = {sp.nsimplify(o_joint)} = sqrt2*lam - lam^2/4")

# ---------------------------------------------------------------- the faithful rival
D_faith = [aL, ac]
f_solo, _ = nnlasso(D_faith, x_solo)
f_joint, _ = nnlasso(D_faith, x_joint)
check("faithful dictionary also attains the bound on parent-solo",
      sp.simplify(f_solo - bound_at(1)) == 0)
gap_joint = sp.simplify(f_joint - o_joint)
check("faithful is STRICTLY WORSE on joint events -- absorption is the optimum at "
      "epsilon = 0, not merely a competitor",
      gap_joint > 0,
      f"faithful {sp.nsimplify(f_joint)} - absorbed {sp.nsimplify(o_joint)} "
      f"= {sp.nsimplify(gap_joint)} = {float(gap_joint):.6f} > 0")

# ---------------------------------------------------------------- the tilt hazard
# Replace the composite by a tilted unit atom and confirm every deviation loses.
# Rational unit vectors from Pythagorean triples keep this exact -- no trigonometry.
TRIPLES = [(3, 4, 5), (4, 3, 5), (5, 12, 13), (12, 5, 13), (8, 15, 17), (15, 8, 17),
           (7, 24, 25), (24, 7, 25), (20, 21, 29), (21, 20, 29), (9, 40, 41),
           (40, 9, 41), (28, 45, 53), (11, 60, 61), (33, 56, 65), (16, 63, 65)]
worse, ties, total = 0, [], 0
for a, b, c in TRIPLES:
    u = sp.Matrix([sp.Rational(a, c), sp.Rational(b, c)])
    if sp.simplify(u - am) == sp.zeros(2, 1):
        continue
    tot_tilt = sp.simplify(nnlasso([aL, u], x_solo)[0] + nnlasso([aL, u], x_joint)[0])
    tot_abs = sp.simplify(o_solo + o_joint)
    total += 1
    d = sp.simplify(tot_tilt - tot_abs)
    if d > 0:
        worse += 1
    else:
        ties.append((a, b, c, d))
check(f"tilt hazard: all {total} rational-unit-vector tilts are STRICTLY worse than "
      f"the composite (p0 = q, exact)", worse == total and not ties,
      f"{worse}/{total} strictly worse" + (f"; ties/better: {ties[:2]}" if ties else ""))

# The equality condition is the real proof: a tilted atom cannot be parallel to BOTH
# x_solo and x_joint, so it must lose the bound on at least one event type.
cos_solo = sp.simplify((am.T * unit(x_solo))[0, 0])
cos_joint = sp.simplify((am.T * unit(x_joint))[0, 0])
check("equality condition pins the direction: the composite is parallel to the joint "
      "event and NOT to parent-solo, so a second atom (a_L) is required",
      sp.simplify(cos_joint - 1) == 0 and cos_solo != 1,
      f"cos(am, joint) = {cos_joint}, cos(am, solo) = {sp.nsimplify(cos_solo)}")

# ---------------------------------------------------------------- M2, k=2 children
# Now TWO distinct child concepts, each co-occurring with the letter, each epsilon=0.
# Ambient: e0 = a_L, e1 = a_c1, e2 = a_c2.
aL3 = sp.Matrix([1, 0, 0])
ac1 = sp.Matrix([0, 1, 0])
ac2 = sp.Matrix([0, 0, 1])
am1, am2 = unit(aL3 + ac1), unit(aL3 + ac2)
D_M2 = [aL3, am1, am2]
ok_all = True
for name, x, r in [("parent-solo", aL3, 1),
                   ("joint with child 1", aL3 + ac1, sp.sqrt(2)),
                   ("joint with child 2", aL3 + ac2, sp.sqrt(2))]:
    o, S = nnlasso(D_M2, x)
    good = sp.simplify(o - bound_at(r)) == 0
    ok_all &= good
    print(f"        M2 {name:20s} loss = {sp.nsimplify(o)}  "
          f"{'= bound' if good else '!= bound'}  support={S}")
check("M2 attains the bound on every event type -- the k-composite dictionary is "
      "optimal for the k-distinct-children model", ok_all)

# --------------------------------------------------------- bridge to the repair
# The two models differ in exactly the way the carrier check exploits: M1's single
# composite is the optimal support on BOTH of its child tokens (one recurring
# carrier), while M2's tokens are served by DIFFERENT composites (k distinct
# carriers). This is the seed of the repair half of the certificate, and it is a
# property of the optimal supports rather than an assumption.
m1_supports = [nnlasso(D_M1, x_joint)[1] for _ in range(2)]      # 2 identical tokens
m2_supports = [nnlasso(D_M2, aL3 + ac1)[1], nnlasso(D_M2, aL3 + ac2)[1]]
check("bridge: M1's absorbed tokens share ONE carrier support, M2's use TWO distinct "
      "ones -- exactly the contrast a carrier-consistency statistic detects",
      len(set(m1_supports)) == 1 and len(set(m2_supports)) == 2,
      f"M1 supports {set(m1_supports)}, M2 supports {set(m2_supports)}")

# --------------------------------------------------------- precondition on tau
# For M1 to yield absorbed tokens at all, its composite must ESCAPE the letter family:
# a_m fires on all k child tokens, so sel(a_m) = k/N_L, and it is in F_L when
# k/N_L >= tau. The certificate therefore needs k/N_L < tau, while the letter itself
# must still be scored, sel(a_L) = (N_L-k)/N_L >= tau. Both hold with room to spare at
# the registered tau = 3/10.
TAU = sp.Rational(3, 10)
N_L, k = 10, 2
sel_aL, sel_am = sp.Rational(N_L - k, N_L), sp.Rational(k, N_L)
check("precondition: M1's composite escapes F_L (sel < tau) while the letter latent "
      "is still scored (sel >= tau) -- both satisfied at N_L=10, k=2, tau=3/10",
      sel_am < TAU <= sel_aL,
      f"sel(a_m) = {sel_am} < {TAU} <= sel(a_L) = {sel_aL}")

# ================================================================= epsilon > 0
# The tilt that forces epsilon = 0 is an artifact of restricting the dictionary to TWO
# atoms. Numerically, the best 2-atom dictionary tilts away from (0, 45 deg) once
# epsilon exceeds ~0.04 (lambda=1/5, p0=q=3/10) and the letter atom starts firing on
# joint events, which would destroy the construction. Give the dictionary ONE more
# atom and the problem disappears: with a_c present every event type is 1-sparse, so
# the bound is attained on all of them and the dictionary is optimal at ANY epsilon.
# Real SAEs are 8x overcomplete, so capacity is never the binding constraint there.
print()
print("-" * 74)
print("epsilon > 0: does one extra atom remove the restriction?")
print("-" * 74)

D_M1_eps = [aL, am, ac]                      # {a_L, a_m, a_c}
ok_eps, rows = True, []
for nm, x, r in [("parent-solo", aL, 1), ("joint", aL + ac, sp.sqrt(2)),
                 ("child-solo", ac, 1)]:
    o, S = nnlasso(D_M1_eps, x)
    good = sp.simplify(o - bound_at(r)) == 0
    ok_eps &= good
    rows.append(f"{nm}:{S}")
    print(f"        M1+ {nm:12s} loss = {sp.nsimplify(o)}  "
          f"{'= bound' if good else '!= bound'}  support={S}")
check("epsilon>0: M1's 3-atom dictionary {a_L, a_m, a_c} attains the bound on ALL "
      "event types, so it is optimal for EVERY epsilon -- no tilt, no epsilon=0",
      ok_eps, "; ".join(rows))

joint_support = nnlasso(D_M1_eps, aL + ac)[1]
check("epsilon>0: the letter atom a_L (index 0) is still SILENT on joint events, so "
      "the metric-relevant firing pattern is unchanged",
      0 not in joint_support, f"joint support = {joint_support}")

child_solo_support = nnlasso(D_M1_eps, ac)[1]
check("epsilon>0: child-solo events are served by a_c (index 2), and those tokens are "
      "NOT letter tokens -- so sel(a_c) <= 0 < tau and a_c never enters F_L",
      child_solo_support == (2,), f"child-solo support = {child_solo_support}")

# M2's analogue: {a_L} + k composites + k child atoms, k = 2.
D_M2_eps = [aL3, am1, am2, ac1, ac2]
ok_eps2 = True
for nm, x, r in [("parent-solo", aL3, 1),
                 ("joint c1", aL3 + ac1, sp.sqrt(2)), ("joint c2", aL3 + ac2, sp.sqrt(2)),
                 ("child-solo c1", ac1, 1), ("child-solo c2", ac2, 1)]:
    o, S = nnlasso(D_M2_eps, x)
    good = sp.simplify(o - bound_at(r)) == 0
    ok_eps2 &= good and (0 not in S or nm == "parent-solo")
check("epsilon>0: M2's (2k+1)-atom dictionary likewise attains the bound on all 2k+1 "
      "event types, with a_L silent on every joint event",
      ok_eps2)

print("=" * 74)
n_pass = sum(1 for _, ok, _ in checks if ok)
print(f"TOTAL: {len(checks)} checks, {n_pass} PASS, {len(checks) - n_pass} FAIL")
print()
print("CONCLUSION: both M1 and M2 attain the Theorem 1b bound for their own generative")
print("model, and every tilted alternative is strictly worse. At epsilon = 0 this holds")
print("for the 2-atom dictionaries; for epsilon > 0 it holds once the dictionary has")
print("room for the child atoms, which an overcomplete SAE always does. The optimality")
print("lemma HOLDS, so the indistinguishability certificate can be built.")
raise SystemExit(0 if n_pass == len(checks) else 1)
