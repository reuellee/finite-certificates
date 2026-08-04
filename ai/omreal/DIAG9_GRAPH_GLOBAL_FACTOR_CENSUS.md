# Diagonal 9: exact global residual-factor census

## Result

The 84,840 labeled residual determinant occurrences in the standard
nine-variable chart do **not** define 84,840 distinct walls.  After exact
division by parent-bracket units, they define precisely

\[
\boxed{26,740}
\]

distinct primitive polynomials over
\(\mathbb Q[a,b,c,d,e,f,g,h,i]\).

The exact class-size distribution is

| Labeled occurrences per wall | Number of wall classes | Occurrences accounted for |
|---:|---:|---:|
| 1 | 25,200 | 25,200 |
| 2 | 420 | 840 |
| 15 | 280 | 4,200 |
| 65 | 840 | 54,600 |
| **Total** | **26,740** | **84,840** |

This is a proof-safe reduction in the number of equations for a normalized
master residual arrangement.  It is not by itself a chamber decomposition
or a proof of the ninth diagonal.

## Exact construction

Use the normalized matrix

\[
Y=\begin{pmatrix}
1&0&0&0&1&1&1&1\\
0&1&0&0&1&a&d&g\\
0&0&1&0&1&b&e&h\\
0&0&0&1&1&c&f&i
\end{pmatrix}.
\]

For every triple \(T\subset[8]\), the verifier expands the normal
\(n_T\) to its plane.  For every one of the 84,840 labeled residual
four-sets \(E=\{T_1,T_2,T_3,T_4\}\), it then expands

\[
D_E=\det(n_{T_1},n_{T_2},n_{T_3},n_{T_4})\in
\mathbb Z[a,b,c,d,e,f,g,h,i].
\]

Let \(p_I=[I](Y)\) run over the 62 nonconstant parent brackets in this
chart; the other eight brackets are constant units.  Exact lexicographic
division over \(\mathbb Q\) produces

\[
D_E=c_E\,u_E\,q_E,
\]

where \(c_E\in\mathbb Q^*\), \(u_E\) is either `1` or one parent bracket,
and no parent bracket divides \(q_E\).  The polynomial \(q_E\) is made
primitive with lex-leading coefficient positive.  Two occurrences receive
the same factor ID exactly when their sparse \(q_E\) fingerprints agree.

For every occurrence, the verifier multiplies the quotient and stripped
unit back together and compares the primitive result with the original
expanded determinant.  It then tries all 62 brackets again and proves none
divides the residual quotient.

The unit census is strikingly uniform:

| Number of stripped brackets | Occurrences |
|---:|---:|
| 0 | 32,760 |
| 1 | 52,080 |

Each of the 62 nonconstant parent brackets occurs as the stripped unit in
exactly 840 labeled determinants.  No occurrence contains two parent-bracket
factors after primitive normalization.  Before localization, there are
76,498 raw proportionality classes; localization is therefore essential to
the reduction.

## The former 65-label crossing

The 65 determinants at the original row-2599 crossing look like 57 raw
proportionality classes:

| Raw class size | Number of classes |
|---:|---:|
| 6 | 1 |
| 2 | 3 |
| 1 | 53 |

Exact division strips one parent bracket from 59 occurrences and none from
six.  All 65 residual quotients are the same primitive polynomial, up to the
fixed sign convention:

\[
q=-bdi+bfg+cdh-ceg+cei-cfh.
\]

Because six raw determinants are already associates of \(q\), while every
raw determinant is divisible by \(q\), their exact gcd over
\(\mathbb Q[a,\ldots,i]\) is \(q\) up to a nonzero rational scalar.  Thus
the common bivariate factor in the earlier row-2599 disk is not an accidental
plane coincidence or tangency of different walls.  It is the restriction of
one genuine global residual wall.

The new transverse row-2599 node uses two different factor IDs, and each ID
has global multiplicity 65.  Hence its two local branches are restrictions
of two distinct global walls from the 840 large classes.

## Certificate and replay

Run

```bash
python ai/omreal/DIAG9_GRAPH_global_factor_census.py
```

The replay is dependency-free apart from NumPy.  It re-expands all 84,840
determinants over exact rational arithmetic, repeats every division, and
compares every stored array.  A complete run takes a few minutes.

The certificate
`data/DIAG9_GRAPH_global_factor_census.npz` contains:

- all 84,840 labeled four-sets in stable order;
- sparse exponent/coefficient fingerprints for all 26,740 residual factors;
- the occurrence-to-factor map and exact factor multiplicities;
- the exact stripped-bracket list for each occurrence;
- sparse fingerprints and multiplicities for all 57 raw crossing classes;
- the 65 crossing occurrence indices and their common factor ID.

Its compressed size is about 1.2 MB.  Its file SHA-256 is

```text
3984ce87e11fd59d804e59568177248e218cd1c7bb07aae0a9f9f746858728bc
```

The semantic SHA-256 over named, typed, shaped array contents is

```text
8dd371e34f9af178c49d4d0152864a394a0b2defcf16e673ddf885feb6ec0071
```

That semantic digest is hard-coded in the verifier as an immutable
regression value; it is independent of ZIP container metadata.

## Consequence for a master roadmap

A roadmap generator should use the 26,740 residual factor IDs, not the
84,840 labeled determinants, as its wall equations.  Signature labels still
remain attached to all occurrences: crossing one factor may simultaneously
change 1, 2, 15, or 65 labeled constraints.  The factor ID map gives exactly
that incidence information.

This reduction does not establish which of the 26,740 walls meet a given
parent realization cell, which wall intersections are nonempty, or whether
the resulting labeled chamber graph satisfies the ninth-diagonal tree/cut
certificate.  Those are the remaining geometric coverage tasks.
