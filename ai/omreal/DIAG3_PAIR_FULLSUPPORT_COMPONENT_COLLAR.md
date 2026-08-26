# Diagonal three: exact full-support component-collar pilot

## Result

The first proof-producing test of the missed-component contract on the
nonrelative full support now passes on one exact two-dimensional collar.
Factor `19069` has exactly one zero-set component in the declared collar; the
component meets retained source edge `39` once and meets the two artificial
ends of the collar.  Every point of the collar lies in the strict row-2599
parent cell, so its artificial boundary is not parent infinity.

This is a complete component theorem for the declared collar, not for the
nine-dimensional parent cell.  Components disjoint from the collar remain
untested, extension-signature labels are not constructed, the global
missed-component gap remains open, and the honest 9DVL score remains **2/9**.

## Deterministic target rule

This rule is deterministic and replayable.  It was fixed prospectively during
the pilot execution, but no durable pre-result artifact records that choice,
so this checkpoint does not claim formal preregistration.

The optimal 40-edge source bank contains 34 mandatory edges forced by factors
that cross exactly one of the original 105 certified strict-parent segments.
Among the 49 uniquely witnessed factors, the pilot maximizes

```text
(total polynomial degree, monomial count, factor id).
```

The unique winner is factor `19069`: total degree `6`, `108` monomials, and
unique source edge `39 = (chart 0, chart 113)`.  Thus the pilot stresses the
component method on the algebraically largest mandatory witness rather than
selecting a favorable low-degree wall after inspecting collar behavior.

For each coordinate axis, the compiler tests dyadic transverse half-widths
`1, 1/2, ..., 2^-24` using one sufficient tensor-Bernstein gate.  It chooses
the largest certified width and breaks ties by least axis.  The winner is
axis `4`, half-width `1/512`; axes `5` and `7` certify the same width.  Failure
at the immediately larger dyadic width means only that this sufficient
Bernstein gate fails there, not that a larger safe collar cannot exist.

## Exact semialgebraic contract

Let `p0,p113` be the two stored exact rational parent realizations and put

```text
x(s,r) = p0 + s(p113-p0) + (2r-1)e_4/512,
0 <= s,r <= 1.
```

For all seventy target-signed parent brackets, every tensor-Bernstein
coefficient after this substitution is strictly positive.  Hence the entire
parameter square maps into the strict parent cell.  An exact nonzero source-
edge coordinate outside transverse axis `4` certifies that the two affine
directions are independent, so this is an embedded two-dimensional collar
rather than a collapsed parameter square.

Write `F(s,r)` for factor `19069` on the square.  Separate exact Bernstein
certificates prove

```text
-partial_s F > 0,       F(0,r) > 0,       -F(1,r) > 0
```

throughout the square.  For each `r`, the intermediate value theorem and
strict monotonicity therefore give one and only one root `s=phi(r)`.  The
nonvanishing derivative and the implicit-function theorem make `phi`
continuous.  Thus the wall is one interval, its complement consists of two
regular open disks, and the wall meets the original source segment `r=1/2`
at exactly one algebraic point.  Exact Sturm replay isolates that point and
the two wall endpoints to width at most `2^-32`.

## Closure and incidence

The emitted regular-CW roadmap has:

| dimension | cells | roles |
|---:|---:|---|
| 0 | 7 | four collar corners, two wall endpoints, one source-skeleton hit |
| 1 | 8 | six artificial boundary arcs, two wall arcs |
| 2 | 2 | positive and negative wall chambers |

Every strict closure pair and strict three-cell chain is stored.  Canonical
edge orientations and the two chamber boundaries give integral matrices
`d1,d2` with `d1*d2=0`.  The six artificial boundary arcs and their vertices
form `scope_boundary_subcomplex`.  The true `parent_infinity_subcomplex` is
empty because all seventy parent inequalities are strict on the closed
collar.  Re-sealed hostile semantic mutations require rejection if the wall
endpoint, component, or scope boundary is relabelled as parent infinity.

## Certificate and separately embodied structural replay

Build the deterministic certificate with

```console
PYTHONDONTWRITEBYTECODE=1 python \
  ai/omreal/build_diag3_pair_fullsupport_component_collar.py
```

Run the separately embodied structural verifier with

```console
PYTHONDONTWRITEBYTECODE=1 python \
  ai/omreal/verify_diag3_pair_fullsupport_component_collar.py
```

The verifier does not import the producer, but this is not implementation-
independent replay.  Producer and verifier share
`diag3_pair_parent_source_transition_core`,
`verify_diag3_pair_fullsupport_safe_segment_walls`,
`verify_diag3_pair_global_parent_face_gate`,
`DIAG2_PIVOT_LABELED_PAIR_ORBITS_VERIFY`, and
`DIAG9_GRAPH_verify_row2599_slice`.  They also use near-parallel exact collar-
substitution and tensor-Bernstein routines.  Within that declared boundary,
the verifier separately embodies the 105-by-17,824 incidence reconstruction,
target and axis selection, seventy parent restrictions, wall inequalities,
three Sturm isolations, closure poset, signed incidence, and source-pin checks.
It rejects nineteen re-sealed hostile semantic mutations, including an extra
top-level theorem claim, false independence claim, collapsed collar,
fabricated second component, missing source-skeleton hit, false parent
infinity, global-coverage claim, invented extension labels, corrupt incidence,
and promotion to `3/9`.

An external SymPy reconstruction was an additional review audit.  It is not a
persisted repository verifier and is not part of this certificate's standing
trust claim.

The certificate is
`data/DIAG3_PAIR_FULLSUPPORT_COMPONENT_COLLAR.json`.

## Decision

The collar shows that the proposed exact component contract is implementable
on a genuinely proof-bearing full-support wall, including complete declared-
scope accounting and topology.  It does not estimate the probability of a
component elsewhere in the parent cell missing all forty retained edges.
The next material scale test is a preregistered factor family or a direct
parent-cell roadmap with complete global component accounting.  The earlier
section-550 and section-960 stars remain proper-support compiler regressions
only: they lie in the relative subspace and generate nothing in the relevant
relative chain complex.
