import json,itertools,sympy as S,numpy as np
from scipy.optimize import linprog
from pathlib import Path
P=Path(__file__).resolve().parent;B=P.parent
D=json.loads((B/'previous_checkpoint/falsifier/certificate.json').read_text());A=np.array([[float(S.Rational(x))for x in row[:3]]for row in D['center_signed_normals']]);K=np.array([[8,9.5],[1.28,.76],[.4,.475],[1,0],[0,1]])
# derivative along H,G from previous exact certificate
d=np.array([0,-2,2,2,-2]);g=np.ones(5)
signs=[]
for sig in itertools.product((-1,1),repeat=5):
 # full-support positive witness at center
 r=linprog(np.zeros(5),A_eq=np.vstack([A.T*np.array(sig),np.ones(5)]),b_eq=[0,0,0,1],bounds=(1e-7,None),method='highs')
 if r.success:signs.append(sig)
print('candidate signs',signs)
# screen 80 rational direction points on square perimeter; collect strict LP primal witnesses
rays=[]
for x in range(-10,11):
 for y in range(-10,11):
  if max(abs(x),abs(y))==10:rays.append((x,y))
coverage=[]
for sig in signs:
 good=set()
 for j,(x,y)in enumerate(rays):
  ss=np.array(sig);r=linprog(np.zeros(3),A_ub=-ss[:,None]*A,b_ub=ss*(x*d+y*g)-1,bounds=[(None,None)]*3,method='highs')
  if r.success:good.add(j)
 coverage.append(good)
for ids in itertools.combinations(range(len(signs)),3):
 if set.union(*(coverage[i]for i in ids))==set(range(len(rays))):
  print('FOUND',ids,[signs[i]for i in ids]);(P/'screen_candidate.json').write_text(json.dumps({'signs':[signs[i]for i in ids],'directions':rays,'coverage':[sorted(coverage[i])for i in ids]},indent=2)+'\n');break
else:print('NO COVER')
