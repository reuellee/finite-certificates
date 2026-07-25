# Fallout harvest: consequences of the Jacobian Conjecture counterexample

**Date:** 2026-07-25 (5 days after the 2026-07-20 announcement).
**Base object:** the Alpöge map `F = (AB, y+3xB, 2x−3x²y−x³z)`, `A = 1+xy`,
`B = A²z + y²(4+3xy)`: a Keller map `C³ → C³` with `det Jac F ≡ −2` and the three
rational points `(0,0,−1/4)`, `(1,−3/2,13/2)`, `(−1,3/2,13/2)` sharing the image
`(−1/4,0,0)` (verified: `verify_base.py`). Normalized form `F̃ = (R/2, Q, P)`:
`det ≡ 1`, `F̃(0)=0`, `Jac F̃(0)=I` (paper Cor. 3.2; verified). All data rational,
so everything below works over any field of characteristic 0.

**Honesty conventions.** Every claim is labeled:
- **[V]** verified here in exact arithmetic by a `verify_*.py` script (all print PASS);
- **[C]** relies on a cited published theorem/lemma (statement and direction given);
- **[A]** abstract corollary of an implication chain, no explicit witness constructed.

Status vocabulary: **REFUTED-W** (refuted with explicit verified witness),
**REFUTED-A** (refuted abstractly via implication chain), **BLOCKED** (a proof
route died, statement itself not decided), **UNAFFECTED**, **UNCHANGED** (was
already false before 2026).

---

## 1. Summary table

| # | Conjecture / formulation | Status | Witness (this work) | Key implication + citation | Scooped? (as of 07-25 scan) |
|---|---|---|---|---|---|
| 1 | Jacobian Conjecture, `n ≥ 3` | REFUTED-W | re-verified base map [V] | — (Alpöge 2026-07-20) | announced; verification paper exists |
| 2 | JC for Keller maps of degree ≤ 3 (Bass–Connell–Wright deg-3 form) | REFUTED-W | dim **27**, `G = X+H₂+H₃`, det ≡ 1, 3-point rational collision [V] | BCW 1982 Prop. (3.1) (witness-preserving stable equivalence) [C] | not seen explicitly; subsumed by #3 claims |
| 3 | JC for cubic-homogeneous maps `X + N`, `J(N)` nilpotent (Yagzhev/BCW form) | REFUTED-W | dim **55**, `L = X+N'`, cubic homogeneous, `J(N')` nilpotent, det ≡ 1, 3-point rational collision [V] | BCW 1982 Thm. (2.1) Steps 2–3 (witness-preserving) [C] | **yes**: 24-var example, W. Thompson (GitHub/Zenodo, not arXiv), collision pair, `(JN)¹⁷=0` |
| 4 | JC for Drużkowski (cubic-linear) maps `y + (Cy)^{*3}` | REFUTED-W | dim **368**, explicit rational matrix `C`, 3-point rational collision [V] | Drużkowski 1983 / Gorni–Zampieri pairing; here a self-certifying Sylvester-identity variant [C] | **no claim found — apparently first** |
| 5 | Dixmier conjecture `DC_n`, `n ≥ 3` | REFUTED-W (non-automorphy step [C]) | explicit endomorphism `φ` of `A₃`: `x_i ↦ F̃_i`, `∂_i ↦ Σ_j W_ij ∂_j`, `W = (JF̃ᵀ)⁻¹`; all Weyl relations verified [V] | classical `DC_n ⟹ JC_n` (see §5); contrapositive refutes `DC_3`; stabilization for `n>3` [C] | **partially**: same-construction informal note (wmayner, GitHub, not arXiv); no Poisson treatment there |
| 6 | Poisson conjecture `PC_3` (Adjamagbo–van den Essen 2007) | REFUTED-W (self-contained) | bracket-preserving endomorphism of `(C[x₁..x₃,ξ₁..ξ₃], canonical bracket)`, non-injective on `C⁶`: 3 distinct points, one image [V] | direct: a non-injective variety map cannot come from an algebra automorphism (no cited theorem needed) | **no claim found — apparently first** |
| 7 | Kontsevich conjecture `Aut(A_n) ≅ Aut(P_n)` (Belov-Kanel–Kontsevich 2005) | UNAFFECTED (directly) | — | statement is about automorphism *groups*, not endomorphisms; our witnesses do not decide it | — |
| 8 | Mathieu conjecture (1997, G-finite functions on compact connected Lie groups) | REFUTED-A (nonabelian case) | none (reduction not traced here) | Mathieu 1997: Mathieu conj. ⟹ JC (all n); JC false ⟹ Mathieu false for some nonabelian `G` (abelian case is a *theorem*, Duistermaat–van der Kallen 1998) [C] | **yes**: two arXiv preprints in window claim refutation for SU(2) (arXiv:2607.19012) and SU(3) |
| 9 | Zhao Vanishing Conjecture (quartic Hessian-nilpotent `P`, `Δ^m P^m = 0` for `m ≫ 0`) | REFUTED-A | none yet (see §8: naive symmetrization provably fails [V-negative]) | Zhao 2007 (TAMS 359): JC ⟺ VC; JC false ⟹ VC false [C] | abstract "VC is false" notes claimed; no explicit Hessian-nilpotent witness seen |
| 10 | Zhao Image Conjecture / Mathieu-subspace program (IC ⟹ JC instances) | REFUTED-A | none | Zhao 2010: IC (for relevant commuting differential operators) ⟹ JC; contrapositive kills those IC instances [C] | abstract notes claimed |
| 11 | Markus–Yamabe (polynomial, `n ≥ 3`) | UNCHANGED (false since 1997) | — | Cima–van den Essen–Gasull–Hubbers–Mañosas 1997 | — |
| 12 | "Every Keller map is proper" formulation | REFUTED-W | — (handled in the Alpöge paper itself: `S_F = V(Δ)` hypersurface) | paper Thm. 2.2/4.3 | in the base paper |
| 13 | `JC_2`, `DC_1`, `DC_2` | OPEN / routes BLOCKED | — | `JC_{2n} ⟹ DC_n` (Tsuchimoto 2005; Belov-Kanel–Kontsevich 2007) now has false antecedent for `2n ≥ 4`: proof route to `DC_2` via `JC_4` is dead; nothing refuted | n=2 impossibility analysis in companion `n2_analysis.md` |

---

## 2. Witness 1: degree ≤ 3 Keller non-automorphism (dim 27) — `verify_deg3_keller.py`

**Statement.** An explicit `G = X + H₂ + H₃ : C²⁷ → C²⁷`, every component of total
degree ≤ 3, `G(0)=0`, `Jac G(0)=I`, `det Jac G ≡ 1`, with three distinct rational
points sharing one image. Hence a Keller map in the BCW degree-reduced class that
is not injective, so not an automorphism.

**Provenance.** Mechanical implementation of BCW 1982, Prop. (3.1) ("reduction to
degree 3"): repeatedly stabilize (`+2` variables), right-compose with the
elementary `z ↦ z + P(x)` (storing a factor), left-compose with the elementary
`w_i ↦ w_i − c·w_a·w_b` (killing the monomial `c·PQ`). Three passes, 24 added
variables. Every step is composition with an explicit triangular elementary
automorphism on one side of `F̃ ⊕ id`, so det and the collision transport exactly
(witness points pushed through the inverse inner elementaries).

**Verified [V]:** degree bound; identity linear part; `G(0)=0`; distinctness +
equal images of the 3 transported points; exact `det Jac G = 1` at random rational
points. **Cited [C]:** `det Jac G ≡ 1` *identically* follows from the verified
elementary factorization + chain rule (a 27×27 fully symbolic determinant was
attempted and did not finish in 600 s; the factorization argument is complete
regardless — each factor's Jacobian is unitriangular).

## 3. Witness 2: cubic-homogeneous Yagzhev/BCW form (dim 55) — `verify_cubic_homogeneous.py`

**Statement.** An explicit `L = X + N' : C⁵⁵ → C⁵⁵` with `N'` **cubic homogeneous**,
`J(N')` nilpotent, `det Jac L ≡ 1`, and three distinct rational points with one
image.

**Provenance.** BCW 1982, proof of Theorem (2.1), Steps 2–3, applied to the dim-27
witness `G = X + F₂ + F₃`:
- *doubling*: `F'(X,Y) = (X + F₂(X) + Y, Y − F₃(X))` on `C⁵⁴`, which factors as
  `G(1) ∘ (G ⊕ id) ∘ H(1)` with `G(T) = (X+TY, Y)`, `H(T) = (X, Y−T·F₃(X))`
  — factorization verified symbolically [V]; witnesses transport as `(p, F₃(p))`;
- *homogenization*: `L(X,Y,T) = (X + T²Y + T·F₂(X), Y − F₃(X), T)`; at `T=1` this
  is `(F', 1)`, so witnesses become `(p, F₃(p), 1)` [V].

**Verified [V]:** cubic homogeneity + identity linear part; `L(·,·,1) = (F',1)`;
the scaling identity `J(E(T))(x) = (Jac G)(Tx)` entrywise (the engine of
Keller-ness); 3-point collision; exact `det Jac L = 1` at random rational points;
pointwise nilpotency `J(N')(pt)⁶⁴ = 0` at a random rational point.
**Cited [C]:** two classical lemmas complete the identical-Keller proof: BCW
Lemma (4.1) (`1 + aT` invertible over `k[T]` ⟺ `a` nilpotent) and BCW's
graded-ring lemma (p. 306–307) giving nilpotency of `J(N'(T))` from that of `J(N)`.

**Duplication note:** W. Thompson's independent 24-variable cubic-homogeneous
example (GitHub/Zenodo, 07-2x, not on arXiv at scan time) is smaller; ours is
independent, carries a *three*-point rational collision, and feeds witness 3.

## 4. Witness 3 (headline): explicit Drużkowski counterexample (dim 368) — `verify_druzkowski.py`

**Statement.** An explicit rational `368×368` matrix `C` such that
`G(y) = y + (Cy)^{*3}` (componentwise cube — Drużkowski / cubic-linear form) is a
Keller map (`det Jac G ≡ 1`) with three distinct rational points sharing one
image. To our knowledge the first explicit Drużkowski counterexample; Drużkowski's
1983 theorem says JC is equivalent to this class, so an explicit member had to
exist, and here it is with all data rational.

**Provenance & self-certification.** From witness 2: polarize
`H(x) = A((Bx)^{*3})` (each cubic monomial as a rational combination of cubes of
rational linear forms; 313 forms + 55 zero-form augmentation columns to make `A`
surjective), set `C = BA`. Then:
- *intertwining* `L ∘ A = A ∘ G` (immediate from `H = A∘cube∘B`);
- *Keller* by **Sylvester's identity** `det(I_m + XA) = det(I_n + AX)`:
  `det Jac G(y) = det(I₅₅ + A·3diag((BAy)^{*2})·B) = det Jac L(Ay) ≡ 1` [C:
  Sylvester; det Jac L ≡ 1 from §3];
- *witnesses*: `y_p` any rational solution of `A y = p`, and
  `y_q = y_p + (Bp)^{*3} − (Bq)^{*3}`; the identity `A((Bp)^{*3} − (Bq)^{*3}) =
  H(p) − H(q) = q − p` makes `A y_q = q` and `G(y_p) = G(y_q)` automatic.

**Verified [V]:** the polarization identity `H = A((Bx)^{*3})` symbolically; the
three points distinct with equal images (exact evaluation); the Sylvester
right-hand side `det(I₅₅ + A·D·B) = 1` and `det Jac L(Ay) = 1` exactly at random
points. Map data dumped in `druzkowski_map.py`.

## 5. Witness 4: Dixmier and Poisson conjectures — `verify_dixmier_poisson.py`

**Construction.** With `F̃ = (R/2, Q, P)` (det ≡ 1) and `W := (JF̃ᵀ)⁻¹ = adj(JF̃)ᵀ`
(polynomial since det ≡ 1), define
`φ(x_i) = F̃_i`, `φ(∂_i) = D_i = Σ_j W_ij(x) ∂_j`.

**Verified [V]:** all defining relations of the Weyl algebra `A₃` are preserved:
`[D_i, F̃_j] = δ_ij` (i.e. `W·JF̃ᵀ = I`) and `[D_i, D_j] = 0` (vanishing of the
Lie brackets of the vector fields; first-order operators with function
coefficients have no ordering corrections). So `φ` is a well-defined endomorphism
of `A₃`, and every endomorphism of the (simple) Weyl algebra is injective.

**Dixmier status audit (careful with directions).**
- `DC_n ⟹ JC_n` per-n is classical ("well known"; stated in Belov-Kanel &
  Kontsevich, *The Jacobian conjecture is stably equivalent to the Dixmier
  conjecture* (2007), and in Adjamagbo & van den Essen, *A proof of the
  equivalence of the Dixmier, Jacobian and Poisson conjectures*, Acta Math.
  Vietnam. 32 (2007) 205–214; the proof constructs exactly the `φ` above and
  shows `φ` automorphism ⟹ `F` automorphism — one presentation: the image of `φ`
  is `⊕_α C[F̃]·D^α`, surjective iff `C[F̃] = C[x]`). **Contrapositive:** `F̃` is
  not an automorphism [V], hence `φ` is **not** an automorphism [C], refuting
  `DC_3`; stabilization (`φ ⊗ id` on `A_n`, `n > 3`, with the stabilized Keller
  counterexample) refutes `DC_n` for all `n ≥ 3`.
- `JC_{2n} ⟹ DC_n` (Tsuchimoto 2005; BKK 2007). This direction now has a false
  antecedent for `2n ≥ 4`: it refutes nothing by itself, but the strategy
  "prove `JC_4` to get `DC_2`" is **dead** (BLOCKED). `DC_1`, `DC_2` remain open.
- **What is [C] vs [V] here:** the endomorphism and its relations are fully
  verified; *non-automorphy* rests on the cited classical implication, whose
  hypotheses (`F̃` Keller, not an automorphism) are verified.

**Poisson conjecture — self-contained refutation.** The same data defines the
cotangent lift `Ψ(a,b) = (F̃(a), W(a)b)` on `C⁶`, i.e. the algebra endomorphism
`Φ` of `C[x₁,x₂,x₃,ξ₁,ξ₂,ξ₃]` with `Φ(x_i) = F̃_i`, `Φ(ξ_i) = Σ_j W_ij ξ_j`. The
verified relations `{Φξ_i, Φx_j} = δ_ij`, `{Φξ_i, Φξ_j} = 0`, `{Φx_i, Φx_j} = 0`
say `Φ` preserves the canonical Poisson bracket [V]. The Poisson Conjecture
`PC_n`, introduced in Adjamagbo–van den Essen (2007) (and implicit in
Tsuchimoto's work): *every bracket-preserving C-algebra endomorphism of the
polynomial symplectic Poisson algebra in 2n variables is an automorphism*. AvdE
prove the cycle `JC_{2n} ⟹ DC_n ⟹ PC_n ⟹ JC_n`, so `JC_3` false already gives
`PC_3` false [A]; but our witness is stronger and **does not need the cycle**:
`Ψ` sends the three distinct points `(p, JF̃(p)ᵀη)`, `p` the collision points,
`η = (1,2,3)`, to one point of `C⁶` [V]; an algebra endomorphism of a polynomial
ring inducing a non-injective map on closed points is not an automorphism.
Hence **`PC_3` is refuted with an explicit verified witness**. (Conservative
caveat: this refutes the endomorphism statement `PC_n` as formulated by AvdE; it
does *not* decide the distinct Belov-Kanel–Kontsevich conjecture
`Aut(A_n) ≅ Aut(P_n)` about automorphism groups, row 7 of the table.)

## 6. Mathieu's conjecture (1997)

Statement (Mathieu 1997, *Some conjectures about invariant theory and their
applications*): for `G` a compact connected Lie group and `f, h` G-finite
(finite-type) functions on `G`: if `∫_G f^P dg = 0` for all large `P`, then
`∫_G f^P h dg = 0` for all large `P`. Mathieu proved **Mathieu ⟹ JC (all n)**.
Direction check: JC false ⟹ **Mathieu's conjecture is false**. Since
Duistermaat–van der Kallen (1998) *proved* the abelian (torus) case, the failure
must occur for some **nonabelian** `G`. We did not trace Mathieu's reduction to an
explicit `(G, f, h)`; the reduction passes through representation-theoretic
averaging and is not obviously mechanical. **Duplication:** two arXiv preprints in
the 07-20..25 window already claim explicit refutations for `G = SU(2)`
(arXiv:2607.19012) and `G = SU(3)` derived from the counterexample, so this
corollary is scooped; we record the chain only.

## 7. Zhao's conjectures

- **Instance-wise criterion** (Zhao, *Hessian nilpotent polynomials and the
  Jacobian conjecture*, Trans. AMS 359 (2007) 249–274, arXiv:math/0409534): for
  `P` homogeneous with nilpotent Hessian, the gradient Keller map `z − ∇P` is
  invertible **iff** `Δ^m P^{m+1} = 0` for `m ≫ 0`; and JC ⟺ **VC**: "for every
  homogeneous quartic `P` with `Hes P` nilpotent, `Δ^m P^m = 0` for `m ≫ 0`".
- **Consequence [A]:** JC false ⟹ VC false. Moreover once a Hessian-nilpotent
  quartic `P₀` with non-invertible gradient map is exhibited, the instance-wise
  criterion certifies `Δ^m P₀^{m+1} ≠ 0` for infinitely many `m` — the
  contrapositive route, as a "some m fails" statement is not finitely checkable.
- **Constructive gap (honest):** the required `P₀` comes from the de Bondt–van
  den Essen symmetrization (*Nilpotent symmetric Jacobian matrices and the
  Jacobian conjecture* I–II, ~2004–05: JC reduces to symmetric Keller maps
  `x + ∇P`, over `C`, with dimension inflation). We **probed** the naive
  candidate `P = ⟨y, N'(x)⟩` built from witness 2 and found its Hessian is *not*
  nilpotent at a random point (exact computation) — so the genuine dBvdE
  construction (with its correction terms) is required and was **not executed**
  here. Status: REFUTED-A with a documented constructive path; the explicit
  witness appears to be **unclaimed** as of the 07-25 scan.
- **Image Conjecture / Mathieu subspaces** (Zhao 2010): the IC instances that
  imply JC are now false [A]; untraced further.

## 8. Markus–Yamabe and other formulations

- Polynomial Markus–Yamabe (`n ≥ 3`) was already false (Cima–van den Essen–
  Gasull–Hubbers–Mañosas 1997) — no change; the new example adds nothing there
  (it is not a MYC vector field).
- The properness reformulation ("every Keller map is proper") is refuted inside
  the Alpöge paper itself (its `S_F = V(Δ)` is a hypersurface).
- van den Essen's catalogue of equivalent formulations (kernel conjectures for
  derivations, etc.): each equivalence transfers falsity [A]; none traced to
  explicit witnesses here beyond rows 2–4, which are the classically canonical
  reduced forms.

## 9. arXiv / public duplication sweep (2026-07-20 → 07-25)

Method: arXiv listings (math.AG/AC/RA 2607) + arXiv API searches ("Jacobian
conjecture", "Dixmier", "Mathieu conjecture", "Druzkowski", "vanishing
conjecture") via a background scout, plus direct fetches of the two GitHub
artifacts. Findings (confidence: GitHub items directly inspected; arXiv items
from the scout report):

1. **Dixmier `A₃` endomorphism**: informal note + repo `wmayner/dixmier-counterexample`
   (GitHub, exact-rational SymPy audit, same construction as ours; cites the
   classical BCW-era `DC ⟹ JC` argument). Not on arXiv at scan time. Our
   contribution overlaps; our addition is the **Poisson companion**, absent there.
2. **Cubic-homogeneous**: `wtho704/explicit-cubic-homogeneous-jacobian-counterexample`
   (GitHub + Zenodo): 24 variables, 54 cubic monomials, `(JN)¹⁷ = 0`,
   `det ≡ 1`, rational collision pair, dual SymPy/BigInt verification. Smaller
   than our 55-dim example; not on arXiv at scan time.
3. **Mathieu**: arXiv:2607.19012 (SU(2)) and an SU(3) companion preprint —
   explicit refutations claimed. Scooped.
4. **Zhao VC / IC, Dixmier "in general"**: abstract-corollary notes circulating;
   no explicit Hessian-nilpotent quartic witness found.
5. **Drużkowski / cubic-linear explicit witness**: **nothing found** — our
   `druzkowski_map.py` (368×368 rational `C`, triple collision) appears to be
   first.
6. **Poisson conjecture explicit witness**: **nothing found** — apparently first.

Coverage caveat: 5-day window, one scout pass + manual fetches; listings may lag
and preprints may be in moderation. Treat "apparently first" accordingly.

## 10. Open leads

- Execute the genuine dBvdE symmetrization to get the explicit Hessian-nilpotent
  quartic `P₀` (Zhao VC witness) — the main remaining unclaimed artifact.
- Trace Mathieu's reduction to an explicit `(G, f, h)` for a *minimal* compact
  group; compare with the SU(2)/SU(3) preprints.
- Minimize dimensions: 27 → (Thompson suggests ≤ 24 possible for cubic
  homogeneous); a smarter monomial-splitting schedule (shared factors across
  passes, BCW's "linear in each variable" refinement) should shrink 27/55/368
  substantially; the 368-dim `C` also has 55 zero rows that a rank-reduction of
  the polarization could largely remove.
- Weyl-algebra positive characteristic / `DC_2`: nothing here touches them.
- The `n = 2` question is genuinely different: see companion `n2_analysis.md`
  (Moh degree ≤ 100, Orevkov/Domrina generic-degree obstructions, and a no-go
  for the cubic-fiber mechanism in the plane).

## 11. Artifact inventory (all PASS, exact arithmetic, sympy 1.11.1)

| script | verifies | output data |
|---|---|---|
| `verify_base.py` | base map: det ≡ −2, triple collision, normalized form | — |
| `verify_deg3_keller.py` | dim-27 degree-≤3 witness (constructs + verifies) | `deg3_map.py` |
| `verify_cubic_homogeneous.py` | dim-55 cubic-homogeneous witness (BCW steps 2–3) | `cubic_map.py` |
| `verify_druzkowski.py` | dim-368 Drużkowski witness (polarization + Sylvester) | `druzkowski_map.py` |
| `verify_dixmier_poisson.py` | `A₃`-endomorphism relations; Poisson bracket preservation; `C⁶` triple collision | — |
| `verify_n2.py`, `n2_analysis.md` | companion `n = 2` analysis (interim session) | — |

Copies banked in `~/finite-certificates/jacobian/`. Not committed to git (per brief).
