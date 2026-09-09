# Complete fixed-plane obstruction for one moving parent column

Status: exact coordinator countercertificate; independent acceptance pending.
Target registration: `390d447eb1dceb3cf78b294a043e303a6430c267`.
The independent Stage D producer was not read or imported.

## Exact predicate and its geometric meaning

For a fixed uniform parent Y and label e, let a_I be the normal of the
three-plane indexed by I. All normals with e in I annihilate y_e. They
therefore lie in a three-dimensional vector subspace. Distinct triples have
nonproportional normals: otherwise four or more parent columns would lie in
one three-plane, contradicting uniformity.

Suppose three nonnegative nonzero signed Gordan witnesses have a union of
incident support normals of rank at most two. Extend a spanning set of that
union to a pair of distinct star normals if necessary. Every incident support
row then lies in the rank closure of that pair. Conversely, three witnesses
on the nonstar rows plus such a closure have incident union rank at most two.
Thus the 1,680 indexed closures exactly exhaust the predicate, with no circuit
minimality or positive-weight requirement on all retained rows.

When the predicate holds, the intersection of the retained support planes
has vector dimension at least two. The existing signed-simplex argument gives
a nonconstant proper path of y_e in that intersection to a true parent
boundary. Every incident selected normal stays on its original positive ray,
so inverse positive scaling transports the three witnesses. The proof does
not require the total number of incident triples to be at most two.

The converse geometric statement is limited and useful: if the incident
normal union has rank three, its annihilator is exactly span(y_e). Holding
the other columns and all selected support planes fixed then fixes the
projective ray of y_e. This does not prohibit changing support planes,
changing witnesses along a different path, or moving multiple columns.

## Exact computation on the frozen actual point

The checker reads only the pre-Stage-D constructor and falsifier certificates,
verifies their byte hashes, and reconstructs all 56 raw normals from the
integer parent. It computes each closure with a two-coordinate Cramer test:
after choosing a nonzero two-by-two minor of a pair a,b, the coefficients
solving the two selected coordinates must solve all four coordinates. All
arithmetic is integral; division and tolerance decisions are absent.

It checks all 70 parent brackets, all three full positive Gordan dependencies,
and the nonzero constant-sign cofactors of each five-row support. It then
uses the 23 integer vectors already frozen in the earlier falsifier package.
For every expanded row set, the checker selects a vector with strictly
positive scalar product on every retained signed row. Failure to find such a
vector is a failed check, not a negative mathematical conclusion.

All checks pass:

| Quantity | Exact value |
| --- | ---: |
| New rank-predicate points | 1 |
| Indexed pair closures | 1,680 |
| Distinct labeled closures | 896 |
| Indexed closures containing six star rows | 840 |
| Indexed closures containing two star rows | 840 |
| Checked expanded strict inequalities | 65,520 |
| Existing vector pool | 23 |
| Pool vectors used by this deterministic replay | 11 |
| Minimum integer margin | 162,514,748,513,691 |

For every label and every triple of nonzero nonnegative Gordan witnesses at
this point, the incident support normals consequently have rank exactly
three. The previously accepted Stage C catalog, normalization, signature
validity, properness, and incomparability bindings remain the input for this
same actual point; no new point or admissibility assumption is introduced.

## Why the obstruction persists near the point

For each of the finitely many pairs, choose a nonzero two-by-two rank minor.
For each star row outside its closure, choose a nonzero three-by-three minor
certifying nonmembership. These finite nonzero conditions persist locally.
The closure of each pair at a nearby point is therefore contained in its
closure at the original point; it can shrink, but cannot acquire one of the
excluded rows in a sufficiently small neighborhood.

Every fixed separator remains strictly positive on every originally retained
row near the point. It remains sufficient for any smaller nearby closure.
The three full five-row signed circuits have rank four and coherent strictly
positive cofactors, so their positive dependencies persist as well. Together
with the 70 strict parent signs, this gives an open neighborhood of triple
badness and failure of the complete rank predicate. Restricting to the
continuous nine-dimensional projective normalization gives the corresponding
open set in the actual parent space. No numerical radius or component count
is asserted.

The independent referee must check this continuity argument and the rank
minors, rather than relying on the coordinator's result label. No D3
cohomology class, compact component, or global vanishing is inferred.

## Replay and scope

Run `py -3 -B ops/team/ai-d3-rank-pencil-coordinator/check_rank_closures.py`.
`CHECK_OUTPUT.json` records the exact replay. The raw integer matrix, row
ordering, signatures, and separator pool are pinned by hashes in the script.
The script imports no other project code. It does not use the active Stage D
producer, LP, floating point, tope enumeration, a new atlas, or extra test
points. Research trajectory is informational; ledger and all seven canonical
obligations remain unchanged. This follow-up ends at the exact certificate.
