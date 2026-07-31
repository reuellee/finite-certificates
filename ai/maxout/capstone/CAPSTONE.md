# The maximum vertex number of (3,5)-zonoboxtopes is 42

**Claim.** Over all (3,5)-zonoboxtopes Q = conv(Z^a ∪ Z^b) — five
segments I_i = m_i + w_i·[−u_i, u_i] in R³, arbitrary midpoints m_i,
arbitrary nonnegative coefficient vectors a, b — the maximum number of
vertices is **f₀ = 42**. In particular the value 44 conjectured by the
odd case of Conjecture 6.6.1 of arXiv:2509.21286 is not attained at
n = 5, and the tightness assertion of its Proposition 6.5 fails at n = 5.

Status: **declared**, subject to the verification manifest at the end of
this document reproducing PASS on an independent machine. Every exact
claim below is machine-checkable from the repository; no step depends on
floating-point output (floats appear only inside search heuristics whose
results are re-proven exactly before use).

---

## 1. Setup and notation

Fix five direction vectors U = (u₀,…,u₄), uᵢ ∈ R³, weights wᵢ > 0,
midpoints mᵢ, and a split s ∈ {±1}⁵ assigning each segment to the A-copy
(sₜ = +1) or B-copy (sₜ = −1). (The reduction of the general
two-coefficient-vector zonoboxtope to this weight/split normal form —
sₜ the sign and wₜ the magnitude of the residual δₜ = aₜ − bₜ — and
the removal of all square roots by row scaling, is the "Exact row model"
of `../stage2b_gpt/STAGE2B.md`, validated against hull counts on live
instances. The normal form exists only when every residual is nonzero;
the boundary cases — a copy missing a generator, or aₜ = bₜ > 0 — are
handled in §3.1 without the model.)

For a generic U (all ten 3×3 determinants nonzero) the central
arrangement {u_i^⊥} has exactly 22 chambers, and the chamber model gives
f₀(Q) = #chambers + #bicolored, where a chamber is *bicolored* when its
sign pattern is realized on both copies (master note, method M2; the
paper's Prop 6.3/Thm 5.5 specialized). Hence f₀ ≤ 44, with equality iff
**every** chamber is bicolored ("cap attainment").

The cap-attainment condition is linear in the pair x = (T, w) ∈ R³×R⁵,
where T = Σ_A αᵢmᵢ − Σ_B βⱼmⱼ carries all midpoint freedom: with
C_ij = uᵢ×u_j and D_tij = |det(u_t, uᵢ, u_j)|, cap attainment with side
pattern σ ∈ {±1}²⁰ (one sign per *ray* ±C_ij of each of the ten pair
classes; the two rays are independent because Q need not be centrally
symmetric when T ≠ 0) is the strict feasibility of the 25-row system

    B(σ, s)·x > 0:   σ_{ij,±} · ( ±C_ij | (s_t·D_tij)_{t∉{i,j}} )  (20 side rows)
                     w_t > 0                                        (5 rows)

Not every σ is consistent with all 22 chambers seeing both signs: the
chamber/side incidence of the arrangement — a purely combinatorial
object determined by the chirotope χ(U) — admits exactly **33,140 valid
labeled side patterns** (three independent enumerations agree:
`../stage1_gpt/`, its review, and `../stage2c2_gpt/common.py`'s
VALID_BITS). A strict 44-vertex instance therefore yields a valid σ and
a split s with B(σ, s)·x > 0 strictly feasible.

**The proof kills every such system.** A *Gordan certificate* y ≥ 0,
y ≠ 0, Bᵀy = 0 proves strict infeasibility. A certificate is *cell-wide*
when its 25 multipliers are polynomials in the ten variables D (side
multipliers of degree ≤ 2, weight multipliers of degree ≤ 3, all
coefficients nonnegative, at least one positive) such that Bᵀy = 0 holds
*identically modulo the Grassmann–Plücker ideal* given the chirotope's
signs — hence specializes to an exact Gordan vector at **every**
configuration realizing that chirotope, not just the reference one.
(Specialization preserves both Gordan conditions unconditionally: on a
generic configuration every D_tij > 0 strictly, so nonnegative
coefficients give y ≥ 0 and the positive coefficient's monomial gives a
strictly positive entry, hence y ≠ 0.)

The reference configuration is the integer matrix

    U_ints = [−6 −13 18; −9 −12 8; −13 −4 16; 4 −19 −8; 16 15 −12]

with chirotope χ_ref (all ten determinants nonzero).

## 2. The certificate library at χ_ref

For each split below, every one of the 33,140 valid σ carries an exact
cell-wide certificate, by one of two mechanisms:

- **Single-class family (closed form).** If some class (i,j) has equal
  side signs σ* with σ*·s_t = −1 for every t ∉ {i,j}, then
  y_{ij,+} = y_{ij,−} = 1, y_{w,t} = 2·D_tij (t ∉ {i,j}) is a
  certificate: the T-parts cancel exactly, the weight parts cancel
  against the positivity rows, all coefficients are positive monomials
  in D — valid on the whole cell with no Grassmann–Plücker reduction.
  (Proven in `../stage2c_gemini/`; moreover this family is *exactly* the
  complete coefficientwise-positive mechanism — the boundary theorem of
  `../stage2c2_gpt/STAGE2C2.md`.)
- **Degree-(2,3) quotient-ring certificate.** Otherwise, an explicit
  polynomial certificate solved modulo the GP ideal
  (`../stage2c2_gpt/gp_degree3_search.py` machinery).

The library, by split:

| split A | systems | family | explicit GP | artifacts |
|---|---|---|---|---|
| ∅ (k=0) | 33,140 | 32,570 | 570 | `../stage2c2_gpt/k0_cellwide_shard_00_of_01.json.gz` |
| {0} (k=1) | 33,140 | 24,691 | 8,449* | `../stage2c2_gpt/gp_all_d2_shard_0{0..3}_of_04.json.gz` + family |
| {0,1} (k=2) | 33,140 | 8,746 | 24,394* | same shards |
| {0,2} (k=2) | 33,140 | 8,916 | 24,224 | `split02_cellwide_shard_0{0..3}_of_04.json.gz` |

(*the four prefix-sweep shards hold the 32,843 explicit certificates for
k ∈ {1,2} jointly; the family covers the complementary 33,437.)

Every certificate in every bundle is re-verified by **two auditors**,
each in a single run, both reporting zero failures. Only the first is
independent of the programs that produced the library; the second is
kept as a second opinion and is described honestly below.

- `independent_audit.py` (this directory) is the **primary** check. It
  is written from scratch against the serialized artifacts and imports
  nothing from any generation-side module; it uses the Python standard
  library only. It decides the cell-wide property by a route that
  shares no algebra with the generator: no Gröbner basis, no normal
  forms, no signed-D quotient ring. Its criterion is that each of the
  ten identity polynomials F (the five u_t-dotted T-identities and the
  five weight identities — the five u_t span R³, so their vanishing
  forces the 3-vector T-part to vanish) satisfies Φ(F) ≡ 0, where Φ
  substitutes D_T ↦ χ_T·det_T(x) for a *symbolic* 5×3 configuration x.
  Since the realizations of χ_ref form a nonempty open subset of R¹⁵
  and a real polynomial vanishing on a nonempty open set is zero, this
  is exactly equivalent to cell-wideness (the generator's
  ideal-membership criterion is a priori only sufficient). The test is
  decided by exact integer evaluation against a set of evaluation
  functionals whose sufficiency is *certified in the run itself*: with
  M_e monomials of degree e, E the evaluation matrix and J the span of
  the monomial multiples of the five signed three-term Plücker
  relations, always rank E + rank J ≤ M_e; the run computes both ranks
  (mod a prime, hence lower bounds on the rational ranks) and finds
  rank E + rank J = M_e, which forces ker E = ker Φ exactly. No
  Hilbert-function or standard-monomial input is assumed; the classical
  values 10 / 50 / 175 / 490 for e = 1..4 are recomputed as predictions
  and confirmed. The same run also re-derives χ_ref, the 22 chambers
  (with a completeness proof: each of the 32 candidate sign vectors
  gets either an explicit integer interior point or an explicit Gordan
  vector), and the 33,140 valid σ, all from U_ints alone, and then
  verifies what no earlier checker did — that the library **covers**
  every valid σ at each of the four splits, with zero gaps and zero
  duplicates.

- `../stage2c2_gpt/audit_all_certificates.py` is the **secondary**
  check and is *not* independent of the generator: it imports
  `quotient_matrix` and `normal_forms` from `gp_degree3_search.py`, so
  its quotient-ring half re-uses the construction it is checking. Its
  other half — specialization at U_ints against an independently
  written row builder — is sound but cannot detect a multiplier that is
  a genuine Gordan vector at U_ints yet not cell-wide (this is
  demonstrated, not asserted: canary C8 of the primary auditor is
  exactly such a mutation, and it passes that layer). Both auditors
  agree on every shared count.

Canary discipline (instituted after a caught sign bug — see §6): the
k ∈ {1,2} completion sweep and the {0,2}-split sweep wire in a
provably-uncertifiable negative control and a known positive control,
all passing in every shard. The k = 0 sweep ran without canaries; its
certificates are covered by both audits and were re-verified at fresh
realizations of the chirotope in review.

`independent_audit.py` carries its own canary battery, run every time
and recorded in `independent_audit_report.json` together with *which
layer* caught each mutation: a corrupted coefficient, a dropped term, a
permuted monomial, a negated coefficient, a flipped σ bit on a side the
certificate uses, a flipped split entry on a weight row it uses, a
rotated monomial-decoding order, a certificate transplanted onto the
strictly-feasible (σ = 0, split {0}) system, and — the two decisive
ones — a mutation constructed to be a genuine Gordan vector at U_ints
while not being cell-wide (C8, rejected *only* by the new algebra: it
passes the coefficient and reference-specialization layers, which are
the shipped auditor's entire independent content), and a simulated
systematic error in the *symbolic semantics* itself (C10: the whole
signed-D construction rebuilt with the wrong chirotope, library
untouched — an auditor that imports the generator's construction agrees
with the generator by definition and cannot see this; every sample
whose identities are not chirotope-free ordinary cancellations is
rejected). Three machinery controls per degree check the reduction is
neither vacuous nor over-strict: a known Plücker multiple must be
accepted, a pseudorandom vector must be rejected, and the rank sandwich
must close.

## 3. From the library to the theorem

The library speaks about one chirotope and four split subsets. The
theorem quantifies over all configurations, midpoints, weights, and
splits. The bridge has five steps; each is either a short argument given
here in full or an exact computation named here and performed in this
directory.

### 3.1 Degenerate cases: f₀ ≤ 40 without certificates

Vertices of a hull of a union are vertices of a part, so
f₀(Q) ≤ f₀(Z^a) + f₀(Z^b). A 3-dimensional zonotope's vertex count
equals the chamber count of the central arrangement of its generators'
normal planes; five planes give at most 2(C(4,0)+C(4,1)+C(4,2)) = 22
chambers, attained only when the arrangement is simple. Hence:

- if U is **non-generic** (a vanishing determinant, a repeated or
  antiparallel direction, a zero direction — anything making the
  arrangement non-simple or smaller), each copy has ≤ 20 vertices and
  f₀(Q) ≤ 40;
- if either copy **misses a generator** (a_i = 0 or b_i = 0, the cases
  outside the full-support chamber model), that copy has ≤ 14 vertices
  (four generic planes: 2(1+3+3) = 14) and f₀(Q) ≤ 14 + 22 = 36.

Both are < 42, so from here on U is generic and both copies have full
support. One boundary remains inside the full-support regime: some
**a_i = b_i > 0**, where the residual δ_i = a_i − b_i vanishes and the
(w, s) normal form of §1 does not exist. It is absorbed by the
following lemma, which also supplies the genericity needed in §3.5.

**Lemma (generic-position perturbation).** Let Q, with parameters
(a, b, m) over a generic U, have f₀(Q) = v. Then arbitrarily small
perturbations (a′, b′, m′) exist whose zonoboxtope Q′ has f₀(Q′) ≥ v
and is in *strict generic position*: every residual a′_i − b′_i is
nonzero, every side value on the twenty rays is nonzero, and no two
distinct candidate points coincide.

*Proof.* Every vertex q of Q is strictly exposed: some functional c has
⟨c, q⟩ exceeding ⟨c, p⟩ by a positive margin for every candidate point
p ∉ {q} (candidates = the 2⁶ sign points, finitely many). Candidates
vary continuously (polynomially) in (a, b, m), so after a small enough
perturbation the maximizer of c over the candidates is a candidate near
q, hence a vertex of Q′; distinct vertices of Q stay separated and give
distinct vertices of Q′, so f₀(Q′) ≥ v. The conditions to avoid — a
vanishing residual, a vanishing side value, a coincidence of two
candidates that are not identical as polynomial maps — each cut a
proper algebraic subset of the parameter space (each is a nontrivial
polynomial equation: same-copy candidate differences are nonzero
because some differing sign contributes a nonzero u_i, and cross-copy
differences are nonzero polynomials even for matching sign patterns
because the a, b, m variables are independent). A finite union of
proper algebraic subsets has dense open complement, so the perturbation
can be chosen inside it. ∎

Consequently every instance with f₀ ≥ 43 yields, arbitrarily nearby,
a strict-generic-position instance with f₀ ≥ 43 in the (w, s) normal
form with strict side signs. From here on we work with such instances.

**Remark (candidate scope).** The lemma and the whole chain extend
verbatim to the paper's wider family of *zonoboxtope candidates* (two
zonotopes with correspondingly parallel generators and independent
translations, cf. its Remark 6.7): restate the lemma in candidate
coordinates — translations c_A, c_B ∈ R³ and width vectors
a, b ∈ R⁵₊, which subsume the shared-midpoint parameterization —
with the same proof (candidates vary polynomially; the excluded loci,
including vanishing width differences a_i − b_i, are proper algebraic
subsets). The certificate systems only ever see (T, w) with T free, so
no other step changes; the arXiv note (`../paper/maxout35note.tex`)
states the argument in this generality. Hence max f₀ = 42 for
candidates as well, attained by a genuine zonoboxtope.

### 3.2 Instance normalization: WLOG χ(U) = χ_ref and s ∈ four subsets

The group G = S₅ ⋉ {±1}⁵ acts on configurations by
(π, ε)·U = (ε_i·u_{π⁻¹(i)})ᵢ. This action **preserves the polytope and
f₀ exactly**: reorientation u_i ↦ −u_i fixes each segment
m_i + w_i[−u_i, u_i] as a set, and relabeling permutes the segments
(with midpoints, weights, and split entries carried along, s ↦ π·s). On
chirotopes it acts by χ ↦ (π,ε)·χ as implemented in
`check_split_orbits.py`.

Two exact computations:

- **Single orbit** (`../check_om35_uniqueness.py`, stdlib): the uniform
  rank-3 chirotopes on 5 elements number exactly 384 and form a single
  G-orbit containing χ_ref. So every generic instance can be moved by
  some g ∈ G — without changing its polytope — to an instance whose
  configuration has chirotope exactly χ_ref.
- **Split orbits** (`check_split_orbits.py`, stdlib, exit 0): the
  stabilizer of χ_ref has order 10 with faithful permutation image (the
  pentagon group D₅). Its orbits on split subsets are: {∅}; all five
  1-subsets; two orbits of 2-subsets, represented by {0,1} and {0,2};
  and the complementary structure for k ≥ 3. Having landed at χ_ref, a
  further stabilizer element (which fixes χ_ref, hence keeps the
  configuration realizing χ_ref) normalizes the split subset to one of
  **∅, {0}, {0,1}, {0,2}** or a complement of one of these.

Complements reduce to the four representatives by the **global flip**.
Physically, swapping the roles of the two copies sends
(T, s, σ) ↦ (−T, −s, −σ) with the geometric ray labels fixed; composing
with the antipodal ray relabeling (which restores the T coordinate)
gives the implemented involution (σ, s) ↦ (flip σ, −s), where flip
negates σ *and* swaps the two rays of each class. It satisfies the
exact row identity
Row(flip σ, −s; class, ray) = Row(σ, s; class, −ray), so certificates
transport by the same ray swap; it is an involution and maps the
33,140-pattern valid set onto itself (verified exactly:
`check_transport.py` "FLIP OK", and independently re-checked in the
GPT review).

### 3.3 Certificate transport

Let g = (π, ε) fix χ_ref (a stabilizer element used in §3.2's split
normalization) or, more generally, map the instance's chirotope to
χ_ref. The labeled system transforms covariantly:

- C_{lo,hi}(g·U) = τ·C_{ij}(U) with τ = ±ε_lo·ε_hi (sign − iff π
  reverses the pair's order), so the ray structure of class (i,j) maps
  to the ray structure of class (π(i),π(j)) with a τ-twist; σ's twenty
  bits move accordingly;
- weight rows, split entries, and the D-variables permute by π
  (D is reorientation-invariant: absolute determinants);
- the GP ideal and the coefficient-nonnegativity condition are
  G-invariant, so cell-wide certificates map to cell-wide certificates,
  and the 33,140 valid σ map bijectively onto the valid σ of the image
  chirotope (validity is defined by the chamber/side incidence, which is
  functorial in the chirotope).

These are exactly the claims a subtle error could hide in, so they are
**checked computationally, exactly**, in `check_transport.py`:
transported multipliers of sampled certificates from every bundle
(family, k=0, prefix sweeps, split02 sweep) are re-verified against an
independently built system for the literally-transformed integer
configuration g·U_ints, over the full stabilizer and dozens of random
group elements — together with the bijection of VALID_BITS under all
ten stabilizer elements ("VALIDITY CLOSURE OK").

### 3.4 No strict 44 anywhere generic

Chain: a strict 44-vertex generic instance → (3.2) an equal-f₀ instance
at χ_ref with split in one of the four representatives (or a
complement, reduced by the flip) → its observed side pattern σ is valid
→ (§2) the library kills (σ, s) with an exact cell-wide certificate,
which (3.3) specializes to the instance's actual configuration →
contradiction with Gordan's theorem. So no generic instance attains 44
with strict side signs.

### 3.5 Parity, perturbation, and attainment: max = 42

- **No 43 and no non-strict 44:** suppose any instance (any parameters,
  U generic by §3.1) has f₀ ≥ 43. The Lemma of §3.1 produces a nearby
  instance in strict generic position with f₀ ≥ 43. In strict generic
  position the chamber-model count is literal — no cross-copy candidate
  coincidences can merge vertices — so f₀ = 22 + #bicolored, and the
  bicolored count is even: the zero set of the support-function
  difference traces cycles in the bipartite chamber-adjacency graph
  (adjacency is bipartite because the chamber graph is dual to a
  great-circle arrangement on S², 2-colorable by parity of the sign
  vector), and each bicolored chamber contributes exactly one segment —
  the zero plane meets a strictly convex open cone in a single
  connected sector, so no chamber is re-entered. Hence f₀ is even and
  ≥ 43, i.e. f₀ = 44 with all side signs strict — which §3.4 kills.
  So no instance reaches 43.
  (Parity argument verified: `../stage2b_gpt/REVIEW_stage2b_claude.md`.)
- **42 is attained:** `../cert_35_42.json` — an explicit rational
  42-vertex (3,5)-zonoboxtope, verified exactly by this repo's
  stdlib verifier (`../verify_c66_new_cases.py`) with strict-witness
  vertex confirmation, and independently by Fukuda's cddlib in exact GMP
  arithmetic (`../check_instances_cddlib.py`).

Together: **max f₀(3,5) = 42.**

## 4. Verification manifest

Run everything with CPython ≥ 3.10. Steps 1, 2, 3 and 7's
`verify_c66_new_cases.py` are **stdlib-only**; steps 4–6 require NumPy,
SciPy, and SymPy — the verification arithmetic itself is exact
`Fraction`/integer throughout. From `ai/maxout/`:

1. `python check_om35_uniqueness.py` — 384 chirotopes, single orbit
   (stdlib, seconds).
2. `python capstone/check_split_orbits.py` — stabilizer order 10, D₅
   orbits, "ACCOUNTING CONFIRMED", exit 0 (stdlib, seconds).
3. `python capstone/independent_audit.py` — **the primary upper-bound
   check**: `INDEPENDENT AUDIT PASS: 132869 checks OK, 0 failed`
   (~2 min, stdlib only, exit 0). Re-proves all 132,560 cell-wide
   certificates of the library from the serialized artifacts with no
   import from any generation-side module and no Gröbner/normal-form
   machinery (see §2), proves the library covers every valid σ at each
   of the four splits, additionally re-certifies the 308 certificates
   of `stage2c2_gpt/gp_degree3_results.json.gz` at every degree they
   claim, runs its canary battery, and writes the immutable
   `capstone/independent_audit_report.json` (counts, per-degree rank
   certification, coverage set-differences, canary table with the layer
   that caught each mutation, SHA-256 of every input artifact).
   Interruptible: `--resume` restarts at the last completed bundle.
4. `python stage2c2_gpt/check_stage2c2.py` — PASS (~2 min; re-derives
   structures, re-verifies the stage's certificates and witnesses).
5. `python stage2c2_gpt/audit_all_certificates.py` — the secondary,
   generator-coupled re-audit of the same library (see §2 for what it
   does and does not establish): expect `AUDIT PASS: … 0 failures`
   (~20 min, scipy for matrix assembly, verification itself in exact
   `Fraction`).
6. `python capstone/check_transport.py` — "ALL TRANSPORT CHECKS PASS"
   (~2 min).
7. `python verify_c66_new_cases.py` and
   `python check_instances_cddlib.py` (optional pycddlib) — the
   42-instance (and the other pinned counts) exactly.

Steps 3 and 5 audit the same 132,560 certificates and agree on every
shared count (step 3's report records the comparison). Only step 3 is
independent of the programs that produced the library.

## 5. What is machine-checked vs. argued in prose

Machine-checked exactly (no trust in this document needed): every
certificate, every canary, the valid-σ count, the *completeness* of the
library's coverage of the valid σ at each of the four splits, the orbit
and stabilizer computations, the transport bookkeeping on samples, the
42-instance.

What `independent_audit.py` still takes as given, and therefore what a
reader must check by reading rather than by running (its docstring says
the same): the 25×8 row model of §1 — that is the *statement* of what
the certificates certify, re-implemented there from this prose, not
re-derived; the definition of a valid labeled side pattern; the
symmetry reduction of §§3.2–3.3 (checked by `check_split_orbits.py`,
which is stdlib and standalone, and by `check_transport.py`, which is
itself generator-coupled in exactly the two narrow respects named here
— from the generation side it imports only `monomials_of_degree`, the
serialization convention, and `VALID_BITS`, the valid-σ list; its other
import, `check_split_orbits`, is a checker); the serialization
layout of the sparse certificate vectors (a data format, tested by a
rotate-the-monomial-order canary); and the 121 `EXACT_DEGREE_NO_GO`
entries of
`gp_degree3_results.json.gz`, which are negative results carrying no
weight in the upper bound and are counted but not re-verified.

Argued in prose above, kept deliberately short so they can be audited by
reading: the hull-of-union bound and the generic-position perturbation
lemma (§3.1 — the lemma also carries the a_i = b_i boundary and the
coincidence-free genericity that §3.5 needs), instance invariance under
G (§3.2, two sentences: segments are orientation-invariant, relabeling
is renaming), the flip row-identity (§3.2, one line of algebra), the
Gordan contradiction (§3.4), and the parity step (§3.5, verified in the
Stage 2b review). The chamber model itself and the
validity enumeration carry three-way independent computational
confirmation (§1).

## 6. Provenance and honesty notes

- The certificate program ran as a multi-model pipeline (GPT-5.6 and
  Gemini 3.1 Pro as executors, Claude as adversarial reviewer) with
  every stage independently re-verified; two serious defects were caught
  along the way (a labeling gap in Stage 2a; a verifier sign bug in
  Stage 2c-1, exposed by a deliberately-impossible canary — five false
  certificates were rejected), both documented in the stage reviews.
- The **split-orbit gap**: every stage through the completion sweeps
  treated splits by size k with prefix representatives, implicitly
  assuming splits of equal size are equivalent. They are not: D₅ has
  two orbits on 2-subsets, and the sweeps covered only the {0,1} orbit.
  The gap was found while writing §3.2 of this document and closed by
  the `split02` sweep in this directory. Consequently Stage 2b's
  per-configuration theorem was **overclaimed as stated** ("any A/B
  split") until that sweep existed; the cell-wide split02 certificates
  specialize to U_ints, repairing it. This is recorded as an erratum in
  the master note.
- The **independence gap**: until 2026-07-31 the only all-library
  auditor was `stage2c2_gpt/audit_all_certificates.py`, and this
  document and the arXiv note both called it a *standalone* audit. It
  is not: it imports `quotient_matrix` and `normal_forms` from the
  generator `gp_degree3_search.py`, so the quotient-ring half of every
  check inherited the generator's Gröbner machinery, and its
  independently written half checks only specialization at U_ints —
  which provably cannot detect a multiplier that is a Gordan vector at
  U_ints but not cell-wide. The defect was raised as finding 1 of
  `reviews/GPT_repo_audit_2026-07.md` and closed by writing
  `capstone/independent_audit.py` from scratch (§2, §4 step 3), which
  re-proves the whole library by a different algorithm, agrees with the
  old auditor on every shared count, and additionally proves the
  coverage completeness nobody had checked. The wording in §2, §4 and
  the note has been corrected; no certificate changed.
- Floating-point appears only in LP support hints and search heuristics;
  every serialized object is exact (integers/Fractions) and was verified
  exactly before serialization, then re-verified by the two audits
  above.
