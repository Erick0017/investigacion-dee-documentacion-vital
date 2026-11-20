"""R03 changes only the read/audit transport; no policy or material calls."""
from pathlib import Path
import hashlib,json
P=Path(__file__).resolve().parent
src=P/'runner_comparador_v3_R02.py';dst=P/'runner_comparador_v3_R03.py'
s=src.read_text('utf-8');needle='from world_comprimido_v3_R02 import CompressedWorld'
assert s.count(needle)==1;s=s.replace(needle,'from world_comprimido_v3_R03 import CompressedWorld')
if dst.exists():raise ValueError('Fresh runner version required')
compile(s,str(dst),'exec');dst.write_text(s,encoding='utf-8',newline='\n')
print(json.dumps({'source_sha256':hashlib.sha256(src.read_bytes()).hexdigest(),
 'output':str(dst),'sha256':hashlib.sha256(dst.read_bytes()).hexdigest(),
 'change':'WorldR03 bounded ACK + compressed full auditor capture only',
 'policy_changed':False,'Native_calls':0,'model_calls':0,'MCP_calls':0}))
