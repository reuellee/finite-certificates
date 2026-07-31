# OMGAMMA — connectivity of the mutation graphs of uniform oriented matroids, n ≤ 9

Slow-lane program note. Started 2026-07-31. Status: ACTIVE.
Predecessor standards apply: every claim carries a machine-checkable
certificate or an explicit trust boundary; deliberately-broken controls
("canaries") are wired into every computation.

## 1. Mission, and a correction to the mission brief

The brief asked to settle "the reorientation-class variant Γ̃ that
Knauer & Marc explicitly suspect has a counterexample," and flagged the
three-graph distinction as the precision-critical point, instructing that
the exact statements be taken from the paper verbatim. Doing so (source:
LaTeX source of arXiv:2002.11403v3, K. Knauer, T. Marc, *Corners and
simpliciality in oriented matroids and partial cubes*, tarball dated
2023-03-14; the brief cites the published version, Eur. J. Combin. 112
(2023) 103714 = DOI 10.1016/j.ejc.2023.103714, which redirects to
Elsevier article S0195669823000318) shows the brief's attribution is off
by one level of the hierarchy. Verbatim, from Section "Mutation graphs of uniform oriented
matroids":

> * $\overline{\mathcal{G}}^{n,r}$ is the graph whose vertices are UOMs of
>   rank $r$ and isometric dimension $n$, embedded into $Q_n$. Two graphs
>   are connected if and only if there exists a mutation between them.
> * $\mathcal{G}^{n,r}$ is the graph whose vertices are reorientation
>   classes of UOMs of rank $r$ and isometric dimension $n$ embedded into
>   $Q_n$. Two reorientation classes are connected if and only if there
>   exists a mutation between them.
> * $\underline{\mathcal{G}}^{n,r}$ is the graph whose vertices are graph
>   isomorphism classes of UOMs of rank $r$ and isometric dimension $n$.
>   Two classes are connected if and only if there exists a mutation
>   between them.

Reorientation is defined there as $f\in\mathbb{Z}_2^n\subseteq
\mathrm{Aut}(Q_n)$ ("$f$ only switches signs"); graph isomorphism classes
correspond to the full $\mathrm{Aut}(Q_n)=\mathbb{Z}_2^n\rtimes S_n$.
Dictionary to the brief's names: Γ = $\overline{\mathcal{G}}$ (labeled),
Γ̃ = $\mathcal{G}$ (reorientation classes), Γ̂ = $\underline{\mathcal{G}}$
(isomorphism classes).

The Cordovil–Las Vergnas conjecture, as Knauer–Marc state it (their
conjecture labeled conj:cordovil in the source, citing Roudneff–Sturmfels
1988; we cite by source label since the published numbering was not
checked against the paywalled version):

> **Conjecture (Cordovil-Las Vergnas).** For all $r,n$ the graph
> $\mathcal{G}^{n,r}$ is connected.

So the CLV conjecture itself lives at the reorientation-class level Γ̃ —
and Knauer–Marc *settled it* for n ≤ 9 (their corollary labeled cor:94: "The graph
$\mathcal{G}^{n,r}$ is connected for $n\leq 9$."), via their proposition
labeled prop:mut ($\underline{\mathcal{G}}$ connected ⟹ $\mathcal{G}$ connected, using
Roudneff–Sturmfels' realizable connectivity) plus an unpublished
computation that $\underline{\mathcal{G}}^{n,r}$ is connected for all
parameters of their Table 1 (using tope graphs + the Bliss graph-iso
package). What they leave open, and where they suspect a counterexample,
is the LABELED graph. Verbatim:

> "Testing graph isomorphism instead of OM-isomorphism was an essential
> ingredient in order to obtain Corollary [ref cor:94]. Checking connectivity of
> $\overline{\mathcal{G}}^{n,r}$ is far more demanding. We do not know
> anything about the connectivity of this graph beyond rank 3."
> (text following cor:94)

> "We have verified it [CLV] by computer for small examples and it holds
> for low rank in general. However, here we suspect the existence of a
> counter example at least in the setting of
> $\overline{\mathcal{G}}^{n,r}$."  (Conclusion)

**Corrected mission**: settle $\overline{\mathcal{G}}^{n,r}$ (the level
where the suspected counterexample lives) for n ≤ 9, and en route
re-derive $\mathcal{G}$ and $\underline{\mathcal{G}}$ independently
(their Γ̂ computation is an assertion without published artifacts), plus
resolve the (4,9) class-count discrepancy. The single holonomy
computation below settles all three levels at once, so the brief's
literal request ("settle Γ̃") is subsumed.

Also verified verbatim (their proofs of prop:mut and the rank-3 result):
their proposition labeled prop:pseudoline proves $\overline{\mathcal{G}}^{n,3}$ connected for
every n via Ringel's homotopy theorem plus an explicit reorientation
gadget; Observation ("obs:connectivities"): $\overline{\mathcal{G}}$
connected ⟹ $\mathcal{G}$ connected ⟹ $\underline{\mathcal{G}}$
connected.

### Erratum found in Knauer–Marc Table 1

Their Table 1 ("Known orders of $\underline{\mathcal{G}}^{n,r}$,
retrieved from om.math.ethz.ch") lists, in row r = 3, the value **482**
at n = 9. This contradicts (i) its own dual entry 4382 at (r,n) = (6,9),
(ii) Finschi's database (4382), (iii) FMM13 Table (4,382), and (iv) our
independent generation (4382, Section 5). A dropped digit: 482 → 4382.

## 2. Objects and conventions (fixed project-wide)

Ground set E = {1..n}, rank r; bases = r-subsets in **colex order**
(Finschi's "RevLex-Index" order — verified: the basis-order header on his
catalog pages matches colex; his glossary defines the representative as
the "lexicographically maximal chirotope" over the class).

A **uniform chirotope** is an alternating map χ: E^r → {±1}; validity =
the 3-term Grassmann–Plücker conditions (CHI2) of Richter-Gebert &
Ziegler, *Handbook of Discrete and Computational Geometry* 3rd ed.,
ch. 6, §6.2.3 — sufficient by their Theorem 6.2.3; (CHI1) is automatic
for uniform. A **UOM** (vertex of $\overline{\mathcal{G}}$) is a pair
{χ,−χ} (= tope graph embedded in Q_n).

**Mutation**: flip the sign of a single basis such that the result is
again a chirotope. Equivalence with Knauer–Marc's tope-graph definition
(fill/remove a vertex of a $Q_r^-$ at a simplicial tope) verified
computationally at (6,3), (6,4), (7,4): #degree-r topes = 2·#mutable
bases, and the incident Θ-classes of each simplicial tope match the
mutable bases exactly, two simplicial topes (an antipodal pair) per
mutable basis (test_core.py, "tope-graph mutation equivalence").

**Group**: G' = S_n × {0,1}^n × {0,1} acts on chirotopes by
((σ,ε,s)·χ)(x₁..x_r) = (−1)^s (−1)^{|ε∩{x}|} χ(σ⁻¹x₁..σ⁻¹x_r).
Composition (σ₁,ε₁,s₁)(σ₂,ε₂,s₂) = (σ₁σ₂, ε₁⊕σ₁(ε₂), s₁⊕s₂) —
action-homomorphism property verified against exact-integer point
configurations (permuting points, negating points, negating a coordinate
of the ambient space), with a deliberately-wrong composition rule as
canary (detected). For n ≥ r+1 the kernel of the action on pairs is
K₄ = {(id,0,0),(id,1ⁿ,0),(id,0,1),(id,1ⁿ,1)}; the effective group is
Ḡ = G'/K₄ of order n!·2^{n−1}. Elements are normalized (s = 0,
ε ↦ min(ε, ε⊕1ⁿ)).

Vertices of Γ̃ = $\mathcal{G}$: orbits of pair-vertices under the sign
subgroup R̄; vertices of Γ̂ = $\underline{\mathcal{G}}$: orbits under Ḡ.
All mutations are Ḡ-equivariant (mutation of g·χ at σ_g(B) = g·(mutation
of χ at B)).

## 3. The lifting reduction (proved, then machine-validated)

**Lemma 1 (transitivity on components).** Let a finite group Ḡ act by
automorphisms on a graph Γ̄ with connected quotient Γ̂ = Γ̄/Ḡ. Then the
images of the components of Γ̄ partition V(Γ̂) with no Γ̂-edge between
distinct parts; hence every component of Γ̄ maps ONTO Γ̂, Ḡ acts
transitively on the set of components, and for a base vertex v₀,

    #components(Γ̄) = [Ḡ : H],   H := {g ∈ Ḡ : g·v₀ ∈ comp(v₀)}.

H is a subgroup ("component stabilizer"). *Proof.* If π(x)=π(y) for x,y
in components C₁,C₂ then y = gx, so C₂ = gC₁ and π(C₂)=π(C₁); if a
Γ̂-edge joined π-images of C₁,C₂ it would lift to an edge inside a single
component C₃ meeting both images, forcing C₁,C₂,C₃ to be translates.
Connectivity of Γ̂ then forces every image to be everything. Orbit-
stabilizer on the transitive action on components gives the count. ∎

**Lemma 2 (generators of H).** Fix class representatives χ_c (canonical
forms), a BFS spanning tree of Γ̂ with root c₀, and transports τ_c ∈ Ḡ
defined by τ_{c₀} = e and τ_{c'} = τ_c·t along tree edges, where a
mutation edge from class c at basis j has *voltage* t defined by
ψ := χ_c ⊕ bit_j = t·χ_{c'} (as pairs). Then H is generated by

    { τ_c u τ_c⁻¹ : u ∈ Stab_Ḡ(χ_c), c any class }  ∪
    { τ_c t τ_{c'}⁻¹ : every mutation edge (c, j, c') with voltage t }.

*Proof.* (⊇): τ_c·χ_c ∈ comp(v₀) by induction along the tree (mutations
are equivariant), so τ_c u τ_c⁻¹ maps the component vertex τ_c·χ_c to
τ_c u·χ_c = τ_c·χ_c, and τ_c t τ_{c'}⁻¹ maps τ_{c'}·χ_{c'} ∈ comp(v₀)
to τ_c t·χ_{c'} = τ_c·(ψ) ∼ τ_c·χ_c ∈ comp(v₀); an element mapping a
component vertex into the component stabilizes the component.
(⊆): let g ∈ H, i.e. a path v₀ = x₀ ∼ x₁ ∼ ... ∼ x_k = g·v₀ in Γ̄.
Write x_i = s_i·χ_{c_i} with s₀ = e; each edge translates to
χ_{c_i} ∼ s_i⁻¹s_{i+1}·χ_{c_{i+1}}, and since the Γ̄-neighbors of χ_{c_i}
are exactly its mutations, s_i⁻¹s_{i+1} ∈ t·Stab_Ḡ(χ_{c_{i+1}}) for the
voltage t of some mutation edge (c_i, j, c_{i+1}). So g ∈ s_k·Stab(χ_{c₀})
and g factors as a product of edge-voltages and stabilizer elements;
inserting τ⁻¹τ between factors rewrites the product in terms of the
conjugated generators (a telescoping standard in covering-space /
voltage-graph arguments). ∎

**Consequences** (Γ̂ connected, H computed from the exhaustive edge and
stabilizer enumeration):
  * Γ̄ = $\overline{\mathcal{G}}^{n,r}$ connected ⟺ H = Ḡ;
    #components = [Ḡ : H].
  * Γ̃ = $\mathcal{G}^{n,r}$: with R̄ ⊴ Ḡ the sign subgroup and
    π: Ḡ → S_n ≅ Ḡ/R̄: an edge R̄x ∼ R̄y of Γ̃ means x ∼ ρy for some
    ρ ∈ R̄, so stepwise lifting gives comp_Γ̃(R̄v₀) = {R̄y : y ∈
    R̄·comp_Γ̄(v₀)}, and the Γ̃-component stabilizer is H̃ = R̄H (a
    subgroup because R̄ is normal). Hence
    #components(Γ̃) = [Ḡ : R̄H] = [S_n : π(H)]; connected ⟺ π(H) = S_n.

**Machine validation of the entire reduction** (test_flip.py): at
(n,r) ∈ {(5,3),(6,3),(5,4),(6,4),(5,2),(6,2)} the full labeled graph Γ̄
was materialized by brute force (all sign vectors, GP-filtered, folded
into pairs, union-find over single-bit flips) and its exact component
count equals [Ḡ : H] with H computed by the quotient-BFS holonomy in
every case (all connected; labeled vertex counts 192, 11904, 16, 1920,
192, 1920 respectively).

The sign part of H is completed deterministically (exact, not
heuristically): Schreier generators over a transversal of ⟨logged
generators⟩ plus harvesting every stored coset representative, then
closing the F₂-span under the permutation action; correctness argument
in flip.py docstring (uses normality + abelianness of R̄).

### Proposition 4 (sign-part dichotomy) — new, 2026-07-31

**Setup.** R̄ ⊴ Ḡ is the sign subgroup {0,1}ⁿ/⟨1ⁿ⟩ (order 2^{n−1}) and
π: Ḡ ↠ S_n = Ḡ/R̄. For H ≤ Ḡ put S := H ∩ R̄ (the "sign part"). R̄ is
normal, so S ⊴ H, and for h ∈ H with π(h) = σ the project's composition
rule gives directly

    (σ,δ,s)·(id,ε,0)·(σ,δ,s)⁻¹ = (id, σ(ε), 0),

so S is π(H)-invariant. **If π(H) = S_n then S is an F₂[S_n]-submodule
of R̄.** (In the code the tracked object is the lift U ≤ F₂ⁿ of S; the
SignSpace is seeded with 1ⁿ, so the printed "sign d/n" is dim U =
dim S + 1, and with π(H) = S_n one has |H| = n!·2^{dim U−1}, hence
#components(Γ̄) = [Ḡ : H] = 2^{n − dim U}.)

**Proposition.** For **n odd**, 2 ∤ n, so F₂ⁿ = ⟨1ⁿ⟩ ⊕ E with E the
even-weight subspace, and R̄ ≅ E is the standard module S^{(n−1,1)},
irreducible over F₂ precisely because 2 ∤ n. Therefore S ∈ {0, R̄} and,
with π(H) = S_n and Γ̂ connected,

    #components(Γ̄^{n,r}) ∈ {2^{n−1}, 1}.

For n = 9: **#components(Γ̄^{9,r}) ∈ {256, 1}** — the labeled question at
n = 9 is exactly binary once π(H) = S₉ is known, and a SINGLE
sign-nontrivial holonomy loop settles the positive case. For **n even**
1ⁿ ∈ E and the intermediate value S = E/⟨1ⁿ⟩ (index 2 in R̄) is also
admissible: the full sign part observed at (8,3), (8,4) was *not* forced
by the algebra.

*Machine check* (`submodules.py` → `artifacts/submodules.json`, exact
integer/F₂ arithmetic, two independent methods plus a canary). For
n = 5..10 all S_n-invariant subspaces of F₂ⁿ are enumerated
  * (M1) as the sums Σ_{w∈W} span(weight-w vectors), W ⊆ {0..n} — complete
    because every invariant subspace is the sum of the spans of the
    S_n-orbits of its elements and those orbits are exactly the weight
    classes; and
  * (M2, n ≤ 7) by filtering ALL subspaces, enumerated through their
    unique reduced row echelon forms — the totals 374 / 2825 / 29212 match
    the Galois numbers G₅ / G₆ / G₇, so the enumeration is provably
    exhaustive.
M1 = M2 in every checked case; each n has exactly four invariant
subspaces (0, ⟨1ⁿ⟩, E, F₂ⁿ). Restricted to those containing 1ⁿ:

| n | possible dim U | #components(Γ̄) if π(H)=S_n |
|---|---|---|
| 5, 7, 9 | 1, n | 2^{n−1}, 1 |
| 6, 8, 10 | 1, n−1, n | 2^{n−1}, 2, 1 |

Canary: the deliberately non-invariant span⟨e₁⟩ is rejected by the
invariance test and is absent from the M1 list at every n. Consistency
with the completed runs: every finished computation in the table below
reported sign dim = n exactly; no run has ever shown an intermediate
value, as the proposition requires for odd n and permits (but does not
force) for even n.

## 4. Remark: the labeled level reduces to the isomorphism level (theory)

The following easy configuration-space lemma seems to be folklore but we
could not find the labeled-level statement in print; it makes the
suspected-counterexample level collapse onto the level Knauer–Marc
already verified, for every n where Γ̂ is connected.

**Lemma 3 (labeled realizable connectivity).** For all n ≥ r ≥ 1 the
subgraph of $\overline{\mathcal{G}}^{n,r}$ induced by the REALIZABLE
uniform OMs is connected. *Proof sketch.* Chambers of
D = {V ∈ (ℝ^r)^n : all r×r minors ≠ 0} map onto realizable labeled
chirotopes; the union of the singular loci of the hypersurfaces
{det_B = 0} and their pairwise intersections has codimension ≥ 2 in
ℝ^{rn}, so any two points of D are joined by a smooth path crossing the
walls transversally one at a time at smooth points; each crossing flips
exactly one basis sign, i.e. is a mutation between realizable uniform
chirotopes. ∎  (Cf. Roudneff–Sturmfels 1988, Geom. Dedicata 27, whose
Prop. is quoted by Knauer–Marc at the reorientation-class level; the
chamber argument gives the labeled statement with the same technique.)

**Corollary.** If $\underline{\mathcal{G}}^{n,r}$ is connected then
$\overline{\mathcal{G}}^{n,r}$ is connected (lift a quotient path from
any labeled A to a labeled copy of a realizable OM — realizability is
Aut(Q_n)-invariant — then apply Lemma 3). In particular Knauer–Marc's own
Γ̂ computation already implies Γ̄ connected for n ≤ 9, *contrary to their
suspicion*, modulo Lemma 3.

Because Lemma 3 is our own argument, we do NOT rest the computational
verdicts on it: the holonomy computation below decides Γ̄ directly,
without any realizability input. Lemma 3 is stated as context and as an
explanation of why the positive outcome should be expected — and the
computation is the check of the Lemma's prediction.

## 5. Computations and results so far (all exact, stdlib Python)

Catalog generation from scratch (single-element coline... extension
solver with brute-force cross-checks at (5,3),(5,4),(6,4); catalog =
dedupe by canonical key):

| (r, n) | classes found | published | source of published |
|---|---|---|---|
| (3, 5..9) | 1, 4, 11, 135, **4382** | same | Finschi DB; FMM13; K–M Table 1 has typo 482 at (3,9) |
| (4, 5..8) | 1, 1, 11, **2628** | same | Finschi DB = K–M = FMM13 |

External anchors: my 11 classes at (7,4) are key-identical to Finschi's
IC(7,4,1..11) (scraped verbatim from finschi.com/math/om); his
representatives are literal fixed points of my max-string
canonicalization; same for the 135 at (8,3) (spot-checked fixed points,
full key-set equality).

Labeled counts via exact stabilizer orders (mass formula, validated
against brute-force stabilizers and against two independent computations
at five levels): labeled chirotopes N_chi(4,8) = 25,703,946,240;
N_chi(3,9) = 795,396,833,280; N_chi(4,7) = N_chi(3,7) = 3,486,720
(duality check passes).

Holonomy verdicts (exhaustive BFS over Γ̂ with all mutation edges and
all stabilizer generators; sign part exact):

| (n,r) | Γ̂ classes | Γ̂ conn. | π(H) = S_n | sign part full | verdict |
|---|---|---|---|---|---|
| (8,3) | 135 ✓cat | yes | yes (40320) | yes (8/8, exact) | **Γ̄(8,3), Γ̃(8,3) connected** |
| (9,3) | 4382 ✓cat | yes | yes (362880) | yes (9/9, exact) | **Γ̄(9,3), Γ̃(9,3) connected** |
| (7,4) | 11 ✓cat | yes | yes (5040) | yes (7/7) | **Γ̄(7,4), Γ̃(7,4) connected** |
| (8,4) | 2628 ✓cat | yes | yes (40320) | yes (8/8, exact) | **Γ̄(8,4), Γ̃(8,4) connected** — NEW (first rank-4 labeled verdict) |
| (9,4) | 9,276,… (campaign, §6) | pending | yes (362880) | yes (9/9, exact) | **H = Ḡ** ⟹ #comp(Γ̄) = #comp(Γ̂) (Result A, §6) |
| tiny  | (5,2),(5,3),(5,4),(6,2),(6,3),(6,4) | yes | yes | yes | connected & brute-force-equal |

Both (8,4) and (9,3) were re-run through the parallel disk-based engine
(runbig.py) with mass-formula termination: the accumulated
orbit-stabilizer mass hit the independently computed target
N_chi exactly (100.0000%), certifying catalog completeness AND
Γ̂-connectivity simultaneously. Γ̂(8,4) has 15,338 directed mutation-edge
traversals from class representatives (avg mutation degree ≈ 11.7).
Both were re-run again on 2026-07-31 after the engine rework, from
scratch and from a forced mid-level resume, with `phase1cap = 2` so that
essentially all holonomy harvesting goes through the parallel path; all
four runs reproduce these numbers exactly (§6).

The mass target itself is re-derivable from its own per-class artifact:
Σ_c (|G'₈|/stab_c)·E_c over `data/extcount_4_9.jsonl` (2628 rows,
Σ E_c = 176,265,330) gives N_chi(4,9) = 1,722,704,635,330,560, equal to
the stored target.

**Standalone certificates + checker**: for each completed (n,r) the run
emits reps/tree/gens/exhibits files; `checker.py` (zero shared code;
independent GP check, group action, orbit-stabilizer-chain order
computation, word evaluation) verifies V1-V5 (see its docstring) and
passed on (8,3), (8,4), (9,3). Sabotage canaries (`canary_checker.py`:
corrupted rep char / tree voltage / generator perm / truncated exhibits /
re-pointed tree parent) are all rejected by the checker.

### Coverage of every rank at n ≤ 9

* **r ≤ 1 and r ≥ n−1** (vacuous-GP lemma): the 3-term GP condition set
  is empty iff r < 2 or n < r+2; then EVERY sign vector on the C(n,r)
  bases is a uniform chirotope and every single-bit flip is a mutation,
  so Γ̄^{n,r} is the folded C(n,r)-cube, which is connected (two antipodal
  pair-classes of any two vertices differ in ≤ C(n,r) bits, flip them one
  at a time). (n,n) is a single pair-vertex. Verified computationally:
  random-sign validity + explicit union-find connectivity at
  (6,5),(7,6),(8,7),(9,8),(9,1) [256-vertex folded cubes etc.].
* **r = 2**: computed directly for every n ≤ 9: brute force at
  (5,2),(6,2); exact holonomy H = Ḡ at (7,2) [1 class, 7 edges],
  (8,2) [1 class, 8 edges], (9,2) [1 class, 9 edges, 66 s — the rank-2
  canonicalizer is slow because all (k,2)-restrictions are equivalent,
  but it terminates]. So Γ̄^{n,2}, Γ̃^{n,2} connected for all n ≤ 9,
  with no reliance on Lemma 3.
* **r = 3**: exhaustive holonomy verdicts n ≤ 9 (table above), agreeing
  with Knauer–Marc's prop:pseudoline (their Ringel-based proof for all n).
* **r = 4**: exhaustive n ≤ 8 (table above); n = 9 campaign below.
* **5 ≤ r ≤ n−2**: by duality. Proposition (duality transport): the map
  χ ↦ χ*, χ*(x_{r+1..n}) = χ(x_1..x_r)·sgn(x_1..x_n), descends to
  isomorphisms Γ̄^{n,r} ≅ Γ̄^{n,n−r}, Γ̃ ≅ Γ̃, Γ̂ ≅ Γ̂: it is a bijection
  on pairs (double dual = ±id, verified), commutes with reorientation and
  relabeling up to sign (standard, [BLSWZ §3.4]; K–M cite Ex. 7.9 for the
  CLV statement), and maps the mutation at B to the mutation at E∖B
  (verified computationally: mutable-basis sets correspond under
  complementation at (7,4)/(7,3) and for all 135 classes at (8,3)/(8,5);
  the 135 dualized (8,3) reps give exactly 135 distinct (8,5) classes,
  and a 110-class sample of (9,3)→(9,6) behaves identically).
  Hence (7,5)≅(7,2), (8,5)≅(8,3), (8,6)≅(8,2), (9,5)≅(9,4),
  (9,6)≅(9,3), (9,7)≅(9,2) as labeled mutation graphs.

## 6. The (9,4) campaign (design)

Cost model: ~9.28M classes × ~⟨mutations⟩ canonicalizations for the
exhaustive BFS; plus completeness. Two independent certificates:

1. **Coverage + holonomy**: disk-based level-synchronous BFS over Γ̂(9,4)
   (frontier files, workers, sort-merge dedupe by canonical key),
   harvesting voltages/stabilizers until the holonomy saturates, then
   key-coverage only.
2. **Completeness by mass formula** (no second class sweep): compare
   Σ_{BFS classes} |G'₉|/stab_c against Σ_{2628 (8,4) classes}
   (|G'₈|/stab)·E_c where E_c = #extension signings of the class rep
   (cheap counting sweep, no canonicalization). Equality is an exact
   integer identity certifying that the BFS reached EVERY class, i.e.
   Γ̂(9,4) is connected AND the class count is definitive — this is what
   settles 9,276,595 vs 9,276,601.

Canary set for the campaign (all executed): (a) the same pipeline at
(8,4) and (9,3) reproduces the known results exactly, both before and
after the full-edge-harvest rework; (b) sabotaged certificates (five
corruption modes) are rejected by BOTH the pure checker and the numpy
fast checker; (c) scrambled chirotopes fail GP; (d) a corrupted mass
target (+998244353) is loudly detected ("frontier empty but mass <
target", complete=false). Note also the stop-rule granularity: the mass
is compared only at level boundaries, so a false "complete" would
additionally require the wrong target to coincide exactly with a
level-boundary partial sum.

Holonomy at (9,4) is harvested from EVERY expanded edge (inline at
known-hits, deferred for in-level duplicates with a bounded, *counted*
buffer) and from the stabilizer of every class with a nontrivial
Ḡ-stabilizer, so if the run terminates by mass with H < Ḡ, the harvested
H is a lower bound with provenance sufficient to investigate; if it
terminates with H = Ḡ, the positive verdicts are certificate-backed. The
final saturation is the exact staged Schreier computation.

### Result A (2026-07-31): the holonomy at (9,4) is everything

**H = Ḡ for (9,4)**, established from generators harvested inside the
already-checkpointed 1,876,681-class region (20.2% of Γ̂(9,4) by mass) —
i.e. *independently of whether the coverage sweep completes*:

* sign part 9/9 (full): from the 2608 family-(i) stabilizer conjugates of
  the 2548 flagged classes, after the exact staged Schreier completion
  (`data/big_4_9/diag_stabhol.json`).
* π(H) = S₉ (order 362,880): the family-(i) generators alone give A₉
  (order 181,440 — every stabilizer element of every flagged class has an
  EVEN permutation part), and the odd coset comes from edge voltages.
  Reached at level 3 of the original sweep, and re-derived after the
  resume at level 9 from just **2** edge generators
  (`data/big_4_9/meta.json`: `hol_perm_order 362880`, `hol_sign_dim 9`,
  `hol_full true`, `stab_gens 2608`, `edge_gens 2`).

A curiosity that survives the retraction of the old "flatness" claim, now
correctly measured: expanding the 2000 classes nearest the root yields
26,013 edge voltages whose permutation parts are **all even** — π stays
at A₉ over that whole ball. The odd coset first appears a couple of BFS
levels out. This is a real, if minor, structural feature of the
alternating OM's neighbourhood at (9,4); it is *not* evidence about the
sign part, which is what the retracted observation confused it with.

Note that Lemma 2's (⊇) direction — every harvested element lies in H —
needs only that the tree paths exist, not that the BFS is complete. So
the harvested elements are genuine members of H whatever the rest of the
graph looks like.

**Consequence, unconditional on coverage.** Apply Lemma 1 to the
Ḡ-invariant subgraph Γ̄′ = π⁻¹(Γ̂′) where Γ̂′ is the component of Γ̂(9,4)
containing the root: Γ̄′ is a union of components of Γ̄, its quotient Γ̂′
is connected, and its component stabiliser contains everything harvested,
hence equals Ḡ. Therefore Γ̄′ is connected, and

    #components(Γ̄^{9,4}) = #components(Γ̂^{9,4}),
    Γ̄^{9,4} connected  ⟺  Γ̂^{9,4} connected,

with the same statement for Γ̃^{9,4} (since π(H) = S₉). In particular the
labeled level at (9,4) carries **no extra components over the
isomorphism level** — which is exactly what Knauer–Marc suspected might
fail, and what Lemma 3 predicts. The coverage sweep is now needed only
for Γ̂-connectivity and the class count, not for the labeled verdict
given Γ̂.

By Proposition 4 this was the only alternative to 256 components; the
"binary" prediction is confirmed on the connected side.

### ~~Empirical observation: local holonomy flatness at (9,4)~~ — RETRACTED

An earlier revision of this section recorded that the (9,4) run showed a
persistently trivial sign part (1/9) through level 8 — 16.6M expanded
edges — and read that as a structural "flatness" of the covering
Γ̄ → Γ̂ near the alternating class, i.e. as evidence that the labeled
question at (9,4) is genuinely delicate. **That reading was wrong, and
the observation was an artifact of a gap in the engine, not a property of
the object.** See the ERRATUM below (missing Lemma-2 family (i)
generators in phase 2). What remains true and unremarkable is the
phase-1 diagnostic itself: a ball of 4000 classes / 18,091 directed
edges around the alternating class yields a holonomy of permutation
order 18 and trivial sign part — the alternating class simply has a
large stabilizer and the ball is small (0.04% of the graph by mass).

### ERRATUM (2026-07-31): phase 2 harvested only half of Lemma 2

Lemma 2 generates H from two families: (i) τ_c u τ_c⁻¹ for u ∈
Stab_Ḡ(χ_c), and (ii) τ_c t τ_{c'}⁻¹ for the mutation edges. The
in-process engine (`flip.bfs_holonomy`) and `runbig.phase1` harvest both.
**`runbig` phase 2 harvested only family (ii)**: its worker computes the
canonical stabilizer of every child (`canonical(..., want_witness=True)`)
and discards everything but its ORDER. So every class discovered in
phase 2 contributed no family-(i) generator. At (9,4), phase 1 covered
4000 of 1,876,681 classes, so 2548 classes with a nontrivial
Ḡ-stabilizer were reachable and only a handful of them had been
harvested. The harvested H was therefore a strict lower bound, and its
sign part was spuriously trivial.

The fix (a) makes phase 2 re-canonicalize, in the master, every fresh
class flagged with stab_order_exact > 2^κ (κ = dim of the kernel of the
sign action on strings; κ = 1 at (9,4), so the flag is stab > 2) and
harvest its family-(i) generators, and (b) has `--resume` backfill the
same for every already-known class. Only flagged classes can contribute,
so the cost is one canonicalization per flagged class — 2548 of 1.88M,
i.e. free. The flag is also a free integrity check: the re-canonicalized
key and stabilizer order must equal the stored ones (they did, for all
2548).

**Effect** (`data/big_4_9/diag_stabhol.json`, produced by
`diag_stabhol.py` on the crashed checkpoint): the 2548 flagged classes
give 2608 nontrivial conjugates; the subgroup they generate has
permutation part A₉ (order 181,440) and, after the exact staged Schreier
completion, **sign part 9/9 — FULL**. Combined with π(H) = S₉ (which the
edge family had already certified at level 3), this gives H = Ḡ. The
"(9,4) is flat" reading is dead; by Proposition 4 the sign part could
only ever have been 0 or everything, and it is everything.

Why the regression suite did not catch this earlier: at (8,4) and (9,3)
phase 1 covered 802 resp. ~1400 classes *including* their stabilizers,
and the remaining family-(i) generators were not needed to reach H = Ḡ.
The suite now runs both cases with `phase1cap = 2`, which forces
essentially all harvesting through phase 2.

### Resume, memory safety, and the completing pass (2026-07-31)

The first (9,4) attempt was killed by the OS at level 9 (8 workers,
16 GB machine with ~2 GB free) with levels 0–8 checkpointed. The engine
now supports `--resume`.

**What is rebuilt, and from what** (`bigstate.load_state`): the class
keys / canonical masks / stabilizer orders / spanning tree
(parent, flip, σ, ε) and the sorted packed-key index are read verbatim
from `level_*.npz`; the **transports τ are recomputed by walking the
saved tree from the root** (τ_c = τ_parent ∘ t, vectorized; the formula
is self-tested against `core.g_compose` on random inputs at import) —
they are never read from disk, because nothing else about them would be
trustworthy. The frontier is the set of classes discovered at the last
completed level.

**Resume gate** (abort loudly on any mismatch): level files contiguous
from 000; the `ids` array of every level exactly `arange`-contiguous;
recomputed class count and recomputed total mass equal to `meta.json`;
`meta.level` equal to the last level file (a torn checkpoint — level file
written, meta not — is refused, with the fix being to delete the trailing
level file); no duplicate canonical keys. Then a random sample of 200
classes is re-canonicalized from scratch: stored key, stored canonical
mask, stored stabilizer order and the tree mutation identity
χ_parent ⊕ bit_j = ±t·χ_child must all reproduce.

**Resume canaries** (`canary_resume.py`, run on the (8,4) checkpoint;
control = the clean checkpoint must be ACCEPTED): six deliberately
corrupted checkpoints are all rejected — total_mass off by one Ḡ-orbit,
total_classes off by one, a torn checkpoint (trailing level file that
meta.json does not know about), a deleted middle level file, a flipped
tree-edge voltage bit, and a flipped bit in a stored canonical mask. The
last two are caught only by the re-canonicalization sample check, which
is what that check is for.

**Holonomy on resume — the correctness trap.** The harvested generators
are NOT on disk. A resumed run therefore harvests family (ii) only from
edges expanded after the resume, so its H′ ≤ H. This is
**sound for a POSITIVE verdict** (H′ = Ḡ ⟹ H = Ḡ ⟹ connected) and
**not sound for a negative one**. Family (i) is *not* affected: the
backfill re-derives it for every already-known class from the
checkpointed masks. Runs record `resumed_from_level` and
`holonomy_is_lower_bound` in `summary.json`.

**Completing pass** (`--holopass <lo> <hi>`), required before any
disconnection claim: re-expands classes [lo,hi) purely to harvest, with
no class discovery. Every mutation must land on an already-known key;
`edges_to_unknown_keys` is counted and reported, so a completed pass over
the whole class list is *also* an independent closure certificate for the
class list (every mutation of every class is a known class), one that
does not go through the mass identity at all.

**Memory work.** Peak RSS is now dominated by the master's key index.
Changes: 6 workers instead of 8; chunks capped at 2000 frontier classes
(the worker's per-chunk Python lists were the largest single allocation);
a bounded submission window of 2·workers outstanding `apply_async` tasks
instead of `imap_unordered` handing out every chunk at once (this also
makes id assignment deterministic, so a from-scratch run is now
reproducible); the per-level "seen" map replaced by sorted packed-key
numpy arrays with an O(N) merge (`merge_sorted`) in place of a bytes-keyed
dict and a full re-sort of the 9.3M-entry index every level; the pending
in-level holonomy buffer bounded at 200k rows with a *counted*
`pend_dropped`; τ bookkeeping and all harvesting short-circuited once
H = Ḡ; vectorized τ composition. `Holonomy.saturate()` — the exact
staged Schreier completion — is now also run at the end of every level
while H ≠ Ḡ, so H reaches Ḡ as soon as it mathematically has rather than
only in post-processing; that is what lets the harvest short-circuit.
Measured on the (9,4) resume: master + 6 workers ≈ 450–600 MB resident,
free physical memory never below 2.1 GB (`data/rss94b.log`).

**Regression canaries for the rework.** (8,4) and (9,3) were re-run
end-to-end with the modified engine, from scratch AND via a forced
resume from a truncated mid-level checkpoint (`truncate_state.py`), all
four runs reproducing the known summaries exactly: 2628 resp. 4382
classes, mass identity hit at 100.0000%, π(H) = S_n, sign part n/n,
H = Ḡ. The five sabotage canaries of `canary_checker.py` are still all
rejected, and `verify_omgamma.py` still passes on the (8,3), (8,4) and
(9,3) certificates.

**Compact certificates** (`export_subcert.py`). Re-verifying
Grassmann–Plücker on 9.3M representatives is neither necessary nor
feasible; what the checker needs is the spanning-tree root-paths of the
classes referenced by holonomy generators (so that it recomputes exactly
the τ the generator identities were built with), plus the generators and
sign exhibits. That set is closed under `parent`, so restricting and
renumbering yields a valid certificate in the checker's own format.
Validated on (9,3), where early saturation makes the generator set tiny:
**56 of 4382 classes and 39 generators suffice to certify H = Ḡ**, and
all of V1–V5 pass under `checker_fast.py`; the five sabotage canaries are
rejected on this certificate too (`canary_checker.py` now takes explicit
paths and handles `.gz`). An earlier, pre-saturation export of the same
result needed 2155 classes / 1044 generators and also passed — two
independent certificates for the same statement.

**The completing pass, executed on (9,3)** as a rehearsal:
`runbig.py 3 9 2 --holopass 0 999999` re-expanded all 4382 classes,
56,473 directed edges, harvesting every one. Results
(`data/big_3_9/holopass_0_4382.json`): `edges_to_unknown_keys = 0` —
i.e. every mutation of every class lands on a class already in the list,
an **independent closure certificate for the (9,3) class list that does
not use the mass identity at all** — and H = Ḡ *exactly* (not a lower
bound). The edge count 56,473 reproduces the in-process engine's
`directed_edge_traversals` for (9,3) to the unit.

`Holonomy.sign_exhibits` was extended at the same time: it now closes the
exhibited sign space under conjugation by the generators (h w h⁻¹ =
(id, π(h)(ε_w)), whose word is just h · word(w) · h⁻¹, re-verified by
explicit composition). Without this the *exhibits* could certify a
strictly smaller space than `saturate()` proves, because saturate's final
P-orbit closure had no word-level counterpart — precisely the situation
at (9,4), where the sign part is reached through the A₉-orbit closure of
the stabilizer generators.

## 7. Trust boundaries

* The standalone certificate checker (`checker.py`, and the vectorized
  `checker_fast.py` with the same semantics) verifies: validity (GP) of
  all listed representatives, every tree edge's mutation identity
  ψ = t·χ_child (as pairs), transports, generator identities, that the
  harvested permutations generate S_n (independent orbit-stabilizer
  chain) and that the exhibited sign words compose to pure-sign elements
  spanning F₂ⁿ (independent Gaussian elimination). It does NOT re-verify
  catalog completeness; completeness rests on the extension sweep + mass
  identity (its own canaries), and on agreement with Finschi/FMM13 counts
  at every level where published numbers exist.
* **What the (9,4) certificate covers.** With `export_subcert.py` the
  emitted certificate lists only the root-path closure of the classes
  referenced by generators, so V1/V2 cover *those* classes, not all
  ~9.3M. That is sufficient for the H = Ḡ claim (Result A) and for
  #components(Γ̄) = #components(Γ̂); it says nothing about coverage.
  Coverage is a separate artifact: the mass identity in
  `data/big_4_9/meta.json` / `summary.json`.
* **The class list's completeness has two independent supports** and they
  should not be conflated: (1) the mass identity against the
  independently computed target N_chi(4,9) from the (8,4) extension
  sweep; (2) optionally, a `--holopass` over the whole class list, whose
  `edges_to_unknown_keys == 0` certifies mutation-closure directly. Only
  (1) has been executed for (9,4).
* **Resumed runs make H a lower bound** for the edge family (ii): sound
  for a positive verdict, not for a negative one. `summary.json` records
  `holonomy_is_lower_bound`.
* `pend_dropped` counts in-level duplicate edges whose holonomy was not
  harvested because the bounded buffer was full; it must be read as part
  of any lower-bound statement (it was 0 in every completed run to date).
* Lemma 3 is proved here but not load-bearing for any computational
  verdict; it is used only as a *prediction* which the computation then
  confirms (Result A is exactly the prediction of Lemma 3's corollary).

## 8. History / errata log

* 2026-07-31 (session 2): **ERRATUM, corrected.** `runbig` phase 2
  harvested only Lemma 2's edge family (ii), never the stabilizer family
  (i). Consequence: the (9,4) sign part read as trivial (1/9) through
  level 8 and the ledger recorded a spurious "local holonomy flatness"
  observation (now retracted, §6). With family (i) backfilled from the
  crashed checkpoint — 2548 flagged classes, 2608 conjugates — the sign
  part is FULL (9/9) and H = Ḡ. Fixed in the engine for both phases;
  regression suite extended to force harvesting through phase 2
  (`phase1cap = 2`).
* 2026-07-31 (session 2): Proposition 4 (sign-part dichotomy) added and
  machine-checked (`submodules.py`); for odd n the labeled component
  count is binary, {2^{n−1}, 1}.
* 2026-07-31 (session 2): the first (9,4) attempt was OOM-killed by the
  OS at level 9 (8 workers, ~2 GB free). `--resume` added
  (`bigstate.py`), with a hard state gate, a 200-class re-canonicalization
  sample check, and an explicit statement of the resumed-holonomy
  lower-bound caveat; memory reworked (bounded submission window, capped
  chunks, numpy in-level dedupe, O(N) index merge, early exact
  saturation). Peak resident ≈ 0.6 GB.
* 2026-07-31 (session 2): `Holonomy.sign_exhibits` extended with the
  conjugation closure, without which the *word-level* certificate could
  fall short of the sign part that `saturate()` proves.
* 2026-07-31: mission-brief attribution corrected (suspected
  counterexample lives in $\overline{\mathcal{G}}$, not $\mathcal{G}$);
  K–M Table 1 typo 482→4382 identified and confirmed by generation.
* 2026-07-31: (4,9) count discrepancy pinned. The dossier:
  - The live database (finschi.com/math/om, "Catalog of Isomorphism
    Classes of Oriented Matroids", non-degenerate filter; archived copy
    in sources/om_49.html) displays **9 276 595** at (4,9) and (5,9).
    Its changelog: "2010 December 21: Added the classes of uniform
    oriented matroids of 9 elements and rank 4 computed by Sonoko
    Moriyama (University of Tokyo) using Lukas Finschi's code."
  - Knauer–Marc Table 1 ("retrieved from om.math.ethz.ch") prints
    **9276595** at (4,9)/(5,9) — consistent with the DB.
  - Fukuda–Miyata–Moriyama, DCG 49 (2013) (arXiv:1204.0645, Table
    labeled existing1: "The numbers of simple oriented matroids ...
    (reorientation class, the numbers enclosed by brackets are those of
    uniform oriented matroids)") prints **(9,276,601)** at both (4,9)
    and (5,9); their reference for the database is [FF] = the same
    homepage ("A database of oriented matroids by Finschi and Fukuda
    [FF] consists of the representatives of the reorientation classes",
    their Sec. on databases). All other entries of their table agree
    with the DB and with our from-scratch counts (in particular (3,9):
    4,382 and (4,8): 2,628).
  - So the two published figures come from the SAME computation lineage
    (Moriyama on Finschi's code), six apart, dual-consistently printed
    in both sources. A Wayback check of the historic ETH pages was
    attempted but the archive API was unreachable from this network.
  - Arbitration by this project: an independent from-scratch count via
    two structurally different sweeps (single-element-extension mass
    identity + mutation-graph BFS) — see Section 6; resolution recorded
    below when the campaign lands.
