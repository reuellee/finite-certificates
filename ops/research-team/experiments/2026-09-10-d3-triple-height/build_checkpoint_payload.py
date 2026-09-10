#!/usr/bin/env python3
"""Prepare the additive Git-data payload; publication uses the connector."""
from pathlib import Path
import hashlib
import json
import sys

ROOT = Path(__file__).resolve().parent
PREFIX = 'ops/research-team/experiments/2026-09-10-d3-triple-height/'

def main():
    output = Path(sys.argv[1])
    known = json.loads((ROOT/'KNOWN_INPUT_BLOBS.json').read_text())
    expected = {}; elements = []
    for p in sorted(ROOT.rglob('*')):
        if not p.is_file() or '__pycache__' in p.parts or p.suffix in ('.pyc','.pkl'):
            continue
        name = p.relative_to(ROOT).as_posix()
        b = p.read_bytes()
        sha = hashlib.sha1(b'blob '+str(len(b)).encode()+b'\0'+b).hexdigest()
        if name in known:
            assert sha == known[name], name
            entry = {'path':PREFIX+name,'mode':'100644','type':'blob','sha':sha}
        else:
            entry = {'path':PREFIX+name,'mode':'100644','type':'blob','content':b.decode('utf8')}
        expected[PREFIX+name] = sha
        elements.append(entry)
    data = {'repository':'reuellee/finite-certificates',
            'parent':'a7a98a927e57c8872aca2b1e48d4615ede649171',
            'base_tree':'4f87a672cf5a992996a594e6617defea7cfa3889',
            'branch':'research/d3-triple-height-20260910',
            'prefix':PREFIX,'tree_elements':elements,'expected':expected}
    output.write_text(json.dumps(data,ensure_ascii=True,separators=(',',':')))
    print(json.dumps({'path':str(output),'bytes':output.stat().st_size,
                      'files':len(elements),'reused':len(known)}))

if __name__=='__main__':
    main()
