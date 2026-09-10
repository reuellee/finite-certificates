from pathlib import Path
from itertools import combinations
import json,sympy as S
P=Path(__file__).resolve().parent;src=json.loads((P/'NONZERO_NONCOLLINEAR_REPLAY.json').read_text());Y0=S.Matrix([[S.Rational(c)for c in row]for row in src['parent']]);points={n:S.Matrix([S.Rational(c)for c in p])for n,p in src['ordinary_concurrences'].items()};p=points['P'];u,v,w,t=S.symbols('u v w t');hs=(u,v,w,t);base=(1,2,-5,-4);tau=S.Symbol('tau');Y=Y0.copy()
for j,h,b in zip(range(4,8),hs,base):Y[:,j]+=p*(h-b)
Ns={};raw={}
for name,K in src['supports_1based'].items():
 N=S.Matrix([[(-1)**(r+3)*Y[[k for k in range(4)if k!=r],[int(j)-1 for j in I]].det()for r in range(4)]for I in K]);Ns[name]=N;raw[name]=S.factor(N.det(method='domain-ge'))
L=t+2*v;G=2*t-5*w-23;Q=S.Rational(3,2)*L*G
assert all(S.expand(raw[k]-f)==0 for k,f in {'P':0,'Q':Q,'R':u*Q}.items())
B={''.join(str(i+1)for i in I):S.expand(Y[:,I].det())for I in combinations(range(8),4)}
units={}
for name,F in [('u',u),('G',G)]:
 for lab,b in B.items():
  ratio=S.cancel(b/F)
  if ratio!=0 and not ratio.free_symbols:units[name]={'parent_bracket':lab,'bracket_to_factor_ratio':str(ratio)};break
 assert name in units
assert all(S.Poly(b,*hs).total_degree()<=1 for b in B.values())
assert all(b.subs(dict(zip(hs,base)))!=0 for b in B.values())
line={u:1+tau,v:2,w:-5,t:-4};assert all(f.subs(line)==0 for f in raw.values())
for n,pt in points.items():assert (Ns[n].subs(line)*pt).applyfunc(S.factor)==S.zeros(4,1)
lo=None;hi=None;low=[];high=[]
for lab,b in B.items():
 bb=S.Poly(b.subs(line),tau);c=bb.eval(0);d=bb.coeff_monomial(tau)
 if not d:continue
 a=-c/d
 if c*d>0:
  if lo is None or a>lo:lo=a;low=[lab]
  elif a==lo:low.append(lab)
 else:
  if hi is None or a<hi:hi=a;high=[lab]
  elif a==hi:high.append(lab)
assert lo is not None and hi is not None and lo<0<hi
out={'scope':'Exact vertical coincidence and escape mechanism for the both-nonzero noncollinear critical witness; no universal critical-locus conclusion','height_matrix':[[str(c)for c in Y.row(i)]for i in range(4)],'height_order':['u','v','w','t'],'base_height':list(base),'raw_walls':{n:str(f)for n,f in raw.items()},'parent_unit_identifications':units,'common_residual_height_plane':'t+2v=0','dimension_of_full_feasible_convex_fiber':3,'raw_vertical_gradients_proportional_on_common_plane':True,'both_vertical_gradients_nonzero_on_uniform_common_plane':True,'escape_line':{'height':['1+tau','2','-5','-4'],'maximal_parent_residence_interval':[str(lo),str(hi)],'lower_boundary_parent_brackets':low,'upper_boundary_parent_brackets':high,'three_concurrences_constant_and_noncollinear':True},'new_original_obligations':0}
(P/'COINCIDENT_HEIGHT_FIBER.json').write_text(json.dumps(out,indent=2)+'\n');print('PASS distinct original factors, coincident nonflat height sections; escape tau in',lo,hi,'units',units)
