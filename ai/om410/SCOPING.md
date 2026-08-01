# om410 — the first datapoint beyond the enumerable frontier

*Scoping note, 2026-08-01. Design phase only; build starts after the (4,9)
sweep completes and its review clears. Nothing here touches the running
sweep.*

## The question

The non-realizability density of uniform rank-4 oriented matroid classes:

| n | classes | non-realizable | density |
|---|---|---|---|
| 8 | 2,628 | 24 | 0.913% |
| 9 | 9,276,595 | sweep in progress | ~1.3% at 31% depth-ordered prefix, rising; ~2.1% projected |
| 10 | ~10¹¹–10¹² (extrapolated) | **unknown — enumeration impossible** | ← this study |

(4,10) can never be enumerated (~420 core-years, MINOR_THEORY §9). But the
omopen completion-LP toolkit decides *individual* classes in
milliseconds-to-seconds, which converts the density question from a sweep
into a **sampling problem**. A measured (4,10) density with honest error
bars would be the first quantitative datapoint past the enumerable
frontier, and the third point on the curve that tracks where Mnëv-style
wildness begins to dominate.

Secondary endpoints, same sample: the minor-closure fraction at n = 10
(is 91% rising toward 1 or falling?), BFP-or-minor coverage of the
non-realizable sample (completeness evidence beyond n = 9), and mutation-
graph mixing behaviour at (4,10) (empirical connectivity evidence — our own
omgamma frontier).

## Sampling design — the crux, and the honest part

There is no catalog to draw from, so the sampling measure must be designed
and *disclosed*. Two independent designs, whose agreement is the
robustness argument:

**S1 — Metropolis mutation walk (primary).** Start from seed (4,10)
chirotopes (random real configurations, rounded — always realizable — plus
lifted non-realizable seeds via Proposition-R-style extension of certified
(4,9) obstructions). Walk by uniform random mutation flips with a
Metropolis degree correction (proposal ∝ 1/|mutable bases|), so the
stationary distribution is uniform over the reachable component.
Conditional on mutation-graph connectivity at (4,10) — which is exactly
the standing conjecture one level up from our omgamma theorem — this
samples uniformly. Diagnostics: many independent chains, split-chain R-hat
on observables (density, mutable-basis count, depth proxies), and explicit
disclosure that the estimate is conditional on connectivity + mixing.
Per-step cost: one basis flip + local GP-consistency check — microseconds.

**S2 — extension sampling with Horvitz–Thompson reweighting (cross-check).**
Draw a parent uniformly from the *enumerated* (4,9) catalog, draw a
uniform single-element extension, land on a (4,10) class C. The raw
measure overweights classes with many prolific parents; the correction
weight needs, per sampled C: its 10 deletion classes (cheap — canonicalize
against the (4,9) index) and each parent's extension count N(P) (hard —
uniform localization counting; candidate method: #SAT on the localization
axioms, or chamber counting in the realized arrangement for realizable
parents). If N(P) proves too expensive, S2 degrades gracefully to a
*disclosed-measure* estimate (report the extension-measure density as its
own quantity) — still a valid cross-check of S1's qualitative story.

## Decision procedure per sampled class (the omopen dividend)

1. **Minor test** (~90% of non-realizable hits expected): canonicalize the
   10 deletions, look up the certified (4,9) non-realizable set. A hit
   yields a *certificate* by lifting the (4,9) BFP one level (the
   Proposition R argument is level-independent — re-prove for 10→9 in the
   build, don't assume).
2. **Direct BFP at (4,10)**: same LP, 210 brackets.
3. **Completion LP** (the new tool): pick a deletion whose (4,9) class is
   realizable (~98% are), fetch its stored realization from the completed
   sweep's store, hill-climb the 4-variable extension LP.
4. **Full multi-deletion weaponA** for the residue; per-class time budget
   with escalation, exactly as in OPEN_ATTACK.md.

Everything two-sided and certified: realizations checked by exact
chirotope recomputation, non-realizability by independently checked FP/
lifted certificates. Sampled classes that resist *both* directions are the
most interesting objects in the study — candidate BFP-completeness
counterexamples at n = 10 — and get reported as a residue, never buried.

## Dependencies and order

- **Blocks on**: (4,9) sweep completion (certified non-realizable witness
  set + realization store must be final), omopen review clearing, and the
  final-residue attack run. Do not start the build before all three.
- Pilot: 1,000 samples per design, then 10,000 if the pilot's CI width
  justifies it. All laptop-scale, post-sweep cores.
- Canaries: sample-and-decide against the *known* (4,9) cell first (both
  samplers must reproduce the sweep's measured density within CI);
  deliberately corrupted samples must be caught by the checkers.

## Free corollary to record in the omreal writeup (not this study)

Oriented-matroid duality (r,n) ↔ (n−r,n) preserves realizability, so the
completed (4,9) split immediately yields the **(5,9)** split — a second
table entry at zero cost. Verify the duality-preserves-realizability
citation and the class-count correspondence when writing up.
