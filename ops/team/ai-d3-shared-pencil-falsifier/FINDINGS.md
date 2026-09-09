# Stage B: an actual-parent counterexample to the shared-pencil lemma

Status: **frozen discovery handoff, pending independent referee acceptance**.
Base: `ee7c110a0862ec2da961a4b8c9987a0b90e03a0a`.
Branch: `research/ai-d3-shared-pencil-falsifier-20260905`.
Owned surface: `ops/team/ai-d3-shared-pencil-falsifier`.

## 1. Conclusion

The preregistered universal pointwise shared-pencil lemma is false. At chart 0
of `seeat_parent2599_upper178.npz`, the three fixed flow-triangle signatures

```text
sigma_0 =    14988895318912
sigma_1 =  3405195891438080
sigma_2 = 40418075143643136
```

are valid, proper, pairwise incomparable, and simultaneously Gordan-bad.
Nevertheless, for **each** of the `8 * choose(21,2) = 1,680` choices of a parent
label `e` and two incident triples `T`, at least one of the three signed systems
has an integer strict primal witness on

```text
R(e,T) = {I : e not in I} union T.
```

That witness excludes every nonzero nonnegative Gordan dependence on those
rows. There is therefore no common choice `e,T` of the required kind. The
negative certificate is a table of 1,680 references to just **23 integer vectors**.
A search-independent checker verifies all **62,160** required strict inequalities
using unbounded Python integers, as well as the source geometry and signature
hypotheses. It does not trust the search or tope enumeration.

This is an actual-parent counterexample to the proposed intermediate lemma.
It is **not a counterexample to D3**: it says nothing about the compactness of
the triple-bad component or the existence of a different proper escape. No
compact-support cohomology class is asserted. The source theorem and pair
invariant are unaffected. The theorem-ledger delta is zero.

## 2. The entire preregistered cohort

No additional shared-pencil predicate cases were tested.

| Fixed case | Exact status | Evidence |
|---|---|---|
| Shatter pattern 0, bits `(0,4,3)` | Positive control passes | Label `1`, incident triples `134/127`, three exact positive Gordan witnesses on the retained rows |
| Upper chart 7, same signatures | Ineligible | Signature at bit 3 is strictly feasible at this chart; the other two are bad |
| Upper chart 0, the three flow signatures | Counterexample | Full badness for all three, valid/proper/incomparable signatures, and 1,680 strict separating certificates |

The search found three successful pairs at the positive-control point. The
independent checker needs and verifies the designated `134/127` success only;
the exhaustive positive count is not needed for any conclusion. The counterexample's
negative denominator is independently verified in full.

The bit-3 signature making chart 7 ineligible is `58432476850159616`.
Its saved full strict primal witness is

```text
(-348602350135272028790280,
 -403819892312073490680720,
 -576253604946604036910007,
  313796342335974611815429).
```

All 56 signed dot products are strictly positive. In accordance with the
preregistration, this case was marked ineligible and not replaced.

## 3. Binding the negative to an actual uniform parent

The counterexample parent is the following integer `4 x 8` matrix, with columns
carrying labels `1,...,8`:

```text
Y = [ -94  -25  256  256    42   -3  -78 -101
     -163   54   35 -164   -96  256  256  -21
      256  256  -27  -25   197  160  -83   54
       71  122   19 -204  -256  -61  -93 -256 ]
```

The verifier compares this matrix literally to upper chart 0. It independently
computes all 70 parent determinants by Bareiss elimination. They are nonzero,
and their signs match zero-based catalog row 2599 of
`ai/omgamma/data/cat_4_8.txt`:

```text
++++++++++++++++++++++++++++-++--+++++++++-+++----+--++--------++--+++
```

For each triple `I=(i,j,k)` in the repository's colex order, the normal is
computed from

```text
a_I(Y) p = det(y_i,y_j,y_k,p).
```

Its four integer cofactors are divided by their positive gcd. This is a
positive row rescaling, so it changes neither strict feasibility nor
nonnegative-dependence existence. Bit `I` of a signature is positive precisely
when its signed normal uses `+a_I`. No arbitrary matrix data or invented normal
labels occur in this construction.

The certificate is written in the integer gauge to keep its arithmetic compact.
It also refutes the lemma on normalized realization space. The first four
columns form a positive basis. If `B=(y_1,...,y_4)`, set
`D=diag(1/|(B^(-1)y_5)_j|)` and apply `G=D B^(-1)`, followed by positive
column normalizations. Uniformity makes the denominators nonzero. Every derived
row transforms as `a'_I=d_I a_I G^(-1)` with `d_I>0`.
The map `w_I -> w_I/d_I` preserves nonnegative dependence and exact row support;
the map `p -> Gp` preserves strict signed inequalities after multiplication by
the positive `d_I`. The row-restriction predicate is consequently unchanged.
This uses no relabeling or unrecorded signature reorientation.

## 4. Full badness, validity, properness, and incomparability

### Full badness at the counterexample point

`upper_chart_0_flow.json` records one exact positive integer five-support Gordan
vector for each signature. The checker reconstructs the actual primitive
derived normals and verifies

```text
sum_I w_I sigma_i(I) a_I(Y) = 0,
w_I > 0 on its recorded nonempty support.
```

Normalize by the positive sum of the weights to obtain normalized witnesses.
Thus the three badness statements are direct dual certificates; they do not
depend on the asserted completeness or count of a tope enumeration.

### Valid extension signatures

For each of the three signatures, the verifier checks all 1,260 uniform rank-four
three-term Grassmann--Pluecker sign relations on nine labels against the same
parent chirotope. It also verifies a strictly feasible actual nine-point
realization of each signature at an auxiliary parent chart below. The latter
is an independent geometric reason that these are valid realizable extension
signatures, not arbitrary signings.

### Exact witnesses for the locus hypotheses

The already stored upper-cover certificate supplies an integer feasible point
for each target signature. Three existing charts suffice:

| Signature index | Existing upper chart | Stored point index | Status at that chart |
|---|---:|---:|---|
| `0` | `3` | `24588` | Signature 0 feasible; signatures 1 and 2 bad |
| `1` | `14` | `14261` | Signature 1 feasible; signatures 0 and 2 bad |
| `2` | `2` | `2534` | Signature 2 feasible; signatures 0 and 1 bad |

The copied matrices and strict integer points, plus six positive integer dual
witnesses for the other signatures, are in `admissibility_flow.json`.
The independent checker compares them to their exact stored NPZ entries,
checks all 70 parent brackets at each chart, and directly verifies the primal
and dual equations. Each of the three charts therefore lies in one feasibility
locus and outside the other two. This proves all six ordered incomparability
directions. Together with simultaneous badness at chart 0, it proves that all
three loci are nonempty and proper.

These auxiliary charts are used only to bind the hypotheses of the fixed
negative case. No shared-pencil predicate is tested there, no chart is created,
and no atlas is expanded. The witness lookup uses binary search in the stored
extension ordering to find candidates, then verifies their actual determinant
signatures. The final checker does not depend on the ordering or lookup method.

For the first two cohort cases, the signature hypotheses are similarly bound
by the stored shatter patterns `1`, `16`, and `8`: each has its designated bit
feasible and the other two bad. The verifier checks those stored exact primal
and dual witnesses, with positive row-gcd conversion for the original raw-normal
Gordan weights.

## 5. The complete exclusion certificate

Each parent label occurs in exactly 21 of the 56 triples. The certificate
`upper_chart_0_flow.json` contains:

- `witness_pool`: 23 records, each with a signature index and an integer point
  in `Z^4`;
- `coverage_rows`: 1,680 records `[e,I,J,witness_index]`, with one-based parent
  label `e`, zero-based colex row indices `I<J`, and `e` contained in both triples;
- three full positive Gordan witnesses, the actual parent, signatures, and
  source-case metadata.

The verifier independently constructs the required set of all 1,680 `(e,I,J)`
keys. It rejects missing, duplicate, or invalid keys. For each key, it constructs
the 35 nonincident rows and the two retained incident rows, and checks that the
referenced point makes every one of those 37 signed dot products positive.

The observed certificate statistics are:

```text
required choices:          1680
verified choices:          1680
strict inequalities:      62160
distinct point records:      23
usage by signature:       (1596,83,1)
minimum integer margin:   162514748513691
largest point coordinate: 46 decimal digits
```

The signature assignment is only a convenient covering choice; it is not a
claim that other signatures fail or survive at those particular restrictions.

For a fixed key, suppose the excluded signature had a nonzero nonnegative
dependence on the retained rows. Pairing its zero vector with the recorded
strict primal point would give a strictly positive sum, a contradiction.
Consequently at least one block is excluded for every key. This argument is
independent of how the point was found.

Testing pairs also excludes all smaller `T`. If all three dependences existed
on an empty or singleton incident set, enlarging it to any incident pair would
retain those dependences. That would contradict the corresponding pair's strict
separator. The countercertificate therefore covers the lemma's literal
“at most two” quantifier.

## 6. Discovery and verification trust boundaries

`search_shared_pencil.py` uses the existing exact recursive tope enumerator on
the three frozen matrices. Each returned tope has an integer witness checked
against all 56 normals. For each signature and label it filters topes agreeing
on the nonincident rows, then checks the two selected incident signs. It also
uses a small exact rational phase-I simplex with Bland pivots to extract positive
Gordan witnesses. There is no floating-point LP or sampling.

The full tope counts were 26,112 at each of the three matrices. Discovery took
approximately 10.65, 10.65, and 11.55 seconds for the three cases, including tope
witness verification. The exhaustive tope method is useful for finding the
certificate; its completeness is not a premise of the negative proof.

`verify_shared_pencil_certificate.py` is separate. It imports neither the
producer nor the tope enumerator, and performs no simplex, LP, circuit search,
or enumeration of extensions. It reconstructs the 70 brackets and 56 normals
with independent determinant code and checks the finite certificates directly.
NumPy is used only to read and bind the existing NPZ source entries. The saved
`VALIDATION.json` reports `PASS`; its verification run took about 0.56 seconds.

No source-constructor lane or coordinator discovery artifacts were inspected.
This is a search-independent producer replay, **not** independent referee
acceptance. The referee must review the frozen commit separately.

## 7. Replay, resources, and decision

From the assigned worktree, using the bundled Python executable:

```powershell
$py = 'C:\Users\reuel\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe'
& $py -B ops/team/ai-d3-shared-pencil-falsifier/verify_shared_pencil_certificate.py
```

Optional reproduction of the bounded discovery and admissibility extraction:

```powershell
& $py -B ops/team/ai-d3-shared-pencil-falsifier/search_shared_pencil.py
& $py -B ops/team/ai-d3-shared-pencil-falsifier/bind_admissibility.py
```

The search stops at the first negative case, which is the third and final
member of the preregistered cohort. No additional predicate cases remain to be
tested in this handoff. Input SHA-256 pins, exact outcome metadata, timings,
and final artifact digests are recorded in `SOURCE_PINS.json` and `RESULT.json`.
Peak resident memory was not instrumented. The lane produced less than 1 MiB
of artifacts and used no paid or external compute.

An early import generated one ignored bytecode file under
`ai/omreal/__pycache__`. Cleanup was rejected by automatic approval review with
the message “blocked by policy” and no more specific reason. The file was left
in place; subsequent commands disable bytecode writes. No tracked source outside
the owned lane changed, and the earlier Stage A lane remained frozen.

Decision: **RETIRE the preregistered universal pointwise shared-pencil lemma**.
It fails on the fully admissible actual-parent data above. Do not replace that
claim by a looser escape statement without a new hypothesis and preregistration.

Trajectory: `INFORMATIONAL` for the D3 program. This result settles the selected
intermediate lemma negatively but does not close either named D3 invariant.
The theorem ledger remains `2/9`; global pair coverage remains `UNKNOWN`, and
the triple component census is unchanged. No push, merge, human contact,
canonical update, or D3 counterexample claim is part of this handoff.
