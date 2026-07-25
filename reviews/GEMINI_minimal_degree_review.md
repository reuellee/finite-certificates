# ADVERSARIAL REVIEW REPORT
**Date:** 2026-07-25  
**Reviewer:** Adversarial Peer Reviewer in Affine Algebraic Geometry  
**Verdict:** **VERIFIED-SOUND** (with precisely delineated boundaries highlighted as the weakest links)

---

## Overview

This review rigorously assesses the mathematical claims, algebraic derivations, and completeness of the draft note. Every symbolic identity, factorization, and classification branch was verified against the companion scripts (`verify_original.py`, `verify_mechanism_lower_bound.py`, and `verify_composition_obstruction.py`). All companion verifiers run in exact arithmetic and pass. 

The note is **mathematically sound and highly polished**. The proofs of both **Theorem A** and **Theorem B** are correct as stated, and the "Honest scope" section is exemplary in its precision.

---

## Detailed Attack Area Analysis

### (i) Theorem A’s $\mu(F) = 1$ Step (Birational Keller Maps)
* **Verdict:** **VERIFIED-SOUND (Airtight)**
* **Analysis:** Let $F: \mathbb{C}^n \to \mathbb{C}^n$ be a birational Keller map ($\mu(F) = 1$). Since $F$ is a Keller map, it is étale (everywhere local biholomorphism, hence quasi-finite). Since the target $\mathbb{C}^n$ is smooth, it is normal.
  1. By **Zariski's Main Theorem (ZMT)**, any quasi-finite birational morphism to a normal variety is an open immersion. Thus, $F$ is an isomorphism of varieties from $\mathbb{C}^n$ onto its image $U = F(\mathbb{C}^n)$.
  2. Because $\mathbb{C}^n$ is affine and $U \cong \mathbb{C}^n$, the open subvariety $U \subset \mathbb{C}^n$ is itself an *affine* variety.
  3. A classical algebraic geometry result (Nagata/Hartshorne Ex. II.3.12) states that **the complement of any open affine subvariety in a normal affine variety is of pure codimension 1** (if non-empty). Thus, if $U \subsetneq \mathbb{C}^n$, then $\mathbb{C}^n \setminus U$ must contain an irreducible hypersurface.
  4. However, Prop 2.1 of Alpöge (and general Keller theory) establishes that the complement of the image of a Keller map has **codimension $\ge 2$**.
  5. The only way to resolve this contradiction is for the complement to be empty. Thus, $U = \mathbb{C}^n$, and $F$ is a surjective, bijective polynomial map, hence a **polynomial automorphism**.
  This step is completely rigorous and matches the classical result of Bass–Connell–Wright (1982).

### (ii) Theorem B’s Completeness & Syzygy Parametrization
* **Verdict:** **VERIFIED-SOUND (Exhaustive)**
* **Analysis:** The note claims that any binary-cubic incidence identity $C_0 x^3 + C_1 x^2 A + C_2 x A^2 + C_3 A^3 \equiv 0$ over a unimodular row $(x, A)$ with $A = 1+xG$ is uniquely parametrized by:
  $$(C_0, C_1, C_2, C_3) = (f_1 A,\, f_2 A - f_1 x,\, f_3 A - f_2 x,\, -f_3 x)$$
  This is indeed mathematically exhaustive. Because $A = 1+xG$, the polynomials $x$ and $A$ are coprime in $\mathbb{C}[x,y,z]$, and thus their powers are coprime.
  * **Proof of Exhaustion:** We can rewrite the identity as:
    $$x^2 (C_0 x + C_1 A) + A^2 (C_2 x + C_3 A) = 0$$
    Coprimality of $x^2$ and $A^2$ forces $A^2 \mid (C_0 x + C_1 A)$, so $C_0 x + C_1 A = A^2 f_2$ for some $f_2 \in \mathbb{C}[x,y,z]$.
    Rearranging, $x C_0 = A(A f_2 - C_1)$. Coprimality of $x$ and $A$ forces $A \mid C_0$, so $C_0 = f_1 A$.
    Substituting this back gives $C_1 = f_2 A - f_1 x$.
    By symmetry, we obtain $C_2 x + C_3 A = -x^2 f_2 \implies C_3 = -f_3 x$ and $C_2 = f_3 A - f_2 x$.
  This proves the syzygy module is free and generated exactly by the three Koszul relations. The classification is complete. Furthermore, the note's definition of "z-linear mechanism map" is precise, and the target-affine postcomposition argument is rigorous.

### (iii) Det Jac Factorization and $G_0 = 2$ Forcing
* **Verdict:** **VERIFIED-SOUND (Airtight)**
* **Analysis:** The determinant factorization $\det \text{Jac} = -E_0 G_0 + c_1 z - x G_2 E_2 z^2$ is correct.
  1. For a Keller map, $\det \text{Jac}$ is a nonzero constant $\lambda \in \mathbb{C}^\times$, forcing the $z^0$ coefficient $-E_0 G_0 = \lambda$. Since $\mathbb{C}[x,y]$ is a domain, both $E_0$ and $G_0$ must be constant.
  2. Evaluating $G_0 = 2xw_0A^2 + 2(2xG+1)A + x^2u$ at $x=0$ yields exactly $2$ (since $A|_{x=0} = 1$). Since $G_0$ is constant, it is identically $2$.
  3. For $A = 1+xy$ (where $G = y$), solving $G_0 \equiv 2$ modulo $x$ forces $w_0 \equiv -3y \pmod x$, yielding the unique parametrization:
     $$w_0 = -3y + x\hat{w},\quad u = 8y^2 + 6xy^3 - 2\hat{w}A^2$$
  4. The degree caps $\deg(P) \le 6 \implies \deg(u) \le 4$ and $\deg(Q) \le 6 \implies \deg(w_0) \le 2$. Since $A^2$ has degree 4, any non-constant $\hat{w}$ would force $\deg(u) \ge \deg(\hat{w}) + 4 \ge 5$ (no top-term cancellation is possible due to $x^2 y^2$ divisibility of $A^2$'s top term), which violates the cap $\deg u \le 4$. Thus, $\hat{w} = k \in \mathbb{C}$ is strictly constant.

### (iv) Endgame Determinants & Other Rows
* **Verdict:** **VERIFIED-SOUND (Airtight)**
* **Analysis:**
  * **Pattern II:** The $z^0$ coefficient of $\det \text{Jac}$ factors as $-\hat{G}_0 \cdot \hat{E}_0$ with $\hat{G}_0 = u_3 A^2 + 2x^2 w_0 A + 2x(2xG+1)$. Keller forces $\hat{G}_0 \equiv g \in \mathbb{C}^\times$. But modulo $A$ (where $xG \equiv -1$), this reduces to $g \equiv -2x \pmod A$, meaning $A$ must divide $g+2x$. Since $\deg A \ge 2$, a degree-wise contradiction ensues immediately. Pattern II is dead for all rows of degree $\ge 2$.
  * **$x$-only rows of high degree:** The $z^0$ coefficient of $\det \text{Jac}$ contains the factor $x^2 G'(x) - 1$. For this to be constant, we must have $G' \equiv 0$, so $\deg A \le 1$.
  * **$x$-only rows of degree 1 ($A = 1+x$):** The endgame determinants $\gamma \mu (\gamma x z + 2)$ and $2 \kappa \mu (\kappa z (1+x) + 1)$ are explicitly $z$-dependent and can never be nonzero constants. Thus, no $z$-linear Keller maps exist for $x$-only rows.

### (v) Proposition 3’s Semigroup/Parity Argument
* **Verdict:** **VERIFIED-SOUND (Airtight)**
* **Analysis:** The top forms of $P, Q, R$ are $t_P = x^3 y^3 z$ (deg 7), $t_Q = 3x^3 y^2 z$ (deg 6), and $t_R = -x^3 z$ (deg 4).
  1. The top form of $Q^a R^b$ is $3^a (-1)^b x^{3a+3b} y^{2a} z^{a+b}$ of degree $6a+4b$.
  2. Since we can uniquely reconstruct $(a, b)$ from the exponents (as $a = \deg_y / 2$ and $b = \deg_z - a$), these monomials are pairwise distinct for different $(a,b)$.
  3. This uniqueness ensures that **no cancellation can occur in the top-degree terms of $h(Q, R)$**, so the degree of any $h(Q, R)$ is exactly the maximum of the even numbers $6a+4b$.
  4. Since $\deg P = 7$ is odd, no term of $h(Q, R)$ can cancel the top form of $P$. Thus, $\deg(P - h(Q, R)) = \max(\deg P, \deg h(Q,R)) \ge 7$.
  5. The degree equations $7a + 4b = 6$ and $7a + 6b = 4$ have no non-negative integer solutions. Thus, single elementary postcompositions cannot reduce any component degree.

---

## The Weakest Links (Delineating the Search Boundaries)

While the mathematical proofs in the note are completely sound, the overall "minimality" claim of the note rests on the boundaries of its searched/proved scope. The weakest links—where a degree $\le 6$ counterexample might still hide—are:

1. **Proposition 3 (Precomposition Degree Cap):** The elementary precompositions in $x$ and $y$ are only exhaustively searched up to degree 3. It remains open whether a precomposition of degree $\ge 4$ can lower the component degrees of $F$ below 7.
2. **Theorem B (Genuinely Affine-Dependent Slots):** The note assumes a "constant slot" (e.g., $C_2 = 2$). The genuinely affine-dependent slot family—where all four coefficients $C_i$ are non-constant but satisfy a linear relation $\alpha P + \beta Q + \gamma R + \delta C_3 = c$ with $\delta \neq 0$—is not covered. This is the most promising unsearched algebraic pocket for a lower-degree map.
3. **Theorem B (Rows with both entries of degree $\ge 2$):** Unimodular rows like $(x^2, 1+x^2 y)$ cannot be normalized to the $(x, 1+xG)$ form by affine coordinates and are excluded from the classification.
