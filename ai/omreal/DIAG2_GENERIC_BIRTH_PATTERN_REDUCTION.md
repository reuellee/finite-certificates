# Diagonal two: exact support-drop pattern reduction

## Result

The support-drop frontier for diagonal two has a small exact signed residue,
and its exchange-saturated closure now proves diagonal two.

At a localization wall, the active positive circuit has size three.  The
complete source-hard `3+5` census consists of 32 labeled partner supports,
or eight orbits after the stabilizer is required to preserve both the active
three-circuit and the dropped residual normal.  Shared-parent rank-four
Grassmann--Pluecker constraints together with incompatibility for all 56
ordered elementary shears make all eight decorated formulas UNSAT.

At an ordinary wall, the active positive circuit has size four.  The exact
unsigned low-source filter leaves 53 support-pair orbits.  The shared-parent
signed constraints reduce these to 23, and the available fixed-unit wall and
partner cofactor identities reduce them to ten:

\[
                         \boxed{53\longrightarrow23\longrightarrow10}.
\]

The ten are necessary abstract signed support candidates, and all ten partner
supports are disjoint from their active wall circuit.  The complete ordinary
`4+4` census leaves only three labeled source-hard pairs; shared-parent
Grassmann--Pluecker constraints and all 56 shear conflicts make all three
UNSAT.  Two of the ten `4+5` candidates are
now realized at exact uniform generic type-50 and type-51 wall points,
proving that the stronger arbitrary-selected-witness theorem is false even
in the `4+5` support-drop regime.  Complete-tope escape masks repair both
exact obstructions.  Their intersections have respectively 51 and 80
oriented shears.  Reciprocal exact child matrices with the same two parent
chirotopes prove that both signature pairs have nonempty, proper,
incomparable feasibility regions.  Neither is a full-mask counterexample or
a compact component.

The selected wall and partner cofactors in the ten patterns touch exactly 35
primitive residual factors: four wall factors and 31 partner-cofactor
factors.  This is a selected-pair footprint, not a full escape-mask chamber
atlas; the complete derived arrangement can change on other residual walls.
The exchange-saturated theorem in
`DIAG2_EXCHANGE_SATURATED_SUPPORT_DROP.md` bypasses that atlas: a positive
minimal five-circuit spans four-space as a cone, so exchanging through a wall
triple produces a positive circuit which meets the wall support.  That
contradicts the complete disjoint rigid-support residue.  The all-strata and
clopen steps then exclude compact simultaneous-bad components.  The honest
9DVL score is now `2/9`.

## 1. Why a support-drop theorem matters

For a signature `rho`, a bad point has a support-minimal positive Gordan
circuit on at most five derived normals.  If a compact simultaneous-bad
component carried only locally persistent witnesses—strict five-circuits or
structural minimal three/four-circuits—for both signatures at every point,
the pair condition would be open there.  Closedness would then give an
impossible compact clopen component of the connected noncompact parent cell.
Thus a compact residue reaches a point at which one signature has a
**nonstructural** minimal circuit of size three or four.

The all-strata rank and padding theorem classifies that circuit even at a
simultaneous or nontransverse wall:

- an ordinary four-circuit at wall types
  `37,38,41,42,44,48,49,50,51`; or
- an active three-circuit at localization types `36,39,46,47`.

At a localization occurrence, any partner of size at most four gives at most
seven colored triples together with the active three-circuit and is automatically
pencil-flexible; all eight source-hard size-five formulas are UNSAT.  At an
ordinary wall the same count handles partners of size at most three.  The
three source-hard size-four occurrences are all signed UNSAT, including on
simultaneous-wall strata.  Every actual minimal five-circuit satisfies the
verifier's `generic5` predicate: four triples through a label are dependent
in a three-dimensional annihilator, and three triples through a label-pair
are dependent in a two-dimensional annihilator.

The moving-witness shear lemma gives the exact closure mechanism.  For an
ordered shear `e -> f`, let

\[
 m(e,f)=\#\{I\in P:e\in I,\ f\notin I\}
       +\#\{I\in R:e\in I,\ f\notin I\},              \tag{1}
\]

where `P` and `R` retain their two colors, so a triple belonging to both is
counted twice.  The compatibility test contains exactly `m(e,f)` transport
signs.  If `m(e,f)<=1`, those signs are automatically constant and the
oriented shear escapes to a parent boundary.  Consequently an incompatible
selected witness pair must satisfy

\[
                         m(e,f)\ge2
        \qquad\text{for all }e\ne f.                  \tag{2}
\]

Call (2) **source-hard**.  This unsigned condition is only necessary.  The
signed verifier asks whether all 56 shear tests can actually conflict for
two extensions of one rank-four parent.

A universal selected-witness small-support one-point exit theorem would have
finished diagonal two:

> whenever a simultaneous-bad point carries minimal circuits `P,R` with
> `|P|<=4` and `|R|<=5`, some common moving-witness shear exists.

The one-point component escape criterion would then send the entire
connected component to the parent boundary.  Section 5 gives an exact
counterexample to this selected-witness statement.  It simultaneously shows
why the statement was stronger than necessary: exchanging witnesses makes
the full escape masks intersect in 51 directions.  The correct target is
therefore the exchange-saturated one-point theorem

\[
                         E_T(\rho)\cap E_T(\eta)\ne\varnothing,    \tag{3}
\]

not compatibility of every preselected minimal pair.

## 2. Exact unsigned census

The C++ verifier exhausts all `C(56,5)=3,819,816` five-subsets.  It rejects
1,797,824 supports with a forced dependent proper subset and retains the

\[
                           2{,}021{,}992
\]

supports eligible to be minimal five-circuits.  The inherited predicate name
is `generic5`, but Section 1 proves that this is a minimality condition, not a
generic-point assumption.  For each canonical wall
support it retains precisely the partners satisfying (2), then quotients by
the stabilizer of that wall support.  The ordinary counts are:

| wall type | labeled source-hard partners | stabilizer orbits |
|---:|---:|---:|
| 37 | 8 | 1 |
| 38 | 0 | 0 |
| 41 | 8 | 2 |
| 42 | 0 | 0 |
| 44 | 4 | 1 |
| 48 | 48 | 2 |
| 49 | 96 | 27 |
| 50 | 22 | 7 |
| 51 | 76 | 13 |
| **total orbits** | -- | **53** |

The C++ support verifier also exhausts all 367,290 four-subsets as possible
partners at the nine ordinary wall types.  The signed-factor replay maps the
survivors to primitive residual factors.  Only three labeled source-hard
supports survive, in two wall-stabilizer orbits:

| wall type | partner support | partner factor | wall factor |
|---:|---|---:|---:|
| 49 | `167/348/568/278` | 1933 | 2267 |
| 49 | `167/258/368/478` | 1973 | 2267 |
| 51 | `356/347/258/178` | 6017 | 18606 |

The two type-49 rows form one orbit of size two; the type-51 row is fixed by
the relevant stabilizer.  Every partner factor differs from the wall factor.
There are no source-hard structural, fixed, or same-factor four-partners.
Thus this entire unsigned `4+4` residue belongs to distinct simultaneous-wall
strata, not the generic simple-wall calculation.  The signed verifier now
adds the shared-parent GP axioms and all 56 conflict predicates and makes all
three formulas UNSAT.  Its additional factor `1973` is outside the 35-factor
footprint of the ten `4+5` candidates, but no `4+4` obstruction survives.

For each localization type there are eight labeled source-hard partners.
The decorated stabilizer must preserve the active three-circuit and the
specific residual normal which has dropped:

| type | active circuit | dropped normal | decorated orbit sizes |
|---:|---|---|---|
| 36 | `123/345/367` | `124` | `4+4` |
| 39 | `123/356/378` | `124` | `8` |
| 46 | `123/145/167` | `246` | `2+6` |
| 47 | `123/145/167` | `248` | `4+2+2` |

Thus the localization census is 32 labeled partners and eight decorated
orbits.  Quotienting by the active-circuit stabilizer alone would incorrectly
collapse each row to one orbit and forget the wall occurrence.

## 3. Exact signed formulas

The signed verifier uses 182 Boolean variables:

- 70 shared parent bracket signs;
- 56 signs of the `rho` extension; and
- 56 signs of the `eta` extension.

It compiles all shared-parent rank-four Grassmann--Pluecker NAE relations and
ten gauge units.  For each colored support pair it then adds one NAE relation
for every ordered shear.  This relation forbids all transport signs from
being equal, so a satisfying assignment represents a necessary abstract
configuration in which every selected-witness shear conflicts.

All eight localization formulas are UNSAT.  Each contains 34,122 unique
clauses including the gauge units.

For the 53 ordinary representatives, the first signed stage gives the middle
column below.  A second stage adds every transported fixed-unit certificate
for the positive wall circuit and the necessary equality of all fixed-unit
partner cofactors after twisting by `eta`.

| type | source-hard | GP + 56 shear conflicts | fixed-unit signed stage |
|---:|---:|---:|---:|
| 37 | 1 | 0 | 0 |
| 38 | 0 | 0 | 0 |
| 41 | 2 | 1 | 1 |
| 42 | 0 | 0 | 0 |
| 44 | 1 | 0 | 0 |
| 48 | 2 | 0 | 0 |
| 49 | 27 | 9 | 4 |
| 50 | 7 | 3 | 3 |
| 51 | 13 | 10 | 2 |
| **total** | **53** | **23** | **10** |

The deterministic exact CDCL solver returns `SAT` or `UNSAT` in every case;
no formula reaches its conflict limit.  Every returned model is checked
against every input clause.

The same shared-parent formula eliminates the three ordinary `4+4` rows in
Section 2.  Each normalized formula has 34,122 clauses; their SHA-256 digests
are respectively
`56db6f1ed30a94e52780001bba0468f9858aed11873f53940e926ad2b787e60f`,
`abab41549d57ce75f776048e6d3ede86ca21c4e9c9454d231c65c3dc80958ec5`,
and
`11d371417e70b30250110b3b249ec6c68ebf24049a20c63bcf2755b734a69a8b`.

## 4. The ten necessary candidates

The four canonical wall supports and their surviving partner supports are:

| type | wall support `P` | partner support `R` |
|---:|---|---|
| 41 | `123/124/356/457` | `137/267/238/158/468` |
| 49 | `123/145/246/357` | `247/167/148/258/368` |
| 49 | `123/145/246/357` | `347/167/258/368/178` |
| 49 | `123/145/246/357` | `347/167/138/568/278` |
| 49 | `123/145/246/357` | `235/167/348/568/278` |
| 50 | `123/145/246/378` | `356/247/167/148/258` |
| 50 | `123/145/246/378` | `356/457/167/148/258` |
| 50 | `123/145/246/378` | `346/147/567/258/168` |
| 51 | `123/145/267/468` | `135/356/347/258/178` |
| 51 | `123/145/267/468` | `356/347/157/258/178` |

Every displayed partner support is disjoint from its wall support.  The
abstract residue does not disappear merely by requiring realizable parent
geometry: the next section gives exact realizations of two candidates in two
parent chirotope strata.  A direct selected-pair proof would still require
the simultaneous geometric cofactor sectors and full escape masks.  The
exchange-saturated theorem avoids that atlas by exchanging each rigid
five-circuit through a wall triple and contradicting this disjoint list.

## 5. A realized selected-witness obstruction, repaired exactly

The first type-50 survivor is genuinely realized:

```text
P   = 123/145/246/378
R   = 356/247/167/148/258
rho = 4380492134087405
eta = 13817772255984237
```

In normalized coordinates `(a,b,c,d,e,f,g,h,i)`, an exact point is

```text
2574354/734987,
-206747/385594,
888999/373972,
-9029165101298939406043/1506368035830677386928,
-101013711008/11454876655,
-881637/996208,
-686811/867154,
-486314/994133,
-36178/872041.
```

Exact arithmetic proves all of the following:

- all 70 parent brackets are nonzero;
- `rho` and `eta` belong to the 60,008 valid extensions of that parent;
- `P` and `R` are strict positive circuits for the displayed signatures;
- among all 26,740 primitive residual factors, only the canonical type-50
  factor `5563` vanishes; and
- the selected colored supports have no compatible ordered shear.

This is a uniform generic point of precisely one residual wall, so the
selected-witness theorem fails in its intended geometric domain rather than
only in an abstract signed relaxation.  Exact `2^-16` samples on the two
sides of the affine wall pivot have the same parent chirotope, reverse the
residual factor, and carry strict positive `rho` five-circuits extending `P`.
Together with the nonzero affine coefficient, this certifies a transverse
support-drop germ rather than an isolated four-circuit coincidence.

The complete derived arrangement at the wall has 26,110 exact topes.  The
circuit-free restriction criterion gives

\[
 |E_T(\rho)|=69,\qquad |E_T(\eta)|=93,\qquad
 |E_T(\rho)\cap E_T(\eta)|=51.                       \tag{4}
\]

The mask union contains 111 of the 112 oriented directions; only
`(1,8,-1)` lies outside both masks.  Thus witness exchange does not merely
repair the example—it leaves a large common-shear margin.  By the one-point
component escape criterion, the simultaneous-bad component containing this
point is noncompact.

The repair can also be made completely explicit.  Exhaustive exact circuit
enumeration gives 101 positive minimal `rho`-circuits and 2,062 positive
minimal `eta`-circuits.  Among all

\[
                          101\cdot2{,}062=208{,}262
\]

selected circuit pairs, the displayed `P,R` is the unique pair with no
compatible ordered shear.  Replace `258` in `R` by `123`:

```text
R' = 123/356/247/167/148.
```

This is another strict positive `eta`-circuit and `P,R'` have twelve
compatible ordered shears.  Thus one circuit exchange repairs the unique
selected-witness obstruction at the point.

There is a second realized survivor of type 51:

```text
P   = 123/145/267/468
R   = 356/347/157/258/178
rho = 31372044921362707
eta = 28905737156930761
```

It lies at a uniform generic point whose sole residual zero is the type-51
factor `18606`.  Again the selected pair has no compatible ordered shear and
the wall arrangement has 26,110 complete topes.  Here

\[
 |E_T(\rho)|=91,\qquad |E_T(\eta)|=101,\qquad
 |E_T(\rho)\cap E_T(\eta)|=80,                         \tag{5}
\]

and the two masks together cover all 112 oriented directions.

The type-51 replay certifies the analogous transverse two-sided support-drop
germ.  Both repair verifiers also store two exact integer `4 x 9` child
matrices with the same parent chirotope as their wall point: one realizes
`rho` while a strict positive circuit obstructs `eta`, and the other realizes
`eta` while a strict positive circuit obstructs `rho`.  Consequently each
displayed pair has nonempty, proper, reciprocal-incomparable feasibility
regions.  This verifies that the selected-witness counterexamples occur in
the relevant diagonal-two class; the child certificates are not being used
as local paths from the displayed wall.

## 6. The 35-factor selected-pair cofactor footprint

The 50 partner four-cofactor occurrences split into 43 residual occurrences
and seven fixed parent units.  The residual occurrences use 31 distinct
primitive global factors:

```text
211, 1011, 1187, 1851, 1933, 2623, 4738, 6016, 6017, 6239,
7807, 12110, 13863, 18201, 19852, 20014, 20050, 20227, 20274,
20321, 21825, 22224, 22270, 22303, 22321, 22443, 22581, 23091,
23357, 24225, 26180
```

The wall factors are:

| wall type | factor ID |
|---:|---:|
| 41 | 8543 |
| 49 | 2267 |
| 50 | 5563 |
| 51 | 18606 |

Their union has exactly 35 factors.  Together with the fixed parent-bracket
unit signs and occurrence orientations, these factors are sufficient to
express the positivity conditions for the ten selected support pairs.  They
are not sufficient to determine the full escape masks: those depend on the
complete derived-arrangement tope table, which may change after crossing any
other residual wall.  A direct selected-pair atlas would therefore have had
to do one of the following for every remaining sector:

1. prove that its required cofactor-sign sector is absent on the indicated
   wall inside every realizable uniform parent cell; or
2. realize the sector and control the full escape masks on every refinement
   by the other residual-factor signs, allowing all witness exchanges.

The realized type-50 and type-51 points take the second branch and are
repaired by (4)--(5).  The proved conic exchange theorem now makes this
sector-by-sector route unnecessary: it establishes (3) at every
nonstructural support drop without determining any full mask.

## 7. Exact verification and scope

Run the unsigned census with:

```console
python ai/omreal/verify_diag2_generic_birth_support_filter.py
```

Run the signed reduction with:

```console
python ai/omreal/verify_diag2_generic_birth_pattern_reduction.py
```

Replay the exact realized obstruction and full-mask repair with:

```console
python ai/omreal/verify_diag2_generic_birth_exchange_repair.py
```

Replay the exhaustive positive-circuit exchange census with:

```console
python ai/omreal/verify_diag2_generic_birth_circuit_exchange.py
```

Replay the second realized type-51 repair with:

```console
python ai/omreal/verify_diag2_generic_birth_type51_exchange_repair.py
```

The signed-reduction verifier pins the complete formula digests, localization
quotient, ordinary stage counts, ordered survivor list, the three `4+4`
UNSAT formulas, disjointness of all ten `4+5` survivors, cofactor census, and
selected-pair cofactor footprint in the semantic digest

```text
4546a2e7ba03c1c9dd63abbe65195fc348accf9bf91ccaa773072f1fcae9df38
```

The exchange-repair point, its complete parent-extension census, exact
circuit coefficients, transverse support-drop germ, reciprocal
same-parent-chirotope child certificates, all 26,110 complete topes, and both
112-bit masks have semantic digest

```text
67d6640c8516ed3e7eac0dfcb95da2413a1d96453f1089387eb41dcbcd853a62
```

The exhaustive type-50 circuit census has semantic digest

```text
4d3ae50be6d6f86794e9b25afb83100a4262bc2f5dbb0990d06c9020c8cb8521
```

The type-51 full-mask repair has semantic digest

```text
1957aa0e56d82d362c77fb5f1a4b6e457066df2b3141c1550f51d094ea0d9801
```

The finite formulas are necessary-condition filters and do not assert that a
SAT survivor is geometrically realizable.  That one-way scope is sufficient
for the proof.  Minimal-five eligibility removes the apparent nongeneric
support gap, the all-strata rank/padding theorem covers simultaneous and
nontransverse walls, and the persistent-circuit clopen alternative covers
components which do not meet a nonstructural support drop.  The realized
examples still show that an incompatible selected pair does **not** make the
full escape masks disjoint.  With the theorem in
`DIAG2_EXCHANGE_SATURATED_SUPPORT_DROP.md`, diagonal two is promoted
integrally and the honest score is `2/9`.
