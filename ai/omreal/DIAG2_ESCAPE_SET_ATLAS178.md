# Diagonal two: common-shear closure and the 178-chart quantitative audit

## Result

The moving-witness escape-set route is stronger than the earlier proof ledger
stated in one important respect:

> A universal common-shear theorem would finish diagonal two directly.  It
> does not leave a separate global direction-gluing problem.

The exact finite evidence for that theorem has also been expanded from 19
selected parent-2599 charts to **all 178 stored exact charts**.  At every
stored chart:

* the derived arrangement has 26,112 complete topes;
* 71,112 of the 97,224 abstract extensions are bad;
* every bad signature has at least 53 oriented elementary shear directions;
* every two distinct bad signatures have intersecting escape sets; and
* the minimum pair overlap over the complete bank is **six** directions.

Thus the audit reconstructs

\[
                 178\cdot71{,}112=12{,}657{,}936
\]

exact 112-bit escape masks without finding a disjoint pair.  Its aggregate
semantic digest is

```text
d255845e6b246865ed3c50a61c001ec8701d3b22fffd218087d955ac0854d111
```

This is a finite theorem about the stored source bank.  The 178 matrices are
not a certified chamber atlas, so the result does not promote the honest 9DVL
score beyond `1/9`.

## 1. One common direction closes a whole component

Fix a uniform parent realization cell `X`, two extension signatures
`rho,eta`, and a connected component

\[
                    C\subset B_\rho\cap B_\eta.
\]

For `T in C`, let `E_T(rho)` and `E_T(eta)` be the 112-direction escape sets
defined in `DIAG2_WITNESS_EXCHANGE_AUDIT.md`.  Suppose

\[
                    E_T(\rho)\cap E_T(\eta)\ne\varnothing.       \tag{1}
\]

Choose the common oriented shear `d=(e,f,a)` and support-minimal witnesses
certifying membership in the two escape sets.  The simultaneous
moving-witness shear lemma gives a path

\[
              \gamma:[0,u_*)\longrightarrow B_\rho\cap B_\eta, \tag{2}
\]

where either `u_*` is the first parent-bracket zero or `u_*=infinity` and the
moving parent columns become projectively parallel at infinity.  Every finite
initial segment of (2) is connected and contains `T`; hence it lies in `C`.
Taking the union over all finite initial segments gives

\[
                         \gamma([0,u_*))\subset C.               \tag{3}
\]

In the standard Hausdorff projective-configuration compactification, (3)
has a limit on the nonuniform boundary.  A compact `C` would have closed image
and would contain this limit, contradicting `C subset X`.  Therefore `C` is
noncompact.

This proves the following sufficient criterion.

> **Common-shear closure criterion.**  If every connected component of every
> relevant `B_rho intersection B_eta` contains one point satisfying (1), then
> diagonal two holds.  In particular it is enough to prove (1) at every
> simultaneous-bad point.

The criterion needs no continuous selection of escape directions.  It also
does not require a vector field, a monotone wall-label potential, or a proof
that the component-decorated transition graph is acyclic.  Those were needed
for a different Cech-incidence route, not after one proper moving-witness ray
has been found in the component.

## 2. Circuit-free finite test

For an oriented shear `d=(e,f,a)`, retain the signed derived rows whose
transport coefficient is compatible with `a`.  Strict Gordan duality gives

\[
 d\in E_T(\rho)
 \quad\Longleftrightarrow\quad
 \text{no complete derived-arrangement tope agrees with `rho` on all
 retained rows}.                                                  \tag{4}
\]

Consequently one exact complete-tope table determines the escape mask of
every abstract extension at the chart.  The verifier independently:

1. enumerates all 97,224 abstract extensions of catalog parent 2599;
2. reconstructs and verifies all 26,112 complete topes at each chart;
3. computes the 112-bit mask of each of the 71,112 bad extensions;
4. proves pairwise intersection by packed exact bitsets; and
5. computes the exact minimum overlap, not merely its positivity.

For the last step, sort the masks by size.  Two masks of sizes `r,s` in a
112-element universe have overlap at least

\[
                            r+s-112.                              \tag{5}

Once (5) reaches the incumbent minimum, all later, larger partners are
rigorously pruned.  Every unpruned pair is tested by integer `bit_count`.

## 3. Exact verification

Run the full replay with:

```console
PYTHONDONTWRITEBYTECODE=1 python \
  ai/omreal/verify_diag2_escape_set_atlas178.py --workers 8
```

An optional deterministic per-chart JSON summary can be written with
`--analysis-output`.  The verifier pins the aggregate digest, global minimum
escape size 53, and global minimum overlap 6.  The original smaller audit in
`verify_diag2_escape_set_topes.py` remains a faster independent regression.

## 4. A genuine mutation is not a one-tope update

The exact `37 -> 44 -> 37` wall-label cycle from
`DIAG2_PIVOT_ALL_COMPACT_SECOND_WALL.md` occurs at a nongeneric chart with
additional labeled residual coincidences, so it is not suitable for measuring
one generic compound mutation.  A separate exact perturbation was therefore
constructed at the transverse canonical type-37/type-44 intersection

```text
a = 104671347209/204100224200
b = -2983/1000
c = -509/500
d = 66134514061/255125280250
e = -991/1000
f = 1997/1000
g = 2007/1000
h = 3009/1000
i = -2987/1000
```

Exactly two of all 26,740 localized residual factors vanish there: canonical
factor IDs 2342 (type 37) and 3487 (type 44).  Four rational perturbations
realize the four adjacent sign chambers.  Each has 26,112 topes, and each
edge flips exactly its intended one residual factor.  Nevertheless crossing
one edge removes 72 topes and adds 72 topes.  Thus a proposed atlas
propagation proof cannot model a generic residual crossing as the exchange of
one antipodal tope pair.

At the four adjacent charts there are 75,026 valid abstract extensions and
48,914 bad extensions.  Every bad pair still has a common shear; the minimum
escape size is 52 and the minimum pair overlap is eight in all four chambers.
Across an edge, 1,238 or 1,410 of the 48,842 signatures bad on both sides
change escape mask, and a single mask can lose as many as 28 directions.
Therefore the six- or eight-direction margin alone does not imply mutation
stability by a cardinality bound.  A successful propagation theorem must use
the signed structure of the 72 exchanged topes.

These mutation-square calculations are replayed and pinned by
`verify_diag2_escape_set_mutation_square.py`, with semantic digest

```text
cfcaa8d8794655e9b8c480b40156ed044904530aa30354d0f52785403eb289ef
```

They are an exact local theorem and a no-go for a tempting shortcut, not a
global chamber-coverage result.

## 5. Remaining proof target

The diagonal-two frontier can now be stated without the earlier ambiguity:

> Prove that `E_T(rho) intersection E_T(eta)` is nonempty for every uniform
> realizable parent chart and every relevant simultaneously bad proper
> incomparable signature pair.

There are two plausible ways to make that universal:

1. prove a covector-elimination or signed-overlap theorem for the complete-
   tope restriction systems; or
2. certify complete residual-chamber coverage for every `UOM(4,8)` parent and
   replay the finite set-system check in every chamber, with lower-dimensional
   strata handled by exact limiting or wall certificates.

A disjoint exact pair would refute this elementary-shear route but would not
by itself refute diagonal two; the decorated transition-cycle and other
geometric escape routes would remain available.
