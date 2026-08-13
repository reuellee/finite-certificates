# Diagonal two: exchange-saturated support-drop theorem

## Result

Let `X` be the normalized realization space of a realizable uniform
rank-four oriented matroid on eight labels.  For an extension signature
`sigma`, let `B_sigma` be its Gordan bad locus in `X`.

> **Second-diagonal theorem.**  For every pair of valid extension signatures
> `rho, eta`, every connected component of
> `B_rho intersection B_eta` is noncompact.

Semialgebraic local connectedness and finiteness of components identify this
statement with
`H_c^0(B_rho intersection B_eta; Z)=0`.

Together with the integral single-region vanishing and compact-support
Mayer--Vietoris isomorphism already proved in
`SECOND_DIAGONAL_SINGLE_REGION_H7_AUDIT.md`, this gives

\[
 H_c^1(B_\rho\cup B_\eta;\mathbb Z)
 \cong H_c^0(B_\rho\cap B_\eta;\mathbb Z)=0.
\]

Supported duality therefore proves the second entry of the Nine-Diagonal
Vanishing Lemma integrally:

\[
                    \boxed{\widetilde H_7(F_{\{\rho,\eta\}};\mathbb Z)=0}.
\]

The proof has two parts.  A point carrying a nonstructural positive minimal
circuit of size three or four has an exchange-saturated common elementary
shear.  A hypothetical compact component must contain such a point, because
strict five-circuits and structural small circuits are locally persistent and
would otherwise make the component clopen in `X`.

## 1. Moving witnesses and the low-source gate

At `T in B_rho`, normalize a Gordan relation to have nonnegative weights
summing to one, and choose one with support minimal under inclusion.  Its
support is a positive linear circuit among the signed derived normals

\[
                         z_I=\rho_I a_I(T)\in W^*,
                         \qquad \dim W^*=4.
\]

Indeed, a linear dependence on a proper subset would perturb the positive
coefficient vector in both signs until one active coefficient first became
zero, leaving a smaller nonnegative Gordan support.

It has size at most five.  Sizes one and two are impossible for a uniform
parent: every derived normal is nonzero, and parallel normals would put at
least four parent columns in a three-space.

For colored supports `P,R` and an ordered elementary column shear `e -> f`,
put

\[
 m(e,f)=\#\{I\in P:e\in I,\ f\notin I\}
       +\#\{I\in R:e\in I,\ f\notin I\}.              \tag{1}
\]

A triple belonging to both supports is counted once in each color.  Every
triple contributes to exactly 15 of the 56 ordered pairs, so

\[
                    \sum_{e\ne f}m(e,f)=15(|P|+|R|). \tag{2}
\]

If `m(e,f)<=1`, the transport-sign set has at most one member and the shear
is automatically sign-compatible.  The simultaneous moving-witness lemma in
`DIAG2_MOVING_WITNESS_SHEAR.md` then transports both nonnegative relations on
one oriented half-ray until the first parent bracket vanishes, or until two
columns become parallel at projective infinity.

Write `E_T(sigma)` for the set of oriented elementary shears compatible with
at least one positive `sigma`-witness at `T`.

In particular, if `|P|+|R|<=7`, then the right side of (2) is at most 105,
whereas `m(e,f)>=2` for all ordered pairs would sum to at least 112.  Thus
every such pair has a compatible oriented shear.  Call a pair **source-hard**
when `m(e,f)>=2` for all 56 ordered pairs.

## 2. The all-strata small-circuit classification

The classification needed here is pointwise, including simultaneous and
nontransverse residual walls.  The all-strata rank and padding theorem in
`NINTH_DIAGONAL_SAFE_GRAPH.md` gives the following alternatives.

* A nonstructural minimal four-circuit is the exact circuit of one of the
  nine ordinary residual types
  `37,38,41,42,44,48,49,50,51`.  A localization four-set has a dependent
  three-subset and hence cannot itself be minimal.
* A nonstructural minimal three-circuit can be padded by a fourth triple to a
  nonstructural residual four-set.  The fixed-unit identities of every
  ordinary type have four nonzero coefficients, so they cannot contain the
  zero-padded three-circuit.  The occurrence is therefore one of the four
  decorated localization types `36,39,46,47`.

Extra residual factors vanishing at the same point do not change these
necessary alternatives.  Nor do they invalidate any shared-parent
Grassmann--Pluecker relation, shear-conflict predicate, or fixed-unit circuit
identity used by the finite filters below.

There are two structural persistent cases: three triples sharing a label
pair, and four triples sharing one label.  They are deliberately excluded
from the support-drop theorem and retained in the clopen argument in
Section 6.

## 3. Minimal five-circuits and the `generic5` filter

The support verifier's historical predicate name `generic5` is not an
assumption that the point is generic.  It excludes exactly these two support
patterns:

1. one label occurs in at least four of the five triples; or
2. one label-pair occurs in at least three of the five triples.

Both exclusions are forced by circuit minimality.  In the first case the
four corresponding normals annihilate the same nonzero parent column and lie
in its three-dimensional annihilator.  In the second case the three normals
annihilate the two-plane spanned by the parent pair and lie in its
two-dimensional annihilator.  Either is a dependent proper subset.

Consequently every support-minimal five-circuit passes `generic5`, even at a
lower residual stratum.  The exact support verifier exhausts all
`C(56,5)=3,819,816` supports and records

```text
minimal-five eligible       2,021,992
structurally nonminimal     1,797,824
```

Thus the five-support census below loses no actual minimal circuit.

## 4. Exact source-hard residue

The exact unsigned verifier
`verify_diag2_generic_birth_support_filter.py` and signed verifier
`verify_diag2_generic_birth_pattern_reduction.py` prove:

| active circuit | partner | exact source-hard residue |
|---|---:|---|
| localization size 3 | size 5 | 32 labeled supports / 8 decorated orbits; all shared-parent signed formulas UNSAT |
| ordinary size 4 | size 4 | 3 labeled supports / 2 wall-stabilizer orbits out of all 367,290 partners; all signed formulas UNSAT |
| ordinary size 4 | size 5 | 53 wall-stabilizer orbits reduce to 23 and then 10 necessary signed supports |

Each signed formula contains the shared rank-four parent
Grassmann--Pluecker axioms, both extension-signature variables, and the
conflict predicate for every one of the 56 ordered shears.  The localization
and ordinary `4+4` UNSAT conclusions therefore remain valid at multiwalls.

The three ordinary `4+4` formulas each have 34,122 normalized clauses:

| type and partner | formula SHA-256 |
|---|---|
| `49:167/348/568/278` | `56db6f1ed30a94e52780001bba0468f9858aed11873f53940e926ad2b787e60f` |
| `49:167/258/368/478` | `abab41549d57ce75f776048e6d3ede86ca21c4e9c9454d231c65c3dc80958ec5` |
| `51:356/347/258/178` | `11d371417e70b30250110b3b249ec6c68ebf24049a20c63bcf2755b734a69a8b` |

Most importantly for witness exchange, every one of the ten signed-possible
ordinary `4+5` survivors has

\[
                              P\cap R=\varnothing.    \tag{3}
\]

The verifier asserts (3) support by support.  Its complete version-three
semantic digest is

```text
4546a2e7ba03c1c9dd63abbe65195fc348accf9bf91ccaa773072f1fcae9df38
```

These are necessary-condition eliminations.  No realizability of a SAT
survivor is asserted or needed.

## 5. Exchange-saturated support-drop theorem

> **Pointwise theorem.**  Let `T` be a uniform parent chart and let `rho,eta`
> be valid extension signatures which are both bad at `T`.  If one signature,
> say `rho`, has a nonstructural positive minimal circuit `P` of size three or
> four, then
>
> \[
>                         E_T(\rho)\cap E_T(\eta)\ne\varnothing. \tag{4}
> \]

Choose any positive minimal `eta`-circuit `R`.

If `|P|=3`, Section 2 puts `P` in a decorated localization occurrence.
Partners of size at most four are handled by (2); a source-hard size-five
partner would satisfy one of the eight signed localization formulas, all of
which are UNSAT.  Hence a compatible pair exists.

Now let `|P|=4`.  Section 2 makes `P` an ordinary residual circuit.  Partners
of size at most three are handled by (2), and source-hard size-four partners
are excluded by the complete `4+4` formulas.  It remains to consider a
source-hard minimal five-circuit `R`.  Sections 3--4 put its selected signed
pair among the ten survivors, so (3) gives `P intersection R=empty`.

Write `z_q=eta_q a_q(T)` for every triple `q`; in particular, the five
vectors `z_r`, `r in R`, are the vectors in the positive `eta`-circuit.
Minimality gives rank four, and their strictly positive relation implies

\[
                         \operatorname{cone}\{z_r:r\in R\}=W^*. \tag{5}
\]

Indeed, express an arbitrary vector as a linear combination of the `z_r`
and add a sufficiently large multiple of the positive zero relation to make
all coefficients nonnegative.

Choose `p in P`.  By (5), `-z_p` is a nonnegative combination of the vectors
in `R`.  Hence the pointed polyhedral cone

\[
 K=\left\{\lambda\ge0:
       \sum_{q\in R\cup\{p\}}\lambda_qz_q=0\right\}
\]

contains a vector whose `p`-coordinate is positive.  Decompose that vector
into extreme rays of `K`; at least one extreme ray still has positive
`p`-coordinate.  The support of an extreme ray of a nonnegative kernel cone
is an inclusion-minimal positive linear dependence: a kernel vector on a
proper subset would perturb the ray in both signs while remaining
nonnegative, contradicting extremality.  Rank four bounds its support by
five, so it gives a positive minimal `eta`-circuit

\[
                   R'\subseteq R\cup\{p\},\qquad
                   p\in R',\qquad |R'|\le5.           \tag{6}
\]

Because `P intersection R=empty`, equation (6) gives

\[
                               P\cap R'=\{p\}.         \tag{7}
\]

Suppose (4) were false.  Then every selected witness pair, including
`(P,R')`, would be source-hard and signed-incompatible.  If `|R'|<=3`, this
contradicts (2).  If `|R'|=4`, the exhaustive ordinary four-partner residue
is wall-disjoint (and in fact signed UNSAT).  If `|R'|=5`, Sections 3--4 put
the pair among the ten wall-disjoint survivors.  Each alternative contradicts
(7).  This proves (4).

The exchange is essential.  The exact type-50 and type-51 examples in
`DIAG2_GENERIC_BIRTH_PATTERN_REDUCTION.md` still disprove compatibility of
an arbitrary preselected `4+5` circuit pair; the theorem replaces the
five-circuit by `R'`.

## 6. Compact components cannot avoid support drop

Every `B_sigma` is closed in `X`.  Indeed, normalize its Gordan vector in the
compact simplex, take the closed incidence subset of
`X times the weight simplex`, and project along the compact factor.

Assume that `C` is a compact connected component of
`B_rho intersection B_eta`.  If some point of `C`, for either signature,
has a nonstructural minimal circuit of size three or four, the pointwise
theorem supplies a common oriented shear.  The moving-witness ray stays in
the simultaneous-bad locus until a nonuniform parent boundary.  Every finite
initial segment is connected and contains its starting point, hence the full
half-open ray lies in `C`.  If `C` were compact, its image in the Hausdorff
projective configuration compactification would be compact and closed, which
would force that image to contain the boundary limit, a contradiction.

Suppose instead that no such point exists.  At every point of `C`, each bad
signature has a positive minimal circuit of one of these persistent forms:

* a size-five circuit, whose nonzero four-by-four cofactors and positive
  kernel signs persist locally; or
* a structural minimal size-three or size-four circuit, whose exact
  dependence is structural while a nonzero rank minor and all kernel signs
  persist locally.

Thus `B_rho intersection B_eta` contains an `X`-neighborhood of every point
of `C`.  The open semialgebraic parent stratum `X` is locally path connected,
so a sufficiently small connected neighborhood lies in the same connected
component and `C` is open in `X`.  Components of the closed
simultaneous-bad locus are closed, hence `C` is clopen.

The parent space `X` is connected by the contractibility theorem recorded in
`PARENT_CONTRACTIBILITY_AUDIT.md`.  It is noncompact: an elementary column
shear, even without witnesses, stays in the parent sign cell until a first
bracket zero or reaches a parallel-column limit at infinity.  Therefore a
nonempty clopen `C` would equal the noncompact space `X`, contradicting the
assumed compactness of `C`.

Both alternatives are impossible.  Every component of every simultaneous-
bad pair is noncompact, proving the theorem.

## 7. Replay

Run the two finite support certificates with:

```console
python ai/omreal/verify_diag2_generic_birth_support_filter.py
python ai/omreal/verify_diag2_generic_birth_pattern_reduction.py
```

The first command exhausts the minimal-five eligibility filter, the
localization and ordinary source-hard supports, and all ordinary four-
partners.  The second command checks the exact signed formulas, the three
`4+4` UNSAT digests, the `53 -> 23 -> 10` reduction, and disjointness of all
ten final supports.  `run_all.py --fast` supplies the surrounding parent,
wall-classification, moving-witness, duality, and status-ledger regressions.
