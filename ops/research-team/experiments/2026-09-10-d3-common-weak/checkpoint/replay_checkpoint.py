#!/usr/bin/env python3
"""Authenticate this research snapshot and run independent exact checks cleanly.

This replays arithmetic and orbit certificates. Written topological proofs
require the accompanying independent deductive reviews; no D3 proof is claimed.
"""
from pathlib import Path
import hashlib, json, os, shutil, subprocess, sys, tempfile, time

ROOT=Path(__file__).resolve().parent
CHECKS=[
 'referee/verify_opening.py',
 'referee/verify_pair_templates_independent.py',
 'falsifier/verify_ruled_quadric_cases.py',
 'referee/verify_hard_orbits_independent.py',
 'referee/verify_hard_pair_independent.py',
 'referee/verify_column_gates_independent.py',
 'referee/verify_tangent_independent.py',
 'falsifier/verify_triple_independent.py',
 'falsifier/verify_triple_reduction_independent.py',
]

def main():
    manifest=json.loads((ROOT/'CHECKPOINT_MANIFEST.json').read_text())
    for item in manifest['files']:
        data=(ROOT/item['path']).read_bytes()
        assert len(data)==item['bytes'],item['path']
        assert hashlib.sha256(data).hexdigest()==item['sha256'],item['path']
    results=[]
    with tempfile.TemporaryDirectory(prefix='d3-wall-replay-') as work:
        clone=Path(work)/'checkpoint'
        for item in manifest['files']:
            p=clone/item['path'];p.parent.mkdir(parents=True,exist_ok=True)
            shutil.copyfile(ROOT/item['path'],p)
        for check in CHECKS:
            print('Checking '+check,flush=True)
            start=time.monotonic()
            run=subprocess.run([sys.executable,'-B',str(clone/check)],cwd=clone,
              capture_output=True,text=True,timeout=180,
              env={**os.environ,'PYTHONDONTWRITEBYTECODE':'1'})
            result={'check':check,'exit_code':run.returncode,
                    'seconds':round(time.monotonic()-start,3),
                    'stdout_sha256':hashlib.sha256(run.stdout.encode()).hexdigest(),
                    'stderr_sha256':hashlib.sha256(run.stderr.encode()).hexdigest()}
            if run.returncode:
                result['stdout_tail']=run.stdout[-4000:]
                result['stderr_tail']=run.stderr[-4000:]
            results.append(result)
            if run.returncode:
                raise RuntimeError(json.dumps(result,indent=2))
    report={'status':'PASS','authenticated_files':len(manifest['files']),
      'clean_independent_checks':results,'original_ledger':'2/9',
      'strong_pair_endpoint':{'total':9476,'proved':8902,'remaining':574},
      'original_D':'OPEN','original_triple_Hc0':'OPEN',
      'scope':'exact certificate replay plus separately recorded deductive audits; no proof-assistant verification'}
    (ROOT/'CLEAN_REPLAY.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report,indent=2))

if __name__=='__main__':main()
