"""Root-only additive R03 experimental reproduction, never principal adoption.

Default describes without writes. --aplicar preserves ONE reconstructed, exact PRE34 S7
source capsule plus exact R03 actor history/old FI before-images, registers the
already stable complete POST4 pair and creates a strict existing-RP recipe.
No Native/owner import, execution, selector or operational-state modification.
"""
from pathlib import Path
import argparse,ast,datetime,hashlib,json,os,shutil,subprocess,sys
P=Path(__file__).resolve().parents[1];H=P/'codigo';S=P/'estados/candidato/sistema';C=P.parents[2]/'DEE Cognitive 2.0';RP=C/'reproducibilidad'
ALIAS='PI07_R03_POST4_T849645';PAIR=RP/'materiales'/ALIAS;CAPKEY='PI07_R03_LOCAL_FI_PRE34_R02';RECIPE='pi07_r03_uso_adquirido_post4_R02'
REFERENCES={'normal_op4':('PI07_RESERVA_A_R03_EP04.json','23ced5c583285139ec5525c1acad474520077293c2eff96daaba8a181adbbd88',{}),'sensor_cut_op4':('PI07_CORTE_SENSOR_04_05_R03_EP04.json','d74d5cfbd9e588fb17fbef9e73c0455b26900786febf3b4c4fd25f08769a0255',{'sensor_ablation':True}),'actuator_cut_op4':('PI07_CORTE_ACTUADOR_04_05_R03_EP04.json','593ecab664543b4612d2c524e43ce0b72af3026ff9505e90b1739bfe1d6b8ca4',{'actuator_ablation':True})}
def sha(p):
 h=hashlib.sha256()
 with Path(p).open('rb')as f:
  for b in iter(lambda:f.read(1048576),b''):h.update(b)
 return h.hexdigest()
def read(p):return json.loads(p.read_text('utf-8-sig'))
def regular(p):
 for x in(p,*p.parents):
  if x.exists()and(x.is_symlink()or getattr(x.lstat(),'st_file_attributes',0)&1024):raise ValueError('No linked source/target')
def put(p,v):
 regular(p);p.parent.mkdir(parents=True,exist_ok=True)
 if p.exists():raise FileExistsError('Existing output preserved')
 with p.open('x',encoding='utf8')as f:json.dump(v,f,ensure_ascii=False,indent=2);f.write('\n')
def snapshot_sources():
 applied_file=P/'control/C2C34_PI07_DELTA_APLICADO_R02.json';applied=read(applied_file)
 originals=H/'ORIGINALES_C2C34_PI07_R02';rows={r['file']:r for r in applied['files']}
 added={name for name,row in rows.items()if row['before_sha256']is None}
 expected_added={'capacidades/pi07_c2c_ofertas_R01.py','capacidades/PROTOCOLO_PI07_C2C_34_R01.json','capacidades/PROTOCOLO_PI07_C2C_EXTENSION_R01.json','capacidades/pi07_permiso_principal_R02.py'}
 if added!=expected_added:raise ValueError('Exact failed34delta scope only')
 replaced={name:row['before_sha256']for name,row in rows.items()if row['before_sha256']is not None}
 if set(replaced)!={'app/mundo_genesis_apd05.py','app/cola_local.py','capacidades/pi04_dispatcher.py'}:raise ValueError('Exact3preservedPRE34beforeimages required')
 files=[]
 for parent in(S/'app',S/'capacidades',S/'contratos',S/'organizaciones'):
  files.extend(p for p in parent.rglob('*')if p.is_file()and p.suffix in('.py','.json','.eventos')and'__pycache__'not in p.parts)
 files+=list(S.glob('*.py'))+list(S.glob('*.json'));result=[]
 for current in sorted(set(files)):
  name=current.relative_to(S).as_posix()
  if name in added:continue
  actual=originals/name if name in replaced else current;regular(actual)
  if name in rows and sha(current)!=rows[name]['sha256']:raise ValueError('Post34source drift: '+name)
  if name in replaced and sha(actual)!=replaced[name]:raise ValueError('Changed actual PRE34beforeimage: '+name)
  result.append({'file':name,'bytes':actual.stat().st_size,'sha256':sha(actual),'source':str(actual)})
 return result

def pre34_validation(files):
 # Invoke the REAL preserved pure-Python validator, not a mocked dependency.
 # Module import and protocol checks use only stdlib and read source files.
 import importlib.util
 actual={r['file']:r for r in files};body=Path(actual['capacidades/pi04_coordinacion_central_C2C.py']['source'])
 spec=importlib.util.spec_from_file_location('PI07_PRE34_contract_check_no_Native',body);module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
 module.PROTOCOL=S/'capacidades/PROTOCOLO_PI05_C2C_30_R01.json';p,digest=module.protocol(material=True,evaluation=True)
 if len(p['schedule'])!=30:raise ValueError('Actual effective30contract required')
 rejected=None
 try:
  module.PROTOCOL=S/'capacidades/PROTOCOLO_PI07_C2C_34_R01.json';module.protocol(material=True,evaluation=True)
 except ValueError as exc:rejected=str(exc)
 if rejected!='One bounded2..32-opportunity schedule required':raise ValueError('Failed34contract must remain explicitly reproduced by pure validation')
 for name in('app/mundo_genesis_apd05.py','app/cola_local.py','capacidades/pi04_dispatcher.py'):
  text=Path(actual[name]['source']).read_text('utf-8-sig');ast.parse(text)
  if 'pi07_c2c_ofertas_R01'in text or'pi07_permiso_principal_R02'in text:raise ValueError('34failedhooks remain in PRE34source')
 return {'Native_imported_or_executed':False,'actual_C2C_protocol30_validator_passed':True,'effective_protocol_sha256':digest,'schedule_length':30,'failed_protocol34_validator_preserved':rejected,'restored_exact_beforeimage_files':3,'excluded_failed34_files':4,'scope':'Pure real contract/source validation; not a new material frontdoor replay or general proof of all dependency/state readiness.'}

def build_recipe():
 variants={};proofs=[]
 for variant,(name,digest,cuts)in REFERENCES.items():
  file=P/'ensayos'/name
  if sha(file)!=digest:raise ValueError('Frozen actual primary changed: '+name)
  saved=read(file);value=json.loads(saved['result'])['result']['rows'][0]
  if saved['status']!='completed'or value['ordinal']!=4 or value['before_tick']!=849645:raise ValueError('Actual closed POST4 first use required')
  actual_literal=json.loads(saved['payload'])['situaciones'][0];literal={'modo':'eci01-pi07-r03-episodio',**cuts}
  if literal!=actual_literal:raise ValueError('Reference direct literal differs')
  label='R03_OP04';base=['result','rows',0]
  step={'label':label,'literal':literal,'feedback':'omit','actuator':'closed','receipt_paths':[base+['requests']],'read_path':base+['actual_failed'],'expected':value['actual_failed'],'stop_on_unapplied_receipt':False}
  checks=[]
  for field,path in(('reader',base+['reader','choice']),('sensor',base+['sensor','actual_state_datum']),('FI_q4',base+['FI','early_physical_choice']),('FI_q6',base+['FI','old_q6_choice']),('pulse',base+['pulse_applied'])):
   v=value
   for part in path[3:]:v=v[part]
   checks.append({'label':field,'operation':'value','values':[{'step':label,'path':path}],'expected':v})
  dose=value['Native_inputs'];variants[variant]={'batches':[[step]],'final_checks':checks,'native_receipt_expectations':{k:dose[k]for k in('unique_requested','applied','rejected','pending_or_other')},'expected_final_physical':value['physical_after']}
  proofs.append({'variant':variant,'path':str(file),'sha256':digest,'source_life_id':value['life_id'],'before_tick':value['before_tick'],'after_tick':value['after_tick'],'literal':literal,'actual_failed':value['actual_failed'],'Native_inputs':dose})
 return{'schema':'DEE.reproduction.recipe.v1','id':RECIPE,'title':'PI07 R03: acquired-state useful protection and fixed information/actuator cuts','revision':'R01_NATIVE_REFERENCE_VERIFIED_CLI_REPLAY_PENDING','prefix':ALIAS,'code_capsule_key':CAPKEY,'required_life_prefix':'ECI02_PI03_REPRO_PI04_PI05_PI07_RP_R03_','requires_explicit_material':True,'reproduction_enabled':True,'variants':variants,'modalities':{'A':'Actual frozen primary/signature/receipt recalculation available in campaign; no world advance.','B':'Explicit acquired POST4 diagnostic use; one next fixed opportunity and two causal link-cut variants. Native reference material procedures actually ran.','C':'This recipe does not replay acquisition or install a policy; it inherits real history through the complete source pair.','D':'Not a capability possessed by the protected PI05 principal. No PI07 main adoption asserted.','E':'No general recovery or unlimited-use promise.'},'assistance':['Prepared Native TC anatomy/identity sensor/fixed perpendicular tool/six-lap calendar/environmental offer; host initiates one opportunity and evaluates only after the actual Native function.','Expected observations are auditor-only. No expected action, private future, control history or answer is sent to the actor.'],'limitations':['Three variants are paired controls from a shared complete prefix, not independent organisms. Sensor cut submits material0; actuator cut omits one pulse and has the declared dose difference.','Same R03 actor40648f/protof69e remains literal; enclosing source may include later dormant FI access. Historical old-FI198tick regression is preserved; no intact-legacy or general-agency claim.','Executable existing RP facade is registered; no additional Native CLI cold world was run in the exhausted14-world campaign. Do not label this new frontdoor end-to-end verified.'],'verification':{'state':'PROCEDIMIENTO_NATIVE_REFERENCIA_PROBADO_CLI_REPLAY_PENDIENTE','Native_replay_verified':False,'source_native_procedure_executed':True,'new_frontdoor_CLI_executed':False,'reference_executions':proofs},'last_verified_source_scope':'Actual reference one-op normal/sensor/actuator material runs; recipe transport read-only requirements checked separately.'}
def main(a):
 recipe=build_recipe();files=snapshot_sources();pre34=pre34_validation(files);source_manifest=PAIR/'EXPORTACION_SERVICIO.json';manifest=read(source_manifest)
 if manifest['life_id']!='ECI02_PI03_REPRO_PI04_PI05_PI07_CAND_01'or manifest['physical']['N']!=67 or manifest['physical']['tick']!=849645:raise ValueError('Exact complete stable POST4 prefix only')
 prefix={'alias':ALIAS,'product_relative':'reproducibilidad/materiales/'+ALIAS,'manifest_sha256':sha(source_manifest),'life_id':manifest['life_id'],'tick':849645,'members':len(manifest['members']),'bytes':sum(v['bytes']for v in manifest['members']),'scope':'Frozen complete experimentally acquired POST4; not a second principal or a current-main backup.'}
 pins={'capacidades/pi07_regulacion_R03.py':'40648fd81c5b1f278ee9c18d0d464c5a4b5e9fd808054afe6ff072a10fda0ac5','capacidades/PROTOCOLO_PI07_R03.json':'f69e8558799558a1ccceb70e0684a061a971b9521ad8985205d1662aea55d269'}
 for name,h in pins.items():
  if sha(S/name)!=h:raise ValueError('Historical R03 actor/protocol changed')
 if not a.aplicar:
  print(json.dumps({'mode':'READ_ONLY_PLAN','prefix':prefix,'capsule_key':CAPKEY,'files':len(files),'source_code_bytes':sum(v['bytes']for v in files),'recipe':RECIPE,'variants':list(recipe['variants']),'Native_executed':False,'product_modified':False,'CLI_replay_already_executed':False,'PRE34_contract_validation':pre34}));return
 if a.closed_source_proof is None:raise ValueError('Actual closed new-FI panel proof required before preserving current source')
 closefile=a.closed_source_proof.resolve(strict=True);closed=read(closefile)
 if not closefile.is_relative_to((P/'control').resolve())or not(closed.get('closed')is True or closed.get('owner_closed')is True):raise ValueError('Actual affected source closure proof required')
 resources_file=RP/'RECURSOS.json';resources=read(resources_file);before_resources=sha(resources_file);caps=RP/'codigo_preservado'/CAPKEY;recipefile=RP/'recetas'/(RECIPE+'.json');out=P/'control/RP_R03_INCORPORADA_PI07_R03.json'
 if caps.exists()or recipefile.exists()or out.exists():raise FileExistsError('Existing capability/version preserved')
 support=P/'codigo/archivar_copias_RP_08_12_PI07_R01.py'
 import runpy
 h=runpy.run_path(str(support),run_name='static_budget_only_for_RP_registration');before=h['scoped_bytes']()
 documentary_size=sum((P/'ensayos'/value[0]).stat().st_size for value in REFERENCES.values())+1_000_000
 if before+sum(v['bytes']for v in files)+documentary_size+2_000_000>5_500_000_000:raise ValueError('Original fixed5.5GBbudget has no small code/evidence/recipe headroom')
 analysis=RP/'materiales/PI07_R03_ANALISIS_POST4_R01';stage=P/'control/RP_R03_DOCUMENTAL_STAGE_R02'
 if analysis.exists()or stage.exists():raise FileExistsError('Existing analysis stage/version preserved')
 command=[sys.executable,'-I','-B','-X','utf8',str(H/'EXPORTAR_PRIMARIOS_PORTABLE_PI07.py'),'--destino',str(stage),'--sistema',str(S),'--primarios',*[str(P/'ensayos'/v[0])for v in REFERENCES.values()]]
 child=subprocess.run(command,capture_output=True,text=True,encoding='utf8',timeout=180,creationflags=getattr(subprocess,'CREATE_NO_WINDOW',0))
 if child.returncode:raise RuntimeError('Documentary export failed; preserve stage, no blind retry: '+child.stderr)
 for name in('RECALCULAR_PRIMARIOS_PI07.py','RECALCULAR_RP_PI07_R02.py'):shutil.copyfile(H/name,stage/name)
 analysis_files=[{'file':f.relative_to(stage).as_posix(),'bytes':f.stat().st_size,'sha256':sha(f)}for f in sorted(stage.rglob('*'))if f.is_file()]
 put(stage/'MANIFIESTO_ESTABLE.json',{'schema':'DEE.PI07.R03.documentary_material.v1','files':analysis_files,'Native_executed':False,'source_reference_primaries_only':True})
 os.rename(stage,analysis)
 recipe['analysis']={'interface':'DEE.recalculation.root_outdir.v1','product_relative':'reproducibilidad/materiales/PI07_R03_ANALISIS_POST4_R01','manifest':'MANIFIESTO_ESTABLE.json','manifest_sha256':sha(analysis/'MANIFIESTO_ESTABLE.json'),'recalculation_script':'RECALCULAR_RP_PI07_R02.py'}
 protected=[C/'sistema/estado/ACTIVO.json',C/'sistema/estado/vidas/ECI02_PI03_REPRO_PI04_PI05_MAIN_01/VIDA.json'];critical={str(f):sha(f)for f in protected};resources_backup=P/'control/RP_RECURSOS_ANTES_R03_PI07_R02.json'
 put(resources_backup,resources);caps.mkdir()
 for row in files:
  file=Path(row['source']);target=caps/row['file'];target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(file,target)
  if sha(file)!=row['sha256']or sha(target)!=row['sha256']:raise ValueError('Source changed during static capsule preservation')
 source_manifest_object={'schema':'DEE.Cognitive.frozen_source_capsule.v1','id':CAPKEY,'files':[{k:r[k]for k in('file','bytes','sha256')}for r in files],'source_system':str(S),'reconstruction':'Exact PRE34 sources restored from 3 recorded beforeimages; 4 failed34-only files excluded. No S7state/source modified.','PRE34_contract_validation':pre34,'source_closed_proof':{'path':str(closefile),'sha256':sha(closefile)},'R03_actor_preserved':pins,'scope':'One exact reconstructed PRE34 enclosing source capsule; R03 Native actor/protocol literal. Later FI facade is dormant without its new metadata and explicit mode/selected contract. No state or engine copied.'}
 # Exact historical before-images are provenance only, never live imports.
 before_images=P/'codigo/ORIGINALES_ACCESO_FI_PI07_R01'
 if before_images.is_dir():
  for file in before_images.rglob('*'):
   if file.is_file():
    regular(file);target=caps/'procedencia/ANTES_ACCESO_FI'/file.relative_to(before_images);target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(file,target);source_manifest_object['files'].append({'file':target.relative_to(caps).as_posix(),'bytes':target.stat().st_size,'sha256':sha(target)})
 put(caps/'SISTEMA_CODIGO.json',source_manifest_object)
 put(recipefile,recipe)
 if ALIAS in resources['pairs']and resources['pairs'][ALIAS]!=prefix:raise ValueError('Existing stable prefix descriptor differs')
 resources['pairs'][ALIAS]=prefix;resources['code_capsules'][CAPKEY]={'product_relative':'reproducibilidad/codigo_preservado/'+CAPKEY,'manifest':'SISTEMA_CODIGO.json','manifest_sha256':sha(caps/'SISTEMA_CODIGO.json')}
 if sha(resources_file)!=before_resources:raise ValueError('Concurrent RP resource registry change')
 temporary=resources_file.with_name('RECURSOS.PI07_R03_WRITING.json');put(temporary,resources);os.replace(temporary,resources_file)
 if any(sha(Path(path))!=v for path,v in critical.items()):raise RuntimeError('Protected principal metadata changed')
 put(out,{'schema':'DEE.PI07.R03.experimental_RP_registration.v1','registered_at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'status':'REGISTERED_USABLE_EXPERIMENTAL_RECIPE_NO_MAIN_ADOPTION','recipe':{'path':str(recipefile),'sha256':sha(recipefile)},'capsule':{'path':str(caps),'manifest_sha256':sha(caps/'SISTEMA_CODIGO.json'),'code_files':len(files)},'prefix':prefix,'resources_before':{'path':str(resources_backup),'sha256':sha(resources_backup)},'resources_after_sha256':sha(resources_file),'closed_source_proof':{'path':str(closefile),'sha256':sha(closefile)},'PRE34_contract_validation':pre34,'source_native_reference_executed':True,'new_frontdoor_CLI_material_replay_executed':False,'Native_executed_by_registration':False,'new_ticks':0,'selected_main_critical_hashes_before_after':critical,'commands':{'list':'gestionar.py reproducibilidad listar','requirements':'gestionar.py reproducibilidad verificar '+RECIPE,'material_example':'gestionar.py reproducibilidad reproducir '+RECIPE+' --variante normal_op4 --vida ECI02_PI03_REPRO_PI04_PI05_PI07_RP_R03_01 --destino ABSOLUTE_NEW_NONEMPTY_REFUSED --material'},'scope':'Experimental local mechanism available from Cognitive through existing strict diagnostic reproduction. Acquired state/source code/contracts/resources preserved; no new cognitive acquisition or main promotion by this registration.'})
 print(json.dumps({'proof':str(out),'sha256':sha(out),'recipe':RECIPE,'Native_executed':False,'new_ticks':0}))
if __name__=='__main__':
 ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--aplicar',action='store_true');ap.add_argument('--closed-source-proof',type=Path);main(ap.parse_args())
