# Witness-rank stratification of the 9DVL incidence space

This note records the proof-safe part of a projective-frame attack on the
still-open 9DVL diagonals.  It gives a reduction for diagonals seven through
nine, but proves no new diagonal.  An exact four-signature certificate then
shows that restricting to independent witnesses does not remove the known
nonconvex parent projection, even for a proper pairwise-incomparable family.

## 1. Projectivized witnesses

For `|S|=s`, recall

\[
 Z_S=\{(Y,(p_\sigma)):Y\in X,\quad
       \sigma_Ia_I(Y)p_\sigma>0\}.
\]

Normalize each private column to unit length and call the resulting space
`\bar Z_S`.  Positive rescaling has contractible orbits, so

\[
                     \bar Z_S\simeq Z_S\simeq F_S.     \tag{1}
\]

It is an open semialgebraic manifold of dimension `9+3s`.  Let

\[
 \bar Z_S^{\rm fr}=\{(Y,(p_\sigma))\in\bar Z_S:
                 \operatorname{rank}(p_\sigma)_{\sigma\in S}=4\}. \tag{2}
\]

Every product of nonempty witness chambers contains a full-rank tuple for
`s\ge4`: choose columns successively outside the span of those already
chosen.  Thus (2) is dense and nonempty in every incidence fiber.

## 2. Codimension and the high-diagonal reduction

The determinantal variety of `4 by s` matrices of rank at most three has
codimension

\[
                         (4-3)(s-3)=s-3.               \tag{3}
\]

Removing zero columns and quotienting their independent positive scales does
not change (3).  Since the incidence inequalities are open, the closed
relative complement

\[
                    D_S=\bar Z_S\setminus\bar Z_S^{\rm fr}
\]

has semialgebraic codimension at least `s-3`.

We use the elementary semialgebraic general-position lemma: if `A` is a
closed semialgebraic subset of an `n`-manifold `T` with `dim A\le n-c`, then

\[
 H_i(T\setminus A;R)\longrightarrow H_i(T;R)
 \quad\begin{cases}
 \text{is an isomorphism},&i<c-1,\\
 \text{is surjective},&i=c-1.
 \end{cases}                                           \tag{4}
\]

Indeed, triangulate compatibly with `A` and put cycles and bounding chains in
PL general position with respect to the `A`-subcomplex.  This proof works for
every coefficient ring `R` and for the noncompact manifolds here.

The diagonal degree is `9-s`.  For `s=7,8,9`, it is strictly below `s-4`, so
(1)--(4) give the proof-safe reduction

\[
 \boxed{\widetilde H_{9-s}(\bar Z_S^{\rm fr};R)
       \cong \widetilde H_{9-s}(F_S;R),\qquad s=7,8,9.} \tag{5}
\]

No analogous conclusion reaches the target degree for `s\le6`; at `s=4`
the rank-deficient locus has only codimension one.  Equation (5) is a
reduction, not a vanishing theorem.

## 3. Exact full-frame no-go

The row-2599 affine family from `DOUBLE_CONTRACTION_FIBERS.md` strengthens to
a direct frame test.  Let `p=L-R` be its first extension witness and let the
second signature be feasible at the two ends but Gordan-infeasible throughout
`1/2\le u\le3/2`.  Add the fixed columns

\[
 q=(339,-435,-214,201)^T,
 \qquad r=(-319,147,82,194)^T.                         \tag{6}
\]

Their signatures stay fixed on the whole parent line and equal

\[
 71899532269460528,
 \qquad 13946487285424257.                             \tag{7}
\]

Together with the first two signatures, these are four proper pairwise-
incomparable feasibility regions.  Twelve exact ordered separators certify
this: each consists of an integer row-2599 chart, a strict integer extension
witness for one signature, and a support-at-most-five positive integer
Gordan circuit for the other.

At `u=0` and `u=2`, use the stored endpoint witness for the second signature.
The ordered frames `(p,p_2,q,r)` have exact determinants

\[
 2000096446698665899,
 \qquad 61638912983024729024.                          \tag{8}
\]

Both ends therefore lie in the same positively oriented full-rank frame
chart, while the middle interval has no second witness at all.  The
projection of that full-rank incidence stratum to the affine parent line has
a disconnected slice.

This rules out the claims that full witness rank restores height-line
convexity, that the raw parent projection of one oriented frame chart is
linewise convex, or that the old contraction gap is caused only by
rank-deficient witnesses.  It does not show that the full frame stratum
itself is disconnected, nor that its image in fixed-frame coordinates is
nonconvex: paths may go around the affine gap, and the frame varies between
the endpoints.  The exact verifier is

```console
python ai/omreal/verify_witness_frame_stratification.py
```

## 4. Remaining viable target

For `s=7,8,9`, cover `\bar Z_S^{fr}` by oriented charts indexed by independent
witness quadruples.  Sending one quadruple to the coordinate frame makes its
four signatures prescribe the signs of all `3 by 3` minors of the four
row-deleted parent matrices.  A successful frame proof must compute the
topology of these compatible row-deletion strata and their transition maps.
The exact gap above shows that convexity or linewise acyclicity cannot replace
that computation.
