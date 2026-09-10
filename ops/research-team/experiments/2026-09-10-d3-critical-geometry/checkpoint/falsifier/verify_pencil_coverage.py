from pathlib import Path
from itertools import combinations
import argparse,json,hashlib,subprocess,sys
import sympy as S
P=Path(__file__).resolve().parent;parser=argparse.ArgumentParser();parser.add_argument('--replay',action='store_true');args=parser.parse_args()
scripts=['height_oval_probe.py','quad_inertia.py','pencil_singular_probe.py','singular_pencil_family.py','exceptional_pencil_probe.py','quadratic_extension_probe.py']
if args.replay:
 for script in scripts:
  subprocess.run([sys.executable,str(P/script)],check=True,stdout=subprocess.DEVNULL)
def get(n):return json.loads((P/n).read_text())
raw=get('HEIGHT_OVAL_PROBE.json');quad=get('QUAD_INERTIA.json')['records'];pencils=get('PENCIL_SINGULAR_PROBE.json')['records'];families=get('SINGULAR_PENCIL_FAMILY.json')['records'];exception=get('EXCEPTIONAL_PENCIL_PROBE.json');extension=get('QUADRATIC_EXTENSION_PROBE.json')['records'];lam=S.Symbol('lam')
assert raw['occurrence_instantiations']==120 and len(quad)==22
assert len({r['trial']for r in quad})==22
assert len(pencils)==231 and {tuple(r['trials'])for r in pencils}==set(combinations(sorted(r['trial']for r in quad),2))
singular=[r for r in pencils if r.get('status')=='identically singular pencil'];regular=[r for r in pencils if r not in singular];assert len(singular)==38
repeated_count=0;higher=[]
for r in regular:
 factors=S.factor_list(S.sympify(r['det_pencil']),lam)[1]
 expected={str(S.solve(f,lam)[0])for f,m in factors if m>=2}
 assert all(S.degree(f,lam)==1 for f,m in factors if m>=2)
 checks=r['repeated_rational_root_checks'];assert{c['lambda']for c in checks}==expected
 repeated_count+=len(checks)
 for c in checks:
  if c.get('nullity',0)>1:higher.append((r['trials'],c['lambda']))
  else:assert c.get('status') in ['infinite kernel point','not common zero']or c.get('actual_uniform')is False
assert{tuple(r['trials'])for r in families}=={tuple(r['trials'])for r in singular}
assert all(r['generic_nullity']==1 and r['status']in['entire generic kernel at infinity','entire generic kernel lies on parent boundary']for r in families)
exc=exception['records'];assert all(r['status']in['whole kernel at infinity','whole kernel on parent boundary','all higher-kernel components excluded']for r in exc)
assert{r['trial']for r in exc if r['kind']=='individual quadric kernel'}=={r['trial']for r in quad}
assert{(tuple(r['trials']),r['lambda'])for r in exc if r['kind']=='nonzero-pencil higher-nullity parameter'}=={(tuple(i),j)for i,j in higher}
assert len(extension)==24 and {tuple(r['trials'])for r in extension}=={tuple(r['trials'])for r in exception['unresolved_nonlinear_parameter_factors']}
assert all(r['status']in['no real pencil parameter','whole kernel on parent boundary','common-zero radical at infinity','common-zero radical on parent boundary']for r in extension)
for r in extension:
 if r['status'].startswith('common-zero radical'):assert r['restricted_B_rank']==1
 if r['status']=='no real pencil parameter':assert not r['real_root_isolating_intervals']
result={'status':'PASS finite same-projection critical-locus exclusion','scope':'For the231 pairs among the22 displayed quadratic restrictions at projected parameters(2,3,4,5), every finite common zero with all70 parent brackets nonzero has independent height gradients. No compact-component or universal all-parent conclusion.','fixed_projected_parents':1,'original_occurrence_instantiations':120,'quadratic_restrictions':22,'quadratic_pairs':231,'nonzero_determinant_pencils':len(regular),'generically_rank4_singular_pencils':len(singular),'nonzero_pencil_repeated_rational_root_checks':repeated_count,'individual_infinite_parameter_kernels':22,'higher_nullity_rational_checks':len(higher),'singular_pencil_rational_exceptions':sum(r['kind']=='singular-pencil exceptional parameter'for r in exc),'nonlinear_exception_factors':len(extension),'new_original_obligations':0,'new_triple_source_count':0,'evidence_sha256':{f.name:hashlib.sha256(f.read_bytes()).hexdigest()for f in sorted(P.glob('*.json'))if f.name not in ['HANDOFF.json','PENCIL_COVERAGE.json','QUAD_PENCIL_SCREEN.json']}}
(P/'PENCIL_COVERAGE.json').write_text(json.dumps(result,indent=2)+'\n')
print('PASS231 same-projection quadratic pairs: no actual uniform vertical critical point')
print('STATUS original2/9; no universal triple escape or compactness conclusion')
