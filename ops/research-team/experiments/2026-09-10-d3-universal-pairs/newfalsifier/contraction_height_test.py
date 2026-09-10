from pathlib import Path
import itertools,json
import sympy as S
P=Path(__file__).resolve().parent;Q=S.Rational
Y=S.Matrix([[1,0,0,0,1,1,1,1],[0,1,0,0,1,7,-Q(17,4),2],[0,0,1,0,1,-8,2,-Q(2116,67)],[0,0,0,1,1,-4,-3,-8]])
Psets=[(1,2,3),(1,4,5),(2,4,6),(3,7,8)];Qsets=[(5,6,7),(1,5,8),(2,6,8),(3,4,7)]
def n(M,tr):
 return S.Matrix([[(-1)**(r+3)*M[[k for k in range(4)if k!=r],[x-1 for x in tr]].det()for r in range(4)]])
NP=S.Matrix.vstack(*(n(Y,tr)for tr in Psets));NQ=S.Matrix.vstack(*(n(Y,tr)for tr in Qsets))
assert NP.det()==NQ.det()==0
assert all(NP[list(k),:].rank()==NQ[list(k),:].rank()==3 for k in itertools.combinations(range(4),3))
p=NP.nullspace()[0];q=NQ.nullspace()[0];assert S.Matrix.hstack(p,q).rank()==2
co=NP[:3,:].T.gauss_jordan_solve(NP[3,:].T)[0];assert all(co)
Arows=S.diag(*co)*NP[:3,:];assert sum((Arows[k,:]for k in range(3)),S.zeros(1,4))==NP[3,:]
hr=next(S.eye(4)[k,:]for k in range(4)if p[k]!=0)
G=Arows.col_join(hr);assert G.det()!=0
M=G*Y
# Positive column scalings fix one nonzero projected coordinate to its sign.
scales=[abs(next(x for x in M[:3,j]if x!=0))for j in range(8)]
M=M*S.diag(*(1/x for x in scales));A=M[:3,:];h=M[3,:]
fr=next(k for k in itertools.combinations(range(8),3)if A[:,list(k)].det()!=0)
translation=h[:,list(fr)]*A[:,list(fr)].inv();h=h-translation*A
hg=next(j for j in range(8)if j not in fr and h[j]!=0);vertical=abs(h[hg]);h=h/vertical
# Apply exactly the same shear and vertical scaling to the marked Q point.
qq=G*q;z=qq[:3,0];w=(qq[3]-(translation*z)[0])/vertical
zscale=next(x for x in z if x!=0);z=z/zscale;w=w/zscale
free=[j for j in range(8)if j not in fr and j!=hg];assert len(free)==4
xs=S.symbols('x0:4');ww=S.symbols('w');t=S.symbols('t')
hvar=h.copy()
for j,x in zip(free,xs):hvar[j]=x
MM=A.col_join(hvar);qvar=z.col_join(S.Matrix([ww]))
expr=[S.expand((n(MM,tr)*qvar)[0])for tr in Qsets]
assert all(S.Poly(e,*xs,ww).total_degree()<=1 for e in expr)
C,b=S.linear_eq_to_matrix(expr,(*xs,ww));rank=C.rank();assert rank==4
anchor=S.Matrix([h[j]for j in free]+[w]);assert C*anchor==b
ker=C.nullspace();assert len(ker)==1;direction=ker[0]
sub={x:v for x,v in zip((*xs,ww),anchor+t*direction)}
MMline=MM.subs(sub);polys=[];lower=[];upper=[]
for J in itertools.combinations(range(8),4):
 f=S.expand(MMline[:,J].det());assert S.degree(f,t)<=1
 s=S.sign(f.subs(t,0));assert s;f=S.expand(s*f);polys.append(f)
 slope=f.coeff(t);inter=f.subs(t,0)
 if slope>0:lower.append((-inter/slope,J))
 elif slope<0:upper.append((-inter/slope,J))
lo=max(x[0]for x in lower)if lower else-S.oo;hi=min(x[0]for x in upper)if upper else S.oo
assert lo<0<hi
out={'status':'PASS_ACTUAL_REMAINING_SOURCE254_CONTRACTION_HEIGHT_INTERVAL','P':Psets,'Q':Qsets,'original_parent':[[str(x)for x in Y.row(k)]for k in range(4)],'P_kernel':list(map(str,p)),'Q_kernel':list(map(str,q)),'P_and_Q_distinct':True,'projected_parent':[[str(x)for x in A.row(k)]for k in range(3)],'four_line_frame_directions':['x=0','y=0','z=0','x+y+z=0'],'height_gauge_zero_labels':[j+1 for j in fr],'height_gauge_unit_label':hg+1,'free_height_labels':[j+1 for j in free],'projected_Q_point':list(map(str,z)),'four_affine_equations':list(map(str,expr)),'coefficient_matrix':[[str(x)for x in C.row(k)]for k in range(4)],'rhs':list(map(str,b)),'rank':rank,'anchor_height_and_Q_height':list(map(str,anchor)),'affine_line_direction':list(map(str,direction)),'whole_parent_interval':[str(lo),str(hi)],'all70_signed_parent_brackets':list(map(str,polys)),'scope':'One actual remaining balanced wall pair with p!=q; supports universal proof consistency, does not prove allcases.'}
(P/'CONTRACTION_HEIGHT_TEST.json').write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps({k:out[k]for k in ['status','rank','whole_parent_interval','affine_line_direction','height_gauge_zero_labels','height_gauge_unit_label']},indent=2))
