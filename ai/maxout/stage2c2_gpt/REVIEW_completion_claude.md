# Completion review: the full-complement and k=0 sweeps (2026-07-31)

Reviewer: Claude (this repo's session agent). This documents the two runs
that completed the cell-wide certificate chain after `STAGE2C2.md`, and the
independent verification performed.

## The runs

1. **Full-complement sweep** (`gp_all_d2_sweep.py`, the executor's script,
   restarted by the reviewer as four detached shards): all **32,843**
   systems outside the single-class family, at splits k ∈ {1, 2}.
   Outcome: **EXACT_CELLWIDE_CERTIFICATE for every system** — including
   all 14,850 HARD systems — zero no-gos, zero empirical/undecided, all
   shards `status=complete`, canary controls passing inside every shard
   (~18.5 min/shard). Artifacts `gp_all_d2_shard_0{0..3}_of_04.json.gz`.
2. **k = 0 sweep** (`k0_cellwide_sweep.py`, written by the reviewer,
   driving the executor's exact machinery with the all-minus split):
   all 33,140 valid labeled sigmas. Outcome: **32,570 covered by the
   single-class family criterion** (with s = all-minus the criterion
   degenerates to "some class has both sides +1") and **570 by exact
   degree-2 quotient-ring certificates** — zero no-gos. k = 5 follows by
   the global flip (σ, s) → (−σ, −s). Artifact
   `k0_cellwide_shard_00_of_01.json.gz`.

## Independent verification (this review)

- **970/970 certificates re-verified with reviewer-owned code**: 400
  sampled uniformly across the four sweep shards plus all 570 k=0
  certificates. For each: decode the (side/weight, monomial) variable
  layout, evaluate multipliers at the reference determinant values, and
  check nonnegativity, nontriviality, and Bᵀy = 0 in all eight columns
  against the reviewer's independently written row builder. Zero failures.
- The earlier representative-certificate check (symbolic T-cancellation
  identically zero over generic vectors) and the executor's
  generation-time exact quotient-ring verification stand as the cell-wide
  half; a single standalone end-to-end re-audit of all ~99k certificates
  (quotient-ring identities included) has NOT yet been run in one pass and
  is listed below as remaining work.

## The assembled chain (statement of what is now established)

For every valid labeled side assignment σ and every split s (k = 0…5, via
flip symmetry for k ≥ 3), there is an exact cell-wide Gordan certificate —
single-class family, equal-pair, or degree-(2,3) quotient-ring — valid for
every configuration realizing the reference chirotope. Together with:

- **Equivariance**: the uniform OM(3,5) chirotopes form a single orbit
  under relabeling × reorientation × negation (computed exhaustively:
  `check_om35_uniqueness.py`, 384 chirotopes, one orbit). The certificate
  data transports along this group action (it permutes/sign-flips the D
  variables and relabels sides, splits, and σ's; the GP ideal is
  invariant; coefficient nonnegativity is preserved), so the
  reference-cell library covers every generic configuration.
- **Non-generic configurations**: chambers of a central arrangement come
  in antipodal pairs, and a non-simple (or deficient) arrangement of ≤ 5
  planes has strictly fewer than 22, hence ≤ 20 chambers; so
  f₀ ≤ 2 × 20 = 40 < 42 there — no certificates needed.
- **The 43-exclusion**: the bipartite-parity + strict-witness-perturbation
  argument (verified in the Stage 2b review), applied per configuration.
- **Attainment**: `cert_35_42.json` (42 vertices, exact).

this yields, pending the remaining work below, the capstone claim
**max f₀(3,5) = 42 over all (3,5)-zonoboxtopes** — refuting the
conjectured value 44 of Conjecture 6.6.1 (odd case) of arXiv:2509.21286 at
n = 5, and the tightness claim of its Proposition 6.5 at n = 5.

## Remaining before the capstone is declared

1. A single standalone auditor re-verifying every certificate in every
   bundle (quotient-ring identities and specialization) in one run —
   multi-hour; not yet executed.
2. The equivariance and non-generic paragraphs above written out as a
   careful standalone argument (the transport bookkeeping under
   reorientation is where an error would hide) and subjected to a
   maximum-settings dual review (Gemini + GPT), given the stakes.
3. The capstone document itself (theorem statement, full component list,
   verification instructions).
