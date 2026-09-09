"""Standard-library replay of a narrow exact auxiliary obstruction.

Reconstructs the graph numerator from pinned original equations and checks a
28-by-28 nonzero integer determinant. No producer/CAS/repository arithmetic
is imported. This does not certify full-source noncompactness or D3.
"""
from itertools import combinations_with_replacement
from pathlib import Path
import hashlib,json

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]
PIN='c9244a47ded5736e7afe724a9914e75631a22b78653442e88c14f5c397919eb8'
ZERO=(0,)*9

def add(*polys):
    out={}
    for poly in polys:
        for mon,co in poly.items():out[mon]=out.get(mon,0)+co
    return {mon:co for mon,co in out.items() if co}

def mul(left,right):
    out={}
    for m,c in left.items():
        for n,d in right.items():
            key=tuple(a+b for a,b in zip(m,n))
            out[key]=out.get(key,0)+c*d
    return {m:c for m,c in out.items() if c}

def scale(poly,scalar):
    return {m:c*scalar for m,c in poly.items() if c*scalar}

def axis(j):
    mon=[0]*9;mon[j]=1
    return {tuple(mon):1}

def coeff(poly,index,power):
    out={}
    for mon,co in poly.items():
        if mon[index]==power:
            m=list(mon);m[index]=0;out[tuple(m)]=co
    return out

def derivative(poly,index):
    out={}
    for mon,co in poly.items():
        if mon[index]:
            m=list(mon);m[index]-=1;out[tuple(m)]=co*mon[index]
    return out

def bareiss(matrix):
    """Fraction-free determinant; exact integer divisions are checked."""
    a=[row[:] for row in matrix]
    n=len(a);last=1;sign=1
    for k in range(n-1):
        swap=next((r for r in range(k,n) if a[r][k]),None)
        if swap is None:return 0
        if swap!=k:a[swap],a[k]=a[k],a[swap];sign=-sign
        pivot=a[k][k]
        for r in range(k+1,n):
            for c in range(k+1,n):
                value=a[r][c]*pivot-a[r][k]*a[k][c]
                assert value%last==0
                a[r][c]=value//last
            a[r][k]=0
        last=pivot
    return sign*a[-1][-1]

def require_nonzero_det(rows):
    determinant=bareiss(rows)
    assert determinant!=0
    return determinant

def reject(function):
    try:function()
    except AssertionError:return
    raise AssertionError('hostile control was accepted')

def verify():
    raw=(ROOT/'ai/omreal/data/DIAG3_triple_fullspace_critical_h1.json').read_bytes()
    assert hashlib.sha256(raw).hexdigest()==PIN
    source=json.loads(raw)
    assert source['named_presentation']==[5563,16134,19284]
    assert source['variables']==list('abcdefghi')
    q=[{tuple(mon):co for co,mon in rec['terms']} for rec in source['equations'][:3]]
    a,b,c,d,e,f,g,h,i=[axis(j) for j in range(9)]
    one={ZERO:1}
    dn=add(mul(b,i),scale(mul(b,f),-1),mul(f,g))
    assert q[0]==add(mul(i,d),scale(dn,-1))
    assert all(max(m[3] for m in p)==1 for p in q[1:])
    reduced=[add(mul(i,coeff(p,3,0)),mul(dn,coeff(p,3,1))) for p in q[1:]]
    assert all(max(m[0] for m in p)==1 for p in reduced)
    B,A=coeff(reduced[0],0,0),coeff(reduced[0],0,1)
    D,C=coeff(reduced[1],0,0),coeff(reduced[1],0,1)
    assert A==mul(mul(i,add(f,scale(one,-1))),mul(add(h,scale(one,-1)),add(mul(b,f),scale(mul(c,e),-1))))
    N=add(mul(A,D),scale(mul(C,B),-1))
    assert len(N)==389 and all(m[0]==m[3]==0 for m in N)
    indices=[1,2,4,5,6,7,8]
    pairs=list(combinations_with_replacement(indices,2))
    hess=[scale(derivative(derivative(N,j),k),1 if j==k else 2) for j,k in pairs]
    support=set().union(*(p.keys() for p in hess))
    certificate=json.loads((HERE/'HARMONIC_SCREEN.json').read_text())
    assert certificate['source_sha256']==PIN
    assert certificate['pair_order']==[[source['variables'][j],source['variables'][k]] for j,k in pairs]
    assert certificate['support_equations']==len(support)==1191
    mons=[tuple(m) for m in certificate['selected_monomials']]
    assert len(mons)==len(set(mons))==28
    assert all(m in support for m in mons)
    rows=[[p.get(m,0) for p in hess] for m in mons]
    assert rows==certificate['selected_coefficient_rows']
    determinant=require_nonzero_det(rows)
    assert str(determinant)==certificate['selected_matrix_determinant']
    assert certificate['rank']==28 and certificate['nullity']==0
    duplicate=[r[:] for r in rows];duplicate[-1]=duplicate[0][:]
    reject(lambda:require_nonzero_det(duplicate))
    corrupted=[r[:] for r in rows];corrupted[0][0]+=1
    def equal_rows(candidate):assert candidate==rows
    reject(lambda:equal_rows(corrupted))
    def pin_match(candidate):assert hashlib.sha256(candidate).hexdigest()==PIN
    reject(lambda:pin_match(raw+b' '))
    return {'status':'PASS','scope':'No nonzero constant symmetric second-order operator annihilates this N identically.',
            'graph_numerator_terms':len(N),'coefficient_equations':len(support),'operator_unknowns':28,
            'integer_certificate_determinant':str(determinant),'hostile_controls_rejected':3,
            'theorem_credit':0,'source_orbits_closed':0,'ledger':'2/9 unchanged'}

if __name__=='__main__':print(json.dumps(verify(),indent=2))
