# Independent verification of the (d, d+1)-zonoboxtope maximum

**Claim under test.** `max f₀((d,d+1)-zonoboxtope) = 2^(d+2) − 6` for every
d ≥ 2. Consequences: the (4,5) maximum is **58, not 60**, and Part 2 of
Conjecture 6.6 of Balakin–Cox–Loho–Sturmfels (arXiv:2509.21286) is false for
every d ≥ 4 at n = d+1.

**Provenance.** Draft and `verify_d_dplus1.py` produced 2026-08-02 in a
ChatGPT (GPT-5.6 Sol) session directed by the repository author; retrieved
from that session and verified here. The draft is `zonoboxtope_d_dplus1.pdf`
(4 pp; `proof.txt` is its extracted text). **This directory's verification
was performed independently of the tools that produced the claim.**

## What this repository already held

`ai/maxout/` certified **58** as a *lower* bound at (4,5) and recorded the
maximum as **open** (conjectured 60). A separate $5 AlphaEvolve campaign
(`ai/alphaevolve/`) searched for a (4,5) instance beating 58 and found none —
consistent with, though not evidence for, 58 being optimal. The claim under
test closes that open case in the direction our searches kept suggesting.

## Verification performed

**1. The construction (lower bound) — CONFIRMED independently.**
`xcheck_zbx.py` rebuilds the paper's family from its own equations (11)–(14)
and counts vertices with **this repository's** exact counter
`ai/alphaevolve/zbx.py`, written weeks earlier and sharing no code with the
draft's script:

| d | n | zbx exact f₀ | claim 2^(d+2)−6 | conjecture (2) |
|---|---|---|---|---|
| 2 | 3 | 10 | 10 | 12 |
| 3 | 4 | 26 | 26 | 28 |
| 4 | 5 | **58** | 58 | 60 |
| 5 | 6 | 122 | 122 | 124 |

The d = 2 and d = 3 values (10, 26) are the maxima already published in
BCLS, so the family reproduces known ground truth and then continues.

**2. The counting machinery (eqns 7, 8, 10) — CONFIRMED end to end.**
The upper bound rests on `f₀(Q) = R + #{bicolored chambers}` with ray values
`g(eᵢ−eⱼ) = pᵢ − qⱼ`. `xcheck_formula.py` tests both *without re-deriving
either*: it builds random generic instances, predicts f₀ combinatorially
from p and q, and compares against `zbx.nverts_exact`, which knows nothing
about chambers. **16/16 random instances agree exactly** (d = 2, 3, 4), and
none exceeds 2^(d+2)−6.

*Harness bug found and fixed here, worth recording:* the first run showed
disagreements, which were an artifact of **our** test, not the draft. PDF
text extraction had flattened a fraction, and we read equation (7) as
`pᵢ = tᵢ + δᵢ/cᵢ` instead of `pᵢ = (tᵢ + δᵢ)/cᵢ`. Only the latter is
invariant under `t → t + λc`, the free choice left by `Uᵀt = T`; with the
wrong reading the differences pᵢ − qⱼ are not well defined at all. After
correction, agreement is exact. (The draft's own script is insensitive to
the distinction because its construction has cᵢ = 1 for all i.)

**3. The external dependency — CONFIRMED verbatim.** Equation (10) cites
[BCLS, Prop. 6.3]. From the paper's full text in our corpus:
"*The number of vertices of conv(P₁ ∪ P₂) is equal to the number of vertices
of P plus the number of bicolored facets of G(P\*) under the candidate
bicoloring*", i.e. `f₀(conv(P₁∪P₂)) = f₀(P) + #{F\* facet of P\* : G(F\*)
bicolored}`. For n = d+1 generators in general position the zonotope has
`2(2^d − 1) = 2^(d+1) − 2` vertices, matching the draft's R.

**4. Lemma 2 (the pigeonhole giving the upper bound) — checked by hand,
holds.** Among the 2n distinct values {pᵢ} ∪ {qᵢ}: the global maximum makes
one chamber monocolored (if it is p_r, chamber {r} has all cross-differences
positive; if q_r, chamber [n]\{r} has all negative), the global minimum makes
another by the mirrored argument, and the two are distinct — same-type
extrema differ by distinctness, opposite-type because a singleton cannot
equal the complement of a singleton when n ≥ 3. Hence #bicolored ≤ R − 2 and
f₀ ≤ 2R − 2 = 2^(d+2) − 6.

## Trust boundaries — what is NOT verified here

* **The perturbation/genericity reduction (§2 of the draft)** — that
  restricting to generic position cannot decrease the maximum — is stated
  and plausible (small perturbations preserve exposed vertices) but was not
  independently re-derived. It is the standard subtlety in results of this
  shape and is the first thing a referee should attack.
* **Equation (8) was validated empirically, not symbolically.** 16 random
  instances is strong evidence the substitution is right; it is not a proof.
* **Novelty is unconfirmed.** The draft reports finding no prior statement.
  Our corpus was not searched for a prior (d,d+1) maximum.
* Verification covers d ≤ 5 computationally; the claim for all d rests on
  the symbolic argument.

## Assessment

Both bounds check out under independent computation, the one external
citation is accurate, and the extremal argument is sound as written. The
result appears **correct**, subject to the genericity reduction receiving a
referee's attention. Verified 2026-08-02.
