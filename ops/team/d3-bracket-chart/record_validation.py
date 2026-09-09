"""Capture the final local checks and a manifest, without changing the ledger."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib
import json
import subprocess
import sys
import time
from zipfile import ZipFile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    state = ROOT/'ai/omreal/data/CANONICAL_RESEARCH_STATE_V11.json'
    before = digest(state)
    assert before == '5929b922ecf04246920d56a1adedc29382379eb5abae8b600601995d6b5dae86'
    validation = {'timestamp_utc':datetime.now(timezone.utc).isoformat(),
                  'python':sys.version,'commands':[]}
    for relative in ['ops/team/d3-bracket-chart/verify_genus_one_fiber.py',
                     'ai/omreal/verify_canonical_research_state_v11.py',
                     'ops/research-team/verify_cycle_protocol.py']:
        args = [sys.executable,'-B',relative]
        start = time.monotonic()
        proc = subprocess.run(args,cwd=ROOT,capture_output=True,text=True,timeout=120)
        record = {'command':args,'script_sha256':digest(ROOT/relative),
                  'seconds':time.monotonic()-start,'exit_code':proc.returncode,
                  'stdout':proc.stdout,'stderr':proc.stderr}
        validation['commands'].append(record)
        assert proc.returncode == 0,record
        if 'genus_one' in relative:
            replay = json.loads(proc.stdout)
            (HERE/'ARITHMETIC_REPLAY.json').write_text(json.dumps(replay,indent=2)+'\n',newline='\n')
    assert digest(state) == before
    validation['canonical_sha256_unchanged'] = before
    (HERE/'VALIDATION.json').write_text(json.dumps(validation,indent=2)+'\n',newline='\n')
    with ZipFile(HERE/'DISCOVERY_OUTPUTS.zip') as z:
        assert z.testzip() is None
        entries = [{'path':name,'bytes':len(z.read(name)),
                    'sha256':hashlib.sha256(z.read(name)).hexdigest()} for name in z.namelist()]
    ignored = {entry['path'] for entry in entries} | {'CLOSING_MANIFEST.json'}
    paths = sorted(p for p in HERE.iterdir() if p.is_file() and p.name not in ignored)
    paths.append(ROOT/'ops/research-team/NEXT_CYCLE.md')
    manifest = {
        'base_revision':'68c3dbaf748416be099ad71af2b7426dbadf9272',
        'base_tree':'d9116a510b2b4c29116ad7c956996e0136264067',
        'source_sha256':'c9244a47ded5736e7afe724a9914e75631a22b78653442e88c14f5c397919eb8',
        'canonical_sha256_unchanged':before,'ledger_opening':'2/9','ledger_closing':'2/9',
        'target_3_of_9_achieved':False,'triple_source_residual':1162302,
        'open_load_bearing_obligations':7,'global_pair_coverage':'UNKNOWN',
        'theorem_trajectory':'STALLED','knowledge_classification':'INFORMATIONAL',
        'decision':'RETIRE_FIXED_BASE_RATIONAL_RULING; STOP_THIS_INVESTIGATION',
        'new_results':['Generic genus-one fiber for projection to (b,f,g,h,i)',
                       'All components of one complete fixed-base fiber are noncompact in every uniform parent cell'],
        'independent_ai_referee':'NOT_PERFORMED',
        'scope':'Coordinator research with separate standard-library arithmetic replay; no full-source or D3 closure',
        'discovery_archive_entries':entries,
        'resource_notes':{'discovery_wall_ceiling_minutes':90,
                          'symbolic_process_ceiling_seconds':300,
                          'flint_process_memory_limit_kib':8388608,
                          'windows_peak_memory_instrumented':False,
                          'active_model_time_instrumented':False,
                          'new_artifact_bytes_before_manifest':sum(p.stat().st_size for p in paths),
                          'larger_critical_solver_runs':0,'orbit_censuses':0},
        'files':[{'path':str(p.relative_to(ROOT)).replace('\\','/'),
                  'bytes':p.stat().st_size,'sha256':digest(p)} for p in paths]}
    (HERE/'CLOSING_MANIFEST.json').write_text(json.dumps(manifest,indent=2)+'\n',newline='\n')
    print('PASS final exact replay, canonical V11, and existing protocol; ledger unchanged at 2/9')


if __name__ == '__main__':
    main()
