#!/usr/bin/env python3
"""REVIEW (Fable): re-run validate.py and canaries.py with all outputs
redirected to review_scratch2/ so the shipped data/ artifacts are untouched.
The sweep has advanced since the builder's run, so the sampled pools differ;
the gates are claimed to be population-level properties and must still pass.
"""
import os
import sys

sys.dont_write_bytecode = True
for _v in ('OMP_NUM_THREADS', 'MKL_NUM_THREADS', 'OPENBLAS_NUM_THREADS',
           'NUMEXPR_NUM_THREADS'):
    os.environ.setdefault(_v, '1')
os.environ['PYTHONDONTWRITEBYTECODE'] = '1'

HERE = os.path.dirname(os.path.abspath(__file__))
OMOPEN = os.path.dirname(HERE)
sys.path.insert(0, OMOPEN)

OUT = os.path.join(HERE, 'gates_data')
os.makedirs(OUT, exist_ok=True)

which = sys.argv[1] if len(sys.argv) > 1 else 'both'

if which in ('validate', 'both'):
    import validate
    validate.DATA = OUT                      # redirect every artifact write
    class A:
        n = 40
        budget = 120.0                       # same as the shipped run
    rc = validate.run(A())
    print('validate rc=%d (0 expected)' % rc)

if which in ('canaries', 'both'):
    import canaries
    canaries.DATA = OUT
    nfail = canaries.run()
    print('canaries failures=%d (0 expected)' % nfail)
