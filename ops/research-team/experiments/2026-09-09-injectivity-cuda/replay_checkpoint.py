#!/usr/bin/env python3
"""Authenticate evidence and replay exact checks in the dedicated CI workflow."""
from pathlib import Path, PurePosixPath
from hashlib import sha256
import json
import subprocess
import sys
import tempfile
import zipfile

HERE = Path(__file__).resolve().parent


def require(condition, message):
    if not condition:
        raise ValueError(message)


def main():
    manifest = json.loads((HERE / 'EVIDENCE_MANIFEST.json').read_text())
    archive = HERE / 'EVIDENCE.zip'
    require(sha256(archive.read_bytes()).hexdigest() == manifest['archive_sha256'],
            'Evidence archive digest mismatch')
    with tempfile.TemporaryDirectory(prefix='9dvl_exact_replay_') as tmp:
        root = Path(tmp)
        with zipfile.ZipFile(archive) as z:
            names = z.namelist()
            require(len(names) == len(set(names)), 'Duplicate archive member')
            require(set(names) == set(manifest['files']), 'Archive member accounting mismatch')
            for name, expected in manifest['files'].items():
                rel = PurePosixPath(name)
                require(not rel.is_absolute() and '..' not in rel.parts and '\\' not in name,
                        'Unsafe archive path')
                data = z.read(name)
                require(len(data) == expected['bytes'] and sha256(data).hexdigest() == expected['sha256'],
                        'Evidence member digest mismatch: ' + name)
                target = root.joinpath(*rel.parts)
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes(data)
            for visible, member in manifest['review_copies'].items():
                require((HERE / visible).read_bytes() == z.read(member),
                        'Readable review copy differs from frozen evidence: ' + visible)
        commands = [
            ['injectivity/referee/verify_frozen_candidates.py'],
            ['collision_diagnostic/referee/verify_independently.py'],
            ['parent_pilot/referee/verify.py', '--structural',
             'parent_pilot/structural/SEARCH_RESULT.json', '--engineer',
             'parent_pilot/engineer/run/exact_candidates.json'],
        ]
        expected = ['PASS_AUXILIARY_AND_ABSTRACT_ONLY',
                    'PASS_INDEPENDENT_ABSTRACT_ONLY',
                    'ACCEPT_FINITE_LOCAL_CERTIFICATES_ONLY']
        replays = []
        for args, verdict in zip(commands, expected):
            completed = subprocess.run([sys.executable, '-B', *args], cwd=root,
                                       capture_output=True, text=True, check=True, timeout=120)
            output = json.loads(completed.stdout)
            require(output.get('verdict', output.get('status')) == verdict, 'Unexpected replay verdict')
            replays.append({'script': args[0], 'verdict': verdict})
        last = output
        require(last['ledger'] == '2/9' and last['original_obligations_closed'] == 0,
                'Original theorem scope changed')
        result = {'status': 'PASS_CHECKPOINT', 'authenticated_files': len(manifest['files']),
                  'replays': replays, 'exact_selected_parents': last['engineer']['selected_parents'],
                  'exact_block_counts': last['engineer']['block_status_counts'],
                  'three_row_certificates': last['structural']['exact_positive_three_row_circuits'],
                  'ledger': '2/9', 'gpu_execution': 'UNTESTED'}
        print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
