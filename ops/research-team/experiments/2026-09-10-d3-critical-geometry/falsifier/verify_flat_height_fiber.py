from pathlib import Path
from itertools import combinations
import json,sympy as S
P=Path(__file__).resolve().parent;source=json.loads((P/'NONCOLLINEAR_INDEPENDENT_REPLAY.json').read_text());Y0=S.Matrix([[S.Rational(x)for x in row]for row in source['parent']]);p=S.Matrix([S.Rational(x)for x in source['ordinary_concurrences']['P']]);q=S.Matrix([S.Rational(x)for x in source['ordinary_concurrences']['Q']]);r0=S.Matrix([S.Rational(x)for x in source['ordinary_concurrences']['R']]);u,v,w,t=S.symbols('u v w t');hs=(u,v,w,t);base=(1,2,-5,-4);tau=S.Symbol('tau');Y=Y0.copy()
for j,h,b in zip(range(4,8),hs,base):Y[:,j]+=p*(h-b)
Ns={};raw={}
for name,K in source['supports_1based'].items():
 A=S.Matrix([[(-1)**(r+3)*Y[[k for k in range(4)if k!=r],[int(j)-1 for j in J]].det()for r in range(4)]for J in K]);Ns[name]=A;raw[name]=S.factor(A.det(method='domain-ge'))
assert raw=={'P':0,'Q':0,'R':S.Rational(5,2)*u*(t-2*u+w+11)}
assert Ns['P']*p==S.zeros(4,1) and (Ns['Q']*q).applyfunc(S.factor)==S.zeros(4,1)
assert S.Matrix.hstack(Y0[:,0],p,q).rank()==3
np=(Ns['R']*p).applyfunc(S.factor);assert np[2]!=0 and not np[2].free_symbols
B={''.join(str(j+1)for j in J):S.expand(Y[:,J].det())for J in combinations(range(8),4)};assert all(S.Poly(b,*hs).total_degree()<=1 for b in B.values());baseval={k:b.subs(dict(zip(hs,base)))for k,b in B.items()};assert all(baseval.values())
# Explicit escape line: only label6 moves, keeping the three selected points fixed.
line={u:1,v:2+tau,w:-5,t:-4};assert all(raw[n].subs(line)==0 for n in raw)
for name,pt in [('P',p),('Q',q),('R',r0)]:assert (Ns[name].subs(line)*pt).applyfunc(S.factor)==S.zeros(4,1)
lo=None;hi=None;lob=[];hib=[]
for lab,b in B.items():
 bb=S.Poly(b.subs(line),tau);c=bb.eval(0);d=bb.coeff_monomial(tau)
 if not d:continue
 root=-c/d
 if c*d>0:
  if lo is None or root>lo:lo=root;lob=[lab]
  elif root==lo:lob.append(lab)
 else:
  if hi is None or root<hi:hi=root;hib=[lab]
  elif root==hi:hib.append(lab)
assert lo is not None and hi is not None and lo<0<hi
out={'scope':'Exact full fixed-P height fiber of the noncollinear critical witness; no universal flat-locus theorem','parent_height_matrix':[[str(c)for c in Y.row(i)]for i in range(4)],'free_height_order':['u','v','w','t'],'base_height':list(base),'raw_wall_polynomials':{k:str(f)for k,f in raw.items()},'parent_brackets':{k:str(f)for k,f in B.items()},'R_plane':'t-2u+w+11=0','dimension_of_full_feasible_convex_fiber':3,'constant_Q_concurrence':[str(c)for c in q],'R257_evaluation_at_p':str(np[2]),'p_q_parent1_span_rank':3,'collision_free_and_noncollinear_throughout_uniform_R_plane':True,'vertical_gradient_rank_throughout_uniform_R_plane':1,'escape_line':{'height':['1','2+tau','-5','-4'],'maximal_parent_residence_interval':[str(lo),str(hi)],'lower_parent_boundary_brackets':lob,'upper_parent_boundary_brackets':hib,'all_selected_concurrences_constant':True},'new_original_obligations':0}
(P/'FLAT_HEIGHT_FIBER.json').write_text(json.dumps(out,indent=2)+'\n');print('PASS full3D convex noncollinear critical fiber; escape tau in',lo,hi,'end walls',lob,hib)
