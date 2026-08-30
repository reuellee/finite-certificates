# D4-S53 constructive track: complete structural null

## Outcome

This track is **inconclusive** and makes no claim-level reduction.  An exact
independent replay reconstructs the complete canonical B31-resistant class:
`800,240` labeled supports in `53` `S_8` orbits, split as four size-four and
forty-nine size-five orbits.  Every one remains a D4-S53 survivor.

The pre-existing partial discovery script was preserved and completed.  It
now generates `STRUCTURAL_SCAN.json`; the separate
`verify_structural_scan.py` imports no discovery code and independently
reconstructs the full `1,715,980 / 130 = 915,740 / 77 + 800,240 / 53`
partition and every structural record.

## Tested signed route: a four-common-apex shear

Say that `e` is dominated by `f` when every support triple containing `e`
also contains `f`.  If four distinct moving labels are dominated by one
fixed apex `f`, the four shears

`y_e -> y_e + t_e y_f`

fix every signed third exterior product in the support.  Consequently they
preserve every nonnegative Gordan dependence, including zero-weight faces.
After quotienting by the retained rays, the parent-safe fiber is an open
subset of `R^4`.  Every parent bracket is affine jointly in all four shear
parameters because each term of degree at least two repeats `y_f`.  Each
fiber component is therefore open convex and contractible, so its compact-
support cohomology vanishes below degree four.  Proper base change and the
compact-support Leray spectral sequence would give `H_c^q=0` for `q<=3`.
This argument is signed, includes structural/residual walls inside the
uniform parent cell and closed weight faces, and does not trivialize a global
orientation local system.

The exact scan finds this premise on **zero of the 53 orbits**.  Thus the
lemma is a failed route on D4-S53 and is not reported as a strict reduction.

## Complete predicates on all 53 representatives

`STRUCTURAL_SCAN.json` lists every representative and its orbit size, degree
sequence, dominance arrows, occurrence masks/classes, and the following
predicate values.

| Predicate | Exact result | Consequence |
| --- | ---: | --- |
| prior B31 | 0/53 | target lock reproduced |
| four movers, one common fixed apex | 0/53 | valid signed convex-fiber lemma has empty target coverage |
| four distinct fixed-apex movers | 32/53 | signed normals are invariant, but profiles are only `2+2`, `2+1+1`, or `1+1+1+1` |
| degree-one plane plus two external light pencils | 53/53 | four support-preserving parameters exist, but only separate convexity follows |
| no four-distinct-mover fixed-apex assignment | 21/53 | elementary domination route stops even before topology |

The 32 weaker four-shear orbits are not removed.  Their block profiles do not
contain `3+1` or `4`; the hostile square has one-dimensional `H_1` despite
separate convexity.  Likewise, the universal degree-one-plane plus two-pencil
construction on all 53 is exactly the previously identified `2+1+1`
topological gap, not a vanishing theorem.

## Canary audit

The independent checker exercises all contract canaries:

- `actual_signed_survivor`: the row-2599 NPZ exactly verifies the positive
  minimal support `123/134/267/258/468` in a proper pairwise-incomparable
  four-family;
- `hostile_split_remerge`: the two-parallel-edge boundary has rank one and
  retains its anti-diagonal cycle;
- `hostile_separate_convexity`: the square incidence has rank three and one
  nonzero cycle;
- `orientation_local_system`: a circle cellular differential is `1-h`, so
  trivial and sign holonomy give different rational ranks and no global
  trivialization is assumed;
- `null_out_of_domain`: `123/124/125/126/127` omits label 8 and is rejected.

## Failed lemmas, blocker, and next discriminator

The four-common-apex premise is absent.  Four arbitrary fixed-apex shears and
the degree-one-plane plus two-pencil construction preserve signed circuit
data but do not control the top component sheaf: separate convexity permits
an `S^1`, and component escape permits a signed split--remerge anti-diagonal.
Unsigned occurrence classes and dominance counts cannot repair this gap.

The next discriminator must therefore be signed/topological: compute the
orientation-holonomy differential for actual admissible occurrences of the
53 shapes (starting with the pinned row-2599 survivor), on a compatible
compactification of the **entire** closed circuit piece.  A subset topology
still needs the full-piece inclusion map; another support-only predicate is
not progress.

## Replay and nonconsequences

From the repository root:

```console
PYTHONDONTWRITEBYTECODE=1 python \
  ops/team/diag4-s53-prover/generate_structural_scan.py \
  --output /tmp/diag4-s53-STRUCTURAL_SCAN.replay.json
cmp ops/team/diag4-s53-prover/STRUCTURAL_SCAN.json \
  /tmp/diag4-s53-STRUCTURAL_SCAN.replay.json
PYTHONDONTWRITEBYTECODE=1 python \
  ops/team/diag4-s53-prover/verify_structural_scan.py
sha256sum -c ops/team/diag4-s53-prover/MANIFEST.sha256
```

This result does not prove or refute D4-S53 or D4-SP, does not remove any of
the 53 orbits, does not compute `H_c^3` of an entire closed piece, and does
not address multi-piece terms, adjacent degrees, compactification maps,
restriction exactness, diagonal four, or the `2/9` theorem ledger.
