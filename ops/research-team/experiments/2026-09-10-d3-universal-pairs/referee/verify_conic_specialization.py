"""Independent conic-fiber replay: rational determinants and exact real-root isolation.

Uses SymPy only for univariate Q-polynomial arithmetic and certified isolation.
No producer modules, stored parametrization, roots, or inequalities are imported.
"""
from pathlib import Path
from itertools import combinations, permutations
from fractions import Fraction as F
import json
import sympy as S

ROOT = Path(__file__).resolve().parent.parent
T = S.Symbol('t')
P = ((1,2,3),(1,4,5),(2,4,6),(3,7,8))
Q = ((5,6,7),(1,5,8),(2,6,8),(3,4,7))


def det(a):
    n = len(a)
    answer = F(0)
    for p in permutations(range(n)):
        v = F(-1 if sum(p[i] > p[j] for i in range(n) for j in range(i+1,n)) % 2 else 1)
        for i in range(n):
            v *= a[i][p[i]]
        answer += v
    return answer


def geometry(c,h,i):
    return list(map(lambda row:list(map(F,row)),[
        [1,0,0,0,1,1,1,1],
        [0,1,0,0,1,7,F(-17,4),-F(5,4)*i-8],
        [0,0,1,0,1,-8,2,h],
        [0,0,0,1,1,c,-3,i]]))


def normal(y,triple):
    return [(-1)**(r+3)*det([[y[k][j-1] for j in triple] for k in range(4) if k!=r]) for r in range(4)]


def bracket(y,cols):
    return det([[y[r][j] for j in cols] for r in range(4)])


def rational(x):
    return S.Rational(x.numerator,x.denominator)


def run_case(cv,expected):
    def quad(h,i):
        y = geometry(cv,F(h),F(i))
        assert det([normal(y,tr) for tr in P]) == 0
        return det([normal(y,tr) for tr in Q])
    z = quad(0,0)
    aa = (quad(1,0)+quad(-1,0))/2-z
    dd = (quad(1,0)-quad(-1,0))/2
    cc = (quad(0,1)+quad(0,-1))/2-z
    ee = (quad(0,1)-quad(0,-1))/2
    bb = quad(1,1)-aa-cc-dd-ee-z
    assert 4*aa-6*bb+9*cc+2*dd-3*ee+z == 0
    determinant = det([[aa,bb/2,dd/2],[bb/2,cc,ee/2],[dd/2,ee/2,z]])
    assert determinant != 0
    alpha = S.Poly(rational(aa)*T*T+rational(bb)*T+rational(cc),T)
    beta = S.Poly(rational(4*aa-3*bb+dd)*T+rational(2*bb-6*cc+ee),T)
    assert S.gcd(alpha,beta).degree() == 0
    # h=2-tu, i=-3-u, u=beta/alpha is the second intersection of a line through the excluded parent7.
    hnum = 2*alpha - S.Poly(T,T)*beta
    inum = -3*alpha-beta
    assert (rational(aa)*hnum*hnum+rational(bb)*hnum*inum+rational(cc)*inum*inum+
            rational(dd)*hnum*alpha+rational(ee)*inum*alpha+rational(z)*alpha*alpha).is_zero
    ys = [geometry(cv,F(h),F(i)) for h,i in [(0,0),(1,0),(0,1)]]
    anchor = geometry(F(-4),F(-2116,67),F(-8))
    numerators=[]
    for cols in combinations(range(8),4):
        b0,bh,bi = [bracket(y,cols) for y in ys]
        v = bracket(anchor,cols)
        assert v
        sign = 1 if v>0 else -1
        num = sign*(rational(b0)*alpha+rational(bh-b0)*hnum+rational(bi-b0)*inum)
        assert not num.is_zero
        numerators.append(num)
    # Isolate every real zero of every irreducible numerator/denominator factor exactly.
    factors={}
    for p in numerators+[alpha]:
        for factor,multiplicity in S.factor_list(p)[1]:
            factor=factor.monic()
            factors[tuple(factor.all_coeffs())]=factor
    roots=[]
    for p in factors.values():
        assert p.degree()<=2
        for interval,multiplicity in p.intervals(eps=S.Rational(1,10**25)):
            roots.append(interval)
    roots.sort(key=lambda r:r[0])
    assert all(left[1]<right[0] for left,right in zip(roots,roots[1:]))
    samples=[roots[0][0]-1]
    samples += [(left[1]+right[0])/2 for left,right in zip(roots,roots[1:])]
    samples += [roots[-1][1]+1]
    valid=[all(p.eval(t)*alpha.eval(t)>0 for p in numerators) for t in samples]
    infinity=all(p.degree()==alpha.degree() and p.LC()*alpha.LC()>0 for p in numerators)
    count=sum(valid)-(1 if infinity and valid[0] and valid[-1] else 0)
    assert count==expected
    return {'c':str(cv),'components':count,'infinity_admissible':infinity,
            'parent_inequalities_rebuilt':70,'distinct_real_cuts':len(roots),
            'accepted_rational_parameter_samples':[str(t) for t,v in zip(samples,valid) if v],
            'conic_nonsingular':True,'root_order_certified_by_disjoint_rational_intervals':True}


def component_path():
    """Certify the common t=5 conic point remains in the parent over the entire c interval."""
    C=S.Symbol('c')
    coefficients=[]
    for cv in [F(0),F(1),F(-1)]:
        def q(h,i):
            return det([normal(geometry(cv,F(h),F(i)),tr) for tr in Q])
        z=q(0,0)
        a=(q(1,0)+q(-1,0))/2-z
        d=(q(1,0)-q(-1,0))/2
        cc=(q(0,1)+q(0,-1))/2-z
        e=(q(0,1)-q(0,-1))/2
        b=q(1,1)-a-cc-d-e-z
        coefficients.append([a,b,cc,d,e,z])
    polys=[]
    for k in range(6):
        z,p,m=[v[k] for v in coefficients]
        polys.append(S.Poly(rational(z)+rational((p-m)/2)*C+rational((p+m)/2-z)*C*C,C))
    a,b,cc,d,e,z=polys
    alpha=25*a+5*b+cc
    beta=5*(4*a-3*b+d)+2*b-6*cc+e
    hp=2*alpha-5*beta;ip=-3*alpha-beta
    assert (a*hp*hp+b*hp*ip+cc*ip*ip+d*hp*alpha+e*ip*alpha+z*alpha*alpha).is_zero
    lo,hi=S.Rational(-3999,1000),S.Rational(-399,100)
    assert alpha.count_roots(lo,hi)==0
    anchor=geometry(F(-4),F(-2116,67),F(-8))
    count=0
    for cols in combinations(range(8),4):
        linear=[]
        for h,i in [(0,0),(1,0),(0,1)]:
            zero=bracket(geometry(F(0),F(h),F(i)),cols)
            one=bracket(geometry(F(1),F(h),F(i)),cols)
            linear.append(S.Poly(rational(zero)+rational(one-zero)*C,C))
        b0,bh,bi=linear
        sign=1 if bracket(anchor,cols)>0 else -1
        numerator=sign*(b0*alpha+(bh-b0)*hp+(bi-b0)*ip)
        assert numerator.count_roots(lo,hi)==0
        assert numerator.eval(lo)*alpha.eval(lo)>0
        count+=1
    return {'parameter':'t=5','c_interval':['-3999/1000','-399/100'],
            'all_parameter_parent_signs':count,'same_parent_component':True,
            'method':'exact conic identity and zero Sturm root counts for every parent numerator and common denominator'}


def main():
    data=json.loads((ROOT/'falsifier/CONIC_COMPONENTS.json').read_text())
    selected={r['c']:r for r in data['records']}
    cases=[(F(-3999,1000),2),(F(-399,100),1)]
    results=[]
    for cv,n in cases:
        assert selected[str(cv)]['components']==n
        results.append(run_case(cv,n))
    # Independently identify the S8-equivalent inherited residue record.
    residue=json.loads((ROOT/'checkpoint/checkpoint/coordinator/HARD_PAIR_RESIDUE.json').read_text())['residue']
    index={(tuple(sorted(map(tuple,r['anchor']))),tuple(sorted(map(tuple,r['partner'])))):i for i,r in enumerate(residue)}
    orbit_hits=[]
    for perm in permutations(range(1,9)):
        pa=tuple(sorted(tuple(sorted(perm[e-1] for e in tr)) for tr in P))
        if pa!=tuple(sorted(P)):
            continue
        qa=tuple(sorted(tuple(sorted(perm[e-1] for e in tr)) for tr in Q))
        if (pa,qa) in index:
            orbit_hits.append(index[(pa,qa)])
    assert orbit_hits
    path=component_path()
    out={'verdict':'ACCEPT_ACTUAL_FULL_CONIC_FIBER_COMPONENT_CHANGE',
         'cases':results,'inherited_residue_orbit_indices':sorted(set(orbit_hits)),
         'component_path':path,
         'producer_parametrization_and_root_lists_used':False,
         'claim':'Two actual full fibers in one fixed parent sign chamber have different component counts.',
         'excluded':'No global Hc1 class, no original D kernel, and no whole-diagonal conclusion.'}
    text=json.dumps(out,indent=2)+'\n'
    (ROOT/'referee/CONIC_SPECIALIZATION_REPLAY.json').write_text(text)
    print(text,end='')


if __name__=='__main__':
    main()
