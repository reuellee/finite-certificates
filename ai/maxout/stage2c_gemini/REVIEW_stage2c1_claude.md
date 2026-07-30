# Review of Stage 2c-1 (Gemini 3.1 Pro High via agy) — adversarial verification

Reviewer: Claude (this repo's session agent), 2026-07-31. Three bounded agy
calls (one infra retry, one scope retry) plus a rescue-agent close-out; see
`STAGE2C.md` and the call prompts/logs for the full trail. Every
load-bearing claim was re-verified independently below.

## The one positive result — VERIFIED BY DERIVATION, with two review notes

**The single-class equal-pair family is correct and cell-wide.** For a
system (σ, s): if some class (i, j) has σ_{ij,+} = σ_{ij,−} = σ* and
σ*·s_t = −1 for all three t ∉ {i, j}, then
y_{(ij,+)} = y_{(ij,−)} = 1, y_{w_t} = 2·D_{tij} (t ∉ {i, j}), all other
multipliers 0, is an exact Gordan certificate: the T-columns cancel by the
equal pair, each weight column t sums to 2·σ*·s_t·D_{tij} + 2·D_{tij} = 0,
and columns i, j are untouched. All multipliers are positive monomials in
the D's, so validity holds on the entire chirotope cell — no
Grassmann–Plücker reduction even needed. The reviewer verified this by
direct derivation (stronger than the sampling in `check_generic_factor2.py`,
which is confirmed as well: factor-1 fails 0/25, factor-2 passes 25/25).

Review notes: (1) the serialized entry's missing factor 2 (the executor's
own documented erratum) is confirmed — the corrected normalized form above
also drops the superfluous common factor D_{t1t2t3} carried by the
executor's version; (2) the family is precisely an equal-pair certificate
with weight-row support, i.e. a *symbolically explicit* member of the
Stage 2b-1 class, which is what makes the consistency check below sharp.

**Coverage independently reproduced:** the reviewer's own bit-scan of the
kill condition over all 33,140 × 2 labeled systems gives exactly **33,437**
(matching the executor). Scope caveat verified: **0** of the 100
hard symbolic targets and **0 canonical members** of either split's
equal-pair residue are covered — the family lives in the easy region.

## The consistency triangle — RESOLVED, with an accounting finding

A naive overlap test suggested the family kills thousands of "residue"
systems, seemingly contradicting Stage 2b-1's exact no-gos. Resolution
(established by direct computation): Stage 2b-1's coverage/residue lists
are **per canonical representative** (one labeled member per global-flip
class), and the equal-pair property is **not flip-invariant**. The family
kills **0 canonical residue members at their residue split** — exact
agreement with the no-gos — while killing 2,127 (k=1) + 2,628 (k=2)
**flip partners**, whose equal-pair status Stage 2b-1 never measured.

Two consequences for the ledger: (a) no artifact is wrong; (b) the
per-representative accounting in Stage 2b-1 *undercounts* the labeled
systems still lacking any T-independent certificate — Stage 2c-2 must
work at labeled-system granularity, and the family's 4,755 flip-partner
kills at residue splits are genuine coverage beyond Stage 2b-1's measured
set.

## The audit — ENDORSED, independently confirmed

Call 2's five claimed per-instance cell-wide certificates are invalid, as
the executor's own audit found (verifier sign bug, `-=` for `+=`). The
reviewer confirmed independently: e.g. the idx-32316 entry applies the
family template to a system where σ*·s_t = **+1** on all three
complementary generators — the exact opposite of the requirement — so its
weight columns sum to a strictly positive quantity, not zero. The
canary-target design (wiring a provably-impossible residue class into the
search set) is what exposed the bug; this practice should be standard in
all future certificate searches. Stage 2b-1's no-go for the colliding
class was independently re-confirmed by the executor's exact primal
witness.

## Honest negatives — ACCEPTED

Numeric rational-function fitting at U_ints fails GP-ideal membership (the
fitting route to cell-wide identities is dead); undetermined coefficients
at degree ≤ 2 finds nothing on the two hard targets attempted; the hard
region (equal-pair residues + the failed-100) remains without cell-wide
certificates. Any success there requires T-carrying supports with genuine
GP-ideal cancellation (the Stage 2a 5-cycle pattern), likely degree ≥ 3 —
that, at labeled-system granularity, is Stage 2c-2's precise target.

## Verdict

ACCEPTED with corrections absorbed: one rigorously verified systematic
cell-wide certificate family (the first transferable mechanism beyond the
Stage 2a 5-cycle instance), exact coverage accounting, five false theorems
kept out of the record by audit, and a sharply characterized frontier.
The executor's STAGE2C.md and symbolic_certs.json are retained as the
historical record; this review carries the corrected family form and the
accounting finding.
