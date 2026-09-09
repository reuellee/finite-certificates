#!/usr/bin/env python3
"""Freeze reproducible replay outputs with LF; no producer code is run."""
from datetime import datetime, timezone
from pathlib import Path
import json
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
jobs = [('independent_check.py', 'CHECK_OUTPUT.json'), ('replay_frozen_stage_c.py', 'STAGE_C_REPLAY_OUTPUT.json')]
resources = []
for name, output in jobs:
    started = time.perf_counter()
    process = subprocess.run([sys.executable, '-B', str(OUT/name)], cwd=ROOT, capture_output=True, text=True)
    (OUT/(name+'.stderr.txt')).write_text(process.stderr, encoding='utf-8', newline='\n')
    if process.returncode:
        raise RuntimeError(name+' failed: '+process.stderr)
    result = json.loads(process.stdout)
    (OUT/output).write_text(json.dumps(result, indent=2)+'\n', encoding='utf-8', newline='\n')
    resources.append({'script': name, 'exit_code': process.returncode, 'seconds': round(time.perf_counter()-started, 6), 'process_memory_if_reported': result.get('process_memory')})
report = {'recorded_utc': datetime.now(timezone.utc).isoformat(), 'python_executable_used': sys.executable,
          'python_version': sys.version, 'replays': resources,
          'whole_role_peak_memory_instrumented': False,
          'memory_scope': 'independent rank-checker peak is measured; inherited checker peak was measured in the frozen Stage C acceptance, not remeasured here'}
(OUT/'RUN_RESOURCES.json').write_text(json.dumps(report, indent=2)+'\n', encoding='utf-8', newline='\n')
print(json.dumps(report, indent=2))
