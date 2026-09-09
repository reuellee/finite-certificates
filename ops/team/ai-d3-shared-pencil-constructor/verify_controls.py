#!/usr/bin/env python3
"""Standard-library exact checker; no LP, SymPy, or producer imports.

Reconstructs actual parent matrices from pinned NPZ arrays using a narrow
NPY integer reader, constructs colex normals and GP signs independently,
and verifies all primal/dual certificates. No search-completeness claim is
trusted: negative coverage is the explicit set of all 8*C(21,2) pairs.
"""
from ast import literal_eval
from fractions import Fraction
from itertools import combinations
from math import prod
from pathlib import Path
import hashlib
import json
import struct
import zipfile

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]
TRIPLES=tuple(sorted(combinations(range(8),3),key=lambda t:tuple(reversed(t))))
BASES=tuple(sorted(combinations(range(8),4),key=lambda t:tuple(reversed(t))))


def require(condition,message):
    if not condition:
        raise AssertionError(message)


def npy_integer_array(path,key):
    with zipfile.ZipFile(path) as archive:
        raw=archive.read(key+'.npy')
    require(raw[:6]==b'\x93NUMPY','Invalid NPY magic')
    major=raw[6]
    require(major in (1,2),'Unsupported NPY version')
    hsize=2 if major==1 else 4
    length=int.from_bytes(raw[8:8+hsize],'little')
    header=literal_eval(raw[8+hsize:8+hsize+length].decode('latin1'))
    require(not header['fortran_order'],'Fortran arrays not supported')
    require(header['descr'] in ('<i8','<u8'),'Only exact 64-bit integer arrays allowed')
    count=prod(header['shape'])
    payload=raw[8+hsize+length:]
    require(len(payload)==8*count,'NPY length mismatch')
    values=struct.unpack('<'+('q' if header['descr']=='<i8' else 'Q')*count,payload)
    return header['shape'],values


def source_matrix(path,key,index):
    shape,values=npy_integer_array(path,key)
    require(shape[1:]==(4,8),'Wrong parent array dimensions')
    start=index*32
    return [list(values[start+8*r:start+8*(r+1)]) for r in range(4)]


def det(matrix):
    if len(matrix)==1:
        return matrix[0][0]
    return sum((-1)**j*matrix[0][j]*det([row[:j]+row[j+1:] for row in matrix[1:]]) for j in range(len(matrix)))


def bracket(parent,indices):
    return det([[row[j] for j in indices] for row in parent])


def parent_signs(parent):
    values=[bracket(parent,t) for t in BASES]
    require(all(values),'Nonuniform parent')
    return tuple(1 if v>0 else -1 for v in values)


def normals(parent):
    return [tuple((-1)**(r+3)*det([[parent[q][j] for j in triple] for q in range(4) if q!=r]) for r in range(4)) for triple in TRIPLES]


def dot(a,b):
    return sum(x*y for x,y in zip(a,b))


def gp_check(parent,signature):
    chi={t:1 if bracket(parent,t)>0 else -1 for t in BASES}
    chi.update({t+(8,):1 if (signature>>i)&1 else -1 for i,t in enumerate(TRIPLES)})
    def alternating(sequence):
        sign=(-1)**sum(sequence[i]>sequence[j] for i in range(4) for j in range(i+1,4))
        return sign*chi[tuple(sorted(sequence))]
    checks=0
    for lam in combinations(range(9),2):
        rest=[i for i in range(9) if i not in lam]
        for a,b,c,d in combinations(rest,4):
            terms=(alternating(lam+(a,b))*alternating(lam+(c,d)),
                   -alternating(lam+(a,c))*alternating(lam+(b,d)),
                   alternating(lam+(a,d))*alternating(lam+(b,c)))
            require(set(terms)=={-1,1},'Invalid GP extension')
            checks+=1
    return checks


def verify_dual(rows,signature,witness,allowed=None):
    require(witness is not None,'Missing dual certificate')
    indices=witness['row_indices']; weights=witness['weights']
    require(len(indices)==len(weights) and len(indices)==len(set(indices)),'Invalid dual indexing')
    require(all(isinstance(v,int) and v>=0 for v in weights) and any(weights),'Invalid dual weights')
    require(all(0<=i<56 for i in indices),'Dual index out of range')
    if allowed is not None:
        require(set(indices)<=set(allowed),'Dual certificate uses a deleted row')
    for c in range(4):
        require(sum(w*(1 if (signature>>i)&1 else -1)*rows[i][c] for i,w in zip(indices,weights))==0,'Dual dependence is not exact')


def verify_primal(rows,signature,point,allowed):
    require(len(point)==4 and all(isinstance(x,int) for x in point),'Invalid integer primal point')
    values=[(1 if (signature>>i)&1 else -1)*dot(rows[i],point) for i in allowed]
    require(all(v>0 for v in values),'Primal inequality is not strict')
    return min(values)


def main():
    controls=json.loads((HERE/'CONTROLS.json').read_text())
    obstruction=json.loads((HERE/'OBSTRUCTION.json').read_text())
    data=ROOT/'ai/omreal/data'
    shatter=data/'seeat_parent2599_shatter8.npz'
    atlas=data/'seeat_parent2599_upper178.npz'
    expected={
        'shatter_pattern_0':source_matrix(shatter,'pattern_chart',0),
        'upper_chart_7':source_matrix(atlas,'chart_matrix',7),
        'upper_chart_0':source_matrix(atlas,'chart_matrix',0)}
    _,sig_values=npy_integer_array(shatter,'signature')
    shatter_sigs=[sig_values[i] for i in (0,4,3)]
    target_sigs=[14988895318912,3405195891438080,40418075143643136]
    common_chi=parent_signs(expected['upper_chart_0'])
    positive_count=0; gp_relations=0
    for case in controls['cases']:
        name=case['case']; parent=case['parent']
        require(parent==expected[name],'Control matrix is not its registered source point')
        require(parent_signs(parent)==common_chi,'Control parent chirotope changed')
        sigs=target_sigs if name=='upper_chart_0' else shatter_sigs
        require(case['signatures']==sigs,'Control signatures changed')
        rows=normals(parent)
        for sig in sigs:
            gp_relations+=gp_check(parent,sig)
        if name=='shatter_pattern_0':
            e=case['label_one_based']-1; pair=case['pair_row_indices']
            require(e==0 and {TRIPLES[i] for i in pair}=={(0,2,3),(0,1,6)},'Positive-control planes changed')
            allowed=[i for i,t in enumerate(TRIPLES) if e not in t or i in pair]
            for sig,witness in zip(sigs,case['restricted_witnesses']):
                verify_dual(rows,sig,witness,allowed)
                positive_count+=1
        elif name=='upper_chart_7':
            feasible=case['full_feasible_witnesses']
            require(any(v['block']==2 for v in feasible),'Ineligibility certificate missing')
            for item in feasible:
                verify_primal(rows,sigs[item['block']],item['point'],range(56))

    require(obstruction['parent']==expected['upper_chart_0'],'Obstruction is not registered chart zero')
    require(obstruction['signatures']==target_sigs,'Obstruction signatures changed')
    rows=normals(obstruction['parent'])
    for sig,witness in zip(target_sigs,obstruction['full_bad_witnesses']):
        verify_dual(rows,sig,witness)
    required={(e,tuple(pair)) for e in range(8) for pair in combinations([i for i,t in enumerate(TRIPLES) if e in t],2)}
    seen=set(); minimum_margin=None
    for record in obstruction['restricted_separators']:
        e=record['label_one_based']-1; pair=tuple(record['pair_row_indices'])
        require((e,pair) in required and (e,pair) not in seen,'Missing, duplicate, or invalid separator case')
        seen.add((e,pair))
        allowed=[i for i,t in enumerate(TRIPLES) if e not in t or i in pair]
        require(len(allowed)==37,'Wrong restricted row set')
        block=record['block']; require(block in (0,1,2),'Invalid blocking signature')
        margin=verify_primal(rows,target_sigs[block],record['point'],allowed)
        minimum_margin=margin if minimum_margin is None else min(margin,minimum_margin)
    require(seen==required and len(seen)==1680,'Incomplete negative coverage')

    ordered_incomparability=set(); feasible_blocks=set()
    for record in obstruction['assigned_feasibility_controls']:
        block=record['good_block']; parent=record['parent']; chart=record['chart_index']
        require(parent==source_matrix(atlas,'chart_matrix',chart),'Admissibility parent is not its source chart')
        require(parent_signs(parent)==common_chi,'Admissibility parent has wrong signs')
        local_rows=normals(parent)
        verify_primal(local_rows,target_sigs[block],record['point'],range(56))
        feasible_blocks.add(block)
        for other,witness in record['other_block_bad_witnesses'].items():
            other=int(other)
            if witness is not None:
                require(other!=block,'Inconsistent admissibility block')
                verify_dual(local_rows,target_sigs[other],witness)
                ordered_incomparability.add((block,other))
    require(feasible_blocks=={0,1,2},'A signature lacks a realized extension point')
    require(ordered_incomparability=={(i,j) for i in range(3) for j in range(3) if i!=j},'Incomplete incomparability bindings')
    result={'status':'PASS_EXACT_ROUTE_COUNTEREXAMPLE_CERTIFICATE',
            'acceptance':'Pending independent research review',
            'positive_control_restricted_witnesses':positive_count,
            'upper_chart_7':'INELIGIBLE_BLOCK_2_FEASIBLE',
            'gp_relations_checked':gp_relations,
            'negative_cases':len(seen),'strict_separator_inequalities':len(seen)*37,
            'minimum_integer_strict_margin':minimum_margin,
            'full_bad_witnesses':3,'realized_good_controls':3,
            'ordered_incomparability_bindings':len(ordered_incomparability),
            'properness':'All three nonempty and all bad at registered chart zero',
            'scope':'Refutes the shared-two-triple pencil predicate only; does not refute triple Hc0 or D3'}
    print(json.dumps(result,indent=2))


if __name__=='__main__':
    main()
