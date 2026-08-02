# Certificate cores for pruning realizability completion trees

Research brief for the next oriented-matroid phase. Proposed 2026-08-02.

## Pilot outcome (2026-08-02)

The preregistered raw-core experiment has now been run on a deterministic
64-class sample of the tracked minor-minimal prefix. It **fails the gate**:
the best three emitted cores cover only 6/64 classes, greedy needs 54 cores
for 90%, and training cores cover 2/36 held-out classes. Exhaustive
relabelling is included, and 206 exact realizable controls have zero matches.

A stronger fixed-labelling test searched the *entire common GP system* of all
2,016 class pairs, rather than comparing arbitrary emitted LP supports. Exact
Gordan alternatives show that only one pair has any common BFP; the other
2,015 carry strict integer witnesses. See [`CORE_PILOT.md`](CORE_PILOT.md) and
its independent verifiers.

**Operational update:** do not scale stages 1 and 3 unchanged to the full
minor-minimal corpus. At most one bounded alternative-certificate experiment
combining common-system search with selected relative relabellings is
justified. If it also fails, pivot to the two-sided extension-atlas target.

## Executive decision

**Do not restart or restructure the live \(UOM(4,9)\) sweep.** Let it finish,
freeze its certificate corpus, and use that corpus to test the following
research target:

> **Certificate-core cover problem.** Can the BFP-certified
> non-realizable classes in \(UOM(4,9)\) be covered by a much smaller
> collection of partial Grassmann--Plücker sign patterns, each carrying one
> exact non-realizability certificate? If the completed sweep establishes
> BFP completeness, this target is the entire non-realizable population.

If the answer is strongly positive, those patterns become reusable pruning
clauses for partial-chirotope and single-element-extension trees at
\(UOM(4,10)\) and beyond. If the cores are almost one-to-one with the full
classes, stop: that is a compressed lookup table, not a structural theorem.

The soundness theorem is elementary and finite-checkable. It is also not, by
itself, new. The possible new result is **quantitative compression**: a small
orbit library that exactly covers a very large classified cell.

---

## 1. Why the present mutation tree cannot be pruned wholesale

The distinction below is load-bearing.

| tree | child operation | are the child's constraints a superset? | does a refutation automatically persist? |
|---|---|---:|---:|
| mutation tree | replace one bracket sign by its opposite | no | no |
| partial-chirotope completion tree | replace an unknown sign by \(+\) or \(-\) | yes | yes |
| same-rank element-extension tree | add elements while retaining the old restriction | yes | yes |

Realizable and non-realizable oriented matroids can be mutation neighbours.
Therefore there can be no valid rule of the form “a non-realizable mutation
parent makes all of its tree descendants non-realizable.” The orientation of
a spanning tree is bookkeeping, not mathematical implication.

The exact rule in
[`MUTATION_INHERITANCE.md`](MUTATION_INHERITANCE.md) cuts only the
descendant subforest on which a particular deletion certificate remains
unchanged. The generic support-avoidance rule for a final polynomial has the
same limitation.

For whole-subtree pruning, the search tree must be a **refinement tree**:
descendants add information but never retract information.

---

## 2. The hereditary GP-core theorem

Fix rank \(r\), ground set \(E=[n]\), and the colex bracket coordinates used
by `ai/omreal/bfp.py`. A three-term Grassmann--Plücker relation has signed
terms

\[
T_0=[Lab][Lcd],\qquad
T_1=-[Lac][Lbd],\qquad
T_2=[Lad][Lbc].
\]

For a uniform chirotope, exactly one signed term is opposite to the other
two. Call it the **BIG** term. In any realization its magnitude is the sum
of the other two magnitudes, so for either SMALL term

\[
|T_{\rm BIG}|>|T_{\rm SMALL}|.
\]

Writing \(u_B=\log|[B]|\), this is a strict linear inequality

\[
v\mathbin{\cdot}u>0,\qquad
v=e_p+e_q-e_s-e_t\in\mathbb Z^{\binom nr}.
\]

### Theorem (hereditary GP core)

Let \(P\) be a partial uniform chirotope. Suppose \(P\) forces a finite list
of GP comparisons \(v_i\mathbin{\cdot}u>0\). If positive integers \(w_i\)
satisfy

\[
\sum_i w_i v_i=0,
\]

then:

1. no realizable uniform chirotope completes \(P\);
2. the same certificate refutes every descendant of \(P\) in any
   partial-chirotope completion tree; and
3. the same certificate, embedded by zeros in the new bracket coordinates,
   refutes every same-rank element extension whose restriction completes
   \(P\).

**Proof.** A realization of any completion would give

\[
0=\left(\sum_iw_iv_i\right)\mathbin{\cdot}u
 =\sum_iw_i(v_i\mathbin{\cdot}u)>0,
\]

a contradiction. Descendants retain every forced comparison. A realization
of an element extension restricts to a realization on the old elements, and
the old GP relations are literally still present. \(\square\)

The finite certificate is:

- the selected GP relation indices;
- the required BIG and selected SMALL terms;
- positive integer weights; and
- enough partial sign information to force the named BIG terms.

The checker needs only integer arithmetic after rebuilding the GP rows.

### Reorientation and relabelling

Reorienting any element multiplies all three signed terms of a GP relation
by one common sign, so it does not change which term is BIG. Global sign
also cancels in the bracket products. Relabelling transports relation and
basis indices. Thus a core is naturally considered modulo relabelling;
reorientation does not create a distinct BIG-term signature.

This transport must be implemented and checked explicitly. Do not infer a
mapping from canonical labels without retaining the permutation.

---

## 3. Universal positive-circuit formulation

For fixed \((r,n)\), form a universal integer matrix whose possible rows are

\[
(\text{GP relation},\text{BIG term},\text{SMALL term}).
\]

A full uniform chirotope selects two rows per GP relation: the two
comparisons from its BIG term to its two SMALL terms. Gordan's theorem gives:

> A chirotope has a biquadratic final polynomial exactly when its selected
> row set contains a positive dependence. An inclusion-minimal positive
> dependence is a positive circuit of this universal row configuration.

Every such circuit is therefore a forbidden partial GP signature. This
repackages:

- ordinary BFP certificates;
- lifted deletion certificates;
- support-stable mutation propagation; and
- pruning of partial completions and element extensions.

The current exact reconstruction in `bfp.py` accepts only a unique
normalized positive kernel on the emitted support, so many shipped
certificates are likely already positive circuits. Verify minimality; do not
assume it.

---

## 4. Prior-art boundary

The general pruning principle is established, not a novelty claim.

- Bokowski, Richter and Sturmfels, *Nonrealizability Proofs in Computational
  Geometry*, DCG 5 (1990), introduce final polynomials and explain, via real
  algebraic geometry, the existence of a final polynomial for every
  non-realizable oriented matroid:
  <https://doi.org/10.1007/BF02187794>.
- Firsching, *Realizability and Inscribability for Some Simplicial Spheres
  and Matroid Polytopes*, Section 2.3.3, explicitly runs the BFP LP on a
  **partial chirotope** and observes that infeasibility proves every
  completion non-realizable:
  <https://arxiv.org/abs/1508.02531>.
- Partial-chirotope extendibility is NP-complete; see Baier,
  <https://arxiv.org/abs/math/0504430>. No general small or efficient core
  theorem should be presumed.
- Over the reals there is no finite excluded-minor characterization
  independent of size. Do not advertise a fixed universal obstruction list.

Accordingly, none of these is a publishable new headline:

- “an inconsistent partial system kills its refinements”;
- “a BFP can use a partial chirotope”;
- “every fixed finite cell has some finite obstruction list”; or
- the universal positive-circuit reformulation by itself.

The potential contribution is an **exact, unexpectedly small core cover**
of the previously unclassified \(UOM(4,9)\) cell, together with measured
pruning power on a future extension tree.

---

## 5. Exact target statement

Let \(\mathcal N^{\mathrm{BFP}}_{4,9}\) be the frozen set of
\(UOM(4,9)\) reorientation classes carrying independently checked BFP
certificates. If the completed sweep proves that every non-realizable class
has a BFP, this is the full non-realizable population. Otherwise the
unsettled or differently certified residue is outside the version-1 target
and must be reported separately.

Seek a set \(\mathcal C\) of core orbits such that

\[
\chi\in\mathcal N^{\mathrm{BFP}}_{4,9}
\quad\Longleftrightarrow\quad
\chi\text{ matches a relabelled core }C\in\mathcal C.
\]

Each \(C\) must carry an exact positive-circuit certificate. The reverse
implication is then mathematical soundness; the forward implication is the
finite exhaustive coverage computation.

For a useful result, report at least:

- number of core orbits;
- number of full classes covered by each orbit;
- greedy and, if feasible, exact minimum-cover sizes;
- number of GP relations and distinct brackets per core;
- GF(2) rank of the bracket-sign parity conditions forced by each core;
- coverage of the deletion-witnessed and minor-minimal populations
  separately;
- the depth at which each core fires in a fixed, preregistered completion
  order; and
- actual node reduction and wall time on held-out completion/extension
  searches.

A fixed-\((4,9)\) “iff” with nearly one core per class has no structural
content. Compression and early triggering are the result.

---

## 6. Experimental program

### Stage 0 — freeze inputs

Do not consume moving sweep shards for a final claim.

1. Let the live sweep finish.
2. Freeze and hash the complete class catalogue, verdict file, certificate
   shards and checker version.
3. Re-run `checkcert.py` on every claimed certificate.
4. Record residue separately. A failure to find a BFP is **OPEN**, never
   realizable.

A pilot may use a frozen prefix, but its numbers must be labelled as pilot
numbers and must not appear as final-cell claims.

### Stage 1 — extract exact cores

For every BFP certificate:

1. rebuild each GP comparison independently from the class sign string;
2. verify the named BIG term and the exact identity
   \(\sum_iw_iv_i=0\);
3. merge duplicate \((\text{relation},\text{BIG})\) conditions;
4. test whether the weighted row support is an inclusion-minimal positive
   dependence; and
5. record the distinct bracket support and parity-condition rank.

Suggested version-1 record:

```json
{
  "core_id": "...",
  "r": 4,
  "n": 9,
  "conditions": [{"relation": 17, "big": 2}],
  "terms": [{"relation": 17, "big": 2, "small": 0, "weight": 3}],
  "source_class": {"key_hi": 0, "key_lo": 0}
}
```

The conditions determine where the certificate applies; the weighted terms
prove infeasibility.

### Stage 2 — search for smaller and broader cores

The LP currently returns one extreme certificate, not necessarily the
certificate with greatest cross-class coverage.

Try, in this order:

1. inclusion-minimality of the shipped support;
2. iterative row deletion with exact reconstruction;
3. reweighted LPs favouring fewer distinct GP relations;
4. a small MILP minimizing activated relations, only if the cheaper stages
   show a plausible payoff; and
5. empirical objectives favouring BIG-term conditions frequent in the
   non-realizable corpus.

Every candidate found numerically must be reconstructed and verified over
the integers before it enters the library.

Do not optimize solely for few weighted rows. Minimize the information that
a partial tree must know before the core fires: distinct BIG conditions,
distinct brackets and parity rank.

### Stage 3 — canonicalize and measure coverage

A full class matches a core when every relation named by the core has the
required BIG term. Then the identical weighted certificate applies.

1. First measure literal labelled reuse.
2. Canonicalize core signatures under \(S_9\).
3. Retain the explicit permutation transporting each matched class to the
   canonical core.
4. Build the class-to-core incidence relation.
5. compute a greedy orbit cover and its coverage curve;
6. run separate statistics for deletion-witnessed and minor-minimal
   classes; and
7. test every core against certified realizable controls. A match is a
   blocking bug because a sound core cannot match a realization.

Avoid materializing a \(3780\times9{,}276{,}595\) dense incidence table.
Batch classes, pack BIG-term values, and store only matches or bitsets for
the non-realizable corpus.

### Stage 4 — independent finite coverage certificate

Ship:

- one canonical exact certificate per core orbit;
- for every covered full class, a pointer
  \((\text{core id},\text{element permutation})\);
- the frozen catalogue hashes; and
- a standalone checker sharing no GP-row or permutation code with the
  producer.

The checker must:

1. rebuild colex bases and GP relations from definitions;
2. verify every positive dependence exactly;
3. transport each core using the recorded permutation;
4. recompute the matched class's BIG terms;
5. verify every class in the declared BFP-covered corpus has a valid pointer;
6. detect missing and duplicate catalogue keys; and
7. reject any pointer attached to a nonmatching class.

The pointer list is itself a finite coverage certificate. It is much cheaper
to verify than to rediscover the cores.

### Stage 5 — test actual subtree pruning

Build or adapt a canonical partial-chirotope completion harness. A core may
fire when its BIG conditions are logically forced, even if not every
individual bracket sign has been assigned.

Preregister at least two sign orders:

- a neutral fixed colex order; and
- a core-aware order learned on a training split.

Evaluate on held-out classes or extension branches. Report nodes visited,
cores triggered, trigger depth, time spent matching, and net wall-time
saving. Comparing only certificate counts is insufficient.

Only after the fixed-cell experiment succeeds should the core matcher be
inserted into a \(UOM(4,10)\) single-element-extension search.

---

## 7. Required canaries

At minimum, the independent checker must reject:

1. one altered positive weight;
2. one changed BIG term;
3. one dropped weighted row;
4. a core transplanted to a nonmatching class;
5. a corrupted element permutation;
6. a duplicate class pointer masking a missing class;
7. a valid certificate attached to the wrong catalogue key; and
8. a deliberately feasible GP-log system presented as infeasible.

Positive controls should include:

- a lifted certificate from each of several known non-realizable
  \(UOM(4,8)\) deletions;
- a minor-minimal \(UOM(4,9)\) BFP; and
- the same core transported through nontrivial relabellings and
  reorientations.

The reorientation control should leave the BIG signature unchanged; the
relabelled control should change indices exactly as predicted.

---

## 8. Go/no-go criteria

Run a bounded pilot before building an elaborate canonicalizer or
completion engine.

**Continue** if the measured result resembles either of these:

- a small fraction of core orbits covers most of
  \(\mathcal N^{\mathrm{BFP}}_{4,9}\); or
- cores trigger early enough that the completion-tree node count falls by
  orders of magnitude, even if the orbit library is not tiny.

**Stop or rescope** if:

- median core coverage is one or a handful of full classes;
- covering 90% of the minor-minimal population requires nearly one core per
  class;
- cores become recognizable only after almost all 126 bracket signs are
  fixed; or
- matching and canonicalization cost more than the LPs or branches saved.

A useful preregistered pilot gate is:

> Pursue the full project only if at most 5% as many core orbits as pilot
> non-realizable classes cover at least 90% of that pilot, **or** the
> held-out completion tree visits at most 10% of its baseline nodes.

The numerical threshold is a project-management gate, not a mathematical
claim. Record it before seeing the pilot result.

---

## 9. Evidence setting the prior

The current checked-in prefix warns against optimism:

- about 90.7% of certified non-realizable \(UOM(4,9)\) classes have one of
  the 24 non-realizable \(UOM(4,8)\) deletions;
- the remaining population is minor-minimal, generic and mostly
  minimum-symmetry;
- sampled minor-minimal BFPs use about 73.5 weighted terms on average,
  versus 61.7 for deletion-witnessed controls; and
- the minor-minimal population shows no small deletion template in the
  measurements in [`MINOR_THEORY.md`](MINOR_THEORY.md).

Thus a small library for the easy 91% is already known: the 24 deletion
obstructions. The experiment earns its keep only if partial cores compress
the hard minor-minimal remainder or fire substantially earlier than full
minor identification.

The live \(UOM(4,9)\) sweep invokes BFP on only about 1% of all classes in
the measured prefix. This project is not expected to save the current run.
Its intended payoff is structural compression and future \(n\geq10\)
pruning.

---

## 10. Higher-degree fallback

If a final residue has no BFP, do not force it into this library. The
general real-algebraic result says that some final polynomial exists for a
non-realizable finite sign system, but useful degree and coefficient bounds
are not supplied.

A later hierarchy could use:

1. BFP/Gordan cores;
2. higher-degree final-polynomial cores; and
3. Positivstellensatz or proof-producing SMT cores.

Each level has the same hereditary pruning theorem: a finite refutation of
a partial constraint set refutes every refinement. Discovery cost and
certificate size may, however, be prohibitive. Do not start the
higher-degree project unless the completed sweep produces genuine residue
or the BFP-core pilot demonstrates strong compression.

---

## 11. Claims this project must not make

- A mutation-tree descendant is not certified merely because its parent is
  non-realizable.
- Failure to match a core is not evidence of realizability.
- Failure to find a BFP is not evidence of realizability.
- A finite cover at \((4,9)\) is not a finite excluded-obstruction theorem
  for all sizes.
- The hereditary theorem and use of partial-chirotope BFPs are not new.
- A large list of nearly full class signatures is not a generating
  structure.
- Pilot prefix percentages are not final catalogue percentages.
- A greedy set cover is not a minimum set cover unless independently proved.

---

## 12. Deliverables if the pilot passes

1. `CORE_THEORY.md`: definitions, theorem, prior art and final statistics.
2. `extract_cores.py`: producer, explicitly non-authoritative.
3. `cores.jsonl.gz`: canonical exact core certificates.
4. `coverage.jsonl.gz`: class-to-core pointers and permutations.
5. `checkcores.py`: standalone standard-library checker.
6. `completion_benchmark.py`: preregistered baseline and core-pruned runs.
7. `MANIFEST.json`: hashes, counts, environment and commands.
8. adversarial review with deliberately failing canaries.
9. a concise paper section only if the compression or pruning gate passes.

## Instruction to the next research agent

Start with the smallest honest experiment:

1. read `ai/omreal/bfp.py`,
   [`MUTATION_INHERITANCE.md`](MUTATION_INHERITANCE.md), and
   [`MINOR_THEORY.md`](MINOR_THEORY.md);
2. take a frozen, independently checked sample of BFP certificates;
3. extract their exact BIG-term cores;
4. compute cross-class coverage without optimizing the certificates;
5. report the coverage distribution and the preregistered go/no-go verdict;
6. write no headline theorem until that measurement is known.

The first question is not “can a core prune a tree?” It can. The first
research question is:

> **Does this corpus contain reusable cores, or nearly one private
> explanation per non-realizable class?**
