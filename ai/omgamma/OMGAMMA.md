# OMGAMMA — connectivity of the mutation graphs of uniform oriented matroids, n ≤ 9

Slow-lane program note. Started 2026-07-31. Status: **MAIN QUESTION
SETTLED** (2026-07-31) — Γ̄^{n,r}, Γ̃^{n,r} and Γ̂^{n,r} are connected for
every n ≤ 9 and every r, so there is no counterexample to the
Cordovil–Las Vergnas conjecture, at any of its three levels, below
n = 10. The final open case (9,4)/(9,5) is in §6.
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

**Status of that check (2026-07-31).** Lemma 3's corollary predicts
exactly #components(Γ̄^{n,r}) = #components(Γ̂^{n,r}) whenever Γ̂ is
connected — equivalently H = Ḡ. That prediction has now been confirmed
by direct holonomy computation at every (n,r) with n ≤ 9 that the
project has reached, *including* the hardest case (9,4) (§6, Result A),
where a period of apparent disagreement turned out to be an engine bug
rather than mathematics. The lemma is still not load-bearing; it is now,
however, a hypothesis that has survived a serious attempt to break it.

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
| (9,4) | **9,276,595** ✓mass | yes (mass identity, 100.0000%) | yes (362880) ✓cert | yes (9/9, exact) ✓cert | **Γ̄(9,4), Γ̃(9,4) connected** — NEW; settles the level Knauer–Marc suspected |
| (9,5) | ≅ (9,4) by duality | yes | yes | yes | **Γ̄(9,5), Γ̃(9,5) connected** |
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

### RESULT (2026-07-31): (9,4) SETTLED — all three graphs connected

The coverage sweep completed. `data/big_4_9/summary.json`:

```
 classes                 9,276,595
 complete_by_mass        true     (accumulated mass == N_chi(4,9) exactly)
 H_equals_Gbar           true     (pi 362880/362880, sign 9/9, exact)
 gamma_hat_connected     true
 gamma_bar_connected     true
 gamma_tilde_connected   true
 edges_expanded          150,561,898 directed mutation-edge traversals
 levels                  19 (BFS eccentricity of the alternating class)
```

**Verdict.** Γ̂^{9,4}, Γ̃^{9,4} and Γ̄^{9,4} are all **CONNECTED**; every
one of them has exactly one component. By the duality proposition (§5)
the same holds for (9,5). Combined with the earlier rows of the §5 table
and the rank/corank coverage list, this closes n ≤ 9 for **all three
graphs at every rank**: the labeled graph
$\overline{\mathcal{G}}^{n,r}$ — the level where Knauer–Marc "suspect the
existence of a counter example" — is connected for every n ≤ 9 and every
r. No counterexample exists below n = 10.

**The (4,9) class count is 9,276,595.** The discrepancy in the
literature is resolved in favour of Finschi's database and Knauer–Marc's
Table 1; Fukuda–Miyata–Moriyama's **9,276,601** (DCG 49 (2013), Table
"existing1", at both (4,9) and (5,9)) is **six too many**. The reason is
an exact integer identity, not agreement with either source:

    sum over the 9,276,595 found classes of |G'_9| / |Stab(chi_c)|
      = 1,722,704,635,330,560
      = N_chi(4,9), computed independently by the single-element
        extension sweep over the 2,628 classes of (8,4)

so the class list is provably exhaustive (any missing class would leave
the sum short by at least |Ḡ|/|Stab| > 0, and the sum can never
overshoot). **That identity is the whole discriminator.** The rational
decomposition below is not a second independent witness — it is
arithmetic on the same stabilizer array, recomputed from the checkpoints
by `stabstats.py` rather than from the engine's running counter — but it
is what makes the six-class gap legible:

    Σ_c 1/nstates_c = N_chi/(|G'_9|/2) = 166,897,693/18   (forced by the target)
    Σ_c (1 − 1/nstates_c)             =      81,017/18    (measured)
    #classes = (166,897,693 + 81,017)/18 = 166,978,710/18 = 9,276,595 ✓

and 9,276,601 would have required Σ(1 − 1/nstates) = 81,125/18. Of the
9,276,595 classes, **8,913 have a nontrivial Ḡ-stabilizer**; the
stabilizer-order histogram is in `stabstats.json`.

**Second, independent support for the class list** (does not use the mass
identity at all): a completing pass over a mid-range slice far from the
symmetric root, `runbig.py 4 9 8 --holopass 5000000 5150000`
(`data/big_4_9/holopass_5000000_5150000.json`) re-expanded 150,000
classes and all **2,499,128** of their directed mutation edges, and
**every single one landed on a key already in the class list**
(`edges_to_unknown_keys: 0`, `closure_certified: true`). It also
re-derived H = Ḡ *exactly* on that region — every edge harvested, no
lower-bound caveat, π 362880/362880 and sign 9/9. A missing class
adjacent to that slice would have shown up here.

**Certificates emitted from the completed sweep.** `finish94.sh` exports
a second compact certificate from the sweep's own generators (as opposed
to `certify.py`'s, built at level 9): **561 classes, 75 generators**,
V1–V5 pass under `checker_fast.py`, five sabotage canaries rejected
(`data/big_4_9/subcertB_*`). Both (9,4) certificates are now required
artifacts of `verify_omgamma.py`, which passes.

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
  Both halves are independently confirmed on the shipped certificate,
  whose 74 generators are 73 stabilizer conjugates + 1 edge voltage:
  `checker.py`'s from-scratch orbit-stabilizer chain gives
  order⟨perm parts of the 73⟩ = 181,440 = |A₉| (and all 73 are even
  permutations, 0 odd), while adding the single edge generator — an odd
  permutation — gives 362,880 = |S₉|. A₉ is the unique index-2 subgroup
  of S₉, so "order 181,440" and "all generators even" are the same fact.
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

**Exactly what the resume does and does not cost here.** A resumed run
harvests the edge family only from levels expanded after the resume, so
its H′ is a LOWER bound: H′ ≤ H ≤ Ḡ. Since H′ = Ḡ was reached, H = Ḡ
outright — a lower bound that equals the whole group *is* the whole
group. So the positive verdict is sound despite the resume, and **no
completing pass over the earlier levels is needed**. (`--holopass` would
be mandatory only for a NEGATIVE verdict, where a lower bound proves
nothing.) What the resume does not supply, and what H = Ḡ alone does not
supply, is **Γ̂-connectivity**: Lemma 1 requires the quotient to be
connected before [Ḡ : H] = 1 can be read as "Γ̄ connected". That is the
mass identity's job and nothing else's. Precisely:

    certified now :  H = Ḡ
    Lemma 1       :  #comp(Γ̄) = #comp(Γ̂)   and   #comp(Γ̃) = #comp(Γ̂)
    still needed  :  #comp(Γ̂^{9,4}) = 1, i.e. accumulated mass = N_chi(4,9)
    ⟹ Γ̄, Γ̃, Γ̂ all connected at (9,4).

**The dichotomy makes the observation a proof.** The run's sign
dimension went 1 → 9 with no intermediate value ever appearing. That is
not luck and not evidence in itself: Proposition 4 (§3, machine-checked
in `artifacts/submodules.json`) shows that for n = 9 the only
S₉-invariant subspaces of F₂⁹ containing 1⁹ are ⟨1⁹⟩ (dim 1) and F₂⁹
(dim 9), so **1 and 9 were the only values the sign dimension could ever
have taken** once π(H) = S₉, and correspondingly #components(Γ̄^{9,4})
could only ever have been 256 or 1. The computation picked out which.

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

**Certificate for Result A** (`certify.py` → `export_subcert.py` →
`checker_fast.py`; artifacts `data/big_4_9/certA_dir/{holonomy,gens,
exhibits}` and `data/big_4_9/subcert_*`). Built from the level-9
checkpoint (3,037,250 classes), *without* waiting for the sweep:
family (i) = 3508 stabilizer conjugates over the 3386 flagged classes →
π = A₉, sign 9/9 after exact saturation; family (ii) = expanding 16
classes starting at id 600,000 → 232 edge voltages, of which the ones
that matter complete π to S₉. The packaged certificate is

    547 classes,  546 tree mutation edges,  74 generators,
    V1–V5 all PASS under BOTH checkers:
      checker_fast.py (numpy)      -- data/big_4_9/subcert_*
      checker.py      (pure python, separate implementation of the
                       GP axiom, the group action, the group-order
                       computation and the word evaluation)

— i.e. **a 547-class artifact proves H = Ḡ for (9,4)**, with V4 (S₉ by an
orbit-stabilizer chain written from scratch) and V5 (the sign words
re-evaluated and Gaussian-eliminated) checked by code sharing nothing
with the generator, in two independent implementations that agree. The
five sabotage canaries are rejected on this certificate.
(Caveat on reading `checker.py`'s closing message: it prints the
connectivity conclusion *given* class-list completeness. The certificate
itself proves H = Ḡ; Γ̂-connectivity is the separate mass-identity
artifact.) This settles the labeled question modulo Γ̂-connectivity and
is independent of the coverage sweep completing.

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

### RESTART RECIPE (if the sweep is interrupted again)

The **only** state needed is `data/big_4_9/level_*.npz` + `meta.json`
(and `data/mass_target_4_9.json`). Everything else is derived.

```
cd .../ai/omgamma
# 1. if a level_XXX.npz exists that meta.json does not know about
#    (crash between the two writes), delete that trailing file.
python -c "import json;print(json.load(open('data/big_4_9/meta.json')))"
ls data/big_4_9/level_*.npz | tail -2
# 2. relaunch detached (workers: 6 is safe on 16 GB, 10 if idle)
powershell -File launch94.ps1 -Workers 6         # runs runbig.py 4 9 6 --resume
# 3. the certificate does NOT depend on the sweep finishing:
python certify.py 4 9 3000 "" 600000             # -> data/big_4_9/certA_dir/
python export_subcert.py 4 9 "" data/big_4_9/certA_dir
python checker_fast.py 9 4 data/big_4_9/subcert_reps.txt.gz \
    data/big_4_9/subcert_tree.txt.gz data/big_4_9/subcert_gens.txt \
    data/big_4_9/subcert_exhibits.txt
# 4. when the sweep does finish:
powershell -File finish94.ps1
```

The resume is gated (§ above): if any of the class count, the total mass,
the level-file contiguity, the `ids` contiguity or the 200-class
re-canonicalization sample disagrees with `meta.json`, it aborts instead
of continuing from a damaged state. `canary_resume.py` demonstrates that
the gate actually fires on six corruption modes.

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

### 6.x The coverage certificate (`export_coverage.py`, `coverage_checker.py`)

The compact certificates above prove H = Ḡ; they say nothing about
coverage, and until 2026-07-31 the *left-hand side* of the mass identity —
the list of 9,276,595 canonical keys with their stabilizer orders — existed
only as the ~326 MB of gitignored `level_*.npz` checkpoints. A reader could
not check that the list consists of that many distinct valid classes with
the asserted stabilizers. That was the single most serious finding of the
GPT referee report on the note (`paper/REVIEW_note_gpt.md`, finding 3).

**The artifact.** `export_coverage.py 4 9 data/big_4_9 data/coverage_4_9`
transports the `keys`/`stab` columns out of the checkpoints, sorts them
strictly increasingly by the 126-bit key, and writes

```
data/coverage_4_9/coverage_4_9.npz    key_hi, key_lo (uint64), stab (uint8)
data/coverage_4_9/MANIFEST.json       conventions, totals, SHA-256s
```

62.2 MB, readable with `np.load` and nothing else. The manifest records n,
r, the basis order, the key bit-encoding, the group and its action, the
**exact canonical convention** (see below), the count, the mass, the
stabilizer histogram, three fully worked example rows (row 0 as a 126-char
± string), the SHA-256 of the `.npz` and, separately, of each array's raw
little-endian buffer, so the hashes survive repacking of the zip container.
The `.npz` is gitignored; `MANIFEST.json` is tracked, so a downloaded or
regenerated copy can be pinned against the repository.

**The checker.** `coverage_checker.py` imports nothing from this project —
no `core`, `canon`, `flip`, `runbig`, `bigstate`, `ext_count`, `checker*`.
It rebuilds the colex basis order, the 1,260 three-term Grassmann–Plücker
conditions, the sign lattice (reduced row echelon over F₂, rank 9, κ = 1)
and the group action from the definitions. It verifies

* (0) every SHA-256 in the manifest, file and per-array;
* (a) every key decodes to a valid uniform chirotope;
* (b) every key is **extremal in its own orbit under the manifest's
  convention** — see the caveat below;
* (c) the keys are strictly increasing, hence sorted *and* pairwise
  distinct (one expression; these are not two independent checks);
* (d) every recorded stabilizer order equals |Stab_{G′}(χ)| recomputed by
  exhaustive enumeration;
* (e) the orbit masses sum to 1,722,704,635,330,560 and the count is
  9,276,595;
* (f) optional, `--extcount`: the tracked 2,628-row extension table sums
  arithmetically to that same target.

**How (b) and (d) are done, and why this is not just canon.py again.**
`canon.py` finds the canonical key by a level-by-level DFS that *prunes*
to the states achieving the maximal prefix. The checker does not reproduce
that search. It computes the invariant element colouring, orders the colour
classes, and then **enumerates every admissible relabelling exhaustively**
(∏_c m_c!: exactly 1 for 93.1% of classes on a 300,000-row sample, 2.43 per
class on average over the whole catalog — the mean is dragged up by a thin
tail ending at the alternating matroid's 362,880), sign-maximises each
image over the full sign lattice, and takes the maximum and the argmax
count. So the checker verifies the *result* of canon.py's pruning by brute
force rather than re-deriving the pruning, and |Stab| = 2^κ · #argmax comes
out of the same enumeration. Two independent agreements were checked while
building it: the colour *partitions* agree with `canon.element_colors` on
2,000/2,000 sampled classes, and a slow reference implementation reproduced
both the stored key and the stored stabilizer order on 5,000/5,000 classes
drawn from all 20 BFS levels.

**The caveat that must not be dropped.** The keys are *not* the maximum
over all of S_n. `canonical()` maximises only over relabellings respecting
the invariant colouring, so the convention is colour-restricted. This was
measured, not assumed: on sampled classes the unrestricted maximum differs
from the stored key in 8 of 9 cases, and computing it costs ~1.5 s/class,
i.e. ~160 CPU-days over the catalog. The colour-restricted maximum is still
a well-defined function of the G′-orbit (the colouring is invariant under
reorientation and global negation and equivariant under relabelling), which
is all the distinctness argument needs — but the reader has to read the
forty lines of `canonical_convention()` rather than accept the word
"canonical". The manifest and the note both say so.

**Canaries** (`--canary`). Six sabotages of a 20,000-row sub-artifact, each
shipped with a **regenerated, internally consistent manifest** — i.e. an
adversary who can rewrite the hashes — plus an untampered control that must
pass. Where the sabotage would otherwise be caught by arithmetic, the
totals are repaired so that only the mathematical check can fire:

| canary | fires on |
|---|---|
| control, untampered | *accepted* (as required) |
| duplicated key (kept sorted, totals repaired) | (c) |
| non-canonical key (another representative of the same orbit) | (b), and (d) |
| corrupted stabilizer order (manifest mass repaired) | (d) |
| GP-invalid key (a **non-mutable** basis flipped) | (a), and (b),(d) |
| truncated artifact, 500 rows dropped | (e) |
| stale SHA-256, data changed | (0) |

All seven behave as required.

**Run of record (2026-07-31).** FULL, not sampled: all 9,276,595 rows,
4 worker processes, 93 shards of 100,000, **510 s wall / ~26 min CPU**,
22,544,370 admissible relabellings enumerated. `18 checks passed, 0
failed` — (0),(a),(b),(c),(d),(e),(f) all green
(`data/coverage_full.log`). The cost is very unevenly distributed: shards
0–91 took 14–19 s each and the last shard, 76,595 rows, took 174 s, because
the artifact is sorted by key and the largest keys are the most symmetric
classes. `--sample N` runs (a),(b),(d) on a seeded pseudorandom subset;
`--cheap-only` skips them; shards are checkpointed into `--state` and a
re-run skips finished ones.

**What this still does not certify.** The checker takes the target
1,722,704,635,330,560 as an input constant. Check (f) confirms that the
tracked extension table adds up to it; nothing here recomputes the 2,628
extension counts E(c) themselves, and nothing here re-derives the (8,4)
catalog they are taken over. The right-hand side of the mass identity
remains reproducible-only.

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
  `data/big_4_9/meta.json` / `summary.json`, whose left-hand side is now
  itself certified by `data/coverage_4_9/` + `coverage_checker.py` (§6.x).
* **The class list's completeness has two independent supports** and they
  should not be conflated: (1) the mass identity against the
  independently computed target N_chi(4,9) from the (8,4) extension
  sweep — executed, exact; (2) a `--holopass`, whose
  `edges_to_unknown_keys == 0` certifies mutation-closure directly —
  executed for (9,3) over the WHOLE class list, and for (9,4) over a
  150,000-class mid-range slice (2,499,128 edges) only, not the whole
  9.28M. A full (9,4) closure pass would cost another ~150M
  canonicalizations (~5 h at 10 workers) and is the obvious next
  hardening step; it is not needed for the verdict, since (1) is an
  exact identity.
* The mass identity's inputs are `canon.py`'s exact stabilizer orders
  (`stab_order_exact`) and the extension-count sweep `ext_count.py`.
  **As of 2026-07-31 the first is re-derived by a standalone checker and
  the second is not.** `coverage_checker.py` (§6.x) recomputes, from the
  shipped artifact and with no project imports, the validity, the
  orbit-extremality and the stabilizer order of every one of the
  9,276,595 classes, and re-adds the masses; so the LEFT-hand side of the
  identity is now certificate-backed, conditional on the manifest's
  colour-restricted canonical convention (which is stated there in full,
  and is a well-defined function of the orbit — the point the distinctness
  argument actually needs). The RIGHT-hand side is not: the target
  1,722,704,635,330,560 enters the checker as a constant, and `--extcount`
  only confirms that the tracked 2,628-row table sums to it. What still
  mitigates the right-hand side: the same machinery reproduces every
  published count where one exists ((3,5..9), (4,5..8)), and the same mass
  identity closes exactly at (8,4) and (9,3), where the class lists are
  independently confirmed against Finschi's representatives.
* **Resumed runs make H a lower bound** for the edge family (ii): sound
  for a positive verdict, not for a negative one. `summary.json` records
  `holonomy_is_lower_bound`.
* **Do not read `stab_gens` / `edge_gens` in a finished `summary.json` as
  totals.** Both counters live inside the `if not hol.full():` guard, so
  they freeze the moment H reaches Ḡ (during level 10 of the (9,4)
  sweep). The number of classes with a nontrivial Ḡ-stabilizer must be
  taken from the `stab` arrays of the checkpoints — `stabstats.py` does
  exactly that, and also re-derives the mass identity independently of
  the engine's running total (it agrees at (8,4): 2628 classes, 243 with
  nontrivial Ḡ-stabilizer, mass 25,703,946,240 = target).
* `pend_dropped` counts in-level duplicate edges whose holonomy was not
  harvested because the bounded buffer was full; it must be read as part
  of any lower-bound statement. It was 0 in every (8,4)/(9,3) run, and
  **5,865,152 at level 9 of the (9,4) sweep** — which does not weaken
  anything, because H had already reached Ḡ during that level and all
  harvesting (including the buffer) is a no-op from that point on. It
  would matter only for a *negative* verdict, which is exactly the case
  `--holopass` exists for.
* Lemma 3 is proved here but not load-bearing for any computational
  verdict; it is used only as a *prediction* which the computation then
  confirms (Result A is exactly the prediction of Lemma 3's corollary).

## 8. History / errata log

* 2026-07-31 (session 3): **coverage gap closed on the left-hand side.**
  The GPT referee report on the note (`paper/REVIEW_note_gpt.md`, finding 3
  and "Single most important fix") established that the headline count and
  the coverage claim were NOT publicly certificate-backed: the repository
  shipped only the compact holonomy certificates, while the list of
  9,276,595 keys + stabilizers lived in ~326 MB of gitignored checkpoints.
  Now: `data/coverage_4_9/` (62.2 MB `.npz` + tracked `MANIFEST.json`) and
  `coverage_checker.py`, a checker with no project imports, run FULL over
  all 9,276,595 rows — validity, orbit-extremality, strict sortedness,
  exact stabilizer orders, mass, and the extension table's arithmetic —
  510 s wall on 4 workers, 18/18 checks green, and 6 sabotages (each with a
  regenerated self-consistent manifest) plus an untampered control all
  behaving as required. **The right-hand side of the mass identity is still
  not certified**: the target enters the checker as a constant, and
  `--extcount` only re-adds the tracked table. Also recorded, because it
  is easy to overstate: the stored keys are extremal under a
  *colour-restricted* convention, not under all of S_n (measured: the
  unrestricted maximum differs on 8 of 9 sampled classes and would cost
  ~160 CPU-days).
* 2026-07-31 (session 2): **(9,4) SETTLED.** 9,276,595 classes,
  150,561,898 directed mutation-edge traversals, 19 BFS levels, mass
  identity exact, H = Ḡ. Γ̄, Γ̃, Γ̂ connected at (9,4) and hence at
  (9,5); n ≤ 9 is now closed at all three levels of the hierarchy, with
  no counterexample. The (4,9) count discrepancy resolved to 9,276,595.
* 2026-07-31 (session 2): **verify_omgamma.py defect fixed (SERIOUS).**
  It treated a MISSING certificate as "SKIP" and still exited 0, so a
  contributor could delete the headline artifacts and CI would stay
  green. The expected certificates are now an explicit manifest;
  required artifacts are checked for existence/readability/non-emptiness
  before any checker runs and a missing one is a loud named FAILURE;
  optional artifacts are declared as such and every skip prints its
  reason; `--canary` self-tests deletion, renaming and emptying of a
  required artifact (all three now rejected).
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
  - **RESOLVED 2026-07-31: the count is 9,276,595** (Finschi's DB and
    K–M Table 1 are right; FMM13's 9,276,601 is six too many). Settled
    by an independent from-scratch count via two structurally different
    sweeps whose results are compared by an exact integer identity: the
    single-element-extension mass target N_chi(4,9) =
    1,722,704,635,330,560 computed from the 2,628 classes of (8,4), and
    the orbit-stabilizer mass accumulated over the 9,276,595 classes
    found by the mutation-graph BFS — equal on the nose (§6). We do not
    know which of the six is spurious in FMM13's table, only that their
    figure cannot be the number of isomorphism classes; note their entry
    and the database entry agree everywhere else, including (3,9) = 4,382
    and (4,8) = 2,628, both of which we also reproduce from scratch.
