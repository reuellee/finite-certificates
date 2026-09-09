#!/usr/bin/env python3
"""One finite sampled actual-parent slice; floating LP output is heuristic only."""
from pathlib import Path
from itertools import combinations
from fractions import Fraction as Q
from hashlib import sha256
import json,time,resource
import numpy as np
from scipy.optimize import linprog
ROOT=Path(__file__).resolve().parents[3]; OWN=Path(__file__).resolve().parent
SOURCE='ops/team/ai-d3-shared-pencil-falsifier/upper_chart_0_flow.json'
TRIPLES=sorted(combinations(range(8),3),key=lambda b:b[::-1]); BASES=sorted(combinations(range(8),4),key=lambda b:b[::-1])
raw=(ROOT/SOURCE).read_bytes(); src=json.loads(raw); P=src['parent']; SIGS=src['signatures']
def det(a):
 a=[list(map(Q,row)) for row in a];out=Q(1)
 for j in range(len(a)):
  k=next((k for k in range(j,len(a)) if a[k][j]),None)
  if k is None:return Q(0)
  if k!=j:a[k],a[j]=a[j],a[k];out=-out
  z=a[j][j];out*=z
  for k in range(j+1,len(a)):
   r=a[k][j]/z
   for c in range(j+1,len(a)):a[k][c]-=r*a[j][c]
 return out
def parent(u,v):
 a=[r[:] for r in P];a[0][7]+=u;a[1][7]+=v;return a
def brackets(a):return [det([[a[r][j] for j in b] for r in range(4)]) for b in BASES]
def normals(a):
 a=np.asarray(a,dtype=float)
 return np.array([[(-1)**(r+3)*np.linalg.det(a[[k for k in range(4) if k!=r]][:,t]) for r in range(4)] for t in TRIPLES])
b0=brackets(P); bu=brackets(parent(1,0));bv=brackets(parent(0,1));
wall=[(abs(z),(x-z)*(1 if z>0 else -1),(y-z)*(1 if z>0 else -1)) for z,x,y in zip(b0,bu,bv)]
vertices=set()
for (c,a,b),(f,d,e) in combinations(wall,2):
 dd=a*e-b*d
 if not dd:continue
 u=(b*f-c*e)/dd;v=(c*d-a*f)/dd
 if all(c+a*u+b*v>=0 for c,a,b in wall):vertices.add((u,v))
verts=sorted(vertices,key=lambda p:np.arctan2(float(p[1]),float(p[0])))
# A strictly positive linear combination of opposing bounds is checked exactly
# through the recession test: every nonzero recession direction has an extreme
# ray perpendicular to one boundary, unless no nonconstant wall exists.
recession=[]
for c,a,b in wall:
 if not(a or b):continue
 for du,dv in [(b,-a),(-b,a)]:
  if all(x*du+y*dv>=0 for _,x,y in wall):recession.append([str(du),str(dv)])
assert verts and not recession,'This registered polygon slice must be bounded.'
# Fan nodes: origin plus N subdivisions on each origin/edge triangle; radial
# j/N, edge k/N. Exclude all true parent edges, include shared radial edges.
N=24; samples={(Q(0),Q(0))}
for p,q in zip(verts,verts[1:]+verts[:1]):
 for j in range(1,N):
  for k in range(N+1):
   u=Q(j,N)*(Q(N-k,N)*p[0]+Q(k,N)*q[0]);v=Q(j,N)*(Q(N-k,N)*p[1]+Q(k,N)*q[1]);samples.add((u,v))
start=time.monotonic();cpu=time.process_time();records=[];counts={}
for u,v in sorted(samples):
 ns=normals(parent(u,v));ns/=np.linalg.norm(ns,axis=1)[:,None]
 margins=[];supports=[];separators=[]
 for sig in SIGS:
  a=ns*np.array([1 if sig>>i&1 else -1 for i in range(56)])[:,None]
  # Maximize t with a*p >= t, |p_j|<=1. Strictly positive t => good.
  fit=linprog([0,0,0,0,-1],A_ub=np.c_[-a,np.ones(56)],b_ub=np.zeros(56),bounds=[(-1,1)]*4+[(0,None)],method='highs')
  assert fit.success
  margins.append(float(fit.x[4]));separators.append(fit.x[:4].tolist())
  dual=-fit.ineqlin.marginals; supports.append(np.flatnonzero(dual>1e-7).tolist())
 bits=''.join('G' if x>1e-7 else 'B' for x in margins);counts[bits]=counts.get(bits,0)+1
 records.append({'u':str(u),'v':str(v),'state':bits,'margins':margins,'dual_supports':supports,'separators':separators})
print('counts',counts,flush=True)
# Chord v=0 and u=0 full parent intervals, separately sampled including center.
chords=[]
for axis in [0,1]:
 low=max(-c/(a,b)[axis] for c,a,b in wall if (a,b)[axis]>0)
 high=min(-c/(a,b)[axis] for c,a,b in wall if (a,b)[axis]<0)
 cr=[]
 for j in range(1,101):
  t=low+(high-low)*Q(j,101);u,v=(t,Q(0)) if axis==0 else (Q(0),t)
  ns=normals(parent(u,v));ns/=np.linalg.norm(ns,axis=1)[:,None];m=[];s=[];pr=[]
  for sig in SIGS:
   a=ns*np.array([1 if sig>>i&1 else -1 for i in range(56)])[:,None]
   fit=linprog([0,0,0,0,-1],A_ub=np.c_[-a,np.ones(56)],b_ub=np.zeros(56),bounds=[(-1,1)]*4+[(0,None)],method='highs')
   assert fit.success;m.append(float(fit.x[4]));s.append(np.flatnonzero(-fit.ineqlin.marginals>1e-7).tolist());pr.append(fit.x[:4].tolist())
  cr.append({'t':str(t),'state':''.join('G' if x>1e-7 else 'B' for x in m),'margins':m,'dual_supports':s,'separators':pr})
 chords.append({'axis':axis,'interval':[str(low),str(high)],'records':cr})
out={'classification':'HEURISTIC_FLOAT_LP_SAMPLE','source':SOURCE,'source_sha256':sha256(raw).hexdigest(),'parameterization':'Y[0,7]+=u; Y[1,7]+=v; other entries fixed','signatures':SIGS,'parent_wall_coefficients':[[str(x) for x in r] for r in wall],'closed_parent_polygon_vertices':[[str(x) for x in p] for p in verts],'recession_rays':recession,'fan_resolution':N,'sample_count':len(records),'state_counts':counts,'records':records,'coordinate_chords':chords,'elapsed_seconds':time.monotonic()-start,'cpu_seconds':time.process_time()-cpu,'maxrss_kib':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,'limitations':'Floating LP classifications; fan nodes do not certify cells, components, holes, or coverage of bad sets. All artificial radial/grid edges are internal.'}
(OWN/'DISCOVERY.json').write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps({k:v for k,v in out.items() if k not in ['records','coordinate_chords','parent_wall_coefficients']},indent=2),flush=True)
for c in chords:
 print('chord',c['axis'],c['interval'],{s:sum(r['state']==s for r in c['records']) for s in set(r['state'] for r in c['records'])})
