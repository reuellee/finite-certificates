# Third diagonal: projective-column fiber compression

## Outcome

There are exactly `79,102,449` unordered triples of distinct localized
residual factors modulo simultaneous `S8`.  This note proves component
noncompactness for exactly

```text
74,767,375  jointly affine after a projective reframe
    26,927  minimum moving-label support-union degree two
 2,410,414  minimum moving-label support-union degree three
-----------
77,204,716  theorem-safe total
```

The remaining `1,897,733` orbits have minimum support-union degree four.
The structural arguments in Sections 1--4 do **not** claim them.  In
particular, neither a generic four-pencil argument nor the
primitive-polynomial affinity mask closes that residue.

A later exact computational checkpoint closes two disjoint subsets of this
degree-four bucket:

```text
    12,333  sequential three-coordinate unit graphs
    65,550  parent-unit Jacobian minors in some role frame
        61  parent-unit constant-shear minors in frame 1119
-----------
    77,944  additional degree-four orbits
```

Thus the current theorem-safe total recorded by this note and its checker is

```text
77,282,660  componentwise-noncompact triple-factor orbits
 1,819,789  unresolved degree-four orbits
```

The compact identity replay uses only the `79` role frames which actually
carry certificates.  Exhaustiveness of the unit-minor *search* is a distinct
statement and used all `1,120` frames of
`S8/(S{2,3,4} x S{6,7,8})`; the `79` witnesses are not asserted to form a
smaller group quotient.

The exact Sections 2--4 replay is

```bash
python ai/omreal/verify_diag3_projective_column_fiber_scan.py
```

The compact exact positive-certificate replay is

```bash
python ai/omreal/verify_diag3_projective_column_fiber_scan.py --morse-only
```

The separate one-frame constant-shear replay is

```bash
python ai/omreal/verify_diag3_frame1119_constant_shear.py
```

To recheck disjointness from the `12,333` triangular closures and regenerate
the pinned post-triangular source, also pass the union-degree-four bucket
exported by the main checker:

```bash
python ai/omreal/verify_diag3_projective_column_fiber_scan.py \
  --morse-only --morse-union4 /path/to/diag3_union_degree4.bin
```

The full run constructs a `40,320 x 26,740` factor-action table and needs
about 4 GiB of memory.  A saved scanner residue can be checked without that
table by

```bash
python ai/omreal/verify_diag3_projective_column_fiber_scan.py \
  --residue /path/to/affine_residue.bin
```

The companion OpenMP scanner is
`verify_diag3_projective_column_fiber_scan.cpp`.

## 1. Equations and unit discipline

Work in a uniform parent cell of the standard nine-coordinate chart.  A
labeled residual occurrence with four support triples `E=(T1,T2,T3,T4)` has
the geometric equation

\[
 D_E=\det(n_{T_1},n_{T_2},n_{T_3},n_{T_4})=M_Eq_f,             \tag{1}
\]

where `M_E` is a product of parent brackets and is nowhere zero in the cell,
and `q_f` is the primitive localized factor.  Thus either equation has the
same zero set in the cell.  Occurrences may be selected independently for
the three factors.

Affinity of a particular polynomial representative is not invariant under
multiplication by a parent unit.  The scanner therefore aggregates the
84 coordinate-three affinity bits over the primitive equation and every
full occurrence equation (1), before intersecting the three factor masks.
For this exact census the occurrence equations add no bit to the primitive
masks; the checker asserts this census-specific equality.  It is not used as
a general invariance principle.

## 2. Square affine fibers

Let `Omega` be a nonempty open subset of `R^n`, with `n>0`, and let `D` be
open in `Omega x R^k`.  If

\[
                 F(w,z)=A(w)z+b(w),\qquad z\in\mathbb R^k,     \tag{2}
\]

then every component of `D intersection Z(F)` is noncompact.  Suppose instead
that `C` were a compact component.  If `C` met `det(A)=0`, then at such a
consistent point the fixed-base solution would be a positive-dimensional
affine space.  Its intersection with the open fiber has a noncompact
semialgebraic component through the point.  That fiber component is closed in
the fixed-`w` zero set (semialgebraic components are closed), and the fixed-`w`
zero set is closed in `D intersection Z(F)`.  It is therefore a closed
noncompact subset of `C`, a contradiction.  If `C` avoids `det(A)=0`, (2) is
the graph of `-A(w)^{-1}b(w)`.  The graph homeomorphism identifies `C` with a
component of a nonempty open subset of the positive-dimensional base.  Such
a component is open in `R^n` and is noncompact, again a contradiction.

Apply this with `k=3` and the other six chart coordinates as base.  The
scanner exhausts all `40,320` projective reframings of each triple orbit and
all aggregated occurrence masks.  Its exact result is

| presentation | triple orbits |
|---|---:|
| standard frame | `65,557,134` |
| some `S8` frame | `74,767,375` |
| no affine-three frame | `4,335,074` |

The full-scan input digest is

```text
76956ac6ab5a9d67bf9ad74f46719a3f9612ebfed22696eae1e797f70f96bf63
```

and the ordered pair-bucket residue digest is

```text
c8cac9809ceaea9438e0d5219f3bca0ed0173f544d6b53d8b33f8a8bce5ee754
```

The four earlier hard triples are pinned as negative canaries and exhaust
all `40,320` frames without success.

## 3. Moving one projective column

Fix a label `p`.  If an occurrence support triple containing `p` is
`{u,v,p}`, its normal ray records the plane through the fixed line `uv` and
the moving point `p`.  For three selected occurrences, let `r` be the number
of distinct incident support triples in their union.

If `r<=2`, hold the corresponding normal rays fixed.  The moving point then
lies in the intersection of at most two projective planes, which has
dimension at least one.  Every selected determinant in (1) is preserved up
to multiplication of a row by a nonzero scalar.  The intersection of this
residence space with the uniform parent cell is an open semialgebraic cell.
The component through the original point contains an open interval that
either escapes in the chart or ends on a parent-bracket wall.  Hence it is
noncompact.  This closes exactly `26,927` residue orbits.

The argument depends on support incidence, not polynomial degree.  A factor
may contain two of the moving normals and be quadratic in chart coordinates;
this is why `26,927` orbits survive the affine-three scan even though their
support-plane residence motion is immediate.

## 4. The degree-three forest lemma

Suppose `r=3`.  If the three selected plane-normal rays are linearly
dependent, their fixed planes meet in dimension at least one and the
residence argument of Section 3 applies.  Assume they are independent.

Each plane belongs to the projective pencil through its fixed support line.
After choosing bracket-ratio affine coordinates on the three pencils, the
map from the moving column to its three plane coordinates is a semialgebraic
homeomorphism onto an open subset of `R^3`: three independent planes have a
unique common projective point, and the uniform parent conditions remove the
degenerate pencil values.  Each selected determinant is multiaffine in these
three pencil coordinates.

Form the bipartite graph whose left vertices are the three factor equations
and whose right vertices are the three pencil coordinates.  Join an equation
to a coordinate precisely when that occurrence uses the corresponding
normal.  Up to a permutation of factor rows, the incidence partitions of
the deterministically selected minimum-degree witnesses and their counts are

| column-color partition | orbits |
|---|---:|
| `(1,1,2)` | `1,388,106` |
| `(1,1,6)` | `250,135` |
| `(1,2,3)` | `174,811` |
| `(1,2,5)` | `590,856` |
| `(1,2,7)` | `4,062` |
| `(1,3,6)` | `2,444` |

Here a color is the three-bit set of equations using one normal.  All six
selected witness graphs are forests.  Only existence of one such occurrence
witness is used; this is not a classification of every minimizing witness.

Argue by induction against a hypothetical compact component `C`, peeling a
leaf pencil variable `x`.  Its unique equation has the form

\[
                         A(y)x+B(y)=0.                           \tag{3}
\]

At a solution with `A=0`, also `B=0`.  Hold every remaining coordinate fixed
and take the **full connected component** through the point of this pencil
slice in the original zero set.  It is closed in the fixed-coordinate slice,
and that slice is closed in the zero set.  If the pencil interval exits at a
parent wall or at infinity, this closed slice component is noncompact.  Its
only other possible frontier inside the parent cell is the dependent-plane
locus; there the dependent residence fiber from the first paragraph of this
section supplies a closed noncompact subset of the same component.  Thus a
compact `C` cannot meet `A=0`.  On `C` one may therefore graph
`x=-B/A` and delete that leaf and equation.  This is a homeomorphism on the
relevant nonzero-slope locus, so compactness and component membership are
preserved at every prior graph elimination.

For `(1,1,2)`, `(1,1,6)`, and `(1,2,3)`, the forest has no matching that
covers all three pencil variables.  Repeated peeling therefore leaves a
full fixed-coordinate pencil-slice component, handled by the preceding
closed-slice argument.  For
`(1,2,5)`, `(1,2,7)`, and `(1,3,6)`, peeling either encounters the zero-slope
escape above or graphs all three pencil variables over a nonempty open subset
of the six-dimensional base.  That graph cannot have a compact component.

Thus all `2,410,414` union-degree-three residue orbits have componentwise
noncompact triple zero sets.  The deterministic bucket digest is

```text
694cbdd93f49a0df5fb4f5c38b3a969286b56b914270ab8933dd765458699bd7
```

The degree-two bucket digest is

```text
0c5413d8fa0de835f3ba777c00d2c57527ff828faf8b1a4c7856384f66421616
```

## 5. Honest degree-four frontier

The unresolved deterministic degree-four bucket has digest

```text
54b03c31910de606b80f9dcc448ce3dde93063a8dbc3f2dbcaa7a02901df0303
```

Its two minimum-incidence patterns are

| partition | factor degrees | orbits |
|---|---:|---:|
| `(1,1,2,2)` | `(2,2,0)` | `1,009,177` |
| `(1,1,2,4)` | `(2,1,1)` | `888,556` |

For one prescribed extension-signature triple, the nested support-drop
induction only reaches factor triples which match the three signatures by
aligned occurrences.  This is a valid family-specific pruning, but it does
not add a sign sector to the zero set.  The local aligned-tope lemma in
`DIAG3_TRIPLE_FACTOR_REDUCTION.md` proves that every nonempty regular
residual occurrence wall admits an actual extension-tope completion of its
wall-circuit signs.  At a simultaneous triple the three completions are
independent.  Thus fixed wall-circuit positivity and the three separate
extension Grassmann--Pluecker systems impose no mixed coefficient identity
which could exclude either incidence core or a compact oval within it.

The exact internal-discriminant checker now pins this distinction on a
realizable canary.  Its factor triple

```text
(5563,16134,19284)
```

has a selected moving-label-3 core

```text
123/145/246/378
126/257/367/458
245/157/348/168
```

with incidence colors `(1,1,2,4)`.  At its exact degree-six algebraic point
all three factors vanish, all 62 nonconstant parent brackets are nonzero,
and the remaining quadratic has a double root across which its discriminant
changes sign.  Hence the `(2,1,1)` core is not removed by realizability or
by parent-cell sign constancy.  This is an internal branch, not a compact
component.

Adding the four-plane common-point carrier creates respectively a
three-row/four-column augmented core and a `K2,2` core.  A bare
four-pencil/Pluecker argument cannot rule out compact ovals: there is an
exact abstract specialization whose carrier equation is
`1-x^2-z^2=0` after the two factor equations graph `y=x` and `w=z`.

There is also an actual discriminant-critical canary found by a separate
exact CAS diagnostic.  It is recorded to prevent reuse of a false generic
conic shortcut, but it is not replayed by the theorem checker above and is
not used in the `77,204,716` proof.  The factor triple

```text
(2277,390,22507)
```

has selected supports

```text
123/124/345/367
234/135/268/578
246/167/158/478
```

After two exact graph eliminations, the remaining quadratic discriminant
strips only the parent factor `[3578]^2`.  Its nonunit factor has degree 14,
`4,347` terms, is irreducible over `Z`, and has digest

```text
c3641d1f9c138ef9532ba49bad5c64c8b48feb2e546f2e0fbfaf936ed11e3376
```

Consequently the next valid endpoint is an occurrence-specific Morse test,
not a generic conic-sign assertion.  For a chosen chart coordinate `b`, the
desired certificate is

\[
 \left\langle q_1,q_2,q_3,
   \text{all }3\mathbin{\times}3\text{ minors of }J_{\ne b}\right\rangle
 :\left(\prod_B[B]\right)^\infty=\langle1\rangle .             \tag{4}
\]

A compact component would have a `b`-critical point, so (4) excludes it.
Classifying (4) must retain the complete colored `3 x 4` occurrence supports
and their nonincident triples.  The coarser incident-edge key is not a valid
algebraic quotient.

### 5.1 Exact triangular and role-frame checkpoint

The degree-four bucket first admits `12,333` exact triangular graph
certificates.  For an ordered factor triple, choose distinct coordinates
`x,y,z` so that the first equation has a parent-unit derivative in `x`, the
second and third are independent of `x`, the second has a parent-unit
derivative in `y`, the third is independent of `y`, and the third has a
parent-unit derivative in `z`.  Successive graph elimination is then a
homeomorphism onto an open subset of the six remaining coordinates.  The
compact feature artifact records only zero derivatives and derivatives which
exactly factor into parent brackets; the full replay rechecks every positive
feature by integer polynomial division.  It leaves `1,885,400` rows, with
digest

```text
1c64017faad2173a3552dd70427d893c6ad4e39f31075ef9941c871f11184949
```

On that residue, let `q=(q1,q2,q3)` and let `M_I` be a `3 by 3` Jacobian
minor in coordinate columns `I`.  If

```text
M_I = plus-or-minus a product of nonzero parent brackets,
```

choose any chart coordinate `b` outside `I`.  Then `J` with the `b` column
deleted has rank three throughout the uniform zero set.  A compact component
would have a maximum of `b`; the Lagrange critical condition there forces
that rank below three, a contradiction.  This proves component
noncompactness without a global choice of escape direction.

The exact role quotient has `1,120` frames.  A modular derivative-wedge
screen proposed `65,624` candidate minors.  Every counted proposal was then
divided exactly over `Z` by the 62 parent brackets:

| result | count |
|---|---:|
| exact parent-unit identity | `65,550` |
| rejected modular proposal | `74` |
| targeted exact rescue | `0` |

There are `79` certificate-carrying frames and the last first appears at
frame `815`; frames `816` through `1119` form a `304`-frame zero tail after
already-certified rows are filtered.  The positive theorem count needs only
the `79` stored witness frames.  The assertion that no further unit-minor
certificate occurs in another role frame uses the full `1,120`-frame sweep;
the long zero tail is not a new symmetry quotient.

The compact certificate contains all `65,550` original triples, role-frame
indices, minor columns, signs, and parent-bracket products.  Its digest is

```text
afe01d6d94bc4b8ce133cbe0d14ceb01d9dd72514f9ed7a59b73d5f6b4299734
```

For audit and resumability, the final raw construction-checkpoint digests
are

```text
closed rows       057e50b205cae8f8aedb45bc968260c4ed4735ab958c48f52b504095706f711f
exact identities  3e4e3311d5ceed97a41e391bfabed3b458de5412dcf7bf84736a999e651ebf59
frame log         123c9f13e0a6cbd4d07a33b723f8f0d3d47a247393296ad11986327cbea5aaff
false proposals   8e42f1d8f51ab77b1d74262bd395704da8d49e3a6e65bd7e69d7abc1b197eafd
```

Those four raw files are construction logs and are not replayed by the
compact tracked checker.  Its theorem claim uses only the positive records,
each of which it reconstructs and divides exactly over `Z`.  The recorded
`1,120`-frame exhaustion and `74` rejected modular proposals document
maximality of this particular search, not an additional positive theorem
input.

### 5.1 Constant-coordinate shears in frame 1119

For the last role frame, a second screen tested every pair of coordinate
minors sharing two columns.  With orientation signs absorbed into the
display, such a combination is

\[
 M_{abc}\mathbin\pm M_{abd}
 = (dq_1\wedge dq_2\wedge dq_3)
   (e_a,e_b,e_c\mathbin\pm e_d).                       \tag{28}
\]

Thus a parent-unit value of (28) is a rank-three certificate on one fixed
constant three-plane.  Choose a nonzero constant linear functional `h`
annihilating that plane.  On a compact component of the common zero set,
`h` has a critical point.  At such a point the restriction of the Jacobian
to `ker dh` has rank at most two, while the certified three-plane lies in
`ker dh` and has rank three, a contradiction.  This is the same compact
Morse argument as above and does not use a polynomial-dependent direction.

The frame-1119 screen tested `2,751,613,200` signed sums and differences.  It
returned `116` modular proposals; exact integer replay accepts all `116`,
which collapse to `61` distinct original triples.  None overlaps the prior
`65,550` compact Morse records.  The replay also checks all `40,320` affine
reframes of these rows, reconstructs their minimum support-union degree four,
and proves failure of the exact triangular feature test.  Thus source
membership and disjointness from every earlier layer are replayed rather
than inferred from the discovery log.  The tracked 61-record artifact has digest

```text
1cece61ff1a551faaeefc0062267e24266d264d9e19748d40fa5a74db9ce0be3
```

This is a positive theorem for one role frame and the displayed `+/-`
family.  It is not an exhaustive constant-`GL9` search, and it does not
extend the old `1,120`-frame maximality statement to sheared projections.

Together with Sections 2--4, this gives the theorem-safe total `77,282,660`
and leaves `1,819,789` degree-four orbits unresolved.  This checkpoint still
proves only component noncompactness, not `H_c^1` vanishing or signed
frontier incidence.

## 6. Scope

This note proves the needed `H_c^0` vanishing for the `77,282,660` listed
triple-factor orbits.  It gives no uniform `H_c^1` vanishing and no signed
frontier-incidence calculation.  The `1,819,789` remaining degree-four
orbits are a genuine obligation.
