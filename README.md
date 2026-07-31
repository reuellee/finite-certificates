# finite-certificates

Small, explicit, machine-checkable research results ("finite certificates"), produced
from 2026-07-25 onward by autonomous multi-agent research sessions (Claude agents,
with adversarial review by Gemini and GPT models). Almost every claim ships with a
standalone verifier in **exact arithmetic** (integers, `fractions.Fraction`, or exact
symbolic computation); floating point is used to *search*, never to *justify*. The one
deliberate exception is [`ai/coherence-transfer/`](ai/coherence-transfer/), which
replicates an empirical third-party result and says so.

**Requirements:** `python3` plus `numpy`, `scipy`, `sympy` (see
[`requirements.txt`](requirements.txt)). Many individual verifiers — including the
primary check of the maxout theorem — are standard-library only, and say so at the top
of the file. The `ai/coherence-transfer/` replication additionally needs
`scikit-learn` and `pandas`.

## Verify everything

```
python3 run_all.py            # runs every verify_*.py; nonzero exit if any fails
python3 run_all.py --fast     # skips the two slow verifiers (~10 min total otherwise)
```

`run_all.py` is what CI runs. Note it is not read-only: a few verifiers regenerate the
artifacts they check, so the working tree may show diffs afterwards.

## Results index

Each directory is self-contained and has its own README stating the result, so you can
go straight to one without reading the rest. No verifier imports any other.

**Sparse autoencoders / interpretability**

| result | where |
|---|---|
| The SAE feature-absorption metric is not identifying — it scores a zero-absorption dictionary as up to 70% absorbed, and cannot tell single-parent from distributed absorption | [`ai/absorption-metric/`](ai/absorption-metric/) |
| An absorbed feature's conditional rate is unidentifiable without labels | [`ai/sae-unidentifiability/`](ai/sae-unidentifiability/) |
| Internal causal relevance does not identify a semantic causal ontology | [`ai/sae-grounding/`](ai/sae-grounding/) |
| Coherence penalties provably distort the features they are meant to fix | [`ai/coherence-distortion/`](ai/coherence-distortion/) |
| Four exact minimal networks on which standard interpretability methods lie | [`ai/interp-illusions/`](ai/interp-illusions/) |
| A third-party empirical result, independently verified and replicated | [`ai/coherence-transfer/`](ai/coherence-transfer/) |

**Other machine-learning theory**

| result | where |
|---|---|
| Exact counterexamples and scope failures in published optimizer convergence claims: Muon's deployed coefficients falsify a coverage claim; Li–Hong's admissible stepsize set is empty for β ≥ 1/2 (vacuous, not false); a Lion period-two cycle contradicts an informal constant-hyperparameter claim (the annealed theorems stand) | [`ai/optimizer/`](ai/optimizer/) |
| **max f₀(3,5) = 42** — refutes the tightness of Prop. 6.5 and the odd case of Conjecture 6.6.1 of Balakin–Cox–Loho–Sturmfels at n=5 (132,560 exact cell-wide certificates; [arXiv note](ai/maxout/paper/)) | [`ai/maxout/`](ai/maxout/) |
| Same conjecture: (4,4) and (4,6) resolved, (3,8) achievability confirmed; at (4,5) and (3,7), instances certified at 58 and 84 vs conjectured 60 and 88 — lower bounds only, those maxima remain open | [`ai/maxout/`](ai/maxout/) |

**Commutative algebra**

| result | where |
|---|---|
| Aftermath of the Jacobian Conjecture counterexample — the n=2 boundary, fallout witnesses, minimal-degree theorems | [`jacobian/`](jacobian/) |

Adversarial review trail for all of the above: [`reviews/`](reviews/).

## Contributing

Pull requests are welcome from anyone — no permission needed, just fork and
open one. Refutations are the most valuable thing you can send: if a
certificate here is wrong, that is a result, and it will be reported as one.

Every pull request runs the verifier suite in CI. The bar for new claims
(exact arithmetic, an independent verifier, deliberately-failing controls,
honest scope) and the credit policy — **contributors are credited by name in
the papers** — are in [`CONTRIBUTING.md`](CONTRIBUTING.md).

Licensed under the [MIT License](LICENSE).

## Detail

### jacobian/ — aftermath of the Jacobian Conjecture counterexample (Alpöge, 2026-07-20)

Reference: the verification preprint at https://www.ulam.ai/research/jacobian.pdf (the original map F, deg (7,6,4),
det Jac ≡ −2, generic degree 3). `verify_original.py` re-verifies it in seconds.

- `n2_analysis.md` + `verify_n2.py` — **no Keller map of generic degree 2 exists in any
  dimension** (short proof; quadratic case of Campbell 1973 — no priority claimed), so
  generic degree 3 is minimal and any n=2 counterexample needs generic degree ≥ 5 and
  total degree > 100 (with Orevkov, Domrina–Orevkov, Moh). Also: y-linear Keller maps in
  n=2 are automorphisms (mechanism no-go), and degree-4 Keller maps have Galois closure
  S₄ or A₄. Gemini review: VERIFIED-SOUND (`reviews/GEMINI_n2_review.md`).
- `minimal_degree_hunt.md` + `verify_mechanism_lower_bound.py` (22 checks) +
  `verify_composition_obstruction.py` (9 checks) — minimal generic degree of a Keller
  non-automorphism is exactly 3 in every dimension ≥ 3, and **within the full z-linear
  cubic-mechanism class of the counterexample no Keller map has max component degree
  ≤ 6** — the original (7,6,4) is degree-minimal in its class (Gemini: VERIFIED-SOUND;
  scope boundaries in the note). Conjectured next step: no C³ counterexample of max
  degree ≤ 4.
- Explicit fallout witnesses derived constructively from F — full write-up with
  implication chains, dimensions, and a 5-day arXiv scoop-check in
  `fallout_harvest.md` (Gemini review: VERIFIED-SOUND). Headlines: the Poisson
  Conjecture PC₃ witness is SELF-CONTAINED (bracket-preserving non-injective endo of
  C⁶) and, with the explicit dim-368 Drużkowski matrix, apparently first; Dixmier DC₃
  refuted via an explicit A₃ Weyl endomorphism + the classical DC_n ⟹ JC_n direction;
  the Mathieu and cubic-homogeneous witnesses were scooped within the window:
  - `verify_dixmier_poisson.py` — explicit polynomial endomorphism of C⁶ preserving the
    standard symplectic Poisson bracket, det Jac ≡ 1, with **three distinct points
    sharing one image** (so: bracket-preserving, not injective, not an automorphism).
  - `deg3_map.py` + `verify_deg3_keller.py` — explicit **degree-3** Keller
    non-automorphism (Bass–Connell–Wright/Yagzhev reduction made explicit).
  - `cubic_map.py` + `verify_cubic_homogeneous.py` — explicit cubic-homogeneous-plus-
    identity Keller non-automorphism in dimension 55, nilpotent Jacobian part.
  - `druzkowski_map.py` + `verify_druzkowski.py` — explicit **Drużkowski-form**
    (x_i + (Ax)_i³) counterexample.

### ai/sae-grounding/ — The Intervention-Grounding Gap (Gemini: VERIFIED-SOUND)

`intervention_grounding_gap.md` (author: Reuel Lee; revisions applied in two-round
review) + `verify_intervention_grounding.py` (31 exact-Fraction checks): exact theorem
— two SCMs with fixed named concepts, identical labels, the same invertible activation,
identical transcript distributions under ANY adaptive internal-intervention protocol,
yet different semantic do-distributions. Internal causal relevance does not identify a
semantic causal ontology. Includes a swap-symmetric witness defeating any equivariant
selection rule, and a corollary at the SAE absorption wall. `REVIEW.md` documents the
full referee pass.

### ai/coherence-distortion/ — coherence penalties provably distort features (Gemini: VERIFIED-SOUND)

`overcomplete_coherence.md` + `verify_overcomplete_coherence.py` (certificate script by
Reuel Lee; class-wide bounds added in review): at λ=1/5, β=1/16, an explicit rational
5-12-13 frame strictly beats EVERY 3-atom dictionary containing the true features under
the Gram penalty (class-wide faithful objective is exactly 19/100+β by a one-line KKT
argument), with a mutual-coherence twin, a near-onset witness against the analytic
threshold λ(2−λ)/16, and a β=0 control proving the distortion is remedy-induced.

### ai/optimizer/ — convergence-theory counterexamples (Gemini: VERIFIED-SOUND)

`optimizer_counterexamples.md` + `verify_muon_ns.py`, `verify_lion.py`:
deployed-coefficient Muon falsifies the coverage claim of arXiv:2601.19156 (exact
one-step certificate + continuity obstruction: no orbit orthogonalizes for any number of
NS steps); an explicit family where 5-step Newton–Schulz has polar error > 0.9999 for
both coefficient sets; a vacuous stepsize condition in arXiv:2502.02900 Thm 3.1 for all
β ≥ 1/2; an exact period-2 cycle for default constant-hyperparameter Lion (contradicts
the informal claim only — the annealed theorems stand; scoping in the note).

### ai/interp-illusions/ — exact minimal interpretability-illusion networks (Gemini: VERIFIED-SOUND)

`certificates.md` + four verifiers: 6-param net where activation-patching variants
disagree and rank a provably inert component above the causal one; 18-param net where
gradient×input and Integrated Gradients put exactly zero attribution on the sole causal
feature; loss-optimal absorbed SAE whose sparse-feature-circuit is the causally inert
child latent (exact KKT); 4-param probing certificate that passes the Hewitt–Liang
control-task defense while probing a causally inert neuron.

### ai/maxout/ — smallest open case of a 2025 Sturmfels-et-al conjecture resolved; (4,6) resolved and (3,8) achievability confirmed; odd-n resistance certified

`attack_maxout66.md` + `verify_maxout66_d4n4.py` (+ `cert_d4n4.json`): explicit
32-vertex exact-rational certificate **confirming achievability in the smallest open
case (d,n)=(4,4) of Conjecture 6.6(2)** of Balakin–Cox–Loho–Sturmfels, *Maxout
Polytopes* (arXiv:2509.21286), where the paper had no computational evidence for d ≥ 4.
`target_list.md` is the ranked harvest of further attackable ML-theory conjectures.

**Second attack (2026-07-30)** — `attack_c66_deficit.md` + `verify_c66_new_cases.py`
(5 certificates, ~2 s, stdlib Fractions): **(4,6) = 104 confirmed** (part 2's first
n > d case; the conjectured maximum is the cap, so the case closes) and
**(3,8) = 110 confirmed** (achievability of the even-n formula at the first n beyond
the paper's DFS range). At the odd-n cases the conjectured maxima were **not
reproduced** despite the paper's own sampling recipe at 15× its budget, ~300
complete-per-direction-set branch-and-bound searches, and generator-drop seeding
from exact even-n extremals: certified exact counts **42/58/84** at
(3,5)/(4,5)/(3,7) vs conjectured 44/60/88. As of that note these were *lower
bounds only* and nothing was refuted; an out-of-sample-falsified intermediate
"deficit law" is documented there with full honesty scoping.

**Capstone (2026-07-31)** — `capstone/CAPSTONE.md`: **THEOREM, max f₀(3,5) = 42**,
so the (3,5) row above is now settled in both directions and the odd case of
Conjecture 6.6.1 is **refuted at n = 5**, as is the tightness of Prop 6.5 there.
The upper bound is 132,560 exact cell-wide Gordan certificates plus a symmetry
reduction to one oriented-matroid cell; the primary re-verification
(`capstone/independent_audit.py`, stdlib, ~2 min) imports nothing from the
programs that generated the library. A submission-ready note is in
`ai/maxout/paper/`. **(4,5) and (3,7) remain lower bounds** — 58 and 84 are
attained; whether their true maxima fall below 60 and 88 is open.

### ai/sae-unidentifiability/ — ρ-unidentifiability certificates (Gemini: r1 BLOCKING → r2 VERIFIED-SOUND)

`unidentifiability-certificate.md` + `verify_unidentifiability.py` (49 exact checks):
finite certificates that an absorbed child's conditional rate ρ is unidentifiable
label-free — culminating in Certificate C (interleaved cones: both dictionaries
support-irreducible, both strict hierarchies, both nonnegative, equal sizes, ρ = 3/4 vs
1/2), which survives the canonical-selection objection that blocked round 1; plus the
coupling identity E[L0]₁−E[L0]₂ = (ρ₁−ρ₂)·P(parent) (sparsity selection is biased, not
identifying) and a boundary map of anchors that do/don't restore identifiability.
Canonical home: the sae-identifiability repo (commit 1cd27e4); mirrored here.

### ai/absorption-metric/ — the absorption metric scores a zero-absorption dictionary (Gemini: SOUND)

`splitting_inflation.md` + `verify_splitting_inflation.py` (17 exact checks): the
SAEBench-style first-letter absorption metric reports a strictly positive rate on the
**loss-optimal, faithful** dictionary for a letter whose tokens are generated by *k*
distinct features — where absorption is zero by construction. The spurious rate is
exactly $1 - N_1/N$; its maximum over all zero-absorption configurations is exactly
$1-\tau$ and is **attained** (the scoring guard $\mathrm{sel}_j \ge \tau$ is
non-strict; sizes $(3,3,3,1)$ hit $7/10$ at $\tau = 3/10$); and the family-corrected
endpoint repairs it **iff** every split group clears $\tau$ — repairing nothing when
none do. A lemma shows the faithful dictionary attains the global per-event optimum
$\lambda r - \lambda^2/4$ while any merged atom is strictly worse for every
$0<\lambda<2$, so splitting here is the correct answer and the metric penalises it.
The metric is re-implemented line-for-line from the reference scorer, so the result is
about the code that produced the empirical rounds, not a paraphrase.

Positioned honestly: that single-latent scoring confounds splitting is folklore (it is
why the family endpoint exists); what is new is the attained bound, the iff, and the
optimality lemma. It is a **non-identification** result — the metric does not determine
absorption without an assumption it never checks — not a claim that any published
number is spurious. `RESPONSE_review.md` adjudicates the referee pass, including one
rejected [BLOCKING]: the objection "linear probes recover first letters, so there is a
monolithic feature" is refuted by this very construction, whose probe
$w=\sum_t u_t$ achieves margin 1 with no monolithic feature anywhere.

### ai/absorption-metric/ (2) — the metric cannot tell single-parent from distributed absorption (Gemini: SOUND)

`indistinguishability.md` + `verify_indistinguishability.py` (14 checks) +
`verify_m1_optimality.py` (10 checks): two generative models — one child absorbed into
ONE composite, versus *k* children absorbed into *k* composites — each carrying its own
**loss-optimal** dictionary, on which the metric returns identical values. Not merely
two matching rates: the entire per-token observable the metric consumes ($F_L$ firing
pattern, present, retained) is identical, so **every** statistic measurable from it
agrees. $F_L = \{a_L\}$ in both models because every composite falls below $\tau$, and
$a_L$ is *strictly* silent on the absorbed tokens (dual gradient
$\lambda(1-1/\sqrt2) > 0$), so the construction is robust rather than knife-edge.

Optimality is the load-bearing half and was gated before anything was written around
it: at $\varepsilon = 0$ Theorem 1b pins the optimal direction set uniquely, excluding
the tilt hazard that makes $\varepsilon^*$ a pure-strategy rather than a global
boundary. Verified with the nonnegative lasso solved by KKT active-set enumeration —
the faithful dictionary is strictly worse by $39/100-\sqrt2/5$, and all 16
Pythagorean-triple tilts lose.

$\varepsilon = 0$ is not the restriction it appears to be. It is the *correct* model
for first-letter absorption — a token like *short* cannot occur without starting with
s, so the child-solo rate is zero by the semantics of the task, and the certificate
sits in exactly the regime of the metric it critiques. And for $\varepsilon > 0$ the
restriction lifts with one extra atom: the tilt is an artifact of a 2-atom dictionary,
whereas $\{a_L, a_m, a_c\}$ makes every event 1-sparse and so attains the bound at
**any** $\varepsilon$, with $a_L$ still silent on joint events and $a_c$ never entering
$F_L$. The real condition is dictionary capacity, which an $8\times$ overcomplete SAE
always has.

The bound is **sharp**: at $k/N_L = \tau$ the composite is swept into $F_L$ and
`rate_family` diverges (0 versus 3/10) — the family endpoint regains power there, while
`rate_single` stays blind because it reads only the argmax latent. The **repair** is a
statistic reading outside $F_L$: modal-carrier share is $1$ for single-parent against
$1/k$ for distributed. That is exactly round 14's P2, so the theory makes the carrier
check a *necessity* rather than an extra — and run on real Pythia-1.4B SAEs it answers
**distributed** (14.1% against a 34.0% null).

### ai/coherence-transfer/ — THIRD-PARTY empirical result, verified and replicated here

**Not this repo's own work.** "Causal-Ontology Inversion in Overcomplete Sparse
Autoencoders" was produced in a separate GPT session; what is ours is the verification.
Unlike everything else here, this is an *empirical* result (120 trained SAEs on
digit-classifier activations with two planted factors), so it cannot be settled by a
finite exact certificate — it is settled by independent recomputation and replication.

`audit_dossier.py` is self-contained: give it the dossier and nothing else and it
extracts all 17 appendices, recomputes every registered statistic from the raw 120-row
table, reproduces the 20,000-replicate bootstrap **bit-exactly**, and re-applies the
decision rules. `REPLICATION_RECORD.md` then retrains all 120 SAEs from the frozen
sources on different hardware. Both primary effect sizes land within 2.4e−3 of the
originals (L1 ΔA −0.2549 vs −0.2553; TopK −0.4068 vs −0.4092), 12/12 seed signs, all
gates pass, and P1/P2/P3 come out identically.

The registered claim is that a strong coherence penalty destroys the *one-atom*
encoding of a planted factor while the *family* still carries it. It does: at β=0.5
single-atom alignment falls to 0.47/0.52 against a computed chance baseline of **0.434**,
while family cosine holds at **0.994/0.983** across ~19/~8 atoms. Redistribution, not
erasure.

Read with four disclosures, stated in full in `IMPORT_ADJUDICATION.md`:
its preregistration has **no trusted timestamp** (treat as post-hoc — the one risk that
cannot be retired); it is **not byte-reproducible** even at exactly matched library
versions, because dataset construction is BLAS-dispatch dependent; the planted factors
are exactly orthogonal, so generalisation to correlated natural features is untested;
and TopK's β=0 alignment is near-ceiling (0.973), so the L1 arm (0.730) carries the
headroom. Three defects are flagged for the original authors rather than patched here.

Of independent interest: the L1 dose profile is non-monotone — alignment 0.730 (β=0) →
**0.965** (β=0.0625) → 0.472 (β=0.5) — the same qualitative shape that
`ai/coherence-distortion/` and the sibling `sae-identifiability` paper derive
analytically, where a Gram penalty helps at moderate strength and *overdosing worsens
it*. An exact toy analysis and a semi-real 120-SAE sweep agreeing on that is a cheap
cross-check worth having.

### reviews/ — adversarial reviews (Gemini 2.5 Pro via gemx)

One review per result set; the unidentifiability result carries two rounds
(BLOCKING → revision with a strengthened construction → VERIFIED-SOUND). The
coherence-transfer review is a *meta*-review — Gemini auditing our audit — and its
three raised risks are adjudicated in `ai/coherence-transfer/IMPORT_ADJUDICATION.md`
rather than adopted wholesale: one is closed by replication, one is downgraded (the
experiment's own TopK fixed-L0 gate already controls the confound it names), and one
is permanent and disclosed.

## Provenance

Each result was produced by a Fable agent, independently re-verified by the
orchestrator (all verifiers re-run from scratch), then adversarially reviewed by
Gemini 2.5 Pro. Reviews that returned MINOR issues were applied before import;
BLOCKING results are excluded. The Jacobian-fallout scripts passed verification but
their prose write-up was interrupted (session limit); claims there are scoped to
exactly what the scripts print.
