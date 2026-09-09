#!/usr/bin/env python3
"""Independent exact supplement: no search, NumPy, or producer/referee imports.

Uses rational Gaussian elimination and 3x3 cofactors, independently of the
replayed referee's 4x4 Leibniz construction. Inputs come only from pinned Git.
"""
from copy import deepcopy
from fractions import Fraction as Q
from functools import reduce
from hashlib import sha256
from itertools import combinations
from math import gcd, lcm
from pathlib import Path
import json
import subprocess
import time

ROOT = Path(__file__).resolve().parents[3]
PRINCIPAL = "7d0efe1c55efff2d17c906569e90f5fb0ae0e371"
SECOND = "da1834fd34065fe826d230c26eb0b6b747dc082c"
INPUTS = {
    PRINCIPAL+":ops/team/ai-d3-shared-pencil-constructor/OBSTRUCTION.json":
        "77bd316237f6fd7060e964aec1852daa10dfaa065a7d0c4194b0a59929a32afa",
    SECOND+":ops/team/ai-d3-shared-pencil-falsifier/upper_chart_0_flow.json":
        "83485ff8bb0a1f8cacffdacbf829cbee5898721b008f8bd54ec2a661ca35e6ab",
    PRINCIPAL+":ai/omgamma/data/cat_4_8.txt":
        "47b2d2b782d298539c85cb170bb10911abe9c82795b4f344e77e3ae64236c7b5",
}
TARGET = [14988895318912, 3405195891438080, 40418075143643136]
TRIPLES = sorted(combinations(range(8),3),key=lambda t:t[::-1])
BASES = sorted(combinations(range(8),4),key=lambda t:t[::-1])

def need(test, message):
    if not test:
        raise AssertionError(message)

def det(matrix):
    """Gaussian determinant over Q; pivoting and sign tracked explicitly."""
    n=len(matrix)
    need(all(len(row)==n for row in matrix),"nonsquare determinant")
    a=[[Q(v) for v in row] for row in matrix]
    result=Q(1)
    for k in range(n):
        pivot=next((r for r in range(k,n) if a[r][k]),None)
        if pivot is None:
            return Q(0)
        if pivot!=k:
            a[pivot],a[k]=a[k],a[pivot]
            result=-result
        value=a[k][k]
        result*=value
        for r in range(k+1,n):
            factor=a[r][k]/value
            for c in range(k+1,n):
                a[r][c]-=factor*a[k][c]
            a[r][k]=Q(0)
    return result

def invert(matrix):
    n=len(matrix)
    a=[[Q(v) for v in row]+[Q(i==j) for j in range(n)]
       for i,row in enumerate(matrix)]
    for k in range(n):
        pivot=next((r for r in range(k,n) if a[r][k]),None)
        need(pivot is not None,"singular frame")
        a[k],a[pivot]=a[pivot],a[k]
        v=a[k][k]
        a[k]=[x/v for x in a[k]]
        for r in range(n):
            if r!=k:
                f=a[r][k]
                a[r]=[x-f*y for x,y in zip(a[r],a[k])]
    return [r[n:] for r in a]

def dot(a,b):
    return sum(x*y for x,y in zip(a,b))

def mm(a,b):
    return [[dot(row,col) for col in zip(*b)] for row in a]

def sign(v):
    need(v!=0,"unexpected zero sign")
    return 1 if v>0 else -1

def signed(sig,i):
    return 1 if sig&(1<<i) else -1

def normals(parent):
    return [[(-1)**(r+3)*det([[parent[k][j] for j in t]
                  for k in range(4) if k!=r]) for r in range(4)]
            for t in TRIPLES]

def primitive(values):
    den=lcm(*(v.denominator for v in values))
    ints=[int(v*den) for v in values]
    div=reduce(gcd,map(abs,ints))
    need(div>0,"zero vector")
    return [v//div for v in ints]

def circuit(rows,sig,record,check_weights=True):
    indices=record.get('row_indices',record.get('support'))
    weights=record['weights']
    need(len(indices)==5 and len(set(indices))==5,"five distinct support rows")
    need(len(weights)==5 and all(type(v) is int and v>0 for v in weights),
         "five strictly positive supplied weights")
    a=[[signed(sig,i)*x for x in rows[i]] for i in indices]
    cof=[(-1)**k*det([row for j,row in enumerate(a) if j!=k])
         for k in range(5)]
    need(all(v!=0 for v in cof),"rank-four circuit: a deletion minor vanished")
    oriented=[sign(cof[0])*v for v in cof]
    need(all(v>0 for v in oriented),"cofactor signs are not coherent")
    for col in range(4):
        need(sum(cof[k]*a[k][col] for k in range(5))==0,"cofactor identity")
    if check_weights:
        need(all(cof[k]*weights[0]==cof[0]*weights[k] for k in range(5)),
             "supplied witness is not the cofactor ray")
    return {'row_indices':indices,'rank':4,'all_five_deletion_minors_nonzero':True,
            'positive_cofactor_vector_primitive':primitive(oriented),
            'minimum_absolute_deletion_minor':str(min(map(abs,cof)))}

def normalize(parent):
    basis=[row[:4] for row in parent]
    inv=invert(basis)
    c=[dot(row,[parent[r][4] for r in range(4)]) for row in inv]
    need(all(c),"fifth frame coordinate zero")
    g=[[v/abs(c[i]) for v in row] for i,row in enumerate(inv)]
    need(det(g)>0,"orientation-preserving normalization")
    gy=mm(g,parent)
    scales=[abs(v) for v in c]+[Q(1)]
    scales.extend(1/sum(abs(gy[r][j]) for r in range(4)) for j in (5,6,7))
    y=[[gy[r][j]*scales[j] for j in range(8)] for r in range(4)]
    need(all(y[r][j]==int(r==j) for r in range(4) for j in range(4)),"basis normalization")
    need([y[r][4] for r in range(4)]==list(map(sign,c)),"fifth signed ray")
    need(all(all(y[r][j]!=0 for r in range(4)) and
             sum(abs(y[r][j]) for r in range(4))==1 for j in (5,6,7)),
         "three open signed simplices")
    return y,g,scales

def gp_relations(parent,sigs):
    chi={t:sign(det([[parent[r][j] for j in t] for r in range(4)])) for t in BASES}
    row_index={t:i for i,t in enumerate(TRIPLES)}
    count=0
    for sig in sigs:
        def ch(labels):
            need(len(set(labels))==4,"repeated GP label")
            parity=(-1)**sum(labels[i]>labels[j] for i in range(4) for j in range(i+1,4))
            t=tuple(sorted(labels))
            return parity*(signed(sig,row_index[t[:3]]) if t[-1]==8 else chi[t])
        for common in combinations(range(9),2):
            rest=[j for j in range(9) if j not in common]
            for a,b,c,d in combinations(rest,4):
                terms=(ch((*common,a,b))*ch((*common,c,d)),
                       -ch((*common,a,c))*ch((*common,b,d)),
                       ch((*common,a,d))*ch((*common,b,c)))
                need(set(terms)=={-1,1},"GP sign relation failed")
                count+=1
    need(count==3780,"GP count")
    return count

def main():
    start=time.perf_counter()
    blobs={}
    for key,digest in INPUTS.items():
        value=subprocess.check_output(['git','show',key],cwd=ROOT)
        need(sha256(value).hexdigest()==digest,"source pin: "+key)
        blobs[key]=value
    keys=list(INPUTS)
    principal=json.loads(blobs[keys[0]])
    second=json.loads(blobs[keys[1]])
    need(principal['parent']==second['parent'],"two frozen parent matrices differ")
    need(principal['signatures']==second['signatures']==TARGET,"frozen signature mismatch")
    parent=principal['parent']
    raw=normals(parent)
    need(all(x.denominator==1 for row in raw for x in row),"raw normal integrality")
    chi=''.join('+' if det([[parent[r][j] for j in t] for r in range(4)])>0 else '-'
                for t in BASES)
    need(all(det([[parent[r][j] for j in t] for r in range(4)])!=0 for t in BASES),"uniformity")
    catalog=[line.strip() for line in blobs[keys[2]].decode().splitlines() if line.strip()]
    need(chi==catalog[2599],"independent catalog binding")
    cp=[circuit(raw,sig,w) for sig,w in zip(TARGET,principal['full_bad_witnesses'])]
    need(len(cp)==3,"principal circuit count")
    prim=[list(map(Q,primitive(row))) for row in raw]
    cs=[circuit(prim,sig,w) for sig,w in zip(TARGET,second['full_dual_witnesses'])]
    need(len(cs)==3,"second circuit count")
    norm,g,scales=normalize(parent)
    nr=normals(norm)
    inverse_g=invert(g)
    for i,t in enumerate(TRIPLES):
        factor=det(g)
        for j in t:
            factor*=scales[j]
        need(factor>0,"positive normal transport")
        transported=[factor*dot(raw[i],col) for col in zip(*inverse_g)]
        need(transported==nr[i],"normal covariance identity")
    normalized_circuits=[circuit(nr,sig,w,check_weights=False)
        for sig,w in zip(TARGET,principal['full_bad_witnesses'])]
    normalized_chi=''.join('+' if det([[norm[r][j] for j in t] for r in range(4)])>0 else '-'
                          for t in BASES)
    need(normalized_chi==chi,"normalized parent signs")
    expected={(e,a,b) for e in range(8)
        for a,b in combinations([i for i,t in enumerate(TRIPLES) if e in t],2)}
    seen=set(); margins=[]
    for rec in principal['restricted_separators']:
        e=rec['label_one_based']-1
        pair=tuple(rec['pair_row_indices'])
        key=(e,*pair)
        need(key in expected and key not in seen,"independent coverage")
        seen.add(key)
        block=rec['block']; need(type(block) is int and block in range(3),"signature index")
        point=[dot(row,rec['point']) for row in g]
        keep=[i for i,t in enumerate(TRIPLES) if e not in t or i in pair]
        need(len(keep)==37,"independent restriction size")
        vals=[signed(TARGET[block],i)*dot(nr[i],point) for i in keep]
        need(min(vals)>0,"normalized separator not strict")
        margins.append(min(vals))
    need(seen==expected and len(seen)==1680,"all normalized choices")
    mutations=[]
    def reject(name,fn):
        try:
            fn()
        except AssertionError:
            mutations.append(name)
            return
        raise AssertionError('mutation escaped: '+name)
    w=deepcopy(principal['full_bad_witnesses'][0]); w['weights'][0]=0
    reject('zero_circuit_weight',lambda:circuit(raw,TARGET[0],w))
    w=deepcopy(principal['full_bad_witnesses'][0]); w['weights'][0]+=1
    reject('corrupt_circuit_ray',lambda:circuit(raw,TARGET[0],w))
    rr=deepcopy(raw); ids=principal['full_bad_witnesses'][0]['row_indices']
    rr[ids[1]]=rr[ids[0]][:]
    reject('dependent_deletion_minor',lambda:circuit(rr,TARGET[0],principal['full_bad_witnesses'][0]))
    rr=deepcopy(raw); rr[ids[0]]=[-v for v in rr[ids[0]]]
    reject('incoherent_cofactor_sign',lambda:circuit(rr,TARGET[0],principal['full_bad_witnesses'][0]))
    result={'status':'PASS_EXACT_OPEN_OBSTRUCTION_SUPPLEMENT','source_hashes':INPUTS,
       'arithmetic':'Python Fraction Gaussian elimination; 3x3 normal cofactors',
       'producer_or_other_referee_imports':False,'search_performed':False,
       'catalog_row_zero_based':2599,'catalog_chirotope':chi,
       'principal_raw_circuits':cp,'second_primitive_circuits':cs,
       'normalized_parent':[[str(v) for v in row] for row in norm],
       'normalization_determinant':str(det(g)),
       'all_56_normal_covariance_identities':True,
       'normalized_circuits':normalized_circuits,
       'normalized_choices_checked':len(seen),'normalized_strict_inequalities':37*len(seen),
       'minimum_normalized_strict_margin':str(min(margins)),
       'independent_gp_sign_relations':gp_relations(parent,TARGET),
       'hostile_mutations_rejected':mutations,
       'robustness_conclusion':'The same finite strict inequalities and the same cofactor signs hold on a nonempty open subset of the nine-dimensional normalized parent space. This excludes only the at-most-two-incident-triples condition.',
       'elapsed_seconds':round(time.perf_counter()-start,6)}
    print(json.dumps(result,indent=2))

if __name__=='__main__':
    main()
