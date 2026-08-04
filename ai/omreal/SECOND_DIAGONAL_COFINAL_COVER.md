# Cofinal five-circuit cover for the second diagonal

## Statement

For a signature `rho` and a set `Q` of parent triples, put

\[
 C_{\rho,Q}=\left\{Y\in X:\exists\lambda\in\Delta_Q,
       \sum_{I\in Q}\lambda_I\rho_Ia_I(Y)=0\right\}.
\]

If `Q'` is contained in `Q`, then

\[
                         C_{\rho,Q'}\subseteq C_{\rho,Q}. \tag{1}
\]

Indeed, a witness on `Q'` is a witness on `Q` after padding its weight vector
by zeros.  Gordan's alternative and Caratheodory give a positive dependence
on at most five of the 56 derived normals at every bad parent realization.
Every set of at most five triples is contained in a five-set.  Consequently

\[
             B_\rho=\bigcup_{|Q|=5}C_{\rho,Q}.          \tag{2}
\]

This is a finite closed semialgebraic cover, so it may replace the cover by
all supports of sizes one through five in the compact-support
Mayer--Vietoris spectral sequence.

## Consequences for the unresolved second diagonal

1. Every single cover piece still has `H_c^0=H_c^1=0`: five triples have
   only fifteen label occurrences, so some one of the eight parent labels
   occurs at most once, and the projective-plane-pencil lemma applies.
2. Every pair index on the `E_1` page is now of type `5+5`.  There are no
   independent `3+5`, `4+4`, or `4+5` pair generators.
3. The weight-gauge dimension of a `5+5` relative interior is at least one.
   There are eight log-weight ratios and the effective positive column torus
   has rank at most seven.
4. Structural three- and four-circuits have not disappeared.  They occur on
   simplex faces, as boundary strata of the five-support incidences.  In
   particular, the previously found `4+5`, `beta=0` loci remain relevant to
   compactness and to the restriction maps, but not as separate cover
   indices.

Thus the second diagonal remains the injectivity problem

\[
 \bigoplus_{\alpha<\beta}H_c^0(C_\alpha\cap C_\beta)
 \longrightarrow
 \bigoplus_{\alpha<\beta<\gamma}
 H_c^0(C_\alpha\cap C_\beta\cap C_\gamma),             \tag{3}
\]

with every index in (3) a five-support piece.  Cofinality removes spurious
lower-support bookkeeping; it does not prove (3) injective, since two
distinct five-sets need not lie in a common larger allowed support.

## Proof status

Equations (1)--(2) and the four consequences above are proved.  Injectivity
of (3), and hence the second diagonal, remains open.

## What circuit exchange does prove

There is a genuine local contraction for two maximal pieces carrying the
**same** signature.  It does not extend to the cross-signature terms which
remain in (3).

> **Same-signature exchange lemma.**  Let `Q` and `R` be distinct five-sets
> of parent triples whose union is pencil-rigid.  For every
>
> \[
>       Y\in C_{\rho,Q}\cap C_{\rho,R}
> \]
>
> there is a five-set `T`, distinct from `Q` and `R`, such that
>
> \[
>       Y\in C_{\rho,Q}\cap C_{\rho,R}\cap C_{\rho,T}.       \tag{4}
> \]

To prove this, first choose support-minimal nonnegative dependences inside
`Q` and `R`.  If either has support at most four, pad that support to a
five-set other than `Q` and `R`; zero-padding the weights proves (4).
Otherwise the two witnesses are strict positive circuits with supports
exactly `Q` and `R`.  Put `U=Q union R`.  Pencil rigidity gives

\[
  3|U|=\sum_{e=1}^8\deg_U(e)\ge24,
  \qquad\text{so}\qquad |U|\ge8.                       \tag{5}
\]

In the common reorientation, let `K` be the cone of nonnegative dependences
on the columns indexed by `U`.  The sum of the two strict circuit vectors is
positive on every coordinate of `U`; hence `K` is full-dimensional in the
kernel on `U`.  Since the derived normals have rank at most four,

\[
       \dim K=|U|-\operatorname{rank}(A_U)\ge |U|-4\ge4. \tag{6}
\]

The cone is pointed, so it has at least four extreme rays.  Extreme rays are
support-minimal nonnegative dependences and therefore have support at most
five.  Besides the rays on `Q` and `R`, choose a third; if its support is
smaller than five, pad it to a five-set distinct from `Q,R`.  This proves
(4).

Consequently every same-signature pair intersection in the pencil-rigid row
is covered by its triple intersections.  In particular, the basis class of
one compact connected component has a nonzero image under `d_1`: a nonempty
triple intersection inside that component has a compact connected component
and restriction of its characteristic class is nonzero.  This does **not**
prove injectivity for a linear combination of pair components; cancellations
around a cycle of triple intersections remain possible.

There is a related boundary pivot for arbitrary signatures.  Let `K` be a
compact component of a maximal pair
`C_(rho,Q) intersection C_(eta,R)`.  Some point of `K` has a positive circuit
with proper support `P subsetneq Q` or `P subsetneq R`.  Otherwise both
five-circuit conditions are strict and rank four everywhere on `K`, so their
intersection is open in `X`; because it is also a connected component of a
closed semialgebraic set, compactness would make it a compact clopen component
of the connected open nine-manifold `X`, which is impossible.

Suppose `P subsetneq Q`.  Minimal positive circuits have size at least three:
two distinct derived normals cannot be proportional, since two distinct
parent triples spanning one projective plane would violate parent uniformity.
If `P union R` is not pencil-rigid, choose a five-set `T` containing `P`,
different from `Q,R`, and preserving one of its deficient labels (all added
triples may be chosen to omit that label).  Then both `Q union T` and
`R union T` are not pencil-rigid: the first has at most seven triples, while
the second retains the chosen degree-two or fixed-partner defect.  Therefore

\[
 H_c^0(C_{\rho,Q}\cap C_{\rho,T})=
 H_c^0(C_{\eta,R}\cap C_{\rho,T})=0.                  \tag{6a}
\]

A compact component of the triple intersection through the chosen boundary
point is contained in `K`.  Its row in `d_1` consequently receives a nonzero
entry from the `Q,R` component and no entry from either of the other two pair
groups in (6a).  Thus a kernel coefficient on `K` must be zero.

This proves a sharper localization: any coefficient in `ker(d_1)` can be
supported only on compact maximal-pair components whose every circuit-drop
boundary is still pencil-rigid after pairing the smaller circuit with the
other maximal five-support.  In particular, maximal cofinalization does not
erase the earlier `4+5` residue; it reappears exactly as the hard boundary
where this private-row pivot stops.  Deeper simultaneous wall strata must be
handled compatibly as well.

## Exact cross-signature obstruction

The cone argument uses one reorientation.  It fails sharply for two
different signatures.  At the exact row-2599 pattern-zero chart, signatures
`rho_0,rho_4` have the strict positive circuits

\[
 \begin{aligned}
 Q&=123/134/267/258/468,\\
 R&=123/256/127/357/478.
 \end{aligned}                                         \tag{7}
\]

Their union is pencil-rigid and the supports meet only in `123`.  Let
`delta_I=rho_{0,I}rho_{4,I}`.  On each of the two support differences,
`delta` takes both signs:

\[
 \begin{array}{c|c}
 Q\setminus R&\delta=(+,+,-,+)\\
 R\setminus Q&\delta=(-,-,+,-)
 \end{array}                                           \tag{8}
\]

up to reversing both sign conventions.  Write `u` and `v` for the two
signed coefficient vectors in the common unsigned kernel.  If
`alpha u+beta v` is nonnegative after reorientation by `rho_0`, then its
coordinates on `R minus Q`, together with (8), force `beta=0`; its remaining
coordinates force `alpha>=0`.  Thus the only `rho_0`-positive ray in
`span(u,v)` is the original ray `R_{>=0}u`.  Symmetrically, the only
`rho_4`-positive ray in that span is `R_{>=0}v`.

Hence the same-signature exchange proof has no cross-signature analogue even
for an exact positive, proper, incomparable, pencil-rigid parent/signature
pair.  Other active circuits may still produce triple intersections; (8)
rules out only the tempting two-witness conic contraction, not injectivity of
(3) itself.

The arithmetic-only checker verifies the cofinal padding counts, both exact
positive dependences and their minimality, pencil rigidity, properness and
incomparability from the stored one-bit charts, and the mixed-sign obstruction
(8):

```console
python ai/omreal/verify_second_diagonal_nerve.py
```
