# Does realizability transport along the mutation tree?

Written argument, 2026-08-01. Companion to `SCOPING.md`; this file is the
theory, that one is the measurements.

**Short answer.** No — and the proof is two lines from omgamma's own
connectivity theorem. But the *correct* statement in the neighbourhood of
the idea is true, is already in the repository, and is strong enough that
the (4,9) cell looks closable on a laptop overnight with no cloud spend at
all. What follows is the argument, what it does and does not license, and
the one gap that a new idea would have to fill.

---

## 1. The question

`witness_4_9.npz` gives every one of the 9 276 595 classes a parent, a
mutated basis `flip[i]`, and a group element g with

```
g . chi_i  =  mu_{B_flip[i]} ( chi_parent[i] )                (*)
```

A mutation is geometrically one point crossing one hyperplane. So: if the
parent is realizable, can its realization always be transported across
that wall to a realization of the child? If yes, realizability would
propagate along the tree by construction and **every class reachable from
a realizable root would be realizable** — which would settle the
realizable side outright, with no sweep.

---

## 2. It cannot. Proof.

> **Proposition 1.** There are realizable uniform rank-4 chirotopes on 9
> elements with a mutable basis j such that mu_j(chi) is *not* realizable.
> Equivalently: realizability is not a mutation invariant, so no
> transport argument can be unconditional.

*Proof.* Realizability is invariant under G' = S_n x {0,1}^n x {0,1}
(relabelling permutes columns, reorientation negates them, the global sign
negates a row), so it is a well-defined property of a class.

Suppose, for contradiction, that mu_j(chi) is realizable whenever chi is
realizable and j is mutable. Then the realizable classes are closed under
mutation, so they are a union of connected components of the mutation
graph on classes.

omgamma settled that this graph is **connected** at (9,4) — that is
Result A of `OMGAMMA.md`, certified by `tree_4_9.npz`. And at least one
class is realizable (the chirotope of any random integer 4x9 matrix; we
exhibit thousands). Hence *every* one of the 9 276 595 classes would be
realizable.

But non-realizable classes exist. Bokowski & Richter (1990) exhibit all 24
non-realizable uniform (4,8) classes, and any 9-element class having one
of those as an 8-element deletion is itself non-realizable — the GP
relations of a deletion are a subset of the class's, so a biquadratic
final polynomial for the deletion is one for the class. We produce **225
such classes with explicit Gordan vectors** in a 10 000-class sample
(§5), and of 25 examined, 23 do have a non-realizable deletion.
Contradiction. ∎

Two consequences worth stating plainly.

* **The walk must fail somewhere, and where it fails is not a defect.**
  The set of tree edges the walk cannot cross is precisely the boundary of
  the realizable region inside the mutation graph. A crossing failure is
  the walk's *decision output*, not its error.
* **No walk-based argument can prove the realizable side by itself.** It
  needs an independent handle on where it stops — which is what
  biquadratic final polynomials supply.

---

## 3. What *is* true — and it is already in this repository

The right theorem is not "mutation preserves realizability" but
"realizability is connected *under* mutation". `OMGAMMA.md` states and
proves it as **Lemma 3 (labeled realizable connectivity)**:

> For all n >= r >= 1 the subgraph of Gbar^{n,r} induced by the REALIZABLE
> uniform OMs is connected. *Proof sketch.* Chambers of
> D = {V in (R^r)^n : all r x r minors nonzero} map onto realizable
> labeled chirotopes; the union of the singular loci of the hypersurfaces
> {det_B = 0} and their pairwise intersections has codimension >= 2 in
> R^{rn}, so any two points of D are joined by a smooth path crossing the
> walls transversally one at a time at smooth points; each crossing flips
> exactly one basis sign, i.e. is a mutation between realizable uniform
> chirotopes.

Restated in the form this project needs:

> **Theorem A.** Let R be the graph whose vertices are the realizable
> uniform chirotopes of rank r on n elements, with an edge between two of
> them whenever some smooth path in R^{r x n} crosses the single wall
> separating them transversally. Then R is connected.

> **Corollary B.** A breadth-first search in R — start from one realized
> configuration, and repeatedly cross walls — reaches **every** realizable
> class. The classes it never reaches are exactly the non-realizable ones.

That is the theoretical content that makes wall crossing more than a
heuristic: **a crossing-based search is complete on the realizable side.**
It is also exactly why the walk's failures coincided with the
non-realizable classes in every case we measured.

**Trust boundary.** Lemma 3 is omgamma's own argument, described there as
"folklore but we could not find the labeled-level statement in print",
citing Roudneff–Sturmfels 1988 (Geom. Dedicata 27) for the
reorientation-class version. We have not read Roudneff–Sturmfels directly.
Theorem A is therefore *not* verified literature; it is a project-internal
lemma. Nothing in any certificate depends on it — every realization is
checked by exact integer determinants and every non-realizability
certificate by a Gordan vector — but the *completeness* claim of
Corollary B does. Before that claim is published it must be checked
against the primary source.

---

## 4. Why the tree is not that BFS, and what the gap costs

The omgamma tree spans the **full** mutation graph, not R. Tree edges may
therefore leave R, and there are exactly two ways the walk stalls:

* **(a) the child is non-realizable.** The crossing must fail. This is the
  answer, not a failure.
* **(b) the child is realizable but its tree-parent is not.** The walk has
  no parent realization to start from — an *orphan*. Nothing is wrong with
  the class; the tree simply routed to it through a non-realizable class.

Measured upper bound on (b): in a uniform sample of 1200 rows, **39
(3.25%)** had a parent our searcher could not realize. That is an upper
bound because it also counts parents that are realizable but hard.

**The repair is Corollary B.** When the tree parent is unusable, cross
from any already-realized *mutant neighbour* instead — a class has 10–26
mutable bases (mean 14.7, measured), so there are many candidate routes,
and Theorem A guarantees one exists. That turns the tree walk into the
BFS of Corollary B, at extra cost only on the ~3% of orphans.

So the algorithm the theory actually recommends is:

1. walk the tree, one crossing per class (cheap, covers ~97%);
2. for orphans, cross from any realized mutant neighbour (Corollary B);
3. everything still unreached: biquadratic final polynomial;
4. anything left over is the genuine open set.

---

## 5. The evidence

All of it laptop-scale, all certificates re-checked by `checkcert.py`
(standard library, shares no code with the producer).

**The identity (\*) and the group action.** 1500/1500 random rows satisfy
(\*), recomputed from decoded sign vectors; the matrix action agrees with
the chirotope action and its inverse round-trips (25/25 each, exact
integer determinants); all six witness arrays match their manifest
SHA-256. (`treewalk.py verify`)

**The walk works.** Depth <= 8 subtree, 4311 rows: **4308 crossed
(99.93%) at 26.1 ms each**, 3 unrealized. All 4309 certificates accepted.

**And it keeps working at depth.** `treewalk.py probe` samples rows
uniformly over all 9 276 595 classes, realizes each row's *parent* from
scratch, then attempts the crossing:

| depth band | probed | parent realized | crossed |
|---|---|---|---|
| 8–11 | 9 | 9 | 9 (100.0%) |
| 12–15 | 146 | 144 | 142 (98.6%) |
| 16–19 | 609 | 585 | 577 (98.6%) |
| 20–23 | 409 | 399 | 394 (98.7%) |
| 24–27 | 27 | 24 | 23 (95.8%) |
| **all** | **1200** | **1161** | **1145 (98.62%)** |

Flat in depth — decay towards the leaves would have killed the idea.

**The failures are exactly the non-realizable classes.** This is the
measurement that matters, and it was the weakest link until it was made.
Every one of the 16 rows that failed to cross was then put to BFP and, if
that failed, to a heavy search and a mutation warm-start:

| what the 16 crossing failures turned out to be | count |
|---|---|
| NON-REALIZABLE, with an explicit Gordan vector | **16** |
| realizable (i.e. a genuine miss by the walk) | **0** |
| undecided | **0** |

So in 1145 successful crossings and 16 failures there is **no observed
case of a realizable class that the crossing could not reach** — exactly
what Corollary B predicts and Proposition 1 permits.

**The residue is gone.** A complete cascade over **10 000** classes
(stages A+B, then the seven-level effort ladder) leaves **zero**
unsettled:

| level | entered | solved | marginal conversion |
|---|---|---|---|
| L1 direct search, small | 821 | 352 | 42.9% |
| L2 direct search | 469 | 182 | 38.8% |
| L3 mutation warm-start, small | 287 | 135 | 47.0% |
| L4 mutation warm-start | 152 | 110 | 72.4% |
| L5 mutation warm-start, heavy | 42 | 42 | **100.0%** |
| L6, L7 heavy direct search | 0 | — | never entered |

**Final residue 0/10 000, 95% Wilson CI [0%, 0.0384%]**, i.e. at most
~3 562 classes catalogue-wide. And the marginal conversion *rises*
monotonically through the ladder rather than plateauing: the
mutation-based levels do all the work at the hard end, and the two heavy
direct-search levels are never reached at all. That is the plateau
question answered — there is no plateau, the curve terminates.

**There is no structural signature of "hard".** Comparing classes solved
at L1 with classes that needed L4/L5 (120 each):

| | mutable bases (mean / median / range) | stabiliser |
|---|---|---|
| easy (L1) | 14.68 / 15 / 11–21 | all trivial |
| hard (L4–L5) | 14.12 / 14 / 10–20 | all trivial |

They are indistinguishable. Of all 821 laddered classes, 820 have
|Stab| = 2 and one has 4 — no enrichment in symmetry. **Difficulty is a
property of searching from scratch, not of the oriented matroid.** That is
the same conclusion the walk reaches from the other direction, and it is
why the right lever was always structure rather than compute.

---

## 6. What this changes

The $315 sweep of `SCOPING.md` §8 was buying with money what should have
been bought with method, and two ideas removed the need for it:

| | per class | catalogue |
|---|---|---|
| search cascade (§7) | 1 530 ms | 3 940 core-hours |
| **tree walk (§11)** | **26.5 ms** | **~70 core-hours** |

Walk + BFP is **~86 core-hours** — one overnight run on this laptop at 4–5
workers, **$0**, no cloud. The remaining orphan repair touches ~3% of
classes. Nothing in the revised plan needs a VM.

---

## 7. What is still missing, precisely

Three gaps, in decreasing order of how much they should worry anyone.

1. **Corollary B's completeness rests on a project-internal lemma.** Every
   *certificate* is independent of it — realizations are checked by exact
   determinants, non-realizability by Gordan vectors — but the claim "the
   classes the walk never reaches are exactly the non-realizable ones"
   does not hold without Theorem A. Verify Lemma 3 against
   Roudneff–Sturmfels 1988 before anything is published.

2. **BFP completeness at (4,9) is not a theorem and should not be
   assumed.** It does not have to be, though: we do not need BFP to be
   complete in general, only to settle the specific classes the walk
   leaves. That is *checkable* rather than conjectural, and the check is
   the run itself. Independent support: our (3,10) sweep finds the
   published non-realizable count at the same LP size as (4,9) (§4.1 of
   SCOPING.md).

3. **The one genuinely open possibility** is a class that the walk cannot
   reach *and* that has no biquadratic final polynomial. We have seen none
   — 0 of 10 000, and 0 of the 16 crossing failures — but the 95% upper
   bound is ~3 562 classes and it is not zero.

If (3) turns out to be non-empty, here is the specification of the idea
that would be needed, since no amount of compute supplies it:

> A decision method for uniform rank-4 realizability **whose failure is
> informative.** Realization search and BFP both fail silently: neither
> tells you which of the two answers you are looking at. What is needed is
> a method whose *negative* answer is itself a certificate — a
> Positivstellensatz witness of a degree above the biquadratic ones, or a
> SAT/SMT encoding of the chirotope axioms with a DRAT proof. That is what
> converts a residue list into a closed cell.

And the cheap version, which nobody appears to have asked and which the
data already supports:

> **Conjecture.** A uniform rank-4 oriented matroid on 9 elements all of
> whose 8-element deletions are realizable, and which has no biquadratic
> final polynomial, is realizable.

Every residue class we ever examined satisfies the hypothesis: 18 of 18
survivors of the full cascade, and 33 of 33 earlier ones, have all nine
deletions realizable. If the conjecture holds, walk + BFP + this theorem
is a complete method and the cell closes. If it fails, the counterexample
is a BFP-resistant uniform oriented matroid at **n = 9** — three to five
elements below the smallest known example — and that is a better result
than the count.
