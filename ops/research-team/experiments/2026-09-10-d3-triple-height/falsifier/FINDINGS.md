# Independent falsification track: fixed-projection height equations

## Outcome

No actual counterexample to triple escape was found. A bounded exact classification does rule out every uniform vertical critical point for the 231 pairs among 22 actual quadratic restrictions at one fixed projected parent configuration. It does **not** rule out a compact smooth component of one of those intersections, prove a universal critical-locus theorem, or close an original obligation. Original status remains **2/9**, with the inherited factor-pair endpoint complete at **9476/9476** and zero new triple-source credit.

The new global reduction in `../proof/VERTICAL_CRITICAL_REDUCTION.md` is deductively sound at the hash recorded below: it confines the remaining compact-support degree-zero obstruction to a closed vertical critical locus. Vanishing on that locus remains unproved.

## Actual parent and finite scope

The ordinary anchor is P=123/145/246/378. Its four contracted planes are fixed as the four ordered projective lines x=0,y=0,z=0,x+y+z=0. The chosen projected parameters are (2,3,4,5). The full four-height parent lift is

```
Y = [0 0 0 1 1 1  1  1]
    [0 1 1 0 0 3  4  5]
    [1 0 -1 0 2 0 -5 -6]
    [0 0 1 0 x y  z  w].
```

The height (-87,-32,-78,96) has all 70 parent brackets nonzero. The anchor determinant vanishes identically, and at this uniform lift its normal matrix has rank three with every three rows independent. `HEIGHT_OVAL_PROBE.json` stores the matrix, all 70 exact bracket values, and the 120 deterministic relabeled occurrences used. Its support arrays are zero-based; the displayed anchor is one-based.

The occurrences are relabelings of ordinary types 50 and 51. Exact determinants and factorization remove only factors proportional to one of the 70 affine parent brackets. The resulting sample contains six linear and 22 quadratic restrictions, as well as higher-degree, unit, or identically zero restrictions. The latter are outside this finite quadratic classification. The test is not an inventory of all primitive factors, parent realizations, or source rows.

The initial work used 120 occurrence instantiations at this one projected parent. The 231 pencils and their algebraic exceptions reuse these forms; the coordinator expressly authorized completing this concrete exception analysis. No additional projected-parent sampling was used.

## Exact quadratic inertia and a scoped escape lemma

Rational congruence gives homogenized five-variable inertia (positive,negative,zero) equal to (2,2,1) for 20 quadratics and (2,1,2) for trials 1 and 79. Full matrices appear in `QUAD_INERTIA.json`.

Consequently none of these quadratics restricted to an affine three-plane can have definite spatial rank three. A real quadric in affine three-space has a compact connected component only in the definite rank-three cases, including an isolated point at zero radius. Lower-rank definite forms leave a free direction or become a graph over an unbounded affine space; indefinite forms have no compact component. Restricting the homogenized quadratic to an affine three-plane cannot increase either inertia index. Thus each of these 22 quadratics has no compact zero component on any affine three-plane.

Intersecting that zero set with an open parent chamber cannot create a compact component: a semialgebraic component of the intersection is open in the full zero set locally, and, if compact, is also closed there. It would therefore be a compact connected component of the full quadric. This proves escape for any linear-plus-one-of-these-quadratics section in this fixed projected-parent chart, including singular restrictions. The original 120 linear/quadratic tests are consistent with this argument. This scoped lemma carries no universal triple-source count.

The inertia bound alone does not settle an intersection of two quadratics. A floating screen for definite spatial pencil combinations found none in these 231 pairs, but that screen is exploratory only and supplies no compactness conclusion.

## Complete finite critical-point classification

Write a quadratic as Q(v)=v^T A v in homogeneous height coordinates v=(x,y,z,w,t). At a common affine zero of Q and R, dependent four-height gradients are equivalent to

    (A + lambda B) v = 0

for some real pencil parameter lambda, or to A v=0 or B v=0 for a parameter endpoint. The equivalence uses Euler's identity: the fifth coordinate of the gradient combination also vanishes when Q=R=0 and t=1.

The finite coverage is as follows.

1. For the 193 pencils with nonzero determinant polynomial, a simple determinant root cannot produce a common zero in its kernel. At rank four, the determinant derivative is a nonzero scalar times v^T B v; a common zero makes that derivative vanish. At lower rank, the determinant root is already multiple. Exact factorization shows that every repeated root here is rational. All 104 repeated rational-root checks are covered. Their rank-four common-zero kernels are at infinity or violate a parent bracket. All 20 higher-nullity repeated-root checks are also excluded.
2. The remaining 38 pencils have generic rank four. Their generic kernel is one-dimensional and lies identically at infinity or on an explicit parent bracket. This identity extends across every parameter where rank stays four; poles of a chosen rational kernel vector do not create an extra rank stratum.
3. The exceptional parameters of each generically singular pencil are exactly the roots of the gcd of its 25 four-by-four minors. All 13 rational exceptional checks are excluded. The one nullity-three kernel has restricted common-zero equation -72 c1 c2: one linear component is at infinity and the other lies on parent brackets.
4. The remaining 24 irreducible nonlinear exception factors are handled in their exact rational quotient fields. Real-root isolation distinguishes real embeddings. Twelve common-zero radicals are at infinity, three lie on parent brackets, four entire kernels lie on parent brackets, and five factors have no real roots. In the radical cases the restricted quadratic has rank one, so its real zero set is exactly its radical; this does not discard a second real branch.
5. All 22 individual quadric kernels are at infinity or on parent brackets, covering the infinite pencil parameter.

It follows that every common zero of each of these 231 quadratic pairs in the actual uniform four-height locus has independent height gradients. This is a finite algebraic exclusion of vertical critical points, not a compactness proof. In particular, a smooth intersection surface can still have a compact component. No inference about the universal relation between criticality and collinearity of three concurrence points is made.

The evidence is split into `PENCIL_SINGULAR_PROBE.json`, `SINGULAR_PENCIL_FAMILY.json`, `EXCEPTIONAL_PENCIL_PROBE.json`, and `QUADRATIC_EXTENSION_PROBE.json`. Earlier-stage files deliberately retain their then-unresolved case labels; the later files cover exactly those cases. `PENCIL_COVERAGE.json` binds and checks the completed chain.

## Independent deductive review

No fault was found in `../proof/VERTICAL_CRITICAL_REDUCTION.md` at SHA256 `e7034f7b3b51fad14e925eeabed3a43cf134e72a1a3689fede5b4ac28b69477e`. The regular locus projects submersively to an open affine four-dimensional projected-parent base. Its semialgebraic components have nonempty open images and cannot be compact. The closed/open compact-support sequence then makes Hc0(K)=0 sufficient for full triple escape. The eight-height circuit formula follows from the rank-one adjugate of an ordinary rank-three normal matrix, and its four gauge annihilators are independent by the nonzero height-frame parent bracket.

The all-kind anchor model in `../referee/ANCHOR_COVERAGE_AUDIT.md`, SHA256 `e067b7f27de4c70877258a8094ad4003edc71713323d778323f52eb03bb9efe9`, retains the coincident projected high parents needed for kinds 36/38. Its three high-parent projections form a frame, the fourth original parent bracket fixes the remaining height scale, and excluded-plane evaluations give the required affine charts and positive column gauges. No fault was found in this coordinate extension.

The updated reduction removes the entire closed concurrence-collision union Delta before taking the regular/critical decomposition inside its open complement. Each collision piece has positive-dimensional full height fibers after anchoring at the repeated point, and the all-three-equal subset is handled separately by closed/open localization. Restriction injects Hc0 of a finite closed union into the sum of the piece groups. Thus the stated sufficient condition Hc0(K minus Delta)=0 uses the correct localization order and does not assume vanishing for an arbitrary intersection K intersect Delta.

No fault was found in the additional theorem `../proof/TWO_PARENT_LINE_FACTORS.md`, SHA256 `85c449f0d814872c92a9b07f5962a9af6fdaa6c0d18b8a779c86610ba5d05b44`. For two global36/38 factors, their unique concurrences lie on actual parent lines and have finite nonzero affine parameters because neither endpoint is allowed. At fixed projected parents and these two parameters, all four remaining equations are jointly affine in the four heights. A lower-rank fiber is full, connected, noncompact, and closed in the incidence. A rank-four component is a graph over an open subset of affine six-space. The argument retains collisions and every original component. This proves the stated all-parent subclass; numerical new-coverage credit remains with the coordinator.

This is acceptance of the reduction and coordinate model only. It is not a second proof of critical-locus vanishing. The exact known (39,48,50) canary has coincident 48/50 concurrence points; the coordinator additionally supplied its existing polynomial dependence. That inherited canary earns no new triple credit and was not used as evidence for a universal collinearity assertion.

## Replay and pinned inputs

From the cycle root run:

```
python falsifier/verify_pencil_coverage.py --replay
```

This reconstructs the actual determinants, exact inertia, regular and singular pencil kernels, rational and algebraic exceptions, and coverage summary. It uses Python and SymPy; acceptance arithmetic is rational or exact algebraic throughout. The optional floating exploratory screen is not part of this command or any acceptance condition.

The inherited checkpoint is commit `a7a98a927e57c8872aca2b1e48d4615ede649171`, tree `4f87a672cf5a992996a594e6617defea7cfa3889`, under `../checkpoint/` relative to this owned directory. The pair theorem input is `../checkpoint/original/CONCURRENCY_HEIGHT_PAIR_VANISHING.md`, SHA256 `c4542171cc2cd0c1dd5007bc80d3dfa2e079892cf6417edce760410eed069f91`. The work order SHA256 is `cee9ade6a166448ce61b7114e80f9b2d5a0bf3370e82083ded408f48a74ae506`.

The next mathematical discriminator is an actual uniform common zero, at another projected parent or for higher-degree restrictions, whose two vertical gradients are dependent while its three ordinary concurrence points are noncollinear. Its existence would refute the proposed localization of K, while still not refuting global triple escape. Absent such an example, a source-structured proof about the full closed critical locus is needed; this finite regularity classification cannot replace it.
