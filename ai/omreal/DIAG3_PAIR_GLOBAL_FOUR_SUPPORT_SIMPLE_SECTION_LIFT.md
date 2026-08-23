# Diagonal three: simple algebraic-section lift for the four-support base

## Result

The ordered root stacks on consecutive open `t` sectors identify **1,022**
algebraic sections whose entire visible transition is one adjacent swap

```text
..., factor A, factor B, ...
              ->
..., factor B, factor A, ...
```

For every one of those sections, exact projection replay proves that:

- the section's irreducible `t` factor divides `Res_u(A,B)` with multiplicity
  exactly one;
- it divides no coefficient or discriminant obligation for any base factor;
- it is not a `u=1` boundary event; and
- the two adjacent sector stacks have the same root count.

Thus each event is a simple transversal interior crossing.  The two swapped
root branches coalesce to one point on the algebraic section, while every
other root continues without identification.

## Certified cells

Across the 1,022 completed algebraic fibers:

| cell type | count |
|---|---:|
| distinct `u`-root points | 84,794 |
| open `u` strips | 85,816 |
| **total algebraic-section base cells** | **170,610** |

Each adjacent open-sector stack contains between 54 and 109 roots.

## Independent replay

The producer uses SymPy only to locate projection-factor incidences.  The
standard-library verifier imports neither SymPy nor the producer.  It
reconstructs the 2,554-polynomial projection family with fraction-free
Sylvester resultants, reassembles the 32 open-sector shards, rediscovers all
1,022 adjacent swaps, and checks the swapped-pair resultant factor and its
multiplicity.  It separately proves the absence of coefficient,
discriminant, and `u=1` events, then rejects twelve hostile mutations.

## Remaining frontier

Exactly 671 algebraic `t` sections remain:

```text
406 no visible root-stack change
251 complex same-count transitions
 14 root-count changes
671 total
```

Those sections require direct algebraic-fiber or subresultant classification.
The 22 original `v` walls, face-compatible gluing, global closure data, and
middle-rank replay also remain open.  The honest 9DVL score remains `2/9`.

## Replay

```bash
PYTHONDONTWRITEBYTECODE=1 python \
  ai/omreal/build_diag3_pair_global_four_support_simple_section_lift.py

PYTHONDONTWRITEBYTECODE=1 python \
  ai/omreal/verify_diag3_pair_global_four_support_simple_section_lift.py
```
