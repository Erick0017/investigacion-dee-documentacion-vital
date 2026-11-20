"""Decode recorded checkpoint bytes only; no engine, network or model."""
from pathlib import Path
import hashlib,json
ROOT=Path(__file__).resolve().parents[1]
d=ROOT/'evidencia/AI02_RECUPERACION_FRONTERA5_R01'
p=d/'WORLD_CHECKPOINT.json'
if p.exists():raise RuntimeError('Preserve existing checkpoint')
raw=bytes.fromhex((d/'WORLD_TRANSPORT.hex').read_text('ascii'))
w=json.loads(raw)
assert len(raw)==255022 and w['boundary']['completed_opportunities']==5
assert w['boundary']['next_opportunity']==6 and w['S']['completedCycles']==5
assert w['native_tick']==0 and w['bridge']['session_id']=='dff2980509d448be9315e75b98fad02f'
with p.open('xb')as f:f.write(raw)
report={'file':str(p),'bytes':len(raw),'sha256':hashlib.sha256(raw).hexdigest(),
 'boundary':w['boundary'],'read_chunks':16,'Native_calls':0,'model_calls':0,
 'capture_method':'Root direct MCP; unchanged frozen checkpoint transport R02 ABI'}
with (d/'TRANSPORTE_ROOT_META.json').open('x',encoding='utf8')as f:json.dump(report,f,ensure_ascii=False,indent=2)
print(json.dumps(report))
