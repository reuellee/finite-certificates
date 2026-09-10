"""Independent certificate validation by polynomial determinant expansion.

No imports from constructive/. All polynomial identities are reconstructed
from the literal parent; no producer acceptance flags are trusted.
"""
import copy
import hashlib
import json
from itertools import permutations
from pathlib import Path
from exact import Q, q, matrix, colex, det, rank, reject, sign

HERE=Path(__file__).resolve().parent
ROOT=HERE.parent
SOURCE=ROOT/'inputs/certificates/THREE_ROW_WITNESS.json'


def trim(p):
    p=list(p)
    while len(p)>1 and not p[-1]:p.pop()
    return p or [Q(0)]


def add(p,r):
    n=max(len(p),len(r))
    return trim([(p[i] if i<len(p) else Q(0))+(r[i] if i<len(r) else Q(0)) for i in range(n)])


def mul(p,r):
    out=[Q(0)]*(len(p)+len(r)-1)
    for i,a in enumerate(p):
        for j,b in enumerate(r):out[i+j]+=a*b
    return trim(out)


def scale(p,c):return trim([c*a for a in p])


def value(p,t):return sum(a*t**i for i,a in enumerate(p))


def pdet(a):
    n=len(a);out=[Q(0)]
    for p in permutations(range(n)):
        term=[Q((-1)**sum(p[i]>p[j] for i in range(n) for j in range(i+1,n)))]
        for i,j in enumerate(p):term=mul(term,a[i][j])
        out=add(out,term)
    return out


def polynomial_geometry(parent,coordinate,signature):
    y=[[[q(x)] for x in row] for row in parent]
    r,c=coordinate;y[r][c].append(Q(1))
    bs=[pdet([[y[r][i] for i in s] for r in range(4)]) for s in colex(8,4)]
    ns=[]
    for i,s in enumerate(colex(8,3)):
        row=[]
        for j in range(4):
            a=[[y[r][k] for k in s]+[[Q(r==j)]] for r in range(4)]
            row.append(scale(pdet(a),Q(1 if (signature>>i)&1 else -1)))
        ns.append(row)
    return bs,ns


def check(c):
    source=json.loads(SOURCE.read_text())
    assert c['input_sha256']==hashlib.sha256(SOURCE.read_bytes()).hexdigest()
    assert c['parent']==source['parent'] and c['coordinate']==source['coordinate']==[2,0]
    assert c['signature']==source['signature']
    assert c['parent_signs']==source['parent_signs']
    bs,ns=polynomial_geometry(c['parent'],c['coordinate'],c['signature'])
    assert all(len(b)<=2 for b in bs) and all(len(v)<=2 for row in ns for v in row)
    get=lambda p,k:p[k] if k<len(p) else Q(0)
    assert [get(b,0) for b in bs]==[q(v) for v in c['parent_brackets_constant']]
    assert [get(b,1) for b in bs]==[q(v) for v in c['parent_brackets_derivative']]
    roots=[-b[0]/b[1] for b in bs if len(b)==2]
    maxint=[max(t for t in roots if t<0),min(t for t in roots if t>0)]
    assert maxint==[q(t) for t in c['maximal_parent_chirotope_open_interval']]
    lo,hi=map(q,c['certified_closed_interval'])
    assert maxint[0]<lo<0<hi<maxint[1]
    margins=[min(sign0*value(b,t) for t in (lo,hi)) for b,sign0 in zip(bs,c['parent_signs'])]
    assert len(margins)==70 and min(margins)>0
    reserve=c['reserve_indices'];assert len(set(reserve))==len(reserve)==5
    assert c['reserve_triples']==[list(colex(8,3)[i]) for i in reserve]
    assert all(len(v)==1 for i in reserve for v in ns[i]),'reserve actually moves'
    e=[[ns[i][j][0] for i in reserve] for j in range(4)]+[[Q(1)]*5]
    determinant=det(e)
    assert determinant==q(c['reserve_augmented_determinant']) and determinant!=0
    reserve_w=list(map(q,c['reserve_constant_normalized_weights']))
    assert len(reserve_w)==5 and min(reserve_w)>0 and sum(reserve_w)==1
    assert [sum(e[j][i]*reserve_w[i] for i in range(5)) for j in range(5)]==[0,0,0,0,1]
    w0=list(map(q,c['full56_weight_constant']));dw=list(map(q,c['full56_weight_derivative']))
    assert len(w0)==len(dw)==56
    ws=[trim([a,b]) for a,b in zip(w0,dw)]
    total=[Q(0)]
    for w in ws:total=add(total,w)
    assert total==[Q(1)]
    residual=[]
    for j in range(4):
        r=[Q(0)]
        for i,w in enumerate(ws):r=add(r,mul(w,ns[i][j]))
        assert r==[Q(0)],'nonzero full56 polynomial residual'
        residual.append([str(get(r,k)) for k in range(3)])
    assert residual==c['normal_residual_polynomial_coefficients']
    weight_margin=min(value(w,t) for w in ws for t in (lo,hi))
    assert weight_margin==q(c['minimum_weight_on_closed_interval'])>0
    eps=q(c['uniform_weight_epsilon'])
    assert eps>0 and all(ws[i]==[eps] for i in range(56) if i not in reserve)
    sup=c['original_three_row_indices'];assert sup==source['support']['indices']
    original=[ns[i] for i in sup]
    assert rank([[v[0] for v in row] for row in original])==c['original_three_row_rank_at_zero']==2
    cols=c['original_three_row_minor_columns']
    minor=pdet([[ns[i][j] for j in cols] for i in sup])
    assert minor==[q(x) for x in c['original_three_row_minor_polynomial']]
    assert len(minor)==2 and minor[0]==0 and minor[1]!=0
    assert c['original_three_row_rank_for_nonzero_t']==3
    old=[Q(0)]*56
    for i,x in zip(sup,source['weights']):old[i]=Q(x,sum(source['weights']))
    old_res=[]
    for j in range(4):
        r=[Q(0)]
        for i,x in enumerate(old):r=add(r,scale(ns[i][j],x))
        old_res.append(r)
    assert all(r[0]==0 for r in old_res) and any(len(r)==2 and r[1]!=0 for r in old_res)
    assert old!=w0,'fixture is a replacement witness, not old witness at zero'
    lift=c['source_matching_lift'];assert lift['formula']=='(old + C*abs(t)*qfull - t*vfull)/(1+C*abs(t))'
    assert list(map(q,lift['old']))==old and lift['matches_original_at_zero'] is True
    qfull=list(map(q,lift['qfull']));vfull=list(map(q,lift['vfull']));C=q(lift['C'])
    assert len(qfull)==len(vfull)==56 and C>0
    assert [qfull[i] for i in reserve]==reserve_w
    assert all(qfull[i]==vfull[i]==0 for i in range(56) if i not in reserve)
    assert sum(qfull)==1 and sum(vfull)==0
    assert C==1+max(abs(vfull[i])/qfull[i] for i in reserve)
    slacks=[C*qfull[i]-abs(vfull[i]) for i in reserve]
    assert slacks==list(map(q,lift['nonnegativity_slack'])) and min(slacks)>0
    assert sorted(set(sup+reserve))==lift['support_union']
    # Put s=abs(t)>=0 and t=side*s. Both rational numerators have
    # nonnegative coefficients; denominator 1+C*s is positive.
    lift_residual=[]
    for side in (-1,1):
        numerators=[trim([old[i],C*qfull[i]-side*vfull[i]]) for i in range(56)]
        assert all(all(a>=0 for a in p) for p in numerators)
        total=[Q(0)]
        for p in numerators:total=add(total,p)
        assert total==[Q(1),C]
        rs=[]
        for j in range(4):
            r=[Q(0)]
            for i,p in enumerate(numerators):
                normal=[a*side**k for k,a in enumerate(ns[i][j])]
                r=add(r,mul(p,normal))
            assert r==[Q(0)],'source lift polynomial residual'
            rs.append([str(get(r,k)) for k in range(3)])
        lift_residual.append(rs)
    assert lift_residual==lift['residual_by_side_and_coordinate']
    assert c['original_obligations_closed']==0 and c['ledger']=='2/9'
    return {'all70_parent_bracket_polynomials_rebuilt':True,'all56_normal_polynomials_rebuilt':True,
            'full56_identity_all_parameters':True,'strict_weight_margin':str(weight_margin),
            'strict_parent_bracket_margin':str(min(margins)),
            'reserve_augmented_determinant':str(determinant),
            'maximal_parent_chamber_interval':list(map(str,maxint)),
            'certified_closed_interval':[str(lo),str(hi)],
            'original_support_minor_polynomial':list(map(str,minor)),
            'replacement_differs_from_original_witness_at_zero':True,
            'separate_support6_lift_matches_original_at_zero':True,
            'support6_lift_exact_on_both_parameter_sides':True,
            'support6_nonnegativity_all_real_parameters':True,
            'minimum_norm_optimality_claimed_or_verified':False,
            'global_original_obligations_closed':0}


def main():
    c=json.loads((ROOT/'constructive/CONTINUATION_CERTIFICATE.json').read_text())
    result=check(c);hostile={}
    def mutation(name,fn):
        x=copy.deepcopy(c);fn(x);hostile[name]=reject(lambda:check(x))
    mutation('altered_normalized_weight',lambda x:x['full56_weight_constant'].__setitem__(0,'1/999'))
    mutation('altered_weight_derivative',lambda x:x['full56_weight_derivative'].__setitem__(0,'1'))
    mutation('reserve_weight_corruption',lambda x:x['reserve_constant_normalized_weights'].__setitem__(0,'1/4'))
    mutation('reserve_duplicate',lambda x:x['reserve_indices'].__setitem__(0,x['reserve_indices'][1]))
    mutation('signature_bit_flip',lambda x:x.__setitem__('signature',x['signature']^(1<<17)))
    mutation('literal_parent_corruption',lambda x:x['parent'][2].__setitem__(0,'-4'))
    mutation('parent_derivative_corruption',lambda x:x['parent_brackets_derivative'].__setitem__(0,'37'))
    mutation('oversized_interval',lambda x:x['certified_closed_interval'].__setitem__(1,'5'))
    mutation('altered_rank_minor',lambda x:x['original_three_row_minor_polynomial'].__setitem__(1,'-27081601'))
    mutation('inflated_weight_margin',lambda x:x.__setitem__('minimum_weight_on_closed_interval','1/999'))
    mutation('source_lift_correction_corruption',lambda x:x['source_matching_lift']['vfull'].__setitem__(17,'0'))
    mutation('source_lift_C_zero',lambda x:x['source_matching_lift'].__setitem__('C','0'))
    mutation('source_lift_zero_join_corruption',lambda x:x['source_matching_lift']['old'].__setitem__(0,'1/1000'))
    result['hostile_controls']=hostile
    (HERE/'CONSTRUCTIVE_REPLAY.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2))


if __name__=='__main__':main()
