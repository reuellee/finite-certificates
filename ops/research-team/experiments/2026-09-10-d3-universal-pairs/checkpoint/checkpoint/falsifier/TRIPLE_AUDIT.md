# Independent audit of the triple conic reduction and uniform fold

**Verdict: ACCEPT the universal conic identity, exact algebraic fold point, and algebraic six-variable reduction for this one named triple. No original triple-escape obligation is discharged.**

The source is `inputs/DIAG3_triple_fullspace_critical_h1.json`, SHA256 `c9244a47ded5736e7afe724a9914e75631a22b78653442e88c14f5c397919eb8`. Its first three original factors have IDs5563,16134,19284 in the named presentation of canonical row5563,4373,23221. Both independent scripts reconstruct polynomials directly from these sparse source records. Neither imports producer code, loads producer pickle files, or accepts a producer PASS as evidence.

## Exact branch point

`verify_triple_independent.py` independently verifies:

- The displayed polynomial in h is irreducible of degree4 over Q.
- An explicitly evaluated rational Sturm sequence has variation difference1 on the supplied rational interval; the endpoints are not roots.
- The three original factors vanish at the displayed rational functions of h, modulo its defining polynomial.
- All70 parent determinants are reconstructed by explicit signed-permutation arithmetic. Their numerators and denominators are coprime to the irreducible quartic, so they are nonzero at the isolated real root. All70 separately recorded rational bracket functions agree identically with this reconstruction.
- The Jacobian minor in `(a,b,c)` vanishes. The minor in `(a,c,d)` also vanishes, so the example applies to the new six-variable base as well.
- The Jacobian minor in `(a,h,i)` is nonzero, proving smoothness and that b is not critical.
- After the certified linear eliminations on the displayed rational parameter slice, the remaining a-polynomial is quadratic, its leading coefficient is nonzero, the displayed a is a double root, and the discriminant has a simple zero in h.

Thus the stated projection has a genuine uniform fold. It refutes an unconditional unbranched-projection claim. It does not refute the absence of compact components or emptiness of the height-b critical system.

## Universal conic and graph identities

The verifier builds the symmetric3-by3 conic matrix directly from the coefficients of the original second factor in `(a,c)`. Its determinant is independently expanded and multiplied by4. The result equals

`-bf(b-e)(e-f)(f-1)^2(h-1)^2(dh-d-eg+e+g-h)`.

Each of its seven factors is checked against an explicitly reconstructed signed parent bracket. Consequently this conic is nonsingular on every uniform parent cell in this named presentation; it contains no projective line.

The verifier also checks `partial_d(q1)=i` and `partial_c(q3)=-g(d-e)(h-1)`, records the actual parent-bracket identities for all their factors, and checks that q3 is affine linear in `(a,c)`. These justify the two unit graph eliminations over the entire uniform parent domain.

## Independent sparse resultant and discriminant replay

`verify_triple_reduction_independent.py` reconstructs the d graph from the coefficient equation of original q1. It obtains the original q2 quadratic and q3 linear polynomial in c after this substitution. Their three-by-three Sylvester determinant is expanded using independent multivariate polynomial arithmetic. Its primitive part agrees, up to sign, with the stored1,951-term polynomial in `(a,b,e,f,g,h,i)`.

The independent replay then computes its quadratic discriminant in a and checks the full exact identity

`Delta = [g(h-1)(b(i-f)+fg-ei)]^2 R`.

The stored R has4,186 terms and total degree18. The six proposed critical generators have term counts4186,3014,3961,3347,3616,4036, totaling22,160. These are complete symbolic equalities, not modular or sampled evaluations.

## Deductive compactness reduction

At a uniform base, the coefficients A,B,C of the a-quadratic cannot all vanish: that would put the full affine line q3=0 inside the nonsingular projective conic q2=0. Its c slope is a parent unit, so this is an actual line and not an undefined graph. Nonsingularity excludes it, even though some other points of that line might fail parent uniformity.

At a maximum of b on a hypothetical compact component, `P_a=0`; otherwise the implicit function theorem presents the zero set locally as a graph over all six base coordinates and permits increasing b within the same component and strict parent chamber. If A=0 at such a root, then B=0 and C=0 as well, which has just been excluded. Hence A is nonzero.

With `a=-B/(2A)` and Delta=0, direct differentiation gives `Delta_v=-4A P_v`. At a smooth constrained b-maximum all five derivatives with respect to e,f,g,h,i vanish by the Lagrange condition. At an intrinsic singular point they vanish by singularity. Thus this argument retains singular extrema. Since the factor removed from Delta is a parent unit, the same five derivatives of R vanish. This gives the proposed necessary critical system and the reconstruction `a=-B/(2A)` with both unit graphs.

The converse is not valid: a solution of this critical system can be a saddle or belong to a noncompact component. The audit supplies no saturation identity, real emptiness proof, roadmap, or classification of critical solutions. It also makes no claim that reducing the variable count compensates for the much larger polynomial density.

## Audit limits

The source's attribution of this named presentation to its canonical factor orbit is inherited from the pinned data, not independently re-enumerated. The64 shifted-coordinate torus experiments and573-term rational parametrization gate were not replayed in this independent audit; they are unnecessary for the accepted conic, fold, and six-variable claims. The original pair injectivity, triple escape, and ledger remain unchanged.

Replay outputs are `TRIPLE_INDEPENDENT_REPLAY.json` and `TRIPLE_REDUCTION_INDEPENDENT_REPLAY.json`.
