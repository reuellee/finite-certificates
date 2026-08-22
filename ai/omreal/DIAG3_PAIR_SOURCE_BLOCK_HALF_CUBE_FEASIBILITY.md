# Diagonal three: exact source block half-cube feasibility

## Result

The chart-0/chart-152 source object now has a parent-resident
three-parameter volume.  If `u,v,w` independently interpolate normalized
moving-column blocks 6, 7 and 8 from chart 0 toward chart 152, then the box

```text
[1/2,1] x [0,1] x [0,1]
```

lies entirely in the strict row-2599 parent cell.  Every one of the `17,824`
full-support residual restrictions is decided exactly on this half-cube:

| class | count |
|---|---:|
| zero-free by tensor Bernstein certificate | `13,374` |
| occurs by an exact dyadic-corner witness | `4,450` |
| unresolved | `0` |

This is exact feasibility coverage of a three-dimensional source volume.  It
also proves boundary attachment for every component of 3,889 graph-type
occurring surfaces.  Component coverage remains open for exactly 561 fully
triquadratic surfaces, and the object is not coverage of the full
nine-dimensional parent cell.  The honest 9DVL score therefore remains `2/9`.

## The naïve full cube is false

The first attempted object was the full block cube `[0,1]^3`.  Exact vertex
evaluation rejects it.  Six vertices are parent-safe, but the vertex
`(0,0,1)` violates `[1268]`, and `(0,1,1)` violates both `[1268]` and
`[5678]`.  In particular, the safe three-segment bridge cannot be promoted
to volume coverage merely by filling its ambient cube.

The half-cube is the simplest exact repair found by the declared dyadic gate.
At its eight vertices every signed parent bracket is positive.  Each of the
70 restrictions is trilinear, so these eight values are its tensor Bernstein
coefficients and certify the whole box.  The smallest signed vertex margin is
at `[5678]`:

```text
1923873060148349365333344163278294950688106825916862269195
-------------------------------------------------------------------- .
6968279168765859521383280085258799343560010449024933961074368
```

The half-cube overlaps the proved source square along
`[1/2,1] x [0,1] x {0}` and contains the chart-152 endpoint.

## Exact wall feasibility

Every residual restriction has tridegree at most `(2,2,2)`.  A direct tensor
Bernstein certificate decides 13,370 zero-free walls without subdivision;
four more become sign-definite after one dyadic split.  Exact corner signs
prove 4,444 walls occur without subdivision, with only six requiring deeper
search:

```text
depth 1: 4,  depth 2: 1,  depth 4: 1.
```

The maximum work for any single restriction is 25 visited subboxes.  The
occurring and zero-free factor-ID digests are

```text
7f231091f50588799355a44e6442facb4b76ec341dda3f0e7c60d663aad5d94c
9de5e297c8520c1c26c4c2828b9bcd6e932cb484adb46e341385fec41e221975
```

and the classification semantic digest is

```text
d3761de31661811d27c1340ab175c1c47431dfbf59c7993b7747bbbbcb622381
```

## Graph-type component theorem

Exactly 3,889 of the 4,450 occurring restrictions have degree at most one in
at least one parameter.  Every component of each such zero set meets the
half-cube boundary.

Indeed, write a restriction affine in the first parameter as

```text
p(u,v,w) = a(v,w)u + b(v,w).
```

If `a=b=0` at a zero, the entire `u` fiber lies in the zero set and reaches
the boundary.  Otherwise `a` is nonzero along any hypothetical interior
compact component, so projection to the `(v,w)` plane is locally a graph.
The image of that component would then be both nonempty and open, but also
compact.  No such subset of `R^2` exists.  The same argument applies after
permuting the three parameters.

This exact degree sieve leaves 561 restrictions of tridegree `(2,2,2)`.  Its
hard-residue factor-ID digest is

```text
483908d8ece34b330e5942c3cedf32c013c9f3e23d1b8487249e17208e332802
```

## Replay and next gate

Build the compact record with

```bash
PYTHONDONTWRITEBYTECODE=1 python \
  ai/omreal/build_diag3_pair_source_block_cube_feasibility.py
```

and run the independent hostile replay with

```bash
PYTHONDONTWRITEBYTECODE=1 python \
  ai/omreal/verify_diag3_pair_source_block_cube_feasibility.py
```

The verifier reconstructs the exact three-variable pullbacks and Bernstein
subdivision without importing the producer core.  It also rejects ten
corruptions, including promotion to the invalid full cube, a false complete
wall-component claim, and a falsified 561-wall hard residue.

The next bounded proof object is a surface-component oracle.  For each of the
561 occurring triquadratic restrictions, a compact interior surface
component would force a projection-critical solution of

```text
p = partial_v p = partial_w p = 0.
```

The next gate will eliminate or isolate these systems exactly on the
half-cube, retaining explicit unresolved factor IDs if the declared
projection budget is exceeded.  Only after that local component theorem is
proved should the source-volume complex be extended toward global
missed-component coverage.
