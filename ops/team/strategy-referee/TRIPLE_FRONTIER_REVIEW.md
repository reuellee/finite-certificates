# Independent referee review: triple multibox frontier canary

## Verdict

**ACCEPT**, at exactly the declared bounded-corridor scope.

Constructive commit `5ef40708218e22f1248db8b294f52b7d44c8dd0b`
correctly extends the accepted one-box triple projection canary to a connected
20-macrobox rectangular corridor, covered by 35 exact projection-certificate
boxes.  Exact parent intervals keep the whole accepted corridor in one
uniform parent cell, the fixed `d,e,h` Jacobian minor is strictly negative on
every certificate box, and the local-diffeomorphism/compact-open argument
therefore proves that every connected component of the named triple-zero set
restricted to the corridor meets its artificial outer boundary.

The exact `[3468]=g-a` witness in rejected macrobox 20 is also valid.  It is a
witness that the next macrobox crosses a genuine parent wall, not a witness
that the triple-zero set reaches that wall.  The candidate states this
nonconsequence correctly and closes no unresolved triple row.

## Reviewed revision and digests

- Exact base: `ec362dba8a912bc4749c004641aee2da0a88dc05`.
- Constructive commit: `5ef40708218e22f1248db8b294f52b7d44c8dd0b`.
- Note SHA-256:
  `541a7c843eae7fd359596698fa2fa58b74c7170ddee6b6005de6feca4b24c42b`.
- Producer SHA-256:
  `f395fbf1336a01a09524d7f172b75b64530057848af8805ac275bd2b3f4f7fcb`.
- Verifier SHA-256:
  `48219a759a3dba795919fd1fbadd447dc389add665488d6a8a4dafdfbb5be984`.
- Certificate raw SHA-256:
  `a41c3d84354bbbcb9d5b39b0899db7ad2479931f95f7363f945b9a9da0f9712a`.
- Certificate semantic SHA-256:
  `5a71b5a6144aa0ab858a5cda2fbca6ee485332954f92976f17f8ce599fd46447`.

The authenticated ledger, critical system, mapping gate, base registration,
and base certificate hashes all match the exact base.

## Clean replay

The commit was exported with `git archive` into an isolated temporary
directory.  No files from the shared working tree were used.  The committed
certificate first passed:

```text
PASS independent deterministic 20-macrobox / 35-certificate-box replay
PASS parent signs: 1400/1400 strict on accepted corridor
PASS fixed projection minor: 35/35 exact intervals strictly negative
PASS exact first frontier: macrobox 20 intersects parent wall [3468]=g-a
PASS boundary accounting: 18 outer facets / 19 macro seams / 15 split seams
PASS compact-sphere negative canary refused
PASS hostile mutations rejected 10/10
THEOREM every restricted component meets the 20-macrobox corridor boundary
SCOPE no complete orbit; unresolved=1162302; score=2/9
```

The producer was then run in the isolated snapshot.  It regenerated the
certificate with the identical raw and semantic digests.  A second verifier
run produced the identical pass transcript.

## Producer/verifier trust separation

Accept with a precise qualification.

The frontier verifier does not import or execute the frontier producer.  It
independently reconstructs:

- the deterministic direction selection;
- all macrobox centers and the first successful subdivision axis;
- every parent and projection interval record;
- both record-stream digests;
- the connected corridor bounds and seam counts;
- the fixed projection identity and sign;
- the first rejected macrobox and exact `[3468]` wall point; and
- the complete scope record and hostile mutations.

Both new programs import the previously accepted
`verify_diag3_triple_local_roadmap_canary.py` for exact sparse arithmetic,
source decoding, parent-bracket construction, interval primitives, and the
base-certificate replay.  Thus the new corridor logic is independently
implemented, but the full stack is not raw-arithmetic independent.  This is
an acceptable inherited trust boundary for the bounded canary and should be
described as “independent frontier reconstruction over the accepted base
verifier,” not as completely independent source arithmetic.

The named presentation to canonical-row mapping is likewise an authenticated
accepted dependency.  The new verifier pins the raw and semantic mapping-gate
bytes and calls the accepted base verifier; it does not independently rerun
the mapping-gate producer or its standalone proof.  No broader `S_8`
transport is claimed.

## Exact geometry audit

### 1. Corridor coverage and overlap

Pass.  Macrobox `k` has the registered radius `1/128`, and consecutive
centers differ by exactly `2/128` in the negative `a` direction.  Adjacent
closed macroboxes therefore share one complete facet without a gap or
positive-volume overlap.  Their union is one closed nine-dimensional
rectangle.

The certificate refinements cover each macrobox exactly:

```text
k=0..4:   no split       -> 5 boxes
k=5..13:  split a       -> 18 boxes
k=14..18: split c       -> 10 boxes
k=19:     split g       -> 2 boxes
total                       35 boxes
```

Each bisection consists of its two closed half-boxes sharing the mid-facet.
The accounting `19` macro seams and `15` intra-macro seams is exact.  The
union rectangle has 18 geometric outer facets.  Those facets are counted as
geometric sets, not as an atomic regular-cell boundary subdivision; that is
sufficient for the present component-to-boundary theorem but not yet for a
gluing or chain-incidence certificate.

### 2. Parent-cell proof

Pass.  Direct rational monomial intervals exclude zero with the registered
sign for all 70 normalized parent brackets on each of the 20 full
macroboxes—1,400 exact intervals.  The macroboxes form a connected union and
include the accepted base box, so the entire corridor lies in the same
connected uniform parent cell as that base canary.  No conclusion about the
row-2599 pair-branch parent cell is needed or claimed.

The closest accepted interval is `[3468]` on macrobox 19:

```text
[-9/224,-1/112].
```

It is strictly negative, so the accepted corridor itself does not reach the
parent wall.

### 3. Fixed projection sign

Pass.  The verifier reconstructs all three residual polynomials and the
147-term minor

```text
det d(q5563,q16134,q19284) / d(d,e,h).
```

Every one of the 35 covering certificate boxes has a strictly negative exact
interval.  Because those boxes cover the full corridor, the residual
Jacobian has rank three everywhere on the triple-zero set in the corridor.
The zero set is therefore smooth of dimension six there, and projection to
the complementary variables `(a,b,c,f,g,i)` is a local diffeomorphism.

The verifier also recomputes the first successful split in the declared
order `none,a,...,i`; it does not merely trust the stored subdivision choice.
Interval failure before a split is treated only as certificate failure, not
as a zero or sign change of the true minor.

### 4. Component-to-artificial-boundary implication

Pass.  Let `Q` be the closed corridor rectangle and let `C` be a connected
component of `V intersect Q` avoiding `boundary(Q)`.  Then `C` is a compact
component lying in the corridor interior and is open in the smooth
semialgebraic zero set.  The fixed projection maps it to a nonempty subset of
`R^6` that is open by local diffeomorphism and compact by continuity.  No
nonempty subset of `R^6` is both open and compact.  Hence every restricted
component meets the geometric outer boundary.

Internal macro and bisection seams are not scope boundary; the projection
certificate holds on both sides and on each shared closed face.  The exact
registered zero in macrobox 0 makes the restricted theorem nonvacuous.

All 18 outer facets remain artificial.  Boundary reach in this theorem is
not parent noncompactness and does not close the canonical row.

### 5. Exact `[3468]` frontier witness

Pass, with the scope guard below.  Rejected macrobox 20 retains the base sign
on exactly 69 parent brackets.  The remaining bracket reconstructs as

```text
[3468] = g-a
```

with exact vertex range

```text
[-11/448,3/448].
```

Linear interpolation between the recorded opposite-sign vertices at
parameter `11/14` gives the stored rational point, and direct substitution
gives `g-a=0`.  The other 69 brackets remain strict throughout that macrobox,
so the point lies on the named genuine parent-wall stratum.

This wall point is not proved to satisfy the three residual equations.  The
projection minor is deliberately not tested after the parent failure.  Thus
the result identifies the next domain frontier but does not attach a
triple-zero component to it.  The note, result handoff, and certificate scope
all preserve this distinction.

## Source and theorem accounting

Pass.  The verifier authenticates:

- named presentation `(5563,16134,19284)`;
- canonical unresolved row `(5563,4373,23221)`;
- the accepted source-mapping gate;
- unresolved count `1,162,302`; and
- source-order digest
  `a76a7c2cd6631c2d9724b450540bec7f3be6c106a41ae41f1736bbd2755a5ca4`.

The corridor covers no complete presentation, no complete canonical row, no
complete orbit, and no full parent cell.  It proves no `S_8` transport and no
genuine parent-infinity attachment.  The before/after unresolved counts are
identical and the theorem score remains `2/9`.

The deterministic branch-selection premise—absence of a canonical
materialized 1,162,302-row presentation stream—is authenticated by a pinned
statement in the accepted base documentation rather than by an exhaustive
filesystem or mathematical impossibility check.  This affects only why the
canary branch was selected, not the canary theorem.

## Hostile mutations

Pass, `10/10`.  Each mutation is re-sealed before replay, and each is rejected
by reconstructed semantics rather than by a stale top-level digest:

1. accepted macrobox count;
2. corridor axis;
3. chosen subdivision axis;
4. projection interval;
5. parent-record digest;
6. frontier factor identity;
7. frontier zero witness;
8. false global-parent-coverage claim;
9. false unresolved-count reduction; and
10. false theorem-score promotion.

The full-object equality checks also reject undeclared changes to macrobox
centers, source identities, pivot fields, seam accounting, frontier records,
or top-level schema, even though those are not separate named canaries.

## Defects and required guards

No blocking mathematical or replay defect was found.  Retain these
nonblocking qualifications:

1. **Inherited implementation trust.**  Producer and verifier share the
   accepted base verifier's arithmetic and decoders.  The new layer is
   independent of the new producer, not fully raw-source independent.
2. **No frontier attachment yet.**  `[3468]=0` is witnessed only in rejected
   macrobox 20 as a parent-domain wall.  A clipped cell still needs complete
   parent signs, the fixed-pivot certificate, an actual triple-zero terminal
   face, and exact overlap with macrobox 19 before any genuine-boundary
   attachment can be claimed.
3. **Artificial boundary only.**  The accepted component theorem terminates
   on 18 artificial facets.  A longer corridor ending on the same kind of
   facets would remain a canary, not a noncompactness proof.
4. **No regular boundary cellulation.**  Eighteen geometric facets suffice
   for the compact-open implication, but future gluing must subdivide them
   compatibly with the 19 macro seams, 15 split seams, residual strata, and
   parent-wall clip.
5. **Accepted mapping dependency.**  Source mapping is hash- and
   semantic-pinned rather than freshly independently derived in the frontier
   verifier.

## Accepted scope

The accepted result is exactly:

> On the connected 20-macrobox corridor for the authenticated named hard
> presentation, all parent signs remain strict and one fixed residual
> Jacobian pivot remains nonzero.  Every connected component of the
> triple-zero set restricted to that corridor therefore meets its artificial
> geometric outer boundary.  The first next macrobox crosses the genuine
> parent wall `[3468]=0` at an exact rational point.

No complete triple source is closed, and neither diagonal-three invariant nor
the `2/9` ledger changes.
