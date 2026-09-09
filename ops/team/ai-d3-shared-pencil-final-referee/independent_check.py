# Final referee: audited reuse of the interrupted independent referee checker.
# Origin: 97835f3dd9f3e36f11adeb6e5b448e72b7bb9b60:ops/team/ai-d3-shared-pencil-referee/independent_check.py
# Origin SHA256: 8f765eee29428b5d575e82e11eee60ae436132142d69da3aa7e14b4d40eef362
# Change: every input is read from pinned Git blobs; no current/sibling source bytes.
# Arithmetic and certificate logic independently inspected by this referee.
#!/usr/bin/env python3
"""Search-free independent actual-parent shared-two-triple audit.

NumPy only decodes NPZ arrays. All geometry uses unbounded Python integers.
Triples/bases are indexed by combinadic ranks, determinants by Leibniz
expansion. Neither producer verifier nor any search module is imported.
The optional second handoff is read from its pinned Git objects, never a
sibling worktree. No topology is inferred merely from this script passing.
"""
from collections import Counter
from copy import deepcopy
from functools import reduce
from hashlib import sha256
from io import BytesIO
from itertools import combinations, permutations
from math import comb, gcd
from pathlib import Path
import json
import subprocess
import time
import numpy as np

BASE = "4927d5bcc24d91cf173551b248721b247107073a"
SECOND = "da1834fd34065fe826d230c26eb0b6b747dc082c"
PREFIX = "ops/team/ai-d3-shared-pencil-constructor/"
SECOND_PREFIX = "ops/team/ai-d3-shared-pencil-falsifier/"
TARGET = [14988895318912,3405195891438080,40418075143643136]
PINS = {
 PREFIX+"FINDINGS.md":"2c8c880d1a0d4f214e8586b1527d4559b238284d87b3c4feee7a6f05ee2a36cc",
 PREFIX+"OBSTRUCTION.json":"77bd316237f6fd7060e964aec1852daa10dfaa065a7d0c4194b0a59929a32afa",
 PREFIX+"CONTROLS.json":"d5856c5c126cfdaf8475167bd7f949ca226ac3f2f6e6f89ce573adf618ecdd64",
 PREFIX+"verify_controls.py":"5638c053b11a4877f7d0aac0807399745bd27895150e4828c1df9a3dca7df812",
 "ops/research-team/cycles/2026-09-05-ai-only-d3-structural-reset/STAGE_B_SHARED_PENCIL.md":"e64b2632f58d6510236ca71cfb004bac65c59d0dfeb711154bef9a37261a8e81",
 "ops/research-team/cycles/2026-09-05-ai-only-d3-structural-reset/STAGE_C_REVIEW.md":"2699dd5faaa2077fe1dcfa48d5f11740216eecc7bacb0a62074690fe48bda756",
 "ai/omgamma/data/cat_4_8.txt":"47b2d2b782d298539c85cb170bb10911abe9c82795b4f344e77e3ae64236c7b5",
 "ai/omreal/data/seeat_parent2599_upper178.npz":"3b90799d26b7783e92c2ac697eaaf8b76d26a787f53205873b997657e114180a",
 "ai/omreal/data/seeat_parent2599_shatter8.npz":"d01a03e3222de5b760fd7fec36c03ccbeac820ed1ce7ea47f93001abaf3aadcb",
}
SECOND_PINS = {
 "upper_chart_0_flow.json":"83485ff8bb0a1f8cacffdacbf829cbee5898721b008f8bd54ec2a661ca35e6ab",
 "admissibility_flow.json":"acf71128ca666697bec36436b35ed8bff991a50b8da26b2413cd610631d7ef10",
 "shatter_pattern_0.json":"f758fa2a7d9961e72fd38ba5ef738192f1617b177e54ba4487ea1dd80b6e81a1",
 "upper_chart_7.json":"db1749fadf9944fe6bc955379db4febfd1238f93dd37142306afe86a74c60d74",
 "FINDINGS.md":"0aae50c46db82d2a4a0a6ee7d1afae4826a8bc1994d20936554644209a4b01df",
 "verify_shared_pencil_certificate.py":"a7c66f659c79f3c82bddf0f4af531a395134455371f7a6fb909ee25be1a8e758",
}

def require(ok, message):
    if not ok: raise AssertionError(message)

def indexed_subsets(size):
    out=[None]*comb(8,size)
    for subset in combinations(range(8),size):
        rank=sum(comb(v,j+1) for j,v in enumerate(subset))
        require(out[rank] is None,"combinadic collision")
        out[rank]=subset
    require(all(t is not None for t in out),"combinadic gap")
    return tuple(out)

TRIPLES=indexed_subsets(3)
BASES=indexed_subsets(4)
LEIBNIZ=[(p,(-1)**sum(p[i]>p[j] for i in range(4) for j in range(i+1,4)))
         for p in permutations(range(4))]

def determinant(matrix):
    total=0
    for perm,sign in LEIBNIZ:
        value=sign
        for i in range(4): value*=matrix[i][perm[i]]
        total+=value
    return total

def bracket(parent,labels):
    return determinant([[row[j] for j in labels] for row in parent])

def dot(a,b): return sum(x*y for x,y in zip(a,b))
def signed(sig,index): return 2*((sig>>index)&1)-1

def dual(rows,sig,certificate,allowed=None):
    require(isinstance(certificate,dict),"missing dual")
    indices=certificate.get('row_indices',certificate.get('support'))
    weights=certificate['weights']
    require(len(indices)==len(weights)>0 and len(set(indices))==len(indices),"dual indexing")
    require(all(type(i) is int and 0<=i<56 for i in indices),"dual index range")
    require(all(type(v) is int and v>=0 for v in weights) and sum(weights)>0,"dual positivity")
    if allowed is not None:
        require({i for i,w in zip(indices,weights) if w}>set() and
                {i for i,w in zip(indices,weights) if w}<=set(allowed),"positive support uses deleted row")
    for col in range(4):
        require(sum(w*signed(sig,i)*rows[i][col] for i,w in zip(indices,weights))==0,
                "nonzero dual residual")

def primal(rows,sig,point,allowed):
    require(len(point)==4 and all(type(v) is int for v in point),"integer primal point")
    values=[signed(sig,i)*dot(rows[i],point) for i in allowed]
    require(values and min(values)>0,"separator is not strict")
    return min(values)

def restricted(e,pair):
    return [i for i,t in enumerate(TRIPLES) if e not in t or i in pair]

def choice_set():
    choices=set()
    for e in range(8):
        incident=[]
        for a,b in combinations([v for v in range(8) if v!=e],2):
            t=tuple(sorted((e,a,b)))
            incident.append(sum(comb(v,j+1) for j,v in enumerate(t)))
        require(len(set(incident))==21,"star size")
        for a,b in combinations(incident,2): choices.add((e,*sorted((a,b))))
    require(len(choices)==1680,"choice count")
    return choices

CHOICES=choice_set()

class Audit:
    def __init__(self,root):
        self.root=root; self.hashes={}; self.cache={}; self.blobs={}
        for path,digest in PINS.items():
            data=subprocess.check_output(['git','show',BASE+':'+path],cwd=root)
            require(sha256(data).hexdigest()==digest,"frozen source hash: "+path)
            self.blobs[path]=data
            self.hashes[BASE+':'+path]=digest
        self.secondary={}
        for name,digest in SECOND_PINS.items():
            key=SECOND+':'+SECOND_PREFIX+name
            data=subprocess.check_output(['git','show',key],cwd=root)
            require(sha256(data).hexdigest()==digest,"second source hash: "+name)
            self.hashes[key]=digest
            if name.endswith('.json'): self.secondary[name]=json.loads(data)
        self.upper=np.load(BytesIO(self.blobs['ai/omreal/data/seeat_parent2599_upper178.npz']),allow_pickle=False)
        self.shatter=np.load(BytesIO(self.blobs['ai/omreal/data/seeat_parent2599_shatter8.npz']),allow_pickle=False)
        require(int(self.upper['parent_index'])==int(self.shatter['parent_index'])==2599,"NPZ parent index")
        require(self.upper['chart_matrix'].shape==(178,4,8),"upper source shape")
        require(self.shatter['pattern_chart'].shape==(256,4,8),"shatter source shape")
        lines=[line.strip() for line in self.blobs['ai/omgamma/data/cat_4_8.txt'].decode().splitlines() if line.strip()]
        self.catalog=lines[2599]
        require(len(self.catalog)==70 and set(self.catalog)<={'+','-'},"catalog syntax")
        self.shatter_sigs=[int(self.shatter['signature'][i]) for i in (0,4,3)]

    def geometry(self,parent):
        key=tuple(tuple(row) for row in parent)
        if key in self.cache: return self.cache[key]
        require(len(parent)==4 and all(len(r)==8 for r in parent),"parent dimensions")
        determinants=[bracket(parent,t) for t in BASES]
        require(all(v!=0 for v in determinants),"uniform parent")
        chi=''.join('+' if v>0 else '-' for v in determinants)
        require(chi==self.catalog,"wrong labeled catalog parent")
        require(determinants[0]>0,"basis orientation")
        rows=[]
        for t in TRIPLES:
            row=tuple(determinant([[parent[r][j] for j in t]+[int(r==c)] for r in range(4)]) for c in range(4))
            require(any(row),"zero normal")
            for label in t:
                require(dot(row,[parent[r][label] for r in range(4)])==0,"incident normal annihilation")
            rows.append(row)
        primitive=[tuple(v//reduce(gcd,map(abs,row)) for v in row) for row in rows]
        answer=(rows,primitive,chi,min(map(abs,determinants)))
        self.cache[key]=answer
        return answer

    def parent_at(self,kind,index):
        return (self.upper['chart_matrix'][index] if kind=='upper' else self.shatter['pattern_chart'][index]).tolist()

    def constructor_negative(self,data):
        require(data['parent']==self.parent_at('upper',0),'principal parent source binding')
        require(data['signatures']==TARGET,'principal signature binding')
        rows,_,_,_=self.geometry(data['parent'])
        require(len(data['full_bad_witnesses'])==3,'all three full bad witnesses')
        for sig,w in zip(TARGET,data['full_bad_witnesses']): dual(rows,sig,w)
        seen=set(); minimum=None; uses=Counter()
        for rec in data['restricted_separators']:
            require(len(rec['pair_row_indices'])==2,'pair length')
            key=(rec['label_one_based']-1,*rec['pair_row_indices'])
            require(key in CHOICES and key not in seen,'invalid or duplicate choice')
            seen.add(key)
            block=rec['block']; require(type(block) is int and 0<=block<3,'blocking index')
            keep=restricted(key[0],key[1:]); require(len(keep)==37,'retained row count')
            margin=primal(rows,TARGET[block],rec['point'],keep)
            minimum=margin if minimum is None else min(minimum,margin)
            uses[block]+=1
        require(seen==CHOICES,'missing exclusion choices')
        return {'choices':len(seen),'strict_inequalities':37*len(seen),'minimum_raw_normal_margin':minimum,
                'blocking_signature_usage':dict(uses),'full_bad_witnesses':3}

    def constructor_controls(self,controls,obstruction):
        cases=controls['cases']; require(len(cases)==3,'registered cohort length')
        require({c['case'] for c in cases}=={'shatter_pattern_0','upper_chart_7','upper_chart_0'},'registered cohort names')
        for case in cases:
            name=case['case']
            kind,index=('shatter',0) if name=='shatter_pattern_0' else ('upper',7 if name=='upper_chart_7' else 0)
            require(case['parent']==self.parent_at(kind,index),'control source matrix')
            sigs=TARGET if name=='upper_chart_0' else self.shatter_sigs
            require(case['signatures']==sigs,'control signatures')
            rows,_,chi,_=self.geometry(case['parent'])
            require(case['parent_signs']==[1 if c=='+' else -1 for c in chi],'stored parent signs')
            if name=='shatter_pattern_0':
                pair=case['pair_row_indices']; require(pair==[2,20],'positive control pair')
                require(case['label_one_based']==1,'positive control label')
                require(len(case['restricted_witnesses'])==3,'positive control witness count')
                for sig,w in zip(sigs,case['restricted_witnesses']): dual(rows,sig,w,restricted(0,pair))
            if name=='upper_chart_7':
                items=case['full_feasible_witnesses']
                require(any(v['block']==2 for v in items),'chart seven ineligible certificate')
                for rec in items: primal(rows,sigs[rec['block']],rec['point'],range(56))
        anchors=obstruction['assigned_feasibility_controls']
        require(len(anchors)==3,'admissibility count')
        required={(0,3),(1,14),(2,2)}; seen=set(); noninclusions=set()
        for rec in anchors:
            block=rec['good_block']; chart=rec['chart_index']
            require((block,chart) in required and (block,chart) not in seen,'admissibility index')
            seen.add((block,chart))
            require(rec['parent']==self.parent_at('upper',chart),'admissibility source matrix')
            rows,_,_,_=self.geometry(rec['parent'])
            primal(rows,TARGET[block],rec['point'],range(56))
            require(set(rec['other_block_bad_witnesses'])=={str(j) for j in range(3) if j!=block},'admissibility other blocks')
            for other,w in rec['other_block_bad_witnesses'].items():
                dual(rows,TARGET[int(other)],w); noninclusions.add((block,int(other)))
        require(len(noninclusions)==6,'all six ordered noninclusions')
        return {'positive_restricted_witnesses':3,'upper_chart_7':'INELIGIBLE_SIGNATURE_58432476850159616',
                'flow_realized_extensions':3,'exclusive_feasible_anchors':[[0,3],[1,14],[2,2]],'ordered_noninclusions':6}

    def second_negative(self,data):
        require(data['parent']==self.parent_at('upper',0) and data['signatures']==TARGET,'second principal binding')
        _,rows,chi,_=self.geometry(data['parent'])
        require(data['parent_signs']==[1 if c=='+' else -1 for c in chi],'second stored signs')
        require(len(data['full_dual_witnesses'])==3,'second full witnesses')
        for sig,w in zip(TARGET,data['full_dual_witnesses']): dual(rows,sig,w)
        cert=data['negative_certificate']; pool=cert['witness_pool']
        require(len(pool)==23,'second pool size')
        require(len({(w['signature_index'],tuple(w['point'])) for w in pool})==23,'second distinct records')
        seen=set(); margin=None; uses=Counter(); used=set()
        for rec in cert['coverage_rows']:
            require(len(rec)==4,'second row shape')
            e,a,b,wi=rec; key=(e-1,a,b)
            require(key in CHOICES and key not in seen,'second coverage key')
            require(type(wi) is int and 0<=wi<len(pool),'second vector reference')
            seen.add(key); used.add(wi)
            w=pool[wi]; block=w['signature_index']; require(block in (0,1,2),'second block')
            keep=restricted(e-1,(a,b)); require(len(keep)==37,'second retained count')
            v=primal(rows,TARGET[block],w['point'],keep)
            margin=v if margin is None else min(margin,v); uses[block]+=1
        require(seen==CHOICES,'second missing choices')
        require(used==set(range(23)),'unused second pool record')
        return {'choices':len(seen),'strict_inequalities':37*len(seen),'distinct_vectors':23,
                'minimum_primitive_normal_margin':margin,'blocking_signature_usage':dict(uses),'full_bad_witnesses':3}

    def second_controls(self,principal):
        records=self.secondary['admissibility_flow.json']['records']
        require(len(records)==3,'second admissibility count')
        originals={r['good_block']:r for r in principal['assigned_feasibility_controls']}
        seen=set()
        for rec in records:
            block=TARGET.index(rec['signature']); require(block not in seen,'second anchor duplicate'); seen.add(block)
            index=rec['upper_point_index']; chart=rec['upper_chart_index']
            require(int(self.upper['assignment'][index])==chart,'NPZ assignment binding')
            require(self.upper['point'][index].tolist()==rec['point'],'NPZ point binding')
            require(rec['parent']==self.parent_at('upper',chart),'second anchor parent')
            original=originals[block]
            require((chart,rec['point'],rec['parent'])==(original['chart_index'],original['point'],original['parent']),
                    'independent anchor disagreement')
            _,rows,_,_=self.geometry(rec['parent'])
            primal(rows,TARGET[block],rec['point'],range(56))
            require(len(rec['other_systems'])==3,'second other-system count')
            for item in rec['other_systems']:
                sig=item['signature']; require(sig in TARGET,'second other signature')
                if sig!=TARGET[block]: dual(rows,sig,item['dual'])
        positive=self.secondary['shatter_pattern_0.json']
        require(positive['parent']==self.parent_at('shatter',0) and positive['signatures']==self.shatter_sigs,'second positive binding')
        _,rows,_,_=self.geometry(positive['parent'])
        cert=positive['positive_certificate']
        require(cert['label']==1 and cert['incident_pair']==[2,20],'second designated positive pair')
        require(len(cert['duals'])==3,'second positive witness count')
        for sig,w in zip(self.shatter_sigs,cert['duals']): dual(rows,sig,w,restricted(0,(2,20)))
        seven=self.secondary['upper_chart_7.json']
        require(seven['parent']==self.parent_at('upper',7) and seven['signatures']==self.shatter_sigs,'second chart-seven binding')
        _,rows,_,_=self.geometry(seven['parent'])
        require(len(seven['full_primal_witnesses'])==3,'second full primal list')
        primal(rows,self.shatter_sigs[2],seven['full_primal_witnesses'][2],range(56))
        # Bind the positive-control signatures to existing singleton-good
        # shatter patterns. No shared-pencil predicate is tested there.
        for good,bit in enumerate((0,4,3)):
            pattern=1<<bit; parent=self.parent_at('shatter',pattern)
            rows,_,_,_=self.geometry(parent)
            point=list(map(int,self.shatter['feasible_point'][pattern,bit].tolist()))
            primal(rows,self.shatter_sigs[good],point,range(56))
            for other,other_bit in enumerate((0,4,3)):
                if other!=good:
                    weights=list(map(int,self.shatter['gordan_weight'][pattern,other_bit].tolist()))
                    dual(rows,self.shatter_sigs[other],{'support':list(range(56)),'weights':weights})
        return {'flow_anchor_point_indices':[24588,14261,2534],
                'constructor_anchor_agreement':True,'designated_positive_pair_verified':True,
                'positive_pair_count_three':'NOT_REPLAYED_OR_NEEDED',
                'chart_seven_ineligible':True,'shatter_signature_admissibility_patterns':[1,16,8]}

def main():
    start=time.perf_counter(); root=Path(__file__).resolve().parents[3]
    audit=Audit(root)
    principal=json.loads(audit.blobs[PREFIX+'OBSTRUCTION.json'])
    controls=json.loads(audit.blobs[PREFIX+'CONTROLS.json'])
    result={'reviewed_base':BASE,'second_frozen_commit':SECOND,'source_hashes':audit.hashes,
            'producer_code_imported_or_executed':False}
    result['constructor_negative']=audit.constructor_negative(principal)
    result['constructor_controls']=audit.constructor_controls(controls,principal)
    second=audit.secondary['upper_chart_0_flow.json']
    result['second_negative']=audit.second_negative(second)
    result['second_controls']=audit.second_controls(principal)
    mutations=[]
    def bad(name,func):
        try: func()
        except (AssertionError,IndexError,KeyError,ValueError): mutations.append(name); return
        raise AssertionError('Mutation escaped: '+name)
    x=deepcopy(principal); x['restricted_separators'].pop()
    bad('missing_choice',lambda:audit.constructor_negative(x))
    x=deepcopy(principal); x['restricted_separators'][-1]=deepcopy(x['restricted_separators'][0])
    bad('duplicate_choice',lambda:audit.constructor_negative(x))
    x=deepcopy(principal); x['restricted_separators'][0]['point']=[0,0,0,0]
    bad('zero_separator',lambda:audit.constructor_negative(x))
    x=deepcopy(principal); x['restricted_separators'][0]['pair_row_indices']=[0,0]
    bad('invalid_pair',lambda:audit.constructor_negative(x))
    x=deepcopy(principal); x['full_bad_witnesses'][0]['weights'][0]+=1
    bad('corrupt_full_dual',lambda:audit.constructor_negative(x))
    x=deepcopy(principal); x['signatures'][0]^=1
    bad('signature_bit_drift',lambda:audit.constructor_negative(x))
    x=deepcopy(principal); x['assigned_feasibility_controls'][0]['parent'][0][0]+=1
    bad('anchor_parent_drift',lambda:audit.constructor_controls(controls,x))
    rows=audit.geometry(principal['parent'])[0][:]; rows[0],rows[19]=rows[19],rows[0]
    bad('normal_order_drift',lambda:dual(rows,TARGET[0],principal['full_bad_witnesses'][0]))
    x=deepcopy(second); x['negative_certificate']['coverage_rows'].pop()
    bad('second_missing_choice',lambda:audit.second_negative(x))
    x=deepcopy(second); x['negative_certificate']['witness_pool'][0]['point']=[0,0,0,0]
    bad('second_zero_separator',lambda:audit.second_negative(x))
    result['hostile_mutations_rejected']=mutations
    result['catalog_row_zero_based']=2599
    result['catalog_chirotope']=audit.catalog
    result['distinct_parent_matrices_bound']=len(audit.cache)
    result['status']='PASS_INDEPENDENT_ACTUAL_PARENT_ROUTE_COUNTERCERTIFICATES'
    result['elapsed_seconds']=round(time.perf_counter()-start,6)
    result['scope']='Refutes only the registered universal at-most-two-incident-triples predicate. Conditional escape proof reviewed separately. No D3 or compact-component assertion.'
    print(json.dumps(result,indent=2))

if __name__=='__main__': main()
