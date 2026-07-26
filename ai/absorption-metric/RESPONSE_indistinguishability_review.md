# Response to `reviews/GEMINI_indistinguishability_review.md`

Verdict returned: **SOUND**, five findings, all [MINOR], no [BLOCKING] and no [FIX].

An all-clear deserves more scrutiny than a critical review, not less — a referee that
finds nothing is either right or not reading. So the one substantive technical claim it
made was checked independently, and two of the strengthenings it offered are declined
as overclaims.

## Verified independently

**The dual-gradient claim (F1).** The review asserted that on joint events the dual
gradient for $a_L$ is $\lambda(1 - 1/\sqrt2) > 0$, so $a_L$ is *strictly* inactive
rather than sitting at a KKT boundary. Recomputed symbolically:

$$2\,a_L^{\!\top}(Df - x) + \lambda \;=\; \tfrac15 - \tfrac{\sqrt2}{10} \;=\; 0.0586 \;=\; \lambda\!\left(1 - \tfrac{1}{\sqrt2}\right)$$

Confirmed. This matters more than the review made explicit: it means "no $F_L$ latent
fires on the absorbed tokens" is a strict inequality, not a tie broken by convention.
The impossibility is robust to perturbation of $\lambda$, not knife-edge. Added to the
record because it strengthens the certificate.

## Accepted, no change needed

- **F2 — $\varepsilon = 0$ does heavy lifting.** Agreed, and §6 already says so. The
  review's own reasoning for why the tilt hazard is excluded — both dictionaries hit
  the global per-event bound on *every* event type, so nothing can beat them — is the
  argument the optimality gate was built to establish.
- **F3 — not vacuous.** Agreed that M1 (a systematic recurring hidden feature, the
  thing absorption metrics exist to catch) and M2 ($k$ independent contextual
  composites) are genuinely different ontologies rather than a relabelling.
- **F5 — novelty.** Agreed, and the note already concedes the carrier statistic is not
  new. The contribution is the impossibility theorem, which upgrades the carrier check
  from a useful extra probe to a provable necessity.

## Declined — two offered strengthenings that overstate

**The review says the flaw "persists for any $\varepsilon > 0$ as long as
$k/N_L < \tau$."** Not adopted. The *metric-level* blindness is trivial at any
$\varepsilon$ — any two models with identical $F_L$-restricted observables are
indistinguishable by definition. What is hard, and what makes this a certificate rather
than an observation, is that both dictionaries are **loss-optimal for their own data**.
That rests on Theorem 1b, which applies at $\varepsilon = 0$. At $\varepsilon > 0$ the
tilt phenomenon returns, neither pure strategy is optimal, and the optimality half
would have to be redone against the global boundary. Claiming the certificate extends
to $\varepsilon > 0$ would assert exactly the thing the optimality gate was built to
avoid assuming. §6 keeps the narrower scope.

**The review says the repair is "empirically proven to survive finite sampling."**
Overstated, not adopted. Round 14's carrier statistic separated at $m = 16384$
(14.1% against a 34.0% null), but at $m = 2048$ the same contrast was **not**
significant (+0.072, CI $[-0.064, +0.212]$), and that arm was underpowered — 7 of 192
TopK cells cleared the $|A| \ge 20$ floor, median $|A| = 2$. So the statistic has
demonstrated signal at one width, not proven robustness. The note says "carriage is
real but non-recurring" at $m = 16384$ and should not say more.

## Net

No changes to the theorem, the construction, or the verifiers. One claim independently
confirmed and promoted into the record (strict inactivity), two proposed strengthenings
declined. 24 exact checks across the two verifiers, all passing.
