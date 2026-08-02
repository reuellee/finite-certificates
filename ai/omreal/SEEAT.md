# SEEAT: a single-element extension atlas theorem

**Status.**  The finite-atlas theorem below is unconditional.  It turns all
realizations of one deletion into finitely many *derived-oriented-matroid
charts*, and it makes extension feasibility constant on each chart.  The
proposed strengthening to four charts for `UOM(4,8)` is **false**: catalog row
2599 has 97,224 realizable uniform extensions, while four charts can cover at
most 96,576.  A compact exact-matrix certificate proves the counterexample.

The generic-arrangement input is standard; the certificate architecture is the
part relevant to the census.  The distinction matters: finiteness is a theorem,
while a useful small atlas remains a concrete computational and theoretical
target.

## 1. The derived arrangement

Let `M` be a realizable uniform oriented matroid of rank `r` on a labeled set
`E`, with `|E| = m`, and let

\[
Y=(y_e:e\in E)\in\mathbb R^{r\times m}
\]

be a realization.  For every ordered `(r-1)`-subset `I` of `E`, define the row
vector `a_I(Y)` by

\[
        a_I(Y)x=\det(Y_I,x).
\]

There are `q = binom(m,r-1)` such rows.  Write `A(Y)` for the resulting
`q`-by-`r` matrix and `D(Y)` for its oriented matroid.  Equivalently, `D(Y)` is
the central hyperplane arrangement in the possible positions of a missing
column `x`.

If `p` is the new element and

\[
        \sigma_I=\widehat\chi(I,p)\in\{+,-\},
\]

then the proposed uniform extension is realizable over this *fixed* `Y` if and
only if

\[
        \sigma_I a_I(Y)x>0\quad\text{for every }I.                 \tag{1}
\]

Thus `sigma` is feasible exactly when it is a tope of `D(Y)`.

## 2. The theorem

> **Single-Element Extension Atlas Theorem (SEEAT).**
> Let `M` be a realizable uniform oriented matroid.  There is a finite set of
> rational realizations
>
> \[
>        \mathcal A(M)=\{Y_1,\ldots,Y_s\}
> \]
>
> with the following properties.
>
> 1. Every realizable uniform single-element extension of `M` is realizable
>    over at least one `Y_j`.
> 2. The `Y_j` may be chosen one per nonempty generic sign stratum of the
>    maximal minors of `A(Y)`.
> 3. On one such stratum, the set of feasible extension signatures is
>    constant: it is the tope set of the common derived oriented matroid.
> 4. If a signature is infeasible on a stratum, one fixed positive-circuit
>    support blocks it throughout that stratum.  The support has size at most
>    `r+1`.  After a finite refinement by signs of smaller coordinate minors,
>    its Gordan weights are given by one cofactor formula whose entries have a
>    fixed positive sign throughout the refined chart.

### Proof

The entries of `A(Y)` are `(r-1)`-minors of `Y`.  Consequently every maximal
minor of `A(Y)` is a polynomial of degree at most `r(r-1)` in the realization
coordinates.  Discard the maximal-minor polynomials that vanish identically.
The complement of their zero sets in the realization space of `M` is cut into
finitely many strict sign strata.

On one stratum, the chirotope of `D(Y)` is fixed.  An oriented matroid's topes
are determined by its chirotope, so the feasibility of (1) is constant on the
stratum.

Suppose a uniform extension is realized by `(Y,x)`, possibly at a zero of one
of the derived determinants.  All brackets of `M` and of the extension are
nonzero.  Their signs therefore survive a sufficiently small perturbation of
`Y`, with `x` held fixed.  The perturbation can simultaneously avoid the
finitely many non-identically-zero derived determinant hypersurfaces.  Hence
every uniform realizable extension occurs on a generic stratum; degenerate
strata add no extension signatures.

Every nonempty generic stratum is an open semialgebraic set defined over the
rationals.  It contains a rational point; clearing denominators gives an
integer representative.  Taking one representative from each nonempty
stratum proves the first three assertions.

For the last assertion, reorient the rows of `A(Y)` by `sigma`.  If (1) is
infeasible, Gordan's theorem supplies a positive dependence among these rows.
An inclusion-minimal one is a circuit of a rank-at-most-`r` vector
configuration, so it uses at most `r+1` rows.  Circuit signs are fixed by the
derived chirotope.  On a refinement that fixes a nonzero coordinate minor,
the usual alternating cofactors give the dependence weights.  The cofactor
identity holds polynomially, and the refined sign conditions make all the
chosen weights positive.  The same support and formula therefore work over
the whole refined chart.  QED.

## 3. What counts as a complete certificate

A list of attractive realizations is not yet an atlas.  A proof-carrying atlas
for one parent `M` needs four objects:

1. **Chart representatives.**  Exact rational or integer matrices `Y_j` that
   realize `M`.
2. **Derived types.**  The exact maximal-minor sign vector of every `A(Y_j)`.
   A checker derives its topes; it does not trust a claimed tope list.
3. **A cover certificate.**  An exact sign-decomposition/CAD trace, or
   equivalent Positivstellensatz exclusions, proving that no other generic
   derived sign stratum meets the realization space of `M`.
4. **Catalog matching.**  Each abstract extension signature is matched against
   the union of chart topes.  Membership proves realizability.  Nonmembership
   proves nonrealizability only after item 3 has passed.

The cover certificate is the trust boundary.  Without it, the construction is
a sound generator of realizable extensions but cannot certify a negative
answer.

For a whole `(r,m+1)` catalog, chart topes can be canonicalized in bulk.  One
matrix then proves thousands of children at once.  The same chart bank is
reused through every possible deletion; dual chart banks do the same through
contractions.  This is the precise route by which SEEAT can replace repeated
per-class nonlinear searches.

## 4. The sharp single-chart capacity at `(r,m)=(4,8)`

Here the normalized projective realization space has dimension

\[
        (r-1)(m-r-1)=3\cdot3=9,
\]

and `A(Y)` has `binom(8,3)=56` rows.  Its maximal-minor discriminants have
degree at most `12`.

For a very general eight-point configuration, the relevant generic-points
arrangement has affine characteristic polynomial

\[
 \chi_{8,3}(t)=t^3-56t^2+1260t-13000.
\]

Homogenizing the 56 planes but not adding the plane at infinity adds the
common origin as the final flat, giving

\[
 \widehat\chi(t)
   =t\chi_{8,3}(t)-\chi_{8,3}(1)
   =t^4-56t^3+1260t^2-13000t+11795.
\]

Zaslavsky's formula therefore gives exactly

\[
        \widehat\chi(-1)=\boxed{26112}
\]

oriented chambers/topes, i.e. 13,056 projective chambers.  Any special
realization has no more: a generic perturbation can split chambers but cannot
merge generic chambers into a larger count.

This is substantially below the loose bound for 56 arbitrary central
hyperplanes in four-space, 55,552.  It is also visible directly in the local
catalog:

| exact quantity | value |
|---|---:|
| uniform extension signings of one `(4,8)` representative | 50,358 to 97,224 |
| topes of one generic realization | 26,112 |
| representatives needing 2 / 3 / 4 charts by raw cardinality if every abstract extension were to be covered positively | 5 / 2,525 / 98 |

So “one realization per deletion representative” cannot be the positive-only
theorem.  Four is merely the first uniform cardinality bound not ruled out by
the largest abstract extension count: `3*26112 < 97224 < 4*26112`.  No
four-chart upper bound follows from this raw count; Section 5 strengthens the
count with forced overlap and refutes such an upper bound.  In general,
nonrealizable abstract extensions mean the raw lower bounds need not be
attained by a realizability atlas.

Across the labeled `(4,8)` parents, the exact one-chart capacity for a fixed
distinguished new label is

\[
  25{,}703{,}946{,}240\cdot26{,}112
  =671{,}181{,}444{,}218{,}880,
\]

versus `1,722,704,635,330,560` labeled `(4,9)` chirotopes.  Thus two uniform
chart layers cannot even supply enough raw slots for *all* abstract extensions
with that fixed deletion: the aggregate lower bound is
`1,722,704,635,330,560 / 671,181,444,218,880 = 2.566...` charts per labeled
parent, so a uniform budget must allow a third layer.  Allowing all nine
deletions is why a small two-sided catalog atlas remains plausible despite
this count.

## 5. A counterexample to the four-chart claim

For a realizable parent `M`, write `T(Y)` for the set of uniform extension
signatures realized over `Y`, and let

\[
 U(M)=\bigcap_{Y\in\mathcal R(M)}T(Y)
\]

be the *universal core*.  Sturmfels--Ziegler's proof of connectedness of the
realizable extension space makes exactly this construction: the extension
posets supplied by all adjoint-equivalence classes have a common intersection,
and every lexicographic extension lies in it (Proposition 2.1 and its proof).
For the uniform signatures considered here the same fact also has an elementary
realization proof.  If `(a_1,...,a_r)` is an ordered basis and
`epsilon_i` are signs, put

\[
 p=\epsilon_1y_{a_1}+\delta\epsilon_2y_{a_2}+\cdots+
       \delta^{r-1}\epsilon_ry_{a_r}.
\]

For every `(r-1)`-set `I`, the first `a_i` outside `I` gives the first
nonzero coefficient of `det(Y_I,p)`.  For all sufficiently small positive
`delta`, simultaneously over the finitely many `I`, its sign is therefore
`epsilon_i chi(I,a_i)`.  This realizes the lexicographic signature over
*every* realization `Y` of `M`.

This common core gives an overlap correction that raw cardinality misses.

> **Universal-core capacity lemma.**  If every chart has at most `C` uniform
> topes and `L` distinct lexicographic uniform extensions of `M` are
> enumerated, then any `k` charts cover at most
>
> \[
>          L+k(C-L)=kC-(k-1)L                         \tag{2}
> \]
>
> distinct uniform extension signatures.

Indeed, all `L` signatures occur in every chart, so each chart can add at
most `C-L` signatures outside the common core.  This proves (2).

The exact catalog data make (2) nearly decisive.  For `(4,8)` catalog row
`2599`:

| exact quantity | value |
|---|---:|
| abstract uniform extensions `E(M)` | 97,224 |
| distinct lexicographic uniform signatures `L` | 2,624 |
| maximum topes in one chart `C` | 26,112 |
| four-chart capacity `4C-3L` | **96,576** |
| `E(M) - (4C-3L)` | **648** |
| child reorientation classes after exact canonicalization | 5,902 |
| extension-signature multiplicities of those classes | `15x8 + 5,705x16 + 182x32` |

Before the realizability certificates are consulted, the counts give a very
small falsification gate:

> **Four-chart obstruction.**  If at most 647 of row 2599's 97,224 abstract
> extensions are non-realizable, then at least 96,577 are realizable, while
> four charts cover at most 96,576.  Its realizability-atlas width is then at
> least five, and the four-chart claim is false.

Conversely, four charts for this parent are not even *cardinally possible*
unless at least 648 of its abstract extensions are non-realizable.  Finding
648 would not prove that four charts suffice; it would only clear this
necessary condition.

The gate fires in the strongest possible way.  Exact canonicalization collapses
the 97,224 labeled extension signatures to 5,902 child reorientation classes.
The certificate `data/seeat_parent2599_realizations.npz` supplies one integer
`4x9` realization for every one of those classes.  The verifier independently
re-enumerates all extensions, canonicalizes them, and recomputes all 126
brackets of all 5,902 matrices in integer arithmetic.  Thus all 97,224 abstract
extensions are realizable.

> **Four-chart counterexample theorem.**  The realizability-atlas width of
> `(4,8)` catalog row 2599 is at least five.  In particular, a universal
> four-chart SEEAT for `UOM(4,8)` is false.

*Proof.*  Every one of the parent's 97,224 abstract uniform extensions is
realizable by the exact certificate.  Every chart has at most 26,112 topes and
contains the same 2,624 lexicographic extensions.  By the universal-core
capacity lemma, four charts cover at most
`4*26112 - 3*2624 = 96576 < 97224` signatures.  QED.

`four_chart_gate.py` verifies the standalone certificate or, independently,
evaluates the same condition from the completed sweep checkpoint.  It runs no
LP and no realization search.  The standalone command is

```console
python ai/omreal/four_chart_gate.py \
  --realizations ai/omreal/data/seeat_parent2599_realizations.npz
```

The distinction is substantive.  Contractibility of a parent realization
space does not imply a four-point transversal for the extension-feasibility
regions, and connectedness of the realizable extension poset does not imply
one either.  The exact counterexample shows that neither fact can be upgraded
to a four-chart bound in this cell.

## 6. The actual next target

The theorem removes the conceptual obstacle; atlas width is now the only hard
quantity.  The next experiment should not rerun realizability searches.  It
should:

1. search for a five-chart cover of row 2599, which is now the first possible
   width;
2. enumerate the derived topes of the already stored exact `(4,8)` matrices;
3. canonicalize the resulting `(4,9)` extensions and take the union over all
   nine deletions and, separately, the dual contraction charts;
4. measure uncovered catalog classes;
5. add a new realization of a parent only when it covers many previously
   uncovered classes; and
6. seek a semialgebraic cover certificate only after the empirical atlas width
   is known.

That computation is arrangement enumeration plus canonical set union.  It
contains no nonlinear realization attempt per child.  If a small chart bank
covers the census, the remaining theorem problem is sharply stated: certify
that its derived sign strata exhaust each nine-dimensional parent realization
space.

## References

* H. Koizumi, Y. Numata, A. Takemura, *On intersection lattices of hyperplane
  arrangements generated by generic points*, Annals of Combinatorics 16
  (2012), 789–813, [arXiv:1009.3676](https://arxiv.org/abs/1009.3676).
* B. Sturmfels, G. M. Ziegler, *Extension spaces of oriented matroids*,
  Discrete & Computational Geometry 10 (1993), 23–45,
  [open preprint](https://www.mi.fu-berlin.de/math/groups/discgeom/ziegler/Preprintfiles/020PREPRINT.pdf).
* T. Zaslavsky, *Facing up to arrangements*, Memoirs of the AMS 154 (1975).
