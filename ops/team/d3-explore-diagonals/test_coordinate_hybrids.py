#!/usr/bin/env python3
"""Exact finite structural test, not a diagonal-nine proof.

Normalize the same first-five oriented rays at both endpoint charts, retaining
positive column scales. Enumerate every endpoint-coordinate hybrid. A valid
edge varies one normalized entry, so every parent determinant is affine.
"""
from fractions import Fraction as Q
from itertools import combinations
from pathlib import Path
from collections import deque
import argparse, hashlib, json, time
import numpy as np

ROOT=Path(__file__).resolve().parents[3]
HERE=Path(__file__).resolve().parent
SOURCE=ROOT/'ai/omreal/data/seeat_parent2599_upper178.npz'
BASES=list(combinations(range(8),4))

def det(a):
    if len(a)==1: return a[0][0]
    return sum((-1)**j*a[0][j]*det([r[:j]+r[j+1:] for r in a[1:]]) for j in range(len(a)))

def normalize(a):
    mat=[[Q(int(x)) for x in row] for row in a]
    basis=[[mat[i][j] for j in range(4)] for i in range(4)]
    work=[basis[i]+[Q(i==j) for j in range(4)] for i in range(4)]
    for j in range(4):
        pivot=next(i for i in range(j,4) if work[i][j])
        work[j],work[pivot]=work[pivot],work[j]
        scale=work[j][j];work[j]=[x/scale for x in work[j]]
        for i in range(4):
            if i!=j:
                scale=work[i][j];work[i]=[x-scale*y for x,y in zip(work[i],work[j])]
    inv=[r[4:] for r in work]
    red=[[sum(inv[i][k]*mat[k][j] for k in range(4)) for j in range(8)] for i in range(4)]
    fifth=[red[i][4] for i in range(4)]
    transform=[[inv[i][j]/fifth[i] for j in range(4)] for i in range(4)]
    b=[[red[i][j]/fifth[i] for j in range(8)] for i in range(4)]
    for j in range(4):
        for i in range(4):b[i][j]*=abs(fifth[j])
    for j in range(5,8):
        scale=abs(b[0][j])
        for i in range(4):b[i][j]/=scale
    return b,str(det(transform))

def signs(mat):
    # Positive denominator clearing makes the arithmetic integer-only.
    from math import lcm
    m=[r[:] for r in mat]
    for j in range(8):
        den=lcm(*[Q(m[i][j]).denominator for i in range(4)])
        for i in range(4): m[i][j]=int(m[i][j]*den)
    ds=[det([[m[i][j] for j in basis] for i in range(4)]) for basis in BASES]
    return tuple((x>0)-(x<0) for x in ds), ds

def reachable(valid,bits,monotone):
    seen={0}; todo=deque([0]); pred={}
    while todo:
        n=todo.popleft()
        for i in range(bits):
            if monotone and n>>i&1: continue
            v=n^(1<<i)
            if v in valid and v not in seen:
                seen.add(v);pred[v]=n;todo.append(v)
    goal=(1<<bits)-1
    path=[]
    if goal in seen:
        x=goal
        while x: path.append(x);x=pred[x]
        path.append(0);path.reverse()
    return sorted(seen),path

def main():
    t0=time.perf_counter();cpu0=time.process_time()
    parser=argparse.ArgumentParser()
    parser.add_argument('--write',action='store_true')
    args=parser.parse_args()
    assert hashlib.sha256(SOURCE.read_bytes()).hexdigest()=='3b90799d26b7783e92c2ac697eaaf8b76d26a787f53205873b997657e114180a', 'source digest moved'
    z=np.load(SOURCE,allow_pickle=False)
    a,ta=normalize(z['chart_matrix'][37]);b,tb=normalize(z['chart_matrix'][176])
    assert all(a[i][j]==b[i][j] for i in range(4) for j in range(5))
    assert all(a[0][j]==b[0][j] for j in range(5,8))
    target,_=signs(a);assert signs(b)[0]==target and 0 not in target
    coords=[(i,j) for j in range(5,8) for i in range(1,4)]
    results={}
    # Initial structural test: insert complete nonframe rays, once each.
    # Follow-through: permit individual normalized coordinates and backtracking.
    for mode,bits in [('columns',3),('coordinates',9)]:
        valid=[];fail=[]
        for mask in range(1<<bits):
            m=[r[:] for r in a]
            for k,(i,j) in enumerate(coords):
                bit=j-5 if mode=='columns' else k
                if mask>>bit&1: m[i][j]=b[i][j]
            ss,ds=signs(m)
            wrong=[i for i,(x,y) in enumerate(zip(ss,target)) if x!=y]
            if not wrong:valid.append(mask)
            else:
                i=wrong[0]
                fail.append({'mask':mask,'basis':''.join(str(j+1) for j in BASES[i]),'determinant':str(ds[i]),'expected_sign':target[i]})
        assert valid==[0,(1<<bits)-1], 'finite finding changed'
        directed,path=reachable(set(valid),bits,True)
        undirected,upath=reachable(set(valid),bits,False)
        results[mode]={'bits':bits,'hybrids':1<<bits,'parent_valid_masks':valid,'invalid_first_witness':fail,'monotone_reachable':directed,'monotone_path':path,'undirected_reachable':undirected,'undirected_path':upath}
    out={'base_revision':'21a97db6aa66912fd37556d81711c0588c454a7d','opening_revision':'c27a36d6e3f47a2b4c7bb017774cbe5df30abdc2','source':str(SOURCE.relative_to(ROOT)),'source_sha256':hashlib.sha256(SOURCE.read_bytes()).hexdigest(),'endpoints':[37,176],'normalized_a':[[str(x) for x in r] for r in a],'normalized_b':[[str(x) for x in r] for r in b],'transform_determinants':[ta,tb],'parent_signs':list(target),'coordinate_order':[[i,j] for i,j in coords],'results':results,'scope':'Exact endpoint-coordinate hybrid graph in one fixed normalized projective frame. Parent safety only; no full F_S or all-parent connectivity statement.','elapsed_seconds':time.perf_counter()-t0,'cpu_seconds':time.process_time()-cpu0}
    if args.write:
        (HERE/'HYBRID_OUTPUT.json').write_text(json.dumps(out,indent=2)+'\n')
    else:
        stored=json.loads((HERE/'HYBRID_OUTPUT.json').read_text())
        for key in ('elapsed_seconds','cpu_seconds'):
            stored.pop(key);out.pop(key)
        assert stored==out, 'stored finite certificate differs from exact replay'
        print('PASS stored exact hybrid certificate')
    for mode,r in results.items():print(mode,'valid',len(r['parent_valid_masks']),'/',r['hybrids'],'monotone_reachable',r['monotone_reachable'],'path',r['monotone_path'],'undirected_reachable',r['undirected_reachable'],'undirected_path',r['undirected_path'])
    print('seconds',time.perf_counter()-t0,'cpu',time.process_time()-cpu0)
if __name__=='__main__':main()
