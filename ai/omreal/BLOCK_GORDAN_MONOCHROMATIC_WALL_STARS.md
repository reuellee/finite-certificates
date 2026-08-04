# Monochromatic residual-wall stars

## Outcome

Monochromatic wall stars are unavoidable in the actual third-compound
geometry.  Every one of the 13 residual orbit types has an exact uniform
parent wall and a proper extension signature with the following behavior:

1. the signature is strictly feasible on one side;
2. its signed wall normals contain the positive wall circuit;
3. every certified auxiliary circuit is positive on the bad side; and
4. no certified or non-unit one-auxiliary circuit is positive on the feasible
   side.

The fourth statement is also forced abstractly by Gordan's alternative:
strict feasibility excludes every nonnegative dependence, regardless of its
support.  Therefore a universal proof cannot repair a genuinely lost block
by looking for an unrelated persistent circuit in that same block.

At the exact row-2599 transverse node, the strongest two-block support test
is favorable: all pairs among `1,553` possible wall-circuit-plus-auxiliary
supports have either a degree-at-most-two label or a common-apex shear.  This
includes all non-unit auxiliaries and is stronger than checking only the
realized positive pairs.

The corresponding triple statement fails.  Three actual proper signatures
have strict positive unit circuits whose union is pencil-rigid, with label
degrees

\[
                             (4,4,6,4,5,5,3,5).                   \tag{1}
\]

Thus neither persistent-circuit search nor the existing pencil/common-apex
lemmas remove the triple `H_c^0` term.  A later global path could still reach
a different flexible witness or the parent boundary; this audit proves that
such a path is not forced by the local wall star.

No diagonal is promoted.  The exact verifier is
`BLOCK_GORDAN_MONOCHROMATIC_WALL_STARS.py`.

## 1. Exact color criterion

Let `P={p_1,...,p_r}` be the positive wall circuit, with `r=4` for an ordinary
wall and `r=3` for a localization wall.  For a certified auxiliary `u`, the
fixed-sign determinant identity is

\[
                         \sum_{i=1}^r A_i(u)a_{p_i}+D_Ea_u=0.     \tag{2}
\]

Let `sigma` be a signature aligned with `P`, and put
`b_j=sigma_j a_j`.  Since

\[
             \sum_i A_i(u)\sigma_{p_i}b_{p_i}
                    +D_E\sigma_ub_u=0,                           \tag{3}
\]

the numbers `A_i(u)sigma_(p_i)` have a common nonzero sign.  Denote it by
`epsilon_u`.  After multiplying (3) by `epsilon_u`, all wall-circuit
coefficients are positive and the auxiliary coefficient has sign

\[
                         \operatorname{sign}(D_E)\,epsilon_u\sigma_u.
                                                                    \tag{4}
\]

Define the certified color

\[
                              c_\sigma(u)=\epsilon_u\sigma_u.     \tag{5}
\]

Then `P union {u}` is a strict positive circuit precisely on the side

\[
                              \operatorname{sign}(D_E)=c_\sigma(u).  \tag{6}
\]

Consequently:

> **Monochromatic criterion.**  The certified wall star is monochromatic if
> and only if `c_sigma(u)` is constant over all certified auxiliaries.

The exact auxiliary counts are:

| type | certified auxiliaries |
|---:|---:|
| 36 | 12 |
| 37 | 14 |
| 38 | 2 |
| 39 | 12 |
| 41 | 14 |
| 42 | 2 |
| 44 | 12 |
| 46 | 12 |
| 47 | 12 |
| 48 | 16 |
| 49 | 8 |
| 50 | 3 |
| 51 | 4 |

This criterion is a complete sign classification for the certified star.  It
does not assert that every abstract assignment of auxiliary colors is a tope.
The exact examples below show that the all-one-color assignment is realized
for every residual type.

## 2. Exact actual-OM examples for all 13 types

Use the standard normalized parent

\[
 Y(a,\ldots,i)=
 \begin{pmatrix}
 1&0&0&0&1&1&1&1\\
 0&1&0&0&1&a&d&g\\
 0&0&1&0&1&b&e&h\\
 0&0&0&1&1&c&f&i
 \end{pmatrix}.                                                   \tag{7}
\]

For each type, the verifier stores a rational point on its representative
residual wall and perturbs the certified pivot coordinate by
`+/-10^(-6)`.  All 70 parent brackets retain one strict sign on the closed
transverse segment.  A stored integer extension vector realizes the signature
on the negative side; the wall circuit and every bad-side auxiliary circuit
are checked by exact kernel arithmetic.

| type | pivot | wall value | certified | all positive auxiliaries on bad side |
|---:|---|---:|---:|---:|
| 36 | `a` | `29/2` | 12 | 18 |
| 37 | `a` | `-69` | 14 | 48 |
| 38 | `a` | `3643/58` | 2 | 48 |
| 39 | `a` | `-179` | 12 | 18 |
| 41 | `a` | `231/23` | 14 | 48 |
| 42 | `a` | `-1669/5` | 2 | 48 |
| 44 | `d` | `298/143` | 12 | 48 |
| 46 | `a` | `601/13` | 12 | 18 |
| 47 | `a` | `-6` | 12 | 18 |
| 48 | `a` | `-35` | 16 | 52 |
| 49 | `d` | `-14` | 8 | 51 |
| 50 | `d` | `223/21` | 3 | 52 |
| 51 | `f` | `-77/5` | 4 | 52 |

The last column exhausts every possible auxiliary normal, not only those
whose cofactors are bracket units.  The feasible-side count is zero for every
row.

These examples also rule out interpreting monochromaticity as an accidental
parent-boundary event: every wall point is uniform and lies in the interior
of one parent chirotope cell.  A bad component may reach a parent boundary
later, but no local circuit axiom forces that continuation.

## 3. Why a persistent circuit cannot be forced

If `sigma` is realized at `Y_+`, there is `p` with

\[
                              A_\sigma(Y_+)p>0.                   \tag{8}
\]

If a nonzero `w>=0` satisfied `A_sigma(Y_+)^Tw=0`, then

\[
                       0=p^TA_\sigma(Y_+)^Tw
                         =w^TA_\sigma(Y_+)p>0,                   \tag{9}
\]

a contradiction.  Thus there is no positive circuit of any support on the
feasible side.  Circuit elimination can reorganize witnesses on the bad
side, but it cannot create a persistent same-block witness across a genuine
feasibility boundary.

This is the precise failure of alternative `(i)` in the proposed local
trichotomy.  Transfer across such a wall must use another signature block, a
base-cell attachment, or a global escape of the bad component.

## 4. Exact row-2599 pair theorem

Before using the row-specific data, there is a universal same-wall result.
Two one-auxiliary supports based on one wall circuit have union

\[
                         P\cup\{u,v\}.                            \tag{10}
\]

For an ordinary wall this contains at most six derived triples; for a
localization wall it contains at most five.  Since every derived normal is
indexed by a parent triple, the total parent-label incidence in (10) is at
most `18`.  Eight labels all having degree at least three would require at
least `24` incidences.  Hence:

> **Universal same-wall pair theorem.**  For every residual wall type and
> every pair of auxiliary normals—including non-unit auxiliaries—the union
> of the two supports has a parent label of degree at most two.  The
> plane-pencil escape applies.

The exhaustive representative check tests `1,326=binom(52,2)` pairs for
each ordinary type and `1,378=binom(53,2)` for each localization type.  The
proof is the incidence count above and is invariant under every relabeling.
It is not special to certified auxiliaries.

This settles the local fixed-wall support question completely.  It does not
settle the pair Mayer--Vietoris column: two witnesses can be supported on
circuits unrelated to the same wall, can encounter different residual walls,
and their support-drop strata can glue during a global loop.

### 4.1 Stronger row-2599 cross-occurrence census

Take branch zero of the exact row-2599 `65+65` transverse node.  For each of
its 65 labeled residual occurrences, take the exact wall circuit `P` and form

\[
                              Q=P\cup\{u\}                        \tag{11}
\]

for every one of the 56 derived normals `u` not already in `P`.  After
deduplication there are

\[
                  1{,}553=1{,}500\text{ five-supports}
                              +53\text{ four-supports}.           \tag{12}
\]

For every unordered pair `Q,Q'`, the verifier checks their union of parent
triples.  At least one parent label either

1. occurs in at most two supporting triples, giving the plane-pencil escape;
   or
2. occurs in several triples having a common second parent label, giving the
   common-apex shear.

Thus no pair among the complete unsigned superset (12) is rigid under the
known escape lemmas.  In particular, every realized positive auxiliary pair
at this node is flexible.  This is stronger than the earlier certified-unit
census.

It remains a local theorem.  A pair component can move through other walls,
use circuits unrelated to this branch, and return globally; the pair
`H_c^1` term is not proved zero by one wall star.

## 5. Exact triple obstruction

In the bad cell `(-,+)` adjacent to the same branch, the following three
proper signatures and unit supports are strict positive circuits:

\[
\begin{array}{c|c}
68231279848521727&0/19/34/37/40\\
62614156573450111&0/18/47/48/53\\
40418078342512640&4/5/18/20/40
\end{array}                                                       \tag{13}
\]

The signature numbers are the exact 56-bit sign encodings used by the node
certificate.  Each has local feasibility mask `0011`, so it is feasible in
two adjacent cells and bad in the displayed opposite cell.  Hence every
signature is proper.

The union in (13) has degree vector (1).  Every degree is at least three, and
for no label do all incident triples share a second common label.  Therefore
the plane-pencil and common-apex escape lemmas do not apply.  This does not
prove that its full triple intersection has a compact component; it proves
that local support elimination cannot force alternative `(ii)`.

Pairwise global incomparability of the three feasibility regions is not
claimed.  Consequently (13) is an obstruction to the proposed local lemma,
not a 9DVL counterexample.

## 6. Consequence for diagonals 3--8

Together with `BLOCK_GORDAN_ALL_CODIM_COHERENCE.md`, this audit sharpens the
remaining task:

- higher wall-intersection coherence is automatic after facewise
  codimension-one maps exist;
- a block which becomes feasible cannot carry its own witness across the
  wall;
- every row-2599 two-block wall support has a known escape; but
- three-block rigid corners already occur exactly.

For `s=3`, the unresolved terms remain pair `H_c^1` globally and triple
`H_c^0`.  For `s=4,...,8`, the same monochromatic mass-transfer problem
appears in higher block-mass faces.  A successful proof now needs a
**multi-block transfer rule**: when one block dies, another bad block or a
proper base-boundary cell must receive its mass, and these transfers must
form an acyclic global matching.  Convex carriers then provide every higher
coherence automatically.

## 7. Verification

Run

```console
python ai/omreal/BLOCK_GORDAN_MONOCHROMATIC_WALL_STARS.py
```

The script uses exact integer/rational arithmetic to verify all parent
brackets, strict extension witnesses, wall circuits, certified and non-unit
auxiliary supports, the complete `1,553`-support pair census, and the rigid
triple in (13).
