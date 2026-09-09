#!/usr/bin/env python3
"""Independent exact arithmetic for local detector exclusions; stdlib only.

No repository producer imports, no tope census, no claim about global Hc1.
"""
import ast
from fractions import Fraction
from hashlib import sha256
from itertools import combinations
import json
from math import gcd
from pathlib import Path
import struct
import zipfile

ROOT = Path(__file__).resolve().parents[3]
OWN = Path(__file__).resolve().parent
PINS = {
    'ai/omreal/data/seeat_parent2599_upper178.npz': '3b90799d26b7783e92c2ac697eaaf8b76d26a787f53205873b997657e114180a',
    'ops/team/ai-d3-shared-pencil-falsifier/admissibility_flow.json': 'acf71128ca666697bec36436b35ed8bff991a50b8da26b2413cd610631d7ef10',
    'ai/omreal/DIAG3_PAIR_DIFFERENTIAL_ENDS.md': '5c47ce64a77784673c8deecc0279fd279154582b625d2d6a86d6da9d35bdde15',
    'ai/omreal/DIAG3_SINGLE_BAD_TWO_SKELETON.md': '141da1b6d9fcd4f601e79871aaa5d06cb98721ece928a0d0d5af83518bddf71f',
    'ops/team/d3-real-pair-prover/FINDINGS.md': '6425d367675fc709cc65f4560e654b645cb4f92f07571bb81f74ca0e9ab99778',
    'ai/omreal/verify_diag3_row2599_common_proper_escape.py': '6b426e94181a0d447f79d70e3eb6f64f2f34227d88b9ae1fa0a87f9539c4297c',
    'ai/omreal/verify_diag3_row2599_p01_tangent_collar.py': '1625d6db2172b5349edbc741704b6de10afbc1c3213b9733e1810640807bf479',
}
PARENT = [
    [-94,-25,256,256,42,-3,-78,-101],
    [-163,54,35,-164,-96,256,256,-21],
    [256,256,-27,-25,197,160,-83,54],
    [71,122,19,-204,-256,-61,-93,-256],
]
SIGS = [14988895318912,3405195891438080,40418075143643136]
SUPPORTS = [(0,19,21,37,38),(0,9,27,30,35),(0,11,17,24,40)]
TRIPLES = sorted(combinations(range(1,9),3),key=lambda x:x[::-1])
BASES = sorted(combinations(range(1,9),4),key=lambda x:x[::-1])

def require(ok, message):
    if not ok:
        raise AssertionError(message)

def det(a):
    if not a:
        return 1
    return sum((-1)**j*x*det([r[:j]+r[j+1:] for r in a[1:]])
               for j,x in enumerate(a[0]))

def rank(a):
    a = [list(map(Fraction,r)) for r in a]
    r = 0
    for c in range(len(a[0])):
        p = next((i for i in range(r,len(a)) if a[i][c]), None)
        if p is None:
            continue
        a[r],a[p] = a[p],a[r]
        q = a[r][c]
        a[r] = [x/q for x in a[r]]
        for i in range(len(a)):
            if i != r:
                q = a[i][c]
                a[i] = [x-q*y for x,y in zip(a[i],a[r])]
        r += 1
        if r == len(a):
            break
    return r

def brackets(p):
    return [det([[p[r][i-1] for i in b] for r in range(4)]) for b in BASES]

def normals(p, primitive=False):
    rows = [[(-1)**(j+5)*det([[p[r][i-1] for r in range(4) if r != j]
                             for i in t]) for j in range(4)] for t in TRIPLES]
    if primitive:
        rows = [[x//gcd(*row) for x in row] for row in rows]
    return rows

def signed(rows,sig):
    return [[(1 if sig>>i&1 else -1)*x for x in row] for i,row in enumerate(rows)]

def witness(rows,sig,support,weights):
    require(len(support)==len(weights) and len(set(support))==len(support), 'witness support')
    require(all(w>0 for w in weights), 'positive witness')
    a = signed(rows,sig)
    require(all(sum(w*a[i][j] for i,w in zip(support,weights))==0 for j in range(4)), 'kernel witness')

def circuit(rows,sig,support):
    a = [signed(rows,sig)[i] for i in support]
    c = [(-1)**j*det([a[k] for k in range(5) if k!=j]) for j in range(5)]
    require(all(x>0 for x in c) or all(x<0 for x in c), 'strict rank-four circuit')
    c = [abs(x) for x in c]
    witness(rows,sig,support,c)
    return c

def load_npy_member(archive,name):
    b = archive.read(name+'.npy')
    require(b[:6] == b'\x93NUMPY' and b[6] in (1,2), 'NPY header')
    off = 10 if b[6]==1 else 12
    size = struct.unpack('<H' if b[6]==1 else '<I',b[8:off])[0]
    h = ast.literal_eval(b[off:off+size].decode())
    require(h['descr'] in ('<i8','<u2') and not h['fortran_order'], 'NPY supported integer C order')
    raw = b[off+size:]
    code,width = ('q',8) if h['descr']=='<i8' else ('H',2)
    return h['shape'],struct.unpack('<'+code*(len(raw)//width),raw)

def gp_checks(p,sig):
    ps = dict(zip(BASES,(1 if v>0 else -1 for v in brackets(p))))
    ti = {t:i for i,t in enumerate(TRIPLES)}
    def chi(seq):
        inversions = sum(x>y for i,x in enumerate(seq) for y in seq[i+1:])
        b = tuple(sorted(seq))
        v = (1 if sig>>ti[b[:3]]&1 else -1) if 9 in b else ps[b]
        return (-1)**inversions*v
    count = 0
    for lam in combinations(range(1,10),2):
        for a,b,c,d in combinations([i for i in range(1,10) if i not in lam],4):
            terms = [chi(lam+(a,b))*chi(lam+(c,d)),
                     -chi(lam+(a,c))*chi(lam+(b,d)),
                     chi(lam+(a,d))*chi(lam+(b,c))]
            require(len(set(terms))==2, 'GP extension signs')
            count += 1
    return count

def main():
    for name,digest in PINS.items():
        require(sha256((ROOT/name).read_bytes()).hexdigest()==digest, 'source hash: '+name)
    with zipfile.ZipFile(ROOT/'ai/omreal/data/seeat_parent2599_upper178.npz') as archive:
        shape,data = load_npy_member(archive,'chart_matrix')
        require(shape==(178,4,8), 'parent array shape')
        def at(i):
            return [list(data[32*i+8*r:32*i+8*r+8]) for r in range(4)]
        require(at(0)==PARENT, 'actual chart zero')
        ashape,assignment = load_npy_member(archive,'assignment')
        pshape,points = load_npy_member(archive,'point')
    values = brackets(PARENT)
    require(len(values)==70 and all(values), 'uniform parent')
    signs = [1 if v>0 else -1 for v in values]
    rows = normals(PARENT)
    records = []
    for b,(sig,sp) in enumerate(zip(SIGS,SUPPORTS)):
        other = (2,)+sp[1:]
        left,right = circuit(rows,sig,sp),circuit(rows,sig,other)
        union = sorted(set(sp)|set(other))
        a = signed(rows,sig)
        augmented = [[a[i][j] for i in union] for j in range(4)]+[[1]*6]
        require(len(union)==6 and rank(augmented)==5, 'actual coordinate edge dimension one')
        records.append({'block':b,'signature':sig,'supports':[list(sp),list(other)],
            'support_labels':[[''.join(map(str,TRIPLES[i])) for i in s] for s in [sp,other]],
            'positive_raw_cofactors':[left,right], 'union':union,'augmented_rank':5,'face_dimension':1})
    anchors = json.loads((ROOT/'ops/team/ai-d3-shared-pencil-falsifier/admissibility_flow.json').read_text())['records']
    require([r['upper_chart_index'] for r in anchors]==[3,14,2], 'admissibility charts')
    require([r['signature'] for r in anchors]==SIGS, 'admissibility signatures')
    for b,rec in enumerate(anchors):
        idx,chart = rec['upper_point_index'],rec['upper_chart_index']
        p = rec['parent']
        require(p==at(chart) and assignment[idx]==chart, 'stored anchor parent')
        require(list(points[4*idx:4*idx+4])==rec['point'], 'stored anchor point')
        require([1 if v>0 else -1 if v<0 else 0 for v in brackets(p)]==signs, 'same labeled parent')
        pr = normals(p,primitive=True)
        require(all(sum(x*y for x,y in zip(row,rec['point']))>0 for row in signed(pr,SIGS[b])), 'strict feasible anchor')
        for other,system in enumerate(rec['other_systems']):
            require(system['signature']==SIGS[other], 'other signature')
            if other!=b:
                dual = system['dual']
                witness(pr,SIGS[other],dual['support'],dual['weights'])
    gp = sum(gp_checks(PARENT,s) for s in SIGS)
    require(gp==3780, 'GP denominator')
    hostile = {}
    try:
        circuit(rows,SIGS[0]^(1<<SUPPORTS[0][0]),SUPPORTS[0])
    except AssertionError:
        hostile['flip_supported_signature_bit_rejected'] = True
    bad_weights = list(records[0]['positive_raw_cofactors'][0]); bad_weights[0]+=1
    try:
        witness(rows,SIGS[0],SUPPORTS[0],bad_weights)
    except AssertionError:
        hostile['alter_kernel_weight_rejected'] = True
    require(len(hostile)==2, 'hostile arithmetic controls')
    result = {'status':'PASS_AUXILIARY_LOCAL_EXCLUSIONS','original_pair_target':'NULL',
      'theorem_credit':0,'base_revision':'730fd6c7b6c2c3e8cbbf94ab4da3bc97ba53f095',
      'parent':PARENT,'parent_brackets':values,'gp_checks':gp,'signatures':SIGS,
      'coordinate_edges':records,'admissibility_chart_indices':[3,14,2],
      'ordered_noninclusions_certified':6,'source_sha256':PINS,'hostile_controls':hostile,
      'excluded_classes':['sheaf-level left inverse of direct-sum pair restriction',
          'fiberwise contractions to one witness strictly natural for every coordinate-face inclusion'],
      'not_excluded':['degree-one compact-support left inverse','homotopy-coherent proper comparison',
          'acyclic-carrier construction','global boundary detection']}
    (OWN/'ARITHMETIC_REPLAY.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({'status':result['status'],'actual_edges':3,'strict_circuits':6,
                      'admissibility_charts':[3,14,2],'gp_checks':gp,'theorem_credit':0}))

if __name__=='__main__':
    main()
