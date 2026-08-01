#!/usr/bin/env python3
"""Search the indexed literature corpus.  One line, no setup, stdlib only.

    python ops/corpus/research_search.py --query "biquadratic final polynomial"
    python ops/corpus/research_search.py --query "..." --top 8 --extract
    python ops/corpus/research_search.py --query "..." --answer
    python ops/corpus/research_search.py --cost-note

Prints, per hit: rank, document id, title, year, url, and a snippet (or an
extractive segment with --extract).  --answer additionally asks Discovery
Engine for a grounded summary with citations back to those documents.

Authentication is whatever `gcloud auth print-access-token` gives; no
libraries to install.  Override the target with the environment variables
CORPUS_PROJECT / CORPUS_ENGINE.

WHAT THIS COSTS  (also printed by --cost-note)
  plain --query   Agent Search "Search Standard Edition", $1.50 / 1,000
                  queries, with the first 10,000 queries per ACCOUNT per
                  month free.  In practice: $0.
  --answer        adds "Advanced Generative Answers (AI Mode)", +$4.00 /
                  1,000 user-input queries.  This SKU is NOT covered by the
                  free-query tier: roughly $0.004 per --answer call.
  at rest         Agent Search index storage, $5/GiB/month above a 10 GiB
                  per-account free tier; this corpus measures 0.0056 GiB,
                  so $0.  Plus a GCS bucket of the same size, measured at
                  $0.00012/month, which is the only real-money line.
  never billed    the OCR parser and the Layout Parser ($10 / 1,000 pages)
                  are NOT enabled on this data store.
  All Discovery Engine SKUs above draw on the GenAI App Builder credit.
"""

from __future__ import annotations

import argparse
import html
import json
import os
import re
import subprocess
import sys
import textwrap
import urllib.error
import urllib.request

# The corpus is full of Ziegler, Montufar, Jesus De Loera and LaTeX math, and
# the default Windows console codec is cp1252.  Without this, printing a hit
# raises UnicodeEncodeError -- which would break the documented one-liner for
# any caller who has not set PYTHONIOENCODING.
for _s in (sys.stdout, sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, ValueError):        # not a reconfigurable stream
        pass

PROJECT = os.environ.get("CORPUS_PROJECT", "project-ebd5a273-53ea-4c8b-81a")
ENGINE = os.environ.get("CORPUS_ENGINE", "finite-certificates-lit-search")
COLLECTION = os.environ.get("CORPUS_COLLECTION", "default_collection")
API = "https://discoveryengine.googleapis.com/v1"

SERVING = (f"projects/{PROJECT}/locations/global/collections/{COLLECTION}"
           f"/engines/{ENGINE}/servingConfigs/default_search")

COST_NOTE = (
    "COST: --query bills Agent Search Search-Standard ($1.50/1k queries, "
    "first 10k/account/month free -> $0). --answer additionally bills "
    "Advanced Generative Answers (+$4.00/1k, NOT free-tier eligible, "
    "~$0.004/call). Index storage 0.0056 GiB measured, inside the 10 GiB/"
    "account free tier -> $0. Layout Parser and OCR are NOT enabled on this "
    "data store. All Discovery Engine SKUs draw on the GenAI App Builder "
    "credit; the only real-money line is the 5.7 MB GCS bucket at "
    "$0.00012/month. See ops/corpus/CORPUS.md section 1.")


def token() -> str:
    return subprocess.run(["gcloud", "auth", "print-access-token"],
                          capture_output=True, text=True, check=True,
                          shell=(os.name == "nt")).stdout.strip()


def post(path: str, body: dict, soft: bool = False) -> dict | None:
    req = urllib.request.Request(
        f"{API}/{path}", data=json.dumps(body).encode(), method="POST",
        headers={"Authorization": f"Bearer {token()}",
                 "Content-Type": "application/json",
                 "X-Goog-User-Project": PROJECT})
    try:
        with urllib.request.urlopen(req, timeout=180) as r:
            return json.loads(r.read() or b"{}")
    except urllib.error.HTTPError as e:
        msg = e.read().decode("utf-8", "replace")
        if soft:
            sys.stderr.write(f"(soft) HTTP {e.code}: {msg[:300]}\n")
            return None
        sys.stderr.write(f"HTTP {e.code}\n{msg}\n")
        raise SystemExit(2)


def clean(s: str) -> str:
    """Snippets come back with <b> highlighting and HTML entities."""
    return html.unescape(re.sub(r"</?b>", "", s)).replace(" ", " ")


def wrap(s: str, indent: str = "     ") -> str:
    s = " ".join(s.split())
    return textwrap.fill(s, width=100, initial_indent=indent,
                         subsequent_indent=indent)


def run_search(query: str, top: int, extract: bool) -> tuple[dict, bool]:
    """Returns (response, extract_actually_happened).

    Extractive segments are an Enterprise-edition feature; this engine is on
    the Standard tier (see CORPUS.md section 6), so --extract is attempted and
    falls back to snippets rather than failing the call.
    """
    base = {"query": query, "pageSize": top,
            "queryExpansionSpec": {"condition": "AUTO"},
            "spellCorrectionSpec": {"mode": "AUTO"}}
    if extract:
        r = post(f"{SERVING}:search", dict(
            base, contentSearchSpec={
                "snippetSpec": {"returnSnippet": True},
                "extractiveContentSpec": {"maxExtractiveSegmentCount": 2,
                                          "numPreviousSegments": 0,
                                          "numNextSegments": 0}}), soft=True)
        if r is not None:
            return r, True
        sys.stderr.write("  -> falling back to snippets (Standard tier)\n")
    return post(f"{SERVING}:search", dict(
        base, contentSearchSpec={"snippetSpec": {"returnSnippet": True}})), False


def show_search(resp: dict, extract: bool) -> None:
    results = resp.get("results", [])
    if not results:
        print("  (no results)")
    for i, r in enumerate(results, 1):
        doc = r.get("document", {})
        sd = doc.get("structData", {}) or {}
        dd = doc.get("derivedStructData", {}) or {}
        did = doc.get("id", "?")
        print(f"\n[{i}] {sd.get('title') or dd.get('title') or '(untitled)'}")
        print(f"     year={sd.get('year', '?')}  arxiv={sd.get('arxiv_id') or '-'}"
              f"  full_text={'yes' if sd.get('has_full_text') else 'no'}")
        print(f"     {sd.get('url', '')}")
        print(f"     doc_id: {did}")
        if sd.get("authors"):
            print(wrap("authors: " + sd["authors"]))
        for sn in dd.get("snippets", []):
            if sn.get("snippet"):
                print(wrap("snippet: " + clean(sn["snippet"])))
        if extract:
            for seg in dd.get("extractive_segments", []) or dd.get("extractiveSegments", []) or []:
                if seg.get("content"):
                    print(wrap("segment: " + seg["content"][:1400]))


def run_answer(query: str, top: int) -> dict:
    return post(f"{SERVING}:answer", {
        "query": {"text": query},
        "searchSpec": {"searchParams": {"maxReturnResults": max(top, 10)}},
        "answerGenerationSpec": {
            "includeCitations": True,
            "ignoreAdversarialQuery": False,
            "ignoreNonAnswerSeekingQuery": False,
            "ignoreLowRelevantContent": False,
        },
    })


def show_answer(resp: dict) -> None:
    ans = resp.get("answer", {})
    print("\n=== GROUNDED ANSWER "
          f"(state={ans.get('answerSkippedReasons') or 'OK'}) ===")
    print(textwrap.fill(ans.get("answerText", "(no answer text)"), width=100))
    refs = ans.get("references", [])
    if refs:
        print("\n--- cited documents ---")
        for i, ref in enumerate(refs):
            ci = ref.get("chunkInfo", {}) or ref.get("unstructuredDocumentInfo", {})
            dm = (ci.get("documentMetadata") or {})
            sd = dm.get("structData", {}) or {}
            print(f"[{i}] {dm.get('title') or sd.get('title') or ci.get('document', '?')}")
            print(f"    doc: {dm.get('document') or ci.get('document', '')}")
            if sd.get("url"):
                print(f"    {sd['url']}  ({sd.get('year', '?')})")


def main() -> None:
    ap = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--query", "-q")
    ap.add_argument("--top", "-n", type=int, default=5)
    ap.add_argument("--answer", action="store_true",
                    help="also request a grounded summary (billable SKU, ~$0.004)")
    ap.add_argument("--extract", action="store_true",
                    help="return extractive segments instead of short snippets")
    ap.add_argument("--json", action="store_true", help="dump the raw API response")
    ap.add_argument("--cost-note", action="store_true",
                    help="print which SKU a call consumes, and exit")
    a = ap.parse_args()

    if a.cost_note and not a.query:
        print(COST_NOTE)
        return
    if not a.query:
        ap.error("--query is required (or use --cost-note alone)")

    print(f"### corpus search: {a.query!r}   engine={ENGINE}")
    resp, got_extract = run_search(a.query, a.top, a.extract)
    if a.json:
        print(json.dumps(resp, indent=1)[:20000])
    else:
        show_search(resp, got_extract)

    if a.answer:
        ar = run_answer(a.query, a.top)
        if a.json:
            print(json.dumps(ar, indent=1)[:20000])
        else:
            show_answer(ar)

    print("\n" + COST_NOTE if a.cost_note else
          "\n(run with --cost-note to see which SKU this consumed)")


if __name__ == "__main__":
    main()
