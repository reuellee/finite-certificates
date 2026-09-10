# Nine-Diagonal Vanishing Lemma: theorem prospectus

## Status and purpose

This is a research prospectus, not a theorem announcement. The exact ledger is
still **2/9**: diagonals 1 and 2 are proved, while diagonals 3 through 9 remain
open. The two post-V10 cycles also closed `NULL / STALLED / STOP / NONE`:
component-decorated saturation lacked materialized component witnesses and an
end-to-end ceiling-bound Q1 path, while the universal mixed-`(1,0,0)` gate
lacked the geometric-carrier and relative-boundary-surjectivity input needed
to turn its formal cone into a theorem object. Current authority is
[`ai/omreal/data/CANONICAL_RESEARCH_STATE_V11.json`](data/CANONICAL_RESEARCH_STATE_V11.json).
See also
[`ai/omreal/data/CANONICAL_RESEARCH_STATE_V10.json`](data/CANONICAL_RESEARCH_STATE_V10.json),
[`ai/omreal/data/CANONICAL_RESEARCH_STATE_V9.json`](data/CANONICAL_RESEARCH_STATE_V9.json),
[`ai/omreal/ATLAS_HELLY.md`](ATLAS_HELLY.md),
[`ai/omreal/data/CANONICAL_RESEARCH_STATE_V8.json`](data/CANONICAL_RESEARCH_STATE_V8.json),
and the
[`accepted feasibility report`](../../ops/research-team/cycles/2026-09-01-d3-mixed-carrier-theorem-feasibility-gate1/CYCLE_REPORT.md).

## Post-cycle disposition

V8's one-round authorization is consumed. V9 selects no active research target.
Historical V9 and V10 authorize no automatic reopening. V11 records the two
additional null closes and likewise selects no successor. Work is scoped to
9DVL, but a new theorem cycle still requires explicit authority for its
named target, a genuinely new theorem-capable input, a concrete finite route
for one first missing global edge, a predeclared theorem-level strict decrease,
and a fresh independent audit. The target definitions below remain
mathematical possibilities until such an opening passes.

The historically proposed next bet was a theorem about globally attached,
genuinely mixed-block `(1,0,0)` carriers for diagonal three. The attraction is
structural: one successful theorem could replace extensive case-by-case
topology by a finite, face-natural construction. The danger is equally clear:
the repository currently proves only a local two-skeleton and contains an
exact obstruction to every filler that stays inside one bad block at a time.

## The statement and the ledger

Let `M` be a realizable uniform rank-four oriented matroid on eight elements.
For a set `S` of `s` pairwise incomparable proper extension signatures, let
`F_S` denote their common proper-feasibility locus in the normalized
nine-dimensional realization space. The Nine-Diagonal Vanishing Lemma
(`9DVL`) is the family of assertions

\[
   \widetilde H_{9-s}(F_S;\mathbb Q)=0,
   \qquad 1\le s\le 9.
\]

Equivalently, if `B_S` is the union of the corresponding bad loci, then

\[
   \widetilde H_{9-s}(F_S;\mathbb Q)
   \cong H_c^{s-1}(B_S;\mathbb Q).
\]

The quantifier is over every realizable parent and every such internal
antichain of proper regions, not merely minimal signatures or sampled charts.
The precise reduction and its relation to the 8--9--10 Extension--Helly
conjecture are in [`ai/omreal/ATLAS_HELLY.md`](ATLAS_HELLY.md).

The exact state relevant to diagonal three is:

| Item | Exact result | Scope limitation |
| --- | --- | --- |
| Diagonals 1 and 2 | Proved integrally | Gives no automatic higher-diagonal vanishing |
| One bad block | `H_c^q(B_\rho;R)=0` for `0<=q<=2` and every coefficient ring `R` | Does not settle pair or triple intersections |
| Triple source accounting | `77,940,147 / 79,102,449` unordered `S_8` factor-triple source orbits settled; `1,162,302` remain | These are not signature triples, connected components, or dimensions of `H_c^0`; a finite triple denominator is not an end-to-end D3 denominator |
| Pair branch | Global residual and coverage are still literally `UNKNOWN` | Local roadmaps and cell inventories do not provide a global relative complex |
| Joined low skeleton | Universal credit only for types `(0)`, `(1)`, `(2)` | `3/10` is a face-type count, not theorem progress or global coverage |

The single-block theorem is
[`ai/omreal/DIAG3_SINGLE_BAD_TWO_SKELETON.md`](DIAG3_SINGLE_BAD_TWO_SKELETON.md).
The exact triple accounting is pinned in
[`ai/omreal/data/DIAG3_RESEARCH_DECISION_LEDGER.json`](data/DIAG3_RESEARCH_DECISION_LEDGER.json)
and independently reconstructed in the
[`theorem-reset verification`](../../ops/team/theorem-reset-independent-verifier/FINDINGS.md).

## The exact diagonal-three split

For three bad loci `B_0,B_1,B_2`, the proved first- and second-diagonal
vanishings and the single-bad two-skeleton reduce diagonal three to two
independent obligations:

\[
 H_c^0(B_0\cap B_1\cap B_2;R)=0,
\]

and

\[
 \ker\!\left[
   \bigoplus_{i<j}H_c^1(B_i\cap B_j;R)
   \longrightarrow H_c^1(B_0\cap B_1\cap B_2;R)
 \right]=0.
\]

The first says that every triple-bad component must escape to genuine
relative infinity. The second is a global pair-to-triple incidence statement;
proving each pair term zero is sufficient but stronger than necessary. The
derivation is given in
[`ai/omreal/DIAG3_JOINED_FLOW_TRIANGLE.md`](DIAG3_JOINED_FLOW_TRIANGLE.md).
Below these become Target C and Target B, respectively; neither may be counted
as closing the other.

Thus diagonal three cannot be promoted by closing only the `1,162,302`-row
triple residue. It also cannot be promoted by a graph-only model of pair
components. A theorem-grade proof object must retain global gluing, extension
labels, strict closure, genuine parent infinity, and the middle-rank replay.
These seven load-bearing obligations are recorded explicitly in the
[`obligation graph`](../../ops/research-team/cycles/2026-09-01-theorem-reset-joined-gordan-tournament-gate1/OBLIGATION_GRAPH.json).

## Joined-face taxonomy

For diagonal three there are three bad blocks, so a joined face has
`1<=r<=3` positive-mass blocks. If their internal coordinate-face dimensions
are `k_1,...,k_r`, then

\[
 k=(r-1)+\sum_i k_i,
 \qquad |U_i|\le 5+k_i.
\]

Through joined dimension three this gives exactly ten types **modulo
permutation of the active blocks**:

| Joined dimension | Active-block types | Maximum support sizes |
| ---: | --- | --- |
| 0 | `(0)` | `5` |
| 1 | `(1)`, `(0,0)` | `6`; `5+5` |
| 2 | `(2)`, `(1,0)`, `(0,0,0)` | `7`; `6+5`; `5+5+5` |
| 3 | `(3)`, `(2,0)`, `(1,1)`, `(1,0,0)` | `8`; `7+5`; `6+6`; `6+5+5` |

Every global assertion must still cover every labeled placement of these
shapes. Only the single-block types `(0)`, `(1)`, and `(2)` are universal theorems.
The other seven types do not yet have globally attached cells. In particular,
the ten types exhaust the formal face taxonomy but do not supply a finite
all-parent subdivision, specialization maps, monodromy descent, true-infinity
attachment, or a global boundary matrix. Consequently `3/10` must not be used
as an end-to-end D3 denominator. Exact sources are
[`ai/omreal/DIAG3_JOINED_FLOW_TRIANGLE.md`](DIAG3_JOINED_FLOW_TRIANGLE.md) and
the [`independent strategy audit`](../../ops/team/theorem-reset-prover-strategy/FINDINGS.md).

## The row-2599 chart-zero canary

For one exact rank-four parent chart and three valid bad signatures, the
elementary escape sets have sizes `56,56,60`; every pair has an admissible
root, but the threefold elementary-root intersection is empty. The block-mass
triangle, three pair strips, and three singleton ordered-root sectors form a
relative complex with

\[
 \operatorname{rank}(d_1)=3,\qquad
 \operatorname{rank}(d_2)=6,\qquad
 \operatorname{rank}(C_2)=7,
\]

and

\[
 H_0=H_1=0,\qquad H_2\cong\mathbb Z.
\]

The primitive class has coefficient vector

\[
 (-1,1,1,1,1,1,1),
\]

relative to the central triangle, the three pair strips, and the three
singleton sectors. An integral nerve cocycle takes value `1` on this class.
It follows that no chain assembled from ordered elementary-root carrier
complexes `K_i`, whose simplices transport one fixed bad block, can fill it,
even after adjoining arbitrarily long ordered singleton-root words.

This is a precise no-go theorem for **singleton elementary-root/root-only
filler architectures**. It does not exclude an arbitrary fixed-block
semialgebraic carrier unless that carrier is first reduced to the `K_i` model.
It does not prove that a genuinely mixed-block carrier is impossible, does
not exhibit a compact triple-bad component, and is not a counterexample to
diagonal three or 9DVL. Rather, it specifies the missing `d_3` boundary that
a mixed cell must realize. The exact construction, cocycle, and verifier are
in [`ai/omreal/DIAG3_JOINED_FLOW_TRIANGLE.md`](DIAG3_JOINED_FLOW_TRIANGLE.md)
and [`ai/omreal/verify_diag3_joined_flow_triangle.py`](verify_diag3_joined_flow_triangle.py).

## Proposed nested theorem targets

The next program has three nested **research targets**. None is currently a
theorem. Keeping them separate prevents a local `d_3` repair from being
mistaken for either global pair exactness or triple-component escape.

### Common quantified scope

For every one of the `2,604` realizable parent reorientation classes, cover
every component of its normalized realization space and every chart needed
for that coverage. For every ordered presentation
`(sigma_0,sigma_1,sigma_2)` of a three-element pairwise-incomparable antichain
of valid proper extension signatures, use one source-derived finite
semialgebraic subdivision that is **simultaneously** compatible with parent
signs, chart overlaps, residual walls, all witness supports, zero-weight
faces, and the genuine parent compactification.

Let `X` be the global normalized parent space, let `Xbar` be the chosen
compactification, and let `I=Xbar\X` be its genuine parent-infinity locus.
Chart divisors covered by another chart are internal seams, not members of
`I`. Likewise, witness-rank, occurrence-rank, concurrence-rank, and residual
rank drops inside `X` remain theorem cells; only a nonuniform **parent** rank
drop or an actual end of `X` may be declared relative infinity. For any
carrier complex over `Xbar`, write `K_I` for the full subcomplex mapping into
`I`.

Specialization data must be coherent along every chain of incident faces,
not only across one wall at a time. Thus iterated zero-weight cospans, chart
changes, orientations, labels, and all higher commuting diagrams are part of
the quantified statement.

### Target A: universal mixed `(1,0,0)` chain construction

Construct a finite face-natural family of genuinely mixed relative
three-cells over the simultaneous subdivision. On the interior of a cell, the
three positive-mass Gordan witness faces have internal dimensions `(1,0,0)`,
so the joined dimension is `2+1=3` and the support bound is `6+5+5`.
Zero-mass faces are retained as lower joined faces rather than deleted.

For every pair-bad cell used by this construction, prove that the required
common-root choices exist and that the singleton ordered elementary-root
graphs used to change those choices remain connected throughout the cell, or
provide an alternative cover-correct lower-skeleton construction. For every
resulting primitive flow-disk class `alpha in ker(partial_2)`, produce a
mixed three-**chain** `z_alpha` such that

\[
                  \partial_3 z_\alpha=\alpha
                  \quad\text{modulo }K_I.
\]

The chain may contain several mixed cells; no individual cell is required to
have the entire seven-term flow-disk boundary. At residual walls and support
drops, the chains must restrict through explicit enlarged
circuit-elimination faces and coherent iterated specialization cospans. Every
unbounded parameter end must map properly to `I`, never to an artificial box
boundary or to an interior witness-rank stratum.

The row-2599 chart-zero class is one mandatory diagnostic instance of Target
A. Bounding it would not establish the universal target. Conversely, an
obstruction on that instance retires the universal target only if it is proved
for the exhaustively defined class of all admissible mixed cells, not merely
one proposed parameterization.

### Target B: complete joined complex and rational pair exactness

Construct a coverage-certified finite regular relative complex `K(M,S)` for
the actual joined Gordan resolution through dimension three. It must include
every labeled instance of all ten face shapes, including the still-unproved
dimension-three types `(3)`, `(2,0)`, `(1,1)`, and `(1,0,0)`, together with
globally stable cell identifiers, complete extension labels, strict closure,
oriented incidence, and the true relative subcomplex `K_I`.

Prove a proper filtration-preserving comparison from `(K(M,S),K_I)` to the
compactified actual bad union relative to `I`, inducing the required
compact-support cohomology comparison through total degree two. Target A may
supply some `C_3` chains, but it does not supply this coverage or comparison
theorem by itself.

On the pair associated piece, prove the actual rational invariant

\[
 \ker\!\left[
   \bigoplus_{i<j}H_c^1(B_i\cap B_j;\mathbb Q)
   \longrightarrow H_c^1(B_0\cap B_1\cap B_2;\mathbb Q)
 \right]=0.
\]

If this is represented by a finite cochain complex
`C_pair^0 --N--> C_pair^1 --M--> C_pair^2`, its matrix endpoint is

\[
 MN=0,\qquad
 \operatorname{rank}_{\mathbb Q}N+
 \operatorname{rank}_{\mathbb Q}M
   =\dim_{\mathbb Q}C_{\rm pair}^1.
\]

Integral incidence matrices are desirable proof data, but the displayed
rank statement is over `Q`, the coefficient field required by 9DVL. An
integral exactness claim would additionally require Smith-invariant control.

### Target C: independent triple-component escape

For every connected component of every actual triple-bad intersection
`B_0 intersection B_1 intersection B_2`, construct a certified proper escape
to `I`, compatible with the same simultaneous subdivision and all boundary
specializations. Equivalently, prove

\[
              H_c^0(B_0\cap B_1\cap B_2;\mathbb Q)=0.
\]

The exact factor-triple accounting supplies a global source denominator for
this target, but each remaining source must receive complete component and
true-boundary coverage. The count `1,162,302` is not itself a component count
or a proof of escape.

Target C is independent of the pair rank calculation. The block-mass
filtration proves that a nonzero triple `H_c^0` class is a permanent summand;
it cannot be canceled by a mixed `d_3` column. A unified geometric theorem may
package Targets B and C, but it must prove both conclusions explicitly.

**Only Targets B and C together**, using the already proved lower vanishing
theorems, could prove diagonal three. Target A is a high-leverage possible
input to B, not a D3 theorem and not a substitute for C.

## Three surviving routes

1. **Joined mixed-carrier program — preferred feasibility bet.** Establish
   Target A and use it inside the complete coverage/comparison theorem of
   Target B. A unified geometric theorem may also prove Target C, but the
   mixed-chain construction and pair rank do not algebraically cancel the
   independent triple `H_c^0` term. The first useful result is not another
   local disk; it is a universal attachment or descent lemma with all boundary
   quantifiers and a finite route to B.

2. **Complete triple parent-boundary atlas.** Construct
   `Q3_COMPLETE_PARENT_BOUNDARY_ATLAS`, or an equivalent all-residual escape
   theorem, for the `1,162,302` remaining factor-triple source orbits. It must attach
   parent walls, chart divisors, coordinate faces, rank drops,
   occurrence/concurrence-rank strata, extra factors, simultaneous walls, and
   true infinity. This route has an exact global source denominator, but even
   complete success leaves the pair obligation open.

3. **Global pair compression/descent/equivalence.** Build a face-compatible
   global diagram with stable cell identifiers, complete bad-signature labels,
   strict closure pairs and three-cell chains, genuine infinity, and signed or
   mod-two incidence. Then prove a chain equivalence or convergent spectral
   sequence recovering the required pair middle rank. The existing
   component-cosheaf work is a post-closure compiler, not a construction of
   these inputs; see
   [`ai/omreal/DIAG3_COMPONENT_COSHEAF_PILOT.md`](DIAG3_COMPONENT_COSHEAF_PILOT.md).

Routes 2 and 3 are exactly the independent C and B obligations: closing only
one does not prove diagonal three. Route 1 is preferred only because a
sufficiently strong, filtration-compatible geometric theorem might package
substantial parts of both; Target A alone does not.

## Mathematical tools worth testing

These are proposed directions with hypotheses to verify, not claims that an
off-the-shelf theorem already solves the problem.

- **Compatible semialgebraic stratification and Hardt triviality.** Hardt
  triviality applies to a semialgebraic map without a properness hypothesis,
  but it supplies neither canonical maps across strata nor compact-support
  boundary control. Apply it only inside a simultaneous stratification of the
  parent, witness, and boundary projections. Separately prove properness in
  the chosen compactification, compatibility with every zero-weight face, and
  coherence of the resulting specialization maps along arbitrary face chains.

- **O-minimal triangulation or regular-CW refinement.** A compatible
  triangulation may turn the stratified family into finite relative chain
  data. It is useful only if it preserves extension labels, orientations,
  strict closures, and true infinity. A cell count without these fields is
  not a proof object.

- **Acyclic carriers and homological descent.** The convex Gordan witness
  fibers suggest an acyclic-carrier theorem. The missing hypotheses are
  functoriality on the full face category, relative acyclicity at boundary
  faces, and coherence around loops. Establishing those hypotheses would be
  the theorem, not a routine application.

- **Exit-path or cellular-cosheaf organization.** Specialization cospans can
  be encoded as a constructible diagram whose monodromy is visible. This may
  separate local witness construction from global descent, but it requires a
  pre-existing coverage-certified face poset and cannot reconstruct omitted
  closure or infinity data.

- **Circuit elimination, positive-kernel geometry, and witness exchange.** A
  mixed cell should arise from controlled transfer between positive Gordan
  faces. The key conjectural lemma is a face-natural three-block exchange that
  survives support loss by enlarging the circuit face. Exact Farkas
  certificates should be used both to prove feasibility and to expose empty
  proposed seams.

- **Relative obstruction theory and spectral sequences.** The nerve cocycle
  and the block-mass spectral sequence provide dual tests: construct a mixed
  `d_3` column, or construct a cocycle that separates every admissible mixed
  column. This is likely the cleanest way to turn failed construction into a
  reusable no-go theorem.

## Falsification program

Every proposed universal lemma should be attacked before it is scaled.

1. **Local mixed-existence test.** On row 2599 chart zero, define the proposed
   mixed witness-transfer space exactly and test whether the primitive `H_2`
   class dies in its relative chain complex. A surviving cocycle retires all
   of Target A only if the definition is proved exhaustive for every
   admissible mixed cell; otherwise it retires only that parameterization.
   Failure of the existing singleton cocycle to extend is evidence, not a
   proof of existence.

2. **Specialization test.** Cross an exact residual wall where a positive
   witness weight becomes zero. Require explicit left-face, wall-face, and
   right-face maps, then test their compatibility on every available
   two-wall and longer face chain. An exact emptiness certificate for the
   necessary enlarged wall face refutes that proposed cospan.

3. **Monodromy test.** Follow the candidate carrier around the smallest exact
   loop in parent/signature/support space. A nontrivial return permutation,
   orientation reversal, or unmatched label gives a descent obstruction unless
   it is represented in the global complex.

4. **Properness test.** For each candidate parameterization, enumerate every
   finite and infinite frontier. An untagged end or an end on an artificial
   scope boundary disqualifies the construction. Conversely, an exact compact
   triple-bad component in full theorem scope would be a genuine D3
   counterexample, not merely a route counterexample.

5. **Pair-rank and triple-escape tests.** For Target B, assemble the smallest
   complete signed integral or mod-two incidence data, verify `d^2=0`, and
   test the pair middle-rank identity over `Q` on the identified pair
   subquotient. Separately test Target C by component-complete roadmaps to true
   parent infinity. Repeat both tests after every wall specialization and
   global gluing step; local rank exactness does not imply global pair
   exactness, and neither implies triple escape.

The distinction between a route counterexample and a theorem counterexample
must remain explicit. The current row-2599 cocycle retires singleton
elementary-root/root-only fillers in the certified `K_i` model; it does not
refute a mixed carrier or 9DVL.

## Hard go/no-go criteria

Canonical state V8 authorized exactly **one bounded feasibility round** for
the mixed route. It authorized no carrier construction, theorem credit,
ledger promotion, broad residual enumeration, or resource enlargement. That
round is now consumed; V9 records `STALLED / STOP / NONE` and no successor.

A new bounded cycle may reopen on one first missing global edge only under
V9's explicit governance and strict-decrease gate. Any request to select a
construction successor for the full A/B/C program must first supply the
positive-feasibility package named in V8, interpreted through Targets A--C:

- a quantifier-complete candidate statement distinguishing universal mixed
  chains, global pair comparison/exactness, and independent triple escape;
- a source-derived finite exhaustive denominator for every proof obligation;
- a predeclared bounded strict-decrease chain;
- exact compatibility with the row-2599 singleton elementary-root no-go; and
- an independent replay and falsification protocol.

This package is a proof-program feasibility result, not an already proved
theorem. It qualifies only for a separate canonical construction-selection
decision and has ledger effect `0/9`.

A negative feasibility result would receive V8's whole-route retirement
verdict only if it is an independently replayed obstruction quantified over
every carrier satisfying the entire V8 feasibility contract: the full Target A
scope and the carrier's claimed specialization, attachment, comparison, and
rank role in Target B. A counterexample to one exchange lemma,
parameterization, or local canary retires only that object. A null result must
pin the first unresolved global obligation; a timeout must pin the completed
and pending frontier. Either result stops without a successor.

A local filler, sampled success rate, artificial-boundary escape, anonymous
`3/10` clause count, unproved monodromy assumption, or rational rank on an
uncompared partial complex is a **no-go**, regardless of the size of the
computation. The authorized round did not produce the full positive or
universal-negative feasibility package, so the route is stopped. Do not resume
the full triple atlas or expand factor-by-factor sampling merely because
compute is available. Preserve and circulate the proved single-block theorem,
the singleton elementary-root no-go, the exact D3 obligation split, and the
triple accounting as independent results; then either test one of the other
two surviving global routes under the same gates or park 9DVL.
