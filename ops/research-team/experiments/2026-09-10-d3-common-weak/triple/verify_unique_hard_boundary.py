#!/usr/bin/env python3
from verify_three_boundary_signatures import *
from copy import deepcopy
path=P/'ACTUAL_UNIQUE_HARD_THREE_BOUNDARY_SIGNATURES.json';J=json.loads(path.read_text());out=verify(J,[4,6,4,5,5,3,3,3])
for z in J['signatures']:assert z['all_zero_indices']==z['support_indices']
# Every positive Gordan witness is supported on zeros of any weak primal;
# exactly four such rows of rank three make the normalized witness unique.
H=json.loads((P/'MULTIWEAK_HEIGHT_GATE.json').read_text());M=matrix(H['matrix']);ell=list(map(F,H['covector']));v=list(map(F,H['direction']));Y=matrix(J['center']['Y']);points=[list(map(F,z['weak_primal']))for z in J['signatures']]
assert all(dot(ell,p)==0 for p in points);assert dot(ell,v)==1
h=[dot(ell,[Y[r][k]for r in range(4)])for k in range(8)];assert h==list(map(F,H['height_vector']))
rows=[]
for z,p in zip(J['signatures'],points):
 for idx in z['support_indices']:
  I=T[idx];row=[F(0)]*8
  for j,col in enumerate(I):
   C=[[Y[r][k]for k in I]+[p[r]]for r in range(4)]
   for r in range(4):C[r][j]=v[r]
   row[col]=det(C)
  rows.append(row)
assert M==rows and rank(M)==7 and all(dot(row,h)==0 for row in M)
assert all(any(Y[r][k]-v[r]*h[k] for r in range(4))for k in range(8))
mutants=[]
q=deepcopy(J);q['signatures'][1]['signs'][4]*=-1;mutants.append(q)
q=deepcopy(J);q['signatures'][2]['weak_primal'][0]='0';mutants.append(q)
q=deepcopy(J);q['signatures'][0]['feasible_parent'][1][6]='31';mutants.append(q)
rejected=0
for q in mutants:
 try:verify(q)
 except (AssertionError,ZeroDivisionError):rejected+=1
assert rejected==3
out.update({'unique_full_witness_polytopes':3,'minimum_union_label_degree':3,'multiweak_height_equation_rank':7,'multiweak_height_kernel_dimension':1,'multiweak_height_kernel':'only the global projective height scale','hostile_mutations_rejected':rejected,'input_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'scope':'Actual proper incomparable triple defeats automatic common weak primal, light-label choice, and this fixed-three-weak-point height deformation. It is not a compactness or D3 counterexample.'})
(P/'UNIQUE_HARD_BOUNDARY_REPLAY.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out,sort_keys=True))
