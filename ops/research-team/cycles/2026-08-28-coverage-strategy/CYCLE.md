# Coverage-strategy research cycle — 2026-08-28

## Control plane

- Canonical remote base: `ec362dba8a912bc4749c004641aee2da0a88dc05`
  (merged pull request 38).
- Active theorem score: `2/9`; both diagonal-three invariant obligations are
  open.
- Execution policy: exact rational arithmetic, pinned raw inputs, fail-closed
  scope, hostile canaries, independent reconstruction, and no theorem-score
  promotion from bounded evidence.
- Publication policy: isolated research branch only; no pull request or merge
  in this cycle.

## Team tracks and gates

| Track | Gate | Result |
|---|---|---|
| Constructive proof | Determine whether complete retained-skeleton data can imply ambient component coverage | Exact information-theoretic no-go; the actual project coverage claim remains open |
| Falsification | Search accepted paths for information lost by endpoint or one-dimensional summaries | Edge 39 has 118 factors with two interior roots and equal endpoint signs; exact bounded null on 6,980 additional endpoint-uncrossed candidates over edges 0 and 39 |
| Certificate engineering | Emit a fail-closed coverage dependency object | Exact partition `10,844 + 1,177 + 5,803 = 17,824`; global component quotient and genuine relative-escape mapping remain missing |
| Theory and source audit | Compare proof architectures and select a bounded decisive experiment | Selected profile-universal order-two Hardt--Mayer--Vietoris compiler; selected triangle `conv(0,89,113)` |
| Independent referee | Replay accepted inputs and challenge scope | Primary artifacts passed; stale metadata and output-path portability defects were found and repaired |
| Triangle certificate | Classify every pinned factor on the selected exact two-cell | `5,665` interior-zero, `12,096` empty, `63` unresolved; `77` interior-zero factors absent from both incident edge event sets |
| Independent triangle referee | Reconstruct without importing the producer | Counts, parent residence, all 77 witnesses, and 10 hostile mutations independently replayed |

## Accepted exact result

Let

```text
x(s,t) = chart0 + s(chart89-chart0) + t(chart113-chart0),
s >= 0, t >= 0, s+t <= 1.
```

The complete simplex-Bernstein controls prove that all 70 signed row-2599
parent brackets stay strict on this closed triangle. Exact classification at
the declared depth-three ceiling gives

```text
5,665 certified interior-zero
+ 12,096 certified empty on the closed triangle
+     63 unresolved at the depth limit
= 17,824 pinned candidate factors.
```

Of the 5,665 certified interior-zero factors, exactly 77 occur on neither
compiled edge 27 nor compiled edge 39. Each of the 77 has an independently
replayed exact witness. This proves that the two-edge source tree is locally
incomplete as a wall-event detector. It does not prove that any factor has a
new global component, that the triangle covers a parent-cell component, that
its boundary is relative infinity, or that the pair or triple obligation is
closed.

## Architecture decision

The retained 40-edge source graph is a forest on 48 vertices with eight
connected components, cycle rank zero, component sizes
`19,10,8,3,2,2,2,2`, and 130 stored charts omitted. Completing the remaining
38 paths would add labelled one-dimensional trees, but it would not by itself
produce two-cells, pair/triple intersection incidence, or a coverage theorem.

The selected architecture is therefore a profile-universal order-two
Hardt--Mayer--Vietoris compiler. Its proof object must retain exact connected
components of cover pieces, pairwise intersections, and triple intersections;
all specialization maps; genuine relative-infinity incidence; and the
signature-to-membership-profile map. The compiler then targets total degree
one of the existing balanced pair complex without materializing an unnecessary
full sign-invariant arrangement.

## Next publication gate

1. Resolve the 63 depth-limit triangle factors without promoting a mixed
   Bernstein hull to a zero claim.
2. Compile and classify the third side, chart 89 to chart 113.
3. Build exact component, specialization, closure, relative-infinity, and
   signature-profile incidence for the 77 new interior-only factors.
4. In parallel, classify the global 5,803-factor feasibility residue or run a
   globally scoped factor-19069 component pilot.
5. Permit a ledger-score change only after independent replay closes both
   invariant obligations.

## Primary-source map

- S. Basu, R. Pollack, and M.-F. Roy, *Computing the First Betti Number and
  Describing the Connected Components of Semi-algebraic Sets*: contractible
  covers with pair/triple component incidences for first Betti computation.
- S. Basu and M.-F. Roy, *Divide and Conquer Roadmap for Algebraic Sets*:
  exact roadmap and prescribed-point component machinery.
- R. Hardt, *Semi-algebraic Local Triviality in Semi-algebraic Mappings*:
  finite trivialization across parameter strata.
- A. Roudneff and B. Sturmfels, *Simplicial Cells in Arrangements and
  Mutations of Oriented Matroids*: mutation connectivity context, not a
  fixed-parent coverage theorem.
- B. Sturmfels and G. Ziegler, *Extension Spaces of Oriented Matroids*:
  extension-space topology context, not the missing project-specific
  profile-labelled two-complex.

The complete source qualification and architecture comparison are recorded in
`ops/team/coverage-theory/ARCHITECTURE_AUDIT.md`.

## Evidence

- `ops/team/coverage-prover/`
- `ops/team/coverage-falsifier/`
- `ops/team/coverage-certificate/`
- `ops/team/coverage-theory/`
- `ops/team/coverage-referee/`
- `ops/team/triangle-certificate/`
- `ops/team/triangle-referee/`
