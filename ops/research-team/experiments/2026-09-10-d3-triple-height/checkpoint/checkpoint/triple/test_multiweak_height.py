import json,sympy as s,itertools
from pathlib import Path
P=Path(__file__).resolve().parent;J=json.loads((P/'ACTUAL_UNIQUE_HARD_THREE_BOUNDARY_SIGNATURES.json').read_text());Y=s.Matrix([[s.Rational(x)for x in r]for r in J['center']['Y']]);T=list(itertools.combinations(range(8),3));points=[s.Matrix([s.Rational(x)for x in Z['weak_primal']])for Z in J['signatures']];ell=s.Matrix.hstack(*points).T.nullspace()[0]
rows=[]
k=next(k for k in range(4)if ell[k]);v=s.Matrix([1,2,3,4]);v=v/(ell.dot(v))
for z,p in zip(J['signatures'],points):
 for idx in z['support_indices']:
  I=T[idx];row=[s.Rational(0)]*8
  for j,col in enumerate(I):
   A=Y[:,I];A[:,j]=v;row[col]=s.Matrix.hstack(A,p).det()
  rows.append(row)
M=s.Matrix(rows);heights=(ell.T*Y).T
print('ell',list(ell),'v',list(v),'rank',M.rank(),'ker',len(M.nullspace()),'heights',list(heights),'kernel?',M*heights==s.zeros(12,1),flush=True)
N=M.nullspace();out={'schema':'three_weak_points_fixed_height_gate_v1','covector':list(map(str,ell)),'direction':list(map(str,v)),'matrix':[[str(x)for x in r]for r in M.tolist()],'rank':M.rank(),'kernel_basis':[[str(x)for x in p]for p in N],'height_vector':list(map(str,heights))};(P/'MULTIWEAK_HEIGHT_GATE.json').write_text(json.dumps(out,indent=2)+'\n')
