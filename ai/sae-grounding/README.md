# Internal causal relevance does not identify a semantic causal ontology

`intervention_grounding_gap.md` — `verify_intervention_grounding.py` (**31 exact
checks**). Gemini adversarial review: VERIFIED-SOUND.

An exact theorem: two structural causal models with fixed named concepts, identical
labels, and the same invertible activation produce **identical transcript distributions
under ANY adaptive internal-intervention protocol** — yet have different semantic
do-distributions. No amount of poking at internals distinguishes them.

Includes a swap-symmetric witness that defeats any equivariant selection rule, and a
corollary at the SAE absorption wall. `REVIEW.md` documents the full referee pass; the
note's originally cited verifier did not exist and was reconstructed here.

## Verify

```
python3 verify_intervention_grounding.py
```

Part of [finite-certificates](../../README.md).
