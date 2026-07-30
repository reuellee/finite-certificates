# Stage 2c-2: labeled equal-pair ground truth and GP-carried hard certificates

Date: 2026-07-31

## Headline results

This stage uses one realization and one labeling throughout: `U_ints`,
the pair order, the 22 chambers, and the 33,140 valid labeled side
assignments are read from
`../stage2b_gpt/reference_structure.json`.  The historically hard-coded
realization in the Stage 2c-1 verifier is not used.

Three exact results were obtained.

1. **The true labeled equal-pair partition is complete.**  Over all
   33,140 labeled sigmas and both \(k=1,2\), allowing every
   antipodal-symmetric class with equal side multipliers plus all five
   weight rows gives:

   | status | \(k=1\) | \(k=2\) | total |
   |---|---:|---:|---:|
   | T-INDEPENDENTLY-COVERED | 28,106 | 23,324 | **51,430** |
   | HARD | 5,034 | 9,816 | **14,850** |

   Every covered labeled system has an exact primitive-integer Gordan
   vector.  Every hard labeled system has an exact strict-primal witness
   proving that no equal-pair certificate exists.  This replaces the
   Stage 2b-1 representative-only accounting.

2. **The coefficientwise-positive, no-GP mechanism has a sharp
   all-degree boundary.**  An ordinary-polynomial equal-pair certificate
   with coefficientwise-nonnegative side multipliers and weight slacks
   exists if and only if some equal-sign class \((i,j)\), with common sign
   \(q_{ij}\), satisfies

   \[
       q_{ij}s_t=-1\qquad\text{for all }t\notin\{i,j\}.
   \]

   This is exactly the Stage 2c-1 single-class criterion.  It covers
   24,691 systems at \(k=1\), 8,746 at \(k=2\), hence **33,437 total**.
   Multi-class coefficientwise-positive polynomials of arbitrary degree
   extend it by **zero** systems.

3. **The hard-region GP hunt succeeds broadly.**  A full quotient-ring
   cone was solved with side multiplier degree \(d\), independent
   coefficientwise-positive weight-row multipliers of degree \(d+1\), and
   all eight equations imposed modulo the signed three-term Pluecker
   ideal.  The research set contains the first ten canonical HARD
   representatives at each split and all 100 mapped failed Stage 2b
   targets, with no duplicates: 120 systems total.

   | side degree | exact certificates | exact degree no-gos |
   |---:|---:|---:|
   | 0 | 0 | 120 |
   | 1 | 64 | 56 |
   | 2 | **120** | 0 |
   | 3 | **120** | 0 |

   Thus all 120 targets, including all failed-100 systems, have exact
   cell-wide certificates already at degree at most two.  The degree-three
   search also succeeds on all of them, as expected after multiplying a
   lower-degree certificate by a positive determinant monomial.

These results do **not** yet claim coverage of all 66,280 systems by the
GP mechanism.  The proven cell-wide union in this stage is the 33,437
single-class systems plus the explicitly searched GP targets (with any
overlap accounted per target).  A full 32,843-system complement sweep was
started only as an optional scale-out; it is not part of the theorem ledger
unless complete shard artifacts are present and checked.

## 1. Exact labeled equal-pair coverage

For an equal-sign class \(e=(i,j)\), let its common sigma sign be \(q_e\).
Equal multipliers on its two sides cancel all three \(T\)-columns
identically.  The reduced weight row is

\[
  R_e(t)=
  \begin{cases}
    2q_es_tD_{tij},&t\notin\{i,j\},\\
    0,&t\in\{i,j\}.
  \end{cases}
\]

Together with the five positive coordinate rows, this is a five-column
Gordan system.  `sweep_equal_pair.py` classifies every distinct reduced
pattern using HiGHS only for a support or primal-point hint.  A terminal
covered result is repaired over `Fraction`, cleared to primitive positive
integers, lifted to the full 25-row system, and checked exactly.  A terminal
hard result is an exact rational \(w\) with every reduced row dot \(w\)
strictly positive.

The artifact is stored pattern-deduplicated but its `systems` array contains
all 66,280 labeled systems in `sigma_bits`-ascending, then \(k=1,2\),
order.  The standalone checker reconstructs and checks every lifted
certificate or witness separately.  This preserves labeled granularity
while avoiding duplicate serialization.

The global-flip accounting difference is real:

| split | covered canonical representatives | covered flip partners | labeled covered |
|---:|---:|---:|---:|
| \(k=1\) | 13,506 | 14,600 | 28,106 |
| \(k=2\) | 10,348 | 12,976 | 23,324 |

The two deliberate canonical-residue canaries were searched first:

- `(sigma_bits=10070, k=1)`;
- `(sigma_bits=25998, k=2)`.

Both returned exact strict-primal witnesses and remained HARD.  A false
dual success would have aborted artifact generation.

## 2. Boundary theorem for ordinary coefficientwise positivity

### Sufficiency

If class \(e=(i,j)\) satisfies the displayed criterion, set both side
multipliers to one.  The \(T\)-columns cancel, and for each complementary
vertex use the positive monomial weight multiplier

\[
    z_t=-2q_es_tD_{tij}=2D_{tij}.
\]

This is the normalized single-class family.

### Necessity at every degree

For every one of the remaining 32,843 labeled systems,
`coefficientwise_boundary.py` stores an exact positive assignment
\(d=(d_{012},\ldots,d_{234})\) to the ten *formal independent* determinant
variables such that, at \(w=(1,1,1,1,1)\),

\[
    q_e\sum_{t\notin e}s_t d_{tij}>0
\]

for every eligible equal-sign class \(e\).

Suppose an ordinary-polynomial certificate with coefficientwise
nonnegative multipliers existed in any degree.  Evaluating its polynomial
identity at this positive formal \(d\) would preserve nonnegativity and
produce a numeric Gordan vector for the strictly feasible reduced system,
a contradiction.  The formal point need not satisfy Pluecker relations:
the mechanism being bounded here is precisely the one whose identities
hold without GP reduction.

This proves necessity, not merely a degree cutoff.  As a finite-cone
cross-check, `coefficientwise_search.py` exhaustively solved homogeneous
degrees zero and one with exact positive vectors or exact separating
functionals.  Degree zero gives 33,437 labeled systems and degree one gives
the identical 33,437: no extension.

Of the 51,430 systems numerically equal-pair-covered at `U_ints`, 17,993
are outside this ordinary coefficientwise family.  Their fixed-realization
certificates depend on determinant ratios; the boundary theorem says they
cannot be promoted by coefficientwise-positive ordinary identities alone.

## 3. T-carrying quotient-ring certificates

Let side multiplier polynomials be homogeneous of degree \(d\) in the ten
positive \(D_{ijk}\), and weight-row multipliers have degree \(d+1\).
All coefficients are constrained nonnegative.  The signed-D Pluecker ideal
is derived from the reference chirotope by substituting
\(p_{ijk}=\chi_{ijk}D_{ijk}\) into the five three-term relations.  Every
coefficient column is reduced by one exact Gröbner basis, and a
nonnegative kernel vector is sought.

The key difference from the failed Stage 2c-1 degree-\(\le2\) attempt is
that the five weight multipliers are independent unknown positive
polynomials and their equations are solved modulo the Pluecker ideal too.
They are not forced to be the coefficientwise ordinary negative of a side
sum.  This is the missing GP-carried freedom.

One compact example is the canonical hard system
`sigma_bits=10070, k=1`.  A degree-one certificate has positive support

```text
side (0,3,+): D234
side (2,3,+): D034
side (3,4,-): D023
weight row w0: 2*D023*D034
```

The three side normals share generator 3 and cancel through their
three-term dependence; the remaining weight equation is GP-carried.
The checker reduces all eight symbolic equations to zero and independently
specializes the multipliers at `U_ints`, where their exact dot product with
the full 25-by-8 integer matrix is zero.

The searched research-set composition is:

- 20 canonical objective-1 HARD systems, ten per split;
- all 100 mapped failed Stage 2b targets;
- among the 32 prefix-\(k=2\) failed targets, 15 are objective-1 HARD and
  17 are fixed-realization equal-pair-covered;
- the other 68 failed targets carry the mapped \(k=3\) split and are kept
  exactly in that labeling.

The strict-feasible negative canary is the deliberately invalid assignment
`sigma_bits=0, k=1`.  Its exact full-system primal witness is

```text
(T0,T1,T2,w0,w1,w2,w3,w4)
= (0,0,0,1,1619/440,447/88,1201/440,1),
```

with minimum margin one.  It is rejected with an exact separating
functional in every degree.  A known single-class positive control is
accepted in every degree.  These controls run before the research targets.

Every accepted research certificate is a primitive positive integer vector
in the quotient coefficient matrix.  Every degree-zero no-go and every
degree-one failure has an exact rational/integer separating functional,
so those negative counts are exact within the stated ansatz rather than
floating LP statuses.

## Proven / conjectured / failed ledger

### Proven

- One self-consistent reference configuration, pair order, chirotope, sigma
  set, and split convention throughout.
- Exact labeled equal-pair partition:
  51,430 T-INDEPENDENTLY-COVERED and 14,850 HARD.
- Exact dual certificate or strict primal no-go for every one of the 66,280
  labeled systems.
- All-degree boundary of the coefficientwise-positive ordinary-polynomial
  equal-pair mechanism: exactly 33,437 systems, with the clean single-class
  criterion above.
- Exact degree-zero and degree-one finite-cone enumeration, with no
  degree-one extension.
- Exact GP-ideal outcomes on 120 research targets: 64 degree-one successes,
  120 degree-two successes, and 120 degree-three successes.
- All 100 formerly failed mapped targets are now cell-wide certified at
  degree at most two.
- Mandatory negative and positive controls pass; all accepted certificates
  also pass exact specialization to the reference integer matrix.

### Conjectured / open

- Degree-two GP certificates may cover the entire 32,843-system complement
  of the single-class family.  The 120/120 result is strong evidence, not
  an exhaustive claim.
- Consequently, the global theorem
  \(\max f_0(3,5)=42\) remains open in this stage's formal ledger.  To close
  it by this route, the GP family must be exhaustively covered over all
  labeled systems (or replaced by an equivariant combinatorial theorem),
  then transported across the unique uniform oriented-matroid orbit with
  all label/reorientation actions explicit.

### Failed / superseded

- Representative-only equal-pair counts are superseded by the labeled map.
- Multi-class coefficientwise-positive ordinary polynomials cannot extend
  the single-class family in any degree.
- The prior expectation that the hard region likely requires degree at
  least three is false for the broader quotient-ring ansatz: every searched
  target succeeds by degree two, and 64 already succeed at degree one.
- The optional parallel full-complement scale-out is not a result unless
  complete shard artifacts exist and pass the checker.

## Artifacts

- `equal_pair_coverage.json.gz` — complete labeled partition, pattern
  certificates, strict-primal witnesses, and canary ledger.
- `coefficientwise_mechanisms.json.gz` — exact degree-zero/one cone
  enumeration with separating functionals.
- `coefficientwise_boundary.json.gz` — exact all-degree boundary witnesses.
- `gp_degree3_results.json.gz` — all target outcomes for degrees zero
  through three, controls, certificates, and exact no-gos.
- `common.py` — conventions derived from `reference_structure.json`.
- `sweep_equal_pair.py`, `coefficientwise_search.py`,
  `coefficientwise_boundary.py`, `gp_degree3_search.py` — generators.
- `check_stage2c2.py` — standalone exact checker for every load-bearing
  artifact and every accepted target certificate.

No file in this directory is named `verify_*.py`.

## Reproduction

From the repository root:

```powershell
$PY = 'E:/Projects/sae-identifiability/.venv/Scripts/python.exe'

& $PY ai/maxout/stage2c2_gpt/sweep_equal_pair.py
& $PY ai/maxout/stage2c2_gpt/coefficientwise_search.py --max-degree 1
& $PY ai/maxout/stage2c2_gpt/coefficientwise_boundary.py
& $PY ai/maxout/stage2c2_gpt/gp_degree3_search.py --degrees 0,1,2,3
& $PY ai/maxout/stage2c2_gpt/check_stage2c2.py
```

Recorded full-run times on the development host were approximately 88 s,
197 s, 21 s, 59 s, and 84 s respectively before the expanded
coefficient-cone checks were added to the final checker.  HiGHS is used
only for discovery/support hints.  All serialized positive kernels,
strict-primal witnesses, separating functionals, quotient identities, and
reference specializations are checked in exact integer or `Fraction`
arithmetic.
