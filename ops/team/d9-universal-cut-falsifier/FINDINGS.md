# Universal D9 cut opening: independent falsifier findings

## Verdict

The opening gate must fail closed at `UNIVERSAL_CUT_SCHEMA_COVERAGE_GAP`.
There is an exact fatal counterexample to the *abstract local-to-global
inference*, but not an actual `UOM(4,8)` D9 counterexample.  Smooth connected
graph walls, fixed coorientations, transverse multiwalls, consistent strict
literals, and proper pairwise-incomparable regions do not determine global
feasible-component cuts.

The missing datum is global memory: a complete compactified incidence object
with stable chamber-component identities, source-derived infinity
attachments, and occurrence-to-global-factor orientation transport.  Calling
the thirteen residual wall types and their local circuits a finite grammar
does not supply that object.

## Minimal exact implication countermodel

In `R^9` with coordinates `(x,y,z1,...,z7)`, set

\[
 q_1=y,\qquad q_2=x^2-1-y,\qquad q_{2+j}=z_j\quad(1\le j\le7),
\]

and `F_i={q_i>0}`.  Every wall is a connected smooth global graph.  The
displayed pivot derivatives are `1`, `-1`, and `1`.  The only intersections
of the first two walls have `x=+-1`; after adjoining the seven coordinate
walls there are two full multiwall points.  Their Jacobian determinants are
`2` and `-2`, so both links are the complete simple-normal-crossing orthant
link.

Nevertheless the common strict sector is

\[
 \{x<-1,\ 0<y<x^2-1,\ z_j>0\}
 \;\sqcup\;
 \{x>1,\ 0<y<x^2-1,\ z_j>0\}.
\]

Each displayed set is connected: use `s=y/(x^2-1)` to identify it with an
interval times `(0,1)` times `(0,infinity)^7`.  The rational points

```text
(-2,1,1,1,1,1,1,1,1) and (2,1,1,1,1,1,1,1,1)
```

are feasible and have the same all-positive factor-sign word.  A path between
them would attain `x=0`, where `q2=-1-y<0` because `q1=y>0`.  Hence they lie
in different components.

The verifier reconstructs exact witnesses for all `9*8=72` ordered
noninclusions.  Thus every `F_i` is nonempty and proper and all nine are
pairwise incomparable.  Properness does not reject the model.

This is minimal inside the relevant common-pivot graph-wall class.  In one
dimension, intersections of oriented sides of connected smooth zero sets are
intervals.  One global graph-wall side in dimension two is connected.  Two
walls in dimension two are the first possible core; the seven coordinate
halfspaces only lift it to the D9 arity and dimension.

The canonical model in `ATLAS_HELLY.md` uses

\[
 q_2=(x^2-1)(x^2-4)-y
\]

and has three components.  The degree-two model above is a smaller exact
version of the same logical obstruction.

## Local types plus coarse infinity still lose global memory

A second pair makes the missing information sharper.  In core coordinates
`(x,z,y)`, keep `q1=y` and compare

\[
\begin{aligned}
q_2^N&=(x^2+z^2-1)(x^2+z^2-4)-y,\\
q_2^D&=((x-3)^2+z^2-1)((x+3)^2+z^2-1)-y.
\end{aligned}
\]

In both arrangements the `q2` wall is one connected smooth graph, its
intersection with `q1=0` is two disjoint smooth circles, every intersection
is transverse, and the degree-four leading form is `(x^2+z^2)^2`.  Thus the
local type counts and the coarse behavior at infinity agree.

For the nested circles, `{q1>0,q2^N>0}` fibers over the disjoint union
`x^2+z^2<1` and `x^2+z^2>4`, so it has two components.  For the disjoint
circles, `{q1>0,q2^D>0}` fibers over the connected exterior of the two
disjoint unit disks centered at `(-3,0)` and `(3,0)`, so it has one component.
For an explicit path, first increase `|z|` to at least `2`, move horizontally
there, and then move on `x=0`; those corridors have squared clearance at
least `4` and `9`, respectively, from the unit-disk centers.
The auxiliary factors

```text
q3=u1, q4=1-u1, q5=u2, ..., q9=u6
```

lift both examples to nine regions in `R^9` without changing the component
count.

This pair does not say that no finite schema can work.  It says exactly what
such a schema must contain: the global attachment/nesting relation of wall
components.  A list of local residual types, circuits, orientation multisets,
recursive flags, and infinity leading signs is not complete.

## What rejects the abstract model

Two different statements must not be conflated.

The exact theorem-domain gate is `SOURCE_RECONSTRUCTIBLE_D9_INSTANCE`:

- `X` is one normalized realization cell of a realizable `UOM(4,8)` parent;
- every factor is reconstructed from actual residual determinant occurrences;
- duplicate occurrences are transported through the fixed sign of `c_E*u_E`;
- every region is the actual feasibility locus of a named extension
  signature; and
- parent residence, properness, and ordered noninclusions are exact.

The abstract model supplies none of the parent, signature, occurrence, unit,
or residence data, so this is the least noncircular domain hypothesis that
rejects it.  It is only a domain restriction.  It does not prove the proposed
cut reduction.

The exact structural discriminator is
`GLOBAL_COMPONENT_FAITHFUL_SIGN_GEODESY`: complete compactified chamber and
stratum coverage, stable global component identities, true-infinity
attachments, and an injective/isometric factor-sign map.  The sufficient
form in `DIAG9_SIGN_GEODESY_AUDIT.md` asks for paths that cross each geometric
factor at most once.  Both disconnected models violate this immediately:
distinct components have the same complete sign word.  No such theorem is
proved for the actual D9 residual arrangement.

The superficially weaker hypothesis “every complete factor-sign cell is
connected” also rejects the model, but simply assumes the desired conclusion
and cannot serve as a reduction lemma.

## Canonical hostile canaries

- **Occurrence orientation.**  The active-sector theorem is proof-safe only
  after every duplicate occurrence is translated through `sign(c_E*u_E)`.
  A factor ID plus a raw occurrence sign is insufficient.
- **S12,37 opposite parent forms.**  At both selected supports, exact
  opposite parent initial forms with positive `(1,1)` Gordan weights make the
  ordinary common-radial strict link empty.  Weighted recursive analysis is
  still open.
- **Factor 8552.**  The exact factor `q=d*i-e` has negative, zero, and
  positive lifts on the same recursive facet with bracket `1237=0`.  It is
  not a strict-open-parent crossing and not a global separator.
- **Parent-860 repair.**  Sixteen exact chords connect every support
  intersection on the resulting 24-chamber network.  The source explicitly
  says that this network neither covers all chambers nor meets every global
  component.  Its connectivity cannot be promoted.
- **Properness.**  Exact ordered witnesses can prove noninclusion.  Absence
  from a sampled network cannot prove inclusion, universal support, or a
  complete feasible-component label.
- **Infinity.**  An artificial box boundary, projective end without a source
  compactification, or a leading homogeneous sign is not a genuine parent
  infinity attachment.

## Null boundary and first discriminator

No actual realizable parent/family with two feasible components and a complete
separator was found.  No exhaustive parent/family search was attempted, and
no current-cycle producer artifact was inspected.  The first unresolved
discriminator is therefore exact and operational:

> For one actual source-reconstructible D9 family, build the complete
> compactified active-sector chamber/stratum incidence with stable component
> IDs and genuine infinity attachments.  Decide whether two chambers with the
> same complete active-factor sign word lie in distinct components.

A same-word pair is a fatal counterexample to global sign-geodesy and to any
component labeling by factor signs.  Its absence under complete coverage is
the first evidence that can reject the abstract mechanism without assuming
connectivity.  Until that object exists, the universal opening gate remains
inconclusive and must stop fail-closed.  The theorem ledger remains `2/9`.

## Replay

```console
PYTHONDONTWRITEBYTECODE=1 python \
  ops/team/d9-universal-cut-falsifier/verify_d9_universal_cut_falsifier.py
```

The replay uses only the Python standard library, reconstructs the exact
rational certificates independently, checks every pinned source, audits the
canonical canary scopes, and rejects all hostile mutations.
