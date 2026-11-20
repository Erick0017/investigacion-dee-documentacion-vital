"""Read exact existing receipts; no new native trajectory."""
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from comun import *
from capacidades.observador_causal_retrospectivo_01 import Snapshot
rows=[]
for number in range(340,348):
    name='MI01_CONTEXTO_B_'+str(number);p=E/(name+'.json')
    if not p.exists():continue
    d=json.loads(p.read_bytes());v=d['data']['result'];record=d['after'];x=Snapshot(S/record['snapshot']);byid={int(z['id']):z for z in x.receipts}
    req=[]
    for r in v['plan']['prepared_B_context']['requests']:req.append({**r,'exact_snapshot_receipt':byid[int(r['id'])]})
    rows.append({'case':number,'requests':req,'source':str(p.relative_to(R)),'source_sha256':sha(p),'snapshot':record['snapshot'],'snapshot_sha256':record['snapshot_sha256']})
atomic_json(E/'RECIBOS_B_CONTEXTO_348_0TICKS.json',{'cases':rows,'native_ticks':0,'finding':'Paired base and failure queries can share the same B sample clock; their extra zero-load matter requests, created after the shared compiler, collide. Fixed43fixture itself is applied. Existing output results remain real but do not demonstrate all requested resources were admitted. Frozen MAIN design is NOT repaired after this discovery.','correction_to_local_interpretation':'SEM_OBSERVER sites count as alive for the frozen matter rule. In306 there are6state-positive non-orphan neighbours first versus5second, not merely2versus1; the43/25gradient remains18,-68,0. Zero-load and SEM4neighbours cannot be ignored.'})
print(json.dumps({'cases':len(rows),'native_ticks':0,'output':'RECIBOS_B_CONTEXTO_348_0TICKS.json'}))
