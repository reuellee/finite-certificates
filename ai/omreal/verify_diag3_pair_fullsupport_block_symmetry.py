#!/usr/bin/env python3
"""Exact S3 moving-column symmetry closure of row-2599 full-support walls.

The preceding 105-segment certificate proves 10,844 candidate residual walls
meet the strict parent interior.  This checker proves that the strict parent
cell is invariant under every permutation of the three moving columns and
transports those certified zero sets through that exact S3 action.

No factor in the final residue is called empty.
"""
from __future__ import annotations
from itertools import permutations
import hashlib, json
from pathlib import Path
import sys
import numpy as np
HERE=Path(__file__).resolve().parent; sys.path.insert(0,str(HERE))
import DIAG2_PIVOT_LABELED_PAIR_ORBITS_VERIFY as labeled
import DIAG9_GRAPH_global_factor_census as global_factors
import verify_diag3_pair_fullsupport_safe_segment_walls as base
import verify_diag3_pair_global_parent_face_gate as gate
EXPECTED_BASE_OPEN=6980
EXPECTED_BASE_OPEN_SHA256='72de0ff0ba439e00a54e8fdb16a1505d4d7a8fbfaf7f42c00030f1c1a7149930'
EXPECTED_CLOSED=16830
EXPECTED_RESIDUE=994
EXPECTED_RESIDUE_SHA256='c330ba558fedd9b0502c8e96b35cecf179e2ec5b2eb5324893a374c4f09039cf'

def primitive_key(poly):
 return tuple(sorted(global_factors.primitive(poly).items()))

def transform(poly,perm):
 out={}
 for monomial,coefficient in poly.items():
  target=[0]*9
  for block in range(3):
   for row in range(3): target[3*perm[block]+row]=monomial[3*block+row]
  target=tuple(target); out[target]=out.get(target,0)+coefficient
 return global_factors.primitive(out)

def base_open_ids(points,polynomials,candidates):
 # Reconstruct the exact theorem partition from the preceding certificate.
 # Float signs only propose an edge; each proposed crossing is rechecked exactly.
 xs=np.asarray([[float(v) for v in point] for point in points])
 values=base.factor_value_table(xs); open_ids=[]
 import verify_diag2_canonical_robust_edges as evaluator
 for factor_id in candidates:
  witness=False
  for i,j in base.EDGES:
   if values[factor_id,i]*values[factor_id,j] < 0:
    left=evaluator.evaluate(polynomials[factor_id],points[i]); right=evaluator.evaluate(polynomials[factor_id],points[j])
    if left*right < 0: witness=True; break
  if not witness: open_ids.append(factor_id)
 digest=hashlib.sha256(','.join(map(str,open_ids)).encode('ascii')).hexdigest()
 if len(open_ids)!=EXPECTED_BASE_OPEN or digest!=EXPECTED_BASE_OPEN_SHA256: raise AssertionError('base 105-segment partition changed')
 return tuple(open_ids)

def main():
 # First replay the load-bearing exact segment theorem, including all 70 parent inequalities.
 base.main()
 records=[json.loads(line) for line in (HERE/'certs_4_8.jsonl').read_text().splitlines() if line]
 parents,_=gate.parent_polynomials(records[2599])
 signed_parent={primitive_key({m:target*c for m,c in poly.items()}) for _label,target,poly,_terms in parents}
 perms=tuple(permutations(range(3)))
 if len(signed_parent)!=63: raise AssertionError('signed parent polynomial census changed')
 for perm in perms:
  transported={primitive_key(transform({m:target*c for m,c in poly.items()},perm)) for _label,target,poly,_terms in parents}
  if transported!=signed_parent: raise AssertionError(f'parent cell lost block symmetry {perm}')
 candidates=gate.parse_candidates(); candidate_set=set(candidates)
 _occ,_map,polynomials=labeled.factor_polynomials(); factor_index={primitive_key(poly):i for i,poly in enumerate(polynomials)}
 if len(factor_index)!=26740: raise AssertionError('factor zero-set keys are not unique')
 with np.load(gate.POINT_BANK,allow_pickle=False) as source: matrices=np.asarray(source['chart_matrix'],dtype=np.int64)
 points=tuple(gate.normalized_values(matrix.tolist()) for matrix in matrices)
 open_ids=set(base_open_ids(points,polynomials,candidates)); crossed=candidate_set-open_ids
 closure=set()
 for factor_id in crossed:
  for perm in perms:
   transported=factor_index[primitive_key(transform(polynomials[factor_id],perm))]
   if transported in candidate_set: closure.add(transported)
 residue=tuple(sorted(candidate_set-closure)); digest=hashlib.sha256(','.join(map(str,residue)).encode('ascii')).hexdigest()
 if len(closure)!=EXPECTED_CLOSED or len(residue)!=EXPECTED_RESIDUE or digest!=EXPECTED_RESIDUE_SHA256: raise AssertionError((len(closure),len(residue),digest))
 print('PASS exact S3 invariance of the strict row-2599 parent cell')
 print('PASS',EXPECTED_CLOSED,'of 17824 candidate residual walls certified interior-nonempty')
 print('NEW',EXPECTED_CLOSED-(len(candidates)-EXPECTED_BASE_OPEN),'walls obtained by symmetry transport')
 print('OPEN',EXPECTED_RESIDUE,'candidate factors retained without emptiness/nonemptiness claim')
 print('OPEN_SHA256',digest)
 print('SCOPE exact nonemptiness transport only; diagonal three remains open')
if __name__=='__main__': main()
