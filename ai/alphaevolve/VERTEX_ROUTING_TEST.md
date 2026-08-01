# Credit-routing test — RESOLVED STRUCTURALLY + LIVE TEST FIRED 2026-08-01

## Original hypothesis: FALSE (settled without needing the billing lag)

The community claim was that Claude Code with `CLAUDE_CODE_USE_VERTEX=1`
bills to the "AI Dev Tools: Claude ..." SKUs. Catalog inspection settles
this structurally:

* The "AI Dev Tools" SKUs (Claude Sonnet 4.6, Claude Opus 4.6, Gemini 2.5/3.0,
  GPT OSS 120B token meters, all `resourceGroup: GenAppBuilder`) belong to
  billing service **74B1-77CF-C302 "Vertex AI Search"** — the Discovery
  Engine / Gemini Enterprise product family.
* Claude Code's Vertex mode calls `aiplatform.googleapis.com` = billing
  service C7E2-9256-1C43 "Vertex AI". A call on one service cannot produce
  SKUs of another. Corroborating: July's metered Vertex Gemini usage (~$113,
  tools/gemini scripts) billed AiPlatform and drew $0.00 of the $1000
  GenAppBuilder credit.
* Additionally, Claude publisher models 404 on this project (Model Garden
  enablement never done), so the routed CLI could not have run anyway.

**Conclusion: the $1000 credit can never fund Claude Code tokens.** Do not
retry CLAUDE_CODE_USE_VERTEX for credit reasons.

## The live successor hypothesis: agy's Claude models

Antigravity (agy 1.1.9) exposes `claude-sonnet-4-6`, `claude-opus-4-6-thinking`
and `gpt-oss-120b-medium` — names matching the AI Dev Tools SKUs one-for-one.
If agy's Claude usage is metered against this project (the Gemini Enterprise
seat lives here), those tokens land in GenAppBuilder SKUs — the family the
credit plausibly covers.

Fired 2026-08-01 ~19:55 local, both via
`agy --model claude-sonnet-4-6 -p ... --disable-slash-commands`:
1. "routing ping" (tiny)
2. an ~840-word generation (unmissable if metered; ≲$0.03 if billed at all)

## The check (~24h later): Billing → Reports, current month, group by SKU

* "AI Dev Tools: Claude Sonnet 4.6 ..." lines present **with credit offset**
  → JACKPOT: credit-funded Claude reasoning exists via agy. Measure rates,
  then decide policy (still respect subscription-first defaults).
* Lines present, **no credit offset** → metered to card; note the rate and
  stop using agy Claude models without budget approval.
* No lines at all → usage is included in the Gemini Enterprise seat quota:
  free Claude via agy while the seat lasts (until 2026-09-01) — also a win,
  but credit-irrelevant.

Record the outcome here either way.
