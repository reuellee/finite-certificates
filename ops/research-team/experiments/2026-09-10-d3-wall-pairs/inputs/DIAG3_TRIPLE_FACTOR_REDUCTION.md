# Third diagonal: conditional reduction of triple badness to three factors

## Outcome

There is a proof-safe support-drop reduction for the intersection of three
bad loci.  It is conditional only at one explicit geometric endpoint.

Let `X` be one normalized realization cell of a realizable uniform
`UOM(4,8)` parent and let

\[
                         B_1,B_2,B_3\subset X
\]

be the Gordan bad loci of three valid extension signatures.  Suppose that,
for every set `F` of at most three **distinct primitive residual factors**,
every connected component of

\[
                  Z_F=X\cap\bigcap_{f\in F}\{q_f=0\}              \tag{1}
\]

is noncompact.  Then every connected component of

\[
                              B_1\cap B_2\cap B_3                 \tag{2}
\]

is noncompact.  In particular,

\[
                    H_c^0(B_1\cap B_2\cap B_3;\mathbb Z)=0.       \tag{3}
\]

The hypotheses in (1) are already proved for `|F|=0,1,2`.  The exact
relative-label endpoint for `|F|=3` has

\[
                             \boxed{79,102,449}
\]

unordered `S_8`-orbits.  No theorem in the repository proves noncompactness
for all of them.  Consequently this note is a conditional reduction, not a
proof of the third diagonal.

For one fixed signature triple the endpoint can be sharpened.  Only factor
triples which can be matched to the three signatures through aligned labeled
wall occurrences can be produced by the induction below.  There is no
further allowed-side or sector inequality on the common zero set.  Across
all possible extension signatures this sharpening gives no occurrence-level
Grassmann--Pluecker exclusion: every nonempty residual occurrence wall is
locally aligned with an actual realizable extension tope.  The precise
statement and proof are in Section 1.

The same theorem holds, with the same proof, after replacing any `B_i` by a
fixed closed circuit piece `C_(rho_i,Q_i)`.  At each point choose a
support-minimal dependence **inside** `Q_i`.  A persistent circuit remains
inside the same closed piece, while a residual wall circuit has support in
`Q_i` and makes that entire factor wall lie in the piece.  Consequently the
three-factor endpoint would kill the circuit-cover `E_1^(2,0)` column
termwise, not merely the triple term for the coarser cover by full bad loci.

## 1. The all-strata persistence dichotomy

At a bad point choose a support-minimal nonnegative Gordan dependence.  For
a fixed circuit piece, choose it among dependences supported in the piece's
index set.  Its support has size three, four, or five.

* A strict size-five circuit is locally persistent: rank four, its five
  nonzero cofactors, and their common positive orientation persist on a
  neighborhood.
* A structural minimal size-three or size-four circuit is locally
  persistent for the same reason, with its structural dependence retained
  and a nonzero rank minor and all kernel signs retained locally.
* A nonstructural minimal size-four circuit is the wall circuit of one of
  the nine ordinary residual types.  A nonstructural minimal size-three
  circuit pads to one of the four localization residual types.

The last classification is pointwise and remains valid on simultaneous and
nontransverse residual strata; see
`DIAG2_EXCHANGE_SATURATED_SUPPORT_DROP.md`, Sections 2, 3, and 6.  More is
true in the residual case.  The fixed-unit wall identities express every
coefficient of the ordinary four-circuit, or of the distinguished
localization three-circuit, as a nonzero product of parent brackets, up to a
common scale.  Its signs are therefore constant throughout the parent cell.
If a signature aligns with that labeled wall circuit at one point of the
primitive factor wall `H_f={q_f=0}`, then

\[
                                H_f\subseteq B_i.                  \tag{4}
\]

This persistence survives intersections with other residual walls and does
not require the displayed dependence to remain support-minimal.  See
`RESIDUAL_STRATUM_NONCOMPACTNESS.md`, Section 3.

If the starting locus is a closed piece `C_(rho_i,Q_i)`, the selected wall
circuit is a subset of `Q_i`; zero-padding its positive relation therefore
strengthens (4) to `H_f subset C_(rho_i,Q_i)`.

After localization, several labeled residual occurrences can define the
same primitive factor.  Encountering another such occurrence does not add a
new equation to (1); equation (4) instead makes its signature automatic on
the current factor stratum.

### Active-factor sharpening and its exact limit

For a valid extension signature `sigma`, let

\[
 A_\sigma=\{f:\text{some labeled occurrence of }f
                 \text{ is circuit-aligned with }\sigma\}.       \tag{4a}
\]

Run the nested induction of Section 2 while recording which unassigned
signature introduced each new factor.  If it reaches three distinct factors,
then, after ordering the signatures, they satisfy

\[
                         f_i\in A_{\sigma_i},\qquad i=1,2,3.      \tag{4b}
\]

Indeed every new factor is introduced by an aligned circuit of an unassigned
signature.  If one factor certifies two new signatures, at most two factors
are needed and the already-proved pair endpoint applies.  Thus in the
three-factor case the three introduction steps give the matching (4b).
This is the minimal proof-safe sharpening for a prescribed signature triple.
For a fixed circuit piece `C_(sigma,Q)`, replace `A_sigma` by the subset whose
aligned occurrence circuit is contained in `Q`; the same introduction-step
argument applies termwise.

It is not a restriction to an allowed **sector**.  Once `f in A_sigma`, the
fixed-unit identities give `H_f subset B_sigma`, including all intersections
with the other factor walls.  At the endpoint every `q_f` equals zero, so an
inequality `epsilon_(sigma,f) q_f>0` is false rather than an extra condition.
The active-sector theorem describes the feasible complement of active walls;
it does not cut down their zero strata.

Nor does occurrence-level extension realizability remove a nonempty wall.
This follows from a local converse to the wall-side theorem.

> **Local aligned-tope lemma.** Let `Y in X intersection H_f`, and fix any
> labeled occurrence `E` of `f`.  Either of the two antipodal signings of the
> unique wall circuit supported on `E` is the restriction of a realizable
> uniform single-element extension signature of the parent chirotope of `X`.

For an ordinary occurrence, the exact fixed-unit identities make all four
circuit cofactors nonzero at every point of the wall.  Thus the four selected
normals have rank exactly three at `Y` and a unique dependence.  Because
`D_E=(nonzero unit) q_f` is a nonzero polynomial and `X` is open, there are
arbitrarily small displacements `Y(t) in X` with `D_E(Y(t))` nonzero; the four
normals then form a basis.  Reorient them by the signs of their wall
dependence.  The inverse image of the positive orthant under this basis is a
nonempty open cone in the extension-column space.  A finite union of the
other 52 derived hyperplanes cannot cover that cone, so a point outside their
union gives a complete uniform extension tope with the required restriction.

For a localization occurrence the exact localization coefficients make the
distinguished three wall normals an exact rank-two circuit at `Y`.  At an
arbitrarily close point off the same occurrence wall, its four-normal
determinant is nonzero, so the distinguished three normals are independent.
Their prescribed strict sign cone is again a nonempty open subset of the
four-dimensional extension-column space, and the same hyperplane-avoidance
argument completes it to a uniform tope.  Replacing the column by its negative
supplies the antipodal choice.  In both cases the nearby parent stays in `X`,
so the resulting sign vector is an actual realizable extension of the same
parent chirotope and automatically satisfies every extension
Grassmann--Pluecker axiom.  QED.

At a simultaneous factor intersection this construction may be performed
independently for the three factors: the three missing extension columns are
independent and may use different nearby parent realizations in `X` to prove
individual validity.  Consequently the fixed circuit signs and the extension
Grassmann--Pluecker axioms do not impose a mixed sign identity on the three
factor equations and cannot, by themselves, forbid a compact component of
their common zero set.  They can still prune factors for one **prescribed**
signature triple through (4b).  Counting that smaller family requires a
global active-factor atlas, including the distinction between dominance-
reduced extension regions; it is not an occurrence-support or local-GP
calculation.

## 2. Nested compact-component induction

Assume for contradiction that `C` is a compact connected component of (2).
The proof maintains the following data:

1. a set `F` of distinct primitive factors;
2. a set `A` of signatures already certified by those factors, meaning
   `Z_F subset B_i` for every `i in A`; and
3. a compact connected component

   \[
        C_F\text{ of }Z_F\cap\bigcap_{i\notin A}B_i               \tag{5}
   \]

   contained in `C`.

Initially `F=A=empty` and `C_F=C`.  Suppose the data have been constructed.
At a point of `C_F`, apply the dichotomy of Section 1 to every unassigned
signature.

If a nonstructural small circuit uses a factor already in `F`, equation (4)
certifies that signature on all of `Z_F`; add it to `A` without changing
`F`.  If it uses a new factor `h`, put

\[
 F'=F\cup\{h\},\qquad A'=A\cup\{i\},                               \tag{6}
\]

and take the connected component through the chosen point of

\[
                  Z_{F'}\cap\bigcap_{j\notin A'}B_j.              \tag{7}
\]

Every assigned signature is bad on `Z_(F')` by (4), so (7) is a connected
subset of the original triple-bad locus.  It meets `C`, hence it lies in the
component `C`.  It is a connected component of a closed semialgebraic set,
so it is closed; as a closed subset of compact `C`, it is compact.  Thus
(7) supplies the next `C_(F')`.

It remains to show that the construction cannot stop early.  Suppose no
unassigned signature has a new residual factor anywhere on `C_F`.  Every
such badness condition is then either automatic on `Z_F`, by an already
imposed factor and (4), or locally persistent.  Consequently (5) is open in
the connected component `W_F` of `Z_F` which contains it.  It is also closed
in `W_F`: bad loci are closed, semialgebraic connected components are
closed, and `C_F` is compact.  Hence `C_F` is a nonempty clopen subset of
connected `W_F`, so

\[
                                  C_F=W_F.                         \tag{8}
\]

The factor-stratum hypothesis says `W_F` is noncompact, contradicting the
compactness of `C_F`.

Therefore either another signature is certified by an existing factor or a
new factor is added.  Every new factor certifies at least one previously
unassigned signature, so at most three distinct factors are added.  When all
three signatures have been certified, (5) is a compact connected component
of `Z_F` itself, again contradicting the hypothesis.  This proves the
conditional theorem.

The topological inputs used above are proof-safe for semialgebraic sets:
they are locally connected and have finitely many connected components, so
their components are open and closed.  The `F=empty` base also uses the
recorded connectedness and noncompactness of the parent realization cell;
the external contractibility trust boundary is documented separately in
`PARENT_CONTRACTIBILITY_AUDIT.md`.

## 3. What is already proved for zero, one, and two factors

The nested induction does not ask for a common circuit or common shear.
It asks only for component noncompactness of the ambient factor strata.

* `|F|=0`: the normalized parent realization cell is connected and
  noncompact under the parent-space theorem used by the current ledger.
* `|F|=1`: every component of every labeled residual wall is noncompact.
  Each canonical residual equation is affine in a pivot with a nowhere-zero
  parent-bracket-unit slope, and arbitrary labels are handled by projective
  reframing.  See `RESIDUAL_STRATUM_NONCOMPACTNESS.md`.
* `|F|=2`: all `9,476` unordered relative-label orbits of distinct primitive
  factor pairs have no compact component.  The exact classification is
  `9,226` bracket-product Jacobian-minor certificates, `124` common affine
  translations, `4` weighted-torus escapes, and `122` iterated affine-fiber
  graphs.  See `DIAG2_PIVOT_LABELED_PAIR_THEOREM.md`,
  `DIAG2_PIVOT_ALL_PAIR_FIBERS.md`, and
  `verify_diag2_pivot_all_pair_fibers.py`.

Repeated labeled factors reduce to a smaller value of `|F|` and are already
covered by this list.

## 4. Exact size of the missing three-factor endpoint

The global factor certificate localizes `84,840` labeled residual determinant
occurrences to `26,740` primitive factors in six full `S_8`-orbits.  For a
permutation `g`, let `f(g)` be the number of primitive factors it fixes.  A
three-element subset fixed by `g` consists of one of:

1. three fixed factors;
2. one fixed factor and one two-cycle; or
3. one three-cycle.

The exact fixed-subset count is therefore

\[
 {f(g)\choose3}
 +f(g)\frac{f(g^2)-f(g)}2
 +\frac{f(g^3)-f(g)}3.                                           \tag{9}
\]

Summing (9) over the 22 conjugacy classes of `S_8` and dividing by `40,320`
gives

\[
             \boxed{79,102,449}
\]

unordered orbits of triples of distinct factors.  The labeled count is

\[
                  {26,740\choose3}=3,186,282,165,780.             \tag{10}
\]

The exact checker `verify_diag3_triple_factor_orbits.py` reconstructs factor
equality and the induced action from the pinned global certificate.  As
canaries it independently reproduces the six one-factor orbits and the
`9,476` pair orbits before accepting (9).  Its pinned semantic digest is

```text
9dc473537e87e509031d4843d960f5ea4bfefb8508262cd1ebb5d44e1a49913d
```

This is a finite endpoint, not an assertion that all `79,102,449` strata are
nonempty or noncompact.

## 5. Existing triple certificates do not close the endpoint

For the twelve distinct canonical representative residual polynomials, the
repository classifies only the `220` representative triples:

| canonical class | triples | compactness consequence |
|---|---:|---|
| fixed bracket-product `3 by 3` minor | 170 | every component noncompact |
| sequential rank-three certificate `(36,38,42)` | 1 | rank only; no fixed-minor compactness conclusion |
| exact uniform rank-two witness | 4 | fixed-minor route is impossible |
| open | 45 | none |

The replay is `DIAG2_PIVOT_REPRESENTATIVE_TRIPLES_VERIFY.py`.  Its own scope
is representative-normalization only; it does not classify arbitrary
relative labels.  The four rank-two examples also falsify a blanket theorem
that three residual gradients always have rank three.

The complete pair classification does not imply the required triple
statement.  An exact elementary model already separates the two claims.  In
`X=R^9`, set

\[
 q_1=x_1,\qquad q_2=x_2,\qquad
 q_3=\sum_{j=3}^9x_j^2-1-x_1x_2.                                  \tag{11}
\]

Then

\[
 \begin{aligned}
  Z(q_1,q_2)&\cong\mathbb R^7,\\
  Z(q_1,q_3)&\cong S^6\times\mathbb R,\\
  Z(q_2,q_3)&\cong S^6\times\mathbb R,
 \end{aligned}                                                   \tag{12}
\]

so every pair component is noncompact, while

\[
                         Z(q_1,q_2,q_3)\cong S^6                  \tag{13}
\]

is compact.  In particular, an affine graph or proper escape for each pair
can be cut to a compact set by the third equation.  Existing pair graph,
translation, torus, and affine-fiber data contain no compatibility condition
with an arbitrary third factor.

## 6. Remaining target and scope

The conditional reduction replaces a global compact triple-bad component,
or a compact component of three fixed closed circuit pieces, by a compact
component of an intersection of at most three primitive residual factors.
It removes witness-choice and support-gluing ambiguity from that specific
`H_c^0` question.  What remains is still a new theorem:

> Every connected component of every common zero set of three distinct
> relative-label primitive residual factors in a normalized uniform parent
> cell is noncompact.

A direct orbit-by-orbit treatment starts from `79,102,449` cases.  A useful
new certificate would need a stronger structural reduction, or a highly
compressed relative-label classifier combining fixed `3 by 3` minors with
escape/fiber certificates for its rank-drop residue.  The existing
`9,476`-pair artifact is not such a classifier.

Accordingly:

\[
              \boxed{\text{the third diagonal is not proved by this note}.}
\]

## 7. Replay

Run

```console
PYTHONDONTWRITEBYTECODE=1 python \
  ai/omreal/verify_diag3_triple_factor_orbits.py
```

Expected output ends with

```text
PASS residual-factor subset orbits: factors=6 pairs=9476 triples=79102449
PASS labeled distinct triples: 3186282165780
SEMANTIC 9dc473537e87e509031d4843d960f5ea4bfefb8508262cd1ebb5d44e1a49913d
CAVEAT finite endpoint only; triple-factor component noncompactness is not proved
```
