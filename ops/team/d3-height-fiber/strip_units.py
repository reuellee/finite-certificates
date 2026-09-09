"""Strip only exactly matched parent-bracket factors from critical generators."""
from pathlib import Path
import json
import sympy as s
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]
data=json.loads((ROOT/'ai/omreal/data/DIAG3_triple_fullspace_critical_h1.json').read_text())
xs=s.symbols('a b c d e f g h i')
a,b,c,d,e,f,g,h,i=xs
Y=s.Matrix([[1,0,0,0,1,1,1,1],[0,1,0,0,1,a,d,g],[0,0,1,0,1,b,e,h],[0,0,0,1,1,c,f,i]])
from itertools import combinations
walls={''.join(str(k+1) for k in I):s.Poly(Y[:,I].det(),*xs) for I in combinations(range(8),4)}
def norm(p):return p.monic().as_expr()
known={norm(p):label for label,p in walls.items() if p.total_degree()>0}
records=[r for r in data['equations'] if r['kind']=='factor' or (0 in r.get('columns',[]) and 3 in r.get('columns',[]))]
out=[]
for record in records:
    q=s.Add(*(s.Integer(co)*s.prod(x**p for x,p in zip(xs,mo)) for co,mo in record['terms']))
    scalar,factors=s.factor_list(q)
    kept=scalar;removed=[]
    for fac,power in factors:
        label=known.get(norm(s.Poly(fac,*xs)))
        if label:
            removed.append([label,power])
        else:kept*=fac**power
    kept=s.expand(kept)
    row={'source':{k:v for k,v in record.items() if k!='terms'},'before':len(s.Poly(q,*xs).terms()),'after':len(s.Poly(kept,*xs).terms()),'removed_parent_factors':removed,'primitive':str(kept)}
    out.append(row)
    print({k:v for k,v in row.items() if k!='primitive'},flush=True)
(HERE/'stripped_units.json').write_text(json.dumps(out,indent=2)+'\n')
