# Producer-independent factor-19069 critical equidimensional certificate

## Verdict

**ACCEPT**, only at the exact fail-closed endpoint
`HASH_PIN_FIRST_UNRESOLVED_SATURATED_IDEAL_BRANCH`.  The reviewed constructor
surface is frozen at `951498b19c17886ffbf3b32d938dd741903d99a7`, tree
`f90cb55cdc51dd3ca0b077ba62e384e5df96e094`.  No constructor or falsifier
module is imported; their executable acceptance logic is outside this
certificate's trust boundary.

## Independent reconstruction

The verifier reconstructs row 2599 directly from the canonical catalogue as
70 ordered sign-normalized parent factors with 209 sparse terms and total
barrier degree 90.  It reconstructs factor 19069 independently as the exact
108-term degree-six, multidegree `(2,2,2)` polynomial.  It then checks every
parent node, all 630 factored barrier-derivative summands, all nine wall
derivatives, and all 36 `dB wedge df` nodes.  The product barrier remains
unexpanded.

The saturation is replayed independently in the 79-variable inverse
extension over `Q`.  Exactly 70 relations `H_i*y_i-1=0` invert the parent
factors.  The nine log-gradient nodes retain all 630 source derivatives, and
the 36 localized wedge equations are checked coordinate by coordinate.  The
identity `dB=B*L` with `B` a unit proves that contraction is
`<f_19069,W_ij>:(product H_i)^infinity`; no geometric projection, lambda-only
replacement, or expanded product is accepted.

The exact set-theoretic branch cover consists of the retained singular branch
`df=0` and nine lex-first nonzero-`df` pivot charts.  Every generator list,
variable precedence, pivot inverse, coefficient field, monomial order, and
semantic hash replays.  None of the ten branches has a characteristic-zero
equidimensional decomposition.  The first unresolved branch is
`EQ-B00-SINGULAR-DF-ZERO`, whose exact dimension, degree, multiplicity, and
strict-real residence all remain unresolved.  Dimensions `0..8` and emptiness
remain possible there, so positive-dimensional pieces are not excluded.

The ten true-boundary candidates, exact pinned-parent path tags, singular
scope, 2,800 skeleton parent tags, and the edge-39 local noncritical anchor are
byte-for-byte preserved from the accepted predecessor.  Algebraic
localization alone does not select the connected real parent component; an
exact path to the pinned row-2599 sample remains mandatory.

The verifier rejects 45/45 semantic-hash-resealed hostile mutations covering
source/factor identity, the unexpanded circuit, saturation and nonboundary
relations, localized ideal identity, singular and regular branch coverage,
unsupported dimensions/degrees/multiplicities/root claims, real residence,
boundary and parent tags, edge-39 overreach, resource scope, endpoint, and
ledger drift.

## Scope and ledger

The exact consequence is an independently replayed 70-inverse localization
circuit and a complete fail-closed singular-plus-regular branch frontier.  It
is not an equidimensional decomposition.  There is no zero-dimensionality
proof, no exact positive-dimensional real component, no real-root frontier,
no component sample, no boundary attachment classification, and no diagonal-
nine theorem or counterexample.  Ledger delta is **none**; the honest theorem
ledger remains **`2/9`**.
