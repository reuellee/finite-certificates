# Diagonal 9: what reducible parents do and do not reduce

## Outcome

Bokowski--Richter reducibility gives a genuine extension-feasibility
reduction, but not an induction from a parent to its deletion.

Let `e` be a parent element, `N=M\e`, and let `S` be a finite family of
extension signatures of `M`.  After retaining one private extension witness
for each signature, deletion of `e` has convex-or-empty insertion fibers.
Consequently

\[
             F_S(M)\simeq G_{e,S},
\]

where `G_(e,S)` is the locus in the **restricted witness-incidence space**
over `N` on which `e` can be reinserted simultaneously with all prescribed
extension signs.

For `S=empty`, reducibility says `G_(e,empty)=R(N)` and recovers the usual
homotopy equivalence `R(M) ~= R(N)`.  For nonempty `S`, reducibility gives no
reason for `G_(e,S)` to be the whole restricted incidence space.

An exact example proves the gap is real even when:

- `M` is the alternating, lexicographically reducible parent `A(4,8)`;
- `S={sigma}` consists of one realizable **proper** extension signature; and
- the deletion realization and restricted signature are fixed exactly.

Thus reducibility is not hereditary under one proper extension.  The natural
deletion map on witness incidence is not surjective, so the 2,546 reducible
catalog classes do not collapse diagonal 9 to seven-element extension loci.
The ninth diagonal remains open.

Replay the certificate with

```bash
python ai/omreal/DIAG9_GRAPH_REDUCIBILITY_NO_GO.py
```

All verdicts use integer determinants and positive integer Gordan circuits.

## 1. The safe simultaneous-insertion theorem

Work in fixed projective-frame slices.  Define the private-witness incidence

\[
\widehat F_S(M)=
\{(Y,(p_\sigma)_{\sigma\in S}):
Y\in\mathcal R(M),\ p_\sigma\text{ realizes }\sigma\text{ over }Y\}.
\]

The projection to `F_S(M)` has a product of nonempty open convex projective
residence chambers as each fiber.  It is a homotopy equivalence.  One direct
proof, avoiding a black-box fiber lemma, is given below.

Delete `e` but retain every `p_sigma`.  The target restricted incidence is

\[
\widehat F_{\bar S}(N)=
\{(Z,(p_\sigma)):
p_\sigma\text{ realizes }\bar\sigma=\sigma\setminus e
\text{ over }Z\}.
\]

Here `bar S` is an **indexed family with index set `S`**.  Two different full
signatures may have the same restriction after deleting `e`; their two
private witnesses must not be identified, because their joint signs involving
`e` may differ.

For `b=(Z,(p_sigma))` in this space, the possible reinsertions of `e` are

\[
K_{e,S}(b)=R_e^M(Z)\cap
\bigcap_{\sigma\in S}\ \bigcap_{J\in\binom{N}{2}}
\{x:\epsilon_{\sigma,J}
       \det(z_J,x,p_\sigma)>0\}.                 \tag{1}
\]

Here `R_e^M(Z)` is the ordinary residence chamber prescribed by `M`, and
`epsilon_(sigma,J)` is the prescribed sign of the basis containing `J,e,p`.
Every inequality in (1) is linear and strict in `x`.

There is a small but essential normalization point.  Choose the labeled
projective frame **entirely inside `N`**, and use the same frame slice before
and after deletion.  Let `I_0` be three of its four basis labels.  Uniformity
prescribes a nonzero sign for `det(z_(I_0),x)` at every admissible insertion.
The positive projective ray of `x` therefore has a unique representative
satisfying

\[
 \epsilon_{I_0}\det(z_{I_0},x)=1.                         \tag{1a}
\]

The frame columns in (1a) are fixed, so (1a) is one fixed affine hyperplane,
canonically an `R^3`, rather than a hyperplane varying with the base point.
Thus every nonempty fiber in (1) is an open convex subset of the same affine
three-space.  This common affine trivialization is what makes averaging local
sections below legitimate.

Put

\[
G_{e,S}=\{b\in\widehat F_{\bar S}(N):K_{e,S}(b)\ne\varnothing\}. \tag{2}
\]

Then deletion gives

\[
             \widehat F_S(M)\longrightarrow G_{e,S}              \tag{3}
\]

with nonempty open convex fibers.

### Why (3) is a homotopy equivalence

The preceding normalization identifies the total space in (3) with

\[
 E=\{(b,x):b\in G_{e,S},\ x\in K_{e,S}(b)\}
       \subset G_{e,S}\times\mathbb R^3.                \tag{3a}
\]

The finitely many defining coefficients are polynomial, hence continuous, in
`b`.  If `x_0` belongs to the fiber at `b_0`, every strict inequality remains
true for `b` in some neighborhood of `b_0`; hence the constant vector `x_0`
is a local section there.  This also proves that `G_(e,S)` is open in the
restricted incidence space.  It is therefore metrizable and paracompact.

Take a locally finite refinement of these section neighborhoods and a
subordinate partition of unity `(phi_alpha)`.  Attach to each refined open
set one of the constant sections `x_alpha` valid on the larger neighborhood.
For every `b`, local finiteness makes

\[
                 s(b)=\sum_\alpha\phi_\alpha(b)x_\alpha
\]

a finite convex combination of points of `K_(e,S)(b)`.  Convexity therefore
puts `s(b)` in that same *strict* fiber.  The map

\[
 H((b,x),t)=\bigl(b,(1-t)x+t s(b)\bigr)
\]

stays in (3a), is continuous, and fixes the graph of `s`.  It is a strong
deformation retraction of `E` onto that graph.  This proves (3), without any
properness assumption on the projection.

For the projection to `F_S(M)`, normalize every private `p_sigma` by the same
fixed frame triple `I_0`, using the sign prescribed by `sigma` in (1a).  Its
fiber is then a product of open convex subsets of a fixed
`(R^3)^S`.  Repeating the preceding argument proves
`widehat F_S(M) ~= F_S(M)`.  Hence

\[
\boxed{\quad F_S(M)\simeq G_{e,S}.\quad}                         \tag{4}
\]

Equation (4) preserves all homotopy and homology groups, not only path
components.  It is the strongest unconditional deletion reduction found in
this audit.

The obstruction is that (2), not `widehat F_(bar S)(N)`, is the base.  If the
private witnesses are forgotten too soon, the remaining joint `(e,p_sigma)`
conditions are bilinear and their fibers need not be convex.

## 2. A reducible alternating parent

Let

\[
y(t)=(1,t,t^2,t^3)
\]

and set

\[
N=(y(-3),y(-2),y(-1),y(0),y(1),y(2),y(3)),\qquad e_0=y(4).
\]

Every increasing four-bracket is positive, so `N=A(4,7)` and

\[
M=N\cup\{e_0\}=A(4,8).
\]

The endpoint extension signature is exactly the lexicographic extension

\[
e=[7^+,6^-,5^+,4^-].                                      \tag{5}
\]

Indeed, for a triple `I`, take the first listed label not in `I`; its signed
bracket has the positive endpoint sign.  The verifier checks all 35 triples.

Equation (5) also proves reducibility directly for every realization `Z` of
`A(4,7)`: for sufficiently small positive `delta`,

\[
z_7-\delta z_6+\delta^2z_5-\delta^3z_4
\]

has the sign prescribed by (5).  There are finitely many triples, so one
small `delta` works for all of them.  Thus every realization of the deletion
extends back to `M`.

## 3. A proper extension signature

Over the displayed moment configuration, take

\[
p_0=(-12,-12,6,18).
\]

It is uniform over `M` and defines a realizable signature `sigma`.  In the
verifier's lexicographic triple ordering its positive-sign bitset is

```text
sigma = 0xf07fe1fffc.
```

This region is proper.  A second realization of the same alternating parent
uses moment parameters

```text
-47, -39, -25, -23, -21, 14, 21, 27.
```

For the 56 signed normal rows prescribed by `sigma`, the following five rows
have the displayed positive integer dependence (row indices are zero-based):

| Row | Triple | Signed normal | Weight |
|---:|---|---|---:|
| 1 | `124` | `(-129512448,-11707392,-334848,-3072)` | 9,817,415,335 |
| 17 | `158` | `(2461088448,78406848,-3786432,-92352)` | 244,690,537 |
| 36 | `345` | `(193200,25328,1104,16)` | 3,688,327,422,780 |
| 44 | `368` | `(-249139800,17057508,421824,-26364)` | 202,820,352 |
| 55 | `678` | `(4334148,-676494,33852,-546)` | 1,665,426,048 |

The weighted vector sum is exactly zero.  Gordan's alternative therefore
excludes every strict witness `p` for `sigma` at this parent chart.  Since
`p_0` realizes `sigma` at the first chart, `F_sigma(M)` is nonempty and
proper.

## 4. Reducibility is lost after the proper extension

Delete `e` from `sigma` and call the restricted signature `tau`.  Its
35-sign bitset is

```text
tau = 0xe7fbffc.
```

Besides `p_0`, the exact column

\[
p_1=(-142669,-427153,430203,-419833)
\]

realizes the same `tau` over the same fixed `N`.  Thus `(N,p_1)` is a genuine
point of the restricted incidence space.

To reinsert `e`, impose the 35 parent signs of `M` and the 21 signs of bases
containing two labels of `N`, `e`, and `p`.  These are 56 strict linear
inequalities in the four homogeneous coordinates of `e`.  At `p_0`, `e_0`
satisfies all of them.  At `p_1`, the following five signed rows have a
strictly positive integer dependence; indices again are zero-based:

| Row | Constraint | Signed row | Weight |
|---:|---|---|---:|
| 13 | parent triple `157` | `(432,-432,-48,48)` | 86,484,824 |
| 18 | parent triple `237` | `(-120,-140,0,20)` | 552,946,456 |
| 33 | parent triple `467` | `(0,36,-30,6)` | 1,460,613,280 |
| 38 | joint pair `15` | `(20664384,-13823104,-6856896,15616)` | 1,403 |
| 46 | joint pair `34` | `(0,10370,7320,-3050)` | 7,867,472 |

Again the weighted sum is exactly `(0,0,0,0)`.  No vector `e` can have
positive dot product with every row.  Hence `(N,p_1)` has no compatible lift
to `sigma` although `(N,p_0)` does.

This proves all of the following.

1. `M` is reducible by `e`.
2. The proper realizable extension `sigma` is **not** reducible by `e`.
3. The deletion map from the realization incidence of `sigma` to that of
   `tau` is not surjective.
4. The simultaneous-insertion locus `G_(e,{sigma})` is a proper subset of the
   restricted incidence space even over one fixed deletion realization.

## 5. Consequences for the 2,546-parent strategy

The Bokowski--Richter count cannot be used as `2,546` automatic inductive
cases for 9DVL:

- direct reducibility controls only the empty-family insertion locus;
- a single proper extension can already destroy it, as above;
- for a nine-signature family, one common insertion `e` must satisfy all nine
  sets of witness-dependent halfspaces in (1); and
- when only `M*` is reducible, duality turns point extensions of `M` into
  liftings/coextensions of `M*`, not into the same rank-four point-extension
  problem on a smaller ground set.

The usable replacement is (4): compute the topology of the semialgebraic
nonempty-insertion locus `G_(e,S)` with all private witnesses retained.  This
may still simplify special signatures or selected reducible elements, and an
exact infeasibility certificate for (1) always has support at most five by
Gordan--Caratheodory.  But reducibility alone neither makes `G_(e,S)` full nor
proves its connectivity.

The example is a no-go for the induction, not a disconnected
ninth-diagonal feasibility locus and not a counterexample to 9DVL.
