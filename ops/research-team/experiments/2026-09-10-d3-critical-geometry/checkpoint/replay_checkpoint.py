#!/usr/bin/env python3
"""Authenticate the frozen checkpoint and replay the new exact diagnostics.

The conventional global proofs are reviewed by humans/independent agents;
this runner does not purport to mechanically prove those theorems.
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

def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def main():
    manifest = json.loads((ROOT/'CHECKPOINT_MANIFEST.json').read_text())
    for row in manifest['files']:
        p = ROOT / row['path']
        assert p.stat().st_size == row['bytes'], row['path']
        assert digest(p) == row['sha256'], row['path']
    runs = [
        ('referee/verify_anchor_frames.py', ['referee/ANCHOR_FRAME_REPLAY.json'], []),
        ('proof/critical_canary.py', ['proof/CRITICAL_CANARY.json'], []),
        ('referee/verify_critical_canary.py', ['referee/CRITICAL_CANARY_REPLAY.json'], []),
        ('referee/verify_quadratic_inputs.py', ['referee/QUADRATIC_INPUT_REPLAY.json'], []),
        ('falsifier/verify_pencil_coverage.py', [
            'falsifier/HEIGHT_OVAL_PROBE.json',
            'falsifier/QUAD_INERTIA.json',
            'falsifier/PENCIL_SINGULAR_PROBE.json',
            'falsifier/SINGULAR_PENCIL_FAMILY.json',
            'falsifier/EXCEPTIONAL_PENCIL_PROBE.json',
            'falsifier/QUADRATIC_EXTENSION_PROBE.json',
            'falsifier/PENCIL_COVERAGE.json'], ['--replay']),
    ]
    records = []
    with tempfile.TemporaryDirectory(prefix='d3-triple-height-replay-') as tmp:
        work = Path(tmp)/'checkpoint'
        shutil.copytree(ROOT, work, ignore=shutil.ignore_patterns('__pycache__','*.pyc'))
        env = dict(os.environ, PYTHONDONTWRITEBYTECODE='1')
        for script, outputs, extra in runs:
            print('Replaying '+script, flush=True)
            result = subprocess.run([sys.executable, str(work/script), *extra],
                                    cwd=work, env=env, capture_output=True,
                                    text=True, timeout=900)
            if result.returncode:
                raise RuntimeError(script+'\n'+result.stdout+'\n'+result.stderr)
            hashes = {}
            for name in outputs:
                assert (work/name).read_bytes() == (ROOT/name).read_bytes(), name
                hashes[name] = digest(work/name)
            records.append({'script':script, 'arguments':extra, 'status':'PASS',
                            'recorded_outputs_reproduced':hashes})
    summary = {'status':'PASS', 'authenticated_files':len(manifest['files']),
               'runs':records, 'original_diagonal_ledger':'2/9',
               'universal_pair_endpoint':'PROVED inherited 9476/9476',
               'universal_triple_endpoint':'OPEN',
               'new_numerical_triple_credit':0,
               'deductive_proofs_machine_verified':False,
               'independent_deductive_review':'referee/FINAL_REVIEW.md'}
    (ROOT/'CLEAN_REPLAY.json').write_text(json.dumps(summary,indent=2)+'\n')
    print('PASS frozen hashes and all new exact replay outputs', flush=True)

if __name__=='__main__':
    main()
