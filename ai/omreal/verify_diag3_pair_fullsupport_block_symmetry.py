#!/usr/bin/env python3
"""Exact no-go for moving-column symmetry closure at row 2599.

The preceding 105-segment certificate proves 10,844 candidate residual walls
meet the strict parent interior.  Permuting the three moving columns preserves
the *unsigned* parent-bracket divisor arrangement, but it does not preserve
the signed row-2599 parent cell.  This checker preserves coefficient signs
while transporting the 70 signed parent brackets and pins the obstruction:
every nonidentity permutation flips 19--27 of the 63 distinct primitive
signed inequalities.

Consequently no additional residual wall may be certified by unconditional
S3 transport.  The exact base-open count remains 6,980.
"""
from __future__ import annotations
from collections import Counter
from fractions import Fraction
from itertools import permutations
from math import gcd, lcm
import hashlib
import json
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
EXPECTED_SIGN_FLIPS = {
 (0,1,2): 0,
 (0,2,1): 23,
 (1,0,2): 19,
 (1,2,0): 22,
 (2,0,1): 22,
 (2,1,0): 27,
}
EXPECTED_SAFE_TRANSFORMED_SEGMENTS = 105
EXPECTED_SEGMENT_FAILURE_HISTOGRAM = {19:105,22:210,23:105,27:105}

def primitive_key(poly): return tuple(sorted(global_factors.primitive(poly).items()))
def raw_transform(poly,perm):
 out={}
 for monomial,coefficient in poly.items():
  target=[0]*9
  for block in range(3):
   for row in range(3): target[3*perm[block]+row]=monomial[3*block+row]
  target=tuple(target); out[target]=out.get(target,0)+coefficient
 return {monomial: coefficient for monomial, coefficient in out.items() if coefficient}
def transform(poly,perm): return global_factors.primitive(raw_transform(poly,perm))
def directed_key(poly):
 """Primitive integer key without identifying a polynomial with its negative."""
 clean={monomial:Fraction(coefficient) for monomial,coefficient in poly.items() if coefficient}
 denominator=1
 for coefficient in clean.values(): denominator=lcm(denominator,coefficient.denominator)
 integers={monomial:int(coefficient*denominator) for monomial,coefficient in clean.items()}
 divisor=0
 for coefficient in integers.values(): divisor=gcd(divisor,abs(coefficient))
 return tuple(sorted((monomial,coefficient//divisor) for monomial,coefficient in integers.items()))
def negative_key(key): return tuple((monomial,-coefficient) for monomial,coefficient in key)
def transform_point(point,perm):
 answer=[None]*9
 for block in range(3):
  for row in range(3): answer[3*perm[block]+row]=point[3*block+row]
 return tuple(answer)
def base_open_ids(points,polynomials,candidates):
 xs=np.asarray([[float(v) for v in point] for point in points]); values=base.factor_value_table(xs); open_ids=[]
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
 base.main()
 records=[json.loads(line) for line in (HERE/'certs_4_8.jsonl').read_text().splitlines() if line]
 parents,_=gate.parent_polynomials(records[2599]); perms=tuple(permutations(range(3)))
 signed_parent={directed_key({m:target*c for m,c in poly.items()}) for _label,target,poly,_terms in parents}
 if len(signed_parent)!=63: raise AssertionError('signed parent polynomial census changed')
 flip_counts={}
 for perm in perms:
  transported={directed_key(raw_transform({m:target*c for m,c in poly.items()},perm)) for _label,target,poly,_terms in parents}
  if any(key not in signed_parent and negative_key(key) not in signed_parent for key in transported):
   raise AssertionError(f'unsigned parent divisor arrangement lost symmetry {perm}')
  flips=sum(key not in signed_parent for key in transported)
  flip_counts[perm]=flips
 if flip_counts!=EXPECTED_SIGN_FLIPS: raise AssertionError(flip_counts)
 with np.load(gate.POINT_BANK,allow_pickle=False) as source: matrices=np.asarray(source['chart_matrix'],dtype=np.int64)
 points=tuple(gate.normalized_values(matrix.tolist()) for matrix in matrices)
 safe_segments=0; failure_histogram=Counter()
 for perm in perms:
  for left,right in base.EDGES:
   start=transform_point(points[left],perm); end=transform_point(points[right],perm); failures=0
   for _label,target,poly,_terms in parents:
    if not base.positive_unit([target*c for c in base.segment_power(poly,start,end)]): failures+=1
   if failures: failure_histogram[failures]+=1
   else: safe_segments+=1
 if safe_segments!=EXPECTED_SAFE_TRANSFORMED_SEGMENTS or dict(sorted(failure_histogram.items()))!=EXPECTED_SEGMENT_FAILURE_HISTOGRAM:
  raise AssertionError((safe_segments,dict(sorted(failure_histogram.items()))))
 print('PASS unsigned parent-bracket divisor arrangement has exact S3 symmetry')
 print('NO_GO signed row-2599 parent cell is not S3-invariant')
 print('SIGN_FLIPS',flip_counts)
 print('NO_GO 525/525 nonidentity transported witness segments leave the signed parent cell')
 print('SEGMENT_FAILURE_HIST',dict(sorted(failure_histogram.items())))
 print('OPEN',EXPECTED_BASE_OPEN,'candidate factors retained after the valid segment theorem')
 print('SCOPE no unconditional symmetry transport is valid; diagonal three remains open')
if __name__=='__main__': main()
