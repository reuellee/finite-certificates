#!/usr/bin/env python3
"""Finite incidence proof for the omitted-label ruled-quadric argument."""
from itertools import combinations
from pathlib import Path
import json
P=Path(__file__).resolve().parent
supports={50:((1,2,3),(1,4,5),(2,4,6),(3,7,8)),51:((1,2,3),(1,4,5),(2,6,7),(4,6,8))}
records=[]
for typ,U in supports.items():
 for moving in range(1,9):
  incident=[T for T in U if moving in T];fixed=[T for T in U if moving not in T]
  assert len(incident)in(1,2)
  if len(incident)==1:
   records.append({'type':typ,'moving_label':moving,'case':'AFFINE_PLANE_OR_WHOLE_SPACE','incident_triple':incident[0]});continue
  lines=[tuple(x for x in T if x!=moving)for T in incident]
  assert len(set(lines[0]+lines[1]))==4
  found=None
  for ix,line in enumerate(lines):
   for C,D in [fixed,fixed[::-1]]:
    for x in line:
     y=next(z for z in line if z!=x)
     if x in C and y not in C and x not in D:
      found=(ix,line,x,y,C,D);break
    if found:break
   if found:break
  assert found
  ix,line,x,y,C,D=found;other=lines[1-ix]
  z=next(k for k in range(1,9)if k not in line and k!=moving)
  outside=next((v,E)for v in other for E in [C,D]if v not in E)
  # All listed four-brackets are actual distinct-label parent units.
  units=[tuple(sorted((*C,y))),tuple(sorted((*D,x))),tuple(sorted((*line,*other))),tuple(sorted((moving,*line,z))),tuple(sorted((*outside[1],outside[0])))]
  assert all(len(set(J))==4 for J in units)
  records.append({'type':typ,'moving_label':moving,'case':'RULED_QUADRIC_WITH_AT_MOST_ONE_EXCEPTIONAL_PLANE','skew_line_ab':line,'other_line_cd':other,'fixed_plane_C':C,'fixed_plane_D':D,'C_intersection_label':x,'affine_cut_label_z':z,'other_line_not_L_witness':{'endpoint':outside[0],'fixed_plane':outside[1]},'parent_bracket_units':units})
assert len(records)==16 and sum(r['case'].startswith('RULED')for r in records)==8
out={'status':'PASS_CANONICAL_INCIDENCE_LEMMA','scope':'Combinatorial skew-line and genuine affine-cut hypotheses for all moving labels of factor kinds50,51; topological argument in RULED_QUADRIC_AUDIT.md','cases':records,'original_D3':'OPEN','original_obligations_closed':0}
(P/'RULED_QUADRIC_CASES.json').write_text(json.dumps(out,indent=2)+'\n')
print('PASS: 8 ruled-quadric and8 affine-linear cases; all asserted brackets use4distinctparentlabels.')
