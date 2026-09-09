# Candidate compact-relative block-Gordan source theorem

Status: `OPENING PROOF DRAFT / NOT INDEPENDENTLY ACCEPTED`.

This note records the new theorem-capable input that justifies opening the
cycle.  It is deliberately stronger than an existence claim for an unrelated
simplicial replacement and weaker than diagonal three: it constructs the
global finite relative source on which the still-open rank and escape
questions can be asked exactly.

## Candidate theorem

Fix a realizable uniform rank-four parent oriented matroid `M` on `[8]`.  Let
`S=(sigma_0,sigma_1,sigma_2)` be an ordered triple of valid proper pairwise-
incomparable extension signatures.  For every nonempty `R subseteq S`, let
`Gamma_R -> B_R` be the joined block-Gordan resolution.

There is one finite oriented simplicial pair `(K_S,K_I)` with labeled
subpairs `(K_R,K_R cap K_I)` for all nonempty `R subseteq S` such that:

1. `K_R\K_I` is a triangulation of `Gamma_R`;
2. `H^*(K_R,K_R cap K_I;Z) = H_c^*(Gamma_R;Z) = H_c^*(B_R;Z)`;
3. `R subseteq R'` is represented by literal zero-padding subcomplex
   inclusion, not an inferred map;
4. the block-mass filtration, every block-coordinate zero face, all parent
   signs, residual walls, and declared rank strata are unions of open
   simplices, while every closed member and true infinity are subcomplexes;
5. the induced finite filtered relative chain complexes recover the
   compact-support Mayer--Vietoris diagram and its integral incidence maps.

The construction is uniform and algorithmic over the finite set of all 2,604
parent classes.  "Algorithmic" means reducible to exact first-order
real-closed-field operations and compatible semialgebraic triangulation; it
does not assert a practical size bound or an installed implementation.

## Proof architecture

### 1. One global compact parent chart per uniform parent

Use labels `1,2,3,4` as a projective basis and label `5` as the scale-fixing
point.  Uniformity makes every required coordinate and bracket nonzero.
Projective transformations send the first four points to the coordinate
points.  Positive column scalings then send point `5` to the sign vector
fixed by the chirotope.  Each of points `6,7,8` lies in a chirotope-fixed open
projective orthant; normalizing the sum of its absolute homogeneous
coordinates to one identifies that orthant with `relint Delta^3`.

Thus the normalized realization space `X_M`, including every connected
component, is exactly the subset of `(relint Delta^3)^3` on which the 70
parent bracket polynomials have the signs prescribed by `M`.  This avoids
declaring affine gauge changes to be infinity.

Required audit: prove uniqueness modulo the stated projective and positive-
scaling actions, and check that no normalized component is lost by the fixed
five-label frame.

### 2. Exact closure, not naive weak closure

Put

```text
Xbar_M = topological closure of X_M in (Delta^3)^3,
I_M    = Xbar_M \ X_M.
```

Because `X_M` is semialgebraic, its closure is closed semialgebraic; because
the ambient product of simplexes is compact, `Xbar_M` is compact.  An exact
first-order definition is

```text
z in Xbar_M  iff  for every epsilon>0 there exists x in X_M
                    with ||x-z||^2 < epsilon^2.
```

Quantifier elimination produces an exact quantifier-free description if one
is required.  This formulation intentionally does not replace every strict
inequality by a weak one without proof.  A point of `I_M` has either a
simplex coordinate or a parent bracket equal to zero; conversely every point
of `Xbar_M` with all those quantities nonzero retains the fixed sign pattern
and lies in `X_M`.  Hence `I_M` is genuine parent boundary.

Required audit: distinguish boundary points from internal residual and
witness-rank strata, and prove that the complement statement remains true on
all components.

### 3. Compactify the total Gordan source

For nonempty `R subseteq S`, extend the polynomial matrices `A_sigma(Y)` to
`Xbar_M` and define

```text
Gammabar_R = {(Y,(w_sigma)) in Xbar_M x Delta^(56|R|-1):
              A_sigma(Y)^T w_sigma=0 for every sigma in R}.
Gammabar_R,I = Gammabar_R cap (I_M x Delta^(56|R|-1)).
```

Nonnegativity and total mass one are carried by the simplex.  This is a
closed subset of a compact set, so it is compact.  Restriction to `X_M` is
exactly the previously proved joined block-Gordan source `Gamma_R`; therefore

```text
Gamma_R = Gammabar_R \ Gammabar_R,I.
```

Extra Gordan fibers which appear only at a degenerate parent lie entirely in
the relative boundary and cannot create artificial interior classes.  If
`R subseteq R'`, zero-padding the new blocks gives a closed inclusion of
compact pairs.  Signature names and witness coordinates are literal labels.

### 4. Simultaneous finite triangulation

Inside the single compact semialgebraic ambient `Gammabar_S`, take the finite
family consisting of:

- every zero-padded `Gammabar_R` and its relative-boundary part;
- every closed level of the block-mass support filtration;
- all block-coordinate zero faces and their finite intersections;
- the inverse images of all parent bracket zero sets, residual factor zero
  sets, and declared witness/occurrence/concurrence rank loci;
- closures, intersections, and differences needed to make the requested
  stratification finite and Boolean-complete.

The compatible semialgebraic triangulation theorem supplies one finite
triangulation in which every family member is a union of open simplices and
every closed member is a subcomplex after subdivision.  Barycentric
subdivision supplies a regular oriented complex if required.  Because all
subdiagrams were included before triangulating, zero-padding maps are literal
subcomplex inclusions and all labels have stable carriers.  Simplicial
closure gives exact strict closure; `K_I` consists exactly of simplices in
the inverse image of `I_M`.

Required audit: state the exact compatible-triangulation theorem used and
confirm that the finite Boolean family, rather than a post hoc list, contains
every datum later used by the degree-two chain complex.

### 5. Relative and filtered comparison

For a compact pair `(Gammabar_R,Gammabar_R,I)`, the standard identification
gives

```text
H^*(K_R,K_R cap K_I;Z)
  = H^*(Gammabar_R,Gammabar_R,I;Z)
  = H_c^*(Gamma_R;Z).
```

The already proved proper block-Gordan projection has nonempty contractible
fibers, so proper base change gives

```text
H_c^*(Gamma_R;Z) = H_c^*(B_R;Z).
```

Compatibility with the closed block-mass filtration makes its finite
spectral sequence the compact-support Mayer--Vietoris spectral sequence.
Orienting the simplices produces exact integer boundary matrices and
`d^2=0`; tensoring with `Q` later gives the required middle-rank problem.

This step supplies a finite exact place to perform the rank calculation.  It
does not prove that calculation, remove a critical cell, or give a proper
escape from every triple component.

## Falsification matrix

| possible failure | exact test | consequence |
| --- | --- | --- |
| fixed five-label frame loses a component | exhibit a uniform realization not represented modulo projective and positive scaling | theorem false |
| `I_M` contains an internal point | give a closure point with all parent brackets and simplex coordinates nonzero but outside `X_M` | theorem false |
| compactified equations add an interior point | give `Y in X_M` where extended and original Gordan systems differ | theorem false |
| zero-padding is not a map of pairs | exhibit a violated equation, mass condition, or boundary label | theorem false |
| simultaneous family is infinite | identify an essential datum not expressible using the finite parent/signature/support/rank lists | theorem incomplete |
| triangulation loses a closed subcomplex | show the invoked compatibility theorem does not cover the finite closed family | theorem incomplete or false |
| relative cohomology is not compact support | violate compactness, closedness of `K_I`, or equality of the open complement | theorem false |
| filtration differs from Mayer--Vietoris | exhibit a block-mass stratum or differential not represented by the filtered pair | theorem false |
| no executable SREP backend | none; this is an implementation fact | no mathematical consequence |
| complexes are astronomically large | none; record resource infeasibility separately | no mathematical consequence |

## What a positive proof would and would not change

A positive, independently verified close would reduce the seven load-bearing
obligations to the three genuine mathematical endpoints:
`middle_rank_replay`, `diag3_pair_hc1`, and `diag3_triple_hc0`.  It would make
a later global potential or discrete-Morse theorem well-posed on a pinned
finite relative source.

It would not change the `2/9` ledger, settle any pair rank, prove any triple
escape, prove diagonal three, validate an implementation, or authorize a
successor cycle.
