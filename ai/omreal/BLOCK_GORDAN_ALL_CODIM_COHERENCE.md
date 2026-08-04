# All-codimension coherence from convex Gordan carriers

## Outcome

The codimension-two acyclic-carrier argument extends to every codimension.
Once all codimension-one specialization maps have been defined facewise on a
common subdivision, convex coordinate restrictions of the block-Gordan
fibers supply integral higher homotopies in every dimension.  No new
coherence obstruction can first appear in codimension `k>=2`.

This is a conditional coherence theorem, not a vanishing theorem.  It does
not construct a codimension-one map into an empty zero face, prove that a
monochromatic wall star has a partner block, make a global Morse matching
acyclic, or control compact support at the parent boundary.  Those are the
remaining geometric problems for diagonals `3,...,8`.

## 1. Coordinate carriers

At a fixed parent `Y`, write the block-Gordan fiber as

\[
 \Gamma_S(Y)=\left\{(w_\sigma)_{\sigma\in S}:
 \begin{array}{l}
 w_\sigma\ge0,\quad A_\sigma(Y)^Tw_\sigma=0,\\
 \displaystyle\sum_{\sigma,i}(w_\sigma)_i=1
 \end{array}\right\}.                                           \tag{1}
\]

Let `U` be any set of block-coordinate pairs `(sigma,i)`.  The coordinate
restriction

\[
 \Gamma_U(Y)=\Gamma_S(Y)\cap
       \{(w_\sigma)_i=0:(\sigma,i)\notin U\}                     \tag{2}
\]

is a face of (1).  It is empty or a compact convex polytope.  Thus every
nonempty restriction is integrally acyclic:

\[
                    \widetilde H_j(\Gamma_U(Y);\mathbb Z)=0
                    \quad(j\ge0).                                \tag{3}
\]

This includes zero block-mass faces and zero circuit-weight faces in one
coordinate system.  If `U' subseteq U`, then
`Gamma_(U')(Y) subseteq Gamma_U(Y)`.

## 2. Facewise chain-homotopy uniqueness

Let `K` be a finite cellular complex and let

\[
                  f,g:C_*(K;\mathbb Z)\longrightarrow
                      C_*(\Gamma_S(Y);\mathbb Z)                 \tag{4}
\]

be cellular chain maps.  Suppose that for every cell `tau` of `K` there is a
coordinate set `U(tau)` such that

1. `Gamma_(U(tau))(Y)` is nonempty;
2. both image chains of every face of `tau` are contained in it; and
3. `U(tau') subseteq U(tau)` whenever `tau'` is a face of `tau`.

Then `tau -> Gamma_(U(tau))(Y)` is an acyclic carrier.  The integral
acyclic-carrier theorem gives a chain homotopy

\[
                             \partial H+H\partial=f-g.            \tag{5}
\]

If `f=g` on a subcomplex, the carrier induction is relative and takes `H=0`
there.  Therefore existing zero-face agreements are preserved.

The support premise in this statement is automatic once both maps are
already defined facewise: take `U(tau)` to be the union of coordinates
appearing in their image chains over all faces of `tau`.  Either image makes
the corresponding carrier nonempty.  If the original maps preserve a
coordinate zero face, their union support also preserves it.

What is not automatic is the existence of the two maps.  On the dying
codimension-one support from
`BLOCK_GORDAN_RESIDUAL_MUTATION_MAP_NO_GO.md`, the diagram is

\[
                            \mathrm{point}\to\mathrm{point}
                                      \leftarrow\varnothing.      \tag{6}
\]

There is no target chain on the empty side.  A larger support or another
block must first repair (6).

## 3. Induction to arbitrary codimension

Assume a finite regular subdivision of the parameter space by residual
walls, and assume every oriented codimension-one incidence has a facewise
specialization map.  At a codimension-two stratum, two composites around a
square are maps of the form (4), so Section 2 supplies their homotopy.

Inductively, suppose coherent fillers have been chosen through dimension
`k-1`.  The boundary of a `k`-dimensional incidence cell gives a
`(k-1)`-cycle in the chain complex of the union-support carrier at its deepest
stratum.  That carrier is nonempty and convex, hence the cycle is an integral
boundary by (3).  Choose a filling.  The relative carrier induction makes it
agree with every previously fixed face filler.  This proves:

> **All-codimension carrier theorem.**  A facewise, support-monotone
> codimension-one block-Gordan specialization system on a common finite
> subdivision extends to a homotopy-coherent integral system over the whole
> incidence poset.  Any two such extensions are themselves coherently
> homotopic within the same union supports.

The argument applies to cubes, polygons produced by interacting flips, and
arbitrary regular incidence cells.  It does not require square/pentagon
cluster relations or a partial-cube chamber graph.

## 4. Compact-support qualification

The construction above is fiberwise and cellular.  To induce the intended
maps on compact-support cochains, the global subdivision and carrier maps
must also be proper on the chosen compactifications.  The block-Gordan
projection itself is proper, but an independently chosen escape or Morse
flow need not be.  Hence the theorem removes higher **coherence** as a new
obstruction; it does not remove the following checks:

- facewise codimension-one existence, especially at monochromatic stars;
- local finiteness and properness at parent-cell infinity;
- compatibility with the block-mass filtration which recovers
  Mayer--Vietoris; and
- acyclicity of the resulting global matching or incidence complex.

## 5. Consequence for the middle diagonals

For `s=3,...,8`, it is unnecessary to classify separate codimension-three,
four, and higher polygon relations **provided** a valid codimension-one
system is found.  Convex carriers then supply all higher homotopies.

This does not close the remaining diagonal terms.  For `s=3`, compact pair
cycles and triple split--remerge components can still survive in the global
codimension-one incidence complex.  Higher `s` have the analogous
Mayer--Vietoris groups.  Coherence ensures that this complex is well defined;
it does not prove its homology vanishes.

The exact codimension-two square matrices and the row-2599 regression are
checked by `BLOCK_GORDAN_CODIM2_DIAMOND_AUDIT.py`.  The proof above is the
dimension-independent acyclic-carrier argument behind that regression.
