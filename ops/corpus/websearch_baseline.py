#!/usr/bin/env python3
"""The control arm: the same questions put to a general web search engine.

Exists so that "the corpus is better/worse than web search" in CORPUS.md is a
recorded comparison rather than an impression.  Uses DuckDuckGo's HTML
endpoint, 5 s apart, a handful of queries -- it is a control, not a crawler.

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

UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"


def search(q: str, top: int = 6) -> list[tuple[str, str]]:
    # curl, not urllib: the endpoint serves an empty anomaly page to clients
    # that send only a User-Agent and no browser header set.
    url = "https://html.duckduckgo.com/html/?q=" + urllib.parse.quote(q)
    page = subprocess.run(
        ["curl", "-s", "--max-time", "45", "-A", UA, url],
        capture_output=True, text=True, encoding="utf-8", errors="replace",
        shell=(os.name == "nt")).stdout
    titles = re.findall(r'class="result__a"[^>]*>(.*?)</a>', page, re.S)
    snips = re.findall(r'class="result__snippet"[^>]*>(.*?)</a>', page, re.S)

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
