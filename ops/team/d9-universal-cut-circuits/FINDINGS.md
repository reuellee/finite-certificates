# D9 universal cut: circuit/combinatorics opening finding

## Outcome

The 13 residual wall types, support-minimal Gordan circuits, circuit
elimination, signed local multiwall incidence, and local transport do **not**
by themselves determine global separator behavior.  They form a finite exact
**local frontier**, but any complete separator grammar must retain additional
global chamber-component memory.

This is a fail-closed null for the actual `UOM(4,8)` universal cut gate, not a
counterexample to diagonal nine.  The local-only completeness claim is
disproved exactly.  A complete grammar with full global memory remains finite
in principle by the master-chamber graph theorem, but no source-reconstructible
master roadmap, `10,000`-type bound, or `250,000`-instance bound is present.
The theorem ledger therefore remains `2/9`.

## Strongest positive theorem retained

The pinned predecessor proofs give the following finite local grammar.

1. **One-sided specialization.**  All 13 residual types split into nine
   ordinary and four localization types.  Their support-minimal circuit
   cospans are respectively `5 -> 4 <- empty` and `4 -> 3 <- empty`.
2. **Opposite-partner elimination.**  Whenever a chosen circuit birth has an
   opposite-side partner in the same block, positive circuit elimination
   supplies an interval carrier on at most six normals (ordinary) or five
   normals (localization).  The exact row counts give `671` certified pairs
   and `2,420` persistent-support candidates.
3. **Choice coherence.**  Same-side partner choices span a simplex at one
   generic wall.
4. **Higher coherence.**  Once all codimension-one maps land facewise in
   common nonempty coordinate carriers, convexity gives integral coherent
   fillers in every codimension.  No independent higher-codimension
   obstruction remains after that support premise is met.

This is the strongest positive circuit theorem available.  It is conditional
exactly where the universal cut proof needs new information: monochromatic
stars, multi-block transfer, global matching acyclicity, complete chamber
gluing, and proper boundary/infinity behavior.

## Exact local-memory no-go

`FINITE_GRAMMAR_FRONTIER.json` contains two connected, simple, bipartite,
cubic signed chamber graphs on 16 vertices.  In both graphs:

- eight chambers have active sign `+` and eight have sign `-`;
- every chamber has one active type-37 wall and two inactive safe edges;
- every active edge carries the same ordinary `5 -> 4` specialization;
- inactive transport is the identity; and
- there are no codimension-two multiwall records.

The complete radius-one typed-star, local circuit-cospan, signed multiwall,
and edge-transport records are identical.  The global cut behavior differs:

| Configuration | Full graph | `+` sector | `-` sector |
| --- | ---: | ---: | ---: |
| two same-sign 4-cycles | 1 component | 2 components | 2 components |
| one same-sign 8-cycle | 1 component | 1 component | 1 component |

Therefore no decision rule factoring through that local observation contract
can be a complete separator grammar.  It must additionally retain how safe
same-sign chamber germs are globally glued.  The pair is minimal within the
declared class: a simple bipartite 2-regular same-sign graph is a union of
cycles of length at least four, so a disconnected example needs at least
eight vertices of one sign; the active perfect matching forces 16 total.

This pair is an abstract signed chamber-graph obstruction, not a claimed
`UOM(4,8)` realization.  Its exact consequence is an information lower bound:
local types cannot determine global cuts.  It does not show that a global-
memory grammar is infinite.

## Why full global memory is sufficient but not yet available

The proved master-chamber graph theorem identifies components of every
feasibility intersection with components of the correspondingly labeled
induced chamber graph.  Thus the following data are sufficient for a finite
separator decision for one fixed parent:

- connected master-chamber identities;
- endpoint incidence for every generic wall component;
- complete chamber signature labels (or exact active-sector sign words);
- coverage showing that no chambers or adjacencies are missing; and
- proper end/boundary accounting for the roadmap construction.

Calling this full incidence object a “grammar” makes it finite, but it no
longer compresses global cuts to the 13 local wall types.  No complete object
of this kind exists for any of the 2,604 parents in the pinned source tree.
The first pivot projection also creates 142 new irreducible factors, so closure
under only the residual catalog is already false.

## First actual unclassified composition

Actual third-compound geometry contains monochromatic wall stars for every
one of the 13 types.  A block feasible on one side has no positive circuit of
any support there, by Gordan's alternative, so same-block circuit elimination
cannot carry its dying witness across the wall.

The first explicit surviving composition is the row-2599 three-block rigid
corner:

| Signature | Positive circuit support |
| ---: | --- |
| `68231279848521727` | `0,19,34,37,40` |
| `62614156573450111` | `0,18,47,48,53` |
| `40418078342512640` | `4,5,18,20,40` |

In the exact colex triple order, the union has parent-label degree vector
`(4,4,6,4,5,5,3,5)`.  Every degree is at least three and no supported label
has the required common-apex structure, so neither the plane-pencil nor
common-apex transfer rule classifies it.  The missing production is an
acyclic multi-block transfer to another bad block or to a proper boundary
cell.  This corner is not a global separator, does not prove a compact
component, and does not disprove 9DVL.

## Hostile abstract countermodels

The Atlas polynomial model with three connected components is correctly
rejected as a diagonal-nine counterexample because it lacks two explicit
load-bearing hypotheses: its polynomials are not certified residual derived-
normal determinants `D_E/(constant * parent-bracket unit)` in one realizable
`UOM(4,8)` parent cell, and its halfspace labels are not certified extension-
signature feasibility labels governed by the Gordan wall-side theorem.  It
still validly refutes any implication from smooth coorientation or local
pivots alone.

The new graph pair is scoped the same way: it tests information content, not
geometric realizability.  The verifier rejects missing edges, sign corruption,
forged component counts, erased specialization transport, and a forged
semantic digest.

## Source discrepancy

The table in `BLOCK_GORDAN_RESIDUAL_ELIMINATION_CELLS.md` prints an auxiliary
total of `131`.  Its 13 displayed rows sum to `123`.  The row-wise counts and
the exact verifier both reproduce `671` pairs and `2,420` support candidates,
so this is a non-load-bearing arithmetic typo; no predecessor file was edited.

## Replay

From the repository root:

```console
python ops/team/d9-universal-cut-circuits/generate_cut_grammar_frontier.py
python ops/team/d9-universal-cut-circuits/verify_cut_grammar_frontier.py
```

The independent verifier hashes every direct source, reconstructs both graph
component counts and the shared local invariant, rechecks the 13-type finite
frontier and rigid-triple degree vector, and exercises all hostile canaries.

The highest-value next discriminator is an exact census of multi-block
transfers out of actual monochromatic stars on a coverage-certified master
roadmap.  Stop at the first pair of globally distinct chamber gluings with the
same proposed bounded grammar state, or produce a global acyclic potential
and proper end attachments for every transfer.
