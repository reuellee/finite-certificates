"""Preserve exact completed discovery bytes in a compact review artifact."""
from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED, ZipInfo

HERE = Path(__file__).resolve().parent
NAMES = ('bracket_discovery.json','quartic_discovery.json',
         'discriminant_factors.json','real_fiber_discovery.json')
archive = HERE/'DISCOVERY_OUTPUTS.zip'
with ZipFile(archive,'w',compression=ZIP_DEFLATED,compresslevel=9) as z:
    for name in NAMES:
        info = ZipInfo(name,date_time=(2026,9,5,0,0,0))
        info.compress_type = ZIP_DEFLATED
        z.writestr(info,(HERE/name).read_bytes(),compresslevel=9)
with ZipFile(archive) as z:
    assert z.testzip() is None
    for name in NAMES:
        assert z.read(name) == (HERE/name).read_bytes()
print('PASS four completed discovery outputs archived byte for byte')
