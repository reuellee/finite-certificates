"""Recover two named ordinary factor occurrences from targeted exact wall parents.
This does not rebuild the factor/triple orbit census.
"""
from pathlib import Path
from itertools import combinations
from collections import defaultdict
from math import gcd,lcm
from functools import reduce
import sympy as s,json,random,hashlib
ROOT=Path(__file__).resolve().parents[1]
SRC=ROOT/'checkpoint/checkpoint/checkpoint/checkpoint/inputs/DIAG3_triple_fullspace_critical_h1.json'
source=json.loads(SRC.read_text());vs=s.symbols(' '.join(source['variables']));a,b,c,d,e,f,g,h,i=vs
polys={o['factor']:s.Poly.from_dict({tuple(m):co for co,m in o['terms']},vs).as_expr() for o in source['equations'] if o['kind']=='factor'}
GEN=s.Matrix([[1,0,0,0,1,1,1,1],[0,1,0,0,1,a,d,g],[0,0,1,0,1,b,e,h],[0,0,0,1,1,c,f,i]])
TR=[''.join(map(str,I)) for I in combinations(range(1,9),3)]
def normal(Y,I):
 A=Y[:,[int(j)-1 for j in I]]
 return s.Matrix([[(-1)**(3+j)*A[[k for k in range(4) if k!=j],:].det() for j in range(4)]])
def prim(v):
 dl=lcm(*[s.denom(x) for x in v]);v=[int(x*dl) for x in v];dd=reduce(gcd,map(abs,v));v=tuple(x//dd for x in v)
 return tuple(-x for x in v) if next(x for x in v if x)<0 else v

def det3(a,b,c):return a[0]*(b[1]*c[2]-b[2]*c[1])-a[1]*(b[0]*c[2]-b[2]*c[0])+a[2]*(b[0]*c[1]-b[1]*c[0])
def cross(a,b,c):return tuple((-1)**j*det3([a[k] for k in range(4) if k!=j],[b[k] for k in range(4) if k!=j],[c[k] for k in range(4) if k!=j]) for j in range(4))
def wall_parent(F,pivot,seed):
 rng=random.Random(seed)
 for attempt in range(16):
  sub={v:s.Integer(rng.randrange(-11,12)) for v in vs if v!=pivot};one=s.Poly(F.subs(sub),pivot)
  if one.degree()!=1:continue
  sub[pivot]=-one.nth(0)/one.nth(1);Y=GEN.subs(sub)
  if all(Y[:,list(J)].det() for J in combinations(range(8),4)):return Y,sub,attempt+1
 raise RuntimeError('no uniform parent in targeted budget')
def recover(Y,target):
 N=[prim(normal(Y,I)) for I in TR];parents={prim(Y[:,j]) for j in range(8)};flats=defaultdict(set)
 for J in combinations(range(56),3):
  q=cross(*[N[j] for j in J])
  if not any(q):continue
  q=prim(q)
  if q not in parents:flats[q].update(J)
 candidates=[]
 for q,inds in flats.items():
  if len(inds)<4:continue
  for J in combinations(sorted(inds),4):
   if not all(any(cross(*[N[j] for j in K])) for K in combinations(J,3)):continue
   K=tuple(TR[j] for j in J);raw=s.factor(s.Matrix.vstack(*(normal(GEN,I) for I in K)).det(method='domain-ge'))
   quotient=s.cancel(raw/target)
   if quotient.as_numer_denom()[1]!=1:continue
   if quotient and quotient.free_symbols==set():return K,quotient,q,len(candidates)
   # If a parent-unit quotient occurs, verify factor-by-factor against the70 brackets.
   if quotient:
    rest=quotient
    for I in combinations(range(8),4):
     unit=s.factor(GEN[:,list(I)].det())
     if not unit.free_symbols:continue
     while s.rem(rest,unit,*vs)==0:rest=s.cancel(rest/unit)
    if not rest.free_symbols:return K,quotient,q,len(candidates)
   candidates.append(K)
 raise RuntimeError(('no symbolic ordinary match',len(candidates)))
results=[]
for ident,pivot in [(16134,a),(19284,c)]:
 Y,sub,attempts=wall_parent(polys[ident],pivot,ident)
 K,ratio,q,rejected=recover(Y,polys[ident])
 row={'factor':ident,'pivot':str(pivot),'ordinary_support':K,'raw_to_named_ratio':str(ratio),'sample_parent':[[str(x) for x in row] for row in Y.tolist()],'sample_substitution':{str(k):str(v) for k,v in sub.items()},'sample_concurrence':list(map(str,q)),'parent_constructions':attempts,'prior_nonmatches':rejected}
 results.append(row);print(json.dumps({k:row[k] for k in ('factor','ordinary_support','raw_to_named_ratio','parent_constructions','prior_nonmatches')},indent=2),flush=True)
out={'status':'PASS_EXACT_ORDINARY_RECOVERY','source_sha256':hashlib.sha256(SRC.read_bytes()).hexdigest(),'canonical_row':source['canonical_row'],'named_presentation':source['named_presentation'],'P_support':['123','145','246','378'],'recovered':results,'scope':'Two targeted wall parents and exact symbolic occurrence identities; no triple closure.'}
(ROOT/'noncollinear/survivor_ORDINARY_SUPPORTS.json').write_text(json.dumps(out,indent=2)+'\n')
