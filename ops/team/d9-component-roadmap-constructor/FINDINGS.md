# D9 component-roadmap projection and stratification preflight

The first constructive roadmap preflight terminates with an exact, fail-closed
endpoint. It reconstructs the pinned `S12,37` active sector from source rather
than trusting the stored inventory: 3,539 distinct active factor classes, 6,167
occurrences, and 70 parent brackets.

The one-wall layer is admissible under the opening gate: it requires 3,539
critical systems, below the 100,000-system ceiling. The complete unfiltered
two-wall layer is not: `C(3539, 2) = 6,260,491`, for a one-plus-two-wall total of
6,264,030 systems. The previously known 2,420 memoryless local candidates
cannot be substituted as a global filter because the preceding cycle disproved
that local representation's completeness.

The polynomial census remains tractable at the individual-wall level. Active
factors have degree at most 6 and at most 108 terms. The compactifying boundary
barrier is retained in factored form across 70 parent brackets, with total
degree 90; no expanded product is required.

The deterministic projection vector `(1,2,4,8,16,32,64,128,256)` is primitive,
but it is not yet authorized: the exact specialization-discriminant exclusion
certificate is absent. Consequently no critical system was solved and no
fixed-domain connectivity statement was attempted.

The producer-independent verifier reconstructs both polynomial inventories,
checks the pinned inputs and all counts, and rejects six hostile mutations. The
exact endpoint is
`STRATIFIED_SYSTEM_FRONTIER_EXCEEDS_GATE_WITHOUT_COMPLETE_INCIDENCE_FILTER`.

The next admissible object is a source-derived, globally complete active
multiwall-incidence filter together with an exact projection-discriminant
exclusion certificate. The theorem ledger remains `2/9`.
