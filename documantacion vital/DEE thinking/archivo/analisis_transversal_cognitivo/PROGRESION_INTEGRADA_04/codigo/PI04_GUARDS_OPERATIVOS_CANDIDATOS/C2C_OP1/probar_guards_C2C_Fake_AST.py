"""Static/fake-only permissions. No DEE, Native, live state or deployment."""
from pathlib import Path
from types import SimpleNamespace
import ast,copy,hashlib,json,runpy,sys
BASE=Path(__file__).resolve().parent;P4=BASE.parents[2];SRC=P4/'estados/candidato_R02/sistema/capacidades'
def sha(b):return hashlib.sha256(b).hexdigest()
def main():
 prep=json.loads((BASE/'PREPARACION_CANDIDATA.json').read_text(encoding='utf-8'))
 before={n:sha((SRC/n).read_bytes())for n in prep['fixed_dependencies_NOT_modified']}
 fake=P4/'control/PI04_C2C_GUARDS_FAKE_LOCAL';system=fake/'sistema'
 if fake.exists():raise FileExistsError('Preserve prior fake test')
 life='ECI02_PI03_REPRO_PI04_MAIN_02';other='ECI02_PI03_REPRO_PI04_C2C_CONTROL_01';home=system/'estado/servicios_locales'/life;home.mkdir(parents=True)
 (system/'estado/ACTIVO.json').write_text(json.dumps({'life_id':life}),encoding='utf-8')
 b=runpy.run_path(str(BASE/'pi04_coordinacion_central_C2C.py'),run_name='fake_B_guard_module')
 hw=runpy.run_path(str(SRC/'progresion_integrada_03_R01.py'),run_name='fake_original_hardware_module')
 r01=json.loads((SRC/'PROTOCOLO_PI03_R01.json').read_text(encoding='utf-8'))
 hw['_identity'].__globals__['_decode']=json.loads
 hardware=SimpleNamespace(protocol=lambda:(r01,'frozen_hw_protocol'),_identity=hw['_identity'],_get=lambda a:{'ready':True,'pending':None,'uncertain':False})
 ph=sha((SRC/'PROTOCOLO_PI04_C2C_R01.json').read_bytes());p={'status':'SEALED_FOR_EVALUATION'}
 g=b['_identity'].__globals__;g['_hardware']=lambda:hardware;g['_decode']=json.loads;g['protocol']=lambda **kw:(p,ph);g['_system_root']=lambda:system
 def adapter(identifier=life,**changes):
  state={'version':b['VERSION'],'life_id':identifier,'ready':True,'admitted':True,'arm':'real','pending':None,'uncertain':False,'halted_reason':None,'calibrations':[],'protocol_sha256':ph,'ordinal':22}
  state.update(changes);entries={hw['SYSTEM_KEY']:json.dumps({'life_id':identifier}),b['KEY']:json.dumps(state)}
  return SimpleNamespace(world=SimpleNamespace(runtime=SimpleNamespace(dimension=67,snapshot_metadata_entries=entries)))
 tests=[]
 def check(name,fn,should_allow):
  try:value=fn();allowed=True;error=None
  except Exception as e:value=None;allowed=False;error=type(e).__name__+': '+str(e)
  if allowed!=should_allow:raise AssertionError(name+' wrong permission '+str(error))
  tests.append({'name':name,'allowed':allowed,'expected':should_allow,'error':error})
 a=adapter()
 check('actual_old_hardware_none_validates_identity',lambda:hardware._identity(a,r01),True)
 check('actual_old_hardware_owned_home_refuses_ACTIVO',lambda:hardware._identity(a,r01,home),False)
 for operation in(b['OPPORTUNITY'],b['STATE']):
  check('adopted_exact_closed_'+operation,lambda op=operation:g['_identity'](a,home,operation=op),True)
 for operation in(b['PREPARE'],b['ADMIT'],b['CALIBRATE'],b['CUT_CONTEXT'],None):
  check('adopted_forbidden_'+str(operation),lambda op=operation:g['_identity'](a,home,operation=op),False)
 for label,change in [('not_admitted',{'admitted':False}),('not_ready',{'ready':False}),('uncertain',{'uncertain':True}),('pending',{'pending':{'id':'unreconciled'}}),('halted',{'halted_reason':'NULL preserved'}),('yoked',{'arm':'yoked'}),('protocol_mismatch',{'protocol_sha256':'wrong'}),('calibration_history',{'calibrations':[{'value':4}]})]:
  check('adopted_rejects_'+label,lambda change=change:g['_identity'](adapter(**change),home,operation=b['OPPORTUNITY']),False)
 wrong=fake/'wrong_parent'/life;wrong.mkdir(parents=True)
 check('adopted_wrong_home_rejected',lambda:g['_identity'](a,wrong,operation=b['OPPORTUNITY']),False)
 otherhome=system/'estado/servicios_locales'/other;otherhome.mkdir()
 check('inactive_diagnostic_original_path_preserved',lambda:g['_identity'](adapter(other),otherhome,operation=b['PREPARE']),True)
 (system/'estado/ACTIVO.json').write_text(json.dumps({'life_id':other}),encoding='utf-8')
 check('different_ACTIVO_id_not_whitelisted',lambda:g['_identity'](adapter(other),otherhome,operation=b['OPPORTUNITY']),False)
 # The unchanged original sensor accepts the exact transported identity prefix;
 # inject only a fake Native tuple, never import the real engine.
 sensor=runpy.run_path(str(SRC/'pi04_selector_contextual_C2_R01.py'),run_name='fake_unchanged_sensor')
 sensor['_guard'].__globals__['_native']=lambda:(object(),object(),object(),json.loads,object())
 check('unchanged_sensor_identity_prefix_already_accepts_exact_id',lambda:sensor['_guard'](adapter()),True)
 # E3 changes only the readonly dependency route, not its material permission.
 e=runpy.run_path(str(BASE/'pi04_e3_contingencia.py'),run_name='fake_E3_guard_module');eg=e['_identity'].__globals__;calls=[]
 class Task:__file__=str(SRC/'pi03_tarea_diferida_R02.py')
 eg['_task']=lambda:Task()
 def task_guard(a,directory=None,*,material=True):
  calls.append(material)
  if material:raise ValueError('ACTIVO still refused for E3 material')
  return {},'frozen',{'origin':[19,54,5]},{'life_id':life}
 eg['_guard']=task_guard
 check('E3_readonly_dependency_identity_allowed',lambda:eg['_identity'](a,home,material=False),True)
 check('E3_material_identity_still_refused',lambda:eg['_identity'](a,home),False)
 # Check actual function deltas and dependency guards without running any body.
 changed=json.loads((BASE/'PREPARACION_CANDIDATA.json').read_text(encoding='utf-8'))['changes']
 for name in('pi04_coordinacion_central_C2C.py','pi04_e3_contingencia.py'):
  old=ast.parse((BASE/'ANTES'/name).read_text(encoding='utf-8-sig'));new=ast.parse((BASE/name).read_text(encoding='utf-8'))
  old_functions={n.name:n for n in old.body if isinstance(n,ast.FunctionDef)};new_functions={n.name:n for n in new.body if isinstance(n,ast.FunctionDef)}
  actual=[k for k,v in old_functions.items()if ast.dump(v)!=ast.dump(new_functions.get(k))]
  if actual!=changed[name]['changed_existing_functions']:raise AssertionError('Unlisted function mutation')
 oldbody=next(n for n in ast.parse((BASE/'ANTES/pi04_coordinacion_central_C2C.py').read_text(encoding='utf-8-sig')).body if isinstance(n,ast.FunctionDef)and n.name=='_opportunity_body')
 newbody=next(n for n in ast.parse((BASE/'pi04_coordinacion_central_C2C.py').read_text(encoding='utf-8')).body if isinstance(n,ast.FunctionDef)and n.name=='_opportunity_body')
 for node in ast.walk(newbody):
  if isinstance(node,ast.Call)and isinstance(node.func,ast.Name)and node.func.id=='_identity':node.keywords=[k for k in node.keywords if k.arg!='operation']
 if ast.dump(oldbody)!=ast.dump(newbody):raise AssertionError('Scientific opportunity body changed beyond permission keyword')

 old_text=(BASE/'ANTES/pi04_coordinacion_central_C2C.py').read_text(encoding='utf-8-sig')
 new_text=(BASE/'pi04_coordinacion_central_C2C.py').read_text(encoding='utf-8')
 old_ast=ast.parse(old_text);new_ast=ast.parse(new_text)
 def node_named(tree,name):return next(n for n in tree.body if isinstance(n,(ast.FunctionDef,ast.ClassDef))and n.name==name)
 scientific_exact={name:ast.dump(node_named(old_ast,name))==ast.dump(node_named(new_ast,name))for name in ('Device','_motor','_operation','_native_input_summary','opportunity')}
 if not all(scientific_exact.values()):raise AssertionError('Scientific helper/Device/quality gate changed')
 def native_calls(tree):
  n=node_named(tree,'_opportunity_body')
  return [ast.unparse(x)for x in ast.walk(n)if isinstance(x,ast.Call)and not(isinstance(x.func,ast.Name)and x.func.id=='_identity')]
 calls_equal=native_calls(old_ast)==native_calls(new_ast)
 if not calls_equal:raise AssertionError('Scientific Native/helper calls or order changed')
 frozen=json.loads((SRC/'PROTOCOLO_PI04_C2C_R01.json').read_text(encoding='utf-8'))['dependencies_sha256']
 frozen_current={name:sha((SRC/name).read_bytes())for name in frozen}
 if frozen_current!=frozen:raise AssertionError('A C2C pinned dependency changed')
 if 'pi04_coordinacion_central_C2C.py'in frozen or 'pi04_e3_contingencia.py'in frozen:raise AssertionError('Own guard patch must not rewrite a pinned dependency')
 current={n:sha((SRC/n).read_bytes())for n in before}
 if current!=before:raise ValueError('Frozen dependency changed concurrently; reconcile')
 imported=[n for n in sys.modules if n=='app'or n.startswith(('app.','dee_thinking'))]
 if imported:raise AssertionError('Native/app imported')
 proof={'schema':'PI04.C2C.operational_guards.fake_AST_verified.NOT_DEPLOYED.v1','tests':tests,'count':len(tests),'scientific_C2C_opportunity_AST_equal_except_explicit_permission_keyword':True,'C2C_body_bytes_identical':False,'C2C_body_change':'Only _identity(a,directory,operation=OPPORTUNITY), an explicit administrative permission keyword; zero Native call/data/reader/clock changes','scientific_helpers_and_Device_AST_exact':scientific_exact,'Native_helper_calls_and_order_exact':calls_equal,'all_protocol_pinned_sources_exact':frozen_current,'E3_guard_material_flags':calls,'fixed_sources_unchanged':current,'candidate_source_hashes':{n:sha((BASE/n).read_bytes())for n in('pi04_coordinacion_central_C2C.py','pi04_e3_contingencia.py')},'DEE_or_app_modules':imported,'Native_ticks':0,'product_or_S2_modified':False,'Native_postpromotion_use_verified':False,'scope':'Permission logic only with fake metadata, fake owned home and unchanged hardware/sensor function bodies. Native current-state compatibility and complete-home continuity remain Root verification after valid adoption.'}
 out=BASE/'PRUEBAS_FAKE_AST.json';out.write_text(json.dumps(proof,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 print(json.dumps({'proof':str(out),'bytes':out.stat().st_size,'sha256':sha(out.read_bytes()),'fake_cases':len(tests),'DEE_imports':0,'Native_ticks':0,'deployed':False},ensure_ascii=False,indent=2))
if __name__=='__main__':main()
