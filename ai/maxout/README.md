# Smallest open case of Sturmfels et al. Conjecture 6.6, resolved

`attack_maxout66.md` — `verify_maxout66_d4n4.py` with `cert_d4n4.json`.

Conjecture 6.6(2) of **Balakin, Cox, Loho & Sturmfels, "Maxout Polytopes"**
([arXiv:2509.21286](https://arxiv.org/abs/2509.21286), Sept 2025) claims a maximum
vertex count for (d,n,1)-maxout polytopes and had **never been computationally verified
for any d ≥ 4** — the paper's own evidence was random sampling at d = 3, n ≤ 6.

This confirms the smallest open case, **(d,n) = (4,4)**, by exhibiting a 32-vertex
instance with a fully exact rational certificate: explicit generators plus a per-vertex
rational witness direction, checkable with `Fraction` arithmetic alone. A d = 3 sanity
check reproducing their published 16/26/44/60 pins the formalisation before any claim
is made.

**Not resolved:** part (1) at n = 8 (the refutation target). Randomised hill-climbing
reached only 92 vertices against the 110 the conjecture allows, which is no evidence
either way — extremal configurations at n ≥ 7 appear to need structured constructions.
`attack_maxout66.md` records the diagnosis and what a future attack should do
differently.

`target_list.md` is a ranked harvest of further ML-theory conjectures attackable by
finite certificate, scored by search-boundedness, verification cheapness, and
consequence.

## Verify

```
python3 verify_maxout66_d4n4.py
```

Part of [finite-certificates](../../README.md).
