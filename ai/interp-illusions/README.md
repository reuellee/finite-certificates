# Four exact minimal networks on which standard interpretability methods lie

`certificates.md` — four verifiers. Gemini adversarial review: VERIFIED-SOUND.

Each is a smallest-known explicit network on which a widely used interpretability
method returns a confidently wrong answer:

- **Activation patching** — a 6-parameter network where patching reports the wrong
  causal component (`verify_activation_patching.py`)
- **Gradient attribution** — an 18-parameter network where both grad×input and
  integrated gradients assign exactly zero to the genuinely causal feature
  (`verify_gradient_attribution.py`)
- **SAE circuit analysis** — a loss-optimal *absorbed* SAE that yields the wrong
  circuit, established via KKT (`verify_sae_circuit.py`)
- **Probing** — a probe that passes the Hewitt–Liang control task while being causally
  inert (`verify_probing.py`)

## Verify

```
python3 verify_activation_patching.py
python3 verify_gradient_attribution.py
python3 verify_probing.py
python3 verify_sae_circuit.py      # slow (~3-5 min)
```

Part of [finite-certificates](../../README.md).
