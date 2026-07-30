# Max-settings referee review — GPT-5.6 (codex exec, reasoning effort xhigh), 2026-07-30

*Static audit; materials supplied inline after the sandbox exec helper crashed. Verdict: BLOCKING — adjudication in RESPONSE_c66_maxreview.md.*

## P1 — blocking

1. **Convex combinations can secretly use the point itself.**  
   Reference: `verify_c66_new_cases.py`, the `for i, parts in com.items()` loop.

   The verifier checks:

   ```python
   if any(j == i for j, _ in parts):
   ```

   but never checks `0 <= j < len(pts)`. Python accepts negative indices. If `N = len(pts)`, candidate `i` can use:

   ```text
   [[i - N, 1]]
   ```

   because `pts[i-N] is pts[i]`, while `i-N != i`. Nonnegativity, sum-to-one, and coordinate equality all pass. Thus every claimed non-vertex can self-certify.

   Consequence: a certificate with `f0` genuine witnesses can pass while the polytope actually has more than `f0` vertices. The partition and distinctness checks do not repair this, because the alias is an index-level failure.

   Required fix:

   ```python
   if any(j < 0 or j >= len(pts) for j, _ in parts):
       fail(f"{fname}: combo {i} has out-of-range index")
   if any(j == i for j, _ in parts):
       ...
   ```

   Then rerun all five certificates.

   `build_cert_extremal.py::combo_cert` appears to emit ordinary nonnegative hull-vertex indices, which is reassuring, but the actual certificate JSON contents were not appended—only their sizes. Therefore the supplied `PASS` result does not establish that the checked-in files avoid this exploit.

   What survives even before repair:

   - `(4,6)` is still exact: its 104 strict witnesses prove at least 104 vertices, and the independent cap is 104.
   - `(3,8)` still proves the lower/achievability statement `max ≥ 110`.
   - `(3,5)/(4,5)/(3,7)` still prove lower bounds 42/58/84.
   - What is blocked is the claimed exact pinning of the latter four instances, especially “the other candidates are non-vertices” and the possibility that the `(3,8)` instance itself exceeds 110.

## P2 — important

1. **M1 does not perform “exact hull counting” or exact deduplication.**  
   References: `attack_c66_deficit.md`, M1; `search_maxout67.py::nverts`.

   The code computes:

   ```python
   P = np.unique(np.round(P, 9), axis=0)
   ConvexHull(P)
   ```

   This replaces every coordinate by a 9-decimal approximation and then uses floating-point Qhull. It can merge distinct points, alter coplanarity, turn an interior point into a hull point, or remove a small-normal-cone vertex. Avoiding Qhull’s `QJ` option does not make this exact; rounding is itself a perturbation.

   The final rational certificates can be exact after the verifier is repaired, but the sampling assertions—especially failure to reproduce Proposition 6.5—must be described as floating numerical evidence, not “exact-deduplicated hull counting.”

2. **`facet_lp.py` is not complete for “fixed U” as presently stated.**  
   References: `facet_lp.py::try_U`, module header; `attack_c66_deficit.md`, M3.

   It is complete only for all of the following fixed restrictions:

   - A fixed ordered partition: the first `k` generators are in A and the rest in B. Other subsets and residual zero weights are not enumerated.
   - Weight bounds `0.02 <= α_i,β_i <= 10`, hence a maximum weight ratio of 500.
   - Every normalized side inequality having margin at least `delta`.
   - The floating LP solver’s feasibility tolerances.
   - Completion before the global time deadline.

   Row normalization preserves signs, but it only makes the margin invariant under rescaling a constraint row. It does not make the search scale-free in the parameter vector. A strictly feasible sign pattern can require weight ratios outside the box or have no representative meeting the requested absolute margin inside that box.

   The honest claim is therefore: “complete for this `(U,k,partition)` inside the stated weight box and δ-robust floating feasibility model, provided enumeration completes.”

3. **The code cannot substantiate the reported count of complete-per-U runs.**  
   References: `facet_lp.py::build`, `try_U`, `main`; note’s “~250” and README’s “~300.”

   `try_U` returns `None` for several different outcomes:

   - sampled chambers were incomplete;
   - U failed a numerical genericity threshold;
   - branch-and-bound exhausted all assignments;
   - the global deadline interrupted enumeration.

   `main` counts every such call as a tried—and in progress messages, “exhausted”—U. No completion flag distinguishes a genuine exhaustive negative run. The claimed number of complete runs therefore needs separate logs or instrumentation not supplied here.

4. **The chamber sampler is conditionally safe, but rejected U’s are being overinterpreted.**  
   Reference: `facet_lp.py::build`.

   For a simple central arrangement in \(\mathbb R^3\), the expected chamber count is

   \[
   2\left(1+(n-1)+\binom{n-1}{2}\right)=n^2-n+2.
   \]

   Every sampled sign vector is an actual chamber, so if the dictionary reaches this cardinality, all chambers have indeed been found. A missed chamber therefore cannot silently produce a false cap result: `try_U` rejects that U.

   The problem is reporting: rejection due to unlucky sampling is not an exhaustive negative result for U, yet it is counted with them.

5. **Side globality and the NAE encoding are otherwise correct under the stated genericity/margin assumptions.**  
   At \(r=u_i\times u_j\), the \(i,j\) terms vanish. For the positive side,

   \[
   \langle s_\varepsilon,r\rangle
   =\langle T,r\rangle+
     \sum_{t\in A}\alpha_t|\langle u_t,r\rangle|
     -\sum_{t\in B}\beta_t|\langle u_t,r\rangle|,
   \]

   independent of the four chambers incident to that ray. On the negative side the \(T\)-term changes sign while the absolute-value sum does not. Thus antipodal sides need not have opposite colors; the LP correctly couples their otherwise separately enumerated signs.

   With all side values nonzero, a linear functional changes sign on a chamber cone exactly when its extreme rays contain both signs. The NAE constraint is therefore correct.

6. **The supplied search tools do not support the prose’s broad d=4 search provenance.**  
   `facet_lp.py`, `tsearch.py`, and `search_maxout67.py` are hard-coded to dimension three. `build_cert_extremal.py` is dimension-generic, but it is a certificate builder, not the claimed search battery. The statement that `(4,5)` received an “analogous battery” needs either narrower wording or the missing d=4 search code/logs.

7. **The Proposition 6.5 tension is overstated by calling the implementation exact and paper-faithful.**  
   The current code fixes a particular residual split, coefficient distribution, 2:1/1:2 construction, rounding threshold, and floating hull implementation. The appended material does not include enough of Proposition 6.5 to demonstrate that every one of those choices matches the authors’ experiment. The negative result is interesting, but not yet a controlled replication.

## P3 — minor

- `verify_c66_new_cases.py` says “four ... certificates” while processing five.
- The note reports approximately 250 complete M3 searches; the README says approximately 300. This may be rounding or later runs, but should be reconciled.
- “Several orders of magnitude beyond” is unsupported: 15,000 versus 1,000 samples is 15×, about 1.18 orders, while LP runs are not directly comparable to samples.
- The README title “two new cases confirmed” is stronger than the body: only `(4,6)` is a fully resolved conjecture case; `(3,8)` confirms its lower/achievability half.
- “The centered family is exactly \(T=0\)” should mean “the centered family maps to the \(T=0\) slice.” Many noncentered midpoint choices also have \(T=0\).
- The earlier note’s phrase that “translated segments are explicitly excluded” conflicts terminologically with the current use of \(I_i=m_i+[-u_i,u_i]\). Under equation (24) as specified in the prompt, arbitrary midpoints are legitimate; what may be excluded is an additional independent translation of the two completed zonotopes.
- The `(3,8)` refutation target 112 needs an explicit parity argument once \(T\ne0\), since central symmetry no longer supplies it. A generic parity proof can be given via the equality-set cycles in the bipartite chamber adjacency graph; without stating that, “no 112 means no refutation” looks unjustified because 111 already exceeds 110.

## Soundness chain after repairing the index check

The underlying finite-set argument is correct.

For each coefficient vector \(c=a\) or \(b\),

\[
Z^c=\sum_i c_i(m_i+[-u_i,u_i])
=\operatorname{conv}\left\{
\sum_i c_i m_i+\sum_i \varepsilon_i c_i u_i:
\varepsilon_i\in\{\pm1\}\right\}.
\]

Therefore the hull of the verifier’s candidate list is exactly

\[
Q=\operatorname{conv}(Z^a\cup Z^b).
\]

A strict witness makes its candidate the unique maximizer of a linear functional and hence an exposed vertex. A candidate expressed as a convex combination of physically different candidates is non-extreme. If witnesses and valid combinations partition the distinct candidates, they pin the count exactly. The standard zonotope bound then supplies the matching upper bound at `(4,6)`.

Under equation (24), the verifier’s computed object is a legitimate zonoboxtope: it uses the same \(m_i,u_i\) on both sides and nonnegative scalars \(a_i,b_i\). Extra rows, coordinates, or coefficients are silently ignored rather than rejected, so schema validation should require exact dimensions, but the effective first-\(n\), first-\(d\) object is still legitimate.

Degeneracies do not create an acceptance loophole:

- If any \(a_i=0\), the two sign choices for \(i\) duplicate a candidate in \(Z^a\).
- If any \(b_i=0\), the same happens in \(Z^b\).
- If \(u_i=0\), both blocks have duplicates.

Thus the global distinctness check indirectly forces every used coefficient and generator to be nonzero. It rejects some legitimate degenerate zonoboxtopes, but does not accept an illegitimate one.

## T-reduction re-derived

Let \(\delta_i=a_i-b_i\). In chamber \(\varepsilon\), the support vertices of the two normally equivalent zonotopes differ by

\[
s_\varepsilon
=\sum_i\delta_i m_i+\sum_i\delta_i\varepsilon_i u_i.
\]

Split the nonzero differences into

\[
A=\{i:\delta_i>0\},\qquad
B=\{i:\delta_i<0\},
\]

with \(\alpha_i=\delta_i\) on A and \(\beta_i=-\delta_i\) on B. Then

\[
s_\varepsilon
=T+\sum_{i\in A}\alpha_i\varepsilon_i u_i
-\sum_{j\in B}\beta_j\varepsilon_j u_j,
\qquad
T=\sum_{i\in A}\alpha_i m_i-\sum_{j\in B}\beta_j m_j.
\]

The chamber cone is \(C_\varepsilon=K_\varepsilon^\ast\), where

\[
K_\varepsilon=\operatorname{cone}\{\varepsilon_i u_i\}.
\]

One zonotope dominates throughout the chamber exactly when
\(s_\varepsilon\in K_\varepsilon\) or
\(-s_\varepsilon\in K_\varepsilon\). Hence the chamber is bicolored precisely when

\[
s_\varepsilon\notin K_\varepsilon\cup(-K_\varepsilon).
\]

For generic U, positive full support, and no cross-candidate coincidences, each chamber contributes one baseline vertex and a bicolored chamber contributes the second, yielding

\[
f_0(Q)=\#\text{chambers}+\#\text{bicolored chambers}.
\]

Thus the T-reduction itself is sound. Common coefficients \(\min(a_i,b_i)\) cancel from the support-vertex difference, while common midpoint effects amount only to translation; all midpoint influence on the coloring is indeed through \(T\).

## Numerical audit

| Case | Candidates | Cap | Claimed \(f_0\) | Required non-vertices |
|---|---:|---:|---:|---:|
| `(4,6)` | \(2^7=128\) | \(4(1+5+10+10)=104\) | 104 | 24 |
| `(3,8)` | \(2^9=512\) | \(4(1+7+21)=116\) | 110 | 402 |
| `(3,5)` | \(2^6=64\) | \(4(1+4+6)=44\) | 42 | 22 |
| `(4,5)` | \(2^6=64\) | \(4(1+4+6+4)=60\) | 58 | 6 |
| `(3,7)` | \(2^8=256\) | \(4(1+6+15)=88\) | 84 | 172 |

The even formula at `(3,8)` subtracts \(n-2=6\), giving 110. The reported odd-case gaps 2, 2, and 4 equal \(2\lceil(n-d)/2\rceil\). The prior `(4,4)` cap is \(4(1+3+3+1)=32\). These arithmetic claims are correct.

The sample totals, run counts, drop outcomes, timings, ancillary-file search, and “minutes/orders of magnitude” claims are not independently auditable from the appended unseeded programs and absence of logs.

## Strongest author-side explanations for Proposition 6.5

Beyond the three possibilities already listed in the note:

- Their sampling distribution or coefficient parameterization may differ from `rand_instance`, despite both being informally described as the same recipe.
- “1000 samples” may count outer samples, each followed by optimization, enumeration of several partitions, or multiple coefficient draws.
- Their random seed may have hit a very low-probability but open extremal region; one historical success does not estimate its probability reliably.
- The current nine-decimal rounding may undercount their valid 44 configuration, especially if extremality has narrow normal cones.
- Their implementation may use higher precision or combinatorial/oriented-matroid hull tests rather than Qhull.
- Success may require coefficients near zero, very unequal weights, or a U/partition correlation excluded by the current uniform ranges and LP weight box.
- The published 44 may come from a structured or post-optimized sample rather than an untouched IID sample.
- There may be a manuscript-version, indexing, or wording discrepancy in what “this method succeeds” refers to.
- A 44-vertex instance cannot be genuinely measure-zero in the full finite-candidate parameter space: strict vertex witnesses persist under small perturbations. It can, however, have extremely small measure under the particular sampling distribution or lie outside the restricted sampled subfamily.
- The authors may simply possess an unpublished valid instance. That remains fully compatible with all three certified lower bounds and all per-U negative searches.

BLOCKING
