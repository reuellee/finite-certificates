# AlphaEvolve on Gemini Enterprise — the working API recipe

Everything below was established empirically against the live service on
**2026-08-01** with a Gemini Enterprise Standard licence. Where the published
reference and reality disagree, reality is recorded and the disagreement is
flagged. `ae_api.py` in this directory is the client that implements it.

The authoritative schema is the **discovery document**, not the HTML reference:

```
https://discoveryengine.googleapis.com/$discovery/rest?version=v1alpha
```

Grep its `schemas` for `AlphaEvolve`. It gave correct field names for every
message; the prose reference did not.

---

## 0. Auth and identifiers

```
base      https://discoveryengine.googleapis.com/v1alpha
token     gcloud auth print-access-token
header    x-goog-user-project: project-ebd5a273-53ea-4c8b-81a   (project ID is fine HERE)
```

On Windows `gcloud` is a `.cmd` shim — `subprocess` needs the explicit
`%LOCALAPPDATA%\Google\Cloud SDK\google-cloud-sdk\bin\gcloud.cmd`.

### GOTCHA 1 — the resource path must use the project NUMBER

This cost the most time and produces the least informative error.

```
projects/159398774377/...                 -> works
projects/project-ebd5a273-53ea-4c8b-81a/... -> 400 "Request contains an invalid
                                               argument." with NO fieldViolations
```

`sessions.create` and `sessions.list` accept **either** form, so the session
you create with the project ID looks healthy — and then
`alphaEvolveExperiments.create` fails with a bare `INVALID_ARGUMENT` that
reads exactly like a bad config. Verified 2x2 (both project forms x two
sessions): project number 200, project ID 400, independent of the session.

Parent for everything:

```
projects/{PROJECT_NUMBER}/locations/global/collections/default_collection
  /engines/{ENGINE}/sessions/{SESSION}
```

Engine `finite-certificates-lit-search` (`solutionType: SOLUTION_TYPE_SEARCH`,
`searchTier: SEARCH_TIER_STANDARD`) works — no special engine type is needed.

---

## 1. Create a session

```http
POST {engine}/sessions
{"displayName": "alphaevolve-maxout", "state": "IN_PROGRESS"}
```

Returns `.../sessions/851551224574743065`. **Use the returned name verbatim**
(it comes back project-number-qualified — see GOTCHA 1).

---

## 2. Create the experiment

```http
POST {session}/alphaEvolveExperiments
{"config": {
  "title": "…",                      // required
  "problemDescription": "…",         // required
  "programLanguage": "PYTHON",       // required
  "runSettings": {                   // required
    "maxPrograms": 200,              //   must be > 1; the seed counts toward it
    "concurrency": 4,                //   must be positive
    "maxDuration": "21600s"          //   optional, default 24h
  },
  "generationSettings": {            // optional
    "context": "…",
    "includeFullProgramInPrompt": true,
    "models": [{"name": "gemini-3.1-pro-preview", "weight": 1.0}]
  },
  "evolutionSettings": {             // optional
    "parentSamplingConfig": {"paretoSamplingConfig":
      {"paretoSamplingProbability": 0.5}}
  }
}}
```

### Corrections to the brief / published reference

| claimed | actual |
|---|---|
| `programmingLanguage` | **`programLanguage`** — the long spelling 400s with `Cannot find field` |
| `notes` (<=1000) | **no such field** anywhere in the config |
| `runSettings.idleTimeout` | **no such field**; only `maxPrograms`, `concurrency`, `maxDuration` |
| `:start` body `{"desiredProgramsCount": 1}` | `StartExperimentRequest` has only `name`; `{}` also works |
| `:acquirePrograms?desiredProgramsCount=N` | it is a **body** field, not a query parameter |
| submit body is one submission | body is `{"evaluationSubmissions": [ …one… ]}` |

### GOTCHA 2 — the model allowlist is one model long

Probed 26 names. **Only `gemini-3.1-pro-preview` is accepted.** Everything
else — `gemini-2.5-pro`, `gemini-2.5-flash`, `gemini-3-pro-preview`,
`gemini-3.1-flash-preview`, `gemini-flash-latest`, `gemini-2.5-flash-lite`, … —
returns `400 unsupported model: <name>`. There is **no Flash tier available**,
so there is no cheap mode; omitting `models` entirely lets the server pick
(also legal, model unknown to the caller).

---

## 3. Seed program — REQUIRED, and it must be evaluated and marked

```http
POST {experiment}/alphaEvolvePrograms
{"content": {"description": "seed",
             "files": [{"path": "main.py", "content": "<source>",
                        "programLanguage": "PYTHON"}]},
 "evaluation": {"scores": {"scores": [{"metric": "vertices", "score": 58.0}]}}}
```

Two hard requirements the reference does not mention:

* **`evaluation.scores` is mandatory on the seed.** Omit it and you get
  `400 evaluation_results.scores must contain at least one score.` Evaluate the
  seed locally first; its score is the baseline.
* **The source must contain a non-empty EVOLVE-BLOCK region.** Verbatim error:

  > `Program content must contain at least one EVOLVE-BLOCK-START /
  > EVOLVE-BLOCK-END region with editable code between the markers (whitespace
  > and comment-only regions don't count -- AlphaEvolve has nothing to mutate).`

  Marker syntax that passes:

  ```python
  # EVOLVE-BLOCK-START
  def build():
      ...
  # EVOLVE-BLOCK-END
  ```

  With `includeFullProgramInPrompt: false` (the default) **only** the marked
  region is shown to the model, so put the mutable strategy inside and the
  fixed harness outside.

Create the seed **before** `:start`.

---

## 4. Start / acquire / submit / list

```http
POST {experiment}:start                      {"name": "{experiment}"}   -> LRO, done:true
POST {experiment}:acquirePrograms            {"desiredProgramsCount": 4}
POST {experiment}:submitProgramsEvaluations  {"evaluationSubmissions": [
      {"program": "{program}", "lockToken": "{lockToken}",
       "evaluation": {"scores": {"scores": [{"metric": "vertices", "score": 59.0}]},
                      "insights": {"insights": [{"label": "note", "text": "…"}]}}}]}
GET  {experiment}/alphaEvolvePrograms?stateFilter=COMPLETED&orderBy=vertices%20desc&pageSize=50
GET  {experiment}                            -> state + stats
DELETE {experiment}                          -> the only way to stop a run
```

* `:acquirePrograms` returns `{}` (no `programs` key) when nothing is ready —
  handle the empty case, don't index.
* `:start` is not idempotent: a second call gives
  `400 Cannot start experiment from state STARTED`; so does `:resume`.
* There is **no `:stop`/`:pause` method** in v1alpha. `DELETE` is the kill switch.
* `stateFilter` accepts the bare enum `COMPLETED`. `INITIALIZED` 400s, so the
  filter grammar is not uniform — prefer omitting it and filtering client-side.
* Only **one** submission per `:submitProgramsEvaluations` call is supported.

### Cost meter — read this, not the billing console

`GET {experiment}` returns

```json
"stats": {"candidatesCount": 1, "evaluatedCandidatesCount": 1,
          "inputTokenCount": "…", "outputTokenCount": "…"}
```

`inputTokenCount` / `outputTokenCount` are **billed** tokens, per experiment,
available immediately — no 6-24h billing lag. The two token fields are simply
**absent when they are zero**. This is the only same-session spend signal and
it is the right one to gate a campaign on.

Billing note (from the coordinator, and consistent with the SKU catalogue):
AlphaEvolve tokens meter under **resourceGroup `AiPlatform`**, *not*
GenAppBuilder, so a Gen App Builder credit does **not** absorb them.

---

## 5. Status of the loop on this licence — READ BEFORE PLANNING A CAMPAIGN

Everything above is confirmed working: session, experiment, seed, start,
acquire, submit, list, stats, delete.

**But the evolution engine produced no candidates.** With a valid
EVOLVE-BLOCK-marked, locally-scored seed and a started experiment, over
repeated polling the service kept `candidatesCount` at 1 (the seed) and
`acquirePrograms` kept returning `{}`. `inputTokenCount`/`outputTokenCount`
never appeared, i.e. **zero tokens were billed**, and Cloud Monitoring has no
descriptor for `discoveryengine.googleapis.com/alpha_evolve_input_tokens_count_regional`
in this project (`404 Cannot find metric(s)`), which confirms it independently.

Ruled out by direct test, none of which changed the behaviour: fresh session;
project-number path; pinned model vs server default; `PATCH engine.modelConfigs
= {"gemini-3.1-pro-preview": "MODEL_ENABLED"}`; assigning the Gemini Enterprise
seat (`userStores/default_user_store` had **no** user licence at all — genuinely
misconfigured, `:batchUpdateUserLicenses` fixed it); `maxPrograms` 3/4/20 and
`concurrency` 1/2/4; APIs enabled and `roles/discoveryengine.serviceAgent`
bound; AlphaEvolve token quotas (1e8/day, not zero); an
`appType: APP_TYPE_INTRANET` + `SUBSCRIPTION_TIER_ENTERPRISE` engine (note
`requiredSubscriptionTier` can only be set on such an engine:
`400 Subscription tier is only supported for engines with appType
"APP_TYPE_INTRANET"`); and ~2h of propagation time after purchase.

Remaining live explanations: an allowlist beyond the licence, or slower
entitlement propagation. Neither is visible from the client.

**Cost exposure if it ever does start.** Only `gemini-3.1-pro-preview` is
allowed (~$4/M in, ~$24/M out) and there is no Flash fallback; the daily quotas
`AlphaEvolve{Input,Output}TokensCountPerDayPerProjectGlobal` are 1e8 each, i.e.
roughly $400/day of unthrottled headroom. Use the client-side ceiling in
`run_campaign.py` (`AE_MAX_USD`) and run `cleanup.py` afterwards — `DELETE` is
the only kill switch.
