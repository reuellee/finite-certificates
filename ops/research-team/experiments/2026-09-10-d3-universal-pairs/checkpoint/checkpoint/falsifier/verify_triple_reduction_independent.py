#!/usr/bin/env python3
"""Independent Sylvester-resultant and discriminant replay from original q data."""
from pathlib import Path
from itertools import permutations
import sympy as S,json,hashlib
P=Path(__file__).resolve().parent;B=P.parent
src=B/'inputs/DIAG3_triple_fullspace_critical_h1.json';D=json.loads(src.read_text());C=json.loads((B/'triple/HEIGHT_DISCRIMINANT_SYSTEM.json').read_text())
xs=S.symbols('a b c d e f g h i');a,b,c,d,e,f,g,h,i=xs;env=dict(zip(map(str,xs),xs))
qs=[sum(S.Integer(co)*S.prod(v**pw for v,pw in zip(xs,m))for co,m in r['terms'])for r in D['equations'][:3]]
# Linear d graph reconstructed by coefficient solve.
pd=S.Poly(qs[0],d);assert pd.degree()==1 and pd.nth(1)==i
ds=S.cancel(-pd.nth(0)/pd.nth(1));assert S.cancel(ds-S.sympify(C['d_graph'],locals=env))==0
F=[]
for q in qs[1:]:
 nn,dd=S.cancel(q.subs(d,ds)).as_numer_denom();assert not (set(dd.free_symbols)-{i});F.append(nn)
fc=S.Poly(F[0],c);gc=S.Poly(F[1],c);assert fc.degree()==2 and gc.degree()==1
cgraph=S.cancel(-gc.nth(0)/gc.nth(1));assert S.cancel(cgraph-S.sympify(C['c_graph'],locals=env))==0
vars7=(a,b,e,f,g,h,i)
# Resultant from its3x3 Sylvester determinant, with independent polynomial arithmetic.
zero=S.Poly(0,*vars7);A0,A1,A2=[S.Poly(fc.nth(k),*vars7)for k in [0,1,2]];B0,B1=[S.Poly(gc.nth(k),*vars7)for k in [0,1]]
M=[[A2,A1,A0],[B1,B0,zero],[zero,B1,B0]];res=zero
for p in permutations(range(3)):
 sg=(-1)**sum(p[r]>p[k]for r in range(3)for k in range(r+1,3));term=S.Poly(sg,*vars7)
 for r in range(3):term*=M[r][p[r]]
 res+=term
_,res=res.primitive()
stored=S.Poly.from_dict({tuple(m):co for co,m in C['quadratic']},vars7)
assert res==stored or res==-stored
# Bind sign to stored polynomial before discriminant; sign does not affect it.
pa=S.Poly(stored.as_expr(),a);vars6=(b,e,f,g,h,i);AA,BB,CC=[S.Poly(pa.nth(k),*vars6)for k in [2,1,0]]
Delta=BB*BB-4*AA*CC
R=S.Poly.from_dict({tuple(m):co for co,m in C['discriminant_primitive']},vars6)
U=S.Poly(g*(h-1)*(b*(i-f)+f*g-e*i),*vars6)
assert Delta==U*U*R
# All factors in U are original parent units on d graph.
assert S.cancel((b*(i-f)+f*g-e*i)-i*(d-e)).subs(d,ds).expand()==0
report={'status':'PASS_INDEPENDENT_SYLVESTER_AND_DISCRIMINANT','source_sha256':hashlib.sha256(src.read_bytes()).hexdigest(),'stored_data_sha256':hashlib.sha256((B/'triple/HEIGHT_DISCRIMINANT_SYSTEM.json').read_bytes()).hexdigest(),'d_graph_exact':True,'c_graph_exact':True,'resultant_matches_quadratic_up_to_sign':True,'quadratic_terms':len(stored.terms()),'quadratic_total_degree':stored.total_degree(),'discriminant_parent_unit_square_identity':True,'discriminant_terms':len(R.terms()),'discriminant_total_degree':R.total_degree(),'critical_generator_terms':[len(R.terms())]+[len(R.diff(v).terms())for v in vars6[1:]],'scope':'Exact algebraic reduction for one original triple; no saturation, real emptiness, or compact-component certificate'}
(P/'TRIPLE_REDUCTION_INDEPENDENT_REPLAY.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
