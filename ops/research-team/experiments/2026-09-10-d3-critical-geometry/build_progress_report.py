#!/usr/bin/env python3
"""Compile the complete new proofs and independent review into one Markdown file."""
from pathlib import Path
import hashlib
import posixpath
import re
import sys

ROOT = Path(__file__).resolve().parent
PREFIX = 'ops/research-team/experiments/2026-09-10-d3-critical-geometry/'
PARTS = [
    'REPORT.md',
    'referee/PARENT_ON_CONCURRENCE_LINE.md',
    'proof/COLLINEAR_RANK_ESCAPE.md',
    'proof/COMMON_STRESS_RANK_IDENTITY.md',
    'proof/ONE_LOW_COLLINEAR_ESCAPE.md',
    'proof/TYPE48_COLLINEAR_ESCAPE.md',
    'proof/RANK_DEFICIENT_BLOCK_ESCAPE.md',
    'proof/FLAT_HEIGHT_BLOCK_EXCISION.md',
    'noncollinear/escape_redundant_height.md',
    'noncollinear/CHARACTERISTIC_KERNELS.md',
    'proof/LINEAR_GRADIENT_PENCIL_GATE.md',
    'noncollinear/NONCOLLINEAR_COUNTEREXAMPLE.md',
    'noncollinear/escape_global_graph.md',
    'noncollinear/escape_critical_classification.md',
    'noncollinear/survivor_FINDINGS.md',
    'SOURCE_ROUTE_AUDIT.md',
    'NEXT_GATE.md',
    'referee/FINAL_REVIEW.md',
]

def main():
    commit, output = sys.argv[1], Path(sys.argv[2])
    assert re.fullmatch('[0-9a-f]{40}', commit)
    base = f'https://github.com/reuellee/finite-certificates/blob/{commit}/'
    pieces = ['# 9DVL critical-geometry progress — 10 September2026\n\n'
              'Original status: **2/9; third diagonal remains open.**\n\n'
              f'Complete checkpoint: [immutable report]({base}{PREFIX}REPORT.md). '
              'The full new proof texts and independent final review follow. '
              'Exact scripts, inputs and review bindings are in the linked checkpoint.\n']
    for name in PARTS:
        p = ROOT/name
        data = p.read_bytes()
        text = data.decode('utf8')
        def link(match):
            label, target = match.groups()
            if ':' in target or target.startswith('#'):
                return match.group(0)
            path, sep, anchor = target.partition('#')
            normalized = posixpath.normpath(posixpath.join(posixpath.dirname(name), path))
            assert (ROOT/normalized).is_file(), (name, target)
            return f'[{label}]({base}{PREFIX}{normalized}{sep}{anchor})'
        text = re.sub(r'\[([^\]\n]+)\]\(([^)\s]+)\)', link, text)
        pieces.append('\n---\n\n'
                      f'Source: [{name}]({base}{PREFIX}{name}); '
                      f'SHA256 `{hashlib.sha256(data).hexdigest()}`.\n\n'+text)
    output.write_text('\n'.join(pieces))
    print(f'Compiled {len(PARTS)} complete source texts into {output} ({output.stat().st_size} bytes)')

if __name__ == '__main__':
    main()
