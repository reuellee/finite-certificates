"""Export a full-source unit-pivot critical system; solver outputs are candidates."""
from pathlib import Path
import hashlib
import json
import sympy as s

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]
source=ROOT/'ai/omreal/data/DIAG3_triple_fullspace_critical_h1.json'
assert hashlib.sha256(source.read_bytes()).hexdigest()=='c9244a47ded5736e7afe724a9914e75631a22b78653442e88c14f5c397919eb8'
data=json.loads(source.read_text())
xs=s.symbols('a b c d e f g h i')
a,b,c,d,e,f,g,h,i=xs
q=[s.Add(*(s.Integer(co)*s.prod(x**p for x,p in zip(xs,mo)) for co,mo in rec['terms'])) for rec in data['equations'][:3]]
J=s.Matrix([[s.diff(z,x) for x in xs] for z in q])
assert s.factor(J[:2,[0,3]].det()) == -i*(f-1)*(h-1)*(b*f-c*e)
G=q+[s.expand(J[:,[0,3,v]].det()) for v in [2,4,5,6,7,8]]
U=i*(f-1)*(h-1)*(b*f-c*e)
out=ROOT.parent/'outputs/d3-height-cas-20260905'
out.mkdir(exist_ok=True)
def write(name,vs,gens,prime):
    body=','.join(map(str,vs))+'\n'+str(prime)+'\n'+',\n'.join(str(s.expand(z)).replace('**','^').replace(' ','') for z in gens)+'\n'
    target=out/name
    target.write_text(body,newline='\n')
    raw=target.read_bytes()
    print(name,len(raw),hashlib.sha256(raw).hexdigest(),flush=True)
write('critical_pivot_p1073741827.ms',xs,G+[U],1073741827)
write('critical_pivot_Q.ms',(*xs,s.Symbol('z')),G+[1-s.Symbol('z')*U],0)
lam,mu,z=s.symbols('lam mu z')
lagrange=q+[lam*J[0,v]+mu*J[1,v]+J[2,v] for v in range(9) if v!=1]+[1-z*U]
write('critical_lagrange_p1073741827.ms',(*xs,lam,mu,z),lagrange,1073741827)
Y=s.Matrix([[1,0,0,0,1,1,1,1],[0,1,0,0,1,a,d,g],[0,0,1,0,1,b,e,h],[0,0,0,1,1,c,f,i]])
walls={name:s.expand(Y[:,[int(k)-1 for k in name]].det()) for name in ['1468','5678']}
write('critical_pivot_more_p1073741827.ms',xs,G+[s.expand(U*s.prod(walls.values()))],1073741827)
Path(HERE/'cas_input_manifest.json').write_text(json.dumps({'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'pivot_columns':['a','d'],'height':'b','minor_columns':['c','e','f','g','h','i'],'pivot_unit':str(U),'additional_parent_units':{k:str(v) for k,v in walls.items()},'equation_terms':[len(s.Poly(z,*xs).terms()) for z in G],'role':'DISCOVERY_ONLY; NOT AN ACCEPTANCE CERTIFICATE'},indent=2)+'\n')
