# Diagonal four: a four-shear theorem and complete D4-SP support sieve

## Handoff

This is a **positive intermediate theorem and strict finite reduction**, not a
proof of D4-SP and not a ledger promotion.

The fixed single-piece proposition is:

> **D4-SP.** For every realizable uniform rank-four oriented matroid `M` on
> `[8]`, every proper pairwise-incomparable four-signature family `S`, every
> `rho in S`, and every circuit support `Q` with `1 <= |Q| <= 5` and union
> `[8]`, the closed piece `C_(rho,Q)`, including zero-weight faces and all
> structural/residual-wall specializations in the normalized realization
> cell, has `H_c^3(C_(rho,Q);Q)=0`.

The theorem below proves D4-SP for `915,740` of the complete `1,715,980`
labeled support shapes, or `77` of `130` `S_8`-orbits. It leaves exactly
`800,240` labeled shapes in `53` orbits. Those survivors are a support-shape
superset: this cycle does not assert that every shape occurs as a positive
signed third-compound circuit.

## 1. The signed four-shear theorem

For a set `U` of parent triples, say that a label `e` is **dominated** by a
distinct apex `f` when

\[
 e\in I\in U\quad\Longrightarrow\quad f\in I.                 \tag{1}
\]

Define `B31(U)` to mean that there are four distinct moving labels
`e_1,e_2,e_3,g` and **distinct** fixed apices `f,h`, neither of which is
moving, such that

\[
 e_1,e_2,e_3\text{ are dominated by }f,
 \qquad g\text{ is dominated by }h.                            \tag{2}
\]

> **Three-plus-one four-shear theorem.** Let
>
> \[
> Z=C_{\rho_1,Q_1}\cap\cdots\cap C_{\rho_t,Q_t}
> \]
>
> be an intersection of closed Gordan circuit pieces in a fixed normalized
> uniform rank-four/eight parent realization cell, and let `U` be the union
> of their support triples. If `B31(U)` holds, then
>
> \[
>                  H_c^q(Z;\mathbb Q)=0\qquad(0\le q\le3).     \tag{3}
> \]

This is a signed third-compound statement. It is not an inference from the
unsigned support count.

### Proof

For each of the first three moving columns and for the fourth moving column,
consider the column motions

\[
 y_{e_i}\mapsto y_{e_i}+t_i y_f\quad(i=1,2,3),
 \qquad y_g\mapsto y_g+u y_h.                                 \tag{4}
\]

If a support triple contains `e_i`, (1) says that it also contains `f`, so
its third exterior product is unchanged by the corresponding motion. The
same holds for `g,h`. No support triple can contain both an `e_i` and `g`,
since it would then contain the four distinct labels `e_i,g,f,h`. Thus every
signed support normal in every
`Q_j` is unchanged along (4), up to the harmless positive ray normalization.
Every nonnegative Gordan dependence persists after positive rescaling and
renormalization. In particular, a zero weight stays zero. This proves that
the full closed pieces—not only their strict five-circuit strata—are constant
along the four-shear leaves.

Here is a projectively invariant quotient description, avoiding a hidden
choice of column scales. Retain the four nonmoving oriented rays. For each
moving label `m` with apex `a`, retain the projective line
`span(y_m,y_a)`. Quotient by the common projective action. A fiber of the
resulting semialgebraic map `pi:Z -> Z'` varies each moving ray on its retained
line away from the apex. Uniformity excludes the apex and supplies an affine
coordinate. Hence a nonempty fiber is an open semialgebraic set

\[
                         \Omega\subset\mathbb R^4              \tag{5}
\]

with coordinates `(t_1,t_2,t_3,u)`. Distinctness of `f,h` is also what makes
the quotient fiber genuinely four-dimensional: relative to the four fixed
rays, preservation of a line with apex `f` equates the three other diagonal
projective scales, while preservation of the line with distinct apex `h`
forces the remaining equality. The stabilizer is therefore scalar. The
circuit conditions impose no extra
cut on (5), by the preceding signed-normal calculation. This construction is
valid on structural and residual derived walls because it used only parent
uniformity and the exact exterior-product identity.

Fix `u`. Every prescribed parent four-bracket is affine jointly in
`(t_1,t_2,t_3)`: any term involving two of those parameters contains two
copies of `y_f` and vanishes. Coefficients may depend affinely on the fixed
`u`; that does not affect the conclusion. Therefore

\[
 \Omega_u=\{(t_1,t_2,t_3):(t_1,t_2,t_3,u)\in\Omega\}           \tag{6}
\]

is empty or open convex.

Let `Omega_0` be a connected component. Its projection `J` to the `u`-axis
is a connected open interval. A nonempty convex section (6) cannot meet two
components of `Omega`, so the fibers of `Omega_0 -> J` are the full nonempty
convex sections. Local persistent points and a partition of unity on `J`
give a continuous section. Straight-line motion in each section retracts
`Omega_0` onto that section and then onto `J`. Thus every component of
`Omega` is contractible.

Each component is an oriented open four-manifold. Poincare duality therefore
gives

\[
 H_c^j(\Omega_0;\mathbb Q)
 \cong H_{4-j}(\Omega_0;\mathbb Q)=0\qquad(j<4).                \tag{7}
\]

Semialgebraicity gives finitely many components, so (7) holds for the whole
fiber. Fiberwise compactification of `pi` and proper base change identify the
stalks of `R^j pi_! Q` with these compact-support groups. All rows below four
vanish. The compact-support Leray spectral sequence then proves (3). QED.

### Quantifiers and boundary audit

The proof does not assume that a support is generic, support-minimal, strict,
or realized away from a residual wall. It is uniform in the parent `M`, the
signature family `S`, the selected `rho`, and all signs. Since it proves more
than needed for any family, it includes the properness and pairwise-
incomparability quantifiers of D4-SP. Positive rescaling preserves each signed
Gordan equation, and zero weights remain zero, so every closed lower-weight
face is retained. Parent nonuniformity is the end of the open realization
cell and is correctly measured by compact supports; it is not silently added
to a fiber.

## 2. Complete support-shape classification for D4-SP

A support with at most two triples cannot cover eight labels, so the complete
cover-all domain has sizes three, four, and five. The exact semantic-kernel
verifier enumerates every subset of the 56 triples, applies `B31`, and
quotients by all `8!` label permutations.

| support size | all labeled | all orbits | B31 labeled | B31 orbits | survivor labeled | survivor orbits |
|---:|---:|---:|---:|---:|---:|---:|
| 3 | 840 | 1 | 840 | 1 | 0 | 0 |
| 4 | 72,380 | 14 | 53,060 | 10 | 19,320 | 4 |
| 5 | 1,642,760 | 115 | 861,840 | 66 | 780,920 | 49 |
| **total** | **1,715,980** | **130** | **915,740** | **77** | **800,240** | **53** |

The previously reported `1,099,560` supports in `66` orbits are only the
generic cover-all five-support subdomain. On that subdomain, `B31` proves
vanishing for `339,360` supports in `21` orbits and leaves `760,200` in `45`
orbits. It would be incorrect to substitute those generic numbers for the
complete D4-SP domain.

The verifier prints the canonical representative of every one of the 53
survivor orbits. Its full classification digest is

```text
16b11cba052b49af777354f256a783b419ec6e246d178de70c238807e50ecc11
```

## 3. Canaries

* **Positive:** `123/124/235/147/368` has block `(5,6,8)` dominated by apex
  `3` and line label `4` dominated by apex `1`. The checked-in row-2599 shatter
  certificate verifies this as an actual strict positive signed five-circuit
  in a proper pairwise-incomparable family.
* **Negative/survivor:** `123/134/267/258/468` has no `B31` witness. The
  checked-in row-2599 certificate verifies that it is a strict positive signed
  five-circuit in one member of an exact proper pairwise-incomparable
  four-signature family. This prevents the sieve from hiding behind an
  unrealizable unsigned support.
* **Null/out of domain:** `123/124/125/126/127` omits label `8` and is not
  promoted into the fixed cover-all proposition.
* **Hostile split--remerge:** two compact parallel edges from a split vertex
  to a merge vertex have rank-one boundary and a nonzero anti-diagonal cycle.
  This is the exact finite core of the doubled-interval warning. It is an
  abstract constructible-sheaf countermodel, not an OM occurrence, and blocks
  any claim based only on branch escape. The new theorem avoids it by proving
  convex three-dimensional sections over a one-dimensional base.
* **Hostile separate convexity:** the square boundary has rank-three
  incidence and one-dimensional `H_1`; it is the finite core of the
  two-block model `{(x,y):x dot y>0}`. The theorem does not infer vanishing
  from separate convexity: its `3+1` domination gives convex
  three-dimensional sections over an interval, so the `2+2` loop mechanism
  is excluded by hypothesis.

## 4. Exact replay

From a clean checkout at this branch head:

```console
python ops/team/diag4-top-sheaf-prover/verify_four_block_line_sieve.py
```

The run uses ordinary local CPU, exact integer combinatorics, exact stored
row-2599 witnesses, the complete `S_8` action, and no network or floating-
point acceptance test. On the cycle host it completed in about 69 seconds.

## 5. Nonconsequences and next discriminator

This result does **not** prove D4-SP on the 53 survivor orbits. It does not
prove that a survivor has nonzero `H_c^3`, compute any restriction map, prove
fivefold middle exactness, or change the `2/9` ledger.

The complete surviving support list is printed by the verifier. The load-
bearing distinction is now exact: every survivor lacks a `3+1` domination
decomposition. Its four light parameters therefore split at best into
interacting `2+2` or smaller blocks, where bilinear cross terms can support a
split--remerge loop. The next discriminator must use the actual signed
determinant system on these 53 orbit representatives—e.g. an exact
top-component-sheaf differential or an admissible realizable split--remerge
obstruction—not another light-label count.
