"""Independent BFS/union-find orbit audit of the remaining support criterion.

Uses bitset supports, generates labeled objects by adjacent-transposition
closure, then quotients partners by explicit equivalence edges. Producer
uses full group enumeration and lexicographic double-coset minimization.
"""
from pathlib import Path
from itertools import permutations
from collections import deque,Counter
import json,hashlib

ROOT=Path(__file__).resolve().parents[1]
SEEDS={50:('123','145','246','378'),51:('123','145','267','468')}
IDENT=tuple(range(8))

def encode(t):return sum(1<<(int(v)-1) for v in t)
def normalized(rows):return tuple(sorted(rows))
def action(obj,p):
    return normalized(sum(1<<p[i] for i in range(8) if mask>>i&1) for mask in obj)
def inverse(p):
    q=[0]*8
    for i,j in enumerate(p):q[j]=i
    return tuple(q)
def degrees(a,b):return tuple(sum(mask>>i&1 for mask in set(a)|set(b)) for i in range(8))
def qualifies(a,b):
    d=degrees(a,b);return min(d)<2 or sum(v==2 for v in d)>1

def orbit(seed):
    steps=[]
    for i in range(7):
        p=list(IDENT);p[i],p[i+1]=p[i+1],p[i];steps.append(tuple(p))
    back={seed:IDENT};queue=deque([seed])
    while queue:
        current=queue.popleft()
        for step in steps:
            child=action(current,step)
            if child not in back:
                # back(current) composed with step sends child back to seed.
                back[child]=tuple(back[current][step[i]] for i in range(8))
                assert action(child,back[child])==seed
                queue.append(child)
    return back

def main():
    target_path=ROOT/'coordinator/HARD_PAIR_RESIDUE.json';target=json.loads(target_path.read_text())
    seeds={k:normalized(map(encode,v)) for k,v in SEEDS.items()}
    objects={k:orbit(seed) for k,seed in seeds.items()}
    assert {k:len(v) for k,v in objects.items()}=={50:10080,51:5040}
    stabs={k:[p for p in permutations(range(8)) if action(seed,p)==seed] for k,seed in seeds.items()}
    assert {k:len(v) for k,v in stabs.items()}=={50:4,51:8}
    rows=[];residue_groups={};classification={}
    for kind,other in ((50,50),(50,51),(51,51)):
        anchor=seeds[kind];partners=set(objects[other])
        if kind==other:partners.remove(anchor)
        ordered=sorted(partners);ids={o:i for i,o in enumerate(ordered)};parent=list(range(len(ordered)))
        def find(i):
            while parent[i]!=i:
                parent[i]=parent[parent[i]];i=parent[i]
            return i
        def join(i,j):
            i,j=find(i),find(j)
            if i!=j:parent[max(i,j)]=min(i,j)
        for q in ordered:
            for p in stabs[kind]:join(ids[q],ids[action(q,p)])
            if kind==other:
                swapped=action(anchor,objects[kind][q])
                join(ids[q],ids[swapped])
        classes={}
        for q in ordered:classes.setdefault(find(ids[q]),[]).append(q)
        passed=0;failed={}
        for representative,group in classes.items():
            outcomes={qualifies(anchor,q) for q in group};assert len(outcomes)==1
            if outcomes=={True}:passed+=1
            else:failed[representative]=group
        seen=set()
        entries=[e for e in target['residue'] if e['kinds']==[kind,other]]
        for e in entries:
            a=normalized(encode(''.join(map(str,t))) for t in e['anchor'])
            q=normalized(encode(''.join(map(str,t))) for t in e['partner'])
            assert a==anchor and q in ids
            identifier=find(ids[q]);assert identifier in failed and identifier not in seen
            seen.add(identifier);assert list(degrees(a,q))==e['degree']
        assert seen==set(failed)
        row={'kinds':[kind,other],'total':len(classes),'two_pencil_covered':passed,'residue':len(failed)}
        assert row==next(x for x in target['counts'] if x['kinds']==[kind,other])
        rows.append(row)
    assert sum(r['total'] for r in rows)==3062
    assert sum(r['two_pencil_covered'] for r in rows)==2488
    assert sum(r['residue'] for r in rows)==574
    print(json.dumps({'status':'PASS','method':'adjacent-transposition BFS plus disjoint-set orbit equivalences',
      'counts':rows,'remaining':574,'covered_in_three_hard_families':2488,
      'source_artifact_sha256':hashlib.sha256(target_path.read_bytes()).hexdigest(),
      'scope':'full relative-label support orbits for singleton-occurrence factor types50/51; not parent components',
      'original_obligations_closed':0},indent=2))

if __name__=='__main__':main()
