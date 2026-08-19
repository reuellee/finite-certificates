# Diagonal three: a common proper escape for the flow-triangle triple

## Exact local theorem

The three signatures in `DIAG3_JOINED_FLOW_TRIANGLE.md`, whose elementary
escape sets have empty triple intersection at row-2599 chart zero, nevertheless
lie on one common proper bad-locus ray.

Start at chart zero of `data/seeat_parent2599_upper178.npz`.  Move only
labelled column 7 in the integer direction

```text
(81,-262,91,86)
```

and parameterize the segment by

```text
t * 23597311 / 105015122,        0 <= t < 1.
```

Every one of the 70 parent brackets keeps its original strict sign for
`0 <= t < 1`.  At `t=1`, exactly `[2467]` vanishes.  Hence the path leaves
every compact subset of the open normalized parent cell through a genuine
parent-boundary face.

The three bad signatures retain the following strict positive circuits on
the entire closed parameter interval:

| block | persistent support |
|---:|:---|
| 0 | `123/456/137/238/148` |
| 1 | `123/345/257/167/128` |
| 2 | `123/136/256/247/348` |

The verifier reconstructs the derived normals over `Q[t]`, constructs all
five alternating cofactor polynomials for each circuit, checks their exact
kernel identities, and proves strict positivity by their Bernstein
coefficients.  Their degree vectors are

```text
(1,1,0,1,1), (2,2,1,1,2), (1,1,1,0,1).
```

Thus the connected component of the triple-bad intersection through this
chart is noncompact and contributes nothing to compactly supported degree
zero.  This is a local instance of the first diagonal-three obligation.

## Why this is not the missing `d3` cell

The joined flow triangle has seven relative two-faces with primitive kernel

```text
-T + S01 + S12 + S20 + H0 + H1 + H2.
```

The common ray supplies a proper target in the triple-bad locus, but the
tracked data provide no face-natural comparison from any of those seven
two-faces to this ray.  In particular, they do not certify a continuous
mixed-block three-parameter family, its zero-block and zero-weight faces, its
residual subdivisions, or its signed boundary incidence.  A proper path is
not a three-cell.

The machine-readable local open object is embedded in
`data/DIAG3_PAIR_GLOBAL_CLOSURE_OPEN_OBJECT.json`.  It records the seven known
boundary faces, the common proper ray, and the six unresolved comparison
incidences needed to join the three pair strips and three singleton sectors
to it.  The central mass face is already shared at the source; it does not
remove those six comparison requirements.

## Replay

```bash
PYTHONDONTWRITEBYTECODE=1 python \
  ai/omreal/verify_diag3_row2599_common_proper_escape.py
```

The result is deliberately local.  It neither constructs the global pair
frontier complex nor changes the honest score from `2/9`.

## Exact bounded tapered-cube checkpoint

There is additional exact positive data, still short of a comparison
incidence.  Write the three displayed pair roots of the joined flow triangle
as `d01,d12,d20`, and let their chart-zero first-wall parameters be

```text
U01 = 1221971981 / 1769366234,   endpoint [1234]
U12 =   42214994 / 2183619501,   endpoint [1358]
U20 =  425791163 / 1286992887,   endpoint [1256].
```

For every order of the two roots incident to a block, the verifier checks
the compact cube

\[
 Y(s,x,y)=g_{d_i}((1-s)xU_i)
             g_{d_j}((1-s)yU_j)Y_{\rm common}(s),
 \qquad (s,x,y)\in[0,1]^3.                              \tag{1}
\]

Here `Y_common(s)` is the column-7 ray above, and the displayed order is
literal: the second shear acts on the already moved matrix.  Exact sparse
polynomials over `Q[s,x,y]` and tensor Bernstein conversion prove that all
70 parent brackets have their prescribed weak signs throughout each of the
six cubes.  For `H0,H1,H2`, respectively, the fixed circuits

```text
123/456/137/238/148
123/345/257/167/128
123/136/256/247/348
```

remain strict.  This is stronger than a sampled ruled-sector experiment:
it is an exact bounded three-parameter bad-locus certificate.

It is not yet any of the six comparison incidences.  The subsequent exact
ordered-sector audit in
`review_scratch/DIAG3_HOSTILE_ROW2599_ORDERED_SECTOR_ROADMAP.md` closes the
old outer-remainder and witness-seam questions: it constructs the H0 outer
cap, proves all six pair/singleton cofactor seams, and isolates the primitive
comparison hexagon.  It also proves two relative parent-wall collars, for
`p12` and `p20`.  Those collars are not complete signed comparison maps.

The corresponding `p01` wall-collar architecture is false.  Block 0 becomes
good along `[1234]` before the first additional parent corner `[1367]`, as
certified by an exact strict tope covector.  Thus the remaining local gate is
a new nonradial `[1234]`-tangent bad-locus cap, followed by a mixed base-space
filler of the comparison hexagon.  The machine-readable full-comparison
count at that checkpoint was `0/6`, despite two certified relative collars.
The later nonradial tangent/prism, two-stage pair, and `H2` certificates
advance the local count to `4/6` without changing this historical no-go.

## Falsified common-root shortcut

The fixed circuits above make the shear `(1 -> 3,+)` look common if one
only recomputes a fresh positive circuit after moving the matrix.  That is
not the moving-witness condition.  On block 1, inverse-exterior transport
has opposite required signs on the two active rows

```text
167 (index 30): -1,     128 (index 35): +1.
```

Thus no single parameter orientation transports that fixed witness.  The
empty threefold elementary escape-set intersection in
`DIAG3_JOINED_FLOW_TRIANGLE.md` is correct; the apparent shortcut was a
failure of face naturality, not a new common root.  This exact negative
regression is now pinned in the verifier.
