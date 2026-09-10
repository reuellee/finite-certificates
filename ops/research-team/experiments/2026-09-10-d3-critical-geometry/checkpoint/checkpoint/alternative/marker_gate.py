from pathlib import Path
import json,hashlib
P=Path(__file__).resolve().parent;src=P.parent/'original/AFFINE_PAIR_COVERAGE.json';J=json.loads(src.read_text());out=[]
for z in J['remaining']:
 choices=[]
 for swap in [False,True]:
  A=z['partner']if swap else z['anchor'];B=z['anchor']if swap else z['partner']
  for e in range(1,9):
   Ae=[set(I)for I in A if e in I];Be=[set(I)for I in B if e in I];B0=[set(I)for I in B if e not in I]
   if len(Ae)!=1 or len(Be)!=2:continue
   pair=Ae[0]-{e};forced=(Be[0]|Be[1])-{e};forced|=B0[0]&B0[1];markers=pair&forced
   if markers:choices.append({'swap':swap,'moving_label':e,'linear_pair':sorted(pair),'quadratic_forced_labels':sorted(forced),'markers':sorted(markers),'quadratic_moving_triples':[sorted(x)for x in Be],'quadratic_fixed_triples':[sorted(x)for x in B0]})
 out.append({'source_index':z['source_index'],'kinds':z['kinds'],'anchor':z['anchor'],'partner':z['partner'],'marker_choices':choices})
R={'schema':'balanced_pair_forbidden_parent_marker_gate_v1','source_sha256':hashlib.sha256(src.read_bytes()).hexdigest(),'remaining_pairs':len(out),'pairs_with_marker':sum(bool(x['marker_choices'])for x in out),'total_marker_choices':sum(len(x['marker_choices'])for x in out),'pairs':out};(P/'CONIC_MARKER_GATE.json').write_text(json.dumps(R,indent=2)+'\n');print({k:v for k,v in R.items()if k!='pairs'});print('unmarked',[x['source_index']for x in out if not x['marker_choices']]);print('first',out[0])
