# Discriminantal and higher-Bruhat audit for the 56 derived normals

## Outcome

There is an exact discriminantal-arrangement identification, but it is on the
**extension-point fiber**, not on the parent realization space where the
middle-diagonal matching must live.

| object | exact status | useful consequence |
|---|---|---|
| fixed-`Y` arrangement of the 56 triple planes | essential discriminantal arrangement `B(8,4,Gale(Y))` | zonotopal, shellable fixed face sphere; tope graph is a partial cube |
| residual-wall decomposition as `Y` varies | discriminant of a family of discriminantal arrangements | 13 genuine wall types, not one fixed arrangement fan |
| higher Bruhat model | available canonically for cyclic/alternating oriented matroids | not applicable to the hard row-2599 parent |
| one global zonotope for all parent chambers | no theorem and the canonical construction does not give one | must glue chamberwise zonotopes across residual mutations |

The exact checker `BLOCK_GORDAN_DISCRIMINANTAL_AUDIT.py` proves the
fixed-fiber identification for all 56 normals of the hard chart, exhausts all
`8!` label orders to show that row 2599 is not cyclic up to reorientation,
and checks that the basic higher-Bruhat packet is a fixed unit wall rather
than one of the 13 residual walls.  It also reruns the saved small
non-partial-cube mutation certificate as a scope warning.

Thus published discriminantal/higher-Bruhat shellings do not directly supply
the coordinated block-Gordan matching.  The viable replacement is a finite
**constructible family of zonotopal complexes with explicit mutation maps**
on the 13 wall types.

No diagonal is promoted by this audit.

## 1. Exact discriminantal identification

Let

\[
                         Y:\mathbb R^8\longrightarrow\mathbb R^4
\]

be a uniform rank-four parent matrix, with columns `y_1,...,y_8`.  Choose a
rank-four Gale matrix `K` whose row space is `ker(Y)`, and write its columns as
`k_1,...,k_8`.

Use the `k_i` as normals of eight affine hyperplanes in `R^4`.  Their parallel
translations have parameter vector `t in R^8`.  Translation by a common
point changes `t` by an element of `row(K)`, so the essential translation
space of the discriminantal arrangement is

\[
                  \mathbb R^8/\operatorname{row}(K)
                  \xrightarrow[\cong]{\ \bar Y\ }\mathbb R^4.       \tag{1}
\]

For a five-set `L`, the translated hyperplanes with labels in `L` have a
common point exactly when

\[
                              c^L\cdot t=0,                         \tag{2}
\]

where `c^L` is the unique circuit of the Gale columns supported on `L`.

Put `I=[8] minus L`, so `|I|=3`.  Since

\[
                  \ker K=(\operatorname{row}K)^\perp
                         =(\ker Y)^\perp=\operatorname{row}Y,
\]

there is a unique `q_I in R^4`, up to the circuit normalization, with

\[
                              c^L=Y^Tq_I.                           \tag{3}
\]

The entries of `c^L` on `I` vanish, so

\[
                       y_i^Tq_I=0\qquad(i\in I).                    \tag{4}
\]

Uniformity makes the common annihilator in (4) one-dimensional.  Therefore
`q_I` is proportional to the derived normal

\[
                         a_I=*\,(y_i\wedge y_j\wedge y_k).          \tag{5}
\]

Finally, (2) descends through (1) because

\[
                    c^L\cdot t=q_I^TYt.                            \tag{6}

\]

Equations (1)--(6) prove a linear isomorphism

\[
 \boxed{
   \{a_I^\perp: I\in\tbinom{[8]}3\}
   \cong
   \mathcal B(8,4,K)_{\rm ess}.                                   \tag{7}
 }
\]

The verifier constructs `K=ker(Y)` over `Q`.  For every one of the 56 triples
it computes the complementary five-circuit by alternating `4x4` Gale minors,
solves (3), and checks exact proportionality with (5).  Thus (7) is not only a
terminological analogy.

This agrees with Falk's description of a discriminantal arrangement as an
adjoint of the dual matroid: [A Note on Discriminantal Arrangements](https://doi.org/10.1090/S0002-9939-1994-1209098-1).

## 2. What the fixed-fiber zonotope gives

For fixed `Y`, put

\[
                          Z_Y=\sum_I[-a_I,a_I].                    \tag{8}

\]

The normal fan of the zonotope (8) is the 56-hyperplane arrangement (7).
Consequently:

* its spherical face complex is polytopal and shellable;
* its chamber graph is a tope graph, hence a partial cube; and
* feasible extension signatures are exactly its topes.

These are genuine structural facts.  They may be useful for choosing a
canonical cellular model inside one fixed parent chamber.

They do not compute `H_c` of a bad locus in parent space.  The normalized
Gordan polytope `P_sigma(Y)` is nonempty precisely when `sigma` is **not** a
tope of (7).  As `Y` moves, both `Z_Y` and the set of non-topes change.  A
shelling of the boundary of one `Z_Y` has no canonical restriction to a
shelling after a derived circuit is born or dies.

In block-Gordan language, fixed-fiber shellability sees the weight simplex at
one `Y`; the middle-diagonal differential also sees support drops, zero-block
faces, and split--remerge attachments over paths in `Y`.

## 3. Why the parent wall complex is a different object

The oriented matroid of (7) changes only when four derived normals become
dependent:

\[
                 \det(a_{I_1},a_{I_2},a_{I_3},a_{I_4})=0.          \tag{9}

\]

The exhaustive classification of (9) has 52 incidence orbits:

\[
                         14\text{ zero}+25\text{ unit}+13\text{ residual}.
                                                                    \tag{10}

\]

The first two classes are forced or forbidden throughout a uniform parent
cell.  The residual factors are genuine nonlinear hypersurfaces in the nine
parent coordinates.  Hence the master parent chambers are chambers of the
**parameter discriminant of the family** `Y -> B(8,4,Gale(Y))`; they are not
the chambers of the fixed discriminantal arrangement (7).

This distinction is standard and essential in discriminantal-arrangement
theory.  The combinatorics need not be determined by the underlying parent
matroid and is constant only on a suitable Zariski-open subset of its
realization space.  See Falk above and [Saito, Degeneration in discriminantal
arrangements](https://arxiv.org/abs/2404.18835).

The exact endpoint reroute in
`BLOCK_GORDAN_ENDPOINT_WALL_REROUTE.md` exhibits the distinction locally:
`Q4` dies on a residual parameter wall, its zero-weight face `P` remains, and
`S4` is born, while `R4` survives.  No fixed-fiber shelling specifies the
retargeting from `Q4` to `P` to `S4`.

## 4. Higher Bruhat does not supply the missing globalization

Ziegler identifies higher Bruhat orders with extension posets of **cyclic**
or alternating oriented matroids.  He also shows that extension posets for
arbitrary affine arrangements need not retain the key cyclic structural
properties: [Higher Bruhat Orders and Cyclic Hyperplane Arrangements](https://www.mi.fu-berlin.de/math/groups/discgeom/ziegler/Preprintfiles/025PREPRINT.pdf).

The hard parent is outside that hypothesis.  For every one of the `8!` label
orders, the verifier solves over `GF(2)` for a global sign and eight element
reorientations which would turn all 70 bracket signs into the alternating
chirotope.  Every system is inconsistent.  Thus row 2599 is not a relabeled
or reoriented cyclic rank-four oriented matroid.

There is also an exact local incidence mismatch.  The four triples in the
basic 3-packet

\[
                         123,124,134,234                           \tag{11}

\]

form derived-wall orbit 9.  Orbit 9 is a parent-bracket unit: it never crosses
inside a uniform parent cell.  In contrast, the local moves that must be
coordinated are precisely the 13 residual orbits

\[
             36,37,38,39,41,42,44,46,47,48,49,50,51.              \tag{12}

\]

Thus the most direct packet-flip identification sends the canonical
higher-Bruhat packet to the wrong kind of wall.

Even in the cyclic setting one should not silently replace a higher Bruhat
graph by one zonotope.  Felsner and Ziegler prove that higher Bruhat graphs
contain natural zonotopal subgraphs but are not polytopal in general, and
those subgraphs need not cover all vertices: [Zonotopes Associated with
Higher Bruhat Orders](https://www.mi.fu-berlin.de/math/groups/discgeom/ziegler/Preprintfiles/066PREPRINT.pdf).

Finally, `verify_mutation_graph_not_partial_cube.py` gives an independent
warning for varying oriented matroids: its 384-vertex rank-three mutation
graph has a nontransitive Djokovic--Winkler relation.  The new verifier
reruns that exact certificate.  This does not disprove partial-cube behavior
inside one fixed `UOM(4,8)` cell, but it rules out importing it from a general
mutation-graph theorem.

## 5. Strongest viable cross-wall target

The discriminantal identification suggests a more precise finite object than
a higher-Bruhat poset.

1. On every full-dimensional residual chamber `C` of a parent cell, use the
   fixed oriented matroid of (7) and a chosen cellular model of its zonotope
   `Z_C`.
2. On a generic residual wall `W`, use the rank-three four-normal circuit to
   build the common specialization `Z_W` and cellular maps

   \[
                         Z_C\longleftarrow Z_W\longrightarrow Z_{C'}.       \tag{13}
   \]

   These maps must retain zero circuit weights.  The exact
   `Q4 -> P -> S4` reroute is one one-dimensional instance of (13).
3. Attach to each cell the product/join of the relevant normalized Gordan
   polytopes.  This gives a constructible diagram over the residual-wall
   stratification, rather than unrelated shellings of individual fibers.
4. Verify the 13 generic transition templates facewise on one common
   subdivision.  The relative acyclic-carrier theorem in
   `BLOCK_GORDAN_ALL_CODIM_COHERENCE.md` then supplies coherent integral
   homotopies around every higher-codimension incidence cell.
5. Only after that, place a lexicographic/discrete-Morse matching on the
   homotopy colimit.  Acyclicity must use a potential which decreases across
   both fiber pivots and parent-wall maps.

For diagonals `s=3,...,8`, only the corresponding low total degrees of this
constructible cellular complex are needed.  This is strictly smaller than a
full CAD and faithfully includes the split--remerge data that fixed-fiber
shellability omits.

The next exact bottleneck is therefore not “prove the discriminantal
arrangement shellable”—that part is already true.  It is:

> construct the codimension-one mutation/mass-transfer maps (13), including
> monochromatic losses, and prove the resulting global matching is proper and
> acyclic.

Higher coherence is no longer an independent target once those facewise maps
exist.  The revised target is compatible with the 13-wall theorem, the hard
endpoint reroute, and the known non-partial-cube warning.  No published
discriminantal or higher-Bruhat theorem located in this audit supplies it
automatically.
