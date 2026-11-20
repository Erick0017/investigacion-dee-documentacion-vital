"""Prospective future load lease; no owner/Native and no reset of supplies."""
from pathlib import Path
import ast,datetime,hashlib,json
ROOT=Path(__file__).resolve().parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
old=ROOT/'load/PROTOCOLO_CARGA_V3_R02.json';v=json.loads(old.read_text('utf8'))
v.update(schema='DEE.R07.three_owner_focal_load.R05',last_new_episode_epoch=1794880800,hard_finish_epoch=1794884820,
 latest_batch_start_epoch=1794872700,latest_GO_epoch=1794873300,original_start_epoch=1794841620,
 prospective_revision_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),
 revision_reason='Finite12h maximum at same15:07start, before any LOAD admission. Old19:15/19:25 start/GO preserved only in unexecuted R02.',
 timing_basis={'observed_first_Main_three_episodes_approx_seconds':2400,'conservative_nine_serial_equivalent_episodes_seconds':7200,
   'latest_batch_start_utc':'2026-11-16T23:45:00Z','latest_GO_utc':'2026-11-16T23:55:00Z','last_new_episode_utc':'2026-11-17T02:00:00Z',
   'hard_finish_utc':'2026-11-17T03:07:00Z','margin_GO_to_last_new_seconds':7500,'new_scope_or_physics_budget_increased':False})
p=ROOT/'load/PROTOCOLO_CARGA_V3_R05.json'
with p.open('x',encoding='utf8')as f:json.dump(v,f,ensure_ascii=False,indent=2)
pins={'native/owner_support_v3_R05.py':sha(ROOT/'native/owner_support_v3_R05.py'),'native/adapter_v3.py':sha(ROOT/'native/adapter_v3.py')}
rows=[]
for old,new in(('worker_carga_v3_R02.py','worker_carga_v3_R05.py'),('ejecutar_carga3_v3_R02.py','ejecutar_carga3_v3_R05.py')):
    s=(ROOT/'load'/old).read_text('utf8').replace('PROTOCOLO_CARGA_V3_R02.json','PROTOCOLO_CARGA_V3_R05.json').replace('1794859200','1794880800').replace('1794863220','1794884820')
    s=s.replace('owner_support_v3.py','owner_support_v3_R05.py').replace('worker_carga_v3_R02.py','worker_carga_v3_R05.py').replace('before19:15UTC','before23:45UTCNov16').replace('after20:00UTC','after02:00UTCNov17')
    if old.startswith('worker'):
        i=s.index('PINS=');j=s.index('def sha',i);s=s[:i]+'PINS='+repr(pins)+'\n\n'+s[j:]
    ast.parse(s);p=ROOT/'load'/new
    with p.open('x',encoding='utf8')as f:f.write(s)
    rows.append({'file':new,'bytes':p.stat().st_size,'sha256':sha(p)})
proof={'Native_calls':0,'MCP_calls':0,'old_R01_R02_sources_preserved':True,'no_LOAD_executed_by_tool':True,'protocol_sha256':sha(ROOT/'load/PROTOCOLO_CARGA_V3_R05.json'),
 'new_start_and_GO_guards_finite':True,'cycles_each':3,'lives':3,'JobLimit':536870912,'same_global_limit':160000,'files':rows}
with(ROOT/'load/CARGA_LEASE_R05_PREPARADA.json').open('x',encoding='utf8')as f:json.dump(proof,f,ensure_ascii=False,indent=2)
print(json.dumps(proof))
