# Response to `reviews/GEMINI_splitting_inflation_review.md`

Verdict returned: **SOUND**, with one [BLOCKING], two [FIX] and two [MINOR]. Every
item is adjudicated below. Three changed the artifact materially; one is rejected on
the grounds that this note's own construction refutes it.

## Accepted — and it found a real bug

### F1 [FIX] The family cap was missing from the theorem — ACCEPTED

Correct. The reference implementation caps $F_L$ at 32 latents by descending
selectivity, and the closed form for `rate_family` silently assumed no cap. More than
32 groups can clear threshold only when $\tau \le 1/33$, so the theorem needed the
hypothesis $\tau > 1/33$.

Fixed, and rather than just adding the words, the verifier now **exhibits the
failure**: at $\tau = 1/40$ with 40 equal groups the true `rate_family` is $1/5$ (32
kept, 8 dropped) while the uncapped formula gives $0$. At the registered
$\tau = 0.30$ at most 3 groups can clear threshold, so the cap can never bind and the
hypothesis is vacuous there — but the theorem now says so instead of getting lucky.

### F2 [MINOR] The $\lambda$ break-even was wrong — ACCEPTED, and the fix strengthens the result

This is the most valuable item in the review. The note claimed merging is strictly
worse "for $\lambda < 1.707$". That number came from extrapolating the unclamped code
$t^\star = 1/\sqrt2 - \lambda/2$ past the point where it goes negative. With the
nonnegativity clamp restored the analysis is piecewise:

- $\lambda < \sqrt2$: gap $= \tfrac12 - \lambda(1-1/\sqrt2)$, minimised at the branch
  end at $\tfrac32-\sqrt2 \approx 0.0858$;
- $\lambda \ge \sqrt2$: $t^\star = 0$, gap $= (\lambda-2)^2/4$.

So merging is strictly worse across the **entire** admissible range $0<\lambda<2$, not
just below 1.707. The reviewer's diagnosis was right and the corrected claim is
stronger than the one it replaced. Independently re-derived symbolically before
accepting.

### F3 [MINOR] Capacity assumption in the optimality lemma — ACCEPTED

The lemma needs an unconstrained dictionary — room for $k$ atoms plus backgrounds.
Under real capacity scarcity $D^\star$ may be infeasible and merging genuinely
optimal. That is a different regime, and notably it is the regime absorption is
actually about. Added as an explicit scope condition.

### F5 [MINOR] Novelty is narrower than implied — ACCEPTED

Fair. "Single-latent scoring confounds splitting" is folklore; it is why the family
endpoint exists at all, and the source paper's title already pairs splitting with
absorption. §6 now says so plainly and claims only what is actually new: the
**attained** bound $1-\tau$, the **iff** characterising when the family correction
works (and the observation that it repairs *nothing* when no split clears $\tau$), and
the **optimality lemma** showing the metric penalises the correct dictionary rather
than a pathological one.

## Accepted in part

### F4 [FIX] The headline is overstated — ACCEPTED, with a more precise rewording

Agreed that "the metric can report 70% absorption with zero absorption" leans on the
generative model. The abstract now carries the qualified form immediately: *for a
letter whose tokens are produced by $k$ distinct features, the metric scores the
loss-optimal faithful dictionary as up to $1-\tau$ absorbed* — a non-identification
result, not a claim that any published number is spurious.

The reviewer's own proposed wording is not adopted verbatim, because it says the
concept "lacks any shared linear geometry". That is false of this construction — see
below.

## Rejected

### F6 [BLOCKING] "Strawman: the DGP violates the linear representation hypothesis" — REJECTED as stated, accepted as a scope note

The reviewer argues the construction is adversarial because real models carry shared
orthographic geometry, evidenced by linear probes recovering first letters easily, and
that the concept here has "exactly zero shared linear geometry".

The second half is factually wrong about this construction, and the error matters. The
probe $w = \sum_t u_t$ separates $L$ from $\neg L$ with margin 1 versus 0 — **perfect
linear recovery** — while no single feature or latent carries the letter. The concept
has excellent shared linear geometry and still has no monolithic feature. So the
inference "linear probes work $\Rightarrow$ there is a monolithic first-letter feature
$\Rightarrow$ the metric's ontology is safe" is invalid, and this note is a
counterexample to it. That matters practically because the metric's *own*
presence/retention tests are linear probes of exactly this kind: they succeed here
while the absorption verdict is wrong.

What survives is weaker and is adopted: the generative model is a modelling choice, so
the result is existence and non-identification rather than evidence about any measured
number. §6 now states that, along with the disjointness assumption and the capacity
condition. The [BLOCKING] severity is not accepted — the construction is a legitimate
model of a real possibility (sub-concepts sharing a letter), and the empirical family
sizes of 2.61 for L1 indicate real SAEs are not in the monolithic regime the objection
presumes.

## Net

17 exact checks, all passing, up from 13 before review. One real bug fixed, one
hypothesis added with a witness for its necessity, three scope conditions stated, and
the novelty claim narrowed to what is defensible.
