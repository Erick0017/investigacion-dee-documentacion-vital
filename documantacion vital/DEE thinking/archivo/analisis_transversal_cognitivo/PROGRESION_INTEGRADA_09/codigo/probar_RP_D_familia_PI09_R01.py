"""Actual code/manifest pure DRF binding tests; no state or DEE imports."""
from pathlib import Path
import ast,hashlib,importlib.util,json,types
H=Path(__file__).resolve().parent;P=H.parent;C=P.parents[2]/'DEE Cognitive 2.0';STAGE=H/'RP_D_FAMILIA_R01_PREPARADA';OUT=H/'PRUEBA_RP_D_FAMILIA_PI09_R01'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):return json.loads(p.read_text('utf-8-sig'))
def put(p,v):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(v,indent=2)+'\n','utf8')
def load(name,p):s=importlib.util.spec_from_file_location(name,p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def main():
 if OUT.exists():raise FileExistsError('Preserve previous proof')
 OUT.mkdir();cap=STAGE/'capsule';m=load('pure_DRF_wrapper',H/'pi09_reproduccion_D_familia_R01.py');b=load('pure_DRF_binder',H/'vincular_familia_D_RP_PI09_R01.py');m.SOURCE=cap/'capacidades/pi09_entorno_persistente_D_R02.py';m.CONFIG=cap/'capacidades/PI09_REPRODUCCION_D_FAMILIA_R01.json';private=m.private();checks=[]
 def check(name,call,expected=True):
  try:call();actual=True
  except(ValueError,KeyError,FileExistsError):actual=False
  if actual!=expected:raise AssertionError(name)
  checks.append({'name':name,'passed':True,'accepted':actual})
 for suffix in('20261111A','20261112A','A','0123456789'):check('family_'+suffix,lambda suffix=suffix:m.need(m.allowed_life(m.PREFIX+suffix),'bad'))
 for value in('','a','A_B','01234567890'):check('reject_id_'+value,lambda value=value:m.need(m.allowed_life(m.PREFIX+value),'bad'),False)
 for row in({'modo':m.PREPARE,'brazo':'real'},{'modo':m.EPISODE},{'modo':m.STATE}):check('literal_'+str(row),lambda row=row:m.validate_literal(row))
 for row in({'modo':m.PREPARE,'brazo':'none'},{'modo':m.PREPARE,'brazo':'yoked','plan':'[]'},{'modo':m.EPISODE,'expected':True}):check('reject_'+str(row),lambda row=row:m.validate_literal(row),False)
 text=m.SOURCE.read_text('utf-8-sig');before="repro=row['brazo']=='real'and identity['life_id']in REPRO_IDS";after="repro=row['brazo']=='real'and _family_allowed(identity['life_id'])";assert text.count(before)==1
 for a,z in zip(ast.parse(text).body,ast.parse(text.replace(before,after)).body):
  if isinstance(a,ast.FunctionDef)and a.name=='validate':continue
  assert ast.dump(a,include_attributes=False)==ast.dump(z,include_attributes=False)
 assert private._identity is m._identity;checks.append({'name':'literal_D2_all_Native_functions_AST_unchanged_only_REPRO_admission_line','passed':True})
 for name,digest in read(cap/'capacidades/SELLO_PI09_D_R02.json')['files_sha256'].items():assert sha(cap/'capacidades'/name)==digest
 checks.append({'name':'all_eight_scientific_and_transport_seal_pins_literal','passed':True})
 registry=read(cap/'capacidades/PI09_PLUGINS_D_R02.json');assert 'pi09_reproduccion_D_familia_R01'in registry['plugins']and 'pi09_entorno_persistente_D_R02'not in registry['plugins']and all(name not in registry['files_sha256']for name in('PI09_TRANSPORTE_D_R02.json','PI09_TRANSPORTE_HEREDADO_R02.json'));checks.append({'name':'bound_JSON_audited_separately_no_duplicate_D_material_plugin','passed':True})
 pair=P/'pares/DISCOVERY_POSTPANEL_T907543';manifest=read(pair/'EXPORTACION_SERVICIO.json');counter=0
 def fresh():
  nonlocal counter
  counter+=1;root=OUT/('FAKE_%02d'%counter)/'sistema';root.mkdir(parents=True);(root/'estado').mkdir();life=m.PREFIX+'20261111A'
  for name in('PI09_REPRODUCCION_D_FAMILIA_R01.json','PI09_TRANSPORTE_HEREDADO_R02.json','PI09_TRANSPORTE_D_R02.json'):put(root/'capacidades'/name,read(cap/'capacidades'/name))
  ctx={'life':life,'system':str(root),'recipe':b.RID,'variant':'real6','source_code_capsule_key':b.CAP,'prefix_manifest_sha256':b.PAIR_SHA,'source_code_manifest_sha256':sha(cap/'SISTEMA_CODIGO.json'),'product':str(C)};put(root.parent/'CONTEXTO_EJECUCION.json',ctx);return types.SimpleNamespace(root=root,state=root/'estado'),life,ctx
 store,life,ctx=fresh();proof=b.bind(store,pair,manifest,life);assert len(proof['files_after'])==3 and proof['new_native_ticks']==proof['new_native_inputs']==0 and not list(store.state.rglob('VIDA.json'));checks.append({'name':'actual_D_binder_three_identity_configs_before_Native_creation','passed':True})
 check('same_binding_not_retried',lambda:b.bind(store,pair,manifest,life),False)
 for mutation in('ACTIVO','used_life','worker','wrong_context','wrong_prefix','wrong_cap'):
  store,life,ctx=fresh()
  if mutation=='ACTIVO':put(store.state/'ACTIVO.json',{'life_id':'FAKE'})
  elif mutation=='used_life':(store.state/'vidas'/life).mkdir(parents=True)
  elif mutation=='worker':(store.state/'servicios_locales'/life).mkdir(parents=True)
  else:
   ctx[{'wrong_context':'recipe','wrong_prefix':'prefix_manifest_sha256','wrong_cap':'source_code_capsule_key'}[mutation]]='WRONG';put(store.root.parent/'CONTEXTO_EJECUCION.json',ctx)
  original={f:sha(f)for f in(store.root/'capacidades').glob('*.json')};check('binder_reject_'+mutation,lambda:b.bind(store,pair,manifest,life),False);assert original=={f:sha(f)for f in original}
 importer=(cap/'app/importacion_emparejada.py').read_text('utf-8-sig');world=(cap/'app/mundo_genesis_apd05.py').read_text('utf-8-sig');assert importer.index('family_binding=bind(')<importer.index('record=store.import_state(')and 'reproduction_family.install_transport()'in world;checks.append({'name':'actual_import_bind_then_declared_dirs_then_Owner_identity_install','passed':True})
 output={'schema':'DEE.PI09.D.reusable_RP_family.pure_tests.R01','passed':len(checks),'checks':checks,'Native_executed':False,'DEE_imports':0,'real_state_or_SQLite_read':False,'only_immutable_preD_manifest_read':True,'actual_family_Native_replay_pending':True,'capsule_manifest_sha256':sha(cap/'SISTEMA_CODIGO.json')};put(OUT/'RESULTADO.json',output);print(json.dumps({'passed':len(checks),'proof':str(OUT/'RESULTADO.json'),'sha256':sha(OUT/'RESULTADO.json'),'Native_executed':False}))
if __name__=='__main__':main()
