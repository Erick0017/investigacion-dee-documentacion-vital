"""Pin prospective lease code only, not operational state or a live writer."""
from pathlib import Path
import ast,datetime,hashlib,json
ROOT=Path(__file__).resolve().parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
names=['native/lease_R05_bundle/'+n for n in('rbx07_native_v3.py','rbx07_identity_v3.py','rbx07_funciones_v3.py')]+[
 'native/lease_core_v3_R05.py','native/migrar_lease_cerrada_v3_R05.py','native/ledger_v3_R05.py','native/owner_support_v3_R05.py',
 'control/mcp_persistente_v3_R05.py','control/world_comprimido_v3_R05.py','control/run_integrated_v3_R05.py','native/test_lease_v3_R05_offline.py']
for name in names:ast.parse((ROOT/name).read_text('utf8'))
for name in('rbx07_identity_v3.py','rbx07_funciones_v3.py'):
    if(ROOT/'native/bundle'/name).read_bytes()!=(ROOT/'native/lease_R05_bundle'/name).read_bytes():raise ValueError('Unchanged helper must remain byte-identical')
value={'schema':'DEE.RBX07.prospective_native_lease_freeze.R05','sealed':True,'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),
 'native_start_epoch':1794841620,'last_new_episode_epoch':1794880800,'native_cutoff_epoch':1794884820,
 'previous_native_freeze_sha256':'692cef5938e352adee4f318fdc3766e41ae4a5fc6181903331444af45e149145',
 'scope':'Administrative prospectively extended finite lease, same15:07start. No live Main29..34 alteration. Root applies only to closed worlds without pending or uncertain futures.',
 'native_sources_sha256':{n:sha(ROOT/'native/lease_R05_bundle'/n)for n in('rbx07_native_v3.py','rbx07_identity_v3.py','rbx07_funciones_v3.py')},
 'files':[{'file':n,'bytes':(ROOT/n).stat().st_size,'sha256':sha(ROOT/n)}for n in names],
 'Native_MCP_model_calls_by_preparation':0,'no_policy_or_reader_change':True,'global_tick_limit':160000,'owner_job_limit_bytes':536870912,
 'raw_support_limit':10000,'source_tick':991187,'max_role_cycles':{'main':24,'control':6,'load':3,'pilot':3},
 'metadata_migration_allowlist':['own m.code_scope','own CODE_SCOPE_KEY','official administrative SYSTEM commit'],
 'never_reset':['cycles','last_sequence','session_id','policy','log_count','log_chain_sha256','RAW','clocks','ledger.consumed','ledger.worlds','ledger.intents']}
p=ROOT/'control/CONGELADO_NATIVE_R07_LEASE_R05.json'
with p.open('x',encoding='utf8')as f:json.dump(value,f,ensure_ascii=False,indent=2)
print(json.dumps({'path':str(p),'bytes':p.stat().st_size,'sha256':sha(p),'native_sources_sha256':value['native_sources_sha256']},ensure_ascii=False))
