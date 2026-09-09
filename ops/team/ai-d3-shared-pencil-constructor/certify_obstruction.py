#!/usr/bin/env python3
"""Propose an independently checkable separator for each registered row pair.

LP and numerical scans are proposal engines only. Every saved certificate
is checked using the exact integer normals, both here and in verify_controls.py.
No active-lane data are read. Admissibility witnesses come from the already
stored upper178 assignment table, not new parent points or a new atlas.
"""
from fractions import Fraction
from itertools import combinations
from math import gcd, lcm
from pathlib import Path
import json

import numpy as np
from scipy.optimize import linprog
import search_controls as search

HERE=Path(__file__).resolve().parent
ROOT=search.ROOT
exact=search.exact
TRIPLES=exact.TRIPLES


def integer_separator(rows, signature, allowed):
    signed=[[int(v)*(1 if (signature>>i)&1 else -1) for v in rows[i]] for i in allowed]
    normalized=np.array([[v/max(map(abs,row)) for v in row] for row in signed])
    result=linprog(np.zeros(4),A_ub=-normalized,b_ub=-np.ones(len(allowed)),
                   bounds=[(None,None)]*4,method='highs')
    if not result.success:
        return None
    for limit in (10**3,10**6,10**9,10**12):
        rational=[Fraction(float(v)).limit_denominator(limit) for v in result.x]
        denominator=lcm(*(v.denominator for v in rational))
        point=[int(v*denominator) for v in rational]
        divisor=gcd(*point)
        point=[v//divisor for v in point]
        if all(sum(a*b for a,b in zip(row,point))>0 for row in signed):
            return point
    return None


def assignment_witnesses(signatures):
    atlas=np.load(ROOT/'ai/omreal/data/seeat_parent2599_upper178.npz',allow_pickle=False)
    found={}
    for chart in sorted(set(map(int,atlas['assignment']))):
        indices=np.flatnonzero(atlas['assignment']==chart)
        parent=[[int(v) for v in row] for row in atlas['chart_matrix'][chart]]
        rows=exact.derived_rows(parent,normalize=False)
        points=atlas['point'][indices]
        # Only use this floating calculation to locate candidates for exact checks.
        dots=np.asarray(points,dtype=float)@np.asarray(rows,dtype=float).T
        masks=np.sum((dots>0).astype(np.uint64)*(np.uint64(1)<<np.arange(56,dtype=np.uint64)),axis=1,dtype=np.uint64)
        for sig in signatures:
            if sig in found:
                continue
            matches=np.flatnonzero(masks==np.uint64(sig))
            for j in matches:
                p=[int(v) for v in points[j]]
                if all((1 if (sig>>i)&1 else -1)*exact.dot(row,p)>0 for i,row in enumerate(rows)):
                    found[sig]={'chart_index':chart,'parent':parent,'point':p}
                    break
        if len(found)==len(signatures):
            break
    return found


def main():
    controls=json.loads((HERE/'CONTROLS.json').read_text())
    case=next(c for c in controls['cases'] if c['case']=='upper_chart_0')
    parent=case['parent']; signatures=case['signatures']; rows=exact.derived_rows(parent,normalize=False)
    records=[]
    for e in range(8):
        star=[i for i,t in enumerate(TRIPLES) if e in t]
        for pair in combinations(star,2):
            allowed=[i for i,t in enumerate(TRIPLES) if e not in t or i in pair]
            for block,sig in enumerate(signatures):
                p=integer_separator(rows,sig,allowed)
                if p is not None:
                    records.append({'label_one_based':e+1,'pair_row_indices':list(pair),'block':block,'point':p})
                    break
            else:
                raise RuntimeError(f'No exact separator at {(e+1,pair)}; no negative conclusion')
    record={'format':'shared-pencil-obstruction-v1','case':'upper_chart_0','parent':parent,
            'signatures':signatures,'full_bad_witnesses':case['full_bad_witnesses'],
            'restricted_separators':records}
    found=assignment_witnesses(signatures)
    if len(found)!=3:
        raise RuntimeError('The assigned feasibility witnesses were not recovered')
    admissibility=[]
    for block,sig in enumerate(signatures):
        witness=found[sig]
        local_rows=exact.derived_rows(witness['parent'],normalize=False)
        bad_others={}
        for other in range(3):
            if other!=block:
                bad_others[str(other)]=search.kernel_proposal(local_rows,signatures[other],list(range(56)))
        admissibility.append({'good_block':block,**witness,'other_block_bad_witnesses':bad_others})
    record['assigned_feasibility_controls']=admissibility
    record['admissibility_note']='Assigned good points prove realizability; a missing other-block bad witness is an unresolved inclusion binding, not proof of inclusion.'
    (HERE/'OBSTRUCTION.json').write_bytes((json.dumps(record,indent=2)+'\n').encode())
    upper7=next(c for c in controls['cases'] if c['case']=='upper_chart_7')
    rows7=exact.derived_rows(upper7['parent'],normalize=False)
    eligible=[]
    for block,sig in enumerate(upper7['signatures']):
        p=integer_separator(rows7,sig,list(range(56)))
        if p is not None:
            eligible.append({'block':block,'point':p})
    upper7['full_feasible_witnesses']=eligible
    if eligible:
        upper7['status']='INELIGIBLE_SOME_SIGNATURE_FEASIBLE'
    controls_path=HERE/'CONTROLS.json'
    controls_path.write_bytes((json.dumps(controls,indent=2)+'\n').encode())
    print(json.dumps({'exact_separators':len(records),'assigned_admissibility':[
        {'good_block':a['good_block'],'chart':a['chart_index'],'bad_other_blocks':[
            k for k,v in a['other_block_bad_witnesses'].items() if v]} for a in admissibility],
        'upper_chart_7_feasible_blocks':[v['block'] for v in eligible]},indent=2),flush=True)


if __name__=='__main__':
    main()
