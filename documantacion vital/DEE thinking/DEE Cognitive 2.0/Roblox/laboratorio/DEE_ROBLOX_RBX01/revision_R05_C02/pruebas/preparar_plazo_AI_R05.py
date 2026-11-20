"""Create declared new AI-only clock wrappers, never run a model or Native."""
from pathlib import Path
import ast,datetime,hashlib,json
ROOT=Path(__file__).resolve().parents[1];NEW=1794766500;OLD=1794744900
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def changed_file(old_name,new_name,fn):
 a=ROOT/old_name;b=ROOT/new_name;assert not b.exists(),'New source only'
 before=digest(a);text=a.read_text('utf8');new=fn(text);ast.parse(new)
 b.write_text(new,encoding='utf8',newline='');assert digest(a)==before
 return dict(original=old_name,original_sha256=before,original_preserved=True,new=new_name,new_sha256=digest(b))
def orq(t):
 assert t.count('HARD_FINISH=1794744900')==1
 t=t.replace('HARD_FINISH=1794744900','HARD_FINISH=1794766500  # AI-only prospective resumed window, 2026-11-15 18:15UTC')
 t=t.replace('puente/run_comparador_C02_R02.py','puente/run_comparador_C02_R03.py')
 old="    need(args.root_run,'Root-only execution')"
 assert t.count(old)==1
 return t.replace(old,old+"\n    need(args.participant=='CONVENTIONAL_AI','R05 resumed deadline is AI-only; Native and completed PROGRAMMED are excluded')")
def runner(t):
 assert t.count('MAX_CUTOFF=1794744900')==1
 t=t.replace('MAX_CUTOFF=1794744900  # 2026-11-15 12:15 UTC, never a rolling horizon.',
             'MAX_CUTOFF=1794766500  # AI-only resumed deadline: 2026-11-15 18:15 UTC, never rolling.')
 t=t.replace("MODES=('PROGRAMMED','CONVENTIONAL_AI')","MODES=('CONVENTIONAL_AI',)")
 t=t.replace("paths=('puente/run_comparador_C02_R02.py'","paths=('protocolo/PRESUPUESTO_AI_C02_R05.json','puente/run_comparador_C02_R03.py'")
 block='''def budget_preflight():
    budget=read(BASE/'protocolo/PRESUPUESTO_AI_C02_R05.json')
    need(budget.get('schema')=='DEE.RBX01.C02.AI_resumed_budget.R05'
         and budget.get('AI_absolute_cutoff_epoch')==MAX_CUTOFF
         and budget.get('new_Native_ticks_authorized')==0
         and budget.get('AI_opportunities')==18
         and budget.get('global_LLM_call_limit')==128
         and budget.get('quota_reset_authorized')is False,
         'Exact resumed AI-only budget required')
    return budget

'''
 assert t.count('def preflight(args):')==1 and t.count('def prepare_config(args):')==1
 t=t.replace('def preflight(args):','def preflight(args):\n    budget_preflight()')
 t=t.replace('def prepare_config(args):','def prepare_config(args):\n    budget_preflight()')
 return t.replace('def preflight(args):',block+'def preflight(args):')
files=[changed_file('control/orquestar_comparador_C02_R04.py','control/orquestar_comparador_C02_R05.py',orq),
       changed_file('puente/run_comparador_C02_R02.py','puente/run_comparador_C02_R03.py',runner)]
budget=dict(schema='DEE.RBX01.C02.AI_resumed_budget.R05',created_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),
 reason='Execution was interrupted awaiting system approval. Root resumed at15:34UTC and prospectively authorized the remaining AI comparison until18:15UTC.',
 previous_absolute_finish_epoch=OLD,previous_absolute_finish_utc='2026-11-15T12:15:00+00:00',
 previous_finish_was_not_met=True,actual_interruption_and_system_approval_record_required=True,
 AI_absolute_cutoff_epoch=NEW,AI_absolute_cutoff_utc='2026-11-15T18:15:00+00:00',rolling_extension=False,
 new_Native_ticks_authorized=0,Native_experiment_already_closed_at_tick=975547,
 Native_cutoff_not_extended=True,PROGRAMMED_already_closed_opportunities=18,
 AI_opportunities=18,AI_suspend_after=6,AI_reserved_opportunities=[13,18],
 global_LLM_call_limit=128,quota_reset_authorized=False,
 quota_file='comparadores/CUOTA_LLM_C02.json',prior_calls_and_reservations_preserved=True,
 policy_unchanged='comparadores/adaptadores_C02.py',policy_sha256='b210c39efeae0f65fb91166cff7bbbe26f071f317ab78e6fd151e2ef5a730f1b',
 client_unchanged='comparadores/cliente_ia_local_C02.py',client_sha256='b3328ab94b2d458568c1f0bc1ef84328b1105280bac11716b37b336658f0a85c',
 relay_unchanged='control/studio_mailbox_relay_C02_R04.py',
 files=files,scientific_criteria_changed=False,Native_calls_during_preparation=0,model_calls_during_preparation=0,
 private_config_written_during_preparation=False)
out=ROOT/'protocolo/PRESUPUESTO_AI_C02_R05.json';assert not out.exists();out.write_text(json.dumps(budget,indent=2)+'\n',encoding='utf8')
print(json.dumps(dict(files=files,budget=str(out),budget_sha256=digest(out)),indent=2))
