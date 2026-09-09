#!/usr/bin/env python3
"""Independent exact audit; imports no producer or repository checker.

NumPy is used only to decode the immutable NPZ input. All mathematics uses
Python integers and Fraction. The written review, not finite fixtures, proves
the universal formal lemma and scopes the local geometric exclusion.
"""
import argparse
from fractions import Fraction
from hashlib import sha256
from itertools import combinations, permutations, product
import json
from math import gcd
from pathlib import Path
import subprocess
import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
BASE = '730fd6c7b6c2c3e8cbbf94ab4da3bc97ba53f095'
TREE = 'dbe7645743d09758eb3403272908ac3dcf88bf65'
SIGS = (14988895318912, 3405195891438080, 40418075143643136)
SUPPORTS = ((0,19,21,37,38),(0,9,27,30,35),(0,11,17,24,40))
# Colexicographic index convention is source data, not inferred from lex order.
TRIPLES = [(a,b,c) for c in range(3,9) for b in range(2,c) for a in range(1,b)]
TINDEX = {x:i for i,x in enumerate(TRIPLES)}
BASES = list(combinations(range(1,9),4))

def check(value, message):
    if not value:
        raise AssertionError(message)

def sign(x):
    return (x > 0)-(x < 0)

def parity(seq):
    return (-1)**sum(seq[i]>seq[j] for i in range(len(seq)) for j in range(i+1,len(seq)))

def determinant(a):
    # Leibniz formula is independent of the producer's recursive minors.
    n = len(a)
    out = 0
    for p in permutations(range(n)):
        term = parity(p)
        for i in range(n):
            term *= int(a[i][p[i]])
        out += term
    return out

def rank_columns(columns, ambient):
    if not columns:
        return 0
    a = [[Fraction(col[i]) for col in columns] for i in range(ambient)]
    row = 0
    for col in range(len(columns)):
        pivot = next((i for i in range(row,ambient) if a[i][col]),None)
        if pivot is None:
            continue
        a[row],a[pivot]=a[pivot],a[row]
        scale=a[row][col]
        a[row]=[x/scale for x in a[row]]
        for i in range(row+1,ambient):
            scale=a[i][col]
            a[i]=[x-scale*y for x,y in zip(a[i],a[row])]
        row += 1
        if row==ambient:
            break
    return row

def brackets(p):
    return {b:determinant([[p[r][c-1] for c in b] for r in range(4)]) for b in BASES}

def normals(p, primitive=False):
    out=[]
    for t in TRIPLES:
        # Coefficient of x_h in det(Y_a,Y_b,Y_c,x), evaluated at x=e_h.
        v=[determinant([[p[r][c-1] for c in t]+[int(r==h)] for r in range(4)]) for h in range(4)]
        if primitive:
            g=gcd(*v)
            v=[x//g for x in v]
        out.append(v)
    return out

def signed(normals_,sig):
    return [[(1 if sig & (1<<i) else -1)*x for x in row] for i,row in enumerate(normals_)]

def check_positive_relation(a,support,weights):
    check(len(set(support))==len(support)==len(weights),'support format')
    check(all(x>0 for x in weights),'strict positive relation')
    check(all(sum(weights[j]*a[k][r] for j,k in enumerate(support))==0 for r in range(4)),'relation equality')

def maximal_circuit(a,support):
    columns=[a[i] for i in support]
    weights=[(-1)**j*determinant([columns[k] for k in range(5) if k!=j]) for j in range(5)]
    check(len(set(map(sign,weights)))==1 and weights[0]!=0,'rank four positive five-circuit')
    weights=[abs(x) for x in weights]
    check_positive_relation(a,support,weights)
    return weights

def verify_gp(parent,sig):
    chi0={k:sign(v) for k,v in brackets(parent).items()}
    def chi(seq):
        key=tuple(sorted(seq))
        if 9 in key:
            value=1 if sig & (1<<TINDEX[key[:3]]) else -1
        else:
            value=chi0[key]
        return parity(seq)*value
    total=0
    for common in combinations(range(1,10),2):
        for a,b,c,d in combinations([v for v in range(1,10) if v not in common],4):
            values=(chi(common+(a,b))*chi(common+(c,d)),
                    -chi(common+(a,c))*chi(common+(b,d)),
                    chi(common+(a,d))*chi(common+(b,c)))
            check(min(values)==-1 and max(values)==1,'uniform GP axiom')
            total+=1
    return total

def finite_linear_controls():
    # Quotient by the two incident image spaces is the formal model for tau_i.
    vectors=((0,0,0),(1,0,0),(0,1,0),(0,0,1),(1,1,0),(0,1,1),(1,1,1))
    examples=positive=0
    for cols in product(vectors,repeat=3):
        full=rank_columns(cols,3)==3
        opposite_injective=[]
        for k in range(3):
            other=[cols[j] for j in range(3) if j!=k]
            opposite_injective.append(rank_columns(other+[cols[k]],3)==rank_columns(other,3)+1)
        check(full==all(opposite_injective),'canonical quotient detector equivalence')
        positive+=int(full)
        examples+=1
    # Three individually nonzero, pairwise independent lines can still sum dependently.
    dependent=((1,0),(0,1),(1,1))
    check(all(rank_columns([dependent[i],dependent[j]],2)==2 for i,j in combinations(range(3),2)),'pairwise fixture')
    check(rank_columns(dependent,2)==2,'three-image dependence survives')
    check(rank_columns([(1,),(-1,),(1,)],1)==1,'actual stalk rank')
    return {'finite_quotient_fixtures':examples,'injective_fixtures':positive,
            'pairwise_independence_countercontrol':True,'stalk_kernel_rank':2}

def selected_plane_control(prover_root):
    old=[[t**r for t in range(8)] for r in range(4)]
    new=[row[:] for row in old]
    for r in range(4):
        new[r][0]+=new[r][1]
    check(all(v>0 for v in brackets(old).values()),'moment curve before')
    check(all(v>0 for v in brackets(new).values()),'moment curve after')
    before,after=normals(old),normals(new)
    check(all(before[TINDEX[(1,2,k)]]==after[TINDEX[(1,2,k)]] for k in range(3,9)),'six preserved planes')
    a,b,c=before[TINDEX[(1,4,5)]],after[TINDEX[(1,4,5)]],before[TINDEX[(2,4,5)]]
    check(b==[x+y for x,y in zip(a,c)] and rank_columns([a,b],4)==2,'omitted plane changes')
    recorded=json.loads((prover_root/'ops/team/d3-detector-prover/GEOMETRY_REPLAY.json').read_text())
    # The isolated plane-only producer uses the opposite uniform normal
    # convention. No signature is attached to that fixture. Compare it
    # explicitly rather than transporting signed witnesses across conventions.
    check(recorded['normal_145_before']==[-x for x in a]
          and recorded['normal_145_after']==[-x for x in b]
          and recorded['normal_245']==[-x for x in c],'independent geometry vectors')
    return {'parent_brackets_each':70,'unchanged_selected_planes':6,'omitted_normal_span_rank':2,
            'producer_normal_convention_relative_to_det_Y_x':-1,
            'admissible_signature_claim':False,'feasibility_flip_claim':False}

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--opening-root',type=Path,default=ROOT)
    parser.add_argument('--prover-root',type=Path,default=ROOT)
    parser.add_argument('--falsifier-root',type=Path,default=ROOT)
    args=parser.parse_args()
    manifest=json.loads((HERE/'REVIEWED_INPUTS.json').read_text())
    roots={'source':ROOT,'opening':args.opening_root,'prover':args.prover_root,'falsifier':args.falsifier_root}
    verified=0
    for group,files in manifest['sha256'].items():
        for name,digest in files.items():
            check(sha256((roots[group]/name).read_bytes()).hexdigest()==digest,'hash '+group+':'+name)
            verified+=1
    tree=subprocess.check_output(['git','rev-parse',BASE+'^{tree}'],cwd=ROOT,text=True).strip()
    check(tree==TREE,'immutable base tree')
    closing=json.loads((ROOT/'ops/research-team/cycles/2026-09-05-real-fiber/CLOSING_STATE.json').read_text())
    check(closing['ledger']=='2/9' and closing['closing_proof_distance'][-2:]==[11,14],'accepted inherited close')
    with np.load(ROOT/'ai/omreal/data/seeat_parent2599_upper178.npz',allow_pickle=False) as data:
        parent=data['chart_matrix'][0].astype(object).tolist()
        base_signs={k:sign(v) for k,v in brackets(parent).items()}
        check(len(base_signs)==70 and all(base_signs.values()),'70 nonzero parent brackets')
        producer=json.loads((args.falsifier_root/'ops/team/d3-detector-falsifier/ARITHMETIC_REPLAY.json').read_text())
        check(parent==producer['parent'],'reported parent equals pinned source')
        raw=normals(parent)
        circuits=[]
        for block,sig in enumerate(SIGS):
            a=signed(raw,sig)
            support=SUPPORTS[block]
            altered=(2,)+support[1:]
            weights=[maximal_circuit(a,s) for s in (support,altered)]
            check(weights==producer['coordinate_edges'][block]['positive_raw_cofactors'],'independent cofactor vectors')
            union=sorted(set(support)|set(altered))
            check(len(union)==6 and rank_columns([a[i]+[1] for i in union],5)==5,'positive one-face dimension')
            circuits.append({'block':block,'supports':[support,altered],'rank':4,'union_face_dimension':1})
        anchors=json.loads((ROOT/'ops/team/ai-d3-shared-pencil-falsifier/admissibility_flow.json').read_text())['records']
        noninclusions=0
        for block,rec in enumerate(anchors):
            chart=rec['upper_chart_index']; point=rec['upper_point_index']
            p=data['chart_matrix'][chart].astype(object).tolist()
            check(p==rec['parent'] and int(data['assignment'][point])==chart,'anchor binding')
            check(data['point'][point].tolist()==rec['point'],'primal point binding')
            check({k:sign(v) for k,v in brackets(p).items()}==base_signs,'same parent chirotope')
            rows=normals(p,True)
            check(rec['signature']==SIGS[block],'original extension signature')
            check(all(sum(x*y for x,y in zip(v,rec['point']))>0 for v in signed(rows,SIGS[block])),'strict feasible anchor')
            for other,system in enumerate(rec['other_systems']):
                check(system['signature']==SIGS[other],'other original label')
                if other!=block:
                    dual=system['dual']
                    check_positive_relation(signed(rows,SIGS[other]),dual['support'],dual['weights'])
                    noninclusions+=1
        check(noninclusions==6,'all ordered noninclusions')
    gp=sum(verify_gp(parent,s) for s in SIGS)
    check(gp==3780,'GP denominator')
    hostile={}
    try:
        maximal_circuit(signed(raw,SIGS[0]^(1<<SUPPORTS[0][0])),SUPPORTS[0])
    except AssertionError:
        hostile['supported_sign_flip']=True
    a=signed(raw,SIGS[0]); w=maximal_circuit(a,SUPPORTS[0]); w[0]+=1
    try:
        check_positive_relation(a,SUPPORTS[0],w)
    except AssertionError:
        hostile['positive_weight_corruption']=True
    check(len(hostile)==2,'hostile arithmetic rejection')
    result={'verdict':'ACCEPT_AUXILIARY_ONLY','producer_logic_imported':False,
            'source_and_artifact_hashes_verified':verified,'base_revision':BASE,'base_tree':tree,
            'parent_brackets':70,'gp_axioms':gp,'strict_circuits':circuits,
            'ordered_noninclusions':noninclusions,'linear_controls':finite_linear_controls(),
            'selected_plane_control':selected_plane_control(args.prover_root),
            'hostile_controls_rejected':hostile,'original_obligations_closed':0,'ledger':'2/9',
            'opening_counters':[11,14],'recommended_closing_counters':[12,15],
            'original_pair_target':'NULL','global_coverage':'UNKNOWN','pair_residual':'UNKNOWN'}
    print(json.dumps(result,indent=2))

if __name__=='__main__':
    main()
