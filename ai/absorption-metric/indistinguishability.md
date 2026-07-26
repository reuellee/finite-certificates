# The absorption metric cannot tell single-parent from distributed absorption

**Claim.** There are two generative models — one where a child concept is absorbed
into a *single* parent composite, one where $k$ distinct children are absorbed into
$k$ *different* composites — such that each model's dictionary is the **loss-optimal**
one for its own data, and the absorption metric assigns them **identical values**. The
agreement is not a coincidence of two rates: the entire per-token observable the
metric consumes is identical, so *every* statistic measurable from it agrees,
including ones nobody has written yet.

The indistinguishability holds exactly on $k/N_L < \tau$ and is **sharp** — at the
boundary the family endpoint regains power, while the single-latent endpoint stays
blind. And a statistic reading *outside* $F_L$ separates the models cleanly. That
statistic is round 14's carrier-consistency test, which on real Pythia-1.4B SAEs
answers **distributed**.

Verifiers: `verify_m1_optimality.py` (10 checks, sympy — the optimality gate) and
`verify_indistinguishability.py` (14 checks, stdlib only). Exact throughout.

---

## 1. The two models

Let the letter $L$ occur on $N_L$ tokens: $N_L - k$ where the parent fires alone, and
$k$ where a child co-occurs. Set $\varepsilon = 0$ — children never fire without the
parent. (This is not a convenience; see §2.)

**M1 — single-parent absorption.** One child concept $a_c$, co-occurring with $a_L$ on
all $k$ tokens, absorbed into one composite $a_m = (a_L + a_c)/\sqrt2$.
Dictionary $D_1 = \{a_L,\; a_m\}$.

**M2 — distributed absorption.** $k$ distinct child concepts $a_{c_1},\dots,a_{c_k}$,
one per token, each absorbed into its own composite
$a_{m_i} = (a_L + a_{c_i})/\sqrt2$. Dictionary $D_2 = \{a_L,\; a_{m_1},\dots,a_{m_k}\}$.

These are genuinely different ontologies. In M1 there is one hidden concept spanning
$k$ contexts — the thing absorption is *supposed* to warn about, because a feature you
might want to monitor is buried inside one identifiable latent. In M2 there are $k$
context-specific concepts and no single hidden feature at all.

## 2. Both dictionaries are optimal — why $\varepsilon = 0$ is load-bearing

The sibling paper's $\varepsilon^*$ is a **pure-strategy** crossover: it ranks
faithful against absorbed and is explicitly *not* the global boundary. A continuously
optimised dictionary tilts through intermediate angles and beats both pure strategies
(functional midpoint near $0.88\,\varepsilon^*$). If that happened here, "M1's
dictionary is optimal" would be false and this certificate would collapse.

At $\varepsilon = 0$ it cannot happen. Theorem 1b gives, per event of norm $r$,
$$\lVert x - Df\rVert^2 + \lambda\lVert f\rVert_1 \;\ge\; \lambda r - \tfrac{\lambda^2}{4},$$
with equality **iff every active atom points along $x/r$** — which pins the optimal
direction set uniquely. A tilted atom cannot be parallel to both the parent-solo event
$a_L$ and a joint event $(a_L + a_{c_i})/\sqrt2$, so it must lose the bound on one of
them.

Verified exactly (`verify_m1_optimality.py`), with the nonnegative lasso solved by KKT
active-set enumeration rather than an iterative solver:

- $D_1$ attains the bound on parent-solo and joint events;
- $D_2$ attains it on all $k+1$ of its event types;
- the **faithful** dictionary $\{a_L, a_c\}$ is strictly worse on joint events by
  $39/100 - \sqrt2/5 \approx 0.107$ at $\lambda = 1/5$ — so absorption is the optimum
  here, not merely a competitor;
- all 16 tilted alternatives built from Pythagorean triples (exact rational unit
  vectors — no trigonometry, no floating point) are strictly worse.

## 3. Impossibility

The metric's entire input, per token, is: which $F_L$ latents fire, whether the letter
is *present* in the input, and whether it is *retained* in the reconstruction.

**Theorem.** For $k/N_L < \tau$, M1 and M2 induce the **same** value of that triple on
every token. Consequently any statistic measurable with respect to it — `rate_single`,
`rate_family`, or any other function of the same data — is identical on M1 and M2.

*Proof.* Selectivity: $a_L$ fires on the $N_L-k$ parent-solo tokens in both models, so
$\mathrm{sel}(a_L) = (N_L-k)/N_L \ge \tau$. M1's composite fires on all $k$ joint
tokens, giving $\mathrm{sel}(a_m) = k/N_L < \tau$; each of M2's composites fires on one
token, giving $1/N_L < \tau$. Hence $F_L = \{a_L\}$ in **both** models. On the joint
tokens $a_L$ is silent in both, and on the parent-solo tokens it fires in both. Both
reconstruct the letter (the code is a positive multiple of $x$), so *retained* agrees;
the probe $w = a_L + \sum_i a_{c_i}$ gives *present* on every $L$ token in both. The
triple therefore matches token by token. $\square$

The silence of $a_L$ on joint tokens is **strict**, not a tie: its dual gradient there
is $2a_L^{\!\top}(Df - x) + \lambda = \lambda(1 - 1/\sqrt2) = 1/5 - \sqrt2/10 \approx
0.0586 > 0$ at $\lambda = 1/5$. So "no $F_L$ latent fires" is robust to perturbation of
$\lambda$ rather than a KKT boundary case decided by convention.

Worked instance ($N_L = 10$, $k = 2$, $\tau = 3/10$): both models report
$\mathrm{rate\_single} = \mathrm{rate\_family} = 1/5$, with $F_L = \{a_L\}$ in each,
while their absorbed-token supports differ — $\{a_m\}$ twice in M1 against
$\{a_{m_1}\}, \{a_{m_2}\}$ in M2. The difference is real; it is simply invisible.

**The bound is sharp.** M1's composite fires on all $k$ tokens, so once
$k/N_L \ge \tau$ it is swept *into* $F_L$, M1's joint tokens stop counting as absorbed,
and `rate_family` diverges — $0$ for M1 against $3/10$ for M2 at $k/N_L = \tau$
exactly. So the metric is not globally blind: it regains discriminating power above
the threshold. But `rate_single` stays equal ($3/10$ both) even there, because it reads
only the single argmax latent. The family correction buys real power; the single-latent
version buys none.

## 4. Repair

A statistic reading *outside* $F_L$ separates the models. On absorbed tokens take the
modal non-family carrier's share:

| | M1 (single parent) | M2 (distributed) |
|---|---|---|
| distinct carriers | $1$ | $k$ |
| modal-carrier share | $1$ | $1/k$ |

Verified for $k = 2,\dots,6$ with $N_L = 10k$: the rates stay identical at $1/10$ while
the carrier statistic reads $1$ against $1/k$ throughout.

This is not a new instrument. It is exactly round 14's P2 — modal-carrier top-1 share
on absorbed trials, against a random-direction null. So the theory says a carrier check
is *necessary* to identify absorption at all, and that check has already been run on
real models.

## 5. What the measurement then says

Round 14 scored 16 Pythia-1.4B SAEs at $m = 16384$: modal carrier top-1 on **14.1%** of
absorbed trials against a **34.0%** random-direction null, with per-trial concentration
0.5935 against 0.6322 on control trials — carriage is real but non-recurring.

In this certificate's terms, real SAEs sit near the **M2** end. What the standard
metric reports as absorption is, at least on that model and endpoint, closer to
distributed carriage by many context-specific composites than to a child hidden inside
one identifiable parent — and the metric cannot report that difference, which is why it
had to be measured separately.

## 6. Scope

- The construction is at $\varepsilon = 0$. That is what makes both dictionaries
  provably optimal; at $\varepsilon > 0$ the tilt phenomenon returns and neither pure
  strategy is optimal, so the certificate would need the global boundary instead of
  Theorem 1b.
- Indistinguishability requires $k/N_L < \tau$, shown sharp in §3.
- Children are orthogonal to each other and to the parent. Correlated children would
  change the selectivity arithmetic.
- This bounds what the metric *can* determine. It does not show any published
  absorption number is wrong — it shows those numbers do not, by themselves,
  distinguish the two ontologies, and identifies the extra statistic that does.
