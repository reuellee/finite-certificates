# Sturmfels et al. Conjecture 6.6: max f₀(3,5) = 42 (the odd case refuted at n=5); (4,6) resolved; (3,8) achievability confirmed

Conjecture 6.6 of **Balakin, Cox, Loho & Sturmfels, "Maxout Polytopes"**
([arXiv:2509.21286](https://arxiv.org/abs/2509.21286), Sept 2025) claims maximal
vertex counts for (d,n,1)-maxout polytopes (zonoboxtopes).

## Headline result — THEOREM: max f₀(3,5) = 42

**[`capstone/CAPSTONE.md`](capstone/CAPSTONE.md)** — over all
(3,5)-zonoboxtopes (and, more generally, zonoboxtope *candidates*) the
maximum vertex number is exactly 42. Hence the tightness assertion of the
paper's Proposition 6.5 fails at n = 5, and the odd case of Conjecture 6.6.1
fails at its first instance beyond n = 3: the conjectured value 44 is not
attained.

The upper bound is carried by **132,560 exact cell-wide Gordan certificates**
covering every valid side pattern at every split-orbit representative, plus a
symmetry reduction to a single oriented-matroid cell. Verify it — the primary
check imports nothing from the programs that generated the library and uses
only the Python standard library:

```
python check_om35_uniqueness.py            # seconds — 384 chirotopes, one orbit
python capstone/check_split_orbits.py      # seconds — stabilizer + split orbits
python capstone/independent_audit.py       # ~2 min  — all 132,560 certificates
python capstone/check_transport.py         # ~2 min  — certificate transport
```

A write-up is in [`paper/`](paper/) (submission-ready note + ancillary
bundle). The three adversarial reviews behind it are in `capstone/` and
`paper/`.

Two earlier attacks, which the capstone grew out of, live here as well.

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
| (3,5) | **42** | 44 | conjectured value **not reproduced** — and now **proven unattainable**: see the capstone theorem above, which supersedes this row |
| (4,5) | **58** | 60 | same resistance (while neighboring (4,6) falls in minutes) |
| (3,7) | **84** | 88 | same resistance (survives 8 drops from the exact (3,8) extremal) |

The empirical dichotomy — every even-n / n=d case attained instantly, every odd
n > d case stuck exactly 2⌈(n−d)/2⌉ short — is documented with methods,
validation ladder, a falsified intermediate hypothesis, and honesty scoping in
`attack_c66_deficit.md`.

**Scope of that table, stated exactly.** Those five entries certify the vertex
count of five *particular* instances. At (4,5) and (3,7) they are therefore
**lower bounds** — 58 and 84 are attained; whether the true maxima are below
the conjectured 60 and 88 is open, and nothing there is refuted. Only (3,5)
has since been settled in both directions, by the capstone theorem above.

`target_list.md` is a ranked harvest of further ML-theory conjectures attackable
by finite certificate.

## Verify

```
python3 verify_maxout66_d4n4.py
python3 verify_c66_new_cases.py
```

Part of [finite-certificates](../../README.md).
