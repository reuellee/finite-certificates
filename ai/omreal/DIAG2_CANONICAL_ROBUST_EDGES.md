# Diagonal 2: canonical robust-edge common-shear audit

## Result

The complete exact replay **passes all thirteen canonical residual incidence
types**

```text
36, 37, 38, 39, 41, 42, 44, 46, 47, 48, 49, 50, 51.
```

For each type, the verifier constructs one exact generic point on the
canonical residual wall and two exact points on its opposite sides.  For an
extension signature `rho` that is bad at both endpoints, define the robust
edge escape mask

\[
 E_{\mathrm{edge}}(\rho)
   =E_{\mathrm{left}}(\rho)\cap E_{\mathrm{right}}(\rho).
\]

The test asks whether

\[
 E_{\mathrm{edge}}(\rho)\cap E_{\mathrm{edge}}(\eta)\ne\varnothing
\]

for every pair of signatures bad on both sides.  Thus every checked edge has one
elementary shear that works for each decorated pair and remains valid on
both sides of that mutation.

The full four-worker replay completed in **205.034 seconds**.  It checked
557,578 common-bad signature records and 12,091,441,965 within-edge decorated
pairs.  Every robust mask has at least 52 directions, and the minimum overlap
of any two robust masks is at least 9.

Every endpoint has exactly 26,112 complete derived topes.  `Exchange` below
is the number removed from each side (equal to the number added); `Bad/side`
is equal at the two endpoints.

| Type | Factor | Valid extensions | Exchange | Bad/side | Common bad | Min robust | Min overlap | Semantic digest |
|---:|---:|---:|---:|---:|---:|---:|---:|:---|
| 36 | 2277 | 80,924 | 72 | 54,812 | 54,740 | 53 | 10 | `2b140df44cda49fd34463e24fad724f5a5011060ab8401af1b7582bd2357b8c6` |
| 37 | 2342 | 71,174 | 72 | 45,062 | 44,990 | 53 | 10 | `23a9ec75cdef3c733207e084fd6913bd18b4c1b60e533b578af1dacda4b6f4c1` |
| 38 | 3811 | 64,764 | 10 | 38,652 | 38,642 | 53 | 11 | `92148e87c8cefde59863fa6d7b910278a3e95d3481c37f3887b2189120a1f224` |
| 39 | 5552 | 70,826 | 72 | 44,714 | 44,642 | 53 | 11 | `e79d1156f42a56914606907784190dab2d2ebf96c8d93a4ddee38d708f31b15e` |
| 41 | 8543 | 73,138 | 72 | 47,026 | 46,954 | 53 | 11 | `74e1ff86866634dc1fcf17257213e4fc0ece04ac30689a9a2f8994054d02e447` |
| 42 | 9559 | 62,872 | 10 | 36,760 | 36,750 | 53 | 9 | `41d8d2bb635d98595e7c140f0019e9771bb8fe6a8c02e23b5cfcca5b969c1431` |
| 44 | 3487 | 64,746 | 72 | 38,634 | 38,562 | 53 | 11 | `8d2cf02aa3a115d01c47cc2d0cb52d014cdbab4282e35f4d778d3908e6ad4f1b` |
| 46 | 18102 | 68,968 | 72 | 42,856 | 42,784 | 53 | 10 | `9bb7ddc900ac8099d83d3b69e95e2b6c2f4dc7de9c1b7bb2713e9671ef9fed41` |
| 47 | 18102 | 66,716 | 72 | 40,604 | 40,532 | 52 | 9 | `89e70fb8500c5fbcd25aa382c4f885d3c4d565c84f8095dc8474e549ed5e0ddf` |
| 48 | 13950 | 66,852 | 4 | 40,740 | 40,736 | 52 | 11 | `7707831a2bb5914efad5ad661ef56335437841f2ecc59357d016d48e2af2905c` |
| 49 | 2267 | 71,076 | 2 | 44,964 | 44,962 | 53 | 9 | `c24d123836af150fa196362a1e0c578b1c48a354f44ecf813933686fbf52dc44` |
| 50 | 5563 | 70,212 | 2 | 44,100 | 44,098 | 53 | 10 | `f8822a2931b53195956bed370718ec6f634c46b3f92297b17e154c31140cd65f` |
| 51 | 18606 | 65,300 | 2 | 39,188 | 39,186 | 52 | 10 | `11d16355dd2103e7bed4d1e3decdb764dc7bc930beea377666a947fc727c2cae` |

All thirteen semantic digests are pinned in the verifier, so any change to an
exact center, endpoint tope table, robust mask, or quantitative report fails
the replay.

## Exact generic-edge construction

Use the normalized parent chart

\[
Y=\begin{bmatrix}
1&0&0&0&1&1&1&1\\
0&1&0&0&1&a&d&g\\
0&0&1&0&1&b&e&h\\
0&0&0&1&1&c&f&i
\end{bmatrix}.
\]

The global-factor census identifies the primitive polynomial `q_k` belonging
to each canonical incidence type.  Types 46 and 47 are deliberately retained
as two incidence types even though they share the same primitive global
factor.  Hence the scope is thirteen incidence types but twelve distinct
primitive factors.

For each type the checker independently verifies the affine identity

\[
q_k=U_kp_k+V_k,
\]

where `p_k` is its canonical pivot and `U_k`, up to sign, is the following
product of parent brackets.

| Type | Pivot | Bracket-unit coefficient |
|---:|:---:|:---|
| 36 | `a` | `[1237]` |
| 37 | `a` | `[1257]` |
| 38 | `a` | `[1278]` |
| 39 | `a` | `[2378]` |
| 41 | `a` | `[2457]` |
| 42 | `a` | `[2478]` |
| 44 | `d` | `[2356][1258]` |
| 46 | `a` | `[1237]` |
| 47 | `a` | `[1237]` |
| 48 | `a` | `1` |
| 49 | `d` | `1` |
| 50 | `d` | `[1238]` |
| 51 | `f` | `[2468][1456]` |

Eight nonpivot coordinates are deterministically generated as small integers,
and the ninth is set to `-V_k/U_k` in exact rational arithmetic.  This does
not merely check `q_k=0`.  Against the complete checked-in census of 26,740
primitive global residual factors, the verifier proves that `q_k` is the
only zero.  It also proves that all seventy parent brackets are nonzero.

The exact perturbations `p_k-epsilon` and `p_k+epsilon` are then checked
against all seventy parent brackets and all 26,740 residual factors.  Every
parent sign and every unselected residual sign stays fixed, while exactly
the selected primitive factor reverses sign.  This is the sense in which the
audit uses a generic residual edge rather than an uncontrolled multistratum
crossing.

## Complete finite test on each endpoint

At both exact endpoints the verifier:

1. clears only positive column denominators, preserving the projective
   configuration and every chirotope sign;
2. enumerates and independently verifies the complete derived-arrangement
   tope table;
3. exactly enumerates every valid uniform one-element extension of that
   endpoint's parent chirotope;
4. proves both complete-tope sets are subsets of that GP-valid universe and
   that `bad + tope = valid` on each side;
5. retains the signatures absent from both endpoint tope tables;
6. computes all 112 elementary-shear escape directions at each endpoint;
7. intersects the two masks signature by signature; and
8. uses the bitset intersection certificate to reject any disjoint pair of
   robust masks.

No floating point arithmetic, sampled extension family, or heuristic LP is
used.

## Reproduction

The complete four-worker replay is the no-argument default:

```console
python ai/omreal/verify_diag2_canonical_robust_edges.py
```

One or two selected types can instead be replayed alone:

```console
python ai/omreal/verify_diag2_canonical_robust_edges.py --types 36 37 --workers 2
```

The same full selection can be requested explicitly:

```console
python ai/omreal/verify_diag2_canonical_robust_edges.py --all --workers 4
```

The lighter construction-only check, which still verifies the unique wall
zero and isolated exact perturbation, is

```console
python ai/omreal/verify_diag2_canonical_robust_edges.py --all --workers 4 --witnesses-only
```

## Scope and what remains

This is intentionally a **canonical-incidence audit**, not a chamber-coverage
theorem.  The passed replay establishes robust common-shear overlap at
thirteen exact generic edges, one for each canonical incidence type.  It does
not by itself cover:

* all 84,840 labeled residual occurrences;
* all 26,740 relative-label primitive factors;
* every chamber adjacent to one of those walls;
* every parent realization cell; or
* diagonal two of 9DVL globally.

The value of this result is narrower and structural: it tests every
canonical local mutation mechanism with the stronger two-sided robust mask,
and it creates a reproducible bridge from the single-chart common-shear
evidence to a future equivariant/coverage argument.
