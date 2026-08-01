# A certified atlas: design note

Written 2026-08-01, after `ai/omminor` was built. **Design note only — no
implementation is proposed here beyond the schema.** It generalizes
`ai/omgamma/data/coverage_4_9`'s tree format from *one* certificate about
*one* property into a reusable artifact, so that the next question about the
same catalog reuses the traversal instead of rebuilding it.

## 1. Why, concretely

`ai/omgamma` certified that the (9,4) mutation graph is connected and
produced `tree_4_9.npz`: 10.4 MB holding the root key plus, per class, its
parent and the mutated basis, from which every key, stabilizer, depth and
edge voltage is *derived* rather than stored. That artifact is excellent and
it is already the right idea. What it is not is *extensible*: it answers one
question, and the two projects that came after it each rebuilt their own
scaffolding around it.

Costs actually paid in this repository for the lack of a shared frame:

* `ai/omreal/sweep49.py` re-flattens the coverage arrays into
  `sweep_state/*.npy`, invents its own status byte-map, its own shard
  layout, its own resume rule and its own certificate schema.
* `ai/omminor` (this directory) then had to *scrape* those shards, invent a
  byte-offset resume protocol, and build an ad-hoc memo cache
  (`data/idcache_4_8.npz`) for a lookup — labeled 8-element chirotope →
  catalog row — that is obviously shared infrastructure, not a private
  detail of one measurement.
* When the harvest record format changed mid-session, the line-count resume
  silently became invalid and the whole prefix had to be recomputed. Nothing
  in the design made that a detectable error.
* The (4,5), (4,6), (4,7) and (3,7) realizability certificates did not exist
  because there was nowhere to put them, even though they cost 4 seconds to
  produce and are needed by any minor-theoretic statement.
* `ai/omreal` and `ai/omminor` both hold a private notion of "the prefix of
  the catalog I have covered", expressed differently, and neither can be
  intersected with the other without re-reading gigabytes.

Each is small. Together they are the reason the same 9.28M classes have been
traversed with four different pieces of bookkeeping.

## 2. The shape

Three layers, each independently checkable.

```
atlas/<r>_<n>/
  spine/                     the canonical enumeration -- ONE per cell
    MANIFEST.json
    tree.npz                 root key + packed (parent, flip)  [~1.1 B/class]
  props/
    <property>/
      MANIFEST.json          schema, checker, canaries, coverage
      shard_0000.jsonl.zst   certificates, one per settled class
      ...
      coverage.bin           1 byte/class: UNSEEN | verdict code
  index/
    <name>.npz               derived lookup tables, each with a recipe
```

### 2.1 The spine

Exactly `coverage_4_9`'s tree, unchanged, promoted to the primary object:
the root key, and per class the parent row and the mutated basis. Its
contract is the one already written in that MANIFEST:

* **row order is canonical** — row 0 is the root; rows of depth d follow
  those of depth d−1, ordered by (parent row, flipped basis);
* **row i is a well-defined class**, reconstructible by replaying the tree;
* **`parent[i] < i`**, so replay is a single forward pass.

Every property slot indexes classes by **spine row**, and nothing else. That
single decision is what removes the four bookkeeping systems: a "prefix"
becomes a set of rows, two prefixes intersect by `&`, and a resume point is a
row number that cannot silently mean something else.

The spine also fixes the one thing this session got wrong by accident: a
property file's ordering is *not* a resume token. Rows are.

### 2.2 A property slot

A property is anything that assigns each class a verdict from a small
alphabet plus, optionally, a certificate. Examples already in the repo, and
one that is not yet:

| property | alphabet | certificate | who has it now |
|---|---|---|---|
| `realizable` | REALIZABLE / NON_REALIZABLE / OPEN | integer r×n matrix, or a Gordan vector | `ai/omreal` sweep shards |
| `minor` | list of (element, witness class) | none needed — the witness class id is the certificate, given `realizable` at n−1 | `ai/omminor` |
| `stab` | integer | the winning placement and sign combination | derived in `coverage_checker` |
| `mutable_degree` | integer | none (recomputable in µs) | derived |
| `bfp_support` | integer or NONE | the Gordan vector | `ai/omreal` |

`props/<property>/MANIFEST.json` declares, at minimum:

```json
{
  "property": "realizable",
  "spine_sha256": "...",              // binds this slot to ONE spine
  "alphabet": ["REALIZABLE", "NON_REALIZABLE", "OPEN"],
  "record_schema_version": 3,          // bumping this INVALIDATES resume
  "checker": "ai/omreal/checkcert.py", // must accept every emitted record
  "checker_sha256": "...",
  "depends_on": [                      // other slots, possibly at other cells
    {"cell": "4_8", "property": "realizable", "manifest_sha256": "..."}
  ],
  "canaries": ["...ids, see 3..."],
  "coverage": {"settled": 1445227, "of": 9276595,
               "verdict_counts": {"REALIZABLE": 1430771, "...": 0}}
}
```

Two fields carry most of the value.

**`record_schema_version`.** A runner refuses to `--extend` a slot whose
manifest declares a different schema version than the runner emits. That is
the error this session hit and did not detect.

**`depends_on`.** The minor property at (4,9) is meaningless without the
realizability verdicts at (4,8); pinning the dependency's manifest hash
makes "which (4,8) answer was this computed against" a fact rather than an
assumption. It also makes the *stale-dependency* case detectable: if the
(4,8) slot is ever extended or corrected, every dependent slot is
mechanically known to be stale.

**`coverage.bin`.** One byte per class, in spine row order. It is the
resume token, the prefix descriptor, and the join key all at once; at
9.28M classes it is 9.3 MB, and at (4,10)-scale it is the only per-class
array that stays affordable. Verdict counts in the manifest are a
*derivable* summary and must be re-derived by the checker, never trusted.

### 2.3 The index layer

Derived tables that are expensive to compute and cheap to check: the
labeled-chirotope → class lookup that `ai/omminor` built ad hoc, key arrays
for binary search, invariant → candidate-class maps for the fast minor test.
Each ships with a **recipe** (the exact command that rebuilds it) and a hash,
and nothing may depend on an index except for speed: deleting `index/` must
change runtimes and nothing else. That rule is what keeps an index from
quietly becoming a second source of truth.

## 3. The generic runner and its canaries

One driver, parameterized by a property module supplying four callables:

```python
decide(rows, chis, ctx) -> [(verdict, record | None), ...]
canaries()              -> [Canary, ...]
schema_version()        -> int
dependencies()          -> [(cell, property), ...]
```

The runner owns everything else: wave/shard planning over the spine,
worker pool, append-only shard writes truncated to the last complete line,
`coverage.bin` as the checkpoint, manifest emission, and the resume rule
("a row is done iff `coverage.bin[row] != UNSEEN`" — never a line count,
never a byte offset).

**Canaries are part of the slot, not the script.** Each property module must
declare, and the runner must run *before every session and record in the
manifest*, at least:

* a **positive control** — a class with a known verdict, which must come
  back with that verdict;
* a **negative control** — a class of the opposite verdict, likewise;
* an **impossible-input control** — an input the property must refuse (a
  non-chirotope, a wrong-length sign string);
* one or more **sabotages** — a certificate the module produces, corrupted
  in a named way, which the declared `checker` must REJECT. `ai/omminor`'s
  five lift sabotages and `ai/omgamma`'s `canary_checker.py` are exactly
  this, written twice.
* a **cross-property control** where one exists. The strongest check found
  in this work was not a sabotage but a *consistency* one: no realizable
  class may have a non-realizable minor. Any two slots related by a lemma
  should declare that lemma as a runnable assertion over their intersection.

Failing a canary must fail the session, and the manifest must record which
canaries ran and their outcomes — an artifact whose manifest does not name
its canaries should be treated as unchecked.

## 4. What this would have changed here

| this session | with the atlas |
|---|---|
| scraped 490 MB of JSONL shards to recover 14,396 chi strings | read `props/realizable/coverage.bin`, take the NON_REALIZABLE rows, replay the spine for their chirotopes |
| byte-offset resume protocol, invalidated by a schema change | `coverage.bin` diff; schema change detected by the manifest |
| ad-hoc `idcache_4_8.npz` | `index/labeled_4_8_to_class.npz` with a recipe |
| (4,7) certificates written into a private `data/` | `atlas/4_7/props/realizable/` — and automatically available to the next question |
| "which prefix is this?" answered by prose in three documents | one row-set, intersectable |
| the (4,8) dependency of the minor result stated in prose | `depends_on` with a hash |

## 5. What it would not fix, and the honest cost

* It does **not** make (4,10) feasible. §9 of `MINOR_THEORY.md` puts that
  cell at 10^11–10^12 classes; `coverage.bin` alone would be 0.1–1 TB and
  the spine 0.1–1 TB, before any property. The atlas is for reusing a
  traversal that fits, not for making one that does not.
* It adds a layer between a question and its answer. `ai/omreal`'s sweep is
  ~400 lines and works; the atlas is worth building only if a *third*
  question about (4,9) is coming. Two of the three properties above already
  exist, so the test is whether a fourth question is expected within the
  same cell.
* The spine is a commitment. Changing the canonical convention, the basis
  order, or the tree's row order invalidates every slot at once. That is
  the right trade — a shared frame that can drift is worse than none — but
  it means the convention must be settled before the first slot is written.
  It is: `OMGAMMA.md` §2, unchanged since 2026-07-31 and used by three
  projects.

## 6. Minimum viable version

If only one piece is built, build **`coverage.bin` plus the resume rule**:
one byte per class in spine row order, written by whatever produces
verdicts, with a manifest recording the spine hash and a schema version.
That single file subsumes `sweep_state/st.dat`, the byte-offset protocol in
`ai/omminor/harvest.py`, and the "which prefix" prose in three documents,
and it is perhaps fifty lines. Everything else in this note is elaboration.
