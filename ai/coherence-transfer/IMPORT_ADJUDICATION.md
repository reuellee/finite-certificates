# Import adjudication — "Causal-Ontology Inversion in Overcomplete Sparse Autoencoders"

**Question asked (2026-07-25 23:11):** is this externally produced report ready to add
to `finite-certificates`?

**Answer: yes, as `ai/coherence-transfer/`, with three disclosures that must travel
with it.** One of the three blocking risks raised in review is now closed by
independent replication; one is permanent and must be stated; one is largely
answered by the experiment's own design and is downgraded.

Inputs: `Causal_Ontology_Coherence_Inversion_Report.pdf`,
`EMPIRICAL_VERIFICATION_DOSSIER.md` (4,900 lines, appendices A–Q, 120 SAEs),
`AUDIT_REPORT.md` + `audit_dossier.py` (this directory),
`reviews/GEMINI_coherence_transfer_audit_review.md`.

---

## 1. Where the audit stands

`audit_dossier.py` is self-contained: it extracts all 17 appendices from the dossier,
recomputes every registered statistic from the raw 120-row table, re-runs the
20,000-replicate bootstrap, and re-applies the decision rules. **87/88 checks pass.**
The bootstrap reproduces *bit-exactly* across numpy versions; the 22 paired contrasts
and all CI endpoints reproduce to ≤2e-15. The single FAIL is a hard-coded stale
literal at the 6th decimal in one narrative template (§5 TopK ΔA printed as
−0.409225 against a true −0.409197) — it touches no registered artifact and no
verdict, and it is kept as a FAIL rather than waived.

That establishes **arithmetic and code integrity**. It does not, by itself, establish
that the experiment happened as described. The three risks below are about that.

---

## 2. The three raised risks, adjudicated

### (i) No trusted preregistration timestamp — VALID, PERMANENT, must be disclosed

The hash lock proves the analysed code equals the locked code. Nothing in the dossier
proves *when* Appendix A was written relative to the confirmatory runs. Nothing can
fix this retroactively — a self-certified preregistration inside a single local
document has no prospective standing.

**Required disclosure:** the import must state that for verification purposes the
analysis is treated as **post-hoc**, and that the preregistration's timing is
asserted, not attested.

*Practice note, since this recurs:* the fix is free going forward — push the lock
commit to a public remote **before** the confirmatory run. That is exactly what makes
`sae-identifiability`'s round-14 lock (`2a81a98`, public before its results existed)
attestable, and it costs nothing to do every time.

### (ii) The physical experiment was never replicated — NOW CLOSED

This was correct when raised. It is closed by the independent retrain recorded in §3:
120 SAEs rebuilt from the frozen sources on a different machine, in a clean
environment, and compared against Appendix H.

### (iii) Construct confounds — SPLIT: one half wrong, one half anticipated by design

The review made two distinct claims here. Neither survives as a blocker.

**(a) "At β=0 the one-atom alignment metric is guaranteed to be trivially high,"**
because the planted factors are 1-sparse in an orthogonal basis, so an overcomplete
dictionary aligns with them for free.

*Wrong for L1, right for TopK, fatal for neither.* Measured mean
`factor1_max_absolute_cosine` at β=0 is **0.7297 for L1** — far from any ceiling, with
ample headroom — and **0.9732 for TopK**, which is indeed near-ceiling and should be
disclosed. But the ceiling story cannot explain the actual result, because of what
happens at the other end. I computed the **chance baseline** for this statistic
(max |cos| between a fixed direction and m=68 random unit atoms in d=34): mean
**0.4344**, 95th percentile 0.5423. Observed at β=0.5: L1 **0.4716**, TopK **0.5184**.

So single-atom alignment does not merely decline, it **falls to chance**. Meanwhile
`factor1_family_cosine` at β=0.5 is **0.9940 (L1)** and **0.9833 (TopK)**, with the
factor spread over ~19 and ~8 atoms respectively. Regression from a favourable
baseline produces neither of those things. The registered wording — "one-atom
alignment falls **while the family survives**" — is precisely what the numbers show:
the factor is *redistributed*, not destroyed.

**(b) "L1 suffered massive L0 drift,"** confounding sparsity with the penalty.

*Real, and controlled by the design the review did not account for.* L1's held-out
L0 does drift badly, 15.7 → 30.2 across the β range. But **gate 4 pins every TopK run
to L0 within 0.05 of 16**, and the measured TopK L0 is exactly 16.0 at all five β
levels. The preregistration states the reason in as many words: *"Passing in TopK is
load-bearing because it rules out a change in $L_0$ as the sole explanation."* The
TopK arm shows the same fall-to-chance with the same family survival at fixed
sparsity. The objection is answered by the experiment, not by argument.

**Genuine residual concern, restated in the form that survives:** the planted factors
are exactly orthogonal to each other and to the representation subspace. That is
idealised, and it limits how far the result generalises to natural features, which
are correlated and non-orthogonal. This belongs in the import as a scope statement —
it is a generalisation limit, not a confound.

---

## 3. Independent replication — done, and it passes

Full detail in `REPLICATION_RECORD.md`. All 120 cells retrained from the frozen
sources on different hardware, ~13 minutes, no cost (the audit's stated blocker — "no
scipy/sklearn, no pip in this environment" — dissolves with `uv`, which brings its own
CPython and wheels).

| | registered | replication |
|---|---|---|
| L1 alignment ΔA | −0.255285 [−0.312468, −0.205723] | **−0.254870** [−0.312251, −0.205154] |
| TopK alignment ΔA | −0.409197 [−0.497319, −0.326966] | **−0.406754** [−0.495909, −0.323709] |
| P1 / P2 / P3 | SUPPORTED / SUPPORTED / TopK-only | **identical** |
| registered gates | pass | **pass** (TopK max\|L0−16\| = 0.0014) |

Both primary effect sizes land within 4e−4 and 2.4e−3 of the originals, 12/12
per-seed negatives in both architectures, and all three registered predictions come
out the same way.

**Nothing reproduces byte-for-byte, and the cause is identified rather than assumed.**
The dataset digest itself differs (`d00e7d6c…` → `2111f9dd…`) while shapes and
classifier accuracy match exactly, because `MLPClassifier(solver="lbfgs")` inside
`build_dataset` is BLAS-heavy and different CPU kernel dispatch changes summation
order. Library versions were matched *exactly* (numpy 2.3.5 / scipy 1.17.0 /
sklearn 1.8.0 / Python 3.12.13); glibc, kernel and CPU differ. Consequently the
byte-identity, 4-decimal and checkpoint-digest checks all fail while every scientific
verdict holds. Bit-exactness here would require pinning the CPU and BLAS kernel set,
which no package pin list can express.

**A defect this surfaced in the dossier's tooling.** The frozen
`analyze_coherence_transfer_semireal.py` calls the replication
*"UNINTERPRETABLE: one or more registered gates failed"* — but of its twelve
conformance sub-checks, eleven pass and the single failure is `data_hash`, compared
against a hard-coded expected digest. That makes the script **structurally unable to
certify any independent replication on different hardware**: it conflates "same
experiment" with "same machine". The substantive gates all pass. Any future dossier
should report the dataset digest as a diagnostic and gate instead on the dataset's
statistical fingerprint.

---

## 4. An unremarked connection to this repo's own results

The L1 dose profile is an inverted U — mean alignment 0.730 (β=0) → 0.941 → **0.965**
(β=0.0625) → 0.519 → 0.472 (β=0.5), with `faithful_geometry` going 0/12 → **12/12** →
0/12 across the same sweep. A moderate coherence penalty helps substantially; a strong
one is worse than none.

That is the same qualitative shape derived analytically in the sibling project
(`sae-identifiability`, PAPER §5.1): a Gram penalty "shrinks the absorption region at
most ~4×, never removes it, **and overdosing worsens it**", with the corrected boundary
$\varepsilon^{**}(\beta)$ increasing in β above β\*. Two independent routes — an exact
two-latent toy analysis and a semi-real 120-SAE sweep on digit-classifier activations —
land on the same non-monotone dose response.

Worth stating carefully: these are different setups measuring different quantities, so
this is qualitative agreement, not a replication of the toy result. But it is the kind
of cross-check that is cheap to note and easy to miss, and it makes both results
somewhat more believable.

---

## 5. Verdict and required import text

**Import as `ai/coherence-transfer/`**, carrying report, dossier, `audit_dossier.py`,
`AUDIT_REPORT.md`, this adjudication, and `REPLICATION_RECORD.md`. The README section
must state all five of:

1. The preregistration has **no trusted timestamp**; treat the analysis as post-hoc.
   This is the one risk that cannot be retired, and it is the only one left.
2. The **arithmetic is independently verified** (87/88; the one FAIL is a stale
   6th-decimal narrative literal) and the experiment is **independently replicated
   from source on different hardware** — both primary effect sizes within 2.4e−3,
   12/12 seed signs, all three registered predictions identical, all gates passing.
3. **It is not byte-reproducible**, at matched library versions, because the dataset
   construction is BLAS-dispatch dependent. Reported as a property of the experiment,
   not a defect: conclusions replicate, bytes do not.
4. **Scope:** planted factors are exactly orthogonal to each other and to the
   representation subspace; generalisation to correlated natural features is untested.
5. **TopK's β=0 alignment is near-ceiling (0.973)**; the L1 arm (0.730) carries the
   headroom, and the fall-to-chance plus family survival is what rules out a
   ceiling-regression reading.

Two corrections belong upstream with the original authors rather than being silently
patched here: the §5 TopK narrative literals are stale at the 6th decimal, and
`analyze_coherence_transfer_semireal.py`'s `data_hash` conformance gate makes the
script unable to certify any independent replication.

The work is not this repo's own and must be labelled as third-party, verified here —
consistent with how the Intervention-Grounding-Gap note was imported.

The work is not this repo's own and must be labelled as third-party, verified here —
consistent with how the Intervention-Grounding-Gap note was imported.
