#!/usr/bin/env python3
"""Authenticate source bytes and run independent exact checks in a clean copy.

Python standard library only. Discovery and producer acceptance routines are
not imported. The written limiting argument and scope audit accompany these
finite polynomial checks; this script does not prove the original 9DVL map.
"""
from pathlib import Path
from tempfile import TemporaryDirectory
import hashlib
import json
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parent
CHECKS = [
    'referee/verify_opening.py',
    'referee/verify_constructive_independent.py',
    'referee/verify_falsifier_independent.py',
]

def authenticate():
    manifest = json.loads((ROOT / 'SOURCE_MANIFEST.json').read_text())
    for row in manifest['files']:
        data = (ROOT / row['path']).read_bytes()
        assert len(data) == row['bytes'], row['path']
        assert hashlib.sha256(data).hexdigest() == row['sha256'], row['path']
        blob = hashlib.sha1(b'blob ' + str(len(data)).encode() + b'\0' + data).hexdigest()
        assert blob == row['git_blob'] and row['remote_blob_match'], row['path']
    final_manifest = ROOT / 'CHECKPOINT_MANIFEST.json'
    if final_manifest.exists():
        for row in json.loads(final_manifest.read_text())['files']:
            data = (ROOT / row['path']).read_bytes()
            assert len(data) == row['bytes'], row['path']
            assert hashlib.sha256(data).hexdigest() == row['sha256'], row['path']
    return len(manifest['files'])

def main():
    sources = authenticate()
    summaries = {}
    with TemporaryDirectory(prefix='9dvl-guess-check-') as tmp:
        clean = Path(tmp) / 'checkpoint'
        shutil.copytree(ROOT, clean, ignore=shutil.ignore_patterns('__pycache__', '*.pyc', '*.zip', 'REPORT_DRAFT.md'))
        for relative in CHECKS:
            result = subprocess.run([sys.executable, '-B', str(clean / relative)], cwd=clean, text=True, capture_output=True, timeout=120)
            if result.returncode:
                sys.stderr.write(result.stdout + result.stderr)
                raise SystemExit(f'Independent replay failed: {relative}')
            summaries[relative] = json.loads(result.stdout)
    print(json.dumps({'status': 'PASS_INDEPENDENT_EXACT_REPLAY', 'source_files_authenticated': sources,
        'original_injectivity': 'OPEN', 'original_ledger': '2/9', 'checks': summaries}, indent=2))

if __name__ == '__main__':
    main()
