# Sturmfels et al. Conjecture 6.6: two new cases confirmed, three odd-n cases resist

Conjecture 6.6 of **Balakin, Cox, Loho & Sturmfels, "Maxout Polytopes"**
([arXiv:2509.21286](https://arxiv.org/abs/2509.21286), Sept 2025) claims maximal
vertex counts for (d,n,1)-maxout polytopes (zonoboxtopes). Two attacks live here.

**Attack 1 (2026-07-25)** — `attack_maxout66.md`, `verify_maxout66_d4n4.py`,
`cert_d4n4.json`: resolves the smallest open case **(4,4) = 32 vertices** with a
fully exact rational certificate (the conjectured maximum is the absolute cap
there, so the case closes completely).

**Attack 2 (2026-07-30)** — `attack_c66_deficit.md`, `verify_c66_new_cases.py`,
`cert_*.json`: five exactly-pinned instances (each candidate point carries either
a strict witness direction or an explicit rational convex combination, so the
vertex counts are equalities, not just bounds):

| (d,n) | certified f0 | conjectured max | meaning |
|---|---|---|---|
| (4,6) | **104** | 104 (= cap) | part 2 case **confirmed** (first with n > d) |
| (3,8) | **110** | 110 (< cap 116) | even-n formula's **achievability confirmed** beyond the paper's DFS range |
| (3,5) | **42** | 44 | conjectured value **not reproduced** — incl. the paper's own claimed-successful sampling recipe at 15× its budget, ~300 complete-per-direction-set searches, generator-drop seeding |
| (4,5) | **58** | 60 | same resistance (while neighboring (4,6) falls in minutes) |
| (3,7) | **84** | 88 | same resistance (survives 8 drops from the exact (3,8) extremal) |

The empirical dichotomy — every even-n / n=d case attained instantly, every odd
n > d case stuck exactly 2⌈(n−d)/2⌉ short — is documented with methods,
validation ladder, a falsified intermediate hypothesis, and honesty scoping in
`attack_c66_deficit.md`. Nothing is refuted; the odd-n certificates are lower
bounds, and the note states what an authors' counterexample-to-our-resistance
would look like.

`target_list.md` is a ranked harvest of further ML-theory conjectures attackable
by finite certificate.

## Verify

```
python3 verify_maxout66_d4n4.py
python3 verify_c66_new_cases.py
```

Part of [finite-certificates](../../README.md).
