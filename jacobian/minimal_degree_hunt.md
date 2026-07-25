# The minimal-degree question for Keller non-automorphisms of C^3

**Date:** 2026-07-25. **Context:** the Alpöge counterexample (`alpoge_jacobian.pdf`)
F = (AB, y+3xB, 2x−3x²y−x³z), A = 1+xy, B = A²z+y²(4+3xy), det Jac = −2,
component degrees **(7,6,4)**, generic degree 3.

**Companion scripts** (sympy, exact arithmetic; all pass):
- `verify_original.py` — the (7,6,4) certificate (det Jac = −2, three-point collision).
- `verify_mechanism_lower_bound.py` — every symbolic step of Theorem B below (20 checks).
- `verify_composition_obstruction.py` — Proposition 3 below (9 checks).

Steps verified there are tagged `[V]`. Everything else is proved by hand in this
file or cited.

---

## Summary of results

1. **Minimal generic degree = 3, in every dimension ≥ 3** (Theorem A; settled,
   by citation + the companion note `n2_analysis.md`). The paper's F achieves 3.
2. **Minimal max component degree:** still **7**, achieved by the known (7,6,4)
   map. **No smaller certificate was found.** But we prove a sharp structural
   lower bound (Theorem B): *within the entire z-linear cubic-mechanism class
   that produced the counterexample — all unimodular rows (x, A), all slot
   patterns, all degenerations, up to affine postcomposition — no Keller map
   (automorphism or not) has max component degree ≤ 6.* The paper's map is
   degree-minimal in its own mechanism, with no slack.
3. **Composition reduction fails** in the searched range (Proposition 3):
   single elementary postcompositions can never reduce any component degree
   (rigorous, all degrees); affine sandwiches reduce to the precomposition case
   (rigorous); elementary precompositions in z fail rigorously for all degrees,
   and in x, y fail for deg ≤ 3 (exhaustive symbolic search).
4. In sufficiently **high dimension** the minimal max component degree is **3**
   (Yagzhev/Bass–Connell–Wright degree reduction applied to F; explicit
   witnesses in `~/finite-certificates/jacobian/deg3_map.py`,
   `verify_deg3_keller.py`). So the open content of the minimal-degree question
   is specific to n = 3: the true value lies in {3, 4, 5, 6, 7}.

---

## Theorem A. The minimal generic degree of a Keller non-automorphism is 3

Let F : C^n → C^n be a Keller map that is not an automorphism, n ≥ 3.

- **μ(F) = 1 is impossible.** A birational Keller map is étale, hence by
  Zariski's Main Theorem an open immersion; its image is then an affine open
  subset of C^n whose complement has pure codimension one (or is empty), while
  Prop. 2.1 of the paper forces codimension ≥ 2. Hence the map is surjective,
  bijective, and an automorphism (this is Keller's classical birational case;
  cf. Bass–Connell–Wright, BAMS 7 (1982)).
- **μ(F) = 2 is impossible.** A degree-2 field extension in characteristic 0 is
  Galois, and a Keller map with Galois extension C(x)/C(F) is invertible —
  L. A. Campbell, *A condition for a polynomial map to be invertible*, Math.
  Ann. 205 (1973), 243–248. A self-contained elementary proof, in the stronger
  form "no intermediate quadratic subextension", is Theorem C of the companion
  note `n2_analysis.md` (this workspace); we cite it rather than rederive.
- **μ(F) = 3 occurs**: the paper's F (its Theorem 4.2).

So the minimal generic degree is exactly 3. (Status: **proved/cited**.)

## Proposition 3. Composition cannot push (7,6,4) below max degree 7 — searched scope

Let F be the original map, top forms P₇ = x³y³z, Q₆ = 3x³y²z, R₄ = −x³z `[V]`.

1. **Affine postcomposition WLOG.** If L is affine invertible and all components
   of L∘F have degree ≤ 6, then, since the components of F are affine
   combinations of those of L∘F, all components of F would have degree ≤ 6 —
   false. The same argument applies on the target side of any composition. So
   target-affine maps never help. (**Proved.**)
2. **Single elementary postcompositions never reduce a component degree.** The
   top forms of Q^aR^b are the pairwise-distinct monomials 3^a(−1)^b
   x^{3a+3b}y^{2a}z^{a+b} `[V]`, so deg h(Q,R) = max(6a+4b) over the support of
   h, which is even — never 7, so no h(Q,R) can cancel P₇. Likewise 7a+4b = 6
   and 7a+6b = 4 have no solutions `[V]`. (**Proved**, all degrees of h.)
3. **Elementary precomposition in z never helps:** P(x,y,z+h(x,y)) = P + A³h
   `[V]`, and the top of A³h is z-free while P₇ = x³y³z: no cancellation, so
   deg ≥ 7 for h ≠ 0. (**Proved**, all degrees of h.)
4. **Elementary precompositions y → y+h(x,z), x → x+h(y,z), deg h ≤ 3:**
   exhaustive symbolic solve of "all coefficients in total degree ≥ 7 vanish";
   no solutions `[V]`. (**Exhaustively searched up to deg 3; open beyond**, as
   are longer compositions mixing pre- and postcomposition non-affinely.)

## Theorem B (main new result). The mechanism cannot do better than (7,6,4)

**Setting.** Call F = (P,Q,R) : C³ → C³ a *z-linear mechanism map* if:

- (z-lin) every component is affine-linear in z;
- (row) there is A = λ + xG(x,y), λ ∈ C^×, G ∈ C[x,y] (so (x,A) is a unimodular
  row; every unimodular row over C[x,y] containing an entry of degree ≤ 1 has
  this form after an affine change of source coordinates), normalized λ = 1;
- (cubic) there is an identity C₀x³ + C₁x²A + C₂xA² + C₃A³ ≡ 0 in C[x,y,z]
  where each C_i is affine-linear in (P,Q,R), the joint affine rank is 3
  (so the fiber cubic Φ(S,T) = C₀S³+C₁S²T+C₂ST²+C₃T³ has [x:A] as a root and
  determines the map), and **some C_i is constant** (possibly 0), the remaining
  three slots being P, Q, R up to affine postcomposition.

This is exactly the class of the paper's construction (F itself: slots
(2P, −Q, 2, −R) `[V]`) and of its Theorem 5.1 family, restricted to z-linear
members; Theorem 5.2's higher-degree families are not z-linear but have max
degree ≥ 7 anyway.

**Theorem B.** No z-linear mechanism map with det Jac ∈ C^× has
max(deg P, deg Q, deg R) ≤ 6. Consequently the paper's (7,6,4) map has minimal
max component degree in this class, and even its degree profile is rigid: the
only surviving branch is the one containing F.

**Proof.** The identity (cubic) says (C₀,C₁,C₂,C₃) is a syzygy of the regular
sequence-generated (x³, x²A, xA², A³); the syzygy module is free on the three
Koszul relations, giving exactly

  (C₀,C₁,C₂,C₃) = (f₁A, f₂A − f₁x, f₃A − f₂x, −f₃x),  f₁,f₂,f₃ ∈ C[x,y,z]. `[V]`

By the affine-WLOG argument (Prop. 3.1) we may take the three non-constant slots
to be P,Q,R on the nose. Constant slot cases:

- **C₀ or C₃ constant** ⇒ that slot is 0 (A ∤ 1, x ∤ 1), and the identity
  collapses to the binary-quadratic identity C₁x² + C₂xA + C₃A² ≡ 0, i.e.
  (P,Q,R) = (g₁A, g₂A − g₁x, −g₂x). Then det Jac is divisible by x `[V]`,
  so it is never a nonzero constant. **Dead (any degrees, any row).**
- **C₂ = 0 (zero interior slot):** forces f₂ = Ah, f₃ = xh, giving
  (P,Q,R) = (f₁A, A²h − f₁x, −x²h); again x | det Jac `[V]`. **Dead.**
  (C₁ = 0 is the mirror case under reversing the row, same conclusion.)
- **C₂ = 2 (Pattern I):** solving f₃A − f₂x = 2 gives f₂ = 2G + Aw,
  f₃ = 2 + xw, so with f₁ = u+vz, w = w₀+w₁z:
  P = f₁A, Q = (2G+Aw)A − f₁x, R = −2x − x²w.
- **C₁ = 2 (Pattern II):** f₂ = 2 + xw, f₁ = 2G + Aw, so
  P = (2G+Aw)A, Q = f₃A − (2+xw)x, R = −f₃x.

*Pattern II dies for every row with deg A ≥ 2.* det Jac's z⁰ coefficient factors
as −Ĝ₀·Ê₀ with Ĝ₀ = u₃A² + 2x²w₀A + 2x(2xG+1) `[V]`. A product of polynomials
equal to a nonzero constant forces each factor constant; but Ĝ₀ ≡ g reduced mod
A (xG ≡ −1) gives g ≡ −2x, i.e. A | g + 2x `[V]` — impossible when
deg A ≥ 2. For x-only rows: deg A = 1 normalizes to A = 1+x, and the forced
cascade (u₃ = 2−6x+x²t, w₀ = 3−tA/2, t = μy+τ(x), then v₃A/2+x²w₁ ≡ κ and the
y-Wronskian of (v₃,w₁) ≡ 0) leaves det Jac = 2κμ(κzA+1) `[V]` — never constant.
**No z-linear Keller map exists in Pattern II at all.**

*Pattern I.* det Jac = −E₀G₀ + (z¹ term) − xG₂E₂·z², with
G₀ = 2xw₀A² + 2(2xG+1)A + x²u, G₂ = 2w₁A² + xv,
E₀ = w₁L[u] − v(L′[w₀]+2), E₂ = −v²·L[w₁/v], where
L[f] = x²Gy·f_x + (1−x²G_x)f_y + xG_y·f in general; for A = 1+xy this is
L[f] = x²f_x + f_y + xf, L′[f] = x²f_x + f_y + 2xf `[V]`.

(i) *x-only rows die.* If G_y ≡ 0 the z⁰ coefficient contains the factor
(x²G′(x) − 1) `[V]`, which must be constant, forcing G′ = 0, i.e. A = 1+cx;
normalizing c = 1 the same forced cascade as above ends with
det Jac = γμ(γxz+2) `[V]` — never constant. **No Keller maps at all.**

(ii) *Rows with deg G ≥ 2 die under the degree cap.* deg A = 1+deg G ≥ 3.
deg P ≤ 6 forces deg f₁ ≤ 5−deg G ≤ 3; in Q the term A²w has degree
≥ 2+2deg G + deg w ≥ 8 unless w has degree 0 with deg G = 2 exactly (deg G ≥ 3
makes deg Q = 1+2deg G ≥ 7 unavoidable: no term can cancel the top of 2GA).
For deg G = 2, w = w₀ ∈ C: then R = −2x − w₀x² is a function of x alone, so
det Jac = R′(x)(P_yQ_z − P_zQ_y); R′ | const forces w₀ = 0, R = −2x, and each
specialization x = x₀ gives a two-variable Keller pair (y,z) ↦ (P,Q)(x₀,·,·)
of degree ≤ 6, an automorphism of C² by Moh's theorem (deg ≤ 100, J. reine
angew. Math. 340 (1983)); since R determines x₀, F is injective, hence an
automorphism (Białynicki-Birula–Rosenlicht) — **not a counterexample**, and in
fact excluded because an automorphism of this shape would still need all the
slot constraints; either way no counterexample of max degree ≤ 6.

(iii) *The main case A = 1+xy* (every row with deg A = 2 and G_y ≠ 0 normalizes
to this by an affine source change, which preserves degrees). Max degree ≤ 6 is
equivalent to the caps deg u ≤ 4, deg v ≤ 3, deg w₀ ≤ 2, deg w₁ ≤ 1 (deg P =
2+deg f₁; the top of A²w cannot cancel in Q). Then:

  1. Keller ⇒ G₀ ≡ const, and evaluation at x = 0 forces the constant = 2;
     G₀ ≡ 2 solves *linearly and exactly* to
     w₀ = −3y + xŵ, u = 8y² + 6xy³ − 2ŵA² `[V]`, and the caps force ŵ = k ∈ C.
     (Note: this already reproduces the original's u = 8y²+6xy³, w₀ = −3y.)
  2. z²-coefficient ≡ 0 ⇔ G₂ ≡ 0 or E₂ ≡ 0 (C[x,y] is a domain).
  3. **Branch G₂ ≡ 0:** xv = −2w₁A² forces w₁ = xh, v = −2hA² `[V]`, so h ≠ 0
     gives deg v ≥ 4 `[V]`, i.e. **deg P ≥ 7** — this is precisely the branch of
     the original map (h = −1: v = 2A², w₁ = −x `[V]`); h = 0 gives E₀ = 0,
     det = 0. So this branch yields nothing below 7.
  4. **Branch E₂ ≡ 0:** E₂ = −v²L[w₁/v] `[V]` and ker L on rational functions is
     {Ψ(x/A)/A} `[V]` (characteristics: L[x^aA^b] = (a+b+1)x^{a+1}A^b `[V]`;
     s = x/A is the invariant; C(s) is algebraically closed in C(x,y) since the
     level curves x−sA are irreducible). Writing Ψ = n/m with coprime binary
     forms in (x,A), the condition w₁·A·m = v·n plus deg w₁ ≤ 1 restricts n to
     {1, x, A, xA}; the cases n = x, xA force deg v ≥ 4 (excluded by caps), and
     n ∈ {1, A} give exactly v = w₁(αx+βA), which also covers v ≡ 0; the
     remaining case is w₁ ≡ 0. Both die on the z⁰ equation:
     - w₁ ≡ 0: E₀ = v(1+6xy−3kx²) `[V]` ≡ const ≠ 0 forces v ∈ C^×, then the
       xy-coefficient gives 6v = 0 — contradiction.
     - v = w₁(αx+βA): E₀ = w₁·[L(u)+(αx+βA)(1+6xy−3kx²)], so w₁ divides a
       nonzero constant, hence w₁ ∈ C^×, hence the bracket is constant; but its
       value at x = 0 is 16y + β `[V]` — contradiction.

  All branches below degree 7 are dead; Theorem B follows. ∎

**Honest scope of Theorem B.** It assumes: (a) z-linearity; (b) the cubic
incidence identity in a row (x, A) with one entry of degree ≤ 1 — rows with both
entries of degree ≥ 2 are not covered; (c) a *constant slot* — the genuinely
affine-dependent slot family (all four coefficients non-constant but affinely
dependent, "C₂ = c + αP+βQ+γR with (α,β,γ) ≠ 0") is **not** covered and is the
most interesting unsearched pocket; (d) fiber equation of degree exactly 3 in
[x:A] (degree 2 collapses to the dead quadratic family above *within this
identity format*; the general μ(F)=2 question is closed by Theorem A, and
μ(F) ≥ 4 mechanisms only raise degrees). Within (a)–(d) the exclusion is a
proof, not a search: no coefficient enumeration was truncated.

## Remark 4. Dimension vs. degree trade-off

By Bass–Connell–Wright/Yagzhev reduction, the existence of F yields Keller
non-automorphisms of **degree 3** (even cubic-homogeneous-plus-linear form) in
some larger dimension N, since the reduction preserves invertibility in both
directions. Explicit low-degree higher-dimensional witnesses derived from F are
in `~/finite-certificates/jacobian/deg3_map.py` / `verify_deg3_keller.py` (see
also `cubic_map.py`, `druzkowski_map.py`). Hence "minimal max degree over all
dimensions" is 3 (floor from Wang's theorem: degree ≤ 2 Keller maps are
automorphisms in every dimension), and the question is only open for n = 3
specifically, where the answer lies in {3,4,5,6,7}.

## Open leads (ranked)

1. **Affine-dependent slots** (scope gap (c)): same syzygy parametrization, one
   extra linear relation with parameters; the staged determinant factorization
   should still be computable. This is the most promising place a (6,·,·) or
   smaller certificate could hide — or the next lower-bound extension.
2. **Non-z-linear maps of low degree**: det Jac is then cubic in z; a staged
   analysis like Theorem B's is harder but the z-top-degree coefficient again
   factors. A z-quadratic hunt at max degree ≤ 5 seems computationally feasible.
3. **Rows (u,v) with both degrees ≥ 2** (e.g. (x², 1+x²y)): not obviously
   normalizable away; the syzygy parametrization generalizes verbatim.
4. **Longer compositions**: elementary-post ∘ F ∘ elementary-pre with both
   nontrivial, and precompositions of degree ≥ 4, were not searched.
5. Conjecture (based on all of the above): **no Keller non-automorphism of C³
   has max component degree ≤ 4**; a proof for the z-linear class via the
   z-coefficient determinant identities (without the mechanism assumption)
   looks within reach and would be a publishable note.
