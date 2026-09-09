# Stage D: the complete fixed-plane condition for one moving column

Registered after the Stage C referee reconstructed both two-triple certificates
and confirmed their open-neighborhood stability. The referee correctly noted
that three or more incident support planes may still share a line. The
two-triple counterexample alone does not exclude that mechanism.

This is a new, explicitly bounded question within the already authorized
AI-only program. The two-triple lemma remains retired. No result is credited
as theorem progress, and no cohort or original resource ceiling is enlarged.

## Exact target

At the same upper178 chart zero of parent 2599 and the same flow signature
triple, test whether there are three nonnegative Gordan witnesses and a label
e for which the normals of all incident supporting triples span dimension
at most two. This is the exact condition for a nontrivial projective motion
of that one column preserving all selected support planes.

For a pair T of distinct star rows, define

```text
Cl_e(T) = {I containing e : a_I lies in span(a_T)}
R_e(T) = {I not containing e} union Cl_e(T).
```

Uniformity makes distinct star normals nonproportional, so every pair spans
dimension two. Every incident support of rank at most two lies in one such
closure, including empty and one-row supports by padding. There are still
exactly 1,680 indexed pairs, although many closures may coincide.

The criterion succeeds if and only if all three restricted signed systems
have nonzero nonnegative kernel vectors for some pair. If successful, the
signed-simplex proper-escape proof applies to the intersection of all retained
planes. A universal version would imply triple Hc0 vanishing. A single
positive instance is not such a universal proof.

## Frozen input and useful endpoints

Only `seeat_parent2599_upper178.npz`, chart zero, signatures
`14988895318912,3405195891438080,40418075143643136` may be tested as a new
rank predicate. Reuse the already certified same-parent admissibility and
badness anchors; do not add other test points.

A negative certificate must recompute every rank closure exactly and give a
strict integer separator for at least one signature on every expanded row
set. Existing separator vectors may be reused only after checking all added
rows. Any additional search is restricted to this one frozen point.

A positive certificate must provide the closure and three exact dual
witnesses. A timeout preserves the first unresolved closure. Either endpoint
stops this follow-up; there is no further automatic weakening or cohort growth.

Assess the direct stability corollary separately. Nonzero rank minors stay
nonzero nearby, so a closure can only shrink in a sufficiently small
neighborhood of the fixed point. Strict separators on the original closures
would then remain sufficient, while positive rank-four full circuits preserve
full badness. This argument requires explicit rank and sign checks.

## Roles, resources, and acceptance

Coordinator: derive the exact equivalence and independently inspect or
construct the expanded certificate in `ops/team/ai-d3-rank-pencil-coordinator`.
Falsifier: independently test only the frozen point in
`ops/team/ai-d3-rank-pencil-falsifier`, using an isolated checkout on a fresh
branch. A previous clean worktree may be reused to respect the disk ceiling;
its old branch remains frozen. Discovery ceiling: 30 wall-minutes per role.

Independent review: at most 30 additional wall-minutes, in the existing
program ceiling. Freeze discovery before review and use separate acceptance
logic. Existing Stage C acceptance is not transferred automatically to this
stronger condition. Per-role memory remains 16 GiB; new artifacts at most
50 MiB per role; aggregate new disk allocation remains 2 GiB including
worktrees and recovery copies. No human contact, paid/external compute,
broad CAD, new atlas, push, merge, or canonical promotion.

The default closing action is precise `RETIRE` if the expanded criterion is
refuted, otherwise `STOP` with the positive or unresolved local scope. Both
leave the pair invariant and the global D3 theorem open unless a separately
accepted full-scope proof is actually produced.
