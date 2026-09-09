"""Compiled exact factorization discovery; run with the recorded WSL FLINT."""
from pathlib import Path
import json
import time
from flint import fmpq_mpoly_ctx

HERE = Path(__file__).resolve().parent
rec = json.loads((HERE/'bracket_discovery.json').read_bytes())['discriminant_u']
ctx = fmpq_mpoly_ctx.get(rec['variables'])
p = ctx.from_dict({tuple(m):c for c,m in rec['terms']})
start = time.monotonic()
content, factors = p.factor()
check = ctx.constant(content)
out = {'variables':rec['variables'],'content':str(content),'factors':[]}
for f,e in factors:
    check *= f**e
    terms = [[int(c),list(map(int,m))] for m,c in f.to_dict().items()]
    out['factors'].append({'terms':terms,'exponent':int(e),'expression':str(f)})
    print('factor',len(terms),'exponent',e, str(f)[:350],flush=True)
assert check == p
out['seconds'] = time.monotonic()-start
(HERE/'discriminant_factors.json').write_text(json.dumps(out,indent=2)+'\n')
print('seconds',out['seconds'],flush=True)
