# Diagonal-eight independent referee: pass-two review

Date: 2026-08-29 UTC

Track: `cycle-20260829-diag8-referee`

Candidate commit: `be7b5953856bb0f8dbb3dc63b5757edfb259268f`

Candidate tree: `18021503f846f85a0b9122e5c4732d0d85fdf080`

Handoff carrier: `d13f84403d9226a8b2f1fa0347d46fe794e24424`

Handoff carrier tree: `6c050ce38f23d92b526923cadbc29bf6c53310ac`

Canonical evidence base: `5393b03fda623dc6b4552130d13467fae71d31bc`

Canonical base tree: `06cc3363a021b8adc59e66865f44bf8eafa66029`

## Publication disposition

**Reject the current immutable candidate for publication.**

The exact computations support the five handoff claims at their stated
bounded scopes, and no diagonal-eight or ledger promotion is attempted.
However, the candidate fails the claim-lock and repository/prose-consistency
gates because it conflates the full represented signature universe with the
proper support-pattern subposet.

The repaired-network artifact contains:

- `26,264` represented signatures;
- `13` total vertex-support classes;
- one universal class containing `25,960` signatures; and
- `12` proper classes containing only `304` signatures in total.

`ops/team/diag8-dual-prover/RESULT.yaml` lines 37--39 state that the 12 proper
patterns have 26,264 represented signatures.  That is false.  The wording in
`ops/team/diag8-dual-prover/PROOF_NOTE.md` lines 10--12 and
`ai/omreal/DUAL_MASTER_CELL_PROGRAM.md` lines 405--406 omits the universal
class and is materially ambiguous.  The handoff's first-family quantifier
also says “all 12 support-pattern classes,” although there are 13 total; it
must say “all 12 proper support-pattern classes, excluding the universal
class.”

This accounting error does not change the exact width-six computation on the
12 proper classes.  It does make the present publication package internally
inconsistent, so G00 and G16 fail closed.  No files were repaired by the
referee.

## Candidate identity and artifact accounting

The immutable identities match the handoff exactly.  All 20 entries in the
candidate artifact manifest match both byte size and SHA-256 at the candidate
tree.  The five canonical NPZ dependencies independently checked by the
referee also match their pinned hashes:

- parent-860 coordinate star;
- parent-860 repaired network;
- row-2599 node roadmap; and
- the two row-2599 global antichain artifacts.

The four transport verifier inputs match their internally pinned hashes.  No
candidate file was modified during replay, and every YAML/JSON artifact in
the four track directories parses successfully.

## Replay and independent checks

All commands were run from a detached checkout of the immutable candidate.

| Replay | Result |
|---|---|
| `verify_diag8_parent860_graph_h1.py` | exit 0; width 6, nine empty-support six-antichains, no local eight-antichain, exact `a/d` filling, all four canaries pass |
| `verify_diag8_falsifier.py` | exit 0; exact `a/g` polygon arrangement, mask-3 filling, mask-6 survivor, abstract countermodel, all canaries pass |
| `verify_diag8_relative_h1_certificate.py` | exit 0; filled/unfilled/infinity fixtures and 11 hostile mutations pass |
| `verify_transport_obstruction.py` | exit 0; mutation, deletion, incidence, infinity, and four hostile canaries pass |
| Four canonical referee regressions from pass one | exit 0 for all four |

The referee also performed checks not taken from the candidate's stored
summaries:

1. SymPy independently reconstructed all parent brackets and derived normals
   for the `a/d` triangle.  It obtained `210/210` strict parent controls and
   `840/840` strict signed fixed-witness controls for the five signatures.
2. Direct parsing of the canonical network NPZ found the exact
   `26,264 / 13 / 12 / 304 / 25,960` signature/class accounting above.
3. The canonical coordinate artifact ties vertices `1,2,3,18,17` to the
   candidate's rational `a/g` coordinates.  Exact evaluation of factors
   `16573` and `22629` gives sector signs
   `(+,−), (−,−), (−,+), (−,+), (+,+)` around the five vertices, so the loop
   visits all four chamber sectors incident to the unique transverse node.
4. The bivariate supports used by the polygon proof are exactly
   `16573: {1,g,g^2,a,ag}` and `22629: {1,a}`.  Thus the verifier's global
   nonzero `a`-derivative test and exact quadratic Sturm count use all terms,
   not a truncated polynomial.

## Claim-by-claim findings

### `parent860_local_support_width`

The finite computation is correct after changing “all support classes” to
“all proper support classes.”  On the 12 proper masks, width is exactly six;
there are nine six-antichains, all with empty common network support, and no
eight-antichain.  The result remains local and vacuous for diagonal eight.

Publication status: **rejected in the current package** because its coverage
prose and handoff quantifier contain the accounting defect above.

### `parent860_ad_triangle_filling`

The bounded geometric claim replays exactly.  The rational triangle remains
in the parent cell, and one fixed strict witness for each of five globally
proper, pairwise-incomparable signatures remains feasible throughout it.
The triangle fills the retained graph cycle.  The result supplies no parent
coverage, infinity, or size-eight conclusion.

Evidence status: verified at the stated bounded scope.  It does not cure the
candidate-wide publication rejection.

### `parent860_ag_pentagon_filling`

The bounded geometric claim replays exactly.  A two-triangle cover makes
26,738 residual factors sign-definite.  Factors `16573` and `22629` are the
only walls meeting the polygon, all 70 parent brackets remain strict, the two
walls meet once transversely, and the boundary visits all four incident
sectors.  All 26,038 stored boundary-common labels therefore extend over the
local disk by the pinned all-strata theorem.  The result fills the mask-3
network cycle only; it does not cover parent 860.

Evidence status: verified at the stated bounded scope.  It does not cure the
candidate-wide publication rejection.

### `graph_only_h1_no_go`

The abstract certificate fixtures have identical complete labeled
zero/one-skeleta and the same witnessed proper incomparable eight-family.
Adding one two-cell changes `H_1` from one to zero.  A separate relative
fixture changes `H_1` when true-infinity membership changes.  The schema
checks exact signed incidence, integral boundary-squared zero, labels,
dominance, mod-two ranks, and hostile mutations.  Its nonzero mod-two result
is correctly not promoted to rational nonvanishing.

Evidence status: verified as an abstract interface no-go, not a UOM
counterexample.

### `unconditional_transport_no_go`

The mutation verifier exactly enumerates `73,712` and `74,342` abstract
uniform one-element extensions on the two sides of a one-bracket mutation,
so no complete label-universe bijection is forced by mutation adjacency.  It
also reconstructs exact chart-tope births and deaths.  The reducible deletion
maps `25,856` full labels onto `5,294` deletion labels with `4,964`
nontrivial fibers and maximum fiber 282.  The finite topology fixtures
separately show that incidence and true infinity are load-bearing.

Evidence status: verified at the two stated counterexample fixtures.  It does
not rule out separately certified quiet-edge transport.

## Gate disposition

The machine-readable results are in `PASS2_GATE_RESULTS.yaml`.  In summary:

- G01--G03 and G15 pass.
- The applicable bounded geometry, label, incidence, rank, and transport
  checks pass at their narrow scopes.
- G04--G14 remain open or inapplicable for any parent-local/global
  diagonal-eight theorem, exactly as the candidate states.
- G00 and G16 fail because the support-class accounting disagrees across the
  artifact, handoff, result prose, and canonical strategy prose.

The candidate correctly keeps `diag8_h1` open and 9DVL at `2/9`.  The exact
surviving mathematical discriminator is still the mask-6 cycle
`4-11-12-14-13-23-4`, which lacks a coverage-certified spanning two-chain or
non-boundary cocycle.

## Required remediation

1. State everywhere that the 26,264 signatures form 13 local support
   classes: one universal class of 25,960 signatures and 12 proper classes
   totaling 304.
2. Correct `RESULT.yaml`, `PROOF_NOTE.md`, and the corresponding dual-master
   prose.  Clarify the first claim's handoff quantifier.  Prefer
   “proper-pattern subposet” where “support quotient” could mean all 13
   classes.
3. Regenerate all affected byte and semantic digests in a new immutable
   candidate and handoff carrier.
4. Replay the same five bounded claims and canaries without changing their
   scope or the theorem ledger.

Until those steps pass a short referee rereview, publication is rejected and
the recommended ledger change is **none**.
