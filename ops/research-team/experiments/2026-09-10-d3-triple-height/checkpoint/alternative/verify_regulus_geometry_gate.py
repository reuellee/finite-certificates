#!/usr/bin/env python3
"""Combinatorial hypotheses for the conventional three-skew-lines proof."""
from pathlib import Path
from itertools import combinations
import json,hashlib
P=Path(__file__).resolve().parent;src=P.parent/'original/AFFINE_PAIR_COVERAGE.json';J=json.loads(src.read_text());rows=[]
for z in J['remaining']:
 choices=[]
 for swap in [False,True]:
  E=[set(x)for x in(z['partner']if swap else z['anchor'])];F=[set(x)for x in(z['anchor']if swap else z['partner'])]
  for e in range(1,9):
   Em=[x for x in E if e in x];Fm=[x for x in F if e in x]
   if len(Em)!=1 or len(Fm)!=2:continue
   E0=[x for x in E if e not in x];F0=[x for x in F if e not in x];ab=Em[0]-{e};lines=[x-{e}for x in Fm]
   assert len(lines[0]|lines[1])==4
   # Two fixed P planes share a parent excluded by the third, hence rank3.
   rank_witness=[]
   for a,b in combinations(range(3),2):
    c=next(k for k in range(3)if k not in[a,b])
    for j in(E0[a]&E0[b])-E0[c]:rank_witness.append([a,b,c,j])
   assert rank_witness
   # P's fixed-three-plane concurrence does not lie on its parent line ab.
   nonzero_witness=[]
   for a in range(3):
    one=E0[a]&ab
    if len(one)!=1:continue
    j=next(iter(one))
    for b in range(3):
     if j not in E0[b]:nonzero_witness.append([a,b,j])
   assert nonzero_witness
   skew=[]
   for line in lines:
    ww=[]
    for a in range(2):
     one=F0[a]&line
     if len(one)!=1:continue
     j=next(iter(one))
     if j not in F0[1-a]:ww.append([a,1-a,j])
    if not ww:break
    skew.append(ww[0])
   if len(skew)!=2:continue
   choices.append({'swap':swap,'moving_label':e,'linear_parent_pair':sorted(ab),'quadratic_parent_lines':[sorted(x)for x in lines],'linear_fixed_triples':[sorted(x)for x in E0],'quadratic_fixed_triples':[sorted(x)for x in F0],'linear_rank_witness':rank_witness[0],'linear_nonzero_witness':nonzero_witness[0],'quadric_skew_witnesses':skew})
 assert choices
 rows.append({'source_index':z['source_index'],'choices':choices})
out={'schema':'balanced_pair_regulus_hypotheses_v1','source_sha256':hashlib.sha256(src.read_bytes()).hexdigest(),'pairs':len(rows),'valid_ordered_presentations':sum(len(x['choices'])for x in rows),'every_pair_has_a_valid_presentation':True,'scope':'All45 source pairs satisfy the elementary incidence hypotheses for a nonzero plane and smooth split quadric with forbidden smooth section marker; no Hc1 closure.','rows':rows};(P/'REGULUS_GEOMETRY_GATE.json').write_text(json.dumps(out,indent=2)+'\n');print({k:v for k,v in out.items()if k!='rows'})
