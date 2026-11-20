"""AST and hashes only. Never imports policy, model, owner or a runner."""
from pathlib import Path
import ast,datetime,hashlib,json
ROOT=Path(__file__).resolve().parents[1]
def read(p):return json.loads((ROOT/p).read_text('utf-8-sig'))
def sha(p):return hashlib.sha256((ROOT/p).read_bytes()).hexdigest()
def functions(name):
 t=ast.parse((ROOT/name).read_text('utf8'))
 return {n.name:ast.dump(n,include_attributes=False)for n in t.body if isinstance(n,(ast.FunctionDef,ast.ClassDef))}
old=functions('puente/run_comparador_C02_R02.py');new=functions('puente/run_comparador_C02_R03.py')
same=('pack_public','wire_output','WireAdapter','db_read','compare_states','serve')
for name in same:assert old[name]==new[name],name
budget=read('protocolo/PRESUPUESTO_AI_C02_R05.json')
assert datetime.datetime.fromtimestamp(budget['AI_absolute_cutoff_epoch'],datetime.timezone.utc).isoformat()=='2026-11-15T18:15:00+00:00'
assert budget['AI_opportunities']==18 and budget['AI_suspend_after']==6 and budget['AI_reserved_opportunities']==[13,18]
assert budget['global_LLM_call_limit']==128 and budget['quota_reset_authorized']is False and budget['new_Native_ticks_authorized']==0
assert budget['previous_finish_was_not_met']is True and budget['previous_absolute_finish_epoch']==1794744900
assert sha(budget['policy_unchanged'])==budget['policy_sha256']and sha(budget['client_unchanged'])==budget['client_sha256']
assert sha('control/orquestar_comparador_C02_R04.py')=='5c0b457933f22ae78fa3a4abde3c36612dbcac8ef16e711c2e523b8ec60969b9'
assert sha('puente/run_comparador_C02_R02.py')=='4c4210dd2b88a95afd5ae68b8682463c4bd0c95738cae939605207c288411a6e'
t=(ROOT/'puente/run_comparador_C02_R03.py').read_text('utf8')
assert "MODES=('CONVENTIONAL_AI',)"in t and 'MAX_CUTOFF=1794766500'in t
assert "paths=('protocolo/PRESUPUESTO_AI_C02_R05.json','puente/run_comparador_C02_R03.py'"in t
assert t.count('    budget_preflight()')==2
o=(ROOT/'control/orquestar_comparador_C02_R05.py').read_text('utf8')
assert 'HARD_FINISH=1794766500'in o and "args.participant=='CONVENTIONAL_AI'"in o
assert 'WORLD_RESTORED_BEFORE_POLICY.json'in o and 'studio_mailbox_relay_C02_R04.py'in o
ast.parse(o)
report=dict(schema='DEE.RBX01.C02.AI_resumed_budget.offline_verification.R05',passed=True,
 unchanged_semantic_functions=list(same),Native_calls=0,model_calls=0,HTTP_calls=0,private_config_writes=0,
 source_sha256={p:sha(p)for p in('control/orquestar_comparador_C02_R05.py','puente/run_comparador_C02_R03.py','protocolo/PRESUPUESTO_AI_C02_R05.json')})
stamp=datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')
out=ROOT/'pruebas'/('PLAZO_AI_R05_'+stamp+'.json');out.write_text(json.dumps(report,indent=2)+'\n',encoding='utf8');print(json.dumps(report,indent=2))
