from pathlib import Path
from itertools import combinations
import json,time
import sympy as S
P=Path(__file__).resolve().parent;src=P.parent/'checkpoint/falsifier/QUAD_INERTIA.json';old=json.loads(src.read_text())['records']
allprior=json.loads((P.parent/'checkpoint/falsifier/HEIGHT_OVAL_PROBE.json').read_text())['records']
for trial in [0,13]:
 r=next(r for r in allprior if r['trial']==trial)
 old.append({'trial':trial,'support_0based':r['support'],'kind':r['kind']})
xs=S.symbols('x y z w');x,y,z,w=xs;s=S.Symbol('s')
Y=S.Matrix([[0,0,0,1,1,1,1,1],[0,1,1,0,0,3,4,s],[1,0,-1,0,2,0,-5,-1-s],[0,0,1,0,x,y,z,w]])
trs=list(combinations(range(8),3));bas=list(combinations(range(8),4))
N={J:[S.expand((-1)**(r+3)*Y[[k for k in range(4)if k!=r],list(J)].det())for r in range(4)]for J in trs}
bpol=[S.expand(Y[:,J].det())for J in bas]
Kfield=S.QQ.frac_field(s)
def canon(f):
 p=S.Poly(f,*xs,domain=Kfield)
 if p.is_zero:return ()
 return tuple((m,S.cancel(c/p.LC()))for m,c in p.terms())
units={canon(f)for f in bpol};records=[];start=time.time()
for r in old:
 J=r['support_0based'];M=S.Matrix([N[tuple(t)]for t in J]);D=S.expand(M.det(method='domain-ge'));fac=S.factor_list(D)[1];remain=[];unit=[]
 for f,m in fac:
  q=S.Poly(f,*xs,domain=Kfield)
  if q.total_degree()==0:unit.append({'polynomial':str(f),'multiplicity':m,'kind':'parameter coefficient'})
  elif canon(f)in units:unit.append({'polynomial':str(f),'multiplicity':m,'kind':'parent bracket'})
  else:remain.append({'polynomial':str(f),'multiplicity':m,'height_degree':q.total_degree()})
 rec={'trial':r['trial'],'support_0based':J,'factor_kind':r['kind'],'raw_normal_determinant':str(S.factor(D)),'residual_factors':remain,'removed_generic_units':unit};records.append(rec)
 print(r['trial'],[(q['height_degree'],q['multiplicity'])for q in remain],flush=True)
out={'scope':'24 selected determinant families (22 quadratic and2 cubic) under one-parameter actual projected-parent deformation; parameter exceptional values not yet classified','parameter':'s','height_matrix':[[str(v)for v in Y.row(i)]for i in range(4)],'records':records,'parent_brackets_1based':{''.join(str(i+1)for i in J):str(f)for J,f in zip(bas,bpol)}}
(P/'DEFORMED_QUADRATICS.json').write_text(json.dumps(out,indent=2)+'\n');print('seconds',time.time()-start)
