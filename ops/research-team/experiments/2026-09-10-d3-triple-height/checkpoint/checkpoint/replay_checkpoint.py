"""Authenticate the checkpoint and replay independently written arithmetic checks.

The conventional vanishing theorem is not machine-proved by this script.
"""
from pathlib import Path
from tempfile import TemporaryDirectory
import hashlib
import json
import os
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parent


def digest(data):
    return hashlib.sha256(data).hexdigest()


def main():
    manifest = json.loads((ROOT / 'CHECKPOINT_MANIFEST.json').read_text())
    files = manifest['files']
    for record in files:
        relative = Path(record['path'])
        assert not relative.is_absolute() and '..' not in relative.parts
        data = (ROOT / relative).read_bytes()
        assert len(data) == record['bytes'], str(relative)
        assert digest(data) == record['sha256'], str(relative)
        blob = b'blob ' + str(len(data)).encode() + b'\0' + data
        assert hashlib.sha1(blob).hexdigest() == record['git_blob_sha1'], str(relative)
    checks = []
    with TemporaryDirectory(prefix='9dvl-direct-review-') as directory:
        clean = Path(directory)
        for record in files:
            target = clean / record['path']
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(ROOT / record['path'], target)
        env = dict(os.environ, PYTHONDONTWRITEBYTECODE='1')
        for script, output in manifest['independent_replays']:
            run = subprocess.run([sys.executable, script], cwd=clean, env=env,
                                 capture_output=True, text=True, timeout=120)
            if run.returncode:
                raise RuntimeError(f'{script} failed:\n{run.stdout}\n{run.stderr}')
            rebuilt = (clean / output).read_bytes()
            recorded = (ROOT / output).read_bytes()
            assert rebuilt == recorded, f'Independent replay output changed: {output}'
            checks.append({'script': script, 'status': 'PASS',
                           'recorded_output_reproduced': True,
                           'output_sha256': digest(rebuilt)})
    result = {'status': 'PASS', 'authenticated_files': len(files),
              'independent_replays': checks, 'original_ledger': '2/9',
              'deductive_proof_machine_verified': False,
              'deductive_review': 'referee/FINAL_REVIEW.md'}
    (ROOT / 'CLEAN_REPLAY.json').write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
