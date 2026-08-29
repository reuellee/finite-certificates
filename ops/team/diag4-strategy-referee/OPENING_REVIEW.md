# Diagonal-four top-sheaf opening strategy review

Date: 2026-08-29 UTC

Track: `diag4-strategy-referee`

Role: independent strategy referee

Control-plane revision: `a58b108063bf25065f8874723728ec51d31d3f51`

Control-plane tree: `6da74080d67b15f90daa989363a947d93206c8ff`

Canonical mathematical base: `d047359e7892106021022b0401554f56eb4e4d8a`

Canonical mathematical tree: `af221cc4a3c2d81ce2c58ecb71bdf2e029b4b929`

Opening ledger: `2/9`; diagonal four remains open.

## Verdict

**MODIFY.**  Keep diagonal four as the primary target, but do not accept a
prover or falsifier handoff against the current target wording.  The pivot is
better justified than another diagonal-three local-coverage cycle, another
parent-860 diagonal-eight filling, or an unbounded diagonal-nine roadmap.
However, the cycle currently conflates a complete single-piece domain with a
66-orbit generic subcensus, does not lock a mathematically decidable
intermediate claim, and understates the independent lower-row and
restriction-map obligations in the fivefold complex.

This is not a `PIVOT` away from diagonal four.  It is a required repair of the
opening contract before candidate evidence can pass an independent gate.

## Independence and scope

This pass audited only the opening strategy, canonical fourth-diagonal notes,
their existing exact regressions, and the sharp abstract split--remerge
countermodels.  It did not perform constructive discovery, inspect any new
prover/falsifier conclusion, modify a candidate artifact, infer theorem
progress, edit the ledger, or merge anything.

## Canonical authentication and replay

The cycle's stated canonical revision and tree agree with Git.  The three
control-plane files are the only changes from the mathematical base to the
work-order carrier.

Relevant canonical byte SHA-256 values are:

| Object | SHA-256 |
| --- | --- |
| `ai/omreal/FOURTH_DIAGONAL_FIVEFOLD.md` | `efac03d2854221b0c8f7dabe2ff6aa3693166b3f8fbacf1bbfaa76aa4c30e2f5` |
| `ai/omreal/THREE_SHEAR_SINGLE_PIECE_REDUCTION.md` | `77dc85c047c3ee8371f1548d59b32f87ced47a5e47c65ff5d8b4b83eb1824de9` |
| `ai/omreal/verify_fourth_diagonal_reduction.py` | `d02d3bfa8994e380cfaa156b76fcc273934c3333abeac3ee3be13401bb8e2b55` |
| `ai/omreal/verify_fourth_single_piece_light_count.py` | `ca7b0128a1eb689cb5e3f6341666e90b72553ef04831a5311578a6038f010bae` |
| `ai/omreal/NINE_DIAGONAL_STATUS.md` | `f4360254e5c7e624b9c9194bb7cb0b3844d5fe3201ec9bc688c2f18d37276782` |
| `ai/omreal/data/DIAG3_RESEARCH_DECISION_LEDGER.json` | `5841dfbb55aa0d8c580b394b50beff54d607ce86b77683985c2d977c03050e14` |

The two canonical exact replays passed:

```console
PYTHONDONTWRITEBYTECODE=1 python \
  ai/omreal/verify_fourth_diagonal_reduction.py
PYTHONDONTWRITEBYTECODE=1 python \
  ai/omreal/verify_fourth_single_piece_light_count.py
```

They independently delimit two different universes that the cycle must not
identify:

| Canonical census | Labeled supports | Scope |
| --- | ---: | --- |
| all supports of one through five triples | `4,216,422` | complete single-piece support index |
| all cover-all supports | `1,715,980` | sizes 3/4/5: `840 / 72,380 / 1,642,760` |
| generic support-minimal five-circuits | `2,021,992` | generic five-support subcensus |
| generic cover-all five-circuits | `1,099,560` | `66` of `117` unsigned `S_8` orbits |

The 66-orbit object is therefore not the complete cover-all top-sheaf
obstruction class.  It omits cover-all size-three and size-four supports,
nongeneric five-support strata, signed tensors, parent chirotopes, weight
faces, and split/merge incidence over the realization cell.  Those omitted
objects can be exactly where the top component sheaf changes.

## Mandatory eight-factor strategy comparison

Ratings use `5` for high leverage/readiness/terminality/compression/
independent verifiability/information return.  For burden and stagnation,
`5` means high burden or high risk and is unfavorable.

| Candidate | Ledger leverage | Quantifier readiness | Coverage burden | Terminality | Structural compression | Independent verification | Resource / information | Stagnation risk | Referee disposition |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| diagonal 3 | 5 | 3 | 5 | 2 | 3 | 3 | 2 | 5 | `PIVOT` away as primary |
| diagonal 4 | 5 | 2 | 4 | 4 after target lock | 5 | 3 | 4 | 1 | **`MODIFY`, then `CONTINUE`** |
| diagonal 8 | 5 | 1 | 5 | 2 | 3 | 4 | 2 | 4 | `RETIRE` as primary |
| diagonal 9 | 5 | 2 | 5 | 2 | 4 | 3 | 2 | 3 | `PIVOT` |

Reasons:

- Diagonal three has two logically independent global obligations.  The
  triple residue remains `1,162,302`, and the pair branch still lacks a
  coverage-certified global closure complex.  Several consecutive local
  expansions have not changed either complete obstruction class.
- Diagonal four has the best plausible one-lemma compression: the fivefold
  truncation is exact, omitted single pieces are killed through degree three,
  and the surviving top-row failure is isolated sharply by an abstract
  split--remerge model.  A direct single-piece theorem or an admissible exact
  counterexample has high decision value.  Its readiness score is only two
  because the current work order has not specified the full actual-OM
  universe or the projection/top-sheaf object.
- Diagonal eight's latest exact work proves that graph labels do not decide
  `H_1`; the parent-860 network has no local eight-antichain, lacks global
  coverage and infinity, and the surviving mask-6 loop is only a local
  discriminator.  Another filling cannot change the theorem ledger.
- Diagonal nine has a clean connectivity target and potentially strong
  structural criteria, but it lacks a full-dimensional parent roadmap.  Even
  one projection layer creates 142 new irreducible factors outside the
  current residual catalog, so the immediate coverage burden remains high.

The ranking supports the diagonal-four pivot, but the four-column comparison
in `CYCLE.md` does not itself satisfy Section 2 of the new protocol, which
requires all eight factors above.

## Quantifier defect and required claim lock

The current target asks for the "strongest globally quantified" statement
that is "actually implied" and asks the falsifier for the "weakest necessary"
premise.  Neither phrase identifies a fixed proposition.  Prover and
falsifier could return logically different lemmas while both claiming to
have met the contract.

The selected intermediate should instead be locked directly as follows.

> **D4-SP (admissible cover-all single-piece vanishing).**  For every
> realizable uniform rank-four oriented matroid `M` on the labeled ground set
> `[8]`, every proper pairwise-incomparable four-signature family `S` in its
> 9DVL domain, every `rho in S`, and every circuit support
> `Q subset binom([8],3)` with `1 <= |Q| <= 5` and union equal to `[8]`, the
> closed circuit piece `C_(rho,Q)`—including every zero-weight face and every
> structural/residual-wall specialization inside the normalized realization
> cell—satisfies `H_c^3(C_(rho,Q);Q)=0`.

This is exactly the unresolved cover-all part of the `(p,q)=(0,3)` column.
It is intentionally not diagonal four.  A proof removes that column only; a
counterexample disproves this compression lemma only.

A no-split--remerge theorem may be used to prove D4-SP, but it must define a
single global semialgebraic quotient `pi` (or a finite compatible atlas), its
base, its three-dimensional fibers, its orientation local system, and its
component-incidence sheaf.  It must then prove the compactly supported
top-sheaf statement needed for D4-SP across chart changes, closed weight
faces, parent boundary, births, deaths, splits, and merges.  A pointwise
escape or a graph with no displayed loop is not such a proof.

The clean falsification standard is one exact tuple `(M,S,rho,Q)` in this
domain together with a checked nonzero class in `H_c^3(C_(rho,Q);Q)`.  A
signed split--remerge event without a closed compact section is only a
mechanism witness.  An abstract semialgebraic split--remerge model is a
hostile canary, not an actual-OM counterexample.  A counterexample outside an
admissible four-family refutes only a stronger optional all-signature lemma,
not D4-SP.

## Sharp countermodel audit

The canonical countermodels correctly rule out the two shortcuts that the
new cycle is most likely to rediscover.

1. `Omega={(x,y):(x+a).(y+a)>0}` has convex fibers under either coordinate
   projection but is homotopy equivalent to `S^1`, hence has nonzero
   `H_c^3`.  Separate convexity and four light parameters do not kill the top
   row.
2. For `A={(t,x):t^2+x^2>1}` and `Omega~=A x R^2 -> R_t`, every fiber
   component is a contractible oriented open three-manifold and every branch
   reaches infinity.  The fiber splits over `[-1,1]` and remerges at both
   ends; the doubled interval carries a compact anti-diagonal section and
   `H_c^3(Omega~;Q)=Q`.  Branchwise noncompactness is insufficient.

Every positive semantic kernel must reject both models.  Every falsifier must
distinguish them from realizable signed third-compound data rather than
quietly treating either abstract model as a 9DVL obstruction.

## Corrected obligation graph

The opening graph records genuine reductions but is not complete, and the
statement that fivefold restriction exactness is dependent on the selected
top-component edge is not established.  The restriction calculation can in
principle kill a surviving single-piece class, while removal of the
single-piece top row does not settle the lower rows.

The fail-closed graph is:

1. Parent `H_5` vanishing and the bad-locus dual reduction: proved in the
   canonical note.
2. Total-degree `2 -> 3 -> 4` fivefold truncation: proved.
3. Single-piece `(p,q)=(0,3)`:
   omitted supports proved zero; complete cover-all domain open as D4-SP.
4. Two-piece `(1,2)` terms after the exact incidence sieve: open.
5. Three-piece `(2,1)` terms after the exact incidence sieve: open.
6. Four-piece `(3,0)` terms after the exact incidence sieve: open.
7. Adjacent total-degree terms, including five-piece outgoing terms, all
   compactification faces, orientation/sign transport, and alternating
   restriction maps: open.
8. Exactness in middle total degree and `H_c^3(B_S;Q)=0`: open and dependent
   on the complete total complex, not only item 3.
9. Diagonal-four ledger entry: open until item 8 and all parent/family
   quantifiers pass independent review.

No candidate in this cycle may recommend a ledger change merely by proving
D4-SP or by shrinking an unsigned support census.

## Stop-rule audit

The 90-minute ordinary-compute ceiling and required null/timeout manifests are
appropriate.  The following amendments are necessary:

- Replace "strictly reduces the current 66 generic cover-all support orbits"
  with a reduction against an explicitly complete declared universe.  A
  reduction of the 66 generic five-support orbits is publishable only when
  labeled as that bounded subcensus and when every excluded nongeneric,
  smaller-support, signed, parent, and boundary stratum is stated as a
  nonconsequence.
- Stop positively at a proof of D4-SP, not at an unspecified persistence
  lemma.  A weaker lemma must state the exact subdomain it removes.
- Stop negatively at an admissible D4-SP counterexample, or classify a
  mechanism-only countermodel as a no-go for the proposed lemma without
  claiming that D4-SP or diagonal four is false.
- A null must list the exact parents/signatures/supports/event strata tested,
  the survivor representation, and the next exact discriminator.  "No
  split--remerge found" is not a useful null.
- A timeout must pin code, input digests, completed shard/domain manifests,
  and resumable state.  No sampled topology may be promoted.

## Grounding and publication gates

The revision and tree are correctly pinned, the opening score is honest, and
the work orders and the actual agent prompt include the user's explicit
publication authorization and its restrictions.  Coordinator-only ledger,
PR, integration, merge, and backup ownership is also preserved.

Before execution evidence is accepted, the coordinator should add:

1. the canonical ledger path and digest, not only the text `2/9`;
2. byte digests for every work-order input;
3. the complete cover-all census distinction above;
4. an explicit inventory of unfinished/concurrent cycles and a non-overlap
   statement; and
5. the corrected eight-factor evaluation, D4-SP claim lock, obligation graph,
   and stop dispositions.

These are opening-contract defects, not defects in the user's publication
authorization.  Publication remains permitted only through the stated
fail-closed coordinator gates.

## Resume gate for candidate review

Freeze this referee track now.  Resume only after the coordinator supplies:

- exact immutable prover and falsifier revisions;
- their result handoffs and artifact digests;
- the amended target or a written disposition of every `MODIFY` item above;
- clean replay commands and independent verifier entry points; and
- an exact claim list distinguishing D4-SP, a bounded subcensus result, a
  mechanism no-go, and any total-complex consequence.

Until then, the opening strategy is **MODIFY**, the theorem ledger remains
`2/9`, and no candidate acceptance is issued.
