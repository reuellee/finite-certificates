# D3 orbit 5563 prover: terminal first-gate null

Date: 2026-08-30 UTC

Track: `diag3-orbit5563-prover`

Outcome: **`null`**. The exact type/frame/diagonal-`S_8` quotient manifest is
complete, but the required all-parent closure-stratum transport and attachment
atlas does not exist in the pinned inputs. Under the signed work order this is
a terminal first-gate result. No local roadmap, collar, clipped-wall,
macrobox, component, or infinity computation was started.

The unresolved row count remains `1,162,302`, and no theorem-ledger change is
recommended.

## Exact quotient theorem

Let `G=S_8`, let

```text
P = {5563,16134,19284},
```

and let `O=G.P` under the authenticated primitive-factor action. Exact
enumeration of all `40,320` label permutations proves

```text
Stab_G(P) = {identity},        |O| = 40,320.
```

Fix one of the `2,604` realizable unlabelled parent types `T`. A raw parent
frame is an element `f in G`. Let `A_T` be the projected permutation
automorphism group of the parent reorientation class. The labeled parent orbit
is `G/A_T`, not `G`: raw frames in one right `A_T`-coset represent the same
labeled parent. The simultaneous domain is

```text
D_T = (G/A_T) x O.
```

The left diagonal action is

```text
h.(T,[f],g.P) = (T,[h*f],(h*g).P).
```

It is free: an element fixing a pair fixes `g.P`, and the stabilizer of every
point in the torsor `O` is trivial. Every orbit meets the slice whose triple
coordinate is `P`: apply `g^{-1}` to `(T,[f],g.P)`. The intersection is unique,
because two such gauge choices differ by an element of `Stab_G(P)`. Thus

```text
D_T/G  <-->  {(T,[f],P) : [f] in G/A_T}
```

by the exact gauge map

```text
(T,[f],g.P) |--> (T,[g^{-1}*f],P).
```

Consequently type `T` contributes exactly

```text
40,320 / |A_T|
```

quotient classes. Each class has exactly `|A_T|` raw frame representatives.
The identity stabilizer of `P` proves freeness of the simultaneous diagonal
action; it does **not** make every raw parent frame a singleton quotient class.

The projected parent automorphisms are recomputed exactly. The chirotope
canonicalizer uses

```text
G' = S8 x {0,1}^8 x {0,1}.
```

For rank four on eight elements the sign-action kernel has order `2`, generated
by reorienting all eight elements. For every catalog type the exact full
stabilizer order is checked to equal `2*|A_T|`, the projected achieving-
permutation count equals `|A_T|`, and `|A_T|` divides `40,320`. All `2,604`
reorientation-canonical keys are distinct.

Burnside now reconciles each compressed row. The right action of `A_T` on the
raw frame set `G` is free, so only the identity fixes a frame and

```text
(1/|A_T|) * sum_(a in A_T) |Fix_G(a)| = 40,320/|A_T|.
```

The complete histograms are:

| `|A_T|` = raw multiplicity | parent types | quotient classes | raw contribution |
| ---: | ---: | ---: | ---: |
| 1 | 2,382 | 96,042,240 | 96,042,240 |
| 2 | 183 | 3,689,280 | 7,378,560 |
| 3 | 10 | 134,400 | 403,200 |
| 4 | 16 | 161,280 | 645,120 |
| 6 | 3 | 20,160 | 120,960 |
| 8 | 6 | 30,240 | 241,920 |
| 12 | 1 | 3,360 | 40,320 |
| 16 | 1 | 2,520 | 40,320 |
| 24 | 2 | 3,360 | 80,640 |
| **total** | **2,604** | **100,086,840** | **104,993,280** |

Thus the number of quotient classes and the sum of their raw multiplicities
are different exact numbers:

```text
number of quotient classes       = 100,086,840
sum of raw class multiplicities  = 104,993,280 = 2,604 * 40,320.
```

`TYPE_FRAME_S8_QUOTIENT_MANIFEST.json` records every type separately. Each
compact row records its pinned catalog-record index, projected automorphism
order (also the per-class raw multiplicity), and quotient-class count. The
whole catalog digest pins every chirotope and stored matrix; a separate
detailed-reconciliation digest seals the independently reconstructed
canonical chirotope, sign stabilizer, and entry-level source identities. The
class counts and multiplicities are independently summed; no raw frame
presentation is uncovered. The manifest also pins exact semantic digests for
the lexicographic `S_8` enumeration and the complete hard-triple orbit.

The stored matrix in each catalog record authenticates its finite sign
representative. It is not a finite cover of the corresponding realization
space and is not used as component, rank-drop, closure, or infinity evidence.

## Transport contract: exact interior, missing closure

Three transport statements hold over every interior point, not merely at the
stored matrices.

1. For every catalog type `T`, frame `f`, point `x in X_T`, and four-subset
   bracket, the bracket is nonzero with the fixed chirotope sign. Relabeling
   changes it only by the exact permutation parity. This is the defining
   quantifier of a fixed uniform realization space.
2. For every `T`, `f`, and `x in X_T`, the first four frame columns form a
   basis and all four replacement minors for the fifth frame column are
   nonzero. Exact Cramer normalization therefore supplies the frame chart at
   every interior point.
3. For every `h in S_8`, the authenticated occurrence-to-primitive-factor map
   is well defined under `triple_map(h)`. The replay transports the parent
   frame and all three residual-factor formulas simultaneously.

These facts do not supply the required closure transport. The smallest
missing object is one exact

```text
all_parent_closure_stratum_transport_and_attachment_atlas
```

with the following quantifier: for every one of the `2,604` types and every
one of its `40,320` frames, give a complete stratified Hausdorff
compactification, charts covering every required closure stratum, and
transition/attachment maps commuting with the `S_8` factor transport. The
atlas must cover all parent-wall, chart-divisor, coordinate, rank-drop,
extra-factor, simultaneous-wall, and true-infinity points, and it must
distinguish true parent infinity from artificial work boundaries.

The exact uncovered set is therefore

```text
union over (T,f) of every required residual-triple closure stratum
and attachment in Xbar_(T,f) \ X_(T,f).
```

No member of that all-parent union is promoted from a catalog matrix or local
box. `PARENT_CONTRACTIBILITY_AUDIT.md` controls the topology of each open
parent space but supplies no compactification or stratum atlas. The pinned
boundary-stratification calculation has only its declared symbolic/local
scope. The pinned full-space feasibility gate remains `FAIL_CLOSED` and still
requires a complete critical census and frontier attachments.

This missing single atlas object makes gate layer 2 fail. Because layer 1 is
complete, the contract classifies the result as `null`, not `timeout`.

## Hostile canaries

The replay checks thirteen fixtures, including every named work-order canary.

- A complete reconstructed quotient and the terminal-null contract accept.
- Removing one raw multiplicity and recomputing the semantic seal rejects.
- Forcing a nontrivial parent automorphism order to identity rejects.
- Claiming a nontrivial hard-triple stabilizer and recomputing the seal
  rejects.
- Promoting a stored matrix to full-space coverage rejects.
- Marking closure transport complete without an attachment artifact rejects.
- An artificial scope boundary cannot be relabeled true infinity.
- Both exact clipped-wall results remain pinned and reject the macrobox-20
  `[3468]=0` attachment.
- `omitted_component`, `unsound_edge`, `positive_exit`, and
  `compact_component` payloads are all rejected before evaluation because a
  terminal first-gate null prohibits topology claims.

## Replay

From the repository root:

```bash
PYTHONDONTWRITEBYTECODE=1 \
  python3 ops/team/diag3-orbit5563-prover/verify_diag3_orbit5563_prover.py
```

Expected terminal lines:

```text
PASS exact quotient manifest: 100086840 classes; raw multiplicities sum to 104993280
PASS parent automorphism/Burnside histogram: 1:2382 2:183 3:10 4:16 6:3 8:6 12:1 16:1 24:2
PASS hard presentation stabilizer=identity and orbit=40320
PASS diagonal gauge slice is free, exhaustive, and unique
MANIFEST_SEMANTIC_SHA256 8182a82272de1b6a36e0052ad2310aaf2a4d1bccf96c1dbf2210a1c185e4d172
PASS interior signs/charts/factor relabeling for all points and frames
NULL missing all-parent closure-stratum transport and attachment atlas
TRANSPORT_SEMANTIC_SHA256 60f686ff659093c3d4f46e8bd01de99cff6bcef2201a7da789f42d780afdebd9
PASS 13/13 positive, null, negative, and hostile canaries
STOP no topology computation; row=1162302 ledger change=none pivot=required
```

The next cycle must pivot to a newly bounded target. This track supplies no
permission for another local box, collar, clipped-wall, or macrobox
continuation for the selected residue.
