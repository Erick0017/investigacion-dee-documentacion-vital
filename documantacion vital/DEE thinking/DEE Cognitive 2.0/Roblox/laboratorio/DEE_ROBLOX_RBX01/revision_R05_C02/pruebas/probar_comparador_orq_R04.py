"""Only comparator relay source revision; no material execution."""
from pathlib import Path
import ast,datetime,hashlib,json
ROOT=Path(__file__).resolve().parents[1]
a=ROOT/'control/orquestar_comparador_C02_R03.py';b=ROOT/'control/orquestar_comparador_C02_R04.py';relay=ROOT/'control/studio_mailbox_relay_C02_R04.py'
x=a.read_text('utf8');y=b.read_text('utf8')
assert x.count('control/studio_mailbox_relay_C02_R03.py')==2
assert x.replace('control/studio_mailbox_relay_C02_R03.py','control/studio_mailbox_relay_C02_R04.py')==y
ast.parse(y);ast.parse(relay.read_text('utf8'))
assert "WORLD_RESTORED_BEFORE_POLICY.json"in y and "if args.world_checkpoint else []"in y
assert hashlib.sha256(a.read_bytes()).hexdigest()=='cb7444345bee71527be6beb0436ad6cac7e15cb7868736cfca16a741fa082abd'
assert hashlib.sha256(relay.read_bytes()).hexdigest()=='c672376186fe9cf5b8059f5a229ecbbb0f7ae9a663ca91bc778112ad5ae050ed'
stamp=datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')
r=dict(schema='DEE.RBX01.C02.comparator_orq_delta.R04',checks=4,passed=True,
       changes='Only two relay module path literals R03 to R04; comparator resume tick0 is supported by separately tested relay',
       sha256={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest()for p in(a,b,relay)},Native_calls=0,MCP_calls=0,HTTP_requests=0,model_calls=0)
out=ROOT/'pruebas'/('COMPARADOR_ORQ_R04_'+stamp+'.json');out.write_text(json.dumps(r,indent=2)+'\n',encoding='utf8');print(json.dumps(r,indent=2))
