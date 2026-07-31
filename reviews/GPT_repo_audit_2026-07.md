# Adversarial repository audit — 2026-07

## Verdict: NEEDS-CORRECTIONS

I found no evidence that the headline theorem `max f₀(3,5) = 42` is false. Its
attainment certificate passed, the 384-chirotope orbit computation passed, the
split-orbit accounting passed, and sampled exact certificate transport passed.
The committed all-library report also records 132,681 checks and zero failures.
Likewise, the current compact `(9,4)` omgamma artifact passed its fast checker.

The repository is nevertheless **not trustworthy as presented**. The most
important public trust claim — that results have independent, standalone
verification — is stronger than the maxout upper-bound checker that is actually
shipped. CI can also pass after material artifacts are deleted or corrupted,
several public status pages contradict one another, and the documented
dependency/reproducibility boundary is inaccurate. These are correctable
certificate-engineering and presentation defects, not a demonstrated
mathematical refutation.

There are no FATAL findings in this audit.

## Scope and method

I inspected the whole working snapshot at
`7fc1c9a864ff989463bf4165cb053ca7338a06c8` and compared it with the public
`origin/main` at `0cef3d4101a8ff3aa4e541835d3f8cee40271654`. The working branch
was 20 commits ahead, principally because of the active omgamma campaign.
Accordingly, omgamma findings below describe the in-flight snapshot and are
clearly distinguished from defects already present on public `origin/main`.
`ai/omgamma/data/big_4_9/meta.json` was changing during the audit; I used it
only for stable facts such as `complete: false`, not as a frozen class-count
record.

I did not run `run_all.py`, because static inspection showed that it is not
read-only: some of its `verify_*.py` children overwrite committed artifacts or
create temporary data. I did not run the prohibited
`audit_all_certificates.py`, any multiprocess search, or any long computation.
Targeted checks performed were:

- `ai/maxout/verify_c66_new_cases.py`: PASS on all five exact instances,
  including the 42-vertex `(3,5)` attainment.
- `ai/maxout/check_om35_uniqueness.py`: PASS; 384 chirotopes, one orbit.
- `ai/maxout/capstone/check_split_orbits.py`: PASS; stabilizer order 10 and
  split accounting confirmed.
- `ai/maxout/capstone/check_transport.py --n-group 12 --n-certs 8 --seed 11`:
  PASS; 144 exact transported pairs.
- `ai/omgamma/checker_fast.py` on the shipped 547-class `(9,4)`
  sub-certificate: V1–V5 PASS, including `S_9` and full sign space.
- `ai/omgamma/checker_fast.py` on `(8,4)`: V1–V5 PASS on 2,628 classes.
- A static tracked-file credential scan found no private-key blocks or obvious
  AWS, GitHub, OpenAI, or bearer-token values. This is evidence, not a guarantee
  that no secret exists.

## Findings

### 1. [SERIOUS] The maxout upper-bound “independent audit” imports the generator's load-bearing symbolic construction

**Locations:** `README.md:3-6,17-18`; `CONTRIBUTING.md:43-52`;
`ai/maxout/capstone/CAPSTONE.md:307-310,339-355`;
`ai/maxout/paper/maxout35note.tex:158-162,394-415`;
`ai/maxout/stage2c2_gpt/audit_all_certificates.py:15-19,37-39,101-122,202-205`;
`ai/maxout/stage2c2_gpt/check_stage2c2.py:210,270-300`;
`ai/maxout/stage2c2_gpt/audit_all_report.json:3-21`.

The public bar says a verifier should not import the generator whose output it
checks. The paper and capstone repeatedly call the all-certificate pass a
“standalone audit” and describe every serialized object as independently
re-verified.

The shipped all-library auditor instead imports
`monomials_of_degree`, `normal_forms`, and `quotient_matrix` directly from
`gp_degree3_search.py`, the generation-side program. It uses that imported
`quotient_matrix` to re-establish the quotient-ring identities. It also imports
`common` for the valid-pattern/family traversal. The stage checker is explicit
about doing the same thing: its comment at lines 270–273 acknowledges importing
the generator's quotient construction.

There is an independently written numeric row builder, but it checks
specialization at the fixed `U_ints`. That is valuable and caught no error; it
does not independently reconstruct the symbolic quotient identities that turn
a fixed-realization certificate into a **cell-wide** certificate. A shared bug
in the generator's symbolic semantics could therefore survive the advertised
full audit.

**Artifact evidence checked:** the committed report says 132,681 entries,
zero failures, PASS. The Fable paper review reports genuinely independent
symbolic checks on nine sampled certificates and fresh-realization checks on a
larger sample (`ai/maxout/paper/REVIEW_note_fable.md:275-292`), which is strong
support for the mathematics. But that independent implementation is not the
shipped all-certificate verifier. Thus this finding is **not “the theorem is
wrong”**; it is “the public independence claim is stronger than the shipped
artifact.”

### 2. [SERIOUS] CI can green-pass missing or corrupted research artifacts

**Locations:** `.github/workflows/verify.yml:19-31,44-59,61-75`;
`run_all.py:2-23`; `CONTRIBUTING.md:43-52,76-81`;
`jacobian/verify_deg3_keller.py:169-194`;
`jacobian/verify_cubic_homogeneous.py:47,133-179`;
`jacobian/verify_druzkowski.py:39,164-187`;
`jacobian/README.md:3-4,27-35`.

The PR job runs only `run_all.py --fast`, which skips
`verify_druzkowski.py` and `verify_sae_circuit.py`. The job named
“full certificate audit” does **not** run the full repository suite: it runs
only maxout's `audit_all_certificates.py`, and only on a schedule or manual
dispatch. Consequently the two slow verifiers are never run by this workflow.

There are concrete false-green cases:

1. A PR can corrupt or delete committed `jacobian/druzkowski_map.py`; the fast
   job never reads it, and the scheduled job is unrelated.
2. The other Jacobian “verifiers” are also generators:
   `verify_deg3_keller.py` overwrites `deg3_map.py`,
   `verify_cubic_homogeneous.py` reads that file and overwrites `cubic_map.py`,
   and `verify_druzkowski.py` reads the latter and overwrites
   `druzkowski_map.py`. Neither `run_all.py` nor CI checks that regeneration
   leaves the committed artifacts byte-identical. An accidentally stale
   committed artifact can be repaired in the CI worktree and still yield green.
3. `run_all.py` discovers only `verify_*.py`. Important check/audit programs
   such as the coherence-transfer audit are outside that contract. The maxout
   upper-bound checks are covered by bespoke workflow steps, but no general
   manifest enforces that every README headline has a required CI target.

The Jacobian mathematical notes are unusually honest about which steps are
exact spot checks and which use classical lemmas. The defect is the claim that
each witness has a cheap **independent** verifier and the inability of CI to
protect the committed witness files.

### 3. [SERIOUS] The maxout result has mutually incompatible public status pages, and two lower bounds can be read as upper-bound results

**Locations:** `README.md:17-18,36-37,136-155`;
`ai/maxout/README.md:1,12-30,35-40`;
`ai/maxout/attack_c66_deficit.md`;
`ai/maxout/capstone/CAPSTONE.md:5-14,285-291`;
`ai/maxout/verify_c66_new_cases.py`.

The results-index headline says `max f₀(3,5) = 42` and that Proposition 6.5 and
the odd conjecture at `n=5` are refuted. The detailed section in the **same
root README** still calls 42/58/84 “lower bounds; nothing refuted.”
`ai/maxout/README.md`, which root says is the self-contained entry point for
the directory, likewise says “Nothing is refuted” and does not mention the
capstone or its verification manifest at all.

The `(4,5)=58` and `(3,7)=84` files certify exact vertex counts for two
particular instances. They do **not** prove that the maxima are below 60 and
88. Root `README.md:37` says those cases are “certified below the conjectured
maxima,” wording that invites exactly that stronger reading. The older attack
note scopes them correctly as lower bounds/search resistance.

**Artifact evidence checked:** `verify_c66_new_cases.py` passed and establishes
the exact counts of the five shipped instances. The additional capstone
artifacts are what promote only `(3,5)` from the 42-instance lower bound to an
exact maximum. This finding therefore says the `(3,5)` theorem is
well-supported but its repository index is internally incoherent; it also says
the `(4,5)` and `(3,7)` index wording is too strong.

### 4. [SERIOUS] The optimizer results-index headline attributes counterexamples where the underlying note does not

**Locations:** `README.md:35,117-125`; `ai/optimizer/README.md:1-11`;
`ai/optimizer/optimizer_counterexamples.md`.

The index calls the directory “Counterexamples to published optimizer
convergence claims (Muon, Li–Hong, Lion).” The directory's own accurate scope
is different:

- Muon's deployed coefficients do falsify a published coverage claim.
- Li–Hong's admissible stepsize set is empty for `β ≥ 1/2`; this makes that
  portion of the theorem vacuous, not false by counterexample.
- The Lion period-two cycle contradicts an informal constant-hyperparameter
  claim; the annealed published theorems stand.

The underlying result is scoped honestly. The public index is not. This is a
claim error in the presentation, not an artifact failure.

### 5. [SERIOUS] The current omgamma wrapper passes vacuously when headline sub-certificates are absent

**Locations:** `ai/omgamma/README.md:23-38`;
`ai/omgamma/verify_omgamma.py:2-10,45-59,61-82`;
`ai/omgamma/OMGAMMA.md:422-503,706-725`;
`ai/omgamma/checker.py:34-36,198-221`;
`ai/omgamma/checker_fast.py:9-24`.

`verify_omgamma.py` checks `(9,4)` and `(9,3)` compact certificates only if all
four files exist. Otherwise it prints `SKIP` and leaves `ok` true. Its final
exit is therefore zero even if a contributor deletes one or all of the
headline `(9,4)` files. Because `run_all.py` invokes this wrapper, CI would
wave the deletion through.

The in-flight ledger's high-level status is otherwise commendably honest:
`OMGAMMA.md:3` says ACTIVE, the table says the `(9,4)` coverage sweep is in
progress, and Result A carefully distinguishes `H = Gbar` from class-list
completeness.

**Artifact evidence checked:** the four `(9,4)` files were present during this
audit, and `checker_fast.py` passed V1–V5 on 547 classes, 546 tree edges, and
74 generators. Thus `H = Gbar` is supported independently of the unfinished
coverage sweep. However, the claimed second pure-Python check is not
reproducible directly from the shipped compact files: `checker.py` uses plain
`open()` and has no `.gz` support, while the only shipped reps/tree files are
gzip-compressed. Direct invocation failed while reading the gzip header;
`checker_fast.py` explicitly supports gzip. Either ship uncompressed files or
give the pure checker gzip support before publishing the current WIP.

This finding concerns the current ahead-of-origin omgamma work. It should be
fixed before those commits are pushed, rather than read as a criticism of an
already-public final `(9,4)` connectivity result.

### 6. [SERIOUS] The documented dependency and hermetic-reproduction boundary is false

**Locations:** `README.md:3-12,234-244`;
`.github/workflows/verify.yml:28-29,42-43,71-72`;
`ai/maxout/stage2c2_gpt/gp_degree3_search.py:25-28`;
`ai/maxout/stage2c2_gpt/coefficientwise_search.py:31-33`;
`ai/coherence-transfer/README.md:9-35`;
`ai/coherence-transfer/audit_dossier.py:12,34-43,364-370,765-776,874-876`;
`ai/coherence-transfer/source/experiments/coherence_transfer_semireal.py:42-49`;
`ai/coherence-transfer/source/analysis/analyze_coherence_transfer_semireal.py:18-19`;
`ai/coherence-transfer/source/run_replication.sh:3-10`;
`ai/maxout/build_cert_d4n4.py:10-11`.

Root says the requirements are “python3 + numpy + sympy only.” The headline
maxout stage checker imports generation modules that import SciPy; the workflow
quietly installs SciPy. The coherence-transfer replication also requires
SciPy, scikit-learn, and pandas. There is no repository-level requirements or
environment manifest, and CI installs unpinned latest NumPy/SciPy/SymPy.
Root's blanket “Every claim ... in exact arithmetic” sentence is also
incompatible with its own later, correctly disclosed empirical
coherence-transfer result.

The coherence-transfer audit has a more subtle hermeticity defect. Although the
README's explicit command supplies the in-repo dossier, the script's
“raw artifacts absent” check walks the hard-coded author home
`/home/reuellee_gmail_com`. On Windows or under another username that walk
finds nothing and passes vacuously. Its outcome therefore cannot support the
README's machine-specific expected 86/88 count. The default dossier/PDF paths
also point into a private upload directory. The replication shell script
assumes `~/repl_bundle` and `~/venv312`, and a maxout certificate-generation
script loads missing arrays from the author's absolute home path.

The coherence-transfer scientific note itself correctly calls the result
empirical, discloses post-hoc work, ships the metrics, and does not pretend to
be an exact certificate. The problem is reproducibility plumbing and the word
“self-contained,” not an identified error in its reported effect.

### 7. [MINOR] The arXiv ancillary bundle does not contain the load-bearing upper-bound library

**Locations:** `ai/maxout/paper/arxiv_submission.zip`;
`ai/maxout/paper/anc/README.txt:29-33`;
`ai/maxout/paper/maxout35note.tex:147-162,388-404`.

I inspected the ZIP without extracting it. It contains the TeX source, five
attainment JSON files, the stdlib attainment verifier, and the ancillary
README. It does not contain the 132,560 upper-bound certificates or their
auditor. The TeX inside the ZIP is byte-identical to the working
`maxout35note.tex`, and the ancillary README accurately sends readers to
GitHub, so this is **not a false claim**.

It is nevertheless a durability and reviewer-readiness risk: the theorem's
load-bearing half depends on a mutable external repository rather than the
submitted archive. A versioned release/DOI containing the upper-bound library
and an independent checker would make the arXiv artifact genuinely
self-preserving.

### 8. [MINOR] Several ledgers, reviews, and count labels are stale or mutually inconsistent

**Locations:** `README.md:277-284`;
`ai/maxout/paper/REVIEW_note_fable.md:9,51-90`;
`ai/maxout/paper/maxout35note.tex:219,275-280`;
`jacobian/fallout_harvest.md:260-270`;
`ai/absorption-metric/README.md:3-5,15,29,44`;
`ai/absorption-metric/indistinguishability.md:17-18`;
`README.md:195-196`;
`ai/omgamma/OMGAMMA.md:443-444,718-725`;
`ai/omgamma/data/big_4_8/meta.json:7-12`;
`ai/omgamma/data/big_4_8/summary.json:5-9`.

- The newest named Fable referee report still says `NEEDS FIXES`, even though
  its false-equality and canary-wording fixes appear in the current TeX. There
  is no response/closure marker, so a public reader cannot tell whether the
  blocking verdict is current.
- Root provenance says the Jacobian fallout prose was interrupted, while a
  full `fallout_harvest.md` is present. That note in turn says the files were
  “Not committed to git,” although they are committed.
- The absorption-metric README says 28 checks total while its own components
  say 17 + 14 + 14 = 45. Root and `indistinguishability.md` still call
  `verify_m1_optimality.py` a 10-check verifier; its current source reports 14.
  These are bookkeeping errors, not mathematical defects.
- In the active omgamma ledger, the trust-boundary sentence says the `(9,4)`
  mass identity “has been executed,” but the live `meta.json` says
  `complete: false` and no final `summary.json` exists. The main table correctly
  says “sweep in progress,” so this is a stale subordinate sentence.
- The old `(8,4)` `meta.json` says sign dimension 4 and `hol_full: false`, while
  `summary.json` says `H_equals_Gbar: true`. The separately shipped current
  `(8,4)` certificate passed this audit with full sign space, so the result is
  supported and the metadata pair is stale.

### 9. [MINOR] Public logs expose private paths and full agent-session transcripts

**Locations:** `.gitignore:1-2`; `.github/agy_infra_review.log`;
`ai/maxout/capstone/codex_review_run.log`;
`ai/maxout/paper/codex_note_review.log`;
`ai/maxout/paper/maxout35note.log`;
`ai/sae-grounding/REVIEW.md:5-7`;
`ai/coherence-transfer/AUDIT_REPORT.md:122`.

These files are already on public `origin/main`, not merely local debris.
`git ls-tree -l origin/main` reports:

- `codex_review_run.log`: 335,283 bytes;
- `codex_note_review.log`: 4,038,423 bytes;
- `maxout35note.log`: 19,813 bytes;
- `.github/agy_infra_review.log`: 3,764 bytes.

The Codex logs contain complete prompts, commands, worktree paths, and
references to a scratchpad copy of source material. The TeX log exposes the
author's Windows profile and package installation paths. Numerous prose/source
files also retain `/home/reuellee_gmail_com`, `C:\Users\reuel`, `E:/Projects`,
or `~/...` paths. Root `.gitignore` ignores only Python bytecode and does not
protect logs or common build products.

I found no obvious credential value in a static secret-pattern scan, so this is
**public-hygiene and privacy leakage, not a discovered secret compromise**.
Separately, the current worktree contains an untracked
`reviews/codex_repo_audit.log` of roughly 3.3 MB. It is not public or tracked,
but the current ignore rules make it easy to commit accidentally with this
report.

### 10. [NOTE] The remaining result directories are mostly scoped more carefully than the root marketing language

**Locations:** `ai/sae-grounding/README.md`;
`ai/sae-unidentifiability/README.md`;
`ai/coherence-distortion/README.md`;
`ai/interp-illusions/README.md`;
`ai/coherence-transfer/README.md`;
`jacobian/fallout_harvest.md:11-19`;
`ai/scouting/TARGETS_2026-07.md`.

I found no material claim/artifact mismatch in the SAE grounding,
SAE-unidentifiability, coherence-distortion, or interpretability-illusion
directory claims. Their theorem scopes and exact-versus-empirical boundaries
are explicit. Jacobian's fallout note also distinguishes machine-verified
facts, cited reductions, and abstract corollaries, even though its top-level
“independent verifier” description and CI handling need correction as described
above. `ai/scouting` is clearly a target shortlist, not a ledger of established
results. `LICENSE` is an ordinary complete MIT license and presented no issue.

## Single most valuable correction before arXiv submission

Ship a **genuinely independent maxout upper-bound verifier** that reconstructs
the valid-pattern systems, quotient-ring identities, and polynomial reductions
from the certificate schema without importing `gp_degree3_search.py`,
`coefficientwise_search.py`, or their shared construction helpers; run it over
all 132,560 certificates, publish its immutable output with the arXiv/release
artifact, and make that check required CI.

That one correction directly closes the largest gap between the paper's trust
claim and the artifacts a skeptical outsider can actually inspect. README
cleanup, dependency pinning, and log removal should follow, but none is as
important to the submitted theorem's credibility.
