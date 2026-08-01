# Retry runbook

On 2026-08-01 the AlphaEvolve control plane worked end to end but the service
never generated a candidate. A real misconfiguration was found and fixed **late
in that session** — the project's single Gemini Enterprise seat was assigned to
nobody — and only about **35 minutes** of testing happened after the fix. That
is not long enough to call the feature broken. This is the clean retry.

Everything here costs $0 until step 3.

## 0. Preconditions (check, don't assume)

```bash
cd ai/alphaevolve
python - <<'PY'
import ae_api as A, json
P = A.PROJECT_NUMBER
us = f"projects/{P}/locations/global/userStores/default_user_store"
print(A.call("GET", us + "/userLicenses", quiet=True).text)      # expect ASSIGNED
print(A.call("GET", f"projects/{P}/locations/global/licenseConfigs",
             quiet=True).text)                                    # expect ACTIVE
PY
```

Expect `licenseAssignmentState: ASSIGNED` for the licence-holder account and a
`SUBSCRIPTION_TIER_ENTERPRISE` licenceConfig in state `ACTIVE`. The
subscription lapses **2026-09-01** (auto-renew off) — after that none of this
applies.

## 1. Free smoke test — does the engine generate at all?

```bash
python probe_toy.py 4          # 20-bit popcount toy, maxPrograms 4
```

**The signal to watch is `stats.candidatesCount`.**

* stays at `1` (the seed) for ~10 minutes and `acquired 0` every poll
  -> still silent. Go to step 4. Nothing was billed.
* goes to `2` or more, and `inputTokenCount` / `outputTokenCount` **appear** in
  `stats` (they are omitted entirely while zero) -> it works. Note the tokens
  for those first few programs; that is your $/program. Go to step 2.

## 2. Re-validate the evaluator before trusting any number

```bash
python canary.py 400           # ~4 min
```

Must print `CANARY PASS`. It checks that `zbx.nverts_exact` reproduces the
repo's five certified counts (42/58/84/104/110), that the float counter agrees
with it, and — the must-fail canary — that over 400 random and hill-climbed
(3,5) instances the float counter never exceeds **42**, the value this repo
proved is the maximum. A 43 would mean the float hull over-counts and nothing
downstream is trustworthy.

## 3. The campaign (this is where money starts)

```bash
AE_MAX_USD=5 python run_campaign.py 4 5 120 4        # (d,n)=(4,5), 120 programs, concurrency 4
```

Start at (4,5), not (3,7): 64 candidates in dim 4 rather than 256 in dim 3
(exact checks ~16x cheaper), the gap is 2 not 4, and **59 alone is a new
result** — 60 is not required.

Cost control, in layers:

* `AE_MAX_USD` — the runner reads `stats` after every submit, prices it at
  $4/M input and $24/M output, and aborts + DELETEs past the ceiling.
* `maxPrograms` (the `120`) is a hard server-side cap.
* The `finally` block deletes the experiment on every exit path.

Only `gemini-3.1-pro-preview` is on the allowlist — there is no Flash tier, so
there is no cheaper mode to fall back to. The project's daily quotas
(`AlphaEvolve{Input,Output}TokensCountPerDayPerProjectGlobal`) are 1e8 each,
about **$400/day of unthrottled headroom**, and v1alpha has **no `:stop` or
`:pause`**. Never leave a started experiment behind.

A candidate at or above the incumbent (58 at (4,5), 84 at (3,7)) is re-counted
exactly by `zbx.nverts_exact` with escalating rationalisation denominators
before it is believed. If one beats the incumbent it is written to
`record_45_<f0>.json`. That file is **not** yet a certificate — feed it through
the repo's own chain before claiming anything:

```bash
python ../maxout/build_cert_extremal.py record_45_59.json cert_45_59.json 59
python ../maxout/verify_c66_new_cases.py         # add the new cert to its CERTS list
python ../maxout/check_instances_cddlib.py       # third-party exact check (pycddlib)
```

## 4. Always, at the end of any session

```bash
python cleanup.py                # deletes every experiment in every session
python cleanup.py --engines      # also deletes the throwaway alphaevolve-probe-app engine
```

Then verify zero remain:

```bash
python - <<'PY'
import ae_api as A
for e in ["finite-certificates-lit-search", "research-search", "alphaevolve-probe-app"]:
    ep = (f"projects/{A.PROJECT_NUMBER}/locations/global/collections/"
          f"default_collection/engines/{e}")
    r = A.call("GET", f"{ep}/sessions", params={"pageSize": 100}, quiet=True)
    for s in (r.json().get("sessions", []) if r.ok else []):
        x = A.call("GET", f"{s['name']}/alphaEvolveExperiments", quiet=True)
        print(e, s["name"].rsplit("/", 1)[-1], x.text.strip())   # want {}
PY
```

## 5. Confirm where the money actually landed

The brief originally assumed AlphaEvolve bills under Gen App Builder SKUs and
would be absorbed by the $1000 credit. It does **not**: the SKUs sit under
resourceGroup **AiPlatform**. After any campaign, open the billing report,
group by SKU, and confirm whether the AlphaEvolve line items were paid by the
card or by a credit. Do not assume.

Same-session signal, no billing lag: `stats.inputTokenCount` /
`outputTokenCount` per experiment. Independent confirmation of zero: Cloud
Monitoring returns `404 Cannot find metric(s)` for
`discoveryengine.googleapis.com/alpha_evolve_input_tokens_count_regional`
until the first token is consumed.

## 6. If it is still silent after a full day post-assignment

Gemini Enterprise Standard includes support access. Open a case and ask the
one question that matters: **does AlphaEvolve require an additional enablement
or allowlist on the tenant beyond a Gemini Enterprise Standard licence?**

Include, because it rules out everything the first-line script will suggest:

* an experiment resource name (`.../alphaEvolveExperiments/{id}`) that sat in
  `STARTED` producing `candidatesCount: 1` forever;
* that `:start` returned an LRO with `done: true` and **no** `error`, and that
  the operation 404s on a subsequent GET;
* that `:acquirePrograms` returns a literal `{}` indefinitely and no program
  ever reaches `EVALUATING`;
* that the seat is `ASSIGNED` to the licence-holder account against an `ACTIVE`
  `SUBSCRIPTION_TIER_ENTERPRISE` licenceConfig;
* that `gemini-3.1-pro-preview` is `MODEL_ENABLED` on the engine, that the
  AlphaEvolve daily token quotas are 1e8 (not zero), that
  `roles/discoveryengine.serviceAgent` is bound, and that the same silence
  occurs on an `appType: APP_TYPE_INTRANET` engine with
  `requiredSubscriptionTier: SUBSCRIPTION_TIER_ENTERPRISE`;
* that Cloud Logging shows nothing from `discoveryengine` for the run.

The error text `See b/510479459` (returned when a seed has no EVOLVE-BLOCK
region) confirms this is an internally-tracked preview surface — worth quoting.

---

## OUTCOME 2026-08-01 — retry executed, campaign complete

Seat propagation WAS the fix. Smoke test generated 4/4 candidates
($0.0448, ~1.5c/program at toy scale). Canary passed. Campaign ran:

    AE_MAX_USD=5 run_campaign.py 4 5 120 4   -> campaign_45.log

* 9 candidates evaluated before the ceiling tripped at ~$5.81
  (34,975 in / 236,369 out tokens). Experiment deleted; engine swept
  afterwards: 0 experiments remain.
* Real-scale economics: **~$0.65/program**, 40x the toy figure —
  output tokens dominate (the model emits long programs + reasoning).
* Best EXACT result: **58 — no new record.** Two candidates claimed
  v=59 by float count; the exact-Fraction gate showed both were
  actually 56. The float hull over-counts on evolved adversarial
  geometry; the gate is not optional.
* Verdict: mechanically AlphaEvolve works end-to-end now, but a
  meaningful evolutionary run (hundreds of generations) costs
  $100-500 at measured rates. 9 candidates is not evolution.
  Do not re-run without an explicit new budget decision.

## Framing post-mortem (Gemini consult, 2026-08-01)

Asked Gemini what problem types AlphaEvolve actually wins at. Answer,
consistent with our measurements: published wins ran MILLIONS of candidate
evaluations (FunSearch-class scale); at tens of candidates one is doing
"zero-shot prompting with a while loop", paying harness overhead for no
search benefit. The correct framing — if ever used at scale — is evolving
small heuristic kernels (priority/support-selection functions scored over a
benchmark suite, ~5-line EVOLVE blocks, exact-only scoring, graded partial
credit), never whole constructors, and never direct record-hunting in
brittle algebraic search spaces. Verdict: structurally misaligned with a
$100/mo exact-mathematics program; dollars go to reasoning passes instead.
Subscription left to lapse 2026-09-01 (auto-renew off).
