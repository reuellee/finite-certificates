# Review brief: the capstone claim max f₀(3,5) = 42

You are asked for a maximally skeptical, adversarial review of a
mathematical claim before it is treated as a theorem. Your job is to
find a hole, not to summarize. Assume the authors are competent and the
easy mistakes are gone; look for the subtle ones.

**The claim.** Over all (3,5)-zonoboxtopes (Q = conv(Z^a ∪ Z^b), five
segments in R³), the maximum vertex count is 42 — refuting the odd case
of Conjecture 6.6.1 of arXiv:2509.21286 (which predicts 44) at n = 5,
and the tightness of its Proposition 6.5 at n = 5.

**Primary document:** `CAPSTONE.md` in this directory — the full
argument chain and verification manifest. Context if needed: the master
note `../attack_c66_deficit.md` and the stage documents/reviews it
names.

**Attack surfaces, in priority order:**

1. **The quantifier-reduction chain** (CAPSTONE §3): degenerate/
   support-deficient cases; the claim that the group action preserves
   the polytope; the single-orbit and split-orbit accounting (is one
   representative per stabilizer-orbit of splits really sufficient? is
   the stabilizer computation's group action the right one?); the
   certificate-transport bookkeeping; the flip identity; the final
   Gordan contradiction.
2. **Semantics of the certificates**: does "cell-wide" (polynomial
   multipliers, identities modulo the Grassmann–Plücker ideal given the
   chirotope signs) really imply a valid Gordan certificate at every
   realization of the chirotope? Is strict infeasibility of the
   25-row system really implied, and is strictness the right notion?
3. **The validity enumeration**: does a strict 44-vertex instance
   really force a side pattern σ in the enumerated valid set? Is the
   chamber/side incidence really chirotope-determined?
4. **The parity/perturbation step** (excluding 43 and non-strict 44).
5. **Definition fidelity**: does the object formalized here match the
   zonoboxtopes of arXiv:2509.21286, and the conjecture's odd case at
   (d, n) = (3, 5)? (The repo's formalization reproduces every other
   value the paper reports — 16/26/60/84/104/110 — which bounds but
   does not eliminate mismatch risk.)
6. Anything else you find.

**You may run** the fast checkers named in CAPSTONE §4 (stdlib,
seconds-to-minutes). You are not asked to re-run the sweeps or the full
audit (their outputs are committed; the standalone audit re-verifies
every certificate and reports zero failures).

**Deliverable:** a verdict — ACCEPT / ACCEPT WITH RESERVATIONS /
REJECT — plus a numbered list of defects or doubts, each with severity
(FATAL / SERIOUS / MINOR / NOTE) and the precise location (document
section or file). If you verify a step independently, say which and
how. Do not pad; a short list of sharp items beats coverage prose.
