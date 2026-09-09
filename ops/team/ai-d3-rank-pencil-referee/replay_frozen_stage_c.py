#!/usr/bin/env python3
"""Replay already accepted Stage C checkers from immutable Git blobs.
This is an inherited-binding supplement, not Stage D acceptance logic.
Use a Python environment containing NumPy for the NPZ replay.
"""
from hashlib import sha256
from pathlib import Path
import json
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
ORIGINAL = '964c427f6b71b6223add7dc7fd3a695d4c7db270'
CURRENT = 'fdd143c8be96636b7b11af0ac7e2ea8d60b65eca'
PREFIX = 'ops/team/ai-d3-shared-pencil-final-referee/'
CHECKERS = {
 'independent_check.py': '82163982583d7468a267eeb78bad9fb998a53e82b0ca5ad657b4cf00daa2b2bf',
 'check_robustness.py': '4b90244310e6aea37e68c3f3f71948241af6154ee8ce064cb1830d072ef8d95f',
}


def blob(key):
    return subprocess.check_output(['git', 'show', key], cwd=ROOT)


def need(value, why):
    if not value:
        raise AssertionError(why)


def main():
    started = time.perf_counter()
    normalization = json.loads(blob(CURRENT+':'+PREFIX+'NORMALIZATION.json'))
    need(normalization['frozen_original_commit'] == ORIGINAL, 'normalization original commit')
    normalized = []
    for name, pin in normalization['files'].items():
        before, after = blob(ORIGINAL+':'+PREFIX+name), blob(CURRENT+':'+PREFIX+name)
        need(sha256(before).hexdigest() == pin['before_sha256'], 'before normalization hash '+name)
        need(sha256(after).hexdigest() == pin['after_sha256'], 'after normalization hash '+name)
        need(before.replace(b'\r\n', b'\n') == after, 'beyond line-ending normalization '+name)
        normalized.append(name)
    outputs, sources = {}, []
    for name, expected in CHECKERS.items():
        key = ORIGINAL+':'+PREFIX+name
        data = blob(key)
        need(sha256(data).hexdigest() == expected, 'original independent checker hash')
        sources.append({'git_source': key, 'sha256': expected, 'bytes': len(data)})
        # Preserve its root calculation without creating or editing an old file.
        program = 'import subprocess\nfrom pathlib import Path\n'
        program += 'source=subprocess.check_output('+repr(['git','show',key])+',cwd='+repr(str(ROOT))+')\n'
        program += 'exec(compile(source,'+repr(key)+',"exec"),{"__name__":"__main__","__file__":'+repr(str(OUT/name))+'})\n'
        process = subprocess.run([sys.executable, '-B', '-c', program], cwd=ROOT, capture_output=True, text=True)
        need(process.returncode == 0, name+' replay failed: '+process.stderr)
        need(not process.stderr, name+' unexpected stderr')
        result = json.loads(process.stdout)
        frozen_name = 'CHECK_OUTPUT.json' if name == 'independent_check.py' else 'ROBUSTNESS_OUTPUT.json'
        frozen = json.loads(blob(ORIGINAL+':'+PREFIX+frozen_name))
        result_without_time = {k: v for k, v in result.items() if k != 'elapsed_seconds'}
        frozen_without_time = {k: v for k, v in frozen.items() if k != 'elapsed_seconds'}
        need(result_without_time == frozen_without_time, name+' non-time output drift')
        outputs[name] = result
    original_review = blob(ORIGINAL+':'+PREFIX+'REVIEW.md')
    need(sha256(original_review).hexdigest() == '8bf6d4d12a0e6067263688a75c93ac1ffe2d3543d809852e2e259898efafaef1', 'Stage C reviewed proof pin')
    print(json.dumps({'status': 'PASS_FROZEN_STAGE_C_BINDINGS_AND_NORMALIZATION',
        'original_referee_commit': ORIGINAL, 'current_principal_commit': CURRENT,
        'normalization_exact_crlf_to_lf_files': normalized,
        'producer_code_imported_or_executed': False,
        'prior_independent_referee_checkers_executed': sources,
        'non_time_outputs_exactly_match_original_acceptance': True,
        'outputs': outputs, 'elapsed_seconds': round(time.perf_counter()-started, 6)}, indent=2))


if __name__ == '__main__':
    main()
