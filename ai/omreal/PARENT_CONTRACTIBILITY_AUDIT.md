# Parent realization-space contractibility audit for 9DVL

## Outcome

For a realizable uniform oriented matroid \(M\) of rank four on eight elements,
the normalized parent realization space

\[
                 X=\mathcal R_{\mathrm{proj}}(M)
\]

is contractible, provided one imports the published small-ground-set statement
in Tsukamoto's 2013 paper.  The literature trace below independently proves
the same conclusion for 2,546 of the 2,604 realizable reorientation
classes.  The remaining 58 rely on Tsukamoto's blanket statement; the older
classification proves their realizability but does not itself supply a
homotopy equivalence.

This audit records that dependency explicitly.  It does **not** attribute a
topology-preserving conclusion to Bokowski--Richter Theorems 4.10 or 4.11.

## 1. Published small-ground-set input

Tsukamoto fixes arbitrary positive integers \(r,n\), defines a realization of
an oriented matroid by an \(r\)-by-\(n\) matrix, and defines its realization
space as realizing matrices modulo \(GL(r,\mathbb R)\):

* Y. Tsukamoto, *New Examples of Oriented Matroids with Disconnected
  Realization Spaces*, Discrete Comput. Geom. 49 (2013), 287--295,
  [Definition 1.2 and p. 288](https://doi.org/10.1007/s00454-012-9456-y).

Immediately after the definition, the paper states that every realizable
oriented matroid on fewer than nine elements has contractible realization
space.  The assertion is not restricted to rank three: the rank-three
specialization begins later in the paper.  Therefore it applies to every
realizable \(\operatorname{UOM}(4,8)\).

The sentence is a published assertion rather than a numbered theorem, and its
nearby reference to the oriented-matroids book is phrased as historical
background rather than as a precise proof citation.  The result is used here
as an imported theorem with that source-trace qualification.

## 2. Why the \(GL\) quotient and projective normalization agree homotopically

Write \(\mathcal R_{GL}(M)\) for Tsukamoto's quotient.  Positive independent
rescaling of the labeled columns descends to an action on this quotient.  The
common rescaling is already the scalar subgroup of \(GL(r,\mathbb R)\), so
the effective column torus is

\[
 T=(\mathbb R_{>0})^n/\mathbb R_{>0,\mathrm{diag}}
   \cong(\mathbb R_{>0})^{n-1}.
\]

For a uniform labeled configuration this action is free: a projective
transformation that rescales every labeled column and fixes the chosen
projective frame is scalar.  Its quotient is the projective realization
space.

The fixed labeled projective-frame normalization gives a global section of
this quotient.  Choose its ordered basis \(B=(b_1,\ldots,b_r)\), use the
basis columns to fix the \(GL\) gauge, and let \(c\) be the remaining frame
element.  Diagonal \(GL\), together with positive rescaling of the basis
columns and \(c\), puts \(c\) at its prescribed sign vector.  Then normalize
one chosen coordinate of every remaining column.  Uniformity guarantees that
all coordinates used as denominators are nonzero.  Hence the principal
\(T\)-bundle is globally trivial and the fixed projective-frame slice gives
the product

\[
 \mathcal R_{GL}(M)\cong
 \mathcal R_{\mathrm{proj}}(M)\times(\mathbb R_{>0})^{n-1}.
\]

For \((r,n)=(4,8)\) the extra factor is
\((\mathbb R_{>0})^7\), hence contractible.  Projection to the first factor is
a homotopy equivalence.  Tsukamoto's contractibility statement therefore
implies that the nine-dimensional normalized parent space \(X\) used in 9DVL
is contractible.

## 3. Independent catalog trace: 2,546 classes

Bokowski and Richter define reducibility by an element \(e\) to mean that every
realization after deleting \(e\) extends back across \(e\):

* J. Bokowski and J. Richter, *On the Classification of Non-Realizable
  Oriented Matroids, Part I: Generation*, Definition 4.4 and
  [Corollary 4.9, printed p. 7](https://www.math.ucdavis.edu/~deloera/MISC/LA-BIBLIO/trunk/Richter-Gebert/Richter13.pdf).

Their exhaustive search proves that, for 2,546 of all 2,628
rank-four/eight-element reorientation classes, either the chirotope or its dual
is reducible by an element.  For those classes:

1. reducibility makes the deletion forgetful map a homotopy equivalence by
   J. Richter and B. Sturmfels,
   *On the Topology and Geometric Construction of Oriented Matroids and
   Convex Polytopes*, Trans. Amer. Math. Soc. 325 (1991), 389--412,
   [Lemma 2.1](https://doi.org/10.1090/S0002-9947-1991-0994170-3);
2. deletion leaves a uniform rank-four matroid on seven elements;
3. duality identifies its realization space with that of a uniform rank-three
   matroid on seven elements; and
4. the Richter--Sturmfels rank-three theorem makes this realization space
   contractible (their theorem covers uniform rank-three matroids on at most
   eight elements).

Hence those 2,546 classes have contractible realization spaces without using
Tsukamoto's blanket statement.

After Corollary 4.9, 82 classes remain.  Bokowski--Richter report on printed
p. 9 that an additional 58 are realizable, using repeated applications of
Theorem 4.11 around one application of Theorem 4.10.  Those theorems prove
only the implication “reduced or boundary chirotope realizable implies the
original chirotope realizable.”  They do not state that a forgetful map,
boundary perturbation, or stretching map is a homotopy equivalence.

Thus the exact audit is:

| catalog part | number | topology status used here |
|---|---:|---|
| reducible \(M\) or \(M^*\) | 2,546 | independently contractible |
| additional realizable classes | 58 | contractible via Tsukamoto |
| nonrealizable classes | 24 | no nonempty realization space |
| total | 2,628 | 2,604 realizable |

The frequently mentioned oriented matroid \(EFM(8)\) is nonrealizable, so it is
not a counterexample to the claim about realizable parents; see F. Santos,
*Triangulations of Oriented Matroids*, Section 5.2.1
([author PDF](https://personales.unican.es/santosf/Articulos/Old/OMtriFinal.pdf)).

## 4. Exact consequence for all nine dual targets

For a set \(S\) of \(s\) extension signatures, put

\[
 F_S=\bigcap_{\sigma\in S}F_\sigma,\qquad
 B_S=X\setminus F_S=\bigcup_{\sigma\in S}(X\setminus F_\sigma).
\]

Poincare duality with supports and the long exact sequence of \((X,F_S)\) give

\[
 H_{10-s}(X;\mathbb Q)\longrightarrow H_c^{s-1}(B_S;\mathbb Q)
 \longrightarrow H_{9-s}(F_S;\mathbb Q)
 \longrightarrow H_{9-s}(X;\mathbb Q).
\]

Contractibility of \(X\) kills both outside groups for \(1\le s\le8\).  When
\(s=9\), the relevant sequence is

\[
 0=H_1(X)\longrightarrow H_c^8(B_S)\longrightarrow H_0(F_S)
 \longrightarrow H_0(X)=\mathbb Q.
\]

The last map is the augmentation on components, so its kernel is reduced
\(H_0\).  Consequently, including the ninth diagonal,

\[
 \boxed{\;
 \widetilde H_{9-s}(F_S;\mathbb Q)
 \cong H_c^{s-1}(B_S;\mathbb Q)
 \quad(1\le s\le9).
 \;}
\]

This is a reduction of 9DVL to nine compact-support bad-locus vanishings, not a
proof that those groups vanish.

## 5. Fallback strategies that do not need blanket contractibility

Two weaker targets remain available if the Tsukamoto input is set aside.

### Boundary-inclusive Alexander strategy

Compactify the projective-frame ambient space to \(S^9\) and set

\[
 A_S=(S^9\setminus X)\cup B_S=S^9\setminus F_S.
\]

Alexander duality gives

\[
 \widetilde H_{9-s}(F_S;\mathbb Q)
 \cong\widetilde{\check H}^{\,s-1}(A_S;\mathbb Q).
\]

This treats all nine diagonals without any assertion about the topology of
\(X\).  The price is that the common boundary term \(S^9\setminus X\) must
remain in every calculation.

### Direct \(H_5\) strategy for the fourth diagonal

The contraction--height theorem gives, for every parent element \(e\),

\[
                  X\simeq G_e(M)\subset\mathbb R^6,
\]

where \(G_e(M)\) is the nonempty-lift locus over the normalized realization
space of \(M/e\).  Alexander duality in \(S^6\) identifies

\[
 \widetilde H_5(G_e(M);\mathbb Q)
 \cong
 \widetilde{\check H}^{\,0}(S^6\setminus G_e(M);\mathbb Q).
\]

Thus proving \(H_5(X)=0\) does not require full reducibility
\(G_e(M)=\mathcal R(M/e)\): it is enough to prove that the compactified
complement of \(G_e(M)\) is connected, equivalently that no bounded
complementary component is cut out in the six-dimensional contraction base.
This is a finite, strictly weaker target for the 58 exceptional catalog
classes and is suitable for exact CAD or a Gordan-circuit cover computation.
