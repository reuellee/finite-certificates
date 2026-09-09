# Method source audit

Checked 2026-09-09 against primary documentation and the pinned repository source.

- Macaulay2 Msolve `msolveSaturate`: https://macaulay2.com/doc/Macaulay2/share/doc/Macaulay2/Msolve/html/_msolve__Saturate.html . Documents F4SAT for principal ideal saturation in grevlex over prime fields with characteristic between 2^16 and 2^31. Modular output alone is not a characteristic-zero or real-topology certificate.
- Basu and Karisani, *Computing the homology functor on semi-algebraic maps and diagrams*, arXiv:2207.10497 (submitted 2022): https://arxiv.org/abs/2207.10497 . Supplies algorithms for induced rational homology maps in fixed low degrees for closed bounded semialgebraic sets and zigzag diagrams. This is a theoretical algorithm, not an installed replacement backend or a ready original 9DVL compact-support comparison. True-boundary and relative adaptation remain obligations.
- Stacks Project, *Cones and termwise split sequences*: https://stacks.math.columbia.edu/tag/014D . Standard cochain algebra supports mapping-cone/relative formulations; it does not supply the geometric input.

The existing repository's balanced-end blocks and canonical detector maps remain the original target. No claim of a new general topology algorithm, F4SAT speedup benchmark, or known manageable total dimension is made. Degree 0–2 cochains suffice to test H1 injectivity only after the cochain model and its original-space comparison are certified.
