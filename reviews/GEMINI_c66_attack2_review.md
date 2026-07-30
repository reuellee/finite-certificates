# Gemini referee review — Conjecture 6.6 attack 2 (2026-07-30)

*Gemini 3.x via agy --print; prompt asked for soundness / overclaim / formula / fairness audit at the VERIFIED-SOUND bar.*

# Audit Review

Here is the full evaluation of the provided files against your criteria, ranked by the severity of the potential risk each category represents to the mathematical and academic validity of the work.

### 1. Verifier Soundness (Severity: CRITICAL — PASS)
**Criteria:** Does the logic pin the exact vertex count of $conv(Z^a \cup Z^b)$?
**Analysis:** The mathematical logic is perfectly sound. It relies on the geometric fact that the extreme points (vertices) of the convex hull of a union of sets must be a subset of the union of their extreme points. Since $Z^a$ and $Z^b$ are zonotopes, their vertices are a subset of their respective $2^n$ sign points. Thus, the combined $2^{n+1}$ sign points form a complete candidate set containing all possible vertices of $Q = conv(Z^a \cup Z^b)$.
The verifier script `verify_c66_new_cases.py` strictly checks that:
1. All candidate points are pairwise distinct.
2. Every claimed vertex has a strictly separating hyperplane (an exact witness direction $c$ where $c \cdot p > c \cdot q$ for all other candidates $q$). This proves the point is an extreme point of the candidate set, and therefore an extreme point of $Q$.
3. Every remaining candidate is exactly reproducible via a convex combination of *other* candidates (coefficients $\ge 0$, summing to 1). This proves they are strictly *not* vertices.

Because the candidate set covers the entire space of possible vertices, the candidates are partitioned exactly, and the checks run in standard library `Fraction` arithmetic, the vertex count of $Q$ is rigorously pinned with zero floating-point vulnerabilities.

### 2. Overclaims & Epistemological Boundaries (Severity: HIGH — PASS)
**Criteria:** Are the limits of the findings properly scoped without overclaiming?
**Analysis:** The text displays excellent scientific discipline regarding what is proven versus what remains conjectural.
- **(4,6) resolved-modulo-cap:** The text explicitly notes "Modulo the classical zonotope vertex bound... the case (4,6) is fully resolved." This is consistent and mathematically appropriate, separating the existence of the 104-vertex extremal instance from the theoretical upper-bound constraint.
- **(3,8) achievability vs. resolution:** The distinction is maintained flawlessly. The text explicitly states this "confirms the achievability half" and correctly points out that since the confirmed value (110) is less than the theoretical cap (116), "the upper-bound half remains conjectural." 
- **Odd-$n$ refutation language:** The author scrupulously avoids claiming a refutation of the conjecture for odd $n$. Sections explicitly state "the three odd-$n$ certificates are lower bounds only" and "Conjecture 6.6 is not refuted anywhere in this note." The resistance is safely classified as an empirical observation.

### 3. Formula Arithmetic (Severity: MEDIUM — PASS)
**Criteria:** Check the correctness of the stated combinatorial bounds.
**Analysis:** All stated values for the cap bounds are mathematically correct based on the formula $cap(d,n) = 4 \sum_{k=0}^{d-1} \binom{n-1}{k}$:
- **(3,5):** $4 \times (\binom{4}{0} + \binom{4}{1} + \binom{4}{2}) = 4 \times (1 + 4 + 6) = 44$.
- **(4,5):** $4 \times (\binom{4}{0} + \binom{4}{1} + \binom{4}{2} + \binom{4}{3}) = 4 \times (1 + 4 + 6 + 4) = 60$.
- **(4,6):** $4 \times (\binom{5}{0} + \binom{5}{1} + \binom{5}{2} + \binom{5}{3}) = 4 \times (1 + 5 + 10 + 10) = 104$.
- **(3,7):** $4 \times (\binom{6}{0} + \binom{6}{1} + \binom{6}{2}) = 4 \times (1 + 6 + 15) = 88$.
- **(3,8):** $4 \times (\binom{7}{0} + \binom{7}{1} + \binom{7}{2}) = 4 \times (1 + 7 + 21) = 116$.
- **(3,8) Deficit Calculation:** The deficit formula computation is $116 - 6 = 110$, exactly matching the reported achievability value. All numbers in the text strictly align.

### 4. Tone and Fairness of Prop 6.5 Tension (Severity: LOW — PASS)
**Criteria:** Is the paragraph regarding Prop 6.5 fair?
**Analysis:** The paragraph is a model of constructive academic discourse. It directly quotes the paper ("using only 1000 samples..."), contrasts it clearly with the author's extensive reproduction attempts (15x budget + other exhaustive searches), and provides three highly plausible, benign explanations for the discrepancy without accusing the authors of malpractice:
1. A thin extremal region hit by luck.
2. Float-hull overcounts (near-duplicate vertices) in the original authors' verification.
3. A subtle definitional mismatch.

It properly acknowledges the lack of published data/code from the original authors and clearly defines the falsifiability of its own stance ("An explicit certified 44-vertex... would settle this immediately"). It is firm but undeniably fair.

VERIFIED-SOUND
