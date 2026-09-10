#!/usr/bin/env python3
"""Exact combinatorial certificates for a conditional topological factor-pair route.

This checks only support geometry and the degree-selection statements used in
FINDINGS.md. It does not compute original pair cohomology or prove D3.
"""
from itertools import combinations, product
from pathlib import Path
import ast, hashlib, json

HERE = Path(__file__).resolve().parent
INPUT = HERE.parent / 'inputs'

def triples(s):
    return tuple(tuple(map(int, t)) for t in s.split('/'))

def degree(support):
    return tuple(sum(v in t for t in support) for v in range(1,9))

def two_dimensional(d):
    return min(d) <= 1 or sum(x == 2 for x in d) >= 2

def source_representatives():
    tree=ast.parse((INPUT/'verify_derived_walls.py').read_text())
    for stmt in tree.body:
        if isinstance(stmt,ast.Assign) and any(isinstance(x,ast.Name) and x.id=='expected_representatives' for x in stmt.targets):
            return stmt.value.func.value.value.split()
    raise AssertionError('source representative table missing')

def main():
    reps=source_representatives()
    canonical={k:triples(reps[k]) for k in (38,48,49,50,51)}
    assert {k:reps[k] for k in canonical} == {
        38:'123/124/345/678',48:'123/145/246/356',49:'123/145/246/357',
        50:'123/145/246/378',51:'123/145/267/468'}
    # All ordinary factor kinds have a global representative with max degree2.
    assert all(max(degree(p))<=2 for p in canonical.values())
    assert degree(canonical[48]).count(0)==2
    assert degree(canonical[49]).count(0)==1
    # Localization kind36 has an inherited global3-circuit. Union with any
    # other chosen support has <=7 triples and <=21 incidences. If every
    # degree>=2 and at most one degree=2, incidence is >=23, contradiction.
    assert 3*(3+4)==21 < 2+7*3
    # Kind38's15 globally equivalent occurrences, from source factor table.
    core=((3,4,5),(6,7,8))
    choices={ab:core+((1,2,ab[0]),(1,2,ab[1])) for ab in combinations(range(3,9),2)}
    # Every4-triple support of max degree2 has one of these266 labeled degree
    # vectors. Degree of a union is <=sum of the two degree vectors. The
    # light-label condition is downward closed. No realization sampling.
    cases=[]
    for q in product(range(3),repeat=8):
        if sum(q)!=12:
            continue
        hits=[]
        for ab,p in choices.items():
            upper=tuple(a+b for a,b in zip(degree(p),q))
            if two_dimensional(upper):
                hits.append((ab,upper))
        assert hits,('kind38 selection failed',q)
        cases.append({'other_degree':q,'chosen_outer_pair':hits[0][0],
                      'union_degree_upper_bound':hits[0][1]})
    assert len(cases)==266
    # Failure canary for support-plane preservation: two different type50
    # supports have a3-regular union, so there is no available light label.
    p=canonical[50]
    q=triples('567/158/268/347')
    perm=(5,6,7,8,1,2,3,4)
    assert set(q)=={tuple(sorted(perm[v-1] for v in t)) for t in p}
    d=degree(set(p)|set(q))
    assert d==(3,)*8 and not two_dimensional(d)
    # This canary is combinatorial; nonempty actual wall intersection is not
    # claimed here. It defeats only an unconditional support-degree proof.
    sources={f:hashlib.sha256((INPUT/f).read_bytes()).hexdigest() for f in (
      'DIAG3_SINGLE_BAD_TWO_SKELETON.md','verify_derived_walls.py',
      'verify_derived_wall_sides.py','DIAG3_PAIR_FACTOR_ROOT_SWITCH.md',
      'DIAG3_TRIPLE_FACTOR_REDUCTION.md','DIAG3_PAIR_DIFFERENTIAL_ENDS.md')}
    report={'status':'PASS_COMBINATORIAL_TEMPLATES_ONLY','kind38_degree_cases':len(cases),
      'covered_factor_kind_pairs':'every pair with36,38,48; additionally49+49',
      'remaining_factor_kind_pairs':[[49,50],[49,51],[50,50],[50,51],[51,51]],
      'source_sha256':sources,'kind38_witnesses':cases,
      'support_rigidity_canary':{'P':p,'Q':q,'degree':d,'nonempty_original_locus':'NOT_CHECKED'},
      'original_D':'OPEN','original_D3':'OPEN','ledger':'2/9'}
    (HERE/'FACTOR_PAIR_TEMPLATE_CERTIFICATE.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps({k:v for k,v in report.items() if k not in ('kind38_witnesses','source_sha256')},indent=2))

if __name__=='__main__':
    main()
