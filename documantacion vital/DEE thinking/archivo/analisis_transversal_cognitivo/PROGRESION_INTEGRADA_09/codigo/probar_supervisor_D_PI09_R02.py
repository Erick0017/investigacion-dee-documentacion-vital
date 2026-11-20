"""Pure plan/guards tests; no world/card/ledger/Owner execution."""
from pathlib import Path
import ast,importlib.util,json,sys
H=Path(__file__).resolve().parent;P=H.parent
s=importlib.util.spec_from_file_location('D_supervisor_pure',H/'ejecutar_D_PI09_R02.py');m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
outdir=P/'control/PRUEBA_PLAN_D_FAKE_R02C';outdir.mkdir(exist_ok=False);fake=outdir/'SELLO_MOCK.json';fake.write_text('{}',encoding='utf8');m.SEAL=fake;m.ADOPTED=fake
seal={'source_prefix':{'tick':910000},'first_milestone_adoption_sha256':'a'*64,'arms':{'real':'DISCOVERY','none':'NONE','yoked':'YOKE'},'native_reproduction_ids':['DREPRO']};protocol={'schedule':[{}]*12}
checks=[]
def check(name,ok):
    if not ok:raise AssertionError(name)
    checks.append(name)
def reject(name,fn):
    try:fn()
    except ValueError:checks.append(name);return
    raise AssertionError(name)
system=P/'estados/FAKE_NOT_CREATED/sistema'
real=m.make_plan(seal,protocol,'real',system,'PI09_D_FAKE_REAL','completo',0,6,910000)
check('research6_default_bound15063',real['finite_bound']==15063 and not real['explicitly_consumes_future_stock']and real['remaining_declared_D_stock_if_completed']==6)
allreal=m.make_plan(seal,protocol,'real',system,'PI09_D_FAKE_ALL','completo',0,12,910000)
check('real12_capacity_explicit_noreset',allreal['finite_bound']==30123 and allreal['explicitly_consumes_future_stock']and allreal['remaining_declared_D_stock_if_completed']==0)
prep=m.make_plan(seal,protocol,'none',system,'PI09_D_FAKE_PREP','preparar',0,6,910000)
check('prepare1birth3separate',prep['finite_bound']==3 and len(prep['steps'])==3 and prep['steps'][1]['require_ready'])
cont=m.make_plan(seal,protocol,'real',system,'PI09_D_FAKE_CONT','evaluar',6,8,923000)
check('continuation_keeps6_to8',cont['finite_bound']==5020 and cont['from_ordinal']==6 and cont['until_ordinal_exclusive']==8 and all(v['literal']['modo']!=m.PREPARE for v in cont['steps']))
reject('controls_never_more6',lambda:m.make_plan(seal,protocol,'none',system,'PI09_D_FAKE_BAD','completo',0,7,910000))
reject('no_prepare_counter_reset',lambda:m.make_plan(seal,protocol,'real',system,'PI09_D_FAKE_BAD','completo',1,6,910000))
reject('no_stale_source_prepare',lambda:m.make_plan(seal,protocol,'real',system,'PI09_D_FAKE_BAD','preparar',0,6,910001))
reject('no_yoke_without_actual_plan',lambda:m.make_plan(seal,protocol,'yoked',system,'PI09_D_FAKE_BAD','preparar',0,6,910000))
plan={'schema':'DEE.PI09.D.yoked_return.fixed_permutation.v1','permutation':[2,0,4,1,5,3],'source_failed':[True,False,False,False,False,False],'values':[False,True,False,False,False,False],'source_evidence_sha256':'b'*64}
yoke=m.make_plan(seal,protocol,'yoked',system,'PI09_D_FAKE_YOKE','completo',0,6,910000,json.dumps(plan))
check('actual_yoke_plan_passed_only_control',json.loads(yoke['steps'][1]['literal']['plan'])==plan)
check('no_expected_answer_in_actual_literals',all(set(v['literal'])=={'modo'}for v in real['steps']if v['label'].startswith('D_EP')))
text=(H/'ejecutar_D_PI09_R02.py').read_text('utf-8-sig');ast.parse(text)
check('ledger_bb1f_pinned_no_native_import',m.LEDGER_SHA=='bb1f326aa981ba00b9a6e3417700cca31d92a0d28a6e8a5ad601042bf2a26260'and'import dee_thinking'not in text)
check('budget_reads_current_registration','ledger[\'world_count\']<=budget[\'diagnostic_worlds_all_new\']'in text)
check('world_path_never_created',not system.exists())
check('DEE_not_imported',not any(v=='dee_thinking'or v.startswith('dee_thinking.')for v in sys.modules))
proof={'schema':'DEE.PI09.D.supervisor.pure_plan_tests.R02','passed':True,'Native_executed':False,'DEE_imported':False,'worlds_or_cards_read':False,'ledger_function_executed':False,'fixture_MOCK_ONLY_NOT_NATIVE':True,'checks':checks,'count':len(checks),'supervisor_sha256':m.sha(H/'ejecutar_D_PI09_R02.py')}
file=P/'control/PRUEBAS_SUPERVISOR_D_PI09_R02_COMMITTED.json'
with file.open('x',encoding='utf8')as f:json.dump(proof,f,indent=2);f.write('\n')
print(json.dumps({'passed':True,'checks':len(checks),'sha256':m.sha(file)}))
