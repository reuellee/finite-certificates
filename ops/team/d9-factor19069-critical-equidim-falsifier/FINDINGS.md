# Factor-19069 critical equidimensional-decomposition falsifier

## Verdict

`PASS` for the falsifier lane, with the research claim left **fail closed**.
The pinned sources independently reconstruct the connected row-2599 parent
scope as exactly 70 ordered signed factors (209 sparse terms; semantic digest
`1d9b940e...de701`) and independently reconstruct factor 19069 as a degree-6,
multidegree `(2,2,2)` polynomial with 108 sparse terms.  The frozen predecessor
circuit binds those sources to the unexpanded product, all 630 derivative
summands, and all 36 coefficients of `dB wedge df`.

No producer-independent Groebner basis, Hilbert series, saturation transcript,
or primary/equidimensional decomposition currently proves the dimension of the
saturated strict-interior critical ideal.  Therefore dimensions 0 through 8
remain possible at the first unresolved stratum
`FB-C0-STRICT-INTERIOR-FULL-SUPPORT`.  In particular, positive-dimensional
critical pieces have not been excluded, and no component degree, multiplicity,
real-root count, or component sample is certified.

The constructor's visible exploratory `probe_singular.py` does not change this
finding.  It asks for a mod-32003 Groebner basis of the smaller wall-singular
ideal `<f, df>`.  Even if that probe terminates, it is neither a
characteristic-zero certificate nor a computation of the saturated full
barrier-critical ideal `<f, dB wedge df> : (product H_I)^infinity`; it also has
no equidimensional, degree, multiplicity, real-residence, or parent-selector
certificate.  The probe is therefore correctly treated as non-authoritative.

## Adversarial coverage

The deterministic verifier rejects 33 hostile mutations.  They cover wrong
parent/factor identity, loss or reordering of any parent factor, expansion of
the 70-factor barrier, missing wall or wedge equations, incorrect saturation,
discarded singular or true-boundary strata, signs-only parent selection, false
parent-component tags, unsupported dimension/degree/multiplicity/root claims,
sampling or projection inference, local skeleton/collar overreach, and ledger
promotion.

## Exact scope

Saturation may invert exactly the 70 source-derived parent factors to describe
the strict interior, but it may not invert factor 19069, discard the Jacobian
singular locus, or erase true compactification-boundary obligations.  Algebraic
saturation alone also does not choose the connected row-2599 parent component;
that selection continues to require an exact path tag to the pinned sample.

The edge-39 root and collar remain a verified local null frontier only.  They
cannot establish ideal dimension, global component count, or attachment.
Sampler-only, active-margin-subset, projection, symmetry, ambient-orbit, and
unfiltered multiwall inferences remain prohibited.

## Ledger

Ledger delta: `none`.  The honest theorem ledger remains `2/9`; diagonal nine
remains open.  A promotion would require a producer-independent exact universal
certificate, which is absent from this lane's evidence.
