"""Standard-library independent check of the scoped tangent-cone census.

Reconstructs signed normals and their derivatives from source parent data,
then derives all cones and reduced component restrictions. Imports no
producer code. This certifies only the explicit linearized planar model.
"""
from fractions import Fraction as F
from itertools import combinations, product, permutations
from pathlib import Path
from math import gcd, lcm
import hashlib, json

ROOT=Path(__file__).resolve().parents[1]

def determinant(a):
    n=len(a); out=F(0)
    for p in permutations(range(n)):
        value=F((-1)**sum(p[i]>p[j] for i in range(n) for j in range(i+1,n)))
        for i in range(n): value*=a[i][p[i]]
        out+=value
    return out

def rank(a,cols=None):
    a=[[F(x) for x in r] for r in a]
    n=len(a); m=len(a[0]) if n else (cols or 0); lead=0
    for c in range(m):
        pivot=next((r for r in range(lead,n) if a[r][c]),None)
        if pivot is None: continue
        a[lead],a[pivot]=a[pivot],a[lead]
        value=a[lead][c];a[lead]=[x/value for x in a[lead]]
        for r in range(n):
            if r!=lead:
                value=a[r][c];a[r]=[x-value*y for x,y in zip(a[r],a[lead])]
        lead+=1
    return lead

def primitive(v):
    mult=lcm(*(x.denominator for x in v));ints=[int(x*mult) for x in v]
    div=gcd(*ints);return tuple(x//div for x in ints)

def dot(a,b):return sum(x*y for x,y in zip(a,b))
def cross(a,b):return a[0]*b[1]-a[1]*b[0]

def derive_normal(y,triple):
    return [(-1)**(r+3)*determinant([[y[i][j] for j in triple] for i in range(4) if i!=r]) for r in range(4)]

def derive_last(y,d,triple):
    total=F(0)
    for replaced in range(3):
        a=[[d[i][j] if k==replaced else y[i][j] for k,j in enumerate(triple)] for i in range(3)]
        total+=determinant(a)
    return total

def components(grid,cones):
    def bad(point):return all(any(dot(ray,point)<=0 for ray in cone) for cone in cones)
    n=len(grid);vertices={i for i,p in enumerate(grid) if bad(p)}
    parent={i:i for i in vertices}
    def find(x):
        while parent[x]!=x:x=parent[x]
        return x
    for i in range(n):
        j=(i+1)%n
        midpoint=tuple(grid[i][k]+grid[j][k] for k in range(2))
        if bad(midpoint):
            assert i in vertices and j in vertices
            parent[find(i)]=find(j)
    classes={}
    for i in vertices:classes.setdefault(find(i),[]).append(i)
    return sorted(sorted(c) for c in classes.values())

def audit(record,source):
    y=[[F(x) for x in row] for row in source['parent']]
    directions=[[[F(x) for x in row] for row in source[key]] for key in ('perturbation','good_direction')]
    all_triples=sorted(combinations(range(8),3),key=lambda t:t[::-1]);sigma=int(source['signature_integer'])
    assert [all_triples.index(tuple(t)) for t in source['center_zero_triples']]==source['center_zero_support']
    actual=[];derivatives=[]
    for triple_list in source['center_zero_triples']:
        triple=tuple(triple_list);idx=all_triples.index(triple);sign=1 if (sigma>>idx)&1 else -1
        normal=[sign*x for x in derive_normal(y,triple)]
        assert normal[-1]==0
        actual.append(normal[:3])
        derivatives.append([sign*derive_last(y,d,triple) for d in directions])
    assert actual==[[F(x) for x in row] for row in record['active_spatial_normals']]
    k=[[F(x) for x in row] for row in record['K']]
    assert rank(actual)==3 and rank(k)==2
    assert all(sum(actual[i][j]*k[i][r] for i in range(5))==0 for j in range(3) for r in range(2))
    param=[[sum(k[i][r]*derivatives[i][c] for i in range(5)) for c in range(2)] for r in range(2)]
    assert param==[[F(x) for x in row] for row in record['parameter_map']]
    assert determinant(param)==F(record['parameter_map_determinant'])!=0

    candidate=set()
    for row in k:
        for sign in (-1,1):candidate.add(primitive((sign*row[1],-sign*row[0])))
    signs=[];cones=[];counts={0:0,1:0,2:0}
    for s in product((-1,1),repeat=5):
        rays=sorted(ray for ray in candidate if all(s[i]*dot(k[i],ray)>=0 for i in range(5)))
        if len(rays)==2 and cross(*rays)!=0:
            assert all(s[i]*dot(k[i],tuple(rays[0][j]+rays[1][j] for j in range(2)))>0 for i in range(5))
            signs.append(list(s));cones.append(rays);counts[2]+=1
        else:
            assert len(rays)<=1;counts[len(rays)]+=1
    assert counts=={0:20,1:4,2:8}
    assert signs==record['signature_relative_signs']
    assert all(set(map(tuple,c))==set(r) for c,r in zip(record['positive_kernel_cone_rays'],cones))
    grid=[tuple(row) for row in record['link_rays']]
    derived_grid={primitive(tuple(sign*x for x in row)) for row in k for sign in (-1,1)}
    assert set(grid)==derived_grid and len(grid)==8
    assert all(cross(grid[i],grid[(i+1)%len(grid)])>0 for i in range(len(grid)))

    indices=list(combinations(range(8),3));assert len(record['records'])==len(indices)==56
    results=[]
    for selected,entry in zip(indices,record['records']):
        assert list(selected)==entry['indices']
        pairs=[components(grid,[cones[selected[i]],cones[selected[j]]]) for i,j in ((0,1),(0,2),(1,2))]
        triple=components(grid,[cones[i] for i in selected]);assert triple
        assert pairs==entry['pair_link_components'] and triple==entry['triple_link_components']
        rows=len(triple)-1;columns=[]
        for sign,pc in zip((1,-1,1),pairs):
            for component in pc[:-1]:
                base=int(triple[-1][0] in component)
                columns.append([sign*(int(tc[0] in component)-base) for tc in triple[:-1]])
        matrix=[[c[i] for c in columns] for i in range(rows)]
        assert matrix==entry['matrix']
        rk=rank(matrix,len(columns));nullity=len(columns)-rk
        assert rk==entry['rank'] and nullity==entry['kernel_dimension']
        assert len(columns)==entry['source_dimension'] and rows==entry['target_dimension']
        nulls=[[F(x) for x in v] for v in entry['null_vectors']]
        assert len(nulls)==nullity and rank(nulls,len(columns))==nullity
        assert all(all(dot(row,v)==0 for row in matrix) for v in nulls)
        results.append(nullity)
    assert sum(x>0 for x in results)==record['kernel_examples']==48
    assert record['empty_links']==0
    special=record['records'][indices.index((0,1,6))]
    assert special['matrix']==[[1,1]] and special['null_vectors']==[['-1','1']]
    # Actual open GOOD sectors are nonempty and incomparable within the model.
    probes=grid+[tuple(grid[i][j]+grid[(i+1)%8][j] for j in range(2)) for i in range(8)]
    good=lambda si,p:all(dot(r,p)>0 for r in cones[si])
    for i,j in permutations((0,1,6),2):assert any(good(i,p) and not good(j,p) for p in probes)
    return {'counts':counts,'triples':56,'noninjective':48,'special_matrix':[[1,1]],'special_kernel':[-1,1]}

def main():
    src_path=ROOT/'previous_checkpoint/falsifier/certificate.json'
    model_path=ROOT/'falsifier/TANGENT_AUDIT.json'
    raw=src_path.read_bytes();source=json.loads(raw);model=json.loads(model_path.read_text())
    assert hashlib.sha256(raw).hexdigest()==model['source_sha256']
    result=audit(model,source)
    corruptions=[]
    for field in ('K','active_spatial_normals','parameter_map','records'):
        changed=json.loads(json.dumps(model))
        if field=='records':changed[field][4]['matrix'][0][0]+=1
        else:changed[field][0][0]=str(F(changed[field][0][0])+1)
        try:audit(changed,source)
        except AssertionError:corruptions.append(field)
        else:raise AssertionError('accepted corrupted '+field)
    result.update({'status':'PASS','scope':'linearized planar model only; no original parent topology comparison','hostile_rejections':corruptions,'model_sha256':hashlib.sha256(model_path.read_bytes()).hexdigest(),'source_sha256':hashlib.sha256(raw).hexdigest(),'original_obligations_closed':0})
    print(json.dumps(result,indent=2))

if __name__=='__main__':main()
