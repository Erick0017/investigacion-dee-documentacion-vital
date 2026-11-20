"""Read saved complete state only, no new native ticks."""
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from comun import *
from capacidades.observador_causal_retrospectivo_01 import Snapshot
p=E/'MI01_EXTENSION_DIAG_136.T23768.deetsnap.gz';snap=Snapshot(p)
rows=[]
for j in range(47):
    site=[(42+j)%67,59,55];v=snap.observation(site)
    if v['raw']!='0':rows.append(v)
atomic_json(E/'CORREDOR_137_SIN_TICKS.json',{'snapshot':str(p.relative_to(R)),'sha256':sha(p),'tick':snap.tick,'corridor_nonzero':rows,'no_native_ticks':True})
print(json.dumps(rows,ensure_ascii=False))
