# A perfect-square conic discriminant: a reduction, not yet a closure, for (50,7977)

## Status

**This conic argument does not close `(50,7977)`.** An earlier version of
this note claimed it did; adversarial review (agy) caught a real gap in the
argument, confirmed independently below, and the claim is retracted to what
is actually proven.  Separately, `DIAG2_PIVOT_ALL_PAIR_FIBERS.md` later closes
all four canonical-presentation exceptions by stabilizer-equivalent affine
graphs.  Nothing below is used for that closure.

What *is* proven, exactly, and kept here because it is a genuine partial
result worth recording: for `(50,7977)`, after eliminating `q_50`'s pivot,
the restricted second-wall polynomial `r` is a plane conic in coordinates
`(a,c)`,

\[
 r = A(x)\,a^2+B(x)\,ac+C(x)\,c^2+D(x)\,a+E(x)\,c+F(x),\qquad x=(b,e,f,g,h,i),
\]

whose discriminant is an **exact perfect square**:

\[
 B^2-4AC=S^2,\qquad
 S=i(e-h)\bigl(bfi-bf-bi^2+bi-egi+ei^2+fg-fi\bigr).
\]

This rules out the `(a,c)`-conic ever being a bounded ellipse or isolated
point, for any values of the other six coordinates: a real plane conic with
discriminant `>=0` is always empty, a line, a pair of lines, a parabola, or a
hyperbola, and every one of those is unbounded when nonempty. That part of
the classical fact is correct and re-confirmed independently (see section
2). What is missing is a valid construction turning "the abstract curve is
unbounded" into an actual escape usable by this repository's noncompactness
argument -- see section 3.

The checker is

```console
python ai/omreal/verify_diag2_conic_factorization_escape.py
```

It verifies only the two facts above (the conic structure and the
perfect-square discriminant identity) and says so explicitly in its output;
it does not print a noncompactness `THEOREM` line.

## 1. The gap, precisely

The fixed-minor / fiber-linear-escape argument
(`DIAG2_AFFINE_FIBER_RESIDUE_CLOSURE.md` section 2) needs, at every point of
a hypothetical compact component `C`, an honest algebraic **line** through
that point which is either identically zero on `r` (an immediate whole-line
escape) or along which projection is a local diffeomorphism *everywhere on
all of `C`* (the global open-map argument). The retracted version of this
note picked, at a point where `A!=0`, the direction

\[
 v=(S-B,\ 2A),
\]

chosen so the quadratic part of `r` varies only linearly along it (since it
holds one of the two linear factors `2Aa+(B-S)c` of the quadratic part
constant). The checker verifies `r(a_0+t(S-B),\,c_0+2At)` has no `t^2`
term -- true, and independently reconfirmed -- but the coefficient of `t^1`
in that expansion is exactly the directional derivative

\[
 v\cdot\nabla r = (S-B)\,\partial_a r + 2A\,\partial_c r,
\]

which is **not** identically zero (497 monomials, checked directly). So at a
*generic* point of the conic this ray only touches `\{r=0\}` at the starting
point itself -- it is a transversal probe, not a path that stays on the zero
locus. The "whole-line escape" only fires at the special points where this
slope happens to vanish; nothing here shows what happens at the (generic)
points where it does not. `RESIDUAL_STRATUM_NONCOMPACTNESS.md` section 1
warns about exactly this failure mode in its own text: "mere full Jacobian
rank without one fixed nonvanishing minor is insufficient: compact manifolds
can be covered by several projection charts."

## 2. What is still solid

The perfect-square discriminant identity itself is a genuine, independently
re-verified fact (twice: once by the original author, once by an
independent reviewer using unrelated code), and it does have real content:
it rules out the *shape* most immediately compatible with compactness (a
bounded ellipse). The natural correct way to convert this into a real proof
is a rational parametrization of the conic through a known point (the
classical "secant pencil" construction for conics), which for a
non-elliptical conic gives a genuinely unbounded path lying *entirely on*
`\{r=0\}` -- unlike the transversal ray used above. Setting that up exactly
(as a further linear change of coordinates `(a,c) -> (L_1,L_2)` diagonalizing
the quadratic form, handling the further degenerate loci `A=0` and `S=0`
where that change is not invertible) is a real, structured piece of
follow-up work, not attempted here.

## 3. The other three

`(50,7861)`, `(50,12128)`, and `(50,20046)` are also exact plane conics in
`(a,c)` (and in three other candidate coordinate pairs each: `(a,g)`,
`(e,f)`, `(e,h)`), but their discriminants genuinely change sign --
confirmed by direct symbolic computation, not sampling: for `(50,12128)` and
`(50,20046)` the discriminant factors as (irreducible)`^2` times a distinct
irreducible factor of multiplicity 1, so its sign is exactly the sign of
that unsquared factor, which is not fixed; for `(50,7861)` the discriminant
is irreducible outright, with no square factor at all. So real elliptical
`(a,c)`-slices genuinely occur for some configurations of the other six
coordinates for these three, and even the (currently incomplete) approach
above would not apply to them without a separate argument for the elliptical
case.

## 4. Exact verification

```text
PASS: (50,7977) independently reconfirmed unresolved by every prior certificate family
PASS: restricted polynomial has 175 terms, degree 7
PASS: restricted polynomial is an exact plane conic in (a,c)
PASS: conic discriminant B^2-4AC is exactly S^2 for the displayed S (never negative)
REDUCTION: (50,7977)'s (a,c)-conic is never a bounded ellipse; this does NOT yet prove
           noncompactness -- see section 1 for the specific gap
STATUS canonical-presentation method: 9472/9476 (unchanged); exceptions: 4
STATUS complete stabilizer-aware pair theorem: 9476/9476 (verified separately)
CAVEAT: this conic argument closes none of the four method-local exceptions
CAVEAT: diagonal two still requires universal common-shear overlap or another global argument
```
