# Slow-lane target shortlist (scouted 2026-07-31)

Four parallel scouts swept: (1) discrete-geometry problem books, (2) the
Erdős database + extremal "known values" tables, (3) polytopes/oriented
matroids, (4) compute-frontier archaeology. Rubric: OLD (20+ yr) +
NEGLECTED (no serious attack since ~2015) + CERTIFICATE-SHAPED (finite
exact reduction) + COMPUTE-BOTTLENECKED, with still-open verification
required and payoff-if-negative preferred. Full scout reports are in the
session transcript; this file is the synthesis of record.

## The strategic finding

The 2025–26 AI wave (checked against the Erdős-database AI-contributions
record) concentrates on (a) formal proof search and (b) constructive /
generative search for better examples. **Symmetry-reduced exhaustive
nonexistence and classification certification — our lane — is untouched
by it.** The one lineage doing certificate-grade exhaustive work
(Heule–Scheucher SAT) is visibly occupied with ES(7)/33-point and
Hadamard-668. Everything below avoids their lanes.

## Tier 1 — recommended program (in order)

### 1. FLAGSHIP: the realizability split of uniform rank-4 oriented matroids on 9 elements
The Finschi–Fukuda–Moriyama census (2010) holds ~9.28M uniform OM(4,9)
chirotopes; the field's reference table (Fukuda–Miyata–Moriyama 2013)
lists their realizable/non-realizable split as **"unknown (unknown)" —
blank for 13 years**. Certificates per object: rational realization
(solvability-sequence / exact repair — our pipeline) or biquadratic
final polynomial (a positive combination of GP 3-term relations — our
quotient-ring machinery, literally). Symmetry: S₉ × reorientation
orbit-transport, which we just built and verified for OM(3,5). No new
enumeration needed. Closing the cell is a citable classification result
with zero conjecture-risk, and the completed split becomes input data
for targets 2 and 3. Crowding LOW. Honest caveat: 13 years stale, not
20+; wins on every other axis.
**Pre-flight (open verification gaps from the scout):** (a) confirm the
cell is still blank in the live database (om.math.ethz.ch unreachable
this session — inference is from Knauer–Marc 2023 Table 1); (b)
reconcile the 9,276,595 (Knauer–Marc) vs 9,276,601 (FMM 2013) count
discrepancy before publishing any derived number.

### 2. FIRST STRIKE (cheap, ~week): Cordovil–Las Vergnas mutation connectivity, Γ̃ variant, n ≤ 9
Knauer–Marc (EJC 2023) verified the isomorphism-class mutation graph
connected for n ≤ 9 and state in print they **suspect a counterexample
in the intermediate reorientation-class graph Γ̃** — checkable on the
same existing n ≤ 9 data, no new enumeration, and the one group aware
of it is working elsewhere. A disconnection witness is a clean finite
certificate refuting a variant of a 1988-published conjecture.
Perfect pipeline-validation project before the flagship.

### 3. SIDE LANE (MaxSAT, parallel): football pool problem K₃(6,1)
Minimum ternary covering code, length 6, radius 1: 65 ≤ K₃(6,1) ≤ 73
over a 729-point universe. Lower bound untouched since Östergård–
Wassermann 2002; the same community just Lean-certified a sibling case
(K₈(4,2)=23, 2026), so the publication template exists. S₆×S₃ symmetry
breaking + modern MaxSAT/ILP; any tightened bound updates the canonical
covering-code tables. Small enough to run alongside the flagship.

### 4. SPOT-CHECK (tiny): Las Vergnas simplex conjecture, the 13-element object
Every OM should have a simplicial tope (1980). Knauer–Marc name a
uniform rank-4, 13-element, 598-tope OM (from Tracy Hall's 2004
construction) outside every known sufficient class. Computing its tope
graph and min degree is nearly free; refutation would kill a 46-year
foundational conjecture.
**Pre-flight:** read Bokowski–Rohlfs 2001 first — "verified up to 12
elements" cannot have been exhaustive (census stops at n=9), so
determine what was actually checked; smaller open cases may exist.

## Tier 2 — medium-term flagships (bigger compute, keep warm)

- **Biplane (121,16,2) existence** — surfaced independently by two
  scouts. The Lam-style "cube" half is already published (2020
  automorphism restrictions); nobody has run the "conquer"
  (SAT/orderly-generation) half; no computational assault since
  Kaski–Östergård 2008. Design-theory classification payoff either way.
- **Grünbaum–Cuntz simplicial arrangement catalogue at n = 28** —
  complete to 27 lines (Cuntz 2012), untouched since; literature itself
  says extending needs "more computational resources." Rank-3 OM
  enumeration + stretchability certificates = our home objects, but
  generation at n=28 is heavy.
- **Circulant Hadamard residual list** — 13 named primes left by
  Leung–Schmidt 2012; per-prime bounded computer-algebra eliminations;
  beware the noise of disputed arXiv "full proof" claims.
- **Costas arrays, order 30** — last full enumeration order 29 (2011,
  ~367 CPU-years then); plausibly cluster-weeks now; enumeration itself
  is the citable result.
- **Kalai's cube-simplex f(3)** — no bound known at all; the 2000-era
  FLAGTOOL LP computation is the only artifact and is unchallenged;
  needs scoping work to become concrete.
- **Shephard's 11 projectively unique 4-polytopes** — never proven
  complete since the 1960s; 11 small realization-space computations plus
  a bounded catalog search; trivial compute, moderate novelty.

## Tier 3 — interesting but flawed

- **Rectilinear crossing K₂₈ ∈ {7233, 7234}** — a literal one-bit
  decision, but scouts disagree on crowding (two say dormant since
  2008; one flags a standing TU Graz distributed project). Resolve the
  project's actual status before touching.
- **Green–Tao effective-threshold gap** (Dirac–Motzkin/orchard) — LOW
  crowding and glamorous (making a landmark theorem effective), but the
  reduction from their ineffective threshold to a computable range is
  research, not mechanical certification. A thinking-first target.
- **Dirac's 1951 conjecture, real case; Firsching's non-rational n=10;
  extension-space explicit witness; Motzkin unimodality d=6,7;
  equiprojective k=6** — all LOW-crowded and cheap-to-start, all
  one-sided or needing harder certificate types; candidates for idle
  cycles.
- **Folkman Fe(3,3;4) → N=22** — SAT-certificate shaped but the niche
  had 2026 activity nearby (MED crowding).

## Avoid (hot lanes, verified)

ES(7)/33-point (Heule–Scheucher, live 2025–26 papers), Hadamard 668
(active certified-search paper), Kobon triangles (active SAT
competitor), big-line-big-clique (Apr 2026 paper), neighborly polytope
search (DeepMind Hopper, 2025), polynomial Hirsch and Ziegler's fatness
(both confirmed hot July 2026), projective plane order 12 and MOLS(10)
(compute-infeasible), W(2,7) full determination (expert-stated
infeasible; bound-push only), vertex-Folkman and z(m,n;2,2) and
degree-diameter (2026 AI-swept).

## Resolved-recently graveyard (scouts' verify-before-target discipline)

Empty hexagon = 30 (2024); Grünbaum triangle and digon conjectures;
Las Vergnas strong-map conjecture (refuted 2021); Bárány's question
(2022); g-theorem for spheres (2018); Barnette–Goodey (2020).
