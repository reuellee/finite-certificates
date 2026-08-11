# Diagonal three: the single-bad two-skeleton

## Outcome

Let `X` be a normalized realization cell of a realizable uniform
rank-four oriented matroid on eight elements, and let `B_rho` be the Gordan
bad locus of one valid extension signature.  Then

\[
                 \boxed{H_c^q(B_\rho;R)=0\qquad(0\le q\le2)}       \tag{1}
\]

for every coefficient ring `R`.

The proof uses the proper normalized Gordan resolution, but filters its
**convex witness fibers by their actual coordinate faces**, rather than by
an arbitrary cofinal cover.  A `k`-face uses at most `5+k` positive
coordinates.  In total compact-support degree at most two, only fiber
dimensions `k=0,1,2` occur.  Their support unions have at most five, six,
and seven parent triples, respectively, and admit proper motion fibers of
dimensions at least three, two, and one.  The compact-support shifts cancel
the fiber-face dimensions exactly.

This proves the single-signature term needed by the coarse three-signature
Mayer--Vietoris complex.  It does **not** prove the pair or triple terms and
does not by itself prove the third diagonal.

The dependency-free arithmetic audit is
[`verify_diag3_single_bad_two_skeleton.py`](verify_diag3_single_bad_two_skeleton.py).

## 1. Coordinate-face filtration of the proper resolution

Write

\[
 P_\rho(Y)=\{\lambda\ge0:\mathbf1^T\lambda=1,
                         A_\rho(Y)^T\lambda=0\}                 \tag{2}
\]

and

\[
 \Gamma_\rho=\{(Y,\lambda):Y\in X,\ \lambda\in P_\rho(Y)\}.
                                                                    \tag{3}
\]

The projection `Gamma_rho -> B_rho` is proper with nonempty compact convex
fibers.  Proper base change therefore gives

\[
                  R\Gamma_c(\Gamma_\rho;R)
                    \simeq R\Gamma_c(B_\rho;R).                   \tag{4}
\]

For `U subset binom([8],3)`, let `P_U(Y)` be the coordinate restriction of
(2) obtained by setting all weights outside `U` to zero.  A point of (2)
lies in the relative interior of one unique coordinate face, namely the
face indexed by its positive support `U`.

On a stratum on which this face has dimension `k`, its augmented equality
matrix consists of the four Gordan rows and the normalization row.  If its
rank is `r_U`, then

\[
                  k=|U|-r_U,\qquad 1\le r_U\le5,                 \tag{5}
\]

and hence

\[
                              |U|\le5+k.                          \tag{6}
\]

On the positive-support locus, constant-rank kernel charts turn these
relative interiors into open `k`-cell bundles, with their orientation local
system.  A radial trivialization from the fiberwise log-barrier point gives
the local cell-bundle charts.  No one augmented pivot is fixed globally: the
usual nonzero-pivot charts merely form an open cover of the constant-rank
kernel bundle.

These strata have the required frontier order.  A limit can replace `U` by
a proper subset, and with `U` fixed it can only lower the augmented rank and
therefore increase `k`.  Ordering first by support inclusion and then by
descending `k` gives a finite closed filtration.  Its compact-support
spectral sequence has contributions

\[
              H_c^{n-k}(D_{U,k};\mathcal O_{U,k})                \tag{7}
\]

in total degree `n`, where `D_(U,k)` is the parent base stratum and
`O_(U,k)` is the fiber-orientation local system.  For `n<=2`, (7) can occur
only for `k=0,1,2`.

It therefore suffices to prove

\[
       H_c^j(D_{U,k};L)=0\qquad(0\le j\le2-k)                    \tag{8}
\]

for every rank-one coefficient system `L` pulled back from the quotient
used below.

## 2. Support-plane motions

For a support union `U`, put `deg_U(e)=|{I in U:e in I}|`.  Moving a parent
column while keeping every incident support three-plane fixed changes each
corresponding derived normal only by a positive scalar before the parent
residence boundary.  Inverse positive scaling of the appropriate Gordan
coordinate identifies the coordinate face `P_U(Y)` throughout the motion;
in particular its dimension and positive support do not change.

The familiar cases are:

* `deg_U(e)=0`: the full projective residence three-cell of `e`;
* `deg_U(e)=1`: the projective two-cell inside its unique support plane;
* `deg_U(e)=2`: the open projective interval in the intersection of its two
  distinct incident support planes.

Each motion has an end at a parent bracket wall.  Normalize a fixed
projective frame among five nonmoving labels and retain, as quotient data,
the projective normal ray of every incident support plane (with duplicate
planes retained only once).  This extra plane data is essential: after a
moving label is forgotten, the other two columns of one incident triple do
not determine its three-plane.  The resulting global semialgebraic quotient
has as its fibers exactly the parent-sign residence domains inside the
prescribed plane intersections.  They are oriented open manifolds, and
their componentwise compact-support cohomology is concentrated in their top
dimension.

We need one additional two-parameter form.

> **Two-pencil theorem.**  If distinct labels `e,g` both have degree two in
> `U`, then the coordinate-face stratum has a quotient whose nonempty fiber
> components are contractible oriented open two-manifolds.

Hold the other six columns and the retained incident-plane rays fixed.
First move `e` in the intersection of its two incident support planes.  Both
planes remain fixed.  Then move `g` in the intersection of its two incident
support planes; a plane containing both labels was already fixed by the
first motion and stays fixed during the second.  Thus every support plane in
`U` remains fixed throughout the ordered two-parameter motion.  Conversely,
the frame and plane-ray quotient data force precisely these two ordered
residence parameters, so no additional point lies in the quotient fiber.

The full residence domain need not be convex.  At fixed first parameter,
every parent bracket is affine in the second parameter, so every nonempty
section is an open interval.  A connected component projects to an open
interval, and a nonempty interval section cannot meet two components.
Locally persistent choices, a partition of unity, and straight-line motion
in each section retract the component onto its projected interval.  Hence
the component is contractible.  The two parameter directions and the fixed
projective frame orient it globally.

The same proof includes supports containing both moving labels: after the
first move their common support plane is fixed, and the second column stays
inside that fixed plane.

All these quotients preserve `D_(U,k)`.  More explicitly, if the support
normal `a_i` is replaced by `s_i a_i`, with every `s_i>0`, then

\[
 \lambda_i\longmapsto
 \frac{\lambda_i/s_i}{\sum_j\lambda_j/s_j}                     \tag{8a}
\]

is a face-preserving homeomorphism of the normalized positive kernel
polytopes.  It preserves positive support and face dimension, hence the
constant-rank kernel stratum, even though an individual augmented pivot
minor can cross zero.  Along the positive-scaling orthant this map is
isotopic to the identity on every face, so it preserves the face orientation.
The orientation system `O_(U,k)` is therefore constant on every residence
fiber and descends to the quotient.  Consequently the compact-support
vanishing holds with the local coefficient system in (8), not only with
constant coefficients.

## 3. The three fiber dimensions

### Vertices

For `k=0`, equation (6) gives `|U|<=5`.  The single-piece
degree-two theorem in `THREE_SHEAR_SINGLE_PIECE_REDUCTION.md` supplies the
underlying three-dimensional motion: an omitted-label three-cell, or a
degree-one support-plane two-cell followed by a light-label pencil.  Apply
that motion proof directly to `D_(U,0)`, rather than inferring the claim from
the closed-piece cohomology statement.  Positive normal scaling preserves
the exact positive support and rank, so the quotient restricts to this
locally closed stratum.  Its fiber components are contractible oriented open
three-manifolds.  The argument is coefficient-independent and the system
`L` descends by Section 2; hence, for every coefficient ring,

\[
                         H_c^j(D_{U,0};L)=0\qquad(j\le2).          \tag{9}
\]

### Edges

For `k=1`, one has `|U|<=6`, so the total label incidence is at most `18`.
If a label has degree zero or one, its residence motion has dimension at
least two.  Otherwise every label has degree at least two.  If at most one
label had degree two, the incidence sum would be at least

\[
                         2+7\cdot3=23>18,                         \tag{10}
\]

which is impossible.  Thus there are two degree-two labels and the
two-pencil theorem applies.  In every case

\[
                         H_c^j(D_{U,1};L)=0\qquad(j\le1).          \tag{11}
\]

### Two-faces

For `k=2`, one has `|U|<=7`, hence at most `21` label incidences.  Some label
has degree at most `floor(21/8)=2`.  Its residence motion has positive
dimension and a proper end.  Hence every component of `D_(U,2)` is
noncompact and

\[
                         H_c^0(D_{U,2};L)=0.                       \tag{12}
\]

Equations (9)--(12) are exactly (8).  Every contribution of total degree at
most two in the coordinate-face filtration is zero, so (1) follows from
(4).

## 4. Corollary for every primitive residual wall

Let `f` be a primitive residual factor and put

\[
                         H_f=X\cap Z(f).                         \tag{13}
\]

Choose one labeled occurrence of `f`.  The certificates in
`verify_derived_wall_sides.py` put it in one of the following two forms.

* For an ordinary occurrence, let `U` be its four derived normals.  Their
  determinant is a nowhere-zero parent-bracket unit times `f`.  On `H_f`,
  all four circuit cofactors obtained from the certified auxiliary normal
  are nonzero parent-bracket units.  Hence the normals in `U` have rank
  exactly three, and their one-dimensional relation has nonzero coefficients
  of constant sign throughout `H_f`.
* For a localization occurrence, let `U=C` be its distinguished three
  normals.  The five-vector identity has three fixed nonzero bracket-unit
  coefficients and a final coefficient equal to a bracket unit times `f`.
  Thus `C` is dependent exactly on `H_f`.  The fixed coefficient minors
  contain two members of `C`, so `C` has rank exactly two there, and again
  its unique relation has nonzero coefficients of constant sign.

Reorient the normals of `U` by these constant signs.  If
`P_U^+(Y)` denotes the normalized coordinate kernel using only those
reoriented rows, the preceding rank statements give the exact equality

\[
 H_f=\{Y\in X:P_U^+(Y)\text{ is a strictly positive singleton}\}
     =D_{U,0}.                                             \tag{14}
\]

The converse in (14) is important: a positive dependence of the ordinary
four-set makes its residual determinant zero; a dependence of the
localization three-set makes the determinant after adjoining its residual
normal zero.  Hence no points away from `H_f` enter the support stratum.
At an intersection with other residual walls, additional positive witnesses
may appear in the full Gordan polytope, but the certified nonzero minor keeps
the selected support at rank `|U|-1`.  Its coordinate face therefore remains
a vertex.  There is no hidden rank-drop stratum to add to (14).

The proof of (9) is local to the reoriented rows in `U`: support-plane motion
multiplies those rows by positive scalars and never uses the extension axioms
for signs outside `U`.  It therefore applies to (14) even when the aligned
support signs have not been extended to a valid global extension signature.
Since `|U|` is four in the ordinary case and three in the localization case,
the same three-dimensional residence motion gives

\[
                    \boxed{H_c^q(H_f;R)=0\qquad(0\le q\le2)}.   \tag{15}
\]

This holds for every coefficient ring `R`.  More generally, the proof gives
(15) for every rank-one coefficient system pulled back from the residence
quotient of Section 2, including the orientation systems used by the
coordinate-face filtration.  It does not assert vanishing for an arbitrary
twisted local system which is not known to descend through that quotient.

Thus individual active factor boundaries have no compact-support cohomology
in degrees zero through two.  This statement does not pass automatically to
unions of factor walls and does not determine the signed frontier maps
between their intersections; the exact no-go is recorded in
`DIAG3_PAIR_DIFFERENTIAL_ENDS.md`.

## 5. Scope for diagonal three

For three signatures, the coarse compact-support Mayer--Vietoris complex in
total degree two now has a zero single-block term.  The remaining obligations
are still global and cannot be mixed with fixed-support calculations without
a functorial comparison:

* degree-one compact-support classes of pair-bad intersections; and
* compact components of triple-bad intersections, together with their
  incidence differential if they are not killed termwise.

The joined block-Gordan relative three-skeleton is the cover-correct place
to compute those terms and their cancellations.

## 6. Replay

Run

```console
PYTHONDONTWRITEBYTECODE=1 python \
  ai/omreal/verify_derived_wall_sides.py
PYTHONDONTWRITEBYTECODE=1 python \
  ai/omreal/verify_diag3_single_bad_two_skeleton.py
```

The first checker proves the fixed-cofactor identities for all thirteen
residual support orbits and all `84,840` labeled walls.  The second reuses
that exact certificate table without rerunning its symbolic determinant
expansions.  It checks the ordinary/localization partition, support sizes,
selected ranks and three-dimensional vertex motion, in addition to the
augmented-rank support bounds, sharp incidence inequalities, and exact
total-degree vanishing table.  The geometric content is the support-plane
and compact-support argument above.
