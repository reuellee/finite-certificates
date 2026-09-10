from pathlib import Path
from itertools import combinations
import json,sympy as S
P=Path(__file__).resolve().parent;D=json.loads((P/'DEFORMED_QUADRATICS.json').read_text());rec={r['trial']:r for r in D['records']};x,y,z,w,s=S.symbols('x y z w s');hs=(x,y,z,w)
Y=S.Matrix([[S.sympify(c)for c in row]for row in D['height_matrix']]);K={'P':[(0,1,2),(0,3,4),(1,3,5),(2,6,7)],'Q':rec[10]['support_0based'],'R':rec[0]['support_0based']}
Ns={name:S.Matrix([[(-1)**(r+3)*Y[[k for k in range(4)if k!=r],list(J)].det()for r in range(4)]for J in support])for name,support in K.items()};raw={name:S.factor(N.det(method='domain-ge'))for name,N in Ns.items()};out=[]
for sv,pt in [(S.Integer(2),[1,3,8,S.Rational(3,2)]),(S.Rational(-9,8),[S.Rational(-3,2),3,S.Rational(26,7),S.Rational(-3,8)])]:
 sub={s:sv,**dict(zip(hs,pt))};YY=Y.subs(sub);vals={''.join(str(j+1)for j in J):YY[:,J].det()for J in combinations(range(8),4)};zero=[lab for lab,b in vals.items()if b==0];assert '1346'in zero and '3458'in zero
 assert all(f.subs(sub)==0 for f in raw.values());J=S.Matrix([[S.diff(raw[name],h).subs(sub)for h in hs]for name in ['Q','R']]);assert J.rank()==1
 pts={name:N.subs(sub).nullspace()[0]for name,N in Ns.items()};assert S.Matrix.hstack(*pts.values()).rank()==3
 out.append({'parameter':str(sv),'heights':[str(v)for v in pt],'parent_zero_brackets':zero,'all_three_raw_walls_zero':True,'vertical_determinant_gradient_rank':1,'ordinary_kernel_vectors':{n:[str(v)for v in p]for n,p in pts.items()},'kernel_span_rank':3,'admissible_original_parent':False})
(P/'DEFORMATION_BOUNDARY_CANARIES.json').write_text(json.dumps({'scope':'Two rejected noncollinear critical points on parent degeneracies; not original-scope counterexamples','records':out},indent=2)+'\n');print('PASS two noncollinear critical boundary canaries rejected by parent units')
