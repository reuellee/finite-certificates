"""Exact integer-polynomial replay, separate from the SymPy discovery producer.

This proves an equivalence of critical systems, not absence of critical points.
It imports no repository polynomial routines and needs only Python's standard
library. Replays all 56 source minors and the 56 unit-pivot identities.
"""
from pathlib import Path
from itertools import combinations, permutations
import hashlib
import json

ROOT=Path(__file__).resolve().parents[3]
SOURCE=ROOT/'ai/omreal/data/DIAG3_triple_fullspace_critical_h1.json'
ZERO=(0,)*9

def const(c): return {ZERO:c} if c else {}
def coord(i): return {tuple(int(j==i) for j in range(9)):1}
def scale(p,c): return {m:v*c for m,v in p.items() if v*c}
def add(*ps):
    out={}
    for p in ps:
        for m,c in p.items():
            out[m]=out.get(m,0)+c
            if not out[m]: del out[m]
    return out
def mul(p,q):
    out={}
    for m,c in p.items():
        for n,d in q.items():
            k=tuple(x+y for x,y in zip(m,n))
            out[k]=out.get(k,0)+c*d
    return {m:c for m,c in out.items() if c}
def prod(ps):
    out=const(1)
    for p in ps: out=mul(out,p)
    return out
def derivative(p,j):
    out={}
    for m,c in p.items():
        if m[j]:
            n=list(m);n[j]-=1
            out[tuple(n)]=c*m[j]
    return out
def determinant(rows):
    n=len(rows);out={}
    for perm in permutations(range(n)):
        inversions=sum(perm[i]>perm[j] for i in range(n) for j in range(i+1,n))
        out=add(out,scale(prod(rows[i][perm[i]] for i in range(n)),(-1)**inversions))
    return out
def columns(rows,indices): return [[r[j] for j in indices] for r in rows]
def decode(record): return {tuple(m):int(c) for c,m in record['terms']}
def termlist(p): return [[c,list(m)] for m,c in sorted(p.items())]

def verify():
    raw=SOURCE.read_bytes()
    assert hashlib.sha256(raw).hexdigest()=='c9244a47ded5736e7afe724a9914e75631a22b78653442e88c14f5c397919eb8'
    data=json.loads(raw)
    assert data['height_index']==1
    assert data['named_presentation']==[5563,16134,19284]
    q=[decode(r) for r in data['equations'][:3]]
    J=[[derivative(p,j) for j in range(9)] for p in q]
    a,b,c,d,e,f,g,h,i=[coord(k) for k in range(9)]
    unit=scale(prod([i,add(f,const(-1)),add(h,const(-1)),add(mul(b,f),scale(mul(c,e),-1))]),-1)
    assert determinant(columns(J[:2],(0,3)))==unit
    Y=[[const(int(r==k)) for k in range(4)]+[const(1)]+[const(1) if r==0 else coord(3*k+r-1) for k in range(3)] for r in range(4)]
    walls={''.join(str(k+1) for k in I):determinant(columns(Y,I)) for I in combinations(range(8),4)}
    # Identify every localizer with a genuine parent bracket, including sign.
    localizers=[i,add(f,const(-1)),add(h,const(-1)),add(mul(b,f),scale(mul(c,e),-1))]
    matches=[]
    for p in localizers:
        options=[(name,sgn) for name,w in walls.items() for sgn in (1,-1) if p==scale(w,sgn)]
        assert options
        matches.append(options)
    remainder=[2,4,5,6,7,8]
    basic={j:determinant(columns(J,(0,3,j))) for j in remainder}
    basic[0]={};basic[3]={}
    reconstructed=0
    for record in data['equations'][3:]:
        I=record['columns']
        actual=determinant(columns(J,I))
        assert actual==decode(record),('source minor',I)
        rhs={}
        for k,j in enumerate(I):
            other=[v for pos,v in enumerate(I) if pos!=k]
            rhs=add(rhs,scale(mul(basic[j],determinant(columns(J[:2],other))),(-1)**k))
        assert mul(unit,actual)==rhs,('pivot identity',I)
        reconstructed+=1
    assert reconstructed==56
    # Reconstruct the d-graph without rational arithmetic: i*d = b*(i-f)+f*g.
    D=add(mul(b,add(i,scale(f,-1))),mul(f,g))
    assert q[0]==add(mul(i,d),scale(D,-1))
    # The a coefficient is a parent unit before and after the d-graph.
    acoefficient=prod(localizers[1:])
    assert derivative(q[1],0)==acoefficient
    assert derivative(acoefficient,3)=={}
    # Unique multipliers solve row3 + lam*row1 + mu*row2 = 0
    # on the eight non-height columns. The unit denominator is retained.
    lam_num=determinant(columns([J[1],J[2]],(0,3)))
    mu_num=scale(determinant(columns([J[0],J[2]],(0,3))),-1)
    for j in [0,2,3,4,5,6,7,8]:
        lhs=add(mul(unit,J[2][j]),mul(lam_num,J[0][j]),mul(mu_num,J[1][j]))
        assert lhs==basic[j],('multiplier identity',j)
    # Without a nonzero pivot, six minors can vanish while another is nonzero.
    degenerate=[[const(0) for _ in range(9)] for _ in range(3)]
    for r,j in enumerate((2,4,5)):degenerate[r][j]=const(1)
    assert all(not determinant(columns(degenerate,(0,3,j))) for j in remainder)
    assert determinant(columns(degenerate,(2,4,5)))==const(1)
    result={'source_sha256':hashlib.sha256(raw).hexdigest(),'source_minors_rebuilt':56,'unit_pivot_identities':56,'multiplier_identities':8,'selected_minors':6,'selected_minor_terms':sum(len(basic[j]) for j in remainder),'pivot_unit_terms':len(unit),'parent_unit_matches':matches,'rank_drop_countermodels_checked':1,'result':'PASS_CRITICAL_SYSTEM_EQUIVALENCE','critical_locus_empty':'NOT_PROVED','full_source_noncompactness':'NOT_PROVED','pair_injectivity':'NOT_PROVED','ledger':'2/9','independent_review':'NOT_PERFORMED; separate arithmetic implementation only'}
    print(json.dumps(result,indent=2))
    return result

if __name__=='__main__':verify()
