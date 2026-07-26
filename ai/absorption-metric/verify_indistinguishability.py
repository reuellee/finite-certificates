#!/usr/bin/env python3
"""Indistinguishability certificate: the absorption metric cannot tell single-parent
absorption from distributed absorption -- and a carrier statistic can.

TWO HALVES.

IMPOSSIBILITY. Two generative models, each with its OWN loss-optimal dictionary
(established exactly in verify_m1_optimality.py, at epsilon = 0 where Theorem 1b pins
the optimal direction set uniquely):

  M1  single-parent absorption -- ONE child concept spanning k tokens, absorbed into
      ONE composite a_m = (a_L + a_c)/sqrt2.
  M2  distributed absorption -- k DISTINCT child concepts, each absorbed into its own
      composite a_mi = (a_L + a_ci)/sqrt2.

The metric sees only three things: which F_L latents fire on each token, whether the
letter is present in the input, and whether it is retained in the reconstruction. This
file shows those three are IDENTICAL between M1 and M2, token for token. Hence every
statistic measurable with respect to them -- rate_single, rate_family, and any other
function of that data, including ones nobody has written yet -- takes the same value
on both. The metric is not merely imprecise here; it is uninformative by construction.

REPAIR. A statistic that reads OUTSIDE F_L does separate them: on absorbed tokens M1
has one recurring carrier and M2 has k distinct ones. That is exactly the
carrier-consistency statistic of round 14, so the fix is already deployed and already
measured -- and on real Pythia-1.4B SAEs it answers "distributed".

The metric is transcribed from the reference scorer
(sae-identifiability/analysis/round13a_family_endpoint.py). To show the transcription
is faithful and not tuned to this file, it is required to reproduce the independently
derived worked example from splitting_inflation.md.

Run: python3 verify_indistinguishability.py     (python3 + stdlib only)
"""
from fractions import Fraction as F

TAU = F(3, 10)
FAM_CAP = 32
checks = []


def check(name, ok, detail=""):
    checks.append((name, bool(ok), detail))
    print(f"[{'PASS' if ok else 'FAIL'}] {name}" + (f" -- {detail}" if detail else ""))
    return ok


# ---------------------------------------------------------------- the metric
# Transcribed from round13a_family_endpoint.py; see splitting_inflation.md §1.
def score_letter(fires, is_L, present, retained, tau=TAU, fam_cap=FAM_CAP):
    n_lat = 1 + max((max(r) for r in fires if r), default=-1)
    L_idx = [t for t in range(len(fires)) if is_L[t]]
    nL_idx = [t for t in range(len(fires)) if not is_L[t]]
    sel = []
    for i in range(n_lat):
        pL = F(sum(1 for t in L_idx if i in fires[t]), len(L_idx)) if L_idx else F(0)
        pN = F(sum(1 for t in nL_idx if i in fires[t]), len(nL_idx)) if nL_idx else F(0)
        sel.append(pL - pN)
    j = max(range(n_lat), key=lambda i: (sel[i], -i))
    if sel[j] < tau:
        return None
    fam = sorted([i for i in range(n_lat) if sel[i] >= tau],
                 key=lambda i: (-sel[i], i))[:fam_cap]
    pres = [t for t in L_idx if present[t]]
    npres = len(pres)
    miss_single = sum(1 for t in pres if j not in fires[t] and retained[t])
    miss_family = sum(1 for t in pres if not (fires[t] & set(fam)) and retained[t])
    return dict(j=j, fam=set(fam), npres=npres,
                rate_single=F(miss_single, npres), rate_family=F(miss_family, npres))


# ---------------------------------------------------------------- the two models
# N_L letter tokens: (N_L - k) parent-solo, k joint (child co-occurring).
# Precondition from the optimality gate: k/N_L < tau <= (N_L-k)/N_L, so M1's composite
# escapes F_L while the letter latent is still scored.
N_L, K, N_BG = 10, 2, 6
LAT_L = 0                                   # latent index of a_L in both models


def build_M1(n_L=N_L, k=K, n_bg=N_BG):
    """ONE child concept -> ONE composite, firing on all k joint tokens."""
    fires, is_L = [], []
    for _ in range(n_L - k):
        fires.append({LAT_L}); is_L.append(True)        # parent-solo
    for _ in range(k):
        fires.append({1}); is_L.append(True)            # joint: the single composite
    for b in range(n_bg):
        fires.append({2 + b}); is_L.append(False)
    return fires, is_L


def build_M2(n_L=N_L, k=K, n_bg=N_BG):
    """k distinct child concepts -> k composites, one token each."""
    fires, is_L = [], []
    for _ in range(n_L - k):
        fires.append({LAT_L}); is_L.append(True)
    for i in range(k):
        fires.append({1 + i}); is_L.append(True)        # a distinct composite per token
    for b in range(n_bg):
        fires.append({1 + k + b}); is_L.append(False)
    return fires, is_L


def flags(n_L=N_L, n_bg=N_BG):
    """present: probe w = a_L + sum_i a_ci separates L with margin 1.
    retained: the reconstruction is a positive scalar multiple of x."""
    return [True] * (n_L + n_bg), [True] * (n_L + n_bg)


present, retained = flags()

print("=" * 74)
print("INDISTINGUISHABILITY CERTIFICATE -- absorption metric, exact")
print(f"tau = {TAU}, N_L = {N_L} letter tokens, k = {K} absorbed, "
      f"{N_BG} background tokens")
print("=" * 74)

# --- transcription check: must reproduce the independently derived worked example ---
def build_split(sizes, n_bg=4):
    fires, is_L = [], []
    for t, sz in enumerate(sizes):
        for _ in range(sz):
            fires.append({t}); is_L.append(True)
    for b in range(n_bg):
        fires.append({len(sizes) + b}); is_L.append(False)
    return fires, is_L, [True] * len(fires), [True] * len(fires)


ref = score_letter(*build_split((3, 1, 1)))
check("transcription is faithful: reproduces splitting_inflation.md's worked example "
      "(3,1,1) -> rate_single = 2/5",
      ref["rate_single"] == F(2, 5) and ref["rate_family"] == F(2, 5))

# --- the two models score identically -------------------------------------------
m1 = score_letter(*build_M1(), present, retained)
m2 = score_letter(*build_M2(), present, retained)
check("M1 is scored (letter clears tau)", m1 is not None and m1["j"] == LAT_L)
check("M2 is scored (letter clears tau)", m2 is not None and m2["j"] == LAT_L)
check("F_L is the SAME set in both models -- {a_L} only; every composite falls below "
      "tau and is excluded",
      m1["fam"] == m2["fam"] == {LAT_L},
      f"F_L(M1) = {m1['fam']}, F_L(M2) = {m2['fam']}")
check("rate_single identical", m1["rate_single"] == m2["rate_single"],
      f"both = {m1['rate_single']} = {float(m1['rate_single']):.3f}")
check("rate_family identical", m1["rate_family"] == m2["rate_family"],
      f"both = {m1['rate_family']}")

# --- the STRONG claim: the whole observable is identical, so ANY statistic is -----
# The metric's entire input is, per token: which F_L latents fire, present, retained.
def observable(fires, is_L, fam):
    return [(frozenset(fires[t] & fam), is_L[t], present[t], retained[t])
            for t in range(len(fires))]


obs1 = observable(*build_M1(), m1["fam"])
obs2 = observable(*build_M2(), m2["fam"])
check("IMPOSSIBILITY: the full per-token observable (F_L firing pattern, present, "
      "retained) is IDENTICAL between M1 and M2 -- so EVERY statistic measurable "
      "from it agrees, not just these two rates",
      obs1 == obs2, f"{len(obs1)} tokens compared, all equal")

# and the models really are different underneath
under1 = [frozenset(r) for r in build_M1()[0]]
under2 = [frozenset(r) for r in build_M2()[0]]
check("...while the underlying firing patterns genuinely DIFFER (the difference is "
      "real, it is simply invisible to the metric)", under1 != under2,
      f"M1 absorbed-token supports {sorted(set(under1[N_L-K:N_L]), key=sorted)}, "
      f"M2 {sorted(set(under2[N_L-K:N_L]), key=sorted)}")

# --- REPAIR: a carrier statistic separates them ----------------------------------
def carrier_stats(fires, fam, n_L=N_L):
    """Round 14's P2: over absorbed tokens, the modal non-family carrier's share."""
    absorbed = [t for t in range(n_L) if not (fires[t] & fam)]
    carriers = [min(fires[t] - fam) for t in absorbed if fires[t] - fam]
    if not carriers:
        return F(0), 0
    top = max(carriers.count(c) for c in set(carriers))
    return F(top, len(carriers)), len(set(carriers))


s1, d1 = carrier_stats(build_M1()[0], m1["fam"])
s2, d2 = carrier_stats(build_M2()[0], m2["fam"])
check("REPAIR: the carrier-consistency statistic SEPARATES M1 from M2",
      s1 != s2 and d1 != d2,
      f"M1 top-1 share {s1} over {d1} distinct carrier(s); "
      f"M2 top-1 share {s2} over {d2}")
check("REPAIR: M1 (single parent) gives top-1 share 1 -- one recurring carrier",
      s1 == 1 and d1 == 1)
check("REPAIR: M2 (distributed) gives top-1 share 1/k -- k distinct carriers",
      s2 == F(1, K) and d2 == K)

# --- scaling INSIDE the precondition k/N_L < tau ---------------------------------
def run(n_L, k):
    p, r = flags(n_L)
    a = score_letter(*build_M1(n_L, k), p, r)
    b = score_letter(*build_M2(n_L, k), p, r)
    ca, da = carrier_stats(build_M1(n_L, k)[0], a["fam"], n_L)
    cb, db = carrier_stats(build_M2(n_L, k)[0], b["fam"], n_L)
    return a, b, (ca, da), (cb, db)


rows, ok_scale = [], True
for k in range(2, 7):
    n_L = 10 * k                                  # keeps k/n_L = 1/10 < tau
    a, b, (ca, da), (cb, db) = run(n_L, k)
    same = a["rate_single"] == b["rate_single"] and a["rate_family"] == b["rate_family"]
    ok_scale &= same and ca != cb and da == 1 and db == k
    rows.append(f"k={k},N_L={n_L}: rates {a['rate_single']}/{a['rate_family']} both; "
                f"carrier {ca} vs {cb}")
check("scaling: whenever k/N_L < tau the two models keep IDENTICAL rates while the "
      "carrier statistic keeps separating them (1 vs 1/k)", ok_scale, "; ".join(rows))

# --- the precondition is SHARP: at k/N_L >= tau the metric CAN separate them ------
# M1's single composite fires on all k tokens, so sel(a_m) = k/N_L. Once that reaches
# tau the composite is swept INTO F_L, M1's joint tokens stop counting as absorbed,
# and rate_family diverges. So the indistinguishability is not universal -- it holds
# exactly on k/N_L < tau, and the boundary is where the metric regains power.
a_b, b_b, _, _ = run(10, 3)                       # 3/10 = tau exactly
check("precondition is SHARP: at k/N_L = tau exactly, M1's composite enters F_L and "
      "rate_family DIVERGES -- the metric distinguishes the models there",
      a_b["rate_family"] != b_b["rate_family"],
      f"k/N_L = 3/10 = tau: rate_family M1 = {a_b['rate_family']} vs "
      f"M2 = {b_b['rate_family']} (rate_single still equal at "
      f"{a_b['rate_single']} = {b_b['rate_single']})")
check("...and rate_single is still blind even at the boundary, because it reads only "
      "the single argmax latent a_L",
      a_b["rate_single"] == b_b["rate_single"])

print("=" * 74)
n_pass = sum(1 for _, ok, _ in checks if ok)
print(f"TOTAL: {len(checks)} checks, {n_pass} PASS, {len(checks) - n_pass} FAIL")
raise SystemExit(0 if n_pass == len(checks) else 1)
