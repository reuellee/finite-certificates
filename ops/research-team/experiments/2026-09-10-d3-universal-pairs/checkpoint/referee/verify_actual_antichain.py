"""Independent stdlib audit of three actual antichain anchor arcs.

No producer modules imported. Literal polynomial geometry and all exact
positivity bounds are rebuilt; no topology is inferred from these anchors.
"""
import copy
import hashlib
import json
from itertools import combinations
from pathlib import Path
from exact import Q,q,matrix,rank,sign,colex,reject
from poly import trim,add,mul,scale,pdet,geometry,poly_expression

HERE=Path(__file__).resolve().parent
ROOT=HERE.parent
EPS=Q(1,100000000)


def column(rows):
    assert all(isinstance(r,list) and len(r)==1 for r in rows)
    return [q(r[0]) for r in rows]


def positive(p,cert=None):
    assert any(p)
    k=next(i for i,x in enumerate(p) if x)
    leading=p[k]
    tail=sum(abs(x)*EPS**(i-k) for i,x in enumerate(p) if i>k)
    assert leading>tail>=0,'punctured-interval sign bound fails'
    if cert is not None:
        assert cert=={'vanishing_order':k,'leading_coefficient':str(leading),'tail_bound':str(tail)}
    return k,leading-tail


def check(c):
    src=ROOT/'checkpoint/previous_checkpoint/falsifier/certificate.json'
    old=json.loads(src.read_text())
    assert c['source_sha256']==hashlib.sha256(src.read_bytes()).hexdigest()
    assert c['base_parent']==old['parent']
    y=matrix(c['base_parent']);base_sig=old['signature_integer']
    zero=[[Q(0)]*8 for _ in range(4)]
    b0,n0=geometry(y,zero,base_sig)
    signs=[sign(p[0]) for p in b0];assert all(signs)
    z=c['active_indices'];assert z==old['center_zero_support']
    assert [i for i in range(56) if n0[i][3]==[0]]==z
    assert c['parent_same_component_interval']=='0<=t<=1/100000000'
    rel=c['relative_signs'];assert len(rel)==3 and all(len(r)==5 and all(abs(x)==1 for x in r) for r in rel)
    sigs=[]
    for r in rel:
        s=base_sig
        for i,v in zip(z,r):
            if v<0:s^=1<<i
        sigs.append(s)
    assert sigs==c['signatures'] and len(set(sigs))==3
    # Certify advertised differential rank using the supplied five pivots.
    pivots=c['derivative_pivots'];assert len(set(map(tuple,pivots)))==5
    cols=[]
    for r,j in pivots:
        assert 0<=r<3 and 0<=j<8
        h=[row[:] for row in zero];h[r][j]=Q(1)
        _,n=geometry(y,h,base_sig)
        cols.append([n[i][3][1] if len(n[i][3])>1 else Q(0) for i in z])
    assert rank(cols)==c['derivative_rank']==5
    assert len(c['records'])==4 and sorted(r['own_signature'] for r in c['records'] if r['own_signature'] is not None)==[0,1,2]
    assert sum(r['own_signature'] is None for r in c['records'])==1
    summaries=[]
    lex=list(combinations(range(8),4));cx=colex(8,4);lexorder=[cx.index(t) for t in lex]
    for rec in c['records']:
        own=rec['own_signature'];direction=matrix(rec['direction'])
        b,base_n=geometry(y,direction,base_sig)
        signed_brackets=[scale(p,s) for p,s in zip(b,signs)]
        assert len(rec['parent_sign_certificates'])==70
        parent_margins=[positive(signed_brackets[i],cert)[1] for i,cert in zip(lexorder,rec['parent_sign_certificates'])]
        h=column(rec['offset']);assert len(h)==5
        assert h==[base_n[i][3][1] if len(base_n[i][3])>1 else Q(0) for i in z]
        good_checks=[]
        if own is not None:
            n=[[scale(p,-1 if ((base_sig^sigs[own])>>i)&1 else 1) for p in row] for i,row in enumerate(base_n)]
            assert len(rec['good_margin_certificates'])==56
            good_checks=[positive(n[i][3],rec['good_margin_certificates'][i]) for i in range(56)]
        else:
            assert rec['good_margin_certificates']==[]
        assert sorted(r['other_signature'] for r in rec['bad'])==[i for i in range(3) if i!=own]
        bad_summaries=[]
        for bad in rec['bad']:
            other=bad['other_signature'];ids=bad['normal_indices']
            assert ids==z+[c['outer_index']] and len(set(ids))==6
            assert c['outer_index'] not in z
            f=[[scale(p,-1 if ((base_sig^sigs[other])>>i)&1 else 1) for p in base_n[i]] for i in ids]
            weights=[poly_expression(r[0]) for r in bad['weight_polynomials']]
            assert len(weights)==len(bad['positivity'])==6
            bounds=[positive(p,cert) for p,cert in zip(weights,bad['positivity'])]
            for j in range(4):
                residual=[Q(0)]
                for w,row in zip(weights,f):residual=add(residual,mul(w,row[j]))
                assert residual==[Q(0)],'Gordan polynomial identity fails'
            rows=bad['rank_four_minor_rows']
            assert len(rows)==len(set(rows))==4 and all(0<=i<6 for i in rows)
            minor=pdet([f[i] for i in rows])
            supplied=poly_expression(bad['rank_four_minor_signed'])
            assert supplied==minor or supplied==scale(minor,-1)
            positive(supplied,bad['rank_four_minor_positivity'])
            lam=column(bad['center_kernel']);assert len(lam)==5 and min(lam)>0
            assert all(sum(lam[k]*f[k][j][0] for k in range(5))==0 for j in range(4))
            ev=sum(lam[k]*rel[other][k]*h[k] for k in range(5))
            assert ev==q(bad['offset_evaluation'])<0
            qq=column(bad['q']);uu=column(rec['transverse_coordinate'])
            assert len(qq)==len(uu)==2 and sum(a*b for a,b in zip(qq,uu))==ev
            bad_summaries.append({'other_signature':other,'positive_weights':6,
                                  'identity_all_parameters':True,'vanishing_orders':[x[0] for x in bounds]})
        summaries.append({'own_signature':own,'all70_parent_signs':True,'strict_good_margins':len(good_checks),
                          'parent_minimum_lower_bound':str(min(parent_margins)),
                          'good_margin_vanishing_orders':[x[0] for x in good_checks],
                          'other_bad_signatures':bad_summaries})
    assert c['original_obligations_closed']==0
    return {'verdict':'ACCEPT_ACTUAL_PROPER_PAIRWISE_INCOMPARABLE_SIGNATURE_TRIPLE',
            'signatures':sigs,'same_parent_component':True,'interval':'0<t<=10^-8',
            'arc_checks':summaries,'ordered_noninclusions_certified':6,
            'rank_four_all_bad_arc_certified':True,
            'all_bad_arc_has_no_nonzero_weak_primal_for_any_block':True,
            'original_global_cohomology_computed':False,'original_obligations_closed':0}


def main():
    c=json.loads((ROOT/'falsifier/ACTUAL_ANTICHAIN.json').read_text())
    result=check(c);controls={}
    def mutation(name,fn):
        x=copy.deepcopy(c);fn(x);controls[name]=reject(lambda:check(x))
    mutation('signature_flip',lambda x:x['signatures'].__setitem__(0,x['signatures'][0]^1))
    mutation('parent_direction_corruption',lambda x:x['records'][0]['direction'][0].__setitem__(1,'0'))
    mutation('good_margin_corruption',lambda x:x['records'][0]['good_margin_certificates'][0].__setitem__('leading_coefficient','2'))
    mutation('gordan_weight_corruption',lambda x:x['records'][0]['bad'][0]['weight_polynomials'][0].__setitem__(0,'1'))
    mutation('duplicate_support',lambda x:x['records'][0]['bad'][0]['normal_indices'].__setitem__(0,1))
    mutation('wrong_other_signature',lambda x:x['records'][0]['bad'][0].__setitem__('other_signature',0))
    mutation('enlarged_interval',lambda x:x.__setitem__('parent_same_component_interval','0<=t<=1'))
    mutation('incorrect_parent_sign_bound',lambda x:x['records'][0]['parent_sign_certificates'][0].__setitem__('leading_coefficient','1'))
    mutation('all_bad_rank_minor_corruption',lambda x:x['records'][3]['bad'][0].__setitem__('rank_four_minor_signed','1'))
    result['hostile_controls']=controls
    (HERE/'ACTUAL_ANTICHAIN_REPLAY.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2))


if __name__=='__main__':main()
