# Robust common shears on two exact residual mutation squares

## Result

The two exact transverse residual-wall nodes currently available in the
repository satisfy a stronger condition than chamberwise common-shear
intersection.

For a signature `rho` which is bad in every chamber `c` of a square, define

\[
                 E_\square(\rho)=\bigcap_{c\in Q_2}E_c(\rho).
\]

The exact audit proves that the robust masks `E_square(rho)` are pairwise
intersecting:

| exact square | bad in all four cells | minimum robust mask | minimum robust pair overlap | unordered pair decorations |
|---|---:|---:|---:|---:|
| generic canonical type `37/44` | 48,770 | 52 | 8 | 1,189,232,065 |
| coverage-certified parent-2599 node | 70,968 | 53 | 11 | 2,518,193,028 |

Thus, for every two distinct signatures bad throughout either square, there
is one oriented elementary shear which works for both signatures in all four
chambers.  The direction may depend on the signature pair; no single
direction is asserted to work for every pair.

This eliminates both stored `Q_2` cycles as counterexamples to a
mutation-stable common-shear theorem.  It is a finite local theorem, not a
proof of diagonal two.

## 1. Why the escape masks are chamber-constant

The 56 derived normals vary polynomially with the parent realization.  Every
nonzero maximal minor of those rows is either a nonzero parent-bracket unit
or such a unit times one of the 26,740 primitive residual factors.  Therefore,
inside one parent chirotope and one fixed residual-factor sign condition, the
oriented matroid of the derived rows is fixed.

The complete-tope restriction criterion computes `E_T(rho)` only from that
oriented matroid and the extension signature.  Hence the escape mask is
constant on every connected chamber carrying the fixed factor-sign word.  In
particular, the four exact tope tables at a certified transverse node give
the masks throughout its four open local cells, not merely at four isolated
floating-point samples.

The generic type-`37/44` square is reconstructed over the rationals.  Exactly
the two intended primitive factors vanish at its center, and their exact
two-by-two Jacobian is nonzero.  Merely comparing the four endpoint sign
words would not prove that those endpoints belong to the four local germs:
another residual or parent wall could in principle separate an endpoint from
the node.

The verifier therefore restricts every wall equation to each radial segment

\[
                         T(t)=T_*+t(T_c-T_*),
                         \qquad 0\le t\le1.              \tag{1}
\]

The two target restrictions are exactly `+/- epsilon*t` with their intended
quadrant signs.  For the other 26,738 residual factors, all 106,952 segment
restrictions have strict constant-sign Bernstein coefficients.  The same is
true for all 280 restrictions of the 70 parent brackets.  Residual degrees
are at most three and parent-bracket degrees at most one; every certificate
already succeeds without subdivision.  Since Bernstein basis functions are
nonnegative and sum to one on `[0,1]`, these exact rational coefficient signs
prove that no other wall meets any segment.  Each sample is therefore joined
to, and lies in, its claimed local chamber germ.  The segment-certificate
serialization uses the intrinsic quadrant-sign order rather than caller-local
sample labels.  Its digest is

```text
00b4816dc519aef84b90e285b8ebd4aded75e5675a0a0a639e72a23d31e6071d
```

The parent-2599 square instead consumes the already hash-pinned exact roadmap
and `Q_2` graph, whose source verifier certifies local coverage and adjacency.

## 2. Why robust directions extend to the walls and node

Fix an oriented shear `d` and a signature `rho`.  Membership

\[
                         d\in E_T(\rho)
\]

means that the retained signed derived rows have a nonzero nonnegative
dependence.  Normalize its weights by

\[
                         \lambda_i\ge0,
               \qquad \sum_i\lambda_i=1.
\]

Let parent realizations `T_n` approach a residual wall or its transverse
node while `d` remains in every `E_{T_n}(rho)`.  Take this limit in the
continuous rational standard gauge.  The normalized weights lie in a compact
simplex, so some subsequence converges to `lambda_*`.  Derived rows vary
continuously, and passing to the limit gives the same nonnegative dependence
at the limiting realization.  Its weights still sum to one, so it is nonzero.
Consequently escape-mask membership is closed at these uniform residual
limits.

The integer matrices used for exact tope enumeration clear denominators by
positive, independently chosen column scalings.  Such scalings positively
rescale each derived row and reparameterize an elementary shear by a positive
scalar.  They therefore preserve all 112 oriented direction labels and every
escape mask, so the integer endpoint computations and the continuous-gauge
limit argument describe the same local square.

It follows that a direction in `E_square(rho)` works not only in all four
open local cells but also on their intervening wall patches and at the node.
For a pair `rho,eta`, any direction in

\[
                  E_\square(\rho)\cap E_\square(\eta)
\]

is therefore a common moving-witness direction on the closed local square.

## 3. Exact edge and cycle margins

On the generic type-`37/44` square, each edge has 48,842 signatures bad on
both sides.  The two-cell robust masks have minimum size 52 and minimum
pairwise overlap 8.  Across the whole square, 48,770 signatures remain bad;
the same minima are 52 and 8.  A minimum-overlap pair is

```text
33578357495277228
34704257403170476
```

and its two robust masks each have size 54 and overlap in eight directions.

On the coverage-certified parent-2599 node, each edge has 71,040 signatures
bad on both sides.  The two-cell robust masks have minimum size 53 and
minimum pairwise overlap 11.  Across the whole square, 70,968 signatures
remain bad; the same minima are 53 and 11.  A minimum-overlap pair is

```text
17531516482543
31638416184377343
```

with robust-mask sizes 53 and 57 and overlap eleven.

The audits include every abstract extension bad in the relevant cells, not
only proper incomparable pairs.  The stated pair-decorations are therefore
strong finite supersets of the pairs needed by diagonal two.

## 4. Exact replay and scope

First replay the source geometry of the coverage-certified parent-2599 node:

```console
PYTHONDONTWRITEBYTECODE=1 python \
  ai/omreal/DIAG9_GRAPH_verify_row2599_node.py
```

Then run the robust-mask audit:

```console
PYTHONDONTWRITEBYTECODE=1 python \
  ai/omreal/verify_diag2_robust_mutation_squares.py
```

The two semantic digests are

```text
generic-37-44:             ad40add5ed1ad5502d57250bdbef4d6ce7873f81958f619531e6b6af516908f6
parent2599-certified-node: f4db21ca8a6fc00f8819988bddab600c54102cb261db8b5a1085ab2258c90455
```

The robust verifier reconstructs the first square, its four exact radial
segment certificates, and all of its complete topes.  For the second it
hash-pins, but does not regenerate, the exact node roadmap and graph, then
recomputes every escape mask and robust intersection from their stored exact
tope tables.  The first command is the independent source replay for that
stored geometry.

No artifact currently gives a covered residual-chamber graph for a complete
parent realization cell.  The 178-chart bank has no adjacency or coverage
claim, and residual factor-sign words are not yet known to have connected
realization sets.  Thus this theorem does not construct the full
component-decorated transition graph, exclude every closed decorated cycle,
or increase the honest `1/9` proof score.
