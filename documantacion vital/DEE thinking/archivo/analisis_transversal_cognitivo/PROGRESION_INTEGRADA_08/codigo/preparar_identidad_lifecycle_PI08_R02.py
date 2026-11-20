"""Prepare explicit reference release inside the writer scope. The official
OrganizationalWorld stub has no close/shutdown API; do not invent one.
"""
from pathlib import Path
import ast,hashlib,json
H=Path(__file__).resolve().parent;source=H/'pi08_identidad_c2c_R01.py';target=H/'pi08_identidad_c2c_R02.py'
if target.exists():raise FileExistsError('Prepared lifecycle revision preserved')
s=source.read_text('utf8').replace('import copy,gzip,hashlib,json,struct','import copy,gzip,hashlib,json,struct,gc')
begin=s.index(' with store.writer(LIFE):\n');end=s.index(" if before['physical']",begin)
block=s[begin+len(' with store.writer(LIFE):\n'):end]
replacement=' with store.writer(LIFE):\n  a=None\n  try:\n'+''.join('  '+line if line.strip()else line for line in block.splitlines(True))+'  finally:\n   # Official OrganizationalWorld has no close/shutdown; remove its only\n   # adapter reference and collect while this world writer is still held.\n   a=None\n   gc.collect()\n'
s=s[:begin]+replacement+s[end:];ast.parse(s);target.write_text(s,encoding='utf8')
proof=H.parent/'control/IDENTIDAD_PI08_LIFECYCLE_PREPARADA_R02.json'
with proof.open('x',encoding='utf8')as f:json.dump({'schema':'DEE.PI08.identity_lifecycle.prepared.v1','source':{'path':str(source),'sha256':hashlib.sha256(source.read_bytes()).hexdigest()},'prepared':{'path':str(target),'sha256':hashlib.sha256(target.read_bytes()).hexdigest()},'official_contract':'dee_thinking-4.5.0 WHL persistence.py226-230 loads _native.OrganizationalWorld; _native.pyi468-508 exposes no close/shutdown.','change':'try/finally releases sole adapter reference(a=None;gc.collect) inside store.writer. No Native function, data, tick, protocol or identity criterion changed.','Native_executed':False,'deploy_target':'app/pi08_identidad_c2c_R01.py'},f,ensure_ascii=False,indent=2);f.write('\n')
print(str(target));print(hashlib.sha256(target.read_bytes()).hexdigest())
