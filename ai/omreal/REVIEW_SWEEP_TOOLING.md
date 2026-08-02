# Adversarial review of the (4,9) sweep tooling

Written 2026-08-03 by an independent reviewer, against the **finished**
sweep (`sweep_state/` treated read-only throughout; no `python.exe` with
`sweep49` in its command line was run or modified). Every claim below is
backed by fresh code under `ai/omreal/review_scratch/`, run against the
actual `sweep_state/certs/*.jsonl` shards and `st.dat`/`Z.dat`/`hi.npy`/
`lo.npy` — not against documentation. `sweep49.py`, `realize.py`,
`treewalk.py`, `omdecode.py`, `bfp.py`, `checkcert.py` were read in full and
not modified.

**Bottom line: the sweep tooling has two real, low-severity defects, both
in the crash-recovery path, neither capable of producing a wrong verdict or
misattributing a certificate to the wrong row, and one of them already
self-detected and self-repaired by the project's own later tooling (which
this review independently re-verified). No row/certificate mismatch, no
unverified write reaching a REALIZABLE verdict, and no catalog-decode
inconsistency were found anywhere in the actual data.**

---

## 1. Row/certificate mismatch (task item A.1)

### 1.1 Catalog-decode consistency — CONFIRMED clean

`sweep49.do_chunk` decodes a chunk's chirotopes with `omdecode.signs_from_keys`
(→ `ai/omgamma/coverage_checker.build_tables`/`decode_keys`), then verifies
every realized matrix against that decoded `chi` using `realize.py`'s
**own, independently built** `Geom` (a second, from-scratch colex-basis
table: `sorted(combinations(range(n), r), key=lambda t: tuple(reversed(t)))`,
built without importing `omdecode` or `coverage_checker` — `realize.py`'s
own docstring for `_gp_ok` says so, and it is true). If these two basis
orderings ever disagreed, `chk == chi` in `do_chunk` would fail almost
always (comparing signs at different bases is not a symmetry any real
configuration respects), and the sweep would never have completed. That
argument is a good sanity check but not a proof, so it was tested directly
(`review_scratch/codec_crosscheck.py`):

| test | result |
|---|---|
| random-pattern round trip, reviewer's own from-scratch codec (`mycodec.py`, pure-Python big-int shifts, no numpy) | 200,000 trials, **0 mismatches** |
| reviewer's own decode of `(hi,lo)` vs `omdecode.signs_from_keys` (→ `coverage_checker`), 20,000 real catalog rows | **20,000/20,000 agree** |
| `encode(reviewer's own decode(hi,lo))` reproduces `(hi,lo)` exactly, same 20,000 rows | **20,000/20,000 agree** |
| `realize.py Geom(9,4).bases0` (0-based, +1) **==** `coverage_checker.build_tables(9,4)['bases']` (1-based), all 126 entries | **True, exact** |
| reviewer's own `colex_bases(9,4)` **==** `coverage_checker`'s, and **==** `realize.py`'s (+1) | **True, both** |

**Grade: CONFIRMED.** The two basis orderings the sweep silently relies on
agreeing (the decoder's and the verifier's) are identical, checked directly
rather than inferred from the sweep's own success. A bug here would have
been a silent, catalogue-wide, invisible corruption (row *i*'s written
matrix would verify against the *wrong* chirotope's sign pattern and no
internal check would ever catch it); it is not present.

### 1.2 The `todo` → `CHI` → row binding inside `do_chunk` — CONFIRMED by inspection

```python
todo = rows[st[rows] == TODO]              # boolean-indexed, order-preserving
CHI = omdecode.signs_from_keys(N, R, hi[todo], lo[todo])   # same todo, same order
for k, i in enumerate(todo):
    chi = CHI[k]                            # CHI[k] <-> hi[todo[k]] <-> row i
```
`todo` is never re-sorted, re-filtered, or copied-with-reordering between
being used to slice `hi`/`lo` and being iterated. Boolean indexing and
NumPy fancy-indexing with the same index array are both order-preserving.
There is no window in which `chi` could correspond to a row other than the
loop's own `i`. **CONFIRMED**, by direct code reading; this is also the
thing item 1.1 empirically stress-tests at scale (a binding bug of this
kind would show up as systematic bracket-check failures, and none occur:
see §4 below, 0 parse failures and later a 2,500-certificate fresh
determinant re-check, 0 mismatches).

### 1.3 `ProcessPoolExecutor` `wid` collision — a real, latent defect, zero observed impact

Inside one wave, **all** chunks are submitted to the executor at once:

```python
chunks = [wave[s:s + a.chunk] for s in range(0, len(wave), a.chunk)]
jobs = [(j % a.workers, c) for j, c in enumerate(chunks)]
futs = {ex.submit(do_chunk, j): j for j in jobs}
```

`wid = j % a.workers` determines which shard file (`shard_%02d.jsonl % wid`)
a chunk's certificates are appended to — but `wid` is a property of the
**chunk's position**, not of the **OS process** that ends up running it.
With typically dozens of chunks per wave and 4 (later 9) workers, `wid`
repeats many times per wave. `concurrent.futures.ProcessPoolExecutor` hands
queued work items to whichever process asks next, in submission order —
but nothing prevents worker A from still being mid-chunk on `wid=0` when
worker B, having finished a different chunk, is handed the *next* `wid=0`
chunk and opens the same `shard_00.jsonl` in append mode concurrently. This
is a genuine, real property of the code: two OS processes **can**, in
principle, hold the same shard file open for append at the same time.

What this can and cannot do, precisely: each `rec` dict is built from
purely loop-local data (`chi = CHI[k]` for that call's own `todo`), so
cross-process interleaving of *file writes* cannot relabel one row's
certificate as another's — the worst case is a corrupted or lost *line*,
never a mis-attributed one. This was tested directly rather than argued
(§4): a full parse of all 9,276,454 certificate lines across all 10 shard
files found **zero** malformed lines and **zero** duplicate chi strings
within a shard.

**Grade: DEFECT, latent, severity LOW, unexercised in this run.** The code
property is real and should be fixed (bind `wid` to a stable per-process
identity, e.g. via an initializer that stashes `os.getpid()`-derived state,
or take a per-shard lock) — but it produced no detectable damage anywhere
in the actual 9,276,595-row sweep, on this platform, across both the
4-worker and 9-worker phases. That "zero damage" is an empirical result
from this run's data, not a guarantee for a future one.

---

## 2. Unverified writes (task item A.2)

Read the full decision cascade in `do_chunk` (wall-crossing → orphan direct
search → BFP → repair ladder). Every exit path was traced to its write:

| exit path | writes `REALIZABLE`? | verified before write? |
|---|---|---|
| wall-crossing succeeds (`tw.cross_from` + `rz._rationalise`) | yes | **yes** — falls through to the shared `chk = rz.exact_bracket_signs(Zi, geom); if chk is None or not np.array_equal(chk, chi): raise SystemExit(...)` gate below |
| orphan direct search (`rz.realize`, weapon-A budget) | yes | **yes**, same shared gate |
| repair ladder (`C_KW`/`E_KW`/`EH_KW`) | yes | **yes**, same shared gate |
| BFP search (`bfpmod.find_bfp` via `_bfp_record`) | writes `NON_REALIZABLE` | **no inline check** — see below |
| nothing worked | writes `RESIDUE`/OPEN, no claim | n/a (no claim to verify) |

**The REALIZABLE side is unconditionally self-verifying by construction.**
Every branch that can set `Zi` funnels through one shared block before
`st[i]` is ever touched:
```python
if Zi is not None:
    chk = rz.exact_bracket_signs(Zi, geom)
    if chk is None or not np.array_equal(chk, chi):
        raise SystemExit('row %d: produced matrix does not realize the class' % i)
    Z[i] = Zi
    rec = {..., 'verdict': 'REALIZABLE', 'matrix': ...}
```
There is no code path that reaches `st[i] = WALK` or `REPAIR` without this
gate. A bug anywhere upstream (search, wall-crossing, rationalisation)
degrades to "search failed" — it cannot silently corrupt a REALIZABLE
verdict. **CONFIRMED.**

**The NON_REALIZABLE side is NOT inline-verified.** `_bfp_record` calls
`bfpmod.find_bfp`, which internally solves an LP for the *support* of a
Gordan certificate and then reconstructs the weights *exactly* via
`_exact_nonneg_kernel` (Fraction-based Gauss-Jordan elimination on
`[V_sup^T; 1^T] w = [0; 1]`) — but nothing in `sweep49.py` or `bfp.py`
re-derives `sum_i w_i V[i] == 0` after the fact before `st[i] = NONREAL` is
set and the record is written. Correctness of every one of the 203,780
NON_REALIZABLE verdicts therefore rests entirely on `_exact_nonneg_kernel`'s
Gauss-Jordan implementation being bug-free — a hand-trace of its pivoting
(full Gauss-Jordan: each pivot clears its column in **every** other row,
not just the ones below, so `w[c] = rhs[piv.index(c)]` is read directly out
of the fully reduced system) did not find an indexing or sign error, but a
hand-trace is not a proof.

**Grade: DEFECT (a real gap in the sweep's own write-time guarantee),
severity LOW.** It is a gap in *this component's own self-verification*,
not an unverified claim in the catalogue overall: every NON_REALIZABLE
certificate the sweep ever wrote has since been re-verified twice
(`checkcert.py`, `fpcheck.py`) and, in this review, a **third** time from
scratch (5,400 of 203,780 sampled — the entire reservoir this review
collected — with an independently re-derived "which term is BIG",
`ai/omopen/review_scratch4/verify_nonrealizable.py`, **0 rejections**, see
the companion review). So the class of bug this gap could have let through
(a `find_bfp` construction that returns a mathematically invalid `w`) would
have been caught downstream even though it was not caught at write time.

---

## 3. Resumability across the 4→9-worker restart (task item A.3)

### 3.1 "A worker skips any row whose status is already set" — CONFIRMED

`todo = rows[st[rows] == TODO]` at the top of `do_chunk`, re-evaluated
fresh for every chunk of every wave of every invocation. There is no
in-memory state carried between `cmd_run` invocations beyond what is on
disk in `st.dat`/`Z.dat`, which are memory-mapped in `'r+'` mode and shared
at the OS page-cache level — a process restart does not roll back writes
already made through the mapping. **CONFIRMED** by code reading; also
consistent with the sweep logs (§3.3).

### 3.2 "Certificate shards are truncated to their last complete line on
resume" — CONFIRMED present, and does what it claims

```python
def _truncate_partial(path):
    ...
    nl = tail.rfind(b'\n')
    if nl < 0: fh.truncate(0)
    else: fh.truncate(size - back + nl + 1)
```
called once per `wid` at the top of `cmd_run`, for `wid in range(a.workers)`
— i.e. only for the *current* run's worker count. This is fine: it only
needs to fix a trailing **partial JSON line**, and a partial line can only
ever be at the true end of whichever shard file was mid-write at the kill
— shard files from a *previous*, differently-sized worker pool are simply
appended to further (their own trailing partial line, if any, is still
truncated on the *next* resume, since `shard_00..03` exist under both the
4-worker and 9-worker numbering). The size skew actually observed
(`shard_00`–`03`: 850–880 MB; `shard_04`–`08`: 120–136 MB) is exactly
consistent with `shard_00`–`03` having accumulated both the 4-worker-phase
and a share of the 9-worker-phase traffic, while `04`–`08` are 9-worker-only
— not evidence of anything wrong.

### 3.3 The real defect: buffered `fh.write`, flushed only once per chunk

This is the mechanism behind the **141 rows with a status but no
certificate line**, which `certaudit.py` found and `backfill.py` repaired.
Independently re-diagnosed here from the code, then confirmed against the
data:

```python
for k, i in enumerate(todo):
    ...
    Z[i] = Zi                              # (1) durable: direct memmap write
    rec = {...}
    fh.write(json.dumps(rec) + '\n')       # (2) BUFFERED — Python's default
                                            #     text-mode buffer, NOT flushed
    st[i] = how                            # (3) durable: direct memmap write
# ... loop continues for up to `chunk` (default 8000) rows ...
fh.flush(); os.fsync(fh.fileno()); fh.close()   # only here, once per WHOLE CHUNK
st.flush(); Z.flush()
```

`Z[i]` and `st[i]` are memory-mapped writes; both are visible to any other
process reading the same file and survive a process kill (they live in the
kernel page cache, not in the killed process's own memory). The **JSONL
text**, however, sits in Python's user-space `TextIOWrapper` buffer
(flushed automatically only when full, ~8 KB, or explicitly at chunk end)
— so a kill between steps (2) and the next buffer-fill/flush **loses
already-`st[i]`-marked rows' certificate lines**, while `Z[i]` (written in
step 1, *before* the buffered write) survives. This is exactly "lost lines,
not lost work" — the failure can only produce a *missing* certificate for
an otherwise-genuine result, never a wrong or misattributed one, because
steps (1)–(3) all derive from the same loop-local `chi`/`Zi` and there is
no way for one iteration's `rec` to leak into another row's `st[i]`.

**This review independently re-derived the mechanism's fingerprint and it
matches exactly.** From a full independent reconciliation of the shards
against `st.dat` (`ai/omopen/review_scratch4/my_certaudit.py`, completely
fresh code, full `json.loads` parsing, not `certaudit.py`'s byte-offset
heuristic — see the companion review for the "0 unmatched, 0 duplicated,
141 missing, all `REALIZABLE(walk)`" reconciliation, which reproduces
`certaudit.py`'s own numbers exactly by an independent method):

| diagnostic | finding |
|---|---|
| depths (waves) touched by the 141 missing rows | **exactly 3** of 27: depth 11 (39 rows), depth 13 (53 rows), depth 20 (49 rows) |
| within each affected depth, row-index clustering (gap threshold 20,000) | depth 11: 4 clusters, sizes 14/14/10/1; depth 13: 4 clusters, sizes 24/19/6/4; depth 20: 4 clusters, sizes 14/13/12/10 |
| cross-reference against the sweep's own run logs | `sweep_run.log` ends mid-depth-13 (last complete wave: depth 12); `sweep_run2.log` **starts** "206421/9276595 rows already done; **4 workers**" and its first wave summary is depth 13 — i.e. depth 13 straddles exactly the run1→run2 restart. `sweep_run2.log` later prints "6683554/9276595 rows already done; **9 workers**" immediately before depth 20's summary — i.e. depth 20 straddles exactly the 4-worker→9-worker restart the task description names. |

Depth 11 is not explained by a boundary visible in the two logs read here
(there was evidently a third, earlier, unlogged restart before `depth 11`
of `43,910` rows had a full summary line in `sweep_run.log`'s own start
count) — its cluster pattern (4 groups of size ≤14, matching a 4-worker
buffer-loss) is consistent with the same mechanism, just at a kill event
outside the two log files this review had access to. Cluster sizes of 1–24
match "up to one Python IO buffer's worth of ~300–500-byte JSON records"
almost exactly. **This is not scattered, ongoing corruption — it is a
small, countable number of discrete kill events, each losing a bounded
tail-buffer per worker.**

**Grade: DEFECT, confirmed mechanism, confirmed blast radius, confirmed
already repaired.** Severity LOW: the failure mode is one-directional
(completeness gap only, never misattribution), fully detectable (a row
with a status and no certificate is a trivial reconciliation query), and
was in fact detected and repaired by the project's own tooling — which
this review re-verified independently and completely (not sampled): all
141 backfilled rows were checked by reading `Z.dat` directly (bypassing
`certs_backfill.jsonl`'s own fields entirely), decoding each row's
chirotope with the reviewer's own codec (bypassing `omdecode` entirely),
and recomputing all 126 brackets with the reviewer's own from-scratch
Leibniz-expansion determinant (bypassing `realize.py`'s determinant
entirely) — **141/141 independently confirmed**
(`ai/omopen/review_scratch4/verify_141_backfill.py`). The recommended fix
for future runs: flush+fsync per row (slower but simple), or reorder so
`st[i] = how` happens only after the chunk's flush/fsync has completed for
every row already written in that chunk.

---

## 4. Empirical corroboration: full parse-validity scan of every shard

`ai/omreal/review_scratch/shard_scan.py` streamed and `json.loads`'d **every
line of every one of the 10 files** in `sweep_state/certs/` (4 parallel
workers, ≤4 cores, 42 s wall time for ~4.35 GB):

| | |
|---|---|
| total lines | 9,276,454 |
| blank lines | 0 |
| **parse failures** | **0** |
| REALIZABLE | 9,072,015 |
| NON_REALIZABLE | 203,780 |
| RESIDUE | 659 |
| distinct RESIDUE `row` values | 659 (all distinct) |
| duplicate chi string within any single shard | **0** |

Every one of these numbers matches `FINAL_RESIDUE.md`'s claims exactly,
independently reproduced by a script that shares no code with `sweep49.py`,
`checkcert.py`, `certaudit.py`, or `fastverify.py`. Combined with §1.3's
theoretical concern, this is the direct evidence that whatever the
`ProcessPoolExecutor` collision risk is in principle, it produced no
detectable file-level damage over the sweep's whole 9,276,454-line output.

---

## 5. Summary table

| item | grade | severity | notes / recommended fix |
|---|---|---|---|
| A.1 row/certificate mismatch — catalog-decode consistency | **CONFIRMED** | — | 200k random + 20k real-row round trips, exact basis-order agreement |
| A.1 row/certificate mismatch — `todo`→`chi` binding | **CONFIRMED** | — | order-preserving indexing, verified by inspection + scale evidence |
| A.1 row/certificate mismatch — `wid` collision race | **DEFECT** | LOW, latent | real code property; 0 observed damage in 9,276,454 lines. **Fix**: derive `wid` from a stable per-process identity set by the pool initializer (e.g. `os.getpid()`-keyed), not from `job_index % workers`, or take a per-shard lock around the `open(...,'a')`/write/close. |
| A.2 unverified writes — REALIZABLE | **CONFIRMED** | — | unconditionally self-verifying by construction |
| A.2 unverified writes — NON_REALIZABLE | **DEFECT** | LOW | not inline-verified at write time; closed by 2 later + this review's 3rd independent re-check, 0 failures over 5,400+141 sampled. **Fix**: re-run `sum_i w_i V[i] == 0` (integer, exact) inside `_bfp_record` before returning, mirroring the `exact_bracket_signs` gate already used on the REALIZABLE side. |
| A.3 resumability — skip-if-done | **CONFIRMED** | — | |
| A.3 resumability — shard truncation | **CONFIRMED** | — | |
| A.3 resumability — buffered-write loss (the 141) | **DEFECT** | LOW, fully diagnosed | mechanism, blast radius, and repair all independently re-derived and re-verified; cannot misattribute, only omit. **Fix**: flush + fsync the certificate file handle once per row (simplest, some throughput cost), or reorder so `st[i] = how` is deferred until after the enclosing chunk's flush/fsync has completed for every row already written in that chunk. |
| A.4 omdecode round trip | **CONFIRMED** | — | see §1.1 |

**No defect found anywhere in this review can cause a wrong verdict to be
attributed to the wrong catalogue row, or a verdict to be written without
the specific guarantee that verdict's own code path claims to provide.**
The two real defects are both in the crash-recovery path, both
one-directional (loss/omission, never misattribution or corruption), and
one of them is the exact, already-known, already-repaired 141-row gap —
independently re-diagnosed and re-verified here down to the individual
row.

---

## Files

- `review_scratch/mycodec.py` — the reviewer's fifth independent
  implementation (colex order, Leibniz-expansion determinant, key codec,
  GP-relation/Gordan-term builder); stdlib only, imports nothing from this
  project.
- `review_scratch/codec_crosscheck.py` — §1.1 (task item A.4).
- `review_scratch/shard_scan.py`, `shard_scan.log`, `shard_scan_result.json`
  — §4; also emits `sample_realizable.jsonl` (22,501 records) and
  `sample_nonrealizable.jsonl` (5,400 records), the reservoir samples the
  companion `ai/omopen/REVIEW_FINAL_RESIDUE.md` review draws on.
- Companion review: `ai/omopen/REVIEW_FINAL_RESIDUE.md` and
  `ai/omopen/review_scratch4/` — Part B, the final agent's own verification
  claims.
