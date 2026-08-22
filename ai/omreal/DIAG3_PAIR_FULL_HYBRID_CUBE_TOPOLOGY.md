# Diagonal three: ambient full-hybrid-cube wall topology

## Result

Let `u,v,w` independently interpolate normalized moving-column blocks 6, 7
and 8 from row-2599 chart 0 toward chart 152.  The entire parameter cube
`Q=[0,1]^3` is **not** contained in the row-2599 parent cell: exact evaluation
of all 70 signed parent brackets at all eight vertices reproduces the two
invalid vertices `(0,0,1)` and `(0,1,1)`.

That parent no-go does not prevent an exact statement about the residual
polynomials restricted to `Q`.  The certificate decides all 17,824 restricted
walls:

| classification | count |
|---|---:|
| zero-free on `Q` | 12,247 |
| occurring on `Q` | 5,577 |
| unresolved | **0** |

Of the 5,577 occurring restrictions, 4,898 are affine in at least one
parameter.  The graph-projection argument excludes a compact component in
the cube interior.  The other 679 are fully triquadratic.  Exact adaptive
critical-system subdivision proves all 679 systems empty, with selected
derivative-pair census

```text
(v,w): 676
(u,w):   2
(u,v):   1
```

Therefore every connected component of every occurring restricted wall meets
the true boundary of the full hybrid cube.  No internal box seam appears in
this conclusion.

This is ambient topology of one three-parameter affine family, not residence
of the whole cube in the parent cell and not coverage of the nine-dimensional
row-2599 parent cell.  The honest 9DVL score remains `2/9`.

## Exact feasibility

Each restricted residual factor has degree at most two in each parameter.
Tensor Bernstein signs certify zero-free boxes, while exact opposite-sign
corners or a zero corner certify occurrence.  Midpoint subdivision is used
only when the initial control net is inconclusive.  The worst restriction
visits 89 subboxes; no restriction reaches the depth-eight budget.

The exact factor-ID and semantic digests are

```text
occurring  ca6e3d7911be1cc341fb4a40369542eadb8c526bd3c81a3f449037e97cfa425b
zero-free  3eab27338a090d6001e6d7d374d50d6983aeafe1967fac37b5b857f8ca168419
semantic   5e290f7aab3da48706f326b1bb89a867b737efb3af354a182e679c62cbe1454d
```

## Exact component coverage

For a graph-type restriction, a coefficient-drop zero supplies a full
boundary-reaching fiber; otherwise projection along the affine parameter is
locally a graph.  A compact interior component would then have a nonempty
image that is both open and compact in `R^2`, which is impossible.

For a fully triquadratic restriction `p`, a compact interior component would
contain a coordinate extremum and hence a common zero of `p` and the two
derivatives transverse to that coordinate.  The verifier tries the three
derivative pairs in fixed order and accepts only an exactly empty system.
Four first-choice attempts are preserved as unresolved; alternate pairs close
all four.  The worst factor uses 352 visited subboxes across its attempts.

The graph, triquadratic, and critical semantic digests are

```text
graph          07b7e6c6b5ae14b0a5302f4b3d4b6810d733b47fe1fb15806bdf86cb95e6e743
triquadratic   8270322d555583c5375b6797b20019f57cf0600df9ee37c0f9c26fa3b43a2191
critical       a7f8f690c855982e8eee416e97f8f7aa444646b0a3c1c964db15920ed6b6548e
```

## Outer-boundary transfer

Let `Z` be one restricted wall zero set and let `S` be any closed
full-dimensional semialgebraic subregion of `Q`, such as a parent-safe source
staircase.  Suppose a component `C` of `Z intersect S` avoided the true
boundary of `S`.  Then `C` lies in the interior of `S`.  The semialgebraic
component of `Z` containing `C` is path connected and, by the full-cube
certificate, has a path to the boundary of `Q`.  The first point where that
path exits the interior of `S` lies in `Z intersect boundary(S)` and is still
connected to `C` inside `Z intersect S`, a contradiction.

Consequently every restricted-wall component in the five-box staircase—and
in any later parent-safe staircase inside this same hybrid cube—meets its
true outer boundary.  Internal seams are no longer part of the topological
claim.  What remains open is the genuinely global incidence statement: a
row-2599 parent-cell wall component may fail to meet this three-parameter
source family at all.

## Replay

Build the compact record with

```bash
PYTHONDONTWRITEBYTECODE=1 python \
  ai/omreal/build_diag3_pair_full_hybrid_cube_topology.py
```

and run the independently coded hostile replay with

```bash
PYTHONDONTWRITEBYTECODE=1 python \
  ai/omreal/verify_diag3_pair_full_hybrid_cube_topology.py
```

The verifier uses the separately written pullback, Bernstein subdivision,
critical-system, and normalization routines from the existing independent
half-cube audit.  It reconstructs every count and digest and rejects 13
hostile mutations, including false parent residence, false global parent
coverage, deletion of alternate axes, and restoration of internal seams.
