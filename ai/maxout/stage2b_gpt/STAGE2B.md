# Stage 2b: exact fixed-configuration obstruction for \(f_0(3,5)=44\)

Date: 2026-07-30

## Headline result

**PROVEN, for the single reference configuration**

```text
U_ints =
[-6, -13,  18]
[-9, -12,   8]
[-13, -4,  16]
[ 4, -19,  -8]
[16,  15, -12].
```

For every one of the **33,140** valid labeled side assignments derived from
this configuration's own chamber incidence, and for each split

```text
s1 = (+,-,-,-,-),   s2 = (+,+,-,-,-),
```

the 25-row homogeneous strict system in
\(x=(T_0,T_1,T_2,w_0,\ldots,w_4)\) is infeasible.  This is certified by
**66,280 exact Gordan vectors**

\[
 y\geq 0,\qquad y\neq0,\qquad B^\mathsf{T}y=0.
\]

Every serialized vector was repaired over `Fraction`, cleared to primitive
positive integers, and verified exactly before serialization.  The
standalone checker independently reconstructs the integral matrices and
checks all identities using only the Python standard library.

Consequently the 44-vertex cap is unattainable on these directions.  In the
generic strict regime the number of bicolored chambers is even: the zero set
of the support-function difference is a union of cycles in the bipartite
chamber-adjacency graph, and each bicolored chamber contributes one segment
to those cycles.  A hypothetical 43-vertex instance can be perturbed while
preserving its existing vertices and avoiding all side equalities, hence
would perturb to 44.  Excluding 44 therefore excludes 43 as well.  Thus the
fixed configuration has the exact upper bound

\[
f_0\leq 42.
\]

This is a **per-configuration theorem**, not a proof over every realization
cell and not yet a proof of the global maximum over all direction sets.

## Exact row model

Let \(C_{ij}=U_i\times U_j\),
\(D_{tij}=|\det(U_t,U_i,U_j)|\), and let side \(+\) use \(C_{ij}\) while
side \(-\) uses \(-C_{ij}\).  Starting with unit directions, multiply each
side inequality by the positive factor \(\|C_{ij}\|\) and replace the
positive original weight \(v_t\) by \(w_t=v_t/\|U_t\|\).  This removes all
square roots without changing strict feasibility.  The 20 side rows are

\[
B_{ij,\pm}
 =\sigma_{ij,\pm}
   \left(\pm C_{ij},\,
   \bigl(s_tD_{tij}\mathbf 1_{t\notin\{i,j\}}\bigr)_{t=0}^4\right).
\]

Rows 20 through 24 are the five coordinate rows \(w_t>0\).  All entries of
\(B\) are integers.  If \(Bx>0\) and a serialized certificate satisfies the
three Gordan conditions above, then

\[
0=y^\mathsf{T}Bx>0,
\]

a contradiction.  Conversely, Gordan's theorem says such a vector exists
exactly when the strict system is infeasible.

The two labeled members of every global-flip class were both certified, so
the core bundle does not rely on a questionable factor-of-two shortcut.

## Combinatorial self-consistency

All load-bearing structure came from `U_ints` itself.

1. Exact rational perturbations of every ray \(U_i\times U_j\) produced
   strict witnesses for exactly **22** chambers.
2. Chamber-to-side incidence was computed with integer determinant signs.
3. A scan of all \(2^{20}\) assignments and an independent
   constraint-pruned DFS agreed exactly on **16,570** representatives with
   side zero fixed, hence **33,140** labeled assignments.
4. `facet_lp.build`, seeded with `2026073002` and retried until it returned
   22 chambers, agreed literally with every exact chamber and side label.  It
   succeeded on attempt 1 in the recorded run.

The reference structure, chamber witnesses, incidence, and complete
representative list are in `reference_structure.json`.

A second integer configuration was generated with seed `2026073003` and
used only as a cross-check.  Its own exact chamber construction and its own
sigma enumeration again gave 22, 33,140, and 16,570; 200 systems made only
from that second configuration gave 200 exact certificates.  Nothing from
it is used by the reference theorem.  See
`second_configuration_crosscheck.json`.

## Certificate bundle and counts

`gordan_bundle.json.gz` stores one sparse primitive integer certificate per
system in this order:

```text
for representative bits in ascending order:
    for sigma in (representative, representative xor (2^20 - 1)):
        for k in (1, 2):
            certificate
```

Exact count:

```text
16,570 representatives
x 2 labeled members
x 2 splits
= 66,280 systems and 66,280 certificates
```

No strict feasible system, LP failure, exact-repair failure, or exact
verification failure occurred.  Sparse support sizes were:

| nonzero rows | certificates |
|---:|---:|
| 4 | 36,439 |
| 5 | 6,592 |
| 6 | 3,502 |
| 7 | 6,883 |
| 8 | 8,878 |
| 9 | 3,986 |

The largest primitive integer coefficient is
`300707411051887257600`.  Large coefficients are harmless: the checker uses
unbounded Python integers.

### Remaining split sizes

Swapping the two residual zonotopes sends

\[
(s,T,\sigma)\longmapsto(-s,-T,-\sigma)
\]

and preserves every signed inequality.  Thus the \(k=1,2\) cases give the
\(k=4,3\) cases, respectively; the convention that the plus block is listed
first is only a relabeling of the two blocks.

For \(k=0\) or \(5\), one obtains \(Q=\operatorname{conv}(Z,2Z)\) up to
swapping the copies.  If \(0\in Z\), then \(Z\subseteq2Z\) and \(Q=2Z\), so
there are at most 22 vertices.  If \(0\notin Z\), strict separation gives
one normal direction in which only the inner copy can contribute and the
opposite direction in which only the outer copy can contribute.  Among the
44 candidates \(v,2v\), at least one candidate from each copy is therefore
lost, giving at most 42.  No certificate enumeration is needed for these
extreme splits.

## Stage 2b-1: antipodal-symmetric support

For each of the 16,570 chosen global-flip representatives and each of
\(k=1,2\), I restricted the dual to classes where the two sigma signs agree
and required equal multipliers on their two sides.  This cancels the three
\(T\)-columns identically for every direction configuration.  The remaining
weight dependence was solved and verified exactly for `U_ints`.

| coverage notion | classes | fraction |
|---|---:|---:|
| \(k=1\) covered | 13,506 | 81.508751% |
| \(k=1\) residue | 3,064 | 18.491249% |
| \(k=2\) covered | 10,348 | 62.450211% |
| \(k=2\) residue | 6,222 | 37.549789% |
| covered for both splits | 9,945 | 60.018105% |
| covered for at least one split | 13,909 | 83.940857% |
| covered for neither split | 2,661 | 16.059143% |
| not covered for both splits | 6,625 | 39.981895% |

The exact per-split residue lists and deduplicated pattern certificates are
in `symmetric_coverage.json.gz`.  Every residue pattern also carries an
exact rational strict-primal witness for the restricted system, proving by
Gordan that an equal-pair certificate does not exist there.  The standalone
checker verifies all covered duals, all residue primal witnesses, and that
nonsymmetric classes have zero multiplier.

This **disproves the Stage 2a conjecture of complete symmetry coverage**:
antipodal-symmetric support alone does not cover every class at this fixed
configuration.  Equal-pair support makes \(T\)-cancellation
configuration-independent, but the serialized weight multipliers themselves
are numeric certificates for `U_ints`; this result alone is not a cell-wide
weight certificate.

## Centered slice: \(k=1\)

At \(T=0\), side pairs collapse to ten class signs.  Re-enumeration from the
same reference incidence gives exactly 200 valid class assignments.
`t0_k1_bundle.json.gz` contains **200/200** exact certificates for \(k=1\).

Together with the repaired Stage 2a artifact
`../stage2_gemini/farkas_t0_exact.json` for \(k=2,3\), global flip for
\(k=4\), and the homothetic \(k=0,5\) observation above, this completes all
split sizes for the centered slice of the reference configuration.

## Stage 2c attempt

The 100 classes with largest Stage-1 margins were read from
`../stage1_gpt/margins.json`.  They were not copied by index or mixed with
the reference labels.  A single explicit signed permutation transports the
Stage-1 reference chirotope, every sigma side, and its selected split into
the literal `U_ints` labeling before the symbolic search.

For each mapped system, `symbolic_gp_search.py` enumerates four distinct
facet-normal circuits.  Cofactor multipliers are expanded using

\[
\det(a\times b,c\times d,e\times f)
=\det(c,d,f)\det(a,b,e)-\det(c,d,e)\det(a,b,f).
\]

A candidate is accepted only if every multiplier is coefficientwise
positive and all five positivity slacks are coefficientwise nonnegative as
polynomials in the ten positive \(D_{ijk}\).  This conservative condition
would prove validity throughout the literal reference chirotope cell.

Result: **0/100 succeeded**.  This is an honest failure of the narrow
four-circuit, coefficientwise-sign test.  It does not rule out symbolic
certificates with larger supports or reductions that use
Grassmann--Pluecker relations to compare opposite-sign monomials.  Full
inputs, the signed permutation, mapped splits, and the per-target ledger are
in `symbolic_gp_results.json`.

## Proven / conjectured / failed ledger

### Proven

- Exact fixed-configuration upper bound \(f_0\leq42\) for `U_ints`, with
  arbitrary \(T\), positive weights, every valid labeled sigma, and the
  nontrivial split sizes.
- Exact self-consistent counts: 22 chambers, 33,140 labeled valid sigmas,
  16,570 global-flip classes.
- Exact Gordan coverage: 66,280/66,280 core systems.
- Exact antipodal-support coverage and residues at the counts above.
- Exact centered-slice \(k=1\) coverage: 200/200.

### Still conjectural / out of scope

- The global statement \( \max f_0(3,5)=42 \) over every direction
  configuration.
- Transfer of the numeric fixed-`U_ints` Gordan vectors across an entire
  realization cell.
- Coverage of the antipodal-support residues by a general
  Grassmann--Pluecker family.

### Failed or negative

- No 44-vertex feasible system was found; the mandated discovery stop was
  never triggered.
- Complete antipodal-symmetric support coverage fails: 6,625 classes are
  uncovered for at least one of the two representative splits.
- The conservative Stage 2c symbolic test found 0/100 certificates.

## Reproduction

From the repository root:

```powershell
$PY = 'E:/Projects/sae-identifiability/.venv/Scripts/python.exe'
& $PY ai/maxout/stage2b_gpt/make_stage2b.py
& $PY ai/maxout/stage2b_gpt/symbolic_gp_search.py
& $PY ai/maxout/stage2b_gpt/check_stage2b.py
```

The generator's float LPs provide support hints only.  The final command
uses no NumPy, SciPy, SymPy, or floating-point arithmetic and prints:

```text
PASS: all Stage 2b exact checks completed
```

Recorded full-run seeds:

```text
core support hints / facet_lp cross-check  2026073002
second-configuration cross-check           2026073003
symbolic search ledger                     2026073004
```

Principal artifact SHA-256 hashes at completion:

```text
gordan_bundle.json.gz
  1AA7A4F751C03D86E9F5A82FF46272504A14DB768BD835FACA51FB5FB34C9FC3
reference_structure.json
  EE9A345861F09FB7C28FDB92AB6B7C9F5BD3593EB0D220D5FC6416BC230626A8
t0_k1_bundle.json.gz
  C3FBB772099EC9E67A9DC84B468F1F2A7093200A23E3DB640A4D34C8CA918C3E
symbolic_gp_results.json
  31D26F75B95E9AE7F5A1A8D31F5DEF277B7E8839454D1AD187EAC1683A49410F
second_configuration_crosscheck.json
  C7A0058E4D85C280B650FE030DC80E06D14E5AFEFBDD9CEBC74F420670D0BEF2
```

The symmetric-coverage hash is intentionally omitted here because that
compressed artifact contains elapsed-time metadata and is regenerated by
the secondary-only workflow; its exact contents are independently checked
by `check_stage2b.py`.
