"""Static first-start and matching-closure guard verification, no runtime."""
from pathlib import Path
import ast,datetime,hashlib,json
ROOT=Path(__file__).resolve().parents[1]
a=ROOT/'control/adjuntar_propietario_sin_material_C02_R05.py'
b=ROOT/'control/adjuntar_propietario_sin_material_C02_R06.py'
t=b.read_text('utf8');ast.parse(t)
assert t.index("o.write(original/'START_NATIVE_INTENT.json',intent)")<t.index("code=o.client_control('START_NATIVE')")
assert t.index("First admission deadline rechecked after relay connection")<t.index("o.write(original/'START_NATIVE_INTENT.json',intent)")
assert t.count("code=o.client_control('START_NATIVE')")==1
assert "proof.get('lifeId')==life"in t and "proof.get('exit_code')==0"in t
assert "'R06_checkpoint',out/'WORLD_CHECKPOINT.json'"in t
assert hashlib.sha256(a.read_bytes()).hexdigest()=='4e39a700f9e939b6e72255006e572053f60d2daed7ed8a44bcf2f030c1f20d2d'
report=dict(schema='DEE.RBX01.C02.attach_guard_delta.R06',created_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),
            checks=6,passed=True,Native_actions=0,MCP_calls=0,HTTP_requests=0,process_actions=0,
            hashes={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest()for p in(a,b)},
            changes=['Shared exclusive-create original START intent before the sole first START',
                     'Recheck new-Q1 margin immediately before that intent',
                     'Require matching life, clean exit, nonrunning child on closure witness',
                     'Distinct passive checkpoint transport label R06'],
            preserved_inflight_R05=True,not_executed=True)
stamp=datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')
out=ROOT/'pruebas'/('ATTACH_GUARDAS_R06_'+stamp+'.json');out.write_text(json.dumps(report,indent=2)+'\n',encoding='utf8');print(json.dumps(report,indent=2))
