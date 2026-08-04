# Moving-witness shears for diagonal two

## Scope and status

This note proves a conditional escape lemma for a pair of Gordan witnesses.
Unlike the earlier frozen-support shear arguments, the witness is transported
by the inverse exterior shear, so replacement triples may enter its support.
The compatibility condition is an exact sign test on the two full signatures
and the two colored active supports.

The hypotheses hold for every one of the 65 pencil-rigid \(4+5\) or \(5+5\)
occurrences in the exact row-2599 shatter certificate, and for the exact
parent-16 defect-two example. That finite evidence is not a universal census.

> **Status.** This note does **not** prove diagonal two. What is still missing
> is a proof that every point of every relevant simultaneous-bad component
> admits a compatible pair of witnesses, or a different global argument.
> Arbitrary signings can fail compatibility; the verifier contains such a
> negative canary.

## 1. Signed Gordan forms

Let \(E=\mathbb R^8\) have ordered basis \(e_1,\ldots,e_8\), let \(W\) be an
oriented four-space, and let

\[
                         T:E\longrightarrow W
\]

have rank four. Write \(y_i=T(e_i)\). For an increasing triple
\(I=(i_1<i_2<i_3)\), put

\[
 e_I=e_{i_1}\wedge e_{i_2}\wedge e_{i_3},
 \qquad a_I(T)=\Lambda^3T(e_I).
\]

After the fixed orientation identification
\(\Lambda^3W\cong W^*\), these are the 56 derived normals in the Gordan
formulation. A signature is a function

\[
              \rho:\binom{[8]}3\longrightarrow\{+1,-1\}.
\]

A badness witness for \(\rho\) is a nonzero vector
\(\lambda=(\lambda_I)\), with every \(\lambda_I\geq0\), such that

\[
 c_\rho=\sum_I\rho_I\lambda_Ie_I,
 \qquad \Lambda^3T(c_\rho)=0.                         \tag{1}
\]

Its active support is \(S_\rho=\{I:\lambda_I>0\}\). The weights may be
divided by their positive sum at every parameter value, so allowing that sum
to change does not change the circuit-piece condition.

## 2. The exact sign test

Fix distinct labels \(e,f\). For a triple \(I\ni e\), \(f\notin I\), let
\(J=I-e+f\), written increasingly. Define
\(\epsilon(I;e,f)\in\{+1,-1\}\) by replacing \(e\) by \(f\) in the already
ordered wedge \(e_I\) and then sorting:

\[
 e_{i_1}\wedge\cdots\wedge e_f\wedge\cdots\wedge e_{i_3}
       =\epsilon(I;e,f)e_J.                            \tag{2}
\]

For a signature \(\rho\), define its transport sign

\[
 \boxed{\alpha_\rho(I;e,f)
       =-\epsilon(I;e,f)\rho_I\rho_{I-e+f}.}           \tag{3}
\]

Consider a \(\rho\)-witness with active support \(Q\) and an
\(\eta\)-witness with active support \(R\). The ordered shear \(e\to f\) is
**sign-compatible** when all signs in

\[
\begin{split}
 \mathcal A(e,f)={}&
 \{\alpha_\rho(I;e,f):I\in Q,\ e\in I,\ f\notin I\}\\
 &{}\cup
 \{\alpha_\eta(I;e,f):I\in R,\ e\in I,\ f\notin I\}
\end{split}                                            \tag{4}
\]

are equal. If this set is nonempty, denote its common value by
\(a(e,f)\in\{+1,-1\}\). If it is empty, either parameter ray works; set
\(a(e,f)=+1\) by convention so the lemma below also covers this vacuous
case.

This is a purely combinatorial condition once the two full signatures and
the two colored active supports are known. It is not a predicate only on the
unsigned union \(Q\cup R\), and it uses signs on replacement triples that
need not be active.

There is a literal XOR form. Encode \(+\) by zero and \(-\) by one.
Compatibility says that

\[
 \operatorname{bit}\epsilon(I;e,f)
 \mathbin\oplus\operatorname{bit}\rho_I
 \mathbin\oplus\operatorname{bit}\rho_{I-e+f}          \tag{5}
\]

is constant over the \(\rho\)-colored sources in (4), together with the
analogous expression for \(\eta\). The leading minus in (3) is common to all
sources and cancels from the equality test.

## 3. Moving-witness shear lemma

> **Lemma (simultaneous moving-witness shear).** Suppose (1) holds for
> signatures \(\rho,\eta\), with nonnegative nonzero witnesses supported on
> \(Q,R\). If \(e\to f\) is sign-compatible, let \(a\) be the common value
> in (4) when that set is nonempty, and choose either
> \(a\in\{+1,-1\}\) when it is empty. Define
>
> \[
> g_t(e_e)=e_e+t e_f,\qquad g_t(e_i)=e_i\quad(i\neq e),
> \qquad T_t=T\circ g_t.                               \tag{6}
> \]
>
> For every \(u\geq0\), set \(t=au\) and transport both signed Gordan forms:
>
> \[
> c_\rho(u)=\Lambda^3(g_{au}^{-1})c_\rho,\qquad
> c_\eta(u)=\Lambda^3(g_{au}^{-1})c_\eta.              \tag{7}
> \]
>
> Both transported forms remain nonzero in their original signed
> nonnegative orthants and
>
> \[
> \Lambda^3T_{au}(c_\rho(u))=0,\qquad
> \Lambda^3T_{au}(c_\eta(u))=0.                       \tag{8}
> \]
>
> Hence every finite part of this ray that remains in the original uniform
> parent cell lies in \(B_\rho\cap B_\eta\). New active triples are allowed.

**Proof.** Let \(N(e_e)=e_f\) and \(N(e_i)=0\) for \(i\neq e\). Then
\(N^2=0\), \(g_t=1+tN\), and \(g_t^{-1}=1-tN\). Therefore

\[
 \Lambda^3(g_t^{-1})(e_I)=
 \begin{cases}
 e_I-t\epsilon(I;e,f)e_{I-e+f},&e\in I,\ f\notin I,\\
 e_I,&e\notin I\text{ or }f\in I.
 \end{cases}                                          \tag{9}
\]

The second line includes \(e,f\in I\), because the possible new wedge then
contains \(e_f\) twice. For a source \(I\in S_\rho\), put \(J=I-e+f\).
The coefficient generated at \(e_J\), measured in the
\(\rho_J\)-reoriented orthant, is

\[
 \rho_J\bigl(-t\epsilon(I;e,f)\rho_I\lambda_I\bigr)
       =t\alpha_\rho(I;e,f)\lambda_I.                 \tag{10}
\]

For fixed \(e,f\), the source-to-target map \(I\mapsto I-e+f\) is injective.
On the compatible ray \(t=au\), every affected target weight is therefore

\[
                         \lambda_J+u\lambda_I\geq0,   \tag{11}
\]

where \(\lambda_J=0\) when \(J\) was inactive. Source weights and all other
weights are unchanged, so the transported form remains nonzero. The same
calculation applies to the \(\eta\) block.

Finally \(T_t\circ g_t^{-1}=T\). Functoriality of exterior powers gives

\[
 \Lambda^3T_t\,\Lambda^3(g_t^{-1})c
                 =\Lambda^3T(c)=0.                   \tag{12}
\]

This proves (8). Equation (11), rather than preservation of a frozen support
plane, is the point of the construction. \(\square\)

## 4. Proper escape: finite wall or infinity

Let \(\Delta_A(T)=\det(y_i:i\in A)\), with \(A\) written increasingly.
Multilinearity under (6) gives

\[
 \Delta_A(T_t)=
 \begin{cases}
 \Delta_A(T),&e\notin A\text{ or }f\in A,\\
 \Delta_A(T)+t\epsilon(A;e,f)\Delta_{A-e+f}(T),
       &e\in A,\ f\notin A.
 \end{cases}                                          \tag{13}
\]

Here \(\epsilon(A;e,f)\) is the four-element analogue of (2). Parent
uniformity makes every slope in the second line nonzero. Restrict to
\(t=au\), \(u\geq0\), and let \(u_*>0\) be the least positive zero of any
parent bracket, if one exists.

* If \(u_*<\infty\), every parent sign is unchanged for
  \(0\leq u<u_*\), and at least one parent bracket vanishes at \(u_*\).
  The moving witnesses persist on the entire half-open interval. The path
  stops at this **first** parent boundary. Nothing here says that it reaches
  a preselected later wall or continues in the same parent cell past \(u_*\).
* If there is no positive root, let \(u\to\infty\). Positive rescaling of the
  moving column by \(1/u\) gives the projectively equivalent column

  \[
                   u^{-1}y_e+a y_f\longrightarrow a y_f.          \tag{14}
  \]

  Thus labels \(e,f\) become parallel or antiparallel in the standard
  projective-configuration compactification, again a nonuniform boundary.

Let \(\gamma:[0,u_*)\to B_\rho\cap B_\eta\) denote the finite-endpoint path,
or \(\gamma:[0,\infty)\to B_\rho\cap B_\eta\) in the second case, after the
standard continuous normalization. For every finite \(v\) in its domain,
\(\gamma([0,v])\) is a connected set containing \(\gamma(0)\). It is
therefore contained in the connected component \(C\) of \(\gamma(0)\).
Every point of the half-open ray lies in one such segment, so

\[
                         \gamma(\operatorname{dom}\gamma)\subset C. \tag{15}
\]

This is why crossing lower circuit faces, acquiring new active triples, or
self-intersecting cannot move the path to another connected component.

Now use the standard Hausdorff projective-configuration compactification of
the normalized realization space. In the finite case, \(\gamma(u)\) tends
to the parent dependency in (13). In the infinite case, the positively
rescaled representatives tend to the dependency in (14). If \(C\) were
compact, its image in that compactification would be compact and hence
closed. The boundary limit of the sequence in (15) would then belong to
\(C\), contradicting that every point of \(C\) has a uniform parent.

> **Corollary (conditional component escape).** If one point of a connected
> component of \(B_\rho\cap B_\eta\) has a pair of sign-compatible Gordan
> witnesses, then that component is noncompact.

Thus the remaining issue is universal existence of compatible witnesses,
not properness of the ray after such witnesses have been found.

## 5. A finite low-source reduction

For active supports \(Q,R\), define the colored source count

\[
 m(e,f)=\#\{I\in Q:e\in I,f\notin I\}
       +\#\{I\in R:e\in I,f\notin I\}.                \tag{16}
\]

Every triple contributes to exactly \(3\cdot5=15\) ordered source-target
pairs. Hence

\[
                  \sum_{e\neq f}m(e,f)=15(|Q|+|R|).  \tag{17}
\]

For minimal Gordan supports \(|Q|,|R|\leq5\), the right side is at most 150,
so some one of the 56 ordered pairs has \(m(e,f)\leq2\). A pair with
\(m\leq1\) is automatically compatible. If every \(m\geq2\), and \(n_2\)
counts the ordered pairs with \(m=2\), then

\[
 150\geq2n_2+3(56-n_2)=168-n_2,
 \qquad\text{so}\qquad n_2\geq18.                    \tag{18}
\]

Thus any obstruction is forced into many two-source XOR conflicts. Equation
(18) is a proved reduction, not a proof that one of those XOR tests passes.
The negative canary below shows that arbitrary full signings can make every
ordered shear fail.

## 6. Exact finite census

The accompanying verifier uses only integer arithmetic and exact rational
comparison. It imports no extension enumerator. It loads the stable
row-2599 shatter certificate, checks each selected Gordan dependence and its
support-minimality, and exhausts all 56 ordered shears.

For the 65 stored pencil-rigid \(4+5\) or \(5+5\) occurrences, representing
55 distinct unsigned support pairs, the exact distribution is:

| compatible shears | occurrences |
|---:|---:|
| 10 | 2 |
| 11 | 1 |
| 12 | 1 |
| 13 | 1 |
| 14 | 1 |
| 15 | 6 |
| 16 | 5 |
| 17 | 7 |
| 18 | 7 |
| 19 | 7 |
| 20 | 2 |
| 21 | 7 |
| 22 | 5 |
| 23 | 4 |
| 24 | 1 |
| 25 | 2 |
| 26 | 1 |
| 27 | 4 |
| 29 | 1 |

There are 1,244 compatible occurrence/shear pairs in total, and all 1,244
meet a finite first parent wall in their stored charts. This endpoint count is
only a feature of the sample; the lemma needs the infinity alternative in
general.

For the exact parent-16 defect-two pair

~~~text
rho = 26988370886400909
eta = 45348283816043521
Q   = 123/124/134/235/567
R   = 126/247/158/468/378
~~~

there are exactly 22 compatible ordered shears. For example,
\(2\to1\) is compatible with \(a=-1\), so the preserving ray is
\(y_2\mapsto y_2-u y_1\). Every one of the 22 rays has a finite first parent
wall. The verifier also checks the exterior transport identity on all 56
basis three-forms, for all 56 ordered label pairs and both integral parameter
signs.

Finally, retain the parent-16 supports but replace the two full signings by

~~~text
canary_left  = 36592014375624197
canary_right =   512238212525449
~~~

These agree with \(\rho,\eta\) on their respective active triples, so the
same positive circuits exist at the displayed parent chart. Nevertheless all
56 ordered shears fail compatibility. The canary is deliberately outside the
oriented-matroid domain: its two signings violate 182 and 224 exact
Grassmann--Pluecker sign relations. It refutes an unsigned or
arbitrary-signing shortcut, not the desired statement for realizable
extension signatures.

Run:

~~~console
python ai/omreal/verify_diag2_moving_witness_shear.py
~~~

## 7. Remaining rigorous target

The direct escape route is now reduced to the following precise question.

> At every point of every simultaneous-bad locus for two valid realizable
> extension signatures, can one choose two support-minimal nonnegative Gordan
> witnesses for which at least one ordered shear passes (4)?

The row-2599 and parent-16 checks are positive evidence. The low-source
identity (17), XOR test (5), and invalid-signing canary delimit the finite
obstruction. No argument presently excludes that obstruction for all valid
extensions and all realizable parents, so the nine-diagonal ledger remains
unchanged.
