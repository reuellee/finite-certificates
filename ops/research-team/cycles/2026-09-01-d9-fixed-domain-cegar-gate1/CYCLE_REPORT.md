# Cycle report: D9 exact fixed-domain counterexample CEGAR gate 1

## Canonical base and target

- Base revision: `a5990bff953432a49cfa186f78e25efdb7df280b`
- Base tree: `96e75f55512f6abbc09749509a45b63adebfa456`
- Opening revision: `6fc3d4d8c4d235dbb262e56abfccb7c32dad1a39`
- Opening tree: `71ced64b12ace616e641befd5624f3b8653d217a`
- Frozen candidate: `55d284e05ab506dc2789045b13f10c3a13afb3ad`
- Frozen candidate tree: `5de3d0b4bda85a2a778e4e9c5d7aef040c41d155`
- Opening ledger: `2/9`
- Closing ledger: `2/9`
- Selected target: `D9_FIXED_DOMAIN_COUNTEREXAMPLE_CEGAR_GATE1`

## Opening strategy tournament

The mandatory tournament compared exact fixed-domain counterexample CEGAR
against projection-free adaptive component decomposition.  CEGAR won `30` to
`20`: it alone had a theorem-decisive positive endpoint inside the cycle, and
each exact path repair was independently replayable refinement information.
The adaptive route remained the reserve because its current smallest complete
product is a one-parent component object rather than a diagonal-nine result.
Exactly one route was selected.

## Role assignments and handoffs

| Role | Surface | Classification | Endpoint |
| --- | --- | --- | --- |
| coordinator | cycle directory | exact integration | tournament and scope enforced |
| constructor | `d9-fixed-domain-cegar-constructor` | exact null | two committed seeds repaired |
| falsifier | `d9-fixed-domain-cegar-falsifier` | exact negative against separator claims | 45,522 path segments |
| certificate verifier | `d9-fixed-domain-cegar-certificate` | independent `ACCEPT` | 12/12 hostile mutations rejected |
| closing referee | `d9-fixed-domain-cegar-referee` | frozen-head `ACCEPT` | `PIVOT` required |

## Exact findings

Both committed row-2599 stress families satisfy the full input quantifiers
needed for a potential diagonal-nine counterexample: nine nonempty proper
regions and all 72 ordered incomparability clauses are certified by exact
integer feasibility or Gordan witnesses.  The two candidate endpoint pairs
are not disconnected.  Exact rational one-column paths place charts `12/37`
and `37/176` in one common-feasibility component, using 22,711 and 22,811
segments respectively.

The exact endpoint is therefore
`COMMITTED_CEGAR_SEED_FRONTIER_EXACTLY_REPAIRED`, classified
`EXACT_NULL_NO_D9_COUNTEREXAMPLE`.  This exhausts the two exact CEGAR seeds
committed at the base revision.  It does not exhaust all proper nine-families,
all row-2599 chambers, all parents, or the D9 theorem domain because no
complete fixed-domain candidate generator or compactified component atlas
exists.

## Gate table

| Gate | Result |
| --- | --- |
| predecessor frozen pins and `PIVOT` mandate | `PASS` |
| exactly one tournament selection | `PASS`: CEGAR |
| theorem-domain quantifiers for seed `12/37` | `PASS`: 63 entries, 72 ordered clauses |
| exact separator disposition for seed `12/37` | `PASS`: repaired by 22,711-segment path |
| theorem-domain quantifiers for seed `37/176` | `PASS`: 63 entries, 72 ordered clauses |
| exact separator disposition for seed `37/176` | `PASS`: repaired by 22,811-segment path |
| producer-independent replay | `PASS` |
| hostile mutations | `PASS`: 7 falsifier, 12 certificate, 8 closing |
| complete fixed-domain candidate generator | `FAIL_CLOSED`: absent |
| source-realized D9 counterexample | `NOT_FOUND` |
| diagonal-nine theorem | `OPEN` |
| ledger promotion | `DENIED`; remains `2/9` |

## Obligation-graph delta

- Closed: exact path-or-separator disposition for seed `12/37`.
- Closed: exact path-or-separator disposition for seed `37/176`.
- Falsified: both sampled endpoint-separation hypotheses.
- Retired: another sampled-separator CEGAR cycle without a complete
  fixed-domain generator.
- Unchanged: complete fixed-domain candidate generation.
- Unchanged: compactified component-faithful coverage and true-boundary
  attachment.
- Unchanged: all-parent quantifiers, diagonal nine, and the theorem ledger.

The result removes two false candidate separators but does not reduce the
complete proof burden enough to claim theorem progress.

## Exact ledger delta and nonconsequences

Ledger delta: **none**.  The honest theorem ledger remains **`2/9`**, with
only diagonals one and two proved.

Nonconsequences:

- no exhaustive fixed-domain counterexample absence;
- no global common-feasibility connectivity theorem;
- no complete row-2599 chamber or component coverage;
- no diagonal-nine proof or counterexample;
- no theorem-ledger promotion to `3/9`.

## Mandatory post-cycle strategy evaluation

The bounded CEGAR seed frontier is terminal: both seeds were exactly repaired,
and repeating sampled separator selection would not change the missing global
quantifiers.  Closing verdict: **`PIVOT`**.  The sampled-separator CEGAR route
without a complete fixed-domain generator is **`RETIRE`**.

The one precise admissible successor is
`D9_ROW2599_FACTOR19069_PROJECTION_FREE_ACTIVE_MARGIN_COMPONENT_GATE1`:
compute a complete parent-resident component sample for the factor-19069 wall
over the entire strict row-2599 parent component, retain all 70 parent-sign
path tags and every true-boundary stratum, and classify every component by
attachment or nonattachment to the fixed 40-edge skeleton.  This is the
projection-free adaptive challenger from the opening tournament, now narrowed
to a producer-independent terminal gate.

## Publication revision and backup manifest

The frozen local candidate is
`55d284e05ab506dc2789045b13f10c3a13afb3ad`.  GitHub was not written, CI was
not triggered, and no pull request or merge was created.  The final local
referee commit and its Google Drive recovery mirror are recorded by the
external checkpoint manifest created after this report is committed; the
mirror target is restricted to `Projects/research-backups`.
