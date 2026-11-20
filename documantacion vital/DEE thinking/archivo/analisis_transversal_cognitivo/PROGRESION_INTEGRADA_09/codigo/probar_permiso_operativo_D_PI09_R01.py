"""Pure prospective D lifecycle/transport tests; no DEE or real state reads."""
from pathlib import Path
import ast,copy,hashlib,importlib.util,json,types
H=Path(__file__).resolve().parent;P=H.parent;C=P.parents[2]/'DEE Cognitive 2.0';OUT=H/'PRUEBA_PERMISO_OPERATIVO_D_PI09_R01'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def write(p,v):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(v,indent=2)+'\n','utf8')
def load(name,file):
 sp=importlib.util.spec_from_file_location(name,file);m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m);return m
def main():
 if OUT.exists():raise FileExistsError('Prior proof preserved')
 OUT.mkdir();m=load('D_permission_pure',H/'pi09_permiso_operativo_D_R01.py');m.__file__=str(OUT/'FAKE/sistema/capacidades/pi09_permiso_operativo_D_R01.py');root=Path(m.__file__).parents[1]
 for name,digest in m.PINS.items():
  source=H/name
  if not source.is_file():source=C/'sistema/capacidades'/name
  assert sha(source)==digest;target=root/'capacidades'/name;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(source.read_bytes())
 contract={'schema':'DEE.PI09.D.exact_operational_permission.v2','status':'PREPARED_DIAGNOSTIC','life_id':m.LIFE,'profile':'fisica_directa','protocol_sha256':m.PINS['PROTOCOLO_PI09_D_R02.json'],'allowed_modes':[m.D_EP,m.D_STATE],'frozen_files_sha256':m.PINS,'all_outer_FI_requests':True,'public_FI_domain':[0,20],'public_FI_backend':'explicit_FI8_same_frozen_body','internal_C2C_FI_redirected':False,'C2C_protocol_sha256':m.C2C_PROTOCOL,'historical_R02_material_disabled':True,'historical_PI07_material_disabled':True,'public_arithmetic_policy':'legacy_partial','all_adoption_gates_met':True,'adoption_decision_sha256':None}
 write(root/'contratos'/m.CONTRACT,contract);write(root/'estado/ACTIVO.json',{'life_id':m.PREDECESSOR})
 current={'life_id':m.LIFE,'profile':'fisica_directa'};meta={'version':'DEE.PI09.persistent_environment.D.R02','ordinal':11,'rows':[{}]*11,'sample_register':None,'ready':True,'pending':None,'uncertain':None,'control':{'arm':'real','query_policy':'native','information_policy':'real'}};old={'ordinal':12,'rows':[{}]*12,'ready':True,'pending':None,'uncertain':None}
 def adapter():return types.SimpleNamespace(world=types.SimpleNamespace(runtime=types.SimpleNamespace(dimension=67,snapshot_metadata_entries=((m.SYSTEM,json.dumps(current)),(m.KEY,json.dumps(meta)),(m.OLDKEY,json.dumps(old))))))
 checks=[]
 def check(name,call,expected=True):
  try:call();actual=True
  except(ValueError,KeyError):actual=False
  if actual!=expected:raise AssertionError(name)
  checks.append({'name':name,'passed':True,'accepted':actual})
 check('exact_PREPARED_Discovery_before_selection',lambda:m.validate_prepared_load(adapter()))
 for operation in('reanudar','pausar','guardar','detener'):check('PREPARED_control_'+operation,lambda operation=operation:m.validate_external(adapter(),None,payload={'operacion':operation}))
 for mode in(m.D_STATE,'eci01-pi09-estado',m.FI8_STATE,'eci01-pi04-c2c-estado'):
  row={'modo':mode};check('PREPARED_STATE_'+mode,lambda row=row:m.validate_external(adapter(),row,payload={'operacion':'sesion','situaciones':[row],'retorno':'omit','actuador':'closed'}))
 for payload,row in(({'operacion':'avanzar','ticks':1},None),({'operacion':'exportar'},None),({'operacion':'sesion','situaciones':[{'modo':m.D_EP}],'retorno':'omit','actuador':'closed'},{'modo':m.D_EP}),({'operacion':'detener','extra':1},None)):
  check('PREPARED_reject_'+str(payload),lambda payload=payload,row=row:m.validate_external(adapter(),row,payload=payload),False)
 write(root/'estado/ACTIVO.json',{'life_id':m.LIFE});check('selected_PREPARED_is_not_COMMITTED',lambda:m.profile(adapter()),False)
 contract['status']='COMMITTED';contract['adoption_decision_sha256']='1'*64;write(root/'contratos'/m.CONTRACT,contract);check('selected_exact_COMMITTED_real',lambda:m.profile(adapter()))
 for mode in(m.D_EP,m.D_STATE,m.FI8_QUERY,m.FI8_STATE,'eci01-pi09-estado'):
  check('selected_current_mode_'+mode,lambda mode=mode:m.validate_external(adapter(),{'modo':mode},payload={'operacion':'sesion','situaciones':[{'modo':mode}]}))
 for mode in('eci01-pi09-preparar','eci01-pi09-episodio','eci01-pi09-d-preparar','eci01-pi09-fi-lote-admitir','eci01-pi07-r03-episodio','eci01-pi07-fi-regulada','eci01-pi08-c2c-preparar'):
  check('selected_historical_or_supply_rejected_'+mode,lambda mode=mode:m.validate_external(adapter(),{'modo':mode},payload={'operacion':'sesion','situaciones':[{'modo':mode}]}),False)
 for role in('none','yoked','reference'):
  meta['control']['arm']=role;check('selected_control_'+role,lambda:m.profile(adapter()),False)
 meta['control']['arm']='real';old['ordinal']=13;check('historical_R02_counter_not_reinterpreted',lambda:m.profile(adapter()),False);old['ordinal']=12
 for left in range(21):
  for right in range(21):assert m.routes_public(adapter(),{'modo':'eci01-balance','izquierda':left,'derecha':right})
 checks.append({'name':'all441_external_FI_pairs_same_fixed_route_without_operand_or_expected_branch','passed':True})
 assert not m.routes_public(adapter(),{'modo':'eci01-aritmetica-directa','operacion':'sumar','izquierda':1,'derecha':7});checks.append({'name':'P0_guard_remains_disabled_no_gain','passed':True})
 proposal,leaf=m.propose_C2C_identity({'life_id':m.ANCESTRAL_C2C,'ordinal':31,'rows':[{'literal':True}],'device':'OLD_LITERAL','pending':None,'uncertain':None});assert proposal['life_id']==m.LIFE and proposal['ordinal']==31 and proposal['rows']==[{'literal':True}]and leaf['changed_paths']==['/life_id'];checks.append({'name':'C2C_only_identity_leaf_no_rows_device_ordinal_change','passed':True})
 builder=load('D_merge_pure',H/'preparar_delta_operativo_D_PI09_R01.py');source=(C/'sistema/app/mundo_genesis_apd05.py').read_text('utf-8-sig');merged=builder.patch_world(source);ast.parse(merged);assert merged.count('d_permission.validate_external(self.a,row,payload=payload)')==2 and merged.count('if d_transport.applies(self.a)')==15;checks.append({'name':'actual_current_product_world_merge_AST_both_payloads_and15_contextual_hooks','passed':True})
 assert 'pi09_transporte_heredado_R02' in merged and 'pi09_transporte_D_R02' in merged and 'pi09_permission.install()'in merged;checks.append({'name':'Native_scope_and_operator_route_preserved_alongside_D','passed':True})
 result={'schema':'DEE.PI09.D.conditional_operational_permission.pure_tests.R01','passed':len(checks),'checks':checks,'Native_executed':False,'DEE_imports':0,'real_states_or_SQLite_read':False,'scientific_actor_or_protocol_changed':False,'Root_D_actual_gates_still_required':True,'sources':{p.name:sha(p)for p in(H/'pi09_permiso_operativo_D_R01.py',H/'preparar_delta_operativo_D_PI09_R01.py')}}
 write(OUT/'RESULTADO.json',result);print(json.dumps({'passed':len(checks),'proof':str(OUT/'RESULTADO.json'),'sha256':sha(OUT/'RESULTADO.json'),'Native_executed':False}))
if __name__=='__main__':main()
