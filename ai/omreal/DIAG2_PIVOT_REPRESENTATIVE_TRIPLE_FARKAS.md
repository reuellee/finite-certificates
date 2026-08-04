# Exact Farkas audit of the canonical rank-two triples

## Result

The four exact uniform rank-two witnesses in
`DIAG2_PIVOT_REPRESENTATIVE_TRIPLES.md` do **not** give four simultaneous-wall
obstructions.  Their primitive gradient dependences and residual values are:

| triple | primitive relation | residual values at the witness |
|---|---|---|
| `(37,41,46)` | `8 dq37 - 2 dq41 + 17 dq46 = 0` | `(-51/5,-136/9,16/45)` |
| `(37,46,49)` | `6 dq37 - 6 dq46 + dq49 = 0` | `(15/8,-25/8,-35/2)` |
| `(39,48,50)` | `dq39 + 3 dq48 + 2 dq50 = 0` | `(0,0,0)` |
| `(41,46,49)` | `3 dq41 + dq46 - 15 dq49 = 0` | `(-5/8,405/256,-21/256)` |

For a signed orientation `p_i=s_i q_i`, uniqueness of the dependence says
that a positive Farkas relation exists exactly for the two antipodal sign
vectors `s=sign(c)` and `s=-sign(c)`, where `c` is the displayed coefficient
vector.  At each of the three witnesses with nonzero residual values, neither
of those orientations makes all three `p_i` strictly positive.  Thus the
rank drop there is not a strict-cone obstruction for the three halfspaces
containing that point.

The witness `(39,48,50)` is different: it lies on all three walls, and both
orientations

\[
 (p_{39},p_{48},p_{50})=(q_{39},q_{48},q_{50})
 \quad\hbox{and}\quad
 (-q_{39},-q_{48},-q_{50})
\]

have the positive Farkas weights `(1,3,2)`.  This is a genuine obstruction
to a strict common direction for that *oriented canonical wall triple*.
It is not, by itself, a certified proper incomparable extension pair.

## The positive wall circuits

At

\[
 (a,b,c,d,e,f,g,h,i)=(-1,2,3,4,-5,2,7,-4,5),
\]

the three residual supports carry the exact signed dependencies

\[
\begin{aligned}
 12n_{123}+3n_{356}-2n_{378}&=0,\\
 2n_{123}-2n_{145}-2n_{246}+n_{356}&=0,\\
 3n_{123}+3n_{145}+3n_{246}-n_{378}&=0.
\end{aligned}
\]

The first is the type-39 wall after its coefficient on `124` has dropped to
zero; its minimal support is `123/356/378`.  The other two are the minimal
type-48 and type-50 supports.  Taking the signs of the displayed coefficients
turns them into positive circuits with weights respectively

\[
 (12,3,2),\qquad(2,2,2,1),\qquad(3,3,3,1).
\]

They can be packaged consistently at support level into two bad signatures:
the type-39 and type-48 circuit signs agree on `123` and `356`, while the
type-50 circuit uses a second signature.  This observation is only local
support compatibility; the checker does not promote it to a global proper
pair.

## Exact tangent escape

Hold every normalized coordinate fixed except `h`, and move

\[
                        -4\ge h\ge -5.
\]

All three residual polynomials are independent of `h`, so the entire segment
stays on `q39=q48=q50=0`; their gradients and the positive Farkas relation
are unchanged.  The three signed normal dependencies above hold with the
same coefficients at both endpoints.  Since the normals are affine in `h`,
the positive wall circuits persist on the full segment.

Every parent bracket is affine in `h`.  Exact endpoint signs show that no
parent bracket changes sign before the endpoint, where precisely

\[
                              [2478]=0
\]

and the other 69 parent brackets remain nonzero.  Therefore this canonical
positive triple obstruction has a tangent path to the parent boundary.  It
cannot be a compact trap on its own.

This result is deliberately scoped to the twelve canonical residual
representatives and these four witnesses.  Relative labeled `S_8`
occurrences, compatibility with an actual proper incomparable pair, and the
global no-cycling problem remain open.  In particular, diagonal two is not
proved.

## Verification

Run

```console
python ai/omreal/DIAG2_PIVOT_REPRESENTATIVE_TRIPLE_FARKAS_VERIFY.py
```

The dependency-free checker evaluates every residual, parent bracket,
Jacobian row dependence, Farkas orientation, wall-circuit identity, and the
complete tangent segment exactly over `Fraction`.
