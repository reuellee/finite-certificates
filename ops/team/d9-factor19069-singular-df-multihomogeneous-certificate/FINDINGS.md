# Producer-independent singular-df certificate findings

Verdict: **accepted fail-closed null frontier**.

The frozen 108-term primitive factor and all nine derivatives were rebuilt exactly, without importing producer code. The affine polynomial is not three-block homogeneous and is not multiaffine: its block-degree supports are `{1,2} x {1,2} x {0,1,2}`, its total degrees are `4,5,6`, and the variable maxima are `(2,1,2,2,2,2,1,2,1)`.  The supplied 12-variable trihomogenization was independently reconstructed and dehomogenizes exactly, but is correctly not used as a decomposition certificate.

The constructor therefore stopped at `MH-B00-AFFINE-SOURCE-STRUCTURE-CONTRACT`.  No characteristic-zero component decomposition, embedded-prime census, dimension/degree/multiplicity result, componentwise 70-factor saturation, strict real residence, or connected row-2599 parent tag is certified.  All 70 parent records and the predecessor null, boundary, and skeleton frontiers remain byte/semantic bound.

Adversarial replay rejected all 35 hostile mutations, including source, derivative, component, embedded/boundary, saturation, real/connected-tag, scope, endpoint, and ledger overclaims.  The theorem ledger remains `2/9` with delta `0/9`.
