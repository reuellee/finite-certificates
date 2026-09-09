#!/usr/bin/env python3
"""Independent final replay of immutable research candidate 65f1524.

Standard library only. Imports only this referee's earlier independent
arithmetic. Candidate files are read from the immutable Git revision, not
from producer execution or verifier acceptance. --repo selects any clone
containing that commit; no absolute workspace path is embedded.
"""
import argparse, hashlib, json, subprocess
from pathlib import Path
from itertools import combinations
from collections import Counter
from audit_cefc495 import (Q,Z,V,add,mul,scale,sub,powp,coeff,specialize,
    degree,deriv,value,determinant,detq,reject,assert_eq)

REV='65f1524bda77ebc5b74a0857e23c4323c18ad263'
a,b,c,d,e,f,g,h,i=V
SOURCE='ai/omreal/data/DIAG3_triple_fullspace_critical_h1.json'
EXPECTED='c9244a47ded5736e7afe724a9914e75631a22b78653442e88c14f5c397919eb8'

# Univariate rational polynomial implementation used only by this referee.
def trim(p):
    p=list(p)
    while p and not p[-1]:p.pop()
    return p

def divrem(p,q):
    p=list(map(Q,trim(p)));q=list(map(Q,trim(q)));assert q
    while len(p)>=len(q):
        k=len(p)-len(q);x=p[-1]/q[-1]
        for j,v in enumerate(q):p[j+k]-=x*v
        p=trim(p)
    return p

def ueval(p,x):
    y=Q(0)
    for v in reversed(p):y=y*x+v
    return y

def sturm(p):
    p=trim(p);assert p
    d=[j*p[j] for j in range(1,len(p))];seq=[p]
    if not d:return seq
    seq.append(d)
    while True:
        r=[-v for v in divrem(seq[-2],seq[-1])]
        if not r:return seq
        # Positive normalization controls integer growth without changing signs.
        r=[v/abs(r[-1]) for v in r]
        seq.append(r)

def variations(seq,x):
    signs=[(ueval(p,x)>0)-(ueval(p,x)<0) for p in seq];signs=[s for s in signs if s]
    return sum(a!=b for a,b in zip(signs,signs[1:]))

def count_closed(p,lo,hi):
    assert lo<hi and ueval(p,lo)!=0 and ueval(p,hi)!=0
    seq=sturm(p)
    return variations(seq,lo)-variations(seq,hi)

def uni(p,j=2):
    assert all(all(k==j or v==0 for k,v in enumerate(m)) for m in p)
    return [Q(coeff(p,j,k).get(Z,0)) for k in range(degree(p,j)+1)]

def decode(terms,vars_):
    r={}
    for cv,mv in terms:
        assert len(mv)==len(vars_)
        m=list(Z)
        for j,k in zip(vars_,mv):m[j]=int(k)
        assert tuple(m) not in r;r[tuple(m)]=Q(cv)
    return {m:v for m,v in r.items() if v}

def scalar_equal(p,q):
    assert p and q and set(p)==set(q)
    m=next(iter(p));t=p[m]/q[m];assert t
    assert p==scale(q,t)

def resultant_e(F,K):
    n,m=degree(F,4),degree(K,4);assert n>=0 and m>=0
    rows=[];fx=[coeff(F,4,j) for j in range(n,-1,-1)];kx=[coeff(K,4,j) for j in range(m,-1,-1)]
    for j in range(m):rows.append([{}]*j+fx+[{}]*(m-1-j))
    for j in range(n):rows.append([{}]*j+kx+[{}]*(n-1-j))
    return determinant(rows)

def interval_product(x,y):
    z=[a*b for a in x for b in y];return min(z),max(z)

def interval_horner(p,lo,hi):
    ans=(Q(0),Q(0))
    for v in reversed(p):
        ans=interval_product(ans,(lo,hi));ans=(ans[0]+v,ans[1]+v)
    return ans

def strict_interval_sign(p,lo,hi):
    low,high=interval_horner(p,lo,hi)
    assert low>0 or high<0
    return 1 if low>0 else -1


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--repo',type=Path,default=Path(__file__).resolve().parents[3]);args=ap.parse_args()
    pins={}; cache={}
    def read(path):
        if path not in cache:
            raw=subprocess.check_output(['git','show',REV+':'+path],cwd=args.repo)
            cache[path]=raw;pins[path]=hashlib.sha256(raw).hexdigest()
        return cache[path]
    def js(path):return json.loads(read(path))
    source=js(SOURCE);assert pins[SOURCE]==EXPECTED
    polys=[decode(row['terms'],range(9)) for row in source['equations'][:3]]
    assert [row['factor'] for row in source['equations'][:3]]==[5563,16134,19284]
    q1,q2,q3=polys
    dnum=add(mul(b,sub(i,f)),mul(f,g));assert q1==sub(mul(i,d),dnum)
    red=[add(mul(i,coeff(q,3,0)),mul(dnum,coeff(q,3,1))) for q in [q2,q3]]
    A,B=coeff(red[0],0,1),coeff(red[0],0,0);C,D=coeff(red[1],0,1),coeff(red[1],0,0)
    assert A==mul(i,sub(f,{Z:1}),sub(h,{Z:1}),sub(mul(b,f),mul(c,e)))
    N=sub(mul(A,D),mul(C,B));assert len(N)==389
    assert coeff(q2,0,1)==mul(sub(f,{Z:1}),sub(h,{Z:1}),sub(mul(b,f),mul(c,e)))
    one={Z:1};zero={}
    matrix=[[one,zero,zero,zero,one,one,one,one],[zero,one,zero,zero,one,a,d,g],[zero,zero,one,zero,one,b,e,h],[zero,zero,zero,one,one,c,f,i]]
    brackets={''.join(str(k+1) for k in cols):determinant([[row[k] for k in cols] for row in matrix]) for cols in combinations(range(8),4)}
    canaries={}
    # Whole-oval reconstruction from q1/q2/q3 and every direct bracket.
    cert=js('ops/team/d3-real-oval-falsifier/certificate.json')
    base={1:Q(-11,3),5:Q(-11,4),6:Q(-5,3),7:Q(3,2),8:Q(17,4)}
    assert cert['base']=={'b':'-11/3','f':'-11/4','g':'-5/3','h':'3/2','i':'17/4','d':'-253/51'}
    dv=value(dnum,[0,base[1],0,0,0,base[5],base[6],base[7],base[8]])/base[8]
    assert dv==Q(-253,51);fixed=dict(base);fixed[3]=dv
    anum=decode(cert['a_numerator'],[2,4]);aden=decode(cert['a_denominator'],[2,4]);F=decode(cert['F'],[2,4])
    assert aden==scale(sub(mul(c,e),{Z:Q(121,12)}),9180)
    assert add(mul(specialize(B,base),aden),mul(specialize(A,base),anum))=={}
    scalar_equal(specialize(N,base),F)
    q2s=specialize(q2,fixed);q3s=specialize(q3,fixed)
    assert add(mul(coeff(q2s,0,0),aden),mul(coeff(q2s,0,1),anum))=={}
    scalar_equal(add(mul(coeff(q3s,0,0),aden),mul(coeff(q3s,0,1),anum)),F)
    L,M,T=[coeff(F,4,k) for k in [2,1,0]]
    W=sub(mul(M,M),scale(mul(L,T),4));assert W==decode(cert['W'],[2])
    Lc=uni(L);assert len(Lc)==3 and Lc[2]>0 and Lc[1]**2-4*Lc[2]*Lc[0]<0
    wu=uni(W);assert len(wu)==5 and wu[-1]>0 and len(sturm(wu)[-1])==1
    iv=[tuple(map(Q,ends)) for ends in cert['W_root_intervals']]
    assert len(iv)==4
    for j,(lo,hi) in enumerate(iv):
        assert count_closed(wu,lo,hi)==1 and ueval(wu,lo)*ueval(wu,hi)<0
        if j:assert iv[j-1][1]<lo
    J=tuple(map(Q,cert['oval_c_enclosure']));assert J==(Q(-53,25),Q(-403,200))
    assert iv[0][1]<J[0]<iv[1][0] and iv[2][1]<J[1]<iv[3][0]
    assert count_closed(wu,*J)==2
    denres=resultant_e(F,aden);scalar_equal(denres,decode(cert['denominator_resultant_primitive'],[2]));assert count_closed(uni(denres),*J)==0
    rows=cert['brackets'];assert len(rows)==70 and [r['bracket'] for r in rows]==list(brackets)
    c0=Q(cert['reference_point']['c']);elo,ehi=map(Q,cert['reference_point']['e_root_interval'])
    assert iv[1][1]<c0<iv[2][0]
    fc0=uni(specialize(F,{2:c0}),4);assert count_closed(fc0,elo,ehi)==1
    den_anchor=uni(specialize(aden,{2:c0}),4);dsign=strict_interval_sign(den_anchor,elo,ehi)
    outsign='';maxresdeg=0
    for row in rows:
        p=specialize(brackets[row['bracket']],fixed)
        assert degree(p,0)<=1 and p==decode(row['wall_before_a'],[0,2,4])
        K=add(mul(coeff(p,0,0),aden),mul(coeff(p,0,1),anum))
        assert K==decode(row['cleared_numerator'],[2,4])
        R=resultant_e(F,K);scalar_equal(R,decode(row['resultant_primitive'],[2]));assert count_closed(uni(R),*J)==0
        ks=strict_interval_sign(uni(specialize(K,{2:c0}),4),elo,ehi)
        outsign+='+' if ks*dsign>0 else '-';maxresdeg=max(maxresdeg,degree(R,2))
    expected_signs='++--+-++-++++--++--+--+-+-++-------------+-++++-+---++-+----+----++++-'
    assert outsign==expected_signs
    canaries['oval_corrupt_equation']=reject(lambda:scalar_equal(specialize(N,base),add(F,one)))
    canaries['oval_missing_bracket']=reject(lambda:assert_eq(len(rows[:-1]),70))
    canaries['oval_false_resultant']=reject(lambda:scalar_equal(denres,add(denres,one)))
    canaries['oval_interval_crosses_true_denominator_root']=reject(lambda:assert_eq(count_closed(uni(denres),Q(-10),Q(10)),0))
    canaries['oval_repeated_branch_roots']=reject(lambda:assert_eq(len(sturm([1,0,-2,0,1])[-1]),1))
    # Constant symmetric Hessian operator: independently derived coefficients.
    hcert=js('ops/team/d3-real-global-prover/HARMONIC_SCREEN.json')
    indexes=[1,2,4,5,6,7,8];pairs=[(x,y) for j,x in enumerate(indexes) for y in indexes[j:]]
    cols=[scale(deriv(deriv(N,x),y),1 if x==y else 2) for x,y in pairs]
    support=set().union(*(set(q) for q in cols));assert len(support)==1191
    assert hcert['pair_order']==[[list('abcdefghi')[x],list('abcdefghi')[y]] for x,y in pairs]
    monomials=[tuple(m) for m in hcert['selected_monomials']];assert len(monomials)==len(set(monomials))==28
    hrows=[[p.get(m,0) for p in cols] for m in monomials]
    assert hrows==hcert['selected_coefficient_rows'];hdet=detq(hrows)
    assert hdet==Q(-7421703487488)==Q(hcert['selected_matrix_determinant'])
    corrupted=[r[:] for r in hrows];corrupted[0]=corrupted[1][:]
    canaries['hessian_duplicate_equation']=reject(lambda:assert_nonzero(detq(corrupted)))
    corrupted=[r[:] for r in hrows];corrupted[0][0]+=1
    canaries['hessian_changed_coefficient']=reject(lambda:assert_eq(corrupted,hrows))
    # Arbitrary-block bit identity and integral H1 fillers, no producer imports.
    edges=list(combinations(range(6),2))
    def pattern(gap,word):
        w=Q(2*gap-1,2);mask=0
        for k,(u,v) in enumerate(edges):
            required_u=int(w>v);required_v=int(u>w)
            if ((word>>u)&1)==required_u and ((word>>v)&1)==required_v:mask|=1<<k
        return mask
    def edge_boundary(x,y):return Counter({(min(x,y),max(x,y)):1 if x<y else -1})
    def chain_boundary(tris):
        out=Counter()
        for scale_,(a_,b_,c_) in tris:
            for x,y in [(a_,b_),(b_,c_),(c_,a_)]:
                out[(min(x,y),max(x,y))]+=scale_*(1 if x<y else -1)
        return {k:v for k,v in out.items() if v}
    def check_matching(vertices):
        for tri in combinations(vertices,3):
            used=set().union(*(set(edges[v]) for v in tri))
            if len(used)!=6:continue
            h_=next((v for v in vertices if v not in tri),None);assert h_ is not None
            a_,b_,c_=tri;fill=[(1,(a_,b_,h_)),(1,(b_,c_,h_)),(1,(c_,a_,h_))]
            assert all(len(set().union(*(set(edges[v]) for v in t)))<=5 for _,t in fill)
            assert chain_boundary(fill)==chain_boundary([(1,tri)])
    tables=[];union=set();matching_count=0
    for gap in range(7):
        pats=[pattern(gap,s) for s in range(64)];single=set(pats);double={x&y for x in single for y in single}
        assert len(single)==58 and len(double)==180
        assert all((x&y) in double for x in double for y in single)
        for s0 in range(64):
            for s1 in range(64):
                for s2 in range(64):
                    synth=s0^((s0^s1)|(s0^s2))
                    assert pats[s0]&pats[s1]&pats[s2]==pats[s0]&pats[synth]
        count=0
        for mask in double:
            vertices=[k for k in range(15) if mask&(1<<k)];check_matching(vertices)
            count+=sum(len(set().union(*(set(edges[k]) for k in tri)))==6 for tri in combinations(vertices,3))
        assert count==15;matching_count+=count;union|=double;tables.append([gap,len(single),len(double),count])
    assert len(union)==487 and matching_count==105
    ss=(8,25,26);pats=[pattern(0,s) for s in ss];inter=pats[0]&pats[1]&pats[2]
    assert pats==[580,1728,1549] and inter==512
    assert all((x&y)!=inter for x,y in combinations(pats,2)) and pattern(0,8)&pattern(0,27)==inter
    # Direct rational parent; original normal pencil attachment.
    pt=list(map(Q,['-1211/27','-26','-32','28','-15','6','-19','-2','-10']))
    assert all(value(p,pt)!=0 for p in brackets.values())
    mv=[[value(p,pt) for p in row] for row in matrix]
    triples=sorted(combinations(range(8),3),key=lambda t:t[::-1])
    normals={j:[(-1)**r*detq([[mv[k][col] for col in tri] for k in range(4) if k!=r]) for r in range(4)] for j,tri in enumerate(triples)}
    core=(9,55);order=(0,4,10,35,1,20)
    assert tuple(triples[j] for j in core)==((2,3,4),(5,6,7))
    assert all(set((0,1))<=set(triples[j]) for j in order)
    assert matrix_rank([normals[j] for j in order])==2
    assert matrix_rank([normals[j] for j in core+order])==3
    circuits=[]
    for u,v in edges:
        ns=[normals[j] for j in (core[0],core[1],order[u],order[v])]
        assert matrix_rank(ns)==3
        kernel=None
        for coordrows in combinations(range(4),3):
            vec=[(-1)**col*detq([[ns[j][row] for j in range(4) if j!=col] for row in coordrows]) for col in range(4)]
            if any(vec):kernel=vec;break
        assert kernel is not None and all(kernel)
        assert all(sum(kernel[j]*ns[j][row] for j in range(4))==0 for row in range(4))
        circuits.append(kernel)
    actual=set()
    for word in range(256):
        mask=0
        for k,((u,v),kernel) in enumerate(zip(edges,circuits)):
            positions=(0,1,2+u,2+v);vals=[z*(1 if (word>>p)&1 else -1) for z,p in zip(kernel,positions)]
            if all(z>0 for z in vals) or all(z<0 for z in vals):mask|=1<<k
        actual.add(mask)
    assert actual=={pattern(1,s) for s in range(64)}
    matching=[edges.index(x) for x in [(0,1),(2,3),(4,5)]]
    canaries['pair_matching_only_unfilled_cycle']=reject(lambda:check_matching(matching))
    target=chain_boundary([(1,(0,1,2))]);wrong=chain_boundary([(1,(0,1,3)),(-1,(1,2,3)),(1,(2,0,3))])
    canaries['pair_signed_filler_reversal']=reject(lambda:assert_eq(target,wrong))
    canaries['synthetic_pair_must_not_be_original']=reject(lambda:assert_eq(any(x&y==inter for x,y in combinations(pats,2)),True))
    ps=js('ops/team/d3-real-pair-prover/ARITHMETIC_REPLAY.json')['scope']
    expected_scope={'generic_supported_factor_only':True,'rank_two_pencil_required':True,'arbitrary_signings':True,'global_pair_map_proved':False,'source_orbits_removed':0,'diagonals_proved':2}
    assert ps==expected_scope
    canaries['pair_remove_genericity']=reject(lambda:assert_eq(dict(ps,generic_supported_factor_only=False),expected_scope))
    canaries['pair_promote_original_map']=reject(lambda:assert_eq(dict(ps,global_pair_map_proved=True),expected_scope))
    numerical=js('ops/team/d3-real-global-prover/CRITICAL_NUMERICAL_DISCOVERY.json')
    records=numerical['records'];assert len(records)==numerical['trials']==120
    assert sum(r['success'] for r in records)==32
    assert sum(r['residual']<1e-6 for r in records)==70
    assert sum(r['residual']<1e-6 and r['minimum_parent_bracket_absolute']>1e-5 for r in records)==0
    # These are descriptive recorded floating-point counts only.
    # Pin every reviewed candidate and inherited scope file. No producer runs.
    prefixes=['ops/team/d3-real-oval-falsifier/','ops/team/d3-real-pair-prover/','ops/team/d3-real-global-prover/','ops/research-team/cycles/2026-09-05-real-fiber/']
    paths=subprocess.check_output(['git','ls-tree','-r','--name-only',REV,'--',*prefixes],cwd=args.repo,text=True).splitlines()
    for p in paths:read(p)
    for p in ['ai/omreal/9DVL_THEOREM_PROSPECTUS.md','ai/omreal/DIAG3_PAIR_FACTOR_ROOT_SWITCH.md','ai/omreal/DIAG3_PAIR_DIFFERENTIAL_ENDS.md','ai/omreal/data/CANONICAL_RESEARCH_STATE_V11.json','ai/omreal/data/DIAG3_RESEARCH_DECISION_LEDGER.json','ops/research-team/PROTOCOL.md','ops/team/ai-d3-reset-referee/REVIEW.md','ops/team/ai-d3-reset-coordinator/ACCEPTANCE.md']:read(p)
    for p,digest in js('ops/team/d3-real-pair-prover/SOURCE_MANIFEST.json')['sources'].items():read(p);assert pins[p]==digest
    opening=js('ops/research-team/cycles/2026-09-05-real-fiber/OPENING_STATE.json')
    for p,digest in opening['source_hashes'].items():read(p);assert pins[p]==digest
    for p in ['ai/omreal/data/CANONICAL_RESEARCH_STATE_V11.json','ai/omreal/data/DIAG3_RESEARCH_DECISION_LEDGER.json',SOURCE]:
        old=subprocess.check_output(['git','show','cefc495b27247c4a76f88bce04978422161f7ce9:'+p],cwd=args.repo)
        assert old==read(p)
    state=js('ai/omreal/data/CANONICAL_RESEARCH_STATE_V11.json')['open_obligations']
    ledger=js('ai/omreal/data/DIAG3_RESEARCH_DECISION_LEDGER.json')['invariant_obligations'][0]
    assert (state['triple_source_settled'],state['triple_source_residual'],state['triple_source_total'])==(77940147,1162302,79102449)
    assert (ledger['proved_noncompact_count'],ledger['unresolved_count'],ledger['universe_count'])==(77940147,1162302,79102449)
    assert 77940147+1162302==79102449
    previous=read('ops/research-team/cycles/2026-09-05-ai-only-d3-structural-reset/CYCLE_REPORT.md').decode()
    assert '(2/9,1,{pair Hc1,triple Hc0},7,UNKNOWN,UNKNOWN,10,13)' in previous
    prior_accept=js('ops/team/ai-d3-rank-pencil-referee/RESULT.json')
    assert prior_accept['research_credit']['theorem_delta']==0 and prior_accept['governance']['successor_route_opened'] is False
    result={'reviewed_revision':REV,'verdict':'ACCEPT_SCOPED_AUXILIARY_CLAIMS_AND_NULL_CLOSURE','dependency':'Python standard library plus this referee audit_cefc495.py','oval':{'source_equivalence':True,'brackets_checked':70,'resultants_recomputed':71,'all_resultant_closed_interval_roots':0,'largest_resultant_degree':maxresdeg,'root_intervals':cert['W_root_intervals'],'anchor_signs':outsign,'compact_fixed_base_oval':True,'compact_full_source_component':'NOT_PROVED','admissible_signature_triple':'NOT_PROVED'},'hessian':{'columns':28,'support_equations':1191,'selected_determinant':str(hdet),'constant_symmetric_kernel_dimension':0},'pair':{'gap_tables':tables,'matching_fillers':105,'union_masks':487,'ternary_inputs_checked':7*64**3,'arbitrary_finite_extension':'deductive bitwise identity; see FINAL_REVIEW.md','actual_parent_normals_verified':True,'global_alternating_map':'NOT_PROVED'},'hostile_controls':canaries,'original_obligations_closed':0,'score':'2/9','classification':'STALLED','source_counts':{'settled':77940147,'unresolved':1162302,'total':79102449},'accepted_current_streaks':{'same_blocker':11,'zero_ledger':14},'accepted_file_sha256':dict(sorted(pins.items()))}
    out=Path(__file__).resolve().parent/'FINAL_ARITHMETIC.json';out.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    print(json.dumps({k:v for k,v in result.items() if k!='accepted_file_sha256'},indent=2,sort_keys=True))

def assert_nonzero(x):assert x!=0

def matrix_rank(m):
    a=[list(map(Q,row)) for row in m];r=0
    for j in range(len(a[0])):
        k=next((k for k in range(r,len(a)) if a[k][j]),None)
        if k is None:continue
        a[k],a[r]=a[r],a[k];pv=a[r][j];a[r]=[v/pv for v in a[r]]
        for k in range(r+1,len(a)):
            t=a[k][j];a[k]=[v-t*w for v,w in zip(a[k],a[r])]
        r+=1
        if r==len(a):break
    return r

if __name__=='__main__':main()
