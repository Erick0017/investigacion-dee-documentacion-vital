"""Read original complete prepare/final snapshots: guard admission vs claim."""
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from comun import *
from capacidades.observador_causal_retrospectivo_01 import Snapshot
from dee_thinking.persistence import decode_metadata
from capacidades.mente_integral_mi01 import KEY
source=E/'MI01_HABITAT_241.PREPARADO.deetsnap.gz';final=E/'MI01_HABITAT_241.FINAL.deetsnap.gz';a=Snapshot(source);b=Snapshot(final);cfg=decode_metadata(a.metadata[KEY]);queries=cfg['material_queries'];rows=[];rec={z['id']:z for z in b.receipts}
for name,p in queries.items():
    if not name.startswith('MI01_HABITAT_241.'):continue
    for r in p['requests']:
        if any(word in r['port']for word in('guard','interceptor')):rows.append({'query':name,'request':r,'receipt_final':rec[r['id']],'prepared_site':a.observation(r['site']),'final_site':b.observation(r['site'])})
atomic_json(E/'HABITAT_RECIBOS_GUARDAS_245_0TICKS.json',{'source':str(source.relative_to(R)),'sha256':sha(source),'final':str(final.relative_to(R)),'final_sha256':sha(final),'guards':rows,'native_ticks':0})
print(json.dumps([{'q':z['query'],'site':z['request']['site'],'tick':z['request']['tick'],'status':z['receipt_final']['status'],'pre_raw':z['prepared_site']['raw']}for z in rows],ensure_ascii=False),flush=True)
