#!/usr/bin/env python3
"""Independent exact replay; imports no repository producer or verifier.

The only equation input is the pinned original source. Standard-library
sparse algebra, determinant expansion, rational Gaussian elimination, and
rational sign isolation reconstruct the reviewed claims.
"""
from pathlib import Path
from fractions import Fraction as Q
from itertools import combinations, permutations
from copy import deepcopy
import hashlib, json, ast, struct, zipfile
from functools import reduce
from math import gcd

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
SOURCE = ROOT/'ai/omreal/data/DIAG3_triple_fullspace_critical_h1.json'
EXPECTED_SOURCE = 'c9244a47ded5736e7afe724a9914e75631a22b78653442e88c14f5c397919eb8'
Z = (0,)*9
V = []
for j in range(9):
    m=list(Z); m[j]=1; V.append({tuple(m):1})
a,b,c,d,e,f,g,h,i=V

def add(*ps):
    r={}
    for p in ps:
        for m,v in p.items(): r[m]=r.get(m,0)+v
    return {m:v for m,v in r.items() if v}
def mul(*ps):
    r={Z:1}
    for p in ps:
        t={}
        for m,v in r.items():
            for n,w in p.items():
                k=tuple(x+y for x,y in zip(m,n)); t[k]=t.get(k,0)+v*w
        r={m:v for m,v in t.items() if v}
    return r
def scale(p,x): return {m:v*x for m,v in p.items() if v*x}
def sub(p,q): return add(p,scale(q,-1))
def powp(p,n):
    r={Z:1}
    for _ in range(n): r=mul(r,p)
    return r
def coeff(p,j,k):
    r={}
    for m,v in p.items():
        if m[j]==k:
            n=list(m);n[j]=0;r[tuple(n)]=v
    return r
def specialize(p,values):
    r={}
    for m,v in p.items():
        n=list(m)
        for j,x in values.items():v*=x**m[j];n[j]=0
        n=tuple(n);r[n]=r.get(n,0)+v
    return {m:v for m,v in r.items() if v}
def value(p,pt): return specialize(p,dict(enumerate(pt))).get(Z,0)
def degree(p,j): return max((m[j] for m in p),default=-1)
def deriv(p,j):
    r={}
    for m,v in p.items():
        if m[j]:
            n=list(m);n[j]-=1;r[tuple(n)]=v*m[j]
    return r
def psign(x): return (x>0)-(x<0)
def reject(fn):
    try:fn()
    except (AssertionError,ValueError,ZeroDivisionError):return True
    raise AssertionError('hostile canary was accepted')
def perm_sign(p):return -1 if sum(p[j]>p[k] for j in range(len(p)) for k in range(j+1,len(p)))%2 else 1

def determinant(matrix):
    n=len(matrix)
    return add(*(scale(mul(*(matrix[j][p[j]] for j in range(n))),perm_sign(p)) for p in permutations(range(n))))
def detq(matrix):
    a=[list(map(Q,row)) for row in matrix];r=Q(1)
    for j in range(len(a)):
        k=next((k for k in range(j,len(a)) if a[k][j]),None)
        if k is None:return Q(0)
        if k!=j:a[k],a[j]=a[j],a[k];r=-r
        pivot=a[j][j];r*=pivot
        for k in range(j+1,len(a)):
            t=a[k][j]/pivot
            for l in range(j+1,len(a)):a[k][l]-=t*a[j][l]
            a[k][j]=0
    return r

def npy_read(z,name):
    raw=z.read(name+'.npy'); assert raw[:6]==b'\x93NUMPY'
    major=raw[6]; offset=10 if major==1 else 12
    ln=struct.unpack('<H' if major==1 else '<I',raw[8:offset])[0]
    head=ast.literal_eval(raw[offset:offset+ln].decode('ascii'))
    assert not head['fortran_order']
    desc=head['descr']; assert desc[0] in '<|='
    formats={'i1':'b','i2':'h','i4':'i','i8':'q','u1':'B','u2':'H','u4':'I','u8':'Q'}
    fmt='<'+formats[desc[1:]]
    flat=[v[0] for v in struct.iter_unpack(fmt,raw[offset+ln:])]
    shape=head['shape']
    if len(shape)==1:return flat
    assert len(shape)==2
    return [flat[k:k+shape[1]] for k in range(0,len(flat),shape[1])]

def main():
    raw=SOURCE.read_bytes(); assert hashlib.sha256(raw).hexdigest()==EXPECTED_SOURCE
    source=json.loads(raw); assert source['variables']==list('abcdefghi')
    eq=source['equations'][:3]; assert [q['factor'] for q in eq]==[5563,16134,19284]
    polys=[]
    for q in eq:
        p={tuple(m):int(v) for v,m in q['terms']}
        assert len(p)==len(q['terms']) and all(len(m)==9 for m in p)
        polys.append(p)
    q1,q2,q3=polys
    # Independent direct extraction from the upstream factor census.
    census=ROOT/'ai/omreal/data/DIAG9_GRAPH_global_factor_census.npz'
    assert hashlib.sha256(census.read_bytes()).hexdigest()=='3984ce87e11fd59d804e59568177248e218cd1c7bb07aae0a9f9f746858728bc'
    with zipfile.ZipFile(census) as z:
        offsets=npy_read(z,'factor_offset');exps=npy_read(z,'factor_exponent');coefs=npy_read(z,'factor_coefficient')
        occurrences=npy_read(z,'occurrence_fourset');fids=npy_read(z,'occurrence_factor')
        unitoffsets=npy_read(z,'occurrence_unit_offset');unitindices=npy_read(z,'occurrence_unit_index');parentlabels=npy_read(z,'parent_bracket_label')
    assert len(offsets)==26741 and len(occurrences)==84840
    for fid,p in zip([5563,16134,19284],polys):
        reconstructed={tuple(exps[k]):coefs[k] for k in range(offsets[fid],offsets[fid+1])}
        assert reconstructed==p
    triple_labels=sorted(combinations(range(1,9),3),key=lambda t:t[::-1]);lookup={x:k for k,x in enumerate(triple_labels)}
    occmap={tuple(o):fid for o,fid in zip(occurrences,fids)}
    permutation=source['named_to_canonical_permutation'];assert permutation==[6,2,5,8,3,4,1,7]
    transported=[]
    for fid in [5563,16134,19284]:
        occ=next(tuple(o) for o,k in zip(occurrences,fids) if k==fid)
        new=tuple(sorted(lookup[tuple(sorted(permutation[v-1] for v in triple_labels[t]))] for t in occ))
        transported.append(occmap[new])
    assert transported==[4373,5563,23221]
    assert sorted(transported)==sorted(source['canonical_row'])
    # Graph solve directly from the input equations.
    dnum=add(mul(b,sub(i,f)),mul(f,g))
    assert q1==sub(mul(i,d),dnum)
    assert degree(q2,3)==degree(q3,3)==1
    red=[]
    for q in [q2,q3]: red.append(add(mul(i,coeff(q,3,0)),mul(dnum,coeff(q,3,1))))
    assert all(degree(q,0)==1 for q in red)
    A,B=coeff(red[0],0,1),coeff(red[0],0,0)
    C,D=coeff(red[1],0,1),coeff(red[1],0,0)
    assert A==mul(i,sub(f,{Z:1}),sub(h,{Z:1}),sub(mul(b,f),mul(c,e)))
    N=sub(mul(A,D),mul(C,B));assert len(N)==389
    assert degree(N,2)==degree(N,4)==2
    C2,C1,C0=[coeff(N,4,k) for k in [2,1,0]]
    Delta=sub(mul(C1,C1),scale(mul(C2,C0),4))
    assert len(Delta)==3257 and degree(Delta,2)==4
    assert sub(sub(powp(add(scale(mul(C2,e),2),C1),2),Delta),scale(mul(C2,N),4))=={}
    # Direct normalized parent determinants, including constants and signs.
    one={Z:1}; zero={}
    matrix=[[one,zero,zero,zero,one,one,one,one],[zero,one,zero,zero,one,a,d,g],[zero,zero,one,zero,one,b,e,h],[zero,zero,zero,one,one,c,f,i]]
    brackets={''.join(str(k+1) for k in cols):determinant([[row[k] for k in cols] for row in matrix]) for cols in combinations(range(8),4)}
    assert len(brackets)==70
    # Reconstruct one original determinant occurrence per named factor;
    # stored units are proposals, checked against independent determinants.
    def primitive(p):
        z=reduce(gcd,(abs(v) for v in p.values()))
        if p[min(p)]<0:z=-z
        return {m:v//z for m,v in p.items()}
    occurrence_audit=[]
    for fid,q in zip([5563,16134,19284],polys):
        idx=next(j for j,k in enumerate(fids) if k==fid);occ=occurrences[idx]
        normals=[]
        for t in occ:
            cols=[v-1 for v in triple_labels[t]]
            normals.append([scale(determinant([[matrix[row][col] for col in cols] for row in range(4) if row!=j]),(-1)**j) for j in range(4)])
        rawdet=determinant([[normals[col][row] for col in range(4)] for row in range(4)])
        names=[''.join(str(x+1) for x in parentlabels[unitindices[j]]) for j in range(unitoffsets[idx],unitoffsets[idx+1])]
        rebuilt=mul(q,*(brackets[name] for name in names))
        assert primitive(rawdet)==primitive(rebuilt)
        occurrence_audit.append({'factor':fid,'derived_triples':[list(triple_labels[t]) for t in occ],'stripped_parent_units':names,'raw_terms':len(rawdet)})
    assert brackets['1346']==a and brackets['1267']==sub(mul(b,f),mul(c,e))
    def unit_name(p):
        names=[name for name,q in brackets.items() if p==q or p==scale(q,-1)]
        assert names;return names[0]
    units={label:unit_name(p) for label,p in [('i',i),('f-1',sub(f,one)),('h-1',sub(h,one)),('bf-ce',sub(mul(b,f),mul(c,e)))]}
    base={1:Q(-23,7),5:Q(-3),6:Q(-1),7:Q(2),8:Q(4)}
    Ns=specialize(N,base)
    F=add(mul(add(scale(powp(c,2),539),scale(c,-28),{Z:1449}),powp(e,2)),mul(add(scale(powp(c,2),1323),scale(c,-8092),{Z:8901}),e),scale(powp(c,2),-2156),scale(c,-27076),{Z:17388})
    assert Ns==scale(F,Q(64,49))
    assert specialize(dnum,base)=={Z:-20}
    anum=add(scale(mul(powp(c,2),e),28),scale(powp(c,2),-28),scale(mul(c,e),37),scale(c,-383),scale(e,69),{Z:-207})
    aden=scale(add(scale(mul(c,e),7),{Z:-69}),2)
    assert add(mul(specialize(B,base),aden),mul(specialize(A,base),anum))=={}
    L,M,T=[coeff(F,4,k) for k in [2,1,0]]
    W=sub(powp(M,2),scale(mul(L,T),4))
    assert specialize(Delta,base)==scale(W,Q(64,49)**2)
    ws=[6398665,36722952,61007646,14826168,-21553047]
    assert W==add(*(scale(powp(c,4-j),v) for j,v in enumerate(ws)))
    assert Q(-28)**2-4*539*1449==-3123260
    derivative=[(4-j)*ws[j] for j in range(4)]
    sylvester=[]
    for j in range(3):sylvester.append([0]*j+ws+[0]*(2-j))
    for j in range(4):sylvester.append([0]*j+derivative+[0]*(3-j))
    resultant=detq(sylvester);disc=resultant/ws[0]
    assert disc==4649793772367457417206802405651256329633792
    def evw(x):
        y=Q(0)
        for v in ws:y=y*x+v
        return y
    intervals=[]
    for k in range(-800,800):
        lo,hi=Q(k,100),Q(k+1,100)
        if evw(lo)*evw(hi)<0:intervals.append((lo,hi))
    assert len(intervals)==4
    def root_contract(iv,polynomial):
        assert len(iv)==4 and degree(polynomial,2)==4
        for j,(lo,hi) in enumerate(iv):
            assert lo<hi
            if j:assert iv[j-1][1]<lo
            assert value(polynomial,[0,0,lo,0,0,0,0,0,0])*value(polynomial,[0,0,hi,0,0,0,0,0,0])<0
    root_contract(intervals,W)
    p=list(map(Q,['-19/28','-23/7','-27/14','-5','-4','-3','-1','2','4']))
    pp=list(map(Q,['90/91','-23/7','-27/14','-5','-6843/1559','-3','-1','2','4']))
    def source_point(pt):
        assert len(pt)==9 and all(value(q,pt)==0 for q in polys)
        assert all(value(q,pt)!=0 for q in brackets.values())
        assert value(i,pt)!=0 and value(A,pt)!=0
        assert pt[3]==value(dnum,pt)/value(i,pt)
        assert pt[0]==-value(B,pt)/value(A,pt)
    source_point(p);source_point(pp)
    assert value(deriv(F,4),p)==Q(5463,4)
    assert value(deriv(F,4),pp)!=0
    def oval_cut(x,y):
        source_point(x);source_point(y)
        assert all(x[j]==y[j]==v for j,v in base.items())
        assert x[2]==y[2] and x[4]!=y[4]
        assert intervals[1][1]<x[2]<intervals[2][0]
        assert x[0]*y[0]<0
    oval_cut(p,pp)
    # Main acceptance predicates exposed to hostile mutations.
    canaries={}
    canaries['wrong_graph_pivot_sign']=reject(lambda:assert_eq(scale(A,-1),mul(i,sub(f,one),sub(h,one),sub(mul(b,f),mul(c,e)))))
    canaries['nonunit_denominator']=reject(lambda:unit_name(add(i,one)))
    canaries['parent_bracket_orientation']=reject(lambda:assert_eq(brackets['1346'],scale(a,-1)))
    canaries['corrupt_fiber_constant']=reject(lambda:assert_eq(Ns,scale(add(F,one),Q(64,49))))
    canaries['repeated_root_quartic']=reject(lambda:root_contract(intervals,powp(sub(powp(c,2),one),2)))
    canaries['duplicate_root_interval']=reject(lambda:root_contract([intervals[0],intervals[0],*intervals[2:]],W))
    canaries['nonuniform_zero_source_denominator']=reject(lambda:source_point([Q(0)]*9))
    wrong=p.copy();wrong[4]+=1
    canaries['point_not_on_source']=reject(lambda:source_point(wrong))
    canaries['same_oval_point_does_not_prove_cut']=reject(lambda:oval_cut(p,p))
    canaries['same_sign_not_a_cut']=reject(lambda:assert_opposite(p[0],p[0]))
    report={'schema':'independent-cefc495-referee-arithmetic-v1','base':'cefc495b27247c4a76f88bce04978422161f7ce9','source_sha256':EXPECTED_SOURCE,'census_sha256':hashlib.sha256(census.read_bytes()).hexdigest(),'factor_provenance':{'ids':[5563,16134,19284],'canonical_transport':transported,'all_factor_ids':26740,'all_occurrences':84840,'direct_derived_determinants':occurrence_audit},'N_terms':len(N),'Delta_terms':len(Delta),'N_bidegree':[degree(N,2),degree(N,4)],'generic_Delta_degree':degree(Delta,2),'parent_units':units,'specialized_quartic':ws,'quartic_resultant':str(resultant),'quartic_discriminant':str(disc),'root_intervals':[[str(x),str(y)] for x,y in intervals],'point_signs_a':[str(p[0]),str(pp[0])],'uniform_points_checked':2,'parent_brackets_per_point':70,'hostile_canaries':canaries,'finite_arithmetic_status':'ACCEPT','deductive_and_source_scope':'See OPENING_AUDIT.md; arithmetic acceptance does not promote D3.'}
    (OUT/'OPENING_ARITHMETIC.json').write_text(json.dumps(report,indent=2,sort_keys=True)+'\n')
    print(json.dumps(report,indent=2,sort_keys=True))

def assert_eq(x,y): assert x==y

def assert_opposite(x,y): assert x*y<0

if __name__=='__main__':main()
