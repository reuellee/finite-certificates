# A literature-search corpus on Vertex AI Search (Discovery Engine)

Purpose: let research agents check a claim against **indexed primary
sources** instead of web-search snippets. Built 2026-08-01.

Status: **§1 (cost statement) written before anything billable was
created.** Sections 2 onward are filled in as the build proceeds.

---

## 1. Cost statement — written BEFORE creating any resource

Every figure below is from the live pricing page
<https://cloud.google.com/generative-ai-app-builder/pricing>, fetched
2026-08-01, and from the `discoveryengine` v1 discovery document fetched
the same day.

### 1.1 What will be created

| # | Resource | Where | Billing surface |
|---|---|---|---|
| 1 | one GCS bucket, plain text + one JSONL | `us-central1`, standard class | Cloud Storage — **real money** |
| 2 | one Discovery Engine data store | `global`, `GENERIC`, `SOLUTION_TYPE_SEARCH`, `CONTENT_REQUIRED` | Agent Search index storage — credit-covered |
| 3 | one Discovery Engine search engine | `global`, `SEARCH_TIER_STANDARD`, add-on `SEARCH_ADD_ON_LLM` | Agent Search queries — credit-covered |

No VM, no `aiplatform.googleapis.com` call, nothing under
`E:/Projects/tools/gemini`.

### 1.2 Real money (Cloud Storage) — the only line that touches the $100/mo ceiling

The corpus is **extracted plain text**, never PDFs. Budgeted at
≤ 60 MB of text plus a metadata JSONL.

| Item | Rate | Quantity | Monthly |
|---|---|---|---|
| Standard storage, `us-central1` | $0.020 / GB / month | ~0.03 GB | **$0.0006** |
| Class A ops (uploads) | $0.005 / 1,000 | ~300 objects, one-off | $0.0015 one-off |
| Class B ops (Discovery Engine reads during import) | $0.0004 / 1,000 | ~600, one-off | $0.0002 one-off |
| Egress to Discovery Engine | $0 (same-cloud) | — | $0 |

**Real-money standing cost: under one tenth of one US cent per month.**
Measured GB is reported in §4 once the bucket exists.

### 1.3 Credit-covered (Discovery Engine / GenAI App Builder SKUs)

| SKU | Rate | Our usage | Charge |
|---|---|---|---|
| Agent Search index storage | first **10 GiB/month free**, then $0.006849315 / GiB-hour (≈ $5 / GiB / month) | ~0.03 GiB | **$0** — free tier, before the credit |
| Search Standard Edition query | first **10,000 queries / account / month free**, then $1.50 / 1,000 | tens | **$0** — free tier, before the credit |
| Advanced Generative Answers (`--answer`) | +$4.00 / 1,000 user-input queries, **excluded from the free-query tier** | tens | ≈ $0.004 per `--answer` call; ~$0.08 for the whole verification run |
| OCR parser | $1.50 / 1,000 pages | **not enabled** | $0 |
| Layout Parser (incl. chunking) | **$10.00 / 1,000 pages**, where a parsed text/HTML page = 3,000 characters | **not enabled** | $0 |

The Layout Parser line is the trap the brief names. On this corpus it
would have been the dominant charge: ~200 documents × ~60 KB of text
÷ 3,000 chars = ~4,000 billable "pages" = **~$40 one-off**. It is
avoided by pinning the **digital parser** explicitly in
`documentProcessingConfig.defaultParsingConfig.digitalParsingConfig`
rather than relying on it being the documented default, so that "layout
parsing was not enabled" is a fact recorded in the resource. Plain text
and HTML go through the free digital path; no PDF is ever uploaded, so
the OCR parser has nothing to act on.

### 1.4 The two subscription traps, and why neither fires

Agent Search has a second pricing model, "Configurable", with a
**minimum monthly commitment of 1,000 QPM and 50 GB of storage**
(1,000 × $6/QPM-month = $6,000/month). It is opt-in through the
`configurableBillingApproach` field on both `DataStore` and `Engine`.
The discovery document records the default:

> `CONFIGURABLE_BILLING_APPROACH_UNSPECIFIED` — "Default value. For
> Spark and non-Spark **non-configurable** billing approach."

We leave that field unset, and likewise `searchEngineConfig.
requiredSubscriptionTier` (the Gemini Enterprise seat subscriptions).
Both resources are read back after creation and the absence of both
fields is recorded in §3 as evidence, not inference.

### 1.5 Caveats stated up front

* The 10 GiB index-storage free tier is documented as **"shared across
  Agent Search"** and metered **per account**, not per project. The
  standing cost is $0 *given no other Agent Search data store on this
  billing account*. At 0.03 GiB the margin is enormous, but the
  qualifier belongs in the sentence.
* The 10,000 free queries are likewise **per account per month**.
* `SEARCH_ADD_ON_LLM` on the engine does not itself bill; the
  Advanced Generative Answers SKU is metered per query that actually
  requests generative output. Plain `--query` calls do not touch it.

### 1.6 Verdict of §1

Real money: **~$0.0006/month.** Credit-covered: **$0/month at rest**,
under a cent per grounded answer in use. Both are inside the brief's
constraints, so the build proceeds. If any of the above turns out to be
wrong in practice — a forced add-on, a minimum charge, an unexpected
SKU on the bill — the build stops and this file says so instead.
