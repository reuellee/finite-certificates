# Max-settings referee review — Gemini 3.1 Pro (High), second deep pass (2026-07-30)

I have completed a rigorous audit of the supplied certificates, verification logic, search methodology, and mathematical reductions. 

Here is the full severity-ranked review:

### P1: Certificate-Logic and Verification Holes (None Found -> ALL CLEAR)
- **Degenerate $a_i=0$ coefficients**: Implicitly forbidden and mathematically handled. The verifier checks `len(set(pts)) == 2**(n+1)`. If any generator coefficient were zero, the $\pm$ sign variations for that dimension would yield identical spatial coordinates, collapsing the set size and instantly failing the distinctness check. Thus, all generators must be strictly non-degenerate.
- **Misuse of $\text{vert}(\text{conv}(A \cup B))$ in $\text{vert}(A) \cup \text{vert}(B)$**: Handled flawlessly. Because any zonotope's vertices are a subset of its sign points, the true vertices of the convex hull of the union must be a subset of the combined $2^{n+1}$ candidate sign points. Proving that exactly $f_0$ of these are extreme points (via strict witnesses) and the rest are strictly internal (via convex combinations) is a mathematically complete proof of the exact vertex count.
- **Witness ties**: The verifier enforces strict separation: `sum(...) >= vi` triggers a failure, meaning $c \cdot q < c \cdot v_i$ for all $q \neq v_i$. This strict inequality ensures no coplanar/collinear degeneracies are falsely counted as multiple vertices.
- **Combo self-reference / Cycles**: The script asserts `j != i` for all combo parts. Being a convex combination of *other* valid candidates guarantees a point lies strictly within the convex hull. Cycles (e.g., A is a combo of B, and B is a combo of A) do not invalidate this, as they simply mean multiple points lie on the same face (and thus none of them are extreme points).
- **Note-vs-Verifier gaps & Arithmetic**: The instances match the note's claims perfectly. All arithmetic uses `fractions.Fraction`, neutralizing any floating-point/Qhull inaccuracies. 

### P2: Search Methodology and Completeness (Robust)
- **T-reduction Derivation**: 100% correct. The boundary between seeing $Z^a$ vs $Z^b$ is defined by $h_{Z^a}(r) - h_{Z^b}(r) = 0$. Using the paper's generator split ($k$ and $n-k$), this expands to $r \cdot (\sum_A \alpha_i m_i - \sum_B \beta_j m_j) + \sum_A \alpha_i |r \cdot u_i| - \sum_B \beta_j |r \cdot u_j|$. The midpoints only ever appear in the first term, rigorously proving they reduce to a single 3D translation vector $T$. The claim that the centered family ($T=0$) is structurally deficient is accurate because it forces $s_\epsilon = w_\epsilon$, permanently locking antipodal facet colors together and preventing them from independently avoiding the forbidden cones. 
- **`facet_lp.py` Completeness-per-U Honesty**:
  - **Sampled chamber enumeration**: The code protects against missing chambers by asserting `len(chambers) == 2 * (1 + (n - 1) + (n - 1) * (n - 2) // 2)`. This equals $n^2 - n + 2$, which is the exact theoretical maximum number of chambers for a generic arrangement of $n$ central planes in 3D. If any chamber were missed, the length check would fail.
  - **LP margin delta**: The $\delta = 10^{-3}$ margin means the search is complete *up to that margin*; extremely narrow extreme configurations could technically slip through, but this is an acknowledged standard bound. 
  - **Antipodal side independence**: Mathematically accurate. With $T \neq 0$, the signs $r \cdot T + r \cdot w_\epsilon$ and $-r \cdot T + r \cdot w_{-\epsilon} = -r \cdot T - r \cdot w_\epsilon$ are linearly independent constraints.

### P3: Steelmanning the Authors (The Prop 6.5 Tension)
The note suggests three explanations for why the authors' 1000-sample recipe claimed 44 vertices at (3,5) while the exact reproduction stalled at 42 (thin extremal region, float-hull overcount, definitional mismatch). Here are **three unconsidered explanations** to add to the steelman:
1. **Analytical Ghost Claim (Typo)**: The authors may have verified $n=3, 4, 6$ empirically, discovered the theoretical formula, and broadly wrote "using only 1000 samples... this method succeeds" for the entire DFS range (up to $n \le 6$) without explicitly confirming $n=5$ in their logs. 
2. **Specialized Distribution Bias**: The paper's unspecified random sampling might not have used isotropic Gaussians. If they initialized with integer coordinates, a stratified hypercube, or grid-aligned generators, their distribution might inherently heavily favor structured, incommensurate fans that easily hit the cap.
3. **Qhull Degeneracy Bug**: If the authors used a floating-point convex hull library (like SciPy's `ConvexHull` / Qhull), rounding errors on near-degenerate flat regions could easily cause Qhull to triangulate a single flat face into multiple simplices, falsely reporting coplanar points as independent extreme vertices (falsely inflating a 42 to a 44).

VERIFIED-SOUND
