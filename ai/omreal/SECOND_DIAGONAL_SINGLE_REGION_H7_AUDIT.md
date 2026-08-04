# Independent audit of the dual-lift single-region `H_7` theorem

## Verdict

The theorem in `DIAG2_PIVOT_DUAL_SINGLE_BAD_ESCAPE.md` is sound.  I found no
counterexample, quotient defect, orientation reversal, or unsupported
duality step.

Two clarifications make the proof fully explicit:

1. Gale duality should be read on realization spaces quotiented by row
   operations and positive column scalings.  On those quotient spaces it is
   a genuine homeomorphism.  In compatible contraction-height coordinates,
   the lift/extension correspondence is the exact linear formula
   \(z=-Bh\), with height gauge kernel exactly `row(A)`.
2. During the rank-five pencil motion, choose the normalized projective frame
   among six of the seven labels different from the moving label.  Uniformity
   guarantees that this is possible.  Then the other seven columns can
   literally remain fixed, and a continuous oriented lift of the residence
   interval makes every support-normal scale positive until the first parent
   wall.

Neither clarification changes the claimed result.  In particular,

\[
 \widetilde H_7(F_\sigma;\mathbb Z)=0,
 \qquad
 H_c^1(B_\sigma;\mathbb Z)=0                                  \tag{1}
\]

for every realizable uniform single-element extension of a realizable
`UOM(4,8)` parent.  This still does not prove the second diagonal for a pair.

The exact regression
[`SECOND_DIAGONAL_SINGLE_REGION_H7_AUDIT.py`](SECOND_DIAGONAL_SINGLE_REGION_H7_AUDIT.py)
checks a row-2599 lift, its contraction and both Gale complements, and an
independent rank-five degree-three pencil equality case.

## 1. Exact Gale lift/extension correspondence

Let \(N\) have rank four on the eight old labels and a distinguished label
\(p\), and put \(A=N/p\).  In contraction-height coordinates, a realization
of \(N\) has matrix

\[
 \widetilde N=
 \begin{pmatrix}
 A&0\\
 h&1
 \end{pmatrix},                                               \tag{2}
\]

where \(A\) is a `3 by 8` realization of the contraction and \(h\) is its
row of lift heights.

Let \(B\) be any `5 by 8` matrix whose row space is \(\ker A\); it realizes
\(A^*\).  Then

\[
 C=\left[B\mid -Bh^T\right]                                   \tag{3}
\]

satisfies

\[
                         \widetilde N C^T=0.
\]

Both matrices have complementary ranks, so `row(C)=ker(N tilde)`.  Thus
\(C\) is a Gale dual realization of \(N\), its deletion at \(p\) is exactly
\(B\), and its new extension column is

\[
                              z=-Bh^T.                           \tag{4}
\]

Conversely, \(B\) has row rank five, so every proposed dual extension column
\(z\in\mathbb R^5\) has a solution of (4).  Two height rows give the same
column precisely when their difference belongs to

\[
                  \ker B=\operatorname{row}(A),                 \tag{5}
\]

which is exactly the contraction-height gauge.  Therefore (4) is a linear
isomorphism

\[
 \mathbb R^8/\operatorname{row}(A)
       \xrightarrow{\ \cong\ }\mathbb R^5                       \tag{6}
\]

from normalized lift heights to the dual extension column.

The complementary-minor identity is

\[
 \det C_J=\lambda\,
   \operatorname{sgn}(J,J^c)\det\widetilde N_{J^c},             \tag{7}
\]

with one nonzero common scalar \(\lambda\).  Hence the oriented matroid of
\(C\) is \(N^*\), up to the immaterial global chirotope sign.  Formula (7)
also proves that the sign inequalities for a lift realizing \(N\) are
exactly the sign inequalities for an extension realizing \(N^*\).

This proves pointwise and fiberwise that

\[
 a\in G_p(N)
 \quad\Longleftrightarrow\quad
 a^*\in F_\tau,                                                \tag{8}
\]

where \(\tau\) is the extension signature of \(N^*\) over
\((N/p)^*=N^*\setminus p\).

### Quotient and normalization check

The row space of a full-rank realization is a point of a Grassmannian, and
orthogonal complement is a homeomorphism

\[
                         \operatorname{Gr}(3,8)cong
                         \operatorname{Gr}(5,8).
\]

If old column \(i\) is positively scaled by \(d_i\), its Gale-dual column is
scaled by \(d_i^{-1}>0\).  Thus orthogonal complement descends through the
positive diagonal quotient.  A fixed nonzero Pluecker coordinate supplies
compatible normalized matrix representatives on the entire uniform cell.
There is therefore no hidden choice of kernel basis and no orientation
monodromy: on quotient realization spaces Gale duality maps \(G_p(N)\)
homeomorphically to \(F_\tau\).

Combining this with the two convex-fiber homotopy equivalences gives

\[
 F_\sigma\simeq\mathcal R(N)simeq G_p(N)cong F_\tau.          \tag{9}
\]

## 2. Rank-five pencil escape

Let \(Y\in B_\tau\), where the rank-five parent has eight elements.
Gordan's alternative supplies a support-minimal nonnegative dependence of
the signed four-plane normals.  Because the normals lie in a five-dimensional
space, its support \(Q\) has at most six members.

Each member of \(Q\) contains four of the eight labels, so

\[
                       \sum_{e=1}^8\deg_Q(e)=4|Q|\le24.
\]

Consequently some label \(e\) has \(\deg_Q(e)\le3\).  This counting argument
includes the equality case \(|Q|=6\), where every label may have degree
three; the verifier contains such an exact example.

For every incident support \(I\), let

\[
 H_I=\mathbb P\operatorname{span}\{y_i:i\in I\}\subset\mathbb P^4.
\]

The intersection of at most three real projective hyperplanes in
\(\mathbb P^4\) has projective dimension at least one and contains
\([y_e]\).  Hence it contains a real projective line \(\ell\) through that
point.

### Gauge check

A projective frame in \(\mathbb P^4\) uses six labels.  Since there are seven
labels other than \(e\), choose all six frame labels away from \(e\).
Uniformity makes them a projective frame.  In this normalized slice, the
other seven parent columns stay literally fixed while \([y_e]\) moves on
\(\ell\).

Choose a continuous nonzero oriented vector lift of the component of
\(\ell\) containing \([y_e]\).  This is possible because that component is
an interval.  For an incident \(I\in Q\), the four columns remain in the
fixed \(H_I\).  Before a parent wall they remain independent, so their span
is exactly \(H_I\), and

\[
                         a_I(t)=c_I(t)a_I(0).                    \tag{10}
\]

The scalar in (10) is continuous and nonzero, and it equals one initially.
Therefore \(c_I(t)>0\) throughout the residence interval.  A sign reversal
would force the four-fold wedge to vanish, which is already a parent
nonuniformity wall.  Normals from supports not containing \(e\) are fixed.
Dividing each original positive Gordan coefficient by \(c_I(t)\) transports
the strict positive dependence, so the path stays in \(B_\tau\).

### Genuine boundary check

For every four-subset \(J\) of the other seven labels, uniformity makes

\[
 W_J=\mathbb P\operatorname{span}\{y_j:j\in J\}
\]

a projective hyperplane.  It cannot contain \(\ell\), because then it would
contain the initial \([y_e]\) and the five columns \(J\cup\{e\}\) would be
dependent.  Hence \(W_J\cap\ell\) is one point.  Removing these finitely many
wall points from the real projective line leaves open intervals.  Approaching
either endpoint of the residence interval makes a five-bracket vanish and
leaves the uniform parent space.

Thus every point of \(B_\tau\) lies in a component containing a path with a
limit only on the parent boundary.  Such a component cannot be compact.
The bad locus is semialgebraic and locally connected, so

\[
                             H_c^0(B_\tau;\mathbb Z)=0.          \tag{11}
\]

No continuous global choice of \(Q,e,\ell\) is needed; the pointwise escape
already excludes compact connected components.

## 3. Supported duality uses only two parent groups

Let \(X^*=\mathcal R(A^*)\), an oriented eight-manifold, and
\(F_\tau=X^*\setminus B_\tau\).  Alexander--Poincare duality with supports
for the closed semialgebraic subset \(B_\tau\) gives

\[
 H_c^0(B_\tau;\mathbb Z)
      \cong H_8(X^*,F_\tau;\mathbb Z).                           \tag{12}
\]

The relevant pair sequence is only

\[
 H_8(X^*)\longrightarrow H_8(X^*,F_\tau)
 \longrightarrow H_7(F_\tau)\longrightarrow H_7(X^*).         \tag{13}
\]

Contraction-height with `(r,n)=(5,8)` realizes \(X^*\) up to homotopy as an
open subset of \(\mathbb R^6\).  It therefore gives integral vanishing in
all degrees at least six, in particular

\[
                         H_8(X^*)=H_7(X^*)=0.                   \tag{14}
\]

Equations (11)--(14) imply \(H_7(F_\tau;\mathbb Z)=0\), and (9) transfers
this to \(F_\sigma\).

For the original nine-dimensional parent \(X=\mathcal R(M)\), supported
duality gives

\[
 H_c^1(B_\sigma;\mathbb Z)cong H_8(X,F_\sigma;\mathbb Z).      \tag{15}
\]

The only pair-sequence terms surrounding (15) are again

\[
 H_8(X)\to H_8(X,F_\sigma)\to H_7(F_\sigma)\to H_7(X).         \tag{16}
\]

Contraction-height with `(r,n)=(4,8)` supplies
\(H_8(X)=H_7(X)=0\) integrally.  No blanket contractibility theorem and no
lower parent homology group are used.  Equations (1), (15), and (16) follow.

## 4. Mayer--Vietoris consequence and scope

The already proved first single-region diagonal also gives
\(H_c^0(B_\sigma)=0\).  Compact-support Mayer--Vietoris for two closed bad
loci therefore has the segment

\[
 0\to H_c^0(B_\sigma\cap B_\tau)
 \to H_c^1(B_\sigma\cup B_\tau)
 \to H_c^1(B_\sigma)\oplus H_c^1(B_\tau).
\]

The last two single-region groups vanish by (1), so

\[
 H_c^1(B_\sigma\cup B_\tau;\mathbb Z)
 \cong H_c^0(B_\sigma\cap B_\tau;\mathbb Z).                   \tag{17}
\]

This removes the former single-region restriction-map term.  It does not
show that the simultaneous-bad intersection has no compact component, which
is exactly the remaining second-diagonal problem.

## 5. Exact regression

Run

```bash
python ai/omreal/SECOND_DIAGONAL_SINGLE_REGION_H7_AUDIT.py
```

The first half uses row-2599 pattern 1 and its stored exact feasible extension
column.  It verifies:

* all 56 original extension inequalities are strict;
* deletion of the exact five-row Gale complement of \(N\) is the exact
  five-row Gale complement of \(N/p\);
* all 126 and 56 complementary Pluecker ratios respectively have one common
  Hodge scale;
* the dual extension column is exactly \(-Bh\);
* `ker(B)=row(A)` is precisely the height gauge; and
* taking the exact complement twice recovers `row(N)`.

The second half uses the rank-five cyclic realization

\[
                         y_j=(1,j,j^2,j^3,j^4)^T
\]

and the six supports

```text
1234, 1256, 1278, 3456, 3478, 5678.
```

Every label has degree three.  Their normals have the exact relation

\[
 (1,-1,1/35,35,-1,1),
\]

which becomes positive after signing the six normals accordingly.  The
intersection line for label 1 has an exact pencil direction.  The first wall
is at \(t=-1/2\), where \(y_1(t)=y_2/16\); throughout
\(-1/2<t\le0\), each of the three incident support normals scales by
\(1+2t>0\), and the transported positive dependence remains exact.

Compilation, the exact verifier, and repository diff checks pass.  No second
diagonal is claimed.
