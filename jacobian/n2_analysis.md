# The n = 2 case after Alpöge: transfer analysis, a no-go theorem for the mechanism, and the impossibility of generic degree 2

**Date:** 2026-07-25.
**Companion script:** `verify_n2.py` (sympy; all checks pass). Every symbolically
checkable identity below is verified there; each such point is tagged `[V]`.

Throughout, a *Keller map* is a polynomial map with constant nonzero Jacobian
determinant, and for a dominant polynomial map `F : C^n -> C^n` the *generic degree*
is `mu(F) = [C(x_1,...,x_n) : C(F_1,...,F_n)]`. `S_F` denotes Jelonek's
nonproperness set. We freely use, from the Alpöge paper (`alpoge_jacobian.pdf`):

* Keller maps are étale (everywhere local biholomorphisms), their image is Zariski
  open dense with complement of codimension >= 2, and `C^n \ F(C^n) ⊆ S_F`
  (Prop. 2.1 there).
* A Keller map is a polynomial automorphism iff it is proper iff `S_F = ∅` iff
  `codim S_F >= 2` (Thm. 2.2 there). By Jelonek, `S_F` is empty or a hypersurface.
* The n = 3 counterexample `F = (AB, y + 3xB, 2x - 3x^2y - x^3z)`,
  `A = 1 + xy`, `B = A^2 z + y^2(4 + 3xy)`: `det Jac F = -2` `[V]`, the three points
  `(0,0,-1/4), (1,-3/2,13/2), (-1,3/2,13/2)` share the image `(-1/4,0,0)` `[V]`,
  `mu(F) = 3` with `C(x,y,z) = C(p,q,r)(s)`, `s = x/A`, satisfying
  `2ps^3 - qs^2 + 2s - r = 0` `[V]`.

## 0. Known constraints on n = 2 (verified citations)

The n = 2 case remains open (stated explicitly in the paper). Any attack must
respect:

* **Moh (1983)**, *On the Jacobian conjecture and the configurations of roots*,
  J. reine angew. Math. **340**, 140–212: no n = 2 counterexample of (total) degree
  <= 100. So coefficient searches in low degree are provably empty.
* **Magnus (1955)**, Math. Scand. **3**, 255–260, and **Nakai–Baba (1977)**,
  *A generalization of Magnus' theorem*, Osaka J. Math. **14**, 403–409: JC_2 holds
  when gcd(deg p, deg q) = 1 (Magnus) or is prime (Nakai–Baba); see also
  **Appelgate–Onishi (1985)**, J. Pure Appl. Algebra **37**, 215–227. Underlying
  these: **Abhyankar–Moh (1975)**, *Embeddings of the line in the plane*, J. reine
  angew. Math. **276**, 148–166.
* **Orevkov (1986)**, *On three-sheeted polynomial mappings of C^2*, Izv. Akad. Nauk
  SSSR **50**(6), 1231–1241: no n = 2 counterexample with `mu = 3`.
  **Domrina–Orevkov (1998)**, Mat. Zametki **64**(6), 847–862, and **Domrina
  (2000)**, Izv. RAN **64**(1), 3–36: none with `mu = 4`.
* **Campbell (1973)**, *A condition for a polynomial map to be invertible*, Math.
  Ann. **205**, 243–248: a Keller map (any n) whose field extension
  `C(x)/C(F)` is **Galois** is invertible.

Theorem C below re-proves, self-contained and elementarily, the quadratic piece of
Campbell's theorem — in a slightly stronger form (no quadratic *subextension*), and
in all dimensions.

---

## 1. Baby no-go: the mechanism does not transfer to n = 2

In n = 3 the counterexample spends the variable `z` affine-linearly: all three
components are affine in `z` `[V]`, with `z`-coefficient row `(A^3, 3xA^2, -x^3)`
`[V]` built from the unimodular row `(x, A)` over `C[x,y]` (`(-y)·x + 1·A = 1`
`[V]`). The direct analogue in n = 2 spends `y` affine-linearly over `C[x]`.

**Proposition A (y-affine Keller maps are automorphisms).**
Let `F = (p, q) : C^2 -> C^2` with `p = a(x)y + b(x)`, `q = c(x)y + d(x)`,
`a, b, c, d ∈ C[x]`, and suppose `det Jac F = λ ∈ C*`. Then `F` is a polynomial
automorphism, and it is affine-triangular: up to the swap `(p,q) -> (q,p)`
and constants, `q = c_0 y + d(x)` and `p = μ q + e_1 x + e_0` with
`c_0 e_1 = λ ≠ 0`, `μ ∈ C`.

*Proof.* Direct computation gives the exact identity `[V]`

    det Jac F = (a'c - ac')·y + (b'c - a d').

Constancy in `y` forces the Wronskian `W(a,c) = a'c - ac'` to vanish and
`b'c - a d' = λ`.

*Case `c = 0`.* Then `a d' = -λ`, a product of polynomials equal to a nonzero
constant, so `a = a_0 ∈ C*` and `d' = d_1 = -λ/a_0 ∈ C*`, i.e.
`F = (a_0 y + b(x), d_1 x + d_0)`. Explicit inverse:
`x = (q - d_0)/d_1`, `y = (p - b((q-d_0)/d_1))/a_0` `[V]`.

*Case `c ≠ 0`.* On the open set `c ≠ 0`, `(a/c)' = W(a,c)/c^2 = 0` `[V]`, and in
characteristic zero a rational function with zero derivative is a constant; since
`a = (a/c)·c` is polynomial, `a = μc` with `μ ∈ C` (the subcase `a = 0` is `μ = 0`).
Substituting, `λ = b'c - μ c d' = c·(b' - μ d')`: again a product of polynomials
equal to a nonzero constant, so `c = c_0 ∈ C*` and `b' - μ d' = e_1 := λ/c_0 ∈ C*`,
whence `b = μ d + e_1 x + e_0`. Therefore

    q = c_0 y + d(x),      p = μ q + e_1 x + e_0,

with explicit inverse `x = (p - μq - e_0)/e_1`, `y = (q - d(x))/c_0` `[V]`. ∎

So **the n = 3 mechanism class is empty of counterexamples in n = 2**: every Keller
map that is affine-linear in one variable over the polynomial ring in the other is
an automorphism. This is sharp in the sense that the n = 3 counterexample lies in
the exactly analogous class one dimension up.

## 2. Why the incidence-variety trick dies: the row degenerates

**Proposition B (row rigidity over a 1-dimensional base).**
In the setting of Proposition A, the coefficient row `(a, c) ∈ C[x]^2` of the fiber
variable is a *constant* vector (both entries in `C`, not both 0); in particular the
induced map `[a : c] : C -> P^1` is constant.

*Proof.* Immediate from the case analysis above: either (`c = 0`, `a ∈ C*`) or
(`c = c_0 ∈ C*`, `a = μ c_0 ∈ C`). ∎

Contrast with n = 3: there the `z`-coefficient row `(A^3, 3xA^2, -x^3)` `[V]` is
projectively nonconstant — it is the third Veronese image of the unimodular row
`(x, A)`, and the induced nonconstant projective coordinate `[x : A] : C^2 -> P^1`
is precisely what identifies `C^3` with the simple-root locus of the binary cubic
`Φ_{p,q,r}` and creates the degree-3 extension `C(p,q,r)(s)`.

Two structural remarks make the obstruction precise.

1. *Unimodular rows over `C[x]` are plentiful but useless here.* A row
   `(f, g) ∈ C[x]^2` is unimodular iff `gcd(f,g) = 1`, and every length-2
   unimodular row over any commutative ring completes to `SL_2` via
   `uf + vg = 1 ↦ [[f, g], [-v, u]]`. Existence is not the issue. The issue is
   Proposition B: the Keller condition over the base `C[x]` forces the row that
   multiplies the fiber variable to be *constant*, so the fiberwise-affine map
   cannot twist along the base, the incidence variety degenerates to a product,
   and the generic degree of any map in the mechanism class is 1.
2. *Dimension count.* In the n = 3 construction, the base `C[x,y]` of the
   `z`-fibration is 2-dimensional: there is room for a nonconstant map base -> P^1
   compatible with a constant Jacobian, because the Wronskian-type constraint is a
   single equation on a 2-dimensional family of directions. Over the 1-dimensional
   base `C[x]` the same constraint `W(a,c) = 0` is equivalent to projective
   constancy. Any n = 2 counterexample must therefore create its field extension
   `C(x,y)/C(p,q)` of degree `d = mu(F) >= 2` *without* a linear fiber variable —
   both components must be genuinely nonlinear in both variables.

## 3. Generic degree 2: the deck involution σ

Suppose (for this section) `F = (p,q) : C^2 -> C^2` is a Keller map with
`mu(F) = 2`, `K = C(p,q) ⊂ L = C(x,y)`. Since char = 0, a degree-2 extension is
Galois; let `σ` be the nontrivial element of `Gal(L/K)`, a birational involution of
`C^2` with `F ∘ σ = F` as rational maps. Write `ω = dx ∧ dy`. These lemmas hold as
stated (they will become vacuous after Theorem C, but they chart the route and the
last one is the germ of the proof).

**Lemma D1 (covering structure).** If `F` is not an automorphism then `S_F` is a
nonempty curve, `D := F^{-1}(S_F)` is a nonempty curve, and
`F : C^2 \ D -> C^2 \ S_F` is a proper étale surjection, hence a (connected,
2-sheeted) covering map; `σ` is regular on `C^2 \ D` and implements the sheet
swap.
*Proof sketch.* `S_F ≠ ∅` and is a hypersurface by Thm. 2.2/Jelonek; local
properness off `S_F` globalizes to properness over `U = C^2 \ S_F`; surjectivity
since the unattained set lies in `S_F` (Prop. 2.1); a proper étale map is a finite
covering, of constant sheet number = generic fiber count = 2 over the connected set
`U`. If `D = F^{-1}(S_F)` were empty, the nonempty hypersurface `S_F` would be
entirely unattained, i.e. `S_F ⊆ C^2 \ F(C^2)`, which has codimension >= 2
(Prop. 2.1) — impossible. `C^2 \ D` is connected (complement of a curve), so the
2-sheeted covering is normal with deck group `Z/2`. The sheet swap
`u ↦ (the other point of F^{-1}(F(u)))` is holomorphic (compose local inverse
branches of `F`), commutes with `F`, and induces a nontrivial `K`-automorphism of
`L`, which must be `σ`; so `σ` agrees with it and is regular on `C^2 \ D`. ∎

**Lemma D2 (σ preserves the volume form exactly).** On the locus where `σ` is
regular, `σ*ω = ω` (not merely up to sign).
*Proof.* `σ*(F*(dp∧dq)) = (F∘σ)*(dp∧dq) = F*(dp∧dq)`, and
`F*(dp∧dq) = (det Jac F)·ω = λω` with `λ ∈ C*` constant. Cancel `λ`. `[V]`
(the underlying chain-rule identity `(det Jσ)(det JF ∘ σ) = det JF` is checked on
the model double cover `F = (x, y^2)`, `σ = (x, -y)`). ∎

**Lemma D3 (σ is fixed-point-free wherever regular).** There is no `z_0 ∈ C^2`
with `σ` regular at `z_0` and `σ(z_0) = z_0`.
*Proof.* `F` is a biholomorphism of a neighborhood `V` of `z_0` onto its image
(étale). Shrink to `W ⊆ V` with `σ(W) ⊆ V`; for `u ∈ W`, `F(σ(u)) = F(u)` with
both `σ(u), u ∈ V`, so injectivity of `F|_V` gives `σ(u) = u` on `W`, hence
`σ = id` as a rational map — contradicting `σ ≠ id`. ∎

**Lemma D4 (σ is not a polynomial automorphism).** If `σ ∈ Aut(C^2)`, then (finite
subgroups of `Aut(C^2)` being linearizable, or directly: every finite-order
polynomial automorphism of `C^2` is conjugate to a linear one) `σ` would be
conjugate to a linear involution of `C^2`, and every affine/linear involution of
`C^2` has a fixed point — contradicting Lemma D3. So `σ` has genuine poles or
indeterminacy, necessarily along `D` (by D1 it is regular off `D`).

**Lemma D5 (the second sheet escapes to infinity along D).** Viewing
`σ : C^2 ⇢ P^2`, every point of `D` at which `σ` is defined is mapped into the
line at infinity. Equivalently: `σ` cannot be extended holomorphically across any
point of `D` with value in `C^2`.
*Proof.* Suppose `σ` is regular at `z_0 ∈ D` with `w = σ(z_0) ∈ C^2`; then
`F(w) = F(z_0) =: s ∈ S_F`. If `w = z_0` this contradicts D3. If `w ≠ z_0`,
choose disjoint bounded neighborhoods of `z_0` and `w`, each mapped
biholomorphically by `F` onto a common ball `V ∋ s`. Every `s' ∈ V` then has one
preimage in each neighborhood, so `#F^{-1}(s') >= 2`; and `#F^{-1}(s') <= mu = 2`
always (were there 3 points in a fiber, disjoint étale neighborhoods would give
nearby fibers >= 3 points, exceeding the generic count). Hence *every* fiber over
`V` consists of exactly one point in each of the two bounded neighborhoods, so
`F^{-1}(V)` is bounded and `F` is proper over `V` — contradicting `s ∈ S_F`. ∎

**Scoping example (the soft constraints do not self-destruct).** The birational
involution `σ(x, y) = (-x, 1/x^2 - y)` of `C^2` satisfies `σ∘σ = id` `[V]`,
`σ*ω = ω` (Jacobian determinant `+1`) `[V]`, is regular exactly off the line
`x = 0`, has no fixed points where regular `[V]`, and maps `{x = 0}` to the point
`[0:1:0]` at infinity. So Lemmas D2, D3, D5 describe a nonempty class of
involutions: no contradiction follows from them alone, and likewise the
Bertini/Bayle–Beauville classification of birational involutions of the plane
(all fixed curves of our `σ` would be forced into the boundary/exceptional locus,
hence rational, making `σ` conjugate to a linear involution) stalls at exactly
this point: conjugacy to a linear involution is *consistent* with D2–D5. The
contradiction has to come from the interplay with the *polynomial* structure of
the source. That is Theorem C.

## 4. Main result: no Keller map has generic degree 2 — in any dimension

**Theorem C.** Let `F : C^n -> C^n` (`n >= 1`) be a Keller map. Then the field
extension `L = C(x_1,...,x_n)` over `K = C(F_1,...,F_n)` contains **no**
intermediate field `K'` with `[K' : K] = 2`. In particular `mu(F) = 2` is
impossible.

*Proof.* Suppose `K ⊆ K' ⊆ L` with `[K' : K] = 2`. In characteristic zero,
`K' = K(t_0)` with `t_0^2 ∈ K`.

**Step 1 (normalize the radicand).** Write `t_0^2 = u/v` with `u, v ∈ C[p_1,...,p_n]`.
Then `(t_0 v)^2 = uv`; since `C[p]` is a UFD, write `uv = h·m^2` with `h ∈ C[p]`
squarefree, and set `t = t_0 v / m ∈ L`. Then

    t^2 = h,   h ∈ C[p] squarefree,   K' = K(t).

If `h` were constant, `t` would be a constant, so `K' = K`, contradicting
`[K':K] = 2`. So `h ∉ C`, and likewise `t ∉ C`.

**Step 2 (hidden properness: t is a polynomial).** `t` satisfies the monic equation
`t^2 - h = 0` over `C[p] ⊆ C[x]`, so `t` is integral over `C[x]`. But `C[x_1,...,x_n]`
is a UFD, hence integrally closed in its fraction field `L`, and `t ∈ L`. Therefore

    t ∈ C[x_1, ..., x_n]   and   t^2 = h ∘ F   holds as a polynomial identity.

(This is the step that neutralizes nonproperness: whatever escapes to infinity,
`t` itself is globally regular on the source.)

**Step 3 (a component of Z(t)).** Since `t ∉ C`, the weak Nullstellensatz gives
`Z(t) ≠ ∅`, and Krull's Hauptidealsatz gives that `Z(t) ⊆ C^n` is of pure
codimension 1: a nonempty hypersurface. Let `Γ` be an irreducible component, with
divisorial valuation `v_Γ` (the order of vanishing along `Γ`, i.e. the valuation of
the DVR `O_{C^n, ξ_Γ}` at the generic point). Since `dF` is everywhere invertible,
`F` has discrete (hence finite) fibers, so dimension is preserved:
`dim overline{F(Γ)} = dim Γ = n - 1`; and `h(F(z)) = t(z)^2 = 0` for `z ∈ Γ`, so
`Δ := overline{F(Γ)}` is an irreducible component of the hypersurface `Z(h)`.
Moreover, because `h` is squarefree, `Z(h)` is a *reduced* hypersurface, so
`Sing(Z(h))` has dimension <= n - 2; since `dim Δ = n - 1`, `Δ` cannot be contained
in the singular locus. Hence the generic point `ξ_Δ` is a smooth point of `Z(h)`
lying on the single component `Δ`, and `O_{C^n, ξ_Δ}` is a DVR in which `h` is a
uniformizer, i.e. `v_Δ(h) = 1`.

**Step 4 (étale parity contradiction).** `F` maps the generic point `ξ_Γ` to
`ξ_Δ` and, being étale (Keller), induces an *unramified* local homomorphism of
DVRs `O_{C^n, ξ_Δ} -> O_{C^n, ξ_Γ}` (both are DVRs by Step 3 and by regularity of
`O_{C^n, ξ_Γ}` at the codimension-1 point `ξ_Γ`): the maximal ideal of the source
generates the maximal ideal of the target, so a uniformizer pulls back to a
uniformizer and `v_Γ(g ∘ F) = v_Δ(g)` for any `g` in the lower ring. By Step 3,
`v_Δ(h) = 1`, hence `v_Γ(h ∘ F) = 1`. But

    v_Γ(h ∘ F) = v_Γ(t^2) = 2·v_Γ(t) >= 2,

since `t` vanishes along `Γ`. So `1 >= 2` — contradiction. ∎

(Concretely, Step 4 says: an étale map pulls reduced divisors back to reduced
divisors, while `t^2 = h∘F` forces the pullback of `Z(h)` to be everywhere
non-reduced unless `Z(t) = ∅`, which Step 3 rules out. The model `F = (x, y^2)`,
where `h = q`, `t = y`, shows all the moving parts and shows why non-Keller maps
escape: there `Z(det Jac F) = Z(t)` exactly — étaleness fails precisely on
`div(t)` `[V]`.)

**Remarks on novelty and consistency.**
* Degree 2 is automatically Galois, so the `mu = 2` case of Theorem C is a special
  case of Campbell (1973). The subextension form appears mildly stronger (it also
  constrains composite maps, see Corollary C2 below) and the proof above is
  elementary (no Galois theory, no covering spaces: UFD + étale). We make no
  priority claim; this is offered as an easily verifiable proof.
* Consistency check against the counterexample: the n = 3 map has `mu = 3` — odd,
  so `L/K` has no quadratic subextension, and its Galois closure has group `S_3`
  (it cannot be `C_3`: that would be Galois, contradicting Campbell). Theorem C is
  sharp: `mu = 3` **is** achieved in n = 3, and the paper's Theorem 5.2/Cor. 5.3
  achieves every `mu = d >= 3` in n = 3. So no "soft" argument of the above kind
  can be dimension-independent for `mu >= 3`; anything killing `mu = 3` in n = 2
  must genuinely use n = 2 (as Orevkov's proof does).

**Corollary C1 (state of the n = 2 problem).** Any n = 2 counterexample to the
Jacobian conjecture has generic degree `mu >= 5` (Theorem C for `mu = 2`; Orevkov
1986 for `mu = 3`; Domrina–Orevkov 1998/2000 for `mu = 4`) and total degree
`> 100` (Moh 1983), with `gcd(deg p, deg q)` neither 1 nor prime (Magnus,
Nakai–Baba). Moreover it is affine-linear in no variable over the other
(Proposition A), and both `S_F` and `F^{-1}(S_F)` are nonempty curves with the
covering structure of Lemma D1 in degree `mu`.

**Corollary C2 (Galois-closure constraint for mu = 4, any n).** If `mu(F) = 4`,
the Galois group of the Galois closure of `L/K`, as a permutation group on the 4
sheets, is `S_4` or `A_4`. Indeed, the transitive subgroups of `S_4` are `S_4`,
`A_4`, `D_4`, `V_4`, `C_4`, and the last three are eliminated as follows. For
`D_4` acting on the 4 sheets, the point stabilizer `H` has order 2 (a reflection);
`H` is not contained in the rotation subgroup `C_4`, but it *is* contained in one
of the two `V_4` index-2 subgroups of `D_4`, and the chain `H ⊂ V_4 ⊂ D_4`
corresponds, under the Galois correspondence inside the Galois closure, to an
intermediate field `K ⊂ K' ⊂ L` with `[K' : K] = [D_4 : V_4] = 2` — contradicting
Theorem C. For `C_4` and `V_4` the action is regular, so `H` is trivial and sits
inside an index-2 subgroup (both groups have one), producing the same forbidden
quadratic subextension; these two cases are moreover Galois (`H = 1`), so they
also fall to Campbell. Only `S_4` and `A_4` survive: `A_4` has no index-2
subgroup, and the sole index-2 subgroup `A_4` of `S_4` does not contain the point
stabilizer `S_3`. This is vacuous for n = 2 by Domrina–Orevkov but is, to
our knowledge, a live constraint for n >= 3 nonproper Keller maps of degree 4 —
e.g. the paper's degree-4 family (Theorem 5.2, `d = 4`) must have Galois closure
`S_4` or `A_4`.

## 5. Honest gaps

1. **`mu = 3` in n = 2 not re-proved.** Our methods do not recover Orevkov's
   theorem. The obstruction is fundamental (see the consistency remark): étale
   parity kills only even ramification patterns. For `mu = 3`, the normalization
   `W` of `C^n` in `L` gives a finite triple cover `π : W -> C^n` and a birational
   morphism `G : C^n -> W` with `F = π ∘ G`; purity forces `π` to ramify along a
   divisor, and étaleness of `F` forces `G(C^n)` to *miss* the smooth ramification
   locus of `π`. Unlike Step 2–4, this is not a contradiction: a birational
   morphism from `C^n` can miss a divisor (model: `(x, y) ↦ (x, xy)` misses
   `{x = 0, y ≠ 0}`). Classifying which divisors a birational morphism `C^2 -> W`
   can miss, versus which curves can carry the ramification of a triple cover with
   rational total space, is exactly where the difficulty concentrates; this is the
   natural next question, and it is where the n = 3 example lives on the other
   side of the wall.
2. **General Galois case.** We did not re-prove Campbell's full theorem; for
   `Gal = Z/2` our proof is complete, and the general case is cited, not redone.
3. **Birational-involution classification route abandoned (with reason).** The
   chain D1–D5 plus Bayle–Beauville ("all fixed curves rational ⇒ conjugate to a
   linear involution") does not close: the scoping example in §3 satisfies every
   soft constraint. We therefore did not complete or rely on the classification
   argument; it is recorded because the fixed-point-freeness (D3) and exact
   volume-preservation (D2) statements are correct, cheap, and reusable.
4. **Lemma D4's linearization input** (finite subgroups of `Aut(C^2)` are
   linearizable) is quoted, not proved; D4 is not used by Theorem C.
5. **No jackpot.** We found no candidate n = 2 counterexample; Proposition A/B
   shows the new mechanism cannot produce one, and Corollary C1 quantifies how far
   away any counterexample must live (`mu >= 5`, degree > 100).

## 6. Summary

* **Strongest new statement (fully proved here, sympy-verified where symbolic):**
  Theorem C — the function-field extension of a Keller map `C^n -> C^n` admits no
  quadratic subextension; in particular **no Keller map in any dimension has
  generic degree 2**, so every counterexample to JC (in any dimension, including
  the open n = 2 case) has `mu >= 3`, sharply attained by the new n = 3 example.
* **Mechanism no-go (Propositions A, B):** the affine-in-one-variable mechanism
  that disproved JC_3 is provably empty in n = 2: the Keller condition forces the
  fiber-coefficient row over `C[x]` to be projectively constant and every such map
  is an explicit affine-triangular automorphism.
* Combined with the verified literature: any n = 2 counterexample has
  `mu(F) >= 5` and `deg F > 100`.
