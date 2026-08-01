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
    "2008.01032",   # Curto et al. -- restates Roudneff-Sturmfels' realizable
                    # connectivity at the LABELED level; the primary evidence
                    # for CITATION_AUDIT row on OMGAMMA.md Lemma 3
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

    # ---- scale-up 2026-08-01: same programme, wider net -------------------
    # A. oriented matroid theory and realizability
    ('all:"oriented matroids"', 120),
    ('all:"oriented matroid" AND all:"realization space"', 60),
    ('all:"oriented matroid" AND all:duality', 50),
    ('all:"oriented matroid" AND all:"single element extension"', 40),
    ('all:"oriented matroid" AND all:"Euclidean"', 40),
    ('all:"oriented matroid" AND all:"non-realizable"', 40),
    ('all:"oriented matroid" AND all:"matroid polytope"', 40),
    ('all:"oriented matroid" AND all:"tope"', 40),
    ('all:"oriented matroid" AND all:"sphere"', 40),
    ('all:"oriented matroid programming"', 25),
    ('all:"rank 3 oriented matroid" OR all:"rank three oriented matroid"', 30),
    ('all:"universality theorem" AND all:polytope', 30),
    ('all:"Mnev" OR all:"Mnev-Sturmfels"', 30),
    ('all:"Richter-Gebert" AND all:realization', 25),
    ('all:"stretchability" AND all:arrangement', 30),
    ('all:"wiring diagram" AND all:arrangement', 25),
    ('all:"line arrangement" AND cat:math.CO', 60),
    ('all:"hyperplane arrangement" AND all:enumeration', 50),
    ('all:"pseudohyperplane"', 25),
    ('all:"matroid" AND all:"axiomatization"', 40),
    ('all:"complex of oriented matroids" OR all:"COM"AND all:matroid', 25),
    ('all:"lopsided set" OR all:"conditional antimatroid"', 20),
    ('all:"affine oriented matroid"', 20),
    ('all:"signed circuit" AND all:matroid', 25),
    ('all:"Las Vergnas" AND all:matroid', 30),
    ('all:"Bjorner" AND all:matroid', 30),
    ('all:"shellability" AND all:complex', 40),
    # B. polytope combinatorics and f-vectors
    ('all:"f-vector"', 80),
    ('all:"flag f-vector"', 30),
    ('all:"cd-index"', 30),
    ('all:"g-theorem" OR all:"g-conjecture"', 30),
    ('all:"simplicial polytope" AND all:enumeration', 40),
    ('all:"cyclic polytope"', 40),
    ('all:"combinatorial type" AND all:polytope', 50),
    ('all:"polytope" AND all:"vertex count"', 40),
    ('all:"polytope" AND all:"upper bound theorem"', 30),
    ('all:"Minkowski sum" AND all:polytope', 50),
    ('all:"zonotope" AND all:"generators"', 40),
    ('all:"generalized permutohedron"', 40),
    ('all:"fiber polytope" OR all:"secondary polytope"', 30),
    ('all:"polytope" AND all:"realization space"', 40),
    ('all:"projectively unique polytope"', 20),
    ('all:"neighborly" AND all:"oriented matroid"', 25),
    ('all:"chamber" AND all:"central arrangement"', 30),
    ('all:"lattice polytope" AND all:classification', 40),
    # C. mutation graphs, flips, connectivity of combinatorial spaces
    ('all:"mutation" AND all:"oriented matroid"', 30),
    ('all:"flip graph" AND all:triangulation', 50),
    ('all:"flip graph" AND all:connectivity', 40),
    ('all:"simplicial cell" AND all:arrangement', 25),
    ('all:"Ringel" AND all:"homotopy theorem"', 20),
    ('all:"reorientation class"', 20),
    ('all:"triangle" AND all:"simple arrangement" AND all:lines', 25),
    ('all:"local move" AND all:"connected" AND all:combinatorial', 25),
    # D. chirotopes, Grassmann-Plucker, Plucker relations
    ('all:"Grassmann-Plucker relations"', 30),
    ('all:"Plucker" AND all:"three-term"', 25),
    ('all:"chirotope" AND all:realizability', 25),
    ('all:"final polynomial" AND all:"biquadratic"', 20),
    ('all:"positive Grassmannian" OR all:"totally positive Grassmannian"', 40),
    ('all:"matroid stratification"', 25),
    ('all:"tropical Grassmannian"', 30),
    ('all:"valuated matroid"', 40),
    ('all:"Positroid"', 40),
    # E. maxout / tropical / neural-network polytopes
    ('all:"maxout" AND all:network', 30),
    ('all:"neural network" AND all:polytope', 50),
    ('all:"ReLU" AND all:polytope', 40),
    ('all:"tropical geometry" AND all:"deep learning"', 30),
    ('all:"linear regions" AND all:"neural network"', 40),
    ('all:"expressivity" AND all:"piecewise linear"', 30),
    ('all:"tropical polynomial" AND all:"Newton polytope"', 30),
    ('all:"newton polytope" AND all:"max-plus"', 25),
    # F. exhaustive computation, catalogs, certificates, open-problem surveys
    ('all:"exhaustive enumeration" AND cat:math.CO', 50),
    ('all:"computer-assisted proof" AND all:combinatorics', 40),
    ('all:"SAT solver" AND all:combinatorial AND all:search', 40),
    ('all:"canonical augmentation" OR all:"orderly generation"', 25),
    ('all:"isomorph-free exhaustive generation"', 20),
    ('all:"catalogue" OR all:"catalog" AND all:matroid', 30),
    ('all:"unavoidable" AND all:"open problem" AND cat:math.CO', 25),
    ('all:"survey" AND all:"discrete and computational geometry"', 40),
    ('all:"research problems" AND all:"discrete geometry"', 25),
    ('all:"order type" AND all:"realizability"', 30),
    ('all:"abstract order type"', 25),
    ('all:"point set" AND all:"order type" AND all:database', 25),
    ('all:"crossing number" AND all:"complete graph"', 40),
    ('all:"Erdos-Szekeres" AND all:"convex position"', 30),
    ('cat:cs.CG AND all:"oriented matroid"', 40),
    ('cat:cs.CG AND all:"arrangement"', 60),
    ('cat:cs.CG AND all:"realizability"', 30),
    ('cat:math.CO AND all:"partial cube"', 30),
    ('cat:math.CO AND all:"lattice of flats"', 30),
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
    # The other EJC dynamic surveys in or near this programme's areas.  The
    # index is at .../issue/view/Surveys; combinatorics.org/robots.txt names
    # only a handful of commercial crawlers and this is not one of them, so
    # these are permitted; a 10 s delay is used anyway.  All are PDFs, so the
    # table renderer above does NOT apply to them (pypdf yields no cell
    # structure) -- see CORPUS.md section 8.
    dict(doc_id="ejc_ds21_graph_crossing_number",
         url="https://www.combinatorics.org/ojs/index.php/eljc/article/download/DS21/pdf/",
         title="The Graph Crossing Number and its Variants: A Survey (EJC Dynamic Survey DS21)",
         authors="Marcus Schaefer", year=2024, arxiv_id="",
         venue="Electron. J. Combin., Dynamic Survey DS21", kind="pdf"),
    dict(doc_id="ejc_ds12_macaulay_posets",
         url="https://www.combinatorics.org/ojs/index.php/eljc/article/download/DS12/pdf/",
         title="Macaulay Posets (EJC Dynamic Survey DS12)",
         authors="Sergei L. Bezrukov; Xavier Portas", year=2002, arxiv_id="",
         venue="Electron. J. Combin., Dynamic Survey DS12", kind="pdf"),
    dict(doc_id="ejc_ds7_packing_unit_squares",
         url="https://www.combinatorics.org/ojs/index.php/eljc/article/view/DS7/html_1",
         title="Packing Unit Squares in Squares: A Survey and New Results (EJC Dynamic Survey DS7)",
         authors="Erich Friedman", year=2009, arxiv_id="",
         venue="Electron. J. Combin., Dynamic Survey DS7", kind="html"),
    dict(doc_id="ejc_ds1_small_ramsey_numbers",
         url="https://www.combinatorics.org/ojs/index.php/eljc/article/download/DS1/pdf/",
         title="Small Ramsey Numbers (EJC Dynamic Survey DS1)",
         authors="Stanislaw P. Radziszowski", year=2024, arxiv_id="",
         venue="Electron. J. Combin., Dynamic Survey DS1", kind="pdf"),

    # Finschi's catalog, the primary source for every published small-case
    # oriented-matroid count.  finschi.com/robots.txt is `allow: /math`,
    # `disallow: /`; these are all under /math and are fetched at 10 s.
    # They are HTML, so the table renderer DOES apply -- which is the whole
    # point, since the (4,9) fabrication came from exactly these tables.
    dict(doc_id="finschi_catom_all",
         url="https://finschi.com/math/om/?p=catom",
         title="Catalog of Oriented Matroids -- all isomorphism classes (L. Finschi)",
         authors="Lukas Finschi", year=2024, arxiv_id="",
         venue="web catalog, finschi.com/math/om", kind="html"),
    dict(doc_id="finschi_catom_nondeg",
         url="https://finschi.com/math/om/?p=catom&filter=nondeg",
         title="Catalog of Oriented Matroids -- non-degenerate (uniform) classes (L. Finschi)",
         authors="Lukas Finschi", year=2024, arxiv_id="",
         venue="web catalog, finschi.com/math/om", kind="html"),
    dict(doc_id="finschi_catpc",
         url="https://finschi.com/math/om/?p=catpc",
         title="Catalog of Point Configurations (L. Finschi)",
         authors="Lukas Finschi", year=2024, arxiv_id="",
         venue="web catalog, finschi.com/math/om", kind="html"),
    dict(doc_id="finschi_catha",
         url="https://finschi.com/math/om/?p=catha",
         title="Catalog of Hyperplane Arrangements (L. Finschi)",
         authors="Lukas Finschi", year=2024, arxiv_id="",
         venue="web catalog, finschi.com/math/om", kind="html"),
    # The two glossary entries the project's conventions actually rest on:
    # the basis order and the canonical representative, and what an
    # "isomorphism class" means in the catalog whose counts we compare against.
    dict(doc_id="finschi_glossary_revlex",
         url="https://finschi.com/math/om/?p=bib&glo=revlex",
         title="Homepage of Oriented Matroids -- glossary: RevLex-Index (L. Finschi)",
         authors="Lukas Finschi", year=2024, arxiv_id="",
         venue="web catalog, finschi.com/math/om", kind="html"),
    dict(doc_id="finschi_glossary_isom",
         url="https://finschi.com/math/om/?p=bib&glo=isom",
         title="Homepage of Oriented Matroids -- glossary: Isomorphism Class (L. Finschi)",
         authors="Lukas Finschi", year=2024, arxiv_id="",
         venue="web catalog, finschi.com/math/om", kind="html"),
    dict(doc_id="finschi_glossary_relabel",
         url="https://finschi.com/math/om/?p=bib&glo=relabel",
         title="Homepage of Oriented Matroids -- glossary: Relabeling Class (L. Finschi)",
         authors="Lukas Finschi", year=2024, arxiv_id="",
         venue="web catalog, finschi.com/math/om", kind="html"),
    dict(doc_id="finschi_glossary",
         url="https://finschi.com/math/om/?p=bib",
         title="Homepage of Oriented Matroids -- glossary and bibliography (L. Finschi)",
         authors="Lukas Finschi", year=2024, arxiv_id="",
         venue="web catalog, finschi.com/math/om", kind="html"),
]

EXTRA_DELAY = 10.0             # neither host publishes a Crawl-delay

# The harvest deliberately over-collects (the queries overlap and the arXiv
# relevance ranking has a long tail); CORPUS_BUDGET keeps the indexed set in
# the 100-250 range the brief asks for, by the relevance score below.
CORPUS_BUDGET = 2000

# Full text is fetched for the seeds plus the highest-scoring papers.
FULLTEXT_BUDGET = 330

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


# ---------------------------------------------------------------------------
# TABLE RENDERING -- the fix for CORPUS.md section 8, defect 1.
#
# The measured failure was an extraction failure, not a model failure: a table
# row was flattened to a bare sequence of numbers, the leading cells that the
# markup expressed as COLSPAN (HTML) or as empty `&` cells (LaTeX) vanished,
# and a reader counting from the header landed one column late.  The concrete
# casualty: Finschi's rank-4 row is
#
#   <TH COLSPAN="3">rank = 4</TH><TD>1</TD>...<TD>9 276 595</TD><TD>unknown</TD>
#
# against a `card = 2 ... card = 10` header.  The COLSPAN=3 header cell
# occupies columns 0,1,2, so the first <TD> is column 3 = `card = 4` and
# 9,276,595 is the **9**-element count, not the 10-element one.
#
# The fix renders every table cell by cell, each value carrying its own column
# header AND its own column index, so no counting is ever required:
#
#   [TABLE 3 ROW 4] rank = 4 (dim = 3) || ... || card = 9 [col 9]: 9 276 595
#
# Empty cells are emitted as `(blank)` rather than dropped, and the caption is
# attached to the block -- the second half of the same defect was cross-TABLE
# confusion (FMM13's dimension-indexed polytope table read as its
# rank-indexed oriented-matroid table, which is where `1142` came from).
# ---------------------------------------------------------------------------

MAX_TABLE_ROWS = 400           # guard against pathological generated tables
MAX_TABLE_COLS = 60
MAX_CELL_CHARS = 300


def _clip(s: str, n: int) -> str:
    """Truncate on a word boundary.  Chopping mid-word cost us a real answer:
    `...brackets are those of simplici` dropped the word `polytopes`, which is
    the only thing distinguishing that table's bracket semantics from the
    oriented-matroid table's."""
    if len(s) <= n:
        return s
    cut = s[:n]
    sp = cut.rfind(" ")
    return (cut[:sp] if sp > n * 0.6 else cut) + " ..."


def _cell_text(inner: str) -> str:
    """Cell payload -> one line of readable text."""
    t = re.sub(r"(?is)<(script|style)\b.*?</\1>", " ", inner)
    t = re.sub(r"(?i)<br\b[^>]*>", " / ", t)
    t = re.sub(r"<[^>]+>", " ", t)
    t = html.unescape(t)
    t = t.replace("\xa0", " ").replace("\u2009", " ").replace("\u202f", " ")
    return " ".join(t.split())[:MAX_CELL_CHARS]


def _span_of(attrs: str, name: str) -> int:
    m = re.search(r'(?i)\b' + name + r'\s*=\s*["\']?(\d+)', attrs)
    if not m:
        return 1
    try:
        return max(1, min(int(m.group(1)), MAX_TABLE_COLS))
    except ValueError:
        return 1


def _split_cells(row_html: str) -> list:
    """(kind, colspan, rowspan, text) per cell.  Tolerant of missing </td>."""
    opens = list(re.finditer(r"(?is)<(t[dh])\b([^>]*)>", row_html))
    cells = []
    for i, m in enumerate(opens):
        end = opens[i + 1].start() if i + 1 < len(opens) else len(row_html)
        inner = row_html[m.end():end]
        close = re.search(r"(?is)</t[dh]\s*>", inner)
        if close:
            inner = inner[:close.start()]
        attrs, kind = m.group(2), m.group(1).lower()
        if "ltx_th" in attrs:          # LaTeXML marks header cells this way
            kind = "th"
        cells.append((kind, _span_of(attrs, "colspan"),
                      _span_of(attrs, "rowspan"), _cell_text(inner)))
    return cells


def _split_rows(table_inner: str) -> list:
    opens = list(re.finditer(r"(?is)<tr\b[^>]*>", table_inner))
    if not opens:
        return [table_inner] if re.search(r"(?is)<t[dh]\b", table_inner) else []
    rows = []
    for i, m in enumerate(opens):
        end = opens[i + 1].start() if i + 1 < len(opens) else len(table_inner)
        rows.append(table_inner[m.end():end])
    return rows


def _render_grid(grid: dict, nrows: int, ncols: int, header_row,
                 caption: str, tag: str) -> str:
    """Common back end for the HTML and LaTeX renderers.

    `grid[(r, c)] = (kind, text)` for the cell anchored at (r, c); every
    further column a cell spans holds ("cont", "") so a spanned-over column
    is still visibly a column and the anchors keep their true indices.
    """
    # LaTeXML wraps every display equation in a <table>, and LaTeX \begin{array}
    # is a tabular too.  Labelling those as tables buries the real tables in
    # noise and inflates the index for nothing.  A block with no caption, no
    # header row and at most one populated cell per row is not a table of
    # values -- emit its contents plainly.
    filled = {}
    for (r, c), v in grid.items():
        if v[0] != "cont" and v[1]:
            filled.setdefault(r, []).append((c, v[1]))
    if not caption and header_row is None and all(
            len(cs) <= 1 for cs in filled.values()):
        body = "\n".join(filled[r][0][1] for r in sorted(filled))
        return ("\n" + body + "\n") if body else " "

    col_label: dict = {}
    if header_row is not None:
        for c in range(ncols):
            v = grid.get((header_row, c))
            if v and v[0] != "cont" and v[1]:
                last = c
                while (last + 1 < ncols
                       and grid.get((header_row, last + 1), ("", ""))[0] == "cont"):
                    last += 1
                for cc in range(c, last + 1):
                    col_label[cc] = v[1]

    out = ["[" + tag + "]"]
    if caption:
        out.append(f"[{tag} CAPTION] {caption}")
    if col_label:
        out.append(f"[{tag} COLUMNS] " + " ; ".join(
            f"col {c+1} = {col_label[c]}" for c in sorted(col_label)))

    for r in range(nrows):
        # NOTE: the header row is emitted as a row too, not skipped.  Header
        # detection is a heuristic; if it misfires on a data row, dropping
        # that row would silently delete a value.  One duplicated line is a
        # much cheaper failure than a missing number.
        first = grid.get((r, 0))
        row_label, start_c = "", 0
        if first and first[0] == "th":
            row_label = first[1] or "(blank)"
            start_c = 1
            while (start_c < ncols
                   and grid.get((r, start_c), ("", ""))[0] == "cont"):
                start_c += 1
        parts = []
        for c in range(start_c, ncols):
            v = grid.get((r, c))
            if v is None or v[0] == "cont":
                continue
            txt = v[1] if v[1] else "(blank)"
            label = col_label.get(c, "")
            parts.append((f"{label} [col {c+1}]: {txt}") if label
                         else f"col {c+1}: {txt}")
        if not parts and not row_label:
            continue
        # The caption is repeated on EVERY row, not printed once at the top.
        # Discovery Engine chunks a document before indexing it, so a caption
        # line and a value line can land in different chunks -- which is how
        # `1142` (a simplicial-POLYTOPE count) survived the column fix and was
        # still read as an oriented-matroid count.  A self-describing row
        # cannot be separated from what it is a row of.
        head = f"[{tag} ROW {r+1}]"
        if caption:
            head += f" (table: {_clip(caption, 220)})"
        if row_label:
            head += f" {row_label} ||"
        out.append(head + " " + " || ".join(parts))
    out.append(f"[END {tag}]")
    return "\n" + "\n".join(out) + "\n"


def render_html_table(table_inner: str, tag: str, attrs: str = "") -> str:
    # LaTeXML marks its equation wrappers explicitly; honour that rather than
    # guessing from shape, and flatten them back to plain math.
    if re.search(r"ltx_(equation|eqn)", attrs, re.I):
        cells = [txt for row in _split_rows(table_inner)
                 for (_k, _cs, _rs, txt) in _split_cells(row) if txt]
        return ("\n" + " ".join(cells) + "\n") if cells else " "
    cap = re.search(r"(?is)<caption\b[^>]*>(.*?)</caption\s*>", table_inner)
    caption = _cell_text(cap.group(1)) if cap else ""
    if cap:
        table_inner = table_inner[:cap.start()] + table_inner[cap.end():]

    rows = _split_rows(table_inner)[:MAX_TABLE_ROWS]
    grid: dict = {}
    occupied: set = set()
    ncols = 0
    for r, row_html in enumerate(rows):
        c = 0
        for (kind, cs, rs, text) in _split_cells(row_html):
            while (r, c) in occupied:
                c += 1
            if c >= MAX_TABLE_COLS:
                break
            for dr in range(rs):
                for dc in range(cs):
                    occupied.add((r + dr, c + dc))
                    if (dr, dc) != (0, 0):
                        grid[(r + dr, c + dc)] = ("cont", "")
            grid[(r, c)] = (kind, text)
            c += cs
            ncols = max(ncols, c)
    if not grid:
        return " "

    header_row = None
    for r in range(min(2, len(rows))):
        anchors = [v for (rr, cc), v in grid.items() if rr == r and v[0] != "cont"]
        if len(anchors) >= 2 and all(v[0] == "th" for v in anchors):
            header_row = r
            break
    if header_row is None and ncols >= 2 and len(rows) >= 2:
        # LaTeXML frequently emits an all-<td> table whose first row is the
        # header and whose first column is the row stub (arXiv's own HTML for
        # FMM13 and Knauer-Marc is exactly this shape).
        first = [grid.get((0, c), ("", "")) for c in range(ncols)]
        if not first[0][1] and sum(1 for v in first[1:] if v[1]) >= 2:
            header_row = 0
            for c in range(ncols):
                if grid.get((0, c), ("", ""))[0] == "td":
                    grid[(0, c)] = ("th", grid[(0, c)][1])
    if header_row is not None and not grid.get((header_row, 0), ("", ""))[1]:
        # blank top-left corner => column 0 holds row labels
        for r in range(len(rows)):
            if r != header_row and grid.get((r, 0), ("", ""))[0] == "td":
                grid[(r, 0)] = ("th", grid[(r, 0)][1])
    return _render_grid(grid, len(rows), ncols, header_row, caption, tag)


def _hoist_figcaptions(t: str) -> str:
    """LaTeXML (arxiv.org/html, ar5iv) puts a table's caption in a
    <figcaption> SIBLING of the <table>, so the plain <caption> lookup misses
    it and every arXiv-sourced table loses the one line that says which table
    it is.  Rewrite each figcaption into a <caption> inside the table it
    belongs to.  The pairing is done strictly INSIDE one <figure> element,
    because LaTeXML puts the caption above the table in some versions and
    below it in others: a positional rule gets it right on one and silently
    off-by-one on the other, which is the same class of mis-attachment this
    whole section exists to remove."""
    out, pos = [], 0
    for fig in re.finditer(r"(?is)<figure\b[^>]*>(.*?)</figure\s*>", t):
        body = fig.group(1)
        cm = re.search(r"(?is)<figcaption\b[^>]*>(.*?)</figcaption\s*>", body)
        tm = re.search(r"(?is)<table\b[^>]*>", body)
        if not cm or not tm:
            continue
        cap = _cell_text(cm.group(1))
        if not cap:
            continue
        body = body[:cm.start()] + " " + body[cm.end():]
        tm = re.search(r"(?is)<table\b[^>]*>", body)
        if not tm:
            continue
        body = (body[:tm.end()] + "<caption>" + cap.replace("<", " ")
                + "</caption>" + body[tm.end():])
        out.append(t[pos:fig.start()])
        out.append("<figure>" + body + "</figure>")
        pos = fig.end()
    out.append(t[pos:])
    return "".join(out)


def render_all_html_tables(t: str, prefix: str = "TABLE") -> str:
    """Replace every <table> with a rendered block, innermost first so that
    nested layout tables (Finschi's page has three levels) come out right."""
    t = _hoist_figcaptions(t)
    blocks: dict = {}
    n = 0
    for _ in range(400):                       # bounded; tables are finite
        close = re.search(r"(?is)</table\s*>", t)
        if not close:
            break
        opens = list(re.finditer(r"(?is)<table\b[^>]*>", t[:close.start()]))
        if not opens:
            t = t[:close.start()] + " " + t[close.end():]
            continue
        op = opens[-1]
        n += 1
        blocks[n] = render_html_table(t[op.end():close.start()],
                                      f"{prefix} {n}", op.group(0))
        # A marker, not the block itself: an inner table sitting inside an
        # outer table's cell would otherwise be collapsed onto one line by the
        # outer renderer's cell-text pass, which is the very flattening this
        # whole function exists to prevent.
        t = t[:op.start()] + f"\n@@TBL{n}@@\n" + t[close.end():]
    t = re.sub(r"(?is)</?table\b[^>]*>", "\n", t)
    for _ in range(8):                         # markers can nest a few deep
        if "@@TBL" not in t:
            break
        t = re.sub(r"@@TBL(\d+)@@",
                   lambda m: blocks.get(int(m.group(1)), " "), t)
    return t


# --- the same fix on the LaTeX side ----------------------------------------

def _tex_split(s: str, sep: str) -> list:
    r"""Split on `sep` only at brace depth 0, honouring backslash escapes.

    Needed because FMM13's cells are `\shortstack{unknown \\ (1142)}` -- a row
    separator living inside a cell.  Naive splitting on `\\` shreds the row.
    """
    parts, buf, depth, i, n = [], [], 0, 0, len(s)
    while i < n:
        ch = s[i]
        if ch == "\\" and i + 1 < n:
            nxt = s[i + 1]
            if nxt == "\\":
                if sep == "\\\\" and depth == 0:
                    parts.append("".join(buf))
                    buf = []
                    i += 2
                    while i < n and s[i] in " \t":
                        i += 1
                    if s[i:i + 1] == "[":            # \\[2pt] spacing argument
                        j = s.find("]", i)
                        if 0 < j < i + 20:
                            i = j + 1
                    continue
                buf.append("\\\\")
                i += 2
                continue
            if nxt in "&%${}_#":
                buf.append(ch)
                buf.append(nxt)
                i += 2
                continue
        if ch == "{":
            depth += 1
        elif ch == "}":
            depth = max(0, depth - 1)
        elif ch == "&" and sep == "&" and depth == 0:
            parts.append("".join(buf))
            buf = []
            i += 1
            continue
        buf.append(ch)
        i += 1
    parts.append("".join(buf))
    return parts


_TEX_RULES = r"\\(hline|toprule|midrule|bottomrule|cline\s*\{[^}]*\}|noalign\s*\{[^}]*\})"


def _tex_cell(s: str) -> str:
    s = re.sub(_TEX_RULES, " ", s)
    s = re.sub(r"\\(shortstack|makecell|textbf|textit|emph|mathbf|scriptsize|"
               r"small|footnotesize|centering|bf|it|rm|tt)\b\s*", " ", s)
    s = s.replace("\\\\", " / ")
    s = s.replace("{", " ").replace("}", " ")
    return " ".join(s.split())[:MAX_CELL_CHARS]


def render_tex_tabular(body: str, caption: str, tag: str) -> str:
    grid: dict = {}
    nrows = ncols = 0
    for row_src in _tex_split(body, "\\\\")[:MAX_TABLE_ROWS]:
        if not re.sub(_TEX_RULES + r"|\s", "", row_src):
            continue
        r, nrows = nrows, nrows + 1
        c = 0
        for raw_cell in _tex_split(row_src, "&"):
            mc = re.match(r"(?s)\s*\\multicolumn\s*\{(\d+)\}\s*\{[^{}]*\}\s*\{(.*)\}\s*$",
                          raw_cell)
            span, payload = 1, raw_cell
            if mc:
                span = max(1, min(int(mc.group(1)), MAX_TABLE_COLS))
                payload = mc.group(2)
            if c >= MAX_TABLE_COLS:
                break
            grid[(r, c)] = ("td", _tex_cell(payload))
            for dc in range(1, span):
                grid[(r, c + dc)] = ("cont", "")
            c += span
            ncols = max(ncols, c)
    if not grid:
        return " "

    # In a LaTeX tabular the first row is the header exactly when its leading
    # cell is empty and the rest are not -- FMM13's `& n = 3 & n = 4 & ...`.
    header_row = None
    first = [grid.get((0, c), ("", "")) for c in range(ncols)]
    if ncols >= 2 and not first[0][1] and any(v[1] for v in first[1:]):
        header_row = 0
        for c in range(ncols):
            if grid.get((0, c), ("", ""))[0] == "td":
                grid[(0, c)] = ("th", grid[(0, c)][1])
        for r in range(nrows):
            if grid.get((r, 0), ("", ""))[0] == "td":
                grid[(r, 0)] = ("th", grid[(r, 0)][1])
    return _render_grid(grid, nrows, ncols, header_row, caption, tag)


def render_all_tex_tables(t: str) -> str:
    r"""Render every tabular, carrying its \caption{} into the block."""
    # Map each enclosing table environment to ITS caption first.  Taking the
    # nearest \caption in a character window instead gives every tabular the
    # caption of whichever table happens to be closest, which is exactly the
    # cross-table confusion that produced the 1142 error in the first place.
    envs = []
    for em in re.finditer(r"(?s)\\begin\{(table\*?|figure\*?)\}(?:\[[^\]]*\])?"
                          r"(.*?)\\end\{\1\}", t):
        cm = re.search(r"(?s)\\caption\s*(?:\[[^\]]*\])?\{", em.group(2))
        cap = ""
        if cm:
            i, depth, start = cm.end(), 1, cm.end()
            while i < len(em.group(2)) and depth:
                ch = em.group(2)[i]
                if ch == "{":
                    depth += 1
                elif ch == "}":
                    depth -= 1
                i += 1
            cap = _tex_cell(em.group(2)[start:i - 1])
        lm = re.search(r"\\label\s*\{([^}]*)\}", em.group(2))
        if lm:
            cap = (cap + f"  [label: {lm.group(1)}]").strip()
        envs.append((em.start(), em.end(), cap))

    def caption_for(a: int, b: int) -> str:
        for s, e, cap in envs:
            if s <= a and b <= e:
                return cap
        return ""

    out, pos, n = [], 0, 0
    pat = (r"(?s)\\begin\{(tabular\*?|array|longtable)\}"
           r"(?:\[[^\]]*\])?[ \t\n]*(?:\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\})?"
           r"(.*?)\\end\{\1\}")
    for m in re.finditer(pat, t):
        n += 1
        out.append(t[pos:m.start()])
        out.append(render_tex_tabular(m.group(2),
                                      caption_for(m.start(), m.end()),
                                      f"TABLE {n}"))
        pos = m.end()
    out.append(t[pos:])
    return "".join(out)


def strip_html(raw: str) -> str:
    """HTML -> readable text, keeping LaTeX for math and structure for tables.

    LaTeXML (arxiv.org/html and ar5iv) emits <math ... alttext="\\chi">MathML
    </math>.  Flattening the MathML gives token soup, so each <math> element
    is replaced by its alttext, i.e. by the author's LaTeX -- and that happens
    BEFORE the tables are rendered, so cells keep the author's own math.
    """
    t = re.sub(r"(?is)<(script|style|head)\b.*?</\1>", " ", raw)

    def math_sub(m: re.Match) -> str:
        alt = m.group(1)
        return " $" + html.unescape(alt) + "$ "

    t = re.sub(r'(?is)<math\b[^>]*\balttext="([^"]*)"[^>]*>.*?</math>', math_sub, t)
    t = re.sub(r"(?is)<math\b[^>]*/>", " ", t)
    t = re.sub(r"(?is)<math\b.*?</math>", " ", t)

    t = render_all_html_tables(t)          # <-- the defect-1 fix; see above

    t = re.sub(r"(?i)<(p|div|br|li|tr|h[1-6]|section)\b[^>]*>", "\n", t)
    t = re.sub(r"(?i)</(p|div|li|tr|h[1-6]|section)>", "\n", t)
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
    aggressive de-macroing destroys exactly the table cells we care about.

    Tabulars are rendered cell by cell with header labels and column indices
    (CORPUS.md section 8, defect 1), with the caption carried into the block."""
    t = re.sub(r"(?m)(?<!\\)%.*$", "", raw)
    t = re.sub(r"(?s)\\begin\{comment\}.*?\\end\{comment\}", " ", t)
    t = render_all_tex_tables(t)
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
    """Fetch full text.  The RAW HTML is kept in cache/raw/, and the text is
    re-extracted from it at emit time -- so an extraction fix (such as the
    table renderer above) applies retroactively to every already-fetched
    paper without re-crawling anything at 15 s a document."""
    records = json.loads((CACHE / "records.json").read_text(encoding="utf-8"))
    ft = CACHE / "fulltext"
    raw_dir = CACHE / "raw"
    ft.mkdir(parents=True, exist_ok=True)
    raw_dir.mkdir(parents=True, exist_ok=True)
    picks = selected_for_fulltext(records)
    if limit:
        picks = picks[:limit]
    print(f"full text for {len(picks)} of {len(records)} records")

    for i, rec in enumerate(picks, 1):
        aid = rec["arxiv_id"]
        did = doc_id_for(aid)
        dest = ft / (did + ".txt")
        rawdest = raw_dir / (did + ".html")
        if rawdest.exists() and rawdest.stat().st_size > 4000:
            print(f"[{i}/{len(picks)}] cached(raw) {aid}")
            continue
        if dest.exists() and dest.stat().st_size > 2000:
            # legacy cache entry with no raw copy: keep it, do not re-crawl
            print(f"[{i}/{len(picks)}] cached(txt) {aid}")
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
                    rawdest.write_bytes(raw)
        if text is None:
            raw = get(f"https://ar5iv.labs.arxiv.org/html/{aid}", AR5IV_DELAY, "ar5iv")
            if raw:
                cand = strip_html(raw.decode("utf-8", "replace"))
                # ar5iv serves a stub page when it has no conversion
                if len(cand) > 4000 and "Failed to convert" not in cand[:4000]:
                    text = cand
                    rawdest.write_bytes(raw)
        if text:
            dest.write_text(text, encoding="utf-8")
            print(f"[{i}/{len(picks)}] got {len(text):>7} chars  {aid}  {rec['title'][:50]}")
        else:
            print(f"[{i}/{len(picks)}] NO FULL TEXT           {aid}")

    for extra in EXTRA_URLS:
        dest = ft / (extra["doc_id"] + ".txt")
        rawdest = raw_dir / (extra["doc_id"] + ".html")
        if dest.exists() and dest.stat().st_size > 2000:
            print(f"cached  {extra['doc_id']}")
            continue
        raw = get(extra["url"], EXTRA_DELAY, "extra")
        if not raw:
            continue
        if extra["kind"] == "pdf":
            # pypdf gives no table structure; nothing downstream can recover
            # it, so PDF-sourced documents keep the known table defect.
            text = pdf_to_text(raw)
        else:
            rawdest.write_bytes(raw)
            text = strip_html(raw.decode("utf-8", "replace"))
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
    raw_dir = CACHE / "raw"
    n_raw = 0
    for aid, rec in sorted(records.items()):
        if aid not in keep:
            continue
        did = doc_id_for(aid)
        body_path = ft / (did + ".txt")
        raw_path = raw_dir / (did + ".html")
        if raw_path.exists() and raw_path.stat().st_size > 4000:
            # re-extract from the stored HTML, so extraction fixes are
            # retroactive with no re-crawl (see fetch()'s docstring)
            body = strip_html(raw_path.read_text(encoding="utf-8", errors="replace"))
            n_raw += 1
        else:
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
    print(f"\n{len(meta_lines)} documents, {n_full} with full text "
          f"({n_raw} re-extracted from cached raw HTML)")
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
