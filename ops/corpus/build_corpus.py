#!/usr/bin/env python3
"""Build the literature-search corpus for Vertex AI Search (Discovery Engine).

Stdlib only.  Three stages, each cached on disk so a re-run is cheap and
polite:

  harvest   arXiv metadata + abstracts via the arXiv API (export.arxiv.org),
            one request per query, >= 3 s apart, as the API manual asks.
  fetch     full text for the highest-value subset, from arXiv's own HTML
            rendering (arxiv.org/html/<id>, `Allow`ed in robots.txt) with a
            15 s delay -- arXiv's published Crawl-delay -- falling back to
            ar5iv.labs.arxiv.org for papers predating native HTML.
  emit      out/docs/<doc_id>.txt   one plain-text file per document
            out/metadata.jsonl      the Discovery Engine ingest manifest
            out/corpus.jsonl        the same records with full_text inline
                                    (local master; not uploaded)

Licence / politeness notes, recorded because they are a judgement call:

  * export.arxiv.org/robots.txt is `Disallow: /`.  That directive governs
    crawlers; the arXiv API *manual* documents export.arxiv.org/api/query as
    the sanctioned programmatic interface and asks for no more than one
    request every 3 seconds.  We use the API, at 3 s, with a descriptive
    User-Agent carrying a contact address.  We do not crawl /find or /list.
  * arxiv.org/robots.txt explicitly Allows /abs, /pdf and /html and sets
    Crawl-delay: 15.  We fetch only /html, at 15 s, for a bounded list.
    /e-print and /src are Disallowed and we never touch them; no bulk S3
    access is used (it is requester-pays and out of budget anyway).
  * Full text is stored as extracted text in a *private* bucket and a
    *private* data store, for one user's claim-checking.  It is not
    redistributed.  Author licences vary and several are arXiv's
    non-exclusive licence, which does not grant redistribution -- hence
    private-only, and hence the teardown section of CORPUS.md.

Usage:
    python build_corpus.py harvest
    python build_corpus.py fetch [--limit N]
    python build_corpus.py emit
    python build_corpus.py all
"""

from __future__ import annotations

import argparse
import html
import json
import os
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path

# The corpus is full of Ziegler, Montufar, Jesus De Loera and LaTeX math, and
# the default Windows console codec is cp1252.  Without this, printing a hit
# raises UnicodeEncodeError -- which would break the documented one-liner for
# any caller who has not set PYTHONIOENCODING.
for _s in (sys.stdout, sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, ValueError):        # not a reconfigurable stream
        pass

HERE = Path(__file__).resolve().parent
REPO = HERE.parent.parent
CACHE = HERE / "cache"
OUT = HERE / "out"

UA = "finite-certificates-corpus/0.1 (research index; mailto:reuellee@gmail.com)"

ARXIV_API = "https://export.arxiv.org/api/query"
ARXIV_API_DELAY = 3.0          # arXiv API manual
ARXIV_HTML_DELAY = 15.0        # arxiv.org robots.txt Crawl-delay
AR5IV_DELAY = 6.0

# ---------------------------------------------------------------------------
# What goes in.  Seeds are papers this program actually cites; only IDs that
# were verified against the repo's own notes appear here.
# ---------------------------------------------------------------------------

SEED_IDS = [
    "1204.0645",    # Fukuda, Miyata, Moriyama -- Complete Enumeration of Small
                    # Realizable Oriented Matroids (the (4,9) cell lives here)
    "2002.11403",   # Knauer, Marc -- Corners and simpliciality in oriented
                    # matroids and partial cubes (mutation graphs, n <= 9)
    "2509.21286",   # Balakin, Cox, Loho, Sturmfels -- Maxout Polytopes
    "2503.02336",   # Rote -- NumPSLA
    "1408.0688",    # Miyata, Padrol -- neighborly polytopes
]

# (query, max_results).  arXiv API search grammar; sorted by relevance.
QUERIES = [
    ('all:"oriented matroid" AND all:realizability', 40),
    ('all:"oriented matroid" AND all:enumeration', 30),
    ('all:"uniform oriented matroid"', 30),
    ('all:"final polynomial"', 25),
    ('all:chirotope', 30),
    ('all:"pseudoline arrangement"', 30),
    ('all:"realization space" AND cat:math.CO', 30),
    ('all:"order type" AND all:"point configuration"', 25),
    ('all:"simplicial arrangement"', 25),
    ('all:"tope graph"', 20),
    ('all:"partial cube"', 20),
    ('all:"matroid" AND all:"mutation graph"', 15),
    ('all:"Las Vergnas"', 20),
    ('all:"Grassmann-Plucker"', 20),
    ('all:"maxout"', 25),
    ('all:"tropical" AND all:"neural network"', 25),
    ('all:zonotope AND cat:math.CO', 30),
    ('all:"neighborly polytope"', 20),
    ('all:"f-vector" AND all:polytope', 30),
    ('all:"projectively unique"', 15),
    ('all:"covering code"', 20),
    ('all:"rectilinear crossing number"', 15),
    ('all:"empty hexagon" OR all:"Erdos-Szekeres"', 20),
    ('all:"circulant Hadamard"', 15),
    ('all:"Costas array"', 12),
    ('all:"biplane" AND all:design', 12),
    ('all:"isomorph-free" AND all:generation', 15),
    ('all:"matroid stratification" OR all:"Grassmannian" AND all:matroid', 20),
    ('all:"allowable sequence"', 12),
    ('all:"Hirsch conjecture"', 12),
    ('all:"open problems" AND all:"discrete geometry"', 20),
    ('all:"arrangement of pseudolines"', 20),
]

# Primary sources already sitting in this repo -- free, and exactly the papers
# the verification questions turn on.  (Our OWN notes are deliberately absent:
# indexing OMGAMMA.md / CAPSTONE.md / the two arXiv notes would make the
# verification self-answering and worthless.)
LOCAL_SOURCES = [
    dict(doc_id="local_knauer_marc_corners_simpliciality",
         path="ai/omgamma/sources/corners_and_simplicity.tex",
         title="Corners and simpliciality in oriented matroids and partial cubes",
         authors="Kolja Knauer; Tilen Marc",
         year=2023, arxiv_id="2002.11403",
         url="https://arxiv.org/abs/2002.11403",
         venue="European J. Combin. 112 (2023) 103714",
         kind="latex_source"),
    dict(doc_id="local_fmm13_om_classification",
         path="ai/omgamma/sources/fmm13_OM_classification.tex",
         title="Complete Enumeration of Small Realizable Oriented Matroids",
         authors="Komei Fukuda; Hiroyuki Miyata; Sonoko Moriyama",
         year=2013, arxiv_id="1204.0645",
         url="https://arxiv.org/abs/1204.0645",
         venue="Discrete Comput. Geom. 49 (2013) 359-381",
         kind="latex_source"),
    dict(doc_id="local_finschi_om_catalog_index",
         path="ai/omgamma/sources/om_index.html",
         title="Homepage of Oriented Matroids -- catalog index (L. Finschi)",
         authors="Lukas Finschi", year=2024, arxiv_id="",
         url="https://finschi.com/math/om/", venue="web catalog",
         kind="html"),
    dict(doc_id="local_finschi_om_catom",
         path="ai/omgamma/sources/om_catom.html",
         title="Homepage of Oriented Matroids -- catalog of oriented matroids (L. Finschi)",
         authors="Lukas Finschi", year=2024, arxiv_id="",
         url="https://finschi.com/math/om/?p=catom", venue="web catalog",
         kind="html"),
    dict(doc_id="local_finschi_om_49",
         path="ai/omgamma/sources/om_49.html",
         title="Homepage of Oriented Matroids -- rank 4, 9 elements catalog page (L. Finschi)",
         authors="Lukas Finschi", year=2024, arxiv_id="",
         url="https://finschi.com/math/om/", venue="web catalog",
         kind="html"),
]

# Non-arXiv open documents worth having.  Only fetched if a text extractor
# for them is available; each records its own licence rationale.
EXTRA_URLS = [
    dict(doc_id="ejc_ds4_oriented_matroids_today_2024",
         url="https://www.combinatorics.org/files/Surveys/ds4/ds4v4-2024.pdf",
         title="Oriented Matroids Today (Electronic J. Combinatorics Dynamic Survey DS4, v4)",
         authors="Guenter M. Ziegler (ed.)", year=2024, arxiv_id="",
         venue="Electron. J. Combin., Dynamic Survey DS4",
         kind="pdf"),
]

# The harvest deliberately over-collects (the queries overlap and the arXiv
# relevance ranking has a long tail); CORPUS_BUDGET keeps the indexed set in
# the 100-250 range the brief asks for, by the relevance score below.
CORPUS_BUDGET = 220

# Full text is fetched for the seeds plus the highest-scoring papers.
FULLTEXT_BUDGET = 55

SCORE_TERMS = {
    "oriented matroid": 6, "chirotope": 6, "realizab": 6, "realization space": 5,
    "final polynomial": 6, "pseudoline": 4, "pseudohyperplane": 4,
    "mutation": 3, "tope": 4, "simplicial arrangement": 4,
    "enumerat": 3, "classification": 2, "catalog": 3, "census": 3,
    "polytope": 3, "zonotope": 4, "f-vector": 3, "neighborly": 3,
    "maxout": 8, "tropical": 2, "neural network": 1,
    "order type": 4, "point configuration": 3, "allowable sequence": 3,
    "Grassmann": 3, "matroid": 2, "partial cube": 3,
    "exhaustive": 3, "certificate": 2, "computer search": 3, "SAT": 1,
    "open problem": 3, "survey": 3, "conjecture": 2,
}

ATOM = "{http://www.w3.org/2005/Atom}"
ARX = "{http://arxiv.org/schemas/atom}"


# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------

def get(url: str, delay: float, tag: str) -> bytes | None:
    """One polite GET, with the delay applied *before* the request."""
    time.sleep(delay)
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    try:
        with urllib.request.urlopen(req, timeout=90) as r:
            return r.read()
    except urllib.error.HTTPError as e:
        print(f"  [{tag}] HTTP {e.code} {url}", file=sys.stderr)
    except Exception as e:                                   # noqa: BLE001
        print(f"  [{tag}] {e.__class__.__name__} {url}", file=sys.stderr)
    return None


def norm_id(arxiv_id: str) -> str:
    """1204.0645v2 -> 1204.0645 ; math/0503050v1 -> math/0503050"""
    return re.sub(r"v\d+$", "", arxiv_id.strip())


def doc_id_for(arxiv_id: str) -> str:
    """Discovery Engine document ids allow [A-Za-z0-9_-] only."""
    return "arxiv_" + re.sub(r"[^A-Za-z0-9]+", "_", norm_id(arxiv_id))


def strip_html(raw: str) -> str:
    """HTML -> readable text, keeping LaTeX for math.

    LaTeXML (arxiv.org/html and ar5iv) emits <math ... alttext="\\chi">MathML
    </math>.  Flattening the MathML gives token soup, so each <math> element
    is replaced by its alttext, i.e. by the author's LaTeX.
    """
    t = re.sub(r"(?is)<(script|style|head)\b.*?</\1>", " ", raw)

    def math_sub(m: re.Match) -> str:
        alt = m.group(1)
        return " $" + html.unescape(alt) + "$ "

    t = re.sub(r'(?is)<math\b[^>]*\balttext="([^"]*)"[^>]*>.*?</math>', math_sub, t)
    t = re.sub(r"(?is)<math\b[^>]*/>", " ", t)
    t = re.sub(r"(?is)<math\b.*?</math>", " ", t)
    t = re.sub(r"(?i)<(p|div|br|li|tr|h[1-6]|section|table)\b[^>]*>", "\n", t)
    t = re.sub(r"(?i)</(p|div|li|tr|h[1-6]|section|table)>", "\n", t)
    t = re.sub(r"(?i)</t[dh]>", " | ", t)
    t = re.sub(r"<[^>]+>", " ", t)
    t = html.unescape(t)
    t = t.replace(" ", " ")
    t = re.sub(r"[ \t\r\f\v]+", " ", t)
    t = re.sub(r"\n[ \t]*", "\n", t)
    t = re.sub(r"\n{3,}", "\n\n", t)
    return t.strip()


def strip_latex(raw: str) -> str:
    """LaTeX source -> text.  Deliberately light: LaTeX reads fine, and
    aggressive de-macroing destroys exactly the table cells we care about."""
    t = re.sub(r"(?m)(?<!\\)%.*$", "", raw)
    t = re.sub(r"(?s)\\begin\{comment\}.*?\\end\{comment\}", " ", t)
    t = re.sub(r"[ \t]+", " ", t)
    t = re.sub(r"\n{3,}", "\n\n", t)
    return t.strip()


def pdf_to_text(data: bytes) -> str | None:
    try:
        from pypdf import PdfReader                          # noqa: PLC0415
    except Exception:                                        # noqa: BLE001
        try:
            from PyPDF2 import PdfReader                     # type: ignore  # noqa: PLC0415
        except Exception:                                    # noqa: BLE001
            return None
    import io
    try:
        rd = PdfReader(io.BytesIO(data))
        return "\n\n".join((p.extract_text() or "") for p in rd.pages).strip()
    except Exception as e:                                   # noqa: BLE001
        print(f"  [pdf] {e.__class__.__name__}", file=sys.stderr)
        return None


def score(rec: dict) -> int:
    hay = (rec.get("title", "") + " " + rec.get("abstract", "")).lower()
    s = sum(w for term, w in SCORE_TERMS.items() if term.lower() in hay)
    if rec["arxiv_id"] in SEED_IDS:
        s += 1000
    return s


# ---------------------------------------------------------------------------
# stage 1: harvest
# ---------------------------------------------------------------------------

def parse_atom(xml_bytes: bytes) -> list[dict]:
    out = []
    try:
        root = ET.fromstring(xml_bytes)
    except ET.ParseError as e:
        print(f"  [atom] parse error {e}", file=sys.stderr)
        return out
    for e in root.findall(ATOM + "entry"):
        raw_id = (e.findtext(ATOM + "id") or "").rsplit("/abs/", 1)[-1]
        if not raw_id:
            continue
        aid = norm_id(raw_id)
        published = e.findtext(ATOM + "published") or ""
        cats = [c.get("term", "") for c in e.findall(ATOM + "category")]
        out.append(dict(
            arxiv_id=aid,
            version=raw_id,
            title=" ".join((e.findtext(ATOM + "title") or "").split()),
            abstract=" ".join((e.findtext(ATOM + "summary") or "").split()),
            authors="; ".join(
                (a.findtext(ATOM + "name") or "").strip()
                for a in e.findall(ATOM + "author")),
            year=int(published[:4]) if published[:4].isdigit() else 0,
            updated=(e.findtext(ATOM + "updated") or "")[:10],
            categories=", ".join(cats),
            doi=e.findtext(ARX + "doi") or "",
            journal_ref=e.findtext(ARX + "journal_ref") or "",
            url=f"https://arxiv.org/abs/{aid}",
        ))
    return out


def harvest() -> None:
    CACHE.mkdir(parents=True, exist_ok=True)
    records: dict[str, dict] = {}

    jobs = [("id_list=" + ",".join(SEED_IDS), None)]
    jobs += [(q, n) for q, n in QUERIES]

    for i, (q, n) in enumerate(jobs, 1):
        key = re.sub(r"[^a-z0-9]+", "_", q.lower())[:70]
        cf = CACHE / f"q_{key}.xml"
        if cf.exists() and cf.stat().st_size > 0:
            data = cf.read_bytes()
            print(f"[{i}/{len(jobs)}] cached  {q[:60]}")
        else:
            if q.startswith("id_list="):
                url = f"{ARXIV_API}?{q}&max_results=100"
            else:
                url = (f"{ARXIV_API}?search_query={urllib.parse.quote(q)}"
                       f"&start=0&max_results={n}&sortBy=relevance")
            data = get(url, ARXIV_API_DELAY, "arxiv-api")
            if not data:
                continue
            cf.write_bytes(data)
            print(f"[{i}/{len(jobs)}] fetched {q[:60]}")
        for rec in parse_atom(data):
            records.setdefault(rec["arxiv_id"], rec)

    (CACHE / "records.json").write_text(
        json.dumps(records, indent=1, ensure_ascii=False), encoding="utf-8")
    print(f"\nharvested {len(records)} distinct arXiv records "
          f"-> {CACHE / 'records.json'}")


# ---------------------------------------------------------------------------
# stage 2: full text
# ---------------------------------------------------------------------------

def selected_for_fulltext(records: dict[str, dict]) -> list[dict]:
    ranked = sorted(records.values(), key=score, reverse=True)
    return ranked[:FULLTEXT_BUDGET]


def fetch(limit: int | None = None) -> None:
    records = json.loads((CACHE / "records.json").read_text(encoding="utf-8"))
    ft = CACHE / "fulltext"
    ft.mkdir(parents=True, exist_ok=True)
    picks = selected_for_fulltext(records)
    if limit:
        picks = picks[:limit]
    print(f"full text for {len(picks)} of {len(records)} records")

    for i, rec in enumerate(picks, 1):
        aid = rec["arxiv_id"]
        dest = ft / (doc_id_for(aid) + ".txt")
        if dest.exists() and dest.stat().st_size > 2000:
            print(f"[{i}/{len(picks)}] cached  {aid}")
            continue
        ver = rec.get("version") or aid
        text = None
        # arXiv native HTML exists for submissions from Dec 2023 on.
        if rec.get("year", 0) >= 2023:
            raw = get(f"https://arxiv.org/html/{ver}", ARXIV_HTML_DELAY, "arxiv-html")
            if raw:
                cand = strip_html(raw.decode("utf-8", "replace"))
                if len(cand) > 4000:
                    text = cand
        if text is None:
            raw = get(f"https://ar5iv.labs.arxiv.org/html/{aid}", AR5IV_DELAY, "ar5iv")
            if raw:
                cand = strip_html(raw.decode("utf-8", "replace"))
                # ar5iv serves a stub page when it has no conversion
                if len(cand) > 4000 and "Failed to convert" not in cand[:4000]:
                    text = cand
        if text:
            dest.write_text(text, encoding="utf-8")
            print(f"[{i}/{len(picks)}] got {len(text):>7} chars  {aid}  {rec['title'][:50]}")
        else:
            print(f"[{i}/{len(picks)}] NO FULL TEXT           {aid}")

    for extra in EXTRA_URLS:
        dest = ft / (extra["doc_id"] + ".txt")
        if dest.exists() and dest.stat().st_size > 2000:
            print(f"cached  {extra['doc_id']}")
            continue
        raw = get(extra["url"], 5.0, "extra")
        if not raw:
            continue
        text = pdf_to_text(raw) if extra["kind"] == "pdf" else strip_html(
            raw.decode("utf-8", "replace"))
        if text and len(text) > 2000:
            dest.write_text(text, encoding="utf-8")
            print(f"got {len(text):>7} chars  {extra['doc_id']}")
        else:
            print(f"NO TEXT (extractor missing?)  {extra['doc_id']}")


# ---------------------------------------------------------------------------
# stage 3: emit
# ---------------------------------------------------------------------------

def emit(gcs_prefix: str, mime: str = "text/plain") -> None:
    records = json.loads((CACHE / "records.json").read_text(encoding="utf-8"))
    ft = CACHE / "fulltext"
    docs = OUT / "docs"
    docs.mkdir(parents=True, exist_ok=True)
    for old in docs.glob("*.txt"):
        old.unlink()

    ext = ".txt" if mime == "text/plain" else ".html"
    meta_lines, corpus_lines = [], []
    n_full = 0

    def add(doc_id, title, authors, year, arxiv_id, url, venue, source,
            abstract, body):
        nonlocal n_full
        header = (f"TITLE: {title}\nAUTHORS: {authors}\nYEAR: {year}\n"
                  f"ARXIV_ID: {arxiv_id}\nURL: {url}\nVENUE: {venue}\n"
                  f"SOURCE: {source}\n\nABSTRACT\n{abstract}\n\n")
        full = header + (body or "")
        if mime == "text/html":
            payload = ("<html><head><title>" + html.escape(title) +
                       "</title></head><body><pre>" + html.escape(full) +
                       "</pre></body></html>")
        else:
            payload = full
        (docs / (doc_id + ext)).write_text(payload, encoding="utf-8")
        struct = dict(title=title, authors=authors, year=year,
                      arxiv_id=arxiv_id, url=url, venue=venue,
                      source=source, has_full_text=bool(body),
                      doc_chars=len(full))
        meta_lines.append(json.dumps({
            "id": doc_id,
            "structData": struct,
            "content": {"mimeType": mime,
                        "uri": f"{gcs_prefix.rstrip('/')}/docs/{doc_id}{ext}"},
        }, ensure_ascii=False))
        corpus_lines.append(json.dumps(
            dict(id=doc_id, **struct, abstract=abstract, full_text=full),
            ensure_ascii=False))
        if body:
            n_full += 1

    keep = {r["arxiv_id"] for r in
            sorted(records.values(), key=score, reverse=True)[:CORPUS_BUDGET]}
    for aid, rec in sorted(records.items()):
        if aid not in keep:
            continue
        did = doc_id_for(aid)
        body_path = ft / (did + ".txt")
        body = body_path.read_text(encoding="utf-8") if body_path.exists() else ""
        add(did, rec["title"], rec["authors"], rec["year"], aid, rec["url"],
            rec.get("journal_ref") or rec.get("categories", ""),
            "arXiv API + arxiv.org/html" if body else "arXiv API (abstract only)",
            rec["abstract"], body)

    for src in LOCAL_SOURCES:
        p = REPO / src["path"]
        if not p.exists():
            print(f"  missing local source {p}", file=sys.stderr)
            continue
        raw = p.read_text(encoding="utf-8", errors="replace")
        body = strip_latex(raw) if src["kind"] == "latex_source" else strip_html(raw)
        add(src["doc_id"], src["title"], src["authors"], src["year"],
            src["arxiv_id"], src["url"], src["venue"],
            f"repo copy: {src['path']}", "", body)

    for extra in EXTRA_URLS:
        p = ft / (extra["doc_id"] + ".txt")
        if not p.exists():
            print(f"  no text for {extra['doc_id']} -- skipped", file=sys.stderr)
            continue
        add(extra["doc_id"], extra["title"], extra["authors"], extra["year"],
            extra["arxiv_id"], extra["url"], extra["venue"],
            extra["url"], "", p.read_text(encoding="utf-8"))

    (OUT / "metadata.jsonl").write_text("\n".join(meta_lines) + "\n", encoding="utf-8")
    (OUT / "corpus.jsonl").write_text("\n".join(corpus_lines) + "\n", encoding="utf-8")
    total = sum(f.stat().st_size for f in docs.glob("*" + ext))
    print(f"\n{len(meta_lines)} documents, {n_full} with full text")
    print(f"docs bytes  : {total:,} ({total/2**20:.1f} MiB)")
    print(f"metadata    : {(OUT/'metadata.jsonl').stat().st_size:,} bytes")
    print(f"corpus.jsonl: {(OUT/'corpus.jsonl').stat().st_size:,} bytes (local master, not uploaded)")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("stage", choices=["harvest", "fetch", "emit", "all"])
    ap.add_argument("--limit", type=int)
    ap.add_argument("--gcs-prefix",
                    default=os.environ.get("CORPUS_GCS_PREFIX", "gs://REPLACE-ME"))
    ap.add_argument("--mime", default="text/plain",
                    choices=["text/plain", "text/html"])
    a = ap.parse_args()
    if a.stage in ("harvest", "all"):
        harvest()
    if a.stage in ("fetch", "all"):
        fetch(a.limit)
    if a.stage in ("emit", "all"):
        emit(a.gcs_prefix, a.mime)


if __name__ == "__main__":
    main()
