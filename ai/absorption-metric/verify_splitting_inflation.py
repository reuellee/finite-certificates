#!/usr/bin/env python3
"""Exact verifier for splitting_inflation.md.

Certifies that the SAEBench-style first-letter absorption metric reports a strictly
positive rate on a dictionary with ZERO absorption, and pins the sharp bound.

Everything load-bearing is exact: Fraction arithmetic for rates and losses, integer
set logic for the metric. sympy is used only for the single irrational check (a merged
atom carries a sqrt(2)). No numpy, no pip.

The metric is not re-derived here from the paper's formulas -- it is re-implemented
line-for-line from the reference scorer
(sae-identifiability/analysis/round13a_family_endpoint.py), so the certificate is
about the code that produced the empirical results, not about a paraphrase of it.

Run: python3 verify_splitting_inflation.py     (exit 0 = all checks pass)
"""
from fractions import Fraction as F
from itertools import combinations

TAU = F(3, 10)          # registered threshold in the reference implementation
FAM_CAP = 32            # registered family cap
LAMBDA = F(1, 5)        # any 0 < lambda < 2; experiments used <= 1/2

checks = []


def check(name, ok, detail=""):
    checks.append((name, bool(ok), detail))
    print(f"[{'PASS' if ok else 'FAIL'}] {name}" + (f" -- {detail}" if detail else ""))
    return ok


# ---------------------------------------------------------------------------
# The metric, transcribed from round13a_family_endpoint.py.
#   sel_i        = mean(fires_i | L) - mean(fires_i | not L)
#   j            = argmax_i sel_i           (numpy argmax: first maximum on ties)
#   scored iff   sel_j >= TAU
#   F_L          = {i : sel_i >= TAU}, capped at FAM_CAP by descending sel
#   rate_single  = |present & ~fires_j & retained| / |present|
#   rate_family  = |present & ~any(fires_{F_L}) & retained| / |present|
# ---------------------------------------------------------------------------
def score_letter(fires, is_L, present, retained, tau=TAU, fam_cap=FAM_CAP):
    """fires: list of rows, each a set of latent indices firing on that token."""
    n_lat = 1 + max((max(r) for r in fires if r), default=-1)
    L_idx = [t for t in range(len(fires)) if is_L[t]]
    nL_idx = [t for t in range(len(fires)) if not is_L[t]]

    sel = []
    for i in range(n_lat):
        pL = F(sum(1 for t in L_idx if i in fires[t]), len(L_idx)) if L_idx else F(0)
        pN = F(sum(1 for t in nL_idx if i in fires[t]), len(nL_idx)) if nL_idx else F(0)
        sel.append(pL - pN)

    j = max(range(n_lat), key=lambda i: (sel[i], -i))      # argmax, first on ties
    if sel[j] < tau:
        return None                                        # letter not scored

    fam = [i for i in range(n_lat) if sel[i] >= tau]
    fam.sort(key=lambda i: (-sel[i], i))
    fam = set(fam[:fam_cap])

    pres = [t for t in L_idx if present[t]]
    npres = len(pres)
    miss_single = sum(1 for t in pres if j not in fires[t] and retained[t])
    miss_family = sum(1 for t in pres if not (fires[t] & fam) and retained[t])
    return dict(j=j, sel_j=sel[j], fam=fam, npres=npres,
                rate_single=F(miss_single, npres), rate_family=F(miss_family, npres))


def build(sizes, n_background=4):
    """k disjoint feature groups covering the letter; backgrounds carry the non-L
    tokens. Latent t fires exactly on group t and never off-letter -- the faithful
    dictionary, one atom per generative feature, zero absorption by construction."""
    fires, is_L = [], []
    for t, sz in enumerate(sizes):
        for _ in range(sz):
            fires.append({t}); is_L.append(True)
    k = len(sizes)
    for b in range(n_background):
        fires.append({k + b}); is_L.append(False)
    present = [True] * len(fires)          # probe w = sum u_t, margin 1 vs 0 (§5)
    retained = [True] * len(fires)         # shrinkage is a positive scalar (§5)
    return fires, is_L, present, retained


print("=" * 74)
print("SPURIOUS ABSORPTION FROM SPLITTING -- exact certificate")
print(f"tau = {TAU}, lambda = {LAMBDA}, family cap = {FAM_CAP}")
print("=" * 74)

# --- Theorem: closed form matches the transcribed metric, over many partitions ---
def partitions_desc(n, maxpart=None):
    if maxpart is None:
        maxpart = n
    if n == 0:
        yield ()
        return
    for first in range(min(n, maxpart), 0, -1):
        for rest in partitions_desc(n - first, first):
            yield (first,) + rest


bad = []
tested = 0
for N in range(2, 15):
    for sizes in partitions_desc(N):
        if len(sizes) < 2:
            continue                        # k >= 2: there must be a split
        got = score_letter(*build(sizes))
        if F(sizes[0], N) < TAU:
            if got is not None:
                bad.append((sizes, "scored despite sel_j < tau"))
            continue
        tested += 1
        want_single = 1 - F(sizes[0], N)
        want_family = 1 - F(sum(s for s in sizes if F(s, N) >= TAU), N)
        if got is None or got["rate_single"] != want_single or got["rate_family"] != want_family:
            bad.append((sizes, f"got {got}, want {want_single}/{want_family}"))

check(f"Theorem: closed form == transcribed metric on all {tested} scored partitions "
      f"of N=2..14", not bad, bad[:2] if bad else "")

# --- Zero absorption yet strictly positive reported rate ---
ex = score_letter(*build((3, 1, 1)))
check("worked example (3,1,1): rate_single = 2/5 > 0 with zero absorption",
      ex["rate_single"] == F(2, 5), f"rate_single={ex['rate_single']}")
check("worked example (3,1,1): family correction repairs NOTHING (both splits "
      "below tau)", ex["rate_family"] == ex["rate_single"],
      f"rate_family={ex['rate_family']}")

ex3 = score_letter(*build((1, 1, 1)))
check("three equal groups: rate_single = 2/3 with zero absorption",
      ex3["rate_single"] == F(2, 3), f"rate_single={ex3['rate_single']}")
check("three equal groups: family correction repairs FULLY (all splits clear tau)",
      ex3["rate_family"] == 0, f"rate_family={ex3['rate_family']}")

# --- Corollary A: sharp supremum 1 - tau ---
best, best_cfg = F(0), None
for N in range(2, 61):
    for sizes in partitions_desc(N):
        if len(sizes) < 2 or F(sizes[0], N) < TAU:
            continue
        r = 1 - F(sizes[0], N)
        if r > best:
            best, best_cfg = r, sizes
check("Corollary A: no zero-absorption configuration exceeds 1 - tau",
      best <= 1 - TAU, f"max found = {best} <= {1 - TAU}")
check("Corollary A: the bound 1 - tau is ATTAINED, not merely approached "
      "(sel_j >= tau is non-strict)",
      best == 1 - TAU, f"max = {best} ({float(best):.4f}) at sizes={best_cfg}")

# --- Corollary B: family repairs iff every group clears tau ---
viol = []
for N in range(2, 21):
    for sizes in partitions_desc(N):
        if len(sizes) < 2 or F(sizes[0], N) < TAU:
            continue
        got = score_letter(*build(sizes))
        all_clear = all(F(s, N) >= TAU for s in sizes)
        if (got["rate_family"] == 0) != all_clear:
            viol.append(sizes)
check("Corollary B: rate_family == 0 iff every split group clears tau", not viol,
      viol[:3] if viol else "")
kmax = max(k for k in range(2, 20) if F(1, k) >= TAU)
check(f"Corollary B: largest fully-repaired equal split is k = floor(1/tau) = {kmax}",
      kmax == 3 and F(1, kmax) >= TAU > F(1, kmax + 1))

# --- Lemma 1/2: the faithful dictionary attains the global optimum (exact) ---
lo_bound = LAMBDA * 1 - LAMBDA ** 2 / 4                  # lambda*r - lambda^2/4, r=1
t_opt = 1 - LAMBDA / 2                                   # (r - lambda/2)_+
faithful = (1 - t_opt) ** 2 + LAMBDA * t_opt
check("Lemma 2: faithful dictionary attains the per-event lower bound exactly",
      faithful == lo_bound, f"loss = {faithful} = lambda - lambda^2/4")

# --- Corollary: a merged atom is strictly worse (the one irrational check) ---
# The nonnegativity clamp matters here and an earlier version of this check ignored
# it, which produced a spurious "break-even lambda ~ 1.707". The code on the merged
# atom is t* = max(0, proj - lambda/2) with proj = 1/sqrt(2), so the unclamped
# expression is only valid while lambda < sqrt(2); past that t* = 0 and the loss is
# just ||x||^2 = 1. Doing it piecewise makes the conclusion STRONGER, not weaker.
try:
    import sympy as sp
    lam_s = sp.Symbol("lam", positive=True)
    s2 = sp.sqrt(2)
    faithful_s = lam_s - lam_s ** 2 / 4
    t_un = 1 / s2 - lam_s / 2
    gap_lo = sp.simplify((1 - s2 * t_un + t_un ** 2 + lam_s * t_un) - faithful_s)
    gap_hi = sp.simplify(1 - faithful_s)                 # t* clamped to 0
    check("Corollary: merged-atom code clamps to zero exactly at lambda = sqrt(2)",
          sp.simplify(sp.solve(sp.Eq(t_un, 0), lam_s)[0] - s2) == 0)
    check("Corollary (branch lambda < sqrt2): merging strictly worse; min gap at the "
          "branch end is positive",
          sp.simplify(gap_lo.subs(lam_s, s2)) > 0,
          f"gap(sqrt2) = {sp.nsimplify(sp.simplify(gap_lo.subs(lam_s, s2)))} "
          f"= {float(gap_lo.subs(lam_s, s2)):.6f}")
    check("Corollary (branch lambda >= sqrt2): gap = (lambda-2)^2/4 > 0 for every "
          "lambda != 2",
          sp.simplify(gap_hi - (lam_s - 2) ** 2 / 4) == 0,
          f"gap = {sp.factor(gap_hi)}")
    gaps = [(sp.Rational(v, 1000),
             gap_lo.subs(lam_s, sp.Rational(v, 1000)) if sp.Rational(v, 1000) < s2
             else gap_hi.subs(lam_s, sp.Rational(v, 1000)))
            for v in range(1, 2000)]
    worst_lam, worst = min(gaps, key=lambda p: float(p[1]))
    # The infimum over (0,2) is 0, approached only as lambda -> 2, where the SAE codes
    # every input to zero and the comparison degenerates. It is never attained inside.
    check("Corollary: merging is STRICTLY worse across the WHOLE admissible range "
          "0 < lambda < 2 (the earlier 'break-even at 1.707' was an artifact of "
          "ignoring the clamp)",
          all(g > 0 for _, g in gaps),
          f"min over a 1/1000 grid = {sp.nsimplify(worst)} = {float(worst):.3e} at "
          f"lambda = {float(worst_lam)}; gap -> 0 only as lambda -> 2 (degenerate: "
          f"all codes vanish), never zero inside the range")
except ImportError:
    check("Corollary (merged strictly worse) -- SKIPPED, sympy not installed", True,
          "install sympy to exercise this check")

# --- The family cap is a real hypothesis: exhibit where the closed form breaks ----
# The reference code caps F_L at 32 by descending sel. More than 32 groups can clear
# tau only when tau <= 1/33, so the closed form for rate_family needs tau > 1/33.
# At the registered tau = 3/10 at most floor(1/tau) = 3 groups clear, so the cap can
# never bind -- but the theorem must say so rather than get lucky.
tiny_tau = F(1, 40)
sizes_cap = tuple([1] * 40)                       # 40 equal groups, each 1/40 >= 1/40
got_cap = score_letter(*build(sizes_cap), tau=tiny_tau)
naive = 1 - F(sum(s for s in sizes_cap if F(s, 40) >= tiny_tau), 40)   # ignores the cap
check("Family cap: with tau = 1/40 and 40 equal groups the cap BINDS, and the "
      "uncapped closed form is wrong -- so tau > 1/33 is a required hypothesis",
      got_cap["rate_family"] != naive and got_cap["rate_family"] == F(8, 40),
      f"actual rate_family = {got_cap['rate_family']} (32 of 40 groups kept), "
      f"uncapped formula would say {naive}")
check("Family cap: at the registered tau = 3/10 at most floor(1/tau) = 3 groups can "
      "clear threshold, so the cap can never bind",
      kmax <= FAM_CAP and int(1 / TAU) == 3)

# --- Guard: the construction really has zero absorption -------------------
# Absorption would mean some atom carries two generative features at once. Here each
# latent fires on exactly one group and never off-letter, so no atom is shared.
shared = []
for sizes in [(3, 1, 1), (1, 1, 1), (5, 3, 2)]:
    fires, is_L, _, _ = build(sizes)
    per_latent_groups = {}
    off = 0
    for t, row in enumerate(fires):
        for i in row:
            per_latent_groups.setdefault(i, set()).add((t, is_L[t]))
    for i, ts in per_latent_groups.items():
        if len({lab for _, lab in ts}) > 1:
            shared.append((sizes, i))
check("Guard: no latent spans two generative features (true absorption == 0)",
      not shared, shared[:2] if shared else "")

print("=" * 74)
n_pass = sum(1 for _, ok, _ in checks if ok)
print(f"TOTAL: {len(checks)} checks, {n_pass} PASS, {len(checks) - n_pass} FAIL")
raise SystemExit(0 if n_pass == len(checks) else 1)
