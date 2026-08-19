#!/usr/bin/env python3
"""Exact row-2599 relative-boundary support collapse."""
from collections import Counter
from itertools import product
import hashlib,json
from pathlib import Path
HERE=Path(__file__).resolve().parent; DATA=HERE/'data'
ATLAS=DATA/'DIAG3_PAIR_GLOBAL_row2599_compactification_atlas.json'
GATE=DATA/'DIAG3_PAIR_GLOBAL_row2599_parent_face_gate.json'
EXPECTED='65b425e0a9507dd536b59e770f3c43f5eb025381b2ca2e75eb009e93d022b02a'

def audit():
 a=json.loads(ATLAS.read_text()); g=json.loads(GATE.read_text())
 if a['model']!='product_of_three_closed_positive_projective_3_simplices': raise AssertionError('model')
 D={(int(r['moving_column']),int(r['coordinate_row'])):str(r['parent_bracket']) for r in a['boundary_divisors']}
 if len(D)!=12 or set(D)!={(c,r) for c in (6,7,8) for r in (1,2,3,4)}: raise AssertionError('divisors')
 for (c,r),b in D.items():
  if len(b)!=4 or str(c) not in b: raise AssertionError('parent divisor')
 rel={}; full=[]
 for s in product(range(1,16),repeat=3):
  tags=[]
  for block,mask in enumerate(s):
   for bit in range(4):
    if not(mask>>bit&1): tags.append(D[(6+block,bit+1)])
  if tags: rel[s]=tuple(sorted(set(tags)))
  else: full.append(s)
 if len(rel)!=3374 or full!=[(15,15,15)]: raise AssertionError('support partition')
 rows=g['nonexcluded_support_faces']; rr=[r for r in rows if tuple(r['support'])!=(15,15,15)]; ff=[r for r in rows if tuple(r['support'])==(15,15,15)]
 if len(rows)!=11 or len(rr)!=10 or len(ff)!=1: raise AssertionError('survivors')
 if any(tuple(r['support']) not in rel for r in rr): raise AssertionError('relative survivor')
 rm=sum(int(r['residual_states'][2]) for r in rr); fm=int(ff[0]['residual_states'][2])
 if (rm,fm,rm+fm)!=(52394,17824,70218): raise AssertionError('mixed accounting')
 p={'proper_support_count':len(rel),'full_support':[15,15,15],'nonexcluded_relative_support_count':len(rr),'nonexcluded_relative_dimension_histogram':dict(sorted(Counter(int(r['dimension']) for r in rr).items())),'relative_mixed_restrictions':rm,'full_support_mixed_restrictions':fm,'total_parent_face_mixed_restrictions':rm+fm,'boundary_divisor_map':[[c,r,D[(c,r)]] for c in (6,7,8) for r in (1,2,3,4)]}
 h=hashlib.sha256(json.dumps(p,sort_keys=True,separators=(',',':')).encode('ascii')).hexdigest()
 if h!=EXPECTED: raise AssertionError(h)
 return p,h

def main():
 p,h=audit(); print('PASS 3374/3374 proper supports are parent-boundary relative'); print('PASS unique possibly nonrelative support (15,15,15)'); print('PASS mixed residue',p['relative_mixed_restrictions'],'relative +',p['full_support_mixed_restrictions'],'full =',p['total_parent_face_mixed_restrictions']); print('SEMANTIC',h)
if __name__=='__main__': main()
