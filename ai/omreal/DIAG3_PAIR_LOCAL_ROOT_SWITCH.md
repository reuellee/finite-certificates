# Diagonal three: universal local ordered-root switches

## Outcome

At every nonstructural residual wall, a root used on an incoming circuit can
be changed to any root used on the opposite outgoing circuit through a chain
of exact ordered two-root carriers at the wall circuit.  The statement is
independent of the parent realization and is valid for an arbitrary signing
of all 56 derived normals.

More precisely, let `P` be the active circuit at one of the thirteen residual
incidence types

```text
36, 37, 38, 39, 41, 42, 44, 46, 47, 48, 49, 50, 51.
```

Thus `|P|=4` at an ordinary wall and `|P|=3` at a localization wall; the
displayed fourth localization normal is not part of `P`.  For every signing

\[
             \sigma:\binom{[8]}3\longrightarrow\{+1,-1\},
\]

the ordered-root graph `G_sigma(P)` defined below is nonempty and connected.
The exact verifier proves this stronger statement without imposing a parent
chirotope, a Grassmann--Pluecker axiom, or realizability.

The construction is equivariant under relabeling by `S_8`, so the thirteen
canonical active supports cover every labeled residual wall of these types.

Consequently, in the six-normal ordinary elimination cospan

\[
       Q_-=P\cup\{u\}\ \longrightarrow\ P\
       \ \longleftarrow\ Q_+=P\cup\{v\},                 \tag{1}
\]

every root valid on `Q_-` and every root valid on `Q_+` belong to one ordered
carrier component after specialization to `P`.  The localization cospan has
five normal coordinates and the same conclusion.  This closes the
single-block cospan root-switch gap in a residual receiver interval.  It does
**not** assert connectivity for roots simultaneously valid for two different
signings, settle the balanced-end `beta` condition, construct a global proper
receiver complex, or prove the third diagonal.

The dependency-free exact checker is
`verify_diag3_pair_local_root_switch.py`.

## 1. Vertices and exact two-root edges

An oriented elementary root is a triple

\[
                         d=(e,f,a),
       \qquad e\ne f,\quad a\in\{+1,-1\}.              \tag{2}
\]

There are 112 roots.  For `I` containing `e` and omitting `f`, write
`J=I-e+f` and let `epsilon(I;e,f)` be the wedge-sorting sign.  The root is a
vertex of `G_sigma(P)` when

\[
             -\epsilon(I;e,f)\sigma_I\sigma_J=a        \tag{3}
\]

for every source row `I in P`.  If there is no source row, both orientations
are vertices.  Equation (3) is exactly the moving-witness compatibility
condition for the selected positive `P` relation.

The graph is uniformly nonempty.  If `m(e,f)` counts source rows for one
ordered label pair, then

\[
                         \sum_{e\ne f}m(e,f)=15|P|.    \tag{4}
\]

A pair with `m=0` contributes both orientations and a pair with `m=1`
contributes its forced orientation.  Conservatively discarding every pair
with `m>=2` leaves at least

\[
                         112-15|P|                  \tag{5}
\]

vertices: at least 52 for an ordinary wall and 67 for a localization wall.
The SAT certificate below therefore proves connectivity, rather than merely
the absence of a two-sided cut in an empty graph.

Let `d_1,d_2` span distinct root lines.  Expand, in the displayed order,

\[
\Lambda^3(1-vN_{d_2})(1-uN_{d_1})e_I.                \tag{6}
\]

The expansion retains the constant, `u`, `v`, and `uv` terms; no commuting
or same-source simplification is made.  The unordered pair `{d_1,d_2}` is an
edge when at least one of the two orders has every nonconstant coefficient
in the `sigma`-orthant for every `I in P`.  Each coefficient condition is a
literal XOR

\[
                         \sigma_I\sigma_J=\pm1.        \tag{7}
\]

Thus an edge is an exact positive two-parameter Gordan carrier for the wall
witness.  A path in `G_sigma(P)` is a chain of such carrier sectors.

## 2. The universal disconnected-cut certificate

For each wall support the verifier reconstructs all conditions (3)--(5) and
asks for a nontrivial cut of `G_sigma(P)`.  Its variables are:

1. the 56 completely unconstrained signing bits;
2. one Tseitin variable for every required pairwise XOR;
3. 112 compatibility variables and 112 cut colors;
4. exact ordered-safety conjunctions for both orders of every pair of
   distinct root lines; and
5. two witnesses per root recording a compatible vertex on either side of
   the cut.

Every realized safe edge forces its endpoints to have the same cut color,
while the final two clauses require a compatible vertex of each color.  The
formula is satisfiable exactly when the graph is disconnected.  All thirteen
formulas are UNSAT.

| type | active `P` | variables | clauses | XORs | conflicts |
|---:|:---|---:|---:|---:|---:|
| 36 | `123/345/367` | 12,956 | 60,546 | 132 | 388 |
| 37 | `123/124/345/567` | 13,000 | 68,114 | 176 | 464 |
| 38 | `123/124/345/678` | 13,001 | 68,094 | 177 | 382 |
| 39 | `123/356/378` | 12,956 | 60,546 | 132 | 348 |
| 41 | `123/124/356/457` | 13,000 | 68,118 | 176 | 387 |
| 42 | `123/124/356/478` | 13,001 | 68,098 | 177 | 464 |
| 44 | `123/124/356/578` | 13,001 | 68,102 | 177 | 419 |
| 46 | `123/145/167` | 12,956 | 60,546 | 132 | 375 |
| 47 | `123/145/167` | 12,956 | 60,546 | 132 | 375 |
| 48 | `123/145/246/356` | 12,998 | 68,130 | 174 | 397 |
| 49 | `123/145/246/357` | 12,999 | 68,118 | 175 | 406 |
| 50 | `123/145/246/378` | 13,000 | 68,102 | 176 | 638 |
| 51 | `123/145/267/468` | 13,000 | 68,106 | 176 | 425 |

Types 46 and 47 are different incidence decorations of the same active
three-circuit and correctly give the same formula.  The verifier pins the
normalized SHA-256 digest of every formula as well as every count in the
table.  Its deterministic exact CDCL implementation exhausts each formula;
the digest alone is not treated as an UNSAT proof.

The compiler is checked independently on deterministic signing canaries:
its one-root masks are compared with the direct transport-alpha calculation,
and its ordered edges are compared with the direct complete exterior
expansion.  Deleting all ordered-edge clauses makes the cut formula SAT,
which protects against a vacuous cut encoding.

## 3. Independent exact-wall audit

The optional second phase constructs the thirteen exact canonical wall
points from `DIAG2_CANONICAL_ROBUST_EDGES.md`, enumerates every GP-valid
one-element extension of their parent chirotopes, and retains exactly those
signatures which make `P` positive.  It then builds every graph directly.

| type | positive valid signings | minimum vertices | minimum edges |
|---:|---:|---:|---:|
| 36 | 1,426 | 68 | 2,223 |
| 37 | 112 | 55 | 1,439 |
| 38 | 370 | 53 | 1,330 |
| 39 | 1,222 | 68 | 2,223 |
| 41 | 80 | 56 | 1,481 |
| 42 | 738 | 55 | 1,417 |
| 44 | 340 | 53 | 1,325 |
| 46 | 2,240 | 68 | 2,223 |
| 47 | 2,224 | 68 | 2,223 |
| 48 | 148 | 57 | 1,537 |
| 49 | 818 | 57 | 1,519 |
| 50 | 216 | 53 | 1,297 |
| 51 | 314 | 54 | 1,364 |
| **total** | **10,248** |  |  |

Every graph is connected.  Per-type semantic digests pin all retained
signatures, vertex masks, and edge counts.  This is a slower independent
regression.  It is deliberately not used as coverage for the universal
theorem in Section 2.

## 4. Why a switch, rather than a surviving root, is necessary

Same-root survival is false at an exact generic type-37 wall.  For

```text
sigma = 70109424330912456
P     = 123/124/345/567
u     = 134
v     = 148
```

the incoming and outgoing circuits and the persistent endpoint are

```text
Q- = P + 134
Q+ = P + 148
R  = 123/134/345/567/148.
```

Their root-mask sizes are respectively `55`, `52`, and `51`.  Seven roots
valid on `Q-` are valid on neither `Q+` nor `R`; the first is `(1 -> 2,+)`.
Nevertheless, the wall graph on `P` is connected.  Since compatibility is
inherited by deleting a zero-weight row, the lost incoming root and every
chosen outgoing root are vertices of that graph and can be joined by ordered
two-root sectors.  The zero-weight wall face is essential.

## 5. Consequence for the residual elimination cospan

At a generic ordinary wall, opposite circuit births live in the six-normal
coordinate face

\[
                         U=P\cup\{u,v\}.              \tag{8}
\]

Its normalized nonnegative-kernel fibers are

\[
 [Q_-,R]\ \longrightarrow\ [P,R]\
       \ \longleftarrow\ [Q_+,R],                    \tag{9}
\]

as proved in `BLOCK_GORDAN_RESIDUAL_ELIMINATION_CELLS.md`.  The localization
version uses five normal coordinates.  Let `d_-` be a root used on `Q_-` and
`d_+` a root used on `Q_+`.  Specialization deletes the `u` or `v` weight, so
both roots are compatible with `P`.  A path

\[
                         d_-=r_0,r_1,\ldots,r_m=d_+   \tag{10}
\]

in `G_sigma(P)` attaches ordered two-root sectors at the `P` endpoint of
`[P,R]`.  Together with the cospan fibers (9), these sectors give the local
cellular reroute which changes roots without requiring one root to survive
both sides.

This conclusion is facewise and integral: every interval and sector has the
formal boundary of an interval or disk with unit incidence.  Realizing those
formal sectors as cells in a common compactification, and comparing different
root-switch paths in higher codimension, remain part of the global receiver
construction.  Convex union-support carriers can supply higher coherence only
after the required codimension-one maps and support-monotone face assignments
have been installed.

## 6. Remaining global receiver-interval criterion

The theorem removes local root switching as a new obstruction.  To turn the
residual receiver strategy into a coverage-certified proper pair
two-complex, one still needs a finite relative CW pair `(K,K_infinity)` with
the following properties.

1. **Receiver coverage.**  Root motion is quotiented by the unparameterized
   motion of column `e` on the oriented projective line through the receiver
   column `f`.  Every fixed parent sign cell cuts such a fiber into an
   interval.  Every non-infinity endpoint where the chosen bad witnesses
   continue must be assigned either a persistent receiver interval or one of
   the residual cospans (9).
2. **Birth and wall attachment.**  At a nonstructural birth, the
   exchange-saturated support-drop theorem supplies the compatible witness,
   (9) supplies the coordinate interval, and the theorem here supplies all
   root switches.  A remaining proof must show that these local attachments
   cover every endpoint encountered by the global receiver system, including
   simultaneous walls and cases whose continuing witness is not the opposite
   member of one certified cospan.
3. **Relative properness.**  The receiver quotient and its interval closures
   must send `K_infinity` to `K_infinity` and be locally finite.  Launching a
   shear ray from every starting point is not a substitute: the model
   `h(x,t)=x+t` has pointwise escaping rays but is nonproper because
   `h(-t,t)=0`.
4. **Incidence acyclicity.**  After all wall and infinity cells are attached,
   the relative matrices must satisfy

   \[
       \operatorname{rank}\partial_2
       =n_1-\operatorname{rank}\partial_1.             \tag{11}
   \]

   Equivalently, choose an escape path `p_v` to `K_infinity` for every
   relative vertex and a two-chain `H_e` for every oriented edge `e:v->w`
   with

   \[
                  \partial H_e=e+p_w-p_v
                  \pmod {C_*(K_\infty)}.              \tag{12}
   \]

   Then every relative one-cycle bounds.  Contracting a certified spanning
   forest to infinity makes the reduced `partial_2` matrix have a unit pivot
   in every remaining row.

Items 1--4 are the remaining global theorem.  In particular, the present
UNSAT certificate does not prove that a pair which is bad on both sides of
an arbitrary wall uses the local `Q_-/P/Q_+` cospan, nor that the receiver
incidence graph is acyclic or proper.  Those claims require component and
endpoint data, not another point atlas.

## 7. Replay

The universal proof is the default:

```console
PYTHONDONTWRITEBYTECODE=1 python \
  ai/omreal/verify_diag3_pair_local_root_switch.py --workers 4
```

Add the independent exact-wall census with:

```console
PYTHONDONTWRITEBYTECODE=1 python \
  ai/omreal/verify_diag3_pair_local_root_switch.py \
  --workers 4 --canonical-audit
```
