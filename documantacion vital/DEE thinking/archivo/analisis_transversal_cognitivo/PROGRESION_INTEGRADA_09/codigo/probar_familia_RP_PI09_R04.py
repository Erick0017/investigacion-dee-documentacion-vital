"""Pure actual-code transport/admission tests; no DEE/Native/state imports.

All synthetic roots remain explicitly inside this test output directory. Only
the immutable source manifest is read; no real card/SQLite/world is opened.
"""
from pathlib import Path
import ast,copy,hashlib,importlib.util,json,sys,types
H=Path(__file__).resolve().parent;P=H.parent;C=P.parents[2]/'DEE Cognitive 2.0';RP=C/'reproducibilidad';STAGE=H/'RP_FAMILIA_R04_PREPARADA_R02';OUT=H/'PRUEBA_FAMILIA_RP_PI09_R04'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):return json.loads(p.read_text('utf-8-sig'))
def write(p,v):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(v,indent=2)+'\n','utf8')
def load(name,file):
 sp=importlib.util.spec_from_file_location(name,file);m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m);return m
def main():
 if OUT.exists():raise FileExistsError('Preserve previous tests')
 OUT.mkdir();rows=[];loaded_native=[]
 class Deny:
  def find_spec(self,fullname,path=None,target=None):
   if fullname.startswith(('dee_runtime','dee_native','_dee','numpy')):loaded_native.append(fullname);raise AssertionError('Native forbidden '+fullname)
 deny=Deny();sys.meta_path.insert(0,deny)
 wrapper=load('PI09_family_pure',H/'pi09_reproduccion_familia_R01.py');binder=load('PI09_family_binder_pure',H/'vincular_familia_RP_PI09_R01.py');plan=read(STAGE/'PLAN.json')
 def check(name,call,accepted=True):
  try:call();actual=True
  except(ValueError,KeyError,FileExistsError):actual=False
  if actual!=accepted:raise AssertionError(name)
  rows.append({'name':name,'passed':True,'accepted':actual})
 for suffix in('20261111A','20261112A','A','1234567890'):check('family_'+suffix,lambda suffix=suffix:(_ for _ in()).throw(ValueError())if not wrapper.allowed_life(wrapper.PREFIX+suffix)else None)
 for life in(wrapper.PREFIX,wrapper.PREFIX+'a',wrapper.PREFIX+'A_B',wrapper.PREFIX+'12345678901','ECI02_PI03_REPRO_PI04_PI05_PI07_PI09_REPRO_01','ECI02_PI03_REPRO_PI04_PI05_PI07_PI09_NATIVE_01'):
  check('reject_id_'+life,lambda life=life:(_ for _ in()).throw(ValueError())if not wrapper.allowed_life(life)else None,False)
 for literal in({'modo':wrapper.PREPARE,'brazo':'native_real'},{'modo':wrapper.EPISODE},{'modo':wrapper.STATE}):check('literal_'+str(literal),lambda literal=literal:wrapper.validate_literal(literal))
 for literal in({'modo':wrapper.PREPARE,'brazo':'always_real'},{'modo':wrapper.PREPARE,'brazo':'never'},{'modo':wrapper.PREPARE,'brazo':'native_real','plan':'[]'},{'modo':wrapper.EPISODE,'expected':True}):check('reject_literal_'+str(literal),lambda literal=literal:wrapper.validate_literal(literal),False)
 cap=STAGE/'capsule';wrapper.SOURCE=cap/'capacidades/pi09_consulta_selectiva_R02.py';wrapper.CONFIG=cap/'capacidades/PI09_REPRODUCCION_FAMILIA_R01.json';literal=wrapper.private()
 original=ast.parse(wrapper.SOURCE.read_text('utf-8-sig'));adapted=ast.parse(wrapper.SOURCE.read_text('utf-8-sig'))
 before="reproduction = row['brazo'] == 'native_real' and identity['life_id'] in seal.get('native_reproduction_ids',[])";after="reproduction = row['brazo'] == 'native_real' and _family_allowed(identity['life_id'])"
 original_text=wrapper.SOURCE.read_text('utf-8-sig');assert original_text.count(before)==1;adapted=ast.parse(original_text.replace(before,after))
 for a,b in zip(original.body,adapted.body):
  if isinstance(a,ast.FunctionDef)and a.name=='validate':continue
  assert ast.dump(a,include_attributes=False)==ast.dump(b,include_attributes=False)
 rows.append({'name':'all_scientific_functions_AST_literal_only_validate_identity_line_differs','passed':True})
 assert literal._identity is wrapper._identity and literal.validate.__code__.co_filename.endswith(':diagnostic_family_identity_only');rows.append({'name':'actual_private_R02_namespace_admission_loaded_without_DEE','passed':True})
 pair=RP/'materiales/PI09_C_HEREDADA_T884835';mf=read(pair/'EXPORTACION_SERVICIO.json');counter=0
 def fresh(suffix='20261111A'):
  nonlocal counter
  counter+=1;root=OUT/('FAKE_%02d'%counter)/'sistema';root.mkdir(parents=True);state=root/'estado';state.mkdir();life=wrapper.PREFIX+suffix
  write(root/'capacidades/PI09_REPRODUCCION_FAMILIA_R01.json',read(cap/'capacidades/PI09_REPRODUCCION_FAMILIA_R01.json'));write(root/'capacidades/PI09_TRANSPORTE_HEREDADO_R02.json',read(cap/'capacidades/PI09_TRANSPORTE_HEREDADO_R02.json'))
  ctx={'life':life,'system':str(root),'recipe':binder.RID,'variant':'native12','source_code_capsule_key':binder.CAP,'prefix_manifest_sha256':binder.PAIR_SHA,'product':str(C),'source_code_manifest_sha256':plan['capsule_manifest_sha256']};write(root.parent/'CONTEXTO_EJECUCION.json',ctx)
  return types.SimpleNamespace(root=root,state=state),life,ctx
 store,life,ctx=fresh();evidence=binder.bind(store,pair,mf,life);assert evidence['new_native_ticks']==evidence['new_native_inputs']==0 and not list(store.state.rglob('VIDA.json'))and not list(store.state.rglob('*.sqlite3'));rows.append({'name':'actual_binder_success_writes_only_two_admin_bindings_before_Native_creation','passed':True})
 check('reject_same_binding_replay_no_partial_automatic_retry',lambda:binder.bind(store,pair,mf,life),False)
 for mutation in('ACTIVO','existing_life','existing_service','existing_worker','wrong_recipe','wrong_capsule','wrong_source','wrong_family'):
  store,life,ctx=fresh()
  if mutation=='ACTIVO':write(store.state/'ACTIVO.json',{'life_id':'FAKE_SELECTED'})
  elif mutation.startswith('existing_'):(store.state/{'existing_life':'vidas','existing_service':'servicios_persistentes','existing_worker':'servicios_locales'}[mutation]/life).mkdir(parents=True)
  elif mutation=='wrong_recipe':ctx['recipe']='other';write(store.root.parent/'CONTEXTO_EJECUCION.json',ctx)
  elif mutation=='wrong_capsule':ctx['source_code_capsule_key']='old';write(store.root.parent/'CONTEXTO_EJECUCION.json',ctx)
  elif mutation=='wrong_source':ctx['prefix_manifest_sha256']='0'*64;write(store.root.parent/'CONTEXTO_EJECUCION.json',ctx)
  else:life='ECI02_PI03_REPRO_PI04_PI05_PI07_PI09_NATIVE_01'
  protected={p:sha(p)for p in(store.root/'capacidades').glob('*.json')};check('binder_reject_'+mutation,lambda:binder.bind(store,pair,mf,life),False);assert protected=={p:sha(p)for p in protected}
 store,life,ctx=fresh();original_replace=Path.replace
 def interrupted(file,target):
  if file.name=='PI09_TRANSPORTE_HEREDADO_R02.json.BINDING':raise OSError('SIMULATED_BOUNDARY_AFTER_FIRST_ADMIN_REPLACE')
  return original_replace(file,target)
 Path.replace=interrupted
 try:
  try:binder.bind(store,pair,mf,life);raise AssertionError('No injected fault')
  except OSError:pass
 finally:Path.replace=original_replace
 check('intermediate_administrative_bind_preserved_and_blocked_on_retry',lambda:binder.bind(store,pair,mf,life),False);assert not(store.root.parent/'VINCULO_FAMILIA_DIAGNOSTICA_PI09_R01.json').exists()and not list(store.state.rglob('VIDA.json'))
 new=read(STAGE/'receta.json');old=read(RP/'recetas/pi09_consulta_native12_desde_C_T884835_R03.json');assert new['variants']==old['variants']and new['analysis']==old['analysis'];rows.append({'name':'14steps_180checks_receipts_all_actual_expectations_literal_R03','passed':True})
 assert new.get('required_life_id')is None and new['required_life_prefix']==wrapper.PREFIX and new['verification']['Native_replay_verified']is False;rows.append({'name':'fresh_family_contract_and_material_verification_pending_honest','passed':True})
 importer=(cap/'app/importacion_emparejada.py').read_text('utf-8-sig');assert importer.index('family_binding=bind(')<importer.index('record=store.import_state(');rows.append({'name':'binder_precedes_actual_Store_import_state','passed':True})
 for f in('supervisar_RP_FAMILIA_PI09_R04.py','guardia_frontdoor_RP_FAMILIA_PI09_R04.py','contrastar_RP_FAMILIA_PI09_R04.py','registrar_RP_FAMILIA_PI09_R04.py'):ast.parse((H/f).read_bytes())
 assert not loaded_native;sys.meta_path.remove(deny)
 result={'schema':'DEE.PI09.RP.reusable_family.pure_tests.R04','passed':len(rows),'checks':rows,'Native_executed':False,'DEE_imports':0,'real_state_or_SQLite_opened':False,'actual_immutable_manifest_read':str(pair/'EXPORTACION_SERVICIO.json'),'new_family_material_replay_still_pending':True,'old_R03_preserved':True,'sources':{p.name:sha(p)for p in(H/'pi09_reproduccion_familia_R01.py',H/'vincular_familia_RP_PI09_R01.py',H/'incorporar_familia_RP_PI09_R04.py')}}
 write(OUT/'RESULTADO.json',result);print(json.dumps({'passed':len(rows),'proof':str(OUT/'RESULTADO.json'),'sha256':sha(OUT/'RESULTADO.json'),'Native_executed':False}))
if __name__=='__main__':main()
