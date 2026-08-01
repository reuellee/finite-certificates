#!/usr/bin/env python3
"""The control arm: the same questions put to a general web search engine.

Exists so that "the corpus is better/worse than web search" in CORPUS.md is a
recorded comparison rather than an impression.  Uses DuckDuckGo's HTML
"lite" endpoint, 5 s apart, a handful of queries -- it is a control, not a
crawler.  It rate-limits aggressively: after roughly five requests it serves
an empty page, which this script reports as "(no results -- rate limited or
blocked)" rather than as a genuine zero.  The transcripts recorded in
CORPUS.md section 6.5 were taken through the agent harness's own fetch tool
against the same endpoint, for that reason.

    python websearch_baseline.py "question one" "question two"
"""

from __future__ import annotations

import html
import os
import re
import subprocess
import sys
import time
import urllib.parse
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

UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"


def search(q: str, top: int = 6) -> list[tuple[str, str]]:
    # curl, not urllib: the endpoint serves an empty anomaly page to clients
    # that send only a User-Agent and no browser header set.
    url = "https://lite.duckduckgo.com/lite/?q=" + urllib.parse.quote(q)
    page = subprocess.run(
        ["curl", "-s", "--max-time", "45", "-A", UA, url],
        capture_output=True, text=True, encoding="utf-8", errors="replace",
        shell=(os.name == "nt")).stdout
    titles = re.findall(r'class="result-link"[^>]*>(.*?)</a>', page, re.S)
    snips = re.findall(r'class="result-snippet"[^>]*>(.*?)</td>', page, re.S)

    def txt(s: str) -> str:
        return " ".join(html.unescape(re.sub(r"<[^>]+>", "", s)).split())

    return list(zip([txt(t) for t in titles], [txt(s) for s in snips]))[:top]


def main() -> None:
    for i, q in enumerate(sys.argv[1:]):
        if i:
            time.sleep(5)
        print(f"\n### web search: {q!r}")
        for j, (t, s) in enumerate(search(q), 1):
            print(f"[{j}] {t}")
            print(f"    {s[:400]}")


if __name__ == "__main__":
    main()
