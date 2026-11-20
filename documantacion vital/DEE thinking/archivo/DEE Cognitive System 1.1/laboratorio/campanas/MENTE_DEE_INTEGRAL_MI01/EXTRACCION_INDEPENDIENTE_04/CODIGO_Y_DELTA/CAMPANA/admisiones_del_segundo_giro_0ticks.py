"""Requested turn resources versus actual frozen-runtime receipts."""
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from comun import *
from capacidades.observador_causal_retrospectivo_01 import Snapshot
d=json.loads((E/'MI01_402_MAIN_ESTADO_PRE_RESERVAS.json').read_bytes())['result'];g=d['protocol'];h=g['native_habitats']['MI01_EVALUACION_FIJADA'];f=h['direct_failure']['opportunities'][0];r=g['selector_returns'][f['reply_name']];turn=r['routes']['1']['turns'][6];x=Snapshot(E/'MI01_SEGUNDO_OBSTACULO_479.T25093.DIAGNOSTICO_NO_OPERATIVO.deetsnap.gz');receipts={v['id']:v for v in x.receipts};selected=[]
for q in r['requests']:
    if q['tick']==turn['tick']-3:
        selected.append({**q,'actual_receipt':receipts[q['id']]})
out={'native_ticks':0,'turn':turn,'requests_at_its_injection_time':selected,'snapshot_sha256':x.encoded_sha256,'scope':'Recorded preparation may contain logical aliases. Actual event IDs/status/reasons decide material admission; no packet is reintroduced for this analysis.'};atomic_json(E/'ADMISION_SEGUNDO_GIRO_482_0TICKS.json',out);print(json.dumps(out,ensure_ascii=False))
