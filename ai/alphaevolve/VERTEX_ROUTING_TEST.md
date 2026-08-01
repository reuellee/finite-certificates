# Pending experiment: does Claude-via-Vertex draw the GenAI App Builder credit?

Hypothesis (community-reported, unverified): running Claude Code with
`CLAUDE_CODE_USE_VERTEX=1` bills tokens to the "AI Dev Tools: Claude ..."
SKUs, which sit in resourceGroup GenAppBuilder — the family the $1000
credit plausibly covers. If true: credit-funded overflow agent capacity.
AlphaEvolve SKUs are AiPlatform and are NOT rescued by this either way.

Status 2026-08-01: BLOCKED ON TOOLING, not on the hypothesis. A nested
`claude -p` under this Claude Code session hangs silently in Vertex mode
(exit 124, no stdout/stderr, env-cleaned run included). Do not debug the
nesting; run it from a plain terminal instead.

## The one-command test (run in a normal terminal)

    CLAUDE_CODE_USE_VERTEX=1 CLOUD_ML_REGION=us-east5 \
    ANTHROPIC_VERTEX_PROJECT_ID=project-ebd5a273-53ea-4c8b-81a \
    claude -p "Reply with exactly: vertex ping" --model sonnet

Cost if it works: well under $0.01. Possible fast failures and meanings:
- 403/404 model not found -> Claude models need enabling in Vertex Model
  Garden for this project (an Anthropic-terms acceptance step: user call).
- Auth error -> `gcloud auth application-default login` first.

## Then, ~24h later, the actual answer

Billing -> Reports -> Group by SKU, current month. Look for:
- "AI Dev Tools: Claude Sonnet ..." (GenAppBuilder) with a credit offset
  -> hypothesis TRUE: credit-funded Claude tokens exist.
- "Claude Sonnet ... (Vertex partner model)" under AiPlatform, no offset
  -> hypothesis FALSE for plain calls; the AI Dev Tools SKUs are triggered
  by something else. Record either way in this file.
