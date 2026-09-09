"""Build an exact whole-oval parent-bracket avoidance certificate.

SymPy is used for discovery/production. Acceptance is independently replayed
by verify_certificate.py with standard-library rational arithmetic.
"""
from pathlib import Path
from itertools import combinations
import hashlib
import json
import sympy as s

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]
SOURCE=ROOT/'ai/omreal/data/DIAG3_triple_fullspace_critical_h1.json'
PIN='c9244a47ded5736e7afe724a9914e75631a22b78653442e88c14f5c397919eb8'


def main():
    raw=SOURCE.read_bytes()
    assert hashlib.sha256(raw).hexdigest()==PIN
    payload=json.loads(raw)
    assert payload['named_presentation']==[5563,16134,19284]
    xs=s.symbols('a b c d e f g h i');a,b,c,d,e,f,g,h,i=xs
    q=[sum(s.Integer(co)*s.prod(x**n for x,n in zip(xs,ex)) for co,ex in rec['terms']) for rec in payload['equations'][:3]]
    base={b:-s.Rational(11,3),f:-s.Rational(11,4),g:-s.Rational(5,3),h:s.Rational(3,2),i:s.Rational(17,4)}
    base[d]=s.cancel((b*(i-f)+f*g)/i).subs(base)
    qa=q[1].subs(base)
    A=s.Poly(s.diff(qa,a),c,e)
    B=s.Poly(qa.subs(a,0),c,e)
    anum,aden=map(s.expand,s.fraction(s.cancel(-B.as_expr()/A.as_expr())))
    asolve=anum/aden
    final=s.cancel(q[2].subs(base).subs(a,asolve))
    fnum,fden=s.fraction(final)
    F=s.Poly(fnum,c,e).primitive()[1]
    if F.LC()<0:F=-F
    C0,C1,C2=[s.Poly(F.as_expr(),e).nth(j) for j in range(3)]
    W=s.Poly(s.expand(C1*C1-4*C0*C2),c)
    lo,hi=-s.Rational(53,25),-s.Rational(403,200)
    Y=s.Matrix([[1,0,0,0,1,1,1,1],[0,1,0,0,1,a,d,g],[0,0,1,0,1,b,e,h],[0,0,0,1,1,c,f,i]])
    records=[]
    def terms(expr,variables):
        return [[str(co),list(ex)] for ex,co in s.Poly(expr,*variables).terms()]
    for inds in combinations(range(8),4):
        label=''.join(str(j+1) for j in inds)
        wall=s.expand(Y[:,inds].det().subs(base))
        # Every determinant is affine in a, because only one column uses a.
        assert s.degree(wall,a)<=1
        num=s.expand(wall.subs(a,0)*aden+s.diff(wall,a)*anum)
        resultant=s.Poly(s.resultant(F.as_expr(),num,e),c)
        assert not resultant.is_zero,(label,'zero resultant')
        normalized=resultant.primitive()[1]
        if normalized.LC()<0:normalized=-normalized
        nroots=normalized.count_roots(lo,hi)
        print(label,'degree',normalized.degree(),'root count',nroots,flush=True)
        assert nroots==0,(label,normalized.intervals())
        records.append({'bracket':label,'wall_before_a':terms(wall,(a,c,e)),
                        'cleared_numerator':terms(num,(c,e)),
                        'resultant_primitive':terms(normalized.as_expr(),(c,)),
                        'roots_on_enclosure':int(nroots)})
    denominator_resultant=s.Poly(s.resultant(F.as_expr(),aden,e),c).primitive()[1]
    if denominator_resultant.LC()<0:denominator_resultant=-denominator_resultant
    assert denominator_resultant.count_roots(lo,hi)==0
    roots=W.intervals(eps=s.Rational(1,10000))
    assert len(roots)==4 and all(mult==1 for _,mult in roots)
    assert roots[0][0][1]<lo<roots[1][0][0]<roots[1][0][1]<roots[2][0][0]<roots[2][0][1]<hi<roots[3][0][0]
    ref_c=-s.Rational(21,10)
    ref_roots=s.Poly(F.as_expr().subs(c,ref_c),e).intervals(eps=s.Rational(1,1000000))
    assert len(ref_roots)==2 and ref_roots[0][1]==1
    ref_e=ref_roots[0][0]
    out={'schema':'d3-entire-parent-interior-oval-v1','status':'CANDIDATE_EXACT_CERTIFICATE',
         'source_sha256':PIN,'named_presentation':payload['named_presentation'],
         'base':{str(k):str(v) for k,v in base.items()},
         'a_numerator':terms(anum,(c,e)),'a_denominator':terms(aden,(c,e)),
         'F':terms(F.as_expr(),(c,e)),'W':terms(W.as_expr(),(c,)),
         'W_root_intervals':[[str(t) for t in endpoints] for endpoints,mult in roots],
         'oval_c_enclosure':[str(lo),str(hi)],
         'reference_point':{'c':str(ref_c),'e_root_interval':[str(v) for v in ref_e]},
         'C2':terms(C2,(c,)),
         'denominator_resultant_primitive':terms(denominator_resultant.as_expr(),(c,)),
         'brackets':records,
         'claims':['The selected smooth compact oval lies entirely in one uniform parent sign cell.',
                   'All-base fixed-base-fiber noncompactness is false.'],
         'nonconsequences':['No compact component of the full six-dimensional source.',
                            'No actual triple-bad compact component.',
                            'No decrease of source residual or proof of diagonal3.']}
    (HERE/'certificate.json').write_text(json.dumps(out,indent=2)+'\n')
    print('CERTIFICATE_WRITTEN',flush=True)


if __name__=='__main__':main()
