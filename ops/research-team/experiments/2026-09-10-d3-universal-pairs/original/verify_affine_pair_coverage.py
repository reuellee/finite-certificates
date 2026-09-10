"""Exact combinatorial applicability audit; no sampling of parent geometry."""
from collections import Counter
from pathlib import Path
import hashlib
import json

ROOT=Path(__file__).resolve().parents[1]
SOURCE=ROOT/'checkpoint/checkpoint/coordinator/HARD_PAIR_RESIDUE.json'
OUTPUT=ROOT/'original/AFFINE_PAIR_COVERAGE.json'

def eligible_labels(P,Q):
    return [e for e in range(1,9)
            if sum(e in I for I in P)==1 and sum(e in I for I in Q)==1]

def main():
    data=json.loads(SOURCE.read_text())
    assert data['remaining']==574 and len(data['residue'])==574
    covered=[];remaining=[];counts=Counter()
    for index,row in enumerate(data['residue']):
        P={tuple(I) for I in row['anchor']}
        Q={tuple(I) for I in row['partner']}
        assert len(P)==len(Q)==4 and all(len(set(I))==3 for I in P|Q)
        assert all(1<=sum(e in I for I in R)<=2 for e in range(1,9) for R in (P,Q))
        degrees=[sum(e in I for I in P|Q) for e in range(1,9)]
        assert degrees==row['degree']
        labels=eligible_labels(P,Q)
        if labels:
            covered.append(dict(row,source_index=index,forgotten_label=labels[0]))
            counts[tuple(row['kinds'])+('covered',)]+=1
        else:
            assert degrees==[3]*8
            remaining.append(dict(row,source_index=index))
            counts[tuple(row['kinds'])+('remaining',)]+=1
    assert len(covered)==529 and len(remaining)==45
    assert counts==Counter({(50,50,'covered'):238,(50,50,'remaining'):19,
                           (50,51,'covered'):233,(50,51,'remaining'):16,
                           (51,51,'covered'):58,(51,51,'remaining'):10})
    # Hostile canary: the actual balanced hard conic pair is not affine in
    # any parent column for both defining determinants at once.
    P={(1,2,3),(1,4,5),(2,4,6),(3,7,8)}
    Q={(5,6,7),(1,5,8),(2,6,8),(3,4,7)}
    assert eligible_labels(P,Q)==[]
    # No incorrect union-degree-only shortcut: check quartet multiplicities.
    assert 1 not in eligible_labels({(1,2,3),(1,4,5)},{(2,3,4),(2,5,6)})
    out={'status':'PASS_EXACT_AFFINE_APPLICABILITY_PARTITION',
         'source':str(SOURCE.relative_to(ROOT)),
         'source_sha256':hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
         'newly_covered_count':529,'remaining_count':45,
         'newly_covered':covered,'remaining':remaining,
         'scope':'Applicability of the deductive affine-pair theorem to inherited complete orbit representatives; not original D injectivity'}
    OUTPUT.write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps({k:v for k,v in out.items() if k not in ('newly_covered','remaining')},indent=2))

if __name__=='__main__':main()
