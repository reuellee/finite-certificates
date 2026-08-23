# Diagonal three: raw-simple constant-stack algebraic sections

## Result

Among the 406 algebraic `t` sections whose adjacent ordered `u` stacks are
identical, exactly **363** carry one and only one raw projection event of
multiplicity one:

```text
356 pair resultants
  6 discriminants
  1 intermediate coefficient
363 total
```

None is a `u=0` or `u=1` boundary event.  A multiplicity-one interior
resultant would transpose two root branches, and a multiplicity-one interior
discriminant would change the real-root count by two.  Since the complete
adjacent stacks are identical, those events occur outside `0<u<1`; the one
intermediate-coefficient event changes neither degree nor boundary incidence.
The algebraic-section fiber therefore has the same ordered interior roots as
both adjacent sectors.

## Certified cells

For every completed constant-stack fiber, `N` continued root points divide
the open `u` interval into `N+1` strips.  The exact aggregate cell counts are
stored and independently replayed.  Forty-three unchanged-stack sections
carry simultaneous or higher-multiplicity events and remain open.

## Independent replay

The producer factors raw exact obligations with SymPy.  The verifier imports
neither SymPy nor the producer.  It reconstructs every coefficient,
discriminant, and pair resultant with standard-library rational arithmetic;
multiplies the source factorizations back; measures each raw factor valuation
by exact polynomial division; reassembles the 32 open-sector shards; and
rediscovers the 363 eligible fibers.  Eleven hostile semantic mutations must
all be rejected.

## Remaining frontier

After the 1,022 transversal crossings and these 363 constant-stack fibers,
exactly 308 algebraic sections remain:

```text
 43 complex unchanged stacks
251 complex same-count transitions
 14 root-count changes
308 total
```

Those fibers, the 22 original `v` walls, global gluing, closure data, and
middle-rank replay remain open.  The honest 9DVL score remains `2/9`.

## Replay

```bash
PYTHONDONTWRITEBYTECODE=1 python \
  ai/omreal/build_diag3_pair_global_four_support_invisible_section_lift.py

PYTHONDONTWRITEBYTECODE=1 python \
  ai/omreal/verify_diag3_pair_global_four_support_invisible_section_lift.py
```
