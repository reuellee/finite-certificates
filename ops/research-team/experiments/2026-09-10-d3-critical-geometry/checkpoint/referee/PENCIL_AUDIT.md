# Independent review: the fixed-projection 231-pair exclusion

Verdict: ACCEPT at the explicitly finite scope. For the22 displayed
quadratic restrictions and the one projected-parent configuration
(2,3,4,5), all231 unordered pairs have no common zero with all70 original
parent brackets nonzero and dependent four-height gradients. This is not
a universal parent theorem, a compactness theorem, or a new source-orbit
count.

Reviewed mathematical account: `falsifier/FINDINGS.md`, SHA256
`474bcc3ae9bdc1811becc980bca6b44a4795439c5968d5b149a2c8d3797e008a`.
Reviewed aggregate: `falsifier/verify_pencil_coverage.py`, SHA256
`42bfafedbb00cfc8b4454356f2967714ef14a53d46ff9fbbd9eb88c908cc46d3`.
All scripts and evidence in the chain are bound in REVIEW_IDENTITIES.json.

## Independent input reconstruction and replay

`referee/verify_quadratic_inputs.py` independently reconstructs the actual
normal determinants, all70 affine parent brackets, the symbolic anchor
identity, and all22 homogeneous quadratic matrices. For each quadratic it
divides the actual occurrence determinant and proves that the quotient has
only parent-bracket factors. It constructs the matrix from polynomial
coefficients rather than importing the producer's Hessian routine. An
altered quadratic is rejected. Output: QUADRATIC_INPUT_REPLAY.json.

The complete aggregate was then run with --replay in a temporary clean copy
of the frozen falsifier directory. All seven regenerated JSON outputs agree
byte-for-byte with the reviewed originals. Output: PENCIL_CLEAN_REPLAY.json.
The updated exceptional-kernel script, which explicitly rejects an
unresolved identically zero binary restriction, was in that copy. Separate
hostile runs prove that deleting one pair or marking an algebraic exception
unresolved is rejected. Output: PENCIL_HOSTILE_REPLAY.json.

No producer acceptance function was imported into the independent input
checker. The projective pencil chain itself was reviewed line-by-line and
then rerun as a separate program; its saved result JSON was not accepted
without this reconstruction.

## Completeness of the algebraic branch analysis

At a common affine zero, dependent four-coordinate gradients of two
homogeneous quadratics force a projective pencil kernel: Euler's identity
supplies the fifth coordinate equation. The individual kernels cover the
parameter at infinity.

For a nonzero determinant pencil, a rank-four common-zero kernel makes its
determinant derivative vanish by the rank-one adjugate formula. Lower rank
also makes the root multiple. Thus simple roots may be omitted. Exact
factorization confirms that every repeated factor in these193 pencils is
linear over Q. All104 repeated-root cases are checked, including the20
higher-nullity cases.

The38 identically singular pencils have generic rank four. Their generic
kernel lies on an explicit parent boundary or at infinity. These identities
extend over every rank-four parameter; a rational kernel basis pole does
not remove a point of the rank-constant kernel line. The gcd of all25
four-by-four minors gives the complete exceptional rank-drop parameter set.

The13 rational exceptions and the24 irreducible nonlinear factors are
covered. Exact quotient-field elimination includes every real embedding;
real-root isolation excludes factors without real embeddings. A real
rank-one symmetric quadratic vanishes exactly on its radical, justifying
the radical checks. The one larger rational kernel splits into two linear
components, both explicitly excluded. The aggregate rejects unresolved
statuses and verifies coverage against the original231 pairs.

Higher-degree restrictions, other projected-parent configurations, and
unlisted primitive factors are outside this theorem. Smooth uniform
common-zero surfaces can still be compact, so this finite regularity result
does not discharge the global critical-locus or triple-escape obligation.
The report's separate fixed-projection inertia observation is not needed
for the accepted global positive theorem or the original ledger.
