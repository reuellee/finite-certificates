"""Exact support applicability for the two-column affine proof."""
from collections import Counter
from itertools import combinations
from pathlib import Path
import hashlib,json
ROOT=Path(__file__).resolve().parents[1]
SOURCE=ROOT/'original/AFFINE_PAIR_COVERAGE.json'

def choices(P,Q):
    ans=[]
    for swapped,(R,T) in enumerate(((P,Q),(Q,P))):
        for I in R:
            low=[e for e in I if sum(e in J for J in R)==1]
            for e,j in combinations(sorted(low),2):
                common=[J for J in T if e in J and j in J]
                only_e=[J for J in T if e in J and j not in J]
                only_j=[J for J in T if j in J and e not in J]
                free=[J for J in T if e not in J and j not in J]
                if not all(len(v)==1 for v in (common,only_e,only_j,free)):continue
                # Type50's remaining triple normals form a triangle of
                # three distinct shared parent labels; each such shared
                # label is absent from the third triple. This certifies
                # their rank3 by the parent-unit argument in the proof.
                fixed=[set(J) for J in R if J!=I]
                meets=[fixed[a]&fixed[b] for a,b in combinations(range(3),2)]
                assert all(len(v)==1 for v in meets)
                assert len(set.union(*meets))==3
                assert not set.intersection(*fixed)
                a=next(v for v in I if v not in (e,j))
                assert any(a not in J for J in fixed)
                ans.append({'swapped':bool(swapped),'moving':[e,j],
                            'P_shared':I,'Q_shared':common[0],
                            'Q_only_e':only_e[0],'Q_only_j':only_j[0],
                            'Q_free':free[0]})
    return ans

def main():
    data=json.loads(SOURCE.read_text());rows=data['remaining'];assert len(rows)==45
    covered=[];remaining=[];counts=Counter()
    for r in rows:
        opts=choices(r['anchor'],r['partner'])
        if opts:
            covered.append(dict(r,options=opts));counts[tuple(r['kinds'])]+=1
        else:remaining.append(r)
    assert counts==Counter({(50,50):17,(50,51):10})
    assert len(covered)==27 and len(remaining)==18
    out={'status':'PASS_EXACT_TWO_COLUMN_AFFINE_APPLICABILITY',
         'source_sha256':hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
         'new_covered_count':27,'remaining_count':18,
         'covered':covered,'remaining':remaining,
         'scope':'Applicability of the deductive two-column theorem; originalD3 remains open'}
    (ROOT/'original/TWO_COLUMN_AFFINE_COVERAGE.json').write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps({k:v for k,v in out.items() if k not in ('covered','remaining')},indent=2))

if __name__=='__main__':main()
