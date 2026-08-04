# Exact block-Gordan reroute through the hard endpoint wall

## Result

The endpoint-specific orbit-50 wall found in
`BLOCK_GORDAN_TRIPLE_WALL_AUDIT.md` does **not** terminate the noncompact
component of the hard row-2599 triple.  There is an exact one-column path in
the same parent realization cell which:

1. joins the original three-pivot cube to a persistent triple of positive
   circuits;
2. crosses the wall at which `Q4` dies and `R4` survives;
3. retains all three bad signatures across the wall; and
4. retains a degree-two pencil escape throughout.

At the wall the block-4 positive face changes exactly as

\[
  [Q_4,R_4]\quad\longrightarrow\quad[P,R_4]
  \quad\longrightarrow\quad[S_4,R_4],                 \tag{1}
\]

where `P` is the zero-weight support-drop face common to `Q4` and `S4`.
Thus (1) is a wall-compatible positive-circuit elimination reroute, not a
choice of a circuit vertex continued past its domain of existence.

This is a theorem about one local component.  It does not construct a global
acyclic matching, settle the remaining pair/triple Mayer--Vietoris terms, or
prove diagonal `s=3`.

The exact verifier is `BLOCK_GORDAN_ENDPOINT_WALL_REROUTE.py`.

## 1. Exact parent path

Put the shatter certificate's pattern-0 parent into the standard frame

\[
 A=[e_1,e_2,e_3,e_4,(1,1,1,1),(1,a,b,c),(1,d,e,f),(1,g,h,i)].
\]

Let `E` agree with `A` in every column except column 7, and replace that
column by the normalized column 7 of upper chart 152.  Explicitly, the only
three changing coordinates are

\[
 (d,e,f)_A=\left(
 \frac{78097702199}{116705334327},
 \frac{133840104735}{246720030751},
 \frac{6261393287}{20965393143}
 \right),                                               \tag{2}
\]

\[
 (d,e,f)_E=\left(
 \frac{2778627904}{5323014921},
 \frac{2747583397}{6674407488},
 \frac{764955152}{5930027229}
 \right).                                               \tag{3}
\]

Define

\[
                         M(t)=(1-t)A+tE,\qquad 0\le t\le1.       \tag{4}
\]

All 70 parent brackets are nonzero and have the same sign at `A` and `E`.
Only column 7 moves, so every bracket is either constant or affine in `t`.
An affine function whose endpoint values have the same strict sign has that
sign on the whole interval.  Hence (4) lies entirely in parent cell 2599.

The standard frame reorients parent columns 1 and 3.  The verifier transforms
every one of the 56 extension signs by

\[
 \sigma'_{ijk}=(-1)^{|\{i,j,k\}\cap\{1,3\}|}\sigma_{ijk}.       \tag{5}
\]

It independently checks (5) against all 70 parent brackets, so the circuit
statements below refer to the original three signatures in the normalized
chart, not to accidentally different sign vectors.

## 2. A persistent bad triple

Use the following signed-normal supports:

| block | support |
|---|---|
| `R0` | `134/234/267/258/468` |
| `R4` | `134/256/127/357/478` |
| `C3` | `127/347/357/578` |

`R0` and `R4` are five-circuits.  `C3` is a structural rank-three
four-circuit.  Along (4), every normal is polynomial in `t`.  Alternating
maximal minors give polynomial dependence coefficients.  Exact conversion
to the Bernstein basis on `[0,1]` gives:

| circuit | coefficient degrees | strict Bernstein sign |
|---|---:|---:|
| `R0` | `0` or `1` | all negative |
| `R4` | `2` or `3` | all negative |
| `C3` | `2` | all positive |

For `C3`, the full four-normal determinant is identically zero.  The four
positive cofactors of the last three coordinate rows have identically zero
residual also in the first row.  Since every Bernstein coefficient is
strictly positive, the relation has rank exactly three at every parameter.

Consequently all three normalized positive Gordan polytopes are nonempty for
every `t`, with continuous witnesses obtained by normalizing these polynomial
cofactor vectors.  Therefore

\[
                  M([0,1])\subset B_{\sigma_0}\cap
                  B_{\sigma_4}\cap B_{\sigma_3}.                \tag{6}
\]

At `t=0`, all six vertices `Q0/R0`, `Q4/R4`, and `Q3/R3` of the distinguished
product cube are strict.  The `C3` circuit is strict there as well.  Each
normalized block fiber is convex, so every point of the product cube joins
inside the same fiber to `(R0,R4,C3)`.  This uses the whole Gordan polytope,
not a frozen support.  Linear blockwise contraction also respects zero
coordinates; in the joined union resolution it fixes any zero-mass block.

## 3. Exact orbit-50 circuit elimination

In block 4 set

\[
\begin{aligned}
 Q_4&=123/256/127/357/478,\\
 R_4&=134/256/127/357/478,\\
 S_4&=123/134/256/357/478,\\
 P  &=123/256/357/478.
\end{aligned}                                             \tag{7}
\]

Let `D(t)` be the alternating `Q4` cofactor which omits `127`.  The
corresponding `S4` cofactor which omits `134` is exactly `-D(t)`.  Exact
Bernstein certificates show:

* every other `Q4` cofactor is strictly negative on `[0,1]`;
* every other `S4` cofactor is strictly negative on `[0,1]`;
* every `R4` cofactor is strictly negative on `[0,1]`;
* `D'(t)>0` on `[0,1]`; and
* `D(1/3)<0<D(3/8)`.

There is therefore one root

\[
                    \rho\in(1/3,3/8).                         \tag{8}
\]

For `t<rho`, `Q4` and `R4` are the two positive circuit rays in the
six-normal restriction in (7).  At `rho`, the `127` weight of `Q4` becomes
zero and the `134` weight of `S4` becomes zero, giving the same positive
four-circuit `P`.  For `t>rho`, the two rays are `S4` and `R4`.

The support `P` has wall orbit 50 and is residual.  Because `R4` stays a
strict rank-four five-circuit, the restricted six-normal matrix has rank four
at the wall.  Its positive kernel cone is two-dimensional and pointed.  The
two rays `P,R4` therefore exhaust it, so its normalized face is again a
closed interval.  The zero weight at `P` is part of that interval and cannot
be deleted without breaking the continuation.

The verifier also independently enumerates all positive minimal circuits of
sizes two through five in this restriction at both rational endpoints.  It
finds exactly

\[
             \{Q_4,R_4\}\quad\hbox{at }t=0,
             \qquad
             \{S_4,R_4\}\quad\hbox{at }t=1.             \tag{9}
\]

Equations (7)--(9) prove the local face replacement (1).

## 4. The escape survives the reroute

The union of the persistent supports `R0/R4/C3` has label-degree vector

\[
                         (2,5,4,5,4,3,6,4).                    \tag{10}
\]

The only support planes incident with label 1 are

\[
                              134\quad\text{and}\quad127.       \tag{11}
\]

Move the parent point `y_1` on the projective line

\[
 \mathbb P\bigl(
   \operatorname{span}(y_1,y_3,y_4)
   \cap
   \operatorname{span}(y_1,y_2,y_7)
 \bigr).                                                       \tag{12}
\]

The two planes in (11) remain fixed, so their normal representatives change
only by nonzero scalars.  Every other active normal is independent of `y_1`.
On the connected residence interval containing the starting point, the two
scalars stay positive; inverse scaling transports all three positive
dependences.  The residence interval ends at a genuine parent bracket wall,
because a projective line meets the finite forbidden-hyperplane arrangement
in boundary points.  Thus (12) is a proper escape to the parent boundary.

This proves that the triple-intersection component containing the original
cube remains noncompact after the endpoint-specific Q4 wall.  In particular,
that wall is not a local obstruction to a coordinated block-Gordan matching.

## 5. What remains open

The certificate resolves exactly one of the 16 endpoint-specific walls of
this cube, along one explicit parent path.  It does not prove that every such
wall admits a compatible reroute, that choices around codimension-two wall
intersections are coherent, or that the resulting directed matching is
acyclic.  It also says nothing by itself about the pair `H_c^1` and triple
`H_c^0` terms still present in the third-diagonal spectral sequence.

Accordingly the proof score remains unchanged.  The reusable local rule is:

> before following a circuit vertex through its cofactor wall, retarget all
> witness blocks inside their convex Gordan fibers; then transport a sparse
> persistent tuple.  At the wall retain the shared zero-weight circuit face.

That rule survives the exact split--remerge and endpoint-death obstruction
which defeated the frozen product cube.
