"""Source adapter for a repository checkout or the self-contained recovery snapshot."""
from pathlib import Path
import importlib.util,hashlib,json,time
import sympy as s
HERE=Path(__file__).resolve().parent
path=HERE.parent/'2026-09-18-d3-parent-localized'/'verify_exact.py'
if not path.exists():path=HERE/'source_verify.py'
if not path.exists():raise FileNotFoundError('Restore the full snapshot or run from the research branch.')
spec=importlib.util.spec_from_file_location('pinned_parent_source',path)
source=importlib.util.module_from_spec(spec);spec.loader.exec_module(source)
TH,j,SOURCE_SHA=source.TH,source.j,source.SOURCE_SHA
A,B,C,D,u,v,w,t=TH
reconstruct,source_path,zero,require=source.reconstruct,source.source_path,source.zero,source.require

def lower_chart():
 local=HERE/'LOWER_CHART.json'
 if local.exists():return json.loads(local.read_text())
 Q,R,_=reconstruct();r,z=s.symbols('r z');change={t:(D*r-u)/A,w:C*z+u}
 q=s.cancel(Q.subs(change,simultaneous=True)/D).expand()
 p=s.cancel(A**2*R.subs(change,simultaneous=True)/C).expand()
 return {'q':str(q),'g':str(p)}
