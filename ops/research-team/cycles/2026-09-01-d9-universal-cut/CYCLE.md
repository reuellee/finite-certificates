# Universal D9 feasible-component cut opening cycle

Date opened: 2026-09-01 UTC

Canonical base revision: `cbe84ccd7273252c81fd4da17ee360a284d2a2a6`

Canonical base tree: `da3cd6feca1052ea14ed5036413c72b8f7fadc2a`

Opening theorem ledger: `2/9`

Selected target: `D9_UNIVERSAL_FEASIBLE_COMPONENT_CUT_GATE1`

## Strategy decision

Five independent competitors and a rubric-first referee compared theorem-wide
D9, fixed-family D9, global-order-two D8, universal-localization D3, and a D3
Nullstellensatz canary.  The referee selected a hybrid scored `82.4/100`:
retain the theorem-wide D9 target and use the exact `S12,37` normal-link data
only as adversarial replay.  A standalone weighted-link continuation scored
`39.4/100` and is rejected because it has no global-quantifier bridge.

## Bounded target

For every realizable `UOM(4,8)` parent `M` and every proper,
pairwise-incomparable nine-family `S` with consistent active literals, prove
the following reduction or stop fail-closed:

> If two connected components of the exact active sector `H_S` both meet the
> simultaneous feasibility locus `F_S`, then a source-reconstructible minimal
> separator witness exists in a finite obstruction schema whose cases are
> completely generated from the 13 residual wall types, support-minimal Gordan
> circuits, signed multiwall incidence, recursive boundary strata, and genuine
> infinity.

Only after that coverage theorem is independently replayed may the cycle test
every schema instance for exact infeasibility or materialize an exact global
separator.

Positive endpoint: every covered obstruction is exact `UNSAT`, the reduction
is universal, and the independent verifier proves diagonal nine.  Negative
endpoint: an exact parent/family, two feasible witnesses, and a
coverage-certified separator disprove diagonal nine.  Null endpoint: the first
uncovered cut, multiwall, transport, recursive-facet, or infinity mode plus a
complete survivor manifest.  Timeout endpoint: a deterministic processed and
pending schema frontier.  No local or fixed-family endpoint changes the
theorem ledger.

## Opening gate

The opening gate has a strict 12-hour / 64-CPU-hour / 16-GiB ceiling and stops
unless all of the following are proved and independently replayable:

1. every global feasible-component cut maps to the finite obstruction schema;
2. signs, duplicate occurrences, charts, properness, multiwalls, recursive
   facets, and infinity survive the reduction;
3. the abstract disconnected polynomial countermodel is rejected for an
   explicit hypothesis absent from that model;
4. the `S12,37` opposite-parent-form and factor-8552 recursive-facet no-go
   artifacts replay as hostile canaries, not as global separators;
5. source-derived replay is portable without requiring the unavailable
   historical referee object `ca730426cdd5847ae262ddc29c6f4ae98369eba3`.

Stop immediately at the first failed coverage lemma, hostile countermodel,
more than 10,000 obstruction types, more than 250,000 exact instances,
non-independent replay, missing portable provenance, or any resource ceiling.
Only an accepted opening gate authorizes the 72-hour / 320-CPU-hour main
obstruction census.

## Roles and ownership

- coordinator: this cycle control plane, integration, ledger and durable
  checkpoint;
- structural prover: `ops/team/d9-universal-cut-prover/`;
- circuit/combinatorics prover: `ops/team/d9-universal-cut-circuits/`;
- boundary and transport prover: `ops/team/d9-universal-cut-boundary/`;
- falsifier: `ops/team/d9-universal-cut-falsifier/`;
- certificate engineer: `ops/team/d9-universal-cut-certificate/`;
- closing referee: activated only at a frozen integrated head and owns
  `ops/team/d9-universal-cut-referee/`.

No worker may edit this cycle directory, canonical state, theorem ledger, or
another worker's surface.  GitHub is read-only.  The ChatGPT Library branch is
canonical and Google Drive `Projects/research-backups` is the recovery mirror.

