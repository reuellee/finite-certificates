"""Independent combinatorial acceptance for the universal pair-wall subfamilies.

Reconstructs canonical support strings from the pinned source, enumerates
degree patterns by deficit multisets (not producer product enumeration),
and independently chooses maximum-degree outer labels. No producer imports.
The geometry and global kind38 identity are deductively audited separately.
"""
from pathlib import Path
from itertools import combinations, combinations_with_replacement
from collections import Counter
import hashlib,json,re

ROOT=Path(__file__).resolve().parents[1]

def degrees(support):
    c=Counter(v for row in set(map(tuple,support)) for v in row)
    return tuple(c[i] for i in range(1,9))

def acceptable(d):
    return any(x<2 for x in d) or sum(x==2 for x in d)>1

def audit(cert):
    for file,sha in cert['source_sha256'].items():
        assert hashlib.sha256((ROOT/'inputs'/file).read_bytes()).hexdigest()==sha
    source=(ROOT/'inputs/verify_derived_walls.py').read_text()
    match=re.search(r'expected_representatives\s*=\s*\((.*?)\)\.split\(\)',source,re.S)
    assert match,'source literal expected_representatives table missing'
    reps=''.join(re.findall(r'"([^"]*)"',match.group(1))).split()
    canonical={k:tuple(tuple(map(int,t)) for t in reps[k].split('/')) for k in (38,48,49,50,51)}
    assert reps[38]=='123/124/345/678'
    for support in canonical.values():
        assert len(support)==4 and all(len(set(t))==3 for t in support)
        assert max(degrees(support))<=2
    assert degrees(canonical[48]).count(0)==2
    assert degrees(canonical[49]).count(0)==1
    # Kind36's 3+4 support bound is below the first incidence total possible
    # when no label has degree<=1 and at most one has degree2.
    assert 21<23

    expected=set()
    for deficit_positions in combinations_with_replacement(range(8),4):
        counts=Counter(deficit_positions)
        if max(counts.values())<=2:
            expected.add(tuple(2-counts[i] for i in range(8)))
    assert len(expected)==266
    entries=cert['kind38_witnesses']
    assert len(entries)==266==cert['kind38_degree_cases']
    actual={tuple(e['other_degree']) for e in entries}
    assert actual==expected
    own_choices=[]
    for e in entries:
        q=tuple(e['other_degree']);ab=tuple(e['chosen_outer_pair'])
        assert len(set(ab))==2 and set(ab)<=set(range(3,9))
        support=((3,4,5),(6,7,8),(1,2,ab[0]),(1,2,ab[1]))
        upper=tuple(a+b for a,b in zip(degrees(support),q))
        assert list(upper)==e['union_degree_upper_bound'] and acceptable(upper)
        # Independent deterministic construction: use the two outer labels
        # carrying largest degree in the other support, preserving low ones.
        picked=tuple(sorted(range(3,9),key=lambda i:(-q[i-1],i))[:2])
        d=degrees(((3,4,5),(6,7,8),(1,2,picked[0]),(1,2,picked[1])))
        assert acceptable(tuple(d[i]+q[i] for i in range(8)))
        own_choices.append((q,picked))
    # Downward closure is what permits shared support triples: decreasing a
    # successful upper degree cannot destroy either a light label or the
    # existence of two degree-two labels unless it creates a light label.
    for e in entries:
        upper=e['union_degree_upper_bound']
        for i in range(8):
            if upper[i]:
                lower=upper.copy();lower[i]-=1;assert acceptable(lower)
    p=tuple(tuple(t) for t in cert['support_rigidity_canary']['P'])
    q=tuple(tuple(t) for t in cert['support_rigidity_canary']['Q'])
    assert p==canonical[50]
    permutation=dict(zip(range(1,9),(5,6,7,8,1,2,3,4)))
    assert set(q)=={tuple(sorted(permutation[i] for i in t)) for t in p}
    assert degrees(set(p)|set(q))==(3,)*8
    assert cert['support_rigidity_canary']['nonempty_original_locus']=='NOT_CHECKED'
    remaining={(49,50),(49,51),(50,50),(50,51),(51,51)}
    assert set(map(tuple,cert['remaining_factor_kind_pairs']))==remaining
    alltypes=list(combinations_with_replacement((36,38,48,49,50,51),2))
    covered=[t for t in alltypes if any(k in t for k in (36,38,48)) or t==(49,49)]
    assert set(alltypes)-set(covered)==remaining and len(covered)==16
    return {'degree_patterns':266,'factor_kind_pairs_proved':16,'factor_kind_pairs_total':21,
            'remaining_kind_pairs':sorted(remaining),
            'own_selection_digest':hashlib.sha256(json.dumps(sorted(own_choices)).encode()).hexdigest()}

def main():
    p=ROOT/'pair/FACTOR_PAIR_TEMPLATE_CERTIFICATE.json';cert=json.loads(p.read_text())
    result=audit(cert);rejected=[]
    for mutation in ('choice','bound','coverage','source','canary'):
        c=json.loads(json.dumps(cert))
        if mutation=='choice':c['kind38_witnesses'][0]['chosen_outer_pair']=[3,3]
        elif mutation=='bound':c['kind38_witnesses'][0]['union_degree_upper_bound'][0]+=1
        elif mutation=='coverage':c['kind38_witnesses'].pop()
        elif mutation=='source':c['source_sha256']['verify_derived_walls.py']='0'*64
        else:c['support_rigidity_canary']['Q'][0][0]=1
        try:audit(c)
        except AssertionError:rejected.append(mutation)
        else:raise AssertionError('accepted corrupted '+mutation)
    result.update({'status':'PASS','scope':'exact support templates; geometric deduction audited in PAIR_THEOREM_AUDIT.md',
                   'certificate_sha256':hashlib.sha256(p.read_bytes()).hexdigest(),
                   'hostile_rejections':rejected,'original_obligations_closed':0})
    print(json.dumps(result,indent=2))

if __name__=='__main__':main()
