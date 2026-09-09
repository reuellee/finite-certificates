"""Independent exact arithmetic replay, using only the Python standard library.

Imports neither the producer, historical checker, SymPy nor NumPy. It
reconstructs original equations and all determinants; verifies polynomial
Sylvester resultants; runs its own rational Sturm algorithm; and isolates a
reference algebraic point's 70 signs. The topology inference is in REPORT.md.
"""
from fractions import Fraction as Q
from itertools import combinations, permutations
from pathlib import Path
import copy
import hashlib
import json

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]
SOURCE=ROOT/'ai/omreal/data/DIAG3_triple_fullspace_critical_h1.json'
PIN='c9244a47ded5736e7afe724a9914e75631a22b78653442e88c14f5c397919eb8'


# Sparse multivariate rational polynomials.
def add(*ps):
    out={}
    for p in ps:
        for m,c in p.items():out[m]=out.get(m,Q(0))+c
    return {m:c for m,c in out.items() if c}


def scale(p,c):return {m:v*c for m,v in p.items() if v*c}


def mul(p,q):
    out={}
    for m,c in p.items():
        for n,d in q.items():
            k=tuple(a+b for a,b in zip(m,n));out[k]=out.get(k,Q(0))+c*d
    return {m:c for m,c in out.items() if c}


def const(c,n):return {(0,)*n:Q(c)} if c else {}


def determinant(rows,nvars):
    n=len(rows);out={}
    for perm in permutations(range(n)):
        inv=sum(perm[j]>perm[k] for j in range(n) for k in range(j+1,n))
        term=const((-1)**inv,nvars)
        for j,k in enumerate(perm):term=mul(term,rows[j][k])
        out=add(out,term)
    return out


def read_terms(rec,nvars):
    out={}
    for co,ex in rec:
        assert len(ex)==nvars and all(isinstance(k,int) and k>=0 for k in ex)
        assert tuple(ex) not in out
        out[tuple(ex)]=Q(co)
    return {m:c for m,c in out.items() if c}


def coefficient(p,j,k):
    return {tuple(v for t,v in enumerate(m) if t!=j):co for m,co in p.items() if m[j]==k}


def evaluate(p,point):
    out=Q(0)
    for m,c in p.items():
        for k,x in zip(m,point):c*=x**k
        out+=c
    return out


def primitive(p):
    assert p
    lead=p[max(p)]
    return scale(p,1/lead)


def resultant_e(p,q):
    m=max(ex[1] for ex in p);n=max(ex[1] for ex in q)
    # Sylvester rows: n shifts of p followed by m shifts of q.
    pc=[coefficient(p,1,k) for k in range(m,-1,-1)]
    qc=[coefficient(q,1,k) for k in range(n,-1,-1)]
    rows=[]
    for shift in range(n):rows.append([{}]*shift+pc+[{}]*(n-1-shift))
    for shift in range(m):rows.append([{}]*shift+qc+[{}]*(m-1-shift))
    if not rows:return const(1,1)
    return determinant(rows,1)


# Dense univariate rational arithmetic for an independent Sturm count.
def trim(p):
    p=list(p)
    while p and not p[-1]:p.pop()
    return p


def dense(p):
    if not p:return []
    return trim([p.get((k,),Q(0)) for k in range(max(m[0] for m in p)+1)])


def value(p,x):
    out=Q(0)
    for c in reversed(p):out=out*x+c
    return out


def derivative(p):return trim([k*p[k] for k in range(1,len(p))])


def remainder(p,q):
    p=trim(p);assert q
    while len(p)>=len(q):
        k=len(p)-len(q);c=p[-1]/q[-1]
        for j,a in enumerate(q):p[j+k]-=c*a
        p=trim(p)
    return p


def sturm(p):
    p=trim(p);assert p
    if len(p)==1:return [p]
    out=[p,derivative(p)]
    while out[-1]:
        rem=remainder(out[-2],out[-1])
        if not rem:break
        out.append([-c for c in rem])
    return out


def sign(v):return (v>0)-(v<0)


def variations(values):
    signs=[sign(v) for v in values if v]
    return sum(a!=b for a,b in zip(signs,signs[1:]))


def root_count(p,lo,hi):
    assert lo<hi and value(p,lo)!=0 and value(p,hi)!=0
    seq=sturm(p)
    return variations([value(t,lo) for t in seq])-variations([value(t,hi) for t in seq])


def interval_mul(x,y):
    products=[a*b for a in x for b in y]
    return min(products),max(products)


def interval_value(p,interval):
    acc=(Q(0),Q(0))
    for c in reversed(p):
        lo,hi=interval_mul(acc,interval);acc=lo+c,hi+c
    return acc


def at_c(p,c):
    out={}
    for (j,k),co in p.items():out[(k,)]=out.get((k,),Q(0))+co*c**j
    return dense(out)


def verify(cert,raw):
    assert hashlib.sha256(raw).hexdigest()==PIN==cert['source_sha256']
    data=json.loads(raw)
    assert data['named_presentation']==[5563,16134,19284]==cert['named_presentation']
    base={k:Q(v) for k,v in cert['base'].items()}
    assert base=={'b':Q(-11,3),'f':Q(-11,4),'g':Q(-5,3),'h':Q(3,2),'i':Q(17,4),'d':Q(-253,51)}
    fixed={j:base[name] for j,name in enumerate('abcdefghi') if name in base}
    q=[]
    for rec in data['equations'][:3]:
        p={}
        for co,ex in rec['terms']:
            co=Q(co)
            for j,x in fixed.items():co*=x**ex[j]
            key=(ex[0],ex[2],ex[4]);p[key]=p.get(key,Q(0))+co
        q.append({m:c for m,c in p.items() if c})
    assert not q[0]
    anum=read_terms(cert['a_numerator'],2);aden=read_terms(cert['a_denominator'],2)
    F=read_terms(cert['F'],2)
    assert max(m[0] for m in q[1])==1 and max(m[0] for m in q[2])==1
    assert primitive(coefficient(q[1],0,1))==primitive(aden)
    reduced=[add(mul(coefficient(p,0,0),aden),mul(coefficient(p,0,1),anum)) for p in q[1:]]
    assert not reduced[0]
    assert primitive(reduced[1])==primitive(F)
    C0,C1,C2=[coefficient(F,1,j) for j in range(3)]
    assert max(m[1] for m in F)==2
    assert C2==read_terms(cert['C2'],1)
    w=add(mul(C1,C1),scale(mul(C0,C2),-4))
    assert w==read_terms(cert['W'],1)
    W=dense(w)
    assert len(W)==5 and W[-1]>0
    # Terminal constant remainder is an exact squarefreeness certificate.
    assert len(sturm(W)[-1])==1
    intervals=[tuple(Q(v) for v in pair) for pair in cert['W_root_intervals']]
    assert len(intervals)==4
    previous=None
    for lo,hi in intervals:
        assert lo<hi and (previous is None or previous<lo)
        assert value(W,lo)*value(W,hi)<0
        assert root_count(W,lo,hi)==1
        previous=hi
    L,R=map(Q,cert['oval_c_enclosure'])
    assert intervals[0][1]<L<intervals[1][0]<intervals[1][1]<intervals[2][0]<intervals[2][1]<R<intervals[3][0]
    leading=dense(C2)
    assert len(leading)==3 and leading[-1]>0
    assert leading[1]**2-4*leading[0]*leading[2]<0
    den_resultant=resultant_e(F,aden)
    assert primitive(den_resultant)==primitive(read_terms(cert['denominator_resultant_primitive'],1))
    assert root_count(dense(den_resultant),L,R)==0

    # Rebuild all 70 original 4x4 parent brackets with base coordinates fixed.
    one=const(1,3)
    variables={name:const(v,3) for name,v in base.items()}
    for j,name in enumerate(('a','c','e')):
        variables[name]={tuple(int(j==k) for k in range(3)):Q(1)}
    rows=[]
    for row in range(4):
        rows.append([const(int(row==col),3) for col in range(4)]+[one]+[
            one if row==0 else variables['abcdefghi'[3*col+row-1]] for col in range(3)])
    expected=[''.join(str(k+1) for k in inds) for inds in combinations(range(8),4)]
    assert [record['bracket'] for record in cert['brackets']]==expected
    ref=cert['reference_point'];refc=Q(ref['c']);refe=tuple(Q(v) for v in ref['e_root_interval'])
    assert intervals[1][1]<refc<intervals[2][0]
    refpoly=at_c(F,refc)
    assert root_count(refpoly,*refe)==1
    assert value(refpoly,refe[0])*value(refpoly,refe[1])<0
    denbounds=interval_value(at_c(aden,refc),refe)
    assert denbounds[0]*denbounds[1]>0
    densign=sign(denbounds[0]);signs={}
    for inds,rec in zip(combinations(range(8),4),cert['brackets']):
        wall=determinant([[row[j] for j in inds] for row in rows],3)
        assert wall==read_terms(rec['wall_before_a'],3)
        assert all(m[0]<=1 for m in wall)
        numerator=add(mul(coefficient(wall,0,0),aden),mul(coefficient(wall,0,1),anum))
        assert numerator==read_terms(rec['cleared_numerator'],2)
        res=resultant_e(F,numerator)
        assert primitive(res)==primitive(read_terms(rec['resultant_primitive'],1))
        assert root_count(dense(res),L,R)==0
        assert rec['roots_on_enclosure']==0
        bounds=interval_value(at_c(numerator,refc),refe)
        assert bounds[0]*bounds[1]>0,rec['bracket']
        signs[rec['bracket']]=sign(bounds[0])*densign
    return {'status':'PASS_EXACT_ENTIRE_OVAL_ARITHMETIC','source_sha256':PIN,
            'W_simple_real_roots':4,'compact_oval_middle_roots':[2,3],
            'graph_denominator_nonzero_on_entire_oval':True,
            'whole_oval_parent_brackets_certified':len(signs),
            'reference_point':ref,'parent_signs':''.join('+' if v>0 else '-' for v in signs.values()),
            'theorem_scope':'Fixed-base factor source only; see REPORT.md for quantified topology inference.',
            'full_source_component_compactness':'NOT_ESTABLISHED',
            'triple_bad_component_compactness':'NOT_ESTABLISHED','diagonal_ledger':'2/9'}


def main():
    raw=SOURCE.read_bytes();cert=json.loads((HERE/'certificate.json').read_text())
    report=verify(cert,raw)
    controls=[]
    altered=copy.deepcopy(cert);altered['F'][0][0]=str(Q(altered['F'][0][0])+1);controls.append(('corrupt_F',altered))
    altered=copy.deepcopy(cert);altered['brackets'].pop();controls.append(('omit_parent_bracket',altered))
    altered=copy.deepcopy(cert);altered['brackets'][0]['resultant_primitive'][0][0]='17';controls.append(('corrupt_resultant',altered))
    altered=copy.deepcopy(cert);altered['base']['b']='-4';controls.append(('wrong_base',altered))
    rejected=[]
    for name,candidate in controls:
        try:verify(candidate,raw)
        except (AssertionError,ValueError):rejected.append(name)
        else:raise AssertionError('Hostile control accepted: '+name)
    report['hostile_controls_rejected']=rejected
    print(json.dumps(report,indent=2))


if __name__=='__main__':main()
