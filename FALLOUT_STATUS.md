# Jacobian-fallout witnesses: status note

The four fallout verifiers in `jacobian/` were produced by an agent that was
interrupted (session limit) after the constructions passed verification but before it
wrote its summary note (`fallout_harvest.md`). Until that write-up lands, treat the
claims as scoped to exactly what each script constructs and checks:

1. `verify_dixmier_poisson.py` — an explicit polynomial endomorphism φ of the
   polynomial Poisson algebra on C⁶ (standard symplectic bracket, coordinates
   x₁..x₃, d₁..d₃) with: bracket relations [φ(dᵢ),φ(xⱼ)] = δᵢⱼ and [φ(dᵢ),φ(dⱼ)] = 0
   verified symbolically; det Jac ≡ 1; three distinct rational points of C⁶ with a
   common image. Non-injective ⇒ not an automorphism. The precise implication chain to
   the Poisson/Kontsevich conjecture (which conjecture text, whose statement, which n)
   is NOT yet documented here and must be nailed down before any external claim.
2. `verify_deg3_keller.py` — explicit degree-3 Keller map verified non-injective
   (collision exhibited), det Jac constant. Dimension and reduction chain (Bass–
   Connell–Wright / Yagzhev) to be documented.
3. `verify_cubic_homogeneous.py` — dimension-55 map x + N(x), N cubic homogeneous,
   J(N) nilpotent (J^64 = 0 verified), det Jac ≡ 1, non-injectivity via the underlying
   construction. To be documented.
4. `verify_druzkowski.py` — explicit Drużkowski form xᵢ + (Ax)ᵢ³ with collision.
   Dimension and A's rank to be documented.

Also verified but NOT imported: nothing else. The arXiv-duplication check for these
witnesses (were they posted by others in the 5 days since 2026-07-20?) was part of the
interrupted agent's brief and has NOT been completed — required before publication.

TODO (next session / after limit reset): resume the fallout agent to (a) write
fallout_harvest.md with exact statements, implication directions with citations, and
dimensions; (b) run the arXiv duplication sweep; (c) Gemini review.
