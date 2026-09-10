# Triple-bad escape track: a conic reduction and an exact fold

## Status

The original triple-bad no-compact-component obligation remains open. This
track closes **zero** of the 1,162,302 source residue orbits and claims no
change to 2/9. It proves exact geometric structure for the named presentation
(5563,16134,19284), canonical source row (5563,4373,23221), on **every**
uniform parent cell in that presentation. It also gives one exact uniform
point refuting an unbranched-projection shortcut.

The important surviving result is that one hard-canary equation is a
nonsingular projective conic throughout the parent cell. Its degeneracies
are products of named parent walls, so an entire troublesome degree-drop
branch is excluded exactly. This permits a six-variable critical-point
reduction retaining singular points. It does not decide the reduced system.

## Source and theorem scope

The original equations are the three `kind=factor` records in
`../inputs/DIAG3_triple_fullspace_critical_h1.json`, SHA-256
`c9244a47ded5736e7afe724a9914e75631a22b78653442e88c14f5c397919eb8`.
The normalized matrix is

\[
Y=\begin{pmatrix}
1&0&0&0&1&1&1&1\\
0&1&0&0&1&a&d&g\\
0&0&1&0&1&b&e&h\\
0&0&0&1&1&c&f&i
\end{pmatrix}.
\]

All 70 four-brackets are required nonzero, with each parent's specified signs.
No fixed witness, selector, discarded support face, sample-to-global inference,
or deletion of parent infinity enters the reduction below.

The inherited `DIAG3_TRIPLE_FACTOR_REDUCTION.md` already reduces triple-bad
compact components to at most three distinct residual-factor zero sets by a
nested support-drop induction. Its same-factor and two-factor cases are
already covered. Reproving those cases would not advance this track.

## 1. Exact nonsingular-conic theorem

Write the second equation as a conic in `(a,c)`:

\[
 q_2=Lac+Ma+Nc^2+Oc+P.
\]

Its coefficients include

\[
\begin{aligned}
L&=-e(f-1)(h-1),\\
M&=bf(f-1)(h-1),\\
N&=(e-1)(dh-d+g-h).
\end{aligned}
\]

If `C` is its homogeneous symmetric 3-by-3 conic matrix in `(a,c,z)`, direct
integer polynomial arithmetic proves

\[
4\det C=-L^2P+LMO-M^2N
=-bf(b-e)(e-f)(f-1)^2(h-1)^2(dh-d-eg+e+g-h).
\]

Every factor is a signed parent bracket:

| factor | exact bracket identity |
|---|---|
| `b` | `-[1246]` |
| `f` | `[1237]` |
| `b-e` | `[2467]` |
| `e-f` | `-[1257]` |
| `f-1` | `[2357]` |
| `h-1` | `-[2458]` |
| `dh-d-eg+e+g-h` | `-[4578]` |

Therefore the projective conic is nonsingular over both R and C on every
uniform parent cell. In particular it contains no projective line.

This is an all-parent identity for this **named factor presentation**. It
has not been classified over the remaining residue or used to close a whole
factor-type family.

## 2. Two global graphs and the degree-drop branch

The other two equations have global unit slopes:

\[
\partial_d q_1=i,\qquad \partial_c q_3=-g(d-e)(h-1).
\]

Thus throughout the parent cell one can solve

\[
 d=\frac{b(i-f)+fg}{i},\qquad
 c=-\frac{q_3|_{c=0}}{\partial_cq_3}.
\]

The second graph is affine in `a`. Substituting both into `q2`, and clearing
only the indicated parent-unit denominators, gives

\[
 P_*(a;y)=A(y)a^2+B(y)a+C(y)=0,
 \qquad y=(b,e,f,g,h,i).
\]

`HEIGHT_DISCRIMINANT_SYSTEM.json` records the exact 1,951-term numerator,
its coefficients, and the discriminant data in an executable sparse format.
`verify_conic_reduction.py` reconstructs it from the original factor records.

At a uniform point it is impossible to have `A=B=C=0`: this would mean the
line `q3=0` in the `(a,c)` plane lies in the nonsingular conic `q2=0`.
This is the exact disposition of the full degree-drop branch, not a generic
rank argument or an assumption that a leading coefficient never vanishes.
When `A=0` at a root, one consequently has `B!=0`, so the implicit function
theorem makes `a` a local function of the six base variables.

Even without the stronger determinant identity, an identically zero
quadratic would furnish a proper escape: with the base fixed only column 6
moves, on an affine line `(a,b,c(a))`; its strict-parent-sign residence
interval ends at a parent wall or at genuine coordinate infinity. The
nonsingular-conic identity proves that this fallback case never occurs in
the uniform cell.

## 3. Exact six-equation compactness criterion

Let `Z` be the common zero locus of these three factors in any normalized
uniform parent cell. Suppose a connected component `K` of `Z` were compact.
Choose a maximum of the coordinate `b` on `K`.

In the two-graph presentation, `P_*a` must vanish at this point: otherwise
`a` is a local graph over an open set in all six base variables, and `b`
can increase while preserving both factor equations and strict parent signs.
The previous section then implies `A!=0`.

Set `Delta=B^2-4AC`. At a double root,

\[
 a=-\frac B{2A},\quad \Delta=0,\quad
 \partial_v\Delta=-4A\,\partial_vP_*\quad
 (v=b,e,f,g,h,i).
\]

At a smooth maximum, the Lagrange condition says `dP_*` is proportional to
`db`, so its five derivatives other than `b` vanish. At an intrinsic
singular point all these derivatives already vanish. Thus singular extrema
are included, not excluded by an unproved smoothness assertion.

The exact discriminant factorization is

\[
 \Delta=\big[g(h-1)(b(i-f)+fg-ei)\big]^2 R(b,e,f,g,h,i).
\]

The displayed square is a parent unit, because
`b(i-f)+fg-ei=i(d-e)` on the graph. Consequently a hypothetical compact
component supplies a real solution of the **six** equations

\[
 R=R_e=R_f=R_g=R_h=R_i=0,
\]

with `A!=0` and all 70 reconstructed parent brackets nonzero. Reconstruct
`a=-B/(2A)`, then `d` and `c` by the two graphs above; this defines every
localization factor exactly. A rational unit-ideal certificate after
saturation by `A` and the reconstructed parent units would prove that this
canonical triple orbit has no compact component. A real-algebraic
certificate of emptiness would also suffice.

The converse is **not** claimed: a critical point need not belong to a compact
component. Nor does smoothness of the discriminant alone establish escape.

### Computational cost

The new variable count is six instead of the previous seven, but this is
not a demonstrated runtime improvement. `R` has degree 18 and 4,186 terms.
The six generators have respectively 4,186, 3,014, 3,961, 3,347, 3,616,
and 4,036 terms: **22,160** in total. The older seven-variable hypersurface
had 594 terms and degrees 7–10. No larger Groebner or saturation run was
launched on the basis of variable count alone.

## 4. Exact uniform fold: the unbranched shortcut is false

A first exact parameter trial already yields a uniform branch point of the
projection forgetting `(a,b,c)`. Set

\[
 d=-5,\quad e=-4,\quad f=-3,\quad g=-1,\quad i=4,
 \quad b=-23/7.
\]

Let `h` be the unique root in

\[
 \left(\frac{1614340}{1610729},\frac{1013489}{1011222}\right)
\]

of the irreducible polynomial

\[
532665h^4-2993010h^3+6165829h^2-5528748h+1823364.
\]

The exact rational functions `a(h),c(h)` are recorded in
`UNIFORM_BRANCH.json`. Independent arithmetic within the producer verifier
checks:

* all three original factor equations vanish modulo this irreducible quartic;
* all 70 parent brackets are nonzero in its exact algebraic number field;
* the Jacobian minor in columns `(a,b,c)` is zero;
* the minor in columns `(a,h,i)` is nonzero;
* the quadratic in `a` has a double root with nonzero leading coefficient,
  and its discriminant has a simple root in `h`.

Thus the original common zero set is smooth here, but the indicated
six-parameter projection folds. The height **b is noncritical here**, as
certified by the nonzero minor omitting `b`. This is not a counterexample to
height-b critical emptiness, triple escape, injectivity, or 9DVL.

The producer replay rejects three deliberate corruptions: changed root
polynomial, changed parent coordinate, and wrong isolating interval.
Independent referee acceptance is still pending; no review is inferred from
the producer's PASS.

## 5. Bounded rational-parametrization gate

The conic has the explicit rational point `[a:c:z]=[1:0:0]` at infinity.
Using the parameter `t=bf-ce` and solving `a` gives a globally valid rational
chart on every parent cell because `t=[1267]` is a parent unit. After the
`d` graph, the third equation has a 573-term degree-11 numerator with
coordinate degrees

| coordinate | t | b | e | f | g | h | i |
|---|---:|---:|---:|---:|---:|---:|---:|
| degree | 2 | 4 | 4 | 4 | 2 | 2 | 3 |

Its denominator is `e^2 i^2 t(f-1)(h-1)`, entirely parent units. This chart
does **not** expose an affine remaining coordinate.

A further exact test used all 64 independent shifts of `(b,e,f,g,h,i)` by
0 or 1, keeping `t` fixed. The exponent-difference matrix has rank seven
modulo 1,000,003 in all 64 cases, hence has rank seven over Q. No nonzero
common diagonal scaling exists in those transformed coordinate systems.
These were rational-coordinate flows outside the earlier original-coordinate
no-go, so the test was not a rerun of that negative theorem. It does not rule
out other rational coordinate systems or nonlinear flows.

## Next discriminator and stop

The concrete remaining mathematical discriminator is the six-variable
localized critical system in Section 3, or a proof that every real critical
point it permits is a saddle with all singular strata separately resolved.
The current certificate supplies its exact polynomial input and attaches the
only quadratic degree-drop branch to a parent-unit conic identity. It does
not supply a positive-dimensional roadmap, a saturation identity, or an
exhaustive classification of the residue.

A different route becomes preferable if another track proves an all-orbit
geometric family theorem that covers this canonical triple. Do not spend
another cycle merely enlarging the 64-coordinate torus search.

Replay:

```text
python triple/verify_uniform_branch.py
python triple/verify_conic_reduction.py
```
