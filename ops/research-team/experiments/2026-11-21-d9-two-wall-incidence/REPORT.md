# D9 two-independent-wall incidence pilot (2026-11-21)

**Status: exact abstract/local-normal-form regression, NOT a new D9 theorem. Original ledger 2/9.**

## Source correction

The repository already certifies a genuine transverse parent-2599 node for two distinct global residual factors, IDs **1657** and **12874**, each with 65 labeled occurrences. `ai/omreal/DIAG9_GRAPH_COM_AUDIT.md` certifies a local 4-chamber diamond, rank-two Jacobian and all nine sign faces. Thus the proposed "find a second independent wall" gate was **already solved** geometrically. This experiment does not rediscover it. The precise local rational coordinates or certified size of a square neighborhood have NOT been reconstructed in this cycle.

## New incidence stress test for the known transverse local type

The inverse-function theorem gives local smooth coordinates `(x,y)=(q_1657,q_12874)` near the certified transverse node (after appropriate rescaling). As a *normal-form test*, consider the proper polynomial Morse function on the entire model plane

`V(x,y)=((x^2-1)^2+(y^2-1)^2)/4.`

Its gradient is `(x(x^2-1),y(y^2-1))`, so all critical points are exactly the nine points in `{-1,0,1}^2`. The Hessian is `diag(3x^2-1,3y^2-1)`: four index-zero minima at `(±1,±1)`, four index-one saddles at `(±1,0),(0,±1)`, and one index-two maximum at `(0,0)`. Negative Euclidean gradient trajectories on coordinate lines connect saddles to adjacent minima, producing the 4-cycle incidence graph. Its integer incidence matrix has rank 3 and therefore `H_0=Q`.

`verify.py` checks exact derivatives, critical Hessian indices, incidence rank and kernel vector using SymPy. This is a nontrivial four-minimum/two-wall *algorithm regression*. It is **not** a certified Morse function on a specific physical neighborhood of the D9 node, because the source does not provide a global diffeomorphism onto a box containing the nine model critical points. Local inverse-function coordinates alone do not justify transporting the complete graph. The source's already certified four-chamber graph remains the actual geometric evidence.

## Research decision

The independent-wall test is not the next unresolved D9 gate. The actual bottleneck is **global coverage and attachment compatibility** of distinct local diamonds, with signature labels, parent boundaries and infinity. A useful next experiment must take two adjacent certified patches, provide explicit overlapping coordinate domains and prove that their chamber labels and low-index attachments glue correctly. Without those data, additional normal-form examples cannot advance D9.

No global connectedness, COM completion, all-parent universality, or new diagonal credit is claimed.
