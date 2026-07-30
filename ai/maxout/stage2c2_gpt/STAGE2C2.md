# Stage 2c-2: labeled equal-pair ground truth and the first broad GP transfer

Date: 2026-07-31

## Headline

All labels, rows, chirotope signs, and target systems in this stage are
derived from the single authoritative configuration in
`../stage2b_gpt/reference_structure.json`:

```text
U_ints =
[-6, -13,  18]
[-9, -12,   8]
[-13, -4,  16]
[ 4, -19,  -8]
[16,  15, -12].
```

There are three main results.

1. **The true labeled equal-pair partition is now exact.** Among the
   66,280 systems \((\sigma,k)\), with all 33,140 valid labeled sigmas and
   \(k\in\{1,2\}\), exactly **51,430** admit some antipodal-symmetric
   (equal-pair) Gordan certificate at `U_ints`, and exactly **14,850** do
   not. Every covered system has an exact primitive-integer certificate;
   every hard system has an exact strict-primal witness proving the no-go.
2. **The ordinary coefficientwise-positive mechanism has a sharp
   all-degree boundary.** It covers exactly the previously known
   single-class family, **33,437 / 66,280** systems. Multi-class
   coefficientwise-positive multiplier polynomials whose identities hold
   without Grassmann--Pluecker reduction add **zero** systems, at every
   degree.
3. **The GP hunt succeeds broadly on the prioritized hard region.** On 120
   research targets (20 canonical HARD systems and all 100 historical
   failed targets), 64 have exact quotient-ring certificates with
   side-multiplier degree 1, and **all 120** have exact certificates with
   side-multiplier degree 2 and weight-multiplier degree 3. Thus every
   prioritized target is covered within overall polynomial degree 3.
   At that degree, 109/120 accepted certificates are genuinely
   T-carrying; the remaining 11 use equal-pair side support but require GP
   reduction in the weight equations.

These results do **not** yet prove global \(\max f_0(3,5)=42\): the
degree-2/3 GP search is exact on its 120 targets, not an exhaustive scan of
the 32,843 systems outside the single-class cell-wide family.

## Conventions and exact row model

Pairs are in lexicographic order

```text
(01),(02),(03),(04),(12),(13),(14),(23),(24),(34).
```

For \(C_{ij}=U_i\times U_j\),
\(D_{tij}=|\det(U_t,U_i,U_j)|\), split signs \(s_t\), and side orientation
\(\rho\in\{+1,-1\}\), side row \((ij,\rho)\) is

\[
 B_{ij,\rho}
 =\sigma_{ij,\rho}
  \left(\rho C_{ij},
  \bigl(s_tD_{tij}{\bf1}_{t\notin\{i,j\}}\bigr)_{t=0}^4\right).
\]

Rows 20--24 are the five positive-weight coordinate rows. The primal
variables are \((T_0,T_1,T_2,w_0,\ldots,w_4)\). All reference rows are
integral.

If the two sigma signs on class \((i,j)\) agree and its two side
multipliers are equal, the T columns cancel identically. The reduced class
row is the sum of the two side rows:

\[
 (0,0,0;\ 2q_{ij}s_tD_{tij}{\bf1}_{t\notin\{i,j\}}),
 \qquad q_{ij}=\sigma_{ij,+}=\sigma_{ij,-}.
\]

This is the exact restricted system used for the labeled equal-pair sweep.

## Objective 1: exact labeled T-independent coverage map

`equal_pair_coverage.json.gz` stores:

- the 33,140 valid labeled sigmas in ascending bit order;
- both splits \(k=1,2\), for 66,280 explicitly indexed systems;
- 8,051 distinct ten-symbol class patterns and 16,102
  `(pattern, split)` results;
- one exact reduced Gordan certificate per covered pattern/split;
- one exact strict-primal witness per hard pattern/split;
- a system-to-pattern mapping, followed by an exact lift/check against the
  full 25-row labeled matrix for every covered system.

The exact partition is:

| labeled status | \(k=1\) | \(k=2\) | total |
|---|---:|---:|---:|
| T-INDEPENDENTLY-COVERED | 28,106 | 23,324 | **51,430** |
| HARD | 5,034 | 9,816 | **14,850** |
| all systems | 33,140 | 33,140 | **66,280** |

Here `HARD` has the precise restricted meaning: no Gordan certificate
using any collection of equal-sign classes, equal multipliers on the two
sides of each used class, and arbitrary nonnegative weight-row
multipliers exists even at the reference determinant values. The stored
strict-primal witness proves this exactly by Gordan's alternative.

This replaces the Stage 2b-1 representative-level counts. Global flip is
not used as a coverage shortcut: both labeled members are reconstructed
and checked. Pattern caching is only an exact reuse after the labeled
class pattern has been computed.

### Mandatory canaries

The sweep searches the following canonical Stage 2b residue members before
all other systems:

| sigma bits | split | pattern | expected/result |
|---:|---:|---|---|
| 10,070 | \(k=1\) | `xxxx+xx---` | HARD / HARD |
| 25,998 | \(k=2\) | `x+-xxxxx--` | HARD / HARD |

Their stored minimum exact strict margins are respectively \(1\) and
\(1986708/1986721\). A dual success on either target would have stopped
the sweep as a verifier failure.

## Objective 2: boundary theorem for ordinary coefficientwise positivity

### The theorem

For a labeled system and split, an equal-pair certificate with
coefficientwise-nonnegative multiplier and weight-slack polynomials, whose
identities hold as ordinary polynomial identities in the ten formal
positive \(D_{ijk}\), exists **if and only if** some equal-sign class
\((i,j)\) satisfies

\[
 q_{ij}s_t=-1\qquad\text{for every }t\notin\{i,j\}.
\]

Sufficiency is the corrected single-class certificate

\[
 y_{ij,+}=y_{ij,-}=1,\qquad
 y_{w_t}=-2q_{ij}s_tD_{tij}=2D_{tij}
 \quad(t\notin\{i,j\}),
\]

with all other multipliers zero.

For necessity, every pattern failing the criterion has a stored exact
positive formal determinant vector \(d=(d_{012},\ldots,d_{234})\) such
that, at primal weights \(w=(1,1,1,1,1)\),

\[
 q_{ij}\sum_{t\notin\{i,j\}}s_t d_{tij}>0
\]

for every eligible equal-sign class. This is a strict-primal witness at a
positive formal-D point. Evaluating any purported ordinary
coefficientwise-positive polynomial Gordan certificate there would give a
numeric certificate and contradict strict feasibility. The argument is
degree-independent.

The resulting exact labeled partition is:

| ordinary coefficientwise mechanism | \(k=1\) | \(k=2\) | total |
|---|---:|---:|---:|
| criterion satisfied | 24,691 | 8,746 | **33,437** |
| impossible at every degree | 8,449 | 24,394 | **32,843** |

`coefficientwise_boundary.json.gz` contains the criterion result or the
exact formal-D strict witness for all 16,102 pattern/split systems.

### Independent finite-degree enumeration

`coefficientwise_mechanisms.json.gz` separately constructs the complete
coefficient cone for homogeneous side-multiplier degrees 0 and 1. Every
success vector and every separating no-go functional is an exact primitive
integer vector. Degree 0 gives 33,437 labeled systems; degree 1 gives the
same 33,437. Thus the explicit enumeration finds zero multi-class
extensions, in agreement with the all-degree theorem.

The formal-D no-go points need not lie on the Pluecker variety. This is
intentional and is valid only for the mechanism whose identities hold
without GP reduction. It does not obstruct the quotient-ring mechanisms
in the next section.

## Objective 3: T-carrying quotient-ring hunt

### Search space

Let \(I_{\rm GP}\) be the five-quadratic Grassmann--Pluecker ideal after
substituting the reference chirotope signs into the positive \(D\)
variables. For search parameter \(d\):

- each of the 20 side multipliers is a homogeneous
  coefficientwise-nonnegative polynomial of degree \(d\);
- each of the five weight-row multipliers has degree \(d+1\);
- all three T equations and all five weight equations vanish modulo
  \(I_{\rm GP}\).

This gives a sparse rational cone in the signed-D quotient ring. HiGHS is
used only to locate a support or a separating functional. A certificate is
accepted only after its nonnegative coefficients and exact quotient-ring
kernel are checked. Every accepted certificate is also specialized at the
integer reference determinant values and checked against all eight columns
of the full labeled 25-row matrix.

Allowing the five weight-row multiplier polynomials as independent
unknowns modulo \(I_{\rm GP}\) is the important enlargement over the
Stage 2c-1 degree search, which derived ordinary coefficientwise slacks and
therefore missed these certificates.

### Targets

The exact ledger contains 120 research targets:

- the first ten canonical objective-1 HARD representatives at \(k=1\);
- the first ten canonical objective-1 HARD representatives at \(k=2\);
- all 100 targets from `../stage2b_gpt/symbolic_gp_results.json`.

The historical failed-100 set contains 68 mapped \(k=3\) splits and 32
mapped \(k=2\) splits. Of the latter 32, 15 are objective-1 HARD and 17
are T-INDEPENDENTLY-COVERED at the reference values. Thus "failed-100" is
a historical search designation, not synonymous with the new labeled
HARD status.

### Exact outcomes

The following degree convention is essential: `d` is the side-multiplier
degree and weight multipliers have degree `d+1`.

| side degree \(d\) | largest multiplier degree | exact certificates | exact degree no-gos | empirical/undecided |
|---:|---:|---:|---:|---:|
| 0 | 1 | 0 | 120 | 0 |
| 1 | 2 | 64 | 56 | 0 |
| 2 | 3 | **120** | 0 | 0 |
| 3 | 4 | **120** | 0 | 0 |

The \(d=2\) row is the load-bearing "degree up to 3" result requested in
this stage. The \(d=3\) row is a redundant higher-degree stability check,
not needed for any claim.

At \(d=1\), all 20 canonical HARD targets and 44/100 historical failed
targets are already covered. At \(d=2\):

- all 20 canonical HARD targets are covered;
- all 100 historical failed targets are covered;
- 109/120 certificates are genuinely T-carrying;
- 11/120 use equal-pair side support but require GP reduction in their
  weight equations.

Degree-2 support sizes are small:

| nonzero polynomial coefficients | targets |
|---:|---:|
| 4 | 94 |
| 5 | 12 |
| 6 | 10 |
| 7 | 2 |
| 8 | 2 |

### Representative new certificate

The canonical HARD canary system \((\sigma=10070,k=1)\), which provably
has no equal-pair certificate at `U_ints`, has the following four-term
cell-wide quotient-ring certificate:

\[
\begin{aligned}
y_{(02,+)} &= D_{024}D_{234},\\
y_{(23,-)} &= D_{024}^2,\\
y_{(24,-)} &= D_{023}D_{024},\\
y_{w_0} &= 2D_{023}D_{024}^2.
\end{aligned}
\]

All four multipliers are positive monomials throughout the cell. The three
unpaired side rows carry T; their T columns cancel by a genuine
Grassmann--Pluecker dependence. Exact quotient reduction and exact
specialization at `U_ints` both give zero in every one of the eight
columns.

### GP canary integrity

The negative GP canary is deliberately **not** a valid chamber coloring:
`sigma_bits=0`, \(k=1\). It has the exact strict full-system primal witness

```text
(0, 0, 0, 1, 1619/440, 447/88, 1201/440, 1)
```

with minimum margin 1. Hence no Gordan certificate can exist even at the
reference point. It is rejected with an exact separating functional at
every searched degree. A known single-class positive control is accepted
at every degree. No empirical or undecided outcome appears in the final
120-target ledger.

## Exact verification

`check_stage2c2.py` performs the following:

1. rechecks the authoritative reference, labeled sigma set, and system
   order;
2. checks all 66,280 equal-pair classifications, lifting every covered
   certificate to the full 25-row matrix and checking every hard strict
   witness in `Fraction`;
3. checks all formal-D witnesses proving the all-degree coefficientwise
   boundary;
4. checks the degree-0/1 coefficient-cone cross-check;
5. rebuilds the signed-D GP quotient matrices for every target, checks
   every certificate or exact separator, and independently specializes
   every accepted polynomial certificate at `U_ints`.

The completed authoritative run in `check.log` reports:

```text
PASS: all available Stage 2c-2 exact checks completed in 83.8s
```

All primary result artifacts predate that completed checker run. A later
attempt to launch a full sharded \(d=2\) complement sweep was externally
terminated before it wrote any shard result artifact; its short logs and
script are not load-bearing and are not read by the checker.

## Proven / conjectured / failed ledger

### Proven

- Exact labeled equal-pair partition:
  51,430 T-INDEPENDENTLY-COVERED and 14,850 HARD.
- Exact per-split counts:
  28,106/5,034 at \(k=1\), and 23,324/9,816 at \(k=2\).
- Exact all-degree boundary for ordinary coefficientwise-positive
  equal-pair identities: exactly the 33,437 single-class systems; zero
  multi-class extensions.
- Exact degree-0 and degree-1 coefficient-cone enumeration, agreeing with
  the boundary theorem.
- Exact quotient-ring outcomes on all 120 prioritized targets:
  64 degree-\((1,2)\) certificates and 120 degree-\((2,3)\)
  certificates, where the pair denotes side/weight degree.
- Exact negative-canary rejection and positive-control acceptance at every
  searched GP degree.

### Conjectured / open

- The \(d=2\) GP mechanism may cover much or all of the 32,843-system
  complement of the single-class family. The 120/120 result is strong
  evidence, not exhaustive coverage.
- Global \(\max f_0(3,5)=42\) remains open. Closing it still requires
  cell-wide certificates for every remaining labeled system (or an
  equivariant theorem covering them), followed by the already established
  parity/perturbation step.

### Failed or negative

- Multi-class ordinary coefficientwise-positive equal-pair polynomials do
  not extend the single-class family at any degree; this is a theorem, not
  merely a failed search.
- The GP cone at side degree 0 has exact no-gos on all 120 research
  targets.
- The GP cone at side degree 1 has exact no-gos on 56/120 targets.
- The attempted all-complement sharded degree-2 sweep was externally
  terminated after control initialization. No shard result JSON exists,
  and no coverage claim is made from it.

## Reproduction

From the repository root:

```powershell
$PY = 'E:/Projects/sae-identifiability/.venv/Scripts/python.exe'

# Exact standalone audit of all final, load-bearing artifacts.
& $PY ai/maxout/stage2c2_gpt/check_stage2c2.py

# Generators (not needed for verification).
& $PY ai/maxout/stage2c2_gpt/sweep_equal_pair.py
& $PY ai/maxout/stage2c2_gpt/coefficientwise_search.py --max-degree 1
& $PY ai/maxout/stage2c2_gpt/coefficientwise_boundary.py
& $PY ai/maxout/stage2c2_gpt/gp_degree3_search.py --degrees 0,1,2,3
```

Float LPs in the generators are support/point hints only. All serialized
positive kernels, strict primal witnesses, coefficient-cone separators,
and quotient-ring separators are repaired and checked exactly before they
are used in a claim.

## Principal artifact hashes

```text
equal_pair_coverage.json.gz
  8574BB914A7A931E7C0DC0C8389C5E599DFDBB6E7B2CC81AA89BA88BADC3F826
coefficientwise_mechanisms.json.gz
  87A854C2CFF0EDD37B783E556B25F845E78FF8B1FB197C9B7BC27A1A68171CB7
coefficientwise_boundary.json.gz
  49004B439C74999A7C11E5D6F23B40F07CCB1A207FA602FD7869BB04260E4271
gp_degree3_results.json.gz
  80A3BF29201B16B193270453ECF8C90B155C433DB28F5DB2747E98337176C383
gp_degree3_checkpoint.json.gz
  5F8641B0B5B38F445D78C44C758A3D018D4B747955133529EA72B4006CC8763A
check_stage2c2.py
  DF5E9C5CF5C63D1348BFCD339D8FF5447F71B01CD5C9C0EE514377D954D087FE
```
