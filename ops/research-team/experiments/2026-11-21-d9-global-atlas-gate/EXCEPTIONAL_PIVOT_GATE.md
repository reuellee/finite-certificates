# D9 exact residual-wall elimination and exceptional pivot gate

**Partial result; STOP / INCOMPLETE. Original theorem ledger 2/9.**

For the previously certified global residual factor
`q=-b*d*i+b*f*g+c*d*h-c*e*g+c*e*i-c*f*h`,
write `P=c*e-b*d` and `R=b*f*g+c*d*h-c*e*g-c*f*h`. Then `q=P*i+R`.

The complete algebraic wall splits into (1) `P != 0`, `i=-R/P`, and (2) `P=0`, `R=0`, with `i` unrestricted by this particular wall equation. Both must be intersected with the actual strict parent-bracket inequalities. Exact symbolic computation confirms the identity and shows `P` is not plus/minus any one of the 70 normalized parent brackets. This **does not prove** the exceptional stratum is realized inside parent 2599; its feasibility is still an open gate.

This is an exact single-factor decomposition, **not** the requested exhaustive full-parent CAD, master chamber graph, or D9 proof. Complete coverage of 17,824 parent-2599 candidate factors, all their intersections, and connected-chamber adjacency remains outstanding. The runnable local SymPy verifier and report are in the companion research ZIP.
