# Aftermath of the Jacobian Conjecture counterexample

Consequences and boundaries of Alpöge's 2026-07-20 counterexample to the Jacobian
Conjecture, each decided by an explicit witness with a cheap independent verifier.

## What is here

**The n = 2 boundary** (`n2_analysis.md`, `verify_n2.py`). No Keller map of generic
degree 2 exists in **any** dimension — the quadratic case of Campbell (1973), with a
short proof. Gemini adversarial review: VERIFIED-SOUND. A counterexample at n = 2 would
need generic degree μ ≥ 5 and degree > 100. A new checkable statement: a degree-4
Keller map forces Galois closure S₄ or A₄.

**Fallout witnesses** (`fallout_harvest.md`). Explicit maps settling downstream
conjectures: a Poisson-bracket-preserving non-injective endomorphism refuting **PC₃**
(self-contained); **Dixmier DC₃** via DC_n ⟹ JC_n; an explicit degree-3 Keller
non-automorphism; a dim-55 cubic-homogeneous witness; and a **dim-368 Drużkowski**
form, which appears to be the first explicit one. Mathieu and cubic-homogeneous were
found already scooped (arXiv:2607.19012, Thompson 24-var) and are labelled so.
Kontsevich is **unaffected** — it concerns automorphism groups, not endomorphisms.

**Minimal-degree theorems** (`minimal_degree_hunt.md`). Theorem A: μ = 3 is minimal in
every dimension ≥ 3. Theorem B: no counterexample of max component degree ≤ 6 exists in
the full z-linear cubic-mechanism class, where (7,6,4) is minimal. Open conjecture,
stated with a route: **no Keller non-automorphism of ℂ³ has max component degree ≤ 4.**

## Verify

```
python3 verify_n2.py                     # the n=2 theorem
python3 verify_dixmier_poisson.py        # PC3 / Dixmier witnesses
python3 verify_deg3_keller.py
python3 verify_cubic_homogeneous.py
python3 verify_mechanism_lower_bound.py  # Theorems A/B
python3 verify_druzkowski.py             # slow (~5-8 min)
```

The third-party preprint is linked rather than vendored. Part of
[finite-certificates](../README.md).
