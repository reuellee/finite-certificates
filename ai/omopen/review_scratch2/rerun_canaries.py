#!/usr/bin/env python3
"""REVIEW (Fable): re-run canaries.py with outputs redirected, loading the
omopen module BY PATH to dodge the omreal/canaries.py name collision."""
import importlib.util
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

spec = importlib.util.spec_from_file_location(
    'omopen_canaries', os.path.join(OMOPEN, 'canaries.py'))
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)
mod.DATA = os.path.join(HERE, 'gates_data')
nfail = mod.run()
print('canaries failures=%d (0 expected)' % nfail)
sys.exit(1 if nfail else 0)
