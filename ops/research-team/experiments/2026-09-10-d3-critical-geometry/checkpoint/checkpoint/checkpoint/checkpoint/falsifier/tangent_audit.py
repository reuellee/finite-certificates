from pathlib import Path
from fractions import Fraction as Q
import itertools,json,math,hashlib
from functools import cmp_to_key
import sympy as S
P=Path(__file__).resolve().parent
K=[(Q(8),Q(19,2)),(Q(32,25),Q(19,25)),(Q(2,5),Q(19,40)),(Q(1),Q(0)),(Q(0),Q(1))]
def dot(a,b):return sum(x*y for x,y in zip(a,b))
def primitive(v):
 l=math.lcm(*(x.denominator for x in v));v=[int(x*l)for x in v];g=math.gcd(*v);return tuple(x//g for x in v)
def ordered(vs):
 def cmp(a,b):
  ha=int(a[1]>0 or(a[1]==0 and a[0]>=0));hb=int(b[1]>0 or(b[1]==0 and b[0]>=0))
  if ha!=hb:return -1 if ha<hb else 1
  cross=a[0]*b[1]-a[1]*b[0];return -1 if cross>0 else (1 if cross<0 else 0)
 vs=sorted(set(vs),key=cmp_to_key(cmp));assert all(vs[i][0]*vs[(i+1)%len(vs)][1]-vs[i][1]*vs[(i+1)%len(vs)][0]>0 for i in range(len(vs)));return vs
rays=ordered([primitive(tuple(s*x for x in r))for r in K for s in [-1,1]])
qrays=ordered([primitive((s*r[1],-s*r[0]))for r in K for s in [-1,1]])
sigs=[];crays=[]
for s in itertools.product((-1,1),repeat=5):
 rr=[q for q in qrays if all(si*dot(k,q)>=0 for si,k in zip(s,K))]
 if len(rr)==2 and rr[0][0]*rr[1][1]-rr[0][1]*rr[1][0]!=0:
  q=[sum(x)for x in zip(*rr)];assert all(si*dot(k,q)>0 for si,k in zip(s,K));sigs.append(s);crays.append(rr)
assert len(sigs)==8
source=json.loads((P.parent/'previous_checkpoint/falsifier/certificate.json').read_text())
A=S.Matrix([[S.Rational(x)for x in row[:3]]for row in source['center_signed_normals']]);KK=S.Matrix(K)
assert A.rank()==3 and KK.rank()==2 and A.T*KK==S.zeros(3,2)
J=KK.T*S.Matrix([[0,1],[-2,1],[2,1],[2,1],[-2,1]])
assert J.det()!=0
N=len(rays)
# circle vertices0...N-1, edge i joins vertexi to i+1. closed B when a dual extreme dot is <=0.
def bad(i,u):return any(dot(q,u)<=0 for q in crays[i])
Bs=[]
for i in range(8):
 v={j for j,r in enumerate(rays)if bad(i,r)};e={j for j in range(N)if bad(i,tuple(x+y for x,y in zip(rays[j],rays[(j+1)%N])))}
 assert all(j in v and (j+1)%N in v for j in e);Bs.append((v,e))
def link(ids):
 v=set.intersection(*(Bs[i][0]for i in ids));e=set.intersection(*(Bs[i][1]for i in ids));comps=[]
 while v:
  todo=[min(v)];v.remove(todo[0]);c=[]
  while todo:
   j=todo.pop();c.append(j)
   for k,edge in [((j+1)%N,j),((j-1)%N,(j-1)%N)]:
    if edge in e and k in v:v.remove(k);todo.append(k)
  comps.append(sorted(c))
 return sorted(comps)
records=[]
for ids in itertools.combinations(range(8),3):
 tc=link(ids);pc=[link(p)for p in itertools.combinations(ids,2)];cols=[]
 for sign,cs in zip([1,-1,1],pc):
  for c in cs[1:]:
   vals=[int(bool(set(t)&set(c)))for t in tc]
   cols.append([sign*(v-vals[0])for v in vals[1:]])
 rows=len(tc)-1
 M=S.Matrix(rows,len(cols),lambda i,j:cols[j][i]);rank=M.rank();null=M.nullspace()
 records.append({'indices':ids,'pair_link_components':pc,'triple_link_components':tc,'source_dimension':len(cols),'target_dimension':rows,'matrix':[list(map(int,M.row(i)))for i in range(M.rows)],'rank':rank,'kernel_dimension':len(cols)-rank,'null_vectors':[[str(x)for x in z]for z in null]})
res={'scope':'EXACT_LINEARIZED_FIVE_ACTIVE_NORMAL_MODEL_ONLY; not full parent geometry or original compact support groups','K':[[str(x)for x in r]for r in K],'active_spatial_normals':[[str(x)for x in A.row(i)]for i in range(5)],'parameter_map':[[str(x)for x in J.row(i)]for i in range(2)],'parameter_map_determinant':str(J.det()),'link_rays':rays,'signature_relative_signs':sigs,'positive_kernel_cone_rays':crays,'records':records,'triple_count':len(records),'kernel_examples':sum(r['kernel_dimension']>0 for r in records),'empty_links':sum(not r['triple_link_components']for r in records),'source_sha256':hashlib.sha256((P.parent/'previous_checkpoint/falsifier/certificate.json').read_bytes()).hexdigest()}
(P/'TANGENT_AUDIT.json').write_text(json.dumps(res,indent=2)+'\n')
print(json.dumps({k:res[k]for k in ['triple_count','kernel_examples','empty_links']},indent=2))
print('Minimal sample',next(r for r in records if r['indices']==(0,1,6)))
