"""Standard-library independent replay of actual-parent no-section example.

Reconstructs literal parent geometry with polynomial permutation determinants;
does not import falsifier code, SymPy, or any numerical solver.
"""
import ast
import copy
import hashlib
import json
from pathlib import Path
from exact import Q,q,matrix,colex,rank,sign,reject
from verify_constructive_independent import trim,add,mul,scale,value,pdet

HERE=Path(__file__).resolve().parent
ROOT=HERE.parent
EPS=Q(1,1000000)


def scalar_column(a):
    assert all(isinstance(r,list) and len(r)==1 for r in a)
    return [q(r[0]) for r in a]


def poly_expression(s):
    def parse(x):
        if isinstance(x,ast.Constant):
            assert type(x.value) is int
            return [Q(x.value)]
        if isinstance(x,ast.Name):
            assert x.id=='t'
            return [Q(0),Q(1)]
        if isinstance(x,ast.UnaryOp):
            assert isinstance(x.op,(ast.USub,ast.UAdd))
            return scale(parse(x.operand),-1 if isinstance(x.op,ast.USub) else 1)
        assert isinstance(x,ast.BinOp)
        a,b=parse(x.left),parse(x.right)
        if isinstance(x.op,ast.Add):return add(a,b)
        if isinstance(x.op,ast.Sub):return add(a,scale(b,-1))
        if isinstance(x.op,ast.Mult):return mul(a,b)
        if isinstance(x.op,ast.Div):
            assert len(b)==1 and b[0]
            return scale(a,1/b[0])
        assert isinstance(x.op,ast.Pow) and len(b)==1 and b[0].denominator==1 and 0<=b[0]<=10
        out=[Q(1)]
        for _ in range(int(b[0])):out=mul(out,a)
        return out
    return trim(parse(ast.parse(s,mode='eval').body))


def geometry(parent,direction,signature):
    y=[[trim([q(x),q(d)]) for x,d in zip(row,dr)] for row,dr in zip(parent,direction)]
    assert len(y)==4 and all(len(r)==8 for r in y)
    bs=[pdet([[y[r][i] for i in s] for r in range(4)]) for s in colex(8,4)]
    ns=[]
    for i,s in enumerate(colex(8,3)):
        ns.append([scale(pdet([[y[r][k] for k in s]+[[Q(r==j)]] for r in range(4)]),
                        1 if signature>>i&1 else -1) for j in range(4)])
    return bs,ns


def positive_lower_bound(p):
    bound=p[0]-sum(abs(x)*EPS**i for i,x in enumerate(p) if i)
    assert bound>0,'whole-interval positivity bound fails'
    return bound


def dot(x,y):return sum(a*b for a,b in zip(x,y))


def check(c):
    inp=ROOT/'falsifier/candidate.json'
    candidate=json.loads(inp.read_text())
    assert c['source_sha256']['candidate.json']==hashlib.sha256(inp.read_bytes()).hexdigest()
    src=ROOT/'inputs/certificates/THREE_ROW_WITNESS.json'
    assert c['source_sha256']['THREE_ROW_WITNESS.json']==hashlib.sha256(src.read_bytes()).hexdigest()
    assert c['parent']==candidate['parent'] and c['perturbation']==candidate['direction']
    sig=c['signature_integer'];assert sig==sum(1<<i for i,s in enumerate(candidate['signs']) if s==1)
    y=matrix(c['parent']);zero=[[Q(0)]*8 for _ in range(4)]
    bs,a=geometry(y,zero,sig);a0=[[x[0] for x in row] for row in a]
    assert [sign(b[0]) for b in bs]==candidate['parent_signs'] and all(b[0] for b in bs)
    z=c['center_zero_support'];assert z==candidate['zero_indices']
    assert [i for i in range(56) if a0[i][3]==0]==z
    assert c['center_zero_triples']==[list(colex(8,3)[i]) for i in z]
    assert [a0[i] for i in z]==matrix(c['center_signed_normals'])
    assert all(a0[i][3]>0 for i in range(56) if i not in z)
    az=[a0[i] for i in z];assert rank(az)==3
    r0=scalar_column(c['center_ray0']);r1=scalar_column(c['center_ray1'])
    assert len(r0)==len(r1)==5 and min(r0)>=0 and min(r1)>=0 and sum(r0)==sum(r1)==1
    assert rank([r0,r1])==2
    for r in (r0,r1):
        assert all(sum(r[k]*az[k][j] for k in range(5))==0 for j in range(4))
    # Nullity is two; zero coordinates force coefficients in this ray basis
    # nonnegative, and normalization forces their sum to one.
    assert r0[3]>0 and r1[3]==0 and r0[4]==0 and r1[4]>0
    assert r0==list(map(q,candidate['minimum_weights']))
    assert dot(r0,r0)==q(c['center_minimum_norm_squared'])
    optimal_dot=dot(r0,[b-a for a,b in zip(r0,r1)])
    assert optimal_dot==q(c['minimum_optimality_direction_dot'])>0
    assert c['same_parent_interval']=='0<=t<=1/1000000'
    families=[]
    for direction in (c['perturbation'],c['second_perturbation'],c['good_direction']):
        b,n=geometry(y,direction,sig)
        margins=[positive_lower_bound(scale(p,s)) for p,s in zip(b,candidate['parent_signs'])]
        outer=[positive_lower_bound(n[i][3]) for i in range(56) if i not in z]
        assert len(margins)==70 and len(outer)==51
        families.append((b,n,min(margins),min(outer)))
    H=matrix(c['perturbation']);H2=matrix(c['second_perturbation']);G=matrix(c['good_direction'])
    assert all(H2[i][j]==-H[i][j]+G[i][j]/89 for i in range(4) for j in range(8))
    bad_summaries=[];ds=[]
    for index,(key,limit_key,deriv_key) in enumerate((
            ('family_positive_kernel_polynomials','family_normalized_kernel_limit','zero_last_derivative'),
            ('second_positive_kernel_polynomials','second_kernel_limit','second_zero_last_derivative'))):
        n=families[index][1];f=[n[i] for i in z]
        raw=[scale(pdet([row for j,row in enumerate(f) if j!=i]),(-1)**i) for i in range(5)]
        assert all(p[0]==0 and len(p)>=2 for p in raw)
        k=[trim(p[1:]) for p in raw]
        if k[0][0]<0:k=[scale(p,-1) for p in k]
        supplied=[poly_expression(r[0]) for r in c[key]]
        assert len(supplied)==5 and k==supplied,'circuit polynomial differs from cofactors'
        kmargins=[positive_lower_bound(p) for p in k]
        for j in range(4):
            residual=[Q(0)]
            for p,row in zip(k,f):residual=add(residual,mul(p,row[j]))
            assert residual==[Q(0)],'exact kernel identity fails'
        limits=[p[0]/sum(v[0] for v in k) for p in k]
        assert limits==scalar_column(c[limit_key])
        d=[n[i][3][1] if len(n[i][3])>1 else Q(0) for i in z]
        assert d==scalar_column(c[deriv_key]);ds.append(d)
        # k is positive on the closed interval. The raw 4x4 deletion minors
        # are ±t*k, hence each is nonzero for t>0 and selected rank is four.
        bad_summaries.append({'parent_signed_bracket_bound':str(families[index][2]),
                              'outside51_last_coordinate_bound':str(families[index][3]),
                              'positive_kernel_bound':str(min(kmargins)),
                              'polynomial_kernel_identity':True,'support_rank_for_positive_t':4})
    d,d2=ds
    assert d==list(map(q,candidate['zero_derivative']))
    assert d2==[-x+Q(1,89) for x in d]
    assert dot(d,r0)==q(c['derivative_dot_center_minimum'])==Q(2,89)
    assert dot(d,r1)==q(c['derivative_dot_second_ray'])<0
    gn=families[2][1]
    for i in z:
        assert gn[i][3][0]==0 and len(gn[i][3])>=2
        positive_lower_bound(gn[i][3][1:])
    good=[[y[i][j]+EPS*G[i][j] for j in range(8)] for i in range(4)]
    assert good==matrix(c['good_parent']) and c['good_primal']==[0,0,0,1]
    good_margin=min(value(gn[i][3],EPS) for i in range(56))
    assert good_margin==q(c['good_minimum_margin'])>0
    assert c['original_obligations_closed']==0 and c['ledger']=='2/9'
    assert c['classification']=='EXACT_ACTUAL_PARENT_NO_CONTINUOUS_NORMALIZED_SECTION'
    return {'verdict':'ACCEPT_ACTUAL_PARENT_NO_LOCAL_CONTINUOUS_WITNESS_SECTION',
            'all70_center_brackets_nonzero':True,'all56_center_normals_rebuilt':True,
            'signature':sig,'center_zero_rows':z,'center_witness_polytope':'exact segment [r0,r1]',
            'center_minimum':'r0','center_optimality_dot':str(optimal_dot),
            'bad_family_checks':bad_summaries,'same_chamber_good_family_all_parameters':True,
            'good_anchor_margin':str(good_margin),'derivative_dot_center_minimum':str(dot(d,r0)),
            'incompatible_necessary_limit_bounds':['d dot w <= 0','d dot w >= 1/89'],
            'original_cohomological_obligations_closed':0,
            'fixed_historical_three_signature_family_tested':False}


def main():
    c=json.loads((ROOT/'falsifier/certificate.json').read_text())
    result=check(c);hostile={}
    def mutation(name,fn):
        x=copy.deepcopy(c);fn(x);hostile[name]=reject(lambda:check(x))
    mutation('signature_flip',lambda x:x.__setitem__('signature_integer',x['signature_integer']^1))
    mutation('zero_support_corruption',lambda x:x['center_zero_support'].__setitem__(0,1))
    mutation('center_ray_corruption',lambda x:x['center_ray0'][0].__setitem__(0,'201/267'))
    mutation('kernel_polynomial_corruption',lambda x:x['family_positive_kernel_polynomials'][0].__setitem__(0,'1'))
    mutation('second_kernel_polynomial_corruption',lambda x:x['second_positive_kernel_polynomials'][0].__setitem__(0,'1'))
    mutation('second_direction_corruption',lambda x:x['second_perturbation'][0].__setitem__(1,'-2'))
    mutation('derivative_bound_corruption',lambda x:x['second_zero_last_derivative'][0].__setitem__(0,'0'))
    mutation('good_direction_corruption',lambda x:x['good_direction'][0].__setitem__(1,'0'))
    mutation('good_primal_negation',lambda x:x.__setitem__('good_primal',[0,0,0,-1]))
    mutation('good_margin_corruption',lambda x:x.__setitem__('good_minimum_margin','1'))
    mutation('claimed_interval_corruption',lambda x:x.__setitem__('same_parent_interval','0<=t<=1'))
    mutation('center_minimum_norm_corruption',lambda x:x.__setitem__('center_minimum_norm_squared','1'))
    result['hostile_controls']=hostile
    (HERE/'FALSIFIER_REPLAY.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2))


if __name__=='__main__':main()
