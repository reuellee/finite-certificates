# Review: "The Intervention-Grounding Gap" (SAE identifiability series, 2026-07-25)

**Reviewer:** Claude (rigorous-math review pass), 2026-07-25
**Materials:** the intervention-grounding note, repository standards, the sibling
unidentifiability result, and its archived blocking review.
**Independent verifier:** `verify_intervention_grounding.py` — reconstructed
from the note's stated parameters, exact `Fraction` arithmetic, **31/31 PASS, exit 0**.

**VERDICT: INCLUDE AFTER REVISIONS (all minor except one repo-standard gap: the claimed
companion verifier does not exist on disk and must ship).** The mathematics is correct;
every number in the note reproduces exactly; the killer canonical-choice objection that
blocked the sibling note does **not** transfer to this one, for a structural reason
analyzed in §4 below.

---

## 1. Mathematical assessment

### 1.1 The construction (§4 of the note) — correct, verified exactly

All arithmetic checks out, independently reconstructed and machine-verified:

- Forward SCM `P~Bern(1/2), Pr(C=1|P=0)=1/4, Pr(C=1|P=1)=1/2` and reverse SCM
  `C~Bern(3/8), Pr(P=1|C=0)=2/5, Pr(P=1|C=1)=2/3` both reproduce Table 1
  ((3/8, 1/4, 1/8, 1/4), strictly positive) exactly. Hence identical laws of
  X=(P,C), identical labels, identical input to any SAE learner.
- Every entry of Table 2 is correct: internal settings give E[Y] ∈
  {3/4, 7/4, 1/2, 5/2} in **both** models; semantic do-means are
  (1/2, 2, 1/2, 5/2) forward vs (3/4, 7/4, 2/5, 8/3) reverse. All four pairs
  differ — the separation is not on a single knife-edge intervention.
- A structural identity the note states in prose and my verifier confirms: the
  internal edit set(X_P=p) coincides exactly with the **reverse** model's do(P=p),
  and set(X_C=c) with the **forward** model's do(C=c). So every internal experiment
  is consistent with *some* semantic ontology — internal results cannot even be
  used as a partial vote for a direction.
- General family (§5): correct. For any strictly positive dependent binary joint,
  do(P=p) gives C ~ Pr(C|P=p) in one factorization and C ~ Pr(C) in the other;
  dependence forces inequality for some p. Standard, and honestly labeled standard.
- Absorption-wall corollary (§6): conditionals q/(p0+q) and p0/(1−q) are correct;
  verified at p0=q=1/4 and at a second generic point (1/8, 1/3). Pr(C=1|do(P=0))
  = 0 vs q. Note the wall joint has a zero cell and each SCM has one deterministic
  mechanism; the note correctly keeps this as a secondary compatibility remark with
  the strictly positive witness primary. Keep it that way.

### 1.2 Theorem 1 (adaptive descendant-intervention equivalence) — correct, but a proof sketch

The claim is genuinely stronger than one-shot distribution equality: equality of the
**complete transcript law of any finite randomized adaptive protocol**. The coupling
argument given (same observational sample, same learner/protocol randomness, induction
over rounds) is the standard and correct argument, and it is valid here. The load-bearing
step the task asked me to scrutinize — interventions **on X itself**, not merely on
descendants — is handled correctly in substance: an intervention set X ← T(X) (or a
stochastic kernel, or an SAE-code edit e(X) ↦ decoded X′, which is again a function of X)
produces a response whose law depends only on (i) the law of the pre-intervention draw
of X, which is shared, and (ii) downstream kernels, which are shared by hypothesis.
The pre-intervention draw is the *only* channel through which upstream structure could
enter, and it exposes only the joint law, never the factorization ("the upstream
factorization of the observational law is never queried" — correct). The no-feedback
assumption (internal operations do not affect upstream mechanisms) is stated and is
essential; without it the theorem is false, and the note says so (§7 boundary
conditions).

Weaknesses of rigor (fixable, none fatal):

- **W1 (formalization).** The protocol/transcript model is never defined: what a round
  is, that the round-t action is a transcript-measurable kernel on X and descendants,
  that fresh units are i.i.d. from the observational law, what "observe" returns. The
  proof is three sentences of the right shape but a referee can reasonably ask for the
  measure-theoretic (here: finite combinatorial) statement. In a finite discrete
  setting this is a half-page and should be written.
- **W2 (wording overclaim).** Abstract and Result-at-a-Glance say "identical
  observations and identical transcripts." What is proved is identical transcript
  **law** (with realization-level equality only under the constructed coupling).
  Say "identically distributed transcripts."
- **W3 (post-intervention label access).** The protocol "may inspect labels" and may
  intervene on X. The interaction is fine — the unit's semantic label is upstream of
  the intervention, unchanged, and equals φ⁻¹(X_pre), whose law is shared — but the
  note never says this, and it is exactly the kind of loophole a referee probes.
  One sentence closes it.
- **W4 (abstract conflation).** "A strictly positive four-state construction rules out
  relabeling and off-support explanations": positivity rules out *off-support* outs
  (all internal maps act on observed states; the do-differences occur on states of
  positive probability); the *fixed names/labels/loadings* rule out relabeling. §7
  separates these correctly; the abstract fuses them. Fix the sentence.
- **W5 (framing).** "Two models can have the same named concepts…" invites misreading
  as two neural networks. The two objects are world+network composites sharing the
  entire network; the difference lives wholly upstream. §7's operational-definition
  paragraph (if "concept" *means* the coordinate, internal edits are its interventions
  by definition) is the right scoping and should be echoed earlier.

**Is the "strictly positive" claim doing the work the note says?** Yes, for
off-support: every deterministic post-X map maps observed states to observed states, so
no argument can appeal to behavior on unseen inputs, and the semantic disagreements
occur at states of positive probability. Relabeling is blocked by the fixed-names
device, not by positivity (see W4). Both devices work; only the abstract's attribution
is sloppy.

### 1.3 Verdict on the mathematics

Correct throughout. No numerical errors found (28 note-derived checks pass). Theorem 1
is true as stated for the static feed-forward setting, with the proof needing the W1
formalization to meet certificate-grade prose standards. Corollary 1 and the general
family are correct. Claim ledger (Table 4) statuses are accurate.

## 2. Verifier report

The note's Appendix A cites a companion script `verify_causal_ontology.py` with
terminal condition "ALL EXACT CHECKS PASSED." **That script does not exist in either
repo or anywhere findable on this machine.** Under the finite-certificates standard —
"every claim ships with a standalone verifier" — this is the one blocking-grade gap:
an appendix asserting a machine-check result for a script that is not shipped.

However, the note **is fully reconstructable**: every rational parameter needed is in
the text (Table 1; §4.2 mechanisms; Y=P+2C; Table 2 targets; §6 wall formulas and the
p0=q=1/4 instance). I implemented `/tmp/igg_review/verify_intervention_grounding.py`
(pure `Fraction`, no floats, python3 stdlib only): **31/31 PASS, exit 0.** Coverage:

1–3. Both factorizations reproduce Table 1 exactly; joints identical; strict positivity.
4. Internal settings match Table 2 col. 2 under both models (computed from each
   model's own factorization, not the shared table).
5. All four semantic do-means match Table 2 and the full do-*distributions* (not just
   means) differ between models for every target setting.
6. All 4⁴ = 256 deterministic post-X maps give identical pushforward laws of (X′, Y′)
   under both models.
7. Two exact rational stochastic kernels (one mixed 4-row kernel, one steering-style)
   give identical pushforwards — spot-checking the "stochastic maps follow" claim.
8. An exact **adaptive 2-round transcript law** (round-2 map chosen from the round-1
   observation) computed in full under both models: identical. This spot-checks the
   Theorem-1 reduction beyond the note's own 256-map check.
9. Wall corollary at p0=q=1/4 **and** a second generic point (1/8, 1/3).
10. The internal-edit ≡ child-model-do identity (§1.1 above: set(X_P) ≡ do(P) in
    M_{C→P}, where P is the child and root C keeps its marginal; set(X_C) ≡ do(C)
    in M_{P→C}).
11. (Reviewer extension, see §4:) a swap-symmetric witness with the same separation.

Adaptive/stochastic reduction argument: stochastic kernels are convex combinations of
the 256 deterministic maps with model-independent weights, so check 6 implies check 7;
adaptivity adds only transcript-measurable selection among kernels, and since each
round's response law is model-independent (checks 6–7) and fresh draws share their law,
induction gives transcript-law equality — check 8 confirms this concretely and exactly
for a genuinely adaptive protocol. The reduction is sound.

**If the author's own script materializes it should be diffed against this one; either
script satisfies the repo standard, but one must actually be in the repo.**

## 3. Prior art and novelty

The note's own positioning is honest and mostly right: the mathematical core is
textbook two-variable Markov-equivalence non-identifiability (Pearl), and the note
disclaims it in three separate places (abstract, §8, Table 4). The question is whether
the *SAE-specific* claim — a transcript-level equivalence theorem for adaptive
internal-intervention protocols, with an exact positive-support witness — is already
published. A dedicated web-search pass (multi-thread, abstracts plus one full text)
found:

- **Causal abstraction (Geiger, Icard, Potts, Wu; interchange interventions, DAS;
  arXiv:2301.04709 = JMLR 2025, arXiv:2303.02536).** The framework is explicitly
  hypothesis-relative: it posits a high-level causal model and validates an alignment
  relative to it. The folklore that internal interventions validate correspondence
  only *given* the high-level model is embedded in that setup, but no negative theorem
  is proved there. **The note currently does not cite this line at all — a real gap.**
- **Two formal near-misses that MUST be cited and distinguished:**
  - *Sutter, Minder, Hofmann, Pimentel, "The Non-Linear Representation Dilemma"*
    (NeurIPS 2025, arXiv:2507.08802): a genuine impossibility theorem — with
    unconstrained (non-linear) alignment maps, any network can be causally abstracted
    to any algorithm (100% interchange-intervention accuracy even on random networks).
    **Different lever:** their non-identifiability comes from freedom of the alignment
    map; the note holds the map fixed and invertible (X=(P,C), identity alignment) and
    locates the ambiguity in the upstream semantic SCM. Orthogonal, and the note's
    fixed-map setting arguably makes its separation the sharper complement — but a
    referee will demand the comparison.
  - *Makelov, Lange, Nanda* (arXiv:2311.17030): a constructed formal counterexample
    where subspace patching succeeds via a dormant, causally disconnected pathway.
    Single-counterexample, about which subspace encodes a feature (the note's Level
    B), not about upstream semantic ontologies, not protocol/transcript-general. The
    Geiger et al. reply (arXiv:2401.12631) shows the community treats this as
    contested methodology, not settled theorem.
- **Méloux, Portet, Maniu, Peyrard, "Is Mechanistic Interpretability Identifiable?"**
  (ICLR 2025, arXiv:2502.20914): systematic *empirical* enumeration showing multiple
  algorithms causally align with one network. No theorem, no adaptive-protocol
  formulation, no SAEs. Cite as empirical precedent.
- **Interpretability illusions (Bolukbasi arXiv:2104.07143; hydra effect
  arXiv:2307.15771; Zhang–Nanda arXiv:2309.16042)** — empirical/methodological, Level
  B; none formalizes upstream-ontology underdetermination.
- **Philosophy / steering critiques:** Millière & Buckner (full text checked: survey,
  no theorem); Harding 2023 (criteria, not theorems); AxBench (arXiv:2501.17148,
  empirical); Leask et al. "SAEs do not find canonical units" (arXiv:2502.04878,
  empirical, about dictionary non-canonicality); "Causality is Key for
  Interpretability Claims to Generalise" (arXiv:2602.16698) — nearest 2026 framing,
  Pearl-hierarchy diagnostic, again no equivalence theorem. The "control ≠ encoding"
  gap is stated informally in the 2025-26 steering literature.
- **Causal representation learning (von Kügelgen arXiv:2306.00542; Ahuja; Squires;
  Varici; Welch — the note cites the right ones).** These prove the *complement*:
  identifiability from latent-/world-level interventional environments. No published
  theorem was found isolating the representation-level-vs-latent-level intervention
  distinction as an impossibility result; it survives as implicit background. No hits
  for "intervention grounding" or adaptive-transcript formulations.

**Novelty verdict: (b)/(c) boundary, leaning (c) — the idea is folklore-published
(gestured at repeatedly, formally proven never in this form); the adaptive-protocol
transcript-equivalence theorem with fixed invertible anchoring and an exact
positive-support witness appears genuinely new as a formalization.** The note's own
"transparent corollary / formulation is the contribution / venue-level novelty
requires expert review" framing (§8, Contribution Statement, §11) is exactly
calibrated to this and should be kept. Required revision: cite and position against
Geiger et al. (causal abstraction), Sutter et al. 2507.08802 (the alignment-map-lever
impossibility), Makelov et al. 2311.17030, and Méloux et al. 2502.20914; their absence
is the note's most conspicuous prior-art omission. Residual risk: the discussion
sections of 2507.08802 and 2502.20914 were checked at abstract/summary level only.
Minor: citation metadata is inconsistent (Ding et al. "2026" with a 2509.* arXiv id;
Mencattini "2026" with 2510.*) — fix years or ids.

## 4. Fit with the sibling result, and the canonical-choice objection

### 4.1 Consistency and complementarity

The two notes are consistent and cleanly complementary along the note's own §12
hierarchy: the sibling certificate attacks **observational** identifiability of a
representation-relative quantity (ρ, an absorbed child's rate); this note attacks
**internal-interventional** identifiability of a world-relative quantity (a semantic
do-distribution). The wall corollary (§6) deliberately reuses the sibling's
distribution, and — importantly — it does **not** depend on any claim of the sibling
that Gemini blocked: it needs only the distribution itself, and its phrasing ("any
fixed canonical solution selected in the companion two-atom analysis … is common to
the two SCMs") in fact *composes gracefully with* the sibling's pending revision: even
after a canonical-selection convention fixes the SAE decomposition, both SCMs share
that canonical solution and all its ablations, and the do-gap survives. The reference
to the companion analysis should just be annotated "under revision."

### 4.2 Does the support-reducibility/canonical-choice objection transfer? — No, and for a structural reason

Gemini's killer objection to the sibling had this shape: the two competing
decompositions were **asymmetric in redundancy** (a 3-feature dictionary containing a
composite u reducible to a 2-feature one), a **standard convention** in the relevant
literature (support-irreducibility in NMF/dictionary learning) canonically rejects the
redundant competitor, and the ambiguous quantity ρ was **representation-relative** —
"a purely nominal artifact of how we label activations" — so once a convention fixes
the representation, the ambiguity dissolves. All three legs fail here:

1. **No redundancy to reduce.** M_{P→C} and M_{C→P} are both edge-minimal faithful
   Markovian SCMs: two variables, one edge, three free parameters each, identical
   support, identical description size. Neither is a sub- or super-model of the other;
   both satisfy minimality and faithfulness. There is no analogue of "the dictionary
   contains a redundant column" for a convention to bite on.
2. **The only candidate selection rules are substantive assumptions, not
   conventions.** What could prefer a direction? Cause-effect inference heuristics:
   algorithmic independence of mechanisms (ICM), MDL on mechanism descriptions,
   additive-noise-style asymmetries. Two answers. (i) These are inductive assumptions
   about the world, and the note *already scopes them out explicitly* — §7 lists
   "structural restrictions / additive-noise asymmetries / known causal graph" as
   things that break the equivalence. Invoking one changes the inference problem; it
   does not refute the theorem, whereas support-irreducibility could plausibly be
   claimed as part of the *definition* of the sibling's problem. (ii) Constructively:
   take the swap-symmetric witness Pr(0,0)=Pr(1,1)=3/8, Pr(0,1)=Pr(1,0)=1/8
   (dependent, strictly positive; forward and reverse mechanisms are exact mirror
   images: root Bern(1/2), conditionals 1/4 and 3/4). Any selection rule that is a
   function of the observational law and equivariant under exchanging the two named
   coordinates must score both factorizations equally — yet Pr(C=1|do(P=0)) is 1/4
   in one and 1/2 in the other. Verified exactly (checks 11–11c). **Recommend adding
   this witness to the note as a dedicated "no canonical choice" subsection** — it is
   the certificate-grade pre-emption of the objection class that killed the sibling.
3. **The disputed quantity is operationally anchored, not nominal.** This is the
   deepest disanalogy. At the sibling's Level 2, the two readings induce the *same*
   distribution over everything that exists in the model — no experiment even in
   principle separates them, which is precisely what made a conventionalist
   resolution ("ρ is representation-relative; pick the canonical representation")
   available. Here the two SCMs are separated *in principle* by a physically
   meaningful experiment — a world-level do(P) — which the theorem's protocol class
   merely excludes. Adopting a canonical model cannot make the world's response to a
   real intervention come out right: if the data were generated by M_{C→P} and you
   canonically adopt M_{P→C}, your prediction for an actual semantic intervention is
   wrong by 1/4 in expected score. Non-identifiability of an in-principle-testable
   quantity from a restricted experiment class is the classic form of a causal
   non-identifiability theorem (Markov equivalence); nobody calls the direction of
   causation a naming convention. The Gemini move is structurally unavailable.

   Residual exposure: a hard-line reviewer could press a *closed-world* variant — "if
   the semantic layer is only ever accessible through X (concepts purely
   hypothesized), the difference is metaphysics." The note's §7 final paragraph
   already contains the correct answer (the theorem applies exactly when the
   coordinate is *interpreted* as recovering a variable whose interventions are
   defined outside it — and real SAE practice does interpret features this way), but
   this defense should be promoted from a boundary remark to a visible paragraph,
   since it is the one attack surface of the same genus as the sibling's.

### 4.3 Shared weaknesses

Both notes share the "population-level, exact, no finite-sample statement" scope; both
say so. This note is additionally clean of the sibling's other Gemini findings (no AMR
positioning, no ICA claim, no coordinate-space loophole — the wall's zero cell is the
only degenerate-support object and it is explicitly non-primary).

## 5. Verdict and recommendations

**INCLUDE AFTER REVISIONS.** None of the revisions touches the mathematics, which is
fully correct and now doubly machine-verified.

Required (blocking for repo inclusion):
1. **Ship the verifier.** Appendix A cites `verify_causal_ontology.py`, which does not
   exist on disk. Adopt `/tmp/igg_review/verify_intervention_grounding.py` (31/31
   PASS; strictly broader coverage: per-model factorization recomputation, full
   do-distribution inequality, exact adaptive 2-round transcript law, stochastic
   kernels, second wall point, symmetric witness) or produce the original and diff.
2. **Formalize Theorem 1's protocol model** (W1): define rounds, transcript,
   transcript-measurable kernels on X/descendants, no-feedback; state intervention
   semantics X ← T(X, ω) and the one-line lemma that responses depend only on the
   shared X-law and shared downstream kernels. Half a page in the finite setting.
3. **Add the missing prior-art positioning** (see §3): causal abstraction
   (Geiger et al., arXiv:2301.04709/2303.02536), the Non-Linear Representation
   Dilemma theorem (Sutter et al., arXiv:2507.08802 — different lever, must be
   distinguished explicitly), Makelov–Lange–Nanda (arXiv:2311.17030), and Méloux et
   al. (arXiv:2502.20914). Their absence is the note's only real prior-art hole; the
   conservative novelty framing otherwise survives the literature check.

Recommended (strengthening):
4. Add the swap-symmetric witness as a "no canonical selection" subsection (§4.2
   above); exact parameters and verification are in checks 11–11c of my script.
5. Fix W2 ("identically distributed transcripts"), W3 (post-intervention label
   sentence), W4 (abstract's positivity-vs-relabeling attribution), W5 (two
   world+network composites, not "two models").
6. Annotate the §6 reference to the companion two-atom analysis as "under revision";
   note the wall corollary is independent of the blocked ρ claim.
7. Fix citation metadata (arXiv id/year mismatches for Ding et al., Mencattini
   et al.; verify Klotz et al. id).

**Placement:** the note carries "SAE identifiability series" branding, but by content
and standard it belongs in **finite-certificates** (ai/ family, e.g. a new
`ai/sae-grounding/` beside `ai/interp-illusions/`, whose absorbed-SAE certificate it
directly extends): it is exactly a small, explicit, machine-checkable exact result
with scrupulous scoping. The sae-identifiability repo can carry a pointer. Given the
sibling's BLOCKING status, the wall corollary's cross-reference should be worded so
this note stands even if the sibling is withdrawn (it does — see §4.1).
