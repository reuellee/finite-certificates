# Universal support-drop wall stars and their exact exceptional census

## Status

There is a universal integral private-row theorem for every cross-signature
`5+5` support-drop wall.  It reduces a possible local `d_1` kernel to one
extreme compactness pattern:

> the central pair component and **every** adjacent cofinal spoke component
> through the wall must all be compact.

If even one of those components is noncompact, the entire wall star is
unit-pivot injective.  The parent-16 wall in
`DIAG2_PIVOT_COMPONENT_GRAPH.md` is the escaping-center case.

The support-level obstruction to finding an automatically noncompact spoke is
also exact.  If `P` is the four-support remaining after one coefficient of a
strict five-circuit drops and `R` is the other active minimal support, then
all cofinal spokes stay pencil-rigid exactly when

\[
                              P\cup R
       \quad\text{is itself pencil-rigid}.             \tag{1}
\]

For generic simple walls, an exhaustive Burnside calculation over all 13
residual four-normal wall types and every strict-circuit-eligible generic
five-support gives:

\[
 \boxed{112{,}041}
\]

`S_8`-orbits of exceptional `(P,R)` support cores after the universal unary
signed filter.  Distinguishing the incoming triple `q_0` of
`Q=P union {q_0}` refines these to

\[
 \boxed{5{,}082{,}873}
\]

support-fan orbits.  These are exact finite **upper bounds** on the remaining
geometric wall types.  They are not millions of compact components: the
census does not impose simultaneous residual-side compatibility, a realizable
parent wall, proper incomparability, or compactness.

The verifiers are

```console
python ai/omreal/DIAG2_PIVOT_UNIVERSAL_WALL_VERIFY.py
```

or directly

```console
g++ -O3 -std=c++17 ai/omreal/DIAG2_PIVOT_RESIDUAL_WALL_ORBITS.cpp \
    -o /tmp/diag2-wall-orbits
/tmp/diag2-wall-orbits
```

This is a quantified advance for diagonal two, not its proof.

## 1. Universal component-decorated wall-star theorem

Let `Q,R` be distinct cofinal five-support cover pieces belonging to different
signatures.  Suppose a point `Y_*` of their intersection carries a positive
witness on a proper four-support

\[
                              P\subset Q,qquad |P|=4.  \tag{2}
\]

For every triple `q notin P`, put

\[
                              T_q=P\cup\{q\}.           \tag{3}
\]

There are 52 such cofinal pieces for the signature of `Q`; one is `Q`, so 51
are genuine third cover indices.  At `Y_*`, the witness on `P` pads by zero to
every `T_q`.

Let

\[
 K_0=\operatorname{Comp}_{Y_*}(C_Q\cap C_R),
 \quad
 A_q=\operatorname{Comp}_{Y_*}(C_Q\cap C_{T_q}),
 \quad
 D_q=\operatorname{Comp}_{Y_*}(C_R\cap C_{T_q}).       \tag{4}
\]

Here `Comp` denotes the connected component containing `Y_*`.

### Automatic removal of the `A_q` columns

The supports `Q` and `T_q` share `P`, so their union contains at most six
distinct triples and at most 18 label occurrences.  Some parent label has
degree at most two.  The projective-plane-pencil lemma applies to every
component, giving

\[
                         H_c^0(C_Q\cap C_{T_q};\mathbb Z)=0.    \tag{5}
\]

Thus no `A_q` contributes a compact-component column.

### Compactness forces the needed triple row

Let `L_q` be the component through `Y_*` of

\[
                       C_Q\cap C_R\cap C_{T_q}.         \tag{6}
\]

If either `K_0` or `D_q` is compact, then `L_q` is compact: it is a connected
component of a closed subset of that compact pair component.  The
characteristic functions of whichever compact pair components occur restrict
to the characteristic function of `L_q`, with Cech incidence coefficient
`+1` or `-1`.

After (5), the row of `L_q` therefore has the form

\[
                     \epsilon_0 x_0+\epsilon_q x_q=0,  \tag{7}
\]

with a term present exactly when its pair component is compact.

This proves the following complete local algebra.

> **Universal wall-star theorem.**  On compact-component columns incident to
> `Y_*`, the wall-star part of `d_1` is injective unless `K_0` and every one of
> the 51 components `D_q` are compact.  In that exceptional all-compact case,
> the restricted star matrix has rank 51 on 52 columns and a
> one-dimensional transfer kernel.  Additional rows outside the star may
> still kill that kernel.

**Proof.**

- If `K_0` is noncompact, it supplies no column.  Every compact `D_q` then has
  a private unit row (7).
- Suppose `K_0` is compact.  If some `D_i` is noncompact, its row contains
  only `epsilon_0 x_0`, so `x_0=0`.  Every remaining compact `D_q` is then
  killed by its own unit row.
- Only when the center and all spokes are compact do all 51 equations have
  two terms.  After changing column signs they read `x_q=x_0`, leaving the
  stated one-dimensional kernel.  QED.

The argument works over `Z`, not only over `Q`, because all pivots are units.
The verifier exhausts all `2^9` compactness decorations on an eight-spoke
model, checks the formula exactly, and checks the full 51-spoke extreme
matrices.

## 2. Exact support criterion for a flexible spoke

Let `R'` be the support-minimal active witness inside the partner five-piece.
Choose any `q in R' minus P`; then

\[
                         (P\cup\{q\})\cup R'=P\cup R'. \tag{8}
\]

Consequently, if `P union R'` is pencil-flexible, the spoke `D_q` has no
compact component and the wall-star theorem is injective.

Conversely pencil rigidity is monotone under adding triples:

- label degrees cannot decrease; and
- the common-partner intersection at a label can only shrink.

Hence if `P union R'` is pencil-rigid, then every
`(P union {q}) union R'` is pencil-rigid.  This proves (1).

There is also an automatic lower-support reduction at a generic simple wall.
If `|R'|<=3`, then
`|P union R'|<=7`, too few triples for minimum label degree three.  If
`|R'|=4`, then—away from a second residual wall—the partner four-circuit is
structural and has a hub in all four triples.  Pencil rigidity would require
exactly eight distinct union triples and every label degree exactly three,
contradicting degree at least four at that hub.  Thus a hard generic simple
wall requires a strict five-support partner.  A residual four-support partner
belongs to a simultaneous-wall stratum and is deliberately deferred to the
recursive lower-dimensional analysis.

## 3. Why the residual-wall census is different from the older `4+5` census

The older count of 4,260 signed-filtered `4+5` orbits concerns structural
four-circuits which exist off the residual walls and have a common hub.  It is
not the support-drop census.

At a first cofactor root of a strict five-circuit, the remaining four normals
were independent immediately before the root.  Their determinant is therefore
neither identically zero nor a parent-bracket unit.  It is one of the 13
genuine residual derived-wall types.  There are exactly 84,840 labeled
residual four-sets in those 13 `S_8` orbits.

The new C++ verifier pairs representatives of each of those 13 orbits with
all 2,021,992 generic size-five supports.  It retains a pair precisely when

1. `P union R` is pencil-rigid; and
2. for the signed run, `R` has at least one residual cofactor.

Condition 2 is the universal unary signed obstruction: an all-unit positive
five-circuit would persist to a chart realizing its signature and is
impossible.  It is necessary but not sufficient for a prescribed extension
signature at the same wall.

## 4. Exact exceptional support-core census

Before the unary signed rejection there are 117,510 exceptional `(P,R)`
orbits.  Afterwards there are 112,041, with aggregate weight-gauge strata

| `beta(P,R)` | support-core orbits |
|---:|---:|
| 0 | 77,649 |
| 1 | 33,453 |
| 2 | 938 |
| 3 | 1 |
| 4 | 0 |
| **total** | **112,041** |

The split by residual wall type is:

| wall orbit | strict paddings of `P` | exceptional cores |
|---:|---:|---:|
| 36 | 30 | 6,157 |
| 37 | 48 | 5,307 |
| 38 | 48 | 2,803 |
| 39 | 30 | 2,694 |
| 41 | 48 | 10,530 |
| 42 | 48 | 4,206 |
| 44 | 48 | 17,178 |
| 46 | 34 | 5,172 |
| 47 | 34 | 13,156 |
| 48 | 52 | 638 |
| 49 | 52 | 12,743 |
| 50 | 52 | 20,758 |
| 51 | 52 | 10,699 |
| **total** | -- | **112,041** |

The `strict paddings` column counts triples `q_0` for which the five-support
`Q=P union {q_0}` has no identically dependent four-face and can therefore be
a strict circuit on one side of the wall.

The exact parent-16 wall has residual type 37 and `beta=0`; it is an actual
proper-incomparable occurrence inside this finite exceptional support class.
Its center escapes, so the component-decorated theorem removes it despite its
exceptional support incidence.

## 5. Distinguished incoming-support fan census

To retain the support `Q`, the Burnside calculation also counts triples
`(P,R,q_0)` with `Q=P union {q_0}` strict-support eligible.  After the unary
signed filter there are 5,082,873 `S_8`-orbits, stratified as

| `beta(P,R)` | distinguished wall-fan orbits |
|---:|---:|
| 0 | 3,540,329 |
| 1 | 1,502,756 |
| 2 | 39,759 |
| 3 | 29 |
| 4 | 0 |
| **total** | **5,082,873** |

The large refinement count is useful diagnostically: an orbit-by-orbit CAD
at the raw support-fan level is not the next sensible step.  Compactness or
signed-side theorems must prune the 112,041 cores before distinguished
incoming supports are expanded.

## 6. What remains finite and unresolved

The census is complete for **generic simple** support-drop walls: one
four-circuit coefficient reaches a simple residual wall while the partner is
a strict minimal five-circuit.  It does not cover simultaneous cofactor drops
or intersections of several residual walls; those are lower-dimensional wall
stars and require recursive component incidence.

Nor does the unary signed filter establish that an exceptional support core
occurs for two prescribed realizable signatures.  The next exact filters are:

1. merge the four-circuit and five-circuit XOR equations on the chosen side of
   the same labeled residual wall;
2. impose the rank-four chirotope Grassmann--Pluecker clauses and extension
   properness/incomparability; and
3. for survivors, decide whether the central and all 51 spoke components can
   simultaneously be compact.

By the universal wall-star theorem, item 3 is the only compactness pattern
which can support a local transfer kernel.  Proving it impossible, or showing
that every all-compact star has an additional private row at a deeper wall,
would close the support-drop part of diagonal two.  Other global pair
components not meeting a support-drop wall would still need the existing
interior-to-boundary argument.

No vanishing beyond the first diagonal is claimed here.
