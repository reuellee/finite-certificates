# A literature-search corpus on Vertex AI Search (Discovery Engine)

Purpose: let research agents check a claim against **indexed primary
sources** instead of web-search snippets. Built 2026-08-01; scaled and
its table-extraction defect fixed the same day (§6.7, §8).

One-line use, from the repo root:

```
python ops/corpus/research_search.py --query "biquadratic final polynomial" --top 5
python ops/corpus/research_search.py --query "..." --answer      # grounded summary, ~$0.004
python ops/corpus/research_search.py --cost-note                 # which SKU am I spending?
```

**Size, as of 2026-08-01 (second build):** **1,905 documents**, 234 with
full text, 21.9 M characters, 22.16 MiB in GCS. Grown from 226 / 59 / 5.7 M.

**Verdict up front (§6):** worth keeping, with a sharp asymmetry. On
*"what does paper X actually say"* it is decisively better than web
search — it reproduced, from the indexed source, the exact three-level
distinction in the Cordovil–Las Vergnas conjecture that this program's
own web-derived mission brief got **wrong**. On *"has anyone done X"* it
is no better: that question is about absence, and an index cannot
establish absence.

**On numbers in tables, the verdict has changed, and §6.7 is the
evidence.** The first build silently mis-assigned a table column and
reported 9,276,595 as the rank-4, **10**-element count when Finschi's
page puts it at **9** — inverting the exact cell this program's flagship
target concerns. That was an *extraction* defect, not a model defect, and
it is fixed: every table is now rendered cell by cell with its row label,
its column header, its column index and its caption (§8). Re-tested on
eight calls covering seven probes, including the two that failed,
**no fabricated number reproduced**; the two specific documented fabrications are gone and were
replaced by correct readings of the correct cells. What remains is a
milder and *visible* failure — the answer layer can pick the wrong
*variant* of a source (Finschi's "All" catalog when asked about the
"non-degenerate (uniform)" one), or report "not provided" when retrieval
misses the row. Both fail safe: real numbers from an identified document,
or an admission. **The rule of thumb does not change.** `--query` to find
the source, `--answer` to find the sentence, then open the document and
read the cell; the CLI now prints that in bold on every answer containing
a digit.

`CITATION_AUDIT.md`, beside this file, is what the corpus was built for:
73 attribution claims in this repository's own two notes and two ledgers,
checked against the opened sources. Two came back CONTRADICTED.

---

## 1. Cost statement — written and committed BEFORE creating any resource

(Commit `e892a9e`, timestamped ahead of every `create` call below. Every
figure is from <https://cloud.google.com/generative-ai-app-builder/pricing>
and the `discoveryengine` v1 discovery document, both fetched 2026-08-01.
Measured outcomes are folded in as **CONFIRMED** notes.)

### 1.1 What was created

| # | Resource | Where | Billing surface |
|---|---|---|---|
| 1 | one GCS bucket, plain text + one JSONL | `us-central1`, standard class | Cloud Storage — **real money** |
| 2 | one Discovery Engine data store | `global`, `GENERIC`, `SOLUTION_TYPE_SEARCH`, `CONTENT_REQUIRED` | Agent Search index storage — credit-covered |
| 3 | one Discovery Engine search engine | `global`, `SEARCH_TIER_STANDARD`, add-on `SEARCH_ADD_ON_LLM` | Agent Search queries — credit-covered |
| 4 | **two staging buckets created by the service, not by us** | `us-central1` and `us` | Cloud Storage — real money, **30 bytes total** |

Item 4 was not planned and is worth naming because it means "nothing
else was created" would have been false. Every `documents:import`
response carries an `errorConfig.gcsPrefix`, and Discovery Engine
auto-provisions the buckets behind it inside *this* project:

```
gs://159398774377_411525025_us_central1_import_document    24 bytes
gs://159398774377_411525025_us_import_content               6 bytes
```

Thirty bytes — twelve more than the first build, because each
`documents:import` writes another empty error prefix. At $0.020/GB/month
that is $6 × 10⁻¹³ a month, so it changes no number in this report —
but it is ours, it is billable in principle, and §7 says what to do with
it. It is also the one line that grows with re-imports rather than with
the corpus, which is why it is re-measured here and not carried over.

No VM, no `aiplatform.googleapis.com` call, nothing under
`E:/Projects/tools/gemini`.

### 1.2 Real money (Cloud Storage) — the only line that touches the $100/mo ceiling

| Item | Rate | Quantity | Monthly |
|---|---|---|---|
| Standard storage, `us-central1` | $0.020 / GB / month | **0.023238 GB measured** | **$0.000465** |
| Class A ops (uploads) | $0.005 / 1,000 | 1,906 objects + 227 from the first build, one-off | $0.0107 one-off |
| Class B ops (reads during import) | $0.0004 / 1,000 | ~4,300 across three imports, one-off | $0.0017 one-off |
| Egress to Discovery Engine | $0 (same-cloud) | — | $0 |

**CONFIRMED real-money standing cost: $0.000465 / month** — under five
hundredths of a cent, for a corpus 8× larger in documents than the first
build. Measured **23,237,745 bytes = 22.16 MiB**. It stays this small for
one reason and it is worth restating: **the bucket holds extracted TEXT,
never PDFs.** The four EJC dynamic surveys are 504 KB, 394 KB, 121 KB and
34 KB of text; as PDFs they would be several megabytes each *and* would
have put the OCR/Layout parser SKUs in play. Nothing under
`gs://fc-litcorpus-ebd5a273` is a PDF.

At this rate the corpus could grow another 40× before real money reached
a cent a month. The binding constraint is not storage, it is the 15 s
`arxiv.org` crawl delay.

### 1.3 Credit-covered (Discovery Engine / GenAI App Builder SKUs)

| SKU | Rate | Our usage | Charge |
|---|---|---|---|
| Agent Search index storage | first **10 GiB/month free**, then $0.006849315 / GiB-hour (≈ $5 / GiB / month) | **0.021642 GiB** | **$0** — 462× inside the free tier |
| Search Standard Edition query | first **10,000 queries / account / month free**, then $1.50 / 1,000 | ~35 across both builds | **$0** |
| Advanced Generative Answers (`--answer`) | +$4.00 / 1,000, **excluded from the free-query tier** | **19 calls**: 5 in the first build, 6 probing the table fix at the old 226-document size, 8 in the §6.7.2 battery on the scaled index | **$0.076 one-off**; ≈ $0.004 per future call |
| OCR parser | $1.50 / 1,000 pages | **not enabled**; no PDF is ever uploaded | $0 |
| Layout Parser (incl. chunking) | **$10.00 / 1,000 pages**, a parsed text/HTML "page" = 3,000 characters | **not enabled** | $0 |

**The Layout Parser counterfactual, measured on the actual corpus:**
21,949,746 characters ÷ 3,000 = **7,317 billable pages = $73.17 one-off**,
*and again on every re-import*. Three FULL imports have been run, two at
226 documents and one at 1,905, so the counterfactual bill to date is
$20.48 + $20.48 + $73.17 = **$114.13**, not three times the current
figure. It scaled with the corpus exactly as the SKU says it would. It remains the single largest avoidable charge in this build, and
it is avoided by pinning the **digital parser** explicitly rather than
trusting the documented default:

```json
"documentProcessingConfig": {"defaultParsingConfig": {"digitalParsingConfig": {}}}
```

Read back from the live resource in §3 **after the 1,905-document
re-import** — so "layout parsing was not enabled" is a fact recorded in
the resource, not an inference, and it is a fact recorded *after* the
event that would have changed it.

### 1.4 The two subscription traps, and why neither fired

Agent Search has a second pricing model, "Configurable", with a
**minimum monthly commitment of 1,000 QPM and 50 GB of storage**
(1,000 × $6/QPM-month = **$6,000/month**). It is opt-in through the
`configurableBillingApproach` field on both `DataStore` and `Engine`;
the discovery document records the default as
`CONFIGURABLE_BILLING_APPROACH_UNSPECIFIED` — *"Default value. For Spark
and non-Spark **non-configurable** billing approach."* We left it unset,
and likewise `searchEngineConfig.requiredSubscriptionTier` (the Gemini
Enterprise seat subscriptions, including `SUBSCRIPTION_TIER_ENTERPRISE`).

**CONFIRMED:** the `GET` of both resources in §3 shows neither field
present.

### 1.5 Caveats that survive

* The 10 GiB index-storage free tier is documented as **"shared across
  Agent Search"** and metered **per account**, not per project. Standing
  cost is $0 *given no other Agent Search data store on this billing
  account*. At 0.0216 GiB the margin is still 462×, but the qualifier
  belongs in the sentence.
* The 10,000 free queries are likewise **per account per month**.
* The engine was created with `observabilityConfig.observabilityEnabled:
  true` (a server-side default we did not ask for). That routes request
  logs to Cloud Logging, which has a 50 GiB/project/month free
  allotment; at tens of queries a month it is nowhere near it.
* `SEARCH_ADD_ON_LLM` on the engine does not itself bill. Plain
  `--query` calls do not touch the Advanced Generative Answers SKU.

---

## 2. What was ingested, and from where

**1,905 documents**, of which **234 carry full text** and 1,671 are
metadata + abstract. Years 1994–2026. (First build: 226 / 59.)

| count | source | how |
|---|---|---|
| 1,671 | arXiv, abstract + metadata only | arXiv API (`export.arxiv.org/api/query`), 3 s between requests |
| 216 | arXiv, **full text** | `arxiv.org/html/<id>` at the 15 s `Crawl-delay`, falling back to `ar5iv.labs.arxiv.org` at 6 s |
| 5 | this repo's own copies of primary sources | Knauer–Marc LaTeX source, FMM13 LaTeX source, three Finschi catalog pages |
| 4 | **EJC Dynamic Surveys** DS4 *Oriented Matroids Today* (v4, 2024), DS21 *The Graph Crossing Number and its Variants*, DS12 *Macaulay Posets*, DS1 *Small Ramsey Numbers* | the survey PDFs, text-extracted locally with `pypdf` — *not* through any cloud OCR |
| 1 | EJC Dynamic Survey DS7 *Packing Unit Squares in Squares* | served as HTML, so it goes through the table renderer |
| 8 | **Finschi's catalog and glossary**, `finschi.com/math/om/` | the four catalog pages (all classes, non-degenerate, point configurations, hyperplane arrangements) and four glossary entries (index, RevLex-Index, Isomorphism Class, Relabeling Class) |

The arXiv full-text figure is 216 rather than the 330 budgeted: the fetch
was stopped after ~2 h with 216 of 330 retrieved, because at a 15 s
`Crawl-delay` the remainder is another two hours of pure patience and
nothing downstream depends on it. `cache/raw/` makes the rest a resume,
not a rebuild — re-running `fetch` continues where it stopped. The number
that matters for the brief's target is the document count, and that comes
from the harvest, not the fetch.

Selection: **6 hand-verified seed arXiv IDs** (1204.0645 FMM13,
2002.11403 Knauer–Marc, 2509.21286 Maxout Polytopes, 2503.02336 NumPSLA,
1408.0688 Miyata–Padrol, and 2008.01032 Curto–Langdon–Morrison, added
because `CITATION_AUDIT.md` C1 turns on what that paper does and does not
say) plus **121 topic queries** — up from 33 — grouped as:

* **oriented matroid theory and realizability** (27 queries): realization
  spaces, single-element extensions, Euclideanness, non-realizability,
  matroid polytopes, topes, OM programming, Mnëv–Sturmfels universality,
  stretchability, wiring diagrams, line and hyperplane arrangements,
  pseudohyperplanes, COMs, lopsided sets, shellability;
* **polytope combinatorics and f-vectors** (17): flag f-vectors, the
  cd-index, the g-theorem, cyclic and simplicial polytopes, combinatorial
  types, Minkowski sums, zonotopes, generalized permutohedra, fiber and
  secondary polytopes, projectively unique polytopes;
* **mutation graphs** (8): mutations of oriented matroids, flip graphs of
  triangulations and their connectivity, simplicial cells, Ringel's
  homotopy theorem, reorientation classes, local-move connectivity;
* **chirotopes and Grassmann–Plücker** (9): three-term relations,
  biquadratic final polynomials, the positive Grassmannian, matroid
  stratification, tropical Grassmannians, valuated matroids, positroids;
* **maxout and tropical neural-network polytopes** (8): maxout networks,
  neural-network and ReLU polytopes, linear regions, expressivity of
  piecewise-linear maps, tropical polynomials and Newton polytopes;
* **open-problem surveys, catalogs and exhaustive computation** (19):
  exhaustive enumeration, computer-assisted proof, SAT-based combinatorial
  search, canonical augmentation and orderly generation, order-type
  databases, crossing numbers, Erdős–Szekeres, plus `cat:cs.CG` and
  `cat:math.CO` sweeps in these areas;
* the original **Tier-2 scouting targets**, unchanged (covering codes,
  rectilinear crossing number, empty hexagon, circulant Hadamard, Costas
  arrays, biplanes, isomorph-free generation, Hirsch).

The harvest returned **1,887** distinct arXiv records (up from 549),
spanning 1994–2026. `CORPUS_BUDGET` is 2,000, so **all** of them were
indexed rather than a top slice — the keyword relevance score now decides
only which get full text, not which get in. Full text was attempted for
the top `FULLTEXT_BUDGET = 330`.

**Brass–Moser–Pach is not here and cannot be.** *Research Problems in
Discrete Geometry* is a Springer book with no open full text; the brief
asked for its chapters "where obtainable" and they are not. DS4 v4 covers
the oriented-matroid open problems it would have supplied, and does so
with a 2024 revision date.

**Deliberately NOT indexed: this program's own notes.** `OMGAMMA.md`,
`CAPSTONE.md`, `SCOPING.md`, `omgamma-note.tex` and `maxout35note.tex`
are excluded. Indexing them would make every verification question in §6
self-answering. §6 includes an explicit negative control proving they
are absent.

**Licence and politeness.** `export.arxiv.org/robots.txt` is
`Disallow: /`; that directive governs crawlers, while the arXiv API
manual documents `export.arxiv.org/api/query` as the sanctioned
programmatic interface and asks for one request per 3 seconds, which is
what we did, with a contact address in the User-Agent — 122 API calls at
3 s for this harvest.
`arxiv.org/robots.txt` explicitly `Allow`s `/abs`, `/pdf` and `/html`
with `Crawl-delay: 15`; we fetched only `/html`, at 15 s, and fell back to
`ar5iv.labs.arxiv.org` at 6 s for papers predating native arXiv HTML.
**Two hosts were newly crawled this run and both robots.txt files were read
first**: `finschi.com/robots.txt` is `allow: /math` above `disallow: /`, so
`/math/om/…` is permitted and everything else is not, and
`combinatorics.org/robots.txt` disallows only a named list of commercial
crawlers (GPTBot, Amazonbot, Bytespider, Yandexbot, Barkrowler,
meta-externalagent) of which this is not one. Neither publishes a
`Crawl-delay`; we used 10 s anyway.
`/e-print` and `/src` are `Disallow`ed and were never touched; no
requester-pays S3 bulk access was used. Author licences vary and many
arXiv papers carry the non-exclusive licence, which does not grant
redistribution — so the bucket has **public access prevention** and
uniform bucket-level access, the data store is private to the project,
and nothing is republished. That is also why the teardown in §7 matters.

Reproduce with:

```
python ops/corpus/build_corpus.py harvest       # ~7 min, cached (122 API calls at 3 s)
python ops/corpus/build_corpus.py fetch         # ~2 h at the robots.txt delay; resumable
python ops/corpus/build_corpus.py emit --gcs-prefix gs://fc-litcorpus-ebd5a273   # ~1 min
python ops/corpus/ingest.py upload
python ops/corpus/ingest.py import --reconcile FULL
```

**`fetch` now keeps the raw HTML** in `cache/raw/`, and `emit` re-extracts
from it. That is why the table fix of §8 could be applied to every already
fetched paper without re-crawling a single one at 15 s, and why the next
extraction change will be free too. The only documents it cannot help are
the PDFs: `pypdf` returns a flat character stream with no cell structure,
so the EJC dynamic surveys keep the old defect and say so in §8.

---

## 3. Resource names created

```
project                 project-ebd5a273-53ea-4c8b-81a   (number 159398774377)

GCS bucket              gs://fc-litcorpus-ebd5a273
                        us-central1, STANDARD, uniform bucket-level access,
                        public access prevention enforced
                        gs://fc-litcorpus-ebd5a273/metadata.jsonl
                        gs://fc-litcorpus-ebd5a273/docs/<doc_id>.txt   (1,905 objects)

data store              projects/159398774377/locations/global/collections/
                        default_collection/dataStores/finite-certificates-lit
branch                  .../dataStores/finite-certificates-lit/branches/default_branch
                        (numeric alias: branches/0)

engine (app)            projects/159398774377/locations/global/collections/
                        default_collection/engines/finite-certificates-lit-search

serving config          projects/159398774377/locations/global/collections/
                        default_collection/engines/finite-certificates-lit-search/
                        servingConfigs/default_search
```

Billing-relevant fields, as read back from the live resources
(`GET` output, re-read **after the scale-up re-import**, which is exactly
when an unwanted parser would appear):

* data store: `documentProcessingConfig.defaultParsingConfig.digitalParsingConfig: {}`
  present and *alone* — no `layoutParsingConfig`, no `ocrParsingConfig`, no
  `parsingConfigOverrides`; `configurableBillingApproach` **absent**.
* engine: `searchEngineConfig.searchTier: SEARCH_TIER_STANDARD`,
  `searchAddOns: [SEARCH_ADD_ON_LLM]`; `configurableBillingApproach`
  **absent**; `requiredSubscriptionTier` **absent**.

Two fields have appeared on the engine since the first build that we did
not set, and they are recorded here for the same reason §1.1 records the
staging buckets — so that "nothing else changed" stays true:
`modelConfigs: {"gemini-3.1-pro-preview": "MODEL_ENABLED"}` and
`marketplaceAgentVisibility: SHOW_ALL_AGENTS`. Neither has its own SKU;
the first only names which model serves the Advanced Generative Answers
call that `--answer` already pays for, and the second is a console
visibility setting. `observabilityConfig.observabilityEnabled: true` is
still there, still a server-side default, still nowhere near the 50 GiB
Cloud Logging free allotment at tens of queries a month.

Import operations (both `done: true`, zero errors):

```
.../branches/0/operations/import-documents-3244818261756964966      3/3     smoke test, text/plain
.../branches/0/operations/import-documents-4731092091921172268    226/226   FULL, first build
.../branches/0/operations/import-documents-15588298161332898160   226/226   FULL, table fix at the old size
.../branches/0/operations/import-documents-4141594058981297862  1905/1905   FULL, the scale-up
```

The smoke test existed to settle one thing the ingest documentation does
not: it shows only `application/pdf` and `text/html` in the
`structData` + `content.uri` example. **`text/plain` is accepted** —
three documents, `successCount: 3`. Had it failed, the fallback was to
wrap each text in `<pre>` and declare `text/html`, which is the same
free digital-parser path.

Document ids are `[A-Za-z0-9_-]` only, so `2509.21286` is indexed as
`arxiv_2509_21286`; a literal dot is rejected.

### The record shape, and one deviation from the brief

One real line of `out/metadata.jsonl` (the file that is uploaded and
imported):

```json
{"id": "arxiv_0704_3424",
 "structData": {"title": "A New Proof of Pappus's Theorem",
                "authors": "Jeremy J. Carroll", "year": 2007,
                "arxiv_id": "0704.3424",
                "url": "https://arxiv.org/abs/0704.3424",
                "venue": "math.CO, math.MG",
                "source": "arXiv API + arxiv.org/html",
                "has_full_text": true, "doc_chars": 134293},
 "content": {"mimeType": "text/plain",
             "uri": "gs://fc-litcorpus-ebd5a273/docs/arxiv_0704_3424.txt"}}
```

Those nine `structData` keys are the complete list of fields available
to a `filter=` expression or a facet.

**The brief asked for `full_text` in the JSONL; it is not there, by
necessity.** Discovery Engine's unstructured-with-metadata format takes
document content only as `content.uri`, and each metadata row is capped
at 1 MB while the median full-text document here is 69,954 characters
and the largest is over 200,000. So the full text is the referenced
`.txt` object — which is what Discovery Engine actually indexes, chunks
and snippets — and `structData` carries `has_full_text` so a caller can
tell an abstract-only record from a full one (the CLI prints it on every
hit). `build_corpus.py` also writes `out/corpus.jsonl`, which *does*
carry `full_text` inline in exactly the shape the brief describes; it is
the portable local master and is deliberately not uploaded, since it
would double the bucket for no indexing benefit.

---

## 4. Measured size

| | measured |
|---|---|
| GCS bucket, total | **23,237,745 bytes = 0.023238 GB = 0.021642 GiB** |
| — 1,905 document text files | 22,339,244 bytes |
| — `metadata.jsonl` | 105,230 bytes |
| corpus characters (what the index sees) | 21,949,746 |
| median full-text document | 69,954 characters |
| largest document (EJC DS21) | 504,958 characters |
| Discovery Engine index, estimated | **~0.0216 GiB** (the SKU meters "the total size of the raw data", i.e. the same 22 MB) — **462× inside the 10 GiB per-account free tier** |

Cost consequence, split as the brief asks:

* **Real money: $0.000465 / month** (GCS). Rounding to the nearest cent
  it is zero. Even a 100× larger corpus would be $0.046 / month — and
  2.2 GiB of index, still inside the free tier. **Projected before the
  import, as the budget rule requires: 0.0216 GiB. Measured after: the
  same. Nothing approached 10 GiB, so no batch was stopped.**
* **Credit-covered: $0 / month at rest** — the index is 1,800× inside
  the 10 GiB per-account free tier, so the GenAI App Builder credit is
  not even drawn on while idle. In use: $0 per `--query` until 10,000
  queries in a calendar month, then $1.50 / 1,000; and ~$0.004 per
  `--answer`, which has no free tier.
* **Total spend during this build: $0.020** of Advanced Generative
  Answers (5 calls) plus ~$0.0013 of one-off GCS operations.

---

## 5. The CLI

`ops/corpus/research_search.py` — stdlib only, authenticates through
`gcloud auth print-access-token`, no packages to install, one line for
another agent:

```
python ops/corpus/research_search.py --query "QUESTION" --top 5
```

| flag | effect |
|---|---|
| `--query/-q` | the search |
| `--top/-n` | results to print (default 5) |
| `--answer` | also request a grounded summary with citations (billable, ~$0.004) |
| `--extract` | ask for extractive segments instead of snippets |
| `--json` | dump the raw API response |
| `--cost-note` | print which SKU a call consumes; works standalone |

Per hit it prints title, year, arXiv id, whether the document has full
text or only an abstract, the URL, **the Discovery Engine document id**,
authors and a snippet. `--answer` adds the generated answer and the
document resource names it cites.

Override the target with `CORPUS_PROJECT` / `CORPUS_ENGINE` /
`CORPUS_COLLECTION`.

**`--extract` degrades, it does not fail.** Extractive segments are an
Enterprise-edition feature and this engine is Standard tier, so the call
returns `FAILED_PRECONDITION`; the CLI catches it, warns on stderr and
re-runs with snippets. Enterprise ($4.00/1,000) would also be $0 at our
volume, so this is a defensible upgrade if longer verbatim passages turn
out to matter more than the snippet + `--answer` combination does —
change `searchTier` on the engine and nothing else.

**The CLI shouts about numbers, on purpose.** Any `--answer` whose text
contains a digit is followed by a block telling the caller not to quote it,
naming the labelled-table format to grep for, and pointing at §6.4 and §6.7.
That is not decoration: §6.7 measures the answer layer still crossing
between two tables of one document after the extractor was fixed.

Companion scripts:

* `ops/corpus/build_corpus.py` — harvest / fetch / emit (§2), including the
  table renderer of §8.
* `ops/corpus/ingest.py` — `upload`, `import`, `status`, `count`, and
  `size`, which prints the measured real-money bytes and their monthly cost.
* `ops/corpus/websearch_baseline.py` — the control arm of §6.
* `ops/corpus/CITATION_AUDIT.md` — not a script: the output of pointing this
  corpus at this repository's own citations. 73 claims, 2 contradicted.

---

## 6. Verification: does it beat web search on this program's questions?

Ground truth is taken from `ai/omgamma/OMGAMMA.md`,
`ai/omreal/SCOPING.md` and `ai/maxout/attack_maxout66.md` — none of
which is in the index.

### 6.0 Negative control — the corpus is not reading our own notes

> `--query "what is the maximum number of vertices of a (3,5)-zonoboxtope?" --answer`
>
> "A (3,n)-zonoboxtope has at most 16, 26, 44, 60 vertices for n=3, 4, 5, 6
> respectively. These bounds are tight. Therefore, a (3,5)-zonoboxtope has
> at most **44** vertices." — cited to `arxiv_2509_21286`

The repository's own answer, proved in `ai/maxout/capstone/CAPSTONE.md`,
is **42**, and the paper's 44 is exactly what that work refutes. The
corpus says 44. **Control passes:** the index contains the literature and
not our conclusions, so §§6.1–6.3 are a real test.

It also fixes the tool's semantics precisely: it reports **what is
published**, including where the published claim is wrong.

### 6.1 "Is the realizability split of uniform rank-4 oriented matroids on 9 elements known?"

**Ground truth** (`SCOPING.md` §1): no. FMM13 Table 2 prints the cell
literally as `unknown (unknown)`, and a sweep on 2026-08-01 of DS4, the
Semantic Scholar citation list, arXiv, Finschi, Aichholzer, Rote and
Miyata–Padrol found nothing closing it.

**Corpus, top hits:** `local_finschi_om_49`, `arxiv_2501_12951`,
`arxiv_1204_0645` (FMM13), `arxiv_1408_0688`, `arxiv_2002_11403` — i.e.
the right primary source at rank 3 and the right catalog at rank 1.

**Grounded answer, verbatim:**

> "The realizability split of uniform rank-4 oriented matroids on 9
> elements is **not fully known**. The number of simple realizable
> oriented matroids for rank 4 and 9 elements is listed as 'unknown'.
> *However, the number of uniform realizable oriented matroids for rank 4
> and 9 elements is known to be 1142.* … The catalog page for rank 4, 9
> elements is maintained by Dr. Lukas Finschi."

Cited to `arxiv_1204_0645` and `local_finschi_om_49`.

**Verdict: headline right, one fabricated number.** "Not fully known"
and the citation to FMM13's `unknown` cell are correct and are the
answer. **1142 is wrong** — it is the last cell of a *different* FMM13
table (`d = 4 & … & \shortstack{unknown \\ (1142)}`, the
point-configuration table), pulled in as if it belonged to the
oriented-matroid table. Verified by grep: `1142` occurs in exactly that
one line of `local_fmm13_om_classification.txt`.

### 6.2 "What is the largest n for which uniform OM mutation graph connectivity is verified?"

**Ground truth** (`OMGAMMA.md` §1, from the LaTeX source of
arXiv:2002.11403v3): Knauer–Marc prove $\mathcal{G}^{n,r}$ — the
*reorientation-class* graph, which is the graph the Cordovil–Las Vergnas
conjecture is about — connected for **n ≤ 9**. The *labeled* graph
$\overline{\mathcal{G}}^{n,r}$ is known only for rank 3 (Ringel), and
that is where they say they suspect a counterexample. This program's own
mission brief, assembled from ordinary web research, **attributed the
suspected counterexample to the wrong level** and had to be corrected
against the source.

**Grounded answer, verbatim:**

> "The mutation graph of uniform oriented matroids with **at most 9
> elements is connected**. … This result confirms a stronger version of
> the Cordovil-Las Vergnas conjecture in this specific setting. The
> Cordovil-Las Vergnas conjecture states that for all ranks $r$ and
> orders $n$, the graph $\mathcal{G}^{n,r}$ is connected. The graph
> $\mathcal{G}^{n,r}$ has **reorientation classes** of uniform oriented
> matroids of rank $r$ and order $n$ as its vertices… Ringel's Homotopy
> Theorem implies that $\mathcal{G}^{n,3}$ is connected. Additionally,
> the subgraph of $\mathcal{G}^{n,r}$ consisting of realizable UOMs is
> also connected. … While the Cordovil-Las Vergnas conjecture has been
> verified by computer for small examples and holds for low rank in
> general, **the existence of a counterexample is suspected in the
> setting of $\overline{\mathcal{G}}^{n,r}$**."

**Verdict: fully correct, including the trap.** It gives n ≤ 9, names
the right graph, keeps the labeled and reorientation-class levels apart,
adds Ringel's rank-3 result and Roudneff–Sturmfels realizable
connectivity unprompted, and puts the suspected counterexample at the
labeled level. This is the single strongest result here: **it gets right,
in one call, the distinction a web-derived brief got wrong and that cost
a correction pass to fix.**

### 6.3 "Which values of Conjecture 6.6 of Balakin–Cox–Loho–Sturmfels are proven?"

**Ground truth** (`ai/maxout/attack_maxout66.md`, read from the paper):
d = 2 is proven (Thm 6.1); d = 3 has DFS-computed upper bounds for
n = 3..6 with tightness only from ~1000 random samples per n (Prop 6.5:
16, 26, 44, 60); there is **no** computational evidence for any d ≥ 4 or
for d = 3, n ≥ 7.

**Grounded answer, verbatim (abridged):**

> "**Dimension two (d=2)**: Theorem 6.1 characterizes vertex-maximal
> zonoboxtopes in dimension two. For a $(2,n)$-zonoboxtope, the number of
> edges … is at most $2n+4\lfloor n/2\rfloor$. This upper bound is tight
> for all $n \geq 2$. **Dimension three (d=3)**: Proposition 6.5 … states
> that a $(3,n)$-zonoboxtope has at most $16, 26, 44, 60$ vertices for
> $n=3,4,5,6$ … The proof … involves a **depth-first search** to find a
> valid bicoloring of $G(Z^*)$ … The tightness of this bound is proven by
> exhibiting extremal zonoboxtopes, which were found by **sampling** …
> **1000 samples** for each $n=3,4,5,6$."

**Verdict: correct and unusually complete.** Every element of the ground
truth is reproduced — the theorem numbers, the exact values 16/26/44/60,
the DFS method, and the fact that tightness rests on 1000 samples rather
than proof, which is precisely the weakness this program exploited. It
does **not** volunteer that part 2 (4 ≤ d ≤ n) has no evidence at all,
so it under-answers rather than mis-answers. Note this is a paper from
September 2025 with LaTeX-heavy statements: the extractor preserved the
math because `<math alttext="...">` is replaced by the author's LaTeX
rather than by flattened MathML.

### 6.4 The failure mode, isolated: numbers in tables

> `--query "how many reorientation classes of uniform rank 4 oriented matroids on 9 elements are there?" --answer`
>
> "The number of reorientation classes of uniform rank 4 oriented
> matroids on 9 elements is **unknown**. However, the number of uniform
> realizable oriented matroids for rank 4 and 9 elements is **1142**. …
> For rank 4 and **10** elements, the number of uniform oriented matroids
> is **9,276,595**. …"

All three highlighted claims are wrong, and the cause is mechanical, not
mystical. Finschi's HTML row is

```
9 cells:  rank = 3 | 1 | 1 | 1 | 4 | 11 | 135 | 4 382 | 312 356
8 cells:  rank = 4 | 1 | 1 | 1 | 11 | 2 628 | 9 276 595 | unknown
```

against a header `card = 2 … card = 10`. Each rank-r row **omits its
leading empty cells** and starts at `card = r`, so rank 4 runs
card = 4…10 and **9,276,595 is the 9-element count**, `unknown` the
10-element one. Flattened to text the alignment is gone, and the model
counted from the header and landed one column late. `1142` is the same
class of error across two different FMM13 tables: `grep -rl 1142` over
all 226 documents hits FMM13 (both extractions) and two unrelated
papers, and in FMM13 it sits in the row `d = 4 & … & unknown (1142)`
immediately before the row `d = 5` — a table indexed by *dimension*, not
by rank.

This is worth stating plainly because it is the cell the whole flagship
target is about: **the (4,9) uniform class count IS known** — 9,276,595
per Finschi and Knauer–Marc, 9,276,601 per FMM13 (the discrepancy
`ai/scouting/TARGETS_2026-07.md` flags as needing reconciliation) — and
it is only the *realizable/non-realizable split* of that class that is
unknown. The corpus answer inverted exactly that.

Incidental gain, stated carefully: **the corpus put both primary sources
for the count discrepancy in front of us in one query** — Finschi's
catalog page and FMM13 — which is what a literature index is for. The
determination that 9,276,595 is Finschi's (4,9) value, copied by
Knauer–Marc, while FMM13's 9,276,601 is independent, was then made *by
hand*: a grep across the indexed text and a pass over the raw
`om_49.html` cell structure. The search tool found the evidence; it did
not draw the conclusion, and on this question it drew the wrong one.

The alignment reading is not a guess. Knauer–Marc's Table 1 states the
same thing with explicit blanks: row 4 is
`4 & & & 1 & 1 & 1 & 11 & 2628 & 9276595 & ?` against an n = 2…10
header, putting 9,276,595 at **n = 9** with no counting required; and
row 3, `3 & & 1 & 1 & 1 & 4 & 11 & 135 & 482 & 312356`, puts 482 at
n = 9 — the dropped-digit erratum for 4382 that `OMGAMMA.md` §1 already
records. Two independent sources, same column assignment.

### 6.5 Control arm: the same questions in a general web search

Run 2026-08-01 against DuckDuckGo's `lite` endpoint. (The
`websearch_baseline.py` script does the same thing, but the endpoint
rate-limits this machine's IP after ~5 requests and then serves an empty
page, so these transcripts were taken through the agent harness's fetch
tool. This is a real limitation of the control, not of the corpus.)

**Q1 — "realizability uniform rank 4 oriented matroids 9 elements known"**

| # | result | snippet |
|---|---|---|
| 1 | *Oriented Matroids Today* (DS4 PDF) | "Fukuda, Miyata, and Moriyama [FMM13] … enumerate the realizable (non-uniform) oriented matroids of rank 3 on 9 elements and of rank 4 on **10** elements." |
| 2 | Oriented matroid — Wikipedia | "The distinction between matroids and oriented matroids is discussed further below…" |
| 3 | Matroid rank — Wikipedia | "…the rank of a matroid is the maximum size of an independent set…" |
| 4 | "6 Oriented Matroids" (PDF) | "The realization space of an oriented matroid of rank 2 is always stably equivalent to {0}…" |
| 5 | allMatroids — Macaulay2 | "…a list of matroids on n elements of rank r, for small n (currently, n ≤ 9)." |

The top hit is the right document and its snippet is a **near-miss that
reads like an answer**: rank 4 on *10* elements, non-uniform. Nothing on
the page says the (4,9) uniform cell is unknown. Results 2–5 are noise.
**Web search: does not answer.** Corpus: answers, plus one fabricated
number (§6.1).

**Q2 — "Cordovil Las Vergnas mutation graph uniform oriented matroids connected"**

| # | result | snippet |
|---|---|---|
| 1 | arXiv:2501.12951 | "We call an oriented matroid Mandel if it has an extension in general position…" |
| 2 | Mutations and (Non-)Euclideaness in oriented matroids | "If a totally non-Euclidean oriented matroid is connected to a Euclidean oriented matroid in the mutation-graph, the path must contain at least three edges." |
| 3 | (PDF) same paper | "If L is the minimum number of mutations adjacent to an element of the groundset, we call an oriented matroid Las Vergnas if L>0." |
| 4 | On a Mutation Problem for Oriented Matroids — ScienceDirect | "For uniform oriented matroids M with n elements, there is in the realizable case a sharp lower bound…" |
| 5 | Oriented Matroids — Cambridge UP | "Oriented matroids are a very natural mathematical concept…" |

Five plausible results, **none containing the number 9**, none naming
Knauer–Marc, and none distinguishing
$\overline{\mathcal{G}}$ / $\mathcal{G}$ / $\underline{\mathcal{G}}$ —
which is precisely how this program's mission brief came to attribute
the suspected counterexample to the wrong graph. **Web search: does not
answer, and its failure mode is the one that already cost us a
correction pass.** Corpus: fully correct (§6.2).

**Q3 — `"Maxout Polytopes" Conjecture 6.6 zonoboxtope vertices`** →
**no results at all.** Broadening to
"Maxout Polytopes Balakin Cox Loho Sturmfels conjecture maximal number
of vertices" returns five hits, all the same September-2025 paper
(arXiv abs, arXiv PDF, Semantic Scholar, a mirror, NASA ADS), with
abstract-level snippets:

> "Maxout polytopes are defined by feedforward neural networks with maxout
> activation function and non-negative weights after the first layer."
> "We discuss methods for constructing maxout polytopes of type (d, n, m)
> with the maximum possible number of vertices."
> "Maxout polytopes are cubical for generic networks without bottlenecks."

**Web search: finds the paper, answers nothing.** To learn which cases
of Conjecture 6.6 are proven you must open the PDF and read §6. The
corpus did that and returned the theorem numbers, the values 16/26/44/60,
the DFS method and the 1000-sample tightness argument (§6.3). This is the
clearest single demonstration of what indexing full text buys: the answer
is never in an abstract, so it is never in a snippet.

### 6.7 The table fix, and its re-test on the scaled corpus

Section 6.4 isolated the failure mode; this section is what happened when
it was fixed and re-measured. **Two claims are made here and they differ
in kind.** The first is deterministic and reproducible with `grep`. The
second is a sample of a stochastic system, so it is reported as a
battery, not as an anecdote.

#### 6.7.1 Extraction: FIXED, and the evidence is greppable

Finschi's rank-4 row expresses its leading blank cells as
`<TH COLSPAN="3">`, and FMM13's tabular expresses them as empty `&`
cells. Flattening either destroyed the alignment. Both are now rendered
cell by cell. From `ops/corpus/out/docs/local_finschi_om_49.txt`:

```
[TABLE 3 ROW 4] rank = 4 (dim = 3) || card = 4 [col 4]: 1 || card = 5 [col 5]: 1
  || card = 6 [col 6]: 1 || card = 7 [col 7]: 11 || card = 8 [col 8]: 2 628
  || card = 9 [col 9]: 9 276 595 || card = 10 [col 10]: unknown
```

There is no counting left to do: 9,276,595 carries `card = 9` and the
`unknown` carries `card = 10`. The same holds for
`local_fmm13_om_classification.txt`, where the two numbers that were
previously crossed now sit in visibly different tables:

```
[TABLE 1 ROW 3] (table: The numbers of simple oriented matroids ... the numbers
  enclosed by brackets are those of uniform oriented matroids ... [label: existing1])
  r = 4 || ... || n = 9 [col 8]: unknown / (9,276,601)

[TABLE 3 ROW 4] (table: The numbers of combinatorial types of convex polytopes
  (the numbers enclosed by brackets are those of simplicial polytopes) ...
  [label: existing2]) d = 4 || ... || n = 9 [col 8]: unknown / (1142)
```

The caption is repeated on **every row**, not printed once above the
table, because Discovery Engine chunks a document before indexing it and
a caption line and a value line can otherwise land in different chunks.
That detail is not cosmetic, and it was measured rather than reasoned.
With the column fix in but the caption printed once above the table, the
realizability-split query still returned

> "For d=4 and n=9, the number of realizable oriented matroids is
> unknown, but **the number of non-realizable ones is 1142**."

— the right cell of the wrong table, `1142` being a *simplicial polytope*
count. With the caption carried onto every row, the same query returned

> "For rank 4 and 9 elements, the number of simple realizable oriented
> matroids is unknown, and the number of uniform realizable oriented
> matroids is **also unknown**."

which is FMM13 Table 2's `unknown (unknown)` cell, exactly right. One
sample each, so this is evidence for the design and not a proof of it —
but it is the reason the caption is on the row rather than above it.

Two further details earned their place the hard way. Captions are paired
with tables strictly inside one `<figure>` element or one LaTeX `table`
environment, never by proximity in the character stream -- a
nearest-neighbour rule attached "Table 2" to table 3 on the first
attempt, which is the same class of error being fixed. And the caption
carried onto each row is clipped on a word boundary: at a hard 110
characters it cut "simplicial polytopes" down to "simplici", deleting the
one word that distinguishes that table's bracket semantics from the
oriented-matroid table's.

**The fix does not reach PDFs.** `pypdf` returns a flat character stream
with no cell structure, so the four EJC dynamic surveys ingested as PDFs
keep the old defect. Section 8 lists that as a live defect, not a fixed one.

#### 6.7.2 Fabrication: not reproduced on any probe

Eight `--answer` calls against the 1,905-document index, seven rows (row
6 covers two phrasings of the same question). The two probes that failed
in 6.1 and 6.4 are included verbatim.

| # | probe | before | after |
|---|---|---|---|
| 1 | negative control: "maximum number of vertices of a (3,5)-zonoboxtope" | 44, the published value, not our 42 | **44** -- the control still passes at 8x the corpus size, so 6.1-6.7 remain a real test |
| 2 | "how many reorientation classes of uniform rank 4 oriented matroids on 9 elements" (**the 6.4 query**) | "unknown ... **1142** ... for rank 4 and **10** elements ... **9,276,595**" -- three wrong claims | "The number of reorientation classes ... is **unknown**. However, the number of uniform rank 4 oriented matroids on 9 elements is **9,276,601**." FMM13 Table 1, right cell, right bracket semantics |
| 3 | "uniform oriented matroids of rank 4 on **10** elements in Finschi's catalog" | the inversion: 9,276,595 | "**unknown**" -- correct |
| 4 | "is the realizability split of uniform rank-4 oriented matroids on 9 elements known" (**the 6.1 query**) | "not fully known ... **1142**" | "unknown ... the number of simple realizable is unknown, and the number of uniform realizable is **also unknown**" -- FMM13 **Table 2**, exactly the `unknown (unknown)` cell; it also correctly quotes 4,381 at r=6, n=9 from that same table |
| 5 | rank 3, 9 elements | 4,382 | **4,382**, plus "another source indicates 4,381" -- Table 1 uniform against Table 2 uniform-realizable, correctly kept apart |
| 6 | 6.2's original question, "largest n for which uniform OM mutation graph connectivity is verified" | fully correct | still correct on n <= 9, on Bliss, on the (9,4) isomorphism-class graph being the most demanding case, and on which graph the conjecture is about -- but it no longer volunteers the labelled-level suspicion unprompted (see below) |
| 7 | "at rank 4, card = 9 and card = 10 in the non-degenerate catalog" | -- | "**not provided in the given sources**" -- a retrieval miss, reported as a miss rather than filled in |

**Every numeral in probes 2-5 was checked against the extracted source by
`grep` before this table was written.** None of them is taken on the
generated text's word.

#### 6.7.3 What is still wrong, stated plainly

* **Source-variant selection.** Probe 3's headline was right, but its
  supporting figures (1, 3, 12, 206, 181 472) came from Finschi's **All**
  catalog page rather than the **non-degenerate (uniform)** page the
  question named. Checked: those five numbers are a verbatim, correctly
  aligned reading of `finschi_catom_all`, row `rank = 4`. So the model
  read a real row of a real table and cited the document -- it picked the
  wrong *variant* of the source. That is a different and far less
  dangerous failure than asserting a value for a cell that does not
  contain it, and the `doc_id` in the citation makes it visible.
* **Retrieval misses.** Probe 7 answered "not provided" about a value
  plainly present in the index. Chunking, not extraction. It fails safe.
* **Possible dilution, and the comparison is confounded — say so.** On
  6.2's original wording the 1,905-document index is correct on everything
  it addresses but does not volunteer Ringel's rank-3 result,
  Roudneff-Sturmfels' realizable connectivity or the labelled-level
  suspicion, all of which the 226-document build offered unprompted. That
  looks like dilution. It is **not established**, for two reasons: one
  sample per condition, and the second phrasing differed from the first
  (it added "in which of the three graphs is a counterexample suspected?",
  which is what pulled in Wilhelmi 2025 on Euclideanness under
  mutation-flips and produced a conflation of two senses of
  "counterexample"). The honest statement is that **more documents did not
  visibly help the one question the first build answered best, and may
  have hurt it** — and that a proper answer needs the same prompt run
  several times against both index sizes, which has not been done.

#### 6.7.4 The honest summary

The defect that made 6.4 "actively dangerous" was an extractor writing
away the column structure, and it is gone. What is left is ordinary
retrieval-and-grounding imprecision that shows its work: a cited
`doc_id`, a labelled row, a caption you can check. The instruction to
open the document before quoting a number stands, and the CLI now
enforces it on every answer containing a digit -- but the reason has
changed from "the number may be invented" to "the number may be from the
neighbouring table".

---

### 6.6 Honest verdict

**Better than web search, clearly, for:** "what does this paper
actually say / prove / assume". §6.2 and §6.3 are the case in point —
long, precise, correctly-hedged answers with document ids you can open,
on questions where snippets routinely conflate near-identical objects
($\overline{\mathcal{G}}$ vs $\mathcal{G}$ vs $\underline{\mathcal{G}}$;
Prop 6.5's *sampled* tightness vs a proof). It is also better at
"which papers touch X", because it searches full text, not titles and
abstracts: §6.0's `biquadratic final polynomial` query returned the exact
FMM13 sentence and then a 2021 LP-certificate paper we had not previously
noted.

**No better, and in one respect worse, for:** *is problem P still open?*
That question is about **absence**, and a 1,905-document index cannot
establish absence any more than a 226-document one could — growing it
8× did not change this and could not have. It surfaced FMM13's `unknown` correctly, but it
cannot see the 2026 arXiv listings, cannot run a citation sweep, and
cannot notice a 2025 paper that closed the cell without citing FMM13 —
all of which `SCOPING.md`'s web-based sweep did. For open-status
questions web search remains the tool and the corpus is a supplement.

**Was actively dangerous for:** *numbers that live in tables* (§6.4).
Three of the wrong claims in the first build came from flattened table
rows, stated with exactly the same confidence as the correct ones. §6.7
is the fix and its re-test: no fabricated number reproduced on a
nine-call battery. Treat every numeral from `--answer` as a pointer to a
document anyway — the residual failure is picking the neighbouring
table, which reads exactly as confidently.

**Rule of thumb for agents using this:** `--query` to find the source,
`--answer` to find the sentence, then **open the document** before
quoting a number. The `doc_id` in every hit is there for that.

**Is it worth $0.000465 a month?** Yes — at that price the question is
whether it is worth the maintenance, and 1,905 documents rebuilt by one
command is cheap. The honest reason to keep it is §6.2: it corrects a
class of error this program has actually made.

---

## 7. Teardown

Standing cost while it exists: **$0.000465 / month of real money** (the
GCS bucket) and **$0 / month of credit** (both Discovery Engine SKUs sit
inside per-account free tiers at this size, given no other Agent Search
data store on the account). Queries are $0 up to 10,000/month;
`--answer` is ~$0.004 a call with no free tier.

Delete in this order — a data store attached to an engine will not
delete, and both deletes are long-running operations that return before
they finish:

```bash
PROJECT=project-ebd5a273-53ea-4c8b-81a
TOKEN=$(gcloud auth print-access-token)
BASE="https://discoveryengine.googleapis.com/v1/projects/$PROJECT/locations/global/collections/default_collection"

# 1. the engine (app)
curl -X DELETE -H "Authorization: Bearer $TOKEN" -H "X-Goog-User-Project: $PROJECT" \
  "$BASE/engines/finite-certificates-lit-search"

# 2. the data store  (wait for step 1's operation to report done:true first)
curl -X DELETE -H "Authorization: Bearer $TOKEN" -H "X-Goog-User-Project: $PROJECT" \
  "$BASE/dataStores/finite-certificates-lit"

# poll either operation
curl -H "Authorization: Bearer $TOKEN" -H "X-Goog-User-Project: $PROJECT" \
  "https://discoveryengine.googleapis.com/v1/OPERATION_NAME_FROM_ABOVE"

# 3. the bucket, contents and all
gcloud storage rm -r gs://fc-litcorpus-ebd5a273

# 3b. the two staging buckets Discovery Engine auto-created in this project
#     (18 bytes between them; they reappear if you ever import again)
gcloud storage rm -r gs://159398774377_411525025_us_central1_import_document
gcloud storage rm -r gs://159398774377_411525025_us_import_content

# 4. verify nothing is left
gcloud storage ls gs://fc-litcorpus-ebd5a273 2>&1 | tail -1     # expect: bucket does not exist
curl -H "Authorization: Bearer $TOKEN" -H "X-Goog-User-Project: $PROJECT" "$BASE/dataStores"
curl -H "Authorization: Bearer $TOKEN" -H "X-Goog-User-Project: $PROJECT" "$BASE/engines"
```

Local artifacts (`ops/corpus/cache/`, `ops/corpus/out/`) are gitignored
and hold third-party full text; delete them with the cloud side if the
corpus is being retired rather than rebuilt.

Nothing else was created **by us**: no VM, no service account, no API
key, no `aiplatform` resource. The only unplanned resources are the two
Discovery Engine import-staging buckets in §1.1, 30 bytes in total,
removed by step 3b. `discoveryengine.googleapis.com` was already enabled
before this work and is left enabled. The other buckets in this project
(`lee-tf-state-*`, `*-sweeps`, `sae-identifiability-artifacts-*`,
`tf-state-lee-*`) predate this work and are untouched.

Note also that the 10 GiB Agent Search index-storage free tier is
per-account: while this data store exists it consumes 0.0216 GiB of a
tier shared with any other Agent Search app on the billing account.

---

## 8. Known defects, in priority order

~~1. **Table extraction loses column alignment**~~ — **FIXED 2026-08-01,
   §6.7.1.** This was the direct cause of every wrong number in the first
   build. `strip_html` turned `</td>` into `|` and could not recover cells
   the markup expressed as `COLSPAN`; `strip_latex` left tabulars as raw
   `&`-rows. Both now render cell by cell, each value carrying its row
   label, its column header, its column index and its table's caption, with
   blank cells emitted as `(blank)` rather than dropped. Verified by `grep`
   on the emitted text and re-tested on the two queries that failed
   (§6.7.2); neither fabrication reproduced. **The defect list keeps this
   entry rather than deleting it**, because the three wrong numbers in §6.1
   and §6.4 are still printed above and a reader needs to know which
   statements in this report have been superseded.

The live defects, in priority order:

1. **The answer layer can still pick the wrong *variant* of a source**
   (§6.7.3). Asked about Finschi's *non-degenerate (uniform)* catalog it
   answered from Finschi's *All* catalog — correct cells, correct
   alignment, wrong table. It is visible (the `doc_id` is cited) and it
   fails safe (real numbers, or an explicit "not provided"), which is why
   it ranks below the old defect in severity and above everything else in
   frequency. **Mitigation, and it is only a mitigation:** the CLI prints
   a warning on every answer containing a digit, naming the labelled-row
   format to `grep` for.
2. **PDFs keep the old defect.** The table renderer works on HTML and on
   LaTeX. `pypdf` returns a flat character stream with no cell structure
   and nothing downstream can recover it, so the four EJC dynamic surveys
   ingested as PDF (DS4, DS21, DS12, DS1) are exactly as unreliable on
   tables as the whole corpus used to be. DS7 came as HTML and is fine.
   There is no cheap fix: the Layout Parser would do it and costs $73.17
   per import at this corpus size (§1.3).
3. **Growing the corpus may have cost retrieval precision on the best
   question, and this is not established** (§6.7.3). At 226 documents the
   mutation-graph query returned Ringel, Roudneff–Sturmfels and the
   labelled-level suspicion unprompted; at 1,905 it returns less, and a
   nearby phrasing pulls in a different paper's unrelated
   "counterexample". One sample per condition and a changed prompt between
   them, so it is a flag rather than a finding — but it is the flag worth
   raising, because "more documents is better" is the assumption a
   scale-up is built on and nothing here confirms it.
4. **Seven eighths of the corpus is abstract-only.** 234 of 1,905
   documents carry full text. The fetch was stopped at 216 of 330 budgeted
   arXiv papers after ~2 h; the rest is patience at the 15 s
   `Crawl-delay`, and `cache/raw/` makes it a resume rather than a
   rebuild — re-running `fetch` continues where it stopped.
5. **Two documents per paper for the seeds** — e.g. `arxiv_2002_11403`
   (arXiv HTML) and `local_knauer_marc_corners_simpliciality` (LaTeX
   source) are the same paper. This turned out to be *useful* rather than
   merely harmless: the arXiv HTML resolves `\ref` to printed numbers, so
   it is what settled that Knauer–Marc's rank-3 theorem is **Proposition
   3.2** (`CITATION_AUDIT.md` V19), which the LaTeX source could only give
   as a label. Still inflates the document count by 2.
6. **Relevance scoring is a keyword sum.** It no longer decides *which*
   documents are indexed — `CORPUS_BUDGET` (2,000) exceeds the harvest
   (1,887), so everything harvested is in — but it still decides which get
   full text, and a handful of `chirotope`-matching mathematical-physics
   papers rank higher than they deserve.
7. **`--extract` needs Enterprise tier** (§5). Not fixed because the
   Standard tier is what the brief specified and snippets plus
   `--answer` cover the need. Worth revisiting now that §6.7.3 traces the
   residual failure to retrieval rather than extraction: longer verbatim
   segments would let a caller see the neighbouring rows without opening
   the file.
