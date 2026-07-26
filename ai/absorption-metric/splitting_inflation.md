# Spurious absorption from feature splitting: an exact certificate

**Claim.** The first-letter absorption metric used by SAEBench-style evaluations
reports a strictly positive absorption rate on dictionaries in which **no absorption
occurs at all** — where the dictionary is the loss-optimal, faithful representation of
the generative features. The spurious rate is exactly $1 - N_1/N$; its maximum over
all zero-absorption configurations is exactly $1 - \tau$ and is *attained*; and the
family-corrected endpoint repairs it precisely when every split group clears $\tau$.

At the registered $\tau = 0.30$ this means: **the single-latent metric can report a
70% absorption rate on a dictionary with zero absorption.** Stated carefully, since
the generative model is load-bearing (§6): *for a letter whose tokens are produced by
$k$ distinct features, the metric scores the loss-optimal faithful dictionary as up to
$1-\tau$ absorbed.* It is a non-identification result — the metric does not determine
absorption without an assumption it never checks — not a claim that any particular
published number is spurious.

Verifier: `verify_splitting_inflation.py` (python3 + stdlib `fractions`; sympy only
for the one irrational strictness check). Exact throughout — no floating point in any
load-bearing step.

---

## 1. The metric, as actually implemented

Taken verbatim from the reference implementation
(`sae-identifiability/analysis/round13a_family_endpoint.py`), which is the code that
produced the empirical rounds this certificate explains. For a letter $L$ with firing
matrix $\mathrm{fires}$ and token label $y_L$:

$$\mathrm{sel}_i \;=\; \Pr[\text{latent } i \text{ fires} \mid L] \;-\; \Pr[\text{latent } i \text{ fires} \mid \neg L]$$

$$j = \arg\max_i \mathrm{sel}_i, \qquad \text{letter scored only if } \mathrm{sel}_j \ge \tau$$

$$F_L = \{\, i : \mathrm{sel}_i \ge \tau \,\} \quad (\text{capped at } 32 \text{ by } \mathrm{sel})$$

$$\mathrm{rate\_single} = \frac{\#\{t : \text{present} \wedge \text{retained} \wedge \neg \mathrm{fires}_{t,j}\}}{\#\{t : \text{present}\}}, \qquad
\mathrm{rate\_family} = \frac{\#\{t : \text{present} \wedge \text{retained} \wedge \neg\!\!\bigvee_{i \in F_L}\!\! \mathrm{fires}_{t,i}\}}{\#\{t : \text{present}\}}$$

"Absorbed" is thus **defined as an absence**: the letter is present in the input, still
recoverable from the reconstruction, and the selected latent(s) did not fire. Nothing
in the definition inspects where the letter's mass went.

## 2. The construction

Fix $\tau \in (0,1)$ and an integer $k \ge 2$.

**Generative model.** A letter $L$ occurs on $N$ tokens, partitioned into $k$ disjoint
groups $G_1, \dots, G_k$ with $|G_t| = N_t$, $N_1 \ge N_2 \ge \dots \ge N_k$,
$\sum_t N_t = N$. There are $k$ distinct features $u_1, \dots, u_k$, orthonormal, with
$u_t$ active (coefficient 1) exactly on the tokens of $G_t$. Non-$L$ tokens activate
background features orthonormal to all $u_t$.

**There is no "starts with $L$" feature in the data.** Membership in $L$ is the
*disjunction* $\bigvee_t [u_t \text{ active}]$ — an emergent property of $k$ distinct
features, not a feature itself. This is the situation the metric's one-feature
ontology cannot express, and it is not exotic: "words starting with S that are nouns"
and "words starting with S that are verbs" are different features that happen to share
a letter.

**Dictionary.** $D^\star = \{u_1, \dots, u_k\} \cup \{\text{background atoms}\}$ — one
atom per generative feature. No atom is a merge of two features, so **true absorption
is zero by construction.**

## 3. The faithful dictionary is optimal (not a hand-picked bad dictionary)

This is what makes the result a statement about the metric rather than about a
strawman dictionary.

**Lemma 1 (per-event lower bound).** For unit-norm dictionary columns and any
$f \ge 0$, $\lVert Df \rVert \le \lVert f \rVert_1$, so for a sample of norm $r$ and
$0 < \lambda < 2$,
$$\lVert x - Df\rVert^2 + \lambda \lVert f \rVert_1 \;\ge\; \min_{t \ge 0} (r-t)^2 + \lambda t \;=\; \lambda r - \tfrac{\lambda^2}{4},$$
with equality iff every atom active in $f$ points along $x/r$.

*(This is Theorem 1b of the sibling `sae-identifiability` paper, restated; the bound
and its equality condition are what the argument needs.)*

**Lemma 2 (attainment).** Every token here is $1$-sparse in $D^\star$: a token of
$G_t$ has $x = u_t$, $r = 1$. Taking $f = (1 - \lambda/2)_+$ on atom $t$ and zero
elsewhere gives loss exactly
$$\left(\tfrac{\lambda}{2}\right)^2 + \lambda\left(1 - \tfrac{\lambda}{2}\right) = \lambda - \tfrac{\lambda^2}{4},$$
which meets the bound. Hence $D^\star$ attains the global optimum, and by the equality
condition any optimal dictionary must use exactly the directions $\{u_t\}$ on these
events.

**Corollary.** A merged atom $(u_a + u_b)/\sqrt2$ does *not* point along $x$ for
tokens of $G_a$, so any dictionary absorbing two of these features is **strictly
worse**. Splitting is not a training pathology here — it is the unique correct answer,
and absorption is the suboptimal alternative.

The gap is strictly positive across the *whole* admissible range $0 < \lambda < 2$,
piecewise: the code on the merged atom is $t^\star = \max(0,\; 1/\sqrt2 - \lambda/2)$,
so for $\lambda < \sqrt2$ the gap is $\tfrac12 - \lambda(1 - 1/\sqrt2)$, minimised at
the branch end at $\tfrac32 - \sqrt2 \approx 0.0858$; for $\lambda \ge \sqrt2$ the code
clamps to zero and the gap is exactly $(\lambda-2)^2/4$. It tends to $0$ only as
$\lambda \to 2$, where every code vanishes and the comparison degenerates.

*(An earlier draft reported a "break-even $\lambda \approx 1.707$". That was an
artifact of extrapolating the unclamped branch past $\sqrt2$; caught in review. The
corrected statement is stronger — merging is worse everywhere, not just below 1.707.)*

## 4. What the metric reports

**Theorem.** For the configuration above with an exact-recovery probe (§5), provided
$N_1/N \ge \tau$ so the letter is scored at all, and provided $\tau > 1/33$ so the
family cap cannot bind (see below):

$$\boxed{\;\mathrm{rate\_single} \;=\; 1 - \frac{N_1}{N}, \qquad \mathrm{rate\_family} \;=\; 1 - \frac{1}{N}\sum_{t \,:\, N_t/N \,\ge\, \tau} N_t \;}$$

while the true absorption rate is $0$.

*Proof.* Latent $t$ fires exactly on $G_t$ and never on $\neg L$, so
$\mathrm{sel}_t = N_t/N - 0 = N_t/N$. Hence $j = 1$ (the largest group) and
$F_L = \{t : N_t/N \ge \tau\}$. Every $L$ token is present and retained (§5). Latent
$j$ fails to fire exactly on $\bigcup_{t \ne 1} G_t$, giving $N - N_1$ spurious
"absorbed" tokens; the family fails to fire exactly on the union of the groups below
threshold. Dividing by $N$ gives the two rates. $\square$

**Corollary A (sharp maximum, attained).** Over all zero-absorption configurations,
$$\max \;\mathrm{rate\_single} \;=\; 1 - \tau .$$
This is a maximum and not merely a supremum, because the scoring guard
$\mathrm{sel}_j \ge \tau$ is **non-strict**: any configuration with $N_1/N = \tau$
exactly is scored, and reports $1 - \tau$. Whenever $\tau$ is rational such a
configuration exists — at $\tau = 3/10$ the sizes $(3,3,3,1)$ with $N = 10$ attain it,
and the verifier exhibits that instance. The guard is the *only* thing bounding the
metric's spurious output; without it the rate would reach $1$. At $\tau = 0.30$ the
attained bound is $\mathbf{0.70}$.

**The $\tau > 1/33$ hypothesis is real, not decoration.** The reference code caps
$F_L$ at 32 latents by descending $\mathrm{sel}$. At most $\lfloor 1/\tau \rfloor$
groups can clear threshold, so the cap binds only when $\tau \le 1/33$ — and there the
closed form above is **false**. The verifier exhibits the failure: at $\tau = 1/40$
with 40 equal groups the true $\mathrm{rate\_family}$ is $1/5$ (32 groups kept, 8
dropped) while the uncapped formula says $0$. At the registered $\tau = 0.30$ at most
3 groups can clear threshold, so the cap can never bind and the hypothesis is
vacuous — but the theorem has to say so rather than get lucky.

**Corollary B (when the family correction works).** $\mathrm{rate\_family} = 0$ iff
every group clears threshold, $N_t/N \ge \tau$ for all $t$; for equal groups this is
$k \le \lfloor 1/\tau \rfloor$. With $\tau = 0.30$ that permits $k \le 3$, so the
largest fully-repaired case is three equal groups with
$\mathrm{rate\_single} = 2/3$ and $\mathrm{rate\_family} = 0$.
Conversely if no split clears $\tau$ then $F_L = \{j\}$ and
$\mathrm{rate\_family} = \mathrm{rate\_single}$: **the family correction repairs
nothing.** It is a fix for coarse splitting only.

## 5. Presence and retention

Both are properties of probes, so they must be pinned down or the theorem is vacuous.

*Presence.* The linear probe $w = \sum_t u_t$ separates $L$ from $\neg L$ with margin
1 versus 0, since backgrounds are orthogonal to every $u_t$. So every $L$ token is
present.

*Retention.* The optimal code shrinks: $\hat{x} = (1-\lambda/2)\,x$ for every $L$
token, a single positive scalar identical across all groups (all have $r=1$). A
sign-thresholded probe is invariant under positive scaling, so retained $=$ present.
Shrinkage therefore cannot rescue the metric here.

## 6. Scope, and what is and is not new

**What is new.** That a single-latent metric confounds splitting with absorption is
folklore — it is precisely why a family-corrected endpoint exists, and the source
paper's own title pairs "feature splitting *and* absorption". This note does not claim
that observation. What it adds is exact:

1. the **attained** maximum $1-\tau$, so the metric's spurious output is bounded by its
   own scoring guard and by nothing else;
2. the **iff** for the family correction — it repairs exactly when every split clears
   $\tau$, and repairs *nothing* when no split does, which is not folklore and is the
   part that matters for practice;
3. the **optimality lemma**: in this model splitting is not a pathology to be corrected
   but the loss-optimal answer, with merging strictly worse for every admissible
   $\lambda$. The metric penalises the correct dictionary.

**The generative model is a modelling choice, and it is load-bearing.** Here the letter
is the disjunction of $k$ distinct features and there is no monolithic "starts with $L$"
feature. A referee will object that real language models do carry shared orthographic
geometry, so this is an adversarial input rather than a fair test. That objection is
partly right and fixes the strength of the claim: this is an **existence and
non-identification** result, not evidence that any published absorption number is
spurious.

But one common form of the objection does not survive. "Linear probes recover the first
letter easily, therefore there is a monolithic first-letter feature" is invalid, and
this construction is the counterexample: the probe $w = \sum_t u_t$ separates $L$ from
$\neg L$ with margin 1 — perfect linear recovery — while no single feature or latent
carries the letter. Linear decodability of a concept does not imply the concept is one
feature, so it cannot be used to argue the metric's ontology is safe. Indeed the
metric's own presence/retention probes are exactly such linear probes, and they succeed
here while the absorption verdict is wrong.

**Two further scope conditions.** The optimality lemma assumes the dictionary is not
capacity-constrained: it needs room for $k$ atoms plus backgrounds. Under real
scarcity $D^\star$ may be infeasible and merging genuinely optimal — which is a
different regime, and the one absorption is actually about. And the theorem assumes
disjoint groups; overlapping features would change the selectivity arithmetic.

**What the certificate removes** is the inference from "the metric reported $R$" to
"absorption of magnitude $R$ occurred", for any $R \le 1-\tau$, *unless* one separately
establishes that the letter is carried by a single feature — which the metric does not
check and which the empirical family sizes below suggest is often false.

**Contact with measurement.** The empirical rounds this was built to explain found
23–33% single-latent inflation at every width, with L1 mean family size 2.61 against
TopK's 1.25 — real SAEs split letters into two to three groups rather than one. Under
the theorem those family sizes put $N_1/N \approx 0.67$–$0.77$ and predict inflation of
exactly that order. So the observed inflation is the generic consequence of splitting,
and the family correction helped there for the reason Corollary B gives: those splits
were coarse enough to clear $\tau$.
