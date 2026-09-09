#!/usr/bin/env python3
"""Find exact positive controls in the three preregistered point cases.

Floating LP is only a proposal engine. Every accepted kernel vector is
reconstructed over Q and checked against the integer actual-parent normals.
No negative result is inferred from solver failure or an unsuccessful search.
The separate verifier does not use an LP solver.
"""
from fractions import Fraction
from itertools import combinations
from math import gcd, lcm
from pathlib import Path
import json
import sys

import numpy as np
from scipy.optimize import linprog
import sympy as sp

ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / 'ai/omreal'))
import DIAG9_GRAPH_exact_topes as exact

TRIPLES = exact.TRIPLES


def primitive_positive(values):
    denominator = lcm(*(Fraction(v).denominator for v in values))
    ints = [int(Fraction(v) * denominator) for v in values]
    divisor = gcd(*ints)
    if divisor:
        ints = [v // divisor for v in ints]
    if all(v < 0 for v in ints):
        ints = [-v for v in ints]
    return ints if any(ints) and all(v >= 0 for v in ints) else None


def kernel_proposal(rows, signature, allowed):
    signed = [[int(v) * (1 if (signature >> i) & 1 else -1) for v in rows[i]] for i in allowed]
    scales = [max(map(abs,row)) for row in signed]
    matrix = np.array([[v / scale for v in row] for row,scale in zip(signed,scales)]).T
    problem = linprog(np.zeros(len(allowed)), A_eq=np.vstack([matrix,np.ones(len(allowed))]),
                      b_eq=np.array([0,0,0,0,1]),bounds=(0,None),method='highs')
    if not problem.success:
        return None
    for threshold in (1e-8,1e-11,0):
        support = [j for j,v in enumerate(problem.x) if v > threshold]
        if not support or len(support)>8:
            continue
        actual = sp.Matrix([signed[j] for j in support]).T
        basis = actual.nullspace()
        if len(basis)!=1:
            continue
        weights = primitive_positive(basis[0])
        if weights is None:
            continue
        if actual * sp.Matrix(weights) != sp.zeros(4,1):
            raise AssertionError('Exact reconstruction failed')
        return {'row_indices':[allowed[j] for j in support], 'weights':weights}
    return None


def run():
    shatter=np.load(ROOT/'ai/omreal/data/seeat_parent2599_shatter8.npz',allow_pickle=False)
    atlas=np.load(ROOT/'ai/omreal/data/seeat_parent2599_upper178.npz',allow_pickle=False)
    first_sigs=[int(shatter['signature'][i]) for i in (0,4,3)]
    cases=[('shatter_pattern_0',shatter['pattern_chart'][0],first_sigs),
           ('upper_chart_7',atlas['chart_matrix'][7],first_sigs),
           ('upper_chart_0',atlas['chart_matrix'][0],[14988895318912,3405195891438080,40418075143643136])]
    answer=[]
    for name,parent_array,sigs in cases:
        parent=[[int(v) for v in row] for row in parent_array]
        signs=exact.parent_signs(parent)
        rows=exact.derived_rows(parent,normalize=False)
        full=[kernel_proposal(rows,sig,list(range(56))) for sig in sigs]
        record={'case':name,'parent':parent,'parent_signs':list(signs),'signatures':sigs,
                'full_bad_witnesses':full}
        if not all(full):
            record['status']='UNRESOLVED_ELIGIBILITY_NO_EXACT_BAD_CERTIFICATE'
            answer.append(record)
            continue
        preferred=(0,tuple(sorted((TRIPLES.index((0,2,3)),TRIPLES.index((0,1,6))))))
        candidates=[(e,pair) for e in range(8)
                    for pair in combinations([i for i,t in enumerate(TRIPLES) if e in t],2)]
        candidates.remove(preferred)
        candidates.insert(0,preferred)
        attempts=0
        for e,pair in candidates:
            attempts+=1
            allowed=[i for i,t in enumerate(TRIPLES) if e not in t or i in pair]
            witnesses=[]
            for sig in sigs:
                witness=kernel_proposal(rows,sig,allowed)
                if witness is None:
                    break
                witnesses.append(witness)
            if len(witnesses)==3:
                record.update({'status':'EXACT_POSITIVE_SHARED_PENCIL','label_one_based':e+1,
                               'pair_row_indices':list(pair),'pair_triples_one_based':[[j+1 for j in TRIPLES[i]] for i in pair],
                               'restricted_witnesses':witnesses,'proposal_cases_examined':attempts})
                break
        else:
            record.update({'status':'NO_POSITIVE_FOUND_NOT_A_NEGATIVE_CERTIFICATE','proposal_cases_examined':attempts})
        answer.append(record)
        print(name,record['status'],record.get('label_one_based'),record.get('pair_triples_one_based'),flush=True)
    (HERE/'CONTROLS.json').write_bytes((json.dumps({'format':'shared-pencil-controls-v1','cases':answer},indent=2)+'\n').encode())


if __name__=='__main__':
    run()
