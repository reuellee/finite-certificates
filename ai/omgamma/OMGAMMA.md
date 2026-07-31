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
| tiny  | (5,2),(5,3),(5,4),(6,2),(6,3),(6,4) | yes | yes | yes | connected & brute-force-equal |

Both (8,4) and (9,3) were re-run through the parallel disk-based engine
(runbig.py) with mass-formula termination: the accumulated
orbit-stabilizer mass hit the independently computed target
N_chi exactly (100.0000%), certifying catalog completeness AND
Γ̂-connectivity simultaneously. Γ̂(8,4) has 15,338 directed mutation-edge
traversals from class representatives (avg mutation degree ≈ 11.7).

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
known-hits, deferred for in-level duplicates with a 500k cap), so if the
run terminates by mass with H < Ḡ, the harvested H is a lower bound with
provenance sufficient to investigate; if it terminates with H = Ḡ, the
positive verdicts are certificate-backed. The final saturation is the
exact staged Schreier computation.

### Empirical observation: local holonomy flatness at (9,4)

Phase-1 diagnostic (2026-07-31): a BFS ball of 4000 classes / 18,091
directed edges around the alternating class of (9,4) harvested 14,092
non-tree loop voltages, yet the holonomy subgroup they generate (with the
root stabilizer) has permutation part of order just 18 (= the dihedral
symmetry of the alternating OM) and sign part = kernel only. In other
words, every loop in that ball is voltage-trivializable: the covering
Γ̄ → Γ̂ is locally "flat" near the alternating class at a scale (4000
classes) at which (8,4) had already saturated to the full group (800
classes sufficed there). This is a concrete structural sense in which
the labeled question at (9,4) is delicate, consistent with Knauer–Marc's
caution; the full-edge harvest in the main run decides it.

## 7. Trust boundaries

* The standalone certificate checker (checker.py, forthcoming) verifies:
  validity (GP) of all representatives, every tree edge's mutation
  identity ψ = t·χ_child (as pairs), transports, generator identities,
  and that the harvested permutations generate S_n (independent BFS over
  S_n) and the sign space is full (independent Gaussian elimination). It
  does NOT re-verify catalog completeness; completeness rests on the
  extension sweep + mass identity (its own canaries), and on agreement
  with Finschi/FMM13 counts at every level where published numbers
  exist.
* Lemma 3 is proved here but not load-bearing for any computational
  verdict.

## 8. History / errata log

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
