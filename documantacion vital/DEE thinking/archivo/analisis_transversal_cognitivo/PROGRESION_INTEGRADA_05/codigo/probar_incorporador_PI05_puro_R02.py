"""Passive guards and mocked migration comparison; never import Native."""
from pathlib import Path
import ast,copy,hashlib,importlib.util,json,types
P=Path(__file__).resolve().parents[1];SRC=P/'codigo/incorporar_PI05.py';OUT=P/'control/INCORPORADOR_PI05_PRUEBAS_PURAS_R02.json'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def need(x,s):
 if not x:raise AssertionError(s)
def reject(fn):
 try:fn()
 except (ValueError,FileNotFoundError):return True
 raise AssertionError('Expected refusal absent')
if __name__=='__main__':
 need(not OUT.exists(),'No overwrite')
 sp=importlib.util.spec_from_file_location('pi05_incorporator_pure',SRC);m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m)
 tree=ast.parse(SRC.read_text());need(not any(isinstance(n,ast.ImportFrom)and n.module and(n.module.startswith('dee_thinking')or n.module.startswith('app'))for n in tree.body),'No top-level DEE import')
 def compare(a,b,allow_service=False):
  need(a['physical']==b['physical']and a['causal_prefix_sha256']==b['causal_prefix_sha256'],'Full fake causalprefix differs')
  if a['metadata']!=b['metadata']:raise ValueError('Unknown metadata difference')
  return {'physical_equal':True,'causal_prefix_equal':True,'new_ticks':0}
 original={'physical':{'N':67,'tick':999999},'causal_prefix_sha256':'c'*64,'metadata':{m.C2C_KEY:json.dumps({'life_id':m.ORIGIN_C2C_LIFE,'rows':[{'actual':7}],'ordinal':28}),'unchanged':'historical'}}
 imported=copy.deepcopy(original);cap=json.loads(imported['metadata'][m.C2C_KEY]);cap['life_id']=m.LIFE;imported['metadata'][m.C2C_KEY]=json.dumps(cap)
 valid=m.compare_migration_native(types.SimpleNamespace(compare_native=compare),original,imported)
 invalid=copy.deepcopy(imported);bad=json.loads(invalid['metadata'][m.C2C_KEY]);bad['rows'][0]['actual']=8;invalid['metadata'][m.C2C_KEY]=json.dumps(bad)
 refusals={'changed_acquired_row':reject(lambda:m.compare_migration_native(types.SimpleNamespace(compare_native=compare),original,invalid))}
 invalid=copy.deepcopy(imported);invalid['metadata']['unknown']='new';refusals['extra_metadata']=reject(lambda:m.compare_migration_native(types.SimpleNamespace(compare_native=compare),original,invalid))
 invalid=copy.deepcopy(imported);invalid['physical']['tick']+=1
 # Above the fake parser raises AssertionError, exactly like a physical invariant,
 # so test it separately rather than misclassify that exception as a valid import.
 try:m.compare_migration_native(types.SimpleNamespace(compare_native=compare),original,invalid)
 except AssertionError:refusals['tick_changed']=True
 else:raise AssertionError('Changed tick was accepted')
 baselines=[{'file':n,'sha256':sha(m.C/n)}for n in sorted(m.CAS_REQUIRED)];d={'product_cas_baselines':baselines};cas=m.check_selector_CAS(d)
 bad=copy.deepcopy(d);bad['product_cas_baselines'][0]['sha256']='0'*64;refusals['changed_selector']=reject(lambda:m.check_selector_CAS(bad))
 bad=copy.deepcopy(d);bad['product_cas_baselines'].pop();refusals['missing_selector']=reject(lambda:m.check_selector_CAS(bad))
 parent=m.protect_parent();need(parent['physical']['tick']==775355 and parent['snapshot_sha256']==m.PARENT_SHA,'Real selected parent differs')
 # Static call order and synthetic contract transaction: not a Native promotion.
 functions={n.name:n for n in tree.body if isinstance(n,ast.FunctionDef)}
 def calls(node,name):return [n for n in ast.walk(node)if isinstance(n,ast.Call)and((isinstance(n.func,ast.Name)and n.func.id==name)or(isinstance(n.func,ast.Attribute)and n.func.attr==name))]
 need(not calls(functions['prepare'],'apply_contracts'),'Preparation must never activate selected permission')
 need(min(x.lineno for x in calls(functions['adopt'],'apply_contracts'))>min(x.lineno for x in calls(functions['adopt'],'promote')),'Permission must follow actual promotion branch')
 root=P/'control/INCORPORACION_ORDEN_MOCK_R02';need(not root.exists(),'Fresh mock transaction only');root.mkdir()
 m.S=root/'synthetic_system';m.CONTROL=root/'synthetic_control';m.BACKUP=root/'synthetic_backup';(m.S/'estado').mkdir(parents=True);m.CONTROL.mkdir()
 (m.S/'estado/ACTIVO.json').write_text(json.dumps({'life_id':m.LIFE}),encoding='utf8')
 decision=m.CONTROL/'DECISION_PROMOCION_PRODUCTO_PI05.json';decision.write_text(json.dumps({'simulation_only':True}),encoding='utf8')
 plan={'new_contract':{'file':'contratos/PI05_C2C_USO_PRINCIPAL_01.json','product_before_sha256':None,'document':{'schema':'DEE.PI05.C2C.exact_adopted_permission.v1','life_id':m.LIFE,'profile':'fisica_directa','requires_environment30':True,'allowed_modes':['eci01-pi04-c2c-oportunidad','eci01-pi04-c2c-estado']}},'catalog_entry':{'id':'PI05_MOCK'},'decision_id':'PI05_MOCK'}
 rec={'snapshot_sha256':'c'*64,'physical':{'N':67,'tick':999999}}
 m.check_json_plans(plan);contract=m.S/'contratos/PI05_C2C_USO_PRINCIPAL_01.json'
 refusals['permission_before_actual_commit']=reject(lambda:m.apply_contracts(plan,rec));need(not contract.exists(),'No permission file before real matching journal')
 row={'phase':'COMMITTED','decision_id':'PI05_MOCK','life_id':m.LIFE,'snapshot_sha256':rec['snapshot_sha256'],'simulation_only_not_Native':True}
 (m.S/'estado/PROMOCIONES.jsonl').write_text(json.dumps(row)+'\n',encoding='utf8')
 written=m.apply_contracts(plan,rec);actual=json.loads(contract.read_text());need(actual['status']=='COMMITTED'and actual['adoption_decision_sha256']==sha(decision)and actual['actual_native_commit_witness']==row,'Permission uses actual matching synthetic journal and decision hash only')
 contract_test={'all_inputs_are_mocks':True,'actual_Native_promotions':0,'prepare_no_contract_call':True,'adopt_permission_after_promote':True,'refused_before_matching_journal':True,'simulated_matching_commit_written_contract':written,'actual_decision_sha256':sha(decision)}
 result={'schema':'DEE.PI05.incorporator.pure_guards.v1','Native_ticks':0,'DEE_imports':0,'product_or_S5_writes':0,'source_sha256':sha(SRC),'mock_comparison':valid,'permission_order_and_transaction':contract_test,'refusals':refusals,'actual_six_selector_CAS_readonly_checked':cas,'actual_parent_readonly_verified':{'life_id':m.PARENT,'N':67,'tick':775355,'snapshot_sha256':m.PARENT_SHA},'prepare_adopt_not_executed':True,'final_decision_not_created':True}
 OUT.write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf8');print(json.dumps({'proof':str(OUT),'sha256':sha(OUT),'Native_ticks':0,'all_refusals':all(refusals.values())}))
