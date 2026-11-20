"""Version transport/boundary only before reference execution; no calls."""
from pathlib import Path
import hashlib,json
HERE=Path(__file__).resolve().parent
old=HERE/'runner_comparador_v3.py';out=HERE/'runner_comparador_v3_R02.py'
s=old.read_text('utf-8')
s=s.replace('from world_comprimido_v3 import CompressedWorld','from world_comprimido_v3_R02 import CompressedWorld')
s=s.replace('29<=a.stop_cycle<=52','29<=a.stop_cycle<=46')
if out.exists():raise ValueError('Fresh reference runner version required')
compile(s,str(out),'exec');out.write_text(s,encoding='utf-8',newline='\n')
print(json.dumps({'source':str(old),'source_sha256':hashlib.sha256(old.read_bytes()).hexdigest(),
 'output':str(out),'sha256':hashlib.sha256(out.read_bytes()).hexdigest(),
 'changes':['R02 exact World preparation-event contract','Prospective reference horizon18new/global46'],
 'policy_changed':False,'Native_calls':0,'model_calls':0,'Studio_calls':0}))
