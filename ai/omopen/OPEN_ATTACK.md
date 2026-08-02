# Deciding the sweep's OPEN classes

Written 2026-08-01, while the (4,9) sweep in `ai/omreal` was running. This
directory is the endgame toolkit for the residue that sweep leaves behind:
the classes it can neither realize nor refute.

---

## 0. Result

**Every OPEN class was decided, and every one of them is REALIZABLE.**

| | |
|---|---|
| OPEN classes attacked | **126** — the sweep's entire residue at 26.15% of the catalog (2,426,068 rows decided) |
| **REALIZABLE**, with an exact integer 4x9 certificate | **126** |
| NON_REALIZABLE | **0** |
| STILL OPEN | **0** |
| accepted by `fpcheck.py` (this directory's independent checker) | 126 / 126 |
| accepted by `ai/omreal/checkcert.py` (the project's older one) | 126 / 126 |
| median time to realize | **3.4 s** (max 45.3 s; 934 s of deciding runs for the whole set) |

**No non-realizable-without-BFP class emerged. The conjecture of
`WALK_THEORY.md` §7, as sharpened in `ai/omminor/MINOR_THEORY.md` §4.3 —**

> *a uniform rank-4 oriented matroid on 9 elements with no biquadratic final
> polynomial is realizable*

**— is not refuted. It survived on 126 classes each of which was a genuine
candidate to refute it**, and every one of those candidates is now closed
with an explicit matrix rather than left as a gap in a search.

Alongside the realizations, each class carries an **exact integer vector u**
with `v . u > 0` for every inequality the three-term Grassmann-Plücker
relations force, which by Gordan's theorem proves that the class has no
biquadratic final polynomial. Be precise about what that adds, because it is
less than it looks:

> **Lemma.** If χ is realized by X, put u_B = log|det X_B|. Every forced
> inequality comes from an identity whose dominating term equals the sum of
> the others, so |[P][Q]| > |[S][T]| and hence v·u > 0. **Every realizable
> class carries a witness**, and by Gordan therefore has no final polynomial
> of that form.

So for a class we have *realized*, "no BFP" is a corollary of the
realization, not an independent finding. The witnesses are still worth
having, for three reasons that are real:

* **they are what the counterexample's hypothesis would have been.** A class
  that survived Weapon A would be reported as "no BFP (certified), no
  realization found" rather than "we looked and did not find one" — and
  without them that claim could not be made at all, because
  `ai/omreal/bfp.py` returning `None` conflates an infeasible LP with a
  failed exact reconstruction;
* **they are an independent cross-check.** The LP's u is not log|brackets|
  of any realization; it is an unrelated object that must satisfy the same
  ~8,100 inequalities. A class carrying both a witness and a Gordan vector
  is impossible, and none does — at either level, on 126 OPEN classes and on
  240 control classes;
* **they rule out a false OPEN.** `bfp.py` can return `None` because its
  exact reconstruction failed on a support the LP *did* find, in which case
  the class would really have a BFP and really be non-realizable and the
  sweep would have mislabelled it. The witness excludes that outright.

The other cross-implementation result on the non-realizable side, which is
not about witnesses: **this directory's independent level-0 Gordan search
agrees with `bfp.py` on every class tested** — 0 certificates on all 126
OPEN classes (matching the sweep's OPEN classification) and 40 of 40 on
classes the sweep certified NON_REALIZABLE.

The strongest statement the run supports is in §11. The short version: the
(4,9) realizability split has **no residue at all** over the portion of the
catalog the sweep has finished, and the machinery to keep it that way is a
resumable command costing a few seconds per class.

**And one actionable finding, since the sweep still has ~74% to run.** The
A1 gate reproduces 40 of 40 REALIZABLE(**repair**) classes at a median of
**0.30 s** — classes where the sweep's own wall crossing failed and its
repair ladder had to run. One-point completion decides them faster *and*
without a residue, because its inner step is an exactly-verified LP
completion rather than a
barrier method that can miss a feasible point. **Running weapon A as the
ladder's last rung, or replacing `realize._cross_wall` with the completion
LP, would very likely stop the sweep producing OPEN rows at all.** §11(4).

---

## 1. What an OPEN class is, and why it is the interesting one

`ai/omreal/sweep49.py` decides each of the 9,276,595 uniform rank-4 classes
on 9 elements by

* crossing one wall from the spanning-tree parent's realization, then
* a biquadratic final polynomial (BFP), then
* a repair ladder — direct search, mutation warm-start, heavy mutation
  warm-start —

and records OPEN when none of that fires. Two things make that residue
worth its own directory.

**It is where a counterexample would live.** `WALK_THEORY.md` §7 states the
one genuinely open possibility as "a class the walk cannot reach *and* that
has no biquadratic final polynomial", and `MINOR_THEORY.md` §4.3 sharpens
it: Proposition R shows that a class with a non-realizable deletion always
has a BFP, so the OPEN set is *enriched* in exactly the minor-minimal
population and the deletion clause of the conjecture is not an independent
hypothesis. Measured there: 451 of 451 OPEN classes had all nine deletions
realizable, with zero exceptions.

**It is small and slow-growing.** At 26.15% of the catalog the sweep had
126 OPEN rows out of 2,426,068 decided — 0.0052%, projecting to ~480
catalogue-wide. Small enough to attack one at a time with a real budget.

---

## 2. Reading a running sweep without writing to it

`ai/omreal` was being written by four sweep workers throughout. Nothing here
opens anything under it for writing.

**2.1 The enumerator was reimplemented.** The documented command
`python sweep49.py report --enumerate-open` reads `st.dat` and `Z.dat`
read-only — but it also *writes* `sweep_state/open_classes.txt`. The sweep
never reads that file, so the risk is nil, but "write nothing" is a
constraint on us and not a risk assessment, so `catalog.py` reimplements the
enumeration from the same two arrays (`st.dat` plus the catalog keys). The
counts agree with what `report` prints for every other status line, which is
the cross-check available without running it.

**2.2 Memmaps are opened `mode='r'`,** including the 1.34 GB `Z.dat`, so the
sweep's realizations can be reused as starting points at zero cost.

**2.3 `sys.dont_write_bytecode = True` is set in `catalog.py`** before any
`ai/omreal` module is imported, and `PYTHONDONTWRITEBYTECODE=1` is used for
every invocation. Importing `realize.py` would otherwise drop `.pyc` files
into `ai/omreal/__pycache__`. Verified after the fact: the only files under
`ai/omreal` modified during this work are the sweep's own certificate
shards.

**2.4 Two processes at most,** with `OMP/MKL/OPENBLAS/NUMEXPR_NUM_THREADS`
pinned to 1 before numpy or scipy load — the same discipline `sweep49.py`
records as worth ~15x.

---

## 3. Weapon A — realization by one-point completion

### 3.1 The reformulation

More budget is not a different experiment. An OPEN class has already
survived a crossing from its tree parent plus `realize_via_mutant` over 30
mutants with 10 attempts each. So the question changes instead.

Fix an element *p*. Let *Y* be an integer 4x8 configuration realizing the
**deletion** χ∖*p*. Every bracket of χ that avoids *p* is then already
correct, and the C(8,3) = 56 brackets that contain *p* are, as functions of
the missing column x_p, **homogeneous linear**:

```
for each basis B = {p} u S,     sigma_B <v_S, x_p>  >  0,
v_S defined by  det(x_{s1}, x_{s2}, x_{s3}, y) = <v_S, y>.
```

So *"does this eight-point configuration extend to a realization of χ?"* is
**one linear program in four variables** — and *as an exact mathematical
statement* that program is complete: the open cone is empty iff the exact
optimum margin is 0, so an exact solver would decide extendibility of this
*Y* definitively.

**Scope of that claim in this implementation (independent review by
GPT-5.6, 2026-08-02; accepted).** The LP here is solved in `float64` via
`scipy.linprog`, so completeness holds for the *reformulation*, not for the
code. Successes are exact — every accepted completion is re-verified in
integer arithmetic over all 126 brackets, so no realization is ever minted
by rounding. Failures are **heuristic**: float conversion of integer rows
(deletion entries reach 2²², so 3×3 minors can exceed 2⁶⁸), solver
tolerances at t ≈ 0, non-`success` statuses treated as failure, and the
finite rounding/`_shrink` cap can each discard a genuine completion. The
honest description is **exactly verified success, heuristic numerical
failure**. Nothing downstream depends on the failure direction (§4 of the
review; the code returns STILL_OPEN, never NON_REALIZABLE, on a weapon-A
failure), and all 126 classes were decided by *success*, so no verdict in
this document rests on an infeasibility claim. Closing the gap properly —
exact rational feasibility (`Ax ≥ 1` after positive scaling) or an exact
Gordan/Farkas dual certificate before declaring a cone empty — is required
before any future run reports a class as STILL_OPEN on numerical grounds.

Three consequences, and they are the reason this is stronger rather than
merely bigger.

* **Crossing a wall is the special case.** If *X* realizes the mutant
  μ_j(χ) and *p* is one of the four elements of the flipped basis B_j, then
  *X* with column *p* deleted realizes χ∖*p* exactly — the only bracket that
  disagreed was B_j, and B_j contains *p*. So every crossing the sweep
  attempts is one (*Y*, *p*) pair here, answered exactly where the barrier
  method `realize.cone_push` answers optimistically.
* **The deletions are easy, and there are nine.** χ∖*p* is a uniform rank-4
  chirotope on eight elements: milliseconds to realize, against seconds and
  usually failure for χ. Each fresh seed gives a different point of a
  9-dimensional realization space, so *Y* can be sampled in bulk. And the
  source never runs dry: `MINOR_THEORY.md` §4.3 measured all nine deletions
  of an OPEN class realizable, 451 of 451.
* **A failure names its cause.** When the LP says no, the constraints
  binding at the optimum name the elements holding the cone shut. Moving
  *those* rather than a random column is what turns a random walk into a
  search.

### 3.2 The search

```
for each of the nine deletions p:
    Y <- an exact integer realization of chi\p, from
         (T1) the sweep's stored realization of the TREE PARENT, pulled back
              through the witness group element and restricted;
         (T2) the same for each already-realized TREE CHILD;
         (S1) a fresh realization search on the (8,4) problem;
    repeat:
        one completion LP for x_p.  feasible -> done.
        infeasible -> propose a move: re-place one BLOCKER column at the
        optimum of a random objective, keeping every sign of chi\p and a
        randomised margin; accept on the completion margin, Metropolis tail.
```

**CORRECTION (independent review by GPT-5.6, 2026-08-02; verified).** This
section originally claimed the LP "returns the best achievable margin for
x_p *even when it is negative*", and that hill-climbing that number turns
the walk into a descent. **That is false.** The program is
`max t s.t. (A/|a|)x >= t, |x|_inf <= cap, t <= 1`, and `x = 0, t = 0` is
always feasible, so the exact optimum satisfies `t* >= 0` for every input:
`t* > 0` exactly when this eight-point configuration extends, `t* = 0` when
it does not. Negative values only ever arise from the floating-point
solver. Consequently the exact margin is **flat at zero across all
non-extendible configurations** and supplies no gradient among them; the
acceptance rule is not the descent this section described.

What remains true is the empirical observation, and it is now reported as
just that — an effect whose mechanism is not established (the plausible
remaining candidate is the blocker-guided move proposal, not the margin
value). Measured on rows that survived a 60 s pass with the
undirected walk: row 586623 survived 1,920 completion LPs and then fell in
4.6 s; row 1213079 in 11.7 s; row 1200032 in 8.7 s. (Numbers corrected to
match `run2.log` after review finding D2.)

The exploratory move deliberately allows small margins (down to 0.02 of the
Chebyshev radius). The configurations that open a completion cone are often
near the boundary of the deletion's own realization space, not at its
analytic centre.

`realize.realize` with a large budget runs last as a **control**. If it ever
succeeded where the structured search failed, the structure would be wrong.
It never did (0 of 126).

### 3.3 Exactness

Everything is integer.

* *Y* is an integer matrix; the constraint rows are exact 3x3 integer
  determinants of its columns.
* The LP proposes x_p in floating point; it is rounded to integers at
  increasing denominators and re-checked against the **exact** rows.
* The completed 4x9 matrix then has all C(9,4) = 126 brackets recomputed
  exactly and compared with χ, before anything is written.
* Transported realizations from the sweep's store are re-checked bracket by
  bracket and required to differ from χ in exactly one position before use,
  so a group-convention error is caught rather than propagated.

A float never touches a verdict. Output is emitted in `ai/omreal`'s
certificate schema, and `ai/omreal/checkcert.py` accepts it unchanged.

---

## 4. Weapon B1 — non-realizability in exponent space, and its exact negation

### 4.1 Gordan's dichotomy is the whole design

Substitute y_B = χ(B)·[B], so a realization has every y_B > 0. A bracket
identity Σ_k ε_k [P_k][Q_k] = 0 becomes Σ_k s_k y_{P_k} y_{Q_k} = 0 with
s_k = ±1 read off from χ. If exactly one term is the odd one out, it equals
the sum of the others and therefore **strictly dominates** each of them; in
logs u = log y that is `v . u > 0` with v = e_P + e_Q − e_S − e_T in Z^126.
Collect all of them into V. Then **exactly one** of

* **(G)** ∃ w ≥ 0, w ≠ 0, with Σ w_i v_i = 0 — a final polynomial: for any
  realization 0 = Σ w_i (v_i·u) > 0, so none exists;
* **(W)** ∃ u with v_i·u > 0 for every i,

holds. At the three-term support this is exactly the biquadratic final
polynomial of Bokowski and Richter-Gebert that `ai/omreal/bfp.py` searches
for; **(W)** is the side the project did not have.

Both are searched by LP and then reproduced exactly:

* **(G)** the LP's support is fed to an exact rational null-space
  computation; the weights are emitted as integers and Σ w_i v_i = 0 is an
  integer identity.
* **(W)** the LP's u is scaled and rounded to integers and V·u > 0 is
  re-checked as an integer matrix-vector product. Rounding is cheap to make
  safe: every v_i has entries in {−1, 0, 1} with ‖v_i‖₁ ≤ 4, so rounding u
  to k/D moves v_i·u by at most 2/D; the search simply raises D until the
  **exact** integer check passes, so the bound is motivation and not part of
  the proof.

Neither certificate depends on the LP being right about anything: what is
emitted is re-derived in integers, and the independent checker re-derives it
a third time from the combinatorics alone.

### 4.2 Widening the support

`gplib.py` generates the whole one-step Plücker exchange family

```
sum_{k=0}^{r} (-1)^k [a_1 .. a_{r-1} b_k] [b_0 .. b^_k .. b_r] = 0
```

for every 3-subset *A* and 5-subset *B* of the ground set. Terms whose first
bracket repeats an index vanish, so the term count is governed by |A ∩ B|:

| \|A ∩ B\| | terms | count at (9,4) | what it is |
|---|---|---|---|
| 2 | 3 | **1,260** | the classical three-term Grassmann-Plücker relations (each arises 4 times; de-duplicated) |
| 1 | 4 | **3,780** | rank-3 relations of a contraction, lifted |
| 0 | 5 | **504** | genuinely rank-4, on eight elements |
| 3 | 2 | — | trivial, discarded |

**Level L0** is the three-term family alone — bit-for-bit `bfp.py`'s support,
including its term order, so an L0 certificate produced here can be handed
to `ai/omreal/checkcert.py`. **Level L1** is all three families: 5,544
relations, ~8,100 forced inequalities against L0's 2,520.

A relation contributes inequalities only when its χ-induced signs split
(N−1, 1). When they do not split at all — every term the same sign — a
nonempty sum of strictly positive numbers is zero and the class is
non-realizable outright; that is emitted as a `MONOCHROME` certificate. It
cannot happen for a three-term relation of a valid chirotope but can for the
four- and five-term ones. It never did.

### 4.3 The identity table is the dangerous part, so it is tested at the source

A sign error in an ε_k would manufacture a spurious "unique odd term", hence
an invalid inequality, hence Gordan vectors for **realizable** classes — and,
for an OPEN class, a fake refutation of the conjecture. This is the failure
mode this research program has been burned by before, so it is checked
before anything downstream:

> every generated identity is evaluated on random integer 4x9 matrices with
> exact integer determinants and must come out **exactly zero**.

1,260 + 3,780 + 504 relations x 60 random configurations, 0 failures. A
deliberately flipped ε is caught by the same test (`python gplib.py`). The
independent checker repeats it for every relation a certificate names, and
for a sample of the whole family behind a witness.

### 4.4 Two strengthenings that look attractive and are worthless

Both are recorded so the next reader does not re-derive them.

**AM-GM.** From y_p y_q = y_s y_t + y_u y_v one also gets
y_p y_q ≥ 2√(y_s y_t y_u y_v), i.e. `d·u ≥ 2 log 2` with
d = 2e_p + 2e_q − e_s − e_t − e_u − e_v. But d = v₁ + v₂ is already the sum
of the two basic inequalities, so it lies in the cone the LP searches and
the constant cannot be used. **Adds nothing.**

**The upper bound.** |big| < 2·max(|small₁|, |small₂|) is genuine extra
information, and it is disjunctive; one might branch on it. Whichever branch
is taken it has the wrong Farkas sign. The system is homogeneous — if u is a
solution so is *tu* for every t > 0 — so any solution can be shrunk until
every bound of the form `v·u < log 2` holds, and the Farkas multiplier on
such a row must be zero in any infeasibility certificate. Branching reduces
to plain BFP. **Adds nothing.**

For completeness: the *dual* matroid's three-term relations are also not new
at (4,9). The dual relation on L\* (3 elements) and {a,b,c,d} ⊂ E∖L\* has
brackets E∖(L\*∪{x,y}) = {the other two of the four} ∪ {e,f}, which is the
primal relation with L = {e,f} on the same four elements. **Self-dual.**

---

## 5. Weapon B2 — general final polynomials, and why they are weaker here

### 5.1 The formulation

A final polynomial in the sense of Bokowski and Sturmfels keeps the
arithmetic and throws away the ordering — the mirror image of a BFP. Take
any polynomial combination

```
P  =  sum_{j,m}  lambda_{j,m} * m * R_j          (m a bracket monomial)
```

with R_j the relations in y-coordinates. Every R_j vanishes on a
realization, so P(y) = 0. If every coefficient of P, expanded in the
monomial basis, has the same weak sign and at least one is strict, then
P(y) ≠ 0 for y > 0. No realization exists. Degree 2 is m = 1; degree 3 is m
a single bracket. Finding λ is a linear feasibility problem.

### 5.2 BFP is *not* the degree-2 case of this hierarchy

The task framing assumed it is; it is not, and building the driver around
that assumption would have produced hours of debugging a non-bug.

A Gordan vector is a statement about **exponent vectors** cancelling in
Z^126. A final polynomial is a statement about **monomials** cancelling.
{y₁y₂, y₃y₄} and {y₁y₃, y₂y₄} have the same exponent sum and are different
monomials, so the two conditions are genuinely different. Converting a
Gordan vector into a polynomial identity means clearing the multiplicative
statement ∏(y_p y_q / y_s y_t)^{w_i} = 1, which produces a polynomial of
degree ≈ 2·Σw_i. `MINOR_THEORY.md` §7 measures those total weights at
~10⁵ — mean 249,833 for minor-minimal classes, 106,676 otherwise. The
equivalent final polynomial has degree of order 10⁵. Degree 3 is not close.

There is also a clean structural reason the first rung is empty:

> **The degree-2 rung over the three-term relations is infeasible for every
> chirotope.** The monomial {B, B'} of a term determines its relation, since
> L = B ∩ B' and {a,b,c,d} = B △ B'. So no two of the 1,260 relations share
> a monomial: the incidence matrix has **exactly one nonzero per row**
> (measured: 3,780 monomials, 3,780 nonzeros), and `Aλ ≤ 0` forces λ_j·s_jk ≤ 0
> for all three k of each relation. Since the s_jk are not all equal, λ = 0.

Widening to L1 breaks that (6,615 monomials, 21,420 nonzeros — monomials
*are* shared) but does not help in practice.

### 5.3 Measured — and it is not vacuous

`python fpprobe.py --limit 25 --deg3` → `data/fp_probe.json`,
`data/fpprobe.log`. 25 classes per population.

| population | FP(2) at L0 | FP(2) at **L1** | FP(3) at L0 |
|---|---|---|---|
| OPEN (all realizable, as it turns out) | 0 / 25 | 0 / 25 | 0 / 25 |
| certified NON_REALIZABLE | 0 / 25 | **3 / 25** | 0 / 25 |
| certified REALIZABLE | 0 / 25 | 0 / 25 | 0 / 25 |
| LP size | 1,260 cols x 3,780 monomials, 0.03 s | 5,544 x 6,615, 0.2 s | 158,760 x 288,540, **6.6 s** |

Three things to read off.

**It works, and the widened support is what makes it work.** Three of the 25
certified non-realizable classes get a genuine degree-2 final polynomial —
but only over L1, never over the three-term relations alone (where §5.2
proves it is impossible). These certificates are new to this repository: the
biquadratic method's support cannot express them. A typical one, after
sparsification, is **four generators over 8 monomials**, all coefficients
−1:

```
row 337599, degree 2, level L1     (data/fp_found.jsonl)
  c = -1   {"kind":"pl","A":[1,3,7],"B":[2,5,6,8,9]}
  c = -1   {"kind":"pl","A":[1,7,8],"B":[2,3,5,6,9]}
  c = -1   {"kind":"pl","A":[2,6,9],"B":[1,3,5,7,8]}
  c = -1   {"kind":"pl","A":[5,6,9],"B":[1,2,3,7,8]}
```

Four five-term Plücker exchange relations whose y-expansions cancel down to
eight monomials of one sign. `fpcheck.py` accepts it, and the raw LP support
was ~4,270 generators — the sparsifying pass (minimise ‖λ‖₁ over the same
cone) is what makes it a readable object rather than a megabyte of JSON.

**These are second opinions, not new verdicts, and the file says so.** Every
row in `data/fp_found.jsonl` carries `sweep_status` and
`also_has_L0_gordan_vector`. Both hits in the saved sample are rows the
sweep had already certified NON_REALIZABLE, and both independently yield a
level-0 Gordan vector here (80 and 82 terms). So a final polynomial in this
directory is a *second, independent* refutation of a class that was already
refuted — which is why 3 in 25 is interesting rather than alarming. **No FP
certificate anywhere in this work asserts non-realizability of a class not
otherwise refuted.**

**The rate is approximate, and the reason is worth knowing.** The control
populations are drawn with `rng.choice` from `rows_with_status(...)`, and
those arrays *grow while the sweep runs* — so the same seed picks different
classes at different times and the probe is not bit-reproducible against a
live sweep. The recorded run (`data/fp_probe.json`) found 3 of 25; a second
draw later found 2 of 25. Read it as **roughly one in ten**, not as a
fraction. (The OPEN population is read from the frozen snapshot file and
*is* reproducible; `--limit 25` takes its first 25 rows, not all 126.)

**Support beats degree.** Degree 3 over the three-term relations — a
158,760-column LP, 220x the work — finds *nothing*, while degree 2 over the
wider families finds three. That is worth knowing before anyone invests in
degree 4.

**Soundness holds, and it was the fatal gate.** 0 of 25 on certified
realizable classes at every degree and level, and 0 of 25 on the OPEN
classes — which we now know are realizable, so those 25 are a second
soundness sample. A single hit there would have meant an invalid identity
and would have voided everything in §4 as well.

The machinery is proved to work by a **positive control**: flip bracket
signs of a real chirotope until one relation is monochrome; the resulting
sign vector is realizable by nothing, and the one-generator final polynomial
P = ±R_j proves it. The LP finds it, the exact reconstruction emits it, the
independent checker accepts it, and three sabotages of it are rejected
(canaries C19–C21).

**What it does not do is decide an OPEN class.** For the reason in §5.2 the
coefficient-space hierarchy at reachable degrees is far weaker than the
exponent-space one, so it was never the likely source of a counterexample;
it is here because the *combination* "no Gordan vector at L1 **and** a final
polynomial" is precisely what a counterexample would look like, and that
combination has to be searched for rather than assumed absent.

---

## 6. Certificate formats

All records are JSONL with `n`, `r`, `chi` (126 signs in colex order) and
`verdict`. `fpcheck.py` reads all of them; `ai/omreal/checkcert.py` reads the
first and, via `certs_nonrealizable_bfpschema.jsonl`, the second at level L0.

A **relation spec** names an identity combinatorially; the checker rebuilds
the identity from its definition rather than trusting coefficients.

```json
{"kind": "gp3", "L": [1,9], "abcd": [5,6,7,8]}
{"kind": "pl",  "A": [1,2,3], "B": [4,5,6,7,8]}
```

`gp3` is `[Lab][Lcd] − [Lac][Lbd] + [Lad][Lbc] = 0` with terms in that
order. `pl` is `Σ_k (−1)^k [A b_k][B∖b_k] = 0` with vanishing terms dropped
and the survivors kept in increasing k; `gp3` is the |A ∩ B| = 2 case,
written separately only so that the term indices match `bfp.py`'s.

**REALIZABLE** — `ai/omreal`'s schema, unchanged.

```json
{"n":9,"r":4,"chi":"...","verdict":"REALIZABLE","matrix":[[...],[...],[...],[...]]}
```

**NON_REALIZABLE / GORDAN** — weighted strict inequalities.

```json
{"verdict":"NON_REALIZABLE","method":"GORDAN","level":"L1",
 "terms":[{"rel":{...},"big":0,"small":2,"w":17}, ...]}
```
Checked: each relation is an identity; `big` is the **unique** odd term
under χ; weights positive; no duplicates; and Σ w_i (e_P+e_Q−e_S−e_T) = 0
exactly.

**NON_REALIZABLE / MONOCHROME** — one relation, all terms one sign.

**NON_REALIZABLE / FP** — a polynomial certificate.

```json
{"verdict":"NON_REALIZABLE","method":"FP","degree":3,
 "gens":[{"rel":{...},"mult":[[2,4,6,9]],"c":[-3,1]}, ...]}
```
Checked: each relation is an identity; the combination is expanded over Q in
the monomial basis; every coefficient must share one weak sign and at least
one must be strict.

**NO_FINAL_POLYNOMIAL / GORDAN_WITNESS** — the proof that no Gordan
certificate exists.

```json
{"verdict":"NO_FINAL_POLYNOMIAL","method":"GORDAN_WITNESS",
 "families":["gp3","pl4","pl5"],"u":[<126 integers>]}
```
Checked the strong way: **the record carries only u**. The checker
enumerates the families itself, rebuilds every forced inequality, and
requires `v·u > 0` for all of them. A certificate therefore cannot
understate the support it claims to have ruled out, and one whose
`families` omits `gp3` is refused as a statement about biquadratic final
polynomials at all.

---

## 7. Validation, and the canaries

### 7.1 Gates, all run before any OPEN class was touched

`python validate.py --budget 120` → `data/validation.json`,
`data/validation.log` (the shipped run used `--budget 120`, not the quick
`--n 40` variant; review finding D6).

| gate | claim | measured | |
|---|---|---|---|
| — | the identity tables really are identities | 1,260 + 3,780 + 504 relations x 60 random integer 4x9 configurations, exact integer determinants, **0 failures** | PASS |
| **A1** | weapon A reproduces REALIZABLE(**repair**) — the hard-but-solved population, where the sweep's crossing failed and its repair ladder had to run | **40 / 40**, median **0.30 s**, max 26.1 s | PASS |
| **A2** | weapon A on REALIZABLE(walk), as a smoke control | **40 / 40**, median 0.01 s | PASS |
| **B1** | level-0 Gordan fires on every certified NON_REALIZABLE class | **40 / 40** | PASS |
| **B2** | level-0 Gordan fires on NO certified REALIZABLE class (**soundness — fatal if violated**) | **0** false positives on 80 | PASS |
| **B2** | the same at level L1, with the new four- and five-term families | **0** false positives on 80 | PASS |
| **B3** | the exact witness exists for every certified REALIZABLE class | **80 / 80** at L0, **80 / 80** at L1 | PASS |
| **B3** | and for none of the certified NON_REALIZABLE ones (Gordan's dichotomy) | **0 / 40** at L0, **0 / 40** at L1 | PASS |
| **B4** | every certificate produced during the gates is accepted by `fpcheck.py` | 80 realizations + 40 Gordan vectors + 160 witnesses, **0 rejections** | PASS |
| **B4** | and the level-0 ones by `ai/omreal/checkcert.py` in its own schema | 80 realizations + 40 Gordan vectors, **0 rejections** | PASS |

Two of those deserve comment. **B1 is an independent reimplementation
agreeing with the sweep** — level L0 is `bfp.py`'s support rebuilt from the
definitions, and it fires on every class the sweep certified non-realizable.
**B2 is the fatal one**: a Gordan vector for a realizable class would mean
the identity table emits an invalid inequality and every non-realizability
verdict in this directory would be void.

**B3 is the dichotomy, measured rather than assumed.** Gordan's theorem says
the witness exists exactly when no certificate does; observing 80/80 and
0/40 at both levels is a mutual canary on the whole inequality machinery,
since a class carrying both would be impossible.

### 7.1a The two inequality systems agree row for row

A witness is only as strong as the system it is checked against, so the
generator's and the checker's systems were compared directly — as *sets of
exponent vectors*, on six OPEN classes at both levels:

| level | rows | distinct | identical sets? |
|---|---|---|---|
| L0 | 2,520 (every class) | 2,520 | **yes**, 6 / 6 classes |
| L1 | 8,172 – 8,644 (varies by class) | 7,082 – 7,476 | **yes**, 6 / 6 classes |

`gplib.py` and `fpcheck.py` share no code and dedupe identities by different
keys, so this is a genuine cross-implementation agreement rather than a
tautology. The L0 count is 1,260 relations x 2 for every chirotope, as it
must be: a three-term relation of a valid chirotope always has exactly one
dominating term. The L1 count varies because a four- or five-term relation
contributes only when its signs split (N−1, 1).

### 7.2 Sabotage canaries

`python canaries.py` → `data/canaries.jsonl` (the records),
`data/canaries_result.json` (the verdicts).
**7 controls accepted, 23 sabotages rejected (21 with a named diagnosis
required and matched; C4/C17 accept any rejection, and their diagnoses do
name the corruption), 0
failures.** Both checkers are exercised: `fpcheck.py` on every record kind,
and `ai/omreal/checkcert.py` on level-0 Gordan vectors re-expressed in its
schema and on realization certificates. A sabotage counts as passing only if
the rejection *names* the corruption; a generic parse error would not do.

| | sabotage | rejected because |
|---|---|---|
| C1 | one weight increased by 1 | the combination does not cancel |
| C2 | `big`/`small` swapped on one term | that term is not the dominating one |
| C3 | one inequality dropped | does not cancel |
| C4 | certificate moved to a realizable class | the dominating term changes |
| C5 | a zero weight | weight not positive |
| C6 | a degenerate relation spec (A ⊂ B) | fewer than three surviving terms |
| C7 | a relation spec with a repeated element | malformed |
| C8 | a duplicated inequality | duplicate |
| C9 | witness with one coordinate corrupted | an inequality fails |
| C10 | witness moved to a class that HAS a BFP | an inequality fails |
| C11 | witness that silently drops the three-term family | says nothing about BFPs |
| C12 | the trivial witness u = 1 | an inequality fails |
| C13a | two columns swapped (relabelling on one side only) | a bracket has the wrong sign |
| C13b | one column negated (reorientation on one side only) | a bracket has the wrong sign |
| C14 | realization moved to another realizable class | a bracket has the wrong sign |
| C15–C18 | the same four, in `checkcert.py`'s schema | (its own diagnoses) |
| C19 | final polynomial with a spurious extra generator | the polynomial has both signs |
| C20 | final polynomial moved to a realizable class | both signs |
| C21 | final polynomial whose relation has been substituted | both signs |
| C22 | a degree-2 certificate carrying a degree-3 multiplier | wrong monomial degree |

**Two canaries had to be redesigned after the checker correctly accepted
them,** and the reason is the same both times and worth recording:
**these certificates are self-validating.**

* "Realization with one matrix entry off by one" is *not* a sabotage. Any
  integer matrix whose 126 brackets match the sign string certifies the
  class, and nudging a well-centred entry by 1 flips no bracket, so the
  perturbed matrix realizes the same class. Replaced by C13a/C13b — a
  relabelling and a reorientation applied to the matrix but not to the
  chirotope, which are the corruptions a real bug produces.
* "Final polynomial with one coefficient tripled" is not a sabotage either
  (c·P is a final polynomial whenever P is), and neither, at first attempt,
  was "substitute a different relation": the substitute happened to be
  monochrome under the rigged sign vector too, so the result was another
  valid certificate. C21 now picks a substitute that is *not* monochrome.

That is a property of the design, not a weakness in the canaries: a
certificate here is checkable from its own contents, so the only way to
break one is to make it false. It does mean canaries have to be chosen with
care, and that the ones above were checked to actually bite.

---

## 8. Results

The snapshot (`data/open_set.txt`, state in `data/enumerate_final.txt`) was
taken with the sweep at **26.15%** — 2,426,068 rows decided — and lists
**126 OPEN rows**, at tree depths 13–17 (1, 4, 32, 54 and 35 rows
respectively). Per-class outcomes are in Appendix B and in
`data/results.jsonl`.

| | |
|---|---|
| attacked | 126 |
| **REALIZABLE** | **126** |
| NON_REALIZABLE | 0 |
| STILL_OPEN | 0 |
| total wall time of the deciding runs | **934 s** (plus ~670 s spent on the 13 first-pass runs that failed before the searcher was improved) |
| time per class | median **3.4 s**, min 0.2 s, max 45.3 s |
| completion LPs that came back *infeasible* | **47,723** in total; 2,938 on the hardest single class |
| largest matrix entry emitted | 262,144; only 8 of the 126 exceed 16,384 |

Which source produced the winning eight-point configuration:

| source | classes |
|---|---|
| `walk` — a fresh (8,4) deletion realization, then the guided hill-climb | 103 |
| `store_walk` — the sweep's stored parent/child realization, then the hill-climb | 14 |
| `store` — the sweep's stored realization, completed immediately | 5 |
| `fresh` — a fresh deletion realization, completed immediately | 4 |
| `control` — `realize.realize` with a large budget | **0** |

The control never fired. That is the intended reading of it: if the
project's existing searcher had succeeded where the structured search
failed, the structure would be wrong.

**How the run was staged, and what the timings mean.** The set grew under
us — the sweep keeps producing OPEN rows — so the attack ran in four passes,
which is exactly what the resume path is for.

| pass | snapshot | new rows | searcher | outcome |
|---|---|---|---|---|
| 1 | 107 rows, sweep at 23.3% | 107 | undirected random walk, `--budget 60` | 94 realized, **13 survived** |
| 2 | same | 0 | hill-climb on the completion margin (§3.2), `--budget 240` | **all 13** realized, 1.9–28.6 s each |
| 3 | 118 rows, 24.7% | 11 | hill-climb | all 11, 1.1–11.0 s |
| 4 | 124 then 126 rows, 26.1% | 8 | hill-climb | all 8, 1.5–20.3 s |

Passes 3 and 4 redid **nothing**: a row with a terminal verdict is skipped,
which is the resume path exercised in anger rather than described.

Two things follow for reading the `s` column of Appendix B. It records the
*deciding* run, so for the 13 rows of pass 2 it excludes the 60 s they
already burned in pass 1. And it mixes two searchers: the 45.3 s maximum
belongs to the undirected walk. **Under the final searcher no class in the
set took more than 28.6 s**, and the 13 hardest — the ones an undirected
walk could not touch — took a median of about 9 s.

**Non-realizability certificates: none.** `data/certs_nonrealizable.jsonl`
and `data/certs_nonrealizable_bfpschema.jsonl` were never created, because
no Gordan vector, no monochrome relation and no final polynomial fired on
any OPEN class at any level or degree tried. Certificates of that shape do
exist and are exercised — 40 of them per validation run, in
`data/validation_gordan.jsonl` and `data/validation_gordan_bfpschema.jsonl`,
plus the rigged final polynomial in `data/fp_positive_control.jsonl`.

Both checkers accept everything produced:

```
$ python fpcheck.py --trials=16 data/certs_realizable.jsonl data/certs_no_bfp.jsonl
data/certs_realizable.jsonl: 126 distinct classes
    REALIZABLE/-                           126
data/certs_no_bfp.jsonl: 0 distinct classes
    NO_FINAL_POLYNOMIAL/GORDAN_WITNESS     252
ALL CERTIFICATES ACCEPTED

$ python ../omreal/checkcert.py data/certs_realizable.jsonl
data/certs_realizable.jsonl: 126 distinct classes
    REALIZABLE       126
    NON_REALIZABLE   0
    RESIDUE          0
ALL CERTIFICATES ACCEPTED
```

(252 = 126 classes x two family sets. `fpcheck` reports "0 distinct classes"
for the witness file because it only tracks class identity for records that
claim REALIZABLE or NON_REALIZABLE; a witness claims neither.)

---

## 9. Trust boundaries

Stated as what would have to be wrong.

**Unconditional.** A `REALIZABLE` verdict is an integer matrix whose 126
brackets are recomputed exactly by two checkers that share no code with the
producer or with each other. Nothing about oriented matroid theory, the
catalog, the mutation tree, or Roudneff–Sturmfels is load-bearing for it.
For these classes to be wrong, integer determinants would have to be wrong
in two independent implementations.

**Unconditional given Gordan's theorem (1873).** A `NO_FINAL_POLYNOMIAL`
witness is an integer vector satisfying an explicit integer inequality
system that the checker rebuilds from the definitions. The only external
input is Gordan's theorem itself.

**Depends on the definition of "biquadratic".** "No BFP" here means "no
Gordan vector over the inequalities forced by the three-term
Grassmann-Plücker relations" — the support `ai/omreal/bfp.py` uses, which is
also the support `MINOR_THEORY.md`'s Proposition R and the sharpened
conjecture are stated against. A treatment that admits a wider family of
biquadratic inequalities would be making a different claim. The L1 witness
covers a strictly wider family (4- and 5-term exchange relations), so the
statement survives that particular widening.

**Depends on the catalog, and the chain was checked.** Which rows are OPEN,
and the sign string attached to a row, come from `coverage_4_9.npz` and from
the live sweep's `st.dat`. If the catalog mislabelled a class, the
certificate would still be a true statement about *the sign vector it names*
— the chirotope string is carried in every record — but the mapping to a
catalog row would be wrong. Nothing here re-derives the catalog. What was
checked, end to end:

| link | result |
|---|---|
| the three raw arrays of `coverage_4_9.npz` against `MANIFEST.json`'s `array_sha256` | **match** |
| the `chi` of every result row against the catalog chirotope decoded **from the npz**, not from the sweep's copy of it | **126 / 126** |
| certificate chirotopes: count, distinctness, and equality with the result set | 126, all distinct, **sets equal** |
| rows attacked vs. the snapshot, and snapshot chirotopes vs. the catalog | **equal**, **126 / 126** |
| status of all rows in the live sweep, after the attack | still `OPEN` — the sweep decided none of them itself, so these are our verdicts and not a re-derivation of its |

**Depends on nothing else.** In particular no verdict depends on the
mutation tree, on Corollary B of `WALK_THEORY.md`, or on BFP completeness.
The tree is used only as a *source of starting points* (T1/T2), and every
transported matrix is re-checked bracket by bracket before use.

**A snapshot, not a final answer.** The sweep was at 26.15% when the final
snapshot was frozen, and had moved on within the hour.
The OPEN set grows as the sweep proceeds; §10 is how to finish it.

---

## 10. Re-running when the sweep finishes

`attack.py` is resumable and keyed by catalog row. `data/results.jsonl` is
append-only; a row with a terminal verdict is skipped, a `STILL_OPEN` row is
retried only when offered a larger budget. So the final pass costs the new
rows plus the escalation of any survivors, not the whole set.

```bash
export PYTHONDONTWRITEBYTECODE=1
cd ai/omopen

python gplib.py                       # identity tables + their own self-test
python fpcheck.py --selftest
python canaries.py                    # 23 sabotages must be rejected
python validate.py --n 40             # the gates; must print VALIDATION PASSED

python attack.py enumerate            # snapshot the OPEN set (read-only)
python attack.py run --budget 60 --verify-identities
python attack.py run --budget 240 --walk-depth 60 --fp     # escalate survivors
python attack.py run --budget 1800 --walk-depth 200 --fp   # if any remain
python attack.py witness              # certify "no BFP" for every class
python attack.py report
python table.py

python fpcheck.py data/certs_realizable.jsonl data/certs_no_bfp.jsonl
python ../omreal/checkcert.py data/certs_realizable.jsonl
```

**What to do if a class survives everything.** Do not report it as
non-realizable, and do not report it as a counterexample. It is
`STILL_OPEN`, and the honest statement is "no biquadratic final polynomial
(certified), no realization found". The escalation that would come next, in
order of expected value:

1. more `--walk-depth` and more budget.  Note what actually cleared the
   13 first-pass survivors, though: not budget, but making the walk a
   hill-climb on the completion margin.  If more of the same is not
   working, the move to look for is another *objective*, not another hour;
2. the class-lookup neighbour source that is *not* implemented here — T1/T2
   use only tree edges, so only the parent and already-realized children are
   available; canonicalizing each of the ~15 mutants and looking up its row
   would give every realizable neighbour, at the cost of the group element;
3. degree-4 final polynomials on a restricted multiplier set, or a
   Positivstellensatz/SDP relaxation — §5.2 says why that is a long way from
   reaching a BFP-equivalent certificate;
4. a SAT/SMT encoding of the chirotope axioms with a DRAT proof, which is
   what `WALK_THEORY.md` §7 asks for and what nothing here supplies.

**If a class ever yields a Gordan vector at L1 or a final polynomial while
carrying a verified L0 witness, that is the counterexample** — a
BFP-resistant non-realizable uniform oriented matroid at n = 9, three to
five elements below the smallest known. `attack.py` labels it in the record
note. Before believing it: re-run `gplib.py`'s identity test, re-run the
canaries, and check that the class does *not* also carry a witness at the
same level (it cannot; if it does, there is a bug).

---

## 11. What this supports

**Strongest supported statement.**

> Of the **126** classes the (4,9) sweep left OPEN over the first **26.15%**
> of the catalog (2,426,068 rows decided; snapshot `data/open_set.txt` and
> `data/enumerate_final.txt`, 2026-08-01), **all 126 are realizable**, each with an explicit integer
> 4x9 matrix verified by two independent checkers that share no code with
> the producer or with each other. **No non-realizable class without a
> biquadratic final polynomial was found**, and every one of the 126 also
> carries an exact rational certificate that it has no biquadratic final
> polynomial — and none over the wider four- and five-term Plücker exchange
> support either.

Consequences, in decreasing strength.

1. **The sweep's residue over its finished portion is empty.** Of the
   2,426,068 classes the sweep had decided when the snapshot was taken, not
   one is left undecided: 2,395,429 realizable by the sweep, 30,513
   non-realizable by the sweep, 126 OPEN and now realizable here. The blank
   (4,9) row of Finschi–Fukuda–Moriyama gets no asterisk *over that
   quarter*; the remaining three quarters are the sweep's to finish, and §10
   is how to close whatever residue they leave.
2. **126 candidate counterexamples eliminated.** These were the only classes
   in that quarter that could have refuted the conjecture: undecided, with
   no biquadratic final polynomial found. Prior support for the conjecture
   was "0 residue in 10,000" (`WALK_THEORY.md` §5) and "451 of 451 OPEN
   classes have all deletions realizable" (`MINOR_THEORY.md` §4.3) — the
   first a population with no candidates in it at all, the second a
   structural fact about the candidates rather than a decision. This is the
   first time the candidate set itself has been emptied with certificates.
   Note the honest scope, per the Lemma in §0: once a class is realized, its
   lack of a BFP follows, so the 126 witnesses are a cross-check and would have
   been the hypothesis of a counterexample, not an extra result.
3. **The OPEN set is a searching artefact, not a structural one.** Median
   3.4 s to realize a class the sweep gave up on after its whole ladder;
   the hardest needed 45 s. This replicates, on the residue, what
   `WALK_THEORY.md` §5 concluded about difficulty and `MINOR_THEORY.md` §7
   about minor-minimality: *difficulty is a property of searching from
   scratch, not of the oriented matroid.* The one-point completion
   reformulation is why — it replaces a 36-dimensional search with sampling
   a 9-dimensional one plus an exact 4-variable oracle.
4. **A concrete recommendation for `sweep49.py`.** The A1 gate is a result
   in its own right: **40 of 40 REALIZABLE(repair) classes reproduced, median
   0.30 s.** Those are classes where the sweep's wall crossing failed and its
   repair ladder had to run. One-point completion decides them faster *and*
   without a residue, because its inner step is an exactly-verified LP
completion rather than a
   barrier method that can miss a feasible point. Swapping
   `realize._cross_wall` for the completion LP — or simply running weapon A
   as the ladder's last rung instead of `realize_via_mutant` — would very
   likely take the sweep's OPEN count to zero at source, at no extra cost.
5. **BFP-completeness at (4,9) is not settled, and this does not settle
   it.** What is settled is that on this population BFP-incompleteness never
   *bit*: no class needed a certificate the biquadratic method could not
   give, because no class needed a non-realizability certificate at all.

**What would change the verdict.** A single OPEN class that survives the
escalation of §10 *and* yields a final polynomial. Nothing observed points
that way, and the projection to the full catalog (~480 OPEN classes at the
observed rate of 0.0052%) makes the finishing run a few hours, not a
research program.

---

## Appendix A — files

| file | what |
|---|---|
| `gplib.py` | the identity families, and the exact test that they are identities |
| `gordan.py` | weapon B1: Gordan vectors and the exact no-final-polynomial witness |
| `fpoly.py` | weapon B2: general final polynomials in coefficient space |
| `weaponA.py` | weapon A: one-point completion over the nine deletions |
| `catalog.py` | read-only access to the catalog and the live sweep |
| `attack.py` | the resumable driver |
| `validate.py` | the gates |
| `canaries.py` | the sabotages |
| `fpcheck.py` | **the independent checker** — stdlib only, shares no code with any of the above |
| `fpprobe.py`, `table.py` | measurement and reporting |
| `data/certs_realizable.jsonl` | **the 126 realization certificates** — the result |
| `data/certs_no_bfp.jsonl` | the 252 "no final polynomial" witnesses (126 classes x two family sets) |
| `data/results.jsonl` | per-class outcome log; the resume key |
| `data/open_set.txt`, `data/enumerate_final.txt` | the OPEN snapshot, and the sweep state when it was taken |
| `data/validation.json`, `data/validation_*.jsonl` | the gates and the certificates they produced |
| `data/canaries.jsonl`, `data/canaries_result.json` | the sabotages and their verdicts |
| `data/fp_probe.json`, `data/fp_found.jsonl`, `data/fp_positive_control.jsonl` | the final-polynomial measurement, its hits, and its rigged control |

`data/certs_nonrealizable.jsonl` and
`data/certs_nonrealizable_bfpschema.jsonl` do **not** exist: no OPEN class
produced a non-realizability certificate of any kind. `attack.py` creates
them the moment one does. Certificates of that shape are exercised anyway,
in `data/validation_gordan*.jsonl` and `data/fp_found.jsonl`.

---

## Appendix B — per-class results

Every row: verdict REALIZABLE, decided by weapon A, certificate in
`data/certs_realizable.jsonl`.  `how` is which source produced the
eight-point configuration that completed (see the table in s8).  `s` is
the deciding run's wall time; see the staging note in s8 for why the
column mixes two searchers.  The last column is the exact
no-final-polynomial witness at level L0 (three-term relations only, i.e.
"no biquadratic final polynomial") and at level L1 (plus the four- and
five-term exchange families).

| row | depth | verdict | how | s | max&#124;entry&#124; | no-FP witness (L0 / L1) |
|---|---|---|---|---|---|---|
| 69566 | 17 | REALIZABLE | walk | 16.2 | 256 | yes / yes |
| 69816 | 15 | REALIZABLE | walk | 1.6 | 262144 | yes / yes |
| 161446 | 17 | REALIZABLE | walk | 1.6 | 16384 | yes / yes |
| 274772 | 17 | REALIZABLE | walk | 2.8 | 64 | yes / yes |
| 338300 | 17 | REALIZABLE | walk | 23.3 | 1024 | yes / yes |
| 383472 | 15 | REALIZABLE | walk | 35.2 | 1024 | yes / yes |
| 482339 | 17 | REALIZABLE | fresh | 1.1 | 1024 | yes / yes |
| 560157 | 15 | REALIZABLE | walk | 6.1 | 1024 | yes / yes |
| 586623 | 16 | REALIZABLE | walk | 4.6 | 8192 | yes / yes |
| 595394 | 15 | REALIZABLE | walk | 8.9 | 1024 | yes / yes |
| 710482 | 17 | REALIZABLE | walk | 3.4 | 16384 | yes / yes |
| 711053 | 17 | REALIZABLE | walk | 2.5 | 512 | yes / yes |
| 785797 | 15 | REALIZABLE | walk | 30.5 | 1024 | yes / yes |
| 865559 | 15 | REALIZABLE | walk | 1.9 | 1024 | yes / yes |
| 902448 | 16 | REALIZABLE | walk | 1.1 | 64 | yes / yes |
| 910517 | 17 | REALIZABLE | walk | 1.1 | 1024 | yes / yes |
| 950263 | 15 | REALIZABLE | walk | 3.9 | 16384 | yes / yes |
| 1164918 | 16 | REALIZABLE | walk | 0.9 | 64 | yes / yes |
| 1200032 | 15 | REALIZABLE | walk | 8.7 | 16384 | yes / yes |
| 1213079 | 16 | REALIZABLE | walk | 11.7 | 262144 | yes / yes |
| 1278069 | 15 | REALIZABLE | walk | 14.3 | 16384 | yes / yes |
| 1321961 | 16 | REALIZABLE | store | 0.8 | 64 | yes / yes |
| 1345534 | 17 | REALIZABLE | fresh | 1.0 | 16384 | yes / yes |
| 1407171 | 16 | REALIZABLE | walk | 20.3 | 1024 | yes / yes |
| 1419655 | 17 | REALIZABLE | walk | 4.6 | 16384 | yes / yes |
| 1486611 | 15 | REALIZABLE | walk | 1.0 | 256 | yes / yes |
| 1504477 | 17 | REALIZABLE | walk | 1.2 | 1024 | yes / yes |
| 1510131 | 15 | REALIZABLE | walk | 24.8 | 1024 | yes / yes |
| 1514892 | 16 | REALIZABLE | walk | 4.1 | 1024 | yes / yes |
| 1518293 | 17 | REALIZABLE | walk | 16.5 | 1024 | yes / yes |
| 1684953 | 17 | REALIZABLE | walk | 4.0 | 262144 | yes / yes |
| 1769360 | 16 | REALIZABLE | walk | 21.5 | 1024 | yes / yes |
| 1774140 | 17 | REALIZABLE | walk | 26.2 | 16384 | yes / yes |
| 1862494 | 17 | REALIZABLE | walk | 3.3 | 64 | yes / yes |
| 1865511 | 16 | REALIZABLE | walk | 21.2 | 1024 | yes / yes |
| 1988690 | 17 | REALIZABLE | walk | 15.4 | 1024 | yes / yes |
| 1989477 | 16 | REALIZABLE | walk | 19.7 | 64 | yes / yes |
| 2016110 | 17 | REALIZABLE | walk | 5.6 | 8192 | yes / yes |
| 2126752 | 14 | REALIZABLE | store | 0.6 | 1024 | yes / yes |
| 2218209 | 17 | REALIZABLE | walk | 3.9 | 1024 | yes / yes |
| 2246262 | 14 | REALIZABLE | store_walk | 0.2 | 1024 | yes / yes |
| 2422219 | 17 | REALIZABLE | walk | 37.0 | 1024 | yes / yes |
| 2444483 | 17 | REALIZABLE | walk | 11.0 | 16384 | yes / yes |
| 2472030 | 16 | REALIZABLE | store_walk | 0.4 | 1024 | yes / yes |
| 2540731 | 17 | REALIZABLE | walk | 2.1 | 1024 | yes / yes |
| 2595537 | 17 | REALIZABLE | walk | 9.0 | 1024 | yes / yes |
| 2616175 | 17 | REALIZABLE | walk | 2.2 | 2048 | yes / yes |
| 2635483 | 15 | REALIZABLE | fresh | 0.2 | 512 | yes / yes |
| 2706717 | 17 | REALIZABLE | walk | 3.9 | 16384 | yes / yes |
| 2765699 | 17 | REALIZABLE | store_walk | 1.1 | 131072 | yes / yes |
| 2927497 | 16 | REALIZABLE | walk | 1.4 | 256 | yes / yes |
| 2963994 | 17 | REALIZABLE | walk | 6.7 | 1024 | yes / yes |
| 2972286 | 16 | REALIZABLE | walk | 1.1 | 1024 | yes / yes |
| 3133872 | 16 | REALIZABLE | walk | 45.3 | 16384 | yes / yes |
| 3144919 | 17 | REALIZABLE | walk | 2.5 | 1024 | yes / yes |
| 3193338 | 16 | REALIZABLE | store | 0.2 | 4096 | yes / yes |
| 3202535 | 16 | REALIZABLE | walk | 9.9 | 64 | yes / yes |
| 3258103 | 16 | REALIZABLE | fresh | 1.2 | 64 | yes / yes |
| 3343276 | 17 | REALIZABLE | walk | 2.5 | 256 | yes / yes |
| 3380682 | 16 | REALIZABLE | walk | 15.1 | 1024 | yes / yes |
| 3572151 | 15 | REALIZABLE | walk | 0.8 | 1024 | yes / yes |
| 3674773 | 17 | REALIZABLE | store_walk | 1.5 | 8192 | yes / yes |
| 3718175 | 16 | REALIZABLE | walk | 2.9 | 16384 | yes / yes |
| 3745519 | 15 | REALIZABLE | store | 0.6 | 4096 | yes / yes |
| 3816617 | 17 | REALIZABLE | walk | 20.3 | 1024 | yes / yes |
| 3840632 | 16 | REALIZABLE | walk | 2.7 | 1024 | yes / yes |
| 3842585 | 15 | REALIZABLE | walk | 1.3 | 1024 | yes / yes |
| 3885899 | 16 | REALIZABLE | walk | 1.4 | 1024 | yes / yes |
| 3969889 | 16 | REALIZABLE | walk | 2.0 | 16384 | yes / yes |
| 4005296 | 17 | REALIZABLE | walk | 4.4 | 1024 | yes / yes |
| 4066535 | 16 | REALIZABLE | walk | 9.5 | 1024 | yes / yes |
| 4099514 | 15 | REALIZABLE | store | 0.6 | 4096 | yes / yes |
| 4125921 | 17 | REALIZABLE | walk | 3.4 | 1024 | yes / yes |
| 4164751 | 17 | REALIZABLE | walk | 11.6 | 16384 | yes / yes |
| 4218710 | 17 | REALIZABLE | walk | 3.2 | 1024 | yes / yes |
| 4289821 | 15 | REALIZABLE | walk | 3.9 | 1024 | yes / yes |
| 4290333 | 17 | REALIZABLE | walk | 3.6 | 1024 | yes / yes |
| 4357916 | 16 | REALIZABLE | walk | 1.0 | 1024 | yes / yes |
| 4405516 | 15 | REALIZABLE | walk | 5.2 | 1024 | yes / yes |
| 4487690 | 16 | REALIZABLE | walk | 16.7 | 8192 | yes / yes |
| 4500573 | 15 | REALIZABLE | walk | 2.7 | 1024 | yes / yes |
| 4546369 | 16 | REALIZABLE | store_walk | 0.4 | 16384 | yes / yes |
| 4748789 | 15 | REALIZABLE | store_walk | 0.3 | 4096 | yes / yes |
| 4993531 | 15 | REALIZABLE | walk | 6.4 | 16384 | yes / yes |
| 5062436 | 15 | REALIZABLE | store_walk | 0.6 | 1024 | yes / yes |
| 5100633 | 16 | REALIZABLE | walk | 4.5 | 8192 | yes / yes |
| 5159768 | 16 | REALIZABLE | walk | 1.4 | 1024 | yes / yes |
| 5193545 | 16 | REALIZABLE | walk | 5.0 | 64 | yes / yes |
| 5298491 | 16 | REALIZABLE | walk | 2.8 | 1024 | yes / yes |
| 5514695 | 14 | REALIZABLE | walk | 2.7 | 1024 | yes / yes |
| 5616046 | 16 | REALIZABLE | walk | 28.6 | 131072 | yes / yes |
| 5723047 | 16 | REALIZABLE | store_walk | 1.9 | 16384 | yes / yes |
| 5749535 | 16 | REALIZABLE | walk | 3.4 | 262144 | yes / yes |
| 6080132 | 16 | REALIZABLE | walk | 9.3 | 64 | yes / yes |
| 6169872 | 15 | REALIZABLE | walk | 0.7 | 64 | yes / yes |
| 6312306 | 16 | REALIZABLE | walk | 1.6 | 512 | yes / yes |
| 6457287 | 16 | REALIZABLE | walk | 9.7 | 1024 | yes / yes |
| 6559976 | 16 | REALIZABLE | store_walk | 0.3 | 256 | yes / yes |
| 6695429 | 16 | REALIZABLE | store_walk | 0.5 | 1024 | yes / yes |
| 6795529 | 16 | REALIZABLE | walk | 0.9 | 16384 | yes / yes |
| 6801373 | 16 | REALIZABLE | walk | 5.4 | 16384 | yes / yes |
| 6862284 | 15 | REALIZABLE | walk | 0.7 | 1024 | yes / yes |
| 6883171 | 15 | REALIZABLE | store_walk | 0.5 | 64 | yes / yes |
| 6885585 | 16 | REALIZABLE | walk | 4.0 | 512 | yes / yes |
| 6904353 | 16 | REALIZABLE | walk | 24.0 | 1024 | yes / yes |
| 6928542 | 16 | REALIZABLE | store_walk | 0.5 | 64 | yes / yes |
| 7268803 | 15 | REALIZABLE | store_walk | 0.4 | 262144 | yes / yes |
| 7338078 | 16 | REALIZABLE | walk | 8.9 | 1024 | yes / yes |
| 7783239 | 16 | REALIZABLE | walk | 5.6 | 1024 | yes / yes |
| 7816209 | 16 | REALIZABLE | walk | 34.5 | 64 | yes / yes |
| 7902858 | 16 | REALIZABLE | walk | 3.1 | 1024 | yes / yes |
| 7916819 | 13 | REALIZABLE | walk | 4.5 | 262144 | yes / yes |
| 8067562 | 15 | REALIZABLE | walk | 16.4 | 1024 | yes / yes |
| 8127895 | 16 | REALIZABLE | store_walk | 0.6 | 16384 | yes / yes |
| 8145146 | 16 | REALIZABLE | walk | 11.9 | 1024 | yes / yes |
| 8245156 | 16 | REALIZABLE | walk | 0.6 | 1024 | yes / yes |
| 8301399 | 15 | REALIZABLE | walk | 2.7 | 1024 | yes / yes |
| 8372832 | 15 | REALIZABLE | walk | 3.4 | 1024 | yes / yes |
| 8444963 | 15 | REALIZABLE | walk | 13.5 | 1024 | yes / yes |
| 8453352 | 16 | REALIZABLE | walk | 17.3 | 1024 | yes / yes |
| 8505902 | 16 | REALIZABLE | walk | 3.4 | 1024 | yes / yes |
| 8541456 | 15 | REALIZABLE | walk | 10.1 | 64 | yes / yes |
| 8603583 | 14 | REALIZABLE | walk | 18.0 | 1024 | yes / yes |
| 8698279 | 16 | REALIZABLE | walk | 12.2 | 8192 | yes / yes |
| 8924175 | 16 | REALIZABLE | walk | 17.5 | 16384 | yes / yes |
| 8929110 | 15 | REALIZABLE | walk | 3.6 | 1024 | yes / yes |

## Post-review provenance notes (findings D3, D4, D5, D7 of REVIEW_FABLE.md)

* `data/fp_found.jsonl` is from the earlier 2-hit draw and carries two
  fields (`also_has_L0_gordan_vector`, `L0_gordan_terms`) emitted by the
  fpprobe.py revision of that draw; `data/fp_probe.json` records the later
  3-hit run. Two draws, one shipped file each — not a single replayable run.
* One positive-control canary record labels a pl5-family relation
  `level: L0`; both checkers ignore the field, so it is cosmetic.
* §7.1a's six-class inequality-system comparison shipped no artifact; the
  adversarial review re-ran the comparison on all 126 classes and confirmed
  the documented ranges (REVIEW_FABLE.md, area 3).
* Pass-1 rows of `data/results.jsonl` were produced by an earlier attack.py
  revision (witness stages backfilled by later passes); the shipped code
  reproduces the verdicts but is not a byte-level replay of pass-1 rows.

## Post-review measurement: how far can the float LP be trusted?

Two studies, and they disagree in a way worth recording rather than
averaging.

**Study 1 (`review_scratch3/gapstudy.py`, built by GPT-5.6).** Inflates the
shipped realizations by random unimodular transforms (det = +1 preserves
every bracket sign, so feasibility is unchanged) and bins by max |entry|.
Result: 0/72 false negatives on the shipped configurations, 0/72 at the
`_shrink` cap of 2^22, first failures in the 2^30 band (29%), rising to
87.5% by 2^50. Its conclusion was that the 47,723 reported infeasible LP
calls are reliable at the magnitudes this repo actually uses.

**Study 2 (`review_scratch3/spotcheck_gap.py`, written here as an
independent check).** Same idea, but the transforms are *compounding shears*
(multiplier 3, cycled through four coordinate pairs) — det = +1, so again
feasibility is provably unchanged, but the configurations become
progressively ill-conditioned. Result (`spotcheck_gap.log`): float agrees
9/9 on the untransformed data, then **starts losing real completions at max
|entry| ≈ 2^15.5**, and by 2^16–2^22 is finding only 2–6 of 9 — while the
exact oracle returns FEASIBLE 9/9 throughout. **That failure onset is below
the repo's own 2^22 cap.**

**Reconciliation, and the honest conclusion.** Magnitude is not the
governing variable; conditioning is. Note the arithmetic: the LP rows are
3×3 minors, i.e. *cubic* in the configuration entries, so the 2^22 cap
already implies row entries up to ~2^66 — far past the 2^53 where float64
is exact. The method survives on real data not because the numbers are
small but because search-produced configurations happen to be
well-conditioned. Therefore:

* the 47,723 infeasible calls are **supported on the tested population and
  unsupported in general** — they are evidence, not certificates;
* no claim in this document depends on them (every one of the 126 verdicts
  came from an exactly-verified *success*);
* **policy for future runs**: before a class is reported STILL_OPEN, the
  deciding infeasibility must be re-confirmed by `exactlp.exact_feasible`,
  which returns a Gordan certificate. Magnitude thresholds must not be used
  as a proxy for numerical safety.
