# Attack: Conjecture 6.6, "Maxout Polytopes" (arXiv:2509.21286)

Balakin, Cox, Loho, Sturmfels, *Maxout Polytopes*, arXiv:2509.21286 (Sep 2025), Section 6.

## Exact statement (as quoted from the paper)

A **(d,n)-zonoboxtope** (= (d,n,1)-maxout polytope) is
`conv( sum_{i=1..n} a_i I_i  u  sum_{i=1..n} b_i I_i ) subset R^d`,
where the I_i are line segments and a_i, b_i >= 0 — i.e. the convex hull of two zonotopes with
parallel (proportionally scaled) corresponding generators. Translated segments are explicitly
*excluded* (the paper's formula (6) variant is a different family).

> **Conjecture 6.6.**
> 1. The maximal number of vertices of a (3,n,1)-maxout polytope equals 4*sum_{k=0}^{2} C(n-1,k)
>    if n is odd, and 4*sum_{k=0}^{2} C(n-1,k) - (n-2) if n is even.
> 2. For 4 <= d <= n, the maximal number of vertices of a (d,n,1)-maxout polytope equals
>    4*sum_{k=0}^{d-1} C(n-1,k).
> 3. (general (d,n,m) formula, not attacked here.)

Paper's evidence: d=2 proven (Thm 6.1); d=3, n=3..6 upper bounds via DFS over combinatorial types,
tightness via ~1000 random samples per n (Prop 6.5: 16, 26, 44, 60). **No computational evidence for
any d >= 4** and none for d=3, n >= 7.

Key structural fact used throughout: every vertex of conv(A u B) is a vertex of A or of B, and a
centered zonotope with n generators in R^d has at most 2*sum_{k=0}^{d-1} C(n-1,k) vertices, so
4*sum_{k=0}^{d-1} C(n-1,k) is an *absolute cap*. Hence part 2 (and the odd case of part 1) are pure
**achievability** claims — resolvable by an explicit instance; the even case of part 1 claims a
mandatory deficit of n-2 — **refutable** by an explicit instance beating the formula.

## Formalization check (guards against attacking a misreading)

We model instances as I_i = [-v_i, v_i] (centered segments; legitimate line segments under any
reading of the definition), a = 1, b = lam >= 0, so P = conv(Z(v) u Z(lam*v)), candidate vertex set
= the 2^(n+1) sign points. Sanity check (search_maxout66.py sanity): hill-climbing in this family at
d=3 reproduces the paper's maxima exactly — reaches 16 (n=3), 26 (n=4), 60 (n=6), 42/44 (n=5,
search-budget shortfall) and **never exceeds** their DFS-proven bounds 16/26/44/60. This validates
the formalization in both directions.

## Result 1 — CONFIRMED: smallest open case of part 2, (d,n) = (4,4)

Claim resolved affirmatively: there is a (4,4)-zonoboxtope with **32 = 4*sum_{k=0}^{3} C(3,k)**
vertices (the cap, = conjectured maximum).

- Found by randomized hill-climbing on (v_i, lam_i) (found at first restart — the property appears
  to hold generically in a large region, which itself supports part 2).
- Instance rationalized to denominators <= 20; all 32 sign points certified as vertices by explicit
  rational witness directions c_p with c_p . p > c_p . q for all other candidate points q,
  verified in exact Fraction arithmetic (no floats anywhere in the verified chain).
- Certificate: `cert_d4n4.json` (generators V, scalings lam, 32 witness directions).
- Verifier: `verify_maxout66_d4n4.py` — standalone, exact, prints PASS, exit 0 (nonzero on FAIL).
  **Status: PASS.**

Honesty note: this **confirms** (does not prove in general) part 2 at its smallest instance — the
conjectured value is attained; the matching upper bound at (4,4) is the trivial cap, so the case
(d,n)=(4,4) of Conjecture 6.6(2) is fully **resolved** (max = 32), assuming only the standard facts
stated above (vertices of conv(A u B) come from vert(A) u vert(B); zonotope vertex cap
2*sum C(n-1,k), which for n=d=4 is just |{-1,1}^4| = 16 — so here the cap argument is elementary
and complete: 32 candidate points, all 32 are vertices).

## Result 2 — attempted REFUTATION: part 1 even case, (d,n) = (3,8)

Conjectured max = 4*(1+7+21) - 6 = **110**; cap = 116. A config with >= 112 (counts are even by
central symmetry) would refute part 1.

**Outcome: no refutation, and no meaningful negative evidence either.** Randomized hill-climbing
(two search designs: random init, and golden-spiral init with alternating scalings; ~15 min total
CPU) reached only **92** vertices at n=8 — well below even the conjectured achievable value 110.
Likewise at n=7 (odd case, conjectured max = cap = 88, previously unverified) search reached only
**84/88**. Interpretation: local search degrades sharply beyond n=6 (the paper's own sampling
stopped there, plausibly for the same reason); extremal configurations at n >= 7 appear to require
structured constructions (the paper hints at Lemma 6.2 / Theorem 6.1-style alternating-angle
families). Nothing here bears on the truth of part 1 at n=8 in either direction.

## Search-quality caveat

The float vertex counter (unique argmax over ~12k-40k random directions) *undercounts* vertices with
tiny normal cones, so hill-climbing is biased against near-degenerate extremal configs. A future
attack should (a) use exact or adaptive direction sampling, (b) seed from the paper's Lemma 6.2
construction, (c) exploit the conjectured combinatorial structure (all-but-(n-2) sign points
extreme) to set up a constraint system per candidate sign-pattern instead of blind search.
