# Type-(49,49) pair saturation

## Result

The seven type-`(49,49)` cases left by the relative-label pair audit are now
settled exactly.  Their localized Jacobian ideals all saturate to the unit
ideal, so the two residual gradients have rank two everywhere on the uniform
common-zero locus.  A fiber-linear argument then proves that every connected
component of every one of the seven pair walls is noncompact.

At this checkpoint, the result raised the exact relative-label pair theorem
from `9,354` to

\[
                         \boxed{9,361/9,476}
\]

certified noncompact pair orbits (`98.786%`) and reduces the honest residue
from `122` to `115`.  In particular, no type-`(49,49)` pair remains.

The later iterated affine-fiber theorem in
`DIAG2_PIVOT_ALL_PAIR_FIBERS.md` subsumes these seven noncompactness results
and settles all `9,476/9,476` pair orbits.  The saturation here remains the
stronger independent smoothness certificate for this slice.

This is a local pair-wall theorem.  It does not promote diagonal two: compact
simultaneous-bad sets can still be assembled through decorated cycles of
different wall chambers and witness transfers.

## 1. Canonical graph reduction

Put the first factor into its canonical type-49 projective frame.  Its
primitive equation is

\[
                    q_{49}=bf+d-b-f=0,
\]

so its wall is the polynomial graph

\[
                         d=b+f-bf.                    \tag{1}
\]

The full stabilizer-frame audit identifies the seven residue representatives
by second-factor ID.  For the saturation calculation, each is moved by a
stabilizer of the first factor to the displayed lower-complexity target:

| residue factor | target factor | terms after (1) | degree |
|---:|---:|---:|---:|
| 8213 | 22372 | 26 | 5 |
| 8217 | 25501 | 16 | 5 |
| 8220 | 20698 | 26 | 5 |
| 8221 | 20753 | 16 | 5 |
| 17797 | 21972 | 22 | 6 |
| 17802 | 21863 | 52 | 6 |
| 21722 | 21862 | 52 | 6 |

The checker verifies that every target lies in the appropriate stabilizer
orbit, so this change of presentation preserves the first wall and the pair
geometry.  If `q` is the target polynomial and `r_raw` is its literal
restriction under (1), it also constructs and expands an exact identity

\[
                    q-r_{\rm raw}=q_{49}Q.            \tag{2}
\]

The polynomial `r` used below is the primitive normalization of `r_raw`;
they differ only by a nonzero integer scalar.

## 2. Uniform-locus saturation

Use the eight free coordinates

\[
                       (a,b,c,e,f,g,h,i).
\]

On the graph (1), the two original gradients lose rank precisely at a
critical zero of `r`.  Thus the relevant ideal is

\[
 J_r=\left\langle r,r_a,r_b,r_c,r_e,r_f,r_g,r_h,r_i\right\rangle.
                                                               \tag{3}
\]

Let `U` be the product of the 62 nonconstant parent brackets restricted to
(1).  The exact calculation proves

\[
                            (J_r:U^\infty)=(1)         \tag{4}
\]

for all seven targets.

The verifier performs integer pseudo-reduction in graded reverse
lexicographic order `giahcefbd`.  Every division used for localization is
checked as exact polynomial division by a restricted parent bracket.  Five
cases reduce to a bracket unit while the original generators are inserted;
one requires one S-pair, and the largest requires only 19 S-pairs:

| residue | basis elements, including `1` | S-pairs | terminal bracket unit |
|---:|---:|---:|---|
| 8213 | 7 | 0 | `[1247][1267]` |
| 8217 | 8 | 0 | `[1237][1468]` |
| 8220 | 9 | 0 | `[1247][1467]` |
| 8221 | 7 | 0 | `[1247][1267]` |
| 17797 | 5 | 0 | `[1246][1348][2367][2378]` |
| 17802 | 10 | 1 | `[1257][2468][1478]` |
| 21722 | 22 | 19 | `[1248][1257][4678]` |

The terminal product is the final localized remainder after the earlier
exact reductions, not a claim that one original derivative equals that
product directly.  The checker pins a semantic SHA-256 digest for every full
trace, including every intermediate polynomial and every bracket division.

Equation (4) proves that no uniform critical zero exists.  Consequently all
seven common walls are smooth seven-manifolds in every parent cell where
they are nonempty.

## 3. Fiber-linear noncompactness lemma

Every restricted target `r` is affine-linear in `g`:

\[
                         r(x,g)=A(x)g+B(x),             \tag{5}
\]

where `x=(a,b,c,e,f,h,i)`.  This gives a proper escape without requiring one
globally fixed Jacobian minor.

Suppose a connected component `C` of `r=0` in an open parent cell were
compact.  If `A(x)=0` at a point of `C`, then (5) and `r=0` also give
`B(x)=0`.  The entire `g`-fiber is therefore in the algebraic zero set.  The
component of that fiber inside the open parent cell runs either to infinity
or to a parent-bracket boundary, contradicting compactness of `C`.

Hence `A` is nonzero everywhere on `C`.  Projection dropping `g` is then a
local diffeomorphism from `C` to `R^7`.  Its image is nonempty and open, but
it is also compact because `C` is compact.  No nonempty subset of `R^7` is
both open and compact.  This contradiction proves that `C` is noncompact.

The argument is componentwise and applies in every parent chirotope cell.
Together with projective frame transport, it settles all seven original
pair orbits.

## 4. Exact verification

Run

```console
PYTHONDONTWRITEBYTECODE=1 python \
  ai/omreal/verify_diag2_pivot_49_pair_saturation.py
```

The checker independently verifies:

1. that the seven IDs are exactly the earlier type-`(49,49)` residues under
   the previous three certificate families;
2. that every chosen target is stabilizer-equivalent while the canonical
   first factor remains fixed;
3. all graph-remainder identities (2);
4. the 62 restricted parent-bracket units;
5. every pseudo-reduction, S-polynomial, and exact bracket division leading
   to (4); and
6. affine-linearity in `g` for every restricted target.

Expected final status:

```text
THEOREM all seven type-(49,49) pair-wall components are smooth and noncompact
HISTORICAL CHECKPOINT certified pair orbits: 9361/9476; residue: 115
CURRENT PAIR THEOREM certified pair orbits: 9476/9476; residue: 0
CAVEAT diagonal two still requires global decorated transition-cycle acyclicity
```

## 5. Historical residue and current boundary

At this checkpoint, the remaining pair residue was

| unordered factor-orbit types | residue |
|---|---:|
| `(49,50)` | 6 |
| `(49,51)` | 12 |
| `(50,50)` | 32 |
| `(50,51)` | 38 |
| `(51,51)` | 27 |
| **total** | **115** |

The later affine-fiber theorem closes all 115 of those cases without needing
smoothness.  The global proof target remains acyclicity of the
component-decorated transition complex.
