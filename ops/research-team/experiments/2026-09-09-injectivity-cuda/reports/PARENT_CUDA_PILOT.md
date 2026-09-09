# Actual-parent certificate search and CUDA pilot

9 September 2026. Mathematical source: PR49 revision
`59fec66666518257c585194b81061f60d91f439d`. Publication base:
`9e77c365b266e9d884e6ac14a0443992bec92c64` on main.

**The bounded pilot produced exact local certificates and a CPU/CUDA search
runner. It did not prove injectivity. The original ledger remains 2/9 and
all seven original global obligations remain open.**

## Results

The engineering run generated 4,096 candidate IDs representing 3,992 distinct
literal rational parent matrices. They include the original 178 source charts,
the three inherited event-side controls, deterministic perturbations, and
two current structural controls. Approximate screening found 2,856 candidates
matching the original parent signs and rejected 1,240 numerically. These are
screening classifications, not an exhaustive exact classification of the batch.

Thirty-two selected parents were verified exactly against all 70 original
parent brackets. All three fixed signatures received a full exact feasibility
or Gordan certificate: 96 block labels, comprising 81 bad and 15 good labels,
with zero UNKNOWN labels in this selected set. The exact patterns are:

| Pattern, in fixed signature order | Selected parents |
|---|---:|
| BBB | 20 |
| GBB | 3 |
| BBG | 2 |
| BGB | 4 |
| BGG | 2 |
| GBG | 1 |

G means a strict separator for all 56 signed derived normals. B means an
exact nonnegative, nonzero signed dependence. The BBB, GBB, BGB and BBG
anchors independently witness nonemptiness, properness and pairwise
incomparability for this particular family of three signatures. They do not
establish global parent-space coverage or any compact-support cohomology map.

The structural track screened 178 charts against 840 supports each, then
performed exactly 128 selected one-coordinate wall solves. It obtained 101
positive three-row circuits in strict parents and 27 exact parent-sign
rejections. The 101 accepted records are 101 distinct literal parents and
parent/support/signature tuples, covering 10 supports, two fixed signatures
and 71 seed charts. Their rank is exactly two and every pair of support rows
is independent. This supplies concrete original-geometry test fixtures for
the known possibility of three-row localization circuits; it is not a new
global theorem or a resolution of 101 original source orbits.

The near-singular control adds an exact 1/10^12 coordinate perturbation to
one witness. All 70 parent signs survive, but a 3-by-3 minor becomes
`-8463/312500000`, so the three rows have rank three. Its normalized singular
value ratio is approximately 9.16e-14, which an illustrative 1e-10 tolerance
would misclassify. In the selected batch, this nearby parent remains bad by
a different five-row certificate. Losing one circuit support therefore does
not imply that the entire signature becomes feasible.

## CPU profile and CUDA implementation

The completed CPU run took approximately 11.11 seconds, with peak reported
resident memory about 83 MiB on this Linux session.

| Stage | Measured CPU-run wall time | Approximate share |
|---|---:|---:|
| Batched determinants and normals | 0.157 s | 1.4% |
| Numerical LP and parent screening | 10.19 s | 91.7% |
| Exact selected-parent certification | 0.444 s | 4.0% |

Other startup, generation, bookkeeping and output time account for the
remainder. These are one-run observations on this environment, not a laptop
benchmark. The structural search separately took about 0.78 seconds.

The runner provides NumPy CPU and optional CuPy CUDA paths for batched geometry.
CUDA selection must fail clearly when CuPy or a usable GPU is absent; it must
not silently fall back to CPU. GPU timing includes synchronization. The LP
and exact certificate stages remain on CPU. Deterministic chunks record
their configuration, candidate identities and payload hashes for resumption.

No NVIDIA device was exposed here. CUDA execution, numerical parity and RTX2070
speedup are **untested**. Even eliminating the entire measured geometry cost
would save only about 1.4% on this particular run if other stages were
unchanged. A larger geometry-bound task or a separately validated solver
strategy would be needed to justify a substantial GPU performance claim.

See the engineering README for CPU/CUDA commands. CuPy documents
[CPU/GPU array usage](https://docs.cupy.dev/en/stable/user_guide/basic.html),
[synchronized performance measurement](https://docs.cupy.dev/en/stable/user_guide/performance.html),
and [CUDA-matched installation packages](https://docs.cupy.dev/en/stable/install.html).
The backend design follows those interfaces; execution on the user's laptop
is still required to validate that path.

## Verification boundary

The independent referee reconstructs literal rational parents, all70
parent signs, all56 raw cofactor normals and each accepted witness without
importing producer acceptance logic. It also rechecks all178 original charts
and the inherited event-side controls. The old FLOW weights use primitive
integer normals; the new certificates explicitly use raw cofactor normals.
This distinction is verified rather than silently mixing normalization rules.

Structural review independently checks all128 recorded wall attempts and
all101 accepted witnesses. It does not assert that the floating screening
ordering is unique across numerical platforms, or that those128 attempts
exhaust the continuous parent space. Hostile controls alter weights, supports,
signatures, exact coordinates, and parent signs and test near-singular cases.
This is exact arithmetic plus written source/scope review, not Lean verification.

Final operational review and clean publication replay are recorded in the
companion referee and publication artifacts. The prior injectivity attack
and collision-deletion diagnostic are preserved byte-for-byte in the same
evidence checkpoint, with their own independent reviews.

## Strategy and ledger

This was the user-authorized bounded discovery/performance pilot, not a
renewal of the abstract deletion route as a theorem-converging strategy.
The preceding attack and deletion diagnostic both left the theorem score at
2/9. Deletion removed the abstract kernel while violating singleton Hc2
vanishing. The current pilot adds admissible local witnesses but does not
provide the missing global comparison of compact-support maps.

Opening and closing proof-distance values are unchanged: score2/9, deficit1
to the next-ledger goal3/9, seven open original obligations, pair residual
and coverage UNKNOWN, triple unresolved source records1,162,302. The source
record count is not a count of connected components. This cycle removes
zero original source records and closes zero original global obligations.

Trajectory: **INFORMATIONAL**. Post-pilot decision: **STOP** this bounded
search. The mathematical next step still requires a global comparison or
attachment theorem preserving the original lower vanishings. More local
samples or a faster geometry backend do not themselves justify continuation.

The publication uses a separate additive GitHub branch and pull request.
PR49, its historical evidence, and original canonical ledger files are
preserved. The backup is a self-contained evidence snapshot, not a complete
repository-history backup. Publication identifiers are recorded separately
so the immutable evidence archive has no circular self-hash dependency.
