"""Exact actual counterexample to noncollinear concurrence => vertical regularity.
No search logic is used in this checker. All determinants are reconstructed.
"""
from pathlib import Path
from itertools import combinations
import hashlib,json
import sympy as s
ROOT=Path(__file__).resolve().parents[1]
Y=s.Matrix([[1,0,0,0,1,1,1,1],[0,1,0,0,1,-1,4,7],[0,0,1,0,1,2,-5,-4],[0,0,0,1,1,3,2,5]])
SUPPORTS={'P48':('123','145','246','356'),'Q36_ordinary':('125','126','356','378'),'R49':('123','145','257','348')}
def normal(V,I):
 A=V[:,[int(j)-1 for j in I]]
 return s.Matrix([[(-1)**(3+j)*A[[k for k in range(4) if k!=j],:].det() for j in range(4)]])
def rawdet(V,K):return s.Matrix.vstack(*(normal(V,I) for I in K)).det(method='domain-ge')
def ordinary_data(V,K):
 N=s.Matrix.vstack(*(normal(V,I) for I in K))
 assert N.rank()==3 and N.det()==0
 assert all(N[list(J),:].rank()==3 for J in combinations(range(4),3))
 q=N.nullspace()[0];lam=N.T.nullspace()[0];assert all(lam)
 return N,q,lam
records={};raw={}
for name,K in SUPPORTS.items():
 N,q,lam=ordinary_data(Y,K);raw[name]=(N,q,lam)
 records[name]={'ordered_triples':K,'normal_matrix':[[str(x) for x in row] for row in N.tolist()],'concurrence':list(map(str,q)),'circuit_dependence':list(map(str,lam)),'normal_rank':N.rank(),'every_three_normals_independent':True}
p=raw['P48'][1];qs=[raw[n][1] for n in SUPPORTS]
assert s.Matrix.hstack(*qs).rank()==3
brackets={''.join(map(str,I)):Y[:,[i-1 for i in I]].det() for I in combinations(range(1,9),4)}
assert len(brackets)==70 and all(brackets.values())
Blist=[];direct=[];t=s.symbols('t')
for name in ('Q36_ordinary','R49'):
 N,q,lam=raw[name];B=s.zeros(8,4)
 for coeff,I in zip(lam,SUPPORTS[name]):
  J=[int(v)-1 for v in I]
  for a,j in enumerate(J):
   for k in range(4):
    cols=[Y[:,v] for v in J];cols[a]=s.eye(4)[:,k]
    B[j,k]+=coeff*s.Matrix.hstack(*cols,q).det()
 assert B*q==s.zeros(8,1) and Y*B==s.zeros(4,4)
 gamma=B*p;dv=[]
 for j in range(8):
  YY=Y.copy();YY[:,j]=Y[:,j]+t*p
  dv.append(s.expand(rawdet(YY,SUPPORTS[name])).coeff(t,1))
 dv=s.Matrix(dv)
 if gamma==s.zeros(8,1):assert dv==s.zeros(8,1)
 else:
  j=next(j for j in range(8) if gamma[j]);scale=s.cancel(dv[j]/gamma[j]);assert scale and dv==scale*gamma
 records[name]['full_gradient_map']=[[str(x) for x in row] for row in B.tolist()]
 records[name]['full_gradient_map_rank']=B.rank();records[name]['full_gradient_kernel']=[list(map(str,v)) for v in B.nullspace()]
 records[name]['gamma']=list(map(str,gamma));records[name]['direct_height_derivative']=list(map(str,dv))
 Blist.append(gamma);direct.append(dv)
G=s.Matrix.hstack(*Blist);D=s.Matrix.hstack(*direct)
assert G.rank()==D.rank()==1 and Blist[0]==s.zeros(8,1) and Blist[1]!=s.zeros(8,1)
# Explicit canonical ordinary occurrence relabelings.
canonicalQ=('123','124','345','567');permQ=(1,2,5,6,3,7,8,4)
canonicalR=('123','145','246','357');permR=(1,2,3,5,4,7,8,6)
def relabel(K,perm):return sorted(''.join(map(str,sorted(perm[int(v)-1] for v in I))) for I in K)
assert relabel(canonicalQ,permQ)==sorted(SUPPORTS['Q36_ordinary'])
assert relabel(canonicalR,permR)==sorted(SUPPORTS['R49'])
a,b,c,d,e,f,g,h,i=s.symbols('a b c d e f g h i')
YY=s.Matrix([[1,0,0,0,1,1,1,1],[0,1,0,0,1,a,d,g],[0,0,1,0,1,b,e,h],[0,0,0,1,1,c,f,i]])
P=a+b*c-b-c
Q=a*f-a*i-c*d*i+c*f*g-c*f+c*i+d*i-f*g
R=e-f+f*g-g
Q50=b*f-b*i+d*i-f*g
primitive={'P48':P,'Q36_ordinary':Q,'R49':R};ratios={}
units={''.join(map(str,I)):s.expand(YY[:,[j-1 for j in I]].det()) for I in combinations(range(1,9),4)}
ratio_unit_matches={}
for name,K in SUPPORTS.items():
 F=s.factor(rawdet(YY,K));rat=s.cancel(F/primitive[name]);ratios[name]=str(rat)
 if rat.free_symbols:
  matches=[(J,str(s.cancel(v/rat))) for J,v in units.items() if not s.cancel(v/rat).free_symbols and s.cancel(v/rat)!=0]
  assert matches,(name,rat)
  ratio_unit_matches[name]=matches
 assert rat!=0
 assert s.factor_list(primitive[name])[1]==[(primitive[name],1)] or s.factor_list(primitive[name])[1]==[(-primitive[name],1)]
assert all(s.gcd(primitive[A],primitive[B])==1 for A,B in combinations(primitive,2))
assert s.expand(Q-(f-i)*P-(1-c)*Q50)==0
units={''.join(map(str,I)):s.expand(YY[:,[j-1 for j in I]].det()) for I in combinations(range(1,9),4)}
unit_matches={tag:[(J,str(s.cancel(v/F))) for J,v in units.items() if not s.cancel(v/F).free_symbols and s.cancel(v/F)!=0] for tag,F in [('1-c',1-c)]}
assert unit_matches['1-c']
# Hostile controls: moving the claimed R concurrence or one parent height fails.
assert raw['R49'][0]*(raw['R49'][1]+s.Matrix([1,0,0,0]))!=s.zeros(4,1)
perturbed=Y.copy();perturbed[1,7]+=1;assert rawdet(perturbed,SUPPORTS['R49'])!=0
out={'status':'PASS_EXACT_UNIFORM_NONCOLLINEAR_VERTICAL_CRITICAL_POINT','scope':'Refutes noncollinearity=>independent height gradients; no counterexample to triple escape and no original diagonal closure.','parent_matrix':[[str(x) for x in row] for row in Y.tolist()],'all_70_parent_brackets_nonzero':True,'parent_brackets':{k:str(v) for k,v in brackets.items()},'ordinary_occurrences':records,'concurrence_span_rank':3,'vertical_gradient_rank':1,'direct_determinant_derivative_rank':1,'global_kinds':[48,36,49],'ordinary_relabelings':{'Q36_from_type37':permQ,'R49_from_type49':permR},'primitive_polynomials':{k:str(v) for k,v in primitive.items()},'raw_determinant_parent_unit_ratios':ratios,'raw_ratio_parent_bracket_matches':ratio_unit_matches,'factor_replacement_identity':'Q36=(f-i)*P48+(1-c)*Q50','factor_replacement_unit_matches':unit_matches,'hostile_controls':2,'script_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}
(ROOT/'noncollinear/NONCOLLINEAR_CRITICAL_WITNESS.json').write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps({k:out[k] for k in ['status','concurrence_span_rank','vertical_gradient_rank','direct_determinant_derivative_rank','global_kinds','raw_determinant_parent_unit_ratios']},indent=2))
