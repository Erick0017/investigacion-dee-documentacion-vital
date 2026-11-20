"""Static actual ABI checks, no Native/MCP/HTTP/model or process calls."""
from pathlib import Path
import ast,datetime,hashlib,json
ROOT=Path(__file__).resolve().parents[1]
files=['control/orquestar_C02_R04.py','control/orquestar_comparador_C02_R03.py','control/studio_mailbox_relay_C02_R03.py','control/adjuntar_comparador_sin_decisiones_C02_R03.py']
sources={p:(ROOT/p).read_text('utf8')for p in files}
for t in sources.values():ast.parse(t)
n=sources[files[0]];c=sources[files[1]];r=sources[files[2]];a=sources[files[3]]
assert "WORLD_RESTORED_BEFORE_NATIVE.json"in n and "WORLD_RESTORED_BEFORE_POLICY.json"in c
assert "['--resume-boundary',str(output/'WORLD_RESTORED_BEFORE_NATIVE.json')]if args.world_checkpoint else []"in n
assert "['--resume-boundary',str(output/'WORLD_RESTORED_BEFORE_POLICY.json')]if args.world_checkpoint else []"in c
assert "preparar_recuperacion_cache_C02_R05.py"in n
assert a.count("code=u.client_control('START_NATIVE')")==1
assert a.index("u.write(original/'START_INTENT.json',intent)")<a.index("code=u.client_control('START_NATIVE')")
assert a.index("while not(original/'RESULTADO.json').exists()")<a.index('transport.capture_world(mcp,context')
assert "relay_events=original/'relay.jsonl'"in a and "'Bridge already has a session, decision or operation'"in a
assert "policy_hosts_started=0"in a and 'run_comparador_C02_R02.py' in a
assert 'subprocess.Popen([sys.executable' in a and a.count('subprocess.Popen(')==1
assert "b['completed_cycles']==state['feedback_operations_completed']"in a and "b['next_opportunity']==b['completed_cycles']+1"in a
assert hashlib.sha256((ROOT/'control/orquestar_C02_R02.py').read_bytes()).hexdigest()=='dce1e9fbefe4fe9fa244742064570e96d5c93c7b6dac41fc8b6c7cec568638ff'
assert hashlib.sha256((ROOT/'control/orquestar_comparador_C02_R02.py').read_bytes()).hexdigest()=='c9081cb33847aeaaaa0b486dd3b7df1444f3c074fda895b63d4e3a3abc0bc9d4'
stamp=datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')
report=dict(schema='DEE.RBX01.C02.explicit_resume_and_comparator_attach.offline.R03',checks=10,passed=True,
            source_sha256={p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest()for p in files},
            Native_calls=0,MCP_calls=0,HTTP_requests=0,model_calls=0,process_calls=0)
out=ROOT/'pruebas'/('TRANSPORTE_Y_ATTACH_COMPARADOR_R03_'+stamp+'.json');out.write_text(json.dumps(report,indent=2)+'\n',encoding='utf8');print(json.dumps(report,indent=2))
