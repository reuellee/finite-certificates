# Relative-label residual-pair theorem

## Result

The relative-label gap in the residual-wall Jacobian program is now finite
and almost completely certified.

The exact global census has `84,840` labeled residual determinant
occurrences.  After dividing parent-bracket units, these give `26,740`
distinct geometric residual factors.  Under relabeling of the eight parent
elements, the factors form six orbits:

| canonical orbit label | factors |
|---:|---:|
| 36 | 840 |
| 38 | 280 |
| 48 | 420 |
| 49 | 10,080 |
| 50 | 10,080 |
| 51 | 5,040 |
| **total** | **26,740** |

The orbit labeled 36 contains canonical types
`36,37,39,41,44,46,47`; types 46 and 47 are already the same localized
factor.  The orbit labeled 38 also contains canonical type 42.  The other
four displayed types give separate factor orbits.

There are exactly

\[
                  \boxed{9,476}
\]

unordered `S_8`-orbits of pairs of **distinct** residual factors.  Of these,
`9,361` have an exact proper escape certificate:

| certificate | pair orbits |
|---|---:|
| bracket-product minor in the primary canonical presentation | 7,217 |
| bracket-product minor after another canonical presentation | 1,091 |
| bracket-product minor after full stabilizer-frame exhaustion | 918 |
| common affine-translation escape | 124 |
| common weighted-torus escape | 4 |
| type-`(49,49)` fiber-linear saturation | 7 |
| **certified noncompact** | **9,361** |
| honest residue | **115** |

Thus every connected component of the common zero set is noncompact for
`98.786%` of all relative-label factor-pair orbits.  This is a theorem about
the exact pair equations, not sampled parent charts.

The remaining 115 orbits are concentrated in the last three factor families:

| unordered factor-orbit types | residue |
|---|---:|
| `(49,50)` | 6 |
| `(49,51)` | 12 |
| `(50,50)` | 32 |
| `(50,51)` | 38 |
| `(51,51)` | 27 |
| **total** | **115** |

No residue is asserted to contain a rank drop or a compact component.  It
means only that the four certificate families above did not settle it.

## 1. The factor action and pair-orbit census

Let `D_P` be the determinant of the four derived normals indexed by a
labeled residual occurrence `P`.  The global factor certificate writes

\[
                 D_P = u_P q_P,
\]

where `u_P` is a product of nonzero parent brackets and `q_P` is primitive.
Two occurrences define the same geometric wall precisely when their
primitive factor IDs agree.

Relabeling must descend from occurrences to factor IDs.  This is checked
exactly on the seven adjacent transpositions generating `S_8`: for every
factor, all of its 1, 2, 15, or 65 labeled occurrences are sent to one common
factor ID.  Hence the induced action on the `26,740` factors is well defined.

Anchoring one factor at a representative and quotienting the second by its
stabilizer gives the following ordered counts:

| first orbit | ordered pair orbits |
|---:|---:|
| 36 | 654 |
| 38 | 255 |
| 48 | 361 |
| 49 | 6,808 |
| 50 | 6,913 |
| 51 | 3,435 |

Canonicalizing under pair reversal gives `9,476` unordered distinct pairs.
An independent Burnside calculation checks the same answer.  If `f(g)` is
the number of factors fixed by `g`, the number of unordered distinct pairs
fixed by `g` is

\[
 {f(g)\choose2}+\frac{f(g^2)-f(g)}2.
\]

Summing this expression over the 22 conjugacy classes of `S_8` and dividing
by `40,320` again gives `9,476`.  The ordinary fixed-point average gives the
six factor orbits above.

## 2. Why changing the projective frame is legitimate

The earlier canonical theorem found a bracket-product Jacobian minor for all
66 pairs among twelve displayed formulas.  That calculation did not cover a
general relative labeling.  It also fixed one projective frame unnecessarily.

On the uniform realization locus, any four parent columns form a basis.
Relabeling the columns and renormalizing the chosen four columns to `I_4`
therefore gives a global semialgebraic diffeomorphism between normalized
parent cells.  Every denominator in this coordinate change is a parent
bracket and is nowhere zero in the cell.  A labeled residual determinant is
carried to its relabeled primitive factor times another such bracket unit.

Consequently it is enough to find a fixed nonzero Jacobian minor in **one**
projective presentation of a factor pair.  The verifier first uses the
primary representatives, then every other canonical formula in the same
factor orbit, both pair orders, and finally every frame in the stabilizer of
the anchored factor.  It expands every claimed identity over `ZZ`; no
floating-point rank test is used.

For `9,226` pair orbits this finds variables `x_i,x_j`, an integer `c`, and
parent brackets `B_1,...,B_m` such that

\[
 \frac{\partial(q_1,q_2)}{\partial(x_i,x_j)}
                       = c\prod_k[B_k].                         \tag{1}
\]

The right side never vanishes on a uniform parent cell.  The fixed-minor
lemma from `RESIDUAL_STRATUM_NONCOMPACTNESS.md`, with `(n,k)=(9,2)`, proves
that every component of `q_1=q_2=0` is a noncompact smooth seven-manifold.

## 3. Affine and torus escape certificates

The fixed-minor test is sufficient, not necessary.  Two further exact
certificates settle 128 of its 250 residual orbits.

### 3.1 Common affine translations

For 124 pair orbits, in some checked projective frame there is a primitive
nonzero integer vector `v` satisfying the polynomial identities

\[
                     D_vq_1=D_vq_2=0.                           \tag{2}
\]

Thus the entire affine line `x+t v` preserves both equations.  Its
intersection with an open parent cell has a component which is an open
interval containing `t=0`.  If the interval is bounded it approaches the
parent boundary; if it is unbounded it escapes to infinity.  Either way it
is a proper curve in the same common-zero component, so that component is
not compact.

The verifier obtains `v` by exact rational row reduction on the coefficient
matrices of all nine partial derivatives and substitutes it back into both
directional derivatives.  A coordinate omitted by both factors is included
as the simplest special case.

### 3.2 Common weighted tori

For four further pair orbits there is a primitive nonzero integer weight
vector `w` for which every monomial of `q_r` has one common `w`-weight
`d_r`, separately for `r=1,2`.  Hence

\[
 q_r(e^{w_1t}x_1,\ldots,e^{w_9t}x_9)
                         =e^{d_rt}q_r(x).                        \tag{3}
\]

Every free coordinate `a,...,i` is, up to sign, a parent bracket in the
standard frame, so uniformity makes all nine coordinates nonzero.  The
nonzero weight vector therefore defines a nonconstant, injective curve.
Intersecting it with the open parent cell gives the same proper-interval
escape as above.

### 3.3 Type-`(49,49)` saturation and fiber-linear escape

The seven type-`(49,49)` residues admit a common graph reduction after an
exact stabilizer reframe.  The first wall is

\[
                   q_{49}=bf+d-b-f=0,
\]

so substitute `d=b+f-bf` into the second factor and call the primitive
restricted polynomial `r`.  In all seven cases the exact localized critical
ideal

\[
 \langle r,r_a,r_b,r_c,r_e,r_f,r_g,r_h,r_i\rangle:
                 \left(\prod_B[B]\right)^\infty
\]

is the unit ideal.  Bounded integer pseudo-reduction needs at most 22 basis
elements and 19 S-pairs.  Hence the original two gradients have rank two
throughout the uniform common-zero locus.

Moreover, every restricted `r` is affine-linear in `g`.  If the `g`
coefficient vanishes at a zero, the whole local `g`-fiber gives a proper
escape.  If it does not vanish on a hypothetical compact component,
projection dropping `g` maps that component locally diffeomorphically to a
nonempty subset of `R^7` which would be both open and compact, an
impossibility.  Thus all seven pair-wall components are noncompact.  See
`DIAG2_PIVOT_49_PAIR_SATURATION.md` and its exact verifier.

## 4. Exact verification

Run

```console
PYTHONDONTWRITEBYTECODE=1 python \
  ai/omreal/DIAG2_PIVOT_LABELED_PAIR_ORBITS_VERIFY.py --all-frames
```

The checker independently reconstructs:

1. all `84,840` labeled residual occurrences and `26,740` factor IDs from
   the pinned global factor certificate;
2. equivariance of factor equality under generators of `S_8`;
3. both the anchored and Burnside `9,476`-orbit censuses;
4. every bracket-product Jacobian identity in every selected frame;
5. every affine directional-derivative identity; and
6. every weighted-homogeneity identity.

The full run is intentionally exhaustive and is assigned its own CI job.
Its pinned pre-saturation semantic digest covers the ordered orbit table,
chosen certificates, affine directions, torus weights, and residue:

```text
08d948e990c21a1ab7520e72f1ce885f36652273d953b95edb4caeba90ad7263
```

That checker deliberately stops at its 122-orbit three-family residue.  Run

```console
PYTHONDONTWRITEBYTECODE=1 python \
  ai/omreal/verify_diag2_pivot_49_pair_saturation.py
```

to reconstruct the seven type-`(49,49)` cases, their stabilizer-equivalent
targets, every localized ideal trace, and the fiber-linearity check.  The two
verifiers together prove the `9,361/9,476` theorem above.

## 5. Consequence and boundary

This closes the former relative-label caveat for all but 115 exact pair
orbits and removes every pair residue involving factor orbits 36, 38, or 48.
It also removes the entire type-`(49,49)` slice.
It is a substantial input to the signed residual-wall transition graph.

It does **not** promote diagonal two.  Noncompact individual wall and
pair-wall strata can still assemble into a compact simultaneous-bad
component through a cycle of chambers, wall faces, and witness transfers.
The remaining proof target is therefore global acyclicity of that decorated
transition complex.

The bounded local task named above -- saturating the Jacobian ideals of the
115 residue orbits -- is now mostly done. The six `(49,50)` cases close in
`DIAG2_PIVOT_49_50_PAIR_SATURATION.md` (four by saturation, two by a cheaper
argument below). That cheaper argument turns out to generalize: a
single-variable affine-fiber refinement of the fixed-minor lemma, needing no
ideal saturation at all, closes 6,886 of the 6,890 candidate pairs across
all five hard factor-type families in `DIAG2_AFFINE_FIBER_RESIDUE_CLOSURE.md`
-- taking the honest residue from 115 to exactly four pairs:
`(50,7861),(50,7977),(50,12128),(50,20046)`, independently reconfirmed
unresolved by every certificate family here. Failure of a bounded
certificate search must continue to be recorded as residue rather than as a
geometric obstruction -- these four remain exactly that, not a rank drop or
a compact component. None of this closes the transition-graph acyclicity
question above; it only shrinks the population of pair-wall pieces that
question would need to glue.
