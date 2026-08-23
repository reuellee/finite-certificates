# Counterexamples to published optimizer convergence claims

`optimizer_counterexamples.md` — two exact verifiers.

- **Muon** — the deployed Newton–Schulz coefficients falsify the coverage claim of
  arXiv:2601.19156, with exact certificates M1–M3 (`verify_muon_ns.py`).
- **Li & Hong (arXiv:2502.02900), Theorem 3.1** — the admissible stepsize set is
  **empty** for β ≥ 1/2, so the theorem is vacuous in that range.
- **Lion** — an exact period-2 cycle (`verify_lion.py`); the refuted claim here was
  informal, and is labelled as such.

## Verify

```
python3 verify_muon_ns.py
python3 verify_lion.py
```

Part of [finite-certificates](../../README.md).
