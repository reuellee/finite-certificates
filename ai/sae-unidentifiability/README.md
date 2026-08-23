# An absorbed feature's conditional rate is unidentifiable without labels

`unidentifiability-certificate.md` — `verify_unidentifiability.py` (**49 exact
checks**). A blocking adversarial objection was resolved by the revised Certificate C
construction and exact replay.

Finite certificates that the conditional rate ρ of an absorbed child feature cannot be
recovered from activations alone. The construction culminates in **Certificate C**
(interleaved cones): two dictionaries, both support-irreducible, both strict
hierarchies, both nonnegative, equal sizes, giving ρ = 3/4 versus ρ = 1/2 — which
survives the canonical-selection objection that blocked the first round.

Also included: the coupling identity E[L0]₁ − E[L0]₂ = (ρ₁ − ρ₂)·P(parent), showing
sparsity selection is *biased* rather than identifying; and a boundary map of which
anchors do and do not restore identifiability.

## Verify

```
python3 verify_unidentifiability.py
```

Canonical home is the `sae-identifiability` repo (commit `1cd27e4`); mirrored here.
Part of [finite-certificates](../../README.md).
