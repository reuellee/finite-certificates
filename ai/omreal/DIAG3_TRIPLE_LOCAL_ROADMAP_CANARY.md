# Diagonal three: first full-space local projection-roadmap canary

## Exact outcome

The canonical unresolved hard row

```text
(5563,4373,23221)
```

has a named factor presentation

```text
(5563,16134,19284).
```

For that presentation, this artifact proves an exact, nonvacuous local
component-coverage theorem on one closed nine-dimensional rational box.  If
`V` is the common zero set of the three authenticated residual factors and
`Q` is the box below, then

\[
       \boxed{\text{every connected component of }V\cap Q
              \text{ meets }\partial Q.}
\]

This is the first certificate in the triple branch that operates on a
full-dimensional box in the nine-variable parent chart rather than on a
pinned one-dimensional slice.  It is a local projection-roadmap **canary**,
not a complete roadmap of the parent cell and not a closure of one `S_8`
orbit.

## Preregistered finite contract

The fixed center, radius, projection columns, success/null outcomes, resource
ceiling, and fail-closed scope were committed before the formal producer and
verifier runs in
`data/DIAG3_TRIPLE_LOCAL_ROADMAP_REGISTRATION.json`.  The registration is
explicit that the center and coarse interval behavior were already known from
reconnaissance; this was not a blinded experiment.  No adaptive radius
reduction or pivot replacement was permitted in the formal run.

The verifier hard-pins the complete preregistration bytes, rather than merely
comparing the certificate with a mutable live registration.  Its SHA-256 is

```text
94224ab5f5f64d8a7e14e3d5d382c5cdc96292d9a455520c3c76e003b77eddb3.
```

It also checks the exact registered schema, status, finite acceptance
contract, authenticated inputs, declared scope, proof consequence, and all
non-consequences.

The registered box has center

\[
 p=\left(-\frac{19}{28},-\frac{23}{7},-\frac{27}{14},
         -5,-4,-3,-1,2,4\right)
\]

and common coordinate radius `1/128`.  Direct exact substitution gives

\[
 q_{5563}(p)=q_{16134}(p)=q_{19284}(p)=0.
\]

Thus the result is not a zero-free-box certificate.

## Uniform-parent accounting

The verifier independently reconstructs the standard normalized parent
matrix

\[
\begin{pmatrix}
1&0&0&0&1&1&1&1\\
0&1&0&0&1&a&d&g\\
0&0&1&0&1&b&e&h\\
0&0&0&1&1&c&f&i
\end{pmatrix}
\]

and all `70` four-by-four brackets.  For each bracket it evaluates an exact
direct-monomial interval enclosure on the entire closed box.  All `70/70`
enclosures exclude zero.  Hence the box lies inside one normalized uniform
parent cell; no box face is silently a parent wall.  This cell is **not** the
row-2599 parent chamber used by the pair branch: in the same direct-determinant
convention, its bracket-sign vector differs from row 2599 on exactly `29` of
the `70` brackets.  Thus “one uniform parent cell” must not be read as
“the row-2599 parent cell.”
The row-2599 reference is an accepted contextual dependency pinned to catalog
SHA-256 `c55e805d60d8086bcb84a312f2103a9973fc2691d0fd97f3d9a1d9809d2b163b`;
its normalized parent-sign replay is
`python ai/omreal/verify_diag3_pair_global_parent_face_gate.py`.

The named-to-canonical factor map is authenticated by the existing
full-space feasibility gate with semantic digest

```text
874c4895ae17843c6827c1c3a8d528eac0b45fc35dedc9159e4f447786ed2ace
```

and raw SHA-256

```text
8ad62abdd3bd7d9bc14e5bfec3e407f3c07fd740a5475d1243e8dbb9e08d8692.
```

That mapping gate is an accepted dependency for the named-presentation to
canonical-row identification only.  Its independent invocation is

```bash
PYTHONDONTWRITEBYTECODE=1 \
  python ai/omreal/verify_diag3_triple_fullspace_feasibility_gate.py
```

The gate's separate full-space feasibility decision remains fail-closed; this
local canary does not turn that earlier decision into a global acceptance.
The three source equations are separately pinned by SHA-256

```text
c9244a47ded5736e7afe724a9914e75631a22b78653442e88c14f5c397919eb8.
```

This accounts completely for the declared one-presentation scope.  It does
not replace the unavailable `1,162,302`-row final-residue stream or infer
anything about a second presentation.

## Projection-critical certificate

Let the fiber variables be

```text
(d,e,h),  zero-based columns (3,4,7),
```

and project to the complementary base variables

```text
(a,b,c,f,g,i).
```

The exact residual Jacobian minor

\[
       \Delta=\det\frac{\partial(q_{5563},q_{16134},q_{19284})}
                          {\partial(d,e,h)}
\]

has `147` terms.  Its value at the rational center is

\[
                         \Delta(p)=-\frac{1000407}{686},
\]

and direct exact interval arithmetic on the whole box gives

```text
[-554912474289739698651/193091834023510016,
 -1196518334587743667/27584547717644288].
```

Both endpoints are negative.  Therefore the projection has no critical point
on `V intersect Q`.  The same nonzero `3 x 3` minor gives rank three for the
residual Jacobian, so the triple-zero set is a smooth six-manifold near its
intersection with the box.

The point of pinning these three columns is stronger than merely proving that
the residual Jacobian has rank three.  By the inverse-function theorem, the
projection to `(a,b,c,f,g,i)` restricts to a local diffeomorphism on the
six-dimensional triple-zero set throughout the box.  If a connected
component `C` of `V intersect Q` missed the box boundary, it would be a
compact subset of the box interior.  Because a smooth manifold is locally
connected, this connected component is open in the smooth triple-zero set.
The local-diffeomorphism charts therefore make its projected image open in
`R^6`.  Its projection would be:

* nonempty;
* open in `R^6`, because the projection is a local diffeomorphism; and
* compact, because `C` is compact.

No nonempty subset of `R^6` is both open and compact.  This contradiction
proves the displayed component-coverage theorem.

## Boundary and trust boundaries

All `18` coordinate faces of the closed box are explicitly included.  They
are classified only as artificial scope boundary.  There are no internal
seams, and the certificate claims zero parent-wall faces and zero
parent-infinity faces.  Reaching this artificial box boundary is not the
same as escaping the parent cell; adjacent compatible boxes would have to be
glued, and any eventual terminal face would have to be identified with a
genuine parent divisor or chart infinity.

The producer uses the repository polynomial utilities.  The verifier does
not import the producer: it separately implements sparse rational arithmetic,
determinants, derivatives, normalized-bracket reconstruction, direct interval
evaluation, and semantic hashing.  It rejects hostile changes to
source identity, row identity, box, bracket accounting, projection, boundary
scope, orbit scope, and theorem score.  It additionally rejects a direct false
parent-infinity claim, a coupled registration-plus-certificate rewrite that
tries to promote the local box to global coverage, and re-sealed unknown
top-level and nested projection theorem fields, for `18/18` total hostile
mutations.  The final verifier comparison reconstructs the complete
certificate object, so unknown keys in any section fail closed.

An interior-sphere negative canary is also retained.  Its projection pivot
derivative has interval `[-2,2]`, so the verifier refuses the sign
certificate.  This guards against turning interval overlap or a generic rank
claim into a false component-escape proof.

The literature audit records the standard Basu--Roy roadmap requirement that
a roadmap meet every semialgebraically connected component and the relevant
fiber components.  This canary uses only the elementary local-diffeomorphism
and compactness implication above.  It is therefore deliberately not called
a complete Basu--Roy roadmap; its value is as the smallest exact full-space
compiler fixture for the triple branch.

## Replay

```bash
PYTHONDONTWRITEBYTECODE=1 \
  python ai/omreal/build_diag3_triple_local_roadmap_canary.py
PYTHONDONTWRITEBYTECODE=1 \
  python ai/omreal/verify_diag3_triple_local_roadmap_canary.py
```

The producer emits
`data/DIAG3_TRIPLE_LOCAL_ROADMAP_CANARY.json`.  The verifier reconstructs the
certificate rather than trusting its interval records.

## Honest theorem accounting

The proof covers one rational box and no complete factor-triple orbit.  It
does not prove reach to parent infinity, reduce the `1,162,302` unresolved
rows, or affect the independent pair-middle-exactness obligation.  The honest
9DVL score remains `2/9`.

The next proof-producing scale-up is a finite chain of sign-certified boxes
whose shared faces are replayed exactly, followed by a proof that every
non-shared terminal face lies on a genuine parent boundary.  Orbit transport
must remain separate until the stabilizer, chart denominator, parent-sign,
and projection-minor transformations are all proved.

This triple checkpoint does not retarget the pair branch.  During integration,
retain the canonical pair routing from checkpoint `c692471`: continue the
exact 40-edge full-support source cover (or replace it with a directly
coverage-certified parent-cell roadmap), while keeping the section-960 and
section-550 stars as compiler stress tests only.
