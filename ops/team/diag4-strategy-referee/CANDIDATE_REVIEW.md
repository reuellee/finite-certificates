# Diagonal-four frozen-candidate review

Date: 2026-08-29 UTC

Track: `diag4-strategy-referee`

Canonical mathematical base:
`d047359e7892106021022b0401554f56eb4e4d8a`

Corrected local control plane:
`ec9a8ddba6f90e5cc96427337d0ad20ef28b8641`, tree
`c7b20b7b85f72f1e5ab0315121fb30073f566e09`

Connector-published corrected control-plane head, as supplied by the
coordinator: `084330a0ea3b53b5e6d001b31ae83932d223620b`.

Opening referee revision:
`a112391eab4311a67a88e6aa9447f658226c65bc`.

## Disposition

- **Prover: ACCEPT WITH SCOPE WORDING.**  The B31 three-plus-one four-shear
  theorem is mathematically valid, and an independent implementation
  reconstructs the complete `915,740 / 77` certified and `800,240 / 53`
  surviving support-shape split.  The result is a positive universal
  intermediate theorem, not D4-SP and not diagonal four.
- **Falsifier: MODIFY SCOPE WORDING, then accept as a useful null.**  The
  signed two-event matrix exhaustion and actual row-2599 calculations are
  exact.  Its claimed complete abstract class must explicitly be restricted
  to a component diagram over a base line with two exterior rays.  Without
  that clause, “connected one-dimensional component diagram” also includes a
  circular base, for which a zero-event cycle contradicts the stated
  minimality.
- **Ledger: no change.**  D4-SP, the remaining total-complex terms,
  restriction exactness, and diagonal four all remain open; the score remains
  `2/9`.
- **Post-cycle strategy: CONTINUE.**  One bounded signed/topological cycle on
  the 53 B31-resistant support-shape orbits is justified because this cycle
  strictly reduced a complete declared D4-SP subdomain.  If the complete
  survivor class is unchanged next cycle, the protocol requires a pivot.

The machine-readable dispositions are in `CANDIDATE_GATE_TABLE.yaml`.

## Frozen identities and publication provenance

### Prover

- local frozen revision:
  `e7baf36f6bb18a4552a9a337d8373e7aa7a87355`;
- local frozen tree: `f85f17fdd390fc3803f1625a83bd2fb68e6f2045`;
- connector-published byte-identical artifact head supplied by the
  coordinator: `d776ff9163c9f27194bfbeca38114434222b64be`.

### Falsifier

- local frozen revision:
  `7dc8a2bfae9672068b6c977302d2ea5b213c412b`;
- local frozen tree: `b1a5b61d1a851440114d1a6b2a1576270f17fdeb`;
- connector-published head supplied by the coordinator:
  `4a3fc3d4bc21eecd1ecabed47d79b2b853069025`.

The published connector commits are not present in the local object database,
so this review authenticates the immutable local trees and the file SHA-256
values below.  The coordinator must require byte equality at integration and
run protected checks at the exact final head.

Both frozen worktrees were clean before and after replay.  No candidate file
was changed by the referee.

## Corrected control-plane gate

The coordinator incorporated every opening `MODIFY` item:

- all eight strategy factors are scored;
- D4-SP is a fixed proposition over all `1,715,980` cover-all supports;
- the complete versus generic support censuses are separated;
- the obligation graph includes the independent two-, three-, four-, and
  five-piece/restriction obligations;
- canonical input and ledger digests and cycle concurrency are recorded; and
- D4-SP is explicitly barred from ledger promotion by itself.

The independent control-plane replay passed:

```console
PYTHONDONTWRITEBYTECODE=1 python \
  ops/research-team/verify_cycle_protocol.py
```

It reports one cycle and three work orders carrying the explicit publication
authorization.

## Prover audit

### Accepted theorem

For a support union `U`, B31 supplies moving labels `e1,e2,e3,g` and distinct
fixed apices `f,h`, with the first three labels dominated by `f` and `g`
dominated by `h`.  The claimed theorem is

\[
 H_c^q\left(\bigcap_j C_{\rho_j,Q_j};\mathbb Q\right)=0
 \quad(0\leq q\leq3)
\]

whenever the union of the supports satisfies B31.

This theorem is accepted for the following reasons.

#### Signed normal invariance

The four motions are

\[
y_{e_i}\mapsto y_{e_i}+t_i y_f,\qquad
y_g\mapsto y_g+u y_h.
\]

Every support triple containing `e_i` also contains `f`, and every support
triple containing `g` also contains `h`.  A support triple cannot contain
both an `e_i` and `g`, because it would then have to contain the four
distinct labels `e_i,g,f,h`.  Alternating multilinearity therefore makes
every involved third exterior product invariant.  This is an exact signed
statement: multiplying by a fixed signature sign does not alter it.
Nonnegative Gordan weights persist, and zero weights remain zero.  The proof
therefore covers closed weight faces as well as strict circuit strata.

#### Projective quotient and stabilizer

There are exactly four nonmoving rays.  Uniformity makes them a basis and
makes every coordinate of every other ray in this basis nonzero.  After
fixing these rays, the residual projective stabilizer is diagonal.

Preservation of a line through `f` and a uniform moving ray forces the three
non-`f` diagonal scales to agree.  Preservation of the line through the
distinct apex `h` and `g` forces the remaining scale to agree with them.
Thus the base object's stabilizer is scalar and trivial in PGL.  The four
apex coordinates are genuine fiber coordinates; no projective gauge
direction has been counted as topology.

The integrated theorem statement should include this fixed-basis argument.
The candidate proof contains it in compressed form, and no mathematical
repair is needed.

#### Fiber topology

At fixed `u`, each parent determinant is affine jointly in
`(t1,t2,t3)`.  Terms containing two of those variables repeat `y_f` and
vanish.  Terms involving one `t_i` and `u` merely change the affine
coefficient after `u` is fixed.  Hence every fixed-`u` section of the
parent-safe fiber is empty or open convex.

For one connected component `Omega0`, projection to `u` is an open interval
`J`.  A nonempty convex section cannot meet two components, so the section
of `Omega0` is the whole convex slice.  Openness gives local persistent
points; a partition of unity on `J` gives a continuous selection.  Fiberwise
straight-line contraction retracts `Omega0` to the graph of that selection,
and hence to `J`.  Every fiber component is therefore contractible.

Each component is an open subset of `R^4` and is oriented.  Poincare duality
gives zero compact-support cohomology below degree four.  Even if the top
orientation system twists over the quotient base, every `R^j pi_! Q` stalk
for `j<=3` is zero.  Compact-support Leray therefore has no term of total
degree at most three.  A global trivialization of `R^4 pi_! Q` is neither
used nor claimed.

#### Structural and residual strata

The proof uses parent uniformity and exterior-product identities, not
genericity or a fixed residual sign chamber.  All parent-safe points on a
fiber retain the selected signed circuit equations.  Residual derived walls
and support drops are included; parent nonuniformity remains an end of the
open realization cell, as compact supports require.

### Accepted complete support-shape sieve

The producer replay passed:

```console
PYTHONDONTWRITEBYTECODE=1 python \
  ops/team/diag4-top-sheaf-prover/verify_four_block_line_sieve.py
```

The referee also implemented B31 independently, enumerated every cover-all
three-, four-, and five-subset of the 56 triples, and reconstructed the full
`S_8` orbit partition without importing the producer.  Both calculations
give:

| Size | Complete labeled | Complete orbits | B31 labeled | B31 orbits | Survivors | Survivor orbits |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 3 | 840 | 1 | 840 | 1 | 0 | 0 |
| 4 | 72,380 | 14 | 53,060 | 10 | 19,320 | 4 |
| 5 | 1,642,760 | 115 | 861,840 | 66 | 780,920 | 49 |
| **total** | **1,715,980** | **130** | **915,740** | **77** | **800,240** | **53** |

The unsigned enumeration is legitimately connected to the signed universal
theorem: B31 is a support-level sufficient condition, while the proof itself
shows that all signed equations are invariant.  The enumeration does not
claim that every support occurs, and no occurrence assumption is needed to
prove a universal implication for any occurrence that does exist.

### Canary qualification

The candidate's B31 positive support uses signature index `7`, while its own
16-pattern admissibility loop uses indices `0,4,3,5`.  That internal loop
alone does not place signature `7` in the displayed four-family.  This is not
a theorem defect: the canonical independent replay

```console
PYTHONDONTWRITEBYTECODE=1 python ai/omreal/verify_seeat_shatter8.py
```

checks all 256 patterns on all eight signatures.  It therefore proves that
the index-7 B31 circuit belongs to many proper pairwise-incomparable
four-families.  The integrated prose must cite the full-shatter replay for
this canary.

### Prover nonconsequences

The prover correctly does not claim any of the following:

- D4-SP on the 53 survivors;
- nonzero cohomology for a survivor;
- a Cech restriction map or fivefold middle-rank result;
- diagonal-four vanishing; or
- a change from `2/9`.

All four prover files are integrable at their reviewed SHA-256 values, subject
to byte equality on the coordinator branch and the final exact-head checks.

## Falsifier audit

### Accepted signed two-event kernel

For the event word `1 -> 2 -> 1`, the two middle branches give a signed
two-by-two boundary matrix.  Exact exhaustion of all 16 sign assignments
gives eight rank-one matrices and eight rank-two matrices.  Row and column
generator changes partition them into two gauge classes.  The product of the
four attachments is the sole holonomy bit and detects the one-dimensional
kernel.  Flipping one sign swaps classes and kills the kernel.

This calculation is exact and independently evident from

\[
 \det D=l_0r_1-l_1r_0.
\]

For signs in `{+1,-1}`, the determinant is zero exactly when
`l0*r1*l1*r0=+1`.

### Required abstract-domain correction

The asserted minimality is complete only over a **base line with two exterior
rays**, connected exterior fibers, no births/deaths, generic split/merge
events, at most two simultaneous branches, and at most two events.  Under
those hypotheses, zero and one event give trees and `1 -> 2 -> 1` is the sole
cyclic word.

“Connected one-dimensional component diagram” without the base-line clause
is too broad: a circular base with one persistent component is already a
zero-event cycle.  Before publication, the coordinator must add the base-line
clause to the abstract search schema and every completeness sentence in
`MINIMAL_SIGNED_MODELS.json`, `RESULT.yaml`, and `FINDINGS.md`, then refresh
affected digests.  This is a scope correction, not a change to the 16-matrix
calculation.  A signed delta rereview is required; the expensive mathematical
replays need not change if the verifier locks the corrected field.

### Accepted actual signed control and four-parameter candidate

The falsifier replay and the canonical full-shatter replay verify that
signature indices `0,4,5,6` are proper and pairwise incomparable and have
positive minimal cover-all circuits at pattern zero.

For signature index `0` and
`Q=123/134/267/258/468`, an independent multilinear determinant
reconstruction verifies that

\[
y_5\mapsto y_5+s y_2+t y_8,\qquad
y_1\mapsto y_1+u y_3,\qquad
y_7\mapsto y_7+v y_2
\]

fixes all five support normals.  Independent Boolean-cube interpolation of
the 70 parent determinants gives exactly 48 nonconstant inequalities, 16
nonlinear inequalities, and maximum total degree three.  This reconstruction
does not import the producer's polynomial arithmetic.

The candidate is actual signed rank-four data but only a four-parameter
subset of one closed circuit piece.  Its compact-support topology is
uncomputed.  Even nonzero cohomology on the subset would not refute D4-SP
unless the class survives inclusion into the full closed piece.  The
falsifier states both limitations correctly.

### Falsifier disposition

The null result is useful after the abstract-domain wording correction.  It
does not remove a D4-SP support subdomain and does not supply a counterexample.
Its row-2599 family is an appropriate adversarial discriminator for the next
cycle, but a local acyclicity result would remain only a bounded null.

## Artifact and replay accounting

### Prover artifacts

| Path | SHA-256 |
| --- | --- |
| `MANIFEST.sha256` | `125c9b65b441b14360bc4c2b2b0a668d91420f43c151341cbc3e7baef3bd3942` |
| `PROOF.md` | `339f8026415c56c3acd7bea7340284f32a739da9f9c15955779e7fb1c817a448` |
| `RESULT.yaml` | `9dec592379ff05e8210236e2db4d7a56c7808c9154fee8e5a2491ff466e3e7df` |
| `verify_four_block_line_sieve.py` | `84a717a3df6ca9eabbee3d3645ecb5ffbb78932b34cb54969b97fab9d4015e48` |

`sha256sum -c MANIFEST.sha256` passes.

### Falsifier artifacts

| Path | SHA-256 |
| --- | --- |
| `WORK_ORDER.yaml` | `06d0278b5463b4946c41914ac0b19537b3e6bfc56375241402488ecb38b018fa` |
| `MINIMAL_SIGNED_MODELS.json` | `80fa2a80557502e0f0015135045d2135f5cd4b8153f872f96bd989bb8fee368f` |
| `RESULT.yaml` | `2f24edc2fed51f9ef8a6b03c8350548a1b124ded7d9a7a21cd01309a11399ad0` |
| `FINDINGS.md` | `dce84765aea0d59a677f3c52bfdf2f318fd98785ef3fac0436f5c76604fb76c1` |
| `verify_diag4_top_sheaf_falsifier.py` | `e9bcc7651938a2aa71e2f400d3e76639ee074a9cd8f6c1dac706e951d0c87a19` |

The shared shatter input is
`d01a03e3222de5b760fd7fec36c03ccbeac820ed1ce7ea47f93001abaf3aadcb`.

Both candidate replay commands exit zero.  Repository and CI status at the
future integrated head remain coordinator-owned pending gates.

## Mandatory post-cycle strategy evaluation

### Exact delta

- Ledger: `2/9 -> 2/9`; no theorem entry changes.
- `diag4_cover_all_single_piece_hc3`: narrowed from `1,715,980` supports in
  130 support-shape orbits to `800,240` supports in 53 B31-resistant orbits.
- D4-SP: open.
- Pair `(1,2)`, triple `(2,1)`, fourfold `(3,0)`, adjacent-degree,
  compactification, restriction-map, and total-complex obligations: open.
- The B31 theorem is stated for intersections as well as single pieces, but
  this cycle enumerates only the complete single-piece support domain.  No
  multi-piece coverage consequence is inferred.

### End-to-end burden

This is genuine structural progress, not an additional sample.  One signed
universal theorem removes every D4-SP case whose support shape has B31 and
cuts the complete single-piece orbit class by `77/130`.  It does not yet
close a ledger-level obligation, and the remaining lower Cech rows prevent a
direct diagonal-four consequence.

The falsifier invalidates two shortcuts inside its declared class:
branchwise escape without signed attachment data, and unsigned component
incidence without orientation holonomy.  It does not invalidate D4-SP or the
diagonal-four strategy.

### Updated route comparison

Scores use the same convention as the opening review: `5` is favorable except
for coverage burden and stagnation risk, where `5` is unfavorable.

| Candidate | Ledger leverage | Quantifier readiness | Coverage burden | Terminality | Structural compression | Independent verification | Resource / information | Stagnation risk | Verdict |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| diagonal 3 | 5 | 3 | 5 | 2 | 3 | 3 | 2 | 5 | `PIVOT` |
| diagonal 4 | 5 | 3 | 4 | 4 | 5 | 4 | 4 | 1 | **`CONTINUE`** |
| diagonal 8 | 5 | 1 | 5 | 2 | 3 | 4 | 2 | 4 | `RETIRE` as primary |
| diagonal 9 | 5 | 2 | 5 | 2 | 4 | 3 | 2 | 3 | `PIVOT` |

### Closing verdict

**CONTINUE diagonal four for one bounded successor cycle.**  The protocol's
mandatory-pivot condition is not triggered because the complete declared
D4-SP support-shape class was strictly reduced.  The next target must be the
remaining 53-orbit class itself, not another unsigned light-label census or a
local topology sample presented as global progress.

A suitable claim lock is:

> Prove a universal signed holonomy/top-sheaf exclusion for every admissible
> occurrence of the 53 B31-resistant support shapes, or produce one exact
> admissible D4-SP counterexample with a nonzero class on the entire closed
> circuit piece.

The row-2599 four-parameter domain is a falsifier canary.  A nonzero class
must pass the inclusion gate into the entire closed piece; an acyclic result
is a useful bounded null only.  If the next cycle neither proves/refutes
D4-SP nor strictly shrinks the complete 53-orbit survivor class, the following
cycle must pivot away from this single-piece route.

## Final publication gate

The prover files may be integrated at the reviewed hashes.  The falsifier
files require the base-line scope correction and refreshed digests before
publication.  The coordinator must then provide the exact integrated head
for a short signed-delta review and run all protected repository checks at
that head.  No merge or ledger change is accepted by this review itself.
