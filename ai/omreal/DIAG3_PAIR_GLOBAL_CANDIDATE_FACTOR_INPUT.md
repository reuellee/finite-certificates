# Diagonal three: pinned row-2599 candidate-factor input

## Result

The first proof-critical input gap for the global master-cell generator is
closed.  The exact sorted list of the `17,824` row-2599 residual factors not
certified empty is now stored in

```text
data/DIAG3_PAIR_GLOBAL_row2599_candidate_factors.bin
```

The artifact is 71,316 bytes with SHA-256

```text
adb2e7257457f158e809450683c46fe7ecafdbdd4a7efdf9ac630e8a4f0fb03f.
```

Its header pins parent `2599`, the complete `26,740`-factor universe, and the
`17,824` candidate count.  The payload is the strictly increasing sequence
of zero-based 32-bit factor IDs.

## Two independent constructions

The export path in `verify_diag9_parent_ranking.py` uses invariant bracket
formulas and bitsets for all 2,604 realizable catalog parents.  It selects
the complement of the row-2599 conflict bits and writes the binary artifact.

The independent verifier does not reuse those bitset evaluations.  It reads
the stored row-2599 integer realization, constructs all 84,840 transported
circuit certificates, and evaluates the required determinants directly.
Exactly 27,944 conflicting occurrences certify 8,916 empty primitive-factor
walls.  Their complement agrees with all 17,824 stored IDs entry for entry.

"Candidate" is intentionally conservative: the absence of a circuit
conflict does not prove that a factor wall is nonempty.  The artifact is a
proof-safe input universe for a later cell generator, not a wall-existence
claim.

## Replay

```bash
PYTHONDONTWRITEBYTECODE=1 python \
  ai/omreal/verify_diag9_parent_ranking.py \
  --export-row2599 \
  ai/omreal/data/DIAG3_PAIR_GLOBAL_row2599_candidate_factors.bin

PYTHONDONTWRITEBYTECODE=1 python \
  ai/omreal/verify_diag3_pair_global_candidate_factors.py
```

The next missing generator block is now singular: choose and pin the finite
projective/reciprocal compactification chart atlas, including exact overlap
coverage and genuine infinity faces.  Only after that should the 17,824
candidate polynomials be passed to a deterministic regular-cell generator.
