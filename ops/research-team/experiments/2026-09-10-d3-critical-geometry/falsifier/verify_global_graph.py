from pathlib import Path
from itertools import combinations
import json,sympy as S
Pth=Path(__file__).resolve().parent;a,b,c,d,e,f,g,h,i=S.symbols('a b c d e f g h i');xs=(a,b,c,d,e,f,g,h,i)
Y=S.Matrix([[1,0,0,0,1,1,1,1],[0,1,0,0,1,a,d,g],[0,0,1,0,1,b,e,h],[0,0,0,1,1,c,f,i]])
Ks={'P':['123','145','246','356'],'Q':['123','146','248','378'],'R':['126','145','248','378']}
raw={}
for name,K in Ks.items():
 M=S.Matrix([[(-1)**(r+3)*Y[[k for k in range(4)if k!=r],[int(j)-1 for j in J]].det()for r in range(4)]for J in K]);raw[name]=S.factor(M.det(method='domain-ge'))
P=a+b*c-b-c;Q=-a*f*h+a*h*i-b*d*i+b*f*g;R=-b*d*i+b*f*g-b*f*h+b*h*i+c*d*h-c*g*h
assert all(S.expand(raw[k]-v)==0 for k,v in {'P':P,'Q':Q,'R':R}.items())
D=b*d-b*f*(b-1)-a*h;G=b*g-b*i*(b-1)-a*h
identities={'Q=fG-iD':Q-f*G+i*D,'b(R-Q)=ch(D-G)+bh(f-i)P':b*(R-Q)-c*h*(D-G)-b*h*(f-i)*P}
assert all(S.expand(v)==0 for v in identities.values())
brackets={''.join(str(j+1)for j in J):S.factor(Y[:,J].det())for J in combinations(range(8),4)}
assert brackets['1246']==-b and brackets['1236']==c and brackets['1248']==-h and brackets['2378']==i-f
subs={a:b+c-b*c,d:f*(b-1)+(b+c-b*c)*h/b,g:i*(b-1)+(b+c-b*c)*h/b}
assert all(S.cancel(F.subs(subs,simultaneous=True))==0 for F in [P,Q,R,D,G])
point={a:-1,b:2,c:3,d:4,e:-5,f:2,g:7,h:-4,i:5};assert all(F.subs(point)!=0 for F in brackets.values());assert all(F.subs(point)==0 for F in [P,Q,R,D,G])
out={'verdict':'PASS exact global graph identities for the specific48/49/50 support triple','supports_1based':Ks,'raw_normal_determinants':{k:str(v)for k,v in raw.items()},'auxiliary_numerators':{'D':str(D),'G':str(G)},'polynomial_identity_remainders':{k:'0'for k in identities},'uniform_units':{'b':'-[1246]','c':'[1236]','h':'-[1248]','f-i':'-[2378]'},'graph':{'a':'b+c-b*c','d':'f*(b-1)+(b+c-b*c)*h/b','g':'i*(b-1)+(b+c-b*c)*h/b'},'free_coordinates':['b','c','e','f','h','i'],'all_raw_walls_vanish_on_graph':True,'actual_witness_on_graph_and_uniform':True,'scope':'Exact equivalence on every uniform parent sign residence in this standard frame; topological openR6 consequence is a deductive argument, not a sampling conclusion','new_original_obligations':0,'new_numerical_triple_credit':0}
(Pth/'GLOBAL_GRAPH_INDEPENDENT.json').write_text(json.dumps(out,indent=2)+'\n');print('PASS actual raw determinants, both ideal identities, all denominator units, and exact rational graph')
