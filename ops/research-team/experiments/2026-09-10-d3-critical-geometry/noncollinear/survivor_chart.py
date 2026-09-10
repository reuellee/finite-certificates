"""Full four-line P50 contraction chart for named survivor. Exact bounded algebra."""
from pathlib import Path
from itertools import combinations
import sympy as s,json,hashlib
ROOT=Path(__file__).resolve().parents[1]
A,B,C,D,u,v,w,t=s.symbols('A B C D u v w t');base=(A,B,C,D);height=(u,v,w,t)
Y=s.Matrix([[0,0,0,1,1,1,1,1],[0,1,1,0,0,B,C,D],[1,0,-1,0,A,0,-1-C,-1-D],[0,0,1,0,u,v,w,t]])
def normal(I):
 M=Y[:,[int(j)-1 for j in I]]
 return s.Matrix([[(-1)**(3+j)*M[[k for k in range(4) if k!=j],:].det() for j in range(4)]])
supports={'P':['123','145','246','378'],'Q':['126','257','367','458'],'R':['157','168','245','348']}
polys={k:s.factor(s.Matrix.vstack(*(normal(I) for I in K)).det(method='domain-ge')) for k,K in supports.items()}
br={''.join(str(j+1) for j in I):s.factor(Y[:,list(I)].det()) for I in combinations(range(8),4)}
assert polys['P']==0
for name,F in polys.items():
 print(name,s.factor(F),flush=True)
 if F:print('totaldegree',s.Poly(F,*(base+height)).total_degree(),'heightdegree',s.Poly(F,*height).total_degree(),'terms',len(s.Poly(F,*(base+height)).terms()),flush=True)
for name in ('Q','R'):
 print(name,'derivatives:',{str(x):s.factor(s.diff(polys[name],x)) for x in height},flush=True)
minors={str(i)+str(j):s.factor(s.diff(polys['Q'],height[i])*s.diff(polys['R'],height[j])-s.diff(polys['Q'],height[j])*s.diff(polys['R'],height[i])) for i,j in combinations(range(4),2)}
print('criticalminors',{k:(s.Poly(f,*(base+height)).total_degree(),len(s.Poly(f,*(base+height)).terms())) for k,f in minors.items()},flush=True)
out={'status':'EXACT_CHART_COMPUTED_NOT_CLOSED','base':list(map(str,base)),'heights':list(map(str,height)),'parent_matrix':[[str(x) for x in row] for row in Y.tolist()],'ordinary_supports':supports,'raw_factors':{k:str(f) for k,f in polys.items()},'parent_brackets':{k:str(f) for k,f in br.items()},'critical_minors':{k:str(f) for k,f in minors.items()},'height_degrees':{k:s.Poly(f,*height).total_degree() for k,f in polys.items() if f},'parent_affine':all(s.Poly(f,*height).total_degree()<=1 for f in br.values()),'scope':'Contraction chart algebra; no noncompactness or critical-locus closure follows.'}
(ROOT/'noncollinear/survivor_CONTRACTION_CHART.json').write_text(json.dumps(out,indent=2)+'\n')
