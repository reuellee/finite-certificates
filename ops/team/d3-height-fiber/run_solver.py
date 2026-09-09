"""Bounded WSL msolve discovery; never infer a theorem from a solver exit code."""
from pathlib import Path
import subprocess
import sys
import json
import time
import shlex

ROOT=Path(__file__).resolve().parents[3]
OUT=ROOT.parent/'outputs/d3-height-cas-20260905'
name=sys.argv[1]
assert name in ('critical_pivot_p1073741827','critical_pivot_more_p1073741827','critical_pivot_Q','critical_lagrange_p1073741827')
source=OUT/(name+'.ms')
linux='/mnt/e/Projects/9DVL Research/outputs/d3-height-cas-20260905/'+name
flags=['-g','2','-l','2','-t','2','-v','2']
if 'p1073741827' in name and 'lagrange' not in name:
    flags+=['-S']
cmd=['/tmp/d3-height-msolve/msolve',*flags,'-f',linux+'.ms','-o',linux+'.basis']
# Hard limits: address space, CPU time, output file size, and wall time.
script='ulimit -c 0\nulimit -v 8388608\nulimit -t 300\nulimit -f 262144\nexec timeout -k 5s 300s '+shlex.join(cmd)
start=time.time()
with (OUT/(name+'.transcript.txt')).open('w') as log:
    result=subprocess.run(['wsl','-d','lee-dev','--','bash','-c',script],stdout=log,stderr=subprocess.STDOUT,timeout=320)
record={'name':name,'seconds':round(time.time()-start,3),'exit_code':result.returncode,'command':cmd,'limits':{'seconds':300,'virtual_memory_kib':8388608,'file_blocks':262144},'theorem_status':'NO_PROMOTION; solver output requires exact certification'}
(OUT/(name+'.run.json')).write_text(json.dumps(record,indent=2)+'\n')
print(json.dumps(record),flush=True)
print('\n'.join((OUT/(name+'.transcript.txt')).read_text(errors='replace').splitlines()[-30:]),flush=True)
