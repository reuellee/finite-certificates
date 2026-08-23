# Regular residual algebraic-section lift

This checkpoint completes another exact layer of the bounded row-2599
four-support base complex.  It closes 40 of the 68 algebraic `t` sections left
after the simultaneous multi-crossing lift:

```text
36 unchanged adjacent stacks
 4 same-count transitions
40 completed regular residual sections
```

The global 9DVL ledger remains **2/9**.  This is a local pair-complex
certificate.  It does not lift the 22 original `v` walls, glue the two covered
square-pyramid supports to all faces, label the resulting cells, or discharge
the invariant triple obligation.

## Regular-event lemma

Fix an isolated squarefree projection section `p(t)=0`.  Suppose:

1. no `u=1` boundary event occurs;
2. no discriminant or leading-`u`-coefficient event occurs;
3. every raw pair resultant containing `p` has multiplicity one; and
4. any remaining coefficient event is a non-leading coefficient.

Then every real common root in `0<u<1` is transverse.  A transverse common
root reverses the order of its two tagged root branches across the section, so
it appears as an inversion between the exact adjacent-sector stacks.
Conversely, continuity forces every tagged inversion to meet on the section.
Connected inversion components must be cliques: one tagged branch cannot meet
two different `u` values at the same `t`, and every pair in a simultaneous
collision reverses order.

It follows that:

- an unchanged tagged stack has no interior collision;
- a changed same-count stack is obtained by collapsing each inversion clique
  to one section root; and
- multiplicity-one resultant events that produce no tagged inversion are
  nonreal or outside the bounded `u` interval and do not change the section
  stack.

A non-leading coefficient may vanish without changing the degree in `u`.
With the leading coefficient, discriminant, resultants, and bounded boundary
already controlled, such a zero is not a root-critical event.

## Exact census

The completed tranche has:

```text
197 raw events
193 multiplicity-one pair resultants
  4 harmless non-leading coefficient events

 30 visible tagged inversion edges
163 invisible simple resultants
 12 interior collision cliques

2,285 section u-root point cells
2,325 open u strips
4,610 exact section base cells
```

The same-count collision profiles are:

```text
2+2+2+2       one section
2+2+2+3+5     one section
2+4           one section
3             one section
```

The four coefficient events occur strictly below the leading `u` degree:
`(base, coefficient degree) = (18,1), (82,1), (65,1), (108,2)` while the
corresponding base degrees are `2,3,3,3`.

## Independent replay

The producer uses SymPy only to discover and serialize the compact section
rows.  The verifier imports neither the producer nor SymPy.  Using only the
Python standard library and the earlier standard-library projection replay, it:

1. reconstructs all 114 base factors;
2. recomputes every coefficient, discriminant, and pair resultant with
   fraction-free arithmetic;
3. measures the exact projection-factor multiplicities;
4. reassembles and hash-checks all open-sector stack shards;
5. rediscovers the 36 unchanged and 4 same-count eligible sections;
6. checks all tagged inversions and clique components;
7. recomputes the 4,610-cell count and the 28-section frontier; and
8. rejects 13 hostile claim mutations.

Run:

```bash
python ai/omreal/verify_diag3_pair_global_four_support_regular_residual_section_lift.py
```

## Remaining algebraic frontier

```text
 7 complex unchanged stacks
 7 exceptional same-count transitions
14 root-count changes
28 total algebraic t sections
```

The remaining cases contain discriminants, higher resultant multiplicities,
or genuine root births/deaths and therefore require algebraic-section gcd or
subresultant certificates rather than the regular-event lemma.
