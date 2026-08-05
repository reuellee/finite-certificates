# Exact canonical residual-triple boundary

## Result

Let `q_r` be the twelve distinct canonical residual polynomials in the
standard nine-variable parent normalization (types 46 and 47 have the same
polynomial).  The exact canonical size-three classification is now:

| class | number of triples | certificate |
|---|---:|---|
| rank three throughout the uniform parent locus | 171 | 170 direct bracket-product minors; one sequential certificate |
| rank two at an exact uniform rational point | 4 | all `3 by 3` minors vanish and a `2 by 2` minor is nonzero |
| not yet classified | 45 | requires further saturation or a witness |

Thus the proposed universal assertion that every three distinct canonical
residual gradients are independent is **false**.  This does not itself
obstruct a positive common descent cone: rank dependence and positive Farkas
dependence are different conditions, and the signs of the dependence have
not been classified here.

This result is deliberately limited to the twelve representatives.  It does
not enumerate relative labeled `S_8` occurrences and does not prove diagonal
two.

## The formerly first-open triple `(36,38,42)`

Write

\[
 p=ae-bd+b-e,
 \qquad
 q=q_{36}=af-cd+c-f.
\]

Two exact Jacobian minors satisfy

\[
 \begin{aligned}
 M_{agi}&=ef(1-c)p
          =[1237][1247][2356]p,\\
 M_{agh}&=(cf^2+cf-f^2)p-bf q.
 \end{aligned}
\]

At a uniform rank-drop point the first equality would give `p=0`, because
`e`, `f`, and `c-1` are nonzero parent brackets.  The second would then give
`q=0`, because `b` and `f` are also nonzero parent brackets.  But

\[
 fp-eq=(1-d)(bf-ce)=-[3457][1267],
\]

which cannot vanish in the uniform parent locus.  Hence the Jacobian of
`(q_36,q_38,q_42)` has rank three everywhere on that locus.  This is a short
explicit saturation certificate; it does not rely on the earlier numerical
observation that attempted rank-drop solutions ran into the boundary.

## Exact uniform rank-drop witnesses

In the coordinate order `(a,b,c,d,e,f,g,h,i)`, the following rational points
have every parent bracket nonzero and give Jacobian rank exactly two:

| triple | point |
|---|---|
| `(37,41,46)` | `(-14/3,-2,2,83/15,43/15,-32/15,-23/25,-29/30,38/21)` |
| `(37,46,49)` | `(47/12,6,35/12,-3/2,-4,-2,1/5,-65/27,3/19)` |
| `(39,48,50)` | `(-1,2,3,4,-5,2,7,-4,5)` |
| `(41,46,49)` | `(2,17/16,-3,59/64,11/16,15/16,79/29,-13/4,166/43)` |

The smallest witness has a transparent two-equation family.  For
`(39,48,50)`, away from the uniform factors `f(c-1)=0`, the third gradient is
in the span of the first two whenever

\[
 a=b+c-bc,
 \qquad
 f(b-g)+i(d-b)=0.
\]

The displayed integer point satisfies these equations.  The verifier does
not rely on this derivation: it evaluates all 84 maximal minors, every parent
bracket, and a nonzero `2 by 2` minor exactly over `Fraction`.

## Direct-product census

For 170 triples, the verifier finds coordinate indices `u,v,w`, a nonzero
integer scalar, and parent brackets `B_1,...,B_m` such that

\[
 \det \frac{\partial(q_r,q_s,q_t)}{\partial(u,v,w)}
   =\epsilon B_1\cdots B_m.
\]

The scan uses sparse integer polynomial arithmetic and exact multivariate
division.  It checks the exact list of the 50 triples which do not have a
certificate of this simple form; `(36,38,42)` and the four witnesses above
are then handled separately.  The remaining 45 canonical triples are left
explicitly open rather than inferred from floating-point searches.

Each of the 170 direct certificates also rules out a compact component of
the corresponding common-zero set.  Projection to the six coordinates
complementary to its fixed nonzero minor is a local diffeomorphism, so the
image of a hypothetical compact component would be both compact and a
nonempty open subset of `R^6`.  This conclusion does not extend merely from
the multi-minor rank certificate for `(36,38,42)`, and it does not classify
relative labeled `S_8` occurrences.  See
`RESIDUAL_STRATUM_NONCOMPACTNESS.md`.

Run

```console
python ai/omreal/DIAG2_PIVOT_REPRESENTATIVE_TRIPLES_VERIFY.py
```

Expected final lines:

```text
PASS exact bracket-product 3-minors for 170 canonical triples
PASS sequential uniform-rank certificate for (36,38,42)
PASS exact uniform rank-two witnesses for ((37, 41, 46), (37, 46, 49), (39, 48, 50), (41, 46, 49))
STATUS 171 rank-three, 4 rank-drop, 45 open among 220 canonical triples
CAVEAT no relative labeled S_8 classification and no diagonal-two proof
```

## Consequence for the strict-cone program

The representative size-two theorem remains valid: distinct representative
gradients are pairwise independent.  Size three cannot be closed by a blanket
rank argument.  The next proof-safe finite task is instead to determine the
sign of the unique dependence at each rank-two stratum and, for a positive
dependence, test whether the associated circuit supports have a common
lower-support tangent escape.  Only after that canonical calculation should
the relative labeled `S_8` overlaps be enumerated.

That canonical calculation is now complete for the four displayed
witnesses.  Three are not simultaneous three-wall points and do not obstruct
the strict active cone there.  The remaining `(39,48,50)` witness has the
positive dependence `(1,3,2)` in both antipodal common orientations, but an
exact tangent path preserves its three positive wall circuits and reaches
the parent boundary `[2478]=0`.  See
`DIAG2_PIVOT_REPRESENTATIVE_TRIPLE_FARKAS.md` and its exact verifier.  This
does not classify other points on the rank-drop strata or relative labeled
occurrences.
