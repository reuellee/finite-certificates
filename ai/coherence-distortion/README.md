# Coherence penalties provably distort the features they are meant to fix

`overcomplete_coherence.md` — `verify_overcomplete_coherence.py`.

At λ = 1/5, β = 1/16, an explicit rational **5-12-13 frame strictly beats every 3-atom
dictionary containing the true features** under the Gram penalty. The class-wide
faithful objective is exactly 19/100 + β by a one-line KKT argument, and the Gram term
is 1 for any faithful triple.

Includes a mutual-coherence twin, a near-onset witness against the analytic threshold
λ(2−λ)/16, and a **β = 0 control** proving the distortion is remedy-induced rather than
present in the base objective. A later addendum separates frame potential from mutual
coherence via the signed basis [I, −I], checked exactly for d = 2..8.

## Verify

```
python3 verify_overcomplete_coherence.py
```

Part of [finite-certificates](../../README.md).
