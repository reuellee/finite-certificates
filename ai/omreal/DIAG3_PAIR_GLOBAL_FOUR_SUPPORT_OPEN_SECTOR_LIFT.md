# Diagonal three: open-sector base lift for the four-support arrangement

## Result

The 1,693 exactly ordered projection roots cut the open `t` axis into 1,694
sectors.  This checkpoint lifts all 114 base curve factors over a rational
sample in every sector and proves the complete ordered `u`-root stack there.

```text
1,694 open t sectors
  114 base factors per sector
193,116 exact specialized factor instances
132,134 ordered u-root sections
133,828 open u strips
265,962 open-sector base cells
```

One sector has between 54 and 109 interior roots.  Of the 193,116 specialized
factor instances, 66,720 have no interior root, 120,658 have one, and 5,738
have two.  No specialization has three interior roots.

## Bounded-square boundary audit

Before claiming a bounded base lift, the construction audits the right square
boundary `u=1`.  Twenty-eight of the 114 evaluations remain nonconstant after
removing the true `t=0,1` boundary factors.  Every rational irreducible factor
of every one of those evaluations is already present in the complete
second-projection catalog.  The `u=0` evaluations are the constant
coefficients already included in that projection family.  Thus a base root
cannot enter or leave through either `u` boundary without crossing one of the
1,693 certified projection sections.

## Exact cell encoding

For each open `t` sector, the certificate derives an exact rational sample and
stores the globally ordered roots of all 114 specializations.  Every root has
an isolating interval on one common `2^-48` dyadic endpoint grid.  Consecutive
root certificates are nonoverlapping.  Thirty-two deterministic gzip shards
are pinned by byte count, SHA-256, sector range, and a digest of their exact
concatenation.  This compact encoding keeps the proof exact while avoiding
repeated large rational denominators.

Because the complete projection includes every coefficient, discriminant,
and pair resultant—and the bounded `u=1` audit is now explicit—degrees,
multiplicities, boundary incidence, and cross-factor root order cannot change
inside an open `t` sector.  The sampled stack therefore encodes the whole
sector's sign-invariant base cells, not only one vertical line.

## Independent replay

The producer uses exact SymPy isolation.  The verifier imports neither SymPy
nor the producer.  It:

1. reconstructs all 114 base factors from the second-projection source;
2. multiplies the stored `u=1` factorizations back exactly;
3. derives all 1,694 rational samples from the ordered root certificate;
4. specializes all 193,116 factor instances with rational arithmetic;
5. independently constructs Sturm sequences and proves complete root
   coverage in `0<u<1`;
6. verifies every isolating point/interval and every within-sector order; and
7. rejects twelve hostile semantic mutations.

## Consequence and next gate

The 265,962 open-sector base cells are below the pinned 1,000,000-cell
ceiling.  The remaining base-CAD step is qualitatively narrower: lift the 114
base factors over the 1,693 algebraic `t` sections and attach those fibers to
their adjacent certified sector stacks.  Lifting the 22 original `v` walls,
face-compatible gluing, global closure data, and middle-rank replay remain
open.  The honest 9DVL score remains `2/9`.

## Replay

```bash
PYTHONDONTWRITEBYTECODE=1 python \
  ai/omreal/build_diag3_pair_global_four_support_open_sector_lift.py

PYTHONDONTWRITEBYTECODE=1 python \
  ai/omreal/verify_diag3_pair_global_four_support_open_sector_lift.py
```
