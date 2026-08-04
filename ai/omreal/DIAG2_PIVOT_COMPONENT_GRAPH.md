# The component-decorated wall star at the parent-16 defect-two pivot

## Result

The first exact support-drop wall in the parent-16 defect-two pair does **not**
carry a local `d_1` kernel once compact-component data are included.

The support-only wall star has a one-dimensional transfer kernel.  Exact
component decoration removes it:

\[
\begin{array}{c|c|c|c}
\text{model} & \text{rows} & \text{columns} & \dim\ker d_1\\ \hline
\text{formal pair star} & 51&103&52\\
\text{after pencil pruning} &51&52&1\\
\text{after exact component decoration} &51&51&0.
\end{array}                                               \tag{1}
\]

The decisive new datum is that the central `Q,R` component through the wall
is noncompact by an exact concatenated escape.  Every `Q,T` component is also
noncompact by the degree-at-most-two pencil lemma.  Therefore any compact
adjacent `R,T` component has a private compact triple-component row with
coefficient `+1` or `-1`.

Thus no compact-component cancellation cycle passes through this exact wall
component.  This is a local integral injectivity theorem, not a universal
proof of diagonal two: other components of these pair intersections and
other walls remain unclassified.

The arithmetic and signed incidence are checked by

```console
python ai/omreal/DIAG2_PIVOT_COMPONENT_GRAPH_VERIFY.py
```

## 1. Exact wall data

Retain the notation of `DIAG2_PIVOT_BLOCK_GORDAN_NO_GO.md`.  The proper
incomparable signatures have strict positive circuits

\[
\begin{aligned}
 Q&=123/124/134/235/567,\\
 R&=126/247/158/468/378
\end{aligned}                                             \tag{2}
\]

at the parent-16 chart.  Along

\[
                         y_5(t)=y_5+t y_2                 \tag{3}
\]

the first event is

\[
                         t_*=\frac{541589}{6442906}.      \tag{4}
\]

At the wall point `Y_*`, only the `123` coefficient of `Q` vanishes.  The
remaining positive minimal four-circuit is

\[
                         P=124/134/235/567.                \tag{5}
\]

Every cofinal five-support piece forced through this four-support face is

\[
                      T_q=P\cup\{q\},
            \qquad q\in\binom{[8]}3\setminus P.           \tag{6}
\]

There are 52 of them, including `T_123=Q`; hence there are 51 genuine third
cover indices `T_q != Q`.  This is the smallest wall star forced by the
zero-padded witness (5).  Other unrelated positive circuits at `Y_*` are not
needed for the rows below and can only add further Cech constraints.

The exact transverse fan from the preceding verifier is

- 45 incoming paddings, including `Q`;
- 3 outgoing paddings, `T_126,T_238,T_478`;
- 4 rank-three paddings, `T_145,T_146,T_147,T_148`.

All 52 unions `T_q union R` are pencil-rigid with global partner defect two.
Consequently unsigned support pruning alone leaves every `R,T_q` spoke.

## 2. The formal signed wall star

For each `T=T_q != Q`, use the triple cover index `{Q,R,T}`.  With any fixed
total order on cover pieces, its Cech row is the oriented triangle boundary

\[
 d_1c(Q,R,T)=
       \epsilon_{RT}c(R,T)+\epsilon_{QT}c(Q,T)
                         +\epsilon_{QR}c(Q,R),          \tag{7}
\]

where every `epsilon` is `+1` or `-1`.  The verifier constructs these signs
from the sorted piece order rather than discarding them.

The 51 rows have the following formal pair columns:

- one central column `(Q,R)`;
- 51 columns `(Q,T_q)`;
- 51 columns `(R,T_q)`.

The resulting `51 by 103` integer matrix has rank 51 and kernel dimension 52.
This is ordinary triangle-boundary redundancy and has no topological content
until compact components are specified.

For every alternative `T_q`, the union `Q union T_q` has at most six distinct
triples and hence at most 18 label occurrences.  Some label has degree at most
two.  The projective-plane-pencil lemma therefore gives

\[
                         H_c^0(C_Q\cap C_{T_q};\mathbb Q)=0.
                                                               \tag{8}
\]

Deleting those 51 columns leaves a `51 by 52` star: the central `(Q,R)`
column and the 51 `(R,T_q)` spokes.  It has rank 51 and the expected
one-dimensional transfer kernel.  Up to the incidence signs, that formal
kernel assigns the same coefficient to the center and every spoke.

## 3. Exact decoration of the central component

Let `K_QR` be the connected component of `C_Q intersection C_R` containing
`Y_*`.  It is noncompact.

Indeed, reverse (3) from `t_*` to zero.  The exact cofactor interpolation in
`DIAG2_PIVOT_VERIFY.py` proves that both witnesses remain nonnegative, and
strict away from the endpoint, on this entire segment.  At the original
parent chart, follow the independently certified escape

\[
                         y_1(s)=y_1+s y_4,
              \qquad 0\le s<\frac{399}{2456}.          \tag{9}
\]

Both circuits `Q,R` remain strict on (9), and its endpoint is the parent wall
`[1678]=0`.  Concatenating the two paths stays in `C_Q intersection C_R` and
approaches the boundary of `X`.  Therefore

\[
              [K_{QR}]\text{ contributes no }H_c^0\text{ column}. \tag{10}
\]

This is exactly the geometric component datum absent from the support-only
star.

## 4. Every potentially compact spoke gets a private unit row

Fix an alternative padding `T=T_q` and let `K_RT` be the connected component
of `C_R intersection C_T` containing `Y_*`.

- If `K_RT` is noncompact, it contributes no `H_c^0` column.
- Suppose `K_RT` is compact.  Since circuit pieces are closed, the connected
  component `L` through `Y_*` of

  \[
                        K_{RT}\cap C_Q                  \tag{11}
  \]

  is compact.  It therefore supplies a row in
  `H_c^0(C_Q intersection C_R intersection C_T)`.

The characteristic function of `K_RT` restricts to the characteristic
function of `L`, so its coefficient in this row is a unit `+1` or `-1`.
The other two possible sources are absent:

1. `L` lies in the noncompact central component `K_QR` from (10);
2. every component of `C_Q intersection C_T` is noncompact by (8).

Thus the row of `L` is private for `K_RT`.  This argument does not require
deciding whether `K_RT` is compact: if it is not, there is no column; if it
is, the private row exists automatically.

Applying this independently to all 51 spokes gives a signed permutation-
diagonal `51 by 51` worst-case matrix with determinant `+1` or `-1`.  Any
actual pattern of compact versus noncompact spokes selects a subset of these
unit pivots and remains injective.  Hence

\[
 \boxed{\text{no }\ker(d_1)\text{ coefficient is supported on a pair
 component incident to this wall star}.}                \tag{12}
\]

The statement is integral because all nonzero restriction coefficients are
units.

## 5. No hidden tensor-flow shortcut

The sparse signed tensors at the wall have supports of sizes four and five.
Their seven log-weight-ratio gauge rows have exact rank seven, so positive
column scaling gauges both witness blocks to the signed unit tensors.

For an endomorphism `A of R^8`, impose

\[
                         A c=\mu c,\qquad A d=\nu d.    \tag{13}
\]

There are 66 unknowns: 64 matrix entries and the two eigenvalues.  The exact
linear system has rank 65.  A modular rank-65 calculation is a rational lower
bound, while the scalar solution is an explicit rational nullvector and gives
the matching upper bound.  Hence the nullspace is exactly one-dimensional
and consists of scalar projective gauge.

So this actual proper-incomparable wall has no non-diagonal common
infinitesimal tensor stabilizer.  The local injectivity in (12) genuinely
comes from component incidence and the concatenated escape, not from the
beta-zero stabilizer mechanism used for the earlier row-2599 sample.

## 6. Remaining universal target

The wall star (12) removes the first hard boundary of the only stored exact
global-defect-two occurrence.  It does not classify:

- other connected components of the same `5+5` intersections which do not
  meet `Y_*`;
- defect-two walls for other parents or signatures;
- compact pair components whose support-drop boundary contains several wall
  components with nontrivial split--merge incidence; or
- cycles assembled through a sequence of distinct derived walls.

The next universal lemma suggested by this calculation is:

> Every component-decorated support-drop wall has either an escaping central
> pair component, as above, or a private unit row on the central side after
> recursively orienting the adjacent spokes.

Proving a well-founded version of that statement over all 52 derived-wall
types would establish the desired injectivity.  The present artifact proves
it only for the exact wall (4), and the honest nine-diagonal score remains
`1/9`.
