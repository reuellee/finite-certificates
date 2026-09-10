#!/usr/bin/env python3
"""Exact construction/replay of one witness-continuation fixture; stdlib only.
No original global obligation is decided. Equality in t follows multilinearity
of cofactors under the sole change Y[2,0] += t.
"""
from pathlib import Path
from itertools import combinations
from fractions import Fraction as Q
from math import prod
import argparse, hashlib, json

HERE=Path(__file__).resolve().parent
ROOT=HERE.parent
TRIPLES=sorted(combinations(range(8),3),key=lambda t:t[::-1])
BASES=sorted(combinations(range(8),4),key=lambda t:t[::-1])
RESERVE=[17,24,33,40,54]

def det(a):
    n=len(a)
    if not n:return Q(1)
    if n==1:return a[0][0]
    return sum((-1)**j*a[0][j]*det([r[:j]+r[j+1:] for r in a[1:]]) for j in range(n))

def solve(a,b):
    n=len(a);m=[list(map(Q,row))+[Q(v)] for row,v in zip(a,b)]
    for j in range(n):
        k=next(i for i in range(j,n) if m[i][j])
        m[j],m[k]=m[k],m[j];d=m[j][j];m[j]=[v/d for v in m[j]]
        for i in range(n):
            if i!=j:
                d=m[i][j];m[i]=[v-d*w for v,w in zip(m[i],m[j])]
    return [m[i][-1] for i in range(n)]

def sign(q):return (q>0)-(q<0)

def geometry(p,sig):
    brackets=[det([[p[r][c] for c in b] for r in range(4)]) for b in BASES]
    a=[[(-1)**(r+3)*(1 if sig>>i&1 else -1)*det([[p[k][c] for c in t] for k in range(4) if k!=r]) for r in range(4)] for i,t in enumerate(TRIPLES)]
    return brackets,a

def stringify(value):
    if isinstance(value,Q):return str(value)
    if isinstance(value,dict):return {k:stringify(v) for k,v in value.items()}
    if isinstance(value,(list,tuple)):return [stringify(v) for v in value]
    return value

def construct():
    src=ROOT/'inputs/certificates/THREE_ROW_WITNESS.json'
    f=json.loads(src.read_text());p=[[Q(v) for v in row] for row in f['parent']]
    sig=f['signature'];assert sig==40418075143643136
    assert f['coordinate']==[2,0]
    b0,a0=geometry(p,sig)
    p1=[r[:] for r in p];p1[2][0]+=1
    b1,a1=geometry(p1,sig)
    db=[v-u for u,v in zip(b0,b1)]
    da=[[v-u for u,v in zip(r,s)] for r,s in zip(a0,a1)]
    assert [sign(v) for v in b0]==f['parent_signs']
    roots=[-b/d for b,d in zip(b0,db) if d]
    lower=max(r for r in roots if r<0);upper=min(r for r in roots if r>0)
    radius=min(-lower,upper)/2
    interval=[-radius,radius]
    # Single-coordinate variation makes every bracket and normal affine.
    for t in interval:
        assert [sign(b+t*d) for b,d in zip(b0,db)]==f['parent_signs']
    assert all(0 not in TRIPLES[i] for i in RESERVE)
    assert all(not any(da[i]) for i in RESERVE)
    E=[[a0[i][j] for i in RESERVE] for j in range(4)]+[[Q(1)]*5]
    determinant=det(E);assert determinant
    q=solve(E,[0,0,0,0,1]);assert all(v>0 for v in q)
    # Add epsilon to all56 slots; reserve correction keeps five affine
    # equalities exact. E is constant on the complete one-parameter family.
    s0=[sum(r[j] for r in a0) for j in range(4)]+[Q(56)]
    ds=[sum(r[j] for r in da) for j in range(4)]+[Q(0)]
    c0=solve(E,s0);dc=solve(E,ds)
    epsilon=Q(1,100)
    while any(q[i]+epsilon*(1-c0[i]-t*dc[i])<=0 for i in range(5) for t in interval):epsilon/=10
    w0=[epsilon]*56;dw=[Q(0)]*56
    for k,i in enumerate(RESERVE):
        w0[i]=q[k]+epsilon*(1-c0[k]);dw[i]=-epsilon*dc[k]
    assert sum(w0)==1 and sum(dw)==0
    # All three polynomial coefficients must vanish; there is no sampling.
    residual=[]
    for j in range(4):
        coeff=[sum(w0[i]*a0[i][j] for i in range(56)),
               sum(dw[i]*a0[i][j]+w0[i]*da[i][j] for i in range(56)),
               sum(dw[i]*da[i][j] for i in range(56))]
        assert not any(coeff);residual.append(coeff)
    endpoint_weights=[[u+t*v for u,v in zip(w0,dw)] for t in interval]
    margin=min(v for w in endpoint_weights for v in w);assert margin>0
    ids=f['support']['indices'];assert ids==[35,24,17]
    eventrows=[a0[i] for i in ids]
    assert eventrows==[[Q(v) for v in row] for row in f['signed_normals']]
    assert all(sum(Q(w)*a0[i][j] for i,w in zip(ids,f['weights']))==0 for j in range(4))
    assert all(any(det([[a0[i][c] for c in cc],[a0[k][c] for c in cc]]) for cc in combinations(range(4),2)) for i,k in combinations(ids,2))
    wallcols=f['wall_minor_columns']
    minor0=det([[a0[i][c] for c in wallcols] for i in ids]);assert minor0==0
    minorderiv=det([[a1[i][c] for c in wallcols] for i in ids]);assert minorderiv!=0
    # Only row35 in original support moves, so the minor is exactly linear.
    assert sum(any(da[i]) for i in ids)==1
    assert all(det([[a0[i][c] for c in cc] for i in ids])==0 for cc in combinations(range(4),3))
    # Hostile controls use exact equality and positivity predicates.
    def valid(w,t):
        return len(w)==56 and all(v>=0 for v in w) and sum(w)==1 and all(sum(w[i]*(a0[i][j]+t*da[i][j]) for i in range(56))==0 for j in range(4))
    corrupt=w0[:];corrupt[RESERVE[0]]+=Q(1,1000000)
    old=[Q(0)]*56
    for i,w in zip(ids,f['weights']):old[i]=Q(w,sum(f['weights']))
    # Lift the exact source three-row witness through the event, with six
    # total support indices. The only changed original row is 35; reserve
    # rows stay constant. A |t| term offsets both signs of the correction.
    defect=[sum(old[i]*da[i][j] for i in range(56)) for j in range(4)]+[Q(0)]
    v=solve(E,defect)
    C=1+max(abs(vi)/qi for vi,qi in zip(v,q))
    qfull=[Q(0)]*56;vfull=[Q(0)]*56
    for k,i in enumerate(RESERVE):qfull[i]=q[k];vfull[i]=v[k]
    assert sum(vfull)==0 and all(C*qi>abs(vi) for qi,vi in zip(q,v))
    assert all(sum(vfull[i]*a0[i][j] for i in range(56))==defect[j] for j in range(4))
    assert all(sum(vfull[i]*da[i][j] for i in range(56))==0 for j in range(4))
    def source_lift(t):
        return [(oi+C*abs(t)*qi-t*vi)/(1+C*abs(t)) for oi,qi,vi in zip(old,qfull,vfull)]
    assert source_lift(Q(0))==old
    assert all(valid(source_lift(t),t) for t in interval+[Q(0)])
    # For each side sigma, numerator is old+t*(sigma*C*qfull-vfull)
    # and denominator 1+sigma*C*t. Verify polynomial equality formally.
    lifted_residual=[]
    for sigma in (-1,1):
        slope=[sigma*C*qi-vi for qi,vi in zip(qfull,vfull)]
        assert sum(old)==1 and sum(slope)==sigma*C
        coeffs=[]
        for j in range(4):
            cc=[sum(old[i]*a0[i][j] for i in range(56)),
                sum(slope[i]*a0[i][j]+old[i]*da[i][j] for i in range(56)),
                sum(slope[i]*da[i][j] for i in range(56))]
            assert not any(cc);coeffs.append(cc)
        lifted_residual.append(coeffs)
    hostile={'altered_weight_rejected':not valid(corrupt,Q(0)),
             'original_three_row_witness_offwall_rejected':not valid(old,interval[1]),
             'original_three_row_witness_at_event_accepted':valid(old,Q(0)),
             'full_witness_at_both_endpoints_accepted':all(valid(w,t) for w,t in zip(endpoint_weights,interval))}
    assert all(hostile.values())
    return stringify({'classification':'EXACT_LOCAL_CONTINUATION_AND_CONDITIONAL_SELECTION_LEMMA',
       'source_revision':'3e69bc43f1a92ebd1c508bd75e695af76c99e0b0',
       'mathematical_source_revision':'59fec66666518257c585194b81061f60d91f439d',
       'input_file':'inputs/certificates/THREE_ROW_WITNESS.json',
       'input_sha256':hashlib.sha256(src.read_bytes()).hexdigest(),
       'parent':f['parent'],'coordinate':[2,0],'parameter':'Y(t)[2,0]=Y(0)[2,0]+t',
       'signature':sig,'triple_order':'colex sorted combinations(range(8),3)',
       'normal_convention':'raw signed cofactor normals, bit1 positive bit0 negative',
       'maximal_parent_chirotope_open_interval':[lower,upper],
       'certified_closed_interval':interval,'parent_signs':f['parent_signs'],
       'parent_brackets_constant':b0,'parent_brackets_derivative':db,
       'reserve_indices':RESERVE,'reserve_triples':[TRIPLES[i] for i in RESERVE],
       'reserve_augmented_determinant':determinant,'reserve_constant_normalized_weights':q,
       'uniform_weight_epsilon':epsilon,'full56_weight_constant':w0,'full56_weight_derivative':dw,
       'minimum_weight_on_closed_interval':margin,'normal_residual_polynomial_coefficients':residual,
       'original_three_row_indices':ids,'original_three_row_rank_at_zero':2,
       'original_three_row_rank_for_nonzero_t':3,'original_three_row_minor_columns':wallcols,
       'original_three_row_minor_polynomial':[0,minorderiv],
       'source_matching_lift':{'support_union':sorted(set(ids+RESERVE)),
          'formula':'(old + C*abs(t)*qfull - t*vfull)/(1+C*abs(t))',
          'old':old,'qfull':qfull,'vfull':vfull,'C':C,
          'nonnegativity_slack':[C*qi-abs(vi) for qi,vi in zip(q,v)],
          'residual_by_side_and_coordinate':lifted_residual,
          'matches_original_at_zero':True,'valid_signed_normal_identity_domain':'all real t; original parent scope restricted to certified interval'},
       'targeted_numerical_support_searches':1,'exact_continuum_families_certified':1,
       'hostile_controls':hostile,'original_obligations_closed':0,'ledger':'2/9',
       'scope_exclusions':['global bad-locus continuity','global support or chart coverage','compact-support maps','original injectivity','triple Hc0 vanishing']})

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--write',action='store_true');args=ap.parse_args()
    cert=construct();path=HERE/'CONTINUATION_CERTIFICATE.json'
    if args.write:path.write_text(json.dumps(cert,indent=2)+'\n')
    else:assert json.loads(path.read_text())==cert,'certificate changed or mismatch'
    print(json.dumps({k:cert[k] for k in ['classification','certified_closed_interval','reserve_indices','reserve_constant_normalized_weights','uniform_weight_epsilon','minimum_weight_on_closed_interval','original_three_row_minor_polynomial','hostile_controls','ledger']},indent=2))

if __name__=='__main__':main()
