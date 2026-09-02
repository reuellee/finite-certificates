# D3 global semialgebraic diagram replacement gate 1 report

## Final status

The formula-first cycle reached its mandatory Q0 checkpoint and closed
fail-closed:

```text
NULL_NO_EXECUTABLE_REPLACEMENT_BACKEND / STALLED / STOP
```

The producer built useful exact formula/compiler and scope-accounting
artifacts, the falsifier validated the topology canaries, and a separate
standard-library verifier confirmed the Q0 null.  Q0 did not pass, so Q1 was
never activated.  The authorized ephemeral worker was audited but not
created.  This cycle proves or refutes neither the selected replacement route,
diagonal three, nor 9DVL.  The theorem ledger remains `2/9`.

No result is described as human-reviewed.  The reviews in this package are
independent machine replays.

## Exact revisions

| role | commit | tree |
| --- | --- | --- |
| immutable canonical predecessor | `0b8141223193c1ea2a1b4fce8e862466749f8b6b` | `faad8f9e78bd54435ee6212535198a08c0e3fe76` |
| initial opening, independently rejected | `5d649d9961642e0afcfb6b369538ccf95d6049f6` | `3b4cd77773ee30ff9d1e2f885fd3d708d8522700` |
| repaired accepted opening | `c50da6c99d465c65b3e54427418d9efe6a3f037e` | `f5d91a7a6ea816b27b4f0a94fe7e26beccd8e72a` |
| frozen producer/falsifier Q0 evidence | `e18efbdea3ef00616f4a6cb83967f6bb267b1a5d` | `db753907ef0d1efa5a71098a33af29b733194b4b` |
| independent Q0 verification | `597537a8f705ac895e7d3e30962eb515cc8f6015` | `f6892f84cc32b89bdc72acdfdb07b6d832df9e82` |
| frozen midpoint/cloud candidate | `d8e61faae0e2318d8eb83fd26dc4140b44a149e1` | `7afe71aad321eb2e91ea1c7b3d4c327e23795328` |
| independent closing referee | `435f098d0ccd42f4dc2b7ddc5f3608ad2be7875b` | `32c9668a352a7fdcab9d84436ea5286ffae3b551` |

The working branch is
`research/local-d3-global-semialgebraic-replacement-gate1-20260902`.
GitHub remained read-only.

## Role assignments and independence

| role | owned surface | acceptance boundary |
| --- | --- | --- |
| coordinator | this cycle directory and integration commits | pins the opening, applies gates, records resources, integrates reviews, and closes; cannot substitute its own work for independent acceptance |
| formula/compiler producer | `ops/team/d3-global-srep-formula-compiler` | may construct Q0 evidence but cannot accept it or grant theorem credit |
| topology falsifier | `ops/team/d3-global-srep-falsifier` | owns independent canaries and hostile mutations; cannot define producer success |
| independent Q0 verifier | `ops/team/d3-global-srep-independent-verifier` | parses frozen inputs as untrusted data and imports no producer acceptance code |
| independent closing referee | `ops/team/d3-global-srep-closing-referee` | reconstructs the frozen midpoint from Git and accepts only a fail-closed close |

No role edited `ai/omreal`, the canonical V9 state, or the theorem ledger.
The two independent reviews are machine reviews; no human-review claim is
made.

## Resource acquisition and qualification

The cycle acquired the useful resources that could be obtained without human
review or unbounded external compute:

- pinned local copies of Basu--Karisani's simplicial-replacement paper and its
  semialgebraic-map/diagram companion;
- a reproducible rootless WSL exact-CAS stack: Singular 4.4.1, Normaliz
  3.11.0, 4ti2 1.6.15, python-flint 0.8.0, and msolve 0.10.1; msolve passed
  64/64 upstream checks and all five tools passed the recorded smoke suite;
- Baker's frontier/monotone CAD paper, thesis, and source archive as
  reproducible scratch.  The source is relevant to low-dimensional frontier
  CAD, but it is neither the selected route nor a Basu--Karisani backend;
- an available exact Wolfram real-closed-field lane and local exact algebra
  primitives; and
- an audited GCE on-demand shape with sufficient N2 quota, a four-hour
  deletion policy, and a USD 5 cycle cap.

No public executable Basu--Karisani implementation was identified in the
bounded paper, repository, code-index, and package-index search.  This is a
search result, not a claim that no private or unpublished implementation
exists.  The newly installed algebra systems are useful primitives, not an
implementation of the paper's ordered-infinitesimal cover and diagram
replacement algorithm.

## Q0 producer and falsification results

The producer emitted canonical sparse integer-polynomial formula ASTs and a
deliberately narrow affine-simplex compiler.  It exactly distinguished its
nonqualifying M3 filled/unfilled canaries with relative rational `H1=0/1`,
rejected the M2 tangential first-exit union before emitting a complex, and
replayed the already proved single-bad control.  All `8/8` producer tests
passed.  These M3 outputs are canaries, not Basu--Karisani outputs.

The independent falsifier supplied a different tetrahedral M3 model with the
same one-skeleton and exit graph but relative rational `H1=1/0`, replayed the
exact M2 family `(1/n,3/2) -> (0,3/2)`, and rejected `23/23` hostile mutations
across eleven categories.

The producer also expanded all 70 parent brackets and all `56*4=224`
derived-normal coefficient polynomials.  Its exact discrete prefilter found:

| quantity | value |
| --- | ---: |
| parent types | 2,604 |
| raw labelled frames per type | 40,320 |
| raw parent/frame presentations | 104,993,280 |
| valid abstract extension signatures summed by type | 174,937,600 |
| ordered distinct triples before properness/incomparability, by type | 807,780,496,606,300,008 |
| raw-frame-expanded version of that prefilter | 32,569,709,623,166,016,322,560 |

The last two values are explicitly **not** the required global denominator.
The first missing denominator is the all-parent classification of proper
feasibility regions and pairwise incomparability on every realization
component.  A second missing input is an exact quantifier-free `P`-closed
compactification `Xbar_M` and genuine infinity `I_M` for every parent.  Weakly
closing strict signs would be unsound.

Only the template ambient dimension `k=178` is exact.  `N`, `s`, and `d`
remain null.  The raw pre-quantifier-elimination degree bound `4` is not the
replacement theorem's final `d`, so no numeric output, memory, or elapsed-time
forecast exists.

## Independent Q0 verdict

The verifier read five pinned producer/falsifier inputs as untrusted data,
independently reconstructed both relative M3 chain complexes, recomputed exact
rational ranks and `d^2=0`, and checked the M2 family and limit.  It rejected
`22/22` hostile mutations without importing producer acceptance code.  Its
verdict is:

```text
Q0_NULL_INDEPENDENTLY_CONFIRMED; THEOREM_CREDIT=NONE
```

The subsequent independent closing referee checked the frozen midpoint and
claim boundaries, reconstructed seven inputs from Git, and rejected `22/22`
hostile mutations.  Its exact commit and pins are recorded in
`CLOSING_MANIFEST.json`.  A later coordinator-scope audit found the read-only
cloud inspection deviation described below; `CLOUD_SCOPE_CORRECTION.json`
supersedes only the frozen preflight's claim of clean scope compliance, not
the referee's mathematical Q0 reconstruction.

## Mid-cycle convergence check

The checkpoint fired immediately after Q0 and the independent replay.  The
opening and midpoint vectors were identical:

```text
(2/9, 1, {diag3_pair_hc1, diag3_triple_hc0}, 7,
 UNKNOWN, UNKNOWN, 6, 9)
```

Continuation failed every mandatory condition:

1. no executable, independently traceable replacement backend exists in the
   qualified resource set;
2. the exact required denominator `N` is unavailable;
3. the exact quantifier-free closed formulas, hence `s` and `d`, are
   unavailable;
4. no numeric `N/N` construction-and-replay forecast can be stated; and
5. the minimum decrease is therefore unreachable under the fixed local and
   cloud ceiling.

Q1 activation was denied.  The producer used its one allowed handoff and no
verifier-directed repair.  The laptop ceiling was not enlarged.  More cores
cannot turn missing algorithmic inputs into a hash-pinned executable job.

## Cloud and resource accounting

GCE project `project-ebd5a273-53ea-4c8b-81a` had on-demand capacity for the
authorized `n2-highcpu-16`: regional N2 quota was 200 vCPUs with zero used.
The cycle prefix `d3-srep-gate1-20260902-` had zero instances and zero disks
when checked.

There was one governance deviation,
`READ_ONLY_EXISTING_INSTANCE_SCOPE_BREACH`: during closeout the coordinator
issued a read-only unfiltered instance listing even though `WORK_ORDERS.yaml`
prohibited inspection of pre-existing instances.  It returned metadata for
the known out-of-scope `claude-control` instance.  No get, stop, start, modify,
or delete operation targeted that instance, but the listing itself breached
the declared scope.  Its final state is therefore not asserted here.
Subsequent absence claims are limited to exact cycle-prefix queries.  The
deviation does not change the Q0 mathematics, but it independently reinforces
`STOP` and means the cloud-policy gate is not reported as a clean pass.

Because Q0 failed, there was no hashed executable job manifest and launch was
forbidden.  Cloud usage, cycle instances, cycle disks, and measured cycle
cloud spend were all zero.  `CLOUD_PREFLIGHT.json` records the official price,
quota observation, maximum-runtime deletion flags, and post-gate inventory.

The measured exact-CAS, vendor-cache, and four evidence-surface footprint was
`678,882,774` bytes (`0.632258853` GiB), below the 25 GiB scratch ceiling.
The governed Git timeline from the initial opening to the frozen midpoint was
3,791 seconds, below eight hours.  Peak RAM and aggregate CPU time were not
continuously instrumented; no out-of-memory or ceiling trigger was observed.
`RESOURCE_ACCOUNTING.json` preserves those measurement boundaries.  No
external compute job was activated.

## Gate table

| gate | final result |
| --- | --- |
| canonical predecessor/source pins | `PASS` |
| repaired opening contract | `PASS`, 35/35 hostiles |
| research-cycle protocol before close | `PASS`, 20 cycles / 82 work orders |
| exact-CAS acquisition smoke | `PASS`, five tools; msolve 64/64 |
| producer qualification replay | `PASS_FAIL_CLOSED`, 8/8 tests |
| falsifier canaries | `PASS`, 23/23 hostiles |
| independent Q0 replay | `PASS`, 5/5 pins and 22/22 hostiles |
| complete global denominator/formulas | `NULL` |
| executable replacement trace | `NULL` |
| numeric full-scope forecast | `NULL` |
| Q0 acceptance | `FAIL_CLOSED` |
| Q1 activation | `DENIED` |
| cloud cleanup inventory | `PASS` for exact cycle-prefix absence; `FAIL_CLOSED` for one read-only existing-instance inspection |
| independent frozen closing referee | `PASS`, 7/7 pins and 22/22 hostiles |

## Mandatory solution-convergence verdict

Opening proof-distance vector:
`(2/9, 1, {diag3_pair_hc1, diag3_triple_hc0}, 7, UNKNOWN, UNKNOWN, 6, 9)`.

Closing proof-distance vector:
`(2/9, 1, {diag3_pair_hc1, diag3_triple_hc0}, 7, UNKNOWN, UNKNOWN, 7, 10)`.

Trajectory classification: **`STALLED`**.  The route produced reusable
formula and falsification machinery but no independently accepted
load-bearing decrease.

Automatic strategy-reset result: **`FIRED -> STOP`**.  The opening rule makes
Q0 failure and a nondecreasing close terminal for this route.

Same-route continuation justified: **`NO`**.  There is no eligible Q1 job and
the cycle may not silently pivot back to direct master CAD.

## Proof-distance and obligation delta

- Opening ledger: `2/9`.
- Closing ledger: `2/9`.
- Ledger delta: `0/9`.
- Opening load-bearing obligations: `7`.
- Closing load-bearing obligations: `7`.
- Pair residual: `UNKNOWN -> UNKNOWN`.
- Pair coverage: `UNKNOWN -> UNKNOWN`.
- Cycle handoff: `NULL`.
- Trajectory: `STALLED`.
- Final action: `STOP`.
- Selected successor: `NONE`.

All seven canonical obligations remain open: global gluing, extension labels,
strict closure, genuine relative infinity, global middle-rank replay,
`diag3_pair_hc1`, and `diag3_triple_hc0`.  The alternate
`diag3_pair_formula_diagram_comparison` edge did not close.  Literal O1--O5,
the bypass burden, the rational pair kernel, diagonal three, and 9DVL are
unchanged.

## Post-cycle resource frontier

The resource gap is now informational rather than computational.  A future
cycle would need at least one genuinely new theorem-capable input:

1. an executable and independently traceable implementation of the published
   replacement construction, or enough formal detail to implement its exact
   ordered-infinitesimal/cover trace locally;
2. a complete exact classifier for properness and pairwise incomparability of
   all parent extension regions, producing the true finite denominator; and
3. exact quantifier-free `P`-closed formulas for every compactified parent and
   genuine infinity subset.

Only after those exist would ephemeral parallel compute become useful for a
predeclared `N/N` construction and independent replay.  More laptop software,
another broad literature search, raw CAD sampling, or an unattached atlas does
not satisfy the next reopen gate.  No route was globally disproved, so
`RETIRE` is not justified.

## Mandatory post-cycle strategy evaluation

The preregistered minimum was closure of
`diag3_pair_formula_diagram_comparison`, hence `diag3_pair_hc1`, with the
load-bearing count falling from seven to at most six.  The achieved delta was
zero.  No obligation-graph edge closed or was falsified.  The first missing
inputs were narrowed to the executable backend, proper/incomparable
denominator, and quantifier-free closed compactification, but that is
informational sharpening only; the end-to-end proof burden did not decrease.

Comparable closing history is:

| cycle | closing vector suffix | trajectory/action |
| --- | --- | --- |
| global-master closure audit | `UNKNOWN, UNKNOWN, 4, 7` | `STALLED / STOP` |
| joined-Gordan tournament | `UNKNOWN, UNKNOWN, 5, 8` | `STALLED / STOP` |
| mixed-carrier feasibility | `UNKNOWN, UNKNOWN, 6, 9` | `STALLED / STOP` |
| this global formula/SREP gate | `UNKNOWN, UNKNOWN, 7, 10` | `STALLED / STOP` |

The cycle invalidated three readiness assumptions: the published algorithm
was not accompanied by a qualified executable backend in the searched public
surfaces; the abstract extension-count table was not the required proper and
incomparable denominator; and a uniform first-order closure recipe was not an
exact quantifier-free `P`-closed input tuple.  It also confirmed that cloud
capacity cannot help before those inputs produce a verifiable job.

The same load-bearing blocker survives: there is still no complete global
pair diagram, comparison, or exact pair kernel.  Another cycle would differ
only if it begins with at least one of the three genuinely new inputs listed
above; otherwise it would repeat this null gate.

| possible route | closing evidence | disposition |
| --- | --- | --- |
| continue the selected global formula/SREP route | Q0 null; backend, denominator, closed formulas, and forecast absent | **`STOP`**; same-route continuation prohibited |
| return to direct master/frontier CAD | repeats the predecessor's stopped global-master burden and does not supply the selected comparison edge | rejected; no silent pivot |
| local carrier/chart refinement, unattached atlas, or residual sampling | expressly excluded by the opening and cannot certify global coverage | rejected/prohibited |
| exact full-scope counterexample | no such counterexample was produced | unavailable; no `RETIRE` |
| start Q1 on laptop or cloud | no eligible executable or hash-pinned `N/N` job exists | denied |

Automatic reset leaves final action **`STOP`** and selected successor
**`NONE`**.  A future governed cycle requires a genuinely new theorem-capable
input from the three-item frontier above; this close grants no automatic
continuation authority.

## Durable close and publication

The in-repository close is recorded in `CLOSING_MANIFEST.json`.  The frozen
publication candidate is commit
`d8e61faae0e2318d8eb83fd26dc4140b44a149e1`; the external recovery manifest
records the exact later final-close commit and tree, avoiding a self-reference.

After the final local close commit, `make_recovery_bundle.py` creates a
complete-history bundle and JSON manifest under
`E:\Projects\9DVL Research\outputs`, then verifies byte-identical native
copies under `G:\My Drive\Projects\research-backups`.  GitHub remains
read-only: no push, pull request, CI trigger, merge, or connector write is
performed.
