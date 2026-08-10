# Diagonal two: minimal tope separators and the eight-source cover

## Result

The complete-tope escape test has a smaller exact form.  Fix a uniform
rank-four parent chart `T`, a bad extension signature `rho`, and a source
label `e`.  It is enough to retain the inclusion-minimal disagreement sets
between `rho` and chart topes which agree with `rho` away from `e`.

At the catalog parent-16 base chart this reduces `2,063,096` raw
source-local tope disagreements to `287,560` inclusion-minimal separators.
For one signature and one source there can be as many as 282 raw candidates,
but at most six minimal ones.  The reduced families independently reconstruct
all 40,524 pinned escape masks and prove their pairwise intersection.

This is a genuine finite compression and a sharper theoretical target.  It
does not prove the universal common-shear theorem: the parent-16 calculation
is one exact chart, and no argument below excludes the resulting eight-source
cover for every realizable chart.

## 1. Separation subcubes

Let `A(T)` be the set of complete topes of the 56-row derived arrangement.
For sign vectors `v,rho`, write

\[
             \operatorname{Sep}(v,\rho)=\{I:v_I\ne\rho_I\}.
\]

For distinct labels `e,f` and `a in {+1,-1}`, define the deleted half-star

\[
 \Delta_\rho(e,f,a)=
 \{I:e\in I,\ f\notin I,\ \alpha_\rho(I;e,f)=-a\},       \tag{1}
\]

where `alpha` is the transport sign from
`DIAG2_MOVING_WITNESS_SHEAR.md`.  These are exactly the signed rows deleted
by the oriented shear `(e,f,a)` in the complete-tope restriction test.

> **Separation-subcube lemma.**
>
> \[
> (e,f,a)\notin E_T(\rho)
> \quad\Longleftrightarrow\quad
> \text{some }v\in A(T)\text{ has }
> \operatorname{Sep}(v,\rho)\subseteq\Delta_\rho(e,f,a). \tag{2}
> \]

Indeed, a complete tope defeats an escape direction precisely when it agrees
with `rho` on every retained row.  Its disagreements are therefore contained
in the deleted rows (1), and the converse is immediate.  Equation (2) is the
set-theoretic form of the strict-Gordan characterization in
`DIAG2_ESCAPE_SET_TOPE_REDUCTION.md`.

## 2. Inclusion-minimal separators

Put

\[
 S_e=\{I:e\in I\},\qquad
 \mathcal D_{T,e}(\rho)=
 \{\operatorname{Sep}(v,\rho):v\in A(T),\
                  \operatorname{Sep}(v,\rho)\subseteq S_e\}.    \tag{3}
\]

Thus (3) uses exactly the chart topes which agree with `rho` on all 35
triples not containing `e`.  Let `M_(T,e)(rho)` be the inclusion-minimal
members of (3).  Because `rho` is bad at `T`, none of them is empty.

> **Minimal-separator lemma.**  For every `e,f,a`,
>
> \[
> (e,f,a)\notin E_T(\rho)
> \quad\Longleftrightarrow\quad
> \text{some }D\in M_{T,e}(\rho)
>                 \text{ satisfies }D\subseteq\Delta_\rho(e,f,a). \tag{4}
> \]

If the right side of (2) holds, the finite family of separation sets
contained in its witness has an inclusion-minimal member.  The reverse
implication is tautological.  Hence nonminimal chart topes contain no further
escape information.

There is also a useful label-carrier form.  For nonempty `D subset S_e`, set

\[
 P_e(D)=\bigcup_{I\in D}(I\setminus\{e\}).             \tag{5}
\]

Then `D subset Delta_rho(e,f,a)` exactly when

1. `f` does not belong to `P_e(D)`; and
2. all values `alpha_rho(I;e,f)`, `I in D`, are equal to `-a`.

Consequently one minimal separator certifies nonescape for at most

\[
                       7-|P_e(D)|\le 5               \tag{6}
\]

oriented directions: `D` contains at least one triple and therefore at least
two partner labels, and for each eligible target it selects at most one of
the two orientations.  This carrier bound is independent of the chart.

## 3. The exact eight-source cover criterion

Let `U_e` be the 14 oriented elementary shears sourced at `e`, and put

\[
 N_{T,e}(\rho)=
 \bigcup_{D\in M_{T,e}(\rho)}
 \{(e,f,a):D\subseteq\Delta_\rho(e,f,a)\}.            \tag{7}
\]

By (4), `N_(T,e)(rho)` is exactly the local nonescape set, so

\[
             E_T(\rho)\cap U_e=U_e\setminus N_{T,e}(\rho).       \tag{8}
\]

The universal common-shear theorem is therefore equivalent to excluding the
following finite local cover at every simultaneous-bad point:

> **Eight-source cover obstruction.**  A pair `rho,eta` has disjoint escape
> sets exactly when, for every source label `e`,
>
> \[
>                N_{T,e}(\rho)\cup N_{T,e}(\eta)=U_e.             \tag{9}
> \]

This exposes two immediate necessary conditions for a counterexample.

* If (3) is empty for `rho` at a source `e`, then all 14 `e`-sourced
  directions escape for `rho`; (9) forces `N_(T,e)(eta)=U_e`.
* Since each nonempty minimal separator covers at most five directions by
  (6), every block in (9) needs at least three separator-cover sets across
  the two signatures.  Moreover both orientations at a fixed target require
  separators with opposite transport signs.

The precise remaining structural problem is to prove that the extension
Grassmann--Pluecker axioms, derived-arrangement covector elimination, and
simultaneous badness forbid all eight equations (9) at once.  It is not
enough to prove a lower bound for an arbitrary selected Gordan circuit: the
minimal families in (7) quantify over the full witness polytope through all
chart topes.

## 4. Exact parent-16 audit

Run:

```console
python ai/omreal/verify_diag2_escape_minimal_separators.py
```

The verifier independently enumerates the complete derived-arrangement
topes and all abstract uniform extensions at catalog parent 16.  For every
bad signature and every source it constructs (3), takes its inclusion
antichain, reconstructs (7), and pins the same semantic digest as the direct
restriction-hash audit.  It checks:

* 26,112 complete topes, 66,636 valid extensions, and 40,524 bad signatures;
* `2,063,096 -> 287,560` raw-to-minimal separator compression;
* maximum source-family sizes `282 -> 6`;
* the universal carrier bound (6) on every retained separator;
* minimum escape-set size 52, attained only by the antipodal pair already
  recorded; and
* absence of an eight-source cover (9) for every pair of bad signatures.

This is an exact theorem about one chart.  Promotion of diagonal two still
requires the universal cover contradiction or certified coverage of all
relevant residual chambers and boundary strata.
