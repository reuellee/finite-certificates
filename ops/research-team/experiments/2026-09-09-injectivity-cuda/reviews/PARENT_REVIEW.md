# Independent review: actual-parent and CUDA portability pilot

**Verdict: ACCEPT FINITE LOCAL CERTIFICATES ONLY.** The original theorem ledger
remains **2/9**, the original injectivity assertion remains open, and zero of the
seven original obligations are closed. Original pair coverage and residual are
unchanged. The numerical search supplies no global coverage certificate.

The independent verifier imports no producer acceptance or discovery code. Its
arithmetic uses Python standard-library rational numbers, permutation
determinants, and a separate row-reduction implementation. Source NPY data are
read through a small standard-library parser. Operational tests execute the
producer as a black box in disposable copies of its outputs.

## Source and geometry

All seven declared source files match their byte lengths, SHA256 digests and Git
blob identifiers at the pinned PR49 head. All 178 literal source matrices satisfy
the same 70 strict colex parent signs. Chart zero is exactly the FLOW parent;
all three signature integers agree across source records.

The old FLOW dual weights use positive-gcd-normalized primitive integer normal
rows. The new certificates use raw rational cofactor rows. These are different
weight conventions: the old weights cannot simply be copied onto the raw rows.
The new producer correctly reconstructs its weights. All three old primitive-row
dual certificates and all nine inherited endpoint block labels were independently
replayed.

## Exact finite results

The structural output contains 128 literal rational wall candidates. Every
candidate's coordinate and rational displacement were independently bound to its
source chart, and all 70 parent signs and recorded failure indices were checked.
Of these, 27 fail the required parent chirotope and are rejected. The other 101
have independently verified positive three-row Gordan relations of rank two,
with each pair of supported rows independent. They comprise 101 distinct
literal parents and 101 distinct parent/support/signature triples, across ten
unordered supports. Signature index 1 contributes 76; index 2 contributes 25.
The numerical selection ordering and its exhaustiveness were not certified.

The selected compact witness, attempt 65, is one of those 101 records. Its
near-singular canary retains the strict parent chirotope but has exact rank three
on the stated support, with minor `-8463/312500000`. This proves the absence of a
three-row relation on that support without making any floating-point assertion.

The engineering output contains 32 independently verified literal parents and
96 block certificates: 81 BAD and 15 GOOD, with zero UNKNOWN. Every point's
provenance was reconstructed from the deterministic rational generator or its
frozen structural control file. All 70 parent brackets and all 56 derived normals
were recomputed from each literal matrix. Every GOOD certificate has 56 strict
positive margins; every BAD certificate has an exact nonnegative, nonzero dual
annihilating all four coordinates. The emitted producer dual supports have zero
weights removed.

The exact pattern counts are BBB:20, GBB:3, BBG:2, BGB:4, BGG:2 and GBG:1.
IDs 0, 2, 164 and 176 exhibit BBB, GBB, BGB and BBG, respectively. Together they
independently establish that the three fixed extension signatures are realizable
and that their feasibility regions are nonempty, proper and pairwise
incomparable. This is a property of this fixed family, not a new universal
cohomology statement.

Both structural controls receive full BGB labels. The first has the advertised
three-row BAD certificate. The near-singular control instead has a five-row BAD
certificate. Rejecting a proposed three-row dependence does not establish full
block feasibility.

## Numerical boundary and operational review

Eleven mathematical controls passed: altered positive dual weight, duplicate
support, changed source-signature bit, zero dual, a tiny rational off-wall
perturbation with unchanged dual, independent rank-three detection at that
perturbation, floating-point parent rejection, rejection of a positive relation
in the wrong parent chamber, negated primal witness, explicit UNKNOWN retention,
and zero-margin primal rejection.

Five independent CLI controls passed: unavailable CUDA returns exit code 2 with
no CPU fallback and no output directory; altered source fails its digest;
complete resume reuses all 16 chunks and emits byte-identical exact certificates;
changed resume configuration is rejected; and changed numerical payload is
rejected. Configuration hashes detect modifications, not an adversary who
rewrites both records and hashes.

Static CUDA review finds a coherent optional CuPy path for floating-point batched
parent determinants and derived normals. Timing synchronizes the current stream
before and after device work and transfers. SciPy LP proposals and exact rational
acceptance run on CPU. CUDA execution, CPU/GPU numerical parity, speedup, and
native Windows execution are **untested**. No mathematical inference depends on
any of these untested claims.

The producer's single initial CPU run reports about 11.11 seconds, of which
about 0.157 seconds is the part currently eligible for CUDA acceleration. Those
are descriptive producer measurements, not independently benchmarked hardware
comparisons. The current profile does not establish a useful GPU speedup.

## Replay

From the checkpoint root:

```sh
python parent_pilot/referee/verify.py --structural parent_pilot/structural/SEARCH_RESULT.json --engineer parent_pilot/engineer/run/exact_candidates.json
python parent_pilot/referee/operational_checks.py
```

The first command is standard-library-only mathematical verification. The second
requires the producer's NumPy/SciPy dependencies and is specifically a test for
an environment where CUDA is unavailable. `COMBINED_AUDIT.json` records the
arithmetic replay; `OPERATIONAL_CHECKS.json` records the CLI controls. Publication
wrapper verification and clean archive replay remain coordinator integration
gates outside this worker review.
