# Diagonal three: simultaneous multi-crossing algebraic sections

## Result

The first two surviving four-support domains have **240** additional exact
algebraic `t`-section lifts.  These are precisely the remaining same-count
sections whose raw projection events are all pair resultants of multiplicity
one, with no coefficient, discriminant, `u=0`, or `u=1` event.

```text
1,549 raw-simple resultant events
1,390 visible order inversions
  549 interior collision groups
  240 completed algebraic t sections
```

The collision groups range from ordinary double crossings to one
ten-branch concurrence.  Every group is a complete inversion clique.  The
completed fibers contain 19,922 distinct `u` root points and 20,162 open
strips, adding **40,084** exact base cells.

The algebraic frontier falls from 308 to **68** sections:

```text
43 complex unchanged stacks
11 exceptional same-count transitions
14 root-count changes
68 total
```

This does not perform the `v` lift, glue the square-pyramid supports, or close
the global pair invariant.  The honest 9DVL score remains `2/9`.

## Multi-crossing lemma

Let `t0` be one isolated projection section and suppose that, in the adjacent
open `t` sectors, all roots in `0<u<1` are simple.  Tag repeated roots of each
base factor by their within-factor order.  Assume:

1. no coefficient, discriminant, or `u`-boundary projection event occurs at
   `t0`;
2. every raw pair resultant containing the section factor contains it with
   multiplicity one; and
3. every inversion between the two tagged root orders belongs to such a raw
   resultant event.

Then every tagged root branch continues uniquely to `t0`.  A collision in the
open `u` interval is transverse, because a repeated resultant factor or a
discriminant event has been excluded.  It therefore reverses the order of its
two branches.  Conversely, a changed order forces a collision at `t0`, since
the complete projection catalog contains no event in either adjacent open
sector.

The inversion graph is thus the exact graph of interior collisions.  Equality
at `t0` is transitive, so each connected component must be a clique and all
its branches meet at one `u` value.  A clique on `k` branches replaces `k`
nearby root points by one section point.  If an adjacent sector has `N` roots
and the collision cliques have sizes `k1,...,kr`, the section has

```text
N - sum(ki - 1)
```

distinct root points and one more open strip.  Raw resultant events not
appearing as inversions are necessarily outside the open `u` interval: a
simple interior event would reverse the corresponding tagged order.

## Exact replay

The producer uses SymPy only to factor the raw projection obligations.  The
independent verifier imports neither the producer nor SymPy.  It reconstructs
all coefficients, discriminants, and 6,441 pair resultants with integer
polynomial arithmetic; measures raw factor valuations; reassembles the 32
ordered-sector shards; tags repeated roots; recomputes every inversion graph;
and proves that all 549 connected components are cliques.  Twelve hostile
semantic mutations must all be rejected.

```bash
PYTHONDONTWRITEBYTECODE=1 python \
  ai/omreal/build_diag3_pair_global_four_support_multi_section_lift.py

PYTHONDONTWRITEBYTECODE=1 python \
  ai/omreal/verify_diag3_pair_global_four_support_multi_section_lift.py
```

The next exact target is the 68-section residue.  The eleven same-count cases
carry coefficient events or repeated raw resultants; the fourteen
root-count-changing cases require discriminant or boundary-aware local
models; and the forty-three unchanged cases require an exact proof that their
higher-multiplicity events are invisible or an explicit section fiber.
