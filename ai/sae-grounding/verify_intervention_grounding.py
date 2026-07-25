#!/usr/bin/env python3
"""Exact-arithmetic verifier for "The Intervention-Grounding Gap" (SAE
identifiability series, 2026-07-25), reconstructed independently from the
note's stated rational parameters by the reviewer.

Checks (all exact Fraction arithmetic, no floats):
  1. Forward SCM  M_{P->C}: P~Bern(1/2), Pr(C=1|P=0)=1/4, Pr(C=1|P=1)=1/2
     reproduces the Table 1 joint exactly.
  2. Reverse SCM  M_{C->P}: C~Bern(3/8), Pr(P=1|C=0)=2/5, Pr(P=1|C=1)=2/3
     reproduces the same joint exactly (=> identical law of X=(P,C), hence
     identical inputs to any SAE learner and identical labels).
  3. Table 1 is strictly positive (blocks off-support objections).
  4. Internal settings set(X_P=p), set(X_C=c) give the Table 2 column-2
     expected scores under BOTH models (computed from each model's own
     factorization, not from the shared table).
  5. Semantic do-distributions: full distributions and expected scores under
     do(P=p), do(C=c) in each model match Table 2 and DIFFER between models
     for all four target settings.
  6. Exhaustive: all 4^4 = 256 deterministic post-X maps T give identical
     pushforward laws of (X'=T(X), Y'=h(X')) under both models, each
     computed from its own factorization.
  7. Stochastic post-X kernels: exact rational kernels (including a
     non-degenerate mixed one) give identical pushforwards.
  8. Adaptive 2-round protocol (exact transcript law): round-2 map chosen as
     a function of the round-1 observation; complete transcript laws under
     both models compared exactly.
  9. Absorption-wall corollary at p0=q=1/4 and at a second generic point
     (p0=1/8, q=1/3): both factorizations reproduce the wall joint;
     Pr(C=1|do(P=0)) = 0 (forward) vs q (reverse).
 10. Structural sanity: internal set(X_P) coincides with the REVERSE model's
     do(P), and internal set(X_C) with the FORWARD model's do(C) — i.e. the
     internal edit agrees with whichever model makes the target a root,
     so internal experiments cannot reveal which ontology generated the data.

Exit code 0 iff every check passes.
"""

from fractions import Fraction as F
from itertools import product
import sys

STATES = [(0, 0), (1, 0), (0, 1), (1, 1)]  # (P, C); X = (P, C) invertibly

failures = []


def check(name, ok, detail=""):
    status = "PASS" if ok else "FAIL"
    print(f"[{status}] {name}" + (f"  {detail}" if detail and not ok else ""))
    if not ok:
        failures.append((name, detail))


def h(x):
    """Downstream score Y = P + 2C on the represented state."""
    p, c = x
    return p + 2 * c


# ---------------------------------------------------------------- Table 1
TABLE1 = {(0, 0): F(3, 8), (1, 0): F(1, 4), (0, 1): F(1, 8), (1, 1): F(1, 4)}


def forward_joint(pP1, c_given_p):
    """Joint from P->C factorization. c_given_p[p] = Pr(C=1|P=p)."""
    j = {}
    for p, c in STATES:
        pp = pP1 if p == 1 else 1 - pP1
        pc = c_given_p[p] if c == 1 else 1 - c_given_p[p]
        j[(p, c)] = pp * pc
    return j


def reverse_joint(pC1, p_given_c):
    """Joint from C->P factorization. p_given_c[c] = Pr(P=1|C=c)."""
    j = {}
    for p, c in STATES:
        pc = pC1 if c == 1 else 1 - pC1
        pp = p_given_c[c] if p == 1 else 1 - p_given_c[c]
        j[(p, c)] = pc * pp
    return j


# Note's parameters (section 4.2)
FWD = dict(pP1=F(1, 2), c_given_p={0: F(1, 4), 1: F(1, 2)})
REV = dict(pC1=F(3, 8), p_given_c={0: F(2, 5), 1: F(2, 3)})

J_fwd = forward_joint(**FWD)
J_rev = reverse_joint(**REV)

check("1. forward factorization reproduces Table 1", J_fwd == TABLE1,
      f"got {J_fwd}")
check("2. reverse factorization reproduces Table 1", J_rev == TABLE1,
      f"got {J_rev}")
check("2b. joints of X=(P,C) identical across models (incl. labels)",
      J_fwd == J_rev)
check("3. strict positivity of the shared joint",
      all(v > 0 for v in TABLE1.values()) and sum(TABLE1.values()) == 1)


# ------------------------------------------------- internal settings (4.3)
def internal_set(joint, coord, val):
    """set(X_coord=val): overwrite one represented coordinate, keep the other
    at its observational draw. Returns law of X' and E[Y]."""
    law = {}
    for (p, c), pr in joint.items():
        x2 = (val, c) if coord == "P" else (p, val)
        law[x2] = law.get(x2, F(0)) + pr
    ey = sum(pr * h(x) for x, pr in law.items())
    return law, ey

TABLE2_INTERNAL = {("P", 0): F(3, 4), ("P", 1): F(7, 4),
                   ("C", 0): F(1, 2), ("C", 1): F(5, 2)}

for (coord, val), expect in TABLE2_INTERNAL.items():
    lf, ef = internal_set(J_fwd, coord, val)
    lr, er = internal_set(J_rev, coord, val)
    check(f"4. internal set(X_{coord}={val}): both models E[Y]={expect}",
          ef == er == expect and lf == lr, f"fwd {ef}, rev {er}")


# ------------------------------------------------- semantic do-operations
def do_forward(model, coord, val):
    """Semantic surgery in M_{P->C}: replace a structural equation and
    regenerate descendants."""
    pP1, cg = model["pP1"], model["c_given_p"]
    law = {}
    if coord == "P":                       # C regenerated from Pr(C|P=val)
        for c in (0, 1):
            pc = cg[val] if c == 1 else 1 - cg[val]
            law[(val, c)] = pc
    else:                                  # P is upstream: keeps its marginal
        for p in (0, 1):
            pp = pP1 if p == 1 else 1 - pP1
            law[(p, val)] = pp
    return law, sum(pr * h(x) for x, pr in law.items())


def do_reverse(model, coord, val):
    """Semantic surgery in M_{C->P}."""
    pC1, pg = model["pC1"], model["p_given_c"]
    law = {}
    if coord == "C":                       # P regenerated from Pr(P|C=val)
        for p in (0, 1):
            pp = pg[val] if p == 1 else 1 - pg[val]
            law[(p, val)] = pp
    else:                                  # C is upstream: keeps its marginal
        for c in (0, 1):
            pc = pC1 if c == 1 else 1 - pC1
            law[(val, c)] = pc
    return law, sum(pr * h(x) for x, pr in law.items())

TABLE2_DO = {  # (coord, val): (E[Y] in P->C, E[Y] in C->P)
    ("P", 0): (F(1, 2), F(3, 4)),
    ("P", 1): (F(2), F(7, 4)),
    ("C", 0): (F(1, 2), F(2, 5)),
    ("C", 1): (F(5, 2), F(8, 3)),
}

for (coord, val), (e_f_exp, e_r_exp) in TABLE2_DO.items():
    law_f, e_f = do_forward(FWD, coord, val)
    law_r, e_r = do_reverse(REV, coord, val)
    check(f"5. do({coord}={val}): P->C mean {e_f_exp}, C->P mean {e_r_exp}",
          e_f == e_f_exp and e_r == e_r_exp, f"got {e_f}, {e_r}")
    check(f"5b. do({coord}={val}): semantic do-distributions DIFFER",
          law_f != law_r and e_f != e_r,
      f"laws equal? {law_f == law_r}")

# 10. structural sanity: internal edit == do() in the model where the target
# coordinate is a CHILD (has no descendants; its root parent keeps its
# marginal, exactly as the internal edit leaves it), for every target:
# set(X_P) matches do(P) in M_{C->P}; set(X_C) matches do(C) in M_{P->C}.
for val in (0, 1):
    _, ei = internal_set(TABLE1, "P", val)
    _, er = do_reverse(REV, "P", val)
    check(f"10. internal set(X_P={val}) == reverse-model do(P={val})", ei == er)
    _, ei = internal_set(TABLE1, "C", val)
    _, ef = do_forward(FWD, "C", val)
    check(f"10. internal set(X_C={val}) == forward-model do(C={val})", ei == ef)


# --------------------------------------- 6. all 256 deterministic post-X maps
def pushforward(joint, T):
    """Law of (X'=T(X), Y'=h(T(X)))."""
    law = {}
    for x, pr in joint.items():
        key = (T[x], h(T[x]))
        law[key] = law.get(key, F(0)) + pr
    return law

n_maps, all_agree = 0, True
for images in product(STATES, repeat=4):
    T = dict(zip(STATES, images))
    if pushforward(J_fwd, T) != pushforward(J_rev, T):
        all_agree = False
        break
    n_maps += 1
check(f"6. all 256 deterministic post-X maps give identical (X',Y') laws",
      all_agree and n_maps == 256, f"checked {n_maps}")


# ----------------------------------------- 7. stochastic post-X kernels
def kernel_pushforward(joint, K):
    """K: state -> dict(state -> prob). Law of (X', Y')."""
    law = {}
    for x, pr in joint.items():
        for x2, kp in K[x].items():
            key = (x2, h(x2))
            law[key] = law.get(key, F(0)) + pr * kp
    return law

K1 = {  # non-degenerate mixed kernel with distinct rational rows
    (0, 0): {(0, 0): F(1, 3), (1, 1): F(2, 3)},
    (1, 0): {(1, 0): F(1, 7), (0, 1): F(4, 7), (1, 1): F(2, 7)},
    (0, 1): {(0, 0): F(5, 11), (0, 1): F(6, 11)},
    (1, 1): {(0, 0): F(1, 2), (1, 0): F(1, 4), (0, 1): F(1, 8),
             (1, 1): F(1, 8)},
}
K2 = {x: ({(1, 0): F(1)} if x == (1, 0)                       # steering-style
          else {(1, 0): F(9, 10), x: F(1, 10)}) for x in STATES}
for i, K in enumerate((K1, K2), 1):
    assert all(sum(row.values()) == 1 for row in K.values())
    check(f"7. stochastic kernel #{i}: identical pushforward laws",
          kernel_pushforward(J_fwd, K) == kernel_pushforward(J_rev, K))


# -------------------------------- 8. adaptive 2-round exact transcript law
def transcript_law(joint):
    """Round 1: draw X1~joint, apply T1 = swap map, observe o1=(T1(X1), Y1).
    Round 2: policy picks a round-2 deterministic map depending on o1
    (adaptive), fresh independent X2~joint, observe o2. Returns exact joint
    law of the transcript (o1, o2)."""
    T1 = {(0, 0): (1, 1), (1, 0): (0, 1), (0, 1): (1, 0), (1, 1): (0, 0)}
    Ta = {x: (x[0], 1) for x in STATES}          # set C-coordinate to 1
    Tb = {x: (0, x[1]) for x in STATES}          # set P-coordinate to 0
    law = {}
    for x1, pr1 in joint.items():
        o1 = (T1[x1], h(T1[x1]))
        T2 = Ta if o1[1] >= 2 else Tb            # adaptive choice on Y1
        for x2, pr2 in joint.items():
            o2 = (T2[x2], h(T2[x2]))
            key = (o1, o2)
            law[key] = law.get(key, F(0)) + pr1 * pr2
    return law

check("8. adaptive 2-round protocol: identical exact transcript laws",
      transcript_law(J_fwd) == transcript_law(J_rev))


# ------------------------------------------- 9. absorption-wall corollary
def wall_check(p0, q, tag):
    wall = {(0, 0): 1 - p0 - q, (1, 0): p0, (1, 1): q, (0, 1): F(0)}
    jf = forward_joint(p0 + q, {0: F(0), 1: q / (p0 + q)})
    jr = reverse_joint(q, {0: p0 / (1 - q), 1: F(1)})
    check(f"9. wall {tag}: both factorizations reproduce the wall joint",
          jf == wall and jr == wall, f"fwd {jf}, rev {jr}")
    # do(P=0): forward forces C=0; reverse leaves C~Bern(q)
    lf, _ = do_forward(dict(pP1=p0 + q,
                            c_given_p={0: F(0), 1: q / (p0 + q)}), "P", 0)
    lr, _ = do_reverse(dict(pC1=q,
                            p_given_c={0: p0 / (1 - q), 1: F(1)}), "P", 0)
    pc1_f = lf.get((0, 1), F(0))
    pc1_r = lr.get((0, 1), F(0))
    check(f"9b. wall {tag}: Pr(C=1|do(P=0)) = 0 (fwd) vs q={q} (rev)",
          pc1_f == 0 and pc1_r == q and pc1_f != pc1_r,
          f"got {pc1_f}, {pc1_r}")

wall_check(F(1, 4), F(1, 4), "p0=q=1/4")
wall_check(F(1, 8), F(1, 3), "p0=1/8, q=1/3")


# ---- 11. REVIEWER EXTENSION (beyond the note's spec): swap-symmetric witness
# Joint invariant under exchanging P and C:
#   Pr(0,0)=Pr(1,1)=3/8, Pr(0,1)=Pr(1,0)=1/8  (dependent, strictly positive).
# Any canonical model-selection rule computed from the observational law and
# equivariant under the coordinate swap must score both factorizations
# equally, so no such rule can prefer a causal direction — yet the semantic
# do-distributions still differ. This pre-empts the canonical-choice
# (support-reducibility-style) objection that blocked the sibling note.
SYM = {(0, 0): F(3, 8), (1, 0): F(1, 8), (0, 1): F(1, 8), (1, 1): F(3, 8)}
SFWD = dict(pP1=F(1, 2), c_given_p={0: F(1, 4), 1: F(3, 4)})
SREV = dict(pC1=F(1, 2), p_given_c={0: F(1, 4), 1: F(3, 4)})
check("11. symmetric witness: joint is swap-invariant, dependent, positive",
      all(SYM[(p, c)] == SYM[(c, p)] for p, c in STATES)
      and SYM[(1, 1)] != (SYM[(1, 0)] + SYM[(1, 1)]) *
                         (SYM[(0, 1)] + SYM[(1, 1)])
      and all(v > 0 for v in SYM.values()) and sum(SYM.values()) == 1)
check("11b. symmetric witness: both factorizations reproduce it "
      "(and are mirror images, so no swap-equivariant rule selects one)",
      forward_joint(**SFWD) == SYM and reverse_joint(**SREV) == SYM)
sl_f, _ = do_forward(SFWD, "P", 0)
sl_r, _ = do_reverse(SREV, "P", 0)
check("11c. symmetric witness: Pr(C=1|do(P=0)) = 1/4 (fwd) vs 1/2 (rev)",
      sl_f.get((0, 1)) == F(1, 4) and sl_r.get((0, 1)) == F(1, 2))


# ---------------------------------------------------------------- summary
print()
if failures:
    print(f"RESULT: {len(failures)} CHECK(S) FAILED")
    for name, detail in failures:
        print(f"  - {name}: {detail}")
    sys.exit(1)
print("RESULT: ALL EXACT CHECKS PASSED (Fraction arithmetic throughout; "
      "no floats)")
sys.exit(0)
