"""Independent exact replay of unique-witness, distinct-weak-ray fixture.

No triple producer imports. Its lex encoding is explicitly converted to
the repository's colex encoding. Determinants use independent permutation sums.
"""
import copy
import json
from itertools import combinations
from pathlib import Path
from exact import Q,q,matrix,det,rank,colex,normals,brackets,sign,reject
from poly import trim,add,mul,scale,pdet,geometry,value

HERE=Path(__file__).resolve().parent
ROOT=HERE.parent
LEX=list(combinations(range(8),3));COLEX=colex(8,3)
L4=list(combinations(range(8),4));C4=colex(8,4)


def norm_lex(y):
    n=normals(y)
    return [n[COLEX.index(t)] for t in LEX]


def br_lex(y):
    b=brackets(y)
    return [b[C4.index(t)] for t in L4]


def dot(a,b):return sum(x*y for x,y in zip(a,b))


def positive_four_relation(rows):
    assert len(rows)==4 and rank(rows)==3
    for cols in combinations(range(4),3):
        w=[(-1)**i*det([[rows[j][k] for k in cols] for j in range(4) if j!=i]) for i in range(4)]
        if not any(w):continue
        assert all(dot(w,[rows[j][k] for j in range(4)])==0 for k in range(4))
        assert min(w)>0 or max(w)<0,'unique rank3 relation is not strictly positive'
        return [x/sum(w) for x in w]
    raise AssertionError('rank3 relation absent')


def check(j,h,curves):
    y=matrix(j['center']['Y']);n=norm_lex(y);bb=br_lex(y)
    assert bb==list(map(q,j['center']['parent_brackets'])) and len(bb)==70 and all(bb)
    assert 'lex' in j['triple_order'].lower()
    signatures=j['signatures'];assert len(signatures)==3
    rays=[];union=set();colex_ids=[];anchor_margins=[]
    for index,s in enumerate(signatures):
        assert s['index']==index
        sigma=s['signs'];assert len(sigma)==56 and all(x in (-1,1) for x in sigma)
        lexid=sum(1<<i for i,x in enumerate(sigma) if x==1)
        colexid=sum(1<<i for i,t in enumerate(COLEX) if sigma[LEX.index(t)]==1)
        assert s['signature_bits_lex']==lexid
        assert s['signature_bits_colex']==colexid;colex_ids.append(colexid)
        ids=s['support_indices'];assert len(ids)==len(set(ids))==4;union.update(ids)
        rows=[[sigma[i]*v for v in n[i]] for i in ids]
        unique=positive_four_relation(rows)
        w=list(map(q,s['positive_weights']));assert len(w)==4 and min(w)>0
        assert unique==[v/sum(w) for v in w]
        ray=list(map(q,s['weak_primal']));assert len(ray)==4 and any(ray);rays.append(ray)
        vals=[sigma[i]*dot(n[i],ray) for i in range(56)]
        assert min(vals)>=0 and max(vals)>0
        assert [i for i,v in enumerate(vals) if v==0]==s['all_zero_indices']==ids
        # Every feasible Gordan vector is supported on these four zero rows;
        # their rank3 relation is unique. Conversely positivity forces every
        # weak vector into their one-dimensional kernel, with ray sign fixed
        # by the52 strict evaluations.
        anchor=matrix(s['feasible_parent']);an=norm_lex(anchor);ab=br_lex(anchor)
        assert all(anchor[r][i]==y[r][i] for r in (0,2,3) for i in range(8))
        assert all(a*b>0 for a,b in zip(bb,ab))
        direction=[[anchor[r][i]-y[r][i] for i in range(8)] for r in range(4)]
        polynomials,_=geometry(y,direction,0)
        assert all(len(p)<=2 for p in polynomials)
        assert all(value(p,0)*value(p,1)>0 for p in polynomials)
        point=list(map(q,s['feasible_point']));margins=[sigma[i]*dot(an[i],point) for i in range(56)]
        assert min(margins)>0;anchor_margins.append(str(min(margins)))
        for other,t in enumerate(signatures):
            if other!=index:
                positive_four_relation([[t['signs'][i]*v for v in an[i]] for i in t['support_indices']])
    assert rank(rays)==3
    degrees=[sum(e in LEX[i] for i in union) for e in range(8)]
    assert degrees==[4,6,4,5,5,3,3,3]
    ell=list(map(q,h['covector']));v=list(map(q,h['direction']))
    assert all(dot(ell,p)==0 for p in rays) and dot(ell,v)==1
    heights=[dot(ell,[y[r][i] for r in range(4)]) for i in range(8)]
    assert heights==list(map(q,h['height_vector'])) and any(heights)
    equations=[]
    for s,p in zip(signatures,rays):
        for index in s['support_indices']:
            support=LEX[index];row=[Q(0)]*8
            for k,col in enumerate(support):
                m=[[y[r][i] for i in support]+[p[r]] for r in range(4)]
                for r in range(4):m[r][k]=v[r]
                row[col]=det(m)
            equations.append(row)
    assert equations==matrix(h['matrix']) and rank(equations)==h['rank']==7
    assert all(dot(row,heights)==0 for row in equations)
    assert len(h['kernel_basis'])==1
    kb=list(map(q,h['kernel_basis'][0]));assert any(kb)
    assert all(dot(row,kb)==0 for row in equations)
    assert rank([kb,heights])==1
    assert all(any(y[r][i]-v[r]*heights[i] for r in range(4)) for i in range(8))
    assert len(curves['curves'])==3
    local_radius=Q(1)
    degree_count=0
    for s,curve in zip(signatures,curves['curves']):
        assert curve['index']==s['index']
        eps=q(s['epsilon']);assert eps>0
        local_radius=min(local_radius,eps)
        anchor=matrix(s['feasible_parent'])
        direction=[[(anchor[r][i]-y[r][i])/eps for i in range(8)] for r in range(4)]
        _,np=geometry(y,direction,(1<<56)-1)
        nl=[np[COLEX.index(t)] for t in LEX]
        assert all(len(p)<=2 for row in nl for p in row)
        point=[trim(row) for row in matrix(curve['point_coefficients_ascending'])]
        assert len(point)==4 and all(len(p)<=4 for p in point)
        atzero=[p[0] for p in point];weak=list(map(q,s['weak_primal']))
        factor=next(a/b for a,b in zip(atzero,weak) if b)
        assert factor>0 and atzero==[factor*x for x in weak]
        assert [value(p,eps) for p in point]==list(map(q,s['feasible_point']))
        ids=s['support_indices'];assert pdet([nl[i] for i in ids])==[Q(0),Q(1)]
        values=[]
        for i in range(56):
            p=[Q(0)]
            for a,b in zip(nl[i],point):p=add(p,mul(a,b))
            values.append(scale(p,s['signs'][i]))
        assert [len(p)-1 for p in values]==curve['signed_value_degrees']
        for i,k in enumerate(ids):assert values[k]==[Q(0),Q([1,2,3,5][i])]
        for p in values:
            first=next(k for k,x in enumerate(p) if x)
            head=p[first];assert head>0
            tail=sum(abs(x) for x in p[first+1:])
            if tail:local_radius=min(local_radius,head/(2*tail))
            degree_count+=1
    assert local_radius>0
    return {'verdict':'ACCEPT_ACTUAL_UNIQUE_WITNESS_DISTINCT_WEAK_RAY_OBSTRUCTION',
            'colex_signature_ids':colex_ids,'lex_encoding_explicitly_converted':True,
            'all70_center_parent_brackets':True,'all56_normals_rebuilt':True,
            'positive_rank3_four_row_circuits':3,'full_normalized_witness_polytopes_are_singletons':3,
            'weak_primal_ray_rank':3,'common_nonzero_weak_vector_exists':False,
            'feasible_anchors_in_same_parent_component':3,'anchor_minimum_primal_margins':anchor_margins,
            'ordered_noninclusions_certified':6,'union_support_label_degrees':degrees,
            'union_degree_at_most2_residence_available':False,
            'fixed_three_weak_point_height_equation_rank':7,'height_kernel_dimension':1,
            'height_kernel_equals_global_GL_scale_direction':True,
            'center_in_boundary_of_each_good_locus':True,
            'primal_curve_polynomial_identities_rebuilt':True,
            'positive_curve_polynomials':degree_count,
            'common_certified_small_parameter_radius':str(local_radius),
            'actual_compact_component_or_original_cohomology_kernel_constructed':False}


def main():
    j=json.loads((ROOT/'triple/ACTUAL_UNIQUE_HARD_THREE_BOUNDARY_SIGNATURES.json').read_text())
    h=json.loads((ROOT/'triple/MULTIWEAK_HEIGHT_GATE.json').read_text())
    curves=json.loads((ROOT/'triple/BOUNDARY_CURVES.json').read_text())
    result=check(j,h,curves);controls={}
    def mutation(name,fn):
        a,b=copy.deepcopy(j),copy.deepcopy(h);fn(a,b);controls[name]=reject(lambda:check(a,b,curves))
    mutation('wrong_colex_id',lambda a,b:a['signatures'][0].__setitem__('signature_bits_colex',0))
    mutation('positive_weight_corruption',lambda a,b:a['signatures'][0]['positive_weights'].__setitem__(0,'31'))
    mutation('weak_ray_corruption',lambda a,b:a['signatures'][1]['weak_primal'].__setitem__(0,'1'))
    mutation('wrong_zero_support',lambda a,b:a['signatures'][0]['all_zero_indices'].__setitem__(0,1))
    mutation('anchor_parent_corruption',lambda a,b:a['signatures'][0]['feasible_parent'][1].__setitem__(6,'31'))
    mutation('height_matrix_corruption',lambda a,b:b['matrix'][0].__setitem__(0,'0'))
    mutation('height_direction_corruption',lambda a,b:b['direction'].__setitem__(0,'0'))
    mutation('height_rank_corruption',lambda a,b:b.__setitem__('rank',6))
    badcurve=copy.deepcopy(curves);badcurve['curves'][0]['point_coefficients_ascending'][0][0]='-61'
    controls['boundary_curve_join_corruption']=reject(lambda:check(j,h,badcurve))
    badcurve=copy.deepcopy(curves);badcurve['curves'][1]['point_coefficients_ascending'][0][1]='4'
    controls['boundary_curve_polynomial_corruption']=reject(lambda:check(j,h,badcurve))
    result['hostile_controls']=controls
    (HERE/'THREE_WEAK_OBSTRUCTION_REPLAY.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2))


if __name__=='__main__':main()
