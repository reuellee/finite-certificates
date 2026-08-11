# Diagonal three: strategy checkpoint after the two-skeleton audit

## Verdict

The honest nine-diagonal score remains `2/9`.  Diagonal three is still the
closest open entry, but it has two independent unresolved obligations:

1. triple `H_c^0`: exclude compact components for the remaining primitive
   factor triples; and
2. pair `H_c^1`: prove split exactness of the signed exclusive-pair end
   complex.

The new single-bad theorem removes the third possible obligation entirely:

\[
                    H_c^q(B_\rho;R)=0\quad(0\le q\le2)
\]

for every coefficient ring.  Nothing in this note promotes the score until
both remaining obligations are proved.

## Exact state of the triple endpoint

The factor reduction has `79,102,449` unordered `S_8` triple orbits.  The
positive certificate layers are disjoint:

| certificate family | closed orbits |
|---|---:|
| jointly affine in three coordinates after reframing | `74,767,375` |
| moving-column support-union degree two | `26,927` |
| degree-three forest fibers | `2,410,414` |
| triangular sequential unit graphs | `12,333` |
| role-frame parent-unit Jacobian minors | `65,550` |
| frame-1119 constant decomposable planes | `61` |
| **total** | **`77,282,660`** |
| **unresolved** | **`1,819,789`** |

Every polynomial identity counted here is replayed exactly over the integers;
the degree-two/three layers instead combine exact incidence classifications
with structural fiber theorems.  Modular arithmetic is used only to propose
identities.  Negative
search accounting is kept separate: 79 role frames are sufficient to replay
the positive coordinate-minor certificates, while exhaustion of that
coordinate-minor family used all 1,120 role frames.  The 61 constant-plane
certificates are a positive screen of frame 1119 only, not an exhaustive
general-linear search.

The tested deterministic full colored occurrence/support key gives no
compression: it is singleton on the unresolved set.  A different
algebraically sufficient quotient is not excluded.  The generic
concurrence lift reduces a presentation to four bilinear equations in ten
variables, with fixed-base complex fiber length at most six, but it does not
turn the projection into a cover.  The stored CAS-produced RUR branch is
verified exactly and gives an internal corank-one ramification point with every parent
bracket nonzero; interval evaluation of all 26,740 residual factors proves
that no fourth factor appears there.
Accordingly the next triple certificate must include the concurrence-chart
frontiers and sheet attachments; support signs or a raw discriminant alone
cannot decide compactness.

## Exact state of the pair endpoint

For

\[
 T=B_0\cap B_1\cap B_2,
 \qquad E_{ij}=(B_i\cap B_j)\setminus T,
\]

the remaining alternating pair differential has the canonical decomposition
(conditional on the still-unproved triple endpoint `H_c^0(T;R)=0`)

\[
 0\to\bigoplus_{ij}H_c^1(E_{ij};R)
 \to\ker H_c^1(D)\to\ker\beta\to0.
\]

On a common finite relative cellular model this is a three-term cochain
complex

\[
                  C^0\mathop{\longrightarrow}^{N}C^1
                     \mathop{\longrightarrow}^{M}C^2.
\]

The coefficient-universal target is a split contraction
`h_2 M+N h_1=I_(C^1)`.  Same-factor root and occurrence choices can be
eliminated through degree one by unit pivots on their proved generic strata,
but the signed specialization and infinity blocks are not yet constructed
globally.

The exact tapered two-dimensional ribbon is a useful negative canary.  Its
cellular matrices have

```text
N : 12098 x 4917, rank 4917
M :  7180 x 12098, rank 7180
```

and leave one free middle class, supported in `H_c^1(E_02)`.  Local product
charts do not remove it: the 39 coincident one-dimensional factor crossings
split transversely.  More generally, `S^7 x R` is an orientable semialgebraic
eight-manifold locally modeled on `I x R^7` but has `H_c^1=Q`.  Thus a Thom
shift requires a **proper exhaustive filtration** whose strata have the
needed compact-support vanishing, not merely local smooth product charts.

## Routes retired by exact counterexamples

The following are not current proof routes:

* switching to diagonals four through nine: their present complete
  certificate inputs are larger or require equally global chamber/frontier
  data;
* the 135-class `UOM(3,8)` private-witness shortcut: the framed rank-three
  base also contains unprescribed flag minors, and the rank-at-most-two locus
  has codimension two and can contribute in the target degree;
* raw discriminant-gradient or saturation Gröbner bases: even an optimized
  828-term discriminant reached large F4 matrices without an algebraic
  result, while the concurrence equations are a strictly smaller endpoint;
* a universal fixed-base submersion and a forced fourth factor at
  ramification: each has an exact counterexample; the tested full-support key
  also gives no compression, without excluding a different invariant;
* local root connectivity or same-factor occurrence `H_1` alone: these
  remove choice fibers but do not determine signed end incidence;
* a local `I x R^7` Thom argument: it does not control global ends or
  exceptional fibers.

## Recommended next certificate

Keep diagonal three.  Do not launch another orbitwise CAS sweep.  The two
remaining work products should be finite, boundary-aware objects:

1. a concurrence-chart roadmap for the `1,819,789` triple residue, retaining
   rank drops, interpolation/gauge frontiers, parent infinity, and sheet
   attachment; and
2. a chamber-decorated receiver/end atlas populating the signed blocks of
   `N,M`, followed by an exact rational-rank and integral Smith/contraction
   replay.

Discovery tools may use modular fingerprints, SAT, and sampled charts, but a
theorem entry must end in exact positive identities or a complete finite
relative boundary complex.  CAS jobs should be restarted only after a
structural reduction makes their output bounded and replayable.
