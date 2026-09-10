# Independent audit of a stronger finite geometric route

Verdict: the following conditional implication is valid. Its two new
geometric hypotheses are not proved by this audit. It gives no D3 promotion.

## Statement

Fix an original normalized parent component X. Let H_f range over its
finitely many complete primitive residual zero sets, without sector cuts
or chart-boundary deletions. Assume the inherited statements

1. `H_c^q(H_f;Q)=0` for q=0,1,2;
2. `H_c^0(H_f intersection H_g;Q)=0` for distinct f,g;
3. `H_c^2(X;Q)=0`; and
4. the all-strata persistence dichotomy and fixed-unit aligned-circuit
   containment theorem for each genuine bad locus.

Add the following stronger geometric targets:

P. `H_c^1(H_f intersection H_g;Q)=0` for every distinct pair.

T. `H_c^0(H_f intersection H_g intersection H_h;Q)=0` for every distinct
triple.

Then every finite union B of genuine extension bad loci has
`H_c^2(B;Q)=0`. In particular, the original D3 conclusion follows for
every three-element proper incomparable extension family.

## Proof

Let A consist of the global factors admitting an occurrence aligned with
at least one of the selected signatures, and let W be the finite union of
their whole walls. Fixed-unit signs give W subset B. Every point of the
boundary of B is a boundary point of at least one selected bad locus.
At such a point no locally persistent circuit can certify that badness;
the all-strata dichotomy therefore produces an aligned residual circuit.
Thus the boundary of B lies in W. Equivalently, B minus W is a union of
connected components, hence a clopen subset, of X minus W.

Finite closed-cover compact-support Mayer--Vietoris for W has
`E_1^(p,q)=direct_sum H_c^q(H_(f0) intersection ... intersection H_(fp))`.
In total degree one, the singleton H_c^1 terms vanish by assumption1 and
the pair H_c^0 terms vanish by assumption2. Hence H_c^1(W)=0. In total
degree two, the singleton H_c^2 terms vanish by assumption1, the pair
H_c^1 terms vanish by P, and the triple H_c^0 terms vanish by T. Hence
H_c^2(W)=0. Terms in higher columns cannot create cohomology in total
degree two when all its E1 terms are zero.

The closed/open sequence for W subset X contains

`H_c^1(W) -> H_c^2(X minus W) -> H_c^2(X)`.

Both outer groups vanish, so H_c^2(X minus W)=0. A clopen decomposition
splits compact-support cohomology into a direct sum; consequently
H_c^2(B minus W)=0. The closed/open sequence for W subset B contains

`H_c^2(B minus W) -> H_c^2(B) -> H_c^2(W)`.

Again both outer groups vanish, proving the result.

The ambient assumption3 follows from compact-support duality in X and
the inherited parent contraction-height bound: H_c^2(X) is H_7(X)=0.
The argument therefore does not require the full parent-contractibility
quotation. All spaces used are locally compact semialgebraic sets, so
finite closed-cover descent and the displayed compact-support sequences
apply. An artificial bounded scope would invalidate the argument.

## Consequences and limits

This reduction would replace the unknown full pair-gluing inventory with
the stronger finite geometric target P, whose factor-pair orbit denominator
is inherited as 9,476. An exhaustive source theorem verifying P at this
denominator must cover all parent components and all rank strata, with
equivariant label/reframing transport. One exact chart per factor orbit is
not sufficient. The triple target T remains independently unresolved.

The union W may contain several active factors from the same signature.
Therefore T must cover every distinct triple among its factors, including
triples which cannot be matched to three different signatures. The weaker
prescribed-signature matching refinement of the triple-bad compactness
reduction does not directly suffice here. The universal all-factor triple
program has the required stronger scope.

P alone is not asserted to imply original pair-map injectivity. The
proof above needs T to kill the triple-wall column in H_c^2(W); without T,
the active-wall decomposition has not removed that contribution.

The graph countermodel in DIAG3_PAIR_DIFFERENTIAL_ENDS.md does not refute
this implication: its pair-wall H_c^1 groups are nonzero, so it violates P.
That countermodel correctly refutes a weaker substitution which asks only
H_c^1(W)=0 and factor component noncompactness. Here H_c^2(W)=0 is proved
from P and T, not inferred from H_c^1(W).

The reduction is elementary topological bookkeeping on top of inherited
geometry. Its value is a precise alternative sufficient endpoint; it is
not evidence that P is true or easier than the original pair restriction.

## Same-factor escape: novelty correction

The initially suggested same-factor multi-circuit escape is already
explicitly proved in RESIDUAL_STRATUM_NONCOMPACTNESS.md section3 and in
DIAG3_TRIPLE_FACTOR_REDUCTION.md sections1--3. The older local-target
sentence in ATLAS_HELLY.md is superseded by those statements. It must
not be reported as a new geometric result of this cycle.
