#!/usr/bin/env python3
"""Stage the corpus to GCS and import it into the Discovery Engine data store.

Stdlib only; authenticates by shelling out to `gcloud auth print-access-token`.

    python ingest.py upload                  # out/docs + out/metadata.jsonl -> GCS
    python ingest.py import                  # GCS -> data store (INCREMENTAL)
    python ingest.py import --reconcile FULL # replace the branch contents
    python ingest.py status <operation-name>
    python ingest.py count                   # documents currently in the branch
    python ingest.py size                    # measured GCS bytes

Cost note: `upload` and `import` touch Cloud Storage Class A/B operations
(fractions of a cent) and the Agent Search index-storage SKU (first 10 GiB
per account per month free).  Neither the OCR parser nor the Layout Parser is
enabled on the data store -- see CORPUS.md section 1.
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import urllib.request
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
OUT = HERE / "out"

PROJECT = os.environ.get("CORPUS_PROJECT", "project-ebd5a273-53ea-4c8b-81a")
BUCKET = os.environ.get("CORPUS_BUCKET", "fc-litcorpus-ebd5a273")
DATA_STORE = os.environ.get("CORPUS_DATA_STORE", "finite-certificates-lit")
COLLECTION = "default_collection"
BRANCH = "default_branch"
API = "https://discoveryengine.googleapis.com/v1"

BASE = (f"projects/{PROJECT}/locations/global/collections/{COLLECTION}"
        f"/dataStores/{DATA_STORE}")


def token() -> str:
    return subprocess.run(["gcloud", "auth", "print-access-token"],
                          capture_output=True, text=True, check=True,
                          shell=(os.name == "nt")).stdout.strip()


def api(method: str, path: str, body: dict | None = None) -> dict:
    req = urllib.request.Request(
        f"{API}/{path}",
        data=json.dumps(body).encode() if body is not None else None,
        method=method,
        headers={"Authorization": f"Bearer {token()}",
                 "Content-Type": "application/json",
                 "X-Goog-User-Project": PROJECT})
    try:
        with urllib.request.urlopen(req, timeout=180) as r:
            return json.loads(r.read() or b"{}")
    except urllib.error.HTTPError as e:
        sys.stderr.write(e.read().decode("utf-8", "replace") + "\n")
        raise


def sh(*cmd: str) -> str:
    p = subprocess.run(cmd, capture_output=True, text=True,
                       shell=(os.name == "nt"))
    sys.stdout.write(p.stdout)
    if p.returncode:
        sys.stderr.write(p.stderr)
        raise SystemExit(p.returncode)
    return p.stdout


def cmd_upload() -> None:
    docs = OUT / "docs"
    n = len(list(docs.glob("*")))
    total = sum(f.stat().st_size for f in docs.glob("*"))
    print(f"uploading {n} document files, {total:,} bytes "
          f"({total / 2**20:.2f} MiB) to gs://{BUCKET}/docs/")
    sh("gcloud", "storage", "rsync", "--delete-unmatched-destination-objects",
       "--recursive", str(docs), f"gs://{BUCKET}/docs")
    sh("gcloud", "storage", "cp", str(OUT / "metadata.jsonl"),
       f"gs://{BUCKET}/metadata.jsonl")


def cmd_import(reconcile: str) -> None:
    body = {
        "gcsSource": {"inputUris": [f"gs://{BUCKET}/metadata.jsonl"],
                      "dataSchema": "document"},
        "reconciliationMode": reconcile,
    }
    op = api("POST", f"{BASE}/branches/{BRANCH}/documents:import", body)
    print(json.dumps(op, indent=1)[:1500])
    print("\npoll with:  python ingest.py status " + op.get("name", "?"))


def cmd_status(name: str) -> None:
    print(json.dumps(api("GET", name), indent=1)[:4000])


def cmd_count() -> None:
    tot, page = 0, ""
    while True:
        q = f"{BASE}/branches/{BRANCH}/documents?pageSize=1000"
        if page:
            q += f"&pageToken={page}"
        r = api("GET", q)
        tot += len(r.get("documents", []))
        page = r.get("nextPageToken", "")
        if not page:
            break
    print(f"{tot} documents in {BASE}/branches/{BRANCH}")


def cmd_size() -> None:
    out = sh("gcloud", "storage", "du", "--summarize", "--readable-sizes",
             f"gs://{BUCKET}")
    raw = sh("gcloud", "storage", "du", "--summarize", f"gs://{BUCKET}")
    b = int(raw.split()[0])
    print(f"exact: {b:,} bytes = {b / 1e9:.6f} GB = {b / 2**30:.6f} GiB")
    print(f"standard storage us-central1 @ $0.020/GB/month = "
          f"${b / 1e9 * 0.020:.6f} per month")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("cmd", choices=["upload", "import", "status", "count", "size"])
    ap.add_argument("arg", nargs="?")
    ap.add_argument("--reconcile", default="INCREMENTAL",
                    choices=["INCREMENTAL", "FULL"])
    a = ap.parse_args()
    {"upload": lambda: cmd_upload(),
     "import": lambda: cmd_import(a.reconcile),
     "status": lambda: cmd_status(a.arg),
     "count": lambda: cmd_count(),
     "size": lambda: cmd_size()}[a.cmd]()


if __name__ == "__main__":
    main()
