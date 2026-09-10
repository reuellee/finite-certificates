import sympy as S,json,itertools,random
from pathlib import Path
P=Path(__file__).resolve().parent
vs=S.symbols('a b c d e f g h i');a,b,c,d,e,f,g,h,i=vs
Y=S.Matrix([[1,0,0,0,1,1,1,1],[0,1,0,0,1,a,d,g],[0,0,1,0,1,b,e,h],[0,0,0,1,1,c,f,i]])
def normal(T):
 return S.Matrix([(-1)**(r+3)*Y[[k for k in range(4)if k!=r],[j-1 for j in T]].det()for r in range(4)])
def derived(s):return S.factor(S.Matrix.hstack(*(normal(tuple(map(int,t)))for t in s.split('/'))).det())
p='123/145/246/378';q='567/158/268/347';f1=derived(p);f2=derived(q)
print('Two exact factors reconstructed',flush=True)
# canonical50 solved d = (b*i+f*g-b*f)/i, i nonzero parent bracket.
dsol=S.solve(f1,d)[0];rest=S.factor(f2.subs(d,dsol));print('Canonical pivot eliminated',flush=True)
(P/'HARD_PAIR_EQUATIONS.json').write_text(json.dumps({'P':p,'Q':q,'variables':list(map(str,vs)),'f':str(f1),'g':str(f2),'solve_d':str(dsol),'substituted_g':str(rest)},indent=2)+'\n')
# Seek one actual rational point with the shared3regular support. Solve affine remaining variable when possible.
rng=random.Random(20260910);found=None
for k in range(300):
 fix={v:S.Integer(rng.randrange(-8,9))for v in [a,b,c,e,f,g,i]};
 if not fix[i]:continue
 expr=S.factor(rest.subs(fix));roots=S.solve(expr,h)
 for hv in roots:
  if not hv.is_Rational:continue
  sub=fix|{h:hv};sub[d]=S.cancel(dsol.subs(sub));YY=Y.subs(sub)
  br=[S.det(YY[:,J])for J in itertools.combinations(range(8),4)]
  if all(v!=0 for v in br):
   found={'attempt':k+1,'point':[str(sub[v])for v in vs],'parent':[[str(x)for x in YY.row(r)]for r in range(4)],'parent_bracket_signs':[int(S.sign(v))for v in br],'nonzero_brackets':70,'factor_ranks':[S.Matrix.hstack(*(normal(tuple(map(int,t)))for t in z.split('/'))).subs(sub).rank()for z in [p,q]]};break
 if found:break
print('FOUND',found,flush=True)
if found:(P/'HARD_PAIR_DISCOVERY_POINT.json').write_text(json.dumps(found,indent=2)+'\n')
