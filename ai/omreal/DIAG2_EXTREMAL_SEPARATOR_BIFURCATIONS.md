# Diagonal two: extremal separator bifurcations and a safe-loss edge

## Result

The first exact attack on the separator-bifurcation boundary left by the
four-singleton obstruction gives a one-sided monotonicity certificate.

At catalog parent `187`, an isolated labeled type-`50` residual crossing
replaces singleton minimal separators by supersets.  Every moving-witness
escape mask therefore stays fixed or expands.  The three overlap-six pair
orbits from the committed extremal atlas remain simultaneously bad on both
sides, and their overlaps change as

```text
(6, 6, 6) -> (9, 6, 6).
```

The strict pair has endpoint escape sizes `(56,56)` on the four-singleton
side and `(61,56)` on the bifurcated side.  Thus this first non-singleton
transition moves away from a disjoint cover rather than toward one.

A broader deterministic survey supports the same strategy.  At the three
catalog parents with three overlap-six pair orbits (`187`, `842`, and
`2612`), `216` exact coordinate samples give `648` tracked pair
observations.  In `495` observations both endpoints remain bad; none has
overlap below six.  All `65` observations containing a non-singleton minimal
separator have overlap at least nine.

These are an exact local theorem and a reproducible finite survey.  They do
not cover the parent realization cells and do not prove diagonal two.

## 1. Separator-dominance lemma

Fix one signature `rho` and two parent charts `T` and `T'`.  Let
`M_(T,e)(rho)` be the inclusion-minimal source-local separator family from
`DIAG2_ESCAPE_MINIMAL_SEPARATORS.md`.

> **Separator-dominance lemma.**  Suppose that for every source `e` and every
> `D' in M_(T',e)(rho)` there is a `D in M_(T,e)(rho)` with `D subset D'`.
> Then
>
> ```text
> N_(T',e)(rho) subset N_(T,e)(rho)
> ```
>
> for every source, and consequently
>
> ```text
> E_T(rho) subset E_T'(rho).
> ```

Indeed, a direction is blocked at `T'` only if its deleted half-star contains
some `D'`.  It then contains the old subset `D`, so the same direction was
already blocked at `T`.  Taking complements proves escape-mask inclusion.

This observation is elementary but useful: a minimal separator which is
lost, or is replaced only by supersets, is globally safe for diagonal two.
Only an **undominated separator birth** can shrink an escape mask.

## 2. Exact isolated type-50 crossing

The verifier puts the checked-in integer realization of parent `187` into
the standard chart

```text
[1 0 0 0 1 1 1 1]
[0 1 0 0 1 a d g]
[0 0 1 0 1 b e h]
[0 0 0 1 1 c f i].
```

It varies coordinate `e`.  Global residual factor `11045` belongs to the
type-`50` orbit and has labeled occurrence rows

```text
124, 357, 467, 568.
```

Its restriction is monic affine and has the exact rational root

```text
-525662980838944803588912159332931345235344
------------------------------------------------
 41907898019468964511553138173016456983893305.
```

At that point it is the unique zero among all `26,740` primitive global
residual factors.  The perturbations `e-epsilon` and `e+epsilon`, with
`epsilon=10^-5`, preserve all seventy parent-bracket signs and every other
residual-factor sign.  Each endpoint has exactly `26,112` complete topes,
and the crossing exchanges exactly two topes in each direction.

The original atlas signatures are transported through the exact projective
normalization, including its old-label reorientation signs.  This gives the
three pinned mapped pair orbits

```text
(41791434804464172, 69849397930972629)
(41224216731022549, 41224087949575724)
(68230936274949461, 70482716760692055).
```

All six signatures are bad at both endpoints.

## 3. The strict safe-loss profile

Only the first signature of the first pair changes its escape mask.  On the
four-singleton side, mutation row `30` (triple `167`) supplies singleton
separators at sources `1`, `6`, and `7`.  Across the wall:

* the source-`1` singleton `30` disappears;
* the source-`6` singleton `30` is replaced by `{30,33}`; and
* the source-`7` singleton `30` is replaced by `{30,33}`,

where row `33` is triple `467`.  All other minimal families are unchanged.
Every new separator therefore contains an old separator.  The verifier
checks this dominance directly for all six signatures, reconstructs every
escape mask independently from the minimal families, and checks

```text
E_plus(rho) subset E_minus(rho)
```

for every endpoint.  Exactly one inclusion is strict.  Its mask gains eleven
directions, and its overlap with its unchanged partner gains three.

The pinned semantic digest is

```text
fbd1109b668d41da64b1657a37d9b12b602ec68ab30a4650f051aacb88c6ee2a
```

Replay it with:

```console
python ai/omreal/verify_diag2_extremal_safe_loss_edge.py
```

## 4. Exact extremal coordinate survey

For each of parents `187`, `842`, and `2612`, the survey uses every one of
the eighteen signed standard-coordinate rays.  Along each ray it finds the
first parent-bracket boundary exactly and samples at `1%`, `10%`, `50%`, and
`90%` of that distance.  Every one of the resulting `72` charts per parent
is checked to preserve the parent chirotope and to have `26,112` complete
derived topes.

| parent | exact charts | both-bad observations | lost endpoint | non-singleton observations | minimum overlap | non-singleton minimum |
|---:|---:|---:|---:|---:|---:|---:|
| 187 | 72 | 178 | 38 | 32 | 6 | 9 |
| 842 | 72 | 149 | 67 | 21 | 6 | 11 |
| 2612 | 72 | 168 | 48 | 12 | 6 | 9 |
| **total** | **216** | **495** | **153** | **65** | **6** | **9** |

The complete both-bad overlap histogram, split by whether either endpoint
has a non-singleton separator, is pinned by semantic digest

```text
c31db4fe4272c12d5d6001f5c47a323a95a2d20750c6d56da5d63505990aa177.
```

Replay the complete survey with:

```console
python ai/omreal/verify_diag2_extremal_coordinate_survey.py --workers 4
```

## 5. Scope and next target

The survey is not a chamber atlas: coordinate samples can miss residual
cells, and three parent representatives do not cover all realizable parents.
The safe-loss theorem is one labeled type-`50` edge, not all `84,840`
labeled residual occurrences.

The next structural target is nevertheless sharper than generic transition
coverage.  A counterexample cannot be created by a separator loss satisfying
the dominance lemma.  The proof search should classify **undominated
separator births** at generic residual flips, especially births that leave
one endpoint outside the four-singleton regime.  A birth landing both
endpoints in the four-singleton regime is already excluded by the universal
four-singleton obstruction.

The honest nine-diagonal score remains `1/9`.
