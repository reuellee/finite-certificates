# Cycle report: D9 row-2599 factor-19069 singular-df multihomogeneous gate 1

## Canonical base, frozen review, and ledger

- Base revision: `9c9a78c4225a39803a0a5ac7e4e204d9b9f3773d`
- Base tree: `af4bdbfc8f89e950936d59e6b0737b12eb5bdfb5`
- Opening revision: `a2860f3f6436f573a913fc8ca6312b944212aadd`
- Opening tree: `56f179cea8b8664156ee2dfcd6a9052d95e3b78e`
- Frozen candidate: `be63abbb49b23134df615eefd646fe6f1c2863e7`
- Frozen candidate tree: `bd9e78d8f640a2bf8c2d69afb70f3e571878b963`
- Closing-evidence revision: `47f8b5ff93332cf49afd231747512d04c9ee172a`
- Integrated referee revision: `0db69d9ac7021b621205e7c62f7644f396d02258`
- Opening ledger: `2/9`
- Closing ledger: `2/9`
- Selected target:
  `D9_ROW2599_FACTOR19069_SINGULAR_DF_MULTIHOMOGENEOUS_DECOMPOSITION_GATE1`

## Opening strategy and scope

The predecessor fixed the original nine-coordinate singular ideal

`J=<f_19069,df/da,df/db,df/dc,df/dd,df/de,df/df,df/dg,df/dh,df/di>`

as the first branch to resolve before returning to the nine regular critical
charts. This cycle preregistered an exact check of the asserted `(2,2,2)`
multihomogeneous/multiaffine structure, followed by a characteristic-zero
component decomposition and componentwise saturation against all 70 parent
factors only if that source contract survived. The 70-inverse-variable
discovery route, sampler-only escalation, active-margin subsets, sampled
CEGAR, projection, symmetry, ambient-orbit transfer, and unfiltered multiwall
enumeration remained retired or prohibited. Numerical and modular probes were
non-evidence.

## Role assignments and handoffs

| Role | Surface | Classification | Endpoint |
| --- | --- | --- | --- |
| coordinator | cycle directory | exact integration | one target, frozen pins, no-hardlink replay |
| constructor | `d9-factor19069-singular-df-multihomogeneous-constructor` | exact source-structure falsification | first unresolved source-contract branch; 34/34 mutations rejected |
| falsifier | `d9-factor19069-singular-df-multihomogeneous-falsifier` | independent exact rejection | affine homogeneity and multiaffinity rejected; 59/59 mutations rejected |
| independent verifier | `d9-factor19069-singular-df-multihomogeneous-certificate` | producer-independent `ACCEPT` | null only; 35/35 mutations rejected |
| closing referee | `d9-factor19069-singular-df-multihomogeneous-referee` | frozen-head `ACCEPT_FAIL_CLOSED_NULL` | 24/24 mutations rejected; `PIVOT` |

## Exact source findings

All lanes reconstruct the same primitive 108-term factor over
`Q[a,b,c,d,e,f,g,h,i]` and the same nine derivatives. The derivative term
counts are `54,44,54,50,50,50,36,61,36`. The affine factor has total-degree
support `{4,5,6}`. For the blocks `(a,b,c)|(d,e,f)|(g,h,i)`, its exact block
degree supports are `{1,2}`, `{1,2}`, and `{0,1,2}`. Ninety-seven of its 108
terms do not have block degree `(2,2,2)`. The per-coordinate maximum exponents
are `(2,1,2,2,2,2,1,2,1)`, with 44 terms containing at least one squared
coordinate. Thus:

- `(2,2,2)` is the affine block-degree upper bound, not an affine
  multihomogeneity statement;
- the affine polynomial is not coordinate-multiaffine; and
- the preregistered affine source premise is exactly false.

The constructor nevertheless supplies the canonical three-block
homogenization in

`Q[a,b,c,u,d,e,f,v,g,h,i,w]`.

Each of its 108 terms has block degree exactly `(2,2,2)`, and setting
`u=v=w=1` recovers `f_19069` exactly. The independent certificate and referee
reconstruct this identity. The homogenized polynomial is multiquadratic, not
multiaffine, and the identity alone is not a primary decomposition, saturation
certificate, real-residence proof, or connected-parent tag.

## Fail-closed decomposition and saturation frontier

The stop rule fires at
`MH-B00-AFFINE-SOURCE-STRUCTURE-CONTRACT`, semantic SHA-256
`73be706424b840acac8130f703649621a3092844bfefd3d25aa765e44f49712d`.
The original Jacobian ideal is exactly reconstructed, but the proposed
affine-structure attack is invalid as stated. No characteristic-zero primary
or equidimensional decomposition is started or accepted.

Accordingly:

- resolved singular components: `0`;
- pending singular component count: unknown;
- exact component equations, dimensions, degrees, and multiplicities: none;
- embedded-component census: unresolved, with none discarded;
- componentwise parent-factor tests: `0` completed of `70` required for each
  future component;
- exact strict real residence: unresolved;
- connected row-2599 parent-component tags: unresolved; and
- exact positive-dimensional real singular component: neither certified nor
  excluded.

The artifact retains all 70 exact parent-factor records and source tags. It
also preserves the predecessor's 3,375 compactification support strata, ten
proper nonexcluded boundary candidates, 40 fixed-skeleton edges, 2,800
parent-tag checks, and the complete inherited null frontier. No singular,
embedded, boundary, or null stratum is silently removed.

A coordinator-side characteristic-zero Gröbner probe on the ten-generator
ideal returned no basis within its short bounded run and was interrupted. It
produced no accepted artifact, supports no claim, and is not part of replay.
No numerical or modular probe was promoted.

## Gate table

| Gate | Result |
| --- | --- |
| exact base/tree, opening ledger, and predecessor pivot | `PASS` |
| exactly one selected target | `PASS` |
| target protocol and authorization | `PASS`: 4/4 lanes |
| exact factor reconstruction | `PASS`: 108 terms in nine affine coordinates |
| exact singular ideal reconstruction | `PASS`: `f` plus nine derivatives |
| affine `(2,2,2)` homogeneity premise | `REJECTED EXACTLY`: supports `{1,2} x {1,2} x {0,1,2}` |
| affine multiaffinity premise | `REJECTED EXACTLY`: six coordinates have exponent two |
| explicit canonical trihomogenization | `PASS_SCOPE`: 12 variables, 108 terms, degree `(2,2,2)`, exact dehomogenization |
| characteristic-zero primary/equidimensional decomposition | `NOT_STARTED_AFTER_MANDATORY_SOURCE_STOP` |
| component equations/dimensions/degrees/multiplicities | `NONE` |
| componentwise saturation against 70 parent factors | `0` component-factor tests; all 70 factors retained |
| strict real and connected-parent residence | `UNRESOLVED` |
| singular/embedded/boundary/null strata accounting | `PASS_SCOPE`: none discarded |
| constructor hostile mutations | `PASS`: 34/34 rejected |
| falsifier hostile mutations | `PASS`: 59/59 rejected |
| producer-independent certificate | `PASS`: 35/35 rejected; null only |
| clean no-hardlink replay | `PASS`: distinct file identities, link counts one, clean worktree |
| frozen-head closing referee | `ACCEPT_FAIL_CLOSED_NULL`: 24/24 rejected |
| diagonal-nine theorem or counterexample | `OPEN / NOT_FOUND` |
| ledger promotion | `DENIED`; remains `2/9` |

## Obligation-graph delta

- Closed: exact reconstruction of the original factor-19069 Jacobian ideal.
- Closed: exact classification of the affine degree structure; the inherited
  `(2,2,2)` record is a block-degree bound, not affine homogeneity.
- Closed: exact falsification of affine coordinate multiaffinity.
- Closed: exact 12-variable canonical trihomogenization and dehomogenization
  identity, with its nonconsequences pinned.
- Narrowed: the first unresolved branch from a vague multihomogeneous attack
  to an explicit trihomogenized Jacobian-chart decomposition whose chart
  equivalence must be proved before decomposition claims.
- Falsified: using the affine source directly as a homogeneous or multiaffine
  system.
- Unchanged: characteristic-zero decomposition, embedded primes, component
  invariants, all 70 componentwise saturations, strict real residence,
  connected-parent tags, boundary attachment, the regular critical charts,
  diagonal nine, and all theorem-global obligations.

## Exact ledger delta and nonconsequences

Ledger delta: **none**. The honest theorem ledger remains **`2/9`**, with only
diagonals one and two proved. No theorem-level counterexample was found.

Nonconsequences:

- no complete characteristic-zero primary or equidimensional decomposition;
- no complete component equations or embedded-component accounting;
- no singular-component dimension, degree, or multiplicity;
- no componentwise 70-factor incidence or saturation classification;
- no proof that the strict singular branch is empty;
- no exact positive-dimensional real singular component;
- no strict real residence or connected row-2599 parent tag;
- no promotion of the nine regular critical charts to the active frontier;
- no complete boundary wall-germ or global attachment classification;
- no diagonal-nine proof or counterexample; and
- no theorem-ledger promotion to `3/9`.

## Mandatory post-cycle strategy evaluation

The cycle returned a terminal structural falsification for the route as
stated. Repeating an affine "multihomogeneous/multiaffine" decomposition would
reuse a false premise. Retrying the undifferentiated 79-variable localization
or increasing a blind Gröbner budget would repeat retired blockers. Closing
verdict: **`PIVOT`**.

The exactly one admissible successor is
`D9_ROW2599_FACTOR19069_EXPLICIT_TRIHOMOGENIZED_JACOBIAN_CHART_DECOMPOSITION_GATE1`.
It must start from the pinned 12-variable degree-`(2,2,2)` polynomial, prove
the Euler/dehomogenization equivalence between its projective Jacobian chart
`u=v=w=1` and the original affine ideal, retain every chart-at-infinity
component as boundary data, and only then compute a characteristic-zero
primary/equidimensional decomposition. It must contract every affine-chart
component to `Q[a,...,i]` and test it componentwise against all 70 parent
factors. Its positive endpoint is exact singular emptiness on the strict
connected row-2599 parent component; its negative endpoint is an exact
positive-dimensional real singular component with all strict signs and a
pinned connected-parent path; its null endpoint is the first source-pinned
projective/affine Jacobian component or chart-contraction branch that remains
unresolved. This differs from the current route by using the explicit correct
homogenized source and proving the chart transfer instead of assuming affine
homogeneity or multiaffinity.

## Replay, publication, and recovery

The candidate was cloned with `--no-hardlinks --no-local`, checked on the
exact candidate branch/revision, and replayed through canonical V6, the
opening audit, target-only protocol plus hostile canaries, constructor,
falsifier, producer-independent certificate, `git diff --check`, and clean
worktree checks. Source and replay result files have link count one and
distinct file identities. The closing referee independently reconstructs the
candidate at its exact commit/tree and accepts the null only.

GitHub remained read-only. No push, pull request, CI trigger, or merge was
performed. The durable working checkpoint remains
`E:\Projects\9DVL Research`. A final local Git bundle and SHA-256 manifest are
written under `E:\Projects\9DVL Research\outputs`. Native mirroring to
`G:\My Drive\Projects\research-backups` is optional, byte-length and SHA-256
verified only if permitted, and nonblocking on denial. The Google Drive
connector was not used.
