# Constructive guess-and-check: a reserve survives the actual rank event

**Result: an exact local continuation certificate and a conditional selection lemma.** The pinned actual parent has a five-row positive reserve circuit whose normals are constant along the coordinate direction that destroys the original three-row circuit. We also construct a full 56-row normalized witness with every weight at least 1/1000 on a certified closed interval. This is a successful local test of support enlargement. It does not establish original injectivity, global bad-locus selection, or any original 9DVL obligation. Ledger: 2/9.

## Source and conventions

Input: `inputs/certificates/THREE_ROW_WITNESS.json`, from diagnostic revision `3e69bc43f1a92ebd1c508bd75e695af76c99e0b0`, mathematical source revision `59fec66666518257c585194b81061f60d91f439d`. The machine certificate binds the input bytes by SHA256 and repeats the literal parent and expected 70 parent signs. Admissibility of this fixed signature and its role in the source antichain are inherited from the pinned source; this track does not replay the distinct anchor certificates. Row indices are zero-based in colex order on the triples of eight labels. Signature is exactly `40418075143643136`. Normals are raw signed cofactor normals; no positive-gcd or Euclidean renormalization is used.

Write A(Y) for the 4-by-56 matrix with these signed normals as columns, and E(Y) for A(Y) with a bottom row of ones. The witness polytope is P(Y)={w≥0:E(Y)w=(0,0,0,0,1)}. The family changes only Y[2,0], adding t to its value -13591/3472. All other coordinates remain exactly those of the source parent.

## Guess checked and exact outcome

Guess: although the selected three-row circuit exists only at a rank event, another support can provide a continuous witness through that event.

One seeded numerical LP, restricted to triples avoiding the moving column 0, suggested support [17,24,33,40,54]. All subsequent acceptance is exact rational arithmetic. No larger support census was conducted. The triples and a common integer scaling of their constant positive weights are:

| Index | Triple | Unnormalized positive weight |
|---|---|---:|
| 17 | (1,4,5) | 403827320 |
| 24 | (1,3,6) | 878543882 |
| 33 | (3,5,6) | 758740625 |
| 40 | (2,3,7) | 599416805 |
| 54 | (4,6,7) | 537553744 |

The weights sum to 3178082376. After division by that sum, their signed normal combination is zero. Their 5-by-5 augmented matrix E_S has determinant 82630141776. It follows that the five signed normals have rank four and this is a strictly positive circuit. All five triples avoid column 0, so their normals and this normalized witness are constant for every t, even outside the parent chamber.

Exact affine parent brackets give the maximal strict parent interval along this line:

(-75255/111104, 94285/38192).

The certificate uses the compact subinterval

I=[-75255/222208, 75255/222208].

All 70 bracket signs hold throughout I. Since only one matrix entry changes, each bracket is affine in t, and endpoint sign checks prove the whole interval, including t=0.

The original support [35,24,17] has rank two at t=0. Its minor in normal coordinates [1,2,3] is exactly -27081600*t. Thus it has rank three at every nonzero t and its old three-row weights fail immediately off the event. Its disappearance does not eliminate the signature's badness: the reserve remains a positive normalized witness.

## Full-support continuation

A sparse continuous section alone need not imply continuity of the canonical minimum-norm witness. We therefore verify the stronger interior-feasibility condition.

Let q=E_S^{-1}b be the reserve weights, b=(0,0,0,0,1), and let s(t)=E(Y(t))1 be the sum of all 56 augmented columns. Set epsilon=1/1000. Put epsilon in all 56 coordinates, and on reserve coordinates add

q - epsilon E_S^{-1}s(t).

The resulting full vector w(t) is affine because E_S is constant and s(t) is affine. Its augmented equality is identically

E(Y(t))w(t)=epsilon s(t)+E_S(q-epsilon E_S^{-1}s(t))=b.

The certificate records all constant and slope coefficients. Every weight is at least 1/1000 at both endpoints of I, hence throughout I. Polynomial equality is checked coefficient by coefficient, including any apparent quadratic coefficient; none is accepted by numerical sampling.

## A second section that equals the original three-row witness at the event

The full56 section above is a support-robust replacement and does not equal the original sparse witness at zero. A separate exact construction now provides that stronger literal handoff.

Let u be the original normalized three-row witness (weights 5642,2595,3450 on [35,24,17], divided by 11687). Embed the constant reserve q in 56 coordinates, writing q_full. Let d=A'(t)u and let v=E_S^{-1}(d,0), also embedded on reserve coordinates as v_full. Choose

C=1+max_i(|v_i|/q_i)=2205884133/880139125.

Then the following is a continuous normalized Gordan witness for the entire family:

h(t)=(u+C|t|q_full-t v_full)/(1+C|t|).

It satisfies h(0)=u exactly. Indeed A(t)u=t d, A(t)q_full=0, and A(t)v_full=d because all reserve columns are constant. Thus A(t)h(t)=0. The coordinate sum is one because sum(u)=sum(q_full)=1 and sum(v_full)=0. On reserve coordinates its numerator is u_i+|t|(Cq_i-sign(t)v_i), which is nonnegative because Cq_i>|v_i|; outside reserve coordinates its numerator is u_i≥0. The denominator is strictly positive. These arguments apply for every real t; claims about the original parent stay restricted to I.

The support is [17,24,33,35,40,54] for every nonzero t. At zero it is exactly the original three-row support. The formula may have a corner at zero and is not claimed to be minimum norm. It enlarges support and is not a face-preserving contraction. Its two rational branches are checked by exact polynomial coefficients, not just endpoint tests. The machine certificate records u, q_full, v_full, C, and all positivity slack values.

## Conditional minimum-norm selection lemma

**Lemma.** Let x range over a metric space (in the application, an open subset of Euclidean parent coordinates), E(x) be a continuous family of real r-by-m matrices, and b be fixed, and suppose the feasible set P(x)={w≥0:E(x)w=b} lies in a common compact simplex because the normalization sum(w)=1 is included. If E(x0) has full row rank and P(x0) contains a vector z with all m coordinates strictly positive, then P(x) is nonempty near x0 and its unique minimum-Euclidean-norm element is continuous at x0.

**Proof.** Full row rank persists locally. The continuous right inverse R(x)=E(x)^T(E(x)E(x)^T)^{-1} exists there. Given any u∈P(x0) and eta∈(0,1], form u_eta=(1-eta)u+eta z. This vector is strictly positive. The transported vector

u_eta(x)=u_eta+R(x)(b-E(x)u_eta)

is feasible and strictly positive for x sufficiently close to x0, and tends to u_eta as x→x0. Taking u=z proves nearby nonemptiness. Each P(x) is compact and convex, so squared norm has a unique minimizer m(x). For any sequence x_n→x0, simplex compactness provides convergent subsequences of m(x_n). Every subsequential limit v belongs to P(x0) by continuity of E. The minimizing inequality against u_eta(x_n), followed by n→infinity and then eta→0, gives ||v||²≤||u||² for every u∈P(x0). Uniqueness makes v=m(x0). Every convergent subsequence has this same limit, proving continuity. QED.

The minimum-Euclidean-norm choice is made in the fixed raw-normal weight coordinates. It is not asserted invariant under arbitrary positive rescaling of individual normals or changes of parent normalization; such a change can change the selected witness. The lemma is a standard convex-feasibility argument presented here with proof, not a novelty claim. The numerical LP never computes or certifies the canonical minimizer itself.

**Application to this fixture.** E_S is invertible, so E(Y(t)) has full row rank throughout I. The exact affine w(t) has all coordinates positive there. Thus the canonical minimum-norm witness is continuous at every Y(t) in this interval. Moreover, the hypotheses persist in an open neighborhood in the full 32-coordinate parent space, not just on the line: determinant and strict positivity are open conditions and the preceding right-inverse construction applies to arbitrary sufficiently small parent perturbations. The 70 strict bracket signs also persist locally. No quantitative 32-dimensional neighborhood is certified here.

## What this does and does not test

- Slater here means strict positivity of every normalized dual weight relative to the five affine equalities. A positive witness on only three rows does not supply it. Our full56 certificate does.
- The E rank condition is essential to this proof; a fixed chosen circuit losing rank does not say that full E loses rank. Here full E stays rank five by a completely different support.
- The explicit section w(t) is not asserted to be the minimum-norm section. Its strict positivity supplies the hypotheses proving continuity of that canonical section.
- This pinned event is a three-row rank event, not the separately inherited zero-weight feasibility boundary. No claim about that other event is made.
- Support enlargement is intentional. The construction does not preserve every support face, does not supply a face-natural contraction, and does not undo the previous strict face-natural-contraction obstruction.
- Nothing here gives a compact-support comparison map, compatible choices among signature intersections, global parent/chart coverage, control at infinity, injectivity of the target cohomology map, or triple Hc0 vanishing.

## Replay and hostile controls

`python constructive/verify_constructive.py` from the cycle root regenerates all exact quantities and compares them against `CONTINUATION_CERTIFICATE.json`. It uses only the Python standard library and imports no earlier producer/acceptance code. The separate `discover.py` is the numerical proposal generator and requires NumPy/SciPy plus the pinned original helper; its output is not a proof dependency of replay.

Replay checks the complete literal family, all70 parent bracket signs on the interval, reserve independence and positivity, the full56 affine section, the source-matching support6 handoff on both parameter sides, and original support rank. Hostile controls reject an altered weight and the old three-row weights off the event, and accept those old weights exactly at the event. Independent referee replay remains a separate required gate before integration claims independent audit.

## Next discriminator

The next useful test is an actual parent boundary where every full-rank positive reserve disappears, so P(Y) has no strictly positive point. This fixture is too far inside the bad locus to discriminate global minimum-norm continuity. On those boundary strata, seek one-sided witness limits and test whether the normalized witness polytope is lower semicontinuous. Failure there would kill unconditional canonical selection while leaving this conditional lemma intact. More samples of this same robust event would not resolve that question.
