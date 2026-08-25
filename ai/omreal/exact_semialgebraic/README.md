# Exact semialgebraic certificate toolkit

This small standard-library-only package extracts the proof primitives used by
the exact 2D and 3D research certificates in `ai/omreal`:

- sparse rational-polynomial arithmetic and affine pullback;
- canonical primitive-integer normalization and semantic digests;
- tensor-product Bernstein conversion and exact midpoint subdivision;
- arbitrary-dimensional simplex Bernstein conversion and deterministic
  longest-edge simplex bisection;
- fail-closed zero-set classification on rational boxes;
- fail-closed simultaneous-equation exclusion; and
- adaptive derivative-axis critical-system exclusion.

The package is a **producer-side library**, not an independent verifier.
Load-bearing certificates must still be replayed by code that does not import
this implementation.  Discovery may use numerical methods, but every function
here consumes and returns exact integer/rational data.  Reaching a subdivision
budget reports `UNRESOLVED`; it never turns absence of a certificate into a
mathematical claim.

`verify_exact_semialgebraic_toolkit.py` checks analytic positive and negative
canaries in two and three dimensions on both boxes and simplices.  In
particular, it requires the critical-system method to exclude a noncompact
hyperboloid-like zero set and both certificate languages to refuse false
emptiness claims for interior spheres, whose compact components are
intentional hostile examples.
