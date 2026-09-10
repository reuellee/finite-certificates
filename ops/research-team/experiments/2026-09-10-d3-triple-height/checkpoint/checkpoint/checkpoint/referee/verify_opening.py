"""Independent source identity and spectral-sequence degree audit.

This checks finite bookkeeping. It does not purport to prove the inherited
topological theorems, nor to compute any original parent cohomology group.
No producer certificate/verifier code is imported.
"""
from pathlib import Path
import hashlib
import json

ROOT = Path(__file__).resolve().parents[1]


def edge(p, q, r):
    return (p + r, q - r + 1)


def incoming(target, r):
    p, q = target
    return p-r, q+r-1


def valid(x):
    return 0 <= x[0] <= 2 and x[1] >= 0


def main():
    manifest = json.loads((ROOT / 'SOURCE_MANIFEST.json').read_text())
    checks = []
    for item in manifest['files']:
        data = (ROOT / item['path']).read_bytes()
        sha = hashlib.sha256(data).hexdigest()
        blob = hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()
        assert len(data) == item['bytes']
        assert sha == item['sha256']
        assert blob == item['git_blob']
        checks.append({'path':item['path'], 'sha256':sha, 'git_blob':blob})

    # Known zero E1 terms relevant to total degrees 1 and 2.
    zero = {(0,0),(0,1),(0,2),(1,0)}
    degree_two = [(0,2),(1,1),(2,0)]
    assert [x for x in degree_two if x not in zero] == [(1,1),(2,0)]
    triple_incoming = {r:incoming((2,0),r) for r in range(1,5)
                       if valid(incoming((2,0),r))}
    assert triple_incoming == {1:(1,0),2:(0,1)}
    assert set(triple_incoming.values()) <= zero
    assert not any(valid(edge(2,0,r)) for r in range(1,5))

    pair_incoming = {r:incoming((1,1),r) for r in range(1,5)
                     if valid(incoming((1,1),r))}
    pair_outgoing = {r:edge(1,1,r) for r in range(1,5)
                     if valid(edge(1,1,r))}
    assert pair_incoming == {1:(0,1)}
    assert pair_outgoing == {1:(2,1)}
    result = {
        'status':'PASS',
        'scope':'source identities and finite bidegree bookkeeping only',
        'source_checks':checks,
        'original_target':'H_6(F_S; Q)=0 for every original three-antichain',
        'surviving_associated_graded':[
            {'bidegree':[1,1], 'group':'kernel of signed pair-to-triple H_c^1 restriction'},
            {'bidegree':[2,0], 'group':'triple H_c^0'}],
        'triple_incoming':{str(k):v for k,v in triple_incoming.items()},
        'pair_incoming':{str(k):v for k,v in pair_incoming.items()},
        'pair_outgoing':{str(k):v for k,v in pair_outgoing.items()},
        'ledger_effect':0,
        'original_obligations_closed':0,
    }
    print(json.dumps(result,indent=2))


if __name__ == '__main__':
    main()
