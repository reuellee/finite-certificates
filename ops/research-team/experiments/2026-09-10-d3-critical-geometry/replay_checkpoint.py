#!/usr/bin/env python3
"""Authenticate the checkpoint and independently rebuild its exact diagnostics.

Conventional global proofs are independently reviewed deductively. This runner
does not claim to mechanically prove them or the original third diagonal.
"""
from pathlib import Path
import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parent

RUNS = [
    ('referee/verify_noncollinear_independent.py', ['referee/NONCOLLINEAR_INDEPENDENT_REPLAY.json']),
    ('referee/verify_new_critical_canaries.py', ['referee/NEW_CRITICAL_CANARIES_REPLAY.json']),
    ('proof/verify_collinear_rank11.py', ['proof/COLLINEAR_RANK11_REPLAY.json']),
    ('referee/verify_witness_slides.py', ['referee/WITNESS_SLIDES_REPLAY.json']),
    ('referee/verify_global_graph_independent.py', ['referee/GLOBAL_GRAPH_REPLAY.json']),
    ('referee/verify_critical_chart.py', ['referee/CRITICAL_CHART_REPLAY.json']),
    ('falsifier/verify_gradient_pencil.py', ['falsifier/GRADIENT_PENCIL_REPLAY.json']),
    ('falsifier/verify_deformation_boundary.py', ['falsifier/DEFORMATION_BOUNDARY_CANARIES.json']),
    ('referee/verify_survivor_supports.py', ['referee/SURVIVOR_SUPPORTS_REPLAY.json']),
    ('referee/verify_survivor_elimination.py', ['referee/SURVIVOR_ELIMINATION_REPLAY.json']),
]

def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def main():
    manifest = json.loads((ROOT/'CHECKPOINT_MANIFEST.json').read_text())
    for row in manifest['files']:
        p = ROOT/row['path']
        assert p.stat().st_size == row['bytes'], row['path']
        assert digest(p) == row['sha256'], row['path']
    review = json.loads((ROOT/'referee/FINAL_REVIEW.json').read_text())
    assert review['verdict'] == 'ACCEPT_CHECKPOINT_NO_ORIGINAL_PROMOTION'
    for name, sha in review['files_sha256'].items():
        assert digest(ROOT/name) == sha, name
    records = []
    with tempfile.TemporaryDirectory(prefix='d3-critical-geometry-replay-') as tmp:
        work = Path(tmp)/'checkpoint'
        shutil.copytree(ROOT, work, ignore=shutil.ignore_patterns('__pycache__', '*.pyc', '*.pkl'))
        env = dict(os.environ, PYTHONDONTWRITEBYTECODE='1')
        for script, outputs in RUNS:
            print('Replaying '+script, flush=True)
            result = subprocess.run([sys.executable, str(work/script)], cwd=work,
                                    env=env, capture_output=True, text=True, timeout=300)
            if result.returncode:
                raise RuntimeError(script+'\n'+result.stdout+'\n'+result.stderr)
            hashes = {}
            for name in outputs:
                assert (work/name).read_bytes() == (ROOT/name).read_bytes(), name
                hashes[name] = digest(work/name)
            records.append({'script':script, 'status':'PASS', 'outputs_reproduced':hashes})
    summary = {'status':'PASS', 'authenticated_files':len(manifest['files']),
               'review_bound_files':len(review['files_sha256']), 'runs':records,
               'original_diagonal_ledger':'2/9', 'universal_pair_endpoint':'PROVED inherited9476/9476',
               'universal_triple_endpoint':'OPEN', 'new_numerical_triple_credit':0,
               'deductive_proofs_machine_verified':False,
               'independent_deductive_review':'referee/FINAL_REVIEW.json'}
    (ROOT/'CLEAN_REPLAY.json').write_text(json.dumps(summary,indent=2)+'\n')
    print('PASS frozen identities and new exact replays', flush=True)

if __name__ == '__main__':
    main()
