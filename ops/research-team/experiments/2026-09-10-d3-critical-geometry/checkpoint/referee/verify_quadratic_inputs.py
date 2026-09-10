#!/usr/bin/env python3
"""Rebuild all22 displayed quadratic inputs from actual parent determinants.

No producer code is imported. This does not replace the separately reviewed
and cleanly replayed projective pencil coverage checker.
"""
from pathlib import Path
from itertools import combinations,permutations
import hashlib,json
import sympy as s

ROOT=Path(__file__).resolve().parent.parent
xs=s.symbols('x y z w')
Y=s.Matrix([[0,0,0,1,1,1,1,1],[0,1,1,0,0,3,4,5],
            [1,0,-1,0,2,0,-5,-6],[0,0,1,0,*xs]])

def determinant(rows):
    n=len(rows);ans=0
    for p in permutations(range(n)):
        term=(-1)**sum(p[i]>p[j] for i in range(n) for j in range(i+1,n))
        for i in range(n):term*=rows[i][p[i]]
        ans+=term
    return s.expand(ans)

def normal(js):
    return [(-1)**(i+3)*determinant([[Y[k,j] for j in js]
             for k in range(4) if k!=i]) for i in range(4)]

def canonical(expr):
    p=s.Poly(expr,*xs)
    return tuple((e,c/p.LC()) for e,c in p.terms())

def homogenized_matrix(q):
    h=s.zeros(5)
    for e,c in s.Poly(q,*xs).terms():
        indices=[i for i,k in enumerate(e) for _ in range(k)]
        indices += [4]*(2-len(indices))
        i,j=indices
        if i==j:h[i,j]+=c
        else:h[i,j]+=c/2;h[j,i]+=c/2
    return h

def check_quotient(d,q,units):
    quotient,remainder=s.div(s.Poly(d,*xs),s.Poly(q,*xs))
    assert remainder.is_zero
    assert all(canonical(f) in units for f,m in s.factor_list(quotient.as_expr())[1])
    return str(s.factor(quotient.as_expr()))

def main():
    recs=json.loads((ROOT/'falsifier/QUAD_INERTIA.json').read_text())['records']
    assert len(recs)==22 and len({r['trial'] for r in recs})==22
    brackets={''.join(str(j+1) for j in ids):determinant(Y[:,ids].tolist())
              for ids in combinations(range(8),4)}
    assert all(s.Poly(b,*xs).total_degree()<=1 and b!=0 for b in brackets.values())
    vals={k:b.subs(dict(zip(xs,(-87,-32,-78,96)))) for k,b in brackets.items()}
    assert all(v!=0 for v in vals.values())
    units={canonical(b) for b in brackets.values()}
    anchor=[(0,1,2),(0,3,4),(1,3,5),(2,6,7)]
    assert determinant([normal(js) for js in anchor])==0
    out=[];hostile=False
    for r in recs:
        q=s.sympify(r['polynomial']);assert s.Poly(q,*xs).total_degree()==2
        d=determinant([normal(js) for js in r['support_0based']])
        unit=check_quotient(d,q,units)
        h=homogenized_matrix(q)
        assert h==s.Matrix([[s.Rational(v) for v in row] for row in r['homogeneous_matrix']])
        if not hostile:
            try:check_quotient(d,q+1,units)
            except AssertionError:hostile=True
            else:raise AssertionError('Altered polynomial unexpectedly accepted')
        out.append({'trial':r['trial'],'determinant_quotient_parent_units':unit,
                    'homogeneous_matrix_rebuilt':True})
    result={'verdict':'PASS_INDEPENDENT_ALL22_ACTUAL_QUADRATIC_REBUILD',
            'quadric_count':len(out),'parent_brackets':len(brackets),
            'anchor_identity':True,'altered_polynomial_rejected':hostile,
            'records':out,'input_sha256':hashlib.sha256((ROOT/'falsifier/QUAD_INERTIA.json').read_bytes()).hexdigest(),
            'scope':'Actual determinants, parent-unit quotient equivalence, and all22 homogeneous matrices. The231-pair theorem additionally uses the reviewed clean pencil replay.'}
    (ROOT/'referee/QUADRATIC_INPUT_REPLAY.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({'verdict':result['verdict'],'quadratics':22,'hostile_rejected':hostile},sort_keys=True))

if __name__=='__main__':main()
