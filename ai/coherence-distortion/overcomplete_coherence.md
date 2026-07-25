# Coherence penalties distort overcomplete SAEs: an exact finite certificate

*Certificate script (`verify_overcomplete_coherence.py`, this directory) authored by
Reuel Lee; the class-wide bounds (§3) and this note were added in review. Every
numbered claim is verified in exact arithmetic (rationals, Q(√3), or sympy symbolic
identities) by the script — run it: `ALL EXACT CHECKS PASSED`, exit 0.*

## 1. Setup

Ambient dimension d = 2. Data distribution: uniform on the two true features
{e₁, e₂} — the data **is** the features (no co-occurrence, no noise, no absorption
pressure; the ε = 0-like setting of the no-go arc). SAE: m = 3 unit-norm decoder
atoms, nonnegative codes, oracle (exact convex) coding, population objective

  L(D) = E_x [ min_{f≥0} ‖x − Df‖² + λ‖f‖₁ ] + β·P(D),  λ = 1/5,

with either the Gram penalty P(D) = Σ_{i<j} ⟨dᵢ,dⱼ⟩² or the squared mutual
coherence M(D) = max_{i<j} ⟨dᵢ,dⱼ⟩², at β = 1/16.

Call a dictionary **faithful** if it contains both e₁ and e₂ (plus one free unit
atom d₃).

## 2. Theorem (exact, m = 3)

**(Gram form.)** At λ = 1/5, β = 1/16:

1. *Every* faithful triple has objective **exactly** 19/100 + β·1 = 101/400.
   (Base loss is exactly 19/100 and Gram penalty exactly 1, class-wide — §3.)
2. The rational 5-12-13 frame {(12/13, 5/13), (12/13, −5/13), e₂} has objective
   101/400 − 913877/164511360 (gap ≈ 5.56·10⁻³), **strictly smaller**.
3. Hence **no penalized-optimal 3-atom dictionary contains the true features** —
   whatever the global optimum is, it is not faithful. The coherence penalty
   distorts the learned dictionary off the ground truth.

**(Mutual-coherence form.)** Same λ, β: every faithful triple has objective
≥ 19/100 + β·(1/2) (base exactly 19/100, M(D) ≥ 1/2 class-wide, infimum attained
at d₃ = (±√2/2, ±√2/2)), while the rational 33-56-65 frame
{(56/65, 33/65), (56/65, −33/65), e₂} has objective 23366423/105996800, smaller by
85369/105996800 ≈ 8.05·10⁻⁴. Same conclusion.

**(β = 0 control — the distortion is remedy-induced.)** For unit atoms,
‖Df‖ ≤ ‖f‖₁, so the per-point coding loss of *any* dictionary is
≥ min_{ρ≥0} (1−ρ)² + λρ = λ − λ²/4 = 19/100 (complete the square:
(1−ρ)² + λρ = (ρ − (1−λ/2))² + λ − λ²/4; verified symbolically, check (d)).
The faithful class attains this at both data points, so **without the penalty the
faithful class is exactly globally optimal**. The penalty alone flips the ranking.

Both witness objectives are *exact* values, not upper bounds: the witness codes
carry exact KKT certificates, so their base losses are the true coding optima.
(For excluding the faithful class an upper bound would already suffice.)

## 3. The class-wide argument

The witness comparisons in the original script used the constants 19/100 (faithful
base) and 1 resp. 1/2 (faithful penalty). The review extension proves these hold
for the *entire* faithful class:

**(a) Exact faithful coding value.** For **any** unit-atom dictionary containing
e₁, the single-atom code f = (1 − λ/2) on e₁ (zero elsewhere) satisfies the exact
KKT conditions of the convex coding problem at x = e₁: the residual is (λ/2)e₁;
the active correlation is ⟨e₁, (λ/2)e₁⟩ = λ/2 exactly; every inactive correlation
is (λ/2)⟨dⱼ, e₁⟩ ≤ λ/2 since ⟨dⱼ, e₁⟩ ≤ 1 for unit dⱼ (Cauchy–Schwarz; symbolic
identity: the slack for dⱼ = (cos θ, sin θ) is λ·sin²(θ/2) ≥ 0). KKT conditions
are sufficient for global optimality of a convex program, so the optimal coding
value is **exactly** (λ/2)² + λ(1 − λ/2) = λ − λ²/4 = **19/100**, independent of
the other atoms. Symmetrically for e₂. Hence every faithful dictionary has base
loss exactly 19/100. *Verified:* symbolic identities plus 200 random
exact-rational dictionaries (Pythagorean-parametrized unit atoms), each checked
by the module's exact KKT checker **and** by an independent pure-Fraction
support-enumeration solver (all supports of size ≤ 2; an optimum with linearly
independent support always exists in 2D) — the enumerated optimum equals 19/100
in every trial, for x = e₁ and x = e₂.

**(b) Gram-penalty identity.** For a faithful triple {e₁, e₂, d₃}, d₃ = (x, y)
unit: P = ⟨e₁,e₂⟩² + x² + y² = 0 + 1 = **1 exactly** — the cross terms with the
two true features sum to ‖d₃‖². Generally, for m unit atoms containing e₁, e₂:
P(D) = (m − 2) + Σ_{extras i<j} ⟨dᵢ,dⱼ⟩² ≥ m − 2 (each extra atom contributes
exactly ‖d‖² = 1 against the pair e₁, e₂). Verified symbolically for m = 3
(identity) and m = 4 (bound), plus rational spot checks up to m = 5. The
certificate's class is m = 3, where the penalty is *identically* 1 — so under
the Gram penalty the faithful class collapses to the single objective value
19/100 + β, and one strict witness excludes all of it.

**(c) Mutual-coherence bound.** With u = x²: max(x², y²) = max(u, 1−u) =
1/2 + |u − 1/2| ≥ **1/2** (symbolic identity), with equality iff x² = y² = 1/2.
So M ≥ 1/2 for every faithful triple, and the witness beats 19/100 + β/2 — a
lower bound on every faithful objective.

## 4. Near-onset structure

The symmetric-split family d₁,₂ = (cos θ, ±sin θ), d₃ = e₂ passes through a
faithful configuration at θ = 0 (frame {e₁, e₁, e₂}, objective exactly
19/100 + β). Second-order expansion at θ = 0 gives
L ≈ L(0) + θ²·[λ(2−λ)/8 − 2β], so the faithful point becomes unstable to
splitting exactly when **β > λ(2−λ)/16 = 9/400 = 0.0225** at λ = 1/5 — the
analytic onset.

The certificates bracket it from above with exact rational exclusion thresholds
β_cert = (witness base − 19/100)/(1 − witness penalty), the exact β above which
the witness beats the whole faithful class:

| witness | β used | exact β_cert | ≈ |
|---|---|---|---|
| near-onset frame {(399/401, ±40/401), e₂} | 1/40 = 0.025 | 25856961601/1118227824000 | 0.0231232 |
| 5-12-13 frame (Gram) | 1/16 | 1228123/34272000 | 0.0358346 |
| triangle frame (Gram, min-coherence, Q(√3)) | 1/16 | 4√3/15 − 61/150 | 0.0552135 |
| 33-56-65 frame (mutual coherence) | 1/16 | 1519479/25677568 | 0.0591753 |

The near-onset witness certifies distortion at β = 1/40 (11% above the analytic
onset), with an exclusion threshold β_cert ≈ 0.023123 only 2.8% above the onset
0.0225; its gap is tiny but exactly positive (753445505641/20582270719204005). Below the onset the expansion says
faithful is locally stable in this family; that direction is *not* certified
(no global lower bound for β < onset is claimed).

The script also verifies the Welch-gap pattern for d = 2…32: with m = d + 1, a
dictionary containing an orthonormal basis has Gram penalty 1 vs (d+1)/(2d) for
the unit-norm simplex tight frame — a positive gap (d−1)/(2d) in every dimension,
so the penalty pressure toward distorted low-coherence frames is not a 2D
artifact (only the d = 2 optimality comparison is certified, though).

## 5. Honest scope

- **Population objective, oracle codes.** Exact convex nonneg-L1 coding per
  point; nothing here is about SGD/TopK/encoder dynamics.
- **m = 3, d = 2, this data distribution** (uniform on {e₁, e₂}), nonneg L1 with
  λ = 1/5, unit decoder columns. The class-wide penalty identity (b) is specific
  to m = 3 in 2D; for m > 3 only the bound P ≥ m − 2 is proved here, and the
  competitor comparison at fixed larger m is not carried out.
- The theorem excludes the faithful class; it does **not** identify the global
  optimum (the witnesses are not claimed optimal).
- Two penalty forms (Gram, squared mutual coherence). The onset formula is for
  the Gram form; for M the certified exclusion threshold is ≈ 0.0592.

## 6. Positioning: the overcomplete companion to the coherence-penalty no-go arc

The sae-identifiability project (`~/sae-identifiability/theory/general_no_go.md`,
`~/sae-identifiability/report.md` §7.1b) established, for m ≤ d: every penalty
that is a function of pairwise decoder inner products is constant on the
orthonormal-frame manifold, so no such penalty can distinguish a faithful frame
from an **anti-rotated absorbed** one — coherence penalties shrink the absorption
region at most ~4×, never eliminate it (bounded remedy, ε\*\*(β) saturating at
≈ 0.0159), and degrade when overdosed. Coherence penalties as an absorption
remedy are prior art — OrtSAE (Korznikov et al., arXiv:2509.22033), chunked
max-pairwise-cosine, weight chosen empirically, no threshold or theorem. That
note explicitly left the overcomplete case m > d **open** (its §Lemma 3 scope:
"O is empty and Lemma 1(iii) instead forces minimal-coherence frames … The
general overcomplete case is open").

This certificate is the smallest overcomplete instance (d = 2, m = 3), and it
isolates a *different, cleaner* failure mode:

- In the no-go arc the penalty fails by **blindness**: absorption lives in the
  codes, the penalty sees only decoder angles, and the absorbed solution evades
  it by anti-rotation. There, absorption pressure (co-occurrence, ε small) does
  the distorting; the penalty merely fails to stop it.
- Here there is **no absorption pressure at all** — each feature appears alone,
  the data is the features, and at β = 0 the faithful dictionary is *exactly*
  globally optimal (§2, β = 0 control). With a free third atom (m > d), the
  faithful configuration necessarily pays coherence (any third unit atom has
  ⟨d₃,e₁⟩² + ⟨d₃,e₂⟩² = 1), while a distorted frame can trade a rational amount
  of base loss for a larger penalty saving. Above an exact rational threshold —
  onset λ(2−λ)/16, certified from β_cert ≈ 0.02312 upward — the **remedy itself
  pushes the optimum off the true features**. Remedy-induced distortion, as a
  finite certificate: the penalized objective provably prefers atoms that are
  not features of the data-generating process, in a setting where the
  unpenalized objective provably recovers them.

Together the two results bracket the practice: below m = d the penalty is
evadable (doesn't fix absorption); above m = d it is actively harmful past an
exact, small threshold (β_cert ≈ 0.023 at λ = 1/5, well below penalty weights
that would be needed to matter). This sharpens the §7.1b dosing advice — the
window between "too weak to help" and "distorts the dictionary" is narrow and
now has an exact overcomplete lower edge.

## 7. Files

- `verify_overcomplete_coherence.py` — the certificate (original witnesses by
  Reuel Lee; CLASS-WIDE BOUNDS section added in review). Exit 0,
  `ALL EXACT CHECKS PASSED`.
- Context: `~/sae-identifiability/theory/general_no_go.md` (general no-go,
  m ≤ d), `~/sae-identifiability/report.md` §7.1b (anti-rotation evasion,
  bounded remedy ε\*\*(β), OrtSAE prior art arXiv:2509.22033).
