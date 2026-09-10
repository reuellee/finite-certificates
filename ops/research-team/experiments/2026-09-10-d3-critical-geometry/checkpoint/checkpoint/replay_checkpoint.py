"""Authenticate this snapshot and replay its independently constructed exact checks.

The conventional universal pair theorem is independently reviewed mathematics;
this script does not claim to prove it by computation.
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


def sha256(data):
    return hashlib.sha256(data).hexdigest()


def main():
    manifest = json.loads((ROOT / 'CHECKPOINT_MANIFEST.json').read_text())
    records = manifest['files']
    paths = set()
    for row in records:
        relative = Path(row['path'])
        assert not relative.is_absolute() and '..' not in relative.parts
        assert row['path'] not in paths
        paths.add(row['path'])
        data = (ROOT / relative).read_bytes()
        assert len(data) == row['bytes'], row['path']
        assert sha256(data) == row['sha256'], row['path']
        blob = b'blob ' + str(len(data)).encode() + b'\0' + data
        assert hashlib.sha1(blob).hexdigest() == row['git_blob_sha1'], row['path']
    checks = []
    with TemporaryDirectory(prefix='9dvl-universal-pair-') as directory:
        clean = Path(directory)
        for row in records:
            target = clean / row['path']
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(ROOT / row['path'], target)
        env = dict(os.environ, PYTHONDONTWRITEBYTECODE='1')
        for script, output in manifest['independent_replays']:
            run = subprocess.run([sys.executable, script], cwd=clean, env=env,
                                 capture_output=True, text=True, timeout=180)
            if run.returncode:
                raise RuntimeError(f'{script} failed:\n{run.stdout}\n{run.stderr}')
            rebuilt = (clean / output).read_bytes()
            assert rebuilt == (ROOT / output).read_bytes(), output
            checks.append({'script': script, 'status': 'PASS',
                           'recorded_output_reproduced': True,
                           'output_sha256': sha256(rebuilt)})
            print('PASS', script, flush=True)
    ledger = json.loads((ROOT / 'CLAIM_LEDGER.json').read_text())
    assert ledger['original_diagonals_proved'] == 2
    assert ledger['stronger_pair_endpoint']['covered_factor_pair_orbits'] == 9476
    assert ledger['stronger_pair_endpoint']['remaining'] == 0
    assert ledger['stronger_triple_endpoint']['unresolved_source_records'] == 1162302
    result = {'status': 'PASS', 'authenticated_files': len(records),
              'independent_replays': checks,
              'original_diagonal_ledger': '2/9',
              'stronger_pair_endpoint': 'PROVED: 9476/9476',
              'triple_residue_records': 1162302,
              'deductive_proof_machine_verified': False,
              'deductive_review': 'referee/FINAL_REVIEW.md'}
    (ROOT / 'CLEAN_REPLAY.json').write_text(json.dumps(result, indent=2) + '\n')
    print('PASS snapshot:', len(records), 'files;', len(checks), 'exact replays')


if __name__ == '__main__':
    main()
