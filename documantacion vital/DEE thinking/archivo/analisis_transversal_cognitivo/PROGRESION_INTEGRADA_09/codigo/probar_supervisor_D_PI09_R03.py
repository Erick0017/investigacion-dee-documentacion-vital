"""Pure technical bound tests. No world/card/ledger/Owner or actual seal read."""
from pathlib import Path
import copy,hashlib,importlib.util,json,sys
H=Path(__file__).resolve().parent;P=H.parent
s=importlib.util.spec_from_file_location('D_supervisor_R03_pure',H/'ejecutar_D_PI09_R03.py');m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
protocol=json.loads((H/'PROTOCOLO_PI09_D_R02.json').read_text('utf8'))
seal={'source_prefix':{'tick':910000},'first_milestone_adoption_sha256':'a'*64,'arms':{'real':'DISCOVERY','none':'NONE','yoked':'YOKE'},'native_reproduction_ids':['DREPRO']}
actual_sha=m.sha;m.sha=lambda _: 'f'*64
checks=[]
def check(name,v):
    assert v,name
    checks.append(name)
def reject(name,fn):
    try:fn()
    except ValueError:checks.append(name);return
    raise AssertionError(name)
system=P/'estados/FAKE_NOT_CREATED_R03/sistema'
real=m.make_plan(seal,protocol,'real',system,'PI09_D_FAKE_R03_REAL','completo',0,12,910000)
eval6=m.make_plan(seal,protocol,'real',system,'PI09_D_FAKE_R03_EVAL','completo',0,6,910000)
check('Actual core2110 plus wait0/400, not universal2510', [v['max_ticks']for v in real['steps']if'ordinal'in v]==[2110,2110,2110,2510,2110,2110,2110,2110,2510,2110,2110,2110])
check('Real12 incl prep3 =26123',real['finite_bound']==26123)
check('Evaluation6 incl prep3 =13063',eval6['finite_bound']==13063)
check('Real12 None6 Yoke6 Replay12 =78372 including4prep',2*real['finite_bound']+2*eval6['finite_bound']==78372)
check('Remaining future6 is explicit after evaluation',eval6['remaining_declared_D_stock_if_completed']==6 and not eval6['explicitly_consumes_future_stock'])
cont=m.make_plan(seal,protocol,'real',system,'PI09_D_FAKE_R03_CONT','evaluar',6,9,925000)
check('Continuation includes wait only at8',cont['finite_bound']==6730 and cont['from_ordinal']==6)
check('Literal actor inputs unchanged',all(v['literal']=={'modo':m.EPISODE}for v in real['steps']if'ordinal'in v))
bad=copy.deepcopy(protocol);bad['schedule'][0]['wait_ticks']=-1
reject('Negative undeclared wait rejected',lambda:m.opportunity_bound(bad,0))
bad=copy.deepcopy(protocol);bad['max_ticks_per_C_opportunity']=2000
reject('Core bound cannot be reduced below actual API2110',lambda:m.opportunity_bound(bad,0))
bad=copy.deepcopy(protocol);bad['max_ticks_per_whole_D_opportunity']=2509
reject('Whole2510 cap remains exact',lambda:m.opportunity_bound(bad,3))
reject('Controls cannot consume future7',lambda:m.make_plan(seal,protocol,'none',system,'PI09_D_FAKE_R03_BAD','completo',0,7,910000))
check('No world created or DEE imported',not system.exists()and not any(x=='dee_thinking'or x.startswith('dee_thinking.')for x in sys.modules))
proof={'schema':'DEE.PI09.D.technical_supervisor_bound.pure_tests.R03','passed':True,'checks':checks,'count':len(checks),'Native_executed':False,'DEE_imported':False,'worlds_cards_ledger_or_actual_seal_read':False,'mock_plan_only':True,'driver_sha256':actual_sha(H/'ejecutar_D_PI09_R03.py'),'actor_sha256':actual_sha(H/'pi09_entorno_persistente_D_R02.py'),'protocol_sha256':actual_sha(H/'PROTOCOLO_PI09_D_R02.json'),'full_four_run_bound':78372,'evaluation_run_bound':13063,'real_or_replay12_bound':26123}
out=P/'control/PRUEBAS_SUPERVISOR_D_PI09_R03.json'
with out.open('x',encoding='utf8')as f:json.dump(proof,f,ensure_ascii=False,indent=2);f.write('\n')
print(json.dumps({'passed':True,'count':len(checks),'proof':str(out),'sha256':actual_sha(out)}))
