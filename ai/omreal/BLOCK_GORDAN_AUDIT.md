# Block-Gordan resolution: exact audit, formal no-go, and a local pivot cube

## Outcome

The proposed block-Gordan space is a correct proper resolution of the union
of bad loci.  With zero blocks allowed and only the **sum of all blocks**
normalized, its fiber is nonempty exactly over

\[
                         B_S=\bigcup_{\sigma\in S}B_\sigma.
\]

Every fiber is a compact convex polytope, and proper base change gives a
functorial derived compact-support equivalence

\[
              R\Gamma_c(\Gamma_S;R)\simeq R\Gamma_c(B_S;R)       \tag{1}
\]

for any coefficient ring `R`.  Thus the construction correctly retains zero
weights, circuit-support changes, and split--remerge attachments.

It does **not**, by itself, prove a middle diagonal.  Stratifying by the
positive block masses recovers the ordinary compact-support
Mayer--Vietoris complex of the bad-locus cover exactly.  Fixed-fiber
shellability therefore cannot remove the unresolved boundary maps.  A fully
explicit family of `56 by 4` strict-feasibility systems below has nonzero
`H_c^(s-1)` for every `s=3,...,8`, despite nonzero rows, full row span,
proper pairwise-incomparable feasibility regions, and singleton normalized
Gordan fibers.  Any successful index theorem must use the special
third-compound/Koszul form of the actual matrices, not only the block-Gordan
format or convexity of its fibers.

There is nevertheless one new exact gain in the actual row-2599 data.  The
support-frozen hard triple from `THIRD_DIAGONAL_E1_REDUCTION.md` lies at one
corner of a genuine three-dimensional cube of positive-circuit pivots.  Its
opposite corner has a degree-two label and is killed by the pencil lemma.
Exact enumeration finds `18,480` such flexible corners.  No flexible corner
is reachable by changing only one or two witness blocks, so the example calls
for a coordinated multi-block matching rather than an independent greedy
pivot.  Persistence of these cubes across cofactor walls remains open.

No diagonal is promoted by this note.

## 1. Definition and union semantics

For a fixed normalized parent realization `Y`, let `A_sigma(Y)` be the
`56 by 4` matrix whose rows are the signed derived normals

\[
                           \sigma_I a_I(Y).
\]

Put

\[
 P_\sigma(Y)=\{\lambda\in\mathbb R_{\ge0}^{56}:
     {\bf1}^T\lambda=1,\ A_\sigma(Y)^T\lambda=0\}.      \tag{2}
\]

Gordan's strict alternative says

\[
 P_\sigma(Y)\ne\varnothing
 \quad\Longleftrightarrow\quad
 \nexists p\in\mathbb R^4\quad A_\sigma(Y)p>0
 \quad\Longleftrightarrow\quad Y\in B_\sigma.          \tag{3}
\]

For a finite signature set `S`, define

\[
 \Gamma_S=\left\{(Y,(w_\sigma)_{\sigma\in S}):
 \begin{array}{l}
   Y\in X,\quad w_\sigma\in\mathbb R_{\ge0}^{56},\\
   A_\sigma(Y)^Tw_\sigma=0\quad(\sigma\in S),\\
   \displaystyle\sum_{\sigma\in S}{\bf1}^Tw_\sigma=1
 \end{array}\right\}.                                  \tag{4}
\]

The individual blocks in (4) are **not** normalized separately.  This is
the point that makes (4) a union model.  Write

\[
                         t_\sigma={\bf1}^Tw_\sigma.
\]

If `(Y,w)` satisfies (4), some `t_sigma` is positive.  Then
`lambda_sigma=w_sigma/t_sigma` belongs to (2), so `Y in B_sigma subset B_S`.
Conversely, if `Y in B_sigma`, choose `lambda_sigma in P_sigma(Y)`, put that
vector in the `sigma` block, and put zero in every other block.  Hence

\[
                         \operatorname{im}(\Gamma_S\to X)=B_S.   \tag{5}
\]

More precisely, if

\[
             T(Y)=\{\sigma\in S:P_\sigma(Y)\ne\varnothing\},
\]

then the fiber of (4) is the join, embedded in disjoint coordinate blocks,

\[
        \Gamma_S(Y)=\mathop{\ast}_{\sigma\in T(Y)}P_\sigma(Y)
        =\operatorname{conv}\!\left(
          \bigsqcup_{\sigma\in T(Y)}P_\sigma(Y)\right).         \tag{6}
\]

Equations (4) and nonnegativity show directly that (6) is a compact convex
polytope.  The join description also shows why a signature which is good at
`Y` contributes only its zero block, while every mixture of bad signatures
is retained.

## 2. Properness and compact-support equivalence

The space `Gamma_S` is closed relative to

\[
                   X\times\Delta^{56|S|-1};
\]

all its equations are continuous and the simplex is compact.  If `K subset
B_S` is compact, its inverse image is closed in the compact space
`K times Delta`.  Therefore the projection

\[
                           p_S:\Gamma_S\longrightarrow B_S       \tag{7}
\]

is proper.

Let `R` be any coefficient ring.  Proper base change identifies the stalk of
\(Rp_{S*}R_{\Gamma_S}\) at `Y` with

\[
                          H^*(\Gamma_S(Y);R).                     \tag{8}
\]

Every fiber in (6) is nonempty, connected, and contractible.  Thus the unit

\[
                          R_{B_S}\longrightarrow Rp_{S*}R_{\Gamma_S}
\]

is a stalkwise quasi-isomorphism.  Since `p_S` is proper,
\(Rp_{S!}=Rp_{S*}\), and

\[
 \begin{aligned}
 R\Gamma_c(\Gamma_S;R)
   &\simeq R\Gamma_c(B_S;Rp_{S!}R_{\Gamma_S})\\
   &\simeq R\Gamma_c(B_S;R_{B_S}).                     \tag{9}
 \end{aligned}
\]

This proves (1).  The argument is stronger and cleaner than choosing a
Gordan witness continuously; a continuous selection need not behave well
when the kernel polytope gains a face.

The construction is functorial in the signature set.  If `S subset S'`,
zero-padding the new blocks defines a closed embedding

\[
                         \Gamma_S\hookrightarrow\Gamma_{S'}      \tag{10}
\]

over `B_S subset B_(S')`, and the units used in (9) commute with (10).  Thus
restriction maps, not only isolated cohomology groups, can be computed in
the block model.

For comparison, normalizing **every** nonzero block separately gives the
intersection model

\[
 \widehat\Gamma_T=\{(Y,(\lambda_\sigma)_{\sigma\in T}):
       \lambda_\sigma\in P_\sigma(Y)\text{ for every }\sigma\in T\}
       \longrightarrow I_T:=\bigcap_{\sigma\in T}B_\sigma.      \tag{11}
\]

Its fibers are the products `prod_(sigma in T) P_sigma(Y)`, so the same
proper-base-change proof gives

\[
                    R\Gamma_c(\widehat\Gamma_T;R)
                    \simeq R\Gamma_c(I_T;R).                     \tag{12}
\]

## 3. The block-mass filtration is exactly Mayer--Vietoris

Let `Gamma_T^circ` be the locally closed stratum of (4) on which

\[
                       t_\sigma>0\iff\sigma\in T.
\]

Dividing each positive block by its mass gives a canonical homeomorphism

\[
 \Gamma_T^\circ
   \cong \operatorname{relint}\Delta_T\times\widehat\Gamma_T,
 \qquad \dim\operatorname{relint}\Delta_T=|T|-1.        \tag{13}
\]

Consequently

\[
 H_c^n(\Gamma_T^\circ;R)
       \cong H_c^{n-|T|+1}(I_T;R).                      \tag{14}
\]

Filter `Gamma_S` by the closed subsets on which at most `r` block masses are
positive.  The successive stratum is the disjoint union of (13) over
`|T|=r`.  After shifting by the open-simplex dimension in (14), the resulting
cohomological spectral sequence is

\[
 E_1^{p,q}=\bigoplus_{\substack{T\subseteq S\\|T|=p+1}}
                 H_c^q(I_T;R)
       \Longrightarrow H_c^{p+q}(B_S;R),               \tag{15}
\]

with the alternating restriction maps, up to the usual orientation sign of
the block simplex.  This is precisely compact-support Mayer--Vietoris for the
finite closed cover `{B_sigma}`.

For `|S|=s`, the target total degree `s-1` receives the signature-level terms

\[
             H_c^{s-r}(I_T;R),\qquad |T|=r.             \tag{16}
\]

No group in (16) vanishes merely because the weight fiber in (6) is convex.
The zero-block faces are exactly what attach the terms of (15); deleting
them would destroy the boundary maps and can lose a split--remerge class.

Filtering each fixed polytope further by coordinate supports leads back to
the circuit resolution.  Its vertices are support-minimal nonnegative
dependences and have support at most five.  A triangulation of the whole
polytope requires simplices spanned by several such circuit vertices, so it
reintroduces multiple circuit intersections rather than replacing them.
The `(s+1)`-fold truncation in `FOURTH_DIAGONAL_FIVEFOLD.md` remains the
correct low-total-degree statement.

## 4. Why the cited shellability theorems do not close (15)

The two suggested precedents are useful fixed-fiber results, but neither is
a parameterized wall-compatibility theorem.

* Novik--Postnikov--Sturmfels, *Syzygies of Oriented Matroids*, constructs a
  cellular resolution from the bounded complex of one fixed affine oriented
  matroid.  Its exactness uses contractibility of specified essential
  subcomplexes of that fixed bounded complex.  It does not identify the
  boundary maps of a family whose oriented matroid changes with `Y`.
* He--Simpson--Xie, *Total positivity for matroid Schubert varieties*, proves
  that the nonnegative compactification associated with one fixed linear
  subspace `V subset R^E` is a shellable regular CW ball, with cells indexed
  by intervals of acyclic flats.  In the present problem the subspace is
  `ker A_sigma(Y)^T`; its acyclic flats and positive circuits change when `Y`
  crosses a derived wall.

For one fixed `Y`, `P_sigma(Y)` is already a convex polytope and hence has a
shellable triangulation.  The missing assertion is much stronger: one needs
pulling or Morse data which restricts compatibly when circuit vertices merge,
appear, or disappear on the 52 derived-wall types.  Neither cited theorem
provides that assertion.  Bistellar changes of individually shellable fibers
do not preserve a chosen shelling or a chosen acyclic matching.

Primary references:

* <https://arxiv.org/abs/math/0009241>
* <https://arxiv.org/abs/2310.18925>

## 5. A formal no-go in the exact numerical block format

The following construction shows sharply what information a future index
theorem must use.

Fix `s in {3,...,8}` and write

\[
 X=\mathbb R^9=\mathbb R_z^{10-s}\times\mathbb R_u^{s-1}.
\]

Choose `s` centers `c_j` on the first coordinate axis, separated by distance
four, and put

\[
                  g_j(z)=\lVert z-c_j\rVert^2-1.       \tag{17}
\]

For each `j`, define a `56 by 4` matrix `A_j(z,u)` with rows

\[
 \begin{array}{rcl}
 a_1&=&(1,g_j^2,0,0),\\
 a_2&=&(-1,g_j^2,0,0),\\
 a_3&=&(0,1,0,0),\\
 a_4&=&(0,0,1,0),\\
 a_5&=&(0,0,0,1),\\
 a_6=\cdots=a_{56}&=&(0,1,0,0).
 \end{array}                                           \tag{18}
\]

Every row in (18) is nonzero, and the rows span `R^4` even when `g_j=0`.
If \(g_j\ne0\), the private witness

\[
                              p=(0,1,1,1)
\]

satisfies every strict inequality `A_jp>0`.  If `g_j=0`, the first two
inequalities would require both `p_1>0` and `-p_1>0`, which is impossible.
Thus

\[
 F_j=X\setminus B_j,
 \qquad B_j=\{g_j=0\}\cong S^{9-s}\times\mathbb R^{s-1}.        \tag{19}
\]

The cylinders `B_j` are pairwise disjoint, so the open regions `F_j` are
proper and pairwise incomparable.

The normalized Gordan equations are equally explicit.  For
`w in Delta^55`, (18) gives

\[
 \begin{aligned}
 w_1-w_2&=0,\\
 g_j^2(w_1+w_2)+w_3+\sum_{i=6}^{56}w_i&=0,\\
 w_4&=0,\\
 w_5&=0.
 \end{aligned}                                         \tag{20}
\]

All weights are nonnegative.  Hence (20) has no normalized solution off
`B_j`, while on `B_j` its unique solution is

\[
                        (w_1,w_2,w_3,\ldots,w_{56})
                        =(1/2,1/2,0,\ldots,0).          \tag{21}
\]

Because the bad cylinders are disjoint, the `s`-block resolution is actually
homeomorphic to their disjoint union.  Compact-support Kunneth gives, for
every component,

\[
 H_c^{s-1}\!\left(S^{9-s}\times\mathbb R^{s-1};\mathbb Q\right)
 \cong
 H^0(S^{9-s};\mathbb Q)\otimes
 H_c^{s-1}(\mathbb R^{s-1};\mathbb Q)
 \cong\mathbb Q.                                       \tag{22}
\]

Therefore

\[
                     H_c^{s-1}(B_1\cup\cdots\cup B_s;\mathbb Q)
                     \cong\mathbb Q^s\ne0.             \tag{23}
\]

This example has the same base dimension, number of rows, private witness
dimension, block normalization, strict Gordan semantics, row nonvanishing,
and full row span as the project.  It even has the proper/incomparable
hypothesis and singleton fibers.  What it deliberately lacks is the special
identity

\[
                    \ker(\Lambda^3T_Y)=K_Y\wedge\Lambda^2\mathbb R^8
\]

and the parent-chirotope restrictions on its rows.  Consequently no theorem
using only the formal properties audited in Sections 1--3 can prove any of
the diagonals `s=3,...,8`.

The exact matrix checks are in `BLOCK_GORDAN_FORMAL_NO_GO.py`.

## 6. Exact local pivot cube at the hard third-diagonal triple

The formal no-go does not make the block construction useless.  It changes
the interpretation of the strongest saved support-frozen obstruction.

At the exact row-2599 pattern-zero chart, the three signatures numbered
`0,4,3` have the positive circuit vertices

```text
Q_0 = 123/134/267/258/468
Q_4 = 123/256/127/357/478
Q_3 = 123/256/356/127/347.
```

Their union has degree vector `(3,5,5,4,4,4,5,3)` and is support-plane
rigid.  Retaining the full normalized positive-kernel polytopes reveals the
following strict positive one-exchange vertices:

```text
R_0 = 134/234/267/258/468
R_4 = 134/256/127/357/478
R_3 = 134/256/356/127/347.
```

For each `j`, `Q_j` and `R_j` share four triples.  Their six signed normals
have rank four, so the normalized kernel slice supported on their union has
dimension

\[
                              6-4-1=1.
\]

Both endpoints are strict support-minimal positive circuits.  They are
therefore the endpoints of an actual edge of `P_j(Y_0)`.  Fixing the three
block masses, the product of these edges is a literal 3-cube inside the
block-Gordan fiber.

At its opposite corner, the support union of `R_0,R_4,R_3` has degree vector

\[
                              (2,5,5,5,4,4,5,3).        \tag{24}
\]

Label 1 has degree two, so the projective-plane-pencil lemma gives
`H_c^0=0` for the corresponding triple circuit-piece intersection.

The exact one-exchange census is stronger:

| signature | positive vertices including the original |
|---:|---:|
| 0 | 52 |
| 4 | 34 |
| 3 | 52 |

Their product has `91,936` corners, stratified as follows.

| minimum union degree | fixed partner | corners |
|---:|:---:|---:|
| 2 | no | 18,480 |
| 3 | no | 49,376 |
| 4 | no | 23,963 |
| 5 | no | 117 |

Every one of the `18,480` pencil-flexible corners has label 1 of degree two.
Every such corner differs from the original in **all three** witness blocks;
no one-block or two-block greedy pivot reaches the formal exit.

This proves that the saved hard triple is an obstruction only to a
support-frozen or block-independent argument.  It is positive evidence for a
coordinated cubical matching.  It is not yet a global cancellation: a chosen
positive circuit vertex can disappear when one of its cofactors reaches a
derived wall, and the local cube does not by itself identify the component
sheaf or the compact-support restriction maps along that wall.

The exact checker is `BLOCK_GORDAN_HARD_TRIPLE_PIVOT.py`.

## 7. Precise surviving theorem target

A block-Gordan proof of any middle diagonal now requires a theorem of the
following genuinely parameterized form.

1. Stratify the parent cell simultaneously by all circuit-cofactor signs and
   rank drops for the relevant signatures.
2. On each stratum, choose a labeled pulling/cubical subdivision of the
   polytopes `P_sigma(Y)`.
3. Match cells in coordinated multi-block cubes, not one block at a time.
4. Prove that the matching restricts under zero-block faces, zero-weight
   faces, and every codimension-one circuit birth/death or merger.
5. Show that no critical total cell remains in degree `s-1` after adjoining
   the compact-support boundary at infinity.

The first finite test should be the persistence of the cube in Section 6
through each adjacent derived-wall stratum.  Passing that test would attack
the genuine `E_1^(2,0)` obstruction for `s=3`.  Failure returns an exact
cofactor-wall cycle, which is precisely the boundary datum missing from the
current atlas.

Fixed-fiber shellability supplies step 2 only.  Steps 3--5 are the unresolved
mathematics, and (15) proves that they cannot be omitted.

## Reproduction

```console
python ai/omreal/BLOCK_GORDAN_FORMAL_NO_GO.py
python ai/omreal/BLOCK_GORDAN_HARD_TRIPLE_PIVOT.py
```

Both scripts use exact integer/rational arithmetic.  Neither claims a new
diagonal vanishing.
