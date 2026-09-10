# A ruled-quadric normal form for the 45 balanced pair presentations

## Statement and exact coverage

For every one of the45 balanced pair records in the authenticated
`original/AFFINE_PAIR_COVERAGE.json`, one can choose a moving parent label
and order the two occurrence quartets so that:

1. the first wall is a nonzero projective plane `L` in the moving point `x`;
2. the second wall is a smooth split projective quadric `Q`;
3. the plane section `C=L intersect Q` has a rationally defined, forbidden
   **smooth point** on two algebraic base charts; and
4. `C` may still be a reducible conic, and all such fibers are retained.

This holds over every uniform realization of the seven fixed parent labels,
and hence on every full-parent component where the corresponding residence
fiber is nonempty. It is a conventional geometric theorem supported by a
small exact check of its incidence hypotheses. It does not prove
`H_c^1` vanishing for the total pair-wall locus.

`REGULUS_GEOMETRY_GATE.json` contains306 qualifying ordered presentations
across all45 records. It is false that **every** degree-two pivot qualifies.
For example, type50 `123/145/246/378` with moving label3 has moving parent
lines12 and78, while both free triples145,246 miss both endpoints7,8.
No parent-unit skew certificate is claimed for that pivot. Every record has
other qualifying choices.

## 1. Notation

The linear occurrence quartet has one moving triple `eab` and three fixed
triples `E1,E2,E3`. Its determinant, evaluated with `y_e=x`, is denoted `P(x)`.
The quadratic quartet has moving triples `ecd,efg` and fixed triples `F1,F2`.
Write

`l1=span(y_c,y_d)`, `l2=span(y_f,y_g)`,
`l0=plane(F1) intersect plane(F2)`.

All spans in this note are projective. The seven fixed parents are uniform:
any four of their homogeneous columns are independent. In particular,
distinct fixed-parent planes are honest planes, and a fixed parent outside
a plane's three labels does not belong to that plane.

The checker records the following purely incidence-level hypotheses.

- Among `E1,E2,E3`, two share a parent excluded by the third.
- Some `Ei` meets `{a,b}` in one endpoint `j`, and another `Ei` excludes `j`.
- The pairs `{c,d}` and `{f,g}` are disjoint.
- For each of these pairs, one of `F1,F2` contains exactly one endpoint `j`,
  and the other fixed triple excludes `j`.

All uses of "excluded" here are literal label exclusions; uniformity turns
them into nonzero parent-bracket conditions.

## 2. The first determinant is an honest plane

The three fixed normal rows have rank3. Indeed, take two fixed planes sharing
an endpoint `j` absent from the third. Their intersection is a line containing
`y_j`. If the third normal were in their span, its plane would contain that
line and hence `y_j`, contradicting a nonzero parent bracket.

Let `p0` be the unique projective intersection of the three fixed planes.
Up to a nonzero scalar, the determinant is therefore

`P(x)=det(x,y_a,y_b,p0)`.

The second incidence condition shows `p0` is not on the parent line `ab`:
one fixed plane meets that line only at `y_j`, while another fixed plane
excludes `y_j`. Thus `P` is not the zero linear form. Its zero plane `L`
contains the whole parent line `ab`. No open-base stratum with `P` identically
zero has been silently discarded.

## 3. The second determinant is a smooth split quadric

The lines `l1,l2` are skew, since their four parent endpoints are independent.
The two fixed planes are distinct, so `l0` is a line. For each `li`, one fixed
plane meets `li` at a specified endpoint `y_j` and the other excludes `y_j`.
Consequently `l0` is disjoint from both `l1` and `l2`. We have three pairwise
skew real projective lines.

The determinant `Q(x)` vanishes on each of these lines. On `l1` or `l2`, one
moving normal row is zero. On `l0`, all four rows annihilate `x`, so their
four-by-four determinant is zero.

More explicitly, choose homogeneous coordinates `x=(u,v)`, with `u,v in R^2`,
so `l1={v=0}` and `l2={u=0}`. Because `l0` is skew to both, it is the graph
`v=T u` of an invertible two-by-two matrix. The two moving plane equations
are, up to nonzero fixed scalars, `det(v_x,v)=0` and `det(u_x,u)=0`. The two
fixed plane equations are an invertible linear recombination of `v-Tu=0`.
Their determinant gives

`Q(x)=k det(Tu,v)`, with `k!=0`.

After an invertible change of coordinates this is `u1 v2-u2 v1=0`. Its
projective gradient never vanishes. Thus `Q` is a smooth split quadric, not
merely a quadratic polynomial containing several real points. The fixed
scalar is nonzero because all changes of basis used above are invertible.
The three lines belong to one ruling of this quadric.

## 4. A forbidden smooth marker on every section

An honest plane cannot contain both skew lines `l1,l2`. On the base chart
where `li` is not contained in `L`, let

`r=L intersect li`.

If `li=span(y_c,y_d)` and `P` is the chosen linear form, a homogeneous formula
is

`r=P(y_d)y_c-P(y_c)y_d`.

It is nonzero precisely on that chart. The two charts cover every base.
The point belongs to `C=L intersect Q` and is forbidden for the moving
parent: placing `x` on a line of two fixed parents violates full-parent
uniformity.

The marker is a smooth point of the plane conic. The tangent plane to `Q`
at `r` contains the ruling line `li`. The plane `L` does not contain `li`,
so `L` is not the tangent plane at `r`; the section is transverse there.
This statement does not require the entire conic to be nonsingular. A
tangent plane section of a smooth split quadric is a pair of real lines;
its node can occur elsewhere, while `r` remains smooth.

Projection from `r` rationally parametrizes a smooth conic minus `r`. In the
reducible case, projection has one collapsed line component through `r` and
parametrizes the other component; both real line components must be retained
or treated separately. No such collapsed component is declared parent
infinity without an actual parent-bracket argument.

This construction applies to source573 as well:

`P=123/145/267/468`, `Q=178/258/347/356`.

Its lack of a forced **parent point** marker does not obstruct the parent-line
intersection marker above.

## 5. Stronger charts for 44 pairs with actual parent markers

The weaker incidence test in `CONIC_MARKER_GATE.json` gives a forbidden
actual parent marker for44/45 records,285 ordered presentations. Intersecting
that test with the smooth-quadric test leaves238 presentations covering the
same44 records. The sole exception remains source573.

For such a presentation, the actual parent marker `y_j` lies on one of
`l1,l2,l0`. Both ruling lines through `y_j` are entirely excluded by parent
uniformity. Its same-ruling line is either a fixed-parent line, or `l0`,
which lies in a fixed-parent plane. Its opposite-ruling line lies in the
plane spanned by `y_j` and a suitable other fixed-parent line. In either case
a parent bracket involving the moving point vanishes everywhere on that
line. The relevant three fixed labels are distinct because the incidence
conditions put `j` outside the other moving pair.

Therefore any line component of a reducible conic passing through this
actual parent marker is entirely forbidden. Projection from the marker has
no collapsed component inside the uniform parent residence. The remaining
uniform locus maps one-to-one to an open subset of the pencil of lines
through the marker, with a rational inverse, including across reducible
sections. Locally this identifies the total uniform locus with an open
subset of a `P^1` bundle over the six-dimensional fixed-parent base.

This is a chart theorem, not a compact-support vanishing theorem. Such open
subsets can still have changing interval components and nontrivial
`R^1 f_!` specialization. The actual conic-fiber splitting example being
checked by the original/falsifier tracks must not be removed by an assumed
single-interval or locally constant-component rule.

## 6. Scope of the remaining step

All45 balanced records now have a uniform ruled-quadric description and
forbidden smooth rational marker after selecting a certified pivot.
Neither this fact nor the44 stronger parent-marker charts proves the
remaining pair-wall `H_c^1` statement. The unresolved mathematical object
is the component/specialization sheaf for the actual parent residence,
including reducible conics, moving parent boundaries, and genuine infinity.
No original diagonal or source pair count is closed by this note.
