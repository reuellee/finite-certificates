# Diagonal two: exact witness-exchange audit

## Outcome

The moving-witness shear lemma is sound, but its compatibility hypothesis
cannot be required of an arbitrary preselected pair of witnesses, even for
valid realizable extensions with proper incomparable feasibility regions.

At the catalog parent-16 base chart, the exact signatures

```text
rho = 50603577668866936
eta = 36319034736575472
```

have positive support-minimal five-circuits

```text
Q = 236/246/347/138/258
R = 156/127/567/458/478
```

for which all 56 ordered elementary shears fail the sign-compatibility test.
Both full signings satisfy every rank-four Grassmann--Pluecker relation.  Two
stored integer `4 by 9` incidences independently realize the two extensions;
at each child parent the other signature has an exact positive Gordan
circuit.  Hence both regions are nonempty and proper, and each has a point
outside the other.  This is a genuine 9DVL pair, not the invalid-signing
canary from `DIAG2_MOVING_WITNESS_SHEAR.md`.

One circuit exchange repairs the obstruction.  Replace `567` in `R` by
`167`:

```text
R' = 156/127/167/458/478.
```

Then the unique compatible ordered shear is `5 -> 8` with negative
direction.  The moving witnesses persist until the first parent boundary

\[
                  u=\frac{533}{1228},\qquad [4567]=0.
\]

Thus the counterexample falsifies **arbitrary-witness compatibility**, not
the existence of compatible witnesses after exchange.  Diagonal two remains
open.

## 1. Exact weights and realizability

At the base chart the cofactor weights, in the displayed support orders, are

\[
\begin{aligned}
 Q:;&(6154715944,12264961032,15996634000,
       26943855000,52114950616),\\
 R:;&(6364432608,4753062630,3883263297,
       1512222528,2420252970),\\
 R':;&(5353124400,11321819622,3883263297,
        1271930400,6687738720).
\end{aligned}
\]

Every entry is strictly positive, every proper four-subset of `Q`, `R`, and
`R'` is independent, and the signed combinations vanish exactly.  The fast
verifier also checks:

1. all parent brackets are the signs of catalog parent 16;
2. both signatures obey every GP sign relation;
3. the two integer child incidences realize `rho` and `eta` exactly;
4. reciprocal positive circuits exclude `eta` at the `rho` child and `rho`
   at the `eta` child; and
5. the exchanged shear reaches only `[4567]=0` at its first endpoint.

The reciprocal exclusions prove global properness and incomparability from
exact witness charts; no point-sample coverage assumption is used.

## 2. Complete minimal-circuit census at the base

An independent exact enumeration finds every support-minimal positive Gordan
circuit at the base chart:

| signature | positive five-circuits | positive four-circuits | total |
|---|---:|---:|---:|
| `rho` | 622 | 0 | 622 |
| `eta` | 1,022 | 18 | 1,040 |

There are therefore `622 * 1040 = 646,880` circuit pairs.  Testing every
pair against all 56 ordered shears gives:

- exactly one pair with zero compatible shears: `(Q,R)`;
- exactly five pairs with one compatible shear; and
- at least two compatible shears for every remaining pair.

All five one-shear pairs are obtained from `R` by one circuit exchange.  The
displayed `R'` is one of them.  This makes the obstruction both real and
exceptionally rigid, while showing that the witness polytope contains ample
repairs at this chart.

## 3. Escape-direction set reformulation

For a bad signature `rho` at a parent chart `T`, let
`C_T(rho)` be its support-minimal positive Gordan circuits.  There are 112
oriented elementary shear directions

\[
             d=(e,f,a),\qquad e\ne f,\quad a\in\{+1,-1\}.
\]

Define

\[
 E_T(\rho)=\{d:\text{some }Q\in C_T(\rho)
                    \text{ is sign-compatible with }d\}.       \tag{1}
\]

A simultaneous moving-witness escape exists for a pair exactly when

\[
                         E_T(\rho)\cap E_T(\eta)\ne\varnothing. \tag{2}
\]

Indeed, a common direction and two witnessing circuits give the shear lemma.
Conversely, if any nonminimal witness is compatible, its positive-kernel
face contains a support-minimal circuit, and compatibility is inherited by
subsupports.

Membership in (1) does not require enumerating circuit vertices.  For fixed
`d=(e,f,a)`, delete every signed derived normal indexed by a source triple
`I` with

\[
                  \alpha_\rho(I;e,f)\ne a.
\]

Then `d` lies in `E_T(rho)` precisely when the remaining signed normals have
a nonzero nonnegative dependence.  This is one restricted Gordan-feasibility
test.  The universal local target is therefore a finite 112-bit set-system
statement rather than compatibility of arbitrary supports.

Strict Gordan duality sharpens this further: the restricted system has such a
dependence precisely when no complete tope of the 56-row derived arrangement
agrees with `rho` on all retained rows.  Thus one exact complete-tope table
computes every escape set at a chart by restriction hashing.  The exhaustive
parent-16 and hard row-2599 audits are in
`DIAG2_ESCAPE_SET_TOPE_REDUCTION.md` and
`verify_diag2_escape_set_topes.py`.

For the exact falsifier,

\[
 |E_T(\rho)|=89,qquad |E_T(\eta)|=99,qquad
 |E_T(\rho)\cap E_T(\eta)|=76,qquad
 E_T(\rho)\cup E_T(\eta)=\{1,\ldots,112\}.             \tag{3}
\]

So witness exchange removes the obstruction very strongly at this point.

## 4. Remaining theorem

The sharpened moving-witness question is:

> For every realizable uniform parent chart `T` and every relevant proper
> incomparable pair of extension signatures bad at `T`, must their two
> escape-direction sets intersect?

A positive answer would finish diagonal two.  Indeed, choose any point of a
putative compact simultaneous-bad component.  A common direction and two
witnesses give the proper moving-witness ray of
`DIAG2_MOVING_WITNESS_SHEAR.md`; every finite initial segment remains in the
same connected component, while the ray approaches a parent boundary or
projective infinity.  This contradicts compactness.  No coherent choice of
directions at different points is required.  Equation (2) is not promoted
here only because its universal validity is still open.

The set formulation suggests two exact attacks: an oriented-matroid theorem
forcing pairwise intersection of the restricted Gordan systems, or a finite
search for a valid chart/signature pair with disjoint 112-bit escape sets.
The latter would be a stronger falsifier than `(Q,R)`, because it would
survive every circuit exchange.

## 5. Exact verification

Run:

```console
python ai/omreal/verify_diag2_witness_exchange_falsifier.py
python ai/omreal/verify_diag2_witness_exchange_census.py
```

The first verifier checks the exact realizability, reciprocal exclusions,
weights, incompatibility, exchange, and boundary endpoint.  The second
enumerates all minimal circuits and all `646,880` circuit pairs, and replays
the 112-direction census (3).  Both use integer/rational arithmetic; the
census uses NumPy only for packed 56-bit comparisons.
