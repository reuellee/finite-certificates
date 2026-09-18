"""Exact source-specific identities and forbidden-boundary classification.
Run: python verify_exact.py
Requires SymPy. No numerical acceptance and no claim of global source closure.
"""
from pathlib import Path
from itertools import combinations
import hashlib, json, time
import sympy as s
HERE = Path(__file__).resolve().parent
TH = s.symbols('A B C D u v w t')
A,B,C,D,u,v,w,t = TH
j,y,a = s.symbols('j y a')
SOURCE_SHA = 'f0261c6e52b5bc2df61a8278926bb80cba9823f1e489b46574ff486ce4696388'

def require(ok, message):
    if not ok:
        raise AssertionError(message)

def zero(expr, message):
    require(s.cancel(expr) == 0, message)

def reconstruct():
    Y = s.Matrix([[0,0,0,1,1,1,1,1], [0,1,1,0,0,B,C,D],
                  [1,0,-1,0,A,0,-1-C,-1-D], [0,0,1,0,u,v,w,t]])
    def normal(key):
        cols = [int(x)-1 for x in key]
        return [(-1)**(i+1)*Y.extract([r for r in range(4) if r != i], cols).det()
                for i in range(4)]
    def determinant(keys):
        return s.expand(s.Matrix([normal(key) for key in keys]).det(method='domain-ge'))
    zero(determinant(['123','145','246','378']), 'anchor P')
    Q = determinant(['126','257','367','458'])
    R = determinant(['157','168','245','348'])
    br = {''.join(str(i+1) for i in c):s.expand(Y[:,c].det())
          for c in combinations(range(8),4)}
    return Q,R,br

def source_path():
    local = HERE/'source_chart.json'
    if local.exists():
        return local
    sibling = HERE.parent/'2026-09-10-d3-critical-geometry'/'noncollinear'/'survivor_CONTRACTION_CHART.json'
    if sibling.exists():
        return sibling
    raise FileNotFoundError('Source chart missing. Restore the checkpoint or use the complete research branch.')

def run():
    start=time.monotonic()
    path=source_path()
    require(hashlib.sha256(path.read_bytes()).hexdigest()==SOURCE_SHA,'source bytes')
    source=json.loads(path.read_text())
    Q,R,br=reconstruct()
    for name,f in [('Q',Q),('R',R)]:
        zero(f-s.sympify(source['raw_factors'][name]),'source '+name)
    for name,f in br.items():
        zero(f-s.sympify(source['parent_brackets'][name]),'bracket '+name)
    L=s.diff(R,w); U=s.diff(Q,B)
    zero(L+br['1468']*br['3458'],'L identity')
    zero(U-br['1267']*br['2458']*br['2357'],'U identity')
    F={x:s.expand(j*s.diff(Q,x)-s.diff(R,x)) for x in TH if x!=B}
    equations=[Q,R]+list(F.values())+[y*L*U-1]
    witness={A:3,B:0,C:-1,D:-3,u:3,v:1,w:0,t:-2,j:1,y:s.Rational(1,1296)}
    for f in equations:
        zero(f.subs(witness), 'corrected-system witness')
    zero_brackets=[name for name,f in br.items() if f.subs(witness)==0]
    require('1247' in zero_brackets and '1456' in zero_brackets,'forbidden witness')
    require(L.subs(witness)==18 and U.subs(witness)==72,'witness pivots')
    # Rational family, a != 0,1,-1. These exclusions are in the proof.
    family={A:a,B:0,C:-1,D:-2*a/(a-1),u:a,v:1,w:0,
            t:-(a+1)/(a-1),j:1,y:(a-1)**2/(16*a**4*(a+1))}
    for f in equations:
        zero(f.subs(family,simultaneous=True),'entire rational family')
    zero(L.subs(family,simultaneous=True)-4*a*a/(a-1),'family L')
    zero(U.subs(family,simultaneous=True)-4*a*a*(a+1)/(a-1),'family U')
    family_zero=[name for name,f in br.items() if s.cancel(f.subs(family,simultaneous=True))==0]
    # Exact identities used to prove completeness on this boundary slice.
    cut={B:0,w:0,C:-1,D:t-1}
    sub=lambda f:s.expand(f.subs(cut,simultaneous=True))
    zero(sub(Q)-A*t*v*(A+u)*(v-1),'slice Q')
    zero(sub(R)-t*u*(A+u)*(v-1),'slice R')
    zero(sub(L)+v*(A+u)*(t-1),'slice L')
    zero(sub(U)+t*v*(A+u)**2,'slice U')
    zero(sub(F[v]).subs(v,1)-t*(A+u)*(A*j-u),'v=1 multiplier relation')
    c2=cut|{v:1,u:A*j}
    zero(F[D].subs(c2,simultaneous=True)+A*j*(A*j*t+A-t+1),'slice D equation')
    zero(F[w].subs(c2,simultaneous=True)+A*(A*j*j+A*j*t-t+1),'slice w equation')
    # New low-degree consequences from logarithmic vector fields.
    VQ=A*D*s.diff(Q,D)+(A*t+u)*s.diff(Q,t)
    VR=A*D*s.diff(R,D)+(A*t+u)*s.diff(R,t)
    WQ=C*s.diff(Q,C)+(w-u)*s.diff(Q,w)
    WR=C*s.diff(R,C)+(w-u)*s.diff(R,w)
    zero(VQ-A*Q,'V(Q)=A Q'); zero(WR-R,'W(R)=R')
    E=s.cancel((2*A*R-VR)/u).expand()
    require(s.Poly(E,*TH).total_degree()<=5,'polynomial consequence E')
    zero(u*E-(A*D*F[D]+(A*t+u)*F[t]-j*A*Q+2*A*R),'E certificate')
    zero(j*WQ-(C*F[C]+(w-u)*F[w]+R),'WQ certificate')
    zero(br['1245']+u,'u is a parent unit')
    zero(F[w].subs(j,0)+L,'j=0 excluded on genuine domain')
    # Authenticate the complete set of parent factors, not a guessed subset.
    factors={}
    for name, f in br.items():
        for g,power in s.factor_list(f,*TH)[1]:
            monic=s.Poly(g,*TH,domain=s.QQ).monic().as_expr()
            factors.setdefault(str(monic),[]).append(name)
    require(len(factors)==61,'complete 61-factor localization')
    factor_path=HERE/'PARENT_FACTORS.json'
    if factor_path.exists():
        saved={str(s.Poly(s.sympify(x['factor']),*TH,domain=s.QQ).monic().as_expr())
               for x in json.loads(factor_path.read_text())}
        require(saved==set(factors),'saved parent factors')
    # Reject corrupted witnesses and corrupted identities.
    bad=witness|{y:s.Rational(1,1295)}
    require(any(s.cancel(f.subs(bad))!=0 for f in equations),'bad inverse rejected')
    bad=witness|{j:2}
    require(any(s.cancel(f.subs(bad))!=0 for f in equations),'bad multiplier rejected')
    require(s.expand(VQ+A*Q)!=0,'wrong vector-field identity rejected')
    return {'status':'PASS','source_chart_sha256':SOURCE_SHA,'parent_brackets':70,
            'parent_factors':61,'exact_witness':{str(k):str(val) for k,val in witness.items()},
            'witness_L':18,'witness_U':72,'witness_zero_brackets':zero_brackets,
            'family':{str(k):str(val) for k,val in family.items()},'family_excluded_parameters':['0','1','-1'],
            'family_identically_zero_brackets':family_zero,
            'boundary_slice_classification':'All solutions on B=w=0,C=-1,D=t-1 classified by the written proof',
            'corrected_partial_unit_target':'NONEMPTY over Q; unit certificate impossible',
            'logarithmic_vector_field_identities':'PASS',
            'augmented_consequence_degrees':[int(s.Poly(E,*TH).total_degree()),int(s.Poly(WQ,*TH).total_degree())],
            'negative_controls':3,'parent_localized_target':'OPEN','whole_authenticated_triple':'OPEN',
            'original_ledger':'2/9','new_source_orbit_credit':0,'independent_referee':False,
            'seconds':time.monotonic()-start}

if __name__=='__main__':
    result=run()
    (HERE/'EXACT_REPLAY.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2))
