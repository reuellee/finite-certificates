# Finite-certificate counterexamples for published optimizer guarantees (2023–2026)

Date: 2026-07-25. Tools: numpy 1.24.2, sympy 1.11.1 (exact rational arithmetic where
marked). All certificates re-runnable: `python3 verify_muon_ns.py`, `python3 verify_lion.py`
(exit 0 = all checks pass; both pass as of this writing).

**Caveat on quotes**: theorem statements below were extracted from arXiv HTML via
automated fetch (2026-07-25). Wording is as extracted; before external use, re-verify
each quote against the paper PDF.

---

## Targets considered (literature pass)

| Target | Paper(s) | Verdict after inspection |
|---|---|---|
| Muon (practical, Newton–Schulz) | **arXiv:2601.19156** "Convergence of Muon with Newton–Schulz" | **CERT-M1/M2/M3: coverage claim falsified for shipped coefficients** |
| Muon (exact msign) | arXiv:2502.02900 (Li & Hong, "A Note on the Convergence of Muon") | Thm 2.1 is a standard normalized-momentum proof; checked deterministic and tuned-stepsize regimes — consistent. **CERT-M4: Thm 3.1 stepsize condition vacuous for all β ≥ 1/2** (incl. Muon default 0.95) |
| Muon inexact LMO | Shulgin et al. arXiv:2510.19933; arXiv:2606.21581 (degenerate case) | Prior art for the inexactness gap; CERT-M3 gives explicit family where small-δ additive models are unsatisfiable at deployed q = 5 |
| Lion | arXiv:2411.07724 ("Convergence Rate Analysis of LION") | Theorems 2/5 + Corollaries 3/6 stress-tested analytically (σ→0 limits, extreme c₁,c₂,c₃ choices, β₁ = 0 endpoint): bounds have correct additive structure, could not falsify. **CERT-L1: exact 2-cycle proves their annealing is necessary; informal constant-hyperparameter claim false** |
| Lion-K / Lyapunov | arXiv:2310.05898 (ICLR 2024) | Discrete-time theorem text not retrievable in session (OpenReview behind bot-check); not pursued — lead for future work |
| Muon variance-reduced | arXiv:2509.15816 | Claimed Õ(T^{−1/3}) matches known STORM-type rates; plausible, not pursued |
| Schedule-Free (Defazio et al. 2024), Prodigy/D-adaptation | — | Convex online-to-batch proofs, heavily vetted; no discrete checkable weakness found in budget |

---

## Certificate 1 (primary): arXiv:2601.19156 "Convergence of Muon with Newton–Schulz"

### Quoted claims (extracted 2026-07-25)

Coverage claim (abstract/intro): analysis of *"Muon as originally proposed and used in
practice—using the momentum orthogonalization with a few Newton–Schulz steps"* and
*"we analyze Muon as originally proposed (Jordan et al., 2024) and as used in practice."*

Polynomial analyzed (Definition 2): `p_κ(λ) = Σ_{s=0}^κ c_s (1−λ)^s, c_s = (2s)!/(4^s (s!)²) > 0`
(Taylor truncation of λ^{−1/2}; all coefficients positive). Prescaling `α_t = max{1, ‖M_t‖_F}`.

Orthogonality residual: `δ_{t,j} := ‖Π_t − X_{t,j} X_{t,j}^⊤‖_op ∈ [0,1)`.

**Theorem 2** (decay): `δ_{t,q} ≤ δ_{t,0}^{(κ+1)^q}` and `χ_q ≤ 1/√(1 − δ_0^{(κ+1)^q})`.

**Theorem 1** (rate): `χ_q · O(√(LD/T) + σr/√(BT) + (rσ²LD/BT)^{1/4})` — the rate is
useful only via the mechanism χ_q → 1 as q grows.

The paper contains **no** limitations remark about tuned coefficients.

### The gap

Muon **as originally proposed by Jordan et al. (2024) and as deployed** does not use the
Taylor polynomial. It uses 5 iterations of the tuned quintic
`p(x) = a x + b x³ + c x⁵` with `(a, b, c) = (3.4445, −4.7750, 2.0315)`
(non-monotone; c₁-equivalent coefficient negative), which by design does **not**
converge to the polar factor.

### CERT-M1 (exact, one step; rational arithmetic)

Input: 1×1 momentum matrix M = [1] (prescaling inactive, δ₀ = 0 exactly).
Theorem-2 law (κ = 2 slot, q = 1) demands δ₁ ≤ δ₀^{3} = 0. Shipped step:
`x₁ = a + b + c = 701/1000` exactly, so `δ₁ = 1 − (701/1000)² = 508599/1000000 ≈ 0.5086 > 0`.
The Taylor polynomial of the same degree fixes x = 1 (δ₁ = 0), confirming the theorem is
consistent for the polynomial it actually covers.

**Scoping (honest)**: Theorem 2 *as literally stated* (Taylor c_s) is **not** violated.
What is falsified is the paper's stated coverage — the abstract/intro claim that the
analysis applies to Muon "as originally proposed (Jordan et al., 2024) and as used in
practice." For the deployed iteration, the load-bearing Theorem-2 decay law fails at
q = 1 from δ₀ = 0, by exact rational computation.

### CERT-M2 (no number of NS steps rescues it; exact obstruction)

Since `p(1) = 701/1000 ≠ ±1` (exact), no orbit of the deployed singular-value map can
have δ_q → 0: if δ_q → 0 then σ_q → 1, whence δ_{q+1} → 508599/1000000 > 1/2 —
contradiction. So **χ_q does not tend to 1 for deployed Muon for any q**; the paper's
convergence mechanism is unavailable regardless of iteration count. Supporting numerics:
both positive fixed points of the map are unstable (exact multipliers 1.582…, 6.473…),
the period-2 points are unstable (multiplier 1.2789), and the orbit from σ = 1 is
bounded and chaotic with δ_q ∈ [0.0959, 0.535] over 2·10⁵ steps (60-digit floats agree
with float64 over 2·10⁴).

### CERT-M3 (degenerate family; kills fixed-q analyses for BOTH coefficient sets)

Explicit family `M_ε = diag(1/2, ε/2)`, ε = 10⁻⁸ (‖M‖_F ≤ 1 so no prescale;
Polar(M) = I₂). Exact rational 5-step computation:

- shipped coefficients: `‖X₅ − Polar(M)‖_op = 0.9999975756…`
- Taylor κ = 2: `‖X₅ − Polar(M)‖_op = 0.9999998841…`

So at the deployed q = 5, the polar error is ≈ 1, and the paper's own Theorem-2 bound
requires **q ≥ 35** NS steps before δ ≤ 1/2 on this family. Consequence (type-4
certificate): any analysis assuming a uniformly small additive orthogonalization error
(e.g. the error model of Shulgin et al., arXiv:2510.19933) is **vacuous on this explicit
family** for the deployed 5-step iteration — near-rank-deficient momentum, which occurs
in practice, drives the inexactness parameter to ≈ 1, where the rate bounds carry no
information.

### CERT-M4 (vacuity note, arXiv:2502.02900 Theorem 3.1)

Quoted condition: *"η ≤ (1/8L)√((1−2β)/(2β)) and β as any constant in (0,1)"*.
The radicand is negative for every β ≥ 1/2 (at Muon's default β = 0.95 it equals
−9/19), so the admissible stepsize set is **empty** on the entire practical momentum
range; the theorem (which concerns the nuclear-norm-scaled Bernstein–Newhouse variant,
not vanilla Muon) is vacuous there. Not an error — the statement's "any constant in
(0,1)" is just misleading; only β < 1/2 yields a nonempty hypothesis.

Verified in: `verify_muon_ns.py` (all checks PASS, exit 0).

---

## Certificate 2: Lion with default constant hyperparameters — exact 2-cycle

### Quoted target statements (arXiv:2411.07724, extracted 2026-07-25)

Update (Alg. 1): `θ^{k+1} ← θ^k − η(sign(c^k) + λθ^k)`, `c^k ← β₁m^{k−1} + (1−β₁)g^k`,
`m^k ← β₂m^{k−1} + (1−β₂)g^k`. Assumptions: (1) L-smoothness; (2) unbiased gradients;
(3) `E‖g^k − ∇f(θ^k)‖² ≤ σ²`. Theorem 2/5 hyperparameters: `β₁ = 1 − c₁/√K`,
`β₂ = 1 − c₂/√K`, `η = c₃/(√d·K^{3/4})` — **annealed with the horizon K**.

### Certificate (exact, rational arithmetic)

f(θ) = θ²/2 (L = 1, 1-strongly convex), exact gradients (σ = 0), Lion **defaults**
β₁ = 9/10, β₂ = 99/100, λ = 0, any constant η > 0. Exact period-2 orbit:

- θ alternates `+η/2 ↔ −η/2`; m alternates `∓η(1−β₂)/(2(1+β₂)) = ∓η/398`;
- sign arguments `c = ±19η/398` bounded away from 0 (no tie);
- `|f′(θ_k)| = η/2` at **every** step, so `(1/K)Σ|f′| = η/2` for all K — no convergence
  in any averaged or last-iterate sense. Cycle closure verified exactly for numeric η = 1
  and symbolically for generic η > 0; long-horizon float runs from generic
  initializations (θ₀ = 0.61, −3.7, 100) all settle into η-scale cycles with tail-average
  gradient = η/2.

### Scoping (honest)

This **does not contradict Theorems 2/5 of arXiv:2411.07724** — those anneal
β₁, β₂ → 1 and η → 0 with K, and the certificate is outside that schedule. What it
establishes, with a finite exact certificate rather than folklore:

1. The informal headline claim, read as "Lion (with its shipped constant
   hyperparameters) converges," is **false even deterministically on a 1-D strongly
   convex quadratic** satisfying Assumptions 1–3 with σ = 0.
2. The horizon-dependent annealing in the published theorems is **necessary**, not an
   artifact of the proof: no constant-hyperparameter variant of the guarantee can hold.

Verified in: `verify_lion.py` (all checks PASS, exit 0).

---

## Prior-art check

- **Non-convergence of tuned NS coefficients**: known and intentional — Jordan et al.'s
  own Muon write-up notes the tuned quintic runs at a non-convergent setting (singular
  values oscillate in ≈ [0.68, 1.13]); PolarExpress (Amsel et al. 2025) and
  Chebyshev-type accelerations (arXiv:2506.10935) discuss non-convergent tuned schemes.
  **Our contribution is not this fact** but its formal consequence: an exact one-step
  certificate that the specific decay law (Thm 2 of arXiv:2601.19156) and its χ_q → 1
  mechanism fail for the deployed coefficients, against that paper's explicit
  "as used in practice" coverage claim. To our knowledge no published note makes this
  falsification explicit (the paper has no limitations remark on it; we could not check
  OpenReview reviews — bot-blocked this session).
- **Inexact/degenerate LMO gap**: Shulgin et al. (arXiv:2510.19933) analyze inexact
  updates under an additive error model; arXiv:2606.21581 (June 2026) proves convergence
  in the degenerate case under (L⁰,L¹)-smoothness, confirming the community knows exact-
  LMO analyses had a gap. CERT-M3's explicit ε-family showing error ≈ 1 at deployed q = 5
  (for both coefficient sets, in exact arithmetic) is a sharper artifact than we found
  published, but the *phenomenon* is prior art.
- **Sign-method cycling**: generically known since signSGD folklore and
  Reddi–Kale–Kumar-adjacent literature. The exact closed-form Lion 2-cycle with default
  (β₁, β₂) = (0.9, 0.99), including the exact momentum offsets ∓η/398 and tie-free sign
  margins, appears to be unpublished in this explicit form, but we claim only
  formalization value, not novelty of the phenomenon.
- Li & Hong (arXiv:2502.02900) Thm 3.1's empty-stepsize-set for β ≥ 1/2: not noted
  anywhere we found, but it is a scoping observation, not an error.

## Negatives (honest)

- **Li & Hong Thm 2.1** (exact-msign Muon, tuned α, η, B = 1): stress-tested the
  deterministic limit (α = 1 ⇒ β = 0, orthogonalized GD) and the stated tuned regime;
  the bound structure matches standard normalized-momentum analyses (Cutkosky–Mehta
  style). No counterexample; appears sound.
- **LION arXiv:2411.07724 Thms 2/5, Corollaries 3/6**: probed σ → 0 degeneracy (bounds
  retain σ-free additive terms — no collapse), extreme constant choices (c₁ = √K ⇒
  β₁ = 0 signGD endpoint; c₂ → 0), and constant-vs-annealed schedules. Bound structure
  survives every probe we tried; appears sound.
- **arXiv:2601.19156 Theorem 2 for its stated Taylor polynomial**: verified the κ = 1
  case analytically (u′ = u²(3 + u)/4 ≤ u² for u ∈ [0,1]) — the inequality is correct
  for the polynomial the paper actually analyzes. The problem is coverage, not algebra.
- Schedule-Free, Prodigy/D-adaptation, variance-reduced Muon (2509.15816): no checkable
  weakness found within budget; rates match known-optimal templates.

## Leads for future work

1. **Lion-K discrete-time theorem** (arXiv:2310.05898, ICLR 2024): could not retrieve
   the discrete-time statement (Sec. 4) this session. If its discrete Lyapunov descent
   inequality has explicit constants without an O(η²) slack, the exact 2-cycle machinery
   here (with λ > 0, constraint ‖x‖_∞ ≤ 1/λ) is directly reusable to test KKT-violation
   margins against the stated constants.
2. **End-to-end rate violation for deployed Muon**: CERT-M3 suggests a matrix problem
   family where momentum is driven near rank-deficiency *persistently* (e.g. adversarial
   stale-momentum construction) could make the effective χ diverge along the actual
   trajectory, potentially violating even the Taylor-coefficient rate at fixed q. Our
   attempts with static quadratics failed (momentum degeneracy is transient there);
   a rotating/alternating-gradient Reddi-style construction is the natural next step.
3. **OpenReview reviews of 2601.19156 and 2510.19933**: bot-blocked here; check whether
   reviewers already raised the tuned-coefficient coverage issue.
4. arXiv:2606.21581's degenerate-case theorem is new (June 2026) and unvetted — its
   (L⁰,L¹) layer-wise assumptions and inexactness model would be the next audit target.
