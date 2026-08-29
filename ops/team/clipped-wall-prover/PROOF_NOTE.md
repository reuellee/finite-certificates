# Diagonal three: exact clipped-wall route refutation

## Result

At base revision
`ae8a3afc24abfea94acf4b22ea35c2ca18f3c577`, let `V` be the common zero
set of the three authenticated residuals for

```text
(5563,16134,19284) -> canonical unresolved row (5563,4373,23221).
```

Let `B20` be macrobox 20 from the deterministic negative-`a` corridor and

```text
K = B20 intersect {g-a <= 0}.
```

The proposed terminal attachment is impossible:

\[
  \boxed{V\cap K=\varnothing.}
\]

Indeed, the residual `q16134` is strictly positive on the **entire** closed
rectangular macrobox `B20`, a stronger domain than `K`.  After exact affine
pullback to the unit 9-cube at coordinate multidegree

```text
(1,1,2,1,1,2,1,1,0),
```

all `576/576` tensor-Bernstein control coefficients are positive.  The
smallest is

```text
846151417395/420906795008 > 0.
```

By the tensor-Bernstein convex-hull property, every value of `q16134` on
`B20` is a convex combination of these controls and is therefore positive.
Consequently there is no common residual zero in `B20`, in `K`, or on the
wall face `K intersect {g-a=0}`.  No connectivity argument can supply an
attachment point that does not exist.

## The three requested decisions

The quantifiers and outcomes are:

1. For every `x in K`, the fixed minor
   `det d(q5563,q16134,q19284)/d(d,e,h)(x)` is strictly negative.  This is
   certified on the stronger full macrobox by two exact rectangular interval
   enclosures obtained by bisecting `g` at `-1`.
2. For every `x in K` and each of the `69` normalized parent brackets other
   than `[3468]`, the bracket is nonzero and retains its registered parent
   sign.  Exact direct intervals establish this on the full macrobox.  The
   closest strict record is `[2467] in [313/448,327/448]`.  On `K`, the one
   remaining bracket `[3468]=g-a` is negative in the relative interior and
   zero exactly on the clipped wall face.
3. There does not exist `x in K intersect {g-a=0}` satisfying all three
   residual equations, hence there cannot exist such a point connected to an
   accepted-corridor triple-zero component.  Direct wall restriction
   `a=g=t` independently gives positive Bernstein certificates for both
   `q16134` (`288/288`, minimum
   `879180358095/420906795008`) and `q19284` (`384/384`, minimum
   `2809875/14680064`).

## Why the previous frontier was insufficient

The prior certificate proved a genuine **parent-wall intersection**, not a
triple-zero wall attachment.  Its exact wall witness has residual values

```text
q5563   = -1/56
q16134  = 5934694995/2202927104
q19284  = 435073/702464.
```

Thus the witness is correctly rejected as a point of `V`.

There is a sharper bounded diagnosis inside the already declared scan:
`q16134` is Bernstein-positive on every full macrobox `6..20`.  Macrobox 6
is the first box in the deterministic `0..20` scan for which all controls are
positive.  Therefore the sign-certified projection corridor is zero-free
from box 6 onward.  A nonzero projection minor proves smooth local projection
where zeros exist; it does not prove that zeros occupy a box or traverse a
box chain.

## Canaries

- Macrobox 19 still retains all `70` parent signs and has a negative fixed
  minor after its registered `g` bisection.  “Accepted” here means accepted
  by those two tests, not occupied by `V`; it is in fact in the zero-free
  suffix.
- Full macrobox 20 is rejected as a parent-interior box solely because
  `[3468]` has exact interval `[-11/448,3/448]`; the other `69` remain strict.
- The wall face is nonempty; the artifact includes a rational feasible point.
- The prior wall witness is rejected by exact residual evaluation.
- The compact-sphere pivot interval is `[-2,2]`, so the false projection-sign
  certificate is refused.

## Scope and next discriminator

This is an exact route refutation, not global noncompactness and not a proof
of any complete factor triple or `S8` orbit.  The unresolved count remains
`1,162,302`, and the honest score remains `2/9`.

The next discriminating computation should return to macroboxes `0..5`,
locate the first exact boundary face through which the component containing
the registered zero exits, and continue it with occupancy-certified adaptive
cells.  Extending the projection-sign-only rectangle chain cannot reach the
wall because the chain becomes zero-free first.

## Replay

```bash
PYTHONDONTWRITEBYTECODE=1 \
  python ai/omreal/build_diag3_clipped_wall_prover_certificate.py
```

The exact certificate is
`ops/team/clipped-wall-prover/DIAG3_CLIPPED_WALL_PROVER_CERTIFICATE.json`.

