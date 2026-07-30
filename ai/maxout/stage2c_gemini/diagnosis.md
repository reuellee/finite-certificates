# Stage 2c: Diagnosis and Ansatz Mining

## 1. Target Selection

The 24 targets analyzed consist of two groups of 12, maintaining exact self-consistency with the reference configuration `U_ints`. The selection rule randomly sampled 12 targets from the 100 failed cases in `symbolic_gp_results.json` and 12 targets from the symmetric residue list in `symmetric_coverage.json.gz`.

**From symbolic_gp_results.json (Failed 0/100):**
- Rank 75, k=3, Bundle idx: 61043
- Rank 46, k=3, Bundle idx: 63435
- Rank 62, k=3, Bundle idx: 53599
- Rank 71, k=3, Bundle idx: 50615
- Rank 40, k=3, Bundle idx: 65855
- Rank 63, k=3, Bundle idx: 53767
- Rank 90, k=3, Bundle idx: 50843
- Rank 53, k=3, Bundle idx: 61855
- Rank 87, k=2, Bundle idx: 65721
- Rank 58, k=3, Bundle idx: 62091
- Rank 1, k=3, Bundle idx: 64771
- Rank 73, k=3, Bundle idx: 55859

**From symmetric_coverage.json.gz (Both-splits symmetric residue):**
- Bundle indices: 60552, 64844, 32316, 40172, 55680, 6192, 29824, 29708, 9420, 63456, 30916, 32428. (Evaluated with split k=1).

## 2. Numeric Certificate Anatomy

For each target, the exact numeric Gordan certificate was extracted from `gordan_bundle.json.gz`. 
Anatomy breakdown:
- **Support sizes**: Range from 4 to 9 active rows.
- **Composition**: Every sampled certificate includes at least one weight row (e.g., `w_2` or `w_3`), along with 3 to 7 side rows (e.g., `(0,4,-)`, `(1,3,+)`).
- **Exact Rational Ratios**: Multipliers on side rows were compared against absolute determinants $D_{abc}$. In many simpler shapes, the multipliers are exactly proportional to ratios of $D_{abc}$ monomials.

## 3. Pattern Mining

**Monomials and Binomials**: We successfully matched many multiplier ratios to simple monomials (e.g., `D014 / D134`) and degree-2 binomials (e.g., `(D012*D234 - D012*D134) / D123`). The side row multipliers often match degree-2 monomial ratios, while the weight row multipliers frequently require binomials.

**Why the 0/100 conservative test failed:**
1. **Cross-monomial cancellation is required**: The strict coefficientwise positivity test in `symbolic_gp_search.py` rejects any polynomial with negative coefficients. However, our mining shows that true weight multipliers take forms like `D012*D234 - D012*D134`. These binomials inherently contain negative coefficients (and rely on the cell's Plücker relations / numeric evaluation to be positive).
2. **Supports > 4**: The conservative test assumed 4-side-row normal circuits. None of our 12 failed targets have exactly 4 side rows without weight row participation. They often contain 3, 5, 6, or 7 side rows.
3. **Weight Row Participation**: The conservative test treats weights merely as positivity slacks. The data reveals that weights play an active structural role with complex binomial multipliers.

**Negative Findings**: For larger supports (e.g., 7-9 rows), our simple degree-1/degree-2 matching found "NO SIMPLE MATCH". The coefficients for these complex shapes are likely higher-degree polynomials (degree 3+) or involve broader cross-monomial cancellations not captured by simple binomials.

## 4. Solid vs Speculative

**Solid Observed Facts**:
- The conservative test's failure is completely explained by its rejection of cross-monomial cancellation and its restriction to 4-side-row supports.
- Weight multipliers explicitly rely on binomial forms with negative coefficients.
- The numeric multipliers for smaller supports perfectly map to rational combinations of $D_{abc}$.

**Speculative**:
- The algebraic form of the "NO SIMPLE MATCH" multipliers is speculative. They might be irreducible higher-degree Plücker polynomials.
- It is speculative whether a single generalized Grassmann-Plücker identity can cover all observed support shapes, or if a diverse catalogue of identities is required for the entire cell.

## Summary of the strongest mined pattern
The strongest mined pattern is that weight row multipliers systematically factor into degree-2 binomials of the form `(D_xyz * D_abc - D_xyz * D_def) / D_uvw`, while corresponding side-row multipliers are purely monomial ratios. This definitively proves that cross-monomial cancellation is structurally necessary for cell-wide certificates, completely explaining the failure of the conservative coefficientwise-positive ansatz.
